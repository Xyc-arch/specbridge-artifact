"""THE FROZEN REQUEST-SET POPULATION (2026-10-17). Three things are fixed and checked, never edited silently:
  1. the TYPE RULE: a choice type enters the request sets only if at least TYPE_RULE of the silent BIRD and Spider references take its
     other reading (paper Table 2, out/paper/data/tab2_references.json "table2"; strict cutoffs stand for value representation);
  2. the REVIEW SHEETS: the author's set review (review-307-author-approve.md -> verdicts.json) and the review of the minority
     references (review-reference-minority.md -> reference_minority_verdicts.json), and the frozen method-comparison draw;
  3. the SET LIST: the accepted request sets.
    python -m specbridge.comm.transfer.freeze freeze   -> human_supervision/FROZEN.json (hashes, rule, accepted ids)
    python -m specbridge.comm.transfer.freeze check    exit 1 if a frozen file or the set list changed, or a set breaks the rule"""
import hashlib, json, os, sys

TYPE_RULE = 0.01
FROZEN = "human_supervision/FROZEN.json"
FILES = ("human_supervision/review-307-author-approve.md", "human_supervision/verdicts.json",
         "human_supervision/review-reference-minority.md", "human_supervision/reference_minority_verdicts.json",
         "out/reqmethod100/sets.json")
FRZ = "out/transfer/all/render/eval/frozen.json"
SET_TYPE = {"tie": "ties_and_selection", "value_representation": "strict_cutoff"}   # set type -> Table 2 row


def kept_types():
    T = json.load(open("out/paper/data/tab2_references.json"))["table2"]
    return sorted(t for t, (u, o) in T.items() if u + o and o / (u + o) >= TYPE_RULE)


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def state():
    V = json.load(open("human_supervision/verdicts.json"))
    C = json.load(open(FRZ))["cases"]
    acc = sorted(c["case"] for c in C if (V.get(c["case"].split("-")[-1]) or {}).get("verdict") == "yes")
    return {"type_rule": TYPE_RULE, "kept_types": kept_types(), "accepted": acc, "files": {p: _sha(p) for p in FILES}}


def rule_violations():
    V = json.load(open("human_supervision/verdicts.json")); K = set(kept_types()); bad = []
    for c in json.load(open(FRZ))["cases"]:
        v = V.get(c["case"].split("-")[-1]) or {}; t = SET_TYPE.get(c["type"], c["type"])
        if v.get("verdict") == "yes" and t not in K: bad.append(("accepted but type below the rule", c["case"], t))
        if "rare in real data" in v.get("note", "") and t in K: bad.append(("rejected by the rule but type passes it", c["case"], t))
    return bad


def main(cmd):
    if cmd == "freeze":
        bad = rule_violations()
        if bad: print("not frozen; the rule is broken:", bad[:5]); sys.exit(1)
        S = state(); json.dump(S, open(FROZEN, "w"), indent=1)
        print("frozen: %d accepted sets, kept types %s, %d files" % (len(S["accepted"]), S["kept_types"], len(S["files"])))
        return
    F = json.load(open(FROZEN)); S = state(); err = []
    for p, h in F["files"].items():
        if not os.path.exists(p): err.append("missing " + p)
        elif _sha(p) != h: err.append("changed " + p)
    for k in ("type_rule", "kept_types", "accepted"):
        if F[k] != S[k]: err.append("changed " + k)
    err += ["%s: %s (%s)" % b for b in rule_violations()]
    print("freeze check: %s" % ("ok (%d accepted sets, rule %.0f%%, %d frozen files)" % (len(S["accepted"]), 100 * TYPE_RULE, len(F["files"])) if not err else "; ".join(err)))
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "check")
