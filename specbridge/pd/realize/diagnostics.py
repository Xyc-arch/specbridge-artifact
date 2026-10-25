"""specbridge.pd.realize.diagnostics -- DIAGNOSTICS, NEVER VERDICTS. What a program does that may be unintended, recorded beside the checker's
verdicts and changing no acceptance. A diagnostic becomes a rejection only where a task's declared contract makes it
an incompatibility (docs/LANGUAGE.md); until then it is a count, and a signal of triviality or difficulty.

Three kinds of facts are kept apart, because each answers a different question:
    STORAGE      how SQLite holds a column's values (the catalogue's `storage`: text or numeric)
    ROLE         what the column means (the catalogue's `semantic_role`: measure, identifier, category, flag, date)
    PARSES       whether every stored value reads as a number (a row check) -- a fact about the values, not the
                 meaning: an account code "00123" parses and stays an identifier
and CONVERSION: a text-stored value used as a number is converted by SQLite only in arithmetic, never in an ordering
comparison, so numeric use needs an explicit CAST.

Static diagnostics (the checker's walk, `Semantics.nodes`, and the catalogue):
    population differs        + or - of two quantities whose known populations differ, no recorded relationship
    text used as a number     a text-stored column in arithmetic or an ordering, with no CAST around it
    order on a category       <, >, BETWEEN on a column whose role is category or identifier
    rows repeated in a listing   a query with no aggregation, grouping or DISTINCT whose joins repeat a table
Execution diagnostics (the program run on the database):
    constant output column    a returned column with one value across two or more rows
    CASE branch never used    a CASE output whose constant branch value never appears
    filter without effect     a WHERE condition whose removal leaves the row count unchanged
"""
from __future__ import annotations
import dataclasses

from specbridge.pd.structures.algebra import Agg, And, Arith, Between, Case, Cast, Cmp, Col, Const, Func, Program, emit
from specbridge.pd.realize.semantics import SUPPORTED, UNKNOWN


def facts(cat, t, c):
    """Storage, role and whether the values parse as numbers, for one stored column (cached on the catalogue)."""
    memo = cat.__dict__.setdefault("_diag_facts", {})
    if (t, c) not in memo:
        from specbridge.pd.realize.semantic import load
        v = cat.__dict__.setdefault("_diag_cols", load(cat)["columns"]).get("%s.%s" % (t, c), {})
        vals = [x for x in (cat.values(t, c) or []) if x is not None]
        def num(x):
            try: float(x); return True
            except Exception: return False
        memo[(t, c)] = {"storage": v.get("storage", ""), "role": v.get("semantic_role", ""),
                        "parses": bool(vals) and all(num(x) for x in vals)}
    return memo[(t, c)]


def _bare(e):
    """The stored column an operand reads directly (under unit-preserving functions), and whether a CAST wraps it."""
    cast = False
    while True:
        if isinstance(e, Cast): cast = True; e = e.expr
        elif isinstance(e, Func) and e.args and e.name.lower() in ("round", "abs", "coalesce", "ifnull", "nullif"): e = e.args[0]
        else: return (e if isinstance(e, Col) else None), cast


def static(p, cat):
    sem, out = cat.sem, []
    for e, steps, rep in sem.nodes(p):
        if isinstance(e, Arith) and e.op in "+-":
            l, r = sem.record(e.l, steps), sem.record(e.r, steps)
            if l.kind != "const" and r.kind != "const" and l.population and r.population \
                    and l.population.strip().lower() != r.population.strip().lower() and sem.verdict(e, steps, rep)[0] != SUPPORTED:
                out.append(("population differs", "%s vs %s" % (l.population, r.population)))
        sides = (e.l, e.r) if isinstance(e, (Arith, Cmp)) else (e.expr, e.lo, e.hi) if isinstance(e, Between) else ()
        ordering = isinstance(e, Between) or (isinstance(e, Cmp) and e.op in ("<", ">", "<=", ">="))
        if isinstance(e, Arith) or ordering:
            for s in sides:
                col, cast = _bare(s)
                if col is None or (col.table, col.name) not in cat.ann: continue
                f = facts(cat, col.table, col.name)
                if f["storage"] == "text" and not cast and (isinstance(e, Arith) or ordering):
                    out.append(("text used as a number", "%s.%s%s" % (col.table, col.name, " (values parse)" if f["parses"] else "")))
                if ordering and f["role"] in ("category", "identifier"):
                    out.append(("order on a category", "%s.%s (%s)" % (col.table, col.name, f["role"])))
    for q in _programs(p):
        agg = bool(q.group) or q.distinct or any(isinstance(x, Agg) for x, _a in q.select) or _has_agg(q.select)
        if not agg and q.scan.joins:
            rep = sem.repeated(q.scan.joins)
            if rep: out.append(("rows repeated in a listing", ", ".join(sorted(rep))))
    return out


def _has_agg(x):
    from specbridge.pd.structures.algebra import _find
    return bool(_find(x, Agg))


def _programs(p):
    out, stack = [], [p]
    while stack:
        q = stack.pop()
        if isinstance(q, Program):
            out.append(q); stack.extend(s for _n, s in q.ctes)
    return out


def executed(p, sql, con, run):
    """Execution diagnostics; `run(con, sql)` returns ("ok", rows) or a failure."""
    out = []
    st, rows = run(con, sql)
    if st != "ok": return [("not executed", str(rows)[:60])]
    if len(rows) >= 2:
        for i in range(len(rows[0])):
            if len({r[i] for r in rows}) == 1: out.append(("constant output column", "column %d = %r" % (i, rows[0][i])))
        for i, (x, _a) in enumerate(p.select if isinstance(p, Program) else ()):
            if isinstance(x, Case) and i < len(rows[0]):
                seen = {r[i] for r in rows}
                vals = [v.value for _w, v in x.whens if isinstance(v, Const)] + ([x.else_.value] if isinstance(x.else_, Const) else [])
                for v in dict.fromkeys(vals):
                    if v not in seen and not any(_same(v, s) for s in seen): out.append(("CASE branch never used", "column %d value %r" % (i, v)))
    if isinstance(p, Program) and isinstance(p.where, And) and len(p.where.preds) >= 2:
        from specbridge.pd.structures.algebra import Agg as A_
        def count(where):
            q = dataclasses.replace(p, where=where, select=((A_("COUNT", None, False, None), "n"),), group=(), having=None,
                                    order=(), limit=None, offset=0, distinct=False)
            s2, r2 = run(con, emit(q))
            return r2[0][0] if s2 == "ok" and r2 else None
        full = count(p.where)
        for k, c in enumerate(p.where.preds):
            rest = tuple(x for j, x in enumerate(p.where.preds) if j != k)
            n = count(rest[0] if len(rest) == 1 else And(rest))
            if full is not None and n is not None and n == full: out.append(("filter without effect", "condition %d of %d" % (k + 1, len(p.where.preds))))
    return out


def _same(a, b):
    try: return float(a) == float(b)
    except Exception: return a == b
