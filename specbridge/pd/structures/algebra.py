"""specbridge.pd.structures.algebra — THE PROGRAM, AND NOTHING ELSE.

A program is what ports. `lift(sql, con)` turns a gold query into one; `emit(p)` turns it back into SQL. The node
types carry no dataset, no database and no English: the only nodes that reference a WORLD are `Col` (a column of a
table), `Const` (a value drawn from data), the names of steps and output aliases (labels), and a clock read — which
is exactly the list of things porting has to rewrite.

Extracted from the 1624-line `synth/ra.py` at the 2026-09-13 restart, MINUS the Python interpreter and the gold
miner. Correctness of a delivered program now rests on SQLite plus the construction rules, not on two semantics
agreeing; the interpreter cost more per attempt than everything else in a build put together.
"""
from __future__ import annotations
import re, sys
from dataclasses import dataclass, fields, is_dataclass, replace
import sqlglot, sqlglot.errors
from sqlglot import exp


# ---------------------------------------------------------------- nodes
@dataclass(frozen=True)
class Col:
    alias: str          # FROM-item alias (the table name when unaliased); a self-join has two aliases
    name: str
    table: str = ""     # real table
    aff: str = "none"   # declared affinity: numeric | text | none (SQLite comparison rules depend on it)

@dataclass(frozen=True)
class Const:
    value: object

@dataclass(frozen=True)
class Arith:
    op: str             # + - * / %
    l: object
    r: object

    def __post_init__(self):
        # AN ANSWER THAT IS THE SAME WHATEVER THE DATA SAYS IS NOT AN ANSWER. `x - x` is 0 and `x / x` is 1 for every
        # row of every database, so a question built on one can be answered without reading anything. Delivered in a
        # BIRD cell as "( the total ( 1 when bond id is exactly 'TR445_4_8' … ) minus the total ( 1 when bond id is
        # exactly 'TR445_4_8' … ) )", answer 0. Neither existing check sees it: ND compares against what the program
        # returns over NO data, and over no data this is NULL rather than 0; LB finds a load-bearing decision inside
        # each branch. Same family as the repeated connective branch, and refused the same way. `+` and `*` are left
        # alone: `x + x` and `x * x` still depend on x.
        if self.op in ("-", "/") and self.l == self.r:
            if ENFORCE_DISTINCT: raise Unsupported(f"`x {self.op} x` is a constant: the answer would not depend on the data")

@dataclass(frozen=True)
class Cast:
    expr: object
    type: str           # REAL | INTEGER | TEXT

@dataclass(frozen=True)
class Func:
    name: str           # function name (sqlglot sql_name) — any scalar function passes through
    args: tuple         # lifted Expression arguments, in order
    template: str = ""  # SQLite rendering with __ARGi__ placeholders (units, keywords, paths kept verbatim)

@dataclass(frozen=True)
class Case:
    whens: tuple        # ((Pred, Expr), …)
    else_: object = None
    def __post_init__(self):
        # A LATER BRANCH ON A CONDITION ALREADY TESTED CAN NEVER FIRE. `CASE WHEN x BETWEEN 589 AND 591 THEN 'group 1'
        # WHEN x BETWEEN 589 AND 591 THEN 'group 2' …` yields 'group 1' always, and the reader is asked to evaluate a
        # second rule that cannot apply — 11 of 40 delivered rows. The binder built it by drawing both branches'
        # bounds from the same seed row, collapsing conditions the source template kept apart.
        # This is `_distinct_branches` for a different connective: a repeated condition says nothing, and the answer
        # is to make it UNREPRESENTABLE rather than to detect it afterwards — the rule `And` and `Or` already hold,
        # and the rule that refuses a CTE nothing reads.
        c = [w for w, _ in self.whens]
        if len(c) != len(set(c)):
            if ENFORCE_DISTINCT: raise Unsupported("a CASE that tests the same condition twice has an unreachable branch")

@dataclass(frozen=True)
class PredVal:
    pred: object        # a predicate used as a value: 1 / 0 / NULL


@dataclass(frozen=True)
class Strftime:
    fmt: str
    expr: object


@dataclass(frozen=True)
class Agg:
    fn: str             # COUNT SUM AVG MAX MIN (or any aggregate name, pass-through)
    arg: object         # None = *
    distinct: bool = False
    filter: object = None   # aggregate FILTER (WHERE pred)


@dataclass(frozen=True)
class Window:
    """A value computed across a set of rows without collapsing them.

    AN AGGREGATE WINDOW MUST BE PARTITIONED, AND THAT IS A RULE ABOUT WHAT ENGLISH CAN SAY.

    `AVG(x) OVER ()` is the mean over the rows that SURVIVE the query's filter and join -- and no phrase
    in a question can convey that, because the reader does not know which rows survived. Meanwhile SQL
    forbids a window in WHERE, so the same idea in a filter has to be built as a CTE over the WHOLE
    table. Two mechanisms, two different row sets, and one English phrase: "its average". Measured
    2026-09-22 on a 900-row corpus -- 111 questions (12%) said "its mean" and "its average" for two
    different numbers, and 253 (28%) computed an unpartitioned window over a filtered set with nothing
    in the words to say so. All three solvers missed those, and sonnet's reading was the better one.

    A PARTITION IS WHAT MAKES IT SAYABLE: "within the same School Type" names the set. Ranking windows
    (RANK, NTILE, PERCENT_RANK) are exempt -- their whole meaning is "among these rows", which the
    phrase says, and they are what R actually spends its windows on.

    AND R NEVER BUILT THIS: 0 of its 108 programs use an unpartitioned aggregate window, against 33% of
    ours. It was never evidence-backed; `pd.derive` put it in the alphabet by hand. So this is not a
    trade between difficulty and clarity -- it removes a shape we invented and R does not have.
    """
    fn: object          # Agg or Func (RANK, ROW_NUMBER, DENSE_RANK, NTILE, LAG …)
    partition: tuple = ()
    order: tuple = ()   # ((Expr, dir), …)

    def __post_init__(self):
        if isinstance(self.fn, Agg) and not self.partition and not self.order:
            raise Unsupported("an unpartitioned aggregate window has no sayable row set")


@dataclass(frozen=True)
class SetOp:
    kind: str           # UNION | INTERSECT | EXCEPT
    left: object        # Program | SetOp
    right: object
    distinct: bool = True
    order: tuple = ()
    limit: object = None
    offset: int = 0
    ctes: tuple = ()

@dataclass(frozen=True)
class Cmp:
    op: str             # = != < <= > >=
    l: object
    r: object

def _distinct_branches(preds, kind):
    """A connective whose branches REPEAT says nothing: `B OR B` is `B`, and a program that asks for a two-branch
    disjunction and gets one is not the program the template asked for. The binder drew the same literal for both
    branches and built it anyway; the renderer then printed the inner group alone and the narrowing check reported a
    rendering fault, when the real fault was upstream in the program. Unrepresentable is cheaper than detected."""
    if len(preds) != len(set(preds)):
        if ENFORCE_DISTINCT: raise Unsupported(f"a {kind} with a repeated branch is degenerate")


@dataclass(frozen=True)
class And:
    preds: tuple
    def __post_init__(self): _distinct_branches(self.preds, "AND")

@dataclass(frozen=True)
class Or:
    preds: tuple
    def __post_init__(self): _distinct_branches(self.preds, "OR")

@dataclass(frozen=True)
class Not:
    pred: object

@dataclass(frozen=True)
class IsNull:
    expr: object
    neg: bool = False

@dataclass(frozen=True)
class Like:
    expr: object
    pattern: object
    neg: bool = False

@dataclass(frozen=True)
class In:
    expr: object
    values: tuple
    neg: bool = False

@dataclass(frozen=True)
class Between:
    expr: object
    lo: object
    hi: object
    neg: bool = False

@dataclass(frozen=True)
class Subq:
    program: object     # a Program used as a scalar (comparison / projection) or as a set (IN)


@dataclass(frozen=True)
class Join:
    alias: str
    table: str
    on: object          # Pred (equalities between aliases) or None for a cross join
    kind: str = "inner" # inner | left

@dataclass(frozen=True)
class Scan:
    alias: str
    table: str
    joins: tuple = ()

@dataclass(frozen=True)
class Program:
    scan: Scan
    where: object = None
    group: tuple = ()
    having: object = None
    select: tuple = ()          # ((Expr, alias|None), …)
    distinct: bool = False
    order: tuple = ()           # ((Expr, "asc"|"desc"), …)
    limit: object = None
    offset: int = 0
    ctes: tuple = ()            # ((name, Program), …) — NAMED INTERMEDIATE RESULTS (09-07): a Scan/Join whose table is a
                                # cte name reads that program's output; a FROM subquery is the same thing named by its alias

    def __post_init__(self):
        """THE DETERMINACY INVARIANT, enforced where the program is BUILT rather than checked after it runs.

        ONE statement covers what were two separate rules. A query COLLAPSES rows when it groups, or when an aggregate
        appears in its result or its group condition — an ungrouped aggregate is just a grouping by the empty tuple.
        In a collapsing query, a result column or sort key that is neither an aggregate nor a grouping key is read from
        an ARBITRARY row of its group: `SELECT molecule_id ... GROUP BY label` answers with whichever molecule SQLite
        met first, and `SELECT name, COUNT(*) FROM t` does the same over the one implicit group. Such a query has no
        determined answer, so it is not a program, and this type does not hold one. No later stage tests for it and
        none can produce it.

        A window function does NOT collapse rows — it is computed per row — so the aggregate inside one is not
        evidence of collapsing, and a bare column beside it stays determined.

        The condition is closed under the ways programs are rebuilt: substituting columns maps equals to equals, so
        membership in the grouping survives it, and appending the sort keys to the select list (which the tie probe
        does) stays inside the invariant precisely because those keys already satisfy it."""
        agg = any(_aggregating(e) for e, _ in self.select)
        # A LIMIT WITH NO ORDERING TAKES AN ARBITRARY SUBSET. `... JOIN ... WHERE gender = 'M' LIMIT 5` returns
        # whichever five rows the engine reaches first: SQLite drove that join from one side and our interpreter from
        # the other, and both were RIGHT — the query simply does not say which five. The tie probe in `certify` only
        # ever ran `if p.limit is not None and p.order`, so a limit with no order at all escaped every check and
        # surfaced as a T1 disagreement, which reads as "our code is broken" when nothing was. An ungrouped aggregate
        # is exempt: it returns exactly one row, so the limit selects nothing.
        if self.limit is not None and not self.order and not (agg and not self.group):
            raise Unsupported("a limit with no ordering selects an arbitrary subset")
        # A NAMED INTERMEDIATE RESULT THAT NOTHING READS IS NOT PART OF THE PROGRAM. It cannot change the answer, but
        # the question must still state it — so the reader is asked to compute a five-table join and a grouping that
        # cannot affect anything. The source's own templates never do this (0 of 75 with a CTE); binding introduced it
        # by renaming the CTEs while a join still pointed at the old name. Refused HERE, where the program is built, so
        # no later stage has to look for it and no binder can emit one.
        if self.ctes:
            # READ means read ANYWHERE in the program: its FROM, a later CTE, or a subquery in any clause -- the
            # same thing SQL means, and what the decoder counts. (Reads inside subqueries were missed.)
            def _reads(prog):
                out = set()
                if isinstance(prog, Program):
                    out |= {str(prog.scan.table).lower()} | {str(j.table).lower() for j in prog.scan.joins}
                    for _n2, _q2 in prog.ctes: out |= _reads(_q2)
                    for sq in _find((prog.select, prog.where, prog.group, prog.having, prog.order), Subq): out |= _reads(sq.program)
                elif isinstance(prog, SetOp):
                    out |= _reads(prog.left) | _reads(prog.right)
                return out
            _seen = {str(self.scan.table).lower()} | {str(j.table).lower() for j in self.scan.joins}
            for sq in _find((self.select, self.where, self.group, self.having, self.order), Subq): _seen |= _reads(sq.program)
            for _n, _q in self.ctes:                            # a CTE may also be read by a LATER CTE
                _seen |= _reads(_q)
            for _n, _ in self.ctes:
                if str(_n).lower() not in _seen:
                    raise Unsupported(f"the intermediate result {_n!r} is computed and never read")
        # DISTINCT COLLAPSES ROWS, SO ITS SORT KEY MUST SURVIVE THE COLLAPSE. `SELECT DISTINCT publisher ... ORDER BY
        # weight` keeps one row per publisher and then orders by a column that had many values per publisher: which one
        # it sorts on is the engine's choice. SQLite answered 'Marvel Comics' and this interpreter answered '', and
        # neither was wrong — the query does not say. A sort key that is not itself projected is therefore not a
        # program here, for the same reason a bare column beside a grouping is not.
        if self.distinct and any(x not in {e for e, _ in self.select} for x, _ in self.order):
            raise Unsupported("DISTINCT with a sort key that is not selected has no determined order")
        keys = tuple(self.group)
        if not (keys or agg or _aggregating(self.having)):
            return
        if any(_has_bare_col(e, keys) for e, _ in self.select + self.order):
            raise Unsupported("result is not determined by the grouping")


    @property
    def aliases(self):
        return [self.scan.alias] + [j.alias for j in self.scan.joins]


# OPTIONAL POLICIES, separate from SQL correctness: a repeated operand (x - x, x / x), a CASE testing one
# condition twice, and a repeated AND/OR branch are valid SQL whose answers do not depend on the repetition. With
# ENFORCE_DISTINCT the IR refuses them at construction; without it they are built, and `specbridge.pd.realize.verify.policies`
# reports them so their selection effect can be measured.
ENFORCE_DISTINCT = False     # x - x, x / x, repeated CASE conditions and branches: usefulness, measured (verify.policies), not enforced in the baseline


class Unsupported(Exception):
    pass


_CLOCK_KW = frozenset("current_timestamp current_date current_time".split())
_CLOCK_FN = frozenset("date time datetime julianday unixepoch".split())


def _has_now(x):
    """a literal SQLite reads as the clock: 'now' and the modifiers that anchor to it, the CURRENT_* KEYWORDS, and a
    date function called with NO argument. Only the first of those is a literal — testing `Const` values alone let
    `STRFTIME('%Y', CURRENT_TIMESTAMP)` through, because the clock is a `Func` node there, not a string."""
    if isinstance(x, Const):
        return isinstance(x.value, str) and x.value.strip().lower() in ("now", "localtime", "utc")
    if isinstance(x, Func):
        nm = (x.name or "").lower()
        if nm in _CLOCK_KW or (not x.args and nm in _CLOCK_FN): return True
    if isinstance(x, (tuple, list)): return any(_has_now(y) for y in x)
    if is_dataclass(x) and not isinstance(x, Program):
        return any(_has_now(getattr(x, f.name)) for f in fields(x))
    if isinstance(x, Program):
        return any(_has_now(getattr(x, f.name)) for f in fields(x) if f.name != "ctes") or any(
            _has_now(q) for _, q in x.ctes)
    return False


def _aggregating(e, _seen=None):
    """Does `e` collapse rows? An aggregate does; a window function does not, and its inner aggregate is not counted.
    A program is a GRAPH -- a reused subexpression is one object in several places -- so each object is visited
    once; walked as a tree, reuse makes this exponential in depth."""
    if e is None or isinstance(e, Window): return False
    if isinstance(e, Agg): return True
    seen = set() if _seen is None else _seen
    if id(e) in seen: return False
    if isinstance(e, (tuple, list)):
        seen.add(id(e)); return any(_aggregating(x, seen) for x in e)
    if is_dataclass(e):
        seen.add(id(e)); return any(_aggregating(getattr(e, f.name), seen) for f in fields(e))
    return False


def nested_aggregate(e, _under=False, _seen=None):
    """Is a plain aggregate nested inside another plain aggregate's argument or filter (SQL: "misuse of aggregate")?
    A window's function is the boundary: `AVG(AVG(x)) OVER (...)` is legal in a grouped query, so the window function's
    argument is walked as if outside any aggregate; its partition and ordering are walked in the enclosing context. A
    subquery is its own scope and is not entered. One definition, read by the checker and the verifier."""
    if e is None: return False
    seen = set() if _seen is None else _seen
    k = (id(e), _under)
    if k in seen: return False
    seen.add(k)
    if isinstance(e, (Subq, Program, SetOp)): return False
    if isinstance(e, Window):
        f = e.fn
        inner = (nested_aggregate(f.arg, False, seen) or nested_aggregate(f.filter, False, seen)) if isinstance(f, Agg) else nested_aggregate(f, _under, seen)
        return inner or nested_aggregate(e.partition, _under, seen) or nested_aggregate(e.order, _under, seen)
    if isinstance(e, Agg):
        return _under or nested_aggregate(e.arg, True, seen) or nested_aggregate(e.filter, True, seen)
    if isinstance(e, (tuple, list)): return any(nested_aggregate(x, _under, seen) for x in e)
    if is_dataclass(e): return any(nested_aggregate(getattr(e, f.name), _under, seen) for f in fields(e))
    return False


def _has_bare_col(e, keys):
    """Is there a column inside `e` that is NOT under an aggregate and NOT itself a grouping key? Such a column is the
    thing an arbitrary row supplies. An expression built only from keys and aggregates is determined by the group."""
    if e in keys: return False
    if isinstance(e, (Agg, Window)): return False
    if isinstance(e, Col): return True
    if isinstance(e, (tuple, list)): return any(_has_bare_col(x, keys) for x in e)
    if is_dataclass(e):
        return any(_has_bare_col(getattr(e, f.name), keys) for f in fields(e))
    return False


def node_types(p) -> set:
    """Which generic node types a program uses — the unit of coverage now (finite, dataset-independent)."""
    if isinstance(p, SetOp):
        out = {"SetOp"} | node_types(p.left) | node_types(p.right)
        for _, sub in p.ctes: out |= node_types(sub)
        return out
    out = {"Scan", "Project"}
    if p.scan.joins: out.add("Join")
    if p.where is not None: out.add("Filter")
    if p.group or any(_has(e, Agg) for e, _ in p.select) or _has(p.having, Agg): out.add("Aggregate")
    if p.group: out.add("Group")          # grouping is its own construct: without this tag a grouped aggregate
                                          # and a whole-table aggregate share a composition, so the sampler draws
                                          # them at their COMBINED rate and the rarer grouped form never surfaces
    if p.having is not None: out.add("Having")
    if p.distinct: out.add("Distinct")
    if p.order: out.add("Sort")
    if p.limit is not None: out.add("Limit")
    walk = [e for e, _ in p.select] + [p.where, p.having] + list(p.group) + [e for e, _ in p.order]
    if p.ctes or any(_has(x, Subq) for x in walk): out.add("Compose")
    for _, sub in p.ctes: out |= node_types(sub)
    if any(_has(x, Case) for x in walk): out.add("Case")
    if any(_has(x, Window) for x in walk): out.add("Window")
    if any(_has(x, Func) for x in walk): out.add("Func")
    for x in walk:
        for sq in _find(x, Subq): out |= node_types(sq.program)
    if any(_has(x, Arith) for x in walk): out.add("Arith")
    if any(_has(x, Cast) for x in walk): out.add("Cast")
    return out


def _find(x, cls):
    if x is None: return []
    out = [x] if isinstance(x, cls) else []
    if isinstance(x, (tuple, list)):
        for y in x: out += _find(y, cls)
    elif hasattr(x, "__dataclass_fields__") and not isinstance(x, cls):
        for f in x.__dataclass_fields__: out += _find(getattr(x, f), cls)
    return out


def _has(x, cls):
    if x is None: return False
    if isinstance(x, cls): return True
    if isinstance(x, (tuple, list)): return any(_has(y, cls) for y in x)
    if hasattr(x, "__dataclass_fields__"):
        return any(_has(getattr(x, f), cls) for f in x.__dataclass_fields__)
    return False


# ---------------------------------------------------------------- lifting: sqlglot AST → Program
_CMP = {exp.EQ: "=", exp.NEQ: "!=", exp.LT: "<", exp.LTE: "<=", exp.GT: ">", exp.GTE: ">="}
_ARITH = {exp.Add: "+", exp.Sub: "-", exp.Mul: "*", exp.Div: "/", exp.Mod: "%"}
_AGG = {exp.Count: "COUNT", exp.Sum: "SUM", exp.Avg: "AVG", exp.Max: "MAX", exp.Min: "MIN"}
_FUNCS = {"ABS", "ROUND", "LENGTH", "UPPER", "LOWER", "SUBSTR", "SUBSTRING", "IIF", "COALESCE"}


WRAPPERS = (exp.Identifier, exp.TableAlias, exp.From, exp.Join, exp.Where, exp.Group, exp.Having, exp.Order, exp.Ordered,
            exp.Limit, exp.Offset, exp.DataType, exp.Paren, exp.Select, exp.Table, exp.Alias, exp.Distinct, exp.Literal,
            exp.Star, exp.Tuple, exp.Var, exp.Null, exp.Boolean, exp.Subquery, exp.With, exp.CTE)


def out_cols(p):
    """output column names of a program (what a consumer sees): alias, else the column's name, else the expression text."""
    return [a or (e.name if isinstance(e, Col) else emit_expr(e)) for e, a in p.select]


class Lifter:
    def __init__(self, schema, consumed=None, depth=0):
        self.schema = dict(schema)      # {table_lower: {"name", "cols", "aff", ["prog"]}} — CTEs are added as pseudo-tables
        self.alias_table = {}           # alias_lower -> real table name (or cte name)
        self.select_alias = {}          # alias_lower -> Expr (for ORDER BY / HAVING by alias)
        self.consumed = consumed if consumed is not None else set()   # id(source AST node) lifted — provenance
        self.depth = depth
        self.ctes = []                  # [(name, Program)] in definition order

    def sub(self, node, name=None):
        """lift a nested SELECT (CTE body / FROM item / value subquery) in its own alias scope, sharing the schema
        (earlier CTEs included) and the provenance set."""
        if self.depth >= 3:
            raise Unsupported("subquery nesting deeper than 3")
        self._c(node)
        inner = node
        while isinstance(inner, (exp.Subquery, exp.Paren)):     # unwrap nested wrappers: IN ((SELECT …))
            self._c(inner); inner = inner.this
        L = Lifter(self.schema, self.consumed, self.depth + 1)
        try:
            return L.program(inner)
        except Unsupported as e:
            raise Unsupported(f"subquery: {e}")

    def generic_func(self, e):
        """Lossless pass-through of any function or opaque scalar expression: Expression arguments are lifted from the
        ORIGINAL node (provenance); units, keywords and paths stay verbatim in a SQLite-rendered template built from a copy."""
        self._c(e)
        args, tmpl = [], e.copy()
        for k in list(e.args.keys()):
            vo, vc = e.args[k], tmpl.args.get(k)
            lo = vo if isinstance(vo, list) else [vo]; lc = vc if isinstance(vc, list) else [vc]
            for xo, xc in zip(lo, lc):
                if isinstance(xo, exp.Expression) and not isinstance(xo, (exp.Var, exp.DataType, exp.Identifier)) \
                        and not (isinstance(xo, exp.Literal) and k in ("unit", "format")):
                    i = len(args); args.append(self.expr(xo))
                    xc.replace(exp.Column(this=exp.Identifier(this=f"__ARG{i}__")))
                elif isinstance(xo, exp.Expression):
                    for n in xo.walk(): self._c(n)
        try:
            text = tmpl.sql(dialect="sqlite")
        except (sqlglot.errors.UnsupportedError, ValueError):
            raise Unsupported(f"function {type(e).__name__.upper()} (cannot render)")
        return Func(e.sql_name().upper() if isinstance(e, exp.Func) else type(e).__name__.upper(), tuple(args), text)

    def register_cte(self, name, prog):
        cols = out_cols(prog)
        self.schema[name.lower()] = {"name": name, "cols": {c.lower(): c for c in cols}, "aff": {c.lower(): "none" for c in cols}, "prog": prog}
        self.ctes.append((name, prog))

    def _c(self, e):
        self.consumed.add(id(e)); return e

    def table(self, t):
        self._c(t)
        if isinstance(t, exp.Subquery):                  # FROM (SELECT …) AS x  ≡  WITH x AS (SELECT …) … FROM x AS x
            if not t.alias:
                raise Unsupported("FROM subquery without alias")
            prog = self.sub(t)
            name = t.alias                               # SCOPE: `(SELECT … FROM trans) AS trans` reads the stored table
            n = 1                                        # inside and names the step outside; the step gets its own name
            while name.lower() in self.schema: n += 1; name = "%s_%d" % (t.alias, n)
            self.register_cte(name, prog)
            self.alias_table[t.alias.lower()] = name
            return t.alias, name
        name = t.name
        real = self.schema.get(name.lower())
        if real is None:
            raise Unsupported(f"unknown table {name}")
        alias = (t.alias or name)
        self.alias_table[alias.lower()] = real["name"]
        return alias, real["name"]

    def col(self, c: exp.Column):
        self._c(c)
        name = c.name
        if c.table:
            al = c.table
            real = self.alias_table.get(al.lower())
            if real is None:
                raise Unsupported(f"unknown alias {al}")
        else:
            cands = [(al, real) for al, real in self.alias_table.items() if name.lower() in self.schema[real.lower()]["cols"]]
            if not cands:
                if name.lower() in self.select_alias:
                    return self.select_alias[name.lower()]
                if c.args.get("this") is not None and getattr(c.this, "quoted", False) and '"' in c.sql():
                    return Const(name)                    # SQLite: a double-quoted name that is no column is a string literal
                raise Unsupported(f"unknown column {name}")
            al, real = cands[0]
        rc = self.schema[real.lower()]["cols"].get(name.lower())
        if rc is None:
            raise Unsupported(f"unknown column {al}.{name}")
        return Col(al, rc, real, self.schema[real.lower()]["aff"].get(name.lower(), "none"))

    def expr(self, e):
        self._c(e)
        if isinstance(e, exp.Paren): return self.expr(e.this)
        if isinstance(e, exp.Column): return self.col(e)
        if isinstance(e, exp.Literal): return Const(_num(e.this) if e.is_number else e.this)
        if isinstance(e, exp.Boolean): return Const(1 if e.this else 0)
        if isinstance(e, exp.Null): return Const(None)
        if isinstance(e, exp.Neg):
            inner = self.expr(e.this)                          # unary minus over a NUMERIC LITERAL is that literal:
            if isinstance(inner, Const) and isinstance(inner.value, (int, float)) and not isinstance(inner.value, bool):
                return Const(-inner.value)                     # lifting it as `0 - x` made every predicate over a
            return Arith("-", Const(0), inner)                 # negative constant opaque, and it is not
        if type(e) in _ARITH: return Arith(_ARITH[type(e)], self.expr(e.left), self.expr(e.right))
        if type(e) in _CMP or isinstance(e, (exp.And, exp.Or, exp.Not, exp.In, exp.Like, exp.Between, exp.Is)):
            return PredVal(self.pred(e))                 # comparison used as a value (SUM(a = b), COUNT(x > 1) …)
        if isinstance(e, exp.TimeToStr) or (isinstance(e, exp.Anonymous) and e.name.upper() == "STRFTIME"):
            if isinstance(e, exp.TimeToStr):
                fmt = e.args["format"]; fmt = fmt.this if isinstance(fmt, exp.Literal) else fmt.sql()
                return Strftime(_sqlite_fmt(fmt), self.expr(e.this))
            args = e.expressions
            return Strftime(args[0].this, self.expr(args[1]))
        if isinstance(e, (exp.TsOrDsToTimestamp, exp.TsOrDsToDate, exp.StrToTime, exp.StrToDate, exp.TsOrDsToDatetime, exp.Date, exp.Datetime)):
            return self.expr(e.this)                     # sqlglot wraps strftime's argument; SQLite keeps the text as is
        if isinstance(e, exp.Cast):
            t = e.to.sql().upper()
            return Cast(self.expr(e.this), "REAL" if "REAL" in t or "FLOAT" in t or "DOUBLE" in t or "NUMERIC" in t or "DECIMAL" in t
                        else "INTEGER" if "INT" in t else "TEXT")
        if type(e) in _AGG:
            fn = _AGG[type(e)]
            arg = e.this
            if isinstance(arg, exp.Star): return Agg(fn, None)
            if isinstance(arg, exp.Distinct):
                inner = arg.expressions[0] if arg.expressions else None
                return Agg(fn, self.expr(inner), True)
            return Agg(fn, self.expr(arg))
        if isinstance(e, exp.Distinct):
            raise Unsupported("DISTINCT outside an aggregate")
        if isinstance(e, exp.Case):
            operand = self.expr(e.this) if e.args.get("this") is not None else None
            if operand is not None:                      # simple CASE: CASE x WHEN v THEN … ≡ CASE WHEN x = v THEN …
                whens = tuple((Cmp("=", operand, self.expr(self._c(w).this)), self.expr(w.args["true"])) for w in e.args.get("ifs", []))
            else:
                whens = tuple((self.pred(self._c(w).this), self.expr(w.args["true"])) for w in e.args.get("ifs", []))   # consume the If wrappers
            return Case(whens, self.expr(e.args["default"]) if e.args.get("default") is not None else None)
        if isinstance(e, exp.If):
            cond = e.this
            pr = self.pred(cond) if not isinstance(cond, (exp.Column, exp.Literal)) else Cmp("!=", self.expr(cond), Const(0))
            return Case(((pr, self.expr(e.args["true"])),), self.expr(e.args["false"]) if e.args.get("false") is not None else None)
        if isinstance(e, (exp.Coalesce, exp.Abs, exp.Round, exp.Length, exp.Upper, exp.Lower, exp.Substring)):
            return self.generic_func(e)
        # AN ATTRIBUTE READ IS AN ATTRIBUTE READ, however the source chose to store it. `blob ->> '$.onlineuse'`
        # MEANS "the onlineuse attribute of this row"; that the source packs its attributes into one column and this
        # target keeps them in separate columns is a STORAGE decision, not part of what the query asks. Lifting it as
        # a function left `json` in the requirement vocabulary — the one role no target supplies — and it blocked 32
        # of LiveSQL's 107 templates outright, all of which place the moment it is gone. Normalised HERE, once, where
        # SQL becomes the algebra, so nothing downstream needs to know: the requirement becomes one more column of
        # whatever role the context wants, and the binder's ordinary search finds it.
        if isinstance(e, (exp.JSONExtract, exp.JSONExtractScalar)):
            col = next((c for c in e.this.find_all(exp.Column)), None) if e.this is not None else None
            path = e.expression.sql(dialect="sqlite").strip("'\"") if e.expression is not None else ""
            field = re.sub(r"[^A-Za-z0-9_]+", "_", path).strip("_") or "attr"
            if col is not None:
                for n in e.walk(): self._c(n)    # the whole access, path nodes included: provenance is total
                base = self.expr(col)
                if isinstance(base, Col):
                    return replace(base, name=f"{base.name}_{field}")
        if isinstance(e, exp.JSONPath):                  # json_extract(col, '$.a.b'): the path is a string literal
            for n in e.walk(): self._c(n)
            t = e.sql(dialect="sqlite")
            return Const(t[1:-1].replace("''", "'") if len(t) >= 2 and t[0] == t[-1] == "'" else t)   # strip the outer quotes once
        if isinstance(e, exp.Window):
            fn = e.this
            if e.args.get("spec") is not None:
                raise Unsupported("window frame specification")
            f = self.expr(fn) if type(fn) in _AGG else Func(fn.sql_name().upper() if not isinstance(fn, exp.Anonymous) else fn.name.upper(),
                                                              tuple(self.expr(x) for x in ([fn.this] if fn.args.get("this") is not None else []) + list(fn.expressions or [])))
            self._c(fn)
            part = tuple(self.expr(x) for x in (e.args.get("partition_by") or []))
            order = tuple((self.expr(o.this), "desc" if o.args.get("desc") else "asc") for o in (e.args["order"].expressions if e.args.get("order") is not None else []))
            if e.args.get("order") is not None: self._c(e.args["order"])
            return Window(f, part, order)
        if isinstance(e, exp.Filter):
            agg = self.expr(e.this)
            if not isinstance(agg, Agg):
                raise Unsupported("FILTER on a non-aggregate")
            self._c(e.expression)
            return Agg(agg.fn, agg.arg, agg.distinct, self.pred(e.expression.this))
        if isinstance(e, exp.Extract):
            raise Unsupported("EXTRACT(field FROM …)")
        if isinstance(e, exp.Anonymous):
            return self.generic_func(e)
        if isinstance(e, exp.Subquery) or isinstance(e, exp.Select):
            return Subq(self.sub(e))                      # scalar subquery as a value
        if isinstance(e, exp.Window):
            raise Unsupported("window function")
        if isinstance(e, exp.Alias):
            return self.expr(e.this)
        if isinstance(e, exp.Star):
            raise Unsupported("SELECT *")
        if isinstance(e, exp.Func):                       # GENERIC PASS-THROUGH: any scalar function
            return self.generic_func(e)
        if isinstance(e, (exp.Interval, exp.DPipe, exp.Bracket, exp.Collate, exp.BitwiseAnd, exp.BitwiseOr)):
            return self.generic_func(e)                  # opaque scalar expressions: same template pass-through
        raise Unsupported(f"expression {type(e).__name__}")

    def pred(self, e):
        self._c(e)
        if isinstance(e, exp.Paren): return self.pred(e.this)
        if isinstance(e, exp.And): return And((self.pred(e.left), self.pred(e.right)))
        if isinstance(e, exp.Or): return Or((self.pred(e.left), self.pred(e.right)))
        if isinstance(e, exp.Not):
            inner = e.this
            if isinstance(inner, exp.In): p = self.pred(inner); return In(p.expr, p.values, True)
            if isinstance(inner, exp.Like): p = self.pred(inner); return Like(p.expr, p.pattern, True)
            if isinstance(inner, exp.Between): p = self.pred(inner); return Between(p.expr, p.lo, p.hi, True)
            return Not(self.pred(inner))
        if type(e) in _CMP:
            return Cmp(_CMP[type(e)], self.expr(e.left), self.expr(e.right))   # a Subq operand is a scalar subquery
        if isinstance(e, exp.Is):
            neg = False
            r = e.right
            if isinstance(r, exp.Not): neg, r = True, r.this
            if isinstance(r, exp.Null): return IsNull(self.expr(e.left), neg)
            raise Unsupported("IS <non-null>")
        if isinstance(e, exp.Like) or isinstance(e, exp.ILike):
            return Like(self.expr(e.this), self.expr(e.expression))
        if isinstance(e, exp.In):
            q = e.args.get("query")
            if q is not None:
                return In(self.expr(e.this), (Subq(self.sub(q)),))
            return In(self.expr(e.this), tuple(Subq(self.sub(x)) if isinstance(x, (exp.Subquery, exp.Select)) else self.expr(x) for x in e.expressions))
        if isinstance(e, exp.Between):
            return Between(self.expr(e.this), self.expr(e.args["low"]), self.expr(e.args["high"]))
        if isinstance(e, exp.Exists):
            raise Unsupported("EXISTS subquery")
        if isinstance(e, exp.Column):                    # bare boolean column
            return Cmp("!=", self.col(e), Const(0))
        if isinstance(e, (exp.Literal, exp.Boolean)):    # WHERE 1 / WHERE TRUE
            return Cmp("!=", self.expr(e), Const(0))
        if isinstance(e, (exp.Subquery, exp.Select, exp.Case, exp.Func)):
            return Cmp("!=", self.expr(e), Const(0))     # any value used as a truth
        raise Unsupported(f"predicate {type(e).__name__}")

    def program(self, t):
        if isinstance(t, (exp.Union, exp.Intersect, exp.Except)):
            self._c(t)
            w = t.args.get("with") if t.args.get("with") is not None else t.args.get("with_")
            if w is not None:
                self._c(w)
                for cte in w.expressions:
                    self._c(cte); self.register_cte(cte.alias, self.sub(cte.this, cte.alias))
            kind = {exp.Union: "UNION", exp.Intersect: "INTERSECT", exp.Except: "EXCEPT"}[type(t)]
            L = Lifter(self.schema, self.consumed, self.depth); left = L.program(t.this)
            R = Lifter(self.schema, self.consumed, self.depth); right = R.program(t.expression)
            order = []
            for o in (t.args["order"].expressions if t.args.get("order") is not None else []):
                self._c(o)
                ex = o.this
                if isinstance(ex, exp.Literal) and ex.is_number:
                    order.append((left.select[int(ex.this) - 1][0], "desc" if o.args.get("desc") else "asc"))
                else:
                    LL = Lifter(self.schema, self.consumed, self.depth); LL.alias_table = dict(L.alias_table); LL.select_alias = dict(L.select_alias)
                    order.append((LL.expr(ex), "desc" if o.args.get("desc") else "asc"))
            lim = t.args.get("limit"); off = t.args.get("offset")
            limit = int(lim.expression.this) if lim is not None and isinstance(lim.expression, exp.Literal) else None
            offset = int(off.expression.this) if off is not None and isinstance(off.expression, exp.Literal) else 0
            return SetOp(kind, left, right, bool(t.args.get("distinct", True)), tuple(order), limit, offset, tuple(self.ctes))
        if not isinstance(t, exp.Select):
            raise Unsupported(f"top-level {type(t).__name__}")
        w = t.args.get("with") if t.args.get("with") is not None else t.args.get("with_")
        if w is not None:                                # named intermediate results, in definition order
            self._c(w)
            if w.args.get("recursive"):
                raise Unsupported("recursive CTE")
            for cte in w.expressions:
                self._c(cte)
                self.register_cte(cte.alias, self.sub(cte.this, cte.alias))
        frm = t.args.get("from_") if t.args.get("from_") is not None else t.args.get("from")   # sqlglot ≥ 27 names it from_
        if frm is None or not isinstance(frm.this, (exp.Table, exp.Subquery)):
            raise Unsupported("no FROM" if frm is None else f"FROM {type(frm.this).__name__}")
        alias, table = self.table(frm.this)
        joins = []
        for j in t.args.get("joins", []) or []:
            if not isinstance(j.this, (exp.Table, exp.Subquery)):
                raise Unsupported(f"JOIN {type(j.this).__name__}")
            ja, jt = self.table(j.this)
            kind = (j.args.get("side") or "inner").lower()
            if (j.args.get("kind") or "").lower() == "cross": kind = "inner"
            if kind not in ("inner", "left", ""):
                raise Unsupported(f"{kind} join")
            on = self.pred(j.args["on"]) if j.args.get("on") is not None else None
            joins.append(Join(ja, jt, on, kind or "inner"))
        scan = Scan(alias, table, tuple(joins))
        where = self.pred(t.args["where"].this) if t.args.get("where") is not None else None
        select = []
        for e in t.expressions:
            if isinstance(e, exp.Star) or (isinstance(e, exp.Column) and isinstance(e.this, exp.Star)):
                raise Unsupported("SELECT *")
            al = e.alias if isinstance(e, exp.Alias) else None
            ex = self.expr(e)
            if al: self.select_alias[al.lower()] = ex
            select.append((ex, al))
        group = tuple(self.expr(g) for g in (t.args["group"].expressions if t.args.get("group") is not None else []))
        having = self.pred(t.args["having"].this) if t.args.get("having") is not None else None
        order = []
        for o in (t.args["order"].expressions if t.args.get("order") is not None else []):
            ex = o.this
            if isinstance(ex, exp.Literal) and ex.is_number:           # ORDER BY 1
                ex_ = select[int(ex.this) - 1][0]
            else:
                ex_ = self.expr(ex)
            order.append((ex_, "desc" if o.args.get("desc") else "asc"))
        lim = t.args.get("limit"); off = t.args.get("offset")
        limit = int(lim.expression.this) if lim is not None and isinstance(lim.expression, exp.Literal) else (None if lim is None else Unsupported("non-literal LIMIT"))
        if isinstance(limit, Unsupported): raise limit
        offset = int(off.expression.this) if off is not None and isinstance(off.expression, exp.Literal) else 0
        prog = Program(scan, where, group, having, tuple(select), bool(t.args.get("distinct")), tuple(order), limit, offset, tuple(self.ctes))
        left = [type(n).__name__ for n in t.walk() if id(n) not in self.consumed and not isinstance(n, WRAPPERS)]
        if left:                                           # LOSSLESSNESS: a semantic source node the tree did not absorb
            raise Unsupported("unconsumed " + ", ".join(sorted(set(left))))
        return prog


def _affinity(decl):
    """SQLite type-affinity rules (§3.1 of the datatype doc)."""
    d = (decl or "").upper()
    if "INT" in d: return "numeric"
    if "CHAR" in d or "CLOB" in d or "TEXT" in d: return "text"
    if not d or "BLOB" in d: return "none"
    if "REAL" in d or "FLOA" in d or "DOUB" in d: return "numeric"
    return "numeric"                                       # NUMERIC affinity (DATE, DECIMAL, BOOLEAN …)


def schema_of(con):
    sch = {}
    for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        info = list(con.execute(f'PRAGMA table_info("{name}")'))
        cols = {c[1].lower(): c[1] for c in info}
        aff = {c[1].lower(): _affinity(c[2]) for c in info}
        sch[name.lower()] = {"name": name, "cols": cols, "aff": aff}
    return sch


def lift(sql: str, con) -> Program:
    t = None
    for d in ("sqlite", "postgres"):
        try:
            t = sqlglot.parse_one(sql, read=d); break
        except sqlglot.errors.ParseError:   # this dialect cannot read it; try the next. Our own bugs still raise.
            continue
    if t is None:
        raise Unsupported("unparsed")
    return _group_as_distinct(_flat_conj(Lifter(schema_of(con)).program(t)))


def _flat_conj(x):
    """`And(And(a, b), c)` IS `And(a, b, c)` — the connective is associative, so the nesting carries no meaning and
    only survives from how the source happened to write its parentheses. It is not free, though: the grammar prints a
    binary AND as "both A and B", so a nested one prints "both both A and B and C" — correct, unambiguous, and written
    by nobody. Flattened here, at the boundary where SQL becomes a program, the renderer sees a three-way conjunction
    and reaches for the list form it already has: "all of the following: A; B; C"."""
    if isinstance(x, (And, Or)):
        kind = type(x)
        parts = []
        for y in (_flat_conj(p) for p in x.preds):
            parts.extend(y.preds if isinstance(y, kind) else [y])
        return kind(tuple(parts))
    if isinstance(x, (tuple, list)): return tuple(_flat_conj(y) for y in x)
    if is_dataclass(x):
        return replace(x, **{f.name: _flat_conj(getattr(x, f.name)) for f in fields(x)})
    return x


def _group_as_distinct(p):
    """`SELECT a, b FROM t GROUP BY a, b` IS `SELECT DISTINCT a, b` — same rows, and grouping collapses NULLs exactly
    as DISTINCT does. 69% of BIRD's grouped programs are this: a grouping used to deduplicate, with no aggregate and
    no condition on the group. Recognising that here means they are DISTINCT programs everywhere downstream, instead of
    grouped ones the renderer then refuses for having "no aggregate in a grouped result"."""
    if not isinstance(p, Program) or not p.group or p.having is not None: return p
    sel = [e for e, _ in p.select]
    if any(_has(e, Agg) or _has(e, Window) for e in sel): return p
    if any(_has(e, Agg) or _has(e, Window) for e, _ in p.order): return p
    if len(sel) != len(p.group) or any(not isinstance(e, Col) for e in sel): return p
    key = lambda c: (c.alias.lower(), c.name)
    if {key(c) for c in sel} != {key(c) for c in p.group if isinstance(c, Col)}: return p
    if any(key(e) not in {key(c) for c in sel} for e, _ in p.order if isinstance(e, Col)): return p
    return replace(p, group=(), distinct=True)          # ordering by anything unselected is left grouped, untouched


# ---------------------------------------------------------------- emitter: node tree → SQL (SQLite)
def qname(x):
    """A table or column name as SQL text, quoted and escaped. ONE of these, for the whole package.

    There were three, and they disagreed about whether the QUOTES were included: `specbridge.pd.structures.algebra` returned
    them, `pd.vouch` did not and left every call site to add its own, `pd.traps` returned them. A helper
    whose convention you must remember is a helper that will be used wrongly, and two of the three had
    already drifted apart in exactly that way.
    """
    return '"' + str(x).replace('"', '""') + '"'


_q = qname


def _lit(v):
    if v is None: return "NULL"
    if _isnum(v): return repr(v) if isinstance(v, float) else str(v)
    return "'" + str(v).replace("'", "''") + "'"


def emit_expr(e):
    if isinstance(e, Col): return f"{_q(e.alias)}.{_q(e.name)}"
    if isinstance(e, Const): return _lit(e.value)
    if isinstance(e, Arith):
        left = emit_expr(e.l)
        # DIVISION IS REAL DIVISION: SQLite truncates a quotient of two integers (7 / 2 is 3), so the dividend is cast
        # to REAL unless it already is (LANGUAGE.md section 7)
        if e.op == "/" and not (isinstance(e.l, Cast) and str(e.l.type).upper() in ("REAL", "FLOAT", "DOUBLE", "NUMERIC")) \
                and not (isinstance(e.l, Const) and isinstance(e.l.value, float)):
            left = f"CAST({left} AS REAL)"
        return f"({left} {e.op} {emit_expr(e.r)})"
    if isinstance(e, Cast): return f"CAST({emit_expr(e.expr)} AS {e.type})"
    if isinstance(e, Func):
        if e.template:
            out = e.template
            for i, a in enumerate(e.args): out = out.replace(f"__ARG{i}__", emit_expr(a))
            return out
        # THE SQLITE DIALECT, in one place: a source's function spelled the way SQLite spells it
        n = e.name.lower()
        if n in ("current_date", "current_timestamp", "now") and not e.args:
            return "CURRENT_DATE" if n == "current_date" else "CURRENT_TIMESTAMP"
        name = {"greatest": "max", "least": "min"}.get(n, e.name)
        return f"{name}({', '.join(emit_expr(a) for a in e.args)})"
    if isinstance(e, Case):
        return "CASE " + " ".join(f"WHEN {emit_pred(pr)} THEN {emit_expr(v)}" for pr, v in e.whens) + (f" ELSE {emit_expr(e.else_)}" if e.else_ is not None else "") + " END"
    if isinstance(e, Agg):
        core = "COUNT(*)" if e.arg is None else f"{e.fn}({'DISTINCT ' if e.distinct else ''}{emit_expr(e.arg)})"
        return core + (f" FILTER (WHERE {emit_pred(e.filter)})" if e.filter is not None else "")
    if isinstance(e, Window):
        inner = emit_expr(e.fn) if isinstance(e.fn, Agg) else f"{e.fn.name}({', '.join(emit_expr(a) for a in e.fn.args)})"
        spec = []
        if e.partition: spec.append("PARTITION BY " + ", ".join(emit_expr(x) for x in e.partition))
        if e.order: spec.append("ORDER BY " + ", ".join(f"{emit_expr(x)} {d.upper()}" for x, d in e.order))
        return f"{inner} OVER ({' '.join(spec)})"
    if isinstance(e, PredVal): return f"({emit_pred(e.pred)})"
    if isinstance(e, Subq): return "(" + emit(e.program) + ")"
    if isinstance(e, Strftime): return f"STRFTIME({_lit(e.fmt)}, {emit_expr(e.expr)})"
    raise TypeError(e)


def emit_pred(p):
    if isinstance(p, Cmp): return f"{emit_expr(p.l)} {p.op} {emit_expr(p.r)}"
    if isinstance(p, And): return "(" + " AND ".join(emit_pred(x) for x in p.preds) + ")"
    if isinstance(p, Or): return "(" + " OR ".join(emit_pred(x) for x in p.preds) + ")"
    if isinstance(p, Not): return f"NOT ({emit_pred(p.pred)})"
    if isinstance(p, IsNull): return f"{emit_expr(p.expr)} IS {'NOT ' if p.neg else ''}NULL"
    if isinstance(p, Like): return f"{emit_expr(p.expr)} {'NOT ' if p.neg else ''}LIKE {emit_expr(p.pattern)}"
    if isinstance(p, In): return f"{emit_expr(p.expr)} {'NOT ' if p.neg else ''}IN ({', '.join(emit_expr(v) for v in p.values)})"
    if isinstance(p, Between): return f"{emit_expr(p.expr)} {'NOT ' if p.neg else ''}BETWEEN {emit_expr(p.lo)} AND {emit_expr(p.hi)}"
    raise TypeError(p)


def emit(p) -> str:
    if isinstance(p, SetOp):
        sql = ("WITH " + ", ".join(f"{_q(n)} AS ({emit(q)})" for n, q in p.ctes) + " ") if p.ctes else ""
        sql += f"{emit(p.left)} {p.kind}{'' if p.distinct else ' ALL'} {emit(p.right)}"
        if p.order: sql += " ORDER BY " + ", ".join(f"{emit_expr(e)} {d.upper()}" for e, d in p.order)
        if p.limit is not None: sql += f" LIMIT {p.limit}" + (f" OFFSET {p.offset}" if p.offset else "")
        return sql
    sql = ("WITH " + ", ".join(f"{_q(n)} AS ({emit(q)})" for n, q in p.ctes) + " ") if p.ctes else ""
    sql += "SELECT " + ("DISTINCT " if p.distinct else "") + ", ".join(emit_expr(e) + (f" AS {_q(a)}" if a else "") for e, a in p.select)
    sql += f" FROM {_q(p.scan.table)} AS {_q(p.scan.alias)}"
    for j in p.scan.joins:
        if j.on is None:
            sql += f" CROSS JOIN {_q(j.table)} AS {_q(j.alias)}"           # a comma/cross join has no ON (round-trips as on=None)
        else:
            sql += f" {'LEFT' if j.kind == 'left' else 'INNER'} JOIN {_q(j.table)} AS {_q(j.alias)} ON {emit_pred(j.on)}"
    if p.where is not None: sql += " WHERE " + emit_pred(p.where)
    if p.group: sql += " GROUP BY " + ", ".join(emit_expr(g) for g in p.group)
    if p.having is not None: sql += " HAVING " + emit_pred(p.having)
    if p.order: sql += " ORDER BY " + ", ".join(f"{emit_expr(e)} {d.upper()}" for e, d in p.order)
    if p.limit is not None: sql += f" LIMIT {p.limit}" + (f" OFFSET {p.offset}" if p.offset else "")
    return sql


def _strip_aliases(p):
    """structural identity modulo select aliases (an emitted alias is syntax, not meaning)."""
    if isinstance(p, SetOp):
        return SetOp(p.kind, _strip_aliases(p.left), _strip_aliases(p.right), p.distinct, p.order, p.limit, p.offset, tuple((n, _strip_aliases(q)) for n, q in p.ctes))
    return Program(p.scan, p.where, p.group, p.having, tuple((e, a) for e, a in p.select), p.distinct, p.order, p.limit, p.offset,
                   tuple((n, _strip_aliases(q)) for n, q in p.ctes))


def _num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


# ---------------------------------------------------------------- the proof: lifted composition vs SQLite on the real DB
def _nz(x):
    """NEGATIVE ZERO IS ZERO. Two implementations that agree on the VALUE can still disagree on the sign of a zero —
    `-117.0 * 0.0` is -0.0 in one and 0.0 in the other — and comparing their printed forms turned that into a T1 halt,
    which asserts that our code is broken. It is not: they agree. This is what `norm` is for, and it already absorbs
    `3` against `3.0`."""
    return 0.0 if x == 0 else x


def norm(rows):
    if rows is None: return None
    out = []
    for r in rows:
        out.append(tuple(str(_nz(round(float(v), 4))) if _isnum(v) else str(v) for v in r))
    return sorted(out)


def run_sqlite(con, sql):
    """Run it. NO TIME LIMIT AND NO STEP LIMIT — a query that takes minutes is a PROBLEM WITH THE PROGRAM WE BUILT,
    and a deadline turns that into "attempt exceeded 2.0s", which names nothing and is counted rather than fixed.
    Without the gate the build stops on the pathological query itself and a stack trace says which one."""
    try:
        return con.execute(sql).fetchall(), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:80]}"


def _isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _sqlite_fmt(fmt):
    """sqlglot rewrites strftime formats into its own tokens (e.g. '%Y' → 'yyyy'); map the common ones back."""
    return {"yyyy": "%Y", "%Y": "%Y", "MM": "%m", "%m": "%m", "dd": "%d", "%d": "%d", "yyyy-MM-dd": "%Y-%m-%d", "%Y-%m-%d": "%Y-%m-%d",
            "yyyy-MM": "%Y-%m", "%Y-%m": "%Y-%m"}.get(fmt, fmt)


def drop_pred(pr, target):
    """The predicate with one leaf removed — an emptied connective disappears with it, so dropping the only leaf of a
    WHERE leaves no WHERE at all. ONE definition: the binder asks what a reader would see if this decision had not
    been made, and the certificate asks the same question by running it."""
    if pr is target: return None
    if isinstance(pr, (And, Or)):
        ps = tuple(x for x in (drop_pred(x, target) for x in pr.preds) if x is not None)
        return None if not ps else (ps[0] if len(ps) == 1 else type(pr)(ps))
    if isinstance(pr, Not):
        inner = drop_pred(pr.pred, target)
        return None if inner is None else Not(inner)
    return pr


def swap_pred(pr, old, new):
    if pr is old: return new
    if isinstance(pr, (And, Or)): return type(pr)(tuple(swap_pred(x, old, new) for x in pr.preds))
    if isinstance(pr, Not): return Not(swap_pred(pr.pred, old, new))
    return pr


