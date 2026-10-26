# Same-family check: open requests rewritten by GPT-Sol (`specbridge.comm.transfer.writer_swap_open`)

60 sets drawn at random (seed 20261026) from the accepted sets; 60 written; 35 pass the review; 35 answered by every model.

| model | both returned, Opus-written | both returned, GPT-Sol-written | only Opus / only GPT | McNemar p | named, Opus / GPT |
|---|---|---|---|---|---|
| haiku | 12 | 10 | 7 / 5 | 0.774 | 15 / 16 |
| sonnet | 18 | 20 | 4 / 6 | 0.754 | 25 / 23 |
| gpt-6-sol | 12 | 17 | 2 / 7 | 0.18 | 16 / 18 |
| gpt-6-luna | 3 | 6 | 1 / 4 | 0.375 | 12 / 13 |

Ranking by both returned: Opus-written ['sonnet', 'haiku', 'gpt-6-sol', 'gpt-6-luna']; GPT-Sol-written ['sonnet', 'gpt-6-sol', 'haiku', 'gpt-6-luna'].
