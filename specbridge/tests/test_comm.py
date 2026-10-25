"""comm reproduces its committed outputs (the identity checks of the 2026-09-29/30 refactor):
  database-first build identical to out/p_gamma/dbfirst_tasks.jsonl
  choice-point verification identical to out/p_gamma/cp/verified_round0.json (known change: one point renders since the
  renderer fix)
  evaluation freeze reproduces eval v3's cases, and grading agrees with every saved answer of out/p_gamma/rcp/eval"""
import json, os, shutil, subprocess, sys, tempfile, warnings
warnings.filterwarnings("ignore")
KNOWN = {("ported:california_schools-005#1", "renders")}
# 2026-10-13: V reads a CASE-written conditional aggregate as the filtered aggregate (rule COND); only these tasks' instruction
# TEXT changes (same SQL, answer, grader): "the sum of x ..., counting only the records for which c (... 0 when there are none)"
KNOWN_V = set(['financial-F201', 'financial-F202', 'store_1-F201', 'store_1-F202', 'store_1-F203'])


def run():
    fails = []
    def check(name, ok):
        print("  %-100s %s" % (name, "ok" if ok else "FAILED"))
        if not ok: fails.append(name)
    tmp = tempfile.mkdtemp()
    subprocess.run([sys.executable, "-m", "specbridge.comm.construct.research.dbfirst", "build", "50", tmp + "/dbfirst.jsonl"], capture_output=True)
    K = ("id", "instruction", "reference_sql", "reference_answer", "grader", "tie_groups", "last_pool", "family", "slots")
    a = [{k: t[k] for k in K} for t in map(json.loads, open("out/p_gamma/dbfirst_tasks.jsonl"))]
    b = [{k: t[k] for k in K} for t in map(json.loads, open(tmp + "/dbfirst.jsonl"))]
    same = lambda x, y: x == y or (x["id"] in KNOWN_V and {k: v for k, v in x.items() if k != "instruction"} == {k: v for k, v in y.items() if k != "instruction"})
    check("database-first build identical (%d tasks; known V-wording changes: %d)" % (len(a), len(KNOWN_V)), len(a) == len(b) and all(same(x, y) for x, y in zip(a, b)))
    import specbridge.comm.transfer.choice_points as C
    C.D = tmp + "/cp"; os.makedirs(C.D); shutil.copy("out/p_gamma/cp/proposals.json", C.D); C.verify()
    x, y = json.load(open(C.D + "/verified_round0.json")), json.load(open("out/p_gamma/cp/verified_round0.json"))
    diff = {(p["id"], f) for k in x if x[k] != "UNPARSED" for p, q in zip(x[k], y[k]) for f in ("applies", "executes", "load_bearing", "renders") if p[f] != q[f]}
    check("choice-point verification identical (known changes only: %s)" % sorted(diff), diff <= KNOWN)
    import specbridge.comm.transfer.evaluate as E
    from specbridge.comm.common import db as DB
    E.D = tmp + "/rcp"; os.makedirs(E.D)
    for f in ("selection.json", "written.json", "review.json", "survivors.json"): shutil.copy("out/p_gamma/rcp/" + f, E.D)
    E.freeze()
    new = {c["case"]: c for c in json.load(open(E.D + "/eval/frozen.json"))["cases"]}
    old = {c["case"]: c for c in json.load(open("out/p_gamma/rcp/eval/frozen.json"))["cases"]}
    check("evaluation freeze: same cases and intentions", sorted(new) == sorted(old) and all(new[k]["intended"] == old[k]["intended"] for k in new))
    ag = tot = 0; runs = "out/p_gamma/rcp/eval/runs_batch_v2/haiku"
    for f in os.listdir(runs):
        o = json.load(open(os.path.join(runs, f)))
        if not o.get("final") or not o.get("executes"): continue
        rs = DB.rows(DB.connect(new[o["case"]]["snapshot"]), o["final"])
        if rs is None: continue
        tot += 1; ag += sorted(E.matches(new[o["case"]], rs)) == sorted(o.get("matches") or [])
    check("grading agrees with every saved answer (%d/%d)" % (ag, tot), ag == tot and tot > 0)
    print("%d failed" % len(fails)); return fails


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
