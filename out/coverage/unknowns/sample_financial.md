# financial: 20 random unknown substantive calculations (of 1593)

## financial-u1 (attempt 175) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - LOG(10, 10))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "disp"."disp_id" AS "o0", (round(((((((1 - (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) * 0.1) * ((CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) + 0)) + ((((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 1.5) / 10)) + 0) * 0.1), 2) * CASE WHEN (CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) > (((1 - (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) * 0.1) * ((CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) + 0)) THEN 5 WHEN ((((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 1.5) / 10) > (CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) THEN 0 ELSE 0 END) AS "o1", round(((((((round(CAST(((CAST(1 
```

## financial-u2 (attempt 56) -- mechanical class: BOTH KNOWN

Node: `("loan"."payments" / "loan"."payments")`

- left operand: unit 'USD', kind 'measure', quantity ('loan.payments', 'value')
- right operand: unit 'USD', kind 'measure', quantity ('loan.payments', 'value')
- stored columns under it: loan.payments [unit 'USD' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s9" AS (SELECT "loan"."status" AS "o0", AVG(("loan"."payments" / "loan"."payments")) AS "o1", coalesce(AVG(("loan"."payments" / "loan"."payments")), 0) AS "o2", (CAST(SUM(CASE WHEN "loan"."date" = '1998-04-16' THEN 3 WHEN ((("loan"."amount" / 117024) / 0.5) / (("loan"."amount" + (("loan"."amount" / 117024) / 0.5)) / 2)) > 0.0 THEN 0 WHEN ((CAST("loan"."payments" AS REAL) * 3) * 0.25) > 2952.75 THEN 3 END) AS REAL) / SUM(CASE WHEN "loan"."date" = '1998-04-16' THEN 3 WHEN ((("loan"."amount" / 117024) / 0.5) / (("loan"."amount" + (("loan"."amount" / 117024) / 0.5)) / 2)) > 0.0 THEN 0 WHEN ((CAST("loan"."payments" AS REAL) * 3) * 0.25) > 2952.75 THEN 3 END)) AS "o3", (MAX("loan"."duration") / SUM(("loan"."amount" / 117024))) AS "o4" FROM "loan" AS "loan" WHERE (((("loan"."amount" / 117024) / 0.5) / (("loan"."amount" + (("loan"."amount" / 117024) / 0.5)) / 2)) > "loan"."date" OR ("loan"
```

## financial-u3 (attempt 187) -- mechanical class: BOTH KNOWN

Node: `("trans"."balance" - "trans"."balance")`

- left operand: unit 'USD', kind 'measure', quantity ('trans.balance', 'value')
- right operand: unit 'USD', kind 'measure', quantity ('trans.balance', 'value')
- stored columns under it: trans.balance [unit 'USD' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "trans"."trans_id" AS "o0", exp(("trans"."balance" - "trans"."balance")) AS "o1", "trans"."amount" AS "o2", coalesce((exp(("trans"."balance" - "trans"."balance")) / CAST((1 - ("trans"."balance" - "trans"."balance")) AS REAL)), 0) AS "o3", CASE WHEN coalesce((exp(("trans"."balance" - "trans"."balance")) / CAST((1 - ("trans"."balance" - "trans"."balance")) AS REAL)), 0) != "trans"."amount" THEN 2 ELSE 0 END AS "o4" FROM "trans" AS "trans" INNER JOIN "account" AS "account" ON "trans"."account_id" = "account"."account_id" WHERE ("trans"."balance" = 23665 OR "trans"."amount" < 9226)
```

## financial-u4 (attempt 77) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - ((ROUND(2, 2) / 3) * 0.25))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "card"."issued" AS "o0", (1 - ((CAST((((CAST((1 - ((round(2, 2) / 3) * 0.25)) AS REAL) * 1.5) + (CAST((round(2, 2) / 3) AS REAL) * 3)) * 10) AS REAL) / (((CAST((1 - ((round(2, 2) / 3) * 0.25)) AS REAL) * 1.5) + (CAST((round(2, 2) / 3) AS REAL) * 3)) * 10)) * ((((round(2, 2) / 3) * 0.25) / (((CAST((1 - ((round(2, 2) / 3) * 0.25)) AS REAL) * 1.5) + (CAST((round(2, 2) / 3) AS REAL) * 3)) * 10)) + 0))) AS "o1", coalesce(("card"."issued" - "card"."issued"), 0) AS "o2", "card"."type" AS "o3", (CAST((1 - ((round(2, 2) / 3) * 0.25)) AS REAL) * 1.5) AS "o4" FROM "card" AS "card" INNER JOIN "disp" AS "disp" ON "card"."disp_id" = "disp"."disp_id" ORDER BY (CAST((1 - ((round(2, 2) / 3) * 0.25)) AS REAL) * 1.5) DESC
```

## financial-u5 (attempt 177) -- mechanical class: BOTH KNOWN

Node: `(ROUND(("order"."amount" * (1 - "order"."amount")), 2) / ROUND(("order"."amount" * (1 - "order"."amount")), 2))`

- left operand: unit 'USD × USD', kind '', quantity ()
- right operand: unit 'USD × USD', kind '', quantity ()
- stored columns under it: order.amount [unit 'USD' (model), kind 'money', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "order"."account_id" AS "o0", "order"."account_to" AS "o1", "order"."order_id" AS "o2", "order"."k_symbol" AS "o3", round(("order"."amount" * (1 - "order"."amount")), 2) AS "o4", (((1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) + CASE WHEN "order"."account_to" > 24157494 THEN 5 WHEN "order"."bank_to" = 'AB' THEN 10 WHEN ("order"."k_symbol" IN ('UVER', 'SIPO') AND round(("order"."amount" * (1 - "order"."amount")), 2) = -6736620.0 AND (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2)) = 1.0) THEN 2 WHEN "order"."bank_to" > 'CD' THEN 5 ELSE 0 END) * 0.75) AS "o5", CASE WHEN "order"."k_symbol" < '' THEN 1 WHEN (1.0 - (round(("order"."amount" * (1 - "order"."amount")), 2) / round(("order"."amount" * (1 - "order"."amount")), 2))) < 0.0 THEN 5 WHEN CASE WH
```

## financial-u6 (attempt 187) -- mechanical class: BOTH KNOWN

Node: `("trans"."balance" - "trans"."balance")`

- left operand: unit 'USD', kind 'measure', quantity ('trans.balance', 'value')
- right operand: unit 'USD', kind 'measure', quantity ('trans.balance', 'value')
- stored columns under it: trans.balance [unit 'USD' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "trans"."trans_id" AS "o0", exp(("trans"."balance" - "trans"."balance")) AS "o1", "trans"."amount" AS "o2", coalesce((exp(("trans"."balance" - "trans"."balance")) / CAST((1 - ("trans"."balance" - "trans"."balance")) AS REAL)), 0) AS "o3", CASE WHEN coalesce((exp(("trans"."balance" - "trans"."balance")) / CAST((1 - ("trans"."balance" - "trans"."balance")) AS REAL)), 0) != "trans"."amount" THEN 2 ELSE 0 END AS "o4" FROM "trans" AS "trans" INNER JOIN "account" AS "account" ON "trans"."account_id" = "account"."account_id" WHERE ("trans"."balance" = 23665 OR "trans"."amount" < 9226)
```

## financial-u7 (attempt 175) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - (LOG(10, 10) / 3))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "disp"."disp_id" AS "o0", (round(((((((1 - (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) * 0.1) * ((CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) + 0)) + ((((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 1.5) / 10)) + 0) * 0.1), 2) * CASE WHEN (CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) > (((1 - (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) * 0.1) * ((CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) + 0)) THEN 5 WHEN ((((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 1.5) / 10) > (CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) THEN 0 ELSE 0 END) AS "o1", round(((((((round(CAST(((CAST(1 
```

## financial-u8 (attempt 164) -- mechanical class: BOTH KNOWN

Node: `("order"."amount" / "order"."amount")`

- left operand: unit 'USD', kind 'money', quantity ('order.amount', 'value')
- right operand: unit 'USD', kind 'money', quantity ('order.amount', 'value')
- stored columns under it: order.amount [unit 'USD' (model), kind 'money', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "order"."account_to" AS "o0", "order"."amount" AS "o1", round((((("loan"."duration" * 0.1) * 1.5) * ("order"."amount" / "order"."amount")) * (((CASE WHEN "order"."amount" > 2596.0 THEN 1 WHEN "loan"."payments" > 5814.0 THEN 3 WHEN ("order"."amount" / "order"."amount") > 1.0 THEN 5 ELSE 0 END * 0.1) * 1.5) + ((CASE WHEN ((CASE WHEN "order"."amount" > 2596.0 THEN 1 WHEN "loan"."payments" > 5814.0 THEN 3 WHEN ("order"."amount" / "order"."amount") > 1.0 THEN 5 ELSE 0 END * 0.1) * 1.5) = "account"."frequency" THEN 1 WHEN ("order"."amount" / "order"."amount") BETWEEN 1.0 AND 1.0 THEN 4 ELSE 0 END * 0.25) * 0.5))), 2) AS "o2", (((("loan"."duration" * 0.1) * 1.5) * ("order"."amount" / "order"."amount")) * (((CASE WHEN "order"."amount" > 2596.0 THEN 1 WHEN "loan"."payments" > 5814.0 THEN 3 WHEN ("order"."amount" / "order"."amount") > 1.0 THEN 5 ELSE 0 END * 0.1) * 1.5) + ((CASE WHEN ((CASE
```

## financial-u9 (attempt 31) -- mechanical class: BOTH KNOWN

Node: `("loan"."payments" * "loan"."amount")`

- left operand: unit 'USD', kind 'measure', quantity ('loan.payments', 'value')
- right operand: unit 'USD', kind 'money', quantity ('loan.amount', 'value')
- stored columns under it: loan.amount [unit 'USD' (model), kind 'money', scale 'ratio']; loan.payments [unit 'USD' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: loan.payments part_of loan.amount; loan.amount comparable loan.payments

Whole query:
```sql
SELECT "loan"."loan_id" AS "o0", SUM(CASE WHEN ((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) + CASE WHEN ((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) > "loan"."loan_id" AND "loan"."loan_id" > 6753) THEN (((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) / (CAST(round(CAST(("loan"."duration" * 0.2) AS REAL), 1) AS REAL) * 0.5)) + ((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) / (((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) * round(CAST((("loan"."payments" * "loan"."amount") + ("loan"."duration" * 0.2)) AS REAL), 2)))) + abs(((((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) * round(CAST((("loan"."payments" * "loan"."amount") + ("loan"."duration" * 0.2)) AS REAL), 2)) + (((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) / ((CAST(("loan"."duration" * 0.2) AS REAL) / 2) - ((CAST("loan"."duration" AS REAL) * 2) * (117.0 - ("loan"."amount" / 1000)
```

## financial-u10 (attempt 122) -- mechanical class: NO UNIT

Node: `((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) - ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / C`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: disp.client_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "disp"."account_id" AS "o0", "disp"."type" AS "o1", "disp"."client_id" AS "o2", ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) - ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) / CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END)) AS "o3", (((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) - ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 
```

## financial-u11 (attempt 199) -- mechanical class: BOTH KNOWN

Node: `((("loan"."payments" * 5) * "loan"."duration") / CAST(("loan"."amount" * 2) AS REAL))`

- left operand: unit 'USD × months', kind '', quantity ()
- right operand: unit 'USD', kind '', quantity ()
- stored columns under it: loan.amount [unit 'USD' (model), kind 'money', scale 'ratio']; loan.duration [unit 'months' (model), kind 'measure', scale 'ratio']; loan.payments [unit 'USD' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: loan.payments part_of loan.amount; loan.amount comparable loan.duration; loan.amount comparable loan.payments; loan.duration comparable loan.payments

Whole query:
```sql
WITH "s15" AS (SELECT "loan"."account_id" AS "o0", round((((("loan"."payments" * 5) * "loan"."duration") / CAST(("loan"."amount" * 2) AS REAL)) / CAST(("loan"."amount" * 2) AS REAL)), 2) AS "o1", coalesce((((round((((("loan"."payments" * 5) * "loan"."duration") / CAST(("loan"."amount" * 2) AS REAL)) / CAST(("loan"."amount" * 2) AS REAL)), 2) * 0.1) + (1 - CASE WHEN (CAST((("loan"."payments" * 5) * "loan"."duration") AS REAL) < "account"."frequency" AND round((((("loan"."payments" * 5) * "loan"."duration") / CAST(("loan"."amount" * 2) AS REAL)) / CAST(("loan"."amount" * 2) AS REAL)), 2) > (((CAST((("loan"."payments" * 5) * "loan"."duration") AS REAL) / ((("loan"."payments" * 5) * "loan"."duration") / CAST(("loan"."amount" * 2) AS REAL))) + 0) / 0.2) AND round((((("loan"."payments" * 5) * "loan"."duration") / CAST(("loan"."amount" * 2) AS REAL)) / CAST(("loan"."amount" * 2) AS REAL)), 2) =
```

## financial-u12 (attempt 51) -- mechanical class: SCORE

Node: `(((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" THEN 3 ELSE 0 END * 1.5) / 3) / CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" THEN 3 ELSE 0 END)`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: client.client_id [unit '' (-), kind '', scale '']; client.district_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "client"."client_id" AS "o0", round((((CAST(round(CAST(((CASE WHEN ("client"."gender" > 'F' OR "client"."district_id" LIKE CAST("client"."district_id" AS REAL)) THEN 1 WHEN "client"."gender" BETWEEN 'M' AND CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END THEN 1 WHEN "client"."client_id" = 25 THEN 5 ELSE 0 END / 1.5) / 0.1) AS REAL), 2) AS INTEGER) / round(CAST(((CASE WHEN ("client"."gender" > 'F' OR "client"."district_id" LIKE CAST("client"."district_id" AS REAL)) THEN 1 WHEN "client"."gender" BETWEEN 'M' AND CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END THEN 1 WHEN "client"."client_id" = 25 THEN 5 ELSE 0 END / 1.5) / 0.1) AS REAL), 2)) * 2) + ((((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" THEN 3 ELSE 0 END * 1.5) / 3) + (CAST(((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" T
```

## financial-u13 (attempt 175) -- mechanical class: NO UNIT

Node: `((CAST(2 AS REAL) / 0.25) * (1 - LOG(10, 10)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "disp"."disp_id" AS "o0", (round(((((((1 - (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) * 0.1) * ((CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) + 0)) + ((((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 1.5) / 10)) + 0) * 0.1), 2) * CASE WHEN (CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) > (((1 - (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) * 0.1) * ((CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) + 0)) THEN 5 WHEN ((((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 1.5) / 10) > (CAST(((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) AS REAL) / (((CAST(2 AS REAL) / 0.25) * (1 - log(10, 10))) * 5)) THEN 0 ELSE 0 END) AS "o1", round(((((((round(CAST(((CAST(1 
```

## financial-u14 (attempt 31) -- mechanical class: LOST

Node: `((ROUND(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) / (((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) * ROUND(CAST((("loan"."payments" * "loan"."amount") + ("loan"."duration" * 0.2)) AS REAL), 2)))`

- left operand: unit 'months', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: loan.amount [unit 'USD' (model), kind 'money', scale 'ratio']; loan.duration [unit 'months' (model), kind 'measure', scale 'ratio']; loan.payments [unit 'USD' (model), kind 'measure', scale 'ratio']
- catalogue relations among them: loan.payments part_of loan.amount; loan.amount comparable loan.duration; loan.amount comparable loan.payments; loan.duration comparable loan.payments

Whole query:
```sql
SELECT "loan"."loan_id" AS "o0", SUM(CASE WHEN ((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) + CASE WHEN ((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) > "loan"."loan_id" AND "loan"."loan_id" > 6753) THEN (((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) / (CAST(round(CAST(("loan"."duration" * 0.2) AS REAL), 1) AS REAL) * 0.5)) + ((round(CAST(("loan"."duration" * 0.2) AS REAL), 1) + 0) / (((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) * round(CAST((("loan"."payments" * "loan"."amount") + ("loan"."duration" * 0.2)) AS REAL), 2)))) + abs(((((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) * round(CAST((("loan"."payments" * "loan"."amount") + ("loan"."duration" * 0.2)) AS REAL), 2)) + (((CAST(("loan"."duration" * 0.2) AS REAL) / 2) + 0) / ((CAST(("loan"."duration" * 0.2) AS REAL) / 2) - ((CAST("loan"."duration" AS REAL) * 2) * (117.0 - ("loan"."amount" / 1000)
```

## financial-u15 (attempt 32) -- mechanical class: BOTH KNOWN

Node: `(CAST("s1"."o1" AS REAL) / "s1"."o1")`

- left operand: unit 'rows', kind 'count', quantity ()
- right operand: unit 'rows', kind 'count', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "trans"."bank" AS "o0", coalesce(COUNT(*), 1) AS "o1" FROM "trans" AS "trans" WHERE "trans"."bank" = "trans"."operation" GROUP BY "trans"."bank") SELECT CAST(AVG(CASE WHEN ((CASE WHEN ("s1"."o0" > 'YZ' AND (log(10, (CAST("s1"."o1" AS REAL) / "s1"."o1")) / 0.2) < 50.0) THEN 0 ELSE 0 END + ((1 - ((coalesce(CAST("s1"."o1" AS REAL), 0) / (CAST("s1"."o1" AS REAL) / "s1"."o1")) / 5)) + 0)) + (((CASE WHEN (coalesce(CAST("s1"."o1" AS REAL), 0) = (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5)) AND (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5)) > (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5))) THEN 4 WHEN (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5)) < (((1 - "s1"."o1") * 0.5) + (("s1"."o1" * 5) * 0.2)) THEN 0 ELSE 0 END / 2) * (1 - (((((1 - "s1"."o1") * 0.5) + (("s1"."o1" * 5) * 0.2)) / 1.5) * 2))) * 1.5)) = ((CASE WHEN ("s1"."o0" > 'YZ' AND (log(10, (CAST("s1"."o1" AS REAL) / "s1"."o1")) / 0.2) < 50.0)
```

## financial-u16 (attempt 32) -- mechanical class: BOTH KNOWN

Node: `(CAST("s1"."o1" AS REAL) / "s1"."o1")`

- left operand: unit 'rows', kind 'count', quantity ()
- right operand: unit 'rows', kind 'count', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "trans"."bank" AS "o0", coalesce(COUNT(*), 1) AS "o1" FROM "trans" AS "trans" WHERE "trans"."bank" = "trans"."operation" GROUP BY "trans"."bank") SELECT CAST(AVG(CASE WHEN ((CASE WHEN ("s1"."o0" > 'YZ' AND (log(10, (CAST("s1"."o1" AS REAL) / "s1"."o1")) / 0.2) < 50.0) THEN 0 ELSE 0 END + ((1 - ((coalesce(CAST("s1"."o1" AS REAL), 0) / (CAST("s1"."o1" AS REAL) / "s1"."o1")) / 5)) + 0)) + (((CASE WHEN (coalesce(CAST("s1"."o1" AS REAL), 0) = (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5)) AND (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5)) > (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5))) THEN 4 WHEN (("s1"."o1" * 0.1) - ("s1"."o1" * 1.5)) < (((1 - "s1"."o1") * 0.5) + (("s1"."o1" * 5) * 0.2)) THEN 0 ELSE 0 END / 2) * (1 - (((((1 - "s1"."o1") * 0.5) + (("s1"."o1" * 5) * 0.2)) / 1.5) * 2))) * 1.5)) = ((CASE WHEN ("s1"."o0" > 'YZ' AND (log(10, (CAST("s1"."o1" AS REAL) / "s1"."o1")) / 0.2) < 50.0)
```

## financial-u17 (attempt 89) -- mechanical class: BOTH KNOWN

Node: `((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5))`

- left operand: unit 'USD', kind '', quantity ()
- right operand: unit 'thousand USD', kind '', quantity ()
- stored columns under it: order.amount [unit 'USD' (model), kind 'money', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s19" AS (SELECT "order"."account_id" AS "o0", COUNT(*) AS "o1", round(CAST(SUM(CASE WHEN (CAST(("order"."amount" / 1000) AS REAL) / ((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5))) > "order"."k_symbol" THEN 1 ELSE 5 END) AS REAL), 2) AS "o2", round(CAST(AVG((CAST(("order"."amount" / 1000) AS REAL) / ((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5)))) AS REAL), 2) AS "o3" FROM "order" AS "order" WHERE (("order"."amount" / ((((((CAST("order"."amount" AS REAL) / 2007.0) * 10) - (((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5)) / 3)) + (CASE WHEN power(CAST(("order"."amount" / 1000) AS REAL), 1.5) != power(CAST(("order"."amount" / 1000) AS REAL), 1.5) THEN 1 WHEN power(CAST(("order"."amount" / 1000) AS REAL), 1.5) < power(CAST(("order"."amount" / 
```

## financial-u18 (attempt 122) -- mechanical class: WHOLE of SCORE

Node: `(1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END)`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: disp.client_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "disp"."account_id" AS "o0", "disp"."type" AS "o1", "disp"."client_id" AS "o2", ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) - ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) / CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END)) AS "o3", (((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS REAL)) - ((CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 THEN 2 ELSE 0 END) AS REAL) * 2) AS INTEGER) / CAST((CAST((1 - CASE WHEN "disp"."client_id" < 1418 
```

## financial-u19 (attempt 51) -- mechanical class: NO UNIT

Node: `(((((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" THEN 3 ELSE 0 END * 1.5) / 3) + (CAST(((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" THEN 3 ELSE 0 END * 1.5) / 3) AS REAL) / (CASE WHEN CASE WHEN "client"."distr`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: client.client_id [unit '' (-), kind '', scale '']; client.district_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "client"."client_id" AS "o0", round((((CAST(round(CAST(((CASE WHEN ("client"."gender" > 'F' OR "client"."district_id" LIKE CAST("client"."district_id" AS REAL)) THEN 1 WHEN "client"."gender" BETWEEN 'M' AND CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END THEN 1 WHEN "client"."client_id" = 25 THEN 5 ELSE 0 END / 1.5) / 0.1) AS REAL), 2) AS INTEGER) / round(CAST(((CASE WHEN ("client"."gender" > 'F' OR "client"."district_id" LIKE CAST("client"."district_id" AS REAL)) THEN 1 WHEN "client"."gender" BETWEEN 'M' AND CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END THEN 1 WHEN "client"."client_id" = 25 THEN 5 ELSE 0 END / 1.5) / 0.1) AS REAL), 2)) * 2) + ((((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" THEN 3 ELSE 0 END * 1.5) / 3) + (CAST(((CASE WHEN CASE WHEN "client"."district_id" = 43 THEN 2 ELSE 0 END > "client"."client_id" T
```

## financial-u20 (attempt 89) -- mechanical class: LOST

Node: `(CAST(((((CAST("order"."amount" AS REAL) / 2007.0) * 10) - (((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5)) / 3)) + (CASE WHEN POWER(CAST(("order"."amount" / 1000) AS REAL), 1.5) != POWER(CAST(("order"."amount" / 1000) AS REAL), 1.5) THEN 1 WHEN POWER(`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'USD', kind '', quantity ()
- stored columns under it: order.amount [unit 'USD' (model), kind 'money', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s19" AS (SELECT "order"."account_id" AS "o0", COUNT(*) AS "o1", round(CAST(SUM(CASE WHEN (CAST(("order"."amount" / 1000) AS REAL) / ((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5))) > "order"."k_symbol" THEN 1 ELSE 5 END) AS REAL), 2) AS "o2", round(CAST(AVG((CAST(("order"."amount" / 1000) AS REAL) / ((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5)))) AS REAL), 2) AS "o3" FROM "order" AS "order" WHERE (("order"."amount" / ((((((CAST("order"."amount" AS REAL) / 2007.0) * 10) - (((((CAST("order"."amount" AS REAL) / 2007.0) / 0.75) / 0.75) * (("order"."amount" / 1000) * 5)) / 3)) + (CASE WHEN power(CAST(("order"."amount" / 1000) AS REAL), 1.5) != power(CAST(("order"."amount" / 1000) AS REAL), 1.5) THEN 1 WHEN power(CAST(("order"."amount" / 1000) AS REAL), 1.5) < power(CAST(("order"."amount" / 
```

