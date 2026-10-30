"""BUILD THE DATA BEHIND EVERY EXHIBIT (model-free; reads only committed results).
    python -m specbridge.report.exhibit_data   -> out/paper/data/<exhibit>.json (+ .csv) and INDEX.md
Uncertainty: paired bootstrap over tasks/families (B = 2000, seed 20261003); Wilson intervals for single proportions;
a stratified permutation test (step depth shuffled within database, 5000 permutations) for the depth effect.
Selection rules for the worked example and the Tab. 2 example rows are written into the output with the result."""
import collections, csv, glob, json, math, os, random, re, statistics, sys
sys.path.insert(0, ".")
OUT = "out/paper/data"; os.makedirs(OUT, exist_ok=True)
B, SEED = 2000, 20261003
E12 = ["baseball_1", "sakila_1", "customers_and_invoices", "chinook_1", "financial", "student_club", "thrombosis_prediction",
       "formula_1", "archeology", "insider", "crypto", "alien"]
SOURCE = {**{d: "Spider" for d in E12[:4]}, **{d: "BIRD" for d in E12[4:8]}, **{d: "LiveSQLBench" for d in E12[8:]}}
MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
EV = "out/corpora/eval12@01cfbb1e713f"; TR = "out/transfer/eval12-v2"; INDEX = []


def wilson(k, n, z=1.96):
    if not n: return [None, None]
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def boot(units, stat, b=B, seed=SEED):
    """Percentile 95% interval of stat(sample) with units resampled with replacement (the same draw for every arm)."""
    rng = random.Random(seed); vals = []
    for _ in range(b):
        s = [units[rng.randrange(len(units))] for _ in units]; vals.append(stat(s))
    vals.sort(); return [round(vals[int(0.025 * b)], 4), round(vals[int(0.975 * b) - 1], 4)]


def save(name, obj, note, rows=None):
    json.dump(obj, open("%s/%s.json" % (OUT, name), "w"), indent=1, default=str)
    if rows:
        with open("%s/%s.csv" % (OUT, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    INDEX.append("- `%s.json`%s -- %s" % (name, " (+ .csv)" if rows else "", note))


# ---------------- Fig. 1: support vs generated -------------------------------------------------------------------------
def fig1():
    FEAT = ["agg", "baseline", "share", "rank", "row ranking", "diff", "ratio", "grouped", "multi-table"]
    per = {}
    for p in glob.glob("out/feasibility/*.json"):
        r = json.load(open(p))
        if not r.get("cells"): continue
        ops = {o for c in r["cells"].values() for o in (c.get("ops") or [])}
        A = max(int(k.split(",")[0]) for k in r["cells"]); S = max(int(k.split(",")[1]) for k in r["cells"])
        per[r["db"]] = {**{f: f in ops for f in FEAT}, "A>=2": A >= 2, "S>=5": S >= 5, "max A": A, "max S": S, "cells": len(r["cells"])}
    tried = len([p for p in glob.glob("out/feasibility/*.json") if "livesqlbench_gt" not in p])   # the LiveSQLBench testcases file is not a database
    sup = lambda dbs: {f: round(sum(per[d][f] for d in dbs) / len(dbs), 4) for f in FEAT + ["A>=2", "S>=5"]}
    pool = [json.loads(l) for d in E12 for l in open("out/coverage/eval12/%s/pool.jsonl" % d)]
    gen = {f: round(sum(f in x["operations"] for x in pool) / len(pool), 4) for f in ["baseline", "share", "rank", "row ranking", "diff", "ratio"]}
    gen["agg"] = round(sum(x["construction"].startswith("agg") for x in pool) / len(pool), 4)
    gen["grouped"] = round(sum(" within " in x["construction"] or "agg:" in x["construction"] and "(by" not in x["construction"] for x in pool) / len(pool), 4)
    gen["A>=2"] = round(sum(x["A"] >= 2 for x in pool) / len(pool), 4); gen["S>=5"] = round(sum(x["S"] >= 5 for x in pool) / len(pool), 4)
    import re
    base = lambda sql: set(re.findall(r'(?:FROM|JOIN)\s+"([^"]+)"', sql)) - set(re.findall(r'"([^"]+)"\s+AS\s+\(', sql)) - {"s%d" % i for i in range(1, 12)}
    gen["multi-table"] = round(sum(len(base(x["sql"])) >= 2 for x in pool) / len(pool), 4)      # >= 2 stored tables read
    # ON DEMAND (2026-10-04): every supported feature requested on every buildable database (coverage.py --set ondemand)
    od = {}
    for p in glob.glob("out/coverage/ondemand152v2/*/summary_ondemand.json"):
        r = json.load(open(p)); od[r["db"]] = r
    ondemand = {}
    for f in FEAT + ["A>=2", "S>=5"]:
        rows = [od[db]["features"][f] for db in od if f in od[db]["features"]]
        clean = lambda r: r.get("delivered") and r.get("use_it") == r["delivered"] and r.get("depth_ok") == r["delivered"] and r.get("receipts_clean") == r["delivered"]
        st = collections.Counter(r.get("status") for r in rows if r["requested"])
        ondemand[f] = {"databases": len(rows), "supported": sum(r["supported_by_feasibility"] for r in rows), "feasible_exact": sum(r["feasible_cells"] > 0 for r in rows),
                       "generated_on_demand": sum(bool(clean(r)) for r in rows),
                       "proven_no_data_valid_program": st.get("no data-valid program (all feasible cells exhausted)", 0),
                       "undetermined": st.get("undetermined (attempt budget)", 0),
                       "defects_among_delivered": sum((r.get("delivered") or 0) - min(r.get("use_it") or 0, r.get("depth_ok") or 0, r.get("receipts_clean") or 0) for r in rows),
                       "programs_requested": sum(r["requested"] for r in rows), "programs_delivered": sum(r.get("delivered") or 0 for r in rows),
                       "supported_not_feasible": sorted(db for db in od if od[db]["features"].get(f, {}).get("supported_by_feasibility") and not od[db]["features"][f]["feasible_cells"]),
                       "undetermined_databases": sorted(db for db in od if od[db]["features"].get(f, {}).get("status") == "undetermined (attempt budget)"),
                       "proven_none_databases": sorted(db for db in od if (od[db]["features"].get(f, {}).get("status") or "").startswith("no data-valid"))}
    mp = "out/coverage/ondemand152v2/meaning_ondemand.json"
    meaning = None
    if os.path.exists(mp):
        mj = json.load(open(mp))
        meaning = {"rubric": mj["rubric"], "programs_reviewed": mj["programs_reviewed"], "programs_passing": mj["programs_passing"], "features": mj["features"]}
    # GENERATOR ABLATION (specbridge.comm.construct.ablation, model-free): where each attempt goes, per arm
    ablation = None
    if glob.glob("out/ablation/full/*.json"):
        from specbridge.comm.construct.ablation import ARMS
        ablation = {}
        for arm in ARMS:
            R = [json.load(open(f)) for f in sorted(glob.glob("out/ablation/%s/*.json" % arm))]
            c = collections.Counter(); att = sum(r["attempts"] for r in R)
            for r in R:
                c["not drawn"] += r["attempts"] - r["drawn"]
                for x in r["rows"]:
                    k = ("invalid" if not x["valid"] else "off target depth" if not x["on_target"] else "duplicate" if x["duplicate"] else
                         "good, not sound" if not x["profile_sound"] else "good and sound")
                    c[k] += 1
            ablation[arm] = {"attempts": att, "databases": len(R), "outcomes": dict(c), "budget_hit": [r["db"] for r in R if r.get("time_budget_hit")]}
    save("fig1_coverage", {"features": FEAT + ["A>=2", "S>=5"], "ondemand": ondemand, "meaning": meaning, "ablation": ablation, "ondemand_databases": len(od), "support_eval12": sup(E12), "support_all_buildable": sup(sorted(per)),
         "generated_pool_eval12": gen, "n_buildable": len(per), "n_tried": tried, "n_pool": len(pool), "per_database": per,
         "note": "support = fraction of databases where SOME program uses the feature (feasibility probes passing the data checks); "
                 "generated = fraction of pool programs (uniform over each database's supported cells, no preferences). "
                 "'grouped' generated is approximated from the construction text, 'multi-table' generated = the SQL reads >= 2 stored tables; support is exact."},
         "radar data: support (12 / all buildable) vs generated", [{"db": d, **v} for d, v in sorted(per.items())])


# ---------------- Tab. 1: construction and control --------------------------------------------------------------------
def tab1():
    S = {d: json.load(open("out/coverage/eval12/%s/summary.json" % d)) for d in E12}
    SR = {d: json.load(open("out/coverage/eval12/%s/summary_require.json" % d)) for d in E12}
    P = lambda d, c: [json.loads(l) for l in open("out/coverage/eval12/%s/%s.jsonl" % (d, c))]
    rows = []
    for d in E12:
        X = P(d, "pool"); c = S[d]["configs"]["pool"]
        rows.append({"database": d, "source": SOURCE[d], "requested": c["requested"], "delivered": c["delivered"],
                     "short_cells": sum(v["delivered"] < v["requested"] for v in c["cells"].values()),
                     "built_for_eq_measured": sum(x.get("built_for") == "%d,%d" % (x["A"], x["S"]) for x in X),
                     "recomputed": sum(x["receipts"]["recomputed"] > 0 for x in X), "trivial": sum(x["receipts"]["trivial"] > 0 for x in X),
                     "distinct_sql": len({x["sql"] for x in X}), "constructions": len({x["construction"] for x in X}),
                     "base_quantities": len({q for x in X for q in x["quantities"]}), "seconds": round(c["seconds"] + S[d]["setup_seconds"], 1), "model_calls": 0})
    ctrl = []
    for d in E12:
        for nm in ("shallow", "balanced", "deep"):
            per_seed = []
            for s in (1, 2, 3):
                X = P(d, "%s_s%d" % (nm, s))
                per_seed.append({"n": len(X), "S3-4": sum(x["S"] <= 4 for x in X) / max(1, len(X)), "S5-7": sum(x["S"] >= 5 for x in X) / max(1, len(X))})
            ctrl.append({"database": d, "request": nm, "delivered_mean": round(statistics.mean(x["n"] for x in per_seed), 1),
                         "share_S3_4_min": round(min(x["S3-4"] for x in per_seed), 3), "share_S3_4_max": round(max(x["S3-4"] for x in per_seed), 3),
                         "share_S5_7_min": round(min(x["S5-7"] for x in per_seed), 3), "share_S5_7_max": round(max(x["S5-7"] for x in per_seed), 3)})
    pref = []
    for d in E12:
        def frac(cfg, op):
            X = P(d, cfg); return round(sum(op in x["operations"] for x in X) / max(1, len(X)), 3)
        pref.append({"database": d, "rank_w1": frac("balanced_s1", "rank"), "rank_w3": frac("ops_rank=3", "rank"), "rank_w10": frac("ops_rank=10", "rank"),
                     "share_w1": frac("balanced_s1", "share"), "share_w10": frac("ops_share=10", "share"),
                     "baseline_w1": frac("balanced_s1", "baseline"), "baseline_w0.1": frac("ops_baseline=0.1", "baseline")})
    from specbridge.comm.construct.pool import ops_of
    req = []
    for d in E12:
        for cname, c in SR[d]["configs"].items():
            X = P(d, cname); need = c["request"]["require"]
            req.append({"database": d, "required": "+".join(need), "delivered": len(X), "all_use_them": sum(all(n in ops_of(x["construction"]) for n in need) for x in X),
                        "built_for_eq_measured": sum(x.get("built_for") == "%d,%d" % (x["A"], x["S"]) for x in X),
                        "cells_not_constructible": ";".join(sorted(k for k, v in c["cells"].items() if (v.get("shortfall") or "").startswith("not constructible with")))})
    rep = json.load(open(EV + "/report.json"))
    save("tab1_construction", {"pool": rows, "control": ctrl, "preferences": pref, "required": req,
         "reviewed_build": {k: rep.get(k) for k in ("delivered", "requested_cells", "delivered_cells", "shortfall", "seconds", "model_calls", "funnel", "operations", "diversity")}},
         "construction and control tables (pool per database, depth control min-max over seeds, preferences, required operations, reviewed build)", rows)
    for nm, rr in (("tab1_control", ctrl), ("tab1_preferences", pref), ("tab1_required", req)):
        with open("%s/%s.csv" % (OUT, nm), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rr[0])); w.writeheader(); w.writerows(rr)


# ---------------- Fig. 2: explicit vs precise ---------------------------------------------------------------------------
def fig2():
    T = {json.loads(l)["id"]: json.loads(l) for l in open(EV + "/corpus.v2.jsonl")}
    ch = {json.loads(l)["id"] for l in open(EV + "-v2-changed/corpus.jsonl")}
    R = {}
    for m in MODELS:
        o = json.load(open("%s/solver_%s.json" % (EV, m)))["results"]; c = json.load(open("%s-v2-changed/solver_%s.json" % (EV, m)))["results"]
        R[m] = {i: (o["%s|explicit" % i]["correct"], (c if i in ch else o)["%s|natural" % i]["correct"]) for i in T}
    ids = sorted(T); out = {"n_tasks": len(ids), "overall": {}, "per_database": {}, "depth": {}, "depth_test": {}}
    for m in MODELS:
        e = [R[m][i][0] for i in ids]; n = [R[m][i][1] for i in ids]
        out["overall"][m] = {"explicit": [sum(e), len(e)], "precise_v2": [sum(n), len(n)],
                             "explicit_ci": boot(ids, lambda s, m=m: sum(R[m][i][0] for i in s) / len(s)),
                             "precise_ci": boot(ids, lambda s, m=m: sum(R[m][i][1] for i in s) / len(s)),
                             "diff_precise_minus_explicit_ci": boot(ids, lambda s, m=m: sum(R[m][i][1] - R[m][i][0] for i in s) / len(s))}
        out["per_database"][m] = {d: {"explicit": [sum(R[m][i][0] for i in ids if T[i]["database"] == d), sum(T[i]["database"] == d for i in ids)],
                                      "precise_v2": [sum(R[m][i][1] for i in ids if T[i]["database"] == d), sum(T[i]["database"] == d for i in ids)]} for d in E12}
        out["depth"][m] = {"S%d" % s: {"explicit_errors": [sum(1 - R[m][i][0] for i in ids if T[i]["S"] == s), sum(T[i]["S"] == s for i in ids)],
                                       "explicit_error_wilson": wilson(sum(1 - R[m][i][0] for i in ids if T[i]["S"] == s), sum(T[i]["S"] == s for i in ids)),
                                       "precise_errors": [sum(1 - R[m][i][1] for i in ids if T[i]["S"] == s), sum(T[i]["S"] == s for i in ids)]} for s in (3, 4, 5, 6)}
    # depth effect controlled for database: shuffle S within database, statistic = sum over tasks of (S - mean S in db) * error
    rng = random.Random(SEED)
    for arm, idx in (("explicit", 0), ("precise_v2", 1)):
        for m in MODELS + ["pooled"]:
            ms = MODELS if m == "pooled" else [m]
            by = collections.defaultdict(list)
            for i in ids: by[T[i]["database"]].append(i)
            Sv = {i: T[i]["S"] for i in ids}
            def stat(Smap):
                tot = 0.0
                for d, xs in by.items():
                    mu = statistics.mean(Smap[i] for i in xs)
                    for i in xs: tot += (Smap[i] - mu) * sum(1 - R[mm][i][idx] for mm in ms)
                return tot
            obs = stat(Sv); ge = 0; P = 5000
            for _ in range(P):
                Sp = {}
                for d, xs in by.items():
                    vals = [Sv[i] for i in xs]; rng.shuffle(vals); Sp.update(zip(xs, vals))
                ge += stat(Sp) >= obs
            out["depth_test"]["%s/%s" % (arm, m)] = {"statistic": round(obs, 3), "p_one_sided": round((ge + 1) / (P + 1), 4), "permutations": P}
    save("fig2_explicit_vs_precise", out, "explicit vs precise v2: overall with paired bootstrap, per database, depth (Wilson), within-database permutation test for step depth")


# ---------------- Fig. 3: real benchmarks -------------------------------------------------------------------------------
def fig3():
    from specbridge.comm.common import grade as G
    out = {"confirmation": {}, "causes": {}}
    for split in ("bird_heldout100", "spider_confirm50"):
        d = "out/confirmation/" + split
        O = {t["id"]: t for t in map(json.loads, open(d + "/tasks_original.jsonl"))}; E = sorted({t["id"] for t in map(json.loads, open(d + "/tasks_explicit.jsonl"))})
        out["confirmation"][split] = {"n": len(E)}
        for m in MODELS:
            r = {}
            for i in E:
                g = {}
                for arm in ("original", "explicit"):
                    f = "%s/runs/%s/%s_rep0/%s.json" % (d, m.replace("-", "_"), arm, i); o = json.load(open(f)) if os.path.exists(f) else {}
                    a = o.get("answer"); g[arm] = (bool(o.get("pass")), bool(a is not None and G.shape_tolerant(O[i]["reference_answer"], a)))
                r[i] = g
            k = lambda arm, j: sum(r[i][arm][j] for i in E)
            out["confirmation"][split][m] = {"original_strict": [k("original", 0), len(E)], "original_shape": [k("original", 1), len(E)], "explicit_strict": [k("explicit", 0), len(E)],
                "original_strict_ci": boot(E, lambda s: sum(r[i]["original"][0] for i in s) / len(s)), "original_shape_ci": boot(E, lambda s: sum(r[i]["original"][1] for i in s) / len(s)),
                "explicit_ci": boot(E, lambda s: sum(r[i]["explicit"][0] for i in s) / len(s)),
                "gap_strict_ci": boot(E, lambda s: sum(r[i]["explicit"][0] - r[i]["original"][0] for i in s) / len(s)),
                "gap_shape_ci": boot(E, lambda s: sum(r[i]["explicit"][0] - r[i]["original"][1] for i in s) / len(s)),
                "explicit_only": sum(r[i]["explicit"][0] and not r[i]["original"][0] for i in E), "original_only": sum(r[i]["original"][0] and not r[i]["explicit"][0] for i in E)}
        out["causes"]["confirmation/" + split] = dict(collections.Counter(g.get("cause") for g in json.load(open(d + "/inspection.json"))))
    dev = collections.Counter()
    for b in ["batch%d" % i for i in range(3, 9)]: dev.update(g.get("cause") for g in json.load(open("out/comm_library/%s/inspection.json" % b)))
    out["causes"]["development/BIRD batches 3-8"] = dict(dev)
    out["causes"]["development/Spider"] = dict(collections.Counter(g.get("cause") for g in json.load(open("out/comm_library/spider_dev/inspection.json"))))
    out["note"] = "confirmation: one run per solver (run variation cannot be labelled); development: haiku, 2 runs (BIRD 8 questions per call, Spider 1)"
    save("fig3_real_benchmarks", out, "confirmation per solver (strict, shape-tolerant, explicit) with paired bootstrap; cause composition dev vs confirmation")


# ---------------- Tab. 2: library ---------------------------------------------------------------------------------------
def tab2():
    E = [json.loads(l) for l in open("library/examples.jsonl")]; Dx = [json.loads(l) for l in open("library/defects.jsonl")]
    rule = ("per type: the first RAISE example (status unresolved/contested) from a two-reading record with gate confidence high, "
            "else medium; ties broken by benchmark (BIRD before Spider) then batch:task order. Reference defects: the first 3 by "
            "batch:task order.")
    conf = {"high": 0, "medium": 1, "low": 2}; rows = []
    for t in sorted({e["type"] for e in E}):
        xs = [e for e in E if e["type"] == t]
        rec = [e for e in xs if e["raise"] and "two-reading" in str(e.get("provenance", {}).get("from"))]
        rec.sort(key=lambda e: (conf.get(((e.get("review") or {}).get("gate") or {}).get("confidence"), 3), e["source"]["benchmark"] != "BIRD dev", "%s:%s" % (e["source"]["batch"], e["source"]["task"])))
        ex = rec[0] if rec else None
        rows.append({"type": t, "raise": sum(e["raise"] for e in xs), "stay_silent": sum(not e["raise"] for e in xs),
                     "from_records": sum("record" in str(e.get("provenance", {}).get("from")) for e in xs), "from_solved_questions": sum("decision site" in str(e.get("provenance", {}).get("from")) for e in xs),
                     "settled_from_failures": sum(not e["raise"] and "decision site" not in str(e.get("provenance", {}).get("from")) for e in xs),
                     "answered_right": sum(not e["raise"] and "decision site" in str(e.get("provenance", {}).get("from")) for e in xs),
                     "example_source": ("%s %s:%s" % (ex["source"]["benchmark"], ex["source"]["batch"], ex["source"]["task"])) if ex else "",
                     "example_question": (ex or {}).get("question", ""), "example_decision": (ex or {}).get("decision", ""),
                     "example_readings": json.dumps([{"id": r.get("id"), "reading": r.get("reading")} for r in (ex or {}).get("readings", [])]),
                     "example_status": (ex or {}).get("status", ""), "example_gate": ((ex or {}).get("review") or {}).get("gate")})
    # value representation is split by its SQL edit (2026-10-17): an edit that changes only comparison strictness (> vs >=, < vs <=,
    # strict bounds vs BETWEEN) is a strict cutoff; any other edit (=, IN, LIKE, case, spelling, a cast) is value matching
    def _strict_only(a, b):
        n = lambda q: re.sub(r"\s+", " ", re.sub(r"(\S+) BETWEEN (\S+) AND (\S+)", r"\1 > \2 AND \1 < \3", q, flags=re.I)).replace(">=", ">").replace("<=", "<").strip().rstrip(";")
        return a != b and n(a) == n(b)
    split = {"strict_cutoff": {"raise": 0, "settled": 0}, "value_matching": {"raise": 0, "settled": 0}}
    for e in E:
        if e["type"] != "value_representation" or "decision site" in str(e.get("provenance", {}).get("from")): continue
        R = {r.get("id"): r.get("sql", "") for r in e.get("readings", [])}
        k = "strict_cutoff" if R.get("A") and R.get("B") and _strict_only(R["A"], R["B"]) else "value_matching"
        split[k]["raise" if e["raise"] else "settled"] += 1
    defects = sorted(Dx, key=lambda d: str(d.get("source")))[:3]
    mean = [e for e in E if e["type"] != "output_form" and "decision site" not in str(e.get("provenance", {}).get("from"))]
    table1 = {"types": len({e["type"] for e in mean}), "open": sum(e["raise"] for e in mean), "settled": sum(not e["raise"] for e in mean)}
    save("tab2_library", {"rule": rule, "types": rows, "value_split": split, "table1_meaning_from_failures": table1, "reference_defects_examples": defects, "n_examples": len(E), "n_defects": len(Dx)},
         "decision types with counts and one rule-selected example each; reference-defect examples", rows)


# ---------------- Fig. 4 / Tab. 3: families -----------------------------------------------------------------------------
def fam():
    from specbridge.comm.diagnose.library import example_for
    from specbridge.comm.transfer.render import libkind
    S = json.load(open(TR + "/render/selection.json")); C = {c["case"]: c for c in json.load(open(TR + "/render/eval/frozen.json"))["cases"]}
    RV = json.load(open(TR + "/render/review.json")); R0 = json.load(open(TR + "/render/review_round0.json")); W = json.load(open(TR + "/render/written.json"))
    ret = {}
    for k, p in S.items():
        a = example_for(libkind(p["kind"])); b = example_for(libkind(p["kind"]))
        ret[k] = {"kind": p["kind"], "type": p.get("type"), "retrieved": a[1], "deterministic": a == b}
    rule = ("worked example: frozen family of type aggregation_level, open label 'mutually recognized open', survived on the first "
            "pass (round 0, status survives), with a retrieved library example; among these the one with the smallest sha1(case id).")
    import hashlib
    cand = [k for k, c in C.items() if c["type"] == "aggregation_level" and c["label"] == "mutually recognized open"
            and R0.get(k, {}).get("status") == "survives" and ret[k]["retrieved"]]
    pick = min(cand, key=lambda k: hashlib.sha1(k.encode()).hexdigest()) if cand else None
    work = None
    if pick:
        c = C[pick]; p = S[pick]; w = W[pick]
        work = {"case": pick, "database": c["database"], "A": c["A_depth"], "S": c["S_depth"], "sql_A": c["sql_A"], "sql_B": c["sql_B"], "decision": p["decision"],
                "reading_A": p["reading_A"], "reading_B": p["reading_B"], "edits": p.get("edits"), "witness": p.get("witness"), "retrieved_example": ret[pick]["retrieved"],
                "plan_shared": w.get("shared"), "choice_A": w.get("choice_A"), "choice_B": w.get("choice_B"), "precise_A": w["precise_A"], "precise_B": w["precise_B"],
                "open": w["open"], "favouring_phrases": w.get("favouring_phrases"), "review": {k2: RV[pick][k2] for k2 in ("label", "precise_selective", "fidelity_ok", "status", "reasons")}}
    save("fig4_worked_example", {"rule": rule, "candidates": len(cand), "example": work}, "worked synthetic-generation example (rule-selected)")
    from specbridge.comm.diagnose import library as LIB
    M = LIB.meaning()
    summary = {"retrieval_collection": "out/comm_library/meaning_retrieval.jsonl (gate high + meaning choice)", "records_in_collection": len(M),
               "records_by_choice_tag": dict(collections.Counter((r.get("tags") or {}).get("choice") for r in M)),
               "query": "example_for(libkind(kind)) -> retrieve({'choice': tag}): choice tag only (no structure or semantics features), so every family of a type gets the same top record",
               "families_with_example": sum(bool(x["retrieved"]) for x in ret.values()), "families": len(ret),
               "distinct_records_shown": len({x["retrieved"] for x in ret.values() if x["retrieved"]}),
               "by_type": {"%s -> %s" % k: n for k, n in collections.Counter((x["type"], x["retrieved"]) for x in ret.values()).items()},
               "consequence": "the ablation tests ONE fixed high-confidence example per decision type (none for counting_unit and novel kinds), not tailored retrieval"}
    save("families_retrieved_examples", {"summary": summary, "per_family": ret}, "which library example each selected family's writer was shown (recomputed; deterministic) and what retrieval actually was")
    # Tab. 3: funnel, distribution, ablation with paired tests
    pairs = json.load(open(TR + "/compare/pairs60.json"))
    def cond(d):
        rv = json.load(open(d + "/review.json")); r0p = d + "/review_round0.json"; r0 = json.load(open(r0p)) if os.path.exists(r0p) else rv
        f = lambda r: {"open_both": r["label"] == "mutually recognized open", "selective": bool(r["precise_selective"]), "fidelity": bool(r["fidelity_ok"]), "pass": r["status"] == "survives"}
        return {k: {"first": f(r0[k]) if k in r0 else None, "final": f(rv[k]) if k in rv else None} for k in pairs}
    A = {"full": cond(TR + "/render"), "noex": cond(TR + "/compare/noex"), "direct": cond(TR + "/compare/direct")}
    abl = {}
    for metric in ("open_both", "selective", "fidelity", "pass"):
        for stage in ("first", "final"):
            v = {c: {k: bool((A[c][k][stage] or {}).get(metric)) for k in pairs} for c in A}
            row = {c: sum(v[c].values()) for c in A}
            for a, b in (("noex", "full"), ("direct", "noex"), ("full", "direct")):
                bc = sum(v[a][k] and not v[b][k] for k in pairs); cb = sum(v[b][k] and not v[a][k] for k in pairs)
                from math import comb
                n = bc + cb; p = min(1.0, 2 * sum(comb(n, i) for i in range(0, min(bc, cb) + 1)) / 2 ** n) if n else 1.0
                row["%s_vs_%s" % (a, b)] = {"only_first": bc, "only_second": cb, "mcnemar_exact_p": round(p, 4),
                                             "diff_ci": boot(pairs, lambda s: (sum(v[a][k] for k in s) - sum(v[b][k] for k in s)) / len(s))}
            abl["%s/%s" % (metric, stage)] = row
    funnel = {"tasks": 382, "inventory": open(TR + "/cp/INVENTORY.md").read().strip().splitlines()[-1], "selected": len(S),
              "selected_types": dict(collections.Counter(p.get("type") for p in S.values())), "frozen": len(C),
              "frozen_types": dict(collections.Counter(c["type"] for c in C.values())), "frozen_databases": dict(collections.Counter(c["database"] for c in C.values())),
              "frozen_labels": dict(collections.Counter(c["label"] for c in C.values())), "intended": dict(collections.Counter(c["intended"] for c in C.values()))}
    save("tab3_generation", {"funnel": funnel, "ablation_60_pairs": abl, "pairs": pairs}, "family funnel, distributions, ablation with exact McNemar and paired bootstrap")


# ---------------- Fig. 5 / Tab. 4: disclosure ---------------------------------------------------------------------------
def disclosure():
    from specbridge.comm.transfer.evaluate import matches
    from specbridge.comm.transfer import combined as CB                   # every request set of both construction runs
    R = CB.D; C = {c["case"]: c for c in json.load(open(R + "/eval/frozen.json"))["cases"]}; J = json.load(open(R + "/disclose/judge.json"))
    JA = json.load(open(R + "/disclose/judge_alternatives.json")); oth = lambda x: "B" if x == "A" else "A"
    from specbridge.comm.transfer import reviewed as RV
    ks = RV.accepted(sorted(C)); out = {"n_families": len(ks), "n_constructed": len(C), "models": {}}
    def load(p):
        o = {}
        for f in os.listdir(p):
            x = json.load(open(os.path.join(p, f))); o[(x["case"], x["wording"])] = x
        return o
    for m in MODELS:
        d = R + "/eval/runs/" + m.replace("-", "_") + "_b1"; pr = {}
        for f in os.listdir(d):
            o = json.load(open(os.path.join(d, f))); k, v = o["key"].rsplit("|", 1); pr[(k, v)] = matches(C[k], o["answer"]) if o.get("answer") is not None else []
        both = {k for k in ks if C[k]["intended"] in pr[(k, "precise")] and oth(C[k]["intended"]) in pr[(k, "precise_other")]}
        D = load(R + "/disclose/" + m); P = load(R + "/disclose/plain/" + m)
        D = {x: v for x, v in D.items() if x[0] in ks}; P = {x: v for x, v in P.items() if x[0] in ks}   # the reviewed population only
        prec = {k: w for (k, w) in D if w != "open"}
        f = {k: {"precise_correct": prec[k][-1] in D[(k, prec[k])]["primary_matches"],
                 "open_admissible": bool(D[(k, "open")]["primary_matches"]),
                 "recognises": (J.get("%s|open|%s" % (k, m)) or {}).get("flags_decision") is True,
                 "states": (J.get("%s|open|%s" % (k, m)) or {}).get("faithful") in ("yes", "no"),
                 "states_faithful": (J.get("%s|open|%s" % (k, m)) or {}).get("faithful") == "yes",
                 "covers_both": {"A", "B"} <= set(D[(k, "open")]["primary_matches"]) | {x for a in D[(k, "open")]["alternatives"] for x in a["matches"]},
                 "false_open": (J.get("%s|%s|%s" % (k, prec[k], m)) or {}).get("claims_open_wrongly") is True,
                 # 2026-10-30: the other false alarm, by execution: an alternative on a specific request returns the other interpretation;
                 # an alternative that returns neither reference is on a choice the set does not test (counted, not a false alarm)
                 "false_other": any(oth(prec[k][-1]) in a["matches"] for a in D[(k, prec[k])]["alternatives"]),
                 "alt_other_choice": any(a["executes"] and not a["matches"] for a in D[(k, prec[k])]["alternatives"]),
                 "both_precise_plain": k in both,
                 "plain_precise_correct": prec[k][-1] in P[(k, prec[k])]["primary_matches"], "plain_open_admissible": bool(P[(k, "open")]["primary_matches"])} for k in ks}
        res = {}
        for key in ("precise_correct", "open_admissible", "recognises", "states", "states_faithful", "covers_both", "false_open", "false_other", "alt_other_choice"):
            res[key] = {"k": sum(f[k][key] for k in ks), "n": len(ks), "ci": boot(ks, lambda s, key=key: sum(f[k][key] for k in s) / len(s))}
        mutual = {k for k in ks if C[k].get("label") == "mutually recognized open"}
        dec = lambda S_: {"not_covered": sum(not f[k]["covers_both"] for k in S_), "both_specific_right": sum((not f[k]["covers_both"]) and f[k]["both_precise_plain"] for k in S_), "n": len(S_)}
        res["decomposition"] = {"exploration": {"all": dec(ks), "mutual": dec([k for k in ks if k in mutual])}}
        mf = R + "/disclose/complement/results.json"
        if os.path.exists(mf):
            mr = json.load(open(mf)).get(m) or {}
            if mr.get("all", {}).get("n") == len(ks):     # matched single-call: only when every family is complete (matched.report, same population)
                res["decomposition"]["matched"] = {"all": mr["all"], "mutual": mr["both reviewers accept the open request"]}
        cond = [k for k in ks if f[k]["both_precise_plain"]]
        res["covers_both_given_both_precise"] = {"k": sum(f[k]["covers_both"] for k in cond), "n": len(cond), "ci": boot(cond, lambda s: sum(f[k]["covers_both"] for k in s) / len(s)) if cond else None}
        # BREAKDOWN (2026-10-15): both readings returned among sets with both specific requests right, by choice type and by source
        SRC = {"sakila_1": "Spider", "baseball_1": "Spider", "chinook_1": "Spider", "customers_and_invoices": "Spider", "financial": "BIRD",
               "formula_1": "BIRD", "student_club": "BIRD", "thrombosis_prediction": "BIRD"}
        MAIN = ("aggregation_level", "tie", "missing_values", "counting_unit", "calculation", "relationship_role", "value_representation")
        grp = {"type": lambda k: C[k]["type"] if C[k]["type"] in MAIN else "other", "source": lambda k: SRC.get(C[k]["database"], "LiveSQLBench")}
        res["by_group"] = {g: {v: {"k": sum(f[k]["covers_both"] for k in cond if fn(k) == v), "n": sum(1 for k in cond if fn(k) == v),
                                   "sets": sum(1 for k in ks if fn(k) == v)} for v in sorted({fn(k) for k in ks})} for g, fn in grp.items()}
        st = [k for k in ks if f[k]["states"]]
        res["faithful_given_stated"] = {"k": sum(f[k]["states_faithful"] for k in st), "n": len(st), "wilson": wilson(sum(f[k]["states_faithful"] for k in st), len(st))}
        alts = [(i, a) for (k, w), o in D.items() for i, a in [("%s|%s|%s|%d" % (k, w, m, j), a) for j, a in enumerate(o["alternatives"])]]
        res["alternatives"] = {"offered": len(alts), "supported_judge": sum((JA.get(i) or {}).get("verdict") == "supported" for i, _a in alts),
                               "judged": sum(i in JA for i, _a in alts), "returns_recorded_reading": sum(bool(a["matches"]) for _i, a in alts)}
        res["overhead"] = {"precise_plain_single": sum(f[k]["plain_precise_correct"] for k in ks), "precise_disclosure": res["precise_correct"]["k"],
                           "precise_diff_ci": boot(ks, lambda s: sum(f[k]["precise_correct"] - f[k]["plain_precise_correct"] for k in s) / len(s)),
                           "open_plain_single": sum(f[k]["plain_open_admissible"] for k in ks), "open_disclosure": res["open_admissible"]["k"],
                           "median_seconds_plain": statistics.median(x["seconds"] for x in P.values()), "median_seconds_disclosure": statistics.median(x["seconds"] for x in D.values()),
                           "median_chars_plain": statistics.median(x["chars_out"] for x in P.values()), "median_chars_disclosure": statistics.median(x["chars_out"] for x in D.values()),
                           "mean_answer_set": round(statistics.mean(1 + len(x["alternatives"]) for x in D.values()), 3), "tokens": "NOT MEASURED"}
        out["models"][m] = res
    save("fig5_tab4_disclosure", out, "disclosure: every dimension per model with bootstrap over families; conditional coverage; alternative validity; matched overhead")


# ---------------- Fig. 6: inclination of the reference SQL ---------------------------------------------------------------
USUAL = {"ties_and_selection": ("A", "one row for an extreme (LIMIT 1), not every tied row"), "counting_unit": ("B", "COUNT rows over a join, not DISTINCT entities"),
         "population_scope": ("A", "inner join, not outer"), "missing_values": ("B", "no IS NOT NULL filter before sorting for an extreme"),
         "calculation_scale": ("A", "percentage times 100, not a fraction"), "calculation_division": ("A", "division made REAL explicitly (CAST or 1.0)"),
         "boundary_between": ("B", "'between' read as inclusive"), "boundary_open": ("A", "'after', 'before', 'over', 'under' ... read as strict"),
         "text_match": ("A", "a named value matched exactly (=), not loosely (LIKE)")}
FIG6_KINDS = ["ties_and_selection", "counting_unit", "missing_values", "population_scope", "boundary_between", "boundary_open", "text_match"]
TAB6_KINDS = FIG6_KINDS + ["calculation_scale", "calculation_division"]                       # + BIRD-only calculation (table, not figure)
LIB_TYPE = {"ties_and_selection": "ties_and_selection", "counting_unit": "counting_unit", "missing_values": "missing_values",
            "population_scope": "population_scope", "calculation_scale": "calculation", "calculation_division": "calculation",
            "boundary_between": "time_scope", "boundary_open": "time_scope", "text_match": "value_representation"}


NOTE_MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]   # a solver enters when all 600 are answered in both arms


def note_experiment(model="sonnet"):
    """Fig. 6c: the same solver on BIRD dev questions in their original wording, with vs without the fixed note of BIRD-train
    defaults (specbridge.comm.diagnose.prior). Subsets are decided from the REFERENCE SQL only."""
    from math import comb
    from specbridge.comm.diagnose import prior as P
    from specbridge.comm.diagnose.inclination import sides, CUES
    U = [k for k, _s, _t in P.LINES if k not in ("population_scope", "text_match")]
    T = [json.loads(l) for l in open(P.OUT + "/tasks.jsonl")]; base = "%s/runs/%s" % (P.OUT, re.sub(r"\W", "_", model)); R = []
    for t in T:
        f = ["%s/%s/%s.json" % (base, arm, t["id"]) for arm in ("plain", "defaults")]
        if all(os.path.exists(x) for x in f):
            sd = sides(t["reference_sql"], t["instruction"])
            R.append((any(k in sd and not (k in CUES and CUES[k].search(t["instruction"])) for k in U), [json.load(open(x)) for x in f], t["database"]))
    mcn = lambda u, d: min(1.0, 2 * sum(comb(u + d, i) for i in range(min(u, d) + 1)) / 2 ** (u + d)) if u + d else 1.0
    if len(R) < len(T): return None   # a solver enters only when both arms of every question are answered
    out = {"model": model, "subsets": {}}
    from specbridge.comm.diagnose.tasks import BIRD_DBS        # the 5 databases of the error analysis; CLEAN = the other 6
    TH = "thrombosis_prediction"
    SUBS = (("all", lambda sil, db: True), ("with a silent decision", lambda sil, db: sil), ("without one", lambda sil, db: not sil),
            ("clean", lambda sil, db: db not in BIRD_DBS), ("clean, silent decision", lambda sil, db: db not in BIRD_DBS and sil),
            ("clean, none detected", lambda sil, db: db not in BIRD_DBS and not sil), ("overlap", lambda sil, db: db in BIRD_DBS),
            ("overlap without thrombosis", lambda sil, db: db in BIRD_DBS and db != TH), ("thrombosis", lambda sil, db: db == TH))
    for lab, keep in SUBS:
        rs = [r for sil, r, db in R if keep(sil, db)]; n = len(rs); S = out["subsets"][lab] = {"n": n}
        for g in ("pass", "shape"):
            p_, d_ = sum(r[0][g] for r in rs), sum(r[1][g] for r in rs); up = sum(r[1][g] and not r[0][g] for r in rs); dn = sum(r[0][g] and not r[1][g] for r in rs)
            S[g] = {"plain": p_, "note": d_, "plain_wilson": wilson(p_, n), "note_wilson": wilson(d_, n), "up": up, "down": dn, "mcnemar_p": mcn(up, dn),
                    "diff_ci": boot(list(range(n)), lambda ix: sum(rs[i][1][g] - rs[i][0][g] for i in ix) / len(ix))}
    return out


def inclination():
    """Output form (sorted value returned, duplicate rows kept) is excluded: grading ignores it and the library calls it output form."""
    from specbridge.comm.diagnose import inclination as I
    G = I.measure_groups({k: USUAL[k][0] for k in TAB6_KINDS})
    for k in TAB6_KINDS:   # the usual reading must be the majority of BIRD and Spider's own references, pooled (silent questions)
        a = sum(G[g]["kinds"][k]["n_A"] for g in ("BIRD train", "BIRD dev", "Spider train (own)", "Spider dev"))
        b = sum(G[g]["kinds"][k]["n_B"] for g in ("BIRD train", "BIRD dev", "Spider train (own)", "Spider dev"))
        assert (a >= b) == (USUAL[k][0] == "A"), (k, a, b)
    out = {"usual": {k: USUAL[k][1] for k in TAB6_KINDS}, "figure_kinds": FIG6_KINDS, "library_types": {k: LIB_TYPE[k] for k in TAB6_KINDS},
           "min_per_db": I.MIN_PER_DB, "groups": {}, "library_open": {}}; rows = []
    for g, r in G.items():
        pq = r["per_question"]
        S = out["groups"][g] = {"questions": r["questions"], "databases": r["databases"], "kinds": {},
                                "silent_questions": {"n": pq.get("with_silent", 0), "against_usual": pq.get("against_usual", 0),
                                                     "wilson": wilson(pq.get("against_usual", 0), pq.get("with_silent", 0))}}
        for kind in TAB6_KINDS:
            v = r["kinds"][kind]; u = USUAL[kind][0]; k, n = v["n_" + u], v["n_A"] + v["n_B"]
            share = {db: round(c[0 if u == "A" else 1] / sum(c), 4) for db, c in v["per_db"].items() if sum(c) >= I.MIN_PER_DB}
            S["kinds"][kind] = {"k": k, "n": n, "wilson": wilson(k, n), "cued": {"A": v["cued_A"], "B": v["cued_B"]}, "db_share": share,
                                "db_usual_majority": sum(x > 0.5 for x in share.values()), "db_n": len(share)}
            rows.append({"group": g, "decision": kind, "usual": USUAL[kind][1], "k": k, "n": n, "databases_usual_majority": S["kinds"][kind]["db_usual_majority"], "databases": len(share)})
    # library: open records (raise) that the gate calls a MEANING choice, high or medium confidence, placed by the same code
    lib = [json.loads(l) for l in open("library/examples.jsonl")]
    for x in lib:
        gate = (x.get("review") or {}).get("gate") or {}
        if not x["raise"] or gate.get("category") != "meaning choice" or gate.get("confidence") not in ("high", "medium"): continue
        sd = I.sides(x["gold_sql"], x["question"]); b = x["source"]["benchmark"].split()[0]
        for kind in TAB6_KINDS:
            if LIB_TYPE[kind] == x["type"] and kind in sd:
                c = out["library_open"].setdefault(b, {}).setdefault(gate["confidence"], {"follows": 0, "against": 0})
                c["follows" if sd[kind] == USUAL[kind][0] else "against"] += 1
                break
    for b, byc in out["library_open"].items():
        f = sum(c["follows"] for c in byc.values()); n = f + sum(c["against"] for c in byc.values())
        byc["high+medium"] = {"follows": f, "against": n - f, "wilson": wilson(f, n)}
    out["note"] = ("side read from the reference SQL alone (sqlglot, no model); only SILENT questions (no wording cue for the decision, "
                   "specbridge.comm.diagnose.inclination.CUES); meaning decisions only (output form excluded); usual = the side most BIRD and "
                   "Spider-own references take; groups = who wrote the SQL (Spider train_others.json = datasets imported from other teams); "
                   "train and dev databases are disjoint; per-database share over databases with >= %d silent references; library_open = "
                   "frozen library records whose question leaves the decision open and whose gate category is a meaning choice, by gate "
                   "confidence, placed by the same rule (all questions, not only silent ones)" % I.MIN_PER_DB)
    from specbridge.comm.diagnose import prior as P
    if os.path.exists(P.OUT + "/NOTE.md"):          # the defaults-note experiment (not in the paper; absent from the release)
        out["note_experiment"] = {"note": open(P.OUT + "/NOTE.md").read(),
                                  "models": {m: r for m in NOTE_MODELS for r in [note_experiment(m)] if r}}
    save("fig6_inclination", out, "silent-question defaults per meaning decision and author group (Wilson), per database, and the library's open meaning records placed", rows)


# ---------------- Fig. impact: how far the unstated reading moves the answer (specbridge.report.impact, model-free) --------
def impact():
    R = json.load(open("out/impact/impact.json"))["results"]
    out = {src: {"questions": R[src]["questions"],
                 "kinds": {k: dict(v, wilson_changed=wilson(v["changed"], v["edits"]), wilson_gt50=wilson(v["gt50"], v["single"]) if v["single"] else None)
                           for k, v in R[src].items() if k != "questions"}} for src in R}
    save("fig_impact", out, "per silent choice: the library edit applied to the reference SQL; answers that change, single values that move > 10% / > 50% (Wilson)")


# ---------------- the human review: what it removes, and whether the results depend on it --------------------------------------
def review():
    """The author's review of the 307 sets that pass every check: sets rejected, sets kept where one reviewer model disputed the open
    request, and both interpretations returned (among the sets each model computes, as in Fig. disclosure) on every set (no human
    filter), on the kept sets, and on the rejected sets."""
    from specbridge.comm.transfer.evaluate import matches
    from specbridge.comm.transfer import combined as CB
    R = CB.D; C = {c["case"]: c for c in json.load(open(R + "/eval/frozen.json"))["cases"]}; V = json.load(open("human_supervision/verdicts.json"))
    oth = lambda x: "B" if x == "A" else "A"
    keeps = lambda k: (lambda v: v["verdict"] == "yes" or v["note"].startswith("No: the type is rare"))(V[k.split("-")[-1]])   # the 1% rule is not the author's
    kept = {k for k in C if keeps(k)}; disputed = {k for k in C if C[k]["label"] == "disputed open"}
    pops = {"all": set(C), "kept": kept, "rejected": set(C) - kept}
    out = {"sets": len(C), "rejected": len(C) - len(kept), "disputed": len(disputed), "disputed_kept": len(disputed & kept), "models": {}}
    for m in MODELS:
        d = R + "/eval/runs/%s_b1" % m.replace("-", "_"); pr = {}
        for f in os.listdir(d):
            o = json.load(open(os.path.join(d, f))); k, v = o["key"].rsplit("|", 1); pr[(k, v)] = matches(C[k], o["answer"]) if o.get("answer") is not None else []
        D = {}
        for f in os.listdir(R + "/disclose/" + m):
            x = json.load(open(os.path.join(R, "disclose", m, f))); D[(x["case"], x["wording"])] = x
        got = lambda o: set(o["primary_matches"]) | {y for a in o["alternatives"] for y in a["matches"]}
        res = {}
        for name, ks in pops.items():
            comp = [k for k in ks if C[k]["intended"] in pr.get((k, "precise"), []) and oth(C[k]["intended"]) in pr.get((k, "precise_other"), [])]
            res[name] = {"k": sum({"A", "B"} <= got(D[(k, "open")]) for k in comp), "n": len(comp)}
        out["models"][m] = res
    save("review", out, "author review of the 307 sets: rejected, disputed kept; both interpretations returned with and without the human filter")


if __name__ == "__main__":
    for f in (sys.argv[1:] and [globals()[a] for a in sys.argv[1:]]) or (fig1, tab1, fig2, fig3, tab2, fam, disclosure, inclination, impact, review):
        print("==", f.__name__, flush=True); f()
    if sys.argv[1:] and os.path.exists(OUT + "/INDEX.md"):   # a partial build keeps the other exhibits' lines
        new = {l.split("`")[1].split(".")[0] for l in INDEX}
        INDEX[:0] = [l for l in open(OUT + "/INDEX.md").read().split("\n") if l.startswith("- `") and l.split("`")[1].split(".")[0] not in new]
    open(OUT + "/INDEX.md", "w").write("# Exhibit data (built by specbridge.report.exhibit_data; model-free)\n\n" + "\n".join(INDEX) + "\n")
    print("\n".join(INDEX))
