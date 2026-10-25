# california_schools: 20 random unknown substantive calculations (of 1020)

## california_schools-u1 (attempt 115) -- mechanical class: BOTH KNOWN

Node: `(ROUND(CAST("schools"."Latitude" AS REAL), 2) - ROUND(CAST("schools"."Latitude" AS REAL), 2))`

- left operand: unit 'degrees', kind '', quantity ('schools.Latitude', 'value')
- right operand: unit 'degrees', kind '', quantity ('schools.Latitude', 'value')
- stored columns under it: schools.Latitude [unit 'degrees' (model), kind '', scale 'interval']
- catalogue relations among them: none

Whole query:
```sql
SELECT "schools"."CDSCode" AS "o0", "schools"."DOCType" AS "o1", round(((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) / CAST((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) AS REAL)), 2) AS "o2", coalesce((round(((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) / CAST((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) AS REAL)), 2) - round(((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) / CAST((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) AS REAL)), 2)), 0) AS "o3", RANK() OVER (PARTITION BY coalesce((round(((round(CAST("schools"."Latitude" AS REAL), 2) - round(CAST("schools"."Latitude" AS REAL), 2)) / CAST((round(C
```

## california_schools-u2 (attempt 61) -- mechanical class: LOST

Node: `((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'thousand students', kind '', quantity ()
- stored columns under it: frpm.Free Meal Count (Ages 5-17) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Percent (%) Eligible FRPM (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']
- catalogue relations among them: frpm.Free Meal Count (Ages 5-17) comparable frpm.Percent (%) Eligible FRPM (Ages 5-17)

Whole query:
```sql
SELECT "schools"."CharterNum" AS "o0", ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) AS "o1", CAST((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23)) - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))) AS REAL) AS "o2", coalesce(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" - ((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) / 1.5) - (("frpm"."Free Meal Count (Ages 5-17)" / 1000) + 0.23))), 1) AS "o3", ((((((CASE WHEN "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" > 0.39 THEN 5 ELSE 0 END * 5) / 1.5) 
```

## california_schools-u3 (attempt 144) -- mechanical class: BOTH KNOWN

Node: `((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3))`

- left operand: unit 'thousand students', kind '', quantity ()
- right operand: unit 'thousand students × thousand students', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "schools"."StatusType" AS "o0", "frpm"."Free Meal Count (Ages 5-17)" AS "o1" FROM "schools" AS "schools" LEFT JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE "frpm"."Percent (%) Eligible Free (K-12)" > 0.3 ORDER BY "frpm"."Free Meal Count (Ages 5-17)" DESC LIMIT 100) SELECT (((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) AS "o0", ((((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1
```

## california_schools-u4 (attempt 69) -- mechanical class: LOST

Node: `(CAST("frpm"."Enrollment (K-12)" AS INTEGER) * (1 - ((("satscores"."NumTstTakr" * 3) * 5) + (CASE WHEN NOT (CAST("satscores"."AvgScrRead" AS REAL) IS NULL) THEN 4 WHEN "frpm"."Free Meal Count (K-12)" = 59.0 THEN 5 ELSE 3 END / 0.25))))`

- left operand: unit 'students', kind 'count', quantity ('frpm.Enrollment (K-12)', 'value')
- right operand: unit '', kind '', quantity ()
- stored columns under it: frpm.Enrollment (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Free Meal Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; satscores.AvgScrRead [unit 'points' (model), kind 'score', scale 'interval']; satscores.NumTstTakr [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: frpm.Free Meal Count (K-12) part_of frpm.Enrollment (K-12); frpm.Enrollment (K-12) comparable frpm.Free Meal Count (K-12); satscores.AvgScrRead comparable satscores.NumTstTakr; frpm.Free Meal Count (K-12) rate frpm.Enrollment (K-12)

Whole query:
```sql
SELECT "satscores"."cds" AS "o0", abs((CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / CAST(round(CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL), 2) AS REAL))) AS "o1", CASE WHEN (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / CAST(round(CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL), 2) AS REAL)) > 0.0 THEN 5 WHEN round(CAST("frpm"."FRPM Count (Ages 5-17)" AS REAL), 2) = 98.0 THEN ((CAST("frpm"."Enrollment (K-12)" AS INTEGER) * (1 - ((("satscores"."NumTstTakr" * 3) * 5) + (CASE WHEN NOT (CAST("satscores"."AvgScrRead" AS REAL) IS NULL) THEN 4 WHEN "frpm"."Free Meal Count (K-12)" = 59.0 THEN 5 ELSE 3 END / 0.25)))) + (CASE WHEN (1 - ((("satscores"."NumTstTakr" * 3) * 5) + (CASE WHEN NOT (CAST("satscores"."AvgScrRead" AS REAL) IS NULL) THEN 4 WHEN "frpm"."Free Meal Count (K-12)" = 59.0 THEN 5 ELSE 3 END / 0.25))) < (abs((CAST("frpm"."Percent (%) Eligible Free (
```

## california_schools-u5 (attempt 146) -- mechanical class: LOST

Node: `((((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'fraction', kind '', quantity ()
- stored columns under it: frpm.FRPM Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Free Meal Count (Ages 5-17) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Free Meal Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Percent (%) Eligible FRPM (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']; frpm.Percent (%) Eligible FRPM (K-12) [unit 'fraction' (doc), kind 'share', scale 'ratio']; frpm.Percent (%) Eligible Free (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']
- catalogue relations among them: frpm.Free Meal Count (K-12) part_of frpm.FRPM Count (K-12); frpm.Percent (%) Eligible Free (K-12) part_of frpm.Percent (%) Eligible FRPM (K-12); frpm.Free Meal Count (Ages 5-17) part_of frpm.FRPM Count (K-12); frpm.Free Meal Count (Ages 5-17) part_of frpm.Free Meal Count (K-12)

Whole query:
```sql
SELECT "frpm"."CDSCode" AS "o0", ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") AS "o1", CASE WHEN "satscores"."dname" < 'New Jerusalem Elementary' THEN 1 WHEN ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") = 0.54 THEN 4 WHEN "schools"."MailZip" = '91710-4130' THEN 3 ELSE 0 END AS "o2", 1 AS "o3", CASE WHEN "frpm"."Enrollment (Ages 5-17)" = 4.0 THEN 4 ELSE 0 END AS "o4" FROM "schools" AS "schools" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE (((((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)
```

## california_schools-u6 (attempt 133) -- mechanical class: LOST

Node: `(CAST((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) + (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / "frpm"."Percent (%) Eligible Free (Ages 5-17)")) AS REAL) / CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL))`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'fraction', kind 'share', quantity ('frpm.Percent (%) Eligible Free (Ages 5-17)', 'value')
- stored columns under it: frpm.Percent (%) Eligible Free (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "frpm"."CDSCode" AS "o0", ((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) + (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / "frpm"."Percent (%) Eligible Free (Ages 5-17)")) + (CAST((("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) + (("frpm"."Percent (%) Eligible Free (Ages 5-17)" / 0.3) / "frpm"."Percent (%) Eligible Free (Ages 5-17)")) AS REAL) / CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL))) AS "o1", "frpm"."Free Meal Count (K-12)" AS "o2" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" ORDER BY "frpm"."Free Meal Count (K-12)" DESC
```

## california_schools-u7 (attempt 162) -- mechanical class: WHOLE of LOST

Node: `(1 - ((CASE WHEN "schools"."Latitude" < 37.83 THEN 2 END / 0.1) / 3))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: schools.Latitude [unit 'degrees' (model), kind '', scale 'interval']
- catalogue relations among them: none

Whole query:
```sql
WITH "s9" AS (SELECT "schools"."CDSCode" AS "o0", "schools"."EdOpsCode" AS "o1", "satscores"."AvgScrMath" AS "o2", "satscores"."NumTstTakr" AS "o3", (((("satscores"."enroll12" + "satscores"."NumGE1500") + ("schools"."Latitude" + (CASE WHEN "schools"."Latitude" = 38.756023 THEN 1 WHEN "schools"."Latitude" < 37.83 THEN 0 ELSE 0 END / 0.25))) * (1 - ((CASE WHEN "schools"."Latitude" < 37.83 THEN 2 END / 0.1) / 3))) * (((("satscores"."enroll12" + "satscores"."NumGE1500") + ("schools"."Latitude" + (CASE WHEN "schools"."Latitude" = 38.756023 THEN 1 WHEN "schools"."Latitude" < 37.83 THEN 0 ELSE 0 END / 0.25))) * (1 - ((CASE WHEN "schools"."Latitude" < 37.83 THEN 2 END / 0.1) / 3))) * round(((CASE WHEN "schools"."Latitude" < 37.83 THEN 2 END / 0.1) / 3), 2))) AS "o4", "schools"."Longitude" AS "o5" FROM "schools" AS "schools" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscore
```

## california_schools-u8 (attempt 148) -- mechanical class: BOTH KNOWN

Node: `("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" / (((ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2) * ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2)) * ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2)) / ROUND(((CAST("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" AS`

- left operand: unit 'fraction', kind 'share', quantity ('frpm.Percent (%) Eligible FRPM (Ages 5-17)', 'value')
- right operand: unit 'students × students × students per fraction', kind '', quantity ()
- stored columns under it: frpm.Free Meal Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Percent (%) Eligible FRPM (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s15" AS (SELECT "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" AS "o0", "frpm"."Free Meal Count (K-12)" AS "o1", power(power(CAST(AVG(CASE WHEN "frpm"."District Code" = 66522 THEN (((("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) * (CASE WHEN (("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) > 2.0 THEN 0 ELSE 0 END * 2)) * CASE WHEN (CASE WHEN (("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) > 2.0 THEN 0 ELSE 0 END * 2) BETWEEN "schools"."StreetAbr" AND "satscores"."NumGE1500" THEN (CAST("frpm"."Free Meal Count (K-12)" AS REAL) * 2) WHEN "frpm"."Free Meal Count (K-12)" < 235.0 THEN 1 ELSE 1 END) END) AS REAL), 1.5), 2) AS "o2", round(CAST(AVG((((((("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) * (CASE WHEN (("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) > 2.0 THEN 0 ELSE 0 END * 2)) * CASE WHEN (
```

## california_schools-u9 (attempt 144) -- mechanical class: BOTH KNOWN

Node: `((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5))`

- left operand: unit 'students', kind '', quantity ()
- right operand: unit 'students', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "schools"."StatusType" AS "o0", "frpm"."Free Meal Count (Ages 5-17)" AS "o1" FROM "schools" AS "schools" LEFT JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" INNER JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" WHERE "frpm"."Percent (%) Eligible Free (K-12)" > 0.3 ORDER BY "frpm"."Free Meal Count (Ages 5-17)" DESC LIMIT 100) SELECT (((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1.5)) / 10) AS "o0", ((((("s1"."o1" * 3) * 3) / (((1 - ((((("s1"."o1" + "s1"."o1") / 5) / (("s1"."o1" + "s1"."o1") / 5)) * (1 - (("s1"."o1" + 230.0) / 5))) / 1000)) * (((((("s1"."o1" + 230.0) / 1.5) / 1000) * (1 - (("s1"."o1" + 230.0) / 1000))) * 0.75) * 3)) * 1
```

## california_schools-u10 (attempt 124) -- mechanical class: LOST

Node: `("frpm"."FRPM Count (K-12)" / ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)"))`

- left operand: unit 'students', kind 'count', quantity ('frpm.FRPM Count (K-12)', 'value')
- right operand: unit '', kind '', quantity ()
- stored columns under it: frpm.Enrollment (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.FRPM Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: frpm.FRPM Count (K-12) part_of frpm.Enrollment (K-12); frpm.Enrollment (K-12) comparable frpm.FRPM Count (K-12); frpm.FRPM Count (K-12) rate frpm.Enrollment (K-12)

Whole query:
```sql
SELECT "schools"."CDSCode" AS "o0", "schools"."School" AS "o1", "schools"."NCESSchool" AS "o2", round((("frpm"."Enrollment (Ages 5-17)" * 3) + ("frpm"."FRPM Count (K-12)" / ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)"))), 4) AS "o3", CASE WHEN (("frpm"."Enrollment (Ages 5-17)" * 3) + ("frpm"."FRPM Count (K-12)" / ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)"))) BETWEEN 1554.54 AND 1554.54 THEN 2 WHEN "schools"."FundingType" = 'Not in CS funding model' THEN 1 WHEN "schools"."FundingType" = 'Directly funded' THEN 1 WHEN ("schools"."NCESSchool" > '09509' AND ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)") > 529.0) THEN ("frpm"."Enrollment (K-12)" * 0.1) WHEN (CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12
```

## california_schools-u11 (attempt 161) -- mechanical class: BOTH KNOWN

Node: `(CAST("s3"."o1" AS REAL) / "s3"."o1")`

- left operand: unit 'fraction', kind 'share', quantity ()
- right operand: unit 'fraction', kind 'share', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s2" AS (SELECT "frpm"."School Name" AS "o0", AVG("frpm"."Percent (%) Eligible Free (K-12)") AS "o1", round(CAST(AVG(((CAST("frpm"."Percent (%) Eligible Free (K-12)" AS INTEGER) / "frpm"."Percent (%) Eligible Free (K-12)") - (1 - "frpm"."Percent (%) Eligible Free (Ages 5-17)"))) AS REAL), 2) AS "o2", round(CAST(AVG((1 - "frpm"."Percent (%) Eligible Free (Ages 5-17)")) AS REAL), 2) AS "o3", sqrt(AVG((1 - "frpm"."Percent (%) Eligible Free (Ages 5-17)"))) AS "o4", CURRENT_DATE AS "o5" FROM "frpm" AS "frpm" WHERE "frpm"."School Name" IN ('Fairview Elementary', 'Roosevelt Elementary') GROUP BY "frpm"."School Name"), "s3" AS (SELECT "s2"."o5" AS "o0", AVG("s2"."o3") AS "o1", coalesce(AVG("s2"."o1"), 0) AS "o2", AVG("s2"."o4") AS "o3", sqrt(round(CAST(AVG("s2"."o2") AS REAL), 2)) AS "o4", round(CAST(SUM("s2"."o3") AS REAL), 1) AS "o5" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm"
```

## california_schools-u12 (attempt 103) -- mechanical class: NO UNIT

Node: `((("satscores"."NumTstTakr" + "satscores"."enroll12") + 303.0) + (CAST((1 - CASE WHEN "satscores"."cds" < '10621661030287' THEN 2 WHEN "satscores"."cds" > '10621581032150' THEN 4 ELSE 0 END) AS REAL) * 5))`

- left operand: unit 'students', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: satscores.NumTstTakr [unit 'students' (model), kind 'count', scale 'ratio']; satscores.cds [unit '' (-), kind '', scale '']; satscores.enroll12 [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: satscores.NumTstTakr part_of satscores.enroll12; satscores.NumTstTakr comparable satscores.enroll12; satscores.NumTstTakr rate satscores.enroll12

Whole query:
```sql
SELECT "satscores"."cds" AS "o0", ((1 - (CAST("satscores"."AvgScrRead" AS REAL) - CAST("satscores"."AvgScrMath" AS REAL))) * CAST(((1 - CASE WHEN "satscores"."cds" < '10621661030287' THEN 2 WHEN "satscores"."cds" > '10621581032150' THEN 4 ELSE 0 END) + (("satscores"."NumGE1500" / 1000) + (((("satscores"."NumTstTakr" + "satscores"."enroll12") + 303.0) + (CAST((1 - CASE WHEN "satscores"."cds" < '10621661030287' THEN 2 WHEN "satscores"."cds" > '10621581032150' THEN 4 ELSE 0 END) AS REAL) * 5)) * 3))) AS REAL)) AS "o1", coalesce((((1 - (CAST("satscores"."AvgScrRead" AS REAL) - CAST("satscores"."AvgScrMath" AS REAL))) * CAST(((1 - CASE WHEN "satscores"."cds" < '10621661030287' THEN 2 WHEN "satscores"."cds" > '10621581032150' THEN 4 ELSE 0 END) + (("satscores"."NumGE1500" / 1000) + (((("satscores"."NumTstTakr" + "satscores"."enroll12") + 303.0) + (CAST((1 - CASE WHEN "satscores"."cds" < '10621
```

## california_schools-u13 (attempt 9) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - ("satscores"."enroll12" * 5))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'students', kind '', quantity ()
- stored columns under it: satscores.enroll12 [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s3" AS (SELECT "satscores"."cds" AS "o0", "schools"."CharterNum" AS "o1", "schools"."State" AS "o2", (CAST("satscores"."NumGE1500" AS REAL) * (1 - ("satscores"."enroll12" * 5))) AS "o3" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" ORDER BY (CAST("satscores"."NumGE1500" AS REAL) * (1 - ("satscores"."enroll12" * 5))) DESC LIMIT 10) SELECT "s3"."o0" AS "o0", "s3"."o3" AS "o1", "s3"."o2" AS "o2", "s3"."o1" AS "o3", CASE WHEN NOT (CASE WHEN "s3"."o1" = '0756' THEN 10 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 1 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 0 ELSE 0 END IS NULL) THEN 2 WHEN ("s3"."o3" - "s3"."o3") = ((1 - (1 - CASE WHEN CASE WHEN "s3"."o1" = '0756' THEN 10 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 1 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 0 ELSE 0 END = ((("s3"."o3" / "s3"."o3") * (((round("s3".
```

## california_schools-u14 (attempt 148) -- mechanical class: BOTH KNOWN

Node: `((1 - (ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2) / ((ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2) * ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2)) * ROUND(CAST("frpm"."Free Meal Count (K-12)" AS INTEGER), 2)))) + ("frpm"."Percent (%) Eligible FRPM (Ages 5-`

- left operand: unit 'students per students × students × students', kind '', quantity ()
- right operand: unit 'fraction per students × students × students per fraction', kind '', quantity ()
- stored columns under it: frpm.Free Meal Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Percent (%) Eligible FRPM (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s15" AS (SELECT "frpm"."Percent (%) Eligible FRPM (Ages 5-17)" AS "o0", "frpm"."Free Meal Count (K-12)" AS "o1", power(power(CAST(AVG(CASE WHEN "frpm"."District Code" = 66522 THEN (((("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) * (CASE WHEN (("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) > 2.0 THEN 0 ELSE 0 END * 2)) * CASE WHEN (CASE WHEN (("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) > 2.0 THEN 0 ELSE 0 END * 2) BETWEEN "schools"."StreetAbr" AND "satscores"."NumGE1500" THEN (CAST("frpm"."Free Meal Count (K-12)" AS REAL) * 2) WHEN "frpm"."Free Meal Count (K-12)" < 235.0 THEN 1 ELSE 1 END) END) AS REAL), 1.5), 2) AS "o2", round(CAST(AVG((((((("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) * (CASE WHEN (("frpm"."FRPM Count (K-12)" / "frpm"."FRPM Count (K-12)") + 1.0) > 2.0 THEN 0 ELSE 0 END * 2)) * CASE WHEN (
```

## california_schools-u15 (attempt 95) -- mechanical class: BOTH KNOWN

Node: `(("frpm"."Percent (%) Eligible Free (K-12)" / 0.3) * "frpm"."Free Meal Count (Ages 5-17)")`

- left operand: unit 'fraction', kind '', quantity ()
- right operand: unit 'students', kind 'count', quantity ('frpm.Free Meal Count (Ages 5-17)', 'value')
- stored columns under it: frpm.Free Meal Count (Ages 5-17) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.Percent (%) Eligible Free (K-12) [unit 'fraction' (doc), kind 'share', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "schools"."EdOpsCode" AS "o0", ((((("frpm"."Percent (%) Eligible Free (K-12)" / 0.3) * "frpm"."Free Meal Count (Ages 5-17)") / 5) * 0.5) + ((1 - coalesce(CAST((((("frpm"."Percent (%) Eligible Free (K-12)" / 0.3) * "frpm"."Free Meal Count (Ages 5-17)") / 5) * 0.5) AS REAL), 0)) + 0)) AS "o1", round(coalesce(CAST((((("frpm"."Percent (%) Eligible Free (K-12)" / 0.3) * "frpm"."Free Meal Count (Ages 5-17)") / 5) * 0.5) AS REAL), 0), 2) AS "o2", CAST("schools"."LastUpdate" AS REAL) AS "o3", "frpm"."Percent (%) Eligible FRPM (K-12)" AS "o4", round("schools"."LastUpdate", 2) AS "o5", CASE WHEN (("frpm"."Percent (%) Eligible Free (K-12)" / 0.3) * "frpm"."Free Meal Count (Ages 5-17)") = 436.21 THEN 1 WHEN (1 - coalesce(CAST((((("frpm"."Percent (%) Eligible Free (K-12)" / 0.3) * "frpm"."Free Meal Count (Ages 5-17)") / 5) * 0.5) AS REAL), 0)) > "schools"."GSoffered" THEN 5 WHEN "schools"."GSo
```

## california_schools-u16 (attempt 146) -- mechanical class: WHOLE of LOST

Node: `(1 - (ABS(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)) / (((CAST("satscores"."NumGE1500" AS REAL) / "satscores"."NumGE1500") + (CAST("frpm"."Percent (%) Eligible Free (Ages 5-17)" AS REAL) / ABS(("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" * 0.75)))) - (((CAST("satscores"."NumGE1500" `

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: frpm.Percent (%) Eligible FRPM (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']; frpm.Percent (%) Eligible Free (Ages 5-17) [unit 'fraction' (doc), kind 'share', scale 'ratio']; satscores.NumGE1500 [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: frpm.Percent (%) Eligible Free (Ages 5-17) part_of frpm.Percent (%) Eligible FRPM (Ages 5-17); frpm.Percent (%) Eligible FRPM (Ages 5-17) comparable frpm.Percent (%) Eligible Free (Ages 5-17)

Whole query:
```sql
SELECT "frpm"."CDSCode" AS "o0", ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") AS "o1", CASE WHEN "satscores"."dname" < 'New Jerusalem Elementary' THEN 1 WHEN ("frpm"."FRPM Count (Ages 5-17)" / "frpm"."Enrollment (Ages 5-17)") = 0.54 THEN 4 WHEN "schools"."MailZip" = '91710-4130' THEN 3 ELSE 0 END AS "o2", 1 AS "o3", CASE WHEN "frpm"."Enrollment (Ages 5-17)" = 4.0 THEN 4 ELSE 0 END AS "o4" FROM "schools" AS "schools" LEFT JOIN "satscores" AS "satscores" ON "schools"."CDSCode" = "satscores"."cds" INNER JOIN "frpm" AS "frpm" ON "schools"."CDSCode" = "frpm"."CDSCode" WHERE (((((((("frpm"."Free Meal Count (Ages 5-17)" / 1000) * 10) + (((("frpm"."Free Meal Count (K-12)" / 1000) * 0.25) * 0.25) * 3)) * (CASE WHEN "frpm"."FRPM Count (K-12)" < 511.0 THEN 1 WHEN ("frpm"."Free Meal Count (K-12)" / 1000) != 0.23 THEN 1 ELSE 0 END + CASE WHEN CASE WHEN "frpm"."FRPM Count (K-12)
```

## california_schools-u17 (attempt 56) -- mechanical class: BOTH KNOWN

Node: `(ROUND((("frpm"."Enrollment (K-12)" * 2) * 1.5), 2) / "frpm"."Enrollment (K-12)")`

- left operand: unit 'students', kind '', quantity ()
- right operand: unit 'students', kind 'count', quantity ('frpm.Enrollment (K-12)', 'value')
- stored columns under it: frpm.Enrollment (K-12) [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "frpm"."CDSCode" AS "o0", round((("frpm"."Enrollment (K-12)" * 2) * 1.5), 2) AS "o1", NTILE(10) OVER (ORDER BY (("frpm"."Enrollment (K-12)" * 2) * 1.5) ASC) AS "o2", CAST((("frpm"."Enrollment (K-12)" * 2) * 1.5) AS REAL) AS "o3", sqrt((((round((("frpm"."Enrollment (K-12)" * 2) * 1.5), 2) / "frpm"."Enrollment (K-12)") + ("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" + 0.39)) / 0.25)) AS "o4", coalesce((sqrt((((round((("frpm"."Enrollment (K-12)" * 2) * 1.5), 2) / "frpm"."Enrollment (K-12)") + ("frpm"."Percent (%) Eligible FRPM (Ages 5-17)" + 0.39)) / 0.25)) * (("frpm"."Percent (%) Eligible Free (Ages 5-17)" * 100) + 57.2)), 0) AS "o5", NTILE(10) OVER (ORDER BY "frpm"."Academic Year" DESC) AS "o6", CAST("frpm"."Academic Year" AS REAL) AS "o7", "frpm"."FRPM Count (K-12)" AS "o8", (CAST((1 - (1 - ("frpm"."Percent (%) Eligible Free (K-12)" * 0.75))) AS REAL) * (("frpm"."FRPM Count (K-1
```

## california_schools-u18 (attempt 124) -- mechanical class: BOTH KNOWN

Node: `((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)")`

- left operand: unit 'students per students', kind '', quantity ()
- right operand: unit 'students', kind 'count', quantity ('frpm.Enrollment (K-12)', 'value')
- stored columns under it: frpm.Enrollment (K-12) [unit 'students' (model), kind 'count', scale 'ratio']; frpm.FRPM Count (K-12) [unit 'students' (model), kind 'count', scale 'ratio']
- catalogue relations among them: frpm.FRPM Count (K-12) part_of frpm.Enrollment (K-12); frpm.Enrollment (K-12) comparable frpm.FRPM Count (K-12); frpm.FRPM Count (K-12) rate frpm.Enrollment (K-12)

Whole query:
```sql
SELECT "schools"."CDSCode" AS "o0", "schools"."School" AS "o1", "schools"."NCESSchool" AS "o2", round((("frpm"."Enrollment (Ages 5-17)" * 3) + ("frpm"."FRPM Count (K-12)" / ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)"))), 4) AS "o3", CASE WHEN (("frpm"."Enrollment (Ages 5-17)" * 3) + ("frpm"."FRPM Count (K-12)" / ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)"))) BETWEEN 1554.54 AND 1554.54 THEN 2 WHEN "schools"."FundingType" = 'Not in CS funding model' THEN 1 WHEN "schools"."FundingType" = 'Directly funded' THEN 1 WHEN ("schools"."NCESSchool" > '09509' AND ((CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12)") + "frpm"."Enrollment (K-12)") > 529.0) THEN ("frpm"."Enrollment (K-12)" * 0.1) WHEN (CAST("frpm"."FRPM Count (K-12)" AS REAL) / "frpm"."FRPM Count (K-12
```

## california_schools-u19 (attempt 9) -- mechanical class: NO UNIT

Node: `((1 - (1 - CASE WHEN CASE WHEN "s3"."o1" = '0756' THEN 10 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 1 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 0 ELSE 0 END = ((("s3"."o3" / "s3"."o3") * (((ROUND("s3"."o3", 2) * 0.5) * 0.25) + (CAST(("s3"."o3" / "s3"."o3") AS REAL) / 2))) + (("s3"."o3" / "s3`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s3" AS (SELECT "satscores"."cds" AS "o0", "schools"."CharterNum" AS "o1", "schools"."State" AS "o2", (CAST("satscores"."NumGE1500" AS REAL) * (1 - ("satscores"."enroll12" * 5))) AS "o3" FROM "satscores" AS "satscores" INNER JOIN "schools" AS "schools" ON "satscores"."cds" = "schools"."CDSCode" ORDER BY (CAST("satscores"."NumGE1500" AS REAL) * (1 - ("satscores"."enroll12" * 5))) DESC LIMIT 10) SELECT "s3"."o0" AS "o0", "s3"."o3" AS "o1", "s3"."o2" AS "o2", "s3"."o1" AS "o3", CASE WHEN NOT (CASE WHEN "s3"."o1" = '0756' THEN 10 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 1 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 0 ELSE 0 END IS NULL) THEN 2 WHEN ("s3"."o3" - "s3"."o3") = ((1 - (1 - CASE WHEN CASE WHEN "s3"."o1" = '0756' THEN 10 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 1 WHEN "s3"."o3" = ("s3"."o3" - "s3"."o3") THEN 0 ELSE 0 END = ((("s3"."o3" / "s3"."o3") * (((round("s3".
```

## california_schools-u20 (attempt 161) -- mechanical class: BOTH KNOWN

Node: `(CAST((CAST("s3"."o1" AS REAL) / "s3"."o1") AS REAL) / "s3"."o1")`

- left operand: unit 'fraction per fraction', kind '', quantity ()
- right operand: unit 'fraction', kind 'share', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s2" AS (SELECT "frpm"."School Name" AS "o0", AVG("frpm"."Percent (%) Eligible Free (K-12)") AS "o1", round(CAST(AVG(((CAST("frpm"."Percent (%) Eligible Free (K-12)" AS INTEGER) / "frpm"."Percent (%) Eligible Free (K-12)") - (1 - "frpm"."Percent (%) Eligible Free (Ages 5-17)"))) AS REAL), 2) AS "o2", round(CAST(AVG((1 - "frpm"."Percent (%) Eligible Free (Ages 5-17)")) AS REAL), 2) AS "o3", sqrt(AVG((1 - "frpm"."Percent (%) Eligible Free (Ages 5-17)"))) AS "o4", CURRENT_DATE AS "o5" FROM "frpm" AS "frpm" WHERE "frpm"."School Name" IN ('Fairview Elementary', 'Roosevelt Elementary') GROUP BY "frpm"."School Name"), "s3" AS (SELECT "s2"."o5" AS "o0", AVG("s2"."o3") AS "o1", coalesce(AVG("s2"."o1"), 0) AS "o2", AVG("s2"."o4") AS "o3", sqrt(round(CAST(AVG("s2"."o2") AS REAL), 2)) AS "o4", round(CAST(SUM("s2"."o3") AS REAL), 1) AS "o5" FROM "schools" AS "schools" INNER JOIN "frpm" AS "frpm"
```

