"""specbridge.comm.verbal.interpret -- the INTERPRETATION RECORD of a task, and the grader it implies.

V produces a question AND its allowed interpretations; the grader is derived from that record, which is fixed BEFORE any
agent answers (never extended because an answer failed). Three cases, handled once, here and in V:

  REPRESENTATION  a coded output column whose codes have VERIFIED meanings (the database's documentation, or an accepted
                  code in catalogues/language): the answer may show the stored code or its documented meaning, word for
                  word, at that position. Both sides are mapped to one canonical form before the ordinary comparison.
  MEANING         two readings of the question are both JUSTIFIED: the record carries each alternative's complete
                  reference result, and an answer passes if it is one of them. Alternatives come only from a declared,
                  evidenced source (catalogues/language/<db>.json "equivalents"); identical documentation is NOT a
                  justification -- it signals uncertainty.
  UNRESOLVED      alternatives cannot be established: V keeps the precise identifier (the handle) and the record flags
                  the site as needing clarification (specbridge.comm.verbal.verbalize.REPORT fallbacks).

The record depends on the task, not on its wording: both arms of a comparison are graded by the same record.
"""
from specbridge.pd.spec import render as R


def record(S, cat, unresolved=()):
    """The interpretation record of specification S (answer query's outputs), from verified resources only."""
    from specbridge.comm.verbal.gamma import value_labels, language
    from specbridge.pd.realize.semantic import load
    meta = load(cat)["columns"]
    labels = cat.__dict__.get("_value_labels") or value_labels(cat.db, cat.con)
    cat.__dict__["_value_labels"] = labels
    rep = []
    for o in S["query"]["outputs"]:
        e = o["expr"]
        while e.get("op") in ("as_real", "as_text"): e = e["arg"]
        if e.get("op") != "column" or "." not in e["ref"]: continue
        t, c = e["ref"].split(".", 1)
        if meta.get(e["ref"], {}).get("semantic_role") not in ("category", "indicator"): continue
        m = labels.get((t, c))
        if m: rep.append({"position": o["position"], "column": e["ref"], "mapping": [[k, v] for k, v in m.items()]})
    eq = language(cat.db).get("equivalents", [])            # declared, evidenced equivalences (none yet)
    return {"representation": rep, "meaning": [], "declared_equivalents": len(eq), "unresolved": list(unresolved)}


def _canon(rows, rep):
    """Each recorded position's value in one canonical form: a code with a verified meaning, or that meaning, becomes
    the meaning; anything else is left as it is."""
    if not rep or rows is None: return rows
    maps = {r["position"] - 1: {str(k): v for k, v in r["mapping"]} for r in rep}
    labels = {i: {v.strip().lower(): v for v in m.values()} for i, m in maps.items()}
    out = []
    for row in rows:
        row = list(row)
        for i, m in maps.items():
            if i < len(row) and row[i] is not None:
                s = str(row[i])
                row[i] = m.get(s) or labels[i].get(s.strip().lower(), row[i])
        out.append(tuple(row))
    return out


def grade(task, answer):
    """The grader the record implies: the ordinary comparison after mapping each recorded representation to one form;
    then each justified alternative's complete result. (ok, why)."""
    rec = task.get("record") or {}
    rep = rec.get("representation", [])
    ok, why = R.grade(task["grader"], _canon([tuple(r) for r in task["reference_answer"]], rep), _canon([tuple(r) for r in answer], rep),
                      task["tie_groups"], _canon([tuple(r) for r in task["last_pool"]], rep) if task["last_pool"] else None)
    if ok: return ok, why
    for alt in rec.get("meaning", []):
        ok2, _w = R.grade(task["grader"], _canon([tuple(r) for r in alt["reference_answer"]], rep), _canon([tuple(r) for r in answer], rep),
                          alt.get("tie_groups"), _canon([tuple(r) for r in alt["last_pool"]], rep) if alt.get("last_pool") else None)
        if ok2: return True, "matches the justified alternative: %s" % alt["justification"]
    return ok, why
