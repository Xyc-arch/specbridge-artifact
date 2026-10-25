"""THE DIAGNOSTIC LADDER on the 215 request sets (2026-10-14; gate: out/ladder/GATE.md). Answers a reviewer's three questions
without human raters:
  check    STRUCTURE, by code, no model: p_A and p_B differ in one step of the SQL; q_B is q_A with the recorded choice edits applied
           (nothing else changes). q_open is a natural wording; that it keeps the shared requirements is a reviewer check (recorded).
  detect   NOTICE: the model, asked directly and without writing SQL, says whether the request leaves a calculation choice open and
           names it. Run on the open request and, as a false-alarm control, on the set's specific request (the one of the
           explanation run). One call per (set, wording, model).
  judge    does a named choice match THIS set's choice? opus on all, gpt-6-sol on a fixed 30% sample (agreement); blind to the model.
  supplied READINGS SUPPLIED on a fixed 100-set sample: the open request plus both readings in words (no SQL, random order);
           SQL for each, scored by execution.
  report   the ladder per model: plain answer -> explanation call -> detection -> readings supplied -> specific requests.
    python -m specbridge.comm.transfer.ladder check | detect | judge | supplied | report
Every model call records its usage (specbridge.pd.ask.USAGE): resolved model, tokens, list cost, seconds."""
import collections, concurrent.futures as cf, difflib, glob, hashlib, json, os, random, re, sys, time
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X

D = "out/transfer/eval12-v2/render"; OUT = "out/ladder"; MODELS = ("haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"); SEED = 20261014

DETECT = """Read the data request below for the database below. Do not write SQL.
Does the request leave open a calculation choice -- a point that the request and the supplied context do not settle, where two
reasonable readings would compute different answers? Name each such choice and its two readings. Say "open": false when the
request and context settle every such point.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

Answer ONLY JSON: {"open": true|false, "choices": [{"choice": "the point left open", "reading_1": "...", "reading_2": "..."}]}
At most three choices; an empty list when "open" is false."""

SUPPLIED = """Answer the request with SQL for the database below. The request can be read in two ways, described below. Give one SQL
query for each reading.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

READING 1: %s
READING 2: %s

Answer ONLY JSON: {"reading_1_sql": "...", "reading_2_sql": "..."}"""

MATCH = """You judge whether a list of choices that someone named for a data request includes ONE specific choice. For each ITEM you
get the request, the specific DECISION (with its two readings), and the named choices. You are not told who named them.
  match   does any named choice describe THIS decision (the same point, with readings that correspond to the two readings)?
          A different point, or a vague mention that does not identify this decision, is false. true|false
Answer ONLY JSON: [{"id": "...", "match": true|false, "why": "one sentence"}]

%s"""


def _key(k): return k.replace(":", "__").replace("/", "_")


def _data():
    fz, wr, out = X._paths(D)
    C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); S = json.load(open(out + "/sample.json"))
    return C, W, S


# ---------------------------------------------------------------- STRUCTURE (no model)
def _steps(sql):
    """The query's steps: each CTE body by name, and the final statement, as normalized SQL."""
    import sqlglot
    t = sqlglot.parse_one(sql, read="sqlite"); w = t.args.get("with"); steps = {}
    if w:
        for cte in w.expressions: steps[cte.alias] = cte.this.sql(dialect="sqlite")
        t = t.copy(); t.set("with", None)
    steps["<final>"] = t.sql(dialect="sqlite")
    return steps


def _norm(s): return re.sub(r"\s+", " ", s or "").strip()


def check():
    C, W, _S = _data(); rows = []
    for k, c in sorted(C.items()):
        w = W[k]; r = {"case": k, "type": c.get("type")}
        try:
            a, b = _steps(c["sql_A"]), _steps(c["sql_B"])
            r["steps"] = len(a); r["steps_changed"] = sum(a.get(n) != b.get(n) for n in set(a) | set(b))
        except Exception as e:
            r["steps_changed"] = None; r["parse_error"] = str(e)[:100]
        qa = _norm(w["precise_A"])
        for e in w.get("edits_B") or []: qa = qa.replace(_norm(e["from"]), _norm(e["to"]))
        r["qB_is_qA_with_edits"] = qa == _norm(w["precise_B"])
        sm = difflib.SequenceMatcher(None, _norm(w["precise_A"]).split(), _norm(w["precise_B"]).split())
        r["text_regions_changed"] = sum(op != "equal" for op, *_x in sm.get_opcodes())
        r["choice_components"] = (len(w.get("choice_A") or []), len(w.get("choice_B") or []))
        r["open_missing_components"] = len(w.get("missing_components") or [])
        r["edits"] = len(w.get("edits_B") or [])
        rows.append(r)
    os.makedirs(OUT, exist_ok=True); json.dump(rows, open(OUT + "/structure.json", "w"), indent=1)
    n = len(rows); cnt = collections.Counter
    print("sets", n)
    print("SQL steps changed:", dict(cnt(r["steps_changed"] for r in rows)))
    print("q_B = q_A with the recorded edits:", sum(r["qB_is_qA_with_edits"] for r in rows))
    print("edits per set:", dict(cnt(r["edits"] for r in rows)), " changed text regions:", dict(cnt(r["text_regions_changed"] for r in rows)))
    print("choice components (A, B):", dict(cnt(r["choice_components"] for r in rows)))
    print("open request: reviewer-recorded missing requirements = 0:", sum(r["open_missing_components"] == 0 for r in rows))
    ok = [r["case"] for r in rows if r["steps_changed"] == 1 and r["qB_is_qA_with_edits"]]
    print("pass (one SQL step and q_B = q_A + edits):", len(ok))
    json.dump(ok, open(OUT + "/structure_pass.json", "w"))


# ---------------------------------------------------------------- model runs
def _call(prompt, m):
    from specbridge.pd.ask import ask, USAGE
    txt = ask(prompt, m, timeout=1500, quiet=True)
    return txt, dict(getattr(USAGE, "last", {}) or {})


def detect(workers=6):
    from specbridge.comm.common.llm import parse
    C, W, S = _data(); jobs = [(k, wd, m) for k in sorted(C) for wd in S["wordings"][k] for m in MODELS]
    random.Random(SEED).shuffle(jobs)
    def one(j):
        k, wd, m = j; f = "%s/detect/%s/%s__%s.json" % (OUT, m, _key(k), wd)
        if os.path.exists(f): return
        schema, docs = DB.context(C[k]); txt, u = _call(DETECT % (schema, docs, W[k][wd]), m)
        if not txt: return                                       # a failed call is not an answer: not saved, retried on rerun
        r = parse(txt, "{")
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"case": k, "wording": wd, "model": m, "response": r, "raw": None if r else txt, "usage": u}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(one, jobs))


def _detections():
    R = {}
    for f in glob.glob(OUT + "/detect/*/*.json"):
        o = json.load(open(f)); R[(o["case"], o["wording"], o["model"])] = o
    return R


def judge(workers=6, judges=("opus", "gpt-6-sol")):
    """Only responses that say "open" with at least one named choice need a judge; the rest cannot match."""
    from specbridge.comm.common.llm import parse
    C, W, S = _data(); R = _detections()
    for jm in judges:
        jf = "%s/judge_%s.json" % (OUT, jm); J = json.load(open(jf)) if os.path.exists(jf) else {}
        keys = sorted(k for k, o in R.items() if (o["response"] or {}).get("open") and (o["response"] or {}).get("choices") and "|".join(k) not in J)
        if jm != "opus":                                         # the second judge: a fixed 30% sample, for agreement only (cost)
            keys = [k for k in keys if int(hashlib.sha1("|".join(k).encode()).hexdigest(), 16) % 10 < 3]
        anon = {k: hashlib.sha1(("|".join(k) + jm).encode()).hexdigest()[:10] for k in keys}
        rng = random.Random(SEED); rng.shuffle(keys)
        def block(k):
            w = W[k[0]]; ch = (R[k]["response"] or {}).get("choices") or []
            return "--- %s\nREQUEST: %s\nDECISION: reading A = %s | reading B = %s\nNAMED CHOICES: %s" % (
                anon[k], w[k[1]], w["reading_A"], w["reading_B"], json.dumps(ch[:3])[:1500])
        def one(b):
            txt, u = _call(MATCH % "\n\n".join(block(k) for k in b), jm); got = parse(txt, "[") or []
            back = {anon[k]: k for k in b}
            return {"|".join(back[g["id"]]): dict(g, usage=u) for g in got if isinstance(g, dict) and g.get("id") in back}
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for d in ex.map(one, [keys[i:i + 5] for i in range(0, len(keys), 5)]): J.update(d)
        json.dump(J, open(jf, "w"), indent=1); print(jm, "judged", len(J))


def supplied(workers=6):
    from specbridge.comm.common.llm import parse
    C, W, S = _data(); sub = sorted(C); random.Random(SEED + 2).shuffle(sub); sub = sorted(sub[:100])   # a fixed 100-set sample (cost)
    jobs = [(k, m) for k in sub for m in MODELS]; random.Random(SEED + 1).shuffle(jobs)
    def one(j):
        k, m = j; f = "%s/supplied/%s/%s.json" % (OUT, m, _key(k))
        if os.path.exists(f): return
        c = C[k]; w = W[k]; flip = random.Random(SEED + hash(k) % 1000).random() < 0.5      # order of the two readings
        r1, r2 = ("B", "A") if flip else ("A", "B")
        schema, docs = DB.context(c); txt, u = _call(SUPPLIED % (schema, docs, w["open"], w["reading_" + r1], w["reading_" + r2]), m)
        if not txt: return
        r = parse(txt, "{") or {}; con = DB.connect(c["snapshot"]); got = {}
        for slot, want in (("reading_1_sql", r1), ("reading_2_sql", r2)):
            q = r.get(slot); rows = DB.rows(con, q) if q else None
            got[want] = {"sql": q, "runs": rows is not None, "matches": X._match(c, rows) if rows is not None else []}
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"case": k, "model": m, "order": [r1, r2], "answers": got, "raw": None if r else txt, "usage": u}, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(one, jobs))


# ---------------------------------------------------------------- report
def _L(x):
    import ast
    if isinstance(x, str):
        try: return ast.literal_eval(x)
        except Exception: return []
    return x or []


def _wilson(k, n, z=1.96):
    if not n: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / d
    return (round(100 * (c - h), 1), round(100 * (c + h), 1))


def report():
    C, W, S = _data(); dd = X._paths(D)[2]; R = _detections(); Jd = json.load(open(dd + "/judge.json"))
    J = {jm: (json.load(open("%s/judge_%s.json" % (OUT, jm))) if os.path.exists("%s/judge_%s.json" % (OUT, jm)) else {}) for jm in ("opus", "gpt-6-sol")}
    def right(p, r): return None if not os.path.exists(p) else r in _L(json.load(open(p))["primary_matches"])
    res = {}; L = ["# Diagnostic ladder on the 215 request sets (gate: out/ladder/GATE.md)\n",
                   "| model | plain: A or B | explanation: both | explanation: names it | detect: open | detect: this choice (opus) | detect: this choice (gpt-6-sol) | false alarm on specific (opus) | readings supplied: both | specific: both |",
                   "|---|---|---|---|---|---|---|---|---|---|"]
    agree = collections.Counter(); usage = collections.defaultdict(lambda: collections.Counter())
    for m in MODELS:
        c = collections.Counter(); prim = collections.Counter(); miss = collections.Counter()
        for k in sorted(C):
            b = _key(k); spec_w = [w for w in S["wordings"][k] if w != "open"][0]
            pl = dd + "/plain/%s/%s__open.json" % (m, b); plo = json.load(open(pl)) if os.path.exists(pl) else None
            c["plain"] += bool(plo and set(_L(plo["primary_matches"])) & {"A", "B"})
            o = json.load(open(dd + "/%s/%s__open.json" % (m, b))); got = set(_L(o["primary_matches"]))
            for a in _L(o["alternatives"]): got |= set(a.get("matches") or [])
            both = {"A", "B"} <= got; c["both"] += both
            c["names"] += bool((Jd.get("%s|open|%s" % (k, m)) or {}).get("flags_decision"))
            sp = {}
            for r in "AB":
                for d2 in (dd + "/" + m, dd + "/complement/" + m):
                    v = right("%s/%s__precise_%s.json" % (d2, b, r), r)
                    if v is not None: sp[r] = v
            spec = bool(sp.get("A") and sp.get("B")); c["spec"] += spec
            do = R.get((k, "open", m)); ds = R.get((k, spec_w, m))
            for o2 in (do, ds):
                if o2: usage[m].update({kk: v for kk, v in (o2.get("usage") or {}).items() if isinstance(v, (int, float))})
            says = bool(do and (do["response"] or {}).get("open")); c["says_open"] += says; c["detect_n"] += do is not None
            mt = {jm: bool((J[jm].get("%s|open|%s" % (k, m)) or {}).get("match")) for jm in J}
            c["det_opus"] += mt["opus"]; c["det_gpt"] += mt["gpt-6-sol"]
            if says and (do["response"] or {}).get("choices") and "%s|open|%s" % (k, m) in J["gpt-6-sol"]: agree[mt["opus"] == mt["gpt-6-sol"]] += 1
            c["ctrl_n"] += ds is not None
            c["ctrl_says_open"] += bool(ds and (ds["response"] or {}).get("open"))
            c["ctrl_opus"] += bool((J["opus"].get("%s|%s|%s" % (k, spec_w, m)) or {}).get("match"))
            sf = "%s/supplied/%s/%s.json" % (OUT, m, b)
            if os.path.exists(sf):
                so = json.load(open(sf)); c["sup_n"] += 1
                c["sup_both"] += all(r in so["answers"][r]["matches"] for r in "AB")
                usage[m].update({kk: v for kk, v in (so.get("usage") or {}).items() if isinstance(v, (int, float))})
            if mt["opus"] and spec: prim["n"] += 1; prim["both"] += both
            if spec and not both: miss["n"] += 1; miss["detected"] += mt["opus"]; miss["named_in_answer"] += c["names"] and bool((Jd.get("%s|open|%s" % (k, m)) or {}).get("flags_decision"))
        n = len(C); res[m] = {"counts": dict(c), "primary": dict(prim), "missed": dict(miss)}
        pc = lambda a, b: "%d/%d (%.0f%%)" % (a, b, 100 * a / b) if b else "-"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (m, pc(c["plain"], n), pc(c["both"], n), pc(c["names"], n), pc(c["says_open"], c["detect_n"]),
                 pc(c["det_opus"], c["detect_n"]), pc(c["det_gpt"], c["detect_n"]), pc(c["ctrl_opus"], c["ctrl_n"]), pc(c["sup_both"], c["sup_n"]), pc(c["spec"], n)))
    L.append("\n## Primary quantity: detected open with this choice (opus) and both specific right -> explanation call returns both\n")
    for m in MODELS:
        p = res[m]["primary"]; q = res[m]["missed"]
        L.append("- %s: both returned in %d of %d (%.1f%%, Wilson %s); of %d computable misses, the model detects the choice in %d (%.1f%%, Wilson %s)" % (
            m, p.get("both", 0), p.get("n", 0), 100 * p.get("both", 0) / max(1, p.get("n", 0)), _wilson(p.get("both", 0), p.get("n", 0)),
            q.get("n", 0), q.get("detected", 0), 100 * q.get("detected", 0) / max(1, q.get("n", 0)), _wilson(q.get("detected", 0), q.get("n", 0))))
    L.append("\nJudge agreement (opus vs gpt-6-sol) on responses that name choices: %d of %d" % (agree[True], sum(agree.values())))
    L.append("\nUsage of the new runs (detection + readings supplied): " + "; ".join("%s: %s" % (m, {k: round(v, 2) for k, v in usage[m].items()}) for m in MODELS))
    json.dump(res, open(OUT + "/results.json", "w"), indent=1); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"check": check, "detect": detect, "judge": judge, "supplied": supplied, "report": report}[sys.argv[1]]()
