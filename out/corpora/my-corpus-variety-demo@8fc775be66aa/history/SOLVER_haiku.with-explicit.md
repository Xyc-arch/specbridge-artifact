# Solver evaluation: `my-corpus-variety-demo@8fc775be66aa`, solver haiku

Same solver (batched agent, up to 6 rounds of exploration queries, then a final query), same grader (the task's own: tolerance, tie groups). Batches never hold both versions of a task. 0 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| explicit instructions | 200 | 149/200 (74%) | 200 | 189 |
| natural-precise questions | 187 | 159/187 (85%) | 187 | 182 |

## Paired, on the 187 tasks with both versions

| | natural right | natural wrong |
|---|---|---|
| explicit right | 121 | 21 |
| explicit wrong | 38 | 7 |

Explicit on the same 187 tasks: 142/187 (76%); natural: 159/187 (85%).
The 13 explicit-fallback tasks (no natural version): explicit 7/13 (54%).

## By step depth

| step depth | tasks | explicit | natural (where written) |
|---|---|---|---|
| S3 | 50 | 42/50 (84%) | 48/50 (96%) |
| S4 | 50 | 44/50 (88%) | 40/49 (82%) |
| S5 | 50 | 34/50 (68%) | 38/44 (86%) |
| S6 | 50 | 29/50 (58%) | 33/44 (75%) |

## By arithmetic depth

| arithmetic depth | tasks | explicit | natural (where written) |
|---|---|---|---|
| A1 | 100 | 75/100 (75%) | 83/94 (88%) |
| A2 | 100 | 74/100 (74%) | 76/93 (82%) |

## By shape

| shape | tasks | explicit | natural (where written) |
|---|---|---|---|
| agg > agg > baseline | 13 | 9/13 (69%) | 8/13 (62%) |
| agg > agg > baseline > agg | 11 | 10/11 (91%) | 9/11 (82%) |
| agg > agg > baseline > baseline | 4 | 1/4 (25%) | 2/4 (50%) |
| agg > baseline | 42 | 36/42 (86%) | 40/42 (95%) |
| agg > baseline > agg | 36 | 34/36 (94%) | 31/35 (89%) |
| agg > baseline > agg > agg | 4 | 4/4 (100%) | 3/4 (75%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 26 | 14/26 (54%) | 20/21 (95%) |
| agg > baseline > baseline > agg | 35 | 19/35 (54%) | 24/30 (80%) |
| agg > rank | 4 | 2/4 (50%) | 4/4 (100%) |
| agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > share > agg | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 7 | 5/7 (71%) | 5/7 (71%) |
| agg > share > baseline > agg | 10 | 8/10 (80%) | 6/9 (67%) |
| agg > share > share | 2 | 1/2 (50%) | 1/1 (100%) |

## By writer status

| writer status | tasks | explicit | natural (where written) |
|---|---|---|---|
| explicit fallback | 13 | 7/13 (54%) | 0/0 (0%) |
| passed | 129 | 103/129 (80%) | 120/129 (93%) |
| revised | 58 | 39/58 (67%) | 39/58 (67%) |

## Disagreements to read (explicit right, natural wrong; a random 6)

- **5ced20d0a8** A2 S3 `agg > baseline`
  - natural: For each winning player (winning player's identifier), compute the average winner age (ignoring missing values) and the average of loser ranking points divided by winner ranking points per match (ignoring missing values). Call that second average X. Also compute the overall average of X across all those players (ignoring missing values), and call it Y. Keep only players where Y is not missing, one row per player. Return the player's identifier, the average winner age, X, and X − Y. Sort by X − Y highest first, missing values last, and return only the first 10 rows.
- **00ad2e2f6c** A2 S5 `agg > baseline > baseline`
  - natural: For each loser playing hand, compute X = the average of winner ranking points ÷ loser ranking points (per match, missing values ignored; missing if none). Let Y be the average of X over all hands (missing values ignored; missing if none). Keep only hands whose X is greater than Y, pairing each hand only with the overall row when Y is not missing (hands with no pairing are dropped; one row per hand). For each kept hand compute Z = X − Y. Let W be the average of X over the kept hands (missing values ignored; missing if none). Return four columns: loser playing hand, X, Z, and X − W.
- **ff78ae7e78** A2 S5 `agg > agg > baseline > agg`
  - natural: Return one summary row with three outputs, computed over the rows of step 4 below: (1) the average of step 4's playing hand-level column 2 (the step-2 age-based average), (2) the average of step 4's column 3 (the step-2 ranking-points average), (3) the average of step 4's column 4 (the difference).  Step 1: Take each match and inner-join it to the players record whose player identifier equals the winning player's identifier (one row per match; matches with no player are dropped). Group by winning player's identifier and playing hand. For each group return (1) winning player's identifier; (2) playing hand; (3) the average of (loser age − winner age) ÷ winner age (missing ignored; missing if n
- **dbbe89e0c4** A1 S6 `agg > share > baseline > agg`
  - natural: Return one summary row with three values computed over the rows of step 5: the total of column (2) of step 5, the average of column (3) of step 5, and the average of column (4) of step 5, in that order.  Step 1: Group all tennis matches by tournament level. Return (1) tournament level; (2) the number of records in the group.  Step 2: From step 1 rows, form one group over all rows and return (1) the sum of column (2) of step 1 (missing ignored; missing if none).  Step 3: Inner-join step 1 rows with the step 2 rows whose column (1) is not missing (one combined record per pairing; unmatched step 1 rows are dropped). Return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B, where A i
- **c9a6394a59** A2 S4 `agg > baseline > agg`
  - natural: For each losing player's identifier, compute P, the average over their matches of the per-match difference (loser ranking points − winner ranking points), ignoring missing values (missing if none). Let G be the average of P over all losing players, ignoring missing values (missing if none). Keep only players whose P is greater than G, dropping players if G is missing (one row per player). For each kept player, compute P − G. Return a single summary row with two outputs in this order: (1) the average of P over the kept players only (not G); (2) the average of P − G over the kept players, ignoring missing values.
- **2b8247c61d** A2 S4 `agg > baseline > agg`
  - natural: For each losing player (loser Player ID), over that player's matches compute P = the average of maximum sets in match (missing values ignored; missing if none) and R = the average, taken per match, of loser ranking points ÷ winner ranking points (the division is done for each match first, then averaged; missing values ignored; missing if none). Let M be the average of R over all these per-player rows (missing values ignored; missing if none). Keep only players whose R is greater than M, pairing each player row only with the overall row when M is not missing (players with no pairing are dropped; one row per player). For each kept player compute D = R − M. Show one summary row over the kept pl
