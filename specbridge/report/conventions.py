"""SILENT CHOICES FOLLOW BENCHMARK CONVENTIONS (2026-10-16). On the accepted tie and counting request sets, one reading is the
convention of BIRD and Spider references (fig6_inclination): a plain LIMIT rather than every row tied at the cut-off, and COUNT over
joined rows rather than DISTINCT entities. The conventional reading is the one whose SQL has fewer tie or DISTINCT expansions. For
each model's main answer to the open request (explanation call), count conventional, other, or neither; binomial test against an
even split.
Also pooled by choice type and by whether the intended reading is the conventional one.
    python -m specbridge.report.conventions   -> out/paper/data/conventions.json, printed table"""
import collections, json, os, re
from scipy.stats import binomtest
from specbridge.comm.transfer.reviewed import verdict
from specbridge.comm.transfer import combined as CB

R = CB.D; DD = R + "/disclose"
MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]; OUT = "out/paper/data/conventions.json"


def expansions(q):
    return q.count("DISTINCT") + q.count("RANK()") + len(re.findall(r">= \(SELECT", q)) + len(re.findall(r"\) < 10", q))


def conventional(c):
    if c["type"] not in ("tie", "counting_unit"): return None
    a, b = expansions(c["sql_A"]), expansions(c["sql_B"])
    return "A" if a < b else "B" if b < a else None


def opens(d, keep):
    for m in MODELS:
        for f in os.listdir(os.path.join(d, m)):
            if f.endswith(".json"):
                x = json.load(open(os.path.join(d, m, f)))
                if x.get("wording") == "open" and x.get("case") in keep: yield m, x


def main():
    C = {c["case"]: c for c in json.load(open(R + "/eval/frozen.json"))["cases"] if verdict(c["case"]) == "yes"}
    cv = {k: conventional(c) for k, c in C.items()}; cv = {k: v for k, v in cv.items() if v}
    per = {m: collections.Counter() for m in MODELS}; split = collections.defaultdict(collections.Counter)
    for m, x in opens(DD, cv):
        pm = set(x["primary_matches"]); c = cv[x["case"]]; o = "B" if c == "A" else "A"
        r = "conventional" if c in pm else "other" if o in pm else "neither"; per[m][r] += 1
        split["type " + C[x["case"]]["type"]][r] += 1
        split["intended " + ("conventional" if C[x["case"]]["intended"] == c else "other")][r] += 1
    pool = sum(per.values(), collections.Counter())
    res = {"sets": len(cv), "by_type": dict(collections.Counter(C[k]["type"] for k in cv)),
           "intended_conventional": sum(C[k]["intended"] == cv[k] for k in cv),
           "models": {m: dict(r, p=binomtest(r["conventional"], r["conventional"] + r["other"]).pvalue) for m, r in per.items()},
           "pooled": dict(pool, p=binomtest(pool["conventional"], pool["conventional"] + pool["other"]).pvalue)}
    res["pooled_by"] = {k: dict(r, p=binomtest(r["conventional"], r["conventional"] + r["other"]).pvalue) for k, r in sorted(split.items())}
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT, "w"), indent=1)
    print("tie and counting sets with a conventional reading: %d %s; intended is conventional in %d" % (res["sets"], res["by_type"], res["intended_conventional"]))
    for m, r in res["models"].items():
        n = r["conventional"] + r["other"]; print("  %-10s conventional %d, other %d, neither %d: %.0f%%, p = %.2g" % (m, r["conventional"], r["other"], r.get("neither", 0), 100 * r["conventional"] / n, r["p"]))
    r = res["pooled"]; n = r["conventional"] + r["other"]; print("  pooled     conventional %d of %d (%.1f%%), p = %.2g" % (r["conventional"], n, 100 * r["conventional"] / n, r["p"]))
    for k, r in res["pooled_by"].items():
        n = r["conventional"] + r["other"]; print("  %-24s conventional %d of %d (%.1f%%), p = %.2g" % (k, r["conventional"], n, 100 * r["conventional"] / n, r["p"]))


if __name__ == "__main__":
    main()
