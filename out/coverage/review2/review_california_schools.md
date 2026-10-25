# california_schools: fresh review of 20 delivered queries

Question: does the query express a coherent calculation over the target data, with its parameters and assumptions explicit?

| id | verdict | has arithmetic (y/n) | cause | reason |
|---|---|---|---|---|
| 1 | yes | n | - | Lists education option code, SAT test takers and an administrator name per school, ordered by option code; one-to-one join on CDS code. |
| 2 | no | y | arbitrary | `sqrt(CURRENT_DATE)` is arithmetic on a date constant; the rest is a list of identifiers. |
| 3 | no | y | arbitrary | Groups by an administrator's first name, computes x/x of a name-comparison CASE, and compares a percent rank with a name, an email and a last name. |
| 4 | no | y | arbitrary | Scores built from string comparisons of street addresses (`StreetAbr BETWEEN District AND cds`), `FRPM Count / round(FRPM Count)` (x/x), and enrollment x 0.5 added to a flag score. |
| 5 | yes | n | - | Lists district code, FRPM and free-meal shares, enrollment and district type, first 100 by district type; the constant column `1` is harmless. |
| 6 | no | y | arbitrary | Output o4 is `FRPM Count / FRPM Count` (x/x) when the count exceeds 502, i.e. a flag written as a division, and the query is ordered by it. |
| 7 | no | y | arbitrary | Adds the high-scorer rate `NumGE1500/enroll12` to that rate divided again by enroll12, then divides these by each other and adds x/x; only the first ratio has a meaning. |
| 8 | no | y | arbitrary | Casts CharterNum (an identifier) to a number and builds a product and ratio chain from a 1/-3 flag on whether the website is 'www.nmusd.us'. |
| 9 | yes | n | - | Free-meal count (K-12) for schools at one stated longitude, ordered by the count; the longitude is a parameter a question could state. |
| 10 | no | y | arbitrary | `(FreeMeal/78)/1000 - (1 - (FreeMeal/78)/(FreeMeal/78))` over 0.25: an x/x term, and the 78 and 0.25 have no purpose. |
| 11 | no | y | arbitrary | The filter is a long chain of weighted free-meal counts, CASE flags, `NumGE1500/NumGE1500` and `Percent/Percent`; only the FRPM rate output o1 is meaningful. |
| 12 | no | y | arbitrary | A 0/5 flag scaled by 5/1.5/1.5 minus free meals in thousands plus 0.23; outputs include that value minus itself, and sqrt of it is compared with OpenDate. |
| 13 | no | y | arbitrary | Weight chain over one free-meal count (x3x3, +230, /1.5, x0.75, x/x) filtered to equal 50.92 and also be greater than 50.92, so no row can pass. |
| 14 | no | n | arbitrary | Filters `Longitude < Phone`, comparing a coordinate with a phone number string. |
| 15 | no | y | arbitrary | Groups by AdmFName3 (a name), casts the name to a number and does arithmetic on it; the aggregate is a weight chain over shares and counts with x/x. |
| 16 | uncertain | y | arbitrary | High-scorer count in thousands (a plausible conversion) is multiplied by 0.1 with no stated purpose; the rest is a plain list. |
| 17 | no | y | arbitrary | Test takers x10/1000 +0.83, summed three times, plus a CASE score over 0.1, compared for equality with LastUpdate (a date). |
| 18 | no | y | arbitrary | Averages `Latitude - ClosedDate`, subtracting a date from a coordinate, then squares it. |
| 19 | yes | n | - | Lists CDS code, last update, free-meal count and longitude, first 100 by free-meal count; one-to-one joins. |
| 20 | yes | n | - | Lists education option code, latitude and an administrator's last name, ordered by that name; one-to-one join. |

## Counts

| | yes | uncertain | no |
|---|---|---|---|
| all 20 | 5 | 1 | 14 |
| with arithmetic (14) | 0 | 1 | 13 |
| without arithmetic (6) | 5 | 0 | 1 |

Causes among uncertain/no (15): arbitrary 15, missing evidence 0, lost in propagation 0.

## Pattern

Every query that contains arithmetic is incoherent or near it: x/x and x - x, identifiers, names, phone numbers and dates used as quantities, and chains of 0.75/1.5/0.25 weights, so none of the 14 arithmetic queries reads as a calculation a question could ask for. The five "yes" verdicts are all plain lists with at most a stated filter, which means the delivered corpus's coherent part carries no arithmetic at all.
