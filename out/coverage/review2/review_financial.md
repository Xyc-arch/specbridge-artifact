# financial: fresh review of 20 delivered queries

Question: does the query express a coherent calculation over the target data, with its parameters and assumptions explicit?

| id | verdict | has arithmetic (y/n) | cause | reason |
|---|---|---|---|---|
| 1 | no | y | arbitrary | Weight chain over a CASE that tests `disp.type BETWEEN district_id AND account_id` (text between identifiers), including x/x, then sqrt. |
| 2 | no | y | arbitrary | `payments/payments` (x/x), `amount/117024` compared with a date, and three steps of weights, exp and sqrt over those step outputs. |
| 3 | uncertain | n | arbitrary | Joins the first 10 classic cards to dispositions on `disp.type` (a category, not a key), which fans every account's rows out over unrelated cards; the loan-amount filter is fine. |
| 4 | no | y | arbitrary | `(1 - ((1 - CASE on k_symbol text)/0.5 + payments/3937)) / (1 - amount/1000)`: a text flag and money mixed with unexplained constants. |
| 5 | uncertain | n | arbitrary | Lists orders with account frequency and date; the LEFT JOIN to disp is unused and duplicates each order for accounts with two dispositions. |
| 6 | uncertain | n | arbitrary | Lists client, district A5 and 1995 unemployment; the LEFT JOIN to trans is unused and repeats each row once per transaction. |
| 7 | no | y | arbitrary | `amount/duration - payments` (monthly principal minus payment) is meaningful, but outputs scale it by 1.5 and by x - 1.5x/0.2 and filter on that weight chain. |
| 8 | no | y | arbitrary | Orders by `amount/1000*0.2` over `duration / (CASE frequency >= 'POPLATEK PO OBRATU' THEN 1 ELSE 4 END / 10) + payments/payments`: a string-order flag and x/x. |
| 9 | yes | n | - | Lists loans with status and account frequency, ordered by status. |
| 10 | yes | n | - | Distinct (account, order purpose) pairs among orders with an amount. |
| 11 | yes | n | - | Lists clients with gender, district and birth date. |
| 12 | no | y | arbitrary | `(A15/2985) * A15` is crimes squared over an unexplained 2985; the CASE scores test A6 = '37' and A5 = '98' as codes. |
| 13 | no | y | arbitrary | `trans.account / trans.amount` divides the partner account identifier by money (the catalogue wrongly types trans.account as a numeric measure). |
| 14 | no | y | arbitrary | Multiplies cities, unemployment 1995/1996, municipality counts and urban ratio with 0.1 and 0.25 weights, adds order amount x0.1 to average salary, compares a number with a date and a birth date. |
| 15 | uncertain | n | arbitrary | A 10/0 score for disp_id = 47 (one identifier) and its rounded copy, plus a constant column; well defined but without purpose. |
| 16 | no | y | arbitrary | Weight chain over crimes, municipality counts, entrepreneurs, unemployment and salary; `A14 BETWEEN 126 AND 113` is empty; filter compares region with gender. |
| 17 | uncertain | n | arbitrary | Lists dispositions with card type and issue date; RANK over account_id ranks by an identifier. |
| 18 | yes | n | - | Lists orders with purpose and recipient bank, ordered by purpose. |
| 19 | no | y | arbitrary | `(A16*A10)^2 = 33048331264` (crimes times urban ratio, squared, matched exactly) and a CASE score compared with A10. |
| 20 | no | y | arbitrary | `amount*(1-amount)` (USD minus USD squared), its x/x, CASE scores on account_to (an identifier) and bank codes, and `k_symbol IN (trans.type)`. |

## Counts

| | yes | uncertain | no |
|---|---|---|---|
| all 20 | 4 | 5 | 11 |
| with arithmetic (11) | 0 | 0 | 11 |
| without arithmetic (9) | 4 | 5 | 0 |

Causes among uncertain/no (16): arbitrary 16, missing evidence 0, lost in propagation 0.

## Pattern

All 11 queries with arithmetic are incoherent: money multiplied by money, identifiers (account, client, disp ids) and codes used as numbers, x/x, and district attributes chained with unexplained weights; the one meaningful kernel (amount/duration - payments in #7) comes wrapped in a weight chain. The queries without arithmetic are sound lists, but five of them carry an unused fan-out join, a join on a category column, or a rank or score keyed on an identifier, so only 4 of 20 are clean.
