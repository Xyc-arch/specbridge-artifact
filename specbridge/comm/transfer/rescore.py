"""WHAT DOES A BENCHMARK SCORE MISS? (2026-10-25; protocol out/rescore/PROTOCOL.md, written before the run.)
On the BIRD dev questions of the simulated-clarification study (out/rewrite/bird/items.json: one library edit of the reference SQL
changes the answer, degenerate edits excluded), each solver answers the ORIGINAL question + evidence once, with the same plain SQL
prompt and schema as that study. Each answer is executed and compared (BIRD execution match) with the reference (reading A, what
BIRD scores) and with the edited reference (reading B, the unstated other reading). Boundary and missing-value items are left out:
"over"/"under" settle a bound, and the missing-value edits were defective (out/rewrite/bird/GATE.md).
Author review (human_supervision/bird-other-reading.csv): every question on which some answer matched only the edited reference was
read; a question whose edited reference the author rejects ("no") is left out of every count.
    python -m specbridge.comm.transfer.rescore run | report   -> out/rescore/runs/<model>/<id>.json, RESULTS.md, results.json"""
import concurrent.futures as cf, json, os, random, sys
from specbridge.comm.transfer import disclose as X
from specbridge.comm.transfer.rewrite import _schema

REVIEW = "human_supervision/bird-other-reading.csv"
OUT = "out/rescore"; MODELS = ("haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"); SEED = 20261025; TYPES = ("ties", "count_unit", "join_kind")


def items():
    from specbridge.comm.diagnose.rules import edit_ok
    return [it for it in json.load(open("out/rewrite/bird/items.json")) if it["rule"] in TYPES and edit_ok(it)]


def run(models=MODELS, workers=6):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    from specbridge.comm.common import grade as G
    from specbridge.report import impact as IM
    jobs = [(m, it) for it in items() for m in models]; random.Random(SEED).shuffle(jobs)
    def one(j):
        m, it = j; f = "%s/runs/%s/%s.json" % (OUT, m, it["id"])
        if os.path.exists(f): return
        gA = IM.run(it["path"], it["gold0"], limit=60); gB = IM.run(it["path"], it["gold"], limit=60)
        if gA is None or gB is None:
            with open(OUT + "/skipped.txt", "a") as fh: fh.write("%s %s gold timed out\n" % (m, it["id"]))
            return
        q0 = it["question"] + ("\nEvidence: " + it["evidence"] if it["evidence"] else "")
        try: sql = (jparse(ask(X.PLAIN % (_schema(it["path"]), "", q0), m, timeout=1500, quiet=True) or "", "{") or {}).get("sql")
        except Exception: sql = None
        rows = IM.run(it["path"], sql) if sql else None
        out = {"id": it["id"], "db": it["db"], "rule": it["rule"], "model": m, "sql": sql, "runs": rows is not None,
               "A": rows is not None and G.bird_ex(gA, rows), "B": rows is not None and G.bird_ex(gB, rows)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(out, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    open(OUT + "/DONE", "w").write("done\n"); report(models)


def rejected():
    import csv
    return sorted(r["id"] for r in csv.DictReader(open(REVIEW)) if r["valid_other_reading (yes/no)"].strip().lower() == "no")


def report(models=MODELS):
    import glob
    no = set(rejected())
    keep = {it["id"] for it in items()}
    R = {m: [o for o in (json.load(open(f)) for f in sorted(glob.glob("%s/runs/%s/*.json" % (OUT, m)))) if o["id"] in keep and o["id"] not in no] for m in models}
    def stats(rs):
        n = len(rs); a = sum(r["A"] for r in rs); b = sum(r["B"] and not r["A"] for r in rs)
        return {"n": n, "A": a, "B_only": b, "either": a + b, "runs": sum(r["runs"] for r in rs),
                "wrong_by_bird": n - a, "B_share_of_wrong": b / max(1, n - a), "B_share_of_reading": b / max(1, a + b)}
    res = {"models": {m: stats(R[m]) for m in models}, "pooled": stats([r for m in models for r in R[m]]),
           "by_type_pooled": {t: stats([r for m in models for r in R[m] if r["rule"] == t]) for t in TYPES},
           "by_type": {m: {t: stats([r for r in R[m] if r["rule"] == t]) for t in TYPES} for m in models},
           "rejected_by_author": sorted(no), "rejected_by_rule": sorted({os.path.basename(f)[:-5] for f in glob.glob(OUT + "/runs/haiku/*.json")} - keep), "questions": len({r["id"] for m in models for r in R[m]}),
           "all_models_other": sorted({r["id"] for m in models for r in R[m]
                                       if all(any(o["id"] == r["id"] and o["B"] and not o["A"] for o in R[mm]) for mm in models)})}
    import csv
    from specbridge.comm.diagnose.rules import edit_ok
    I = {it["id"]: it for it in json.load(open("out/rewrite/bird/items.json"))}
    V = {r["id"]: r["valid_other_reading (yes/no)"].strip().lower() == "yes" for r in csv.DictReader(open(REVIEW))}
    res["rule_vs_author"] = {"verdicts": len(V), "agree": sum(edit_ok(I[k]) == v for k, v in V.items())}
    json.dump(res, open(OUT + "/results.json", "w"), indent=1)
    L = ["# BIRD scored with both readings (protocol: out/rescore/PROTOCOL.md)\n",
         "| model | questions | right by BIRD (A) | other reading only (B) | either | B of answers BIRD marks wrong | B of answers giving a reading |", "|---|---|---|---|---|---|---|"]
    for name, s in list(res["models"].items()) + [("pooled", res["pooled"])]:
        L.append("| %s | %d | %d (%.1f%%) | %d | %d (%.1f%%) | %.1f%% | %.1f%% |" % (name, s["n"], s["A"], 100 * s["A"] / max(1, s["n"]), s["B_only"],
                 s["either"], 100 * s["either"] / max(1, s["n"]), 100 * s["B_share_of_wrong"], 100 * s["B_share_of_reading"]))
    L += ["", "By choice type (pooled): " + "; ".join("%s n=%d A %d B-only %d" % (t, s["n"], s["A"], s["B_only"]) for t, s in res["by_type_pooled"].items())]
    open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
