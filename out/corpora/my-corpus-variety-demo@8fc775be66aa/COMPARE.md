# my-corpus@c319e0daf960 vs my-corpus-variety-demo@8fc775be66aa

Same database (wta_1), same standard, same seed; only the configuration differs. Measured from the corpora's files.

| | my-corpus@c319e0daf960 | my-corpus-variety-demo@8fc775be66aa |
|---|---|---|
| delivered / requested | 200 / 200 | 200 / 200 |
| depth cells requested | A1 S2×29, A1 S3×29, A1 S4×29, A2 S2×28, A2 S3×28, A2 S4×57 | A1 S3×25, A1 S4×25, A1 S5×25, A1 S6×25, A2 S3×25, A2 S4×25, A2 S5×25, A2 S6×25 |
| depth cells delivered | A1 S2×29, A1 S3×29, A1 S4×29, A2 S2×28, A2 S3×28, A2 S4×57 | A1 S3×25, A1 S4×25, A1 S5×25, A1 S6×25, A2 S3×25, A2 S4×25, A2 S5×25, A2 S6×25 |
| tasks using aggregation | 200 (100%) | 200 (100%) |
| tasks using comparison with an average | 138 (69%) | 189 (94%) |
| tasks using shares | 0 (0%) | 24 (12%) |
| tasks using rankings | 4 (2%) | 4 (2%) |
| tasks using differences (between steps) | 0 (0%) | 0 (0%) |
| tasks using ratios (between steps) | 0 (0%) | 0 (0%) |
| construction shapes | 6 | 15 |
| largest shape | agg > baseline > agg (42%) | agg > baseline (21%) |
| tables read (tasks) | matches 200, players 63 | matches 166, players 67, rankings 34 |
| multi-table tasks | 63 (31%) | 67 (33%) |
| distinct computations / base quantities | 193 / 23 | 166 / 25 |
| runtime | 6853 s (34.3 s per task) | 588 s (2.9 s per task) |
| model calls | 952 (4.8 per task) | 508 (2.5 per task) |

Configurations: A `{"count": 200, "counts": {"wta_1": 200}, "databases": {"wta_1": 200}, "max_move": {"arith": 1, "steps": 1}, "seed": 2026, "standard": "benchmark", "target": {"cells": {"1,2": 1, "1,3": 1, "1,4": 1, "2,2": 1, "2,3": 1, "2,4": 2}}}`; B `{"count": 200, "counts": {"wta_1": 200}, "databases": {"wta_1": 200}, "seed": 2026, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}, "target": {"cells": {"1,3": 1, "1,4": 1, "1,5": 1, "1,6": 1, "2,3": 1, "2,4": 1, "2,5": 1, "2,6": 1}}, "ops": {"rank": 2, "share": 2}, "prefer": {"joins": 2}, "variety": "normal"}`.

The first corpus was built by the earlier builder (full packaging before review, oversampling at an assumed 50%); its runtime is not comparable with the second's as a measure of configuration.
