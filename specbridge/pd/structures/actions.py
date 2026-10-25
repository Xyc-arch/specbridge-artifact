"""specbridge.pd.structures.actions — THE ACTION VOCABULARY OF P; A PROGRAM AS ONE SEQUENCE OF IT; P AS COUNTS OVER IT; AND ONE
DECODER THAT TURNS ACTIONS BACK INTO A PROGRAM, whether the actions come from a recorded sequence (the
round trip) or from P (the sampler).

A token is a semantic construction action, never a SQL word, a table, a column or a target value. The
IR (`specbridge.pd.structures.algebra`) fixes which actions are possible at each position; fitting on R learns how often each
is taken there. What the target supplies is left as a SLOT: a relation, a column of a computational
type, a data value, a threshold, a constant in a column's unit. What is meaning is kept: the operator,
the nesting, and a REFERENCE to something already introduced -- so `(x-y)/x` is DIVIDE, SUBTRACT,
slot A, slot B, REF(A), and the reuse of A is part of the pattern.

    families            tokens
    query               QUERY  SETOP  RELATION  STEP_REL(i)  INNER LEFT CROSS  ALL DISTINCT  ASC DESC  LIMIT NONE
    expression          COL:NUM COL:TEXT COL:DATE COL:KEY COL:ANY  LIT(role)  ARITH  AGG  CASE  WINDOW  SUBQUERY
                        FUNC  CAST  STRFTIME  PREDVAL  STAR  STEP_OUT(step, output)  REF(distance)
    operators           ADD SUBTRACT MULTIPLY DIVIDE MOD  COUNT SUM AVG MAX MIN AGG:name  EQ NE LT LE GT GE
                        AND OR NOT ISNULL LIKE IN BETWEEN EXISTS  RANK ROW_NUMBER DENSE_RANK NTILE WIN:name
    literal roles       DATA_VALUE  DATA_THRESHOLD  UNIT_PARAM  FORMULA_PARAM  CLOCK  TOP_K  PARAM
    list boundary       MORE / STOP

EVERY LITERAL IS A PARAMETER, and the role says who fills it. WHAT P MEASURES IS THE ABSTRACT PROGRAM, AND
EVERY DECISION P MAKES IS IN THE EMITTED PROGRAM: no decision is later overwritten by the binder. So a role
whose value the target supplies carries NO value decision -- DATA_VALUE and DATA_THRESHOLD are bare slots,
and an ARITHMETIC CONSTANT -- UNIT_PARAM (beside a bare column) or FORMULA_PARAM (beside a computed
expression) -- is a PARAMETER SLOT that decides only its KIND (`const_kinds`: ZERO, WHOLE, REFERENCE, CONVERT,
WEIGHT); the target binds its value by the kind's declared rule, and the source's number is kept as evidence
beside the law, never as a decision (2026-09-26: before this, FORMULA_PARAM copied the source's number, and 80%
of arithmetic constants on a target were numbers nothing in the target explained). TOP_K (the k asked for) and
PARAM (a function's argument) ARE decisions, with their values, because their values are in the emitted
program. CLOCK is the snapshot. The role of an
arithmetic constant is DIMENSIONAL, read off R (2026-09-24, every arithmetic constant with its sibling's
kind): beside a BARE COLUMN an added or subtracted constant is in that column's unit (`ambictemp - 20.0`,
`1 - transparency`, `100 - successrate`) and so is a divisor (`coverpct / 100`, `dlyflow / 1000`); a
multiplier is a dimensionless weight (`0.3 * assets`), and any constant beside a COMPUTED expression is
part of the formula (`1 - (x / y)`, `ratio * 100`).

DIVISION HAS ONE CONVENTION, NOT A DECISION. SQLite returns NULL for any division by zero, so `NULLIF(y, 0)`
in a denominator changes nothing and is read as the plain denominator; the contract states "missing when the
denominator is zero" once. SQLite truncates an integer quotient (7 / 2 is 3), so the compiler casts to REAL.

WHICH STEPS ARE INLINED, exactly (`grammar.inline_lets`): a step with no GROUP, no aggregate or window in
its output, no HAVING, no LIMIT, no DISTINCT and no steps of its own only names per-row expressions; the
outer query reads the expressions instead. Every step that summarises, cuts or ranks stays. `sequence` is
the one door, so a source program, a target gold and a sampled program are all read under the same rule.

THE CONDITIONING STATE OF P, exactly. A decision's context is
    (parent token, slot, position in the list, arithmetic depth, the query's MODE, references available
     capped at 3, whether a step is in the query's FROM)
for an expression, plus the LEFT OPERAND'S TOKEN for the right operand of an arithmetic node. The mode is
"collapsed" once the query groups or an aggregate stands in its output, "row" once a bare column does,
"undecided" before either, "free" outside the output clauses -- the determinacy rule of the IR, known from
the prefix. A REF then decides WHAT it reuses -- OUT, one of this query's outputs; KEY, a grouping key; ANY,
something else by distance -- so "the sort key is an output" is a habit P learns, not a distance that
happens to land there. A list boundary is (parent, slot, position, the query's role) and the joins also
carry whether the base is a step. Nothing of the source's database is in any of it. A fitted count is
looked up by the full context and backs off through its prefixes, then a pool by slot.

THE STRUCTURAL MASKS are the IR's own rules applied at the decision (the Decoder's `allow`): the
determinacy rule above, a REF needs an admissible target, every step is read, a LIMIT needs an ordering,
an aggregate window needs a partition or ordering, a constant opposite a constant is not an expression,
STAR only under COUNT, lists have R's minima and maxima, nesting and depth have R's caps. On R they
exclude 11 of 12,000 decisions (six reads of a step output the step never lists, one LIMIT without an
ordering, one constant times a constant, one subquery as a denominator, two step reads), each a single
occurrence and listed by the report as "outside".

    python -m specbridge.pd.structures.actions [source] [n]   # the vocabulary on R; the round trip; n samples from P against R
"""
from __future__ import annotations
import collections, math, random, re, sys

from specbridge.pd.structures.algebra import (Agg, And, Arith, Between, Case, Cast, Cmp, Col, Const, Func, In, IsNull, Join, Like, Not,
                      Or, PredVal, Program, Scan, SetOp, Strftime, Subq, Window, Unsupported)

MORE, STOP = "MORE", "STOP"
POS_CAP, AVAIL_CAP = 16, 3
_ARITH = {"+": "ADD", "-": "SUBTRACT", "*": "MULTIPLY", "/": "DIVIDE", "%": "MOD"}
_SYM = {v: k for k, v in _ARITH.items()}
_CMP = {"=": "EQ", "!=": "NE", "<>": "NE", "<": "LT", "<=": "LE", ">": "GT", ">=": "GE"}
_CMPSYM = {"EQ": "=", "NE": "!=", "LT": "<", "LE": "<=", "GT": ">", "GE": ">="}
_RANKS = {"RANK", "ROW_NUMBER", "DENSE_RANK", "NTILE", "PERCENT_RANK"}
_AGGS = ("COUNT", "SUM", "AVG", "MAX", "MIN")
_NUM_KINDS = {"count", "money", "measure", "score", "share", "percent", "thousands", "duration", "rank"}
_TYPES = ("NUM", "TEXT", "DATE", "KEY", "ANY")
_PASS = {"coalesce", "abs", "round", "nullif", "ifnull", "greatest", "least", "ceil", "ceiling", "floor"}
VALUED = ("UNIT_PARAM", "FORMULA_PARAM", "SCORE", "TOP_K", "PARAM")     # roles with a decision of their own: a KIND for the two arithmetic roles, a value for TOP_K and PARAM
COMPOUND = {"ARITH", "AGG", "CASE", "WINDOW", "FUNC", "CAST", "STRFTIME", "SUBQUERY", "PREDVAL"}
ROLES = ("DATA_VALUE", "DATA_THRESHOLD", "UNIT_PARAM", "FORMULA_PARAM", "SCORE", "CLOCK", "TOP_K", "PARAM")
KINDED = ("UNIT_PARAM", "FORMULA_PARAM", "SCORE")      # parameter slots: P decides a KIND, the target binds the value
LITS = {"LIT:" + r for r in ROLES}
LEAVES = {"STAR", "REF", "STEP_OUT"} | LITS | {"COL:" + t for t in _TYPES}
MINIMUM = {("QUERY", "select"): 1, ("CASE", "whens"): 1, ("IN", "values"): 1, ("AND", "preds"): 2, ("OR", "preds"): 2}


def col_type(c, typer=None):
    """The computational type of a column slot: NUM, TEXT, DATE, KEY or ANY. A slot the decoder made carries
    its type as its affinity; a source column is typed from its documentation's kind, else its affinity."""
    if c.aff in _TYPES: return c.aff
    k = str(typer.kind(c)).split()[0] if typer is not None else "?"
    if k == "id": return "KEY"
    if k == "date": return "DATE"
    if k in _NUM_KINDS: return "NUM"
    if k in ("label", "text", "category", "name", "flag"): return "TEXT"
    return {"numeric": "NUM", "text": "TEXT"}.get(c.aff, "ANY")


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _looks_date(v):
    return isinstance(v, str) and bool(re.match(r"^\d{4}-\d{2}-\d{2}", v))


def _bare(e):
    """A stored column, possibly cast or passed through a function that keeps its unit."""
    while True:
        if isinstance(e, Cast): e = e.expr
        elif isinstance(e, Func) and e.name.lower() in _PASS and e.args: e = e.args[0]
        else: break
    return isinstance(e, Col)


def _unguard(r):
    """`NULLIF(y, 0)` as a denominator is `y` under the one division convention."""
    if isinstance(r, Func) and r.name.lower() == "nullif" and len(r.args) == 2 and \
            isinstance(r.args[1], Const) and r.args[1].value in (0, 0.0):
        return r.args[0]
    return r


def slot_roles(par, slot, leftnode=None):
    """THE INVERSE OF `Seq._role`: the literal roles a constant can have at this slot, so the checker offers
    exactly the roles the encoder would assign. One definition of roles, read two ways; the round trip on R tests that
    they agree. `leftnode` is the left operand when the slot is the right of an arithmetic node."""
    if par.startswith("ARITH:"):
        op = par.split(":")[1]
        if slot == "r":
            if leftnode is None or isinstance(leftnode, Const): return set()      # a constant expression
            unit = _bare(leftnode) and op in ("ADD", "SUBTRACT", "DIVIDE")
            return {"CLOCK", "UNIT_PARAM" if unit else "FORMULA_PARAM"}
        # on the left: + and * put a constant on the right (canonical), - decides the right's class by role
        return {"SUBTRACT": {"UNIT_PARAM", "FORMULA_PARAM", "CLOCK"}}.get(op, {"FORMULA_PARAM", "CLOCK"} if op in ("DIVIDE", "MOD") else set())
    if par == "LIMIT": return {"TOP_K"}
    if par == "CMP": return set() if slot == "l" else {"DATA_THRESHOLD", "DATA_VALUE"}   # the column side first
    if par == "BETWEEN": return {"DATA_THRESHOLD", "DATA_VALUE"}
    if par in ("IN", "LIKE"): return {"DATA_VALUE"}
    if par == "CASE" and slot in ("then", "else"): return {"SCORE"}
    return {"PARAM"}


FACTORS = (7, 12, 24, 30, 60, 100, 365, 1000)      # the conversion factors of the declared table (catalogue.CONVERSIONS)
def _placeholder(kind, n):
    """A value for a parameter in a program built without a database: of its kind (so it reads back as that kind)
    and distinct per draw, so two parameters never make two expressions equal that the program kept apart."""
    return {"ZERO": 0, "ONE": 1, "WHOLE": 100, "CONVERT": FACTORS[n % len(FACTORS)], "WEIGHT": 1000.5 + n,
            "LABEL": "label%d" % n}.get(kind, 1000 + n)


CLOCK_FUNCS = {"current_date", "current_timestamp", "now", "current_time"}
WINDOW_FUNCS = {"rank", "dense_rank", "row_number", "ntile", "percent_rank", "cume_dist", "lag", "lead", "first_value", "last_value"}


def reads_data(e):
    """Does an expression depend on the rows: a column, a step output, an aggregate, a window, a subquery?"""
    from specbridge.pd.structures.algebra import _has, Agg, Window, Subq
    return any(_has(e, k) for k in (Col, Agg, Window, Subq))


def const_kinds(par, side, role):
    """The kinds an arithmetic constant may take at (operator, side, role) -- the universe of its decision.
    A constant is a PARAMETER SLOT: P decides its kind, the target binds its value by the kind's declared rule
    (`Binder.constant`), and no source number reaches a target program.
        ZERO       0                         (+, -)
        WHOLE      the whole of the operand's unit, 1 for a share, 100 for a percentage (left of -: a complement)
        REFERENCE  the operand's typical value, read from the rows  (+, -; and the divisor of a bare column)
        CONVERT    a factor from the operand's unit to another unit, from the declared table (right of * and /)
        WEIGHT     a dimensionless number the question states (* and /, and %)
    and a CASE result constant (role SCORE) is ZERO, ONE (together: an indicator), SCORE (a number of a scoring
    rule the question states) or LABEL (text, which a target does not take from the source)."""
    if role == "SCORE": return {"ZERO", "ONE", "SCORE", "LABEL"}
    op = par.split(":")[1] if par.startswith("ARITH:") else ""
    if op in ("ADD", "SUBTRACT"):
        return {"ZERO", "REFERENCE"} | ({"WHOLE"} if op == "SUBTRACT" and side == "l" else set())
    if op in ("MULTIPLY", "DIVIDE") and side == "r":
        return {"CONVERT", "REFERENCE" if (op == "DIVIDE" and role == "UNIT_PARAM") else "WEIGHT"}
    return {"WEIGHT"}


def const_kind(par, side, role, value):
    """The kind of a constant read from a program: the one reading of `const_kinds` a value admits."""
    op = par.split(":")[1] if par.startswith("ARITH:") else ""
    ks = const_kinds(par, side, role)
    try: v = float(value) if not isinstance(value, bool) else None
    except Exception: v = None
    if role == "SCORE": return "LABEL" if v is None else "ZERO" if v == 0 else "ONE" if v == 1 else "SCORE"
    if "ZERO" in ks and v == 0: return "ZERO"
    if "WHOLE" in ks and v in (1.0, 100.0): return "WHOLE"
    if "CONVERT" in ks and v in FACTORS: return "CONVERT"
    if "REFERENCE" in ks: return "REFERENCE"
    return "WEIGHT"




def _conj(p):
    """A WHERE or HAVING as its conjuncts, flattened at every depth: an AND inside an AND is the same list."""
    if p is None: return ()
    if not isinstance(p, And): return (p,)
    return tuple(x for q in p.preds for x in _conj(q))


# ================================================================ encoding: a program as a sequence
class Seq:
    """One program's canonical action sequence: (context, action) pairs. A REF's distance, a step index, a
    step's output and a literal's value are decisions in contexts of their own, right after the action that
    needs them. Also records what the caps are fitted from: list lengths and nesting."""

    def __init__(self, typer=None):
        self.typer, self.out = typer, []
        self.intro, self.steps = [], []          # objects introduced in this scope; (name, program) of steps
        self.nest, self.maxnest, self.maxlen = 0, 0, collections.Counter()
        self.evidence = []                       # (context, value, sibling kind) of every UNIT_PARAM: the fill's evidence
        self.outputs, self.keys = [], []         # this query's select expressions so far, and its grouping keys
        self.mode, self.in_agg, self.in_window = "free", 0, 0   # the decoder's mode, computed the same way as it goes

    def emit(self, ctx, action):
        self.out.append((ctx, action))

    def _ctx(self, par, slot, pos, d, left):
        return (par, slot, min(pos, POS_CAP), d, self.mode, min(len(self.intro), AVAIL_CAP), self.has_step) + ((left,) if left is not None else ())

    @property
    def has_step(self):
        """Is a step of this query in its FROM? The encoder reads it off the scan; the decoder off its reads."""
        q = self.current
        names = [n for n, _q in self.steps]
        return any(str(t).lower() in names for t in [q.scan.table] + [j.table for j in q.scan.joins])

    @property
    def relaxed(self):
        return self.in_agg and not self.in_window

    def _settle(self, e):
        """An undecided query is settled by the first thing its output shows: an aggregate collapses it, a
        bare column keeps it per-row."""
        if self.mode == "undecided" and not self.relaxed:
            from specbridge.pd.structures.algebra import _aggregating, _find
            self.mode = "collapsed" if _aggregating(e) else ("row" if _find(e, Col) else self.mode)

    def _ref(self, ctx, e):
        """A REF names WHAT it reuses: OUT, one of this query's outputs (1 = the latest); KEY, a grouping key;
        ANY, an object by its distance back. That is what makes "the sort key is an output" a learnable habit."""
        for i in range(len(self.intro) - 1, -1, -1):
            if self.intro[i] == e:
                self.emit(ctx, "REF")
                outs = [k for k, o in enumerate(self.outputs) if o == e]; keys = [k for k, o in enumerate(self.keys) if o == e]
                kind = "OUT" if outs else "KEY" if keys else "ANY"
                self.emit(("REF", "kind", ctx[0], self.mode), kind); self._settle(e)
                if kind == "OUT": self.emit(("REF", "OUT", min(len(self.outputs), AVAIL_CAP)), len(self.outputs) - outs[-1])
                elif kind == "KEY": self.emit(("REF", "KEY", min(len(self.keys), AVAIL_CAP)), keys[-1])
                else:
                    others = [k for k, o in enumerate(self.intro) if not any(o == x for x in self.outputs) and not any(o == x for x in self.keys)]
                    self.emit(("REF", "ANY", min(len(others), AVAIL_CAP)), len(others) - others.index(i))
                return True
        return False

    def _step_of(self, c):
        names = [n for n, _q in self.steps]
        for key in (str(c.table).lower(), str(c.alias).lower()):
            if key in names: return names.index(key)
        return None

    def _output(self, st, c):
        q = self.steps[st][1]
        if isinstance(q, SetOp): return -1
        name = str(c.name).lower()
        for i, (x, alias) in enumerate(q.select):
            if (alias and str(alias).lower() == name) or (not alias and isinstance(x, Col) and str(x.name).lower() == name):
                return i
        return -1

    def _kind(self, e):
        return str(self.typer.kind(e)).split()[0] if self.typer is not None and e is not None else "?"

    def _role(self, par, side, sib, value):
        if par.startswith("ARITH"):
            if _looks_date(value): return "CLOCK"
            op, bare = par.split(":")[1], _bare(sib)
            if bare and op in ("ADD", "SUBTRACT"): return "UNIT_PARAM"
            if bare and op == "DIVIDE" and side == "r": return "UNIT_PARAM"
            return "FORMULA_PARAM"
        if par == "LIMIT": return "TOP_K"
        if par in ("CMP", "BETWEEN"): return "DATA_THRESHOLD" if _is_number(value) or _looks_date(value) else "DATA_VALUE"
        if par in ("IN", "LIKE"): return "DATA_VALUE"
        if par == "CASE" and side in ("then", "else"): return "SCORE"
        return "PARAM"

    def expr(self, e, par, slot, d=0, pos=0, left=None, sib=None):
        ctx = self._ctx(par, slot, pos, d, left)
        if e is None:
            self.emit(ctx, "STAR"); return "STAR"
        if isinstance(e, Const):
            role = self._role(par, slot, sib, e.value)
            self.emit(ctx, "LIT:" + role)
            if role in KINDED:
                self.emit((par, slot, role), const_kind(par, slot, role, e.value))
                self.evidence.append(((par, slot), e.value, self._kind(sib)))      # the source's number: evidence, not a decision
            elif role in VALUED: self.emit((par, slot, role), e.value)
            return "LIT"
        if not isinstance(e, Col) and self._ref(ctx, e): return "REF"
        if isinstance(e, Col):
            if self._ref(ctx, e): return "REF"
            st = self._step_of(e)
            if st is not None:
                q = self.steps[st][1]
                self.emit(ctx, "STEP_OUT"); self.emit(("STEP_OUT", "step", len(self.steps)), st)
                self.emit(("STEP_OUT", "out", min(len(q.select), POS_CAP) if isinstance(q, Program) else 0), self._output(st, e))
                self.intro.append(e); self._settle(e); return "STEP_OUT"
            t = "COL:" + col_type(e, self.typer)
            self.emit(ctx, t); self.intro.append(e); self._settle(e); return t
        self.nest += 1; self.maxnest = max(self.maxnest, self.nest)
        try:
            if isinstance(e, Arith):
                op = _ARITH[e.op]; l_, r = e.l, _unguard(e.r) if e.op == "/" else e.r
                # CANONICAL: a constant stands on the RIGHT of + and *, so a constant's role is decided by an
                # operand already built. On the left of - it stays, and the decoder constrains its right.
                if e.op in "+*" and isinstance(l_, Const) and not isinstance(r, Const): l_, r = r, l_
                self.emit(ctx, "ARITH"); self.emit(("ARITH", "op", d), op)
                l = self.expr(l_, "ARITH:" + op, "l", d + 1, sib=r)
                self.expr(r, "ARITH:" + op, "r", d + 1, left=l, sib=l_)
                self.intro.append(e); return "ARITH"
            if isinstance(e, Agg):
                fn = e.fn.upper()
                self.emit(ctx, "AGG")
                if self.mode == "undecided" and not self.in_window: self.mode = "collapsed"
                self.emit(("AGG", "fn", d), fn if fn in _AGGS else "AGG:" + fn.lower())
                self.emit(("AGG", "distinct"), "DISTINCT" if e.distinct else "ALL")
                self.in_agg += 1
                self.expr(e.arg, "AGG:" + fn, "arg", 0)
                if e.filter is not None: self.emit(("AGG", "filter"), "PRED"); self.pred(e.filter, "AGG", "filter")
                else: self.emit(("AGG", "filter"), "NONE")
                self.in_agg -= 1
                self.intro.append(e); return "AGG"
            if isinstance(e, Window):
                self.emit(ctx, "WINDOW")
                if isinstance(e.fn, Func):
                    name = e.fn.name.upper()
                    self.emit(("WINDOW", "fn"), name if name in _RANKS else "WIN:" + name.lower())
                    self.list(e.fn.args, "WINDOW:" + name, "args", lambda x, i: self.expr(x, "WINDOW:" + name, "arg", 0, i))
                else:
                    self.emit(("WINDOW", "fn"), "AGG"); self.in_window += 1; self.expr(e.fn, "WINDOW", "agg", 0); self.in_window -= 1
                self.list(e.partition, "WINDOW", "partition", lambda x, i: self.expr(x, "WINDOW", "partition", 0, i))
                self.list(e.order, "WINDOW", "order", lambda x, i: self.key(x, "WINDOW", i))
                self.intro.append(e); return "WINDOW"
            if isinstance(e, Case):
                self.emit(ctx, "CASE")
                def when(w, i):
                    self.pred(w[0], "CASE", "when"); self.expr(w[1], "CASE", "then", d, i)
                self.list(e.whens, "CASE", "whens", when)
                if e.else_ is not None: self.emit(("CASE", "else"), "ELSE"); self.expr(e.else_, "CASE", "else", d)
                else: self.emit(("CASE", "else"), "NONE")
                self.intro.append(e); return "CASE"
            if isinstance(e, Func):
                name = e.name.lower()
                self.emit(ctx, "FUNC"); self.emit(("FUNC", "name"), name)
                self.list(e.args, "FUNC:" + name, "args", lambda x, i: self.expr(x, "FUNC:" + name, "arg", d, i))
                self.intro.append(e); return "FUNC"
            if isinstance(e, Cast):
                self.emit(ctx, "CAST"); self.emit(("CAST", "type"), e.type.upper()); self.expr(e.expr, "CAST", "expr", d)
                return "CAST"
            if isinstance(e, Strftime):
                self.emit(ctx, "STRFTIME"); self.emit(("STRFTIME", "fmt"), e.fmt); self.expr(e.expr, "STRFTIME", "expr", d)
                self.intro.append(e); return "STRFTIME"
            if isinstance(e, Subq):
                self.emit(ctx, "SUBQUERY"); self.program(e.program, "SUBQUERY"); return "SUBQUERY"
            if isinstance(e, PredVal):
                self.emit(ctx, "PREDVAL"); self.pred(e.pred, "PREDVAL", "pred"); return "PREDVAL"
            if isinstance(e, (Program, SetOp)):
                self.emit(ctx, "SUBQUERY"); self.program(e, "SUBQUERY"); return "SUBQUERY"
            raise Unsupported("no action for a %s" % type(e).__name__)
        finally:
            self.nest -= 1

    def pred(self, p, par, slot, pos=0):
        ctx = (par, slot, min(pos, POS_CAP))
        if isinstance(p, Cmp):
            self.emit(ctx, "CMP"); self.emit(("CMP", "op"), _CMP.get(p.op, p.op))
            l, r = (p.r, p.l) if isinstance(p.l, Const) and not isinstance(p.r, Const) else (p.l, p.r)
            self.expr(l, "CMP", "l", 0); self.expr(r, "CMP", "r", 0)
        elif isinstance(p, (And, Or)):
            k = "AND" if isinstance(p, And) else "OR"
            self.emit(ctx, k); self.list(p.preds, k, "preds", lambda x, i: self.pred(x, k, "preds", i))
        elif isinstance(p, Not):
            self.emit(ctx, "NOT"); self.pred(p.pred, "NOT", "pred")
        elif isinstance(p, IsNull):
            self.emit(ctx, "ISNULL"); self.emit(("ISNULL", "neg"), "NOT" if p.neg else "IS"); self.expr(p.expr, "ISNULL", "expr", 0)
        elif isinstance(p, Like):
            self.emit(ctx, "LIKE"); self.emit(("LIKE", "neg"), "NOT" if p.neg else "IS")
            self.expr(p.expr, "LIKE", "expr", 0); self.expr(p.pattern, "LIKE", "pattern", 0)
        elif isinstance(p, In):
            self.emit(ctx, "IN"); self.emit(("IN", "neg"), "NOT" if p.neg else "IS"); self.expr(p.expr, "IN", "expr", 0)
            if len(p.values) == 1 and isinstance(p.values[0], (Subq, Program, SetOp)):
                self.emit(("IN", "values"), "SUBQUERY"); self.program(getattr(p.values[0], "program", p.values[0]), "SUBQUERY")
            else:
                self.emit(("IN", "values"), "LIST"); self.list(p.values, "IN", "values", lambda x, i: self.expr(x, "IN", "value", 0, i))
        elif isinstance(p, Between):
            self.emit(ctx, "BETWEEN"); self.emit(("BETWEEN", "neg"), "NOT" if p.neg else "IS")
            self.expr(p.expr, "BETWEEN", "expr", 0); self.expr(p.lo, "BETWEEN", "lo", 0); self.expr(p.hi, "BETWEEN", "hi", 0)
        elif isinstance(p, (Subq, Program)):
            self.emit(ctx, "EXISTS"); self.program(getattr(p, "program", p), "SUBQUERY")
        else:
            self.emit(ctx, "EXPR"); self.expr(p, "PRED", "expr", 0)

    def list(self, items, par, slot, each, role=(), flag=None):
        self.maxlen[(par, slot)] = max(self.maxlen[(par, slot)], len(items))
        tail = lambda: role + ((flag(),) if flag else ())
        for i, x in enumerate(items):
            self.emit((par, slot, min(i, POS_CAP)) + tail(), MORE); each(x, i)
        self.emit((par, slot, min(len(items), POS_CAP)) + tail(), STOP)

    def key(self, k, par, i):
        e, direction = k
        self.expr(e, par, "order", 0, i); self.emit((par, "dir"), direction.upper())

    def relation(self, name, par, slot, i=0, role=None):
        n = str(name).lower(); names = [k for k, _q in self.steps]
        ctx = (par, slot, min(i, POS_CAP), bool(names)) + ((role,) if role is not None else ())
        if n in names: self.emit(ctx, "STEP_REL"); self.emit(("STEP_REL", len(names)), names.index(n)); self.consumed.add(n)
        else: self.emit(ctx, "RELATION")

    def program(self, p, par="ROOT"):
        if isinstance(p, SetOp):
            self.emit((par, "query"), "SETOP"); self.emit(("SETOP", "kind"), p.kind.upper())
            self.emit(("SETOP", "distinct"), "DISTINCT" if p.distinct else "ALL")
            self.program(p.left, "SETOP"); self.program(p.right, "SETOP")
            return
        self.emit((par, "query"), "QUERY")
        outer = (self.intro, self.steps, self.outputs, self.keys, self.mode, self.in_agg, self.in_window, getattr(self, "current", None), getattr(self, "clause", None))
        self.intro, self.steps, self.outputs, self.keys, self.mode, self.in_agg, self.in_window, self.current = [], list(self.steps), [], [], "free", 0, 0, p
        if not hasattr(self, "consumed"): self.consumed = set()
        def step(nq, i):
            name, q = nq
            saved = (self.intro, self.outputs, self.keys, self.mode, self.in_agg, self.in_window, self.current)
            self.intro, self.outputs, self.keys, self.mode, self.in_agg, self.in_window = [], [], [], "free", 0, 0
            self.program(q, "STEP")
            self.intro, self.outputs, self.keys, self.mode, self.in_agg, self.in_window, self.current = saved; self.steps.append((str(name).lower(), q))
        role = (par,)
        self.list(p.ctes, "QUERY", "steps", step, role)
        self.relation(p.scan.table, "QUERY", "from", role=par)
        names = [n for n, _q in self.steps]
        base_is_step = str(p.scan.table).lower() in names
        own = {n for n, _q in self.steps[len(self.steps) - len(p.ctes):]}
        unread = lambda: any(n not in self.consumed for n in own)
        def join(j, i):
            self.relation(j.table, "JOIN", "rel", i, role=unread())
            self.emit(("JOIN", "kind"), "CROSS" if j.on is None else j.kind.upper())
        # JOINS ARE KEPT IN THE ORDER WRITTEN. An earlier canonical order put unread steps first; that was a
        # decoder convenience, and it lost every step that D could reach only through a table joined before it.
        joins = list(p.scan.joins)                  # in the order written: SQL already makes each ON refer backwards
        self.list(joins, "QUERY", "joins", join, role + (base_is_step,), unread)
        self.clause = "where"
        self.list(_conj(p.where), "QUERY", "where", lambda x, i: self.pred(x, "WHERE", "pred", i), role)
        self.clause = None
        self.list(p.group, "QUERY", "group", lambda x, i: self.expr(x, "GROUP", "expr", 0, i), role)
        self.keys = list(p.group); self.mode = "collapsed" if p.group else "undecided"
        self.emit(("QUERY", "distinct", par), "DISTINCT" if p.distinct else "ALL")
        def out(x, i):
            self.expr(x[0], "SELECT", "expr", 0, i); self.outputs.append(x[0])
        self.list(p.select, "QUERY", "select", out, role)
        if self.mode == "undecided": self.mode = "row"
        self.list(_conj(p.having), "QUERY", "having", lambda x, i: self.pred(x, "HAVING", "pred", i), role)
        self.list(p.order, "QUERY", "order", lambda x, i: self.key(x, "ORDER", i), role)
        if p.limit is None: self.emit(("QUERY", "limit", par), "NONE")
        else:
            self.emit(("QUERY", "limit", par), "LIMIT")
            self.expr(p.limit if isinstance(p.limit, Const) else Const(p.limit), "LIMIT", "k", 0)
        self.intro, self.steps, self.outputs, self.keys, self.mode, self.in_agg, self.in_window, self.current, self.clause = outer


def encode(p, typer=None, lets=False):
    """The Seq of a program, let-binding steps inlined unless `lets`."""
    if not lets:
        from specbridge.pd.structures.grammar import inline_lets
        try: p = inline_lets(p)
        except Exception: pass
    s = Seq(typer); s.program(p); return s


def sequence(p, typer=None, lets=False):
    """The canonical action sequence of a program."""
    return encode(p, typer, lets).out


# ================================================================ decoding: actions back into a program
def _aggregating(e):
    from specbridge.pd.structures.algebra import _aggregating as agg
    return agg(e)


def _leaf_cols(e):
    from specbridge.pd.structures.algebra import _find
    return _find(e, Col)


class NotInLanguage(Exception):
    """An action outside the universe the language states at its decision: nothing to interpret."""


class CheckerBug(Exception):
    """The checker offered an action outside the universe: a defect of `specbridge.pd.realize.check`, never of the program."""


Decision = collections.namedtuple("Decision", "ctx universe allow")

EXPRS = LEAVES | COMPOUND
PREDS = {"CMP", "AND", "OR", "NOT", "ISNULL", "LIKE", "IN", "BETWEEN", "EXISTS", "EXPR"}
_CLOSED = {("ARITH", "op"): set(_SYM), ("AGG", "distinct"): {"ALL", "DISTINCT"}, ("AGG", "filter"): {"PRED", "NONE"},
           ("CASE", "else"): {"ELSE", "NONE"}, ("IN", "values"): {"LIST", "SUBQUERY"},
           ("JOIN", "kind"): {"INNER", "LEFT", "CROSS"}, ("SETOP", "distinct"): {"ALL", "DISTINCT"},
           ("QUERY", "distinct"): {"ALL", "DISTINCT"}, ("QUERY", "limit"): {"NONE", "LIMIT"},
           ("QUERY", "query"): {"QUERY", "SETOP"}}
NEG, DIRS = {"IS", "NOT"}, {"ASC", "DESC"}


class Decoder:
    """INTERPRETS an action sequence into a program. At every decision it states the UNIVERSE -- every action
    the language has there, which it can interpret -- asks the checker (`specbridge.pd.realize.check`) for the admissible subset,
    and hands both to the chooser as a `Decision`. The chooser may replay a recorded sequence (the round trip),
    draw from P (the sampler).

    Errors are specific. An action outside the universe raises NotInLanguage. The IR's own construction rules
    raise Unsupported. The checker offering an action outside the universe raises CheckerBug. Any other
    exception is a defect of the decoder and is never caught as a verdict about a program.

    The state (LANGUAGE.md §4) is kept here because interpreting an action is what changes it; the checker
    only reads it. Open decisions (a function's name, a literal's value, an aggregate's name) have universe
    None: the vocabulary there is whatever the source wrote."""

    def __init__(self, choose, caps=None, checker=None, binder=None, explain=False):
        from specbridge.pd.realize.check import Checker
        self.explain = explain
        self.choose, self.caps, self.check, self.binder = choose, caps or {}, checker or Checker(), binder
        self.scope, self.joined, self.cmp_left, self.pending_on = [], [], None, None
        self.frames = []          # the operators open above the current slot, innermost last: what the checker judges a candidate in
        self.intro, self.steps, self.n, self.nest = [], [], 0, 0
        self.maxdepth, self.maxnest = self.caps.get("depth", 99), self.caps.get("nest", 99)
        self.mode, self.groupkeys, self.in_agg, self.in_window, self.read, self.targets = "free", [], 0, 0, set(), None
        self.outputs, self.mine, self.exclude, self.item_nest, self.consumed = [], set(), [], -1, set()
        self.clause, self.nulltested, self.need, self.nulltest = None, [], None, False

    def act(self, ctx, universe, allow=None):
        self._fill_cache = {}
        self.last_why, self._why = self.__dict__.get("_why", {}), {}
        self.decisions = getattr(self, "decisions", 0) + 1
        self.max_open = max(getattr(self, "max_open", 0), self.open_depth())
        cap = self.caps.get("size", 10 ** 9)
        # the size cap is an OPTIONAL policy; without it a runaway guard at four times R's longest program remains
        if self.decisions > (cap if getattr(self, "enforce_size", True) else 4 * cap):
            raise Unsupported(("longer than any program in the source (%d decisions)" % cap) if getattr(self, "enforce_size", True)
                              else "runaway: four times the longest source program")
        if callable(allow):                                   # a rule over an open vocabulary
            a = self.choose(Decision(ctx, universe, allow))
            if not allow(a): raise NotInLanguage("%r refused at %r" % (a, ctx))
            return a
        if allow is not None and universe is not None and not set(allow) <= universe:
            raise CheckerBug("%r offered %r outside the universe" % (ctx, set(allow) - universe))
        a = self.choose(Decision(ctx, universe, universe if allow is None else set(allow)))
        if universe is not None and a not in universe: raise NotInLanguage("%r at %r" % (a, ctx))
        return a

    def _ctx(self, par, slot, pos, d, left):
        return (par, slot, min(pos, POS_CAP), d, self.mode, min(len(self.intro), AVAIL_CAP), bool(self.read)) + ((left,) if left is not None else ())

    def fresh(self, t):
        self.n += 1; return Col("?", "c%d" % self.n, "", t)

    def intro_node(self, e):
        """A finished node equal to one already introduced IS that object: two derivations of one program
        (build it again, or refer to it) are merged, never discarded. Returns the object to use."""
        for x in self.intro:
            if x == e: return x
        self.intro.append(e); return e

    @property
    def relaxed(self):
        """Inside an aggregate's argument (not a window's) a bare column is fine and a nested aggregate is not."""
        return self.in_agg and not self.in_window

    # ---- the universe: what the language has at a decision
    def ref_lists(self):
        """The objects a REF may name, by kind, as the encoder classifies them: this query's outputs, its
        grouping keys, and everything else introduced. Only introduced objects can be named (§3 REF)."""
        intro = lambda o: any(o is x for x in self.intro)
        outs = [o for o in self.outputs if intro(o)]
        keys = [o for o in self.groupkeys if intro(o) and not any(o is x for x in self.outputs)]
        others = [o for o in self.intro if not any(o is x for x in self.outputs) and not any(o is x for x in self.groupkeys)]
        return outs, keys, others

    def ref_targets(self):
        outs, keys, others = self.ref_lists(); return outs + keys + others

    def step_universe(self):
        return {k for k, (_n, q) in enumerate(self.steps) if isinstance(q, Program) and q.select}

    def universe_expr(self, par, slot, d):
        if (par, slot) == ("LIMIT", "k"): return {"LIT:TOP_K"}
        if (par, slot) == ("WINDOW", "agg"): return {"AGG"}
        u = set(EXPRS)
        if (par, slot) != ("AGG:COUNT", "arg"): u.discard("STAR")
        if d >= self.maxdepth: u.discard("ARITH")
        if self.nest >= self.maxnest: u -= COMPOUND
        if not self.ref_targets(): u.discard("REF")
        if not self.step_universe(): u.discard("STEP_OUT")
        return u

    # ---- interpretation
    def _explain_refs(self, universe, allow, target_of, forbid):
        """Record, for each reuse the checker removed, the condition that removed it -- only when asked for."""
        if not getattr(self, "explain", False): return
        why = self.__dict__.setdefault("_why", {})
        for x in set(universe) - set(allow or ()):
            e = target_of(x)
            if e is not None: why.setdefault(x, self.check.ref_reason(self, e, forbid, self.need) or "other")

    def _ref(self, par, forbid):
        e = self._ref_target(par, forbid)
        # THE DEPTH A REUSE REACHES, in the units legality charges it (open depth + the reused object's own depth), so
        # the cap fitted from R (`fit`) and the cap checked at a REF (`check.ok_target`) measure the same thing
        self.max_open = max(getattr(self, "max_open", 0), self.open_depth() + depth_units(e))
        return e

    def _ref_target(self, par, forbid):
        self.ref_par = par
        outs, keys, others = self.ref_lists()
        uk = {k for k, xs in (("OUT", outs), ("KEY", keys), ("ANY", others)) if xs}
        ak = self.check.ref_kinds(self, uk, forbid)
        first = {"OUT": outs, "KEY": keys, "ANY": others}
        self._explain_refs(uk, ak, lambda k: first[k][0] if first[k] else None, forbid)
        kind = self.act(("REF", "kind", par, self.mode), uk, ak)
        if kind == "OUT":
            u = {len(self.outputs) - k for k, o in enumerate(self.outputs) if any(o is x for x in outs)}
            am = self.check.ref_members(self, kind, forbid)
            self._explain_refs(u, am, lambda m: self.outputs[len(self.outputs) - m], forbid)
            return self.outputs[len(self.outputs) - self.act(("REF", "OUT", min(len(self.outputs), AVAIL_CAP)), u, am)]
        if kind == "KEY":
            u = {k for k, o in enumerate(self.groupkeys) if any(o is x for x in keys)}
            am = self.check.ref_members(self, kind, forbid)
            self._explain_refs(u, am, lambda m: self.groupkeys[m], forbid)
            return self.groupkeys[self.act(("REF", "KEY", min(len(self.groupkeys), AVAIL_CAP)), u, am)]
        u = set(range(1, len(others) + 1))
        am = self.check.ref_members(self, kind, forbid)
        self._explain_refs(u, am, lambda m: others[len(others) - m], forbid)
        return others[len(others) - self.act(("REF", "ANY", min(len(others), AVAIL_CAP)), u, am)]

    def expr(self, par, slot, d=0, pos=0, left=None, leftnode=None):
        ctx = self._ctx(par, slot, pos, d, left)
        forbid = leftnode if par.split(":")[-1] in ("SUBTRACT", "DIVIDE") and slot == "r" else None
        u = self.universe_expr(par, slot, d)
        a = self.act(ctx, u, self.check.expr(self, u, left, forbid, leftnode, par, slot, d))
        if a == "STAR": return None, a
        if a.startswith("LIT:"):
            role = a[4:]; kind = None
            if role in KINDED:
                uu = const_kinds(par, slot, role)
                kind = self.act((par, slot, role), uu, self.check.const_kind(self, uu, par, slot, leftnode, role, d))
                self.n += 1
                if self.binder: v = self.binder.constant(self, kind, par, slot, leftnode, role)   # on the left: re-bound against the right
                else: v = _placeholder(kind, self.n)
            elif role in VALUED: v = self.act((par, slot, role), None, self.check.parameter(self, role))
            elif self.binder:
                v = {"DATA_THRESHOLD": lambda: self.binder.threshold(self, self.cmp_left),
                     "DATA_VALUE": lambda: self.binder.value(self, self.cmp_left),
                     "CLOCK": self.binder.clock}.get(role, lambda: "?")()
            else:
                self.n += 1
                v = {"DATA_THRESHOLD": self.n, "CLOCK": "2000-01-%02d" % (self.n % 28 + 1)}.get(role, "?%d" % self.n)
            self.lit_info = (role, kind)
            c = Const(v)
            if self.binder and kind:
                self.binder.kinds[id(c)] = (role, kind, c)
                if kind == "REFERENCE" and getattr(self.binder, "_ref_ok", False): self.binder.grounded[id(c)] = c
            return c, "LIT"
        if a == "REF":
            e = self._ref(par, forbid); self.need = None
            if self.mode == "undecided" and not self.relaxed: self.mode = "collapsed" if _aggregating(e) else ("row" if _leaf_cols(e) else self.mode)
            return e, a
        if a == "STEP_OUT":
            st = self.act(("STEP_OUT", "step", len(self.steps)), self.step_universe(), self.check.step_steps(self))
            q = self.steps[st][1]
            o = self.act(("STEP_OUT", "out", min(len(q.select), POS_CAP)), set(range(len(q.select))), self.check.step_outs(self, st))
            if self.mode == "undecided" and not self.relaxed: self.mode = "row"
            nm = self.steps[st][0]; self.need = None
            c = Col(nm, "o%d" % o, nm, "ANY"); self.intro.append(c)
            return c, a
        if a.startswith("COL:"):
            self.need = None
            c = self.binder.column(self, a[4:], par, slot, leftnode) if self.binder else self.fresh(a[4:])
            self.intro.append(c)
            if self.mode == "undecided" and not self.relaxed: self.mode = "row"
            return c, a
        self.nest += 1
        nframes = len(self.frames)
        # MEANING IS NOT DECIDED HERE: each compound opens a frame for the operator it builds, and the one checker
        # (specbridge.pd.realize.semantics) judges every candidate in the frames open above it
        if a in ("WINDOW", "SUBQUERY", "PREDVAL", "STRFTIME"): self.frames.append(("STOP",))
        # a class requirement passes through CAST and a unit-preserving function to its (first) argument,
        # because that is where `_bare` looks; any other compound satisfies "compound" and ends it
        if a not in ("CAST", "FUNC"): self.need = None
        try:
            if a == "ARITH":
                op = self.act(("ARITH", "op", d), _CLOSED[("ARITH", "op")], self.check.arith_ops(self, d))
                saved_need, self.need = self.need, None
                self.frames.append(("ARITH", _SYM[op], "l", None))
                l, lt = self.expr("ARITH:" + op, "l", d + 1)
                linfo = self.lit_info if isinstance(l, Const) else None   # read NOW: the right operand may draw constants of its own
                # the role of a left constant fixes its right operand (LANGUAGE.md §7)
                if op == "SUBTRACT" and linfo:
                    self.need = {"UNIT_PARAM": "bare", "FORMULA_PARAM": "compound"}.get(linfo[0])
                if self.binder:                                            # the right is judged against the left as drawn
                    sem = self.binder.cat.sem
                    partner = sem.const("WHOLE") if linfo and linfo[1] == "WHOLE" else sem.record(l, dict(self.steps))
                else: partner = None
                self.frames[-1] = ("ARITH", _SYM[op], "r", partner)
                r, _ = self.expr("ARITH:" + op, "r", d + 1, left=lt, leftnode=l)
                self.frames.pop()
                rinfo = self.lit_info if isinstance(r, Const) else None
                self.need = saved_need
                if self.binder and linfo and linfo[1]:
                    l = Const(self.binder.constant(self, linfo[1], "ARITH:" + op, "l", r, linfo[0]))   # a left parameter is bound against its right
                    self.binder.kinds[id(l)] = (linfo[0], linfo[1], l)
                    if linfo[1] == "REFERENCE" and getattr(self.binder, "_ref_ok", False): self.binder.grounded[id(l)] = l
                e = self.intro_node(Arith(_SYM[op], l, r)); return e, a
            if a == "AGG":
                if self.mode == "undecided" and not self.in_window: self.mode = "collapsed"
                fn = self.act(("AGG", "fn", d), None); fn = fn[4:] if fn.startswith("AGG:") else fn
                dis = self.act(("AGG", "distinct"), _CLOSED[("AGG", "distinct")])
                self.in_agg += 1
                self.frames.append(("AGG", fn.upper(), dis == "DISTINCT", bool(self.in_window)))
                arg, _ = self.expr("AGG:" + fn.upper(), "arg", 0)
                self.frames.pop()
                closes_as = Agg(fn, arg, dis == "DISTINCT", None)
                repeat = self.nest - 1 == self.item_nest and any(closes_as == x for x in self.exclude)
                f = self.act(("AGG", "filter"), _CLOSED[("AGG", "filter")], {"PRED"} if repeat else None)
                self.in_filter = getattr(self, "in_filter", 0) + 1      # state only: the binder reports triviality here
                try: flt = self.pred("AGG", "filter") if f == "PRED" else None
                finally: self.in_filter -= 1
                self.in_agg -= 1
                e = self.intro_node(Agg(fn, arg, dis == "DISTINCT", flt)); return e, a
            if a == "WINDOW":
                self.win_def = getattr(self, "win_def", 0) + 1
                try: return self._window(d, a)
                finally: self.win_def -= 1
            if a == "CASE":
                def whens_of(f):
                    def when(i):
                        p = f(self.pred("CASE", "when")); x, _ = self.expr("CASE", "then", d, i); return (p, x)
                    return self.list("CASE", "whens", when)
                self.frames.append(("CASE",))                              # a branch's value passes to the CASE's result
                whens = tuple(self.sibling_list(whens_of))
                el = self.act(("CASE", "else"), _CLOSED[("CASE", "else")])
                els = self.expr("CASE", "else", d)[0] if el == "ELSE" else None
                self.frames.pop()
                e = self.intro_node(Case(whens, els)); return e, a
            if a == "FUNC":
                name = self.act(("FUNC", "name"), None, self.check.func_name(self, par))
                if name.lower() not in _PASS: self.need = None
                need, self.need = self.need, None
                def arg(i):
                    if i == 0: self.need = need
                    n = len(self.frames); self.frames.append(("FUNC", name.lower(), i))
                    try: x = self.expr("FUNC:" + name, "arg", d, i)[0]
                    finally: del self.frames[n:]
                    self.need = None; return x
                args = tuple(self.list("FUNC:" + name, "args", arg))
                e = self.intro_node(Func(name, args)); return e, a
            if a == "CAST":
                t = self.act(("CAST", "type"), None, self.check.cast_type(self))
                n = len(self.frames); self.frames.append(("CAST", t))
                try: x, _ = self.expr("CAST", "expr", d)
                finally: del self.frames[n:]
                self.need = None
                return Cast(x, t), a
            if a == "STRFTIME":
                fmt = self.act(("STRFTIME", "fmt"), None); x, _ = self.expr("STRFTIME", "expr", d)
                e = self.intro_node(Strftime(fmt, x)); return e, a
            if a == "SUBQUERY":
                return Subq(self.program("SUBQUERY")), a
            if a == "PREDVAL":
                return PredVal(self.pred("PREDVAL", "pred")), a
            raise AssertionError("an expression action with no interpretation: %s" % a)
        finally:
            self.nest -= 1; del self.frames[nframes:]

    def _window(self, d, a):
            fn = self.act(("WINDOW", "fn"), None)
            if fn == "AGG":
                self.in_window += 1; f, _ = self.expr("WINDOW", "agg", 0); self.in_window -= 1
            else:
                name = fn[4:].upper() if fn.startswith("WIN:") else fn
                f = Func(name, tuple(self.list("WINDOW:" + name, "args", lambda i: self.expr("WINDOW:" + name, "arg", 0, i)[0])))
            part = tuple(self.distinct_list("WINDOW", "partition", lambda i: self.expr("WINDOW", "partition", 0, i)[0], item=("WINDOW", "partition")))
            order = tuple(self.distinct_list("WINDOW", "order", lambda i: self.key("WINDOW", i), lo=1 if isinstance(f, Func) or not part else 0, item=("WINDOW", "order")))
            e = self.intro_node(Window(f, part, order)); return e, a

    def pred(self, par, slot, pos=0):
        self.pdepth = getattr(self, "pdepth", 0) + 1
        n = len(self.frames); self.frames.append(("STOP",))            # a predicate's operands start a new context
        try: return self._pred(par, slot, pos)
        finally: self.pdepth -= 1; del self.frames[n:]                  # by length: a failed subquery leaves no frames to pop

    def open_depth(self):
        return self.nest + getattr(self, "pdepth", 0)

    def _pred(self, par, slot, pos=0):
        ctx = (par, slot, min(pos, POS_CAP))
        u = PREDS - {"AND"} if par in ("WHERE", "HAVING") else PREDS
        a = self.act(ctx, u, self.check.preds(self, u))
        if a == "CMP":
            op = self.act(("CMP", "op"), set(_CMPSYM))
            outer = (getattr(self, "cmp_left", None), getattr(self, "cmp_op", None))   # a comparison nested in another's operand
            n = len(self.frames); self.frames.append(("CMP", None, _CMPSYM[op]))      # the operator judges the left too
            try: l, _ = self.expr("CMP", "l", 0)
            finally: del self.frames[n:]
            self.cmp_left, self.cmp_op = l, op
            n = len(self.frames); self.frames.append(("CMP", self.binder.record_of(self, l) if self.binder else None, _CMPSYM[op]))
            try: r, _ = self.expr("CMP", "r", 0)
            finally: del self.frames[n:]
            self.cmp_left, self.cmp_op = outer                   # restored, not cleared: the outer comparison's value binds against ITS left
            return Cmp(_CMPSYM[op], l, r)
        if a in ("AND", "OR"):
            saved, self.nulltested = self.nulltested, []
            self.loose = getattr(self, "loose", 0) + (a == "OR")     # under an OR or a NOT a condition need not hold for a row
            try: ps = tuple(self.sibling_list(lambda f: self.list(a, "preds", lambda i: f(self.pred(a, "preds", i)))))
            finally: self.loose -= (a == "OR")
            self.nulltested = saved
            return And(ps) if a == "AND" else Or(ps)
        if a == "NOT":
            self.loose = getattr(self, "loose", 0) + 1
            try: return Not(self.pred("NOT", "pred"))
            finally: self.loose -= 1
        if a == "ISNULL":
            neg = self.act(("ISNULL", "neg"), NEG)
            self.nulltest = True
            x, _ = self.expr("ISNULL", "expr", 0)
            self.nulltest = False; self.nulltested.append(x)
            return IsNull(x, neg == "NOT")
        if a == "LIKE":
            neg = self.act(("LIKE", "neg"), NEG); x, _ = self.expr("LIKE", "expr", 0)
            self.cmp_left = x; pat, _ = self.expr("LIKE", "pattern", 0); self.cmp_left = None
            return Like(x, pat, neg == "NOT")
        if a == "IN":
            neg = self.act(("IN", "neg"), NEG); x, _ = self.expr("IN", "expr", 0); kind = self.act(("IN", "values"), _CLOSED[("IN", "values")])
            self.cmp_left = x
            if kind == "SUBQUERY": vals = (Subq(self.program("SUBQUERY")),)
            else:
                n = len(self.frames); self.frames.append(("CMP", self.binder.record_of(self, x) if self.binder else None, "="))
                try: vals = tuple(self.list("IN", "values", lambda i: self.expr("IN", "value", 0, i)[0]))
                finally: del self.frames[n:]
            self.cmp_left = None
            return In(x, vals, neg == "NOT")
        if a == "BETWEEN":
            neg = self.act(("BETWEEN", "neg"), NEG)
            n = len(self.frames); self.frames.append(("CMP", None, "BETWEEN"))
            try: x, _ = self.expr("BETWEEN", "expr", 0)
            finally: del self.frames[n:]
            self.cmp_left = x
            n = len(self.frames); self.frames.append(("CMP", self.binder.record_of(self, x) if self.binder else None, "BETWEEN"))
            try:
                lo, _ = self.expr("BETWEEN", "lo", 0)
                self.between_lo = lo; hi, _ = self.expr("BETWEEN", "hi", 0)
            finally: del self.frames[n:]
            self.cmp_left = None; self.between_lo = None
            return Between(x, lo, hi, neg == "NOT")
        if a == "EXISTS": return Subq(self.program("SUBQUERY"))
        return self.expr("PRED", "expr", 0)[0]

    def slot_allow(self, par, slot, d=0):
        """The admissible first actions of an expression slot, computed without building anything."""
        u = self.universe_expr(par, slot, d)
        return self.check.expr(self, u, None, None, None, par, slot, d)

    def list(self, par, slot, each, lo=None, more_only=None, role=(), flag=None, item=None, can=None):
        items, lo, hi = [], MINIMUM.get((par, slot), 0) if lo is None else lo, self.caps.get((par, slot), self.caps.get("list", 99))
        while True:
            i = len(items)
            u = {MORE, STOP} - ({MORE} if i >= hi else set())
            if item: can = lambda: bool(self.slot_allow(*item))
            a = self.act((par, slot, min(i, POS_CAP)) + role + ((flag(),) if flag else ()), u, self.check.list(self, u, i, lo, more_only, can))
            if a == STOP: return items
            items.append(each(i))

    def key(self, par, i):
        e, _ = self.expr(par, "order", 0, i); direction = self.act((par, "dir"), DIRS); self.exclude.append(e); return (e, direction.lower())

    def distinct_list(self, par, slot, each, **kw):
        """A list whose items may not repeat an object: an output, a key, a sort key, a partition."""
        saved = (self.exclude, self.item_nest); self.exclude, self.item_nest = [], self.nest
        try: return self.list(par, slot, lambda i: self._noted(each(i)), **kw)
        finally: self.exclude, self.item_nest = saved

    def _noted(self, item):
        self.exclude.append(item[0] if isinstance(item, tuple) else item); return item

    def relation(self, par, slot, i=0, room=99, role=None):
        u = {"RELATION", "STEP_REL"} if self.steps else {"RELATION"}
        allow, members = self.check.relation(self, u, par, room)
        a = self.act((par, slot, min(i, POS_CAP), bool(self.steps)) + ((role,) if role is not None else ()), u, allow)
        if a == "STEP_REL":
            k = self.act(("STEP_REL", len(self.steps)), set(range(len(self.steps))), members)
            self.read.add(k); self.consumed.add(self.steps[k][0])
            if self.binder and par == "JOIN": self.pending_on = self.binder.step_on(self, k)
            return self.steps[k][0]
        if self.binder:
            if par == "JOIN":
                t, (lt, lc, rt, rc) = self.rng_pick(self.binder.feasible_links(self, room) or self.binder.links(self))
                self.pending_on = Cmp("=", Col(lt, lc, lt, "KEY"), Col(rt, rc, rt, "KEY"))
            else:
                t = self.binder.base(self)
            self.scope.append(t); return t
        self.n += 1; return "t%d" % self.n

    def sibling_list(self, build):
        """A list whose items are predicates that must differ (a conjunction, a disjunction, a CASE's
        conditions): each finished item is recorded, so a binding that would repeat one is not offered."""
        self.siblings = getattr(self, "siblings", [])
        self.siblings.append([])
        def note(p):
            self.siblings[-1].append(p); return p
        try: return build(note)
        finally: self.siblings.pop()

    def join_possible(self, cap):
        """MORE on the join list is feasible exactly when the next relation decision has an admissible binding:
        the same question the relation decision will ask, asked first."""
        u = {"RELATION", "STEP_REL"} if self.steps else {"RELATION"}
        allow, members = self.check.relation(self, u, "JOIN", cap - len(self.joined))
        return bool(allow - {"STEP_REL"}) or ("STEP_REL" in allow and bool(members))

    def _noted_where(self, p):
        self.where_so_far.append(p); return p

    def rng_pick(self, xs):
        return self.binder.rng.choice(xs)

    def program(self, par="ROOT"):
        a = self.act((par, "query"), _CLOSED[("QUERY", "query")])
        if a == "SETOP":
            kind = self.act(("SETOP", "kind"), None); dis = self.act(("SETOP", "distinct"), _CLOSED[("SETOP", "distinct")])
            l = self.program("SETOP"); r = self.program("SETOP")
            return SetOp(kind, l, r, dis == "DISTINCT")
        saved = (self.intro, self.steps, self.mode, self.groupkeys, self.in_agg, self.read, self.in_window, self.targets, self.outputs, self.mine, self.exclude, self.clause, self.nulltested, getattr(self, "role", "ROOT"), getattr(self, "distinct", False))
        saved_scope = (self.scope, self.joined, self.cmp_left, getattr(self, "base", None), getattr(self, "where_so_far", []))
        saved_frames, self.frames = self.frames, []
        self.role, self.distinct = par, False
        self.intro, self.steps, self.mode, self.groupkeys, self.in_agg, self.read = [], list(self.steps), "free", [], 0, set()
        self.in_window, self.targets, self.outputs, self.exclude, self.clause, self.nulltested = 0, None, [], [], None, []
        def step(i):
            inner = (self.intro, self.mode, self.groupkeys, self.in_agg); self.intro, self.mode, self.groupkeys, self.in_agg = [], "free", [], 0
            q = self.program("STEP")
            self.intro, self.mode, self.groupkeys, self.in_agg = inner
            self.n += 1; name = "s%d" % self.n; self.steps.append((name, q)); return (name, q)
        first, role = len(self.steps), (par,)
        ctes = tuple(self.list("QUERY", "steps", step, role=role))
        self.scope, self.joined, self.cmp_left = [], [], None
        mine = self.mine = {n for n, _q in self.steps[first:]}
        cap = self.caps.get(("QUERY", "joins"), self.caps.get("list", 99))
        base = self.relation("QUERY", "from", room=cap + 1, role=par); self.base = base
        base_is_step = base in {n for n, _q in self.steps}
        unread = lambda: bool(mine - self.consumed)
        def join(i):
            self.pending_on = None
            t = self.relation("JOIN", "rel", i, room=cap - i, role=unread())
            u = _CLOSED[("JOIN", "kind")]
            # the join's kind follows its binding: a key link joins INNER or LEFT; no link is a CROSS join
            allow = None if not self.binder else ({"CROSS"} if self.pending_on is None else {"INNER", "LEFT"})
            kind = self.act(("JOIN", "kind"), u, allow)
            if self.binder: on = None if kind == "CROSS" else self.pending_on
            else: on = None if kind == "CROSS" else Cmp("=", Col(base, "k", base, "KEY"), Col(t, "k", t, "KEY"))
            j = Join(t, t, on, kind.lower() if kind != "CROSS" else "inner"); self.joined.append(j); return j
        joins = tuple(self.list("QUERY", "joins", join, more_only=unread, role=role + (base_is_step,), flag=unread,
                                can=(lambda: self.join_possible(cap)) if self.binder else None))
        self.clause, self.nulltested, self.where_so_far = "where", [], []
        where = self.sibling_list(lambda f: self.list("QUERY", "where", lambda i: self._noted_where(f(self.pred("WHERE", "pred", i))), role=role))
        self.clause = None
        self.clause = "group"
        group = tuple(self.distinct_list("QUERY", "group", lambda i: self.expr("GROUP", "expr", 0, i)[0], role=role, item=("GROUP", "expr")))
        self.clause = None
        self.groupkeys = list(group); self.mode = "collapsed" if group else "undecided"
        dis = self.act(("QUERY", "distinct", par), _CLOSED[("QUERY", "distinct")]); self.distinct = dis == "DISTINCT"
        def out(i):
            e = self.expr("SELECT", "expr", 0, i)[0]; self.outputs.append(e); return (e, "o%d" % i)
        select = tuple(self.distinct_list("QUERY", "select", out, role=role, item=("SELECT", "expr")))
        if self.mode == "undecided": self.mode = "row"
        self.clause = "having"
        having = self.sibling_list(lambda f: self.list("QUERY", "having", lambda i: f(self.pred("HAVING", "pred", i)), role=role,
                                                         can=lambda: self.mode == "collapsed"))
        self.clause = None
        self.has_having = bool(having)
        if dis == "DISTINCT": self.targets = [e for e, _a in select]
        order = tuple(self.distinct_list("QUERY", "order", lambda i: self.key("ORDER", i), role=role, item=("ORDER", "order"),
                                         lo=1 if self.check.must_cut(self) else 0))
        self.targets = None
        u = _CLOSED[("QUERY", "limit")]
        lim = self.act(("QUERY", "limit", par), u, self.check.limit(self, u, bool(order)))
        limit = self.expr("LIMIT", "k", 0)[0].value if lim == "LIMIT" else None
        self.intro, self.steps, self.mode, self.groupkeys, self.in_agg, self.read, self.in_window, self.targets, self.outputs, self.mine, self.exclude, self.clause, self.nulltested, self.role, self.distinct = saved
        self.scope, self.joined, self.cmp_left, self.base, self.where_so_far = saved_scope
        self.frames = saved_frames
        conj = lambda ps: None if not ps else (ps[0] if len(ps) == 1 else And(tuple(ps)))
        return Program(Scan(base, base, joins), conj(where), group, conj(having), select, dis == "DISTINCT", order, limit, 0, ctes)


def rebuild(seq, caps=None):
    """A program from a recorded sequence. Raises if the decoder asks for a context the sequence did not
    record -- the round-trip receipt. Returns (program, decisions of R outside the checker's allow)."""
    it, outside = iter(seq), []
    def choose(d):
        c, a = next(it)
        if c != d.ctx: raise AssertionError("decoder at %r, sequence at %r (%s)" % (d.ctx, c, a))
        if d.allow is not None and not (d.allow(a) if callable(d.allow) else a in d.allow): outside.append((d.ctx, a))
        return a
    p = Decoder(choose, caps).program()
    try: next(it); raise AssertionError("sequence has actions the decoder did not consume")
    except StopIteration: pass
    return p, outside


# ================================================================ the fit, and the sampler
def _is_member_ctx(ctx):
    return ctx[0] in ("REF", "STEP_REL", "STEP_OUT") or (len(ctx) == 3 and ctx[2] in VALUED)


class Law:
    """P as counts of the next action in each context. A member (a REF's distance, a step index, a literal's
    value) is an action in a context of its own, so one table holds everything."""

    def __init__(self):
        self.next = collections.defaultdict(collections.Counter)
        self.caps, self.n, self.evidence = {"depth": 0, "nest": 0}, 0, []
        self.pool = collections.defaultdict(collections.Counter)         # role -> every value it took, anywhere
        self.back = collections.defaultdict(collections.Counter)         # every proper prefix of a context

    def observe(self, s):
        self.n += 1; self._tokens = None
        for ctx, a in s.out:
            self.next[ctx][a] += 1
            if len(ctx) == 3 and ctx[2] in VALUED: self.pool[ctx[2]][a] += 1
            for k in range(1, len(ctx)): self.back[ctx[:k]][a] += 1
            if len(ctx) >= 2 and not _is_member_ctx(ctx): self.back[("SLOT", ctx[1])][a] += 1
            if len(ctx) >= 4 and str(ctx[0]).startswith("ARITH") and isinstance(ctx[3], int):
                self.caps["depth"] = max(self.caps["depth"], ctx[3])
        self.caps["nest"] = max(self.caps["nest"], s.maxnest)
        self.caps["size"] = max(self.caps.get("size", 0), len(s.out))
        for k, v in s.maxlen.items(): self.caps[k] = max(self.caps.get(k, 0), v)
        self.evidence += s.evidence

    def tokens(self):
        if getattr(self, "_tokens", None) is None:
            c = collections.Counter()
            for ctx, acts in self.next.items():
                if not _is_member_ctx(ctx): c.update(acts)
            self._tokens = c
        return self._tokens

    def counts(self, ctx):
        """The fitted counts for a context, backing off by dropping the last element of the context."""
        if len(ctx) == 3 and ctx[2] in VALUED:
            return self.next[ctx] if ctx in self.next else self.pool.get(ctx[2])
        if ctx in self.next: return self.next[ctx]
        for k in range(len(ctx) - 1, 1, -1):
            if ctx[:k] in self.back: return self.back[ctx[:k]]
        return self.back.get(("SLOT", ctx[1])) if len(ctx) >= 2 else None

    def sample(self, rng, record=None):
        """One program drawn from P under the structural masks only (no database). `record`, if a list,
        receives every masked decision's Z: the mass of the allowed actions in the counts used."""
        def choose(d):
            ctx, allow = d.ctx, d.allow
            c = self.counts(ctx)
            ok = allow if callable(allow) else (lambda a: allow is None or a in allow)
            opts = {a: k for a, k in (c or {}).items() if ok(a)}
            if not opts:
                seen = self.tokens() if not _is_member_ctx(ctx) else None
                opts = {a: 1 for a in sorted(allow, key=str) if seen is None or a in seen} if allow and not callable(allow) else {}
                if not opts: raise Unsupported("no admissible action at %r" % (ctx,))
            elif allow is not None and record is not None: record.append((ctx, sum(opts.values()) / sum(c.values())))
            return _draw(opts, rng)
        return Decoder(choose, self.caps).program()


def _draw(counter, rng):
    tot = sum(counter.values()); x = rng.random() * tot
    for a, k in counter.items():
        x -= k
        if x <= 0: return a
    return a


def edepth(x, _memo=None):
    """How deeply an expression nests when written out: expressions and predicates alike, a reused object
    counted at its full depth wherever it stands. SQLite's parser bounds this; so does R."""
    from dataclasses import fields, is_dataclass
    memo = {} if _memo is None else _memo
    if id(x) in memo: return memo[id(x)][1]
    if isinstance(x, (tuple, list)): v = max((edepth(y, memo) for y in x), default=0)
    elif isinstance(x, (Program, SetOp)): v = 0                    # a subquery is written as its own statement
    elif is_dataclass(x) and not isinstance(x, type):
        v = 1 + max((edepth(getattr(x, f.name), memo) for f in fields(x)), default=0)
    else: v = 0
    memo[id(x)] = (x, v)
    return v


_COMPOUNDS = (Arith, Agg, Case, Func, Cast, Window, Strftime, PredVal, Subq)
_PREDS = (Cmp, Not, IsNull, Like, In, Between, Or, And)


def depth_units(x, _memo=None):
    """How many compounds and predicates open inside `x`, in the units the decoder counts (a leaf adds
    nothing); a reused object costs this much wherever it is reused."""
    from dataclasses import fields, is_dataclass
    memo = {} if _memo is None else _memo
    if id(x) in memo: return memo[id(x)][1]
    if isinstance(x, (tuple, list)): v = max((depth_units(y, memo) for y in x), default=0)
    elif isinstance(x, (Program, SetOp)): v = 0
    elif is_dataclass(x) and not isinstance(x, type):
        inner = max((depth_units(getattr(x, f.name), memo) for f in fields(x)), default=0)
        v = inner + (1 if isinstance(x, _COMPOUNDS + _PREDS) else 0)
    else: v = 0
    memo[id(x)] = (x, v)
    return v


def program_edepth(p):
    qs = [p] + [q for _n, q in getattr(p, "ctes", ())]
    return max((edepth((q.select, q.where, q.group, q.having, q.order)) for q in qs if isinstance(q, Program)), default=0)


def fit(programs, typers=None, lets=False):
    law = Law()
    for i, p in enumerate(programs):
        if typers: typers[i]._index(p)
        law.observe(encode(p, typers[i] if typers else None, lets))
    # THE DEPTH CAP, IN THE DECODER'S OWN UNITS: rebuild every source program and take the deepest point
    for i, p in enumerate(programs):
        seq = sequence(p, typers[i] if typers else None, lets)
        it = iter(seq)
        dec = Decoder(lambda d: next(it)[1], {k: v for k, v in law.caps.items() if k != "edepth"})
        try: dec.program(); law.caps["edepth"] = max(law.caps.get("edepth", 0), dec.max_open)
        except Exception: pass
    return law


def divergence(law, samples, least=8, top=10):
    """The contexts where a law refitted on `samples` departs most from `law`, weighted by the law's count.
    The receipt of the projection: with no database this should read near zero everywhere."""
    S = Law()
    for p in samples: S.observe(encode(p, None, lets=True))
    rows = []
    for ctx, c in law.next.items():
        n = sum(c.values())
        if n < least or ctx not in S.next: continue
        q = S.next[ctx]; m = sum(q.values())
        kl = sum(k / n * math.log((k / n) / ((q.get(a, 0) + 0.5) / (m + 0.5 * len(c)))) for a, k in c.items())
        rows.append((kl * n, kl, n, ctx, dict(c.most_common(4)), dict(q.most_common(4))))
    rows.sort(reverse=True)
    return rows[:top], sum(r[0] for r in rows) / max(1, sum(r[2] for r in rows))


def show(seq):
    return "\n".join("  %-48s %s" % (" ".join(str(x) for x in ctx), a) for ctx, a in seq)


# ================================================================ the report
def _stats(seqs):
    """Per-program statistics no single context stores, measured identically on R and on samples."""
    n = max(1, len(seqs)); c = collections.Counter()
    for s in seqs:
        acts = [a for _c, a in s]
        c["actions"] += len(acts); c["arith"] += acts.count("ARITH"); c["ref"] += acts.count("REF")
        c["agg"] += acts.count("AGG"); c["case"] += acts.count("CASE")
        c["joins"] += sum(1 for x, a in s if a == MORE and x[:2] == ("QUERY", "joins"))
        c["root_joins"] += sum(1 for x, a in s if a == MORE and x[:2] == ("QUERY", "joins") and "ROOT" in x)
        c["ordered"] += any(a == MORE and x[:3] == ("QUERY", "order", 0) and x[-1] == "ROOT" for x, a in s)
        c["depth"] += max([x[3] for x, a in s if len(x) >= 4 and str(x[0]).startswith("ARITH") and isinstance(x[3], int)] or [0])
        c["has_ref_in_arith"] += any(a == "REF" and str(x[0]).startswith("ARITH") for x, a in s)
        c["grouped"] += any(a == MORE and x[:3] == ("QUERY", "group", 0) and x[-1] == "ROOT" for x, a in s)
        c["step"] += any(a == MORE and x[:3] == ("QUERY", "steps", 0) and x[-1] == "ROOT" for x, a in s)
        c["sort_is_ref"] += any(a == "REF" and x[:2] == ("ORDER", "order") for x, a in s)
        c["limited"] += any(a == "LIMIT" for _x, a in s)
        c["base_is_step"] += any(a == "STEP_REL" and x[:2] == ("QUERY", "from") and x[-1] == "ROOT" for x, a in s)
    return {k: v / n for k, v in c.items()}


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.sources import programs, typers
    from specbridge.pd.structures.algebra import emit
    src = sys.argv[1] if len(sys.argv) > 1 else "livesql"
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    R, T = programs(src), typers(src)
    law = fit(R, T)
    seqs = [sequence(p, T[i]) for i, p in enumerate(R)]
    print("%s: %d programs, %d decisions, %d contexts, %d distinct tokens; caps: depth %d, nest %d" % (
        src, law.n, sum(len(s) for s in seqs), len(law.next), len(law.tokens()), law.caps["depth"], law.caps["nest"]))
    print("\nTHE VOCABULARY, COUNTED ON R")
    toks = law.tokens().most_common()
    for j in range(0, len(toks), 4):
        print("  " + "".join("%-18s %5d   " % t for t in toks[j:j + 4]))

    print("\nROUND TRIP: program -> actions -> program -> actions, on every program of R")
    ok, outside_all, fails = 0, [], []
    for i, s in enumerate(seqs):
        try:
            p2, outside = rebuild(s, law.caps)
            s2 = sequence(p2, lets=True)
            if s2 == s: ok += 1
            else:
                k = next((k for k in range(min(len(s), len(s2))) if s[k] != s2[k]), None)
                fails.append((i, "first difference at %s: %s vs %s" % (k, s[k] if k is not None else len(s), s2[k] if k is not None else len(s2))))
            outside_all += outside
        except Exception as e:
            fails.append((i, repr(e)[:160]))
    print("  %d / %d identical; %d decisions of R outside the structural allow-set" % (ok, len(seqs), len(outside_all)))
    for f in fails[:8]: print("   program %d: %s" % f)
    if outside_all: print("   outside:", collections.Counter((c[:2], a) for c, a in outside_all).most_common(8))

    print("\nSAMPLES FROM P, NO DATABASE (n=%d): what R does per program against what P does" % N)
    rng = random.Random(0); samples, progs, refused, zs = [], [], collections.Counter(), []
    for k in range(N):
        try:
            p = law.sample(rng, record=zs); progs.append(p); samples.append(sequence(p, lets=True))
        except Unsupported as e: refused[str(e).split(":")[0][:70]] += 1
        except Exception as e: refused[type(e).__name__ + " " + str(e)[:60]] += 1
    rs, ss = _stats(seqs), _stats(samples)
    print("  %d built, %d refused by the IR's own invariants; mean -log Z per masked decision %.4f over %d" % (
        len(samples), sum(refused.values()), -sum(math.log(z) for _c, z in zs) / max(1, len(zs)), len(zs)))
    cost = collections.Counter()
    for ctx, z in zs: cost[ctx[:2] + ((ctx[4],) if len(ctx) > 4 else ())] -= math.log(z)
    print("  where the structural masks cost most (total -log Z): " + "; ".join("%s %.0f" % (" ".join(map(str, k)), v) for k, v in cost.most_common(6)))
    for why, k in refused.most_common(6): print("    refused %3d  %s" % (k, why))
    print("  per program, mean over R's %d programs and P's %d built samples (of %d drawn):" % (len(seqs), len(samples), N))
    print("  %-20s %8s %8s" % ("", "R", "P"))
    for k in ("actions", "arith", "depth", "ref", "has_ref_in_arith", "sort_is_ref", "ordered", "limited", "agg", "case", "joins", "root_joins", "grouped", "step", "base_is_step"):
        print("  %-20s %8.2f %8.2f" % (k, rs.get(k, 0), ss.get(k, 0)))
    rows, mean_kl = divergence(law, progs)
    print("\nWHERE THE SAMPLED LAW DEPARTS FROM R (R count x KL; mean KL per decision %.3f)" % mean_kl)
    for w, kl, n, ctx, c, q in rows[:8]:
        print("  %6.1f  kl %.2f  n %3d  %-50s R %s\n%57s P %s" % (w, kl, n, " ".join(map(str, ctx))[:50], c, "", q))
    for i in rng.sample(range(len(samples)), min(3, len(samples))):
        try:
            p, _ = rebuild(samples[i], law.caps); print("\n  sample %d:  %s" % (i, emit(p)[:420]))
        except Exception as e: print("\n  sample %d: (not emittable: %s)" % (i, str(e)[:100]))
