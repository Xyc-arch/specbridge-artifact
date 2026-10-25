"""THE SETUP PATH: reviewed task pools and the saved profile, once per database and version (never on a user request).
    python -m specbridge.comm.construct.pool build <db> [<db> ...]                  from out/depth_eval/results.json
    python -m specbridge.comm.construct.pool replenish <db> [--per-cell 4] [--cells 2,4 3,5]   generate + check + review more, add them
    python -m specbridge.comm.construct.pool status [<db> ...]
  -> out/pool/<db>/pool.jsonl (every reviewed task, with its tier), out/pool/<db>/profile.json (per cell: constructible,
     likely useful, ready now), out/pool/<db>/log.jsonl (what each build/replenish added)
TIERS (a task's review, never inferred from its cell):
  approved     kept by the veto (opus and sonnet, each task alone) AND audited useful (fable)
  acceptable   kept by the veto and audited acceptable (coherent, of little interest)
  rejected     vetoed, or audited not meaningful -- kept in the pool file for the record, never served
A pool is tied to its grammar version and the database's catalogue version: an entry built under another version is
reported as stale and not served (its cell may have changed meaning)."""
import collections, hashlib, json, os, sys, time
from specbridge.pd.structures.compose import Space, VERSION

ROOT = "out/pool"


def bench(e):
    """The benchmark standard: coherent meaning and a determined answer (rubric, both reviewers)."""
    q = e.get("quality") or {}
    return q.get("meaning") == "yes" and q.get("determined") == "yes"


def signature(e): return (e["db"], e["construction"], tuple(sorted(e["quantities"])))


def diversity(es):
    """Not corpus size: distinct computations (construction + base quantities), quantities, tables, constructions."""
    return {"tasks": len(es), "computations": len({signature(e) for e in es}), "quantities": len({(e["db"], q) for e in es for q in e["quantities"]}),
            "tables": len({(e["db"], t) for e in es for t in e["tables"]}), "constructions": len({(e["db"], e["construction"]) for e in es})}


def cat_version(db): return json.load(open("catalogues/%s.json" % db)).get("version")


def tier(kept, audit):
    if not kept: return "rejected"
    return {"useful": "approved", "acceptable": "acceptable"}.get(audit, "rejected")


def ops_of(c):
    return sorted({p.split(":")[0] for p in c.split(" > ")} - {"agg", "rows"}) or ["aggregate only" if "agg" in c else "row ranking"]


def load(db):
    f = "%s/%s/pool.jsonl" % (ROOT, db)
    return [json.loads(l) for l in open(f)] if os.path.exists(f) else []


def save(db, entries, note):
    d = "%s/%s" % (ROOT, db); os.makedirs(d, exist_ok=True)
    with open(d + "/pool.jsonl", "w") as f:
        for e in entries: f.write(json.dumps(e) + "\n")
    with open(d + "/log.jsonl", "a") as f: f.write(json.dumps(dict(note, at=time.strftime("%Y-%m-%d %H:%M"))) + "\n")


def entry(db, r, cv):
    return {"quality": r.get("quality"), **{"id": r["id"], "db": db, "A": r["A"], "S": r["S"], "sql": r["sql"], "spec": r["spec"], "construction": r["construction"],
            "ops": ops_of(r["construction"]), "tables": sorted({q.split(".")[0] for q in r["quantities"]}), "quantities": r["quantities"],
            "tier": tier(r["kept"], r["audit"]) if r.get("kept") is not None else "rubric-only", "veto": r["veto"], "audit": r["audit"], "audit_reason": r.get("audit_reason"),
            "grammar": VERSION, "catalogue": cv}}


def add(db, rows, note):
    cv = cat_version(db); cur = load(db); seen = {e["sql"] for e in cur}; new = [entry(db, r, cv) for r in rows if r["sql"] not in seen]
    save(db, cur + new, dict(note, added=len(new), approved=sum(e["tier"] == "approved" for e in new)))
    profile(db); return new


def affected_v31(construction):
    """Is a construction touched by the v3.1 rule? Only a comparison (baseline, share) FOLLOWED by an aggregation or another
    comparison can be; anything else is built identically by v3 and v3.1."""
    parts = construction.split(" > ")
    for i, p in enumerate(parts):
        if p.split(":")[0] in ("baseline", "share") and any(q.split(":")[0] in ("agg", "baseline", "share") for q in parts[i + 1:]): return True
    return False


def migrate(dbs, frm="compose-v3"):
    """Carry reviewed tasks to the current grammar where the change cannot touch them; RETIRE the rest (kept on file with
    their review, never served; their cells get fresh samples under the current grammar)."""
    for db in dbs:
        P = load(db); carried = retired = 0
        for e in P:
            if e["grammar"] != frm: continue
            if affected_v31(e["construction"]): e["retired"] = "touched by %s" % VERSION; retired += 1
            else: e["grammar"] = VERSION; e["carried_from"] = frm; carried += 1
        save(db, P, {"source": "migrate %s -> %s" % (frm, VERSION), "carried": carried, "retired": retired}); profile(db)
        print("%s: carried %d, retired %d" % (db, carried, retired))


def build(dbs, source="out/depth_eval/%s/results.json" % VERSION):
    R = json.load(open(source)); rows = [x for x in R["rows"] if x.get("stage") == "reviewed"]
    for db in dbs:
        new = add(db, [x for x in rows if x["db"] == db], {"source": source, "seed": R["seed"], "per_cell": R["per_cell"]})
        print("%s: %d reviewed tasks added (%d approved)" % (db, len(new), sum(e["tier"] == "approved" for e in new)))


def profile(db):
    """Per cell: constructible (exact, the grammar's reachability), likely useful (approved / reviewed: an ESTIMATE from the
    reviewed samples, with n), ready now (approved and acceptable tasks in the pool, current versions only)."""
    sp = Space(db); R = sp.reachable(); cv = cat_version(db); P = load(db)
    live = [e for e in P if e["grammar"] == VERSION and e["catalogue"] == cv]
    cells = {}
    for c in sorted(set(R) | {(e["A"], e["S"]) for e in live}):
        es = [e for e in live if (e["A"], e["S"]) == c]
        n = len(es); ap = sum(e["tier"] == "approved" for e in es); ac = sum(e["tier"] == "acceptable" for e in es)
        qa = [e for e in es if e.get("quality")]; bp = [e for e in qa if bench(e)]
        cells["%d,%d" % c] = {"constructible": c in R, "reviewed": n, "likely_useful": (ap / n) if n else None,
                              "ready_approved": ap, "ready_acceptable": ac,
                              "assessed": len(qa), "benchmark_pass": len(bp), "benchmark_rate": (len(bp) / len(qa)) if qa else None,
                              "uncertain": sum(e["quality"]["meaning"] == "uncertain" for e in qa), "diversity": diversity(bp)}
    out = {"db": db, "grammar": VERSION, "catalogue": cv, "cells": cells, "stale_entries": len(P) - len(live),
           "benchmark_diversity": diversity([e for e in live if bench(e)]), "complexity": "not assessed",
           "built": time.strftime("%Y-%m-%d %H:%M")}
    json.dump(out, open("%s/%s/profile.json" % (ROOT, db), "w"), indent=1); return out


def replenish(db, cells=None, per_cell=4):
    """Generate, check, package and review more tasks for the given cells (default: every constructible cell), and add them.
    Background work: it calls the models; the request path never does."""
    from specbridge.comm.construct.profile import deliver
    from specbridge.comm.construct.freeze import packaged
    from specbridge.comm.construct.research.veto import judge
    from specbridge.comm.construct.research.filtered import audit
    sp = Space(db); R = sp.reachable(); cells = cells or sorted(R)
    rounds = sum(1 for l in open("%s/%s/log.jsonl" % (ROOT, db))) if os.path.exists("%s/%s/log.jsonl" % (ROOT, db)) else 0
    seed = 2026 + 1000 * rounds; have = {e["sql"] for e in load(db)}
    out, _rep, _W = deliver(sp, {"cells": {"%d,%d" % c: 1 for c in cells}, "count": per_cell * len(cells), "seed": seed}, set(R))
    out = [x for x in out if x["sql"] not in have]
    tasks = [t for t in (packaged(x["id"], db, x["sql"], "compose " + x["construction"], level="spec", A=x["A"], S=x["S"], construction=x["construction"],
                                  quantities=x["quantities"])[0] for x in out) if t]
    from specbridge.comm.construct.rubric import judge as rjudge, combine, VERSION as RV
    J = rjudge([{"id": t["id"], "db": db, "sql": t["reference_sql"], "spec": t["instruction"], "snapshot": t["snapshot"]} for t in tasks])
    rows = []
    for t in tasks:
        qv = combine(J.get(t["id"], {}))
        rows.append({"id": t["id"], "A": t["A"], "S": t["S"], "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0],
                     "construction": t["construction"], "quantities": t["quantities"], "kept": None, "veto": None, "audit": None, "quality": qv})
    new = add(db, rows, {"source": "replenish", "seed": seed, "cells": ["%d,%d" % c for c in cells], "per_cell": per_cell})
    print("%s: replenished %d (%d pass the benchmark standard)" % (db, len(new), sum(bench(e) for e in new)))
    return new


def expand(dbs, min_rate=0.6, min_n=3, per_cell=8):
    """MORE WHERE IT PAYS: cells whose assessed benchmark pass rate is at least min_rate on at least min_n tasks get per_cell
    new programs (generate -> data checks -> rubric). Reports the MARGINAL diversity each batch adds, not just its size."""
    rep = []
    for db in dbs:
        p = profile(db); cells = [tuple(int(v) for v in k.split(",")) for k, c in p["cells"].items()
                                  if c["constructible"] and (c.get("assessed") or 0) >= min_n and (c.get("benchmark_rate") or 0) >= min_rate]
        if not cells: rep.append((db, [], 0, 0, {}, {})); continue
        before = diversity([e for e in load(db) if bench(e) and not e.get("retired") and e["grammar"] == VERSION])
        new = replenish(db, cells, per_cell)
        after = diversity([e for e in load(db) if bench(e) and not e.get("retired") and e["grammar"] == VERSION])
        rep.append((db, cells, len(new), sum(bench(e) for e in new), before, after))
    L = ["| database | cells expanded | new tasks | pass benchmark | computations | quantities | tables | constructions |", "|---|---|---|---|---|---|---|---|"]
    for db, cells, n, b, bf, af in rep:
        f = lambda k: "%d -> %d" % (bf.get(k, 0), af.get(k, 0)) if af else "-"
        L.append("| %s | %d | %d | %d | %s | %s | %s | %s |" % (db, len(cells), n, b, f("computations"), f("quantities"), f("tables"), f("constructions")))
    print("\n".join(L)); return rep


def status(dbs):
    for db in dbs:
        p = json.load(open("%s/%s/profile.json" % (ROOT, db)))
        c = p["cells"]; d = p.get("benchmark_diversity", {})
        print("%-13s constructible cells %d | assessed %d | benchmark pass %d (uncertain %d) | diversity of passing: %d computations, %d quantities, %d tables, %d constructions | complexity: %s" % (
            db, sum(v["constructible"] for v in c.values()), sum(v.get("assessed") or 0 for v in c.values()), sum(v.get("benchmark_pass") or 0 for v in c.values()),
            sum(v.get("uncertain") or 0 for v in c.values()), d.get("computations", 0), d.get("quantities", 0), d.get("tables", 0), d.get("constructions", 0), p.get("complexity")))


if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dbs = [x for x in a[1:] if not x.startswith("--") and "," not in x and not x.isdigit()] or sorted(os.listdir(ROOT) if os.path.isdir(ROOT) else [])
    if cmd == "build": build(dbs)
    elif cmd == "migrate": migrate(dbs)
    elif cmd == "replenish":
        cs = [tuple(int(v) for v in x.split(",")) for x in a if "," in x and x[0].isdigit()] or None
        for db in dbs: replenish(db, cs, int(opt("--per-cell", 4)))
    elif cmd == "status": status(dbs)
    elif cmd == "expand": expand(dbs, float(opt("--min-rate", 0.6)), int(opt("--min-n", 3)), int(opt("--per-cell", 8)))
