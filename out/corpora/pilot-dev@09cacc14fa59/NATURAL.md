# Precise natural questions for `pilot-dev@09cacc14fa59` (tasks_paired.jsonl)

Writer: frozen lm-writer (sonnet, input language+facts, one revision), ported to specbridge.comm.verbal.precise; batches of 8 per database, 6 concurrent. SQL, answers and graders unchanged. Delivered: corpus.jsonl, the rendered tasks with their natural question and explicit instructions.

**Natural coverage: 47 of 48 tasks** (passed on round 1: 37; revised and accepted: 10; deterministic, no model: 0). **Not rendered: 1** (the draft failed review twice or a symbol was undefined; the task is not delivered). **Missing output: 0** (the writer returned no draft even after the retry; not delivered). All 48 tasks accounted for: True.

Runtime 104 s; model calls 71 (write 6, review 59, revise 6; of these, 0 retries after a missing output); tokens in 713777, out 39583; per natural question written by the model: 1.5 calls.

Review: one task per call.

Review failures by requirement (all rounds, before revision too): {'steps': 4, 'join 1': 4, 'output 2': 3, 'output 1': 3, 'output 4': 3, 'definition B': 3, 'output 3': 1, 'records': 1, 'record filter': 1, 'ordering': 1}

The reviewer's verdict is evidence, not proof. The language resource for a database without one falls back to the catalogue's column labels.

## A random sample of paired tasks

### 119443f16c -- A1 S6, passed
**Natural (precise):** Join each interaction to its recommendation (reckey equals the interaction's related recommendation id), then to the recommended article (artkey equals the recommendation's article id), then to the article author user (userkey equals the article's author user id); records lacking any match are dropped. Group by related recommendation id and A/B test group, and count records per group. Compute the total of those counts. Divide each group's count by the total (inner join, one row per match). Then group by A/B test group, summing the counts and averaging the count shares (missing values ignored). Compute the average of the per-test-group summed counts (missing values ignored). Pair each test group row with that average (inner join, dropping rows where it is missing, one row per match), keep only rows where the group's summed count is greater than that average, and return A/B test group, summed count, average share, and summed count minus that average.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `interactions` record; combine it with each `recommendations` record for which reckey (`recommendations.reckey`) equals A BIGINT FK referencing Recommendations(RecKey) (`interactions.reclink`), one combined record per match (a record without a match is dropped); combine it with each `articles` record for which artkey (`articles.artkey`) equals artlink (`recommendations.artlink`), one combined record per match (a record without a match is dropped); combine it with each `users` record for which userkey (`users.userkey`) equals authref (`articles.authref`), one combined record per match (a record without a match is dropped); group the kept records by A BIGINT FK referencing Recommendations(RecKey) (`interactions.reclink`) and A/B test group (`users.testgrp`); each group gives one result row; for each result row, return (1) A BIGINT FK referencing Recommendations(RecKey) (`interactions.reclink`); (2) A/B test group (`users.testgrp`); (3) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A ÷ B. Here A is column (3) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; group the kept records by column (2) of step 3; each group gives one result row; for each result row, return (1) column (2) of step 3; (2) the sum of column (3) of step 3 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 4; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 4 in the group (missing values ignored; missing when there are none).
Step 6 (the answer). Start from the rows of step 4; combine it with the rows of step 5 for which it is not true that column (1) of step 5 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 4 is greater than column (1) of step 5; for each kept record, return (1) column (1) of step 4; (2) column (2) of step 4; (3) column (3) of step 4; (4) A − B. Here A is column (2) of step 4; B is column (1) of step 5.
</details>

### 57392f9179 -- A1 S3, revised
**Natural (precise):** Count the atom records for each chemical element; call this count A for each element. Compute B as the average of these per-element counts over all elements (missing if there are none). Pair each element's row with that single B row through an inner join, one row per match, dropping any element row with no match, so a missing B leaves no rows. Keep only elements where A is greater than B. Return the element, A, and A − B.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `atom` record; group the kept records by chemical element of the atom (`atom.element`); each group gives one result row; for each result row, return (1) chemical element of the atom (`atom.element`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3 (the answer). Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 1 is greater than column (1) of step 2; for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A − B. Here A is column (2) of step 1; B is column (1) of step 2.
</details>

### 0448b02ef9 -- A1 S5, revised
**Natural (precise):** Count the atom records for each chemical element; call this count A for each element. Let S be the sum of these per-element counts over all elements (missing if there are none). Pair each element row with S through an inner join, one row per match, dropping any element row with no match, so a missing S leaves no rows; for each kept row compute R = A ÷ S. Let B be the average of the per-element counts A over the kept rows (missing values ignored; missing when there are none). Pair each kept row with B through an inner join, one row per match, dropping any row with no match, so a missing B leaves no rows. Return the element, A, R, and A ÷ B.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `atom` record; group the kept records by chemical element of the atom (`atom.element`); each group gives one result row; for each result row, return (1) chemical element of the atom (`atom.element`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A ÷ B. Here A is column (2) of step 3; B is column (1) of step 4.
</details>

### 7adb1feb1d -- A2 S5, passed
**Natural (precise):** Join interactions to recommendations (reckey = the interaction's related recommendation id), then to articles (artkey = artlink), then to users (userkey = authref); all inner joins, dropping unmatched, one row per match. Group by related recommendation id and subscription status (of the article's author) and count records (call it C). Let T be the sum of C over all groups. For each group compute R = C ÷ T (rows with T missing dropped). Then group these rows by subscription status and compute the average R (call it S). Join each (recommendation, status, C, R) row to the status average S on subscription status equal as text (inner join, one row per match). Return related recommendation id, subscription status, C, R, and R − S. Sort by R − S highest first, missing last, and return the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `interactions` record; combine it with each `recommendations` record for which reckey (`recommendations.reckey`) equals A BIGINT FK referencing Recommendations(RecKey) (`interactions.reclink`), one combined record per match (a record without a match is dropped); combine it with each `articles` record for which artkey (`articles.artkey`) equals artlink (`recommendations.artlink`), one combined record per match (a record without a match is dropped); combine it with each `users` record for which userkey (`users.userkey`) equals authref (`articles.authref`), one combined record per match (a record without a match is dropped); group the kept records by A BIGINT FK referencing Recommendations(RecKey) (`interactions.reclink`) and subscription status (`users.substatus`); each group gives one result row; for each result row, return (1) A BIGINT FK referencing Recommendations(RecKey) (`interactions.reclink`); (2) subscription status (`users.substatus`); (3) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A ÷ B. Here A is column (3) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; group the kept records by column (2) of step 3; each group gives one result row; for each result row, return (1) column (2) of step 3; (2) the average of column (4) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which column (2) of step 3 equals column (1) of step 4 (compared as text, character by character), one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) column (4) of step 3; (5) A − B; order the result rows by A − B descending (missing last); keep only the first 10 rows. Here A is column (4) of step 3; B is column (2) of step 4.
</details>

### 061bb0131b -- A2 S3, passed
**Natural (precise):** For each article author (authref), compute the sum of media elements (ignoring missing) and the average of word count ÷ estimated reading time (ignoring missing) (call it A). Compute B as the overall average of A across all authors, and keep only authors where B is not missing. Return authref, sum of media elements, A, and A ÷ B. Sort by A ÷ B highest first, missing last, and return the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `articles` record; group the kept records by authref (`articles.authref`); each group gives one result row; for each result row, return (1) authref (`articles.authref`); (2) the sum of media elements (`articles.mediacount`) in the group (missing values ignored; missing when there are none); (3) the average of A ÷ B in the group (missing values ignored; missing when there are none). Here A is word count (`articles.wordlen`); B is estimated reading time (`articles.readsec`).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3 (the answer). Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A ÷ B; order the result rows by A ÷ B descending (missing last); keep only the first 10 rows. Here A is column (3) of step 1; B is column (1) of step 2.
</details>

### c7c8683c6d -- A1 S3, passed
**Natural (precise):** For each device id in the system performance records, compute the average overall system performance rating score (missing values ignored). Also compute the average of those per-device averages (missing values ignored). Pair each device row with that overall average (inner join, dropping rows where the overall average is missing, one row per match). Return device id, the device's average performance score, and the device's average divided by the overall average. Sort by that ratio, highest first, missing values last, and return only the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `systemperformance` record; group the kept records by devlink (`systemperformance.devlink`); each group gives one result row; for each result row, return (1) devlink (`systemperformance.devlink`); (2) the average of system performance score (`systemperformance.perfscore`) in the group (missing values ignored; missing when there are none).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3 (the answer). Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B; order the result rows by A ÷ B descending (missing last); keep only the first 10 rows. Here A is column (2) of step 1; B is column (1) of step 2.
</details>

