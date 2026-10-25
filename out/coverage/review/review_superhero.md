# superhero: semantic coherence review (20 delivered queries)

Question: does the query express a coherent calculation over the target data, with its parameters and assumptions explicit?

| query id | verdict | cause (if not yes) | reason |
|---|---|---|---|
| superhero-1 | uncertain | arbitrary | Sensible listing of tall heroes, but `1 AS o3` is a purposeless constant column and `round(CAST(attribute_value AS INTEGER), 2) IS NOT NULL` is a wrapped not-null test. |
| superhero-2 | no | arbitrary | `weight_kg - height_cm` subtracts kg from cm, then feeds a CASE keyed on `full_name > 'Xenomorph'` and `id = 35` into `power(..., 1.5)`. |
| superhero-3 | uncertain | arbitrary | Plain listing, but the filter `alignment > 'Bad'` is a lexical ordering on a category, and the unused LEFT JOIN to hero_power only duplicates rows. |
| superhero-4 | no | arbitrary | `weight_kg * (height*2 + height*0.1) * 0.1` is a chain of arbitrary weights, and the CASE branch divides an expression by itself (x / x). |
| superhero-5 | no | arbitrary | `skin_colour_id` (an identifier) is bucketed into divisors 2/4/0 for `weight_kg`, then combined with `1 - weight_kg`. |
| superhero-6 | no | arbitrary | `COUNT(*)` grouped by the primary key `colour.id` on the colour table itself is always 1. |
| superhero-7 | no | arbitrary | AVG of CASE scores from lexical gender comparisons, grouped by gender id (one row each), then a ratio of two such averages. |
| superhero-8 | yes |  | Lists eye colour, weight, name and height for heroes with a publisher; plain and sensible. |
| superhero-9 | no | arbitrary | Sum of two CASE scores keyed on a hero name, lexical gender comparisons and `eye_colour_id > 7`, then `/5 /0.25`. |
| superhero-10 | no | arbitrary | Step s16 is arithmetic on constants only (`round(2,2)`, `CAST(0 AS INTEGER) * 0.2`, `sqrt(2)*sqrt(2)`), and its sum is compared to another sum of constants. |
| superhero-11 | no | arbitrary | `weight_kg / (1 - height_cm)` has no meaning, and the CASE compares `DENSE_RANK()` to `full_name`. |
| superhero-12 | no | arbitrary | `weight_kg/72 + attribute_value/50` could be an index, but it is multiplied by a CASE score keyed on `eye_colour_id > 7`, and the query uses `colour.id LIKE colour.id`. |
| superhero-13 | no | arbitrary | `height_cm/100` is a cm-to-m conversion, but `attribute_value / (1 - (h + 1.5h + 4.45))` has no meaning. |
| superhero-14 | yes |  | Distinct hero ids that have any attribute, sorted; trivial but coherent. |
| superhero-15 | yes |  | Lists publisher and race ids of heroes with an alignment; uninformative but coherent. |
| superhero-16 | uncertain | arbitrary | The CASE gives 10 to `weight_kg > 98` with no stated purpose, has a contradictory branch (`weight_kg > 98 AND weight_kg = 70`), and RANK orders by `race.id`. |
| superhero-17 | no | arbitrary | The filter `superhero.full_name = gender.gender` compares a person's name to a gender label. |
| superhero-18 | no | arbitrary | Arithmetic on `1 - CASE WHEN power_id > 31`, constants (`round(2,2) + abs(2)`), and a contradictory `hero_id > 595 AND hero_id < 399`. |
| superhero-19 | yes |  | Heroes' names and heights (joined to hero_attribute, which duplicates rows); coherent. |
| superhero-20 | yes |  | Attribute values, gender and height of the hero 'Wildfire' at 193 cm; coherent. |

## Totals

- yes: 5 (8, 14, 15, 19, 20)
- uncertain: 3 (1, 3, 16)
- no: 12 (2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 17, 18)
- causes (15 non-yes): arbitrary 15, missing evidence 0, lost in propagation 0

## Dominant pattern

Every query with arithmetic is incoherent. The superhero schema has only three numeric quantities (height, weight, attribute value), so the generator builds expressions from identifiers (`eye_colour_id > 7`, `skin_colour_id` as a divisor), lexical comparisons on text labels, and chains of constant weights, 0.1 / 0.2 / 0.75 / 1.5, with `1 - x` wrappers. The failures are not knowledge gaps: the catalogue's one relation (height~weight, "comparable") would not rescue `weight_kg - height_cm`, and the degenerate cases (x/x, COUNT per primary key, constant-only steps) are decidable from the AST alone. The coherent queries are the ones without arithmetic.
