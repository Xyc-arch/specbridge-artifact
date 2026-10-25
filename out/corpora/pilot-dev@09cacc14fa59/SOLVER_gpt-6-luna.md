# Solver evaluation: `pilot-dev@09cacc14fa59`, solver gpt-6-luna

The delivered corpus (47 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 152 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 47 | 42/47 (89%) | 47 | 46 |
| explicit instructions | 47 | 41/47 (87%) | 47 | 45 |

## Paired, same 47 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 36 | 5 |
| explicit wrong | 6 | 0 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 12 | 11/12 (92%) | 12/12 (100%) |
| S4 | 10 | 10/10 (100%) | 9/10 (90%) |
| S5 | 14 | 12/14 (86%) | 11/14 (79%) |
| S6 | 11 | 9/11 (82%) | 9/11 (82%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 25 | 22/25 (88%) | 23/25 (92%) |
| A2 | 22 | 20/22 (91%) | 18/22 (82%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 1 | 1/1 (100%) | 0/1 (0%) |
| agg > baseline | 8 | 8/8 (100%) | 8/8 (100%) |
| agg > baseline > agg | 9 | 9/9 (100%) | 9/9 (100%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 5 | 4/5 (80%) | 2/5 (40%) |
| agg > baseline > baseline > agg | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > share | 4 | 3/4 (75%) | 4/4 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 8 | 7/8 (88%) | 8/8 (100%) |
| agg > share > baseline > agg | 7 | 6/7 (86%) | 5/7 (71%) |
| agg > share > share | 1 | 1/1 (100%) | 1/1 (100%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 37 | 33/37 (89%) | 33/37 (89%) |
| revised | 10 | 9/10 (90%) | 8/10 (80%) |

## Wrong answers to read (a random 6)

- **8ac7dd4f7e** A2 S6 `agg > baseline > baseline > agg`
  - Step 1: Join each match to the player record whose player identifier equals the match's loser player ID (inner join; unmatched matches dropped, one row per match). Group by loser player ID and playing hand; return (1) loser player ID, (2) playing hand, (3) the average loser age (missing ignored; missing if none). Step 2: over all step-1 rows as one group, return (1) the average of step 1's column (3) (missing ignored). Step 3: join each step-1 row to the step-2 row where step 2's column (1) is not missing (inner join; unmatched dropped); return (1) step 1's column (1), (2) step 1's column (2), (3) step 1's column (3), (4) step 1's column (3) minus step 2's column (1). Step 4: group step 3 by
- **f90379a5ce** A1 S3 `agg > share`
  - Group articles by the occupation of their author, matching each article to the user whose user identifier equals the article's author's user id; articles with no matching user are dropped. For each occupation, compute the average article content freshness score (missing values ignored) and the total of media elements (missing values ignored). Then compute the overall sum of those per-occupation media element totals (missing values ignored). Return one row per occupation, keeping only occupations that have a non-missing overall total (an inner join to that overall total, one row per match), with: occupation, average content freshness score, total media elements, and total media elements divid
- **4198b33ff8** A2 S6 `agg > share > baseline > agg`
  - Count atoms per chemical element (E1: element, count). Let T be the sum of the counts. For each element compute share = count ÷ T (only if T is not missing). Let M be the average of share over all elements. Keep only elements whose share is greater than M, and compute diff = share − M. Return one summary row with three outputs: (1) the total of count over the kept elements, (2) the average of share over the kept elements, (3) the average of diff over the kept elements.
- **eafd676353** A1 S5 `agg > share > baseline`
  - For each molecule id in bond, count the bond records (call this count A). Let S be the sum of these counts over all molecules, and let R = A ÷ S for each molecule. Let B be the average of R across all molecules. Return the molecule id, A, R, and R ÷ B, sorted by R ÷ B highest first (missing values last), and only the first 10 rows.
- **7fce510d39** A1 S5 `agg > baseline > baseline`
  - Step 1: for each loser country code, compute the average winner age, ignoring missing values. Step 2: the overall average of those per-country averages. Step 3: keep countries with a non-missing step 2 value and an average winner age greater than it, giving loser country code, average winner age, and average winner age minus the step 2 value. Step 4: the average of the step 3 average winner ages. Then pair each step 3 row with the step 4 value (inner join, requiring it to be non-missing, one row per match), and return the loser country code, the average winner age, the step 3 difference from the step 2 value, and the average winner age minus the step 4 value.
