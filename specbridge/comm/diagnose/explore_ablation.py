"""DOES DATABASE EXPLORATION CHANGE THE RESULT? The BIRD held-out confirmation questions, original question and explicit V,
answered with exploration OFF (rounds=1: the first reply must be FINAL), compared question by question with the saved runs that
allowed exploration (rounds=6). Same solver, prompt, limits and grading otherwise.
    python -m specbridge.comm.diagnose.explore_ablation run <model>      -> out/confirmation/bird_heldout100/runs_noexplore/<model>/<arm>/
    python -m specbridge.comm.diagnose.explore_ablation report <model>   -> .../runs_noexplore/<model>/RESULTS.md"""
import json, os, re, sys
from math import comb
from specbridge.comm.common import db as DB, grade as G
from specbridge.comm.common.solve import solve
D = "out/confirmation/bird_heldout100"
tasks = lambda arm: {t["id"]: t for t in map(json.loads, open("%s/tasks_%s.jsonl" % (D, arm)))}
mdir = lambda m: re.sub(r"\W", "_", m)


def run(model):
    for arm in ("original", "explicit"):
        T = tasks(arm); out = "%s/runs_noexplore/%s/%s" % (D, mdir(model), arm)
        res = solve([{"key": k, "text": t["instruction"], "snapshot": t["snapshot"], "database": t["database"]} for k, t in T.items()], model, out, bsize=1, rounds=1)
        for k, o in res.items():
            a = o.get("answer")
            if a is None and o.get("final"):
                a = DB.rows(DB.connect(T[k]["snapshot"]), o["final"])
                if a is not None: o.update(answer=a, executes=True)
            o["pass"] = a is not None and G.bird_ex(T[k]["reference_answer"], a); o["shape"] = a is not None and G.shape_tolerant(T[k]["reference_answer"], a)
            json.dump(o, open("%s/%s.json" % (out, k), "w"), default=str)


def report(model):
    mcn = lambda u, d: min(1.0, 2 * sum(comb(u + d, i) for i in range(min(u, d) + 1)) / 2 ** (u + d)) if u + d else 1.0
    L = ["# Exploration ablation, BIRD held-out (%s)\n" % model, "| request | n | with exploration | without | right only with | right only without | McNemar p |", "|---|---|---|---|---|---|---|"]
    out = {}
    for arm in ("original", "explicit"):
        T = tasks(arm); w, wo = [], []
        for k, t in T.items():
            f1 = "%s/runs/%s/%s_rep0/%s.json" % (D, mdir(model), arm, k); f0 = "%s/runs_noexplore/%s/%s/%s.json" % (D, mdir(model), arm, k)
            if os.path.exists(f1) and os.path.exists(f0):
                o1, o0 = json.load(open(f1)), json.load(open(f0))
                a1 = o1.get("answer"); w.append(bool(o1.get("pass"))); wo.append(bool(o0.get("pass")))
        n = len(w); up = sum(a and not b for a, b in zip(w, wo)); dn = sum(b and not a for a, b in zip(w, wo))
        out[arm] = {"n": n, "with": sum(w), "without": sum(wo), "only_with": up, "only_without": dn, "p": mcn(up, dn)}
        L.append("| %s | %d | %d | %d | %d | %d | %.2g |" % ("original question" if arm == "original" else "explicit V", n, sum(w), sum(wo), up, dn, mcn(up, dn)))
    base = "%s/runs_noexplore/%s" % (D, mdir(model)); json.dump(out, open(base + "/results.json", "w"), indent=1)
    open(base + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: run(sys.argv[2]), "report": lambda: report(sys.argv[2])}[sys.argv[1]]()
