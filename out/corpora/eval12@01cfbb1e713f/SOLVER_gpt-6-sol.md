# Solver evaluation: `eval12@01cfbb1e713f`, solver gpt-6-sol

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 19 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 365/382 (96%) | 382 | 382 |
| explicit instructions | 382 | 378/382 (99%) | 382 | 381 |

## Paired, same 382 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 361 | 17 |
| explicit wrong | 4 | 0 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 100 | 97/100 (97%) | 100/100 (100%) |
| S4 | 86 | 82/86 (95%) | 86/86 (100%) |
| S5 | 100 | 98/100 (98%) | 96/100 (96%) |
| S6 | 96 | 88/96 (92%) | 96/96 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 211 | 205/211 (97%) | 210/211 (100%) |
| A2 | 171 | 160/171 (94%) | 168/171 (98%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 8/11 (73%) | 11/11 (100%) |
| agg > agg > baseline > agg | 6 | 5/6 (83%) | 6/6 (100%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > agg > share > baseline | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > baseline | 60 | 57/60 (95%) | 60/60 (100%) |
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
| revised | 109 | 107/109 (98%) | 107/109 (98%) |

## Wrong answers to read (a random 6)

- **97769b0922** A2 S6 `agg > share > baseline > agg`
  - Count product lines (order items) per product id. Let S be the total of these counts over all products, R = (product's line count ÷ S) for each product, and M the average of R over the products. Keep only products whose R is greater than M. Over those kept products, give one summary row with: (1) the total of the line counts, (2) the average of R, (3) the average of (R − M).
- **bd51f2bd3c** A2 S3 `agg > baseline`
  - For each invoice number, over its invoice line items, compute the average of A ÷ B (call it R) and the number of line records. A is line product cost (Invoice_Line_Items.derived_product_cost). B is line total cost including VAT. Compute the average of R over all invoices. Call it S. Pair each invoice row with that single value, dropping rows where S is missing. Return the invoice number, R, the line count, and R ÷ S. Sort by R ÷ S, highest first, with missing values last. Return the first 10 rows.
- **6ec8137fd3** A2 S4 `agg > agg > baseline`
  - Join each invoice line item to its order item (matching order item id), then to its order (matching order id), then to its customer (matching customer id), dropping lines with no match at any step. Group by order item id and customer town or city. For each group, compute the average product price per unit and the average of A ÷ B. A is line product cost (Invoice_Line_Items.derived_product_cost). B is line total cost including VAT. Then group those rows by town or city. For each town or city, compute the average of the group average prices and the average of the group A ÷ B averages. Call the average price per town P. Compute the average of P over all towns. Call it Q. Pair each town row with
- **bbce981d7b** A2 S6 `agg > share > baseline > agg`
  - Considering standing orders, count the orders per account. Call that count N, and let T be the sum of N over all accounts. For each account, let share = N ÷ T, and let AVGSHARE be the average of share over all accounts. Keep only accounts whose share is greater than AVGSHARE, and let diff = share − AVGSHARE. Over those kept accounts, return a single summary row with three outputs in this order: (1) the total of N, (2) the average of share, (3) the average of diff.
- **5f1a57a3d8** A1 S6 `agg > share > baseline > agg`
  - For each order reference in risk and margin, count the risk and margin records. Let T be the total of these counts. For each order reference compute R = count ÷ T (inner join to T where T is not missing). Let Y be the average of R over all order references. Inner join to Y (where Y is not missing), keep only the order references with R greater than Y, and compute D = R − Y. Return one summary row with (1) the total of the counts over those kept rows, (2) the average of R, (3) the average of D.
- **c94de1efe9** A2 S3 `agg > baseline`
  - Using the steps below, return 5 outputs from step 1 rows: (1) column 1, (2) column 2, (3) column 3, (4) column 4 of step 1, (5) A − B, where A is column 4 of step 1 and B is column 1 of step 2. Step 1 rows are inner joined with step 2 rows whose column 1 is not missing (one row per match; unmatched step 1 rows dropped). Include only combined records where A > B. Sort by A − B descending (as numbers, missing last) and return only the first 10 rows.  Step 1: From each Laboratory record, inner join with each Patient record where Patient ID equals Laboratory patient ID (one combined record per match, unmatched dropped); group by Laboratory patient ID and patient sex; return (1) patient ID, (2) p
