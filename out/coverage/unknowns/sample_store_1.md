# store_1: 20 random unknown substantive calculations (of 2184)

## store_1-u1 (attempt 62) -- mechanical class: NO UNIT

Node: `((1 - CASE WHEN "s6"."o0" > '700 W Pender Street' THEN 10 ELSE 2 END) + ((1 - CASE WHEN "s6"."o0" > 'Av. Paulista, 2022' THEN 4 ELSE 0 END) * ROUND((CAST("s6"."o2" AS REAL) / "s6"."o1"), 2)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s6" AS (SELECT "invoices"."billing_address" AS "o0", AVG((((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3))) AS "o1", round(CAST(COUNT(*) AS REAL), 2) AS "o2", round(CAST(COUNT(*) AS INTEGER), 2) AS "o3" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" WHERE ("tracks"."unit_price" > 0.99 OR (((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3)) > -4555391.94) GROUP BY "invoices"."billing_address") SELECT "s6"."o0" AS "o0", ((1 - (((CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 WHEN "s6"."o0" >= 'Rotenturmstraße 4, 1010 Innere Stadt' THEN 4 ELSE 1 END * 0.75) + (CASE WHEN CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 W
```

## store_1-u2 (attempt 135) -- mechanical class: LOST

Node: `((((CAST("tracks"."bytes" AS REAL) / 8107896) * (1 - (1 - ("tracks"."milliseconds" / 255634)))) + (ROUND((CAST("tracks"."bytes" AS REAL) * 0.25), 2) * ROUND((CAST("tracks"."bytes" AS REAL) * 0.25), 2))) + ((("tracks"."milliseconds" / "tracks"."milliseconds") * 5) / COALESCE(CAST("tracks"."bytes" AS `

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: tracks.bytes [unit 'bytes' (model), kind '', scale 'ratio']; tracks.milliseconds [unit 'ms' (model), kind '', scale 'ratio']
- catalogue relations among them: tracks.bytes rate tracks.milliseconds

Whole query:
```sql
SELECT DISTINCT "tracks"."bytes" AS "o0", AVG(((("tracks"."bytes" + 8107896) + (("tracks"."milliseconds" / "tracks"."milliseconds") * 5)) * coalesce(CAST("tracks"."bytes" AS REAL), 0))) AS "o1", round(CAST(COUNT(*) AS REAL), 1) AS "o2", AVG(CASE WHEN (("tracks"."milliseconds" / "tracks"."milliseconds") = 1.0 AND CASE WHEN ("tracks"."milliseconds" / "tracks"."milliseconds") BETWEEN 1.0 AND 1.0 THEN 3 WHEN (((("tracks"."bytes" + 8107896) + (("tracks"."milliseconds" / "tracks"."milliseconds") * 5)) * coalesce(CAST("tracks"."bytes" AS REAL), 0)) > 131475995633112.0 OR "tracks"."milliseconds" = 261433) THEN 1 WHEN (((("tracks"."bytes" + 8107896) + (("tracks"."milliseconds" / "tracks"."milliseconds") * 5)) * coalesce(CAST("tracks"."bytes" AS REAL), 0)) > 131475995633112.0 AND "tracks"."name" LIKE 'The Wizard' AND coalesce(CAST("tracks"."bytes" AS REAL), 0) > 8107896) THEN 4 WHEN coalesce(CAST(
```

## store_1-u3 (attempt 197) -- mechanical class: NO UNIT

Node: `(((((CASE WHEN (CAST("s1"."o1" AS REAL) / (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96))) = 0.44 THEN 3 WHEN (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96)) = 8.92 THEN 4 ELSE 0 END / 10) * (CASE WHEN "s1"."o0" > '10789' THEN 1 WHEN (CAST("s1"."o1" AS REAL) / (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "customers"."postal_code" AS "o0", "invoices"."total" AS "o1" FROM "customers" AS "customers" INNER JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" ORDER BY "customers"."postal_code" ASC LIMIT 100) SELECT round(AVG(CASE WHEN ((((CASE WHEN (CAST("s1"."o1" AS REAL) / (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96))) = 0.44 THEN 3 WHEN (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96)) = 8.92 THEN 4 ELSE 0 END / 10) * (CASE WHEN "s1"."o0" > '10789' THEN 1 WHEN (CAST("s1"."o1" AS REAL) / (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96))) > 0.44 THEN 3 WHEN "s1"."o1" = 7.96 THEN 1 WHEN (CAST("s1"."o1" AS REAL) / (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96))) = 0.44 THEN 0 ELSE 0 END / 0.1)) / 3) / 1.5) > ((coalesce(CAST(CASE WHEN "s1"."o0" > '10789' THEN 1 WHEN (CAST("s1"."o1" AS REAL) / (("s1"."o1" + "s1"."o1") + ("s1"."o1" / 3.96))) > 0.44 THEN 3 WH
```

## store_1-u4 (attempt 1) -- mechanical class: NO UNIT

Node: `(((CASE WHEN (CAST(COALESCE(CAST(ROUND(1, 2) AS REAL), 0) AS REAL) / CAST(COALESCE(CAST(ROUND(1, 2) AS REAL), 0) AS REAL)) = (CAST(COALESCE(CAST(ROUND(1, 2) AS REAL), 0) AS REAL) / CAST(COALESCE(CAST(ROUND(1, 2) AS REAL), 0) AS REAL)) THEN 1 ELSE 1 END + CASE WHEN COALESCE(CAST(ROUND(1, 2) AS REAL),`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "genres"."id" AS "o0", coalesce((((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) + (((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1))) - ((((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0
```

## store_1-u5 (attempt 159) -- mechanical class: NO UNIT

Node: `((ROUND(CAST((ROUND(((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) * 0.5), 2) + ROUND(CAST((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) AS REAL), 2)) AS REAL), 2) * (((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) / ((ROUND((CAST(((CA`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s10" AS (SELECT "genres"."id" AS "o0", SUM(((round(CAST((round(((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) * 0.5), 2) + round(CAST((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) AS REAL), 2)) AS REAL), 2) * (((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) / ((round((CAST(((CAST(0 AS REAL) * 0.2) * 0.5) AS REAL) * 10), 2) * round((CAST(((CAST(0 AS REAL) * 0.2) * 0.5) AS REAL) * 10), 2)) + ((CAST((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) AS INTEGER) / 10) * (1 - ((CAST(0 AS REAL) * 0.2) / 0.1))))) * 0.25)) * (log(10, round(round((CAST(((CAST(0 AS REAL) * 0.2) * 0.5) AS REAL) * 10), 2))) + 10.0))) AS "o1" FROM "genres" AS "genres" GROUP BY "genres"."id") SELECT "s10"."o0" AS "o0", SUM(((0.25 / ((((coalesce("s10"."o1", 0) * (1 - ("s10"."o1" / coalesce("s10"."o1", 0)))) - (1 - "s10"."o1")) + (((
```

## store_1-u6 (attempt 62) -- mechanical class: NO UNIT

Node: `((1 - CASE WHEN "s6"."o0" > 'Av. Paulista, 2022' THEN 4 ELSE 0 END) * ROUND((CAST("s6"."o2" AS REAL) / "s6"."o1"), 2))`

- left operand: unit '', kind '', quantity ()
- right operand: unit 'rows per bytes × ms × currency (USD assumed)', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s6" AS (SELECT "invoices"."billing_address" AS "o0", AVG((((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3))) AS "o1", round(CAST(COUNT(*) AS REAL), 2) AS "o2", round(CAST(COUNT(*) AS INTEGER), 2) AS "o3" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" WHERE ("tracks"."unit_price" > 0.99 OR (((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3)) > -4555391.94) GROUP BY "invoices"."billing_address") SELECT "s6"."o0" AS "o0", ((1 - (((CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 WHEN "s6"."o0" >= 'Rotenturmstraße 4, 1010 Innere Stadt' THEN 4 ELSE 1 END * 0.75) + (CASE WHEN CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 W
```

## store_1-u7 (attempt 4) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - POWER(1.5, 2))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "playlist_tracks"."playlist_id" AS "o0", ((((((1 - power(1.5, 2)) / 5) + (((1 - power(1.5, 2)) * 0.25) / 2)) * 0.2) * (((((CAST(power(1.5, 2) AS REAL) / ((1 - power(1.5, 2)) / 5)) * (CASE WHEN "playlists"."name" = 'Music' THEN 1 WHEN "playlists"."name" > 'Music Videos' THEN 4 ELSE 1 END / 0.2)) * 1.5) * 10) + 0)) - ((((((round(CAST(power(1.5, 2) AS REAL), 2) + 0) * 0.2) * 10) * (CASE WHEN round(CAST(power(1.5, 2) AS REAL), 2) = (CASE WHEN "playlists"."name" = 'Music' THEN 1 WHEN "playlists"."name" > 'Music Videos' THEN 4 ELSE 1 END / 0.2) THEN 10 WHEN CASE WHEN "playlists"."name" = 'Music' THEN 1 WHEN "playlists"."name" > 'Music Videos' THEN 4 ELSE 1 END = CASE WHEN "playlists"."name" = 'Music' THEN 1 WHEN "playlists"."name" > 'Music Videos' THEN 4 ELSE 1 END THEN 1 WHEN round(CAST(power(1.5, 2) AS REAL), 2) < (CASE WHEN "playlists"."name" = 'Music' THEN 1 WHEN "playlists"."name" 
```

## store_1-u8 (attempt 47) -- mechanical class: SCORE

Node: `((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (ROUND(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END)`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind 'indicator', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s16" AS (SELECT "customers"."last_name" AS "o0", (((CAST((CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) AS REAL) / (CAST(round(2, 2) AS REAL) * 0.5)) * 5) * CASE WHEN (CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) > "customers"."first_name" THEN 1 END) AS "o1", "customers"."fax" AS "o2", "customers"."first_name" AS "o3", coalesce((((CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) * 0.1) - ((round(CAST
```

## store_1-u9 (attempt 17) -- mechanical class: WHOLE of BOTH KNOWN

Node: `(1 - ROUND(CAST("tracks"."bytes" AS REAL), 2))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit 'bytes', kind '', quantity ('tracks.bytes', 'value')
- stored columns under it: tracks.bytes [unit 'bytes' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "invoice_lines"."id" AS "o0", (CAST((CASE WHEN round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) = (round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) * 10) THEN (1 - "tracks"."milliseconds") WHEN ("tracks"."unit_price" > 0.99 AND (CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."milliseconds" AS REAL)) = (CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."milliseconds" AS REAL))) THEN 3 ELSE 1 END * 3) AS REAL) / CAST(((round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) * 10) * (CASE WHEN round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) = (round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) * 10) THEN (1 - "tracks"."milliseconds") WHEN ("tracks"."unit_price" > 0.99 AND (CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."millise
```

## store_1-u10 (attempt 145) -- mechanical class: NO UNIT

Node: `((CAST(1.5 AS INTEGER) * 10) * (ROUND(2, 2) + SQRT(2)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "albums"."title" AS "o0", "albums"."id" AS "o1", "artists"."id" AS "o2", round(((CAST(((CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * 0.5) + (((CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) + (CAST((CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) / (CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * 0.5)) AS REAL) * 2)) + (CASE WHEN (CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) = (CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * ((CAST(1.5 AS INTEGER) * 10) * (round(2, 2) + sqrt(2)))) THEN 2 ELSE 0 END / 5))) AS REAL) / ((CAST(CASE WHEN (CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) = (CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * ((CAST(1.5 AS INTEGER) * 10) * (round(2, 2) + sqrt(2)))) THEN 2 ELSE 0 END AS REAL) / (((CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) + (CAST((CAS
```

## store_1-u11 (attempt 159) -- mechanical class: NO UNIT

Node: `(((0.5 / ("s10"."o1" * 0.2)) / ((CAST((1 - ("s10"."o1" / COALESCE("s10"."o1", 0))) AS REAL) * 1.5) * (CASE WHEN ("s10"."o0" > 7 AND (1 - "s10"."o1") > ((1 - "s10"."o1") * ROUND("s10"."o1", 2)) AND (1 - "s10"."o1") != (0.5 / ("s10"."o1" * 0.2))) THEN 3 ELSE 0 END / CASE WHEN ("s10"."o0" > 7 AND (1 - `

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s10" AS (SELECT "genres"."id" AS "o0", SUM(((round(CAST((round(((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) * 0.5), 2) + round(CAST((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) AS REAL), 2)) AS REAL), 2) * (((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) / ((round((CAST(((CAST(0 AS REAL) * 0.2) * 0.5) AS REAL) * 10), 2) * round((CAST(((CAST(0 AS REAL) * 0.2) * 0.5) AS REAL) * 10), 2)) + ((CAST((((CAST(0 AS REAL) * 0.2) * 0.5) * ((CAST(0 AS REAL) * 0.2) * 0.5)) AS INTEGER) / 10) * (1 - ((CAST(0 AS REAL) * 0.2) / 0.1))))) * 0.25)) * (log(10, round(round((CAST(((CAST(0 AS REAL) * 0.2) * 0.5) AS REAL) * 10), 2))) + 10.0))) AS "o1" FROM "genres" AS "genres" GROUP BY "genres"."id") SELECT "s10"."o0" AS "o0", SUM(((0.25 / ((((coalesce("s10"."o1", 0) * (1 - ("s10"."o1" / coalesce("s10"."o1", 0)))) - (1 - "s10"."o1")) + (((
```

## store_1-u12 (attempt 62) -- mechanical class: BOTH KNOWN

Node: `(((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3))`

- left operand: unit 'bytes × ms', kind '', quantity ()
- right operand: unit 'currency (USD assumed)', kind '', quantity ()
- stored columns under it: invoices.total [unit 'currency (USD assumed)' (model), kind '', scale 'ratio']; tracks.bytes [unit 'bytes' (model), kind '', scale 'ratio']; tracks.milliseconds [unit 'ms' (model), kind '', scale 'ratio']
- catalogue relations among them: tracks.bytes rate tracks.milliseconds

Whole query:
```sql
WITH "s6" AS (SELECT "invoices"."billing_address" AS "o0", AVG((((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3))) AS "o1", round(CAST(COUNT(*) AS REAL), 2) AS "o2", round(CAST(COUNT(*) AS INTEGER), 2) AS "o3" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" WHERE ("tracks"."unit_price" > 0.99 OR (((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3)) > -4555391.94) GROUP BY "invoices"."billing_address") SELECT "s6"."o0" AS "o0", ((1 - (((CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 WHEN "s6"."o0" >= 'Rotenturmstraße 4, 1010 Innere Stadt' THEN 4 ELSE 1 END * 0.75) + (CASE WHEN CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 W
```

## store_1-u13 (attempt 145) -- mechanical class: NO UNIT

Node: `((CAST(1.5 AS INTEGER) * 10) * (ROUND(2, 2) + SQRT(2)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "albums"."title" AS "o0", "albums"."id" AS "o1", "artists"."id" AS "o2", round(((CAST(((CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * 0.5) + (((CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) + (CAST((CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) / (CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * 0.5)) AS REAL) * 2)) + (CASE WHEN (CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) = (CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * ((CAST(1.5 AS INTEGER) * 10) * (round(2, 2) + sqrt(2)))) THEN 2 ELSE 0 END / 5))) AS REAL) / ((CAST(CASE WHEN (CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) = (CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END * ((CAST(1.5 AS INTEGER) * 10) * (round(2, 2) + sqrt(2)))) THEN 2 ELSE 0 END AS REAL) / (((CAST(CASE WHEN "artists"."id" = 50 THEN 3 ELSE 0 END AS REAL) * 2) + (CAST((CAS
```

## store_1-u14 (attempt 17) -- mechanical class: BOTH KNOWN

Node: `(CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."milliseconds" AS REAL))`

- left operand: unit 'ms', kind '', quantity ()
- right operand: unit 'ms', kind '', quantity ('tracks.milliseconds', 'value')
- stored columns under it: tracks.milliseconds [unit 'ms' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "invoice_lines"."id" AS "o0", (CAST((CASE WHEN round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) = (round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) * 10) THEN (1 - "tracks"."milliseconds") WHEN ("tracks"."unit_price" > 0.99 AND (CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."milliseconds" AS REAL)) = (CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."milliseconds" AS REAL))) THEN 3 ELSE 1 END * 3) AS REAL) / CAST(((round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) * 10) * (CASE WHEN round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) = (round(CAST((1 - round(CAST("tracks"."bytes" AS REAL), 2)) AS INTEGER), 2) * 10) THEN (1 - "tracks"."milliseconds") WHEN ("tracks"."unit_price" > 0.99 AND (CAST(("tracks"."milliseconds" * 0.2) AS REAL) / CAST("tracks"."millise
```

## store_1-u15 (attempt 62) -- mechanical class: BOTH KNOWN

Node: `(CAST("s6"."o2" AS REAL) / "s6"."o1")`

- left operand: unit 'rows', kind 'count', quantity ()
- right operand: unit 'bytes × ms × currency (USD assumed)', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s6" AS (SELECT "invoices"."billing_address" AS "o0", AVG((((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3))) AS "o1", round(CAST(COUNT(*) AS REAL), 2) AS "o2", round(CAST(COUNT(*) AS INTEGER), 2) AS "o3" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" WHERE ("tracks"."unit_price" > 0.99 OR (((1 - (("tracks"."bytes" / 8107896) * ("tracks"."milliseconds" * 3))) / 2) * ("invoices"."total" * 3)) > -4555391.94) GROUP BY "invoices"."billing_address") SELECT "s6"."o0" AS "o0", ((1 - (((CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 WHEN "s6"."o0" >= 'Rotenturmstraße 4, 1010 Innere Stadt' THEN 4 ELSE 1 END * 0.75) + (CASE WHEN CASE WHEN "s6"."o0" != 'Barbarossastraße 19' THEN 3 W
```

## store_1-u16 (attempt 1) -- mechanical class: NO UNIT

Node: `(((CASE WHEN COALESCE(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN COALESCE(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN COALESCE(0, 0) = 0 THEN 3 ELSE 1 END) / 5))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "genres"."id" AS "o0", coalesce((((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) + (((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1))) - ((((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0
```

## store_1-u17 (attempt 59) -- mechanical class: BOTH KNOWN

Node: `(((CAST(("tracks"."bytes" * "tracks"."milliseconds") AS REAL) * 2) / 10) * (CAST(("tracks"."bytes" * "tracks"."milliseconds") AS REAL) * 2))`

- left operand: unit 'bytes × ms', kind '', quantity ()
- right operand: unit 'bytes × ms', kind '', quantity ()
- stored columns under it: tracks.bytes [unit 'bytes' (model), kind '', scale 'ratio']; tracks.milliseconds [unit 'ms' (model), kind '', scale 'ratio']
- catalogue relations among them: tracks.bytes rate tracks.milliseconds

Whole query:
```sql
SELECT "tracks"."unit_price" AS "o0", AVG(((((("tracks"."bytes" * "tracks"."milliseconds") * CASE WHEN "tracks"."milliseconds" = 262791 THEN 1 ELSE 1 END) / 1.5) + 0) + ((("tracks"."bytes" * "tracks"."milliseconds") * CASE WHEN "tracks"."milliseconds" = 262791 THEN 1 ELSE 1 END) * 0.1))) AS "o1", AVG(round(CAST((CAST((((("tracks"."bytes" * "tracks"."milliseconds") * CASE WHEN "tracks"."milliseconds" = 262791 THEN 1 ELSE 1 END) / 1.5) + 0) AS REAL) / ((((("tracks"."bytes" * "tracks"."milliseconds") * CASE WHEN "tracks"."milliseconds" = 262791 THEN 1 ELSE 1 END) / 1.5) + 0) + ((("tracks"."bytes" * "tracks"."milliseconds") * CASE WHEN "tracks"."milliseconds" = 262791 THEN 1 ELSE 1 END) * 0.1))) AS REAL), 2)) AS "o2", power(round(CAST(AVG(((round(CAST(CASE WHEN "invoice_lines"."unit_price" = 1.99 THEN 0 WHEN "tracks"."name" >= 'Can I Play With Madness' THEN 10 ELSE 0 END AS REAL), 2) * 10) -
```

## store_1-u18 (attempt 148) -- mechanical class: BOTH KNOWN

Node: `((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds")))`

- left operand: unit 'ms', kind '', quantity ()
- right operand: unit 'per ms', kind '', quantity ()
- stored columns under it: tracks.milliseconds [unit 'ms' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
SELECT "tracks"."media_type_id" AS "o0", CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")
```

## store_1-u19 (attempt 69) -- mechanical class: BOTH KNOWN

Node: `(((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (("tracks"."milliseconds" / ((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5)))) * 0.1)))`

- left operand: unit 'bytes × ms', kind '', quantity ()
- right operand: unit 'bytes × ms × ms per bytes × ms', kind '', quantity ()
- stored columns under it: tracks.bytes [unit 'bytes' (model), kind '', scale 'ratio']; tracks.milliseconds [unit 'ms' (model), kind '', scale 'ratio']
- catalogue relations among them: tracks.bytes rate tracks.milliseconds

Whole query:
```sql
SELECT "tracks"."media_type_id" AS "o0", abs((((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (("tracks"."milliseconds" / ((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5)))) * 0.1)))) AS "o1", "tracks"."bytes" AS "o2", ("tracks"."bytes" - abs((((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (("tracks"."milliseconds" / ((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5)))) * 0.1))))) AS "o3", (((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (((("tracks"."bytes" / 8107896) + 1.0) * (1280000.0 - ("tracks"."milliseconds" * 5))) * (("tracks"
```

## store_1-u20 (attempt 50) -- mechanical class: WHOLE of SCORE

Node: `(1 - CASE WHEN ("employees"."last_name" > 'Peacock' AND "s8"."o0" = '1000' AND ("tracks"."bytes" / 8107896) > 1.0) THEN 1 ELSE 3 END)`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: employees.last_name [unit '' (-), kind '', scale '']; tracks.bytes [unit 'bytes' (model), kind '', scale 'ratio']
- catalogue relations among them: none

Whole query:
```sql
WITH "s8" AS (SELECT "invoices"."billing_postal_code" AS "o0", log(10, round(((("invoices"."total" / 3.96) * round(CAST((((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) + ("invoices"."total" / 3.96)) AS INTEGER), 2)) - ((round(CAST("invoices"."invoice_date" AS REAL), 2) + log(10, (((CAST(((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) AS REAL) * 0.5) * 0.1) + 0))) * (((((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) * (((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) + ("invoices"."total" / 3.96))) * 2) * 0.75))), 2)) AS "o1" FROM "customers" AS "customers" LEFT JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" WHERE (((((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) * (((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) + ("invoices"."total" / 3.96))) * 2) > 
```

