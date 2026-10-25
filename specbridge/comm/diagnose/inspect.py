"""STEP 3: inspect every task whose arms disagree (or whose repeats split): an inspecting model sees the question, explicit
V, the reference SQL and answer and every submitted SQL with its result, and names the concrete difference and the element
of explicit V that supplied it. Tasks where explicit V refuses the reference are skipped. The diagnosis is a proposal.
    python -m specbridge.comm.diagnose.inspect run <dir> <model> | report <dir>"""
import collections, concurrent.futures as cf, json, sys
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose.compare import runs, tasks

CAUSES = ["semantic mapping (which column, table or stored value a phrase means)",
          "implicit requirement (a filter, join, DISTINCT, grouping or condition the question leaves unstated)",
          "unwanted processing (the agent added rounding, extra columns, extra filters or reformatting)",
          "output shape (which columns, how many, in what form)",
          "numeric precision / grading sensitivity (values equal up to rounding or type)",
          "reading choice (a known ambiguity: the explicit version picks the reading)",
          "run variation (the agent did it right in one repeat)",
          "renderer defect (the explicit version is worse or wrong)", "other"]

INSPECT = """You diagnose why an agent failed a BIRD text-to-SQL task from the ORIGINAL question but passed from an EXPLICIT
specification of the gold query (or the reverse). Grading compares result rows as sets. Base every claim on concrete
differences between the SUBMITTED SQL/results and the GOLD SQL/results; do not assume the explicit version is a better
interpretation of the question -- say only what information it supplied.
For each TASK, answer:
  cause         one of: %s
  supplied      the exact element of the explicit version that the original lacked or left open (quote it), or "" if none
  difference    the concrete difference between the failing submission and the gold (quote SQL fragments / values)
  question_gap  does the ORIGINAL question + evidence actually determine the gold's choice here? yes | no | partly -- one sentence
  confidence    high | medium | low
Answer ONLY JSON: [{"task": "<id>", "cause": "...", "supplied": "...", "difference": "...", "question_gap": "...", "confidence": "..."}]

%s"""


def run(d, model, only=None):
    """only: a list of task ids to inspect again (e.g. a call that failed and came back UNPARSED); their entries replace the old
    ones in inspection.json and every other entry is kept. Given in the original order, they form the same group, so the
    inspector sees the identical prompt."""
    T = {t["id"]: t for t in tasks(d, "original")}; E = {t["id"]: t for t in tasks(d, "explicit")}; todo = []
    for i, t in T.items():
        if i not in E: continue
        o = [g["pass"] for g in runs(d, model, "original", i)]; e = [g["pass"] for g in runs(d, model, "explicit", i)]
        if sorted(o) != sorted(e) or len(set(o)) > 1 or len(set(e)) > 1: todo.append(i)
    if only: todo = [i for i in todo if i in set(only)]
    def block(i):
        t, e = T[i], E[i]
        s = ["--- TASK %s (audit category: %s)" % (i, t["category"]), "ORIGINAL QUESTION + EVIDENCE: %s" % t["instruction"],
             "EXPLICIT VERSION: %s" % e["instruction"].split("\nConventions")[0], "GOLD SQL: %s" % t["reference_sql"],
             "GOLD ANSWER (first rows, %d rows): %s" % (len(t["reference_answer"]), str(t["reference_answer"][:5])[:400])]
        for arm in ("original", "explicit"):
            for k, g in enumerate(runs(d, model, arm, i)):
                s.append("%s repeat %d: %s%s | submitted: %s | answer (%s rows): %s" % (arm.upper(), k, "PASS" if g["pass"] else "FAIL",
                         " (would pass within 0.005)" if g.get("tol") and not g["pass"] else "", (g.get("final") or "no FINAL")[:700],
                         g.get("rows_answer"), str((g.get("answer") or [])[:5])[:300]))
        return "\n".join(s)
    def one(b):
        return ask_json(INSPECT % ("; ".join(CAUSES), "\n\n".join(block(i) for i in b)), "opus", brace="[") or [{"task": i, "cause": "UNPARSED"} for i in b]
    with cf.ThreadPoolExecutor(max_workers=4) as ex: got = [x for r in ex.map(one, [todo[k:k + 5] for k in range(0, len(todo), 5)]) for x in r]
    for g in got:
        i = g.get("task"); g["category"] = T.get(i, {}).get("category")
        g["original"] = [x["pass"] for x in runs(d, model, "original", i)]; g["explicit"] = [x["pass"] for x in runs(d, model, "explicit", i)]
    if only:
        old = json.load(open(d + "/inspection.json")); json.dump(old, open(d + "/inspection.before-retry.json", "w"), indent=1)
        new = {g["task"]: g for g in got}; got = [new.get(g["task"], g) for g in old] + [g for t, g in new.items() if t not in {x["task"] for x in old}]
    json.dump(got, open(d + "/inspection.json", "w"), indent=1); print("inspected %d tasks" % len(got))


def report(d):
    G = json.load(open(d + "/inspection.json")); c = collections.Counter((g["cause"].split(" (")[0], g["category"]) for g in G)
    L = ["# Inspected disagreements\n", "| cause | category | tasks |", "|---|---|---|"] + ["| %s | %s | %d |" % (k[0], k[1], n) for k, n in sorted(c.items())]
    L += ["\n| task | cause | supplied by explicit V | difference | does the question determine it? |", "|---|---|---|---|---|"]
    L += ["| %s | %s | %s | %s | %s |" % (g["task"], g["cause"].split(" (")[0], (g.get("supplied") or "").replace("|", "/")[:160],
          (g.get("difference") or "").replace("|", "/")[:200], (g.get("question_gap") or "").replace("|", "/")[:150]) for g in G]
    open(d + "/INSPECTION.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:12]))


if __name__ == "__main__":
    a = sys.argv[1:]
    {"run": lambda: run(a[1], a[2], a[a.index("--only") + 1].split(",") if "--only" in a else None), "report": lambda: report(a[1])}[a[0]]()
