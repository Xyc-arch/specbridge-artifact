# thrombosis_prediction: 20 random delivered programs

## thrombosis_prediction-1 (attempt 86)

```sql
WITH "s4" AS (SELECT "Laboratory"."CENTROMEA" AS "o0", "Laboratory"."IGA" AS "o1", round((CAST((("Laboratory"."C3" / 42) / 2) AS REAL) * (("Laboratory"."C3" / 42) * 3)), 2) AS "o2", "Laboratory"."PLT" AS "o3" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE ("Laboratory"."UA" = 2.8 AND CAST("Laboratory"."UA" AS REAL) = 4.4) ORDER BY round((CAST((("Laboratory"."C3" / 42) / 2) AS REAL) * (("Laboratory"."C3" / 42) * 3)), 2) ASC LIMIT 10), "s11" AS (SELECT "s4"."o3" AS "o0", abs(((((0.75 / (((CASE WHEN "s4"."o3" = 241 THEN 10 WHEN "s4"."o3" > 248 THEN 2 END / 0.75) + 0) * ((CASE WHEN "s4"."o3" = 241 THEN 10 WHEN "s4"."o3" > 248 THEN 2 END / 0.75) + 0))) * 5) * CAST("s4"."o3" AS INTEGER)) * coalesce(CAST("s4"."o3" AS REAL), 0))) AS "o1" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" LEFT JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" INNER JOIN "s4" AS "s4" ON "s4"."o0" = "Laboratory"."CENTROMEA" GROUP BY "s4"."o3") SELECT "s4"."o0" AS "o0", "s11"."o0" AS "o1", (CAST(round(CAST((("s4"."o3" / 248.0) * 2) AS INTEGER), 2) AS REAL) / ("s11"."o0" * 3)) AS "o2", "s4"."o2" AS "o3", ((1 - ((CAST("s4"."o1" AS REAL) / 343.0) + 1.0)) + (((round(CAST((1 - ((CAST("s4"."o1" AS REAL) / 343.0) + 1.0)) AS REAL), 2) * 0.75) + ((1 - CASE WHEN ("s4"."o2" = ((("s4"."o2" / "s4"."o2") * ((("s11"."o0" + 248.0) * 2) * (("s11"."o0" + "s11"."o0") * 3))) * 0.25) AND ((("s4"."o2" / "s4"."o2") * ((("s11"."o0" + 248.0) * 2) * (("s11"."o0" + "s11"."o0") * 3))) * 0.25) > ((10 / (coalesce(("s11"."o0" * 5), 0) * 0.5)) * 2) AND "s4"."o0" > 'negative') THEN 10 WHEN ((10 / (coalesce(("s11"."o0" * 5), 0) * 0.5)) * 2) > 0.03 THEN 4 WHEN (((10 / (coalesce(("s11"."o0" * 5), 0) * 0.5)) * 2) = 0.03 AND ((10 / (coalesce(("s11"."o0" * 5), 0) * 0.5)) * 2) > 0.03) THEN 10 WHEN coalesce(("s11"."o0" * 5), 0) < 1240 THEN 5 WHEN ((("s4"."o2" / "s4"."o2") * ((("s11"."o0" + 248.0) * 2) * (("s11"."o0" + "s11"."o0") * 3))) > ((("s11"."o0" + 248.0) * 2) * (("s11"."o0" + "s11"."o0") * 3)) AND ("s11"."o0" * 5) < 1240) THEN 2 ELSE 0 END) * 3)) + (((CAST(round(CAST((("s4"."o3" / 248.0) * 2) AS INTEGER), 2) AS REAL) / ("s11"."o0" * 3)) - (CAST(round(CAST((("s4"."o3" / 248.0) * 2) AS INTEGER), 2) AS REAL) / ("s11"."o0" * 3))) * sqrt(((coalesce((CAST((10 / (coalesce(("s11"."o0" * 5), 0) * 0.5)) AS REAL) * 0.1), 0) * 0.25) + (((1 - (1 - ((("s4"."o3" / 248.0) / 2) * (0.75 / (("s4"."o3" / 248.0) / 2))))) + ((("s4"."o2" / (1 - ("s11"."o0" / 248.0))) * 0.75) * 5)) + (CAST(((("s4"."o2" / (1 - ("s11"."o0" / 248.0))) * 0.75) * 5) AS INTEGER) * 3))))))) AS "o4" FROM "s4" AS "s4" INNER JOIN "s11" AS "s11" ON "s11"."o0" = "s4"."o3" WHERE ("s11"."o1" > (((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / ((((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2)) / 0.25) * 10)) + (CAST(((((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2)) / 0.25) * 10) AS REAL) / 1.5)) - ((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2))) AND ((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / ((((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2)) / 0.25) * 10)) + (CAST(((((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2)) / 0.25) * 10) AS REAL) / 1.5)) > (CAST(round(CAST((("s4"."o3" / 248.0) * 2) AS INTEGER), 2) AS REAL) / ("s11"."o0" * 3)) AND NOT (("s11"."o0" * 3) IS NULL) AND (CAST(round(CAST((("s4"."o3" / 248.0) * 2) AS INTEGER), 2) AS REAL) / ("s11"."o0" * 3)) < (((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / ((((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2)) / 0.25) * 10)) + (CAST(((((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2)) / 0.25) * 10) AS REAL) / 1.5)) - ((((max(CAST("s11"."o1" AS INTEGER), CAST("s11"."o1" AS REAL)) / (CAST("s11"."o1" AS REAL) / CAST("s11"."o1" AS REAL))) * 0.5) * 5) * (("s4"."o3" / 248.0) * 2))))
```

- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/step output: unknown
- `*` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` constant-derived: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/step output: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` step output/step output: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/function: unknown

## thrombosis_prediction-2 (attempt 48)

```sql
SELECT "Examination"."ID" AS "o0", "Examination"."RVVT" AS "o1", "Patient"."Diagnosis" AS "o2", 1 AS "o3", (((1 - ("Examination"."aCL IgG" / 0.8)) + 0) - ((1 - ("Examination"."ANA" / 16)) * (("Examination"."aCL IgG" / 0.8) / (1 - ("Examination"."ANA" / 16))))) AS "o4" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID"
```

- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## thrombosis_prediction-3 (attempt 137)

```sql
WITH "s1" AS (SELECT "Patient"."ID" AS "o0", ("Examination"."aCL IgM" - "Examination"."Thrombosis") AS "o1", "Examination"."ID" AS "o2", round("Examination"."Thrombosis", 2) AS "o3" FROM "Examination" AS "Examination" LEFT JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE ("Examination"."ANA" != 1024 AND ("Examination"."aCL IgM" - "Examination"."Thrombosis") < 2.1) ORDER BY ("Examination"."aCL IgM" - "Examination"."Thrombosis") DESC LIMIT 100), "s2" AS (SELECT "Examination"."ID" AS "o0" FROM "Examination" AS "Examination" LEFT JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" ORDER BY "Examination"."ID" DESC LIMIT 5) SELECT "s2"."o0" AS "o0", "s1"."o3" AS "o1", "s1"."o0" AS "o2" FROM "s2" AS "s2" LEFT JOIN "Patient" AS "Patient" ON "s2"."o0" = "Patient"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" INNER JOIN "s1" AS "s1" ON "s1"."o0" = "Patient"."ID" ORDER BY "s1"."o3" DESC LIMIT 100
```

- `-` column/column: unknown

## thrombosis_prediction-4 (attempt 175)

```sql
SELECT "Examination"."ID" AS "o0", "Patient"."ID" AS "o1", "Examination"."aCL IgG" AS "o2" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE ("Examination"."Thrombosis" = 2 OR CAST("Examination"."aCL IgG" AS REAL) > 1.5) ORDER BY "Patient"."ID" ASC
```


## thrombosis_prediction-5 (attempt 25)

```sql
SELECT "Patient"."ID" AS "o0", abs(((((1 - CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END) + "Laboratory"."TAT2") + 0) * (("Laboratory"."UN" / 10) * ("Laboratory"."LDH" * 10)))) AS "o1", CAST("Laboratory"."Date" AS INTEGER) AS "o2", CASE WHEN CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END = (("Laboratory"."LDH" * 10) * 0.2) THEN 1 WHEN CAST("Laboratory"."C4" AS REAL) = 24 THEN (((100 - "Laboratory"."HCT") * (CAST("Laboratory"."GOT" AS REAL) / abs(((((1 - CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END) + "Laboratory"."TAT2") + 0) * (("Laboratory"."UN" / 10) * ("Laboratory"."LDH" * 10)))))) * (1 - (abs(((((1 - CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END) + "Laboratory"."TAT2") + 0) * (("Laboratory"."UN" / 10) * ("Laboratory"."LDH" * 10)))) / (100 - "Laboratory"."HCT")))) ELSE 0 END AS "o3", "Laboratory"."DNA" AS "o4", "Laboratory"."UA" AS "o5" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" WHERE ("Laboratory"."RA" < '+' AND "Laboratory"."TAT" > (CAST("Laboratory"."C3" AS REAL) * 0.75)) ORDER BY CASE WHEN CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END = (("Laboratory"."LDH" * 10) * 0.2) THEN 1 WHEN CAST("Laboratory"."C4" AS REAL) = 24 THEN (((100 - "Laboratory"."HCT") * (CAST("Laboratory"."GOT" AS REAL) / abs(((((1 - CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END) + "Laboratory"."TAT2") + 0) * (("Laboratory"."UN" / 10) * ("Laboratory"."LDH" * 10)))))) * (1 - (abs(((((1 - CASE WHEN "Laboratory"."C3" < 69 THEN 10 WHEN (CAST("Laboratory"."C3" AS REAL) * 0.75) = 51.75 THEN 1 WHEN "Laboratory"."C3" = 75 THEN 1 WHEN "Laboratory"."TAT" BETWEEN 118 AND 101 THEN 10 ELSE 0 END) + "Laboratory"."TAT2") + 0) * (("Laboratory"."UN" / 10) * ("Laboratory"."LDH" * 10)))) / (100 - "Laboratory"."HCT")))) ELSE 0 END DESC LIMIT 100
```

- `*` derived/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `/` derived/derived: unknown
- `-` parameter WHOLE: plausible (model)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` column/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-6 (attempt 3)

```sql
WITH "s8" AS (SELECT "Patient"."ID" AS "o0" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE (((((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + (((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + "Examination"."aCL IgG")) * "Examination"."aCL IgA") > 0.0 AND ("Examination"."aCL IgG" = 0.0 OR (("Examination"."aCL IgM" + 2.1) + (((("Examination"."Thrombosis" * 0.75) / 0.2) + 0) / 0.25)) = 4.2 OR "Examination"."RVVT" = '+')) GROUP BY "Patient"."ID") SELECT round(SUM(((((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))) * CAST(((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) AS REAL)) / (round(CAST((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5) AS REAL), 2) * 0.25))), 2) AS "o0", ((((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))) * CAST(((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) AS REAL)) / (round(CAST((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5) AS REAL), 2) * 0.25)) AS "o1", AVG(CASE WHEN ((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))) < (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)) THEN ((((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)) - (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))) ELSE 0 END) FILTER (WHERE ((((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))) * CAST(((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) AS REAL)) / (round(CAST((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5) AS REAL), 2) * 0.25)) >= ((((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))) * CAST(((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) AS REAL)) - ((((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)) - (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)))))) AS "o2", coalesce(AVG((10 / (round((((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25)) + ((CAST(abs(2) AS INTEGER) * 0.5) / 0.5)), 2) * 0.5))), 0) AS "o3", round(CAST(COUNT(*) AS REAL), 2) AS "o4", round(CAST(COUNT(*) AS REAL), 2) AS "o5" FROM "s8" AS "s8" WHERE "s8"."o0" < 2936723 ORDER BY round(CAST(COUNT(*) AS REAL), 2) DESC
```

- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` column/derived: unknown
- `+` derived/derived: unknown
- `+` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `-` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` constant-derived: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-7 (attempt 174)

```sql
SELECT "Laboratory"."RF" AS "o0", abs(((("Laboratory"."HGB" / 10.8) * ("Laboratory"."TAT" + 77)) * 0.75)) AS "o1" FROM "Laboratory" AS "Laboratory" ORDER BY abs(((("Laboratory"."HGB" / 10.8) * ("Laboratory"."TAT" + 77)) * 0.75)) DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)

## thrombosis_prediction-8 (attempt 95)

```sql
SELECT "Laboratory"."ID" AS "o0", (1 - ((("Laboratory"."T-CHO" * 10) * 5) * 0.75)) AS "o1", round(((("Laboratory"."T-CHO" * 10) * 5) * 0.75), 2) AS "o2", "Laboratory"."HCT" AS "o3", "Examination"."ANA Pattern" AS "o4", ((("Laboratory"."T-CHO" * 10) * 5) * 0.75) AS "o5", "Laboratory"."GLU" AS "o6", "Laboratory"."UA" AS "o7", CAST("Laboratory"."WBC" AS REAL) AS "o8" FROM "Patient" AS "Patient" LEFT JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" ORDER BY ((("Laboratory"."T-CHO" * 10) * 5) * 0.75) DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## thrombosis_prediction-9 (attempt 85)

```sql
WITH "s5" AS (SELECT "Patient"."ID" AS "o0", "Examination"."ANA" AS "o1", round((("Examination"."ANA" * 0.75) * ((("Laboratory"."WBC" * 0.1) + ("Laboratory"."ALB" / 3.7)) + 1.84)), 2) AS "o2" FROM "Patient" AS "Patient" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" LEFT JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" ORDER BY ((("Laboratory"."WBC" * 0.1) + ("Laboratory"."ALB" / 3.7)) + 1.84) ASC LIMIT 100), "s6" AS (SELECT "Patient"."ID" AS "o0", CAST("Examination"."ID" AS REAL) AS "o1" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" LEFT JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" ORDER BY "Patient"."ID" DESC LIMIT 100), "s7" AS (SELECT "Laboratory"."DNA" AS "o0", COUNT(*) AS "o1", coalesce(COUNT(*), 0) AS "o2" FROM "Patient" AS "Patient" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" GROUP BY "Laboratory"."DNA"), "s10" AS (SELECT "Laboratory"."RA" AS "o0", AVG((CAST((((0.75 / (round(CAST("Laboratory"."GOT" AS INTEGER), 2) / log(10, "Laboratory"."T-BIL"))) * 0.25) + (((0.75 / (round(CAST("Laboratory"."GOT" AS INTEGER), 2) / log(10, "Laboratory"."T-BIL"))) * 0.25) * coalesce(CAST("Laboratory"."C3" AS REAL), 0))) AS REAL) + power((((0.75 / (round(CAST("Laboratory"."GOT" AS INTEGER), 2) / log(10, "Laboratory"."T-BIL"))) * 0.25) * "Laboratory"."T-CHO"), 1.5))) AS "o1" FROM "Laboratory" AS "Laboratory" GROUP BY "Laboratory"."RA") SELECT "Examination"."ID" AS "o0", AVG("s5"."o2") AS "o1", coalesce(MAX("s5"."o0"), 0) AS "o2", COUNT(*) AS "o3", coalesce(AVG("s7"."o1"), 0) AS "o4" FROM "s6" AS "s6" INNER JOIN "s5" AS "s5" ON "s5"."o0" = "s6"."o0" INNER JOIN "Patient" AS "Patient" ON "s6"."o1" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "s7" AS "s7" ON "s7"."o0" = "Laboratory"."DNA" LEFT JOIN "s10" AS "s10" ON "s10"."o0" = "Laboratory"."RA" WHERE ("Laboratory"."APTT" > 95 AND "s10"."o1" = (CAST("Laboratory"."TAT2" AS REAL) * 10) AND "s10"."o1" = "Laboratory"."Date" AND ("Laboratory"."Date" = '1985-04-22' OR "s5"."o1" < 16)) GROUP BY "Examination"."ID" ORDER BY coalesce(AVG("s7"."o1"), 0) DESC
```

- `+` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown (disputed (model))
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/function: unknown
- `*` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` column/function: unknown
- `+` derived/derived: unknown
- `*` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-10 (attempt 70)

```sql
SELECT "Examination"."Examination Date" AS "o0", ((1 - (CAST("Laboratory"."T-BIL" AS REAL) - CAST("Patient"."First Date" AS REAL))) * 0.2) AS "o1", "Examination"."aCL IgG" AS "o2" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" ORDER BY ((1 - (CAST("Laboratory"."T-BIL" AS REAL) - CAST("Patient"."First Date" AS REAL))) * 0.2) ASC
```

- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` column/column: unknown

## thrombosis_prediction-11 (attempt 146)

```sql
SELECT "Examination"."ID" AS "o0", ((1 - "Examination"."ANA") * 0.2) AS "o1", "Examination"."aCL IgG" AS "o2", "Examination"."ANA" AS "o3", "Examination"."aCL IgA" AS "o4", "Examination"."RVVT" AS "o5", LAG("Examination"."RVVT") OVER (ORDER BY ((1 - "Examination"."ANA") * 0.2) DESC) AS "o6" FROM "Examination" AS "Examination"
```

- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## thrombosis_prediction-12 (attempt 54)

```sql
SELECT "Patient"."Admission" AS "o0" FROM "Patient" AS "Patient" WHERE "Patient"."SEX" > 'M'
```


## thrombosis_prediction-13 (attempt 193)

```sql
WITH "s20" AS (SELECT "Examination"."Thrombosis" AS "o0", COUNT(*) AS "o1", max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0) AS "o2", log(10, (((COUNT(*) * ((((CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0)) + 0) + ((CAST(COUNT(*) AS REAL) / (CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0))) / 10)) + ((((CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0)) + 0) + ((CAST(COUNT(*) AS REAL) / (CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0))) / 10)) - CASE WHEN "Examination"."Thrombosis" > 0 THEN 3 WHEN ((2 / (CASE WHEN "Examination"."Thrombosis" > 0 THEN 1 WHEN "Examination"."Thrombosis" = 2 THEN 3 ELSE 0 END * 1.5)) - (CASE WHEN "Examination"."Thrombosis" > 0 THEN 1 WHEN "Examination"."Thrombosis" = 2 THEN 3 ELSE 0 END / (1 - CAST(round("Examination"."Thrombosis", 2) AS REAL)))) = ((round("Examination"."Thrombosis", 2) * round(CAST("Examination"."Thrombosis" AS REAL), 2)) / (CASE WHEN "Examination"."Thrombosis" > 0 THEN 1 WHEN "Examination"."Thrombosis" = 2 THEN 3 ELSE 0 END * "Examination"."Thrombosis")) THEN 10 ELSE 1 END))) - coalesce(CAST("Examination"."Thrombosis" AS REAL), 0)) * (1 - (COUNT(*) * ((((CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0)) + 0) + ((CAST(COUNT(*) AS REAL) / (CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0))) / 10)) + ((((CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0)) + 0) + ((CAST(COUNT(*) AS REAL) / (CAST("Examination"."Thrombosis" AS INTEGER) / max(CAST(COUNT(*) AS REAL), CAST(COUNT(*) AS REAL), 0))) / 10)) - CASE WHEN "Examination"."Thrombosis" > 0 THEN 3 WHEN ((2 / (CASE WHEN "Examination"."Thrombosis" > 0 THEN 1 WHEN "Examination"."Thrombosis" = 2 THEN 3 ELSE 0 END * 1.5)) - (CASE WHEN "Examination"."Thrombosis" > 0 THEN 1 WHEN "Examination"."Thrombosis" = 2 THEN 3 ELSE 0 END / (1 - CAST(round("Examination"."Thrombosis", 2) AS REAL)))) = ((round("Examination"."Thrombosis", 2) * round(CAST("Examination"."Thrombosis" AS REAL), 2)) / (CASE WHEN "Examination"."Thrombosis" > 0 THEN 1 WHEN "Examination"."Thrombosis" = 2 THEN 3 ELSE 0 END * "Examination"."Thrombosis")) THEN 10 ELSE 1 END)))))) AS "o3", round(CAST(AVG(((((coalesce(CAST("Examination"."Thrombosis" AS REAL), 0) / (((CAST("Examination"."aCL IgM" AS REAL) * 5) + "Laboratory"."HCT") + 48.6)) + (((100 - "Laboratory"."HCT") * (((CAST("Examination"."aCL IgM" AS REAL) * 5) + "Laboratory"."HCT") + 48.6)) * 0.2)) + coalesce(CAST("Examination"."Thrombosis" AS INTEGER), 0)) / ((CAST("Examination"."aCL IgM" AS REAL) * 5) + "Laboratory"."HCT"))) FILTER (WHERE "Laboratory"."C4" = 41) AS REAL), 2) AS "o4", coalesce(AVG(CASE WHEN coalesce(CAST("Examination"."Thrombosis" AS INTEGER), 0) = 2 THEN 10 WHEN "Examination"."Thrombosis" = 1 THEN 1 WHEN ((coalesce(CAST("Examination"."Thrombosis" AS REAL), 0) / (((CAST("Examination"."aCL IgM" AS REAL) * 5) + "Laboratory"."HCT") + 48.6)) + (((100 - "Laboratory"."HCT") * (((CAST("Examination"."aCL IgM" AS REAL) * 5) + "Laboratory"."HCT") + 48.6)) * 0.2)) < 1203.34 THEN 10 END), 0) AS "o5" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE "Examination"."Thrombosis" > 0 GROUP BY "Examination"."Thrombosis"), "s21" AS (SELECT "s20"."o2" AS "o0", "s20"."o3" AS "o1", coalesce(("s20"."o3" / abs("s20"."o2")), 0) AS "o2", "s20"."o1" AS "o3" FROM "s20" AS "s20" ORDER BY ("s20"."o3" / abs("s20"."o2")) DESC LIMIT 100) SELECT "s21"."o1" AS "o0", "s21"."o3" AS "o1", "s21"."o0" AS "o2", "s21"."o2" AS "o3", CASE WHEN "s21"."o2" > ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 1 WHEN ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) = ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 5 ELSE 0 END AS "o4", AVG("s21"."o2") OVER (ORDER BY "s21"."o2" DESC) AS "o5", CASE WHEN (CASE WHEN "s21"."o2" > ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 1 WHEN ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) = ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 5 ELSE 0 END IN ("s21"."o3", "s21"."o3") OR CASE WHEN "s21"."o2" > ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 1 WHEN ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) = ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 5 ELSE 0 END = (CASE WHEN "s21"."o2" > ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 1 WHEN ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) = ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 5 ELSE 0 END - "s21"."o0")) THEN 1 WHEN "s21"."o3" > (CASE WHEN "s21"."o2" > ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 1 WHEN ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) = ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 5 ELSE 0 END - (CASE WHEN "s21"."o2" > ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 1 WHEN ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) = ((1 - ("s21"."o1" / "s21"."o0")) / 0.1) THEN 5 ELSE 0 END - "s21"."o0")) THEN 1 ELSE 0 END AS "o6" FROM "s21" AS "s21" WHERE "s21"."o2" = "s21"."o2" ORDER BY "s21"."o0" DESC
```

- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `+` column/derived: unknown (disputed (model))
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: plausible (model)
- `/` column/derived: unknown
- `/` derived/derived: unknown
- `+` column/derived: unknown
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/summary: unknown
- `+` derived/derived: unknown
- `-` case/derived: unknown
- `/` derived/derived: unknown
- `*` case/column: unknown
- `*` column/column: unknown
- `-` derived/derived: unknown
- `/` case/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/summary: unknown
- `/` column/function: unknown
- `+` parameter ZERO: unknown (a constant)
- `-` column/derived: unknown
- `/` step output/step output: unknown
- `-` case/derived: unknown
- `-` case/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` step output/step output: unknown

## thrombosis_prediction-14 (attempt 144)

```sql
WITH "s7" AS (SELECT "Laboratory"."ID" AS "o0", max(CAST(AVG(("Laboratory"."HCT" / ("Laboratory"."HCT" / (("Laboratory"."GPT" * (((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25) * ((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25))) * 0.1)))) AS REAL), CAST(AVG("Laboratory"."GOT") AS INTEGER)) AS "o1", AVG((((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25) * "Laboratory"."GOT")) AS "o2", ((1 - (AVG("Laboratory"."GOT") * coalesce(CAST(AVG(CASE WHEN "Laboratory"."C3" > 69 THEN (((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25) * ((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25)) WHEN ("Laboratory"."UA" = 3.7 AND "Laboratory"."UA" = 4.4) THEN 2 ELSE 1 END) AS REAL), 0))) - ((1 - (AVG("Laboratory"."GOT") * coalesce(CAST(AVG(CASE WHEN "Laboratory"."C3" > 69 THEN (((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25) * ((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25)) WHEN ("Laboratory"."UA" = 3.7 AND "Laboratory"."UA" = 4.4) THEN 2 ELSE 1 END) AS REAL), 0))) * coalesce(CAST(AVG(CASE WHEN "Laboratory"."C3" > 69 THEN (((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25) * ((CAST("Laboratory"."FG" AS INTEGER) * 5) / 0.25)) WHEN ("Laboratory"."UA" = 3.7 AND "Laboratory"."UA" = 4.4) THEN 2 ELSE 1 END) AS REAL), 0))) AS "o3" FROM "Laboratory" AS "Laboratory" WHERE "Laboratory"."LDH" = 148 GROUP BY "Laboratory"."ID") SELECT "s7"."o3" AS "o0", coalesce(((((log(10, (round(CAST("s7"."o2" AS REAL), 2) * 0.25)) * 0.2) + 2.0) * (("s7"."o2" - "s7"."o3") * log(10, ("Laboratory"."ALB" / 3.7)))) * 0.25), 0) AS "o1", log(10, ("Laboratory"."ALB" / 3.7)) AS "o2", ((1 - coalesce(((((log(10, (round(CAST("s7"."o2" AS REAL), 2) * 0.25)) * 0.2) + 2.0) * (("s7"."o2" - "s7"."o3") * log(10, ("Laboratory"."ALB" / 3.7)))) * 0.25), 0)) * 0.5) AS "o3", ("Laboratory"."ALB" / 3.7) AS "o4", coalesce((("Laboratory"."ALB" / 3.7) - ("Laboratory"."ALB" / 3.7)), 0) AS "o5", CASE WHEN (log(10, ("Laboratory"."ALB" / 3.7)) > 10 AND "Laboratory"."ALB" = 3.5) THEN 1 ELSE 0 END AS "o6", (coalesce((("Laboratory"."ALB" / 3.7) - ("Laboratory"."ALB" / 3.7)), 0) / CASE WHEN (log(10, ("Laboratory"."ALB" / 3.7)) > 10 AND "Laboratory"."ALB" = 3.5) THEN 1 ELSE 0 END) AS "o7", "Laboratory"."ALP" AS "o8" FROM "Patient" AS "Patient" INNER JOIN "s7" AS "s7" ON "s7"."o0" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" LEFT JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" WHERE (NOT ("s7"."o0" IS NULL) AND NOT ("Laboratory"."ID" IS NULL) AND "s7"."o1" = "s7"."o1" AND "s7"."o2" = "Patient"."First Date") ORDER BY CASE WHEN (log(10, ("Laboratory"."ALB" / 3.7)) > 10 AND "Laboratory"."ALB" = 3.5) THEN 1 ELSE 0 END DESC
```

- `-` derived/derived: unknown
- `*` derived/summary: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` summary/summary: unknown
- `*` column/derived: unknown
- `/` column/derived: unknown
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/function: unknown
- `-` step output/step output: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## thrombosis_prediction-15 (attempt 59)

```sql
WITH "s3" AS (SELECT DISTINCT "Laboratory"."RNP" AS "o0", AVG(CASE WHEN "Patient"."ID" != 287861 THEN 1 ELSE 0 END) AS "o1" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE "Laboratory"."RNP" IN ((SELECT "Laboratory"."Date" AS "o0" FROM "Laboratory" AS "Laboratory")) GROUP BY "Laboratory"."RNP"), "s4" AS (SELECT "Examination"."ID" AS "o0", COUNT(*) AS "o1" FROM "Examination" AS "Examination" LEFT JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" GROUP BY "Examination"."ID") SELECT "s4"."o1" AS "o0", "Laboratory"."DNA" AS "o1", ((((CASE WHEN "s4"."o1" = ("s4"."o1" / round((("s3"."o1" - exp(("s3"."o1" - "s3"."o1"))) / 10), 2)) THEN 10 ELSE 1 END * 0.5) * abs(("s4"."o1" - "s4"."o1"))) + ("s4"."o1" / "Laboratory"."APTT")) - ((((CASE WHEN "s4"."o1" = ("s4"."o1" / round((("s3"."o1" - exp(("s3"."o1" - "s3"."o1"))) / 10), 2)) THEN 10 ELSE 1 END * 0.5) * abs(("s4"."o1" - "s4"."o1"))) / CASE WHEN "s4"."o1" = ("s4"."o1" / round((("s3"."o1" - exp(("s3"."o1" - "s3"."o1"))) / 10), 2)) THEN 10 ELSE 1 END) * (((("Laboratory"."ALP" * 10) + "Laboratory"."GPT") * 0.75) + (((((((("Laboratory"."ALP" * 10) + "Laboratory"."GPT") * 0.75) / 0.2) * 0.75) / 10) + ("Examination"."aCL IgA" * 3)) + (1 - CASE WHEN "s4"."o1" = "Laboratory"."CENTROMEA" THEN 4 END))))) AS "o2", (((1 - power(CAST("Laboratory"."T-BIL" AS INTEGER), 1.5)) * (round(CAST("Laboratory"."UN" AS REAL), 2) * 0.25)) * 2) AS "o3", PERCENT_RANK() OVER (ORDER BY (((1 - power(CAST("Laboratory"."T-BIL" AS INTEGER), 1.5)) * (round(CAST("Laboratory"."UN" AS REAL), 2) * 0.25)) * 2) ASC) AS "o4" FROM "s4" AS "s4" INNER JOIN "Patient" AS "Patient" ON "s4"."o0" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" INNER JOIN "s3" AS "s3" ON "s3"."o0" = "Laboratory"."RNP"
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown (disputed (model))
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` column/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `/` case/derived: unknown
- `/` derived/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` function/step output: unknown
- `-` step output/step output: unknown (equal operands)
- `*` constant-derived: unknown (a constant)
- `-` step output/step output: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` column/step output: unknown

## thrombosis_prediction-16 (attempt 14)

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

## thrombosis_prediction-17 (attempt 114)

```sql
SELECT "Examination"."ID" AS "o0", "Examination"."aCL IgA" AS "o1", coalesce(("Examination"."aCL IgA" - "Examination"."aCL IgM"), 0) AS "o2" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE NOT (CAST("Examination"."aCL IgM" AS REAL) IS NULL) ORDER BY "Examination"."ID" DESC, coalesce(("Examination"."aCL IgA" - "Examination"."aCL IgM"), 0) DESC
```

- `-` column/column: unknown (disputed (model))

## thrombosis_prediction-18 (attempt 10)

```sql
SELECT "Patient"."ID" AS "o0", AVG(((((100 - "Laboratory"."HCT") + 61.9) - ((100 - "Laboratory"."HCT") / 100)) * 10)) AS "o1", CASE WHEN AVG(((((100 - "Laboratory"."HCT") + 61.9) - ((100 - "Laboratory"."HCT") / 100)) * 10)) > 1231.81 THEN AVG(((((100 - "Laboratory"."HCT") + 61.9) - ((100 - "Laboratory"."HCT") / 100)) * 10)) ELSE 0 END AS "o2" FROM "Patient" AS "Patient" INNER JOIN "Laboratory" AS "Laboratory" ON "Patient"."ID" = "Laboratory"."ID" WHERE ((((100 - "Laboratory"."HCT") + 61.9) - ((100 - "Laboratory"."HCT") / 100)) * 10) = ((100 - "Laboratory"."HCT") + 61.9) GROUP BY "Patient"."ID"
```

- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown (disputed (model))
- `/` parameter CONVERT: plausible (model)
- `-` parameter WHOLE: plausible (model)
- `+` parameter REFERENCE: unknown (a constant)

## thrombosis_prediction-19 (attempt 98)

```sql
SELECT "Examination"."ID" AS "o0", "Patient"."Admission" AS "o1", CASE WHEN "Examination"."KCT" > '+' THEN 1 WHEN "Examination"."ANA Pattern" > 'P,S' THEN 1 ELSE 0 END AS "o2", round(CAST("Examination"."aCL IgG" AS REAL), 2) AS "o3" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE ("Examination"."Symptoms" = "Patient"."Admission" AND "Examination"."KCT" IN ('-', '+') AND "Examination"."RVVT" = '+') ORDER BY "Patient"."Admission" DESC, CAST("Examination"."aCL IgA" AS REAL) ASC
```


## thrombosis_prediction-20 (attempt 157)

```sql
SELECT "Patient"."ID" AS "o0", "Patient"."Admission" AS "o1", "Patient"."SEX" AS "o2" FROM "Patient" AS "Patient" ORDER BY "Patient"."ID" DESC LIMIT 100
```


