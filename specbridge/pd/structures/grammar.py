"""specbridge.pd.structures.grammar — THE LAW AS A TREE, NOT AS FOURTEEN BITS, WITH A DIAL FOR DIFFICULTY.

THE DISTRIBUTIONS, DEFINED ONCE.

    P            the fitted law: a program is a sequence of decisions, and P(x) = prod_t P(x_t | ctx_t),
                 each factor a Dirichlet-smoothed count in `child`, `size` or `member`.
    pi_D         the projection onto a database D: at each decision the options D cannot host are
                 removed and the rest renormalised, P_D(x_t | ctx) = P(x_t | ctx) / Z_t, with
                 Z_t = sum over the allowed options. `_pick` is pi_D applied to one decision.
    P_D          = pi_D(P): the distribution `pd.bind.realise` draws from, when nothing but D masks.
    KL(P_D || P) = E_{P_D}[ sum_t -log Z_t ] -- since log P_D(x) - log P(x) = -sum_t log Z_t for every x
                 in the support. It is the mean over a corpus of the recorded `-log Z`s, which is why
                 every mask records its Z. It is a statement about D: the part of the source's habits this
                 database cannot host.
    the receipt  refit a law on the realised corpus and measure it against P per decision (`divergence`).
                 Whatever that shows beyond the recorded projection is a restriction that is OURS, not
                 D's, and `pd.projection` reports it by context and by cause. It should read zero.

WHY THIS REPLACES `pd.law`'s COINS. The old law summarised a program as fourteen presence bits. A bit
cannot see magnitude, and magnitude is where the difficulty is: measured over R against our own corpus,

    max arithmetic depth   R 3.08 (max 8)     the 14-bit sampler 0.58 (max 1, never more)
    distinct columns       R 13.08 (max 51)   5.21
    joins                  R 2.17             0.86

`Arith` as a bit reads 0.56 against P's 0.92 -- a mild-looking gap over a quantity that is 0.58 against
3.08. Close the bit perfectly and the corpus still emits depth-one expressions forever while the metric
reports success. Worse, `pd.law.cost` and `pd.gaps` are both defined on those same bits, so no instrument
we had could report it. A divergence computed on the fitting features cannot detect its own blindness.

WHY 108 PROGRAMS ARE ENOUGH, though they were not enough for a joint over compositions. A grammar is not
fitted on programs; it is fitted on EXPANSIONS -- 26,468 of them, 72 nodes per program, over 65 contexts
with a median of 84 observations and none below three. Better evidenced than the 18 parameters it
replaces. The estimability argument that produced the bits counted the wrong unit.

WHAT IT CONDITIONS ON. `(parent type, slot, how deep the arithmetic already is)`. The depth belongs in
the context because the continuation rate DECAYS -- P(Arith.l -> Arith) is 0.59 at depth 1, 0.44 at 2,
0.24 at 3 -- so one marginal rate (0.375) is subcritical on average while being supercritical at the
first level. Fitted flat, the grammar reaches R's mean depth by emitting monsters: max depth 28 and 136
arithmetic nodes against R's 8 and 82. Conditioned, its maximum is 10 against R's 8. "Start eagerly,
then taper" is not something a context-free rate can say.

THE DIAL. `lam` exponentially tilts every choice towards continuing rather than stopping:

    w(child) = count(child) * exp(lam)   for a child that extends the tree, count(child) for stopping

AND lam = 0 IS NOT FAITHFUL TO R, which was the first thing this measured and the opposite of what I
expected. The maximum-likelihood grammar UNDERSHOOTS what it was fitted on:

                    R        lam 0      lam 0.8
      columns    23.48      11.86        23.96
      constants  15.97       7.62        15.03
      arith      10.53       5.04         9.63
      aggregates  1.48       0.72         1.35
      depth       3.08       1.98         2.67
      joins       2.17       2.27         3.40   <- the one it overshoots

That is expected once stated: the MLE fits LOCAL rates and a tree's size is a global property, and the
Dirichlet smoothing adds mass to stopping at all 65 contexts at once. So lam is not only a difficulty
knob, it is the CALIBRATION, and it has to be fitted against out-of-sample statistics the way any
generative model is checked -- not assumed to be zero because zero is the likelihood optimum. On this
fit that is lam ~ 0.8, matching six of nine statistics closely; `Join` overshoots because one scalar
tilts every production equally, and a per-production calibration is the obvious refinement.

Beyond calibration, positive lam walks into P's own long tail -- the structures R writes rarely --
without inventing any structure R never wrote, because a production with no observations still has no
weight. That is the difference between sampling hard and fabricating hard, and it is why the dial is
safe: it can only reweight R's own alphabet, never extend it.

    python -m specbridge.pd.structures.grammar [lam ...]
"""
from __future__ import annotations
from specbridge.pd.structures.algebra import _find
import functools
import collections, json, math, random, sqlite3, sys
from dataclasses import is_dataclass, fields

import specbridge.pd.structures.algebra as _A

# Every dataclass in the algebra, and its slots. Read off the module so a new node type cannot be
# forgotten here -- the grammar's alphabet IS the algebra's, which is what makes the feature set closed.
FIELDS = {nm: [f.name for f in fields(o)] for nm in dir(_A)
          for o in [getattr(_A, nm)] if is_dataclass(o)}

STOP = "-"          # a slot that holds no node: None, a string, a number
# HOW MANY LEVELS OF ARITHMETIC DEPTH THE CONTEXT TELLS APART. Pooled past 3, every level below the third
# continued at one rate (24%), a geometric tail R does not have: R's deepest tree is 8 and its mean 3.3, and
# the pooled fit drew 3.9 with a tail past 9. Six levels are told apart; a context with few draws is
# Dirichlet-smoothed like every other.
DCAP = 6
ICAP = 8           # list positions past the eighth child share the eighth's counts
CAP = 40            # nothing in R is near this; it exists so a bad fit cannot hang the sampler


def adepth(t, d):
    """How deep the arithmetic is BELOW a node of type `t` sitting at depth `d`.

    One definition, called from both the fitting and the sampling side. Keyed separately they disagree
    by one, the lookup reads an empty bucket, and the sampler silently stops recursing -- which cost two
    invalid measurements before it was noticed.
    """
    return d + 1 if t == "Arith" else 0


class Grammar:
    """P over trees: which child fills a slot, how many, and which member a terminal takes."""

    def __init__(self):
        self.child = collections.defaultdict(collections.Counter)   # (parent, slot, depth) -> type
        self.size = collections.defaultdict(collections.Counter)    # (parent, slot, depth) -> item count (measured, never drawn)
        # A LIST IS GROWN ONE CHILD AT A TIME, AND STOPPED. `more[(parent, slot, i)]` counts, for a list with i
        # children already placed, how often R placed another and how often it stopped. A count is never a
        # decision: it is what the stops add up to, and D masks "more" and "stop" after every child.
        self.more = collections.defaultdict(collections.Counter)    # (parent, slot, placed) -> more | stop
        self.member = collections.defaultdict(collections.Counter)  # (type, field) -> literal
        self.n = 0

    # ---------------------------------------------------------------- fitting
    def observe(self, x, par="ROOT", slot="root", d=0, typer=None):
        """`d` is the arithmetic depth AT THE PARENT -- the same thing the sampler knows when it chooses.

        `typer` (`specbridge.pd.structures.meaning.Typer`) is what makes the fit ABSTRACT WHERE IT MATTERS. A column of R is not
        recorded -- that is someone else's database -- and neither is the source's word for it. Under
        arithmetic and inside an aggregate a leaf is recorded by its CLASS (`specbridge.pd.structures.meaning.klass`): an amount,
        a ratio, a time -- what the operator needs of it -- and a constant as one leaf, its value kept
        under the operator (`("Const", "value", op)`) for the fill to draw from. So P says "an amount over
        an amount, times a constant", and a target fills that with its own columns and R's number.
        """
        if isinstance(x, (list, tuple)):
            # A SORT KEY IS A PAIR (expression, direction), NOT A LIST OF TWO CHILDREN. Read as a list, every
            # key added a "size 2" to the order slot and its direction was counted as an absent child --
            # so the fitted law said R sorts 93 times by two things and 83 times by nothing, and the
            # direction, which R chooses `desc` 69 times in 83, was not in the law at all. The sampler
            # then had to make it up, which is the one thing a fitted law exists to prevent.
            if slot == "order" and len(x) == 2 and x[1] in ("asc", "desc"):
                self.member[("Order", "dir")][x[1]] += 1
                self.observe(x[0], par, slot, d, typer)
                return
            # AN ITEM THAT IS A PAIR IS ONE ITEM. A select item is (expression, alias), a step is (name,
            # program), a CASE arm is (condition, value): read as lists of two, every one added a "size 2"
            # to its slot and its alias or name counted as an absent child -- so the law said every
            # select has two items and half of them are nothing, and that a program has two steps 154
            # times. The pair's nodes are the children; its string is syntax.
            if x and all(isinstance(y, tuple) and len(y) == 2 for y in x):
                self.size[(par, slot, min(d, DCAP))][len(x)] += 1
                self._stops(par, slot, len(x))
                for y in x:
                    if slot == "order": self.observe(y, par, slot, d, typer)     # a sort key: its direction is a member
                    else:
                        for z in y:
                            if is_dataclass(z): self.observe(z, par, slot, d, typer)
                return
            self.size[(par, slot, min(d, DCAP))][len(x)] += 1
            self._stops(par, slot, len(x))
            for y in x: self.observe(y, par, slot, d, typer)
            return
        if not is_dataclass(x):
            # A BARE NUMBER IN A SLOT IS A CONSTANT. `Program.limit` is lifted as an int, so R's 26 limits
            # were counted as 26 absences and the law could never draw one.
            if slot == "limit" and isinstance(x, (int, float)) and not isinstance(x, bool):
                self.child[(par, slot, min(d, DCAP))]["Const"] += 1
                self.member[("Limit", "n")][int(x)] += 1
                return
            self.child[(par, slot, min(d, DCAP))][STOP] += 1
            return
        t = type(x).__name__
        if typer is not None and t == "Func" and x.args and x.name.upper() == "ROUND" and par == "Program":
            # ROUNDING IS PRESENTATION. `ROUND(AVG(x), 2)` in a select is the average; read through here as
            # under arithmetic, or the law asks the binder for a "Func" that is nothing but the aggregate.
            self.observe(x.args[0], par, slot, d, typer); return
        if typer is not None and t == "Cast" and par == "Program":
            # ...AND SO IS A CAST: `CAST(x AS REAL)` listed is x listed (47 of R's select items).
            self.observe(x.expr, par, slot, d, typer); return
        if typer is not None and (str(par).startswith("Arith") or par == "Agg"):
            # PLUMBING IS NOT A FEATURE. `CAST(a AS REAL) / b`, `a / NULLIF(b, 0)`, `COALESCE(a, 0)` and
            # `JULIANDAY(d)` are how SQL is made to compute `a / b` and `d`; the fit reads through them to
            # the thing they carry, so P asks for the quantity and the binder supplies the plumbing.
            from specbridge.pd.structures.meaning import _PASS_FN, _DATE_FN
            if t == "Cast":
                self.observe(x.expr, par, slot, d, typer); return
            if t == "Func" and x.args and (x.name.upper() in _PASS_FN or
                                           (x.name.upper() in _DATE_FN and type(x.args[0]).__name__ == "Col")):
                self.observe(x.args[0], par, slot, d, typer); return
        self.child[(par, slot, min(d, DCAP))][typed(x, par, typer) if typer is not None else t] += 1
        if t == "Arith" and typer is not None:
            # THE RIGHT CHILD IS DRAWN KNOWING THE LEFT. Siblings are not independent in R: a constant never
            # sits beside a constant (0 of 245 nodes), and drawn independently they did in a quarter of
            # all trees. So the right slot is recorded as `rc` (the left is a constant) or `rq` (a
            # quantity) -- one more bit of context, fitted like the rest.
            from specbridge.pd.structures.meaning import _PASS_FN, _DATE_FN
            def carried(v):
                while True:
                    tv = type(v).__name__
                    if tv == "Cast": v = v.expr; continue
                    if tv == "Func" and v.args and (v.name.upper() in _PASS_FN or v.name.upper() in _DATE_FN): v = v.args[0]; continue
                    return v
            # ...and whether it continues: R's trees are chains far more than bushes, so a right child
            # beside an arithmetic left (`ra`) stops more often than one beside a column (`rq`).
            lt = type(carried(x.l)).__name__
            rslot = {"Const": "rc", "Arith": "ra"}.get(lt, "rq")
            # ...AND WHAT THE LEFT IS, NOT JUST WHICH SORT: siblings under + and - share a kind in 92% of R's
            # nodes and a sum nests to the left in 99%; drawn knowing only "the left is a column" or "a tree",
            # the right matched the kind 40% of the time and nested left 33%. The slot carries the left
            # leaf's kind or the left tree's operator; `_look` pools the finer slots where R is thin.
            if rslot == "ra": rslot = "ra:" + carried(x.l).op
            elif rslot == "rq" and typer is not None:
                lk = typed(carried(x.l), "Arith", typer)
                if lk.startswith("Col:"): rslot = "rq:" + lk[4:]           # the left leaf's class
            self.member[("Arith", "op")][x.op] += 1
            # THE OPERATOR OF A CHILD TREE IS DRAWN KNOWING WHERE IT SITS: the right child of a + is a weighted
            # term (* or /) and never another +, which is why R's sums nest to the left (99%) and P's did not
            # (35%). Recorded under the parent's context; the sampler falls back to the global table.
            self.member[("Arith", "op", par, slot)][x.op] += 1
            # A CHILD IS DRAWN KNOWING ITS OPERATOR. A constant's role is defined by the operator above it (a
            # normaliser divides, an offset adds), so a child drawn without the operator put a normaliser under
            # a minus in 92% of depth-5 draws -- shapes R cannot write, unfillable by construction. The context
            # carries the operator; `_look` falls back to the operator-less sum where R is thin.
            self.observe(x.l, "Arith:" + x.op, "l", adepth(t, d), typer)
            self.observe(x.r, "Arith:" + x.op, rslot, adepth(t, d), typer)
            # A CONSTANT IS A NODE OF THE TREE AND ITS VALUE IS LANGUAGE: 0.4 of this, over 1000, plus 1 -- how a
            # question is asked, like a limit of 3. The value is kept by the operator above it, and the fill
            # draws one there; the question states it, and that is all a constant has to mean.
            for side in ("l", "r"):
                v = getattr(x, side)
                if type(v).__name__ == "Const" and isinstance(v.value, (int, float)) and not isinstance(v.value, bool):
                    self.member[("Const", "value", x.op)][float(v.value)] += 1
            self.n += (par == "ROOT")
            return
        # A STEP IS A PROGRAM WITH ITS OWN CONTEXT. A program inside a `ctes` slot records its decisions under
        # "Step" rather than "Program": what R groups, filters and cuts in a step differs from what it does in an
        # outer program. The sampler draws a step by the same door as any program, under this context, and
        # `_look` backs off to the outer's counts where R's steps are thin.
        tpar = "Step" if (t == "Program" and slot == "ctes") else t
        for f in FIELDS[t]:
            v = getattr(x, f, None)
            # A GROUP KEY IN THE SELECT IS THE GROUPING'S, NOT THE SELECT'S. `SELECT county, AVG(x) ... GROUP BY
            # county` lists the key because SQL makes it; the choice was made in the group slot, and counting
            # it here too charged the binder ~1.2 nats per item for "not drawing a column" after it had placed
            # the keys -- 6 of 9.7 nats of the whole projection. The select slot is fitted on what is chosen
            # there: everything but the keys.
            slot = f
            if t == "Program" and f == "select" and x.group:
                keys = list(x.group)
                v = [it for it in v if not (isinstance(it, tuple) and any(it[0] == k for k in keys))]
                slot = "select_g"          # ...and a grouped query's items are their own distribution: aggregates
            # A MEMBER IS PART OF THE QUERY LANGUAGE. A BINDING IS PART OF SOMEONE ELSE'S DATABASE.
            #
            # `op` and `fn` are the language -- `/`, `AVG`, `ROUND` -- and carrying their frequencies is
            # the point of fitting a law. `Col.name` is not: it is a column of LiveSQLBench's schemas, and
            # recording it made the grammar memorise `opmaintregistry` and `watereqref`, which mean
            # nothing on any target. A structure grown from this law arrived with someone else's columns
            # already in it, so it could not be a structure at all -- only a copy.
            #
            # `Col` is left a HOLE. That is what makes the grown tree a SHAPE, which a binder then fills
            # from what this database can back -- the projection onto A_D, done where the choice is made.
            # `Func.name` IS language too -- ROUND, JULIANDAY, STRFTIME -- so the exclusion is `Col.name`
            # specifically, not the field called "name".
            if (f in ("op", "fn") or (f == "name" and t != "Col")) and isinstance(v, str) and v:
                self.member[(t, f)][v] += 1
            self.observe(v, tpar, slot, adepth(t, d), typer)
        self.n += (par == "ROOT")

    def events(self):
        return sum(sum(c.values()) for c in self.child.values())

    # ---------------------------------------------------------------- sampling
    def _stops(self, par, slot, n):
        """a list of n children: "more" after each of the first n, "stop" after the n-th"""
        for i in range(n): self.more[(par, slot, min(i, ICAP))]["more"] += 1
        self.more[(par, slot, min(n, ICAP))]["stop"] += 1

    def _more(self, par, slot, i):
        """the more/stop counts after i children -- at this position, else the nearest earlier position R
        reached, else the outer program's for a step"""
        for ii in range(min(i, ICAP), -1, -1):
            c = self.more.get((par, slot, ii))
            if c: return c
        if par == "Step": return self._more("Program", slot, i)
        return collections.Counter({"stop": 1})

    def another(self, par, slot, i, rng, lam=0.0, cost=None, can_more=True, can_stop=True, ours=False):
        """ONE MORE CHILD, OR STOP -- P's draw after i children, masked by D: `can_more` when one more can stand
        on the program as it is, `can_stop` when the list may end here (a program with no join stands; a
        select with one item is a question). Both masked leaves STOP with everything charged. Returns True
        for another child. `ours` marks a "more" we do not build, charged to us."""
        c = self._more(par, slot, i)
        k = self._pick({"more": c.get("more", 0), "stop": c.get("stop", 0)}, rng, lam, ctx=(par, slot, "more", min(i, ICAP)), cost=cost,
                       allow=lambda _c, x: (x == "more" and can_more) or (x == "stop" and can_stop),
                       ours={"more"} if ours else ())
        return k == "more"

    def _look(self, tbl, par, slot, d):
        """The counts for a context -- at this depth, else the nearest shallower depth R reached, else the
        depthless entry. A sparse deep context (the right child beside a constant, five levels down) is
        answered by the level above it rather than by nothing."""
        for dd in range(min(d, DCAP), -1, -1):
            c = tbl.get((par, slot, dd))
            if c: return c
        if ":" in str(slot):                                 # thin for this left sibling: every left sibling of the sort
            return self._look(tbl, par, slot.split(":")[0], d)
        if str(par).startswith("Arith:"):                    # thin under this operator: every operator's children
            return self._look(tbl, "Arith", slot, d)
        if par == "Step":                                    # thin for a step: what an outer program does there
            return self._look(tbl, "Program", slot, d)
        for dd in range(min(d, DCAP), -1, -1):               # a coarse slot ("ra", "rq") pools its finer ones
            pool = collections.Counter()
            for (p, s, x), c in tbl.items():
                if (p == par or (par == "Arith" and str(p).startswith("Arith:"))) and str(s).split(":")[0] == slot and x == dd: pool.update(c)
            if pool: return pool
        return collections.Counter()

    def _pick(self, c, rng, lam=0.0, alpha=0.5, allow=None, ctx=None, cost=None, ours=(), meaning=()):
        """One choice, Dirichlet-smoothed, tilted by `lam` towards continuing, and PROJECTED ONTO D.

        `allow(ctx, k)` is where D enters: it may REMOVE a child type this database cannot host or the
        renderer cannot say. Removing is all it may do -- the projection can shrink the support and never
        extend it, so no structure is sampled that R did not write.

        THREE THINGS THIS DID NOT DO, EACH OF WHICH MADE IT A FILTER RATHER THAN A PROJECTION:

        1. IT WAS CONTEXT-FREE. `allow(k)` could not tell a `Window` under an aggregate from one in a
           projection, so a database that can host a shape in one place and not another had to refuse
           both or neither.
        2. IT RECORDED NOTHING. Masking without `-log Z` is a filter: the mass removed is gone and no
           number says how much. `pd.law.restrict` computes exactly this for the fourteen-bit vector and
           reports it; every decision here should too, which is what makes KL(pi_D || P) a SUM over
           decisions rather than one figure for the whole program.
        3. IT FELL BACK SILENTLY. `if not ks: return STOP` turned "D can host nothing here" into an
           ordinary stop, which is the same shape as the depth fallback and the shape-fill retry -- the
           corpus comes out shallow or plain and nothing says a choice was taken away. The set is never
           empty: with everything masked, STOP is what remains, and the cost is always attributable.

        AND STOP ITSELF MAY BE MASKED, when something else remains. "No filter" is a form like any
        other, and a database can fail to host it: the unfiltered aggregate over this table may have
        no answer worth giving while a filtered one does. `pd.bind` asks for exactly that, and it is
        recorded as a narrowing like every other -- the mass on stopping was removed and `cost` says so.
        """
        ks = [k for k in c if allow is None or allow(ctx, k)]
        if not ks: ks = [STOP]
        w = [(c.get(k, 0) + alpha) * (math.exp(lam) if k != STOP else 1.0) for k in ks]
        if cost is not None:
            # THE PROJECTION, ACCOUNTED PER DECISION. `-log Z` is this decision's term of KL(P_D || P); the
            # entry also says WHICH options were removed and how much of the mass each carried, and which of
            # them were removed because the binder does not grow them yet (`ours`) rather than because D
            # cannot host them. `pd.projection` sums the corpus by context and by cause; the "ours" mass
            # is the part of the divergence that is not the projection, and it should read zero.
            wt = {k: (c[k] + alpha) * (math.exp(lam) if k != STOP else 1.0) for k in c}
            whole = sum(wt.values()) or 1.0
            kept = sum(w) or 1e-12
            if kept < whole:
                removed = {k: wt[k] / whole for k in c if k not in ks}
                # THREE CAUSES, KEPT APART: D's shape (nothing stands), OUR unbuilt slots (`ours`), and MEANING
                # -- an option the shape would admit that the alphabet's kinds refuse (`meaning`). The last is
                # the cost of the meaning table, and the contexts where it is large are where the profile has
                # the most to learn.
                cost.append({"ctx": ctx, "nats": -math.log(kept / whole), "removed": removed,
                             "ours": sorted(k for k in removed if k in ours),
                             "meaning": sorted(k for k in removed if k in meaning)})
            else:
                # EVERY DRAW IS RECORDED, masked or not. A decision that recorded nothing when nothing was
                # removed could not be told from a decision never made -- and 140 of 300 rows had never made
                # the step decision at all, with P's mass on it neither realised nor charged. A zero entry
                # says the decision was reached; the build's coverage receipt reads it.
                cost.append({"ctx": ctx, "nats": 0.0, "removed": {}, "ours": [], "meaning": []})
        return rng.choices(ks, weights=w)[0]

    def grow(self, t, rng, d=0, lam=0.0, budget=None, allow=None, cost=None):
        """A shape tree: {"t": type, slot: child | [children] | None}.

        `allow(ctx, kind)` projects each expansion onto what D can host AND the renderer can say; `cost`
        collects the nats each masking took, so the program's total is `sum(cost)` -- KL(pi_D || P) as a
        sum over decisions rather than one number for a whole structure.
        """
        budget = [400] if budget is None else budget
        out = {"t": t}
        for slot in FIELDS.get(t, []):
            nd = adepth(t, d)
            ctx = (t, slot, nd)
            if (t, slot) in self.member:
                out[slot] = self._pick(self.member[(t, slot)], rng, ctx=ctx, cost=cost)
                continue
            sizes = self._look(self.size, t, slot, nd)
            kinds = self._look(self.child, t, slot, nd)
            if sizes:
                kids = []
                for _ in range(self._pick(sizes, rng, lam, ctx=ctx, cost=cost) if sizes else 0):
                    c = self._pick(kinds, rng, lam, allow=allow, ctx=ctx, cost=cost)
                    if c != STOP and budget[0] > 0 and d < CAP:
                        budget[0] -= 1; kids.append(self.grow(c, rng, nd, lam, budget, allow, cost))
                out[slot] = kids
            else:
                c = self._pick(kinds, rng, lam, allow=allow, ctx=ctx, cost=cost)
                if c == STOP or budget[0] <= 0 or d >= CAP: out[slot] = None
                else:
                    budget[0] -= 1; out[slot] = self.grow(c, rng, nd, lam, budget, allow, cost)
        return out


def logprob(g, x, par="ROOT", slot="root", d=0, alpha=0.5):
    """How many nats this grammar spends on one program -- the LM loss, not a feature count.

    LENGTH COMES FOR FREE. A program is a sequence of decisions and every one contributes a term, so a
    query that does more costs more, and there is nothing to add for size. `pd.law.cost` compared the
    FREQUENCY of features and therefore could not see magnitude at all: `Arith` present in 56% of our
    rows against 92% of R's read as a mild gap over a quantity that was 0.58 deep against 3.08.

    AND STOPPING IS A DECISION. The empty slot is the child `-`, drawn from the same distribution as any
    other, so a generator that quits early puts mass on `-` where R does not and pays for it here. That
    is the whole of "length aware": there is no separate length model because stopping is in the alphabet.
    """
    lp = 0.0
    if isinstance(x, (list, tuple)):
        if slot == "order" and len(x) == 2 and x[1] in ("asc", "desc"):     # a sort key: see `observe`
            return logprob(g, x[0], par, slot, d, alpha)
        c = g.size.get((par, slot, min(d, DCAP))) or g.size.get((par, slot, 0))
        if c:
            n, v = sum(c.values()), len(c)
            lp += math.log((c.get(len(x), 0) + alpha) / (n + alpha * (v + 1)))
        if x and all(isinstance(y, tuple) and len(y) == 2 for y in x):        # items that are pairs: see `observe`
            for y in x:
                if slot == "order": lp += logprob(g, y, par, slot, d, alpha)
                else:
                    for z in y:
                        if is_dataclass(z): lp += logprob(g, z, par, slot, d, alpha)
            return lp
        for y in x: lp += logprob(g, y, par, slot, d, alpha)
        return lp
    key = (par, slot, min(d, DCAP))
    c = g.child.get(key) or g.child.get((par, slot, 0))
    t = (type(x).__name__ if is_dataclass(x) else
         "Const" if slot == "limit" and isinstance(x, (int, float)) and not isinstance(x, bool) else STOP)
    if c:
        n, v = sum(c.values()), len(c)
        lp += math.log((c.get(t, 0) + alpha) / (n + alpha * (v + 1)))
    if not is_dataclass(x): return lp
    for f in FIELDS[t]:
        lp += logprob(g, getattr(x, f, None), t, f, adepth(t, d), alpha)
    return lp


def divergence(ours, theirs, alpha=0.5, by="theirs"):
    """KL per DECISION between two grammars, weighted by how often the decision is made.

    WHICH SIDE DOES THE WEIGHTING DECIDES WHAT THE NUMBER MEANS, and getting it wrong inverts the answer.

    Weighted by OURS (`by="ours"`), it asks "is what we produce plausible under R" -- and it REWARDS A
    GENERATOR FOR NOT ATTEMPTING ANYTHING. Measured that way the old corpus scored 0.074 against the new
    one's 0.282 and looked three times better, purely because it almost never reached `Arith.r`, the
    context where the two differ most (KL 3.66). A generator emitting nothing but `SELECT col FROM t`
    would score near zero. That is the same blindness as the feature-frequency divergence wearing a
    different hat.

    Weighted by THEIRS (the default), it asks "do we cover what R does" -- so a context R spends 2% of its
    decisions in costs 2% of the total whether we ever go there or not, and never going there is charged
    in full. That is the direction that measures a generator.

    Contexts R never reached are skipped rather than charged infinity: a structure R never wrote is not
    evidence about R. Which means this cannot punish us for INVENTING something, only for missing it --
    a real blind spot, and the reason `by="ours"` is still available rather than deleted.

    THE SCALE, so the number can be read. A divergence with no floor is unusable, and the floor here is
    what SAMPLING ALONE produces: fit two random halves of R and measure them against each other.

        R against itself                      0.000
        R's own halves, 12 random splits      0.017   (0.014 to 0.020)  <- the floor
        the 09-20 corpus                      0.168   ten times it
        the 09-21 corpus                      0.333   twenty times it

    So both corpora are far outside the noise and the difference between them is real. And one more
    reading falls out: our corpus's OWN halves diverge by 0.004, four times LESS than R's halves do. A
    corpus built from one repeated idiom has less internal variety than the thing it is imitating, which
    is the monotony showing up from a direction nothing else measures.
    """
    tot, per = 0.0, {}
    base = theirs if by == "theirs" else ours
    N = sum(sum(c.values()) for c in base.child.values()) or 1
    for key, oc in (ours.child.items() if by == "ours" else
                    [(k, ours.child.get(k) or collections.Counter()) for k in theirs.child]):
        tc = theirs.child.get(key) or theirs.child.get((key[0], key[1], 0))
        if not tc: continue
        n_o, n_t = sum(oc.values()), sum(tc.values())
        vocab = set(oc) | set(tc)
        d = 0.0
        for v in vocab:
            p = (oc.get(v, 0) + alpha) / (n_o + alpha * len(vocab))
            q = (tc.get(v, 0) + alpha) / (n_t + alpha * len(vocab))
            # the direction of the KL follows the weighting: measure the side that sets the agenda
            d += (p * math.log(p / q)) if by == "ours" else (q * math.log(q / p))
        w = (n_o if by == "ours" else n_t) / N
        per[key] = (d, w)
        tot += d * w
    return tot, per


def typed(x, par, typer):
    """The abstract label of a node under the fit: a leaf's KIND or a constant's ROLE where meaning is
    asked -- under arithmetic and inside an aggregate -- and the bare node type everywhere else."""
    t = type(x).__name__
    if str(par).startswith("Arith:"): par = "Arith"          # the operator-aware context types its leaves the same way
    if par not in ("Arith", "Agg"): return t
    if t == "Col":
        # A LEAF IS RECORDED BY ITS CLASS (`specbridge.pd.structures.meaning.klass`): amount, ratio, time, or "?" -- what the
        # operator above it needs, not the source's word for the column. A compound ("measure times measure")
        # is classed by its leading kind.
        from specbridge.pd.structures.meaning import klass
        return "Col:" + klass(typer.kind(x))
    if t == "Const" and par == "Arith": return "Const"
    return t


def inline_lets(p):
    """A STEP THAT ONLY NAMES PER-ROW COMPUTATIONS IS A LET-BINDING, NOT A FEATURE. Half of R's programs
    (52 of 107) write `WITH t AS (SELECT ..., x / y AS r FROM ...) SELECT AVG(r) FROM t`: the step groups
    nothing, aggregates nothing, cuts nothing -- it names a computed column so the outer query can read
    it. That is the same program as `SELECT AVG(x / y) FROM ...`, which is what the binder builds; fitted
    as a step it made P ask for a second SELECT in 64% of programs and charged the binder for every one.
    Such steps are inlined before the fit: the outer's references take the step's expressions, the
    outer's scan takes the step's scan, the filters conjoin. A step that groups, aggregates, cuts or
    windows is a real second level and stays."""
    from dataclasses import replace, fields, is_dataclass
    from specbridge.pd.structures.algebra import Agg, And, Col, Program, Scan, Window
    ctes = list(p.ctes)
    outer = replace(p, ctes=())
    changed = True
    stuck = set()
    while ctes and changed:
        changed = False
        from specbridge.pd.structures.algebra import _aggregating
        def naming(q):
            return not (q.group or q.limit is not None or q.distinct or q.having is not None or q.ctes or
                        any(_aggregating(e) for e, _a in q.select) or _find(q.select, Window) or _find(q.where, Window))
        # ANY let-binding step is inlined, wherever it stands: canonical form may not depend on step order
        k = next((k for k in range(len(ctes)) if naming(ctes[k][1]) and (k, ctes[k][0]) not in stuck), None)
        if k is None: break
        name, q = ctes[k]
        # every later program that reads the step by name gets its expressions instead
        subst = {}
        for e, alias in q.select:
            if alias: subst[str(alias).lower()] = e
            elif isinstance(e, Col): subst[str(e.name).lower()] = e
        def rewrite(x):
            if isinstance(x, Col) and str(x.table).lower() == name.lower():
                return subst.get(str(x.name).lower(), x)
            if isinstance(x, tuple) and len(x) == 2 and isinstance(x[0], Col) and str(x[0].table).lower() == name.lower() \
                    and x[1] is None and str(x[0].name).lower() in subst:
                # AN OUTPUT READ FROM THE STEP KEEPS ITS NAME: `SELECT hr.res` was `res` to the query above it,
                # and after the step's expression replaces the column the name must stay, or nothing can read it.
                return (subst[str(x[0].name).lower()], x[0].name)
            if isinstance(x, (list, tuple)): return type(x)(rewrite(y) for y in x)
            if is_dataclass(x) and not isinstance(x, type):
                return replace(x, **{f.name: rewrite(getattr(x, f.name)) for f in fields(x)})
            return x
        def rescan(prog):
            from specbridge.pd.structures.algebra import Join
            sc = prog.scan
            if str(sc.table).lower() == name.lower():
                # the step is the base: the outer reads the step's scan, its joins after the step's own
                scan = Scan(q.scan.table, q.scan.alias, tuple(q.scan.joins) + tuple(sc.joins))
            elif any(str(j.table).lower() == name.lower() for j in sc.joins):
                # the step is joined in: it becomes the step's base table (and the step's own joins follow)
                joins = []
                for j in sc.joins:
                    if str(j.table).lower() == name.lower():
                        joins.append(replace(j, table=q.scan.table, alias=q.scan.alias)); joins += list(q.scan.joins)
                    else:
                        joins.append(j)
                scan = Scan(sc.table, sc.alias, tuple(joins))
            else:
                return None
            where = prog.where if q.where is None else (q.where if prog.where is None else And((q.where, prog.where)))
            return replace(prog, scan=scan, where=where)
        users = [i for i, (_n, r) in enumerate(ctes) if i > k and _find(r, Col) and any(str(c.table).lower() == name.lower() for c in _find(r, Col))]
        users_outer = any(str(c.table).lower() == name.lower() for c in _find(outer, Col)) or str(outer.scan.table).lower() == name.lower()
        try:
            ok = True
            new_ctes = list(ctes[:k])
            for i, (n2, r) in enumerate(ctes):
                if i <= k: continue
                if i in users:
                    r2 = rescan(rewrite(r))
                    if r2 is None: ok = False; break
                    new_ctes.append((n2, r2))
                else:
                    new_ctes.append((n2, r))
            o2 = rescan(rewrite(outer)) if users_outer else outer
            if not ok or o2 is None: stuck.add((k, name)); changed = True; continue
            ctes, outer, changed = new_ctes, o2, True
        except Exception:
            stuck.add((k, name)); changed = True          # a step that cannot be rewritten stays, and is counted
    try:
        return replace(outer, ctes=tuple(ctes))
    except Exception:
        return p                                      # a rewrite the algebra refuses: the program stays as written


def fit(programs, typers=None):
    """P from R's programs. With `typers` (one per program, `specbridge.pd.structures.meaning.Typer`), the leaves under arithmetic
    are recorded by kind and role; without, as bare nodes. Let-binding steps are inlined first."""
    g = Grammar()
    for i, p in enumerate(programs):
        try: p = inline_lets(p)
        except Exception: pass
        # THE TYPER INDEXES THE PROGRAM THE FIT READS. Inlining builds new nodes, and a typer indexed on the
        # original program knew none of their constants: every constant of an inlined program fell to the
        # "text" role -- 296 `Const:text` leaves under arithmetic in a source with three text constants.
        if typers: typers[i]._index(p)
        g.observe(p, typer=typers[i] if typers else None)
        # HOW THE OUTER QUERY USES ITS STEP -- one more decision R makes, fitted like the rest: it aggregates
        # over the step (a summary of a summary), joins the step back to a base table (a row beside its
        # group's statistic), or filters and cuts on the step's value (the top few per group).
        if p.ctes: g.member[("Step", "use")][step_use(p)] += 1
    return g


def step_use(p):
    """What the outer query does with its steps: "aggregate", "join", "filter" or "read"."""
    from specbridge.pd.structures.algebra import Agg, Col, _find
    steps = {str(n).lower() for n, _q in p.ctes}
    tabs = [str(p.scan.table).lower()] + [str(j.table).lower() for j in p.scan.joins]
    if p.group or any(_find(e, Agg) for e, _a in p.select): return "aggregate"
    if any(t in steps for t in tabs) and any(t not in steps for t in tabs): return "join"
    if p.limit is not None or (p.where is not None and any(str(c.table).lower() in steps for c in _find(p.where, Col))): return "filter"
    return "read"


def shape(x, d=0, c=None):
    """Node counts and arithmetic depth, measured identically on a real program and on a sampled tree."""
    c = collections.Counter() if c is None else c
    if isinstance(x, (list, tuple)):
        for y in x: shape(y, d, c)
        return c
    if isinstance(x, dict):
        t = x["t"]; kids = [v for k, v in x.items() if k != "t"]
    elif is_dataclass(x):
        t = type(x).__name__; kids = [getattr(x, f, None) for f in FIELDS[t]]
    else:
        return c
    c[t] += 1; nd = adepth(t, d); c["depth"] = max(c["depth"], nd)
    for v in kids: shape(v, nd, c)
    return c


def mined(src="livesql"):
    """R, lifted: the programs the law is fitted from, read through `specbridge.pd.structures.sources` -- one source or a tuple."""
    from specbridge.pd.structures.sources import programs
    return [p for s in ((src,) if isinstance(src, str) else src) for p in programs(s)]


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    lams = [float(x) for x in sys.argv[1:]] or [0.0, 0.4, 0.8]
    R = mined(); g = fit(R)
    rs = [shape(p) for p in R]
    print("  fitted from %d programs / %d expansions / %d contexts\n" % (g.n, g.events(), len(g.child)))
    print("  OUT OF SAMPLE -- none of these is a parameter of the grammar")
    print("  %-12s %14s %s" % ("", "R", "".join("%14s" % ("lam=%.1f" % l) for l in lams)))
    S = {l: [shape(g.grow("Program", random.Random(i), lam=l)) for i in range(400)] for l in lams}
    for k in ("depth", "Arith", "Col", "Join", "Agg", "Func", "Const", "Case", "Window"):
        m = lambda xs: sum(x[k] for x in xs) / len(xs)
        print("  %-12s %7.2f /%4d %s" % (k, m(rs), max(x[k] for x in rs),
              "".join("%7.2f /%4d" % (m(S[l]), max(x[k] for x in S[l])) for l in lams)))
