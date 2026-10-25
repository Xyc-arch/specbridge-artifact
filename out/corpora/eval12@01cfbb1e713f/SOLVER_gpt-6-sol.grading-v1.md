# Solver evaluation: `eval12@01cfbb1e713f`, solver gpt-6-sol

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 748 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 364/382 (95%) | 382 | 381 |
| explicit instructions | 382 | 378/382 (99%) | 382 | 381 |

## Paired, same 382 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 360 | 18 |
| explicit wrong | 4 | 0 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 100 | 96/100 (96%) | 100/100 (100%) |
| S4 | 86 | 82/86 (95%) | 86/86 (100%) |
| S5 | 100 | 98/100 (98%) | 96/100 (96%) |
| S6 | 96 | 88/96 (92%) | 96/96 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 211 | 205/211 (97%) | 210/211 (100%) |
| A2 | 171 | 159/171 (93%) | 168/171 (98%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 8/11 (73%) | 11/11 (100%) |
| agg > agg > baseline > agg | 6 | 5/6 (83%) | 6/6 (100%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > agg > share > baseline | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > baseline | 60 | 56/60 (93%) | 60/60 (100%) |
| agg > baseline > agg | 68 | 67/68 (99%) | 68/68 (100%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 22 | 22/22 (100%) | 20/22 (91%) |
| agg > baseline > baseline > agg | 24 | 20/24 (83%) | 24/24 (100%) |
| agg > baseline > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > baseline > share | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline > share > agg | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > share | 38 | 38/38 (100%) | 38/38 (100%) |
| agg > share > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 64 | 64/64 (100%) | 63/64 (98%) |
| agg > share > baseline > agg | 62 | 58/62 (94%) | 62/62 (100%) |
| agg > share > share | 1 | 1/1 (100%) | 0/1 (0%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 273 | 258/273 (95%) | 271/273 (99%) |
| revised | 109 | 106/109 (97%) | 107/109 (98%) |

## Wrong answers to read (a random 6)

- **69c4bd1cc2** A2 S6 `agg > share > baseline > agg`
  - Count invoices per order id. Let S be the total of these counts over all orders, R = (order's invoice count ÷ S) for each order, and M the average of R over the orders. Keep only orders whose R is greater than M. Over those kept orders, give one summary row with: (1) the total of the invoice counts, (2) the average of R, (3) the average of (R − M).
- **6c1b7822e6** A1 S3 `agg > baseline`
  - For each order, compute the average units of product ordered across its order items (missing values ignored); call this A. Compute the average of these per-order averages across all orders (call it B). Pair each order with B, keeping only rows where B is not missing. Return order id, A, and A − B. Sort by A − B highest first, missing values last, and return the first 10 rows.
- **c94de1efe9** A2 S3 `agg > baseline`
  - Using the steps below, return 5 outputs from step 1 rows: (1) column 1, (2) column 2, (3) column 3, (4) column 4 of step 1, (5) A − B, where A is column 4 of step 1 and B is column 1 of step 2. Step 1 rows are inner joined with step 2 rows whose column 1 is not missing (one row per match; unmatched step 1 rows dropped). Include only combined records where A > B. Sort by A − B descending (as numbers, missing last) and return only the first 10 rows.  Step 1: From each Laboratory record, inner join with each Patient record where Patient ID equals Laboratory patient ID (one combined record per match, unmatched dropped); group by Laboratory patient ID and patient sex; return (1) patient ID, (2) p
- **ef4d2acbf1** A2 S6 `agg > baseline > baseline > agg`
  - Start with each lab record and compute, per patient (grouped by patient identifier), the average of hemoglobin concentration ÷ hematocrit fraction across that patient's records (missing values ignored; missing if none). Call this per-patient value R. Then compute the overall average of R across all patients (missing values ignored). Keep only patients whose R is greater than that overall average (an overall average that is missing drops everything), and for each compute D1 = R − overall average. Next compute the average of R over these kept patients, call it M2. Keep only those kept patients whose R is greater than M2 (an M2 that is missing drops everything), and for each compute D2 = R − M2
- **69dd47a5b6** A2 S4 `agg > agg > baseline`
  - For each pair of account number and region name, join each transaction to its account, then to the district whose district id equals the account's district id. Drop any transaction with no match at either join. Per pair, compute M as the average of signed transaction amounts, and B as the average account balance after transaction. A credit transaction counts as +amount, a withdrawal counts as −amount, and any other transaction type is ignored. For each region name, compute RM as the average of M over the pairs with that region, and RB as the average of B over the pairs with that region, ignoring missing values. Let G be the average of RM over all regions, ignoring missing values. Pair every 
- **5f1a57a3d8** A1 S6 `agg > share > baseline > agg`
  - For each order reference in risk and margin, count the risk and margin records. Let T be the total of these counts. For each order reference compute R = count ÷ T (inner join to T where T is not missing). Let Y be the average of R over all order references. Inner join to Y (where Y is not missing), keep only the order references with R greater than Y, and compute D = R − Y. Return one summary row with (1) the total of the counts over those kept rows, (2) the average of R, (3) the average of D.
