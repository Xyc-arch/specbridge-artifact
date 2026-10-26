# Figure sources

Every figure of the paper and the supplement (`figures/*.pdf`) is built from these files with pdfLaTeX, in the paper's own
fonts, at its printed width; the paper includes each PDF at 1:1.

| File | What it is |
|---|---|
| `sbstyle.tex` | The shared style: fonts, the one text size, colors and what they mean, axes, legend keys, diagram boxes. |
| `col_*.tex` | Data figures (pgfplots). Each reads its files in `data/`. |
| `diag_*.tex` | Diagrams (TikZ). Their values are written in the files. |
| `data/` | CSV files (and tick-label lists) written by `export.py`. |
| `export.py` | Writes `data/` from the artifact repository's data files, with the arithmetic of `specbridge/report/figures_col.py`. |
| `build.py` | Builds figures and copies each PDF to `figures/`. |

## Rebuild

```sh
python3 -I export.py /path/to/specbridge-artifact data   # only when the data change
python3 build.py                                          # every figure
python3 build.py col_funnel diag_teaser                   # some figures
```

`build.py` needs pdfLaTeX (TeX Live with pgfplots, libertine, zi4 and newtx) and Ghostscript, which it uses to keep every figure
exactly one column (241.15 pt) or two columns (506.3 pt) wide.

## Style

- Text: Linux Biolinum 7.5 pt, the sans companion of the body font; SQL in Inconsolata 7 pt; hierarchy by weight, not size.
- A figure uses one color family: models (purple = Claude, green = GPT, lighter = the smaller model), or readings
  (blue = A, orange = B), or outcomes (dark = the wanted outcome or our method, grays = baselines and other categories,
  red = the problem).
- Left and bottom axes only, light grid on the value axis, flat bars, intervals without caps, legends above the plot.
  When every bar carries its value, the value axis is left out.

The diagram `diag_datamap.tex` restyles the file that `python -m specbridge.report.datamap_tex` writes in the repository; a new
run of that script writes the old style.
