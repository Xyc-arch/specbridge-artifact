# thrombosis_prediction: fresh review of 20 delivered queries

Question: does this query express a coherent calculation over the target data, with its parameters and assumptions explicit? Judged from the SQL and `catalogues/thrombosis_prediction.json`, not from the automated verdicts.

| id | verdict | has arithmetic (y/n) | cause | reason |
|---|---|---|---|---|
| 1 | no | y | arbitrary | Filters on `(100 - HCT) * (UN/CRE) * 3 = 3714.0` (plasma fraction times BUN/creatinine ratio, tested for exact equality) and on text `SSB > '0'`, `CENTROMEA >= 'negative'` (lexicographic). |
| 2 | no | y | arbitrary | `FG + FG`, `(1 - C3/42) * (1 - CASE ... THEN 0 ELSE 0)`, CASEs comparing numbers to text `SM` and `U-PRO`, and tautological CASEs dividing o9: x - x style chains. |
| 3 | no | y | arbitrary | `ALB / 3.7 / 2 / 2` and `ALB - DENSE_RANK()` subtract a row rank from albumin in g/dL. |
| 4 | no | y | arbitrary | `HGB / (aCL IgG * 0.75) > 20.83` divides hemoglobin by an antibody titre; no relation connects them. |
| 5 | no | n | arbitrary | `CAST(Symptoms AS INTEGER) = 'retina artery occlusion'` is an impossible comparison; `Symptoms > 'CNS lupus (headache)'` is lexicographic on free text; a specific patient ID is a CASE branch. |
| 6 | no | y | arbitrary | `UN / round(CASE(CRP text, ID < 4843434, ID = 1066089, ANA Pattern > 'S,N')*5*0.1 + HCT/100)`: urea nitrogen divided by a score built from identifiers and text ranges. |
| 7 | no | y | arbitrary | Weight chains on CASE over `COUNT(*) = 1390`; the result is compared to text `KCT` and to `Birthday`; `SSA < U-PRO` compares two text lab results. |
| 8 | no | y | arbitrary | `o2 / (o2/o2)`, `1 - o2/o2`, `log(10,10) = 10`, `CURRENT_DATE BETWEEN text AND PERCENT_RANK()`: x/x, always-false filter, impossible comparisons. |
| 9 | no | y | arbitrary | Polynomials of `COUNT(*)` (count x 1.5 x count x 3 x 3 x 10 ...) and `1 - COUNT(*)`, plus a CASE on `Diagnosis > 'PM'`. |
| 10 | no | y | arbitrary | `power(ALP,2) / power(ALP,2)` (x/x), `power(ALP,1.5)`, `(ALP*0.75)*(UN/14)/1.5 = ALP^2` comparisons. |
| 11 | no | y | arbitrary | `(aCL IgG/0.8 * aCL IgA /0.75 + 1 - ANA/16) * (Thrombosis / aCL IgM * 1.5)`, then compared `< Examination Date`: unrelated units multiplied, a number compared to a date. |
| 12 | no | n | arbitrary | The flag `CPK > 36 OR RBC != 2.5 OR SSA > '16'` ORs unrelated conditions, with an exact inequality on RBC and a lexicographic comparison of a text antibody result. |
| 13 | uncertain | n | arbitrary | Lists HGB per lab row, but also `CAST(Patient.ID AS REAL)`, an identifier output as a number for no purpose. |
| 14 | yes | n | - | Lists aCL IgG, aCL IgM (rounded) and ANA per examination, ordered by aCL IgM. |
| 15 | uncertain | n | arbitrary | Lists First Date per patient, plus `CAST(Examination.ID AS REAL)`: identifier cast to a number for no purpose. |
| 16 | uncertain | y | arbitrary | `Thrombosis * 0.25` scales a severity grade by an unexplained 0.25 (the grade runs 0-3, so it is not a normalisation to the maximum). |
| 17 | yes | n | - | Lists 100 patients by ID with admission status and sex. |
| 18 | no | y | arbitrary | `(100 - HCT) * TP * 10 / (ALP*0.25 * (T-BIL + CRE)/0.25 - C3/C4)`: bilirubin plus creatinine, times an enzyme, minus a complement ratio; C3/C4 alone is supported, the whole is not. |
| 19 | no | y | arbitrary | ANA^2.5, aCL mixes and `Thrombosis / aCL IgG`, then `o1/o1`, `(o1/o1)/o1`, `1 - CASE(...)`: x/x and arbitrary weight chains. |
| 20 | yes | n | - | Lists platelet count and sex per lab row (CAST to REAL is harmless). |

## Counts

Overall (20): yes 3, uncertain 3, no 14.

With arithmetic (13): yes 0, uncertain 1, no 12.

Causes (17 non-yes): missing evidence 0, lost in propagation 0, arbitrary 17.

## Pattern

Every query that contains arithmetic is incoherent or at best has an unexplained weight; the only "yes" answers are plain listings with no calculation, so the delivered corpus has no acceptable arithmetic in this sample. The failures are not missing catalogue facts: the SQL itself combines unrelated units, uses identifiers and free text as numbers, and stacks constant weights, x/x and tautological CASEs, which the catalogue already shows to be meaningless.
