# Corpus `eval12@01cfbb1e713f`

Request: `{"name": "eval12", "count": 400, "counts": {"baseball_1": 34, "sakila_1": 33, "customers_and_invoices": 33, "chinook_1": 34, "financial": 33, "student_club": 33, "thrombosis_prediction": 34, "formula_1": 33, "archeology": 33, "insider": 34, "crypto": 33, "alien": 33}, "databases": {"baseball_1": 34, "sakila_1": 33, "customers_and_invoices": 33, "chinook_1": 34, "financial": 33, "student_club": 33, "thrombosis_prediction": 34, "formula_1": 33, "archeology": 33, "insider": 34, "crypto": 33, "alien": 33}, "seed": 20261003, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}, "target": {"cells": {"1,3": 1, "1,4": 1, "1,5": 1, "1,6": 1, "2,3": 1, "2,4": 1, "2,5": 1, "2,6": 1}}, "ops": {"rank": 2, "share": 2}, "prefer": {"joins": 2}, "variety": "normal"}`

Grammar compose-v3.4, rubric v1.1, standard **benchmark**. Complexity integrity: no task recomputes an existing aggregate (proven on the SQL); other redundancy not assessed.

**384 of 400 tasks delivered** in 2197 s with 1664 model calls (5.7 s and 4.3 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|---|
| baseball_1 | 34 | 33 | 72 | 41 | 0 | 6 | 2 | 0 | 160.3 |
| sakila_1 | 33 | 33 | 70 | 70 | 0 | 10 | 27 | 0 | 150.0 |
| customers_and_invoices | 33 | 33 | 48 | 48 | 0 | 10 | 5 | 0 | 109.3 |
| chinook_1 | 34 | 34 | 46 | 46 | 0 | 6 | 6 | 0 | 96.4 |
| financial | 33 | 33 | 41 | 41 | 0 | 0 | 8 | 0 | 165.8 |
| student_club | 33 | 33 | 41 | 41 | 0 | 1 | 7 | 0 | 80.1 |
| thrombosis_prediction | 34 | 33 | 109 | 109 | 0 | 71 | 5 | 0 | 275.9 |
| formula_1 | 33 | 33 | 49 | 48 | 0 | 5 | 10 | 0 | 107.2 |
| archeology | 33 | 33 | 56 | 56 | 0 | 19 | 4 | 0 | 141.7 |
| insider | 34 | 28 | 148 | 148 | 0 | 114 | 6 | 0 | 355.9 |
| crypto | 33 | 33 | 42 | 42 | 0 | 0 | 9 | 0 | 90.7 |
| alien | 33 | 25 | 142 | 142 | 0 | 111 | 6 | 0 | 356.8 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 1,3 | 60 | 64 |
| 1,4 | 52 | 52 |
| 1,5 | 48 | 48 |
| 1,6 | 48 | 48 |
| 2,3 | 48 | 36 |
| 2,4 | 48 | 36 |
| 2,5 | 48 | 52 |
| 2,6 | 48 | 48 |

Operations used: {'baseline': 333, 'share': 183, 'rank': 4}

Diversity: 352 distinct computations, 118 base quantities, 93 tables, 312 constructions.

Variety (normal): 21 construction shapes; the largest is 17% of the corpus (agg > baseline > agg).

## Shortfalls
- **baseball_1**: 2,3: 1 short after 6 rounds (not enough generated SQL passed the benchmark standard)
- **thrombosis_prediction**: 2,3: 1 short after 6 rounds (not enough generated SQL passed the benchmark standard)
- **insider**: 2,3: 2 short after 6 rounds (not enough generated SQL passed the benchmark standard); 2,4: 4 short after 6 rounds (not enough generated SQL passed the benchmark standard)
- **alien**: 2,3: 4 short after 6 rounds (not enough generated SQL passed the benchmark standard); 2,4: 4 short after 6 rounds (not enough generated SQL passed the benchmark standard)

## A random sample of delivered tasks

- **customers_and_invoices** A1 S3 `agg:Orders (by order_id) > baseline:all`
  - Step 1. Start from each `Order_Items` record; group the kept records by order id (`Order_Items.order_id`); each group gives one result row; for each result row, return (1) order id (`Order_Items.order_id`); (2) the average of units of product ordered (`Order_Items.product_quantity`) in the group (missing values ignored; missing when there are none). / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of c
- **archeology** A2 S5 `agg:projects (by arcref) > share:all > baseline:all`
  - Step 1. Start from each `scanqc` record; group the kept records by Points to a project for QC (`scanqc.arcref`); each group gives one result row; for each result row, return (1) Points to a project for QC (`scanqc.arcref`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step
- **baseball_1** A2 S6 `agg:team (by team_id) > share:all > baseline:all > agg:all`
  - Step 1. Start from each `manager` record; group the kept records by Team identifier (`manager.team_id`); each group gives one result row; for each result row, return (1) Team identifier (`manager.team_id`); (2) the sum of A − B in the group (missing values ignored; missing when there are none). Here A is games managed (`manager.g`); B is wins (`manager.w`). / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum 
- **chinook_1** A2 S6 `agg:Employee (by SupportRepId) > share:all > baseline:all > agg:all`
  - Step 1. Start from each `Customer` record; group the kept records by Support Rep Id (`Customer.SupportRepId`); each group gives one result row; for each result row, return (1) Support Rep Id (`Customer.SupportRepId`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3. St
- **sakila_1** A2 S5 `agg:film.rating > share:all > baseline:all`
  - Step 1. Start from each `film_category` record; combine it with each `film` record for which Unique identifier for each film (`film.film_id`) equals Unique identifier for each film (`film_category.film_id`), one combined record per match (a record without a match is dropped); group the kept records by film content rating (`film.rating`); each group gives one result row; for each result row, return (1) film content rating (`film.rating`); (2) the number of records in the group. / Step 2. Start from
- **formula_1** A2 S5 `agg:circuits.country > share:all > baseline:all`
  - Step 1. Start from each `races` record; combine it with each `circuits` record for which Unique identifier for each circuit (`circuits.circuitId`) equals circuit Id (`races.circuitId`), one combined record per match (a record without a match is dropped); group the kept records by circuit country (`circuits.country`); each group gives one result row; for each result row, return (1) circuit country (`circuits.country`); (2) the number of records in the group. / Step 2. Start from the rows of step 1;
- **thrombosis_prediction** A2 S6 `agg:Patient within Patient.SEX > baseline:all > baseline:g > agg:all`
  - Step 1. Start from each `Laboratory` record; combine it with each `Patient` record for which identification of the patient (`Patient.ID`) equals identification of the patient (`Laboratory.ID`), one combined record per match (a record without a match is dropped); group the kept records by identification of the patient (`Laboratory.ID`) and patient sex (`Patient.SEX`); each group gives one result row; for each result row, return (1) identification of the patient (`Laboratory.ID`); (2) patient sex 
- **formula_1** A1 S4 `agg:races within circuits.country > agg:g > baseline:all`
  - Step 1. Start from each `constructorStandings` record; combine it with each `races` record for which Unique identifier for each race (`races.raceId`) equals race Id (`constructorStandings.raceId`), one combined record per match (a record without a match is dropped); combine it with each `circuits` record for which Unique identifier for each circuit (`circuits.circuitId`) equals circuit Id (`races.circuitId`), one combined record per match (a record without a match is dropped); group the kept rec
