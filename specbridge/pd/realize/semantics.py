"""specbridge.pd.realize.semantics — THE ONE SEMANTIC CHECKER. Every expression has a record; every operator has a contract.

A model interprets the database ONCE (`specbridge.pd.realize.semantic` -> catalogues/<db>.json). This module combines that saved
knowledge mechanically, and it is the ONLY place meaning is interpreted: the binder asks it which candidates to
prefer and which to exclude while a program is built, and the verifier asks it, over the finished program, the
same question with the same records. There is no second interpretation.

THE RECORD (`catalogue.Ann`): computational type (slot), unit, kind, measurement scale (ratio | interval), grain
(the entity a value belongs to: a table, "group" after an aggregate), the stored QUANTITY it measures and the FORM
it takes (the value itself, or SUM/AVG/MIN/MAX of it), a constant's value, and per property its PROVENANCE
(rows | doc | rule | model).

A CONTRACT takes its operands' records and returns (the result's record, a verdict, the basis of the verdict).
The verdict is "supported", "contradicted" or "unknown", with its basis. Support and contradiction alike are
ESTABLISHED (rows, documentation, a declared rule) or PLAUSIBLE (the model's one-time reading, saved in the
catalogue); both kinds of contradiction exclude, both kinds of support are preferred. Only missing evidence is
"unknown", and it is allowed.
Contracts exist per OPERATOR, never per formula: a new tree composes existing contracts.

    column       the catalogue's record
    constant     kind "const", its value
    step output  EXACTLY the record of the expression that produced it (no new rule)
    reuse (REF)  the same object, so exactly the same record (no new rule)
    CAST         REAL keeps the record; INTEGER truncates (a fraction does not survive); TEXT is text; an identifier
                 or a category cast to a number is contradicted (a name is not a measurement)
    function     its declared transformation (FUNCS below); an undeclared function gives an unknown record
    aggregate    COUNT counts rows; SUM/AVG need a quantity (not an identifier or text), SUM a true zero;
                 SUM/AVG/COUNT of a value count each row of its table once, so a join that repeats that table's
                 rows contradicts them (the query's MULTIPLICITY, `repeated`)
    arithmetic   identifiers and text never; + and - need one unit (elementary units compared), * / % a true
                 zero; a complement 1 - x or 100 - x is supported only for a fraction or a percentage; a
                 conversion factor from the declared table is supported and changes the unit; structurally
                 equal operands give a constant (x - x = 0), recorded, not banned; related quantities (catalogue
                 relations: comparable, part_of, rate) support + - and /, respecting their forms
    CASE         0/1 results are an indicator; numeric constants a score; otherwise the branches' common unit
    BETWEEN      constant bounds in reverse order are an empty range
    join         a declared link is supported; a link read off the rows into a primary key is plausible; a match
                 of values alone is contradicted

USEFULNESS IS NOT HERE. Whether an expression is informative to a human (x - x, AVG(2), round(2, 2)) is measured
separately (`verify.usefulness`); this checker guarantees consistency with known semantics and records unknowns.
"""
from __future__ import annotations
import collections, dataclasses

from specbridge.pd.structures.algebra import Agg, Arith, Between, Case, Cast, Col, Const, Func, In, Join, PredVal, Program, SetOp, Strftime, Subq, Window, Cmp

SUPPORTED, CONTRA, UNKNOWN = "supported", "contradicted", "unknown"
NUMBER_TYPES = {"REAL", "INTEGER", "INT", "BIGINT", "NUMERIC", "FLOAT", "DOUBLE", "DECIMAL"}

PASS = {"round", "abs"}                                      # same value, same meaning
TRUNC = {"ceil", "ceiling", "floor"}                         # a whole number: a fraction does not survive
NULLS = {"coalesce", "ifnull", "nullif"}                     # the first argument, with a fallback of the same meaning
EXTREMES = {"max", "min", "greatest", "least"}               # one of its arguments: they must be comparable
CLOCK = {"current_date", "current_timestamp", "now", "current_time"}
DATES = {"date", "datetime"}
NUMERIC = {"log", "ln", "log10", "log2", "exp", "sqrt", "power", "pow", "sign", "sin", "cos", "tan"}
TEXTS = {"lower", "upper", "substr", "substring", "trim", "ltrim", "rtrim", "replace", "strftime", "printf", "format"}
RANKS = {"rank", "dense_rank", "row_number", "ntile", "percent_rank", "cume_dist"}
SHIFTS = {"lag", "lead", "first_value", "last_value", "nth_value"}


def _close(a, b):
    import math
    return math.isclose(a, b, rel_tol=1e-6)


def _compose(da, db, sign):
    """Dimensions multiplied (sign 1) or divided (sign -1): exponents add or subtract; None when either is unknown."""
    if da is None or db is None: return None
    d = dict(da)
    for k, e in db: d[k] = d.get(k, 0) + sign * e
    return tuple(sorted((k, e) for k, e in d.items() if e))


def _category(a):
    """A value that names an unordered class: the profile's category role (an identifier is not one: its ranges are
    ordered, BIRD gold uses them)."""
    return a is not None and a.kind != "const" and a.role == "category"


def same_operands(a):
    """Are an arithmetic node's two operands the same value? Structurally equal, or a quotient whose dividend is the
    divisor under the compiler's cast to REAL (`CAST(x AS REAL) / x`: division is real division, LANGUAGE.md section 7,
    and the cast changes no value of x). No other wrapper is looked through: a cast to INTEGER truncates, a round
    rounds. The one test the checker's contract and the duplicate policy share."""
    if a.l == a.r: return True
    return a.op == "/" and isinstance(a.l, Cast) and str(a.l.type).upper() in ("REAL", "FLOAT", "DOUBLE") and a.l.expr == a.r


def _ann(**kw):
    from specbridge.pd.realize.catalogue import Ann
    return Ann(**kw)


def _num(v):
    try: return float(v) if not isinstance(v, bool) else None
    except Exception: return None


REFERENCE_UNIT = True    # a REFERENCE divisor is a value of its operand's quantity (see `record`)


class Semantics:
    def __init__(self, cat):
        self.cat = cat
        self._memo, self._admit, self._local = {}, {}, {}
        self.NONE = _ann()

    # ================================================================ contracts: records in -> (record, verdict, basis)
    @staticmethod
    def _out(rec, t, b):
        """A verdict with its basis. A contradiction, like a support, is ESTABLISHED when it rests on rows,
        documentation or a declared rule, and PLAUSIBLE when it rests on the model's one-time reading of the
        database; both exclude. Missing evidence is never a contradiction: it stays unknown."""
        return rec, t, b

    def const(self, v):
        """A constant. "WHOLE" stands for the whole of a unit (1 or 100) on the left of a complement before its right
        operand is drawn: a number whose value is bound once the right is known."""
        n = _num(v)
        return _ann(slot="NUM" if n is not None or v == "WHOLE" else "TEXT", amount=True, kind="const", value=v)

    def cast(self, typ, a):
        from specbridge.pd.realize.catalogue import _unit_word
        t = str(typ or "").upper()
        if t in NUMBER_TYPES and a.slot in ("KEY", "TEXT"):          # an identifier or a category read as a number
            return self.NONE, CONTRA, a.ev.get("slot") or "rows"
        if t in ("TEXT", "VARCHAR", "CHAR"): return _ann(slot="TEXT"), UNKNOWN, ""
        if t == "DATE": return _ann(slot="DATE", scale="interval", kind="date", ev={"scale": "rule"}), UNKNOWN, ""
        if t in ("INTEGER", "INT", "BIGINT") and (_unit_word(a) == "fraction" or a.kind in ("share", "indicator")):
            return _ann(slot="NUM", amount=a.amount, grain=a.grain), UNKNOWN, "a fraction truncated"
        return a, UNKNOWN, ""

    def func(self, name, args):
        """A function's declared transformation of its arguments' records."""
        from specbridge.pd.realize.catalogue import _unit_word, _weakest, _all3
        n = str(name).lower(); a = args[0] if args else self.NONE
        if n in CLOCK: return _ann(slot="DATE", scale="interval", kind="date", ev={"scale": "rows"}), UNKNOWN, "the snapshot"
        if n in DATES: return _ann(slot="DATE", scale="interval", kind="date", ev={"scale": "rows"}), UNKNOWN, ""
        if n == "julianday": return _ann(slot="NUM", scale="interval", unit="days", kind="date", ev={"scale": "rows", "unit": "rule"}), UNKNOWN, ""
        if n in PASS | TRUNC | NUMERIC and a.slot in ("KEY", "TEXT"): return self.NONE, CONTRA, "rows"
        if n in NUMERIC and a.slot == "DATE" and a.kind != "const": return self.NONE, CONTRA, "rows"   # sqrt of a date
        if n in PASS:
            if n == "round" and len(args) > 1 and _num(args[1].value) == 0 and _unit_word(a) == "fraction":
                return _ann(slot="NUM", amount=a.amount, grain=a.grain), UNKNOWN, "a fraction rounded to a whole"
            return a, UNKNOWN, ""
        if n in TRUNC:
            return self.cast("INTEGER", a)
        if n in NULLS | EXTREMES:
            units = [x.unit for x in args if x.kind != "const" and x.unit and " per " not in x.unit and " × " not in x.unit]
            dims = {x.dim for x in args if x.kind != "const" and x.dim is not None}
            if len(dims) > 1:
                return self._out(self.NONE, CONTRA, _weakest(*[x.ev.get("unit") for x in args if x.unit]))
            if n in NULLS: return a, UNKNOWN, ""
            live = [x for x in args if x.kind != "const"] or list(args)
            return _ann(slot="NUM", amount=_all3(x.amount for x in live), unit=units[0] if units else "", scale=live[0].scale,
                        kind=live[0].kind if len({x.kind for x in live}) == 1 else "", grain=live[0].grain if len({x.grain for x in live}) == 1 else "", ev={"unit": _weakest(*[x.ev.get("unit") for x in live if x.unit])}), UNKNOWN, ""
        if n in NUMERIC: return _ann(slot="NUM", grain=a.grain), UNKNOWN, ""
        if n == "strftime" and args: return self.strftime(args[0].value if args[0].kind == "const" else None)
        if n in TEXTS: return _ann(slot="TEXT"), UNKNOWN, ""
        if n == "length": return _ann(slot="NUM", kind="count", unit="characters"), UNKNOWN, ""
        if n in RANKS: return _ann(slot="NUM", kind="rank"), UNKNOWN, ""
        if n in SHIFTS: return a, UNKNOWN, ""
        return _ann(), UNKNOWN, ""

    DATE_PARTS = {"%Y": "years", "%m": "months", "%d": "days", "%j": "days", "%H": "hours", "%M": "minutes",
                  "%S": "seconds", "%s": "seconds", "%J": "days"}

    def strftime(self, fmt):
        """strftime returns TEXT. With a single numeric part as its whole format ('%Y'), that text is a number:
        SQLite's ARITHMETIC reads '1996' as 1996, so the record is a date part -- a point on an interval scale,
        whose difference is a duration (strftime('%Y', a) - strftime('%Y', b) is years). It stays text with no
        affinity for COMPARISON: SQLite does not convert it there ('1996' = 1996 is false). Any other format
        ('%Y-%m') is text."""
        u = self.DATE_PARTS.get(str(fmt)) if fmt is not None else None
        if u is None: return _ann(slot="TEXT"), UNKNOWN, ""
        return _ann(slot="TEXT", kind="date part", unit=u, scale="interval", ev={"scale": "rule", "unit": "rule", "kind": "rule"}), UNKNOWN, ""

    @staticmethod
    def _as_number(a):
        """What arithmetic reads: a date part's text is its number (see `strftime`)."""
        if a.kind == "date part": return _ann(slot="NUM", kind="date", unit=a.unit, scale="interval", amount=False, ev=a.ev)
        return a

    def agg(self, fn, distinct, a, repeated=frozenset()):
        """An aggregate over its argument's record, in a query whose joins repeat the rows of `repeated` tables."""
        fn = str(fn).upper()
        grain_hit = a is not None and not distinct and a.grain and a.grain in repeated
        if fn == "COUNT":
            rec = _ann(slot="NUM", amount=True, scale="ratio", kind="count", unit="rows", grain="group", ev={"unit": "rule", "scale": "rule"},
                       role="count", dim=(("count", 1),), factor=1.0)
            return (rec, CONTRA, "grain") if grain_hit else (rec, UNKNOWN, "")
        a = a or self.NONE
        if fn in ("SUM", "AVG") and a.slot in ("KEY", "TEXT"): return self.NONE, CONTRA, "rows"
        if fn in ("SUM", "AVG", "MIN", "MAX") and _category(a): return self._out(self.NONE, CONTRA, a.ev.get("role") or "rows")
        if fn == "SUM" and isinstance(a.additive, dict) and a.kind != "const":
            # ADDITIVITY BY AXIS: a SUM runs along every axis its table's rows vary over; a balance summed over time
            axes = self.cat.axes.get(a.grain, ("entities",)) if hasattr(self.cat, "axes") else ("entities",)
            if any(a.additive.get(ax) is False for ax in axes): return self._out(self.NONE, CONTRA, a.ev.get("additive") or "model")
        if fn == "SUM" and a.scale == "interval" and a.kind != "const": return self._out(self.NONE, CONTRA, a.ev.get("scale") or "rows")
        if fn in ("SUM", "AVG") and grain_hit: return self.NONE, CONTRA, "grain"
        if a.kind == "const":
            return _ann(slot="NUM", amount=True, kind="const" if fn != "SUM" else "", value=a.value if fn != "SUM" else None,
                        grain="group"), UNKNOWN, "a summary of a constant"
        if a.kind == "indicator" and fn in ("SUM", "AVG"):          # counting the rows a condition holds on, or their share
            return _ann(slot="NUM", amount=True, scale="ratio", kind="count" if fn == "SUM" else "share",
                        unit="rows" if fn == "SUM" else "fraction", grain="group",
                        ev={"unit": "rule", "kind": "rule", "scale": "rule"}), UNKNOWN, ""
        q = (a.quantity[0], fn) if a.quantity and a.quantity[1] == "value" and fn in ("SUM", "AVG", "MIN", "MAX") else ()
        level = fn in ("AVG", "MIN", "MAX")                          # a level keeps the kind; a total of shares is not a share
        return _ann(slot=a.slot if fn in ("MIN", "MAX") else "NUM", amount=a.amount, scale=a.scale, unit=a.unit,
                    kind=a.kind if level or a.kind not in ("share", "percent") else "", population=a.population,
                    grain="group", quantity=q, ev=a.ev, role=a.role if level else "", meaning=a.meaning, dim=a.dim,
                    factor=a.factor, order=a.order if fn in ("MIN", "MAX") else None), UNKNOWN, ""

    def arith(self, op, l, r, equal=False):
        """One arithmetic operation over two records: the result's record, the verdict, its basis. The result's
        dimension is derived from its operands' (docs/LANGUAGE.md section 3a)."""
        import dataclasses
        rec, t, b = self._arith(op, l, r, equal)
        if t == CONTRA or rec is None or rec is self.NONE or rec.dim is not None or rec.kind == "const": return rec, t, b
        from specbridge.pd.realize.semantic import parse_unit
        const = lambda a: a.kind == "const"
        l2, r2 = self._as_number(l), self._as_number(r)
        if const(l2) or const(r2):
            x = r2 if const(l2) else l2
            pu = parse_unit(rec.unit) if rec.unit and rec.unit != x.unit else None
            if pu: dim, fac = pu                                       # a conversion or a complement names its unit
            elif op == "/" and const(l2): dim, fac = _compose((), x.dim, -1), (1 / x.factor if x.factor else None)
            else: dim, fac = x.dim, x.factor                           # a shift or a stated weight keeps the unit
        elif op in "+-": dim, fac = (l2.dim, l2.factor) if l2.dim == r2.dim else (None, None)
        elif op in "*/":
            sign = 1 if op == "*" else -1
            dim = _compose(l2.dim, r2.dim, sign)
            fac = None if l2.factor is None or r2.factor is None else (l2.factor * r2.factor if sign > 0 else l2.factor / r2.factor)
        else: dim, fac = None, None
        return dataclasses.replace(rec, dim=dim, factor=fac), t, b

    def _arith(self, op, l, r, equal=False):
        from specbridge.pd.realize.catalogue import _unit_word, conversions, _UNIT_KIND, _weakest, _strongest, _all3
        const = lambda a: a.kind == "const"
        grain = l.grain if (l.grain == r.grain or const(r)) else r.grain if const(l) else ""
        # ---- established contradictions, whatever the partner
        l, r = self._as_number(l), self._as_number(r)
        for a in (l, r):
            if a.slot in ("KEY", "TEXT"): return self.NONE, CONTRA, "rows"
        # INTERVAL SCALE. A date (a point in time) is never added to another nor multiplied. An interval MEASURE (a
        # score, a temperature, a coordinate) has no true zero: an explicit weighting by a stated number (x * w, x / w)
        # and a sum or difference of one dimension are defined; a RATIO reading of it is not (x * y, x / y, w / x, x % y).
        date = lambda a: a.scale == "interval" and a.kind == "date" and not const(a)
        if op == "+" and date(l) and date(r):
            return self._out(self.NONE, CONTRA, _weakest(l.ev.get("scale"), r.ev.get("scale")))
        if op in "*/%" and (date(l) or date(r)):
            return self._out(self.NONE, CONTRA, _weakest(*[a.ev.get("scale") for a in (l, r) if a.scale == "interval"]))
        if op in "*/%":
            for a, other, side in ((l, r, "l"), (r, l, "r")):
                if a.scale == "interval" and not const(a):
                    weighting = const(other) and (op == "*" or (op == "/" and side == "l"))
                    if not weighting: return self._out(self.NONE, CONTRA, a.ev.get("scale") or "rows")
        for a in (l, r):                                               # a coded class read as a quantity
            if _category(a): return self._out(self.NONE, CONTRA, a.ev.get("role") or "rows")
        # DIMENSIONS: a sum or difference needs one dimension and one factor (kg + m, or cm + m without a conversion);
        # a product or quotient composes them (in `arith`). Unknown dimensions decide nothing.
        if op in "+-" and not (const(l) or const(r)) and l.dim is not None and r.dim is not None:
            if l.dim != r.dim: return self._out(self.NONE, CONTRA, _weakest(l.ev.get("dim") or l.ev.get("unit"), r.ev.get("dim") or r.ev.get("unit")))
            if l.factor is not None and r.factor is not None and not _close(l.factor, r.factor):
                return self._out(self.NONE, CONTRA, _weakest(l.ev.get("unit"), r.ev.get("unit")))
        # ---- structurally equal operands: a constant, recorded (usefulness is judged elsewhere)
        if equal and op in "-/":
            return _ann(slot="NUM", amount=True, kind="const", value=0 if op == "-" else 1), UNKNOWN, "equal operands"
        # ---- a constant operand
        if const(l) or const(r):
            k, x = (l, r) if const(l) else (r, l)
            v = _num(k.value)
            if op == "-" and const(l) and not const(r):
                w = _unit_word(r)
                if (k.value == "WHOLE" and w in ("fraction", "percent")) or (v == 1 and w == "fraction") or (v == 100 and w == "percent"):
                    b = r.ev.get("unit") or r.ev.get("kind") or "rule"
                    return self._out(_ann(slot="NUM", amount=True, scale="ratio", unit=r.unit or "fraction", kind=r.kind or "share",
                                          grain=r.grain, ev={"unit": b, "kind": b, "scale": b}), SUPPORTED, b)   # a complement
                # THE PARAMETER'S ROLE: a 1 or 100 on the left of a subtraction IS the WHOLE of a complement -- the one
                # reading the language gives it (`actions.const_kind`), so the complement's contract applies to it. The
                # whole of a count, an amount or a rate does not exist: contradicted when the operand's unit is known
                # and is not a fraction or a percentage (an unknown unit stays unknown).
                if (k.value == "WHOLE" or v in (1.0, 100.0)) and w:
                    return self._out(self.NONE, CONTRA, r.ev.get("unit") or r.ev.get("kind") or "rows")
            if op in "*/" and const(r) and v is not None:
                conv = dict(conversions(op, l))
                if v in conv:
                    nu = conv[v]; b = l.ev.get("unit") or "rule"
                    return self._out(_ann(slot="NUM", amount=l.amount, scale=l.scale, unit=nu, kind=_UNIT_KIND.get(nu, ""), grain=grain, ev={"unit": b, "kind": b, "scale": l.ev.get("scale", "")}), SUPPORTED, b)   # a conversion
            if op in "+-":      # a shift keeps the unit and the scale; the kind (a share's bounds) does not survive
                rec = _ann(slot="NUM", amount=x.amount, scale=x.scale, unit=x.unit, grain=grain, ev={"unit": x.ev.get("unit", ""), "scale": x.ev.get("scale", "")})
            elif op == "/" and const(l):
                rec = _ann(slot="NUM", amount=x.amount, unit=("per " + x.unit) if x.unit else "", grain=grain, ev={"unit": x.ev.get("unit", "")})
            else:               # scaling by a number keeps the unit; the kind does not survive
                rec = _ann(slot="NUM", amount=_all3((x.amount, k.amount)), scale=x.scale, unit=x.unit, grain=grain, ev={"unit": x.ev.get("unit", "")})
            return rec, UNKNOWN, "a constant"
        # ---- two non-constant operands: the relation between their quantities, respecting their forms
        ql, qr = l.quantity, r.quantity
        hit = None
        levels = ("value", "AVG", "MIN", "MAX")
        add_ok = not (ql and qr) or (ql[1] in levels and qr[1] in levels) or ql[1] == qr[1]
        div_ok = bool(ql and qr) and ql[1] == qr[1] and (l.grain == r.grain or ql[1] == "value")
        t, b = UNKNOWN, ""
        if op == "-" and l.scale == "interval" and r.scale == "interval" and l.kind == r.kind == "date":
            t, b = SUPPORTED, _weakest(l.ev.get("scale"), r.ev.get("scale")) or "rows"     # a duration between two dates
        elif op in "+-" and not add_ok: t, b = UNKNOWN, "different summaries of their quantities"
        elif op in "+-" and ql and qr and ql[0] == qr[0]: t, b = SUPPORTED, "rows"                 # one quantity at two levels
        elif ql and qr and self.cat.rel:
            a_, b_ = ql[0], qr[0]
            ks = ([(a_, b_, "comparable"), (b_, a_, "comparable")] if op in "+-" else
                  [(a_, b_, "part_of"), (a_, b_, "rate")] if op == "/" and div_ok else
                  [(a_, b_, "product"), (b_, a_, "product")] if op == "*" and ql[1] == qr[1] == "value" else [])
            hits = [k for k in ks if k in self.cat.rel]
            if hits: t, b = SUPPORTED, _strongest(*[self.cat.rel[k] for k in hits]); hit = hits[0]
        # A SHARED UNIT IS NECESSARY, NOT SUFFICIENT: total bilirubin and urea nitrogen are both mg/dL. A sum or
        # difference is supported by one quantity or a recorded relationship; a shared unit alone stays unknown.
        if t == UNKNOWN and not b and op in "+-" and l.unit and l.unit == r.unit: b = "same unit, quantities not related"
        ev = {"unit": _weakest(l.ev.get("unit") if l.unit else "", r.ev.get("unit") if r.unit else "")}
        if op in "+-":
            if op == "-" and l.scale == "interval" and r.scale == "interval": amount, scale = True, "ratio"   # a difference of dates
            else: amount = _all3((l.amount, r.amount)); scale = "ratio" if amount else ""
            rec = _ann(slot="NUM", amount=amount, scale=scale, unit=l.unit if l.unit == r.unit else "",
                       grain=grain,
                       ev={**ev, "scale": _weakest(l.ev.get("scale"), r.ev.get("scale"))})
        elif op == "/" and t == SUPPORTED:          # a supported quotient is a share (part over whole) or a rate
            share = bool(ql and qr) and (ql[0], qr[0], "part_of") in self.cat.rel
            res = self.cat.rel_result.get(hit, "") if hit else ""
            rec = _ann(slot="NUM", amount=True, scale="ratio", unit="fraction" if share else (res or "%s per %s" % (l.unit or "?", r.unit or "?")),
                       kind="share" if share else "rate", grain=grain, ev={"unit": b, "kind": b, "scale": b, "amount": b})
        elif op == "*" and t == SUPPORTED:          # a supported product: what the relationship says it yields
            rec = _ann(slot="NUM", amount=True, scale="ratio", unit=(self.cat.rel_result.get(hit, "") if hit else "") or "%s × %s" % (l.unit, r.unit),
                       kind="product", grain=grain, ev={"unit": b, "kind": b, "scale": b, "amount": b})
        elif op == "/":
            rec = _ann(slot="NUM", amount=_all3((l.amount, r.amount)), unit="%s per %s" % (l.unit, r.unit) if l.unit and r.unit else "", grain=grain, ev=ev)
        elif op == "*":
            rec = _ann(slot="NUM", amount=_all3((l.amount, r.amount)), unit="%s × %s" % (l.unit, r.unit) if l.unit and r.unit else "", grain=grain, ev=ev)
        else:
            rec = _ann(slot="NUM", amount=l.amount, unit=l.unit, grain=grain, ev=ev)
        return self._out(rec, t, b)

    def between(self, lo, hi):
        """BETWEEN lo AND hi over two constant bounds: bounds in reverse order make an empty range."""
        a, b = lo.value if lo is not None and lo.kind == "const" else None, hi.value if hi is not None and hi.kind == "const" else None
        if a is None or b is None: return UNKNOWN, ""
        na, nb = _num(a), _num(b)
        try: reversed_ = (na > nb) if na is not None and nb is not None else (isinstance(a, str) and isinstance(b, str) and a > b)
        except Exception: reversed_ = False
        return (CONTRA, "rule") if reversed_ else (UNKNOWN, "")

    ORDERING = ("<", ">", "<=", ">=", "BETWEEN")

    def compare(self, l, r, op=None):
        """A comparison of two values. SQLite compares a stored text value with a number AS TEXT (the number takes the
        column's text affinity): equality is exact ('12' = 12), but an ORDERING is the order of characters, not of
        values ('100' < '30') -- a type inconsistency (LANGUAGE.md section 3). A deliberate conversion reads the text
        as a number first (a CAST, whose own contract judges it). Checked against the targets' gold (out/review):
        equality of a text column with a number is used there and is kept. A date compared with a computed number is
        not a comparison of dates. Ordering text against text is not judged here."""
        # AN ORDERING NEEDS AN ORDERED OPERAND: a number, a date, a date part, an identifier range. A text value --
        # a category, a name, a code -- has no order the language can state; SQLite would order its characters.
        # R never orders a text column (0 of its orderings); lexical order stays available only to a task that
        # declares it, and the language has no such declaration.
        if op in self.ORDERING:
            for a in (l, r):
                if a is None or a.kind in ("const", "date part"): continue
                if a.role == "ordinal" and isinstance(a.order, list):
                    # the declared order must be the order SQLite compiles: characters for text, values for numbers
                    compiled = sorted(a.order) if a.slot == "TEXT" else sorted(a.order, key=lambda v: float(v) if _num(v) is not None else 0)
                    if compiled != list(a.order): return CONTRA, a.ev.get("role") or "model"
                    continue
                if a.slot == "TEXT" or _category(a): return CONTRA, a.ev.get("role") or "language"
        if l is None or r is None: return UNKNOWN, ""
        for a, b in ((l, r), (r, l)):
            if a.slot == "TEXT" and a.kind != "const" and b.slot == "NUM" and not isinstance(b.value, str) \
                    and (op in self.ORDERING or not a.key):       # an expression's text has no affinity: '1996' = 1996 is false
                return CONTRA, a.ev.get("slot") or "rows"
            if a.slot == "DATE" and a.kind != "const" and b.slot == "NUM" and b.kind != "const":   # a date is not a number
                return CONTRA, a.ev.get("slot") or "rows"
        return UNKNOWN, ""

    def join(self, t1, c1, t2, c2):
        """A join of t1.c1 with t2.c2. A link the schema declares is supported; a link read off the rows is plausible
        when it reaches a table's primary key (it names that row); a match of values alone -- two columns that
        happen to share values, such as two phone columns -- establishes no relationship and is contradicted.
        Joins to a step (our own intermediate result) are judged by the step's own keys, not here."""
        w = self.cat.world
        if t1 not in w.rel or t2 not in w.rel: return UNKNOWN, ""
        for c, cc, p, pc in ((t1, c1, t2, c2), (t2, c2, t1, c1)):
            if (c, cc, p, pc) in w.declared: return SUPPORTED, "doc"
        for c, cc, p, pc in ((t1, c1, t2, c2), (t2, c2, t1, c1)):
            if (c, cc, p, pc) in w.fks and w.pk.get(p) == [pc]: return SUPPORTED, "rows"
        # TWO KEYS OF ONE ENTITY: both columns reference the same parent key, so equal values name the same row of it
        # (satscores.cds and frpm.CDSCode both reference schools.CDSCode). Two phone columns reference nothing.
        for p, pc in {(p, pc) for c, cc, p, pc in w.fks if (c, cc) == (t1, c1)}:
            if (t2, c2, p, pc) in w.fks:
                return SUPPORTED, "doc" if (t1, c1, p, pc) in w.declared and (t2, c2, p, pc) in w.declared else "rows"
        return CONTRA, "rule"

    def case(self, branches):
        from specbridge.pd.realize.catalogue import _all3
        vals = [b.value for b in branches if b.kind == "const"]
        if branches and len(vals) == len(branches) and all(_num(v) in (0.0, 1.0) for v in vals):
            return _ann(slot="NUM", amount=True, scale="ratio", kind="indicator", ev={"kind": "rule", "scale": "rule"}), UNKNOWN, ""
        if branches and len(vals) == len(branches) and all(_num(v) is not None for v in vals):
            return _ann(slot="NUM", kind="score", ev={"kind": "rule"}), UNKNOWN, ""
        live = [b for b in branches if b.kind != "const"] or branches
        units = {b.unit for b in live}; grains = {b.grain for b in live}; dims = {b.dim for b in live}
        return _ann(slot="NUM" if all(b.slot == "NUM" for b in branches) else "ANY", amount=_all3(b.amount for b in branches),
                    unit=units.pop() if len(units) == 1 else "", grain=grains.pop() if len(grains) == 1 else "", dim=dims.pop() if len(dims) == 1 else None), UNKNOWN, ""

    # ================================================================ composition over a program
    def record(self, e, steps=None):
        """The record of any expression, by its constructor's contract over its operands' records. Memoised per
        object and per steps in scope: a program is a graph, and a reused part is the same record."""
        key = (id(e), tuple(sorted((n, id(q)) for n, q in (steps or {}).items())))
        hit = self._memo.get(key)
        if hit is not None and hit[0] is e: return hit[1]
        rec = self._contract(e, steps or {}, frozenset())[0]
        if len(self._memo) > 300000: self._memo.clear()
        self._memo[key] = (e, rec)
        return rec

    def _contract(self, e, steps, repeated):
        """(record, verdict, basis) of the node `e` itself: its contract over its children's records."""
        R = lambda x: self.record(x, steps) if x is not None else None
        if isinstance(e, Col):
            a = self.cat.ann.get((e.table, e.name))
            if a is not None: return a, UNKNOWN, ""
            q = steps.get(e.table)                                    # a step's output: exactly its expression's record
            if isinstance(q, Program) and e.name[:1] == "o" and e.name[1:].isdigit() and int(e.name[1:]) < len(q.select):
                return self.record(q.select[int(e.name[1:])][0], {**steps, **dict(q.ctes)}), UNKNOWN, ""
            return _ann(slot="ANY"), UNKNOWN, ""
        if isinstance(e, Const): return self.const(e.value), UNKNOWN, ""
        if isinstance(e, Cast): return self.cast(e.type, R(e.expr))
        if isinstance(e, Func): return self.func(e.name, [R(x) for x in e.args])
        if isinstance(e, Agg): return self.agg(e.fn, e.distinct, R(e.arg), repeated)
        if isinstance(e, Arith):
            l = R(e.l)
            if e.op == "/" and isinstance(e.r, Const) and REFERENCE_UNIT and l is not None and l is not self.NONE:
                # THE CONSTANT'S ROLE, read as the language reads it (`actions.const_kind`): the divisor of a bare
                # column that is not a conversion factor is a REFERENCE -- the operand's typical value, read from its
                # rows -- so it is a value of the operand's quantity, not a plain number: x / typical(x) has no unit.
                from specbridge.pd.structures.actions import _bare, const_kind, slot_roles
                role = "UNIT_PARAM" if "UNIT_PARAM" in slot_roles("ARITH:DIVIDE", "r", e.l) else "FORMULA_PARAM"
                if role == "UNIT_PARAM" and const_kind("ARITH:DIVIDE", "r", role, e.r.value) == "REFERENCE" and _num(e.r.value):
                    ref = dataclasses.replace(l, key="", quantity=(), grain="", ev={**l.ev, "kind": "rule"})
                    rec, t, b = self.arith("/", l, ref)
                    if t != CONTRA and rec is not None and rec is not self.NONE and rec.dim == ():
                        rec = dataclasses.replace(rec, unit="", kind="")          # relative to typical: no unit
                    return rec, t, b
            return self.arith(e.op, l, R(e.r), equal=same_operands(e))
        if isinstance(e, Case): return self.case([R(v) for _p, v in e.whens] + ([R(e.else_)] if e.else_ is not None else []))
        if isinstance(e, Window):
            if isinstance(e.fn, Agg): return self.agg(e.fn.fn, e.fn.distinct, R(e.fn.arg), frozenset())
            return R(e.fn) if e.fn is not None else self.NONE, UNKNOWN, ""
        if isinstance(e, Subq):
            q = e.program
            if isinstance(q, Program) and q.select: return self.record(q.select[0][0], {**steps, **dict(q.ctes)}), UNKNOWN, ""
            return self.NONE, UNKNOWN, ""
        if isinstance(e, PredVal): return self.case([self.const(1), self.const(0)])
        if isinstance(e, Strftime): return self.strftime(e.fmt)
        if isinstance(e, Between):
            x = R(e.expr)
            for bound in (e.lo, e.hi):
                t, b = self.compare(x, R(bound), "BETWEEN")
                if t == CONTRA: return self.NONE, t, b
            return (self.NONE,) + self.between(R(e.lo), R(e.hi))
        if isinstance(e, Cmp): return (self.NONE,) + self.compare(R(e.l), R(e.r), e.op)
        if isinstance(e, In):
            x = R(e.expr)
            for v in e.values:
                if isinstance(v, Subq): continue
                t, b = self.compare(x, R(v), "=")
                if t == CONTRA: return self.NONE, t, b
            return self.NONE, UNKNOWN, ""
        if isinstance(e, Join): return (self.NONE,) + self.join(e.on.l.table, e.on.l.name, e.on.r.table, e.on.r.name)
        return self.NONE, UNKNOWN, ""

    def verdict(self, e, steps=None, repeated=frozenset()):
        """The verdict of node `e`'s own contract (its operands' records as they are)."""
        _rec, t, b = self._contract(e, steps or {}, repeated)
        return t, b

    # ---------------------------------------------------------------- the whole program
    def unique(self, t, c):
        """Is column c of table t unique: its table's whole primary key, or no value repeated in the rows?"""
        cache = self.__dict__.setdefault("_unique", {})
        if (t, c) not in cache:
            w = self.cat.world
            if w.pk.get(t) == [c]: cache[(t, c)] = True
            else:
                try:
                    n, d = self.cat.con.execute('SELECT COUNT("%s"), COUNT(DISTINCT "%s") FROM "%s"' % (c, c, t)).fetchone()
                    cache[(t, c)] = bool(n) and n == d
                except Exception: cache[(t, c)] = False
        return cache[(t, c)]

    def repeated(self, joins):
        """The tables whose rows a FROM clause's joins repeat: along the join tree from a table T, a step from a
        parent to its child (the child holds the foreign key) gives several child rows per T row. A join to a step
        has no established direction and repeats nothing we can prove. Read off the join conditions only, so the
        binder (on a FROM being built) and the verifier (on a finished one) compute it the same way."""
        edges = []
        for j in joins:
            on = getattr(j, "on", None)
            if not isinstance(on, Cmp) or not isinstance(on.l, Col) or not isinstance(on.r, Col): continue
            a, b = (on.l.table, on.l.name), (on.r.table, on.r.name)
            for c, cc, p, pc in self.cat.world.fks:
                # a link whose child key is unique (a primary key, or unique in the rows) is ONE TO ONE: it repeats nothing
                if ((a, b) == ((c, cc), (p, pc)) or (a, b) == ((p, pc), (c, cc))) and not self.unique(c, cc): edges.append((c, p))
        key = tuple(edges)
        cache = self.__dict__.setdefault("_repeat_cache", {})
        if key in cache: return cache[key]
        adj = collections.defaultdict(list)
        for child, parent in edges:
            adj[parent].append((child, True)); adj[child].append((parent, False))
        rep = set()
        for t in set(x for e in edges for x in e):
            seen, stack = {t}, [t]
            while stack:
                x = stack.pop()
                for y, down in adj[x]:
                    if y in seen: continue                    # the edge back to where the walk came from is no new step
                    if down: rep.add(t)
                    seen.add(y); stack.append(y)
        cache[key] = frozenset(rep)
        return cache[key]

    def nodes(self, p, inherited=None):
        """Every expression node of a program, at every depth and in every scope, with the steps in scope and the
        query's multiplicity: THE ONE WALK, read by the final check and by every report."""
        from dataclasses import fields, is_dataclass
        if isinstance(p, SetOp):
            for side in (p.left, p.right): yield from self.nodes(side, inherited)
            return
        steps = {**(inherited or {}), **dict(getattr(p, "ctes", ()))}
        for _n, q in getattr(p, "ctes", ()): yield from self.nodes(q, steps)
        rep = self.repeated(getattr(p.scan, "joins", ()))
        stack = [getattr(p, f.name) for f in fields(p) if f.name not in ("ctes", "scan")]
        stack += [j.on for j in getattr(p.scan, "joins", ())]
        for j in getattr(p.scan, "joins", ()):
            on = getattr(j, "on", None)
            if isinstance(on, Cmp) and isinstance(on.l, Col) and isinstance(on.r, Col): yield j, steps, rep
        seen = set()
        while stack:
            e = stack.pop()
            if e is None or isinstance(e, (str, int, float, bool)): continue
            if isinstance(e, (tuple, list)): stack.extend(e); continue
            if isinstance(e, (Program, SetOp)): yield from self.nodes(e, steps); continue
            if is_dataclass(e) and not isinstance(e, type):
                if id(e) in seen: continue
                seen.add(id(e))
                if isinstance(e, (Arith, Agg, Func, Cast, Case, Window, Between, Cmp, In)): yield e, steps, rep
                if isinstance(e, Subq): yield from self.nodes(e.program, steps); continue
                stack.extend(getattr(e, f.name) for f in fields(e))

    def check(self, p):
        """What the final check refuses in a finished program, with the contracts the binder applied: every
        contradiction. Support is preferred when binding, never required: unknown stays an honest diagnostic."""
        out = []
        for e, steps, rep in self.nodes(p):
            t, b = self.verdict(e, steps, rep)
            if t == CONTRA: out.append((type(e).__name__, getattr(e, "op", None) or getattr(e, "fn", None) or getattr(e, "name", None) or "", b))
        return out

    # ---------------------------------------------------------------- during construction
    def admit(self, frames, rec, repeated=frozenset()):
        """A candidate operand, by its record, placed in the operators still open above it (`frames`, innermost
        last): each open operator's contract is applied in turn, with what is already known of its other operands
        (unknown otherwise). Returns the first contradiction, else the verdict of the nearest arithmetic operator.
        The SAME contracts the final check applies to the finished program."""
        cur, nearest = rec, None
        for f in reversed(frames):
            kind = f[0]
            if kind == "STOP": break
            if kind == "ARITH":
                op, side, partner = f[1], f[2], f[3] if len(f) > 3 and f[3] is not None else self.NONE
                cur, t, b = self.arith(op, cur, partner) if side == "l" else self.arith(op, partner, cur)
                if nearest is None: nearest = (t, b)
            elif kind == "AGG": cur, t, b = self.agg(f[1], f[2], cur, frozenset() if len(f) > 3 and f[3] else repeated)   # a window keeps its rows
            elif kind == "CAST": cur, t, b = self.cast(f[1], cur) if f[1] else (cur, UNKNOWN, "")
            elif kind == "FUNC":
                if f[1] is None: t, b = UNKNOWN, ""
                elif f[2] == 0: cur, t, b = self.func(f[1], [cur])
                else: break                                           # a later argument does not become the result
            elif kind == "CMP":                                       # the other side of a comparison, already built
                t, b = self.compare(f[1], cur, f[2] if len(f) > 2 else None)
                return (CONTRA, b) if t == CONTRA else (nearest or (UNKNOWN, ""))
            else: t, b = UNKNOWN, ""                                  # CASE, WINDOW: the value passes through
            if t == CONTRA: return CONTRA, b
        return nearest or (UNKNOWN, "")

    # ---------------------------------------------------------------- the same contracts, run incrementally
    @staticmethod
    def signature(frames):
        """The open operators as a hashable context: each operator, its side, and its known partner's record by
        identity (records are immutable and cached, so identity is exact)."""
        return tuple((f[0], f[1], f[2], id(f[3])) if f[0] == "ARITH" else (f[0], id(f[1]), f[2] if len(f) > 2 else None) if f[0] == "CMP" else tuple(f) for f in frames)

    def admit_cached(self, sig, frames, rec, repeated):
        """`admit`, remembered by its full context: the open operators, the candidate's record, the multiplicity.
        The partner records the signature names by identity are held by the cache entry, so an identity is never
        reused for another record while the entry lives."""
        key = (sig, id(rec), repeated)
        hit = self._admit.get(key)
        if hit is not None and hit[0] is rec: return hit[1]
        v = self.admit(frames, rec, repeated)
        if len(self._admit) > 400000: self._admit.clear()
        self._admit[key] = (rec, v, frames)
        return v

    @staticmethod
    def near(frames):
        """The frames from the slot up to and including the nearest open ARITH (with its known partner), through any
        aggregate, cast or first function argument between; without arithmetic above, up to the outermost such
        aggregate. Empty when a predicate, a later function argument or nothing is above."""
        agg = None
        for i in range(len(frames) - 1, -1, -1):
            f = frames[i]
            if f[0] in ("ARITH", "CMP"): return frames[i:]  # the nearest operator with a known partner
            if f[0] == "AGG": agg = i; continue            # through a summary to the arithmetic above it
            if f[0] == "STOP" or (f[0] == "FUNC" and f[2] not in (0, None)): break
        return frames[agg:] if agg is not None else []

    def at_slot(self, frames, rec, repeated):
        """THE BINDING VERDICT: the candidate judged by the nearest operator (with its known partner) and the casts
        and functions between it and the slot -- the same chain lookahead checks, so the two never disagree. The
        operators further out are not asked about an unfinished expression: they judge its record when it closes,
        and the final check applies them to the finished program."""
        sub = self.near(frames)
        if not sub: return UNKNOWN, ""
        return self.admit_cached(self.signature(sub), sub, rec, repeated if any(f[0] == "AGG" for f in sub) else frozenset())

    def local(self, frames, rec, repeated):
        """Lookahead asks the same local question as the decision (`at_slot`), and needs only whether it excludes."""
        v = self.at_slot(frames, rec, repeated)
        return v if v[0] == CONTRA else (UNKNOWN, "")

    @staticmethod
    def tier(t, b):
        """The binder's preference: 0 strongly supported (rows, documentation, a declared rule), 1 plausible
        (a model's proposal), 2 unknown; None for a contradiction."""
        if t == CONTRA: return None
        if t == SUPPORTED: return 1 if b == "model" else 0
        return 2
