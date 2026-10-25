# SpecBridge: PVLDB (Vol. 20) manuscript

This folder is self-contained: upload it as is to Overleaf (main document `specbridge.tex`, compiler pdfLaTeX) or build it locally with `make`.

| File or folder | What it is |
|---|---|
| `specbridge.tex` → `specbridge.pdf` | The whole paper in one file. Body on pages 1–12 (no appendix), references from page 13. |
| `supplement.tex` → `supplement.pdf` | The whole supplementary material in one file: only what the paper leaves out (query generation details, library composition, a second worked example, the nine-case survey, further details, pilots). Its figures and tables are S1, S2, ...; its references to the paper print the paper's numbers. |
| generated regions | Lines between `% >>> name` and `% <<< name` are written by tools, never by hand: the three data tables in `specbridge.tex` (`python -m specbridge.report.tables_tex`) and each file's `labels` region (the other document's `\newlabel` lines, written by `make`), so either file compiles alone, e.g. on Overleaf. |
| `figures/` | `col_*.pdf` (data figures), `diag_*.pdf` (diagrams); `tikz/` holds the diagram sources. Captions are in the two `.tex` files. |
| `fig_explain.md`, `tab_explain.md` | The source and meaning of every figure and table. |
| `acmart.cls`, `pvldb.sty`, `ACM-Reference-Format.bst` | Pinned copies of the official [PVLDB template](https://github.com/vldbproceedings/VLDB-Template) (acmart v2.19, `sigconf, nonacm`). |
| `references.bib` | Bibliography. |

## Build

`make` (from this folder) builds the three diagrams with XeLaTeX, then the paper, writes its labels into `supplement.tex`, builds the supplement, writes its labels into `specbridge.tex`, and builds the paper again. Overleaf: upload the two `.tex` files, `references.bib`, the three template files and `figures/`; set the main document to `specbridge.tex` (or `supplement.tex`).

## Regenerate figures and tables

From the repository root:

```sh
python -m specbridge.report.figures_col   # data figures -> figures/col_*.pdf (NumPy, Matplotlib, Arial)
python -m specbridge.report.tables_tex    # generated tables -> their regions in specbridge.tex (copies in out/paper/tables/)
make -C paper/tex                         # diagrams (XeLaTeX, Arial, fontawesome5) and both PDFs
```

The other tables are written by hand; their numbers come from `paper/result.md` and `paper/example.md`. All figure text is Arial, in black, with no white fills; figures are one column wide and printed at 1:1.

## Submission rules

The [PVLDB Vol. 20 guidelines](https://www.vldb.org/pvldb/volumes/20/submission) allow twelve pages excluding references, appendices included. Review is single-blind. Code and data must be in a public archival repository. Before submission, fill the placeholders in `specbridge.tex` (co-authors, DOI, pages), and make the availability URL point to a public repository. Raw AMBROSIA outputs stay out of that repository at the AMBROSIA authors' request.
