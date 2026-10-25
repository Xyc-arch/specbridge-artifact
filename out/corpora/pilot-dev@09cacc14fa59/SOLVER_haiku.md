# Solver evaluation: `pilot-dev@09cacc14fa59`, solver haiku

The delivered corpus (47 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 481 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 47 | 43/47 (91%) | 47 | 47 |
| explicit instructions | 47 | 45/47 (96%) | 47 | 46 |

## Paired, same 47 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 42 | 3 |
| explicit wrong | 1 | 1 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 12 | 12/12 (100%) | 12/12 (100%) |
| S4 | 10 | 8/10 (80%) | 8/10 (80%) |
| S5 | 14 | 13/14 (93%) | 14/14 (100%) |
| S6 | 11 | 10/11 (91%) | 11/11 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 25 | 24/25 (96%) | 24/25 (96%) |
| A2 | 22 | 19/22 (86%) | 21/22 (95%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 1 | 0/1 (0%) | 0/1 (0%) |
| agg > baseline | 8 | 8/8 (100%) | 8/8 (100%) |
| agg > baseline > agg | 9 | 8/9 (89%) | 8/9 (89%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 5 | 5/5 (100%) | 5/5 (100%) |
| agg > baseline > baseline > agg | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > share | 4 | 4/4 (100%) | 4/4 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 8 | 7/8 (88%) | 8/8 (100%) |
| agg > share > baseline > agg | 7 | 7/7 (100%) | 7/7 (100%) |
| agg > share > share | 1 | 1/1 (100%) | 1/1 (100%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 37 | 35/37 (95%) | 36/37 (97%) |
| revised | 10 | 8/10 (80%) | 9/10 (90%) |

## Wrong answers to read (a random 6)

- **ab6ab77478** A1 S4 `agg > baseline > agg`
  - Join each session to the user whose user identifier equals the session's user id (sessions with no matching user are dropped). Group by user type and compute, per user type, the average recommendations shown (missing values ignored) and the average of pages viewed divided by session duration (missing values ignored). Compute also the average of the per-type average recommendations shown across all user types (missing values ignored). Keep only the user types whose average recommendations shown is greater than that overall average (inner join, one row per match), and give for each: user type, average recommendations shown, average pages-viewed-per-duration, and the difference between the type
- **1de658b99c** A2 S4 `agg > agg > baseline`
  - Join each session to its user (users.userkey = sessions.userel; inner join, sessions with no matching user are dropped, one row per match). Group by user id of the session (sessions.userel) and user type, and for each group compute the average UTC time zone offset and the average of pages viewed ÷ session duration (missing values ignored in both averages; missing when none). Then group those rows by user type and compute, per user type, the average of the time zone offset averages and the average of the (pages viewed ÷ session duration) averages (missing values ignored; missing when none). Let A be a user type's average of the (pages viewed ÷ session duration) averages, and let B be the over
- **8ac7dd4f7e** A2 S6 `agg > baseline > baseline > agg`
  - Step 1: Join each match to the player record whose player identifier equals the match's loser player ID (inner join; unmatched matches dropped, one row per match). Group by loser player ID and playing hand; return (1) loser player ID, (2) playing hand, (3) the average loser age (missing ignored; missing if none). Step 2: over all step-1 rows as one group, return (1) the average of step 1's column (3) (missing ignored). Step 3: join each step-1 row to the step-2 row where step 2's column (1) is not missing (inner join; unmatched dropped); return (1) step 1's column (1), (2) step 1's column (2), (3) step 1's column (3), (4) step 1's column (3) minus step 2's column (1). Step 4: group step 3 by
- **7adb1feb1d** A2 S5 `agg > share > baseline`
  - Join interactions to recommendations (reckey = the interaction's related recommendation id), then to articles (artkey = artlink), then to users (userkey = authref); all inner joins, dropping unmatched, one row per match. Group by related recommendation id and subscription status (of the article's author) and count records (call it C). Let T be the sum of C over all groups. For each group compute R = C ÷ T (rows with T missing dropped). Then group these rows by subscription status and compute the average R (call it S). Join each (recommendation, status, C, R) row to the status average S on subscription status equal as text (inner join, one row per match). Return related recommendation id, sub
