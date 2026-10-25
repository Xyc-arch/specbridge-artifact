"""FINDING 1 ON THE FILTER REQUEST SETS (2026-10-16). The 92 sets built with compose's FILTER rule (specbridge.comm.transfer.extension),
of which the author accepts 71 (human_supervision/review-307-author-approve.md -> verdicts.json). Recomputed from the saved runs, no
model calls: per model and per choice type, both specific requests right with exploration, both readings returned for the open
request (explanation call), the choice named (Opus judge), and the settled request called open.
    python -m specbridge.report.filter_sets   -> out/paper/data/filter_sets.json, printed table"""
import collections, json, os
from specbridge.comm.transfer.evaluate import matches
from specbridge.comm.transfer.reviewed import verdict

R = "out/transfer/ext/render"; DD = R + "/disclose"; MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
OUT = "out/paper/data/filter_sets.json"


def main():
    C = {c["case"]: c for c in json.load(open(R + "/eval/frozen.json"))["cases"]}; J = json.load(open(DD + "/judge.json"))
    V = collections.Counter(verdict(k) for k in C); acc = sorted(k for k in C if verdict(k) == "yes")
    oth = lambda x: "B" if x == "A" else "A"; per, by = {}, collections.defaultdict(collections.Counter)
    for m in MODELS:
        d = R + "/eval/runs/" + m.replace("-", "_") + "_b1"; pr = {}
        for f in os.listdir(d):
            o = json.load(open(os.path.join(d, f))); k, v = o["key"].rsplit("|", 1)
            pr[(k, v)] = matches(C[k], o["answer"]) if o.get("answer") is not None else []
        D = {}
        for f in os.listdir(DD + "/" + m):
            x = json.load(open(os.path.join(DD, m, f))); D[(x["case"], x["wording"])] = x
        M = collections.Counter()
        for k in acc:
            t = C[k]["type"]; both = C[k]["intended"] in pr[(k, "precise")] and oth(C[k]["intended"]) in pr[(k, "precise_other")]
            o = D[(k, "open")]; got = set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]}; cov = {"A", "B"} <= got
            names = (J.get("%s|open|%s" % (k, m)) or {}).get("flags_decision") is True
            sw = [w for (kk, w) in D if kk == k and w != "open"][0]
            row = {"sets": 1, "both_specific": both, "covers": cov, "covers_if_both": cov and both, "names": names,
                   "specific_right": sw[-1] in D[(k, sw)]["primary_matches"], "misses": not cov, "misses_computable": (not cov) and both,
                   "settled_called_open": (J.get("%s|%s|%s" % (k, sw, m)) or {}).get("claims_open_wrongly") is True}
            M.update(row); by[t].update(row)
        per[m] = dict(M)
    res = {"verdicts": dict(V), "accepted": len(acc), "per_type_sets": dict(collections.Counter(C[k]["type"] for k in acc)),
           "models": per, "by_type_pooled": {t: dict(v) for t, v in by.items()}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT, "w"), indent=1)
    print("verdicts", res["verdicts"], "accepted", len(acc), res["per_type_sets"])
    for m, r in per.items():
        print("  %-10s both specific %d | covers %d (%d of %d if both) | names %d | specific right %d | misses computable %d of %d | settled called open %d" % (
            m, r["both_specific"], r["covers"], r["covers_if_both"], r["both_specific"], r["names"], r["specific_right"], r["misses_computable"], r["misses"], r["settled_called_open"]))
    for t, v in by.items(): print("  %-25s pooled: covers if both %d of %d, names %d of %d" % (t, v["covers_if_both"], v["both_specific"], v["names"], v["sets"]))


if __name__ == "__main__":
    main()
