"""THE REQUEST PATH: the closest sensible mix to a user's intent, served from the reviewed pools. No model calls.
    python -m specbridge.comm.construct.serve intent.json            -> the tasks (out/serve/tasks.jsonl) and SERVED.md
    python -m specbridge.comm.construct.serve --db student_club --preset deep --count 50 [--priority-arith 2] [--no-substitute]
INTENT
  target    where the user wants tasks: {"cells": {"A,S": w}} | {"arith": [lo, hi], "steps": [lo, hi]} | {"preset": ...} | {"mix": [...]}
            (a TARGET, not a requirement: the delivered mix may move to nearby cells, reported)
  count, seed
  hard      REQUIREMENTS, never crossed: databases, tables (only these), exclude_tables, ops_required (every task uses one of
            them), ops_forbidden, exclude_partial (no task that deliberately leaves out stated rows)
  standard  the quality standard (STANDARDS): benchmark (default) | analyst | exploratory | strict. Every returned task says
            its verdicts; complexity integrity is reported as "not assessed" until it is, and strict then returns nothing
  priority  {"arith": wA, "steps": wS}: the cost of moving one task one unit of depth along each axis (default 1, 1)
  substitute   false = no moves at all (exact cells or shortfall)
  max_move  {"arith": 1, "steps": 1} (default): the largest depth deviation a substituted task may have on each axis. A
            cell farther than this is never used: the task becomes a reported shortfall ("closest available" must not
            become "too different to be useful"). Set a larger value to allow wider substitution.
  max_share_per_quantity   diversity: no base quantity in more than this share of the tasks (default 0.2). A cap of c
            needs at least 1/c distinct quantities in stock; with thin stock it causes its own shortfall, reported apart.
  fresh     true = also generate new SQL for the shortfall, labelled PENDING REVIEW (not approved, not in the pool)
CLOSEST, defined: among assignments of the requested tasks (per target cell) to cells with approved stock, the one of least
total cost = sum over tasks of (wA |dA| + wS |dS|), with every unfilled task costing more than any allowed move -- so the
most tasks are delivered, then with the least total deviation. Solved exactly (min-cost flow). Hard constraints filter the
pool BEFORE the solve, so no move crosses them."""
import collections, json, math, os, random, sys, time

PRESETS = {"shallow": {"arith": [0, 1], "steps": [1, 2]}, "medium": {"arith": [1, 2], "steps": [2, 4]},
           "deep": {"arith": [2, 3], "steps": [4, 6]}, "very deep": {"arith": [3, 6], "steps": [6, 8]}}
STANDARDS = {
    # meaning and determined come from the task-quality rubric (specbridge.comm.construct.rubric, both reviewers); nothing else is assumed
    "benchmark":   lambda e: q(e, "meaning") == "yes" and q(e, "determined") == "yes",
    "analyst":     lambda e: q(e, "meaning") == "yes" and q(e, "determined") == "yes" and (all(v == "useful" for v in (e.get("quality") or {}).get("interest", {}).values()) or e.get("tier") == "approved"),
    "exploratory": lambda e: q(e, "meaning") in ("yes", "uncertain") and q(e, "determined") == "yes",
    "strict":      lambda e: q(e, "meaning") == "yes" and q(e, "determined") == "yes" and (e.get("complexity") or {}).get("known_redundancy") is False,
}


def q(e, k): return (e.get("quality") or {}).get(k)


def weights(t):
    W = collections.Counter()
    def rng(r, w):
        a, s = r.get("arith", [0, 6]), r.get("steps", [1, 8]); cs = [(x, y) for x in range(a[0], a[1] + 1) for y in range(s[0], s[1] + 1)]
        for c in cs: W[c] += w / len(cs)
    if t.get("cells"):
        for k, w in t["cells"].items(): W[tuple(int(x) for x in k.split(","))] += float(w)
    elif t.get("mix"):
        for m in t["mix"]: rng(PRESETS[m["preset"]] if "preset" in m else m, float(m.get("weight", 1)))
    else: rng(PRESETS[t["preset"]] if t.get("preset") else t, 1.0)
    tot = sum(W.values()); return {c: w / tot for c, w in W.items() if w > 0}


def quotas(W, n):
    raw = {c: W[c] * n for c in W}; q = {c: int(math.floor(v)) for c, v in raw.items()}
    for c in sorted(raw, key=lambda c: (-(raw[c] - q[c]), c))[: n - sum(q.values())]: q[c] += 1
    return {c: v for c, v in q.items() if v}


def available(intent):
    """The pool entries the hard constraints allow (current versions only), by cell."""
    from specbridge.comm.construct.pool import load, cat_version
    from specbridge.pd.structures.compose import VERSION
    h = intent.get("hard") or {}; dbs = h.get("databases") or [intent["db"]]; ok = STANDARDS[intent.get("standard", "benchmark")]
    by, dropped = collections.defaultdict(list), collections.Counter()
    for db in dbs:
        cv = cat_version(db)
        for e in load(db):
            if e.get("retired") or not ok(e): continue
            if h.get("exclude_partial") and (e.get("quality") or {}).get("partial"): dropped["partial population"] += 1; continue
            if e["grammar"] != VERSION or e["catalogue"] != cv: dropped["stale version"] += 1; continue
            reads = set(tables_read(e["sql"]))
            if h.get("tables") and not reads <= set(h["tables"]): dropped["reads a table not allowed"] += 1; continue
            if h.get("exclude_tables") and reads & set(h["exclude_tables"]): dropped["reads an excluded table"] += 1; continue
            if h.get("ops_required") and not set(e["ops"]) & set(h["ops_required"]): dropped["lacks a required operation"] += 1; continue
            if h.get("ops_forbidden") and set(e["ops"]) & set(h["ops_forbidden"]): dropped["uses a forbidden operation"] += 1; continue
            by[(e["A"], e["S"])].append(e)
    return by, dropped


def solve(demand, supply, wA, wS, substitute=True, max_move=None):
    """Exact min-cost assignment of demanded tasks to supplied cells; unfilled tasks cost more than any allowed move.
    -> ({(from, to): n}, {cell: unfilled})"""
    import networkx as nx
    G = nx.DiGraph(); SCALE = 100
    cost = lambda i, j: wA * abs(i[0] - j[0]) + wS * abs(i[1] - j[1])
    big = int(SCALE * (wA * 6 + wS * 8 + 1)) + 1
    n = sum(demand.values()); G.add_node("src", demand=-n); G.add_node("sink", demand=n)
    for i, d in demand.items():
        G.add_edge("src", ("d", i), capacity=d, weight=0); G.add_edge(("d", i), "sink", capacity=d, weight=big)   # shortfall
        for j, s in supply.items():
            if not s: continue
            c = cost(i, j)
            if i != j and not substitute: continue
            if max_move and (abs(i[0] - j[0]) > max_move.get("arith", 99) or abs(i[1] - j[1]) > max_move.get("steps", 99)): continue
            G.add_edge(("d", i), ("s", j), capacity=d, weight=int(round(SCALE * c)))
    for j, s in supply.items():
        if s: G.add_edge(("s", j), "sink", capacity=s, weight=0)
    F = nx.min_cost_flow(G)
    moves = collections.Counter(); short = {}
    for i in demand:
        for v, f in F[("d", i)].items():
            if not f: continue
            if v == "sink": short[i] = f
            else: moves[(i, v[1])] += f
    return moves, short


def pick(entries, k, rng, qcount, cap, ops_pref=None):
    """k tasks from one cell's stock: round robin over constructions, no base quantity past the diversity cap. Operation
    preferences order the constructions (a weighted, seeded order: weight = product of the preferences of its operations)."""
    by = collections.defaultdict(list)
    for e in entries: by[e["construction"]].append(e)
    keys = sorted(by); rng.shuffle(keys)
    if ops_pref:
        w = lambda key: math.prod(float(ops_pref.get(o, 1.0)) for o in by[key][0]["ops"])
        keys = sorted(keys, key=lambda key: (-math.log(1.0 - rng.random()) / w(key)) if w(key) > 0 else float("inf"))
        keys = [key for key in keys if w(key) > 0]
    for key in keys: rng.shuffle(by[key])
    out = []
    while len(out) < k and any(by.values()):
        progressed = False
        for key in keys:
            if len(out) >= k: break
            while by[key]:
                e = by[key].pop()
                if all(qcount[q] < cap for q in e["quantities"]):
                    out.append(e); progressed = True
                    for q in e["quantities"]: qcount[q] += 1
                    break
        if not progressed: break
    return out


def serve(intent):
    t0 = time.time(); n = int(intent.get("count", 50)); rng = random.Random(int(intent.get("seed", 42)))
    pr = intent.get("priority") or {}; wA, wS = float(pr.get("arith", 1)), float(pr.get("steps", 1))
    W = weights(intent.get("target") or {"preset": "medium"}); demand = quotas(W, n)
    by, dropped = available(intent); supply = {c: len(v) for c, v in by.items()}
    mm = intent.get("max_move") or {"arith": 1, "steps": 1}
    moves, short = solve(demand, supply, wA, wS, intent.get("substitute", True), mm)
    # what is ALSO in stock under the more permissive standard (reported, never served silently)
    extra = {}
    if intent.get("standard", "benchmark") in ("benchmark", "analyst", "strict"):
        by2, _d2 = available(dict(intent, standard="exploratory"))
        extra = {c: len(v) - len(by.get(c, [])) for c, v in by2.items() if len(v) > len(by.get(c, []))}
    share = float(intent.get("max_share_per_quantity", 0.2)); cap = max(1, int(math.ceil(share * n))); qcount = collections.Counter()
    distinct_q = len({q for v in by.values() for e in v for q in e["quantities"]})
    need = collections.Counter()
    for (i, j), f in moves.items(): need[j] += f
    got = {j: pick(by[j], need[j], rng, qcount, cap, intent.get("ops")) for j in sorted(need)}
    diversity_short = {j: need[j] - len(got[j]) for j in need if len(got[j]) < need[j]}
    tasks = []
    for (i, j), f in sorted(moves.items()):
        for e in got[j][:f]: tasks.append(dict(e, requested_cell="%d,%d" % i, standard=intent.get("standard", "benchmark"),
                                               complexity=e.get("complexity") or {"status": "not assessed"}))
        got[j] = got[j][f:]
    fresh = []
    if intent.get("fresh") and (short or diversity_short):
        fresh = pending(intent, {**short, **{j: d for j, d in diversity_short.items()}})
    res = {"intent": intent, "demand": {"%d,%d" % c: d for c, d in demand.items()}, "delivered": collections.Counter("%d,%d" % (t["A"], t["S"]) for t in tasks),
           "moves": {"%d,%d -> %d,%d" % (i + j): f for (i, j), f in moves.items() if i != j}, "shortfall": {"%d,%d" % c: s for c, s in short.items()},
           "diversity_shortfall": {"%d,%d" % c: s for c, s in diversity_short.items()}, "dropped_by_hard_constraints": dict(dropped),
           "meaning": dict(collections.Counter(q(t, "meaning") for t in tasks)), "more_under_exploratory": {"%d,%d" % c: k for c, k in extra.items()},
           "partial_population": sum(bool((t.get("quality") or {}).get("partial")) for t in tasks),
           "unique_computations": len({signature(t) for t in tasks}),
           "diversity": {"cap_share": share, "cap_tasks": cap, "distinct_quantities_in_stock": distinct_q, "needed_for_cap": math.ceil(1 / share) if share else None},
           "deviation": deviation(moves),
           "max_move": mm,
           "cost": sum((wA * abs(i[0] - j[0]) + wS * abs(i[1] - j[1])) * f for (i, j), f in moves.items()), "seconds": time.time() - t0,
           "explanation": explain(demand, moves, short, diversity_short, wA, wS, intent)}
    return tasks, fresh, res


def tables_read(sql):
    """Every database table the SQL reads (FROM and JOIN), not only those its quantities come from; step names excluded."""
    import re
    return sorted({t for t in re.findall(r'(?:FROM|JOIN)\s+"([^"]+)"', sql) if not re.fullmatch(r"s\d+", t)})


def signature(e):
    """One COMPUTATION: the database, the construction (operations and levels) and the base quantities. Two tasks with the
    same signature differ only in choices the construction does not record (e.g. which aggregate of a carried measure)."""
    return (e["db"], e["construction"], tuple(sorted(e["quantities"])))


def deviation(moves):
    """Per delivered task, how far its cell is from the requested cell: mean and max |dA|, |dS|."""
    fs = [(abs(i[0] - j[0]), abs(i[1] - j[1]), f) for (i, j), f in moves.items()]; n = sum(f for _a, _s, f in fs)
    if not n: return {"tasks": 0}
    return {"tasks": n, "exact": sum(f for a, s, f in fs if not a and not s), "mean_dA": round(sum(a * f for a, s, f in fs) / n, 2),
            "mean_dS": round(sum(s * f for a, s, f in fs) / n, 2), "max_dA": max(a for a, s, f in fs if f), "max_dS": max(s for a, s, f in fs if f)}


def explain(demand, moves, short, dshort, wA, wS, intent):
    n = sum(demand.values()); exact = sum(f for (i, j), f in moves.items() if i == j); moved = sum(f for (i, j), f in moves.items() if i != j)
    s = ["Requested %d tasks; %d delivered in the requested cells" % (n, exact)]
    if moved:
        dA = sum((j[0] - i[0]) * f for (i, j), f in moves.items() if i != j); dS = sum((j[1] - i[1]) * f for (i, j), f in moves.items() if i != j)
        s.append("%d moved to the nearest cells with stock meeting the %s standard (net arithmetic depth %+d, net step depth %+d; a move costs %g per arithmetic level and %g per step)" % (moved, intent.get("standard", "benchmark"), dA, dS, wA, wS))
    mm = intent.get("max_move") or {"arith": 1, "steps": 1}
    if short: s.append("%d not delivered: no stock meeting the %s standard %s" % (sum(short.values()), intent.get("standard", "benchmark"),
                        "within %d arithmetic level(s) and %d step(s) of the requested cells" % (mm.get("arith", 99), mm.get("steps", 99)) if intent.get("substitute", True) else "in the requested cells (substitution off)"))
    if dshort: s.append("%d not delivered because of the diversity cap (no base quantity in more than %s of the tasks)" % (sum(dshort.values()), intent.get("max_share_per_quantity", 0.2)))
    return "; ".join(s) + "."


def pending(intent, cells):
    """NEW SQL for unfilled cells, generated and data-checked now, NOT reviewed: labelled pending review, never approved."""
    from specbridge.pd.structures.compose import Space
    from specbridge.comm.construct.profile import deliver
    db = intent["db"]; sp = Space(db); R = sp.reachable()
    ok = {c: k for c, k in cells.items() if c in R}
    if not ok: return []
    out, _r, _w = deliver(sp, {"cells": {"%d,%d" % c: k for c, k in ok.items()}, "count": sum(ok.values()), "seed": int(intent.get("seed", 42)) + 7}, set(R))
    return [dict(x, status="pending review") for x in out]


def main(a):
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if a and a[0].endswith(".json"): intent = json.load(open(a[0]))
    else:
        intent = {"db": opt("--db"), "count": int(opt("--count", 50)), "seed": int(opt("--seed", 42)), "substitute": "--no-substitute" not in a,
                  "priority": {"arith": float(opt("--priority-arith", 1)), "steps": float(opt("--priority-steps", 1))}, "fresh": "--fresh" in a}
        t = {}
        if opt("--preset"): t["preset"] = opt("--preset")
        if opt("--arith"): t["arith"] = [int(x) for x in opt("--arith").split("-")]
        if opt("--steps"): t["steps"] = [int(x) for x in opt("--steps").split("-")]
        intent["target"] = t or {"preset": "medium"}
        if opt("--standard"): intent["standard"] = opt("--standard")
    tasks, fresh, res = serve(intent)
    os.makedirs("out/serve", exist_ok=True)
    with open("out/serve/tasks.jsonl", "w") as f:
        for t in tasks + fresh: f.write(json.dumps(t) + "\n")
    L = ["# Served", "", res["explanation"], "", "Served in %.3fs from the reviewed pools (no model calls)%s." % (res["seconds"], "; %d more generated fresh and PENDING REVIEW" % len(fresh) if fresh else ""), "",
         "| cell | requested | delivered |", "|---|---|---|"]
    for c in sorted(set(res["demand"]) | set(res["delivered"]), key=lambda k: tuple(map(int, k.split(",")))):
        L.append("| %s | %d | %d |" % (c, res["demand"].get(c, 0), res["delivered"].get(c, 0)))
    if res["moves"]: L += ["", "Moves: " + ", ".join("%s x%d" % kv for kv in res["moves"].items())]
    if res["dropped_by_hard_constraints"]: L += ["", "Excluded by hard constraints: %s" % res["dropped_by_hard_constraints"]]
    open("out/serve/SERVED.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
    return res


if __name__ == "__main__":
    main(sys.argv[1:])
