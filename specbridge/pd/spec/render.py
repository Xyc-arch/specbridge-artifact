"""specbridge.pd.spec.render -- DETERMINISTIC TASK TEXT FROM THE IR, with each constructor's meaning rendered by contract.

    spec(p, cat)          the program as data: every operation and condition, with the type each value has in SQLite
    english(s)            controlled English from the contracts (docs/RENDER.md): the clauses in SQL's logical order
                          (rows, joins, filter, groups, group filter, outputs, duplicates, order, limit), formulas over
                          letters defined once per instruction, numbered steps
    determinacy(s)        what the SQL leaves undetermined (ties under row_number, a limit without an order, ...)
    grader(s)             how an answer is compared -- or an explicit refusal naming what it cannot grade

FAIL CLOSED: a constructor or a semantic detail without a contract raises `Unrenderable` naming it. Nothing is
omitted, approximated or rendered by a generic phrase. Columns are named by their exact `table.column`, with the
catalogue's words beside them. Templates change wording only; the specification is authoritative.

What is established and what is not: docs/RENDER.md.
"""
from __future__ import annotations
import json

import collections
from specbridge.pd.structures.algebra import (Agg, And, Arith, Between, Case, Cast, Cmp, Col, Const, Func, In, IsNull, Like, Not, Or, PredVal,
                      Program, SetOp, Strftime, Subq, Window)


class Unrenderable(Exception):
    pass


# ================================================================ the specification (types follow SQLite)
def spec(p, cat):
    if isinstance(p, SetOp): raise Unrenderable("a set operation (UNION / INTERSECT / EXCEPT)")
    if not isinstance(p, Program): raise Unrenderable("a %s at the top level" % type(p).__name__)
    from specbridge.pd.structures.algebra import _find, Subq
    steps = []
    def inner(q):                                        # the FROM-subquery steps a program reads, INCLUDING those inside its
        if not isinstance(q, Program): return            # value subqueries -- both were dropped, leaving "each `t` record"
        add(q.ctes)
        for sq in _find((q.select, q.where, q.group, q.having, q.order), Subq): inner(sq.program)
    def add(ctes):
        for name, q in ctes:
            if any(s["name"].lower() == name.lower() for s in steps): raise Unrenderable("two intermediate results named %s" % name)
            if name.lower() in {r[0].lower() for r in cat.con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}:
                raise Unrenderable("an intermediate result named like the stored table %s (it would read itself)" % name)
            inner(q)
            steps.append({"name": name, "number": len(steps) + 1, "query": _query(q, cat, {s["name"]: s for s in steps}, top=False)})
    add(p.ctes)
    for sq in _find((p.select, p.where, p.group, p.having, p.order), Subq): inner(sq.program)
    out = {"steps": steps, "query": _query(p, cat, {s["name"]: s for s in steps}, top=True)}
    _complete(out); return out


def _complete(s):
    """COMPLETENESS, checked on the specification before any text exists: every record set read is a stored table or an
    EARLIER step, and every reference to a step's column names an existing step, a position inside its outputs, and the
    output that carries that name. Anything else is refused -- never worded."""
    by = {st["name"]: st for st in s["steps"]}
    def walk(x, here):
        if isinstance(x, dict):
            if x.get("op") == "step_output":
                st = by.get(x["step"])
                if st is None or st["number"] >= here: raise Unrenderable("a reference to step %s, which is not an earlier step" % x["step"])
                outs = st["query"]["outputs"]
                if not 1 <= x["position"] <= len(outs): raise Unrenderable("column (%d) of step %d does not exist" % (x["position"], st["number"]))
                o = outs[x["position"] - 1]; nm = x["name"].lower()
                named = (o["alias"] or "").lower() == nm or (o["alias"] is None and (
                    (o["expr"]["op"] == "column" and o["expr"]["ref"].split(".", 1)[1].lower() == nm) or
                    (o["expr"]["op"] == "step_output" and o["expr"].get("name", "").lower() == nm) or nm == "o%d" % (x["position"] - 1)))
                if not named: raise Unrenderable("column %s of step %d resolves to an output with another name" % (x["name"], st["number"]))
            for k in ("source", "joins"):
                pass
            for v in x.values(): walk(v, here)
        elif isinstance(x, (list, tuple)):
            for v in x: walk(v, here)
    def sources(q, here):
        for src in [q["source"]] + list(q["joins"]):
            if src["step"] and (src["table"] not in by or by[src["table"]]["number"] >= here):
                raise Unrenderable("reads step %s before it is defined" % src["table"])
    for st in s["steps"]: sources(st["query"], st["number"]); walk(st["query"], st["number"])
    sources(s["query"], len(s["steps"]) + 1); walk(s["query"], len(s["steps"]) + 1)


def _declared(cat, t, c):
    """(value type, column affinity). The AFFINITY follows SQLite's rules for the declared type (INT -> integer; CHAR,
    CLOB, TEXT -> text; REAL, FLOA, DOUB -> real; anything else -> numeric). The VALUE TYPE is read from the stored values
    (`typeof` of every non-missing value, which SQLite does not constrain by the declaration): integer, real (numbers
    with a decimal among them), text, "mixed" (numbers and text both), or unknown (no stored value)."""
    memo = cat.__dict__.setdefault("_render_types", {})
    if t not in memo:
        memo[t] = {r[1]: (r[2] or "").upper() for r in cat.con.execute('PRAGMA table_info("%s")' % t)}
    d = memo[t].get(c, "")
    aff = ("integer" if "INT" in d else "text" if any(k in d for k in ("CHAR", "CLOB", "TEXT")) else
           "real" if any(k in d for k in ("REAL", "FLOA", "DOUB")) else "numeric")
    tm = cat.__dict__.setdefault("_render_typeof", {})
    if (t, c) not in tm:
        try: kinds = {r[0] for r in cat.con.execute('SELECT DISTINCT typeof("%s") FROM "%s" WHERE "%s" IS NOT NULL' % (c, t, c))}
        except Exception: kinds = set()
        tm[(t, c)] = ("unknown" if not kinds else "integer" if kinds == {"integer"} else "real" if kinds <= {"integer", "real"}
                      else "text" if kinds == {"text"} else "mixed")
    return tm[(t, c)], aff


def _parses(cat, t, c):
    """A row fact: does every stored value of the column read as a number (so SQLite's conversion of it is exact)?
    Read from the rows themselves, every distinct value."""
    memo = cat.__dict__.setdefault("_render_parses", {})
    if (t, c) not in memo:
        ok = True
        try:
            for (v,) in cat.con.execute('SELECT DISTINCT "%s" FROM "%s" WHERE "%s" IS NOT NULL' % (c, t, c)):
                try: float(str(v).strip()) if str(v).strip() == str(v) else (_ for _ in ()).throw(ValueError())
                except Exception: ok = False; break
        except Exception: ok = False
        memo[(t, c)] = ok
    return memo[(t, c)]


def _label(cat, t, c):
    role, qn = "", ""
    try:
        from specbridge.pd.realize.semantic import load
        v = cat.__dict__.setdefault("_render_cols", load(cat)["columns"]).get("%s.%s" % (t, c), {})
        qn, role = (v.get("quantity") or "").strip(), v.get("semantic_role") or ""
    except Exception: pass
    return (qn or cat.name(t, c)), role


def _query(q, cat, steps, top):
    if not isinstance(q, Program): raise Unrenderable("a %s where a query is expected" % type(q).__name__)
    tables = {q.scan.alias: q.scan.table, **{j.alias: j.table for j in q.scan.joins}}
    real = cat.__dict__.setdefault("_render_real", {r[0].lower() for r in cat.con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")})
    for t in tables.values():                            # FAIL CLOSED: every record set read is a stored table or a defined step
        if t not in steps and t.lower() not in real: raise Unrenderable("reads `%s`, which is neither a table nor a defined step" % t)
    seen = collections.Counter(tables.values())
    env = {"cat": cat, "steps": steps, "tables": set(tables.values()) | set(tables),
           "dup": {t for t, n in seen.items() if n > 1}}      # a table read twice (self-join): name each side by its alias
    E = lambda e: _expr(e, env)
    joins = []
    for j in q.scan.joins:
        if j.on is None: raise Unrenderable("a join without a condition (a cross product)")
        joins.append({"table": j.table, "step": j.table in steps, "kind": j.kind, "on": _pred(j.on, env), "alias": j.alias if j.table in env["dup"] else None})
    outs = [{"position": i + 1, "expr": E(e), "alias": a} for i, (e, a) in enumerate(q.select)]
    aggregated = bool(q.group) or any(_has_agg(o["expr"]) for o in outs)
    return {"source": {"table": q.scan.table, "step": q.scan.table in steps, "alias": q.scan.alias if q.scan.table in env["dup"] else None}, "joins": joins,
            "where": _pred(q.where, env) if q.where is not None else None,
            "group": [E(g) for g in q.group], "single_group": aggregated and not q.group,
            "having": _pred(q.having, env) if q.having is not None else None,
            "outputs": outs, "distinct": bool(q.distinct),
            "order": [{"expr": E(e), "dir": d.lower()} for e, d in q.order],
            "limit": q.limit, "offset": q.offset or 0, "top": top}


def _has_agg(x):
    """An aggregate at this query's level (not inside a window or a subquery, which have their own levels)."""
    if isinstance(x, dict):
        if x.get("op") == "aggregate": return True
        if x.get("op") in ("within", "running", "window", "subquery"): return False
        return any(_has_agg(v) for v in x.values())
    if isinstance(x, list): return any(_has_agg(v) for v in x)
    return False


WINDOW_FNS = {"rank", "dense_rank", "row_number", "percent_rank", "cume_dist", "ntile", "first_value", "last_value", "lag", "lead"}
SCALAR = {"sqrt", "power", "pow", "log", "ln", "log10", "exp", "abs", "round", "coalesce", "ifnull", "nullif",
          "greatest", "least", "max", "min", "current_date", "current_timestamp"}


def _expr(e, env):
    E = lambda x: _expr(x, env)
    cat, steps = env["cat"], env["steps"]
    if isinstance(e, Col):
        if e.table in steps:
            q = steps[e.table]["query"]
            nm = e.name.lower()                              # SQL names are case-insensitive; the NAME decides first --
            i = next((k for k, o in enumerate(q["outputs"]) if (o["alias"] or "").lower() == nm), None)   # "o0" need not be column 1
            if i is None and e.name[:1] == "o" and e.name[1:].isdigit() and int(e.name[1:]) < len(q["outputs"]) and q["outputs"][int(e.name[1:])]["alias"] is None:
                i = int(e.name[1:])                          # the position rule only for an UNNAMED output; otherwise refuse
            if i is None:                                    # an unaliased output named by the column or step output it passes on
                i = next((k for k, o in enumerate(q["outputs"]) if o["alias"] is None and (
                    (o["expr"]["op"] == "column" and o["expr"]["ref"].split(".", 1)[1].lower() == nm) or
                    (o["expr"]["op"] == "step_output" and o["expr"].get("name", "").lower() == nm))), None)
            if i is None or i >= len(q["outputs"]): raise Unrenderable("a reference to column %s of step %s" % (e.name, e.table))
            return {"op": "step_output", "step": e.table, "number": steps[e.table]["number"], "position": i + 1,
                    "name": e.name, "type": q["outputs"][i]["expr"]["type"]}
        if e.table not in env["tables"]: raise Unrenderable("a correlated reference to %s.%s (an outer query's column)" % (e.table, e.name))
        label, role = _label(cat, e.table, e.name)
        t, aff = _declared(cat, e.table, e.name)
        return {"op": "column", "ref": "%s.%s" % (e.alias if e.table in env.get("dup", ()) else e.table, e.name), "label": label, "role": role, "type": t, "affinity": aff,
                "parses": t == "text" and _parses(cat, e.table, e.name), "values": t}
    if isinstance(e, Const):
        v = e.value
        t = "text" if isinstance(v, str) else "real" if isinstance(v, float) else "integer" if isinstance(v, int) and not isinstance(v, bool) else "unknown"
        return {"op": "value", "value": v, "type": t}
    if isinstance(e, Arith):
        l, r = E(e.l), E(e.r)
        for x in (l, r):
            if _texty(x): raise Unrenderable("arithmetic on a text value that may not be a number (SQLite reads its numeric prefix, else 0)")
        tl, tr = l["type"], r["type"]
        num = lambda t: t in ("integer", "real")
        if e.op == "/":
            # THE COMPILER'S DIVISION (algebra.emit_expr): the dividend is cast to REAL unless it already is a REAL cast
            # or a decimal literal, so every compiled division is exact. A NUMERIC cast is not recast: it could stay an
            # integer and divide as integers, so it fails closed (in Cast below).
            kind, t = "divide", "real"
        elif e.op == "%": kind, t = "modulo", "integer"
        else:
            kind = {"+": "add", "-": "subtract", "*": "multiply"}[e.op]
            t = "real" if "real" in (tl, tr) and num(tl) and num(tr) else "integer" if tl == tr == "integer" else "unknown"
        return {"op": kind, "args": [l, r], "type": t}
    if isinstance(e, Agg):
        fn = e.fn.upper()
        if fn not in ("COUNT", "SUM", "AVG", "MIN", "MAX"): raise Unrenderable("the aggregate %s" % fn)
        # CONDITIONAL AGGREGATION WRITTEN WITH CASE (2026-10-13, rule COND): one WHEN, the aggregate of THEN over the records the
        # condition keeps, is the filtered aggregate -- COUNT(CASE WHEN c THEN <non-missing value> END) = COUNT(*) FILTER (c);
        # COUNT/SUM/AVG/MIN/MAX(CASE WHEN c THEN x END) = the same aggregate of x FILTER (c); SUM(CASE WHEN c THEN x ELSE 0 END)
        # = that filtered sum except that it is 0, not missing, when no record of a non-empty group meets c.
        if isinstance(e.arg, Case) and len(e.arg.whens) == 1 and e.filter is None and not e.distinct:
            (w, x), els = e.arg.whens[0], e.arg.else_
            zero = isinstance(els, Const) and els.value == 0 and fn == "SUM"
            if els is None or zero:
                if fn == "COUNT" and isinstance(x, Const) and x.value is not None: arg = None
                else: arg = E(x)
                return {"op": "aggregate", "fn": fn, "distinct": False, "arg": arg, "filter": _pred(w, env), "zero_if_none": zero,
                        "type": "integer" if fn == "COUNT" else "real" if fn == "AVG" else arg["type"]}
        a = None if e.arg is None else E(e.arg)
        if fn in ("SUM", "AVG") and a is not None and _texty(a):
            raise Unrenderable("%s of a text value that may not be a number (SQLite reads its numeric prefix, else 0)" % fn)
        t = "integer" if fn == "COUNT" else "real" if fn == "AVG" else a["type"]
        return {"op": "aggregate", "fn": fn, "distinct": bool(e.distinct), "arg": a,
                "filter": None if e.filter is None else _pred(e.filter, env), "type": t}
    if isinstance(e, Strftime):
        part = {"%Y": "year", "%Y-%m": "year-month", "%m": "month", "%Y-%m-%d": "date", "%d": "day of the month"}.get(e.fmt)
        if part is None: raise Unrenderable("the date format %s" % e.fmt)
        return {"op": "date_part", "part": part, "fmt": e.fmt, "arg": E(e.expr), "type": "text"}
    if isinstance(e, Cast):
        t = str(e.type).upper(); a = E(e.expr)
        if t in ("REAL", "FLOAT", "DOUBLE", "INTEGER", "INT", "BIGINT") and _texty(a):
            raise Unrenderable("a numeric cast of a text value that may not be a number")
        if t in ("REAL", "FLOAT", "DOUBLE"): return {"op": "as_real", "arg": a, "type": "real"}
        if t in ("INTEGER", "INT", "BIGINT"): return {"op": "truncate", "arg": a, "type": "integer"}
        if t in ("TEXT", "VARCHAR", "CHAR"):
            if a["type"] not in ("integer", "text"):         # a decimal's text form is SQLite's float formatting
                raise Unrenderable("a cast to TEXT of a value that may be a decimal (its text form is SQLite's float formatting)")
            return {"op": "as_text", "arg": a, "type": "text"}
        raise Unrenderable("a cast to %s (its value may stay an integer or become a decimal)" % t)
    if isinstance(e, Func):
        n = e.name.lower()
        if n not in SCALAR: raise Unrenderable("the function %s" % e.name)
        if e.template:                                       # the compiler emits the template: it must be the call R defines
            sqlite_name = {"greatest": "max", "least": "min"}.get(n, n)
            plain = "%s(%s)" % (sqlite_name, ", ".join("__ARG%d__" % i for i in range(len(e.args))))
            ok = {plain.replace(" ", "").lower()} | ({sqlite_name} if not e.args else set())
            if e.template.replace(" ", "").lower() not in ok:
                raise Unrenderable("the function %s compiled as %s" % (e.name, e.template))
        args = [E(x) for x in e.args]
        if n not in ("coalesce", "ifnull", "nullif", "current_date", "current_timestamp") and any(_texty(x) for x in args):
            raise Unrenderable("the function %s of a text value that may not be a number" % e.name)
        if n in ("current_date", "current_timestamp"): return {"op": "today", "time": n != "current_date", "type": "text"}
        if n == "round":
            if len(args) > 1 and args[1]["op"] != "value": raise Unrenderable("round to a computed number of digits")
            return {"op": "round", "digits": int(args[1]["value"]) if len(args) > 1 else 0, "arg": args[0], "type": "real"}
        if n in ("coalesce", "ifnull"): return {"op": "first_present", "args": args, "type": _common(args)}
        if n == "nullif": return {"op": "nullif", "args": args, "type": args[0]["type"]}
        if n in ("greatest", "least", "max", "min"):
            if len(args) < 2: raise Unrenderable("the scalar %s of one value" % n)
            return {"op": "larger" if n in ("greatest", "max") else "smaller", "args": args, "type": _common(args)}
        name = {"pow": "power", "log": "log10" if len(args) == 1 else "log_base"}.get(n, n)
        return {"op": "fn", "name": name, "args": args, "type": args[0]["type"] if name == "abs" else "real"}
    if isinstance(e, Window):
        part = [E(x) for x in e.partition]; order = [{"expr": E(x), "dir": d.lower()} for x, d in e.order]
        if isinstance(e.fn, Agg):
            a = E(e.fn)
            return {"op": "running" if order else "within", "agg": a, "partition": part, "order": order, "type": a["type"]}
        n = getattr(e.fn, "name", "").lower()
        if n not in WINDOW_FNS: raise Unrenderable("the window function %s" % n)
        args = [E(x) for x in e.fn.args]
        t = "real" if n in ("percent_rank", "cume_dist") else "integer" if n in ("rank", "dense_rank", "row_number", "ntile") else (args[0]["type"] if args else "unknown")
        return {"op": "window", "name": n, "args": args, "partition": part, "order": order, "type": t}
    if isinstance(e, Case):
        whens = [{"if": _pred(w, env), "then": E(v)} for w, v in e.whens]
        els = None if e.else_ is None else E(e.else_)
        return {"op": "case", "whens": whens, "else": els, "type": _common([w["then"] for w in whens] + ([els] if els else []))}
    if isinstance(e, PredVal): return {"op": "truth", "cond": _pred(e.pred, env), "type": "integer"}
    if isinstance(e, Subq):
        sub = _query(e.program, cat, steps, top=False)
        if len(sub["outputs"]) != 1: raise Unrenderable("a scalar subquery with %d columns" % len(sub["outputs"]))
        return {"op": "subquery", "query": sub, "type": sub["outputs"][0]["expr"]["type"],
                "single_row": sub["single_group"] or sub["limit"] == 1}
    raise Unrenderable("the constructor %s" % type(e).__name__)


def _texty(x):
    """A value SQLite would convert from text in arithmetic, where that conversion is not exact: a text column whose
    values do not all read as numbers, a text literal, text() of something, a date part other than digits."""
    op = x["op"]
    if op == "column": return x["type"] == "mixed" or (x["type"] == "text" and not x.get("parses"))
    if op == "value": return x["type"] == "text"
    if op == "as_text": return True
    if op == "date_part": return x["fmt"] not in ("%Y", "%m", "%d")
    return x["type"] == "text" and op not in ("step_output",)


def _common(xs):
    ts = {x["type"] for x in xs if x}
    return ts.pop() if len(ts) == 1 else ("real" if ts <= {"integer", "real"} else "unknown")


def _pred(x, env):
    E = lambda e: _expr(e, env)
    if isinstance(x, And): return {"op": "all", "args": [_pred(a, env) for a in x.preds]}
    if isinstance(x, Or): return {"op": "any", "args": [_pred(a, env) for a in x.preds]}
    if isinstance(x, Not): return {"op": "not", "arg": _pred(x.pred, env)}
    if isinstance(x, Cmp):
        l, r = E(x.l), E(x.r)
        return {"op": "compare", "cmp": x.op, "left": l, "right": r, "mode": _mode(l, r)}
    if isinstance(x, Between):
        a, lo, hi = E(x.expr), E(x.lo), E(x.hi)
        m1, m2 = _mode(a, lo), _mode(a, hi)
        if m1 != m2: raise Unrenderable("a BETWEEN whose bounds compare differently (%s, %s)" % (m1, m2))
        return {"op": "between", "neg": x.neg, "arg": a, "lo": lo, "hi": hi, "mode": m1}
    if isinstance(x, IsNull): return {"op": "missing", "neg": x.neg, "arg": E(x.expr)}
    if isinstance(x, In):
        if len(x.values) == 1 and isinstance(x.values[0], Subq):
            sub = _query(x.values[0].program, env["cat"], env["steps"], top=False)
            if len(sub["outputs"]) != 1: raise Unrenderable("IN a subquery with %d columns" % len(sub["outputs"]))
            return {"op": "in_query", "neg": x.neg, "arg": E(x.expr), "query": sub}
        if any(isinstance(v, Subq) for v in x.values): raise Unrenderable("an IN list mixing values and a subquery")
        a, vals = E(x.expr), [E(v) for v in x.values]
        modes = {_mode(a, v) for v in vals}
        if len(modes) > 1: raise Unrenderable("an IN list whose values compare differently (%s)" % ", ".join(sorted(modes)))
        return {"op": "one_of", "neg": x.neg, "arg": a, "values": vals, "mode": modes.pop()}
    if isinstance(x, Like): return {"op": "matches", "neg": x.neg, "arg": E(x.expr), "pattern": E(x.pattern)}
    if isinstance(x, Subq): return {"op": "exists", "query": _query(x.program, env["cat"], env["steps"], top=False)}
    raise Unrenderable("the condition %s" % type(x).__name__)


def _affinity(x):
    """SQLite's affinity of an operand: a column's declared affinity, a CAST's type; anything else has none."""
    if x["op"] == "column": return x["affinity"]
    if x["op"] == "as_real": return "real"
    if x["op"] == "truncate": return "integer"
    if x["op"] == "as_text": return "text"
    return None


def _mode(a, b):
    """How SQLite compares a and b (datatype3.html, 'Type Conversions Prior To Comparison'): an operand with numeric
    affinity applies numeric affinity to a text or affinity-less other side; one with text affinity applies text
    affinity to an affinity-less other side; otherwise values compare by storage class (numbers before text).
    Returns "number", "text", "as a number" (text converted), "as text" (a number converted); fails closed when the
    comparison would be decided by storage class between a number and text (always the same way)."""
    num = lambda t: t in ("integer", "real")
    ta, tb, fa, fb = a["type"], b["type"], _affinity(a), _affinity(b)
    if "mixed" in (ta, tb): raise Unrenderable("a comparison with a column holding both numbers and text")
    if ta == "unknown" or tb == "unknown":
        if (ta == "text" or tb == "text") and not (fa or fb): raise Unrenderable("a comparison of text with a value of unknown type")
        return "number" if (num(ta) or num(tb) or fa in ("integer", "real", "numeric") or fb in ("integer", "real", "numeric")) else "text"
    if num(ta) and num(tb): return "number"
    if ta == "text" and tb == "text": return "text"
    t_side, n_side = (a, b) if ta == "text" else (b, a)
    ft, fn = _affinity(t_side), _affinity(n_side)
    if fn in ("integer", "real", "numeric"):             # numeric affinity converts the text side, if it reads as a number
        if t_side["op"] == "value" and _is_number(t_side["value"]): return "as a number"
        if t_side["op"] == "column" and t_side.get("parses"): return "as a number"
        raise Unrenderable("a comparison of a number with text that may not read as a number (decided by storage class)")
    if ft == "text" and fn is None: return "as text"      # a text column converts an affinity-less number to text
    raise Unrenderable("a comparison of a number with text, decided by storage class (a number is always less)")


def _is_number(v):
    try: float(v); return True
    except Exception: return False


# ================================================================ determinacy, separate from rendering
def determinacy(s):
    """What the SQL leaves undetermined: (where, what, gradable). The grader handles the gradable ones."""
    out = []
    def walk(q, where):
        if q["limit"] is not None and not q["order"]:
            out.append((where, "a row limit without an order: which rows are kept is not determined", False))
        if q["limit"] is not None and q["order"] and not q["top"]:
            out.append((where, "the first %s rows by an order that may tie: rows tied at the cut are chosen arbitrarily" % q["limit"], False))
        if q["order"] and q["top"]:
            out.append((where, "rows equal on every order key may come in any order" + (", and a tie at the row limit may be filled by any of its rows" if q["limit"] is not None else ""), True))
        for x in _nodes(q):
            if x.get("op") == "window" and x["name"] in ("row_number", "ntile", "first_value", "last_value", "lag", "lead"):
                out.append((where, "%s depends on the order among rows tied on the window's order" % x["name"], False))
            if x.get("op") == "subquery" and not x["single_row"]:
                out.append((where, "a scalar subquery that may return several rows: SQLite takes one, which is not determined", False))
            if x.get("op") == "today":
                out.append((where, "the answer depends on the date the query is run", False))
    for st in s["steps"]: walk(st["query"], "step %d" % st["number"])
    walk(s["query"], "the answer")
    return out


def _nodes(x):
    if isinstance(x, dict):
        yield x
        for v in x.values(): yield from _nodes(v)
    elif isinstance(x, list):
        for v in x: yield from _nodes(v)


# ================================================================ controlled English
CMP = {"=": "equals", "!=": "does not equal", "<": "is less than", "<=": "is at most", ">": "is greater than", ">=": "is at least"}
SYM = {"add": "+", "subtract": "−", "multiply": "×", "divide": "÷", "modulo": "mod"}
ARITH = set(SYM)
FUNCS = {"round", "truncate", "fn", "first_present", "nullif", "larger", "smaller", "as_real", "as_text"}
_CTX = []            # per instruction: its level ("group" or "row") and ONE legend of letters, shared by nested parts
_STEPNO = {}


def _ctx(): return _CTX[-1]


def _col(x):
    ind = ", 1 = yes and 0 = no" if x.get("role") == "indicator" else ""
    if _GAMMA.get("columns") == "natural" and x.get("gamma_col"):         # column identification: the verified meaning
        return "%s%s" % (x["gamma_col"], ind)
    return "%s (`%s`)%s" % (x["label"], x["ref"], ind)


def _val(v):
    if isinstance(v, str): return "'%s'" % v.replace("'", "''")
    return repr(v) if isinstance(v, float) else str(v)


def _value_node(y):
    """A constant: its value -- or, under gamma value resolution, the documented meaning of the stored code."""
    if _GAMMA.get("values") == "natural" and y.get("gamma_label"):
        return "the stored code for '%s'" % y["gamma_label"].replace("'", "''")
    return _val(y["value"])


def _letter(y):
    ctx = _ctx(); key = json.dumps(y, sort_keys=True)
    if key not in ctx["keys"]:
        ctx["keys"][key] = chr(ord("A") + len(ctx["keys"])) if len(ctx["keys"]) < 26 else "X%d" % len(ctx["keys"])
        ctx["legend"].append((ctx["keys"][key], y))
    return ctx["keys"][key]


def term(y, top=False):
    """An expression as a formula: operators and functions written out, every other value a letter of the legend
    (the same expression is the same letter everywhere in the instruction)."""
    op = y["op"]
    if op in ARITH:
        s = "%s %s %s" % (term(y["args"][0]), SYM[op], term(y["args"][1]))
        return s if top else "(%s)" % s
    if op == "value": return _value_node(y)
    if op == "round": return "round(%s, %d)" % (term(y["arg"], True), y["digits"])
    if op == "truncate": return "trunc(%s)" % term(y["arg"], True)
    if op == "as_real": return term(y["arg"], top)                 # a conversion to a decimal changes no value
    if op == "as_text": return "text(%s)" % term(y["arg"], True)
    if op == "fn": return "%s(%s)" % (y["name"], ", ".join(term(a, True) for a in y["args"]))
    if op == "first_present": return "first_present(%s)" % ", ".join(term(a, True) for a in y["args"])
    if op == "nullif": return "nullif(%s, %s)" % (term(y["args"][0], True), term(y["args"][1], True))
    if op in ("larger", "smaller"): return "%s(%s)" % (op, ", ".join(term(a, True) for a in y["args"]))
    return _letter(y)


def value(y):
    """An operand or an output: a formula when it computes, else its noun phrase -- or its letter, when the same
    expression already has one in this instruction (one expression, one name)."""
    if y["op"] in ARITH | FUNCS: return term(y, True)
    k = _ctx()["keys"].get(json.dumps(y, sort_keys=True))
    return k if k else noun(y)


def noun(y):
    op, ctx = y["op"], _ctx()
    if op == "column": return _col(y)
    if op == "value": return _value_node(y)
    if op == "today": return "the current %s (when the query runs)" % ("date and time" if y["time"] else "date")
    if op == "step_output": return "column (%d) of step %d" % (y["position"], y["number"])
    if op == "aggregate" and _STYLE.get("aggregate"): return _STYLE["aggregate"](y)   # a verbalizer style's own phrase
    if op == "aggregate":
        over = "in the group" if ctx["level"] == "group" else "over all kept records"
        filt = ", counting only the records for which %s" % cond(y["filter"]) if y.get("filter") else ""
        a = y["arg"]
        if a is None: return "the number of records %s%s" % (over, filt)
        v = value(a)
        if y["fn"] == "COUNT":
            if y["distinct"]: return "the number of distinct non-missing values of %s %s%s" % (v, over, filt)
            return "the number of records %s whose %s is not missing%s" % (over, v, filt)
        words = {"SUM": "the sum of", "AVG": "the average of", "MIN": "the smallest", "MAX": "the largest"}[y["fn"]]
        if y["fn"] in ("MIN", "MAX") and a["type"] == "text": words += " (in character order)"
        return "%s%s %s %s%s (missing values ignored; %s when there are none)" % (words, " the distinct values of" if y["distinct"] else "", v, over, filt,
                                                                             "0" if y.get("zero_if_none") else "missing")
    if op == "date_part": return "the %s of %s (as text, `%s`)" % (y["part"], value(y["arg"]), y["fmt"])
    if op == "within":
        return "%s taken over the result rows%s" % (_agg_over(y["agg"]), _share(y["partition"]))
    if op == "running":
        return ("%s taken over the result rows%s in order of %s, counting every row up to the current one and every row "
                "tied with it on that order") % (_agg_over(y["agg"]), _share(y["partition"]), _by(y["order"]))
    if op == "window": return _window(y)
    if op == "case":
        rules = ["if %s then %s" % (cond(w["if"]), value(w["then"])) for w in y["whens"]]
        return "the value of the first rule that applies: %s; otherwise %s" % ("; ".join(rules), value(y["else"]) if y["else"] else "missing")
    if op == "truth": return "1 if %s, 0 if not, missing when it cannot be decided" % cond(y["cond"])
    if op == "subquery":
        if y["single_row"]: return "the single value returned by [%s] (missing when it returns no row)" % _instruction(y["query"], nested=True)
        return ("the value in the first row returned by [%s] (missing when it returns no row; when it returns several, which "
                "row comes first is not determined)") % _instruction(y["query"], nested=True)
    raise Unrenderable("no wording for %s" % op)


def _agg_over(a):
    if a["filter"] is not None: raise Unrenderable("a window over a filtered aggregate")
    if a["fn"] == "COUNT":
        if a["arg"] is not None: raise Unrenderable("a windowed COUNT of a value")
        return "the number of records"
    if a["distinct"]: raise Unrenderable("a windowed aggregate of distinct values")
    return {"SUM": "the sum of %s", "AVG": "the average of %s", "MIN": "the smallest %s", "MAX": "the largest %s"}[a["fn"]] % value(a["arg"])


def _share(part): return (" that share the same value of %s" % " and of ".join(value(k) for k in part)) if part else ""


def _by(order):
    def one(o):
        chars = " in character order" if o["expr"]["type"] == "text" else ""
        return "%s %s%s" % (value(o["expr"]), "ascending" if o["dir"] == "asc" else "descending",
                            chars + (" (missing first)" if o["dir"] == "asc" else " (missing last)"))
    return ", then ".join(one(o) for o in order)


def _window(y):
    n, set_, by = y["name"], "the result rows%s" % _share(y["partition"]), _by(y["order"])
    if n == "rank": return "the rank of the row among %s by %s (tied rows share a rank; the next rank skips)" % (set_, by)
    if n == "dense_rank": return "the dense rank of the row among %s by %s (tied rows share a rank; no rank is skipped)" % (set_, by)
    if n == "row_number": return "the position (1, 2, ...) of the row among %s by %s" % (set_, by)
    if n == "percent_rank":
        return "(r − 1) ÷ (m − 1), where r is the rank of the row among %s by %s (tied rows share a rank) and m is the number of those rows; 0 when m is 1" % (set_, by)
    if n == "cume_dist": return "the share of %s by %s that come before the row or tie with it" % (set_, by)
    if n == "ntile":
        if not (y["args"] and y["args"][0]["op"] == "value"): raise Unrenderable("ntile of a computed number")
        k = y["args"][0]["value"]
        return ("the bucket number (1 to %s) of the row when %s, taken in order of %s, are split into %s buckets whose sizes "
                "differ by at most one, earlier buckets taking the extra rows") % (k, set_, by, k)
    if n == "first_value": return "%s of the first row among %s by %s" % (value(y["args"][0]), set_, by)
    if n == "last_value": return "%s of the last row among %s by %s, up to the current row and the rows tied with it" % (value(y["args"][0]), set_, by)
    if n in ("lag", "lead"):
        if len(y["args"]) > 1 and y["args"][1]["op"] != "value": raise Unrenderable("%s by a computed offset" % n)
        k = y["args"][1]["value"] if len(y["args"]) > 1 else 1
        d = value(y["args"][2]) if len(y["args"]) > 2 else "missing"
        return "%s of the row %s position%s %s it among %s by %s (%s when there is no such row)" % (
            value(y["args"][0]), k, "" if k == 1 else "s", "before" if n == "lag" else "after", set_, by, d)
    raise Unrenderable("no wording for the window %s" % n)


def cond(c):
    op = c["op"]
    if op in ("all", "any"):                # a numbered list: "and" / "or" never collide with "between x and y"
        items = "; ".join("[%d] %s" % (i + 1, cond(a)) for i, a in enumerate(c["args"]))
        return "%s of the following hold%s: %s [end]" % ("all" if op == "all" else "at least one", "" if op == "all" else "s", items)
    if op == "not": return "it is not true that %s" % cond(c["arg"])
    tx = {"as text": " (compared as text: the number is written as text first)", "as a number": " (compared as numbers: the text is read as a number)",
          "text": " (compared as text, character by character)"}.get(c.get("mode"), "")
    if op == "compare" and _GAMMA.get("values") == "natural" and c["cmp"] in ("=", "!=") and c["right"].get("gamma_label"):
        # value resolution: the code by its documented meaning; which stored code that is, and how it is spelled, is the
        # agent's to find, so the comparison mode of the spelling is not stated
        return "%s %s '%s'" % (value(c["left"]), "is" if c["cmp"] == "=" else "is not", c["right"]["gamma_label"].replace("'", "''"))
    if op == "compare": return "%s %s %s%s" % (value(c["left"]), CMP[c["cmp"]], value(c["right"]), tx)
    if op == "between": return "%s is %sbetween %s and %s, inclusive%s" % (value(c["arg"]), "not " if c["neg"] else "", value(c["lo"]), value(c["hi"]), tx)
    if op == "missing": return "%s is %s" % (value(c["arg"]), "not missing" if c["neg"] else "missing")
    three = lambda neg: (" (%s when it equals one of them; undetermined when it is missing, or when it equals none of them "
                         "and one of them is missing; otherwise %s)" % (("false", "true") if neg else ("true", "false")))
    if op == "one_of": return "%s %s %s%s%s" % (value(c["arg"]), "is none of" if c["neg"] else "is one of", ", ".join(value(v) for v in c["values"]), tx, three(c["neg"]))
    if op == "in_query":
        empty = " (when [the bracketed query] returns no rows it is %s, even for a missing value; otherwise%s" % (
            "true" if c["neg"] else "false", three(c["neg"])[1:])
        return "%s %s the values returned by [%s]%s" % (value(c["arg"]), "is none of" if c["neg"] else "is among", _instruction(c["query"], nested=True), empty)
    if op == "exists": return "[%s] returns at least one row" % _instruction(c["query"], nested=True)
    if op == "matches":
        return "%s %s the pattern %s (ASCII letters match regardless of case; %% stands for any run of characters and _ for one)" % (
            value(c["arg"]), "does not match" if c["neg"] else "matches", value(c["pattern"]))
    raise Unrenderable("no wording for the condition %s" % op)


def _rows(t, step, alias=None):
    return ("the rows of step %d" % _STEPNO[t]) if step else ("each `%s` record (called `%s`)" % (t, alias) if alias else "each `%s` record" % t)


def _instruction(q, nested=False):
    """One query, its clauses in SQL's logical order. A nested query shares its enclosing instruction's legend."""
    level = "group" if (q["group"] or q["single_group"]) else "row"
    _CTX.append({**_ctx(), "level": level} if nested else {"level": level, "legend": [], "keys": {}})
    try:
        s = ["start from %s" % _rows(q["source"]["table"], q["source"]["step"], q["source"].get("alias"))]
        for j in q["joins"]:
            s.append("combine it with %s for which %s, one combined record per match (%s)" % (
                _rows(j["table"], j["step"], j.get("alias")), cond(j["on"]),
                "a record without a match keeps one combined record with those values missing" if j["kind"] == "left"
                else "a record without a match is dropped"))
        if q["where"] is not None: s.append("keep only the records for which %s" % cond(q["where"]))
        if q["group"]: s.append("group the kept records by %s; each group gives one result row" % " and ".join(value(g) for g in q["group"]))
        elif q["single_group"]: s.append("all kept records form one group, which gives one result row")
        if q["having"] is not None: s.append("keep only the groups for which %s" % cond(q["having"]))
        outs = "; ".join("(%d) %s" % (o["position"], value(o["expr"])) for o in q["outputs"])
        s.append("%s return %s" % ("for each result row," if level == "group" else "for each kept record,", outs))
        if q["distinct"]: s.append("remove duplicate result rows")
        if q["order"]: s.append("order the result rows by %s" % _by(q["order"]))
        if q["limit"] is not None: s.append("keep only the first %s rows%s" % (q["limit"], " after skipping %d" % q["offset"] if q["offset"] else ""))
        text = "; ".join(s)
        if not nested and _ctx()["legend"]:
            defs, i = [], 0
            while i < len(_ctx()["legend"]):                     # a definition may introduce further letters
                name, y = _ctx()["legend"][i]; defs.append("%s is %s" % (name, noun(y))); i += 1
            text += ". Here " + "; ".join(defs)
        return text
    finally:
        _CTX.pop()


NOTES = ("Conventions (SQLite's semantics): a condition that involves a missing value is undetermined, and neither it nor "
         "its negation holds. A formula is missing when any value in it is missing. Numbers are 64-bit integers or IEEE "
         "double-precision reals: ÷ is real-valued division (floating point); a division by 0 is missing; +, − and × of "
         "whole numbers stay whole unless the result leaves the 64-bit range, when it becomes a real; a sum of whole "
         "numbers that leaves that range is an error. a mod b is the remainder after both are truncated to whole numbers "
         "(missing when b truncates to 0). round rounds the double-precision value, halves away from zero; trunc truncates "
         "toward zero; text of a whole number is its decimal digits; sqrt, log10 and ln of a value outside their domain are "
         "missing; first_present is the first of its values that is not missing; nullif(a, b) is a, or missing when a "
         "equals b; larger and smaller are missing when any of their values is missing. Text is compared character by "
         "character, upper and lower case distinct (except in pattern matching). A date part of a value that is not a "
         "date is missing. When grouping or removing duplicates, missing values count as equal to each other.")


_STYLE = {}          # hooks a verbalizer style sets for one call (specbridge.comm.verbal.verbalize); empty = the explicit style
_GAMMA = {}          # rendering controls for this call (specbridge.comm.verbal.gamma, docs/GAMMA.md); empty = the explicit rendering


def english(s, gamma=None):
    """The instruction. `gamma` selects, per angle, a less explicit wording at the sites `specbridge.comm.verbal.gamma` located and
    verified: {"values": "natural"} names a stored value by its documented meaning. The SQL and grader are the same."""
    _GAMMA.clear(); _GAMMA.update(gamma or {})
    _STEPNO.clear(); _STEPNO.update({st["name"]: st["number"] for st in s["steps"]})
    cap = lambda t: t[:1].upper() + t[1:]
    lines = ["Step %d. %s." % (st["number"], cap(_instruction(st["query"]))) for st in s["steps"]]
    final = cap(_instruction(s["query"]))
    lines.append(("Step %d (the answer). %s." % (len(s["steps"]) + 1, final)) if s["steps"] else final + ".")
    return "\n".join(lines) + "\n" + NOTES


# ================================================================ the grader the specification implies
def grader(s):
    """The comparison rule, or a refusal naming every undetermined outcome it cannot grade."""
    bad = ["%s: %s" % (w, what) for w, what, ok in determinacy(s) if not ok]
    if bad: return {"declined": bad}
    q = s["query"]
    tol = [0.5 * 10 ** (-o["expr"]["digits"]) + 1e-9 if o["expr"]["op"] == "round" else None for o in q["outputs"]]
    return {"columns": len(q["outputs"]), "tolerance": tol, "ordered": bool(q["order"]), "limit": q["limit"]}


def reference(p, con, run):
    """The reference answer and how the grader reads it: (rows, tie group sizes, pool for a cut last group). The
    order keys are computed by running the program with them appended and without its LIMIT; consecutive rows equal
    on every key form a tie group; a LIMIT ending inside a group may be filled by any rows of the whole group."""
    import dataclasses
    from specbridge.pd.structures.algebra import emit
    st, rows = run(con, emit(p))
    if st != "ok": raise RuntimeError("the reference does not execute: %s" % (rows,))
    if not p.order: return rows, None, None
    k = len(p.select)
    full = dataclasses.replace(p, select=tuple(p.select) + tuple((e, "k%d" % i) for i, (e, _d) in enumerate(p.order)), limit=None, offset=0)
    st2, frows = run(con, emit(full))
    if st2 != "ok": raise RuntimeError("the reference with its order keys does not execute: %s" % (frows,))
    frows = frows[p.offset or 0:]
    groups, i = [], 0
    while i < len(frows):
        j = i
        while j + 1 < len(frows) and frows[j + 1][k:] == frows[i][k:]: j += 1
        groups.append((i, j + 1)); i = j + 1
    n, sizes, pool = len(rows), [], None
    for a, b in groups:
        if a >= n: break
        if b > n: sizes.append(n - a); pool = [r[:k] for r in frows[a:b]]; break
        sizes.append(b - a)
    return rows, sizes, pool


def grade(g, ref_rows, answer, tie_groups=None, last_pool=None):
    """Positional columns; numeric tolerance from the stated rounding; rows tied on every order key in any order; a
    cut last tie group filled from its whole pool. A declined grader grades nothing. Linear in the rows: multisets are
    compared by canonical keys (numbers on the tolerance grid, or to 9 significant digits), and only rows left
    unmatched are compared pairwise with the exact tolerance -- so a key rounding at a grid boundary cannot fail an
    answer that is within tolerance."""
    import collections, math
    if "declined" in g: return False, "declined: " + "; ".join(g["declined"])
    if answer and len(answer[0]) != g["columns"]: return False, "expected %d columns, got %d" % (g["columns"], len(answer[0]))
    if len(answer) != len(ref_rows): return False, "expected %d rows, got %d" % (len(ref_rows), len(answer))
    tol = g["tolerance"]
    def same(a, b, t):
        if a is None or b is None: return a is None and b is None
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if not (math.isfinite(a) and math.isfinite(b)): return repr(a) == repr(b)
            return abs(a - b) <= t if t is not None else math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-9)
        return str(a) == str(b)
    row_eq = lambda r1, r2: all(same(x, y, t) for x, y, t in zip(r1, r2, tol))
    def key(r):
        out = []
        for v, t in zip(r, tol):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if not math.isfinite(v): out.append(("n", repr(v)))     # inf / -inf / nan: its own key (was a crash)
                else: out.append(("n", round(v / (2 * t)) if t else float("%.9g" % v)))
            else: out.append(("s", None if v is None else str(v)))
        return tuple(out)
    def sub(xs, pool):
        """Is xs a sub-multiset of pool (within tolerance)?"""
        need = collections.Counter(key(x) for x in xs); have = collections.Counter(key(y) for y in pool)
        left_x = [x for x in xs if need[key(x)] > have.get(key(x), 0)]
        if not left_x: return True
        rest = list(pool)                                    # the unmatched residue: pairwise, exact tolerance
        for x in xs:
            for i, y in enumerate(rest):
                if row_eq(x, y): del rest[i]; break
            else: return False
        return True
    if not g["ordered"]:
        ok = sub(answer, ref_rows) and sub(ref_rows, answer)
        return ok, "ok" if ok else "rows differ as a multiset"
    groups, i = tie_groups or [1] * len(ref_rows), 0
    if all(n == 1 for n in groups) and last_pool is None:    # a total order: row by row
        for j, (x, y) in enumerate(zip(answer, ref_rows)):
            if not row_eq(x, y): return False, "row %d differs" % (j + 1)
        return True, "ok"
    for gi, n in enumerate(groups):
        cut = last_pool is not None and gi == len(groups) - 1
        a_, r_ = answer[i:i + n], ref_rows[i:i + n]
        ok = sub(a_, last_pool) if cut else (row_eq(a_[0], r_[0]) if n == 1 else (sub(a_, r_) and sub(r_, a_)))
        if not ok: return False, "rows %d-%d differ (rows tied on every order key may be in any order)" % (i + 1, i + n)
        i += n
    return True, "ok"
