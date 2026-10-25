.PHONY: all clean diagrams check numbers
# One .tex file per document: specbridge.tex (the paper) and supplement.tex. They cite each other: make copies each one's
# \newlabel lines into the other's "labels" region, so either file compiles on its own (e.g. on Overleaf).
# Order: diagrams (XeLaTeX, Arial) -> paper -> its labels into the supplement -> supplement -> its labels into the paper -> paper.
LABELS = PYTHONPATH=../.. python3 -m specbridge.report.texfile labels
all: diagrams
	latexmk -pdf -interaction=nonstopmode -halt-on-error specbridge.tex
	$(LABELS) specbridge.aux supplement.tex "labels specbridge"
	latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
	$(LABELS) supplement.aux specbridge.tex "labels supplement" ext-
	latexmk -pdf -interaction=nonstopmode -halt-on-error specbridge.tex
	$(LABELS) specbridge.aux supplement.tex "labels specbridge"

diagrams: figures/diag_teaser.pdf figures/diag_pipeline.pdf figures/diag_worked.pdf figures/diag_method.pdf figures/diag_rewrite.pdf
figures/diag_%.pdf: figures/tikz/%.tex figures/tikz/style.tex
	cd figures/tikz && xelatex -interaction=nonstopmode -halt-on-error $*.tex >/dev/null && cp $*.pdf ../diag_$*.pdf && rm -f $*.pdf $*.aux $*.log

# Every number printed in specbridge.tex and supplement.tex, recomputed from the data files (specbridge.report.numbers).
check: numbers
numbers:
	PYTHONPATH=../.. python3 -m specbridge.report.numbers check
	cd ../.. && python3 -m specbridge.comm.transfer.freeze check

clean:
	latexmk -c specbridge.tex supplement.tex
