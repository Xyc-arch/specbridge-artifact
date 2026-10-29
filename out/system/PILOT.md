# System dev pilot (gate: out/system/PREREG.md)

## AMBROSIA dev, Sonnet (shape-tolerant; merged as every arm)

| arm | AllFound | recall | precision (unambiguous) | answers per unambiguous q. | calls per q. |
|---|---|---|---|---|---|
| dtp | 27 / 60 | 0.692 | 0.443 | 4.20 | 8.0 |
| ours | 27 / 60 | 0.669 | 0.667 | 1.53 | 3.1 |
| system | 29 / 60 | 0.697 | 0.676 | 2.63 | 8.2 |

AMBROSIA gate: PASS (AllFound 29 vs DtP 27; precision 0.676 vs DtP 0.443 + 0.10).

## Request sets dev, sonnet

| arm | open: both interpretations | specific: main right | specific: false alarm |
|---|---|---|---|
| plain | 13 / 30 | 29 / 30 | 0 |
| samplek | 17 / 30 | 29 / 30 | 0 |
| dtp | 1 / 30 | 16 / 30 | 0 |
| ours | 18 / 30 | 29 / 30 | 0 |
| system | 18 / 30 | 30 / 30 | 2 |

Request-set gate, sonnet: PASS.

## Request sets dev, gpt-6-sol

| arm | open: both interpretations | specific: main right | specific: false alarm |
|---|---|---|---|
| plain | 10 / 30 | 24 / 30 | 0 |
| samplek | 15 / 30 | 24 / 30 | 0 |
| dtp | 9 / 30 | 24 / 30 | 0 |
| ours | 14 / 30 | 26 / 30 | 0 |
| system | 15 / 30 | 27 / 30 | 0 |

Request-set gate, gpt-6-sol: PASS.

**Pilot: PASS.**
