# thrombosis_prediction: semantic coherence review (20 delivered queries)

| query id | verdict | cause (if not yes) | reason |
|---|---|---|---|
| thrombosis_prediction-1 | no | arbitrary | `(C3/42)/2 * (C3/42)*3`, `o2/o2`, `x - x`, and the contradictory filter `UA = 2.8 AND UA = 4.4` make the output meaningless. |
| thrombosis_prediction-2 | no | arbitrary | `(1 - aCL IgG/0.8) - (1 - ANA/16) * ((aCL IgG/0.8)/(1 - ANA/16))` mixes an antibody level and a titer through unexplained references. |
| thrombosis_prediction-3 | no | arbitrary | `aCL IgM - Thrombosis` subtracts a thrombosis severity grade from an antibody concentration. |
| thrombosis_prediction-4 | yes | | Patients with thrombosis grade 2 or aCL IgG above 1.5, both clear filters. |
| thrombosis_prediction-5 | no | arbitrary | `(UN/10) * (LDH*10)` times a CASE score, and `TAT BETWEEN 118 AND 101` (always empty), form an arbitrary chain. |
| thrombosis_prediction-6 | no | arbitrary | The outputs are pure constant arithmetic on `abs(2)` with chains of weights; the only column arithmetic, `(ANA/16)*aCL IgG*1.5 ... * aCL IgA`, has no meaning. |
| thrombosis_prediction-7 | no | arbitrary | `(HGB/10.8) * (TAT + 77) * 0.75` multiplies hemoglobin by a shifted TAT value with no purpose. |
| thrombosis_prediction-8 | no | arbitrary | `T-CHO*10*5*0.75` stacks weights, and `1 - that` treats a cholesterol value as a fraction. |
| thrombosis_prediction-9 | no | arbitrary | `WBC*0.1 + ALB/3.7 + 1.84` sums unrelated lab values, and `s10.o1 = Laboratory.Date` compares an average against a date. |
| thrombosis_prediction-10 | no | arbitrary | `T-BIL - First Date` subtracts a date cast to a number from bilirubin. |
| thrombosis_prediction-11 | no | arbitrary | `(1 - ANA) * 0.2` treats an antibody titer as a fraction of 1. |
| thrombosis_prediction-12 | no | arbitrary | `SEX > 'M'` orders a categorical code alphabetically, so the filter cannot be meaningful. |
| thrombosis_prediction-13 | no | arbitrary | `Thrombosis / COUNT(*)`, `log(...)` of CASE scores, and `((aCL IgM*5)+HCT)+48.6` add an antibody level to a hematocrit percent. |
| thrombosis_prediction-14 | no | arbitrary | `HCT/(HCT/...)`, `ALB/3.7 - ALB/3.7`, division by a 0/1 flag, and `s7.o2 = First Date` are degenerate or incomparable. |
| thrombosis_prediction-15 | no | arbitrary | `RNP IN (Date)`, `s4.o1 - s4.o1`, and `ALP*10 + GPT + aCL IgA*3` mix unrelated quantities. |
| thrombosis_prediction-16 | no | arbitrary | `power(ALP,2)/power(ALP,2)`, `ALP*0.75 * UN/14`, and `Diagnosis > 'PSS, SJS'` are degenerate or meaningless. |
| thrombosis_prediction-17 | uncertain | missing evidence | `aCL IgA - aCL IgM` is a difference within one antibody panel, but it is in APL vs MPL units, and the catalogue does not say whether they can be compared. |
| thrombosis_prediction-18 | no | arbitrary | `((100-HCT)+61.9 - (100-HCT)/100)*10`, filtered where it equals itself divided by 10, is an arbitrary chain. |
| thrombosis_prediction-19 | no | arbitrary | `Symptoms = Admission` equates two unrelated text fields, and `KCT > '+'` and `ANA Pattern > 'P,S'` order categories alphabetically. |
| thrombosis_prediction-20 | yes | | Lists the patient ID, admission status and sex, ordered by ID. |

## Totals

- yes: 2
- uncertain: 1
- no: 17
- Causes: missing evidence 1, lost in propagation 0, arbitrary 17

## Dominant pattern

Almost every query that has arithmetic is incoherent at the point where the operation is chosen. It combines unrelated lab values, applies long chains of unexplained weights and references (`*0.75`, `/3.7`, `+61.9`), or produces degenerate terms (`x/x`, `x - x`). Missing knowledge is not the cause: the catalogue's units and descriptions already show these combinations are meaningless. Only the arithmetic-free filter and listing queries (4, 20) are coherent. The one borderline case is a difference within the antibody panel whose units are not confirmed to be comparable (17).
