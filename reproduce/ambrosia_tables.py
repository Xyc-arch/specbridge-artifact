"""AMBROSIA final test from the scores-only tables (no AMBROSIA text needed): queries, wrong queries and readings found per question
and AllFound per arm, checked against out/ambrosia/final/{exchange,final}.json; and Table 5's AMBROSIA columns (per 100 requests),
checked against out/system/method.json.
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

# Table 5, AMBROSIA columns: per 100 requests of which 20% leave a choice open (interpretations missed, wrong answers shown, calls),
# per model and arm, from the scores-only table of the six arms; checked against out/system/method.json.
T = [json.loads(l) for l in open("out/system/scores.jsonl")]; M = json.load(open("out/system/method.json"))["stream"]["per_model"]; PI = 0.2; bad5 = 0
for m in sorted({x["model"] for x in T}):
    for a in ("plain", "samplek", "dtp", "state", "ours", "method"):
        X = [x for x in T if x["model"] == m and x["arm"] == a]; A = [x for x in X if x["ambiguous"]]; U = [x for x in X if not x["ambiguous"]]
        per = lambda k: round(100 * (PI * sum(x[k] for x in A) / len(A) + (1 - PI) * sum(x[k] for x in U) / len(U)), 1)
        got = {"missed": per("missed"), "wrong": per("wrong"), "calls": round(per("calls"))}; ref = M[m][a]["0.2"]
        ok = all(abs(got[k] - ref[k]) < 0.051 for k in got); bad5 += not ok
        print("%-10s %-8s per 100 requests: missed %5.1f  wrong %5.1f  calls %4d  %s" % (m, a, got["missed"], got["wrong"], got["calls"], "ok" if ok else "MISMATCH %s" % ref))
print("TABLE 5 (AMBROSIA) MATCHES method.json" if not bad5 else "%d TABLE 5 MISMATCHES" % bad5)
raise SystemExit(1 if (bad or bad5) else 0)   # a mismatch fails make test (and make all)
