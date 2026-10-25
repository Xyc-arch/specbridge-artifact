"""THE COMBINED REQUEST-SET COLLECTION (2026-10-17). The request sets come from two construction runs on the same 12 databases:
the generator's queries (out/transfer/eval12-v2/render, 215 sets) and the same queries with one filter condition added for the
library types that live in a filter (out/transfer/ext/render, 92 sets). Every result is reported on the union (307 sets, 249
accepted). This merges the two render directories into one, so every evaluation module reads and extends a single collection:
    python -m specbridge.comm.transfer.combined     -> out/transfer/all/render (frozen cases, wordings, allocations, runs, judges)
Files are copied, never overwritten: answers already saved in the combined directory are kept, so a rerun only adds."""
import json, os, random, shutil

PARTS = ("out/transfer/eval12-v2/render", "out/transfer/ext/render"); D = "out/transfer/all/render"
DERIVED = ("sample.json", "judge.json", "judge_alternatives.json", "results.json")   # merged below or rebuilt by the reports


def part_cases(i):
    return sorted(c["case"] for c in json.load(open(PARTS[i] + "/eval/frozen.json"))["cases"])


def extend(chosen, seed):
    """A seeded sample drawn from the first part, extended to the union at the same rate: the first part's draw is kept as it
    was, and the second part contributes round(len(chosen) * |second| / |first|) sets drawn with the same seed."""
    a, b = part_cases(0), part_cases(1); n = round(len(chosen) * len(b) / len(a))
    return sorted(chosen) + sorted(random.Random(seed).sample(b, n))


def extend_accepted(chosen, seed):
    """As extend, for a draw of accepted sets: the second part's accepted sets join at the rate of the first part's accepted."""
    from specbridge.comm.transfer import reviewed as RV
    a, b = RV.accepted(part_cases(0)), RV.accepted(part_cases(1)); n = round(len(chosen) * len(b) / len(a))
    return list(chosen) + sorted(random.Random(seed).sample(b, n))


def _copytree(src, dst):
    for root, _dirs, files in os.walk(src):
        for f in files:
            s = os.path.join(root, f); t = os.path.join(dst, os.path.relpath(s, src))
            if f.endswith((".done", ".md", ".txt")) or f in DERIVED or os.path.exists(t): continue
            os.makedirs(os.path.dirname(t), exist_ok=True); shutil.copy2(s, t)


def build():
    cases, written, judge, alts = [], {}, {}, {}
    S = {"cases": [], "wordings": {}, "judge_open": []}
    for p in PARTS:
        cases += json.load(open(p + "/eval/frozen.json"))["cases"]; written.update(json.load(open(p + "/written.json")))
        s = json.load(open(p + "/disclose/sample.json")); S.update({k: s[k] for k in ("seed", "prompt_sha")})
        S["cases"] += s["cases"]; S["wordings"].update(s["wordings"]); S["judge_open"] += s["judge_open"]
        judge.update(json.load(open(p + "/disclose/judge.json")))
        if os.path.exists(p + "/disclose/judge_alternatives.json"): alts.update(json.load(open(p + "/disclose/judge_alternatives.json")))
        for sub in ("eval/runs", "disclose"):
            _copytree(p + "/" + sub, D + "/" + sub)
    os.makedirs(D + "/eval", exist_ok=True)
    json.dump({"cases": cases}, open(D + "/eval/frozen.json", "w"), indent=1)
    json.dump(written, open(D + "/written.json", "w"), indent=1)
    S["cases"] = sorted(S["cases"]); S["judge_open"] = sorted(S["judge_open"]); json.dump(S, open(D + "/disclose/sample.json", "w"), indent=1)
    for f, new in (("judge.json", judge), ("judge_alternatives.json", alts)):           # keep judgments added in the combined directory
        f = D + "/disclose/" + f; old = json.load(open(f)) if os.path.exists(f) else {}; json.dump({**new, **old}, open(f, "w"), indent=1)
    print("combined:", len(cases), "cases,", len(written), "written,", len(judge), "judged ->", D)


if __name__ == "__main__":
    build()
