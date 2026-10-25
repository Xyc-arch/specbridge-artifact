# california_schools: why 20 UNKNOWN calculations are unknown

Causes: 1 = catalogue lacks it, 2 = propagation loses it, 3 = no supported interpretation.

| id | cause | reason |
|---|---|---|
| u1 | 3 | `round(Latitude,2) - round(Latitude,2)` is x - x, identically 0; it then feeds x/x, so nothing is being measured. |
| u2 | 3 | Subtracts `Free Meal Count (Ages 5-17)/1000 + 0.23` from a 0/5 flag on `Percent Eligible FRPM > 0.39` scaled by 5/1.5/1.5; a flag score minus a count in thousands has no meaning. |
| u3 | 3 | Product of `1 - (x/x)*(1-(x+230)/5)/1000` and `((x+230)/1.5/1000)*(1-(x+230)/1000)*0.75*3` over one free-meal count: an arbitrary chain of weights and offsets (with an x/x) giving students squared. |
| u4 | 3 | `Enrollment (K-12) * (1 - (NumTstTakr*15 + CASE(4/5/3)/0.25))`: test takers times 15 plus a score code, subtracted from 1, times enrollment; the operands are unrelated and the constants have no purpose. |
| u5 | 3 | Weighted sum of two free-meal counts in thousands (x10, x0.1875) times a sum of CASE flags that includes `Percent/Percent`; an arbitrary weight chain over counts and indicators. |
| u6 | 3 | `(p/0.3 + (p/0.3)/p) / p` over one share p = Percent Eligible Free (Ages 5-17); `(p/0.3)/p` is the constant 3.33, and dividing the sum by p again has no interpretation. |
| u7 | 3 | `1 - (CASE WHEN Latitude < 37.83 THEN 2 END / 0.1 / 3)`: a latitude cut turned into the constant 6.67 (or NULL) and subtracted from 1; constants only after the test. |
| u8 | 3 | `Percent Eligible FRPM (Ages 5-17)` divided by `Free Meal Count (K-12)` cubed over a share: students cubed has no meaning. |
| u9 | 3 | `((x+x)/5) / ((x+x)/5)` over the step output of a free-meal count is x/x, identically 1. |
| u10 | 2 | Numerically `FRPM Count (K-12) / (Enrollment (K-12) + 1)`, the catalogued FRPM rate (`rate` relation exists at the stored columns) with +1 in the denominator; the checker lost it because the +1 is spelled as `CAST(FRPM)/FRPM` (itself defect u18). |
| u11 | 3 | `CAST(s3.o1 AS REAL) / s3.o1` is x/x over a step output (an average share), identically 1. |
| u12 | 3 | `NumTstTakr + enroll12 + 303` adds a part to its whole (test takers are part_of enroll12, double counting), plus a score built by comparing the CDS code (an identifier) with string constants. |
| u13 | 3 | `1 - enroll12 * 5`: one minus five times an enrollment count; no quantity is "1" on this scale, so the result means nothing. |
| u14 | 3 | `1 - count/count^3 + share/(count^3/share)`: students to the minus two plus a share over students cubed; dimensionally and semantically empty. |
| u15 | 3 | `(Percent Eligible Free (K-12) / 0.3) * Free Meal Count (Ages 5-17)`: a K-12 share scaled by an unexplained 0.3 times an ages-5-17 count; share times count only means something when share and count are over the same base, and then without a 0.3 divisor. |
| u16 | 3 | `1 - |0.75 p| / ((N/N + q/|0.75 p|) - (N/N + q/|0.75 p|)*0.1)` with N = NumGE1500: contains x/x twice and mixes two shares through arbitrary weights. |
| u17 | 3 | `round(Enrollment*2*1.5) / Enrollment` is the constant 3, an x/x with a weight. |
| u18 | 3 | `CAST(FRPM Count)/FRPM Count + Enrollment (K-12)`: x/x (the constant 1) added to a count. |
| u19 | 3 | Nested CASE on CharterNum = '0756' (an identifier) and on `o3 = o3 - o3`, compared with `o3/o3 * (...)`; x - x and x/x throughout. |
| u20 | 3 | `(s3.o1 / s3.o1) / s3.o1` is 1 over an average share, reached through x/x; no stated purpose. |

## Counts

| cause | count |
|---|---|
| 1 catalogue lacks it | 0 |
| 2 propagation loses it | 1 |
| 3 no supported interpretation | 19 |

## Pattern

Almost every UNKNOWN is not a checker blind spot but a calculation the generator should never have built: x - x, x/x, identifiers used as numbers, counts cubed, and chains of weights like 0.75, 1.5 and 0.25 that no question could state. The catalogue is not the bottleneck here; the one case the checker lost (u10) was lost only because the generator spelled "+1" as `x/x`.
