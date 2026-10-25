"""READ-BACK REPAIR OF PRECISE NATURAL QUESTIONS (2026-10-02).
    python -m specbridge.comm.verbal.repair <corpus dir> <reader> [--round N]
        -> <corpus dir>/repair/round<N>.json, and <corpus dir>/corpus.repaired.jsonl (questions replaced where repaired)

WHY. A model reviewer, Sonnet or Opus, accepted questions that state a different computation than V (pilot 8ac7dd4f7e,
eval12 6ec8137fd3, 227771660b: a measure changes column number between steps and the question names the wrong one;
568a31721e: "hematocrit fraction" invites a unit change). The READ-BACK is an execution check instead of an opinion: a
reader that is not one of the evaluated solvers answers the natural question alone (the solver harness,
specbridge.comm.construct.solver_eval --model <reader>), and its answer is graded against the reference answer.

A task is REPAIRED only when the reader is wrong on the natural question AND right on explicit V (so the wording, not the
task, is at fault). The writer (precise.MODEL) revises with the reader's SQL as the finding; the reviewer
(precise.REVIEW_MODEL) reviews the revision alone; the caller reads it back again. A question that still fails after
the rounds is NOT delivered. The reader's SQL is shown to the writer, never the reference answer.
"""
import glob, json, os, re, sys, concurrent.futures as cf
from specbridge.comm.verbal import precise as P


def suspects(d, reader):
    """Tasks the reader gets wrong on the natural question: {id: reader's final SQL}."""
    R = json.load(open("%s/solver_%s.json" % (d, reader)))["results"]
    out = {}
    for k, v in R.items():
        tid, arm = k.split("|")[:2]
        if arm == "natural" and not v["correct"]:
            fs = glob.glob("out/solver/%s/%s/%s*.json" % (d.rstrip("/").split("/")[-1], reader, re.sub(r"[^\w.-]", "_", k)))   # + question hash
            sql = json.load(open(fs[0])).get("final") if fs else None
            out[tid] = sql
    return out


def revise(d, findings, workers=6):
    """findings: {id: reason}. One task per call: revise with the finding, then review alone. -> {id: record}"""
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.spec import render as R
    T = {json.loads(l)["id"]: json.loads(l) for l in open(d + "/tasks_paired.jsonl")}
    cats, prep = {}, {}
    for i in findings:     # specifications in THIS thread (SQLite connections are per thread); only model calls run in parallel
        t = T[i]; cat = cats.setdefault(t["database"], Catalogue(t["database"])); p = lift(t["reference_sql"], cat.con); s = R.spec(p, cat)
        tk = P.VZ.task(s, "natural", P.GM, cat); rec = tk["record"]
        req, extra = P.language_requirements(s, cat, rec); extra["FACTS"] = P.facts(s, cat, p)
        ctx = P.meanings(t["database"], [{"id": i, "database": t["database"], "sql": t["reference_sql"], "req": req, "extra": extra, "rec": rec, "cat": cat}], cat)
        prep[i] = (t, rec, ctx, "--- %s\nREQUIREMENTS: %s\n%s" % (i, json.dumps(req), json.dumps(extra)))
    def one(i):
        t, rec, ctx, spec = prep[i]
        draft = t["natural_precise"]["question"]; hist = [{"round": "read-back", "draft": draft, "failures": [{"id": "*", "reason": findings[i]}]}]
        for rnd in range(2):
            body = spec + "\nFAILED: [\"*\"]\nDRAFT: %s\nFINDINGS: %s" % (hist[-1]["draft"], json.dumps(hist[-1]["failures"]))
            txt, _u = P.llm(P.WRITER % ("\nREVISION: fix exactly the findings; every other requirement must stay satisfied.\n", P.VARIANT_DESC,
                                        "=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n%s" % (t["database"], ctx, body)), "revise")
            new = next((x.get("question") for x in P.parse_list(txt) if x.get("id") == i and x.get("question")), "")
            txt, _u = P.llm(P.REVIEWER % ("=== DATABASE %s -- MEANINGS:\n%s\n\nTASKS:\n%s\nDRAFT: %s" % (t["database"], ctx, spec, new)), "review")
            fails = next((x.get("failures") for x in P.parse_list(txt) if x.get("task") == i), [{"id": "*", "reason": "the reviewer returned nothing"}])
            fails = list(fails or []) + [dict(x, by="representation check") for x in P.representation_terms(new, rec)]
            hist.append({"round": rnd + 1, "draft": new, "failures": fails})
            if new and not fails: break
        ok = bool(hist[-1]["draft"]) and not hist[-1]["failures"]
        return i, {"question": hist[-1]["draft"] if ok else None, "accepted_by_review": ok, "history": hist}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(ex.map(one, list(findings)))


def finding(sql):
    return ("READ-BACK: a careful reader, given only this question, the schema and the documentation, wrote the SQL below. Its "
            "answer differs from the answer the requirements define. Find which requirement the question states differently, "
            "names wrongly (for example a column number of an earlier step), or leaves open, and fix only that. The reader's "
            "SQL: %s" % (sql or "(none)"))


def apply(d, records, out_name="corpus.repaired.jsonl"):
    """A new corpus file: repaired questions replace the old ones; a question that could not be repaired is dropped."""
    C = [json.loads(l) for l in open(d + "/corpus.jsonl")]; out = []
    for t in C:
        r = records.get(t["id"])
        if r is None: out.append(t); continue
        if not r["accepted_by_review"]: continue
        t = dict(t, question=r["question"], natural_precise=dict(t["natural_precise"], question=r["question"], status="repaired after read-back",
                                                                 repair=r["history"], reviewer=P.REVIEW_MODEL))
        out.append(t)
    with open("%s/%s" % (d, out_name), "w") as f:
        for t in out: f.write(json.dumps(t) + "\n")
    return len(C), len(out)
