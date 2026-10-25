"""AMBROSIA final test from the scores-only table (no AMBROSIA text needed): Table 4 (queries and wrong queries per unambiguous
question, readings found per ambiguous question) and AllFound per arm, checked against out/ambrosia/final/{exchange,final}.json.
    python reproduce/ambrosia_tables.py"""
import collections, json
S = [json.loads(l) for l in open("out/ambrosia/final/scores.jsonl")]
rows = collections.defaultdict(set)
for x in S: rows[x["model"]].add((x["ambrosia_row"], x["arm"]))
ARMS = ("plain", "samplek", "dtp", "ours"); bad = 0
F = json.load(open("out/ambrosia/final/final.json"))
for m in sorted(rows):
    full = {r for r, _a in rows[m] if all((r, a) in rows[m] for a in ARMS)}
    for a in ARMS:
        X = [x for x in S if x["model"] == m and x["arm"] == a and x["ambrosia_row"] in full]
        U = [x for x in X if not x["ambiguous"]]; A = [x for x in X if x["ambiguous"]]
        q, w, f = (sum(x["queries_returned"] for x in U) / len(U), sum(x["wrong_queries"] for x in U) / len(U), sum(x["readings_found"] for x in A) / len(A))
        af = sum(x["readings_found"] == x["gold_readings"] for x in A); ref = F["solvers"][m]["arms"][a]["allfound"]
        bad += af != ref
        print("%-10s %-8s queries %.2f  wrong %.2f  readings %.2f  AllFound %d/%d (final.json %d)" % (m, a, q, w, f, af, len(A), ref))
print("ALLFOUND MATCHES final.json" if not bad else "%d MISMATCHES" % bad)
