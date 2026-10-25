# Precise natural questions for `pilot-dev@09cacc14fa59-corr1` (tasks_paired.jsonl)

Writer: frozen lm-writer (sonnet, input language+facts, one revision), ported to specbridge.comm.verbal.precise; batches of 8 per database, 6 concurrent. SQL, answers and graders unchanged. Delivered: corpus.jsonl, the rendered tasks with their natural question and explicit instructions.

**Natural coverage: 1 of 1 tasks** (passed on round 1: 1; revised and accepted: 0; deterministic, no model: 0). **Not rendered: 0** (the draft failed review twice or a symbol was undefined; the task is not delivered). **Missing output: 0** (the writer returned no draft even after the retry; not delivered). All 1 tasks accounted for: True.

Runtime 12 s; model calls 2 (write 1, review 1, revise 0; of these, 0 retries after a missing output); tokens in 23462, out 951; per natural question written by the model: 2.0 calls.

Review: one task per call.

Review failures by requirement (all rounds, before revision too): none

The reviewer's verdict is evidence, not proof. The language resource for a database without one falls back to the catalogue's column labels.

## A random sample of paired tasks

### 8ac7dd4f7e -- A2 S6, passed
**Natural (precise):** Step 1: Join each match to the player whose player identifier equals the match's losing player's identifier (inner join, one row per match; matches with no matching player are dropped). Group by losing player's identifier and playing hand, and compute the average loser age in each group (missing ages ignored; missing if none). Call the columns (1) losing player's identifier, (2) playing hand, (3) average loser age.

Step 2: Over all rows of step 1 as one group, compute the average of column (3) of step 1 (missing ignored; missing if none). Call it column (1).

Step 3: Join the rows of step 1 with the rows of step 2 where column (1) of step 2 is not missing (inner join, one row per match; unmatched rows dropped). Return (1) column (1) of step 1, (2) column (2) of step 1, (3) column (3) of step 1, (4) column (3) of step 1 minus column (1) of step 2.

Step 4: Group the rows of step 3 by column (2) of step 3 and return (1) column (2) of step 3, (2) the average of column (4) of step 3 in the group (missing ignored; missing if none).

Step 5: Join the rows of step 3 with the rows of step 4 where column (2) of step 3 equals column (1) of step 4 (compared as text, character by character; inner join, one row per match; unmatched rows dropped). Keep only rows where column (4) of step 3 is greater than column (2) of step 4. Return (1) column (1) of step 3, (2) column (2) of step 3, (3) column (3) of step 3, (4) column (4) of step 3, (5) column (4) of step 3 minus column (2) of step 4.

Final answer: using the rows of step 5, return one row per column (2) of step 5 (playing hand), with four outputs in this order: (1) column (2) of step 5, (2) the average of column (3) of step 5, (3) the average of column (4) of step 5, (4) the average of column (5) of step 5.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Player ID (`matches.loser_id`), one combined record per match (a record without a match is dropped); group the kept records by Player ID (`matches.loser_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Player ID (`matches.loser_id`); (2) playing hand (`players.hand`); (3) the average of loser age (`matches.loser_age`) in the group (missing values ignored; missing when there are none).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A − B. Here A is column (3) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; group the kept records by column (2) of step 3; each group gives one result row; for each result row, return (1) column (2) of step 3; (2) the average of column (4) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which column (2) of step 3 equals column (1) of step 4 (compared as text, character by character), one combined record per match (a record without a match is dropped); keep only the records for which column (4) of step 3 is greater than column (2) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) column (4) of step 3; (5) A − B. Here A is column (4) of step 3; B is column (2) of step 4.
Step 6 (the answer). Start from the rows of step 5; group the kept records by column (2) of step 5; each group gives one result row; for each result row, return (1) column (2) of step 5; (2) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none); (4) the average of column (5) of step 5 in the group (missing values ignored; missing when there are none).
</details>

