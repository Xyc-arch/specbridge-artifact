"""THE REVIEWED POPULATION (2026-10-14; 2026-10-16: plus the 92 filter sets, human_supervision/review-307-author-approve.md). An author reviewed all 215 main request sets (the first 215 rows of that file,
parsed to verdicts.json): could a reasonable analyst mean either reading? Every result on request sets is reported on the sets
judged "yes" (178). Raw runs stay on disk for all 215; ALL = True restores the full population (robustness line in the paper)."""
import json, os

VERDICTS = "human_supervision/verdicts.json"
ALL = os.environ.get("SB_ALL_SETS") == "1"


def verdict(case):
    """The author's verdict, or None for a set not yet reviewed (it is not reported until it is)."""
    return (json.load(open(VERDICTS)).get(case.split("-")[-1]) or {}).get("verdict")


def keep(case):
    """True when the request set belongs to the reported population."""
    return ALL or verdict(case) == "yes"


def accepted(cases):
    return [k for k in cases if keep(k)]
