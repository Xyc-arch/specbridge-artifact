"""specbridge.pd.structures.dbfirst -- DATABASE-CENTRED P, defined from D alone (docs/DBFIRST.md). Gold-free by construction.

    Signature(db)            Σ_D: tables, the catalogue's roles and additivity, foreign keys, one-to-many links     §1
    families(S)              every instance of F1-F4 on D: (family, slots, SQL)                                     §2
    matters(S, F, slots, q)  non-triviality on D's data: (kept?, why, rows)                                         §3
    law(admissible, n, seed) uniform within each (family, database) stratum, seeded round robin over strata         §4

Ported P is fitted on a source and projected by the checker (docs/LANGUAGE.md); this one has no source."""
import collections, itertools, json, os, random, sqlite3
Q = lambda s: '"%s"' % s


class Signature:
    def __init__(self, db):
        self.db = db                                                  # Σ_D (docs/DBFIRST.md §1)
        from specbridge.pd.corpora import found
        self.con = sqlite3.connect("file:%s/%s.sqlite?mode=ro" % (found(db), db), uri=True)
        self.cat = json.load(open("catalogues/%s.json" % db))
        self.fk = []                                                  # (child, col, parent, pcol)
        self.composite = []                                           # (child, [cols], parent): excluded, reported as lost coverage
        for (t,) in self.con.execute("select name from sqlite_master where type='table'"):
            links = {}
            for r in self.con.execute('PRAGMA foreign_key_list("%s")' % t):
                if r[2] and r[4]: links.setdefault(r[0], []).append((t, r[3], r[2], r[4]))
            # A COMPOSITE KEY is one link over several columns; joining on one of its columns alone would multiply rows.
            # Until composite joins are supported they are left out of the join graph (never a partial join).
            self.fk += [l[0] for l in links.values() if len(l) == 1]
            self.composite += [(t, [x[1] for x in l], l[0][2]) for l in links.values() if len(l) > 1]
        self.col = self.cat["columns"]
        self.memo = {}                                                # table statistics computed once per signature

    def many(self, child, col):
        if ("many", child, col) in self.memo: return self.memo[("many", child, col)]
        m = self.con.execute('SELECT MAX(c) FROM (SELECT COUNT(*) c FROM %s GROUP BY %s)' % (Q(child), Q(col))).fetchone()[0]
        self.memo[("many", child, col)] = (m or 0) > 1       # an empty table repeats nothing
        return self.memo[("many", child, col)]

    def up(self, t, depth=2):
        """Tables reachable from t along many-to-one foreign keys: [(table, [join clauses])]."""
        out, frontier = [(t, [])], [(t, [])]
        for _ in range(depth):
            nxt = []
            for cur, path in frontier:
                for c, cc, p, pc in self.fk:
                    if c == cur and p not in [x for x, _ in out]:
                        j = path + ["JOIN %s ON %s.%s = %s.%s" % (Q(p), Q(p), Q(pc), Q(c), Q(cc))]
                        out.append((p, j)); nxt.append((p, j))
            frontier = nxt
        return out

    def cols(self, t, pred):
        return [c.split(".", 1)[1] for c, m in self.col.items() if c.split(".", 1)[0] == t and pred(m)]

    def run(self, sql, cap=5000):
        try: return self.con.execute(sql).fetchmany(cap)
        except Exception as e: return "ERROR " + str(e)[:80]


measure = lambda m: m.get("semantic_role") == "measure" and m.get("scale") in ("ratio", "interval")
summable = lambda m, axis: measure(m) and (m.get("additive") or {}).get(axis) is True
category = lambda m: m.get("semantic_role") == "category"
date = lambda m: m.get("semantic_role") == "date"


def sum_ok(D, table, col):
    """SUM is defensible only over axes the measure adds along: across entities always needed; over time too when the
    records carry a date (a stock such as a running balance is not additive over time)."""
    m = D.col["%s.%s" % (table, col)]
    return summable(m, "entities") and (not D.cols(table, date) or summable(m, "time"))


def families(D):
    out = []
    record_tables = [t for t in D.cat["tables"] if any(c == t and D.many(t, cc) for c, cc, p, pc in D.fk)]
    for child in record_tables:
        ups = D.up(child)
        groups = [(t, g, j) for t, j in ups for g in D.cols(t, category) if t != child]      # the group comes through a join
        ms = D.cols(child, measure)
        # F1: aggregate across groups
        for m, (gt, g, j) in itertools.product(ms, groups):
            aggs = ["AVG"] + (["SUM"] if sum_ok(D, child, m) else [])
            for a in aggs:
                sql = "SELECT %s.%s, %s(%s.%s) FROM %s %s GROUP BY %s.%s" % (Q(gt), Q(g), a, Q(child), Q(m), Q(child), " ".join(j), Q(gt), Q(g))
                out.append(("F1", {"child": child, "measure": m, "agg": a, "group": "%s.%s" % (gt, g)}, sql))
        # F2: temporal comparison (summable over time and entities; a date on the child)
        for d in D.cols(child, date):
            for m, (gt, g, j) in itertools.product([m for m in ms if summable(D.col["%s.%s" % (child, m)], "time")], groups):
                yrs = [r[0] for r in D.run("SELECT strftime('%%Y', %s) y, COUNT(*) FROM %s GROUP BY y ORDER BY COUNT(*) DESC LIMIT 2" % (Q(d), Q(child)))]
                if len(yrs) < 2 or None in yrs: continue
                y1, y2 = sorted(yrs)
                s = lambda y: "SUM(CASE WHEN strftime('%%Y', %s.%s) = '%s' THEN %s.%s ELSE 0 END)" % (Q(child), Q(d), y, Q(child), Q(m))
                sql = "SELECT %s.%s, (%s - %s) * 100.0 / %s FROM %s %s GROUP BY %s.%s" % (Q(gt), Q(g), s(y2), s(y1), s(y1), Q(child), " ".join(j), Q(gt), Q(g))
                out.append(("F2", {"child": child, "measure": m, "date": d, "years": [y1, y2], "group": "%s.%s" % (gt, g)}, sql))
        # F3 / F4: entity = the parent the child repeats under; group attribute reachable upward from the entity
        for c, cc, ent, ek in D.fk:
            if c != child or not D.many(child, cc): continue
            egroups = [(t, g, j) for t, j in D.up(ent) for g in D.cols(t, category) if t != ent or True]
            for m, (gt, g, j) in itertools.product(ms, egroups):
                a = "SUM" if sum_ok(D, child, m) else "AVG"
                step = ("WITH per AS (SELECT %s.%s AS e, %s.%s AS g, %s(%s.%s) AS v FROM %s JOIN %s ON %s.%s = %s.%s %s GROUP BY %s.%s, %s.%s)"
                        % (Q(ent), Q(ek), Q(gt), Q(g), a, Q(child), Q(m), Q(ent), Q(child), Q(child), Q(cc), Q(ent), Q(ek), " ".join(j), Q(ent), Q(ek), Q(gt), Q(g)))
                out.append(("F3", {"records": child, "entity": ent, "measure": m, "agg": a, "group": "%s.%s" % (gt, g)},
                            step + ", grp AS (SELECT g, AVG(v) AS av FROM per GROUP BY g) SELECT per.e, per.g, per.v FROM per JOIN grp ON per.g = grp.g WHERE per.v > grp.av"))
                out.append(("F4", {"records": child, "entity": ent, "measure": m, "agg": a, "group": "%s.%s" % (gt, g), "k": 3},
                            step + ", ranked AS (SELECT g, e, v, RANK() OVER (PARTITION BY g ORDER BY v DESC) AS r FROM per) SELECT g, e, v, r FROM ranked WHERE r <= 3"))
    return out


def matters(D, fam, slots, sql):
    """Data checks: does the intermediate result matter on this database?"""
    rows = D.run(sql)
    if isinstance(rows, str): return False, rows, None
    if not rows: return False, "empty answer", rows
    if fam in ("F1", "F2"):
        vals = [r[1] for r in rows if r[1] is not None]
        if len(rows) < 2: return False, "fewer than 2 groups", rows
        if len(set(vals)) < 2: return False, "every group has the same value", rows
        if fam == "F2" and len(vals) < len(rows) / 2: return False, "most groups lack one of the years", rows
        return True, "%d groups, %d distinct values" % (len(rows), len(set(vals))), rows
    per = D.run(sql.split("), grp AS")[0].split("), ranked AS")[0] + ") SELECT g, COUNT(*), MIN(v), MAX(v) FROM per GROUP BY g")
    if isinstance(per, str) or len(per) < 2: return False, "fewer than 2 groups", rows
    if not any(n >= 2 and lo != hi for _g, n, lo, hi in per): return False, "no group has entities that differ", rows
    if fam == "F3":
        n_ent = sum(n for _g, n, _l, _h in per)
        if len(rows) >= n_ent: return False, "every entity is above its group average", rows
        return True, "%d groups; %d of %d entities above their group's average" % (len(per), len(rows), n_ent), rows
    ties = len(rows) - 3 * len(per)
    if all(n <= 3 for _g, n, _l, _h in per): return False, "no group has more than k entities", rows
    return True, "%d groups; %d rows (%+d from ties at rank 3)" % (len(per), len(rows), ties), rows




def law(admissible, n, seed=20261004):
    """A sample of n from the admissible instances (records with "family" and "database"): uniform within each stratum,
    seeded round robin over the strata in sorted order."""
    rng = random.Random(seed); by = collections.defaultdict(list)
    for x in admissible: by[(x["family"], x["database"])].append(x)
    for v in by.values(): rng.shuffle(v)
    keys = sorted(by); pick = []; i = 0
    while len(pick) < n and any(by.values()):
        k = keys[i % len(keys)]; i += 1
        if by[k]: pick.append(by[k].pop())
    return pick
