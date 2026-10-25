"""SETUP FOR MANY DATABASES: catalogue (once) and FEASIBILITY -- what the grammar can build on each, with no reviewed pool.
    python -m specbridge.comm.construct.feasibility [db ...] [--workers 6] [--probes 3] [--timeout 600]   -> out/feasibility/<db>.json
Per database: its catalogue (specbridge.pd.realize.semantic, one model review, only if missing), then
  reachable   the (A, S) cells the grammar (compose, frozen) can construct on it: EXACT under the grammar and bounds
  probes      `probes` programs drawn per cell and run through the data checks: a data-valid ESTIMATE (no model calls)
  support     record tables, row quantities, grouping levels (with their names)
  examples    up to 2 data-valid probe programs per cell: construction, quantities, SQL, explicit instructions (V)
Each database runs in its own process with a time limit; a database that fails or times out is recorded with the reason.
Resumable: a database with a feasibility file for the current grammar and catalogue is skipped."""
import concurrent.futures as cf, json, os, subprocess, sys, time

OUT = "out/feasibility"


def _explicit(sql, sp):
    """The example's explicit instructions (V), deterministic from the SQL, rendered on the database snapshot exactly as a
    corpus task is (specbridge.comm.construct.freeze.packaged, level spec, cached); None when the renderer refuses it."""
    try:
        from specbridge.comm.construct.freeze import packaged
        t, _why = packaged("example", sp.db, sql, "feasibility example")
        return t["instruction"].split("\nConventions")[0] if t else None
    except Exception:
        return None


def one(db, probes):
    """In a child process: catalogue if missing, then reachability and probes."""
    from specbridge.pd.realize.semantic import build, path
    t0 = time.time()
    if not os.path.exists(path(db)): build(db, log=lambda *a: None)
    from specbridge.pd.structures.compose import Space, VERSION, _lvlname
    from specbridge.comm.construct.profile import space
    sp = Space(db); cells = space(sp, probes, True); ops = sp.cell_ops()
    cat = json.load(open(path(db)))
    res = {"db": db, "grammar": VERSION, "catalogue": cat.get("version"), "seconds": round(time.time() - t0, 1), "probes": probes,
           "cells": {"%d,%d" % c: {"tables": len(v["tables"]), "routes": v["routes"], "probe_distinct": v["probe_distinct"],
                                    "quantities": v["probe_quantities"], "valid": v["valid"], "checked": v["checked"], "ops": ops.get(c, []),
                                    "examples": [dict(x, instruction=_explicit(x["sql"], sp)) for x in v.get("examples", [])]} for c, v in cells.items()},
           "record_tables": {t: {"quantities": len(sp.qs[t]), "levels": len(sp.levels[t]), "quantity_names": sorted({q["name"] for q in sp.qs[t]}),
                                 "level_names": [_lvlname(sp, L) for L in sp.levels[t]]} for t in sp.rec}}
    os.makedirs(OUT, exist_ok=True); json.dump(res, open("%s/%s.json" % (OUT, db), "w"))
    return res


def run(dbs, workers=6, probes=3, timeout=600):
    from specbridge.pd.structures.compose import VERSION
    def todo(db):
        f = "%s/%s.json" % (OUT, db)
        if not os.path.exists(f): return True
        r = json.load(open(f)); cp = "catalogues/%s.json" % db
        return (r.get("grammar") != VERSION or not os.path.exists(cp) or json.load(open(cp)).get("version") != r.get("catalogue")
                or any("ops" not in c or "examples" not in c for c in (r.get("cells") or {}).values()))
    dbs = [d for d in dbs if todo(d)]; t0 = time.time(); done = 0
    def child(db):
        try:
            p = subprocess.run([sys.executable, "-m", "specbridge.comm.construct.feasibility", "--one", db, "--probes", str(probes)], capture_output=True, text=True, timeout=timeout)
            if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip().splitlines()[-1][:200] if (p.stderr or p.stdout).strip() else "failed")
            return db, "ok"
        except subprocess.TimeoutExpired: why = "timed out after %ds" % timeout
        except Exception as e: why = str(e)[:200]
        os.makedirs(OUT, exist_ok=True); json.dump({"db": db, "grammar": VERSION, "error": why}, open("%s/%s.json" % (OUT, db), "w")); return db, why
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for db, st in ex.map(child, dbs):
            done += 1; sys.stderr.write("[%d/%d %.0fs] %s: %s\n" % (done, len(dbs), time.time() - t0, db, st)); sys.stderr.flush()


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    if a[:1] == ["--one"]: one(a[1], int(opt("--probes", 3))); sys.exit(0)
    dbs = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    if not dbs:
        from specbridge.pd.corpora import ROOTS, TARGETS
        reserved = set(TARGETS["unseen"][1]) - {"financial"}
        dbs = sorted({d for r in ROOTS for d in os.listdir((r % "").rstrip("/")) if os.path.exists(os.path.join(r % d, d + ".sqlite"))} - reserved)
    run(dbs, int(opt("--workers", 6)), int(opt("--probes", 3)), int(opt("--timeout", 600)))
