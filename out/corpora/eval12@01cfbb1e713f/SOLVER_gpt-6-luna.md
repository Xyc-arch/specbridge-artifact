# Solver evaluation: `eval12@01cfbb1e713f`, solver gpt-6-luna

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 470 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 342/382 (90%) | 382 | 363 |
| explicit instructions | 382 | 307/382 (80%) | 382 | 361 |

## Paired, same 382 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 281 | 26 |
| explicit wrong | 61 | 14 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 100 | 94/100 (94%) | 99/100 (99%) |
| S4 | 86 | 74/86 (86%) | 73/86 (85%) |
| S5 | 100 | 91/100 (91%) | 71/100 (71%) |
| S6 | 96 | 83/96 (86%) | 64/96 (67%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 211 | 190/211 (90%) | 158/211 (75%) |
| A2 | 171 | 152/171 (89%) | 149/171 (87%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 7/11 (64%) | 6/11 (55%) |
| agg > agg > baseline > agg | 6 | 5/6 (83%) | 5/6 (83%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) | 1/3 (33%) |
| agg > agg > share | 4 | 4/4 (100%) | 2/4 (50%) |
| agg > agg > share > baseline | 3 | 3/3 (100%) | 1/3 (33%) |
| agg > baseline | 60 | 59/60 (98%) | 59/60 (98%) |
| agg > baseline > agg | 68 | 61/68 (90%) | 63/68 (93%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 22 | 22/22 (100%) | 12/22 (55%) |
| agg > baseline > baseline > agg | 24 | 22/24 (92%) | 15/24 (62%) |
| agg > baseline > rank | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline > share | 2 | 1/2 (50%) | 1/2 (50%) |
| agg > baseline > share > agg | 2 | 1/2 (50%) | 1/2 (50%) |
| agg > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > share | 38 | 33/38 (87%) | 38/38 (100%) |
| agg > share > agg | 3 | 2/3 (67%) | 2/3 (67%) |
| agg > share > agg > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 64 | 58/64 (91%) | 48/64 (75%) |
| agg > share > baseline > agg | 62 | 52/62 (84%) | 44/62 (71%) |
| agg > share > share | 1 | 1/1 (100%) | 0/1 (0%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 273 | 241/273 (88%) | 233/273 (85%) |
| revised | 109 | 101/109 (93%) | 74/109 (68%) |

## Wrong answers to read (a random 6)

- **6e06ef65bb** A1 S4 `agg > baseline > agg`
  - Join each track to its media type (inner join, dropping tracks with no match). For each media type name, compute the average of track file size divided by track length, and the number of tracks. Compute the average of those per-type track counts across all media types. Keep only media types whose track count is greater than that average, and for each compute the difference (track count minus that average). Return one summary row: the average of the kept types' average size-per-length values, the total of the kept types' track counts, and the average of the differences.
- **5f1a57a3d8** A1 S6 `agg > share > baseline > agg`
  - For each order reference in risk and margin, count the risk and margin records. Let T be the total of these counts. For each order reference compute R = count ÷ T (inner join to T where T is not missing). Let Y be the average of R over all order references. Inner join to Y (where Y is not missing), keep only the order references with R greater than Y, and compute D = R − Y. Return one summary row with (1) the total of the counts over those kept rows, (2) the average of R, (3) the average of D.
- **b06ce2f77f** A1 S3 `agg > share`
  - For each risk-and-margin order reference, count its records. Also compute the sum of those counts across all order references (missing ignored). Keep only rows where the sum is not missing (inner join, one row per match). Return order reference, record count, and record count divided by the sum. Sort by that ratio highest first, missing last, and return the first 10 rows.
- **156f4616e3** A1 S5 `agg > baseline > share`
  - Count addresses per city id. Compute the average of these per-city counts across all cities. For each city, compute its address count divided by that average, keeping only cities where the average is not missing. Then take the sum of the per-city address counts over those rows. Pair each city row with that sum, provided the sum is not missing, giving one row per match and dropping rows with no match. Return the city id, the address count, the count divided by the average count, and the address count divided by the sum of the counts. Sort by the last value, highest first, with missing values last, and return only the first 10 rows.
- **1d21023bca** A2 S4 `agg > agg > baseline`
  - Using the steps below, return 4 outputs from step 2 rows: (1) column 1, (2) column 2, (3) column 3 of step 2, (4) A − B, where A is column 3 of step 2 and B is column 1 of step 3. Step 2 rows are inner joined with step 3 rows whose column 1 is not missing (one row per match; unmatched step 2 rows dropped). Include only combined records where A > B.  Step 1: From each Laboratory record, inner join with each Patient record where Patient ID equals Laboratory patient ID (one combined record per match, unmatched dropped); group by Laboratory patient ID and patient sex; return (1) patient ID, (2) patient sex, (3) the average activated partial thromboplastin time in the group (missing ignored; miss
- **9b5fcd3c98** A2 S6 `agg > share > baseline > agg`
  - For each final position or retirement code (as text) in the results, sum the laps completed (L). Let T be the sum of L over all codes, so each code's share is L ÷ T. Let AVG be the average of those shares over all codes. Keep only codes whose share is greater than AVG, and give each one a difference of share − AVG. Over those kept codes, return one summary row with: the total of L, the average share, and the average difference.
