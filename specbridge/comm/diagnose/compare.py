"""STEP 2: the same solver on the original wording and on explicit V; everything else identical.
    python -m specbridge.comm.diagnose.compare run <dir> <model> [repeats]
    python -m specbridge.comm.diagnose.compare report <dir> <model>
Runs: <dir>/runs/<model>/<arm>_rep<r>/<task>.json with pass (BIRD set match) and tol (within 0.005)."""
import collections, json, os, re, sys
from specbridge.comm.common import db as DB, grade as G
from specbridge.comm.common.solve import solve


def tasks(d, arm): return [json.loads(l) for l in open("%s/tasks_%s.jsonl" % (d, arm))]


def run(d, model, repeats=2, bsize=8):
    """bsize: questions per solver call. BIRD's diagnosis batches ran with 8 (distinct questions); Spider (2026-10-03) runs with 1."""
    for rep in range(repeats):
        for arm in ("original", "explicit"):
            T = {t["id"]: t for t in tasks(d, arm)}
            out = "%s/runs/%s/%s_rep%d" % (d, re.sub(r"\W", "_", model), arm, rep)
            res = solve([{"key": k, "text": t["instruction"], "snapshot": t["snapshot"], "database": t["database"]} for k, t in T.items()], model, out, bsize=bsize)
            for k, o in res.items():
                a = o.get("answer")
                o["pass"] = a is not None and G.bird_ex(T[k]["reference_answer"], a); o["tol"] = a is not None and G.tol_match(T[k]["reference_answer"], a)
                json.dump(o, open("%s/%s.json" % (out, k), "w"), default=str)


def rerun(d):
    """After ALL runs of a directory finish: every final query that did not execute is run again alone under the same limit
    (load-induced timeouts are not answers; specbridge.comm.construct.solver_eval.serial_rerun), then pass / tol re-graded.
    Recorded on the run as "serial_rerun"."""
    import glob
    T = {t["id"]: t for arm in ("original", "explicit") if os.path.exists("%s/tasks_%s.jsonl" % (d, arm)) for t in tasks(d, arm)}
    n = collections.Counter()
    for f in glob.glob("%s/runs/*/*/*.json" % d):
        o = json.load(open(f))
        if not o.get("final") or o.get("answer") is not None or o.get("serial_rerun"): continue
        t = T[os.path.basename(f)[:-5]]; a = DB.rows(DB.connect(t["snapshot"]), o["final"])
        o["serial_rerun"] = "executes" if a is not None else "still fails"; n[o["serial_rerun"]] += 1
        if a is not None:
            o.update(answer=a, executes=True); o["pass"] = G.bird_ex(t["reference_answer"], a); o["tol"] = G.tol_match(t["reference_answer"], a)
        json.dump(o, open(f, "w"), default=str)
    print("serial re-run:", dict(n))


def runs(d, model, arm, tid):
    base = "%s/runs/%s" % (d, re.sub(r"\W", "_", model)); out = []
    for r in range(10):
        f = "%s/%s_rep%d/%s.json" % (base, arm, r, tid)
        if os.path.exists(f): out.append(json.load(open(f)))
    return out


def report(d, model):
    T = tasks(d, "original"); E = {t["id"] for t in tasks(d, "explicit")}
    v = lambda gs: None if not gs else "pass" if all(g["pass"] for g in gs) else "fail" if not any(g["pass"] for g in gs) else "mixed"
    L = ["# Original vs explicit V (%s)\n" % model, "| category | tasks | original pass (runs) | explicit pass (runs) |", "|---|---|---|---|"]
    for cat in sorted({t["category"] for t in T}) + [None]:
        ts = [t for t in T if cat is None or t["category"] == cat]
        o = [g for t in ts for g in runs(d, model, "original", t["id"])]; e = [g for t in ts if t["id"] in E for g in runs(d, model, "explicit", t["id"])]
        L.append("| %s | %d | %d/%d | %d/%d |" % (cat or "**all**", len(ts), sum(g["pass"] for g in o), len(o), sum(g["pass"] for g in e), len(e)))
    paired = [{"id": t["id"], "category": t["category"], "original": v(runs(d, model, "original", t["id"])),
               "explicit": v(runs(d, model, "explicit", t["id"])) if t["id"] in E else "refused"} for t in T]
    L.append("\nPaired per task: %s" % dict(collections.Counter((p["original"], p["explicit"]) for p in paired)))
    json.dump(paired, open("%s/paired_%s.json" % (d, re.sub(r"\W", "_", model)), "w"), indent=1)
    open("%s/RESULTS_%s.md" % (d, re.sub(r"\W", "_", model)), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]
    {"run": lambda: run(a[1], a[2], int(a[3]) if len(a) > 3 else 2, int(a[4]) if len(a) > 4 else 8), "report": lambda: report(a[1], a[2]), "rerun": lambda: rerun(a[1])}[a[0]]()
