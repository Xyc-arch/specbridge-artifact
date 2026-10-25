# superhero: 20 random unknown substantive calculations (of 2210)

## superhero-u1 (attempt 85) -- mechanical class: BOTH KNOWN

Node: `("superhero"."height_cm" * ("superhero"."weight_kg" * 3))`

- left operand: unit 'cm', kind 'measure', quantity ('superhero.height_cm', 'value')
- right operand: unit 'kg', kind '', quantity ()
- stored columns under it: superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
WITH "s1" AS (SELECT "superhero"."gender_id" AS "o0", CAST("superhero"."weight_kg" AS REAL) AS "o1" FROM "gender" AS "gender" INNER JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" ORDER BY "superhero"."gender_id" DESC LIMIT 5), "s15" AS (SELECT "superhero"."id" AS "o0", log(10, ((((CASE WHEN "superhero"."superhero_name" < 'Wildfire' THEN 1 WHEN "gender"."gender" < 'Female' THEN 3 WHEN "gender"."gender" BETWEEN ("superhero"."height_cm" * ("superhero"."weight_kg" * 3)) AND "gender"."id" THEN 10 ELSE 1 END * 0.2) + ((CASE WHEN "superhero"."superhero_name" < 'Wildfire' THEN 1 WHEN "gender"."gender" < 'Female' THEN 3 WHEN "gender"."gender" BETWEEN ("superhero"."height_cm" * ("superhero"."weight_kg" * 3)) AND "gender"."id" THEN 10 ELSE 1 END * 0.2) / "superhero"."height_cm")) + (((CAST(("superhero"."weight_kg" * 3) AS REAL) - CASE WHEN "superhero"."id" = 33 THEN 1 WH
```

## superhero-u2 (attempt 117) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - ROUND((CAST("s1"."o1" AS INTEGER) / 100), 1))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'm', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "publisher"."publisher_name" AS "o0", "superhero"."height_cm" AS "o1" FROM "colour" AS "colour" INNER JOIN "superhero" AS "superhero" ON "colour"."id" = "superhero"."skin_colour_id" INNER JOIN "publisher" AS "publisher" ON "superhero"."publisher_id" = "publisher"."id" ORDER BY "superhero"."height_cm" DESC LIMIT 10) SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", coalesce(((CASE WHEN "s1"."o0" > 'SyFy' THEN 0 WHEN "s1"."o1" BETWEEN 188 AND 188 THEN 1 WHEN ("s1"."o0" > 'HarperCollins' AND "s1"."o0" = 'Wildstorm' AND "s1"."o0" = 'DC Comics' AND ("s1"."o0" > 'Universal Studios' OR ("s1"."o1" = 198 AND "s1"."o0" = 'Marvel Comics'))) THEN 2 WHEN ("s1"."o0" > 'J. K. Rowling' AND "s1"."o1" = 305) THEN 1 ELSE 0 END * ((1 - CASE WHEN CASE WHEN "s1"."o0" > 'SyFy' THEN 0 WHEN "s1"."o1" BETWEEN 188 AND 188 THEN 1 WHEN ("s1"."o0" > 'HarperCollins' AND "s1"."o0" = 'Wildstorm' AND "s1"
```

## superhero-u3 (attempt 199) -- mechanical class: LOST

Node: `((((((CAST("superhero"."weight_kg" AS REAL) / "superhero"."height_cm") / 0.2) * ((((ROUND("superhero"."weight_kg", 2) / 72) / 0.5) * ((ROUND("superhero"."weight_kg", 2) / 72) / 0.5)) * 1.5)) * (((CAST("superhero"."height_cm" AS REAL) / ROUND("superhero"."weight_kg", 2)) * 0.1) - ((((ROUND("superhero`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'kg', kind '', quantity ()
- stored columns under it: superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT "superhero"."race_id" AS "o0", round((((CAST("superhero"."height_cm" AS REAL) / round("superhero"."weight_kg", 2)) * 0.1) - ((((round("superhero"."weight_kg", 2) / 72) * 2) * ((round("superhero"."weight_kg", 2) / 72) * 1000)) * ((1 - ((1 - "superhero"."height_cm") * ("superhero"."height_cm" / 100))) * ((("superhero"."weight_kg" / 72) + ("superhero"."weight_kg" / 72)) * 0.75)))), 1) AS "o1", ("superhero"."height_cm" - ((((((CAST("superhero"."weight_kg" AS REAL) / "superhero"."height_cm") / 0.2) * ((((round("superhero"."weight_kg", 2) / 72) / 0.5) * ((round("superhero"."weight_kg", 2) / 72) / 0.5)) * 1.5)) * (((CAST("superhero"."height_cm" AS REAL) / round("superhero"."weight_kg", 2)) * 0.1) - ((((round("superhero"."weight_kg", 2) / 72) * 2) * ((round("superhero"."weight_kg", 2) / 72) * 1000)) * ((1 - ((1 - "superhero"."height_cm") * ("superhero"."height_cm" / 100))) * ((("superhero
```

## superhero-u4 (attempt 16) -- mechanical class: SCORE

Node: `(CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * ROUND((CAST(3 AS REAL) / 1.5), 2))`

- left operand: unit '', kind 'indicator', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: gender.gender [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "gender"."id" AS "o0", "gender"."gender" AS "o1", coalesce((((CAST(((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * 0.75) / 5) AS REAL) / ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * 0.75) / 5)) * (1 - (CASE WHEN ("gender"."gender" < 'Female' AND "gender"."gender" > 'N/A' AND CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END = ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) / 0.5)) THEN 10 WHEN (CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) < ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) / 0.5) THEN 2 WHEN "gender"."id" < 1 THEN 4 ELSE 0 END * 10))) * 1.5), 0) AS "o2" FROM "gender" AS "gender" WHERE "gender"."gender" > 'N/A' ORDER BY coalesce((((CAST(((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 
```

## superhero-u5 (attempt 172) -- mechanical class: SCORE

Node: `((CASE WHEN ("attribute"."attribute_name" != 'Strength' AND "attribute"."attribute_name" >= 'Durability') THEN 5 WHEN ("hero_attribute"."hero_id" = 756 AND "attribute"."attribute_name" > 'Strength' AND "attribute"."attribute_name" > 'Power' AND "hero_attribute"."hero_id" = 754 AND "attribute"."attri`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: attribute.attribute_name [unit '' (-), kind '', scale '']; hero_attribute.hero_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "hero_attribute"."hero_id" AS "o0", abs((((((round(CAST((round(CAST(COUNT(*) AS REAL), 2) * COUNT(*)) AS REAL), 2) / round(SUM(CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "hero_attribute"."hero_id" > 383 THEN 4 ELSE 1 END), 3)) * 0.1) * 1.5) + round(CAST(round(SUM(CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "hero_attribute"."hero_id" > 383 THEN 4 ELSE 1 END), 3) AS REAL), 2)) * (CAST((((round(CAST((round(CAST(COUNT(*) AS REAL), 2) * COUNT(*)) AS REAL), 2) / round(SUM(CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "hero_attribute"."hero_id" > 383 THEN 4 ELSE 1 END), 3)) * 0.1) * 1.5) AS INTEGER) * 5))) AS "o1", coalesce(AVG((((1 - "hero_attribute"."attribute_value") + round(CAST((1 - "hero_attribute"."attribute_value") AS REAL), 2)) + log(10, ((1 - "hero_attribute"."attribute_value") * round(((CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "her
```

## superhero-u6 (attempt 84) -- mechanical class: LOST

Node: `((("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) + ((CASE WHEN CAST(("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) AS REAL) >= "alignment"."alignment" THEN 1 WHEN "superhero"."superhero_name" = 'Vibe' THEN 1 ELSE 0 END / 0.2`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: alignment.alignment [unit '' (-), kind '', scale '']; superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.superhero_name [unit '' (-), kind '', scale '']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT CAST("superhero"."weight_kg" AS REAL) AS "o0", "superhero"."full_name" AS "o1", "superhero"."height_cm" AS "o2", "superhero"."weight_kg" AS "o3", (CAST("superhero"."weight_kg" AS REAL) * ((("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) + ((CASE WHEN CAST(("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) AS REAL) >= "alignment"."alignment" THEN 1 WHEN "superhero"."superhero_name" = 'Vibe' THEN 1 ELSE 0 END / 0.2) + (1 - "superhero"."height_cm"))) + ((round(CAST((1 - "superhero"."height_cm") AS REAL), 2) + round((1 - "superhero"."height_cm"), 2)) + ((CASE WHEN round(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ("superhero"."weight_kg" * 5) THEN 4 WHEN "superhero"."weight_kg" < 98 THEN 1 WHEN round(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ((("superhero"."height_cm" / "superhero"."weight_kg") * (1 -
```

## superhero-u7 (attempt 18) -- mechanical class: NO UNIT

Node: `(((((1 - (ROUND(2, 2) / 0.25)) * (1 - (10 / ROUND(2, 2)))) / 0.5) * (((1 - (ROUND(2, 2) / 0.1)) * (ROUND(CAST(10 AS REAL), 2) / CAST(ROUND(2, 2) AS REAL))) * 3)) * (CAST(((1 - (ROUND(2, 2) / 0.1)) * (ROUND(CAST(10 AS REAL), 2) / CAST(ROUND(2, 2) AS REAL))) AS REAL) / (((1 - (ROUND(2, 2) / 0.25)) * (`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "race"."race" AS "o0", ((((CASE WHEN ((CAST(2 AS REAL) * 0.2) + (round(2, 2) + 2.0)) > ((CAST(2 AS REAL) * 0.2) + (round(2, 2) + 2.0)) THEN 3 ELSE 0 END / 3) * 0.1) / 0.5) + (((CASE WHEN (round(2, 2) + 2.0) > 4.0 THEN 2 WHEN round(2, 2) > 2 THEN 5 ELSE 0 END / 10) + 0) / (((((1 - (round(2, 2) / 0.25)) * (1 - (10 / round(2, 2)))) / 0.5) * (((1 - (round(2, 2) / 0.1)) * (round(CAST(10 AS REAL), 2) / CAST(round(2, 2) AS REAL))) * 3)) * (CAST(((1 - (round(2, 2) / 0.1)) * (round(CAST(10 AS REAL), 2) / CAST(round(2, 2) AS REAL))) AS REAL) / (((1 - (round(2, 2) / 0.25)) * (1 - (10 / round(2, 2)))) / 0.5))))) AS "o1", RANK() OVER (ORDER BY ((((CASE WHEN ((CAST(2 AS REAL) * 0.2) + (round(2, 2) + 2.0)) > ((CAST(2 AS REAL) * 0.2) + (round(2, 2) + 2.0)) THEN 3 ELSE 0 END / 3) * 0.1) / 0.5) + (((CASE WHEN (round(2, 2) + 2.0) > 4.0 THEN 2 WHEN round(2, 2) > 2 THEN 5 ELSE 0 END / 10) + 0) / (((((
```

## superhero-u8 (attempt 62) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - (("superhero"."weight_kg" + 72) / 0.1))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'kg', kind '', quantity ()
- stored columns under it: superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "superhero"."hair_colour_id" AS "o0", (((1 - ((((CASE WHEN "superhero"."superhero_name" > 'Vixen' THEN 10 WHEN "superhero"."full_name" > 'Violet Parr' THEN 4 ELSE 0 END / 0.1) * 1.5) - ((CAST("superhero"."weight_kg" AS REAL) / "superhero"."height_cm") * ((((1 - (("superhero"."weight_kg" + 72) / 0.1)) * (1 - (("superhero"."weight_kg" + 72) / 0.5))) / 0.1) * ((round(CAST(("superhero"."weight_kg" + 72) AS REAL), 2) / 1.5) * 10)))) + ((((((1 - (("superhero"."weight_kg" + 72) / 0.1)) * (1 - (("superhero"."weight_kg" + 72) / 0.5))) / 0.1) * ((round(CAST(("superhero"."weight_kg" + 72) AS REAL), 2) / 1.5) * 10)) * 5) - ((1 - ((coalesce(CAST("superhero"."weight_kg" AS REAL), 0) / 72) / 1.5)) + 0.333)))) + ((1 - coalesce(CAST("superhero"."weight_kg" AS REAL), 0)) / 0.75)) + (((1 - coalesce(CAST("superhero"."weight_kg" AS REAL), 0)) * 1.5) * CASE WHEN round(CAST((1 - coalesce(CAST("superhero
```

## superhero-u9 (attempt 34) -- mechanical class: LOST

Node: `(COALESCE(CAST(((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) AS REAL), 0) / (CASE WHEN ((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) > 70.67 THEN 4 WHEN ((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) < 70.67 `

- left operand: unit 'kg', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: hero_attribute.attribute_value [unit 'score point (0-100 scale)' (model), kind '', scale 'ratio']; superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT "colour"."id" AS "o0", (((coalesce(CAST(((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) AS REAL), 0) / (CASE WHEN ((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) > 70.67 THEN 4 WHEN ((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) < 70.67 THEN 1 WHEN (CAST("hero_attribute"."attribute_value" AS REAL) / "superhero"."height_cm") > 0.28 THEN 10 WHEN round(CAST(("superhero"."weight_kg" * 0.75) AS REAL), 1) = round(CAST(("superhero"."weight_kg" * 0.75) AS REAL), 1) THEN 1 ELSE 1 END / 10)) + (CAST(coalesce(CAST(((("superhero"."weight_kg" * 0.75) - ("superhero"."weight_kg" / 72)) / 0.75) AS REAL), 0) AS REAL) / round(CAST(("superhero"."weight_kg" * 0.75) AS REAL), 1))) + (((((1 - ((round("superhero"."height_cm", 0) / 100) * 5)) * 0.25) / (1 - round("superhero"."height_cm", 0))) + (CASE WHEN "superhero".
```

## superhero-u10 (attempt 132) -- mechanical class: LOST

Node: `((EXP(("hero_attribute"."attribute_value" / 50)) * ("superhero"."height_cm" / "superhero"."weight_kg")) * EXP(("hero_attribute"."attribute_value" / 50)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: hero_attribute.attribute_value [unit 'score point (0-100 scale)' (model), kind '', scale 'ratio']; superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT DISTINCT "superhero"."alignment_id" AS "o0", AVG(((("superhero"."height_cm" / "superhero"."weight_kg") * (("superhero"."height_cm" / ((exp(("hero_attribute"."attribute_value" / 50)) * ("superhero"."height_cm" / "superhero"."weight_kg")) * exp(("hero_attribute"."attribute_value" / 50)))) * 0.75)) - ((1 - (round(("hero_attribute"."attribute_value" - 50), 2) * 1.5)) + abs((CASE WHEN (1 - (round(("hero_attribute"."attribute_value" - 50), 2) * 1.5)) = 1.0 THEN 1 ELSE 0 END * 10))))) AS "o1" FROM "hero_power" AS "hero_power" INNER JOIN "superpower" AS "superpower" ON "hero_power"."power_id" = "superpower"."id" LEFT JOIN "superhero" AS "superhero" ON "hero_power"."hero_id" = "superhero"."id" LEFT JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" GROUP BY "superhero"."alignment_id" ORDER BY AVG(((("superhero"."height_cm" / "superhero"."weight_kg") 
```

## superhero-u11 (attempt 172) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - (ROUND(CAST((1 - "hero_attribute"."attribute_value") AS REAL), 2) * "hero_attribute"."attribute_value"))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'score point (0-100 scale) × score point (0-100 scale)', kind '', quantity ()
- stored columns under it: hero_attribute.attribute_value [unit 'score point (0-100 scale)' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "hero_attribute"."hero_id" AS "o0", abs((((((round(CAST((round(CAST(COUNT(*) AS REAL), 2) * COUNT(*)) AS REAL), 2) / round(SUM(CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "hero_attribute"."hero_id" > 383 THEN 4 ELSE 1 END), 3)) * 0.1) * 1.5) + round(CAST(round(SUM(CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "hero_attribute"."hero_id" > 383 THEN 4 ELSE 1 END), 3) AS REAL), 2)) * (CAST((((round(CAST((round(CAST(COUNT(*) AS REAL), 2) * COUNT(*)) AS REAL), 2) / round(SUM(CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "hero_attribute"."hero_id" > 383 THEN 4 ELSE 1 END), 3)) * 0.1) * 1.5) AS INTEGER) * 5))) AS "o1", coalesce(AVG((((1 - "hero_attribute"."attribute_value") + round(CAST((1 - "hero_attribute"."attribute_value") AS REAL), 2)) + log(10, ((1 - "hero_attribute"."attribute_value") * round(((CASE WHEN "hero_attribute"."hero_id" > 560 THEN 5 WHEN "her
```

## superhero-u12 (attempt 84) -- mechanical class: BOTH KNOWN

Node: `("superhero"."height_cm" / "superhero"."weight_kg")`

- left operand: unit 'cm', kind 'measure', quantity ('superhero.height_cm', 'value')
- right operand: unit 'kg', kind 'measure', quantity ('superhero.weight_kg', 'value')
- stored columns under it: superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT CAST("superhero"."weight_kg" AS REAL) AS "o0", "superhero"."full_name" AS "o1", "superhero"."height_cm" AS "o2", "superhero"."weight_kg" AS "o3", (CAST("superhero"."weight_kg" AS REAL) * ((("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) + ((CASE WHEN CAST(("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) AS REAL) >= "alignment"."alignment" THEN 1 WHEN "superhero"."superhero_name" = 'Vibe' THEN 1 ELSE 0 END / 0.2) + (1 - "superhero"."height_cm"))) + ((round(CAST((1 - "superhero"."height_cm") AS REAL), 2) + round((1 - "superhero"."height_cm"), 2)) + ((CASE WHEN round(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ("superhero"."weight_kg" * 5) THEN 4 WHEN "superhero"."weight_kg" < 98 THEN 1 WHEN round(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ((("superhero"."height_cm" / "superhero"."weight_kg") * (1 -
```

## superhero-u13 (attempt 135) -- mechanical class: SCORE

Node: `(CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END / CASE WHEN NOT (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END IS NULL) THEN 4 ELSE 0 END)`

- left operand: unit '', kind 'indicator', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "superhero"."superhero_name" AS "o0" FROM "race" AS "race" INNER JOIN "superhero" AS "superhero" ON "race"."id" = "superhero"."race_id" WHERE NOT ("superhero"."height_cm" IS NULL) GROUP BY "superhero"."superhero_name") SELECT "s1"."o0" AS "o0", (((CAST(((CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END / 0.75) / 0.5) AS REAL) - CASE WHEN NOT (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END IS NULL) THEN 4 ELSE 0 END) + (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END / CASE WHEN NOT (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END IS NULL) THEN 4 ELSE 0 END)) * 0.5) AS "o1", (((((CAST(((CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END / 0.75) / 0.5) AS REAL) - CASE WHEN NOT (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END IS NULL) THEN 4 ELSE 0 END) + (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END / CASE WHEN NOT (CASE WHEN "s1"."o0" = 'Zoom' THEN 1 ELSE 0 END IS NULL) THEN
```

## superhero-u14 (attempt 32) -- mechanical class: BOTH KNOWN

Node: `(((ROUND((ROUND("hero_attribute"."attribute_value", 2) / 50), 2) / 5) * 1.5) * ((ROUND((ROUND("hero_attribute"."attribute_value", 2) / 50), 2) / 1.5) / 10))`

- left operand: unit 'score point (0-100 scale)', kind '', quantity ()
- right operand: unit 'score point (0-100 scale)', kind '', quantity ()
- stored columns under it: hero_attribute.attribute_value [unit 'score point (0-100 scale)' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "alignment"."id" AS "o0", coalesce("superhero"."id", 0) AS "o1", CASE WHEN coalesce("superhero"."id", 0) > 565 THEN 1 ELSE 0 END AS "o2", (((CASE WHEN ((CAST(round("hero_attribute"."attribute_value", 2) AS REAL) / CAST(("hero_attribute"."attribute_value" * 3) AS REAL)) < (CAST(round("hero_attribute"."attribute_value", 2) AS REAL) / CAST(("hero_attribute"."attribute_value" * 3) AS REAL)) AND "superhero"."full_name" = 'Henry Jonathan Pym' AND coalesce("superhero"."id", 0) = 27 AND "superhero"."full_name" > 'Nathaniel Christopher Adam') THEN 1 WHEN "superhero"."full_name" = 'Vanessa Carlysle' THEN 1 WHEN "superhero"."superhero_name" > 'Violator' THEN 5 ELSE 0 END * 0.5) * 1.5) + 0) AS "o3", "alignment"."alignment" AS "o4", 1 AS "o5", (((1 - (((CAST(((("hero_attribute"."attribute_value" * 3) / 0.75) + 200.0) AS REAL) / (("hero_attribute"."attribute_value" * 3) / 0.75)) * 0.2) - (((CAS
```

## superhero-u15 (attempt 84) -- mechanical class: LOST

Node: `((ROUND(CAST((1 - "superhero"."height_cm") AS REAL), 2) + ROUND((1 - "superhero"."height_cm"), 2)) + ((CASE WHEN ROUND(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ("superhero"."weight_kg" * 5) THEN 4 WHEN "superhero"."weight_kg" < 98 THEN 1 WHEN ROUND(CAST((1 - "superhero"."height_cm") AS REAL`

- left operand: unit 'cm', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT CAST("superhero"."weight_kg" AS REAL) AS "o0", "superhero"."full_name" AS "o1", "superhero"."height_cm" AS "o2", "superhero"."weight_kg" AS "o3", (CAST("superhero"."weight_kg" AS REAL) * ((("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) + ((CASE WHEN CAST(("superhero"."height_cm" - CASE WHEN "superhero"."weight_kg" = 88 THEN 5 ELSE 1 END) AS REAL) >= "alignment"."alignment" THEN 1 WHEN "superhero"."superhero_name" = 'Vibe' THEN 1 ELSE 0 END / 0.2) + (1 - "superhero"."height_cm"))) + ((round(CAST((1 - "superhero"."height_cm") AS REAL), 2) + round((1 - "superhero"."height_cm"), 2)) + ((CASE WHEN round(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ("superhero"."weight_kg" * 5) THEN 4 WHEN "superhero"."weight_kg" < 98 THEN 1 WHEN round(CAST((1 - "superhero"."height_cm") AS REAL), 2) = ((("superhero"."height_cm" / "superhero"."weight_kg") * (1 -
```

## superhero-u16 (attempt 9) -- mechanical class: BOTH KNOWN

Node: `("superhero"."height_cm" - ((("hero_attribute"."attribute_value" / 50) + 1.0) * ((("hero_attribute"."attribute_value" / 50) + 1.0) * 0.25)))`

- left operand: unit 'cm', kind 'measure', quantity ('superhero.height_cm', 'value')
- right operand: unit 'score point (0-100 scale) × score point (0-100 scale)', kind '', quantity ()
- stored columns under it: hero_attribute.attribute_value [unit 'score point (0-100 scale)' (model), kind '', scale 'ratio']; superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "superhero"."publisher_id" AS "o0", ("superhero"."weight_kg" / (1 - (("superhero"."height_cm" - ((("hero_attribute"."attribute_value" / 50) + 1.0) * ((("hero_attribute"."attribute_value" / 50) + 1.0) * 0.25))) * 0.75))) AS "o1", (1 - (("superhero"."height_cm" - ((("hero_attribute"."attribute_value" / 50) + 1.0) * ((("hero_attribute"."attribute_value" / 50) + 1.0) * 0.25))) * 0.75)) AS "o2", (("superhero"."weight_kg" / (1 - (("superhero"."height_cm" - ((("hero_attribute"."attribute_value" / 50) + 1.0) * ((("hero_attribute"."attribute_value" / 50) + 1.0) * 0.25))) * 0.75))) * ((((("superhero"."weight_kg" / (1 - (("superhero"."height_cm" - ((("hero_attribute"."attribute_value" / 50) + 1.0) * ((("hero_attribute"."attribute_value" / 50) + 1.0) * 0.25))) * 0.75))) * 5) * 5) + ((1 - (("superhero"."height_cm" - ((("hero_attribute"."attribute_value" / 50) + 1.0) * ((("hero_attribute"."attr
```

## superhero-u17 (attempt 74) -- mechanical class: BOTH KNOWN

Node: `("superhero"."height_cm" * (CAST("superhero"."weight_kg" AS REAL) / 72))`

- left operand: unit 'cm', kind 'measure', quantity ('superhero.height_cm', 'value')
- right operand: unit 'kg', kind '', quantity ()
- stored columns under it: superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT "superhero"."race_id" AS "o0", round(((("superhero"."height_cm" * (CAST("superhero"."weight_kg" AS REAL) / 72)) * 0.2) * 2), 0) AS "o1", (((((("superhero"."height_cm" * (CAST("superhero"."weight_kg" AS REAL) / 72)) * 0.2) * 2) / round(((("superhero"."height_cm" * (CAST("superhero"."weight_kg" AS REAL) / 72)) * 0.2) * 2), 0)) * (round(((("superhero"."height_cm" * (CAST("superhero"."weight_kg" AS REAL) / 72)) * 0.2) * 2), 0) * 0.2)) * 0.75) AS "o2" FROM "publisher" AS "publisher" INNER JOIN "superhero" AS "superhero" ON "publisher"."id" = "superhero"."publisher_id"
```

## superhero-u18 (attempt 154) -- mechanical class: SCORE

Node: `(CASE WHEN ((CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) = (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) AND (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) < (1 - "superhero"."height_cm")) THEN 2 END + CASE WHEN (CAS`

- left operand: unit '', kind 'score', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.superhero_name [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
WITH "s36" AS (SELECT DISTINCT "superhero"."publisher_id" AS "o0", (CASE WHEN ((CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) = (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) AND (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) < (1 - "superhero"."height_cm")) THEN 2 END + CASE WHEN (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END < "superhero"."superhero_name" AND round(CAST(CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END AS REAL), 2) > ((CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) * 0.1)) THEN 10 ELSE 0 END) AS "o1", (((CASE WHEN ((CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) = (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 ELSE 0 END * 3) AND (CASE WHEN "superhero"."superhero_name" > 'Angel' THEN 10 E
```

## superhero-u19 (attempt 88) -- mechanical class: LOST

Node: `((((CAST("hero_attribute"."attribute_value" AS REAL) / 50) * (CAST((CAST("hero_attribute"."attribute_value" AS REAL) / 50) AS REAL) / (CAST("hero_attribute"."attribute_value" AS REAL) / 50))) * ("hero_attribute"."attribute_value" * 3)) + (CASE WHEN ((CAST("hero_attribute"."attribute_value" AS REAL) `

- left operand: unit 'score point (0-100 scale) × score point (0-100 scale) per score point (0-100 scale) × score point (0-100 scale)', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: hero_attribute.attribute_value [unit 'score point (0-100 scale)' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "hero_attribute"."attribute_id" AS "o0", CAST(((1 - (CASE WHEN (CAST("hero_attribute"."attribute_value" AS REAL) / 50) > 1.0 THEN 4 ELSE 0 END * 1.5)) - (2 / CAST((CASE WHEN (CAST("hero_attribute"."attribute_value" AS REAL) / 50) > 1.0 THEN 4 ELSE 0 END * 1.5) AS REAL))) AS REAL) AS "o1", ((((((CAST("hero_attribute"."attribute_value" AS REAL) / 50) * (CAST((CAST("hero_attribute"."attribute_value" AS REAL) / 50) AS REAL) / (CAST("hero_attribute"."attribute_value" AS REAL) / 50))) * ("hero_attribute"."attribute_value" * 3)) + (CASE WHEN ((CAST("hero_attribute"."attribute_value" AS REAL) / 50) * (CAST((CAST("hero_attribute"."attribute_value" AS REAL) / 50) AS REAL) / (CAST("hero_attribute"."attribute_value" AS REAL) / 50))) = (CAST((CAST("hero_attribute"."attribute_value" AS REAL) / 50) AS REAL) / (CAST("hero_attribute"."attribute_value" AS REAL) / 50)) THEN 3 ELSE 0 END + CASE WHEN 
```

## superhero-u20 (attempt 66) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - (COALESCE((CASE WHEN ("superhero"."height_cm" / "superhero"."weight_kg") = 2.47 THEN 2 WHEN "superhero"."hair_colour_id" = 4 THEN 1 ELSE 1 END * 0.2), 0) + ROUND("superhero"."height_cm", 2)))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: superhero.hair_colour_id [unit '' (-), kind '', scale '']; superhero.height_cm [unit 'cm' (model), kind 'measure', scale 'ratio']; superhero.weight_kg [unit 'kg' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: superhero.height_cm comparable superhero.weight_kg

Whole query:
```sql
SELECT "superhero"."eye_colour_id" AS "o0", "superhero"."hair_colour_id" AS "o1", "superhero"."superhero_name" AS "o2", round(((("superhero"."height_cm" / "superhero"."weight_kg") * 0.2) * ((1 - (coalesce((CASE WHEN ("superhero"."height_cm" / "superhero"."weight_kg") = 2.47 THEN 2 WHEN "superhero"."hair_colour_id" = 4 THEN 1 ELSE 1 END * 0.2), 0) + round("superhero"."height_cm", 2))) / 10)), 2) AS "o3", sqrt((round(((("superhero"."height_cm" / "superhero"."weight_kg") * 0.2) * ((1 - (coalesce((CASE WHEN ("superhero"."height_cm" / "superhero"."weight_kg") = 2.47 THEN 2 WHEN "superhero"."hair_colour_id" = 4 THEN 1 ELSE 1 END * 0.2), 0) + round("superhero"."height_cm", 2))) / 10)), 2) / round(((("superhero"."height_cm" / "superhero"."weight_kg") * 0.2) * ((1 - (coalesce((CASE WHEN ("superhero"."height_cm" / "superhero"."weight_kg") = 2.47 THEN 2 WHEN "superhero"."hair_colour_id" = 4 THEN 1 
```

