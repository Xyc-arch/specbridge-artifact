"""DOES KNOWING THE AUTHORS' DEFAULTS HELP? The same solver answers BIRD dev questions in their original wording, with and
without one fixed note that tells it how the people who wrote BIRD usually settle what a question leaves unsaid. The note
is the same for every question (nothing about the question is revealed) and is built from BIRD TRAIN only
(specbridge.comm.diagnose.inclination, silent questions); it covers decisions of meaning, never output form.

    python -m specbridge.comm.diagnose.prior build            -> out/prior/bird600/tasks.jsonl, NOTE.md
    python -m specbridge.comm.diagnose.prior run <model> [n]  -> out/prior/bird600/runs/<model>/{plain,defaults}/<id>.json (first n tasks)
    python -m specbridge.comm.diagnose.prior report <model>   -> out/prior/bird600/RESULTS_<model>.md
    python -m specbridge.comm.diagnose.prior placebo <model> [<model> ...] -> runs/<model>/placebo/ (CLEAN questions only)
    python -m specbridge.comm.diagnose.prior report3                 -> out/prior/bird600/PLACEBO.md, placebo.json

PLACEBO AND CLEAN SET (2026-10-12, reviewer points): CLEAN = questions from the 6 databases never used in the error analysis
(specbridge.comm.diagnose.tasks.BIRD_DBS are the 5 that were). The placebo note has the same frame, length and tone as the note but
only SQL formatting style, which cannot change a query's result. Three arms on CLEAN: plain, placebo, note.

Sample: 600 BIRD dev questions whose reference runs, drawn with a fixed seed from all 11 databases. Solver and grading as in
the confirmation runs: one question per call, up to 6 rounds, BIRD set match and the shape-tolerant grade."""
import hashlib, json, os, random, re, sys
from specbridge.comm.common import db as DB, grade as G
from specbridge.comm.common.solve import solve

ROOT = "dev_unzipped/dev_20240627"
OUT = "out/prior/bird600"
N, SEED = 600, 20261005

# The note: one line per decision, "<usual reading>" with BIRD-train share among silent questions; filled in by note().
LINES = [("ties_and_selection", "A", "When a question asks for the highest, lowest, first or last item, return one row (ORDER BY ... LIMIT 1), not every tied row"),
         ("counting_unit", "B", "When counting over joined tables, count rows (COUNT(x)), not distinct entities, unless the question says \"different\", \"distinct\" or \"unique\""),
         ("missing_values", "B", "When sorting to find the highest or lowest value, do not add a filter for missing values (IS NOT NULL) unless asked"),
         ("population_scope", "A", "Join tables with inner joins; records without a match are left out"),
         ("boundary_between", "B", "\"Between X and Y\" includes both ends (BETWEEN, or >= and <=)"),
         ("boundary_open", "A", "\"After\", \"before\", \"over\", \"above\", \"under\" and \"below\" are strict (> or <)"),
         ("text_match", "A", "A named value is matched exactly (=), not as a substring (LIKE '%...%')"),
         ("calculation_scale", "A", "A percentage is multiplied by 100"),
         ("calculation_division", "A", "Divisions are made real-valued (CAST(... AS REAL) or * 1.0), so integer division never truncates")]


def note():
    from specbridge.comm.diagnose.inclination import measure_groups
    k = measure_groups()["BIRD train"]["kinds"]
    rows = []
    for kind, side, text in LINES:
        a, b = k[kind]["n_A"], k[kind]["n_B"]; share = (a if side == "A" else b) / (a + b)
        rows.append("- %s (%.0f%% of such questions)." % (text, 100 * share))
    return ("NOTE ON THESE USERS. These questions come from users who often leave some decisions unsaid. When the question does "
            "not settle a decision, they usually mean the following (the share is how often their own answers did so):\n"
            + "\n".join(rows) +
            "\nThey also leave other choices unsaid (for example which of two similar columns, a stored code or its label, which date). "
            "Choose as these users most likely would, in the same spirit. Anything the question states overrides this note.\n\n")


PLACEBO = ("NOTE ON THESE USERS. These questions come from users who care about how SQL is written. When the question does not "
           "settle how to write the query, they usually prefer the following (their habits when they write SQL themselves):\n"
           "- Write SQL keywords such as SELECT, FROM, WHERE, GROUP BY and ORDER BY in upper case, and names as they appear in the schema.\n"
           "- Give each table in a join a short alias of one to three letters, and use that alias for every column taken from that table.\n"
           "- Write joins with explicit JOIN ... ON syntax, not as a comma-separated list of tables with the condition in WHERE.\n"
           "- Put each major clause (SELECT, FROM, each JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT) on its own line.\n"
           "- Do not end the query with a semicolon, and do not add comments inside the query.\n"
           "- Use single quotes for text values and double quotes only for names that contain spaces or symbols.\n"
           "- Leave one space on each side of operators such as =, <, >, + and -, and after each comma in a list.\n"
           "- When a subquery is needed, indent it and give it a short, readable alias that says what it holds.\n"
           "- Keep the query as short as it can be while still answering the question in full.\n"
           "They also have other style habits (for example how long a line may be, or where a line breaks). Write as these users most "
           "likely would, in the same spirit. Anything the question states overrides this note.\n\n")


PLACEBO_N = 180      # 2026-10-12: a fixed random half of the clean questions (seeded, NOT chosen by which answers finished first)


def clean_ids(n=PLACEBO_N):
    from specbridge.comm.diagnose.tasks import BIRD_DBS
    ids = [t["id"] for t in tasks() if t["database"] not in BIRD_DBS]
    return sorted(random.Random(SEED + 180).sample(ids, n)) if n else ids


def _grade_save(o, t, out):
    a = o.get("answer"); ref = t["reference_answer"]
    if a is None and o.get("final") and not o.get("serial_rerun"):
        a = DB.rows(DB.connect(t["snapshot"]), o["final"]); o["serial_rerun"] = "executes" if a is not None else "still fails"
        if a is not None: o.update(answer=a, executes=True)
    o["pass"] = a is not None and G.bird_ex(ref, a); o["shape"] = a is not None and G.shape_tolerant(ref, a)
    json.dump(o, open("%s/%s.json" % (out, t["id"]), "w"), default=str)


def placebo(models):
    """On the CLEAN questions: the placebo note and the real note again ("note2"), interleaved in ONE run in random order across
    models, arms and questions, so the key contrast (note vs placebo) has no time difference. At most 6 concurrent calls."""
    import concurrent.futures as cf
    keep = set(clean_ids()); T = [t for t in tasks() if t["id"] in keep]; nt = open(OUT + "/NOTE.md").read()
    jobs = [(m, arm, pre, t) for m in models for arm, pre in (("placebo", PLACEBO), ("note2", nt)) for t in T]
    random.Random(SEED + 12).shuffle(jobs)
    def one(j):
        m, arm, pre, t = j; out = "%s/runs/%s/%s" % (OUT, re.sub(r"\W", "_", m), arm)
        if os.path.exists("%s/%s.json" % (out, t["id"])) and "pass" in json.load(open("%s/%s.json" % (out, t["id"]))): return
        try:
            r = solve([{"key": t["id"], "text": pre + t["instruction"], "snapshot": t["snapshot"], "database": t["database"]}], m, out, bsize=1, workers=1)
            if t["id"] in r: _grade_save(r[t["id"]], t, out)
        except Exception as e: print("failed", m, arm, t["id"], e, flush=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for n, _ in enumerate(ex.map(one, jobs), 1):
            if n % 100 == 0: print("done %d/%d" % (n, len(jobs)), flush=True)


def report3():
    """Three arms on CLEAN questions, paired: plain vs placebo vs note; gains with paired bootstrap and exact McNemar; and the
    note-minus-placebo gain on questions with / without a silent decision the note addresses."""
    from math import comb
    from specbridge.comm.diagnose.inclination import sides, CUES
    mcn = lambda u, d: min(1.0, 2 * sum(comb(u + d, i) for i in range(min(u, d) + 1)) / 2 ** (u + d)) if u + d else 1.0
    U = {k: sd for k, sd, _ in LINES}
    def silent(t):
        sd = sides(t["reference_sql"], t["instruction"])
        return any(k in sd and not (k in CUES and CUES[k].search(t["instruction"])) for k in U if k not in ("population_scope", "text_match"))
    keep = set(clean_ids()); T = [t for t in tasks() if t["id"] in keep]; res = {"note_chars": len(open(OUT + "/NOTE.md").read()), "placebo_chars": len(PLACEBO), "models": {}}
    L = ["# Placebo control on the clean questions (databases never used in the error analysis)\n",
         "%d questions from %d databases. Note %d characters, placebo %d (formatting style only).\n" % (len(T), len({t["database"] for t in T}), res["note_chars"], res["placebo_chars"]),
         "| solver | grade | n | plain | placebo | note | placebo - plain | note - plain | note - placebo [95% CI], p |", "|---|---|---|---|---|---|---|---|---|"]
    for model in ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]:
        base = "%s/runs/%s" % (OUT, re.sub(r"\W", "_", model)); rows = []
        for t in T:
            f = {a: "%s/%s/%s.json" % (base, "note2" if a == "defaults" else a, t["id"]) for a in ("plain", "placebo", "defaults")}
            if all(os.path.exists(p) for p in f.values()): rows.append((t, {a: json.load(open(p)) for a, p in f.items()}))
        n = len(rows)
        if not n: continue
        res["models"][model] = {"n": n}
        for g in ("pass", "shape"):
            c = {a: sum(bool(r[a][g]) for _t, r in rows) for a in ("plain", "placebo", "defaults")}
            diff = [int(bool(r["defaults"][g])) - int(bool(r["placebo"][g])) for _t, r in rows]; rng = random.Random(20261003)
            bs = sorted(sum(diff[rng.randrange(n)] for _ in range(n)) / n for _ in range(2000)); p = mcn(sum(x > 0 for x in diff), sum(x < 0 for x in diff))
            sub = {}
            for lab, kp in (("silent", True), ("other", False)):
                rs = [r for t, r in rows if silent(t) == kp]
                sub[lab] = {"n": len(rs), **{a: sum(bool(r[a][g]) for r in rs) for a in ("plain", "placebo", "defaults")}}
            res["models"][model][g] = {"counts": c, "note_minus_placebo": 100 * sum(diff) / n, "ci95": [100 * bs[50], 100 * bs[1949]], "p": p, "by_subset": sub}
            L.append("| %s | %s | %d | %d | %d | %d | %+.1f | %+.1f | %+.1f [%.1f, %.1f], p=%.2g |" % (model, "BIRD" if g == "pass" else "shape", n, c["plain"], c["placebo"], c["defaults"],
                     100 * (c["placebo"] - c["plain"]) / n, 100 * (c["defaults"] - c["plain"]) / n, 100 * sum(diff) / n, 100 * bs[50], 100 * bs[1949], p))
    L += ["\n| solver | subset (BIRD grade) | n | plain | placebo | note |", "|---|---|---|---|---|---|"]
    for model, v in res["models"].items():
        for lab in ("silent", "other"):
            s_ = v["pass"]["by_subset"][lab]; L.append("| %s | %s | %d | %d | %d | %d |" % (model, "silent decision the note addresses" if lab == "silent" else "other", s_["n"], s_["plain"], s_["placebo"], s_["defaults"]))
    L.append("\nThe note and placebo arms ran together in one interleaved run (2026-10-12); the plain arm is the run of the 600-question experiment (2026-10-05), so note-minus-placebo is the same-run contrast.")
    json.dump(res, open(OUT + "/placebo.json", "w"), indent=1); open(OUT + "/PLACEBO.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


def build():
    snaps = DB.snapshots(); dev = json.load(open(ROOT + "/dev.json")); rng = random.Random(SEED); rng.shuffle(dev); T = []
    for x in dev:
        if len(T) == N: break
        db = x["db_id"]; snap = snaps.get(db, ("%s/dev_databases/%s/%s.sqlite" % (ROOT, db, db), None))[0]
        ref = DB.rows(DB.connect(snap), x["SQL"])
        if ref is None: continue
        T.append({"id": "q%04d" % x["question_id"], "question_id": x["question_id"], "database": db, "snapshot": snap, "difficulty": x["difficulty"],
                  "instruction": x["question"] + ("\nEvidence: " + x["evidence"] if x.get("evidence") else ""), "reference_sql": x["SQL"], "reference_answer": ref})
    os.makedirs(OUT, exist_ok=True)
    with open(OUT + "/tasks.jsonl", "w") as f:
        for t in T: f.write(json.dumps(t, default=str) + "\n")
    n = note(); open(OUT + "/NOTE.md", "w").write(n)
    print("tasks", len(T), "databases", len({t["database"] for t in T}), "note sha", hashlib.sha256(n.encode()).hexdigest()[:12])


def tasks(): return [json.loads(l) for l in open(OUT + "/tasks.jsonl")]


def run(model, n=None):
    T = tasks()[:int(n)] if n else tasks(); nt = open(OUT + "/NOTE.md").read()
    for arm, pre in (("plain", ""), ("defaults", nt)):
        out = "%s/runs/%s/%s" % (OUT, re.sub(r"\W", "_", model), arm)
        res = solve([{"key": t["id"], "text": pre + t["instruction"], "snapshot": t["snapshot"], "database": t["database"]} for t in T], model, out, bsize=1)
        R = {t["id"]: t for t in T}
        for k, o in res.items():
            a = o.get("answer"); ref = R[k]["reference_answer"]
            if a is None and o.get("final") and not o.get("serial_rerun"):   # a timeout under load is not an answer: run alone once
                a = DB.rows(DB.connect(R[k]["snapshot"]), o["final"]); o["serial_rerun"] = "executes" if a is not None else "still fails"
                if a is not None: o.update(answer=a, executes=True)
            o["pass"] = a is not None and G.bird_ex(ref, a); o["shape"] = a is not None and G.shape_tolerant(ref, a)
            json.dump(o, open("%s/%s.json" % (out, k), "w"), default=str)


def report(model):
    T = tasks(); base = "%s/runs/%s" % (OUT, re.sub(r"\W", "_", model)); rows = []
    for t in T:
        f = {arm: "%s/%s/%s.json" % (base, arm, t["id"]) for arm in ("plain", "defaults")}
        if all(os.path.exists(p) for p in f.values()):
            rows.append((t, {arm: json.load(open(p)) for arm, p in f.items()}))
    n = len(rows); L = ["# Original question, with vs without the note on the authors' defaults (%s)\n" % model,
                        "Paired over %d questions (both arms answered). Note: `NOTE.md` (from BIRD train only).\n" % n,
                        "| grade | plain | with note | note only right | plain only right |", "|---|---|---|---|---|"]
    for g in ("pass", "shape"):
        p = sum(r["plain"][g] for _t, r in rows); d = sum(r["defaults"][g] for _t, r in rows)
        up = sum(r["defaults"][g] and not r["plain"][g] for _t, r in rows); down = sum(r["plain"][g] and not r["defaults"][g] for _t, r in rows)
        L.append("| %s | %d/%d | %d/%d | %d | %d |" % ("BIRD set match" if g == "pass" else "shape tolerated", p, n, d, n, up, down))
    from math import comb
    from specbridge.comm.diagnose.inclination import sides, CUES
    mcn = lambda u, d: min(1.0, 2 * sum(comb(u + d, i) for i in range(min(u, d) + 1)) / 2 ** (u + d)) if u + d else 1.0
    rng = random.Random(20261003); L += ["", "| grade | gain, points | 95% interval (paired bootstrap, 2000) | exact McNemar p |", "|---|---|---|---|"]
    for g in ("pass", "shape"):
        diff = [r["defaults"][g] - r["plain"][g] for _t, r in rows]; bs = sorted(sum(diff[rng.randrange(n)] for _ in range(n)) / n for _ in range(2000))
        L.append("| %s | %+.1f | [%.1f, %.1f] | %.2g |" % (g, 100 * sum(diff) / n, 100 * bs[50], 100 * bs[1949],
                                                   mcn(sum(x > 0 for x in diff), sum(x < 0 for x in diff))))
    U = {k: sd for k, sd, _ in LINES}
    def silent(t):   # from the REFERENCE SQL only: a silent decision the note speaks to (join type and exact match left out: near-universal)
        sd = sides(t["reference_sql"], t["instruction"])
        return any(k in sd and not (k in CUES and CUES[k].search(t["instruction"])) for k in U if k not in ("population_scope", "text_match"))
    L += ["", "| questions (BIRD grade) | n | plain | with note | note only right | plain only right |", "|---|---|---|---|---|---|"]
    for lab, keep in (("with a silent decision the note addresses (ties, counting, missing values, boundaries, calculation)", True), ("without one", False)):
        rs = [r for t, r in rows if silent(t) == keep]
        L.append("| %s | %d | %d | %d | %d | %d |" % (lab, len(rs), sum(r["plain"]["pass"] for r in rs), sum(r["defaults"]["pass"] for r in rs),
                                                   sum(r["defaults"]["pass"] and not r["plain"]["pass"] for r in rs), sum(r["plain"]["pass"] and not r["defaults"]["pass"] for r in rs)))
    L.append("\nOne run per arm: part of the changes in both directions is run-to-run variation.")
    open("%s/RESULTS_%s.md" % (OUT, re.sub(r"\W", "_", model)), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"build": lambda: build(), "run": lambda: run(*sys.argv[2:]), "report": lambda: report(sys.argv[2]), "placebo": lambda: placebo(sys.argv[2:]), "report3": lambda: report3()}[sys.argv[1]]()
