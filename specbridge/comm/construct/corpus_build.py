"""BUILD A VERSIONED CORPUS FROM A SAVED REQUEST (the explorer's "Build a corpus" section, or a JSON file).
    python -m specbridge.comm.construct.corpus_build <request.json> [--rounds 3]   -> out/corpora/<name>@<version>/{tasks.jsonl, REPORT.md, report.json}
    python -m specbridge.comm.construct.corpus_build <request.json> --base <corpus dir> --drop <ids.json>   a top-up: replace only the dropped tasks
REQUEST: {name, count, seed, databases: {db: weight}, target: {cells: {"A,S": w}} | {preset}, standard, max_move, ops, prefer}
  prefer   {"joins": w, "grouping": w}: multi-table and grouped constructions weighted up (w > 1) or down (w < 1)
  targets  {db: target}: a database's own depth choice, overriding the common `target` for that database
  counts   {db: n}: exact numbers of tasks per database (then count = their sum), instead of shares by weight
  variety  off | less | normal (default) | more | most: how strongly a table, first level or construction shape already used is
           discounted when the next program is drawn (specbridge.pd.structures.compose; at construction, never by filtering)
STEPS, cheapest first, so nothing costly is spent on a task that will not be kept (grammar: specbridge.pd.structures.compose VERSION; rubric v1.1):
  1 plan     tasks per database by weight (largest remainder); per database, the target cells it can build; a cell it
             cannot build moves to the nearest buildable cell within max_move, else it is a shortfall ("not constructible")
  2 generate fresh SQL toward each planned cell, WITHOUT REPLACEMENT (specbridge.pd.structures.compose: no duplicate is ever drawn;
             operations weighted 0 are never offered), with the data checks -- which execute the answer, so an answer with
             no rows or over 2,000 is dropped here, before any review
  3 light    the instructions only (explicit V; specbridge.comm.construct.freeze.packaged level "spec", cached): what a reviewer needs
  4 review   the benchmark rubric (coherent meaning, determined answer; opus and sonnet each judging alone, both must agree),
             reusing any earlier verdict on the same SQL
  5 package  explicit instructions, full reference answer with tie groups, grader, snapshot hash (specbridge.comm.construct.freeze)
             ONLY for the tasks kept, in parallel processes
ROUNDS: each round asks only for what is still missing, divided by the pass rate MEASURED so far in this build (the
database's earlier history, else an optimistic 0.9, as the starting point), so the build reviews a little more than it
keeps instead of a fixed multiple. Up to `rounds` rounds, or until a cell is exhausted.
  5 report   requested vs delivered (cells, databases, operations), diversity, review outcomes, cost, every shortfall's reason
Every task carries its provenance: corpus version, request hash, database, grammar / catalogue / rubric versions, seed and
round, construction, base quantities, measured depth, both reviewers' verdicts, complexity integrity: no recomputed aggregate (proven on the SQL); other redundancy not assessed."""
from specbridge.pd.structures.compose import VERSION as GRAMMAR
import collections, concurrent.futures as cf, hashlib, json, math, os, random, sys, time

OUT = "out/corpora"


def version_of(req, binds):
    return hashlib.sha256(json.dumps({"request": req, "bindings": binds}, sort_keys=True).encode()).hexdigest()[:12]


def setup(db):
    """A database chosen before it was set up: its catalogue is built now (one model review; specbridge.pd.realize.semantic). It has no
    reviewed history, so its pass rate is unknown and its first build oversamples at a default rate (reported)."""
    from specbridge.pd.realize.semantic import build, path
    if not os.path.exists(path(db)): build(db); return True
    return False


def plan(req):
    from specbridge.comm.construct.serve import weights, quotas, solve
    from specbridge.pd.structures.compose import Space
    if req.get("counts"):
        per = {d: int(k) for d, k in req["counts"].items() if int(k) > 0}
    else:
        n = int(req["count"]); dbw = {d: float(w) for d, w in req["databases"].items() if float(w) > 0}
        tot = sum(dbw.values()); raw = {d: n * w / tot for d, w in dbw.items()}; per = {d: int(math.floor(v)) for d, v in raw.items()}
        for d in sorted(raw, key=lambda d: (-(raw[d] - per[d]), d))[: n - sum(per.values())]: per[d] += 1
    mm = req.get("max_move") or {"arith": 1, "steps": 1}
    out = {}
    for db, k in per.items():
        if not k: continue
        W = weights((req.get("targets") or {}).get(db) or req.get("target") or {"preset": "medium"})
        R = Space(db, extra=req.get("extra") or ()).reachable(); demand = quotas(W, k)
        moves, short = solve(demand, {c: 10 ** 6 for c in R}, 1.0, 1.0, True, mm)
        out[db] = {"quota": k, "demand": demand, "moves": moves, "short": short, "reach": set(R)}
    return per, out


def _freeze(a):
    from specbridge.comm.construct.freeze import freeze
    tid, db, sql = a
    return freeze(tid, db, sql, "corpus")


def run(req, rounds=6, base=None, drop=()):
    """base, drop: a TOP-UP of an existing corpus -- every task of `base` not in `drop` is kept verbatim (id, review, package,
    provenance); new tasks are drawn only for the dropped tasks' cells, with a different seed, and never repeat a base program."""
    B = [json.loads(l) for l in open(base + "/tasks.jsonl")] if base else []
    if base: req = dict(req, topup_of=base.rstrip("/").split("/")[-1], replaced=sorted(drop))
    from specbridge.pd.structures.compose import Space, VERSION as GV
    from specbridge.comm.construct.profile import deliver, skeleton, sampler_for
    from specbridge.comm.construct.freeze import packaged
    from specbridge.comm.construct.rubric import judge, combine, VERSION as RV
    from specbridge.comm.construct.pool import load as pload, cat_version, ops_of
    from specbridge.comm.construct.serve import STANDARDS, tables_read
    from specbridge.comm.common.llm import CALLS
    T0 = time.time(); calls0 = sum(CALLS.values())
    fresh_setup = {db: setup(db) for db in req["databases"] if float(req["databases"][db]) > 0}   # a new database: catalogue first
    binds = {db: {"grammar": GV, "catalogue": cat_version(db), "rubric": RV} for db in req["databases"] if float(req["databases"][db]) > 0}
    ver = version_of(req, binds); name = "%s@%s" % (req.get("name", "corpus"), ver); d = "%s/%s" % (OUT, name); os.makedirs(d, exist_ok=True)
    ok = STANDARDS[req.get("standard", "benchmark")]; zero = {o for o, w in (req.get("ops") or {}).items() if float(w) == 0}
    per, P = plan(req); tasks = []; funnel = collections.Counter(); shortfall = collections.defaultdict(dict); cost = {}
    for db, p in P.items():
        sp = Space(db, extra=req.get("extra") or ()); t0 = time.time()     # extra: opt-in rules (compose EXTRA_VERSION)
        known = {e["sql"]: e.get("quality") for e in pload(db) if e.get("quality")}
        pf = "out/pool/%s/profile.json" % db
        prof = json.load(open(pf))["cells"] if os.path.exists(pf) else {}
        hist = (sum(c.get("benchmark_pass") or 0 for c in prof.values()), sum(c.get("assessed") or 0 for c in prof.values()))
        passed, reviewed = (hist[0], hist[1]) if hist[1] else (9, 10)       # no history: an optimistic 0.9 to start, replaced by what is measured
        need = collections.Counter()
        for (i, j), f in p["moves"].items(): need[j] += f
        kept_base = [t for t in B if t["database"] == db and t["id"] not in drop]
        for t in kept_base: need[(t["A"], t["S"])] -= 1
        need = collections.Counter({c: k for c, k in need.items() if k > 0})
        base_sql = {t["reference_sql"] for t in B if t["database"] == db}
        tasks += kept_base; funnel[(db, "kept from the base corpus")] += len(kept_base)
        for i, s_ in p["short"].items(): shortfall[db]["%d,%d" % i] = "%d not constructible within the allowed moves" % s_
        got = collections.defaultdict(list); seen = set(); exhausted = set()
        smp = sampler_for(sp, dict(req, seed=int(req.get("seed", 2026)) + (1 if base else 0)))   # ONE sampler across rounds: no round redraws a program
        accept = lambda Pr: not (zero & set(ops_of(skeleton(Pr))))
        for rnd in range(rounds):
            missing = {c: need[c] - len(got[c]) for c in need if len(got[c]) < need[c] and c not in exhausted}
            if not missing: break
            rate = max(0.2, passed / max(1, reviewed))
            ask = {"%d,%d" % c: min(3 * k, max(k, math.ceil(k / rate * 1.1))) for c, k in missing.items()}
            rows, rep, _w = deliver(sp, {"cells": ask, "count": sum(ask.values()), "seed": int(req.get("seed", 2026)), "ops": req.get("ops"), "prefer": req.get("prefer"),
                                         "variety": req.get("variety", "normal")},
                                    p["reach"], True, accept, sampler=smp, max_rows=2000)
            for c, r in rep.items():
                if r.get("exhausted"): exhausted.add(c)
                for why, n in (r.get("fail") or {}).items(): funnel[(db, "dropped before review: " + why)] += n
            assert not ({x["sql"] for x in rows} & seen), "a round redrew a program"      # impossible by construction
            if base_sql:                                 # a top-up's own sampler may meet a base program: it is not drawn again
                funnel[(db, "already in the base corpus")] += sum(x["sql"] in base_sql for x in rows); rows = [x for x in rows if x["sql"] not in base_sql]
            seen |= {x["sql"] for x in rows}; funnel[(db, "generated")] += len(rows)
            # 3 light package (instructions only) and 4 review -- never the full answer before a task is kept
            items = []
            for x in rows:
                if x["sql"] in known: continue
                t, why = packaged(x["id"], db, x["sql"], "corpus", level="spec")
                if t: items.append({"id": x["id"], "db": db, "sql": x["sql"], "spec": t["instruction"], "snapshot": t["snapshot"]})
                else: funnel[(db, "not in the language")] += 1
            J = judge(items); funnel[(db, "reviewed now")] += len(items); funnel[(db, "review reused")] += sum(x["sql"] in known for x in rows)
            keep = []
            for x in rows:
                q = known.get(x["sql"]) or (combine(J[x["id"]]) if x["id"] in J else None)
                if not q: continue
                passed += ok({"quality": q}); reviewed += 1
                if not ok({"quality": q}): funnel[(db, "failed the standard")] += 1; continue
                c = (x["A"], x["S"])
                if len(got[c]) + sum(1 for y, _q in keep if (y["A"], y["S"]) == c) >= need.get(c, 0): funnel[(db, "passed, not needed")] += 1; continue
                keep.append((x, q))
            # 5 full packaging, only for the tasks kept, in parallel processes
            with cf.ProcessPoolExecutor(max_workers=6) as ex:
                full = list(ex.map(_freeze, [(x["id"], db, x["sql"]) for x, _q in keep]))
            for (x, q), (t, why) in zip(keep, full):
                if not t: funnel[(db, "packaging refused")] += 1; continue
                got[(x["A"], x["S"])].append((x, t, q, rnd))
        for c, k in need.items():
            if len(got[c]) < k:
                shortfall[db]["%d,%d" % c] = ("%d short: the cell is exhausted (every distinct program was drawn)" % (k - len(got[c])) if c in exhausted else
                                              "%d short after %d rounds (not enough generated SQL passed the %s standard)" % (k - len(got[c]), rounds, req.get("standard", "benchmark")))
        for c, xs in got.items():
            for x, t, q, rnd in xs:
                tasks.append(dict(t, id="%s-%s" % (name, hashlib.sha1(x["sql"].encode()).hexdigest()[:10]), A=x["A"], S=x["S"], built_for=x.get("built_for"),
                                  depth_agrees=(x.get("built_for") == "%d,%d" % (x["A"], x["S"])) if x.get("built_for") else None,
                                  construction=x["construction"], operations=ops_of(x["construction"]), tables_read=tables_read(x["sql"]), quantities=x["quantities"],
                                  review={"standard": req.get("standard", "benchmark"), "rubric": q.get("rubric"), "meaning": q["meaning"], "determined": q["determined"],
                                          "partial": q.get("partial"), "reviewers": q.get("reasons")},
                                  complexity={"recomputed_aggregate": False, "by": "specbridge.pd.structures.integrity, read off the SQL (the grammar never builds one; the data checks refuse one)",
                                              "other redundancy": "not assessed"},
                                  provenance={"corpus": name, "request": ver, "database": db, **binds[db], "seed": int(req.get("seed", 2026)), "round": rnd,
                                              "why_built": x["why"], "built": time.strftime("%Y-%m-%d %H:%M")},
                                  **({"planted": x["planted"]} if x.get("planted") else {})))
        cost[db] = round(time.time() - t0, 1)
    with open(d + "/tasks.jsonl", "w") as f:
        for t in tasks: f.write(json.dumps(t, default=str) + "\n")
    for db, new in fresh_setup.items():
        if new: shortfall.setdefault(db, {})["setup"] = "set up during this build (catalogue built now; no reviewed history, so oversampling used a default pass rate)"
    rep = report(req, name, per, P, tasks, funnel, shortfall, cost, time.time() - T0, sum(CALLS.values()) - calls0, d)
    json.dump({"request": req, "bindings": binds, **rep}, open(d + "/report.json", "w"), indent=1, default=str)
    return name, rep


def report(req, name, per, P, tasks, funnel, shortfall, cost, secs, calls, d):
    got = collections.Counter("%d,%d" % (t["A"], t["S"]) for t in tasks)
    reqc = collections.Counter()
    for db, p in P.items():
        for c, k in p["demand"].items(): reqc["%d,%d" % c] += k
    div = {"tasks": len(tasks), "computations": len({(t["database"], t["construction"], tuple(sorted(t["quantities"]))) for t in tasks}),
           "quantities": len({(t["database"], q) for t in tasks for q in t["quantities"]}), "tables": len({(t["database"], x) for t in tasks for x in t["tables_read"]}),
           "constructions": len({(t["database"], t["construction"]) for t in tasks})}
    ops = collections.Counter(o for t in tasks for o in t["operations"])
    L = ["# Corpus `%s`\n" % name, "Request: `%s`\n" % json.dumps(req), "Grammar %s, rubric v1.1, standard **%s**. Complexity integrity: no task recomputes an existing aggregate (proven on the SQL); other redundancy not assessed.\n" % (GRAMMAR, req.get("standard", "benchmark")),
         "**%d of %d tasks delivered** in %.0f s with %d model calls (%.1f s and %.1f calls per delivered task).\n" % (len(tasks), req["count"], secs, calls, secs / max(1, len(tasks)), calls / max(1, len(tasks))),
         "## By database\n", "| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |", "|---|---|---|---|---|---|---|---|---|---|"]
    for db in per:
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %s |" % (db, per[db], sum(t["database"] == db for t in tasks), funnel[(db, "generated")], funnel[(db, "reviewed now")],
                 funnel[(db, "review reused")], funnel[(db, "failed the standard")], funnel[(db, "passed, not needed")], funnel[(db, "packaging refused")], cost.get(db, "-")))
    drop = {k[1]: v for k, v in funnel.items() if k[1].startswith("dropped before review")}
    if drop: L.append("\nDropped before review (no model calls spent): %s" % drop)
    L += ["\n## Requested vs delivered by depth cell (all databases)\n", "| A,S | requested | delivered |", "|---|---|---|"]
    for k in sorted(set(reqc) | set(got), key=lambda k: tuple(map(int, k.split(",")))): L.append("| %s | %d | %d |" % (k, reqc.get(k, 0), got.get(k, 0)))
    shp = collections.Counter(" > ".join(p.split(":")[0] for p in t["construction"].split(" > ")) for t in tasks)
    L += ["\nOperations used: %s" % dict(ops.most_common()), "\nDiversity: %(computations)d distinct computations, %(quantities)d base quantities, %(tables)d tables, %(constructions)d constructions." % div,
          "\nVariety (%s): %d construction shapes; the largest is %d%% of the corpus (%s)." % (req.get("variety", "normal"), len(shp), 100 * shp.most_common(1)[0][1] // max(1, len(tasks)), shp.most_common(1)[0][0]) if tasks else ""]
    sf = {db: v for db, v in shortfall.items() if v}
    L.append("\n## Shortfalls\n" + ("\n".join("- **%s**: %s" % (db, "; ".join("%s: %s" % kv for kv in v.items())) for db, v in sf.items()) if sf else "\nNone."))
    L.append("\n## A random sample of delivered tasks\n")
    for t in random.Random(1).sample(tasks, min(8, len(tasks))):
        L += ["- **%s** A%d S%d `%s`" % (t["database"], t["A"], t["S"], t["construction"]), "  - %s" % t["instruction"].split("\nConventions")[0][:500].replace("\n", " / ")]
    open(d + "/REPORT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:14 + len(per)]))
    return {"delivered": len(tasks), "requested_cells": dict(reqc), "delivered_cells": dict(got), "diversity": div, "operations": dict(ops),
            "shortfall": sf, "seconds": round(secs), "model_calls": calls, "funnel": {"%s|%s" % k: v for k, v in funnel.items()}}


if __name__ == "__main__":
    a = sys.argv[1:]; r = json.load(open(a[0])); r = r.get("request", r)
    drop = json.load(open(a[a.index("--drop") + 1])) if "--drop" in a else ()
    run(r, int(a[a.index("--rounds") + 1]) if "--rounds" in a else 6, a[a.index("--base") + 1] if "--base" in a else None, set(drop))
