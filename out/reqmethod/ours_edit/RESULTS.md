# Arm `ours_edit` vs saved arms, 30 dev request sets (gate: out/reqmethod/ours_edit/GATE.md)

## sonnet

| arm | open: both readings | specific: main right | specific: false alarm | calls per request (all wordings) |
|---|---|---|---|---|
| plain | 13 / 30 | 29 / 30 | 0 | 1 |
| samplek | 17 / 30 | 29 / 30 | 0 | 3.0 |
| ours | 16 / 30 | 29 / 30 | 0 | 2.5 |
| ours_edit | 16 / 30 | 29 / 30 | 2 | 3.5 |

## gpt-6-sol

| arm | open: both readings | specific: main right | specific: false alarm | calls per request (all wordings) |
|---|---|---|---|---|
| plain | 10 / 30 | 24 / 30 | 0 | 1 |
| samplek | 15 / 30 | 24 / 30 | 0 | 3.0 |
| ours | 14 / 30 | 26 / 30 | 0 | 2.5 |
| ours_edit | 17 / 30 | 27 / 30 | 0 | 2.5 |

