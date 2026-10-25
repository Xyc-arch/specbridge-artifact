# Precise natural questions for `my-corpus-variety-demo@8fc775be66aa` (tasks_paired_sample.jsonl)

Writer: frozen lm-writer (sonnet, input language+facts, one revision), ported to comm.verbal.precise; batches of 8 per database, 6 concurrent. SQL, answers, graders and explicit instructions unchanged.

**Natural coverage: 10 of 10 tasks** (passed on round 1: 9; revised and accepted: 1; deterministic, no model: 0). **Explicit fallback: 0** -- these keep the explicit instructions and are not counted as natural.

Runtime 39 s; model calls 4 (write 1, review 2, revise 1); tokens in 45473, out 5008; per natural question written by the model: 0.4 calls.

Review failures by requirement (all rounds, before revision too): {'output 1': 1}

The reviewer's verdict is evidence, not proof. The language resource for a database without one falls back to the catalogue's column labels.

## A random sample of paired tasks

### 1e50455720 -- A2 S6, passed
**Natural (precise):** Step 1: join each match to the player whose player ID equals the match's winner ID (inner join; unmatched dropped). Group by winner ID and playing hand. Return: winner ID (c1), playing hand (c2), average winner ranking points (c3, missing values ignored, missing if none).
Step 2: from step 1, one group of all rows; return the average of step 1 c3 (c1, missing values ignored, missing if none).
Step 3: join step 1 rows to step 2 rows where step 2 c1 is not missing (inner join, unmatched dropped). Return step 1 c1, step 1 c2, step 1 c3, and (step 1 c3 ÷ step 2 c1) as c4.
Step 4: from step 3, group by c2; return c2 (c1) and average of step 3 c4 (c2, missing values ignored, missing if none).
Step 5: join step 3 rows to step 4 rows where step 3 c2 equals step 4 c1 (compared as text, character by character; inner join, unmatched dropped); keep only rows where step 3 c4 is greater than step 4 c2. Return step 3 c1, c2, c3, c4, and (step 3 c4 − step 4 c2) as c5.
Final: one summary row over all step 5 rows with 3 outputs: (1) average of step 5 column 3; (2) average of step 5 column 4; (3) average of step 5 column 5.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.winner_id`); (2) playing hand (`players.hand`); (3) the average of winner ranking points (`matches.winner_rank_points`) in the group (missing values ignored; missing when there are none).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A ÷ B. Here A is column (3) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; group the kept records by column (2) of step 3; each group gives one result row; for each result row, return (1) column (2) of step 3; (2) the average of column (4) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which column (2) of step 3 equals column (1) of step 4 (compared as text, character by character), one combined record per match (a record without a match is dropped); keep only the records for which column (4) of step 3 is greater than column (2) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) column (4) of step 3; (5) A − B. Here A is column (4) of step 3; B is column (2) of step 4.
Step 6 (the answer). Start from the rows of step 5; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (2) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (5) of step 5 in the group (missing values ignored; missing when there are none).
</details>

### acfe87cb18 -- A1 S6, passed
**Natural (precise):** Step 1: from rankings, group by player ID; return player ID (c1) and average ranking points (c2, missing values ignored, missing if none).
Step 2: from step 1, one group of all rows; return the average of step 1 c2 (c1, missing values ignored, missing if none).
Step 3: join step 1 rows to step 2 rows where step 2 c1 is not missing (inner join, unmatched dropped); keep only rows where step 1 c2 is greater than step 2 c1. Return step 1 c1, step 1 c2, and (step 1 c2 − step 2 c1).
Step 4: from step 3, one group of all rows; return the average of step 3 c2 (c1, missing values ignored, missing if none).
Step 5: join step 3 rows to step 4 rows where step 4 c1 is not missing (inner join, unmatched dropped); keep only rows where step 3 c2 is greater than step 4 c1. Return step 3 c1, step 3 c2, step 3 c3, and (step 3 c2 − step 4 c1).
Final: one summary row over all step 5 rows with 3 outputs: (1) average of step 5 column 2; (2) average of step 5 column 3; (3) average of step 5 column 4.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `rankings` record; group the kept records by Unique player identifiers (`rankings.player_id`); each group gives one result row; for each result row, return (1) Unique player identifiers (`rankings.player_id`); (2) the average of ranking points (`rankings.ranking_points`) in the group (missing values ignored; missing when there are none).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 1 is greater than column (1) of step 2; for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A − B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 3 is greater than column (1) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B. Here A is column (2) of step 3; B is column (1) of step 4.
Step 6 (the answer). Start from the rows of step 5; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 5 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none).
</details>

### abd8c575d1 -- A2 S3, passed
**Natural (precise):** Step 1: from tennis matches, group by loser playing hand and return the loser playing hand; the average loser age (missing values ignored; missing if none); and the average of (winner ranking points − loser ranking points) ÷ loser ranking points (missing values ignored; missing if none). Step 2: from step 1's rows, put all rows in one group and return the average of step 1's average loser age (missing values ignored; missing if none). Final: join step 1 to step 2 where step 2's value is not missing (inner join, one row per match; unmatched step 1 rows dropped). Return, in order: step 1's loser playing hand; step 1's average loser age; step 1's average relative ranking-points difference; and step 1's average loser age − step 2's average.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `matches` record; group the kept records by loser playing hand (`matches.loser_hand`); each group gives one result row; for each result row, return (1) loser playing hand (`matches.loser_hand`); (2) the average of loser age (`matches.loser_age`) in the group (missing values ignored; missing when there are none); (3) the average of (A − B) ÷ B in the group (missing values ignored; missing when there are none). Here A is winner ranking points (`matches.winner_rank_points`); B is loser ranking points (`matches.loser_rank_points`).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3 (the answer). Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A − B. Here A is column (2) of step 1; B is column (1) of step 2.
</details>

### 6580de1893 -- A2 S4, passed
**Natural (precise):** Step 1: from matches, group by tournament level; return tournament level (c1) and the average of (loser ranking points − winner ranking points) (c2, missing values ignored, missing if none).
Step 2: from step 1, one group of all rows; return the average of step 1 c2 (c1, missing values ignored, missing if none).
Step 3: join step 1 rows to step 2 rows where step 2 c1 is not missing (inner join, unmatched dropped); keep only rows where step 1 c2 is greater than step 2 c1. Return step 1 c1, step 1 c2, and (step 1 c2 − step 2 c1).
Final: one summary row over all step 3 rows with 2 outputs: (1) average of step 3 column 2; (2) average of step 3 column 3.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `matches` record; group the kept records by tournament level (`matches.tourney_level`); each group gives one result row; for each result row, return (1) tournament level (`matches.tourney_level`); (2) the average of A − B in the group (missing values ignored; missing when there are none). Here A is loser ranking points (`matches.loser_rank_points`); B is winner ranking points (`matches.winner_rank_points`).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 1 is greater than column (1) of step 2; for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A − B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4 (the answer). Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 3 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
</details>

### a050d02452 -- A2 S5, passed
**Natural (precise):** Step 1: join each match to the player whose player ID equals the match's winner ID (inner join; unmatched dropped). Group by winner ID and playing hand. Return: winner ID (c1), playing hand (c2), average of (loser height − winner height) (c3, missing values ignored, missing if none), and number of records in the group (c4).
Step 2: from step 1, group by c2; return c2 (c1), average of step 1 c3 (c2, missing values ignored, missing if none), average of step 1 c4 (c3, missing values ignored, missing if none).
Step 3: from step 2, one group of all rows; return the average of step 2 c2 (c1, missing values ignored, missing if none).
Step 4: join step 2 rows to step 3 rows where step 3 c1 is not missing (inner join, unmatched dropped); keep only rows where step 2 c2 is greater than step 3 c1. Return step 2 c1, step 2 c2, step 2 c3, and (step 2 c2 − step 3 c1).
Final: one summary row over all step 4 rows with 3 outputs: (1) average of step 4 column 2; (2) average of step 4 column 3; (3) average of step 4 column 4.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `matches` record; combine it with each `players` record for which Unique player identifiers (`players.player_id`) equals Unique identifier for each player (`matches.winner_id`), one combined record per match (a record without a match is dropped); group the kept records by Unique identifier for each player (`matches.winner_id`) and playing hand (`players.hand`); each group gives one result row; for each result row, return (1) Unique identifier for each player (`matches.winner_id`); (2) playing hand (`players.hand`); (3) the average of A − B in the group (missing values ignored; missing when there are none); (4) the number of records in the group. Here A is loser height (`matches.loser_ht`); B is winner height (`matches.winner_ht`).
Step 2. Start from the rows of step 1; group the kept records by column (2) of step 1; each group gives one result row; for each result row, return (1) column (2) of step 1; (2) the average of column (3) of step 1 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 2; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 2 in the group (missing values ignored; missing when there are none).
Step 4. Start from the rows of step 2; combine it with the rows of step 3 for which it is not true that column (1) of step 3 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 2 is greater than column (1) of step 3; for each kept record, return (1) column (1) of step 2; (2) column (2) of step 2; (3) column (3) of step 2; (4) A − B. Here A is column (2) of step 2; B is column (1) of step 3.
Step 5 (the answer). Start from the rows of step 4; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 4 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 4 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 4 in the group (missing values ignored; missing when there are none).
</details>

### deed201a1f -- A2 S6, passed
**Natural (precise):** Step 1: from rankings, group by player ID; return player ID (c1) and number of records in the group (c2).
Step 2: from step 1, one group of all rows; return the sum of step 1 c2 (c1, missing values ignored, missing if none).
Step 3: join step 1 rows to step 2 rows where step 2 c1 is not missing (inner join, unmatched dropped). Return step 1 c1, step 1 c2, and (step 1 c2 ÷ step 2 c1).
Step 4: from step 3, one group of all rows; return the average of step 3 c3 (c1, missing values ignored, missing if none).
Step 5: join step 3 rows to step 4 rows where step 4 c1 is not missing (inner join, unmatched dropped); keep only rows where step 3 c3 is greater than step 4 c1. Return step 3 c1, step 3 c2, step 3 c3, and (step 3 c3 − step 4 c1).
Final: one summary row over all step 5 rows with 3 outputs: (1) total of step 5 column 2; (2) average of step 5 column 3; (3) average of step 5 column 4.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `rankings` record; group the kept records by Unique player identifiers (`rankings.player_id`); each group gives one result row; for each result row, return (1) Unique player identifiers (`rankings.player_id`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (3) of step 3 is greater than column (1) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B. Here A is column (3) of step 3; B is column (1) of step 4.
Step 6 (the answer). Start from the rows of step 5; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 5 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none).
</details>

