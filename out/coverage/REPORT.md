# Semantic coverage of delivered SQL

The same attempts as `out/crossdb` (P, seed and code unchanged), with every judgement of the one checker recorded. Strong and plausible both count as SUPPORTED. Reproduce: `python -m pd.coverage california_schools financial thrombosis_prediction toxicology superhero store_1`.

## 1. Operations: how much meaning the checker establishes

Substantive operations are arithmetic over data (two non-constant operands, or a parameter the target explains: a conversion, a whole, a reference). Everything else is shown apart and never counts toward support.

| database | substantive ops | supported (strong + plausible) | strong | plausible | unknown | contradicted |
|---|---|---|---|---|---|---|
| california_schools | 523 | **15%** | 6% | 10% | 85% | 0% |
| financial | 581 | **11%** | 3% | 8% | 89% | 0% |
| thrombosis_prediction | 424 | **7%** | 0% | 7% | 93% | 0% |
| toxicology | 508 | **1%** | 1% | 0% | 99% | 0% |
| superhero | 711 | **5%** | 0% | 5% | 95% | 0% |
| store_1 | 784 | **3%** | 0% | 3% | 97% | 0% |

Not substantive, for reference (counts of nodes, and the share the checker supports):

| database | declared number (weight, score, zero) | arithmetic on a constant expression | aggregate | function | cast | CASE | window |
|---|---|---|---|---|---|---|---|
| california_schools | 260 (0% supported) | 12 (0% supported) | 39 (0% supported) | 178 (0% supported) | 179 (0% supported) | 92 (0% supported) | 31 (0% supported) |
| financial | 391 (0% supported) | 24 (0% supported) | 61 (0% supported) | 250 (0% supported) | 234 (0% supported) | 97 (0% supported) | 19 (0% supported) |
| thrombosis_prediction | 268 (0% supported) | 13 (0% supported) | 45 (0% supported) | 186 (0% supported) | 174 (0% supported) | 88 (0% supported) | 29 (0% supported) |
| toxicology | 496 (0% supported) | 54 (0% supported) | 45 (0% supported) | 221 (0% supported) | 310 (0% supported) | 129 (0% supported) | 17 (0% supported) |
| superhero | 483 (0% supported) | 30 (0% supported) | 39 (0% supported) | 244 (0% supported) | 292 (0% supported) | 138 (0% supported) | 37 (0% supported) |
| store_1 | 610 (0% supported) | 38 (0% supported) | 70 (0% supported) | 301 (0% supported) | 345 (0% supported) | 156 (0% supported) | 15 (0% supported) |

## 2. Relationships: does support survive aggregates, casts, arithmetic and steps?

Arithmetic between two non-constant operands, by how each operand reached the operator (casts and value-keeping functions looked through). Share supported, with the count of such nodes.

| database | derived/derived | column/derived | column/column | case/derived | derived/function | derived/step output | case/case | step output/step output |
|---|---|---|---|---|---|---|---|---|
| california_schools | 5% of 208 | 5% of 62 | 35% of 43 | 0% of 11 | 0% of 4 | 29% of 7 | 0% of 4 | 12% of 8 |
| financial | 6% of 262 | 7% of 44 | 32% of 25 | 0% of 14 | 0% of 12 | 5% of 19 | 0% of 6 | 18% of 11 |
| thrombosis_prediction | 3% of 177 | 4% of 53 | 47% of 32 | 0% of 16 | 0% of 9 | 0% of 14 | 0% of 3 | 0% of 10 |
| toxicology | 0% of 329 | - | - | 0% of 31 | 0% of 13 | 0% of 5 | 0% of 18 | 0% of 7 |
| superhero | 3% of 362 | 3% of 38 | 0% of 29 | 0% of 37 | 0% of 14 | 0% of 7 | 0% of 17 | 0% of 7 |
| store_1 | 3% of 432 | 0% of 22 | 33% of 18 | 0% of 38 | 0% of 22 | 0% of 15 | 0% of 12 | 7% of 15 |

## 3. Parameters: unit-justified, data-grounded, or declared

| parameter | california_schools | financial | thrombosis_prediction | toxicology | superhero | store_1 |
|---|---|---|---|---|---|---|
| CONVERT: unit-justified conversion | 35 | 24 | 3 | 2 | 20 | 3 |
| CONVERT: unit not established | 0 | 0 | 0 | 0 | 0 | 0 |
| WHOLE: complement of a share or percentage | 13 | 7 | 5 | 2 | 2 | 2 |
| WHOLE: operand not a share or percentage | 42 | 70 | 37 | 67 | 90 | 97 |
| REFERENCE: grounded in the rows | 58 | 53 | 45 | 6 | 59 | 68 |
| REFERENCE: no stored values | 9 | 10 | 3 | 13 | 8 | 11 |
| WEIGHT: declared, stated by the question | 244 | 355 | 245 | 454 | 453 | 556 |
| ZERO: declared | 16 | 36 | 23 | 42 | 30 | 54 |

## 4. Whole queries: are their substantive operations supported?

| database | delivered | all supported | some supported | none supported | no substantive operation |
|---|---|---|---|---|---|
| california_schools | 128 | 8 (6%) | 42 (33%) | 30 (23%) | 48 (38%) |
| financial | 128 | 5 (4%) | 30 (23%) | 42 (33%) | 51 (40%) |
| thrombosis_prediction | 116 | 4 (3%) | 17 (15%) | 46 (40%) | 49 (42%) |
| toxicology | 97 | 0 (0%) | 4 (4%) | 57 (59%) | 36 (37%) |
| superhero | 125 | 0 (0%) | 18 (14%) | 67 (54%) | 40 (32%) |
| store_1 | 126 | 0 (0%) | 15 (12%) | 63 (50%) | 48 (38%) |

## 5. Rejections: what the contracts prevented

Column candidates and reused objects a contract rejected at the decisions actually made, per 100 attempts, by the operators judging them and the basis (rows: an identifier, text or date where a quantity is needed; doc or model: a documented or proposed unit or scale; grain: a join repeating the rows an aggregate counts). Counted at every decision, so a column refused at many decisions counts each time; 'rows' is mostly identifiers and text offered to arithmetic.

- **california_schools** (291315 exclusions in 200 attempts): column: ARITH * | rows: 45234, column: ARITH / | rows: 28468, column: ARITH + | rows: 19961, column: ARITH - | rows: 15652, column: AGG AVG | rows: 4048, column: ARITH / > CAST REAL | rows: 2601
- **financial** (62647 exclusions in 200 attempts): column: ARITH * | rows: 8682, column: ARITH / | rows: 5629, column: ARITH + | rows: 3602, column: ARITH - | rows: 2706, reuse: ARITH * | rows: 2266, reuse: ARITH / | rows: 1374
- **thrombosis_prediction** (89391 exclusions in 200 attempts): column: ARITH * | rows: 12605, column: ARITH / | rows: 8520, column: ARITH + | rows: 4803, column: ARITH - | rows: 3574, reuse: ARITH * | rows: 1814, column: AGG AVG | grain: 1449
- **toxicology** (41902 exclusions in 200 attempts): column: ARITH * | rows: 4472, column: ARITH / | rows: 3420, reuse: ARITH * | rows: 2048, column: ARITH + | rows: 1974, reuse: ARITH / | rows: 1605, column: ARITH - | rows: 1571
- **superhero** (58514 exclusions in 200 attempts): column: ARITH * | rows: 8230, column: ARITH / | rows: 5852, column: ARITH + | rows: 4024, column: ARITH - | rows: 3088, reuse: ARITH * | rows: 1610, reuse: ARITH / | rows: 1059
- **store_1** (86891 exclusions in 200 attempts): column: ARITH * | rows: 11852, column: ARITH / | rows: 8350, column: ARITH + | rows: 6050, column: ARITH - | rows: 4245, reuse: ARITH * | rows: 2114, reuse: ARITH / | rows: 1552

Finished programs the final check refused, by constructor, operator and basis:

- **california_schools** (49 of 200 attempts): (Arith +, model) 12, (Agg AVG, grain) 8, (Arith *, model) 7, (Arith -, rows) 5, (Func round, rows) 4, (Arith -, model) 3
- **financial** (42 of 200 attempts): (Agg AVG, grain) 11, (Arith /, rows) 10, (Func round, rows) 6, (Arith -, model) 4, (Arith *, rows) 4, (Arith +, model) 4
- **thrombosis_prediction** (55 of 200 attempts): (Arith +, model) 13, (Func round, rows) 11, (Agg AVG, grain) 9, (Arith /, rows) 7, (Arith *, rows) 5, (Arith -, model) 4
- **toxicology** (15 of 200 attempts): (Func round, rows) 10, (Func sqrt, rows) 2, (Arith +, rule) 1, (Arith /, rows) 1, (Arith *, rows) 1
- **superhero** (33 of 200 attempts): (Arith +, model) 10, (Func round, rows) 9, (Agg AVG, grain) 7, (Agg SUM, grain) 2, (Func greatest, model) 2, (Func power, rows) 1
- **store_1** (33 of 200 attempts): (Agg AVG, grain) 10, (Func round, rows) 6, (Arith /, rows) 5, (Arith *, rows) 4, (Arith +, model) 2, (Arith -, rows) 2