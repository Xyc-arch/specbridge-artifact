"""THE ASK MECHANISM ON SPIDER 2.0-LITE, Sonnet (2026-10-12). Tasks: the meaning-different SQLite tasks (out/spider2/audit.json) NOT
used by the rgv pilot (rgv.pick), and later single-answer tasks not used by it either.
    describe   Opus writes one line per accepted READING (answers merged by spider2.distinct): the computational choice that makes this
               reading differ from the others, never a value or number from the results. Cached: out/spider2/ask/readings.json
    oracle     STEP 0 (ceiling): per (task, reading) the question + that reading's line, one SQL-only answer (disclose.PLAIN); plain = the
               question alone, one answer per task. An instance is right when the answer matches THAT reading.
    python -m specbridge.comm.transfer.ask describe | show [n] | oracle [model] | report0 [model]
At most 6 workers."""
import collections, concurrent.futures as cf, json, math, os, random, sys, time
from specbridge.comm.transfer import spider2 as S, rgv as RG, disclose as X

OUT = "out/spider2/ask"; SEED = 20261018

DESCRIBE = """Each item below is a data request from a benchmark that accepts several different answers, because the request leaves a
computational choice open. For each item you get the request and, for each accepted READING, its column names and first rows (and
its SQL when available). Write ONE line per reading that says how that reading settles the open choice -- the definition, the
population, the rule for ties or missing values, the formula -- so that an analyst told only this line would compute that reading
and not the others. Never quote a value, count or number taken from the results; describe the choice, not the answer. Lines of
one item must be different from each other.
Answer ONLY JSON: [{"id": "...", "readings": [{"reading": "<reading id>", "line": "..."}]}]

%s"""


def tasks_meaning():
    pilot, A = RG.pick(); return sorted(i for i, v in A.items() if v["class"] == "meaning-different" and i not in set(pilot))


def readings(iid, E):
    """Reading id -> list of accepted-answer indices, ids R1, R2, ... in the order of their first accepted answer."""
    G, io = S.golds(iid, E); lab = S.distinct(G, io); reps = sorted(set(lab.values()))
    return {"R%d" % (k + 1): [j for j in range(len(G)) if lab[j] == r] for k, r in enumerate(reps)}, G, io


def _E(): return {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}


def describe(batch=4, workers=6):
    from specbridge.comm.common.llm import ask_json
    T = S.tasks(); E = _E(); f = OUT + "/readings.json"; done = json.load(open(f)) if os.path.exists(f) else {}
    todo = [i for i in tasks_meaning() if i not in done]
    def item(iid):
        R, G, _io = readings(iid, E); parts = ["--- %s\nREQUEST: %s" % (iid, T[iid]["question"])]
        sql = S.GOLD + "/sql/%s.sql" % iid
        for rid, js in R.items():
            g = G[js[0]][0]; parts.append("READING %s: columns %s\n%s" % (rid, list(g.columns), g.head(5).to_csv(index=False)[:900]))
        if os.path.exists(sql): parts.append("(one accepted SQL: %s)" % open(sql).read()[:1500])
        return "\n".join(parts)
    def one(b):
        got = ask_json(DESCRIBE % "\n\n".join(item(i) for i in b), "opus", brace="[") or []
        return {x["id"]: {r["reading"]: r["line"] for r in x.get("readings", []) if isinstance(r, dict)} for x in got if isinstance(x, dict) and x.get("id") in b}
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for d in ex.map(one, [todo[k:k + batch] for k in range(0, len(todo), batch)]): done.update(d)
    os.makedirs(OUT, exist_ok=True); json.dump(done, open(f, "w"), indent=1)
    miss = [i for i in tasks_meaning() if set(done.get(i, {})) != set(readings(i, E)[0])]
    print("described %d tasks; incomplete %d %s" % (len(done), len(miss), miss[:10]))


def show(n=10):
    T = S.tasks(); D = json.load(open(OUT + "/readings.json")); ids = sorted(D); random.Random(SEED).shuffle(ids)
    for i in ids[:n]:
        print("%s [%s]\n  Q: %s" % (i, T[i]["db"], T[i]["question"][:300]))
        for r, l in sorted(D[i].items()): print("  %s: %s" % (r, l))
        print()


def _f(arm, m, iid, rid=""): return "%s/%s/%s/%s%s.json" % (OUT, arm, m, iid, "__" + rid if rid else "")


def oracle(model="sonnet", workers=6):
    from specbridge.comm.common.llm import call, parse
    T = S.tasks(); E = _E(); D = json.load(open(OUT + "/readings.json")); ids = [i for i in tasks_meaning() if i in D]; ctx = {}
    jobs = [(i, "plain", "") for i in ids] + [(i, "oracle", r) for i in ids for r in sorted(D[i])]; random.Random(SEED).shuffle(jobs)
    for i in ids: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    def one(job):
        iid, arm, rid = job; f = _f(arm, model, iid, rid)
        if os.path.exists(f): return
        t = T[iid]; q = t["question"] + ("\nWhat I mean: " + D[iid][rid] if rid else "")
        t0 = time.time(); txt = call(X.PLAIN % (S.context(t["db"]) if t["db"] not in ctx else ctx[t["db"]], S.docs(t), q), model)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; G, io = S.golds(iid, E); df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"instance_id": iid, "arm": arm, "reading": rid, "sql": r.get("sql"), "runs": df is not None, "matches": S.matches(df, G, io), "seconds": round(time.time() - t0, 1)}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report0(model)


def report0(model="sonnet"):
    E = _E(); D = json.load(open(OUT + "/readings.json")); rows = []; mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    for iid in [i for i in tasks_meaning() if i in D]:
        R, _G, _io = readings(iid, E); fp = _f("plain", model, iid)
        if not os.path.exists(fp): continue
        p = set(json.load(open(fp))["matches"])
        for rid, js in R.items():
            fo = _f("oracle", model, iid, rid)
            if not os.path.exists(fo): continue
            o = set(json.load(open(fo))["matches"]); rows.append({"task": iid, "reading": rid, "plain": bool(p & set(js)), "oracle": bool(o & set(js))})
    u = sum(r["oracle"] and not r["plain"] for r in rows); d = sum(r["plain"] and not r["oracle"] for r in rows)
    tasks = sorted({r["task"] for r in rows}); both = lambda k: sum(all(r[k] for r in rows if r["task"] == t) for t in tasks)
    L = ["# Step 0, oracle ceiling (`specbridge.comm.transfer.ask`), %s\n" % model,
         "%d meaning-different tasks not in the pilot; %d (task, reading) instances. Right = the one answer matches THAT reading.\n" % (len(tasks), len(rows)),
         "| arm | instances right | tasks with every reading right |", "|---|---|---|",
         "| plain (question only; the same answer for every reading) | %d/%d | %d/%d |" % (sum(r["plain"] for r in rows), len(rows), both("plain"), len(tasks)),
         "| oracle (question + the reading's line) | %d/%d | %d/%d |" % (sum(r["oracle"] for r in rows), len(rows), both("oracle"), len(tasks)),
         "", "Oracle vs plain: +%d/-%d instances, exact McNemar p = %.2g." % (u, d, mc(u, d))]
    json.dump(rows, open("%s/step0_%s.json" % (OUT, model), "w"), indent=1); open("%s/STEP0_%s.md" % (OUT, model), "w").write("\n".join(L) + "\n"); print("\n".join(L))


# --- STRICT VERSION (2026-10-12, after the user's check): meaning groups from out/spider2/audit_strict.json (code rule + hand check
# of 10 tasks, out/spider2/ask/HANDCHECK.md); one choice-only line per GROUP; an answer is right for a group when it matches ANY
# accepted answer in that group (tolerant: the official comparison, extra columns allowed) and, strict, also has exactly that
# answer's number of columns.
STRICT = "out/spider2/audit_strict.json"
RULE = ("STEP 0 RULE (written before the run): continue to Step 1-2 only if the oracle beats plain by at least 15 points per "
        "instance (tolerant score) with exact paired McNemar p < 0.05. Otherwise stop and report.")
DESCRIBE2 = """Each item below is a data request from a benchmark that accepts several answers because the request leaves a choice of
MEANING open. For each item you get the request and, for each MEANING GROUP, the column names and first rows of its accepted answers.
Write ONE line per group that states ONLY how that group settles the open choice: the definition, the population, the rule for ties,
missing values or matching rows, or the formula. The line must NOT contain any value, name, count, number of rows, or anything taken
from the results, and must NOT mention columns, rounding, units, labels or sort order (those are not the choice). An analyst told
only the line must be able to compute that group's reading and not the others. Lines of one item must state different choices.
Answer ONLY JSON: [{"id": "...", "groups": [{"group": "<group id>", "line": "..."}]}]

%s"""


def groups(iid, E):
    """Meaning group id (G1, G2, ...) -> accepted-answer indices, from the strict audit."""
    R, G, io = readings(iid, E); D = json.load(open(STRICT))[iid]
    return {"G%d" % (k + 1): [j for r in grp for j in R[r]] for k, grp in enumerate(D["groups"])}, G, io


def tasks_strict():
    pilot = set(RG.pick()[0]); D = json.load(open(STRICT)); return sorted(i for i, d in D.items() if d["meaning_groups"] >= 2 and i not in pilot)


def describe2(batch=4, workers=6):
    from specbridge.comm.common.llm import ask_json
    T = S.tasks(); E = _E(); f = OUT + "/groups.json"; done = json.load(open(f)) if os.path.exists(f) else {}
    todo = [i for i in tasks_strict() if i not in done]
    def item(iid):
        Gr, G, _io = groups(iid, E); parts = ["--- %s\nREQUEST: %s" % (iid, T[iid]["question"])]
        for gid, js in Gr.items():
            parts.append("MEANING GROUP %s:" % gid)
            for j in js[:2]: parts.append("  answer columns %s\n%s" % (list(G[j][0].columns), G[j][0].head(4).to_csv(index=False)[:700]))
        return "\n".join(parts)
    def one(b):
        got = ask_json(DESCRIBE2 % "\n\n".join(item(i) for i in b), "opus", brace="[") or []
        return {x["id"]: {g["group"]: g["line"] for g in x.get("groups", []) if isinstance(g, dict)} for x in got if isinstance(x, dict) and x.get("id") in b}
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for d in ex.map(one, [todo[k:k + batch] for k in range(0, len(todo), batch)]): done.update(d)
    os.makedirs(OUT, exist_ok=True); json.dump(done, open(f, "w"), indent=1)
    miss = [i for i in tasks_strict() if set(done.get(i, {})) != set(groups(i, E)[0])]
    print("described %d tasks; incomplete %d %s" % (len(done), len(miss), miss))


def show2(n=10):
    T = S.tasks(); D = json.load(open(OUT + "/groups.json")); ids = sorted(D); random.Random(SEED).shuffle(ids)
    for i in ids[:n]:
        print("%s [%s]\n  Q: %s" % (i, T[i]["db"], T[i]["question"][:240]))
        for g, l in sorted(D[i].items()): print("  %s: %s" % (g, l))
        print()


def oracle2(model="sonnet", workers=6):
    from specbridge.comm.common.llm import call, parse
    os.makedirs(OUT, exist_ok=True); open(OUT + "/RESULTS.md", "w").write("# Ask mechanism on Spider 2.0-lite\n\n" + RULE + "\n")
    T = S.tasks(); E = _E(); D = json.load(open(OUT + "/groups.json")); ids = [i for i in tasks_strict() if i in D]; ctx = {}
    jobs = [(i, "plain2", "") for i in ids] + [(i, "oracle2", g) for i in ids for g in sorted(D[i])]; random.Random(SEED).shuffle(jobs)
    for i in ids: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    def one(job):
        iid, arm, gid = job; f = _f(arm, model, iid, gid)
        if os.path.exists(f): return
        t = T[iid]; q = t["question"] + ("\nWhat I mean: " + D[iid][gid] if gid else "")
        t0 = time.time(); txt = call(X.PLAIN % (ctx[t["db"]], S.docs(t), q), model)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; G, io = S.golds(iid, E); df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"instance_id": iid, "arm": arm, "group": gid, "sql": r.get("sql"), "runs": df is not None, "ncols": None if df is None else df.shape[1],
                   "matches": S.matches(df, G, io), "seconds": round(time.time() - t0, 1)}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report2(model)


def report2(model="sonnet"):
    E = _E(); D = json.load(open(OUT + "/groups.json")); rows = []
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    for iid in [i for i in tasks_strict() if i in D]:
        Gr, G, _io = groups(iid, E); fp = _f("plain2", model, iid)
        if not os.path.exists(fp): continue
        P = json.load(open(fp))
        def ok(o, js, strict):
            hit = [j for j in o["matches"] if j in js]
            return bool(hit) and (not strict or any(o["ncols"] == G[j][0].shape[1] for j in hit))
        for gid, js in Gr.items():
            fo = _f("oracle2", model, iid, gid)
            if not os.path.exists(fo): continue
            O = json.load(open(fo)); rows.append({"task": iid, "group": gid, **{"%s_%s" % (a, k): ok(o, js, k == "strict") for a, o in (("plain", P), ("oracle", O)) for k in ("tol", "strict")}})
    n = len(rows); tasks = sorted({r["task"] for r in rows}); L = ["# Ask mechanism on Spider 2.0-lite, %s\n" % model, RULE + "\n",
         "## Step 0, oracle ceiling\n", "%d strict meaning tasks not in the pilot; %d (task, meaning group) instances. Right = the one answer matches an "
         "accepted answer of THAT group (tolerant: official comparison; strict: also the same number of columns).\n" % (len(tasks), n),
         "| arm | instances right, tolerant | strict | tasks with every group right, tolerant |", "|---|---|---|---|"]
    res = {"n": n, "tasks": len(tasks), "rows": rows}
    for a in ("plain", "oracle"):
        allg = sum(all(r[a + "_tol"] for r in rows if r["task"] == t) for t in tasks)
        L.append("| %s | %d/%d (%.1f%%) | %d/%d | %d/%d |" % (a, sum(r[a + "_tol"] for r in rows), n, 100 * sum(r[a + "_tol"] for r in rows) / max(1, n), sum(r[a + "_strict"] for r in rows), n, allg, len(tasks)))
    for k in ("tol", "strict"):
        u = sum(r["oracle_" + k] and not r["plain_" + k] for r in rows); d = sum(r["plain_" + k] and not r["oracle_" + k] for r in rows)
        gain = 100 * (sum(r["oracle_" + k] for r in rows) - sum(r["plain_" + k] for r in rows)) / max(1, n)
        res[k] = {"gain_points": gain, "up": u, "down": d, "p": mc(u, d)}; L.append("\nOracle - plain (%s): %+.1f points; +%d/-%d instances, exact McNemar p = %.2g." % (k, gain, u, d, mc(u, d)))
    g = res["tol"]; verdict = "CONTINUE" if g["gain_points"] >= 15 and g["p"] < 0.05 else "STOP"
    L.append("\n**Step 0 decision: %s** (tolerant gain %+.1f points, p = %.2g; rule: >= 15 points and p < 0.05)." % (verdict, g["gain_points"], g["p"]))
    json.dump(res, open("%s/step0_%s.json" % (OUT, model), "w"), indent=1); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]
    {"describe": lambda: describe(), "show": lambda: show(int(a[1]) if len(a) > 1 else 10), "oracle": lambda: oracle(*(a[1:2] or ["sonnet"])), "report0": lambda: report0(*(a[1:2] or ["sonnet"])),
     "describe2": lambda: describe2(), "show2": lambda: show2(int(a[1]) if len(a) > 1 else 10), "oracle2": lambda: oracle2(*(a[1:2] or ["sonnet"])),
     "report2": lambda: report2(*(a[1:2] or ["sonnet"]))}[a[0]]()
