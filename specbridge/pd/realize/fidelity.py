"""specbridge.pd.realize.fidelity — HOW MUCH OF P SURVIVES ON A DATABASE. A structural-fidelity PROXY, not a certificate.

Three populations, every program measured on its canonical form (the program itself; unfinished attempts get
no invented measurement and are reported as a rate):

    P      samples from frozen P with no database (the reference)
    C      database-constrained attempts that FINISHED decoding (the effect of masks and binding)
    E      executable outputs (C, further selected by the verifier and by execution)

Two comparisons: P -> C is the database-decoding shift; C -> E is rejection's selection effect. Each distance
is calibrated against sampling noise: two independent equal-sized batches from P, compared repeatedly, give
the distance that chance alone produces at this sample size.

    TV   total variation between binned histograms: how much probability mass differs (0..1)
    W1   Wasserstein distance between numeric distributions, in the feature's own units
    KL   the context-level refit KL (`actions.divergence`): a diagnostic, not a whole-program guarantee

    python -m specbridge.pd.realize.fidelity <db> [<db> ...] [--n 200] [--reps 10]
"""
from __future__ import annotations
import collections, json, os, random, sys, time

from specbridge.pd.structures.algebra import Agg, And, Arith, Between, Case, Cmp, In, IsNull, Like, Not, Or, Program, SetOp, Subq, Window, _find

NUMERIC = ("arith_depth", "query_nesting", "step_chain", "joins", "aggregates", "predicates", "outputs", "refs", "size")
PRESENCE = ("has_arith", "has_window", "has_case", "has_subquery", "has_step")


def _reads(x, memo):
    """Does `x` read data: a column (a stored one or a step's output), an aggregate, a window or a subquery?"""
    from dataclasses import fields, is_dataclass
    from specbridge.pd.structures.algebra import Agg, Col, Subq, Window
    if id(x) in memo: return memo[id(x)][1]
    if isinstance(x, (Col, Agg, Window, Subq)): v = True
    elif isinstance(x, (tuple, list)): v = any(_reads(y, memo) for y in x)
    elif is_dataclass(x) and not isinstance(x, type): v = any(_reads(getattr(x, f.name), memo) for f in fields(x))
    else: v = False
    memo[id(x)] = (x, v)
    return v


def _arith_depth(x, memo=None, rmemo=None):
    """The deepest nesting of arithmetic operators that compute from data: an operator counts only when its subtree
    reads data, so arithmetic over constants alone (round(2, 1) / 5) adds no depth -- it is a constant, however
    it is written. (R_s and BIRD's gold never nest arithmetic over constants: there the two measures agree.)"""
    from dataclasses import fields, is_dataclass
    memo = {} if memo is None else memo; rmemo = {} if rmemo is None else rmemo
    if id(x) in memo: return memo[id(x)][1]
    if isinstance(x, (tuple, list)): v = max((_arith_depth(y, memo, rmemo) for y in x), default=0)
    elif isinstance(x, (Program, SetOp)): v = 0
    elif is_dataclass(x) and not isinstance(x, type):
        v = max((_arith_depth(getattr(x, f.name), memo, rmemo) for f in fields(x)), default=0) + \
            (1 if isinstance(x, Arith) and _reads(x, rmemo) else 0)
    else: v = 0
    memo[id(x)] = (x, v)
    return v


def _queries(p, depth=0):
    """(query, subquery nesting depth) for the program and everything nested in it."""
    if isinstance(p, SetOp):
        yield from _queries(p.left, depth); yield from _queries(p.right, depth); return
    yield p, depth
    for _n, q in p.ctes: yield from _queries(q, depth)
    for s in _find((p.select, p.where, p.having, p.order), Subq): yield from _queries(s.program, depth + 1)


def _step_chain(p):
    """The longest chain of steps each reading an earlier one (0 without steps)."""
    if not isinstance(p, Program) or not p.ctes: return 0
    names = [n.lower() for n, _q in p.ctes]; depth = {}
    for n, q in p.ctes:
        reads = [str(t).lower() for t in ([q.scan.table] + [j.table for j in q.scan.joins])] if isinstance(q, Program) else []
        depth[n.lower()] = 1 + max((depth[r] for r in reads if r in depth), default=0)
    return max(depth.values())


def features(p):
    from specbridge.pd.structures.actions import sequence
    seq = sequence(p, lets=True)
    qs = list(_queries(p))
    root = p if isinstance(p, Program) else None
    preds = sum(len(_find(q.where, (Cmp, IsNull, Like, In, Between))) + len(_find(q.having, (Cmp, IsNull, Like, In, Between)))
                for q, _d in qs if isinstance(q, Program))
    f = {
        "arith_depth": max((_arith_depth((q.select, q.where, q.having, q.order)) for q, _d in qs if isinstance(q, Program)), default=0),
        "query_nesting": max(d for _q, d in qs),
        "step_chain": _step_chain(p),
        "joins": len(root.scan.joins) if root else 0,
        "aggregates": sum(len(_find((q.select, q.having, q.order), Agg)) for q, _d in qs if isinstance(q, Program)),
        "predicates": preds,
        "outputs": len(root.select) if root else 0,
        "refs": sum(1 for _c, a in seq if a == "REF"),
        "size": len(seq),
    }
    f.update(has_arith=int(f["arith_depth"] > 0), has_window=int(bool(_find(p, Window))),
             has_case=int(bool(_find(p, Case))), has_subquery=int(f["query_nesting"] > 0),
             has_step=int(bool(root and root.ctes)))
    return f


# ---------------------------------------------------------------- distances
def _bins(key, v):
    if key == "size": return min(v // 25, 16)              # 25-action bins, 400+ pooled
    if key in ("refs", "predicates", "aggregates"): return min(v, 12)
    return min(v, 10)


def tv(xs, ys, key):
    a, b = collections.Counter(_bins(key, x) for x in xs), collections.Counter(_bins(key, y) for y in ys)
    na, nb = max(1, len(xs)), max(1, len(ys))
    return 0.5 * sum(abs(a[k] / na - b[k] / nb) for k in set(a) | set(b))


def w1(xs, ys):
    """Wasserstein-1 between two empirical distributions: the area between their CDFs."""
    if not xs or not ys: return float("nan")
    xs, ys = sorted(xs), sorted(ys)
    pts = sorted(set(xs) | set(ys)); out = 0.0
    import bisect
    for a, b in zip(pts, pts[1:]):
        fa = bisect.bisect_right(xs, a) / len(xs); fb = bisect.bisect_right(ys, a) / len(ys)
        out += abs(fa - fb) * (b - a)
    return out


def joint_tv(A, B, k1, k2):
    a = collections.Counter((x[k1], _bins(k2, x[k2])) for x in A)
    b = collections.Counter((x[k1], _bins(k2, x[k2])) for x in B)
    na, nb = max(1, len(A)), max(1, len(B))
    return 0.5 * sum(abs(a[k] / na - b[k] / nb) for k in set(a) | set(b))


def compare(A, B):
    out = {}
    for k in NUMERIC: out[k] = (tv([x[k] for x in A], [y[k] for y in B], k), w1([x[k] for x in A], [y[k] for y in B]))
    for k in PRESENCE:
        pa = sum(x[k] for x in A) / max(1, len(A)); pb = sum(x[k] for x in B) / max(1, len(B))
        out[k] = (abs(pa - pb), None)
    out["arith x depth"] = (joint_tv(A, B, "has_arith", "arith_depth"), None)
    out["step x joins"] = (joint_tv(A, B, "has_step", "joins"), None)
    return out


# ---------------------------------------------------------------- populations
def p_samples(law, n, rng):
    """n FINISHED samples from P with no database, and how many draws it took."""
    out, tries = [], 0
    while len(out) < n and tries < n * 5:
        tries += 1
        try: out.append(law.sample(rng))
        except Exception: pass
    return out, tries


def constrained(law, db, n, rng, log=print):
    """n attempts on the database: (finished programs, executable programs, unfinished count, timings)."""
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.realize.generate import attempt, execute
    from specbridge.pd.structures.algebra import emit
    cat = Catalogue(db)
    finished, executable, unfinished, tg, te = [], [], collections.Counter(), 0.0, 0.0
    for i in range(n):
        t = time.time(); p, verdict, _b = attempt(law, cat, rng, law.caps); tg += time.time() - t
        if p is None:
            # a program the judge rejected still FINISHED decoding; only a decoding failure is unfinished
            if verdict.startswith("invalid: dead end") or "longer than" in verdict or verdict.startswith("bug"):
                unfinished[verdict.split(" at ")[0][:60]] += 1
            else:
                unfinished["finished but rejected: " + verdict[:50]] += 1
            continue
        finished.append(p)
        t = time.time(); status, _res = execute(cat.con, emit(p)); te += time.time() - t
        if status == "ok": executable.append(p)
    return finished, executable, unfinished, tg, te


def main(dbs, n=200, reps=10, log=print):
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit, divergence
    from specbridge.pd.structures.sources import programs, typers
    R, T = programs("livesql"), typers("livesql"); law = fit(R, T)
    rng = random.Random(0)
    t0 = time.time()
    # the reference, and the noise baseline: pairs of independent equal-sized batches from P
    ref, ref_tries = p_samples(law, n, rng)
    PF = [features(p) for p in ref]
    base = collections.defaultdict(list)
    for r in range(reps):
        a, _ = p_samples(law, n, rng); b, _ = p_samples(law, n, rng)
        for k, (d_tv, d_w) in compare([features(x) for x in a], [features(x) for x in b]).items():
            base[k].append((d_tv, d_w))
    noise = {k: (sum(v[0] for v in vs) / len(vs), (sum(v[1] for v in vs) / len(vs)) if vs[0][1] is not None else None) for k, vs in base.items()}
    log("STRUCTURAL-FIDELITY PROXY (not a certificate). P frozen on %d livesql programs." % len(R))
    log("Reference: %d finished samples from P with no database (%d draws). Noise baseline: %d pairs of %d-sample batches from P. %.0fs." % (
        len(ref), ref_tries, reps, n, time.time() - t0))
    for db in dbs:
        t1 = time.time()
        C, E, unf, tg, te = constrained(law, db, n, random.Random(1))
        CF, EF = [features(p) for p in C], [features(p) for p in E]
        log("\n" + "=" * 100 + "\n%s: %d attempts -> %d finished decoding, %d executable. Unfinished or rejected: %s" % (
            db, n, len(C), len(E), ", ".join("%s %d" % kv for kv in unf.most_common())))
        log("generation %.0f ms per attempt, execution %.0f ms per finished program (%.0fs)" % (1000 * tg / n, 1000 * te / max(1, len(C)), time.time() - t1))
        pc, ce = compare(PF, CF), compare(CF, EF)
        log("\n  %-15s %-22s %-22s %-22s" % ("feature", "noise P vs P", "P -> constrained", "finished -> executable"))
        log("  %-15s %-22s %-22s %-22s" % ("", "TV     W1", "TV     W1   (x noise)", "TV     W1   (x noise)"))
        for k in list(NUMERIC) + list(PRESENCE) + ["arith x depth", "step x joins"]:
            nt, nw = noise[k]
            def cell(d):
                t, w = d
                ratio = t / nt if nt else float("inf")
                return "%.3f %s (%4.1fx)" % (t, ("%6.2f" % w) if w is not None else "      ", ratio)
            log("  %-15s %.3f %s   %s   %s" % (k, nt, ("%6.2f" % nw) if nw is not None else "      ", cell(pc[k]), cell(ce[k])))
        log("\n  means           P        constrained  executable")
        for k in NUMERIC + PRESENCE:
            m = lambda F: sum(x[k] for x in F) / max(1, len(F))
            log("  %-15s %8.2f %10.2f %10.2f" % (k, m(PF), m(CF), m(EF)))
        log("\n  arithmetic depth histogram (share of programs)")
        for dep in range(0, 9):
            h = lambda F: sum(1 for x in F if min(x["arith_depth"], 8) == dep) / max(1, len(F))
            log("    depth %s   P %.2f   constrained %.2f   executable %.2f" % (dep if dep < 8 else "8+", h(PF), h(CF), h(EF)))
        _rows, klc = divergence(law, C); _rows, kle = divergence(law, E)
        log("\n  context refit KL per decision (diagnostic): constrained %.3f, executable %.3f" % (klc, kle))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    n = int(opts.get("--n", 200)); reps = int(opts.get("--reps", 10))
    main([a for a in args if not a.isdigit()] or ["california_schools"], n, reps)
