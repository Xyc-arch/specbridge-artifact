# Decomposition on AMBROSIA's own items, dev sample (`specbridge.comm.transfer.ambrosia decomp_report`)

60 ambiguous dev questions (test split, seeded) with 140 unambiguous versions (one per reading). Same single call and prompt for open and specific questions. A reading is matched to the open question's gold reading by executing both golds. Grades: shape-tolerant (primary) / strict.

| solver | AMBROSIA recall | AllFound | every specific right | AllFound where every specific right [Wilson 95%%] | readings missed in the open answer | **missed but computed when asked** [Wilson 95%%] |
|---|---|---|---|---|---|---|
| haiku | 0.23 / 0.16 | 3 / 1 of 60 | 22 / 15 | 2 of 22 (9%) [3, 28] / 0 of 15 | 110 / 118 | **57 of 110 (52%)** [43, 61] / 53 of 118 (45%) |
| sonnet | 0.57 / 0.49 | 15 / 10 of 60 | 44 / 33 | 15 of 44 (34%) [22, 49] / 8 of 33 | 62 / 73 | **39 of 62 (63%)** [50, 74] / 41 of 73 (56%) |
| gpt-6-sol | 0.57 / 0.42 | 15 / 7 of 60 | 42 / 33 | 10 of 42 (24%) [13, 39] / 4 of 33 | 60 / 82 | **37 of 60 (62%)** [49, 73] / 44 of 82 (54%) |
| gpt-6-luna | 0.35 / 0.25 | 6 / 0 of 60 | 31 / 29 | 4 of 31 (13%) [5, 29] / 0 of 29 | 90 / 106 | **44 of 90 (49%)** [39, 59] / 48 of 106 (45%) |

AMBROSIA's recall and AllFound count only the readings that appear in the open answer; they cannot tell a reading the model could not compute from one it computed but did not report. The last column makes that split.
