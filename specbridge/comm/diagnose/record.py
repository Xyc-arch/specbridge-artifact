"""STEP 4: separate the causes and record the interpretation choices. Candidates are inspected tasks whose question does
not determine the reference's choice (not a plain agent mistake, not a tool defect). Per candidate: the choice, reading A
(the reference) and reading B, B's SQL as a minimal edit of the reference, further readings; B must execute and change the
answer; two blind reviewers judge every reading on the ORIGINAL question (mutually recognized | disputed | one-sided); the
communication analysis records how the real question carries each requirement of explicit V. Records append to the library.
    python -m specbridge.comm.diagnose.record run <dir> <model>"""
import collections, concurrent.futures as cf, json, random, re, sys, zlib
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose import LIB
from specbridge.comm.diagnose.compare import runs, tasks
VERSION = "comm-library-v2"

CHOICE = ["tie", "which_column_source", "missing_values", "counting_unit", "aggregation_level", "time_scope", "relationship_role",
          "value_mapping", "output_form", "other"]

STRUCT = ["aggregation_over_join", "extreme_selection", "repeated_entity_records", "ratio", "grouping", "filter_only", "other"]

SEMANT = ["entity_vs_event", "dated_attributes", "competing_roles", "coded_values", "shared_column_names", "other"]

PAIR = """A BIRD question was answered differently from its gold query by an agent. An inspection suggests the question may not
determine the gold's choice. Build the interpretation record:
  decision     the one choice the gold and the agent's reading differ on
  reading_A    the gold's reading (plain words)
  reading_B    the agent's reading (plain words), if it is a reading of the question at all
  sql_B        the GOLD SQL changed MINIMALLY to implement reading_B (only the decision changes; keep everything else)
  further      other plausible readings of the same decision, each {"reading": "...", "sql": "..."} (may be empty)
  tags         choice: one of %s; structure: list from %s; semantics: list from %s
If the agent's answer is not a reading of the question (a plain mistake), set reading_B = "" and sql_B = "".
Answer ONLY JSON: {"decision": "...", "reading_A": "...", "reading_B": "...", "sql_B": "...", "further": [], "tags": {"choice": "...", "structure": [], "semantics": []}}

ORIGINAL QUESTION + EVIDENCE: %s
GOLD SQL: %s
AGENT'S SUBMITTED SQL (failing runs): %s
INSPECTION: %s

SCHEMA:
%s

DOCUMENTATION:
%s"""

REVIEWN = """Independent review of a REAL data question (with its evidence) over the database below. QUESTION:
\"\"\"%s\"\"\"
Readings of one decision in it (random order). For EACH: is it a reasonable reading of the question and evidence? (fits | does not
fit), one sentence. Judge only the wording, evidence, schema and documentation.
%s
Also list any OTHER plausible reading of the same decision not listed, or [].
Answer ONLY JSON: {"readings": [{"reading": "R1", "fit": "...", "why": "..."}], "other_readings": [...]}

SCHEMA:
%s

DOCUMENTATION:
%s"""

ANALYZE = """You compare how a REAL data question communicates a task with an EXPLICIT specification of the same task's gold
query. For each TASK:
1. requirements: go through every requirement the EXPLICIT version states (which records, links, filters, computation,
   output columns, ordering/limit, missing values, ties, duplicates). For each give:
     requirement   (short)
     real          stated | via_evidence | implied (ordinary wording or convention settles it) | left_open | contradicted
     phrase        the exact words of the real question or evidence that carry it (or "" if none)
2. choice: the two SQL readings A and B differ in one decision. Name it, quote the real phrase that leaves it open, and say in
   one sentence why a careful reader could take either reading.
3. pattern: 3-6 short statements of HOW this real question communicates, in abstract terms with no database names
   (e.g. "names the extreme with a singular superlative and states no tie rule").
Answer ONLY JSON: [{"task": "<id>", "requirements": [{"requirement": "...", "real": "...", "phrase": "..."}],
"choice": {"decision": "...", "open_phrase": "...", "why_both": "..."}, "pattern": ["..."]}]

%s"""


def settled(g):
    """The inspector said the question determines the reference's choice: its answer begins with 'yes' (any punctuation)."""
    w = (g.get("question_gap") or "").strip().split()
    return bool(w) and re.sub(r"\W", "", w[0]).lower() == "yes"


def reroute(d):
    """Correct a batch recorded with the old filter (first word exactly 'yes'): a record whose inspection says the question settles
    it is moved to other_causes, and its rows leave library.jsonl. No model calls. -> the tasks moved"""
    G = {g["task"]: g for g in json.load(open(d + "/inspection.json"))}; R = json.load(open(d + "/records.json"))
    moved = [r["task"] for r in R["library"] + R["not_library"] if r.get("task") in G and settled(G[r["task"]])]
    if not moved: return []
    json.dump(R, open(d + "/records.before-reroute.json", "w"), indent=1, default=str)
    R["other_causes"] += [{"task": t, "cause": G[t].get("cause"), "question_gap": G[t].get("question_gap"), "difference": G[t].get("difference"),
                           "rerouted": "question settles the choice (inspector answered yes)"} for t in moved]
    R["library"] = [r for r in R["library"] if r.get("task") not in moved]; R["not_library"] = [r for r in R["not_library"] if r.get("task") not in moved]
    json.dump(R, open(d + "/records.json", "w"), indent=1, default=str)
    rows = [l for l in open(LIB + "/library.jsonl") if not (json.loads(l).get("source") == d and json.loads(l).get("task") in moved)]
    open(LIB + "/library.jsonl", "w").writelines(rows)
    return moved


def run(d, model, only=None):
    """only: task ids to record again (after their inspection was redone); their entries replace the old ones in records.json and
    their old rows leave library.jsonl; every other record is kept."""
    T = {t["id"]: t for t in tasks(d, "original")}; E = {t["id"]: t for t in tasks(d, "explicit")}; G = json.load(open(d + "/inspection.json"))
    if only: G = [g for g in G if g["task"] in set(only)]
    cand = [g for g in G if g.get("category") != "contradiction" and not settled(g) and not str(g.get("cause", "")).startswith("renderer")]
    other = [{"task": g["task"], "cause": g.get("cause"), "question_gap": g.get("question_gap"), "difference": g.get("difference")} for g in G if g not in cand]
    def one(g):
        t = T[g["task"]]; schema, docs = DB.context(t); con = DB.connect(t["snapshot"])
        fails = [x.get("final") for x in runs(d, model, "original", g["task"]) if not x["pass"] and x.get("final")]
        p = ask_json(PAIR % (CHOICE, STRUCT, SEMANT, t["instruction"], t["reference_sql"], " || ".join(fails)[:2500],
                             json.dumps({k: g.get(k) for k in ("cause", "difference", "question_gap")}), schema, docs), "opus")
        if not p: return {"task": g["task"], "status": "pair not built"}
        if not p.get("sql_B"): return {"task": g["task"], "status": "agent mistake (no reading)", "pair": p}
        a = t["reference_answer"]; b = DB.rows(con, p["sql_B"])
        readings = [("A", p["reading_A"], t["reference_sql"], a), ("B", p["reading_B"], p["sql_B"], b)]
        for i, f in enumerate(p.get("further") or []):
            if f.get("sql"): readings.append(("C%d" % i, f.get("reading"), f["sql"], DB.rows(con, f["sql"])))
        diff = lambda x: x is not None and sorted(map(repr, x)) != sorted(map(repr, a))
        if not diff(b): return {"task": g["task"], "status": "reading B gives the reference answer or does not run", "pair": p}
        rng = random.Random(zlib.crc32(g["task"].encode()) % 1000); revs = []     # replayable (hash() is randomized per process)
        for model_ in ("opus", "sonnet"):
            order = readings[:]; rng.shuffle(order)
            rv = ask_json(REVIEWN % (t["instruction"], "\n".join("R%d: %s" % (i + 1, r[1]) for i, r in enumerate(order)), schema, docs), model_) or {}
            fit = {order[int(x["reading"][1:]) - 1][0]: x.get("fit") for x in rv.get("readings", []) if str(x.get("reading", "")).startswith("R")}
            revs.append({"reviewer": model_, "fit": fit, "other_readings": rv.get("other_readings")})
        status = ("mutually recognized" if all(r["fit"].get("A") == "fits" and r["fit"].get("B") == "fits" for r in revs) else
                  "disputed" if any(r["fit"].get("B") == "fits" for r in revs) and any(r["fit"].get("A") == "fits" for r in revs) else "one-sided")
        rec = {"version": VERSION, "task": g["task"], "question_id": t.get("question_id"), "database": t["database"], "original": t["instruction"],
               "explicit": E[g["task"]]["instruction"].split("\nConventions")[0] if g["task"] in E else None, "gold_sql": t["reference_sql"],
               "decision": p["decision"], "readings": [{"id": r[0], "reading": r[1], "sql": r[2], "rows": len(r[3]) if r[3] is not None else "does not run",
               "differs_from_gold": diff(r[3]) if r[0] != "A" else False} for r in readings], "tags": p.get("tags"), "review": revs, "status": status,
               "inspection": {k: g.get(k) for k in ("cause", "difference", "question_gap", "supplied")}}
        if status != "one-sided" and rec["explicit"]:
            A = ask_json(ANALYZE % ("--- TASK %s\nREAL QUESTION + EVIDENCE: %s\nEXPLICIT (gold): %s\nGOLD SQL: %s\nREADING A: %s\n  SQL A: %s\nREADING B: %s\n  SQL B: %s" % (
                g["task"], t["instruction"], rec["explicit"], t["reference_sql"], p["reading_A"], t["reference_sql"], p["reading_B"], p["sql_B"])), "opus", brace="[")
            rec["analysis"] = A[0] if A else None
        return rec
    with cf.ThreadPoolExecutor(max_workers=4) as ex: out = list(ex.map(one, cand))
    lib = [r for r in out if r.get("status") in ("mutually recognized", "disputed")]
    nl = [r for r in out if r not in lib]
    if only:
        old = json.load(open(d + "/records.json")); json.dump(old, open(d + "/records.before-retry.json", "w"), indent=1, default=str)
        keep = lambda xs: [r for r in xs if r.get("task") not in set(only)]
        lib, nl, other = keep(old["library"]) + lib, keep(old["not_library"]) + nl, keep(old["other_causes"]) + other
        rows = [l for l in open(LIB + "/library.jsonl") if not (json.loads(l).get("source") == d and json.loads(l).get("task") in set(only))]
        open(LIB + "/library.jsonl", "w").writelines(rows)
        out_new = [r for r in lib if r.get("task") in set(only)]
    json.dump({"library": lib, "not_library": nl, "other_causes": other}, open(d + "/records.json", "w"), indent=1, default=str)
    if only: lib = out_new
    with open(LIB + "/library.jsonl", "a") as f:
        for r in lib: f.write(json.dumps(dict(r, source=d), default=str) + "\n")
    print("%s: candidates %d -> library %d (%s); not library %d; other causes %d" % (d, len(cand), len(lib), dict(collections.Counter(r["status"] for r in lib)),
          len(out) - len(lib), len(other)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "reroute": print(reroute(a[1])); sys.exit(0)
    run(a[1], a[2], a[a.index("--only") + 1].split(",") if "--only" in a else None)
