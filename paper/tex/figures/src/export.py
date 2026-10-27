"""Write the CSV file(s) behind every data figure, from the artifact repository's data files.

The numbers are the ones specbridge/report/figures_col.py plots (same inputs, same arithmetic); only the drawing moved to pgfplots.
Usage: python3 -I export.py <artifact repo root> <output dir> [<paper data dir>]
The paper data files are read from reproduce/expected/out/paper/data (the files behind the paper) unless a paper data dir is
given (relative to the repository root); make reproduce passes out/paper/data, the files it has just rebuilt.
"""
import collections, glob, json, math, os, sys

REPO, OUT = sys.argv[1], sys.argv[2]
DATA = os.path.join(REPO, sys.argv[3] if len(sys.argv) > 3 else "reproduce/expected/out/paper/data")
M = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
SHORT = {"haiku": "h", "sonnet": "s", "gpt-6-sol": "g", "gpt-6-luna": "l"}
pct = lambda k, n: 100.0 * k / n
_C = {}


def J(p):
    """A JSON file of the repository: a bare name is a paper data file, anything else a path from the repository root."""
    path = os.path.join(DATA, p + ".json") if "/" not in p else os.path.join(REPO, p)
    if path not in _C: _C[path] = json.load(open(path))
    return _C[path]


def wilson(k, n, z=1.96):
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return c - h, c + h


def err(ci, v):
    """An interval given as fractions -> (minus, plus) around v in percent, as figures_col.err."""
    return max(0.0, v - 100 * ci[0]), max(0.0, 100 * ci[1] - v)


def write(name, header, rows):
    with open(os.path.join(OUT, name + ".csv"), "w") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join(("%.4f" % x) if isinstance(x, float) else str(x) for x in r) + "\n")


def accepted_cases():
    V = J("human_supervision/verdicts.json")
    return [c for c in J("out/transfer/all/render/eval/frozen.json")["cases"] if (V.get(c["case"].split("-")[-1]) or {}).get("verdict") == "yes"]


def sets_of(t):
    t = {"ties_and_selection": "tie"}.get(t, t)
    return sum(1 for c in accepted_cases() if c["type"] == t)


# ---------------------------------------------------------------- Fig. 5 funnel
def funnel():
    G = J("tab3_generation")["funnel"]; inv = lambda i: int(G["inventory"].split("|")[i + 2].strip())
    E = [r for r in open(os.path.join(REPO, "out/transfer/ext/cp/INVENTORY.md")) if r.startswith("| all ")][0].split("|")
    ex = lambda i: int(E[i + 2].strip())
    sel = len(J("out/transfer/ext/render/selection.json")); fil = sum(J("filter_sets")["verdicts"].values())
    S = [inv(1) + ex(1), inv(2) + ex(2), inv(3) + ex(3), inv(4) + inv(5) + ex(4) + ex(5), G["selected"] + sel, G["frozen"] + fil,
         J("accepted")["scopes"]["accepted_all_types"]["n"], J("fig5_tab4_disclosure")["n_families"]]
    write("funnel", ["y", "v"], [[len(S) - 1 - i, v] for i, v in enumerate(S)])


# ---------------------------------------------------------------- Fig. 6 ablation, Fig. S2 coverage
ABL = [("full", 8), ("-dedupe", 7), ("-varies", 6), ("-stepcheck", 5), ("-restate", 4), ("-profile", 3), ("-types", 2), ("-lookahead", 1), ("naive", 0)]
ABC = ["good and sound", "good, not sound", "duplicate", "off target depth", "invalid", "not drawn"]


def ablation():
    ab = J("fig1_coverage")["ablation"]; rows = []
    for key, y in ABL:
        o = ab[key]["outcomes"]; n = ab[key]["attempts"]; vals = [pct(o.get(c, 0), n) for c in ABC]
        g = vals[0]; rows.append([y] + vals + [("%.0f" % g) if g >= 1 else ("%.1f" % g)])
    write("ablation", ["y", "good", "notsound", "dup", "off", "invalid", "notbuilt", "glabel"], rows)
    return ab["full"]["attempts"]


NICE = {"agg": "Aggregation", "baseline": "Baseline comparison", "share": "Share of total", "rank": "Top-k within group", "row ranking": "Top-k rows",
        "diff": "Difference of two measures", "ratio": "Ratio of two measures", "grouped": "Grouping", "multi-table": "Joins",
        "A>=2": "Arithmetic depth $\\geq$ 2", "S>=5": "Step depth $\\geq$ 5"}


def coverage():
    f = J("fig1_coverage"); feats = f["features"]; N = f.get("ondemand_databases") or f["n_buildable"]
    sup = [100 * f["support_all_buildable"][k] for k in feats]; gen = [pct(f["meaning"]["features"][k]["meaningful"], N) for k in feats]
    order = list(reversed(sorted(range(len(feats)), key=lambda i: sup[i])))     # numpy's argsort(...)[::-1] on these values
    write("coverage", ["y", "sup", "gen"], [[len(feats) - 1 - r, sup[i], gen[i]] for r, i in enumerate(order)])
    with open(os.path.join(OUT, "coverage_labels.tex"), "w") as fh:      # the tick labels, top to bottom reversed (y = 0 first)
        fh.write("\\def\\coveragelabels{%s}\n" % ",".join("{%s}" % NICE[feats[i]] for i in reversed(order)))
    return N


# ---------------------------------------------------------------- Fig. 7 specification
def specification():
    f = J("fig2_explicit_vs_precise"); rows = []
    for i, m in enumerate(M):
        o = f["overall"][m]; e = pct(*o["explicit"]); p = pct(*o["precise_v2"])
        rows.append([i, e, *err(o["explicit_ci"], e), p, *err(o["precise_ci"], p), ("$+$%.1f" if p >= e else "$-$%.1f") % abs(p - e)])  # a true minus sign
    write("specification_overall", ["x", "e", "em", "ep", "p", "pm", "pp", "diff"], rows)
    write("specification_depth", ["S"] + [SHORT[m] for m in M],
          [[s] + [pct(*f["depth"][m]["S%d" % s]["explicit_errors"]) for m in M] for s in (3, 4, 5, 6)])
    return f["n_tasks"]


# ---------------------------------------------------------------- Fig. 8 disclosure, 9 decomposition, 10 outcomes, 11 bytype
def disclosure():
    F = J("fig5_tab4_disclosure")["models"]
    mets = ["precise_correct", "open_admissible", "recognises", "states_faithful", "covers_both"]
    rows = []
    for i, k in enumerate(mets):
        r = [len(mets) - 1 - i]
        for m in M:
            x = F[m][k]; v = pct(x["k"], x["n"]); r += [v, *err(x["ci"], v)]
        rows.append(r)
    write("disclosure", ["y"] + [c % SHORT[m] for m in M for c in ("%s", "%sm", "%sp")], rows)
    write("disclosure_given", ["y"] + [SHORT[m] for m in M],
          [[0] + [pct(F[m]["covers_both_given_both_precise"]["k"], F[m]["covers_both_given_both_precise"]["n"]) for m in M]])


def decomposition():
    F = J("fig5_tab4_disclosure")["models"]; A = [J("out/ambrosia/%s.json" % f)["models"] for f in ("decomposition", "decomposition_conf")]
    get = [lambda m: (F[m]["decomposition"]["matched"]["all"]["both_specific_right"], F[m]["decomposition"]["matched"]["all"]["not_covered"]),
           lambda m: (F[m]["decomposition"]["exploration"]["all"]["both_specific_right"], F[m]["decomposition"]["exploration"]["all"]["not_covered"]),
           lambda m: (sum(a[m]["shape"]["missed_computed"] for a in A), sum(a[m]["shape"]["missed"] for a in A))]
    rows = []
    for i, m in enumerate(M):
        r = [len(M) - 1 - i]
        for g in get:
            k, n = g(m); v = pct(k, n); r += [v, *err(wilson(k, n), v)]
        rows.append(r)
    write("decomposition", ["y", "a", "am", "ap", "b", "bm", "bp", "c", "cm", "cp"], rows)


def stacked(name, counts, keys, colors):
    """Shares of a stacked bar per model, and the counts to print centred in the segments wide enough to hold them (>= 6%)."""
    rows, labels = [], []
    for i, m in enumerate(M):
        o = counts[m]; n = sum(o.get(k, 0) for k in keys); left = 0.0; y = len(M) - 1 - i
        rows.append([y] + [pct(o.get(k, 0), n) for k in keys])
        for k, tc in zip(keys, colors):
            w = pct(o.get(k, 0), n)
            if w >= 6: labels.append([y, left + w / 2, o.get(k, 0), tc])
            left += w
    write(name, ["y"] + [k.replace("_", "") for k in keys], rows)
    write(name + "_labels", ["y", "xc", "lab", "tc"], labels)


def outcomes():
    A = J("accepted")["scopes"]["accepted"]
    stacked("outcomes", {m: A["models"][m]["outcomes"] for m in M}, ["both", "named_one", "silent_computable", "not_computable", "no_run"],
            ["white", "white", "white", "sbInk", "sbInk"])
    return A["n"]


def conventions():
    C = J("conventions")
    stacked("conventions", C["models"], ["conventional", "other", "neither"], ["white", "white", "sbInk"])
    return C["sets"]


def bytype():
    F = J("fig5_tab4_disclosure")["models"]
    T = ["value_representation", "aggregation_level", "missing_values", "counting_unit", "tie"]
    for name, group, keys in (("bytype_type", "type", T), ("bytype_source", "source", ["Spider", "BIRD", "LiveSQLBench"])):
        rows = []
        for i, t in enumerate(keys):
            r = [len(keys) - 1 - i, F[M[0]]["by_group"][group][t]["sets"]]
            for m in M:
                g = F[m]["by_group"][group][t]; v = pct(g["k"], g["n"]); r += [v, *err(wilson(g["k"], g["n"]), v)]
            rows.append(r)
        write(name, ["y", "sets"] + [c % SHORT[m] for m in M for c in ("%s", "%sm", "%sp")], rows)
    NAMES = {"value_representation": "Strict or inclusive cutoff", "aggregation_level": "Aggregation level", "missing_values": "Missing values",
             "counting_unit": "Counting unit", "tie": "Ties", "Spider": "Spider", "BIRD": "BIRD", "LiveSQLBench": "LiveSQLBench"}
    with open(os.path.join(OUT, "bytype_labels.tex"), "w") as fh:
        for macro, group, keys in (("bytypetypelabels", "type", T), ("bytypesourcelabels", "source", ["Spider", "BIRD", "LiveSQLBench"])):
            fh.write("\\def\\%s{%s}\n" % (macro, ",".join("{%s (%d)}" % (NAMES[t], F[M[0]]["by_group"][group][t]["sets"]) for t in reversed(keys))))


# ---------------------------------------------------------------- Fig. 13 real, 14 causes
def real():
    R = J("fig3_real_benchmarks")["confirmation"]; ns = {}
    for split, name in (("bird_heldout100", "real_bird"), ("spider_confirm50", "real_spider")):
        rows = []
        for i, m in enumerate(M):
            x = R[split][m]; r = [i]
            for key, ci in (("original_strict", "original_strict_ci"), ("original_shape", "original_shape_ci"), ("explicit_strict", "explicit_ci")):
                v = pct(*x[key]); r += [v, *err(x[ci], v)]
            rows.append(r)
        write(name, ["x", "o", "om", "op", "c", "cm", "cp", "e", "em", "ep"], rows); ns[name] = R[split]["n"]
    return ns


CAUSES = ["implicit requirement", "semantic mapping", "reading choice", "unwanted processing", "run variation", "output shape",
          "numeric precision / grading sensitivity", "other"]


def causes():
    f = J("fig3_real_benchmarks")["causes"]; cs = [f["development/BIRD batches 3-8"], f["development/Spider"]]
    tot = [sum(v for c, v in x.items() if c) for x in cs]
    Y = [9.2, 8.2, 7.2, 5.8, 4.8, 3.4, 2.4, 1.4]
    write("causes", ["y", "bird", "spider", "nbird", "nspider"],
          [[Y[i], pct(cs[0].get(k, 0), tot[0]), pct(cs[1].get(k, 0), tot[1]), cs[0].get(k, 0), cs[1].get(k, 0)] for i, k in enumerate(CAUSES)])
    with open(os.path.join(OUT, "causes_labels.tex"), "w") as fh:
        fh.write("\\def\\causesnbird{%d}\\def\\causesnspider{%d}\n" % tuple(tot))
    return tot


# ---------------------------------------------------------------- Fig. 15 defaults, 16 impact
def defaults():
    G = J("fig6_inclination")["groups"]
    rows = [("BIRD train", 0), ("BIRD dev", 0), ("Spider train (own)", 1), ("Spider dev", 1), (None, 2)]
    out = []
    for i, (g, fam) in enumerate(rows):
        r = [len(rows) - 1 - i, fam]
        for kind, imp in (("ties_and_selection", "imported: geo, restaurants"), ("counting_unit", "imported: academic, imdb, yelp")):
            x = G[g or imp]["kinds"][kind]; r += [pct(x["k"], x["n"]), x["k"], x["n"]]
        out.append(r)
    write("defaults", ["y", "fam", "ties", "tiesk", "tiesn", "count", "countk", "countn"], out)


IMPACT = [("boundary", "Bound inclusive"), ("count_unit", "Rows vs entities"), ("ties", "Ties at extreme"), ("null_filter", "Missing values"),
          ("join_kind", "Unmatched rows")]


def impact():
    K = J("fig_impact")["BIRD dev"]["kinds"]
    rows = sorted(IMPACT, key=lambda kr: K[kr[0]]["changed"] / K[kr[0]]["edits"])        # bottom (y = 0) to top
    out = []
    for y, (key, _l) in enumerate(rows):
        r = K[key]; a, b, c = pct(r["gt50"], r["edits"]), pct(r["gt10"] - r["gt50"], r["edits"]), pct(r["changed"] - r["gt10"], r["edits"])
        out.append([y, a, b, c, a + b + c, "%.0f" % (a + b + c)])
    write("impact", ["y", "gt50", "gt10", "other", "total", "tlabel"], out)
    with open(os.path.join(OUT, "impact_labels.tex"), "w") as fh:
        fh.write("\\def\\impactlabels{%s}\n" % ",".join("{%s}" % lab for _k, lab in rows))


# ---------------------------------------------------------------- Fig. 18 method, 19 breakeven
def method():
    S = J("out/ambrosia/final/final.json")["solvers"]
    for m, name in (("sonnet", "method_sonnet"), ("gpt-6-sol", "method_sol")):
        x = S[m]; n = x["n_ambiguous"]; rows = []
        for a in ("plain", "samplek", "dtp", "ours"):
            v = x["arms"][a]; py = pct(v["allfound"], n)
            rows.append([a, 100 * v["precision"], py, py - 100 * v["allfound_ci"][0], 100 * v["allfound_ci"][1] - py, "%.1f" % v["calls"]])
        write(name, ["arm", "prec", "af", "afm", "afp", "calls"], rows)


def breakeven():
    X = J("out/ambrosia/final/exchange.json")["models"]["pooled"]["rates"]; rs = sorted(X, key=float)
    write("breakeven", ["x", "share", "wrong", "readings", "wlab", "rlab"],
          [[i, "%d" % round(100 * float(r)), X[r]["extra_wrong"], X[r]["extra_readings"], "%.0f" % X[r]["extra_wrong"], "%.0f" % X[r]["extra_readings"]]
           for i, r in enumerate(rs)])


# ---------------------------------------------------------------- Fig. 21 rewrite
def rewrite():
    V = J("human_supervision/verdicts.json")
    keep = lambda case: (V.get(case.split("-")[-1]) or {}).get("verdict") == "yes"
    main = {c["case"] for c in J("out/transfer/eval12-v2/render/eval/frozen.json")["cases"]}
    R = []
    for f in glob.glob(os.path.join(REPO, "out/rewrite/runs/*/*.json")):
        o = json.load(open(f))
        if not keep(o["case"]) or o["case"] not in main: continue
        R.append((o["model"], {v: o["reading"] in o[v]["matches"] for v in "abcd" if v in o}, "%s|%s|%s" % (o["model"], o["case"], o["reading"])))
    names = M + ["pooled"]; rows = []
    for i, name in enumerate(names):
        rs = [r for m, r, _k in R if name == "pooled" or m == name]; n = len(rs); row = [len(names) - 1 - i]
        for v in "acbd":
            k = sum(r[v] for r in rs); val = pct(k, n)
            row += [val, *err(wilson(k, n), val)] if name == "pooled" else [val, 0.0, 0.0]
        rows.append(row)
    write("rewrite_left", ["y", "a", "am", "ap", "c", "cm", "cp", "b", "bm", "bp", "d", "dm", "dp"], rows)
    C = J("out/rewrite/classify.json")
    lost = collections.Counter((C.get(k) or {}).get("lost", "other") for _m, r, k in R if r["a"] and not r["b"])
    order = [c for c, _n in lost.most_common()]; tot = sum(lost.values())
    write("rewrite_right", ["y", "v"], [[len(order) - 1 - i, pct(lost[c], tot)] for i, c in enumerate(order)])
    with open(os.path.join(OUT, "rewrite_labels.tex"), "w") as fh:
        fh.write("\\def\\rewritelabels{%s}\n" % ",".join("{%s}" % (c[:1].upper() + c[1:]) for c in reversed(order)))
    return len(R), tot


# ---------------------------------------------------------------- Fig. 4 choices (two columns)
LIB13 = ["aggregation_level", "calculation", "comparison_quantifier", "condition_linkage", "counting_unit", "missing_values", "negated_membership_scope",
         "population_scope", "referent_column", "relationship_role", "ties_and_selection", "time_scope", "value_representation"]


def choices():
    LIB = {t["type"]: t for t in J("tab2_library")["types"]}; REF = J("tab2_references")["table2"]; VS = J("tab2_library")["value_split"]
    MAJ = ("aggregation_level", "ties_and_selection", "counting_unit", "missing_values", "referent_column")
    rest = lambda k: sum(v[k] for t, v in LIB.items() if t in LIB13 and t not in MAJ and t != "value_representation") \
        + VS["value_matching"]["raise" if k == "raise" else "settled"]
    other_sets = J("fig5_tab4_disclosure")["n_families"] - sum(sets_of(t) for t in MAJ[:4] + ("value_representation",))
    R = [(LIB["aggregation_level"]["raise"], LIB["aggregation_level"]["settled_from_failures"], REF["aggregation_level"], sets_of("aggregation_level")),
         (VS["strict_cutoff"]["raise"], VS["strict_cutoff"]["settled"], REF["strict_cutoff"], sets_of("value_representation")),
         (LIB["ties_and_selection"]["raise"], LIB["ties_and_selection"]["settled_from_failures"], REF["ties_and_selection"], sets_of("ties_and_selection")),
         (LIB["counting_unit"]["raise"], LIB["counting_unit"]["settled_from_failures"], REF["counting_unit"], sets_of("counting_unit")),
         (LIB["missing_values"]["raise"], LIB["missing_values"]["settled_from_failures"], REF["missing_values"], sets_of("missing_values")),
         (LIB["referent_column"]["raise"], LIB["referent_column"]["settled_from_failures"], None, sets_of("referent_column")),
         (rest("raise"), rest("settled_from_failures"), None, other_sets)]
    rows = []
    for i, (op, st, ref, sets) in enumerate(R):
        share = pct(ref[1], sum(ref)) if ref else -1.0
        reflab = ("%.1f\\%% of %s" % (share, format(sum(ref), ",").replace(",", "{,}"))) if ref else ("not readable" if i == 5 else "")
        rows.append([len(R) - 1 - i, op, st, op + st, "%d + %d" % (op, st), share, reflab, sets])
    write("choices", ["y", "open", "settled", "total", "flab", "share", "rlab", "sets"], rows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    info = {"funnel": funnel(), "ablation attempts": ablation(), "coverage N": coverage(), "specification n": specification(),
            "disclosure": disclosure(), "decomposition": decomposition(), "outcomes n": outcomes(), "conventions sets": conventions(),
            "bytype": bytype(), "real n": real(), "causes n": causes(), "defaults": defaults(), "impact": impact(), "method": method(),
            "breakeven": breakeven(), "rewrite (readings, lost)": rewrite(), "choices": choices()}
    for k, v in info.items():
        if v is not None: print("%-26s %s" % (k, v))
    print("wrote", len(glob.glob(os.path.join(OUT, "*.csv"))), "csv files to", OUT)
