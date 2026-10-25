# Text-to-SQL Models Make Choices Without Saying So — reproducibility package

Artifact of the PVLDB Experiment, Analysis & Benchmark paper *Text-to-SQL Models Make Choices Without Saying So*. It contains:

| | What | Where |
|---|---|---|
| 1 | **The request-set benchmark**: 307 request sets on 12 databases (215 main, 92 with an added filter), 204 accepted by an author's review (161 and 43); databases and an execution scorer | `benchmark/` |
| 2 | **The choice library**: reviewed choices of meaning mined from BIRD and Spider failures (Figure 4); the file also keeps the output-format failures and the choice points of solved questions, marked in `provenance` | `library/` |
| 3 | **The disclosure method** (Section 7.1, Figure 17): list the readings, answer each in its own call, show an alternative only when its result differs | `methods/disclose.py` |
| 4 | **The clarification design** (Section 7.3): keep the request and add one clause, with the two rewrite baselines | `methods/clarify.py` |
| 5 | The full code base, every saved model run behind a reported result, the generator's inputs, the author's reviews, and the paper source | see below |

## Reproduce everything (no model access needed, about 6 minutes)

```sh
make setup        # pip install -r requirements.txt  (Python 3.11)
make all          # fetch the BIRD dev databases, rebuild every figure and table, compare with the paper, run the tests
```

`make all` runs four steps, each also available alone:

| Step | What it does |
|---|---|
| `make data` | `reproduce/fetch_bird.sh`: the BIRD dev databases from the BIRD authors (346 MB download), checked against `reproduce/bird_dev.sha256` |
| `make reproduce` | rebuilds every figure and table of the paper from the saved runs (no model calls, about 4 minutes) |
| `make check` | compares with the paper: data files, generated tables, figure pixels, every number printed in the text, the frozen review |
| `make test` | the methods and prompts against the experiment code; every reference query matches its own reading; the AMBROSIA table from the scores-only file |

It ends with `ALL OUTPUTS REPRODUCED` and a ledger line with 0 mismatches. Figures match pixel for pixel when Arial is installed
(the paper's figure font); data files, tables and numbers match on any system. `make paper` builds the paper (pdfLaTeX; the
diagrams use XeLaTeX with Arial), and `make full-data` fetches the 155 source databases needed only to rerun query generation.

## What is where

```
benchmark/          request_sets.jsonl (307 sets), databases/ (12 SQLite files), score.py, examples/ (four models' answers)
library/            the choice library (examples.jsonl, defects.jsonl)
methods/            the disclosure method and the clarification design, standalone
human_supervision/  the author's reviews: request sets, minority references, BIRD other readings
reproduce/          check.py, expected/ (the paper's outputs), tests, fetch scripts with checksums
specbridge/         the full code base; docs/ describes the query language and the pipeline
out/                every saved model run and result behind the paper (map below)
catalogues/         column meanings per database, the generator's input
spider_data/, train_meta/, dev_unzipped/   Spider and BIRD files, at the paths their releases use (BIRD dev databases: make data)
paper/              the paper and supplement source
```

| `out/` folder | What it holds (paper section) |
|---|---|
| `corpora/`, `coverage/`, `feasibility/`, `ablation/`, `profiles/`, `rules/`, `gamma_pool/` | query generation: the corpora, which databases it runs on and its coverage, the ablation, mined templates (§2.2, §4.2) |
| `comm_library/`, `diagnose_coverage/` | mining choices from BIRD and Spider failures, per batch, and the questions covered (§2.3) |
| `transfer/` | the request sets: `eval12-v2/` (215 main sets: construction and review), `ext/` (92 filter sets), `all/render/` (every model run on all 307 sets) (§2, §5) |
| `writer_swap/` | the writer swap (§4.2) |
| `confirmation/` | held-out BIRD and Spider questions, causes (§6) |
| `impact/`, `rescore/` | the effect of the other reading; BIRD scored with both readings (§6) |
| `ambrosia/`, `reqmethod100/` | disclosure methods on AMBROSIA (aggregates only) and on 100 request sets (§7.2) |
| `rewrite/` | edit vs rewrite, on request sets and on BIRD (§7.3) |

## Use the benchmark and the methods

```python
from benchmark.score import load, run, matches
sets = load()                                     # the 204 accepted sets
s = sets["06768b2b94"]                            # the film request of Figure 1
s["requests"]["open"], s["readings"], s["context"]["schema"]
matches(s, run(s, "SELECT ..."))                  # -> ["A"], ["B"], ["A", "B"] or []

from methods.disclose import disclose             # ask(prompt) -> reply text; any model
out = disclose(question, schema_text, "benchmark/databases/sakila_1.sqlite", ask)

from methods.clarify import edit
request = edit(open_request, reading)             # the recommended way to carry a clarification
```

`methods/models.py` gives the model access the paper used (`claude` CLI and `codex exec`, sealed: no tools, an empty directory).
`python methods/clarify.py --model sonnet` reruns the clarification test on the benchmark.

## Where each figure and table comes from

`make reproduce` runs the reports listed in the `Makefile`, ending with `specbridge.report.exhibit_data` (writes `out/paper/data/*.json`),
`specbridge.report.accepted`, `specbridge.report.figures_col` (figures) and `specbridge.report.tables_tex` (generated tables).

| Exhibit | Built from | By |
|---|---|---|
| Fig. 1, 2, 3, 17, 20 (diagrams) | values from `sakila_1`, `insider`, `financial` and the recorded responses | `paper/tex/figures/tikz/*.tex` (XeLaTeX) |
| Table 1 (comparison) | properties of the cited benchmarks | `tables_tex.comparison` |
| Fig. 4 (choice types) | `library/examples.jsonl` → `tab2_library.json`; request sets per type from `fig5_tab4_disclosure.json` | `figures_col.choices` |
| Table 2 (how the measures score four responses) | recorded responses in `out/transfer/all/render/disclose/` | written in the paper |
| Fig. 5 (construction funnel) | `tab3_generation.json`, `out/transfer/ext/cp/INVENTORY.md`, `out/transfer/ext/render/selection.json`, `filter_sets.json` | `figures_col.funnel` |
| Fig. 6 (generation ablation) | `out/ablation/`, `out/coverage/` → `fig1_coverage.json` | `figures_col.ablation` |
| Fig. 7 (exact description vs natural request) | `out/corpora/` runs → `fig2_explicit_vs_precise.json` | `figures_col.specification` |
| Fig. 8 (answering and communicating) | `out/transfer/all/render/disclose/` → `fig5_tab4_disclosure.json` | `figures_col.disclosure` |
| Fig. 9 (missed readings the model computes) | Fig. 8 data, `disclose/complement/`, `out/ambrosia/decomposition*.json` | `figures_col.decomposition` |
| Fig. 10 (outcome of every open request) | `accepted.json` (`outcomes`) | `figures_col.outcomes` |
| Fig. 11 (by choice type and source) | `fig5_tab4_disclosure.json` | `figures_col.bytype` |
| Fig. 12 (silent choices follow conventions) | tie and counting sets → `conventions.json` (`specbridge.report.conventions`) | `figures_col.conventions` |
| Fig. 13, 14 (held-out benchmarks, causes) | `out/confirmation/` → `fig3_real_benchmarks.json` | `figures_col.real`, `.causes` |
| Fig. 15 (conventions by author group) | Spider and BIRD train/dev SQL → `fig6_inclination.json` | `figures_col.defaults` |
| Fig. 16 (effect of the other reading) | BIRD dev → `out/impact/impact.json` (`specbridge.report.impact impact`) → `fig_impact.json` | `figures_col.impact` |
| Table 3, and BIRD scored with both readings (Section 6) | `out/rescore/runs/`, author review `human_supervision/bird-other-reading.csv` → `out/rescore/results.json` | `specbridge.comm.transfer.rescore report` |
| Fig. 18 (method on AMBROSIA) | `out/ambrosia/final/final.json` | `figures_col.method` |
| Table 4 (disclosure methods) | `out/ambrosia/final/` and `out/reqmethod100/results.json`; the AMBROSIA columns also from `scores.jsonl` | `tables_tex.methods`, `reproduce/ambrosia_tables.py` |
| Fig. 19 (DtP break-even) | `out/ambrosia/final/exchange.json` | `figures_col.breakeven` |
| Fig. 21 (edit vs rewrite) | `out/rewrite/runs/`, `out/rewrite/classify.json` | `figures_col.rewrite` |
| BIRD clarification test (Section 7.3) | `out/rewrite/bird/runs/` | `specbridge.report.numbers` (`bird_clar`) |
| Finding 1 numbers in the text | `out/paper/data/accepted.json` | `specbridge.report.accepted` |
| Database scan (Section 6) | `out/impact/AUDIT.md`, `audit.json` | `specbridge.report.impact audit` |
| Supplement figures and tables | `filter_sets.json`, `fig1_coverage.json`, `tab3_generation.json` | `figures_col.filters`, `.coverage` |

`paper/tex/fig_explain.md` and `paper/tex/tab_explain.md` give the source of every exhibit; `specbridge/report/numbers.py` gives
the source of every number in the text.

**Which BIRD edits count as a valid other reading.** Section 6 applies the library's SQL edit to BIRD references. An edit counts only
when `specbridge.comm.diagnose.rules.alternative_ok` accepts it: counts go from rows to distinct entities (never the reverse), a count
inside a ratio is edited only when the other side already counts distinct values, and a join is edited only when the joined table adds
an output column and no condition. The author reviewed every BIRD question on which a model's answer matched only the edited query
(`human_supervision/bird-other-reading.csv`, with reasons); the rule agrees with all 39 verdicts (`out/rescore/results.json`,
`rule_vs_author`).

## The experiments (with model access)

To rerun query generation or the 152-database coverage run, first fetch the 155 source databases the generator runs on:
`sh reproduce/fetch_databases.sh` (83 MB release asset, checked against `reproduce/source_databases.sha256`). The generator's other
inputs ship here: `catalogues/<db>.json` (column meanings, built once per database by `python -m specbridge.pd.realize.semantic <db>`),
`out/profiles/<source>/templates.jsonl` (query templates mined from BIRD and Spider references) and `out/gamma_pool/tasks.jsonl`.

Every experiment appends one file per answered item and resumes from the files, so a rerun only asks for what is missing. At most
six calls run at once. Models: Claude Haiku, Sonnet and Opus through the `claude` CLI (2.1.287–2.1.300), GPT-Sol and GPT-Luna
(`gpt-6-sol`, `gpt-6-luna`) through `codex exec` (0.147–0.160, reasoning effort medium). Per-call model snapshots and token counts
were not recorded for the paper's runs; `specbridge/pd/ask.py` now records both for new runs (`USAGE.last`).

| Experiment (paper section) | Command | Saved runs |
|---|---|---|
| Query generation, coverage, ablation (§2.2, §4.2) | `python -m specbridge.comm setup|build|natural ...` (see `specbridge/docs/PIPELINE.md`); `python -m specbridge.comm.construct.coverage run`; `python -m specbridge.comm.construct.ablation run` | `out/coverage/`, `out/ablation/`, `out/corpora/` |
| Mining choices from benchmark failures (§2.3) | `specbridge.comm.diagnose`: `tasks` (two wordings) → `compare run` → `inspect` → `record` → `gate` → `library`; `batches` runs them per batch (each module's docstring gives its command) | `out/comm_library/`, `library/` |
| Exact description vs natural request (§4.2) | `python -m specbridge.comm.construct.solver_eval <corpus> [--explicit]` | `out/corpora/` |
| Writer swap (§4.2) | `python -m specbridge.comm.construct.writer_swap` | `out/writer_swap/` |
| Specific requests with exploration (§5) | `python -m specbridge.comm.transfer.evaluate out/transfer/all/render run <model>` | `.../render/eval/runs/` |
| Explanation call and plain control (§5) | `python -m specbridge.comm.transfer.disclose out/transfer/all/render run|plain|judge` | `.../render/disclose/` |
| Matched single call (§5) | `python -m specbridge.comm.transfer.matched run` | `.../disclose/complement/` |
| Five samples (§5) | `python -m specbridge.comm.transfer.topk run` | `.../disclose/topk/` |
| AMBROSIA decomposition and final method test (§5, §7.2) | `sh reproduce/fetch_ambrosia.sh`, then `python -c "from specbridge.comm.transfer import ambrosia as A; A.decomp_run(A.MODELS); A.run_final()"` | aggregates in `out/ambrosia/` |
| Held-out BIRD and Spider, causes (§6) | `python -m specbridge.comm.diagnose.compare run <dir> <model>`; `python -m specbridge.comm.diagnose.explore_ablation run <model>` | `out/confirmation/` |
| BIRD scored with both readings (§6, Table 3) | `python -m specbridge.comm.transfer.rescore run` (protocol `out/rescore/PROTOCOL.md`, written before the run) | `out/rescore/runs/` |
| Request-set methods (§7.2) | `REQMETHOD_OUT=out/reqmethod100 REQMETHOD_N=100 python -m specbridge.comm.transfer.reqmethod run` | `out/reqmethod100/` |
| Edit vs rewrite (§7.3) | `python -m specbridge.comm.transfer.rewrite run|classify|report`; BIRD: `bird` | `out/rewrite/` |

The request sets themselves come from the pipeline in `specbridge/comm/transfer/` (choice points, rendering, review, freeze); the
author's reviews are in `human_supervision/`, and `specbridge/comm/transfer/reviewed.py` restricts every report to the accepted sets
(`SB_ALL_SETS=1` restores all 215).

## Environment

Results were produced on an Apple M2 Max laptop (12 cores, 32 GB) with Python 3.11.5 and SQLite 3.41.2; no GPU, no special
hardware. The rebuild needs only the Python packages in `requirements.txt` and the BIRD dev databases. Rerunning experiments needs
access to the models above.

## What is not included

Nothing from the paper's experiments is withheld except, at their authors' request, AMBROSIA's own content: the per-call AMBROSIA
runs contain the models' restatements of AMBROSIA questions and SQL that often equals AMBROSIA's gold SQL, so the package ships the
aggregates and `out/ambrosia/final/scores.jsonl` (per question and arm: readings found, wrong queries, calls), from which Table 4
and Figures 9, 18 and 19 are recomputed. Rerunning the AMBROSIA experiments regenerates the runs (`reproduce/fetch_ambrosia.sh`).
LiveSQLBench's withheld reference SQL was never used. Experiments that are not in the paper (an in-context checklist, Spider 2.0,
earlier pilots) and run logs are left out.

## Data and licences

See `DATA_LICENSE.md`. Code: MIT. Benchmark, library and saved outputs: CC BY-SA 4.0 (they derive from Spider and BIRD).
AMBROSIA is not redistributed, at its authors' request; the package ships aggregate results and a scores-only table, and
`reproduce/fetch_ambrosia.sh` fetches the rest from the authors. The BIRD dev databases are fetched by `reproduce/fetch_bird.sh`.
