# Subsample calibration of writer self-preference (`specbridge.comm.construct.writer_swap`)

Corpus: 382 tasks with all four full-run answers (Sonnet-written, frozen). Calibration subsample: 200 sampled (seed 20261012), 200 rendered by gpt-6-sol and answered by all four.
Same pipeline for both writers (Opus review, one revision). Extra cost: 200 writes, 800 answers.

| solver | calibration: Sonnet-written | calibration: gpt-6-sol-written | writer effect d_s, points [95% CI] | p |
|---|---|---|---|---|
| haiku | 183/200 | 185/200 | -1.0 [-6.0, +4.0] | 0.840 |
| sonnet | 189/200 | 198/200 | -4.5 [-8.0, -1.0] | 0.021 |
| gpt-6-sol | 193/200 | 197/200 | -2.0 [-5.0, +0.5] | 0.290 |
| gpt-6-luna | 177/200 | 174/200 | +1.5 [-4.5, +7.5] | 0.749 |

| estimate | points [95% CI] | p |
|---|---|---|
| writer effect on neutral solvers (Haiku, GPT-Luna) | +0.2 [-3.8, +4.2] | |
| Sonnet home advantage | -4.8 [-9.2, +0.0] | 0.060 |
| GPT-Sol home advantage (its own text) | +2.2 [-2.0, +6.5] | 0.351 |
| Sonnet, full run (biased) | 95.0% | |
| **Sonnet, debiased** | +99.8 [95.5, 100.0] (interval capped to 0-100) | |
| haiku, full run (no correction: not the writer) | 91.4% | |
| gpt-6-sol, full run (no correction: not the writer) | 95.5% | |
| gpt-6-luna, full run (no correction: not the writer) | 89.5% | |

Sonnet-written answers: full run (2026-10-02).
