"""THE EXTENSION REQUEST SETS (2026-10-16): the five library types the main request sets do not reach, because the main corpus's
queries have no date, bound, negated, linked or outer-join condition. The corpus is built with compose's opt-in FILTER rule
(specbridge.pd.structures.compose, Space(extra={"filter"})), which plants one such condition on the first stage's rows and builds
the other reading where the choice is made. So code, not a model, proposes each task's choice point: the edit is the difference
between the two readings' SQL after both are re-emitted in the language. The rest of the pipeline is the main one unchanged
(choice_points verify | review | report, render, evaluate, disclose).
    python -m specbridge.comm.transfer.extension points <corpus dir> <choice-point dir>"""
import json, os, sys
from specbridge.comm.common import db as DB

KIND = {   # planted kind -> (the choice point's kind, which is its library type; decision; reading A; reading B)
    "window": ("time_scope", "Whether records dated exactly on the first or the last day of the date range count",
               "the range includes both of its end dates", "the range excludes both of its end dates"),
    "bound": ("value_representation", "Whether rows whose value equals the threshold exactly count",
              "values equal to the threshold count (at least the threshold)", "only values above the threshold count (more than the threshold)"),
    "none": ("negated_membership_scope", "What 'without' a category means for an entity with several records",
             "entities none of whose records has the category", "entities with at least one record that does not have the category"),
    "both": ("condition_linkage", "Whether the two conditions must hold on the same record",
             "entities with one record that meets both conditions", "entities with a record meeting each condition, possibly different records"),
    "outer": ("population_scope", "Whether entities with no records are part of the result",
              "only entities that have records", "every entity, those without records with a count of zero"),
}


def edit(a, b):
    """One exact edit turning a into b: the differing span, widened until its text occurs once in a."""
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]: i += 1
    j = 0
    while j < min(len(a), len(b)) - i and a[-1 - j] == b[-1 - j]: j += 1
    s, e = i, len(a) - j
    while a.count(a[s:e]) != 1 or e == s:
        s, e = max(0, s - 1), min(len(a), e + 1)
    return {"from": a[s:e], "to": b[s:len(b) - (len(a) - e)]}


def points(corpus, out, source="ext"):
    from specbridge.pd.structures.algebra import emit, lift
    T = [json.loads(l) for l in open(corpus + "/corpus.jsonl" if os.path.exists(corpus + "/corpus.jsonl") else corpus + "/tasks.jsonl")]
    P, skipped = {}, 0
    for t in T:
        pl = t.get("planted")
        if not pl or not pl.get("sql_B"): skipped += 1; continue
        try: b = emit(lift(pl["sql_B"], DB.catalogue(t["database"]).con))
        except Exception: skipped += 1; continue
        kind, dec, ra, rb = KIND[pl["kind"]]
        P["%s:%s" % (source, t["id"])] = [{"kind": kind, "decision": "%s (%s)" % (dec, pl["text"]), "reading_A": ra, "reading_B": rb,
                                           "edits": [edit(t["reference_sql"], b)], "why_open": "a natural request can name the condition without settling this",
                                           "planted": pl["kind"]}]
    os.makedirs(out, exist_ok=True); json.dump(P, open(out + "/proposals.json", "w"), indent=1)
    print("points for %d tasks (%d without a planted condition); kinds %s" % (len(P), skipped, json.dumps(
        __import__("collections").Counter(v[0]["kind"] for v in P.values()))))


if __name__ == "__main__":
    a = sys.argv[1:]
    {"points": lambda: points(a[1], a[2])}[a[0]]()
