"""specbridge.pd.realize.split — P -> P_D -> SQL, WITH THE TWO DIFFERENCES KEPT APART.

    P -> P_D        the INTENDED projection: at every decision, the actions the checker removed, the share of
                    P's probability they carried, and the rule that removed each -- of three kinds:
                        D            the database cannot supply a binding (no column, value, link, date)
                        LANGUAGE     a rule of the IR, the canonical form or a declared policy
                        FEASIBILITY  what the action would open cannot be filled
                    Measured on the same draws with no database too, so D's own share is visible.
    P_D -> SQL      REALISATION loss: draws from P_D that do not become SQL, with reasons; and, per decision,
                    the actions chosen across ALL draws (every decision a failed draw made was still a draw from
                    P_D) against the actions in emitted programs -- what realisation selects away.
    SQL             the delivered structure (`specbridge.pd.realize.fidelity` features) against P.

    python -m specbridge.pd.realize.split <db> [<db> ...] [--n 300]
"""
from __future__ import annotations
import collections, math, random, re, sys, time

MODES = ("free", "undecided", "collapsed", "row")


def family(ctx, a):
    """The decision a context belongs to, for the report (never used to decide anything)."""
    if len(ctx) >= 7 and ctx[4] in MODES: return "expression %s" % ctx[0].split(":")[0]
    if ctx[:2] == ("QUERY", "steps"): return "steps list (%s)" % ctx[-1]
    if ctx[:2] in (("QUERY", "from"), ("JOIN", "rel")): return "relation"
    if ctx[0] == "QUERY" and len(ctx) > 2 and ctx[1] in ("joins", "where", "group", "select", "having", "order"): return "%s list" % ctx[1]
    if ctx[0] in ("REF", "STEP_OUT", "STEP_REL"): return "%s member" % ctx[0]
    return "%s %s" % ctx[:2]


def default_rule(ctx):
    """The rule behind a mask at a decision the checker does not itemise."""
    f = family(ctx, None)
    if f == "relation": return "D/feasibility: relation not linkable, or the step obligation"
    if f.endswith(" list") or f.startswith("steps list"): return "language/feasibility: list minimum, cap, owed step or item that cannot be filled"
    if ctx[:2] == ("QUERY", "limit"): return "language: LIMIT needs ORDER, or a step owes a cut"
    if ctx[0] in ("REF",): return "unattributed reuse"
    if ctx[0] in ("STEP_OUT", "STEP_REL"): return "language: a step output is introduced once, or its step is not in FROM"
    if len(ctx) == 3 and ctx[2] in ("UNIT_PARAM", "FORMULA_PARAM", "SCORE", "TOP_K", "PARAM"): return "language: constants carried by P are numbers"
    if ctx[:2] == ("AGG", "filter"): return "language: an item may not repeat an earlier one"
    if ctx[:2] == ("ARITH", "op"): return "feasibility: operator with no fillable left operand"
    if ctx[:2] == ("JOIN", "kind"): return "D: the join's kind follows its key link"
    return "language: %s %s" % ctx[:2]


def kind_of(rule):
    return rule.split(":")[0].split("/")[0].upper() if ":" in rule else "UNATTRIBUTED"


class Ledger:
    def __init__(self):
        self.removed = collections.Counter()        # rule -> probability mass removed (summed over decisions)
        self.logz = 0.0; self.decisions = 0; self.masked = 0
        self.chosen = collections.defaultdict(collections.Counter)   # family -> action -> count, all draws
        self.programs = 0

    def see(self, law, d, why, a):
        c = law.counts(d.ctx) or {}
        tot = sum(c.values())
        self.decisions += 1
        if tot and d.allow is not None:
            ok = d.allow if callable(d.allow) else (lambda x: x in d.allow)
            kept = sum(k for x, k in c.items() if ok(x))
            if kept < tot:
                self.masked += 1
                if kept: self.logz -= math.log(kept / tot)
                for x, k in c.items():
                    if not ok(x): self.removed[why.get(x) or default_rule(d.ctx)] += k / tot
        self.chosen[family(d.ctx, a)][a if not isinstance(a, (int, float)) or isinstance(a, bool) else "#"] += 1


from specbridge.pd.realize.sampler import PROJECTION as LAW, project as _project


def hierarchical(law, d, opts):
    return _project(law, d, opts)


def first_step(trace):
    """Did the draw's root query choose a step at its FIRST step decision? One decision per program."""
    for d, _w, a in trace:
        if d.ctx[:3] == ("QUERY", "steps", 0) and d.ctx[-1] == "ROOT": return a == "MORE"
    return False


def run(law, cat, n, rng, ledger, emitted_ledger, log, explain_n=10 ** 9):
    """Draws with the OPTIONAL policies off. Returns the correct executable programs, each with the policies it
    violates, the correctness failures, and per-draw step choice for every population."""
    from specbridge.pd.structures.actions import Decoder, _draw, NotInLanguage
    from specbridge.pd.structures import algebra
    from specbridge.pd.structures.algebra import Unsupported, emit
    from specbridge.pd.realize.catalogue import Binder
    from specbridge.pd.realize.generate import execute
    from specbridge.pd.realize.sampler import _p
    from specbridge.pd.realize import verify
    from specbridge.pd.realize.verify import judge, DeadEnd, policies
    algebra.ENFORCE_DISTINCT = False; verify.ENFORCE["duplicates"] = False
    fails, programs = collections.Counter(), []
    run.step_all, run.slow = [], []
    for i in range(n):
        binder = Binder(cat, rng) if cat else None
        trace = []
        box = []
        def choose(d):
            dec = box[0]
            opts, _ = _p(law, d.ctx, d.allow)
            if not opts: raise DeadEnd(d.ctx)
            opts = _project(law, d, opts)
            a = _draw(opts, rng)
            ledger.see(law, d, dec.last_why, a); trace.append((d, dict(dec.last_why), a))
            return a
        dec = Decoder(choose, law.caps, binder=binder, explain=i < explain_n); box.append(dec)
        dec.enforce_size = False
        seq = []
        t_draw = time.time()
        try:
            p = dec.program()
        except DeadEnd as e: run.step_all.append(first_step(trace)); fails["dead end at %s %s" % e.args[0][:2]] += 1; continue
        except (NotInLanguage, Unsupported) as e:
            run.step_all.append(first_step(trace)); fails["IR: " + re.sub(r"'s\d+'", "'s#'", str(e))[:60]] += 1; continue
        except Exception as e: run.step_all.append(first_step(trace)); fails["bug: %s" % type(e).__name__] += 1; continue
        finally:
            pass
        run.step_all.append(first_step(trace))
        seqd = [(d.ctx, a) for d, _w, a in trace]
        why = judge(p, seqd)
        if why: fails["verifier: " + why[:50]] += 1; continue
        if cat:
            status, _res = execute(cat.con, emit(p))
            if status != "ok": fails["timeout (3 s)" if status == "timeout" else "sqlite: " + str(_res)[:40]] += 1; continue
        if time.time() - t_draw > 10: run.slow.append((i, round(time.time() - t_draw, 1)))
        programs.append((p, policies(p, seqd, law.caps.get("size")), first_step(trace)))
        for d, w, a in trace: emitted_ledger.see(law, d, w, a)
    ledger.programs = n; emitted_ledger.programs = len(programs)
    return programs, fails


def tv(a, b):
    na, nb = sum(a.values()) or 1, sum(b.values()) or 1
    return 0.5 * sum(abs(a[k] / na - b[k] / nb) for k in set(a) | set(b))


def main(dbs, n=300, log=print):
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.realize.fidelity import features, compare
    from specbridge.pd.structures.sources import programs, typers
    R, T = programs("livesql"), typers("livesql"); law = fit(R, T)
    t0 = time.time()
    base, base_e = Ledger(), Ledger()
    P0, _f = run(law, None, n, random.Random(7), base, base_e, log)
    P_step = sum(run.step_all) / max(1, len(run.step_all))
    PF = [features(p) for p, _pol, _s in P0]
    log("P frozen (%d livesql programs). Reference: %d draws from P with no database, %d finished (%.0fs)." % (len(R), n, len(P0), time.time() - t0))
    log("Optional policies (size cap, duplicate rejection) are OFF while drawing; programs are classified against them afterwards.")
    for db in dbs:
        t1 = time.time()
        cat = Catalogue(db)
        L, LE = Ledger(), Ledger()
        progs, fails = run(law, cat, n, random.Random(11), L, LE, log)
        steps_all = run.step_all
        ok = [x for x in progs if not x[1]]
        log("\n" + "=" * 100 + "\n%s: %d draws from P_D; %d correct and executable; %d of those also pass both optional policies (%.0fs)" % (
            db, n, len(progs), len(ok), time.time() - t1))
        if run.slow: log("   draws over 10 s: %s" % run.slow)

        log("\n1. P -> P_D. P's probability on masked actions, SUMMED over a draw's ~%d decisions (not a percentage, not KL)" % (L.decisions // max(1, n)))
        log("   Kinds are kept apart; only rows marked D are the database's own. LANGUAGE, POLICY and UNATTRIBUTED are not.")
        log("   %-78s %8s %8s" % ("rule", db[:8], "no DB"))
        kinds = collections.Counter(); kinds0 = collections.Counter()
        for r, m in L.removed.items(): kinds[kind_of(r)] += m / n
        for r, m in base.removed.items(): kinds0[kind_of(r)] += m / n
        for k in sorted(set(kinds) | set(kinds0)): log("   %-78s %8.3f %8.3f" % ("[" + k + "]", kinds[k], kinds0[k]))
        for r, m in L.removed.most_common(12): log("   %-78s %8.3f %8.3f" % (r[:78], m / n, base.removed.get(r, 0) / n))
        log("   -log Z per draw %.2f (no DB %.2f)" % (L.logz / n, base.logz / n))

        log("\n2. P_D -> CORRECT SQL. Correctness failures (%d of %d draws):" % (n - len(progs), n))
        for f_, c in fails.most_common(): log("   %4d  %s" % (c, f_))

        log("\n3. OPTIONAL POLICIES: their selection effect on the correct programs (%d)" % len(progs))
        viol = collections.Counter(v for _p, pol, _s in progs for v in pol)
        log("   violate the size cap %d, violate duplicate rejection %d, violate either %d" % (viol["size"], viol["duplicate"], len(progs) - len(ok)))
        CF, OF = [features(p) for p, _pol, _s in progs], [features(p) for p, _pol, _s in ok]
        m = lambda F, k: sum(x[k] for x in F) / max(1, len(F))
        log("   %-12s %8s %10s %12s" % ("", "P", "correct", "+ policies"))
        for k in ("arith_depth", "size", "joins", "aggregates", "has_step", "has_arith", "has_case"):
            log("   %-12s %8.2f %10.2f %12.2f" % (k, m(PF, k), m(CF, k), m(OF, k)))

        log("\n4. STEPS, ONE STATISTIC IN EVERY POPULATION: the share of draws whose root chooses a step at its first step decision")
        log("   P, no database                        %.3f  (%d draws)" % (P_step, len(P0)))
        log("   P_D, all draws                        %.3f  (%d draws)" % (sum(steps_all) / max(1, len(steps_all)), len(steps_all)))
        log("   correct and executable                %.3f  (%d)" % (sum(s for _p, _pol, s in progs) / max(1, len(progs)), len(progs)))
        log("   correct and passing both policies     %.3f  (%d)" % (sum(s for _p, _pol, s in ok) / max(1, len(ok)), len(ok)))
        log("   (has_step on the same programs: %.3f and %.3f -- it can differ from the first-decision share only if a"
            " program's steps were all inlined)" % (m(CF, "has_step"), m(OF, "has_step")))


def compare_laws(dbs, n=300, log=print):
    """FLAT against HIERARCHICAL projection: same P, databases and seeds, optional policies off."""
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.realize.fidelity import features
    from specbridge.pd.structures.sources import programs, typers
    R, T = programs("livesql"), typers("livesql"); law = fit(R, T)
    LAW["mode"] = "flat"
    P0, _f = run(law, None, n, random.Random(7), Ledger(), Ledger(), log)
    PF = [features(p) for p, _pol, _s in P0]; P_step = sum(run.step_all) / max(1, len(run.step_all))
    m = lambda F, k: sum(x[k] for x in F) / max(1, len(F))
    pct = lambda F, k, q: sorted(x[k] for x in F)[int(q * (len(F) - 1))] if F else 0
    for db in dbs:
        cat = Catalogue(db); rows = {}
        for mode in ("flat", "hier"):
            LAW["mode"] = mode; LAW["cases"] = collections.Counter()
            t0 = time.time()
            progs, fails = run(law, cat, n, random.Random(11), Ledger(), Ledger(), log)
            dt = time.time() - t0
            F = [features(p) for p, _pol, _s in progs]
            rows[mode] = dict(ok=len(progs), fails=fails, F=F, step_all=sum(run.step_all) / max(1, len(run.step_all)),
                              step_ok=sum(s for _p, _pol, s in progs) / max(1, len(progs)), t=dt, slow=len(run.slow),
                              size_viol=sum(1 for _p, pol, _s in progs if "size" in pol), cases=dict(LAW["cases"]))
        log("\n" + "=" * 100 + "\n%s: %d draws each, optional policies off, same P and seeds" % (db, n))
        log("   %-38s %10s %10s %10s" % ("", "P (no DB)", "flat", "hierarch."))
        log("   %-38s %10s %10d %10d" % ("correct and executable", "", rows["flat"]["ok"], rows["hier"]["ok"]))
        for k, lab in (("size", "size, mean"), ("arith_depth", "arithmetic depth, mean"), ("joins", "joins, mean"),
                       ("aggregates", "aggregates, mean"), ("has_step", "has a step"), ("has_arith", "has arithmetic"), ("has_case", "has CASE")):
            log("   %-38s %10.2f %10.2f %10.2f" % (lab, m(PF, k), m(rows["flat"]["F"], k), m(rows["hier"]["F"], k)))
        log("   %-38s %10d %10d %10d" % ("size, 90th percentile", pct(PF, "size", .9), pct(rows["flat"]["F"], "size", .9), pct(rows["hier"]["F"], "size", .9)))
        log("   %-38s %10.3f %10.3f %10.3f" % ("step at first decision, all draws", P_step, rows["flat"]["step_all"], rows["hier"]["step_all"]))
        log("   %-38s %10s %10.3f %10.3f" % ("step at first decision, correct", "", rows["flat"]["step_ok"], rows["hier"]["step_ok"]))
        log("   %-38s %10s %10d %10d" % ("correct programs over R's size cap", "", rows["flat"]["size_viol"], rows["hier"]["size_viol"]))
        log("   %-38s %10s %10.2f %10.2f" % ("seconds per draw", "", rows["flat"]["t"] / n, rows["hier"]["t"] / n))
        log("   %-38s %10s %10d %10d" % ("draws over 10 s", "", rows["flat"]["slow"], rows["hier"]["slow"]))
        for mode in ("flat", "hier"):
            log("   %s failures: %s" % (mode, ", ".join("%s %d" % kv for kv in rows[mode]["fails"].most_common(5))))
        log("   hierarchical cases: %s" % rows["hier"]["cases"])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 300
    if "--compare" in sys.argv: compare_laws(args or ["california_schools"], n)
    else: main(args or ["california_schools"], n)
