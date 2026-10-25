# Rewriting vs editing a request (`specbridge.comm.transfer.rewrite`; gate: out/rewrite/GATE.md)

Accuracy per reading: (a) original specific request, (b) solver's DtP-style interpretation, (c) open request + the reading description. Same plain SQL prompt.

| model | readings | (a) | (b) | (c) | (c) - (a) | (b) - (a) | McNemar (b) vs (a): lost / gained, p | (c) vs (a): lost / gained, p | gate |
|---|---|---|---|---|---|---|---|---|---|
| haiku | 91 | 81.3 | 73.6 | 89.0 | +7.7 | -7.7 | 18 / 11, 0.26 | 4 / 11, 0.12 | fail |
| sonnet | 95 | 97.9 | 91.6 | 98.9 | +1.1 | -6.3 | 8 / 2, 0.11 | 1 / 2, 1 | fail |
| gpt-6-sol | 87 | 86.2 | 88.5 | 82.8 | -3.4 | +2.3 | 2 / 4, 0.69 | 4 / 1, 0.38 | fail |
| gpt-6-luna | 90 | 74.4 | 60.0 | 70.0 | -4.4 | -14.4 | 19 / 6, 0.015 | 12 / 8, 0.5 | fail |
| pooled | 363 | 85.1 | 78.5 | 85.4 | +0.3 | -6.6 | 47 / 23, 0.0056 | 21 / 22, 1 | fail |

Secondary tests (GATE.md amendment 22:25), exact McNemar on paired readings:

| model | (c) - (b) | lost / gained, p | readings with (d) | (d) | (c) - (d) | lost / gained, p |
|---|---|---|---|---|---|---|
| haiku | +15.4 | 20 / 6, 0.0094 | 91 | 62.6 | +26.4 | 27 / 3, 8.4e-06 |
| sonnet | +7.4 | 7 / 0, 0.016 | 95 | 94.7 | +4.2 | 4 / 0, 0.12 |
| gpt-6-sol | -5.7 | 2 / 7, 0.18 | 87 | 74.7 | +8.0 | 10 / 3, 0.092 |
| gpt-6-luna | +10.0 | 13 / 4, 0.049 | 90 | 62.2 | +7.8 | 14 / 7, 0.19 |
| pooled | +6.9 | 42 / 17, 0.0015 | 363 | 73.8 | +11.6 | 55 / 13, 2.7e-07 |

What (b) lost, on readings right under (a) and wrong under (b) (47; Opus, V of reference vs V of answer): output columns 17 (36%), formula 8 (17%), join 7 (15%), grouping 6 (13%), filter 4 (9%), the choice 3 (6%), other 2 (4%)

Request length (characters, mean): (a) 540, (b) 383, (c) 529. (b) answers that do not execute: 23 of 363.

## Filter sets (reported apart; 93 readings)

| model | readings | (a) | (b) | (c) | (c) - (a) | (b) - (a) | McNemar (b) vs (a): lost / gained, p | (c) vs (a): lost / gained, p | gate |
|---|---|---|---|---|---|---|---|---|---|
| pooled | 93 | 89.2 | 88.2 | 93.5 | +4.3 | -1.1 | 4 / 3, 1 | 0 / 4, 0.12 | fail |

| model | (c) - (b) | lost / gained, p | readings with (d) | (d) | (c) - (d) | lost / gained, p |
|---|---|---|---|---|---|---|
| pooled | +5.4 | 6 / 1, 0.12 | 93 | 91.4 | +2.2 | 3 / 1, 0.62 |

## Two (b) rewrites that lost the answer

- haiku, 00d65781cc: (b) "Count the invoice line items per product color, with products that have no color (NULL) as their own group, then compute each color's share of the total count, keep the colors whose count is above the average count per color, and output one row per kept color with its average count, average share, a" -- lost: The answer returns one row per kept color instead of collapsing them into a single row of averages for amount, share and excess.
- haiku, 11c73410e6: (b) "For each equipment status, average `signals.pulsepersec` over all signals joined to telescopes in that status (NULLs excluded, each signal weighted equally); keep statuses whose average exceeds the mean of all status averages and report each one's excess; then keep those above the mean of the kept a" -- lost: The second column averages the first-stage excess over all statuses that pass the first cut, not just the statuses that remain after the second cut.
