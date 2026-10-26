"""FINDING 1 ON THE REVIEWED REQUEST SETS (2026-10-14). The author reviewed all 215 sets: could a reasonable analyst mean either
reading? (human_supervision/completed-review-215.md -> verdicts.json). This recomputes every Finding 1 number from the saved runs
(no model calls) on three scopes: all 215 (reproduces the paper), accepted (yes), accepted or unsure.
    python -m specbridge.report.accepted   -> out/paper/data/accepted.json, printed table"""
import collections, json, os, random
from specbridge.comm.transfer.evaluate import matches
from specbridge.comm.transfer import topk as TK, combined as CB

R = CB.D; DD = R + "/disclose"; MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
OUT = "out/paper/data/accepted.json"


def _load(p):
    o = {}
    for f in os.listdir(p):
        x = json.load(open(os.path.join(p, f))); o[(x["case"], x["wording"])] = x
    return o


def _wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def per_set():
    """Per request set and model: both specific requests right (with exploration; in one call), open request covers both
    readings, the response names the choice, five samples cover both. Returns (cases, per) with per[(model, case)]."""
    C = {c["case"]: c for c in json.load(open(R + "/eval/frozen.json"))["cases"]}; J = json.load(open(DD + "/judge.json"))
    oth = lambda x: "B" if x == "A" else "A"; top = set(TK.subset())
    per = {}
    for m in MODELS:
        d = R + "/eval/runs/" + m.replace("-", "_") + "_b1"; pr = {}
        for f in os.listdir(d):
            o = json.load(open(os.path.join(d, f))); k, v = o["key"].rsplit("|", 1)
            pr[(k, v)] = matches(C[k], o["answer"]) if o.get("answer") is not None else []
        Dm = _load(DD + "/" + m); Cm = _load(DD + "/complement/" + m)
        for k in C:
            sw = [w for (kk, w) in Dm if kk == k and w != "open"][0]; ow = "precise_B" if sw == "precise_A" else "precise_A"
            o = Dm[(k, "open")]; got = set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]}
            topk = None
            if k in top:
                fs = [TK._plain(DD, m, k)] + [TK._f(DD, m, k, s) for s in range(2, TK.K + 1)]
                if all(os.path.exists(f) for f in fs): topk = {"A", "B"} <= set().union(*(set(json.load(open(f))["primary_matches"]) for f in fs))
            per[(m, k)] = {"explore_both": C[k]["intended"] in pr[(k, "precise")] and oth(C[k]["intended"]) in pr[(k, "precise_other")],
                           "single_both": sw[-1] in Dm[(k, sw)]["primary_matches"] and (k, ow) in Cm and ow[-1] in Cm[(k, ow)]["primary_matches"],
                           "runs": Dm[(k, sw)]["primary_executes"] and (k, ow) in Cm and Cm[(k, ow)]["primary_executes"],
                           "covers": {"A", "B"} <= got, "names": (J.get("%s|open|%s" % (k, m)) or {}).get("flags_decision") is True, "topk": topk}
    return C, per


def main():
    C, per = per_set()
    V = json.load(open("human_supervision/verdicts.json")); verdict = {k: V[k.split("-")[-1]]["verdict"] for k in C}
    scopes = {"all": sorted(C), "accepted": sorted(k for k in C if verdict[k] == "yes"),
              "accepted_or_unsure": sorted(k for k in C if verdict[k] in ("yes", "unsure")),
              "accepted_no_filter": sorted(k for k in C if verdict[k] == "yes" and k in set(CB.part_cases(0))),   # robustness: no filter rule
              "accepted_all_types": sorted(k for k in C if verdict[k] == "yes" or "rare in real data" in V[k.split("-")[-1]].get("note", ""))}   # robustness: before the type rule
    res = {"verdicts": dict(collections.Counter(verdict.values())), "scopes": {}}
    for sn, ks in scopes.items():
        S = {"n": len(ks), "models": {}}
        for m in MODELS:
            f = [per[(m, k)] for k in ks]; c = lambda p: sum(1 for x in f if p(x))
            ex = c(lambda x: x["explore_both"]); sg = c(lambda x: x["single_both"])
            miss = c(lambda x: not x["covers"])
            row = {"explore_both_specific": ex, "single_both_specific": sg, "covers_both": c(lambda x: x["covers"]), "names": c(lambda x: x["names"]),
                   "covers_given_explore_both": [c(lambda x: x["explore_both"] and x["covers"]), ex],
                   "covers_given_single_both": [c(lambda x: x["single_both"] and x["covers"]), sg],
                   "misses": miss, "misses_computable_single": c(lambda x: not x["covers"] and x["single_both"]),
                   "misses_computable_explore": c(lambda x: not x["covers"] and x["explore_both"]),
                   "named_and_computable": [c(lambda x: x["names"] and x["single_both"] and not x["covers"]), c(lambda x: x["names"] and x["single_both"])],
                   "topk": [c(lambda x: x["topk"] is True), c(lambda x: x["topk"] is not None)]}
            row["outcomes"] = {"both": c(lambda x: x["covers"]), "named_one": c(lambda x: not x["covers"] and x["single_both"] and x["names"]),
                               "silent_computable": c(lambda x: not x["covers"] and x["single_both"] and not x["names"]),
                               "not_computable": c(lambda x: not x["covers"] and not x["single_both"] and x["runs"]),
                               "no_run": c(lambda x: not x["covers"] and not x["single_both"] and not x["runs"])}   # every open request, one outcome each
            row["ci_covers_given_explore_both"] = _wilson(*row["covers_given_explore_both"])
            row["ci_covers_given_single_both"] = _wilson(*row["covers_given_single_both"])
            S["models"][m] = row
        from specbridge.report.impact import compare
        imp = collections.Counter()
        for k in ks:
            a, b = C[k].get("answer_A"), C[k].get("answer_B")
            if not a or not b: continue
            o = compare(a, b, C[k]["grader"].get("ordered", False)); imp["sets"] += 1
            imp["row_keys_differ"] += {r[0] for r in a} != {r[0] for r in b}; imp["first_key_changes"] += a[0][0] != b[0][0]
            if "value" in o: imp["single_value"] += 1; imp["value_gt50"] += o["value"] > 0.5
        S["readings_differ"] = dict(imp)   # impact.compare: row keys, first row's key, single-value relative change
        S["per_database"] = dict(collections.Counter(C[k]["database"] for k in ks))
        res["scopes"][sn] = S
    json.dump(res, open(OUT, "w"), indent=1)
    pc = lambda a, b: "%d/%d (%.1f%%)" % (a, b, 100 * a / b) if b else "-"
    print("verdicts:", res["verdicts"])
    for sn, S in res["scopes"].items():
        print("\n== %s (%d sets)" % (sn, S["n"]), S["readings_differ"], sorted(S["per_database"].values()))
        for m, r in S["models"].items():
            print("  %-10s spec both (explore) %s | single %s | covers %s | names %s | covers|explore-both %s | covers|single-both %s | misses computable: single %s, explore %s | named+computable but one: %s | top-5 both %s" % (
                m, pc(r["explore_both_specific"], S["n"]), pc(r["single_both_specific"], S["n"]), pc(r["covers_both"], S["n"]), pc(r["names"], S["n"]),
                pc(*r["covers_given_explore_both"]), pc(*r["covers_given_single_both"]), pc(r["misses_computable_single"], r["misses"]),
                pc(r["misses_computable_explore"], r["misses"]), pc(*r["named_and_computable"]), pc(*r["topk"])))


if __name__ == "__main__":
    main()
