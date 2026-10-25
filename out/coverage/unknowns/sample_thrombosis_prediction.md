# thrombosis_prediction: 20 random unknown substantive calculations (of 1062)

## thrombosis_prediction-u1 (attempt 102) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - "s1"."o1")`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'rows', kind 'count', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."RVVT" AS "o0", COUNT(*) AS "o1" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" GROUP BY "Examination"."RVVT"), "s45" AS (SELECT DISTINCT "s1"."o0" AS "o0", power((((1 - round((round(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END AS REAL) * 3))), 2)) * (1 - round(CAST((((round(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((coalesce(0, 0) / 0.5) * 0.25))) - ((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1")
```

## thrombosis_prediction-u2 (attempt 123) -- mechanical class: NO UNIT

Node: `("s12"."o9" / ((CASE WHEN "s12"."o9" = ("s12"."o9" - ("s12"."o9" * 3)) THEN 2 WHEN ("s12"."o9" - ("s12"."o9" * 3)) = ("s12"."o9" - ("s12"."o9" * 3)) THEN 5 ELSE 0 END / 0.5) / 0.2))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s12" AS (SELECT "Patient"."ID" AS "o0", "Laboratory"."PLT" AS "o1", "Laboratory"."FG" AS "o2", (((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) + ("Laboratory"."FG" + "Laboratory"."FG")) AS "o3", "Laboratory"."GOT" AS "o4", ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) AS "o5", CASE WHEN ("Laboratory"."FG" + "Laboratory"."FG") > 78.0 THEN 1 WHEN CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END < "Laboratory"."SM" THEN 4 WHEN ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) = "Laboratory"."U-PRO" THEN 0 ELSE 1 END AS "o6", FIRST_VALUE("Laboratory"."SM") OVER (ORDER BY ((1 - ("Laboratory"."C3" / 42)) * (1 - CASE WHEN "Laboratory"."C3" = 87 THEN 0 ELSE 0 END)) ASC) AS "o7", coalesce("Examination"."ID", 0) AS "o8", ((((1 - ("Laboratory"."C3" / 42)) * (1
```

## thrombosis_prediction-u3 (attempt 3) -- mechanical class: NO UNIT

Node: `(((CAST(COALESCE(CAST(ABS(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(COALESCE(CAST(ABS(2) AS REAL), 0) AS REAL) * 0.5)) * (CAST(COALESCE(CAST(ABS(2) AS REAL), 0) AS REAL) * 0.25))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s8" AS (SELECT "Patient"."ID" AS "o0" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE (((((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + (((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + "Examination"."aCL IgG")) * "Examination"."aCL IgA") > 0.0 AND ("Examination"."aCL IgG" = 0.0 OR (("Examination"."aCL IgM" + 2.1) + (((("Examination"."Thrombosis" * 0.75) / 0.2) + 0) / 0.25)) = 4.2 OR "Examination"."RVVT" = '+')) GROUP BY "Patient"."ID") SELECT round(SUM(((((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REA
```

## thrombosis_prediction-u4 (attempt 171) -- mechanical class: NO UNIT

Node: `(COALESCE(CAST(COUNT(*) AS INTEGER), 0) / ABS((COALESCE(CAST(COUNT(*) AS INTEGER), 0) * (1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUNT(*) = 1390 THEN 1 WHEN "Laboratory"."ID" > 4843434 THEN 2 ELSE 0 END * 10)))))`

- left operand: unit 'rows', kind 'count', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: Laboratory.ID [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "Laboratory"."ID" AS "o0", COUNT(*) AS "o1", (((1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUNT(*) = 1390 THEN 1 WHEN "Laboratory"."ID" > 4843434 THEN 2 ELSE 0 END * 10)) + 0) + coalesce(CAST(COUNT(*) AS INTEGER), 0)) AS "o2", AVG(CASE WHEN "Laboratory"."CPK" = 48 THEN 3 ELSE 0 END) AS "o3", ((1 - (((coalesce(CAST(COUNT(*) AS INTEGER), 0) / abs((coalesce(CAST(COUNT(*) AS INTEGER), 0) * (1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUNT(*) = 1390 THEN 1 WHEN "Laboratory"."ID" > 4843434 THEN 2 ELSE 0 END * 10))))) * 10) * 0.75)) * round((CAST(COUNT(*) AS REAL) / ((coalesce(CAST(COUNT(*) AS INTEGER), 0) / abs((coalesce(CAST(COUNT(*) AS INTEGER), 0) * (1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUN
```

## thrombosis_prediction-u5 (attempt 102) -- mechanical class: NO UNIT

Node: `((1 - ROUND((ROUND(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWE`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."RVVT" AS "o0", COUNT(*) AS "o1" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" GROUP BY "Examination"."RVVT"), "s45" AS (SELECT DISTINCT "s1"."o0" AS "o0", power((((1 - round((round(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END AS REAL) * 3))), 2)) * (1 - round(CAST((((round(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((coalesce(0, 0) / 0.5) * 0.25))) - ((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1")
```

## thrombosis_prediction-u6 (attempt 14) -- mechanical class: NO UNIT

Node: `(POWER(ROUND("s1"."o1", 2), 1.5) + (ROUND((1 - CASE WHEN (POWER(ROUND(CAST("s1"."o1" AS REAL), 2), 2) > 101 OR POWER(ROUND(CAST("s1"."o1" AS REAL), 2), 2) = 101) THEN 3 WHEN (POWER(ROUND(CAST("s1"."o1" AS REAL), 2), 2) = 101 AND POWER(ROUND(CAST("s1"."o1" AS REAL), 2), 2) = POWER(ROUND(CAST("s1"."o1`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Patient"."Diagnosis" AS "o0", "Laboratory"."ALP" AS "o1", "Laboratory"."UN" AS "o2" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE "Laboratory"."UN" >= 11 ORDER BY "Patient"."Diagnosis" DESC LIMIT 10), "s12" AS (SELECT "s1"."o2" AS "o0", power(round(CAST("s1"."o1" AS REAL), 2), 2) AS "o1", (((power(round(CAST("s1"."o1" AS REAL), 2), 2) / power(round(CAST("s1"."o1" AS REAL), 2), 2)) * ((power(round("s1"."o1", 2), 1.5) + (round((1 - CASE WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) > 101 OR power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101) THEN 3 WHEN (power(round(CAST("s1"."o1" AS REAL), 2), 2) = 101 AND power(round(CAST("s1"."o1" AS REAL), 2), 2) = power(round(CAST("s1"."o1" AS REAL), 2), 2) AND power(round(CAST("s1"
```

## thrombosis_prediction-u7 (attempt 94) -- mechanical class: SCORE

Node: `((CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) * ROUND(CAST(CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END AS REAL), 2))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."Symptoms" AS "o0", COUNT(*) AS "o1" FROM "Examination" AS "Examination" GROUP BY "Examination"."Symptoms") SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", CASE WHEN "s1"."o0" = 'CVA' THEN 10 ELSE ("s1"."o1" / round(CAST((1 - ((CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) * round(CAST(CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END AS REAL), 2))) AS REAL), 2)) END AS "o2", ("s1"."o1" / round(CAST((1 - ((CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) * round(CAST(CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END AS REAL), 2))) AS REAL), 2)) AS "o3", CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung 
```

## thrombosis_prediction-u8 (attempt 71) -- mechanical class: LOST

Node: `("Laboratory"."PT" + ((((1 - ("Laboratory"."PT" / 11.0)) * (("Laboratory"."ALB" + "Laboratory"."HGB") * 5)) * 0.75) + ("Laboratory"."TAT2" * 0.1)))`

- left operand: unit 'seconds', kind 'measure', quantity ('Laboratory.PT', 'value')
- right operand: unit '', kind '', quantity ()
- stored columns under it: Laboratory.ALB [unit 'g/dL' (model), kind 'measure', scale '']; Laboratory.HGB [unit 'g/dL' (model), kind 'measure', scale '']; Laboratory.PT [unit 'seconds' (model), kind 'measure', scale '']; Laboratory.TAT2 [unit 'ng/mL' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "Examination"."ID" AS "o0", abs((((("Laboratory"."PT" + ((((1 - ("Laboratory"."PT" / 11.0)) * (("Laboratory"."ALB" + "Laboratory"."HGB") * 5)) * 0.75) + ("Laboratory"."TAT2" * 0.1))) * "Laboratory"."TAT") * ("Laboratory"."UN" / 10)) * CASE WHEN ((("Laboratory"."PT" + ((((1 - ("Laboratory"."PT" / 11.0)) * (("Laboratory"."ALB" + "Laboratory"."HGB") * 5)) * 0.75) + ("Laboratory"."TAT2" * 0.1))) * "Laboratory"."TAT") * ("Laboratory"."UN" / 10)) = 2681.12 THEN 2 WHEN "Examination"."ID" = 5746950 THEN 0 ELSE 0 END)) AS "o1", (((("Laboratory"."PT" + ((((1 - ("Laboratory"."PT" / 11.0)) * (("Laboratory"."ALB" + "Laboratory"."HGB") * 5)) * 0.75) + ("Laboratory"."TAT2" * 0.1))) * "Laboratory"."TAT") * ("Laboratory"."UN" / 10)) * CASE WHEN ((("Laboratory"."PT" + ((((1 - ("Laboratory"."PT" / 11.0)) * (("Laboratory"."ALB" + "Laboratory"."HGB") * 5)) * 0.75) + ("Laboratory"."TAT2" * 0.1))) * "La
```

## thrombosis_prediction-u9 (attempt 133) -- mechanical class: NO UNIT

Node: `("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))`

- left operand: unit '', kind '', quantity ('Examination.Thrombosis', 'value')
- right operand: unit 'GPL units', kind '', quantity ()
- stored columns under it: Examination.Thrombosis [unit '' (-), kind '', scale '']; Examination.aCL IgG [unit 'GPL units' (model), kind 'measure', scale '']
- catalogue relations among them: none

Whole query:
```sql
WITH "s10" AS (SELECT "Examination"."Examination Date" AS "o0", ((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) / (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) * (1 - (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) / ((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1
```

## thrombosis_prediction-u10 (attempt 171) -- mechanical class: NO UNIT

Node: `(((1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUNT(*) = 1390 THEN 1 WHEN "Laboratory"."ID" > 4843434 THEN 2 ELSE 0 END * 10)) + 0) + COALESCE(CAST(COUNT(*) AS INTEGER), 0))`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'rows', kind 'count', quantity ()
- stored columns under it: Laboratory.ID [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "Laboratory"."ID" AS "o0", COUNT(*) AS "o1", (((1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUNT(*) = 1390 THEN 1 WHEN "Laboratory"."ID" > 4843434 THEN 2 ELSE 0 END * 10)) + 0) + coalesce(CAST(COUNT(*) AS INTEGER), 0)) AS "o2", AVG(CASE WHEN "Laboratory"."CPK" = 48 THEN 3 ELSE 0 END) AS "o3", ((1 - (((coalesce(CAST(COUNT(*) AS INTEGER), 0) / abs((coalesce(CAST(COUNT(*) AS INTEGER), 0) * (1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUNT(*) = 1390 THEN 1 WHEN "Laboratory"."ID" > 4843434 THEN 2 ELSE 0 END * 10))))) * 10) * 0.75)) * round((CAST(COUNT(*) AS REAL) / ((coalesce(CAST(COUNT(*) AS INTEGER), 0) / abs((coalesce(CAST(COUNT(*) AS INTEGER), 0) * (1 - (CASE WHEN (COUNT(*) = 1390 AND COUNT(*) > 1390) THEN 4 WHEN "Laboratory"."ID" >= 4843434 THEN 3 WHEN COUN
```

## thrombosis_prediction-u11 (attempt 102) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - "s1"."o1")`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'rows', kind 'count', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."RVVT" AS "o0", COUNT(*) AS "o1" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" GROUP BY "Examination"."RVVT"), "s45" AS (SELECT DISTINCT "s1"."o0" AS "o0", power((((1 - round((round(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END AS REAL) * 3))), 2)) * (1 - round(CAST((((round(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((coalesce(0, 0) / 0.5) * 0.25))) - ((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1")
```

## thrombosis_prediction-u12 (attempt 133) -- mechanical class: NO UNIT

Node: `(((((("Examination"."ANA" * (POWER(ROUND("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) / ((((("Examination"."ANA" * (POW`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: Examination.ANA [unit 'titer' (model), kind '', scale 'ratio']; Examination.Thrombosis [unit '' (-), kind '', scale '']; Examination.aCL IgA [unit 'APL units' (model), kind 'measure', scale '']; Examination.aCL IgG [unit 'GPL units' (model), kind 'measure', scale '']; Examination.aCL IgM [unit 'MPL units' (model), kind 'measure', scale '']
- catalogue relations among them: Examination.aCL IgA comparable Examination.aCL IgG; Examination.aCL IgA comparable Examination.aCL IgM; Examination.aCL IgG comparable Examination.aCL IgM

Whole query:
```sql
WITH "s10" AS (SELECT "Examination"."Examination Date" AS "o0", ((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) / (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) * (1 - (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) / ((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1
```

## thrombosis_prediction-u13 (attempt 62) -- mechanical class: BOTH KNOWN

Node: `("Laboratory"."HGB" / ("Laboratory"."TG" + "Laboratory"."UN"))`

- left operand: unit 'g/dL', kind 'measure', quantity ('Laboratory.HGB', 'value')
- right operand: unit 'mg/dL', kind '', quantity ()
- stored columns under it: Laboratory.HGB [unit 'g/dL' (model), kind 'measure', scale '']; Laboratory.TG [unit 'mg/dL' (model), kind 'measure', scale '']; Laboratory.UN [unit 'mg/dL' (model), kind 'measure', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "Laboratory"."RA" AS "o0", round("Laboratory"."Date", 2) AS "o1", (("Laboratory"."C3" * 10) + ((("Laboratory"."C3" * 10) * 0.2) / 5)) AS "o2", (("Laboratory"."C3" * 10) * 0.2) AS "o3", ((coalesce(CAST(((("Laboratory"."C3" * 10) * 0.2) / 5) AS REAL), 0) - round("Laboratory"."Date", 2)) * (CAST(coalesce(CAST(((("Laboratory"."C3" * 10) * 0.2) / 5) AS REAL), 0) AS REAL) * ("Laboratory"."ALB" / 3.7))) AS "o4" FROM "Laboratory" AS "Laboratory" INNER JOIN "Patient" AS "Patient" ON "Laboratory"."ID" = "Patient"."ID" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" WHERE (((((("Laboratory"."HGB" / ("Laboratory"."TG" + "Laboratory"."UN")) + ((CASE WHEN (sqrt("Laboratory"."UN") * CASE WHEN "Laboratory"."TG" = 88 THEN 2 ELSE 0 END) > "Laboratory"."Date" THEN 3 WHEN "Laboratory"."LDH" < 158 THEN 4 WHEN "Laboratory"."LDH" > 158 THEN 5 WHEN "Laboratory"."LDH" > 29
```

## thrombosis_prediction-u14 (attempt 3) -- mechanical class: BOTH KNOWN

Node: `(((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + "Examination"."aCL IgG")`

- left operand: unit 'titer × GPL units', kind '', quantity ()
- right operand: unit 'GPL units', kind 'measure', quantity ('Examination.aCL IgG', 'value')
- stored columns under it: Examination.ANA [unit 'titer' (model), kind '', scale 'ratio']; Examination.aCL IgG [unit 'GPL units' (model), kind 'measure', scale '']
- catalogue relations among them: none

Whole query:
```sql
WITH "s8" AS (SELECT "Patient"."ID" AS "o0" FROM "Examination" AS "Examination" INNER JOIN "Patient" AS "Patient" ON "Examination"."ID" = "Patient"."ID" WHERE (((((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + (((("Examination"."ANA" / 16) * "Examination"."aCL IgG") * 1.5) + "Examination"."aCL IgG")) * "Examination"."aCL IgA") > 0.0 AND ("Examination"."aCL IgG" = 0.0 OR (("Examination"."aCL IgM" + 2.1) + (((("Examination"."Thrombosis" * 0.75) / 0.2) + 0) / 0.25)) = 4.2 OR "Examination"."RVVT" = '+')) GROUP BY "Patient"."ID") SELECT round(SUM(((((0.25 / (CAST((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) AS REAL) * 0.2)) / (((coalesce(CAST(abs(2) AS REAL), 0) * (CAST(abs(2) AS INTEGER) * 0.5)) / ((CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 1.5) * (CAST(coalesce(CAST(abs(2) AS REAL), 0) AS REAL) * 0.25))) + (((CAST(coalesce(CAST(abs(2) AS REA
```

## thrombosis_prediction-u15 (attempt 102) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - "s1"."o1")`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'rows', kind 'count', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."RVVT" AS "o0", COUNT(*) AS "o1" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" GROUP BY "Examination"."RVVT"), "s45" AS (SELECT DISTINCT "s1"."o0" AS "o0", power((((1 - round((round(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END AS REAL) * 3))), 2)) * (1 - round(CAST((((round(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((coalesce(0, 0) / 0.5) * 0.25))) - ((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1")
```

## thrombosis_prediction-u16 (attempt 137) -- mechanical class: NO UNIT

Node: `("Laboratory"."FG" * (CASE WHEN "Examination"."ANA Pattern" > 'p' THEN 1 ELSE 1 END * 2))`

- left operand: unit 'mg/dL', kind 'measure', quantity ('Laboratory.FG', 'value')
- right operand: unit '', kind '', quantity ()
- stored columns under it: Examination.ANA Pattern [unit '' (-), kind '', scale '']; Laboratory.FG [unit 'mg/dL' (model), kind 'measure', scale '']
- catalogue relations among them: none

Whole query:
```sql
WITH "s11" AS (SELECT "Patient"."First Date" AS "o0", ((("Laboratory"."FG" * (CASE WHEN "Examination"."ANA Pattern" > 'p' THEN 1 ELSE 1 END * 2)) * ((CAST(("Laboratory"."FG" * (CASE WHEN "Examination"."ANA Pattern" > 'p' THEN 1 ELSE 1 END * 2)) AS REAL) / "Examination"."ANA") + (CASE WHEN "Examination"."ANA Pattern" < 'p' THEN 1 WHEN (CAST(("Laboratory"."FG" * (CASE WHEN "Examination"."ANA Pattern" > 'p' THEN 1 ELSE 1 END * 2)) AS REAL) / "Examination"."ANA") > "Examination"."LAC" THEN 10 WHEN "Patient"."First Date" > '1992-02-27' THEN 1 WHEN (CAST(("Laboratory"."FG" * (CASE WHEN "Examination"."ANA Pattern" > 'p' THEN 1 ELSE 1 END * 2)) AS REAL) / "Examination"."ANA") = "Laboratory"."RA" THEN 2 ELSE 0 END * 5))) * 0.75) AS "o1", ((CAST(("Laboratory"."FG" * (CASE WHEN "Examination"."ANA Pattern" > 'p' THEN 1 ELSE 1 END * 2)) AS REAL) / "Examination"."ANA") + (CASE WHEN "Examination"."ANA 
```

## thrombosis_prediction-u17 (attempt 102) -- mechanical class: NO UNIT

Node: `((ROUND(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((COALESCE(0, 0) / 0.5) * 0.25)))`

- left operand: unit 'rows × rows × rows', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."RVVT" AS "o0", COUNT(*) AS "o1" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" GROUP BY "Examination"."RVVT"), "s45" AS (SELECT DISTINCT "s1"."o0" AS "o0", power((((1 - round((round(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END AS REAL) * 3))), 2)) * (1 - round(CAST((((round(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((coalesce(0, 0) / 0.5) * 0.25))) - ((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1")
```

## thrombosis_prediction-u18 (attempt 102) -- mechanical class: BOTH KNOWN

Node: `((1 - "s1"."o1") * (1 - "s1"."o1"))`

- left operand: unit 'rows', kind '', quantity ()
- right operand: unit 'rows', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."RVVT" AS "o0", COUNT(*) AS "o1" FROM "Patient" AS "Patient" INNER JOIN "Examination" AS "Examination" ON "Patient"."ID" = "Examination"."ID" GROUP BY "Examination"."RVVT"), "s45" AS (SELECT DISTINCT "s1"."o0" AS "o0", power((((1 - round((round(CAST(((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) + 0) AS INTEGER), 0) + ((CAST((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END / 1.5) AS REAL) * 2) * (CAST(CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1") THEN 1 ELSE 0 END AS REAL) * 3))), 2)) * (1 - round(CAST((((round(CAST("s1"."o1" AS REAL)) * (((1 - "s1"."o1") * (1 - "s1"."o1")) * 0.1)) * (CAST(((1 - "s1"."o1") * (1 - "s1"."o1")) AS REAL) / ((coalesce(0, 0) / 0.5) * 0.25))) - ((CASE WHEN (1 - "s1"."o1") BETWEEN (1 - "s1"."o1") AND (1 - "s1"."o1")
```

## thrombosis_prediction-u19 (attempt 133) -- mechanical class: LOST

Node: `("Examination"."ANA" * (POWER(ROUND("Examination"."ANA", 0), 1.5) / 0.25))`

- left operand: unit 'titer', kind '', quantity ('Examination.ANA', 'value')
- right operand: unit '', kind '', quantity ()
- stored columns under it: Examination.ANA [unit 'titer' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s10" AS (SELECT "Examination"."Examination Date" AS "o0", ((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) / (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) * (1 - (((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1) + (("Examination"."ANA" * ("Examination"."aCL IgA" * 0.25)) * 2))) * 1.5) / 1.5) + ("Examination"."Thrombosis" / (("Examination"."aCL IgG" * 10) * 5))) / ((((("Examination"."ANA" * (power(round("Examination"."ANA", 0), 1.5) / 0.25)) + (("Examination"."aCL IgM" / 2.1
```

## thrombosis_prediction-u20 (attempt 94) -- mechanical class: NO UNIT

Node: `((((1 - CASE WHEN (CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) > (CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) THEN 0 ELSE 0 END) + (CASE WHEN CASE WHEN "s1"."o0" > 'fin`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "Examination"."Symptoms" AS "o0", COUNT(*) AS "o1" FROM "Examination" AS "Examination" GROUP BY "Examination"."Symptoms") SELECT "s1"."o1" AS "o0", "s1"."o0" AS "o1", CASE WHEN "s1"."o0" = 'CVA' THEN 10 ELSE ("s1"."o1" / round(CAST((1 - ((CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) * round(CAST(CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END AS REAL), 2))) AS REAL), 2)) END AS "o2", ("s1"."o1" / round(CAST((1 - ((CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END * 0.2) * round(CAST(CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung emboli' THEN 3 ELSE 0 END AS REAL), 2))) AS REAL), 2)) AS "o3", CASE WHEN "s1"."o0" > 'finger ulcer' THEN 5 WHEN "s1"."o0" = 'CNS, CVA, Lung 
```

