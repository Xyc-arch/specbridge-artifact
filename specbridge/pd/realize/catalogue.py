"""specbridge.pd.realize.catalogue — A TARGET DATABASE AS THE DECODER SEES IT, and the BINDER that fills P's slots from it.

A database is read through `specbridge.pd.realize.semantic.Source` (its rows as `specbridge.pd.realize.world` reads them, its documentation) and its
meaning ONLY from the saved catalogue, `catalogues/<db>.json`: one record per column (`Ann`: type, unit, kind,
scale, population, grain, the quantity it measures, and each property's provenance -- rows, doc, rule or model)
and the relationships between columns (comparable, part_of, rate, with their provenance). Nothing here interprets
meaning: records are combined, and candidates judged, by the one checker, `specbridge.pd.realize.semantics` (`Catalogue.sem`).

THE BINDER chooses among the candidates the checker admits at a slot, preferring those it calls supported
(strongly, then plausibly) over unknown ones, uniformly within a tier, and records every binding. Literal values
come from cached column statistics; parameters by their kind's declared rule (`Binder.constant`).
"""
from __future__ import annotations
import math
import collections, json, os, random, re, sqlite3
from dataclasses import dataclass, field

from specbridge.pd.structures.algebra import Agg, Arith, Case, Cast, Col, Const, Func, Program, Window, emit_expr, qname, Cmp
from specbridge.pd.realize.semantic import Source, load


def filter_probe(head, from_sql, where, cond):
    """The probe query of `filter_triviality`: SELECT 1 over the partial query's FROM, its WHERE conjuncts and `cond`.
    Built by concatenation, never by %-formatting: table and column names may contain '%' (e.g. "Percent (%) Eligible")."""
    return head + "SELECT 1 " + from_sql + " WHERE " + " AND ".join(["(%s)" % x for x in where] + [cond])


@dataclass
class Ann:
    """What is known about an expression's meaning, and where each fact came from."""
    slot: str = "ANY"          # NUM TEXT DATE KEY ANY
    amount: object = None      # a true zero (sums, ratios, scalings mean something): True | False | None = unknown
    scale: str = ""            # "ratio" | "interval" | "" unknown -- from profile evidence, never from observed values
    unit: str = ""
    kind: str = ""
    population: str = ""
    key: str = ""              # "table.col" when it is a single column
    grain: str = ""            # the entity each value belongs to: a table; "group" after an aggregate; "step:<name>"; "" unknown
    quantity: tuple = ()       # (column "table.col", FORM): the stored quantity this measures and how it is summarised --
                               # "value" (the column itself, rounded, cast, or passed through a step), or SUM/AVG/MIN/MAX of it
    ev: dict = field(default_factory=dict)   # property -> where it came from: "rows" | "doc" | "model" | "rule"
    value: object = None       # a constant's value
    # ---- the semantic profile (docs/LANGUAGE.md section 3a); every field may be unknown
    role: str = ""             # identifier category ordinal measure count date duration indicator; "" unknown
    meaning: str = ""          # the profile's QUANTITY: what is measured or named ("K-12 enrollment") -- not its dimension
    dim: object = None         # the dimension: a sorted tuple of (base, exponent), () dimensionless; None unknown
    factor: object = None      # the unit's factor to its base dimensions; None unknown
    order: object = None       # an ordinal's values in order, or "numeric"; None when not declared
    additive: object = None    # {"entities": bool|None, "time": bool|None}: is a SUM meaningful along that axis
    period: str = ""


class Catalogue(Source):
    """A database for generation: its rows (World), and its meaning read ONLY from the saved catalogue
    (catalogues/<db>.json, built by `python -m specbridge.pd.realize.semantic`). Meaning is combined by the one checker (`sem`)."""
    def __init__(self, db, con=None):
        super().__init__(db, con)
        c = load(self)
        self.catalogue_version = c["version"]
        cols = c["columns"]
        self.cols, self.ann = {}, {}                     # table -> columns; (table, col) -> the column's record
        for t, r in self.world.rel.items():
            self.cols[t] = []
            for col in r.cols.values():
                key = "%s.%s" % (t, col.name)
                v = cols[key]; ev = v.get("evidence", {})
                scale = v["scale"] if v["scale"] in ("ratio", "interval", "nominal", "ordinal") else ""
                from specbridge.pd.realize.semantic import parse_unit
                du = parse_unit(v.get("unit")) if v.get("unit") else None
                self.ann[(t, col.name)] = Ann(
                    slot=v["type"], amount={"ratio": True, "interval": False}.get(scale), scale=scale, unit=v["unit"],
                    kind=v["kind"], population=v["population"], key=key, quantity=(key, "value"), grain=t,
                    role=v.get("semantic_role", "") if v.get("semantic_role") not in (None, "unknown", "other") else "",
                    meaning=v.get("quantity", ""), dim=du[0] if du else None, factor=du[1] if du else None,
                    order=v.get("order"), additive=v.get("additive"), period=v.get("period", ""),
                    ev={"slot": "rows", "grain": "rows", "unit": ev.get("unit", ""), "kind": ev.get("kind", ""),
                        "scale": ev.get("scale", ""), "amount": ev.get("scale", ""), "population": ev.get("population", ""),
                        "role": ev.get("semantic_role", ""), "dim": ev.get("unit", ""), "additive": ev.get("additive", "")})
                self.cols[t].append(col)
        # the aggregation axes each table's rows vary over ("entities"; "time" when one entity has rows over time)
        self.axes = {t: tuple(c["tables"].get(t, {}).get("axes") or ["entities"]) for t in self.world.rel}
        self.rel, self.rel_result = {}, {}               # (a, b, kind) -> evidence; -> what it yields (a unit)
        for r in c.get("relations", []):
            k = (r["a"], r["b"], r["kind"])
            self.rel[k] = _strongest(self.rel.get(k, ""), r.get("evidence", "model"))
            if r.get("result"): self.rel_result[k] = r["result"]
        self._values, self._dist = {}, {}
        # THE LINKS GENERATION MAY FOLLOW: the schema's and the rows', minus those the join contract contradicts
        self.links = [f for f in self.world.fks if self.sem.join(f[0], f[1], f[2], f[3])[0] != "contradicted"]

    # ---------------------------------------------------------------- names, for the English
    def name(self, t, c):
        m = self.meta.get((t, c)) or {}
        d = (m.get("desc") or "").strip() if isinstance(m, dict) else ""
        if d and len(d.split()) <= 6 and not re.search(r"[.;:]", d): return d
        return re.sub(r"([a-z])([A-Z])", r"\1 \2", c).replace("_", " ")

    # ---------------------------------------------------------------- values
    def values(self, t, c, k=200):
        """Distinct stored values of a column, most frequent first."""
        if (t, c) not in self._values:
            import time
            t0 = time.time()                                  # bounded like every catalogue query: 1 s, then none
            self.con.set_progress_handler(lambda: 1 if time.time() - t0 > 1.0 else 0, 10000)
            try:
                rows = self.con.execute('SELECT %s, COUNT(*) n FROM %s WHERE %s IS NOT NULL GROUP BY 1 ORDER BY n DESC LIMIT %d'
                                        % (qname(c), qname(t), qname(c), k)).fetchall()
            except Exception: rows = []
            finally: self.con.set_progress_handler(None, 0)
            self._values[(t, c)] = [r[0] for r in rows]
        return self._values[(t, c)]

    def quantiles(self, t, c):
        """The 10th..90th percentiles of a column's stored values, computed once and cached: metadata."""
        key = ("q", t, c)
        if key not in self._values:
            vals = self.distribution('SELECT %s FROM %s WHERE %s IS NOT NULL' % (qname(c), qname(t), qname(c)), 20000)
            vals = [v for v in vals if isinstance(v, (int, float))] or [v for v in vals if isinstance(v, str)]
            self._values[key] = [vals[min(len(vals) - 1, int(len(vals) * q))] for q in (.1, .25, .5, .75, .9)] if vals else []
        return self._values[key]

    def extent(self, t, c):
        """The smallest and largest stored value of a column (numbers, else text), from the same cached distribution
        as `quantiles`; None when it has none."""
        vals = self.distribution('SELECT %s FROM %s WHERE %s IS NOT NULL' % (qname(c), qname(t), qname(c)), 20000)
        vals = [v for v in vals if isinstance(v, (int, float))] or [v for v in vals if isinstance(v, str)]
        return (vals[0], vals[-1]) if vals else None

    def distribution(self, sql, k=4000):
        """The values an expression takes over a FROM clause, sorted: what a threshold is drawn from."""
        if sql not in self._dist:
            import time
            t0 = time.time()                                  # a probe is bounded like any query: 1 s, then no values
            self.con.set_progress_handler(lambda: 1 if time.time() - t0 > 1.0 else 0, 10000)
            status = "ok"
            try: rows = self.con.execute(sql + " LIMIT %d" % k).fetchall()
            except Exception as e:
                rows = []; status = "timeout" if time.time() - t0 > 1.0 or "interrupt" in str(e).lower() else "error"
            finally: self.con.set_progress_handler(None, 0)
            if status == "ok" and not rows: status = "empty"
            self.__dict__.setdefault("_dist_status", {})[sql] = status
            vals = sorted((r[0] for r in rows if r[0] is not None and not isinstance(r[0], bytes)),
                          key=lambda v: (isinstance(v, str), v))
            self._dist[sql] = vals
        return self._dist[sql]

    # ---------------------------------------------------------------- annotation propagation
    # ---------------------------------------------------------------- the semantic record, one rule per constructor
    # ---------------------------------------------------------------- meaning: the one checker (specbridge.pd.realize.semantics)
    @property
    def sem(self):
        if "_sem" not in self.__dict__:
            from specbridge.pd.realize.semantics import Semantics
            self._sem = Semantics(self)
        return self._sem


# THE DECLARED CONVERSION TABLE: (unit of the operand, operator, factor, unit of the result). A CONVERT parameter
# is bound only from here, so its value is explained by the operand's unit and nothing else.
CONVERSIONS = [("percent", "/", 100, "fraction"), ("fraction", "*", 100, "percent"),
               ("months", "/", 12, "years"), ("days", "/", 7, "weeks"), ("days", "/", 30, "months"), ("days", "/", 365, "years"),
               ("hours", "/", 24, "days"), ("hours", "*", 60, "minutes"), ("minutes", "/", 60, "hours"), ("seconds", "/", 60, "minutes"),
               ("cm", "/", 100, "m"), ("m", "*", 100, "cm"), ("m", "/", 1000, "km"), ("g", "/", 1000, "kg"), ("kg", "*", 1000, "g"),
               ("usd", "/", 1000, "thousand USD"), ("students", "/", 1000, "thousand students"),
               ("rate", "*", 100, "per hundred"), ("rate", "*", 1000, "per thousand")]
_UNIT_KIND = {"fraction": "share", "percent": "percent"}


def _unit_word(a):
    """The unit a conversion is looked up by: the record's unit, normalised; a share is a fraction; a quotient of two
    units is a rate."""
    u = (a.unit or "").strip().lower()
    if u in ("%", "percentage") or a.kind == "percent": return "percent"
    if (a.kind == "share" and u in ("", "fraction", "ratio")) or a.kind == "indicator": return "fraction"
    if " per " in u or a.kind == "rate": return "rate"
    return u


def conversions(op, a):
    """The (factor, resulting unit) pairs the declared table offers for an operand record under * or /."""
    w = _unit_word(a)
    return [(float(f), nu) for u, o, f, nu in CONVERSIONS if o == op and u == w] if w else []


WEIGHTS = (0.1, 0.2, 0.25, 0.5, 0.75, 1.5, 2, 3, 5, 10)
SCORES = (2, 3, 4, 5, 10)                                     # a CASE score the question states      # a WEIGHT is stated by the question; these are its plain values
MODULI = (2, 3, 5, 7, 10)


def _operator(chain):
    """The operators a candidate was judged by, outermost first: 'ARITH -', 'AGG SUM', 'FUNC round', 'CAST TEXT'."""
    return " > ".join("%s %s" % (f[0], f[1]) for f in chain if f[0] in ("ARITH", "AGG", "FUNC", "CAST") and f[1]) or "none"


def _unwrap(e):
    """The expression under casts and unit-preserving functions: what `bare` means for an operand."""
    while True:
        if isinstance(e, Cast): e = e.expr
        elif isinstance(e, Func) and e.args and e.name.lower() in ("round", "abs", "coalesce", "ifnull", "nullif", "ceil", "floor"): e = e.args[0]
        else: return e


def _placeholder_value(kind):
    return {"ZERO": 0, "WHOLE": 1, "CONVERT": 100, "WEIGHT": 2}.get(kind, 1)


def _num(v):
    """A carried number, bucketed so the report groups them: 0.5, 2, 10, 100, 1000 stay; others are 'other'."""
    try: f = float(v)
    except Exception: return "?"
    return ("%g" % f) if f in (0.5, 2, 10, 12, 100, 1000, 365, 60, 24, 7, 30) else "other"


def _strongest(*srcs):
    """Of several independent sources for one fact, the best."""
    order = {"rows": 0, "rule": 0, "doc": 1, "model": 2}
    known = [s for s in srcs if s]
    return min(known, key=lambda s: order.get(s, 3)) if known else ""


def _all3(vals):
    """Three-valued AND: False if any is known False, None (unknown) if any is unknown, else True."""
    vals = list(vals)
    if any(v is False for v in vals): return False
    if any(v is None for v in vals): return None
    return True


def _weakest(*srcs):
    """The evidence a conclusion from several facts rests on is the weakest of them."""
    order = {"rows": 0, "rule": 0, "doc": 1, "model": 2}
    known = [s for s in srcs if s]
    return max(known, key=lambda s: order.get(s, 3)) if known else ""


from specbridge.pd.structures.algebra import Unsupported


class Binder:
    """Fills P's slots from a catalogue, during decoding. Each method answers for the CURRENT state only; a
    later dead end is the verifier's to count. Records the evidence tier of every choice."""

    def __init__(self, cat, rng, probes=True):
        """`probes` (on by default): read thresholds and values off the partial query's rows during decoding -- its
        FROM, joins, steps and the conditions bound so far -- so that a bound value keeps a row. Measured on 900
        attempts (out/funnel/PROBE.md): empty answers 129 -> 79 and complex tasks 55 -> 76 at the same cost per complex
        task. `probes=False` (`--no-probes`) reads cached column statistics only."""
        self.cat, self.rng, self.probes = cat, rng, probes
        self.evidence = collections.Counter()
        self.log = []                                         # (what, bound to, why) for every binding
        self.trivial = []                                     # TRIVIALITY found while binding (reported, never refused here)
        self.kinds = {}                                       # id(Const) -> (role, kind, the Const): every parameter's kind
        self._rep, self._recs = {}, {}                        # multiplicity per join list; records of built expressions
        self.grounded = {}                                    # id(Const) -> Const: REFERENCE values read from rows
        self.grain_hits = 0                                   # column candidates excluded by the grain rule
        self.excluded = collections.Counter()                 # (operator at the slot, basis) -> candidates a contract excluded
        self._partner = cat.__dict__.setdefault("_partner_cache", {})

    # ---- relations
    def tables(self):
        return [t for t, r in self.cat.world.rel.items() if r.n > 0]

    def bases(self, s, unread=()):
        """Tables a FROM may start at: every unread step of the query must link to it (feasibility of the step
        obligation), so a base the steps cannot reach is never chosen."""
        out = []
        for t in self.tables():
            ok = True
            for k in unread:
                q = s.steps[k][1]
                if not isinstance(q, Program): ok = False; break
                outs = self._stored_outputs(q, s)
                if not any(tb == t or any({(c, cc), (p, pc)} == {(tb, cn), (p if c == tb else c, pc if c == tb else cc)}
                                          and t in (c, p) for c, cc, p, pc in self.cat.links) for tb, cn in outs):
                    ok = False; break
            if ok: out.append(t)
        return out

    def _stored_outputs(self, q, s=None):
        """The stored columns a step's outputs carry, followed through CAST, unit-preserving functions and
        earlier steps' outputs (the same resolution values use)."""
        if not isinstance(q, Program): return []
        out = []
        for x, _a in q.select:
            sc = self._stored(s, x) if s is not None else ((x.table, x.name) if isinstance(x, Col) and x.table in self.cat.world.rel else None)
            if sc: out.append(sc)
        return out

    def _linked(self, a, b):
        """Two stored columns join: the same column, or a declared or discovered key between them."""
        return a == b or any({(c, cc), (p, pc)} == {a, b} for c, cc, p, pc in self.cat.links)

    def step_bases(self, s, unread):
        """Steps a FROM may start at: every OTHER unread step links to one of its stored outputs."""
        out = set()
        for k in unread:
            mine = self._stored_outputs(s.steps[k][1], s)
            if all(any(self._linked(a, b) for a in mine for b in self._stored_outputs(s.steps[j][1], s)) for j in unread if j != k):
                out.add(k)
        return out

    # ---- reachability: the step obligation as a count of joins through D's links
    def _dist(self):
        if "_hops" not in self.cat.__dict__:
            tabs = list(self.cat.world.rel); adj = {t: set() for t in tabs}
            for c, _cc, p, _pc in self.cat.links: adj[c].add(p); adj[p].add(c)
            dist = {}
            for t in tabs:
                d, frontier = {t: 0}, [t]
                while frontier:
                    nxt = []
                    for x in frontier:
                        for y in adj[x]:
                            if y not in d: d[y] = d[x] + 1; nxt.append(y)
                    frontier = nxt
                dist[t] = d
            self.cat._hops = dist                       # join distances; `_dist` is the catalogue's query cache
        return self.cat._hops

    def feasible_after(self, s, tables, step, unread, room):
        """Can every unread step still be linked after adding `tables` (or reading `step`) with `room` joins left?
        A LOWER BOUND on the joins needed, so a False is a proof. Reachability as joins actually work: a TABLE in
        scope offers all its columns; a STEP read in FROM offers only its OUTPUT columns, and reaches a table only
        through a key on one of them; another step links through a column both carry or a key between them."""
        if not unread: return room >= 0
        dist, fks = self._dist(), self.cat.links
        partners = lambda col: {p if (c, cc) == col else c for c, cc, p, pc in fks if col in ((c, cc), (p, pc))}
        linked_cols = lambda col: {col} | {(p, pc) if (c, cc) == col else (c, cc) for c, cc, p, pc in fks if col in ((c, cc), (p, pc))}
        scope = set(s.scope) | set(tables)
        step_cols = {sc for k in sorted(s.read) for sc in self._stored_outputs(s.steps[k][1], s)}
        if step is not None: step_cols |= set(self._stored_outputs(s.steps[step][1], s))
        # where joins can start: every table in scope (0 joins), every table a step's key column reaches (1 join)
        start = {t: 0 for t in scope}
        for col in step_cols:
            for p in partners(col): start[p] = min(start.get(p, 99), 1)
        worst = 0
        for k in unread:
            outs = self._stored_outputs(s.steps[k][1], s)
            if not outs: return False                      # nothing to link by: only a FROM could read it
            if any(linked_cols(o) & step_cols for o in outs): continue              # links to a step already read
            need = 99
            for o in outs:
                anchors = {o[0]} | partners(o)             # a table in scope holding this column, or a key to it
                for u in anchors:
                    for h, base_cost in start.items():
                        d = dist.get(h, {}).get(u)
                        if d is not None: need = min(need, base_cost + d)
            if need >= 99: return False                    # unreachable from anything the query can hold
            worst = max(worst, need)
        return len(unread) + worst <= room

    def base(self, s):
        unread = [k for k, (n, _q) in enumerate(s.steps) if n in s.mine and n not in s.consumed]
        cap = s.caps.get(("QUERY", "joins"), s.caps.get("list", 99))
        ok = [t for t in self.tables() if self.feasible_after(s, [t], None, unread, cap)]
        return self.rng.choice(ok or self.tables())

    def _keys(self, s):
        """(alias, column, underlying table, underlying column) for everything in this query's FROM: the real
        tables' columns, and each read step's outputs that are a stored column."""
        out = [(t, c.name, t, c.name) for t in s.scope for c in self.cat.cols.get(t, [])]
        for k in sorted(s.read):
            nm, q = s.steps[k]
            if isinstance(q, Program):
                for i, (x, _a) in enumerate(q.select):
                    sc = self._stored(s, x)
                    if sc: out.append((nm, "o%d" % i, sc[0], sc[1]))
        return out

    def feasible_links(self, s, room):
        unread = [k for k, (n, _q) in enumerate(s.steps) if n in s.mine and n not in s.consumed]
        return [(u, l) for u, l in self.links(s) if self.feasible_after(s, [u], None, unread, room - 1)]

    def links(self, s):
        """(table to join, ON pair) for every table a key in this query's FROM links to, not in scope yet."""
        out = []
        for alias, col, ot, oc in self._keys(s):
            for c, cc, p, pc in self.cat.links:
                if (c, cc) == (ot, oc) and p not in s.scope: out.append((p, (alias, col, p, pc)))
                if (p, pc) == (ot, oc) and c not in s.scope: out.append((c, (alias, col, c, cc)))
        seen, uniq = set(), []
        for u, l in out:
            if u not in seen: seen.add(u); uniq.append((u, l))
        return uniq

    def linkable_steps(self, s, candidates):
        return {k for k in candidates if self.step_on(s, k) is not None}

    def step_on(self, s, k):
        """The ON condition joining step k to this query's FROM: one of its outputs is a stored column that a
        relation in scope holds or links to. None when there is none (the join is then a CROSS join)."""
        nm, q = s.steps[k]
        if not isinstance(q, Program): return None
        from specbridge.pd.structures.algebra import Cmp
        for i, (x, _a) in enumerate(q.select):
            sc = self._stored(s, x)
            if not sc: continue
            for alias, col, ot, oc in self._keys(s):
                if alias == nm: continue
                same = (ot, oc) == sc
                linked = any({(c, cc), (p, pc)} == {(ot, oc), sc} for c, cc, p, pc in self.cat.links)
                if same or linked: return Cmp("=", Col(nm, "o%d" % i, nm, "ANY"), Col(alias, col, alias, "KEY"))
        return None

    # ---- grain
    def repeated(self, s):
        """The tables whose rows this query's joins repeat: the checker's own rule, recomputed only when the joins
        change (an incremental fact of the query, not of the leaf)."""
        joined = getattr(s, "joined", [])
        key = tuple(id(j) for j in joined)
        hit = self._rep.get(key)
        if hit is not None and all(x is y for x, y in zip(hit[0], joined)): return hit[1]
        rep = self.cat.sem.repeated(joined)
        self._rep[key] = (list(joined), rep)
        return rep

    def record_of(self, s, e):
        """The record of an expression already built in this draw: computed once, then read (a REF reads it)."""
        hit = self._recs.get(id(e))
        if hit is not None and hit[0] is e: return hit[1]
        r = self.cat.sem.record(e, dict(s.steps))
        self._recs[id(e)] = (e, r)
        return r

    def by_slot(self, t, slot):
        """The columns of table `t` with computational type `slot`, indexed once per catalogue."""
        idx = self.cat.__dict__.setdefault("_by_slot", {})
        if (t, slot) not in idx:
            idx[(t, slot)] = [(c, self.cat.ann[(t, c.name)]) for c in self.cat.cols.get(t, []) if self.cat.ann[(t, c.name)].slot == slot]
        return idx[(t, slot)]

    # ---- columns
    def _candidates(self, s, slot, exact):
        """(table, column, record, verdict) for every column of `slot` in scope not yet introduced. EXACT (at the
        decision itself): the checker's verdict in all the operators open above the slot, cached by that full
        context. Otherwise (lookahead): the checker's cheap necessary condition from the nearest operator only."""
        sem = self.cat.sem
        frames = getattr(s, "frames", [])
        rep = self.repeated(s)
        taken = {(c.table, c.name) for c in s.intro if isinstance(c, Col)}
        for t in s.scope:
            for c, a in self.by_slot(t, slot):
                if (t, c.name) in taken: continue
                v = sem.at_slot(frames, a, rep) if exact else sem.local(frames, a, rep)
                yield t, c, a, v

    def columns(self, s, slot, par, side, leftnode):
        """Candidate columns for a COL slot, as (Col, tier), admitted by the checker (exactly). A left operand,
        whose partner is not drawn yet, is ranked by the best partner the scope offers it."""
        sem = self.cat.sem
        frames = getattr(s, "frames", [])
        top = next((f for f in reversed(frames) if f[0] not in ("CAST", "FUNC")), None)
        out = []
        for t, c, a, (v, b) in self._candidates(s, slot, True):
            if v == "contradicted":
                if b == "grain": self.grain_hits += 1
                continue
            if top is not None and top[0] == "ARITH" and top[2] == "l": tier = self.partnered(s, top[1], t, c.name)
            else: tier = ("strong", "plausible", "unknown")[sem.tier(v, b)]
            out.append((Col(t, c.name, t, slot), tier))
        return out

    def count_exclusions(self, s, slots, targets):
        """At a real decision: every column candidate of the offered types, and every object offered for reuse, that
        a contract rejects here -- by the operators judging it and the basis. What the contracts prevented."""
        sem, frames = self.cat.sem, getattr(s, "frames", [])
        op = _operator(sem.near(frames))
        for slot in slots:
            for _t, _c, _a, (v, b) in self._candidates(s, slot, True):
                if v == "contradicted": self.excluded[("column: " + op, b)] += 1
        rep = self.repeated(s)
        for e in targets:
            v, b = sem.at_slot(frames, self.record_of(s, e), rep)
            if v == "contradicted": self.excluded[("reuse: " + op, b)] += 1

    def has_column(self, s, slot, par, side, leftnode, exact=True):
        """Is some column admissible here? Stops at the first one."""
        return any(v[0] != "contradicted" for _t, _c, _a, v in self._candidates(s, slot, exact))

    def partnered(self, s, sym, t, c):
        """A left operand's tier: the best verdict some column in scope would give it as a partner."""
        key = (tuple(s.scope), sym, t, c)
        if key not in self._partner:
            sem = self.cat.sem; a = self.cat.ann[(t, c)]
            ranks = [sem.tier(*sem.arith(sym, a, self.cat.ann[(u, x.name)])[1:]) for u in s.scope for x in self.cat.cols.get(u, []) if (u, x.name) != (t, c)]
            best = min([r for r in ranks if r is not None], default=2)
            self._partner[key] = ("strong", "plausible", "unknown")[best]
        return self._partner[key]

    def column(self, s, slot, par, side, leftnode):
        cands = self.columns(s, slot, par, side, leftnode)
        best = next((t for t in ("strong", "plausible", "unknown") if any(c[1] == t for c in cands)), None)
        sup = [c for c in cands if c[1] == best] if best else cands
        col, tier = self.rng.choice(sup or cands)
        self.log.append(("%s column in %s" % (slot, par), "%s.%s" % (col.table, col.name),
                         "%d candidates, %d preferred" % (len(cands), len(sup))))
        return col

    def node_report(self, p):
        """Every contract verdict of a delivered program, read by the checker's own walk (`Semantics.nodes`): the
        final check's verdicts, reported. Arithmetic is classed by its operands -- a PARAMETER beside an operand (with
        the parameter's kind, how its value was chosen), two QUANTITIES (stored columns, summaries of them, step
        outputs of either), or a DERIVED operand; every other operator by its constructor."""
        sem = self.cat.sem
        out = collections.Counter()
        tiername = lambda t, b: {"supported": "supported, plausible (model)" if b == "model" else "supported, strong"}.get(t, t)
        for e, steps, rep in sem.nodes(p):
            t, b = sem.verdict(e, steps, rep)
            name = tiername(t, b)
            if not isinstance(e, Arith):
                out["%s | %s (%s)" % (type(e).__name__.lower(), name, b or "no evidence")] += 1
                continue
            la, ra = sem.record(e.l, steps), sem.record(e.r, steps)
            cl, cr = isinstance(e.l, Const), isinstance(e.r, Const)
            if cl or cr:
                c = e.l if cl else e.r
                info = self.kinds.get(id(c))
                kind = info[1] if info and info[2] is c else "?"
                how = {"WEIGHT": "stated by the question", "SCORE": "stated by the question", "REFERENCE": "read from the rows" if self.grounded.get(id(c)) is c else "no stored values",
                       "CONVERT": "declared conversion table", "WHOLE": "the unit's whole", "ZERO": "zero"}.get(kind, "")
                out["operand and parameter | %s (%s) | %s: %s" % (name, b or "no evidence", kind, how)] += 1
            elif la.kind == "const" or ra.kind == "const":
                out["a constant under a cast or function | %s (%s)" % (name, b or "no evidence")] += 1
            elif la.quantity and ra.quantity:
                out["two quantities | %s (%s) | forms %s/%s" % (name, b or "no evidence", la.quantity[1], ra.quantity[1])] += 1
            else:
                what = "unit known on both" if la.unit and ra.unit else "unit known on one" if la.unit or ra.unit else "no unit"
                out["a derived operand | %s (%s) | %s" % (name, b or "no evidence", what)] += 1
        return out

    # ---- literals: read off the query's own rows
    def probe(self, s, e, distinct=False, filtered=True):
        """The values expression `e` takes over this query's FROM (its steps, base and joins so far), grouped
        by the query's keys when `e` aggregates. Row facts belong to the current query, not the catalogue."""
        from specbridge.pd.structures.algebra import emit, emit_pred, _aggregating
        self.last_probe = "unbuildable"
        if e is None or not getattr(s, "base", None): return []
        try:
            sql = ("WITH " + ", ".join("%s AS (%s)" % (qname(n), emit(q)) for n, q in s.steps) + " ") if s.steps else ""
            sql += "SELECT %s%s " % ("DISTINCT " if distinct else "", emit_expr(e)) + self._from(s)
            conds = [w for w in getattr(s, "where_so_far", []) if not _aggregating(w)] if filtered else []
            if conds: sql += " WHERE " + " AND ".join(emit_pred(w) for w in conds)
            if _aggregating(e) and s.groupkeys: sql += " GROUP BY " + ", ".join(emit_expr(g) for g in s.groupkeys)
        except Exception:
            return []
        v = self.cat.distribution(sql)
        self.last_probe = self.cat.__dict__.get("_dist_status", {}).get(sql, "ok")   # ok | empty | error | timeout
        return v

    def _from(self, s):
        """FROM of the partial query: its base and the joins so far."""
        from specbridge.pd.structures.algebra import emit_pred
        sql = "FROM %s AS %s" % (qname(s.base), qname(s.base))
        for j in s.joined:
            sql += (" CROSS JOIN %s AS %s" % (qname(j.table), qname(j.alias)) if j.on is None else
                    " %s JOIN %s AS %s ON %s" % ("LEFT" if j.kind == "left" else "INNER", qname(j.table), qname(j.alias), emit_pred(j.on)))
        return sql

    def filter_triviality(self, s, e, op, v):
        """REPORTING ONLY, never acceptance: inside an aggregate's FILTER, does the filter as bound so far (its earlier
        conjuncts and this condition) keep no row, or every row, of the rows the query's WHERE keeps? One bounded probe
        each; a probe that errs or times out classifies nothing."""
        from specbridge.pd.structures.algebra import emit, emit_pred, _aggregating, Cmp
        sym = {"EQ": "=", "NE": "!=", "LT": "<", "LE": "<=", "GT": ">", "GE": ">="}.get(op)
        if not getattr(s, "in_filter", 0) or sym is None or e is None or not getattr(s, "base", None): return
        try:
            head = ("WITH " + ", ".join("%s AS (%s)" % (qname(n), emit(q)) for n, q in s.steps) + " ") if s.steps else ""
            sibs = s.siblings[-1] if getattr(s, "siblings", None) else []
            conds = [c for c in sibs if not _aggregating(c)] + [Cmp(sym, e, Const(v))]
            f = " AND ".join("(%s)" % emit_pred(c) for c in conds)
            w = [emit_pred(c) for c in getattr(s, "where_so_far", []) if not _aggregating(c)]
            fill = lambda cond: filter_probe(head, self._from(s), w, cond)
        except Exception:
            return
        kept = self.cat.distribution(fill(f), 1); st1 = self.cat.__dict__.get("_dist_status", {}).get(fill(f))
        if st1 == "empty": self.trivial.append("an aggregate FILTER that keeps no row"); return
        if st1 != "ok": return
        out = fill("NOT COALESCE((%s), 0)" % f)
        self.cat.distribution(out, 1)
        if self.cat.__dict__.get("_dist_status", {}).get(out) == "empty": self.trivial.append("an aggregate FILTER that keeps every row")

    def numeric(self, s, e):
        a = self.record_of(s, e)
        if a.slot in ("NUM", "DATE"): return True
        if a.slot in ("TEXT", "KEY"): return False
        vals = self.probe(s, e, distinct=True)
        return bool(vals) and isinstance(vals[0], (int, float))

    # ---- literals from cached metadata (probes only when `self.probes`)
    def _stored(self, s, e):
        """The stored column an expression reads as a value, through CAST, a unit-preserving function, or a
        step's output that is itself a stored column. None for a computation."""
        from specbridge.pd.structures.actions import _PASS
        while True:
            if isinstance(e, Cast): e = e.expr
            elif isinstance(e, Func) and e.name.lower() in _PASS and e.args: e = e.args[0]
            else: break
        if not isinstance(e, Col): return None
        if (e.table, e.name) in self.cat.ann: return (e.table, e.name)
        for n, q in s.steps:                                   # a step's output: what the step selected there
            if n == e.table and isinstance(q, Program) and e.name[:1] == "o" and e.name[1:].isdigit():
                i = int(e.name[1:])
                if i < len(q.select): return self._stored(s, q.select[i][0])
        return None

    def typical(self, s, e):
        """A value the expression typically takes, from cached column statistics propagated through it."""
        from specbridge.pd.structures.algebra import Agg
        sc = self._stored(s, e)
        if sc: qs = self.cat.quantiles(*sc); return qs[2] if qs and isinstance(qs[2], (int, float)) else None
        if isinstance(e, Const): return e.value if isinstance(e.value, (int, float)) else None
        if isinstance(e, Arith):
            l, r = self.typical(s, e.l), self.typical(s, e.r)
            if l is None or r is None: return None
            try: return {"+": l + r, "-": l - r, "*": l * r, "/": l / r if r else None, "%": l % r if r else None}[e.op]
            except Exception: return None
        if isinstance(e, Agg):
            if e.fn.upper() == "COUNT":
                n = self.cat.world.rel[s.scope[0]].n if s.scope else None
                return max(1, n // 10) if n else None
            v = self.typical(s, e.arg) if e.arg is not None else None
            return v * 10 if v is not None and e.fn.upper() == "SUM" else v
        if isinstance(e, Func) and e.args: return self.typical(s, e.args[0])
        return None

    def has_value(self, s, e):
        if self.probes: return any(isinstance(v, str) for v in self.probe(s, e, distinct=True, filtered=False)[:200])
        sc = self._stored(s, e)
        if sc: return bool(self._fresh(s, e, [v for v in self.cat.values(*sc)[:50] if isinstance(v, str)]))
        if isinstance(e, Case): return any(isinstance(v, Const) and isinstance(v.value, str) for _p, v in e.whens)
        return False

    def has_threshold(self, s, e):
        if self.probes:
            return any(isinstance(v, (int, float)) or (isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}", v))
                       for v in self.probe(s, e, filtered=False)[:200])
        sc = self._stored(s, e)
        if sc:
            qs = self.cat.quantiles(*sc)
            ok = bool(qs) and (isinstance(qs[0], (int, float)) or bool(re.match(r"^\d{4}-\d{2}-\d{2}", str(qs[0]))))
            return ok and bool(self._fresh(s, e, list(self.cat.values(*sc)[:50]) + qs[1:4]))
        t = self.typical(s, e)
        return t is not None and bool(self._fresh(s, e, [round(t, 2) if isinstance(t, float) else t]))

    def _fresh(self, s, e, vals):
        """Values that would not repeat a sibling condition (IDENTITY applied to a binding)."""
        from specbridge.pd.structures.algebra import Cmp
        sibs = s.siblings[-1] if getattr(s, "siblings", None) else []
        op = {"EQ": "=", "NE": "!=", "LT": "<", "LE": "<=", "GT": ">", "GE": ">="}.get(getattr(s, "cmp_op", None))
        if not sibs or op is None: return vals
        return [v for v in vals if Cmp(op, e, Const(v)) not in sibs]

    def threshold(self, s, e):
        v = self._threshold(s, e)
        if self.probes: self.filter_triviality(s, e, getattr(s, "cmp_op", None), v)
        sc = self._stored(s, e)
        self.log.append(("threshold vs %s" % (emit_expr(e)[:50] if e is not None else "?"), v,
                         ("a stored value of %s.%s" % sc if getattr(s, "cmp_op", None) in ("EQ", "NE") else "a quantile of %s.%s" % sc)
                         if sc else "the typical value of the expression, from column statistics"))
        return v

    def _threshold(self, s, e):
        """A value the expression takes, chosen so that the comparison it enters KEEPS A ROW of the values it was read
        from: an equality takes a value that is there, exactly (never a rounded one); > takes one below the largest,
        < one above the smallest. Read from the query's own rows (its FROM, joins and the conditions bound so far)
        with probes, else from the column's cached statistics; the expression's typical value when neither applies."""
        op = getattr(s, "cmp_op", None)
        keeps = lambda v, lo, hi: (v < hi) if op == "GT" else (v > lo) if op == "LT" else True
        rnd = lambda v: round(v, 2) if isinstance(v, float) else v
        if e is None: return 0                            # no left operand to read a value from (not reached once cmp_left is restored)
        if self.probes:
            r = self._probed_threshold(s, e, op, keeps, rnd)
            if r is not None: return r[0]
        sc = self._stored(s, e)
        if sc and op in ("EQ", "NE"):
            vals = self._fresh(s, e, [v for v in self.cat.values(*sc)[:50] if not isinstance(v, str) or re.match(r"^\d{4}-\d{2}-\d{2}", v)])
            if vals: return self.rng.choice(vals)
        cands = self.cat.quantiles(*sc)[1:4] if sc and self.cat.quantiles(*sc) else [self.typical(s, e)]
        cands = [rnd(v) for v in cands if v is not None]
        ext = self.cat.extent(*sc) if sc else None
        if ext and all(isinstance(x, (int, float)) for x in ext) and op in ("GT", "LT"):
            cands = [v for v in cands if isinstance(v, (int, float)) and keeps(v, *ext)] or \
                    ([ext[0]] if op == "GT" and ext[0] < ext[1] else [ext[1]] if op == "LT" and ext[0] < ext[1] else [])
        cands = self._fresh(s, e, cands)
        lo = getattr(s, "between_lo", None)             # BETWEEN's upper bound: only values the contract allows
        if isinstance(lo, Const):
            sem = self.cat.sem
            cands = [v for v in cands if sem.between(sem.const(lo.value), sem.const(v))[0] != "contradicted"] or [lo.value]
        if cands: return self.rng.choice(cands)
        if self.probes and getattr(self, "_unavailable", False):
            raise Unsupported("probe unavailable: %s (%s), and no statistics to bind from" % (emit_expr(e)[:40], self._unavailable))
        if self.probes:
            # no stored column and no statistics (a step's output, a computation): the values the expression takes over
            # its FROM, without the conditions (one bounded probe, cached) -- in place of an invented 0. In WHERE, where
            # the value decides which rows exist, a value the conditions so far do not keep is not offered.
            if s.clause != "where":
                vals = sorted(set(v for v in self.probe(s, e, filtered=False) if isinstance(v, (int, float))))
                if vals:
                    lo, hi = vals[0], vals[-1]
                    inside = self._fresh(s, e, [rnd(x) for x in vals if keeps(x, lo, hi) and keeps(rnd(x), lo, hi)])
                    if inside: return self.rng.choice(inside)
            raise Unsupported("no allowed candidate found: %s has no numeric value to read" % emit_expr(e)[:40])   # a search failure, not a claim about rows
        return 0

    def _probed_threshold(self, s, e, op, keeps, rnd):
        """A threshold for (operator, expression) in the current query, from what the probe shows. Returns (value,),
        or None to fall back to cached statistics. SEARCH FAILURES and PROVEN IMPOSSIBILITY are told apart:
          the probe errors or times out     couldn't check: one retry without the conditions, else statistics
          the conditions so far keep no row PROVEN (rows confirmed empty) where every row must pass: refused
          =  (a match is required)          an observed value; none allowed -> "no allowed candidate found"
          != and a value leaves other rows  an observed value (selective); else an unobserved one: TRIVIAL
          < or > and a value splits rows    bound: a selective condition is preferred
          < or > and none splits            a boundary outside the range (need not occur in the data): bound,
                                            labelled TRIVIAL (keeps every row), never refused"""
        self._unavailable = None
        must = s.clause == "where" and not getattr(s, "loose", 0)
        num = lambda xs: [v for v in xs if isinstance(v, (int, float))]
        vals = num(self.probe(s, e)); st = self.last_probe
        if st in ("error", "timeout", "unbuildable"):
            vals = num(self.probe(s, e, filtered=False)); st2 = self.last_probe
            if st2 in ("error", "timeout", "unbuildable"):
                self._unavailable = st2; self.evidence["probe unavailable: " + st2] += 1; return None
            self.evidence["probe retried without the conditions (%s)" % st] += 1
        elif st == "empty":
            if must: raise Unsupported("no row under the conditions so far (confirmed): %s" % emit_expr(e)[:40])
            vals = num(self.probe(s, e, filtered=False))
        if not vals: return None                                         # text or nothing numeric: statistics
        if op == "EQ":                            # = needs a match: a value that is there
            c = self._fresh(s, e, sorted(set(vals)))
            if c: return (self.rng.choice(c),)
            raise Unsupported("no allowed candidate found: every value of %s repeats a sibling condition" % emit_expr(e)[:40])
        if op == "NE":                            # != needs no match: a value that leaves other rows (selective) if any
            d = sorted(set(vals))
            c = self._fresh(s, e, d) if len(d) > 1 else []
            if c: return (self.rng.choice(c),)
            # all values equal, or every observed value repeats a sibling: a value outside them keeps every row
            self.trivial.append("a filter that keeps every row" if must else "a condition true for every row")
            return (math.floor(d[0]) - 1,)
        lo, hi = vals[0], vals[-1]
        near = lambda x: rnd(x) if keeps(rnd(x), lo, hi) else x          # rounded for reading, unless rounding loses the split
        c = self._fresh(s, e, [near(x) for x in (vals[min(len(vals) - 1, int(len(vals) * q))] for q in (0.25, 0.5, 0.75)) if keeps(near(x), lo, hi)])
        if not c: c = self._fresh(s, e, [near(x) for x in sorted(set(vals)) if keeps(near(x), lo, hi)])
        if c and (op not in ("GE", "LE") or lo < hi): return (self.rng.choice(c),)      # splits the rows
        if op in ("GE", "LE"):                                           # all equal: the value itself keeps every row
            self.trivial.append("a filter that keeps every row" if must else "a condition true for every row")
            return (rnd(lo),)
        if op not in ("GT", "LT"): return None
        # No value splits them (all equal). A THRESHOLD need not occur in the data: a boundary just outside the range
        # retains every row -- one of the expression's wider values if it has one, else the next whole number beyond
        # the range (-0.5 < 0). The operator and the expression stay as P drew them; the condition is labelled trivial.
        wide = sorted(set(num(self.probe(s, e, filtered=False)))) if self.last_probe == "ok" else []
        ret = [x for x in wide if (x < lo if op == "GT" else x > hi)]
        v = (ret[-1] if op == "GT" else ret[0]) if ret else (math.floor(lo) - 1 if op == "GT" else math.ceil(hi) + 1)
        self.trivial.append("a filter that keeps every row" if must else "a condition true for every row")
        return (v,)

    def value(self, s, e):
        v = self._value(s, e)
        if self.probes: self.filter_triviality(s, e, getattr(s, "cmp_op", None), v)
        sc = self._stored(s, e)
        self.log.append(("value vs %s" % (emit_expr(e)[:50] if e is not None else "?"), v,
                         "a stored value of %s.%s" % sc if sc else "a label of the expression"))
        return v

    def _value(self, s, e):
        """A value the expression holds: a stored category, or one of a CASE's own labels."""
        if self.probes:
            vals = [v for v in self.probe(s, e, distinct=True)[:200] if isinstance(v, str)]
            if not vals and self._stored(s, e): vals = self.cat.values(*self._stored(s, e))     # the column's own values, never '?'
        else:
            sc = self._stored(s, e)
            vals = self.cat.values(*sc) if sc else [v.value for _p, v in e.whens if isinstance(v, Const)] if isinstance(e, Case) else []
        vals = self._fresh(s, e, [v for v in vals if isinstance(v, str)][:50])
        return self.rng.choice(vals) if vals else "?"

    def reference(self, s, e):
        """The operand's typical value, from cached statistics of the rows: a bare column's stored middle, or the
        typical value propagated through the expression. None when the rows give none (or it is zero, which no
        ratio can be taken to)."""
        u = _unwrap(e)
        if isinstance(u, Col):
            st = self.cat.world.rel.get(u.table)
            c = st.cols.get(u.name) if st else None
            if c is not None and c.mid is not None and c.mid != 0: return round(c.mid, 2)
        try: v = self.typical(s, e)
        except Exception: v = None
        if not isinstance(v, (int, float)) or v == 0 or v != v: return None
        return float("%.3g" % v)

    def constant(self, s, kind, par, side, operand, role=None):
        """THE TARGET-BINDING RULE of a parameter, by its kind (actions.const_kinds). `operand` is the other side of
        the operator; a parameter on the left is bound again once its right is known. A WEIGHT and a SCORE are
        drawn uniformly from a declared list of plain numbers, independent of the source and of the data: the
        question states them, and that is their only reason."""
        if role == "SCORE" or par == "CASE":
            v = {"ZERO": 0, "ONE": 1}.get(kind)
            if v is None: v = self.rng.choice(SCORES)
            self.log.append(("parameter %s in CASE" % kind, v, "stated by the question" if kind == "SCORE" else "an indicator value"))
            return v
        op = {"ADD": "+", "SUBTRACT": "-", "MULTIPLY": "*", "DIVIDE": "/", "MOD": "%"}.get(par.split(":")[-1], "")
        if operand is None: return _placeholder_value(kind)          # a left parameter before its right: bound again after
        a = self.cat.sem.record(operand, dict(getattr(s, "steps", ())))
        self._ref_ok = False
        if kind == "ZERO": v = 0
        elif kind == "WHOLE": v = 100 if _unit_word(a) == "percent" else 1
        elif kind == "CONVERT":
            conv = conversions(op, a)
            v = self.rng.choice(conv)[0] if conv else 1
            v = int(v) if v == int(v) else v
        elif kind == "WEIGHT": v = self.rng.choice(MODULI if op == "%" else WEIGHTS)
        elif kind == "REFERENCE":
            r = self.reference(s, operand)
            v = r if r is not None else 1; self._ref_ok = r is not None
        else: v = 1
        self.log.append(("parameter %s in %s %s" % (kind, par, side), v, "unit %s" % (_unit_word(a) or "unknown")))
        return v

    def clock(self):
        return "2025-01-01"
