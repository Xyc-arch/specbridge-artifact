# Corpus `pilot-dev@09cacc14fa59`

Request: `{"name": "pilot-dev", "count": 48, "counts": {"wta_1": 16, "toxicology": 16, "news": 16}, "databases": {"wta_1": 16, "toxicology": 16, "news": 16}, "seed": 20261002, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}, "target": {"cells": {"1,3": 1, "1,4": 1, "1,5": 1, "1,6": 1, "2,3": 1, "2,4": 1, "2,5": 1, "2,6": 1}}, "ops": {"rank": 2, "share": 2}, "prefer": {"joins": 2}, "variety": "normal"}`

Grammar compose-v3.4, rubric v1.1, standard **benchmark**. Complexity integrity: no task recomputes an existing aggregate (proven on the SQL); other redundancy not assessed.

**48 of 48 tasks delivered** in 168 s with 36 model calls (3.5 s and 0.8 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|---|
| wta_1 | 16 | 16 | 36 | 26 | 0 | 7 | 3 | 0 | 78.0 |
| toxicology | 16 | 16 | 22 | 22 | 0 | 0 | 6 | 0 | 2.1 |
| news | 16 | 16 | 37 | 37 | 0 | 18 | 3 | 0 | 81.3 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 1,3 | 6 | 8 |
| 1,4 | 6 | 6 |
| 1,5 | 6 | 6 |
| 1,6 | 6 | 6 |
| 2,3 | 6 | 4 |
| 2,4 | 6 | 4 |
| 2,5 | 6 | 8 |
| 2,6 | 6 | 6 |

Operations used: {'baseline': 43, 'share': 22}

Diversity: 42 distinct computations, 24 base quantities, 13 tables, 41 constructions.

Variety (normal): 11 construction shapes; the largest is 18% of the corpus (agg > baseline > agg).

## Shortfalls

None.

## A random sample of delivered tasks

- **wta_1** A2 S3 `agg:players within players.hand > baseline:all`
  - Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.win
- **news** A1 S5 `agg:users within users.seglabel > share:all > share:g`
  - Step 1. Start from each `devices` record; combine it with each `users` record for which userkey (`users.userkey`) equals uselink (`devices.uselink`), one combined record per match (a record without a match is dropped); group the kept records by uselink (`devices.uselink`) and user segment (`users.seglabel`); each group gives one result row; for each result row, return (1) uselink (`devices.uselink`); (2) user segment (`users.seglabel`); (3) the number of records in the group. / Step 2. Start from 
- **wta_1** A1 S5 `agg:matches.winner_ioc > baseline:all > baseline:all`
  - Step 1. Start from each `matches` record; group the kept records by winner country code (`matches.winner_ioc`); each group gives one result row; for each result row, return (1) winner country code (`matches.winner_ioc`); (2) the average of players in tournament draw (`matches.draw_size`) in the group (missing values ignored; missing when there are none). / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average
- **toxicology** A1 S3 `agg:atom.element > baseline:all`
  - Step 1. Start from each `atom` record; group the kept records by chemical element of the atom (`atom.element`); each group gives one result row; for each result row, return (1) chemical element of the atom (`atom.element`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none). / 
- **wta_1** A1 S6 `agg:matches.winner_ioc > share:all > baseline:all > agg:all`
  - Step 1. Start from each `matches` record; group the kept records by winner country code (`matches.winner_ioc`); each group gives one result row; for each result row, return (1) winner country code (`matches.winner_ioc`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3.
- **toxicology** A2 S6 `agg:molecule (by molecule_id) > share:all > baseline:all > agg:all`
  - Step 1. Start from each `atom` record; group the kept records by molecule id (`atom.molecule_id`); each group gives one result row; for each result row, return (1) molecule id (`atom.molecule_id`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3. Start from the rows of
- **toxicology** A2 S5 `agg:molecule (by molecule_id) > share:all > baseline:all`
  - Step 1. Start from each `bond` record; group the kept records by molecule id (`bond.molecule_id`); each group gives one result row; for each result row, return (1) molecule id (`bond.molecule_id`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3. Start from the rows of
- **toxicology** A2 S6 `agg:atom.element > share:all > baseline:all > agg:all`
  - Step 1. Start from each `atom` record; group the kept records by chemical element of the atom (`atom.element`); each group gives one result row; for each result row, return (1) chemical element of the atom (`atom.element`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step
