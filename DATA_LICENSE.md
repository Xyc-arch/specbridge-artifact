# Data licences

| What | Licence | Why |
|---|---|---|
| Code (`specbridge/`, `benchmark/*.py`, `methods/`, `reproduce/`, `tests/`) | MIT (`LICENSE`) | ours |
| Request-set benchmark (`benchmark/request_sets.jsonl`, `benchmark/databases/`) | CC BY-SA 4.0 | built on Spider and BIRD databases (CC BY-SA 4.0, share-alike) and LiveSQLBench databases (CC BY 4.0) |
| Decision library (`library/`) | CC BY-SA 4.0 | built from Spider and BIRD development questions and reference SQL |
| Saved model outputs and results (`out/`, `human_supervision/`) | CC BY-SA 4.0 | contain benchmark questions and databases above |
| Spider and BIRD files used by the analysis (`spider_data/`, `train_meta/`, `dev_unzipped/`) | CC BY-SA 4.0, unchanged | redistributed with attribution |
| DtP prompts (`methods/third_party/dtp_prompts.py`) | MIT (`methods/third_party/DTP_LICENSE`) | verbatim from github.com/saparina/disambiguate-then-parse, commit 39c92c0 |

## Not included, on purpose

- **AMBROSIA** (CC BY 4.0). Its authors ask that the dataset not be uploaded to GitHub or the Hugging Face Hub. The package ships only
  aggregate AMBROSIA results and `out/ambrosia/final/scores.jsonl` (per question: row index, arm, counts; no question, interpretation
  or SQL text). `scripts/fetch_ambrosia.sh` fetches the prompt and scorer from the authors and explains how to download the data.
- **LiveSQLBench reference SQL and test cases.** They are withheld by their authors to prevent leakage, and this work never used them.
- **The 155 source databases of the generator** (Spider, BIRD and LiveSQLBench databases, as snapshotted; 557 MB): a release asset of
  the artifact repository, fetched by `scripts/fetch_databases.sh` and checked against `scripts/source_databases.sha256`; same
  licences as their sources.
- **BIRD development databases** (`dev_unzipped/dev_20240627/dev_databases/`, CC BY-SA 4.0, 1.4 GB): too large for the repository;
  `scripts/fetch_bird.sh` downloads them from the BIRD authors and checks each file against `scripts/bird_dev.sha256`.
- **The defaults-note experiment** (`out/prior/`), which is not in the paper.

## Sources

- Spider: Yu et al., EMNLP 2018. https://yale-lily.github.io/spider (CC BY-SA 4.0)
- BIRD: Li et al., NeurIPS 2023. https://bird-bench.github.io (CC BY-SA 4.0)
- LiveSQLBench: BIRD team, 2025. https://huggingface.co/datasets/birdsql/livesqlbench-base-lite (CC BY 4.0)
- AMBROSIA: Saparina and Lapata, NeurIPS 2024. https://ambrosia-benchmark.github.io (CC BY 4.0)
- DtP: Saparina and Lapata, Findings of ACL 2025. https://github.com/saparina/disambiguate-then-parse (MIT)
