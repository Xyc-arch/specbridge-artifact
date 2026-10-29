"""MANUSCRIPT TABLES GENERATED FROM DATA (model-free): out/paper/data + saved runs -> its region in paper/tex/specbridge.tex (+ a copy in out/paper/tables/<name>.tex)
    python -m specbridge.report.tables_tex [name ...]
main_results: every accuracy-type result of the paper, conditions x solvers, one column wide.
note_breakdown: the defaults-note experiment by BIRD difficulty and by database.
conventions: author defaults per group (share of silent questions read the usual way) with the share against it."""
import collections, json, math, os, re, sys
sys.path.insert(0, ".")
DATA, TAB, PAPER = "out/paper/data", "out/paper/tables", "paper/tex/specbridge.tex"
TARGET = {}      # table name -> file, for tables that live in the supplement
CHECKLIST = "out/transfer/eval12-v2/render/disclose/incontext/results.json"
TOPK = "out/transfer/all/render/disclose/topk/results.json"
M = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
LABEL = {"haiku": "Haiku", "sonnet": "Sonnet", "gpt-6-sol": "GPT-Sol", "gpt-6-luna": "GPT-Luna"}
d = lambda n: json.load(open("%s/%s.json" % (DATA, n)))
pc = lambda k, n: 100.0 * k / n


def write(name, body):
    """The table goes into its region of the paper (paper/tex/specbridge.tex, one file); a copy is kept in out/paper/tables/."""
    from specbridge.report.texfile import splice
    os.makedirs(TAB, exist_ok=True); open("%s/%s.tex" % (TAB, name), "w").write(body)
    splice(TARGET.get(name, PAPER), "table " + name, body)
    print("table", name)


def cells(vals, fmt="%.1f", low=False):
    """Bold the best value of a row (ties all bold; low=True: the lowest is best); None -> --."""
    best = (min if low else max)(v for v in vals if v is not None)
    return [("--" if v is None else ("\\textbf{%s}" % (fmt % v) if abs(v - best) < 1e-9 else fmt % v)) for v in vals]


def main_results():
    f2, f3, f5, f6 = d("fig2_explicit_vs_precise"), d("fig3_real_benchmarks"), d("fig5_tab4_disclosure"), d("fig6_inclination")
    C = f3["confirmation"]
    rows = []   # (group, label, n, [values per solver])
    rows.append(("Generated tasks (12 DBs)", "exact description", f2["n_tasks"], [pc(*f2["overall"][m]["explicit"]) for m in M]))
    rows.append(("", "natural request", f2["n_tasks"], [pc(*f2["overall"][m]["precise_v2"]) for m in M]))
    for split, name in (("bird_heldout100", "BIRD held-out"), ("spider_confirm50", "Spider held-out")):
        n = C[split]["n"]
        rows.append((name, "original question", n, [pc(*C[split][m]["original_strict"]) for m in M]))
        rows.append(("", "\\quad extra columns allowed", n, [pc(*C[split][m]["original_shape"]) for m in M]))
        rows.append(("", "exact description of reference", n, [pc(*C[split][m]["explicit_strict"]) for m in M]))
    nf = f5["n_families"]; F = f5["models"]
    rows.append(("Request sets (%d), scored by execution" % nf, "specific request right", nf, [pc(F[m]["precise_correct"]["k"], F[m]["precise_correct"]["n"]) for m in M]))
    rows.append(("", "open request: A or B", nf, [pc(F[m]["open_admissible"]["k"], F[m]["open_admissible"]["n"]) for m in M]))
    rows.append(("", "returns both A and B", nf, [pc(F[m]["covers_both"]["k"], F[m]["covers_both"]["n"]) for m in M]))
    rows.append(("", "\\quad if both specific right", "%d--%d" % (min(F[m]["covers_both_given_both_precise"]["n"] for m in M), max(F[m]["covers_both_given_both_precise"]["n"] for m in M)), [pc(F[m]["covers_both_given_both_precise"]["k"], F[m]["covers_both_given_both_precise"]["n"]) for m in M]))
    rng = lambda ns: ("%d" % ns[0]) if min(ns) == max(ns) else "%d--%d" % (min(ns), max(ns))
    A = d("accepted")["scopes"]["accepted"]["models"]; T = json.load(open(TOPK))["models"]
    rows.append(("Request sets, judged by a model", "names the open choice", nf, [pc(F[m]["recognises"]["k"], F[m]["recognises"]["n"]) for m in M]))
    rows.append(("", "stated interpretation matches SQL", rng([F[m]["faithful_given_stated"]["n"] for m in M]), [pc(F[m]["faithful_given_stated"]["k"], F[m]["faithful_given_stated"]["n"]) for m in M]))
    rows.append(("", "settled request called open", nf, [pc(F[m]["false_open"]["k"], F[m]["false_open"]["n"]) for m in M], True))
    rows.append(("Request sets, median seconds per request", "SQL only", nf, [F[m]["overhead"]["median_seconds_plain"] for m in M], True))
    rows.append(("", "SQL and explanation", nf, [F[m]["overhead"]["median_seconds_disclosure"] for m in M], True))
    L = ["\\begin{table}[t]",
         "\\caption{Results per model, in \\% of $n$ questions or request sets ($n$ is a range when it differs by model). Generated tasks, benchmark questions and the row ``if both specific right'' let the model explore the database first; the other rows use one call. Bold: best in the row (lowest for false alarms and time).}",
         "\\label{tab:main}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{3.2pt}", "\\renewcommand{\\arraystretch}{1.05}",
         "\\begin{tabular}{@{}llrrrrr@{}}", "\\toprule", "& Condition & $n$ & Haiku & Sonnet & GPT-Sol & GPT-Luna\\\\", "\\midrule"]
    first = True
    for row in rows:
        grp, lab, n, vals = row[:4]; low = len(row) > 4 and row[4]
        if grp and not first: L.append("\\midrule")
        first = False
        if grp: L.append("\\multicolumn{7}{@{}l}{\\textit{%s}}\\\\" % grp)
        L.append("& %s & %s & %s\\\\" % (lab, "" if n is None else n, " & ".join(cells(vals, low=low))))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("main_results", "\n".join(L) + "\n")


def note_breakdown():
    """Base rates for all 600 (two rows), then the gain in points by BIRD difficulty and by database; one column per solver."""
    from specbridge.comm.diagnose import prior as P
    T = P.tasks(); E = d("fig6_inclination")["note_experiment"]["models"]; ms = [m for m in M if m in E]
    R = {}
    for m in ms:
        base = "%s/runs/%s" % (P.OUT, re.sub(r"\W", "_", m))
        R[m] = {t["id"]: (json.load(open("%s/plain/%s.json" % (base, t["id"])))["pass"], json.load(open("%s/defaults/%s.json" % (base, t["id"])))["pass"]) for t in T}
    rate = lambda m, ts, k: pc(sum(R[m][t["id"]][k] for t in ts), len(ts))
    gain = lambda lab, ts: "%s & %d & %s\\\\" % (lab, len(ts), " & ".join("%+.1f" % (rate(m, ts, 1) - rate(m, ts, 0)) for m in ms))
    L = ["\\begin{table}[t]",
         "\\caption{The defaults note in detail. First two rows: share right (\\%%) on all %d questions with the question only and with the note. "
         "Other rows: the gain in points; \\emph{clean} = the six databases never used in the error analysis, \\emph{overlap} = the five that were; then by BIRD "
         "difficulty and by database. Same runs as Figure~\\ref{fig:note}; per-database samples are small.}" % len(T),
         "\\label{tab:notebreakdown}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{4pt}",
         "\\begin{tabular}{@{}lr" + "r" * len(ms) + "@{}}", "\\toprule",
         "Questions & $n$ & " + " & ".join(LABEL[m] for m in ms) + "\\\\", "\\midrule",
         "all, question only & %d & %s\\\\" % (len(T), " & ".join("%.1f" % rate(m, T, 0) for m in ms)),
         "all, with the note & %d & %s\\\\" % (len(T), " & ".join("%.1f" % rate(m, T, 1) for m in ms)), "\\midrule",
         "\\multicolumn{%d}{@{}l}{\\textit{gain in points}}\\\\" % (2 + len(ms)), gain("all", T)]
    from specbridge.comm.diagnose.tasks import BIRD_DBS
    L.append(gain("clean (6 databases)", [t for t in T if t["database"] not in BIRD_DBS]))
    L.append(gain("overlap (5 databases)", [t for t in T if t["database"] in BIRD_DBS]))
    L.append(gain("\\quad without \\texttt{thrombosis}", [t for t in T if t["database"] in BIRD_DBS and t["database"] != "thrombosis_prediction"]))
    L.append("\\midrule")
    for lev in ("simple", "moderate", "challenging"): L.append(gain(lev, [t for t in T if t["difficulty"] == lev]))
    L.append("\\midrule")
    for db in sorted({t["database"] for t in T}): L.append(gain("\\texttt{%s}" % db.replace("_", "\\_"), [t for t in T if t["database"] == db]))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("note_breakdown", "\n".join(L) + "\n")


def conventions():
    """The four groups of the two benchmarks' own authors; every cell has at least MIN cases (the imported groups, which reverse one
    decision each, are shown in Figure 9 and described in the text, where several decisions arise fewer than 5 times)."""
    MIN = 5
    f = d("fig6_inclination"); G = f["groups"]; K = f["figure_kinds"]
    head = {"ties_and_selection": "Tie", "counting_unit": "Count", "missing_values": "Null", "population_scope": "Join", "boundary_between": "Betw.",
            "boundary_open": "Strict", "text_match": "Text"}
    rows = [("BIRD train", "BIRD train"), ("BIRD dev", "BIRD dev"), ("Spider train (own)", "Spider train"), ("Spider dev", "Spider dev")]
    for g, _n in rows:
        for k in K: assert G[g]["kinds"][k]["n"] >= MIN, (g, k)
    L = ["\\begin{table}[t]",
         "\\caption{Shared defaults of BIRD and Spider: share (\\%%) of silent questions whose reference takes the usual interpretation. Tie: one row at an extreme. Count: rows. Null: no missing-value filter. Join: inner. Betw.: inclusive. Strict: ``after'', ``over'' strict. Text: exact match. Last column: silent questions against the usual interpretation. Cells $\\ge$ %d cases; counts in Appendix~\\ref{sec:disaggregated}.}" % MIN,
         "\\label{tab:conventionscol}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{2.8pt}",
         "\\begin{tabular}{@{}l" + "r" * len(K) + "r@{}}", "\\toprule",
         "Group & " + " & ".join(head[k] for k in K) + " & Against\\\\", "\\midrule"]
    for g, name in rows:
        v = G[g]; sq = v["silent_questions"]
        L.append("%s & %s & %.1f\\\\" % (name, " & ".join("%.0f" % pc(v["kinds"][k]["k"], v["kinds"][k]["n"]) for k in K), pc(sq["against_usual"], sq["n"])))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("conventions", "\n".join(L) + "\n")


# ---- related work: AmbiQT (Bhaskar et al., EMNLP 2023) and AMBROSIA (Saparina and Lapata, NeurIPS D&B 2024), read in
# readings/text2sql_published/pdfs. Which of OUR library kinds their taxonomies cover is our mapping, stated in the caption:
# AmbiQT column/table ambiguity ~ referent_column; AMBROSIA vagueness ~ referent_column, scope ~ comparison_quantifier,
# attachment ~ condition_linkage. AMBROSIA explicitly excludes NULL handling, coverage and output format.
COVERED = {"AmbiQT": {"referent_column"}, "AMBROSIA": {"referent_column", "comparison_quantifier", "condition_linkage"}}


def comparison():
    """Related work: SpecBridge and the two closest benchmarks, numbers and check marks only (the descriptive rows are in the text)."""
    T = {t["type"]: t for t in d("tab2_library")["types"]}
    meaning = {k: v["raise"] for k, v in T.items() if k != "output_form"}
    tot = sum(meaning.values()); either = COVERED["AmbiQT"] | COVERED["AMBROSIA"]
    cov = lambda ks: sum(meaning.get(k, 0) for k in ks)
    outside = sorted((k for k in meaning if k not in either and meaning[k]), key=lambda k: -meaning[k])
    from specbridge.comm.transfer import freeze as FZ   # types the request sets test: the kept types that have accepted sets
    C = json.load(open(FZ.FRZ))["cases"]; A = set(json.load(open(FZ.FROZEN))["accepted"]) if os.path.exists(FZ.FROZEN) else set()
    tested = {FZ.SET_TYPE.get(c["type"], c["type"]) for c in C if c["case"] in A}   # cutoff sets test strict cutoffs, not value matching
    L = ["\\begin{table}[t]",
         "\\caption{\\system{} and the two closest benchmarks of ambiguous text-to-SQL. Schema: synonym or split columns and tables; wording: scope, attachment, vagueness; calculation: ties, counting units, missing values, aggregation level. Mined: in our library of choices from benchmark failures, but not built into the request sets we test here.}",
         "\\label{tab:comparison}", "\\centering\\footnotesize", "\\providecommand{\\cm}{\\ensuremath{\\checkmark}}\\providecommand{\\xm}{\\ensuremath{\\times}}", "\\setlength{\\tabcolsep}{3.5pt}",
         "\\begin{tabular}{@{}lccc@{}}", "\\toprule",
         "& AmbiQT~\\cite{ambiqt2023} & AMBROSIA~\\cite{ambrosia2024} & \\system{}\\\\", "\\midrule",
         "Choices in the schema & \\cm & \\xm & mined\\\\",
         "Choices in the wording & \\xm & \\cm & mined\\\\",
         "Choices in the calculation & \\xm & \\xm & \\cm\\\\",
         "\\midrule",
         "Benchmark databases, unmodified & \\xm & \\xm & \\cm\\\\",
         "Measures reference conventions & \\xm & \\xm & \\cm\\\\",
         "One request per interpretation & \\xm & \\cm & \\cm\\\\",
         "Separates computing from reporting & \\xm & \\xm & \\cm\\\\",
         "Checks the stated interpretation & \\xm & \\xm & \\cm\\\\",
         "Penalizes raising a settled choice & \\xm & \\xm & \\cm\\\\",
         "\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("comparison", "\n".join(L) + "\n")
    print("  kinds outside both taxonomies:", {k: meaning[k] for k in outside}, "sum", cov(outside), "of", tot)

def decomposition():
    """Open requests not covered (both interpretations not returned), and the share of them where the same solver answers BOTH specific requests
    right: (1) specific requests with exploration, (2) the same on the sets both reviewers accept, (3) matched: specific requests in the
    same single call as the open request (specbridge.comm.transfer.matched), when complete."""
    f = d("fig5_tab4_disclosure"); F = f["models"]; n = f["n_families"]
    have_matched = all("matched" in F[m]["decomposition"] for m in M)
    sh = lambda x: "%d/%d (%.0f\\%%)" % (x["both_specific_right"], x["not_covered"], pc(x["both_specific_right"], x["not_covered"]))
    cols = ["exploration", "both reviewers"] + (["matched single call"] if have_matched else [])
    L = ["\\begin{table}[t]",
         "\\caption{Missed interpretations the solver can compute. Among open requests not answered with both interpretations, the share where the same solver answers \\emph{both} specific requests right, under three settings for the specific requests.}",
         "\\label{tab:decomposition}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
         "\\begin{tabular}{@{}l" + "r" * len(cols) + "@{}}", "\\toprule",
         "& \\multicolumn{%d}{c}{both specific right / open not covered}\\\\" % len(cols), "\\cmidrule(l){2-%d}" % (1 + len(cols)),
         "Solver & " + " & ".join(cols) + "\\\\", "\\midrule"]
    for m in M:
        D_ = F[m]["decomposition"]
        cells = [sh(D_["exploration"]["all"]), sh(D_["exploration"]["mutual"])] + ([sh(D_["matched"]["all"])] if have_matched else [])
        L.append("%s & %s\\\\" % (LABEL[m], " & ".join(cells)))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("decomposition", "\n".join(L) + "\n")


WRITER_SWAP = "out/writer_swap/calib200/results.json"     # specbridge.comm.construct.writer_swap report


def writer_swap():
    """Writer self-preference ablation: a random subsample re-written by GPT-Sol under the same pipeline; per solver the score on each
    version, the writer effect, and the home advantages against the neutral solvers (Haiku, GPT-Luna)."""
    r = json.load(open(WRITER_SWAP)); E, A, n = r["estimates"], r["calibration_accuracy"], r["n_calibration"]
    ci = lambda k: ("%+.1f [%+.1f, %+.1f]" % (E[k]["points"], E[k]["ci95"][0], E[k]["ci95"][1])).replace("-", "$-$")
    L = ["\\begin{table}[t]",
         "\\caption{Does the request writer favor itself? On %d random tasks, GPT-Sol rewrites the request under the same pipeline. Change: accuracy on Sonnet-written minus GPT-Sol-written requests (points, paired 95\\%% CI). Home advantage: a writer's change minus the mean change of the two models that wrote neither.}" % n,
         "\\label{tab:writerswap}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
         "\\begin{tabular}{@{}lrrr@{}}", "\\toprule",
         "Solver & Sonnet-written & GPT-Sol-written & Change \\\\", "\\midrule"]
    for m in M:
        a = A[m]; L.append("%s & %d/%d & %d/%d & %s\\\\" % (LABEL[m], a["sonnet_written"], n, a["gpt-6-sol_written"], n, ci("d_" + m)))
    L += ["\\midrule",
          "\\multicolumn{3}{@{}l}{Home advantage, Sonnet ($p=%.2f$)} & %s\\\\" % (E["h_sonnet"]["p"], ci("h_sonnet")),
          "\\multicolumn{3}{@{}l}{Home advantage, GPT-Sol ($p=%.2f$)} & %s\\\\" % (E["h_gpt-6-sol"]["p"], ci("h_gpt-6-sol")),
          "\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("writer_swap", "\n".join(L) + "\n")


def checklist():
    """In-context personalization vs a same-length style placebo (specbridge.comm.transfer.checklist), split by the benchmark each
    database comes from: open requests with both interpretations (placebo -> personalized), exact McNemar per cell, pooled sign-flip per column,
    and main SQL right on the specific request."""
    r = json.load(open(CHECKLIST)); S = dict(r["by_source"], Overall={"models": r["models"], "pooled": r["pooled"]})
    cols = ["BIRD", "Spider", "LiveSQLBench", "Overall"]; star = lambda v: "$^{*}$" if v < 0.05 else ""
    sets = {c: S[c]["models"][M[0]]["n"] for c in cols}
    L = ["\\begin{table}[t]",
         "\\caption{Personalization against a placebo, on %d request sets drawn at random, split by the benchmark each database comes from. "
         "Both arms use the explanation call with one block added before the schema: the choices this user wants raised (personalized), "
         "or the same length and procedure about the user's SQL writing style (placebo). The arms ran interleaved. Cells: open requests "
         "whose answer returns both interpretations, placebo $\\rightarrow$ personalized; $^{*}$ exact McNemar $p<0.05$. Gain: pooled over solvers, "
         "in points, with sign-flip $p$. Specific: main SQL right on the sets' specific requests, summed over solvers.}" % r["n_sets"],
         "\\label{tab:checklist}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
         "\\begin{tabular}{@{}lrrrr@{}}", "\\toprule",
         "Solver & " + " & ".join("%s (%d)" % (c, sets[c]) for c in cols) + " \\\\", "\\midrule"]
    for m in M:
        L.append(LABEL[m] + " & " + " & ".join("%d$\\rightarrow$%d%s" % (S[c]["models"][m]["placebo"], S[c]["models"][m]["check"], star(S[c]["models"][m]["p"])) for c in cols) + " \\\\")
    g = lambda c: ("%+.1f" % (100 * S[c]["pooled"]["mean_diff"])).replace("-", "$-$")
    gp = lambda c: "%.4f" % S[c]["pooled"]["p"]
    sp = lambda c: "%d$\\rightarrow$%d" % tuple(sum(S[c]["models"][m][k] for m in M) for k in ("right_placebo", "right_check"))
    L += ["\\midrule", "Gain & " + " & ".join(g(c) for c in cols) + " \\\\", "Gain $p$ & " + " & ".join(gp(c) for c in cols) + " \\\\", "Specific & " + " & ".join(sp(c) for c in cols) + " \\\\",
          "\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("checklist", "\n".join(L) + "\n")

def method_ambrosia():
    """Section 5: the disclosure method on AMBROSIA's fresh test questions, per solver and arm, plus the pooled paired differences."""
    J = json.load(open("out/ambrosia/final/final.json")); NAME = {"plain": "Plain", "dtp": "DtP", "samplek": "Three samples", "ours": "Ours"}
    L = ["\\begin{table}[t]",
         "\\caption{Disclosure method on 150 fresh AMBROSIA test questions per solver (90 ambiguous, 60 unambiguous), shape-tolerant. "
         "Recovered: of the interpretations the plain answer missed that the solver computes when asked the unambiguous version. Precision on "
         "unambiguous questions. Bottom: ours minus each arm, pooled over both solvers, paired 95\\% bootstrap intervals (points).}",
         "\\label{tab:method}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{2.0pt}",
         "\\begin{tabular}{@{}llrrrrr@{}}", "\\toprule", "& Arm & AllFound & Recall & Recovered & Precision & Calls / kchars \\\\", "\\midrule"]
    for m, lab in (("sonnet", "Sonnet"), ("gpt-6-sol", "GPT-Sol")):
        x = J["solvers"][m]; first = True
        for a in ("plain", "dtp", "samplek", "ours"):
            v = x["arms"][a]; b = "\\textbf{%s}" if a == "ours" else "%s"
            L.append("%s & %s & %d & %.2f & %d/%d & %s & %.1f / %.1f \\\\" % (lab if first else "", b % NAME[a], v["allfound"], v["recall"], v["recovered"], x["computable"],
                     b % ("%.2f" % v["precision"]), v["calls"], v["chars_in"] / 1000)); first = False
        L.append("\\addlinespace")
    est = lambda t: ("%+.1f" % (100 * t[0])).replace("-", "$-$"); iv = lambda t: ("[%+.1f, %+.1f]" % (100 * t[1], 100 * t[2])).replace("-", "$-$")
    L.append("\\midrule")
    for k, lab in (("vs_dtp", "Ours $-$ DtP"), ("vs_samplek", "Ours $-$ Sample-3")):
        P = J["pooled"][k]
        L.append("\\multicolumn{2}{@{}l}{%s} & %s & %s & %s & %s & \\\\" % (lab, est(P["allfound"]), est(P["recall"]), est(P["recovered"]), est(P["precision"])))
        L.append("& & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize %s} & \\\\" % (iv(P["allfound"]), iv(P["recall"]), iv(P["recovered"]), iv(P["precision"])))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("method_ambrosia", "\n".join(L) + "\n")


def method_reqsets():
    """Section 5: the same arms on 30 development request sets (data-side choices). One row per arm; each cell Sonnet / GPT-Sol."""
    J = json.load(open("out/reqmethod/results.json")); NAME = {"plain": "Plain", "samplek": "Three samples", "dtp": "DtP", "ours": "Ours", "ours+lib": "Ours + library edits"}
    S, G = J["sonnet"], J["gpt-6-sol"]; pair = lambda f: "%s / %s" % (f(S), f(G))
    L = ["\\begin{table}[t]",
         "\\caption{The same four methods on %d development request sets; each cell gives Sonnet / GPT-Sol. Both: the open request's answers include "
         "both interpretations. Names: the response names the choice built into the set (Opus judge, blind to method and model). Recovered: of the %d interpretations per model "
         "that the plain answer missed but the model computes when asked. Right: specific requests answered correctly (of %d). Calls: per request.}" % (S["sets"], S["computable"], S["sets"]),
         "\\label{tab:methodsets}", "\\centering\\footnotesize", "\\setlength{\\tabcolsep}{3.5pt}",
         "\\begin{tabular}{@{}lccccc@{}}", "\\toprule", "Method & Both & Names & Recovered & Right & Calls \\\\", "\\midrule"]
    for a in ("plain", "samplek", "dtp", "ours", "ours+lib"):
        c = lambda x: x["arms"][a]["cost"].split(" /")[0].replace("saved", "1")
        L.append("%s & %s & %s & %s & %s & %s \\\\" % (NAME[a], pair(lambda x: x["arms"][a]["both"]), pair(lambda x: x["arms"][a]["names"]), pair(lambda x: x["arms"][a]["recovered"]),
                 pair(lambda x: x["arms"][a]["right"]), pair(c)))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("method_reqsets", "\n".join(L) + "\n")

def methods():
    """Section 7: decide-then-answer, its wide-search option (decide-then-search) and four baselines, measured the same way on both
    datasets: coverage (AMBROSIA AllFound; request sets, both interpretations), precision on clear or specific requests, calls.
    out/system/method.json (system.report_method)."""
    M = json.load(open("out/system/method.json")); A, S = M["ambrosia"], M["sets"]
    NAME = {"plain": "Plain", "samplek": "Three samples", "dtp": "DtP", "state": "Interpret-and-state", "ours": "Decide-then-answer", "method": "\\quad Decide-then-search"}
    arms = ("plain", "samplek", "dtp", "state", "ours", "method")
    n_amb = A["sonnet"]["method"]["n_amb"]; n_sets = S["sonnet"]["method"]["sets"]
    L = ["\\begin{table}[t]",
         "\\caption{Decide-then-answer, decide-then-search and four baselines, among them interpret-and-state, the single answer that production assistants return, measured the same way on both datasets: coverage (all interpretations returned, of %d ambiguous AMBROSIA questions and %d open requests), precision on clear or specific requests (\\%%), and calls per request. Bold: best per model.}" % (n_amb, n_sets),
         "\\label{tab:methods}", "\\centering\\footnotesize\\setlength{\\tabcolsep}{3.2pt}",
         "\\begin{tabular}{@{}llrrrrrr@{}}", "\\toprule",
         "& & \\multicolumn{3}{c}{AMBROSIA} & \\multicolumn{3}{c}{Request sets} \\\\", "\\cmidrule(lr){3-5}\\cmidrule(l){6-8}",
         "Model & Method & Cover & Prec. & Calls & Cover & Prec. & Calls \\\\", "\\midrule"]
    for mi, (m, lab) in enumerate((("sonnet", "Sonnet"), ("gpt-6-sol", "GPT-Sol"))):
        if mi: L.append("\\midrule")
        a, r = A[m], S[m]
        col = {"acov": [a[x]["allfound"] for x in arms], "apre": [100 * a[x]["precision"] for x in arms], "acall": [a[x]["calls"] for x in arms],
               "scov": [r[x]["both"] for x in arms], "spre": [r[x]["precision"] for x in arms], "scall": [r[x]["calls"] for x in arms]}
        fmt = {"acov": "%d", "apre": "%.1f", "acall": "%.1f", "scov": "%d", "spre": "%.1f", "scall": "%.1f"}
        C = {k: cells(v, fmt[k], low=k in ("acall", "scall")) for k, v in col.items()}
        for i, x in enumerate(arms):
            L.append("%s & %s & %s \\\\" % (lab if i == 0 else "", NAME[x], " & ".join(C[k][i] for k in ("acov", "apre", "acall", "scov", "spre", "scall"))))
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    write("methods", "\n".join(L) + "\n")


ALL = [comparison, methods]   # 2026-10-24: results per model and the methods comparison are shown as figures (disclosure, real, specification, bytype, method)   # the tables the paper uses; the others are kept as functions only
if __name__ == "__main__":
    for fn in ([globals()[a] for a in sys.argv[1:]] or ALL): fn()
