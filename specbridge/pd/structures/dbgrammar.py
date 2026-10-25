"""specbridge.pd.structures.dbgrammar -- DATABASE-CENTRED P WITH MEANINGFUL ARITHMETIC AND STEPS (v2, 2026-09-30; docs/DBGRAMMAR.md).
Defined from the database's signature (specbridge.pd.structures.dbfirst.Signature: the catalogue's roles, units, additivity, relations;
foreign keys). No source benchmark is read. Two controls: arithmetic depth A and step depth S. Every operation carries WHY
it makes sense, read from the catalogue; nothing database-specific is written here.

QUANTITIES on one row of a record table c (units AND kind decide -- two flows or two stocks, by the catalogue's additivity over
time; a catalogue relation alone never licenses arithmetic; a derived quantity must not restate a column; a denominator must be
positive on the data):
  base        a measure column                                                                      depth 0
  diff        a - b      a, b measures of c in the SAME unit                                         depth 1
  relative    a / b      same unit (a ratio of like quantities), or b's declared part a, or a declared rate a per b
  product     a * b      a declared product whose units combine (X/Y * Y = X)
  gap         p - m      a product or measure compared with a same-unit measure of the row            depth 2
  reldiff     (a - b)/b  same unit                                                                    depth 2
AGGREGATION LEVELS (steps; joins only upward along foreign keys, so no row is multiplied):
  S0  rank the rows of c by a quantity (top 10)
  S1  per group g (a category of c or reachable upward): AVG, SUM (only if additive), or a ratio of sums (+1 arithmetic)
  S2  per entity e (a parent c repeats under), then: entities above their group's average with the gap v - avg (+1) |
      rank within the group | the average per-entity value per group
  S3  per entity -> per group -> the groups above the overall average, with the gap (+1)
Every instance is checked on the data: the quantity varies and differs from its operands; groups differ; a comparison cuts.
    instances(S, A=None, S_=None) -> [{"id", "A", "S", "construct", "sql", "why": [...], "slots"}]"""
import collections, itertools, re
from specbridge.pd.structures.dbfirst import Signature, Q

AGGS = ("AVG", "SUM")


def unit(S, t, c): return (S.col.get("%s.%s" % (t, c), {}) or {}).get("unit") or ""


def numeric_cols(S, t):
    """Measures (ratio or interval scale) and counts (v2: admitted as quantities; whether they may be summed is rule 1's)."""
    return [c.split(".", 1)[1] for c, m in S.col.items() if c.split(".", 1)[0] == t and
            ((m.get("semantic_role") == "measure" and m.get("scale") in ("ratio", "interval")) or (m.get("semantic_role") == "count" and m.get("scale") == "ratio"))]


def is_count(S, t, c): return (S.col.get("%s.%s" % (t, c), {}) or {}).get("semantic_role") == "count"


def population(S, t, c): return ((S.col.get("%s.%s" % (t, c), {}) or {}).get("population") or "").strip().lower()


def time_indexed(S, t):
    """The records of t are placed in time: t has a date, or reaches a table with one along its upward links (a standing
    is placed in time by its race)."""
    return any(S.cols(u, lambda m: m.get("semantic_role") == "date") for u, _j in S.up(t))


def label(S, t, c):
    m = S.col.get("%s.%s" % (t, c), {}) or {}
    return m.get("quantity") or m.get("desc") or c


def additive(S, t, c, dated):
    """RULE 1 (v2): SUM is admissible only if the catalogue declares the quantity additive over EVERY dimension the
    aggregation spans: always entities (records of different units), and time when the records are placed in time
    (`dated` = time_indexed). A stock (not additive over time) is never summed across times; unknown additivity rejects."""
    a = (S.col.get("%s.%s" % (t, c), {}) or {}).get("additive") or {}
    return a.get("entities") is True and (not dated or a.get("time") is True)


def combine_units(u1, u2):
    """X/Y * Y -> X; Y * X/Y -> X; else ''."""
    for a, b in ((u1, u2), (u2, u1)):
        if "/" in a:
            num, den = a.split("/", 1)
            if den.strip().rstrip("s") == b.strip().rstrip("s") or den.strip() in b: return num.strip()
    return ""


def quantities(S, t):
    """Row quantities of table t: dicts {sql, depth, unit, additive, why, ops}."""
    dated = time_indexed(S, t)
    col = lambda c: '%s.%s' % (Q(t), Q(c))
    ms = numeric_cols(S, t)
    rel = [r for r in S.cat.get("relations", []) if r["a"].split(".")[0] == t and r["b"].split(".")[0] == t]
    out = []
    for m in ms:
        d = (S.col.get("%s.%s" % (t, m), {}) or {}).get("direction")
        if d:   # AN UNSIGNED FLOW whose direction is another column (catalogue): its sum is VOLUME, never a net flow
            out.append({"sql": col(m), "depth": 0, "unit": unit(S, t, m), "additive": additive(S, t, m, dated), "name": "%s (unsigned)" % label(S, t, m), "ops": {m},
                        "why": ["%s is stored unsigned (direction in %s.%s): summing it gives total volume, credits and withdrawals together, not a net flow" % (label(S, t, m), t, d["by"])]})
            lit = lambda xs: ", ".join("'%s'" % x for x in xs)
            out.append({"sql": "(CASE WHEN %s.%s IN (%s) THEN %s WHEN %s.%s IN (%s) THEN -%s END)" % (Q(t), Q(d["by"]), lit(d["in"]), col(m), Q(t), Q(d["by"]), lit(d["out"]), col(m)),
                        "depth": 1, "unit": unit(S, t, m), "additive": additive(S, t, m, dated), "name": "net %s" % label(S, t, m), "ops": {m},
                        "why": ["net %s: %s counted positive (%s), %s negative (%s) by the documented direction%s" % (label(S, t, m), lit(d["in"]), "in", lit(d["out"]), "out",
                                "; %s undocumented and left out" % lit(d["undocumented"]) if d.get("undocumented") else "")]})
        else:
            out.append({"sql": col(m), "depth": 0, "unit": unit(S, t, m), "additive": additive(S, t, m, dated), "why": [], "name": label(S, t, m), "ops": {m}})
    kind = lambda c: ((S.col.get("%s.%s" % (t, c), {}) or {}).get("additive") or {}).get("time")      # True flow, False stock
    # SAME UNIT AND SAME KIND: two flows or two stocks. A flow and a stock in one unit (a transaction and the balance after
    # it) are not like quantities, and their difference or ratio has no reading.
    same = [(a, b) for a, b in itertools.permutations(ms, 2) if unit(S, t, a) and unit(S, t, a) == unit(S, t, b) and kind(a) == kind(b)
            and (not (is_count(S, t, a) or is_count(S, t, b)) or (is_count(S, t, a) and is_count(S, t, b) and population(S, t, a) and population(S, t, a) == population(S, t, b)))]
    # RULE 2 (v2): two counts combine only when the catalogue names the same population (crimes '95 vs crimes '96); a count
    # with a measure, or counts of different populations, combine only through a declared rate relation
    for a, b in same:
        ua = unit(S, t, a); la, lb = label(S, t, a), label(S, t, b)
        if a < b:
            out.append({"sql": "(%s - %s)" % (col(a), col(b)), "depth": 1, "unit": ua, "additive": additive(S, t, a, dated) and additive(S, t, b, dated),
                        "why": ["%s - %s: both in %s and of the same kind (%s) on the same %s" % (la, lb, ua, {True: "flows", False: "stocks"}.get(kind(a), "same additivity"), S.cat["tables"].get(t, {}).get("grain", t))], "name": "%s minus %s" % (la, lb), "ops": {a, b}})
        out.append({"den": b, "sql": "(CAST(%s AS REAL) / %s)" % (col(a), col(b)), "depth": 1, "unit": "ratio", "additive": False,
                    "why": ["%s / %s: a ratio of two quantities in %s" % (la, lb, ua)], "name": "%s relative to %s" % (la, lb), "ops": {a, b}})
        out.append({"den": b, "sql": "(CAST((%s - %s) AS REAL) / %s)" % (col(a), col(b), col(b)), "depth": 2, "unit": "ratio", "additive": False,
                    "why": ["(%s - %s) / %s: the relative difference of two quantities in %s" % (la, lb, lb, ua)], "name": "relative difference of %s from %s" % (la, lb), "ops": {a, b}})
    for r in rel:
        a, b = r["a"].split(".")[1], r["b"].split(".")[1]
        if a not in S.cols(t, lambda m: True) or b not in S.cols(t, lambda m: True): continue
        la, lb = label(S, t, a), label(S, t, b); ua, ub = unit(S, t, a), unit(S, t, b)
        if r["kind"] in ("part_of", "rate") and ua != ub:
            out.append({"den": b, "sql": "(CAST(%s AS REAL) / %s)" % (col(a), col(b)), "depth": 1, "unit": "%s per %s" % (ua or la, ub or lb), "additive": False,
                        "why": ["%s / %s: the catalogue declares %s %s %s" % (la, lb, la, "part of" if r["kind"] == "part_of" else "a rate over", lb)], "name": "%s per %s" % (la, lb), "ops": {a, b}})
        if r["kind"] == "product":
            u = combine_units(ua, ub)
            if not u: continue
            p = {"sql": "(%s * %s)" % (col(a), col(b)), "depth": 1, "unit": u, "additive": additive(S, t, a, dated),
                 "why": ["%s x %s: the catalogue declares a product, %s x %s = %s" % (la, lb, ua, ub, u)], "name": "%s times %s" % (la, lb), "ops": {a, b}}
            out.append(p)
            for m in ms:
                if m not in (a, b) and unit(S, t, m) == u:
                    out.append({"sql": "(%s - %s)" % (p["sql"], col(m)), "depth": 2, "unit": u, "additive": p["additive"] and additive(S, t, m, dated),
                                "why": p["why"] + ["(%s) - %s: both in %s" % (p["name"], label(S, t, m), u)], "name": "%s minus %s" % (p["name"], label(S, t, m)), "ops": {a, b, m}})
    return out


def varies(S, t, q):
    """On the data: the quantity takes at least 2 values; a derived quantity differs, on some row, from EVERY column of its
    table (not only its operands: `amount - remaining` that equals `spent` restates a column); and a ratio's denominator is
    positive on every row where it is present (a zero or negative denominator makes the ratio unreadable).
    Batched: all comparisons in one scan. "At least 2 values" and "differs on some row" are EXISTENTIAL, so a prefix of the
    rows that shows them settles them and only what it leaves open is scanned in full -- the same answer as a full scan.
    Memoised on the signature."""
    key = ("varies", t, q["sql"], q.get("den"))
    if key in S.memo: return S.memo[key]
    others = numeric_cols(S, t) + sorted(q["ops"]) if q["depth"] else []
    parts = ["COUNT(DISTINCT %s)" % q["sql"]] + ["SUM(CASE WHEN %s IS NOT %s.%s THEN 1 ELSE 0 END)" % (q["sql"], Q(t), Q(o)) for o in others]
    settled = lambda i, x: x >= 2 if i == 0 else x > 0
    def scan(ps, src):
        r = S.run("SELECT %s FROM %s" % (", ".join(ps), src))
        return None if isinstance(r, str) or not r else [x or 0 for x in r[0]]
    v = scan(parts, "(SELECT * FROM %s LIMIT %d) AS %s" % (Q(t), PREFIX, Q(t)))
    need = [i for i, x in enumerate(v) if not settled(i, x)] if v is not None else None
    w = scan([parts[i] for i in need], Q(t)) if need else []
    ok = need is not None and w is not None and all(settled(i, x) for i, x in zip(need, w))
    if ok and q["depth"] and q.get("den"):   # universal: every row, one scan
        r = scan(["SUM(CASE WHEN %s.%s <= 0 THEN 1 ELSE 0 END)" % (Q(t), Q(q["den"]))], Q(t))
        ok = r is not None and not r[0]
    S.memo[key] = ok; return ok


PREFIX = 2000


MIN_PER_GROUP = 2     # a group key must GROUP: on average at least this many units (rows of t) per group


def groups(S, t, include_self=True):
    """Category columns of t or reachable upward that group the rows of t: 2..50 distinct values and, on average, at least
    MIN_PER_GROUP rows of t per value -- a near-unique label (one event per event name) groups nothing, so comparing a unit
    with "its group" would compare it with itself. (table, column, joins). Memoised on the signature."""
    if ("groups", t, include_self) in S.memo: return S.memo[("groups", t, include_self)]
    out = []
    for gt, j in S.up(t):
        if gt == t and not include_self: continue
        for g in S.cols(gt, lambda m: m.get("semantic_role") == "category"):
            r = S.run("SELECT COUNT(DISTINCT %s.%s), COUNT(%s.%s) FROM %s %s" % (Q(gt), Q(g), Q(gt), Q(g), Q(t), " ".join(j)))
            if isinstance(r, str) or not r: continue
            k, n = r[0][0] or 0, r[0][1] or 0
            if 2 <= k <= 50 and n >= MIN_PER_GROUP * k: out.append((gt, g, j))
    S.memo[("groups", t, include_self)] = out; return out


def instances(S, A=None, S_=None, cap_per_cell=None, check=True):
    """check=False: every instance the grammar can write, WITHOUT the data checks (so a caller can deduplicate and select
    first, then check only what it selected with `admit`)."""
    out = []
    rec = [t for t in S.cat["tables"] if any(c == t and S.many(t, cc) for c, cc, p, pc in S.fk)]
    for t in rec:
        qs = [q for q in quantities(S, t) if not check or varies(S, t, q)]
        key = S.cat["tables"].get(t, {}).get("keys", [None])[0] or S.cols(t, lambda m: m.get("semantic_role") == "identifier")[0]
        dated = time_indexed(S, t)
        for q in qs:
            base = {"table": t, "quantity": q["name"], "unit": q["unit"], "quantity_sql": q["sql"]}
            # S0: rank rows
            out.append({"A": q["depth"], "S": 0, "construct": "rank rows", "why": q["why"] + ["rank %s rows by it" % t],
                        "sql": "SELECT %s.%s, %s FROM %s WHERE %s IS NOT NULL ORDER BY %s DESC LIMIT 10" % (Q(t), Q(key), q["sql"], Q(t), q["sql"], q["sql"]), "slots": base})
            # S1: per group
            for gt, g, j in groups(S, t):
                J = " ".join(j)
                for a in AGGS:
                    if a == "SUM" and not q["additive"]: continue
                    out.append({"A": q["depth"], "S": 1, "construct": "%s per group" % a,
                                "why": q["why"] + ["%s over the %s records of each %s group%s" % (a, t, g, " (additive)" if a == "SUM" else "")],
                                "sql": "SELECT %s.%s, %s(%s) FROM %s %s GROUP BY %s.%s" % (Q(gt), Q(g), a, q["sql"], Q(t), J, Q(gt), Q(g)), "slots": dict(base, group=g, agg=a)})
            # S2 / S3: per entity, then per group
            for c, cc, e, ek in S.fk:
                if c != t or not S.many(t, cc): continue
                for gt, g, j in groups(S, e):
                    agg = "SUM" if q["additive"] else "AVG"
                    per = ("WITH per AS (SELECT %s.%s AS e, %s.%s AS g, %s(%s) AS v FROM %s JOIN %s ON %s.%s = %s.%s %s GROUP BY %s.%s, %s.%s)"
                           % (Q(e), Q(ek), Q(gt), Q(g), agg, q["sql"], Q(e), Q(t), Q(t), Q(cc), Q(e), Q(ek), " ".join(j), Q(e), Q(ek), Q(gt), Q(g)))
                    w = q["why"] + ["%s of it per %s (%s)" % (agg, e, "additive" if agg == "SUM" else "a ratio or stock is averaged")]
                    sl = dict(base, entity=e, group=g, agg=agg)
                    out.append({"A": q["depth"] + 1, "S": 2, "construct": "above group average, with the gap",
                                "why": w + ["compare each %s with the average of its %s group; the gap is in the same unit" % (e, g)],
                                "sql": per + ", grp AS (SELECT g, AVG(v) AS av FROM per GROUP BY g) SELECT per.e, per.g, per.v, per.v - grp.av FROM per JOIN grp ON per.g = grp.g WHERE per.v > grp.av", "slots": sl})
                    out.append({"A": q["depth"], "S": 2, "construct": "rank within group", "why": w + ["rank each %s within its %s group (ties kept)" % (e, g)],
                                "sql": per + ", ranked AS (SELECT g, e, v, RANK() OVER (PARTITION BY g ORDER BY v DESC) AS r FROM per) SELECT g, e, v FROM ranked WHERE r <= 3", "slots": sl})
                    out.append({"A": q["depth"], "S": 2, "construct": "average per-entity value per group", "why": w + ["average the per-%s values within each %s group" % (e, g)],
                                "sql": per + " SELECT g, AVG(v) FROM per GROUP BY g", "slots": sl})
                    out.append({"A": q["depth"] + 1, "S": 3, "construct": "groups above the overall average, with the gap",
                                "why": w + ["average per %s group, then compare with the average over all %s; the gap is in the same unit" % (g, e)],
                                # the overall average is its own one-row step, attached by the comparison itself (no constant key)
                                "sql": per + ", grp AS (SELECT g, AVG(v) AS av FROM per GROUP BY g), tot AS (SELECT AVG(v) AS ov FROM per)"
                                       " SELECT grp.g, grp.av, grp.av - tot.ov FROM grp JOIN tot ON grp.av > tot.ov", "slots": sl})
    for i, x in enumerate(out): x["id"] = "%s-g%04d" % (S.db, i)
    return [x for x in out if (A is None or x["A"] == A) and (S_ is None or x["S"] == S_)]


def quantity_of(S, x):
    """The row quantity an instance was built on (by its SQL: names can repeat within a table)."""
    t = x["slots"]["table"]
    if ("qs", t) not in S.memo: S.memo[("qs", t)] = {q["sql"]: q for q in quantities(S, t)}
    return S.memo[("qs", t)][x["slots"]["quantity_sql"]]


def admit(S, x):
    """The data checks for one instance, as `instances(check=True)` applies them: its quantity varies, and its intermediate
    result matters. (ok, why)."""
    if not varies(S, x["slots"]["table"], quantity_of(S, x)): return False, "quantity does not vary"
    return matters(S, x)


def matters(S, x):
    """The intermediate result matters on the data (per construct)."""
    rows = S.run(x["sql"])
    if isinstance(rows, str) or not rows: return False, "empty or error"
    if x["S"] == 1:
        vals = [r[1] for r in rows if r[1] is not None]
        return (len(rows) >= 2 and len(set(vals)) >= 2), "%d groups" % len(rows)
    if x["construct"].startswith("groups above"):
        return (1 <= len(rows)), "%d groups above" % len(rows)
    if x["S"] == 2 and x["construct"].startswith("above"):
        return (len(rows) >= 1), "%d entities above" % len(rows)
    if x["S"] == 2 and x["construct"].startswith("average per-entity"):
        vals = [r[1] for r in rows if r[1] is not None]
        return (len(rows) >= 2 and len(set(vals)) >= 2), "%d groups" % len(rows)
    return True, "%d rows" % len(rows)


def coverage(S):
    """WHAT THE GRAMMAR CAN REACH ON THIS DATABASE, and where it stops, table by table (a zero is reported, never hidden).
    Per table: rows; whether it is a RECORD table (it repeats under a single-column foreign key); its numeric columns as the
    catalogue has them (measure/count with a ratio or interval scale), which of those can be summed over the dimensions
    aggregated, the quantities that vary on the data, and the groups. Plus the composite foreign keys left out of the join
    graph and the tables that thereby lose every link."""
    rows = lambda t: (S.run("SELECT COUNT(*) FROM %s" % Q(t)) or [[0]])[0][0]
    rec = {t for t in S.cat["tables"] if any(c == t and S.many(t, cc) for c, cc, p, pc in S.fk)}
    linked = {x for c, cc, p, pc in S.fk for x in (c, p)}
    T = []
    for t in S.cat["tables"]:
        roles = collections.Counter((m or {}).get("semantic_role") for c, m in S.col.items() if c.split(".", 1)[0] == t)
        nc = numeric_cols(S, t); dated = time_indexed(S, t)
        qs = [q for q in quantities(S, t) if varies(S, t, q)] if t in rec else []
        T.append({"table": t, "rows": rows(t), "record": t in rec, "roles": dict(roles), "numeric": nc,
                  "summable": [c for c in nc if additive(S, t, c, dated)], "time_indexed": dated,
                  "quantities": len(qs), "by_depth": dict(collections.Counter(q["depth"] for q in qs)),
                  "groups": len(groups(S, t)) if t in rec else 0,
                  "composite_only": t not in linked and any(t in (c, p) for c, _cs, p in S.composite)})
    return {"tables": T, "fk": len(S.fk), "composite": S.composite}
