.PHONY: all clean figures check numbers
# One .tex file per document: specbridge.tex (the paper) and supplement.tex. They cite each other: make copies each one's
# \newlabel lines into the other's "labels" region, so either file compiles on its own (e.g. on Overleaf).
# Order: figures (pdfLaTeX) -> paper -> its labels into the supplement -> supplement -> its labels into the paper -> paper.
LABELS = PYTHONPATH=../.. python3 -m specbridge.report.texfile labels
all: figures
	latexmk -pdf -interaction=nonstopmode -halt-on-error specbridge.tex
	$(LABELS) specbridge.aux supplement.tex "labels specbridge"
	latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
	$(LABELS) supplement.aux specbridge.tex "labels supplement" ext-
	latexmk -pdf -interaction=nonstopmode -halt-on-error specbridge.tex
	$(LABELS) specbridge.aux supplement.tex "labels specbridge"

# Every figure from its source in figures/src (pgfplots and TikZ in the paper's fonts; figures/src/README.md), rebuilt when the
# source, the shared style or a data file is newer than the PDF. figures/tikz/ (XeLaTeX, Arial) is legacy: no target builds it.
FIGURES = $(patsubst figures/src/%.tex,figures/%.pdf,$(wildcard figures/src/col_*.tex figures/src/diag_*.tex))
figures: $(FIGURES)
figures/%.pdf: figures/src/%.tex figures/src/sbstyle.tex $(wildcard figures/src/data/*)
	python3 figures/src/build.py $*

# Every number printed in specbridge.tex and supplement.tex, recomputed from the data files (specbridge.report.numbers).
check: numbers
numbers:
	PYTHONPATH=../.. python3 -m specbridge.report.numbers check
	cd ../.. && python3 -m specbridge.comm.transfer.freeze check

clean:
	latexmk -c specbridge.tex supplement.tex
