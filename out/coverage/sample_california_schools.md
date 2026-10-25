# california_schools: 20 random delivered programs

## california_schools-1 (attempt 89)

```sql
SELECT "schools"."EdOpsCode" AS "o0", "satscores"."NumTstTakr" AS "o1", "schools"."AdmFName2" AS "o2" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" ORDER BY "schools"."EdOpsCode" DESC
```


## california_schools-2 (attempt 54)

```sql
SELECT "schools"."CharterNum" AS "o0", "schools"."MailCity" AS "o1", CURRENT_DATE AS "o2", "satscores"."cds" AS "o3", sqrt(CURRENT_DATE) AS "o4" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds"
```


## california_schools-3 (attempt 138)

```sql
WITH "s1" AS (SELECT "frpm"."County Code" AS "o0", AVG("frpm"."Percent (%) Eligible FRPM (Ages 5-17)") AS "o1" FROM "frpm" AS "frpm" GROUP BY "frpm"."County Code"), "s5" AS (SELECT "schools"."AdmFName3" AS "o0", abs((SUM(CASE WHEN "schools"."AdmFName3" > 'Michelle' THEN 1 WHEN "schools"."AdmFName3" = 'Gerardo' THEN 1 ELSE 0 END) / SUM(CASE WHEN "schools"."AdmFName3" > 'Michelle' THEN 1 WHEN "schools"."AdmFName3" = 'Gerardo' THEN 1 ELSE 0 END))) AS "o1" FROM "schools" AS "schools" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" GROUP BY "schools"."AdmFName3", "schools"."MailZip") SELECT "s5"."o1" AS "o0", "s5"."o0" AS "o1", "s1"."o1" AS "o2", RANK() OVER (PARTITION BY "s1"."o1" ORDER BY "s5"."o0" DESC) AS "o3", PERCENT_RANK() OVER (ORDER BY "s5"."o0" DESC) AS "o4", NTILE(4) OVER (PARTITION BY "s1"."o1" ORDER BY "s1"."o1" DESC) AS "o5", CASE WHEN (PERCENT_RANK() OVER (ORDER BY "s5"."o0" DESC) > (("frpm"."Percent (%) Eligible Free (K-12)" / CAST("frpm"."Percent (%) Eligible Free (K-12)" AS REAL)) * 3) AND ("frpm"."Percent (%) Eligible Free (K-12)" / CAST("frpm"."Percent (%) Eligible Free (K-12)" AS REAL)) = 1.0 AND RANK() OVER (PARTITION BY "s1"."o1" ORDER BY "s5"."o0" DESC) < "schools"."AdmLName1") THEN 10 WHEN NTILE(4) OVER (PARTITION BY "s1"."o1" ORDER BY "s1"."o1" DESC) = (((power(CAST("schools"."Latitude" AS REAL), 1.5) * 1.5) * (abs((coalesce("frpm"."Percent (%) Eligible Free (Ages 5-17)", 1000000) * 100)) * 0.25)) / 0.25) THEN 10 WHEN PERCENT_RANK() OVER (ORDER BY "s5"."o0" DESC) > "schools"."AdmEmail1" THEN 1 WHEN PERCENT_RANK() OVER (ORDER BY "s5"."o0" DESC) = "schools"."AdmLName3" THEN 2 ELSE 1 END AS "o6" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" INNER JOIN "s5" AS "s5" ON "s5"."o0" = "schools"."AdmFName3" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "s1" AS "s1" ON "s1"."o0" = "frpm"."County Code" ORDER BY "schools"."AdmLName3" DESC LIMIT 100
```

- `/` summary/summary: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter CONVERT: strong (doc)
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown
- `*` parameter WEIGHT: unknown (a constant)

## california_schools-4 (attempt 186)

```sql
WITH "s6" AS (SELECT "frpm"."School Type" AS "o0", coalesce(AVG(CASE WHEN "frpm"."School Type" > 'Elementary Schools (Public)' THEN 0 WHEN ("schools"."StreetAbr" > '2607 Myrtle St.' AND "schools"."StreetAbr" > '4610 Foothill Blvd.') THEN 2 WHEN "schools"."StreetAbr" = '840 North Branciforte Ave.' THEN 1 WHEN "schools"."StreetAbr" BETWEEN "schools"."District" AND (SELECT "satscores"."cds" AS "o0" FROM "satscores" AS "satscores") THEN 5 ELSE 0 END), 0) AS "o1", sqrt(((AVG(CASE WHEN "frpm"."School Type" > 'Elementary Schools (Public)' THEN 0 WHEN ("schools"."StreetAbr" > '2607 Myrtle St.' AND "schools"."StreetAbr" > '4610 Foothill Blvd.') THEN 2 WHEN "schools"."StreetAbr" = '840 North Branciforte Ave.' THEN 1 WHEN "schools"."StreetAbr" BETWEEN "schools"."District" AND (SELECT "satscores"."cds" AS "o0" FROM "satscores" AS "satscores") THEN 5 ELSE 0 END) * round((AVG(CASE WHEN "frpm"."School Type" > 'Elementary Schools (Public)' THEN 0 WHEN ("schools"."StreetAbr" > '2607 Myrtle St.' AND "schools"."StreetAbr" > '4610 Foothill Blvd.') THEN 2 WHEN "schools"."StreetAbr" = '840 North Branciforte Ave.' THEN 1 WHEN "schools"."StreetAbr" BETWEEN "schools"."District" AND (SELECT "satscores"."cds" AS "o0" FROM "satscores" AS "satscores") THEN 5 ELSE 0 END) * coalesce(AVG(CASE WHEN "frpm"."School Type" > 'Elementary Schools (Public)' THEN 0 WHEN ("schools"."StreetAbr" > '2607 Myrtle St.' AND "schools"."StreetAbr" > '4610 Foothill Blvd.') THEN 2 WHEN "schools"."StreetAbr" = '840 North Branciforte Ave.' THEN 1 WHEN "schools"."StreetAbr" BETWEEN "schools"."District" AND (SELECT "satscores"."cds" AS "o0" FROM "satscores" AS "satscores") THEN 5 ELSE 0 END), 0)), 2)) / round((AVG(CASE WHEN "frpm"."School Type" > 'Elementary Schools (Public)' THEN 0 WHEN ("schools"."StreetAbr" > '2607 Myrtle St.' AND "schools"."StreetAbr" > '4610 Foothill Blvd.') THEN 2 WHEN "schools"."StreetAbr" = '840 North Branciforte Ave.' THEN 1 WHEN "schools"."StreetAbr" BETWEEN "schools"."District" AND (SELECT "satscores"."cds" AS "o0" FROM "satscores" AS "satscores") THEN 5 ELSE 0 END) * coalesce(AVG(CASE WHEN "frpm"."School Type" > 'Elementary Schools (Public)' THEN 0 WHEN ("schools"."StreetAbr" > '2607 Myrtle St.' AND "schools"."StreetAbr" > '4610 Foothill Blvd.') THEN 2 WHEN "schools"."StreetAbr" = '840 North Branciforte Ave.' THEN 1 WHEN "schools"."StreetAbr" BETWEEN "schools"."District" AND (SELECT "satscores"."cds" AS "o0" FROM "satscores" AS "satscores") THEN 5 ELSE 0 END), 0)), 2))) AS "o2", COUNT(*) AS "o3" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" GROUP BY "schools"."GSserved", "frpm"."School Type"), "s7" AS (SELECT "frpm"."County Code" AS "o0", ("frpm"."FRPM Count (K-12)" / round(CAST("frpm"."FRPM Count (K-12)" AS REAL), 2)) AS "o1" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" ORDER BY ("frpm"."FRPM Count (K-12)" / round(CAST("frpm"."FRPM Count (K-12)" AS REAL), 2)) DESC LIMIT 100) SELECT "s7"."o0" AS "o0", (("frpm"."Free Meal Count (Ages 5-17)" / "frpm"."FRPM Count (Ages 5-17)") * 0.2) AS "o1", "s6"."o2" AS "o2", ((1 - ("s6"."o1" * 0.75)) + ("frpm"."Enrollment (Ages 5-17)" * 0.5)) AS "o3" FROM "satscores" AS "satscores" LEFT JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" LEFT JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "s6" AS "s6" ON "s6"."o0" = "frpm"."School Type" INNER JOIN "s7" AS "s7" ON "s7"."o0" = "frpm"."County Code" WHERE ("frpm"."Free Meal Count (K-12)" = 60.0 AND "s7"."o1" > ((("frpm"."Free Meal Count (Ages 5-17)" / "frpm"."FRPM Count (Ages 5-17)") * 0.2) + ("s6"."o1" * 0.75))) ORDER BY "s6"."o2" DESC LIMIT 100
```

- `/` derived/derived: unknown
- `*` summary/summary: unknown
- `*` derived/summary: unknown
- `/` column/column: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/column: strong (doc)
- `+` derived/derived: unknown

## california_schools-5 (attempt 26)

```sql
SELECT "frpm"."District Code" AS "o0", "frpm"."Percent (%) Eligible FRPM (K-12)" AS "o1", "frpm"."County Name" AS "o2", "frpm"."Percent (%) Eligible Free (Ages 5-17)" AS "o3", "frpm"."Enrollment (K-12)" AS "o4", 1 AS "o5", "frpm"."District Type" AS "o6" FROM "frpm" AS "frpm" ORDER BY "frpm"."District Type" ASC LIMIT 100
```


## california_schools-6 (attempt 6)

```sql
SELECT "schools"."CDSCode" AS "o0", "schools"."County" AS "o1", CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL) AS "o2", "satscores"."AvgScrWrite" AS "o3", CASE WHEN "frpm"."FRPM Count (Ages 5-17)" > 502.0 THEN ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."FRPM Count (Ages 5-17)") ELSE 0 END AS "o4" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" ORDER BY CASE WHEN "frpm"."FRPM Count (Ages 5-17)" > 502.0 THEN ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."FRPM Count (Ages 5-17)") ELSE 0 END DESC LIMIT 100
```

- `/` column/column: unknown (equal operands)

## california_schools-7 (attempt 183)

```sql
SELECT "satscores"."cds" AS "o0", CAST("satscores"."NumTstTakr" AS REAL) AS "o1", round(((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) + ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")), 2) AS "o2", CAST(((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) + ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")) AS REAL) AS "o3", round(((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12"), 2) AS "o4", ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) + ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")) AS "o5", coalesce(((((((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) + ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")) / ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")) * 2) + ((round(((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12"), 2) / round(((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12"), 2)) + (round(((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) + ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")), 2) * 0.1))) * 10), 0) AS "o6" FROM "satscores" AS "satscores" ORDER BY ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) + ((CAST("satscores"."NumGE1500" AS REAL) / CAST("satscores"."enroll12" AS REAL)) / "satscores"."enroll12")) DESC
```

- `+` derived/derived: unknown
- `/` column/derived: unknown
- `/` column/column: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown

## california_schools-8 (attempt 97)

```sql
SELECT "schools"."CharterNum" AS "o0", "schools"."SOCType" AS "o1", "schools"."SOC" AS "o2", CAST("schools"."CharterNum" AS REAL) AS "o3", ((1 - (1 - (1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END))) * (((1 - (1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END)) / (1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END)) * (((1 - (1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END)) / (1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END)) / (1 - (1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END))))) AS "o4", round(CAST((1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END) AS REAL), 2) AS "o5" FROM "schools" AS "schools" ORDER BY "schools"."SOCType" DESC, round(CAST((1 - CASE WHEN "schools"."Website" != 'www.nmusd.us' THEN 4 ELSE 0 END) AS REAL), 2) DESC
```

- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)

## california_schools-9 (attempt 87)

```sql
SELECT "schools"."CDSCode" AS "o0", "frpm"."Free Meal Count (K-12)" AS "o1", CAST("schools"."Longitude" AS REAL) AS "o2" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" WHERE "schools"."Longitude" = -118.44949 ORDER BY "frpm"."Free Meal Count (K-12)" DESC LIMIT 100
```


## california_schools-10 (attempt 76)

```sql
SELECT "schools"."CharterNum" AS "o0", (((("frpm"."Free Meal Count (Ages 5-17)" / 78.0) / 1000) - (1 - (("frpm"."Free Meal Count (Ages 5-17)" / 78.0) / ("frpm"."Free Meal Count (Ages 5-17)" / 78.0)))) / 0.25) AS "o1", "frpm"."Enrollment (K-12)" AS "o2", "satscores"."AvgScrMath" AS "o3" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE ((((("frpm"."Free Meal Count (Ages 5-17)" / 78.0) / 1000) - (1 - (("frpm"."Free Meal Count (Ages 5-17)" / 78.0) / ("frpm"."Free Meal Count (Ages 5-17)" / 78.0)))) / 0.25) < 0.01 AND "satscores"."AvgScrMath" > 483) ORDER BY (1 - (("frpm"."Free Meal Count (Ages 5-17)" / 78.0) / ("frpm"."Free Meal Count (Ages 5-17)" / 78.0))) DESC
```

- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `/` parameter CONVERT: plausible (model)

## california_schools-11 (attempt 146)

```sql
SELECT "frpm"."CDSCode" AS "o0", ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") AS "o1", CASE WHEN "satscores"."dname" < 'New Jerusalem Elementary' THEN 1 WHEN ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") = 0.54 THEN 4 WHEN "schools"."MailZip" = '91710-4130' THEN 3 ELSE 0 END AS "o2", 1 AS "o3", CASE WHEN "frpm"."Enrollment (Ages 5-17)" = 4.0 THEN 4 ELSE 0 END AS "o4" FROM "schools" AS "schools" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE (((((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END > ("frpm"."Percent (%) Eligible Free (K-12)" / "frpm"."Percent (%) Eligible Free (K-12)") THEN 10 ELSE 0 END)) * 0.5) + (1 - (abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) * 0.1))))) * ("frpm"."Percent (%) Eligible FRPM (K-12)" + 0.39)) > ((((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END > ("frpm"."Percent (%) Eligible Free (K-12)" / "frpm"."Percent (%) Eligible Free (K-12)") THEN 10 ELSE 0 END)) * 0.5) + (1 - (abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) * 0.1))))) * ("frpm"."Percent (%) Eligible FRPM (K-12)" + 0.39)) AND ((((abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) * 0.1))) + (((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END > ("frpm"."Percent (%) Eligible Free (K-12)" / "frpm"."Percent (%) Eligible Free (K-12)") THEN 10 ELSE 0 END)) * 0.5) + (1 - (abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) * 0.1)))))) * 0.2) + ("satscores"."enroll12" * 0.75)) > ((((abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) * 0.1))) + (((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END > ("frpm"."Percent (%) Eligible Free (K-12)" / "frpm"."Percent (%) Eligible Free (K-12)") THEN 10 ELSE 0 END)) * 0.5) + (1 - (abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / abs(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) * 0.1)))))) * 0.2) + ("satscores"."enroll12" * 0.75)) AND NOT ("satscores"."enroll12" IS NULL) AND ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") > 0.54) ORDER BY "schools"."MailZip" DESC
```

- `/` column/column: plausible (model)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` case/case: unknown
- `/` column/column: unknown (equal operands)
- `/` parameter CONVERT: plausible (model)
- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)

## california_schools-12 (attempt 61)

```sql
SELECT "schools"."CharterNum" AS "o0", ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) AS "o1", CAST((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))) AS REAL) AS "o2", coalesce(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))), 1) AS "o3", ((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))) * 1.5) AS "o4", CASE WHEN "satscores"."rtype" > 'D' THEN 10 WHEN ("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))) < ("satscores"."NumGE1500" / (coalesce(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))), 1) + ((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))) * 1.5))) THEN 2 WHEN (((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) * 0.2) BETWEEN "satscores"."AvgScrRead" AND CASE WHEN "schools"."Charter" > 0 THEN 1 ELSE 0 END THEN 10 ELSE 0 END AS "o5", round((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) * 0.2), 2) AS "o6" FROM "frpm" AS "frpm" INNER JOIN "schools" AS "schools" ON "frpm"."CDSCode" = "schools"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE sqrt((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) * 0.2)) > "schools"."OpenDate" ORDER BY CASE WHEN "schools"."Charter" > 0 THEN 1 ELSE 0 END DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `-` column/derived: unknown

## california_schools-13 (attempt 144)

```sql
WITH "s1" AS (SELECT "schools"."StatusType" AS "o0", "frpm"."Free Meal Count (Ages 5-17)" AS "o1" FROM "schools" AS "schools" LEFT JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE "frpm"."Percent (%) Eligible Free (K-12)" > 0.3 ORDER BY "frpm"."Free Meal Count (Ages 5-17)" DESC LIMIT 100) SELECT (((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) AS "o0", ((((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) / 10) AS "o1", coalesce(COUNT(*) FILTER (WHERE ((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) > 3394.78), 0) AS "o2" FROM "s1" AS "s1" WHERE ("s1"."o0" > 'Closed' AND "s1"."o1" < 230.0 AND (((((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) / 10) * 1.5) = 50.92 AND (((((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) / 10) * 1.5) > 50.92) GROUP BY (((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10), ((((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) / 10)
```

- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` constant-derived: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `+` step output/step output: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## california_schools-14 (attempt 64)

```sql
SELECT "schools"."CDSCode" AS "o0", "schools"."Longitude" AS "o1", "schools"."Phone" AS "o2", 1 AS "o3" FROM "schools" AS "schools" WHERE "schools"."Longitude" < "schools"."Phone" ORDER BY "schools"."Phone" DESC LIMIT 5
```


## california_schools-15 (attempt 17)

```sql
WITH "s18" AS (SELECT "schools"."AdmFName3" AS "o0", AVG((((((1 - "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * (("frpm"."FRPM Count (K-12)" / 104.0) + ("frpm"."Free Meal Count (Ages 5-17)" * 5))) / 5) * round(((("frpm"."Percent (%) Eligible Free (K-12)" / (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) * (1 - (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10)))) + ("frpm"."Free Meal Count (K-12)" / ((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) * (1 - (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10))) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10)))) / 0.2), 2)) * ((("frpm"."FRPM Count (Ages 5-17)" / "frpm"."FRPM Count (Ages 5-17)") + 1.0) + ("frpm"."FRPM Count (Ages 5-17)" * (((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) * (1 - (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10))) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10)) / 0.75))))) FILTER (WHERE (((((1 - "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * (("frpm"."FRPM Count (K-12)" / 104.0) + ("frpm"."Free Meal Count (Ages 5-17)" * 5))) / 5) * round(((("frpm"."Percent (%) Eligible Free (K-12)" / (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) * (1 - (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10)))) + ("frpm"."Free Meal Count (K-12)" / ((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) * (1 - (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10))) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10)))) / 0.2), 2)) * ((("frpm"."FRPM Count (Ages 5-17)" / "frpm"."FRPM Count (Ages 5-17)") + 1.0) + ("frpm"."FRPM Count (Ages 5-17)" * (((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) * (1 - (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10))) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / 10)) / 0.75)))) = 32115509.0) AS "o1", abs((((((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) + 0) * (max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL)) + 0)) * (1 - ((round(CAST(((((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) + 0) * (max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL)) + 0)) AS REAL), 2) * 2) + (((((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) * (((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) + 0)) * ((((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) + 0) * (max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL)) + 0))) + (((((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) * (((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) + 0)) * ((((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) + 0) * (max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL)) + 0))) / ((CAST(((1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL))) * 10) AS REAL) / (1 - max(CAST("schools"."AdmFName3" AS INTEGER), CAST("schools"."AdmFName3" AS REAL)))) + 0))))))) AS "o2" FROM "schools" AS "schools" LEFT JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE ((((1 - "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * (("frpm"."FRPM Count (K-12)" / 104.0) + ("frpm"."Free Meal Count (Ages 5-17)" * 5))) / 5) > 72.12 AND (((1 - "frpm"."Percent (%) Eligible FRPM (Ages 5-17)") * (("frpm"."FRPM Count (K-12)" / 104.0) + ("frpm"."Free Meal Count (Ages 5-17)" * 5))) / 5) = 72.12) GROUP BY "schools"."AdmFName3") SELECT "s18"."o2" AS "o0", "s18"."o0" AS "o1", coalesce(CAST("s18"."o1" AS INTEGER), 1) AS "o2" FROM "s18" AS "s18" WHERE ("s18"."o1" = "s18"."o1" OR "s18"."o0" > (CAST(coalesce(CAST("s18"."o1" AS INTEGER), 1) AS REAL) / CAST(coalesce(CAST("s18"."o1" AS INTEGER), 1) AS INTEGER)))
```

- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: strong (doc)
- `+` parameter REFERENCE: unknown (a constant)
- `/` column/column: unknown (equal operands)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` column/derived: unknown
- `/` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: strong (doc)
- `/` step output/step output: unknown

## california_schools-16 (attempt 114)

```sql
SELECT "satscores"."cds" AS "o0", "schools"."Longitude" AS "o1", round(((CAST("satscores"."NumGE1500" AS REAL) / 1000) * 0.1), 2) AS "o2" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" ORDER BY (CAST("satscores"."NumGE1500" AS REAL) / 1000) DESC
```

- `/` parameter CONVERT: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)

## california_schools-17 (attempt 11)

```sql
SELECT "frpm"."School Code" AS "o0", (("satscores"."NumTstTakr" * 10) / 1000) AS "o1" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE (((((("satscores"."NumTstTakr" * 10) / 1000) + 0.83) + (((("satscores"."NumTstTakr" * 10) / 1000) + 0.83) + ((("satscores"."NumTstTakr" * 10) / 1000) + 0.83))) + ((1 - CASE WHEN (((("satscores"."NumTstTakr" * 10) / 1000) + 0.83) + (((("satscores"."NumTstTakr" * 10) / 1000) + 0.83) + ((("satscores"."NumTstTakr" * 10) / 1000) + 0.83))) < 4.98 THEN 2 END) / 0.1)) = "schools"."LastUpdate" AND NOT (((1 - CASE WHEN (((("satscores"."NumTstTakr" * 10) / 1000) + 0.83) + (((("satscores"."NumTstTakr" * 10) / 1000) + 0.83) + ((("satscores"."NumTstTakr" * 10) / 1000) + 0.83))) < 4.98 THEN 2 END) / 0.1) IS NULL)) ORDER BY (("satscores"."NumTstTakr" * 10) / 1000) ASC
```

- `/` parameter CONVERT: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: plausible (model)
- `+` derived/derived: plausible (model)
- `+` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown

## california_schools-18 (attempt 100)

```sql
SELECT "schools"."EdOpsCode" AS "o0", "schools"."StatusType" AS "o1", coalesce(AVG((coalesce(CAST("schools"."Latitude" AS REAL), 0) - "schools"."ClosedDate")), 0) AS "o2", abs(((coalesce(AVG((coalesce(CAST("schools"."Latitude" AS REAL), 0) - "schools"."ClosedDate")), 0) * coalesce(AVG((coalesce(CAST("schools"."Latitude" AS REAL), 0) - "schools"."ClosedDate")), 0)) * 0.1)) AS "o3" FROM "schools" AS "schools" GROUP BY "schools"."EdOpsCode", "schools"."StatusType" ORDER BY "schools"."StatusType" ASC LIMIT 10
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` summary/summary: unknown
- `-` column/column: unknown

## california_schools-19 (attempt 156)

```sql
SELECT "satscores"."cds" AS "o0", "schools"."LastUpdate" AS "o1", "frpm"."Free Meal Count (K-12)" AS "o2", "schools"."Longitude" AS "o3" FROM "schools" AS "schools" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" ORDER BY "frpm"."Free Meal Count (K-12)" ASC LIMIT 100
```


## california_schools-20 (attempt 167)

```sql
SELECT "schools"."EdOpsCode" AS "o0", "schools"."Latitude" AS "o1", "schools"."AdmLName2" AS "o2" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" ORDER BY "schools"."AdmLName2" DESC
```


