# Human review

The authors' reviews. Two authors cross-checked every request set independently; the files hold the final verdicts. These files are final; the code reads the verdicts from them and never changes them.

| File | What it holds |
|---|---|
| `review-307-author-approve.md` | the review sheet of all 307 request sets: per set, the open request, the two interpretations, how their results differ, and the verdict (could a reasonable analyst mean either interpretation? yes / no / unsure) with a note |
| `verdicts.json` | the verdict, choice type and note of each of the 307 sets, parsed from the sheet (204 yes); a note that starts "No: the type is rare in real data" marks the 28 sets the type-frequency rule removes |
| `review-reference-minority.md` | the review sheet of the references of open BIRD and Spider questions that take the less common interpretation (it feeds Figure 4, Table S1 and the type-frequency rule) |
| `reference_minority_verdicts.json` | the verdict and reason for each of the 1,259 references on that sheet (719 yes, 540 no) |
| `FROZEN.json` | the frozen population: the type-frequency rule (1%), the seven choice types it keeps, the 204 accepted set ids, and SHA-256 hashes of the four files above and of the method-comparison draw `out/reqmethod100/sets.json` (`python -m specbridge.comm.transfer.freeze check`) |
| `bird-other-reading.csv` | the review of BIRD answers that return the other interpretation (Section 6.2 and Table 4; `in_table_4`: the question is shown in Table 4) |
