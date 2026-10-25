.PHONY: all setup data full-data reproduce check test paper
# make all: fetch the BIRD dev databases, rebuild every figure and table from the saved runs (no model calls), compare with the
# paper, and run the tests. About 6 minutes on a laptop.
all: data reproduce check test

setup:
	pip install -r requirements.txt

# BIRD dev databases (Section 6, Section 7.3); fetched once, checked against reproduce/bird_dev.sha256
data: dev_unzipped/dev_20240627/dev_databases/financial/financial.sqlite
dev_unzipped/dev_20240627/dev_databases/financial/financial.sqlite:
	sh reproduce/fetch_bird.sh

# the 155 source databases, needed only to rerun query generation (Sections 2.2, 4.2)
full-data:
	sh reproduce/fetch_databases.sh

reproduce: data
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

# data files, generated tables and figure pixels against the paper's; every number printed in the paper; the frozen review
check:
	python reproduce/check.py
	python -m specbridge.report.numbers check --release
	python -m specbridge.comm.transfer.freeze check

test:
	python reproduce/test_release.py
	python benchmark/score.py --self-test
	python reproduce/ambrosia_tables.py

paper:
	$(MAKE) -C paper/tex
