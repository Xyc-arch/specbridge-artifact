.PHONY: reproduce check paper all
# Rebuild every figure and table of the paper from the saved runs (no model calls), then compare with the paper's outputs.
reproduce:
	python -m specbridge.comm.transfer.matched report
	python -m specbridge.comm.transfer.topk report
	python -m specbridge.comm.transfer.rewrite report
	REQMETHOD_OUT=out/reqmethod100 REQMETHOD_N=100 python -m specbridge.comm.transfer.reqmethod report
	python -m specbridge.report.filter_sets
	python -m specbridge.report.impact impact
	python -m specbridge.comm.transfer.rescore report
	python -m specbridge.report.conventions
	python -m specbridge.report.exhibit_data
	python -m specbridge.comm.diagnose.reference_split
	python -m specbridge.report.ambrosia_types
	python -m specbridge.report.accepted
	python -m specbridge.report.figures_col
	python -m specbridge.report.tables_tex
check:
	python reproduce/check.py
	python -m specbridge.report.numbers check --release
	python -m specbridge.comm.transfer.freeze check
paper:
	$(MAKE) -C paper/tex
all: reproduce check paper
