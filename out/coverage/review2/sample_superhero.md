# superhero: 20 random delivered programs

## superhero-1 (attempt 55)

```sql
SELECT "superhero"."full_name" AS "o0", "superhero"."weight_kg" AS "o1", "superhero"."height_cm" AS "o2", "alignment"."alignment" AS "o3" FROM "alignment" AS "alignment" INNER JOIN "superhero" AS "superhero" ON "alignment"."id" = "superhero"."alignment_id" INNER JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id" INNER JOIN "gender" AS "gender" ON "superhero"."gender_id" = "gender"."id" INNER JOIN "race" AS "race" ON "superhero"."race_id" = "race"."id" WHERE NOT ("superhero"."height_cm" IS NULL) ORDER BY "superhero"."full_name" ASC, "superhero"."height_cm" DESC LIMIT 100
```


## superhero-2 (attempt 117)

```sql
WITH "s1" AS (SELECT "publisher"."publisher_name" AS "o0", "superhero"."height_cm" AS "o1" FROM "colour" AS "colour" INNER JOIN "superhero" AS "superhero" ON "colour"."id" = "superhero"."skin_colour_id" INNER JOIN "publisher" AS "publisher" ON "superhero"."publisher_id" = "publisher"."id" ORDER BY "superhero"."height_cm" DESC LIMIT 10) SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", coalesce(((CASE WHEN "s1"."o0" > 'SyFy' THEN 0 WHEN "s1"."o1" BETWEEN 188 AND 188 THEN 1 WHEN ("s1"."o0" > 'HarperCollins' AND "s1"."o0" = 'Wildstorm' AND "s1"."o0" = 'DC Comics' AND ("s1"."o0" > 'Universal Studios' OR ("s1"."o1" = 198 AND "s1"."o0" = 'Marvel Comics'))) THEN 2 WHEN ("s1"."o0" > 'J. K. Rowling' AND "s1"."o1" = 305) THEN 1 ELSE 0 END * ((1 - CASE WHEN CASE WHEN "s1"."o0" > 'SyFy' THEN 0 WHEN "s1"."o1" BETWEEN 188 AND 188 THEN 1 WHEN ("s1"."o0" > 'HarperCollins' AND "s1"."o0" = 'Wildstorm' AND "s1"."o0" = 'DC Comics' AND ("s1"."o0" > 'Universal Studios' OR ("s1"."o1" = 198 AND "s1"."o0" = 'Marvel Comics'))) THEN 2 WHEN ("s1"."o0" > 'J. K. Rowling' AND "s1"."o1" = 305) THEN 1 ELSE 0 END BETWEEN ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) AND ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) THEN 5 WHEN ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) = (((1 - CASE WHEN ("s1"."o1" = 203 AND "s1"."o0" = '') THEN 1 ELSE 0 END) * ((CAST("s1"."o1" AS INTEGER) / 100) + 1.78)) + ((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) + ("s1"."o1" / 100))) THEN 5 WHEN (((1 - CASE WHEN ("s1"."o1" = 203 AND "s1"."o0" = '') THEN 1 ELSE 0 END) * ((CAST("s1"."o1" AS INTEGER) / 100) + 1.78)) + ((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) + ("s1"."o1" / 100))) < ("s1"."o1" - "s1"."o1") THEN 1 WHEN ("s1"."o1" - "s1"."o1") BETWEEN 0 AND 0 THEN 0 ELSE 0 END) * ((1 - CASE WHEN ("s1"."o1" - "s1"."o1") = 0 THEN 1 WHEN ("s1"."o1" / 100) BETWEEN 1.78 AND 1.78 THEN 5 WHEN ((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) < -0.78 AND ((CAST("s1"."o1" AS INTEGER) / 100) + 1.78) > 3.56 AND round((CAST("s1"."o1" AS INTEGER) / 100), 1) > 1.78) THEN 5 ELSE 0 END) / 0.5))) - (coalesce(CAST((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) AS REAL), 0) - ("s1"."o1" / 100))), 0) AS "o2", coalesce(CAST((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) AS REAL), 0) AS "o3" FROM "s1" AS "s1" ORDER BY coalesce(((CASE WHEN "s1"."o0" > 'SyFy' THEN 0 WHEN "s1"."o1" BETWEEN 188 AND 188 THEN 1 WHEN ("s1"."o0" > 'HarperCollins' AND "s1"."o0" = 'Wildstorm' AND "s1"."o0" = 'DC Comics' AND ("s1"."o0" > 'Universal Studios' OR ("s1"."o1" = 198 AND "s1"."o0" = 'Marvel Comics'))) THEN 2 WHEN ("s1"."o0" > 'J. K. Rowling' AND "s1"."o1" = 305) THEN 1 ELSE 0 END * ((1 - CASE WHEN CASE WHEN "s1"."o0" > 'SyFy' THEN 0 WHEN "s1"."o1" BETWEEN 188 AND 188 THEN 1 WHEN ("s1"."o0" > 'HarperCollins' AND "s1"."o0" = 'Wildstorm' AND "s1"."o0" = 'DC Comics' AND ("s1"."o0" > 'Universal Studios' OR ("s1"."o1" = 198 AND "s1"."o0" = 'Marvel Comics'))) THEN 2 WHEN ("s1"."o0" > 'J. K. Rowling' AND "s1"."o1" = 305) THEN 1 ELSE 0 END BETWEEN ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) AND ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) THEN 5 WHEN ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) = (((1 - CASE WHEN ("s1"."o1" = 203 AND "s1"."o0" = '') THEN 1 ELSE 0 END) * ((CAST("s1"."o1" AS INTEGER) / 100) + 1.78)) + ((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) + ("s1"."o1" / 100))) THEN 5 WHEN (((1 - CASE WHEN ("s1"."o1" = 203 AND "s1"."o0" = '') THEN 1 ELSE 0 END) * ((CAST("s1"."o1" AS INTEGER) / 100) + 1.78)) + ((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) + ("s1"."o1" / 100))) < ("s1"."o1" - "s1"."o1") THEN 1 WHEN ("s1"."o1" - "s1"."o1") BETWEEN 0 AND 0 THEN 0 ELSE 0 END) * ((1 - CASE WHEN ("s1"."o1" - "s1"."o1") = 0 THEN 1 WHEN ("s1"."o1" / 100) BETWEEN 1.78 AND 1.78 THEN 5 WHEN ((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) < -0.78 AND ((CAST("s1"."o1" AS INTEGER) / 100) + 1.78) > 3.56 AND round((CAST("s1"."o1" AS INTEGER) / 100), 1) > 1.78) THEN 5 ELSE 0 END) / 0.5))) - (coalesce(CAST((1 - round((CAST("s1"."o1" AS INTEGER) / 100), 1)) AS REAL), 0) - ("s1"."o1" / 100))), 0) ASC LIMIT 10
```

- `-` derived/derived: unknown
- `-` derived/derived: plausible (model)
- `/` parameter CONVERT: plausible (model)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` case/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `-` step output/step output: unknown (equal operands)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: plausible (model)
- `*` derived/derived: unknown
- `-` parameter WHOLE: strong (rule)

## superhero-3 (attempt 110)

```sql
SELECT "hero_power"."power_id" AS "o0", "superhero"."hair_colour_id" AS "o1" FROM "attribute" AS "attribute" INNER JOIN "hero_attribute" AS "hero_attribute" ON "attribute"."id" = "hero_attribute"."attribute_id" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" INNER JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id"
```


## superhero-4 (attempt 27)

```sql
SELECT "hero_power"."power_id" AS "o0", "hero_attribute"."attribute_value" AS "o1", CAST("superhero"."weight_kg" AS REAL) AS "o2", CAST("superhero"."height_cm" AS REAL) AS "o3" FROM "superhero" AS "superhero" LEFT JOIN "alignment" AS "alignment" ON "superhero"."alignment_id" = "alignment"."id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" LEFT JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" INNER JOIN "attribute" AS "attribute" ON "hero_attribute"."attribute_id" = "attribute"."id" INNER JOIN "race" AS "race" ON "superhero"."race_id" = "race"."id" ORDER BY "hero_attribute"."attribute_value" DESC
```


## superhero-5 (attempt 81)

```sql
SELECT "superhero"."alignment_id" AS "o0", "superhero"."height_cm" AS "o1", "superhero"."weight_kg" AS "o2", "superhero"."full_name" AS "o3" FROM "superhero" AS "superhero"
```


## superhero-6 (attempt 183)

```sql
SELECT "superhero"."race_id" AS "o0", ((("superhero"."height_cm" * ("superhero"."weight_kg" / 72)) * 0.5) * (((("superhero"."height_cm" * ("superhero"."weight_kg" / 72)) * 0.5) / "superhero"."weight_kg") + CASE WHEN "superhero"."race_id" = 4 THEN 2 WHEN "superhero"."race_id" > 24 THEN 3 ELSE 0 END)) AS "o1", ((("superhero"."height_cm" * ("superhero"."weight_kg" / 72)) * 0.5) / "superhero"."weight_kg") AS "o2" FROM "superpower" AS "superpower" LEFT JOIN "hero_power" AS "hero_power" ON "superpower"."id" = "hero_power"."power_id" INNER JOIN "superhero" AS "superhero" ON "hero_power"."hero_id" = "superhero"."id" ORDER BY ((("superhero"."height_cm" * ("superhero"."weight_kg" / 72)) * 0.5) * (((("superhero"."height_cm" * ("superhero"."weight_kg" / 72)) * 0.5) / "superhero"."weight_kg") + CASE WHEN "superhero"."race_id" = 4 THEN 2 WHEN "superhero"."race_id" > 24 THEN 3 ELSE 0 END)) DESC
```

- `*` derived/derived: unknown
- `+` case/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)

## superhero-7 (attempt 120)

```sql
SELECT "hero_power"."power_id" AS "o0", "superhero"."height_cm" AS "o1", "hero_attribute"."attribute_value" AS "o2", round("superhero"."height_cm", 1) AS "o3" FROM "publisher" AS "publisher" INNER JOIN "superhero" AS "superhero" ON "publisher"."id" = "superhero"."publisher_id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" INNER JOIN "attribute" AS "attribute" ON "hero_attribute"."attribute_id" = "attribute"."id" INNER JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id"
```


## superhero-8 (attempt 97)

```sql
SELECT "hero_attribute"."attribute_id" AS "o0", "hero_attribute"."hero_id" AS "o1", "hero_attribute"."attribute_value" AS "o2", (((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) + ((CAST((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) AS REAL) / (1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END)) * 10)) + (("hero_attribute"."attribute_value" / "hero_attribute"."attribute_value") * (1 - (("hero_attribute"."attribute_value" / "hero_attribute"."attribute_value") / ((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) + ((CAST((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) AS REAL) / (1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END)) * 10)))))) AS "o3", (1 - (("hero_attribute"."attribute_value" / "hero_attribute"."attribute_value") / ((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) + ((CAST((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) AS REAL) / (1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END)) * 10)))) AS "o4" FROM "hero_attribute" AS "hero_attribute" ORDER BY (("hero_attribute"."attribute_value" / "hero_attribute"."attribute_value") * (1 - (("hero_attribute"."attribute_value" / "hero_attribute"."attribute_value") / ((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) + ((CAST((1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END) AS REAL) / (1 - CASE WHEN ("hero_attribute"."attribute_id" = 4 AND "hero_attribute"."attribute_value" >= 50 AND "hero_attribute"."hero_id" < 383) THEN 4 WHEN "hero_attribute"."attribute_value" > 80 THEN 3 WHEN "hero_attribute"."attribute_value" > 25 THEN 5 ELSE 10 END)) * 10))))) DESC LIMIT 10
```

- `*` constant-derived: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `/` column/column: unknown (equal operands)
- `+` derived/derived: unknown

## superhero-9 (attempt 124)

```sql
WITH "s8" AS (SELECT "race"."id" AS "o0", (((((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5) + ((((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5) * 0.5)) * (1 - ((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) / (((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5)))) AS "o1", DENSE_RANK() OVER (ORDER BY "race"."id" DESC) AS "o2", (1 - ((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) / (((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5))) AS "o3", ((((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5) + ((((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5) * 0.5)) AS "o4", round(CAST((((coalesce(CAST(((CAST((0.75 / CAST(2 AS REAL)) AS REAL) / (0.75 / CAST(2 AS REAL))) + 0) AS REAL), 0) * 2) / 0.2) * 5) AS REAL), 2) AS "o5" FROM "race" AS "race") SELECT "s8"."o3" AS "o0", "s8"."o4" AS "o1", round(CAST("s8"."o5" AS INTEGER), 2) AS "o2" FROM "s8" AS "s8" WHERE ("s8"."o4" >= "s8"."o4" OR "s8"."o0" > 16)
```

- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `*` derived/derived: unknown

## superhero-10 (attempt 116)

```sql
WITH "s1" AS (SELECT "superhero"."eye_colour_id" AS "o0", "superhero"."weight_kg" AS "o1" FROM "superhero" AS "superhero" WHERE (NOT ("superhero"."weight_kg" IS NULL) AND "superhero"."weight_kg" = "superhero"."superhero_name") ORDER BY "superhero"."weight_kg" DESC LIMIT 10), "s10" AS (SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", (((((round(CAST("s1"."o1" AS REAL), 2) * 2) + (round(CAST((round(CAST("s1"."o1" AS REAL), 2) * 2) AS INTEGER), 2) * 0.2)) * (CAST(round(CAST((round(CAST("s1"."o1" AS REAL), 2) * 2) AS INTEGER), 2) AS REAL) / 10)) * (round(((round((CAST(round(CAST("s1"."o1" AS REAL), 2) AS REAL) * 0.25), 1) * 1.5) / 2), 2) * 10)) * 0.1) AS "o2" FROM "s1" AS "s1" INNER JOIN "colour" AS "colour" ON "s1"."o0" = "colour"."id" WHERE "s1"."o0" = 4 ORDER BY "s1"."o0" DESC LIMIT 100) SELECT "s10"."o1" AS "o0", "s10"."o2" AS "o1", "s10"."o0" AS "o2", ("s10"."o2" - "s10"."o0") AS "o3" FROM "s10" AS "s10" ORDER BY ("s10"."o2" - "s10"."o0") DESC LIMIT 100
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `-` step output/step output: unknown

## superhero-11 (attempt 16)

```sql
SELECT "gender"."id" AS "o0", "gender"."gender" AS "o1", coalesce((((CAST(((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * 0.75) / 5) AS REAL) / ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * 0.75) / 5)) * (1 - (CASE WHEN ("gender"."gender" < 'Female' AND "gender"."gender" > 'N/A' AND CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END = ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) / 0.5)) THEN 10 WHEN (CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) < ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) / 0.5) THEN 2 WHEN "gender"."id" < 1 THEN 4 ELSE 0 END * 10))) * 1.5), 0) AS "o2" FROM "gender" AS "gender" WHERE "gender"."gender" > 'N/A' ORDER BY coalesce((((CAST(((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * 0.75) / 5) AS REAL) / ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * 0.75) / 5)) * (1 - (CASE WHEN ("gender"."gender" < 'Female' AND "gender"."gender" > 'N/A' AND CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END = ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) / 0.5)) THEN 10 WHEN (CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) < ((CASE WHEN "gender"."gender" = 'Female' THEN 1 ELSE 1 END * round((CAST(3 AS REAL) / 1.5), 2)) / 0.5) THEN 2 WHEN "gender"."id" < 1 THEN 4 ELSE 0 END * 10))) * 1.5), 0) DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` case/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## superhero-12 (attempt 2)

```sql
SELECT "superhero"."alignment_id" AS "o0", "superhero"."height_cm" AS "o1" FROM "race" AS "race" LEFT JOIN "superhero" AS "superhero" ON "race"."id" = "superhero"."race_id" INNER JOIN "colour" AS "colour" ON "superhero"."eye_colour_id" = "colour"."id" INNER JOIN "alignment" AS "alignment" ON "superhero"."alignment_id" = "alignment"."id" LEFT JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" LEFT JOIN "attribute" AS "attribute" ON "hero_attribute"."attribute_id" = "attribute"."id"
```


## superhero-13 (attempt 181)

```sql
SELECT "superhero"."publisher_id" AS "o0", ((("hero_attribute"."attribute_value" / 50) * ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0)) * 0.75) AS "o1", "superhero"."height_cm" AS "o2", (((1 - (CASE WHEN ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) > 43200.0 AND ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0) = 86400.0) THEN 1 WHEN (((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) = 43200.0 THEN 2 WHEN "superhero"."full_name" = 'Warren Kenneth Worthington III' THEN 5 ELSE 0 END * 0.1)) + ((((("hero_attribute"."attribute_value" / 50) * ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0)) * 0.75) / "superhero"."height_cm") * 0.5)) + ((((("hero_attribute"."attribute_value" / 50) * ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0)) * 0.75) / "superhero"."height_cm") * 0.2)) AS "o3", CAST(((0.25 / CAST((CASE WHEN ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) > 43200.0 AND ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0) = 86400.0) THEN 1 WHEN (((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) = 43200.0 THEN 2 WHEN "superhero"."full_name" = 'Warren Kenneth Worthington III' THEN 5 ELSE 0 END * 0.1) AS REAL)) * (((("hero_attribute"."attribute_value" / 50) * ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0)) * 0.75) * "superhero"."height_cm")) AS REAL) AS "o4", power(CAST((0.25 / CAST((CASE WHEN ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) > 43200.0 AND ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0) = 86400.0) THEN 1 WHEN (((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) = 43200.0 THEN 2 WHEN "superhero"."full_name" = 'Warren Kenneth Worthington III' THEN 5 ELSE 0 END * 0.1) AS REAL)) AS REAL), 2) AS "o5" FROM "attribute" AS "attribute" LEFT JOIN "hero_attribute" AS "hero_attribute" ON "attribute"."id" = "hero_attribute"."attribute_id" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" ORDER BY power(CAST((0.25 / CAST((CASE WHEN ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) > 43200.0 AND ((((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) + 43200.0) = 86400.0) THEN 1 WHEN (((CAST("superhero"."weight_kg" AS REAL) * 1000) * 3) * 0.2) = 43200.0 THEN 2 WHEN "superhero"."full_name" = 'Warren Kenneth Worthington III' THEN 5 ELSE 0 END * 0.1) AS REAL)) AS REAL), 2) DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter CONVERT: plausible (model)
- `+` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `*` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## superhero-14 (attempt 169)

```sql
SELECT "superhero"."race_id" AS "o0", "hero_power"."hero_id" AS "o1", "superhero"."superhero_name" AS "o2" FROM "attribute" AS "attribute" INNER JOIN "hero_attribute" AS "hero_attribute" ON "attribute"."id" = "hero_attribute"."attribute_id" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" LEFT JOIN "alignment" AS "alignment" ON "superhero"."alignment_id" = "alignment"."id" INNER JOIN "hero_power" AS "hero_power" ON "superhero"."id" = "hero_power"."hero_id" ORDER BY "superhero"."superhero_name" ASC
```


## superhero-15 (attempt 58)

```sql
SELECT "superhero"."id" AS "o0", "hero_attribute"."attribute_value" AS "o1", CAST("superhero"."race_id" AS REAL) AS "o2", CASE WHEN "superhero"."race_id" = 51 THEN 1 WHEN "hero_attribute"."attribute_value" > 50 THEN 1 ELSE 3 END AS "o3", sqrt((("superhero"."height_cm" * (1 - ("superhero"."weight_kg" / 72))) * 0.5)) AS "o4" FROM "publisher" AS "publisher" INNER JOIN "superhero" AS "superhero" ON "publisher"."id" = "superhero"."publisher_id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id"
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)

## superhero-16 (attempt 111)

```sql
SELECT "superhero"."skin_colour_id" AS "o0", "superhero"."weight_kg" AS "o1", round(("superhero"."weight_kg" / round(CAST("superhero"."weight_kg" AS REAL), 2)), 2) AS "o2", DENSE_RANK() OVER (ORDER BY ("superhero"."weight_kg" / round(CAST("superhero"."weight_kg" AS REAL), 2)) DESC) AS "o3", "alignment"."alignment" AS "o4" FROM "gender" AS "gender" INNER JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" INNER JOIN "hero_attribute" AS "hero_attribute" ON "superhero"."id" = "hero_attribute"."hero_id" INNER JOIN "alignment" AS "alignment" ON "superhero"."alignment_id" = "alignment"."id" ORDER BY ("superhero"."weight_kg" / round(CAST("superhero"."weight_kg" AS REAL), 2)) DESC
```

- `/` column/column: unknown

## superhero-17 (attempt 54)

```sql
SELECT "superhero"."full_name" AS "o0", "superhero"."superhero_name" AS "o1", PERCENT_RANK() OVER (PARTITION BY "superhero"."full_name" ORDER BY "superhero"."superhero_name" DESC) AS "o2" FROM "publisher" AS "publisher" LEFT JOIN "superhero" AS "superhero" ON "publisher"."id" = "superhero"."publisher_id" INNER JOIN "race" AS "race" ON "superhero"."race_id" = "race"."id" WHERE (NOT ("superhero"."weight_kg" IS NULL) AND CAST("superhero"."weight_kg" AS REAL) = 86 AND "superhero"."height_cm" IN ((SELECT "alignment"."id" AS "o0" FROM "alignment" AS "alignment"), CASE WHEN "superhero"."superhero_name" > 'Wonder Girl' THEN 2 WHEN ("superhero"."superhero_name" > 'X-23' AND "superhero"."superhero_name" = 'X-Man') THEN 5 ELSE 0 END) AND "superhero"."height_cm" = 203) ORDER BY "superhero"."superhero_name" ASC
```


## superhero-18 (attempt 42)

```sql
SELECT "alignment"."id" AS "o0", AVG((((((coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0) / round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2)) + ((power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) + (round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)))) * 2) + (round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) + ((CAST(power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2) AS REAL) * 3) + (((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) - (1 - power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2)))))) + CASE WHEN (((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) - (1 - power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2))) = "alignment"."id" THEN ((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) * coalesce(CAST(coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0) AS REAL), 0)) ELSE 0 END)) AS "o1", AVG(((CAST(power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2) AS REAL) * 3) + (((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) - (1 - power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2))))) AS "o2", AVG(((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) * coalesce(CAST(coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0) AS REAL), 0))) AS "o3", (((AVG(((CAST(power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2) AS REAL) * 3) + (((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) - (1 - power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2))))) / 0.5) + (CASE WHEN (((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) - (1 - power(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS INTEGER), 2))) = "alignment"."id" THEN ((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) * coalesce(CAST(coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0) AS REAL), 0)) ELSE 0 END * round(CAST(round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) AS REAL), 2))) - ((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * AVG(((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) * coalesce(CAST(coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0) AS REAL), 0)))) + round((round(CAST(round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) AS REAL), 2) * coalesce(CAST((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) AS REAL), 0)), 2))) AS "o4" FROM "alignment" AS "alignment" GROUP BY "alignment"."id" ORDER BY AVG(((round(CAST((CAST(sqrt(2) AS REAL) / sqrt(2)) AS REAL), 2) * coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0)) * coalesce(CAST(coalesce(CAST(((CAST(sqrt(2) AS REAL) * 0.5) * (CAST(sqrt(2) AS REAL) / sqrt(2))) AS REAL), 0) AS REAL), 0))) DESC LIMIT 1
```

- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `/` function/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `*` derived/summary: unknown
- `+` derived/derived: unknown
- `*` case/derived: unknown
- `-` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` case/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/function: unknown
- `/` derived/derived: unknown

## superhero-19 (attempt 146)

```sql
WITH "s11" AS (SELECT "hero_attribute"."hero_id" AS "o0", AVG(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END) FILTER (WHERE ((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) + coalesce(CAST((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) AS INTEGER), 0)) = ("superhero"."height_cm" - (("hero_attribute"."attribute_value" + 50) / ((1 - "superhero"."height_cm") * (CASE WHEN ("superhero"."eye_colour_id" IN ((SELECT "attribute"."id" AS "o0" FROM "attribute" AS "attribute")) OR ("hero_attribute"."attribute_value" + 50) > 100) THEN 0 WHEN ("hero_attribute"."hero_id" > 383 AND "superhero"."weight_kg" > 98) THEN 1 ELSE 0 END * 0.5))))) AS "o1", round(CAST(MAX(("superhero"."height_cm" - (("hero_attribute"."attribute_value" + 50) / ((1 - "superhero"."height_cm") * (CASE WHEN ("superhero"."eye_colour_id" IN ((SELECT "attribute"."id" AS "o0" FROM "attribute" AS "attribute")) OR ("hero_attribute"."attribute_value" + 50) > 100) THEN 0 WHEN ("hero_attribute"."hero_id" > 383 AND "superhero"."weight_kg" > 98) THEN 1 ELSE 0 END * 0.5))))) AS REAL)) AS "o2", abs((((MAX(("superhero"."height_cm" - (("hero_attribute"."attribute_value" + 50) / ((1 - "superhero"."height_cm") * (CASE WHEN ("superhero"."eye_colour_id" IN ((SELECT "attribute"."id" AS "o0" FROM "attribute" AS "attribute")) OR ("hero_attribute"."attribute_value" + 50) > 100) THEN 0 WHEN ("hero_attribute"."hero_id" > 383 AND "superhero"."weight_kg" > 98) THEN 1 ELSE 0 END * 0.5))))) + (1 - ((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) + coalesce(CAST((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) AS INTEGER), 0)))) * ((1 - ((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) + coalesce(CAST((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) AS INTEGER), 0))) * (coalesce(CAST((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) AS INTEGER), 0) / 0.75))) - (CAST(round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2) AS REAL) / AVG(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END) FILTER (WHERE ((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) + coalesce(CAST((CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END * round(CAST(CASE WHEN "hero_attribute"."hero_id" = 731 THEN 5 ELSE 0 END AS REAL), 2)) AS INTEGER), 0)) = ("superhero"."height_cm" - (("hero_attribute"."attribute_value" + 50) / ((1 - "superhero"."height_cm") * (CASE WHEN ("superhero"."eye_colour_id" IN ((SELECT "attribute"."id" AS "o0" FROM "attribute" AS "attribute")) OR ("hero_attribute"."attribute_value" + 50) > 100) THEN 0 WHEN ("hero_attribute"."hero_id" > 383 AND "superhero"."weight_kg" > 98) THEN 1 ELSE 0 END * 0.5)))))))) AS "o3" FROM "hero_attribute" AS "hero_attribute" INNER JOIN "superhero" AS "superhero" ON "hero_attribute"."hero_id" = "superhero"."id" LEFT JOIN "attribute" AS "attribute" ON "hero_attribute"."attribute_id" = "attribute"."id" GROUP BY "hero_attribute"."hero_id", "superhero"."full_name", "attribute"."attribute_name") SELECT "s11"."o0" AS "o0", (("s11"."o3" * 3) * ("s11"."o3" * 3)) AS "o1", ("s11"."o3" * 3) AS "o2", RANK() OVER (ORDER BY ("s11"."o3" * 3) DESC) AS "o3" FROM "s11" AS "s11" WHERE ("s11"."o2" = ((((1 - "s11"."o2") * 2) * 1.5) * ("s11"."o1" * 0.1)) AND (1 - "s11"."o2") > "s11"."o1" AND (((((1 - "s11"."o2") * 2) * 1.5) * ("s11"."o1" * 0.1)) < (("s11"."o3" * 3) * ("s11"."o3" * 3)) OR (("s11"."o3" * 3) * ("s11"."o3" * 3)) > (("s11"."o3" * 3) * ("s11"."o3" * 3)))) ORDER BY ("s11"."o3" * 3) ASC
```

- `-` derived/derived: unknown
- `/` case/summary: unknown
- `-` column/derived: unknown
- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `*` case/case: unknown
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)
- `+` derived/summary: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## superhero-20 (attempt 85)

```sql
WITH "s1" AS (SELECT "superhero"."gender_id" AS "o0", CAST("superhero"."weight_kg" AS REAL) AS "o1" FROM "gender" AS "gender" INNER JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" ORDER BY "superhero"."gender_id" DESC LIMIT 5), "s15" AS (SELECT "superhero"."id" AS "o0", log(10, ((((CASE WHEN "superhero"."superhero_name" < 'Wildfire' THEN 1 WHEN "gender"."gender" < 'Female' THEN 3 WHEN "gender"."gender" BETWEEN ("superhero"."height_cm" * ("superhero"."weight_kg" * 3)) AND "gender"."id" THEN 10 ELSE 1 END * 0.2) + ((CASE WHEN "superhero"."superhero_name" < 'Wildfire' THEN 1 WHEN "gender"."gender" < 'Female' THEN 3 WHEN "gender"."gender" BETWEEN ("superhero"."height_cm" * ("superhero"."weight_kg" * 3)) AND "gender"."id" THEN 10 ELSE 1 END * 0.2) / "superhero"."height_cm")) + (((CAST(("superhero"."weight_kg" * 3) AS REAL) - CASE WHEN "superhero"."id" = 33 THEN 1 WHEN ("superhero"."weight_kg" * 3) = 216 THEN 1 WHEN "superhero"."id" > 377 THEN 3 ELSE 1 END) / 0.1) + 0)) * 1.5)) AS "o1", ((CAST(("superhero"."weight_kg" * 3) AS REAL) - CASE WHEN "superhero"."id" = 33 THEN 1 WHEN ("superhero"."weight_kg" * 3) = 216 THEN 1 WHEN "superhero"."id" > 377 THEN 3 ELSE 1 END) / 0.1) AS "o2" FROM "gender" AS "gender" INNER JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" ORDER BY log(10, ((((CASE WHEN "superhero"."superhero_name" < 'Wildfire' THEN 1 WHEN "gender"."gender" < 'Female' THEN 3 WHEN "gender"."gender" BETWEEN ("superhero"."height_cm" * ("superhero"."weight_kg" * 3)) AND "gender"."id" THEN 10 ELSE 1 END * 0.2) + ((CASE WHEN "superhero"."superhero_name" < 'Wildfire' THEN 1 WHEN "gender"."gender" < 'Female' THEN 3 WHEN "gender"."gender" BETWEEN ("superhero"."height_cm" * ("superhero"."weight_kg" * 3)) AND "gender"."id" THEN 10 ELSE 1 END * 0.2) / "superhero"."height_cm")) + (((CAST(("superhero"."weight_kg" * 3) AS REAL) - CASE WHEN "superhero"."id" = 33 THEN 1 WHEN ("superhero"."weight_kg" * 3) = 216 THEN 1 WHEN "superhero"."id" > 377 THEN 3 ELSE 1 END) / 0.1) + 0)) * 1.5)) ASC LIMIT 10) SELECT "s15"."o2" AS "o0" FROM "s1" AS "s1" INNER JOIN "gender" AS "gender" ON "s1"."o0" = "gender"."id" INNER JOIN "superhero" AS "superhero" ON "gender"."id" = "superhero"."gender_id" INNER JOIN "s15" AS "s15" ON "s15"."o0" = "superhero"."id" WHERE ("s15"."o1" > "superhero"."full_name" AND "s1"."o0" > 1 AND NOT ("s15"."o1" IS NULL))
```

- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown

