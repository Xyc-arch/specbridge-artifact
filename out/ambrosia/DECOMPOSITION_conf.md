# Decomposition on AMBROSIA's own items, conf sample (`specbridge.comm.transfer.ambrosia decomp_report`)

60 ambiguous dev questions (test split, seeded) with 140 unambiguous versions (one per reading). Same single call and prompt for open and specific questions. A reading is matched to the open question's gold reading by executing both golds. Grades: shape-tolerant (primary) / strict.

| solver | AMBROSIA recall | AllFound | every specific right | AllFound where every specific right [Wilson 95%%] | readings missed in the open answer | **missed but computed when asked** [Wilson 95%%] |
|---|---|---|---|---|---|---|
| haiku | 0.47 / 0.33 | 7 / 4 of 60 | 35 / 22 | 5 of 35 (14%) [6, 29] / 2 of 22 | 75 / 94 | **44 of 75 (59%)** [47, 69] / 43 of 94 (46%) |
| sonnet | 0.56 / 0.45 | 12 / 4 of 60 | 39 / 36 | 8 of 39 (21%) [11, 36] / 3 of 36 | 62 / 77 | **43 of 62 (69%)** [57, 79] / 51 of 77 (66%) |
| gpt-6-sol | 0.52 / 0.42 | 8 / 4 of 60 | 36 / 31 | 4 of 36 (11%) [4, 25] / 1 of 31 | 68 / 83 | **47 of 68 (69%)** [57, 79] / 52 of 83 (63%) |
| gpt-6-luna | 0.37 / 0.32 | 4 / 0 of 60 | 27 / 26 | 3 of 27 (11%) [4, 28] / 0 of 26 | 87 / 96 | **42 of 87 (48%)** [38, 59] / 49 of 96 (51%) |

AMBROSIA's recall and AllFound count only the readings that appear in the open answer; they cannot tell a reading the model could not compute from one it computed but did not report. The last column makes that split.
