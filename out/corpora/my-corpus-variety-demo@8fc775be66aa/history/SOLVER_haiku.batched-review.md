# Solver evaluation: `my-corpus-variety-demo@8fc775be66aa`, solver haiku

Same solver (batched agent, up to 6 rounds of exploration queries, then a final query), same grader (the task's own: tolerance, tie groups). Batches never hold both versions of a task. 845 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| explicit instructions | 200 | 149/200 (74%) | 200 | 189 |
| natural-precise questions | 193 | 170/193 (88%) | 193 | 191 |

## Paired, on the 193 tasks with both versions

| | natural right | natural wrong |
|---|---|---|
| explicit right | 130 | 17 |
| explicit wrong | 40 | 6 |

Explicit on the same 193 tasks: 147/193 (76%); natural: 170/193 (88%).
The 7 explicit-fallback tasks (no natural version): explicit 2/7 (29%).

## By step depth

| step depth | tasks | explicit | natural (where written) |
|---|---|---|---|
| S3 | 50 | 42/50 (84%) | 48/50 (96%) |
| S4 | 50 | 44/50 (88%) | 43/50 (86%) |
| S5 | 50 | 34/50 (68%) | 42/49 (86%) |
| S6 | 50 | 29/50 (58%) | 37/44 (84%) |

## By arithmetic depth

| arithmetic depth | tasks | explicit | natural (where written) |
|---|---|---|---|
| A1 | 100 | 75/100 (75%) | 86/99 (87%) |
| A2 | 100 | 74/100 (74%) | 84/94 (89%) |

## By shape

| shape | tasks | explicit | natural (where written) |
|---|---|---|---|
| agg > agg > baseline | 13 | 9/13 (69%) | 7/13 (54%) |
| agg > agg > baseline > agg | 11 | 10/11 (91%) | 8/11 (73%) |
| agg > agg > baseline > baseline | 4 | 1/4 (25%) | 2/4 (50%) |
| agg > baseline | 42 | 36/42 (86%) | 41/42 (98%) |
| agg > baseline > agg | 36 | 34/36 (94%) | 35/36 (97%) |
| agg > baseline > agg > agg | 4 | 4/4 (100%) | 3/4 (75%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 26 | 14/26 (54%) | 24/25 (96%) |
| agg > baseline > baseline > agg | 35 | 19/35 (54%) | 27/30 (90%) |
| agg > rank | 4 | 2/4 (50%) | 3/4 (75%) |
| agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > share > agg | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 7 | 5/7 (71%) | 5/7 (71%) |
| agg > share > baseline > agg | 10 | 8/10 (80%) | 7/9 (78%) |
| agg > share > share | 2 | 1/2 (50%) | 2/2 (100%) |

## By writer status

| writer status | tasks | explicit | natural (where written) |
|---|---|---|---|
| explicit fallback | 7 | 2/7 (29%) | 0/0 (0%) |
| passed | 158 | 126/158 (80%) | 143/158 (91%) |
| revised | 35 | 21/35 (60%) | 27/35 (77%) |

## Disagreements to read (explicit right, natural wrong; a random 6)

- **e566b11c72** A1 S6 `agg > share > baseline > agg`
  - natural: Return one summary row with three values computed over the rows of step 5: the average of column (2) of step 5, the average of column (3) of step 5, and the average of column (4) of step 5, in that order.  Step 1: Group all tennis matches by losing player's identifier. Return (1) losing player's identifier; (2) the number of records in the group.  Step 2: From step 1 rows, form one group over all rows and return (1) the sum of column (2) of step 1 (missing ignored; missing if none).  Step 3: Inner-join step 1 rows with the step 2 rows whose column (1) is not missing (one combined record per pairing; unmatched step 1 rows are dropped). Return (1) column (1) of step 1; (2) column (2) of step 1
- **7c18795a4c** A1 S5 `agg > share > baseline`
  - natural: For each ranked player (grouped by ranked player's identifier in rankings), count that player's ranking records; call that count C. Let T be the sum of C over all players. For each player compute R = C ÷ T. Let M be the average of R over all players. Keep players whose C is greater than M. Pair each with the single average value M (inner join; one row per match). Return the player identifier, C, R, and C − M, where C is the player's record count and M is the average of R. Sort by C − M highest first, missing values last, and return the first 10 rows.
- **cebaf61275** A1 S5 `agg > agg > baseline > agg`
  - natural: Over the rows of step 4 defined below, show one summary row with three outputs, in this order: (1) the average of column (2) of step 4; (2) the average of column (3) of step 4; (3) the average of column (4) of step 4. Missing values are ignored in each average, and an average is missing when there are none.  Step 1. Start from each tennis match. Join it to each player whose player identifier equals the match's winning player's identifier. This gives one combined record per match, and a match with no matching player is dropped. Group the kept records by winning player's identifier and playing hand, with one result row per group. Return (1) winning player's identifier; (2) playing hand; (3) th
- **5ced20d0a8** A2 S3 `agg > baseline`
  - natural: For each winning player (winning player's identifier), compute the average winner age (ignoring missing values) and the average of loser ranking points divided by winner ranking points per match (ignoring missing values). Call that second average X. Also compute the overall average of X across all those players (ignoring missing values), and call it Y. Keep only players where Y is not missing, one row per player. Return the player's identifier, the average winner age, X, and X − Y. Sort by X − Y highest first, missing values last, and return only the first 10 rows.
- **ff78ae7e78** A2 S5 `agg > agg > baseline > agg`
  - natural: Return one summary row with three outputs, computed over the rows of step 4 below: (1) the average of step 4's playing hand-level column 2 (the step-2 age-based average), (2) the average of step 4's column 3 (the step-2 ranking-points average), (3) the average of step 4's column 4 (the difference).  Step 1: Take each match and inner-join it to the players record whose player identifier equals the winning player's identifier (one row per match; matches with no player are dropped). Group by winning player's identifier and playing hand. For each group return (1) winning player's identifier; (2) playing hand; (3) the average of (loser age − winner age) ÷ winner age (missing ignored; missing if n
- **68ec5734b8** A2 S4 `agg > agg > baseline`
  - natural: Join each match to the player whose player identifier equals the match's winning player's identifier (matches with no such player are dropped; one row per match). Group by winning player's identifier and the player's playing hand. For each group compute the average of (loser age − winner age) and the average of (loser height − winner height), ignoring missing values (missing if none). Then group those rows by playing hand and compute, per hand, the average of the age-difference averages and the average of the height-difference averages, ignoring missing values (missing if none). Let G be the average, across all those per-hand rows, of the per-hand average height difference (ignoring missing 
