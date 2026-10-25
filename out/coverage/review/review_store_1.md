# store_1: semantic coherence review (20 delivered queries)

Question: does the query express a coherent calculation over the target data, with its parameters and assumptions explicit?

| query id | verdict | cause (if not yes) | reason |
|---|---|---|---|
| store_1-1 | uncertain | arbitrary | Plain track listing, but `FIRST_VALUE(bytes) OVER (ORDER BY milliseconds)` repeats the shortest track's size on every row for no stated purpose. |
| store_1-2 | no | arbitrary | A long chain over `milliseconds / 255634`, `10 / milliseconds / 0.25`, composer-keyed CASE scores and `milliseconds * bytes`, with a filter that compares an expression to itself. |
| store_1-3 | yes |  | Billing postal code, state and invoice total ordered by total (with a redundant CAST copy of total); coherent. |
| store_1-4 | no | arbitrary | `sqrt(ms + 255634) * sqrt(ms + 255634) * ms`, `bytes / (...)`, and `media_type_id IN (ratio, composer)` use an identifier and a text column as quantities. |
| store_1-5 | no | arbitrary | `AVG((1 - bytes) * CASE ... END)`, where every CASE branch is 1, and the step output is then joined back through playlists and genres. |
| store_1-6 | no | arbitrary | `total / (1 - total/3.96)`, customers joined to employees on phone, and a filter setting that ratio equal to `invoice_date`. |
| store_1-7 | no | arbitrary | `bytes + (bytes/8107896)/0.1` adds bytes to a scaled ratio of bytes, then `1 - (1 - x/0.25)` and CASE scores on lexical media-type comparisons. |
| store_1-8 | no | arbitrary | The CASE on `invoices.id` returns 0 in every branch, so `power(0 * (0.1/total), 1.5)` is constant, and the invoice id is cast to REAL as a quantity. |
| store_1-9 | no | arbitrary | `bytes / sqrt(bytes)` is a degenerate way of writing sqrt(bytes), with no purpose. |
| store_1-10 | no | arbitrary | Step outputs are divided by themselves (`o1 / o1`), `1 - total` is taken, and `log(10, 1 - (total-3.96)/0.5/0.1)` appears in a long chain of constant weights. |
| store_1-11 | no | arbitrary | CASE scores on `fax > '+1 (604) ...'` and `first_name > 'Tim'` multiply `total*5`, and a term divides by itself (x / x). |
| store_1-12 | yes |  | Customer last name, fax and invoice billing city and address; a plain listing. |
| store_1-13 | no | arbitrary | `abs(c)/abs(c)` (x / x), `x - x`, `CAST(playlists.name AS REAL) = 'Music Videos'`, and a filter `a > a AND a = a`. |
| store_1-14 | no | arbitrary | `AVG(invoices.id BETWEEN 207 AND 310)` per invoice id (0 or 1), then `log(10, sqrt(...))` over chains of 0.75 / 5 / 1.5 on that flag. |
| store_1-15 | no | arbitrary | Arithmetic on constants only: `5 / (1.5 / (log(round(2,2) * ...)) ...)` over the artists table. |
| store_1-16 | no | arbitrary | `(birth_date - hire_date)` on dates cast to REAL is multiplied by itself over itself (x * x/x), and customers are joined to employees on phone. |
| store_1-17 | uncertain | arbitrary | Invoice listing is fine, but the CASE assigns unexplained scores (3, 10, 5) to customer ids 49 and 31 and to one surname, and `1 AS o3` is a constant column. |
| store_1-18 | no | arbitrary | `(ms/bytes) / ((ms/bytes)/0.1)` is the constant 10, and `1 - coalesce(ms, 1000000)` and `(1 - ms)/3` appear alongside a CASE on `genre_id < 3`. |
| store_1-19 | no | arbitrary | `-7850000 - (milliseconds - bytes)` subtracts bytes from ms; genre ids are turned into CASE scores, and a playlist-name CASE is divided by itself. |
| store_1-20 | no | arbitrary | The filter `total*2 - (total*0.75 - (total/3.96 + 1)) > 6.95` is an arbitrary weighting, and `COUNT / tracks.bytes` divides a count of invoice lines by a file size. |

## Totals

- yes: 2 (3, 12)
- uncertain: 2 (1, 17)
- no: 16 (2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 19, 20)
- causes (18 non-yes): arbitrary 18, missing evidence 0, lost in propagation 0

## Dominant pattern

Almost every delivered query in store_1 is a deep random expression tree. It uses degenerate parts (x/x, x - x, bytes/sqrt(bytes), CASEs whose branches are all equal), long chains of constant weights, and `1 - x` wrappers on quantities that are not fractions (`1 - bytes`, `1 - total`, `1 - milliseconds`). It also treats ids, dates, fax numbers and names as quantities or as lexical thresholds. The catalogue's one relation (bytes per millisecond as a rate) is the only meaningful combination, and even that is immediately divided by itself (store_1-18), so the defect is not missing evidence. The generator composes operations that are decidably meaningless from the AST, including the non-key join `customers.phone = employees.phone` (4 of 20).
