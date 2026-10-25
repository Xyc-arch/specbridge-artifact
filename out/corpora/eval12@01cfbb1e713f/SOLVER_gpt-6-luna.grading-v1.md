# Solver evaluation: `eval12@01cfbb1e713f`, solver gpt-6-luna

The delivered corpus (382 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 742 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 382 | 333/382 (87%) | 382 | 354 |
| explicit instructions | 382 | 307/382 (80%) | 382 | 361 |

## Paired, same 382 tasks

| | natural right | natural wrong |
|---|---|---|
| explicit right | 274 | 33 |
| explicit wrong | 59 | 16 |

## By step depth

| step depth | tasks | natural | explicit |
|---|---|---|---|
| S3 | 100 | 91/100 (91%) | 99/100 (99%) |
| S4 | 86 | 73/86 (85%) | 73/86 (85%) |
| S5 | 100 | 89/100 (89%) | 71/100 (71%) |
| S6 | 96 | 80/96 (83%) | 64/96 (67%) |

## By arithmetic depth

| arithmetic depth | tasks | natural | explicit |
|---|---|---|---|
| A1 | 211 | 186/211 (88%) | 158/211 (75%) |
| A2 | 171 | 147/171 (86%) | 149/171 (87%) |

## By shape

| shape | tasks | natural | explicit |
|---|---|---|---|
| agg > agg > baseline | 11 | 7/11 (64%) | 6/11 (55%) |
| agg > agg > baseline > agg | 6 | 5/6 (83%) | 5/6 (83%) |
| agg > agg > baseline > baseline | 3 | 3/3 (100%) | 1/3 (33%) |
| agg > agg > share | 4 | 4/4 (100%) | 2/4 (50%) |
| agg > agg > share > baseline | 3 | 2/3 (67%) | 1/3 (33%) |
| agg > baseline | 60 | 57/60 (95%) | 59/60 (98%) |
| agg > baseline > agg | 68 | 60/68 (88%) | 63/68 (93%) |
| agg > baseline > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > baseline > baseline | 22 | 22/22 (100%) | 12/22 (55%) |
| agg > baseline > baseline > agg | 24 | 22/24 (92%) | 15/24 (62%) |
| agg > baseline > rank | 2 | 1/2 (50%) | 2/2 (100%) |
| agg > baseline > share | 2 | 1/2 (50%) | 1/2 (50%) |
| agg > baseline > share > agg | 2 | 1/2 (50%) | 1/2 (50%) |
| agg > rank | 2 | 2/2 (100%) | 2/2 (100%) |
| agg > share | 38 | 32/38 (84%) | 38/38 (100%) |
| agg > share > agg | 3 | 2/3 (67%) | 2/3 (67%) |
| agg > share > agg > agg | 3 | 3/3 (100%) | 3/3 (100%) |
| agg > share > agg > baseline | 1 | 1/1 (100%) | 1/1 (100%) |
| agg > share > baseline | 64 | 56/64 (88%) | 48/64 (75%) |
| agg > share > baseline > agg | 62 | 50/62 (81%) | 44/62 (71%) |
| agg > share > share | 1 | 1/1 (100%) | 0/1 (0%) |

## By writer status

| writer status | tasks | natural | explicit |
|---|---|---|---|
| passed | 273 | 241/273 (88%) | 233/273 (85%) |
| revised | 109 | 92/109 (84%) | 74/109 (68%) |

## Wrong answers to read (a random 6)

- **6782deeb9c** A2 S6 `agg > agg > share > baseline`
  - Join each player_award record to the player record where player.player_id equals player_award.player_id (compared as text, character by character); inner join, unmatched dropped. Group by player_award.player_id and batting hand (player.bats), counting records (C). Then group these rows by batting hand, summing C (H; missing ignored). Let T be the sum of H across all batting hands (missing ignored). For each batting hand compute R = H ÷ T. Let B be the average of R across batting hands (missing ignored). Pair each batting hand row with B, inner join, dropping rows if B is missing. Keep only rows where R is greater than B. Return: batting hand, H, R, and R − B.
- **b6c41d0861** A2 S5 `agg > share > baseline`
  - Inner join each driverStandings record to the race whose race identifier (races.raceId) equals driverStandings.raceId, dropping records with no match. Group by race name and count the joined records (n). Let T be the sum of n over all race names, so each race name's share is n ÷ T. Let AVG be the average of those shares over all race names. Keep only race names whose share is greater than AVG. Return race name, n, share, and share − AVG.
- **dabca577ba** A1 S3 `agg > baseline`
  - Join constructor results to races on race identifier and then to circuits on the race's circuit identifier (inner joins, dropping unmatched records). Group by constructorResults.raceId and circuit country, and return for each group: constructorResults.raceId, circuit country, the sum of constructor points in race, and the number of records. Also give the record count minus the average record count across all these groups, keeping only groups where the record count is greater than that average. Return the five columns, sorted by that difference from highest to lowest (missing values last), first 10 rows only.
- **a83a9b0bf3** A1 S6 `agg > share > baseline > agg`
  - Take each player_college record and inner-join it to the player record whose player.player_id equals player_college.player_id (compared as text, character by character; unmatched records dropped; one row per match). Group by birth country and count the records per country. Let T be the sum of these counts over all countries, and for each country compute share = count ÷ T. Let A be the country's count and B be the average of the per-country counts (missing ignored). Inner-join each country to B (dropped if B is missing) and keep only countries where A is greater than B, with difference A − B. Return one summary row with three values: (1) the total of the kept countries' counts; (2) the averag
- **6060d223ca** A1 S4 `agg > share > agg`
  - Join each playlist track to its track and then to the track's media type (inner joins, dropping records with no match). Group by track id and media type name, counting records in each group. Divide each group's count by the total of the counts across all groups (drop rows only if that total is missing). Then, for each media type name, return the name, the total of the group counts, and the average of the ratios.
- **93eb8cae64** A2 S6 `agg > share > baseline > agg`
  - For each race ID in the constructor results, sum the constructor points in race (S). Let T be the sum of S over all races, so each race's share is S ÷ T. Let AVG be the average of those shares over all races. Keep only races whose share is greater than AVG, and give each one a difference of share − AVG. Over those kept races, return one summary row with: the total of S, the average share, and the average difference.
