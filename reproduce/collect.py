"""Collect everything `make reproduce` produced into results/, named after the paper's figures and tables.
    python reproduce/collect.py"""
import os, shutil

OUT = "results"
FIGURES = {"fig04": "choices", "fig05": "funnel", "fig06": "disclosure", "fig07": "decomposition", "fig08": "outcomes",
           "fig09": "bytype", "fig10": "conventions", "fig11": "real", "fig12": "causes", "fig13": "defaults", "fig14": "impact",
           "fig16": "method", "fig17": "breakeven", "fig19": "rewrite", "figS2": "ablation", "figS3": "specification", "figS4": "coverage"}
TABLES = {"table1_comparison.tex": "out/paper/tables/comparison.tex", "table4_bird_rescoring.json": "out/rescore/results.json",
          "table5_methods.tex": "out/paper/tables/methods.tex"}

INDEX = """# Results of your run

Everything here was produced on your machine by `make reproduce`, from the saved model runs in `out/`.

| Folder or file | What it holds |
|---|---|
| `figures/` | every data figure, drawn from your run with matplotlib and named by its number (`fig06_disclosure.pdf` is Figure 6; `figS2`–`figS4` are in the supplement); the paper prints the same data with pgfplots (`make figures`) |
| `figure_data/` | the files the paper's printed figures read (`paper/tex/figures/src/data`), written from your run |
| `tables/` | Tables 1 and 5 as LaTeX, and the numbers of Table 4 (BIRD scored with both interpretations) |
| `data/` | the numbers behind each figure and table, as JSON |
| `check.txt` | the comparison with the paper (written by `make check`) |
| `numbers.txt` | every number printed in the paper, its value recomputed from the data, and whether they match (`make check`) |
| `tests.txt` | the test results (written by `make test`) |

Figures 1, 2, 3, 15, 18 and S1 are diagrams (`paper/tex/figures/src/diag_*.tex`), and Table 2 is written in the paper.
"""


def main():
    for d in ("figures", "figure_data", "tables", "data"):
        shutil.rmtree(os.path.join(OUT, d), ignore_errors=True); os.makedirs(os.path.join(OUT, d))
    for k, v in FIGURES.items():
        shutil.copy2("out/paper/figures_col/col_%s.pdf" % v, "%s/figures/%s_%s.pdf" % (OUT, k, v))
    for k, v in TABLES.items():
        shutil.copy2(v, "%s/tables/%s" % (OUT, k))
    for f in sorted(os.listdir("out/paper/data")):
        if f.endswith(".json"): shutil.copy2("out/paper/data/" + f, "%s/data/%s" % (OUT, f))
    for f in sorted(os.listdir("out/paper/figure_data")): shutil.copy2("out/paper/figure_data/" + f, "%s/figure_data/%s" % (OUT, f))
    open(OUT + "/README.md", "w").write(INDEX)
    n = sum(len(os.listdir(os.path.join(OUT, d))) for d in ("figures", "figure_data", "tables", "data"))
    print("results/: %d files (figures, tables, data); see results/README.md" % n)


if __name__ == "__main__":
    main()
