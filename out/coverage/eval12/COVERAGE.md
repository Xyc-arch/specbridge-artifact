# Construction coverage and control (`eval12`, model-free)

Generated, mechanically checked programs (grammar, data checks, measured depth, receipts). No model call; none of these is a reviewed benchmark task.

## Stage 1: the pool (about 100 programs per database, uniform over its supported cells)

| database | supported cells | requested | delivered | short cells | built-for = measured | recomputed | trivial | distinct SQL | constructions | base quantities | tables | operations | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alien | 25 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 75 | 10 | 3 | baseline 70, aggregate only 24, share 8, row ranking 2, rank 2 | 7 |
| archeology | 27 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 80 | 63 | 13 | baseline 63, aggregate only 23, share 6, diff 5, row ranking 4, ratio 3, rank 2 | 12 |
| baseball_1 | 25 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 80 | 74 | 17 | baseline 69, aggregate only 21, share 17, rank 3, row ranking 2, diff 2, ratio 1 | 116 |
| chinook_1 | 15 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 74 | 5 | 8 | baseline 62, aggregate only 32, share 28, rank 3, row ranking 1 | 2 |
| crypto | 25 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 78 | 8 | 5 | baseline 69, aggregate only 25, share 12, row ranking 2, rank 1 | 10 |
| customers_and_invoices | 25 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 84 | 20 | 9 | baseline 70, aggregate only 26, share 15, row ranking 1, diff 1, ratio 1, rank 1 | 3 |
| financial | 18 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 66 | 4 | 6 | baseline 63, share 33, aggregate only 27, rank 2, row ranking 1 | 249 |
| formula_1 | 11 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 71 | 10 | 9 | baseline 66, share 32, aggregate only 23, rank 3, row ranking 2 | 10 |
| insider | 27 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 76 | 60 | 5 | baseline 61, aggregate only 25, share 9, diff 5, row ranking 4, ratio 3, rank 1 | 8 |
| sakila_1 | 21 | 100 | 98 | 1 | 98/98 | 0 | 0 | 98 | 51 | 10 | 10 | baseline 60, aggregate only 31, share 24, rank 5, row ranking 1 | 6 |
| student_club | 25 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 76 | 8 | 7 | baseline 64, share 29, aggregate only 24, rank 3, row ranking 1, diff 1 | 3 |
| thrombosis_prediction | 27 | 100 | 100 | 0 | 100/100 | 0 | 0 | 100 | 57 | 90 | 3 | baseline 59, aggregate only 22, share 10, ratio 8, row ranking 3, rank 2, diff 2 | 12 |

Total: 1198 of 1200 delivered; built-for = measured on 1198 of 1198.

### Shortfalls in the pool (cell: requested -> delivered, reason)

- sakila_1 3,6: 4 -> 2; cell exhausted: all 2 distinct programs of the cell were drawn

## Stage 2A: does a request move the delivered workload? (48 per run, A1-2; mean over seeds 1-3)

| database | request | delivered | share at S3-4 | share at S5-7 | mean S | distinct constructions |
|---|---|---|---|---|---|---|
| alien | shallow | 48.0 | 100% | 0% | 3.50 | 32.3 |
| alien | balanced | 48.0 | 42% | 58% | 4.94 | 41.0 |
| alien | deep | 48.0 | 0% | 100% | 6.00 | 41.7 |
| archeology | shallow | 48.0 | 100% | 0% | 3.50 | 31.0 |
| archeology | balanced | 48.0 | 42% | 58% | 4.94 | 41.7 |
| archeology | deep | 48.0 | 0% | 100% | 6.00 | 41.0 |
| baseball_1 | shallow | 48.0 | 100% | 0% | 3.50 | 29.7 |
| baseball_1 | balanced | 48.0 | 42% | 58% | 4.94 | 40.3 |
| baseball_1 | deep | 48.0 | 0% | 100% | 6.00 | 39.7 |
| chinook_1 | shallow | 48.0 | 100% | 0% | 3.50 | 25.7 |
| chinook_1 | balanced | 48.0 | 42% | 58% | 4.94 | 40.0 |
| chinook_1 | deep | 48.0 | 0% | 100% | 6.00 | 40.3 |
| crypto | shallow | 48.0 | 100% | 0% | 3.50 | 33.0 |
| crypto | balanced | 48.0 | 42% | 58% | 4.94 | 43.0 |
| crypto | deep | 48.0 | 0% | 100% | 6.00 | 40.7 |
| customers_and_invoices | shallow | 48.0 | 100% | 0% | 3.50 | 34.7 |
| customers_and_invoices | balanced | 48.0 | 42% | 58% | 4.94 | 42.7 |
| customers_and_invoices | deep | 48.0 | 0% | 100% | 6.00 | 39.3 |
| financial | shallow | 48.0 | 100% | 0% | 3.50 | 25.7 |
| financial | balanced | 48.0 | 42% | 58% | 4.94 | 38.0 |
| financial | deep | 48.0 | 0% | 100% | 6.00 | 34.7 |
| formula_1 | shallow | 24.0 | 100% | 0% | 3.50 | 19.3 |
| formula_1 | balanced | 38.0 | 26% | 74% | 5.32 | 34.3 |
| formula_1 | deep | 48.0 | 0% | 100% | 6.00 | 37.7 |
| insider | shallow | 48.0 | 100% | 0% | 3.50 | 27.7 |
| insider | balanced | 48.0 | 42% | 58% | 4.94 | 39.3 |
| insider | deep | 48.0 | 0% | 100% | 6.00 | 35.7 |
| sakila_1 | shallow | 48.0 | 100% | 0% | 3.50 | 21.0 |
| sakila_1 | balanced | 48.0 | 42% | 58% | 4.94 | 37.7 |
| sakila_1 | deep | 48.0 | 0% | 100% | 6.00 | 37.3 |
| student_club | shallow | 48.0 | 100% | 0% | 3.50 | 32.3 |
| student_club | balanced | 48.0 | 42% | 58% | 4.94 | 41.0 |
| student_club | deep | 48.0 | 0% | 100% | 6.00 | 41.3 |
| thrombosis_prediction | shallow | 48.0 | 100% | 0% | 3.50 | 18.3 |
| thrombosis_prediction | balanced | 48.0 | 42% | 58% | 4.94 | 30.7 |
| thrombosis_prediction | deep | 48.0 | 0% | 100% | 6.00 | 22.3 |

## Stage 2A: does an operation preference move the mix? (48 per run, S3-7, A1-2, seed 1; share of programs using the operation)

| database | rank (w=1) | rank (w=3) | rank (w=10) | share (w=1) | share (w=10) | baseline (w=1) | baseline (w=0.1) |
|---|---|---|---|---|---|---|---|
| alien | 0% of 48 | 0% of 48 | 2% of 48 | 23% of 48 | 31% of 48 | 92% of 48 | 88% of 48 |
| archeology | 0% of 48 | 2% of 48 | 2% of 48 | 31% of 48 | 38% of 48 | 96% of 48 | 90% of 48 |
| baseball_1 | 0% of 48 | 0% of 48 | 0% of 48 | 38% of 48 | 35% of 48 | 92% of 48 | 88% of 48 |
| chinook_1 | 2% of 48 | 2% of 48 | 2% of 48 | 42% of 48 | 54% of 48 | 92% of 48 | 90% of 48 |
| crypto | 0% of 48 | 2% of 48 | 2% of 48 | 29% of 48 | 48% of 48 | 94% of 48 | 88% of 48 |
| customers_and_invoices | 2% of 48 | 2% of 48 | 0% of 48 | 40% of 48 | 62% of 48 | 94% of 48 | 79% of 48 |
| financial | 0% of 48 | 4% of 48 | 4% of 48 | 48% of 48 | 65% of 48 | 94% of 48 | 83% of 48 |
| formula_1 | 0% of 38 | 0% of 38 | 3% of 38 | 37% of 38 | 53% of 38 | 95% of 38 | 89% of 38 |
| insider | 0% of 48 | 0% of 48 | 0% of 48 | 17% of 48 | 27% of 48 | 96% of 48 | 96% of 48 |
| sakila_1 | 0% of 48 | 0% of 48 | 2% of 48 | 42% of 48 | 62% of 48 | 96% of 48 | 90% of 48 |
| student_club | 0% of 48 | 0% of 48 | 0% of 48 | 46% of 48 | 60% of 48 | 92% of 48 | 83% of 48 |
| thrombosis_prediction | 0% of 48 | 0% of 48 | 0% of 48 | 17% of 48 | 12% of 48 | 92% of 48 | 92% of 48 |

## Stage 2A: required operations (48 requested per run, S3-7, A1-2, seed 1; `require` in the request)

Every delivered program must use the required operations; a cell that no route can build with them is reported, not filled.

| database | required | delivered | all use them | built-for = measured | cells not constructible with them |
|---|---|---|---|---|---|
| alien | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| alien | share | 48 | 48 | 48 | none |
| alien | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| archeology | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| archeology | share | 48 | 48 | 48 | none |
| archeology | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| baseball_1 | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| baseball_1 | share | 48 | 48 | 48 | none |
| baseball_1 | rank+share | 10 | 10 | 10 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,6, 2,7 |
| chinook_1 | rank | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| chinook_1 | share | 38 | 38 | 38 | 2,3, 2,4 |
| chinook_1 | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| crypto | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| crypto | share | 48 | 48 | 48 | none |
| crypto | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| customers_and_invoices | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| customers_and_invoices | share | 48 | 48 | 48 | none |
| customers_and_invoices | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| financial | rank | 15 | 15 | 15 | 1,4, 1,6, 1,7, 2,3, 2,4, 2,6, 2,7 |
| financial | share | 48 | 48 | 48 | none |
| financial | rank+share | 10 | 10 | 10 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,6, 2,7 |
| formula_1 | rank | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,5, 2,6, 2,7 |
| formula_1 | share | 38 | 38 | 38 | none |
| formula_1 | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,5, 2,6, 2,7 |
| insider | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| insider | share | 48 | 48 | 48 | none |
| insider | rank+share | 4 | 4 | 4 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| sakila_1 | rank | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| sakila_1 | share | 40 | 40 | 40 | 2,4 |
| sakila_1 | rank+share | 5 | 5 | 5 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
| student_club | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| student_club | share | 48 | 48 | 48 | none |
| student_club | rank+share | 10 | 10 | 10 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,6, 2,7 |
| thrombosis_prediction | rank | 20 | 20 | 20 | 1,4, 1,6, 1,7, 2,4, 2,6, 2,7 |
| thrombosis_prediction | share | 48 | 48 | 48 | none |
| thrombosis_prediction | rank+share | 4 | 4 | 4 | 1,3, 1,4, 1,6, 1,7, 2,3, 2,4, 2,5, 2,6, 2,7 |
