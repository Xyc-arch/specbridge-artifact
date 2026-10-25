# thrombosis_prediction: 20 random delivered programs

## thrombosis_prediction-1 (attempt 55)

```sql
WITH "s3" AS (SELECT "Laboratory"."ID" AS "o0", "Examination"."Symptoms" AS "o1", "Laboratory"."SSB" AS "o2", DENSE_RANK() OVER (ORDER BY "Laboratory"."ID" ASC) AS "o3", "Laboratory"."PLT" AS "o4" FROM "Patient" AS "Patient" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE ((((100 - "Laboratory"."HCT") * ("Laboratory"."UN" / "Laboratory"."CRE")) * 3) = 3714.0 AND "Laboratory"."SSB" > '0')), "s4" AS (SELECT "Laboratory"."ID" AS "o0", "Laboratory"."SC170" AS "o1" FROM "Laboratory" AS "Laboratory" WHERE ("Laboratory"."ALP" > 70 AND "Laboratory"."CENTROMEA" >= 'negative') ORDER BY "Laboratory"."SC170" DESC LIMIT 100) SELECT "s4"."o0" AS "o0" FROM "Patient" AS "Patient" INNER JOIN "s4" AS "s4" ON "s4"."o0" = "Patient"."ID" INNER JOIN "s3" AS "s3" ON "s3"."o0" = "Patient"."ID" ORDER BY "s4"."o0" DESC LIMIT 10
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` column/column: plausible (model)
- `-` parameter WHOLE: plausible (model)

## thrombosis_prediction-2 (attempt 123)

```sql
WITH "s12" AS (SELECT "Patient"."ID" AS "o0", "Laboratory"."PLT" AS "o1", "Laboratory"."FG" AS "o2", (((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) + ("Laboratory"."FG" + "Laboratory"."FG")) AS "o3", "Laboratory"."GOT" AS "o4", ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) AS "o5", CASE WHEN ("Laboratory"."FG" + "Laboratory"."FG") > 78.0 THEN 1 WHEN CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END < "Laboratory"."SM" THEN 4 WHEN ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) = "Laboratory"."U-PRO" THEN 0 ELSE 1 END AS "o6", FIRST_VALUE("Laboratory"."SM") OVER (ORDER BY ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) ASC) AS "o7", coalesce("Examination"."ID", 0) AS "o8", ((((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) + ("Laboratory"."FG" + "Laboratory"."FG")) * 2) AS "o9", CAST((CASE WHEN ("Laboratory"."FG" + "Laboratory"."FG") > 78.0 THEN 1 WHEN CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END < "Laboratory"."SM" THEN 4 WHEN ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) = "Laboratory"."U-PRO" THEN 0 ELSE 1 END * 0.75) AS REAL) AS "o10", ROW_NUMBER() OVER (ORDER BY "Patient"."First Date" ASC) AS "o11" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID") SELECT "s12"."o8" AS "o0", "s12"."o9" AS "o1", CASE WHEN "s12"."o9" < (("s12"."o9" * 3) - (("s12"."o9" / ((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2)) + (round(CAST(((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2) AS REAL), 2) * 2))) THEN 5 WHEN CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END > (round(CAST(((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2) AS REAL), 2) * 2) THEN 10 WHEN (("s12"."o9" * 3) - (("s12"."o9" / ((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2)) + (round(CAST(((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2) AS REAL), 2) * 2))) = (((round(CAST(((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2) AS REAL), 2) * 0.5) * (("s12"."o9" / ((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2)) / "s12"."o9")) * 0.2) THEN 2 WHEN ((round(CAST(((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2) AS REAL), 2) * 2) = ((round(CAST((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) AS REAL), 2) * 0.2) * 1.5) AND (round(CAST(((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2) AS REAL), 2) * 2) > ((round(CAST(("s12"."o9" - ("s12"."o9" * 3)) AS REAL), 2) * 0.1) / 3)) THEN 4 ELSE 1 END AS "o2", "s12"."o5" AS "o3", "s12"."o3" AS "o4" FROM "s12" AS "s12" ORDER BY "s12"."o5" DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: strong (rule)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` column/column: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/step output: unknown
- `/` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `+` derived/derived: unknown

## thrombosis_prediction-3 (attempt 116)

```sql
SELECT "Laboratory"."ID" AS "o0", round(((("Laboratory"."ALB" / 3.7) / 2) / 2), 2) AS "o1", DENSE_RANK() OVER (PARTITION BY round(((("Laboratory"."ALB" / 3.7) / 2) / 2), 2) ORDER BY "Laboratory"."ID" ASC) AS "o2", ((("Laboratory"."ALB" / 3.7) / 2) / 2) AS "o3", ("Laboratory"."ALB" - DENSE_RANK() OVER (PARTITION BY round(((("Laboratory"."ALB" / 3.7) / 2) / 2), 2) ORDER BY "Laboratory"."ID" ASC)) AS "o4", 1 AS "o5" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" ORDER BY (("Laboratory"."ALB" / 3.7) / 2) DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` column/window: unknown
- `/` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-4 (attempt 27)

```sql
SELECT "Laboratory"."ID" AS "o0", "Patient"."Admission" AS "o1", "Examination"."ANA" AS "o2" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" WHERE (NOT (round(CAST("Laboratory"."IGA" AS REAL), 2) IS NULL) AND ("Laboratory"."HGB" / ("Examination"."aCL IgG" * 0.75)) > 20.83 AND "Laboratory"."DNA" IN ('28.4', '23.4') AND "Laboratory"."IGA" < 252) ORDER BY "Patient"."Admission" DESC
```

- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-5 (attempt 81)

```sql
SELECT "Examination"."ID" AS "o0", "Examination"."Symptoms" AS "o1", "Examination"."aCL IgM" AS "o2", CASE WHEN CAST("Examination"."Symptoms" AS INTEGER) = 'retina artery occlusion' THEN 1 WHEN "Examination"."ID" = 5749920 THEN 1 ELSE 0 END AS "o3", CAST("Examination"."aCL IgM" AS REAL) AS "o4", NTILE(10) OVER (ORDER BY "Examination"."Symptoms" DESC) AS "o5", CASE WHEN "Examination"."ANA" = 4096 THEN 5 ELSE 1 END AS "o6", "Examination"."aCL IgA" AS "o7" FROM "Patient" AS "Patient" LEFT JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE (("Examination"."Symptoms" > 'CNS lupus (headache)' OR "Examination"."Symptoms" > 'abortion, epilepsy' OR "Examination"."Symptoms" = 'renal artery thrombosis') AND "Examination"."aCL IgM" > 1.4) ORDER BY CASE WHEN CAST("Examination"."Symptoms" AS INTEGER) = 'retina artery occlusion' THEN 1 WHEN "Examination"."ID" = 5749920 THEN 1 ELSE 0 END DESC
```


## thrombosis_prediction-6 (attempt 128)

```sql
SELECT "Laboratory"."ID" AS "o0", ("Laboratory"."UN" / round((((CASE WHEN "Laboratory"."CRP" = '1.5' THEN 0 WHEN ("Laboratory"."ID" < 4843434 AND "Laboratory"."CRP" > '0.5') THEN 4 WHEN "Examination"."ANA Pattern" > 'S,N' THEN 3 WHEN "Laboratory"."ID" = 1066089 THEN 10 ELSE 0 END * 5) * 0.1) + ("Laboratory"."HCT" / 100)), 2)) AS "o1", "Examination"."Thrombosis" AS "o2" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID"
```

- `/` column/derived: unknown
- `+` derived/derived: unknown
- `/` parameter CONVERT: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-7 (attempt 100)

```sql
WITH "s10" AS (SELECT "Laboratory"."SSA" AS "o0", round(COUNT(*), 2) AS "o1", (((CASE WHEN COUNT(*) = 1390 THEN 1 ELSE 10 END * 1.5) * (1 - (CASE WHEN (CASE WHEN COUNT(*) = 1390 THEN 1 ELSE 10 END < (CASE WHEN COUNT(*) = 1390 THEN 1 ELSE 10 END * 1.5) OR COUNT(*) >= 1390) THEN 10 ELSE 0 END * 0.5))) * ((((CASE WHEN COUNT(*) = 1390 THEN 1 ELSE 10 END * 1.5) * (1 - (CASE WHEN (CASE WHEN COUNT(*) = 1390 THEN 1 ELSE 10 END < (CASE WHEN COUNT(*) = 1390 THEN 1 ELSE 10 END * 1.5) OR COUNT(*) >= 1390) THEN 10 ELSE 0 END * 0.5))) / 5) / 3)) AS "o2" FROM "Laboratory" AS "Laboratory" WHERE "Laboratory"."SSA" < "Laboratory"."U-PRO" GROUP BY "Laboratory"."SSA") SELECT "s10"."o1" AS "o0", "Examination"."KCT" AS "o1", "Patient"."Birthday" AS "o2", "s10"."o0" AS "o3", "Examination"."aCL IgG" AS "o4" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "s10" AS "s10" ON "s10"."o0" = "Laboratory"."SSA" WHERE ("s10"."o2" = "Examination"."KCT" AND "Examination"."LAC" IN ('+', '-') AND "s10"."o2" < "Patient"."Birthday" AND "s10"."o0" > '4') ORDER BY "s10"."o0" ASC
```

- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-8 (attempt 132)

```sql
WITH "s1" AS (SELECT "Examination"."ID" AS "o0", "Examination"."KCT" AS "o1" FROM "Examination" AS "Examination" WHERE (NOT ("Examination"."aCL IgG" IS NULL) AND "Examination"."ANA" = 4) ORDER BY "Examination"."ID" ASC LIMIT 10), "s9" AS (SELECT CURRENT_DATE AS "o0", "s1"."o1" AS "o1", CASE WHEN ("s1"."o1" = '-' AND "s1"."o1" > '+') THEN 1 WHEN CURRENT_DATE BETWEEN "s1"."o1" AND PERCENT_RANK() OVER (ORDER BY "s1"."o1" ASC) THEN 1 WHEN "Laboratory"."SC170" = '0' THEN 2 WHEN "s1"."o1" > '+' THEN 1 ELSE 1 END AS "o2", (("Examination"."aCL IgM" * 0.5) * 2) AS "o3" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" LEFT JOIN "s1" AS "s1" ON "s1"."o0" = "Patient"."ID" WHERE "s1"."o1" = '-') SELECT "s9"."o0" AS "o0", "s9"."o1" AS "o1", ((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) AS "o2", (CAST(coalesce(CAST(max(1, (((CAST(round(CAST(("s9"."o3" * 0.25) AS REAL), 2) AS REAL) / (((1 - ("s9"."o2" / "s9"."o2")) + 0) * ((log(10, 10) + ("s9"."o3" * 0.1)) + 0))) + ((((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / 0.25) * 2)) * 0.2)) AS REAL), 0) AS REAL) * 0.25) AS "o3", ROW_NUMBER() OVER (ORDER BY ((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) DESC) AS "o4", CASE WHEN ((log(10, 10) + ("s9"."o3" * 0.1)) + 0) > (((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / ((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0)) THEN 2 ELSE 0 END AS "o5", CASE WHEN (((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / ((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0)) < ((round(((CAST(round(CAST(("s9"."o3" * 0.25) AS REAL), 2) AS REAL) / (((1 - ("s9"."o2" / "s9"."o2")) + 0) * ((log(10, 10) + ("s9"."o3" * 0.1)) + 0))) + ((((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / 0.25) * 2)), 1) * 2) * 1.5) THEN 3 ELSE 0 END AS "o6" FROM "s9" AS "s9" WHERE ((((((("s9"."o2" * (1 - ("s9"."o3" / (coalesce(((3 / "s9"."o3") / ("s9"."o3" / "s9"."o3")), 0) / 5)))) * 0.5) * 5) * 2) / 10) + ((abs((round((((CASE WHEN (3 / "s9"."o3") = ("s9"."o3" * 0.25) THEN 5 WHEN ("s9"."o3" * 0.25) = "s9"."o3" THEN 1 ELSE 0 END / 0.1) + 0) - ((round((("s9"."o3" + 0) / 3), 2) + ((("s9"."o2" - "s9"."o3") + 0) * 10)) * (round(CAST(("s9"."o3" * 0.25) AS REAL), 2) + ((("s9"."o3" * 0.25) / 0.25) * 1.5)))), 0) / 0.2)) * 0.5) * 2)) > (CAST(coalesce(CAST(max(1, (((CAST(round(CAST(("s9"."o3" * 0.25) AS REAL), 2) AS REAL) / (((1 - ("s9"."o2" / "s9"."o2")) + 0) * ((log(10, 10) + ("s9"."o3" * 0.1)) + 0))) + ((((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / 0.25) * 2)) * 0.2)) AS REAL), 0) AS REAL) * 0.25) AND log(10, 10) = 10) ORDER BY CASE WHEN (((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / ((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0)) < ((round(((CAST(round(CAST(("s9"."o3" * 0.25) AS REAL), 2) AS REAL) / (((1 - ("s9"."o2" / "s9"."o2")) + 0) * ((log(10, 10) + ("s9"."o3" * 0.1)) + 0))) + ((((CAST("s9"."o2" AS REAL) / ("s9"."o2" / "s9"."o2")) + 0) / 0.25) * 2)), 1) * 2) * 1.5) THEN 3 ELSE 0 END DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `+` derived/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `+` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `-` step output/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/step output: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `/` step output/step output: unknown (equal operands)

## thrombosis_prediction-9 (attempt 122)

```sql
SELECT "Patient"."Diagnosis" AS "o0", COUNT(*) AS "o1", "Patient"."Admission" AS "o2", CASE WHEN COUNT(*) < 123 THEN (((COUNT(*) + 123.0) * (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10)) / 10) WHEN ((COUNT(*) + 123.0) * (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10)) > (((((COUNT(*) + 123.0) * (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10)) / 10) * 0.25) * 0.75) THEN 1 WHEN (((COUNT(*) + 123.0) * (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10)) > ((((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * ((COUNT(*) + 123.0) * (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10))) * 2) AND ((((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * ((COUNT(*) + 123.0) * (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10))) * 2) > (((((CAST(COUNT(*) AS REAL) * 1.5) * (CAST(COUNT(*) AS INTEGER) * 3)) + 0) * 3) * 10) AND ((1 - ((CAST(COUNT(*) AS REAL) * 1.5) / 1.5)) * (10 / ((((1 - ((CAST(COUNT(*) AS REAL) * 1.5) / 1.5)) - CASE WHEN ((CAST(2 AS REAL) * 0.2) + CASE WHEN "Patient"."Diagnosis" > 'PM' THEN 10 WHEN "Patient"."Diagnosis" > 'MRA' THEN 5 ELSE 0 END) < ((1 - COUNT(*)) * round(CAST(10 AS REAL), 2)) THEN 5 ELSE 0 END) * 10) + 0))) != ((1 - COUNT(*)) * round(CAST(10 AS REAL), 2))) THEN 1 ELSE 0 END AS "o3" FROM "Patient" AS "Patient" GROUP BY "Patient"."Admission", "Patient"."Diagnosis"
```

- `*` constant-derived: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` case/derived: unknown
- `+` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-10 (attempt 14)

```sql
WITH "s1" AS (SELECT "Patient"."Diagnosis" AS "o0", "Laboratory"."ALP" AS "o1", "Laboratory"."UN" AS "o2" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE "Laboratory"."UN" >= 11 ORDER BY "Patient"."Diagnosis" DESC LIMIT 10), "s12" AS (SELECT "s1"."o2" AS "o0", power(round(CAST("s1"."o1" AS REAL), 2), 2) AS "o1", (((power(round(CAST("s1"."o1" AS REAL), 2), 2) / power(round(CAST("s1"."o1" AS REAL), 2), 2)) * ((power(round("s1"."o1", 2), 1.5) + (round((1 - CASE WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) > 101 OR power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101) THEN 3 WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101 AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = power(round(CAST("s1"."o1" AS REAL), 2), 2) AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = ((("s1"."o1" * 0.75) * ("s1"."o2" / 14.0)) / 1.5) AND ((("s1"."o1" * 0.75) * ("s1"."o2" / 14.0)) / 1.5) > 50.5) THEN 10 ELSE 4 END), 2) * 3)) + 0)) * 0.75) AS "o2", (power(round("s1"."o1", 2), 1.5) + (round((1 - CASE WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) > 101 OR power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101) THEN 3 WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101 AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = power(round(CAST("s1"."o1" AS REAL), 2), 2) AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = ((("s1"."o1" * 0.75) * ("s1"."o2" / 14.0)) / 1.5) AND ((("s1"."o1" * 0.75) * ("s1"."o2" / 14.0)) / 1.5) > 50.5) THEN 10 ELSE 4 END), 2) * 3)) AS "o3", NTILE(4) OVER (ORDER BY (power(round("s1"."o1", 2), 1.5) + (round((1 - CASE WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) > 101 OR power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101) THEN 3 WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101 AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = power(round(CAST("s1"."o1" AS REAL), 2), 2) AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = ((("s1"."o1" * 0.75) * ("s1"."o2" / 14.0)) / 1.5) AND ((("s1"."o1" * 0.75) * ("s1"."o2" / 14.0)) / 1.5) > 50.5) THEN 10 ELSE 4 END), 2) * 3)) DESC) AS "o4" FROM "s1" AS "s1" WHERE ("s1"."o1" = 108 AND "s1"."o0" > 'PSS, SJS')) SELECT "s12"."o0" AS "o0", AVG("s12"."o1") AS "o1", COUNT(*) AS "o2", AVG("s12"."o3") AS "o3", round(CAST(COUNT(*) AS INTEGER), 0) AS "o4", round(CAST(SUM("s12"."o1") AS REAL), 2) AS "o5", round(CAST(AVG("s12"."o4") AS REAL), 2) AS "o6" FROM "s12" AS "s12" WHERE "s12"."o0" > 11 GROUP BY "s12"."o0" ORDER BY COUNT(*) DESC
```

- `+` derived/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` function/function: unknown (equal operands)

## thrombosis_prediction-11 (attempt 1)

```sql
SELECT "Examination"."ID" AS "o0", "Examination"."Symptoms" AS "o1", "Examination"."Examination Date" AS "o2", CAST(((((("Examination"."aCL IgG" / 0.8) * "Examination"."aCL IgA") / 0.75) + (1 - ("Examination"."ANA" / 16))) * (("Examination"."Thrombosis" / "Examination"."aCL IgM") * 1.5)) AS REAL) AS "o3" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE (((((("Examination"."aCL IgG" / 0.8) * "Examination"."aCL IgA") / 0.75) + (1 - ("Examination"."ANA" / 16))) * (("Examination"."Thrombosis" / "Examination"."aCL IgM") * 1.5)) > 0.0 AND (("Examination"."Thrombosis" / "Examination"."aCL IgM") * 1.5) < "Examination"."Examination Date") ORDER BY ((((("Examination"."aCL IgG" / 0.8) * "Examination"."aCL IgA") / 0.75) + (1 - ("Examination"."ANA" / 16))) * (("Examination"."Thrombosis" / "Examination"."aCL IgM") * 1.5)) DESC
```

- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)

## thrombosis_prediction-12 (attempt 185)

```sql
SELECT "Laboratory"."ID" AS "o0", "Laboratory"."CPK" AS "o1", CASE WHEN ("Laboratory"."CPK" > 36 OR "Laboratory"."RBC" != 2.5 OR "Laboratory"."SSA" > '16') THEN 1 ELSE 0 END AS "o2" FROM "Laboratory" AS "Laboratory" WHERE CAST("Laboratory"."RBC" AS REAL) < 4.3
```


## thrombosis_prediction-13 (attempt 59)

```sql
SELECT "Laboratory"."ID" AS "o0", CAST("Patient"."ID" AS REAL) AS "o1", "Laboratory"."HGB" AS "o2" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" ORDER BY "Laboratory"."ID" DESC
```


## thrombosis_prediction-14 (attempt 118)

```sql
SELECT "Examination"."ID" AS "o0", "Patient"."ID" AS "o1", "Examination"."aCL IgG" AS "o2", 1 AS "o3", round(CAST("Examination"."aCL IgM" AS REAL), 2) AS "o4", "Examination"."ANA" AS "o5" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" ORDER BY round(CAST("Examination"."aCL IgM" AS REAL), 2) ASC
```


## thrombosis_prediction-15 (attempt 51)

```sql
SELECT "Patient"."First Date" AS "o0", "Patient"."ID" AS "o1", CAST("Examination"."ID" AS REAL) AS "o2" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" ORDER BY "Patient"."ID" ASC
```


## thrombosis_prediction-16 (attempt 44)

```sql
SELECT "Examination"."ID" AS "o0", round(("Examination"."Thrombosis" * 0.25), 2) AS "o1", ("Examination"."Thrombosis" * 0.25) AS "o2" FROM "Examination" AS "Examination" WHERE (NOT ("Examination"."Thrombosis" IS NULL) AND NOT ("Examination"."KCT" IS NULL)) ORDER BY round(("Examination"."Thrombosis" * 0.25), 2) DESC, CAST("Examination"."Thrombosis" AS REAL) DESC
```

- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-17 (attempt 157)

```sql
SELECT "Patient"."ID" AS "o0", "Patient"."Admission" AS "o1", "Patient"."SEX" AS "o2" FROM "Patient" AS "Patient" ORDER BY "Patient"."ID" DESC LIMIT 100
```


## thrombosis_prediction-18 (attempt 86)

```sql
SELECT "Patient"."ID" AS "o0", "Laboratory"."SM" AS "o1", (((100 - "Laboratory"."HCT") * (round(CAST("Laboratory"."TP" AS REAL), 2) * 10)) / ((("Laboratory"."ALP" * 0.25) * (("Laboratory"."T-BIL" + "Laboratory"."CRE") / 0.25)) - ("Laboratory"."C3" / "Laboratory"."C4"))) AS "o2", CAST(((((100 - "Laboratory"."HCT") * (round(CAST("Laboratory"."TP" AS REAL), 2) * 10)) / ((("Laboratory"."ALP" * 0.25) * (("Laboratory"."T-BIL" + "Laboratory"."CRE") / 0.25)) - ("Laboratory"."C3" / "Laboratory"."C4"))) * 0.25) AS REAL) AS "o3", "Patient"."Diagnosis" AS "o4", "Laboratory"."C4" AS "o5", CASE WHEN (((100 - "Laboratory"."HCT") * (round(CAST("Laboratory"."TP" AS REAL), 2) * 10)) / ((("Laboratory"."ALP" * 0.25) * (("Laboratory"."T-BIL" + "Laboratory"."CRE") / 0.25)) - ("Laboratory"."C3" / "Laboratory"."C4"))) < 37.27 THEN 0 WHEN "Laboratory"."C3" < 55 THEN 3 WHEN (((((100 - "Laboratory"."HCT") * (round(CAST("Laboratory"."TP" AS REAL), 2) * 10)) / ((("Laboratory"."ALP" * 0.25) * (("Laboratory"."T-BIL" + "Laboratory"."CRE") / 0.25)) - ("Laboratory"."C3" / "Laboratory"."C4"))) * 0.25) = 9.32 OR "Laboratory"."C4" > 16) THEN 1 ELSE 1 END AS "o6" FROM "Patient" AS "Patient" LEFT JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE (((100 - "Laboratory"."HCT") * (round(CAST("Laboratory"."TP" AS REAL), 2) * 10)) / ((("Laboratory"."ALP" * 0.25) * (("Laboratory"."T-BIL" + "Laboratory"."CRE") / 0.25)) - ("Laboratory"."C3" / "Laboratory"."C4"))) < 37.27 ORDER BY CAST((((((CASE WHEN "Laboratory"."C4" < 21 THEN 1 ELSE 4 END / 5) * 10) * 0.75) * ((((CASE WHEN "Laboratory"."C4" < 21 THEN 1 ELSE 4 END / 5) * 10) * 0.75) / "Laboratory"."C4")) + (0.75 / CAST(((CASE WHEN "Laboratory"."C4" < 21 THEN 1 ELSE 4 END / 5) * 10) AS REAL))) AS INTEGER) DESC
```

- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `-` derived/derived: unknown
- `/` column/column: plausible (model)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` column/column: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: plausible (model)

## thrombosis_prediction-19 (attempt 133)

```sql
WITH "s10" AS (SELECT "Examination"."Examination Date" AS "o0", ((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) / (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) * (1 - (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) / ((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))))))) AS "o1" FROM "Examination" AS "Examination" ORDER BY ((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) / (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) * (1 - (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) / ((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))))))) DESC LIMIT 50) SELECT "s10"."o1" AS "o0", "s10"."o0" AS "o1", round(CAST(("s10"."o1" / sqrt(round(CAST(((("s10"."o1" / "s10"."o1") * (1 - CASE WHEN ("s10"."o1" / "s10"."o1") >= (("s10"."o1" / "s10"."o1") / "s10"."o1") THEN 10 ELSE 0 END)) / ((round(CAST((("s10"."o1" / "s10"."o1") / "s10"."o1") AS REAL), 2) * 10) + 0)) AS REAL), 2))) AS REAL), 2) AS "o2", RANK() OVER (PARTITION BY ("s10"."o1" / sqrt(round(CAST(((("s10"."o1" / "s10"."o1") * (1 - CASE WHEN ("s10"."o1" / "s10"."o1") >= (("s10"."o1" / "s10"."o1") / "s10"."o1") THEN 10 ELSE 0 END)) / ((round(CAST((("s10"."o1" / "s10"."o1") / "s10"."o1") AS REAL), 2) * 10) + 0)) AS REAL), 2))) ORDER BY "s10"."o0" DESC) AS "o3", (1 - CASE WHEN ("s10"."o1" / "s10"."o1") >= (("s10"."o1" / "s10"."o1") / "s10"."o1") THEN 10 ELSE 0 END) AS "o4", round(CAST((("s10"."o1" / "s10"."o1") / "s10"."o1") AS REAL), 2) AS "o5" FROM "s10" AS "s10" ORDER BY round(CAST(("s10"."o1" / sqrt(round(CAST(((("s10"."o1" / "s10"."o1") * (1 - CASE WHEN ("s10"."o1" / "s10"."o1") >= (("s10"."o1" / "s10"."o1") / "s10"."o1") THEN 10 ELSE 0 END)) / ((round(CAST((("s10"."o1" / "s10"."o1") / "s10"."o1") AS REAL), 2) * 10) + 0)) AS REAL), 2))) AS REAL), 2) DESC
```

- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `+` derived/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` function/step output: unknown
- `/` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `*` constant-derived: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)

## thrombosis_prediction-20 (attempt 188)

```sql
SELECT "Laboratory"."ID" AS "o0", "Patient"."SEX" AS "o1", CAST("Laboratory"."PLT" AS REAL) AS "o2" FROM "Patient" AS "Patient" LEFT JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" ORDER BY "Laboratory"."ID" DESC
```


