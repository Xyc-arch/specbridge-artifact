# Corpus `my-corpus-variety-demo@8fc775be66aa`

Request: `{"name": "my-corpus-variety-demo", "count": 200, "counts": {"wta_1": 200}, "databases": {"wta_1": 200}, "seed": 2026, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}, "target": {"cells": {"1,3": 1, "1,4": 1, "1,5": 1, "1,6": 1, "2,3": 1, "2,4": 1, "2,5": 1, "2,6": 1}}, "ops": {"rank": 2, "share": 2}, "prefer": {"joins": 2}, "variety": "normal"}`

Grammar compose-v3.1 (frozen), rubric v1.1, standard **benchmark**. Complexity integrity: not assessed.

**200 of 200 tasks delivered** in 588 s with 508 model calls (2.9 s and 2.5 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|---|
| wta_1 | 200 | 200 | 414 | 260 | 0 | 43 | 17 | 0 | 586.7 |

Dropped before review (no model calls spent): {'dropped before review: derived measure is constant': 7, 'dropped before review: derived measure restates an operand': 10, 'dropped before review: empty answer': 4, 'dropped before review: denominator not positive': 17}

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 1,3 | 25 | 25 |
| 1,4 | 25 | 25 |
| 1,5 | 25 | 25 |
| 1,6 | 25 | 25 |
| 2,3 | 25 | 25 |
| 2,4 | 25 | 25 |
| 2,5 | 25 | 25 |
| 2,6 | 25 | 25 |

Operations used: {'baseline': 189, 'share': 24, 'rank': 4}

Diversity: 166 distinct computations, 25 base quantities, 3 tables, 68 constructions.

Variety (normal): 15 construction shapes; the largest is 21% of the corpus (agg > baseline).

## Shortfalls

None.

## A random sample of delivered tasks

- **wta_1** A1 S4 `agg:players within players.hand > agg:g > baseline:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Player ID (`matches.loser_id`), one combined record per match (a record without a match is dropped); group the kept records by Player ID (`matches.loser_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Player ID (`matches.loser_id`); (2) playing hand (`players.hand`); (3) the average of players in 
- **wta_1** A2 S4 `agg:matches.surface > baseline:all > agg:all`
  - Step 1. Start from each `matches` record; group the kept records by court surface (`matches.surface`); each group gives one result row; for each result row, return (1) court surface (`matches.surface`); (2) the average of A ÷ B in the group (missing values ignored; missing when there are none). Here A is loser ranking points (`matches.loser_rank_points`); B is winner ranking points (`matches.winner_rank_points`). / Step 2. Start from the rows of step 1; all kept records form one group, which gives
- **wta_1** A2 S6 `agg:players within players.hand > baseline:all > baseline:g > agg:g`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **wta_1** A1 S3 `agg:players (by player_id) > baseline:all`
  - Step 1. Start from each `rankings` record; group the kept records by Unique player identifiers (`rankings.player_id`); each group gives one result row; for each result row, return (1) Unique player identifiers (`rankings.player_id`); (2) the average of ranking points (`rankings.ranking_points`) in the group (missing values ignored; missing when there are none). / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the 
- **wta_1** A1 S5 `agg:players within players.hand > baseline:g > agg:g > agg:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **wta_1** A1 S4 `agg:players within players.hand > agg:g > baseline:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Player ID (`matches.loser_id`), one combined record per match (a record without a match is dropped); group the kept records by Player ID (`matches.loser_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Player ID (`matches.loser_id`); (2) playing hand (`players.hand`); (3) the average of loser heigh
- **wta_1** A2 S4 `agg:players within players.hand > agg:g > baseline:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **wta_1** A2 S6 `agg:players (by loser_id) > baseline:all > baseline:all > agg:all`
  - Step 1. Start from each `matches` record; group the kept records by Player ID (`matches.loser_id`); each group gives one result row; for each result row, return (1) Player ID (`matches.loser_id`); (2) the average of A − B in the group (missing values ignored; missing when there are none). Here A is loser ranking points (`matches.loser_rank_points`); B is winner ranking points (`matches.winner_rank_points`). / Step 2. Start from the rows of step 1; all kept records form one group, which gives one r
