# Wrong alternatives per extra reading on AMBROSIA (`specbridge.comm.transfer.exchange`)

Final test after the truncation rerun; scoring as the final report (identical results merged, shape-tolerant). Wrong = a returned query that does not return the single correct result of an unambiguous question.

| model | arm | unambiguous: queries per question | wrong per question | ambiguous: readings found per question |
|---|---|---|---|---|
| sonnet | plain | 2.00 | 1.13 | 1.42 |
| sonnet | samplek | 2.53 | 1.52 | 1.53 |
| sonnet | dtp | 4.07 | 2.27 | 1.53 |
| sonnet | ours | 1.57 | 0.73 | 1.56 |
| gpt-6-sol | plain | 1.30 | 0.62 | 1.18 |
| gpt-6-sol | samplek | 1.70 | 0.97 | 1.33 |
| gpt-6-sol | dtp | 2.88 | 1.90 | 1.71 |
| gpt-6-sol | ours | 1.22 | 0.48 | 1.49 |

## sonnet: DtP minus ours (60 unambiguous, 90 ambiguous questions)

Per question: wrong alternatives +1.53 [1.25, 1.82]; readings found -0.02 [-0.11, 0.07].

| ambiguity rate | extra readings DtP finds per 100 questions | extra wrong alternatives DtP shows per 100 | wrong alternatives per extra reading [95%] |
|---|---|---|---|
| 10% | -0.2 | 138.0 | undefined: DtP finds no extra readings  |
| 20% | -0.4 | 122.7 | undefined: DtP finds no extra readings  |
| 30% | -0.7 | 107.3 | undefined: DtP finds no extra readings  |
| 50% | -1.1 | 76.7 | undefined: DtP finds no extra readings  |

Break-even ambiguity rate (one wrong alternative per extra reading): none (DtP does not find more readings).

## gpt-6-sol: DtP minus ours (60 unambiguous, 90 ambiguous questions)

Per question: wrong alternatives +1.42 [1.08, 1.77]; readings found +0.22 [0.07, 0.37].

| ambiguity rate | extra readings DtP finds per 100 questions | extra wrong alternatives DtP shows per 100 | wrong alternatives per extra reading [95%] |
|---|---|---|---|
| 10% | 2.2 | 127.5 | 57.4 [31.7, 196.7] (DtP finds no extra reading in 0% of resamples) |
| 20% | 4.4 | 113.3 | 25.5 [14.1, 87.4] (DtP finds no extra reading in 0% of resamples) |
| 30% | 6.7 | 99.2 | 14.9 [8.2, 51.0] (DtP finds no extra reading in 0% of resamples) |
| 50% | 11.1 | 70.8 | 6.4 [3.5, 21.9] (DtP finds no extra reading in 0% of resamples) |

Break-even ambiguity rate (one wrong alternative per extra reading): 86% [78%, 96%] over resamples where DtP finds more readings.

## pooled: DtP minus ours (120 unambiguous, 180 ambiguous questions)

Per question: wrong alternatives +1.48 [1.26, 1.69]; readings found +0.10 [0.01, 0.19].

| ambiguity rate | extra readings DtP finds per 100 questions | extra wrong alternatives DtP shows per 100 | wrong alternatives per extra reading [95%] |
|---|---|---|---|
| 10% | 1.0 | 132.8 | 132.8 [67.9, 765.0] (DtP finds no extra reading in 2% of resamples) |
| 20% | 2.0 | 118.0 | 59.0 [30.2, 340.0] (DtP finds no extra reading in 2% of resamples) |
| 30% | 3.0 | 103.2 | 34.4 [17.6, 198.3] (DtP finds no extra reading in 2% of resamples) |
| 50% | 5.0 | 73.8 | 14.8 [7.5, 85.0] (DtP finds no extra reading in 2% of resamples) |

Break-even ambiguity rate (one wrong alternative per extra reading): 94% [88%, 99%] over resamples where DtP finds more readings.
