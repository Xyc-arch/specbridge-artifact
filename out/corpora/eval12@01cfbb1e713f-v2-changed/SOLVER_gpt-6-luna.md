# Solver evaluation: `eval12@01cfbb1e713f-v2-changed`, solver gpt-6-luna

The delivered corpus (11 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 60 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 11 | 10/11 (91%) | 11 | 10 |

## By step depth

| step depth | tasks | natural |
|---|---|---|
| S3 | 4 | 4/4 (100%) |
| S4 | 3 | 2/3 (67%) |
| S5 | 2 | 2/2 (100%) |
| S6 | 2 | 2/2 (100%) |

## By arithmetic depth

| arithmetic depth | tasks | natural |
|---|---|---|
| A1 | 6 | 6/6 (100%) |
| A2 | 5 | 4/5 (80%) |

## By shape

| shape | tasks | natural |
|---|---|---|
| agg > agg > baseline | 2 | 2/2 (100%) |
| agg > agg > baseline > agg | 1 | 1/1 (100%) |
| agg > baseline | 2 | 2/2 (100%) |
| agg > baseline > agg | 1 | 0/1 (0%) |
| agg > share | 2 | 2/2 (100%) |
| agg > share > baseline | 1 | 1/1 (100%) |
| agg > share > baseline > agg | 2 | 2/2 (100%) |

## By writer status

| writer status | tasks | natural |
|---|---|---|
| repaired after read-back | 11 | 10/11 (91%) |

## Wrong answers to read (a random 6)

- **e2ae5e3b8f** A2 S4 `agg > baseline > agg`
  - Join each `appearances` record to every `player` record whose unique player identifier (`player.player_id`) equals `appearances.player_id`, compared as text character by character. Each match gives one combined record, and `appearances` records with no matching player are dropped. Group the combined records by `appearances.player_id` and death country (`player.death_country`), so each group is one row. For each group, compute S as the sum over the group's records of (games at first base − games in center field). A record where either value is missing gives a missing difference, and missing differences are ignored. S is missing if the group has no non-missing differences. Compute T as the ave
