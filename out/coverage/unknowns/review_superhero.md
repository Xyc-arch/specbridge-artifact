# superhero: why are 20 calculations UNKNOWN? (manual review)

Causes: 1 = catalogue lacks it; 2 = propagation loses it; 3 = no supported interpretation.

| id | cause | reason |
|---|---|---|
| u1 | 3 | `height_cm * (weight_kg * 3)`: a product of height and tripled weight has no body-measure meaning (BMI divides weight by height squared); the "comparable" relation does not license a product, and the node sits inside a BETWEEN against a gender text. |
| u2 | 3 | `1 - ROUND(CAST(height_cm AS INTEGER)/100, 1)`: the unit (m) survived the step, but "1 minus a height in metres" is not a complement of any fraction; the integer cast also truncates it. |
| u3 | 3 | Nested chain of weight/height, (weight/72)^2 x 1000, (1 - height_cm) x height/100: an arbitrary composition; `1 - height_cm` alone subtracts a length from a pure number. |
| u4 | 3 | `CASE ... THEN 1 ELSE 1 END * ROUND(3/1.5, 2)`: a constant indicator times a constant; arithmetic on constants only. |
| u5 | 3 | Score CASE whose branches test `hero_id` ranges (an identifier used as a quantity) and contradictory name conditions, combined arithmetically with further CASE scores. |
| u6 | 3 | `(height_cm - CASE weight=88 ...) + indicator/0.2 + (1 - height_cm)`: mixes a length, an arbitrary score and a length subtracted from 1; the CASE also compares a number with `alignment` text. |
| u7 | 3 | Every leaf is a literal (ROUND(2,2), SQRT(2), 10, 0.25): arithmetic on constants only. |
| u8 | 3 | `1 - ((weight_kg + 72) / 0.1)`: shifting weight by 72 kg, scaling by 10 and subtracting from 1 gives no quantity. |
| u9 | 3 | `(weight_kg*0.75 - weight_kg/72)/0.75` divided by a score CASE: subtracts a dimensionless ratio from a mass, then divides by an arbitrary 1/4/10 score. |
| u10 | 3 | `exp(attribute_value/50) * (height_cm/weight_kg) * exp(attribute_value/50)`: an attribute score exponentiated and multiplied into a body ratio; no link between power scores and body proportion. |
| u11 | 3 | `1 - ROUND(1 - attribute_value) * attribute_value`: a 0-100 score subtracted from 1 then squared; "1 - score" is not a complement on a 0-100 scale. |
| u12 | 1 | `height_cm / weight_kg` on the same superhero is a meaningful height-to-weight proportion; the catalogue records only "comparable" (BMI panel), not that their ratio is a defined body index. |
| u13 | 3 | `CASE name='Zoom' THEN 1 ELSE 0 END / CASE ... THEN 4 ELSE 0 END`: an indicator divided by a constant-valued CASE; arithmetic on flags only. |
| u14 | 3 | `(ROUND(attr/50)/5*1.5) * (ROUND(attr/50)/1.5/10)`: a normalised score multiplied by itself through an arbitrary chain of weights (x 0.3 x 1/15). |
| u15 | 3 | `ROUND(1 - height_cm) + ROUND(1 - height_cm) + CASE(...)`: doubled "1 minus a height" plus a score whose conditions compare it to weight x 5. |
| u16 | 3 | `height_cm - ((attr/50 + 1)^2 * 0.25)`: subtracts a transformed attribute score from a length; unrelated quantities. |
| u17 | 3 | `height_cm * (weight_kg / 72)`: height times weight relative to 72 kg has no domain meaning; the relation "comparable" does not support a product. |
| u18 | 3 | Sum of two CASE scores built from name comparisons and `x*3 = x*3` tautologies, with `10*3 < 1 - height_cm`; arbitrary. |
| u19 | 3 | `(attr/50) * ((attr/50)/(attr/50)) * (attr*3)`: contains x/x and squares a score through arbitrary weights. |
| u20 | 3 | `1 - (CASE(height/weight = 2.47 ...)*0.2 + ROUND(height_cm))`: a score plus a raw height subtracted from 1; the CASE tests `hair_colour_id = 4` (a code). |

## Counts

| cause | n |
|---|---|
| 1 catalogue lacks it | 1 |
| 2 propagation loses it | 0 |
| 3 no supported interpretation | 19 |

## Pattern

Nineteen of twenty UNKNOWN calculations are not near-misses of the checker: they are arbitrary compositions (x/x, "1 - raw measure", constants-only chains, score CASEs over ids and names, unrelated score x length products) that no catalogue fact or better propagation could support. Only the plain `height_cm / weight_kg` is a real calculation the checker missed, and it is missing because the catalogue's height-weight relation is "comparable" rather than a ratio fact.
