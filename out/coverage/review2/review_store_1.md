# store_1: fresh review of 20 delivered queries

Question: does this query express a coherent calculation over the target data, with its parameters and assumptions explicit?

| id | verdict | has arithmetic (y/n) | cause | reason |
|---|---|---|---|---|
| 1 | no | y | arbitrary | `(total/3.96)/(total/3.96)` (x/x), `CAST(invoice_date AS REAL)` added to a log, and a second step built only from constants (round(2,2), 2.5). |
| 2 | no | y | arbitrary | `composer IN (SELECT total ...)` compares a name with invoice amounts; `bytes/bytes` (x/x). |
| 3 | no | y | arbitrary | `genre_id` used as a quantity (max, exp), contradictory filters (name IN (...) AND name = another), `ms - ms`, `(1-bytes)/((1-bytes)*2)`. |
| 4 | no | n | arbitrary | Joins customers to employees on `phone` equality, which has no meaning (a customer's phone is not an employee's); only casts of total follow. |
| 5 | no | y | arbitrary | `CAST(first_name AS REAL) > 'Eduardo'` and `CAST(first_name AS INTEGER) < 'Ladislav'`: text cast to numbers and compared with names; then chains on the resulting score. |
| 6 | yes | n | - | Distinct media type, album and file size of tracks that appear on at least one invoice line. |
| 7 | no | y | arbitrary | `total * CAST(total AS INTEGER) * (total/3.96)` cubes a currency amount; fax filter `> X AND = Y` is redundant. |
| 8 | no | y | arbitrary | Constants only, including division by `CAST(0 AS REAL)/2` (zero); a CASE compares a constant with `state`. |
| 9 | yes | n | - | Albums with artist id and album id, ordered by title (the constant column `1` is harmless). |
| 10 | no | y | arbitrary | Indicator `playlist_id = 13` put through x/x and `1 - x*(x/x)`; a code comparison as the only input. |
| 11 | no | y | arbitrary | `1 - (bytes/8107896 + CASE(genre_id thresholds)*3 ...)`, x/x ratios, and relative size x (ms*3); ids used as quantities. |
| 12 | no | y | arbitrary | Constants only (power(1.5,2)/10 ... divided by itself) with CASEs on `genres.id` thresholds. |
| 13 | yes | y | - | Invoice lines with their track's media type, unit price, file size and log10 of file size; log of size is a clear order-of-magnitude transform. |
| 14 | no | y | arbitrary | `(ms*2*(ms/255634)) / CAST(same)`: x/x, a column that is 1 for every row. |
| 15 | no | y | arbitrary | `log10(bytes) - birth_date` subtracts a date from a log size; FILTER compares it with an address; customers-employees join on phone. |
| 16 | no | y | arbitrary | `x - x` on rounded totals, `(total+total)/0.75`, `billing_country = invoice_date`, and `o1/abs(o1)`; incoherent. |
| 17 | no | y | arbitrary | First step is constants only compared with `first_name`; later steps use `o0/o0` (x/x). |
| 18 | no | y | arbitrary | Birth-date indicator divided by `total*5*1.5`; customers-employees joined on phone; address and fax string-order filters. |
| 19 | no | y | arbitrary | `CASE ... THEN 1 ... ELSE 1` constant, and a chain of bytes/ms x (ms/255634) x (1 - ms/255634) x (1 - 0.2/ms) x (255634 - ms). |
| 20 | no | y | arbitrary | `CASE ... THEN 1 ELSE 1` constants, `1 - CAST(bytes/8110000 AS INTEGER)`, `ms/bytes` compared with bytes, and IN over FIRST_VALUE of a ratio. |

## Counts

| | yes | uncertain | no |
|---|---|---|---|
| all 20 | 3 | 0 | 17 |
| with arithmetic (17) | 1 | 0 | 16 |
| without arithmetic (3) | 2 | 0 | 1 |

Causes (uncertain + no = 17): arbitrary 17; missing evidence 0; lost in propagation 0.

## Pattern

Sixteen of seventeen queries with arithmetic are incoherent in ways the SQL alone shows (x/x, constants-only chains, text cast to numbers, dates subtracted from log sizes, ids as quantities); the only coherent one applies a single log to file size. The non-arithmetic defects are joins with no meaning (customers to employees on phone), so the failures come from what the generator composes, not from missing catalogue evidence.
