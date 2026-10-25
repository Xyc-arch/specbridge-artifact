# Solver evaluation: `eval12@01cfbb1e713f`, solver sonnet

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 318 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 363/382 (95%) | 382 | 376 |
| explicit instructions | 382 | 380/382 (99%) | 382 | 382 |

## Paired, same 382 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 362 | 18 |
| explicit wrong | 1 | 1 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 100 | 96/100 (96%) | 100/100 (100%) |
| S4 | 86 | 76/86 (88%) | 85/86 (99%) |
| S5 | 100 | 98/100 (98%) | 100/100 (100%) |
| S6 | 96 | 93/96 (97%) | 95/96 (99%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 211 | 206/211 (98%) | 209/211 (99%) |
| A2 | 171 | 157/171 (92%) | 171/171 (100%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 8/11 (73%) | 10/11 (91%) |
| agg > agg > baseline > agg | 6 | 5/6 (83%) | 6/6 (100%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > agg > share > baseline | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > baseline | 60 | 57/60 (95%) | 60/60 (100%) |
| agg > baseline > agg | 68 | 61/68 (90%) | 68/68 (100%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 22 | 22/22 (100%) | 22/22 (100%) |
| agg > baseline > baseline > agg | 24 | 24/24 (100%) | 24/24 (100%) |
| agg > baseline > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > baseline > share | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > baseline > share > agg | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > share | 38 | 37/38 (97%) | 38/38 (100%) |
| agg > share > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 64 | 63/64 (98%) | 64/64 (100%) |
| agg > share > baseline > agg | 62 | 59/62 (95%) | 61/62 (98%) |
| agg > share > share | 1 | 1/1 (100%) | 1/1 (100%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 273 | 256/273 (94%) | 272/273 (100%) |
| revised | 109 | 107/109 (98%) | 108/109 (99%) |

## Wrong answers to read (a random 6)

- **cd6c8a9de0** A2 S4 `agg > baseline > agg`
  - Group product lines (each invoice line item matched to its product by product id; lines with no matching product are dropped) by product color. For each color compute: X = the average line product cost (Invoice_Line_Items.derived_product_cost, missing values ignored) and Y = the average of (line total cost including VAT ÷ product price per unit) per line (missing values ignored). Let T be the average of Y over all the color groups (missing ignored). Keep only colors whose Y is greater than T. Then give one summary row with: (1) the average of X over those colors, (2) the average of Y over those colors, (3) the average of (Y − T) over those colors.
- **60a79fabd7** A2 S4 `agg > baseline > agg`
  - Join each scan session to its site where the site's unique code equals the scan's site code (compared as text; inner join, drop scans with no site). Group by health and safety approval status, computing the average of scan file size ÷ scanning duration (ignore missing) and the number of records. Let G be the average across groups of that group average (ignore missing). Keep only groups (inner join with G; drop if G is missing) whose group average is greater than G, computing group average − G. Over those kept groups, return one row with: the average of the group averages, the average of the record counts, and the average of group average − G.
- **6c1b7822e6** A1 S3 `agg > baseline`
  - For each order, compute the average units of product ordered across its order items (missing values ignored); call this A. Compute the average of these per-order averages across all orders (call it B). Pair each order with B, keeping only rows where B is not missing. Return order id, A, and A − B. Sort by A − B highest first, missing values last, and return the first 10 rows.
- **c94de1efe9** A2 S3 `agg > baseline`
  - Using the steps below, return 5 outputs from step 1 rows: (1) column 1, (2) column 2, (3) column 3, (4) column 4 of step 1, (5) A − B, where A is column 4 of step 1 and B is column 1 of step 2. Step 1 rows are inner joined with step 2 rows whose column 1 is not missing (one row per match; unmatched step 1 rows dropped). Include only combined records where A > B. Sort by A − B descending (as numbers, missing last) and return only the first 10 rows.  Step 1: From each Laboratory record, inner join with each Patient record where Patient ID equals Laboratory patient ID (one combined record per match, unmatched dropped); group by Laboratory patient ID and patient sex; return (1) patient ID, (2) p
- **b3691a7c41** A2 S6 `agg > share > baseline > agg`
  - For each patient ID in the examination records, count the examination records. Let T be the total of these counts. For each patient compute ratio = count ÷ T. Let M be the average of those ratios (missing ignored). Keep only patients whose ratio is greater than M (inner join to M, dropping non-matches), with difference = ratio − M. Return one summary row with three outputs in order: the average of the kept patients' examination counts, the average of their ratios, and the average of their differences.
- **351fb7579b** A2 S6 `agg > share > baseline > agg`
  - Count customers grouped by support representative id (N). Compute the total of N over all groups; for each group, share = N divided by that total. Compute the average share (missing ignored). Keep only groups whose share is greater than the average share, with difference = share minus average share. Over these kept groups, return one row with: the total of N, the average of share, and the average of the difference.
