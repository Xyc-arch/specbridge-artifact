# Solver evaluation: `rb2`, solver opus

The delivered corpus (11 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 13 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 11 | 10/11 (91%) | 11 | 11 |

## By step depth

| step depth | tasks | natural |
|---|---|---|
| S3 | 4 | 4/4 (100%) |
| S4 | 3 | 2/3 (67%) |
| S5 | 2 | 2/2 (100%) |
| S6 | 2 | 2/2 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural |
|---|---|---|
| A1 | 6 | 6/6 (100%) |
| A2 | 5 | 4/5 (80%) |

## By shape

| shape | tasks | natural |
|---|---|---|
| agg > agg > baseline | 2 | 1/2 (50%) |
| agg > agg > baseline > agg | 1 | 1/1 (100%) |
| agg > baseline | 2 | 2/2 (100%) |
| agg > baseline > agg | 1 | 1/1 (100%) |
| agg > share | 2 | 2/2 (100%) |
| agg > share > baseline | 1 | 1/1 (100%) |
| agg > share > baseline > agg | 2 | 2/2 (100%) |

## By writer status

| writer status | tasks | natural |
|---|---|---|
| passed | 9 | 8/9 (89%) |
| revised | 2 | 2/2 (100%) |

## Wrong answers to read (a random 6)

- **6ec8137fd3** A2 S4 `agg > agg > baseline`
  - Join each invoice line item to its order item (order item id equal), then to its order (order id equal), then to its customer (customer id equal). Each join gives one row per match and drops lines with no match. Group by order item id and customer town or city. For each group, compute the average product price per unit and the average of `Invoice_Line_Items.derived_product_cost` ÷ line total cost including VAT. Missing values are ignored in both averages (missing when there are none). Then group those group rows by town or city. For each town, compute P, the average of the group average prices, and R, the average of the group cost ratio averages. Missing values are ignored (missing when ther
