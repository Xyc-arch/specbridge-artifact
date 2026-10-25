"""THE DISTRIBUTION PROFILE OF P_D, AND SAMPLING FROM A CHOSEN DISTRIBUTION OVER IT.
    python -m specbridge.comm.construct.profile <db> [--probes 6] [--no-checks]                          profile only
    python -m specbridge.comm.construct.profile <db> --request req.json                                    profile + sample a request
    python -m specbridge.comm.construct.profile <db> --arith 0-1 --steps 3-4 --count 100 --seed 42         the same, from flags
    python -m specbridge.comm.construct.profile <db> --preset medium --count 50
  -> out/profile/<db>/PROFILE.md, profile.json, delivered.jsonl

FIVE LAYERS, never merged (docs/COMPOSE.md):
  1 database support    quantities by type, grouping levels, entities, catalogue relations, catalogue uncertainties
  2 grammar-reachable   the (arithmetic depth x step depth) cells the typed grammar can construct on this catalogue within
                        the bounds: EXACT (specbridge.pd.structures.compose.reach, over types). Per cell: tables and start routes (exact);
                        distinct programs, quantities and constructions among `probes` draws (SAMPLED, a lower bound)
  3 data-valid          share of the probes that pass the data checks (compose.check): an ESTIMATE from the probes
  4 filtered            the sensibility veto and the audit: only at milestones (specbridge.comm.construct.research.pipeline / filtered), not here
  5 requested/delivered what the request asked per cell, what was delivered, and why any cell fell short:
                        "not constructible" (proven by reach) | "all attempts failed the data checks" | "attempt budget ended"
A REQUEST is a distribution over the reachable space: joint cell weights (or ranges / presets / a mix of presets), operation
preferences, joins and grouping preferences, table weights, a repetition penalty, count and seed. There is no finite list of
distributions; the profile shows the support and the request chooses weights on it."""
import collections, json, math, os, random, sys, time
from specbridge.pd.structures.compose import Space, Sampler, check_many, BATCH, A_MAX, S_MAX, VERSION
from specbridge.pd.structures.depth import of_sql

PRESETS = {"shallow": {"arith": [0, 1], "steps": [1, 2]}, "medium": {"arith": [1, 2], "steps": [2, 4]},
           "deep": {"arith": [2, 3], "steps": [4, 6]}, "very deep": {"arith": [3, A_MAX], "steps": [6, S_MAX]}}


def support(sp):
    S = sp.S; out = {"record_tables": {}, "relations": S.cat.get("relations", []), "composite_fk": S.composite, "uncertain": []}
    for t in sp.rec:
        cls = collections.Counter((q["unit"], {True: "flow", False: "stock"}.get(q["kind"], "?"), "summable" if q["additive"] else "averaged", q["depth"]) for q in sp.qs[t])
        out["record_tables"][t] = {"quantities": len(sp.qs[t]), "classes": [list(k) + [n] for k, n in sorted(cls.items(), key=str)],
                                   "levels": [_lv(L) for L in sp.levels[t]]}
    for k, m in S.col.items():
        low = [f for f, c in (m.get("confidence") or {}).items() if c == "low"]
        if low or m.get("semantic_role") == "unknown": out["uncertain"].append({"column": k, "role": m.get("semantic_role"), "low_confidence": low})
    return out


def _lv(L):
    if L[0] == "e": return "per %s (by %s)" % (L[2], L[1])
    if L[0] == "eg": return "per %s within %s.%s" % (L[2], L[4], L[5])
    if L[0] == "g": return "per %s.%s" % (L[1], L[2])
    return "overall"


def skeleton(P): return " > ".join(str(x[0]) + ("" if x[0] in ("diff", "ratio", "rank") else ":" + str(x[1])) for x in P.trace)


def space(sp, probes, checks, seed=0):
    R = sp.reachable(); rng = random.Random(seed); smp = Sampler(sp, rng); cells = {}
    for c in sorted(R):
        progs = {}
        for _ in range(probes):
            P = smp.draw(c)
            if P is not None: progs.setdefault(P.sql(), P)
        cells[c] = {"progs": progs}
    todo = [(c, P) for c in cells for P in cells[c]["progs"].values()]
    res = dict(zip([id(P) for _c, P in todo], check_many(sp, [P for _c, P in todo]))) if checks else {}
    for c in sorted(R):
        progs = cells[c].pop("progs"); ok = collections.Counter(); why = collections.Counter()
        for P in progs.values():
            if checks:
                r, w = res[id(P)]; ok[r] += 1
                if not r: why[w] += 1
        good = [P for P in progs.values() if not checks or res[id(P)][0]]
        cells[c] = {"reachable": True, "tables": sorted(R[c]["tables"]), "routes": R[c]["routes"],
                    "examples": [{"construction": skeleton(P), "quantities": sorted("%s.%s" % x for x in P.base), "why": P.why, "sql": P.sql()} for P in good[:2]],
                    "probe_distinct": len(progs), "probe_quantities": len({b for P in progs.values() for b in P.base}),
                    "probe_constructions": len({skeleton(P) for P in progs.values()}),
                    "valid": ok[True], "checked": sum(ok.values()), "fail": dict(why)}
    return cells


def parse_request(a):
    """A request from a JSON file or flags."""
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    req = json.load(open(opt("--request"))) if opt("--request") else {}
    if isinstance(req.get("target"), dict): req = dict(req, **req["target"])      # the same intent file the server reads
    rng = lambda s: [int(x) for x in s.split("-")] if "-" in s else [int(s), int(s)]
    if opt("--arith"): req["arith"] = rng(opt("--arith"))
    if opt("--steps"): req["steps"] = rng(opt("--steps"))
    if opt("--preset"): req["preset"] = opt("--preset")
    if opt("--count"): req["count"] = int(opt("--count"))
    if opt("--seed"): req["seed"] = int(opt("--seed"))
    return req if (req.get("cells") or req.get("arith") or req.get("steps") or req.get("preset") or req.get("mix")) else None


def weights(req):
    """{cell: weight} over the whole grid (reachable or not) from cells | ranges | preset | mix of presets."""
    W = collections.Counter()
    def rng(r, w):
        a, s = r.get("arith", [0, A_MAX]), r.get("steps", [1, S_MAX])
        cs = [(x, y) for x in range(a[0], a[1] + 1) for y in range(s[0], s[1] + 1)]
        for c in cs: W[c] += w / len(cs)
    if req.get("cells"):
        for k, w in req["cells"].items(): W[tuple(int(x) for x in k.split(","))] += float(w)
    elif req.get("mix"):
        for m in req["mix"]: rng(PRESETS[m["preset"]] if "preset" in m else m, float(m.get("weight", 1)))
    else: rng(PRESETS[req["preset"]] if req.get("preset") else req, 1.0)
    tot = sum(W.values()); return {c: w / tot for c, w in W.items() if w > 0}


def sampler_for(sp, req):
    """The sampler a request implies: its seed and its preferences (operations, structure, tables, repetition)."""
    prefs = dict(("op:" + k, v) for k, v in (req.get("ops") or {}).items())
    prefs.update(dict((k, v) for k, v in (req.get("prefer") or {}).items()))
    prefs.update(dict(("table:" + k, v) for k, v in (req.get("tables") or {}).items()))
    if "repeat_penalty" in req: prefs["repeat_penalty"] = req["repeat_penalty"]
    if req.get("variety") is not None: prefs["variety"] = VARIETY.get(req["variety"], req["variety"])
    return Sampler(sp, random.Random(int(req.get("seed", 42))), prefs)


# the user's Variety setting -> the discount per earlier use of a table, a first level, or a construction-shape prefix
VARIETY = {"off": 1.0, "less": 0.8, "normal": 0.6, "more": 0.4, "most": 0.25}


def deliver(sp, req, reach, checks=True, accept=None, sampler=None, max_rows=None):
    """Sample the request: quotas per cell (largest remainder), draws toward each cell, distinct SQL, data checks."""
    n = int(req.get("count", 50)); seed = int(req.get("seed", 42)); W = weights(req)
    prefs = dict(("op:" + k, v) for k, v in (req.get("ops") or {}).items())
    prefs.update(dict((k, v) for k, v in (req.get("prefer") or {}).items()))
    prefs.update(dict(("table:" + k, v) for k, v in (req.get("tables") or {}).items()))
    if "repeat_penalty" in req: prefs["repeat_penalty"] = req["repeat_penalty"]
    raw = {c: W[c] * n for c in W}; quota = {c: int(math.floor(v)) for c, v in raw.items()}
    for c in sorted(raw, key=lambda c: -(raw[c] - quota[c]))[: n - sum(quota.values())]: quota[c] += 1
    smp = sampler or sampler_for(sp, req); out, report = [], {}; seen = set(); tries = int(req.get("max_attempts_per_task", 20))
    for c in sorted(quota):
        q = quota[c]; r = {"weight": W[c], "requested": q, "delivered": 0, "attempts": 0, "duplicates": 0, "fail": collections.Counter()}
        report[c] = r
        if not q: continue
        if c not in reach: r["shortfall"] = "not constructible (no route under this grammar, catalogue and bounds)"; continue
        need = frozenset(req.get("require") or ())
        if need and not sp.feasible(c, need):
            r["shortfall"] = "not constructible with the required operations %s (no route under this grammar uses them in this cell)" % sorted(need); continue
        while r["delivered"] < q and r["attempts"] < q * tries and not r.get("exhausted"):
            batch = []
            while len(batch) < BATCH and r["attempts"] < q * tries:      # a fixed batch of fresh draws, then checks
                r["attempts"] += 1; P = smp.draw(c, frozenset(req.get("require") or ()))   # required operations: every program uses them
                if P is None: r["exhausted"] = True; break          # every program of the cell has been drawn
                sql = P.sql()
                if sql in seen: raise AssertionError("the sampler drew a program twice: %s" % sql[:200])   # impossible by construction
                seen.add(sql)
                if accept and not accept(P): r["fail"]["outside the hard constraints"] += 1; continue
                batch.append(P)
            results = check_many(sp, batch) if checks else [(True, "")] * len(batch)
            for P, (ok, why) in zip(batch, results):                    # consumed in draw order: deterministic
                if r["delivered"] >= q: break
                if not ok: r["fail"][why] += 1; continue
                rows = int(why.split()[0]) if checks and why.split() and why.split()[0].isdigit() else None
                if max_rows and rows is not None and rows > max_rows: r["fail"]["answer over %d rows" % max_rows] += 1; continue   # before any review
                sql = P.sql(); m = of_sql(sql, sp.S.con)
                out.append({"id": "%s-%s" % (sp.db, __import__("hashlib").sha1(sql.encode()).hexdigest()[:10]), "database": sp.db, "sql": sql, "A": m["arith"], "S": m["steps"],
                            "built_for": "%d,%d" % c,      # the cell the construction's bookkeeping reached; A, S are MEASURED on the SQL
                            "construction": skeleton(P), "quantities": sorted("%s.%s" % b for b in P.base), "why": P.why, "grammar": VERSION, "answer_rows": rows,
                            "route": {"first_level": P.level[0] if getattr(P, "level", None) else "row",                  # the route taken (2026-10-04)
                                      "multi_table": bool(getattr(P, "level", None) and (P.level[0] == "eg" or (P.level[0] == "g" and P.level[-1])))},
                            **({"planted": P.planted} if getattr(P, "planted", None) else {})})       # FILTER: the condition and the other reading
                r["delivered"] += 1
        if r["delivered"] < q and r.get("exhausted"):
            r["shortfall"] = "cell exhausted: all %d distinct programs of the cell were drawn%s" % (len([1 for x in out if (x["A"], x["S"]) == c]) + sum(r["fail"].values()),
                                                                                                   " (%s)" % dict(r["fail"]) if r["fail"] else "")
        elif r["delivered"] < q:
            r["shortfall"] = ("all %d attempts failed the data checks" % r["attempts"] if not r["delivered"] and r["fail"] and not r["duplicates"] else
                              "attempt budget ended (%d attempts: %d duplicates, %d failed checks)" % (r["attempts"], r["duplicates"], sum(r["fail"].values())))
    return out, report, W


def grid(title, cells, fmt):
    L = ["### %s\n" % title, "| A \\ S | " + " | ".join(str(s) for s in range(1, S_MAX + 1)) + " |", "|---|" + "---|" * S_MAX]
    for a in range(0, A_MAX + 1):
        L.append("| **%d** | " % a + " | ".join(fmt(cells.get((a, s))) for s in range(1, S_MAX + 1)) + " |")
    return L


def run(db, probes=6, checks=True, req=None):
    t0 = time.time(); sp = Space(db); sup = support(sp); cells = space(sp, probes, checks); t1 = time.time()
    L = ["# Distribution profile of P_D on `%s`\n" % db,
         "Space: grammar `%s`, catalogue `%s`, bounds A <= %d, S <= %d, at most 3 measures per stage. Reachability is EXACT under these; "
         "per-cell program, quantity and construction counts are SAMPLED lower bounds from %d probes per cell; data-valid shares are ESTIMATES from those probes. "
         "Depth is measured on the emitted SQL (specbridge.pd.structures.depth). Built in %.1fs.\n" % (VERSION, sp.S.cat.get("version"), A_MAX, S_MAX, probes, t1 - t0),
         "## 1. Database support\n"]
    for t, r in sup["record_tables"].items():
        L.append("- **%s**: %d row quantities; grouping levels: %s" % (t, r["quantities"], "; ".join(r["levels"])))
        L.append("  - classes (unit, kind, aggregation, depth, n): " + "; ".join("%s" % c for c in r["classes"][:12]) + (" ..." if len(r["classes"]) > 12 else ""))
    L.append("- relations in the catalogue: %d; composite foreign keys left out: %s" % (len(sup["relations"]), sup["composite_fk"] or "none"))
    L.append("- catalogue uncertainties (low-confidence fields or unknown role): %d columns%s" % (len(sup["uncertain"]), (": " + ", ".join(u["column"] for u in sup["uncertain"][:15])) if sup["uncertain"] else ""))
    L += ["\n## 2. Grammar-reachable space (arithmetic depth A x step depth S)\n"]
    L += grid("reachable: tables (exact) / distinct programs in %d probes (sampled)" % probes, cells, lambda c: "%d / %d" % (len(c["tables"]), c["probe_distinct"]) if c else "--")
    L += [""] + grid("diversity in the probes: distinct quantities / constructions (sampled)", cells, lambda c: "%d / %d" % (c["probe_quantities"], c["probe_constructions"]) if c else "--")
    if checks:
        L += ["\n## 3. Data-valid (estimate from the probes)\n"] + grid("passed / checked", cells, lambda c: "%d/%d" % (c["valid"], c["checked"]) if c else "--")
        fails = collections.Counter()
        for c in cells.values(): fails.update(c["fail"])
        L.append("\nCheck failures in the probes: %s" % (dict(fails) or "none"))
    L.append("\n## 4. Filtered\n\nNot run here (model review only at milestones: `specbridge.comm.construct.research.pipeline`, `specbridge.comm.construct.research.filtered`).")
    res = {"db": db, "grammar": VERSION, "bounds": {"A": A_MAX, "S": S_MAX}, "support": sup, "cells": {"%d,%d" % c: v for c, v in cells.items()}, "probes": probes}
    if req:
        t2 = time.time(); out, rep, W = deliver(sp, req, {c for c in cells}, checks)
        L += ["\n## 5. Requested and delivered\n", "Request: `%s`. %d delivered of %d requested in %.1fs.\n" % (json.dumps(req), len(out), sum(r["requested"] for r in rep.values()), time.time() - t2)]
        L += ["| A | S | weight | requested | delivered | attempts | why short |", "|---|---|---|---|---|---|---|"]
        for c, r in sorted(rep.items()):
            if r["requested"]: L.append("| %d | %d | %.2f | %d | %d | %d | %s |" % (c[0], c[1], r["weight"], r["requested"], r["delivered"], r["attempts"], r.get("shortfall", "")))
        got = collections.Counter((x["A"], x["S"]) for x in out)
        L += [""] + grid("delivered (measured on the SQL)", {c: n for c, n in got.items()}, lambda n: str(n) if n else ".")
        q = collections.Counter(b for x in out for b in x["quantities"]); k = collections.Counter(x["construction"] for x in out)
        L.append("\nDelivered diversity: %d quantities (top share %s), %d constructions (top share %s), %d tables." % (
            len(q), "%d/%d" % (q.most_common(1)[0][1], len(out)) if q else "-", len(k), "%d/%d" % (k.most_common(1)[0][1], len(out)) if k else "-",
            len({b.split(".")[0] for b in q})))
        L.append("\n### A random sample of the delivered SQL\n")
        for x in random.Random(1).sample(out, min(5, len(out))):
            L += ["- A%d S%d `%s`: %s" % (x["A"], x["S"], x["construction"], " | ".join(x["why"][-3:])), "  - `%s`" % x["sql"][:400]]
        res["request"] = req; res["delivered"] = {"%d,%d" % c: {k: (dict(v) if isinstance(v, collections.Counter) else v) for k, v in r.items()} for c, r in rep.items()}
        os.makedirs("out/profile/%s" % db, exist_ok=True)
        with open("out/profile/%s/delivered.jsonl" % db, "w") as f:
            for x in out: f.write(json.dumps(x) + "\n")
    os.makedirs("out/profile/%s" % db, exist_ok=True)
    json.dump(res, open("out/profile/%s/profile.json" % db, "w"), indent=1, default=list)
    open("out/profile/%s/PROFILE.md" % db, "w").write("\n".join(L) + "\n"); print("\n".join(L))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    run(a[0], int(a[a.index("--probes") + 1]) if "--probes" in a else 6, "--no-checks" not in a, parse_request(a))
