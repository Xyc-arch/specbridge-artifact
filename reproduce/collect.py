"""Collect everything `make reproduce` produced into results/, named after the paper's figures and tables.
    python reproduce/collect.py"""
import os, shutil

OUT = "results"
FIGURES = {"fig04": "choices", "fig05": "funnel", "fig06": "ablation", "fig07": "specification", "fig08": "disclosure",
           "fig09": "decomposition", "fig10": "outcomes", "fig11": "bytype", "fig12": "conventions", "fig13": "real",
           "fig14": "causes", "fig15": "defaults", "fig16": "impact", "fig18": "method", "fig19": "breakeven", "fig21": "rewrite",
           "figS2": "coverage"}
TABLES = {"table1_comparison.tex": "out/paper/tables/comparison.tex", "table3_bird_rescoring.json": "out/rescore/results.json",
          "table4_methods.tex": "out/paper/tables/methods.tex"}

INDEX = """# Results of your run

Everything here was produced on your machine by `make reproduce`, from the saved model runs in `out/`.

| Folder or file | What it holds |
|---|---|
| `figures/` | every data figure of the paper, named by its number (`fig08_disclosure.pdf` is Figure 8; `figS2` is in the supplement) |
| `tables/` | Tables 1 and 4 as LaTeX, and the numbers of Table 3 (BIRD scored with both readings) |
| `data/` | the numbers behind each figure and table, as JSON |
| `check.txt` | the comparison with the paper (written by `make check`) |
| `numbers.txt` | every number printed in the paper, its value recomputed from the data, and whether they match (`make check`) |
| `tests.txt` | the test results (written by `make test`) |

Figures 1, 2, 3, 17 and 20 are diagrams drawn by hand (`paper/tex/figures/tikz/`), and Table 2 is written in the paper.
"""


def main():
    for d in ("figures", "tables", "data"):
        shutil.rmtree(os.path.join(OUT, d), ignore_errors=True); os.makedirs(os.path.join(OUT, d))
    for k, v in FIGURES.items():
        shutil.copy2("paper/tex/figures/col_%s.pdf" % v, "%s/figures/%s_%s.pdf" % (OUT, k, v))
    for k, v in TABLES.items():
        shutil.copy2(v, "%s/tables/%s" % (OUT, k))
    for f in sorted(os.listdir("out/paper/data")):
        if f.endswith(".json"): shutil.copy2("out/paper/data/" + f, "%s/data/%s" % (OUT, f))
    open(OUT + "/README.md", "w").write(INDEX)
    n = sum(len(os.listdir(os.path.join(OUT, d))) for d in ("figures", "tables", "data"))
    print("results/: %d files (figures, tables, data); see results/README.md" % n)


if __name__ == "__main__":
    main()
