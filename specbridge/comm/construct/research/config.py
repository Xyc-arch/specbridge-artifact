"""P_D^theta: A NAMED, VERSIONED, EXECUTABLE CONFIGURATION OF P_D.
    python -m specbridge.comm.construct.research.config save <draft.json>                 -> configs/<db>/<name>@<version>.json
    python -m specbridge.comm.construct.research.config run <config.json> [--mode pool|fresh] [--review]
                                                                      -> out/runs/<name>@<version>/<mode>/tasks.jsonl, REPORT.md, run.json
    python -m specbridge.comm.construct.research.config show <config.json>
A CONFIGURATION (theta) is the user's choice over the profiled space of one database:
  target    joint depth weights {"cells": {"A,S": w}} | ranges | a preset | a mix of presets (a target, not a requirement)
  ops       operation preferences (relative weights; 0 = never): diff, ratio, baseline, share, rank, agg
  prefer    joins, grouping (relative weights, fresh generation)
  hard      requirements, never crossed: tables (only these), exclude_tables, ops_required, ops_forbidden, exclude_partial
  standard  benchmark | analyst | exploratory | strict (pool mode; fresh SQL carries its own review status)
  max_move  the largest depth deviation of a substituted task, per axis
  count, seed, mode ("pool": reviewed tasks from the pools | "fresh": new SQL from the grammar, data-checked)
SAVING binds it to what it was chosen against -- grammar version, catalogue version, rubric version -- and its VERSION is a
hash of all of it: the same name with any change is a new version. RUNNING checks the bindings (a configuration made for
another grammar or catalogue is refused: the space it was chosen over has changed) and executes:
  pool   selects reviewed tasks (specbridge.comm.construct.serve): no model calls; every task carries its rubric verdicts
  fresh  generates new SQL (specbridge.pd.structures.compose via specbridge.comm.construct.profile.deliver) toward the target under the hard
         constraints, with data checks; review status "pending review" -- unless the SQL was reviewed before (its verdict is
         reused) or --review runs the rubric now (model calls, reported)
Every run returns the SQL with its MEASURED structure, review status, requested vs delivered per cell with the reason for
every shortfall, and a fingerprint of the output: the same configuration run again gives the same fingerprint."""
import collections, hashlib, json, os, sys, time

ROOT, RUNS = "configs", "out/runs"
FIELDS = ("target", "ops", "prefer", "hard", "standard", "max_move", "max_share_per_quantity", "priority", "substitute")


def bindings(db):
    from specbridge.pd.structures.compose import VERSION as GV
    from specbridge.comm.construct.rubric import VERSION as RV
    from specbridge.comm.construct.pool import cat_version
    return {"grammar": GV, "catalogue": cat_version(db), "rubric": RV}


def canonical(c): return json.dumps({k: c[k] for k in ("db", "theta", "count", "seed", "mode", "bindings")}, sort_keys=True)


def save(draft):
    c = {"name": draft["name"], "db": draft["db"], "theta": {k: draft[k] for k in FIELDS if k in draft},
         "count": int(draft.get("count", 50)), "seed": int(draft.get("seed", 42)), "mode": draft.get("mode", "pool"), "bindings": bindings(draft["db"])}
    for k in ("target",):
        if k not in c["theta"]: raise ValueError("a configuration needs a target distribution")
    c["version"] = hashlib.sha256(canonical(c).encode()).hexdigest()[:12]; c["saved"] = time.strftime("%Y-%m-%d %H:%M")
    d = "%s/%s" % (ROOT, c["db"]); os.makedirs(d, exist_ok=True); f = "%s/%s@%s.json" % (d, c["name"], c["version"])
    json.dump(c, open(f, "w"), indent=1); print("saved %s" % f); return f


def load(f):
    c = json.load(open(f))
    if hashlib.sha256(canonical(c).encode()).hexdigest()[:12] != c["version"]: raise ValueError("%s was edited after saving: save it again for a new version" % f)
    return c


def entry_ops(construction):
    from specbridge.comm.construct.pool import ops_of
    return set(ops_of(construction))


def run(f, mode=None, review=False):
    c = load(f); mode = mode or c["mode"]; db = c["db"]; th = c["theta"]; t0 = time.time()
    now = bindings(db)
    stale = {k: (c["bindings"][k], now[k]) for k in ("grammar", "catalogue") if c["bindings"][k] != now[k]}
    if stale: raise SystemExit("refused: %s was chosen over a different space %s; open the profile and save it again" % (f, stale))
    intent = dict(th, db=db, count=c["count"], seed=c["seed"])
    if mode == "pool":
        from specbridge.comm.construct.serve import serve
        tasks, _fresh, res = serve(intent)
        from specbridge.comm.construct.serve import tables_read
        out = [{"id": t["id"], "db": db, "sql": t["sql"], "A": t["A"], "S": t["S"], "construction": t["construction"], "ops": t["ops"], "tables": tables_read(t["sql"]),
                "quantities": t["quantities"], "requested_cell": t["requested_cell"], "source": "pool",
                "review": {"status": status(t.get("quality")), "rubric": (t.get("quality") or {}).get("rubric"), "standard": th.get("standard", "benchmark"),
                           "partial": (t.get("quality") or {}).get("partial")}, "complexity": "not assessed", "spec": t["spec"]} for t in tasks]
        requested = res["demand"]; shortfall = {"no stock meeting the standard within the allowed moves": res["shortfall"],
                                                "the diversity cap": res["diversity_shortfall"]}
        moves = res["moves"]; note = res["explanation"]; calls = 0
    else:
        out, requested, shortfall, moves, note, calls = fresh(c, review)
    delivered = collections.Counter("%d,%d" % (x["A"], x["S"]) for x in out)
    fp = hashlib.sha256(json.dumps([[x["sql"], x["A"], x["S"], x["review"]["status"]] for x in out]).encode()).hexdigest()[:16]
    d = "%s/%s@%s/%s" % (RUNS, c["name"], c["version"], mode); os.makedirs(d, exist_ok=True)
    with open(d + "/tasks.jsonl", "w") as fh:
        for x in out: fh.write(json.dumps(x) + "\n")
    rj = {"config": f, "version": c["version"], "mode": mode, "requested": requested, "delivered": dict(delivered), "shortfall": shortfall,
          "moves": moves, "explanation": note, "fingerprint": fp, "seconds": round(time.time() - t0, 3), "model_calls": calls,
          "review": dict(collections.Counter(x["review"]["status"] for x in out)), "diversity": diversity(out)}
    json.dump(rj, open(d + "/run.json", "w"), indent=1)
    report(c, rj, out, d); return rj


def status(q):
    if not q: return "pending review"
    if q["meaning"] == "yes" and q["determined"] == "yes": return "benchmark pass"
    return {"uncertain": "uncertain meaning", "no": "fails meaning"}.get(q["meaning"], "answer not determined" if q["determined"] == "no" else q["meaning"])


def diversity(xs):
    return {"tasks": len(xs), "computations": len({(x["construction"], tuple(sorted(x["quantities"]))) for x in xs}),
            "quantities": len({q for x in xs for q in x["quantities"]}), "tables": len({t for x in xs for t in x["tables"]}),
            "constructions": len({x["construction"] for x in xs})}


def fresh(c, review):
    """New SQL toward the target, under the hard constraints, with data checks. Review status: reused when the same SQL was
    reviewed before (pools), else 'pending review', or the rubric now with --review."""
    from specbridge.pd.structures.compose import Space
    from specbridge.comm.construct.profile import deliver, skeleton
    from specbridge.comm.construct.pool import load as pload
    th = c["theta"]; db = c["db"]; h = th.get("hard") or {}; sp = Space(db); R = sp.reachable()
    from specbridge.comm.construct.serve import tables_read
    def accept(P):
        tabs = set(tables_read(P.sql())); ops = entry_ops(skeleton(P))
        if h.get("tables") and not tabs <= set(h["tables"]): return False
        if h.get("exclude_tables") and tabs & set(h["exclude_tables"]): return False
        if h.get("ops_required") and not ops & set(h["ops_required"]): return False
        if h.get("ops_forbidden") and ops & set(h["ops_forbidden"]): return False
        if any(float((th.get("ops") or {}).get(o, 1)) == 0 for o in ops): return False
        return True
    req = dict(th.get("target"), count=c["count"], seed=c["seed"], ops=th.get("ops"), prefer=th.get("prefer"))
    rows, rep, W = deliver(sp, req, set(R), checks=True, accept=accept)
    known = {e["sql"]: e.get("quality") for e in pload(db) if e.get("quality")}
    out = []
    for x in rows:
        from specbridge.comm.construct.serve import tables_read
        tabs = tables_read(x["sql"])
        out.append({"id": x["id"], "db": db, "sql": x["sql"], "A": x["A"], "S": x["S"], "construction": x["construction"], "ops": sorted(entry_ops(x["construction"])),
                    "tables": tabs, "quantities": x["quantities"], "source": "fresh", "why": x["why"],
                    "review": {"status": status(known.get(x["sql"])), "rubric": (known.get(x["sql"]) or {}).get("rubric"), "reused": x["sql"] in known},
                    "complexity": "not assessed"})
    calls = 0
    if review:
        from specbridge.comm.construct.rubric import judge, combine
        from specbridge.comm.construct.freeze import packaged, snapshot
        from specbridge.comm.common.llm import CALLS
        before = sum(CALLS.values()); todo = [x for x in out if x["review"]["status"] == "pending review"]
        items = []
        for x in todo:
            t, _w = packaged(x["id"], db, x["sql"], "fresh", level="spec")
            if t: items.append({"id": x["id"], "db": db, "sql": x["sql"], "spec": t["instruction"], "snapshot": snapshot(db)[0]})
        J = judge(items)
        for x in todo:
            q = combine(J.get(x["id"], {})); x["review"] = {"status": status(q), "rubric": q["rubric"], "reused": False, "partial": q["partial"]}
        calls = sum(CALLS.values()) - before
    requested = {"%d,%d" % k: r["requested"] for k, r in rep.items() if r["requested"]}
    shortfall = {"%d,%d" % k: "%d: %s" % (r["requested"] - r["delivered"], r.get("shortfall")) for k, r in rep.items() if r.get("shortfall")}
    note = "Generated fresh toward the target under the hard constraints; data-checked; %s." % ("reviewed now with the rubric" if review else "review status reused where the same SQL was reviewed before, otherwise PENDING REVIEW")
    return out, requested, shortfall, {}, note, calls


def report(c, rj, out, d):
    L = ["# P_D^theta run: `%s` @ %s (%s mode)\n" % (c["name"], c["version"], rj["mode"]),
         "Database `%s`; grammar %s, catalogue %s, rubric %s. Count %d, seed %d.\n" % (c["db"], c["bindings"]["grammar"], c["bindings"]["catalogue"], c["bindings"]["rubric"], c["count"], c["seed"]),
         "theta: `%s`\n" % json.dumps(c["theta"]),
         rj["explanation"], "",
         "Delivered %d of %d in %.2fs, %d model calls. Fingerprint **%s** (the same configuration gives the same fingerprint).\n" % (
             len(out), sum(rj["requested"].values()), rj["seconds"], rj["model_calls"], rj["fingerprint"]),
         "Review status: %s. Complexity integrity: not assessed.\n" % rj["review"],
         "Diversity: %(computations)d computations, %(quantities)d base quantities, %(tables)d tables, %(constructions)d constructions.\n" % rj["diversity"],
         "| A,S | requested | delivered |", "|---|---|---|"]
    cells = sorted(set(rj["requested"]) | set(rj["delivered"]), key=lambda k: tuple(map(int, k.split(","))))
    for k in cells: L.append("| %s | %d | %d |" % (k, rj["requested"].get(k, 0), rj["delivered"].get(k, 0)))
    if rj["moves"]: L.append("\nMoves to nearby cells: %s" % rj["moves"])
    sf = {k: v for k, v in rj["shortfall"].items() if v}
    if sf: L.append("\nShortfalls: %s" % sf)
    L.append("\n## The tasks\n")
    for x in out:
        L += ["- A%d S%d `%s` [%s] tables %s" % (x["A"], x["S"], x["construction"], x["review"]["status"], ", ".join(x["tables"])), "  - `%s`" % x["sql"][:300]]
    open(d + "/REPORT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:14 + len(cells)]))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "save": save(json.load(open(a[1])))
    elif a[0] == "show": print(json.dumps(load(a[1]), indent=1))
    elif a[0] == "run": run(a[1], a[a.index("--mode") + 1] if "--mode" in a else None, "--review" in a)
