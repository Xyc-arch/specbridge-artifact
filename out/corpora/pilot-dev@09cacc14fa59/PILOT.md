# Pilot, Stages 1-3, development databases (2026-10-02)

Request `out/corpora/request_pilot-dev-1.json`: wta_1, toxicology, news, 16 tasks each, A1-2 x S3-6. Grammar compose-v3.4.

## Construction (Stage 1)
- 48 of 48 delivered, 166 s, 58 model calls (semantic review, Opus and Sonnet). No shortfall. toxicology cannot build A2 at
  S3-S4; its tasks moved to 1,3 and 2,5.
- Built-for cell = measured cell: 48 of 48 (`depth_agrees`, recorded from this build on).
- Receipts: recomputed 0, trivial 0, constant row quantity 0 (one top-10 cut falls inside a tie group; graded by tie groups).
- Operations: baseline 43, share 22, **rank 0** although weighted 2 (earlier corpora: rank 2-4 of 200). The operation
  preference barely moves the delivered mix -- a Stage 2 control finding.

## Precise natural questions (Stage 3)
- 47 of 48 written: 37 passed review on round 1, 10 revised and accepted, 1 not rendered. 71 calls, 714k input tokens, 104 s.

## Solvers, one question per call (47 tasks)
| solver | explicit V | natural | explicit only | natural only |
|---|---|---|---|---|
| haiku | 45 | 43 | 3 | 1 |
| sonnet | 47 | 46 | 1 | 0 |
| gpt-6-sol | 47 | 45 | 2 | 0 |
| gpt-6-luna | 41 | 42 | 5 | 6 |

## Defect found by reading
Task `8ac7dd4f7e` (wta_1, A2 S6, writer status "revised"): the natural question's final output (1) is "step 5's column (1)
(player ID)"; the specification says column (2) (playing hand). All four solvers followed the question and were scored
wrong. The reviewer accepted the revised draft: model review missed a changed output requirement. The question is also a
near-restatement of the specification (deep tasks), which Table 2 must report. Added to the human sheet as item 41.

## Human sheet
https://claude.ai/artifact/CTzv3didKKjNV138Gj1YgA, collection `pilot_fidelity`: 41 tasks (40 stratified + the defect),
453 requirement marks, plus "exact computation?" and "meaningful analysis?". Gate: >= 90% exact; coherence sound.

## Status (appended 2026-10-02; results above unchanged)
Human validation PENDING. Correction of 8ac7dd4f7e and an Opus recheck of all 47 questions: `../pilot-dev@09cacc14fa59-corr1/CORRECTION.md`.
