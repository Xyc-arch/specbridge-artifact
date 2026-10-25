# california_schools: review of 20 delivered queries

Question per query: does it express a coherent calculation over the target data, with its parameters and assumptions explicit?

| query id | verdict | cause (if not yes) | reason |
|---|---|---|---|
| california_schools-1 | no | arbitrary | `1 - enroll12 + FRPM Count * 2` adds students to a constant and doubles a count for no reason, and `sname = AdmEmail3` compares a school name to an email address. |
| california_schools-2 | no | arbitrary | `WHERE Percent Eligible FRPM = Charter School Number` compares a fraction with an identifier, and the output is a made-up code (4 or 0). |
| california_schools-3 | no | arbitrary | `NumGE1500 / AvgScrRead` divides a head count by a score, and `o0 / o0` is always 1. |
| california_schools-4 | yes | | Lists test takers per school with its district code, sorted by number of test takers. |
| california_schools-5 | yes | | Free-meal count for schools whose FRPM share is above 0.69. |
| california_schools-6 | no | arbitrary | `Latitude * (Percent FRPM / Free Meal Count)` uses a coordinate as a quantity and divides a share by a head count. |
| california_schools-7 | no | arbitrary | Long chain of weights and CASE codes: a District Code compared with 69625 as if it were a number, plus `o1/o1` and `o1 - o1`. |
| california_schools-8 | yes | | Plain lookup of charter number, open date, magnet status and free-meal count for schools that have SAT rows. |
| california_schools-9 | no | arbitrary | `0 - Free Meal Count + (... * Latitude) + Enrollment*0.75 ... + Longitude*0.75` mixes students, shares and coordinates; also `CASE - same CASE` and `coalesce(CDSCode, 0)`. |
| california_schools-10 | uncertain | arbitrary | `NCESSchool > '09508'` filters on a text ID by string order, which no sensible question states. |
| california_schools-11 | no | arbitrary | Everything is built on `Free Meal Count / Free Meal Count` (always 1), then sqrt, log and weights applied to that constant. |
| california_schools-12 | uncertain | lost in propagation | `CAST(LastUpdate AS REAL)` turns a date into a bare number (effectively the year) with no stated purpose. |
| california_schools-13 | uncertain | arbitrary | Mostly a sensible filtered lookup, but `rtype < 'S'` uses string order on a type code to mean `rtype = 'D'` without saying so. |
| california_schools-14 | no | arbitrary | `NumGE1500 / NumGE1500` is always 1, then multiplied by `AvgScrWrite * 2 * 3 / 10`, a chain of weights with no meaning. |
| california_schools-15 | no | arbitrary | The meaningful share `NumGE1500 / NumTstTakr` is multiplied by Latitude and divided by 0.25, and the o3 expression cancels to a constant. |
| california_schools-16 | no | arbitrary | `School Code BETWEEN CAST(School Code AS INTEGER) AND GSoffered` compares an ID with a grade-span text, and `3 / (1 - Percent FRPM)` has no purpose. |
| california_schools-17 | no | arbitrary | `Free Meal Count / (1 - Free Meal Count)` and `Percent Free / (0 - Enrollment)` subtract head counts from constants, which is meaningless. |
| california_schools-18 | no | arbitrary | Adds Latitude to SAT scores and head counts (`AvgScrMath*0.75/5 + Latitude + NumGE1500*3`), and compares EdOpsCode to 'HOMHOS' by string order. |
| california_schools-19 | no | arbitrary | o1 sums the square of `round(FRPM Count/1000,2)*10` plus a `+ 0` step, and `CAST(AVG(percent) AS INTEGER)` is always 0 (the other outputs are fine). |
| california_schools-20 | no | arbitrary | `power(Free Meal Count, 1.5)` raises a head count to an arbitrary power, and `CAST(OpenDate AS REAL)` treats a date as a number. |

## Totals

- yes: 3
- uncertain: 3
- no: 14
- Causes (17 not-yes): arbitrary 16, lost in propagation 1, missing evidence 0.

## Dominant pattern

Almost every query with arithmetic is incoherent, and the reason is not missing catalogue facts. The generator stacks arbitrary weights (`*0.75`, `/0.25`, `*3`), subtracts quantities from constants (`1 - count`), divides a value by itself, and treats coordinates, IDs, emails and dates as numbers. Only the plain lookups with simple filters (4, 5, 8) are coherent. The catalogue already holds the facts that would give meaning to the few meaningful sub-expressions (for example NumGE1500/NumTstTakr, FRPM Count/1000), and those end up inside meaningless outer operations.
