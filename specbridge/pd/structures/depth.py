"""DEPTH OF A QUERY, measured on the query itself (never on how it was built).
    measure(program) -> {"arith": A, "steps": S}
  STEP DEPTH S      the longest chain of dependent query stages. A stage is the main query, a named intermediate result
                    (CTE; a FROM subquery is one too), or a subquery in a clause. A stage depends on the stages it reads.
                    One flat query has S = 1; `per -> grp -> answer` has S = 3. The number of CTEs does not matter: two
                    stages that both read the table and are joined at the end give S = 2.
  ARITHMETIC DEPTH A the longest chain of dependent arithmetic operations (+ - * / %) that compute from data, FOLLOWED THROUGH
                    STAGES: a column of an earlier stage carries the depth of the expression that produced it, so a ratio
                    computed in step 1 and compared with its group average in step 3 (v - avg) has A = 2. Aggregates,
                    casts, CASE and windows pass depth through without adding to it; arithmetic over constants adds none.
                    Only what the answer depends on counts: the main query's expressions, with what they read."""
from dataclasses import fields, is_dataclass
from specbridge.pd.structures.algebra import Arith, Col, Program, SetOp, Subq


def _reads_data(x, memo):
    from specbridge.pd.realize.fidelity import _reads
    return _reads(x, memo)


class _Measure:
    def __init__(self, p):
        self.ctes = {}; self.cols = {}; self.steps = {}; self.rmemo = {}
        self._collect(p)
        self.root = p

    def _collect(self, p):
        if isinstance(p, SetOp):
            for n, q in p.ctes: self.ctes[str(n).lower()] = q
            self._collect(p.left); self._collect(p.right); return
        if isinstance(p, Program):
            for n, q in p.ctes:
                self.ctes[str(n).lower()] = q; self._collect(q)

    def _sources(self, q):
        """alias -> cte name for the FROM items of q that read a stage."""
        if not isinstance(q, Program): return {}
        items = [(q.scan.alias, q.scan.table)] + [(j.alias, j.table) for j in q.scan.joins]
        return {str(a).lower(): str(t).lower() for a, t in items if str(t).lower() in self.ctes}

    def stage_steps(self, q):
        """Steps of the chain ending at q (q counted)."""
        key = id(q)
        if key in self.steps: return self.steps[key]
        self.steps[key] = 1                                   # a guard against cycles (SQL has none)
        if isinstance(q, SetOp): s = max(self.stage_steps(q.left), self.stage_steps(q.right))
        else:
            reads = [self.ctes[t] for t in self._sources(q).values()]
            reads += [sq.program for sq in _find_subq(q)]
            s = 1 + max((self.stage_steps(r) for r in reads), default=0)
        self.steps[key] = s; return s

    def col_depth(self, cte, name):
        key = (cte, str(name).lower())
        if key in self.cols: return self.cols[key]
        self.cols[key] = 0
        q = self.ctes[cte]; d = 0
        progs = [q] if isinstance(q, Program) else [q.left, q.right]
        for pr in progs:
            for i, (e, alias) in enumerate(pr.select):
                nm = str(alias if alias is not None else (e.name if isinstance(e, Col) else "")).lower()
                if nm == key[1]: d = max(d, self.expr(e, pr))
        self.cols[key] = d; return d

    def expr(self, x, q):
        if isinstance(x, (tuple, list)): return max((self.expr(y, q) for y in x), default=0)
        if isinstance(x, Col):
            src = self._sources(q).get(str(x.alias).lower())
            return self.col_depth(src, x.name) if src else 0
        if isinstance(x, Subq): return self.query_arith(x.program)
        if isinstance(x, (Program, SetOp)): return 0
        if is_dataclass(x) and not isinstance(x, type):
            d = max((self.expr(getattr(x, f.name), q) for f in fields(x)), default=0)
            return d + (1 if isinstance(x, Arith) and _reads_data(x, self.rmemo) else 0)
        return 0

    def query_arith(self, q):
        if isinstance(q, SetOp): return max(self.query_arith(q.left), self.query_arith(q.right))
        return self.expr((q.select, q.where, q.having, q.order, q.group), q)


def _find_subq(q):
    from specbridge.pd.structures.algebra import _find
    return _find((q.select, q.where, q.group, q.having, q.order), Subq) if isinstance(q, Program) else []


def measure(p):
    m = _Measure(p)
    return {"arith": m.query_arith(p), "steps": m.stage_steps(p)}


def of_sql(sql, con):
    from specbridge.pd.structures.algebra import lift
    return measure(lift(sql, con))
