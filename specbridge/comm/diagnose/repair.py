"""STEP 6: repair records whose alternative mixes several decisions (gate: medium). Isolate the intended choice (every edit
it requires, and why), re-execute, two blind reviewers re-judge on the ORIGINAL question with a clause diff as locator.
The original record is never changed. A clean repair (both readings fit for both reviewers, both call it one choice, no
qualification applies) becomes a new record beside the original; coupled choices go to coupled.jsonl.
    python -m specbridge.comm.diagnose.repair run <record keys ...> | promote"""
import collections, concurrent.futures as cf, json, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose import LIB
from specbridge.comm.diagnose.gate import key
from specbridge.comm.diagnose.record import ANALYZE

REVISE = """An interpretation record pairs the GOLD query of a real question (reading A) with an alternative (reading B). A reviewer
found that B changes MORE than the intended interpretation choice. Isolate that choice:
  decision      the single intended interpretation choice (plain words)
  reading_B     the alternative reading of that choice only (plain words)
  sql_B         the GOLD SQL changed only as that choice requires. One meaning choice may need several edits (a join, a
                filter, a DISTINCT); make every edit the choice requires and no other.
  edits         each edit: {"edit": "...", "why_required": "..."}
  separable     true if the extra change could be removed; false if it is inseparable from the choice (say why in "note")
Answer ONLY JSON: {"decision": "...", "reading_B": "...", "sql_B": "...", "edits": [], "separable": true, "note": "..."}

ORIGINAL QUESTION + EVIDENCE: %s
GOLD SQL (reading A): %s
READING A: %s
RECORDED READING B: %s
RECORDED SQL B: %s
REVIEWER'S FINDING: %s

SCHEMA:
%s

DOCUMENTATION:
%s"""

REREVIEW = """Independent review of a REAL data question (with its evidence) over the database below. QUESTION:
\"\"\"%s\"\"\"
Two readings (random order), each with its SQL. A clause-level diff of the two SQL queries is given only to help you locate
what differs; it is not proof of anything.
R1: %s
  SQL: %s
R2: %s
  SQL: %s
CLAUSES THAT DIFFER: %s
1. For EACH reading: is it a reasonable reading of the question and evidence? (fits | does not fit), one sentence.
2. Is the difference between R1 and R2 ONE interpretation choice? (yes | no); if no, list the separate choices.
Answer ONLY JSON: {"readings": [{"reading": "R1", "fit": "...", "why": "..."}, {"reading": "R2", "fit": "...", "why": "..."}],
"single_choice": "...", "separate_choices": [...]}

SCHEMA:
%s

DOCUMENTATION:
%s"""

COUPLED_BY_QUALIFICATION = {
    "batch2:b015": "the route through disp leaves owner-only vs any linked person to be decided, and neither the question nor the "
                   "documentation supports the unfiltered choice: the district choice is coupled to an unsupported role choice"}


def run(targets):
    R = {key(json.loads(l)): json.loads(l) for l in open(LIB + "/library.jsonl")}
    def one(k):
        r = R[k]; snap = __import__("specbridge.comm.construct.freeze", fromlist=["snapshot"]).snapshot(r["database"])[0]; schema, docs = DB.context({"snapshot": snap, "database": r["database"]})
        A = next(x for x in r["readings"] if x["id"] == "A"); B = next(x for x in r["readings"] if x["id"] == "B")
        v = ask_json(REVISE % (r["original"], r["gold_sql"], A["reading"], B["reading"], B["sql"], r["gate"]["reason"], schema, docs), "opus")
        if not v: return {"record": k, "outcome": "revision not built"}
        con = DB.connect(snap); rb = DB.rows(con, v["sql_B"])
        if rb is None: return {"record": k, "revision": v, "outcome": "revised B does not run"}
        ra = DB.rows(con, r["gold_sql"]); differs = sorted(map(repr, ra)) != sorted(map(repr, rb)); diff = DB.changed_clauses(r["gold_sql"], v["sql_B"])
        out = {"record": k, "revision": v, "rows_A": len(ra), "rows_B_revised": len(rb), "differs": differs, "clauses_changed": diff}
        if not differs: out["outcome"] = "difference vanished"; return out
        rng = random.Random(hash(k) % 997); revs = []
        for m in ("opus", "sonnet"):
            swap = rng.random() < 0.5
            (r1, s1), (r2, s2) = ((v["reading_B"], v["sql_B"]), (A["reading"], r["gold_sql"])) if swap else ((A["reading"], r["gold_sql"]), (v["reading_B"], v["sql_B"]))
            g = ask_json(REREVIEW % (r["original"], r1, s1, r2, s2, diff, schema, docs), m) or {}
            rd = {x.get("reading"): x for x in g.get("readings", []) if isinstance(x, dict)}; a, b = ("R2", "R1") if swap else ("R1", "R2")
            revs.append({"reviewer": m, "A": rd.get(a, {}).get("fit"), "B": rd.get(b, {}).get("fit"), "single_choice": g.get("single_choice"), "separate_choices": g.get("separate_choices")})
        out["review"] = revs; both = [x["A"] == "fits" and x["B"] == "fits" for x in revs]
        out["outcome"] = "construction fixed" if all(both) else "unsupported" if not any(x["B"] == "fits" for x in revs) else "still disputed"
        return out
    with cf.ThreadPoolExecutor(max_workers=5) as ex: res = list(ex.map(one, targets))
    with open(LIB + "/revisions.jsonl", "a") as f:
        for x in res: f.write(json.dumps(dict(x, version="revise-1"), default=str) + "\n")
    print(dict(collections.Counter(x["outcome"] for x in res)))


def promote():
    R = {key(json.loads(l)): json.loads(l) for l in open(LIB + "/library.jsonl")}; done = {r.get("revision_of") for r in R.values()}
    X = [json.loads(l) for l in open(LIB + "/revisions.jsonl")]; new, coupled = [], []
    for x in X:
        if x["record"] in done: continue
        rv = x.get("review") or []; clean = x["outcome"] == "construction fixed" and all(r.get("single_choice") == "yes" for r in rv)
        if clean and x["record"] not in COUPLED_BY_QUALIFICATION:
            o = R[x["record"]]; v = x["revision"]; A = next(r for r in o["readings"] if r["id"] == "A")
            rec = {k: o[k] for k in ("task", "question_id", "database", "original", "explicit", "gold_sql", "tags", "source")}
            rec.update(version="comm-library-v2", revision_of=x["record"], decision=v["decision"], status="mutually recognized (revised)",
                       readings=[A, {"id": "B", "reading": v["reading_B"], "sql": v["sql_B"], "rows": x["rows_B_revised"], "differs_from_gold": True}],
                       review=[{"reviewer": r["reviewer"], "fit": {"A": r["A"], "B": r["B"]}, "single_choice": r["single_choice"]} for r in rv],
                       repair={"edits": v.get("edits"), "separable": v.get("separable"), "note": v.get("note")})
            A_ = ask_json(ANALYZE % ("--- TASK %s\nREAL QUESTION + EVIDENCE: %s\nEXPLICIT (gold): %s\nGOLD SQL: %s\nREADING A: %s\n  SQL A: %s\nREADING B: %s\n  SQL B: %s" % (
                rec["task"], rec["original"], rec["explicit"], rec["gold_sql"], A["reading"], rec["gold_sql"], v["reading_B"], v["sql_B"])), "opus", brace="[")
            rec["analysis"] = A_[0] if A_ else None; rec["task"] += "r"; new.append(rec)
        elif x["outcome"] == "construction fixed" or x["record"] in COUPLED_BY_QUALIFICATION:
            coupled.append({"record": x["record"], "why": COUPLED_BY_QUALIFICATION.get(x["record"]) or json.dumps([r.get("separate_choices") for r in rv]), "revision": x["revision"]})
    with open(LIB + "/library.jsonl", "a") as f:
        for r in new: f.write(json.dumps(r, default=str) + "\n")
    with open(LIB + "/coupled.jsonl", "a") as f:
        for c in coupled: f.write(json.dumps(c, default=str) + "\n")
    print("promoted %d; coupled %d" % (len(new), len(coupled)))


if __name__ == "__main__":
    a = sys.argv[1:]
    run(a[1:]) if a[0] == "run" else promote()
