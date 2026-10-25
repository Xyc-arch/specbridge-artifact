"""ABLATION OF THE GENERATOR, MODEL-FREE (2026-10-05): what each mechanism contributes.
    python -m specbridge.comm.construct.ablation run [--per-cell 25] [--workers 6]   -> out/ablation/<arm>/<db>.json
    python -m specbridge.comm.construct.ablation report                               -> out/ablation/ABLATION.md
Arms (leave one out, plus everything off = a naive combination of the same operations):
  full        the generator as used everywhere else
  -profile    no column meaning: every numeric column (keys included) is one unit and additive (compose.naive_quantities)
  -varies     row quantities need not vary on the data
  -types      no unit / kind / additivity rules on operations
  -restate    restated, recomputed and collapsing comparisons allowed; a quantity may be combined with itself
  -lookahead  each step is chosen without checking that the target depth is still reachable (checked only at the end)
  -stepcheck  no data check when a step is taken (checked only at the end)
  -dedupe     sampling with replacement (duplicates possible)
  naive       all of the above off
Every arm requests the same depth cells (arithmetic depth 1-2 x step depth 3-6, those the FULL grammar reaches on the
database) with the same number of attempts per cell and the same seed. Every finished program is judged by the same
yardstick: it runs and has rows, every data check of its steps holds (compose.check), no aggregate is recomputed and no
comparison or cut is trivial (integrity receipts), its depth MEASURED on the SQL equals the requested cell, and it is new.
Whether a program is MEANINGFUL is not judged here (no model call)."""
import collections, concurrent.futures as cf, json, os, random, subprocess, sys, time

OUT = "out/ablation"
E12 = ["baseball_1", "sakila_1", "customers_and_invoices", "chinook_1", "financial", "student_club", "thrombosis_prediction",
       "formula_1", "archeology", "insider", "crypto", "alien"]
ALL = ("profile", "varies", "types", "restate")
ARMS = {"full": ((), {}), "-profile": (("profile",), {}), "-varies": (("varies",), {}), "-types": (("types",), {}),
        "-restate": (("restate",), {}), "-lookahead": ((), {"lookahead": False}), "-stepcheck": ((), {"data_checks": False}),
        "-dedupe": ((), {"dedupe": False}), "naive": (ALL, {"lookahead": False, "data_checks": False, "dedupe": False})}
CELLS = [(a, s) for a in (1, 2) for s in (3, 4, 5, 6)]


def one(arm, db, per_cell=25, seed=1, budget=240):
    from specbridge.pd.structures.compose import Space, Sampler, check
    from specbridge.pd.structures.depth import of_sql
    from specbridge.pd.structures import integrity as I
    from specbridge.pd.structures.algebra import lift
    ablate, prefs = ARMS[arm]
    t0 = time.time(); F = Space(db)                                       # built ONCE: targets, admitted quantities, and the full arm
    targets = [c for c in CELLS if c in F.reachable()]                     # the same targets for every arm
    full_q = {t: {q["sql"] for q in F.qs[t]} for t in F.rec} if ablate else {}   # the row quantities the full profile admits
    sp = Space(db, ablate) if ablate else F; setup = time.time() - t0
    smp = Sampler(sp, random.Random(seed), dict(prefs)); con = sp.S.con
    seen, rows, fail = set(), [], collections.Counter()
    t1 = time.time(); attempts = 0; stopped = False
    from specbridge.pd.structures.compose import step_check
    def valid(P, sql):
        # the same yardstick as compose.check, reusing the step checks the sampler already ran on this program
        from specbridge.pd.structures.integrity import recomputed
        try:
            rc = recomputed(lift(sql, con))
            if rc: return False, "a step recomputes an existing aggregate"
            if not con.execute(sql).fetchone(): return False, "empty answer"
            for ck in P.checks:
                k = json.dumps(ck, default=str)
                why = smp._step[k] if k in smp._step else step_check(con, ck)
                smp._step[k] = why
                if why: return False, why
            return True, ""
        except Exception as e: return False, "error: %s" % str(e)[:60]
    for c in targets:
        for _ in range(per_cell):
            if time.time() - t1 > budget: stopped = True; break
            attempts += 1
            try: P = smp.draw(c)
            except Exception as e: fail["generator error"] += 1; continue
            if P is None: fail["nothing left to draw"] += 1; continue
            sql = P.sql(); r = {"cell": "%d,%d" % c, "sql": sql}
            # PROFILE-SOUND (model-free proxy for meaning): every row quantity the program uses is one the full profile admits
            # (a measure or count column, or a difference / ratio the units allow) -- not a key, code or unit-mixing combination
            qsql = {q["sql"] for q in sp.qs.get(P.t, []) if (P.t, q["name"]) in P.base} if hasattr(P, "t") else set()
            r["profile_sound"] = ((not full_q) or all(x in full_q.get(P.t, set()) for x in qsql)) and not getattr(P, "untyped", False)
            r["duplicate"] = sql in seen; seen.add(sql)
            try:
                m = of_sql(sql, con); r["measured"] = "%d,%d" % (m["arith"], m["steps"])
            except Exception: r["measured"] = None
            con.set_progress_handler((lambda t=time.time(): 1 if time.time() - t > 20 else 0), 10000)
            ok, why = valid(P, sql)
            con.set_progress_handler(None, 0)
            if ok:
                try:
                    p = lift(sql, con); ok = not I.trivial(p, con); why = why if ok else "trivial comparison or cut"
                except Exception as e: ok, why = False, "error: %s" % str(e)[:60]
            r["valid"], r["why"] = ok, why if not ok else ""
            r["on_target"] = r["measured"] == r["cell"]
            r["good"] = ok and r["on_target"] and not r["duplicate"]
            rows.append(r)
    sec = time.time() - t1
    res = {"arm": arm, "db": db, "targets": len(targets), "attempts": attempts, "time_budget_hit": stopped, "setup_seconds": round(setup, 1), "seconds": round(sec, 1),
           "drawn": len(rows), "valid": sum(r["valid"] for r in rows), "on_target": sum(r["on_target"] for r in rows),
           "duplicates": sum(r["duplicate"] for r in rows), "good": sum(r["good"] for r in rows),
           "good_and_sound": sum(r["good"] and r["profile_sound"] for r in rows),
           "fail": dict(fail), "invalid_reasons": dict(collections.Counter(r["why"].split(":")[0] for r in rows if not r["valid"]).most_common()), "rows": rows}
    os.makedirs("%s/%s" % (OUT, arm), exist_ok=True); json.dump(res, open("%s/%s/%s.json" % (OUT, arm, db), "w"), indent=1)


def run(per_cell=25, workers=6, timeout=900):
    jobs = [(a, db) for a in ARMS for db in E12 if not os.path.exists("%s/%s/%s.json" % (OUT, a, db))]
    def child(j):
        try:
            p = subprocess.run([sys.executable, "-m", "specbridge.comm.construct.ablation", "--one", j[0], j[1], str(per_cell)], capture_output=True, text=True, timeout=timeout)
            return j, p.returncode, p.stderr[-300:]
        except subprocess.TimeoutExpired: return j, "timeout", ""
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for j, rc, err in ex.map(child, jobs): print(j, rc, err.strip().splitlines()[-1] if err.strip() else "", flush=True)
    print(report())


def report():
    L = ["# Generator ablation (model-free)\n", __doc__.split("\n", 2)[2].strip() + "\n",
         "Each job draws for at most 240 s; rates are per attempt made. Time is not reported: two harness versions ran (the first ran each data check twice), so seconds are not comparable across arms. 'Sound' = every row quantity is one the full profile admits AND no "
         "step breaks the full type rules (unit, kind, additivity): a model-free proxy for meaning.\n",
         "| arm | attempts | programs drawn | valid | on target depth | duplicates | good (valid, on target, new) | good and sound | good per attempt | good and sound per attempt |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    reasons = {}
    for a in ARMS:
        R = [json.load(open(f)) for f in sorted(__import__("glob").glob("%s/%s/*.json" % (OUT, a)))]
        if not R: continue
        s = lambda k: sum(r[k] for r in R)
        L.append("| %s | %d | %d | %d | %d | %d | **%d** | %d | %.2f | %.3f |" % (a, s("attempts"), s("drawn"), s("valid"), s("on_target"), s("duplicates"), s("good"), s("good_and_sound"),
                 s("good") / max(1, s("attempts")), s("good_and_sound") / max(1, s("attempts"))))
        reasons[a] = collections.Counter()
        for r in R: reasons[a].update(r["invalid_reasons"]); reasons[a].update({"not drawn: " + k: v for k, v in r["fail"].items()})
        L[-1] += "" if len(R) == len(E12) else " (%d of %d databases)" % (len(R), len(E12))
        hit = [r["db"] for r in R if r.get("time_budget_hit")]
        if hit: L[-1] += " (time budget ended on %s)" % ", ".join(hit)
    L += ["\n## Why programs were not good, per arm\n"]
    for a, c in reasons.items(): L.append("- **%s**: %s" % (a, "; ".join("%s %d" % kv for kv in c.most_common(6)) or "none"))
    open("%s/ABLATION.md" % OUT, "w").write("\n".join(L) + "\n"); return "\n".join(L)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--one": one(a[1], a[2], int(a[3])); sys.exit(0)
    opt = lambda k, d: int(a[a.index(k) + 1]) if k in a else d
    if a[0] == "run": run(opt("--per-cell", 25), opt("--workers", 6))
    elif a[0] == "report": print(report())
