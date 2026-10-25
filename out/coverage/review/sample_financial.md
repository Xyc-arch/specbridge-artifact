# financial: 20 random delivered programs

## financial-1 (attempt 90)

```sql
SELECT "loan"."loan_id" AS "o0", (((CAST("loan"."payments" AS REAL) * 3) * ("loan"."amount" * 0.2)) * 0.25) AS "o1", "loan"."amount" AS "o2", "loan"."duration" AS "o3", NTILE(10) OVER (PARTITION BY "loan"."amount" ORDER BY "loan"."duration" DESC) AS "o4" FROM "loan" AS "loan" INNER JOIN "account" AS "account" ON "loan"."account_id" = "account"."account_id" ORDER BY "loan"."amount" DESC, "loan"."duration" DESC LIMIT 5
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## financial-2 (attempt 52)

```sql
SELECT "loan"."loan_id" AS "o0", "loan"."amount" AS "o1", CAST("account"."account_id" AS REAL) AS "o2" FROM "loan" AS "loan" LEFT JOIN "account" AS "account" ON "loan"."account_id" = "account"."account_id" ORDER BY "account"."account_id" DESC
```


## financial-3 (attempt 136)

```sql
SELECT "account"."date" AS "o0", "order"."account_to" AS "o1", "order"."k_symbol" AS "o2" FROM "order" AS "order" INNER JOIN "account" AS "account" ON "order"."account_id" = "account"."account_id" ORDER BY "order"."account_to" ASC
```


## financial-4 (attempt 174)

```sql
SELECT "client"."district_id" AS "o0", sqrt("client"."birth_date") AS "o1" FROM "client" AS "client" WHERE (((((((CAST(((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) AS REAL) / round(CAST(0 AS REAL), 3)) * 0.75) + (1 - CASE WHEN round(CAST(0 AS REAL), 3) > ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) THEN 1 WHEN ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) BETWEEN (SELECT "account"."account_id" AS "o0" FROM "account" AS "account") AND round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 WHEN round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) > round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 END)) / 0.5) / 0.75) * (CAST(((CAST(((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) AS REAL) / round(CAST(0 AS REAL), 3)) * 0.75) AS REAL) / ((1 - CASE WHEN round(CAST(0 AS REAL), 3) > ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) THEN 1 WHEN ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) BETWEEN (SELECT "account"."account_id" AS "o0" FROM "account" AS "account") AND round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 WHEN round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) > round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 END) / 0.25))) / 0.25) = "client"."birth_date" ORDER BY (((((((CAST(((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) AS REAL) / round(CAST(0 AS REAL), 3)) * 0.75) + (1 - CASE WHEN round(CAST(0 AS REAL), 3) > ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) THEN 1 WHEN ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) BETWEEN (SELECT "account"."account_id" AS "o0" FROM "account" AS "account") AND round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 WHEN round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) > round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 END)) / 0.5) / 0.75) * (CAST(((CAST(((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) AS REAL) / round(CAST(0 AS REAL), 3)) * 0.75) AS REAL) / ((1 - CASE WHEN round(CAST(0 AS REAL), 3) > ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) THEN 1 WHEN ((round(CAST(0 AS REAL), 3) / 0.75) / 0.2) BETWEEN (SELECT "account"."account_id" AS "o0" FROM "account" AS "account") AND round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 WHEN round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) > round(CAST(round(CAST(0 AS REAL), 3) AS REAL), 0) THEN 1 END) / 0.25))) / 0.25) DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: strong (rule)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown

## financial-5 (attempt 24)

```sql
SELECT "district"."district_id" AS "o0", abs(((round(CAST("trans"."amount" AS REAL), 2) * 0.25) + ("district"."A15" * (CAST("order"."amount" AS REAL) / "district"."A15")))) AS "o1", (abs(((round(CAST("trans"."amount" AS REAL), 2) * 0.25) + ("district"."A15" * (CAST("order"."amount" AS REAL) / "district"."A15")))) * ((("district"."A8" / 2) * 10) * 0.25)) AS "o2", ((("district"."A8" / 2) * 10) * 0.25) AS "o3", coalesce((("trans"."account" * (CAST("trans"."balance" AS REAL) * 0.5)) - ("district"."A14" / "trans"."balance")), 0) AS "o4" FROM "order" AS "order" INNER JOIN "account" AS "account" ON "order"."account_id" = "account"."account_id" INNER JOIN "district" AS "district" ON "account"."district_id" = "district"."district_id" INNER JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" INNER JOIN "trans" AS "trans" ON "account"."account_id" = "trans"."account_id" WHERE NOT ("district"."A12" IS NULL)
```

- `-` derived/derived: unknown
- `/` column/column: unknown
- `*` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` column/derived: unknown
- `/` column/column: unknown
- `*` parameter WEIGHT: unknown (a constant)

## financial-6 (attempt 3)

```sql
SELECT "disp"."client_id" AS "o0", "district"."A5" AS "o1", "district"."A12" AS "o2" FROM "district" AS "district" INNER JOIN "account" AS "account" ON "district"."district_id" = "account"."district_id" INNER JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" LEFT JOIN "trans" AS "trans" ON "account"."account_id" = "trans"."account_id" ORDER BY "disp"."client_id" ASC
```


## financial-7 (attempt 173)

```sql
SELECT "account"."district_id" AS "o0", abs((((1 - ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1)) * 0.1) + ((1 - (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)) + (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) / (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2))))) AS "o1", sqrt((((1 - (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)) + (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) / (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2))) / CAST((((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) / CAST((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) AS REAL)) AS INTEGER))) AS "o2", ((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) AS "o3", (((1 - ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1)) * 0.1) + ((1 - (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)) + (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) / (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)))) AS "o4", ((1 - ((1 - (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)) * 0.2)) * 5) AS "o5", ((1 - (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)) * 0.2) AS "o6" FROM "account" AS "account" WHERE ("account"."frequency" = 'POPLATEK TYDNE' AND NOT ("account"."account_id" IS NULL)) ORDER BY (((1 - ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1)) * 0.1) + ((1 - (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)) + (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) / (CASE WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) = "account"."account_id" THEN 5 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) < "account"."date" THEN 1 WHEN ((CASE WHEN ("account"."district_id" = 28 OR ("account"."account_id" < 1183 AND "account"."account_id" > 3553 AND "account"."account_id" < 2369)) THEN 1 WHEN "account"."district_id" = 15 THEN 1 WHEN "account"."frequency" = 'POPLATEK PO OBRATU' THEN 2 WHEN "account"."frequency" = 'POPLATEK MESICNE' THEN 2 ELSE 0 END * 3) * 0.1) > (((1 - (1 - CASE WHEN "account"."district_id" <= 38 THEN 3 WHEN "account"."date" != '1995-06-13' THEN 3 WHEN "account"."district_id" > 13 THEN 10 WHEN "account"."district_id" = 6 THEN 4 ELSE 0 END)) * 2) - (((CASE WHEN "account"."date" = '1993-08-03' THEN 4 WHEN "account"."account_id" < 1183 THEN 1 ELSE 1 END * 2) + 0) * 5)) THEN 10 ELSE 0 END * 0.2)))) DESC
```

- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `/` derived/derived: unknown

## financial-8 (attempt 100)

```sql
SELECT DISTINCT "account"."account_id" AS "o0", coalesce(((("district"."A12" / 100) * (("district"."A15" * 3) + (round(("district"."A13" / 100), 2) / 1.5))) * ((((100 - "district"."A10") + ("district"."A11" / 1000)) * 0.25) + ("district"."A8" / 2))), 0) AS "o1", CASE WHEN "district"."A11" = 9893 THEN 3 ELSE 0 END AS "o2", ((((100 - "district"."A10") + ("district"."A11" / 1000)) * 0.25) + ("district"."A8" / 2)) AS "o3", (CASE WHEN "district"."A11" = 9893 THEN 3 ELSE 0 END / CAST((("district"."A9" / (((((100 - "district"."A10") + ("district"."A11" / 1000)) * 0.25) + ("district"."A8" / 2)) * 3)) * 0.25) AS REAL)) AS "o4", 1 AS "o5", CASE WHEN (("district"."A9" / (((((100 - "district"."A10") + ("district"."A11" / 1000)) * 0.25) + ("district"."A8" / 2)) * 3)) * 0.25) = 0.04 THEN 10 WHEN ((("district"."A9" / (((((100 - "district"."A10") + ("district"."A11" / 1000)) * 0.25) + ("district"."A8" / 2)) * 3)) * 0.25) < 0.04 AND CASE WHEN "district"."A11" = 9893 THEN 3 ELSE 0 END = "district"."A3") THEN 1 ELSE 0 END AS "o6" FROM "disp" AS "disp" INNER JOIN "card" AS "card" ON "disp"."disp_id" = "card"."disp_id" INNER JOIN "client" AS "client" ON "disp"."client_id" = "client"."client_id" INNER JOIN "district" AS "district" ON "client"."district_id" = "district"."district_id" INNER JOIN "account" AS "account" ON "disp"."account_id" = "account"."account_id" WHERE NOT ("district"."A12" IS NULL)
```

- `*` parameter WEIGHT: unknown (a constant)
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown (disputed (model))
- `/` parameter CONVERT: plausible (model)
- `-` parameter WHOLE: plausible (model)
- `/` case/derived: unknown
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `+` derived/derived: unknown (disputed (model))
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)

## financial-9 (attempt 89)

```sql
SELECT DISTINCT "client"."client_id" AS "o0", "client"."district_id" AS "o1", "client"."gender" AS "o2", "client"."birth_date" AS "o3", log(10, round(CAST("client"."birth_date" AS REAL), 2)) AS "o4" FROM "client" AS "client" ORDER BY "client"."birth_date" DESC LIMIT 10
```


## financial-10 (attempt 78)

```sql
SELECT "trans"."trans_id" AS "o0", ((("trans"."balance" / -692) * 5) + (("trans"."account" / 46100000.0) + "order"."amount")) AS "o1", ("trans"."balance" / -692) AS "o2", "trans"."balance" AS "o3", "trans"."operation" AS "o4", CASE WHEN CAST("order"."amount" AS INTEGER) = 2329.0 THEN 1 WHEN ("trans"."trans_id" > 23696 AND (((("trans"."balance" / -692) * 5) + (("trans"."account" / 46100000.0) + "order"."amount")) * 1.5) > 3523.08) THEN (((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) - (1 - "trans"."amount")) ELSE 0 END AS "o5", CASE WHEN ((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) BETWEEN 5.0 AND 5.0 THEN 1 WHEN ((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) > 5.0 THEN 1 END AS "o6", (((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) - (1 - "trans"."amount")) AS "o7", CAST(((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) AS REAL) AS "o8" FROM "account" AS "account" INNER JOIN "disp" AS "disp" ON "account"."account_id" = "disp"."account_id" LEFT JOIN "order" AS "order" ON "account"."account_id" = "order"."account_id" INNER JOIN "trans" AS "trans" ON "account"."account_id" = "trans"."account_id" WHERE (power("trans"."amount", 2) < (((("trans"."balance" / -692) * 5) + (("trans"."account" / 46100000.0) + "order"."amount")) * 1.5) AND (("trans"."account" / 46100000.0) + "order"."amount") = 2597.0) ORDER BY CASE WHEN ((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) BETWEEN 5.0 AND 5.0 THEN 1 WHEN ((("trans"."balance" / -692) / ("trans"."balance" / -692)) / 0.2) > 5.0 THEN 1 END DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `/` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` column/derived: unknown (disputed (model))
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## financial-11 (attempt 145)

```sql
SELECT "loan"."status" AS "o0", "loan"."payments" AS "o1", "loan"."amount" AS "o2", "loan"."duration" AS "o3", CAST("loan"."duration" AS REAL) AS "o4", AVG("loan"."duration") OVER (PARTITION BY "loan"."duration" ORDER BY "loan"."status" ASC) AS "o5", CASE WHEN AVG("loan"."duration") OVER (PARTITION BY "loan"."duration" ORDER BY "loan"."status" ASC) = (AVG("loan"."duration") OVER (PARTITION BY "loan"."duration" ORDER BY "loan"."status" ASC) * 0.5) THEN 1 ELSE 0 END AS "o6" FROM "loan" AS "loan" ORDER BY CASE WHEN AVG("loan"."duration") OVER (PARTITION BY "loan"."duration" ORDER BY "loan"."status" ASC) = (AVG("loan"."duration") OVER (PARTITION BY "loan"."duration" ORDER BY "loan"."status" ASC) * 0.5) THEN 1 ELSE 0 END DESC, "loan"."amount" DESC
```

- `*` parameter WEIGHT: unknown (a constant)

## financial-12 (attempt 61)

```sql
SELECT "account"."district_id" AS "o0", "account"."frequency" AS "o1", CAST("account"."date" AS REAL) AS "o2" FROM "account" AS "account"
```


## financial-13 (attempt 197)

```sql
WITH "s1" AS (SELECT "account"."account_id" AS "o0", "account"."frequency" AS "o1", "account"."district_id" AS "o2", "account"."date" AS "o3" FROM "account" AS "account" ORDER BY "account"."account_id" DESC LIMIT 5) SELECT "district"."A2" AS "o0", "s1"."o1" AS "o1", "s1"."o2" AS "o2", "s1"."o0" AS "o3", ROW_NUMBER() OVER (ORDER BY "s1"."o0" DESC) AS "o4", CASE WHEN "s1"."o2" BETWEEN 60 AND 38 THEN 5 ELSE 1 END AS "o5", CASE WHEN "district"."A6" = '26' THEN 4 WHEN "district"."A6" < '15' THEN 5 ELSE 0 END AS "o6" FROM "district" AS "district" INNER JOIN "s1" AS "s1" ON "s1"."o2" = "district"."district_id"
```


## financial-14 (attempt 142)

```sql
SELECT CAST("loan"."payments" AS REAL) AS "o0", ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10) AS "o1", "order"."amount" AS "o2", (("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) AS "o3", round((((("order"."amount" * 3) + 7790.0) * (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10))) / ("order"."amount" * (((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 5) + ("order"."amount" / (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10)))))), 3) AS "o4", ("order"."amount" * (((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 5) + ("order"."amount" / (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10))))) AS "o5", (((("order"."amount" * 3) + 7790.0) * (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10))) / ("order"."amount" * (((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 5) + ("order"."amount" / (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10)))))) AS "o6", PERCENT_RANK() OVER (ORDER BY round((((("order"."amount" * 3) + 7790.0) * (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10))) / ("order"."amount" * (((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 5) + ("order"."amount" / (("order"."amount" * 3) / ((("loan"."amount" / 1000) + (CAST("loan"."duration" AS REAL) * 0.5)) * 10)))))), 3) ASC) AS "o7" FROM "order" AS "order" LEFT JOIN "account" AS "account" ON "order"."account_id" = "account"."account_id" INNER JOIN "loan" AS "loan" ON "account"."account_id" = "loan"."account_id"
```

- `/` derived/derived: unknown
- `*` column/derived: unknown
- `+` derived/derived: unknown
- `/` column/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown (disputed (model))
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)

## financial-15 (attempt 67)

```sql
SELECT "order"."bank_to" AS "o0", CAST("order"."account_to" AS REAL) AS "o1", "order"."amount" AS "o2", CAST("order"."account_to" AS REAL) AS "o3", coalesce("order"."order_id", 0) AS "o4" FROM "order" AS "order" ORDER BY coalesce("order"."order_id", 0) DESC
```


## financial-16 (attempt 13)

```sql
SELECT "district"."A7" AS "o0", AVG((("district"."A15" / 2985) * "order"."amount")) FILTER (WHERE "district"."A7" >= '2') AS "o1", AVG((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13"))) AS "o2", AVG(((((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13")) + 388000.0) / 2) / "district"."A12")) AS "o3", round(CAST(AVG(((((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13")) + 388000.0) / 2) / "district"."A12")) AS REAL), 2) AS "o4", AVG(((((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13")) + 388000.0) / 2) / "district"."A12")) FILTER (WHERE (round(CAST("district"."A11" AS REAL), 2) + 8814) > 17628) AS "o5" FROM "order" AS "order" INNER JOIN "account" AS "account" ON "order"."account_id" = "account"."account_id" LEFT JOIN "district" AS "district" ON "account"."district_id" = "district"."district_id" WHERE (((((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13")) + 388000.0) / 2) / "district"."A12") < "account"."date" AND ((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13")) + 388000.0) = 776109.44) GROUP BY "order"."account_id", "district"."A7" ORDER BY round(CAST(AVG(((((((("district"."A15" / 2985) * "order"."amount") + ((round(CAST("district"."A11" AS REAL), 2) + 8814) * 0.2)) * ("district"."A10" + "district"."A13")) + 388000.0) / 2) / "district"."A12")) AS REAL), 2) DESC LIMIT 100
```

- `/` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `+` column/column: plausible (model)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)

## financial-17 (attempt 114)

```sql
SELECT "client"."client_id" AS "o0", round((((CASE WHEN "disp"."type" > 'OWNER' THEN 5 WHEN ("client"."gender" = 'M' AND "client"."client_id" = 39) THEN 4 ELSE 1 END + CASE WHEN "client"."client_id" > 4257 THEN 1 ELSE 0 END) / 0.1) / CAST(((CASE WHEN "disp"."type" > 'OWNER' THEN 5 WHEN ("client"."gender" = 'M' AND "client"."client_id" = 39) THEN 4 ELSE 1 END + CASE WHEN "client"."client_id" > 4257 THEN 1 ELSE 0 END) / 0.1) AS REAL)), 2) AS "o1" FROM "client" AS "client" INNER JOIN "disp" AS "disp" ON "client"."client_id" = "disp"."client_id" ORDER BY round((((CASE WHEN "disp"."type" > 'OWNER' THEN 5 WHEN ("client"."gender" = 'M' AND "client"."client_id" = 39) THEN 4 ELSE 1 END + CASE WHEN "client"."client_id" > 4257 THEN 1 ELSE 0 END) / 0.1) / CAST(((CASE WHEN "disp"."type" > 'OWNER' THEN 5 WHEN ("client"."gender" = 'M' AND "client"."client_id" = 39) THEN 4 ELSE 1 END + CASE WHEN "client"."client_id" > 4257 THEN 1 ELSE 0 END) / 0.1) AS REAL)), 2) DESC
```

- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` case/case: unknown

## financial-18 (attempt 10)

```sql
SELECT SUM(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS "o0", COUNT(*) AS "o1", round(CAST(AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS REAL), 2) AS "o2", CASE WHEN AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) = (((((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * 3) + ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) - (((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))))) + 0) + round(((((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * 3) + ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) - (((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))))) + 0), 1)) THEN 2 ELSE 0 END AS "o3", round(CAST(SUM(CASE WHEN "district"."A10" > 51.9 THEN 10 WHEN ((0.25 / ("district"."A10" + 59.8)) * (("district"."A13" / 100) * ((((100 - "district"."A12") * "district"."A13") * 10) * CAST("district"."A16" AS REAL)))) > 800.49 THEN 3 ELSE 1 END) FILTER (WHERE "account"."account_id" IN ("account"."account_id", "account"."date")) AS REAL), 2) AS "o4", CASE WHEN (round(CAST(AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS REAL), 2) = ((((((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * 3) + ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) - (((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))))) + 0) * ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * 3)) * (0.75 / ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) + (((AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75)) + ((AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75)) * AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END))) + (((CAST(COUNT(*) AS INTEGER) / 0.75) * (CAST(COUNT(*) AS INTEGER) / 0.75)) * ((CAST(COUNT(*) AS INTEGER) / 0.75) * (CAST(COUNT(*) AS INTEGER) / 0.75))))))) AND COUNT(*) > 7) THEN ((((((((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * 3) + ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) - (((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))))) + 0) * ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * 3)) * (0.75 / ((((CAST(COUNT(*) AS INTEGER) / 0.75) / 5) + (AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75))) + (((AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75)) + ((AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75)) * AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END))) + (((CAST(COUNT(*) AS INTEGER) / 0.75) * (CAST(COUNT(*) AS INTEGER) / 0.75)) * ((CAST(COUNT(*) AS INTEGER) / 0.75) * (CAST(COUNT(*) AS INTEGER) / 0.75))))))) * round(CAST(round(CAST(AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS REAL), 2) AS REAL), 0)) * ((round(CAST(round(CAST(AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS REAL), 2) AS REAL), 0) * ((((((CAST(COUNT(*) AS INTEGER) / 0.75) * (CAST(COUNT(*) AS INTEGER) / 0.75)) * ((CAST(COUNT(*) AS INTEGER) / 0.75) * (CAST(COUNT(*) AS INTEGER) / 0.75))) * ((AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75)) + ((AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) * (CAST(COUNT(*) AS INTEGER) / 0.75)) * AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END)))) * round(CAST(round(CAST(AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS REAL), 2) AS REAL), 0)) * 0.1)) + round(CAST(round(CAST(AVG(CASE WHEN "district"."A10" = 55.3 THEN 1 ELSE 1 END) AS REAL), 2) AS REAL), 2))) ELSE 0 END AS "o5" FROM "district" AS "district" INNER JOIN "account" AS "account" ON "district"."district_id" = "account"."district_id" LEFT JOIN "order" AS "order" ON "account"."account_id" = "order"."account_id" ORDER BY round(CAST(SUM(CASE WHEN "district"."A10" > 51.9 THEN 10 WHEN ((0.25 / ("district"."A10" + 59.8)) * (("district"."A13" / 100) * ((((100 - "district"."A12") * "district"."A13") * 10) * CAST("district"."A16" AS REAL)))) > 800.49 THEN 3 ELSE 1 END) FILTER (WHERE "account"."account_id" IN ("account"."account_id", "account"."date")) AS REAL), 2) DESC
```

- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `-` parameter WHOLE: plausible (model)
- `/` parameter CONVERT: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/summary: unknown
- `*` derived/summary: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/summary: unknown
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/summary: unknown
- `*` derived/summary: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` derived/summary: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `+` derived/derived: unknown

## financial-19 (attempt 102)

```sql
SELECT "district"."district_id" AS "o0", "district"."A7" AS "o1", CASE WHEN ((((("district"."A13" / 3.6) * "district"."A11") * round(CAST("district"."A9" AS INTEGER), 2)) / 2) * ((CAST("district"."A15" AS REAL) / (1 - ((("district"."A13" / 3.6) * "district"."A11") * round(CAST("district"."A9" AS INTEGER), 2)))) / 1.5)) < -995.02 THEN 2 WHEN ("district"."A6" = '18' AND "district"."A3" >= 'west Bohemia' AND "district"."A3" > 'central Bohemia' AND ("district"."A16" > 4595 OR (("district"."A13" / 3.6) < 1.0 AND "district"."A7" = '13')) AND "district"."A7" = '2') THEN 1 ELSE 0 END AS "o2", CAST("district"."A3" AS REAL) AS "o3", coalesce(((("district"."A12" / 100) + ("district"."A10" * 2)) / (0 - "district"."A10")), 0) AS "o4" FROM "district" AS "district" WHERE (((((("district"."A13" / 3.6) * "district"."A11") * round(CAST("district"."A9" AS INTEGER), 2)) / 2) * ((CAST("district"."A15" AS REAL) / (1 - ((("district"."A13" / 3.6) * "district"."A11") * round(CAST("district"."A9" AS INTEGER), 2)))) / 1.5)) > -995.02 AND "district"."A16" < 4595 AND "district"."A6" < '49') ORDER BY coalesce(((("district"."A12" / 100) + ("district"."A10" * 2)) / (0 - "district"."A10")), 0) DESC, "district"."district_id" ASC
```

- `/` derived/derived: unknown
- `-` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown (disputed (model))
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter CONVERT: plausible (model)
- `/` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` column/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` column/derived: unknown
- `*` column/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)

## financial-20 (attempt 158)

```sql
SELECT CAST("order"."amount" AS INTEGER) AS "o0", "order"."bank_to" AS "o1", abs((((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) * (1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2)))) + (round(CAST((1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2))) AS REAL), 2) - round(CAST((1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2))) AS REAL), 2)))) AS "o2", (((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) * (1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2)))) + (round(CAST((1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2))) AS REAL), 2) - round(CAST((1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2))) AS REAL), 2))) AS "o3" FROM "order" AS "order" INNER JOIN "account" AS "account" ON "order"."account_id" = "account"."account_id" ORDER BY ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) * (1 - ((((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2) + 0) / ((CASE WHEN "order"."k_symbol" = 'POJISTNE' THEN 1 WHEN ("order"."amount" = 17.0 AND "order"."bank_to" < 'OP') THEN 1 ELSE 0 END * 100) / 0.2)))) DESC LIMIT 100
```

- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter CONVERT: strong (rule)
- `+` parameter ZERO: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `-` derived/derived: unknown (equal operands)

