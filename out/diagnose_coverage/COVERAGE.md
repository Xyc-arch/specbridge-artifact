# Stage 4 prerequisite: can explicit V render the benchmarks' gold SQL? (2026-10-03, no model calls)

| benchmark | questions | gold runs on our SQLite | explicit V renders | both (usable) |
|---|---|---|---|---|
| Spider dev (20 databases) | 1,034 | 1,032 | 837 | **835 (81%)** |
| LiveSQLBench (18 databases), all | 270 | -- | -- | -- |
| ... "Query" category (90 are "Management", DML) | 180 | 64 | 84 | **56 (31%)** |
| ... after sqlglot postgres -> sqlite translation of the gold | 180 | 129 | -- | **82 (46%)** |

LiveSQLBench's gold is PostgreSQL (`livesql_dbs/livesqlbench_gt_kg_testcases_0528.jsonl`); our databases are SQLite
copies. Failures on SQLite: `::` casts 83, syntax 20+, ARRAY_AGG / STDDEV / JSON_BUILD_OBJECT / LEAST. The translated
gold has NOT been checked against PostgreSQL answers (no PostgreSQL here); using it changes the reference.
BIRD dev, diagnosis batches (corrected 2026-10-03; "594/604" earlier was solver RUNS, not questions):

| BIRD source | unique questions attempted | reference does not run | explicit V refuses | usable |
|---|---|---|---|---|
| seed (bird_pairs) | 44 | 0 | 3 | 41 |
| batches 1-2 | 120 | 0 | 2 | 118 |
| batches 3-8 | 317 | 0 | 15 | 302 |
| **total** (5 databases: california_schools, financial, superhero, thrombosis_prediction, toxicology) | **481** | **0** | **20** | **461** |

The 98% vs 54% result is over runs: batches 3-8, 302 usable questions x 2 repeats = 604 runs per wording. No question
appears in two batches, and none is in the held-out 100 (seed ids recovered by matching the reference SQL to dev.json).
Renderer refusals in the seed and batches 1-2 were not logged in refused.json; they are counted here as tasks without an
explicit version. Findings apply to the executable, V-renderable subset only.
Script: `render_coverage.py`; per question: `coverage.json`.
