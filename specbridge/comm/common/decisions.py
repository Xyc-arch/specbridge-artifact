"""THE COMMUNICATION LIBRARY OF DECISIONS (docs/COMM_DECISIONS.md): types of decision a reader must resolve, and examples, each
with its own resolution status. Shared by diagnosis, synthetic generation and inference.
    python -m specbridge.comm.common.decisions build     normalize every diagnosed record into library/ (no model calls)
    python -m specbridge.comm.common.decisions regress   the regression checks; exit 1 on a failure
    python -m specbridge.comm.common.decisions report    library/REPORT.md: coverage per type, statuses, candidates, new-type rate
    python -m specbridge.comm.common.decisions match     unmatched candidates: opus proposes, sonnet reviews; then `build` again
    python -m specbridge.comm.common.decisions observe   the per-requirement statuses of the analyses, typed and checked, grouped by source task
Sources, in order: two-reading records (out/comm_library/library.jsonl, with the gate's verdicts), one-sided records (each
batch's records.json: the question resolved it), and the decision sites of questions solved in both wordings in every repeat
(stay-silent examples). Held-out questions are never read. Matching is by the record's choice tag or the site's family,
through the two tables below; anything they cannot place goes to library/candidates.jsonl, provisional."""
import collections, glob, json, os, sys, time

LIB, SRC = "library", "out/comm_library"
VERSION = "decisions-1"

# ---------------------------------------------------------------------------------------------------- the types (seed v1)
TYPES = [
    {"id": "referent_column", "name": "Which column or table a phrase means",
     "decision": "Which stored attribute does the phrase refer to, when several columns or tables could carry it?",
     "applies_when": {"sites": ["which_column"], "schema": "look-alike or shared column names; the same attribute in two tables"},
     "readings": ["the column the reference uses", "a look-alike column (abbreviated, another table's copy, another role)"],
     "resolution_rules": ["documentation or evidence naming the column", "the table the question's entity lives in"],
     "clarification": "Do you mean <column A> or <column B>?"},
    {"id": "value_representation", "name": "Stored value vs its meaning",
     "decision": "Is a value said in words to be matched as stored (a code, an exact spelling) or by its documented meaning?",
     "applies_when": {"sites": ["representation", "matching_boundaries"], "schema": "coded columns; values whose stored form differs from the words"},
     "readings": ["the stored code or spelling", "the documented label or a looser match"],
     "resolution_rules": ["evidence giving the stored form", "documentation listing the codes"],
     "clarification": "Should '<words>' match the stored value '<code>'?"},
    {"id": "population_scope", "name": "Which records are in scope",
     "decision": "Which records does the question range over: only those with a match, all of them, or a subset?",
     "applies_when": {"sites": ["population_scope"], "schema": "optional relationships; records without a match"},
     "readings": ["only records with a match (inner join)", "every record, with missing values (left join)", "a filtered subset"],
     "resolution_rules": ["wording such as 'all', 'including', 'if any'", "the entity the question counts"],
     "clarification": "Should records with no <related item> be included?"},
    {"id": "counting_unit", "name": "What is counted",
     "decision": "Count rows (events, records) or distinct entities?",
     "applies_when": {"sites": ["counting_multiplicity"], "schema": "an entity that repeats across joined or event rows"},
     "readings": ["rows", "distinct entities"],
     "resolution_rules": ["the counted noun ('patients' vs 'examinations')", "'distinct', 'different', 'unique'"],
     "clarification": "Count each <entity> once, or every <event>?"},
    {"id": "aggregation_level", "name": "At which level an aggregate is taken",
     "decision": "Over which rows, at which level, is the average or total computed?",
     "applies_when": {"sites": ["aggregation", "calculation"], "schema": "values that exist at two levels (per record, per entity)"},
     "readings": ["over individual records", "over per-entity aggregates", "weighted vs unweighted"],
     "resolution_rules": ["'per', 'each', 'on average per'", "the unit named in the question"],
     "clarification": "Average over <records> or over <entities>?"},
    {"id": "missing_values", "name": "How missing values are treated",
     "decision": "Are missing values excluded, kept, or counted as zero?",
     "applies_when": {"sites": ["missing_values"], "schema": "nullable columns that hold missing values in the data"},
     "readings": ["excluded", "kept (as missing)", "treated as zero"],
     "resolution_rules": ["'if any', 'with a value'", "the documented meaning of missing"],
     "clarification": "Should <items> with no <value> be included?"},
    {"id": "ties_and_selection", "name": "Ties at an extreme, and how many to return",
     "decision": "When several rows share the extreme value, return one or all of them?",
     "applies_when": {"sites": ["ordering_selection"], "schema": "an ordering key with tied values in the data"},
     "readings": ["one row (LIMIT)", "every tied row"],
     "resolution_rules": ["singular vs plural wording", "an explicit tie rule"],
     "clarification": "If several share the <extreme>, return all of them?"},
    {"id": "time_scope", "name": "Which time a condition refers to",
     "decision": "Which date or period does a time condition use, and are its boundaries included?",
     "applies_when": {"sites": ["time"], "schema": "several dates per entity; date boundaries"},
     "readings": ["one date column vs another", "inclusive vs exclusive boundary", "age now vs at an event"],
     "resolution_rules": ["the event named", "'after', 'since', 'between ... and'"],
     "clarification": "Measured at <date A> or <date B>?"},
    {"id": "relationship_role", "name": "Which role in a relationship",
     "decision": "When an entity is linked in several roles (owner, user, winner, loser), which role counts?",
     "applies_when": {"sites": [], "schema": "a linking table with a role column; two foreign keys to the same table"},
     "readings": ["one role", "any role"],
     "resolution_rules": ["the role named in the question or evidence"],
     "clarification": "Only as <role>, or in any role?"},
    {"id": "calculation", "name": "Which formula",
     "decision": "Which formula: the denominator of a rate, the definition of an increase, the order of operations?",
     "applies_when": {"sites": ["calculation"], "schema": ""},
     "readings": ["the reference formula", "another defensible formula"],
     "resolution_rules": ["evidence stating the formula"],
     "clarification": "Should <quantity> be computed as <formula A> or <formula B>?"},
    {"id": "output_form", "name": "Which columns are returned, in what form",
     "decision": "Which columns does the answer return, in which order, with which formatting?",
     "applies_when": {"sites": [], "schema": ""},
     "readings": ["the reference's columns", "a subset, a superset or another order"],
     "resolution_rules": ["the outputs the question names"],
     "clarification": "Return only <column>, or <column> with <other>?",
     "consumers": {"grading": "tolerated (specbridge.comm.common.grade.shape_tolerant)", "inference": "not raised as a meaning choice",
                   "synthesis": "outputs stated or left to the solver; graded tolerantly"}},
]
TAG_TO_TYPE = {"which_column_source": "referent_column", "value_mapping": "value_representation", "counting_unit": "counting_unit",
               "aggregation_level": "aggregation_level", "missing_values": "missing_values", "tie": "ties_and_selection",
               "time_scope": "time_scope", "relationship_role": "relationship_role", "calculation": "calculation", "output_form": "output_form"}
SITE_TO_TYPE = {"population_scope": "population_scope", "counting_multiplicity": "counting_unit", "aggregation": "aggregation_level",
                "missing_values": "missing_values", "ordering_selection": "ties_and_selection", "time": "time_scope",
                "matching_boundaries": "value_representation", "calculation": "calculation", "representation": "value_representation",
                "referent": "referent_column"}
# WHAT AN INTERPRETER DOES with an example (2026-10-01: "inspect internally" and "ask the user" are different actions):
#   ask      the context cannot settle it: surface it / ask a clarification (unresolved, contested, conflicting)
#   inspect  the context settles it, but only by looking: read the documentation, evidence or data, then proceed silently
#            (recoverable; and resolved, where the source of the resolution was not recorded)
#   none     the wording or an ordinary convention settles it: nothing to do (explicit, implied)
ACTION = {"unresolved": "ask", "contested": "ask", "conflicting": "ask", "recoverable": "inspect", "resolved": "inspect",
          "explicit": "none", "implied": "none"}
RAISE = {k: v == "ask" for k, v in ACTION.items()}


def _heldout():
    return set(json.load(open(SRC + "/heldout_eval.json"))["question_ids"])


def _gate():
    g = json.load(open(SRC + "/gate.json")) if os.path.exists(SRC + "/gate.json") else []
    return {x["record"]: x for x in g}                     # later verdicts win


def _key(source, task): return "%s:%s" % (source.rstrip("/").split("/")[-1], task)


def _readings(r):
    return [{k: x.get(k) for k in ("id", "reading", "sql", "rows", "differs_from_gold")} for x in r.get("readings", [])]


DEV_DIRS = ["batch*", "spider_dev"]      # development diagnosis directories under SRC; a confirmation directory is never listed


def _bench(batch): return "Spider dev" if batch.startswith("spider") else "BIRD dev"


def _example(r, typ, status, source, how):
    return {"type": typ, "status": status, "action": ACTION[status], "raise": RAISE[status],
            "source": {"benchmark": _bench(source.rstrip("/").split("/")[-1]), "batch": source.rstrip("/").split("/")[-1], "task": r.get("task"), "database": r.get("database"),
                       "question_id": r.get("question_id")},
            "question": r.get("original"), "gold_sql": r.get("gold_sql"), "decision": r.get("decision"), "readings": _readings(r),
            "evidence": {"analysis": r.get("analysis"), "inspection": r.get("inspection")}, "review": {"reviewers": r.get("review"), "gate": r.get("gate_verdict")},
            "provenance": {"from": how, "record_version": r.get("version"), "library": VERSION, "built": time.strftime("%Y-%m-%d")}}


def _candidate(r, status, source):
    return {"source": _key(source, r["task"]), "tag": (r.get("tags") or {}).get("choice"), "decision": r.get("decision"), "record_status": status,
            "question": r.get("original"), "gold_sql": r.get("gold_sql"), "readings": _readings(r), "review": r.get("review"), "status": "provisional"}


def _matches():
    """Accepted matching outcomes by source key (library/matches.jsonl, written by `match`)."""
    f = LIB + "/matches.jsonl"
    return {m["source"]: m for m in map(json.loads, open(f))} if os.path.exists(f) else {}


def build():
    held = _heldout(); gate = _gate(); ex, defects, cand = [], [], []; seen = set(); M = _matches()
    def add(e):
        k = (e["source"]["batch"], e["source"]["task"], e["type"])
        if e["source"].get("question_id") in held: raise AssertionError("a held-out question reached the library: %s" % (k,))
        if k in seen: return
        seen.add(k); e["id"] = "%s:%s:%s" % k; ex.append(e)
    # 1. two-reading records; a revision supersedes its original for the same task and type
    recs = [json.loads(l) for l in open(SRC + "/library.jsonl")]
    superseded = {r["revision_of"] for r in recs if r.get("revision_of")}         # a promoted revision REPLACES its original
    recs = [r for r in recs if _key(r["source"], r["task"]) not in superseded]
    recs.sort(key=lambda r: 0 if "revised" in str(r.get("status")) else 1)
    for r in recs:
        g = gate.get(_key(r["source"], r["task"])) or r.get("gate") or {}; r["gate_verdict"] = g
        tag = (r.get("tags") or {}).get("choice"); typ = TAG_TO_TYPE.get(tag)
        if g.get("category") == "output form": typ = "output_form"                # the gate's verdict on the record outranks the tag
        if g.get("category") == "reference defect":
            defects.append({"source": _key(r["source"], r["task"]), "decision": r.get("decision"), "gate": g, "gold_sql": r.get("gold_sql")}); continue
        st = "unresolved" if str(r.get("status")).startswith("mutually") else "contested"
        if g.get("confidence") == "low": st = "contested"
        if not typ:
            m = M.get(_key(r["source"], r["task"]))
            if m and m["outcome"] == "merged": typ = m["type"]
            elif m and m["outcome"] == "new provisional type": typ = m["type"]
            elif m and m["outcome"] == "reference defect":
                defects.append({"source": _key(r["source"], r["task"]), "decision": r.get("decision"), "gate": g, "gold_sql": r.get("gold_sql"), "by": "matching"}); continue
            else:
                cand.append(dict(_candidate(r, st, r["source"]), why="no type for choice tag %r" % tag, matching=m)); continue
            st = m.get("status") or st
        add(_example(r, typ, st, r["source"], "two-reading record" + (" (matched: %s)" % M[_key(r["source"], r["task"])]["outcome"] if _key(r["source"], r["task"]) in M else "")))
    # 2. one-sided records: a decision the question resolved (stay silent)
    for f in sorted(f for g in DEV_DIRS for f in glob.glob(SRC + "/%s/records.json" % g)) + ["out/bird_pairs/records.json"]:
        if not os.path.exists(f): continue
        for r in json.load(open(f)).get("not_library", []):
            if r.get("status") != "one-sided": continue
            tag = (r.get("tags") or {}).get("choice"); typ = TAG_TO_TYPE.get(tag)
            if not typ:
                m = M.get(_key(os.path.dirname(f), r["task"]))
                if m and m["outcome"] in ("merged", "new provisional type"): typ = m["type"]
                elif m and m["outcome"] == "reference defect":
                    defects.append({"source": _key(os.path.dirname(f), r["task"]), "decision": r.get("decision"), "gold_sql": r.get("gold_sql"), "by": "matching"}); continue
                else:
                    cand.append(dict(_candidate(r, "resolved", os.path.dirname(f)), why="one-sided record with no type for choice tag %r" % tag, matching=m)); continue
            add(_example(r, typ, "resolved", os.path.dirname(f), "one-sided record (reviewers: only the reference reading fits)"))
    # 3. decision sites of questions solved in both wordings, every repeat (stay silent)
    from specbridge.comm.diagnose.ambiguity import sites
    from specbridge.comm.diagnose.compare import runs, tasks
    for d in sorted(d for g in DEV_DIRS for d in glob.glob(SRC + "/" + g)):
        if not os.path.exists(d + "/summary.json"): continue          # older batches use another run layout
        O = {t["id"]: t for t in tasks(d, "original")}; E = {t["id"] for t in tasks(d, "explicit")}
        for i in E:
            o, e = [g["pass"] for g in runs(d, "haiku", "original", i)], [g["pass"] for g in runs(d, "haiku", "explicit", i)]
            if not (o and e and all(o) and all(e)): continue
            t = O[i]
            for s in sites(t["reference_sql"]):
                typ = SITE_TO_TYPE.get(s["family"])
                if not typ: continue
                add({"type": typ, "status": "resolved", "action": ACTION["resolved"], "raise": False,
                     "source": {"benchmark": _bench(os.path.basename(d)), "batch": os.path.basename(d), "task": i, "database": t["database"], "question_id": t.get("question_id")},
                     "question": t["instruction"], "gold_sql": t["reference_sql"], "decision": s["hint"], "readings": [],
                     "evidence": {"site": s, "solved": "both wordings correct in every repeat"}, "review": {},
                     "provenance": {"from": "decision site of a question solved in both wordings", "library": VERSION, "built": time.strftime("%Y-%m-%d")}})
    os.makedirs(LIB, exist_ok=True)
    types = [dict(t, status="reviewed", version=1, consumers=t.get("consumers", {"grading": "exact", "inference": "raise when unresolved",
                                                                                  "synthesis": "state, imply or leave open"}),
                  history=[{"version": 1, "date": time.strftime("%Y-%m-%d"), "change": "seeded from the diagnosis tags and the site families"}]) for t in TYPES]
    pf = LIB + "/types_provisional.json"
    if os.path.exists(pf): types += json.load(open(pf))
    json.dump(types, open(LIB + "/types.json", "w"), indent=1)
    for name, rows in (("examples", ex), ("defects", defects), ("candidates", cand)):
        with open("%s/%s.jsonl" % (LIB, name), "w") as f:
            for x in rows: f.write(json.dumps(x, default=str) + "\n")
    json.dump(inference_view(), open(LIB + "/inference_view.json", "w"), indent=1)
    print("types %d; examples %d (raise %d, stay silent %d); defects %d; candidates %d" % (len(types), len(ex), sum(e["raise"] for e in ex),
          sum(not e["raise"] for e in ex), len(defects), len(cand)))


def load():
    T = {t["id"]: t for t in json.load(open(LIB + "/types.json"))}
    E = [json.loads(l) for l in open(LIB + "/examples.jsonl")]
    return T, E


def regress():
    """Every example maps to an existing type, and its mapping rule still gives that type; every type has examples; no source
    task is both 'raise' and 'stay silent' for one type; no held-out question; statuses are known."""
    T, E = load(); held = _heldout(); bad = []
    for e in E:
        if e["type"] not in T: bad.append("%s: unknown type %s" % (e["id"], e["type"]))
        if e["status"] not in ACTION or ACTION[e["status"]] != e.get("action") or RAISE[e["status"]] != e["raise"]:
            bad.append("%s: status %s with action %s" % (e["id"], e["status"], e.get("action")))
        if e["source"].get("question_id") in held: bad.append("%s: held-out question" % e["id"])
        site = (e.get("evidence") or {}).get("site")
        if site and SITE_TO_TYPE.get(site["family"]) != e["type"]: bad.append("%s: site rule now gives %s" % (e["id"], SITE_TO_TYPE.get(site["family"])))
    by = collections.defaultdict(set)
    for e in E: by[(e["source"]["batch"], e["source"]["task"], e["type"])].add(e["raise"])
    bad += ["%s: both raise and stay silent" % (k,) for k, v in by.items() if len(v) > 1]
    empty = [t for t in T if not any(e["type"] == t for e in E)]
    # the inference view never carries SQL or diagnosis, and excludes a target's own examples
    V = inference_view(); txt = json.dumps(V)
    for leak in ("gold_sql", "\"sql\"", "inspection", "analysis", "\"review\"", "\"gate\""):
        if leak in txt: bad.append("inference view carries %s" % leak)
    some = next((e for e in E if e.get("readings")), None)
    if some:
        k = "%s:%s" % (some["source"]["batch"], some["source"]["task"])
        if any(x["question"] == some["question"] for t in inference_view(exclude_tasks=[k], per_type=10 ** 6) for x in t["examples"]):
            bad.append("inference view still shows the excluded target %s" % k)
    for e in [x for x in E if x.get("readings")]:                 # every target, not one: its own question never comes back
        k = "%s:%s" % (e["source"]["batch"], e["source"]["task"])
        if any(x["question"] == e["question"] for t in inference_view(exclude_tasks=[k], per_type=10 ** 6) for x in t["examples"]):
            bad.append("inference view shows target %s to itself" % k); break
    L = ["# Regression (%s)\n" % VERSION, "%d examples, %d types; failures: %d; types without any example: %s\n" % (len(E), len(T), len(bad), empty or "none")]
    L += ["- " + b for b in bad[:50]]
    os.makedirs(LIB, exist_ok=True); open(LIB + "/REGRESSION.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:3]))
    return not bad


def report():
    T, E = load(); cand = [json.loads(l) for l in open(LIB + "/candidates.jsonl")]; defects = [json.loads(l) for l in open(LIB + "/defects.jsonl")]
    L = ["# Communication library: coverage (%s)\n" % VERSION,
         "Types are decisions; each example has its own status. 'Raise' = an interpreter should surface it (unresolved, contested, "
         "conflicting); 'stay silent' = the question or its context resolved it. This is coverage of what was observed, not a claim "
         "that every communication issue is known.\n",
         "| type | raise | stay silent | statuses | from records | from solved questions |", "|---|---|---|---|---|---|"]
    for t in T:
        es = [e for e in E if e["type"] == t]
        L.append("| %s | %d | %d | %s | %d | %d |" % (t, sum(e["raise"] for e in es), sum(not e["raise"] for e in es),
                 dict(collections.Counter(e["status"] for e in es)), sum("record" in e["provenance"]["from"] for e in es),
                 sum("site" in e["provenance"]["from"] for e in es)))
    nb = collections.OrderedDict()
    for e in sorted(E, key=lambda e: e["source"]["batch"]):
        if e["raise"]: nb.setdefault(e["source"]["batch"], set()).add(e["type"])
    seen, rate = set(), []
    for b, ts in nb.items(): rate.append("%s +%d" % (b, len(ts - seen))); seen |= ts
    L += ["\n**New types appearing per batch (raise examples):** %s\n" % ", ".join(rate),
          "**Unmatched candidates (provisional):** %d %s\n" % (len(cand), dict(collections.Counter(c.get("tag") for c in cand))),
          "**Reference defects kept out:** %d\n" % len(defects)] + observation_report()
    open(LIB + "/REPORT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


# ---------------------------------------------------------------------------------------------------- matching (model-assisted)
MATCH = """You maintain a library of COMMUNICATION DECISIONS in text-to-SQL: decisions a reader of a request must resolve. A type is a
DISTINCTION plus the rule that resolves it; whether one question states, implies or leaves it open is that example's STATUS, not a
new type. Place the CASE below.

RULES
- Match by the UNDERLYING DECISION (what interpretation varies between the readings), never by similar wording.
- "merged": an existing type explains the decision. Give its id. If this case resolves it under a condition the type does not yet
  list, say so in "new_condition".
- "new provisional type": ONLY when no existing type explains the decision. Give the type: id (snake_case), name, decision (the
  question a reader must answer), applies_when (SQL constructs / schema facts), readings (kinds of alternative), resolution_rules,
  clarification (smallest question). One case justifies a provisional candidate, not a rule.
- "reference defect": the question and the reference disagree (it names a different value, date, entity) -- not a decision.
- "unresolved evidence": the case does not isolate one decision (several things differ, or the readings do not differ in meaning).
- status of THIS example: explicit | recoverable (documentation/evidence settles it) | implied (ordinary convention settles it) |
  unresolved (both readings fit) | contested (reasonable readers disagree) | conflicting (the request contradicts itself or the reference).

EXISTING TYPES
%s

CASE
%s

Answer ONLY JSON: {"outcome": "...", "type": "<id of the existing or new type, or null>", "new_type": {...} or null,
"new_condition": "..." or null, "status": "...", "distinction": "the underlying decision in one sentence", "reason": "one or two sentences"}"""

REVIEW = """You independently review a proposed placement of a case in a library of communication decisions (types are distinctions;
an example's status says whether its question states, implies or leaves the decision open). Judge ONLY: is the outcome right? A
"merged" placement is right when the type's decision is the case's underlying decision; a "new provisional type" is right only when
no existing type explains it; "reference defect" when the question and reference disagree; "unresolved evidence" when no single
decision is isolated.

EXISTING TYPES
%s

CASE
%s

PROPOSAL
%s

Answer ONLY JSON: {"agree": true|false, "outcome": "<your outcome if you disagree>", "type": "<your type id if you disagree>",
"reason": "one or two sentences"}"""


def _types_text(T):
    return "\n".join("- %s: %s | decision: %s | readings: %s | resolved by: %s" % (t["id"], t["name"], t["decision"], "; ".join(t["readings"]),
                     "; ".join(t["resolution_rules"])) for t in T)


def _case_text(c):
    rd = "\n".join("  %s: %s\n    SQL: %s\n    rows: %s; changes the answer: %s" % (x.get("id"), x.get("reading"), (x.get("sql") or "")[:600], x.get("rows"),
                   x.get("differs_from_gold")) for x in c.get("readings") or [])
    rv = "; ".join("%s: %s" % (r.get("reviewer"), r.get("fit")) for r in (c.get("review") or []))
    return "QUESTION + EVIDENCE: %s\nREFERENCE SQL: %s\nRECORDED DECISION: %s\nREADINGS:\n%s\nBLIND REVIEWERS (fit per reading): %s\nRECORD STATUS: %s" % (
        c.get("question"), (c.get("gold_sql") or "")[:800], c.get("decision"), rd, rv, c.get("record_status"))


def match(workers=4):
    """Every unmatched candidate: opus proposes, sonnet reviews independently. Agreement is accepted; disagreement stays
    unresolved with both verdicts. Accepted new types are provisional (library/types_provisional.json). Outcomes append to
    library/matches.jsonl (one line per candidate; earlier lines kept, later ones win)."""
    import concurrent.futures as cf
    from specbridge.comm.common.llm import ask_json
    T = list(json.load(open(LIB + "/types.json"))); C = [json.loads(l) for l in open(LIB + "/candidates.jsonl")]
    done = _matches(); C = [c for c in C if c["source"] not in done or done[c["source"]]["outcome"].startswith("unresolved (")]
    tt = _types_text(T); cache = LIB + "/cache"
    def one(c):
        ct = _case_text(c)
        p = ask_json(MATCH % (tt, ct), "opus", cache=cache) or {"outcome": "UNPARSED"}
        r = ask_json(REVIEW % (tt, ct, json.dumps(p)), "sonnet", cache=cache) or {"agree": None}
        ok = r.get("agree") is True and p.get("outcome") != "UNPARSED"
        out = {"source": c["source"], "outcome": p.get("outcome") if ok else "unresolved (matcher and reviewer disagree)" if r.get("agree") is False else "unresolved (a call failed)",
               "type": p.get("type") if ok else None, "status": p.get("status"), "proposal": p, "review": r, "date": time.strftime("%Y-%m-%d")}
        return out
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: res = list(ex.map(one, C))
    with open(LIB + "/matches.jsonl", "a") as f:
        for m in res: f.write(json.dumps(m, default=str) + "\n")
    # accepted new types, merged by id across cases; provisional until reviewed
    pf = LIB + "/types_provisional.json"; prov = {t["id"]: t for t in (json.load(open(pf)) if os.path.exists(pf) else [])}
    for m in res:
        if m["outcome"] == "new provisional type" and m["proposal"].get("new_type"):
            nt = m["proposal"]["new_type"]; tid = m["type"] or nt.get("id")
            t = prov.setdefault(tid, dict({k: nt.get(k) for k in ("name", "decision", "applies_when", "readings", "resolution_rules", "clarification")},
                                          id=tid, status="provisional", version=1, cases=[], consumers={"grading": "exact", "inference": "raise when unresolved",
                                          "synthesis": "state, imply or leave open"}, history=[{"version": 1, "date": time.strftime("%Y-%m-%d"),
                                          "change": "proposed by matching; provisional until its distinction and applicability are reviewed"}]))
            t["cases"].append(m["source"]); m["type"] = tid
    for t in prov.values():
        for k in ("readings", "resolution_rules"):
            if not isinstance(t.get(k), list): t[k] = [t.get(k)] if t.get(k) else []
    json.dump(list(prov.values()), open(pf, "w"), indent=1)
    print(json.dumps(collections.Counter(m["outcome"] for m in res)))
    return res


# ---------------------------------------------------------------------------------------------------- the two views
INFERENCE_FIELDS = ("id", "name", "decision", "applies_when", "readings", "resolution_rules", "clarification", "status")


def inference_view(exclude_tasks=(), exclude_question_ids=(), per_type=6):
    """RESTRICTED VIEW for an interpreter at inference time: per type, its definition and a few examples reduced to what an asker
    would see -- the question's words, the decision, the readings in words, the status and the action. NEVER a gold SQL, a reading's
    SQL, the diagnosis (inspection, analysis, reviews, gate) or any example from the target itself (`exclude_tasks`: source keys
    "batch:task"; `exclude_question_ids`). Held-out questions are never in the library. Ask examples first, then inspect, then none."""
    T, E = load(); ex_t, ex_q = set(exclude_tasks), set(exclude_question_ids)
    # the target is excluded by IDENTITY, not by record: its task keys, question ids, and every record of the same question
    # (a revision or a copy can carry another task id)
    norm = lambda q: " ".join(str(q or "").split()).lower()
    ex_text = {norm(e["question"]) for e in E if "%s:%s" % (e["source"]["batch"], e["source"]["task"]) in ex_t or e["source"].get("question_id") in ex_q}
    order = {"ask": 0, "inspect": 1, "none": 2}; out = []
    for tid, t in T.items():
        es = [e for e in E if e["type"] == tid and "%s:%s" % (e["source"]["batch"], e["source"]["task"]) not in ex_t
              and e["source"].get("question_id") not in ex_q and norm(e["question"]) not in ex_text and e.get("readings")]
        es.sort(key=lambda e: (order[e["action"]], e["id"]))
        out.append(dict({k: t.get(k) for k in INFERENCE_FIELDS}, action_rule={"ask": "the context cannot settle it: ask",
                        "inspect": "the context settles it by looking: read documentation/evidence/data, proceed silently", "none": "nothing to do"},
                        examples=[{"question": e["question"], "database": e["source"].get("database"), "decision": e["decision"],
                                   "readings": [x.get("reading") for x in e["readings"]], "status": e["status"], "action": e["action"]} for e in es[:per_type]]))
    return out


def synthesis_view():
    """FULL VIEW for synthetic generation: every example with its executable readings (SQL, rows, whether each changes the answer),
    status, evidence and reviews -- what a controlled wording change needs. Never used at inference."""
    T, E = load()
    return {"types": list(T.values()), "examples": E}


# ---------------------------------------------------------------------------------------------------- requirement-level evidence
REQ_STATUS = {"stated": "explicit", "via_evidence": "recoverable", "implied": "implied", "left_open": "unresolved", "contradicted": "conflicting"}
TYPE_REQS = """Type each REQUIREMENT of each task below by the DECISION it settles, using the library's types (by the underlying decision,
not similar wording). Use "none" when the requirement is not a decision a reader could get wrong (e.g. which table holds the data, a
filter the question states literally with nothing to interpret), and "unplaced" when it is a decision no type covers.

TYPES
%s

TASKS
%s

Answer ONLY JSON: [{"task": "<key>", "types": ["<type id | none | unplaced>", ... one per requirement, in order]}]"""
REVIEW_REQS = """Independently check this typing of requirements by communication decision (types below; "none" = not a decision a
reader could get wrong; "unplaced" = a decision no type covers). For each requirement, agree or give your type.

TYPES
%s

TASKS WITH THE PROPOSED TYPES
%s

Answer ONLY JSON: [{"task": "<key>", "agree": [true|false, ... one per requirement], "yours": ["<type or null>", ...]}]"""


def observe(workers=4, per_call=4):
    """The per-requirement statuses of the communication analyses, typed (opus) and independently checked (sonnet), grouped by
    source task -> library/observations.jsonl. A requirement whose typing the reviewer rejects is kept as 'unplaced (disputed)'."""
    import concurrent.futures as cf
    from specbridge.comm.common.llm import ask_json
    T = json.load(open(LIB + "/types.json")); tt = _types_text(T); cache = LIB + "/cache"; held = _heldout()
    recs = {}
    for r in map(json.loads, open(SRC + "/library.jsonl")):
        a = r.get("analysis") or {}
        if a.get("requirements") and r.get("question_id") not in held: recs[_key(r["source"], r["task"])] = (r, a["requirements"])
    keys = sorted(recs)
    def block(k, with_types=None):
        r, reqs = recs[k]
        lines = ["--- TASK %s\nQUESTION + EVIDENCE: %s\nREFERENCE SQL: %s" % (k, r.get("original"), (r.get("gold_sql") or "")[:600])]
        for i, q in enumerate(reqs):
            lines.append("  R%d: %s  [how the question carries it: %s; phrase: %s]%s" % (i + 1, q.get("requirement"), q.get("real"), q.get("phrase"),
                         ("  -> proposed: %s" % with_types[i]) if with_types and i < len(with_types) else ""))
        return "\n".join(lines)
    def one(ks):
        got = ask_json(TYPE_REQS % (tt, "\n\n".join(block(k) for k in ks)), "opus", brace="[", cache=cache) or []
        prop = {x.get("task"): x.get("types") or [] for x in got}
        rv = ask_json(REVIEW_REQS % (tt, "\n\n".join(block(k, prop.get(k)) for k in ks)), "sonnet", brace="[", cache=cache) or []
        rev = {x.get("task"): x for x in rv}; out = []
        for k in ks:
            r, reqs = recs[k]; ps = prop.get(k, []); rk = rev.get(k, {})
            for i, q in enumerate(reqs):
                p = ps[i] if i < len(ps) else None; ag = (rk.get("agree") or [])[i] if i < len(rk.get("agree") or []) else None
                yours = (rk.get("yours") or [])[i] if i < len(rk.get("yours") or []) else None
                typ = p if (p and ag is True) else ("unplaced (disputed)" if ag is False else "unplaced (a call failed)")
                out.append({"task": k, "database": r.get("database"), "question_id": r.get("question_id"), "n": i + 1, "requirement": q.get("requirement"),
                            "phrase": q.get("phrase"), "real": q.get("real"), "status": REQ_STATUS.get(q.get("real"), q.get("real")),
                            "action": ACTION.get(REQ_STATUS.get(q.get("real"))), "type": typ, "proposed": p, "reviewer": yours if ag is False else p})
        return out
    groups = [keys[i:i + per_call] for i in range(0, len(keys), per_call)]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: res = [x for g in ex.map(one, groups) for x in g]
    with open(LIB + "/observations.jsonl", "w") as f:
        for x in res: f.write(json.dumps(x, default=str) + "\n")
    c = collections.Counter(x["type"] for x in res)
    print("requirements %d from %d tasks; typed %s" % (len(res), len(keys), dict(c.most_common())))


def observation_report():
    """Per type: how many SOURCE TASKS carry the decision with each status (a task counts once per type and status)."""
    if not os.path.exists(LIB + "/observations.jsonl"): return []
    X = [json.loads(l) for l in open(LIB + "/observations.jsonl")]
    by = collections.defaultdict(lambda: collections.defaultdict(set))
    for x in X: by[x["type"]][x["status"]].add(x["task"])
    tasks = len({x["task"] for x in X})
    L = ["\n## Requirement-level evidence (%d requirements from %d source tasks; counted in TASKS)\n" % (len(X), tasks),
         "From the communication analyses of the two-reading records (failure cases: they over-represent decisions left open).\n",
         "| type | explicit | recoverable | implied | unresolved | conflicting |", "|---|---|---|---|---|---|"]
    for t in sorted(by, key=lambda t: -sum(len(v) for v in by[t].values())):
        L.append("| %s | %s |" % (t, " | ".join(str(len(by[t].get(s, ()))) for s in ("explicit", "recoverable", "implied", "unresolved", "conflicting"))))
    return L


if __name__ == "__main__":
    {"build": build, "regress": lambda: sys.exit(0 if regress() else 1), "report": report, "match": match, "observe": observe}[sys.argv[1]]()
