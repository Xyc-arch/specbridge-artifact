# Remaining BIRD questions: real question vs explicit V (batch3, batch4, batch5, batch6, batch7, batch8)

Haiku, 2 repeats; grading: BIRD set match, and beside it the shape-tolerant grade (column order and extra columns tolerated, rows must match).

**Denominators:** 317 tasks; explicit V rendered for 302; refused by the renderer 15; runs: original 604, explicit 604 (on the rendered tasks).

| runs correct | BIRD grade | shape tolerated |
|---|---|---|
| real question + evidence | 329/604 (54%) | 377/604 (62%) |
| explicit V | 594/604 (98%) | 594/604 (98%) |

| outcome per task (every repeat) | BIRD grade | shape tolerated |
|---|---|---|
| both correct | 138 | 167 |
| explicit only correct | 109 | 90 |
| real question only correct | 0 | 0 |
| neither correct | 2 | 2 |
| mixed across repeats | 53 | 43 |
| incomplete runs | 0 | 0 |
| explicit refused (no explicit V) | 15 | 15 |

Tasks whose outcome changes when shape is tolerated: 36.

**Tool failures (runs):** {'explicit: final query does not execute': 1, 'original: final query does not execute': 10}

**Diagnosed causes (162 inspected):** {'run variation': 48, 'semantic mapping': 31, 'implicit requirement': 27, 'output shape': 27, 'unwanted processing': 13, 'reading choice': 9, 'other': 5, 'numeric precision / grading sensitivity': 2}

**Library records:** 76; gate: {'medium / meaning choice': 23, 'high / meaning choice': 8, 'low / reference defect': 11, 'medium / output form': 21, 'low / meaning choice': 2, 'low / output form': 8, 'high / output form': 3}; accepted (high): 11

## Unresolved (per batch)

- **batch3**: mixed across repeats: 9; inspection unparsed or uncertain: 2; records gated medium/low or uncertain: 12; not recorded (not_library): 9
- **batch4**: mixed across repeats: 14; inspection unparsed or uncertain: 0; records gated medium/low or uncertain: 16; not recorded (not_library): 4
- **batch5**: mixed across repeats: 8; inspection unparsed or uncertain: 0; records gated medium/low or uncertain: 12; not recorded (not_library): 4
- **batch6**: mixed across repeats: 8; inspection unparsed or uncertain: 0; records gated medium/low or uncertain: 13; not recorded (not_library): 7
- **batch7**: mixed across repeats: 12; inspection unparsed or uncertain: 1; records gated medium/low or uncertain: 8; not recorded (not_library): 21
- **batch8**: mixed across repeats: 2; inspection unparsed or uncertain: 2; records gated medium/low or uncertain: 4; not recorded (not_library): 10
