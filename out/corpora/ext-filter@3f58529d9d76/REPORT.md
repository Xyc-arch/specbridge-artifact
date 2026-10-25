# Corpus `ext-filter@3f58529d9d76`

Request: `{"name": "ext-filter", "seed": 20261016, "standard": "benchmark", "extra": ["filter"], "counts": {"baseball_1": 15, "sakila_1": 15, "customers_and_invoices": 15, "chinook_1": 15, "financial": 15, "student_club": 15, "thrombosis_prediction": 15, "formula_1": 15, "archeology": 15, "insider": 15, "crypto": 15, "alien": 15}, "databases": {"baseball_1": 1, "sakila_1": 1, "customers_and_invoices": 1, "chinook_1": 1, "financial": 1, "student_club": 1, "thrombosis_prediction": 1, "formula_1": 1, "archeology": 1, "insider": 1, "crypto": 1, "alien": 1}, "count": 180, "max_move": {"arith": 1, "steps": 1}, "target": {"cells": {"0,1": 1, "1,1": 1, "0,2": 1, "1,2": 1, "1,3": 1, "2,3": 1}}, "variety": "more"}`

Grammar compose-v3.4, rubric v1.1, standard **benchmark**. Complexity integrity: no task recomputes an existing aggregate (proven on the SQL); other redundancy not assessed.

**161 of 180 tasks delivered** in 1758 s with 974 model calls (10.9 s and 6.0 calls per delivered task).

## By database

| database | planned | delivered | generated | reviewed now | review reused | failed the standard | passed, not needed | packaging refused | seconds |
|---|---|---|---|---|---|---|---|---|---|
| baseball_1 | 15 | 13 | 53 | 29 | 0 | 4 | 12 | 0 | 152.7 |
| sakila_1 | 15 | 15 | 32 | 32 | 0 | 8 | 9 | 0 | 90.0 |
| customers_and_invoices | 15 | 15 | 32 | 32 | 0 | 8 | 9 | 0 | 98.4 |
| chinook_1 | 15 | 15 | 25 | 25 | 0 | 3 | 7 | 0 | 61.4 |
| financial | 15 | 15 | 23 | 23 | 0 | 0 | 8 | 0 | 106.8 |
| student_club | 15 | 15 | 30 | 30 | 0 | 1 | 14 | 0 | 75.7 |
| thrombosis_prediction | 15 | 12 | 75 | 75 | 0 | 46 | 17 | 0 | 218.6 |
| formula_1 | 15 | 15 | 27 | 23 | 0 | 6 | 2 | 0 | 69.3 |
| archeology | 15 | 15 | 25 | 25 | 0 | 6 | 4 | 0 | 89.0 |
| insider | 15 | 8 | 86 | 86 | 0 | 74 | 4 | 0 | 262.5 |
| crypto | 15 | 15 | 30 | 30 | 0 | 3 | 12 | 0 | 98.1 |
| alien | 15 | 8 | 79 | 79 | 0 | 63 | 8 | 0 | 236.8 |

## Requested vs delivered by depth cell (all databases)

| A,S | requested | delivered |
|---|---|---|
| 0,1 | 36 | 39 |
| 0,2 | 36 | 36 |
| 1,1 | 36 | 23 |
| 1,2 | 24 | 18 |
| 1,3 | 24 | 28 |
| 2,3 | 24 | 17 |

Operations used: {'aggregate only': 122, 'baseline': 30, 'share': 9}

Diversity: 155 distinct computations, 89 base quantities, 68 tables, 125 constructions.

Variety (more): 4 construction shapes; the largest is 52% of the corpus (agg).

## Shortfalls
- **baseball_1**: 1,1: 2 short after 4 rounds (not enough generated SQL passed the benchmark standard)
- **thrombosis_prediction**: 1,1: 2 short after 4 rounds (not enough generated SQL passed the benchmark standard); 2,3: 1 short after 4 rounds (not enough generated SQL passed the benchmark standard)
- **insider**: 1,1: 3 short after 4 rounds (not enough generated SQL passed the benchmark standard); 1,2: 2 short after 4 rounds (not enough generated SQL passed the benchmark standard); 2,3: 2 short after 4 rounds (not enough generated SQL passed the benchmark standard)
- **alien**: 1,1: 3 short after 4 rounds (not enough generated SQL passed the benchmark standard); 1,2: 2 short after 4 rounds (not enough generated SQL passed the benchmark standard); 2,3: 2 short after 4 rounds (not enough generated SQL passed the benchmark standard)

## A random sample of delivered tasks

- **customers_and_invoices** A0 S2 `agg:Product_Categories (by production_type_code)`
  - Start from each `Products` record; keep only the records for which production type code (`Products.production_type_code`) is among the values returned by [start from each `Products` record; keep only the records for which all of the following hold: [1] product size (`Products.product_size`) equals 'Small' (compared as text, character by character); [2] product color (`Products.product_color`) equals 'Yellow' (compared as text, character by character); [3] it is not true that production type code
- **crypto** A0 S2 `agg:orders (by ordersmark) > agg:all`
  - Step 1. Start from each `orderexecutions` record; keep only the records for which all of the following hold: [1] expiry time (`orderexecutions.expirespot`) is at least '2025-02-28 08:29:46.10496' (compared as text, character by character); [2] expiry time (`orderexecutions.expirespot`) is at most '2025-03-13 08:29:46.068533' (compared as text, character by character) [end]; group the kept records by ordersmark (`orderexecutions.ordersmark`); each group gives one result row; for each result row, 
- **sakila_1** A1 S1 `agg:film.rating`
  - Start from each `film` record; keep only the records for which one-time asset value of a physical film copy (charged if lost or damaged) (`film.replacement_cost`) is at least 20.99; group the kept records by film content rating (`film.rating`); each group gives one result row; for each result row, return (1) film content rating (`film.rating`); (2) the average of film running time (`film.length`) in the group (missing values ignored; missing when there are none); (3) the average of A ÷ B in the 
- **financial** A0 S2 `agg:account within account.frequency > agg:all`
  - Step 1. Start from each `trans` record; combine it with each `account` record for which the id of the account (`account.account_id`) equals Account number (`trans.account_id`), one combined record per match (a record without a match is dropped); keep only the records for which all of the following hold: [1] transaction date (`trans.date`) is at least '1996-05-09' (compared as text, character by character); [2] transaction date (`trans.date`) is at most '1998-01-06' (compared as text, character b
- **customers_and_invoices** A0 S1 `agg:all`
  - Start from each `Accounts` record; keep only the records for which all of the following hold: [1] account opening date (`Accounts.date_account_opened`) is at least '2011-03-29 15:06:59' (compared as text, character by character); [2] account opening date (`Accounts.date_account_opened`) is at most '2015-02-02 09:47:08' (compared as text, character by character) [end]; all kept records form one group, which gives one result row; for each result row, return (1) the number of records in the group.
- **archeology** A1 S3 `agg:equipment (by equipref) > agg:all`
  - Step 1. Start from each `scanprocessing` record; keep only the records for which Site code for which processing applies (`scanprocessing.zoneref`) is none of the values returned by [start from each `scanprocessing` record; keep only the records for which all of the following hold: [1] metadata framework (`scanprocessing.metabench`) equals 'Dublin Core' (compared as text, character by character); [2] it is not true that Site code for which processing applies (`scanprocessing.zoneref`) is missing 
- **archeology** A0 S1 `agg:sites within sites.healtheval`
  - Start from each `scanenvironment` record; combine it with each `sites` record for which Primary key for a site (`sites.zoneregistry`) equals zoneref (`scanenvironment.zoneref`) (compared as text, character by character), one combined record per match (a record without a match is dropped); keep only the records for which air temperature (`scanenvironment.ambictemp`) is at least 21.0; group the kept records by zoneref (`scanenvironment.zoneref`) and health and safety approval status (`sites.health
- **archeology** A1 S1 `agg:sites.riskeval`
  - Start from each `scans` record; combine it with each `sites` record for which Primary key for a site (`sites.zoneregistry`) equals zoneref (`scans.zoneref`) (compared as text, character by character), one combined record per match (a record without a match is dropped); keep only the records for which all of the following hold: [1] scan timestamp (`scans.chronotag`) is at least '2024-06-06 11:53:59.684274' (compared as text, character by character); [2] scan timestamp (`scans.chronotag`) is at mo
