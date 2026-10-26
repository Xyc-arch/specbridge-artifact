"""DIALECT RERUN (2026-10-26). The answering prompts (disclose.INSTRUCTION, disclose.PLAIN) never named the SQL dialect. On the four
LiveSQLBench databases, whose schemas carry PostgreSQL DDL, answers used PostgreSQL syntax (`x::numeric`) that SQLite rejects; on the
Spider and BIRD sets 3 of about 1,000 answers did. This reruns every accepted request set on those four databases with one change to the
prompt -- "for the SQLite database below" -- for all four models and every run that answers request sets with that prompt:
the explanation call, the SQL-only call, the matched other specific request, the sampled open requests; then the same judges.
The first runs stay untouched; outputs go to <render>/disclose_sqlite/ in the same layout as <render>/disclose/.
    python -m specbridge.comm.transfer.dialect_rerun sample
    python -m specbridge.comm.transfer.dialect_rerun run        (all stages; resumable: saved answers are not asked again)
    python -m specbridge.comm.transfer.dialect_rerun compare    -> <render>/disclose_sqlite/COMPARE.md, compare.json
At most 6 workers (machine rule)."""
import hashlib, json, os, sys
from specbridge.comm.transfer import disclose as X, combined as CB

LIVE = ("alien", "archeology", "crypto", "insider")
OLD, NEW = "for the database below", "for the SQLite database below"
D = CB.D; OUT = D + "/disclose_sqlite"; MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
_orig_paths = X._paths


def use_sqlite_prompt():
    """Point disclose (and the modules that read its prompts and paths) at the SQLite prompt and the new output tree."""
    if NEW in X.INSTRUCTION: return                          # already applied in this process
    assert OLD in X.INSTRUCTION and OLD in X.PLAIN
    X.INSTRUCTION = X.INSTRUCTION.replace(OLD, NEW); X.PLAIN = X.PLAIN.replace(OLD, NEW)
    X.PROMPT_SHA = hashlib.sha256(X.INSTRUCTION.encode()).hexdigest()[:12]
    X._paths = lambda d: (_orig_paths(d)[0], _orig_paths(d)[1], OUT) if d == D else _orig_paths(d)


def live_cases():
    """The accepted request sets on the four databases (the sets every result uses)."""
    from specbridge.comm.transfer import reviewed as RV
    C = json.load(open(D + "/eval/frozen.json"))["cases"]
    return RV.accepted(sorted(c["case"] for c in C if c["database"] in LIVE))


def sample():
    """The first run's allocation (open + the same specific wording), restricted to the LiveSQLBench sets."""
    use_sqlite_prompt(); S = json.load(open(D + "/disclose/sample.json")); ks = live_cases()
    os.makedirs(OUT, exist_ok=True)
    json.dump({"from": D + "/disclose/sample.json", "prompt_sha": X.PROMPT_SHA, "change": [OLD, NEW], "cases": ks,
               "wordings": {k: S["wordings"][k] for k in ks}, "judge_open": [k for k in S.get("judge_open", []) if k in ks]},
              open(OUT + "/sample.json", "w"), indent=1)
    print(len(ks), "LiveSQLBench sets; prompt", X.PROMPT_SHA)


STAGES = ("explain", "sql_only", "matched", "sampled", "judge", "judge_alternatives")


def run(only=None, workers=6):
    """All stages in order, or one stage (`only`) so independent stages can run side by side. workers above 6 only with the
    user's approval for this run (2026-10-26: approved, finish in 15 minutes)."""
    use_sqlite_prompt()
    from specbridge.comm.transfer import matched as MT, topk as TK
    S = json.load(open(OUT + "/sample.json")); assert S["prompt_sha"] == X.PROMPT_SHA
    live = set(S["cases"]); sub = [k for k in TK.subset() if k in live]
    TK.subset = lambda: sub                                    # the sampling run: its sets on these databases only
    w = workers
    for stage, fn in (("explain", lambda: X.run(D, MODELS, w)), ("sql_only", lambda: X.plain(D, MODELS, w)),
                      ("matched", lambda: MT.run(MODELS, w)), ("sampled", lambda: TK.run(MODELS, w)),
                      ("judge", lambda: X.judge(D, w, scope="all")), ("judge_alternatives", lambda: X.judge_alternatives(D, w))):
        if only and stage != only: continue
        print("stage", stage, flush=True); fn(); open(OUT + "/%s.done" % stage, "w").write("ok\n")
    print("sampling sets on these databases:", len(sub))


def compare():
    """First run vs. SQLite rerun on the same LiveSQLBench sets, per model: runs, specific right, open gives a reading, both readings."""
    from specbridge.comm.transfer import reviewed as RV
    C = {c["case"]: c for c in json.load(open(D + "/eval/frozen.json"))["cases"]}
    ks = [k for k in RV.accepted(sorted(C)) if C[k]["database"] in LIVE]
    def load(p, m):
        o = {}
        for f in os.listdir(os.path.join(p, m)):
            x = json.load(open(os.path.join(p, m, f))); o[(x["case"], x["wording"])] = x
        return o
    res = {"n_sets": len(ks)}
    for m in MODELS:
        for arm, sub in (("explain", ""), ("sql_only", "plain/")):
            r = {}
            for name, base in (("first", D + "/disclose/" + sub), ("sqlite", OUT + "/" + sub)):
                P = load(base, m); sp = {k: [w for (kk, w) in P if kk == k and w != "open"] for k in ks}
                spec = [P[(k, sp[k][0])] for k in ks if sp[k]]; op = [P[(k, "open")] for k in ks if (k, "open") in P]
                got = lambda o: set(o["primary_matches"]) | {x for a in o.get("alternatives", []) for x in a.get("matches", [])}
                r[name] = {"answered": len(spec) + len(op), "runs": sum(o["primary_executes"] for o in spec + op),
                           "specific_right": sum(o["wording"][-1] in o["primary_matches"] for o in spec),
                           "open_a_reading": sum(bool(o["primary_matches"]) for o in op),
                           "open_both": sum({"A", "B"} <= got(o) for o in op) if arm == "explain" else None,
                           "postgres_syntax": sum("::" in json.dumps(o.get("response")) for o in spec + op)}
            res["%s/%s" % (m, arm)] = r
    json.dump(res, open(OUT + "/compare.json", "w"), indent=1)
    L = ["# SQLite rerun vs first run on the %d accepted LiveSQLBench request sets\n" % len(ks),
         "| model / prompt | answers run | specific right | open gives a reading | open gives both | answers with `::` |", "|---|---|---|---|---|---|"]
    for k, r in res.items():
        if k == "n_sets": continue
        for name in ("first", "sqlite"):
            x = r[name]; L.append("| %s %s | %d/%d | %d | %d | %s | %d |" % (k, name, x["runs"], x["answered"], x["specific_right"], x["open_a_reading"],
                                                                         "-" if x["open_both"] is None else x["open_both"], x["postgres_syntax"]))
    open(OUT + "/COMPARE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


def control(model="haiku", n=40, seed=20261026, workers=6):
    """Does the dialect line change answers where the dialect was never a problem? n random accepted Spider/BIRD sets, the open
    request answered now with the first prompt and with the SQLite prompt -> <out>/control/<model>/<prompt>/; prints alternatives
    offered and both interpretations returned, against the first run's saved answers."""
    import concurrent.futures as cf, random, time
    from specbridge.comm.common import db as DB
    from specbridge.comm.common.llm import call, parse
    from specbridge.comm.transfer import reviewed as RV
    C = {c["case"]: c for c in json.load(open(D + "/eval/frozen.json"))["cases"]}; W = json.load(open(D + "/written.json"))
    ks = random.Random(seed).sample(RV.accepted(sorted(k for k in C if C[k]["database"] not in LIVE)), n)
    first = X.INSTRUCTION; sqlite = first.replace(OLD, NEW)
    def one(job):
        k, name, prompt = job; f = "%s_control/%s/%s/%s.json" % (OUT, model, name, k.replace(":", "__").replace("/", "_"))
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); con = DB.connect(c["snapshot"])
        txt = call(prompt % (schema, docs, W[k]["open"]), model)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; a = DB.rows(con, r.get("sql")) if r.get("sql") else None
        alts = [{"executes": b is not None, "matches": X._match(c, b)} for x in (r.get("alternatives") or [])[:2] if isinstance(x, dict) and x.get("sql")
                for b in [DB.rows(con, x["sql"])]]
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"case": k, "prompt": name, "primary_matches": X._match(c, a), "alternatives": alts}, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, [(k, nm, p) for k in ks for nm, p in (("first", first), ("sqlite", sqlite))]))
    got = lambda o: set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]}
    res = {}
    for nm in ("saved", "first", "sqlite"):
        os_ = []
        for k in ks:
            p = (D + "/disclose/%s/%s__open.json" % (model, k.replace(":", "__").replace("/", "_"))) if nm == "saved" else \
                "%s_control/%s/%s/%s.json" % (OUT, model, nm, k.replace(":", "__").replace("/", "_"))
            if os.path.exists(p): os_.append(json.load(open(p)))
        res[nm] = {"n": len(os_), "alternatives": sum(len(o["alternatives"]) for o in os_), "both": sum({"A", "B"} <= got(o) for o in os_)}
    json.dump(res, open("%s_control/%s/result.json" % (OUT, model), "w"), indent=1); print(model, res)



def merge():
    """Put the SQLite rerun in place of the first run for the accepted LiveSQLBench sets: answers (explanation, SQL-only, matched,
    sampled) and their judge entries. Each replaced first-run file or entry is moved to out/archive/first-run-livesql/<path>."""
    import glob, shutil
    A = "out/archive/first-run-livesql"; ks = set(live_cases()); base = D + "/disclose"; n = 0
    name = lambda k: k.replace(":", "__").replace("/", "_")
    for sub in ("", "plain/", "complement/", "topk/"):
        for m in MODELS:
            for f in glob.glob("%s/%s%s/*.json" % (OUT, sub, m)):
                o = json.load(open(f))
                if o["case"] not in ks: continue
                dst = "%s/%s%s/%s" % (base, sub, m, os.path.basename(f))
                if os.path.exists(dst):
                    a = os.path.join(A, dst); os.makedirs(os.path.dirname(a), exist_ok=True); shutil.move(dst, a)
                shutil.copy2(f, dst); n += 1
    for jf in ("judge.json", "judge_alternatives.json"):
        J = json.load(open(base + "/" + jf)); N = json.load(open(OUT + "/" + jf))
        old = {k: v for k, v in J.items() if k.split("|")[0] in ks}
        os.makedirs(os.path.join(A, base), exist_ok=True); json.dump(old, open(os.path.join(A, base, jf), "w"), indent=1)
        J = {k: v for k, v in J.items() if k.split("|")[0] not in ks}; J.update({k: v for k, v in N.items() if k.split("|")[0] in ks})
        json.dump(J, open(base + "/" + jf, "w"), indent=1)
    json.dump({"sets": sorted(ks), "files_copied": n, "prompt": [OLD, NEW]}, open(A + "/MANIFEST.json", "w"), indent=1)
    print("merged", n, "answers for", len(ks), "sets")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "run": run(a[1] if len(a) > 1 else None, int(a[2]) if len(a) > 2 else 6)
    elif a[0] == "control": control(*(a[1:2] or ["haiku"]))
    elif a[0] == "retry":                                    # re-ask failed (empty) replies for one model, every stage
        for f in __import__("glob").glob(OUT + "/%s/*.json" % a[1]):
            if not json.load(open(f))["response"]: os.remove(f)
        MODELS[:] = [a[1]]
        for st in STAGES[:4]: run(st, 6)
    else: {"sample": sample, "compare": compare, "merge": merge}[a[0]]()

