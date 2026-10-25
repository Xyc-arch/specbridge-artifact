# Corpus `lean-test@4bdef56762cc`

Request: `{"name": "lean-test", "count": 20, "counts": {"car_1": 20}, "databases": {"car_1": 20}, "seed": 11, "target": {"preset": "medium"}, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}}`

Grammar compose-v3.1 (frozen), rubric v1.1, standard **benchmark**. Complexity integrity: not assessed.

**20 of 20 tasks delivered** in 40 s with 52 model calls (2.0 s and 2.6 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|---|
| car_1 | 20 | 20 | 26 | 26 | 0 | 0 | 6 | 0 | 40.2 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 0,2 | 0 | 4 |
| 1,2 | 4 | 0 |
| 1,3 | 4 | 10 |
| 1,4 | 3 | 6 |
| 2,2 | 3 | 0 |
| 2,3 | 3 | 0 |
| 2,4 | 3 | 0 |

Operations used: {'baseline': 12, 'aggregate only': 4, 'share': 4}

Diversity: 17 distinct computations, 0 base quantities, 4 tables, 17 constructions.

## Shortfalls

None.

## A random sample of delivered tasks

- **car_1** A1 S3 `agg:continents (by Continent) > baseline:all`
  - Step 1. Start from each `countries` record; group the kept records by Continent (`countries.Continent`); each group gives one result row; for each result row, return (1) Continent (`countries.Continent`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3 (the answer)
- **car_1** A1 S4 `agg:countries within continents.Continent > share:all > agg:g`
  - Step 1. Start from each `car_makers` record; combine it with each `countries` record for which Country Id (`countries.CountryId`) equals Country (`car_makers.Country`) (compared as numbers: the text is read as a number), one combined record per match (a record without a match is dropped); combine it with each `continents` record for which Cont Id (`continents.ContId`) equals Continent (`countries.Continent`), one combined record per match (a record without a match is dropped); group the kept rec
- **car_1** A0 S2 `agg:car_makers (by Maker) > agg:all`
  - Step 1. Start from each `model_list` record; group the kept records by Maker (`model_list.Maker`); each group gives one result row; for each result row, return (1) Maker (`model_list.Maker`); (2) the number of records in the group. / Step 2 (the answer). Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
- **car_1** A1 S3 `agg:car_makers within continents.Continent > baseline:all`
  - Step 1. Start from each `model_list` record; combine it with each `car_makers` record for which Id (`car_makers.Id`) equals Maker (`model_list.Maker`), one combined record per match (a record without a match is dropped); combine it with each `countries` record for which Country Id (`countries.CountryId`) equals Country (`car_makers.Country`) (compared as numbers: the text is read as a number), one combined record per match (a record without a match is dropped); combine it with each `continents` 
- **car_1** A0 S2 `agg:countries (by Country) > agg:all`
  - Step 1. Start from each `car_makers` record; group the kept records by Country (`car_makers.Country`); each group gives one result row; for each result row, return (1) Country (`car_makers.Country`); (2) the number of records in the group. / Step 2 (the answer). Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
- **car_1** A1 S3 `agg:countries (by Country) > share:all`
  - Step 1. Start from each `car_makers` record; group the kept records by Country (`car_makers.Country`); each group gives one result row; for each result row, return (1) Country (`car_makers.Country`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3 (the answer). Start f
- **car_1** A1 S3 `agg:continents (by Continent) > baseline:all`
  - Step 1. Start from each `countries` record; group the kept records by Continent (`countries.Continent`); each group gives one result row; for each result row, return (1) Continent (`countries.Continent`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3 (the answer)
- **car_1** A1 S4 `agg:countries (by Country) > baseline:all > agg:all`
  - Step 1. Start from each `car_makers` record; group the kept records by Country (`car_makers.Country`); each group gives one result row; for each result row, return (1) Country (`car_makers.Country`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none). / Step 3. Start from the r
