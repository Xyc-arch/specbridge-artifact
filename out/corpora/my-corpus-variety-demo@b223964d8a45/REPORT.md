# Corpus `my-corpus-variety-demo@b223964d8a45`

Request: `{"name": "my-corpus-variety-demo", "count": 200, "counts": {"wta_1": 200}, "databases": {"wta_1": 200}, "seed": 2026, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}, "target": {"cells": {"1,3": 1, "1,4": 1, "1,5": 1, "1,6": 1, "2,3": 1, "2,4": 1, "2,5": 1, "2,6": 1}}, "ops": {"rank": 2, "share": 2}, "prefer": {"joins": 2}, "variety": "normal"}`

Grammar compose-v3.2, rubric v1.1, standard **benchmark**. Complexity integrity: no task recomputes an existing aggregate (proven on the SQL); other redundancy not assessed.

**199 of 200 tasks delivered** in 673 s with 384 model calls (3.4 s and 1.9 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|---|
| wta_1 | 200 | 199 | 388 | 251 | 0 | 37 | 15 | 0 | 671.4 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 1,3 | 25 | 24 |
| 1,4 | 25 | 25 |
| 1,5 | 25 | 25 |
| 1,6 | 25 | 25 |
| 2,3 | 25 | 25 |
| 2,4 | 25 | 25 |
| 2,5 | 25 | 25 |
| 2,6 | 25 | 25 |

Operations used: {'baseline': 186, 'share': 28, 'rank': 2}

Diversity: 179 distinct computations, 25 base quantities, 3 tables, 63 constructions.

Variety (normal): 17 construction shapes; the largest is 20% of the corpus (agg > baseline).

## Shortfalls
- **wta_1**: 1,3: 1 short after 6 rounds (not enough generated SQL passed the benchmark standard)

## A random sample of delivered tasks

- **wta_1** A1 S4 `agg:players within players.hand > share:all > agg:g`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Player ID (`matches.loser_id`), one combined record per match (a record without a match is dropped); group the kept records by Player ID (`matches.loser_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Player ID (`matches.loser_id`); (2) playing hand (`players.hand`); (3) the average of loser heigh
- **wta_1** A2 S4 `agg:players (by winner_id) > baseline:all > agg:all`
  - Step 1. Start from each `matches` record; group the kept records by Unique identifier for each player (`matches.winner_id`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.winner_id`); (2) the average of players in tournament draw (`matches.draw_size`) in the group (missing values ignored; missing when there are none); (3) the average of A − B in the group (missing values ignored; missing when there are none). Here A is loser height (
- **wta_1** A2 S6 `agg:matches.loser_ioc > share:all > baseline:all > agg:all`
  - Step 1. Start from each `matches` record; group the kept records by loser country code (`matches.loser_ioc`); each group gives one result row; for each result row, return (1) loser country code (`matches.loser_ioc`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3. Sta
- **wta_1** A1 S3 `agg:players (by player_id) > share:all`
  - Step 1. Start from each `rankings` record; group the kept records by Unique player identifiers (`rankings.player_id`); each group gives one result row; for each result row, return (1) Unique player identifiers (`rankings.player_id`); (2) the average of tournaments played (`rankings.tours`) in the group (missing values ignored; missing when there are none); (3) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; f
- **wta_1** A1 S5 `agg:players within players.hand > baseline:all > agg:g > agg:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **wta_1** A1 S4 `agg:players within players.hand > agg:g > baseline:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **wta_1** A2 S4 `agg:players within players.hand > agg:g > baseline:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **wta_1** A2 S6 `agg:players within players.hand > baseline:all > baseline:g > agg:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
