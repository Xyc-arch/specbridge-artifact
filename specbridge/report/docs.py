"""THE THREE PAPER DOCUMENTS, generated from committed results (model-free).
    python -m specbridge.report.exhibit_data && python -m specbridge.report.methods && python -m specbridge.report.docs
        -> paper/result.md (every result and the data behind every exhibit), paper/example.md (every example),
           and the generated appendices of paper/method.md (parameters, prompts) refreshed between markers.
Example selection rules are stated next to each example."""
import collections, glob, hashlib, json, os, re, sys
sys.path.insert(0, ".")
DATA = "out/paper/data"; EV = "out/corpora/eval12@01cfbb1e713f"; TR = "out/transfer/eval12-v2"
M = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
J = lambda f: json.load(open(f))
d = lambda name: J("%s/%s.json" % (DATA, name))
kn = lambda x: "%d/%d" % (x[0], x[1])
pct = lambda k, n: "%.1f%%" % (100 * k / n) if n else "n/a"
ci = lambda c: "[%.1f, %.1f]" % (100 * c[0], 100 * c[1]) if c and c[0] is not None else ""
fence = lambda s, lang="": "```%s\n%s\n```" % (lang, (s or "").strip())


def table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


# =========================================================================== result.md
def names(xs):
    xs = list(xs); return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
NOTE_SOLVERS = lambda: names(__import__("specbridge.report.explain", fromlist=["LABEL"]).LABEL[m] for m in d("fig6_inclination")["note_experiment"]["models"])


def result():
    from specbridge.report.explain import NICE, LABEL
    from specbridge.report.figures import PLAIN
    f1, t1, f2, f3, t2, t3, f5 = (d(x) for x in ("fig1_coverage", "tab1_construction", "fig2_explicit_vs_precise", "fig3_real_benchmarks", "tab2_library", "tab3_generation", "fig5_tab4_disclosure"))
    L = lambda m: LABEL[m]; MN = [L(m) for m in M]
    typ = lambda t: t.replace("_", " ")
    R = ["# SpecBridge: results",
         "Every result, with the counts behind each figure and table (k/n), 95% intervals and the files they come from. How each was "
         "produced: `method.md` (its \"Terms used throughout\" table defines explicit V, natural question, depth, family and the other terms "
         "used here). Examples: `example.md`. Figure and table explanations: `../out/paper/explain/fig_explain.md`, `tab_explain.md`.",
         "Intervals: resampling tasks or families 2,000 times with the same resample for every condition compared (paired), unless marked "
         "Wilson. Each solver was run once. Solvers: Haiku, Sonnet, GPT-Sol, GPT-Luna.",
         "**Human validation: PENDING** for every number that rests on a model's judgment (audit page "
         "https://claude.ai/artifact/BwD6CcMhmGVwwD6zWuiK8g: 63 natural questions, 40 diagnoses, 47 families, 120 comparison items, 60 "
         "disclosure answers).\n",
         "The results follow the argument: generate diverse programs (R1) -> check that solvers can follow an exact description of them "
         "(R2) -> find, in existing benchmarks, where the original question rather than the computation causes failures (R3, R4) -> "
         "build tests that vary only one unstated decision (R5, R6) -> measure whether solvers notice and communicate that decision (R7) -> "
         "show that each group of authors settles unstated decisions by its own hidden defaults, shared by its train and dev data, and that "
         "telling a solver those defaults raises its score (R8).\n",
         "## Figures and tables",
         "Record figures are in `out/paper/figures/` and record tables in `out/paper/tables/`; the manuscript (`paper/tex/`) has its own figures and tables. All are generated "
         "from `out/paper/data/` by `python -m specbridge.report.figures`; their explanations by `python -m specbridge.report.explain`.\n",
         table(["exhibit", "file", "what it shows", "section", "sample, uncertainty"], [
             ["Fig. 1 Supported features and generator ablation", "`figures/fig1_coverage`", "(a) percentage of databases where each feature is possible by the schema, and where meaningful programs with it were generated; (b) outcome of each attempt when one mechanism of the generator is removed", "R1.1, R1.2", "152 databases; exact counts"],
             ["Tab. 1 Construction and control", "`tables/tab1a_construction`, `tab1b_control`", "programs per source, depth requests, operation weights, required operations, reviewed tasks and natural questions", "R1.3-R1.7", "counts; min-max over 3 seeds"],
             ["Fig. 2 Explicit V vs natural question", "`figures/fig2_specification`", "(a) per database; (b) overall; (c) explicit-V errors by step depth", "R2", "382 tasks; paired intervals; Wilson; within-database shuffle test"],
             ["Fig. 3 Real benchmarks", "`figures/fig3_real_benchmarks`", "(a) original question vs explicit V of the reference, BIRD and Spider; (b) causes of the gap", "R3", "BIRD 96, Spider 50 questions; paired intervals"],
             ["Tab. 2 Decision library", "`tables/tab2_library`", "kinds of decision found in real benchmark questions, with counts and one example each", "R4, example.md E5", "examples"],
             ["Fig. 4 Worked example", "`figures/fig4_worked_example`", "one program, its two readings, the three wordings, the checks and the solvers' answers", "example.md E1", "one family chosen by a stated rule"],
             ["Tab. 3 Building the tests", "`tables/tab3a_funnel`, `tab3b_plan_vs_direct`", "from proposed decisions to frozen families; plan-and-check vs direct generation", "R5", "families; exact McNemar"],
             ["Fig. 5 Disclosure", "`figures/fig5_disclosure`", "per solver: answers right, names the decision, states its reading truthfully, covers both readings", "R7", "215 families; paired intervals"],
             ["Tab. 4-5 Disclosure", "`tables/tab4_disclosure_controls`, `tab5_disclosure_results`", "settled decisions wrongly called open, alternatives, cost against the same call without disclosure", "R7", "exact counts"],
             ["Fig. 6 Hidden defaults", "`figures/fig6_inclination`", "(a) per decision, the reading of silent questions in train vs dev (same authors) and Spider vs imported data (other authors); (b) silent questions against the usual reading; (c) a solver told the authors' defaults vs told nothing (b) train vs dev of the same authors, and Spider vs imported data", "R8", "all BIRD and Spider train and dev reference queries; Wilson; (c) 600 BIRD dev questions, %s, paired" % NOTE_SOLVERS()]]),
         ""]

    # ---------------- R1
    R += ["## R1. Generating programs (Fig. 1, Tab. 1)",
          "*Question:* which kinds of program can the system generate, on how many databases, and does it deliver what is requested? "
          "*Finding:* on 152 databases every feature the data allow can be generated on request; requested depth is delivered exactly and "
          "every program's measured depth equals its target; no program fails an integrity check; weights barely change how often an operation "
          "appears, but requiring it delivers it exactly wherever it is possible.\n",
          "### R1.1 Which features each database supports (Fig. 1)",
          "Possible by the schema = the profiler finds, from column types and table links plus 3 test programs per depth cell on the data, that "
          "the feature can occur (the feature itself is not tried on the data, so this is an upper bound). Possible on the data = programs using "
          "the feature were generated on request and passed every check (below). Databases tried: %d; usable: %d (the other %d have no table "
          "whose rows repeat under another table, so nothing can be aggregated; 5 of the 11 BIRD dev databases are among them). Meaningful = at "
          "least one of those generated programs passed the benchmark review (Opus and Sonnet each alone; both find the meaning coherent and the "
          "answer determined; R1.7). Source: `out/feasibility/`, `out/coverage/ondemand152v2/` (`meaning_ondemand.json` for the review).\n" % (f1["n_tried"], f1["n_buildable"], f1["n_tried"] - f1["n_buildable"])]
    od = f1.get("ondemand") or {}; N = f1.get("ondemand_databases") or f1["n_buildable"]; MEAN = (f1.get("meaning") or {}).get("features") or {}
    R += [table(["feature", "possible by the schema", "possible on the data (generated)", "meaningful (reviewed)", "proven impossible on the data", "undecided", "programs with a defect", "programs delivered / requested", "possible by the schema, 12 evaluation databases"],
                [[NICE.get(k, k), v["supported"], v["generated_on_demand"], MEAN[k]["meaningful"] if MEAN else "pending", v["proven_no_data_valid_program"], v["undetermined"], v["defects_among_delivered"], "%d/%d" % (v["programs_delivered"], v["programs_requested"]), "%.0f%%" % (100 * f1["support_eval12"][k])] for k, v in od.items()]),
          "\nHow \"possible on the data\" was decided: for each database and each feature possible by the schema, 5 programs were requested that "
          "must use the feature. The depth cells where it can occur were tried one by one in a fixed random order, each searched until programs "
          "were found or every possible program had been tried and rejected by the data. A database counts when every delivered program uses the "
          "feature, has measured depth equal to its target and passes the integrity checks. Nothing was left undecided, so the rest are proven "
          "impossible.\n",
          "The schema-level profile is exact for every feature except top-k within group (possible by the schema on %d databases, on the data on "
          "%d): on the other %d every group has 3 or fewer members, so a top-3 cut would keep every row and is refused as trivial. Fewer than 5 "
          "programs (top-k rows: %d of %d) means fewer distinct valid programs exist on those small databases.\n" % (
              od["rank"]["supported"], od["rank"]["generated_on_demand"], od["rank"]["proven_no_data_valid_program"], od["row ranking"]["programs_delivered"], od["row ranking"]["programs_requested"]),
          ("The review removes little except for two features: difference of two measures (meaningful on %d of %d databases) and ratio of two "
          "measures (%d of %d). The reviewers reject subtracting or dividing two quantities whose definitions do not make them comparable. "
          "Review totals: %d programs reviewed, %d accepted; %d database-feature pairs have no accepted program among those generated (not proven "
          "impossible: at most 5 were generated) and %d still had unreviewed programs when the review stopped (8 rounds)." % (
              MEAN["diff"]["meaningful"], MEAN["diff"]["generated"], MEAN["ratio"]["meaningful"], MEAN["ratio"]["generated"], (f1.get("meaning") or {})["programs_reviewed"], (f1.get("meaning") or {})["programs_passing"],
              sum(v["none_among_generated"] for v in MEAN.values()), sum(v["unreviewed"] for v in MEAN.values())) + "\n") if MEAN else ""]
    ab = f1.get("ablation")
    if ab:
        ARMDEF = [("full", "ours (all mechanisms)", "nothing removed"),
            ("-profile", "without the profile", "no column meaning: every numeric column, keys included, is one unit and additive"),
            ("-types", "without type rules", "a difference or ratio may combine different units or kinds; SUM may apply to a non-additive measure"),
            ("-varies", "without 'must vary'", "a row quantity may be constant on the data"),
            ("-restate", "without restatement rules", "a comparison may restate or recompute an existing result; a quantity may be combined with itself"),
            ("-lookahead", "without look-ahead", "each step is chosen without checking that the target depth is still reachable"),
            ("-stepcheck", "without step data checks", "the data checks run only on the finished program"),
            ("-dedupe", "without deduplication", "sampling with replacement"),
            ("naive", "naive (all off)", "all of the above removed: a naive combination of the same operations")]
        oc = lambda k, c: ab[k]["outcomes"].get(c, 0)
        R += ["### R1.2 What each mechanism of the generator contributes (Fig. 1b)",
              "Leave-one-out ablation on the 12 evaluation databases, no model: each arm requests the same depth cells with 25 attempts per cell; "
              "every finished program is judged by the same standard (valid on the data, depth measured on the SQL equal to the request, new, and "
              "sound: only row quantities the full profile admits and only steps the full type rules allow). Rates are per attempt made; each job "
              "draws for at most 240 s. Time is not reported (two harness versions ran). Source: `out/ablation/`, `specbridge.comm.construct.ablation`.\n",
              table(["arm", "what is removed", "attempts", "valid, on target, new and sound", "not sound", "duplicate", "off target depth", "invalid on the data", "not built"],
                    [[lab, d_, ab[k]["attempts"]] + ["%.1f%%" % (100 * oc(k, c) / ab[k]["attempts"]) for c in ("good and sound", "good, not sound", "duplicate", "off target depth", "invalid", "not drawn")] for k, lab, d_ in ARMDEF]),
              "\nLook-ahead decides whether the requested depth is reached; the profile and the type rules decide whether a program is sound "
              "(the data checks cannot see these errors); the restatement rules, step data checks and deduplication each remove waste. A naive "
              "combination of the same operations yields %.1f%% sound programs per attempt, the full generator %.1f%%.\n" % (
                  100 * oc("naive", "good and sound") / ab["naive"]["attempts"], 100 * oc("full", "good and sound") / ab["full"]["attempts"])]
    R += ["### R1.3 Programs per database with nothing requested (Tab. 1a)", table(["database", "source", "requested", "delivered", "cells short", "measured depth = target", "integrity failures", "distinct SQL", "distinct constructions", "distinct row quantities", "seconds", "model calls"],
          [[r["database"], r["source"], r["requested"], r["delivered"], r["short_cells"], r["built_for_eq_measured"], r["recomputed"] + r["trivial"], r["distinct_sql"], r["constructions"], r["base_quantities"], r["seconds"], r["model_calls"]] for r in t1["pool"]])]
    tot = lambda k: sum(r[k] for r in t1["pool"])
    R.append("\nTotal %s of %s delivered; measured depth = target for %s of %s; no integrity failures. The only shortfall is sakila_1 at arithmetic depth 3, "
             "step depth 6 (2 of 4), where no further program exists.\n" % tuple(format(tot(k), ",") for k in ("delivered", "requested", "built_for_eq_measured", "delivered")))
    R += ["### R1.4 Requesting depth (Tab. 1b; 48 programs at arithmetic depth 1-2; 3 seeds, min-max)", table(["database", "request", "delivered (mean)", "share at step depth 3-4", "share at step depth 5-7"],
          [[r["database"], {"shallow": "step depth 3-4", "balanced": "step depth 3-7", "deep": "step depth 5-7"}.get(r["request"], r["request"]), r["delivered_mean"], "%.0f-%.0f%%" % (100 * r["share_S3_4_min"], 100 * r["share_S3_4_max"]), "%.0f-%.0f%%" % (100 * r["share_S5_7_min"], 100 * r["share_S5_7_max"])] for r in t1["control"]]),
          "\nformula_1 has fewer cells at step depth 3-4, so fewer programs exist there.\n"]
    R += ["### R1.5 Weighting an operation (Tab. 1b; 48 programs, step depth 3-7, arithmetic depth 1-2; share of programs using it)", table(["database", "top-k in group, weight 1", "weight 3", "weight 10", "share of total, weight 1", "weight 10", "baseline comparison, weight 1", "weight 0.1"],
          [[r["database"]] + ["%.0f%%" % (100 * r[k]) for k in ("rank_w1", "rank_w3", "rank_w10", "share_w1", "share_w10", "baseline_w1", "baseline_w0.1")] for r in t1["preferences"]]),
          "\nWhy weights barely change the mix: a weight only acts where the operation is offered. Top-3 within group is offered only after a "
          "per-entity-within-group step and only as the last step, so whether it can appear is decided by earlier choices. The data checks are "
          "not the cause (they refused one top-3 cut, on two databases, at weight 10). Requiring the operation (R1.6) does not have this limit.\n"]
    R += ["### R1.6 Requiring an operation (Tab. 1b; 48 requested, step depth 3-7, arithmetic depth 1-2)", table(["database", "required", "delivered", "all use it", "measured depth = target", "depth cells where it is impossible (arithmetic, step)"],
          [[r["database"], r["required"].replace("rank", "top-k in group").replace("share", "share of total").replace("+", " + "), r["delivered"], r["all_use_them"], r["built_for_eq_measured"], (r["cells_not_constructible"] or "none").replace(";", "; ")] for r in t1["required"]]), ""]
    rb = t1["reviewed_build"]
    short = "; ".join("%s at (%s): %s" % (db, c, v.split(" after")[0]) for db, cells in (rb.get("shortfall") or {}).items() for c, v in cells.items())
    R += ["### R1.7 Reviewed benchmark tasks and natural questions (Tab. 1a)",
          "- 400 tasks requested (33-34 per database, arithmetic depth 1-2, step depth 3-6) -> **384 delivered** in %s s with %s model calls "
          "(each task accepted by both Opus and Sonnet); frozen as delivered (tag eval12-tasks-frozen-2026-10-02). Shortfall after 6 rounds, "
          "which this run could not supply (not shown to be impossible): %s." % (rb.get("seconds"), format(rb.get("model_calls"), ","), short),
          "- Reviewers rejected most often on insider (114 of 148 generated) and alien (111 of 142). Sampled reasons: arithmetic on quantities "
          "that should not be combined (e.g. the difference of two different kinds of angle), and a few errors in the column descriptions (text "
          "columns treated as numbers).",
          "- Natural questions: **382 of 384** (273 accepted on the first check, 109 after one revision, 2 not delivered); 585 model calls "
          "(58 writing, 495 checking, 32 revising); 6.1M input tokens; 1,063 s. Source: `%s/NATURAL.md`." % EV,
          "- Read-back test (Opus answers each natural question alone): 371 of 382 right; the 11 it got wrong it answered right from explicit V. "
          "All 11 were repaired and then read back right. The four solvers on those 11, before -> after repair: Haiku 6 -> 10, Sonnet 3 -> 11, "
          "GPT-Sol 6 -> 11, GPT-Luna 7 -> 10 (`%s/CORRECTIONS_v2.md`)." % EV,
          "- Pilot on three trial databases (wta_1, toxicology, news): 48 of 48 programs built, measured depth = target 48 of 48, no integrity "
          "failure; 47 of 48 natural questions; one question named the wrong output column and still passed Sonnet's check (example.md E3), "
          "which is why Opus checks since.\n"]

    # ---------------- R2
    R += ["## R2. Following an exact description: explicit V vs natural question (Fig. 2)",
          "*Question:* can solvers carry out the computation when it is described exactly, and does writing it as a natural question change that? "
          "*Finding:* the strong solvers (Sonnet, GPT-Sol) are near 100%% on both; the weaker ones (Haiku, GPT-Luna) do better on the natural "
          "question; explicit-V errors grow with step depth for the weaker solver of each family. %d tasks (384 frozen minus the 2 without a "
          "natural question); natural questions after the read-back repair; final queries that did not run were run again alone. Source: "
          "`%s/RESULTS_stage3.md`, `solver_<model>.json`, `%s-v2-changed/`.\n" % (f2["n_tasks"], EV, EV)]
    R.append(table(["solver", "explicit V right", "natural question right", "natural - explicit, 95% interval (points)"],
                   [[L(m), "%s (%s) %s" % (kn(f2["overall"][m]["explicit"]), pct(*f2["overall"][m]["explicit"]), ci(f2["overall"][m]["explicit_ci"])),
                     "%s (%s) %s" % (kn(f2["overall"][m]["precise_v2"]), pct(*f2["overall"][m]["precise_v2"]), ci(f2["overall"][m]["precise_ci"])),
                     ci(f2["overall"][m]["diff_precise_minus_explicit_ci"])] for m in M]))
    E12 = list(next(iter(f2["per_database"].values())).keys())
    R += ["\n### R2.1 Per database (explicit V right / natural question right)", table(["database"] + MN, [[db] + ["%s / %s" % (kn(f2["per_database"][m][db]["explicit"]), f2["per_database"][m][db]["precise_v2"][0]) for m in M] for db in E12])]
    R += ["\n### R2.2 Explicit-V errors by step depth (Wilson 95%)", table(["solver"] + ["step depth %d" % s for s in (3, 4, 5, 6)],
          [[L(m)] + ["%s (%s) %s" % (kn(f2["depth"][m]["S%d" % s]["explicit_errors"]), pct(*f2["depth"][m]["S%d" % s]["explicit_errors"]), ci(f2["depth"][m]["S%d" % s]["explicit_error_wilson"])) for s in (3, 4, 5, 6)] for m in M])]
    arm = {"explicit": "explicit V", "precise_v2": "natural question"}
    tests = "; ".join("%s, %s %s" % (arm.get(k.split("/")[0], k.split("/")[0]), LABEL.get(k.split("/")[1], "all four solvers"), v["p_one_sided"]) for k, v in f2["depth_test"].items())
    R += ["\nDoes step depth predict errors beyond differences between databases? Step depth shuffled among the tasks of each database 5,000 "
          "times; one-sided p: " + tests + ".",
          "Arithmetic depth does not show the effect (explicit-V errors, all four solvers: depth 1 86/844 = 10.2%, depth 2 34/684 = 5.0%).",
          "Where the errors are (counted from the program structure, `%s/ERRORS_<arm>_<model>.json`): on explicit V, GPT-Luna fails 2%% of "
          "programs with one comparison after the aggregation and 0%% with one share, but 25-45%% of programs that stack a second comparison on a "
          "first (a share then a baseline comparison, or two baseline comparisons); 59 of its 75 explicit-V errors are right on the natural "
          "question. The strong solvers' few natural-question errors are mostly at arithmetic depth 2 (Sonnet 10 of 11, GPT-Sol 10 of 13). "
          "Queries that did not run: invalid window functions (GPT-Luna), a repeated name for an intermediate result (Sonnet), text instead of "
          "SQL as the final answer (Haiku).\n" % EV]

    # ---------------- R3
    R += ["## R3. Existing benchmarks: the original question vs an exact description of its own answer (Fig. 3)",
          "*Question:* when solvers fail a real benchmark question, is the computation hard, or is the question unclear about what is wanted? "
          "*Finding:* on BIRD and Spider questions whose reference answer can be described exactly, every solver is near 100% from the "
          "description and far lower from the original question. Much of the gap is the form of the output (extra or reordered columns); "
          "after ignoring column differences, Spider's remaining gap is smaller than BIRD's, and BIRD shows more failures from wording "
          "(a phrase mapped to another column, an unstated requirement). That BIRD's questions are harder to read is an interpretation "
          "supported by this diagnosis, not a direct measurement.\n",
          "Grading: strict = the same rows as the reference (BIRD's rule); column differences ignored = the same rows, allowing extra or "
          "reordered columns.\n",
          "### R3.1 Which questions can be used",
          table(["benchmark", "questions", "reference answer runs", "explicit V can be produced", "used"],
                [["BIRD dev, development (5 databases)", 481, 481, 461, 461], ["BIRD dev, confirmation", 100, 100, 96, 96], ["Spider dev (20 databases)", 1034, 1032, 837, 835],
                 ["LiveSQLBench (Query category)", 180, 64, 84, "56 (not diagnosed)"]]),
          "Spider excludes questions whose answer uses UNION / INTERSECT / EXCEPT, which explicit V cannot describe. LiveSQLBench answers are "
          "written for PostgreSQL and our copies are SQLite, so it was not diagnosed. Source: `out/diagnose_coverage/COVERAGE.md`.\n",
          "### R3.2 Confirmation (Fig. 3a; questions kept aside until the protocol was frozen; one run per solver, one question per call)"]
    for split, lab in (("bird_heldout100", "BIRD (n = 96)"), ("spider_confirm50", "Spider (n = 50)")):
        C = f3["confirmation"][split]
        R.append(table(["%s: solver" % lab, "original, strict", "original, column differences ignored", "explicit V", "gap, strict (points, 95% interval)", "gap, column differences ignored", "right only from explicit V / only from original"],
                       [[L(m), "%s %s" % (kn(C[m]["original_strict"]), ci(C[m]["original_strict_ci"])), "%s %s" % (kn(C[m]["original_shape"]), ci(C[m]["original_shape_ci"])),
                         "%s %s" % (kn(C[m]["explicit_strict"]), ci(C[m]["explicit_ci"])), ci(C[m]["gap_strict_ci"]), ci(C[m]["gap_shape_ci"]), "%d / %d" % (C[m]["explicit_only"], C[m]["original_only"])] for m in M]))
        R.append("")
    R += ["### R3.3 Development (Haiku, 2 runs per question; counts are runs)",
          table(["questions", "number", "original, strict", "original, column differences ignored", "explicit V", "right only from explicit V / only from original (questions)"],
                [["BIRD, last six batches (8 questions per call)", "302", "329/604 (54%)", "377/604 (62%)", "594/604 (98%)", "109 / 0"],
                 ["BIRD, first three batches", "44, 60, 60", "49/88, 72/120, 68/120", "--", "79/82, 116/118, 118/118", "--"],
                 ["Spider development (1 question per call)", 150, "210/300 (70%)", "256/300 (85%)", "291/300 (97%)", "32 / 0"]]),
          "Sources: `out/comm_library/REMAINING_RESULTS.md`, `out/comm_library/spider_dev/TOTALS.md`.\n",
          "### R3.4 What the gap consists of (Fig. 3b; Opus's cause for each question Haiku answered right from explicit V and wrong from the original)"]
    causes = sorted({c for v in f3["causes"].values() for c in v if c}, key=lambda c: (c == "other", c))
    colname = {"confirmation/bird_heldout100": "BIRD confirmation", "confirmation/spider_confirm50": "Spider confirmation", "development/BIRD batches 3-8": "BIRD development (last six batches)", "development/Spider": "Spider development"}
    R.append(table(["cause"] + [colname.get(k, k) for k in f3["causes"]], [[PLAIN.get(c, c)] + [f3["causes"][k].get(c, 0) for k in f3["causes"]] for c in causes]))
    R.append("\nConfirmation has one run per question, so \"solver inconsistent across runs\" cannot be observed there; such cases fall under "
             "other causes, and development and confirmation shares are only roughly comparable.\n")

    # ---------------- R4
    R += ["## R4. The decision library (Tab. 2)",
          "Decisions that real benchmark questions leave to the reader, collected from the development questions only (481 BIRD, 150 Spider) and "
          "frozen on 2026-10-03 before any confirmation question was run (tag library-dev-frozen-2026-10-03). %d examples; %d errors in "
          "reference answers kept apart. \"Should raise\" = the question leaves the decision open or the reviewers disagree; \"should stay silent\" "
          "= the question settles it. One example per kind (chosen by a stated rule) is in `example.md` E5. Source: `library/REPORT.md`, "
          "`library/examples.jsonl`, `library/defects.jsonl`.\n" % (t2["n_examples"], t2["n_defects"]),
          table(["kind of decision", "should raise", "should stay silent", "from diagnosed failures", "from questions always solved"], [[typ(r["type"]), r["raise"], r["stay_silent"], r["from_records"], r["from_solved_questions"]] for r in t2["types"]]),
          "\ncomparison quantifier (3 disputed Spider cases) and negated membership scope (1) are provisional kinds, added when a case fit no "
          "existing kind. 4 cases could not be placed.\n"]

    # ---------------- R5
    fu = t3["funnel"]; lab = {"mutually recognized open": "accepted as open by both reviewers", "disputed open": "accepted as open by one reviewer"}
    R += ["## R5. Building the communication tests (Fig. 4, Tab. 3)",
          "### R5.1 From proposed decisions to frozen families (Tab. 3a)",
          "382 tasks -> 704 decisions proposed -> 660 whose second reading changes the answer -> 633 whose second reading can also be described as "
          "explicit V -> 606 accepted as reasonable by the reviewers (357 by both, 249 by one) on 330 tasks -> %d chosen (one per task, balanced "
          "across kinds) -> **%d frozen families** (24 failed review; for 1 the edits did not reproduce precise B). Intended reading: A %d, B %d. "
          "Open wording: %s. Source: `%s/RESULTS.md`, `cp/INVENTORY.md`.\n" % (fu["selected"], fu["frozen"], fu["intended"].get("A", 0), fu["intended"].get("B", 0), ", ".join("%s %d" % (lab.get(k, k), v) for k, v in fu["frozen_labels"].items()), TR),
          table(["kind of decision", "chosen", "frozen"], [[typ(t), fu["selected_types"].get(t, 0), fu["frozen_types"].get(t, 0)] for t in sorted(set(fu["selected_types"]) | set(fu["frozen_types"]), key=lambda t: -fu["selected_types"].get(t, 0))]),
          "\nFrozen per database: " + ", ".join("%s %d" % kv for kv in sorted(fu["frozen_databases"].items())) + ".\n",
          "### R5.2 Plan-and-check vs direct generation (Tab. 3b; 60 tasks fixed before any writing; exact McNemar test)"]
    mname = {"open_both": "open wording accepted for both readings", "selective": "each precise wording accepted only for its own reading",
             "fidelity": "no shared requirement lost or changed", "pass": "passes every check"}
    rows = []
    for key, v in t3["ablation_60_pairs"].items():
        t = v["full_vs_direct"]; m_, st = key.split("/")
        rows.append(["%s, %s" % (mname.get(m_, m_), "first draft" if st == "first" else "after one revision"), v["full"], v["direct"], "%d / %d" % (t["only_first"], t["only_second"]), t["mcnemar_exact_p"], ci(t["diff_ci"])])
    R.append(table(["check (of 60)", "plan-and-check", "direct generation (one prompt, no plan, no revision)", "only plan-and-check / only direct", "exact McNemar p", "difference, 95% interval (points)"], rows))
    R += ["\nThe plan is what keeps the wordings faithful. Direct generation writes open and precise wordings that the reviewers accept as open "
          "and as selecting one reading, but it loses or changes a shared requirement in 28 of 60; after one revision, plan-and-check passes every "
          "check on 49 of 60, direct generation on 32 (direct generation has no revision step, so its first and final counts are the same). "
          "Source: `%s/compare/`, `out/paper/data/tab3_generation.json`.\n" % TR,
          "### R5.3 Kinds of decision not in the library",
          "8 chosen, 7 frozen: running total vs per-event value (2), active vs all customers, how the baseline is defined, which rows the baseline "
          "covers, what is compared with the baseline, counting rows vs summing a quantity. Provisional: accepted by model reviewers only. All "
          "cases are in `example.md` E7.\n"]

    # ---------------- R6
    R += ["## R6. Answering the families with the full solver procedure (one question per call, may explore the database)",
          "\"Both precise right\" = the solver answered precise A with reading A and precise B with reading B. On the open wording, each answer "
          "is classified by which reading it returns.\n",
          table(["solver", "explicit V of the intended reading", "precise, intended reading", "precise, other reading", "both precise right", "open: intended / other / neither", "open, among both precise right: intended / other / neither"],
                [["Haiku", "193/213", "187/215", "189/215", 169, "83 / 75 / 57", "70 / 66 / 33 (of 169)"], ["Sonnet", "211/213", "210/215", "207/215", 203, "108 / 97 / 10", "99 / 94 / 10 (of 203)"],
                 ["GPT-Sol", "213/213", "207/215", "207/215", 203, "105 / 92 / 18", "101 / 88 / 14 (of 203)"], ["GPT-Luna", "182/213", "187/215", "188/215", 168, "97 / 77 / 41", "78 / 60 / 30 (of 168)"]]),
          "Source: `%s/RESULTS.md`, `render/eval/runs/`. Explicit V exists for 213 of the 215 families.\n" % TR]

    # ---------------- R7
    R += ["## R7. Disclosure: do solvers notice and say what the request leaves open? (Fig. 5, Tab. 4-5)",
          "*Finding:* naming the open decision, stating the reading adopted, and supplying the other reading are separate abilities. When a solver "
          "states its reading, the statement is true of its SQL almost always (97-100%); the weak links are naming the decision and supplying "
          "the alternative. Covering both readings: Sonnet 42%, GPT-Sol 33%, Haiku 13%, GPT-Luna 8% among families where the solver computes "
          "both readings when told which. Solvers almost never call a settled decision open (0-1%). Asking for disclosure costs time and length, "
          "not accuracy.\n",
          "All %d families per solver; each solver answers in one call, without exploring the database, with the disclosure instruction "
          "(version `eea2aeafdbd5`, method.md M2). Every response and every alternative was judged by Opus without knowing which solver wrote "
          "it; every query was run. Comparison: the same single call without the disclosure sentences, on the same family and wording. Source: "
          "`%s/DISCLOSURE_FULL.md`, `render/disclose/`.\n" % (f5["n_families"], TR)]
    mm = f5["models"]
    row = lambda lab_, key: [lab_] + ["%d/%d (%s) %s" % (mm[m][key]["k"], mm[m][key]["n"], pct(mm[m][key]["k"], mm[m][key]["n"]), ci(mm[m][key].get("ci"))) for m in M]
    R.append(table(["measure (how decided)"] + MN, [
        row("precise wording: main answer returns its reading (run)", "precise_correct"), row("open wording: main answer returns reading A or B (run)", "open_admissible"),
        row("names the decision as open (judge)", "recognises"), row("states the reading it adopted (judge)", "states"),
        ["statement true of its SQL, among those that state one (judge; Wilson)"] + ["%d/%d %s" % (mm[m]["faithful_given_stated"]["k"], mm[m]["faithful_given_stated"]["n"], ci(mm[m]["faithful_given_stated"]["wilson"])) for m in M],
        row("states its reading truthfully, of all (judge)", "states_faithful"), row("answer plus alternatives return both readings, all families (run)", "covers_both"),
        row("both readings returned, among families with both precise right (run)", "covers_both_given_both_precise"),
        ["alternatives offered"] + [mm[m]["alternatives"]["offered"] for m in M],
        ["alternatives judged a reasonable reading (judge)"] + ["%d/%d" % (mm[m]["alternatives"]["supported_judge"], mm[m]["alternatives"]["judged"]) for m in M],
        ["alternatives that return reading A or B (run)"] + ["%d/%d" % (mm[m]["alternatives"]["returns_recorded_reading"], mm[m]["alternatives"]["offered"]) for m in M],
        row("precise wording wrongly called open (judge)", "false_open"),
        ["precise right: without -> with disclosure (difference, 95% interval)"] + ["%d -> %d (%s)" % (mm[m]["overhead"]["precise_plain_single"], mm[m]["overhead"]["precise_disclosure"], ci(mm[m]["overhead"]["precise_diff_ci"])) for m in M],
        ["open returns A or B: without -> with disclosure"] + ["%d -> %d" % (mm[m]["overhead"]["open_plain_single"], mm[m]["overhead"]["open_disclosure"]) for m in M],
        ["median seconds: without -> with"] + ["%.0f -> %.0f" % (mm[m]["overhead"]["median_seconds_plain"], mm[m]["overhead"]["median_seconds_disclosure"]) for m in M],
        ["median answer length in characters: without -> with"] + ["%d -> %d" % (mm[m]["overhead"]["median_chars_plain"], mm[m]["overhead"]["median_chars_disclosure"]) for m in M],
        ["mean number of distinct answers returned (with disclosure)"] + [mm[m]["overhead"]["mean_answer_set"] for m in M], ["tokens"] + ["not logged"] * 4]))
    R += ["\nThe right comparison for cost is the same single call without the disclosure sentences. Against the full solver procedure of R6, "
          "which may explore the database, disclosure answers are 13-16 points lower for Haiku, GPT-Sol and GPT-Luna; that is the effect of not "
          "exploring, not of the instruction (precise right, single call vs full procedure: GPT-Sol 176 vs 207, Haiku 163 vs 188).\n"]

    # ---------------- R8
    f6 = d("fig6_inclination"); GR = list(f6["groups"]); KS = list(f6["usual"]); g6 = f6["groups"]
    lb = f6["library_open"].get("BIRD", {}); hm, hi = lb.get("high+medium", {"follows": 0, "against": 0, "wilson": None}), lb.get("high", {"follows": 0, "against": 0})
    from specbridge.report.figures import MIN_SPLIT_N
    cell = lambda r: "%d/%d (%s)" % (r["k"], r["n"], pct(r["k"], r["n"])) if r["n"] >= MIN_SPLIT_N else ("-- (n = %d)" % r["n"] if r["n"] else "--")
    def cue(bench):         # counting: DISTINCT among questions WITH the cue, train + dev of one benchmark's own authors
        gs = ["BIRD train", "BIRD dev"] if bench == "BIRD" else ["Spider train (own)", "Spider dev"]
        a = sum(g6[g]["kinds"]["counting_unit"]["cued"]["A"] for g in gs); n = a + sum(g6[g]["kinds"]["counting_unit"]["cued"]["B"] for g in gs); return "%d/%d" % (a, n)
    def sq(g):              # silent questions against the usual reading, k/n (%) [Wilson]
        r = g6[g]["silent_questions"]; return "%d/%d (%s, Wilson %s)" % (r["against_usual"], r["n"], pct(r["against_usual"], r["n"]), ci(r["wilson"]))
    def said(g):            # share of counts over a join whose question carries the cue
        c = g6[g]["kinds"]["counting_unit"]; m = sum(c["cued"].values()); return "%d/%d (%s)" % (m, m + c["n"], pct(m, m + c["n"]))
    R += ["## R8. Hidden defaults: how each group of authors settles what the question leaves unsaid (Fig. 6)",
          "*Question:* when the wording gives no cue for a decision of meaning, which reading does the reference SQL take, and does that "
          "depend on the words or on who wrote the SQL? *Finding:* mostly on the authors, never completely. BIRD and Spider's own data "
          "settle all seven decisions the same way (one row for an extreme, count rows over a join, no filter on missing values before "
          "sorting, inner join, 'between' inclusive, 'after' / 'over' / 'under' strict, a named value matched exactly), and within each, "
          "train and dev agree although their databases differ. The datasets Spider imported from earlier work were written by other teams, "
          "and two of them reverse a decision on the same kind of wording: geo and restaurants return every tied row (one row in %s), "
          "academic, imdb and yelp count distinct entities (rows in %s). So a model trained on BIRD train meets the same unstated defaults in "
          "BIRD dev and can learn them; the question does not communicate them, and telling a solver the defaults raises its BIRD score "
          "(R8.1). The defaults are not complete: %s of BIRD dev and %s of "
          "Spider dev questions with a silent decision have a reference that goes against the usual reading (Fig. 6b); a model that learned "
          "every default would still need the question to say what is meant for these.\n" % (
              cell(g6["imported: geo, restaurants"]["kinds"]["ties_and_selection"]), cell(g6["imported: academic, imdb, yelp"]["kinds"]["counting_unit"]),
              sq("BIRD dev"), sq("Spider dev")),
          "Only decisions of meaning are counted; output form (extra or reordered columns, duplicate rows) is left out, as in grading. "
          "Silent question: one whose wording has no cue for the decision (for example \"different\", \"distinct\" or \"unique\" for counting; "
          "method.md section 7.8). Where the cue is present, the reference follows it in both benchmarks (counting: DISTINCT in %s BIRD and %s "
          "Spider own questions); BIRD writes the cue less often (%s of BIRD train vs %s of Spider own train counts over a join). In the "
          "library, the open records of these decisions that the reviewers call a meaning choice (high or medium confidence) come from BIRD "
          "only: the reference takes the usual reading in %d of %d (Wilson %s; high confidence alone %d of %d). Source: "
          "`out/comm_library/INCLINATION.md`, `out/paper/data/fig6_inclination.json`.\n" % (
              cue("BIRD"), cue("Spider"), said("BIRD train"), said("Spider train (own)"), hm["follows"], hm["follows"] + hm["against"],
              ci(hm["wilson"]), hi["follows"], hi["follows"] + hi["against"])]
    R.append(table(["usual reading (silent questions)"] + ["%s (%d db)" % (g, g6[g]["databases"]) for g in GR],
                   [[f6["usual"][k]] + [cell(g6[g]["kinds"][k]) for g in GR] for k in KS]))
    R.append("\nLibrary kind of each row: %s. The last two rows (calculation) arise almost only in BIRD and are not drawn in Fig. 6. "
             "Of the library's 13 kinds of meaning decision, 7 have a reading code can take from the SQL and are covered here; which "
             "column a phrase means, which role a relationship plays, how two conditions link, comparison with any vs all, the scope of "
             "a negation, and the level of an average need the meaning of the database and are not counted.\n" % "; ".join(
                 "%s = %s" % (f6["usual"][k], f6["library_types"][k].replace("_", " ")) for k in KS))
    EM = f6["note_experiment"]["models"]
    dpt = lambda S, n: 100 * (S["note"] - S["plain"]) / n
    def said_m(m):
        es = EM[m]["subsets"]; A, Si, No = es["all"], es["with a silent decision"], es["without one"]
        return ("%s: %d to %d (%+.1f points, %s, p = %.2g; %d became right, %d wrong); with a silent decision %+.1f (%s, p = %.2g); without one "
                "%+.1f (%s, p = %.2g); shape-tolerant %+.1f (%s)" % (LABEL[m], A["pass"]["plain"], A["pass"]["note"], dpt(A["pass"], A["n"]), ci(A["pass"]["diff_ci"]),
                A["pass"]["mcnemar_p"], A["pass"]["up"], A["pass"]["down"], dpt(Si["pass"], Si["n"]), ci(Si["pass"]["diff_ci"]), Si["pass"]["mcnemar_p"],
                dpt(No["pass"], No["n"]), ci(No["pass"]["diff_ci"]), No["pass"]["mcnemar_p"], dpt(A["shape"], A["n"]), ci(A["shape"]["diff_ci"])))
    n0 = list(EM.values())[0]["subsets"]
    R += ["### R8.1 Telling the solver the defaults (Fig. 6c)",
          "%s each answered the same %d BIRD dev questions in their original wording twice: once as is, once after one fixed note on how "
          "BIRD's authors usually settle silent decisions (built from BIRD train only; nothing about the question is revealed; method.md "
          "section 7.9). %d of the questions have a reference with a silent decision the note addresses (decided from the reference SQL "
          "only). BIRD grade, paired, exact McNemar p: %s. Reading the changed answers: some gains are the note's defaults applied "
          "(count rows, one row for an extreme, 'between' inclusive, exact match); most others are a more literal, more minimal BIRD style "
          "the note does not spell out (Sonnet: no DISTINCT, the hint's formula copied; GPT-Sol: no extra columns, no filters nobody asked "
          "for, values copied as written). Part of that is output form, which is why the shape-tolerant gain is smaller; it stays "
          "significant for both solvers. Some losses apply the note where it does not fit. One run per arm. Source: "
          "`out/prior/bird600/RESULTS_<solver>.md`.\n" % (names(LABEL[m] for m in EM), n0["all"]["n"], n0["with a silent decision"]["n"],
                                                           "; ".join(said_m(m) for m in EM))]
    R.append("Silent questions against the usual reading (Fig. 6b):\n")
    R.append(table(["author group", "silent questions", "against the usual reading on at least one decision"],
                   [[g, g6[g]["silent_questions"]["n"], "%d (%s) %s" % (g6[g]["silent_questions"]["against_usual"], pct(g6[g]["silent_questions"]["against_usual"], g6[g]["silent_questions"]["n"]),
                                                                       ci(g6[g]["silent_questions"]["wilson"]))] for g in GR]))
    R.append("")

    # ---------------- R9-R10
    R += ["## R9. Failures, recoveries and cost",
          "- Usage-limit outages: on 2026-10-02 (read-back test) 335 empty answers were removed and redone; on 2026-10-03 (families) 1,236 failed "
          "outputs (Sonnet full procedure 448; Haiku and Sonnet disclosure 788) were removed and redone, and 28 families that had failed only "
          "because a reviewer's verdict was missing were reviewed again. Since then an error or limit message is a failed call, never an answer.",
          "- Timeouts under load: 10 answers were right when run again alone (GPT-Luna 9, GPT-Sol 1); running non-executing queries again alone "
          "is part of grading.",
          "- Model calls (where logged): reviewed tasks 1,664; natural questions 585; read-back 382 + repair 32 + re-read 11; confirmation 1,184 "
          "solver calls; families: 3,432 full-procedure and 1,720 disclosure solver calls, judges 1,720 + 555. Tokens were logged only for the "
          "natural-question writer (6.1M in, 0.29M out). Money was not logged.\n",
          "## R10. Limitations",
          "- Human validation is pending for every number that rests on a model's judgment (R1.7, R2, R3.4, R4, R5, R7).",
          "- One run per solver, so no run-to-run variation is reported. BIRD development used 8 questions per call. LiveSQLBench questions were "
          "not diagnosed.",
          "- Only questions whose reference answer runs and can be described as explicit V are used (Spider set operations excluded).",
          "- Weights do not steer top-k within group (a property of where the operation can occur); requirements do.",
          "- The exact model version behind each call was not logged; the Claude command-line tool moved from 2.1.287 to 2.1.289 and Codex from "
          "0.147 to 0.160 during the work.",
          "- The library comes from benchmark reference answers; generating tasks never uses any benchmark's answers.",
          "- Hidden defaults (R8) are measured only for decisions with a syntax signature, and silence is decided by word lists checked on "
          "samples, not by a reader. A side read from syntax does not say whether the other side changes the answer on the data. Authors and "
          "databases change together, so author habit is not fully separated from the databases. Telling a solver the defaults (R8.1) "
          "was run with %s, one run per arm, on BIRD only." % NOTE_SOLVERS()]
    open("paper/result.md", "w").write("\n".join(R) + "\n")


# =========================================================================== example.md
def example():
    from specbridge.comm.diagnose.library import example_for
    from specbridge.comm.transfer.evaluate import matches
    from specbridge.report.explain import LABEL
    from specbridge.report.figures import PLAIN
    LB = lambda m: LABEL.get(m, m)
    dep = lambda a, s_: "arithmetic depth %s, step depth %s" % (a, s_)
    STATUS = {"contested": "reviewers disagree", "unresolved": "the question leaves it open", "conflicting": "examples conflict", "resolved": "the question settles it"}
    def checks(r):
        lab = r.get("label") or ""
        return "; ".join(x for x in ["open wording accepted for both readings by %s" % ("both reviewers" if lab.startswith("mutually") else "one reviewer") if lab else "",
                                      "each precise wording accepted only for its own reading" if r.get("precise_selective") else "a precise wording was not accepted only for its own reading",
                                      "no requirement lost or changed" if r.get("fidelity_ok") else "a requirement was lost or changed",
                                      {"survives": "kept"}.get(r.get("status"), "not kept (%s)" % r.get("status"))] if x)
    X = ["# SpecBridge: examples", "Every example referred to by `result.md`, with the rule that selected it. Terms are defined in `method.md`, \"Terms used throughout\". Human validation: PENDING.\n"]
    # E1 worked family
    w = d("fig4_worked_example"); e = w["example"]; C = {c["case"]: c for c in J(TR + "/render/eval/frozen.json")["cases"]}; c = C[e["case"]]
    ex_text, ex_id = example_for("aggregation_level")
    rule = w["rule"].replace("aggregation_level", "aggregation level").replace("open label 'mutually recognized open'", "open wording accepted for both readings by both reviewers").replace("survived on the first pass (round 0, status survives)", "kept without revision")
    X += ["## E1. One program becomes a communication test (Fig. 4)", "Rule: %s (%d candidates)\n" % (rule, w["candidates"]),
          "**Program A** (%s, %s):" % (e["database"], dep(e["A"], e["S"])), fence(e["sql_A"], "sql"), "**Explicit V of the intended reading (%s):**" % c["intended"], fence(c["texts"].get("explicit", "")),
          "**Decision the request could leave unstated.** %s  \nReading A: %s  \nReading B: %s  \nSQL edits that turn A into B: `%s`  \nRows that differ between the two answers: `%s`" % (e["decision"], e["reading_A"], e["reading_B"], json.dumps(e["edits"])[:600], json.dumps(e.get("witness"))[:400]),
          "**SQL B:**", fence(e["sql_B"], "sql"), "**Retrieved library example shown to the writer (%s):**" % ex_id, fence(ex_text[:2500]),
          "**Plan.** Shared requirements: %s  \nReading A's choice: %s  \nReading B's choice: %s" % (json.dumps(e["plan_shared"])[:1200], json.dumps(e["choice_A"]), json.dumps(e["choice_B"])),
          "**Precise A:** %s\n\n**Precise B:** %s\n\n**Open:** %s" % (e["precise_A"], e["precise_B"], e["open"]),
          "**Checks:** %s." % checks(e["review"]), ""]
    rows = []
    for m in M:
        dd = TR + "/render/eval/runs/" + m.replace("-", "_") + "_b1"; got = {}
        for f in glob.glob(dd + "/*.json"):
            o = J(f)
            if o["key"].startswith(e["case"] + "|"): got[o["key"].rsplit("|", 1)[1]] = matches(c, o["answer"]) if o.get("answer") is not None else []
        disc = {o["wording"]: o for o in (J(f) for f in glob.glob(TR + "/render/disclose/%s/*.json" % m)) if o["case"] == e["case"]}
        op = disc.get("open")
        cov = op and {"A", "B"} <= set(op["primary_matches"]) | {x for a in op["alternatives"] for x in a["matches"]}
        rows.append([LB(m)] + ["/".join(got.get(v, [])) or "neither" for v in ("explicit", "precise", "precise_other", "open")] + [("covers both" if cov else "main answer " + ("/".join(op["primary_matches"]) or "neither")) if op else "-"])
    X += ["Reading returned by each solver (A, B, or neither); full procedure except the last column, which is the single disclosure call.\n",
          table(["solver", "explicit V", "precise (intended %s)" % c["intended"], "precise (other)", "open", "open, with disclosure"], rows), ""]
    # E2 explicit V vs real question
    X += ["## E2. Real question vs explicit V of the reference (Fig. 3)", "Rule: the first BIRD and the first Spider confirmation question (in task order) that every solver answers right from explicit V and wrong from the original question.\n"]
    for split in ("bird_heldout100", "spider_confirm50"):
        dd = "out/confirmation/" + split; O = {t["id"]: t for t in map(json.loads, open(dd + "/tasks_original.jsonl"))}; Ex = {t["id"]: t for t in map(json.loads, open(dd + "/tasks_explicit.jsonl"))}
        def ok(m, arm, i):
            f = "%s/runs/%s/%s_rep0/%s.json" % (dd, m.replace("-", "_"), arm, i); return os.path.exists(f) and J(f).get("pass")
        pick = next((i for i in sorted(Ex) if all(ok(m, "explicit", i) and not ok(m, "original", i) for m in M)), None)
        if pick:
            fs = "%s/runs/haiku/original_rep0/%s.json" % (dd, pick)
            X += ["### %s confirmation %s (%s)" % ({"bird_heldout100": "BIRD", "spider_confirm50": "Spider"}[split], pick, O[pick]["database"]), "**Original question:** %s" % O[pick]["instruction"], "**Reference SQL:**", fence(O[pick]["reference_sql"], "sql"),
                  "**Explicit V:**", fence(Ex[pick]["instruction"].split("\nConventions")[0]), "**Haiku's SQL from the original question (wrong):**", fence(J(fs).get("final"), "sql"), ""]
    # E3 wording defects
    X += ["## E3. Wording errors in natural questions and their repair (R1.7)", "Rule: the pilot error; two of the 11 questions repaired after the read-back test; one error the single reader missed.\n"]
    P0 = {json.loads(l)["id"][-10:]: json.loads(l) for l in open("out/corpora/pilot-dev@09cacc14fa59/corpus.jsonl")}
    P1 = {json.loads(l)["id"][-10:]: json.loads(l) for l in open("out/corpora/pilot-dev@09cacc14fa59-corr1/tasks_paired.jsonl")}
    t = P0["8ac7dd4f7e"]
    X += ["### Pilot 8ac7dd4f7e (wta_1, %s): a wrong output column that Sonnet's check accepted" % dep(2, 6), "**Explicit V, final step:**", fence(t["instruction"].split("Step 6")[1].split("\nConventions")[0][:900]),
          "**Question as delivered (output (1) names step 5's column (1), the player ID):**", fence(t["question"][-900:]),
          "**Corrected (checked by Opus; output (1) = column (2), the playing hand):**", fence(P1["8ac7dd4f7e"]["natural_precise"]["question"][-700:]), ""]
    V1 = {json.loads(l)["id"][-10:]: json.loads(l) for l in open(EV + "/corpus.jsonl")}; V2 = {json.loads(l)["id"][-10:]: json.loads(l) for l in open(EV + "/corpus.v2.jsonl")}
    sus = J(EV + "-readback11/suspects.json"); sus = {k[-10:]: v for k, v in sus.items()}
    for tid, why in (("6ec8137fd3", "the question compares the average PRICE; explicit V compares the average cost RATIO (a measure renumbered between steps)"),
                     ("227771660b", "the question compares step 1's '(3)'; explicit V compares column (3) of step 2, which is step 1's column (4)")):
        X += ["### Evaluation task %s (%s): %s" % (tid, V1[tid]["database"], why), "**Before:**", fence(V1[tid]["question"]), "**Opus's SQL from the question before repair (wrong):**", fence(sus.get(tid), "sql"),
              "**After repair (read back right):**", fence(V2[tid]["question"]), ""]
    X += ["### Evaluation task 568a31721e (thrombosis_prediction): missed by the single reader", "The question says \"hematocrit **fraction**\"; three solvers divided HCT by 100; explicit V uses the stored value. Opus read it correctly, so the read-back did not flag it -- one reason the human audit is needed.",
          fence(V2["568a31721e"]["question"]), ""]
    # E4 diagnosis per cause
    X += ["## E4. Why the original question failed: one diagnosed case per cause and benchmark (R3.4)", "Rule: per cause, the first BIRD (last six development batches) and the first Spider development case in task order with a wrong run on the original question.\n"]
    for bench, dirs in (("BIRD", ["out/comm_library/batch%d" % i for i in range(3, 9)]), ("Spider", ["out/comm_library/spider_dev"])):
        seen = set()
        for dd in dirs:
            T = {t["id"]: t for t in map(json.loads, open(dd + "/tasks_original.jsonl"))}
            for g in sorted(J(dd + "/inspection.json"), key=lambda g: g["task"]):
                cause = g.get("cause")
                if not cause or cause in seen or g["task"] not in T: continue
                f = next((x for x in ("%s/runs/haiku/original_rep%d/%s.json" % (dd, r, g["task"]) for r in (0, 1)) if os.path.exists(x) and not J(x).get("pass")), None)
                if not f: continue
                seen.add(cause); tt = T[g["task"]]
                X += ["### %s / %s -- %s:%s (%s)" % (bench, PLAIN.get(cause, cause), os.path.basename(dd), g["task"], tt["database"]), "**Question:** %s" % tt["instruction"], "**Reference SQL:**", fence(tt["reference_sql"], "sql"),
                      "**Solver SQL (wrong):**", fence(J(f).get("final"), "sql"), "**Opus's diagnosis:** %s  \n**Does the question settle the reference's choice?** %s" % (g.get("difference"), g.get("question_gap")), ""]
    # E5 library rows and defects
    t2 = d("tab2_library")
    X += ["## E5. The decision library: one example per kind, and errors in reference answers (Tab. 2)", "Rule: %s\n" % t2["rule"].replace("RAISE", "should-raise").replace("two-reading record", "diagnosed case with two readings").replace("gate confidence", "confidence")]
    for r in t2["types"]:
        if not r["example_source"]: X.append("### %s -- no should-raise example with two readings (stay-silent examples only)\n" % r["type"].replace("_", " ")); continue
        for fld in ("example_readings", "example_gate"):
            if isinstance(r.get(fld), str):
                try: r[fld] = json.loads(r[fld])
                except ValueError: pass
        X += ["### %s -- %s (%s)" % (r["type"].replace("_", " "), r["example_source"], STATUS.get(r["example_status"], r["example_status"])), "**Question:** %s" % r["example_question"], "**Decision:** %s" % r["example_decision"],
              "**Readings:** %s" % "  \n".join("%s: %s" % (x.get("id"), x.get("reading")) for x in (r["example_readings"] if isinstance(r["example_readings"], list) else [])) or r["example_readings"],
              "**Confidence and category (Opus):** %s" % ("%s; %s. %s" % (r["example_gate"].get("confidence"), r["example_gate"].get("category"), r["example_gate"].get("reason", "")) if isinstance(r["example_gate"], dict) else r["example_gate"]), ""]
    X.append("### Errors in reference answers (kept out of the library)")
    for dfx in t2["reference_defects_examples"]:
        g_ = dfx.get("gate") or {}
        X += ["- **%s:** %s  \n  Opus: %s" % (dfx.get("source"), dfx.get("decision"), (g_.get("reason") or json.dumps(g_))[:400] if isinstance(g_, dict) else str(g_)[:400])]
    X.append("")
    # E6 rendering ablation
    pairs = J(TR + "/compare/pairs60.json"); conds = (("plan-and-check", TR + "/render"), ("direct", TR + "/compare/direct"))
    Wc = {n: J(p + "/written.json") for n, p in conds}; Rc = {n: J(p + "/review.json") for n, p in conds}
    k = next(k for k in pairs if all(Wc[n].get(k, {}).get("open") for n, _ in conds))
    X += ["## E6. The same task written by plan-and-check and by direct generation (R5.2)", "Rule: the first of the 60 fixed tasks with both methods written. Case %s.\n" % k]
    for n, _p in conds:
        ww = Wc[n][k]; rr = Rc[n].get(k, {})
        X += ["### %s -- review: %s" % (n, checks(rr)), "**Precise A:** %s\n\n**Precise B:** %s\n\n**Open:** %s" % (ww.get("precise_A"), ww.get("precise_B"), ww.get("open")),
              "**Reviewers' reasons:** %s" % ("; ".join(rr.get("reasons", []))[:800] or "none"), ""]
    # E7 novel
    nov = open(TR + "/NOVEL.md").read().split("\n", 3)[3]
    for x, y in (("mutually recognized open", "open wording accepted for both readings by both reviewers"), ("disputed open", "open wording accepted for both readings by one reviewer"), ("Reading A (reference)", "Reading A (the program)"),
                 ("Plain open answers (which reading each solver computed)", "Open wording, full procedure (reading returned)"), ("Disclosure, open wording", "Open wording, with disclosure"),
                 (" primary ", " main answer "), ("haiku ", "Haiku "), ("sonnet ", "Sonnet "), ("gpt-6-sol ", "GPT-Sol "), ("gpt-6-luna ", "GPT-Luna ")):
        nov = nov.replace(x, y)
    nov = re.sub(r"\bA(\d) S(\d)\b", r"arithmetic depth \1, step depth \2", nov)
    X += ["## E7. Kinds of decision not in the library (R5.3)", "All frozen families whose kind is not in the library (provisional: accepted by model reviewers only).\n", nov.replace("## ", "### "), ""]
    # E8 disclosure
    Jd = J(TR + "/render/disclose/judge.json"); JA = J(TR + "/render/disclose/judge_alternatives.json")
    def resp(m):
        return {(o["case"], o["wording"]): o for o in (J(f) for f in sorted(glob.glob(TR + "/render/disclose/%s/*.json" % m)))}
    picks = []
    S = resp("sonnet"); picks.append(("covers both readings (Sonnet, open wording)", "sonnet", next(kw for kw, o in S.items() if kw[1] == "open" and {"A", "B"} <= set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]})))
    G = resp("gpt-6-sol"); picks.append(("states its reading truthfully, offers no alternative (GPT-Sol, open wording)", "gpt-6-sol", next(kw for kw, o in G.items() if kw[1] == "open" and not o["alternatives"] and (Jd.get("%s|open|gpt-6-sol" % kw[0]) or {}).get("faithful") == "yes")))
    L = resp("gpt-6-luna"); picks.append(("names the decision but does not return both readings (GPT-Luna, open wording)", "gpt-6-luna", next(kw for kw, o in L.items() if kw[1] == "open" and (Jd.get("%s|open|gpt-6-luna" % kw[0]) or {}).get("flags_decision") is True and not ({"A", "B"} <= set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]}))))
    fo = next(((m, k2) for m in M for k2, v in sorted(Jd.items()) if k2.endswith("|" + m) and "|open|" not in k2 and v.get("claims_open_wrongly") is True), None)
    if fo: picks.append(("calls a settled decision open (%s, precise wording)" % LB(fo[0]), fo[0], tuple(fo[1].split("|")[:2])))
    ua = next((k2 for k2, v in sorted(JA.items()) if v.get("verdict") == "unsupported"), None)
    if ua: c_, w_, m_, _i = ua.split("|"); picks.append(("an alternative the judge finds unreasonable (%s)" % LB(m_), m_, (c_, w_)))
    Wr = J(TR + "/render/written.json")
    X += ["## E8. Disclosure answers (R7)", "Rule: per pattern, the first response in file order that shows it. The judge's fields: flags_decision = names the decision as open; faithful = what it states is true of its SQL; claims_open_wrongly = calls a settled decision open.\n"]
    for lab, m, kw in picks:
        o = resp(m)[kw]; jj = Jd.get("%s|%s|%s" % (kw[0], kw[1], m))
        X += ["### %s -- %s" % (lab, kw[0]), "**Request (%s):** %s" % (kw[1], Wr[kw[0]][kw[1]]), "**Readings:** A: %s | B: %s" % (Wr[kw[0]]["reading_A"], Wr[kw[0]]["reading_B"]),
              "**Response:**", fence(json.dumps(o["response"], indent=1)[:2500], "json"),
              "**Run:** main answer returns %s; alternatives return %s" % (o["primary_matches"] or "neither", [a["matches"] for a in o["alternatives"]]),
              "**Judge (Opus):** %s" % json.dumps(jj), "**Judgments of the alternatives:** %s" % json.dumps([JA.get("%s|%s|%s|%d" % (kw[0], kw[1], m, i)) for i in range(len(o["alternatives"]))])[:800], ""]
    # E9 hidden defaults, E10 the defaults note (R8)
    from specbridge.comm.diagnose import inclination as I, prior as P
    f6 = d("fig6_inclination"); USU = {"ties_and_selection": "A", "counting_unit": "B"}
    X += ["## E9. The same kind of silent question, settled by different authors (R8, Fig. 6a)",
          "Rule: for ties and for counting, per author group, the first silent question in file order whose reference takes that group's "
          "majority reading. Readings are read from the SQL by code.\n"]
    for kind, groups in (("ties_and_selection", ["BIRD dev", "Spider dev", "imported: geo, restaurants"]), ("counting_unit", ["BIRD dev", "Spider dev", "imported: academic, imdb, yelp"])):
        X.append("### %s" % {"ties_and_selection": "Ties: one row (LIMIT 1) or every tied row", "counting_unit": "Counting over a join: rows or distinct entities"}[kind])
        for g in groups:
            r = f6["groups"][g]["kinds"][kind]; maj = USU[kind] if r["k"] * 2 >= r["n"] else ("B" if USU[kind] == "A" else "A")
            for db, sql, q in I.GROUPS[g]():
                sd = I.sides(sql, q)
                if sd.get(kind) == maj and not I.CUES[kind].search(q):
                    lab = dict((k, (a, b)) for k, _t, a, b in I.KINDS)[kind][0 if maj == "A" else 1]
                    X += ["**%s** (%s; this group's majority: %s, %d/%d silent questions on the usual reading)  " % (g, db, lab, r["k"], r["n"]),
                          "Question: %s  " % " ".join(q.split()), "```sql\n%s\n```\n" % " ".join(sql.split())]
                    break
    EM = f6["note_experiment"]["models"]; T = {t["id"]: t for t in P.tasks()}; U = {k: sd for k, sd, _t in P.LINES}
    X += ["## E10. Answers changed by the defaults note (R8.1, Fig. 6c)",
          "Rule: per solver, the two questions with the shortest wording among those that became right with the note while a decision "
          "the note names moved to its usual reading; and the shortest among those that became wrong while a decision moved to the "
          "usual reading (the note applied where it does not fit). Decisions read from the SQL by code. The note itself: method.md "
          "Appendix M2 (NOTE).\n"]
    for m in EM:
        base = "%s/runs/%s" % (P.OUT, re.sub(r"\W", "_", m)); gain, loss = [], []
        for k, t in T.items():
            pl, nt = json.load(open("%s/plain/%s.json" % (base, k))), json.load(open("%s/defaults/%s.json" % (base, k)))
            if pl["pass"] == nt["pass"]: continue
            sp, sn = I.sides(pl.get("final") or "", t["instruction"]), I.sides(nt.get("final") or "", t["instruction"])
            moved = [kk for kk in U if kk in sp and kk in sn and sp[kk] != sn[kk] and sn[kk] == U[kk]]
            if moved: (gain if nt["pass"] else loss).append((len(t["instruction"]), k, moved))
        for tag, picks in (("became right", sorted(gain)[:2]), ("became wrong", sorted(loss)[:1])):
            for _n, k, moved in picks:
                t = T[k]; pl, nt = json.load(open("%s/plain/%s.json" % (base, k))), json.load(open("%s/defaults/%s.json" % (base, k)))
                X += ["### %s, %s %s: %s (moved: %s)" % (LABEL[m], k, t["database"], tag, ", ".join(x.replace("_", " ") for x in moved)),
                      "Question: %s  " % " ".join(t["instruction"].split()),
                      "Reference:\n```sql\n%s\n```" % " ".join(t["reference_sql"].split()),
                      "Without the note:\n```sql\n%s\n```" % " ".join((pl.get("final") or "").split()),
                      "With the note:\n```sql\n%s\n```\n" % " ".join((nt.get("final") or "").split())]
    open("paper/example.md", "w").write("\n".join(X) + "\n")


# =========================================================================== method.md generated parts
def method():
    s = open("paper/method.md").read()
    for tag, f, title in (("PARAMETERS", "out/paper/methods/PARAMETERS.md", "## Appendix M1. Parameters, budgets, seeds and versions (generated)"),
                          ("PROMPTS", "out/paper/methods/PROMPTS.md", "## Appendix M2. Prompts, verbatim (generated)")):
        body = open(f).read().split("\n", 1)[1].replace("\n## ", "\n### ")
        s = re.sub(r"<!-- BEGIN GENERATED: %s -->.*?<!-- END GENERATED: %s -->" % (tag, tag),
                   lambda _m: "<!-- BEGIN GENERATED: %s -->\n%s\n%s\n<!-- END GENERATED: %s -->" % (tag, title, body.strip(), tag), s, flags=re.S)
    open("paper/method.md", "w").write(s)


if __name__ == "__main__":
    result(); example(); method(); print("paper/result.md, paper/example.md, paper/method.md written")
