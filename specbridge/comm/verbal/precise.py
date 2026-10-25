"""THE PRECISE NATURAL-QUESTION WRITER (unconditioned): one natural question per task, meaning exactly its explicit specification.
Ported 2026-10-01 from out/lm_natural/workflow2.py at tag lm-writer-frozen-2026-09-28. FROZEN and unchanged: the WRITER and
REVIEWER prompts, the system prompt, the input variant (language+facts), the model (sonnet), one revision, the deterministic
representation-term check, the deterministic skip for simple tasks, the fail-closed check on undefined symbols, the cache key.
Before writing, the database's language resource is ensured for the corpus's gaps (specbridge.comm.verbal.language, cached).
Changed for scale only: imports (the reorganised modules), tasks are sent in BATCHES of up to BATCH per database (each batch
carries its database's meanings once, as before) and batches run concurrently; the output is the corpus itself, paired.
    python -m specbridge.comm.verbal.precise <corpus dir> [--limit N] [--ids a,b]   -> <corpus>/tasks_paired.jsonl, NATURAL.md, corpus.jsonl
    python -m specbridge.comm.verbal.precise <corpus dir> --rereview   -> accepted questions reviewed again ONE task per call (REREVIEW.json)
REVIEW (2026-10-01): one task per review call; writing stays batched.
Each task keeps its SQL, answer, grader and explicit instructions unchanged and gains `natural_precise`:
  question  the natural question; null when the writer's draft was not accepted
  status    passed (round 1) | revised (accepted after the one revision) | deterministic (simple task: the rule-based natural
            question, no model) | not rendered (the draft failed review twice, or a symbol was undefined): no question, and the
            task is not delivered
The DELIVERED corpus is corpus.jsonl (deliver): rendered tasks only, each with its natural question and its explicit
instructions (V, kept: deterministic from the SQL, the reference the natural question is checked against).
  checks    every round's draft and the reviewer's failures per requirement ID (empty = pass); the requirement IDs
The reviewer's verdict is evidence, not proof."""
import collections, hashlib, json, os, random, re, subprocess, sys, time, warnings
warnings.filterwarnings("ignore")
import concurrent.futures as cf, threading
from specbridge.pd.structures.algebra import lift, emit, emit_expr, emit_pred
from specbridge.pd.realize.catalogue import Catalogue
from specbridge.pd.spec import render as R
from specbridge.comm.verbal import verbalize as VZ, gamma as G
MODEL, BUDGET, D = os.environ.get("PRECISE_WRITER_MODEL", "sonnet"), 1, "out/lm_natural"
# WRITER SWAP (2026-10-12): PRECISE_WRITER_MODEL replaces only the writer (write and revise stages), for the writer-by-solver
# crossover (specbridge.comm.construct.writer_swap). The default is the frozen "sonnet"; MODEL is part of the cache key.
# THE REVIEWER IS NOT THE WRITER (2026-10-02). With Sonnet in both roles, a changed output requirement (pilot task 8ac7dd4f7e:
# "step 5's column (1)" where V says column (2)) passed review, passed a single-task recheck, and on a rewrite the reviewer
# itself demanded the wrong column: the two roles made the same misreading. Opus reviews; it is not one of the solvers.
# The pilot (tag pilot-dev-frozen-2026-10-02) ran with "sonnet"; its cache keys are unchanged because the reviewer enters
# the prompt version only when it differs from the writer.
REVIEW_MODEL = os.environ.get("PRECISE_REVIEW_MODEL", "opus")
REVIEW_STAGES = ("review", "recheck", "re-review")
RENDERED = ("passed", "revised", "deterministic")                # statuses that deliver a natural question
VARIANT = os.environ.get("INPUT_VARIANT", "language+facts")      # the frozen choice
BATCH, WORKERS = 8, 6                                            # scale only: tasks per call, concurrent batches
VARIANT_DESC = {"language": "each task's requirements as exact English phrases under stable IDs",
                "language+facts": "each task's requirements as exact English phrases under stable IDs, plus STRUCTURED FACTS "
                                  "(join kind, which records are dropped or kept, multiplicity; window frames; each sort key's "
                                  "direction and where missing values go; the number of outputs)",
                "sql": "each task's requirements as exact SQL clauses with semantic annotations under stable IDs"}[VARIANT]   # "language": V's exact phrase per requirement ID; "sql": SQL clauses + annotations
GM = {"columns": "natural", "values": "natural"}
SYS = "You follow the instructions exactly and answer with JSON only."

WRITER = """Write each task below as a concise, natural question an analyst might ask, for a solver who has the database
(schema and documentation) and must write the SQL.
RULES: preserve every requirement AND every FACT exactly; define every formula symbol you use (give its definition from
the 'definition X' requirements, or say it in words); preserve every requirement exactly (outputs and their order; filters and their parameters; which records a join
drops or keeps; multiplicity: where a join gives one row per match, say so; grouping; formulas, stated exactly unless a name
alone determines them; ordering, where missing values go, limits). Refer to columns by the MEANINGS given; a column listed
as UNRESOLVED keeps its raw name. An output listed as REPRESENTATION may be the stored code or its documented meaning, word
for word -- say that, never list values. A stored code may be said by its documented meaning, unquoted (quotes = stored
values). No purpose, context or extra requirement; no general SQL conventions.
CONVENTIONS OF THE REQUIREMENTS: an INNER join drops a record with no match, a LEFT join keeps it once with missing values;
ORDER ... ASC puts missing values first, DESC last; text compares character by character.
%s
The input below is %s, per database: its MEANINGS once (column: meaning; code meanings; entity names), then its tasks.

%s

Answer with ONLY a JSON list: [{"id": "<task id>", "question": "..."}, ...]"""

REVIEWER = """Check each DRAFT against its REQUIREMENTS. A requirement FAILS when a careful solver could read the draft and
compute something different for it. Check multiplicity, which records are dropped or kept, filters and parameters,
formulas, output order, representation (an output listed as REPRESENTATION may be the stored code or its documented
meaning word for word -- nothing else may be invited), UNRESOLVED columns by raw name, ordering, missing values, limits.
When FACTS are given, check each one explicitly: for EVERY join, that the draft says which records are dropped or kept
exactly as stated (an INNER join must never be described as keeping unmatched records) and its multiplicity; for EVERY
window, its frame; for EVERY sort key, its direction and where missing values go; that every formula symbol the draft uses
is defined in the draft. A fact the draft contradicts or omits is a failure under the requirement it belongs to.
Do not judge style.
CONVENTIONS: INNER join drops unmatched; LEFT keeps once with missing values; ASC missing first, DESC missing last.

%s

Answer with ONLY a JSON list, one object per task: [{"task": "<id>", "failures": [{"id": "<requirement id>", "reason": "..."}]}]
(an empty failures list means the draft passes)."""

USAGE = []
_LOCK = threading.Lock()
CHECK_VERSION = "representation-terms-1"      # part of the cache key: a changed check re-runs the workflow
REVIEW_MODE = "single-task"                    # part of the cache key (2026-10-01): verdicts of the batched review are not reused


def representation_terms(draft, rec):
    """Where a draft explicitly names output codes or decoded labels, they must be the interpretation record's: every term of
    an enumeration that mentions at least one recorded term must be a stored code (exactly), a documented meaning
    (ignoring case, as the grader compares), or an explanation "N = word" of a code N. Returns the failures (empty = ok)."""
    reps = rec.get("representation") or []
    if not reps or not draft: return []
    codes = {str(k) for r in reps for k, _v in r["mapping"]}
    meanings = {str(v).strip().lower() for r in reps for _k, v in r["mapping"]}
    def ok(term):
        t = term.strip().strip("'\"").strip()
        if not t: return True
        if t in codes or t.lower() in meanings: return True
        m = re.fullmatch(r"(\S+)\s*=\s*.+", t)
        return bool(m) and m.group(1).strip("'\"") in codes
    def recorded(term):
        t = term.strip().strip("'\"").strip()
        return t in codes or t.lower() in meanings or t.lower() in {c.lower() for c in codes} or bool(re.fullmatch(r"(\S+)\s*=\s*.+", t))
    fails = []
    for grp in re.findall(r"\(([^()]*)\)", draft) + re.findall(r"(?:either|such as|e\.g\.,?)\s+([^.;:]*)", draft):
        items = [x for x in re.split(r"\s*(?:,\s*or\s+|,|\bor\b|/)\s*", grp) if x.strip()]
        if len(items) < 2 or not any(recorded(x) for x in items): continue
        bad = [x.strip() for x in items if not ok(x)]
        if bad: fails.append({"id": "representation", "reason": "names output values %s that are neither stored codes nor documented meanings in the interpretation record (%s)" % (bad, grp.strip()[:80])})
    return fails


def llm(prompt, stage):
    """One sealed call: minimal system prompt, no tools, empty working directory; returns (text, usage). Review stages use
    REVIEW_MODEL, writing stages MODEL."""
    from specbridge.pd.ask import _SEALED, _CLAUDE
    m = REVIEW_MODEL if stage in REVIEW_STAGES else MODEL
    if m.startswith("gpt-"):                                          # codex route: no usage report; same sealed call
        from specbridge.pd.ask import ask, LIMIT
        res = ask(prompt, m, timeout=1500, quiet=True, system=SYS) or ""
        rec = {"stage": stage, "model": m, "input": 0, "fresh_input": 0, "cached_input": 0, "output": 0, "prompt_chars": len(prompt)}
        with _LOCK: USAGE.append(rec)
        return ("" if LIMIT.search(res) else res), rec
    cmd = [_CLAUDE or "claude", "-p", "--model", REVIEW_MODEL if stage in REVIEW_STAGES else MODEL, "--output-format", "json", "--system-prompt", SYS, "--tools", ""]
    for attempt in range(3):
        try:
            out = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=_SEALED, timeout=1500).stdout
            d = json.loads(out); break
        except Exception:
            d = {}; time.sleep(3)
    u = d.get("usage", {})
    rec = {"stage": stage, "model": REVIEW_MODEL if stage in REVIEW_STAGES else MODEL, "input": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
           "fresh_input": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0), "cached_input": u.get("cache_read_input_tokens", 0),
           "output": u.get("output_tokens", 0), "prompt_chars": len(prompt)}
    with _LOCK: USAGE.append(rec)
    from specbridge.pd.ask import LIMIT
    res = d.get("result", "") or ""
    if d.get("is_error") or LIMIT.search(res): res = ""                 # a limit/error reply is a failed call, not a draft
    return res, rec


def parse_list(text):
    m = re.search(r"\[.*\]", text, re.S)
    try: return json.loads(m.group(0)) if m else []
    except Exception: return []


# ---------------------------------------------------------------- the compact specification
def requirements(p, s, cat, rec):
    """Structured requirements under V's component IDs: exact clauses plus the facts SQL leaves implicit."""
    q = s["query"]; req = {}
    if p.ctes: req["steps"] = [{"name": n, "sql": emit(x)} for n, x in p.ctes]
    req["records"] = "FROM %s" % p.scan.table
    scope = [p.scan.table]
    for k, (j, js) in enumerate(zip(p.scan.joins, q["joins"])):
        rel = VZ.relation(cat, js, scope) if not js["step"] else None
        req["join %d" % (k + 1)] = {"join": "%s JOIN %s ON %s" % (j.kind.upper(), j.table, emit_pred(j.on)),
                                    "multiplicity": ("at most one match per record" if rel and rel[0] == "its" else
                                                     "one row per matching record" if rel else "one row per match (not a key relationship)")}
        scope.append(j.table)
    if p.where is not None: req["record filter"] = emit_pred(p.where)
    if p.group: req["grouping"] = [emit_expr(g) for g in p.group]
    if p.having is not None: req["group filter"] = emit_pred(p.having)
    for i, (e, _a) in enumerate(p.select, 1): req["output %d" % i] = emit_expr(e)
    if p.distinct: req["duplicates removed"] = True
    if p.order: req["ordering"] = ["%s %s" % (emit_expr(e), d.upper()) for e, d in p.order]
    if p.limit is not None: req["limit"] = p.limit
    if p.offset: req["offset"] = p.offset
    extra = {}
    if rec.get("representation"): extra["REPRESENTATION"] = ["output %d" % r["position"] for r in rec["representation"]]
    un = sorted({x["item"] for x in rec.get("unresolved", []) if x.get("kind") == "column"})
    if un: extra["UNRESOLVED"] = un
    return req, extra


def language_requirements(s, cat, rec):
    """The LANGUAGE input variant: each requirement ID with the exact phrase V (gamma explicit) states it with."""
    q = VZ.V(s, "natural", None, cat)
    req = {k: " | ".join(q[a:b] for a, b in v) for k, v in VZ.REPORT.get("spans", {}).items()}
    extra = {}
    if rec.get("representation"): extra["REPRESENTATION"] = ["output %d" % r["position"] for r in rec["representation"]]
    un = sorted({x["item"] for x in rec.get("unresolved", []) if x.get("kind") == "column"})
    if un: extra["UNRESOLVED"] = un
    return req, extra


def facts(s, cat, p):
    """STRUCTURED SEMANTIC FACTS the English must not lose, from the specification (not from any wording)."""
    q = s["query"]; f = {"number of outputs": len(q["outputs"])}
    scope, js = [q["source"]["table"]], []
    for k, j in enumerate(q["joins"], 1):
        rel = VZ.relation(cat, j, scope) if not j["step"] else None
        js.append({"id": "join %d" % k, "kind": j["kind"].upper() if j["kind"] else "INNER",
                   "records without a match": "kept once, with this join's values missing" if j["kind"] == "left" else "dropped",
                   "multiplicity": "at most one match per record" if rel and rel[0] == "its" else "one row per matching record"})
        scope.append(j["table"])
    if js: f["joins"] = js
    w = []
    for o in q["outputs"]:
        for n in G._walk(o["expr"]):
            op = n.get("op")
            if op == "running": w.append({"output": o["position"], "frame": "an aggregate over the rows of its partition, in the stated order, from the first row up to the current row AND every row tied with it on that order"})
            elif op == "within": w.append({"output": o["position"], "frame": "an aggregate over ALL rows of its partition (no order)"})
            elif op == "window": w.append({"output": o["position"], "frame": "%s over the rows of its partition in the stated order (ties as stated)" % n.get("name")})
    if w: f["windows"] = w
    if q["order"]:
        f["sort keys"] = [{"key": i, "direction": o["dir"].upper(), "missing values": "first" if o["dir"] == "asc" else "last",
                           "compared": "as text, character by character" if o["expr"].get("type") == "text" else "as numbers"} for i, o in enumerate(q["order"], 1)]
    if q["limit"] is not None: f["rows returned"] = "the first %s after sorting%s" % (q["limit"], " and skipping %d" % q["offset"] if q["offset"] else "")
    return f


def complicated(s, p, fallbacks):
    js = json.dumps(s)
    return bool(fallbacks) or bool(p.ctes) or len(p.scan.joins) > 1 or any(k in js for k in ('"op": "case"', '"op": "window"', '"op": "within"', '"op": "running"', '"op": "in_query"', '"op": "exists"', '"op": "subquery"')) \
        or any(o["expr"]["op"] in R.ARITH | {"round"} for o in s["query"]["outputs"])


def meanings(db, tasks, cat):
    """The shared context of one database batch: the meanings of the columns the batch uses, entity names, code meanings."""
    lang = G.language(db)["columns"]; labels = G.value_labels(db, cat.con); ents = VZ.entities(cat)
    cols = sorted({c for t in tasks for c in re.findall(r'"(\w[\w ()%.-]*)"\."([^"]+)"', t["sql"])})
    lines = []
    for tb, c in cols:
        lab = lang.get("%s.%s" % (tb, c), {}).get("label") or R._label(cat, tb, c)[0]
        lines.append("%s.%s: %s" % (tb, c, lab))
        if (tb, c) in labels: lines.append("  codes: " + "; ".join("%r = %s" % (k, v) for k, v in labels[(tb, c)].items()))
    ts = sorted({tb for tb, _c in cols})
    lines.append("entities: " + "; ".join("%s = %s" % (tb, ents[tb][0]) for tb in ts if tb in ents))
    return "\n".join(lines)


def key(t, cat, prompt_version):
    lang = open("catalogues/language/%s.json" % t["database"]).read() if os.path.exists("catalogues/language/%s.json" % t["database"]) else ""
    catf = "catalogues/%s.json" % t["database"]; catv = hashlib.sha1(open(catf, "rb").read()).hexdigest() if os.path.exists(catf) else ""
    return hashlib.sha1((t["reference_sql"] + "|" + hashlib.sha1(lang.encode()).hexdigest() + "|" + catv + "|" + prompt_version).encode()).hexdigest()[:20]


def prepare(tasks):
    """Per task: cache hit, deterministic skip, fail-closed fallback, or an item for the writer (as frozen)."""
    os.makedirs(D + "/cache", exist_ok=True)
    pv = hashlib.sha1((WRITER + REVIEWER + SYS + MODEL + str(BUDGET) + VARIANT + CHECK_VERSION + REVIEW_MODE + ("" if REVIEW_MODEL == MODEL else "|reviewer=" + REVIEW_MODEL)).encode()).hexdigest()[:12]
    cats, items, out = {}, [], []
    for t in tasks:
        cat = cats.setdefault(t["database"], Catalogue(t["database"]))
        p = lift(t["reference_sql"], cat.con); s = R.spec(p, cat)
        tk = VZ.task(s, "natural", GM, cat); rec = t.get("record") or tk["record"]
        awkward_now = list(VZ.REPORT.get("awkward", []))
        det = tk["question"].replace("\n" + R.NOTES, "")
        k = key(t, cat, pv); cp = "%s/cache/%s.json" % (D, k)
        base = {"id": t["id"], "database": t["database"], "sql": t["reference_sql"], "explicit": t["instruction"].replace("\n" + R.NOTES, ""), "cache_key": k, "prompt_version": pv}
        if os.path.exists(cp):
            c = json.load(open(cp))
            if not (c.get("history") and not c["history"][-1].get("draft")):      # a missing output is not a verdict: recompute
                out.append(dict(base, **c, cached=True)); continue
        listing = any(x.get("why") == "a slash or parenthesis" for x in awkward_now)
        if not complicated(s, p, tk["record"].get("unresolved")) and not listing:
            r = dict(base, final=det, outcome="deterministic skip (no LM)", history=[])
            json.dump({k2: r[k2] for k2 in ("final", "outcome", "history")}, open(cp, "w")); out.append(r); continue
        req, extra = requirements(p, s, cat, rec) if VARIANT == "sql" else language_requirements(s, cat, rec)
        if VARIANT == "language+facts": extra["FACTS"] = facts(s, cat, p)
        if VARIANT != "sql":
            missing = VZ.undefined_symbols(req)
            if missing:                                    # fail closed BEFORE any model call
                out.append(dict(base, final=base["explicit"], outcome="explicit fallback (undefined symbols %s)" % missing, history=[])); continue
        items.append(dict(base, req=req, extra=extra, cat=cat, cp=cp, rec=rec))
    return items, out


def write_batch(group, ctxs):
    """The frozen write -> review -> (one) revise -> review, on one batch of one database's tasks."""
    spec_of = lambda it: "--- %s\nREQUIREMENTS: %s%s" % (it["id"], json.dumps(it["req"]), ("\n" + json.dumps(it["extra"])) if it["extra"] else "")
    def sections(grp, body):
        g = collections.defaultdict(list)
        for it in grp: g[it["database"]].append(it)
        return "\n\n".join("=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n%s" % (db, ctxs[db], "\n".join(body(it) for it in its)) for db, its in g.items())
    def review(grp):
        """ONE task per review call (2026-10-01): with 8 tasks in sight the reviewer passed unfaithful drafts that the same
        prompt catches with one task (5 of 17); the call carries only this task's column meanings."""
        if not grp: return
        for it in grp:
            ctx1 = {it["database"]: meanings(it["database"], [it], it["cat"])}
            body = "\n\n".join("=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n%s" % (db, ctx1[db], spec_of(it) + "\nDRAFT: " + it["history"][-1]["draft"]) for db in ctx1)
            txt, _u = llm(REVIEWER % body, "review")
            got = {d.get("task"): d.get("failures", None) for d in parse_list(txt)}
            f = got.get(it["id"]); it["history"][-1]["failures"] = f if f is not None else [{"id": "*", "reason": "the reviewer returned nothing"}]
            det = representation_terms(it["history"][-1]["draft"], it["rec"])
            if det: it["history"][-1]["failures"] = list(it["history"][-1]["failures"]) + [dict(x, by="representation check") for x in det]
    txt, _u = llm(WRITER % ("", VARIANT_DESC, sections(group, spec_of)), "write")
    drafts = {d.get("id"): d.get("question", "") for d in parse_list(txt)}
    missing = [it for it in group if not drafts.get(it["id"])]
    for i in range(0, len(missing), 2):          # MISSING OUTPUT (e.g. a long batch cut short): the same prompt, two tasks at a time
        txt, _u = llm(WRITER % ("", VARIANT_DESC, sections(missing[i:i + 2], spec_of)), "write (missing output)")
        drafts.update({d.get("id"): d.get("question", "") for d in parse_list(txt) if d.get("question")})
    for it in group: it["history"] = [{"round": 1, "draft": drafts.get(it["id"], ""), "rewritten_after_missing_output": it in missing}]
    review(group)
    for rnd in range(BUDGET):
        failed = [it for it in group if it["history"][-1]["failures"] or not it["history"][-1]["draft"]]
        if not failed: break
        body = lambda it: spec_of(it) + "\nFAILED: %s\nDRAFT: %s\nFINDINGS: %s" % (
            json.dumps([f.get("id") for f in it["history"][-1]["failures"]]), it["history"][-1]["draft"], json.dumps(it["history"][-1]["failures"]))
        txt, _u = llm(WRITER % ("\nREVISION: fix exactly the findings; every other requirement must stay satisfied.\n", VARIANT_DESC, sections(failed, body)), "revise")
        rev = {d.get("id"): d.get("question", "") for d in parse_list(txt)}
        miss = [it for it in failed if not rev.get(it["id"])]
        for i in range(0, len(miss), 2):
            txt, _u = llm(WRITER % ("\nREVISION: fix exactly the findings; every other requirement must stay satisfied.\n", VARIANT_DESC, sections(miss[i:i + 2], body)), "revise (missing output)")
            rev.update({d.get("id"): d.get("question", "") for d in parse_list(txt) if d.get("question")})
        for it in failed: it["history"].append({"round": rnd + 2, "draft": rev.get(it["id"], "")})
        review(failed)
    res = []
    for it in group:
        ok = not it["history"][-1]["failures"] and it["history"][-1]["draft"]
        r = {k2: it[k2] for k2 in ("id", "database", "explicit", "cache_key", "prompt_version")}
        r.update(final=it["history"][-1]["draft"] if ok else it["explicit"], history=it["history"], requirement_ids=sorted(it["req"]),
                 outcome=("LM-written, accepted on round %d" % len(it["history"])) if ok else "explicit fallback (LM rejected)")
        json.dump({k2: r[k2] for k2 in ("final", "outcome", "history", "requirement_ids")}, open(it["cp"], "w")); res.append(r)
    return res


def status(outcome, history=None):
    if outcome.startswith("explicit fallback (LM rejected)") and history and not history[-1].get("draft"): return "missing output"
    if outcome.startswith("LM-written, accepted on round 1"): return "passed"
    if outcome.startswith("LM-written"): return "revised"
    if outcome.startswith("deterministic"): return "deterministic"
    return "not rendered"


def run_corpus(d, limit=None, ids=None):
    t0 = time.time(); T = [json.loads(l) for l in open(d + "/tasks.jsonl")]
    sel = [t for t in T if (not ids or t["id"] in ids)][: limit or None]
    from specbridge.comm.verbal.language import ensure         # setup step before rendering: names for this corpus's gaps (cached)
    for db in sorted({t["database"] for t in sel}): ensure(db, [t["reference_sql"] for t in sel if t["database"] == db])
    items, out = prepare(sel)
    by = collections.defaultdict(list)
    for it in items: by[it["database"]].append(it)
    ctxs = {db: meanings(db, its, its[0]["cat"]) for db, its in by.items()}
    batches = [its[i:i + BATCH] for its in by.values() for i in range(0, len(its), BATCH)]
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for res in ex.map(lambda g: write_batch(g, ctxs), batches): out.extend(res)
    got = {r["id"]: r for r in out}
    paired = []
    for t in T:
        r = got.get(t["id"])
        if r is None: continue
        st = status(r["outcome"], r.get("history"))
        paired.append(dict(t, natural_precise={"question": r["final"] if st in RENDERED else None, "status": st, "outcome": r["outcome"],
                                              "checks": r.get("history", []), "requirement_ids": r.get("requirement_ids"), "writer": {"model": MODEL, "reviewer": REVIEW_MODEL, "variant": VARIANT,
                                              "prompt_version": r["prompt_version"], "frozen_at": "lm-writer-frozen-2026-09-28", "batch": BATCH}, "cached": bool(r.get("cached"))}))
    name = "tasks_paired.jsonl" if not (limit or ids) else "tasks_paired_sample.jsonl"
    with open(d + "/" + name, "w") as f:
        for t in paired: f.write(json.dumps(t, default=str) + "\n")
    report(d, paired, time.time() - t0, name)
    if name == "tasks_paired.jsonl": deliver(d)
    return paired


DELIVERED = ("id", "database", "snapshot", "snapshot_sha256", "question", "instruction", "reference_sql", "reference_answer", "grader", "tie_groups", "last_pool",
             "A", "S", "construction", "operations", "tables_read", "quantities", "review", "complexity", "provenance", "natural_precise")


def deliver(d):
    """THE DELIVERED CORPUS: <corpus>/corpus.jsonl, one row per task that has a natural question, carrying BOTH renderings:
    `question` (natural precise) and `instruction` (explicit V, deterministic from the SQL, the reference meaning). A task
    without a natural question is not delivered; it is listed with its reason in <corpus>/NOT_RENDERED.json."""
    P = [json.loads(l) for l in open(d + "/tasks_paired.jsonl")]
    ok = [t for t in P if t["natural_precise"]["status"] in RENDERED]
    with open(d + "/corpus.jsonl", "w") as f:
        for t in ok: f.write(json.dumps({k: (t["natural_precise"]["question"] if k == "question" else t.get(k)) for k in DELIVERED}, default=str) + "\n")
    no = [{"id": t["id"], "status": t["natural_precise"]["status"], "outcome": t["natural_precise"].get("outcome"),
           "last_findings": next((h.get("failures") for h in reversed(t["natural_precise"].get("checks", [])) if h.get("failures")), None)} for t in P if t not in ok]
    json.dump(no, open(d + "/NOT_RENDERED.json", "w"), indent=1, default=str)
    return len(ok), len(no)


def report(d, paired, secs, name):
    st = collections.Counter(t["natural_precise"]["status"] for t in paired)
    natural = st["passed"] + st["revised"] + st["deterministic"]
    accounted = natural + st["not rendered"] + st["missing output"]
    fails = collections.Counter(f.get("id") for t in paired for h in t["natural_precise"]["checks"] for f in (h.get("failures") or []))
    tin, tout = sum(u["input"] for u in USAGE), sum(u["output"] for u in USAGE)
    calls = collections.Counter(u["stage"].split(" (")[0] for u in USAGE); retries = sum(1 for u in USAGE if "missing output" in u["stage"])
    L = ["# Precise natural questions for `%s` (%s)\n" % (d.split("/")[-1], name),
         "Writer: frozen lm-writer (sonnet, input language+facts, one revision), ported to specbridge.comm.verbal.precise; batches of %d per database, %d concurrent. "
         "SQL, answers and graders unchanged. Delivered: corpus.jsonl, the rendered tasks with their natural question and explicit instructions.\n" % (BATCH, WORKERS),
         "**Natural coverage: %d of %d tasks** (passed on round 1: %d; revised and accepted: %d; deterministic, no model: %d). "
         "**Not rendered: %d** (the draft failed review twice or a symbol was undefined; the task is not delivered). "
         "**Missing output: %d** (the writer returned no draft even after the retry; not delivered). All %d tasks accounted for: %s.\n" % (
             natural, len(paired), st["passed"], st["revised"], st["deterministic"], st["not rendered"], st["missing output"], accounted, accounted == len(paired)),
         ("Runtime %.0f s; model calls %d (write %d, review %d, revise %d; of these, %d retries after a missing output); tokens in %d, out %d; per natural question written by the model: %.1f calls.\n" % (
             secs, sum(calls.values()), calls["write"], calls["review"], calls["revise"], retries, tin, tout, sum(calls.values()) / max(1, st["passed"] + st["revised"])))
         if USAGE else "Report regenerated from the paired file (no model calls); runtime and calls of the review are in REREVIEW.json.\n",
         "Review: %s.\n" % ("single task per call, re-review of the batched version (2026-10-01)" if any(t["natural_precise"].get("review") == "single-task" for t in paired) else "one task per call"),
         "Review failures by requirement (all rounds, before revision too): %s\n" % (dict(fails.most_common(12)) or "none"),
         "The reviewer's verdict is evidence, not proof. The language resource for a database without one falls back to the catalogue's column labels.\n",
         "## A random sample of paired tasks\n"]
    for t in random.Random(5).sample(paired, min(6, len(paired))):
        np = t["natural_precise"]
        L += ["### %s -- A%s S%s, %s" % (t["id"].split("-")[-1], t.get("A"), t.get("S"), np["status"]), "**Natural (precise):** %s\n" % np["question"],
              "<details><summary>Explicit instructions</summary>\n\n%s\n</details>\n" % t["instruction"].split("\nConventions")[0]]
    open(d + "/NATURAL%s.md" % ("" if name == "tasks_paired.jsonl" else "_SAMPLE"), "w").write("\n".join(L) + "\n"); print("\n".join(L[:7]))


def recheck(d, ids, workers=6):
    """The frozen REVIEWER on accepted natural questions, ONE task per prompt (no other task in sight): a second look at
    fidelity, e.g. on tasks where a solver did worse with the natural question. -> {id: failures}"""
    T = {json.loads(l)["id"]: json.loads(l) for l in open(d + "/tasks_paired.jsonl")}
    from specbridge.pd.realize.catalogue import Catalogue
    its = []
    for i in ids:
        t = T[i]; cat = Catalogue(t["database"]); p = lift(t["reference_sql"], cat.con); s = R.spec(p, cat)
        tk = VZ.task(s, "natural", GM, cat); rec = tk["record"]
        req, extra = language_requirements(s, cat, rec); extra["FACTS"] = facts(s, cat, p)
        its.append({"id": i, "database": t["database"], "sql": t["reference_sql"], "req": req, "extra": extra, "rec": rec, "cat": cat, "draft": t["natural_precise"]["question"]})
    ctxs = {db: meanings(db, [x for x in its if x["database"] == db], next(x["cat"] for x in its if x["database"] == db)) for db in {x["database"] for x in its}}
    def one(it):
        body = "=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n--- %s\nREQUIREMENTS: %s\n%s\nDRAFT: %s" % (it["database"], ctxs[it["database"]], it["id"], json.dumps(it["req"]), json.dumps(it["extra"]), it["draft"])
        txt, _u = llm(REVIEWER % body, "recheck")
        got = {x.get("task"): x.get("failures") for x in parse_list(txt)}
        return it["id"], got.get(it["id"], [{"id": "*", "reason": "the reviewer returned nothing"}])
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(ex.map(one, its))


def rereview(d, workers=6):
    """SINGLE-TASK RE-REVIEW of an already paired corpus: every accepted natural question is reviewed again, alone. A failure
    gets the one revision the frozen budget allows if it has not used it (status passed), then a single-task review; a
    failure after that, or a failing question that was already revised, is not rendered. The previous file is
    kept as tasks_paired.<old prompt version>.jsonl; the result replaces tasks_paired.jsonl. -> summary"""
    import shutil
    from specbridge.pd.realize.catalogue import Catalogue
    t0 = time.time(); USAGE.clear()
    T = [json.loads(l) for l in open(d + "/tasks_paired.jsonl")]
    keep = d + "/tasks_paired.batched-review.jsonl"
    if not os.path.exists(keep): shutil.copyfile(d + "/tasks_paired.jsonl", keep)
    todo = [t for t in T if t["natural_precise"]["status"] in ("passed", "revised")]
    cats = {}
    def item(t):
        cat = cats.setdefault(t["database"], Catalogue(t["database"])); p = lift(t["reference_sql"], cat.con); s = R.spec(p, cat)
        tk = VZ.task(s, "natural", GM, cat); rec = t.get("record") or tk["record"]
        req, extra = language_requirements(s, cat, rec); extra["FACTS"] = facts(s, cat, p)
        return {"id": t["id"], "database": t["database"], "sql": t["reference_sql"], "req": req, "extra": extra, "rec": rec, "cat": cat,
                "explicit": t["instruction"].replace("\n" + R.NOTES, ""), "history": [{"round": "re-review", "draft": t["natural_precise"]["question"]}],
                "was": t["natural_precise"]["status"]}
    its = [item(t) for t in todo]
    spec_of = lambda it: "--- %s\nREQUIREMENTS: %s%s" % (it["id"], json.dumps(it["req"]), ("\n" + json.dumps(it["extra"])) if it["extra"] else "")
    def review1(it):
        ctx = meanings(it["database"], [it], it["cat"])
        txt, _u = llm(REVIEWER % ("=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n%s" % (it["database"], ctx, spec_of(it) + "\nDRAFT: " + it["history"][-1]["draft"])), "re-review")
        f = {x.get("task"): x.get("failures") for x in parse_list(txt)}.get(it["id"])
        f = f if f is not None else [{"id": "*", "reason": "the reviewer returned nothing"}]
        f = list(f) + [dict(x, by="representation check") for x in representation_terms(it["history"][-1]["draft"], it["rec"])]
        it["history"][-1]["failures"] = f
        return it
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(review1, its))
    failed = [it for it in its if it["history"][-1]["failures"]]
    can = [it for it in failed if it["was"] == "passed"]
    by = collections.defaultdict(list)
    for it in can: by[it["database"]].append(it)
    for db, grp in by.items():
        ctx = meanings(db, grp, grp[0]["cat"])
        for i in range(0, len(grp), 3):                      # revision: the writer, a few tasks at a time
            g = grp[i:i + 3]
            body = "\n".join(spec_of(it) + "\nFAILED: %s\nDRAFT: %s\nFINDINGS: %s" % (json.dumps([f.get("id") for f in it["history"][-1]["failures"]]), it["history"][-1]["draft"],
                                                                                    json.dumps(it["history"][-1]["failures"])) for it in g)
            txt, _u = llm(WRITER % ("\nREVISION: fix exactly the findings; every other requirement must stay satisfied.\n", VARIANT_DESC,
                                    "=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n%s" % (db, ctx, body)), "revise")
            rev = {x.get("id"): x.get("question", "") for x in parse_list(txt)}
            for it in g: it["history"].append({"round": "revision after re-review", "draft": rev.get(it["id"], "")})
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(review1, [it for it in can if it["history"][-1]["draft"]]))
    new = {}
    for it in its:
        h = it["history"]; ok = not h[-1].get("failures") and h[-1]["draft"]
        new[it["id"]] = (it["was"] if len(h) == 1 else "revised") if ok else "not rendered", h, h[-1]["draft"] if ok else None
    out = []
    for t in T:
        np_ = dict(t["natural_precise"])
        if t["id"] in new:
            st, h, q = new[t["id"]]
            np_.update(status_before_rereview=np_["status"], status=st, question=q, checks=list(np_.get("checks", [])) + h, review="single-task")
        out.append(dict(t, natural_precise=np_))
    with open(d + "/tasks_paired.jsonl", "w") as f:
        for t in out: f.write(json.dumps(t, default=str) + "\n")
    U = collections.defaultdict(lambda: collections.Counter())
    for u in USAGE: U[u["stage"]].update({"calls": 1, "fresh": u.get("fresh_input", 0), "cached": u.get("cached_input", 0), "out": u["output"]})
    trans = collections.Counter((t["natural_precise"].get("status_before_rereview"), t["natural_precise"]["status"]) for t in out if "status_before_rereview" in t["natural_precise"])
    summ = {"seconds": round(time.time() - t0), "reviewed": len(its), "failed_single_task_review": len(failed), "transitions": {"%s -> %s" % k: v for k, v in trans.items()},
            "status": dict(collections.Counter(t["natural_precise"]["status"] for t in out)), "usage": {k: dict(v) for k, v in U.items()}}
    json.dump(summ, open(d + "/REREVIEW.json", "w"), indent=1); print(json.dumps(summ, indent=1)); deliver(d)
    return summ


if __name__ == "__main__" and "--rereview" in sys.argv:
    rereview(sys.argv[1]); sys.exit(0)

if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k: a[a.index(k) + 1] if k in a else None
    run_corpus(a[0], int(opt("--limit")) if opt("--limit") else None, set(opt("--ids").split(",")) if opt("--ids") else None)
