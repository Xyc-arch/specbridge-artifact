# financial: review of 20 delivered queries

Question per query: does it express a coherent calculation over the target data, with its parameters and assumptions explicit?

| query id | verdict | cause (if not yes) | reason |
|---|---|---|---|
| financial-1 | no | arbitrary | `payments*3 * amount*0.2 * 0.25` multiplies the monthly payment by the loan amount (USD squared) with unexplained weights. |
| financial-2 | uncertain | arbitrary | `CAST(account_id AS REAL)` outputs an identifier as a number for no stated purpose; the rest is a plain lookup. |
| financial-3 | yes | | Lists account creation date, recipient account and payment purpose of orders, sorted by recipient account. |
| financial-4 | no | arbitrary | The WHERE is arithmetic on constants only (`round(CAST(0 AS REAL),3)/0.75/0.2 / 0 ...`) compared to a birth date, and `sqrt(birth_date)` treats a date as a number. |
| financial-5 | no | arbitrary | `A15 * (order.amount / A15)` cancels, `trans.amount*0.25 + ...` adds unrelated amounts, and `trans.account * balance` multiplies a partner account ID by money. |
| financial-6 | uncertain | arbitrary | Plain lookup of client, A5 and unemployment, but the unused `LEFT JOIN trans` repeats each row once per transaction for no reason. |
| financial-7 | no | arbitrary | CASE codes built from `account_id < 1183 AND account_id > 3553` (impossible) and district_id thresholds, then weighted and compared to a date. |
| financial-8 | no | arbitrary | `A12/100 * (A15*3 + ...) * ((100 - A10) + A11/1000)*0.25 + A8/2` mixes unemployment, crimes, urban share, salary and municipality counts. |
| financial-9 | no | arbitrary | `log(10, CAST(birth_date AS REAL))` takes the log of a date read as a number. |
| financial-10 | no | arbitrary | `balance / -692 * 5 + trans.account / 46100000 + order.amount` adds a partner account ID to money, and `x / x` appears repeatedly. |
| financial-11 | no | arbitrary | `AVG(duration) OVER (PARTITION BY duration)` just returns duration, and `x = x * 0.5` is only true when x is 0. |
| financial-12 | uncertain | lost in propagation | `CAST(account.date AS REAL)` turns the opening date into a bare number (effectively the year) with no stated purpose. |
| financial-13 | no | arbitrary | `district_id BETWEEN 60 AND 38` is an empty range, and `A6 < '15'` compares a count stored as text by string order, producing arbitrary codes. |
| financial-14 | no | arbitrary | `amount/1000 + duration*0.5` adds thousands of USD to months, and the o4 chain adds `order.amount*3 + 7790`. |
| financial-15 | uncertain | arbitrary | `CAST(account_to AS REAL)` (twice) and `coalesce(order_id, 0)` apply operations to identifiers that have no purpose. |
| financial-16 | no | arbitrary | `A15/2985 * order.amount + (A11 + 8814)*0.2) * (A10 + A13)` mixes crimes, money, salary and percentages with arbitrary offsets. |
| financial-17 | no | arbitrary | The output is `x / CAST(x AS REAL)` (always 1) of a CASE code built from `disp.type > 'OWNER'` and client_id thresholds. |
| financial-18 | no | arbitrary | `CASE WHEN A10 = 55.3 THEN 1 ELSE 1 END` is constant, and the rest is weight chains on COUNT(*) with `x - x` and `+ 0`. |
| financial-19 | no | arbitrary | `A13/3.6 * A11 * A9` multiplies unemployment, salary and city count, `CAST(A3 AS REAL)` makes a region name a number, and `(A12/100 + A10*2)/(0 - A10)` has no meaning. |
| financial-20 | no | arbitrary | CASE flag `*100/0.2 + 0` times `1 - x/x`, plus `round(y) - round(y)`: degenerate parts all the way down. |

## Totals

- yes: 1
- uncertain: 4
- no: 15
- Causes (19 not-yes): arbitrary 18, lost in propagation 1, missing evidence 0.

## Dominant pattern

Almost every query that computes something is incoherent. District columns with unrelated units (crimes, salary, percentages, municipality counts), identifiers (account_id, trans.account) and dates are combined with made-up weights and offsets, and degenerate parts (`x/x`, `x - x`, `+ 0`, empty BETWEEN) show up everywhere. The catalogue already marks these columns as KEY/DATE or with different units, so the fault is how the queries are built, not missing evidence. The only coherent queries are plain lookups with no arithmetic.
