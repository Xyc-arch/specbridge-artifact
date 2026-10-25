"""RAISE -> GROUND -> VERIFY ON SPIDER 2.0-LITE, a very cheap first test (2026-10-12). One step per finding of the paper:
    raise    the choice checklist (checklist.CHECK)                      -- models compute both readings but do not raise the choice
    ground   + this database's data facts (spider2.db_facts)             -- a choice matters only where the data makes readings differ
    verify   keep an alternative only if it runs and its result differs from the main answer and from every kept one, at most 2
             (code only, applied to the raise+ground answer)             -- models offer alternatives that change nothing
Arms on the same tasks, interleaved: plain (the explanation call, which already allows two alternatives), placebo (the neutral
style block, ambrosia.PLACEBO, same length as raise), raise, ground (= raise + facts), verify (= ground, filtered), and sample3
(disclose.PLAIN, SQL only, sampled 3 times: the same budget of three answers with no method).
Tasks: audit.json classes -- N_MEANING meaning-different tasks and N_SINGLE single-answer tasks (false alarms), seeded.
Scores (official spider2 comparison; it already allows extra columns): main accuracy (first answer), answer set (any answer),
readings covered (distinct accepted readings matched, meaning-different tasks), answers per task, and on single-answer tasks the
share with an extra answer (a false alarm only in the sense that the benchmark accepts one reading).
    python -m specbridge.comm.transfer.rgv run [<model>]   -> out/spider2/rgv/<arm>/<model>/<instance>.json, RESULTS.md"""
import collections, concurrent.futures as cf, json, math, os, random, sys, time
from specbridge.comm.transfer import spider2 as S, checklist as K, ambrosia as AM, disclose as X

OUT = "out/spider2/rgv"; SEED, N_MEANING, N_SINGLE = 20261017, 20, 10
CALLS = {"plain": 1, "placebo": 1, "raise": 1, "ground": 1, "sample3": 3}          # verify reuses the ground answer
ARMS = ["plain", "placebo", "raise", "ground", "verify", "sample3"]


def pick():
    A = json.load(open("out/spider2/audit.json")); rng = random.Random(SEED)
    m = sorted(i for i, v in A.items() if v["class"] == "meaning-different"); s = sorted(i for i, v in A.items() if v["class"] == "single answer")
    rng.shuffle(m); rng.shuffle(s); return m[:N_MEANING] + s[:N_SINGLE], A


def prompt(arm, db):
    head, tail = X.INSTRUCTION.split("\n\nDATABASE SCHEMA:", 1)
    if arm == "sample3": return X.PLAIN
    block = {"plain": "", "placebo": AM.PLACEBO, "raise": K.CHECK, "ground": S.block("facts", db)}[arm]
    return head + ("\n\n" + block.replace("%", "%%") if block else "") + "\n\nDATABASE SCHEMA:" + tail


def _f(arm, m, iid, k=0): return "%s/%s/%s/%s%s.json" % (OUT, arm, m, iid, "__%d" % k if k else "")


def run(model="sonnet", workers=6):
    from specbridge.comm.common.llm import call, parse
    ids, _A = pick(); T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; ctx = {}
    jobs = [(i, a, k) for i in ids for a, n in CALLS.items() for k in range(n)]; random.Random(SEED).shuffle(jobs)
    for i in ids: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    def one(job):
        iid, a, k = job; f = _f(a, model, iid, k)
        if os.path.exists(f): return
        t = T[iid]; t0 = time.time(); txt = call(prompt(a, t["db"]) % (ctx[t["db"]], S.docs(t), t["question"]), model)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; G, io = S.golds(iid, E); sqls = [r.get("sql")] + [x.get("sql") for x in (r.get("alternatives") or [])[:2] if isinstance(x, dict)]
        res = []
        for q in sqls:
            if not q: continue
            df = S.run_sql(t["db"], q); res.append({"sql": q, "runs": df is not None, "matches": S.matches(df, G, io),
                                                     "sig": None if df is None else df.round(4).astype(str).to_csv(index=False)[:20000]})
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"instance_id": iid, "arm": a, "sample": k, "answers": res, "raw": None if r else txt, "seconds": round(time.time() - t0, 1)}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report(model)


def answers(arm, model, iid):
    """The answers an arm returns for a task, in order; None when not all its calls are saved."""
    if arm == "sample3":
        fs = [_f("sample3", model, iid, k) for k in range(3)]
        return None if not all(os.path.exists(f) for f in fs) else [json.load(open(f))["answers"][0] if json.load(open(f))["answers"] else {"runs": False, "matches": [], "sig": None} for f in fs]
    f = _f("ground" if arm == "verify" else arm, model, iid)
    if not os.path.exists(f): return None
    A = json.load(open(f))["answers"]
    if arm != "verify": return A
    keep, seen = A[:1], {A[0]["sig"]} if A else set()            # main answer always kept; alternatives must run and change the result
    for x in A[1:]:
        if x["runs"] and x["sig"] not in seen and len(keep) < 3: keep.append(x); seen.add(x["sig"])
    return keep


def report(model="sonnet"):
    ids, A = pick(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}
    D = {i: S.distinct(*S.golds(i, E)) for i in ids}; mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    done = [i for i in ids if all(answers(a, model, i) is not None for a in ARMS)]; R = {}
    for a in ARMS:
        x = {}
        for i in done:
            an = answers(a, model, i); got = {g for y in an for g in y["matches"]}
            x[i] = {"main": bool(an and an[0]["matches"]), "set": bool(got), "readings": len({D[i][g] for g in got}), "n": len(an)}
        R[a] = x
    M = [i for i in done if A[i]["class"] == "meaning-different"]; Sg = [i for i in done if A[i]["class"] == "single answer"]
    L = ["# Raise -> Ground -> Verify on Spider 2.0-lite, %s (`specbridge.comm.transfer.rgv`)\n" % model,
         "%d tasks done (%d meaning-different, %d single-answer; audit out/spider2/AUDIT.md). Official comparison. vs placebo / vs sample3: tasks "
         "gained/lost on answer set (all tasks) and on >= 2 readings (meaning-different tasks).\n" % (len(done), len(M), len(Sg)),
         "| arm | main correct | answer set | readings covered (meaning tasks) | >= 2 readings | answers per task | single-answer tasks with extra answers | answer set vs placebo | vs sample3 | >= 2 readings vs placebo | vs sample3 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in ARMS:
        x = R[a]; cells = []
        for key, sub in (("set", done), ("two", M)):
            for b in ("placebo", "sample3"):
                if a == b: cells.append(""); continue
                v = (lambda r: r["set"]) if key == "set" else (lambda r: r["readings"] >= 2)
                u = sum(v(x[i]) and not v(R[b][i]) for i in sub); d = sum(v(R[b][i]) and not v(x[i]) for i in sub); cells.append("+%d/-%d (p %.2g)" % (u, d, mc(u, d)))
        L.append("| %s | %d | %d | %d | %d | %.2f | %d/%d | %s |" % (a, sum(x[i]["main"] for i in done), sum(x[i]["set"] for i in done), sum(x[i]["readings"] for i in M),
                 sum(x[i]["readings"] >= 2 for i in M), sum(x[i]["n"] for i in done) / max(1, len(done)), sum(x[i]["n"] > 1 for i in Sg), len(Sg), " | ".join(cells)))
    os.makedirs(OUT, exist_ok=True); json.dump({"done": done, "arms": R}, open("%s/results_%s.json" % (OUT, model), "w"), indent=1)
    open("%s/RESULTS_%s.md" % (OUT, model), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: run(*(sys.argv[2:3] or ["sonnet"])), "report": lambda: report(*(sys.argv[2:3] or ["sonnet"]))}[sys.argv[1]]()
