"""WHAT THE FAST PATH ACTUALLY DELIVERS: fixed intents against the reviewed pools, with latency, delivered count, quality
tier, deviation from intent and every shortfall reason side by side.
    python -m specbridge.comm.construct.research.serve_eval [db ...]      -> out/serve/EVAL.md"""
import json, sys, time
from specbridge.comm.construct.serve import serve

INTENTS = [("shallow x20", {"target": {"preset": "shallow"}, "count": 20}),
           ("medium x20", {"target": {"preset": "medium"}, "count": 20}),
           ("deep x20", {"target": {"preset": "deep"}, "count": 20}),
           ("very deep x20", {"target": {"preset": "very deep"}, "count": 20}),
           ("deep x20, no substitution", {"target": {"preset": "deep"}, "count": 20, "substitute": False}),
           ("deep x20, moves up to 2", {"target": {"preset": "deep"}, "count": 20, "max_move": {"arith": 2, "steps": 2}}),
           ("deep x20, exploratory", {"target": {"preset": "deep"}, "count": 20, "standard": "exploratory"}),
           ("medium x20, analyst", {"target": {"preset": "medium"}, "count": 20, "standard": "analyst"}),
           ("medium x20, strict", {"target": {"preset": "medium"}, "count": 20, "standard": "strict"}),
           ("medium x20, no diversity cap", {"target": {"preset": "medium"}, "count": 20, "max_share_per_quantity": 1.0})]


def run(dbs):
    L = ["# What the fast path delivers (reviewed pools, no model calls)\n",
         "Default standard: benchmark (coherent meaning and a determined answer, rubric v1.1, both reviewers); complexity not assessed, so strict returns nothing. A substituted task may move at most 1 arithmetic level and 1 step; no base quantity in more "
         "than 20% of the tasks. 'dev' = mean |dA| / mean |dS| over delivered tasks.\n",
         "| database | intent | ms | delivered / asked | exact cells | dev A / S | unique computations | short: no stock nearby | short: diversity cap | more under exploratory |", "|---|---|---|---|---|---|---|---|---|---|"]
    for db in dbs:
        for name, it in INTENTS:
            it = dict(it, db=db, seed=42); t0 = time.time(); tasks, fresh, r = serve(it); ms = 1000 * (time.time() - t0)
            d = r["deviation"]
            L.append("| %s | %s | %.0f | %d / %d | %d | %s | %s | %d | %d | %d |" % (db, name, ms, len(tasks), it["count"], d.get("exact", 0),
                     "%.2f / %.2f" % (d["mean_dA"], d["mean_dS"]) if d.get("tasks") else "-", r["unique_computations"], sum(r["shortfall"].values()),
                     sum(r["diversity_shortfall"].values()), sum(r["more_under_exploratory"].values())))
    open("out/serve/EVAL.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    run(sys.argv[1:] or ["student_club", "financial", "formula_1", "sakila_1", "soccer_1", "college_2"])
