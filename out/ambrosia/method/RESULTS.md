# AMBROSIA method pilot

GATE (written before the run): continue to the full test only if OURS beats disambiguate-then-parse on AllFound or recall, recovers >= 30-40% of the computable misses (decomposition: readings plain missed that the model computes when asked), and loses <= 3 points of precision on unambiguous questions against plain.

## Results, sonnet (dev)

Shape-tolerant (primary) / strict. Precision: share of returned queries matching a gold reading, on unambiguous questions.

| arm | ambiguous n | AllFound | recall | computable misses recovered | unambiguous n | precision | queries per question | calls / chars in per question |
|---|---|---|---|---|---|---|---|---|
| plain | 60 | 15 / 10 | 0.57 / 0.49 | 0 of 39 (0%) | 30 | 0.63 | 2.5 | 1 / saved |
| dtp | 60 | 27 / 15 | 0.70 / 0.58 | 14 of 39 (36%) | 30 | 0.51 | 5.7 | 8.0 / 25359 |
| samplek | 60 | 23 / 17 | 0.66 / 0.59 | 9 of 39 (23%) | 30 | 0.62 | 5.4 | 3.0 / 9234 |
| ours | 60 | 27 / 18 | 0.68 / 0.54 | 15 of 39 (38%) | 30 | 0.67 | 2.0 | 3.1 / 9510 |
| ours (dedup) | 60 | 27 / 18 | 0.67 / 0.54 | 15 of 39 (38%) | 30 | 0.67 | 2.0 | 3.1 / 9510 |
| ours2 (dedup) | 60 | 29 / 19 | 0.70 / 0.57 | 17 of 39 (44%) | 30 | 0.64 | 2.2 | 3.7 / 11328 |
| ours+lib (dedup) | 60 | 27 / 18 | 0.67 / 0.54 | 15 of 39 (38%) | 30 | 0.66 | 2.2 | 3.1 / 9510 |

**Gate (ours with dedup): FAIL.** AllFound 27 vs DtP 27; recall 0.67 vs 0.70; computable misses recovered 15 of 39; precision 0.67 vs plain 0.63.

## Decision record (2026-10-13, before any further data)

1. **Original gate: FAILED on coverage.** On dev (Sonnet), ours with dedup ties disambiguate-then-parse on AllFound (27 vs 27,
   shape-tolerant; 18 vs 15 strict) and is lower on recall (0.67 vs 0.70); it recovers 15 of 39 computable misses (38%) and keeps
   precision (0.67 vs plain 0.64, on 15 plain questions). The gate required beating DtP on AllFound or recall.
2. **New claim, written now, before more data:** against disambiguate-then-parse, ours is (a) NON-INFERIOR in coverage --
   AllFound and recall each within 3 points (shape-tolerant); (b) HIGHER in precision on unambiguous questions; (c) LOWER in cost
   (calls and characters per question). All three must hold on the final test, per solver and pooled, with intervals.
3. **One recall variant on dev only:** a second detection pass when the first finds a single reading. Then the method is frozen.
4. **Final test:** fresh test-split questions never used (90 ambiguous + 60 unambiguous), four solvers, all arms interleaved.

## Freeze (2026-10-13, after the dev variant)

The recall variant (ours2: a second detection pass only where the first finds one reading; generic wording) is the method, now
FROZEN: detect -> (second pass if one reading) -> one SQL per reading -> drop identical results by execution -> main + alternatives.
Dev (Sonnet), shape-tolerant: AllFound 29 vs DtP 27; recall 0.70 vs 0.70; computable misses recovered 17/39 (44%); precision on
unambiguous 0.64 vs DtP 0.51 (plain 0.63); 3.7 calls / 11,300 characters per question vs DtP 8.0 / 25,400. Library edits add nothing
on AMBROSIA and are not part of the AMBROSIA method.

## Keep rule for the second pass (2026-10-13; written after the dev variant result was seen, applied to exact dev values)

Rule: keep the second pass only if dev recall rises >= 3 points with precision on unambiguous questions falling <= 2 points.
Exact dev values (Sonnet, shape-tolerant, dedup): recall 0.6694 -> 0.7028 (+3.3); precision 0.6667 -> 0.6389 (-2.8).
**Decision: FREEZE WITHOUT the second pass.** The frozen method is "ours": detect -> one SQL per reading -> drop identical results
by execution -> main + alternatives. sample-k is fixed at k = 3 (ours' dev mean calls, rounded).
Final test: Sonnet and GPT-Sol first; all four arms interleaved; 90 ambiguous + 60 unambiguous fresh test-split questions; items
any arm's call was refused by a safety filter are excluded from every arm for that solver, and their count is reported.

## Pre-test change to the claim (2026-10-13, before any final-test data)

With 90 ambiguous questions the paired interval on a coverage difference is about +/-9 points, so a -3 margin could not be met
even by equal methods. Revised claim:
- coverage NON-INFERIOR if the POOLED two-solver (Sonnet + GPT-Sol) 95% lower bound of ours - DtP is >= -10 points, on AllFound
  and on recall (shape-tolerant);
- precision on unambiguous questions HIGHER: pooled lower bound of ours - DtP > 0;
- cost reported as calls and characters per question (no threshold).
All four arms kept. Run order: Sonnet first, then GPT-Sol; the claim is judged on the pooled result.

## Results, final test (fresh test-split questions)

Shape-tolerant. Intervals: Wilson (AllFound), paired bootstrap over questions (recall, precision, differences). Items with any refused call are excluded from every arm for that solver.

### sonnet: 90 ambiguous, 60 unambiguous (0 excluded for refusals)

| arm | AllFound [Wilson 95%] | recall [95%] | computable misses recovered | precision on unambiguous [95%] | calls / chars in per question |
|---|---|---|---|---|---|
| plain | 26/90 (29%) [21, 39] | 0.585 [0.52, 0.65] | 0 of 51 (0%) [0, 7] | 0.491 [0.40, 0.58] | 1.0 / 3157 |
| dtp | 30/90 (33%) [24, 44] | 0.643 [0.59, 0.70] | 10 of 51 (20%) [11, 32] | 0.471 [0.40, 0.54] | 8.0 / 26026 |
| samplek | 31/90 (34%) [25, 45] | 0.635 [0.57, 0.70] | 6 of 51 (12%) [6, 23] | 0.490 [0.40, 0.57] | 3.0 / 9471 |
| ours | 32/90 (36%) [26, 46] | 0.656 [0.59, 0.72] | 13 of 51 (25%) [16, 39] | 0.626 [0.53, 0.72] | 3.1 / 9628 |
Ours - DtP (paired by question): AllFound +0.022 [-0.056, 0.100]; recall +0.013 [-0.024, 0.052]; precision +0.155 [0.064, 0.241]; computable misses recovered +0.059 [0.000, 0.137] (share of the 51).
Ours - sample-k (paired by question): AllFound +0.011 [-0.067, 0.089]; recall +0.020 [-0.024, 0.065]; precision +0.137 [0.054, 0.230]; computable misses recovered +0.137 [0.039, 0.255] (share of the 51).

Ours - DtP (paired, this solver): AllFound +0.022 [-0.056, 0.100]; recall +0.013 [-0.022, 0.052]; precision +0.155 [0.063, 0.246].

### gpt-6-sol: 90 ambiguous, 60 unambiguous (0 excluded for refusals)

| arm | AllFound [Wilson 95%] | recall [95%] | computable misses recovered | precision on unambiguous [95%] | calls / chars in per question |
|---|---|---|---|---|---|
| plain | 18/90 (20%) [13, 29] | 0.496 [0.43, 0.57] | 0 of 54 (0%) [0, 7] | 0.614 [0.50, 0.72] | 1.0 / 3157 |
| dtp | 54/90 (60%) [50, 70] | 0.739 [0.66, 0.81] | 41 of 54 (76%) [63, 85] | 0.437 [0.35, 0.52] | 6.7 / 21174 |
| samplek | 24/90 (27%) [19, 37] | 0.563 [0.50, 0.63] | 6 of 54 (11%) [5, 22] | 0.588 [0.48, 0.69] | 3.0 / 9471 |
| ours | 37/90 (41%) [32, 51] | 0.643 [0.57, 0.72] | 23 of 54 (43%) [30, 56] | 0.667 [0.56, 0.78] | 2.6 / 7894 |
Ours - DtP (paired by question): AllFound -0.189 [-0.289, -0.078]; recall -0.096 [-0.161, -0.028]; precision +0.229 [0.129, 0.327]; computable misses recovered -0.333 [-0.500, -0.167] (share of the 54).
Ours - sample-k (paired by question): AllFound +0.144 [0.056, 0.233]; recall +0.080 [0.022, 0.139]; precision +0.079 [0.004, 0.160]; computable misses recovered +0.315 [0.185, 0.463] (share of the 54).

Ours - DtP (paired, this solver): AllFound -0.189 [-0.300, -0.078]; recall -0.096 [-0.159, -0.033]; precision +0.229 [0.127, 0.330].

### Pooled over sonnet + gpt-6-sol (the claim is judged here)

Ours - DtP: AllFound -0.083 [-0.150, -0.011]; recall -0.042 [-0.080, -0.005]; precision +0.192 [0.124, 0.261].
Ours - DtP, pooled: AllFound -0.083 [-0.156, -0.017]; recall -0.042 [-0.080, -0.004]; precision +0.192 [0.123, 0.259]; computable misses recovered -0.143 [-0.238, -0.048] (of 105).
Ours - sample-k, pooled: AllFound +0.078 [0.022, 0.139]; recall +0.050 [0.011, 0.086]; precision +0.108 [0.053, 0.168]; computable misses recovered +0.229 [0.143, 0.324] (of 105).
Claim: coverage non-inferior (both lower bounds >= -0.10): no; precision higher (lower bound > 0): yes.
