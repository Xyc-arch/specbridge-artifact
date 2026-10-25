# Solver evaluation: `pilot-dev@09cacc14fa59`, solver sonnet

The delivered corpus (47 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 76 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 47 | 46/47 (98%) | 47 | 47 |
| explicit instructions | 47 | 47/47 (100%) | 47 | 47 |

## Paired, same 47 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 46 | 1 |
| explicit wrong | 0 | 0 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 12 | 12/12 (100%) | 12/12 (100%) |
| S4 | 10 | 10/10 (100%) | 10/10 (100%) |
| S5 | 14 | 14/14 (100%) | 14/14 (100%) |
| S6 | 11 | 10/11 (91%) | 11/11 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 25 | 25/25 (100%) | 25/25 (100%) |
| A2 | 22 | 21/22 (95%) | 22/22 (100%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline | 8 | 8/8 (100%) | 8/8 (100%) |
| agg > baseline > agg | 9 | 9/9 (100%) | 9/9 (100%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 5 | 5/5 (100%) | 5/5 (100%) |
| agg > baseline > baseline > agg | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 8 | 8/8 (100%) | 8/8 (100%) |
| agg > share > baseline > agg | 7 | 7/7 (100%) | 7/7 (100%) |
| agg > share > share | 1 | 1/1 (100%) | 1/1 (100%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 37 | 37/37 (100%) | 37/37 (100%) |
| revised | 10 | 9/10 (90%) | 10/10 (100%) |

## Wrong answers to read (a random 6)

- **8ac7dd4f7e** A2 S6 `agg > baseline > baseline > agg`
  - Step 1: Join each match to the player record whose player identifier equals the match's loser player ID (inner join; unmatched matches dropped, one row per match). Group by loser player ID and playing hand; return (1) loser player ID, (2) playing hand, (3) the average loser age (missing ignored; missing if none). Step 2: over all step-1 rows as one group, return (1) the average of step 1's column (3) (missing ignored). Step 3: join each step-1 row to the step-2 row where step 2's column (1) is not missing (inner join; unmatched dropped); return (1) step 1's column (1), (2) step 1's column (2), (3) step 1's column (3), (4) step 1's column (3) minus step 2's column (1). Step 4: group step 3 by
