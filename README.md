# Text-to-SQL Models Make Choices Without Saying So

Code, data and saved model runs for our PVLDB paper (Experiment, Analysis & Benchmark track).

Paper: [`paper/tex/specbridge.pdf`](paper/tex/specbridge.pdf) · Supplement: [`paper/tex/supplement.pdf`](paper/tex/supplement.pdf)

A text-to-SQL answer can run, return a plausible number, and still compute something other than what the analyst meant. This
happens when a request leaves a calculation choice open (count rows or count entities?) and the model picks one reading without
saying so. We test this with *request sets*: three requests on the same data, one for each reading and one that leaves the choice
open, all scored by execution.

## Requirements

- Python 3.11 and about 3 GB of free disk space. Any laptop works; no GPU is needed.
- Internet access once, to download the BIRD dev databases (346 MB).
- We used an Apple M2 Max laptop (32 GB RAM), Python 3.11.5 and SQLite 3.41.2.

## Reproduce the paper (about 6 minutes)

```sh
git clone https://github.com/Xyc-arch/specbridge-artifact && cd specbridge-artifact
python3 -m venv .venv      # Python 3.11 && source .venv/bin/activate
make setup     # install the Python packages
make all       # download BIRD dev, rebuild every figure and table, compare with the paper, run the tests
```

No model access is needed: every result is rebuilt from the saved model runs in `out/`. If all is well, you will see these lines near the end:

```
ALL OUTPUTS REPRODUCED
numbers found: 452; in the ledger: 452 (...) ok 398, mismatch 0 (...)
204 sets, 408 reference queries checked, 0 failures
```

`make all` runs four steps, which you can also run one at a time:

| Step | What it does |
|---|---|
| `make data` | downloads the BIRD dev databases and checks them against `reproduce/bird_dev.sha256` |
| `make reproduce` | rebuilds every figure and table from the saved runs |
| `make check` | compares the result with the paper: data, tables, figure pixels, and every number in the text |
| `make test` | tests the scorer, the two methods and their prompts |

Figures match pixel for pixel only when the Arial font is installed; data, tables and numbers match on any system.
`make paper` builds the PDF.

## Where each result comes from

Scripts are in `specbridge/report/` unless a path is given. The numbers behind each figure are written to `out/paper/data/`.

| Paper | Script | Saved runs |
|---|---|---|
| Fig. 1, 2, 3, 17, 20 (diagrams) | `paper/tex/figures/tikz/*.tex` | |
| Table 1 | `tables_tex.py` | properties of the cited benchmarks |
| Table 2 | written in the paper | `out/transfer/all/render/disclose/` |
| Fig. 4 | `figures_col.py` | `library/` |
| Fig. 5 | `figures_col.py` | `out/transfer/` |
| Fig. 6 | `figures_col.py` | `out/ablation/`, `out/coverage/` |
| Fig. 7 | `figures_col.py` | `out/corpora/` |
| Fig. 8–11 | `figures_col.py`, `accepted.py` | `out/transfer/all/render/`, `out/ambrosia/` |
| Fig. 12 | `conventions.py` | `out/transfer/all/render/` |
| Fig. 13, 14 | `figures_col.py` | `out/confirmation/` |
| Fig. 15 | `figures_col.py` | `spider_data/`, `train_meta/` |
| Fig. 16 | `impact.py` | BIRD dev, `out/impact/` |
| Table 3, BIRD scored with both readings (§6) | `specbridge/comm/transfer/rescore.py` | `out/rescore/`, `human_supervision/bird-other-reading.csv` |
| Fig. 18, 19 | `figures_col.py` | `out/ambrosia/final/` |
| Table 4 | `tables_tex.py`, `reproduce/ambrosia_tables.py` | `out/ambrosia/final/`, `out/reqmethod100/` |
| Fig. 21, BIRD clarification (§7.3) | `figures_col.py` | `out/rewrite/` |
| Every number in the text | `numbers.py` (one entry per number, with its source) | all of the above |

## Use the benchmark

```python
from benchmark.score import load, run, matches
sets = load()                                   # the 204 accepted request sets
s = sets["06768b2b94"]                          # the film example of Figure 1
print(s["requests"]["open"], s["readings"])
matches(s, run(s, "SELECT ..."))                # -> ["A"], ["B"], ["A", "B"] or []
```

To score your own model, write one JSON line per answer and run `python benchmark/score.py answers.jsonl`.
[`benchmark/README.md`](benchmark/README.md) gives the format; `benchmark/examples/` has the four models' answers from the paper.

The two methods of Section 7 work with any model. `ask` takes a prompt and returns the reply text:

```python
from methods.disclose import disclose     # list the readings, answer each, show an alternative only if its result differs
from methods.clarify import edit          # clarify a request by adding one clause
```

## Rerun the experiments (optional, needs model access)

The saved runs in `out/` are the outputs of the commands below. A rerun calls the models again: Claude Haiku, Sonnet and Opus
through the `claude` CLI, and GPT-Sol and GPT-Luna through `codex exec`. Each run saves one file per answer and skips answers it
already has, so you can stop and restart it at any time.

| Experiment (paper section) | Command |
|---|---|
| Query generation and coverage (§2.2, §4.2) | `make full-data` (downloads the 155 source databases), then `python -m specbridge.comm.construct.coverage run` and `python -m specbridge.comm.construct.ablation run` |
| Mining choices from BIRD and Spider failures (§2.3) | `python -m specbridge.comm.diagnose.batches run <batch>` |
| Exact description vs natural request (§4.2) | `python -m specbridge.comm.construct.solver_eval <corpus> [--explicit]` |
| Writer swap (§4.2) | `python -m specbridge.comm.construct.writer_swap` |
| Request sets (§5) | `python -m specbridge.comm.transfer.evaluate out/transfer/all/render run <model>` and `python -m specbridge.comm.transfer.disclose out/transfer/all/render run` |
| AMBROSIA (§5, §7.2) | `sh reproduce/fetch_ambrosia.sh`, then `python -c "from specbridge.comm.transfer import ambrosia as A; A.decomp_run(A.MODELS); A.run_final()"` |
| Held-out BIRD and Spider (§6) | `python -m specbridge.comm.diagnose.compare run <dir> <model>` |
| BIRD scored with both readings (§6) | `python -m specbridge.comm.transfer.rescore run` |
| Disclosure methods (§7.2) | `REQMETHOD_OUT=out/reqmethod100 REQMETHOD_N=100 python -m specbridge.comm.transfer.reqmethod run` |
| Edit vs rewrite (§7.3) | `python -m specbridge.comm.transfer.rewrite run` |

Each module's docstring lists its other options. [`specbridge/docs/PIPELINE.md`](specbridge/docs/PIPELINE.md) explains how the
request sets are built.

## What is in this repository

```
benchmark/          the 307 request sets (204 accepted), their 12 databases, the scorer
library/            624 calculation choices mined from BIRD and Spider failures
methods/            the two methods of Section 7, standalone
human_supervision/  the author's reviews of the request sets and of the BIRD answers
out/                every saved model run and intermediate result
specbridge/         all code: query generation, mining, evaluation, figures
catalogues/         column meanings per database, used by query generation
spider_data/        Spider questions, schemas and databases used by the analysis
train_meta/         BIRD train questions and schemas
reproduce/          the check script, expected outputs, tests and download scripts
paper/              paper and supplement source
```

**Not included:** the AMBROSIA dataset, because its authors ask that it not be uploaded to GitHub. We include our aggregate
AMBROSIA results and a per-question score table, which rebuild Table 4 and Figures 9, 18 and 19.
`reproduce/fetch_ambrosia.sh` explains how to get the dataset from its authors.

## License

Code: MIT. Benchmark, library and saved runs: CC BY-SA 4.0, because they build on Spider and BIRD.
Details in [`DATA_LICENSE.md`](DATA_LICENSE.md).
