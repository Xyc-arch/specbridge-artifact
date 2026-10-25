# Corpus `setup-smoke@530deb57082e`

Request: `{"name": "setup-smoke", "count": 3, "seed": 3, "databases": {"car_1": 1}, "target": {"preset": "medium"}, "standard": "benchmark", "max_move": {"arith": 1, "steps": 1}}`

Grammar compose-v3.1 (frozen), rubric v1.1, standard **benchmark**. Complexity integrity: not assessed.

**3 of 3 tasks delivered** in 24 s with 18 model calls (8.0 s and 6.0 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|
| car_1 | 3 | 3 | 9 | 9 | 0 | 0 | 0 | 15.8 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 0,2 | 0 | 1 |
| 1,2 | 1 | 0 |
| 1,3 | 1 | 1 |
| 1,4 | 1 | 1 |

Operations used: {'aggregate only': 1, 'share': 1, 'baseline': 1}

Diversity: 3 distinct computations, 0 base quantities, 4 tables, 3 constructions.

## Shortfalls
- **car_1**: setup: set up during this build (catalogue built now; no reviewed history, so oversampling used a default pass rate)

## A random sample of delivered tasks

- **car_1** A0 S2 `agg:continents.Continent > agg:all`
  - Step 1. Start from each `countries` record; combine it with each `continents` record for which Cont Id (`continents.ContId`) equals Continent (`countries.Continent`), one combined record per match (a record without a match is dropped); group the kept records by continent name (`continents.Continent`); each group gives one result row; for each result row, return (1) continent name (`continents.Continent`); (2) the number of records in the group. / Step 2 (the answer). Start from the rows of step 1;
- **car_1** A1 S4 `agg:car_makers within continents.Continent > baseline:g > agg:g`
  - Step 1. Start from each `model_list` record; combine it with each `car_makers` record for which Id (`car_makers.Id`) equals Maker (`model_list.Maker`), one combined record per match (a record without a match is dropped); combine it with each `countries` record for which Country Id (`countries.CountryId`) equals Country (`car_makers.Country`) (compared as numbers: the text is read as a number), one combined record per match (a record without a match is dropped); combine it with each `continents` 
- **car_1** A1 S3 `agg:continents.Continent > share:all`
  - Step 1. Start from each `countries` record; combine it with each `continents` record for which Cont Id (`continents.ContId`) equals Continent (`countries.Continent`), one combined record per match (a record without a match is dropped); group the kept records by continent name (`continents.Continent`); each group gives one result row; for each result row, return (1) continent name (`continents.Continent`); (2) the number of records in the group. / Step 2. Start from the rows of step 1; all kept rec
