# superhero: 20 random delivered programs

## superhero-1 (attempt 51)

```sql
SELECT "superhero"."full_name" AS "o0", "hero_attribute"."attribute_value" AS "o1", "superhero"."height_cm" AS "o2", 1 AS "o3" FROM "hero_attribute" AS "hero_attribute" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id" WHERE (NOT (round(CAST("hero_attribute"."attribute_value" AS INTEGER), 2) IS NULL) AND "superhero"."height_cm" > 188) ORDER BY "hero_attribute"."attribute_value" DESC
```


## superhero-2 (attempt 123)

```sql
SELECT "superhero"."id" AS "o0", ("superhero"."weight_kg" - "superhero"."height_cm") AS "o1", power(((1.5 / CAST("superhero"."height_cm" AS REAL)) + ((1 - CASE WHEN "superhero"."height_cm" = 366 THEN 0 WHEN "superhero"."full_name" > 'Xenomorph' THEN 1 WHEN (1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 THEN 3 WHEN "superhero"."id" = 35 THEN 0 WHEN ((1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 OR ("superhero"."weight_kg" - "superhero"."height_cm") > -106) THEN 1 ELSE 0 END) * 2)), 1.5) AS "o2", round(((1.5 / CAST("superhero"."height_cm" AS REAL)) + ((1 - CASE WHEN "superhero"."height_cm" = 366 THEN 0 WHEN "superhero"."full_name" > 'Xenomorph' THEN 1 WHEN (1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 THEN 3 WHEN "superhero"."id" = 35 THEN 0 WHEN ((1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 OR ("superhero"."weight_kg" - "superhero"."height_cm") > -106) THEN 1 ELSE 0 END) * 2)), 2) AS "o3", "superhero"."superhero_name" AS "o4", ((1.5 / CAST("superhero"."height_cm" AS REAL)) + ((1 - CASE WHEN "superhero"."height_cm" = 366 THEN 0 WHEN "superhero"."full_name" > 'Xenomorph' THEN 1 WHEN (1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 THEN 3 WHEN "superhero"."id" = 35 THEN 0 WHEN ((1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 OR ("superhero"."weight_kg" - "superhero"."height_cm") > -106) THEN 1 ELSE 0 END) * 2)) AS "o5", PERCENT_RANK() OVER (ORDER BY power(((1.5 / CAST("superhero"."height_cm" AS REAL)) + ((1 - CASE WHEN "superhero"."height_cm" = 366 THEN 0 WHEN "superhero"."full_name" > 'Xenomorph' THEN 1 WHEN (1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 THEN 3 WHEN "superhero"."id" = 35 THEN 0 WHEN ((1.5 / CAST("superhero"."height_cm" AS REAL)) < 0.01 OR ("superhero"."weight_kg" - "superhero"."height_cm") > -106) THEN 1 ELSE 0 END) * 2)), 1.5) ASC) AS "o6" FROM "race" AS "race" INNER JOIN "superhero" AS "superhero" ON "race"."id" = "superhero"."race_id"
```

- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)
- `-` column/column: unknown (disputed (model))
- `/` parameter WEIGHT: unknown (a constant)

## superhero-3 (attempt 114)

```sql
SELECT "colour"."colour" AS "o0", "superhero"."weight_kg" AS "o1", "hero_attribute"."attribute_value" AS "o2" FROM "hero_attribute" AS "hero_attribute" INNER JOIN "attribute" AS "attribute" ON "hero_attribute"."attribute_id" = "attribute"."id" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id" INNER JOIN "race" AS "race" ON "superhero"."race_id" = "race"."id" LEFT JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" INNER JOIN "alignment" AS "alignment" ON "superhero"."alignment_id" = "alignment"."id" WHERE "alignment"."alignment" > 'Bad'
```


## superhero-4 (attempt 28)

```sql
SELECT "superhero"."eye_colour_id" AS "o0", coalesce((("superhero"."weight_kg" * ((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1))) * 0.1), 0) AS "o1", "colour"."colour" AS "o2", ((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1)) AS "o3", CASE WHEN "superhero"."eye_colour_id" = 28 THEN (((1 - (round(CAST((("superhero"."weight_kg" * ((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1))) * 0.1) AS INTEGER), 2) + round(CAST((round("superhero"."height_cm", 2) * 0.1) AS REAL), 2))) * 0.2) / CAST(((1 - (round(CAST((("superhero"."weight_kg" * ((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1))) * 0.1) AS INTEGER), 2) + round(CAST((round("superhero"."height_cm", 2) * 0.1) AS REAL), 2))) * 0.2) AS REAL)) WHEN "colour"."colour" >= 'Gold' THEN 1 ELSE 0 END AS "o4" FROM "colour" AS "colour" INNER JOIN "superhero" AS "superhero" ON "colour"."id" = "superhero"."skin_colour_id" WHERE (("superhero"."weight_kg" * ((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1))) < 26913.6 AND NOT (((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1)) IS NULL)) ORDER BY ((round("superhero"."height_cm", 2) * 2) + (round("superhero"."height_cm", 2) * 0.1)) DESC
```

- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown

## superhero-5 (attempt 80)

```sql
SELECT "superhero"."skin_colour_id" AS "o0", ((1 - (CAST("superhero"."weight_kg" AS REAL) - CAST("superhero"."height_cm" AS REAL))) * CAST(((1 - CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + (("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + ((1 - "superhero"."weight_kg") + (CASE WHEN ("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) > "superhero"."skin_colour_id" THEN 10 ELSE 0 END * 0.75)))) AS REAL)) AS "o1", ((1 - CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + (("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + ((1 - "superhero"."weight_kg") + (CASE WHEN ("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) > "superhero"."skin_colour_id" THEN 10 ELSE 0 END * 0.75)))) AS "o2", "superhero"."superhero_name" AS "o3", (("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + ((1 - "superhero"."weight_kg") + (CASE WHEN ("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) > "superhero"."skin_colour_id" THEN 10 ELSE 0 END * 0.75))) AS "o4", ((("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + ((1 - "superhero"."weight_kg") + (CASE WHEN ("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) > "superhero"."skin_colour_id" THEN 10 ELSE 0 END * 0.75))) / CAST((1 - "superhero"."weight_kg") AS REAL)) AS "o5", CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END AS "o6" FROM "superhero" AS "superhero" ORDER BY ((("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) + ((1 - "superhero"."weight_kg") + (CASE WHEN ("superhero"."weight_kg" / CASE WHEN "superhero"."skin_colour_id" < 1 THEN 2 WHEN "superhero"."skin_colour_id" > 1 THEN 4 ELSE 0 END) > "superhero"."skin_colour_id" THEN 10 ELSE 0 END * 0.75))) / CAST((1 - "superhero"."weight_kg") AS REAL)) DESC LIMIT 10
```

- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` case/column: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `-` column/column: unknown (disputed (model))

## superhero-6 (attempt 199)

```sql
SELECT "colour"."id" AS "o0", COUNT(*) AS "o1" FROM "colour" AS "colour" GROUP BY "colour"."id" ORDER BY COUNT(*) DESC
```


## superhero-7 (attempt 125)

```sql
WITH "s4" AS (SELECT "gender"."id" AS "o0", AVG(CASE WHEN "gender"."gender" > 'N/A' THEN 5 WHEN "gender"."gender" > 'Female' THEN 1 ELSE 1 END) AS "o1", COUNT(*) AS "o2", AVG(CASE WHEN "gender"."gender" > 'N/A' THEN 5 WHEN "gender"."gender" > 'Female' THEN 1 ELSE 1 END) FILTER (WHERE "gender"."gender" > 'N/A') AS "o3" FROM "gender" AS "gender" GROUP BY "gender"."id") SELECT "s4"."o2" AS "o0", coalesce(("s4"."o1" / "s4"."o3"), 0) AS "o1", ("s4"."o1" / "s4"."o3") AS "o2" FROM "s4" AS "s4"
```

- `/` step output/step output: unknown

## superhero-8 (attempt 101)

```sql
SELECT "colour"."id" AS "o0", "colour"."colour" AS "o1", "superhero"."weight_kg" AS "o2", "superhero"."superhero_name" AS "o3", "superhero"."height_cm" AS "o4" FROM "publisher" AS "publisher" INNER JOIN "superhero" AS "superhero" ON "publisher"."id" = "superhero"."publisher_id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id"
```


## superhero-9 (attempt 129)

```sql
SELECT "superhero"."eye_colour_id" AS "o0", (((CASE WHEN "superhero"."superhero_name" = 'Wildfire' THEN 3 WHEN ("gender"."gender" > 'N/A' OR "gender"."gender" > 'Female' OR "gender"."gender" > 'Male') THEN 5 WHEN (CAST("superhero"."height_cm" AS REAL) = 160 AND "superhero"."eye_colour_id" > 7) THEN 4 WHEN "superhero"."eye_colour_id" > 7 THEN 3 ELSE 4 END + CASE WHEN "superhero"."eye_colour_id" = 15 THEN 3 WHEN "superhero"."full_name" != 'Jason Peter Todd' THEN 3 ELSE 1 END) / 5) / 0.25) AS "o1", "hero_attribute"."attribute_value" AS "o2", CAST(CASE WHEN "superhero"."eye_colour_id" = 15 THEN 3 WHEN "superhero"."full_name" != 'Jason Peter Todd' THEN 3 ELSE 1 END AS INTEGER) AS "o3", "superhero"."full_name" AS "o4" FROM "superhero" AS "superhero" LEFT JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" INNER JOIN "gender" AS "gender" ON "superhero"."gender_id" = "gender"."id" LEFT JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" ORDER BY ((CASE WHEN "superhero"."superhero_name" = 'Wildfire' THEN 3 WHEN ("gender"."gender" > 'N/A' OR "gender"."gender" > 'Female' OR "gender"."gender" > 'Male') THEN 5 WHEN (CAST("superhero"."height_cm" AS REAL) = 160 AND "superhero"."eye_colour_id" > 7) THEN 4 WHEN "superhero"."eye_colour_id" > 7 THEN 3 ELSE 4 END + CASE WHEN "superhero"."eye_colour_id" = 15 THEN 3 WHEN "superhero"."full_name" != 'Jason Peter Todd' THEN 3 ELSE 1 END) / 5) DESC LIMIT 5
```

- `/` parameter WEIGHT: unknown (a constant)
- `+` case/case: unknown
- `/` parameter WEIGHT: unknown (a constant)

## superhero-10 (attempt 121)

```sql
WITH "s1" AS (SELECT "superhero"."full_name" AS "o0", MAX("hero_attribute"."attribute_value") AS "o1", "hero_attribute"."hero_id" AS "o2" FROM "colour" AS "colour" INNER JOIN "superhero" AS "superhero" ON "colour"."id" = "superhero"."skin_colour_id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" GROUP BY "hero_attribute"."hero_id", "superhero"."full_name"), "s16" AS (SELECT "alignment"."alignment" AS "o0", round(SUM(((round(((((round((CAST(2 AS REAL) / 10), 2) * round((CAST(2 AS REAL) / 10), 2)) + (coalesce((CAST(4 AS INTEGER) * 10), 0) * round((CAST(2 AS REAL) / 10), 2))) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)))) + ((CAST(0 AS INTEGER) * 0.2) / (CAST((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) AS INTEGER) * 0.75))), 2) * 2) / coalesce((CAST(4 AS INTEGER) * 10), 0))), 2) AS "o1" FROM "alignment" AS "alignment" WHERE NOT ("alignment"."id" IS NULL) GROUP BY "alignment"."alignment" HAVING (SUM(((round(((((round((CAST(2 AS REAL) / 10), 2) * round((CAST(2 AS REAL) / 10), 2)) + (coalesce((CAST(4 AS INTEGER) * 10), 0) * round((CAST(2 AS REAL) / 10), 2))) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)))) + ((CAST(0 AS INTEGER) * 0.2) / (CAST((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) AS INTEGER) * 0.75))), 2) * 2) / coalesce((CAST(4 AS INTEGER) * 10), 0))) > (SUM((round(((((round((CAST(2 AS REAL) / 10), 2) * round((CAST(2 AS REAL) / 10), 2)) + (coalesce((CAST(4 AS INTEGER) * 10), 0) * round((CAST(2 AS REAL) / 10), 2))) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)))) + ((CAST(0 AS INTEGER) * 0.2) / (CAST((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) AS INTEGER) * 0.75))), 2) * 2)) / SUM(CASE WHEN (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) < ((round(((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (coalesce((CAST(0 AS INTEGER) * 0.2), 0) - (CAST(0 AS INTEGER) * 0.2))), 2) * 0.25) - ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) / 0.75) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (((sqrt(round(2, 2)) * sqrt(round(2, 2))) * round(2, 2)) * 0.75)))) THEN 0 WHEN ((round(((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (coalesce((CAST(0 AS INTEGER) * 0.2), 0) - (CAST(0 AS INTEGER) * 0.2))), 2) * 0.25) - ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) / 0.75) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (((sqrt(round(2, 2)) * sqrt(round(2, 2))) * round(2, 2)) * 0.75)))) = ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) * 5) / 0.2) THEN 1 ELSE 0 END) FILTER (WHERE "alignment"."alignment" IN ('Neutral', 'Neutral'))) AND ((round(((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (coalesce((CAST(0 AS INTEGER) * 0.2), 0) - (CAST(0 AS INTEGER) * 0.2))), 2) * 0.25) - ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) / 0.75) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (((sqrt(round(2, 2)) * sqrt(round(2, 2))) * round(2, 2)) * 0.75)))) > CASE WHEN (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) < ((round(((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (coalesce((CAST(0 AS INTEGER) * 0.2), 0) - (CAST(0 AS INTEGER) * 0.2))), 2) * 0.25) - ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) / 0.75) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (((sqrt(round(2, 2)) * sqrt(round(2, 2))) * round(2, 2)) * 0.75)))) THEN 0 WHEN ((round(((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (coalesce((CAST(0 AS INTEGER) * 0.2), 0) - (CAST(0 AS INTEGER) * 0.2))), 2) * 0.25) - ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) / 0.75) + ((coalesce((CAST(0 AS INTEGER) * 0.2), 0) / 0.2) + (((sqrt(round(2, 2)) * sqrt(round(2, 2))) * round(2, 2)) * 0.75)))) = ((((coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0)) * (coalesce((CAST(0 AS INTEGER) * 0.2), 0) * coalesce((CAST(0 AS INTEGER) * 0.2), 0))) * 5) / 0.2) THEN 1 ELSE 0 END)) SELECT "attribute"."id" AS "o0", "s16"."o0" AS "o1", "s1"."o1" AS "o2", "s1"."o2" AS "o3" FROM "s1" AS "s1" INNER JOIN "superhero" AS "superhero" ON "s1"."o2" = "superhero"."id" INNER JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" INNER JOIN "attribute" AS "attribute" ON "hero_attribute"."attribute_id" = "attribute"."id" INNER JOIN "race" AS "race" ON "superhero"."race_id" = "race"."id" LEFT JOIN "alignment" AS "alignment" ON "superhero"."alignment_id" = "alignment"."id" INNER JOIN "superpower" AS "superpower" ON "hero_power"."power_id" = "superpower"."id" INNER JOIN "publisher" AS "publisher" ON "superhero"."publisher_id" = "publisher"."id" INNER JOIN "gender" AS "gender" ON "superhero"."gender_id" = "gender"."id" INNER JOIN "s16" AS "s16" ON "s16"."o0" = "alignment"."alignment" ORDER BY "s1"."o1" DESC
```

- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `*` function/function: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `-` derived/derived: unknown
- `/` summary/summary: unknown

## superhero-11 (attempt 13)

```sql
SELECT "superhero"."race_id" AS "o0", "superhero"."height_cm" AS "o1", DENSE_RANK() OVER (ORDER BY "superhero"."height_cm" DESC) AS "o2", "superhero"."id" AS "o3", CASE WHEN "superhero"."id" > 189 THEN 2 WHEN "superhero"."race_id" > 24 THEN ("superhero"."weight_kg" / (1 - "superhero"."height_cm")) WHEN (DENSE_RANK() OVER (ORDER BY "superhero"."height_cm" DESC) = "superhero"."full_name" AND ("superhero"."weight_kg" / (1 - "superhero"."height_cm")) = -0.41) THEN 4 ELSE 0 END AS "o4", "superhero"."full_name" AS "o5", ("superhero"."weight_kg" / (1 - "superhero"."height_cm")) AS "o6", PERCENT_RANK() OVER (ORDER BY ("superhero"."weight_kg" / (1 - "superhero"."height_cm")) DESC) AS "o7", CAST("superhero"."weight_kg" AS REAL) AS "o8", CASE WHEN (1 - "superhero"."height_cm") > -177 THEN 1 WHEN "superhero"."full_name" = 'Erik Stephan Josten' THEN 1 ELSE 0 END AS "o9" FROM "race" AS "race" INNER JOIN "superhero" AS "superhero" ON "race"."id" = "superhero"."race_id" INNER JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" WHERE (CAST("superhero"."height_cm" AS INTEGER) >= 188 AND "superhero"."height_cm" >= 188 AND "superhero"."superhero_name" > 'Violator') ORDER BY "superhero"."full_name" DESC LIMIT 100
```

- `-` parameter WHOLE: unknown (a constant)
- `/` column/derived: unknown

## superhero-12 (attempt 1)

```sql
SELECT "superhero"."eye_colour_id" AS "o0", round(((("superhero"."weight_kg" / 72) + ("hero_attribute"."attribute_value" / 50)) * CASE WHEN "superhero"."eye_colour_id" > 7 THEN 0 WHEN ((("superhero"."weight_kg" / 72) + ("hero_attribute"."attribute_value" / 50)) >= 2.0 OR "superhero"."eye_colour_id" > 4) THEN 3 WHEN "gender"."gender" = 'Male' THEN 3 WHEN "gender"."gender" = 'N/A' THEN 1 WHEN ("superhero"."full_name" > 'Jason Peter Todd' AND "colour"."id" LIKE "colour"."id" AND "superhero"."eye_colour_id" > 7) THEN 1 ELSE 0 END), 2) AS "o1", ((("superhero"."weight_kg" / 72) + ("hero_attribute"."attribute_value" / 50)) * CASE WHEN "superhero"."eye_colour_id" > 7 THEN 0 WHEN ((("superhero"."weight_kg" / 72) + ("hero_attribute"."attribute_value" / 50)) >= 2.0 OR "superhero"."eye_colour_id" > 4) THEN 3 WHEN "gender"."gender" = 'Male' THEN 3 WHEN "gender"."gender" = 'N/A' THEN 1 WHEN ("superhero"."full_name" > 'Jason Peter Todd' AND "colour"."id" LIKE "colour"."id" AND "superhero"."eye_colour_id" > 7) THEN 1 ELSE 0 END) AS "o2", "superhero"."superhero_name" AS "o3", "superhero"."height_cm" AS "o4" FROM "gender" AS "gender" INNER JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" LEFT JOIN "race" AS "race" ON "superhero"."race_id" = "race"."id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id"
```

- `*` case/derived: unknown
- `+` derived/derived: unknown (disputed (model))
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)

## superhero-13 (attempt 197)

```sql
SELECT "superhero"."race_id" AS "o0", ("hero_attribute"."attribute_value" / round(CAST((1 - ((("superhero"."height_cm" / 100) + (("superhero"."height_cm" / 100) * 1.5)) + 4.45)) AS REAL), 2)) AS "o1" FROM "hero_attribute" AS "hero_attribute" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" ORDER BY ("hero_attribute"."attribute_value" / round(CAST((1 - ((("superhero"."height_cm" / 100) + (("superhero"."height_cm" / 100) * 1.5)) + 4.45)) AS REAL), 2)) DESC LIMIT 100
```

- `/` column/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)

## superhero-14 (attempt 180)

```sql
WITH "s1" AS (SELECT "hero_attribute"."hero_id" AS "o0" FROM "attribute" AS "attribute" INNER JOIN "hero_attribute" AS "hero_attribute" ON "attribute"."id" = "hero_attribute"."attribute_id" GROUP BY "hero_attribute"."hero_id") SELECT "s1"."o0" AS "o0" FROM "s1" AS "s1" ORDER BY "s1"."o0" ASC LIMIT 100
```


## superhero-15 (attempt 56)

```sql
SELECT "superhero"."publisher_id" AS "o0", "superhero"."race_id" AS "o1" FROM "alignment" AS "alignment" INNER JOIN "superhero" AS "superhero" ON "alignment"."id" = "superhero"."alignment_id"
```


## superhero-16 (attempt 116)

```sql
SELECT "race"."id" AS "o0", "superhero"."height_cm" AS "o1", "superhero"."full_name" AS "o2", "superhero"."weight_kg" AS "o3", CASE WHEN "superhero"."weight_kg" > 98 THEN 10 WHEN (CAST("superhero"."height_cm" AS REAL) = 122 AND "superhero"."weight_kg" > 98 AND "superhero"."weight_kg" = 70) THEN 5 ELSE 0 END AS "o4", RANK() OVER (ORDER BY "race"."id" ASC) AS "o5" FROM "race" AS "race" INNER JOIN "superhero" AS "superhero" ON "race"."id" = "superhero"."race_id"
```


## superhero-17 (attempt 50)

```sql
SELECT "superhero"."race_id" AS "o0", coalesce("superhero"."id", 0) AS "o1", "superhero"."height_cm" AS "o2", "superhero"."weight_kg" AS "o3" FROM "gender" AS "gender" LEFT JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" WHERE ("superhero"."full_name" = "gender"."gender" AND "superhero"."height_cm" > 160)
```


## superhero-18 (attempt 43)

```sql
SELECT "hero_power"."power_id" AS "o0", "hero_power"."hero_id" AS "o1", abs(((round(((1 - CASE WHEN "hero_power"."power_id" > 31 THEN 1 END) * 0.2), 2) * 10) - ((((1 - CASE WHEN "hero_power"."power_id" > 31 THEN 1 END) - CASE WHEN ((((1 - CASE WHEN "hero_power"."power_id" > 31 THEN 1 END) * 0.2) = (((coalesce(0, 0) + round(2, 2)) * 3) + ((round(2, 2) + abs(2)) * 0.5)) AND "hero_power"."hero_id" > 595 AND "hero_power"."hero_id" < 399 AND (round(2, 2) + abs(2)) = 4) OR "hero_power"."hero_id" = 447) THEN 0 ELSE 4 END) * 10) * ((CASE WHEN (round(2, 2) + abs(2)) > 4 THEN 5 ELSE 0 END * 0.2) * 0.5)))) AS "o2", ((round(((1 - CASE WHEN "hero_power"."power_id" > 31 THEN 1 END) * 0.2), 2) * 10) - ((((1 - CASE WHEN "hero_power"."power_id" > 31 THEN 1 END) - CASE WHEN ((((1 - CASE WHEN "hero_power"."power_id" > 31 THEN 1 END) * 0.2) = (((coalesce(0, 0) + round(2, 2)) * 3) + ((round(2, 2) + abs(2)) * 0.5)) AND "hero_power"."hero_id" > 595 AND "hero_power"."hero_id" < 399 AND (round(2, 2) + abs(2)) = 4) OR "hero_power"."hero_id" = 447) THEN 0 ELSE 4 END) * 10) * ((CASE WHEN (round(2, 2) + abs(2)) > 4 THEN 5 ELSE 0 END * 0.2) * 0.5))) AS "o3" FROM "hero_power" AS "hero_power"
```

- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` case/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: strong (rule)
- `*` parameter WEIGHT: unknown (a constant)

## superhero-19 (attempt 151)

```sql
SELECT "superhero"."full_name" AS "o0", "superhero"."height_cm" AS "o1" FROM "hero_attribute" AS "hero_attribute" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" ORDER BY "superhero"."full_name" DESC
```


## superhero-20 (attempt 86)

```sql
SELECT "superhero"."alignment_id" AS "o0", "gender"."gender" AS "o1", "hero_attribute"."attribute_value" AS "o2", round(CAST("superhero"."height_cm" AS REAL), 2) AS "o3" FROM "hero_power" AS "hero_power" LEFT JOIN "superhero" AS "superhero" ON "hero_power"."hero_id" = "superhero"."id" INNER JOIN "gender" AS "gender" ON "superhero"."gender_id" = "gender"."id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" WHERE ("superhero"."height_cm" = 193 AND "superhero"."superhero_name" = 'Wildfire')
```


