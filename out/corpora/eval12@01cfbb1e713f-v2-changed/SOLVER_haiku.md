# Solver evaluation: `eval12@01cfbb1e713f-v2-changed`, solver haiku

The delivered corpus (11 tasks). One solver (batched agent, up to 6 rounds of exploration queries, then a final query), the task's own grader (tolerance, tie groups). 0 s.

| arm | tasks | correct | answered | executes |
|---|---|---|---|---|
| natural question | 11 | 10/11 (91%) | 11 | 10 |

## By step depth

| step depth | tasks | natural |
|---|---|---|
| S3 | 4 | 4/4 (100%) |
| S4 | 3 | 3/3 (100%) |
| S5 | 2 | 1/2 (50%) |
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
| agg > agg > baseline > agg | 1 | 0/1 (0%) |
| agg > baseline | 2 | 2/2 (100%) |
| agg > baseline > agg | 1 | 1/1 (100%) |
| agg > share | 2 | 2/2 (100%) |
| agg > share > baseline | 1 | 1/1 (100%) |
| agg > share > baseline > agg | 2 | 2/2 (100%) |

## By writer status

| writer status | tasks | natural |
|---|---|---|
| repaired after read-back | 11 | 10/11 (91%) |

## Wrong answers to read (a random 6)

- **227771660b** A2 S5 `agg > agg > baseline > agg`
  - Join each lab record to the patient with the same patient ID, one combined row per match, dropping lab records with no matching patient. Group by patient ID and patient sex. For each group compute X, the average of (serum albumin − total serum protein), and Y, the average of (activated partial thromboplastin time − prothrombin time). Missing values are ignored, and the result is missing if there are none. Then group those per-patient rows by sex. For each sex compute Xs, the average of X, and Ys, the average of Y, both ignoring missing values and missing if there are none. Let M be the average of Ys over all sexes, ignoring missing values. Combine the per-sex rows with M only when M is not m
