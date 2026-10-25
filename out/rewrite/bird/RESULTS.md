# Simulated user clarification on BIRD dev (gate: out/rewrite/bird/GATE.md)

| model | questions | (c) add | (b) rewrite | (d) standalone | (c)-(b): lost / gained, p | (c)-(d): lost / gained, p |
|---|---|---|---|---|---|---|
| sonnet | 149 | 53.7 | 47.0 | 45.0 | 13 / 3, 0.021 | 16 / 3, 0.0044 |
| gpt-6-sol | 149 | 37.6 | 37.6 | 31.5 | 10 / 10, 1 | 16 / 7, 0.093 |
| pooled | 298 | 45.6 | 42.3 | 38.3 | 23 / 13, 0.13 | 32 / 10, 0.00094 |

Why answers failed (pooled; execution): add: clarification lost 27, other requirement lost 132, does not run 3; rewrite: clarification lost 24, other requirement lost 139, does not run 9; standalone: clarification lost 21, other requirement lost 157, does not run 6

By choice type (pooled): boundary n=12 add 75 / rewrite 75 / standalone 83; count_unit n=90 add 49 / rewrite 49 / standalone 44; join_kind n=112 add 40 / rewrite 38 / standalone 33; null_filter n=12 add 0 / rewrite 0 / standalone 0; ties n=72 add 53 / rewrite 43 / standalone 38
