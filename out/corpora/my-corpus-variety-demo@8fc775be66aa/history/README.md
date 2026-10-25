# Superseded versions (historical, not active)

The active corpus is `../corpus.jsonl`: 187 tasks, natural question only (single-task review; explicit V not delivered; manifest `../FROZEN.json`).

| file | what it was |
|---|---|
| tasks_paired.batched-review.jsonl | paired corpus with the batched review: 193 natural, 7 explicit fallbacks (tag corpus-my-corpus-variety-demo-frozen-2026-10-01) |
| FROZEN.batched-review.json | its manifest |
| NATURAL.batched-review.md | its natural-question report |
| SOLVER_haiku.batched-review.md, solver_haiku.batched-review.json | haiku on it: explicit 149/200, natural 170/193 |
| RECHECK_natural.json | single-task recheck of 47 of its questions (6 unfaithful) |
| tasks_paired_sample.pilot.jsonl, NATURAL_SAMPLE.pilot.md | the writer's 20-task pilot before the full run |
| tasks_paired.with-explicit-fallback.jsonl | 200 tasks, 13 carrying the explicit instructions as fallback (before explicit V was dropped as a rendering, 2026-10-01) |
| SOLVER_haiku.with-explicit.md, solver_haiku.with-explicit.json | haiku on both arms: explicit 149/200, natural 159/187 |
| ERRORS_*_haiku* | error attribution by code for both arms (explicit: 28 of 51 wrong answers on tasks that re-average an already averaged column) |
