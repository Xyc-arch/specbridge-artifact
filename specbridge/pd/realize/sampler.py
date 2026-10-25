"""specbridge.pd.realize.sampler — DRAW FROM P, WITH A CERTIFIED BOUND ON HOW FAR THE DRAW IS FROM THE INTENDED PROJECTION.

The intended law at a prefix s is Q(a|s) ∝ P(a|s)·1[a has a valid completion]. It is not computed. Instead:

    U(s)   the checker's allow: every action not PROVEN infeasible (the checker removes only by proof)
    L(s)   actions with a WITNESS: a complete sequence through them that the verifier accepts
    L ⊆ A ⊆ U, and the draw is P restricted to U, so at each decision TV(draw, Q) ≤ 1 − ℓ/u with ℓ, u the
    P-mass of L and U. Over a program the bound adds up: η = Σ_t (1 − ℓ_t/u_t).

WITNESSES ARE CHEAP BECAUSE THEY ARE REUSED. A dive is one decoder run: replay the prefix, then draw from P
restricted to the checker's allow until the program is finished, then verify. After a choice, the rest of
the chosen action's witness witnesses every later prefix on its path, so a new dive is needed only where
the draw leaves it. At a decision, unknown actions are dived in order of P-mass until the local bound is
under `eps` or `dives` are spent; a spent budget leaves the bound loose and visible, never hidden.

EMISSION IS DECIDED BY THE VERIFIER, NOT BY THE SAMPLER. A drawn program the verifier rejects is counted
with its reason and not emitted. The delivered distribution is therefore the draw conditioned on
acceptance; with η the trajectory bound and acceptance probability α, TV(delivered, Q) ≤ min(1, 2η/α) in
general and the report gives the attempted and emitted frequencies side by side. The output is not called
the exact projection.

    python -m specbridge.pd.realize.sampler [n] [audit]      # n generated (fast), then `audit` draws with the witness bound
"""
from __future__ import annotations
import collections, math, random, sys, time

from specbridge.pd.structures.actions import STOP, _draw, _is_member_ctx
from specbridge.pd.realize.verify import interpret, judge, DeadEnd as _Dead, DeadEnd as _Dead, DeadEnd as _Dead


FALLBACK = collections.Counter()      # how often each fallback level was needed, for the report


def _p(law, ctx, allow):
    """P's probability at a decision, restricted to `allow`. When every option P gives probability to in this
    exact context is masked, P's OWN coarser contexts are used (the same backoff the fit uses when a context is
    unseen), so a draw never invents probability for an action P gives none. Uniform over R's tokens is the
    last resort, counted in FALLBACK."""
    ok = allow if callable(allow) else (lambda a: allow is None or a in allow)
    c = law.counts(ctx) or {}
    opts = {a: k for a, k in c.items() if ok(a)}
    if opts: return opts, True
    if len(ctx) == 3 and ctx[2] in ("UNIT_PARAM", "FORMULA_PARAM", "SCORE", "TOP_K", "PARAM"):
        pool = law.pool.get(ctx[2]) or {}
        opts = {a: k for a, k in pool.items() if ok(a)}
        if opts: FALLBACK["pool of the role"] += 1; return opts, False
    else:
        for k in range(len(ctx) - 1, 1, -1):
            back = law.back.get(ctx[:k])
            if back:
                opts = {a: v for a, v in back.items() if ok(a)}
                if opts: FALLBACK["backed off to %d context fields" % k] += 1; return opts, False
        back = law.back.get(("SLOT", ctx[1])) if len(ctx) >= 2 else None
        if back:
            opts = {a: v for a, v in back.items() if ok(a)}
            if opts: FALLBACK["backed off to the slot"] += 1; return opts, False
    if not allow or callable(allow): return {}, False
    seen = law.tokens() if not _is_member_ctx(ctx) else None
    FALLBACK["uniform over admissible tokens"] += 1
    return {a: 1 for a in sorted(allow, key=str) if seen is None or a in seen}, False


# THE PROJECTION LAW FOR REAL GENERATION (decided 2026-09-25): HIERARCHICAL. At an expression or predicate
# decision, P's own split between leaf and compound is kept whenever both categories still have an admissible
# action P gives probability to; masking and renormalisation happen WITHIN the chosen category. If one category has
# nothing left, the other takes all. FLAT (renormalise across both at once) is kept only as an experimental baseline.
# Two levels only, frozen: no deeper hierarchy until the aggregate shift on financial is explained.
PROJECTION = {"mode": "hier", "cases": collections.Counter()}
PRED_LEAVES = {"CMP", "ISNULL", "LIKE", "IN", "BETWEEN", "EXISTS", "EXPR"}
PRED_COMPOUNDS = {"AND", "OR", "NOT"}
_MODES = ("free", "undecided", "collapsed", "row")


def project(law, d, opts):
    """Apply the projection law to the admissible options at a decision (see PROJECTION)."""
    if PROJECTION["mode"] != "hier": return opts
    from specbridge.pd.structures.actions import COMPOUND, LEAVES
    ctx = d.ctx
    if len(ctx) >= 7 and ctx[4] in _MODES: leaf_set, comp_set = LEAVES, COMPOUND
    elif d.universe is not None and not callable(d.allow) and set(d.universe) <= (PRED_LEAVES | PRED_COMPOUNDS): leaf_set, comp_set = PRED_LEAVES, PRED_COMPOUNDS
    else: return opts
    c = law.counts(ctx) or {}
    m_leaf = sum(k for a, k in c.items() if a in leaf_set); m_comp = sum(k for a, k in c.items() if a in comp_set)
    L = {a: k for a, k in opts.items() if a in leaf_set}; C = {a: k for a, k in opts.items() if a in comp_set}
    sl, sc = sum(L.values()), sum(C.values())
    if not (m_leaf and m_comp): PROJECTION["cases"]["P gives one category no mass"] += 1; return opts
    if sl and sc:
        PROJECTION["cases"]["both available: P's split kept"] += 1
        out = {a: m_leaf * k / sl for a, k in L.items()}; out.update({a: m_comp * k / sc for a, k in C.items()}); return out
    PROJECTION["cases"]["only %s available" % ("leaves" if sl else "compounds")] += 1
    return opts


class Draw:
    def __init__(self): self.eta, self.decisions, self.dives, self.loose = 0.0, 0, 0, 0


def dive(law, prefix, caps, rng):
    """One witness attempt: replay `prefix`, then draw from P within allow. Returns (sequence or None,
    outcome) with outcome "valid", "invalid: <why>" or "bug: <why>" -- an implementation error is never
    folded into an invalid candidate."""
    seq, it = [], iter(prefix)
    def choose(d):
        try: c, a = next(it)
        except StopIteration:
            opts, _ = _p(law, d.ctx, d.allow)
            if not opts: raise _Dead(d.ctx)
            a = _draw(opts, rng)
            seq.append((d.ctx, a)); return a
        seq.append((c, a)); return a
    kind, x = interpret(choose, caps)
    if kind == "bug": return None, "bug: " + x
    if kind != "program": return None, "invalid: " + x
    why = judge(x, seq)
    return (seq, "valid") if why is None else (None, "invalid: " + why)


def sample(law, rng, caps=None, eps=0.02, dives=0, stats=None):
    """One program. Returns (program or None, sequence, Draw, verdict, bugs). With `dives` 0 (generation):
    P under the checker's allow, then the verifier -- no search. With `dives` > 0 (the audit): witnesses and
    the per-decision bound, at the cost of one prefix replay per dive."""
    caps = caps or law.caps
    st, seq, witness, bugs = Draw(), [], [None], []
    def choose(d):
        opts, fitted = _p(law, d.ctx, d.allow)
        if not opts: raise _Dead(d.ctx)
        if not dives:
            st.decisions += 1; a = _draw(opts, rng); seq.append((d.ctx, a)); return a
        i = len(seq); W = witness[0]
        L = {}
        if W is not None and i < len(W) and W[i][0] == d.ctx and W[i][1] in opts: L[W[i][1]] = W
        u = sum(opts.values())
        ell = lambda: sum(opts[a] for a in L)
        if len(opts) > 1:
            for a in sorted(opts, key=lambda a: -opts[a]):
                if 1 - ell() / u <= eps: break
                if a in L: continue
                for _ in range(dives):
                    st.dives += 1
                    w, outcome = dive(law, seq + [(d.ctx, a)], caps, rng)
                    if w is not None: L[a] = w; break
                    if outcome.startswith("bug"): bugs.append(outcome)
            if 1 - ell() / u > eps: st.loose += 1
        # one admissible action: the draw equals Q there whenever Q is defined (some action is feasible)
        if len(opts) > 1: st.eta += 1 - ell() / u
        st.decisions += 1
        a = _draw(opts, rng)
        if a not in L:                            # keep a witness along the drawn path, so later prefixes reuse it
            for _ in range(dives):
                st.dives += 1
                w, outcome = dive(law, seq + [(d.ctx, a)], caps, rng)
                if w is not None: L[a] = w; break
                if outcome.startswith("bug"): bugs.append(outcome)
        witness[0] = L.get(a)
        seq.append((d.ctx, a)); return a
    kind, x = interpret(choose, caps)
    if kind != "program": return None, seq, st, x, bugs
    why = judge(x, seq)
    if why == "not canonical":
        from specbridge.pd.structures.actions import sequence
        again = sequence(x); i = next((i for i in range(min(len(again), len(seq))) if again[i] != seq[i]), None)
        why += ": %s drawn %s, reads back as %s" % ((" ".join(map(str, seq[i][0][:2])), seq[i][1], again[i][1]) if i is not None else ("length", len(seq), len(again)))
    return (x if why is None else None), seq, st, why or "valid", bugs


def main(n=500, audit=0, eps=0.02, dives=2, out="out/sampler", log=print):
    """Generate `n` programs (fit, masked draw, verify) and report; then, if `audit`, run the witness bound on
    `audit` further draws. Every draw is appended to out/<mode>.jsonl as it finishes, so a run is auditable
    and its progress readable while it runs."""
    import json, os, warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit, _stats
    from specbridge.pd.structures.sources import programs, typers
    os.makedirs(out, exist_ok=True)
    t0 = time.time(); R, T = programs("livesql"), typers("livesql"); law = fit(R, T)
    log("fit P on %d programs in %.2fs" % (len(R), time.time() - t0))
    for mode, k, dv in (("generate", n, 0), ("audit", audit, dives)):
        if not k: continue
        rng = random.Random(0); t0 = time.time()
        verdicts, etas, emitted, attempted, allbugs, loose, ndives, ndec = collections.Counter(), [], [], [], collections.Counter(), 0, 0, 0
        with open("%s/%s.jsonl" % (out, mode), "w") as f:
            for i in range(k):
                p, seq, st, verdict, bugs = sample(law, rng, eps=eps, dives=dv)
                verdicts[verdict[:110]] += 1; etas.append(st.eta); attempted.append(seq)
                loose += st.loose; ndives += st.dives; ndec += st.decisions
                for b in bugs: allbugs[b[:90]] += 1
                if p is not None: emitted.append(seq)
                f.write(json.dumps({"i": i, "verdict": verdict, "decisions": st.decisions, "dives": st.dives,
                                    "eta": round(st.eta, 4), "seconds": round(time.time() - t0, 2)}) + "\n"); f.flush()
        dt = time.time() - t0
        log("\n%s: %d draws in %.1fs (%.1f ms each); emitted %d (%.0f%%)" % (mode.upper(), k, dt, 1000 * dt / k, len(emitted), 100 * len(emitted) / k))
        for v, c in verdicts.most_common(12):
            if v != "valid": log("    %4d  %s" % (c, v))
        if dv:
            etas.sort()
            log("  bound eta per program: median %.3f, 90th pct %.3f, max %.3f" % (etas[len(etas) // 2], etas[int(len(etas) * .9)], etas[-1]))
            log("  %d decisions, %d dives (%.2f per decision), %d decisions looser than eps %.2f" % (ndec, ndives, ndives / max(1, ndec), loose, eps))
            for b, c in allbugs.most_common(5): log("    bug %4d  %s" % (c, b))
        if mode == "generate":
            rs, at, em = _stats([sequence_of(p) for p in R]), _stats(attempted), _stats(emitted)
            log("  per program: R (n=%d), attempted (n=%d), emitted (n=%d)" % (len(R), len(attempted), len(emitted)))
            for key in ("actions", "arith", "depth", "ref", "sort_is_ref", "ordered", "limited", "agg", "case", "joins", "grouped", "step"):
                log("    %-14s %7.2f %9.2f %8.2f" % (key, rs.get(key, 0), at.get(key, 0), em.get(key, 0)))


def sequence_of(p):
    from specbridge.pd.structures.actions import sequence
    return sequence(p)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500, int(sys.argv[2]) if len(sys.argv) > 2 else 0)
