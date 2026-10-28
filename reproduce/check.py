"""Compare the rebuilt outputs with the outputs behind the paper: every figure/table data file (JSON, exact), every generated
table (out/paper/tables/*.tex, exact; the same text sits in its region of paper/tex/specbridge.tex), the data files behind
every printed figure (paper/tex/figures/src/data, exact) and every check drawing of figures_col (pixels at 100 dpi, exact).
Exit 1 on any difference.
    python reproduce/check.py"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, "."); import specbridge, sqlite3                       # specbridge selects the SQLite that runs every query
_v = tuple(map(int, sqlite3.sqlite_version.split(".")))
print("SQL engine: SQLite %s (%s)%s" % (sqlite3.sqlite_version, sqlite3.__name__, "" if _v < (3, 43) else
      "; WARNING: SQLite 3.43 and later sum floats differently, so a few results differ from the paper (see README)"))
E = "reproduce/expected"; bad = 0
for f in sorted(os.listdir(E + "/out/paper/data")):
    if not f.endswith(".json"): continue
    a, b = json.load(open(os.path.join(E, "out/paper/data", f))), json.load(open("out/paper/data/" + f))
    a.pop("note_experiment", None); b.pop("note_experiment", None)        # not in the paper; its data is not shipped
    ok = a == b; bad += not ok; print("%-4s data   %s" % ("ok" if ok else "DIFF", f))
for f in sorted(os.listdir(E + "/out/paper/tables")):
    ok = open(os.path.join(E, "out/paper/tables", f)).read() == open("out/paper/tables/" + f).read(); bad += not ok
    print("%-4s table  %s" % ("ok" if ok else "DIFF", f))
    ok = open("out/paper/tables/" + f).read().strip() in open("paper/tex/specbridge.tex").read(); bad += not ok
    print("%-4s table  %s, as printed in paper/tex/specbridge.tex" % ("ok" if ok else "DIFF", f))
def pixels(pdf):
    d = tempfile.mkdtemp(); subprocess.run(["pdftoppm", "-r", "100", "-png", pdf, d + "/p"], check=True)
    return b"".join(open(os.path.join(d, x), "rb").read() for x in sorted(os.listdir(d)))
P = "paper/tex/figures/src/data"                                        # what the printed (pgfplots) figures read
for f in sorted(os.listdir(P)):
    ok = os.path.exists("out/paper/figure_data/" + f) and open(os.path.join(P, f), "rb").read() == open("out/paper/figure_data/" + f, "rb").read()
    bad += not ok; print("%-4s figure data %s" % ("ok" if ok else "DIFF", f))
def why_no_pixels():
    """The pixel comparison needs pdftoppm (poppler) and the Arial font; without them it is skipped, never failed."""
    import shutil
    if not shutil.which("pdftoppm"): return "pdftoppm (poppler) is not installed"
    from matplotlib import font_manager
    try: font_manager.findfont("Arial", fallback_to_default=False)
    except ValueError: return "the Arial font is not installed"
skip = why_no_pixels()
if skip: print("skip figure pixels: %s; the figure data above are compared exactly" % skip)
for f in sorted(os.listdir(E + "/figures_col")) if not skip else []:
    if not f.endswith(".pdf"): continue
    ok = pixels(os.path.join(E, "figures_col", f)) == pixels("out/paper/figures_col/" + f); bad += not ok
    print("%-4s figure %s" % ("ok" if ok else "DIFF", f))
print("\n%s" % ("ALL OUTPUTS REPRODUCED" if not bad else "%d DIFFERENCES" % bad)); sys.exit(1 if bad else 0)
