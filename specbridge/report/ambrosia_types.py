"""AMBROSIA BY AMBIGUITY TYPE (2026-10-17). The Section 5 AMBROSIA decomposition (out/ambrosia/decomposition{,_conf}.json, 60 + 60
test questions per model, authors' prompt, one call), split by AMBROSIA's three types. Vagueness questions ask which column or value a
phrase means, the library's referent-column type that the request sets do not test. Per model and type: questions; readings missing
from the answer to the ambiguous question, and how many of them the model computes when asked the unambiguous version (shape score);
questions with every reading returned.
    python -m specbridge.report.ambrosia_types   -> out/paper/data/ambrosia_types.json"""
import collections, json

OUT = "out/paper/data/ambrosia_types.json"


def main():
    R = collections.defaultdict(lambda: {"questions": 0, "missed": 0, "missed_computed": 0, "all_found": 0})
    for f in ("decomposition", "decomposition_conf"):
        for m, v in json.load(open("out/ambrosia/%s.json" % f))["models"].items():
            for q in v["questions"]:
                r = R["%s|%s" % (m, q["type"])]; rs = q["readings"]
                r["questions"] += 1; r["all_found"] += all(x["open_shape"] for x in rs)
                for x in rs:
                    if not x["open_shape"]: r["missed"] += 1; r["missed_computed"] += bool(x["spec_shape"])
    out = {}
    for k, r in sorted(R.items()):
        m, t = k.split("|"); out.setdefault(t, {})[m] = dict(r, computed_pct=round(100 * r["missed_computed"] / r["missed"], 1) if r["missed"] else None)
    json.dump(out, open(OUT, "w"), indent=1)
    for t, v in out.items(): print(t, {m: (r["questions"], r["computed_pct"], r["all_found"]) for m, r in v.items()})


if __name__ == "__main__":
    main()
