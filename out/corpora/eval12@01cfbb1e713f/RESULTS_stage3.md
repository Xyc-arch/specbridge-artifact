# Stage 2B/3 results on the frozen eval12 sample (2026-10-02)

382 of the 384 frozen tasks have a precise natural question (Sonnet writes, Opus reviews one task per call: 273 passed
round 1, 109 revised, 2 not rendered). Four solvers, one question per call, same harness for both wordings. Human
validation: PENDING.

| solver | explicit V | natural | both | explicit only | natural only | neither |
|---|---|---|---|---|---|---|
| haiku | 343 (89.8%) | 349 (91.4%) | 313 | 30 | 36 | 3 |
| sonnet | 380 (99.5%) | 363 (95.0%) | 362 | 18 | 1 | 1 |
| gpt-6-sol | 378 (99.0%) | 364 (95.3%) | 360 | 18 | 4 | 0 |
| gpt-6-luna | 307 (80.4%) | 333 (87.2%) | 274 | 33 | 59 | 16 |

By step depth (explicit / natural), n = 100 / 86 / 100 / 96:
- haiku S3 93/94, S4 81/79, S5 86/85, S6 83/91
- sonnet S3 100/96, S4 85/76, S5 100/98, S6 95/93
- gpt-6-sol S3 100/96, S4 86/82, S5 96/98, S6 96/88
- gpt-6-luna S3 99/91, S4 73/73, S5 71/89, S6 64/80

## Fidelity is not established by the model review
Tasks both strong solvers (sonnet, gpt-6-sol) get right on explicit V and wrong on the natural question: 6 (all
"passed" review); either strong solver: 30 (`fidelity_suspects.json`). The 3 tasks missed by 3+ solvers were read: all 3
are wording defects that the Opus reviewer accepted --
- 6ec8137fd3 (customers_and_invoices A2 S4): the question compares the average PRICE; V compares the average cost RATIO.
- 227771660b (thrombosis A2 S5): the question compares the "(3)" measure of step 1; V compares column (3) of step 2,
  which is step 1's column (4). Same mechanism as 6ec8137fd3 and as pilot 8ac7dd4f7e: a measure changes column
  number between steps and the question names the wrong one.
- 568a31721e (thrombosis A2 S4): the question says "hematocrit FRACTION"; solvers divide HCT by 100; V uses the stored value.
So the strong solvers' 4-5 point natural-vs-explicit gap contains real wording defects; the size of that share is for
the human audit to measure (suspects + a stratified sample).

## Weaker solvers do better on the natural question
gpt-6-luna 333 vs 307 (59 natural-only vs 33 explicit-only); haiku 349 vs 343. Luna's explicit accuracy falls with
depth (S3 99% -> S6 67%) while its natural accuracy stays >= 80%. The explicit V's length does not explain it (median
V length 3,133 characters on Luna's natural-only tasks vs 2,966 overall). Not yet explained.

## First structural result: step depth and errors on the explicit V (kept, 2026-10-02)
Error rate (explicit V, one run per solver, 382 tasks):

| solver | S3 | S4 | S5 | S6 |
|---|---|---|---|---|
| sonnet | 0/100 | 1/86 | 0/100 | 1/96 |
| gpt-6-sol | 0/100 | 0/86 | 4/100 | 0/96 |
| haiku | 7/100 (7%) | 5/86 (6%) | 14/100 (14%) | 13/96 (14%) |
| gpt-6-luna | 1/100 (1%) | 13/86 (15%) | 29/100 (29%) | 32/96 (33%) |
| all four | 2.0% [1.0, 3.9] | 5.5% [3.6, 8.5] | 11.8% [9.0, 15.3] | 12.0% [9.1, 15.6] |

(Pooled Wilson intervals treat the four solvers' answers as independent; they are not -- indicative only.)
Arithmetic depth does not show it: A1 10.2% vs A2 5.0% (all four). The natural question shows no clean trend
(5.8 / 9.9 / 7.5 / 8.3%); its errors include known wording defects. Not yet done: a database-controlled test
(stratified permutation or regression; statsmodels is broken in this environment).

## Regrading after the serial re-run (2026-10-03) and with the corrected questions (corpus.v2)
Final queries that did not execute were re-run alone under the same 60 s limit (now part of `solver_eval`): 10 had timed
out under parallel load and were right when run alone (gpt-6-luna natural 9, gpt-6-sol natural 1). Original grading kept
as `solver_<m>.grading-v1.json`.

| solver | explicit V | natural v2 | S3 | S4 | S5 | S6 (explicit / natural, % right) |
|---|---|---|---|---|---|---|
| sonnet | 380 (99.5%) | 371 (97.1%) | 100 / 98 | 99 / 92 | 100 / 99 | 99 / 99 |
| gpt-6-sol | 378 (99.0%) | 370 (96.9%) | 100 / 98 | 100 / 98 | 96 / 99 | 100 / 93 |
| haiku | 343 (89.8%) | 353 (92.4%) | 93 / 95 | 94 / 94 | 86 / 85 | 86 / 96 |
| gpt-6-luna | 307 (80.4%) | 345 (90.3%) | 99 / 94 | 85 / 87 | 71 / 92 | 67 / 88 |
| error, all four | | | 2.0% / 3.8% | 5.5% / 7.3% | 11.8% / 6.2% | 12.0% / 6.2% |

## Error patterns (code attribution, `ERRORS_<arm>_<model>.json`)
- Cheaper models on explicit V fail on STACKED comparisons: gpt-6-luna wrong on 2% of single-comparison tasks
  (agg > baseline) and 0% of agg > share, but 25-45% of tasks with a second comparison on the first (share > baseline,
  baseline > baseline). Step depth grows with that stacking. Differing output: usually the final derived quantity
  (output 4) or all outputs (an earlier step went wrong). 59 of its 75 explicit errors are right on the natural question.
- Strong models' remaining natural errors are mostly arithmetic depth 2 (sonnet 10 of 11, gpt-6-sol 10 of 13; A2 is 45%
  of tasks), all right on explicit V: wording around which derived quantity is meant; on the human audit sheet.
- Real non-executing SQL: invalid window functions (gpt-6-luna), a CTE name repeated in another case (sonnet), prose
  instead of SQL in FINAL (haiku).
