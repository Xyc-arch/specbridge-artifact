# Gate + wide search + execute vs every baseline (saved arms, zero calls)

## AMBROSIA final test

| model | method | AllFound | recall | precision (clear) | calls per q. | asks the user per 100 q. |
|---|---|---|---|---|---|---|
| sonnet | plain | 26 / 90 | 0.585 | 0.491 | 1.0 | 0 |
| sonnet | samplek | 31 / 90 | 0.635 | 0.490 | 3.0 | 0 |
| sonnet | dtp | 30 / 90 | 0.643 | 0.471 | 8.0 | 0 |
| sonnet | state | 9 / 90 | 0.428 | 0.650 | 1.0 | 0 |
| sonnet | ours | 32 / 90 | 0.656 | 0.626 | 3.1 | 0 |
| sonnet | method | 37 / 90 | 0.681 | 0.540 | 8.7 | 0 |
| gpt-6-sol | plain | 18 / 90 | 0.496 | 0.614 | 1.0 | 0 |
| gpt-6-sol | samplek | 24 / 90 | 0.563 | 0.588 | 3.0 | 0 |
| gpt-6-sol | dtp | 54 / 90 | 0.739 | 0.437 | 6.7 | 0 |
| gpt-6-sol | state | 8 / 90 | 0.385 | 0.650 | 1.0 | 0 |
| gpt-6-sol | ours | 37 / 90 | 0.643 | 0.667 | 2.6 | 0 |
| gpt-6-sol | method | 45 / 90 | 0.698 | 0.654 | 6.0 | 0 |

## Request sets (Table 5's 111 sets)

| model | method | open: both interpretations | specific: main right | specific: false alarm | calls per request | asks per 100 requests |
|---|---|---|---|---|---|---|
| sonnet | plain | 64 / 111 | 109 / 111 | 0 | 1.0 | 0 |
| sonnet | samplek | 72 / 111 | 108 / 111 | 0 | 3.0 | 0 |
| sonnet | dtp | 10 / 111 | 72 / 111 | 3 | 8.0 | 0 |
| sonnet | state | 0 / 111 | 109 / 111 | 0 | 1.0 | 0 |
| sonnet | ours | 78 / 111 | 109 / 111 | 0 | 2.6 | 0 |
| sonnet | method | 79 / 111 | 109 / 111 | 0 | 6.7 | 0 |
| gpt-6-sol | plain | 47 / 111 | 92 / 111 | 0 | 1.0 | 0 |
| gpt-6-sol | samplek | 60 / 111 | 92 / 111 | 0 | 3.0 | 0 |
| gpt-6-sol | dtp | 35 / 111 | 84 / 111 | 0 | 5.3 | 0 |
| gpt-6-sol | state | 0 / 111 | 92 / 111 | 0 | 1.0 | 0 |
| gpt-6-sol | ours | 62 / 111 | 106 / 111 | 0 | 2.5 | 0 |
| gpt-6-sol | method | 68 / 111 | 106 / 111 | 0 | 5.3 | 0 |

## Pooled over both models, method minus each, paired by item (points [95% bootstrap])

- vs plain: AMBROSIA AllFound [21.1, 14.4, 27.8], recall [14.9, 11.0, 18.9], precision [4.4, -1.3, 10.0]; request sets both [16.2, 10.8, 21.6], specific right [6.3, 2.7, 9.9].
- vs samplek: AMBROSIA AllFound [15.0, 8.3, 21.7], recall [9.1, 5.3, 12.6], precision [5.8, -0.2, 11.1]; request sets both [6.8, 1.8, 11.7], specific right [6.8, 3.2, 10.4].
- vs dtp: AMBROSIA AllFound [-1.1, -7.2, 5.0], recall [-0.1, -3.7, 3.4], precision [14.3, 7.7, 20.4]; request sets both [45.9, 39.2, 52.7], specific right [26.6, 21.2, 32.4].
- vs state: AMBROSIA AllFound [36.1, 28.9, 43.3], recall [28.3, 23.9, 33.0], precision [-5.3, -12.6, 1.9]; request sets both [66.2, 60.4, 72.1], specific right [6.3, 2.7, 9.9].
- vs ours: AMBROSIA AllFound [7.2, 3.9, 11.1], recall [4.1, 2.3, 6.0], precision [-5.0, -7.6, -2.5]; request sets both [3.2, 0.9, 5.4], specific right [0.0, 0.0, 0.0].

## Pooled, narrow search (ours) minus each baseline, paired by item

- vs plain: AMBROSIA AllFound [13.9, 7.8, 20.6], recall [10.8, 6.8, 14.8], precision [9.4, 3.2, 15.5]; request sets both [13.1, 7.7, 18.5], specific right [6.3, 2.7, 9.9].
- vs samplek: AMBROSIA AllFound [7.8, 1.7, 13.9], recall [5.0, 0.9, 8.6], precision [10.8, 4.4, 16.4]; request sets both [3.6, -1.4, 8.6], specific right [6.8, 3.2, 10.4].
- vs dtp: AMBROSIA AllFound [-8.3, -15.6, -1.7], recall [-4.2, -8.1, -0.1], precision [19.2, 12.3, 25.7]; request sets both [42.8, 35.1, 50.5], specific right [26.6, 21.2, 32.4].
- vs state: AMBROSIA AllFound [28.9, 22.2, 35.6], recall [24.3, 19.7, 28.8], precision [-0.3, -7.7, 7.2]; request sets both [63.1, 57.2, 69.4], specific right [6.3, 2.7, 9.9].
