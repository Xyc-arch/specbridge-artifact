"""CHOICE POINTS on generated tasks, each decided where it is made.
  facts    code: per column the reference SQL touches -- rows, NULLs, zeros, empty strings, negatives, distinct; rows per key
           on every join column; the tie at the cut
  propose  every choice point of a task; B is exact text edits of SQL A, so points combine and B stays in A's language
  verify   code only: edits apply | B runs | B's answer differs under the task's own grader (load-bearing) | B renders in
           explicit V | a witness (rows only in A / only in B, changed values)
  repair   one batched round: failed points go back with the code's result; revised points are re-verified
  combine  a pair combines only if the combined SQL runs and EACH point still changes the answer given the other
  review   one batched call per task and reviewer (opus, sonnet) under interp-v7 applied to requests about the task
    python -m specbridge.comm.transfer.choice_points <out dir> [--tasks name=path ...] [--seeds <seeds.jsonl>] freeze-seeds | facts | propose | verify | repair | review | report
Tasks: the files in TASKS (ported and database-first)."""
import collections, concurrent.futures as cf, itertools, json, os, random, re, sys
from specbridge.comm.common import db as DB, grade as G
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose.library import summary
TASKS = {"ported": "out/p_gamma/tasks.jsonl", "dbfirst": "out/p_gamma/dbfirst_tasks.jsonl"}
WORKERS = int(os.environ.get("TRANSFER_WORKERS", 6))      # concurrent model calls (API-bound)
D = "out/p_gamma/cp"

PROPOSE = """List EVERY interpretation choice point in each generated data task below. A choice point is a semantic decision that a
natural request for this task could leave unstated, where reading A (the reference SQL) is one reasonable resolution and
reading B another -- not a mistake, not a different task. Use the DATA FACTS: a choice only matters if the data makes the
readings differ (zeros present, empty strings present, several rows per key, a tie at the cut, negative values, ...).
Typical kinds (not exhaustive): tie at a limit; aggregation level (per record vs per entity); unit counted (rows vs distinct
entities); duplicate rows; sentinel values (0 or '' meaning missing, per the documentation); missing group kept or dropped;
missing values in a calculation; join path for an attribute; inclusive vs strict boundaries; signed vs absolute amounts.
Write B as EXACT TEXT EDITS to SQL A: each edit {"from": a substring copied exactly from SQL A, "to": its replacement}. Keep the
edits minimal and inside one decision; always alias a subquery; never use SELECT *; keep A's output columns and their order.
List all points you find (zero is a valid answer for a task); do not rank or filter them.
Answer ONLY JSON: [{"task": "<id>", "points": [{"kind": "...", "decision": "...", "reading_A": "...", "reading_B": "...",
"edits": [{"from": "...", "to": "..."}], "why_open": "why a natural request could leave this unstated"}]}]

DATABASE %s -- SCHEMA:
%s

DOCUMENTATION:
%s

%s"""

REPAIR = """Your proposed choice points below were checked by executing SQL A and SQL B on the database under the task's grading
rule. Each FAILED: the edits did not apply exactly, B did not run, or B gives the same answer as A here (not load-bearing).
For each, either REVISE it (new exact text edits to SQL A that make the SAME decision change the answer on this data -- use the
data facts) or DISCARD it. Do not invent a different decision. Answer ONLY JSON:
[{"id": "...", "action": "revise|discard", "why": "...", "edits": [{"from": "...", "to": "..."}]}]

%s"""

REVIEW = """Judge this as a human analytical request, not an executable program. For each reading, ask whether a reasonable reader
could infer it from the wording, evidence and documentation. Distinguish your preferred reading from other defensible readings.
Do not reject a reading merely because its SQL requires an unstated operation. Reject it when it contradicts the request or
requires an unsupported assumption. Explain the decisive phrase or contextual fact.

Here there is no single wording yet. The REQUEST is the task below as a person would naturally ask it, WITHOUT the sentence
that settles the listed decision (everything else in the specification stays as stated). For each decision point, judge
reading A and reading B of that request. Points are independent; judge each alone.
TASK SPECIFICATION (reading A settles every decision): %s
DECISION POINTS:
%s
Answer ONLY JSON: [{"point": "<id>", "A": {"verdict": "preferred|defensible|rejected", "decisive": "..."}, "B": {"verdict": "...", "decisive": "..."}}]

SCHEMA:
%s

DOCUMENTATION:
%s"""


def configure(argv):
    """Options shared by the three stages: --tasks name=path (repeatable; replaces the default sources) and --seeds <file> (a
    frozen copy of the retrieval records). Returns the positional arguments."""
    global TASKS
    pos, i, tk = [], 0, {}
    while i < len(argv):
        if argv[i] == "--tasks": n, f = argv[i + 1].split("=", 1); tk[n] = f; i += 2
        elif argv[i] == "--seeds":
            from specbridge.comm.diagnose import library as LB
            LB.SEEDS = argv[i + 1]; i += 2
        elif argv[i] == "--cp": pos.append(("cp", argv[i + 1])); i += 2
        else: pos.append(argv[i]); i += 1
    if tk: TASKS = tk
    return pos


def tasks():
    return [dict(json.loads(l), source=s, key="%s:%s" % (s, json.loads(l)["id"])) for s, f in TASKS.items() for l in open(f)]


def tie_fact(t):
    tg = t.get("tie_groups") or []; pool = t.get("last_pool"); m = re.search(r"LIMIT (\d+)", t["reference_sql"])
    if m and pool:
        return "row limit %s; the last tie group at the cut has %d rows in the answer, and %d rows in the database tie with it (so keeping every tied row gives %d rows instead of %s)" % (
            m.group(1), tg[-1] if tg else 0, len(pool), len(t["reference_answer"]) - (tg[-1] if tg else 0) + len(pool), m.group(1))
    return "row limit %s; no tie at the cut" % m.group(1) if m else "no row limit"


def profile(t):
    import sqlglot
    from sqlglot import exp
    con = DB.connect(t["snapshot"]); q = sqlglot.parse_one(t["reference_sql"], read="sqlite"); alias = {}
    for tb in q.find_all(exp.Table): alias[tb.alias_or_name] = tb.name
    out = []
    for tb, col in sorted({(alias.get(c.table, c.table), c.name) for c in q.find_all(exp.Column) if c.table and alias.get(c.table, c.table) in alias.values()}):
        try:
            n, nn, z, e, neg, dv = con.execute('SELECT COUNT(*), SUM("{c}" IS NULL), SUM("{c}" = 0), SUM("{c}" = \'\'), SUM(typeof("{c}") IN (\'integer\',\'real\') AND "{c}" < 0), COUNT(DISTINCT "{c}") FROM "{t}"'.format(c=col, t=tb)).fetchone()
            out.append("%s.%s: %d rows, %d NULL, %d zero, %d empty-string, %d negative, %d distinct" % (tb, col, n, nn or 0, z or 0, e or 0, neg or 0, dv))
        except Exception: pass
    for j in q.find_all(exp.Join):
        for eq in (j.args.get("on") or exp.Boolean(this=True)).find_all(exp.EQ):
            for c in (eq.left, eq.right):
                if isinstance(c, exp.Column) and c.table:
                    tb = alias.get(c.table, c.table)
                    try:
                        mx, av = con.execute('SELECT MAX(k), AVG(k) FROM (SELECT COUNT(*) AS k FROM "%s" WHERE "%s" IS NOT NULL GROUP BY "%s")' % (tb, c.name, c.name)).fetchone()
                        out.append("join key %s.%s: rows per key value max %s, average %.2f" % (tb, c.name, mx, av or 0))
                    except Exception: pass
    out += [tie_fact(t), "answer A: %d rows" % len(t["reference_answer"])]
    return sorted(set(out), key=out.index)


def J(name, default=None):
    p = "%s/%s" % (D, name)
    return json.load(open(p)) if os.path.exists(p) else default


def W(name, obj): os.makedirs(D, exist_ok=True); json.dump(obj, open("%s/%s" % (D, name), "w"), indent=1, default=str)


def facts():
    F = {t["key"]: profile(t) for t in tasks()}; W("facts.json", F); print("facts for %d tasks" % len(F))


def propose():
    T = tasks(); F = J("facts.json"); by = collections.defaultdict(list)
    for t in T: by[(t["source"], t["database"])].append(t)
    jobs = [(k, ts[i:i + 3]) for k, ts in by.items() for i in range(0, len(ts), 3)]
    def one(job):
        (src, db), ts = job; schema, docs = DB.context(ts[0])
        body = "\n\n".join("--- TASK %s\nEXPLICIT SPECIFICATION: %s\nSQL A: %s\nANSWER A (first rows): %s\nDATA FACTS:\n%s" % (
            t["id"], t["instruction"].split("\nConventions")[0], t["reference_sql"], str(t["reference_answer"][:3])[:240], "\n".join("  " + f for f in F[t["key"]])) for t in ts)
        got = {x.get("task"): x.get("points", []) for x in (ask_json(PROPOSE % (db, schema, docs, body), "opus", brace="[") or []) if isinstance(x, dict)}
        return {"%s:%s" % (src, t["id"]): got.get(t["id"], "UNPARSED") for t in ts}
    P = {}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for d in ex.map(one, jobs): P.update(d)
    W("proposals.json", P); print("tasks %d; points %d" % (len(P), sum(len(v) for v in P.values() if v != "UNPARSED")))


def differs(t, rows):
    """B changes the answer: A's own grader (tie pool accepted) does not accept B's rows."""
    return not G.spec(t["grader"], t["reference_answer"], rows, t["tie_groups"], t["last_pool"])


def same(g, ref, rows): return G.spec(dict(g, ordered=False), ref, rows)


def check_point(t, con, p, pid):
    sql_b, spans = DB.apply_edits(t["reference_sql"], p.get("edits"))
    rec = dict(p, id=pid, sql_B=sql_b, spans=spans, applies=sql_b is not None)
    rs = DB.rows(con, sql_b) if sql_b else None
    rec.update(executes=rs is not None, load_bearing=bool(rs is not None and differs(t, rs)), renders=bool(sql_b) and DB.explicit(sql_b, t["database"]) is not None,
               witness=DB.witness(t["reference_answer"], rs) if rs is not None else None)
    return rec


def combine(t, con, pts):
    for a, b in itertools.combinations([p for p in pts if p["load_bearing"]], 2):
        a.setdefault("combines_with", []); b.setdefault("combines_with", [])
        s_ab, _ = DB.apply_edits(t["reference_sql"], a["edits"] + b["edits"])
        if not s_ab: continue
        ab, ra, rb = DB.rows(con, s_ab), DB.rows(con, a["sql_B"]), DB.rows(con, b["sql_B"])
        if None not in (ab, ra, rb) and differs(t, ab) and not same(t["grader"], rb, ab) and not same(t["grader"], ra, ab):
            a["combines_with"].append(b["id"]); b["combines_with"].append(a["id"])


def verify():
    T = {t["key"]: t for t in tasks()}; P = J("proposals.json"); V = {}
    for k, pts in P.items():
        V[k] = "UNPARSED" if pts == "UNPARSED" else [check_point(T[k], DB.connect(T[k]["snapshot"]), p, "%s#%d" % (k, i)) for i, p in enumerate(pts)]
    W("verified_round0.json", V); allp = [r for v in V.values() if v != "UNPARSED" for r in v]
    print("round 0: points %d | apply %d | run %d | load-bearing %d | + renders %d" % (len(allp), sum(r["applies"] for r in allp), sum(r["executes"] for r in allp),
          sum(r["load_bearing"] for r in allp), sum(r["load_bearing"] and r["renders"] for r in allp)))


def repair():
    T = {t["key"]: t for t in tasks()}; V = J("verified_round0.json"); F = J("facts.json"); by = collections.defaultdict(list)
    for k, pts in V.items():
        if pts != "UNPARSED": by[T[k]["database"]] += [(k, p) for p in pts if not p["load_bearing"]]
    def one(xs):
        body = "\n\n".join("--- POINT %s (task %s)\nSQL A: %s\nDECISION: %s\nREADING B: %s\nEDITS TRIED: %s\nRESULT: %s\nDATA FACTS: %s" % (
            p["id"], k, T[k]["reference_sql"], p["decision"], p["reading_B"], json.dumps(p.get("edits")),
            "edits do not apply exactly" if not p["applies"] else "B does not run" if not p["executes"] else "same answer as A (%d rows)" % p["witness"]["rows_B"],
            "; ".join(F[k])) for k, p in xs)
        return {x.get("id"): x for x in (ask_json(REPAIR % body, "opus", brace="[") or []) if isinstance(x, dict)}
    R = {}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for d in ex.map(one, [xs[i:i + 8] for xs in by.values() for i in range(0, len(xs), 8)]): R.update(d)
    for k, pts in V.items():
        if pts == "UNPARSED": continue
        con = DB.connect(T[k]["snapshot"])
        for i, p in enumerate(pts):
            if p["load_bearing"]: continue
            r = R.get(p["id"]) or {"action": "no reply"}; p["repair"] = r
            if r.get("action") == "revise": q = check_point(T[k], con, dict(p, edits=r.get("edits")), p["id"]); q.update(repair=r, revised=True); pts[i] = q
        combine(T[k], con, pts)
    W("verified.json", V); allp = [r for v in V.values() if v != "UNPARSED" for r in v]
    print("after repair: load-bearing %d; combinable pairs %d" % (sum(p["load_bearing"] for p in allp), sum(len(p.get("combines_with", [])) for p in allp) // 2))


def review():
    T = {t["key"]: t for t in tasks()}; V = J("verified.json"); jobs = []
    for k, pts in V.items():
        lb = [p for p in pts if p["load_bearing"]] if pts != "UNPARSED" else []
        if not lb: continue
        schema, docs = DB.context(T[k])
        listing = "\n".join("- %s | decision: %s | reading A: %s | reading B: %s" % (p["id"], p["decision"], p["reading_A"], p["reading_B"]) for p in lb)
        for m in ("opus", "sonnet"): jobs.append((k, m, REVIEW % (T[k]["instruction"].split("\nConventions")[0], listing, schema, docs)))
    out = collections.defaultdict(dict)
    def one(j):
        k, m, p = j; return k, m, {x.get("point"): x for x in (ask_json(p, m, brace="[") or []) if isinstance(x, dict)}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for k, m, r in ex.map(one, jobs): out[k][m] = r
    fits = lambda v: v in ("preferred", "defensible")
    for k, pts in V.items():
        for p in (pts if pts != "UNPARSED" else []):
            if not p["load_bearing"]: continue
            rv = {m: (out[k].get(m) or {}).get(p["id"]) or {} for m in ("opus", "sonnet")}
            acc = [m for m in rv if fits((rv[m].get("A") or {}).get("verdict")) and fits((rv[m].get("B") or {}).get("verdict"))]
            p["review"] = rv; p["label"] = "mutually recognized" if len(acc) == 2 else "disputed" if acc else "not supported"
    W("inventory.json", V); print("reviewed:", dict(collections.Counter(p.get("label") for v in V.values() if v != "UNPARSED" for p in v if p["load_bearing"])))


def report():
    V = J("inventory.json"); rows = lambda ks: [p for k in ks if V[k] != "UNPARSED" for p in V[k]]
    L = ["# Choice-point inventory\n", "| source | tasks | proposed | load-bearing | + renders | mutually recognized | disputed | not supported | tasks with an open point |", "|---|---|---|---|---|---|---|---|---|"]
    for src in list(TASKS) + ["all"]:
        ks = [k for k in V if src == "all" or k.startswith(src + ":")]; ps = rows(ks); lb = [p for p in ps if p["load_bearing"]]; c = collections.Counter(p.get("label") for p in lb)
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d |" % (src, len(ks), len(ps), len(lb), sum(p["renders"] for p in lb), c["mutually recognized"], c["disputed"],
                 c["not supported"], sum(1 for k in ks if any(p.get("label") in ("mutually recognized", "disputed") for p in rows([k])))))
    open(D + "/INVENTORY.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = configure(sys.argv[1:]); D = a[0]
    if a[1] == "freeze-seeds":
        from specbridge.comm.diagnose.library import freeze_seeds
        freeze_seeds(D); sys.exit(0)
    {"facts": facts, "propose": propose, "verify": verify, "repair": repair, "review": review, "report": report}[a[1]]()
