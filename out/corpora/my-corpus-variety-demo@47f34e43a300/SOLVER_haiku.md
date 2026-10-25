# Solver evaluation: `my-corpus-variety-demo@47f34e43a300`, solver haiku

The delivered corpus (196 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 108 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 196 | 179/196 (91%) | 196 | 190 |
| explicit instructions | 196 | 177/196 (90%) | 196 | 194 |

## Paired, same 196 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 170 | 7 |
| explicit wrong | 9 | 10 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 50 | 50/50 (100%) | 50/50 (100%) |
| S4 | 50 | 45/50 (90%) | 47/50 (94%) |
| S5 | 47 | 42/47 (89%) | 39/47 (83%) |
| S6 | 49 | 42/49 (86%) | 41/49 (84%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 100 | 92/100 (92%) | 87/100 (87%) |
| A2 | 96 | 87/96 (91%) | 90/96 (94%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 10/11 (91%) | 9/11 (82%) |
| agg > agg > baseline > agg | 8 | 6/8 (75%) | 5/8 (62%) |
| agg > agg > share | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline | 42 | 42/42 (100%) | 42/42 (100%) |
| agg > baseline > agg | 36 | 34/36 (94%) | 35/36 (97%) |
| agg > baseline > agg > agg | 2 | 2/2 (100%) | 1/2 (50%) |
| agg > baseline > agg > baseline | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline > baseline | 28 | 25/28 (89%) | 24/28 (86%) |
| agg > baseline > baseline > agg | 33 | 29/33 (88%) | 27/33 (82%) |
| agg > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > share | 6 | 6/6 (100%) | 6/6 (100%) |
| agg > share > agg | 1 | 0/1 (0%) | 1/1 (100%) |
| agg > share > agg > agg | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > agg > share | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 8 | 8/8 (100%) | 8/8 (100%) |
| agg > share > baseline > agg | 13 | 11/13 (85%) | 11/13 (85%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 167 | 154/167 (92%) | 153/167 (92%) |
| revised | 29 | 25/29 (86%) | 24/29 (83%) |

## Wrong answers to read (a random 6)

- **ffd7f9ee30** A2 S4 `agg > agg > baseline`
  - Join each match to the player whose player_id equals the match's winner_id (inner join; unmatched matches dropped; one row per match). Group by winner_id and the player's playing hand; for each group return winner_id, hand, the average winner age, and the average of (winner ranking points − loser ranking points) ÷ loser ranking points (missing values ignored; missing if none). Call this table S1. Group S1 by hand: return hand, the average of S1's average winner age, and the average of S1's average ranking-points ratio (missing ignored; missing if none). Call this S2. Let G be the average of S2's average winner age column over all S2 rows (missing ignored; missing if none). Pair each S2 row w
- **6eee64ddd2** A1 S6 `agg > share > baseline > agg`
  - For each winning player's identifier in matches, count the matches won; call this C. Let T be the sum of C over all players, and R = C ÷ T. Let AR be the average of R over all players. Pair each player with AR (inner join, rows without a match dropped). Compute, for each player, the value R − AR as the fourth column, and keep only players whose R is greater than AR. Over these kept players, show one summary row with three outputs: the total of C, the average of R, and the average of the fourth value (R − AR). Hmm: the third output averages the fourth column, R − AR.
- **b9c241ade0** A1 S6 `agg > baseline > baseline > agg`
  - Compute the following in steps. Step 1: From all tennis matches, inner-join each match to the player whose player identifier equals the match's winning player identifier (unmatched matches dropped; one row per match). Group by winning player identifier and playing hand (players.hand). Return (1) winning player identifier; (2) playing hand; (3) the average winner ranking points (missing ignored; missing if none). Step 2: From step 1 rows, group by column (2) and return (1) column (2); (2) the average of column (3) (missing ignored; missing if none). Step 3: Inner-join step 1 rows to step 2 rows where step 1 column (2) equals step 2 column (1) (compared as text, character by character; unmatch
- **add45b7fea** A2 S4 `agg > baseline > agg`
  - Step 1: join each match to the player whose player identifier equals the match's winning player's identifier (matches with no such player are dropped; one row per match). Group by winning player's identifier and playing hand, and return the winning player's identifier, the playing hand, and the average of (loser ranking points − winner ranking points) in the group (missing values ignored; missing if none). Step 2: over all step 1 rows as a single group, compute the average of step 1's third column (missing values ignored). Step 3: join step 1 rows to the step 2 row, only if step 2's value is not missing (inner join, one row per step 1 row). For each, return the winning player's identifier, t
- **dadb9a0c56** A1 S6 `agg > share > baseline > agg`
  - Step 1: from the tennis matches, group by loser country code and return the code and the number of matches. Step 2: over all step 1 rows as one group, return the sum of the match counts (missing ignored; missing if none). Step 3: inner join step 1 to step 2 (step 2's value must not be missing; one row per match, unmatched dropped); return the country code, the count, and (count ÷ total count). Step 4: over all step 3 rows as one group, return the average of step 3's ratio (missing ignored; missing if none). Step 5: inner join step 3 to step 4 (step 4's value must not be missing; one row per match, unmatched dropped); keep only rows where step 3's ratio is greater than step 4's average; retur
- **a022a78cb1** A2 S5 `agg > baseline > baseline`
  - Step 1: group matches by losing player's identifier; return the identifier and the average of (loser ranking points − winner ranking points) (missing values ignored; missing if none). Step 2: average step 1's second column over all rows (one group). Step 3: inner join step 1 rows to the step 2 row (only if step 2's value is not missing; one row per step 1 row), keeping only rows where step 1's second column is greater than step 2's value; return the identifier, the second column, and (second column − step 2's value). Step 4: average step 3's second column over all rows (one group). Final: inner join step 3 rows to the step 4 row (only if its value is not missing; one row per step 3 row), ret
