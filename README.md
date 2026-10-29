# Text-to-SQL Models Make Choices Without Saying So

Code, data and saved model runs for our PVLDB paper (Experiment, Analysis & Benchmark track).

Paper: [`paper/tex/specbridge.pdf`](paper/tex/specbridge.pdf) · Supplement: [`paper/tex/supplement.pdf`](paper/tex/supplement.pdf)

A text-to-SQL answer can run, return a plausible number, and still compute something other than what the analyst meant. This
happens when a request leaves a calculation choice open (count rows or count entities?) and the model picks one interpretation without
saying so. We test this with *request sets*: three requests on the same data, one for each interpretation and one that leaves the choice
open, all scored by execution.

There are two ways to use this repository:

1. **Offline reproduction (the main path).** Rebuild every figure, table and number in the paper from our saved model runs.
   CPU only, no GPU, no model access, about 8 minutes.
2. **Rerun with models (optional).** Call the models again to regenerate the saved runs. This needs model access and is
   described at the end.

## Requirements

- macOS with Python 3.11, and about 3 GB of free disk space. Any recent Mac works; we used an Apple M2 Max laptop with
  Python 3.11.5.
- Internet access once, to download the BIRD dev databases (346 MB download, 1.4 GB unpacked).

The code also runs on Linux, but some numbers can differ slightly there, so use macOS to reproduce the paper exactly.

## Offline reproduction (CPU only, about 8 minutes)

```sh
git clone https://github.com/Xyc-arch/specbridge-artifact && cd specbridge-artifact
python3 -m venv .venv && source .venv/bin/activate     # Python 3.11
make setup     # install the Python packages
make all       # download BIRD dev, rebuild every figure and table, compare with the paper, run the tests
```

Every result is rebuilt from the saved model runs in `out/`; no model is called. If all is well, you will see these lines near the end:

```
ALL OUTPUTS REPRODUCED
numbers found: 454; in the ledger: 454 (...) ok 399, mismatch 0 (...)
204 sets, 408 reference queries checked, 0 failures
```

Everything your run produces is collected in `results/`:

```
results/
  figures/      every data figure, drawn from your run, named by its number (fig08_outcomes.pdf is Figure 8)
  figure_data/  the files the paper's printed figures read, written from your run
  tables/       Tables 1 and 5, and the numbers of Table 4
  data/         the numbers behind each figure and table (JSON)
  check.txt     the comparison with the paper
  numbers.txt   every number printed in the paper, recomputed from the data, with ok / MISMATCH
  tests.txt     the test results
```

`make all` runs four steps, which you can also run one at a time:

| Step | What it does |
|---|---|
| `make data` | downloads the BIRD dev databases and checks them against `reproduce/bird_dev.sha256` |
| `make reproduce` | rebuilds every figure and table from the saved runs |
| `make check` | compares the result with the paper: data, tables, the data of every printed figure, figure pixels, and every number in the text |
| `make test` | tests the scorer, the two methods and their prompts |

The paper prints its figures with pgfplots from `paper/tex/figures/src/` (`*.tex` and the CSV files in `data/`). `make reproduce`
writes those CSV files again from your run (`out/paper/figure_data/`) and `make check` compares them byte for byte with the
paper's. It also draws each data figure with matplotlib (`out/paper/figures_col/`) and compares the pixels with our drawings;
these match when the packages come from `make setup` (pip) and the Arial font is installed (conda's matplotlib draws text
slightly differently). Data, tables and numbers match on any system.
`make figures` builds the printed figures from your run's data (needs pdfLaTeX with pgfplots, and Ghostscript); `make paper`
builds the PDF.

## Where each result comes from

Scripts are in `specbridge/report/` unless a path is given. The numbers behind each figure are written to `out/paper/data/`. Each
printed figure is `paper/tex/figures/src/col_<name>.tex`; its CSV files come from `paper/tex/figures/src/export.py`, with the
same arithmetic as `figures_col.py`.

| Paper | Script | Saved runs |
|---|---|---|
| Fig. 1, 2, 3, 15 (diagrams) | `paper/tex/figures/src/diag_*.tex` | |
| Table 1 | `tables_tex.py` | properties of the cited benchmarks |
| Table 2 | written in the paper | `out/transfer/all/render/disclose/` |
| Table 3 (the data and where each is used) | written in the paper | |
| Fig. 4 | `figures_col.py` | `library/` |
| Fig. 5 | `figures_col.py` | `out/transfer/` |
| Fig. 6–9 | `figures_col.py`, `accepted.py` | `out/transfer/all/render/`, `out/ambrosia/` |
| Fig. 10 | `conventions.py` | `out/transfer/all/render/` |
| Fig. 11, 12 | `figures_col.py` | `out/confirmation/` |
| Fig. 13 | `figures_col.py` | `spider_data/`, `train_meta/` |
| Fig. 14 | `impact.py` | BIRD dev, `out/impact/` |
| Table 4, BIRD scored with both interpretations (§6.2) | `specbridge/comm/transfer/rescore.py` | `out/rescore/`, `human_supervision/bird-other-reading.csv` |
| Fig. 16 | `figures_col.py` | `out/ambrosia/final/`, `out/system/method.json` |
| Table 5 | `tables_tex.py`, `reproduce/ambrosia_tables.py` | `out/system/method.json`, `out/system/scores.jsonl`, `out/reqmethod100/` |
| Fig. 17 (edit vs rewrite) and BIRD clarification (§7.3) | `figures_col.py` | `out/rewrite/` |
| Human review and the result without it (§4.2) | `exhibit_data.py` (`review`) | `human_supervision/verdicts.json`, `out/transfer/all/render/` |
| Open requests rewritten by GPT-Sol (§4.2) | `specbridge/comm/transfer/writer_swap_open.py` | `out/writer_swap_open/` |
| Supplement Figures S2, S3, S4 (generator ablation; exact description vs natural request; coverage) | `figures_col.py` | `out/ablation/`, `out/coverage/`, `out/corpora/` |
| Supplement Figure S1 (data and experiments, with sample sizes) | `datamap_tex.py` | the files behind the paper's numbers |
| Supplement Tables S2, S6 and S7 (how widely each choice occurs, selected examples) | `catalogue_tex.py` | `library/`, `benchmark/`, `human_supervision/` |
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

The two phases of the method (Section 7) work with any model. `ask` takes a prompt and returns the reply text:

```python
from methods.disclose import disclose     # phase 1, decide-then-answer: list the interpretations, answer each, show those that differ
from methods.clarify import edit          # phase 2: carry the user's pick by adding one clause to the request
```

## Rerun with models (optional)

You do not need this to check the paper: the offline reproduction above already computes every number from our saved model
outputs, on CPU only. Rerun the models only if you want to regenerate those outputs or test another model.

The saved runs in `out/` are the outputs of the commands below. Each run saves one file per answer and skips answers it already
has, so you can stop and restart it at any time. Choose one way to call the models:

| Option | Setup |
|---|---|
| **CLIs** (what the paper used) | install and log in to [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`claude`) and [Codex](https://github.com/openai/codex) (`codex`) |
| **API keys** | `export SPECBRIDGE_BACKEND=api ANTHROPIC_API_KEY=... OPENAI_API_KEY=...` |
| **Another model** | `export SPECBRIDGE_BACKEND=api OPENAI_BASE_URL=<your server's URL>`, then give your model's name to the commands |

Model names: `haiku`, `sonnet`, `opus` (Claude Haiku 4.5, Sonnet 5.5, Opus 5.5), `gpt-6-sol`, `gpt-6-luna`. The CLIs add their
own system prompt, so answers through the API can differ slightly from the saved runs.

| Experiment (paper section) | Command |
|---|---|
| Query generation and coverage (§2.2, §4.2) | `make full-data` (downloads the 155 source databases), then `python -m specbridge.comm.construct.coverage run` and `python -m specbridge.comm.construct.ablation run` |
| Mining choices from BIRD and Spider failures (§2.3) | `python -m specbridge.comm.diagnose.batches run <batch>` |
| Exact description vs natural request (§4.2) | `python -m specbridge.comm.construct.solver_eval <corpus> [--explicit]` |
| Writer swap (§4.2) | `python -m specbridge.comm.construct.writer_swap` |
| Open requests rewritten by GPT-Sol (§4.2) | `python -m specbridge.comm.transfer.writer_swap_open` |
| Request sets (§5) | `python -m specbridge.comm.transfer.evaluate out/transfer/all/render run <model>` and `python -m specbridge.comm.transfer.disclose out/transfer/all/render run` |
| AMBROSIA (§5, §7.2) | `sh reproduce/fetch_ambrosia.sh`, then `python -c "from specbridge.comm.transfer import ambrosia as A; A.decomp_run(A.MODELS); A.run_final()"` |
| Held-out BIRD and Spider (§6) | `python -m specbridge.comm.diagnose.compare run <dir> <model>` |
| BIRD scored with both interpretations (§6) | `python -m specbridge.comm.transfer.rescore run` |
| Phase 1 and the baselines (§7.2) | `REQMETHOD_OUT=out/reqmethod100 REQMETHOD_N=100 python -m specbridge.comm.transfer.reqmethod run`, then `python -m specbridge.comm.transfer.system report_method`, `report_stream` and `report_budget` (these read the AMBROSIA runs, so fetch AMBROSIA and run it first). `REQMETHOD_N=100` draws 100 main sets and 30 filter sets; 111 of them are accepted and used. The two-turn test with clarifying question: `python -m specbridge.comm.transfer.system report_twoturn` |
| Phase 2: edit vs rewrite (§7.3) | `python -m specbridge.comm.transfer.rewrite run` |

Each module's docstring lists its other options. [`specbridge/docs/PIPELINE.md`](specbridge/docs/PIPELINE.md) explains how the
request sets are built.

## What is in this repository

```
benchmark/          the 307 request sets (204 accepted), their 12 databases, the scorer
library/            624 calculation choices mined from BIRD and Spider failures
methods/            the two phases of the method in Section 7, standalone
human_supervision/  the authors' reviews of the request sets and of the BIRD answers
out/                every saved model run and intermediate result (the out/**/*.md files are run logs written during the research, not paper text)
specbridge/         all code: query generation, mining, evaluation, figures
catalogues/         column meanings per database, used by query generation
spider_data/        Spider questions, schemas and databases used by the analysis
train_meta/         BIRD train questions and schemas
reproduce/          the check script, expected outputs, tests and download scripts
paper/              paper and supplement source
```

**Not included:** the AMBROSIA dataset, because its authors ask that it not be uploaded to GitHub. We include our aggregate
AMBROSIA results and a per-question score table, which rebuild Figures 7 and 16 and Table 5.
`reproduce/fetch_ambrosia.sh` explains how to get the dataset from its authors.

## License

Code: MIT. Benchmark, library and saved runs: CC BY-SA 4.0, because they build on Spider and BIRD.
Details in [`DATA_LICENSE.md`](DATA_LICENSE.md).
