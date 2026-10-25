"""REVISION WITHOUT COLLATERAL DAMAGE (2026-10-14; gate: out/revision/GATE.md). After the model answers a BIRD question, a simulated
user revises one choice (code template). REGENERATE: the full transcript -> new SQL. EDIT: the model's SQL + the revision -> "change only
what the revision asks". Scored against the reference with that one library edit; failures split by execution.
    python -m specbridge.comm.transfer.revision run | report   -> out/revision/"""
import collections, concurrent.futures as cf, glob, json, math, os, random, sys
from specbridge.comm.common import grade as G
from specbridge.comm.transfer import disclose as X, rewrite as RW
from specbridge.report import impact as IM

OUT = "out/revision"; MODELS = ("sonnet", "gpt-6-sol"); SEED = 20261029
REGEN = """Answer the user's latest request with SQL for the database below.

DATABASE SCHEMA:
%s

CONVERSATION:
User: %s
Assistant (SQL): %s
User: %s

Answer ONLY JSON: {"sql": "your query"}"""
EDIT = """Revise the SQL below for the database below. Change only what the user's revision asks; keep everything else exactly as it is.

DATABASE SCHEMA:
%s

ORIGINAL REQUEST:
%s

CURRENT SQL:
%s

REVISION:
%s

Answer ONLY JSON: {"sql": "the revised query"}"""


def run(workers=6):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    items = [x for x in RW.bird_items() if x["rule"] != "null_filter"]; jobs = [(m, x) for x in items for m in MODELS]; random.Random(SEED).shuffle(jobs)
    def sql_of(t): return (jparse(t or "", "{") or {}).get("sql")
    def one(j):
        m, x = j; f = "%s/runs/%s/%s.json" % (OUT, m, x["id"])
        if os.path.exists(f): return
        sch = RW._schema(x["path"]); q = x["question"] + ("\nEvidence: " + x["evidence"] if x["evidence"] else "")
        g0, g1 = IM.run(x["path"], x["gold0"], 60), IM.run(x["path"], x["gold"], 60)
        if g0 is None or g1 is None: return
        t1 = ask(X.PLAIN % (sch, "", q), m, timeout=1500, quiet=True) or ""; s1 = sql_of(t1); r1 = IM.run(x["path"], s1) if s1 else None
        out = {"id": x["id"], "model": m, "rule": x["rule"], "revision": x["clarification"], "turn1": {"sql": s1, "raw": t1, "right": r1 is not None and G.bird_ex(g0, r1)}}
        arms = ["regenerate", "edit"]; random.Random(hash(j[1]["id"] + m) & 0xffff).shuffle(arms)
        for a in arms:
            p = (REGEN % (sch, q, s1 or "(no SQL)", x["clarification"])) if a == "regenerate" else (EDIT % (sch, q, s1 or "(no SQL)", x["clarification"]))
            t = ask(p, m, timeout=1500, quiet=True) or ""; s = sql_of(t); r = IM.run(x["path"], s) if s else None
            out[a] = {"sql": s, "raw": t, "runs": r is not None, "right": r is not None and G.bird_ex(g1, r), "unrevised": r is not None and G.bird_ex(g0, r)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(out, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(one, jobs))
    report()


def _mc(b, c): return 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, i) for i in range(min(b, c) + 1)) / 2 ** (b + c))


def report():
    R = [json.load(open(f)) for f in glob.glob(OUT + "/runs/*/*.json")]
    L = ["# Revision without collateral damage (gate: out/revision/GATE.md)\n", "| set | model | items | regenerate right | edit right | edit - regenerate | edit-only / regenerate-only, p |", "|---|---|---|---|---|---|---|"]
    res = {}
    for sn, sel in (("primary (turn 1 right)", lambda r: r["turn1"]["right"]), ("all", lambda r: True)):
        for mn, ms in (("sonnet", ("sonnet",)), ("gpt-6-sol", ("gpt-6-sol",)), ("pooled", MODELS)):
            rs = [r for r in R if r["model"] in ms and sel(r)]
            if not rs: continue
            a, b = sum(r["regenerate"]["right"] for r in rs), sum(r["edit"]["right"] for r in rs)
            w = sum(r["edit"]["right"] and not r["regenerate"]["right"] for r in rs); l = sum(r["regenerate"]["right"] and not r["edit"]["right"] for r in rs)
            L.append("| %s | %s | %d | %.1f%% | %.1f%% | %+.1f | %d / %d, %.3g |" % (sn, mn, len(rs), 100 * a / len(rs), 100 * b / len(rs), 100 * (b - a) / len(rs), w, l, _mc(w, l)))
            res["%s|%s" % (sn, mn)] = {"n": len(rs), "regen": a, "edit": b, "w": w, "l": l, "p": _mc(w, l)}
    P = [r for r in R if r["turn1"]["right"]]
    for a in ("regenerate", "edit"):
        L.append("\n%s on the primary set: right %d, revision not applied %d, collateral damage %d, does not run %d" % (a, sum(r[a]["right"] for r in P),
                 sum(r[a]["runs"] and not r[a]["right"] and r[a]["unrevised"] for r in P), sum(r[a]["runs"] and not r[a]["right"] and not r[a]["unrevised"] for r in P), sum(not r[a]["runs"] for r in P)))
    g = res.get("primary (turn 1 right)|pooled")
    if g: L.insert(1, "**Pilot gate** (pooled, primary set: edit - regenerate >= 5 points, p < 0.05): %+.1f points, p = %.3g -> %s\n" % (100 * (g["edit"] - g["regen"]) / g["n"], g["p"], "PASS" if (g["edit"] - g["regen"]) / g["n"] >= 0.05 and g["p"] < 0.05 else "FAIL"))
    json.dump(res, open(OUT + "/results.json", "w"), indent=1); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


EDIT_SETS = """Revise the SQL below for the database below. Change only this choice in the SQL below; keep everything else exactly as it is.

%s

ORIGINAL REQUEST:
%s

CURRENT SQL:
%s

REVISION:
%s

Answer ONLY JSON: {"sql": "the revised query"}"""
REGEN_SETS = """Answer the user's latest request with SQL for the database below.

%s

CONVERSATION:
User: %s
Assistant (SQL): %s
User: %s

Answer ONLY JSON: {"sql": "your query"}"""
SETS_MODELS = ("haiku", "sonnet", "gpt-6-sol", "gpt-6-luna")


def run_sets(n=60, workers=6):
    """GATE_sets.md: request sets, model minimal edit vs regenerate."""
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    from specbridge.comm.common import db as DB
    from specbridge.comm.transfer import ledger as LG
    fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr))
    from specbridge.comm.transfer import combined as CB                  # n sets of the first construction run, then the filter sets at the same rate
    rng = random.Random(SEED); ks = CB.part_cases(0); rng.shuffle(ks); ks = ks[:n]; start = {k: rng.choice("AB") for k in ks}
    jobs = [(m, k) for k in ks for m in SETS_MODELS]; rng.shuffle(jobs)
    r2 = random.Random(SEED + 1); ext = sorted(r2.sample(CB.part_cases(1), round(n * len(CB.part_cases(1)) / len(CB.part_cases(0)))))
    start.update({k: r2.choice("AB") for k in ext}); jobs += [(m, k) for k in ext for m in SETS_MODELS]
    def one(j):
        m, k = j; f = "%s/sets/%s/%s.json" % (OUT, m, k.replace(":", "__").replace("/", "_"))
        if os.path.exists(f): return
        c = C[k]; w = W[k]; a = start[k]; b = "B" if a == "A" else "A"; schema, docs = DB.context(c); con = DB.connect(c["snapshot"])
        ctx = "DATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s" % (schema, docs); q = w["precise_" + a]; rev = "Actually, " + w["reading_" + b]
        t1 = ask(X.PLAIN % (schema, docs, q), m, timeout=1500, quiet=True) or ""; s1 = (jparse(t1, "{") or {}).get("sql"); r1 = DB.rows(con, s1) if s1 else None
        out = {"case": k, "model": m, "start": a, "revision": rev, "turn1": {"sql": s1, "raw": t1, "right": r1 is not None and a in X._match(c, r1)}}
        arms = ["regenerate", "edit"]; random.Random(hash(k + m) & 0xffff).shuffle(arms)
        for arm in arms:
            p = (EDIT_SETS if arm == "edit" else REGEN_SETS) % (ctx, q, s1 or "(no SQL)", rev)
            t = ask(p, m, timeout=1500, quiet=True) or ""; s = (jparse(t, "{") or {}).get("sql"); r = DB.rows(con, s) if s else None; mt = X._match(c, r) if r is not None else []
            out[arm] = {"sql": s, "raw": t, "runs": r is not None, "right": b in mt, "unrevised": a in mt}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(out, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(one, jobs))
    report_sets()


def report_sets():
    R = [json.load(open(f)) for f in glob.glob(OUT + "/sets/*/*.json")]
    L = ["# Revision on request sets: model minimal edit vs regenerate (gate: out/revision/GATE_sets.md)\n",
         "| set | model | items | regenerate right | model edit right | edit - regenerate | edit-only / regenerate-only, p |", "|---|---|---|---|---|---|---|"]; res = {}
    for sn, sel in (("primary (turn 1 right)", lambda r: r["turn1"]["right"]), ("all", lambda r: True)):
        for mn, ms in [(m, (m,)) for m in SETS_MODELS] + [("pooled", SETS_MODELS)]:
            rs = [r for r in R if r["model"] in ms and sel(r)]
            if not rs: continue
            a, b = sum(r["regenerate"]["right"] for r in rs), sum(r["edit"]["right"] for r in rs)
            w = sum(r["edit"]["right"] and not r["regenerate"]["right"] for r in rs); l = sum(r["regenerate"]["right"] and not r["edit"]["right"] for r in rs)
            L.append("| %s | %s | %d | %.1f%% | %.1f%% | %+.1f | %d / %d, %.3g |" % (sn, mn, len(rs), 100 * a / len(rs), 100 * b / len(rs), 100 * (b - a) / len(rs), w, l, _mc(w, l)))
            res["%s|%s" % (sn, mn)] = {"n": len(rs), "regen": a, "edit": b, "w": w, "l": l, "p": _mc(w, l)}
    P = [r for r in R if r["turn1"]["right"]]
    for arm in ("regenerate", "edit"):
        L.append("\n%s on the primary set: right %d, revision not applied %d, collateral damage %d, does not run %d" % (arm, sum(r[arm]["right"] for r in P),
                 sum(r[arm]["runs"] and not r[arm]["right"] and r[arm]["unrevised"] for r in P), sum(r[arm]["runs"] and not r[arm]["right"] and not r[arm]["unrevised"] for r in P), sum(not r[arm]["runs"] for r in P)))
    g = res.get("primary (turn 1 right)|pooled")
    if g: L.insert(1, "**Gate** (pooled, primary set: model edit - regenerate >= 3 points, p < 0.05): %+.1f points, p = %.3g -> %s\n" % (100 * (g["edit"] - g["regen"]) / g["n"], g["p"], "PASS" if (g["edit"] - g["regen"]) / g["n"] >= 0.03 and g["p"] < 0.05 else "FAIL"))
    json.dump(res, open(OUT + "/results_sets.json", "w"), indent=1); open(OUT + "/RESULTS_sets.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "report": report, "sets": run_sets, "report_sets": report_sets}[sys.argv[1]]()
