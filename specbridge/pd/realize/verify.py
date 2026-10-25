"""specbridge.pd.realize.verify — WHAT MAY BE EMITTED. Correctness is decided here, exactly, on the finished program; nothing
upstream has to be exact for an emitted example to be correct.

    run(seq, caps)      interpret a sequence: ("next", Decision) | ("program", p) | ("refused", why) | ("bug", why)
    judge(p, seq)       LANGUAGE.md §1 and §3 on the built program, and the canonical form; None or why not

Three outcomes are kept apart and counted apart: an INVALID candidate (the language or the IR refused it, or
the judge did), an IMPLEMENTATION ERROR (any other exception: a bug, never relabelled), and, once execution
is added, a TIMEOUT. Today the verifier checks the abstract program only. Execution on a database snapshot
and the parse of the question back to its program join here when the binder and the English exist; until
then an emitted program is "valid in the language", and the report says so.
"""
from __future__ import annotations
import traceback

from specbridge.pd.structures.actions import Decoder, NotInLanguage, CheckerBug, sequence
from specbridge.pd.structures.algebra import Agg, Arith, Cmp, Col, Const, SetOp, Subq, Unsupported, Window, _find


class _Stop(Exception):
    def __init__(self, d): self.d = d


class DeadEnd(Exception):
    """A chooser found no admissible action: the prefix was allowed but has no allowed continuation. An
    invalid candidate (a gap in the checker's soundness), not an implementation error."""


def interpret(choose, caps):
    """Run the decoder with a chooser. ("program", p) | ("refused", why) | ("bug", why) | ("next", Decision)."""
    try:
        return "program", Decoder(choose, caps).program()
    except _Stop as s: return "next", s.d
    except DeadEnd as e: return "refused", "dead end at %s" % (e.args[0][:2],)
    except (NotInLanguage, Unsupported) as e: return "refused", "%s: %s" % (type(e).__name__, str(e)[:70])
    except CheckerBug as e: return "bug", "CheckerBug: " + str(e)[:120]
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return "bug", "%s at %s:%d: %s" % (type(e).__name__, tb.filename.split("/")[-1], tb.lineno, str(e)[:80])


def run(seq, caps):
    """Replay `seq`; stop at the first decision past it."""
    it = iter(seq)
    def choose(d):
        try: _c, a = next(it)
        except StopIteration: raise _Stop(d)
        return a
    kind, x = interpret(choose, caps)
    if kind == "program":
        try: next(it); return "refused", "unconsumed"
        except StopIteration: pass
    return kind, x


def _queries(p):
    if isinstance(p, SetOp): yield from _queries(p.left); yield from _queries(p.right); return
    yield p
    for _n, q in p.ctes: yield from _queries(q)
    for s in _find((p.select, p.where, p.having, p.order), Subq): yield from _queries(s.program)


# USEFULNESS IS MEASURED, NOT ENFORCED, in the clean baseline: the baseline guarantees correct SQL consistent with
# known semantics (specbridge.pd.realize.semantics); whether an expression is useful to a human is reported by `policies`. A policy may
# be switched on here to exclude what it names, and is then a declared choice of the benchmark, never of meaning.
ENFORCE = {"duplicates": False}


def _every(x, cls):
    """Every node of a class at every depth -- nested inside another of its class too (`algebra._find` stops at the
    first match, so a policy walking with it never saw an x / x inside a larger calculation)."""
    out = []
    def walk(y):
        if y is None or isinstance(y, (str, int, float, bool)): return
        if isinstance(y, cls): out.append(y)
        if isinstance(y, (tuple, list)):
            for z in y: walk(z)
        elif hasattr(y, "__dataclass_fields__"):
            for f in y.__dataclass_fields__: walk(getattr(y, f))
    walk(x)
    return out


def policies(p, seq, size_cap=None):
    """The OPTIONAL policies a correct program violates -- never a correctness verdict:
        size        more decisions than the longest source program
        duplicate   a repeated operand, CASE condition, AND/OR branch, or list item
        uninformative  a cast, scalar function or aggregate of constants only (`round(2, 2)`, `AVG(2)`)"""
    from specbridge.pd.structures.algebra import Arith, Case, And, Or
    out = []
    if size_cap and len(seq) > size_cap: out.append("size")
    from specbridge.pd.realize.semantics import same_operands
    dup = any(a.op in "-/" and same_operands(a) for a in _every(p, Arith))            # nested ones too
    dup = dup or any(len({w for w, _v in c.whens}) < len(c.whens) for c in _every(p, Case))
    dup = dup or any(len(set(x.preds)) < len(x.preds) for x in _every(p, (And, Or)))
    for q in _queries(p):
        for xs in (q.select, q.group, q.order):
            items = [x[0] if isinstance(x, tuple) else x for x in xs]
            if len(items) != len(set(items)): dup = True
    if dup: out.append("duplicate")
    if uninformative(p): out.append("uninformative")
    return out


def uninformative(p):
    """A cast, a scalar function or an aggregate whose arguments read no data: its value does not depend on the
    rows. A POLICY of the benchmark (the IR admits it, and R happens never to contain one), enforced at the
    measurement of usefulness, never enforced by the meaning checker."""
    from specbridge.pd.structures.algebra import Cast, Func, Agg
    from specbridge.pd.structures.actions import reads_data, CLOCK_FUNCS, WINDOW_FUNCS
    return any(not reads_data(x.expr) for x in _every(p, Cast)) or \
        any(x.name.lower() not in CLOCK_FUNCS | WINDOW_FUNCS and not reads_data(x.args) for x in _every(p, Func)) or \
        any(x.arg is not None and not reads_data(x.arg) for x in _every(p, Agg))


def _own_nodes(x):
    """Every node of one query's own clause, stopping at a nested subquery (its own scope)."""
    from dataclasses import fields, is_dataclass
    out, stack = [], [x]
    while stack:
        e = stack.pop()
        if e is None or isinstance(e, (Subq, SetOp)) or type(e).__name__ == "Program": continue
        if isinstance(e, (tuple, list)): stack.extend(e); continue
        if is_dataclass(e) and not isinstance(e, type):
            out.append(e); stack.extend(getattr(e, f.name) for f in fields(e))
    return out


def _own_cols(x):
    """The columns of one query's own clauses: a nested subquery is its own scope and is judged by itself."""
    from dataclasses import fields, is_dataclass
    out, stack = [], [x]
    while stack:
        e = stack.pop()
        if e is None or isinstance(e, (Subq, SetOp)) or type(e).__name__ == "Program": continue
        if isinstance(e, Col): out.append(e)
        elif isinstance(e, (tuple, list)): stack.extend(e)
        elif is_dataclass(e) and not isinstance(e, type): stack.extend(getattr(e, f.name) for f in fields(e))
    return out


from specbridge.pd.structures.algebra import nested_aggregate


def judge(p, seq):
    """LANGUAGE.md §1 and §3 on the built program, and the canonical form. None, or why not."""
    if any(isinstance(a.l, Const) and isinstance(a.r, Const) for a in _find(p, Arith)): return "constant expression"
    if any(isinstance(c.l, Const) and isinstance(c.r, Const) for c in _find(p, Cmp)): return "constant expression"
    for q in _queries(p):
        if q.limit is not None and not q.order: return "LIMIT without ORDER"
        if q.where is not None and any(isinstance(x, (Agg, Window)) for x in _own_nodes(q.where)): return "aggregate in WHERE"
        if nested_aggregate((q.select, q.having, q.order)): return "nested aggregate"
        if not q.select: return "empty SELECT"
        if ENFORCE["duplicates"]:
            for xs in (q.select, q.group, q.order):
                items = [x[0] if isinstance(x, tuple) else x for x in xs]
                if len(items) != len(set(items)): return "repeated list item"
        inscope = {str(q.scan.table)} | {str(j.table) for j in q.scan.joins}
        for c in _own_cols((q.select, q.where, q.group, q.having, q.order)):
            if c.alias != "?" and c.name != "k" and c.alias not in inscope: return "step column out of scope"
    # REPRESENTABLE: the program's own canonical sequence rebuilds the same program. (The drawn sequence may be
    # another derivation of it -- a node built twice is merged into one object -- which is not an error.)
    from specbridge.pd.structures.actions import rebuild
    try:
        again = sequence(p); q, _ = rebuild(again)
    except Exception as e: return "not representable: %s" % type(e).__name__
    if sequence(q) != again: return "not canonical"
    return None
