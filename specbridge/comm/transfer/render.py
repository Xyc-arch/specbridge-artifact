"""RENDER one choice point per task into precise and open natural questions, then review them.
  select   one point per task with a load-bearing, accepted point: mutually recognized before disputed, then renders, then
           list order
  write    ONE writer call per database batch (<= 3 tasks), in order inside the answer: 1 plan (shared requirements / choice A /
           choice B / evidence; every V component in shared or choice, checked by code; readings without outcomes), 2 precise A,
           3 precise B as exact edits of precise A (reproduced by code), 4 open (keeps shared requirements, favours neither)
  review   batched, opus and sonnet, two SEPARATE prompts: fidelity (each version against its requirements; no evidence shown)
           and interpretation (interp-v7: preferred | defensible | rejected per reading)
  revise   one rewrite for failing tasks, then re-review
  survive  plan complete, B edits reproduce, fidelity clean, precise A/B select their own reading (both reviewers), open
           accepted by at least one reviewer (labels kept: mutually recognized open | disputed open)
    python -m specbridge.comm.transfer.render <out dir> [--cp <choice-point dir>] [--tasks name=path ...] [--seeds <seeds.jsonl>] select | write | review | revise | survive"""
import collections, concurrent.futures as cf, json, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose.library import example_for
from specbridge.comm.transfer import choice_points as CP
WORKERS = int(os.environ.get("TRANSFER_WORKERS", 6))      # concurrent model calls (API-bound)
D = "out/p_gamma/rcp"; INVENTORY = "out/p_gamma/cp/inventory.json"
fits = lambda v: v in ("preferred", "defensible")

INTERP = """Judge this as a human analytical request, not an executable program. For each reading, ask whether a reasonable reader
could infer it from the wording, evidence and documentation. Distinguish your preferred reading from other defensible readings.
Do not reject a reading merely because its SQL requires an unstated operation. Reject it when it contradicts the request or
requires an unsupported assumption. Explain the decisive phrase or contextual fact.

REQUEST: \"\"\"%s\"\"\"
Two readings of one choice (random order):
   R1: %s
   R2: %s
Answer ONLY JSON: {"readings": [{"reading": "R1", "verdict": "preferred|defensible|rejected", "decisive": "the phrase or fact", "why": "..."},
{"reading": "R2", "verdict": "...", "decisive": "...", "why": "..."}]}

SCHEMA:
%s

DOCUMENTATION:
%s"""

INTERP_HEAD = INTERP.split("REQUEST:")[0].strip()

WRITE = """You render data questions for tasks where ONE interpretation choice is to be left open. For EACH task, work in order:
1. PLAN. Sort everything the explicit specification requires into: "shared" (holds under both readings: population, joins,
   grouping, formulas, missing values vs empty strings, output columns and order, rounding, ordering, limit size ...),
   "choice_A" / "choice_B" (the one decision, settled each way) and "evidence" (facts for checking answers -- row counts, tie
   counts, NULL counts -- that no question needs to state). Label each shared/choice item with a COMPONENT from the task's
   list; every component must appear. Also restate readings A and B WITHOUT any outcome on the data (no counts, no result rows).
2. PRECISE A: one natural question meaning exactly reading A -- every shared requirement and choice A, conveyed naturally,
   nothing omitted, changed or added. Name columns in backticks where a label alone would be unclear.
3. PRECISE B: exact text edits to precise A ({"from": substring of precise A, "to": replacement}) that settle the choice as B
   instead; change nothing else. Give the resulting text too.
4. OPEN: the question a person might ask without having thought about this choice: a careful reader could take it as A or B.
   Treat A and B symmetrically; you may rewrite freely; keep every shared requirement; say nothing that settles the choice and
   do not mention that a choice exists. List the phrases of precise A / B that favour a reading and how OPEN avoids them.
%s
Answer ONLY JSON: [{"task": "<id>", "shared": [{"component": "...", "requirement": "..."}], "choice_A": [...], "choice_B": [...],
"evidence": ["..."], "reading_A": "...", "reading_B": "...", "precise_A": "...", "edits_B": [{"from": "...", "to": "..."}],
"precise_B": "...", "favouring_phrases": [{"phrase": "...", "favours": "A|B", "handling": "..."}], "open": "..."}]

DATABASE %s -- SCHEMA:
%s

DOCUMENTATION:
%s

%s"""

FIDEL = """Fidelity review. Each ITEM gives a data QUESTION and the REQUIREMENTS it must keep. For EACH requirement, judge the question:
preserved (quote the words that carry it; natural paraphrase counts) | omitted | changed | contradicted. Then list anything the
question ADDS: a condition, output or rule neither required nor implied by the requirements (an explanation of a listed
requirement is not added). Judge each item alone.
%s
Answer ONLY JSON: [{"item": "<id>", "requirements": [{"requirement": "...", "verdict": "...", "evidence": "..."}], "added": [...]}]

SCHEMA:
%s

DOCUMENTATION:
%s"""

INTERPB = INTERP_HEAD + """

Each ITEM below is a separate REQUEST with two readings of one choice (random order). Judge each item alone.
%s
Answer ONLY JSON: [{"item": "<id>", "readings": [{"reading": "R1", "verdict": "preferred|defensible|rejected", "decisive": "the phrase or fact", "why": "..."},
{"reading": "R2", "verdict": "...", "decisive": "...", "why": "..."}]}]

SCHEMA:
%s

DOCUMENTATION:
%s"""


def J(name, default=None):
    p = "%s/%s" % (D, name)
    return json.load(open(p)) if os.path.exists(p) else default


def W(name, obj): os.makedirs(D, exist_ok=True); json.dump(obj, open("%s/%s" % (D, name), "w"), indent=1, default=str)


def libkind(kind):
    """A proposer's free-text kind -> the library's choice tag (the first rule that matches)."""
    k = kind.lower()
    for words, tag in ((("tie",), "tie"), (("aggregation", "per record", "per entity", "weighting", "mean of", "average of"), "aggregation_level"),
                       (("unit", "count", "duplicate", "distinct"), "counting_unit"), (("sentinel", "missing", "null", "empty"), "missing_values"),
                       (("signed", "absolute", "formula", "ratio", "denominator", "percentage"), "calculation"), (("role", "join path"), "relationship_role"),
                       (("time", "date", "boundary", "inclusive"), "time_scope"), (("which column", "column source"), "which_column_source"),
                       (("code", "stored value", "label"), "value_mapping")):
        if any(w in k for w in words): return tag
    return k


def task_facts(t):
    """Facts from the reference answer and SQL: missing values and empty strings per output column, rounding, limit and tie."""
    import re
    rows = t["reference_answer"]; out = []; ncol = len(rows[0]) if rows else 0
    for j in range(ncol):
        nn = sum(1 for r in rows if r[j] is None); es = sum(1 for r in rows if r[j] == "")
        if nn or es: out.append("output column %d: %d missing (NULL) values, %d empty strings" % (j + 1, nn, es))
    out.append("the reference SQL %s" % ("rounds with ROUND" if "ROUND(" in t["reference_sql"].upper() else "does not round any output"))
    m = re.search(r"LIMIT (\d+)", t["reference_sql"])
    if m: out.append("row limit %s%s" % (m.group(1), "; a tie falls at the cut: %d rows tie with the last kept one" % len(t["last_pool"]) if t.get("last_pool") else "; no tie at the cut"))
    out.append("answer A has %d rows and %d columns" % (len(rows), ncol))
    return out


def select():
    """One point per task. With RENDER_TARGET set (2026-10-03), STRATIFIED: tasks in a seeded order, each takes its accepted
    load-bearing point of the least-used decision type that is under its cap (aggregation level <= RENDER_CAP_TYPE of the
    target; other types uncapped), databases capped at RENDER_CAP_DB, until RENDER_TARGET points. Without it, the
    original rule (mutually recognized first, then renders, then list order)."""
    V = json.load(open(INVENTORY)); S = {}
    pref = lambda pts, p: (p["label"] != "mutually recognized", not p["renders"], pts.index(p))
    cand = {k: sorted([p for p in (pts if pts != "UNPARSED" else []) if p["load_bearing"] and p.get("label") in ("mutually recognized", "disputed")],
                      key=lambda p, pts=pts: pref(pts, p)) for k, pts in V.items()}
    cand = {k: v for k, v in cand.items() if v}
    target = int(os.environ.get("RENDER_TARGET", 0))
    if not target:
        S = {k: v[0] for k, v in cand.items()}
    else:
        cap_t = float(os.environ.get("RENDER_CAP_TYPE", 0.4)) * target; cap_db = int(os.environ.get("RENDER_CAP_DB", 25))
        T = {t["key"]: t for t in CP.tasks()}; ty, dbn = collections.Counter(), collections.Counter()
        order = sorted(cand); random.Random(int(os.environ.get("RENDER_SEED", 20261003))).shuffle(order)
        for _pass in range(2):                       # second pass fills remaining places if the first leaves room
            for k in order:
                if k in S or len(S) >= target or dbn[T[k]["database"]] >= cap_db: continue
                ok = [p for p in cand[k] if libkind(p["kind"]) != "aggregation_level" or ty["aggregation_level"] < cap_t]
                if not ok: continue
                p = min(ok, key=lambda p: (ty[libkind(p["kind"])] if _pass == 0 else 0, pref(V[k], p)))
                S[k] = dict(p, type=libkind(p["kind"])); ty[S[k]["type"]] += 1; dbn[T[k]["database"]] += 1
    W("selection.json", S)
    print("selected %d tasks; %s; types %s" % (len(S), dict(collections.Counter(p["label"] for p in S.values())), dict(collections.Counter(libkind(p["kind"]) for p in S.values()))))


def ledgers():
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.spec import render as R
    from specbridge.comm.verbal import verbalize as VZ
    T = {t["key"]: t for t in CP.tasks()}; out = {}
    for k in J("selection.json"):
        cat = DB.catalogue(T[k]["database"])
        try: out[k] = VZ.ledger(R.spec(lift(T[k]["reference_sql"], cat.con), cat), cat)[1]
        except Exception: out[k] = None
    return out


def write(keys=None, feedback=None):
    T = {t["key"]: t for t in CP.tasks()}; S = J("selection.json"); LED = J("ledgers.json") or ledgers(); W("ledgers.json", LED)
    keys = keys or [k for k in S if LED.get(k)]; Wr = J("written.json", {}); by = collections.defaultdict(list)
    for k in keys: by[T[k]["database"]].append(k)
    jobs = [(db, ks[i:i + 3]) for db, ks in by.items() for i in range(0, len(ks), 3)]
    def one(job):
        db, ks = job; schema, docs = DB.context(T[ks[0]]); ex = ""
        for k in (ks if not os.environ.get("RENDER_NO_EXAMPLE") else []):      # condition "no retrieved example" (2026-10-03)
            e, _ = example_for(libkind(S[k]["kind"]))
            if e and e not in ex: ex += e
        body = "\n\n".join("--- TASK %s\nCOMPONENTS: %s\nEXPLICIT SPECIFICATION (reading A): %s\nSQL A: %s\nSQL B: %s\nTHE CHOICE: %s\nREADING A: %s\nREADING B: %s\nDATA FACTS: %s%s" % (
            k, LED[k], T[k]["instruction"].split("\nConventions")[0], T[k]["reference_sql"], S[k]["sql_B"], S[k]["decision"], S[k]["reading_A"], S[k]["reading_B"],
            "; ".join(task_facts(T[k])), ("\nREVISION -- your previous rendering failed review: %s\nPREVIOUS: %s" % (feedback[k], json.dumps({x: Wr[k].get(x) for x in ("precise_A", "precise_B", "open")}))) if feedback else "")
            for k in ks)
        r = ask_json(WRITE % ((("RETRIEVED ANALYSES of real questions that left such choices open:\n" + ex) if ex else ""), db, schema, docs, body), "opus", brace="[") or []
        return {d.get("task"): d for d in r if isinstance(d, dict)}
    got = {}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex_:
        for d in ex_.map(one, jobs): got.update(d)
    for k in keys:
        w = got.get(k) or {"error": "unparsed"}
        cov = {r.get("component") for r in (w.get("shared") or []) + (w.get("choice_A") or [])}
        w["missing_components"] = [e for e in LED[k] if e not in cov] if not w.get("error") else LED[k]
        w["B_reproduced"] = bool(w.get("precise_A")) and DB.apply_edits(w["precise_A"], w.get("edits_B"))[0] == w.get("precise_B")
        w["round"] = 1 if feedback else 0
        if feedback: w["previous"] = Wr.get(k)
        Wr[k] = w
    W("written.json", Wr)
    print("written %d; missing components %d; B edits reproduce %d" % (len(keys), sum(1 for k in keys if Wr[k]["missing_components"]), sum(Wr[k]["B_reproduced"] for k in keys)))


DIRECT = """For each task below, write three natural data questions about the database: PRECISE A means exactly reading A (the
explicit specification and SQL A), PRECISE B means exactly reading B (SQL B), and OPEN is the question a person might ask
without having thought about the choice, so that a careful reader could take it as A or B.
Answer ONLY JSON: [{"task": "<id>", "precise_A": "...", "precise_B": "...", "open": "..."}]

DATABASE %s -- SCHEMA:
%s

DOCUMENTATION:
%s

%s"""


def direct(plans):
    """CONDITION "direct generation" (2026-10-03): one prompt per database batch from the executable pair -- no plan, no
    retrieved example, no revision. For review, each task borrows the requirement lists (shared / choice A / choice B) and
    the reading texts of `plans` (the full pipeline's written.json), so all conditions are reviewed against the same
    requirements."""
    T = {t["key"]: t for t in CP.tasks()}; S = J("selection.json"); P = json.load(open(plans)); keys = [k for k in S if k in P and not P[k].get("error")]
    done = {k: w for k, w in (J("written.json") or {}).items() if not w.get("error")}       # resume: completed drafts are kept
    keys = [k for k in keys if k not in done]
    by = collections.defaultdict(list)
    for k in keys: by[T[k]["database"]].append(k)
    jobs = [(db, ks[i:i + 3]) for db, ks in by.items() for i in range(0, len(ks), 3)]
    def one(job):
        db, ks = job; schema, docs = DB.context(T[ks[0]])
        body = "\n\n".join("--- TASK %s\nEXPLICIT SPECIFICATION (reading A): %s\nSQL A: %s\nSQL B: %s\nTHE CHOICE: %s\nREADING A: %s\nREADING B: %s" % (
            k, T[k]["instruction"].split("\nConventions")[0], T[k]["reference_sql"], S[k]["sql_B"], S[k]["decision"], S[k]["reading_A"], S[k]["reading_B"]) for k in ks)
        r = ask_json(DIRECT % (db, schema, docs, body), "opus", brace="[") or []
        return {d.get("task"): d for d in r if isinstance(d, dict)}
    got = {}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex_:
        for d in ex_.map(one, jobs): got.update(d)
    Wr = dict(done)
    for k in keys:
        g = got.get(k) or {}
        Wr[k] = {"shared": P[k]["shared"], "choice_A": P[k]["choice_A"], "choice_B": P[k]["choice_B"], "reading_A": P[k]["reading_A"], "reading_B": P[k]["reading_B"],
                 "precise_A": g.get("precise_A"), "precise_B": g.get("precise_B"), "open": g.get("open"), "condition": "direct",
                 "error": None if g.get("precise_A") and g.get("precise_B") and g.get("open") else "unparsed", "missing_components": [], "B_reproduced": True, "round": 0}
    W("written.json", Wr); print("direct: %d tasks, %d unparsed" % (len(keys), sum(1 for k in keys if Wr[k]["error"])))


def reqs(items): return "; ".join("(%s) %s" % (r.get("component"), r.get("requirement")) for r in items or [])


def review(keys=None, round_=0):
    T = {t["key"]: t for t in CP.tasks()}; Wr = J("written.json", {})
    keys = keys or [k for k, w in Wr.items() if not w.get("error") and not w["missing_components"] and w["B_reproduced"]]
    rng = random.Random(11 + round_); items = collections.defaultdict(list)
    for k in keys:
        w = Wr[k]; need = {"open": w["shared"], "precise_A": w["shared"] + w["choice_A"], "precise_B": w["shared"] + w["choice_B"]}
        for v in ("open", "precise_A", "precise_B"):
            swap = rng.random() < 0.5; r1, r2 = (w["reading_B"], w["reading_A"]) if swap else (w["reading_A"], w["reading_B"])
            items[(T[k]["database"], "interp")].append(("%s|%s" % (k, v), swap, "--- ITEM %s|%s\nREQUEST: \"\"\"%s\"\"\"\n   R1: %s\n   R2: %s" % (k, v, w[v], r1, r2)))
            items[(T[k]["database"], "fidelity")].append(("%s|%s" % (k, v), None, "--- ITEM %s|%s\nQUESTION: \"\"\"%s\"\"\"\nREQUIREMENTS: %s" % (k, v, w[v], reqs(need[v]))))
    jobs = []
    for (db, kind), its in items.items():
        schema, docs = DB.context(next(T[k] for k in keys if T[k]["database"] == db))
        for i in range(0, len(its), 6):
            ch = its[i:i + 6]
            for m in ("opus", "sonnet"): jobs.append((kind, m, ch, (INTERPB if kind == "interp" else FIDEL) % ("\n\n".join(c[2] for c in ch), schema, docs)))
    def one(j):
        kind, m, ch, p = j; got = {d.get("item"): d for d in (ask_json(p, m, brace="[") or []) if isinstance(d, dict)}; out = []
        for iid, swap, _ in ch:
            g = got.get(iid)
            if kind == "fidelity": out.append((kind, iid, m, {"parsed": g is not None, "fail": [x for x in (g or {}).get("requirements", []) if x.get("verdict") != "preserved"], "added": (g or {}).get("added") or []}))
            else:
                rd = {x.get("reading"): x for x in (g or {}).get("readings", []) if isinstance(x, dict)}; a, b = ("R2", "R1") if swap else ("R1", "R2")
                out.append((kind, iid, m, {"parsed": g is not None, "A": rd.get(a, {}), "B": rd.get(b, {})}))
        return out
    RR = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for o in ex.map(one, jobs): RR += o
    rec = {k: {"interp": {}, "fidelity": {}, "round": round_} for k in keys}
    for kind, iid, m, r in RR:
        k, v = iid.split("|"); rec[k][kind]["%s/%s" % (v, m)] = r
    for k in keys: judge(rec[k])
    R = J("review.json", {}); R.update(rec); W("review.json", R)
    print("review round %d: %d tasks; %s" % (round_, len(keys), dict(collections.Counter(rec[k]["status"] for k in keys))))


def judge(rec):
    it, fd = rec["interp"], rec["fidelity"]; v = lambda ver, m, r: (it.get("%s/%s" % (ver, m)) or {}).get(r, {}).get("verdict")
    acc = [m for m in ("opus", "sonnet") if fits(v("open", m, "A")) and fits(v("open", m, "B"))]
    rec["label"] = "mutually recognized open" if len(acc) == 2 else "disputed open" if acc else "not supported"
    rec["precise_selective"] = all(fits(v("precise_A", m, "A")) and v("precise_A", m, "B") == "rejected" and fits(v("precise_B", m, "B")) and v("precise_B", m, "A") == "rejected" for m in ("opus", "sonnet"))
    rec["fidelity_ok"] = len(fd) == 6 and all(r["parsed"] and not r["fail"] and not r["added"] for r in fd.values())
    rec["reasons"] = ([] if rec["fidelity_ok"] else ["fidelity %s: %s" % (key, [i.get("requirement") for i in r["fail"]] + r["added"] if r["parsed"] else "unparsed") for key, r in fd.items() if r["fail"] or r["added"] or not r["parsed"]]) + \
                     ([] if rec["precise_selective"] else ["precise versions not selective"]) + ([] if rec["label"] != "not supported" else ["open: neither reviewer accepts both readings"])
    rec["status"] = "survives" if not rec["reasons"] else "fails"


def revise():
    R = J("review.json"); W("review_round0.json", R); ks = [k for k, r in R.items() if r["status"] == "fails"]
    if not ks: return
    write(ks, feedback={k: R[k]["reasons"] for k in ks}); Wr = J("written.json")
    ok = [k for k in ks if not Wr[k].get("error") and not Wr[k]["missing_components"] and Wr[k]["B_reproduced"]]
    if ok: review(ok, round_=1)


def rereview():
    """A MISSING VERDICT IS NOT A REJECTION (2026-10-03): tasks with any unparsed review item (a failed reviewer call, e.g. a
    usage limit) are reviewed again, both kinds and both reviewers, at the round they were in; nothing else changes."""
    R = J("review.json", {}); Wr = J("written.json", {})
    new = [k for k, w in Wr.items() if k not in R and not w.get("error") and not w.get("missing_components") and w.get("B_reproduced")]
    if new: print("reviewing %d tasks never reviewed" % len(new)); review(new, round_=0); R = J("review.json", {})
    for rnd in sorted({r["round"] for r in R.values()}):
        ks = [k for k, r in R.items() if r["round"] == rnd and any(not x.get("parsed") for x in list(r["interp"].values()) + list(r["fidelity"].values()))]
        if ks: print("re-reviewing %d tasks at round %d" % (len(ks), rnd)); review(ks, round_=rnd)


def survive():
    S = J("selection.json"); Wr = J("written.json", {}); R = J("review.json", {}); LED = J("ledgers.json")
    stop = {k: ("no ledger" if not LED.get(k) else "writer answer unparsed" if Wr.get(k, {}).get("error") else "plan misses a component" if Wr[k]["missing_components"]
                else "precise B edits do not reproduce" if not Wr[k]["B_reproduced"] else R[k]["status"] if k in R else "not reviewed") for k in S}
    sv = [k for k, v in stop.items() if v == "survives"]; W("survivors.json", sv)
    L = ["# Rendering\n", "Outcomes: %s" % dict(collections.Counter(stop.values())), "Survivors by open label: %s" % dict(collections.Counter(R[k]["label"] for k in sv))]
    open(D + "/RENDER.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = CP.configure(sys.argv[1:]); cp = [x[1] for x in a if isinstance(x, tuple)]; a = [x for x in a if not isinstance(x, tuple)]
    D = a[0]
    if cp: INVENTORY = cp[0] + "/inventory.json"
    {"select": select, "write": lambda: write(), "review": lambda: review(), "revise": revise, "survive": survive,
     "direct": lambda: direct(a[2]), "rereview": rereview}[a[1]]()
