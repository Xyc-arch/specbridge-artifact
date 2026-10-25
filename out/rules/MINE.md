# Rule priors from training golds (`specbridge.comm.diagnose.rules mine`)

Spider train (seeded 2500 queries; executed): sites, share where the edit runs and CHANGES the answer, the gold's side among sites where it changes. BIRD train (9,428 queries): syntax only -- sites and the gold's side.

| rule | Spider sites | edit runs | edit changes answer | gold side when it changes | BIRD sites | BIRD gold side |
|---|---|---|---|---|---|---|
| ties | 340 | 339 | 67 (20%) | cut 67 | 1686 | cut 1686 |
| count_unit | 268 | 268 | 62 (23%) | entities 58, rows 4 | 3216 | rows 2886, entities 330 |
| join_kind | 1909 | 1909 | 125 (7%) | drop_unmatched 125 | 9571 | drop_unmatched 9524, keep_unmatched 47 |
| null_filter | 121 | 121 | 0 (0%) |  | 1015 | unfiltered 1003, filtered 12 |
| division | 0 | 0 | 0 (0%) |  | 985 | integer 691, real 294 |
| dedup | 858 | 858 | 9 (1%) | duplicates 9 | 4034 | duplicates 3256, distinct 778 |
| boundary | 370 | 370 | 130 (35%) | strict 77, inclusive 53 | 1157 | strict 958, inclusive 199 |
