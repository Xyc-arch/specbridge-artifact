"""specbridge.pd.realize.crossdb — ONE REPRODUCIBLE CROSS-DATABASE SQL-GENERATION RESULT. Unchanged code on every database.

    python -m specbridge.pd.realize.crossdb <db> [<db> ...] [--n 200] [--out out/crossdb]

Per database, in its own process (at most six at once): the frozen P (fitted on LiveSQLBench), the database's
saved semantic catalogue (`specbridge.pd.realize.semantic`; its version is recorded, and no model is called), `--n` attempts from a
fixed seed. Every attempt is appended to <out>/<db>.jsonl as it finishes. Then one report, <out>/REPORT.md:

    EXECUTION      verified and executable SQL / attempts, split by whether a step was drawn; failures by kind
    LATENCY        generation per attempt; generation and execution per executable query
    FIDELITY       structural features of the executable SQL against samples from P with no database, as total
                   variation (TV) and its ratio to the TV two independent batches from P show (the noise); a
                   proxy for how much of P survives, not a certificate
    MEANING        every node of every executable program, judged by the one checker's own walk
                   (`Semantics.nodes`): arithmetic by operand type, and every aggregate, function, cast and CASE, as
                   the share supported (strong: rows, documentation or a declared rule; plausible: a model's
                   proposal), unknown or contradicted; and how each arithmetic parameter's value was chosen
    USEFULNESS     measured apart from meaning (`verify.policies`): programs with a repeated operand or item, an
                   expression of constants only, or more decisions than any source program
    SAMPLES        random executable SQL per database
"""
from __future__ import annotations
import collections, json, os, random, subprocess, sys, time

FEATS = ("size", "arith_depth", "aggregates", "joins", "step_chain", "predicates", "has_case", "has_window", "has_subquery")
TIERS = ("supported, strong", "supported, plausible", "unknown", "contradicted")


def one(db, n, seed, out):
    """One database: every attempt appended to <out>/<db>.jsonl."""
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit
    from specbridge.pd.structures.algebra import emit
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.realize.fidelity import features
    from specbridge.pd.realize.generate import attempt, execute
    from specbridge.pd.realize.verify import policies
    from specbridge.pd.structures.sources import programs, typers
    law = fit(programs("livesql"), typers("livesql")); cat = Catalogue(db)
    rng = random.Random(seed)
    with open(os.path.join(out, db + ".jsonl"), "w") as f:
        f.write(json.dumps({"db": db, "catalogue": cat.catalogue_version, "n": n, "seed": seed}) + "\n")
        for i in range(n):
            t0 = time.time()
            p, verdict, binder = attempt(law, cat, rng, law.caps)
            tg = time.time() - t0
            step = any(c[:3] == ("QUERY", "steps", 0) and c[-1] == "ROOT" and a == "MORE" for c, a in attempt.seq)
            row = {"i": i, "verdict": verdict, "step": step, "gen": tg}
            if p is not None:
                sql = emit(p); t1 = time.time()
                status, res = execute(cat.con, sql)
                row.update(exec=time.time() - t1, status=status, sql=sql)
                if status == "ok":
                    row.update(features=features(p), nodes=dict(binder.node_report(p)), rows=len(res),
                               policies=policies(p, attempt.seq, law.caps.get("size")))
                else: row["error"] = str(res)[:80]
            f.write(json.dumps(row, default=str) + "\n"); f.flush()


def reference(n, out, reps=10):
    """Samples from P with no database, and the TV two independent P batches show: the noise floor."""
    import warnings; warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit
    from specbridge.pd.realize.fidelity import features, p_samples, compare
    from specbridge.pd.structures.sources import programs, typers
    law = fit(programs("livesql"), typers("livesql")); rng = random.Random(0)
    ref, _ = p_samples(law, n, rng)
    noise = collections.defaultdict(list)
    for _r in range(reps):
        a, _ = p_samples(law, n, rng); b, _ = p_samples(law, n, rng)
        for k, (t, _w) in compare([features(x) for x in a], [features(x) for x in b]).items(): noise[k].append(t)
    json.dump({"P": [features(p) for p in ref], "noise": {k: sum(v) / len(v) for k, v in noise.items()}},
              open(os.path.join(out, "reference.json"), "w"))


def _tier(verdict):
    for t in TIERS:
        if verdict.startswith(t): return t
    return "unknown"


def report(dbs, out, log=print):
    from specbridge.pd.realize.fidelity import compare
    ref = json.load(open(os.path.join(out, "reference.json")))
    PF, noise = ref["P"], ref["noise"]
    L = []
    w = L.append
    w("# Cross-database SQL generation\n")
    w("P frozen (fitted on LiveSQLBench's 107 programs), hierarchical projection, the same code on every database; "
      "each database's saved semantic catalogue, no model call at generation. Reproduce: `python -m specbridge.pd.realize.crossdb %s --n N`.\n" % " ".join(dbs))
    rows, meaning, fid, samples, fails, params, useful = [], {}, {}, {}, {}, {}, {}
    for db in dbs:
        lines = [json.loads(x) for x in open(os.path.join(out, db + ".jsonl"))]
        head, att = lines[0], lines[1:]
        n = len(att); ok = [a for a in att if a.get("status") == "ok"]
        st = [a for a in att if a["step"]]; st_ok = [a for a in st if a.get("status") == "ok"]
        gen = sum(a["gen"] for a in att) / max(1, n)
        per_ok = (sum(a["gen"] for a in att) + sum(a.get("exec", 0) for a in att)) / max(1, len(ok))
        rows.append((db, head["catalogue"] or "none", n, len(ok), len(st_ok), len(st), len(ok) - len(st_ok), n - len(st), gen, per_ok))
        f = collections.Counter()
        for a in att:
            if a.get("status") == "ok": continue
            v = a.get("error") and ("SQLite: " + a["error"][:40]) if a.get("status") not in (None, "ok", "timeout") else \
                "timeout" if a.get("status") == "timeout" else a["verdict"].split(":")[0] + ": " + ":".join(a["verdict"].split(":")[1:])[:60]
            f[v.strip()] += 1
        fails[db] = f
        EF = [a["features"] for a in ok]
        fid[db] = (compare(PF, EF), {k: sum(x[k] for x in EF) / max(1, len(EF)) for k in FEATS})
        m, kinds, use = collections.defaultdict(collections.Counter), collections.Counter(), collections.Counter()
        for a in ok:
            for k, v in a["nodes"].items():
                cls, _, rest = k.partition(" | ")
                m[cls][_tier(rest)] += v
                if cls == "operand and parameter": kinds[k.split(" | ")[-1]] += v
            for pol in a.get("policies", []): use[pol] += 1
        meaning[db] = m; params[db] = kinds; useful[db] = (use, len(ok))
        samples[db] = random.Random(2).sample(ok, min(3, len(ok)))
    w("## Execution and latency\n")
    w("| database | catalogue | attempts | executable | with a step | without a step | generation per attempt | per executable query |")
    w("|---|---|---|---|---|---|---|---|")
    for db, cv, n, e, se, sn, pe, pn, gen, per in rows:
        w("| %s | %s | %d | %d (%.0f%%) | %d / %d | %d / %d | %.2f s | %.2f s |" % (db, cv, n, e, 100 * e / max(1, n), se, sn, pe, pn, gen, per))
    w("\n## Failures\n")
    for db in dbs:
        w("- **%s**: %s" % (db, "; ".join("%s %d" % (k, v) for k, v in fails[db].most_common(6))))
    w("\n## Structural fidelity of executable SQL against P\n")
    w("Total variation (TV) against samples from P with no database, and its multiple of the TV between two P batches of the same size.\n")
    w("| feature | noise | " + " | ".join(dbs) + " |")
    w("|---|---|" + "---|" * len(dbs))
    for k in FEATS:
        w("| %s | %.3f | " % (k, noise.get(k, 0)) + " | ".join("%.3f (%.1fx)" % (fid[db][0][k][0], fid[db][0][k][0] / noise[k] if noise.get(k) else 0) for db in dbs) + " |")
    w("\nMeans: P against each database.\n")
    w("| feature | P | " + " | ".join(dbs) + " |")
    w("|---|---|" + "---|" * len(dbs))
    for k in FEATS:
        w("| %s | %.2f | " % (k, sum(x[k] for x in PF) / len(PF)) + " | ".join("%.2f" % fid[db][1][k] for db in dbs) + " |")
    w("\n## Meaning, judged by the one checker\n")
    w("Every node of every executable program, by the checker's own walk: the final check's verdicts, reported. "
      "Arithmetic by what its operands are; every other operator by its constructor. Shares within each row.\n")
    classes = ["operand and parameter", "two quantities", "a derived operand", "a constant under a cast or function",
               "agg", "func", "cast", "case", "window"]
    for cls in classes:
        w("\n**%s**\n" % cls)
        w("| database | nodes | " + " | ".join(TIERS) + " |")
        w("|---|---|" + "---|" * len(TIERS))
        for db in dbs:
            c = meaning[db].get(cls, collections.Counter()); tot = sum(c.values())
            w("| %s | %d | " % (db, tot) + " | ".join("%.0f%%" % (100 * c[t] / tot) if tot else "-" for t in TIERS) + " |")
    w("\n## How arithmetic parameters were chosen\n")
    w("Each parameter's kind (P's decision) and the rule that bound its value on the target. Counts of nodes.\n")
    allk = sorted({k for db in dbs for k in params[db]}, key=lambda k: -sum(params[db][k] for db in dbs))
    w("| kind: how its value was chosen | " + " | ".join(dbs) + " |")
    w("|---|" + "---|" * len(dbs))
    for k in allk: w("| %s | " % k + " | ".join(str(params[db][k]) for db in dbs) + " |")
    w("\n## Usefulness, measured apart from meaning\n")
    w("Share of executable programs a declared usefulness policy would flag. None is enforced in this baseline.\n")
    w("| policy | " + " | ".join(dbs) + " |")
    w("|---|" + "---|" * len(dbs))
    for pol, what in (("duplicate", "a repeated operand (x - x, x / x), CASE condition, AND/OR branch or list item"),
                      ("uninformative", "a cast, function or aggregate of constants only"),
                      ("size", "more decisions than any source program")):
        w("| %s: %s | " % (pol, what) + " | ".join("%.0f%%" % (100 * useful[db][0][pol] / max(1, useful[db][1])) for db in dbs) + " |")
    w("\n## Random executable SQL\n")
    for db in dbs:
        w("\n**%s**\n" % db)
        for a in samples[db]:
            w("```sql\n%s\n```" % (a["sql"][:700] + (" ..." if len(a["sql"]) > 700 else "")))
    text = "\n".join(L)
    open(os.path.join(out, "REPORT.md"), "w").write(text)
    log(text)


def main(dbs, n=200, out="out/crossdb", jobs=6, log=print):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    todo = [["reference", str(n), out]] + [["one", db, str(n), "11", out] for db in dbs]
    running = []
    for args in todo:
        while len([p for p in running if p.poll() is None]) >= jobs: time.sleep(2)
        running.append(subprocess.Popen([sys.executable, "-m", "specbridge.pd.realize.crossdb"] + args, stderr=open(os.path.join(out, args[1] + ".err"), "w")))
    for p in running: p.wait()
    log("all runs finished in %.0fs" % (time.time() - t0))
    report(dbs, out, log)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "one": one(a[1], int(a[2]), int(a[3]), a[4]); sys.exit()
    if a and a[0] == "reference": reference(int(a[1]), a[2]); sys.exit()
    if a and a[0] == "report":
        b = a[1:]
        report([x for i, x in enumerate(b) if not x.startswith("--") and not (i and b[i - 1].startswith("--"))],
               b[b.index("--out") + 1] if "--out" in b else "out/crossdb"); sys.exit()
    opts = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
    dbs = [x for i, x in enumerate(a) if not x.startswith("--") and not (i and a[i - 1].startswith("--"))]
    main(dbs, int(opts.get("--n", 200)), opts.get("--out", "out/crossdb"))
