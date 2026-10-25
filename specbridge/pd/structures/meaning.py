"""specbridge.pd.structures.meaning — HOW A COLUMN IS TYPED, AND THE FOUR CLASSES THE LAW IS FITTED OVER.

A column's KIND (count, money, measure, score, share, duration, date ...) is read from its documentation
and its values (`kind_of_col`, `unit_of`), through the same door for the source's columns (the `Typer`,
which types R's programs for the fit) and a target's (`pd.profile`). The law itself sees only the CLASS
of a leaf (`klass`): amount, ratio, time -- what an operator needs -- so that arithmetic R wrote over
measures ports to a database of counts. `result` is the generic algebra of kinds, used to type a filled
tree (a difference of counts is a count; a count over a count is a share).
"""
from __future__ import annotations
import collections, json, os, re, sqlite3, sys

from specbridge.pd.structures.algebra import Agg, Arith, Case, Cast, Col, Const, Func, Program, Window

# kinds beyond `vocab.kind_of`: a date (documented as such, or made by a date function) and a date part
_DATEW = re.compile(r"\btimestamp\b|\bdate\b|\bdatetime\b|\btime of\b|\bwhen the\b", re.I)
_DATE_FN = {"JULIANDAY", "DATE", "DATETIME", "TO_DATE", "TO_TIMESTAMP", "NOW", "CURRENT_DATE", "CURRENT_TIMESTAMP"}
_PART_FN = {"EXTRACT", "STRFTIME", "DATE_PART", "YEAR", "MONTH", "DAY", "DATE_TRUNC"}
_PASS_FN = {"NULLIF", "COALESCE", "ROUND", "ABS", "CEIL", "CEILING", "FLOOR", "GREATEST", "LEAST", "IFNULL",
            "ANONYMOUS", "SQRT", "POWER", "LN", "LOG", "EXP", "TRUNC"}


def kind_of_desc(desc):
    """The kind a documented column has -- `vocab.kind_of` on the words, with a date read first."""
    from specbridge.pd.realize.vocab import kind_of
    if isinstance(desc, dict): desc = " ".join(str(v) for v in desc.values())   # a JSON column's fields
    d = desc or ""
    if re.search(r"\bprimary key\b|\bserial\b|\bforeign key\b|\breferenc(es|ing)\b", d, re.I): return "id"
    if _DATEW.search(d) and not re.search(r"\bnumber of\b|\bcount\b", d, re.I): return "date"
    k = kind_of(d, None)
    if k: return k
    # the declared type, when the words say nothing: an integer/decimal is a measure, a varchar a label
    if re.search(r"\b(integer|int|bigint|smallint|decimal|numeric|real|double|float)\b", d, re.I): return "measure"
    if re.search(r"\b(varchar|text|char|string)\b", d, re.I): return "label"
    return "?"


# constants that convert a unit: percent to fraction, days to years, months to years, hours, thousands ...


def kind_of_col(desc, stat):
    """THE ONE TYPING RULE FOR BOTH SIDES. A target's column is typed here from its description and its
    statistics; R's leaves are typed by `kind_of_desc` from their documentation alone. A date is a date
    by its role in the data before anything the words say."""
    from specbridge.pd.realize.vocab import kind_of
    if stat is not None and getattr(stat, "role", "") == "date": return "date"
    if isinstance(desc, dict): desc = " ".join(str(v) for v in desc.values())
    d = desc or ""
    if stat is None: return kind_of_desc(d)
    k = kind_of(d, stat)
    if not k and _DATEW.search(d): return "date"
    return k or "?"


def unit_of(desc, name=""):
    """The stored unit a normaliser converts FROM, read off the words: a share kept as a percent, a
    duration in days or months, an amount in thousands. "" when nothing says."""
    d = ("%s %s" % (desc or "", name or "")).lower()
    if re.search(r"percent|%|\bpct\b", d): return "percent"
    if re.search(r"\bin thousands\b|\(thousands\)|\bk\$|\bthousands of\b", d): return "thousands"
    if re.search(r"\bin millions\b|\(millions\)|\bmillions of\b", d): return "millions"
    if re.search(r"\bdays?\b", d): return "days"
    if re.search(r"\bmonths?\b", d): return "months"
    if re.search(r"\bhours?\b", d): return "hours"
    if re.search(r"\bminutes?\b", d): return "minutes"
    if re.search(r"\bcents\b", d): return "cents"
    return ""


class Typer:
    """Types every expression of one program against one database's documentation."""

    def __init__(self, meanings, program, kinds=None):
        self.m, self.steps = meanings, {n.lower(): q for n, q in program.ctes}
        self.kinds = {k.lower(): v["kind"] for k, v in (kinds or {}).items()}   # a target's profile, "table.column" -> kind
        self.parent = {}
        self._index(program)

    def _index(self, x):
        """Every constant's parent arithmetic node, so a constant can be typed by its role."""
        from dataclasses import fields, is_dataclass
        if isinstance(x, (list, tuple)):
            for y in x: self._index(y)
            return
        if not is_dataclass(x): return
        if isinstance(x, Arith):
            for side in ("l", "r"):
                if isinstance(getattr(x, side), Const): self.parent[id(getattr(x, side))] = (x, side)
        for f in fields(x): self._index(getattr(x, f.name))


    def kind(self, e):
        if isinstance(e, Col):
            t, c = str(e.table).lower(), str(e.name).lower()
            if self.kinds and "%s.%s" % (t, c) in self.kinds: return self.kinds["%s.%s" % (t, c)]
            if t in self.steps:                              # a step's column: what filled it
                q = self.steps[t]
                inner = Typer(self.m, q, kinds=None); inner.kinds = self.kinds
                for x, alias in q.select:
                    if alias and str(alias).lower() == c: return inner.kind(x)
                for x, alias in q.select:                    # carried up under its own name
                    if not alias and isinstance(x, Col) and str(x.name).lower() == c: return inner.kind(x)
                # a column carried up unlisted (SELECT *): whichever of the step's tables has it
                for tt in [q.scan.table] + [j.table for j in q.scan.joins]:
                    k = inner.kind(Col(tt, c, tt))
                    if k != "?": return k
                return "?"
            if (t, c) not in self.m:                         # a JSON column's field, flattened as name_field
                for (tt, cc), v in self.m.items():
                    if tt == t and isinstance(v, dict) and c.startswith(cc + "_"):
                        return kind_of_desc(v.get(c[len(cc) + 1:], " ".join(map(str, v.values()))))
            return kind_of_desc(self.m.get((t, c)))
        if isinstance(e, Const): return "const"
        if isinstance(e, Cast): return self.kind(e.expr)
        if isinstance(e, Agg):
            return "count" if e.fn.upper() == "COUNT" else self.kind(e.arg) if e.arg is not None else "count"
        if isinstance(e, Window): return self.kind(e.fn) if not isinstance(e.fn, Func) or e.fn.name.upper() not in ("RANK", "ROW_NUMBER", "DENSE_RANK", "NTILE", "PERCENT_RANK") else "rank"
        if isinstance(e, Func):
            n = e.name.upper()
            if n in _DATE_FN: return "date"
            if n in _PART_FN: return "datepart"
            if n in _PASS_FN and e.args: return self.kind(e.args[0])
            return "fn:" + n.lower()
        if isinstance(e, Case):
            ks = {self.kind(x) for _p, x in e.whens} | ({self.kind(e.else_)} if e.else_ is not None else set())
            ks.discard("const")
            return next(iter(ks)) if len(ks) == 1 else ("const" if not ks else "?")
        if isinstance(e, Arith):
            return result(self.kind(e.l), e.op, self.kind(e.r))
        return "?"


# ---------------------------------------------------------------- the one rule
# A CONSTANT'S ROLE IS A UNIT TRANSFORM, and the transforms are a table: what a normaliser divides a unit by
# and what it makes of it, and what "the whole" is in a share's unit (1 of a fraction, 100 of a percent).
# THE FOUR CLASSES OF AN ARITHMETIC LEAF -- what an operator needs of a leaf, and all the law records of it.
# Two amounts add or subtract; an amount over an amount is a ratio; a ratio times an amount is an amount; a
# time is a date or a duration. The profile's kinds (count, money, measure, score ...) are a target's own words
# for its columns; the law is fitted over the classes, so a count fills what R wrote over a measure.
KLASS = {"count": "amount", "money": "amount", "measure": "amount", "score": "amount",
         "share": "ratio", "duration": "time", "date": "time"}


def klass(kind):
    """the class of a profile kind: amount | ratio | time | ? (a leaf no operator asks anything of)"""
    return KLASS.get(str(kind).split()[0] if kind else "?", "?")


def result(a, op, b):
    """WHAT AN OPERATOR MAKES OF TWO KINDS -- the generic algebra, three rules and no cases. A constant scales
    the other side; two of one kind add or subtract to that kind (two dates to a duration); one kind over
    itself is a share; anything else across kinds is named by its parts ("money per count", "share times
    count"). The law does not ask whether such a thing is asked for: it is a stated calculation (goal 4)."""
    if a.startswith("const") or b.startswith("const"):
        return b if a.startswith("const") else a
    if op in ("+", "-"):
        if a == b == "date": return "duration" if op == "-" else "?"
        return a if a == b else "?"
    # A SHARE IS DIMENSIONLESS: it scales a quantity and leaves its kind alone (share x measure is a measure,
    # measure / share is a measure); one kind over itself is a share. Anything else is named by its parts.
    if op == "/":
        if a == b: return "share"
        if b == "share": return a
        return "%s per %s" % (a, b)
    if op == "*":
        if a == "share": return b
        if b == "share": return a
        return "%s times %s" % (a, b)
    return "?"


