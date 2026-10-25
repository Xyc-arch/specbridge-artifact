"""DEPTH-STRATIFIED SENSIBILITY OF THE FROZEN GRAMMAR (compose-v3): which regions of P_D produce useful tasks?
    python -m specbridge.comm.construct.research.depth_eval [db ...] [--per-cell 4] [--seed 2026]   -> out/depth_eval/<grammar version>/REPORT.md, results.json
Per database, per reachable (A, S) cell: `per_cell` programs drawn by the sampler (equal weight on every reachable cell,
fixed seed) that pass the data checks -> explicit V (spec-level packaging) -> the sensibility veto, each task judged alone
(opus + sonnet, kept only if both say sensible) -> the independent auditor (fable) on every kept task.
Reported by MEASURED depth: sampled, kept, useful (kept and audited useful), acceptable, not meaningful; diversity of the
useful tasks; and by operation. The veto and the auditor are separate judgments, neither is ground truth; the single-task
veto's decisions flip on about 5% of tasks between repeated calls (specbridge.comm.construct.research.recheck)."""
import collections, json, os, sys, time
from specbridge.pd.structures.compose import Space, VERSION
from specbridge.comm.construct.profile import deliver
from specbridge.comm.construct.freeze import packaged
from specbridge.comm.construct.research.veto import judge
from specbridge.comm.construct.research.filtered import audit
from specbridge.comm.common.llm import CALLS

DBS = ["student_club", "financial", "formula_1", "sakila_1", "soccer_1", "college_2"]
DEV = {"student_club", "financial", "formula_1", "college_2", "sakila_1", "soccer_1"}   # all six informed earlier work


def ops_of(c):
    """The operations in a construction sequence ('agg:e > baseline:all > rank' -> {'baseline', 'rank'}), aggregation implied."""
    return sorted({p.split(":")[0] for p in c.split(" > ")} - {"agg", "rows"}) or ["aggregate only" if "agg" in c else "row ranking"]


def run(dbs, per_cell=4, seed=2026):
    OUT = "out/depth_eval/%s" % VERSION; os.makedirs(OUT, exist_ok=True); T0 = time.time(); rows = []
    for db in dbs:
        sp = Space(db); R = sp.reachable()
        out, rep, _W = deliver(sp, {"cells": {"%d,%d" % c: 1 for c in R}, "count": per_cell * len(R), "seed": seed}, set(R))
        tasks = []
        for x in out:
            t, why = packaged(x["id"], db, x["sql"], "compose " + x["construction"], level="spec", A=x["A"], S=x["S"],
                              construction=x["construction"], quantities=x["quantities"], why_built=x["why"])
            if t: tasks.append(t)
            else: rows.append(dict(x, stage="packaging refused", reason=why))
        V = judge([{"id": t["id"], "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0], "snapshot": t["snapshot"], "database": db} for t in tasks],
                  cache="out/cache/veto/%s" % db)
        kept = [t for t in tasks if V.get(t["id"], {}).get("kept")]
        A = audit(kept, cache="out/cache/audit/%s" % db)
        for t in tasks:
            v = V.get(t["id"], {}); a = A.get(t["id"]) or {}
            rows.append({"db": db, "id": t["id"], "A": t["A"], "S": t["S"], "construction": t["construction"], "quantities": t["quantities"],
                         "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0], "veto": v.get("labels"), "veto_reasons": v.get("reasons"),
                         "kept": bool(v.get("kept")), "audit": a.get("label"), "audit_reason": a.get("reason"), "stage": "reviewed"})
        shortfall = {"%d,%d" % c: r.get("shortfall") for c, r in rep.items() if r.get("shortfall")}
        rows.append({"db": db, "stage": "sampling", "shortfall": shortfall, "reachable": len(R)})
        print("%s: %d reviewed, %d kept, %d useful (%.0fs so far)" % (db, len(tasks), len(kept), sum((A.get(t["id"]) or {}).get("label") == "useful" for t in kept), time.time() - T0), flush=True)
    json.dump({"grammar": VERSION, "per_cell": per_cell, "seed": seed, "rows": rows, "seconds": time.time() - T0, "model_calls": dict(CALLS)},
              open(OUT + "/results.json", "w"), default=str)
    report(rows, per_cell, seed, time.time() - T0, OUT)


def tally(xs):
    k = [x for x in xs if x["kept"]]
    return {"n": len(xs), "kept": len(k), "useful": sum(x["audit"] == "useful" for x in k), "acceptable": sum(x["audit"] == "acceptable" for x in k),
            "not": sum(x["audit"] == "not meaningful" for x in k)}


def report(rows, per_cell, seed, secs, OUT="out/depth_eval/" + VERSION):
    R = [x for x in rows if x.get("stage") == "reviewed"]
    L = ["# Which regions of P_D produce useful tasks? (grammar %s, frozen)\n" % VERSION,
         "%d programs per reachable (A, S) cell per database (seed %d), each passing the data checks, packaged with explicit V; "
         "veto = opus + sonnet, each task judged alone, kept only if both say sensible; audit = fable on every kept task. "
         "**useful** = kept and audited useful. Depth is measured on the SQL. All six databases informed earlier work (development evidence). %.0f min.\n" % (per_cell, seed, secs / 60)]
    def table(title, key, keys):
        out = ["## %s\n" % title, "| %s | sampled | kept by veto | useful | acceptable | not meaningful | useful / sampled |" % title.split(" ")[-1], "|---|---|---|---|---|---|---|"]
        for k in keys:
            t = tally([x for x in R if key(x) == k])
            if t["n"]: out.append("| %s | %d | %d | %d | %d | %d | %.0f%% |" % (k, t["n"], t["kept"], t["useful"], t["acceptable"], t["not"], 100.0 * t["useful"] / t["n"]))
        return out
    L += table("By arithmetic depth A", lambda x: x["A"], range(0, 7)) + [""]
    L += table("By step depth S", lambda x: x["S"], range(1, 9)) + [""]
    L += table("By database", lambda x: x["db"], DBS) + [""]
    opk = collections.defaultdict(list)
    for x in R:
        for o in ops_of(x["construction"]): opk[o].append(x)
    L += ["## By operation used\n", "| operation | sampled | kept | useful | not meaningful | useful / sampled |", "|---|---|---|---|---|---|"]
    for o, xs in sorted(opk.items(), key=lambda z: -len(z[1])):
        t = tally(xs); L.append("| %s | %d | %d | %d | %d | %.0f%% |" % (o, t["n"], t["kept"], t["useful"], t["not"], 100.0 * t["useful"] / t["n"]))
    L += ["\n## The A x S grid, all databases: useful / sampled\n", "| A \\ S | " + " | ".join(str(s) for s in range(1, 9)) + " |", "|---|" + "---|" * 8]
    for a in range(0, 7):
        cells = []
        for s in range(1, 9):
            t = tally([x for x in R if x["A"] == a and x["S"] == s]); cells.append("%d/%d" % (t["useful"], t["n"]) if t["n"] else "--")
        L.append("| **%d** | " % a + " | ".join(cells) + " |")
    U = [x for x in R if x["kept"] and x["audit"] == "useful"]
    L += ["\n## Diversity of the useful tasks\n",
          "%d useful tasks: %d distinct base quantities, %d construction sequences, %d databases. Deep (A >= 2 and S >= 4): %d useful of %d sampled." % (
              len(U), len({q for x in U for q in x["quantities"]}), len({x["construction"] for x in U}), len({x["db"] for x in U}),
              sum(x["A"] >= 2 and x["S"] >= 4 for x in U), sum(x["A"] >= 2 and x["S"] >= 4 for x in R))]
    sf = [x for x in rows if x.get("stage") == "sampling"]
    L.append("\nSampling shortfalls (cells that could not supply %d programs passing the checks): %s" % (per_cell, "; ".join("%s %s" % (x["db"], x["shortfall"]) for x in sf if x["shortfall"]) or "none"))
    L.append("\n## Deep tasks the reviewers rejected or found not meaningful (a random 12)\n")
    import random
    bad = [x for x in R if x["A"] + x["S"] >= 6 and (not x["kept"] or x["audit"] == "not meaningful")]
    for x in random.Random(1).sample(bad, min(12, len(bad))):
        L += ["- **%s** A%d S%d `%s`: veto %s; auditor %s" % (x["db"], x["A"], x["S"], x["construction"], x["veto"], x["audit"] or "-"),
              "  - %s" % ((x.get("veto_reasons") or {}).get("sonnet") or (x.get("veto_reasons") or {}).get("opus") or x.get("audit_reason") or "")[:300]]
    L.append("\n## Deep useful tasks (a random 8)\n")
    for x in random.Random(2).sample([x for x in U if x["A"] + x["S"] >= 6], min(8, len([x for x in U if x["A"] + x["S"] >= 6]))):
        L += ["- **%s** A%d S%d `%s`" % (x["db"], x["A"], x["S"], x["construction"]), "  - %s" % x["spec"][:700].replace("\n", " / ")]
    open(OUT + "/REPORT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:80]))


def compare(old="compose-v3", new=None):
    """Old vs new grammar version on the reviewed samples: useful yield by measured depth and ABSOLUTE useful diversity."""
    new = new or VERSION
    R = {v: [x for x in json.load(open("out/depth_eval/%s/results.json" % v))["rows"] if x.get("stage") == "reviewed"] for v in (old, new)}
    use = lambda x: x["kept"] and x["audit"] == "useful"
    L = ["# %s vs %s: useful yield and absolute useful diversity\n" % (old, new),
         "Same protocol (4 programs per reachable cell per database, seed 2026, single-task veto + audit). Development evidence.\n",
         "| | %s | %s |" % (old, new), "|---|---|---|"]
    def row(name, f): L.append("| %s | %s | %s |" % (name, f(R[old]), f(R[new])))
    row("sampled", lambda xs: len(xs))
    row("kept by the veto", lambda xs: sum(x["kept"] for x in xs))
    row("useful", lambda xs: sum(map(use, xs)))
    row("not meaningful (audited, among kept)", lambda xs: sum(x["kept"] and x["audit"] == "not meaningful" for x in xs))
    row("distinct base quantities in useful", lambda xs: len({q for x in xs if use(x) for q in x["quantities"]}))
    row("distinct tables in useful", lambda xs: len({(x["db"], q.split(".")[0]) for x in xs if use(x) for q in x["quantities"]}))
    row("distinct constructions in useful", lambda xs: len({x["construction"] for x in xs if use(x)}))
    row("(db, A, S) cells with a useful task", lambda xs: len({(x["db"], x["A"], x["S"]) for x in xs if use(x)}))
    row("deep (A>=2, S>=4): useful / sampled", lambda xs: "%d / %d" % (sum(use(x) for x in xs if x["A"] >= 2 and x["S"] >= 4), sum(x["A"] >= 2 and x["S"] >= 4 for x in xs)))
    for k, lab in (("A", "arithmetic depth"), ("S", "step depth")):
        L += ["\n## Useful / sampled by %s\n" % lab, "| %s | %s | %s |" % (k, old, new), "|---|---|---|"]
        for v in sorted({x[k] for xs in R.values() for x in xs}):
            f = lambda xs: "%d / %d" % (sum(use(x) for x in xs if x[k] == v), sum(x[k] == v for x in xs)) if any(x[k] == v for x in xs) else "--"
            L.append("| %d | %s | %s |" % (v, f(R[old]), f(R[new])))
    open("out/depth_eval/%s/COMPARE.md" % new, "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--compare"]: compare(); sys.exit(0)
    a = sys.argv[1:]; dbs = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))] or DBS
    run(dbs, int(a[a.index("--per-cell") + 1]) if "--per-cell" in a else 4, int(a[a.index("--seed") + 1]) if "--seed" in a else 2026)
