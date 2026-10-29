"""A SECOND LABELER FOR THE FAILURE CAUSES (2026-10-28; paper Figure causes): GPT-Sol labels, blind to Opus's labels, the same tasks
with the same prompt (inspect.INSPECT), the same task blocks and the same groups of five; we report how often the two causes agree.
Runs are the stored Haiku runs of each batch (inspect.run's model); no solver is called again.
    python -m specbridge.comm.diagnose.inspect_check run | report"""
import collections, concurrent.futures as cf, json, os, sys
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose import inspect as I
from specbridge.comm.diagnose.compare import runs, tasks

DIRS = ["out/comm_library/batch%d" % i for i in range(3, 9)] + ["out/comm_library/spider_dev"]
SECOND = "gpt-6-sol"; SOLVER = "haiku"; OUT = "out/comm_library/cause_check.json"


def _block(T, E, d, i):
    t, e = T[i], E[i]
    s = ["--- TASK %s (audit category: %s)" % (i, t["category"]), "ORIGINAL QUESTION + EVIDENCE: %s" % t["instruction"],
         "EXPLICIT VERSION: %s" % e["instruction"].split("\nConventions")[0], "GOLD SQL: %s" % t["reference_sql"],
         "GOLD ANSWER (first rows, %d rows): %s" % (len(t["reference_answer"]), str(t["reference_answer"][:5])[:400])]
    for arm in ("original", "explicit"):
        for k, g in enumerate(runs(d, SOLVER, arm, i)):
            s.append("%s repeat %d: %s%s | submitted: %s | answer (%s rows): %s" % (arm.upper(), k, "PASS" if g["pass"] else "FAIL",
                     " (would pass within 0.005)" if g.get("tol") and not g["pass"] else "", (g.get("final") or "no FINAL")[:700],
                     g.get("rows_answer"), str((g.get("answer") or [])[:5])[:300]))
    return "\n".join(s)


def run(workers=4):
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}; jobs = []
    for d in DIRS:
        T = {t["id"]: t for t in tasks(d, "original")}; E = {t["id"]: t for t in tasks(d, "explicit")}
        ids = [g["task"] for g in json.load(open(d + "/inspection.json")) if g.get("task") in T and g.get("task") in E]
        for k in range(0, len(ids), 5):
            b = ids[k:k + 5]
            if all("%s|%s" % (d, i) in done for i in b): continue
            jobs.append((d, b, I.INSPECT % ("; ".join(I.CAUSES), "\n\n".join(_block(T, E, d, i) for i in b))))
    def one(j):
        d, b, p = j; got = ask_json(p, SECOND, brace="[") or []
        return {"%s|%s" % (d, g.get("task")): g.get("cause") for g in got if isinstance(g, dict) and g.get("task") in b}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(one, jobs): done.update(r); json.dump(done, open(OUT, "w"), indent=1)
    report()


def _norm(c):
    c = (c or "").lower()
    return next((x.split(" (")[0] for x in I.CAUSES if c.startswith(x.split(" (")[0].split(" /")[0])), "other")


def report():
    S = json.load(open(OUT)); pairs = []
    for d in DIRS:
        for g in json.load(open(d + "/inspection.json")):
            k = "%s|%s" % (d, g.get("task"))
            if k in S: pairs.append((_norm(g.get("cause")), _norm(S[k])))
    n = len(pairs); agree = sum(a == b for a, b in pairs); ca = collections.Counter(a for a, _b in pairs); cb = collections.Counter(b for _a, b in pairs)
    pe = sum(ca[x] * cb[x] for x in ca) / (n * n) if n else 0; kappa = (agree / n - pe) / (1 - pe) if n and pe < 1 else 0
    oc = "reading choice"; both_oc = sum(a == oc and b == oc for a, b in pairs); any_oc = sum(a == oc or b == oc for a, b in pairs)
    res = {"n": n, "agree": agree, "kappa": round(kappa, 3), "opus": dict(ca), "second": dict(cb), "open_choice_both": both_oc, "open_choice_either": any_oc,
           "confusion": {"%s -> %s" % k: v for k, v in collections.Counter(pairs).most_common() if k[0] != k[1]}}
    json.dump(res, open(OUT.replace(".json", "_report.json"), "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
