"""specbridge.pd.realize.check — WHICH ACTIONS ARE ADMISSIBLE (LANGUAGE.md §5).

The third of three interfaces. The LANGUAGE (`specbridge.pd.structures.actions`: the vocabulary, the canonical encoding, and the
universe the decoder states at each decision) says which actions exist. The DECODER (`actions.Decoder`)
interprets an action or raises a specific error. The CHECKER, here, decides which actions of the universe
are admissible at the current state. It reads the decoder's state (§4) and never interprets an action or
changes the state; every method returns a subset of the universe it is given.

What each method implements, by clause of LANGUAGE.md §5:
    legality     type (slot classes, literal roles, the anchor of a left constant), determinacy (the
                 query's mode), identity (left operand of - and /, distinct lists, null tests)
    feasibility  obligations against room: unread steps against join slots, list minima, a compound's
                 need for a non-constant leaf, an aggregate window's need for an ordering
Exactness of allow is argued, not verified by search (LANGUAGE.md §9); emission is decided by `specbridge.pd.realize.verify`.
"""
from __future__ import annotations
import collections

from specbridge.pd.structures.algebra import Col, Const, Program, _find
from specbridge.pd.structures.algebra import _aggregating as _agg_walk, nested_aggregate


_AGG = {}


def _aggregating(e):
    """Whether an object aggregates, computed once per object: objects are immutable once built, so the
    answer never changes, and the checker asks it of every candidate at every decision."""
    k = id(e)
    hit = _AGG.get(k)
    if hit is not None and hit[0] is e: return hit[1]
    v = _agg_walk(e); _AGG[k] = (e, v)
    if len(_AGG) > 200000: _AGG.clear()
    return v

_NEST = {}


def _nested(e):
    """nested_aggregate, once per object (objects are immutable once built)."""
    hit = _NEST.get(id(e))
    if hit is not None and hit[0] is e: return hit[1]
    v = nested_aggregate(e); _NEST[id(e)] = (e, v)
    if len(_NEST) > 200000: _NEST.clear()
    return v

MORE, STOP = "MORE", "STOP"


_COLS = {}


def _has_window(e):
    from specbridge.pd.structures.algebra import Window
    from dataclasses import fields, is_dataclass
    seen, stack = set(), [e]
    while stack:
        x = stack.pop()
        if x is None or id(x) in seen: continue
        seen.add(id(x))
        if isinstance(x, Window): return True
        if isinstance(x, (tuple, list)): stack.extend(x)
        elif is_dataclass(x) and not isinstance(x, type): stack.extend(getattr(x, f.name) for f in fields(x))
    return False


def _cols_once(e):
    """The columns inside `e`, each shared node visited once (a program is a graph)."""
    from dataclasses import fields, is_dataclass
    out, seen, stack = [], set(), [e]
    while stack:
        x = stack.pop()
        if x is None or id(x) in seen: continue
        seen.add(id(x))
        if isinstance(x, Col): out.append(x)
        elif isinstance(x, (tuple, list)): stack.extend(x)
        elif is_dataclass(x) and not isinstance(x, type): stack.extend(getattr(x, f.name) for f in fields(x))
    return out


def _leaf_cols(e):
    k = id(e); hit = _COLS.get(k)
    if hit is not None and hit[0] is e: return hit[1]
    v = _cols_once(e); _COLS[k] = (e, v)
    if len(_COLS) > 200000: _COLS.clear()
    return v


def _near_key(s):
    """What lookahead depends on: the chain from the slot to the nearest open operator (`Semantics.near`), with its
    known partner by identity, and the query's multiplicity when an aggregate is in it -- exactly the context of
    the cheap necessary condition, no less."""
    from specbridge.pd.realize.semantics import Semantics
    sub = Semantics.near(getattr(s, "frames", ()))
    if not sub: return None
    b = getattr(s, "binder", None)
    agg = any(f[0] == "AGG" for f in sub)
    return (Semantics.signature(sub), b.repeated(s) if agg and b is not None else None)


LOOK = 1      # how far feasibility looks into what a decision opens: its first slot, not a recursive completion search
WRAPPERS = {"CAST", "FUNC", "STRFTIME"}     # a compound that passes its one operand's slot through (the same state, one level deeper)
BOUNDED_WRAPPERS = True   # a wrapper inside a wrapper's operand is credited only if its own operand takes a leaf


class Checker:

    # ---------------------------------------------------------------- legality of a target object
    def ok_target(self, s, e):
        """May the current slot refer to object `e`? Identity, then determinacy under the mode, then depth."""
        cap = getattr(s, "caps", {}).get("edepth")
        if cap:
            from specbridge.pd.structures.actions import depth_units
            if s.open_depth() + depth_units(e) > cap: return False
        if s.nest == s.item_nest and any(e is x for x in s.exclude): return False
        if s.clause in ("where", "group") and _aggregating(e): return False
        if (s.clause in ("where", "group", "having") or s.in_agg or getattr(s, "win_def", 0)) and _has_window(e): return False
        if not s.in_window and _nested(e): return False
        if s.nulltest and any(e is x for x in s.nulltested): return False
        if s.targets is not None: return any(e is t for t in s.targets)
        if s.mode == "collapsed" and not s.relaxed:
            if any(e is g for g in s.groupkeys) or _aggregating(e): return True
            return all(any(c is g for g in s.groupkeys) for c in _leaf_cols(e)) and not isinstance(e, Col)
        if s.mode == "row" or s.relaxed:
            return not _aggregating(e)
        return True

    def ref_reason(self, s, e, forbid=None, need=None, par=None):
        """The first condition that makes object `e` inadmissible for reuse here, as a labelled rule; None if
        it is admissible. The same conditions `ref_ok` applies, in the same order."""
        from specbridge.pd.structures.actions import _bare
        if s.nest == s.item_nest and any(e is x for x in s.exclude): return "policy: an item may not repeat an earlier one (duplicate)"
        if s.clause in ("where", "group") and _aggregating(e): return "language: no aggregate in WHERE or GROUP BY"
        if (s.clause in ("where", "group", "having") or s.in_agg or getattr(s, "win_def", 0)) and _has_window(e): return "language: window placement"
        if not s.in_window and _nested(e): return "language: no nested aggregate (an object valid only inside its window)"
        if s.nulltest and any(e is x for x in s.nulltested): return "policy: a null test may not repeat"
        cap = getattr(s, "caps", {}).get("edepth")
        if cap:
            from specbridge.pd.structures.actions import depth_units
            if s.open_depth() + depth_units(e) > cap: return "language: depth cap from R"
        if s.targets is not None and not any(e is t for t in s.targets): return "language: DISTINCT orders by an output"
        if s.targets is None:
            if s.mode == "collapsed" and not s.relaxed and not (any(e is g for g in s.groupkeys) or _aggregating(e) or
                    (all(any(c is g for g in s.groupkeys) for c in _leaf_cols(e)) and not isinstance(e, Col))):
                return "language: determinacy under grouping"
            if (s.mode == "row" or s.relaxed) and _aggregating(e): return "language: determinacy (per-row query)"
        if e is forbid: return "policy: x - x and x / x (duplicate operand)"
        if need is not None and (_bare(e) if need != "bare" else not _bare(e)): return "language: the anchor class after a constant"
        v, basis = self.meaning(s, e)
        if v == "contradicted":
            return "D: grain -- a join repeats its table's rows under this aggregate" if basis == "grain" else "D: its meaning contradicts the operator it enters"
        return None

    def meaning(self, s, e, exact=True):
        """The checker's verdict on object `e` here: EXACT at the decision itself (every operator open above the slot,
        cached by that context), or the cheap necessary condition in lookahead. The object's record is read, not
        rebuilt: it was computed once when the object was built."""
        b = getattr(s, "binder", None)
        if b is None: return "unknown", ""
        sem, frames, rec, rp = b.cat.sem, getattr(s, "frames", []), b.record_of(s, e), b.repeated(s)
        return sem.at_slot(frames, rec, rp) if exact else sem.local(frames, rec, rp)

    def ref_ok(self, s, forbid, need, par=None, exact=True):
        """A reused object is checked like a fresh binding: identity, determinacy, the anchor class, and the one
        checker's verdict in the operators it enters (a REF is not a way around meaning). `forbid` is the left
        operand of - and /, excluded only under the declared duplicates policy."""
        from specbridge.pd.structures.actions import _bare
        from specbridge.pd.realize.verify import ENFORCE
        forbid = forbid if ENFORCE.get("duplicates") else None
        return lambda e: self.ok_target(s, e) and e is not forbid and self.meaning(s, e, exact)[0] != "contradicted" and \
            (need is None or (_bare(e) if need == "bare" else not _bare(e)))

    # ---------------------------------------------------------------- an expression slot
    def expr(self, s, universe, left=None, forbid=None, leftnode=None, par=None, slot=None, d=0, recurse=True):
        """The admissible first actions of an expression slot. Every removal is attributed to the rule that made
        it (`s._why`), and each rule is one of three kinds -- D (the database cannot supply a binding), LANGUAGE
        (a rule of the IR, the canonical form or a declared policy) or FEASIBILITY (what it opens cannot be filled)."""
        from specbridge.pd.structures.actions import COMPOUND, LITS, _TYPES, _bare, slot_roles
        if (par, slot) == ("WINDOW", "agg"): return set(universe)        # the WINDOW contract: legal in every mode
        allow = set(universe)
        why = s.__dict__.get("_why") if recurse and getattr(s, "explain", False) else None
        def drop(items, rule):
            gone = allow & set(items)
            if why is not None:
                for a in gone: why.setdefault(a, rule)
            allow.difference_update(gone)
        def keep(items, rule): drop(allow - set(items), rule)
        cols = {"COL:" + t for t in _TYPES}
        if left == "LIT": drop(LITS, "language: constant expression")
        ok = self.ref_ok(s, forbid, s.need, par, exact=recurse)
        if not any(ok(e) for e in s.ref_targets()):
            if why is not None and getattr(s, "explain", False):    # explanations only when asked for
                rs = collections.Counter(self.ref_reason(s, e, forbid, s.need, par) or "other" for e in s.ref_targets())
                drop({"REF"}, rs.most_common(1)[0][0] if rs else "language: nothing introduced yet to reuse")
            else:
                drop({"REF"}, "reuse: no admissible object")
        if not self.step_steps(s, exact=recurse): drop({"STEP_OUT"}, "language: no step output in scope")
        if s.mode == "collapsed" and not s.relaxed: drop(cols | {"STEP_OUT"}, "language: determinacy under grouping")
        if s.mode == "row" or s.relaxed: drop({"AGG"}, "language: determinacy (per-row query)")
        if s.mode != "free" and not s.relaxed: drop({"SUBQUERY"}, "language: subquery placement")
        if s.clause in ("where", "group"): drop({"AGG", "WINDOW"}, "language: no aggregate or window in WHERE or GROUP BY")
        if s.clause == "having" or s.in_agg or getattr(s, "win_def", 0): drop({"WINDOW"}, "language: window placement")
        if s.targets is not None: keep({"REF"}, "language: DISTINCT orders by an output")
        if not (allow & {"REF", "STEP_OUT", "AGG"} or allow & cols):
            drop(COMPOUND, "language: constant expression (no leaf that reads data)")
            if left is None and s.nest > 0 and (par, slot) != ("LIMIT", "k"): drop(LITS, "language: constant expression (no leaf that reads data)")
        drop(LITS - {"LIT:" + r for r in slot_roles(par or "", slot, leftnode)}, "language: a literal's role is fixed by its slot")
        for role in ("UNIT_PARAM", "FORMULA_PARAM"):
            if "LIT:" + role in allow and par and par.startswith("ARITH:") and slot == "r" and leftnode is not None:
                from specbridge.pd.structures.actions import const_kinds
                if self.const_kind(s, const_kinds(par, slot, role), par, slot, leftnode, role, d) == set():
                    drop({"LIT:" + role}, "D: no kind of parameter can be bound against this operand")
        if par == "ARITH:SUBTRACT" and slot == "l":
            outs = [e for e in s.ref_targets() if self.ok_target(s, e)]
            if not (allow & cols or any(_bare(e) for e in outs) or "STEP_OUT" in allow): drop({"LIT:UNIT_PARAM"}, "feasibility: no stored operand for a unit constant")
        b = getattr(s, "binder", None)
        if b is not None and recurse and getattr(s, "count_exclusions", False):
            b.count_exclusions(s, [ty for ty in _TYPES if "COL:" + ty in universe], [e for e in s.ref_targets() if self.ok_target(s, e)])
        if b is not None:
            for ty in _TYPES:
                if "COL:" + ty in allow and not b.has_column(s, ty, par or "", slot, leftnode, exact=recurse):
                    in_scope = any(b.cat.ann[(t, c.name)].slot == ty for t in s.scope for c in b.cat.cols.get(t, []))
                    drop({"COL:" + ty}, "D: every %s column in scope contradicts the operator or is already used" % ty if in_scope
                         else "D: no %s column in the relations in scope" % ty)
            if "LIT:CLOCK" in allow:
                date_there = (leftnode is not None and b.record_of(s, leftnode).slot == "DATE") or \
                    (leftnode is None and any(b.cat.ann[(t, c.name)].slot == "DATE" for t in s.scope for c in b.cat.cols.get(t, [])))
                if not date_there: drop({"LIT:CLOCK"}, "D: no date for a clock value")
            if s.cmp_left is not None and (par, slot) in (("CMP", "r"), ("BETWEEN", "lo"), ("BETWEEN", "hi"), ("IN", "value"), ("LIKE", "pattern")):
                if "LIT:DATA_VALUE" in allow and not b.has_value(s, s.cmp_left): drop({"LIT:DATA_VALUE"}, "D: no stored text value to compare with")
                if "LIT:DATA_THRESHOLD" in allow and not b.has_threshold(s, s.cmp_left): drop({"LIT:DATA_THRESHOLD"}, "D: no numeric value to compare with")
        if s.need == "bare": keep(cols | {"STEP_OUT", "CAST", "FUNC", "REF"}, "language: a unit constant's operand is a stored column")
        elif s.need == "compound": keep(COMPOUND | {"REF"}, "language: a formula constant's operand is computed")
        cap = s.caps.get("edepth")
        if cap:
            room = cap - s.open_depth()
            if room < 1: drop(COMPOUND, "language: depth cap from R")
            elif room < 2: drop({"CASE", "PREDVAL", "SUBQUERY"}, "language: depth cap from R")
        if recurse:
            kept = self.complete(s, allow, par, slot, d, leftnode)
            drop(allow - kept, "feasibility: what it opens cannot be filled")
        return allow

    def preds(self, s, universe):
        """A predicate at this depth: a comparison opens nothing further; AND, OR and NOT hold a predicate, so
        they need one more level under the depth cap fitted from R."""
        allow = set(universe)
        cap = s.caps.get("edepth")
        if cap and cap - s.open_depth() < 1: allow -= {"AND", "OR", "NOT"}
        return allow

    # ---------------------------------------------------------------- feasibility, recursively
    def _key(self, s, par, slot, d, leftnode):
        from specbridge.pd.structures.actions import _bare
        lk = None if leftnode is None else ("C" if isinstance(leftnode, Const) else "B" if _bare(leftnode) else "X")
        return (par, slot, d, s.need, _near_key(s), getattr(s, "_look", 0), s.nest, s.open_depth(), s.mode, s.clause, s.in_agg, s.in_window,
                getattr(s, "win_def", 0), len(s.intro), tuple(getattr(s, "scope", ())), tuple(sorted(s.read)),
                lk, s.nulltest, len(s.exclude), s.item_nest == s.nest,
                s.targets is not None, id(getattr(s, "cmp_left", None)))

    def fillable(self, s, par, slot, d, leftnode=None, left=None):
        """Can this expression slot be filled, in the current state? The full admissibility of its first
        decision, which itself asks this question of what it would open."""
        cache = s.__dict__.setdefault("_fill_cache", {})
        key = self._key(s, par, slot, d, leftnode) + (left,)
        if key in cache: return cache[key]
        cache[key] = False                                    # a cycle would be infeasible, never assumed fine
        u = s.universe_expr(par, slot, d)
        forbid = leftnode if par.split(":")[-1] in ("SUBTRACT", "DIVIDE") and slot == "r" else None
        local = self.expr(s, u, left, forbid, leftnode, par, slot, d, recurse=False)
        from specbridge.pd.structures.actions import LEAVES
        leaves = local & LEAVES
        if par.startswith("ARITH:") and slot == "l" and not any(not a.startswith("LIT:") for a in leaves):
            # only constants fit: each is credited only if its right operand can follow, the same test the
            # left-operand decision applies. (Any other leaf fills the slot, and then none needs testing.)
            leaves = {a for a in leaves if self.right_after_constant(s, par, d, a[4:])}
        # a leaf fills the slot outright; only when none fits is a compound's own fillability asked
        comp = local - LEAVES
        if not leaves and BOUNDED_WRAPPERS:
            # a slot with no leaf: a wrapper (CAST, a function) opens the SAME slot one level deeper -- the same mode,
            # clause, scope and operand requirement (`_enter` keeps `need`) -- so beyond the lookahead it would be
            # assumed fillable, and a draw could wrap forever: round(CAST(round(CAST(...)))), or a unit constant
            # admitted before a right operand no stored column can fill. A wrapper is credited only when its own
            # operand takes a leaf: one level more, leaves only, never a completion search. Other compounds as before.
            comp = {a for a in comp if a not in WRAPPERS or self.leaf_under(s, a, d)}
        v = bool(leaves) or bool(self.complete(s, comp, par, slot, d, leftnode))
        cache[key] = v
        return v

    def leaf_under(self, s, a, d):
        """Does wrapper `a`'s operand, opened here, take a leaf? The local admissibility of its first slot only."""
        from specbridge.pd.structures.actions import LEAVES
        saved = self._enter(s, a, None, None)
        s.frames.append(("CAST", None) if a == "CAST" else ("FUNC", None, 0) if a == "FUNC" else ("STOP",))
        try:
            cpar = {"CAST": "CAST", "FUNC": "FUNC:round", "STRFTIME": "STRFTIME"}[a]
            slot = "expr" if a != "FUNC" else "arg"
            return bool(self.expr(s, s.universe_expr(cpar, slot, d), None, None, None, cpar, slot, d, recurse=False) & LEAVES)
        finally: self._leave(s, saved); s.frames.pop()

    def _enter(self, s, a, par, leftnode):
        """The state change the decoder makes on opening compound `a` (LANGUAGE.md §4), for simulation."""
        saved = (s.nest, s.need)
        s.nest += 1
        if a not in ("CAST", "FUNC"): s.need = None
        return saved

    def _leave(self, s, saved):
        s.nest, s.need = saved

    def complete(self, s, allow, par, slot, d, leftnode):
        """Which compounds can be opened here: each is asked whether ITS FIRST SLOT can be filled -- one level, not a
        recursive completion search (LOOK). Beyond that, what a compound opens is assumed fillable and judged when it
        is drawn; a draw may then dead-end, which is the accepted cost of not searching."""
        out = set(allow)
        if getattr(s, "_look", 0) >= LOOK: return out
        s._look = getattr(s, "_look", 0) + 1
        try:
            return self._complete(s, out, par, slot, d, leftnode)
        finally: s._look -= 1

    def _complete(self, s, out, par, slot, d, leftnode):
        for a in list(out):
            ok = True
            if a == "ARITH":
                saved = self._enter(s, a, par, leftnode)
                try: ok = bool(self.arith_ops(s, d))
                finally: self._leave(s, saved)
            elif a in ("CAST", "FUNC", "STRFTIME"):
                saved = self._enter(s, a, par, leftnode)
                s.frames.append(("CAST", None) if a == "CAST" else ("FUNC", None, 0) if a == "FUNC" else ("STOP",))   # its type or name is not drawn yet
                try:
                    cpar = {"CAST": "CAST", "FUNC": "FUNC:round", "STRFTIME": "STRFTIME"}[a]
                    ok = self.fillable(s, cpar, "expr" if a != "FUNC" else "arg", d)
                finally: self._leave(s, saved); s.frames.pop()
            elif a == "CASE":
                saved = self._enter(s, a, par, leftnode)
                try: ok = self.fillable(s, "CASE", "then", d)
                finally: self._leave(s, saved)
            elif a.startswith("LIT:") and par and par.startswith("ARITH:") and slot == "l":
                ok = self.right_after_constant(s, par, d, a[4:])
            if not ok: out.discard(a)
        return out

    def arith_ops(self, s, d):
        """The operators whose left operand can be filled. Called at the operator decision and, through
        `complete`, by the parent deciding whether to open arithmetic: the same function, the same state."""
        from specbridge.pd.structures.actions import _CLOSED, _SYM
        saved = s.need; s.need = None
        out = set()
        try:
            for op in _CLOSED[("ARITH", "op")]:
                s.frames.append(("ARITH", _SYM[op], "l", None))       # the frame the decoder will open
                try:
                    if self.fillable(s, "ARITH:" + op, "l", d + 1): out.add(op)
                finally: s.frames.pop()
            return out
        finally:
            s.need = saved

    def right_after_constant(self, s, par, d, role):
        """A constant on the left is feasible only if the right slot can then take what its role requires."""
        need = {"UNIT_PARAM": "bare", "FORMULA_PARAM": "compound"}.get(role) if par == "ARITH:SUBTRACT" else None
        saved = s.need; s.need = need
        fr = s.frames[-1] if getattr(s, "frames", None) and s.frames[-1][0] == "ARITH" else None
        if fr: s.frames[-1] = (fr[0], fr[1], "r", s.binder.cat.sem.const("WHOLE") if getattr(s, "binder", None) else None)
        try: return self.fillable(s, par, "r", d, Const(1), "LIT")
        finally:
            s.need = saved
            if fr: s.frames[-1] = fr

    # ---------------------------------------------------------------- references
    def ref_kinds(self, s, universe, forbid):
        ok = self.ref_ok(s, forbid, s.need)
        outs, keys, others = s.ref_lists()
        return {k for k, xs in (("OUT", outs), ("KEY", keys), ("ANY", others)) if k in universe and any(ok(e) for e in xs)}

    def ref_members(self, s, kind, forbid):
        ok = self.ref_ok(s, forbid, s.need)
        outs, keys, others = s.ref_lists()
        if kind == "OUT": return {len(s.outputs) - k for k, o in enumerate(s.outputs) if any(o is x for x in outs) and ok(o)}
        if kind == "KEY": return {k for k, o in enumerate(s.groupkeys) if any(o is x for x in keys) and ok(o)}
        return {len(others) - k for k, o in enumerate(others) if ok(o)}

    # ---------------------------------------------------------------- step outputs
    def step_outs(self, s, st, exact=True):
        """Outputs of step `st` not yet introduced in this scope: an output introduced is reused by REF."""
        q = s.steps[st][1]
        if not isinstance(q, Program): return set()
        taken = {int(c.name[1:]) for c in s.intro if isinstance(c, Col) and c.alias == s.steps[st][0] and c.name[:1] == "o"}
        left = set(range(len(q.select))) - taken
        # the same type contract as a fresh column or a REF: an output entering an operator must suit it
        nm = s.steps[st][0]
        return {i for i in left if self.meaning(s, self._step_col(s, nm, i), exact)[0] != "contradicted"}   # the one checker

    def step_steps(self, s, exact=True):
        """Steps read in this scope's FROM with an output left."""
        return {st for st in s.read if st < len(s.steps) and self.step_outs(s, st, exact)}

    @staticmethod
    def _step_col(s, nm, i):
        """One Col object per step output per draw, so its record is computed once and read after."""
        cache = s.__dict__.setdefault("_step_cols", {})
        if (nm, i) not in cache: cache[(nm, i)] = Col(nm, "o%d" % i, nm, "ANY")
        return cache[(nm, i)]

    # ---------------------------------------------------------------- lists, relations, the limit
    def list(self, s, universe, i, lo, more_only=None, can=None):
        """STOP while an obligation is outstanding is infeasible; MORE when no item can start is infeasible."""
        allow = set(universe)
        why = s.__dict__.get("_why") if getattr(s, "explain", False) else None
        if i < lo or (more_only and more_only()):
            allow.discard(STOP)
            if why is not None and STOP in universe:
                why.setdefault(STOP, "language: a step that summarises nothing must end in a cut (§1, §2)" if self.must_cut(s) and i < lo
                               else "feasibility: the list owes more items")
        if can is not None and MORE in allow and not can():
            allow.discard(MORE)
            if why is not None: why.setdefault(MORE, "feasibility: no item can start here")
        return allow

    def unread(self, s):
        return [k for k, (n, _q) in enumerate(s.steps) if n in s.mine and n not in s.consumed]

    def relation(self, s, universe, par, room):
        """The next relation of a FROM clause: a table or a step, whichever D can link now, with the step
        obligation kept feasible. A step is ruled out only by PROOF: even the shortest path to it through D's
        links (in joins) plus one join for each other unread step exceeds the room left. No ordering is imposed."""
        unread = self.unread(s)
        allow = set(universe)
        members = set(range(len(s.steps))) - set(s.read)                 # a relation once per FROM
        if room <= len(unread): allow &= {"STEP_REL"}                     # only steps fit in the room left
        b = getattr(s, "binder", None)
        if b is None:
            if unread and room <= len(unread): members &= set(unread)
            return allow, members
        if par == "JOIN":
            if not [u for u, _l in b.links(s) if b.feasible_after(s, [u], None, unread, room - 1)]: allow.discard("RELATION")
            members = {k for k in b.linkable_steps(s, members)
                       if b.feasible_after(s, [], k, [x for x in unread if x != k], room - 1)}
        else:
            if not [t for t in b.tables() if b.feasible_after(s, [t], None, unread, room - 1)]: allow.discard("RELATION")
            members = {k for k in members if b.feasible_after(s, [], k, [x for x in unread if x != k], room - 1)}
        if not members: allow.discard("STEP_REL")
        return allow, members

    def must_cut(self, s):
        """THE STEP OBLIGATION (canonical form, LANGUAGE.md §2): a step that groups nothing, aggregates nothing,
        windows nothing, keeps distinct rows of nothing and has no HAVING only names expressions and is not a
        step. After its SELECT, the only discharge left is a cut -- an ordering and a LIMIT -- so both are
        owed. Checked when the order list may stop and at the LIMIT decision."""
        from specbridge.pd.structures.algebra import Window
        if getattr(s, "role", "ROOT") != "STEP": return False
        if s.groupkeys or s.distinct or getattr(s, "has_having", False) or s.mine: return False
        return not any(_aggregating(e) or _find(e, Window) for e in s.outputs)

    def limit(self, s, universe, ordered):
        why = s.__dict__.get("_why") if getattr(s, "explain", False) else None
        if not ordered:
            if why is not None and "LIMIT" in universe: why.setdefault("LIMIT", "policy: LIMIT without ORDER (the subset would be arbitrary, §1)")
            return {"NONE"}
        if self.must_cut(s):
            if why is not None:
                for a in set(universe) - {"LIMIT"}: why.setdefault(a, "language: a step that summarises nothing must end in a cut (§1, §2)")
            return {"LIMIT"} & universe
        return set(universe)

    def const_kind(self, s, universe, par, slot, operand, role=None, d=0):
        """The kinds of a parameter whose binding rule can succeed here (actions.const_kinds). A CASE result never
        takes a source's text on a target (LABEL). On the right of an arithmetic node the operand is known: CONVERT
        needs a declared conversion for its unit, REFERENCE a typical value from its rows. These are rules of
        BINDING (can the value be chosen), not of meaning: whether 1 - x is a supported complement is the
        checker's verdict once x is known."""
        b = getattr(s, "binder", None)
        if b is None: return None
        out = set(universe)
        if role == "SCORE": out.discard("LABEL"); return out
        if operand is None or slot != "r": return out
        from specbridge.pd.realize.catalogue import conversions
        op = {"ADD": "+", "SUBTRACT": "-", "MULTIPLY": "*", "DIVIDE": "/", "MOD": "%"}.get(par.split(":")[-1], "")
        a = b.record_of(s, operand)
        if "CONVERT" in out and not conversions(op, a): out.discard("CONVERT")
        if "REFERENCE" in out and b.reference(s, operand) is None: out.discard("REFERENCE")
        return out

    def parameter(self, s, role):
        """GROUNDED: a constant P carries is a number. Text belongs to the target's data (DATA_VALUE), so a text
        parameter from the source -- a CASE label, a function's string argument -- is not offered on a target."""
        if getattr(s, "binder", None) is None: return None
        return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)

    def func_name(self, s, par=""):
        """Language: a unit constant's operand is a stored column, so only a function that keeps its argument.
        Meaning: a function whose result the checker can judge as soon as it is named (a text or date function, a
        clock) is judged at the slot like any candidate: its record with an argument not yet known."""
        from specbridge.pd.structures.actions import _PASS
        if s.need == "bare": return set(_PASS)
        return self._by_result(s, lambda sem, n: sem.func(n, [sem.NONE])[0])

    def cast_type(self, s):
        """A cast whose type fixes its result (TEXT, DATE) is judged at the slot like any candidate."""
        return self._by_result(s, lambda sem, t: sem.cast(t, sem.NONE)[0])

    @staticmethod
    def _by_result(s, result):
        """Admit a name or type unless the record it yields, whatever its argument, contradicts the operators at the
        slot (`Semantics.at_slot`). None when there is no catalogue."""
        b = getattr(s, "binder", None)
        if b is None: return None
        sem, frames, rep = b.cat.sem, list(getattr(s, "frames", [])), b.repeated(s)
        return lambda n: sem.at_slot(frames, result(sem, n), rep)[0] != "contradicted"
