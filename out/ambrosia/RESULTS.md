# Raise vs placebo on AMBROSIA (`specbridge.comm.transfer.ambrosia`)

Test split, seeded: 20 ambiguous and 10 unambiguous questions per type (scope, attachment, vague). AMBROSIA's prompt, parser and scorer. Questions with all three arms saved. AllFound and found: count (raise vs placebo gained/lost, exact McNemar p).

| solver | ambiguous n | AllFound: plain | placebo | raise | recall: plain / placebo / raise | precision: plain / placebo / raise | unambiguous n | found: plain / placebo / raise | precision: plain / placebo / raise |
|---|---|---|---|---|---|---|---|---|---|
| haiku | 30 | 0 | 0 | 0 (+0/-0, p 1) | 0.15 / 0.25 / 0.26 | 0.32 / 0.53 / 0.48 | 15 | 3 / 7 / 7 | 0.20 / 0.43 / 0.43 |
| sonnet | 30 | 4 | 4 | 3 (+1/-2, p 1) | 0.50 / 0.51 / 0.44 | 0.57 / 0.69 / 0.52 | 15 | 11 / 13 / 11 | 0.58 / 0.59 / 0.45 |
| gpt-6-sol | 29 | 4 | 2 | 1 (+1/-2, p 1) | 0.48 / 0.43 / 0.39 | 0.76 / 0.76 / 0.70 | 15 | 9 / 10 / 9 | 0.53 / 0.60 / 0.57 |
| gpt-6-luna | 29 | 0 | 0 | 0 (+0/-0, p 1) | 0.21 / 0.20 / 0.27 | 0.50 / 0.48 / 0.53 | 15 | 10 / 9 / 9 | 0.63 / 0.57 / 0.53 |

Pooled raise - placebo, all_found: 118 pairs, -0.017, sign-flip p = 0.7046.
Pooled raise - placebo, recall: 118 pairs, -0.007, sign-flip p = 0.7166.
Pooled raise - placebo, unambig_precision: 60 pairs, -0.053, sign-flip p = 0.1917.

AllFound by ambiguity type (plain / placebo / raise of n):
- haiku: scope 0/0/0 of 8; attachment 0/0/0 of 10; vague 0/0/0 of 12
- sonnet: scope 2/1/2 of 8; attachment 1/1/1 of 10; vague 1/2/0 of 12
- gpt-6-sol: scope 1/0/0 of 8; attachment 1/1/0 of 9; vague 2/1/1 of 12
- gpt-6-luna: scope 0/0/0 of 7; attachment 0/0/0 of 10; vague 0/0/0 of 12

BUG (found 2026-10-14): DtP interpretation lines were parsed with x.strip(" -*0123456789."), cutting final numbers off; the DtP arms
of the dev pilot and the final test are affected. Fixed by ambrosia.item_line; DtP needs a rerun before its numbers are final.
