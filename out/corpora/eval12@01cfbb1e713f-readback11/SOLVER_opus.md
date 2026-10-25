# Solver evaluation: `eval12@01cfbb1e713f-readback11`, solver opus

The delivered corpus (11 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 66 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 11 | 2/11 (18%) | 11 | 10 |
| explicit instructions | 11 | 11/11 (100%) | 11 | 11 |

## Paired, same 11 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 2 | 9 |
| explicit wrong | 0 | 0 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 4 | 2/4 (50%) | 4/4 (100%) |
| S4 | 3 | 0/3 (0%) | 3/3 (100%) |
| S5 | 2 | 0/2 (0%) | 2/2 (100%) |
| S6 | 2 | 0/2 (0%) | 2/2 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 6 | 2/6 (33%) | 6/6 (100%) |
| A2 | 5 | 0/5 (0%) | 5/5 (100%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 2 | 0/2 (0%) | 2/2 (100%) |
| agg > agg > baseline > agg | 1 | 0/1 (0%) | 1/1 (100%) |
| agg > baseline | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline > agg | 1 | 0/1 (0%) | 1/1 (100%) |
| agg > share | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > share > baseline | 1 | 0/1 (0%) | 1/1 (100%) |
| agg > share > baseline > agg | 2 | 0/2 (0%) | 2/2 (100%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 9 | 2/9 (22%) | 9/9 (100%) |
| revised | 2 | 0/2 (0%) | 2/2 (100%) |

## Wrong answers to read (a random 6)

- **b9ceda40df** A1 S3 `agg > share`
  - For each payment purpose code of standing orders, compute the average standing order amount (ignoring missing values) and the number of orders. Divide that number by the total number of orders over all payment purpose codes. Return the payment purpose code, the average amount, the order count, and the ratio.
- **6ec8137fd3** A2 S4 `agg > agg > baseline`
  - Join each invoice line item to its order item (matching order item id), then to its order (matching order id), then to its customer (matching customer id), dropping lines with no match at any step. Group by order item id and customer town or city. For each group, compute the average product price per unit and the average of A ÷ B. A is line product cost (Invoice_Line_Items.derived_product_cost). B is line total cost including VAT. Then group those rows by town or city. For each town or city, compute the average of the group average prices and the average of the group A ÷ B averages. Call the average price per town P. Compute the average of P over all towns. Call it Q. Pair each town row with
- **c759056a31** A1 S4 `agg > agg > baseline`
  - Join each constructor standings record to its race (by race identifier), then to that race's circuit (by circuit identifier), dropping records with no match at either join, with one row per match. Group by constructorStandings.raceId (keep this raw column name) and circuit country. For each group, compute the average season-to-date constructor championship points and the average season-to-date constructor race wins, ignoring missing values. Then group those rows by circuit country. For each country, compute the average of the per-group average points and the average of the per-group average wins, ignoring missing values. Let A be a country's average of the average points. Let B be the averag
- **227771660b** A2 S5 `agg > agg > baseline > agg`
  - Join each lab record to the patient with the same patient ID (drop lab records with no matching patient). Group by patient ID and patient sex and compute (3) the average of serum albumin minus total serum protein, and (4) the average of activated partial thromboplastin time minus prothrombin time (missing values ignored). Then group those rows by sex and compute for each sex the average of (3) and the average of (4). Let M be the average of the per-sex (3)-averages over all sexes (missing ignored). Keep only sexes whose per-sex (3)-average is greater than M. For each kept sex, the difference is its (3)-average minus M. Return one summary row with three outputs in order: the average over the 
- **5f1a57a3d8** A1 S6 `agg > share > baseline > agg`
  - For each order reference in risk and margin, count the risk and margin records. Let T be the total of these counts. For each order reference compute R = count ÷ T (inner join to T where T is not missing). Let Y be the average of R over all order references. Inner join to Y (where Y is not missing), keep only the order references with R greater than Y, and compute D = R − Y. Return one summary row with (1) the total of the counts over those kept rows, (2) the average of R, (3) the average of D.
- **e2ae5e3b8f** A2 S4 `agg > baseline > agg`
  - Join each appearances record to the player whose unique player identifier equals the appearances player_id (compared as text, character by character); drop records with no matching player, one row per match. Group by appearances player_id and death country. For each group compute S, the sum of (games at first base − games in center field) over the group's records, ignoring missing values; S is missing (not 0) if the group has no non-missing values. Compute T, the average of S over all these groups, ignoring groups where S is missing; T is missing if no group has a non-missing S. Pair each group with T, keeping only when T is not missing (groups with no match are dropped, one row per match), 
