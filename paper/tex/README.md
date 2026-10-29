# SpecBridge: PVLDB (Vol. 20) manuscript

This folder is self-contained: upload it as is to Overleaf (main document `specbridge.tex`, compiler pdfLaTeX) or build it locally with `make`.

| File or folder | What it is |
|---|---|
| `specbridge.tex` → `specbridge.pdf` | The whole paper in one file. Body on pages 1–12 (no appendix), references from page 13. |
| `supplement.tex` → `supplement.pdf` | The whole supplementary material in one file: only what the paper leaves out (query generation details, library composition, a second worked example, the nine-case survey, further details, pilots). Its figures and tables are S1, S2, ...; its references to the paper print the paper's numbers. |
| generated regions | Lines between `% >>> name` and `% <<< name` are written by tools, never by hand: the three data tables in `specbridge.tex` (`python -m specbridge.report.tables_tex`) and each file's `labels` region (the other document's `\newlabel` lines, written by `make`), so either file compiles alone, e.g. on Overleaf. |
| `figures/` | `col_*.pdf` (data figures), `diag_*.pdf` (diagrams), each built from its source in `figures/src/` (pgfplots and TikZ; see its `README.md`). Captions are in the two `.tex` files. `tikz/` holds the earlier XeLaTeX diagram sources, kept as legacy; no target builds them. |
| `acmart.cls`, `pvldb.sty`, `ACM-Reference-Format.bst` | Pinned copies of the official [PVLDB template](https://github.com/vldbproceedings/VLDB-Template) (acmart v2.19, `sigconf, nonacm`). |
| `references.bib` | Bibliography. |

## Build

`make` (from this folder) builds every figure whose source, style or data changed (`python3 figures/src/build.py`, pdfLaTeX; needs TeX Live with pgfplots, libertine, zi4 and newtx, and Ghostscript), then the paper, writes its labels into `supplement.tex`, builds the supplement, writes its labels into `specbridge.tex`, and builds the paper again. Overleaf: upload the two `.tex` files, `references.bib`, the three template files and `figures/`; set the main document to `specbridge.tex` (or `supplement.tex`).

## Regenerate figures and tables

From the repository root, after `make reproduce` (which writes `out/paper/data`):

```sh
python3 -I paper/tex/figures/src/export.py . paper/tex/figures/src/data out/paper/data   # the data figures' numbers -> figures/src/data/
python -m specbridge.report.tables_tex    # generated tables -> their regions in specbridge.tex (copies in out/paper/tables/)
make -C paper/tex                         # every figure whose source or data changed (pdfLaTeX), and both PDFs
python -m specbridge.report.datamap_tex   # Figure S1's counts and exhibit numbers -> figures/src/diag_datamap.tex (reads the .aux files)
```

`make figures` (repository root) runs `make reproduce`, copies the figure data it wrote (`out/paper/figure_data/`) into `figures/src/data/` and builds every figure. The other tables are written by hand. All figure text is set in the paper's fonts (Linux Biolinum 7.5 pt, code in Inconsolata); figures are one column (241.15 pt) or two columns (506.3 pt) wide and printed at 1:1, in the style that `figures/src/README.md` describes. `specbridge.report.figures_col` draws the same data with Matplotlib only as check drawings (`out/paper/figures_col/`, compared by `make check`).

## Submission rules

The [PVLDB Vol. 20 guidelines](https://www.vldb.org/pvldb/volumes/20/submission) allow twelve pages excluding references, appendices included. Review is single-blind. Code and data must be in a public archival repository. Before submission, fill the placeholders in `specbridge.tex` (co-authors, DOI, pages), and make the availability URL point to a public repository. Raw AMBROSIA outputs stay out of that repository at the AMBROSIA authors' request.
