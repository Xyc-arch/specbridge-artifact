# Does a silent choice change the answer? (`specbridge.report.impact`, zero model calls)

Per question with a silent choice (the reference settles it, no cue in the question or evidence), the matching library edit is applied to the reference(-equivalent) SQL and both are executed. One edit per choice type and question. Only edits that give a valid reading count (rules.alternative_ok).

## BIRD dev: 1534 questions, 1216 with a silent choice the edit can express

Per question (of 664 with an applicable edit): the answer changes under some other reading in 156 (23%); excluding join-type edits, 121; a single value moves by more than 10% in 55; the top-ranked item changes in 29.

| choice | edits | answer changes | value > 10% (single values) | value > 50% | top item changes (ordered) | top-k set changes | row set changes |
|---|---|---|---|---|---|---|---|
| all choices | 882 | 171 / 882 (19%) | 55 / 317 (17%) | 47 / 317 (15%) | 30 / 437 (7%) | 61 / 437 (14%) | 152 / 882 (17%) |
| inclusive vs strict bound | 20 | 8 / 20 (40%) | 5 / 15 (33%) | 2 / 15 (13%) | - | - | 8 / 20 (40%) |
| rows vs distinct entities | 168 | 49 / 168 (29%) | 47 / 158 (30%) | 43 / 158 (27%) | 3 / 11 (27%) | 3 / 11 (27%) | 49 / 168 (29%) |
| unmatched rows kept or dropped | 322 | 43 / 322 (13%) | 2 / 52 (4%) | 1 / 52 (2%) | 15 / 59 (25%) | 14 / 59 (24%) | 42 / 322 (13%) |
| missing values filtered | 155 | 15 / 155 (10%) | 0 / 41 (0%) | 0 / 41 (0%) | 11 / 152 (7%) | 11 / 152 (7%) | 15 / 155 (10%) |
| ties at an extreme | 217 | 56 / 217 (26%) | 1 / 51 (2%) | 1 / 51 (2%) | 1 / 215 (0%) | 33 / 215 (15%) | 38 / 217 (18%) |

