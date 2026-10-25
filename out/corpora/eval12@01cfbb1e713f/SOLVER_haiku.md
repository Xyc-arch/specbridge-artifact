# Solver evaluation: `eval12@01cfbb1e713f`, solver haiku

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 0 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 349/382 (91%) | 382 | 376 |
| explicit instructions | 382 | 343/382 (90%) | 382 | 366 |

## Paired, same 382 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 313 | 30 |
| explicit wrong | 36 | 3 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 100 | 94/100 (94%) | 93/100 (93%) |
| S4 | 86 | 79/86 (92%) | 81/86 (94%) |
| S5 | 100 | 85/100 (85%) | 86/100 (86%) |
| S6 | 96 | 91/96 (95%) | 83/96 (86%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 211 | 196/211 (93%) | 181/211 (86%) |
| A2 | 171 | 153/171 (89%) | 162/171 (95%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 8/11 (73%) | 11/11 (100%) |
| agg > agg > baseline > agg | 6 | 3/6 (50%) | 6/6 (100%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) | 2/3 (67%) |
| agg > agg > share | 4 | 3/4 (75%) | 3/4 (75%) |
| agg > agg > share > baseline | 3 | 3/3 (100%) | 2/3 (67%) |
| agg > baseline | 60 | 57/60 (95%) | 55/60 (92%) |
| agg > baseline > agg | 68 | 65/68 (96%) | 64/68 (94%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 22 | 20/22 (91%) | 16/22 (73%) |
| agg > baseline > baseline > agg | 24 | 24/24 (100%) | 24/24 (100%) |
| agg > baseline > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > baseline > share | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > baseline > share > agg | 2 | 2/2 (100%) | 1/2 (50%) |
| agg > rank | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > share | 38 | 36/38 (95%) | 36/38 (95%) |
| agg > share > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > agg | 3 | 3/3 (100%) | 1/3 (33%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 64 | 54/64 (84%) | 58/64 (91%) |
| agg > share > baseline > agg | 62 | 57/62 (92%) | 52/62 (84%) |
| agg > share > share | 1 | 1/1 (100%) | 1/1 (100%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 273 | 244/273 (89%) | 259/273 (95%) |
| revised | 109 | 105/109 (96%) | 84/109 (77%) |

## Wrong answers to read (a random 6)

- **a0375d75e0** A2 S6 `agg > share > baseline > agg`
  - Join each disposition to its client (drop if no match by client id), then to the client's district (drop if no match). Group by region name, counting the dispositions per region. Let T be the total of those counts over all regions. For each region compute share = count ÷ T. Let M be the average of the shares over all regions (missing ignored). Keep only regions whose share is greater than M, and compute share − M for them. Return one summary row with three outputs, in order: the average of the kept regions' counts, the average of their shares, and the average of their share − M values.
- **4e90c69b8d** A1 S5 `agg > agg > baseline > agg`
  - Match each customer invoice to its customer. Invoices with no matching customer are dropped. For each pair of customer id and customer country, compute the average invoice total amount. Then, for each country, average those per-customer averages. Next, compute the average of those per-country values across all countries. Keep only the countries whose value is greater than that overall average. Show one summary row with two outputs, in this order: (1) the average of the kept countries' values, and (2) the average of the differences, where each difference is the country's value minus the overall average.
- **70ea90e305** A2 S5 `agg > share > baseline`
  - Count employees grouped by the id of their manager (reports-to). Compute the total of these counts. For each manager group, compute share = count divided by the total. Compute the average of those shares (missing ignored). Join each group row to that average (inner join, dropping rows if the average is missing), one row per match. Return the manager id, the count, the share, and share minus the average share. Sort by that last difference highest first, missing last, and return the first 10 rows.
- **989c45ebd2** A2 S5 `agg > share > baseline`
  - Step 1: Join each advanced behavior record to each transaction record whose trade-day transaction record id equals the advanced behavior record's linked transaction record id. Then join to each trader record whose trader account id equals the transaction record's trader account id. Compare both joins as text, character by character. Drop records with no match. Group by trader type. For each group return the trader type and the number of records in the group. Step 2: Treat all step 1 rows as one group and return the sum of step 1's column 2 (missing values ignored). Step 3: Join the step 1 rows to the step 2 row where step 2's value is not missing. Drop rows with no match. Return step 1's col
- **0a50862c56** A1 S5 `agg > share > baseline`
  - Join each examination record to the patient record with the same patient identifier (inner join; unmatched examination records are dropped; one row per match) and count records per primary diagnosed disease. Let T be the sum of those counts. For each diagnosis compute count ÷ T (inner join to T; T must be non-missing). Let M be the average of the per-diagnosis counts (missing values ignored). Return, joined to M by inner join (M must be non-missing; one row per match): diagnosis, count, count ÷ T, and count − M, including only diagnoses where the count is greater than M.
- **6c50e3c2db** A2 S4 `agg > baseline > agg`
  - Group fees by fee order reference, returning: order reference, the average of (fee rate − maker rebate rate) (missing ignored; missing if none), and the record count. Call this step 1. Step 2 is the average of that column-2 average over step 1 rows (missing ignored; missing if none). Step 3: inner-join step 1 to step 2 where the step 2 value is not missing (one row per match), keep only rows where the group's average difference is greater than the step 2 value, and return order reference, average difference, record count, and average difference minus the step 2 value. Return one summary row with the average of each of the last three step 3 columns, in order: average difference, record count,
