"""THE TASK-QUALITY RUBRIC (v1, pilot): three separate questions, each answered on its own.
    python -m specbridge.comm.construct.rubric pilot        -> out/rubric/v1/PILOT.md, pilot.json
  meaning     does every computed quantity have a coherent reading?          yes | no | uncertain (+ the element at fault)
  determined  do the instructions determine a single answer?                  yes | no (+ what is left open)
  interest    would an analyst of this database plausibly want the result?    useful | acceptable | not useful
Meaning is judged apart from interest and from complexity: an uninteresting, unusual or redundantly computed task can
still be coherent. A difference or ratio of two quantities needs their DEFINITIONS to make them comparable -- sharing a
numeric scale is not enough. Weightings the instructions state (a mean of group means) are coherent.
Each task is judged alone by each reviewer (opus, sonnet), with the database's schema, documentation and verified
corrections. The pilot checks whether reviewers keep the three questions apart: agreement between reviewers, agreement
with the reference verdicts on the nine agreed examples, and interest or complexity leaking into meaning."""
import collections, concurrent.futures as cf, hashlib, json, os, random, re, sys
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json

VERSION = "rubric-v1.1"
REVIEWERS = ("opus", "sonnet")
RUBRIC = """You review ONE generated task for a text-to-SQL benchmark: its SQL and the instructions a solver receives.
Answer three SEPARATE questions. Do not let one answer influence another.

1. meaning -- does every quantity the task computes have a coherent reading on this database?  yes | no | uncertain
   - Judge meaning ONLY. A task can be coherent and still uninteresting, unusual, long-winded or computed redundantly;
     none of that affects this answer.
   - A weighting the instructions state (e.g. an average of group averages, so each group counts equally) is coherent.
   - A population the instructions state is coherent: if the instructions say which rows are left out (e.g. transactions
     whose direction is undocumented), the result is a coherent figure over the rows kept. Report it under "partial".
   - A difference or ratio of two quantities is coherent only if their DEFINITIONS make them comparable (the same kind of
     thing, e.g. two money amounts of the same kind). Being on the same numeric scale is not enough: two different ratings
     are comparable only if their definitions say so. If the documentation does not settle it, answer uncertain.
   - For no or uncertain, name the element at fault.
2. determined -- do the instructions determine a single answer?  yes | no
   Ties at a cut-off are handled by the grader and are not a defect. For no, name what is left open.
3. interest -- would an analyst of this database plausibly want this result?  useful | acceptable | not useful
   (acceptable = coherent but of little interest). This is a separate question from meaning.
Also: partial -- do the instructions deliberately leave out a stated part of the rows (yes | no)?

Answer ONLY JSON: {"meaning": "...", "meaning_reason": "one sentence", "determined": "...", "determined_reason": "one sentence",
"interest": "...", "interest_reason": "one sentence", "partial": "yes|no"}

TASK
SQL: %s
INSTRUCTIONS: %s

SCHEMA:
%s

DOCUMENTATION:
%s"""

REFERENCE = {"U1": "yes", "U2": "yes", "U3": "yes", "A1": "yes", "A2": "uncertain", "A3": "yes", "R1": "yes", "R2": "no", "R3": "uncertain"}
LEAK = re.compile(r"\b(interest|interesting|useful|contrived|analyst|trivial|redundant|pointless|little value|no analytic|odd)\b", re.I)


def judge(tasks, cache="out/cache/rubric", workers=6):
    """{id: {reviewer: answer}} -- each task alone, each reviewer separately, cached per (reviewer, rubric, context, task)."""
    ctx = {}
    def one(job):
        t, m = job; db = t["db"]
        if db not in ctx: ctx[db] = DB.context({"database": db, "snapshot": t["snapshot"]})
        schema, docs = ctx[db]
        p = RUBRIC % (t["sql"], t["spec"], schema, docs)      # never truncated: the Conventions paragraph is at the end
        f = "%s/%s.json" % (cache, hashlib.sha256((m + "\0" + p).encode()).hexdigest()[:24])
        if os.path.exists(f): return t["id"], m, json.load(open(f))
        r = ask_json(p, m) or {}
        if r: os.makedirs(cache, exist_ok=True); json.dump(r, open(f, "w"))
        return t["id"], m, r
    out = collections.defaultdict(dict)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, m, r in ex.map(one, [(t, m) for t in tasks for m in REVIEWERS]): out[i][m] = r
    return dict(out)


def sample(per_db=4, seed=21):
    """The nine agreed examples plus per_db more per database, spread over depth bands and the old tiers."""
    R = [x for x in json.load(open("out/depth_eval/compose-v3.1/results.json"))["rows"] if x.get("stage") == "reviewed"]
    snap = {x["db"]: None for x in R}
    nine = json.load(open("out/depth_eval/compose-v3.1/standard_examples.json"))
    ids = ["U1", "U2", "U3", "A1", "A2", "A3", "R1", "R2", "R3"]
    chosen = {x["id"] for x in nine}
    tier = lambda x: "rejected" if not x["kept"] or x["audit"] == "not meaningful" else ("useful" if x["audit"] == "useful" else "acceptable")
    rng = random.Random(seed); extra = []
    for db in sorted({x["db"] for x in R}):
        xs = [x for x in R if x["db"] == db and x["id"] not in chosen]; rng.shuffle(xs)
        bands = [lambda x: x["A"] + x["S"] <= 3, lambda x: 4 <= x["A"] + x["S"] <= 5, lambda x: 6 <= x["A"] + x["S"] <= 7, lambda x: x["A"] + x["S"] >= 8]
        for b, t in zip(bands, ["useful", "acceptable", "rejected", "acceptable"]):
            pick = next((x for x in xs if b(x) and tier(x) == t and x not in extra), None) or next((x for x in xs if b(x) and x not in extra), None)
            if pick: extra.append(pick)
    from specbridge.comm.construct.freeze import snapshot
    tasks = [dict(x, ref=REFERENCE[i], label=i, old=x["tier"]) for i, x in zip(ids, nine)] + [dict(x, ref=None, label="S%d" % k, old=tier(x)) for k, x in enumerate(extra)]
    for t in tasks: t["snapshot"] = snapshot(t["db"])[0]
    return tasks


def combine(a):
    """The rubric's verdict from the two reviewers: meaning yes only if BOTH say yes; any uncertain -> uncertain; a no needs
    a named element (a bare no counts as uncertain); determined yes only if both say yes. Interest is kept per reviewer."""
    ms = [(a.get(m) or {}).get("meaning") for m in REVIEWERS]
    if any(x is None for x in ms): meaning = "unreviewed"
    elif all(x == "yes" for x in ms): meaning = "yes"
    elif any(x == "no" and ((a.get(m) or {}).get("meaning_reason") or "").strip() for m, x in zip(REVIEWERS, ms)) and "uncertain" not in ms: meaning = "no"
    else: meaning = "uncertain"
    det = "yes" if all((a.get(m) or {}).get("determined") == "yes" for m in REVIEWERS) else "no"
    return {"rubric": VERSION, "meaning": meaning, "determined": det, "agree": len(set(ms)) == 1,
            "partial": any((a.get(m) or {}).get("partial") == "yes" for m in REVIEWERS),
            "interest": {m: (a.get(m) or {}).get("interest") for m in REVIEWERS},
            "reasons": {m: {k: (a.get(m) or {}).get(k) for k in ("meaning_reason", "determined_reason", "interest_reason")} for m in REVIEWERS}}


def assess_pools(dbs):
    """Rubric v1.1 on every task the pools currently serve (current grammar and catalogue); written into the pool entries."""
    from specbridge.comm.construct import pool as PL
    from specbridge.comm.construct.freeze import snapshot, packaged
    from specbridge.pd.structures.compose import VERSION as GV
    tot = collections.Counter()
    for db in dbs:
        P = PL.load(db); cv = PL.cat_version(db)
        live = [e for e in P if e["grammar"] == GV and e["catalogue"] == cv]
        tasks = []
        for e in live:
            full, _w = packaged(e["id"], db, e["sql"], "pool", level="spec")      # the FULL instructions, Conventions included
            tasks.append({"id": e["id"], "db": db, "sql": e["sql"], "spec": full["instruction"] if full else e["spec"], "snapshot": snapshot(db)[0]})
        J = judge(tasks)
        for e in live:
            e["quality"] = combine(J.get(e["id"], {})); tot[(db, e["quality"]["meaning"])] += 1
        PL.save(db, P, {"source": "assess " + VERSION, "assessed": len(live)}); PL.profile(db)
        print(db, {k[1]: v for k, v in tot.items() if k[0] == db}, flush=True)
    return tot


def pilot():
    T = sample(); J = judge(T); os.makedirs("out/rubric/v1", exist_ok=True)
    rows = []
    for t in T:
        a = J.get(t["id"], {})
        rows.append({"label": t["label"], "db": t["db"], "A": t["A"], "S": t["S"], "old": t["old"], "ref": t["ref"],
                     **{"%s_%s" % (m, k): (a.get(m) or {}).get(k) for m in REVIEWERS for k in ("meaning", "meaning_reason", "determined", "determined_reason", "interest", "interest_reason")}})
    json.dump({"rubric": VERSION, "rows": rows}, open("out/rubric/v1/pilot.json", "w"), indent=1)
    n = len(rows); m = lambda r, x: r["%s_meaning" % x]
    agree = sum(m(r, "opus") == m(r, "sonnet") for r in rows)
    ref = [r for r in rows if r["ref"]]
    leak = [(r, x) for r in rows for x in REVIEWERS if m(r, x) in ("no", "uncertain") and LEAK.search(r["%s_meaning_reason" % x] or "")]
    sep = sum(1 for r in rows for x in REVIEWERS if m(r, x) == "yes" and r["%s_interest" % x] in ("acceptable", "not useful"))
    L = ["# Rubric %s pilot: do reviewers keep meaning, determinacy and interest apart?\n" % VERSION,
         "%d tasks: the nine agreed examples plus %d across six databases and depth bands (compose-v3.1 reviews; development evidence). "
         "Each task judged alone by opus and by sonnet.\n" % (n, n - 9),
         "- meaning, opus vs sonnet agree: **%d/%d**" % (agree, n),
         "- meaning vs the reference on the nine: opus %d/9, sonnet %d/9" % (sum(m(r, "opus") == r["ref"] for r in ref), sum(m(r, "sonnet") == r["ref"] for r in ref)),
         "- coherent but not useful (meaning yes, interest acceptable or not useful): %d of %d judgments -- the questions are kept apart this often" % (sep, 2 * n),
         "- possible leakage (meaning no/uncertain with an interest or redundancy word in the reason): %d of %d judgments" % (len(leak), 2 * n),
         "- determined = no: %d judgments" % sum(1 for r in rows for x in REVIEWERS if r["%s_determined" % x] == "no"),
         "\n| task | db | A,S | old tier | reference | opus meaning / interest | sonnet meaning / interest |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %s | %s | %d,%d | %s | %s | %s / %s | %s / %s |" % (r["label"], r["db"], r["A"], r["S"], r["old"], r["ref"] or "-",
                 r["opus_meaning"], r["opus_interest"], r["sonnet_meaning"], r["sonnet_interest"]))
    L.append("\n## Every meaning judgment that is not yes, with its reason\n")
    for r in rows:
        for x in REVIEWERS:
            if m(r, x) != "yes":
                L.append("- **%s** (%s, A%d S%d) %s: %s -- %s%s" % (r["label"], r["db"], r["A"], r["S"], x, m(r, x), r["%s_meaning_reason" % x],
                                                                 "  **[possible leakage]**" if (r, x) in leak else ""))
    L.append("\n## Disagreements between the reviewers on meaning\n")
    for r in rows:
        if m(r, "opus") != m(r, "sonnet"):
            L.append("- **%s** (%s): opus %s -- %s | sonnet %s -- %s" % (r["label"], r["db"], m(r, "opus"), r["opus_meaning_reason"], m(r, "sonnet"), r["sonnet_meaning_reason"]))
    open("out/rubric/v1/PILOT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["pilot"]: pilot()
    elif sys.argv[1:2] == ["assess"]: assess_pools(sys.argv[2:] or ["student_club", "financial", "formula_1", "sakila_1", "soccer_1", "college_2"])
