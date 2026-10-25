"""REMAINING DISAGREEMENT after single-task judging, on a small FIXED sample: 4 packaged tasks per database (seeded), each
judged 3 times by the veto and 3 times by the auditor, uncached. The decision flip rate is the noise margin the adaptation
procedure's acceptance rule uses (specbridge.comm.construct.research.adapt).
    python -m specbridge.comm.construct.research.recheck   -> out/recheck/RECHECK.md, recheck.json"""
import collections, json, os, random
from specbridge.comm.construct.research.veto import recheck
from specbridge.comm.construct.research.filtered import audit

SOURCES = {"financial": "out/filtered/financial/frozen.jsonl", "student_club": "out/filtered/student_club/frozen.jsonl",
           "formula_1": "out/filtered/formula_1/frozen.jsonl", "sakila_1": "out/filtered/sakila_1/frozen.jsonl",
           "soccer_1": "out/pipeline/soccer_1/candidates.jsonl", "college_2": "out/filtered/college_2/frozen.jsonl"}


def sample(per_db=4, seed=1001):
    out = []
    for db, f in SOURCES.items():
        ts = [r.get("task", r) for r in map(json.loads, open(f))]
        ts = [t for t in ts if t and "instruction" in t]
        out += random.Random(seed).sample(ts, min(per_db, len(ts)))
    return out


def main(repeats=3):
    os.makedirs("out/recheck", exist_ok=True); T = sample()
    items = [{"id": t["id"], "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0], "snapshot": t["snapshot"], "database": t["database"]} for t in T]
    V = recheck(items, repeats)
    A = [audit(T) for _ in range(repeats)]
    ach = sum(len({a.get(t["id"], {}).get("label") for a in A}) > 1 for t in T)
    auf = sum(len({a.get(t["id"], {}).get("label") == "useful" for a in A}) > 1 for t in T)
    res = {"veto": {k: v for k, v in V.items() if k != "runs"}, "auditor_label_changes": ach, "auditor_useful_flips": auf, "items": len(T)}
    json.dump(dict(res, veto_runs=V["runs"], audit_runs=A), open("out/recheck/recheck.json", "w"), default=str)
    L = ["# Remaining disagreement with single-task judging\n", "%d fixed tasks (4 per database), each judged %d times, uncached.\n" % (len(T), repeats),
         "| judge | items whose label changed across repeats | items whose decision flipped |", "|---|---|---|"]
    for m, n in V["label_changes"].items(): L.append("| veto: %s | %d/%d | |" % (m, n, len(T)))
    L.append("| veto: kept (both sensible) | | %d/%d (%.0f%%) |" % (V["decision_flips"], len(T), 100 * V["flip_rate"]))
    L.append("| auditor | %d/%d | useful vs not: %d/%d |" % (ach, len(T), auf, len(T)))
    open("out/recheck/RECHECK.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
