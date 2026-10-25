"""WHAT ACCOUNTS FOR SPIDER 2.0 ERRORS (2026-10-13). Step 1: a baseline answer for all 135 SQLite tasks (Sonnet, disclose.PLAIN:
schema with example rows, the task's knowledge document, SQL only, one call, no exploration). Step 2: every failure labelled by two
independent labellers with an actionable taxonomy, from the question, the knowledge document, the model's SQL and result, the head of
EVERY accepted reading, and the released gold SQL when there is one. Each label also says whether inspecting the data would likely
have fixed it (what exploration could buy).
    python -m specbridge.comm.transfer.errors run      -> out/spider2/errors/plain/<id>.json
    python -m specbridge.comm.transfer.errors label    -> out/spider2/errors/labels.json, ERRORS.md"""
import collections, concurrent.futures as cf, hashlib, json, math, os, random, sqlite3, sys, time
from specbridge.comm.transfer import spider2 as S, disclose as X

OUT = "out/spider2/errors"; MODEL = "sonnet"; SEED = 20261021
CAUSES = ["scorer or gold artifact", "output form", "open meaning choice", "wrong column or table", "stored value or format",
          "calculation logic", "missed knowledge definition", "data quirk", "dialect or timeout", "incomplete answer"]
LABEL = """You diagnose why a text-to-SQL answer on Spider 2.0 (SQLite) was scored wrong. The scorer accepts ANY of the listed accepted
answers; it allows extra columns in the model's result but compares values (numbers within 0.01). For each item pick the ONE main cause:
  scorer or gold artifact      the model's result is in fact equivalent to an accepted answer, or the accepted answers look wrong
  output form                  right computation, but the result's form fails the comparison (rounding, units like a fraction vs a percentage, missing required column, row granularity)
  open meaning choice          the request allows the model's reading, but the benchmark accepts only other readings
  wrong column or table        a different column, table or join path than the request means
  stored value or format       the right column, but the stored value or its format is matched wrongly (codes, case, dates as text)
  calculation logic            the formula, window, aggregation level, filter or step is computed wrongly
  missed knowledge definition  the knowledge document defines the computation and the model did not follow it
  data quirk                   NULLs, duplicates, dirty or inconsistent data the SQL does not handle
  dialect or timeout           the SQL does not run in SQLite or is too slow
  incomplete answer            the SQL answers only part of the request
Also: would inspecting the data first (running a few exploratory queries) likely have fixed it? yes | no.
Answer ONLY JSON: [{"id": "...", "cause": "...", "data_inspection_would_fix": "yes|no", "why": "one sentence"}]

%s"""


def _f(iid): return "%s/plain/%s.json" % (OUT, iid)


def run(workers=6):
    from specbridge.comm.common.llm import call, parse
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; ctx = {}
    ids = sorted(T); random.Random(SEED).shuffle(ids)
    for i in ids: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    def one(iid):
        f = _f(iid)
        if os.path.exists(f): return
        t = T[iid]; t0 = time.time(); txt = call(X.PLAIN % (ctx[t["db"]], S.docs(t), t["question"]), MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; G, io = S.golds(iid, E); df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"instance_id": iid, "sql": r.get("sql"), "runs": df is not None, "matches": S.matches(df, G, io),
                   "head": None if df is None else df.head(6).to_csv(index=False)[:900], "shape": None if df is None else list(df.shape),
                   "seconds": round(time.time() - t0, 1)}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, ids))
    done = [json.load(open(_f(i))) for i in ids if os.path.exists(_f(i))]
    print("answered %d/%d, right %d, does not run %d" % (len(done), len(ids), sum(bool(o["matches"]) for o in done), sum(not o["runs"] for o in done)))


def label(batch=5, labellers=("opus", "gpt-6-sol")):
    from specbridge.comm.common.llm import ask_json
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}
    A = json.load(open("out/spider2/audit.json")) if os.path.exists("out/spider2/audit.json") else {}
    done = [json.load(open(_f(i))) for i in sorted(T) if os.path.exists(_f(i))]; fails = [o for o in done if not o["matches"]]
    def item(o):
        iid = o["instance_id"]; t = T[iid]; G, io = S.golds(iid, E); lab = S.distinct(G, io); reps = sorted(set(lab.values()))
        acc = "\n".join("ACCEPTED ANSWER %d (shape %s):\n%s" % (k + 1, list(G[r][0].shape), G[r][0].head(5).to_csv(index=False)[:700]) for k, r in enumerate(reps[:3]))
        gs = S.GOLD + "/sql/%s.sql" % iid
        return "--- %s\nREQUEST: %s\nKNOWLEDGE DOCUMENT: %s\nMODEL SQL: %s\nMODEL RESULT (%s): %s\n%s\nRELEASED GOLD SQL: %s" % (
            iid, t["question"], S.docs(t)[:1200] if t.get("external_knowledge") else "(none)", (o["sql"] or "(none)")[:2500],
            "does not run" if not o["runs"] else "shape %s" % o["shape"], o["head"] or "", acc, open(gs).read()[:1500] if os.path.exists(gs) else "(not released)")
    out = {}
    for lab_ in labellers:
        got = {}
        def one(b):
            r = ask_json(LABEL % "\n\n".join(item(o) for o in b), lab_, brace="[") or []
            return {x["id"]: x for x in r if isinstance(x, dict) and "id" in x}
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for d in ex.map(one, [fails[k:k + batch] for k in range(0, len(fails), batch)]): got.update(d)
        out[lab_] = got
    ids = [o["instance_id"] for o in fails]; l1, l2 = labellers
    both = lambda c: sum(out[l1].get(i, {}).get("cause") == c and out[l2].get(i, {}).get("cause") == c for i in ids)
    either = lambda c: sum(out[l1].get(i, {}).get("cause") == c or out[l2].get(i, {}).get("cause") == c for i in ids)
    agree = sum(out[l1].get(i, {}).get("cause") == out[l2].get(i, {}).get("cause") for i in ids)
    L = ["# What accounts for Spider 2.0 errors (`specbridge.comm.transfer.errors`), Sonnet, SQL only, no exploration\n",
         "%d tasks answered, %d right, %d wrong. Two independent labellers (%s); agreement on the cause %d/%d.\n" % (len(done), len(done) - len(fails), len(fails), " and ".join(labellers), agree, len(ids)),
         "| cause | %s | %s | both agree | either |" % labellers, "|---|---|---|---|---|"]
    for c in CAUSES:
        L.append("| %s | %d | %d | %d | %d |" % (c, sum(out[l1].get(i, {}).get("cause") == c for i in ids), sum(out[l2].get(i, {}).get("cause") == c for i in ids), both(c), either(c)))
    L += ["", "Data inspection would likely fix: %s." % "; ".join("%s %d/%d" % (l, sum(out[l].get(i, {}).get("data_inspection_would_fix") == "yes" for i in ids), len(ids)) for l in labellers),
          "", "By audit class of the task (meaning-different / format only / single answer):",
          "- " + ", ".join("%s %d" % kv for kv in collections.Counter((A.get(i) or {}).get("class", "?") for i in ids).items()),
          "", "| task | %s | %s |" % labellers, "|---|---|---|"]
    L += ["| %s | %s (%s): %s | %s (%s): %s |" % (i, *(x for l in labellers for x in (out[l].get(i, {}).get("cause"), out[l].get(i, {}).get("data_inspection_would_fix"), (out[l].get(i, {}).get("why") or "")[:120]))) for i in ids]
    os.makedirs(OUT, exist_ok=True); json.dump({"failures": ids, "labels": out}, open(OUT + "/labels.json", "w"), indent=1)
    open(OUT + "/ERRORS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:20]))



# --- STEP A: the agentic baseline (2026-10-13) ---------------------------------------------------------------------------------
# The standard exploration harness (specbridge.comm.common.solve: up to 6 rounds, up to 5 exploratory queries per round, 20 visible rows)
# on the 45 failures + 30 correct tasks (seeded). The task's knowledge document is appended to the request (the harness's own
# documentation slot is empty for these databases). Characters in/out are counted per task by wrapping the harness's model call.
import threading
_TL = threading.local()


def _counted(orig):
    def call(prompt, model):
        txt = orig(prompt, model)
        c = getattr(_TL, "c", None)
        if c is not None: c["calls"] += 1; c["chars_in"] += len(prompt); c["chars_out"] += len(txt or "")
        return txt
    return call


def agent_ids(n_right=30):
    T = S.tasks(); done = [json.load(open(_f(i))) for i in sorted(T) if os.path.exists(_f(i))]
    wrong = sorted(o["instance_id"] for o in done if not o["matches"]); right = sorted(o["instance_id"] for o in done if o["matches"])
    random.Random(SEED + 1).shuffle(right); return wrong, right[:n_right]


def run_agent(workers=6):
    from specbridge.comm.common import solve as SV
    SV.call = _counted(SV.call)
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}
    wrong, right = agent_ids(); out = OUT + "/agent"
    def one(iid):
        f = "%s/%s.json" % (out, iid)
        if os.path.exists(f) and "matches" in json.load(open(f)): return
        t = T[iid]; text = t["question"] + ("\n\nKNOWLEDGE DOCUMENT:\n" + S.docs(t) if t.get("external_knowledge") else "")
        _TL.c = collections.Counter(); t0 = time.time()
        r = SV.solve([{"key": iid, "text": text, "snapshot": "%s/%s.sqlite" % (S.DBDIR, t["db"]), "database": t["db"]}], MODEL, out, bsize=1, workers=1)
        if iid not in r: return
        o = r[iid]; G, io = S.golds(iid, E); df = S.run_sql(t["db"], o.get("final")) if o.get("final") else None
        o.update(matches=S.matches(df, G, io), runs_final=df is not None, cost=dict(_TL.c), seconds=round(time.time() - t0, 1))
        json.dump(o, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, wrong + right))
    report_agent()


def report_agent():
    wrong, right = agent_ids(); out = OUT + "/agent"; Lb = json.load(open(OUT + "/labels.json"))["labels"]; l1, l2 = list(Lb)
    agreed = lambda i: Lb[l1].get(i, {}).get("cause") if Lb[l1].get(i, {}).get("cause") == Lb[l2].get(i, {}).get("cause") else "labellers disagree"
    load = lambda i: json.load(open("%s/%s.json" % (out, i))) if os.path.exists("%s/%s.json" % (out, i)) else None
    W = {i: load(i) for i in wrong}; R = {i: load(i) for i in right}; W = {i: o for i, o in W.items() if o and "matches" in o}; R = {i: o for i, o in R.items() if o and "matches" in o}
    by = collections.defaultdict(lambda: [0, 0])
    for i, o in W.items(): by[agreed(i)][0] += 1; by[agreed(i)][1] += bool(o["matches"])
    cost = lambda D, k: sum(o["cost"].get(k, 0) for o in D.values()) / max(1, len(D))
    L = ["# Step A: agentic baseline (exploration harness, Sonnet) on Spider 2.0 (`errors run_agent`)\n",
         "Failures fixed: %d of %d. Correct tasks broken: %d of %d.\n" % (sum(bool(o["matches"]) for o in W.values()), len(W), sum(not o["matches"] for o in R.values()), len(R)),
         "| agreed cause (baseline failure) | failures | fixed by the agent |", "|---|---|---|"]
    L += ["| %s | %d | %d |" % (c, v[0], v[1]) for c, v in sorted(by.items(), key=lambda kv: -kv[1][0])]
    allo = list(W.values()) + list(R.values())
    L += ["", "Per task: rounds %.1f, model calls %.1f, characters in %d / out %d (about 4 characters per token); seconds %.0f." % (
        sum(o.get("turns", 0) for o in allo) / max(1, len(allo)), cost({**W, **R}, "calls"), cost({**W, **R}, "chars_in"), cost({**W, **R}, "chars_out"),
        sum(o.get("seconds", 0) for o in allo) / max(1, len(allo))),
          "For comparison, the one-call baseline: about %d characters in per task." % (sum(len(X.PLAIN) + len(S.context(S.tasks()[i]["db"])) for i in list(W)[:10]) / max(1, min(10, len(W))))]
    open(OUT + "/AGENT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- STEP B: the expectations gate (2026-10-13) --------------------------------------------------------------------------------
# On the failures the agent did not fix + the 30 correct tasks: ONE call per task writes a plan of <= 6 steps with checkable
# expectations per step and CTEs s1..sk implementing it. Code runs each step's CTE prefix and checks every expectation. Question:
# are expectations violated far more often when the resulting SQL is wrong than when it is right? (V wording check: not possible
# here -- Spider 2.0 databases have no catalogue.)
PLAN = """Answer the request with SQL for the database below, in two linked parts.
PLAN: at most 6 numbered steps s1..s6, each one sentence saying exactly what the step computes, with CHECKABLE EXPECTATIONS about its
result that must hold if the step is right. Expectation kinds (use only these):
  {"kind": "rows", "op": "=|<=|>=", "value": N}                       number of rows of the step's result
  {"kind": "unique", "columns": ["col", ...]}                         these columns identify each row (no duplicates)
  {"kind": "not_null", "columns": ["col", ...]}                       no NULLs in these columns
  {"kind": "range", "column": "col", "min": x, "max": y}              every value within [min, max] (omit a bound you do not know)
  {"kind": "same_rows_as", "step": "sK"}                              as many rows as step sK (a join or filter keeps every row)
SQL: one query WITH s1 AS (...), s2 AS (...), ... SELECT ... FROM <last step>; each CTE implements the plan step of the same name.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

Answer ONLY JSON: {"plan": [{"step": "s1", "does": "...", "expect": [ ... ]}], "sql": "WITH s1 AS (...) ... SELECT ..."}"""


def _check(db, sql, plan):
    """Every expectation of every step, checked on that step's CTE prefix. -> list of {step, kind, ok (True/False/None)}"""
    import sqlglot
    try: q = sqlglot.parse_one(sql, read="sqlite") if sql else None
    except Exception: q = None                                   # unparseable: no step can be checked
    w = (q.args.get("with") or q.args.get("with_")) if q is not None else None
    ctes = {c.alias: k for k, c in enumerate(w.expressions)} if w else {}; out = []; rows = {}
    def stepq(name, body):
        k = ctes[name]; return "WITH " + ", ".join(c.sql(dialect="sqlite") for c in w.expressions[:k + 1]) + " " + body
    def one(name, body):
        if name not in ctes: return None
        try:
            con = sqlite3.connect("file:%s/%s.sqlite?mode=ro" % (S.DBDIR, db), uri=True); t0 = time.time()
            con.set_progress_handler(lambda: 1 if time.time() - t0 > 30 else 0, 100000)
            try: return con.execute(stepq(name, body)).fetchall()
            finally: con.close()
        except Exception: return None
    for st in plan or []:
        if not isinstance(st, dict): continue
        nm = st.get("step")
        for e in st.get("expect") or []:
            if not isinstance(e, dict): continue
            k = e.get("kind"); ok = None
            try:
                if k == "rows":
                    r = one(nm, "SELECT COUNT(*) FROM %s" % nm); n = r[0][0] if r else None; v = float(e["value"])
                    ok = None if n is None else {"=": n == v, "<=": n <= v, ">=": n >= v}.get(e.get("op", "="))
                elif k == "unique":
                    cols = ", ".join('"%s"' % c for c in e["columns"]); r = one(nm, "SELECT COUNT(*) FROM (SELECT %s FROM %s GROUP BY %s HAVING COUNT(*) > 1)" % (cols, nm, cols)); ok = None if r is None else r[0][0] == 0
                elif k == "not_null":
                    cond = " OR ".join('"%s" IS NULL' % c for c in e["columns"]); r = one(nm, "SELECT COUNT(*) FROM %s WHERE %s" % (nm, cond)); ok = None if r is None else r[0][0] == 0
                elif k == "range":
                    c = '"%s"' % e["column"]; cond = " OR ".join(x for x in (("%s < %s" % (c, float(e["min"]))) if e.get("min") is not None else "", ("%s > %s" % (c, float(e["max"]))) if e.get("max") is not None else "") if x)
                    r = one(nm, "SELECT COUNT(*) FROM %s WHERE %s" % (nm, cond)) if cond else None; ok = None if r is None else r[0][0] == 0
                elif k == "same_rows_as":
                    a = one(nm, "SELECT COUNT(*) FROM %s" % nm); b = one(e["step"], "SELECT COUNT(*) FROM %s" % e["step"]); ok = None if not (a and b) else a[0][0] == b[0][0]
            except Exception: ok = None
            out.append({"step": nm, "kind": k, "ok": ok})
    return out


def run_gate(workers=6):
    from specbridge.comm.common.llm import call, parse
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}
    wrong, right = agent_ids(); ag = lambda i: json.load(open("%s/agent/%s.json" % (OUT, i)))
    todo = [i for i in wrong if not ag(i)["matches"]] + right; ctx = {}
    for i in todo: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    def one(iid):
        f = "%s/gate/%s.json" % (OUT, iid)
        if os.path.exists(f): return
        t = T[iid]; p = PLAN % (ctx[t["db"]], S.docs(t), t["question"]); txt = call(p, MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; sql = r.get("sql"); G, io = S.golds(iid, E); df = S.run_sql(t["db"], sql) if sql else None
        o = {"instance_id": iid, "group": "unfixed failure" if iid in wrong else "baseline correct", "plan": r.get("plan"), "sql": sql, "runs": df is not None,
             "matches": S.matches(df, G, io), "checks": _check(t["db"], sql, r.get("plan")) if sql else [], "chars_in": len(p), "chars_out": len(txt)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, todo))
    report_gate()


def report_gate():
    import glob
    O = [json.load(open(f)) for f in glob.glob(OUT + "/gate/*.json")]; O = [o for o in O if o.get("sql")]
    W = [o for o in O if not o["matches"]]; R = [o for o in O if o["matches"]]
    viol = lambda o: any(c["ok"] is False for c in o["checks"]); checked = lambda o: sum(c["ok"] is not None for c in o["checks"])
    L = ["# Step B: expectations gate on Spider 2.0 (`errors run_gate`), Sonnet, one call per task\n",
         "%d tasks with SQL (%d unfixed failures, %d baseline-correct). The gate's own SQL is scored; expectations checked on each step's CTE prefix.\n" % (
             len(O), sum(o["group"] == "unfixed failure" for o in O), sum(o["group"] == "baseline correct" for o in O)),
         "| gate SQL | tasks | any expectation violated | expectations checkable per task | violated / checked |", "|---|---|---|---|---|"]
    for lab, X_ in (("wrong", W), ("right", R)):
        ch = sum(checked(o) for o in X_); vi = sum(sum(c["ok"] is False for c in o["checks"]) for o in X_)
        L.append("| %s | %d | %d (%.0f%%) | %.1f | %d / %d (%.0f%%) |" % (lab, len(X_), sum(viol(o) for o in X_), 100 * sum(viol(o) for o in X_) / max(1, len(X_)), ch / max(1, len(X_)), vi, ch, 100 * vi / max(1, ch)))
    L += ["", "By group: " + "; ".join("%s: %d tasks, gate SQL right %d" % (g, sum(o["group"] == g for o in O), sum(o["group"] == g and bool(o["matches"]) for o in O)) for g in ("unfixed failure", "baseline correct")),
          "By kind (violated / checked): " + ", ".join("%s %d/%d" % (k, sum(c["ok"] is False for o in O for c in o["checks"] if c["kind"] == k), sum(c["ok"] is not None for o in O for c in o["checks"] if c["kind"] == k)) for k in ("rows", "unique", "not_null", "range", "same_rows_as")),
          "Characters in / out per task: %d / %d." % (sum(o["chars_in"] for o in O) / max(1, len(O)), sum(o["chars_out"] for o in O) / max(1, len(O)))]
    open(OUT + "/GATE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- STEP C: independent checkers (2026-10-13) ---------------------------------------------------------------------------------
# GPT-Sol and GPT-Luna each write expectations about the FINAL ANSWER from the question, schema (with example rows) and knowledge
# document only -- never Sonnet's plan or SQL. Code checks them on Sonnet's gate answer (out/spider2/errors/gate). Column-level
# expectations name what the column holds; code maps that to an answer column by word overlap (no match -> not checkable).
# Also: GPT-Luna's own gate answers with its own self-check (STEP B for a second model family).
CHECK = """You will NOT write the answer. You write checks that any correct answer to the request below must pass, so that a wrong
answer can be caught. Use only these kinds:
  {"kind": "rows", "op": "=|<=|>=", "value": N}                                 number of rows of the answer
  {"kind": "probe", "sql": "SELECT <one number> ...", "relation": "equals_rows"} a query of yours whose single number must equal
                                                                                the answer's row count (e.g. how many entities qualify)
  {"kind": "unique", "describes": "what the identifying column holds"}           that column has no duplicates
  {"kind": "not_null", "describes": "what the column holds"}                     that column has no NULLs
  {"kind": "range", "describes": "what the column holds", "min": x, "max": y}    every value within [min, max] (omit an unknown bound)
Give only checks you are confident in. Probe queries must be SQLite SELECT statements on this database.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

Answer ONLY JSON: {"checks": [ ... ]}"""


def _words(s): import re as _re; return {w for w in _re.findall(r"[a-z]+", _re.sub(r"([a-z])([A-Z])", r"\1 \2", s or "").lower()) if len(w) > 2}


def _map(df, desc):
    best, score = None, 0
    for c in df.columns:
        sc = len(_words(str(c)) & _words(desc))
        if sc > score: best, score = c, sc
    return best


def _check_final(db, df, checks):
    out = []
    for e in checks or []:
        if not isinstance(e, dict): continue
        k = e.get("kind"); ok = None
        try:
            if df is None: ok = None
            elif k == "rows": v = float(e["value"]); n = len(df); ok = {"=": n == v, "<=": n <= v, ">=": n >= v}.get(e.get("op", "="))
            elif k == "probe":
                r = S.run_sql(db, e["sql"]); ok = None if r is None or r.empty else float(r.iloc[0, 0]) == float(len(df))
            elif k in ("unique", "not_null", "range"):
                c = _map(df, e.get("describes", ""))
                if c is not None:
                    col = df[c]
                    if k == "unique": ok = not col.duplicated().any()
                    elif k == "not_null": ok = not col.isna().any()
                    else:
                        import pandas as pd
                        x = pd.to_numeric(col, errors="coerce")
                        if x.notna().any(): ok = not (((x < float(e["min"])) if e.get("min") is not None else False) | ((x > float(e["max"])) if e.get("max") is not None else False)).any()
        except Exception: ok = None
        out.append({"kind": k, "ok": ok})
    return out


def run_checkers(checkers=("gpt-6-sol", "gpt-6-luna"), workers=6):
    import glob
    from specbridge.comm.common.llm import call, parse
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}
    G = [json.load(open(f)) for f in glob.glob(OUT + "/gate/*.json")]; G = [o for o in G if o.get("sql")]; ctx = {}
    for o in G: ctx.setdefault(T[o["instance_id"]]["db"], S.context(T[o["instance_id"]]["db"]))
    jobs = [("check", m, o["instance_id"]) for o in G for m in checkers] + [("self", "gpt-6-luna", o["instance_id"]) for o in G]
    random.Random(SEED + 3).shuffle(jobs)
    def one(job):
        kind, m, iid = job; f = "%s/%s/%s/%s.json" % (OUT, "checker" if kind == "check" else "gate_self", m, iid)
        if os.path.exists(f): return
        t = T[iid]; p = (CHECK if kind == "check" else PLAN) % (ctx[t["db"]], S.docs(t), t["question"]); txt = call(p, m)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; o = {"instance_id": iid, "model": m, "chars_in": len(p), "chars_out": len(txt)}
        if kind == "check": o["checks_spec"] = r.get("checks")
        else:
            sql = r.get("sql"); Gd, io = S.golds(iid, E); df = S.run_sql(t["db"], sql) if sql else None
            o.update(sql=sql, plan=r.get("plan"), matches=S.matches(df, Gd, io), checks=_check(t["db"], sql, r.get("plan")) if sql else [])
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report_checkers(checkers)


def report_checkers(checkers=("gpt-6-sol", "gpt-6-luna")):
    import glob
    T = S.tasks(); G = {o["instance_id"]: o for o in (json.load(open(f)) for f in glob.glob(OUT + "/gate/*.json")) if o.get("sql")}
    flag = {}
    for iid, o in G.items():
        df = S.run_sql(T[iid]["db"], o["sql"])
        for m in checkers:
            f = "%s/checker/%s/%s.json" % (OUT, m, iid)
            if os.path.exists(f):
                c = _check_final(T[iid]["db"], df, json.load(open(f)).get("checks_spec")); flag[(m, iid)] = (any(x["ok"] is False for x in c), sum(x["ok"] is not None for x in c))
    W = [i for i, o in G.items() if not o["matches"]]; R = [i for i, o in G.items() if o["matches"]]
    L = ["# Step C: independent checkers on Sonnet's gate answers (`errors run_checkers`)\n",
         "Checkers see the question, schema and knowledge document only. %d wrong and %d right Sonnet answers. Rule: build repair only if a "
         "variant flags >= 40%% of wrong and <= 10%% of right.\n" % (len(W), len(R)),
         "| variant | wrong flagged | right flagged | checkable checks per task | meets the rule |", "|---|---|---|---|---|"]
    variants = {m: (lambda i, m=m: flag.get((m, i), (False, 0))[0]) for m in checkers}
    variants["both agree"] = lambda i: all(flag.get((m, i), (False, 0))[0] for m in checkers)
    variants["either"] = lambda i: any(flag.get((m, i), (False, 0))[0] for m in checkers)
    for v, fn in variants.items():
        w = sum(fn(i) for i in W) / max(1, len(W)); r = sum(fn(i) for i in R) / max(1, len(R))
        ck = sum(flag.get((m, i), (False, 0))[1] for m in (checkers if v in ("both agree", "either") else [v]) for i in G) / max(1, len(G))
        L.append("| %s | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %.1f | %s |" % (v, sum(fn(i) for i in W), len(W), 100 * w, sum(fn(i) for i in R), len(R), 100 * r, ck, "yes" if w >= 0.4 and r <= 0.1 else "no"))
    S_ = [json.load(open(f)) for f in glob.glob(OUT + "/gate_self/gpt-6-luna/*.json")]; S_ = [o for o in S_ if o.get("sql")]
    Ws = [o for o in S_ if not o["matches"]]; Rs = [o for o in S_ if o["matches"]]; v = lambda o: any(c["ok"] is False for c in o["checks"])
    L += ["", "GPT-Luna self-check on its own gate answers: %d answers, %d right. Self-check flags %d/%d wrong (%.0f%%) and %d/%d right (%.0f%%)." % (
        len(S_), len(Rs), sum(v(o) for o in Ws), len(Ws), 100 * sum(v(o) for o in Ws) / max(1, len(Ws)), sum(v(o) for o in Rs), len(Rs), 100 * sum(v(o) for o in Rs) / max(1, len(Rs))),
          "(Sonnet self-check, Step B: 6/29 wrong (21%), 2/34 right (6%).)"]
    open(OUT + "/CHECKERS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- STEP D: specification vs compilation, directional test (2026-10-13) -----------------------------------------------------------
# On the released Spider 2.0-lite SQLite gold queries that match their own accepted answer (14 of 24): Opus writes an EXACT
# step-by-step specification of the gold SQL (a stand-in for V, which needs catalogues these databases lack); Sonnet compiles
# request + specification into SQL with the same one call as the baseline. High accuracy = compiling works and the baseline
# failures are specification errors; low accuracy = compiling these operations is itself the bottleneck.
SPEC = """Write an EXACT specification of what the SQL query below computes, as numbered steps in plain words, so that an analyst
could rebuild the same result without seeing the SQL. For each step state: source tables and the rows kept (every filter, with its
exact constants), joins and whether unmatched rows are kept, grouping level, every formula exactly (including CAST, rounding,
NULL handling, weights), window functions (partition, order, frame), ordering, ties and limits, and the final output columns in
order. Use table and column names as they appear. Do not write SQL.

SQL:
%s

Answer ONLY JSON: {"spec": "1. ...\\n2. ..."}"""


def run_spec(workers=6):
    from specbridge.comm.common.llm import call, parse, ask_json
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; base = {}
    ids = []
    for f in sorted(os.listdir(S.GOLD + "/sql")):
        iid = f[:-4]
        if iid not in T: continue
        G, io = S.golds(iid, E); sql = open(S.GOLD + "/sql/" + f).read()
        old = S.TIMEOUT; S.TIMEOUT = 60; ok = bool(S.matches(S.run_sql(T[iid]["db"], sql), G, io)); S.TIMEOUT = old
        if ok: ids.append(iid)
    def one(iid):
        f = "%s/spec/%s.json" % (OUT, iid)
        if os.path.exists(f): return
        sql = open(S.GOLD + "/sql/%s.sql" % iid).read(); sp = (ask_json(SPEC % sql, "opus") or {}).get("spec")
        if not sp: return
        t = T[iid]; q = t["question"] + "\n\nEXACT SPECIFICATION OF THE INTENDED COMPUTATION:\n" + sp
        txt = call(X.PLAIN % (S.context(t["db"]), S.docs(t), q), MODEL); r = parse(txt or "", "{") or {}
        G, io = S.golds(iid, E); df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
        b = json.load(open(_f(iid))) if os.path.exists(_f(iid)) else {}
        o = {"instance_id": iid, "spec": sp, "sql": r.get("sql"), "matches": S.matches(df, G, io), "baseline_right": bool(b.get("matches"))}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, ids))
    O = [json.load(open("%s/spec/%s.json" % (OUT, i))) for i in ids if os.path.exists("%s/spec/%s.json" % (OUT, i))]
    L = ["# Step D: specification vs compilation (`errors run_spec`), Sonnet compiles Opus's exact specification of the gold SQL\n",
         "%d valid released gold queries (they match their own accepted answer)." % len(ids),
         "- from the request alone (baseline): %d / %d right" % (sum(o["baseline_right"] for o in O), len(O)),
         "- from request + exact specification: %d / %d right" % (sum(bool(o["matches"]) for o in O), len(O)),
         "- baseline failures fixed by the specification: %d / %d" % (sum(bool(o["matches"]) and not o["baseline_right"] for o in O), sum(not o["baseline_right"] for o in O)),
         "- baseline successes lost with the specification: %d" % sum(o["baseline_right"] and not o["matches"] for o in O)]
    open(OUT + "/SPEC.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- SPIDER 2.0 DESIGN, GATE 1 (2026-10-13): code-only grounding + one call ----------------------------------------------------
# Split fixed once: 65 dev / 70 test of the 135 SQLite tasks, seeded, stratified by the baseline outcome (all 135 were seen in the
# error analysis; no method was tuned on any; from here only dev is used for development).
# Grounding, by code from the database and the request (no model): relevant tables/columns (request words vs names, plus tables
# linked by a foreign key), stored values that match request words, value formats, NULL shares -- added to the baseline context.
def split():
    f = OUT + "/split.json"
    if os.path.exists(f): return json.load(open(f))
    T = S.tasks(); done = {i: json.load(open(_f(i))) for i in T if os.path.exists(_f(i))}
    rng = random.Random(SEED + 7); dev, test = [], []
    for ok in (True, False):
        xs = sorted(i for i, o in done.items() if bool(o["matches"]) == ok); rng.shuffle(xs); n = round(len(xs) * 65 / len(done))
        dev += xs[:n]; test += xs[n:]
    out = {"dev": sorted(dev), "test": sorted(test)}; json.dump(out, open(f, "w"), indent=1); return out


GENERIC = {"other", "two", "one", "three", "first", "last", "year", "years", "month", "months", "day", "days", "most", "least", "common",
           "different", "each", "total", "number", "average", "count", "value", "values", "type", "types", "name", "names", "all", "any",
           "per", "with", "from", "for", "and", "the", "that", "which", "their", "there", "than", "more", "less", "top", "high", "low", "new"}


def _words2(s): import re as _re; return {w for w in _re.findall(r"[a-z]+", _re.sub(r"([a-z])([A-Z])", r"\1 \2", s or "").lower().replace("_", " ")) if len(w) > 2}


def grounding(db, question, max_tables=6, max_values=25, dbpath=None):
    con = sqlite3.connect("file:%s?mode=ro" % (dbpath or "%s/%s.sqlite" % (S.DBDIR, db)), uri=True); q = _words2(question); L = []
    try:
        tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        cols = {t: [(r[1], (r[2] or "").upper()) for r in con.execute('PRAGMA table_info("%s")' % t)] for t in tabs}
        score = {t: len(_words2(t) & q) * 2 + sum(len(_words2(c) & q) for c, _ty in cols[t]) for t in tabs}
        rel = [t for t in sorted(tabs, key=lambda t: -score[t]) if score[t] > 0][:max_tables]
        fk = set()
        for t in rel:
            for r in con.execute('PRAGMA foreign_key_list("%s")' % t): fk.add(r[2])
        rel += [t for t in sorted(fk) if t in tabs and t not in rel][:2]
        if not rel: return ""
        L.append("RELEVANT TABLES (by the request's words and foreign keys): " + ", ".join(rel))
        vals, fmts, nulls = [], [], []
        for t in rel:
            n = con.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0] or 0
            for c, ty in cols[t]:
                if not n: continue
                nn = con.execute('SELECT SUM("%s" IS NULL) FROM "%s"' % (c, t)).fetchone()[0] or 0
                if nn: nulls.append("%s.%s %.0f%%" % (t, c, 100 * nn / n))
                if "INT" in ty or "REAL" in ty or "NUM" in ty or "FLOA" in ty or "DOUB" in ty: continue
                sample = [r[0] for r in con.execute('SELECT DISTINCT "%s" FROM "%s" WHERE "%s" IS NOT NULL LIMIT 200' % (c, t, c))]
                if sample and all(isinstance(v, str) and len(v) >= 8 and v[:4].isdigit() and v[4] in "-/" for v in sample[:20]): fmts.append("%s.%s like '%s'" % (t, c, sample[0]))
                if len(sample) < 200:
                    hits = [(v, (_words2(v) & q) - GENERIC) for v in sample if isinstance(v, str) and len(v) <= 60]
                    wc = collections.Counter(w for _v, ws in hits for w in ws)          # a word matching many values is generic here
                    keep = [v for v, ws in hits if ws and all(wc[w] <= 3 for w in ws)]
                    vals += ["%s.%s = '%s'" % (t, c, v) for v in keep[:3]]
        if vals: L.append("STORED VALUES MATCHING WORDS OF THE REQUEST: " + "; ".join(vals[:max_values]))
        if fmts: L.append("VALUE FORMATS: " + "; ".join(fmts[:12]))
        if nulls: L.append("MISSING VALUES (share NULL): " + "; ".join(nulls[:20]))
    finally: con.close()
    return "\n".join(L)


def run_gate1(workers=6):
    """Gate 1 on dev: grounding + one call (disclose.PLAIN; the grounding is appended to the documentation) vs the one-call
    baseline (saved) vs the agentic harness (saved; run for dev tasks it has not answered)."""
    from specbridge.comm.common.llm import call, parse
    from specbridge.comm.common import solve as SV
    T = S.tasks(); E_ = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; dev = split()["dev"]; ctx = {}
    for i in dev: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    def agent(iid):
        f = "%s/agent/%s.json" % (OUT, iid)
        if os.path.exists(f) and "matches" in json.load(open(f)): return
        t = T[iid]; text = t["question"] + ("\n\nKNOWLEDGE DOCUMENT:\n" + S.docs(t) if t.get("external_knowledge") else "")
        r = SV.solve([{"key": iid, "text": text, "snapshot": "%s/%s.sqlite" % (S.DBDIR, t["db"]), "database": t["db"]}], MODEL, OUT + "/agent", bsize=1, workers=1)
        if iid not in r: return
        o = r[iid]; G, io = S.golds(iid, E_); df = S.run_sql(t["db"], o.get("final")) if o.get("final") else None
        o.update(matches=S.matches(df, G, io)); json.dump(o, open(f, "w"), indent=1, default=str)
    def grounded(iid):
        f = "%s/grounded/%s.json" % (OUT, iid)
        if os.path.exists(f): return
        t = T[iid]; gr = grounding(t["db"], t["question"]); d = S.docs(t) + ("\n\nFACTS FROM THE DATABASE (computed by code):\n" + gr if gr else "")
        p = X.PLAIN % (ctx[t["db"]], d, t["question"]); txt = call(p, MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; G, io = S.golds(iid, E_); df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"instance_id": iid, "sql": r.get("sql"), "matches": S.matches(df, G, io), "chars_in": len(p), "chars_out": len(txt), "grounding": gr}, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(agent, dev)); list(ex.map(grounded, dev))
    report_gate1()


def report_gate1():
    T = S.tasks(); dev = split()["dev"]; ld = lambda d, i: json.load(open("%s/%s/%s.json" % (OUT, d, i))) if os.path.exists("%s/%s/%s.json" % (OUT, d, i)) else None
    rows = [(i, ld("plain", i), ld("agent", i), ld("grounded", i)) for i in dev]; rows = [r for r in rows if all(r[1:])]
    acc = lambda k: sum(bool(r[k]["matches"]) for r in rows)
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    up = sum(bool(r[3]["matches"]) and not r[2]["matches"] for r in rows); dn = sum(bool(r[2]["matches"]) and not r[3]["matches"] for r in rows)
    L = ["# Gate 1 on Spider 2.0 dev: code-only grounding + one call (`errors run_gate1`), Sonnet\n",
         "%d dev tasks with all three arms.\n" % len(rows), "| arm | right | characters in per task (approx.) |", "|---|---|---|",
         "| one call (saved baseline) | %d | about %d |" % (acc(1), sum(len(X.PLAIN) + len(S.context(T[r[0]]["db"])) for r in rows[:15]) / max(1, min(15, len(rows)))),
         "| agentic harness (exploration) | %d | about 10,000 (measured on 15 tasks) |" % acc(2),
         "| grounding + one call | %d | %d |" % (acc(3), sum(r[3]["chars_in"] for r in rows) / max(1, len(rows))),
         "", "Grounding vs agentic: +%d / -%d tasks (exact McNemar p = %.2g). Grounding vs one call: +%d / -%d." % (
             up, dn, mc(up, dn), sum(bool(r[3]["matches"]) and not r[1]["matches"] for r in rows), sum(bool(r[1]["matches"]) and not r[3]["matches"] for r in rows))]
    open(OUT + "/GATE1.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- SPIDER 2.0 FINAL TEST (2026-10-13): ship candidate = generic grounding + one call ------------------------------------------
# Untouched test split (70). Arms: plain (one call), agent (exploration harness), ground (grounding + one call), groundplan
# (grounding + a one-line plan per step and the SQL as CTEs s1..sk). 3 independent runs per arm, all interleaved. The model
# interface (`claude -p`) has no temperature setting, so runs use its default: run-to-run agreement is measured, not assumed.
PLANSQL = """Answer the request with SQL for the database below. First write a short PLAN: one line per step s1, s2, ... saying what the
step computes. Then the SQL as one query WITH s1 AS (...), s2 AS (...), ... SELECT ... FROM <last step>, each CTE implementing the
plan step of the same name.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

Answer ONLY JSON: {"plan": ["s1: ...", "s2: ..."], "sql": "WITH s1 AS (...) ... SELECT ..."}"""
FT = OUT + "/final"; RUNS = 3; FARMS = ("plain", "agent", "ground", "groundplan", "plan")
# 2026-10-13: "plan" (the step-plan prompt WITHOUT grounding) added after an interim look at 34 test task-runs, to see whether the
# plan alone gives the gain of grounding + plan. Recorded as a post-hoc arm.


def run_final(workers=6, arms=None, only=None):
    import threading
    from specbridge.comm.common.llm import call, parse
    from specbridge.comm.common import solve as SV
    T = S.tasks(); E_ = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; test = split()["test"]; ctx = {}
    for i in test: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    lock = threading.Lock(); COST = collections.defaultdict(collections.Counter); texts = {}
    orig = SV.call
    def counted(prompt, model):
        txt = orig(prompt, model)
        with lock:
            for key, q in texts.items():
                if q[:200] in prompt: COST[key]["calls"] += 1; COST[key]["chars_in"] += len(prompt); COST[key]["chars_out"] += len(txt or "")
        return txt
    SV.call = counted
    def job(j):
        arm, iid, run = j; f = "%s/%s/r%d/%s.json" % (FT, arm, run, iid)
        if os.path.exists(f): return
        os.makedirs(os.path.dirname(f), exist_ok=True); t = T[iid]; t0 = time.time(); G, io = S.golds(iid, E_); o = {"instance_id": iid, "arm": arm, "run": run}
        if arm == "agent":
            text = t["question"] + ("\n\nKNOWLEDGE DOCUMENT:\n" + S.docs(t) if t.get("external_knowledge") else "") + "\n\n(run %d)" % run
            key = "%s|%d" % (iid, run)
            with lock: texts[key] = text
            r = SV.solve([{"key": iid, "text": text, "snapshot": "%s/%s.sqlite" % (S.DBDIR, t["db"]), "database": t["db"]}], MODEL, "%s/agent_raw/r%d" % (FT, run), bsize=1, workers=1)
            if iid not in r: return
            sql = r[iid].get("final"); o.update(cost=dict(COST[key]), turns=r[iid].get("turns"))
        else:
            gr = grounding(t["db"], t["question"]) if arm in ("ground", "groundplan") else ""
            d = S.docs(t) + ("\n\nFACTS FROM THE DATABASE (computed by code):\n" + gr if gr else "")
            p = (PLANSQL if arm in ("groundplan", "plan") else X.PLAIN) % (ctx[t["db"]], d, t["question"]); txt = call(p, MODEL)
            if not (txt or "").strip(): return
            r = parse(txt, "{") or {}; sql = r.get("sql"); o.update(cost={"calls": 1, "chars_in": len(p), "chars_out": len(txt)}, plan=r.get("plan"), grounding=gr)
        df = S.run_sql(t["db"], sql) if sql else None
        o.update(sql=sql, runs_sql=df is not None, matches=S.matches(df, G, io), seconds=round(time.time() - t0, 1),
                 result_sig=None if df is None else hashlib.sha1(df.round(4).astype(str).to_csv(index=False).encode()).hexdigest()[:16])
        json.dump(o, open(f, "w"), indent=1, default=str)
    jobs = [(a, i, r) for r in range(RUNS) for i in test for a in (arms or FARMS)]; random.Random(SEED + 41).shuffle(jobs)
    if only: jobs = [j for j in jobs if (j[1], j[2]) in only]               # a subset of (task, run), e.g. for a quick signal
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(job, jobs))
    report_final()


def report_final():
    import statistics as st
    T = S.tasks(); test = split()["test"]; E_ = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}
    ld = lambda a, r, i: json.load(open("%s/%s/r%d/%s.json" % (FT, a, r, i))) if os.path.exists("%s/%s/r%d/%s.json" % (FT, a, r, i)) else None
    tasks = [i for i in test if all(ld(a, r, i) for a in FARMS for r in range(RUNS))]
    L = ["# Spider 2.0 final test (untouched test split), Sonnet (`errors run_final`)\n",
         "%d of %d test tasks with all arms and runs. %d independent runs per arm (the interface has no temperature setting). Same scorer for all arms.\n" % (len(tasks), len(test), RUNS),
         "| arm | right per run | mean (sd) | right in all 3 runs | right in >= 2 runs (majority) | runs agree on correctness | runs return the same result | chars in / out per task | calls per task | seconds per task |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    acc = {}
    for a in FARMS:
        per = [sum(bool(ld(a, r, i)["matches"]) for i in tasks) for r in range(RUNS)]
        allr = sum(all(ld(a, r, i)["matches"] for r in range(RUNS)) for i in tasks); maj = sum(sum(bool(ld(a, r, i)["matches"]) for r in range(RUNS)) >= 2 for i in tasks)
        agree = sum(len({bool(ld(a, r, i)["matches"]) for r in range(RUNS)}) == 1 for i in tasks); same = sum(len({ld(a, r, i)["result_sig"] for r in range(RUNS)}) == 1 for i in tasks)
        c = [ld(a, r, i).get("cost") or {} for r in range(RUNS) for i in tasks]; sec = [ld(a, r, i)["seconds"] for r in range(RUNS) for i in tasks]
        acc[a] = per
        L.append("| %s | %s | %.1f (%.1f) | %d | %d | %d / %d | %d / %d | %d / %d | %.1f | %.0f |" % (a, ", ".join(map(str, per)), st.mean(per), st.pstdev(per), allr, maj, agree, len(tasks), same, len(tasks),
                 sum(x.get("chars_in", 0) for x in c) / len(c), sum(x.get("chars_out", 0) for x in c) / len(c), sum(x.get("calls", 0) for x in c) / len(c), sum(sec) / len(sec)))
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    L += ["", "Flips vs plain, by majority over the 3 runs (exact McNemar):"]
    maj = lambda a, i: sum(bool(ld(a, r, i)["matches"]) for r in range(RUNS)) >= 2
    for a in FARMS[1:]:
        up = sum(maj(a, i) and not maj("plain", i) for i in tasks); dn = sum(maj("plain", i) and not maj(a, i) for i in tasks)
        L.append("- %s: +%d / -%d (p %.2g)" % (a, up, dn, mc(up, dn)))
    # WHEN TO PREFER GROUNDING: the majority-vote gain over plain by task feature
    L += ["", "When grounding helps (majority over runs; gain = tasks turned right minus tasks turned wrong, vs plain):", "", "| task feature | tasks | ground: + / - | groundplan: + / - |", "|---|---|---|---|"]
    feat = {}
    for i in tasks:
        g = ld("ground", 0, i).get("grounding") or ""; t = T[i]
        feat[i] = {"request matches stored values": "STORED VALUES" in g, "no stored-value match": "STORED VALUES" not in g, "has a knowledge document": bool(t.get("external_knowledge")),
                   "long request (> 300 chars)": len(t["question"]) > 300, "short request (<= 300 chars)": len(t["question"]) <= 300,
                   "several readings accepted": len(S.golds(i, E_)[0]) > 1, "one accepted answer": len(S.golds(i, E_)[0]) == 1}
    for k in next(iter(feat.values())):
        sub = [i for i in tasks if feat[i][k]]
        cell = lambda a: "+%d / -%d" % (sum(maj(a, i) and not maj("plain", i) for i in sub), sum(maj("plain", i) and not maj(a, i) for i in sub))
        L.append("| %s | %d | %s | %s |" % (k, len(sub), cell("ground"), cell("groundplan")))
    bad = []
    for f in sorted(os.listdir(S.GOLD + "/sql")):
        iid = f[:-4]
        if iid in test and not os.path.exists("%s/spec/%s.json" % (OUT, iid)): bad.append(iid)
    L += ["", "Scorer notes: every arm is scored by the same official comparison (spider2.matches) against all accepted answers. Test tasks whose "
          "released gold SQL does not reproduce its own accepted answer (released-file mismatch, scored against the answer files as for every arm): %s." % (", ".join(bad) or "none")]
    open(FT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "label": label, "run_agent": run_agent, "report_agent": report_agent, "run_gate": run_gate, "report_gate": report_gate, "run_checkers": run_checkers, "report_checkers": report_checkers, "run_spec": run_spec, "run_gate1": run_gate1, "report_gate1": report_gate1, "run_final": run_final, "report_final": report_final}[sys.argv[1]]()
