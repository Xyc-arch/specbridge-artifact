"""specbridge.pd.realize.generate — GROUNDED SQL ON A TARGET DATABASE, WITH P FROZEN. English is deferred.

Fit P on the source; catalogue the target; decode with P restricted by the checker and the binder; compile;
verify; execute. Every attempt is appended to out/<db>/rows.jsonl as it finishes, with its verdict, so a
run is readable while it runs and a rejection is never silent.

    verdicts   valid | invalid: <why> (the language, the IR or the judge refused it) | bug: <why> (an
               implementation error, never relabelled) | timeout | policy: <why> (a benchmark policy on the answer)
    evidence   per row, how many arithmetic and aggregate bindings were SUPPORTED by the catalogue and how many
               were UNKNOWN (allowed, stated literally)

    python -m specbridge.pd.realize.generate <db> [n] [source] [--no-probes]

The report is five measures and nothing else: executable queries per attempt; failure categories; proposed
against emitted structure; supported against unknown bindings under arithmetic; generation against
execution time. An empty answer is reported separately and does not make a query invalid.
"""
from __future__ import annotations
import collections, json, os, random, re, sys, time


MODES = ("free", "undecided", "collapsed", "row")


def mass(law, d, stats, key):
    """At an expression decision: the share of P's probability on compounds before and after the mask."""
    from specbridge.pd.structures.actions import COMPOUND
    ctx = d.ctx
    if not (len(ctx) >= 7 and ctx[4] in MODES) or d.allow is None or callable(d.allow): return
    c = law.counts(ctx) or {}
    tot = sum(c.values())
    if not tot: return
    allowed = {a: k for a, k in c.items() if a in d.allow}
    at = sum(allowed.values())
    stats[key + "_n"] += 1
    stats[key + "_pre"] += sum(k for a, k in c.items() if a in COMPOUND) / tot
    if at: stats[key + "_post"] += sum(k for a, k in allowed.items() if a in COMPOUND) / at
    stats[key + "_leafmask"] += sum(k for a, k in c.items() if a not in COMPOUND and a not in d.allow) / tot


def attempt(law, cat, rng, caps, probes=True, stats=None):
    from specbridge.pd.structures.actions import Decoder, _draw
    from specbridge.pd.realize.catalogue import Binder
    from specbridge.pd.realize.sampler import _p
    from specbridge.pd.realize.verify import interpret, judge, DeadEnd
    binder, seq = Binder(cat, rng, probes), []
    attempt.seq = seq
    from specbridge.pd.realize.sampler import project
    def choose(d):
        if stats is not None: mass(law, d, stats, "db")
        opts, _ = _p(law, d.ctx, d.allow)
        if not opts: raise DeadEnd(d.ctx)
        opts = project(law, d, opts)                      # the projection law (hierarchical by default)
        a = _draw(opts, rng); seq.append((d.ctx, a)); return a
    from specbridge.pd.realize.verify import _Stop
    import traceback
    from specbridge.pd.structures.actions import NotInLanguage, CheckerBug
    from specbridge.pd.structures.algebra import Unsupported
    try:
        p = Decoder(choose, caps, binder=binder).program()
    except DeadEnd as e: return None, "invalid: dead end at %s" % (e.args[0][:2],), binder
    except (NotInLanguage, Unsupported) as e: return None, "invalid: %s" % str(e)[:80], binder
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return None, "bug: %s at %s:%d: %s" % (type(e).__name__, tb.filename.split("/")[-1], tb.lineno, str(e)[:80]), binder
    why = judge(p, seq)
    if why is None and cat is not None:
        bad = cat.sem.check(p)                                # the one checker, over the finished program
        if bad: why = "meaning: refused (%s %s, %s)" % bad[0]
    return (p, "valid", binder) if why is None else (None, "invalid: " + why, binder)


def execute(con, sql, ms=3000):
    t0 = time.time()
    con.set_progress_handler(lambda: 1 if (time.time() - t0) * 1000 > ms else 0, 10000)
    try:
        cur = con.execute(sql); rows = cur.fetchmany(1001)
        return "ok", rows
    except Exception as e:
        return ("timeout" if "interrupt" in str(e).lower() else "error"), str(e)[:100]
    finally:
        con.set_progress_handler(None, 0)


def p_only_mass(law, n, rng):
    """The same measure with no database: structural masks only."""
    from specbridge.pd.structures.actions import Decoder, _draw
    from specbridge.pd.realize.sampler import _p
    stats = collections.Counter()
    for _ in range(n):
        def choose(d):
            mass(law, d, stats, "p")
            opts, _ = _p(law, d.ctx, d.allow)
            if not opts: raise RuntimeError("dead")
            return _draw(opts, rng)
        try: Decoder(choose, law.caps).program()
        except Exception: pass
    return stats


def main(db="california_schools", n=200, source="livesql", out="out", probes=True, log=print, show=3):
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit
    from specbridge.pd.structures.algebra import emit
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.structures.sources import programs, typers
    t0 = time.time()
    R, T = programs(source), typers(source); law = fit(R, T)
    cat = Catalogue(db)
    log("P frozen: fitted on %d %s programs; %s catalogued (%d tables); %.1fs" % (len(R), source, db, len(cat.world.rel), time.time() - t0))
    os.makedirs("%s/%s" % (out, db), exist_ok=True)
    rng = random.Random(0); stats = collections.Counter(); ev_total = collections.Counter(); grain_attempts = 0
    out_counts = collections.Counter(); fails = collections.Counter(); samples = []
    tgen = texe = 0.0
    with open("%s/%s/sql.jsonl" % (out, db), "w") as f:
        for i in range(n):
            t1 = time.time()
            p, verdict, binder = attempt(law, cat, rng, law.caps, probes, stats)
            if p is not None: ev_total.update(binder.node_report(p))     # read off the finished program: the verifier's walk
            grain_attempts += binder.grain_hits > 0
            tgen += time.time() - t1
            step = any(c[:3] == ("QUERY", "steps", 0) and c[-1] == "ROOT" and a == "MORE" for c, a in attempt.seq)
            kind = "step" if step else "plain"
            out_counts[kind + "_attempts"] += 1
            row = {"i": i, "verdict": verdict, "step": step}
            if p is not None:
                sql = emit(p); t2 = time.time()
                status, res = execute(cat.con, sql); texe += time.time() - t2
                row["sql"] = sql
                if status == "ok":
                    out_counts[kind + "_executable"] += 1; out_counts["empty"] += not res
                    row.update(rows=len(res), answer=[list(r) for r in res[:3]], bindings=binder.log)
                    if len(samples) < 40: samples.append(row)
                elif status == "timeout": fails["timeout (3 s)"] += 1
                else: fails["sqlite error: " + str(res)[:50]] += 1
            elif "dead end" in verdict: fails["dead end at " + verdict.split(" at ")[-1][:30]] += 1
            elif "longer than" in verdict: fails["size cap from R"] += 1
            else: fails[re.sub(r"[\d.]+", "#", verdict)[:70]] += 1
            f.write(json.dumps(row, default=str) + "\n"); f.flush()
    ex = out_counts["step_executable"] + out_counts["plain_executable"]
    log("\nEXECUTABLE / ATTEMPTS   %d / %d (%.0f%%)" % (ex, n, 100 * ex / n))
    log("   with a step      %d / %d" % (out_counts["step_executable"], out_counts["step_attempts"]))
    log("   without a step   %d / %d" % (out_counts["plain_executable"], out_counts["plain_attempts"]))
    log("   empty answers (reported, not failures): %d" % out_counts["empty"])
    log("\nFAILURES")
    for k in ("dead end", "size cap", "timeout"):
        tot = sum(v for f_, v in fails.items() if f_.startswith(k))
        log("   %-10s %d" % (k, tot))
    for f_, v in fails.most_common():
        if not f_.startswith(("dead end", "size cap", "timeout")): log("   %-10s %d  %s" % ("other", v, f_))
    log("   dead ends by decision: " + ", ".join("%s %d" % (f_[12:], v) for f_, v in fails.most_common() if f_.startswith("dead end")))
    log("\nTIME   generation %.0f ms per attempt; %.0f ms per executable query, generation and execution together" % (
        1000 * tgen / n, 1000 * (tgen + texe) / max(1, ex)))
    pm = p_only_mass(law, 200, random.Random(5))
    log("\nGRAIN: attempts in which the grain rule excluded a column under SUM, AVG or COUNT: %d of %d" % (grain_attempts, n))
    log("\nOPERATOR NODES in verified programs, by what the operands are; the verdict and the evidence it rests on:")
    groups = collections.defaultdict(collections.Counter)
    for k, v in ev_total.items(): cls, _, rest = k.partition(" | "); groups[cls][rest] += v
    for cls in sorted(groups, key=lambda c: -sum(groups[c].values())):
        tot = sum(groups[cls].values())
        log("   %-34s %5d" % (cls, tot))
        for k, v in groups[cls].most_common(): log("      %5d  %5.1f%%  %s" % (v, 100 * v / tot, k))
    log("\nWHY SIZE GROWS UNDER MASKS: at expression decisions, P's probability on compounds")
    log("   no database:     before mask %.3f   after mask %.3f   leaf mass masked %.3f   (%d decisions)" % (
        pm["p_pre"] / max(1, pm["p_n"]), pm["p_post"] / max(1, pm["p_n"]), pm["p_leafmask"] / max(1, pm["p_n"]), pm["p_n"]))
    log("   on %-12s before mask %.3f   after mask %.3f   leaf mass masked %.3f   (%d decisions)" % (
        db, stats["db_pre"] / max(1, stats["db_n"]), stats["db_post"] / max(1, stats["db_n"]), stats["db_leafmask"] / max(1, stats["db_n"]), stats["db_n"]))
    log("\nSAMPLE SQL WITH ITS BINDINGS")
    for r in random.Random(2).sample(samples, min(show, len(samples))):
        log("\n  %s query, %d rows" % ("step" if r["step"] else "plain", r["rows"]))
        log("  SQL: %s" % (r["sql"][:600] + (" ..." if len(r["sql"]) > 600 else "")))
        for what, to, why in r["bindings"][:10]: log("     %-44s -> %-34s %s" % (str(what)[:44], str(to)[:34], why))
        if len(r["bindings"]) > 10: log("     ... %d more bindings" % (len(r["bindings"]) - 10))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "california_schools", int(sys.argv[2]) if len(sys.argv) > 2 else 200,
         sys.argv[3] if len(sys.argv) > 3 else "livesql", probes="--no-probes" not in sys.argv)
