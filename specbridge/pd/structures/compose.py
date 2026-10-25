"""specbridge.pd.structures.compose -- P_D AS A TYPED RECURSIVE GRAMMAR WITH A DEPTH-CONDITIONED AUTOREGRESSIVE SAMPLER (v3, 2026-09-30).
docs/COMPOSE.md. Grounded in one database's catalogue (specbridge.pd.structures.dbfirst.Signature); no benchmark is read.

A PROGRAM is built stage by stage. The current stage has a LEVEL (what one of its rows is) and typed MEASURES:
  level    row of a record table t | entity e (t repeats under e) | entity e within group g | group g | all
  measure  unit (a count's unit names its population), kind (flow / stock, catalogue additivity over time), additive (may
           be summed across the rows it is aggregated over), arithmetic depth, lineage (which comparisons made it), slots
           (which base quantities it derives from)
RULES (each a typed operation; a rule applies only when the types allow it):
  AGG       coarsen the level (rows -> entity | entity-in-group | group | all; entity-in-group -> group | all; entity/group
            -> all). SUM only if the measure is additive, AVG always. From rows: 1-2 base quantities (dbgrammar row
            quantities, v2 meaning rules), or the record count.                                         +1 step
  ARITH     a difference or ratio of two measures of the current stage: same unit and same kind, disjoint slots (never a
            quantity with itself or with its own sum/average), and never SUM(x)/COUNT(*) (that restates AVG). +1 A
  BASELINE  compare a measure with its average over a coarser level: the gap v - avg (+1 A) or the index v / avg (+1 A),
            optionally keeping only rows above it. Each (comparison, level) at most once per lineage.  +2 steps
  SHARE     an additive measure as a share of its total over a coarser level (+1 A).                +2 steps
  RANK      rank within the group (entity-in-group level), then keep the top 3.                      +2 steps
  FINAL     the current stage is the answer (ordered, first 10 rows, at entity and row levels).
CANONICAL FORMS: one ARITH per stage; operand pairs ordered; a coarsening strictly coarsens; no repeated comparison at one
level on one lineage -- so equivalent constructions are not counted twice and no rule restates a column.
DEPTH is MEASURED on the emitted SQL (specbridge.pd.structures.depth: dependency-based); the construction's bookkeeping steers the
sampler toward a cell, and the measured depth decides where a program is filed (no cross-check between the two is run).
BOUNDS: A_MAX, S_MAX, at most 3 measures per stage. Within them, `reach` computes EXACTLY which (A, S) cells each state can
still complete to, by memoised search over the TYPES (not the SQL); the sampler only takes moves that can still reach its
target cell, so a requested cell is either delivered or proven unreachable under this grammar, catalogue and bounds."""
import collections, dataclasses, itertools, json, random
from specbridge.pd.structures.dbfirst import Signature, Q
from specbridge.pd.structures import dbgrammar as G

A_MAX, S_MAX, M_MAX = 6, 8, 3
VERSION = "compose-v3.4"   # 2026-10-13: opt-in extra rules (COND) leave this unchanged; Space.version names them
EXTRA_VERSION = {"cond": "cond-v1", "filter": "filter-v1"}


@dataclasses.dataclass(frozen=True)
class M:
    expr: str                # SQL of the measure in the current stage
    unit: str
    kind: object             # True flow, False stock, None unknown
    add: bool
    depth: int
    lin: frozenset = frozenset()
    slots: frozenset = frozenset()
    name: str = ""
    count_of: str = ""       # "t" for COUNT(*) of t's records
    facts: frozenset = frozenset()   # (fact, K) PROVEN for the stage's CURRENT population with equal row weights:
                                     # ("mean0", K) a gap to the K average: its mean over every K group is 0
                                     # ("mean1", K) an index against the K average: its mean over every K group is 1
                                     # ("sum1", K)  a share of the K total: it sums to 1 over every K group
                                     # cleared whenever the rows change (an aggregation, or an "above" filter)
    computed: frozenset = frozenset()  # v3.2: (fn, K) -- this measure's K-level AVG (a baseline) or SUM (a share) is ALREADY
                                     # computed over the current rows; computing it again would be a step that recomputes an
                                     # existing result, so the comparison is not offered. Cleared when the rows change.

    def type(self): return (self.unit, self.kind, self.add, self.depth, self.lin, self.slots, bool(self.count_of), self.facts, self.computed)


@dataclasses.dataclass(frozen=True)
class Stage:
    level: tuple             # ("row",) ("e", cc) ("eg", cc, gt, g) ("g", gt, g) ("all",)
    ms: tuple                # measures
    steps: int               # dependency steps of this stage (0 = the record table's rows, not a stage yet)
    arith: bool = False      # an ARITH already added in this stage
    rank: bool = False       # a rank is pending (the answer must filter it)

    def sig(self): return (self.level, tuple(m.type() for m in self.ms), self.steps, self.arith, self.rank)


def naive_quantities(S, t):
    """ABLATION "profile": row quantities from the SQL schema alone -- every column with a numeric declared type (keys
    included), one unit, additive; a difference and a ratio for every pair. What a generator without the profile would see."""
    import re
    num = [r[1] for r in S.con.execute('PRAGMA table_info("%s")' % t) if re.search("INT|REAL|NUM|FLOA|DOUB|DEC", (r[2] or "").upper())]
    col = lambda c: "%s.%s" % (Q(t), Q(c))
    out = [{"sql": col(c), "depth": 0, "unit": "number", "additive": True, "why": [], "name": c, "ops": {c}} for c in num]
    for a, b in itertools.combinations(num, 2):
        out.append({"sql": "(%s - %s)" % (col(a), col(b)), "depth": 1, "unit": "number", "additive": True, "why": [], "name": "%s minus %s" % (a, b), "ops": {a, b}})
        out.append({"den": b, "sql": "(CAST(%s AS REAL) / %s)" % (col(a), col(b)), "depth": 1, "unit": "ratio", "additive": False, "why": [], "name": "%s relative to %s" % (a, b), "ops": {a, b}})
    return out


class Space:
    """The grammar grounded in one database: levels and row quantities per record table, typed moves, exact reachability."""

    def __init__(self, db, ablate=frozenset(), extra=frozenset()):
        # ABLATE (2026-10-05, ablation study only; empty by default): switch off one mechanism to measure what it contributes --
        # "profile" (column meaning: roles, units, kinds, additivity -> every numeric column is one unit, additive), "varies"
        # (row quantities must vary on the data), "types" (unit / kind / additivity rules on moves), "restate" (no restated,
        # recomputed or collapsing comparison; no quantity with itself)
        self.ablate = A = frozenset(ablate)
        self.db = db; self.S = S = Signature(db)
        self.rec = [t for t in S.cat["tables"] if any(c == t and S.many(t, cc) for c, cc, p, pc in S.fk)]
        self.qs, self.levels, self.key = {}, {}, {}
        for t in self.rec:
            qs = []
            for q in (naive_quantities(S, t) if "profile" in A else G.quantities(S, t)):
                u = q["unit"]
                if "profile" not in A and G.is_count(S, t, next(iter(q["ops"]))) and q["depth"] == 0: u = "count of %s" % (G.population(S, t, next(iter(q["ops"]))) or "?")
                kind = None if "profile" in A else ((S.col.get("%s.%s" % (t, next(iter(q["ops"]))), {}) or {}).get("additive") or {}).get("time")
                qs.append(dict(q, unit=u or q["unit"], kind=kind))
            # v3.4: a row quantity must vary on the data (>= 2 values; a derived one differs from every column; a ratio's
            # denominator positive) -- the v2 row-level check (dbgrammar.varies), which v3 had stopped applying: wta_1's
            # matches.best_of is 3 on every row, and 15 delivered tasks carried it as an output that is always 3.0
            self.qs[t] = [q for q in qs if q["unit"] and ("varies" in A or G.varies(S, t, q))]
            self.key[t] = (S.cat["tables"].get(t, {}).get("keys") or [None])[0] or S.cols(t, lambda m: m.get("semantic_role") == "identifier")[0]
            L = []
            for c, cc, e, ek in S.fk:
                if c != t or not S.many(t, cc): continue
                L.append(("e", cc, e, ek))
                for gt, g, j in G.groups(S, e): L.append(("eg", cc, e, ek, gt, g, tuple(j)))
            for gt, g, j in G.groups(S, t): L.append(("g", gt, g, tuple(j)))
            L.append(("all",))
            self.levels[t] = L
        self.memo = {}
        self.untyped = set()     # ablation "types": (stage signature, move) pairs the type rules would have refused
        # EXTRA RULES (2026-10-13, opt-in; empty by default so every earlier corpus is unchanged): "cond" = conditional
        # aggregation (COND): a measure aggregated only over the rows where a categorical column takes one value.
        self.extra = frozenset(extra); self.conds = {t: (self._conditions(t) if "cond" in self.extra else []) for t in self.rec}
        # "filter" (2026-10-16) = one condition on the first stage's rows that leaves a calculation choice open (FILTER)
        self.preds = {t: (self._predicates(t) if "filter" in self.extra else []) for t in self.rec}
        self.version = VERSION + "".join("+" + EXTRA_VERSION[x] for x in sorted(self.extra))

    def _conditions(self, t, lo=0.1, hi=0.9, per_col=2, cap=6):
        """COND candidates for record table t, decided on the DATA (gold-free): non-key columns with 2..20 distinct non-missing
        values, and their values that cover between `lo` and `hi` of the rows -- so a condition always keeps some rows and drops
        some. The most balanced first. [(column, value, share)]"""
        S = self.S; con = S.con; keys = {cc for c, cc, _e, _ek in S.fk if c == t} | {self.key[t]}
        quant = {o for q in self.qs.get(t, []) for o in q["ops"]}            # a measured quantity is not a category
        out = []
        for r in con.execute('PRAGMA table_info("%s")' % t).fetchall():
            col = r[1]
            if col in keys or col in quant or (S.col.get("%s.%s" % (t, col)) or {}).get("scale") in ("ratio", "interval"): continue
            n, d = con.execute('SELECT COUNT(*), COUNT(DISTINCT "%s") FROM "%s"' % (col, t)).fetchone()
            if not n or not (2 <= d <= 20): continue
            for v, k in con.execute('SELECT "%s", COUNT(*) FROM "%s" WHERE "%s" IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 6' % (col, t, col)).fetchall()[:per_col * 3]:
                if lo <= k / n <= hi and isinstance(v, (str, int)) and str(v).strip() != "": out.append((col, v, k / n))
        out.sort(key=lambda x: (abs(x[2] - 0.5), x[0], str(x[1]))); seen = collections.Counter(); keep = []
        for c in out:
            if seen[c[0]] < per_col: keep.append(c); seen[c[0]] += 1
        return keep[:cap]

    def _predicates(self, t, lo=0.2, hi=0.8, per_kind=3):
        """FILTER candidates for record table t (2026-10-16, opt-in): one condition on t's rows, each with the condition of
        the OTHER reading of one calculation choice. Decided on the DATA (gold-free), where the choice is made: the condition
        keeps between `lo` and `hi` of the rows, and the two readings keep different rows of t.
          window   a date column between two of its own values, ends included | ends excluded           (time scope)
          bound    a numeric column at least one of its frequent values | more than it                    (value bounds)
          none     rows of entities with no record where category = v | entities with a record where it is not v   (negation)
          both     rows of entities with ONE record meeting two conditions | a record for each                (condition linkage)
          outer    the entity-level count keeps entities with records only | every entity, with zero       (population scope)
        [{kind, sql, alt, text, ...}]: sql and alt are SQL conditions on t's rows (outer: the entity table and keys)."""
        S = self.S; con = S.con; out = []
        n = con.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
        if not n: return out
        c_ = lambda c: _q(t, c)
        lit = lambda v: "'%s'" % str(v).replace("'", "''") if isinstance(v, str) else repr(v)
        kept = lambda w: con.execute('SELECT COUNT(*) FROM "%s" WHERE %s' % (t, w)).fetchone()[0]
        role = lambda c: (S.col.get("%s.%s" % (t, c)) or {}).get("semantic_role")
        cols = [r[1] for r in con.execute('PRAGMA table_info("%s")' % t)]
        keys = {cc for c, cc, _e, _ek in S.fk if c == t} | {self.key[t]}
        ok = lambda k: lo <= k / n <= hi
        def add(kind, sql, alt, text, **kw):
            k, k2 = kept(sql), kept(alt) if kind != "outer" else None
            if ok(k) and (k2 is None or k2 != k or kind in ("none", "both")): out.append(dict(kind=kind, sql=sql, alt=alt, text=text, share=k / n, **kw))
        for c in cols:                                                     # window
            if role(c) != "date" or c in keys: continue
            vs = [r[0] for r in con.execute('SELECT "%s" FROM "%s" WHERE "%s" IS NOT NULL AND typeof("%s") = \'text\' ORDER BY 1' % (c, t, c, c))]
            if len(set(vs)) < 4: continue
            a, b = vs[int(len(vs) * 0.3)], vs[int(len(vs) * 0.7)]
            if a == b: continue
            add("window", "%s >= %s AND %s <= %s" % (c_(c), lit(a), c_(c), lit(b)), "%s > %s AND %s < %s" % (c_(c), lit(a), c_(c), lit(b)),
                "%s.%s from %s to %s" % (t, c, a, b), column=c)
        for c in cols:                                                     # bound
            if role(c) not in ("measure", "count") or c in keys: continue
            best = None
            for v, k in con.execute('SELECT "%s", COUNT(*) FROM "%s" WHERE typeof("%s") IN (\'integer\', \'real\') GROUP BY 1 HAVING COUNT(*) >= 2 ORDER BY 2 DESC LIMIT 12' % (c, t, c)):
                share = kept("%s >= %s" % (c_(c), lit(v))) / n
                if lo <= share <= hi and (best is None or abs(share - 0.5) < abs(best[1] - 0.5)): best = (v, share)
            if best: add("bound", "%s >= %s" % (c_(c), lit(best[0])), "%s > %s" % (c_(c), lit(best[0])), "%s.%s at least %s" % (t, c, best[0]), column=c)
        cats = self._conditions(t, per_col=1, cap=6)
        ents = [cc for c, cc, _e, _ek in S.fk if c == t and S.many(t, cc)]
        sub = lambda cc, w: '(SELECT "x"."%s" FROM "%s" AS "x" WHERE %s AND "x"."%s" IS NOT NULL)' % (cc, t, w, cc)
        xc = lambda col, v, op="=": '"x"."%s" %s %s' % (col, op, lit(v))
        for cc in ents:
            for col, v, _sh in cats:                                       # none
                if col == cc: continue
                mixed = con.execute('SELECT COUNT(*) FROM (SELECT "%s" FROM "%s" GROUP BY 1 HAVING SUM("%s" = %s) > 0 AND SUM("%s" <> %s) > 0)' % (cc, t, col, lit(v), col, lit(v))).fetchone()[0]
                if mixed: add("none", "%s NOT IN %s" % (c_(cc), sub(cc, xc(col, v))), "%s IN %s" % (c_(cc), sub(cc, xc(col, v, "<>"))),
                              "%s whose records include none with %s = %s" % (cc, col, v), entity=cc, column=col)
            for (c1, v1, _a), (c2, v2, _b) in itertools.combinations(cats, 2):   # both
                if c1 == c2 or cc in (c1, c2): continue
                add("both", "%s IN %s" % (c_(cc), sub(cc, "%s AND %s" % (xc(c1, v1), xc(c2, v2)))),
                    "%s IN %s AND %s IN %s" % (c_(cc), sub(cc, xc(c1, v1)), c_(cc), sub(cc, xc(c2, v2))),
                    "%s with a record where %s = %s and %s = %s" % (cc, c1, v1, c2, v2), entity=cc, column="%s,%s" % (c1, c2))
        for c, cc, e, ek in S.fk:                                          # outer
            if c != t or not S.many(t, cc): continue
            m = con.execute('SELECT COUNT(*) FROM "%s" WHERE "%s" NOT IN (SELECT "%s" FROM "%s" WHERE "%s" IS NOT NULL)' % (e, ek, cc, t, cc)).fetchone()[0]
            tot = con.execute('SELECT COUNT(*) FROM "%s"' % e).fetchone()[0]
            if m and m < tot: out.append(dict(kind="outer", sql="", alt="", text="every %s, including the %d without %s records" % (e, m, t), entity=cc, parent=e, pkey=ek, share=1 - m / tot))
        by = collections.defaultdict(list)
        for x in sorted(out, key=lambda x: (abs(x["share"] - 0.5), x["text"])): by[x["kind"]].append(x)
        return [x for k in sorted(by) for x in by[k][:per_kind]]

    # ------------------------------------------------------------------ typed moves (abstract: types only)
    def starts(self, t):
        """(level, measures) for the first stage from t's rows. Measures are ABSTRACT here: one representative quantity
        per type class; the sampler later draws a concrete quantity from the class."""
        cls = collections.OrderedDict()
        for q in self.qs[t]: cls.setdefault((q["unit"], q["kind"], q["additive"], q["depth"]), []).append(q)
        out = []
        for L in self.levels[t]:
            lvl = self._lvl(L)
            singles = []
            for k, members in cls.items():
                u, kind, add, d = k
                for fn in (["SUM", "AVG"] if add or "types" in self.ablate else ["AVG"]):
                    singles.append((k, fn))
            cnt = ("count", None)
            opts = [(s,) for s in singles] + [(cnt,)]
            for a, b in itertools.combinations(singles, 2):
                if a[0] == b[0] and a[1] == b[1]: continue          # canonical: two of one class use the class once
                if not self.pairable(t, cls, a[0], b[0]): continue   # the concrete pair must exist (disjoint columns)
                opts.append((a, b))
            for s in singles: opts.append((s, cnt))
            if self.conds.get(t):                 # COND: conditional measures, and each paired with its unconditional version
                for k, fn in singles: opts += [(("cond", k, fn),), (("cond", k, fn), (k, fn))]
                opts += [(("ccount",),), (("ccount",), cnt)]
            for o in opts: out.append((L, lvl, o))
        return out, cls

    def pairable(self, t, cls, ka, kb):
        """Is there a quantity in class ka and one in class kb built on disjoint columns? (memoised)"""
        key = ("pair", t, ka, kb)
        if key not in self.memo:
            self.memo[key] = any(a is not b and ("restate" in self.ablate or a["ops"].isdisjoint(b["ops"])) for a in cls[ka] for b in cls[kb])
        return self.memo[key]

    def _lvl(self, L):
        return {"e": lambda: ("e", L[1]), "eg": lambda: ("eg", L[1], L[4], L[5]), "g": lambda: ("g", L[1], L[2]), "all": lambda: ("all",)}[L[0]]()

    def _m_from(self, t, choice, slot):
        if choice[0] == "ccount":
            return M(expr="", unit="count of %s records" % t, kind=True, add=True, depth=0, slots=frozenset({"nc"}), name="CCOUNT", count_of=t)
        if choice[0] == "cond":
            _c, (u, kind, add, d), fn = choice
            return M(expr="", unit=u, kind=kind, add=(fn == "SUM"), depth=d, slots=frozenset({slot + "c"}), name="C" + fn)
        if choice[0] == "count":
            return M(expr="COUNT(*)", unit="count of %s records" % t, kind=True, add=True, depth=0, slots=frozenset({"n"}), name="number of %s records" % t, count_of=t)
        (u, kind, add, d), fn = choice
        return M(expr="", unit=u, kind=kind, add=(fn == "SUM"), depth=d, slots=frozenset({slot}), name=fn)

    @staticmethod
    def covers(L2, K):
        """Is every L2 group a union of K groups (L2 is K itself, or everything)?"""
        return L2 == K or L2 == ("all",)

    def collapses(self, m, L2):
        """v3.1: aggregating m over L2 gives a CONSTANT (or a pure count) -- mean of gaps 0, mean of indices 1, mean of
        shares = groups / rows -- when m carries a fact at a level K that L2 covers (same rows, same weights)."""
        return any(self.covers(L2, K) for _f, K in m.facts)

    def restates(self, m, op, K2):
        """v3.1: comparing m again at K2 is PROVEN constant or a restatement: a gap or index of a mean-0 / mean-1 measure at
        a covering level (divides by 0, subtracts 0, divides by 1, shifts by 1), a share of either (sums to 0 or to a
        count); a share of a share at a covering level (a count rescaling); an index of a share at its own level (= the
        index of the original measure)."""
        for f, K in m.facts:
            if not self.covers(K2, K): continue
            if f in ("mean0", "mean1"): return True
            if f == "sum1" and (op == "share" or (op == "index" and K2 == K)): return True
        return False

    def coarser(self, lvl):
        if lvl[0] == "eg": return [("g", lvl[2], lvl[3]), ("all",)]
        if lvl[0] in ("e", "g"): return [("all",)]
        return []

    def moves(self, st):
        """Abstract successor stages of st: [(move, stage')]. FINAL is ('final',)."""
        out = [(("final",), None)]
        if st.rank: return out
        ms = st.ms; TY = "types" not in self.ablate; RS = "restate" not in self.ablate
        if not st.arith and len(ms) < M_MAX:
            for i, j in itertools.permutations(range(len(ms)), 2):
                a, b = ms[i], ms[j]
                bad = a.unit != b.unit or a.kind != b.kind or (bool(a.count_of or b.count_of) and not (a.count_of and b.count_of))
                if TY and bad: continue
                if RS and (a.slots & b.slots): continue
                if bad: self.untyped.update({(st.sig(), ("diff", i, j)), (st.sig(), ("ratio", i, j))})
                if max(a.depth, b.depth) + 1 > A_MAX: continue
                if i < j:
                    out.append((("diff", i, j), dataclasses.replace(st, arith=True, ms=ms + (M("", a.unit, a.kind, a.add and b.add, max(a.depth, b.depth) + 1, a.lin | b.lin, a.slots | b.slots),))))
                if not RS or not (b.count_of and "SUM" in (a.name,)):
                    out.append((("ratio", i, j), dataclasses.replace(st, arith=True, ms=ms + (M("", "ratio", None, False, max(a.depth, b.depth) + 1, a.lin | b.lin, a.slots | b.slots),))))
        if st.steps + 1 <= S_MAX:
            for L2 in self.coarser(st.level):
                # v3.1: an aggregation that would turn a measure into a constant is not built at all (dropping the measure
                # instead would leave a computed comparison unused: steps padded with work nothing reads)
                if RS and any(self.collapses(m, L2) for m in ms): continue
                keep = tuple(range(len(ms)))
                for fns in itertools.product(*[(["SUM", "AVG"] if ms[i].add or not TY else ["AVG"]) for i in keep]):
                    if any(f == "SUM" and not ms[i].add for i, f in zip(keep, fns)): self.untyped.add((st.sig(), ("agg", L2, fns, keep)))
                    ms2 = tuple(dataclasses.replace(ms[i], add=(f == "SUM"), expr="", name=f, facts=frozenset(), computed=frozenset()) for i, f in zip(keep, fns))
                    out.append((("agg", L2, fns, keep), Stage(L2, ms2, st.steps + 1)))
        if st.steps + 2 <= S_MAX and len(ms) < M_MAX:
            for K in self.coarser(st.level):
                for i, m in enumerate(ms):
                    if m.depth + 1 > A_MAX: continue
                    # v3.2: the source measure records which of its K-level aggregates the rows already have
                    marked = lambda fn: tuple(dataclasses.replace(x, computed=x.computed | {(fn, K)}) if k == i else x for k, x in enumerate(ms))
                    for kind in ("gap", "index"):
                        if RS and ((kind, K) in m.lin or ("gap", K) in m.lin or ("index", K) in m.lin): continue
                        if RS and ("AVG", K) in m.computed: continue           # its K average exists: a second one recomputes it
                        if RS and self.restates(m, kind, K): continue
                        u = m.unit if kind == "gap" else "ratio"
                        for above in ((False, True) if kind == "gap" else (False,)):
                            if above:   # the rows change: every fact about the old population is void
                                nm = M("", u, m.kind, False, m.depth + 1, m.lin | {(kind, K)}, m.slots)
                                out.append((("baseline", i, K, kind, above), Stage(st.level, tuple(dataclasses.replace(x, facts=frozenset(), computed=frozenset()) for x in ms) + (nm,), st.steps + 2)))
                            else:
                                nm = M("", u, m.kind if kind == "gap" else None, False, m.depth + 1, m.lin | {(kind, K)}, m.slots,
                                       facts=frozenset({("mean0" if kind == "gap" else "mean1", K)}))
                                out.append((("baseline", i, K, kind, above), Stage(st.level, marked("AVG") + (nm,), st.steps + 2)))
                    if not m.add and not TY: self.untyped.add((st.sig(), ("share", i, K)))
                    if (m.add or not TY) and (not RS or (("share", K) not in m.lin and ("SUM", K) not in m.computed and not self.restates(m, "share", K))):
                        out.append((("share", i, K), Stage(st.level, marked("SUM") + (M("", "ratio", None, False, m.depth + 1, m.lin | {("share", K)}, m.slots, facts=frozenset({("sum1", K)})),), st.steps + 2)))
            if st.level[0] == "eg":
                for i, m in enumerate(ms):
                    if ("rank", "g") not in m.lin:
                        out.append((("rank", i), Stage(st.level, tuple(dataclasses.replace(x, lin=x.lin | {("rank", "g")}) if k == i else x for k, x in enumerate(ms)), st.steps + 1, rank=True)))
        return out

    def final_cell(self, st):
        return (max(m.depth for m in st.ms), st.steps + (1 if st.rank else 0))

    def reach(self, st):
        """EXACT set of (A, S) cells st can complete to under the rules and bounds (memoised on the type signature)."""
        k = st.sig()
        if k in self.memo: return self.memo[k]
        self.memo[k] = frozenset()
        r = set()
        for mv, nxt in self.moves(st):
            if mv[0] == "final": r.add(self.final_cell(st))
            else: r |= self.reach(nxt)
        self.memo[k] = frozenset(r); return self.memo[k]

    def reach_ops(self, st):
        """EXACT set of (cell, operations) pairs st can complete to: which operation kinds a program from st may use on its
        way to each cell (memoised on the type signature, like `reach`)."""
        k = ("ops",) + st.sig()
        if k in self.memo: return self.memo[k]
        self.memo[k] = frozenset()
        r = set()
        for mv, nxt in self.moves(st):
            if mv[0] == "final": r.add((self.final_cell(st), frozenset()))
            else:
                for c, ops in self.reach_ops(nxt): r.add((c, ops | {mv[0]}))
        self.memo[k] = frozenset(r); return self.memo[k]

    # STRUCTURAL REQUIREMENTS (2026-10-04) are decided by the ROUTE (first level and table), not by a move: the same definitions
    # as `cell_ops` -- grouped = first level eg or g; multi-table = eg, or g reached through a join; row ranking = a row route
    STRUCT = frozenset({"agg", "grouped", "multi-table", "row ranking"})

    def route_ok(self, kind, L, need):
        """Does a route (kind "row" or "stage", first level L) satisfy the structural requirements in `need`?"""
        sn = need & self.STRUCT
        if kind == "row": return not (need - {"row ranking"}) if "row ranking" in sn else not need
        if "row ranking" in sn: return False                 # "agg" (an aggregating stage route) is met by every stage route
        if "grouped" in sn and L[0] not in ("eg", "g"): return False
        if "multi-table" in sn and not (L[0] == "eg" or (L[0] == "g" and L[-1])): return False
        return True

    def feasible(self, cell, need):
        """Can SOME program in `cell` satisfy every requirement in `need` (operations and structure)? Exact, like `reach`."""
        for t in self.rec:
            if cell in self.row_final_cells(t) and self.route_ok("row", None, need): return True
            for L, lvl, opt in self.starts(t)[0]:
                if self.route_ok("stage", L, need) and self.can(self.start_stage(t, L, lvl, opt), cell, need - self.STRUCT): return True
        return False

    def can(self, st, target, need):
        """REQUIRED OPERATIONS (2026-10-02): can st still complete to `target` on a path that uses every operation kind in
        `need`? The same exact look-ahead as `reach`, over `reach_ops`. With nothing required it IS `target in reach(st)`."""
        if not need: return target in self.reach(st)
        return any(c == target and need <= ops for c, ops in self.reach_ops(st))

    def cell_ops(self):
        """{cell: set of what SOME program in the cell can use}: the operation kinds (baseline, share, rank, diff, ratio, agg)
        and the structures 'grouped' (the first step groups by a category) and 'multi-table' (the first step joins another
        table). Exact under the rules and bounds; what any one sampled program uses is a subset."""
        out = collections.defaultdict(set)
        for t in self.rec:
            for c in self.row_final_cells(t): out[c].add("row ranking")
            starts, _cls = self.starts(t)
            for L, lvl, opt in starts:
                extra = set()
                if L[0] in ("eg", "g"): extra.add("grouped")
                if L[0] == "eg" or (L[0] == "g" and L[-1]): extra.add("multi-table")
                for c, ops in self.reach_ops(self.start_stage(t, L, lvl, opt)): out[c] |= ops | extra | {"agg"}
        return {c: sorted(v) for c, v in out.items()}

    def start_stage(self, t, L, lvl, opt):
        return Stage(lvl, tuple(self._m_from(t, c, "q%d" % i) for i, c in enumerate(opt)), 1)

    def row_final_cells(self, t):
        return {(q["depth"], 1) for q in self.qs[t]}

    def reachable(self):
        """{cell: {"tables": set, "starts": n}} over every record table: EXACT under the rules and bounds (types only; the
        data checks can still empty a reachable cell -- that is the data-valid layer)."""
        out = collections.defaultdict(lambda: {"tables": set(), "routes": 0})
        for t in self.rec:
            for c in self.row_final_cells(t): out[c]["tables"].add(t); out[c]["routes"] += 1
            starts, _cls = self.starts(t)
            for L, lvl, opt in starts:
                for c in self.reach(self.start_stage(t, L, lvl, opt)): out[c]["tables"].add(t); out[c]["routes"] += 1
        return dict(out)


# ---------------------------------------------------------------------- concrete programs (SQL) and the sampler
class Program:
    """A program under construction: materialised stages (CTEs), the current builder, the typed stage, the trace."""

    def __init__(self, space, t):
        self.sp, self.t = space, t; self.ctes = []; self.trace = []; self.why = []; self.checks = []
        self.frm = self.where = ""; self.group = []; self.keys = []; self.sel = []; self.st = None; self.base = set(); self.n = 0
        self.order = ""

    def name(self): self.n += 1; return "s%d" % self.n

    def builder_sql(self, extra=(), where=True, order=True):
        sel = [("%s AS %s" % (e, a)) for e, a in self.keys + self.sel + list(extra)]
        s = "SELECT %s FROM %s" % (", ".join(sel), self.frm)
        if where and self.where: s += " WHERE " + self.where
        if self.group: s += " GROUP BY " + ", ".join(self.group)
        if order and self.order: s += " " + self.order
        return s

    def materialise(self):
        nm = self.name(); self.ctes.append((nm, self.builder_sql(order=False)))
        keys = [('"%s"."%s"' % (nm, a), a) for _e, a in self.keys]
        ms = [('"%s"."%s"' % (nm, a), a) for _e, a in self.sel]
        return nm, keys, ms

    def sql(self):
        w = ("WITH " + ", ".join('"%s" AS (%s)' % (n, s) for n, s in self.ctes) + " ") if self.ctes else ""
        return w + self.builder_sql()

    def snap(self, extra=(), where=True):
        """The CURRENT stage as a standalone query (for a check registered now), without ordering."""
        return list(self.ctes), self.builder_sql(extra=extra, where=where, order=False)


def _q(t, c): return '"%s"."%s"' % (t, c)


class Sampler:
    def __init__(self, space, rng, prefs=None):
        self.sp, self.rng = space, rng; self.prefs = prefs or {}; self.used = collections.Counter()
        self.exhausted = {}          # target cell -> used or exhausted branches (sampling without replacement)
        # VARIETY (a user control): each choice is discounted by how often it was already used -- the starting table, the
        # first aggregation level, and every prefix of the construction shape -- by a factor `variety` per earlier use
        # (1 = off). Choices still respect the target cell and the preferences; duplicates stay impossible.
        self.vpen = float(self.prefs.get("variety", 1.0)); self.seen_t = collections.Counter(); self.seen_lvl = collections.Counter()
        self.seen_shape = collections.Counter()
        # v3.2: DATA CHECKS AT THE MOVE. A move's data check runs when the move is taken; a move that fails it is a used-up
        # branch (never offered again for this target), so every finished program has passed every data check, and the
        # same check is never run twice (cached by its SQL). step_fail counts what was pruned, by reason.
        self.step_fail = collections.Counter(); self._step = {}
        self.data_checks = bool(self.prefs.get("data_checks", True))

    def step_ok(self, checks):
        """None when every check holds on the data, else the first failing reason (cached; time-limited)."""
        import time
        con = self.sp.S.con
        for c in checks:
            k = json.dumps(c, default=str)
            if k not in self._step:
                t0 = time.time(); con.set_progress_handler(lambda: 1 if time.time() - t0 > 20 else 0, 10000)
                try: self._step[k] = step_check(con, c)
                except Exception as e: self._step[k] = "error: %s" % str(e)[:80]
                finally: con.set_progress_handler(None, 0)
            if self._step[k]: return self._step[k]
        return None

    def w(self, key): return float(self.prefs.get(key, 1.0))

    def pick(self, items, weights):
        tot = sum(weights)
        if tot <= 0: return None
        x = self.rng.random() * tot
        for it, w in zip(items, weights):
            x -= w
            if x <= 0: return it
        return items[-1]

    def diversity(self, q):
        cap = self.prefs.get("repeat_penalty", 0.5)
        return cap ** self.used[(q["table"] if "table" in q else "", q["name"])]

    RESTART = object()

    def draw(self, target, need=frozenset()):
        """One program whose measured cell is `target` that this sampler has NEVER produced before, or None when no route
        reaches the cell or every program of the cell has been produced. Sampling WITHOUT REPLACEMENT over the choice tree:
        every choice (route, concrete quantity, move, finish) is a branch; a finished program marks its leaf used, and a
        branch with no unused completion left is marked exhausted when reached and never offered again. So a duplicate
        cannot be drawn, and no data check or review is ever spent on one. A restart after reaching an exhausted branch is
        cheap (no SQL runs)."""
        need = frozenset(need)
        ex = self.exhausted.setdefault((target, need) if need else target, set())   # a requirement has its own choice tree
        for _ in range(10000):
            if not self.prefs.get("dedupe", True): ex = set()      # ablation: sampling WITH replacement
            if () in ex: return None
            r = self._draw_once(target, ex, need)
            if r is not self.RESTART: return r
        return None

    def choose(self, ex, prefix, items, weights, key):
        """A weighted pick among the items whose branch (prefix + key) is not exhausted; marks prefix exhausted if none."""
        live = [(it, w) for it, w in zip(items, weights) if prefix + (key(it),) not in ex and w > 0]
        if not live: ex.add(prefix); return None
        it = self.pick([i for i, _w in live], [w for _i, w in live])
        return it

    def _draw_once(self, target, ex, need=frozenset()):
        # `need`: operation kinds the program must still use. Every route and move below must keep the target reachable
        # WITH them (Space.can), so a requirement is met where the choice is made, never by filtering finished programs.
        sp = self.sp; routes = []; path = ()
        for t in sp.rec:
            if "filter" in sp.extra and not sp.preds.get(t): continue          # FILTER: every program carries one condition
            if "filter" not in sp.extra and (target in sp.row_final_cells(t) or not self.prefs.get("lookahead", True)) and sp.route_ok("row", None, need): routes.append(("row", t, None, None, None))
            starts, cls = sp.starts(t)
            for L, lvl, opt in starts:
                st = sp.start_stage(t, L, lvl, opt)
                if sp.route_ok("stage", L, need) and (not self.prefs.get("lookahead", True) or sp.can(st, target, need - sp.STRUCT)): routes.append(("stage", t, L, lvl, opt))
        if not routes: ex.add(()); return None
        # A TABLE AND ITS FIRST LEVEL are the unit a preference or the variety discount speaks about, not each route: a
        # route's weight is divided among the live routes of its (table, level kind), so a table with many quantity
        # classes does not win by count alone
        live = [r for r in routes if path + (("route",) + r,) not in ex]
        grp = collections.Counter((r[1], r[2][0] if r[2] else "row") for r in live)
        wts = [self.w("table:" + r[1]) * (self.w("joins") if r[2] and r[2][0] in ("eg", "g") and r[2][-1] else 1.0) *
               (self.w("grouping") if r[2] and r[2][0] in ("eg", "g") else 1.0) *
               self.vpen ** (self.seen_t[r[1]] + self.seen_lvl[(r[1], r[2][0] if r[2] else "row")]) / max(1, grp[(r[1], r[2][0] if r[2] else "row")]) for r in routes]
        if "filter" in sp.extra:      # FILTER: a table is worth what its least-used condition kind is worth (variety on kinds)
            seen = getattr(self, "seen_kind", collections.Counter())
            wts = [w * max(self.vpen ** seen[c["kind"]] for c in sp.preds[r[1]]) for w, r in zip(wts, routes)]
        r = self.choose(ex, path, routes, wts, lambda r: ("route",) + r)
        if r is None: return self.RESTART
        kind, t, L, lvl, opt = r; path = path + (("route",) + r,)
        P = Program(sp, t); S = sp.S; P.level = L; need = need - sp.STRUCT     # the route met the structural requirements
        if "types" in sp.ablate and opt and any(c[0] != "count" and c[1] == "SUM" and not c[0][2] for c in opt): P.untyped = True
        if kind == "row":
            qs = [q for q in sp.qs[t] if q["depth"] == target[0] or not self.prefs.get("lookahead", True)]
            q = self.choose(ex, path, qs, [self.diversity(dict(q, table=t)) for q in qs], lambda q: ("q", q["sql"]))
            if q is None: return self.RESTART
            ex.add(path + (("q", q["sql"]),))                  # a row ranking is complete once its quantity is chosen
            self.seen_t[t] += 1; self.seen_lvl[(t, "row")] += 1; self.seen_shape[("row",)] += 1
            P.frm = Q(t); P.keys = [(_q(t, sp.key[t]), "k")]; P.sel = [(q["sql"], "m1")]; P.where = "%s IS NOT NULL" % q["sql"]
            P.order = "ORDER BY m1 DESC LIMIT 10"; P.st = Stage(("row",), (M(q["sql"], q["unit"], q["kind"], False, q["depth"], name=q["name"]),), 1)
            P.base = {(t, q["name"])}; P.why = q["why"] + ["rank %s rows by %s" % (t, q["name"])]; P.trace = [("rows", t, q["name"])]
            self.used[(t, q["name"])] += 1
            return P
        # first stage from the rows of t
        _starts, cls = sp.starts(t)
        ms, slot_qs = [], []
        if any(c[0] in ("cond", "ccount") for c in opt):
            r = self._cond_start(P, t, L, opt, cls, ex, path)
            if r is None: return self.RESTART
            ms, slot_qs, path = r
        for i, c in enumerate(opt if not ms else ()):
            if c[0] == "count":
                ms.append(sp._m_from(t, c, "n")); slot_qs.append(None); continue
            members = [q for q in cls[c[0]] if all(q["ops"].isdisjoint(p["ops"]) for p in slot_qs if p)]
            other = [o for o in opt[i + 1:] if o[0] != "count"]
            if other:   # the first of a pair: only quantities that have a disjoint partner in the second class
                members = [q for q in members if any(q is not b and q["ops"].isdisjoint(b["ops"]) for b in cls[other[0][0]])]
            if not members: raise AssertionError("reachability promised a pair the catalogue cannot build: %s" % (opt,))
            q = self.choose(ex, path, members, [self.diversity(dict(q, table=t)) for q in members], lambda q, i=i: ("q", i, q["sql"]))
            if q is None: return self.RESTART
            path = path + (("q", i, q["sql"]),); slot_qs.append(q)
            fn = c[1]; ms.append(M("%s(%s)" % (fn, q["sql"]), q["unit"], q["kind"], fn == "SUM", q["depth"], frozenset(), frozenset({"q%d" % i}),
                                   name="%s of %s" % ({"SUM": "total", "AVG": "average"}[fn], q["name"])))
            P.why += q["why"] + ["%s of %s per %s%s" % ({"SUM": "total", "AVG": "average"}[fn], q["name"], _lvlname(sp, L), " (additive)" if fn == "SUM" else "")]
        for q in slot_qs:
            if q: P.base.add((t, q["name"])); self.used[(t, q["name"])] += 1
        if L[0] == "e":
            P.frm = Q(t); P.keys = [(_q(t, L[1]), "e")]; P.group = [_q(t, L[1])]
        elif L[0] == "eg":
            _, cc, e, ek, gt, g, j = L
            P.frm = "%s JOIN %s ON %s = %s %s" % (Q(t), Q(e), _q(e, ek), _q(t, cc), " ".join(j)); P.keys = [(_q(t, cc), "e"), (_q(gt, g), "g")]; P.group = [_q(t, cc), _q(gt, g)]
        elif L[0] == "g":
            _, gt, g, j = L
            P.frm = "%s %s" % (Q(t), " ".join(j)); P.keys = [(_q(gt, g), "g")]; P.group = [_q(gt, g)]
        else:
            P.frm = Q(t); P.keys = []; P.group = []
        P.sel = [(m.expr, "m%d" % (i + 1)) for i, m in enumerate(ms)]
        if "filter" in sp.extra:
            path = self._filter(P, t, L, opt, ex, path)
            if path is None: return self.RESTART
        P.st = Stage(lvl, tuple(ms), 1); P.trace = [("agg", _lvlname(sp, L), tuple(m.name for m in ms))]
        if getattr(P, "cond", None) and self.data_checks:           # COND: the condition must matter on THIS stage's rows
            P.checks.append(("cond", P.snap(extra=[(u, "_u%d" % k) for k, u in P.cond_u]), [("m%d" % (k + 1), "_u%d" % k) for k, _u in P.cond_u]))
            why = self.step_ok(P.checks[-1:])
            if why: ex.add(path); self.step_fail[why] += 1; return self.RESTART
        # continue autoregressively: only moves that can still reach the target
        while True:
            opts = []
            LA = self.prefs.get("lookahead", True)
            for mv, nxt in sp.moves(P.st):
                if mv[0] == "final":
                    if (not LA or sp.final_cell(P.st) == target) and not need: opts.append((mv, nxt))
                elif not LA or sp.can(nxt, target, need - {mv[0]}): opts.append((mv, nxt))
            if not opts: ex.add(path); return self.RESTART
            shape = (L[0],) + tuple(m[0] for _k, m in [p for p in path if p[0] == "mv"])
            # THE KIND OF OPERATION is what a preference or the variety discount speaks about: a move's weight is divided
            # among the live moves of its kind, so a kind with many variants (comparisons: each measure, level, gap or
            # index, filtered or not) does not win by count alone
            kinds = collections.Counter(mv[0] for mv, _n in opts if path + (("mv", mv),) not in ex)
            o = self.choose(ex, path, opts, [self.w("op:" + mv[0]) * (self.w("op:above") if mv[0] == "baseline" and mv[4] else 1.0) *
                                             self.vpen ** self.seen_shape[shape + (mv[0],)] / max(1, kinds[mv[0]]) for mv, _n in opts],
                            lambda o: ("mv", o[0]))
            if o is None: return self.RESTART
            mv, nxt = o; path = path + (("mv", mv),); need = need - {mv[0]}
            if sp.untyped and (P.st.sig(), mv) in sp.untyped: P.untyped = True
            if mv[0] == "final":
                ex.add(path); P = self._final(P)
                if self.data_checks:
                    k = "rows:" + P.sql()
                    if k not in self._step:
                        try: self._step[k] = None if self.sp.S.con.execute(P.sql()).fetchone() else "empty answer"
                        except Exception as e: self._step[k] = "error: %s" % str(e)[:80]
                    if self._step[k]: self.step_fail[self._step[k]] += 1; return self.RESTART
                if getattr(P, "planted", None):
                    q = P.sql(); a, b = P.planted["first_A"], P.planted["first_B"]
                    if q.count(a) != 1: self.step_fail["the planted condition is not unique in the SQL"] += 1; return self.RESTART
                    P.planted["sql_B"] = q.replace(a, b)
                    self.seen_kind = getattr(self, "seen_kind", collections.Counter()); self.seen_kind[P.planted["kind"]] += 1
                full = shape + ("final",)
                self.seen_t[t] += 1; self.seen_lvl[(t, L[0])] += 1
                for i in range(1, len(full) + 1): self.seen_shape[full[:i]] += 1
                return P
            n0 = len(P.checks); self._apply(P, mv, nxt)
            if self.data_checks:
                why = self.step_ok(P.checks[n0:])
                if why: ex.add(path); self.step_fail[why] += 1; return self.RESTART

    def _filter(self, P, t, L, opt, ex, path):
        """FILTER (2026-10-16): one condition on the first stage's rows, chosen without replacement like every other choice, each
        kind weighted equally. Records on P the condition and the first stage of BOTH readings (P.planted), so the other
        reading is built where the choice is made: the finished SQL with the first stage's condition (or, for "outer", the
        first stage) replaced."""
        sp = self.sp
        cands = [c for c in sp.preds[t] if c["kind"] != "outer" or (L[0] == "e" and L[1] == c["entity"] and any(o[0] == "count" for o in opt))]
        kc = collections.Counter(c["kind"] for c in cands)
        seen = getattr(self, "seen_kind", collections.Counter())          # the variety discount, on the condition's kind
        c = self.choose(ex, path, cands, [self.vpen ** seen[c["kind"]] / kc[c["kind"]] for c in cands], lambda c: ("filter", c["kind"], c["text"]))
        if c is None: return None
        path = path + (("filter", c["kind"], c["text"]),)
        if c["kind"] == "outer":
            a = P.builder_sql(order=False); e, ek, cc = c["parent"], c["pkey"], c["entity"]
            sel = [(x.replace("COUNT(*)", "COUNT(%s)" % _q(t, sp.key[t])), al) for x, al in P.sel]
            b = "SELECT %s FROM %s LEFT JOIN %s ON %s = %s GROUP BY %s" % (", ".join("%s AS %s" % (x, al) for x, al in [(_q(e, ek), "e")] + sel), Q(e), Q(t), _q(t, cc), _q(e, ek), _q(e, ek))
            P.planted = dict(c, first_A=a, first_B=b)
        else:
            P.where = c["sql"]; P.planted = dict(c, first_A=c["sql"], first_B=c["alt"])
        P.why.append("condition on the %s rows: %s (%s)" % (t, c["text"], c["kind"]))
        return path

    def _cond_start(self, P, t, L, opt, cls, ex, path):
        """COND (2026-10-13): the measures of a conditional start. One condition (column = value) per program, chosen without
        replacement like every other choice; never on the column the stage groups by. A plain measure that follows a
        conditional one of the same class is the SAME quantity unconditioned (a conditional total and its total)."""
        sp = self.sp; gcols = {L[5]} if L[0] == "eg" else ({L[2]} if L[0] == "g" else set())
        conds = [c for c in sp.conds[t] if c[0] not in gcols]
        cnd = self.choose(ex, path, conds, [1.0] * len(conds), lambda c: ("cond", c[0], c[1]))
        if cnd is None: return None
        path = path + (("cond", cnd[0], cnd[1]),); col, val, share = cnd
        lit = "'%s'" % str(val).replace("'", "''") if isinstance(val, str) else str(val)
        csql = "%s = %s" % (_q(t, col), lit); ctext = "%s.%s is %s" % (t, col, lit)
        ms, slot_qs, last, cond_u = [], [], None, []
        for i, c in enumerate(opt):
            if c[0] == "ccount":
                ms.append(M("COUNT(*) FILTER (WHERE %s)" % csql, "count of %s records" % t, True, True, 0, frozenset(), frozenset({"nc"}),
                            name="number of %s records where %s" % (t, ctext), count_of=t)); slot_qs.append(None); cond_u.append((i, "COUNT(*)")); continue
            if c[0] == "count":
                ms.append(sp._m_from(t, c, "n")); slot_qs.append(None); continue
            if c[0] == "cond":
                _c, k, fn = c; members = list(cls[k])
                q = self.choose(ex, path, members, [self.diversity(dict(q, table=t)) for q in members], lambda q, i=i: ("q", i, q["sql"]))
                if q is None: return None
                path = path + (("q", i, q["sql"]),); slot_qs.append(q); last = (k, fn, q)
                ms.append(M("%s(%s) FILTER (WHERE %s)" % (fn, q["sql"], csql), q["unit"], q["kind"], fn == "SUM", q["depth"], frozenset(), frozenset({"q%dc" % i}),
                            name="%s of %s where %s" % ({"SUM": "total", "AVG": "average"}[fn], q["name"], ctext)))
                cond_u.append((i, "%s(%s)" % (fn, q["sql"])))
                P.why += q["why"] + ["%s of %s over the %s rows where %s (%.0f%% of them)" % ({"SUM": "total", "AVG": "average"}[fn], q["name"], t, ctext, 100 * share)]
                continue
            k, fn = c
            if not (last and last[0] == k and last[1] == fn): return None      # starts() only pairs a conditional with its own class
            q = last[2]; slot_qs.append(q)
            ms.append(M("%s(%s)" % (fn, q["sql"]), q["unit"], q["kind"], fn == "SUM", q["depth"], frozenset(), frozenset({"q%d" % i}),
                        name="%s of %s" % ({"SUM": "total", "AVG": "average"}[fn], q["name"])))
        P.cond = (col, val, share); P.cond_u = cond_u
        return ms, slot_qs, path                        # base and use counts are recorded by the caller, as for every start

    def _apply(self, P, mv, nxt):
        sp = self.sp; st = P.st; ms = list(st.ms)
        if mv[0] in ("diff", "ratio"):
            _, i, j = mv; a, b = P.sel[i][0], P.sel[j][0]; A, B = ms[i], ms[j]
            e = "(%s - %s)" % (a, b) if mv[0] == "diff" else "(CAST(%s AS REAL) / %s)" % (a, b)
            nm = "%s %s %s" % (A.name, "minus" if mv[0] == "diff" else "relative to", B.name)
            new = dataclasses.replace(nxt.ms[-1], expr=e, name=nm)
            P.sel.append((e, "m%d" % (len(P.sel) + 1))); P.st = dataclasses.replace(nxt, ms=tuple(ms) + (new,))
            P.checks.append(("derived", "m%d" % len(P.sel), [P.sel[i][1], P.sel[j][1]], P.snap(), P.snap(extra=[(b, "_den")]) if mv[0] == "ratio" else None, None))
            P.why.append("%s: both in %s, of the same kind, from different quantities" % (nm, A.unit)); P.trace.append((mv[0], A.name, B.name)); return
        if mv[0] == "agg":
            _, L2, fns, keep = mv; src, keys, cols = P.materialise()
            new_keys = [(k, a) for k, a in keys if (a == "g" and L2[0] == "g")]
            P.frm = Q(src); P.where = ""; P.keys = new_keys; P.group = [k for k, _a in new_keys]
            P.sel = [("%s(%s)" % (f, cols[i][0]), "m%d" % (n + 1)) for n, (i, f) in enumerate(zip(keep, fns))]
            P.st = dataclasses.replace(nxt, ms=tuple(dataclasses.replace(m2, expr=P.sel[n][0], name="%s of %s" % ({"SUM": "total", "AVG": "average"}[f], st.ms[i].name))
                                                    for n, (i, m2, f) in enumerate(zip(keep, nxt.ms, fns))))
            if st.level[0] == "eg" and L2[0] == "g": P.checks.append(("members", (list(P.ctes), 'SELECT COUNT(*), COUNT(DISTINCT "g") FROM "%s"' % src)))
            P.why.append("coarsen to %s: %s" % (L2[0], ", ".join("%s (%s)" % (f, "additive" if f == "SUM" else "averaged") for f in fns))); P.trace.append(("agg", L2[0], fns)); return
        src, keys, cols = P.materialise()
        if mv[0] in ("baseline", "share"):
            i = mv[1]; K = mv[2]; b = P.name(); col = cols[i][0]
            kc = [(k, a) for k, a in keys if a == "g"] if K[0] == "g" else []
            agg = "AVG" if mv[0] == "baseline" else "SUM"
            P.ctes.append((b, "SELECT %s%s(%s) AS v FROM %s%s" % ("".join("%s AS %s, " % (k, a) for k, a in kc), agg, col, Q(src), (" GROUP BY " + ", ".join(k for k, _a in kc)) if kc else "")))
            on = " AND ".join('%s = "%s"."%s"' % (k, b, a) for k, a in kc) or '"%s"."v" IS NOT NULL' % b
            ref = '"%s"."v"' % b
            if mv[0] == "baseline" and mv[3] == "gap": e, word = "(%s - %s)" % (col, ref), "gap to the %s average" % K[0]
            elif mv[0] == "baseline": e, word = "(CAST(%s AS REAL) / %s)" % (col, ref), "index against the %s average" % K[0]
            else: e, word = "(CAST(%s AS REAL) / %s)" % (col, ref), "share of the %s total" % K[0]
            # v3.3: the reference (the K average, or the K total) must be taken over >= 2 rows, and at K = group not every group
            # may be a single row -- otherwise every comparison is trivially 0 (gap), 1 (index) or 1 (share), whatever the data
            P.checks.append(("reference", (list(P.ctes), 'SELECT COUNT(*), %s FROM "%s"' % ('COUNT(DISTINCT "g")' if kc else "1", src)), bool(kc)))
            P.frm = "%s JOIN %s ON %s" % (Q(src), Q(b), on); P.keys = keys; P.group = []
            P.sel = cols + [(e, "m%d" % (len(cols) + 1))]
            P.where = ("%s > %s" % (col, ref)) if mv[0] == "baseline" and mv[4] else ""
            new = dataclasses.replace(nxt.ms[-1], expr=e, name="%s: %s" % (st.ms[i].name, word))
            P.st = dataclasses.replace(nxt, ms=tuple(dataclasses.replace(m2, expr=c, name=m.name) for m, m2, (c, _a) in zip(st.ms, nxt.ms, cols)) + (new,))
            P.checks.append(("derived", "m%d" % len(P.sel), [cols[i][1]], P.snap(), None if (mv[0] == "baseline" and mv[3] == "gap") else P.snap(extra=[(ref, "_den")], where=False),
                             P.snap(where=False) if P.where else None))
            P.why.append("%s of %s (%s level)" % (word, st.ms[i].name, K[0])); P.trace.append((mv[0], K[0]) + tuple(x for x in mv[3:])); return
        if mv[0] == "rank":
            i = mv[1]; col = cols[i][0]; gk = [k for k, a in keys if a == "g"][0]
            P.frm = Q(src); P.keys = keys; P.group = []; P.where = ""
            P.sel = cols + [("RANK() OVER (PARTITION BY %s ORDER BY %s DESC)" % (gk, col), "r")]
            P.checks.append(("rank", P.snap()))          # v3.3: "top 3 within each group" must drop some rows (groups of <= 3 keep all)
            P.st = dataclasses.replace(nxt, ms=tuple(dataclasses.replace(m, expr=c) for m, (c, _a) in zip(nxt.ms, cols)))
            P.why.append("rank within the group by %s, keep the top 3" % st.ms[i].name); P.trace.append(("rank",)); return
        raise ValueError(mv)

    def _final(self, P):
        if P.st.rank:
            src, keys, cols = P.materialise()
            P.frm = Q(src); P.keys = keys; P.sel = cols; P.group = []; P.where = '"%s"."r" <= 3' % src; P.order = ""
        elif P.st.level[0] in ("e", "eg"):
            P.order = "ORDER BY %s DESC LIMIT 10" % P.sel[-1][1]
        return P


def _lvlname(sp, L):
    return {"e": lambda: "%s (by %s)" % (L[2], L[1]), "eg": lambda: "%s within %s.%s" % (L[2], L[4], L[5]), "g": lambda: "%s.%s" % (L[1], L[2]), "all": lambda: "all"}[L[0]]()


# ---------------------------------------------------------------------- data checks (the data-valid layer)
def step_check(con, c):
    """One move's data check (a P.checks entry) on the data: None when it holds, else the reason. SMALL POPULATIONS (v3.3
    audit): a derived value on ONE row is legitimate (an overall total, a ratio of two summary values) and is not refused for
    being "constant"; a COMPARISON is refused when its reference aggregate covers < 2 rows or only single-row groups (the
    "reference" check), a top-3 cut when it keeps every row (the "rank" check). The "members" check bounds the AVERAGE group
    size (>= 2), so a grouped aggregation may still contain some single-entity groups (not trivial: their value is data). The sampler runs it when
    the move is TAKEN (so a finished program is data-valid by construction); check() runs every one again as a receipt."""
    run = lambda snap, tail: con.execute(("WITH " + ", ".join('"%s" AS (%s)' % (n, b) for n, b in snap[0]) + ", " if snap[0] else "WITH ") + "_c AS (%s) %s" % (snap[1], tail)).fetchone()
    if c[0] == "derived":
        _, new, ops, body, den, nowhere = c
        parts = ["COUNT(*)", "COUNT(DISTINCT %s)" % new] + ["SUM(CASE WHEN %s IS NOT %s THEN 1 ELSE 0 END)" % (new, o) for o in ops]
        r = run(body, "SELECT %s FROM _c" % ", ".join(parts))
        if r[0] >= 2 and (r[1] or 0) < 2: return "derived measure is constant"
        if any(not (x or 0) for x in r[2:]): return "derived measure restates an operand"
        if den:
            d = run(den, "SELECT MIN(_den) FROM _c")[0]
            if d is None or d <= 0: return "denominator not positive"
        if nowhere:
            a = run(nowhere, "SELECT COUNT(*) FROM _c")[0]
            if not (1 <= r[0] < a): return "filter keeps all or none"
    elif c[0] == "reference":
        snap, grouped = c[1], c[2]
        r = con.execute(("WITH " + ", ".join('"%s" AS (%s)' % (n, b) for n, b in snap[0]) + " ") + snap[1]).fetchone()
        if (r[0] or 0) < 2: return "comparison against an aggregate of fewer than 2 rows (trivial)"
        if grouped and r[0] == r[1]: return "comparison within groups that are all single rows (trivial)"
    elif c[0] == "rank":
        r = run(c[1], "SELECT COUNT(*), SUM(CASE WHEN r <= 3 THEN 1 ELSE 0 END) FROM _c")
        if r[0] and r[1] == r[0]: return "top 3 within each group keeps every row (trivial)"
    elif c[0] == "cond":
        snap, pairs = c[1], c[2]
        for m, u in pairs:
            r = run(snap, "SELECT COUNT(*), SUM(%s IS NOT NULL), SUM(%s IS NOT %s) FROM _c" % (m, m, u))
            if not r[1]: return "conditional measure is missing on every row"
            if not r[2]: return "the condition changes nothing on this stage"
    elif c[0] == "members":
        snap, q = c[1]
        r = con.execute(("WITH " + ", ".join('"%s" AS (%s)' % (n, b) for n, b in snap) + " ") + q).fetchone()
        if r[1] and r[0] < 2 * r[1]: return "groups of fewer than 2 entities"
    return None


def check(sp, P, ms=20000, con=None):
    """(ok, why): no step recomputes an existing aggregate (specbridge.pd.structures.integrity); the answer runs and has rows; every derived measure takes >= 2 values and differs from its operands on
    some row; every denominator is positive; every filter keeps some rows but not all; every group has >= 2 members on
    average. All on the data, stage by stage."""
    import time
    con = con or sp.S.con; sql = P.sql()
    t0 = time.time(); con.set_progress_handler(lambda: 1 if (time.time() - t0) * 1000 > ms else 0, 10000)
    try:
        from specbridge.pd.structures.integrity import recomputed
        from specbridge.pd.structures.algebra import lift
        rc = recomputed(lift(sql, con))                  # receipt of the v3.2 rule, read off the SQL: must never fire
        if rc: return False, "a step recomputes an existing aggregate (%s in %s)" % (rc[0]["aggregate"], rc[0]["stage"])
        rows = con.execute(sql).fetchall()
        if not rows: return False, "empty answer"
        for c in P.checks:
            why = step_check(con, c)
            if why: return False, why
        return True, "%d rows" % len(rows)
    except Exception as e:
        return False, "error: %s" % str(e)[:80]
    finally:
        con.set_progress_handler(None, 0)


# ---------------------------------------------------------------------- checks in parallel, cached, deterministic
BATCH = 8          # fixed: the sampler draws this many before checking, so the output does not depend on the worker count
_LOCAL = __import__("threading").local()


def _con(sp):
    import sqlite3
    if getattr(_LOCAL, "db", None) != sp.db:
        from specbridge.pd.corpora import found
        _LOCAL.con = sqlite3.connect("file:%s/%s.sqlite?mode=ro" % (found(sp.db), sp.db), uri=True, check_same_thread=False); _LOCAL.db = sp.db
    return _LOCAL.con


def _key(sp, P):
    import hashlib, os
    if not hasattr(sp, "_ver"):
        h = hashlib.sha256(open(__file__, "rb").read() + open("catalogues/%s.json" % sp.db, "rb").read()); sp._ver = h.hexdigest()[:12]
    return hashlib.sha256((sp._ver + "\0" + P.sql() + "\0" + json.dumps(P.checks, default=str)).encode()).hexdigest()[:24]


def check_many(sp, Ps, workers=6, cache=None):
    """check() for each program, in input order: cached on disk by (compose code, catalogue, SQL, checks), the rest run on
    `workers` threads with one read-only connection each (SQLite runs queries outside the GIL)."""
    import concurrent.futures as cf, os
    d = "%s/%s" % (cache or os.environ.get("COMPOSE_CHECK_CACHE", "out/cache/compose_check"), sp.db); os.makedirs(d, exist_ok=True)
    def one(P):
        f = "%s/%s.json" % (d, _key(sp, P))
        if os.path.exists(f): return tuple(json.load(open(f)))
        r = check(sp, P, con=_con(sp)); json.dump(list(r), open(f, "w")); return r
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, Ps))
