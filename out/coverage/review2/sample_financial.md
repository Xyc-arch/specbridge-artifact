# financial: 20 random delivered programs

## financial-1 (attempt 101)

```sql
SELECT "client"."client_id" AS "o0", sqrt((((((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75) + ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) / ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75))) * (CAST(round((((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75) + ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) / ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75))), 2) AS REAL) / (((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75) + ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) / ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75))))) / 0.5)) AS "o1", (((((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75) + ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) / ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75))) * (CAST(round((((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75) + ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) / ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75))), 2) AS REAL) / (((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75) + ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) / ((CASE WHEN "disp"."type" = 'DISPONENT' THEN 3 WHEN "disp"."type" BETWEEN CAST("client"."district_id" AS REAL) AND "disp"."account_id" THEN 1 ELSE 0 END / 2) * 0.75))))) / 0.5) AS "o2" FROM "client" AS "client" INNER JOIN "disp" AS "disp" ON "client"."client_id" = "disp"."client_id"
```

- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## financial-2 (attempt 56)

```sql
WITH "s9" AS (SELECT "loan"."status" AS "o0", AVG(("loan"."payments" / "loan"."payments")) AS "o1", coalesce(AVG(("loan"."payments" / "loan"."payments")), 0) AS "o2", (CAST(SUM(CASE WHEN "loan"."date" = '1998-04-16' THEN 3 WHEN ((("loan"."amount" / 117024) / 0.5) / (("loan"."amount" + (("loan"."amount" / 117024) / 0.5)) / 2)) > 0.0 THEN 0 WHEN ((CAST("loan"."payments" AS REAL) * 3) * 0.25) > 2952.75 THEN 3 END) AS REAL) / SUM(CASE WHEN "loan"."date" = '1998-04-16' THEN 3 WHEN ((("loan"."amount" / 117024) / 0.5) / (("loan"."amount" + (("loan"."amount" / 117024) / 0.5)) / 2)) > 0.0 THEN 0 WHEN ((CAST("loan"."payments" AS REAL) * 3) * 0.25) > 2952.75 THEN 3 END)) AS "o3", (MAX("loan"."duration") / SUM(("loan"."amount" / 117024))) AS "o4" FROM "loan" AS "loan" WHERE (((("loan"."amount" / 117024) / 0.5) / (("loan"."amount" + (("loan"."amount" / 117024) / 0.5)) / 2)) > "loan"."date" OR ("loan"."payments" / "loan"."payments") = 1.0) GROUP BY "loan"."status"), "s15" AS (SELECT round(CAST("s9"."o4" AS REAL), 2) AS "o0", AVG("s9"."o2") AS "o1", AVG((0.1 / (abs((((((CAST(round(CAST("s9"."o4" AS REAL), 2) AS REAL) / "s9"."o4") * (round(CAST("s9"."o4" AS REAL), 2) * ("s9"."o3" / CAST("s9"."o3" AS REAL)))) / 1.5) * 10) + ("s9"."o2" / "s9"."o2"))) * 0.5))) AS "o2" FROM "s9" AS "s9" WHERE "s9"."o4" < (CAST(exp(((round(CAST("s9"."o4" AS REAL), 2) / ((((CAST(round(CAST("s9"."o4" AS REAL), 2) AS REAL) / "s9"."o4") * (round(CAST("s9"."o4" AS REAL), 2) * ("s9"."o3" / CAST("s9"."o3" AS REAL)))) / 1.5) * 10)) * 0.1)) AS REAL) / exp(((round(CAST("s9"."o4" AS REAL), 2) / ((((CAST(round(CAST("s9"."o4" AS REAL), 2) AS REAL) / "s9"."o4") * (round(CAST("s9"."o4" AS REAL), 2) * ("s9"."o3" / CAST("s9"."o3" AS REAL)))) / 1.5) * 10)) * 0.1))) GROUP BY round(CAST("s9"."o4" AS REAL), 2)) SELECT "s15"."o0" AS "o0", AVG(CASE WHEN coalesce(CAST("s15"."o1" AS REAL), 0) < ((10 / ((coalesce(CAST("s15"."o1" AS REAL), 0) * 1.5) / 10)) * round(CAST("s15"."o0" AS REAL), 2)) THEN (((((coalesce(CAST("s15"."o1" AS REAL), 0) * 1.5) / 10) + ((((CAST("s15"."o0" AS INTEGER) / ((coalesce(CAST("s15"."o1" AS REAL), 0) * 1.5) / 10)) * (CAST("s15"."o0" AS REAL) * 100)) + 0) + ("s15"."o0" / sqrt(round(CAST("s15"."o0" AS REAL), 2))))) + 0) * coalesce(CAST("s15"."o0" AS REAL), 0)) WHEN ((((coalesce(CAST("s15"."o1" AS REAL), 0) * 1.5) / 10) + ((((CAST("s15"."o0" AS INTEGER) / ((coalesce(CAST("s15"."o1" AS REAL), 0) * 1.5) / 10)) * (CAST("s15"."o0" AS REAL) * 100)) + 0) + ("s15"."o0" / sqrt(round(CAST("s15"."o0" AS REAL), 2))))) + 0) < ((1 - sqrt(round(CAST("s15"."o0" AS REAL), 2))) * abs("s15"."o0")) THEN 10 ELSE 0 END) AS "o1", AVG((abs("s15"."o0") - coalesce(CAST("s15"."o0" AS REAL), 0))) AS "o2", round(AVG((((1 - round(CAST("s15"."o0" AS REAL), 2)) + (1 - round(CAST("s15"."o0" AS REAL), 2))) * coalesce(CAST("s15"."o0" AS REAL), 0))), 2) AS "o3", coalesce(AVG(((coalesce(CAST("s15"."o0" AS REAL), 0) * 2) * coalesce(CAST("s15"."o0" AS REAL), 0))), 0) AS "o4" FROM "s15" AS "s15" WHERE (NOT ("s15"."o0" IS NULL) AND "s15"."o2" = (CAST(coalesce(CAST(round((((1 - ((("s15"."o1" / "s15"."o2") / 0.2) / 10)) + ((1 - ((("s15"."o1" / "s15"."o2") / 0.2) / 10)) / 0.2)) + (coalesce(CAST("s15"."o1" AS REAL), 0) * 1.5)), 2) AS REAL), 0) AS REAL) * 3)) GROUP BY "s15"."o0"
```

- `/` summary/summary: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `/` summary/summary: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` column/derived: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `/` constant-derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/step output: unknown
- `/` step output/step output: unknown
- `/` step output/step output: unknown
- `/` function/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/step output: unknown
- `*` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/step output: unknown
- `+` derived/derived: plausible (model)
- `-` parameter WHOLE: unknown (a constant)
- `-` step output/step output: plausible (model)
- `*` derived/step output: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` function/step output: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter CONVERT: plausible (model)
- `/` derived/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/step output: unknown
- `*` derived/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)

## financial-3 (attempt 153)

```sql
WITH "s1" AS (SELECT "card"."card_id" AS "o0", "disp"."type" AS "o1" FROM "card" AS "card" INNER JOIN "disp" AS "disp" ON "card"."disp_id" = "disp"."disp_id" WHERE "card"."type" = 'classic' ORDER BY "card"."card_id" ASC LIMIT 10) SELECT "s1"."o0" AS "o0", "trans"."amount" AS "o1", "s1"."o1" AS "o2", "account"."district_id" AS "o3" FROM "trans" AS "trans" INNER JOIN "account" AS "account" ON "trans"."account_id" = "account"."account_id" INNER JOIN "loan" AS "loan" ON "account"."account_id" = "loan"."account_id" INNER JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" INNER JOIN "s1" AS "s1" ON "s1"."o1" = "disp"."type" WHERE ("loan"."amount" > 210744 AND NOT ("trans"."amount" IS NULL) AND NOT ("s1"."o1" IS NULL))
```


## financial-4 (attempt 192)

```sql
SELECT "account"."date" AS "o0", round(((1 - (((1 - CASE WHEN "order"."k_symbol" > '' THEN 5 ELSE 0 END) / 0.5) + ("loan"."payments" / 3937.0))) / (1 - ("loan"."amount" / 1000))), 2) AS "o1", "loan"."amount" AS "o2" FROM "trans" AS "trans" INNER JOIN "account" AS "account" ON "trans"."account_id" = "account"."account_id" INNER JOIN "loan" AS "loan" ON "account"."account_id" = "loan"."account_id" INNER JOIN "order" AS "order" ON "account"."account_id" = "order"."account_id" ORDER BY "loan"."amount" ASC
```

- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)

## financial-5 (attempt 29)

```sql
SELECT "order"."order_id" AS "o0", "order"."amount" AS "o1", "account"."frequency" AS "o2", CAST("account"."date" AS TEXT) AS "o3" FROM "account" AS "account" LEFT JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" INNER JOIN "order" AS "order" ON "account"."account_id" = "order"."account_id" ORDER BY "order"."order_id" DESC
```


## financial-6 (attempt 3)

```sql
SELECT "disp"."client_id" AS "o0", "district"."A5" AS "o1", "district"."A12" AS "o2" FROM "district" AS "district" INNER JOIN "account" AS "account" ON "district"."district_id" = "account"."district_id" INNER JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" LEFT JOIN "trans" AS "trans" ON "account"."account_id" = "trans"."account_id" ORDER BY "disp"."client_id" ASC
```


## financial-7 (attempt 191)

```sql
SELECT "account"."district_id" AS "o0", (((0 - "loan"."payments") + ("loan"."amount" / "loan"."duration")) * 1.5) AS "o1", "account"."frequency" AS "o2", (((0 - "loan"."payments") + ("loan"."amount" / "loan"."duration")) - ((((0 - "loan"."payments") + ("loan"."amount" / "loan"."duration")) * 1.5) / 0.2)) AS "o3", ("loan"."amount" / "loan"."duration") AS "o4" FROM "account" AS "account" INNER JOIN "loan" AS "loan" ON "account"."account_id" = "loan"."account_id" INNER JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" INNER JOIN "client" AS "client" ON "disp"."client_id" = "client"."client_id" WHERE (((0 - "loan"."payments") + ("loan"."amount" / "loan"."duration")) - ((((0 - "loan"."payments") + ("loan"."amount" / "loan"."duration")) * 1.5) / 0.2)) >= 4461.17
```

- `/` column/column: plausible (model)
- `-` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `-` parameter ZERO: unknown (a constant)

## financial-8 (attempt 111)

```sql
SELECT "account"."district_id" AS "o0", "account"."frequency" AS "o1", "loan"."payments" AS "o2" FROM "loan" AS "loan" INNER JOIN "account" AS "account" ON "loan"."account_id" = "account"."account_id" ORDER BY CAST(((("loan"."amount" / 1000) * 0.2) / CAST(((("loan"."duration" / (CASE WHEN "account"."frequency" >= 'POPLATEK PO OBRATU' THEN 1 ELSE 4 END / 10)) + ("loan"."payments" / "loan"."payments")) + 0) AS REAL)) AS REAL) DESC
```

- `/` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `/` column/column: unknown (equal operands)
- `/` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)

## financial-9 (attempt 99)

```sql
SELECT "loan"."loan_id" AS "o0", "loan"."status" AS "o1", "account"."frequency" AS "o2" FROM "loan" AS "loan" INNER JOIN "account" AS "account" ON "loan"."account_id" = "account"."account_id" ORDER BY "loan"."status" DESC
```


## financial-10 (attempt 81)

```sql
SELECT "order"."k_symbol" AS "o0", "account"."account_id" AS "o1" FROM "order" AS "order" INNER JOIN "account" AS "account" ON "order"."account_id" = "account"."account_id" WHERE NOT ("order"."amount" IS NULL) GROUP BY "account"."account_id", "order"."k_symbol"
```


## financial-11 (attempt 161)

```sql
SELECT "client"."client_id" AS "o0", "client"."gender" AS "o1", "client"."district_id" AS "o2", "client"."birth_date" AS "o3" FROM "client" AS "client" ORDER BY "client"."client_id" DESC
```


## financial-12 (attempt 63)

```sql
SELECT "district"."A4" AS "o0", (("district"."A15" / 2985) * CAST("district"."A15" AS REAL)) AS "o1", round("district"."A14", 2) AS "o2", "district"."A9" AS "o3", "district"."A12" AS "o4", 1 AS "o5", CASE WHEN (round("district"."A14", 2) = 104 AND "district"."A6" = '37') THEN 5 WHEN "district"."A12" < 1.7 THEN 5 WHEN "district"."A9" = 5 THEN 1 WHEN "district"."A9" = 8 THEN 1 ELSE 0 END AS "o6", CASE WHEN "district"."A5" = '98' THEN 3 WHEN "district"."A12" = 7.0 THEN 2 ELSE 0 END AS "o7" FROM "client" AS "client" INNER JOIN "district" AS "district" ON "client"."district_id" = "district"."district_id" ORDER BY CASE WHEN (round("district"."A14", 2) = 104 AND "district"."A6" = '37') THEN 5 WHEN "district"."A12" < 1.7 THEN 5 WHEN "district"."A9" = 5 THEN 1 WHEN "district"."A9" = 8 THEN 1 ELSE 0 END DESC
```

- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)

## financial-13 (attempt 159)

```sql
SELECT "trans"."account_id" AS "o0", ("trans"."account" / "trans"."amount") AS "o1", round("trans"."account", 2) AS "o2", CAST("trans"."balance" AS REAL) AS "o3" FROM "trans" AS "trans" INNER JOIN "account" AS "account" ON "trans"."account_id" = "account"."account_id" WHERE ("trans"."account" / "trans"."amount") > 13965.57 ORDER BY round("trans"."account", 2) DESC LIMIT 10
```

- `/` column/column: unknown

## financial-14 (attempt 69)

```sql
SELECT "account"."frequency" AS "o0", "district"."A10" AS "o1", ((((("district"."A9" / 6) + 1.0) * 0.1) / CAST("district"."A13" AS REAL)) * ("district"."A12" * ("district"."A8" / 2))) AS "o2", "district"."A16" AS "o3", (((("district"."A10" * 0.25) + (round(CAST(("district"."A10" * 0.25) AS REAL), 2) / 0.1)) * (("order"."amount" * 0.1) + "district"."A11")) + (1 - (1 - (("district"."A15" / 2985) + (CASE WHEN ((("district"."A10" * 0.25) + (round(CAST(("district"."A10" * 0.25) AS REAL), 2) / 0.1)) * (("order"."amount" * 0.1) + "district"."A11")) > "account"."date" THEN 3 ELSE 0 END / 0.75))))) AS "o4", "district"."A14" AS "o5", CASE WHEN (("district"."A15" / 2985) + (CASE WHEN ((("district"."A10" * 0.25) + (round(CAST(("district"."A10" * 0.25) AS REAL), 2) / 0.1)) * (("order"."amount" * 0.1) + "district"."A11")) > "account"."date" THEN 3 ELSE 0 END / 0.75)) > "client"."birth_date" THEN 1 ELSE 0 END AS "o6" FROM "client" AS "client" INNER JOIN "disp" AS "disp" ON "client"."client_id" = "disp"."client_id" INNER JOIN "card" AS "card" ON "disp"."disp_id" = "card"."disp_id" LEFT JOIN "district" AS "district" ON "client"."district_id" = "district"."district_id" INNER JOIN "account" AS "account" ON "disp"."account_id" = "account"."account_id" INNER JOIN "order" AS "order" ON "account"."account_id" = "order"."account_id" WHERE "order"."bank_to" = 'ST'
```

- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` column/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)

## financial-15 (attempt 18)

```sql
SELECT "disp"."account_id" AS "o0", "disp"."disp_id" AS "o1", "disp"."client_id" AS "o2", 1 AS "o3", CASE WHEN "disp"."disp_id" = 47 THEN 10 ELSE 0 END AS "o4", round(CASE WHEN "disp"."disp_id" = 47 THEN 10 ELSE 0 END, 2) AS "o5", "disp"."type" AS "o6" FROM "disp" AS "disp"
```


## financial-16 (attempt 124)

```sql
SELECT "district"."district_id" AS "o0", round(((((("district"."A15" * 0.2) + 597.0) * 3) * (("district"."A8" / 2) * "district"."A14")) + ((((CASE WHEN "district"."A14" BETWEEN 126 AND 113 THEN 2 WHEN "district"."district_id" = 23 THEN 10 ELSE 1 END / 0.25) * 10) + (CAST("district"."A12" AS REAL) / 2.8)) * ("district"."A11" * 0.5)))) AS "o1", (CASE WHEN "district"."A14" BETWEEN 126 AND 113 THEN 2 WHEN "district"."district_id" = 23 THEN 10 ELSE 1 END / 0.25) AS "o2" FROM "district" AS "district" INNER JOIN "client" AS "client" ON "district"."district_id" = "client"."district_id" INNER JOIN "account" AS "account" ON "district"."district_id" = "account"."district_id" WHERE "district"."A3" > "client"."gender" ORDER BY "district"."district_id" DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## financial-17 (attempt 12)

```sql
SELECT "disp"."disp_id" AS "o0", "disp"."account_id" AS "o1", "disp"."type" AS "o2", "card"."type" AS "o3", "card"."issued" AS "o4", RANK() OVER (ORDER BY "disp"."account_id" DESC) AS "o5", RANK() OVER (ORDER BY "card"."issued" DESC) AS "o6" FROM "card" AS "card" INNER JOIN "disp" AS "disp" ON "card"."disp_id" = "disp"."disp_id" ORDER BY "disp"."type" DESC
```


## financial-18 (attempt 113)

```sql
SELECT "order"."amount" AS "o0", "order"."k_symbol" AS "o1", "order"."bank_to" AS "o2" FROM "order" AS "order" ORDER BY "order"."k_symbol" DESC
```


## financial-19 (attempt 171)

```sql
SELECT "disp"."disp_id" AS "o0", CASE WHEN "disp"."type" = 'DISPONENT' THEN 5 WHEN "disp"."type" > 'OWNER' THEN 0 WHEN (("district"."A16" * "district"."A10") * ("district"."A16" * "district"."A10")) = 33048331264.0 THEN 1 ELSE 1 END AS "o1", "disp"."type" AS "o2" FROM "disp" AS "disp" INNER JOIN "client" AS "client" ON "disp"."client_id" = "client"."client_id" INNER JOIN "district" AS "district" ON "client"."district_id" = "district"."district_id" INNER JOIN "card" AS "card" ON "disp"."disp_id" = "card"."disp_id" INNER JOIN "account" AS "account" ON "disp"."account_id" = "account"."account_id" WHERE ((("district"."A16" * "district"."A10") * ("district"."A16" * "district"."A10")) = 33048331264.0 AND NOT ((("district"."A16" * "district"."A10") * ("district"."A16" * "district"."A10")) IS NULL) AND CASE WHEN "disp"."type" = 'DISPONENT' THEN 5 WHEN "disp"."type" > 'OWNER' THEN 0 WHEN (("district"."A16" * "district"."A10") * ("district"."A16" * "district"."A10")) = 33048331264.0 THEN 1 ELSE 1 END = "district"."A10") ORDER BY "disp"."type" DESC
```

- `*` derived/derived: unknown
- `*` column/column: unknown

## financial-20 (attempt 177)

```sql
SELECT "order"."account_id" AS "o0", "order"."account_to" AS "o1", "order"."order_id" AS "o2", "order"."k_symbol" AS "o3", round(("order"."amount" * (1 - "order"."amount")), 2) AS "o4", (((1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) + CASE WHEN "order"."account_to" > 24157494 THEN 5 WHEN "order"."bank_to" = 'AB' THEN 10 WHEN ("order"."k_symbol" IN ('UVER', 'SIPO') AND round(("order"."amount" * (1 - "order"."amount")), 2) = -6736620.0 AND (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2)) = 1.0) THEN 2 WHEN "order"."bank_to" > 'CD' THEN 5 ELSE 0 END) * 0.75) AS "o5", CASE WHEN "order"."k_symbol" < '' THEN 1 WHEN (1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) < 0.0 THEN 5 WHEN CASE WHEN "order"."account_to" > 24157494 THEN 5 WHEN "order"."bank_to" = 'AB' THEN 10 WHEN ("order"."k_symbol" IN ('UVER', 'SIPO') AND round(("order"."amount" * (1 - "order"."amount")), 2) = -6736620.0 AND (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2)) = 1.0) THEN 2 WHEN "order"."bank_to" > 'CD' THEN 5 ELSE 0 END = (((1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) + CASE WHEN "order"."account_to" > 24157494 THEN 5 WHEN "order"."bank_to" = 'AB' THEN 10 WHEN ("order"."k_symbol" IN ('UVER', 'SIPO') AND round(("order"."amount" * (1 - "order"."amount")), 2) = -6736620.0 AND (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2)) = 1.0) THEN 2 WHEN "order"."bank_to" > 'CD' THEN 5 ELSE 0 END) / CAST((((((1 - "order"."amount") * 0.2) / 1000) + -0.519) + ((1 - ((((1 - "order"."amount") * 0.2) / 1000) + -0.519)) * 0.75)) AS REAL)) THEN 2 ELSE 0 END AS "o6", NTILE(4) OVER (PARTITION BY (((1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) + CASE WHEN "order"."account_to" > 24157494 THEN 5 WHEN "order"."bank_to" = 'AB' THEN 10 WHEN ("order"."k_symbol" IN ('UVER', 'SIPO') AND round(("order"."amount" * (1 - "order"."amount")), 2) = -6736620.0 AND (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2)) = 1.0) THEN 2 WHEN "order"."bank_to" > 'CD' THEN 5 ELSE 0 END) * 0.75) ORDER BY round(("order"."amount" * (1 - "order"."amount")), 2) DESC) AS "o7", CAST((((1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) + CASE WHEN "order"."account_to" > 24157494 THEN 5 WHEN "order"."bank_to" = 'AB' THEN 10 WHEN ("order"."k_symbol" IN ('UVER', 'SIPO') AND round(("order"."amount" * (1 - "order"."amount")), 2) = -6736620.0 AND (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2)) = 1.0) THEN 2 WHEN "order"."bank_to" > 'CD' THEN 5 ELSE 0 END) / CAST((((((1 - "order"."amount") * 0.2) / 1000) + -0.519) + ((1 - ((((1 - "order"."amount") * 0.2) / 1000) + -0.519)) * 0.75)) AS REAL)) AS REAL) AS "o8", CAST((((1 - "order"."amount") * 0.2) / 1000) AS INTEGER) AS "o9" FROM "order" AS "order" WHERE "order"."k_symbol" IN ((SELECT "trans"."type" AS "o0" FROM "trans" AS "trans")) ORDER BY ((1 - ((((1 - "order"."amount") * 0.2) / 1000) + -0.519)) * 0.75) ASC
```

- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `+` derived/derived: plausible (model)
- `+` case/derived: unknown
- `/` derived/derived: unknown (equal operands)
- `*` column/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

