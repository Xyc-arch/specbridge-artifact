"""THE EXACT-OUTPUT GATE for P_D (specbridge.pd.structures.compose + specbridge.comm.construct.profile).
    python -m specbridge.tests.test_gate            compare with specbridge/tests/golden/compose.json; exit 1 on a COMPUTATION change
    python -m specbridge.tests.test_gate --update   record the current outputs as the golden ones (an intentional change)
For each fixed workload (database, request, seed), from a cold check cache:
  computation  the reachable cells; per delivered task its SQL, measured (A, S) and check outcome; per cell requested,
               delivered, attempts, duplicates, failures. A change here is a change in WHAT P_D produces.
  metadata     the construction names, quantities and reasons attached to each task. A change here is reported, not failed.
  runtime      seconds, cold; compared with the golden run (reported, not failed: speed may change, output may not)."""
import hashlib, json, os, shutil, sys, tempfile, time

WORKLOADS = [("student_club", {"preset": "medium", "count": 30, "seed": 42}),
             ("sakila_1", {"arith": [0, 1], "steps": [3, 4], "count": 30, "seed": 42}),
             ("soccer_1", {"mix": [{"preset": "shallow", "weight": 0.5}, {"preset": "deep", "weight": 0.5}], "count": 30, "seed": 42})]
GOLDEN = "specbridge/tests/golden/compose.json"


def fingerprint(db, req):
    from specbridge.pd.structures.compose import Space
    from specbridge.comm.construct.profile import deliver
    t0 = time.time(); sp = Space(db); R = sp.reachable()
    out, rep, _W = deliver(sp, req, set(R), checks=True)
    comp = {"reachable": sorted("%d,%d" % c for c in R),
            "tasks": [[x["sql"], x["A"], x["S"]] for x in out],
            "cells": {"%d,%d" % c: [r["requested"], r["delivered"], r["attempts"], r["duplicates"], sorted(dict(r["fail"]).items())] for c, r in sorted(rep.items())}}
    meta = [[x["construction"], x["quantities"], x["why"]] for x in out]
    h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True, default=str).encode()).hexdigest()[:16]
    return {"computation": h(comp), "metadata": h(meta), "tasks": len(out), "seconds": round(time.time() - t0, 2)}


def main():
    tmp = tempfile.mkdtemp(); os.environ["COMPOSE_CHECK_CACHE"] = tmp
    try: now = {"%s %s" % (db, json.dumps(req, sort_keys=True)): fingerprint(db, req) for db, req in WORKLOADS}
    finally: shutil.rmtree(tmp, ignore_errors=True)
    from specbridge.pd.structures.compose import VERSION
    if "--update" in sys.argv or not os.path.exists(GOLDEN):
        why = sys.argv[sys.argv.index("--update") + 1] if "--update" in sys.argv and len(sys.argv) > sys.argv.index("--update") + 1 else "first record"
        old = json.load(open(GOLDEN)) if os.path.exists(GOLDEN) else {}
        hist = old.get("_history", []) + [{"grammar": VERSION, "reason": why, "at": time.strftime("%Y-%m-%d %H:%M"),
                                          "changed": sorted(k for k in now if k in old and old[k]["computation"] != now[k]["computation"])}]
        os.makedirs(os.path.dirname(GOLDEN), exist_ok=True); json.dump(dict(now, _history=hist), open(GOLDEN, "w"), indent=1)
        print("golden recorded (%s): %s" % (VERSION, why)); return 0
    gold = json.load(open(GOLDEN)); bad = 0
    for k, v in now.items():
        g = gold.get(k)
        if k.startswith("_"): continue
        if not g: print("NEW      %s" % k); continue
        comp = "same" if v["computation"] == g["computation"] else "CHANGED"; bad += comp != "same"
        print("%-8s %s | computation %s | metadata %s | tasks %d | %.1fs (golden %.1fs)" % ("ok" if comp == "same" else "FAIL", k[:70], comp,
              "same" if v["metadata"] == g["metadata"] else "changed", v["tasks"], v["seconds"], g["seconds"]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
