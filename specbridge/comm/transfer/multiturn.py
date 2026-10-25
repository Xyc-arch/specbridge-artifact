"""HOW SHOULD A CONVERSATIONAL SQL SYSTEM CARRY A CLARIFICATION AND A FOLLOW-UP TO THE SQL STEP? (2026-10-14; gate: out/multiturn/GATE.md)
One design decision changes, everything else is fixed: the same BIRD dev question, model, schema and user turns. The user turns are
written by code (so every arm replays the same user): turn 1 = question + evidence; turn 2 = a clarification settling one library
choice (the BIRD single-turn items of rewrite.bird_items); turn 3 = an elliptical follow-up that adds a filter ("Now only the ones
where <column> is <value>."). Gold per turn: the reference with the edits so far, executed; conversations whose edits do not apply,
run, change the answer and combine are dropped and counted.
Arms (text given to the same plain SQL prompt): transcript (all user turns) | append (turn 1 + each later turn as a clause) | condensed
(the retrieval-chat condense prompt over the turns so far) | latest (latest user turn only; a lower bound).
Computable set: per turn, the model answers V of that turn's gold 3 times; computable if right in >= 2 of 3 (not one of the arms).
3 runs per arm; Sonnet and GPT-Sol; jobs interleaved; raw output saved.
    python -m specbridge.comm.transfer.multiturn build | run | report   -> out/multiturn/"""
import collections, concurrent.futures as cf, glob, hashlib, json, math, os, random, re, sqlite3, sys
from sqlglot import exp
from specbridge.comm.common import db as DB, grade as G
from specbridge.comm.transfer import disclose as X, rewrite as RW
from specbridge.comm.diagnose import rules as RU
from specbridge.report import impact as IM

OUT = "out/multiturn"; MODELS = ("sonnet", "gpt-6-sol"); RUNS = 3; SEED = 20261028; ARMS = ("transcript", "append", "condensed", "latest")
CONDENSE = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{}
Follow Up Input: {}
Standalone question:"""
PROMPTS_SHA = hashlib.sha256((CONDENSE + X.PLAIN).encode()).hexdigest()[:12]


def _words(c): return re.sub(r"([a-z])([A-Z])", r"\1 \2", c).replace("_", " ").strip()


def followup(path, sql):
    """(follow-up text, follow-up gold SQL) adding one equality filter on a low-cardinality text column of a top-level table."""
    q = RU.parse(sql)
    if not isinstance(q, exp.Select) or q.args.get("with") or q.args.get("with_"): return None
    fr = q.args.get("from") or q.args.get("from_")                       # sqlglot 30 stores FROM under "from_"
    tabs = [t for t in [fr.this] + [j.this for j in (q.args.get("joins") or [])] if isinstance(t, exp.Table)] if fr else []
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True); base = IM.run(path, sql)
    for t in tabs:
        cols = [r[1] for r in con.execute('PRAGMA table_info("%s")' % t.name) if (r[2] or "").upper() in ("TEXT", "") or "CHAR" in (r[2] or "").upper()]
        for c in cols:
            try: vs = con.execute('SELECT "%s", COUNT(*) FROM "%s" WHERE "%s" IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 13' % (c, t.name, c)).fetchall()
            except Exception: continue
            if not 2 <= len(vs) <= 12: continue
            for v, _n in vs[:3]:
                if not isinstance(v, str) or not v.strip() or "'" in v: continue
                q2 = q.copy(); q2.where(exp.EQ(this=exp.column(c, table=t.alias_or_name, quoted=True), expression=exp.Literal.string(v)), copy=False)
                e2 = q2.sql(dialect="sqlite"); r2 = IM.run(path, e2)
                if r2 and base is not None and not G.bird_ex(base, r2) and any(x is not None for row in r2 for x in row):
                    con.close(); return "Now only the ones where %s is %s." % (_words(c), v), e2
    con.close(); return None


def build():
    os.makedirs(OUT, exist_ok=True); items = [x for x in RW.bird_items() if x["rule"] != "null_filter"]; C = []; drop = collections.Counter()
    for x in items:
        g0, g1 = IM.run(x["path"], x["gold0"], 60), IM.run(x["path"], x["gold"], 60)
        if g0 is None or g1 is None or G.bird_ex(g0, g1): drop["clarification edit does not run or change the answer"] += 1; continue
        f = followup(x["path"], x["gold"])
        if not f: drop["no follow-up filter that runs and changes the clarified answer"] += 1; continue
        C.append(dict(x, turns=[x["question"] + ("\nEvidence: " + x["evidence"] if x["evidence"] else ""), x["clarification"], f[0]], gold1=x["gold"], gold2=f[1]))
    json.dump({"conversations": C, "dropped": drop, "prompts_sha": PROMPTS_SHA}, open(OUT + "/conversations.json", "w"), indent=1)
    print(len(C), "conversations;", dict(drop))


def text(arm, turns, k, m, raw):
    """Request text for turn k (1 = clarified turn, 2 = follow-up turn) under one arm."""
    from specbridge.pd.ask import ask
    ts = turns[:k + 1]
    if arm == "transcript": return "\n".join("User: " + t for t in ts)
    if arm == "append": return "\n".join(ts)
    if arm == "latest": return ts[-1]
    t = ask(CONDENSE.format("\n".join("Human: " + t for t in ts[:-1]), ts[-1]), m, timeout=1500, quiet=True) or ""; raw["condense"] = t
    return t.split("Standalone question:")[-1].strip()


def run(workers=6):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    D = json.load(open(OUT + "/conversations.json")); C = {c["id"]: c for c in D["conversations"]}
    # Order (GATE.md note 12:00): one group per (model, conversation, run) with its 10 jobs in random order; groups shuffled, groups
    # whose database renders V first (they can enter the computable set). Order only; every job is the same as before.
    novc = {"card_games", "codebase_community", "european_football_2", "debit_card_specializing"}; rng = random.Random(SEED)
    groups = [(m, c, r) for c in C for m in MODELS for r in range(RUNS)]; rng.shuffle(groups); groups.sort(key=lambda g: C[g[1]]["db"] in novc)
    jobs = []
    for m, c, r in groups:
        js = [(m, c, r, a, k) for k in (1, 2) for a in ARMS + ("V",)]; rng.shuffle(js); jobs += js
    def one(j):
        m, cid, r, a, k = j; f = "%s/runs/%s/%s/%s_t%d_r%d.json" % (OUT, m, cid, a, k, r)
        if os.path.exists(f): return
        c = C[cid]; gold = c["gold1"] if k == 1 else c["gold2"]; raw = {}
        req = (DB.explicit(gold, c["db"]) or "") if a == "V" else text(a, c["turns"], k, m, raw)
        out = {"model": m, "conv": cid, "run": r, "arm": a, "turn": k, "request": req}
        if req:
            t = ask(X.PLAIN % (RW._schema(c["path"]), "", req), m, timeout=1500, quiet=True) or ""; raw["sql"] = t
            sql = (jparse(t, "{") or {}).get("sql"); rows = IM.run(c["path"], sql) if sql else None; g = IM.run(c["path"], gold, 60)
            out.update(sql=sql, runs=rows is not None, right=rows is not None and g is not None and G.bird_ex(g, rows))
        else: out.update(sql=None, runs=False, right=False, no_text=True)
        out["raw"] = raw; os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(out, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(one, jobs))
    report()


def _signflip(d, B=20000, seed=SEED):
    rng = random.Random(seed); obs = sum(d) / len(d); k = 0
    for _ in range(B): k += abs(sum(x if rng.random() < 0.5 else -x for x in d) / len(d)) >= abs(obs) - 1e-12
    return k / B


def report():
    R = collections.defaultdict(list)
    for f in glob.glob(OUT + "/runs/*/*/*.json"):
        o = json.load(open(f)); R[(o["model"], o["conv"], o["turn"], o["arm"])].append(bool(o["right"]))
    keys = sorted({(m, c) for m, c, _k, _a in R})
    acc = lambda m, c, k, a: sum(R[(m, c, k, a)]) / len(R[(m, c, k, a)]) if R.get((m, c, k, a)) else None
    comp = lambda m, c, k: R.get((m, c, k, "V")) and sum(R[(m, c, k, "V")]) >= 2
    L = ["# Carrying a clarification and a follow-up to the SQL step (gate: out/multiturn/GATE.md)\n",
         "Accuracy averaged over 3 runs per conversation-model pair; tests: paired sign-flip over pairs on run-averaged accuracy.\n"]
    out = {}
    for k, name in ((2, "follow-up turn"), (1, "clarified turn")):
        for setname, sel in (("computable", lambda m, c: comp(m, c, k)), ("all", lambda m, c: True)):
            L += ["## %s, %s set\n" % (name, setname), "| model | pairs | transcript | append | condensed | latest | append - condensed, p | append - transcript, p |", "|---|---|---|---|---|---|---|---|"]
            for mname, ms in (("sonnet", ("sonnet",)), ("gpt-6-sol", ("gpt-6-sol",)), ("pooled", MODELS)):
                P = [(m, c) for m, c in keys if m in ms and sel(m, c) and all(acc(m, c, k, a) is not None for a in ARMS)]
                if not P: continue
                A = {a: [acc(m, c, k, a) for m, c in P] for a in ARMS}; mean = lambda v: 100 * sum(v) / len(v)
                d1 = [x - y for x, y in zip(A["append"], A["condensed"])]; d2 = [x - y for x, y in zip(A["append"], A["transcript"])]
                L.append("| %s | %d | %.1f | %.1f | %.1f | %.1f | %+.1f, %.3g | %+.1f, %.3g |" % (mname, len(P), *[mean(A[a]) for a in ARMS], mean(d1), _signflip(d1), mean(d2), _signflip(d2)))
                out["%s|%s|%s" % (name, setname, mname)] = {"pairs": len(P), **{a: mean(A[a]) for a in ARMS}, "append-condensed": mean(d1), "p1": _signflip(d1), "append-transcript": mean(d2), "p2": _signflip(d2)}
            L.append("")
    g = out.get("follow-up turn|computable|pooled")
    if g: L.insert(2, "**Primary gate** (pooled, computable set, follow-up turn: append - condensed >= 3 points, p < 0.05): %+.1f points, p = %.3g -> %s\n" % (g["append-condensed"], g["p1"], "PASS" if g["append-condensed"] >= 3 and g["p1"] < 0.05 else "FAIL"))
    json.dump(out, open(OUT + "/results.json", "w"), indent=1); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"build": build, "run": run, "report": report}[sys.argv[1]]()
