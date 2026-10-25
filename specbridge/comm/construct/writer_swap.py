"""SUBSAMPLE CALIBRATION OF WRITER SELF-PREFERENCE (2026-10-12). Sonnet writes all natural requests and is also an evaluated
solver, so its score may carry a home advantage. With one writer no item is free of Sonnet, so no adjustment can remove it.
The cheap fix is two-phase: keep the full single-writer evaluation, and on a small RANDOM subsample C (N tasks) add a
second version written by another model (GPT-Sol) under the SAME frozen pipeline (prompts, input variant, Opus review, one
revision; only the writer changes: specbridge.comm.verbal.precise, PRECISE_WRITER_MODEL). All four solvers answer the new
version; the Sonnet-written answers are those of the full run being corrected.
Per task i in C, solver s: d_s(i) = Y(s, Sonnet-written) - Y(s, GPT-Sol-written).
  h_Sonnet   = mean_C[ d_Sonnet - mean(d_Haiku, d_Luna) ]     Sonnet's home advantage; neutral solvers remove writer quality
  h_GPT-Sol  = mean_C[ mean(d_Haiku, d_Luna) - d_GPT-Sol ]    GPT-Sol's home advantage on its own text (by-product)
  debiased Sonnet score = full-run score - h_Sonnet           (other solvers: Sonnet's text is already not their own)
Because C is a random subsample, h is unbiased for the whole corpus; the interval comes from a stratified bootstrap (C and
the rest resampled separately, so the dependence between the full score and h is kept), p from a sign-flip test on C.
Extra cost: N writes and 4N answers, instead of rewriting and re-solving the corpus.
    python -m specbridge.comm.construct.writer_swap sample | write | solve | report
At most 6 concurrent model calls (machine rule)."""
import collections, concurrent.futures as cf, hashlib, json, os, random, subprocess, sys
BASE = "out/corpora/eval12@01cfbb1e713f"; OUT = "out/writer_swap/calib200"; PREV = "out/writer_swap/calib50"; N, SEED, B = 200, 20261012, 2000   # nested: calib200 keeps calib50's tasks
WRITER2 = "gpt-6-sol"; SOLVERS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]; CONTROLS = ["haiku", "gpt-6-luna"]
RENDERED = ("passed", "revised", "deterministic")
W2 = OUT + "/" + WRITER2
FULL = "out/solver/eval12@01cfbb1e713f"                  # the full run being corrected (frozen corpus)


def sample():
    ids = sorted(json.loads(l)["id"] for l in open(BASE + "/corpus.jsonl"))
    os.makedirs(OUT, exist_ok=True)
    keep = json.load(open(PREV + "/sample.json"))["ids"] if os.path.exists(PREV + "/sample.json") else []
    S = sorted(keep + random.Random(SEED + N).sample([i for i in ids if i not in set(keep)], N - len(keep)))   # extension, not a redraw
    json.dump({"seed": SEED, "n": N, "from": BASE + "/corpus.jsonl (frozen, before read-back repairs)", "extends": PREV, "ids": S}, open(OUT + "/sample.json", "w"), indent=1)
    print("sampled %d of %d" % (N, len(ids)))


def write():
    S = json.load(open(OUT + "/sample.json"))["ids"]; os.makedirs(W2, exist_ok=True)
    if not os.path.exists(W2 + "/tasks.jsonl"):
        open(W2 + "/tasks.jsonl", "w").write(open(BASE + "/tasks.jsonl").read())
    env = dict(os.environ, PRECISE_WRITER_MODEL=WRITER2)
    subprocess.run([sys.executable, "-m", "specbridge.comm.verbal.precise", W2, "--ids", ",".join(S)], env=env, check=True)


def arms():
    """{id: {writer: text}} for sampled tasks rendered by BOTH writers, plus the task rows."""
    S = set(json.load(open(OUT + "/sample.json"))["ids"])
    T = {t["id"]: t for t in map(json.loads, open(BASE + "/corpus.jsonl")) if t["id"] in S}
    G = {t["id"]: t["natural_precise"] for t in map(json.loads, open(W2 + "/tasks_paired_sample.jsonl"))}
    A = {i: {"sonnet": T[i]["question"], WRITER2: G[i]["question"]} for i in sorted(S) if i in G and G[i]["status"] in RENDERED}
    return A, T, G


def _key(i, w, text): return "%s|%s|%s" % (i, w, hashlib.sha1(text.encode()).hexdigest()[:8])


def solve(workers=6):
    from specbridge.comm.common.solve import solve as agent
    from specbridge.comm.construct.solver_eval import serial_rerun
    A, T, _ = arms()
    jobs = [(m, dict(database=T[i]["database"], snapshot=T[i]["snapshot"], task=i, key=_key(i, w, q), text=q))
            for i, ws in A.items() for w, q in ws.items() if w == WRITER2 for m in SOLVERS]
    random.Random(SEED + 1).shuffle(jobs)                   # arms and solvers interleaved in time
    def one(j):
        m, it = j
        try: agent([it], m, "%s/solver/%s" % (OUT, m), bsize=1, rounds=6, workers=1)
        except Exception as e: print("failed", m, it["key"], e, flush=True)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for n, _ in enumerate(ex.map(one, jobs), 1):
            if n % 50 == 0: print("done %d/%d" % (n, len(jobs)), flush=True)
    for m in SOLVERS:
        d = "%s/solver/%s" % (OUT, m); R = {}
        for f in os.listdir(d) if os.path.isdir(d) else []:
            r = json.load(open(d + "/" + f)); R[r["key"]] = r
        serial_rerun(R, T, d)
    open(OUT + "/solve.done", "w").write("ok\n")


SAME = OUT + "/same"     # Sonnet-written version re-answered on 2026-10-12 with the same harness as the GPT-Sol-written one


def solve_same(workers=6):
    """Re-answer the Sonnet-written version of the calibration tasks now, so both versions are answered on the same day with the same
    harness (the full-run answers are from 2026-10-02). -> <OUT>/same/<model>/"""
    from specbridge.comm.common.solve import solve as agent
    A, T, _ = arms()
    jobs = [(m, dict(database=T[i]["database"], snapshot=T[i]["snapshot"], task=i, key=_key(i, "sonnet", ws["sonnet"]), text=ws["sonnet"])) for i, ws in A.items() for m in SOLVERS]
    random.Random(SEED + 5).shuffle(jobs)
    def one(j):
        m, it = j
        try: agent([it], m, "%s/%s" % (SAME, m), bsize=1, rounds=6, workers=1)
        except Exception as e: print("failed", m, it["key"], e, flush=True)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for n, _ in enumerate(ex.map(one, jobs), 1):
            if n % 100 == 0: print("done %d/%d" % (n, len(jobs)), flush=True)
    from specbridge.comm.construct.solver_eval import serial_rerun
    for m in SOLVERS:
        d = "%s/%s" % (SAME, m); R = {json.load(open(d + "/" + f))["key"]: json.load(open(d + "/" + f)) for f in os.listdir(d)}
        serial_rerun(R, T, d)


def _grade(t, r):
    from specbridge.comm.common.grade import spec
    return int(bool(r.get("executes") and spec(t["grader"], t["reference_answer"], r.get("answer"), t.get("tie_groups"), t.get("last_pool"))))


def outcomes(same=False):
    """F[m][id]: full run on the Sonnet-written frozen corpus (all tasks). C[m][id]: the second writer's version on the subsample.
    Only saved answers count (a failed call is not wrong)."""
    import re
    T = {t["id"]: t for t in map(json.loads, open(BASE + "/corpus.jsonl"))}; A, _, _ = arms()
    F = {m: {} for m in SOLVERS}; C = {m: {} for m in SOLVERS}
    for m in SOLVERS:
        for i, t in T.items():
            f = "%s/%s/%s.json" % (FULL, m, re.sub(r"[^\w.-]", "_", "%s|natural|%s" % (i, hashlib.sha1(t["question"].encode()).hexdigest()[:8])))
            if os.path.exists(f): F[m][i] = _grade(t, json.load(open(f)))
        for i, ws in A.items():
            f = "%s/solver/%s/%s.json" % (OUT, m, re.sub(r"[^\w.-]", "_", _key(i, WRITER2, ws[WRITER2])))
            if os.path.exists(f): C[m][i] = _grade(T[i], json.load(open(f)))
            if same:                                         # same-day Sonnet-written answer replaces the full-run one
                g = "%s/%s/%s.json" % (SAME, m, re.sub(r"[^\w.-]", "_", _key(i, "sonnet", ws["sonnet"])))
                if os.path.exists(g): F[m][i] = _grade(T[i], json.load(open(g)))
                else: F[m].pop(i, None)
    return F, C, A


def _est(F, C, cal, rest):
    mean = lambda v: sum(v) / len(v) if v else float("nan")
    d = {m: {i: F[m][i] - C[m][i] for i in cal} for m in SOLVERS}
    ctl = {i: sum(d[c][i] for c in CONTROLS) / len(CONTROLS) for i in cal}
    e = {"h_sonnet": mean([d["sonnet"][i] - ctl[i] for i in cal]), "h_gpt-6-sol": mean([ctl[i] - d[WRITER2][i] for i in cal]),
         "writer_effect_controls": mean([ctl[i] for i in cal])}
    for m in SOLVERS:
        e["d_" + m] = mean([d[m][i] for i in cal])
        e["full_" + m] = mean([F[m][i] for i in cal + rest])
    e["debiased_sonnet"] = e["full_sonnet"] - e["h_sonnet"]
    return e


def report(same=False):
    F, C, A = outcomes(same)
    allids = [i for i in F["sonnet"] if all(i in F[m] for m in SOLVERS)]
    cal = [i for i in A if i in allids and all(i in C[m] for m in SOLVERS)]; rest = [i for i in allids if i not in set(cal)]
    est = _est(F, C, cal, rest); rng = random.Random(SEED + 2); boots = collections.defaultdict(list)
    for _ in range(B):                                       # stratified: subsample and the rest resampled separately
        bc = [rng.choice(cal) for _ in cal]; br = [rng.choice(rest) for _ in rest]
        for k, v in _est(F, C, bc, br).items(): boots[k].append(v)
    def flip(vals, draws=20000):                             # sign-flip randomization test, two-sided
        obs = abs(sum(vals)); r2 = random.Random(SEED + 3); nz = [x for x in vals if x]
        if not nz: return 1.0
        return (sum(abs(sum(x if r2.random() < .5 else -x for x in nz)) >= obs - 1e-12 for _ in range(draws)) + 1) / (draws + 1)
    ctl = lambda i: sum(F[c][i] - C[c][i] for c in CONTROLS) / len(CONTROLS)
    pv = {"h_sonnet": flip([F["sonnet"][i] - C["sonnet"][i] - ctl(i) for i in cal]),
          "h_gpt-6-sol": flip([ctl(i) - (F[WRITER2][i] - C[WRITER2][i]) for i in cal])}
    for m in SOLVERS: pv["d_" + m] = flip([F[m][i] - C[m][i] for i in cal])
    ci = lambda k: [100 * sorted(boots[k])[int(.025 * B)], 100 * sorted(boots[k])[int(.975 * B) - 1]]
    res = {"n_corpus": len(allids), "n_calibration": len(cal), "sampled": N, "rendered_by_second_writer": len(A),
           "estimates": {k: {"points": 100 * v, "ci95": ci(k), "p": pv.get(k)} for k, v in est.items()},
           "calibration_accuracy": {m: {"sonnet_written": sum(F[m][i] for i in cal), WRITER2 + "_written": sum(C[m][i] for i in cal), "n": len(cal)} for m in SOLVERS}}
    res["sonnet_written_answers"] = "same day (2026-10-12)" if same else "full run (2026-10-02)"
    json.dump(res, open(OUT + ("/results_same.json" if same else "/results.json"), "w"), indent=1)
    E = res["estimates"]; f = lambda k: "%+.1f [%+.1f, %+.1f]" % (E[k]["points"], E[k]["ci95"][0], E[k]["ci95"][1])
    L = ["# Subsample calibration of writer self-preference (`specbridge.comm.construct.writer_swap`)\n",
         "Corpus: %d tasks with all four full-run answers (Sonnet-written, frozen). Calibration subsample: %d sampled (seed %d), %d rendered by %s and answered by all four." % (len(allids), N, SEED, len(cal), WRITER2),
         "Same pipeline for both writers (Opus review, one revision). Extra cost: %d writes, %d answers.\n" % (N, 4 * len(cal)),
         "| solver | calibration: Sonnet-written | calibration: %s-written | writer effect d_s, points [95%% CI] | p |" % WRITER2, "|---|---|---|---|---|"]
    for m in SOLVERS:
        a = res["calibration_accuracy"][m]
        L.append("| %s | %d/%d | %d/%d | %s | %.3f |" % (m, a["sonnet_written"], a["n"], a[WRITER2 + "_written"], a["n"], f("d_" + m), E["d_" + m]["p"]))
    L += ["\n| estimate | points [95% CI] | p |", "|---|---|---|",
          "| writer effect on neutral solvers (Haiku, GPT-Luna) | %s | |" % f("writer_effect_controls"),
          "| Sonnet home advantage | %s | %.3f |" % (f("h_sonnet"), E["h_sonnet"]["p"]),
          "| GPT-Sol home advantage (its own text) | %s | %.3f |" % (f("h_gpt-6-sol"), E["h_gpt-6-sol"]["p"]),
          "| Sonnet, full run (biased) | %.1f%% | |" % E["full_sonnet"]["points"],
          "| **Sonnet, debiased** | %+.1f [%.1f, %.1f] (interval capped to 0-100) | |" % (E["debiased_sonnet"]["points"], max(0, E["debiased_sonnet"]["ci95"][0]), min(100, E["debiased_sonnet"]["ci95"][1]))]
    L += ["| %s, full run (no correction: not the writer) | %.1f%% | |" % (m, E["full_" + m]["points"]) for m in SOLVERS if m != "sonnet"]
    L.append("\nSonnet-written answers: %s." % res["sonnet_written_answers"])
    open(OUT + ("/RESULTS_same.md" if same else "/RESULTS.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"sample": sample, "write": write, "solve": solve, "report": report, "solve_same": solve_same, "report_same": lambda: report(True)}[sys.argv[1]]()
