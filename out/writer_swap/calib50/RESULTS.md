# Subsample calibration of writer self-preference (`specbridge.comm.construct.writer_swap`)

Corpus: 382 tasks with all four full-run answers (Sonnet-written, frozen). Calibration subsample: 50 sampled (seed 20261012), 50 rendered by gpt-6-sol and answered by all four.
Same pipeline for both writers (Opus review, one revision). Extra cost: 50 writes, 200 answers.

| solver | calibration: Sonnet-written | calibration: gpt-6-sol-written | writer effect d_s, points [95% CI] | p |
|---|---|---|---|---|
| haiku | 46/50 | 49/50 | -6.0 [-14.0, +2.0] | 0.376 |
| sonnet | 48/50 | 50/50 | -4.0 [-10.0, +0.0] | 0.499 |
| gpt-6-sol | 50/50 | 49/50 | +2.0 [+0.0, +6.0] | 1.000 |
| gpt-6-luna | 47/50 | 46/50 | +2.0 [-6.0, +10.0] | 1.000 |

| estimate | points [95% CI] | p |
|---|---|---|
| writer effect on neutral solvers (Haiku, GPT-Luna) | -2.0 [-8.0, +4.0] | |
| Sonnet home advantage | -2.0 [-9.0, +5.0] | 0.803 |
| GPT-Sol home advantage (its own text) | -4.0 [-12.0, +3.0] | 0.437 |
| Sonnet, full run (biased) | 95.0% | |
| **Sonnet, debiased** | +97.0 [+89.7, +104.3] | |
| haiku, full run (no correction: not the writer) | 91.4% | |
| gpt-6-sol, full run (no correction: not the writer) | 95.5% | |
| gpt-6-luna, full run (no correction: not the writer) | 89.5% | |
