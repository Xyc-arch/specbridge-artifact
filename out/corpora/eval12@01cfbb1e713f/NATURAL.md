# Precise natural questions for `eval12@01cfbb1e713f` (tasks_paired.jsonl)

Writer: frozen lm-writer (sonnet, input language+facts, one revision), ported to specbridge.comm.verbal.precise; batches of 8 per database, 6 concurrent. SQL, answers and graders unchanged. Delivered: corpus.jsonl, the rendered tasks with their natural question and explicit instructions.

**Natural coverage: 382 of 384 tasks** (passed on round 1: 273; revised and accepted: 109; deterministic, no model: 0). **Not rendered: 2** (the draft failed review twice or a symbol was undefined; the task is not delivered). **Missing output: 0** (the writer returned no draft even after the retry; not delivered). All 384 tasks accounted for: True.

Runtime 1063 s; model calls 585 (write 58, review 495, revise 32; of these, 0 retries after a missing output); tokens in 6126611, out 289738; per natural question written by the model: 1.5 calls.

Review: one task per call.

Review failures by requirement (all rounds, before revision too): {'steps': 80, 'definition B': 28, 'output 4': 26, 'join 1': 24, 'definition A': 21, 'output 3': 21, 'output 1': 10, 'ordering': 10, 'record filter': 7, 'output 2': 5, 'output 5': 1, 'grouping': 1}

The reviewer's verdict is evidence, not proof. The language resource for a database without one falls back to the catalogue's column labels.

## A random sample of paired tasks

### 7690ebdcab -- A2 S5, passed
**Natural (precise):** Step 1: Join each advanced behavior record to each transaction record whose trade-day transaction record id equals the advanced behavior record's linked transaction record id. Then join to each trader record whose trader account id equals the transaction record's trader account id. Compare both joins as text, character by character. Drop records with no match, and keep one row per match. Group by linked transaction record id and trader type. For each group return the linked transaction record id, the trader type, and the number of records in the group.
Step 2: Group the step 1 rows by trader type. Return the trader type and the sum of step 1's column 3 (missing values ignored).
Step 3: Join the step 1 rows to the step 2 rows where the trader type is equal, compared as text. Drop rows with no match. Return step 1's columns 1, 2 and 3. Also return a fourth column: step 1's column 3 ÷ step 2's sum for that trader type.
Step 4: Treat all step 3 rows as one group and return the average of step 3's column 4 (missing values ignored).
Final: Join the step 3 rows to the step 4 row where step 4's value is not missing. This is an inner join, so step 3 rows with no match are dropped, and there is one row per match. Return (1) step 3's column 1, (2) column 2, (3) column 3, (4) column 4, (5) step 3's column 4 − step 4's value. Sort by that fifth value, highest first, with missing values last. Return only the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `advancedbehavior` record; combine it with each `transactionrecord` record for which transreg (`transactionrecord.transreg`) equals translink (`advancedbehavior.translink`) (compared as text, character by character), one combined record per match (a record without a match is dropped); combine it with each `trader` record for which tradereg (`trader.tradereg`) equals trdref (`transactionrecord.trdref`) (compared as text, character by character), one combined record per match (a record without a match is dropped); group the kept records by translink (`advancedbehavior.translink`) and trader type (`trader.tradekind`); each group gives one result row; for each result row, return (1) translink (`advancedbehavior.translink`); (2) trader type (`trader.tradekind`); (3) the number of records in the group.
Step 2. Start from the rows of step 1; group the kept records by column (2) of step 1; each group gives one result row; for each result row, return (1) column (2) of step 1; (2) the sum of column (3) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which column (2) of step 1 equals column (1) of step 2 (compared as text, character by character), one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) column (3) of step 1; (4) A ÷ B. Here A is column (3) of step 1; B is column (2) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (4) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) column (4) of step 3; (5) A − B; order the result rows by A − B descending (missing last); keep only the first 10 rows. Here A is column (4) of step 3; B is column (1) of step 4.
</details>

### 351fb7579b -- A2 S6, passed
**Natural (precise):** Count customers grouped by support representative id (N). Compute the total of N over all groups; for each group, share = N divided by that total. Compute the average share (missing ignored). Keep only groups whose share is greater than the average share, with difference = share minus average share. Over these kept groups, return one row with: the total of N, the average of share, and the average of the difference.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `Customer` record; group the kept records by Support Rep Id (`Customer.SupportRepId`); each group gives one result row; for each result row, return (1) Support Rep Id (`Customer.SupportRepId`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5. Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (3) of step 3 is greater than column (1) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B. Here A is column (3) of step 3; B is column (1) of step 4.
Step 6 (the answer). Start from the rows of step 5; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 5 in the group (missing values ignored; missing when there are none); (2) the average of column (3) of step 5 in the group (missing values ignored; missing when there are none); (3) the average of column (4) of step 5 in the group (missing values ignored; missing when there are none).
</details>

### da10959f8c -- A2 S5, passed
**Natural (precise):** Step 1: group telescopes by observstation; return observstation and the number of telescopes in each group. Step 2: the sum of the step 1 counts (missing ignored; missing if none). Step 3: pair each step 1 row with the step 2 row, only if the step 2 sum is not missing (inner join; unmatched dropped); return observstation, count, and count divided by the step 2 sum. Step 4: the average of the step 3 third column over all step 3 rows (missing ignored; missing if none). Final: pair each step 3 row with the step 4 row, only if the step 4 value is not missing (inner join, one row per match; unmatched step 3 rows dropped). Let A be step 3's third column and B be the step 4 value. Return step 3's first, second and third columns, and A − B. Sort by A − B as a number, highest first, missing values last, and return only the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `telescopes` record; group the kept records by observstation (`telescopes.observstation`); each group gives one result row; for each result row, return (1) observstation (`telescopes.observstation`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B; order the result rows by A − B descending (missing last); keep only the first 10 rows. Here A is column (3) of step 3; B is column (1) of step 4.
</details>

### bf298fafe5 -- A2 S3, passed
**Natural (precise):** For each event status of budget records, compute the average of (amount budgeted − amount spent), ignoring missing values. Call this the per-status average. Let G be the average of the per-status averages across all statuses (missing ignored). Return, for each event status with a non-missing G, (1) event status, (2) its per-status average, (3) per-status average − G.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `budget` record; group the kept records by event status (`budget.event_status`); each group gives one result row; for each result row, return (1) event status (`budget.event_status`); (2) the average of A − B in the group (missing values ignored; missing when there are none). Here A is amount budgeted (`budget.amount`); B is amount spent in category (`budget.spent`).
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3 (the answer). Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A − B. Here A is column (2) of step 1; B is column (1) of step 2.
</details>

### 96d38a34f5 -- A2 S5, passed
**Natural (precise):** Count order executions per original order reference. Let T be the total of these counts across all order references. For each order reference, compute R = its count ÷ T. Let M be the average of R over all order references (ignoring missing values). Pair each order reference row with M (inner join; rows with missing M are dropped, one row per match). Keep only rows where R is greater than M. Return: original order reference, its count, R, and R − M, sorted by R − M highest first with missing values last, limited to the first 10 rows.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `orderexecutions` record; group the kept records by ordersmark (`orderexecutions.ordersmark`); each group gives one result row; for each result row, return (1) ordersmark (`orderexecutions.ordersmark`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); keep only the records for which column (3) of step 3 is greater than column (1) of step 4; for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B; order the result rows by A − B descending (missing last); keep only the first 10 rows. Here A is column (3) of step 3; B is column (1) of step 4.
</details>

### 0ffb817b41 -- A2 S5, passed
**Natural (precise):** Step 1: group telescopes by power source status; return power source status and the number of telescopes in each group. Step 2: the sum of the step 1 counts (missing ignored; missing if none). Step 3: pair each step 1 row with the step 2 row, only if the step 2 sum is not missing (inner join; unmatched dropped); return power source status, count, and count divided by the step 2 sum. Step 4: the average of the step 3 third column over all step 3 rows (missing ignored; missing if none). Final: pair each step 3 row with the step 4 row, only if the step 4 value is not missing (inner join, one row per match; unmatched step 3 rows dropped). Let A be step 3's third column and B be the step 4 value. Return step 3's first, second and third columns, and A − B.

<details><summary>Explicit instructions</summary>

Step 1. Start from each `telescopes` record; group the kept records by power source status (`telescopes.powerstatus`); each group gives one result row; for each result row, return (1) power source status (`telescopes.powerstatus`); (2) the number of records in the group.
Step 2. Start from the rows of step 1; all kept records form one group, which gives one result row; for each result row, return (1) the sum of column (2) of step 1 in the group (missing values ignored; missing when there are none).
Step 3. Start from the rows of step 1; combine it with the rows of step 2 for which it is not true that column (1) of step 2 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 1; (2) column (2) of step 1; (3) A ÷ B. Here A is column (2) of step 1; B is column (1) of step 2.
Step 4. Start from the rows of step 3; all kept records form one group, which gives one result row; for each result row, return (1) the average of column (3) of step 3 in the group (missing values ignored; missing when there are none).
Step 5 (the answer). Start from the rows of step 3; combine it with the rows of step 4 for which it is not true that column (1) of step 4 is missing, one combined record per match (a record without a match is dropped); for each kept record, return (1) column (1) of step 3; (2) column (2) of step 3; (3) column (3) of step 3; (4) A − B. Here A is column (3) of step 3; B is column (1) of step 4.
</details>

