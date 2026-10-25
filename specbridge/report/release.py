"""BUILD THE PVLDB EA&B REPRODUCIBILITY PACKAGE (2026-10-15) -> release/.
The package is self-contained: the benchmark (request sets + databases + scorer), the decision library, the two methods as standalone
code, the full code base (white box), every input the paper's figures and tables are rebuilt from (found by tracing the rebuild), the
expected outputs, and the paper source. Third-party data whose authors ask not to redistribute it (AMBROSIA) is fetched, not shipped.
    python -m specbridge.report.release [inputs.json]   # inputs.json: {"reads": [...]} from tracing the rebuild"""
import json, os, shutil, sys
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import reviewed as RV

DEST = "release"; R = "out/transfer/eval12-v2/render"; RF = "out/transfer/ext/render"
EXCLUDE = ("out/prior/", "out/feasibility/livesqlbench_gt", "ambrosia_data/", "paper/", "out/paper/data/", "release/")
DOCS = ("docs/OBJECTIVE.md", "docs/PIPELINE.md", "docs/LANGUAGE.md")


# run logs and run-status files: not results, and they hold machine details (paths in tracebacks); never shipped
SKIP = ("__pycache__", "*.pyc", ".DS_Store", "*.log", "*_run.txt", "*_run[0-9].txt", "run.txt", "rerun.txt", "*.done", "*.sh",
        "scorer_slow.txt", "vcheck.txt", ".~*")


def cp(src, dst=None):
    import fnmatch
    if any(fnmatch.fnmatch(os.path.basename(src), p) for p in SKIP): return
    dst = os.path.join(DEST, dst or src); os.makedirs(os.path.dirname(dst), exist_ok=True)
    (shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*SKIP)) if os.path.isdir(src) else shutil.copy2(src, dst))


def benchmark():
    C, W = [], {}
    for fam, r in (("main", R), ("filter", RF)):                 # the 215 main sets and the 92 filter sets (paper Section 2)
        cs = json.load(open(r + "/eval/frozen.json"))["cases"]; C += [dict(c, family=fam) for c in cs]; W.update(json.load(open(r + "/written.json")))
    V = json.load(open(RV.VERDICTS)); os.makedirs(DEST + "/benchmark/databases", exist_ok=True); out = []
    for c in sorted(C, key=lambda c: (c["family"] != "main", c["case"])):
        w = W[c["case"]]; sid = c["case"].split("-")[-1]; schema, docs = DB.context(c)
        out.append({"id": sid, "database": c["database"], "source": {"sakila_1": "Spider", "baseball_1": "Spider", "chinook_1": "Spider", "customers_and_invoices": "Spider",
                    "financial": "BIRD", "formula_1": "BIRD", "student_club": "BIRD", "thrombosis_prediction": "BIRD"}.get(c["database"], "LiveSQLBench"),
                    "family": c["family"], "choice_type": c["type"], "choice_kind": c.get("kind"), "review": V[sid]["verdict"], "accepted": V[sid]["verdict"] == "yes",
                    "requests": {"specific_A": w["precise_A"], "specific_B": w["precise_B"], "open": w["open"]},
                    "readings": {"A": w["reading_A"], "B": w["reading_B"]}, "sql": {"A": c["sql_A"], "B": c["sql_B"]},
                    "shared_requirements": w.get("shared"), "choice_components": {"A": w.get("choice_A"), "B": w.get("choice_B")},
                    "context": {"schema": schema, "documentation": docs},
                    "grading": {"grader": c["grader"], "answer_A": c["answer_A"], "answer_B": c["answer_B"], "tie_groups": c.get("tie_groups"),
                                "last_pool": c.get("last_pool"), "B": c.get("B")},
                    "depth": {"arithmetic": c.get("A_depth"), "steps": c.get("S_depth")}})
        db = DEST + "/benchmark/databases/%s.sqlite" % c["database"]
        if not os.path.exists(db): shutil.copy2(c["snapshot"], db)
    with open(DEST + "/benchmark/request_sets.jsonl", "w") as f:
        for o in out: f.write(json.dumps(o, default=str) + "\n")
    print("benchmark:", len(out), "sets,", sum(o["accepted"] for o in out), "accepted")


def code_and_data(inputs):
    cp("specbridge"); shutil.rmtree(DEST + "/specbridge/archive", ignore_errors=True)
    for d in DOCS: cp(d)
    cp("human_supervision")
    reads = [p for p in json.load(open(inputs))["reads"] if not p.startswith("SQLITE:")]
    n = 0
    for p in reads:
        if p.startswith(EXCLUDE) or not os.path.isfile(p) or p.startswith("specbridge/"): continue
        cp(p); n += 1
    # the rebuild reads the 12 databases at out/gamma_pool/snapshot/; point that path at the benchmark's copies (no duplicate files)
    os.makedirs(DEST + "/out/gamma_pool", exist_ok=True)
    link = DEST + "/out/gamma_pool/snapshot"
    if not os.path.lexists(link): os.symlink("../../benchmark/databases", link)
    cp("out/paper/data", "reproduce/expected/out/paper/data"); cp(inputs, "reproduce/inputs.json")
    for f in os.listdir("paper/tex"):
        if f.endswith((".tex", ".bib", ".cls", ".sty", ".bst")) or f in ("Makefile", "README.md", "fig_explain.md", "tab_explain.md", "specbridge.pdf", "supplement.pdf"):
            cp("paper/tex/" + f)
    cp("paper/tex/figures")
    cp("library/examples.jsonl"); cp("library/defects.jsonl")
    print("data files copied:", n)


# results cited in the paper's text but not read by the figure/table rebuild (all licences allow redistribution)
EXTRA = ("out/rescore", "out/rewrite/bird", "out/confirmation/bird_heldout100/runs_noexplore",
         "out/impact", "out/transfer/eval12-v2/compare", "out/writer_swap", "out/rewrite/RESULTS.md", "out/rewrite/classify.json",
         "out/transfer/eval12-v2/render/disclose/judge.json", "out/transfer/eval12-v2/render/disclose/judge_alternatives.json")
# "all experimental data and related software (there are no excuses)": every saved run behind a reported result, and the
# generator's inputs, so the pipeline can be rerun end to end (2026-10-25)
FULL = ("out/corpora", "out/coverage", "out/comm_library", "out/reqmethod", "catalogues", "out/profiles", "out/rules",
        "out/gamma_pool/tasks.jsonl", "out/gamma_pool/pairs.jsonl")
# AMBROSIA: aggregate files only (checked to hold no question, interpretation or SQL text), plus a scores-only table per question
AMBROSIA_AGG = ("out/ambrosia/decomposition.json", "out/ambrosia/decomposition_conf.json", "out/ambrosia/DECOMPOSITION.md",
                "out/ambrosia/DECOMPOSITION_conf.md", "out/ambrosia/results.json", "out/ambrosia/RESULTS.md", "out/ambrosia/method/RESULTS.md",
                "out/ambrosia/final/final.json", "out/ambrosia/final/exchange.json", "out/ambrosia/final/EXCHANGE.md")


def extra():
    for p in EXTRA + FULL + AMBROSIA_AGG:
        if os.path.exists(p): cp(p)
    from specbridge.comm.transfer import exchange as EX, ambrosia as AM
    S = EX.score(); os.makedirs(DEST + "/out/ambrosia/final", exist_ok=True)
    with open(DEST + "/out/ambrosia/final/scores.jsonl", "w") as f:
        for (m, a, row), v in sorted(S.items(), key=lambda kv: (kv[0][0], kv[0][1], str(kv[0][2]))):
            try: cost = json.load(open(AM._ff(a, m, row))).get("cost", {})
            except Exception: cost = {}
            f.write(json.dumps({"model": m, "arm": a, "ambrosia_row": row, "ambiguous": v["amb"], "gold_readings": len(v["row"]["gold"]),
                                "queries_returned": v["n"], "readings_found": v["found"], "wrong_queries": v["wrong"], "calls": cost.get("calls")}) + "\n")
    print("AMBROSIA scores-only rows:", len(S))


def hand_written():
    """release_src/: README, licences, Makefile, scorer, methods, tests, reproduce checks, scripts (kept in the research repo)."""
    shutil.copytree("release_src", DEST, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))


def examples():
    """The four models' single-call answers from the paper, in benchmark/score.py's input format."""
    import ast, glob
    d0 = R + "/disclose"; os.makedirs(DEST + "/benchmark/examples", exist_ok=True)
    for m in ("haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"):
        with open(DEST + "/benchmark/examples/%s_single_call.jsonl" % m, "w") as f:
            for d in (d0 + "/" + m, d0 + "/complement/" + m):
                for p in sorted(glob.glob(d + "/*.json")):
                    o = json.load(open(p)); r = o["response"]
                    if isinstance(r, str):
                        try: r = ast.literal_eval(r)
                        except Exception: r = {}
                    r = r or {}; req = {"precise_A": "specific_A", "precise_B": "specific_B", "open": "open"}[o["wording"]]
                    a = {"id": o["case"].split("-")[-1], "request": req, "sql": r.get("sql")}
                    if req == "open": a["alternatives"] = [x.get("sql") for x in (r.get("alternatives") or [])[:2] if isinstance(x, dict) and x.get("sql")]
                    f.write(json.dumps(a) + "\n")


def expected_outputs():
    """What reproduce/check.py compares against: the paper's figure/table data, generated tables and figures."""
    for t in ("comparison.tex", "methods.tex"):   # 2026-10-24: the generated tables left in the paper
        cp("out/paper/tables/" + t, "reproduce/expected/out/paper/tables/" + t)
    for x in os.listdir("paper/tex/figures"):
        if x.startswith("col_") and x.endswith(".pdf"): cp("paper/tex/figures/" + x, "reproduce/expected/paper/tex/figures/" + x)


if __name__ == "__main__":
    if os.path.exists(DEST): shutil.rmtree(DEST)
    hand_written(); benchmark(); examples(); code_and_data(sys.argv[1] if len(sys.argv) > 1 else "out/release/inputs.json"); extra(); expected_outputs()
