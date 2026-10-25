# thrombosis_prediction: why 20 UNKNOWN calculations are unknown

Judged from the SQL and `catalogues/thrombosis_prediction.json`, not from the automated verdicts.

| id | cause (1/2/3) | reason |
|---|---|---|
| u1 | 3 | `1 - COUNT(*)` subtracts a row count from the constant 1; no quantity is "one minus a count of RVVT groups". |
| u2 | 3 | `o9 / (CASE ... /0.5/0.2)` divides a sum of a C3 term and doubled FG by a CASE whose conditions are tautologies on o9 (a constant 5), an arbitrary composition. |
| u3 | 3 | A product of `abs(2)`-derived constants: arithmetic on constants only, no column under it. |
| u4 | 3 | `COUNT(*) / abs(COUNT(*) * (1 - CASE on Laboratory.ID >= 4843434 ... * 10))` uses the patient identifier as a threshold quantity inside a count ratio. |
| u5 | 3 | `1 - round(...)` over CASE expressions whose condition `x BETWEEN x AND x` is always true: constants dressed as data. |
| u6 | 3 | `power(ALP, 1.5) + (1 - CASE ...)*3` raises a U/L enzyme activity to 1.5 and adds a tautological score; ALP's unit is catalogued, but no fact makes this meaningful. |
| u7 | 3 | `CASE(Symptoms > 'finger ulcer' ...)*0.2 * round(same CASE)` squares a score built from a lexicographic comparison of free-text symptoms. |
| u8 | 3 | `PT + ((1 - PT/11)*(ALB+HGB)*5*0.75 + TAT2*0.1)` adds seconds, g/dL and ng/mL; the catalogue has all three units and they are unrelated. |
| u9 | 3 | `Thrombosis / (aCL IgG*10*5)` divides a thrombosis severity grade by an antibody titre in GPL units; no relation or domain meaning connects them. |
| u10 | 3 | `(1 - CASE on Laboratory.ID ... *10) + COUNT(*)` adds an identifier-threshold score to a row count. |
| u11 | 3 | Same `1 - COUNT(*)` node as u1 (same query). |
| u12 | 3 | A ratio of sums of ANA^2.5, aCL IgM/2.1, ANA*aCL IgA and Thrombosis/aCL IgG: titer, three antibody units and a grade mixed; the aCL "comparable" relations do not cover ANA or Thrombosis. |
| u13 | 3 | `HGB / (TG + UN)` divides hemoglobin by triglyceride plus urea nitrogen; both are mg/dL but belong to different panels with no relation, so the sum and ratio mean nothing. |
| u14 | 3 | `(ANA/16)*aCL IgG*1.5 + aCL IgG` adds titer x GPL units to GPL units; units are catalogued and incompatible. |
| u15 | 3 | Same `1 - COUNT(*)` node as u1 (same query). |
| u16 | 2 | `FG * (CASE WHEN ANA Pattern > 'p' THEN 1 ELSE 1 END * 2)` is fibrinogen x 2 (the CASE is constant 1); FG's mg/dL is catalogued, but the checker could not see through the constant CASE. |
| u17 | 3 | `COUNT*(1-COUNT)^2*0.1 * (x / ((0/0.5)*0.25))` is a cubic in a row count divided by zero. |
| u18 | 3 | `(1 - COUNT(*)) * (1 - COUNT(*))` squares one-minus-a-count. |
| u19 | 3 | `ANA * power(round(ANA),1.5) / 0.25` is ANA to the power 2.5, which no titer interpretation supports. |
| u20 | 3 | `1 - CASE WHEN a > a THEN 0 ELSE 0 END + ...` builds on always-false/always-zero CASEs over a free-text score. |

## Counts

| cause | n |
|---|---|
| 1 catalogue lacks it | 0 |
| 2 propagation loses it | 1 |
| 3 no supported interpretation | 19 |

## Pattern

The UNKNOWN pool is not a catalogue gap: 19 of 20 nodes are incoherent on the facts already present (counts squared or subtracted from 1, identifiers as thresholds, constants-only chains, tautological CASEs, sums of unrelated units), and several come from the same few queries (attempt 102 alone supplies u1, u5, u11, u15, u17 and u18). The catalogue is not what is missing here; the calculations cannot be supported because they have no meaning, and they should be refused where they are drawn, not waiting for a fact that would support them.
