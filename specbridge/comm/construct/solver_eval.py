"""SOLVER EVALUATION OF A DELIVERED CORPUS: each task's natural question (and, with --explicit, its explicit instructions), one
solver, the task's own grader.
    python -m specbridge.comm.construct.solver_eval <corpus dir> [--model haiku] [--bsize 8] [--rounds 6] [--explicit] [--workers 6]   (workers = concurrent model calls; the work is network-bound)
        -> out/solver/<corpus>/<model>/<key>.json (one per answer, resumable), <corpus>/SOLVER_<model>.md, solver_<model>.json
  input      <corpus>/corpus.jsonl: the delivered tasks (specbridge.comm.verbal.precise.deliver), each with its natural question
  --explicit also solve each task's explicit instructions (V, delivered beside the question); the report then pairs the arms
  solver     specbridge.comm.common.solve: batched agent, one database per call, up to `rounds` rounds of up to 5 exploration queries,
             then FINAL; batches are per arm
  cache      one file per answer; a natural answer's key carries a hash of the question's text, so a rewritten question is
             solved afresh and an unchanged one reuses its answer
  grading    the task's own grader (specbridge.comm.common.grade.spec: positional columns, rounding tolerance, tie groups at a cut)
  report     accuracy; by step depth, arithmetic depth, shape and writer status; a random sample of wrong answers"""
import hashlib, json, random, sys, time
from specbridge.comm.common.solve import solve
from specbridge.comm.common.grade import spec


def run(d, model="haiku", bsize=8, rounds=6, explicit=False, workers=6):
    T = [json.loads(l) for l in open(d + "/corpus.jsonl")]; name = d.rstrip("/").split("/")[-1]
    out = "out/solver/%s/%s" % (name, model); t0 = time.time()
    items = []
    for t in T:
        q = t["question"]
        items.append(dict(database=t["database"], snapshot=t["snapshot"], task=t["id"], key="%s|natural|%s" % (t["id"], hashlib.sha1(q.encode()).hexdigest()[:8]),
                          arm="natural", text=q, res="%s|natural" % t["id"]))
    if explicit:
        V = {x["id"]: x["instruction"] for x in map(json.loads, open(d + "/tasks.jsonl"))}
        items += [dict(database=t["database"], snapshot=t["snapshot"], task=t["id"], key="%s|explicit" % t["id"], arm="explicit", text=V[t["id"]]) for t in T]
    R = solve(items, model, out, bsize=bsize, rounds=rounds, group=lambda it: it["arm"], workers=workers)
    serial_rerun(R, {t["id"]: t for t in T}, out)
    by = {t["id"]: t for t in T}; res = {}
    missing = [it["key"] for it in items if it["key"] not in R]
    if missing: print("NOT SCORED: %d questions have no saved answer (failed calls); rerun to complete them" % len(missing), flush=True)
    for it in items:
        r = R.get(it["key"]); t = by[it["task"]]
        if r is None: continue                       # not attempted is not wrong (2026-10-03)
        ok = bool(r and r.get("executes") and spec(t["grader"], t["reference_answer"], r.get("answer"), t.get("tie_groups"), t.get("last_pool")))
        res[it.get("res", it["key"])] = {"correct": ok, "answered": bool(r and r.get("final")), "executes": bool(r and r.get("executes")), "turns": (r or {}).get("turns")}
    report(d, name, model, T, res, time.time() - t0)


def serial_rerun(R, by, out):
    """A FINAL QUERY THAT DID NOT EXECUTE IS RUN AGAIN ALONE, under the same time limit, before grading (2026-10-03). With
    four solvers x 16 workers querying at once, correct queries hit the 60 s limit: 9 of gpt-6-luna's natural answers on
    eval12 ran alone and were right. The limit is a property of the query, not of the load at the moment. Recorded on the
    answer as "serial_rerun"."""
    import os, re
    from specbridge.comm.common import db as DB
    for k, r in R.items():
        if not r.get("final") or r.get("executes") or r.get("serial_rerun"): continue
        t = by[k.split("|")[0]]; a = DB.rows(DB.connect(t["snapshot"]), r["final"])
        r["serial_rerun"] = "executes" if a is not None else "still fails"
        if a is not None: r.update(executes=True, answer=a, rows_answer=len(a))
        json.dump(r, open("%s/%s.json" % (out, re.sub(r"[^\w.-]", "_", k)), "w"), default=str)


def report(d, name, model, T, res, secs):
    arms = [a for a in ("natural", "explicit") if any(k.endswith("|" + a) for k in res)]
    keys = lambda ts, a: ["%s|%s" % (t["id"], a) for t in ts if "%s|%s" % (t["id"], a) in res]
    pct = lambda ks: "%d/%d (%.0f%%)" % (sum(res[k]["correct"] for k in ks), len(ks), 100.0 * sum(res[k]["correct"] for k in ks) / max(1, len(ks)))
    shape = lambda t: " > ".join(p.split(":")[0] for p in t["construction"].split(" > "))
    L = ["# Solver evaluation: `%s`, solver %s\n" % (name, model),
         "The delivered corpus (%d tasks). One solver (batched agent, up to 6 rounds of exploration "
         "queries, then a final query), the task's own grader (tolerance, tie groups). %.0f s.\n" % (len(T), secs),
         "| arm | tasks | correct | answered | executes |", "|---|---|---|---|---|"]
    for a in arms:
        ks = keys(T, a)
        L.append("| %s | %d | %s | %d | %d |" % ("natural question" if a == "natural" else "explicit instructions", len(ks), pct(ks),
                                               sum(res[k]["answered"] for k in ks), sum(res[k]["executes"] for k in ks)))
    if len(arms) == 2:
        import collections
        pc = collections.Counter((res["%s|explicit" % t["id"]]["correct"], res["%s|natural" % t["id"]]["correct"]) for t in T)
        L += ["\n## Paired, same %d tasks\n" % len(T), "| | natural right | natural wrong |", "|---|---|---|",
              "| explicit right | %d | %d |" % (pc[(True, True)], pc[(True, False)]), "| explicit wrong | %d | %d |" % (pc[(False, True)], pc[(False, False)])]
    for title, key in (("step depth", lambda t: "S%d" % t["S"]), ("arithmetic depth", lambda t: "A%d" % t["A"]), ("shape", shape), ("writer status", lambda t: t["natural_precise"]["status"])):
        L += ["\n## By %s\n" % title, "| %s | tasks | %s |" % (title, " | ".join(arms)), "|---|---|%s" % ("---|" * len(arms))]
        for k in sorted({key(t) for t in T}):
            ts = [t for t in T if key(t) == k]
            L.append("| %s | %d | %s |" % (k, len(ts), " | ".join(pct(keys(ts, a)) for a in arms)))
    L.append("\n## Wrong answers to read (a random 6)\n")
    bad = [t for t in T if not res.get("%s|natural" % t["id"], {}).get("correct", True)]
    for t in random.Random(3).sample(bad, min(6, len(bad))):
        L += ["- **%s** A%d S%d `%s`" % (t["id"].split("-")[-1], t["A"], t["S"], shape(t)), "  - %s" % t["question"][:700].replace("\n", " ")]
    json.dump({"model": model, "results": res, "seconds": round(secs)}, open("%s/solver_%s.json" % (d, model), "w"))
    open("%s/SOLVER_%s.md" % (d, model), "w").write("\n".join(L) + "\n"); print("\n".join(L[:7]))


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, v: a[a.index(k) + 1] if k in a else v
    run(a[0], opt("--model", "haiku"), int(opt("--bsize", 8)), int(opt("--rounds", 6)), "--explicit" in a, int(opt("--workers", 6)))
