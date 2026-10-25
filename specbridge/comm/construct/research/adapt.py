"""ADAPTING P_D TO A DATABASE: a fixed, bounded procedure that may change only the database's catalogue facts.
    python -m specbridge.comm.construct.research.adapt <db>       -> out/adapt/<db>/ADAPT.md, adapt.json; accepted revisions in catalogues/corrections/<db>.json
Fixed across databases: the grammar (specbridge.pd.structures.dbgrammar), the pipeline, the veto's rubric, the auditor's rubric, the
adapter's prompt, the budget (BUDGET) and the acceptance rule (accept). Only the catalogue changes, through this procedure.
Gold-free: the adapter sees the schema, the rows, the documentation the database ships, the catalogue, and the reviewers'
reasons on GENERATED tasks. Never a gold SQL query or a question-SQL pair.

  0 catalogue   built once if missing (specbridge.pd.realize.semantic: schema, documentation, data; one model review)
  1 diagnose    a diagnostic sample (seeded, per_cell tasks in every (A, S) cell): pipeline -> single-task veto -> audit of kept
  2 propose     the adapter reads the sample's rejections, the coverage table and the catalogue, and proposes at most
                max_revisions revisions of catalogue facts, each for a problem seen in SEVERAL tasks or a whole missing class,
                each with an evidence query on this database
  3 apply       a revision is applied only if its field and value are in the catalogue's vocabulary and its evidence query
                runs; the result is recorded with it (catalogues/corrections/<db>.json, evidence source "adaptation")
  4 validate    a SEPARATE validation sample (a fresh seed), drawn before and after the revision
  5 accept      keep the revisions only if the validation sample strictly improves (accept); otherwise revert them all
Rounds: at most BUDGET["rounds"]. The next round diagnoses on the latest validation sample and draws a new one to validate."""
import collections, copy, json, math, os, random, shutil, subprocess, sys, time
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json, CALLS
from specbridge.comm.construct.research.filtered import audit

BUDGET = {"rounds": 2, "per_cell": 4, "max_revisions": 8, "evidence_rows": 12}
SEEDS = {"diagnose": 101, "validate": [201, 202, 203]}
ADAPTER = "opus"
FIELDS = {"semantic_role", "scale", "unit", "additive", "population", "quantity", "desc", "direction"}
FLIP_RATE_FILE = "out/recheck/recheck.json"      # remaining disagreement of single-task judging (specbridge.comm.construct.research.recheck)

PROPOSE = """You are adapting a query generator to one database. The generator writes analytical SQL from a CATALOGUE of facts
about each column (role, scale, unit, additivity, population, quantity, description). Reviewers judged a sample of the
generated tasks. Your job: find SYSTEMATIC catalogue errors -- a wrong fact that spoils several tasks, or hides a whole class
of sensible tasks -- and propose corrections of those facts.

Typical errors: a label or code catalogued as a quantity (averaging car numbers); a quantity catalogued as an identifier
(hiding it); a column that groups rows (a category, INCLUDING an ordinal class such as a rating band or a size) not catalogued
as a category, so nothing is grouped by it; a bounded score or index catalogued as ratio scale although ratios of it have no
reading (then scale "interval"; differences stay readable); a running or cumulative total not recognised as such (then its
description and quantity must say so, and additive.time is false); a stored unsigned flow whose direction lives in another
column. Do NOT propose a correction for one task. Do not invent facts: every proposal needs an evidence query on this database
whose result supports it.

Fields you may change and their values:
  semantic_role  identifier | category | ordinal | measure | count | date | duration | indicator | unknown
                 (the generator GROUPS only by category; it computes only with a measure or count whose scale is
                 ratio or interval -- a role change to measure or count needs its scale, unit and additive set too)
  scale          nominal | ordinal | interval | ratio
  unit           a unit word (USD, points, days, count, ...)
  additive       {"entities": true|false|null, "time": true|false|null}   (can the column be summed across entities / over time)
  population     what a count counts
  quantity       what is measured, a few words
  desc           one sentence
  direction      {"by": "<column>", "in": [values], "out": [values]}   (sign of an unsigned flow)

At most %d proposals. Answer ONLY JSON:
[{"column": "table.column", "field": "...", "value": ..., "problem": "which tasks or which missing class this fixes",
  "evidence_sql": "SELECT ... (read-only, on this database)", "claim": "what the evidence shows"}]

COVERAGE (what the generator reaches, per table):
%s

CATALOGUE (columns of the tables above):
%s

EARLIER ROUNDS ON THIS DATABASE (do not propose a correction that was reverted unless you have NEW evidence; do not repeat
an accepted one):
%s

REVIEWED SAMPLE: %d tasks, %d kept by the veto, %d of the kept judged useful by the auditor.
TASKS THE REVIEWERS REJECTED OR FOUND NOT USEFUL (specification, then the reviewers' reasons):
%s

DOCUMENTATION THE DATABASE SHIPS:
%s

SCHEMA:
%s"""


def sample(db, seed, tag):
    """One reviewed sample in a fresh process (so no in-process cache holds an old catalogue): pipeline (single-task veto),
    then the auditor on every kept task. -> records, cost"""
    out = "out/adapt/%s/%s" % (db, tag); t0 = time.time()
    r = subprocess.run([sys.executable, "-m", "specbridge.comm.construct.research.pipeline", db, "--per-cell", str(BUDGET["per_cell"]), "--seed", str(seed), "--out", out],
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-2000:])
    run = json.load(open(out + "/run.json"))
    recs = [json.loads(l) for l in open(out + "/candidates.jsonl")]
    recs = [x for x in recs if "instruction" in x]
    before = sum(CALLS.values())
    A = audit([x for x in recs if (x.get("veto") or {}).get("kept")], cache="out/cache/audit/%s" % db)
    for x in recs: x["audit"] = A.get(x["id"])
    json.dump(recs, open(out + "/reviewed.json", "w"), default=str)
    calls = sum(run.get("model_calls", {}).values()) + sum(CALLS.values()) - before
    return recs, {"seconds": time.time() - t0, "model_calls": calls, "funnel": run["funnel"]}


def metrics(recs):
    kept = [x for x in recs if (x.get("veto") or {}).get("kept")]
    lab = lambda x: (x.get("audit") or {}).get("label")
    useful = [x for x in kept if lab(x) == "useful"]
    return {"reviewed": len(recs), "kept": len(kept), "useful": len(useful),
            "not_meaningful_rate": sum(lab(x) == "not meaningful" for x in kept) / max(1, len(kept)),
            "cells": len({(x["A"], x["S"]) for x in useful}), "deep": sum(x["A"] >= 1 and x["S"] >= 2 for x in useful),
            "diversity": len({(x["slots"]["table"], x["slots"]["quantity"]) for x in useful})}


def margin(n):
    """How many tasks the judges' own disagreement can move in a sample of n reviewed tasks: the expected number of flipped
    decisions plus two standard deviations (binomial, single-task flip rate r measured by specbridge.comm.construct.research.recheck), and never
    less than 2 -- a one-task change is inside the noise of any small sample."""
    r = json.load(open(FLIP_RATE_FILE))["veto"]["flip_rate"] if os.path.exists(FLIP_RATE_FILE) else 0.1
    return max(2, math.ceil(r * n + 2 * math.sqrt(n * r * (1 - r))))


def accept(old, new):
    """STRICT IMPROVEMENT, fixed: nothing worse beyond the judges' noise, and something better beyond it.
      better: useful tasks (+margin), (A, S) cells with a useful task (+1), deep useful tasks A>=1 and S>=2 (+margin)
      not worse: useful, cells, deep, diversity (distinct useful quantities) not down by the margin (cells: by 1), and the
                 share of kept tasks the auditor finds not meaningful not up by more than the flip rate
    A trade-off or a change inside the noise is not an improvement. -> (bool, reasons)"""
    n = max(old["reviewed"], new["reviewed"]); m = margin(n); r = m / max(1, n)
    worse = [k for k in ("useful", "deep", "diversity") if old[k] - new[k] >= m] + (["cells"] if old["cells"] - new["cells"] >= 1 else [])
    if new["not_meaningful_rate"] - old["not_meaningful_rate"] > r: worse.append("not_meaningful_rate")
    better = [k for k in ("useful", "deep") if new[k] - old[k] >= m] + (["cells"] if new["cells"] - old["cells"] >= 1 else [])
    return (not worse and bool(better)), {"margin": m, "better": better, "worse": worse}


def context(db, recs):
    from specbridge.pd.structures.dbfirst import Signature, Q
    from specbridge.pd.structures import dbgrammar as G
    S = Signature(db); C = G.coverage(S)
    cov = "\n".join("%s: %d rows, record table %s, numeric %s, summable %s, quantities %d, groups %d" % (
        r["table"], r["rows"] or 0, r["record"], r["numeric"] or "-", r["summable"] or "-", r["quantities"], r["groups"]) for r in C["tables"])
    if C["composite"]: cov += "\ncomposite foreign keys (not joined): %s" % C["composite"]
    lines = []
    for k, m in S.col.items():
        t, c = k.split(".", 1)
        v = S.run("SELECT COUNT(DISTINCT %s), MIN(%s), MAX(%s) FROM %s" % (Q(c), Q(c), Q(c), Q(t)))
        top = S.run("SELECT %s FROM %s WHERE %s IS NOT NULL GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 5" % (Q(c), Q(t), Q(c)))
        v = v[0] if not isinstance(v, str) and v else ("?", "?", "?")
        lines.append("%s: role=%s scale=%s unit=%s additive=%s population=%s quantity=%s desc=%s | distinct %s, min %s, max %s, common %s" % (
            k, m.get("semantic_role"), m.get("scale"), m.get("unit") or "-", m.get("additive"), m.get("population") or "-", m.get("quantity") or "-",
            (m.get("desc") or "-")[:80], v[0], str(v[1])[:20], str(v[2])[:20], [str(x[0])[:15] for x in top] if not isinstance(top, str) else "?"))
    bad = [x for x in recs if not (x.get("veto") or {}).get("kept") or (x.get("audit") or {}).get("label") != "useful"]
    ex = "\n\n".join("- A%d S%d %s | %s\n  SPEC: %s\n  veto: %s\n  auditor: %s" % (
        x["A"], x["S"], x["construct"], x["slots"]["quantity"], x["instruction"].split("\nConventions")[0][:500],
        " | ".join("%s: %s" % (k, v) for k, v in ((x.get("veto") or {}).get("reasons") or {}).items()), (x.get("audit") or {}).get("reason", "-"))
        for x in random.Random(0).sample(bad, min(30, len(bad))))
    return cov, "\n".join(lines), ex


def history_text(history):
    if not history: return "(none)"
    return "\n".join("round %d, %s: %s" % (h["round"], h["decision"], "; ".join("%s %s = %s" % (x["column"], x["field"], json.dumps(x["value"])) for x in h["revisions"]))
                     for h in history)


def propose(db, recs, history=()):
    cov, cat, ex = context(db, recs)
    M = metrics(recs); schema = DB.schema(recs[0]["snapshot"]) if recs else ""
    p = PROPOSE % (BUDGET["max_revisions"], cov, cat, history_text(history), M["reviewed"], M["kept"], M["useful"], ex or "(none)", DB.docs(db)[:12000], schema[:6000])
    r = ask_json(p, ADAPTER, brace="[", cache="out/cache/adapt/%s" % db) or []
    return [x for x in r if isinstance(x, dict)][:BUDGET["max_revisions"]]


def valid(S, rev):
    """A revision is applicable only with a known field, a value in the catalogue's vocabulary, and an evidence query that runs."""
    from specbridge.pd.realize.semantic import ROLES, SCALES, parse_unit
    k, f, v = rev.get("column"), rev.get("field"), rev.get("value")
    if k not in S.col: return "unknown column"
    if f not in FIELDS: return "field not allowed"
    if f == "semantic_role" and v not in ROLES: return "role outside the vocabulary"
    if f == "scale" and v not in SCALES: return "scale outside the vocabulary"
    if f == "unit" and parse_unit(str(v)) is None: return "unit outside the vocabulary"
    if f == "additive" and not (isinstance(v, dict) and set(v) <= {"entities", "time"}): return "additive must be {entities, time}"
    if f == "direction" and not (isinstance(v, dict) and {"by", "in", "out"} <= set(v)): return "direction must be {by, in, out}"
    sql = str(rev.get("evidence_sql") or "")
    if not sql.lstrip().upper().startswith(("SELECT", "WITH")): return "evidence is not a query"
    r = S.run(sql, cap=BUDGET["evidence_rows"])
    if isinstance(r, str): return "evidence query fails: " + r[6:80]
    rev["evidence_rows"] = [list(map(str, x)) for x in r]
    return None


def apply(db, revs):
    """Write the valid revisions into catalogues/corrections/<db>.json (with their evidence) and rebuild the catalogue from
    its saved proposal (no model call). Returns (applied, refused, backup)."""
    from specbridge.pd.structures.dbfirst import Signature
    from specbridge.pd.realize.semantic import build, corrections_path, path
    S = Signature(db); cf_ = corrections_path(db)
    backup = {"corrections": open(cf_).read() if os.path.exists(cf_) else None, "catalogue": open(path(db)).read()}
    fixes = json.load(open(cf_)) if os.path.exists(cf_) else {}
    applied, refused = [], []
    for rv in revs:
        why = valid(S, rv)
        if why: refused.append(dict(rv, refused=why)); continue
        e = fixes.setdefault(rv["column"], {})
        e[rv["field"]] = rv["value"]
        note = "%s (adaptation, %s): %s Evidence: %s -> %s" % (rv["field"], time.strftime("%Y-%m-%d"), rv.get("claim", ""), rv["evidence_sql"], rv["evidence_rows"][:6])
        e["evidence"] = {"source": "rows", "note": ((e.get("evidence") or {}).get("note", "") + " " + note).strip()}
        applied.append(rv)
    if applied:
        os.makedirs(os.path.dirname(cf_), exist_ok=True); json.dump(fixes, open(cf_, "w"), indent=1)
        build(db, revalidate=True)
    return applied, refused, backup


def revert(db, backup):
    from specbridge.pd.realize.semantic import corrections_path, path
    cf_ = corrections_path(db)
    if backup["corrections"] is None:
        if os.path.exists(cf_): os.remove(cf_)
    else: open(cf_, "w").write(backup["corrections"])
    open(path(db), "w").write(backup["catalogue"])


def adapt(db):
    from specbridge.pd.realize.semantic import build, path
    T0 = time.time(); calls0 = sum(CALLS.values()); log = {"db": db, "budget": BUDGET, "rounds": []}; os.makedirs("out/adapt/%s" % db, exist_ok=True)
    samples_calls = 0
    if not os.path.exists(path(db)): build(db); log["catalogue_built"] = True
    diag, c = sample(db, SEEDS["diagnose"], "r0-diagnose"); samples_calls += c["model_calls"]
    log["diagnose"] = metrics(diag)
    for r in range(1, BUDGET["rounds"] + 1):
        seed = SEEDS["validate"][r - 1]
        old, c = sample(db, seed, "r%d-before" % r); samples_calls += c["model_calls"]
        history = [{"round": R["round"], "decision": R["decision"], "revisions": R["applied"]} for R in log["rounds"]]
        revs = propose(db, diag, history)
        applied, refused, backup = apply(db, revs)
        R = {"round": r, "proposed": revs, "applied": applied, "refused": refused, "before": metrics(old)}
        if not applied: R["decision"] = "nothing to apply"; log["rounds"].append(R); break
        new, c = sample(db, seed, "r%d-after" % r); samples_calls += c["model_calls"]
        R["after"] = metrics(new); ok, why = accept(R["before"], R["after"]); R["accept"] = why
        if ok: R["decision"] = "accepted"; diag = new
        else: R["decision"] = "reverted"; revert(db, backup); diag = old
        log["rounds"].append(R)
        json.dump(log, open("out/adapt/%s/adapt.json" % db, "w"), indent=1, default=str)
    log["seconds"] = time.time() - T0; log["model_calls"] = samples_calls + sum(CALLS.values()) - calls0
    json.dump(log, open("out/adapt/%s/adapt.json" % db, "w"), indent=1, default=str); report(db, log)
    return log


def report(db, log):
    L = ["# Adapting P_D to `%s`\n" % db, "Budget %s. Time %.0fs, model calls %d (sample reviews, audits, adapter).\n" % (log["budget"], log["seconds"], log["model_calls"]),
         "Diagnostic sample: %s\n" % log["diagnose"]]
    for R in log["rounds"]:
        L.append("## Round %d: %s\n" % (R["round"], R["decision"]))
        L.append("| metric | before | after |"); L.append("|---|---|---|")
        for k in ("reviewed", "kept", "useful", "cells", "deep", "diversity", "not_meaningful_rate"):
            L.append("| %s | %s | %s |" % (k, R["before"].get(k), (R.get("after") or {}).get(k, "-")))
        if R.get("accept"): L.append("\nmargin %d; better %s; worse %s\n" % (R["accept"]["margin"], R["accept"]["better"], R["accept"]["worse"]))
        L.append("Applied:")
        L += ["- `%s` %s = %s -- %s" % (x["column"], x["field"], json.dumps(x["value"]), x.get("problem", "")[:200]) for x in R["applied"]]
        if R["refused"]: L.append("Refused:"); L += ["- `%s` %s = %s -- %s" % (x.get("column"), x.get("field"), json.dumps(x.get("value")), x["refused"]) for x in R["refused"]]
        L.append("")
    open("out/adapt/%s/ADAPT.md" % db, "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    for d in sys.argv[1:]: adapt(d)
