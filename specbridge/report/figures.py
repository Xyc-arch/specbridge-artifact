"""FIGURES AND TABLES OF THE PAPER, from out/paper/data (model-free).
    python -m specbridge.report.figures   -> out/paper/figures/fig<N>_*.{pdf,png}, out/paper/tables/tab<N>_*.{tex,md} (records; the paper uses figures_col)
Every figure shows 95% intervals where the data has them; every table prints exact denominators (k/n)."""
import collections, json, os, sys, textwrap, zlib
sys.path.insert(0, ".")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA, FIG, TAB = "out/paper/data", "out/paper/figures", "out/paper/tables"
os.makedirs(FIG, exist_ok=True); os.makedirs(TAB, exist_ok=True)
M = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
LABEL = {"haiku": "Haiku", "sonnet": "Sonnet", "gpt-6-sol": "GPT-Sol", "gpt-6-luna": "GPT-Luna"}
COL = {"haiku": "#0072B2", "sonnet": "#56B4E9", "gpt-6-sol": "#D55E00", "gpt-6-luna": "#E69F00"}   # Okabe-Ito; Claude blues, GPT oranges
plt.rcParams.update({"font.family": "Arial", "text.color": "black", "axes.labelcolor": "black", "axes.edgecolor": "black", "xtick.color": "black",
                     "ytick.color": "black", "legend.labelcolor": "black", "axes.titlecolor": "black", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "legend.fontsize": 7.5, "xtick.labelsize": 7.5,
                     "ytick.labelsize": 7.5, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "savefig.dpi": 200})
d = lambda n: json.load(open("%s/%s.json" % (DATA, n)))


def save(fig, name):
    for ext in ("pdf", "png"): fig.savefig("%s/%s.%s" % (FIG, name, ext), bbox_inches="tight")
    plt.close(fig); print("figure", name)


def err(ci, v):  # interval -> asymmetric error bars around v (all in %)
    return [[max(0, v - 100 * ci[0])], [max(0, 100 * ci[1] - v)]]


# ------------------------------------------------------------------ Fig. 1
def fig1():
    f = d("fig1_coverage"); feats = f["features"]; n = len(feats); od = f.get("ondemand") or {}; N = f.get("ondemand_databases") or f["n_buildable"]
    nice = {"agg": "aggregation", "baseline": "baseline\ncomparison", "share": "share of\ntotal", "rank": "top-k within\ngroup", "row ranking": "top-k rows",
            "diff": "difference of\ntwo measures", "ratio": "ratio of\ntwo measures", "grouped": "grouping", "multi-table": "joins", "A>=2": "arithmetic\ndepth >= 2", "S>=5": "step\ndepth >= 5"}
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist(); ang += ang[:1]
    ab = f.get("ablation")
    if ab:
        fig = plt.figure(figsize=(10.4, 4.4)); gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.1], wspace=0.95)
        ax = fig.add_subplot(gs[0, 0], polar=True)
    else:
        fig, ax = plt.subplots(figsize=(4.6, 4.6), subplot_kw={"polar": True})
    v_of = lambda vals: [vals.get(k, 0) for k in feats] + [vals.get(feats[0], 0)]
    for lab, vals, c, ls, fill, lw in (("possible by the schema", f["support_all_buildable"], "#009E73", "-", True, 1.8),
                                       ) + (
                                       (("meaningful (generated and reviewed)", {k: f["meaning"]["features"][k]["meaningful"] / N for k in feats}, "#D55E00", "--", False, 1.8),) if f.get("meaning") else ()):
        ax.plot(ang, v_of(vals), color=c, lw=lw, ls=ls, label=lab)
        if fill: ax.fill(ang, v_of(vals), color=c, alpha=0.12)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels([nice[k] for k in feats], fontsize=6.8); ax.xaxis.set_tick_params(pad=9); ax.set_ylim(0, 1); ax.set_rlabel_position(196)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["25", "50", "75", "100"], fontsize=6)
    ax.set_title("(a) Supported features: databases (%%) of %d" % N if ab else "Databases (%%) of %d" % N, pad=18, fontsize=8.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), frameon=False, fontsize=7, ncol=1 if ab else 2)
    if ab:
        ax = fig.add_subplot(gs[0, 1])
        arms = [("full", "ours (all mechanisms)"), ("-dedupe", "without deduplication"), ("-varies", "without \"must vary\""), ("-stepcheck", "without step data checks"),
                ("-restate", "without restatement rules"), ("-profile", "without the profile"), ("-types", "without type rules"), ("-lookahead", "without look-ahead"), ("naive", "naive (all off)")]
        cats = [("good and sound", "#D55E00", ""), ("good, not sound", "#F2C29B", ""), ("duplicate", "#009E73", ""), ("off target depth", "#56B4E9", ""),
                ("invalid", "#0072B2", ""), ("not drawn", "white", "///")]
        y = np.arange(len(arms))[::-1]
        for (key, lab), yy in zip(arms, y):
            o = ab[key]["outcomes"]; n = ab[key]["attempts"]; left = 0
            for c, col, h in cats:
                v = 100 * o.get(c, 0) / n
                if v: ax.barh(yy, v, left=left, color=col, edgecolor="black" if h else col, hatch=h, lw=0.4, height=0.7)
                left += v
            ax.text(101, yy, "%.0f%%" % (100 * o.get("good and sound", 0) / n) if o.get("good and sound", 0) / n >= 0.01 else "%.1f%%" % (100 * o.get("good and sound", 0) / n), va="center", fontsize=7)
        ax.set_yticks(y); ax.set_yticklabels([lab for _k, lab in arms], fontsize=7); ax.set_xlim(0, 100); ax.set_xlabel("attempts (%)")
        ax.set_title("(b) What each mechanism contributes", fontsize=8.5)
        from matplotlib.patches import Patch
        ax.legend([Patch(facecolor=col, edgecolor="black" if h else col, hatch=h) for _c, col, h in cats],
                  ["valid, on target, new and sound", "valid, on target, new, not sound", "duplicate", "off target depth", "invalid on the data", "not built"],
                  loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, frameon=False, fontsize=6.6)
    else:
        fig.tight_layout()
    save(fig, "fig1_coverage")


# ------------------------------------------------------------------ Fig. 2
def fig2():
    f = d("fig2_explicit_vs_precise"); dbs = list(f["per_database"]["haiku"])
    fig = plt.figure(figsize=(7.2, 5.2)); gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1])
    ax = fig.add_subplot(gs[0, :])
    x = np.arange(len(dbs)); off = {m: (i - 1.5) * 0.18 for i, m in enumerate(M)}
    for m in M:
        e = [100 * f["per_database"][m][db]["explicit"][0] / f["per_database"][m][db]["explicit"][1] for db in dbs]
        p = [100 * f["per_database"][m][db]["precise_v2"][0] / f["per_database"][m][db]["precise_v2"][1] for db in dbs]
        ax.scatter(x + off[m], e, color=COL[m], marker="o", s=16, label=LABEL[m] + ", explicit V", zorder=3)
        ax.scatter(x + off[m], p, facecolor="white", edgecolor=COL[m], marker="o", s=16, label=LABEL[m] + ", natural question", zorder=3)
        for xi, a, b in zip(x + off[m], e, p): ax.plot([xi, xi], [a, b], color=COL[m], lw=0.7, alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(dbs, rotation=30, ha="right"); ax.set_ylabel("tasks right (%)"); ax.set_ylim(40, 102)
    ax.set_title("(a) Per database"); ax.legend(ncol=4, frameon=False, loc="lower left", fontsize=6.5)
    ax = fig.add_subplot(gs[1, 0]); w = 0.36
    for i, m in enumerate(M):
        o = f["overall"][m]; e = 100 * o["explicit"][0] / o["explicit"][1]; p = 100 * o["precise_v2"][0] / o["precise_v2"][1]
        ax.bar(i - w / 2, e, w, color=COL[m], yerr=err(o["explicit_ci"], e), capsize=2, error_kw={"lw": 0.8})
        ax.bar(i + w / 2, p, w, color="white", edgecolor=COL[m], hatch="///", yerr=err(o["precise_ci"], p), capsize=2, error_kw={"lw": 0.8})
        ax.text(i, 101, "%+.1f" % (p - e), ha="center", fontsize=6.5)
    ax.set_xticks(range(len(M))); ax.set_xticklabels([LABEL[m] for m in M]); ax.set_ylim(60, 105); ax.set_ylabel("tasks right (%)")
    ax.set_title("(b) Overall (n = %d)" % f["n_tasks"])
    from matplotlib.patches import Patch
    ax.legend([Patch(facecolor="black"), Patch(facecolor="white", edgecolor="black", hatch="///")], ["explicit V", "natural question"], frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=7)
    ax = fig.add_subplot(gs[1, 1]); S = [3, 4, 5, 6]
    for m in M:
        r = [f["depth"][m]["S%d" % s] for s in S]; y = [100 * c["explicit_errors"][0] / c["explicit_errors"][1] for c in r]
        lo = [100 * c["explicit_error_wilson"][0] for c in r]; hi = [100 * c["explicit_error_wilson"][1] for c in r]
        ax.plot(S, y, "-o", color=COL[m], ms=3, lw=1.3, label="%s (p = %s)" % (LABEL[m], ("%.4f" % f["depth_test"]["explicit/%s" % m]["p_one_sided"]) if f["depth_test"]["explicit/%s" % m]["p_one_sided"] < 0.001 else "%.2f" % f["depth_test"]["explicit/%s" % m]["p_one_sided"]))
        ax.fill_between(S, lo, hi, color=COL[m], alpha=0.12)
    ax.set_xticks(S); ax.set_xticklabels(["S%d" % s for s in S]); ax.set_ylabel("explicit-V errors (%)"); ax.set_title("(c) Errors by step depth")
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    fig.tight_layout(); save(fig, "fig2_specification")


# ------------------------------------------------------------------ Fig. 3
PLAIN = {"output shape": "output columns differ", "unwanted processing": "solver added steps", "semantic mapping": "phrase mapped to another column or value",
         "implicit requirement": "unstated requirement", "reading choice": "open choice", "run variation": "solver inconsistent across runs",
         "numeric precision / grading sensitivity": "numeric precision", "other": "other"}


def fig3():
    f = d("fig3_real_benchmarks")
    fig = plt.figure(figsize=(7.2, 4.8)); gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])
    for j, (split, title) in enumerate((("bird_heldout100", "BIRD"), ("spider_confirm50", "Spider"))):
        ax = fig.add_subplot(gs[0, j]); C = f["confirmation"][split]; w = 0.26
        for i, m in enumerate(M):
            c = C[m]
            for k, (key, cik, sty) in enumerate((("original_strict", "original_strict_ci", dict(color="white", edgecolor=COL[m])),
                                                 ("original_shape", "original_shape_ci", dict(color="white", edgecolor=COL[m], hatch="///")),
                                                 ("explicit_strict", "explicit_ci", dict(color=COL[m])))):
                v = 100 * c[key][0] / c[key][1]
                ax.bar(i + (k - 1) * w, v, w, yerr=err(c[cik], v), capsize=1.5, error_kw={"lw": 0.7}, **sty)
        ax.set_xticks(range(len(M))); ax.set_xticklabels([LABEL[m] for m in M]); ax.set_ylim(0, 105); ax.set_ylabel("questions right (%)")
        n = C["n"]; ax.set_title(("(a) %s (n = %d)" if j == 0 else "%s (n = %d)") % (title, n))
    from matplotlib.patches import Patch
    fig.legend([Patch(facecolor="white", edgecolor="black"), Patch(facecolor="white", edgecolor="black", hatch="///"), Patch(facecolor="black")],
               ["original question", "original question, column differences ignored", "explicit V"], ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.03))
    ax = fig.add_subplot(gs[1, :]); order = ["output shape", "unwanted processing", "semantic mapping", "implicit requirement", "reading choice", "run variation", "numeric precision / grading sensitivity", "other"]
    pal = ["#999999", "#E69F00", "#0072B2", "#56B4E9", "#009E73", "#CC79A7", "#F0E442", "#666666"]
    rows = [("BIRD", f["causes"]["development/BIRD batches 3-8"]), ("Spider", f["causes"]["development/Spider"])]; y = np.arange(len(rows))
    for k, (lab, cs) in enumerate(rows):
        tot = sum(v for c, v in cs.items() if c); left = 0
        for c, colr in zip(order, pal):
            v = cs.get(c, 0) / tot * 100
            ax.barh(k, v, left=left, color=colr, label=PLAIN.get(c, c) if k == 0 else None); left += v
    ax.set_yticks(y); ax.set_yticklabels(["%s (n = %d)" % (lab, sum(v for c, v in cs.items() if c)) for lab, cs in rows]); ax.set_xlim(0, 100); ax.set_xlabel("share of failures (%)")
    ax.set_title("(b) Why the original question failed"); ax.invert_yaxis()
    ax.legend(ncol=4, frameon=False, fontsize=6.3, loc="upper center", bbox_to_anchor=(0.5, -0.28))
    fig.tight_layout(); save(fig, "fig3_real_benchmarks")


# ------------------------------------------------------------------ Fig. 4
def fig4():
    w = d("fig4_worked_example")["example"]; W = json.load(open("out/transfer/eval12-v2/render/written.json"))[w["case"]]
    one = lambda s: " ".join(str(s).split())
    edits = "; ".join('"%s" -> "%s"' % (one(e.get("from")), one(e.get("to"))) for e in (W.get("edits_B") or []))
    boxes = [("1  Program A  (%s, arithmetic depth %s, step depth %s)" % (w["database"], w["A"], w["S"]), textwrap.shorten(one(w["sql_A"]), 330, placeholder=" ...")),
             ("2  A decision the request could leave unstated", "Decision: %s\nReading A (the program): %s\nReading B: %s\nB is a small edit of SQL A; it runs and changes the answer." % (one(w["decision"]), one(w["reading_A"]), one(w["reading_B"]))),
             ("3  Library example shown to the writer", "%s, a reviewed real benchmark question with the same kind of decision" % w["retrieved_example"]),
             ("4  Three wordings", "Precise A: %s\nPrecise B = precise A with %s\nOpen: %s" % (one(w["precise_A"]), edits, one(w["open"]))),
             ("5  Checks passed", "plan covers every requirement; the edits reproduce precise B; both reviewers find no requirement lost or changed; each precise wording is accepted only for its own reading; open wording accepted for both readings by %s" % ("both reviewers" if w["review"]["label"].startswith("mutually") else "one reviewer"))]
    wrapped = [(t, "\n".join(textwrap.fill(line, 110) for line in body.split("\n"))) for t, body in boxes]
    lines = [b.count("\n") + 1 for _t, b in wrapped]; unit = 0.0205; heights = [0.05 + n * unit for n in lines]; gap = 0.03
    total = sum(heights) + gap * (len(heights) - 1); fig, ax = plt.subplots(figsize=(7.2, 9.6 * total)); ax.axis("off")
    y = 1.0
    for k, ((t, body), h) in enumerate(zip(wrapped, heights)):
        hh, gg = h / total, gap / total
        ax.add_patch(matplotlib.patches.FancyBboxPatch((0.005, y - hh), 0.99, hh, boxstyle="round,pad=0.003,rounding_size=0.008", fc="#F2F5FA", ec="#0072B2", lw=0.9, transform=ax.transAxes))
        ax.text(0.02, y - 0.012 / total, t, ha="left", va="top", fontsize=8.3, weight="bold", transform=ax.transAxes)
        ax.text(0.02, y - 0.042 / total, body, ha="left", va="top", fontsize=6.8, transform=ax.transAxes, linespacing=1.3)
        if k < len(heights) - 1: ax.annotate("", xy=(0.5, y - hh - gg + 0.002), xytext=(0.5, y - hh - 0.002), xycoords="axes fraction", arrowprops=dict(arrowstyle="->", lw=1.0, color="black"))
        y -= hh + gg
    save(fig, "fig4_worked_example")


# ------------------------------------------------------------------ Fig. 5
def fig5():
    f = d("fig5_tab4_disclosure")["models"]
    mets = [("precise_correct", "precise wording:\nanswer right"), ("open_admissible", "open wording:\nanswer is A or B"), ("recognises", "names the\nopen decision"),
            ("states_faithful", "states its reading\ntruthfully"), ("covers_both", "covers both\nreadings")]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); off = {m: (i - 1.5) * 0.16 for i, m in enumerate(M)}
    for j, (k, lab) in enumerate(mets):
        for m in M:
            r = f[m][k]; v = 100 * r["k"] / r["n"]
            ax.errorbar(j + off[m], v, yerr=err(r["ci"], v), fmt="o", color=COL[m], ms=4, lw=0.9, capsize=1.5, label=LABEL[m] if j == 0 else None)
            if k == "covers_both":
                c = f[m]["covers_both_given_both_precise"]; cv = 100 * c["k"] / c["n"]
                ax.errorbar(j + off[m] + 0.06, cv, yerr=err(c["ci"], cv), fmt="D", mfc="white", color=COL[m], ms=3.5, lw=0.8, capsize=1.2)
    ax.set_xticks(range(len(mets))); ax.set_xticklabels([l for _k, l in mets]); ax.set_ylabel("families (%) of 215"); ax.set_ylim(0, 105)
    ax.axvline(1.5, color="#BBBBBB", lw=0.6, ls=":"); ax.text(0.5, 103, "answer", ha="center", fontsize=7); ax.text(3, 103, "communication", ha="center", fontsize=7)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=COL[m], marker="o", ls="", label=LABEL[m]) for m in M] + [Line2D([], [], color="black", marker="D", mfc="white", ls="", label="covers both, among families with both precise right")]
    ax.legend(handles=h, ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=7)

    fig.tight_layout(); save(fig, "fig5_disclosure")


# ------------------------------------------------------------------ Fig. 6
MIN_SPLIT_N = 10   # a group is drawn for a decision only where at least this many silent references arise
# author groups (Fig. 6a, b) use colours no solver uses (solvers keep their blue/orange of every figure, Fig. 6c)
_BIRD, _SPIDER, _GEO, _ACAD, _SCH = "#332288", "#882255", "#44AA99", "#999933", "#555555"
GROUP_STY = {"BIRD train": (_BIRD, "white", "o"), "BIRD dev": (_BIRD, _BIRD, "o"), "Spider train (own)": (_SPIDER, "white", "o"),
             "Spider dev": (_SPIDER, _SPIDER, "o"), "imported: geo, restaurants": (_GEO, _GEO, "D"),
             "imported: academic, imdb, yelp": (_ACAD, _ACAD, "D"), "imported: scholar": (_SCH, _SCH, "D")}
SHORT = {"ties_and_selection": "ties: one row", "counting_unit": "count rows", "boundary_between": "between: inclusive",
         "boundary_open": "after/over: strict", "text_match": "exact match", "output_duplicates": "keep duplicates",
         "output_extreme": "value not returned", "missing_values": "no NULL filter", "population_scope": "inner join"}


def fig6():
    f = d("fig6_inclination"); kinds = f["figure_kinds"]; gs = list(GROUP_STY); G = f["groups"]
    pc_ = lambda g, k: 100 * G[g]["kinds"][k]["k"] / G[g]["kinds"][k]["n"] if G[g]["kinds"][k]["n"] >= MIN_SPLIT_N else None
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.2, 2.75), gridspec_kw={"width_ratios": [1.05, 0.85, 1.05], "wspace": 0.42})
    # (a) each decision as one point: same authors (train -> dev) vs other authors (Spider own train -> imported)
    pairs = [("BIRD train", "BIRD dev", _BIRD, "o"), ("Spider train (own)", "Spider dev", _SPIDER, "o")] + \
            [("Spider train (own)", g, GROUP_STY[g][0], "D") for g in gs if g.startswith("imported")]
    a.plot([0, 100], [0, 100], color="#BBBBBB", lw=0.7, ls="--", zorder=0); flips = []
    for gx, gy, col, mk in pairs:
        for kind in kinds:
            vx, vy = pc_(gx, kind), pc_(gy, kind)
            if vx is None or vy is None: continue
            a.plot(vx, vy, mk, ms=3.8, mec=col, mfc=col, alpha=0.9)
            if vy < 60: flips.append((vy, vx, "%s\n(%s)" % (SHORT[kind], gy.split(": ")[1])))
    ty = -100
    for vy, vx, lab in sorted(flips):
        ty = max(vy + 4, ty + 22); a.annotate(lab, (vx, vy), xytext=(vx - 5, ty), ha="right", va="center", fontsize=5.6, arrowprops=dict(arrowstyle="-", lw=0.4, color="#888888"))
    a.set_xlim(40, 102); a.set_ylim(-4, 104); a.set_xticks([40, 60, 80, 100])
    a.set_xlabel("BIRD train / Spider own train,\nusual way (%)", fontsize=7.2); a.set_ylabel("compared group, usual way (%)", fontsize=7.2)
    a.set_title("(a) Same vs other authors", fontsize=8.5)
    a.text(42, 74, "one point per decision\ncircles: compared with its\nown dev (same authors)\ndiamonds: Spider own train\ncompared with imported\ntrain data (other authors)", fontsize=5.4, va="top")
    # (b) silent questions whose reference goes against the usual reading on at least one decision
    for i, g in enumerate(gs):
        r = G[g]["silent_questions"]; v = 100 * r["against_usual"] / r["n"]; ec, fc, _mk = GROUP_STY[g]; yy = len(gs) - 1 - i
        b.barh(yy, v, 0.62, color=fc, edgecolor=ec, lw=0.9, xerr=err(r["wilson"], v), error_kw={"lw": 0.6, "capsize": 1.2, "ecolor": ec})
        b.text(100 * r["wilson"][1] + 1.2, yy, "%.0f%%" % v, va="center", fontsize=6)
    b.set_yticks([]); b.set_xlim(0, 55); b.set_xlabel("silent questions answered\nagainst the usual way (%)", fontsize=7.2)
    b.set_title("(b) Not covered by the default", fontsize=8.5)
    # (c) the solver told the authors' defaults (one fixed note, from BIRD train) vs told nothing
    E = f["note_experiment"]["models"]; ms = list(E); subs = list(E[ms[0]]["subsets"]); x = np.arange(len(subs)); w = 0.8 / (2 * len(ms))
    for i, m in enumerate(ms):
        col = COL[m]
        for j, lab in enumerate(subs):
            S = E[m]["subsets"][lab]["pass"]; n = E[m]["subsets"][lab]["n"]
            for k, (key, sty) in enumerate((("plain", dict(color="white", edgecolor=col)), ("note", dict(color=col, edgecolor=col)))):
                v = 100 * S[key] / n; xx = j + (2 * i + k - (2 * len(ms) - 1) / 2) * w
                c.bar(xx, v, w, yerr=err(S[key + "_wilson"], v), capsize=1.0, error_kw={"lw": 0.5}, lw=0.8, **sty)
            pv = S["mcnemar_p"]; ps = ("%.2f" % pv) if pv >= 0.01 else ("%.3f" % pv) if pv >= 0.001 else "<0.001"
            c.text(j + (2 * i + 0.5 - (2 * len(ms) - 1) / 2) * w, 100 * max(S["plain_wilson"][1], S["note_wilson"][1]) + 2.5,
                   "%+.1f\n%s" % (100 * (S["note"] - S["plain"]) / n, ps), ha="center", fontsize=4.9, color=col)
    n0 = E[ms[0]]["subsets"]
    c.set_xticks(x); c.set_xticklabels(["all\n(n = %d)" % n0["all"]["n"], "silent decision\n(n = %d)" % n0["with a silent decision"]["n"],
                                        "none\n(n = %d)" % n0["without one"]["n"]], fontsize=6.6)
    c.set_ylim(0, 122); c.set_yticks(range(0, 101, 20)); c.set_ylabel("BIRD dev questions right (%)", fontsize=7.2); c.set_title("(c) Telling the solver the defaults", fontsize=8.5)
    from matplotlib.patches import Patch
    c.legend([Patch(facecolor="white", edgecolor=COL[m]) for m in ms] + [Patch(facecolor=COL[m]) for m in ms],
             ["%s, question only" % LABEL[m] for m in ms] + ["%s + note" % LABEL[m] for m in ms],
             frameon=False, fontsize=5.4, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.03), columnspacing=0.8, handlelength=1.2)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker=GROUP_STY[g][2], ls="", mec=GROUP_STY[g][0], mfc=GROUP_STY[g][1], label="%s (%d db)" % (g, G[g]["databases"])) for g in gs]
    fig.legend(handles=h, ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=6.4, handletextpad=0.2, columnspacing=1.0,
               title="author groups, panels (a) and (b)", title_fontsize=6.4)
    save(fig, "fig6_inclination")


# ------------------------------------------------------------------ tables
def tex_escape(s):
    return str(s).replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$").replace("~", "\\textasciitilde{}").replace("^", "\\^{}")


def write_table(name, caption, head, rows, note=""):
    md = ["**%s**\n" % caption, "| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows] + (["", note] if note else [])
    open("%s/%s.md" % (TAB, name), "w").write("\n".join(md) + "\n")
    wide = len(head) > 5; env = "table*" if wide else "table"          # wide tables span both columns, scaled to the text width (needs graphicx)
    tab = ["\\begin{tabular}{%s}" % ("l" + "r" * (len(head) - 1)), "\\toprule", " & ".join(tex_escape(h) for h in head) + " \\\\", "\\midrule"] + \
          [" & ".join(tex_escape(c) for c in r) + " \\\\" for r in rows] + ["\\bottomrule", "\\end{tabular}"]
    tex = ["\\begin{%s}[t]" % env, "\\centering", "\\small", "\\caption{%s}" % tex_escape(caption), "\\label{tab:%s}" % name] + \
          (["\\resizebox{\\textwidth}{!}{%"] + tab + ["}"] if wide else tab) + (["\\par\\smallskip\\footnotesize %s" % tex_escape(note)] if note else []) + ["\\end{%s}" % env]
    open("%s/%s.tex" % (TAB, name), "w").write("\n".join(tex) + "\n"); print("table", name)


def tab1():
    t = d("tab1_construction"); by = collections.defaultdict(list)
    for r in t["pool"]: by[r["source"]].append(r)
    rows = []
    for src, rs in (("Spider", by["Spider"]), ("BIRD", by["BIRD"]), ("LiveSQLBench", by["LiveSQLBench"]), ("all", t["pool"])):
        s = lambda k: sum(r[k] for r in rs)
        rows.append([src, len(rs), "%d/%d" % (s("delivered"), s("requested")), "%d/%d" % (s("built_for_eq_measured"), s("delivered")), s("recomputed"), s("trivial"),
                     s("distinct_sql"), s("constructions"), "%.0f" % s("seconds"), 0])
    write_table("tab1a_construction", "Generating programs on the 12 evaluation databases (no model involved; about 100 programs per database)",
                ["source", "databases", "delivered / requested", "measured depth = target", "repeated computation", "trivial comparison", "distinct SQL", "distinct constructions", "seconds", "model calls"], rows,
                "Reviewed benchmark tasks on the same databases: 384 of 400 delivered (1,664 review calls); natural questions 382 of 384 (585 calls).")
    rows = []; ctl = collections.defaultdict(list)
    for r in t["control"]: ctl[r["request"]].append(r)
    for req, rng in (("shallow", "step depth 3-4"), ("balanced", "step depth 3-7"), ("deep", "step depth 5-7")):
        rs = ctl[req]
        rows.append(["depth request: %s" % rng, "%.1f of 48" % np.mean([r["delivered_mean"] for r in rs]),
                     "at step depth 3-4: %.0f-%.0f%%; at 5-7: %.0f-%.0f%%" % (100 * min(r["share_S3_4_min"] for r in rs), 100 * max(r["share_S3_4_max"] for r in rs), 100 * min(r["share_S5_7_min"] for r in rs), 100 * max(r["share_S5_7_max"] for r in rs))])
    pr = t["preferences"]; rngp = lambda k: "%.0f-%.0f%%" % (100 * min(r[k] for r in pr), 100 * max(r[k] for r in pr))
    for lab, k in (("weight: top-k in group 1", "rank_w1"), ("weight: top-k in group 10", "rank_w10"), ("weight: share of total 1", "share_w1"), ("weight: share of total 10", "share_w10"),
                   ("weight: baseline comparison 1", "baseline_w1"), ("weight: baseline comparison 0.1", "baseline_w0.1")):
        rows.append([lab, "48", "programs using it: %s" % rngp(k)])
    for need in ("rank", "share", "rank+share"):
        rs = [r for r in t["required"] if r["required"] == need]; dl = sum(r["delivered"] for r in rs)
        rows.append(["required: %s" % need.replace("rank", "top-k in group").replace("share", "share of total").replace("+", " + "), "%d" % dl, "all use it: %d/%d; measured depth = target %d/%d; databases with depth cells where it is impossible: %d/12" % (
            sum(r["all_use_them"] for r in rs), dl, sum(r["built_for_eq_measured"] for r in rs), dl, sum(1 for r in rs if r["cells_not_constructible"]))])
    write_table("tab1b_control", "Control: requesting depth, weighting an operation, requiring an operation (12 databases; ranges over databases and seeds)",
                ["request", "delivered per database", "outcome"], rows,
                "A weight acts only where the operation is offered (top-k in group only as the last step after a per-entity-within-group step); a requirement acts at every choice.")


def tab2():
    t = d("tab2_library"); rows = []
    for r in sorted(t["types"], key=lambda r: -(r["raise"] + r["stay_silent"])):
        q = textwrap.shorten(r["example_question"] or "", 70, placeholder="...") if r["example_question"] else "--"
        rows.append([r["type"].replace("_", " "), r["raise"], r["stay_silent"], r["from_records"], r["from_solved_questions"], r["example_source"] or "--", q])
    write_table("tab2_library", "Kinds of decision found in real benchmark questions (BIRD and Spider development questions only)",
                ["kind", "should raise", "should stay silent", "from diagnosed failures", "from questions always solved", "example source", "example question"], rows,
                "%d examples; %d errors in reference answers kept apart. comparison quantifier and negated membership scope are provisional kinds." % (t["n_examples"], t["n_defects"]))


CHECK = {"open_both": "open accepted for both readings", "selective": "each precise accepted only for its reading", "fidelity": "no requirement lost or changed", "pass": "passes every check"}


def tab3():
    t = d("tab3_generation"); fu = t["funnel"]
    rows = [["tasks", 382], ["decisions proposed", 704], ["reading B runs and changes the answer", 660], ["reading B can be described as explicit V", 633],
            ["accepted as reasonable (both reviewers / one)", "606 (357 / 249) on 330 tasks"], ["chosen (one per task, balanced across kinds)", fu["selected"]], ["frozen families", fu["frozen"]]]
    rows += [["  kind: %s" % k.replace("_", " "), "%d chosen, %d frozen" % (fu["selected_types"].get(k, 0), fu["frozen_types"].get(k, 0))] for k in sorted(fu["selected_types"], key=lambda k: -fu["selected_types"][k])]
    write_table("tab3a_funnel", "Building the communication tests: from proposed decisions to frozen families", ["stage", "count"], rows)
    rows = []
    for key, v in t["ablation_60_pairs"].items():
        c = v["full_vs_direct"]; mk, st = key.split("/"); rows.append(["%s, %s" % (CHECK.get(mk, mk), "first draft" if st == "first" else "after one revision"), "%d/60" % v["full"], "%d/60" % v["direct"], "%d / %d" % (c["only_first"], c["only_second"]), c["mcnemar_exact_p"]])
    write_table("tab3b_plan_vs_direct", "Plan-and-check vs direct generation on 60 tasks fixed before any writing",
                ["check", "plan-and-check", "direct", "only plan-and-check / only direct", "exact McNemar p"], rows,
                "Direct generation has no revision step, so its first-draft and final counts are equal.")


def tab4():
    f = d("fig5_tab4_disclosure")["models"]; rows = []
    for m in M:
        x = f[m]; o = x["overhead"]; a = x["alternatives"]
        rows.append([LABEL[m], "%d/215" % x["false_open"]["k"], "%d/%d" % (a["supported_judge"], a["judged"]), "%d/%d" % (a["returns_recorded_reading"], a["offered"]),
                     "%d -> %d" % (o["precise_plain_single"], o["precise_disclosure"]), "%d -> %d" % (o["open_plain_single"], o["open_disclosure"]),
                     "%.0f -> %.0f" % (o["median_seconds_plain"], o["median_seconds_disclosure"]), "%d -> %d" % (o["median_chars_plain"], o["median_chars_disclosure"]), "%.2f" % o["mean_answer_set"]])
    write_table("tab4_disclosure_controls", "Disclosure: settled decisions called open, alternatives, and cost against the same call without disclosure (215 families per solver)",
                ["solver", "precise wording called open", "alternatives judged reasonable", "alternatives returning A or B", "precise right: without -> with",
                 "open returns A or B: without -> with", "median seconds", "median answer characters", "distinct answers"], rows,
                "Without = the same single call without the disclosure sentences, on the same family and wording. Tokens not logged. Judge: Opus, not told which solver answered; human check pending.")
    rows = []
    for m in M:
        x = f[m]; p = lambda k: "%d (%.0f%%)" % (x[k]["k"], 100 * x[k]["k"] / x[k]["n"])
        c = x["covers_both_given_both_precise"]
        rows.append([LABEL[m], p("precise_correct"), p("open_admissible"), p("recognises"), p("states"), "%d/%d" % (x["faithful_given_stated"]["k"], x["faithful_given_stated"]["n"]),
                     p("states_faithful"), p("covers_both"), "%d/%d (%.0f%%)" % (c["k"], c["n"], 100 * c["k"] / c["n"])])
    write_table("tab5_disclosure_results", "Disclosure, all measures (exact counts behind Fig. 5; of 215 families)",
                ["solver", "precise: answer right", "open: answer is A or B", "names the decision", "states its reading", "true, among stated", "states it truthfully", "covers both readings", "covers both, among both precise right"], rows)


if __name__ == "__main__":
    for fn in (sys.argv[1:] and [globals()[a] for a in sys.argv[1:]]) or (fig1, fig2, fig3, fig4, fig5, fig6, tab1, tab2, tab3, tab4): fn()
