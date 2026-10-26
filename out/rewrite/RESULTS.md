# Rewriting vs editing a request (`specbridge.comm.transfer.rewrite`; gate: out/rewrite/GATE.md)

Accuracy per reading: (a) original specific request, (b) solver's DtP-style interpretation, (c) open request + the reading description. Same plain SQL prompt.

| model | readings | (a) | (b) | (c) | (c) - (a) | (b) - (a) | McNemar (b) vs (a): lost / gained, p | (c) vs (a): lost / gained, p | gate |
|---|---|---|---|---|---|---|---|---|---|
| haiku | 91 | 69.2 | 48.4 | 70.3 | +1.1 | -20.9 | 29 / 10, 0.0034 | 10 / 11, 1 | PASS |
| sonnet | 95 | 97.9 | 91.6 | 98.9 | +1.1 | -6.3 | 8 / 2, 0.11 | 1 / 2, 1 | fail |
| gpt-6-sol | 87 | 86.2 | 88.5 | 82.8 | -3.4 | +2.3 | 2 / 4, 0.69 | 4 / 1, 0.38 | fail |
| gpt-6-luna | 90 | 74.4 | 60.0 | 70.0 | -4.4 | -14.4 | 19 / 6, 0.015 | 12 / 8, 0.5 | fail |
| pooled | 363 | 82.1 | 72.2 | 80.7 | -1.4 | -9.9 | 58 / 22, 7e-05 | 27 / 22, 0.57 | fail |

Secondary tests (GATE.md amendment 22:25), exact McNemar on paired readings:

| model | (c) - (b) | lost / gained, p | readings with (d) | (d) | (c) - (d) | lost / gained, p |
|---|---|---|---|---|---|---|
| haiku | +22.0 | 30 / 10, 0.0022 | 91 | 48.4 | +22.0 | 25 / 5, 0.00032 |
| sonnet | +7.4 | 7 / 0, 0.016 | 95 | 94.7 | +4.2 | 4 / 0, 0.12 |
| gpt-6-sol | -5.7 | 2 / 7, 0.18 | 87 | 74.7 | +8.0 | 10 / 3, 0.092 |
| gpt-6-luna | +10.0 | 13 / 4, 0.049 | 90 | 62.2 | +7.8 | 14 / 7, 0.19 |
| pooled | +8.5 | 52 / 21, 0.00037 | 363 | 70.2 | +10.5 | 53 / 15, 4.1e-06 |

What (b) lost, on readings right under (a) and wrong under (b) (58; Opus, V of reference vs V of answer): formula 20 (34%), output columns 13 (22%), join 8 (14%), the choice 7 (12%), grouping 4 (7%), filter 4 (7%), other 2 (3%)

Request length (characters, mean): (a) 540, (b) 376, (c) 529. (b) answers that do not execute: 30 of 363.

## Filter sets (reported apart; 93 readings)

| model | readings | (a) | (b) | (c) | (c) - (a) | (b) - (a) | McNemar (b) vs (a): lost / gained, p | (c) vs (a): lost / gained, p | gate |
|---|---|---|---|---|---|---|---|---|---|
| pooled | 93 | 88.2 | 83.9 | 89.2 | +1.1 | -4.3 | 5 / 1, 0.22 | 2 / 3, 1 | fail |

| model | (c) - (b) | lost / gained, p | readings with (d) | (d) | (c) - (d) | lost / gained, p |
|---|---|---|---|---|---|---|
| pooled | +5.4 | 7 / 2, 0.18 | 93 | 86.0 | +3.2 | 6 / 3, 0.51 |

## Two (b) rewrites that lost the answer

- haiku, 00d65781cc: (b) "Count invoice line items per product color (with NULL as a separate group), compute each color's share of total line item count, identify colors exceeding the average line item count, and output one row with their average count, average share, and average excess above the per-color average." -- lost: The share is computed as integer ÷ integer (line_item_count / total_count) with no cast, so integer division truncates every share to 0 instead of giving the true fraction.
- haiku, 1490d5931d: (b) "For each distinct batting hand (including blank/missing values), count the number of fielding records (where each record is unique by player_id, year, stint, and position), calculate the percentage of total records for that hand, calculate the average count across all hands, and display only hands w" -- lost: The share is multiplied by 100 and rounded to a percentage instead of being the plain unrounded fraction count ÷ total.
