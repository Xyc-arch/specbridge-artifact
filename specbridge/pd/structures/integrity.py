"""COMPLEXITY INTEGRITY, read off the query itself (never off how it was built): does a stage RECOMPUTE an aggregate an
earlier stage already computed?
    recomputed(program) -> [finding, ...]     (empty = no recomputed aggregate)
A finding is two stages computing the same aggregate function, over the same column, with the same grouping, over the same
rows. The column is followed through stages: a column a stage passes on unchanged (a bare column of the stage it reads)
is the column it came from. The rows are followed too: a stage keeps its source's rows when it neither filters, groups,
aggregates, removes duplicates nor limits, and every stage it joins to is an aggregated stage joined on its grouping keys
(one match per row) or a one-row result; otherwise its rows are its own. Such a pair is a redundant step: the second
stage's value is the first stage's value, and the query's depth overstates the work it needs. Different functions (SUM
and AVG), different columns, different groupings or different rows are different aggregations and are never findings.
This is the review-side receipt of the grammar's rule (specbridge.pd.structures.compose: a measure is compared with its average at
a level at most once per population); on the grammar's output it must read zero."""
from specbridge.pd.structures.algebra import Agg, Col, Program, SetOp, Subq, _find


def _collapsing(q):
    return bool(q.group) or any(_find(e, Agg) for e, _a in q.select)


class _Lineage:
    def __init__(self, p):
        self.ctes = {}
        self._collect(p)

    def _collect(self, p):
        if isinstance(p, SetOp):
            for n, q in p.ctes: self.ctes[str(n).lower()] = q
            self._collect(p.left); self._collect(p.right); return
        if isinstance(p, Program):
            for n, q in p.ctes:
                self.ctes[str(n).lower()] = q; self._collect(q)

    def sources(self, q):
        items = [(q.scan.alias, q.scan.table)] + [(j.alias, j.table) for j in q.scan.joins]
        return {str(a).lower(): str(t).lower() for a, t in items}

    def origin(self, stage, q, col):
        """(stage, column) a column reference of q (a Col) comes from, following unchanged pass-throughs."""
        if not isinstance(col, Col): return None
        src = self.sources(q).get(str(col.alias).lower())
        if src is None: return None
        if src not in self.ctes: return ("table", src, col.name)
        sq = self.ctes[src]
        for e, a in sq.select:
            if str(a or "").lower() == str(col.name).lower():
                o = self.origin(src, sq, e) if isinstance(e, Col) and not _collapsing(sq) else None
                return o or (src, str(a).lower())
        return (src, str(col.name).lower())

    def rows(self, name, q):
        """An identifier of the rows q produces: its source's rows when q keeps them, else q itself."""
        if _collapsing(q) or q.where is not None or q.having is not None or q.distinct or q.limit is not None: return name
        src = str(q.scan.table).lower()
        for j in q.scan.joins:
            t = str(j.table).lower()
            if t not in self.ctes or not _collapsing(self.ctes[t]) or j.kind != "inner": return name
        return self.rows(src, self.ctes[src]) if src in self.ctes else ("table", src)


def recomputed(p):
    if not isinstance(p, (Program, SetOp)): return []
    L = _Lineage(p); seen, out = {}, []
    stages = list(L.ctes.items()) + ([("(answer)", p)] if isinstance(p, Program) else [])
    for name, q in stages:
        if not isinstance(q, Program) or not _collapsing(q): continue
        src = str(q.scan.table).lower()
        rows = q.where is None and (L.rows(src, L.ctes[src]) if src in L.ctes else ("table", src))
        if rows is False: rows = name                    # a filtered aggregation aggregates its own rows
        group = tuple(sorted(map(repr, (L.origin(name, q, g) or g for g in q.group))))
        for e, a in q.select:
            for ag in _find(e, Agg):
                if not isinstance(ag.arg, Col) or ag.filter is not None: continue
                k = (ag.fn.upper(), ag.distinct, L.origin(name, q, ag.arg), group, rows)
                if k[2] is None: continue
                if k in seen and seen[k] != name:
                    out.append({"stage": name, "recomputes": seen[k], "aggregate": "%s of %s.%s" % (ag.fn.upper(), k[2][0], k[2][-1]), "grouping": list(group)})
                else: seen.setdefault(k, name)
    return out


def trivial(p, con):
    """TRIVIAL COMPARISONS AND CUTS, read off the query and its data (independent of how it was built):
      a comparison  a stage joins an aggregated stage R (AVG or SUM, the reference) computed from the rows it reads itself; it is
                    trivial when R aggregates fewer than 2 rows, or when R groups and every group is a single row -- every
                    gap is then 0, every index or share 1
      a top-3 cut   a stage ranks within groups and the answer keeps rank <= 3; trivial when that keeps every row
    -> [finding, ...]. A value computed on ONE row is not a finding by itself (an overall total is a legitimate answer)."""
    from specbridge.pd.structures.algebra import Program, Agg, Col, Window, emit
    if not isinstance(p, Program): return []
    L = _Lineage(p); out = []
    W = "WITH " + ", ".join('"%s" AS (%s)' % (n, emit(q)) for n, q in p.ctes) + " " if p.ctes else ""
    def run(src, group):                                 # counted on the query's own stages (a Program may not hold an unread stage)
        return con.execute(W + 'SELECT COUNT(*)%s FROM "%s"' % (', COUNT(DISTINCT "%s"."%s")' % (src, group) if group else "", src)).fetchone()
    stages = list(L.ctes.items()) + [("(answer)", p)]
    for name, q in stages:
        if not isinstance(q, Program): continue
        mine = str(q.scan.table).lower()
        for j in q.scan.joins:
            r = str(j.table).lower(); R = L.ctes.get(r)
            if R is None or not _collapsing(R) or str(R.scan.table).lower() != mine or R.where is not None or R.scan.joins: continue
            if not any(isinstance(a, Agg) and a.fn.upper() in ("AVG", "SUM") for e, _a in R.select for a in _find(e, Agg)): continue
            g = [x for x in R.group if isinstance(x, Col)]
            res = run(mine, g[0].name if g else None)
            if (res[0] or 0) < 2: out.append({"stage": name, "reference": r, "why": "the reference aggregates %d row(s)" % (res[0] or 0)})
            elif g and res[0] == res[1]: out.append({"stage": name, "reference": r, "why": "every reference group is a single row"})
        if any(_find(e, Window) for e, _a in q.select) and name != "(answer)" and str(p.scan.table).lower() == name and p.where is not None:
            n = run(name, None)[0]
            m = con.execute("SELECT COUNT(*) FROM (%s)" % emit(p)).fetchone()[0]
            if n and m == n: out.append({"stage": name, "why": "the top-3 cut keeps every row"})
    return out
