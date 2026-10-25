"""EVALUATE rendered tasks: explicit V (execution reference), precise natural and open natural, one hidden intention per task.
  freeze   intended reading per task, balanced within (open label, source), seeded; texts: explicit V of the intended reading
           WITH its Conventions paragraph (where V renders it), precise natural of that reading, open natural
  run      the solver; the versions of a task never share a batch
  report   intended match | either recorded reading | neither; paired precise -> open (kept / lost / gained)
Grading: reading A with the task's grader and tie pool; reading B with B's OWN grader and tie pool when B renders, else a
plain multiset comparison (recorded per task).
    python -m specbridge.comm.transfer.evaluate <render dir> [--tasks name=path ...] [--cp <choice-point dir>] freeze | run <model> | report <model> | funnel"""
import collections, json, os, random, re, sys
from specbridge.comm.common import db as DB, grade as G
from specbridge.comm.common.solve import solve
from specbridge.comm.transfer import choice_points as CP
D = "out/p_gamma/rcp"


def grade_B(c):
    """B's own grader and tie pool, computed as for A (or None with the reason)."""
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.spec import render as R
    try:
        cat = DB.catalogue(c["database"]); pB = lift(c["sql_B"], cat.con); g = R.grader(R.spec(pB, cat))
    except Exception as e: return None, "B does not render (%s)" % type(e).__name__
    if "declined" in g: return None, "B's grader declines: %s" % g["declined"]
    rows, groups, pool = R.reference(pB, DB.connect(c["snapshot"]), lambda cc, q: (lambda st, res, _c: (st, res))(*DB.execute(cc, q, ms=60000)))
    return {"grader": g, "answer": [list(r) for r in rows], "tie_groups": groups, "last_pool": [list(r) for r in pool] if pool else None}, "own grader and tie pool"


def matches(c, rs):
    """Which recorded readings an answer matches: A with the task's grader and tie pool; B with its own grader and tie pool
    when B renders, else a plain multiset comparison."""
    m = ["A"] if G.spec(c["grader"], c["answer_A"], rs, c["tie_groups"], c["last_pool"]) else []
    b = c.get("B")
    if (G.spec(b["grader"], b["answer"], rs, b["tie_groups"], b["last_pool"]) if b else G.spec(dict(c["grader"], ordered=False, limit=None), c["answer_B"], rs)): m.append("B")
    return m


def freeze(seed=2026):
    T = {t["key"]: t for t in CP.tasks()}; S = json.load(open(D + "/selection.json")); Wr = json.load(open(D + "/written.json"))
    R = json.load(open(D + "/review.json")); sv = json.load(open(D + "/survivors.json")); strata = collections.defaultdict(list)
    for k in sv: strata[(R[k]["label"], k.split(":")[0])].append(k)
    rng = random.Random(seed); intend = {}
    old = {c["case"]: c["intended"] for c in json.load(open(D + "/eval/frozen.json"))["cases"]} if os.path.exists(D + "/eval/frozen.json") else {}
    for key, ks in sorted(strata.items()):
        ks = sorted(ks); rng.shuffle(ks); first = rng.choice("AB")
        for i, k in enumerate(ks): intend[k] = first if i % 2 == 0 else ("B" if first == "A" else "A")
    if old:   # STABLE re-freeze (2026-10-03): a case frozen before keeps its intended reading (its stored answers depend on it);
        n = collections.Counter(old[k] for k in sv if k in old)      # cases new to this freeze alternate toward balance
        for k in sorted(k for k in sv if k not in old):
            intend[k] = "A" if n["A"] <= n["B"] else "B"; n[intend[k]] += 1
        intend.update({k: old[k] for k in sv if k in old})
    cases = []
    for k in sv:
        t = T[k]; I = intend[k]
        c = {"case": k, "source": k.split(":")[0], "database": t["database"], "snapshot": t["snapshot"], "kind": S[k]["kind"], "type": S[k].get("type") or __import__("specbridge.comm.transfer.render", fromlist=["libkind"]).libkind(S[k]["kind"]), "label": R[k]["label"], "intended": I,
             "A_depth": t.get("A"), "S_depth": t.get("S"), "construction": t.get("construction"),
             "grader": t["grader"], "answer_A": t["reference_answer"], "tie_groups": t["tie_groups"], "last_pool": t["last_pool"], "sql_A": t["reference_sql"],
             "sql_B": S[k]["sql_B"], "answer_B": DB.rows(DB.connect(t["snapshot"]), S[k]["sql_B"])}
        c["B"], c["b_grading"] = grade_B(c)
        ex = t["instruction"] if I == "A" else DB.explicit(S[k]["sql_B"], t["database"])
        O = "B" if I == "A" else "A"
        # BOTH precise wordings (2026-10-03): "precise" = the intended reading's, "precise_other" = the other reading's, so
        # "computes both readings when told which" is measured per family (graded against the other reading)
        c["texts"] = {"precise": Wr[k]["precise_" + I], "precise_other": Wr[k]["precise_" + O], "open": Wr[k]["open"]}
        if ex: c["texts"]["explicit"] = ex
        cases.append(c)
    os.makedirs(D + "/eval", exist_ok=True); json.dump({"cases": cases}, open(D + "/eval/frozen.json", "w"), indent=1, default=str)
    print("frozen %d cases, intended %s" % (len(cases), dict(collections.Counter(intend.values()))))


BSIZE = int(os.environ.get("TRANSFER_BSIZE", 1))     # questions per solver call. Default 1: variants of one task in one batch bleed into each other
                                                     # (explicit V 114/176 batched by 8 vs 159/176 alone)
RUN = lambda model: re.sub(r"\W", "_", model) + ("" if BSIZE == 8 else "_b%d" % BSIZE)


def run(model):
    C = json.load(open(D + "/eval/frozen.json"))["cases"]; out = "%s/eval/runs/%s" % (D, RUN(model))
    items = [{"key": "%s|%s" % (c["case"], v), "version": v, "text": x, "snapshot": c["snapshot"], "database": c["database"]} for c in C for v, x in c["texts"].items()]
    R = solve(items, model, out, bsize=BSIZE, group=lambda it: it["version"], workers=int(os.environ.get("TRANSFER_WORKERS", 6)))
    from specbridge.comm.construct.solver_eval import serial_rerun     # a timed-out final query is run again alone (2026-10-03)
    serial_rerun(R, {c["case"]: {"snapshot": c["snapshot"]} for c in C}, out)


def report(model):
    C = {c["case"]: c for c in json.load(open(D + "/eval/frozen.json"))["cases"]}; out = "%s/eval/runs/%s" % (D, RUN(model))
    res = {}
    for f in os.listdir(out):
        o = json.load(open(os.path.join(out, f))); k, v = o["key"].rsplit("|", 1)
        res[(k, v)] = matches(C[k], o["answer"]) if o.get("answer") is not None else []
    cell = lambda ks, v: (lambda rs: "%d/%d · %d/%d · %d" % (sum(C[k]["intended"] in m for k, m in rs), len(rs), sum(bool(m) for _k, m in rs), len(rs), sum(not m for _k, m in rs)))(
        [(k, res[(k, v)]) for k in ks if (k, v) in res])
    L = ["# Explicit V vs precise natural vs open natural (%s, %d question(s) per solver call)\n" % (model, BSIZE),
         "Cells: matched the INTENDED reading · matched EITHER recorded reading · NEITHER. On an open question, matching the other recorded "
         "reading is a defensible answer, not a solver mistake; only 'neither' is a mistake there.\n",
         "| group | tasks | explicit V | precise natural | open natural | precise -> open intended: kept / lost / gained |", "|---|---|---|---|---|---|"]
    ok = lambda k, v: C[k]["intended"] in res.get((k, v), [])
    groups = [("all", lambda c: True)] + [("source " + s_, (lambda s_: lambda c: c["source"] == s_)(s_)) for s_ in sorted({c["source"] for c in C.values()})]
    groups += [("mutually recognized open", lambda c: c["label"] == "mutually recognized open"), ("disputed open", lambda c: c["label"] == "disputed open")]
    groups += [("type: " + ty, (lambda ty: lambda c: c.get("type") == ty)(ty)) for ty in sorted({c.get("type") or "" for c in C.values()})]
    groups += [("kind: " + kd, (lambda kd: lambda c: c["kind"] == kd)(kd)) for kd in sorted({c["kind"] for c in C.values()})]
    groups += [("depth S%s" % d, (lambda d: lambda c: c.get("S_depth") == d)(d)) for d in sorted({c.get("S_depth") for c in C.values()}, key=str)]
    groups += [("depth A%s" % d, (lambda d: lambda c: c.get("A_depth") == d)(d)) for d in sorted({c.get("A_depth") for c in C.values()}, key=str)]
    for name, sel in groups:
        ks = [k for k, c in C.items() if sel(c)]
        L.append("| %s | %d | %s | %s | %s | %d / %d / %d |" % (name, len(ks), cell(ks, "explicit"), cell(ks, "precise"), cell(ks, "open"),
                 sum(ok(k, "precise") and ok(k, "open") for k in ks), sum(ok(k, "precise") and not ok(k, "open") for k in ks), sum(ok(k, "open") and not ok(k, "precise") for k in ks)))
    open("%s/eval/RESULTS_%s.md" % (D, RUN(model)), "w").write("\n".join(L) + "\n"); print("\n".join(L))


def funnel(cp):
    """From the input tasks to accepted variants: every stage's count and every stop reason."""
    V = json.load(open(cp + "/inventory.json")); S = json.load(open(D + "/selection.json")) if os.path.exists(D + "/selection.json") else {}
    Wr = json.load(open(D + "/written.json")) if os.path.exists(D + "/written.json") else {}; R = json.load(open(D + "/review.json")) if os.path.exists(D + "/review.json") else {}
    sv = json.load(open(D + "/survivors.json")) if os.path.exists(D + "/survivors.json") else []
    fr = json.load(open(D + "/eval/frozen.json"))["cases"] if os.path.exists(D + "/eval/frozen.json") else []
    T = CP.tasks(); pts = lambda k: [] if V.get(k) in (None, "UNPARSED") else V[k]
    has = lambda f: sum(1 for t in T if any(f(p) for p in pts(t["key"])))
    L = ["# Funnel: %d input tasks to accepted variants\n" % len(T), "| stage | tasks |", "|---|---|",
         "| input tasks | %d |" % len(T), "| proposer answer unparsed | %d |" % sum(1 for t in T if V.get(t["key"]) == "UNPARSED"),
         "| with any proposed choice point | %d |" % has(lambda p: True), "| with a load-bearing point (edits apply, B runs, B changes the answer) | %d |" % has(lambda p: p["load_bearing"]),
         "| ... that also renders in explicit V | %d |" % has(lambda p: p["load_bearing"] and p["renders"]),
         "| with a point both reviewers accept (mutually recognized) | %d |" % has(lambda p: p["load_bearing"] and p.get("label") == "mutually recognized"),
         "| with a point one reviewer accepts (disputed) | %d |" % has(lambda p: p["load_bearing"] and p.get("label") == "disputed"),
         "| selected for rendering (one point each) | %d |" % len(S), "| written (plan + precise A/B + open) | %d |" % len(Wr),
         "| survive all checks and reviews | %d |" % len(sv), "| frozen for evaluation | %d (%s) |" % (len(fr), dict(collections.Counter(c["label"] for c in fr)))]
    if os.path.exists(D + "/RENDER.md"): L += ["\nRender stop reasons: " + open(D + "/RENDER.md").read().split("\n")[2]]
    L.append("\nSelected by kind: %s" % dict(collections.Counter(p["kind"] for p in S.values())))
    open(D + "/FUNNEL.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = CP.configure(sys.argv[1:]); cp = [x[1] for x in a if isinstance(x, tuple)]; a = [x for x in a if not isinstance(x, tuple)]; D = a[0]
    {"freeze": freeze, "run": lambda: run(a[2]), "report": lambda: report(a[2]), "funnel": lambda: funnel(cp[0])}[a[1]]()
