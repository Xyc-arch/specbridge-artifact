"""SINGLE-COLUMN FIGURES FOR THE MANUSCRIPT (paper/tex), from out/paper/data (model-free).
    python -m specbridge.report.figures_col [name ...]   -> out/paper/figures_col/col_<name>.pdf
The paper prints pgfplots versions of the same data (paper/tex/figures/src, data from its export.py); these drawings are the
reproduction check.
Every figure is drawn at the ACM column width (3.33 in) so it is printed at 1:1: text is 7-8 pt in the paper, never shrunk.
The wide multi-panel figures of specbridge.report.figures stay for the Markdown records (result.md, fig_explain.md)."""
import json, os, sys, textwrap
sys.path.insert(0, ".")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

DATA, FIG = "out/paper/data", "out/paper/figures_col"
os.makedirs(FIG, exist_ok=True)
W = 3.33                                     # ACM sigconf column width, inches
M = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
LABEL = {"haiku": "Haiku", "sonnet": "Sonnet", "gpt-6-sol": "GPT-Sol", "gpt-6-luna": "GPT-Luna"}
# Colors as in the seminal text-to-SQL papers' plots (DAIL-SQL, PVLDB 2024; Alpha-SQL): matplotlib's tab10/tab20, bars with
# thin black edges. Meaning is fixed in every figure: blue = the wanted reading or outcome, red = failure, gray = neutral;
# the four models take the first four tab10 colors in order.
BLUE, BLUE_M, BLUE_L = "#1F77B4", "#6BAED6", "#AEC7E8"
RED, RED_L = "#D62728", "#FF9896"
GRAY, GRAY_L, GRAY_XL = "#7F7F7F", "#C7C7C7", "#E5E5E5"
INK = "black"
EDGE = dict(edgecolor="black", lw=0.4)
COL = {"haiku": "#1F77B4", "sonnet": "#FF7F0E", "gpt-6-sol": "#2CA02C", "gpt-6-luna": "#D62728"}
plt.rcParams.update({"font.family": "Arial", "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
                     "legend.fontsize": 6.5, "axes.spines.top": True, "axes.spines.right": True, "axes.grid": True, "axes.grid.axis": "x", "axes.axisbelow": True,
                     "grid.color": "#D9D9D9", "grid.linestyle": "--", "grid.linewidth": 0.4, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                     "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5, "pdf.fonttype": 42, "svg.fonttype": "none",
                     "savefig.dpi": 300, "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold", "text.color": "black", "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black",
                     "axes.edgecolor": "black", "legend.frameon": False, "legend.handlelength": 1.2, "legend.columnspacing": 1.0})
d = lambda n: json.load(open("%s/%s.json" % (DATA, n)))
pct = lambda k, n: 100.0 * k / n


def save(fig, name, width=W):
    """Resize the figure until its tight bounding box is exactly `width` wide (one column by default), so every figure prints at 1:1 and all
    figure text has the same printed size."""
    for _ in range(6):
        fig.canvas.draw(); bb = fig.get_tightbbox(fig.canvas.get_renderer()); wide = bb.width + 0.04
        if abs(wide - width) < 0.005: break
        fig.set_size_inches(fig.get_figwidth() + (width - wide), fig.get_figheight())
    fig.savefig("%s/col_%s.pdf" % (FIG, name), bbox_inches="tight", pad_inches=0.02,
                metadata={"CreationDate": None})                     # no timestamp: a rebuild gives the same bytes
    plt.close(fig); print("figure col_%s" % name)


def err(ci, v):  # interval (fractions) -> asymmetric error bars around v (%)
    return [[max(0, v - 100 * ci[0])], [max(0, 100 * ci[1] - v)]]


def wilson(k, n, z=1.96):
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return [c - h, c + h]


# ---------------------------------------------------------------- construction: which features each database supports
NICE = {"agg": "aggregation", "baseline": "baseline comparison", "share": "share of total", "rank": "top-k within group", "row ranking": "top-k rows",
        "diff": "difference of two measures", "ratio": "ratio of two measures", "grouped": "grouping", "multi-table": "joins",
        "A>=2": "arithmetic depth ≥ 2", "S>=5": "step depth ≥ 5"}


def coverage():
    f = d("fig1_coverage"); feats = f["features"]; N = f.get("ondemand_databases") or f["n_buildable"]
    sup = [100 * f["support_all_buildable"][k] for k in feats]; gen = [pct(f["meaning"]["features"][k]["meaningful"], N) for k in feats]
    order = np.argsort(sup)[::-1]; y = np.arange(len(feats))[::-1]
    fig, ax = plt.subplots(figsize=(W, 2.25))
    for yy, i in zip(y, order):
        ax.barh(yy + 0.19, sup[i], 0.36, color=BLUE_L, **EDGE)
        ax.barh(yy - 0.19, gen[i], 0.36, color=BLUE, **EDGE)
    ax.set_yticks(y); ax.set_yticklabels([NICE[feats[i]] for i in order]); ax.set_xlim(0, 104); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("databases (%%) of %d" % N)
    ax.legend([Patch(facecolor=BLUE_L, **EDGE), Patch(facecolor=BLUE, **EDGE)],
              ["possible by the schema", "generated and accepted by both reviewers"], loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2, fontsize=6.5)
    save(fig, "coverage")


def ablation():
    ab = d("fig1_coverage")["ablation"]
    arms = [("full", "all mechanisms"), ("-dedupe", "− deduplication"), ("-varies", "− “must vary”"), ("-stepcheck", "− step data checks"),
            ("-restate", "− restatement rules"), ("-profile", "− column profile"), ("-types", "− type rules"), ("-lookahead", "− look-ahead"),
            ("naive", "none (naive)")]
    cats = [("good and sound", BLUE, "", "valid, on target, sound"), ("good, not sound", BLUE_L, "", "valid, on target, not sound"),
            ("duplicate", GRAY_L, "", "duplicate"), ("off target depth", RED_L, "", "off target depth"), ("invalid", RED, "", "invalid on the data"),
            ("not drawn", "none", "////", "not built")]
    fig, ax = plt.subplots(figsize=(W, 2.35)); y = np.arange(len(arms))[::-1]
    for (key, lab), yy in zip(arms, y):
        o = ab[key]["outcomes"]; n = ab[key]["attempts"]; left = 0
        for c, col, h, _l in cats:
            v = pct(o.get(c, 0), n)
            if v: ax.barh(yy, v, left=left, color=col, edgecolor="black", hatch=h, lw=0.4, height=0.68)
            left += v
        g = pct(o.get("good and sound", 0), n); ax.text(101.5, yy, ("%.0f%%" % g) if g >= 1 else "%.1f%%" % g, va="center", fontsize=6.5)
    ax.set_yticks(y); ax.set_yticklabels([lab for _k, lab in arms]); ax.set_xlim(0, 100); ax.set_xlabel("generation attempts (%%), %d per configuration" % ab["full"]["attempts"])
    ax.legend([Patch(facecolor=col, edgecolor="black", hatch=h, lw=0.4) for _c, col, h, _l in cats], [l for *_x, l in cats],
              loc="upper center", bbox_to_anchor=(0.42, -0.2), ncol=3, fontsize=6.5, handlelength=1.0, columnspacing=0.8)
    save(fig, "ablation")


# ---------------------------------------------------------------- explicit V vs natural request on generated tasks
def specification():
    f = d("fig2_explicit_vs_precise")
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 1.95), gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.42})
    w = 0.38
    for ax in (a, b): ax.grid(axis="x", visible=False); ax.grid(axis="y", visible=True)
    for i, m in enumerate(M):
        o = f["overall"][m]; e = pct(*o["explicit"]); p = pct(*o["precise_v2"])
        a.bar(i - w / 2, e, w, color=COL[m], yerr=err(o["explicit_ci"], e), capsize=1.3, error_kw={"lw": 0.6})
        a.bar(i + w / 2, p, w, color="none", edgecolor=COL[m], lw=0.9, yerr=err(o["precise_ci"], p), capsize=1.3, error_kw={"lw": 0.6})
        a.text(i, 102.5, "%+.1f" % (p - e), ha="center", fontsize=6.5)
    a.set_xticks(range(len(M))); a.set_xticklabels([LABEL[m].replace("-", "-\n") for m in M], fontsize=6.5); a.set_ylim(60, 106); a.set_ylabel("tasks right (%)")
    a.set_title("overall (n = %d)" % f["n_tasks"], fontsize=7.5)
    fig.legend([Patch(facecolor="#777777"), Patch(facecolor="none", edgecolor="#777777")], ["exact description", "natural request"], loc="upper center",
               bbox_to_anchor=(0.5, 1.1), ncol=2, fontsize=6.5)
    S = [3, 4, 5, 6]
    for m in M:
        r = [f["depth"][m]["S%d" % s] for s in S]; yv = [pct(*c["explicit_errors"]) for c in r]
        b.plot(S, yv, "-o", color=COL[m], ms=2.6, lw=1.1)
    for m in ("gpt-6-luna", "haiku"):
        r = f["depth"][m]["S6"]; b.text(6.1, pct(*r["explicit_errors"]), LABEL[m], fontsize=6.5, va="center")
    b.text(6.1, 3.0, "Sonnet,\nGPT-Sol", fontsize=6.5, va="center")
    b.set_xticks(S); b.set_xlim(2.7, 8.1); b.set_xlabel("step depth"); b.set_ylabel("errors, exact description (%)")
    b.set_title("errors by step depth", fontsize=7.5)
    save(fig, "specification")


# ---------------------------------------------------------------- real benchmarks: held-out accuracy, and why the original failed
def real():
    f = d("fig3_real_benchmarks")
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.85), sharey=True, gridspec_kw={"wspace": 0.12})
    for ax, (split, title) in zip(axes, (("bird_heldout100", "BIRD"), ("spider_confirm50", "Spider"))):
        C = f["confirmation"][split]; w = 0.27; ax.grid(axis="x", visible=False); ax.grid(axis="y", visible=True)
        for i, m in enumerate(M):
            c = C[m]
            for k, (key, cik, sty) in enumerate((("original_strict", "original_strict_ci", dict(color="none", edgecolor=COL[m], lw=0.8)),
                                                 ("original_shape", "original_shape_ci", dict(color="none", edgecolor=COL[m], hatch="//////", lw=0.8)),
                                                 ("explicit_strict", "explicit_ci", dict(color=COL[m])))):
                v = pct(*c[key]); ax.bar(i + (k - 1) * w, v, w, yerr=err(c[cik], v), capsize=0.9, error_kw={"lw": 0.5}, **sty)
        ax.set_xticks(range(len(M))); ax.set_xticklabels([LABEL[m].replace("-", "-\n") for m in M], fontsize=6.5); ax.set_ylim(0, 104)
        ax.set_title("%s held-out (n = %d)" % (title, C["n"]), fontsize=7.5)
    axes[0].set_ylabel("questions right (%)")
    fig.legend([Patch(facecolor="none", edgecolor="#555555", lw=0.8), Patch(facecolor="none", edgecolor="#555555", hatch="//////", lw=0.8), Patch(facecolor="#555555")],
               ["original question", "extra columns allowed", "exact description"], loc="upper center",
               bbox_to_anchor=(0.52, 1.12), ncol=3, fontsize=6.5, handlelength=1.0, columnspacing=0.7)
    save(fig, "real")


CAUSES = [("implicit requirement", "unstated requirement", BLUE), ("semantic mapping", "phrase mapped to another column", BLUE_M),
          ("reading choice", "open choice", BLUE_L), ("unwanted processing", "solver added steps", RED),
          ("run variation", "inconsistent across runs", RED_L), ("output shape", "output columns differ", GRAY),
          ("numeric precision / grading sensitivity", "numeric precision", GRAY_L), ("other", "other", GRAY_XL)]


def causes():
    f = d("fig3_real_benchmarks")
    rows = [("BIRD", f["causes"]["development/BIRD batches 3-8"]), ("Spider", f["causes"]["development/Spider"])]
    fig, ax = plt.subplots(figsize=(W, 1.42))
    for k, (lab, cs) in enumerate(rows):
        tot = sum(v for c, v in cs.items() if c); left = 0
        for key, _l, col in CAUSES:
            v = pct(cs.get(key, 0), tot)
            ax.barh(k, v, left=left, color=col, height=0.62, **EDGE)
            if v >= 7: ax.text(left + v / 2, k, "%.0f" % v, ha="center", va="center", fontsize=6.5, color="white" if col in (BLUE, RED, GRAY) else "black")
            left += v
    ax.set_yticks([0, 1]); ax.set_yticklabels(["%s (n = %d)" % (lab, sum(v for c, v in cs.items() if c)) for lab, cs in rows]); ax.invert_yaxis()
    ax.set_xlim(0, 100); ax.set_xlabel("development failures (%)")
    ax.legend([Patch(facecolor=col, **EDGE) for _k, _l, col in CAUSES], [l for _k, l, _c in CAUSES], loc="upper center", bbox_to_anchor=(0.42, -0.36),
              ncol=2, fontsize=6.5, handlelength=1.0, columnspacing=1.0)
    save(fig, "causes")


# ---------------------------------------------------------------- answering vs communicating on 215 request sets
def disclosure():
    f = d("fig5_tab4_disclosure")["models"]
    mets = [("precise_correct", "specific request:\nanswer right"), ("open_admissible", "open request:\nanswer is A or B"), ("recognises", "names the\nopen choice"),
            ("states_faithful", "states its interpretation\ncorrectly"), ("covers_both", "returns both\nA and B")]
    fig, ax = plt.subplots(figsize=(W, 2.54)); y = np.arange(len(mets))[::-1]; off = {m: (1.5 - i) * 0.15 for i, m in enumerate(M)}
    for (k, _l), yy in zip(mets, y):
        for m in M:
            r = f[m][k]; v = pct(r["k"], r["n"])
            ax.errorbar(v, yy + off[m], xerr=err(r["ci"], v), fmt="o", ms=3.2, color=COL[m], lw=0.7, capsize=1.0)
        if k == "covers_both":
            for m in M:
                c = f[m]["covers_both_given_both_precise"]; v = pct(c["k"], c["n"])
                ax.plot(v, yy + off[m], "D", ms=3.0, mfc="none", mec=COL[m], mew=0.8)
    ax.axhline(2.5, color="#BBBBBB", lw=0.5, ls=":")
    ax.set_yticks(y); ax.set_yticklabels([l for _k, l in mets]); ax.set_xlim(0, 100); ax.set_xlabel("request sets (%%) of %d" % d("fig5_tab4_disclosure")["n_families"])
    h = [Line2D([], [], marker="o", ls="", color=COL[m], ms=3.2, label=LABEL[m]) for m in M] + \
        [Line2D([], [], marker="D", ls="", mfc="none", mec="black", ms=3.0, label="both, if both specific right")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=3, fontsize=6.5, handletextpad=0.2)
    save(fig, "disclosure")


# ---------------------------------------------------------------- author defaults: gap to the training data, per decision
SHORT = {"ties_and_selection": "one row for an extreme", "counting_unit": "count rows, not entities", "missing_values": "no NULL filter before sorting",
         "population_scope": "inner join", "boundary_between": "“between” inclusive", "boundary_open": "“after”, “over” strict",
         "text_match": "exact text match"}
PAIRS = [("BIRD dev", "BIRD train", "BIRD dev vs BIRD train", "#332288", "o"), ("Spider dev", "Spider train (own)", "Spider dev vs Spider train", "#882255", "o"),
         ("imported: geo, restaurants", "Spider train (own)", "geo, restaurants vs Spider train", "#44AA99", "D"),
         ("imported: academic, imdb, yelp", "Spider train (own)", "academic, imdb, yelp vs Spider train", "#999933", "D"),
         ("imported: scholar", "Spider train (own)", "scholar vs Spider train", "#555555", "D")]


def defaults(min_n=10):
    """The convention is the authors': for the two decisions with a clear split, the share of silent questions whose reference takes the
    usual interpretation, for BIRD and Spider's own authors (train and dev) and for the imported Spider group that reverses it."""
    f = d("fig6_inclination"); G = f["groups"]
    FAM = {"BIRD": BLUE_M, "Spider, own authors": BLUE_L, "Spider, imported from older datasets": RED_L}
    panels = [("ties_and_selection", "Ties at an extreme:\n% returning one row", "imported: geo, restaurants", "Geo, Restaurants"),
              ("counting_unit", "Count over a join:\n% counting joined rows", "imported: academic, imdb, yelp", "Academic, IMDB, Yelp")]
    rows = [("BIRD train", "BIRD train", "BIRD"), ("BIRD dev", "BIRD dev", "BIRD"), ("Spider train (own)", "Spider train", "Spider, own authors"),
            ("Spider dev", "Spider dev", "Spider, own authors"), (None, "Spider imported", "Spider, imported from older datasets")]
    ys = list(range(len(rows)))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.11), sharey=True, gridspec_kw={"wspace": 0.16})
    for ax, (kind, title, imp, implab) in zip(axes, panels):
        for (g, lab, fam), yy in zip(rows, ys):
            g = g or imp; k, n = G[g]["kinds"][kind]["k"], G[g]["kinds"][kind]["n"]; v = pct(k, n)
            ax.barh(yy, max(v, 0.8), color=FAM[fam], height=0.66, **EDGE)
            if v >= 40: ax.text(v - 2, yy, "%.0f%%" % v, va="center", ha="right", fontsize=6.5, color="black")
            else: ax.text(v + 2.5, yy, "%.0f%%\n%s" % (v, implab), va="center", ha="left", fontsize=6.5, color="black")
        ax.set_xlim(0, 106); ax.set_xticks([0, 50, 100]); ax.set_title(title, fontsize=6.8, pad=3, loc="left"); ax.tick_params(axis="y", length=0); ax.axhline(0.5, color="#999999", lw=0.5, ls=":")
    axes[0].set_yticks(ys); axes[0].set_yticklabels([r[1] for r in rows], fontsize=6.5)
    fig.legend(handles=[Patch(facecolor=c, label=l, **EDGE) for l, c in FAM.items()], loc="upper center", bbox_to_anchor=(0.52, 0.02), ncol=3, fontsize=6.5, handlelength=1.0, columnspacing=0.8)
    others = [k for k in f["figure_kinds"] if k not in ("ties_and_selection", "counting_unit")]
    mins = min(pct(G[g]["kinds"][k]["k"], G[g]["kinds"][k]["n"]) for g in G for k in others if G[g]["kinds"][k]["n"] >= min_n)
    print("  other decisions: minimum share read the usual way in any group (n >= %d): %.1f%%" % (min_n, mins))
    save(fig, "defaults")

def note():
    """Gain from the defaults note, per solver and subset, with the paired bootstrap 95% interval (exhibit_data.note_experiment)."""
    E = d("fig6_inclination")["note_experiment"]["models"]; ms = [m for m in M if m in E]
    subs = [("all", "all"), ("clean", "clean"), ("clean, silent decision", "clean,\nsilent decision"), ("clean, none detected", "clean,\nnone detected")]
    fig, ax = plt.subplots(figsize=(W, 1.9)); off = {m: (i - (len(ms) - 1) / 2) * 0.17 for i, m in enumerate(ms)}
    for j, (key, _l) in enumerate(subs):
        for m in ms:
            S = E[m]["subsets"][key]["pass"]; n = E[m]["subsets"][key]["n"]; g = pct(S["note"] - S["plain"], n)
            lo, hi = 100 * S["diff_ci"][0], 100 * S["diff_ci"][1]
            ax.errorbar(j + off[m], g, yerr=[[g - lo], [hi - g]], fmt="o", ms=3.4, color=COL[m], lw=0.8, capsize=1.2)
    ax.axhline(0, color="#999999", lw=0.6)
    n0 = E[ms[0]]["subsets"]
    ax.set_xticks(range(len(subs))); ax.set_xticklabels(["%s\n(n = %d)" % (l, n0[k]["n"]) for k, l in subs], fontsize=6.5); ax.set_xlim(-0.5, len(subs) - 0.5)
    ax.set_ylabel("gain from the note (points)")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=COL[m], ms=3.4, label=LABEL[m]) for m in ms], loc="upper center",
              bbox_to_anchor=(0.5, -0.27), ncol=len(ms), fontsize=6.5, handletextpad=0.2)
    save(fig, "note")


def method():
    """Section 5: the disclosure method's trade-off on fresh AMBROSIA test questions -- per solver, each arm at its precision on
    unambiguous questions (x) and AllFound on ambiguous questions (y, Wilson 95%); the number beside a point is calls per question."""
    J = json.load(open("out/ambrosia/final/final.json"))
    ARM = [("plain", "Plain", "o", GRAY, "none"), ("samplek", "Three samples", "s", GRAY, GRAY),
           ("dtp", "DtP", "D", RED, RED), ("ours", "Ours", "*", BLUE, BLUE)]
    OFF = {("sonnet", "dtp"): (-5, 0, "right", "center"), ("sonnet", "samplek"): (5, 5, "left", "bottom"), ("sonnet", "plain"): (5, -5, "left", "top"),
           ("sonnet", "ours"): (6, 0, "left", "center"), ("gpt-6-sol", "dtp"): (6, 0, "left", "center"), ("gpt-6-sol", "samplek"): (-5, 0, "right", "center"),
           ("gpt-6-sol", "plain"): (6, 0, "left", "center"), ("gpt-6-sol", "ours"): (6, 0, "left", "center")}
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.05), sharey=True); hs = []
    for ax, (m, lab) in zip(axes, (("sonnet", "Sonnet"), ("gpt-6-sol", "GPT-Sol"))):
        x = J["solvers"][m]; n = x["n_ambiguous"]
        for a, name, mk, ec, fc in ARM:
            v = x["arms"][a]; px, py = 100 * v["precision"], 100 * v["allfound"] / n; ci = v["allfound_ci"]
            h = ax.errorbar(px, py, yerr=[[py - 100 * ci[0]], [100 * ci[1] - py]], fmt=mk, ms=7.5 if mk == "*" else 4.2, mec=ec, mfc=fc, ecolor=ec, elinewidth=0.6,
                            capsize=1.5, mew=0.8, zorder=3, label=name)
            if m == "sonnet": hs.append(h)
            dx, dy, ha, va = OFF[(m, a)]
            ax.annotate("%.1f" % v["calls"], (px, py), xytext=(dx, dy), textcoords="offset points", fontsize=6.5, ha=ha, va=va)
        ax.set_title(lab + ", AMBROSIA", pad=2); ax.set_xlim(36, 74); ax.set_xticks([40, 50, 60, 70]); ax.grid(axis="both", lw=0.3, color="#DDDDDD", zorder=0)
        ax.set_xlabel("precision, unambiguous (%)")
    axes[0].set_ylabel("AllFound, ambiguous (%)"); axes[0].set_ylim(10, 70)
    fig.legend(hs, [h.get_label() for h in hs], loc="upper center", ncol=4, bbox_to_anchor=(0.55, 1.07), handletextpad=0.3)
    fig.tight_layout(w_pad=0.6); save(fig, "method")


# ---------------------------------------------------------------- missed readings the model computes when asked
def decomposition():
    """Per solver: of the interpretations missing from the open answer, the share the same solver computes when asked for that interpretation alone.
    Request sets (three settings for the specific requests) and AMBROSIA's own items (dev + confirmation samples, one call)."""
    F = d("fig5_tab4_disclosure")["models"]
    A = [json.load(open("out/ambrosia/%s.json" % f))["models"] for f in ("decomposition", "decomposition_conf")]
    S = [("request sets, same single call", lambda m: (F[m]["decomposition"]["matched"]["all"]["both_specific_right"], F[m]["decomposition"]["matched"]["all"]["not_covered"]), "o", True),
         ("request sets, specific with exploration", lambda m: (F[m]["decomposition"]["exploration"]["all"]["both_specific_right"], F[m]["decomposition"]["exploration"]["all"]["not_covered"]), "o", False),
         ("AMBROSIA, single call", lambda m: (sum(a[m]["shape"]["missed_computed"] for a in A), sum(a[m]["shape"]["missed"] for a in A)), "D", True)]
    fig, ax = plt.subplots(figsize=(W, 1.75)); y = np.arange(len(M))[::-1]; off = [0.2, 0.0, -0.2]
    for (lab, get, mk, filled), o in zip(S, off):
        for m, yy in zip(M, y):
            k, n = get(m); v = pct(k, n)
            ax.errorbar(v, yy + o, xerr=err(wilson(k, n), v), fmt=mk, ms=3.4, color=COL[m], mfc=COL[m] if filled else "none", mec=COL[m], mew=0.8, lw=0.7, capsize=1.0)
    ax.set_yticks(y); ax.set_yticklabels([LABEL[m] for m in M]); ax.set_xlim(0, 100); ax.set_ylim(-0.5, len(M) - 0.5)
    ax.axvline(50, color="#BBBBBB", lw=0.5, ls=":"); ax.set_xlabel("missed interpretations the model computes when asked (%)")
    h = [Line2D([], [], marker=mk, ls="", color="black", mfc="black" if f else "none", mec="black", ms=3.4, label=l) for l, _g, mk, f in S]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.45, -0.32), ncol=1, fontsize=6.5, handletextpad=0.3)
    save(fig, "decomposition")


# ---------------------------------------------------------------- editing vs rewriting a request (specbridge.comm.transfer.rewrite)
def rewrite():
    """Left: accuracy per interpretation under four request texts, per solver and pooled. Right: what the rewrite lost (interpretations right
    from the original specific request and wrong from the rewrite)."""
    import glob, collections
    R = []
    from specbridge.comm.transfer import reviewed as RV, combined as CB
    main = set(CB.part_cases(0))                                  # the primary result: readings of sets built without a filter
    for f in glob.glob("out/rewrite/runs/*/*.json"):
        o = json.load(open(f))
        if not RV.keep(o["case"]) or o["case"] not in main: continue
        R.append((o["model"], {v: o["reading"] in o[v]["matches"] for v in "abcd" if v in o}, "%s|%s|%s" % (o["model"], o["case"], o["reading"])))
    J = json.load(open("out/rewrite/classify.json"))
    V = [("a", "original specific request", INK, "o", True), ("c", "open request + one clause", BLUE, "o", False),
         ("b", "rewritten as one interpretation", RED_L, "s", True), ("d", "rewritten as a standalone question", RED, "^", True)]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(W, 2.18), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.95})
    rows = M + ["pooled"]; y = np.arange(len(rows))[::-1]
    for (v, lab, col, mk, fill), o in zip(V, [0.24, 0.08, -0.08, -0.24]):
        for name, yy in zip(rows, y):
            rs = [r for m, r, _k in R if name == "pooled" or m == name]; k = sum(r[v] for r in rs); n = len(rs); val = pct(k, n)
            ax.errorbar(val, yy + o, xerr=err(wilson(k, n), val) if name == "pooled" else None, fmt=mk, ms=3.2, color=col, mfc=col if fill else "none", mec=col, mew=0.8, lw=0.7, capsize=1.0)
    ax.axhline(0.5, color="#BBBBBB", lw=0.5, ls=":")
    ax.set_yticks(y); ax.set_yticklabels([LABEL.get(r, "Pooled") for r in rows]); ax.set_xlim(55, 100); ax.set_xlabel("interpretations computed right (%)")
    lost = collections.Counter((J.get(k) or {}).get("lost", "other") for _m, r, k in R if r["a"] and not r["b"])
    order = [c for c, _n in lost.most_common()]; tot = sum(lost.values())
    bx.barh(np.arange(len(order))[::-1], [pct(lost[c], tot) for c in order], color=GRAY_L, height=0.62, **EDGE)
    bx.set_yticks(np.arange(len(order))[::-1]); bx.set_yticklabels(order); bx.set_xlabel("rewrite failures (%)"); bx.set_xlim(0, 40)
    h = [Line2D([], [], marker=mk, ls="", color=col, mfc=col if f else "none", mec=col, ms=3.2, label=lab) for _v, lab, col, mk, f in V]
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=6.5, handletextpad=0.3)
    save(fig, "rewrite")


IMPACT_ROWS = [("boundary", "bound inclusive"), ("count_unit", "rows vs entities"), ("ties", "ties at extreme"),
               ("null_filter", "missing values"), ("join_kind", "unmatched rows")]


def impact():
    """How far the unstated interpretation moves the answer on BIRD dev: per choice type, the library edit applied to the reference SQL of
    silent questions. Stacked share of all such questions whose answer changes, split by how far a single value moves."""
    K = d("fig_impact")["BIRD dev"]["kinds"]
    segs = [("single value moves > 50%", BLUE, lambda r: r["gt50"]), ("moves 10–50%", BLUE_M, lambda r: r["gt10"] - r["gt50"]),
            ("other change", BLUE_L, lambda r: r["changed"] - r["gt10"])]
    rows = sorted(IMPACT_ROWS, key=lambda kr: K[kr[0]]["changed"] / K[kr[0]]["edits"])
    fig, ax = plt.subplots(figsize=(2.98, 1.8))
    for y, (key, lab) in enumerate(rows):
        r = K[key]; left = 0
        for _l, c, f in segs:
            v = pct(f(r), r["edits"]); ax.barh(y, v, left=left, color=c, height=0.62, **EDGE); left += v
        ax.text(left + 1, y, "%.0f%%" % left, va="center", ha="left", fontsize=6.5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([lab for _k, lab in rows], fontsize=6.8)
    ax.set_xlim(0, 60); ax.set_xticks([0, 20, 40, 60]); ax.set_xlabel("% of silent questions whose answer changes")
    ax.tick_params(axis="y", length=0)
    ax.legend(handles=[Patch(facecolor=c, label=l, **EDGE) for l, c, _f in segs], loc="lower center", bbox_to_anchor=(0.36, 1.0), ncol=3, fontsize=6.3,
              handlelength=0.9, handletextpad=0.35, columnspacing=0.8)
    save(fig, "impact")


def outcomes():
    """Every open request of the accepted sets, by what the response did (single call with explanation)."""
    A = d("accepted")["scopes"]["accepted"]["models"]
    seg = [("both", "both interpretations returned", BLUE_M), ("named_one", "choice named, one interpretation", BLUE_L),
           ("silent_computable", "silent, both computable", RED_L), ("not_computable", "a specific request computed wrong", GRAY_L),
           ("no_run", "a specific answer does not run", GRAY_XL)]
    fig, ax = plt.subplots(figsize=(W, 1.45)); ys = list(range(len(M)))[::-1]
    for m, y in zip(M, ys):
        o = A[m]["outcomes"]; n = sum(o.values()); left = 0
        for k, _l, c in seg:
            v = pct(o[k], n); ax.barh(y, v, left=left, color=c, height=0.66, **EDGE)
            if v >= 6: ax.text(left + v / 2, y, str(o[k]), ha="center", va="center", fontsize=6.5)
            left += v
    ax.set_yticks(ys); ax.set_yticklabels([LABEL[m] for m in M]); ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("%% of %d open requests" % d("accepted")["scopes"]["accepted"]["n"]); ax.tick_params(axis="y", length=0)
    ax.legend(handles=[Patch(facecolor=c, label=l, **EDGE) for _k, l, c in seg], loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, fontsize=6.5,
              handlelength=0.9, handletextpad=0.35, columnspacing=1.0)
    save(fig, "outcomes")


def conventions():
    """Main answer to the open request on the 61 accepted tie and counting sets: the interpretation BIRD and Spider references take by
    convention, the other interpretation, or neither (single call with explanation)."""
    A = d("conventions")["models"]
    seg = [("conventional", "benchmark convention", BLUE_M), ("other", "other interpretation", RED_L), ("neither", "neither interpretation", GRAY_L)]
    fig, ax = plt.subplots(figsize=(W, 1.35)); ys = list(range(len(M)))[::-1]
    for m, y in zip(M, ys):
        o = A[m]; n = sum(o.get(k, 0) for k, _l, _c in seg); left = 0
        for k, _l, c in seg:
            v = pct(o.get(k, 0), n); ax.barh(y, v, left=left, color=c, height=0.66, **EDGE)
            if v >= 6: ax.text(left + v / 2, y, str(o.get(k, 0)), ha="center", va="center", fontsize=6.5)
            left += v
    ax.set_yticks(ys); ax.set_yticklabels([LABEL[m] for m in M]); ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("%% of %d open requests (tie and counting sets)" % d("conventions")["sets"]); ax.tick_params(axis="y", length=0)
    ax.legend(handles=[Patch(facecolor=c, label=l, **EDGE) for _k, l, c in seg], loc="lower center", bbox_to_anchor=(0.42, 1.0), ncol=3, fontsize=6.5,
              handlelength=0.9, handletextpad=0.35, columnspacing=1.0)
    save(fig, "conventions")


# ---------------------------------------------------------------- both readings returned, by choice type
def bytype():
    """Per choice type (at least five accepted sets): open requests answered with both interpretations, among the sets in which the same
    model answers both specific requests right (fig5 by_group/type, the same counts as the former rows of Table 1)."""
    f = d("fig5_tab4_disclosure")["models"]
    T = [("value_representation", "strict or inclusive cutoff"), ("aggregation_level", "aggregation level"), ("missing_values", "missing values"),
         ("counting_unit", "counting unit"), ("tie", "ties")]
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(W, 2.75), gridspec_kw={"height_ratios": [5, 3]}); y = np.arange(len(T))[::-1]; off = {m: (1.5 - i) * 0.15 for i, m in enumerate(M)}
    for (t, _l), yy in zip(T, y):
        for m in M:
            g = f[m]["by_group"]["type"][t]; v = pct(g["k"], g["n"])
            ax.errorbar(v, yy + off[m], xerr=err(wilson(g["k"], g["n"]), v), fmt="o", ms=3.2, color=COL[m], lw=0.7, capsize=1.0)
    ax.set_yticks(y); ax.set_yticklabels(["%s (%d)" % (l, f[M[0]]["by_group"]["type"][t]["sets"]) for t, l in T]); ax.set_xlim(0, 100)
    ax.set_xticklabels([]); ax.set_title("by choice type", fontsize=7, pad=2, loc="left")
    SRC = ["Spider", "BIRD", "LiveSQLBench"]; y2 = np.arange(len(SRC))[::-1]
    for t, yy in zip(SRC, y2):
        for m in M:
            g = f[m]["by_group"]["source"][t]; v = pct(g["k"], g["n"])
            bx.errorbar(v, yy + off[m], xerr=err(wilson(g["k"], g["n"]), v), fmt="o", ms=3.2, color=COL[m], lw=0.7, capsize=1.0)
    bx.set_yticks(y2); bx.set_yticklabels(["%s (%d)" % (t, f[M[0]]["by_group"]["source"][t]["sets"]) for t in SRC]); bx.set_xlim(0, 100); bx.set_ylim(-0.5, len(SRC) - 0.5)
    bx.set_title("by source of the database", fontsize=7, pad=2, loc="left"); bx.set_xlabel("both interpretations returned (%)")
    h = [Line2D([], [], marker="o", ls="", color=COL[m], ms=3.2, label=LABEL[m]) for m in M]
    bx.legend(handles=h, loc="upper center", bbox_to_anchor=(0.4, -0.45), ncol=4, fontsize=6.5, handletextpad=0.2)
    fig.tight_layout(h_pad=0.6); save(fig, "bytype")


# ---------------------------------------------------------------- choice types at a glance (full page width)
def choices():
    """Figure* of the choice types: each row gives the choice, one open phrase with its two interpretations (A blue, B orange, the
    diagram colors), and three bar panels: choices found in benchmark failures (open / settled), the share of silent BIRD and
    Spider references that take the rarer interpretation, and the accepted request sets. Same counts as supplement Table librarydetail."""
    from specbridge.report import numbers as N
    LIB, REF, VS = N.LIB(), N.REF(), N.P("tab2_library")["value_split"]
    MAJ = ("aggregation_level", "ties_and_selection", "counting_unit", "missing_values", "referent_column")
    rest = lambda k: sum(v[k] for t, v in LIB.items() if t in N.LIB13 and t not in MAJ and t != "value_representation") + VS["value_matching"]["raise" if k == "raise" else "settled"]
    other_sets = N.P("fig5_tab4_disclosure")["n_families"] - sum(N.sets_of(t) for t in ("aggregation_level", "ties_and_selection", "counting_unit", "missing_values", "value_representation"))
    R = [("Aggregation level", "rows or group averages?", "“average standings points at races held there”", "pool all records", "average each race first",
          LIB["aggregation_level"]["raise"], LIB["aggregation_level"]["settled_from_failures"], REF["aggregation_level"], N.sets_of("aggregation_level")),
         ("Strict cutoff", "strict or inclusive?", "“using 0.149 as the cutoff”", "greater than 0.149", "at least 0.149",
          VS["strict_cutoff"]["raise"], VS["strict_cutoff"]["settled"], REF["strict_cutoff"], N.sets_of("value_representation")),
         ("Ties", "one tied row, or all?", "“the top 10 telescopes by share of signals”", "exactly ten rows", "every telescope tied with the tenth",
          LIB["ties_and_selection"]["raise"], LIB["ties_and_selection"]["settled_from_failures"], REF["ties_and_selection"], N.sets_of("ties_and_selection")),
         ("Counting unit", "rows or entities?", "“how many manager award winners”", "distinct managers", "award records",
          LIB["counting_unit"]["raise"], LIB["counting_unit"]["settled_from_failures"], REF["counting_unit"], N.sets_of("counting_unit")),
         ("Missing values", "keep or skip missing?", "“group members by their major”", "no major is its own group", "members without a major left out",
          LIB["missing_values"]["raise"], LIB["missing_values"]["settled_from_failures"], REF["missing_values"], N.sets_of("missing_values")),
         ("Referent column", "which column is meant?", "“schools in Riverside”", "the district field", "the county or the city field",
          LIB["referent_column"]["raise"], LIB["referent_column"]["settled_from_failures"], None, N.sets_of("referent_column")),
         ("Seven other types", "e.g. conditions on one record?", "", "", "", rest("raise"), rest("settled_from_failures"), None, other_sets)]
    A_C, B_C = "#3A6AA8", "#B07800"
    fig = plt.figure(figsize=(7.0, 2.9)); n = len(R); top, rowh = 0.85, 0.115
    ys = [top - (i + 0.5) * rowh for i in range(n)]
    T = fig.add_axes([0, 0, 1, 1]); T.axis("off"); T.set_xlim(0, 1); T.set_ylim(0, 1)
    hdr = dict(fontsize=7.5, fontweight="bold", va="bottom")
    T.text(0.005, top + 0.01, "Choice type", **hdr); T.text(0.165, top + 0.01, "Example open phrase", **hdr)
    T.text(0.36, top + 0.01, "One\ninterpretation", linespacing=1.0, **hdr); T.text(0.485, top + 0.01, "Other\ninterpretation", linespacing=1.0, **hdr)
    for i, (name, q, ph, a, b, *_r) in enumerate(R):
        y = ys[i]
        T.plot([0, 0.6], [y - rowh / 2] * 2, color="#BBBBBB", lw=0.4)
        T.text(0.005, y + 0.018, name, fontsize=7.5, fontweight="bold", va="center")
        T.text(0.005, y - 0.025, q, fontsize=6.8, va="center")
        T.text(0.165, y, "\n".join(textwrap.wrap(ph, 30)), fontsize=6.8, va="center")
        T.text(0.36, y, "\n".join(textwrap.wrap(a, 22)), fontsize=6.8, va="center")
        T.text(0.485, y, "\n".join(textwrap.wrap(b, 22)), fontsize=6.8, va="center")
    y0, y1 = top - n * rowh, top
    def panel(x0, w, title):
        ax = fig.add_axes([x0, y0, w, y1 - y0]); ax.set_ylim(top - n * rowh, top); ax.set_yticks([]); ax.patch.set_alpha(0)
        T.text(x0, top + 0.01, title, fontsize=7.5, fontweight="bold", va="bottom", linespacing=1.0); ax.tick_params(axis="x", labelsize=6.5); return ax
    a1 = panel(0.615, 0.115, "Found in failures\nopen + settled"); a2 = panel(0.765, 0.12, "References taking\nthe rarer\ninterpretation"); a3 = panel(0.92, 0.07, "Request\nsets")
    h = rowh * 0.5
    for i, (_n, _q, _p, _a, _b, op, st, ref, sets) in enumerate(R):
        y = ys[i]
        a1.barh(y, op, h, color=GRAY, **EDGE); a1.barh(y, st, h, left=op, color="white", **EDGE)
        a1.text(op + st + 0.8, y, "%d + %d" % (op, st), fontsize=6.2, va="center")
        if ref is None: a2.text(0.3, y, "not readable" if _n == "Referent column" else "", fontsize=6.2, va="center")
        else:
            sh = pct(ref[1], sum(ref)); a2.barh(y, sh, h, color=GRAY, **EDGE)
            a2.text(sh + 0.4, y, "%.1f%% of %s" % (sh, format(sum(ref), ",")), fontsize=6.2, va="center")
        if sets: a3.barh(y, sets, h, color=GRAY, **EDGE)
        a3.text(sets + 1.5, y, "%d" % sets, fontsize=6.2, va="center")
    a1.set_xlim(0, 52); a1.set_xticks([0, 20, 40]); a2.set_xlim(0, 29); a2.set_xticks([0, 5, 10, 15]); a2.set_xlabel("% of silent questions", fontsize=6.5, labelpad=1)
    a3.set_xlim(0, 80); a3.set_xticks([0, 30, 60]); a1.set_xlabel("choices", fontsize=6.5, labelpad=1); a3.set_xlabel("sets", fontsize=6.5, labelpad=1)
    save(fig, "choices", width=7.0)


# ---------------------------------------------------------------- what each construction stage keeps
def funnel():
    """Request-set construction as a funnel. Every stage counts both runs of the same pipeline: the generated tasks
    (tab3_generation funnel) and the tasks given a filter condition (out/transfer/ext: cp inventory, selection, render)."""
    from specbridge.report import numbers as N
    G = N.P("tab3_generation")["funnel"]; inv = lambda i: int(G["inventory"].split("|")[i + 2].strip())
    E = [r for r in open("out/transfer/ext/cp/INVENTORY.md") if r.startswith("| all ")][0].split("|")
    ex = lambda i: int(E[i + 2].strip())
    sel = len(json.load(open("out/transfer/ext/render/selection.json"))); fil = sum(N.FIL()["verdicts"].values())
    F5 = N.P("fig5_tab4_disclosure")
    S = [("choices proposed", inv(1) + ex(1)), ("the other interpretation changes the answer", inv(2) + ex(2)),
         ("both interpretations described exactly", inv(3) + ex(3)), ("a reviewer model finds it open", inv(4) + inv(5) + ex(4) + ex(5)),
         ("one choice kept per task", G["selected"] + sel), ("requests pass all checks", G["frozen"] + fil),
         ("both authors find it open", N.P("accepted")["scopes"]["accepted_all_types"]["n"]),
         ("other interpretation in \u22651% of references", F5["n_families"])]
    fig, ax = plt.subplots(figsize=(W, 1.95)); y = np.arange(len(S))[::-1]
    for (lab, v), yy in zip(S, y):
        last = lab.startswith("other interpretation")
        ax.barh(yy, v, 0.62, color=BLUE if last else BLUE_L, **EDGE)
        ax.text(v + 10, yy, "%d" % v, va="center", fontsize=6.8, fontweight="bold" if last else "normal")
    ax.set_yticks(y); ax.set_yticklabels([l for l, _v in S]); ax.set_xlim(0, 980); ax.set_xlabel("count")
    save(fig, "funnel")


ALL = [funnel, choices, bytype, coverage, ablation, specification, real, causes, disclosure, outcomes, defaults, impact, method, decomposition, rewrite, conventions]
if __name__ == "__main__":
    for fn in ([globals()[a] for a in sys.argv[1:]] or ALL): fn()
