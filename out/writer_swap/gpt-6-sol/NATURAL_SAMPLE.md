# Precise natural questions for `gpt-6-sol` (tasks_paired_sample.jsonl)

Writer: frozen lm-writer (sonnet, input language+facts, one revision), ported to specbridge.comm.verbal.precise; batches of 8 per database, 6 concurrent. SQL, answers and graders unchanged. Delivered: corpus.jsonl, the rendered tasks with their natural question and explicit instructions.

**Natural coverage: 4 of 4 tasks** (passed on round 1: 4; revised and accepted: 0; deterministic, no model: 0). **Not rendered: 0** (the draft failed review twice or a symbol was undefined; the task is not delivered). **Missing output: 0** (the writer returned no draft even after the retry; not delivered). All 4 tasks accounted for: True.

Runtime 31 s; model calls 8 (write 4, review 4, revise 0; of these, 0 retries after a missing output); tokens in 46399, out 775; per natural question written by the model: 2.0 calls.

Review: one task per call.

Review failures by requirement (all rounds, before revision too): none

The reviewer's verdict is evidence, not proof. The language resource for a database without one falls back to the catalogue's column labels.

## A random sample of paired tasks

### 018d9bb7b2 -- A2 S6, passed
**Natural (precise):** For each account disposition, join every client whose unique identifier equals the disposition’s linked client ID, keeping one row per match and dropping dispositions without a match. Group the joined rows by client gender and count the rows in each group. Sum those counts across all gender groups, ignoring missing values and returning missing if there are none. Join each gender group to every total row whose total is present, keeping one row per match and dropping groups without a match; divide its count by that total to get its share. Average the shares across all such rows, ignoring missing values and returning missing if there are none. Join each share row to every average row whose average is present, keeping one row per match and dropping rows without a match; retain only rows whose share exceeds that average. Across the retained rows, return one summary row with, in order, the total of their counts, the average of their shares, and the average of each share minus that average share.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `disp` record; combine it with each `client` record for which the unique number (`client.client_id`) equals id number of client (`disp.client_id`), one combined record per match (a record without a match is dropped); group the kept records by client gender (`client.gender`); each group gives one result row; for each result row, return (1) client gender (`client.gender`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (3) of step 3 is greater than column (1) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B. Here A is column (3) of step 3; B is column (1) of step 4.
Step 6 (the answer). Start from the rows of step 5; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 5 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none).
</details>

### 01410c6c11 -- A2 S5, passed
**Natural (precise):** For each patient identifier in the lab test panels, count the records in its group (step 1). Sum those counts across all step 1 rows as one group, ignoring missing values and returning missing if there are none (step 2). Pair each step 1 row with every step 2 row whose sum is not missing, one row per match, dropping unmatched rows; calculate A ÷ B, where A is that patient's count and B is the step 2 sum (step 3). Average the step 3 ratios across all step 3 rows as one group, ignoring missing values and returning missing if there are none (step 4). Pair each step 3 row with every step 4 row whose average is not missing, one row per match, dropping unmatched rows. Return, in order, the patient identifier, its count, its ratio, and A − B, where A is that ratio and B is the step 4 average. Sort by A − B numerically, highest first with missing values last, and return the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `Laboratory` record; group the kept records by identification of the patient (`Laboratory.ID`); each group gives one result row; for each result row, return (1) identification of the patient (`Laboratory.ID`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B; order the result rows by A − B descending (missing last); keep only the first 10 rows. Here A is column (3) of step 3; B is column (1) of step 4.
</details>

### 00d65781cc -- A1 S6, passed
**Natural (precise):** For each product line, match every product whose unique product id equals the id of the product on the invoice line, producing one row per match and dropping unmatched lines. Group those rows by product color and count the rows in each group. Sum those counts over all color groups, ignoring missing counts and returning a missing sum if there are none. Combine each color group with every total row whose sum is present, one row per match, dropping groups without a match; for each, divide its count by that sum. Average the counts in these combined rows, ignoring missing counts and returning a missing average if there are none. Combine each of these rows with every average row whose average is present, one row per match, dropping rows without a match, and keep only those whose count exceeds the average. For each kept row, subtract the average from its count. Over all kept rows, return one summary row with, in order, the average count, the average of count divided by the sum, and the average of count minus the average count.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `Invoice_Line_Items` record; combine it with each `Products` record for which product id (`Products.product_id`) equals product id (`Invoice_Line_Items.product_id`), one combined record per match (a record without a match is dropped); group the kept records by product color (`Products.product_color`); each group gives one result row; for each result row, return (1) product color (`Products.product_color`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (2) of step 3 is greater than column (1) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B. Here A is column (2) of step 3; B is column (1) of step 4.
Step 6 (the answer). Start from the rows of step 5; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 5 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none).
</details>

### 00d645c60b -- A1 S4, passed
**Natural (precise):** For each manager_award record, join every player record whose unique player identifier code equals manager_award.player_id when compared as text character by character, producing one row per match and dropping unmatched records. Group by manager_award.player_id and batting hand, returning the identifier, batting hand, and record count for each group. Then group those rows by batting hand and sum their counts, ignoring missing values and returning missing when there are none. Sum those batting hand totals across all rows as one group, again ignoring missing values and returning missing when there are none. Pair each batting hand row with every overall-total row whose total is not missing, producing one row per match and dropping unmatched batting hand rows. Return, in order, batting hand, its total, and A ÷ B, where A is that batting hand total and B is the overall total.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `manager_award` record; combine it with each `player` record for which Unique identifier for each player (`player.player_id`) equals Player identifier (`manager_award.player_id`) (compared as text, character by character), one combined record per match (a record without a match is dropped); group the kept records by Player identifier (`manager_award.player_id`) and batting hand (`player.bats`); each group gives one result row; for each result row, return (1) Player identifier (`manager_award.player_id`); (2) batting hand (`player.bats`); (3) the number of records in the group.
Step 2. Start from the rows of step 1; group the kept records by column (2) of step 1; each group gives one result row; for each result row, return (1) column (2) of step 1; (2) the sum of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 2; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 2 in the group (missing values ignored; missing when there are none).
Step 4 (the answer). Start from the rows of step 2; combine it with the rows of step 3 for which it is not true that column (1) of step 3 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 2; (2) column (2) of step 2; (3) A ÷ B. Here A is column (2) of step 2; B is column (1) of step 3.
</details>

