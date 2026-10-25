"""AMBIQT-STYLE SCORING ON SPECBRIDGE ITEMS (2026-10-12, reviewer point). AmbiQT counts an ambiguous question as handled when both
readings appear among a model's top-k SQL outputs (k = 5). Here each solver answers the OPEN request of a random subset of request sets
K times with the plain single call (disclose.PLAIN: same schema, documentation and request, SQL only, no exploration). Sample 1 is the
saved plain run (<disclose>/plain/<model>/); samples 2..K are new calls of the same prompt. The sampled score is then set against the
SpecBridge measures on the same sets: names the choice (Opus judge) and returns both readings in the explanation call.
    python -m specbridge.comm.transfer.topk run [<model> ...]   -> <disclose>/topk/<model>/<case>__s<k>.json
    python -m specbridge.comm.transfer.topk report               -> <disclose>/topk/RESULTS.md, results.json
A failed call (empty reply) is not saved, so a rerun asks again. At most 6 workers (machine rule)."""
import concurrent.futures as cf, json, os, random, sys, time
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X, combined as CB

D = CB.D; MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]; N, K, SEED = 60, 5, 20261012


def _f(out, m, k, s): return "%s/topk/%s/%s__s%d.json" % (out, m, k.replace(":", "__").replace("/", "_"), s)
def _plain(out, m, k): return "%s/plain/%s/%s__open.json" % (out, m, k.replace(":", "__").replace("/", "_"))


def subset():
    """N sets drawn from the first construction run (as first run), extended to the combined collection at the same rate."""
    S = json.load(open(X._paths(CB.PARTS[0])[2] + "/sample.json"))
    return CB.extend(random.Random(SEED).sample(sorted(S["cases"]), N), SEED)


def run(models, workers=6):
    from specbridge.comm.common.llm import call, parse
    fz, wr, out = X._paths(D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr))
    def one(job):
        k, m, s = job; f = _f(out, m, k, s)
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); t0 = time.time(); txt = call(X.PLAIN % (schema, docs, W[k]["open"]), m)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; prim = r.get("sql"); a = DB.rows(DB.connect(c["snapshot"]), prim) if prim else None
        o = {"case": k, "sample": s, "model": m, "response": r, "primary_executes": a is not None, "primary_matches": X._match(c, a), "seconds": round(time.time() - t0, 1)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    jobs = [(k, m, s) for k in subset() for m in models for s in range(2, K + 1)]
    random.Random(SEED + 1).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for n, _ in enumerate(ex.map(one, jobs), 1):
            if n % 200 == 0: print("done %d/%d" % (n, len(jobs)), flush=True)
    open(out + "/topk/run.done", "w").write("ok\n")


def report():
    from specbridge.comm.transfer import reviewed as RV
    fz, _wr, out = X._paths(D); J = json.load(open(out + "/judge.json")); ks = RV.accepted(subset()); res = {"n_sets": len(ks), "k": K, "models": {}}
    def load(p):
        o = {}
        for f in os.listdir(p):
            x = json.load(open(os.path.join(p, f))); o[(x["case"], x["wording"])] = x
        return o
    L = ["# AmbiQT-style sampled coverage vs SpecBridge measures (`specbridge.comm.transfer.topk`)\n",
         "%d request sets drawn at random (seed %d) from the 215; each solver answers the open request %d times with the plain single call "
         "(SQL only). Sets with all %d samples saved.\n" % (N, SEED, K, K),
         "| solver | sets | top-1 returns a reading | top-%d: both readings sampled | explanation call: both returned | names the choice | both sampled, choice never named | named, but one reading only in the explanation call |" % K,
         "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        Dm = load(out + "/" + m); rows = []
        for k in ks:
            fs = [_plain(out, m, k)] + [_f(out, m, k, s) for s in range(2, K + 1)]
            if not all(os.path.exists(f) for f in fs): continue
            got = [set(json.load(open(f))["primary_matches"]) for f in fs]
            o = Dm[(k, "open")]; cov = {"A", "B"} <= set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]}
            rec = (J.get("%s|open|%s" % (k, m)) or {}).get("flags_decision") is True
            rows.append({"case": k, "top1": bool(got[0]), "topk": {"A", "B"} <= set().union(*got), "explain_cover": cov, "names": rec,
                         "distinct_readings_per_sample": [sorted(g) for g in got]})
        n = len(rows); c = lambda key: sum(r[key] for r in rows)
        sampled_unnamed = sum(r["topk"] and not r["names"] for r in rows); named_one = sum(r["names"] and not r["explain_cover"] for r in rows)
        res["models"][m] = {"n": n, "top1": c("top1"), "topk": c("topk"), "explain_cover": c("explain_cover"), "names": c("names"),
                            "topk_not_named": sampled_unnamed, "named_not_covered": named_one, "rows": rows}
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d |" % (m, n, c("top1"), c("topk"), c("explain_cover"), c("names"), sampled_unnamed, named_one))
    rank = lambda key: [m for m in sorted(res["models"], key=lambda m: -res["models"][m][key] / max(1, res["models"][m]["n"]))]
    res["ranking"] = {key: rank(key) for key in ("topk", "explain_cover", "names")}
    L += ["", "Ranking by top-%d coverage: %s" % (K, " > ".join(res["ranking"]["topk"])),
          "Ranking by both readings returned in the explanation call: %s" % " > ".join(res["ranking"]["explain_cover"]),
          "Ranking by naming the choice: %s" % " > ".join(res["ranking"]["names"])]
    json.dump(res, open(out + "/topk/results.json", "w"), indent=1); open(out + "/topk/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: run(sys.argv[2:] or MODELS), "report": report}[sys.argv[1]]()
