# Solver evaluation: `my-corpus-variety-demo@b223964d8a45`, solver haiku

The delivered corpus (195 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 0 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 195 | 176/195 (90%) | 195 | 187 |
| explicit instructions | 195 | 171/195 (88%) | 195 | 193 |

## Paired, same 195 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 164 | 7 |
| explicit wrong | 12 | 12 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 49 | 49/49 (100%) | 49/49 (100%) |
| S4 | 50 | 45/50 (90%) | 47/50 (94%) |
| S5 | 47 | 42/47 (89%) | 39/47 (83%) |
| S6 | 49 | 40/49 (82%) | 36/49 (73%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 99 | 89/99 (90%) | 82/99 (83%) |
| A2 | 96 | 87/96 (91%) | 89/96 (93%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 10/11 (91%) | 9/11 (82%) |
| agg > agg > baseline > agg | 8 | 6/8 (75%) | 5/8 (62%) |
| agg > agg > baseline > baseline | 6 | 3/6 (50%) | 1/6 (17%) |
| agg > agg > share | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline | 41 | 41/41 (100%) | 41/41 (100%) |
| agg > baseline > agg | 36 | 34/36 (94%) | 35/36 (97%) |
| agg > baseline > agg > agg | 2 | 2/2 (100%) | 1/2 (50%) |
| agg > baseline > agg > baseline | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline > baseline | 29 | 26/29 (90%) | 25/29 (86%) |
| agg > baseline > baseline > agg | 30 | 26/30 (87%) | 24/30 (80%) |
| agg > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > share | 6 | 6/6 (100%) | 6/6 (100%) |
| agg > share > agg | 1 | 0/1 (0%) | 1/1 (100%) |
| agg > share > agg > agg | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > agg > share | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 7 | 7/7 (100%) | 7/7 (100%) |
| agg > share > baseline > agg | 10 | 9/10 (90%) | 8/10 (80%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 163 | 150/163 (92%) | 146/163 (90%) |
| revised | 32 | 26/32 (81%) | 25/32 (78%) |

## Wrong answers to read (a random 6)

- **b9c241ade0** A1 S6 `agg > baseline > baseline > agg`
  - Compute the following in steps. Step 1: From all tennis matches, inner-join each match to the player whose player identifier equals the match's winning player identifier (unmatched matches dropped; one row per match). Group by winning player identifier and playing hand (players.hand). Return (1) winning player identifier; (2) playing hand; (3) the average winner ranking points (missing ignored; missing if none). Step 2: From step 1 rows, group by column (2) and return (1) column (2); (2) the average of column (3) (missing ignored; missing if none). Step 3: Inner-join step 1 rows to step 2 rows where step 1 column (2) equals step 2 column (1) (compared as text, character by character; unmatch
- **e24b1d1c17** A2 S5 `agg > baseline > baseline`
  - Build four stages of results.  Stage 1: Take each match and group by winning player's identifier. For each group, return (1) the winning player's identifier and (2) the average of (loser ranking points − winner ranking points). Missing values are ignored, and the average is missing if there are none.  Stage 2: Over all stage 1 rows as a single group, return (1) the average of stage 1 column 2, ignoring missing values. It is missing if there are none.  Stage 3: Inner-join the stage 1 rows to the stage 2 rows, excluding any stage 2 row whose column 1 is missing. Matches with no partner are dropped. Keep only rows where stage 1 column 2 is greater than stage 2 column 1. Return (1) stage 1 colum
- **9ebf452be6** A1 S6 `agg > baseline > baseline > agg`
  - For each loser country code, compute the average winner height (missing ignored). Let G be the average of these per-country averages (countries with a missing average ignored; those rows dropped by the join). Keep countries whose average is greater than G, with D1 = country average − G. Let B be the average of the kept countries' averages (not of D1). Keep only the kept countries whose country average is greater than B, with D2 = country average − B. Over these final rows, show one summary row with three outputs: the average of the country averages, the average of D1, and the average of D2.
- **712f74ccc0** A2 S4 `agg > baseline > agg`
  - Join each match to the player whose player_id equals the match's winner_id (inner join; unmatched matches dropped; one row per match). Group by player's playing hand; for each hand return hand, the average winner age, and the average of (winner ranking points − loser ranking points) ÷ loser ranking points (missing values ignored; missing if none). Call this table H. Let G be the average of H's per-hand average winner age (missing ignored; missing if none). Combine H with G only if G is not missing (every H row pairs with the single G row), and keep only H rows whose average winner age is greater than G. For each kept row, return hand, average winner age, average ratio, and (average winner ag
- **976fc78103** A2 S5 `agg > baseline > baseline`
  - For each losing player ID in matches, compute the average of (loser age − winner age) over that player's matches, ignoring missing values. Call this the player average. Compute the overall average of the player averages, ignoring missing values. Keep only players whose player average is greater than the overall average. For each kept player, compute D = player average − overall average. Compute M, the average of D across the kept players, ignoring missing values. Inner-join each kept player to M, dropping the player if M is missing. This gives one row per player. Return the player ID, the player average, D and D ÷ M. Sort by D ÷ M, highest first, with missing values last. Return the first 10
- **b3bf0189b5** A1 S6 `agg > agg > baseline > baseline`
  - Compute the following in steps. Step 1: From all tennis matches, inner-join each match to the player whose player identifier equals the match's winning player identifier (unmatched matches dropped; one row per match). Group by winning player identifier and playing hand (players.hand). Return (1) winning player identifier; (2) playing hand; (3) the average players in tournament draw (missing ignored; missing if none). Step 2: From step 1 rows, group by column (2) and return (1) column (2); (2) the average of column (3) (missing ignored; missing if none). Step 3: From step 2 rows, treat all as one group and return (1) the average of column (2) (missing ignored; missing if none). Step 4: Inner-
