"""CONSTRUCTION COVERAGE AND CONTROL, MODEL-FREE (paper Stage 1 and Stage 2A; paper/EXPERIMENTS.md).
    python -m specbridge.comm.construct.coverage run <name> <db> [<db> ...] [--workers 6]   -> out/coverage/<name>/<db>/<config>.jsonl, summary.json
    python -m specbridge.comm.construct.coverage report <name>                              -> out/coverage/<name>/COVERAGE.md
Per database, one child process builds the grammar space once and draws every configuration from it
(specbridge.comm.construct.profile.deliver: quotas per cell, distinct SQL, the data checks, answers over 2,000 rows dropped):
  pool        about 100 programs, uniform over the cells this database supports (out/feasibility/<db>.json), no preferences
  shallow / balanced / deep   48 programs over S3-4 / S3-7 / S5-7 (A1-2), seeds 1-3: does a request move the delivered workload?
  ops:<op>=<w>                48 programs over S3-7 (A1-2), one operation's weight changed: does a preference move the mix?
Every program carries its MEASURED (A, S) and the cell it was built for; the receipts (recomputed aggregate, trivial
comparison) are read off its SQL. No model call anywhere: these are generated, mechanically checked programs, not reviewed
benchmark tasks."""
import collections, concurrent.futures as cf, json, os, sqlite3, subprocess, sys, time

OUT = "out/coverage"
SEEDS = (1, 2, 3)
CONTROL = {"shallow": {"arith": [1, 2], "steps": [3, 4]}, "balanced": {"arith": [1, 2], "steps": [3, 7]}, "deep": {"arith": [1, 2], "steps": [5, 7]}}
OPS = [("rank", 3), ("rank", 10), ("share", 10), ("baseline", 0.1)]
REQUIRE = [["rank"], ["share"], ["rank", "share"]]      # required operations (every program uses them), S3-7, A1-2


def configs(db, which="main"):
    if which == "require":
        for need in REQUIRE: yield "require_%s" % "+".join(need), dict(CONTROL["balanced"], count=48, seed=1, require=need)
        return
    cells = json.load(open("out/feasibility/%s.json" % db))["cells"]
    yield "pool", {"cells": {c: 1 for c in cells}, "count": 100, "seed": 1}
    for name, r in CONTROL.items():
        for s in SEEDS: yield "%s_s%d" % (name, s), dict(r, count=48, seed=s)
    for op, w in OPS: yield "ops_%s=%g" % (op, w), dict(CONTROL["balanced"], count=48, seed=1, ops={op: w})


FEATURES = ["agg", "baseline", "share", "rank", "row ranking", "diff", "ratio", "grouped", "multi-table", "A>=2", "S>=5"]


def uses(x, f):
    """Does a delivered program use feature f? Read off the program (its operations, route and measured depth)."""
    from specbridge.comm.construct.pool import ops_of
    if f == "agg": return x["route"]["first_level"] != "row"
    if f == "grouped": return x["route"]["first_level"] in ("eg", "g")
    if f == "multi-table": return x["route"]["multi_table"]
    if f == "row ranking": return x["route"]["first_level"] == "row"
    if f == "A>=2": return x["A"] >= 2
    if f == "S>=5": return x["S"] >= 5
    return f in ops_of(x["construction"])


def one_ondemand(name, db, k=5):
    """ON DEMAND (2026-10-04): for every feature, request k programs that must use it -- operations and structure via
    `require` (Space.route_ok / can), depth thresholds via the requested cells -- over the cells where it is EXACTLY feasible."""
    from specbridge.pd.structures.compose import Space
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.structures import integrity as I
    from specbridge.comm.construct.profile import deliver
    d = "%s/%s/%s" % (OUT, name, db); os.makedirs(d, exist_ok=True)
    sup = {o for c in json.load(open("out/feasibility/%s.json" % db))["cells"].values() for o in (c.get("ops") or [])}
    cells0 = json.load(open("out/feasibility/%s.json" % db))["cells"]
    sup |= {"A>=2"} if any(int(c.split(",")[0]) >= 2 for c in cells0) else set(); sup |= {"S>=5"} if any(int(c.split(",")[1]) >= 5 for c in cells0) else set()
    t0 = time.time(); sp = Space(db); reach = set(sp.reachable()); con = sp.S.con; res = {}
    for f in FEATURES:
        if f in ("A>=2", "S>=5"):
            cells = [c for c in reach if (c[0] >= 2 if f == "A>=2" else c[1] >= 5)]; need = []
        else:
            cells = [c for c in reach if sp.feasible(c, frozenset({f}))]; need = [f]
        r = {"supported_by_feasibility": f in sup, "feasible_cells": len(cells), "requested": k if cells else 0}
        if cells:
            # cells in a seeded order, one at a time, until k programs: a cell either yields programs or is EXHAUSTED (every
            # distinct program drawn and refused by the data checks) -- so "none" over all cells is a proof, not a guess
            import random as _r
            order = sorted(cells); _r.Random(1).shuffle(order); out = []; cells_out = {}; t1 = time.time()
            for c in order:
                if len(out) >= k: break
                got, rep, W = deliver(sp, {"cells": {"%d,%d" % c: 1}, "count": k - len(out), "seed": 1, "require": need, "max_attempts_per_task": 400}, reach, True, max_rows=2000)
                v = rep.get(c, {}); out += got
                cells_out["%d,%d" % c] = {"delivered": len(got), "exhausted": bool(v.get("exhausted")), "shortfall": v.get("shortfall")}
            tried = [v for v in cells_out.values()]
            r.update(delivered=len(out), use_it=sum(uses(x, f) for x in out), depth_ok=sum(x.get("built_for") == "%d,%d" % (x["A"], x["S"]) for x in out),
                     receipts_clean=sum(not I.recomputed(lift(x["sql"], con)) and not I.trivial(lift(x["sql"], con), con) for x in out), seconds=round(time.time() - t1, 1),
                     cells_tried=len(tried), all_tried_exhausted=all(v["exhausted"] for v in tried) and len(tried) == len(cells),
                     status=("generated" if out else "no data-valid program (all feasible cells exhausted)" if all(v["exhausted"] for v in tried) and len(tried) == len(cells) else "undetermined (attempt budget)"),
                     cells=cells_out)
            with open("%s/ondemand_%s.jsonl" % (d, f.replace(">=", "ge").replace(" ", "_")), "w") as fh:
                for x in out: fh.write(json.dumps(x, default=str) + "\n")
        res[f] = r
    json.dump({"db": db, "k": k, "setup_seconds": round(time.time() - t0, 1), "features": res}, open(d + "/summary_ondemand.json", "w"), indent=1, default=str)


def one(name, db, which="main"):
    """All configurations of one database, in this process. -> summary per configuration"""
    from specbridge.pd.structures.compose import Space
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.structures import integrity as I
    from specbridge.comm.construct.profile import deliver
    from specbridge.comm.construct.pool import ops_of
    d = "%s/%s/%s" % (OUT, name, db); os.makedirs(d, exist_ok=True)
    t0 = time.time(); sp = Space(db); reach = set(sp.reachable()); setup = time.time() - t0
    con = sp.S.con; summ = {"db": db, "setup_seconds": round(setup, 1), "configs": {}}
    for cname, req in configs(db, which):
        f = "%s/%s.jsonl" % (d, cname)
        t1 = time.time(); out, rep, W = deliver(sp, req, reach, True, max_rows=2000); secs = time.time() - t1
        for x in out:
            p = lift(x["sql"], con)
            x["receipts"] = {"recomputed": len(I.recomputed(p)), "trivial": len(I.trivial(p, con))}
            x["operations"] = ops_of(x["construction"])
        with open(f, "w") as fh:
            for x in out: fh.write(json.dumps(x, default=str) + "\n")
        summ["configs"][cname] = {"request": req, "seconds": round(secs, 1), "requested": sum(r["requested"] for r in rep.values()),
                                  "delivered": len(out), "cells": {"%d,%d" % c: {"requested": r["requested"], "delivered": r["delivered"], "attempts": r["attempts"],
                                                                                  "fail": dict(r["fail"]), "shortfall": r.get("shortfall")} for c, r in rep.items() if r["requested"]}}
    json.dump(summ, open(d + ("/summary.json" if which == "main" else "/summary_%s.json" % which), "w"), indent=1, default=str)
    return summ


def run(name, dbs, workers=6, which="main"):
    """One child process per database (at most `workers` at once); a database already summarised is skipped."""
    todo = [db for db in dbs if not os.path.exists("%s/%s/%s/%s" % (OUT, name, db, "summary.json" if which == "main" else "summary_%s.json" % which))]
    def child(db):
        t = time.time()
        r = subprocess.run([sys.executable, "-m", "specbridge.comm.construct.coverage", "--one", name, db, which], capture_output=True, text=True)
        print("%s: %s in %.0fs%s" % (db, "ok" if r.returncode == 0 else "FAILED", time.time() - t, "" if r.returncode == 0 else " " + r.stderr[-300:]), flush=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(child, todo))


def tables_read(sql):
    import re
    return set(re.findall(r'(?:FROM|JOIN)\s+"([^"]+)"', sql)) - set(re.findall(r'"(s\d+)"\s+AS', sql)) - {"s%d" % i for i in range(1, 12)}


def report(name):
    base = "%s/%s" % (OUT, name); dbs = sorted(x for x in os.listdir(base) if os.path.exists("%s/%s/summary.json" % (base, x)))
    S = {db: json.load(open("%s/%s/summary.json" % (base, db))) for db in dbs}
    P = {db: {c: [json.loads(l) for l in open("%s/%s/%s.jsonl" % (base, db, c))] for c in S[db]["configs"]} for db in dbs}
    L = ["# Construction coverage and control (`%s`, model-free)\n" % name,
         "Generated, mechanically checked programs (grammar, data checks, measured depth, receipts). No model call; none of these is a reviewed benchmark task.\n",
         "## Stage 1: the pool (about 100 programs per database, uniform over its supported cells)\n",
         "| database | supported cells | requested | delivered | short cells | built-for = measured | recomputed | trivial | distinct SQL | constructions | base quantities | tables | operations | seconds |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    tot = collections.Counter()
    for db in dbs:
        c = S[db]["configs"]["pool"]; X = P[db]["pool"]
        short = [k for k, v in c["cells"].items() if v["delivered"] < v["requested"]]
        agree = sum(1 for x in X if x.get("built_for") == "%d,%d" % (x["A"], x["S"]))
        ops = collections.Counter(o for x in X for o in x["operations"])
        L.append("| %s | %d | %d | %d | %d | %d/%d | %d | %d | %d | %d | %d | %d | %s | %.0f |" % (db, len(c["cells"]), c["requested"], c["delivered"], len(short), agree, len(X),
                 sum(x["receipts"]["recomputed"] > 0 for x in X), sum(x["receipts"]["trivial"] > 0 for x in X), len({x["sql"] for x in X}),
                 len({x["construction"] for x in X}), len({q for x in X for q in x["quantities"]}), len({t for x in X for t in tables_read(x["sql"])}),
                 ", ".join("%s %d" % kv for kv in ops.most_common()), c["seconds"] + S[db]["setup_seconds"]))
        tot.update(requested=c["requested"], delivered=c["delivered"], agree=agree, n=len(X))
    L.append("\nTotal: %d of %d delivered; built-for = measured on %d of %d.\n" % (tot["delivered"], tot["requested"], tot["agree"], tot["n"]))
    L += ["### Shortfalls in the pool (cell: requested -> delivered, reason)\n"]
    for db in dbs:
        for k, v in sorted(S[db]["configs"]["pool"]["cells"].items()):
            if v["delivered"] < v["requested"]: L.append("- %s %s: %d -> %d; %s" % (db, k, v["requested"], v["delivered"], v["shortfall"]))
    L += ["\n## Stage 2A: does a request move the delivered workload? (48 per run, A1-2; mean over seeds 1-3)\n",
          "| database | request | delivered | share at S3-4 | share at S5-7 | mean S | distinct constructions |", "|---|---|---|---|---|---|---|"]
    for db in dbs:
        for nm in CONTROL:
            runs = [P[db]["%s_s%d" % (nm, s)] for s in SEEDS]; X = [x for r in runs for x in r]
            if not X: L.append("| %s | %s | 0 | - | - | - | - |" % (db, nm)); continue
            L.append("| %s | %s | %.1f | %.0f%% | %.0f%% | %.2f | %.1f |" % (db, nm, len(X) / 3, 100 * sum(x["S"] <= 4 for x in X) / len(X), 100 * sum(x["S"] >= 5 for x in X) / len(X),
                     sum(x["S"] for x in X) / len(X), sum(len({x["construction"] for x in r}) for r in runs) / 3))
    L += ["\n## Stage 2A: does an operation preference move the mix? (48 per run, S3-7, A1-2, seed 1; share of programs using the operation)\n",
          "| database | " + " | ".join(["rank (w=1)", "rank (w=3)", "rank (w=10)", "share (w=1)", "share (w=10)", "baseline (w=1)", "baseline (w=0.1)"]) + " |", "|---|" + "---|" * 7]
    for db in dbs:
        def frac(cfg, op):
            X = P[db].get(cfg, []); return "%.0f%% of %d" % (100 * sum(op in x["operations"] for x in X) / len(X), len(X)) if X else "-"
        L.append("| %s | %s |" % (db, " | ".join([frac("balanced_s1", "rank"), frac("ops_rank=3", "rank"), frac("ops_rank=10", "rank"), frac("balanced_s1", "share"),
                                                     frac("ops_share=10", "share"), frac("balanced_s1", "baseline"), frac("ops_baseline=0.1", "baseline")])))
    R = {db: json.load(open("%s/%s/summary_require.json" % (base, db))) for db in dbs if os.path.exists("%s/%s/summary_require.json" % (base, db))}
    if R:
        L += ["\n## Stage 2A: required operations (48 requested per run, S3-7, A1-2, seed 1; `require` in the request)\n",
              "Every delivered program must use the required operations; a cell that no route can build with them is reported, not filled.\n",
              "| database | required | delivered | all use them | built-for = measured | cells not constructible with them |", "|---|---|---|---|---|---|"]
        from specbridge.comm.construct.pool import ops_of
        for db in sorted(R):
            for cname, c in R[db]["configs"].items():
                X = [json.loads(l) for l in open("%s/%s/%s.jsonl" % (base, db, cname))]; need = c["request"]["require"]
                bad = sorted(k for k, v in c["cells"].items() if (v.get("shortfall") or "").startswith("not constructible with"))
                L.append("| %s | %s | %d | %d | %d | %s |" % (db, "+".join(need), len(X), sum(all(n in ops_of(x["construction"]) for n in need) for x in X),
                         sum(x.get("built_for") == "%d,%d" % (x["A"], x["S"]) for x in X), ", ".join(bad) or "none"))
    open(base + "/COVERAGE.md", "w").write("\n".join(L) + "\n")
    return "\n".join(L)


def meaning_ondemand(name, workers=12, rounds=8):
    """MEANINGFUL ON DEMAND (2026-10-05): the benchmark review (rubric v1.1: Opus and Sonnet each alone; both must find the meaning
    coherent and the answer determined) applied to the programs generated on demand. A (database, feature) counts when at least
    one generated program of that database that USES the feature passes. As in the build pipeline, each round asks only for
    what is still missing and reuses every earlier verdict on the same SQL (cached per call): per database, the fewest
    unreviewed programs that cover the features still lacking a passing program (greedy cover). A failed call leaves the program
    unreviewed (never a rejection). A pair with no passing program among those generated is NOT proven impossible."""
    import glob
    from specbridge.comm.construct.rubric import judge, combine, VERSION as RV
    from specbridge.comm.construct.freeze import packaged, snapshot
    fname = lambda f: f.replace(">=", "ge").replace(" ", "_")
    progs, pairs = {}, set()
    for d in sorted(glob.glob("%s/%s/*/" % (OUT, name))):
        db = d.rstrip("/").split("/")[-1]
        for f in FEATURES:
            fp = "%s/ondemand_%s.jsonl" % (d, fname(f))
            xs = [json.loads(l) for l in open(fp)] if os.path.exists(fp) else []
            if xs: pairs.add((db, f))
            for x in xs: progs[x["id"]] = x
    feats = {i: {f for f in FEATURES if uses(x, f)} for i, x in progs.items()}
    verdict, unpack = {}, set()
    passes = lambda i: verdict.get(i, {}).get("meaning") == "yes" and verdict.get(i, {}).get("determined") == "yes"
    def met(db, f): return any(passes(i) and f in feats[i] for i, x in progs.items() if x["database"] == db and i in verdict)
    snaps = {}
    for r in range(rounds):
        todo = []
        for db in sorted({k[0] for k in pairs}):
            need = {f for (d, f) in pairs if d == db and not met(d, f)}
            cand = sorted(i for i, x in progs.items() if x["database"] == db and i not in verdict and i not in unpack)
            while need:
                best = max(cand, key=lambda i: (len(feats[i] & need), i), default=None)
                if best is None or not feats[best] & need: break
                todo.append(best); need -= feats[best]; cand.remove(best)
        if not todo: break
        tasks = []
        for i in todo:
            x = progs[i]; db = x["database"]
            if db not in snaps: snaps[db] = snapshot(db)[0]
            t, _w = packaged(i, db, x["sql"], "ondemand", level="spec")
            if not t: unpack.add(i); continue
            tasks.append({"id": i, "db": db, "sql": x["sql"], "spec": t["instruction"], "snapshot": snaps[db]})
        J = judge(tasks, workers=workers)
        for t in tasks:
            q = combine(J.get(t["id"], {}))
            if q["meaning"] != "unreviewed": verdict[t["id"]] = q
        print("round %d: reviewed %d programs, pairs met %d/%d" % (r + 1, len(tasks), sum(met(*k) for k in pairs), len(pairs)), flush=True)
    exhausted = lambda db, f: all(i in verdict or i in unpack for i, x in progs.items() if x["database"] == db and f in feats[i])
    by = {f: {"generated": sum(1 for k in pairs if k[1] == f), "meaningful": sum(met(*k) for k in pairs if k[1] == f),
              "none_among_generated": sum(1 for k in pairs if k[1] == f and not met(*k) and exhausted(*k)),
              "unreviewed": sum(1 for k in pairs if k[1] == f and not met(*k) and not exhausted(*k))} for f in FEATURES}
    out = {"rubric": RV, "databases": len({k[0] for k in pairs}), "programs_reviewed": len(verdict), "programs_passing": sum(map(passes, verdict)),
           "features": by, "pairs": {"%s|%s" % k: met(*k) for k in sorted(pairs)}, "verdicts": verdict}
    json.dump(out, open("%s/%s/meaning_ondemand.json" % (OUT, name), "w"), indent=1, default=str)
    return out

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--one":
        if len(a) > 3 and a[3] == "ondemand": one_ondemand(a[1], a[2])
        else: one(a[1], a[2], a[3] if len(a) > 3 else "main")
        sys.exit(0)
    if a[0] == "run":
        dbs = [x for i, x in enumerate(a[2:], 2) if not x.startswith("--") and a[i - 1] not in ("--workers", "--set")]
        run(a[1], dbs, int(a[a.index("--workers") + 1]) if "--workers" in a else 6, a[a.index("--set") + 1] if "--set" in a else "main")
    elif a[0] == "report": print(report(a[1]))
    elif a[0] == "meaning": meaning_ondemand(a[1], int(a[a.index("--workers") + 1]) if "--workers" in a else 12)
