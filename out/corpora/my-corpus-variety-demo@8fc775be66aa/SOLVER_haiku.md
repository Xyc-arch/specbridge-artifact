# Solver evaluation: `my-corpus-variety-demo@8fc775be66aa`, solver haiku

The delivered corpus (187 tasks, each with its natural question). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 0 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 187 | 159/187 (85%) | 187 | 182 |

## By step depth

| step depth | tasks | natural |
|---|---|---|
| S3 | 50 | 48/50 (96%) |
| S4 | 49 | 40/49 (82%) |
| S5 | 44 | 38/44 (86%) |
| S6 | 44 | 33/44 (75%) |

## By arithmetic depth

| arithmetic depth | tasks | natural |
|---|---|---|
| A1 | 94 | 83/94 (88%) |
| A2 | 93 | 76/93 (82%) |

## By shape

| shape | tasks | natural |
|---|---|---|
| agg > agg > baseline | 13 | 8/13 (62%) |
| agg > agg > baseline > agg | 11 | 9/11 (82%) |
| agg > agg > baseline > baseline | 4 | 2/4 (50%) |
| agg > baseline | 42 | 40/42 (95%) |
| agg > baseline > agg | 35 | 31/35 (89%) |
| agg > baseline > agg > agg | 4 | 3/4 (75%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) |
| agg > baseline > baseline | 21 | 20/21 (95%) |
| agg > baseline > baseline > agg | 30 | 24/30 (80%) |
| agg > rank | 4 | 4/4 (100%) |
| agg > share | 4 | 4/4 (100%) |
| agg > share > agg | 1 | 1/1 (100%) |
| agg > share > baseline | 7 | 5/7 (71%) |
| agg > share > baseline > agg | 9 | 6/9 (67%) |
| agg > share > share | 1 | 1/1 (100%) |

## By writer status

| writer status | tasks | natural |
|---|---|---|
| passed | 129 | 120/129 (93%) |
| revised | 58 | 39/58 (67%) |

## Wrong answers to read (a random 6)

- **e566b11c72** A1 S6 `agg > share > baseline > agg`
  - Return one summary row with three values computed over the rows of step 5: the average of column (2) of step 5, the average of column (3) of step 5, and the average of column (4) of step 5, in that order.  Step 1: Group all tennis matches by losing player's identifier. Return (1) losing player's identifier; (2) the number of records in the group.  Step 2: From step 1 rows, form one group over all rows and return (1) the sum of column (2) of step 1 (missing ignored; missing if none).  Step 3: Inner-join step 1 rows with the step 2 rows whose column (1) is not missing (one combined record per pairing; unmatched step 1 rows are dropped). Return (1) column (1) of step 1; (2) column (2) of step 1
- **6580de1893** A2 S4 `agg > baseline > agg`
  - For each tournament level, compute the average of loser ranking points minus winner ranking points per match (missing values ignored; missing if none). Compute the overall average of those per-level averages (missing values ignored; missing if none). Pair each level row with that overall value only if it is not missing (inner join, one row per level). Keep only the levels whose average is greater than the overall average. For each kept level, compute its average minus the overall average. Return a single summary row with two outputs in this order: (1) the average, over only the kept levels, of the levels' averages, and (2) the average, over only the kept levels, of the differences from the o
- **2f2bdd36c4** A2 S4 `agg > baseline > agg`
  - Join each match to the player whose player identifier equals the match's winning player's identifier (inner join: matches with no matching player are dropped; one row per match). Group by the player's playing hand. For each hand, compute: (a) the average winner ranking points (missing values ignored; missing if none), and (b) the average, over the matches in the group, of the per-match value loser height minus winner height (missing values ignored, so a match with either height missing contributes nothing; missing if none). Call these the hand rows. Compute one overall value: the average of (b) across all hand rows (missing values ignored; missing if none). Pair each hand row with that overa
- **cebaf61275** A1 S5 `agg > agg > baseline > agg`
  - Over the rows of step 4 defined below, show one summary row with three outputs, in this order: (1) the average of column (2) of step 4; (2) the average of column (3) of step 4; (3) the average of column (4) of step 4. Missing values are ignored in each average, and an average is missing when there are none.  Step 1. Start from each tennis match. Join it to each player whose player identifier equals the match's winning player's identifier. This gives one combined record per match, and a match with no matching player is dropped. Group the kept records by winning player's identifier and playing hand, with one result row per group. Return (1) winning player's identifier; (2) playing hand; (3) th
- **5ced20d0a8** A2 S3 `agg > baseline`
  - For each winning player (winning player's identifier), compute the average winner age (ignoring missing values) and the average of loser ranking points divided by winner ranking points per match (ignoring missing values). Call that second average X. Also compute the overall average of X across all those players (ignoring missing values), and call it Y. Keep only players where Y is not missing, one row per player. Return the player's identifier, the average winner age, X, and X − Y. Sort by X − Y highest first, missing values last, and return only the first 10 rows.
- **2b8247c61d** A2 S4 `agg > baseline > agg`
  - For each losing player (loser Player ID), over that player's matches compute P = the average of maximum sets in match (missing values ignored; missing if none) and R = the average, taken per match, of loser ranking points ÷ winner ranking points (the division is done for each match first, then averaged; missing values ignored; missing if none). Let M be the average of R over all these per-player rows (missing values ignored; missing if none). Keep only players whose R is greater than M, pairing each player row only with the overall row when M is not missing (players with no pairing are dropped; one row per player). For each kept player compute D = R − M. Show one summary row over the kept pl
