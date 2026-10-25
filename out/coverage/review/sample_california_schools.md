# california_schools: 20 random delivered programs

## california_schools-1 (attempt 72)

```sql
SELECT "frpm"."School Code" AS "o0", "schools"."MailStrAbr" AS "o1", "satscores"."enroll12" AS "o2", "frpm"."CDSCode" AS "o3", round(("frpm"."Percent (%) Eligible Free (K-12)" / ((1 - (((1 - "satscores"."enroll12") + (CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL) * 2)) + (CASE WHEN ((1 - "satscores"."enroll12") + (CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL) * 2)) = 339.0 THEN 2 END / 2))) + (CAST("frpm"."Enrollment (K-12)" AS INTEGER) * 2))), 2) AS "o4" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE ("satscores"."sname" = "schools"."AdmEmail3" AND "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" < 0.69 AND "schools"."AdmEmail3" > 'llamb@lcer.org' AND "satscores"."enroll12" = 58)
```

- `/` column/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## california_schools-2 (attempt 186)

```sql
SELECT "frpm"."School Code" AS "o0", "frpm"."Educational Option Type" AS "o1", CASE WHEN "frpm"."Educational Option Type" = 'State Special School' THEN 4 ELSE 0 END AS "o2" FROM "frpm" AS "frpm" WHERE "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" = "frpm"."Charter School Number" ORDER BY CASE WHEN "frpm"."Educational Option Type" = 'State Special School' THEN 4 ELSE 0 END DESC
```


## california_schools-3 (attempt 172)

```sql
WITH "s1" AS (SELECT "satscores"."AvgScrRead" AS "o0", round(AVG(("satscores"."NumGE1500" / "satscores"."AvgScrRead")), 2) AS "o1" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" WHERE ("satscores"."AvgScrRead" = 433 AND NOT ("schools"."CDSCode" IS NULL)) GROUP BY "satscores"."AvgScrRead") SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", CASE WHEN "s1"."o0" > 439 THEN 1 WHEN ("s1"."o0" = 533 AND "s1"."o0" != 494) THEN 4 WHEN ("s1"."o1" = ("s1"."o0" / round(CAST("s1"."o0" AS REAL), 2)) AND "s1"."o1" > ("s1"."o0" / "s1"."o0") AND ("s1"."o0" / "s1"."o0") > 1.0 AND ("s1"."o0" IN ("s1"."o0", "s1"."o0") OR "s1"."o0" = 450)) THEN 2 WHEN ("s1"."o0" / "s1"."o0") BETWEEN 1.0 AND 1.0 THEN 0 ELSE 10 END AS "o2", ("s1"."o0" / "s1"."o0") AS "o3", round(CAST("s1"."o0" AS REAL), 2) AS "o4" FROM "s1" AS "s1" WHERE "s1"."o0" > 520 ORDER BY round(CAST("s1"."o0" AS REAL), 2) DESC
```

- `/` column/column: unknown (disputed (model))
- `/` step output/step output: unknown (disputed (model))
- `/` step output/step output: unknown (disputed (model))

## california_schools-4 (attempt 42)

```sql
SELECT "frpm"."District Code" AS "o0", "satscores"."NumTstTakr" AS "o1" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" ORDER BY "satscores"."NumTstTakr" DESC
```


## california_schools-5 (attempt 116)

```sql
SELECT "frpm"."School Code" AS "o0", "frpm"."Free Meal Count (Ages 5-17)" AS "o1" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.69
```


## california_schools-6 (attempt 189)

```sql
SELECT "frpm"."County Code" AS "o0", "schools"."Latitude" AS "o1", "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" AS "o2", "schools"."NCESDist" AS "o3", (CAST("schools"."Latitude" AS REAL) * (CAST("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" AS REAL) / CAST("frpm"."Free Meal Count (K-12)" AS REAL))) AS "o4" FROM "frpm" AS "frpm" LEFT JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode"
```

- `*` column/derived: unknown (disputed (model))
- `/` column/column: unknown

## california_schools-7 (attempt 148)

```sql
WITH "s1" AS (SELECT "frpm"."District Code" AS "o0", AVG(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" - (("frpm"."Percent (%) Eligible Free (K-12)" * "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * "satscores"."NumGE1500"))) AS "o1" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" LEFT JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE ("schools"."AdmEmail3" = 'cschmidt@mjusd.com' AND (("frpm"."Enrollment (Ages 5-17)" > 518.0 AND "frpm"."Percent (%) Eligible Free (K-12)" < 0.76) OR "schools"."AdmEmail3" > 'sroner@echs.org')) GROUP BY "frpm"."District Code") SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", ((power(((CAST("s1"."o1" AS REAL) / (1 - "s1"."o1")) * ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)), 1.5) - (((CASE WHEN ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3) > ("s1"."o1" / "s1"."o1") THEN 10 WHEN (CAST("s1"."o1" AS REAL) / (1 - "s1"."o1")) > ("s1"."o1" / "s1"."o1") THEN 1 ELSE 0 END / (1 - CASE WHEN ("s1"."o0" = 68585 AND ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3) > "s1"."o0") THEN 1 WHEN "s1"."o0" = 66597 THEN 2 ELSE 0 END)) * 0.1) + ((CASE WHEN "s1"."o1" < ("s1"."o1" / ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)) THEN 3 WHEN ("s1"."o1" / ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)) = ("s1"."o1" / ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)) THEN 5 WHEN "s1"."o0" = 68585 THEN 2 WHEN "s1"."o0" > 67082 THEN 0 ELSE 0 END / 1.5) / 2))) * 10) AS "o2", ("s1"."o1" - "s1"."o1") AS "o3" FROM "s1" AS "s1" ORDER BY ((power(((CAST("s1"."o1" AS REAL) / (1 - "s1"."o1")) * ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)), 1.5) - (((CASE WHEN ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3) > ("s1"."o1" / "s1"."o1") THEN 10 WHEN (CAST("s1"."o1" AS REAL) / (1 - "s1"."o1")) > ("s1"."o1" / "s1"."o1") THEN 1 ELSE 0 END / (1 - CASE WHEN ("s1"."o0" = 68585 AND ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3) > "s1"."o0") THEN 1 WHEN "s1"."o0" = 66597 THEN 2 ELSE 0 END)) * 0.1) + ((CASE WHEN "s1"."o1" < ("s1"."o1" / ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)) THEN 3 WHEN ("s1"."o1" / ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)) = ("s1"."o1" / ((CASE WHEN "s1"."o0" > 69625 THEN 5 ELSE 1 END / 0.2) * 3)) THEN 5 WHEN "s1"."o0" = 68585 THEN 2 WHEN "s1"."o0" > 67082 THEN 0 ELSE 0 END / 1.5) / 2))) * 10) DESC
```

- `-` column/derived: unknown
- `*` column/derived: unknown
- `*` column/column: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/function: unknown
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` case/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `/` derived/step output: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `-` step output/step output: unknown (equal operands)

## california_schools-8 (attempt 197)

```sql
SELECT "schools"."CharterNum" AS "o0", "schools"."OpenDate" AS "o1", "schools"."Magnet" AS "o2", "frpm"."Free Meal Count (K-12)" AS "o3" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds"
```


## california_schools-9 (attempt 183)

```sql
SELECT "frpm"."School Code" AS "o0", "schools"."GSserved" AS "o1", CASE WHEN "schools"."Longitude" = -120.77703 THEN 5 ELSE 0 END AS "o2", (CASE WHEN "schools"."Longitude" = -120.77703 THEN 5 ELSE 0 END - CASE WHEN "schools"."Longitude" = -120.77703 THEN 5 ELSE 0 END) AS "o3", "schools"."Longitude" AS "o4", "frpm"."District Type" AS "o5", ((((0 - "frpm"."Free Meal Count (Ages 5-17)") + (((((("frpm"."Percent (%) Eligible Free (K-12)" + "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * 0.1) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" + "frpm"."Percent (%) Eligible FRPM (K-12)") * "schools"."Latitude")) + 5.62) / ("frpm"."FRPM Count (Ages 5-17)" + 98.0)) + ("frpm"."Enrollment (K-12)" * 0.75))) * 3) + ((((("frpm"."Free Meal Count (K-12)" / 82.0) / (1 - "frpm"."FRPM Count (K-12)")) + ("schools"."Longitude" * 0.75)) * 0.75) / 0.25)) AS "o6", PERCENT_RANK() OVER (PARTITION BY ((((("frpm"."Free Meal Count (K-12)" / 82.0) / (1 - "frpm"."FRPM Count (K-12)")) + ("schools"."Longitude" * 0.75)) * 0.75) / 0.25) ORDER BY "frpm"."District Type" DESC) AS "o7", coalesce("schools"."CDSCode", 0) AS "o8" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE ((((0 - "frpm"."Free Meal Count (Ages 5-17)") + (((((("frpm"."Percent (%) Eligible Free (K-12)" + "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * 0.1) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" + "frpm"."Percent (%) Eligible FRPM (K-12)") * "schools"."Latitude")) + 5.62) / ("frpm"."FRPM Count (Ages 5-17)" + 98.0)) + ("frpm"."Enrollment (K-12)" * 0.75))) * 3) + ((((("frpm"."Free Meal Count (K-12)" / 82.0) / (1 - "frpm"."FRPM Count (K-12)")) + ("schools"."Longitude" * 0.75)) * 0.75) / 0.25)) > 229.61 ORDER BY coalesce("schools"."CDSCode", 0) DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (disputed (model))
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `*` column/derived: unknown (disputed (model))
- `+` column/column: strong (doc)
- `*` parameter WEIGHT: unknown (a constant)
- `+` column/column: strong (doc)
- `-` parameter ZERO: unknown (a constant)
- `-` case/case: unknown (equal operands)

## california_schools-10 (attempt 19)

```sql
SELECT "frpm"."School Code" AS "o0", "frpm"."FRPM Count (K-12)" AS "o1", "schools"."NCESSchool" AS "o2", "schools"."StatusType" AS "o3" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE "schools"."NCESSchool" > '09508' ORDER BY "schools"."Longitude" DESC
```


## california_schools-11 (attempt 191)

```sql
WITH "s13" AS (SELECT DISTINCT "schools"."CDSCode" AS "o0", AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) AS "o1", CASE WHEN (AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) = 1.0 AND AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) > 1.0) THEN 3 WHEN (AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) > 1.0 AND AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) = 1.0 AND (((CASE WHEN AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) > 1.0 THEN 1 WHEN "schools"."CDSCode" >= '01316090131755' THEN 5 ELSE 0 END * 0.2) + ((AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) / ((sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * (sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))))) * 5)) - (((CASE WHEN AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) > 1.0 THEN 1 WHEN "schools"."CDSCode" >= '01316090131755' THEN 5 ELSE 0 END * 0.2) + ((AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) / ((sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * (sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))))) * 5)) * round(CAST(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) AS REAL), 2))) > (((((sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * (sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")))) * (round(CAST(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) AS REAL), 2) / 2)) + log(10, round((((sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * (sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")))) * (round(CAST(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) AS REAL), 2) / 2)), 2))) * 10)) THEN 1 WHEN log(10, round((((sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * (sqrt(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)"))) * AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")))) * (round(CAST(AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) AS REAL), 2) / 2)), 2)) < 10 THEN 3 WHEN AVG(("frpm"."Free Meal Count (K-12)" / "frpm"."Free Meal Count (K-12)")) < 1.0 THEN 1 ELSE 0 END AS "o2" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" WHERE ("schools"."Phone" IN ('(530) 235-4835', '(562) 868-0431') OR "schools"."Phone" = '(951) 276-7670') GROUP BY "schools"."CDSCode") SELECT "s13"."o2" AS "o0", "s13"."o1" AS "o1", "s13"."o0" AS "o2", LAG("s13"."o1") OVER (PARTITION BY "s13"."o2" ORDER BY "s13"."o1" DESC) AS "o3", CASE WHEN "s13"."o1" > ("s13"."o2" / "s13"."o1") THEN 4 ELSE 0 END AS "o4" FROM "s13" AS "s13"
```

- `/` column/column: unknown (equal operands)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/function: unknown
- `-` derived/derived: unknown
- `*` constant-derived: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)

## california_schools-12 (attempt 3)

```sql
SELECT "schools"."CharterNum" AS "o0", "schools"."Street" AS "o1", CAST("schools"."LastUpdate" AS REAL) AS "o2" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode"
```


## california_schools-13 (attempt 147)

```sql
SELECT "frpm"."CDSCode" AS "o0", "schools"."MailZip" AS "o1", "schools"."Street" AS "o2", "frpm"."Percent (%) Eligible FRPM (K-12)" AS "o3", CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) AS "o4" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE ("satscores"."dname" = 'San Jose Unified' AND CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL) = 8.0 AND "satscores"."rtype" < 'S' AND "frpm"."Percent (%) Eligible FRPM (K-12)" >= 0.68) ORDER BY "frpm"."Percent (%) Eligible Free (Ages 5-17)" DESC LIMIT 100
```


## california_schools-14 (attempt 80)

```sql
SELECT "schools"."CharterNum" AS "o0", "schools"."OpenDate" AS "o1", "schools"."Longitude" AS "o2", CAST((((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") * (("satscores"."AvgScrWrite" * 2) * 3)) / 10) AS REAL) AS "o3", round((((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") * (("satscores"."AvgScrWrite" * 2) * 3)) / 10), 2) AS "o4", PERCENT_RANK() OVER (ORDER BY "schools"."Longitude" DESC) AS "o5", "schools"."District" AS "o6" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" ORDER BY "schools"."District" DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (disputed (model))
- `/` column/column: unknown

## california_schools-15 (attempt 175)

```sql
SELECT "satscores"."cds" AS "o0", AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) AS "o1", COUNT(*) FILTER (WHERE "schools"."Latitude" > 37.83) AS "o2", abs(((AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) * round((AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) / 0.2), 2)) / ((AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) / 0.2) * 0.75))) AS "o3", round(CAST(AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) AS REAL), 2) AS "o4" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" GROUP BY "satscores"."cds" ORDER BY abs(((AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) * round((AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) / 0.2), 2)) / ((AVG(((("satscores"."NumGE1500" / "satscores"."NumTstTakr") * "schools"."Latitude") / 0.25)) / 0.2) * 0.75))) DESC
```

- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown (disputed (model))
- `/` column/column: strong (doc)
- `*` derived/summary: unknown

## california_schools-16 (attempt 71)

```sql
SELECT "frpm"."School Code" AS "o0", AVG(CASE WHEN "frpm"."School Code" BETWEEN CAST("frpm"."School Code" AS INTEGER) AND "schools"."GSoffered" THEN 3 WHEN "frpm"."Percent (%) Eligible Free (Ages 5-17)" = 0.863636363636364 THEN 3 ELSE 1 END) AS "o1", AVG(CASE WHEN "frpm"."School Code" BETWEEN CAST("frpm"."School Code" AS INTEGER) AND "schools"."GSoffered" THEN 3 WHEN "frpm"."Percent (%) Eligible Free (Ages 5-17)" = 0.863636363636364 THEN 3 ELSE 1 END) FILTER (WHERE ("frpm"."Percent (%) Eligible Free (Ages 5-17)" = 0.6 AND ((3 / (1 - "frpm"."Percent (%) Eligible FRPM (Ages 5-17)")) - (abs((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * CAST("frpm"."Percent (%) Eligible FRPM (K-12)" AS INTEGER))) * ("frpm"."Percent (%) Eligible Free (K-12)" / 0.3))) = 9.29)) AS "o2", AVG(CASE WHEN "frpm"."School Code" BETWEEN CAST("frpm"."School Code" AS INTEGER) AND "schools"."GSoffered" THEN 3 WHEN "frpm"."Percent (%) Eligible Free (Ages 5-17)" = 0.863636363636364 THEN 3 ELSE 1 END) FILTER (WHERE (("frpm"."Free Meal Count (Ages 5-17)" / 1000) * CAST("frpm"."Percent (%) Eligible FRPM (K-12)" AS INTEGER)) > 0.16) AS "o3", AVG(CASE WHEN "frpm"."School Code" BETWEEN CAST("frpm"."School Code" AS INTEGER) AND "schools"."GSoffered" THEN 3 WHEN "frpm"."Percent (%) Eligible Free (Ages 5-17)" = 0.863636363636364 THEN 3 ELSE 1 END) FILTER (WHERE "frpm"."Percent (%) Eligible FRPM (K-12)" = 0.65) AS "o4" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" GROUP BY "frpm"."School Code" ORDER BY AVG(CASE WHEN "frpm"."School Code" BETWEEN CAST("frpm"."School Code" AS INTEGER) AND "schools"."GSoffered" THEN 3 WHEN "frpm"."Percent (%) Eligible Free (Ages 5-17)" = 0.863636363636364 THEN 3 ELSE 1 END) FILTER (WHERE "frpm"."Percent (%) Eligible FRPM (K-12)" = 0.65) DESC
```

- `*` column/derived: unknown
- `/` parameter CONVERT: plausible (model)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: strong (doc)

## california_schools-17 (attempt 61)

```sql
SELECT "frpm"."County Code" AS "o0", "frpm"."School Code" AS "o1", CASE WHEN (("frpm"."Free Meal Count (Ages 5-17)" * "frpm"."Percent (%) Eligible FRPM (K-12)") / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) BETWEEN -76.53 AND -76.53 THEN ((((("frpm"."Free Meal Count (Ages 5-17)" * "frpm"."Percent (%) Eligible FRPM (K-12)") / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) + ("frpm"."Enrollment (K-12)" * 3)) / 0.25) ELSE 0 END AS "o2", "frpm"."Academic Year" AS "o3", ((("frpm"."FRPM Count (K-12)" / 1000) * ((coalesce("frpm"."Percent (%) Eligible Free (K-12)", 1) / (0 - "frpm"."Enrollment (Ages 5-17)")) * 0.5)) * 1000) AS "o4" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" WHERE (("frpm"."Free Meal Count (Ages 5-17)" * "frpm"."Percent (%) Eligible FRPM (K-12)") / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) > -76.53 ORDER BY CASE WHEN (("frpm"."Free Meal Count (Ages 5-17)" * "frpm"."Percent (%) Eligible FRPM (K-12)") / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) BETWEEN -76.53 AND -76.53 THEN ((((("frpm"."Free Meal Count (Ages 5-17)" * "frpm"."Percent (%) Eligible FRPM (K-12)") / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) / ((CAST("frpm"."Free Meal Count (K-12)" AS REAL) / (1 - "frpm"."Free Meal Count (Ages 5-17)")) * 2)) + ("frpm"."Enrollment (K-12)" * 3)) / 0.25) ELSE 0 END DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `*` column/column: unknown
- `*` parameter CONVERT: plausible (model)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/derived: unknown
- `-` parameter ZERO: unknown (a constant)
- `/` parameter CONVERT: plausible (model)

## california_schools-18 (attempt 170)

```sql
SELECT "schools"."EdOpsCode" AS "o0", "satscores"."AvgScrRead" AS "o1", "schools"."FundingType" AS "o2", CAST("satscores"."AvgScrRead" AS REAL) AS "o3", ((("satscores"."AvgScrMath" * 0.75) + (1 - ((((CAST(("satscores"."AvgScrMath" * 0.75) AS REAL) / 5) + "schools"."Latitude") + ("satscores"."NumGE1500" * 3)) + ("satscores"."NumTstTakr" / 1000)))) / (CASE WHEN "schools"."EdOpsCode" > 'HOMHOS' THEN 1 WHEN ((((CAST(("satscores"."AvgScrMath" * 0.75) AS REAL) / 5) + "schools"."Latitude") + ("satscores"."NumGE1500" * 3)) + ("satscores"."NumTstTakr" / 1000)) = "schools"."NCESDist" THEN 10 WHEN "schools"."EdOpsCode" > 'COMMDAY' THEN 3 WHEN "schools"."FundingType" > 'Not in CS funding model' THEN 3 ELSE 1 END * 1.5)) AS "o4" FROM "schools" AS "schools" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds"
```

- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter CONVERT: plausible (model)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (disputed (model))
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)

## california_schools-19 (attempt 173)

```sql
SELECT "frpm"."County Code" AS "o0", SUM(((round(("frpm"."FRPM Count (K-12)" / 1000), 2) * 10) * round((round(CAST((round(("frpm"."FRPM Count (K-12)" / 1000), 2) * 10) AS REAL), 2) + 0), 2))) AS "o1", round(CAST(AVG("frpm"."Percent (%) Eligible Free (Ages 5-17)") AS INTEGER), 2) AS "o2", AVG("frpm"."Enrollment (K-12)") AS "o3", COUNT(*) AS "o4", coalesce(AVG((round(("frpm"."FRPM Count (K-12)" / 1000), 2) * 10)), 0) AS "o5" FROM "frpm" AS "frpm" WHERE NOT ("frpm"."FRPM Count (Ages 5-17)" IS NULL) GROUP BY "frpm"."County Code" ORDER BY COUNT(*) DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)

## california_schools-20 (attempt 125)

```sql
SELECT "frpm"."District Code" AS "o0", CAST("schools"."OpenDate" AS REAL) AS "o1", "frpm"."School Name" AS "o2", power(CAST("frpm"."Free Meal Count (K-12)" AS REAL), 1.5) AS "o3" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" ORDER BY "schools"."OpenDate" DESC
```


