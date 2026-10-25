"""GENERATE, THEN FILTER: the frozen grammar (specbridge.pd.structures.dbgrammar v2) proposes candidates, freezing enforces SQL /
specification / grader correctness, the sensibility veto (specbridge.comm.construct.research.veto) filters. Meaningfulness is a property of the
FILTERED corpus, measured here, not a guarantee of the grammar.
    python -m specbridge.comm.construct.research.filtered <db> [<db> ...]      -> out/filtered/<db>/{frozen,kept}.jsonl, EVAL.md
Four measures, per database and per (A, S) cell:
  yield      candidates -> data check -> frozen -> distinct -> kept by the veto
  quality    an INDEPENDENT audit: a third model (fable), not one of the veto's reviewers, with its own rubric, judges a seeded
             blind mix of kept tasks and vetoed controls. The veto's own verdict is never counted as proof.
  diversity  what survives: depth by cell, distinct quantities, tables, constructs; the largest share one quantity takes
  cost       time per stage, model calls, candidates and calls per kept task
Every stage writes its file as it finishes; a rerun reuses them (model calls cached in out/filtered/<db>/cache)."""
import collections, json, os, random, sys, time
from specbridge.comm.construct.freeze import freeze
from specbridge.comm.construct.research.veto import judge, REVIEWERS
from specbridge.comm.common.llm import ask_json
from specbridge.comm.common import db as DB

AUDITOR = "claude-fable-5-1"
AUDIT = """You are auditing a generated text-to-SQL dataset. Each ITEM is a SQL query over the database below with its explicit
specification. For each, decide whether an analyst who works with this database could plausibly want this result, and whether
every calculation in it (each subtraction, division, sum, average and comparison) means something for this data.
  label    useful | acceptable | not meaningful
           useful: a question someone would ask; acceptable: coherent but of little interest; not meaningful: some step has no reading
  reason   one sentence naming the step at fault if not meaningful
Judge each item alone.
%s
Answer ONLY JSON: [{"item": "<id>", "label": "...", "reason": "..."}]

SCHEMA:
%s

DOCUMENTATION:
%s"""


def spec(t): return t["instruction"].split("\nConventions")[0]


def audit(tasks, cache=None, workers=6):
    """The independent auditor on each task ALONE, with the fixed rubric and the database's review context (documentation +
    verified corrections). Cached per task by (auditor, rubric, context, SQL, specification). -> {id: {"label", "reason"}}"""
    import concurrent.futures as cf, hashlib
    ctx = {}
    def one(t):
        db = t["database"]
        if db not in ctx: ctx[db] = DB.context(t)
        schema, docs = ctx[db]
        f = cache and "%s/audit-%s.json" % (cache, hashlib.sha256("\0".join([AUDITOR, AUDIT, schema, docs, t["reference_sql"], spec(t)]).encode()).hexdigest()[:24])
        if f and os.path.exists(f): return t["id"], json.load(open(f))
        body = "--- ITEM %s\nSQL: %s\nSPECIFICATION: %s" % (t["id"], t["reference_sql"], spec(t)[:2500])
        r = [d for d in (ask_json(AUDIT % (body, schema, docs), AUDITOR, brace="[") or []) if isinstance(d, dict)]
        d = r[0] if r else {"label": "no answer"}
        if f and r: os.makedirs(cache, exist_ok=True); json.dump(d, open(f, "w"))
        return t["id"], d
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(ex.map(one, tasks))


QMAX = 60   # EVALUATION ONLY: a table with more row quantities than this is evaluated on a seeded sample of them (reported)


def stage_freeze(db, out, cost):
    from specbridge.pd.structures.dbfirst import Signature
    from specbridge.pd.structures import dbgrammar as G
    ff = out + "/frozen.jsonl"
    if os.path.exists(ff): return [json.loads(l) for l in open(ff)], json.load(open(out + "/cost_freeze.json"))
    S = Signature(db); full = G.quantities; sampled = {}
    def quantities(S_, t):   # the grammar is unchanged; only which of its quantities are enumerated
        qs = full(S_, t)
        if len(qs) <= QMAX: return qs
        sampled[t] = (QMAX, len(qs)); return random.Random(t).sample(qs, QMAX)
    G.quantities = quantities
    try: t0 = time.time(); X = G.instances(S)
    finally: G.quantities = full
    c = {"enumerate_s": time.time() - t0, "candidates": len(X), "sampled_quantities": sampled}
    t0 = time.time(); rows = []
    for x in X:
        ok, why = G.matters(S, x)
        rows.append(dict(x, matters=bool(ok)))
    c["data_check_s"] = time.time() - t0
    t0 = time.time()
    for x in rows:
        if not x["matters"]: continue
        t, why = freeze(x["id"], db, x["sql"], "grammar A%d S%d %s" % (x["A"], x["S"], x["construct"]), why=x["why"], A=x["A"], S=x["S"], construct=x["construct"], slots=x["slots"])
        if t: x["task"] = t
        else: x["refused"] = str(why)[:80]
    c["freeze_s"] = time.time() - t0
    with open(ff, "w") as f:
        for x in rows: f.write(json.dumps(x, default=str) + "\n")
    json.dump(c, open(out + "/cost_freeze.json", "w"))
    return rows, c


def run(db, audit_kept=12, audit_vetoed=6, seed=930):
    out = "out/filtered/%s" % db; os.makedirs(out, exist_ok=True)
    rows, cost = stage_freeze(db, out, {})
    seen, U = set(), []
    for x in rows:
        t = x.get("task")
        if t and t["reference_sql"] not in seen: seen.add(t["reference_sql"]); U.append(x)
    t0 = time.time()
    V = judge([{"id": x["id"], "sql": x["task"]["reference_sql"], "spec": spec(x["task"]), "snapshot": x["task"]["snapshot"], "database": db} for x in U], cache=out + "/cache")
    cost["veto_s"] = time.time() - t0; cost["veto_calls"] = len(REVIEWERS) * -(-len(U) // 6)
    for x in U: x["veto"] = V.get(x["id"], {"kept": False, "labels": {}})
    K = [x for x in U if x["veto"]["kept"]]
    with open(out + "/kept.jsonl", "w") as f:
        for x in K: f.write(json.dumps(x["task"] | {"veto": x["veto"]}, default=str) + "\n")
    # QUALITY: a blind, shuffled mix of kept tasks and vetoed controls, judged by a model the veto never used
    rng = random.Random(seed)
    ks = rng.sample(K, min(audit_kept, len(K))); vs = rng.sample([x for x in U if not x["veto"]["kept"]], min(audit_vetoed, len(U) - len(K)))
    mix = ks + vs; rng.shuffle(mix); t0 = time.time(); A = {}
    if mix:
        schema, docs = DB.context({"database": db, "snapshot": mix[0]["task"]["snapshot"]})
        for i in range(0, len(mix), 6):
            ch = mix[i:i + 6]
            body = "\n\n".join("--- ITEM %s\nSQL: %s\nSPECIFICATION: %s" % (x["id"], x["task"]["reference_sql"], spec(x["task"])[:2500]) for x in ch)
            for d in ask_json(AUDIT % (body, schema, docs), AUDITOR, brace="[", cache=out + "/cache") or []:
                if isinstance(d, dict): A[d.get("item")] = d
    cost["audit_s"] = time.time() - t0; cost["audit_calls"] = -(-len(mix) // 6)
    report(db, out, rows, U, K, ks, vs, A, cost)


def cells(xs): return collections.Counter((x["A"], x["S"]) for x in xs)


def report(db, out, rows, U, K, ks, vs, A, cost):
    fresh = db not in ("financial", "student_club", "formula_1", "college_2")
    L = ["# Generate, then filter: `%s` (%s)\n" % (db, "FRESH: nothing was tuned on it" if fresh else "DEVELOPMENT: rules were informed by it"),
         "Grammar dbgrammar v2 (tag dbgrammar-v2-frozen-2026-09-30); veto = %s, kept only if both say sensible; audit = %s (independent).\n" % (" + ".join(REVIEWERS), AUDITOR),
         "## Yield\n", "| A | S | candidates | data check | frozen | distinct | kept | kept / candidates |", "|---|---|---|---|---|---|---|---|"]
    cc, cm, cf, cu, ck = cells(rows), cells([x for x in rows if x["matters"]]), cells([x for x in rows if x.get("task")]), cells(U), cells(K)
    for c in sorted(cc):
        L.append("| %d | %d | %d | %d | %d | %d | %d | %.0f%% |" % (c + (cc[c], cm[c], cf[c], cu[c], ck[c], 100.0 * ck[c] / cc[c])))
    L.append("| all | | %d | %d | %d | %d | %d | %.0f%% |" % (len(rows), sum(cm.values()), sum(cf.values()), len(U), len(K), 100.0 * len(K) / max(1, len(rows))))
    if cost.get("sampled_quantities"):
        L.append("\nSAMPLED: " + "; ".join("%s: %d of %d row quantities (seeded); yield counts are for the sample" % (t, a, b) for t, (a, b) in cost["sampled_quantities"].items()))
    ref = collections.Counter(x["refused"] for x in rows if x.get("refused"))
    if ref: L.append("\nFreeze refusals: %s" % dict(ref))
    L.append("\nVeto labels (opus/sonnet) on distinct frozen: %s" % dict(collections.Counter("%s/%s" % (x["veto"]["labels"].get("opus"), x["veto"]["labels"].get("sonnet")) for x in U)))
    # QUALITY
    lab = lambda xs: collections.Counter((A.get(x["id"]) or {}).get("label", "no answer") for x in xs)
    good = lambda c: c["useful"] + c["acceptable"]
    L += ["\n## Quality (independent audit, blind mix)\n", "| set | n | useful | acceptable | not meaningful | no answer |", "|---|---|---|---|---|---|"]
    for name, xs in (("kept by the veto", ks), ("vetoed (controls)", vs)):
        c = lab(xs); L.append("| %s | %d | %d | %d | %d | %d |" % (name, len(xs), c["useful"], c["acceptable"], c["not meaningful"], c["no answer"]))
    L.append("\nKept tasks the auditor finds meaningful (useful or acceptable): %d/%d. Vetoed controls it finds meaningful: %d/%d." % (good(lab(ks)), len(ks), good(lab(vs)), len(vs)))
    # DIVERSITY
    q = collections.Counter((x["slots"]["table"], x["slots"]["quantity"]) for x in K)
    L += ["\n## Diversity of what survives\n",
          "- kept: %d; by arithmetic depth %s; by step depth %s" % (len(K), dict(sorted(collections.Counter(x["A"] for x in K).items())), dict(sorted(collections.Counter(x["S"] for x in K).items()))),
          "- with arithmetic (A >= 1): %d; with two or more steps (S >= 2): %d; both: %d" % (sum(x["A"] >= 1 for x in K), sum(x["S"] >= 2 for x in K), sum(x["A"] >= 1 and x["S"] >= 2 for x in K)),
          "- distinct quantities %d, tables %d, constructs %d, (quantity, construct) pairs %d" % (len(q), len({x["slots"]["table"] for x in K}), len({x["construct"] for x in K}), len({(x["slots"]["quantity"], x["construct"]) for x in K})),
          "- largest share one quantity takes: %s" % ("%d/%d (%s)" % (q.most_common(1)[0][1], len(K), q.most_common(1)[0][0][1]) if q else "-"),
          "- surviving quantities: " + "; ".join("%s.%s x%d" % (t, n, k) for (t, n), k in q.most_common())]
    # COST
    calls = cost["veto_calls"] + cost["audit_calls"]
    L += ["\n## Cost\n", "| stage | seconds |", "|---|---|"] + ["| %s | %.0f |" % (k[:-2], cost[k]) for k in ("enumerate_s", "data_check_s", "freeze_s", "veto_s", "audit_s")]
    L.append("\nModel calls: veto %d, audit %d. Per kept task: %.1f candidates, %.2f veto calls, %.0f seconds of generation and filtering (audit excluded)."
             % (cost["veto_calls"], cost["audit_calls"], len(rows) / max(1, len(K)), cost["veto_calls"] / max(1, len(K)),
                sum(cost[k] for k in ("enumerate_s", "data_check_s", "freeze_s", "veto_s")) / max(1, len(K))))
    L.append("\n## A random sample of kept tasks, with the audit\n")
    for x in random.Random(7).sample(K, min(8, len(K))):
        a = A.get(x["id"]) or {}
        L += ["- **%s** A%d S%d %s -- audit: %s" % (x["id"], x["A"], x["S"], x["construct"], a.get("label", "not audited")),
              "  - %s" % spec(x["task"])[:600], "  - `%s`" % x["task"]["reference_sql"][:300]] + (["  - auditor: %s" % a["reason"]] if a else [])
    L.append("\n## Audited kept tasks the auditor finds not meaningful\n")
    for x in ks:
        a = A.get(x["id"]) or {}
        if a.get("label") == "not meaningful": L += ["- **%s** A%d S%d %s: %s" % (x["id"], x["A"], x["S"], x["construct"], spec(x["task"])[:500]), "  - auditor: %s" % a.get("reason")]
    json.dump({"db": db, "candidates": len(rows), "frozen": sum(cf.values()), "distinct": len(U), "kept": len(K), "cells": {"%d,%d" % c: [cc[c], ck[c]] for c in cc},
               "audit_kept": dict(lab(ks)), "audit_vetoed": dict(lab(vs)), "cost": cost, "fresh": fresh}, open(out + "/summary.json", "w"))
    open(out + "/EVAL.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:60]))




def by_depth(dbs, per_cell=8, seed=931, root="out/filtered"):
    """EXPANDED AUDIT where the spot check is too small: per (database, A, S) cell, up to `per_cell` kept tasks in total
    (the spot check's plus a fresh seeded sample), judged by the same independent auditor in batches SHUFFLED across cells and
    databases' cells (similar items are not judged side by side). -> out/filtered/AUDIT_BY_DEPTH.md, audit_by_depth.json"""
    import concurrent.futures as cf
    rng = random.Random(seed); jobs = []; done = {}
    for db in dbs:
        out = "%s/%s" % (root, db)
        K = [json.loads(l) for l in open(out + "/kept.jsonl")]
        prev = {}
        for f in (os.listdir(out + "/cache") if os.path.isdir(out + "/cache") else []):
            j = json.load(open(out + "/cache/" + f))
            if j.get("model") == AUDITOR: prev.update({d.get("item"): d for d in j["reply"] if isinstance(d, dict)})
        by = collections.defaultdict(list)
        for t in K: by[(t["A"], t["S"])].append(t)
        pick = []
        for c, ts in by.items():
            have = [t for t in ts if t["id"] in prev]; rest = [t for t in ts if t["id"] not in prev]; rng.shuffle(rest)
            for t in have: done[t["id"]] = (db, c, t, prev[t["id"]])
            pick += rest[:max(0, per_cell - len(have))]
        rng.shuffle(pick)
        schema, docs = DB.context({"database": db, "snapshot": K[0]["snapshot"]}) if K else ("", "")
        for i in range(0, len(pick), 6): jobs.append((db, out, pick[i:i + 6], schema, docs))
    def one(j):
        db, out, ch, schema, docs = j
        body = "\n\n".join("--- ITEM %s\nSQL: %s\nSPECIFICATION: %s" % (t["id"], t["reference_sql"], spec(t)[:2500]) for t in ch)
        r = {d.get("item"): d for d in (ask_json(AUDIT % (body, schema, docs), AUDITOR, brace="[", cache=out + "/cache") or []) if isinstance(d, dict)}
        return [(db, (t["A"], t["S"]), t, r.get(t["id"]) or {"label": "no answer"}) for t in ch]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(one, jobs):
            for db, c, t, d in res: done[t["id"]] = (db, c, t, d)
    rows = collections.defaultdict(collections.Counter)
    for db, c, t, d in done.values(): rows[(db, c)][d.get("label")] += 1
    L = ["# Independent audit by depth (auditor %s, kept tasks only)\n" % AUDITOR,
         "Up to %d kept tasks per cell (spot check + fresh sample). meaningful = useful + acceptable. The auditor is a separate judgment, not ground truth.\n" % per_cell,
         "| database | A | S | kept in cell | audited | useful | acceptable | not meaningful | meaningful |", "|---|---|---|---|---|---|---|---|---|"]
    kept = {db: collections.Counter((json.loads(l)["A"], json.loads(l)["S"]) for l in open("%s/%s/kept.jsonl" % (root, db))) for db in dbs}
    for (db, c) in sorted(rows):
        r = rows[(db, c)]; n = sum(r.values())
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d/%d |" % (db, c[0], c[1], kept[db][c], n, r["useful"], r["acceptable"], r["not meaningful"], r["useful"] + r["acceptable"], n))
    for name, f in (("A", lambda c: c[0]), ("S", lambda c: c[1])):
        agg = collections.defaultdict(collections.Counter)
        for (db, c), r in rows.items(): agg[f(c)].update(r)
        L.append("\nBy %s (all databases): " % name + "; ".join("%s%d %d/%d" % (name, k, v["useful"] + v["acceptable"], sum(v.values())) for k, v in sorted(agg.items())))
    L.append("\n## Every kept task the auditor finds not meaningful\n")
    for db, c, t, d in sorted(done.values(), key=lambda z: (z[0], z[1])):
        if d.get("label") == "not meaningful":
            L.append("- **%s** A%d S%d %s | %s -- %s" % (t["id"], c[0], c[1], t["construct"], t["slots"].get("quantity"), d.get("reason")))
    json.dump({k: [db, list(c), d] for k, (db, c, t, d) in done.items()}, open(root + "/audit_by_depth.json", "w"))
    open(root + "/AUDIT_BY_DEPTH.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))




def use(x):
    """How a task uses a quantity across snapshots (for reading a disputed column's tasks)."""
    s = x["slots"]
    if x["S"] == 0: return "rank individual rows"
    if x["S"] == 1: return "average over all rows in a group"
    return "per %s, then across %s" % (s.get("entity"), "races" if s.get("entity") == "races" else "entities")


def reassess(db, tables):
    """A DISPUTED COLUMN'S TASKS AGAIN, after a catalogue correction: every frozen task on `tables` is re-frozen (same SQL,
    the corrected names in its specification) and judged again by the veto and the auditor, whose documentation now carries
    the correction's evidence (specbridge.comm.common.db.verified). Old and new verdicts side by side. -> out/filtered/<db>/REASSESS.md"""
    out = "out/filtered/%s" % db
    rows = [json.loads(l) for l in open(out + "/frozen.jsonl")]
    K = {json.loads(l)["id"] for l in open(out + "/kept.jsonl")}
    prevA = {}
    for f in os.listdir(out + "/cache"):
        j = json.load(open(out + "/cache/" + f))
        if j.get("model") == AUDITOR: prevA.update({d.get("item"): d for d in j["reply"] if isinstance(d, dict)})
    xs = [x for x in rows if x.get("task") and x["slots"]["table"] in tables]
    T = []
    for x in xs:
        t, why = freeze(x["id"], db, x["sql"], "grammar A%d S%d %s" % (x["A"], x["S"], x["construct"]), why=x["why"], A=x["A"], S=x["S"], construct=x["construct"], slots=x["slots"])
        if t: T.append((x, t))
    V = judge([{"id": t["id"], "sql": t["reference_sql"], "spec": spec(t), "snapshot": t["snapshot"], "database": db} for x, t in T], cache=out + "/cache_reassess")
    A = {}; schema, docs = DB.context({"database": db, "snapshot": T[0][1]["snapshot"]})
    order = list(T); random.Random(932).shuffle(order)
    for i in range(0, len(order), 6):
        ch = order[i:i + 6]
        body = "\n\n".join("--- ITEM %s\nSQL: %s\nSPECIFICATION: %s" % (t["id"], t["reference_sql"], spec(t)[:2500]) for x, t in ch)
        for d in ask_json(AUDIT % (body, schema, docs), AUDITOR, brace="[", cache=out + "/cache_reassess") or []:
            if isinstance(d, dict): A[d.get("item")] = d
    tab = collections.defaultdict(collections.Counter)
    L = ["# Reassessing the tasks on %s after the catalogue correction\n" % ", ".join(tables),
         "%d frozen tasks (%d kept before). Same SQL; specifications re-rendered with the corrected names; veto and auditor see the correction's evidence.\n" % (len(T), sum(x["id"] in K for x, t in T)),
         "| use | tasks | veto kept before | veto kept now | auditor meaningful now | auditor meaningful now, among veto-kept |", "|---|---|---|---|---|---|"]
    for x, t in T:
        u = use(x); a = (A.get(t["id"]) or {}).get("label"); k = V.get(t["id"], {}).get("kept")
        tab[u].update({"n": 1, "before": x["id"] in K, "now": bool(k), "aud": a in ("useful", "acceptable"), "both": bool(k) and a in ("useful", "acceptable")})
    for u, c in sorted(tab.items()):
        L.append("| %s | %d | %d | %d | %d | %d/%d |" % (u, c["n"], c["before"], c["now"], c["aud"], c["both"], c["now"]))
    c = sum(tab.values(), collections.Counter())
    L.append("| all | %d | %d | %d | %d | %d/%d |" % (c["n"], c["before"], c["now"], c["aud"], c["both"], c["now"]))
    L.append("\n## Every task, old and new verdicts\n")
    for x, t in sorted(T, key=lambda z: (use(z[0]), z[0]["id"])):
        v = V.get(t["id"], {}); a = A.get(t["id"]) or {}
        L += ["- **%s** A%d S%d %s [%s] %s -- veto before %s, now %s %s; auditor before %s, now %s" % (
            t["id"], x["A"], x["S"], x["construct"], use(x), x["slots"]["quantity"], "kept" if x["id"] in K else "vetoed", "kept" if v.get("kept") else "vetoed",
            v.get("labels"), (prevA.get(t["id"]) or {}).get("label", "-"), a.get("label")),
              "  - opus: %s | sonnet: %s | auditor: %s" % ((v.get("reasons") or {}).get("opus"), (v.get("reasons") or {}).get("sonnet"), a.get("reason"))]
    json.dump({t["id"]: {"use": use(x), "before": x["id"] in K, "veto": V.get(t["id"]), "audit": A.get(t["id"]), "task": t} for x, t in T}, open(out + "/reassess.json", "w"), default=str)
    open(out + "/REASSESS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:12 + len(tab)]))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--by-depth"]:
        a = sys.argv[2:]; root = a[a.index("--root") + 1] if "--root" in a else "out/filtered"
        by_depth([d for d in a if d != "--root" and d != root], root=root)
    elif sys.argv[1:2] == ["--reassess"]: reassess(sys.argv[2], sys.argv[3:])
    else:
        for d in sys.argv[1:]: run(d)
