# Solver evaluation: `eval12@01cfbb1e713f`, solver opus

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 60 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 371/382 (97%) | 382 | 380 |

## By step depth

| step depth | tasks | natural |
|---|---|---|
| S3 | 100 | 96/100 (96%) |
| S4 | 86 | 83/86 (97%) |
| S5 | 100 | 98/100 (98%) |
| S6 | 96 | 94/96 (98%) |

## By arithmetic depth

| arithmetic depth | tasks | natural |
|---|---|---|
| A1 | 211 | 205/211 (97%) |
| A2 | 171 | 166/171 (97%) |

## By shape

| shape | tasks | natural |
|---|---|---|
| agg > agg > baseline | 11 | 9/11 (82%) |
| agg > agg > baseline > agg | 6 | 5/6 (83%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) |
| agg > agg > share | 4 | 4/4 (100%) |
| agg > agg > share > baseline | 3 | 3/3 (100%) |
| agg > baseline | 60 | 58/60 (97%) |
| agg > baseline > agg | 68 | 67/68 (99%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) |
| agg > baseline > baseline | 22 | 22/22 (100%) |
| agg > baseline > baseline > agg | 24 | 24/24 (100%) |
| agg > baseline > rank | 2 | 2/2 (100%) |
| agg > baseline > share | 2 | 2/2 (100%) |
| agg > baseline > share > agg | 2 | 2/2 (100%) |
| agg > rank | 2 | 2/2 (100%) |
| agg > share | 38 | 36/38 (95%) |
| agg > share > agg | 3 | 3/3 (100%) |
| agg > share > agg > agg | 3 | 3/3 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) |
| agg > share > baseline | 64 | 63/64 (98%) |
| agg > share > baseline > agg | 62 | 60/62 (97%) |
| agg > share > share | 1 | 1/1 (100%) |

## By writer status

| writer status | tasks | natural |
|---|---|---|
| passed | 273 | 264/273 (97%) |
| revised | 109 | 107/109 (98%) |

## Wrong answers to read (a random 6)

- **6ec8137fd3** A2 S4 `agg > agg > baseline`
  - Join each invoice line item to its order item (matching order item id), then to its order (matching order id), then to its customer (matching customer id), dropping lines with no match at any step. Group by order item id and customer town or city. For each group, compute the average product price per unit and the average of A ÷ B. A is line product cost (Invoice_Line_Items.derived_product_cost). B is line total cost including VAT. Then group those rows by town or city. For each town or city, compute the average of the group average prices and the average of the group A ÷ B averages. Call the average price per town P. Compute the average of P over all towns. Call it Q. Pair each town row with
- **c759056a31** A1 S4 `agg > agg > baseline`
  - Join each constructor standings record to its race (by race identifier), then to that race's circuit (by circuit identifier), dropping records with no match at either join, with one row per match. Group by constructorStandings.raceId (keep this raw column name) and circuit country. For each group, compute the average season-to-date constructor championship points and the average season-to-date constructor race wins, ignoring missing values. Then group those rows by circuit country. For each country, compute the average of the per-group average points and the average of the per-group average wins, ignoring missing values. Let A be a country's average of the average points. Let B be the averag
- **b3691a7c41** A2 S6 `agg > share > baseline > agg`
  - For each patient ID in the examination records, count the examination records. Let T be the total of these counts. For each patient compute ratio = count ÷ T. Let M be the average of those ratios (missing ignored). Keep only patients whose ratio is greater than M (inner join to M, dropping non-matches), with difference = ratio − M. Return one summary row with three outputs in order: the average of the kept patients' examination counts, the average of their ratios, and the average of their differences.
- **6c1b7822e6** A1 S3 `agg > baseline`
  - For each order, compute the average units of product ordered across its order items (missing values ignored); call this A. Compute the average of these per-order averages across all orders (call it B). Pair each order with B, keeping only rows where B is not missing. Return order id, A, and A − B. Sort by A − B highest first, missing values last, and return the first 10 rows.
- **40a0836cfa** A2 S5 `agg > share > baseline`
  - For each patient ID in the examination records, count the examination records. Let T be the sum of these counts over all patients (missing counts ignored). For each patient, compute R = their count ÷ T. Let M be the average of R over all patients (missing values ignored; missing if there are none). Pair each patient row with the single row holding M, using an inner join that keeps only matches where M is not missing, one row per match; patients with no matching M row (i.e., when M is missing) are dropped. Keep only patients whose R is greater than M. Return patient ID, examination count, R, and R − M, sorted by R − M highest first with missing values last, and return only the first 10 rows.
- **b9ceda40df** A1 S3 `agg > share`
  - For each payment purpose code of standing orders, compute the average standing order amount (ignoring missing values) and the number of orders. Divide that number by the total number of orders over all payment purpose codes. Return the payment purpose code, the average amount, the order count, and the ratio.
