# superhero: fresh review of 20 delivered queries

Question: does this query express a coherent calculation over the target data, with its parameters and assumptions explicit?

| id | verdict | has arithmetic (y/n) | cause | reason |
|---|---|---|---|---|
| 1 | uncertain | n | arbitrary | Plain listing of heroes with weight, height, alignment, but the inner join to hero_power repeats each hero once per power (and colour/gender/race joins are unused), so the LIMIT 100 is over duplicated rows. |
| 2 | no | y | arbitrary | `s1.o1 - s1.o1`, `BETWEEN 188 AND 188`, contradictory publisher conditions (= 'Wildstorm' AND = 'DC Comics'), "1 - height in m", ROW_NUMBER compared to a score. |
| 3 | uncertain | n | arbitrary | Pairs of power_id and hair_colour_id, repeated once per attribute row through an unused hero_attribute join; well defined but no purpose. |
| 4 | uncertain | n | arbitrary | Attribute value, weight, height per power: the hero_attribute x hero_power fan-out repeats every attribute value once per power; ordering by attribute value mixes the six attributes. |
| 5 | yes | n | - | Lists every superhero with alignment id, height, weight and full name. |
| 6 | no | y | arbitrary | `height_cm * (weight_kg/72) * 0.5` divided by weight again, plus a CASE on `race_id = 4 / > 24` (identifier thresholds). |
| 7 | uncertain | n | arbitrary | Height and attribute value per power with hero_attribute x hero_power fan-out; the `round(height,1)` column duplicates height. |
| 8 | no | y | arbitrary | `attribute_value / attribute_value` (x/x), `1 - CASE` of scores, and a CASE testing `hero_id < 383`. |
| 9 | no | y | arbitrary | Every computed column is arithmetic on constants only (0.75/2 divided by itself, weights 2, 0.2, 5); WHERE `o4 >= o4` is a tautology. |
| 10 | no | y | arbitrary | Filter `weight_kg = superhero_name` compares a mass with a name; then an arbitrary weight chain on weight and `o2 - o0`. |
| 11 | no | y | arbitrary | `CASE gender='Female' THEN 1 ELSE 1` (constant) divided by itself and multiplied through constant weights; arithmetic on constants only. |
| 12 | uncertain | n | arbitrary | Alignment id and height per hero, but the LEFT JOIN to hero_attribute repeats each hero up to six times; the colour/attribute joins have no purpose. |
| 13 | no | y | arbitrary | `weight_kg * 1000 * 3 * 0.2 + 43200` (grams plus half a day of seconds), times attribute/50, divided by height; unrelated quantities. |
| 14 | uncertain | n | arbitrary | race_id, hero_id, name with hero_attribute x hero_power fan-out; each hero repeated attributes x powers times. |
| 15 | no | y | arbitrary | `CAST(race_id AS REAL)` treats a code as a quantity; `sqrt(height_cm * (1 - weight_kg/72) * 0.5)` multiplies a length by "1 minus relative weight". |
| 16 | no | y | arbitrary | `weight_kg / round(weight_kg, 2)` is x/x (about 1), then ranked. |
| 17 | no | n | arbitrary | `height_cm IN (alignment ids, CASE score)` compares a height with identifiers; PERCENT_RANK partitioned by full_name is degenerate. |
| 18 | no | y | arbitrary | All arithmetic on constants (sqrt(2)/sqrt(2), 0.5, powers); a CASE compares a constant to alignment.id. |
| 19 | no | y | arbitrary | CASE on `hero_id = 731`, `eye_colour_id IN (attribute ids)`, `1 - height_cm`, attribute+50 over height, `(o3*3)^2`; incoherent throughout. |
| 20 | no | y | arbitrary | `gender BETWEEN height*weight*3 AND gender.id`, CASE on `superhero.id` thresholds, `log10` of mixed scores, `o1 > full_name`. |

## Counts

| | yes | uncertain | no |
|---|---|---|---|
| all 20 | 1 | 6 | 13 |
| with arithmetic (12) | 0 | 0 | 12 |
| without arithmetic (8) | 1 | 6 | 1 |

Causes (uncertain + no = 19): arbitrary 19; missing evidence 0; lost in propagation 0.

## Pattern

Every query that contains arithmetic is incoherent: the operations are x/x, constants-only chains, identifier thresholds, "1 - raw measure" and cross-unit products, so none of them could be made coherent by a better catalogue or better propagation. The arithmetic-free queries are well defined but mostly carry purposeless many-side joins (hero_attribute, hero_power) that duplicate rows, leaving only one clean listing in twenty.
