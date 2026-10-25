# store_1: 20 random delivered programs

## store_1-1 (attempt 86)

```sql
SELECT "tracks"."id" AS "o0", "tracks"."bytes" AS "o1", "tracks"."milliseconds" AS "o2", "media_types"."name" AS "o3", FIRST_VALUE("tracks"."bytes") OVER (ORDER BY "tracks"."milliseconds" ASC) AS "o4", "tracks"."name" AS "o5" FROM "tracks" AS "tracks" INNER JOIN "genres" AS "genres" ON "tracks"."genre_id" = "genres"."id" LEFT JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" ORDER BY "media_types"."name" DESC LIMIT 100
```


## store_1-2 (attempt 49)

```sql
SELECT "playlist_tracks"."track_id" AS "o0", ((((((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) + (0.000156 - ((10 / "tracks"."milliseconds") / 0.25))) * ((1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))) * 1.5)) / (1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))))) * 2) + 0) * ((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) / 10) + 0)) AS "o1", (((round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) * 0.75) * (1 - round(CAST("tracks"."milliseconds" AS REAL), 2))) * (CAST((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) AS REAL) / CAST(round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) AS REAL))) AS "o2", ((round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) * 0.75) * (1 - round(CAST("tracks"."milliseconds" AS REAL), 2))) AS "o3", (CAST((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) AS REAL) / CAST(round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) AS REAL)) AS "o4", round((((round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) * 0.75) * (1 - round(CAST("tracks"."milliseconds" AS REAL), 2))) - ((((((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) + (0.000156 - ((10 / "tracks"."milliseconds") / 0.25))) * ((1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))) * 1.5)) / (1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))))) * 2) + 0) * ((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) / 10) + 0))), 2) AS "o5", CASE WHEN ((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) / 10) + 0) = ((1 - (CAST((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) AS REAL) / CAST(round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) AS REAL))) * ((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * (((CASE WHEN (round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) > 1.0 THEN 1 WHEN ("playlist_tracks"."track_id" = 3418 AND round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229) THEN 10 WHEN "playlist_tracks"."track_id" = 3444 THEN 3 WHEN "playlist_tracks"."track_id" > 888 THEN 1 END / 10) * 2) * 2))) THEN 5 WHEN ((1 - (CAST((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) AS REAL) / CAST(round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) AS REAL))) * ((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * (((CASE WHEN (round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) > 1.0 THEN 1 WHEN ("playlist_tracks"."track_id" = 3418 AND round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229) THEN 10 WHEN "playlist_tracks"."track_id" = 3444 THEN 3 WHEN "playlist_tracks"."track_id" > 888 THEN 1 END / 10) * 2) * 2))) = ((1 - (CAST((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) AS REAL) / CAST(round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) AS REAL))) * ((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * (((CASE WHEN (round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) > 1.0 THEN 1 WHEN ("playlist_tracks"."track_id" = 3418 AND round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229) THEN 10 WHEN "playlist_tracks"."track_id" = 3444 THEN 3 WHEN "playlist_tracks"."track_id" > 888 THEN 1 END / 10) * 2) * 2))) THEN 5 ELSE 1 END AS "o6", CAST(((1 - (CAST((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) AS REAL) / CAST(round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) AS REAL))) * ((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * (((CASE WHEN (round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) > 1.0 THEN 1 WHEN ("playlist_tracks"."track_id" = 3418 AND round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229) THEN 10 WHEN "playlist_tracks"."track_id" = 3444 THEN 3 WHEN "playlist_tracks"."track_id" > 888 THEN 1 END / 10) * 2) * 2))) AS REAL) AS "o7" FROM "playlist_tracks" AS "playlist_tracks" INNER JOIN "tracks" AS "tracks" ON "playlist_tracks"."track_id" = "tracks"."id" WHERE ((("tracks"."milliseconds" * "tracks"."bytes") + (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 10) / 0.5)) > 2072653886064.01 AND (round(CAST((("tracks"."milliseconds" * "tracks"."bytes") + (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 10) / 0.5)) AS REAL), 2) * CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END) > (round(CAST((("tracks"."milliseconds" * "tracks"."bytes") + (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 10) / 0.5)) AS REAL), 2) * CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END) AND NOT (("tracks"."milliseconds" * "tracks"."bytes") IS NULL) AND ((((((CASE WHEN "tracks"."name" = 'Where Eagles Dare' THEN 4 WHEN (CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") = 0.03 THEN 1 WHEN (CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END > "tracks"."name" AND "tracks"."unit_price" > 0.99 AND ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 10) = 0.0) THEN 4 ELSE 0 END * 0.2) + ((((((1 - (10 / "tracks"."milliseconds")) * ((0.1 / "tracks"."bytes") / 1.5)) / 0.25) * (((CAST("tracks"."bytes" AS REAL) / 8107896) * (1 - ("tracks"."milliseconds" / 255634))) * 0.1)) * 100) * ((CAST("tracks"."bytes" AS REAL) / 8107896) * 0.75))) + 0) * 2) - ((((((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) + (0.000156 - ((10 / "tracks"."milliseconds") / 0.25))) * ((1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))) * 1.5)) / (1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))))) * 2) + 0) * ((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) / 10) + 0))) > (((((CASE WHEN "tracks"."name" = 'Where Eagles Dare' THEN 4 WHEN (CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") = 0.03 THEN 1 WHEN (CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END > "tracks"."name" AND "tracks"."unit_price" > 0.99 AND ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 10) = 0.0) THEN 4 ELSE 0 END * 0.2) + ((((((1 - (10 / "tracks"."milliseconds")) * ((0.1 / "tracks"."bytes") / 1.5)) / 0.25) * (((CAST("tracks"."bytes" AS REAL) / 8107896) * (1 - ("tracks"."milliseconds" / 255634))) * 0.1)) * 100) * ((CAST("tracks"."bytes" AS REAL) / 8107896) * 0.75))) + 0) * 2) - ((((((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) + (0.000156 - ((10 / "tracks"."milliseconds") / 0.25))) * ((1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))) * 1.5)) / (1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634)))))) * 2) + 0) * ((coalesce(CAST(CASE WHEN "tracks"."composer" = 'James Hetfield, Lars Ulrich' THEN 2 WHEN "tracks"."composer" = 'The Tea Party' THEN 3 ELSE 0 END AS REAL), 0) / 10) + 0))) OR round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2) = round(CAST((1.0 - (1 - ((1 - ("tracks"."milliseconds" / 255634)) * (1 - ("tracks"."milliseconds" / 255634))))) AS REAL), 2)))
```

- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` case/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter CONVERT: plausible (model)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown
- `*` column/column: unknown
- `*` case/derived: unknown
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)

## store_1-3 (attempt 145)

```sql
SELECT "invoices"."billing_postal_code" AS "o0", "invoices"."billing_state" AS "o1", CAST("invoices"."total" AS REAL) AS "o2", "invoices"."total" AS "o3" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" ORDER BY "invoices"."total" DESC LIMIT 100
```


## store_1-4 (attempt 186)

```sql
SELECT "tracks"."composer" AS "o0", AVG(CASE WHEN "tracks"."name" = 'Without You' THEN 2 WHEN "tracks"."media_type_id" IN (("tracks"."bytes" / (("tracks"."milliseconds" + 255634) + round((1 - (((sqrt(("tracks"."milliseconds" + 255634)) * sqrt(("tracks"."milliseconds" + 255634))) * "tracks"."milliseconds") * 10)), 2))), "tracks"."composer") THEN 5 WHEN ("tracks"."bytes" / (("tracks"."milliseconds" + 255634) + round((1 - (((sqrt(("tracks"."milliseconds" + 255634)) * sqrt(("tracks"."milliseconds" + 255634))) * "tracks"."milliseconds") * 10)), 2))) > -0.0 THEN 4 WHEN ((("tracks"."milliseconds" + 255634) + round((1 - (((sqrt(("tracks"."milliseconds" + 255634)) * sqrt(("tracks"."milliseconds" + 255634))) * "tracks"."milliseconds") * 10)), 2)) < -668214412046692891 AND ("tracks"."bytes" / (("tracks"."milliseconds" + 255634) + round((1 - (((sqrt(("tracks"."milliseconds" + 255634)) * sqrt(("tracks"."milliseconds" + 255634))) * "tracks"."milliseconds") * 10)), 2))) > -0.0) THEN 1 WHEN round((1 - (((sqrt(("tracks"."milliseconds" + 255634)) * sqrt(("tracks"."milliseconds" + 255634))) * "tracks"."milliseconds") * 10)), 2) = -668214412047204159 THEN 3 ELSE 0 END) AS "o1" FROM "playlists" AS "playlists" INNER JOIN "playlist_tracks" AS "playlist_tracks" ON "playlists"."id" = "playlist_tracks"."playlist_id" LEFT JOIN "tracks" AS "tracks" ON "playlist_tracks"."track_id" = "tracks"."id" WHERE "playlists"."name" > 'Music Videos' GROUP BY "tracks"."composer" ORDER BY "tracks"."composer" DESC LIMIT 1
```

- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` column/derived: unknown
- `*` function/function: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `/` column/derived: unknown
- `+` derived/derived: unknown

## store_1-5 (attempt 22)

```sql
WITH "s9" AS (SELECT DISTINCT "tracks"."album_id" AS "o0", AVG(((1 - round(CAST("tracks"."bytes" AS REAL), 2)) * CASE WHEN "tracks"."album_id" > 141 THEN 1 WHEN ((1.5 / (1 - "tracks"."milliseconds")) * (abs((round(CAST("tracks"."bytes" AS REAL), 2) / 8107896)) + 1.0)) > -0.0 THEN 1 ELSE 1 END)) AS "o1" FROM "tracks" AS "tracks" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" GROUP BY "tracks"."album_id") SELECT "s9"."o0" AS "o0", "s9"."o1" AS "o1", "media_types"."name" AS "o2", "playlist_tracks"."track_id" AS "o3" FROM "tracks" AS "tracks" INNER JOIN "s9" AS "s9" ON "s9"."o0" = "tracks"."album_id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" INNER JOIN "playlist_tracks" AS "playlist_tracks" ON "tracks"."id" = "playlist_tracks"."track_id" LEFT JOIN "playlists" AS "playlists" ON "playlist_tracks"."playlist_id" = "playlists"."id" INNER JOIN "genres" AS "genres" ON "tracks"."genre_id" = "genres"."id" WHERE NOT ("s9"."o1" IS NULL) ORDER BY "s9"."o1" DESC LIMIT 100
```

- `*` case/derived: unknown
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## store_1-6 (attempt 5)

```sql
SELECT "customers"."postal_code" AS "o0", ("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) AS "o1", "invoices"."invoice_date" AS "o2", (1 - (CAST("invoices"."total" AS REAL) / 3.96)) AS "o3", CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END AS "o4", 1 AS "o5", CASE WHEN CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END < ((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) + ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) * round(CAST((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) AS REAL), 2))) THEN 1 WHEN (("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) > ((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) * 0.75) AND "employees"."address" > '7727B 41 Ave') THEN 1 WHEN (CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END = "employees"."birth_date" AND CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END = "employees"."hire_date" AND CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END < "employees"."title") THEN 1 WHEN ("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) = ((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) / CAST((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) AS REAL)) THEN 0 ELSE 0 END AS "o6" FROM "customers" AS "customers" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id" WHERE ("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) = "invoices"."invoice_date" ORDER BY CASE WHEN CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END < ((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) + ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) * round(CAST((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) AS REAL), 2))) THEN 1 WHEN (("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) > ((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) * 0.75) AND "employees"."address" > '7727B 41 Ave') THEN 1 WHEN (CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END = "employees"."birth_date" AND CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END = "employees"."hire_date" AND CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END < "employees"."title") THEN 1 WHEN ("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) = ((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) / CAST((("invoices"."total" / ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0)) * CASE WHEN ((1 - (CAST("invoices"."total" AS REAL) / 3.96)) + 0) = 0.0 THEN 4 ELSE 0 END) AS REAL)) THEN 0 ELSE 0 END DESC
```

- `/` derived/derived: unknown
- `*` case/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `/` column/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown

## store_1-7 (attempt 185)

```sql
SELECT CAST("tracks"."milliseconds" AS REAL) AS "o0", abs((((1 - ((CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / 0.1) / 10)) * (CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / (1 - ((CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / 0.1) / 10)))) + (1 - (1 - (("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)) / 0.25))))) AS "o1", round(("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)), 2) AS "o2", (((1 - ((CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / 0.1) / 10)) * (CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / (1 - ((CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / 0.1) / 10)))) + (1 - (1 - (("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)) / 0.25)))) AS "o3", CAST((1 - (1 - (("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)) / 0.25))) AS REAL) AS "o4", PERCENT_RANK() OVER (PARTITION BY (((1 - ((CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / 0.1) / 10)) * (CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / (1 - ((CASE WHEN ("media_types"."name" > 'Purchased AAC audio file' OR "tracks"."unit_price" = 1.99) THEN 10 ELSE 0 END / 0.1) / 10)))) + (1 - (1 - (("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)) / 0.25)))) ORDER BY round(("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)), 2) DESC) AS "o5", FIRST_VALUE("tracks"."unit_price") OVER (PARTITION BY "tracks"."bytes" ORDER BY round(("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)), 2) DESC) AS "o6" FROM "albums" AS "albums" INNER JOIN "artists" AS "artists" ON "albums"."artist_id" = "artists"."id" INNER JOIN "tracks" AS "tracks" ON "albums"."id" = "tracks"."album_id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" ORDER BY FIRST_VALUE("tracks"."unit_price") OVER (PARTITION BY "tracks"."bytes" ORDER BY round(("tracks"."bytes" + ((CAST("tracks"."bytes" AS REAL) / 8107896) / 0.1)), 2) DESC) DESC
```

- `+` column/derived: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` case/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## store_1-8 (attempt 93)

```sql
SELECT "customers"."last_name" AS "o0", "employees"."reports_to" AS "o1", CAST("invoices"."id" AS REAL) AS "o2", "invoices"."total" AS "o3", CASE WHEN "invoices"."id" = 30 THEN 0 WHEN "invoices"."id" < 104 THEN 0 ELSE 0 END AS "o4", power((CASE WHEN "invoices"."id" = 30 THEN 0 WHEN "invoices"."id" < 104 THEN 0 ELSE 0 END * (0.1 / CAST("invoices"."total" AS REAL))), 1.5) AS "o5", CASE WHEN (CASE WHEN "invoices"."id" = 30 THEN 0 WHEN "invoices"."id" < 104 THEN 0 ELSE 0 END * (0.1 / CAST("invoices"."total" AS REAL))) = (CASE WHEN "invoices"."id" = 30 THEN 0 WHEN "invoices"."id" < 104 THEN 0 ELSE 0 END * 0.75) THEN 2 WHEN "employees"."reports_to" = 6 THEN 1 ELSE 0 END AS "o6" FROM "invoices" AS "invoices" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" ORDER BY CASE WHEN "invoices"."id" = 30 THEN 0 WHEN "invoices"."id" < 104 THEN 0 ELSE 0 END DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` case/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)

## store_1-9 (attempt 85)

```sql
SELECT "tracks"."composer" AS "o0", ("tracks"."bytes" / sqrt(round(CAST("tracks"."bytes" AS REAL), 2))) AS "o1" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" WHERE NOT ("tracks"."bytes" IS NULL) ORDER BY sqrt(round(CAST("tracks"."bytes" AS REAL), 2)) DESC
```

- `/` column/function: unknown

## store_1-10 (attempt 71)

```sql
WITH "s5" AS (SELECT "invoices"."total" AS "o0", AVG(CASE WHEN "invoices"."billing_address" = '69 Salem Street' THEN 1 WHEN "invoices"."billing_address" > 'Praça Pio X, 119' THEN 3 WHEN "invoices"."total" = 3.96 THEN 2 ELSE 0 END) FILTER (WHERE ("invoices"."billing_address" > 'Qe 7 Bloco G' AND CASE WHEN "invoices"."billing_address" = '69 Salem Street' THEN 1 WHEN "invoices"."billing_address" > 'Praça Pio X, 119' THEN 3 WHEN "invoices"."total" = 3.96 THEN 2 ELSE 0 END > "invoices"."billing_city" AND "invoices"."billing_city" = 'New York')) AS "o1" FROM "invoices" AS "invoices" WHERE "invoices"."total" >= 3.96 GROUP BY "invoices"."total") SELECT CAST(AVG(CASE WHEN NOT (CASE WHEN ((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) + 1.0) = 2.0 THEN 1 ELSE 0 END IS NULL) THEN ((log(10, coalesce(CAST((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) AS REAL), 0)) * 5) + coalesce(CAST((CASE WHEN ((1 - "s5"."o0") / 3) = -0.99 THEN 4 WHEN (((1 - "s5"."o0") / 3) * ((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) / 10)) = round(("s5"."o0" - 3.96), 2) THEN 0 ELSE 0 END + CASE WHEN round(("s5"."o0" - 3.96), 2) = 0.0 THEN 1 ELSE 0 END) AS REAL), 0)) ELSE 5 END) AS REAL) AS "o0", AVG(CASE WHEN NOT (CASE WHEN ((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) + 1.0) = 2.0 THEN 1 ELSE 0 END IS NULL) THEN ((log(10, coalesce(CAST((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) AS REAL), 0)) * 5) + coalesce(CAST((CASE WHEN ((1 - "s5"."o0") / 3) = -0.99 THEN 4 WHEN (((1 - "s5"."o0") / 3) * ((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) / 10)) = round(("s5"."o0" - 3.96), 2) THEN 0 ELSE 0 END + CASE WHEN round(("s5"."o0" - 3.96), 2) = 0.0 THEN 1 ELSE 0 END) AS REAL), 0)) ELSE 5 END) AS "o1", SUM(CASE WHEN ((((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) + 1.0) / 0.1) * 0.1) < 2.0 THEN (coalesce(CAST((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) AS REAL), 0) - coalesce(CAST((CASE WHEN ((1 - "s5"."o0") / 3) = -0.99 THEN 4 WHEN (((1 - "s5"."o0") / 3) * ((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) / 10)) = round(("s5"."o0" - 3.96), 2) THEN 0 ELSE 0 END + CASE WHEN round(("s5"."o0" - 3.96), 2) = 0.0 THEN 1 ELSE 0 END) AS REAL), 0)) ELSE 1 END) AS "o2" FROM "s5" AS "s5" WHERE round(CAST(((((((1 - round(CAST(round(CAST("s5"."o1" AS REAL), 2) AS REAL), 2)) - ((CAST(round(CAST("s5"."o1" AS REAL), 2) AS REAL) / round(CAST("s5"."o1" AS REAL), 2)) * (CASE WHEN "s5"."o1" > "s5"."o1" THEN 1 WHEN "s5"."o1" = ("s5"."o1" / "s5"."o1") THEN 1 WHEN "s5"."o0" > 3.96 THEN 4 WHEN ("s5"."o0" > 8.91 OR "s5"."o0" = 13.86) THEN 4 ELSE 3 END / CASE WHEN "s5"."o1" > "s5"."o1" THEN 1 WHEN "s5"."o1" = ("s5"."o1" / "s5"."o1") THEN 1 WHEN "s5"."o0" > 3.96 THEN 4 WHEN ("s5"."o0" > 8.91 OR "s5"."o0" = 13.86) THEN 4 ELSE 3 END))) + (((1 - ((("s5"."o0" / 3.96) + (1 - "s5"."o0")) * 0.1)) + 1.2) / 1.5)) + ((((1 - (((1 - "s5"."o0") / 3) * 10)) / 2) / ((CAST(((1 - "s5"."o0") / 3) AS INTEGER) / ((1 - "s5"."o0") / 3)) + 0)) / 10)) * 2) / ((1 - ((((((1 - "s5"."o0") / 3) * ((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) / 10)) * (CAST((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) AS INTEGER) / 3)) * 1.5) / 0.1)) + (((1 - "s5"."o1") / 0.5) * 0.75))) AS REAL), 2) IN ((round(((((((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) + 1.0) / 0.1) * 0.1) + ((CASE WHEN ((1 - "s5"."o0") / 3) = -0.99 THEN 4 WHEN (((1 - "s5"."o0") / 3) * ((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) / 10)) = round(("s5"."o0" - 3.96), 2) THEN 0 ELSE 0 END + CASE WHEN round(("s5"."o0" - 3.96), 2) = 0.0 THEN 1 ELSE 0 END) * 1.5)) * 2), 2) * CASE WHEN ((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) + 1.0) = 2.0 THEN 1 ELSE 0 END), '?') ORDER BY AVG(CASE WHEN NOT (CASE WHEN ((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) + 1.0) = 2.0 THEN 1 ELSE 0 END IS NULL) THEN ((log(10, coalesce(CAST((1 - ((round(("s5"."o0" - 3.96), 2) / 0.5) / 0.1)) AS REAL), 0)) * 5) + coalesce(CAST((CASE WHEN ((1 - "s5"."o0") / 3) = -0.99 THEN 4 WHEN (((1 - "s5"."o0") / 3) * ((("s5"."o1" / "s5"."o1") + (1 - "s5"."o1")) / 10)) = round(("s5"."o0" - 3.96), 2) THEN 0 ELSE 0 END + CASE WHEN round(("s5"."o0" - 3.96), 2) = 0.0 THEN 1 ELSE 0 END) AS REAL), 0)) ELSE 5 END) DESC
```

- `+` derived/derived: unknown
- `+` case/case: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: plausible (model)
- `/` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown
- `*` constant-derived: unknown (a constant)
- `/` case/case: unknown (equal operands)
- `/` step output/step output: unknown
- `-` parameter REFERENCE: unknown (a constant)

## store_1-11 (attempt 155)

```sql
SELECT "customers"."country" AS "o0", round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2) AS "o1", CAST(((((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END) * round((CAST("invoices"."total" AS REAL) * 5), 1)) - ((((round((CAST("invoices"."total" AS REAL) * 5), 1) * 0.2) * 5) * 0.25) + 4.95)) AS REAL) AS "o2", "customers"."city" AS "o3", (((1 - (round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2) / round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2))) / 0.2) - ((1 - (round(((CAST(((round((CAST("invoices"."total" AS REAL) * 5), 1) * 0.2) * 5) AS REAL) * 0.2) * 1.5), 2) + coalesce(CAST((round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2) / round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2)) AS REAL), 0))) / 0.5)) AS "o4", ((1 - (round(((CAST(((round((CAST("invoices"."total" AS REAL) * 5), 1) * 0.2) * 5) AS REAL) * 0.2) * 1.5), 2) + coalesce(CAST((round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2) / round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2)) AS REAL), 0))) / 0.5) AS "o5", ((((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END) * round((CAST("invoices"."total" AS REAL) * 5), 1)) - ((((round((CAST("invoices"."total" AS REAL) * 5), 1) * 0.2) * 5) * 0.25) + 4.95)) AS "o6", RANK() OVER (ORDER BY ((((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END) * round((CAST("invoices"."total" AS REAL) * 5), 1)) - ((((round((CAST("invoices"."total" AS REAL) * 5), 1) * 0.2) * 5) * 0.25) + 4.95)) ASC) AS "o7", CURRENT_DATE AS "o8" FROM "invoices" AS "invoices" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" WHERE "customers"."first_name" IN ('Patrick', 'Hannah') ORDER BY coalesce(CAST((round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2) / round(((CASE WHEN "customers"."fax" > '+1 (604) 688-8756' THEN 1 ELSE 0 END * 10) * CASE WHEN "customers"."first_name" > 'Tim' THEN 10 ELSE 2 END), 2)) AS REAL), 0) ASC
```

- `/` derived/derived: unknown (equal operands)
- `*` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## store_1-12 (attempt 57)

```sql
SELECT "customers"."last_name" AS "o0", "customers"."fax" AS "o1", "invoices"."billing_city" AS "o2", "invoices"."billing_address" AS "o3" FROM "invoices" AS "invoices" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id"
```


## store_1-13 (attempt 151)

```sql
SELECT "playlists"."id" AS "o0", ((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) AS "o1", round((((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) - ((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0)), 2) AS "o2", (CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) AS "o3", CASE WHEN ((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) = (((((CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END * 10) / 0.2) + (CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 10)) + ((((CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 10) AS REAL) * 0.5) + ((CAST(CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END AS INTEGER) / (CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END * 10)) / 0.1)) * 0.5) * 2)) / CAST(((((CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 10) AS REAL) * 0.5) + ((CAST(CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END AS INTEGER) / (CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END * 10)) / 0.1)) * 0.5) * 2) AS REAL)) THEN 4 ELSE 0 END AS "o4", CURRENT_DATE AS "o5" FROM "playlist_tracks" AS "playlist_tracks" INNER JOIN "playlists" AS "playlists" ON "playlist_tracks"."playlist_id" = "playlists"."id" WHERE (((((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) / 3) / 0.5) > ((((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) / 3) / 0.5) AND ((((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) / 3) / 0.5) = ((((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) / 3) / 0.5)) ORDER BY CASE WHEN ((CAST(abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL)) AS REAL) / abs(CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 3) AS REAL))) + 0) = (((((CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END * 10) / 0.2) + (CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 10)) + ((((CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 10) AS REAL) * 0.5) + ((CAST(CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END AS INTEGER) / (CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END * 10)) / 0.1)) * 0.5) * 2)) / CAST(((((CAST((CASE WHEN "playlists"."name" = 'Classical 101 - The Basics' THEN 1 ELSE 10 END * 10) AS REAL) * 0.5) + ((CAST(CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END AS INTEGER) / (CASE WHEN CAST("playlists"."name" AS REAL) = 'Music Videos' THEN 3 ELSE 0 END * 10)) / 0.1)) * 0.5) * 2) AS REAL)) THEN 4 ELSE 0 END DESC LIMIT 10
```

- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## store_1-14 (attempt 59)

```sql
WITH "s3" AS (SELECT "invoices"."id" AS "o0", AVG(CASE WHEN "invoices"."id" BETWEEN 207 AND 310 THEN 1 ELSE 0 END) AS "o1" FROM "invoices" AS "invoices" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id" GROUP BY "invoices"."id") SELECT "s3"."o1" AS "o0", log(10, sqrt(((((2 / ("s3"."o1" - 0)) * 3) * CAST("s3"."o1" AS REAL)) - (((1 - "s3"."o1") / 0.75) + ((((1 - "s3"."o1") / 0.75) / 5) + ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5))))))) AS "o1", round(CAST(AVG(CASE WHEN ((((2 / ("s3"."o1" - 0)) * 3) * CAST("s3"."o1" AS REAL)) - (((1 - "s3"."o1") / 0.75) + ((((1 - "s3"."o1") / 0.75) / 5) + ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5))))) = ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5)) THEN (2 / ((((CAST("s3"."o1" AS REAL) * 3) + 0) / 1.5) / ((1 - "s3"."o1") / 0.75))) WHEN (2 / ((((CAST("s3"."o1" AS REAL) * 3) + 0) / 1.5) / ((1 - "s3"."o1") / 0.75))) = (2 / ((((CAST("s3"."o1" AS REAL) * 3) + 0) / 1.5) / ((1 - "s3"."o1") / 0.75))) THEN 2 WHEN (((1 - "s3"."o1") / 0.75) + ((((1 - "s3"."o1") / 0.75) / 5) + ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5)))) = (0.25 / (1 - "s3"."o1")) THEN 1 WHEN ((0.25 / (1 - "s3"."o1")) < ((((CAST("s3"."o1" AS REAL) * 3) + 0) / 1.5) / ((1 - "s3"."o1") / 0.75)) OR (0.25 / (1 - "s3"."o1")) != (0.25 / (1 - "s3"."o1"))) THEN 5 ELSE 0 END) AS REAL)) AS "o2", AVG(CASE WHEN log(10, sqrt(((((2 / ("s3"."o1" - 0)) * 3) * CAST("s3"."o1" AS REAL)) - (((1 - "s3"."o1") / 0.75) + ((((1 - "s3"."o1") / 0.75) / 5) + ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5))))))) = 10 THEN (0.75 / (sqrt(((0.25 / (1 - "s3"."o1")) + (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) * (((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) * 0.5)))) * 0.5)) WHEN (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) = (100 - (((1 - "s3"."o1") * 1.5) * 100)) AND ((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) > ((CAST("s3"."o1" AS REAL) * 3) - ((0.25 / (1 - "s3"."o1")) + (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) * (((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) * 0.5))))) THEN 0 WHEN (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) * (((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) * 0.5)) > ((0.25 / "s3"."o1") + round(CAST((0.25 / "s3"."o1") AS REAL), 1)) THEN 2 ELSE 0 END) AS "o3", coalesce(AVG(CASE WHEN "s3"."o1" = "s3"."o1" THEN ((round(CAST("s3"."o1" AS REAL), 2) * 2) * round((log(10, coalesce(CAST("s3"."o1" AS REAL), 0)) * 10), 2)) ELSE 0 END) FILTER (WHERE log(10, sqrt(((((2 / ("s3"."o1" - 0)) * 3) * CAST("s3"."o1" AS REAL)) - (((1 - "s3"."o1") / 0.75) + ((((1 - "s3"."o1") / 0.75) / 5) + ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5))))))) < 10), 0) AS "o4" FROM "s3" AS "s3" GROUP BY "s3"."o1" ORDER BY AVG(CASE WHEN log(10, sqrt(((((2 / ("s3"."o1" - 0)) * 3) * CAST("s3"."o1" AS REAL)) - (((1 - "s3"."o1") / 0.75) + ((((1 - "s3"."o1") / 0.75) / 5) + ((((1 - "s3"."o1") / 0.75) / 5) / (((CAST("s3"."o1" AS REAL) * 3) + 0) * 0.5))))))) = 10 THEN (0.75 / (sqrt(((0.25 / (1 - "s3"."o1")) + (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) * (((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) * 0.5)))) * 0.5)) WHEN (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) = (100 - (((1 - "s3"."o1") * 1.5) * 100)) AND ((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) > ((CAST("s3"."o1" AS REAL) * 3) - ((0.25 / (1 - "s3"."o1")) + (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) * (((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) * 0.5))))) THEN 0 WHEN (round((((CAST("s3"."o1" AS REAL) / (0.25 / (1 - "s3"."o1"))) * (CAST("s3"."o1" AS REAL) * 10)) + 0), 2) * (((CASE WHEN (1 - "s3"."o1") = "s3"."o1" THEN 3 ELSE 1 END / ((1 - "s3"."o1") / 0.75)) * (100 - (((1 - "s3"."o1") * 1.5) * 100))) * 0.5)) > ((0.25 / "s3"."o1") + round(CAST((0.25 / "s3"."o1") AS REAL), 1)) THEN 2 ELSE 0 END) DESC
```

- `+` derived/derived: strong (rule)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: strong (rule)
- `*` parameter CONVERT: strong (rule)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: strong (rule)
- `/` case/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/step output: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## store_1-15 (attempt 13)

```sql
SELECT CAST(AVG((5 / (((1.5 / (round(CAST(log(10, (round(2, 2) * (round(2, 2) * 10))) AS REAL), 2) / round(CAST((round(2, 2) * (round(2, 2) * 10)) AS REAL), 2))) / 0.2) + ((1.5 / (round(CAST(log(10, (round(2, 2) * (round(2, 2) * 10))) AS REAL), 2) / round(CAST((round(2, 2) * (round(2, 2) * 10)) AS REAL), 2))) + (1 - round(2, 2)))))) AS REAL) AS "o0", (5 / (((1.5 / (round(CAST(log(10, (round(2, 2) * (round(2, 2) * 10))) AS REAL), 2) / round(CAST((round(2, 2) * (round(2, 2) * 10)) AS REAL), 2))) / 0.2) + ((1.5 / (round(CAST(log(10, (round(2, 2) * (round(2, 2) * 10))) AS REAL), 2) / round(CAST((round(2, 2) * (round(2, 2) * 10)) AS REAL), 2))) + (1 - round(2, 2))))) AS "o1", round(CAST(COUNT(*) AS REAL), 2) AS "o2" FROM "artists" AS "artists" ORDER BY round(CAST(COUNT(*) AS REAL), 2) DESC, (5 / (((1.5 / (round(CAST(log(10, (round(2, 2) * (round(2, 2) * 10))) AS REAL), 2) / round(CAST((round(2, 2) * (round(2, 2) * 10)) AS REAL), 2))) / 0.2) + ((1.5 / (round(CAST(log(10, (round(2, 2) * (round(2, 2) * 10))) AS REAL), 2) / round(CAST((round(2, 2) * (round(2, 2) * 10)) AS REAL), 2))) + (1 - round(2, 2))))) DESC
```

- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/function: unknown
- `*` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## store_1-16 (attempt 122)

```sql
SELECT "customers"."id" AS "o0", coalesce((((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) * ((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) / (CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)))) / CAST(((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) * ((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) / (CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)))) AS INTEGER)), 1) AS "o1", (((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) * ((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) / (CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)))) / CAST(((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) * ((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) / (CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)))) AS INTEGER)) AS "o2", ((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) * ((CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)) / (CAST("employees"."birth_date" AS REAL) - CAST("employees"."hire_date" AS REAL)))) AS "o3" FROM "customers" AS "customers" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone"
```

- `*` constant-derived: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `-` column/column: unknown
- `/` derived/derived: unknown

## store_1-17 (attempt 9)

```sql
SELECT "customers"."last_name" AS "o0", "invoices"."customer_id" AS "o1", "invoices"."total" AS "o2", 1 AS "o3", CASE WHEN "invoices"."customer_id" = 49 THEN 3 WHEN "invoices"."customer_id" = 31 THEN 10 WHEN "customers"."last_name" = 'Van der Berg' THEN 5 ELSE 0 END AS "o4" FROM "employees" AS "employees" INNER JOIN "customers" AS "customers" ON "employees"."id" = "customers"."support_rep_id" INNER JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" ORDER BY "invoices"."total" DESC
```


## store_1-18 (attempt 103)

```sql
SELECT "tracks"."genre_id" AS "o0", round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) AS "o1", round((((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) + (1 - coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000))) * (CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634)), 0) AS "o2", (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) AS "o3", (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) AS "o4", CASE WHEN CAST((CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634) AS REAL) < ((((round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * 1.5) * (((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) + 0)) THEN 4 WHEN ((((round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * 1.5) * (((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) + 0)) < (((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) - round((((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) + (1 - coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000))) * (CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634)), 0)) THEN ((10 / CAST(((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) AS REAL)) * (((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * ((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) * 0.1))) WHEN (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) = "tracks"."composer" THEN 1 WHEN round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) >= (round((((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) + (1 - coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000))) * (CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634)), 0) - (((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * ((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) * 0.1))) THEN ((10 / CAST(((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) AS REAL)) * 1.5) WHEN round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) = "tracks"."composer" THEN 5 ELSE 0 END AS "o5", PERCENT_RANK() OVER (ORDER BY ((10 / CAST(((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) AS REAL)) * 1.5) DESC) AS "o6" FROM "tracks" AS "tracks" INNER JOIN "albums" AS "albums" ON "tracks"."album_id" = "albums"."id" WHERE ((("tracks"."bytes" / "tracks"."milliseconds") = 31.72 OR ((((1 - (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1) - (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1) * 0.5))) + 0.842) - (round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2) * 1000)) * (1 - (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1) - (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1) * 0.5)))) > (((1 - (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1) - (((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1) * 0.5))) + 0.842) - (round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2) * 1000))) AND ("tracks"."name" IN ('Wasting Love', 'Can I Play With Madness') OR (round(CAST(round(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3), 2) AS REAL), 2) * CASE WHEN "tracks"."unit_price" = 0.99 THEN 4 ELSE 1 END) < (round(CAST(round(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3), 2) AS REAL), 2) * CASE WHEN "tracks"."unit_price" = 0.99 THEN 4 ELSE 1 END))) ORDER BY CASE WHEN CAST((CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634) AS REAL) < ((((round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * 1.5) * (((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) + 0)) THEN 4 WHEN ((((round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * 1.5) * (((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) + 0)) < (((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) - round((((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) + (1 - coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000))) * (CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634)), 0)) THEN ((10 / CAST(((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) AS REAL)) * (((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * ((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) * 0.1))) WHEN (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2) = "tracks"."composer" THEN 1 WHEN round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) >= (round((((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) + (1 - coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000))) * (CAST(coalesce(CAST(round(CAST("tracks"."milliseconds" AS REAL), 2) AS REAL), 1000000) AS INTEGER) / 255634)), 0) - (((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) / (round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) * 2)) * ((abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2)) * 0.1))) THEN ((10 / CAST(((1 - (abs((CASE WHEN "tracks"."genre_id" < 3 THEN 1 WHEN "tracks"."unit_price" = 1.99 THEN 1 WHEN round(CAST("tracks"."milliseconds" AS REAL), 2) > 207229 THEN 5 ELSE 1 END * 0.1)) + round(CAST(((1 - round(CAST("tracks"."milliseconds" AS REAL), 2)) / 3) AS REAL), 2))) * 1.5) AS REAL)) * 1.5) WHEN round(round(CAST((CAST((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") AS REAL) / ((CAST("tracks"."milliseconds" AS INTEGER) / "tracks"."bytes") / 0.1)) AS REAL), 2), 2) = "tracks"."composer" THEN 5 ELSE 0 END DESC
```

- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `*` case/derived: unknown
- `-` derived/derived: unknown
- `*` parameter CONVERT: plausible (model)
- `+` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` derived/derived: plausible (model)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` column/column: plausible (model)

## store_1-19 (attempt 166)

```sql
WITH "s10" AS (SELECT DISTINCT "genres"."name" AS "o0", AVG(((((CASE WHEN "genres"."id" = 15 THEN 5 WHEN "genres"."id" > 19 THEN 3 WHEN ("genres"."id" > 19 AND "genres"."id" = 3 AND "genres"."id" < 13) THEN 1 WHEN "genres"."id" BETWEEN 7 AND 7 THEN 0 ELSE 0 END * 0.1) / 1.5) + 0) * (CASE WHEN "genres"."id" = 15 THEN 5 WHEN "genres"."id" > 19 THEN 3 WHEN ("genres"."id" > 19 AND "genres"."id" = 3 AND "genres"."id" < 13) THEN 1 WHEN "genres"."id" BETWEEN 7 AND 7 THEN 0 ELSE 0 END * 5))) AS "o1" FROM "genres" AS "genres" GROUP BY "genres"."name"), "s21" AS (SELECT DISTINCT "playlists"."id" AS "o0", round(CAST((((CAST((1 - CASE WHEN "playlists"."name" = 'Classical' THEN 3 END) AS REAL) / CASE WHEN "playlists"."name" = 'Classical' THEN 3 END) + (((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * (((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END / 0.5) * (1 - (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10))) + 0)) * 0.2) + ((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * (((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END / 0.5) * (1 - (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10))) + 0)) / CASE WHEN "playlists"."name" = 'Classical' THEN 3 END))) * ((((((CAST((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10) AS INTEGER) / (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10)) / 0.5) * 0.5) * 1.5) + (CAST(((CAST((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10) AS INTEGER) / (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10)) / 0.5) AS REAL) / (((CAST((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10) AS INTEGER) / (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10)) / 0.5) * 0.5))) + ((((CAST((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10) AS INTEGER) / (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10)) / 0.5) * 0.5) / ((CAST((CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10) AS INTEGER) / (CASE WHEN "playlists"."name" = 'Classical' THEN 3 END * 10)) / 0.5)))) AS REAL), 2) AS "o1" FROM "playlists" AS "playlists" LEFT JOIN "playlist_tracks" AS "playlist_tracks" ON "playlists"."id" = "playlist_tracks"."playlist_id"), "s24" AS (SELECT "tracks"."album_id" AS "o0", round(((-7850000.0 - (CAST("tracks"."milliseconds" AS REAL) - CAST("tracks"."bytes" AS REAL))) + (((-7850000.0 - (CAST("tracks"."milliseconds" AS REAL) - CAST("tracks"."bytes" AS REAL))) / (-7850000.0 - (CAST("tracks"."milliseconds" AS REAL) - CAST("tracks"."bytes" AS REAL)))) + 1.0)), 2) AS "o1" FROM "invoice_lines" AS "invoice_lines" LEFT JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" ORDER BY round(((-7850000.0 - (CAST("tracks"."milliseconds" AS REAL) - CAST("tracks"."bytes" AS REAL))) + (((-7850000.0 - (CAST("tracks"."milliseconds" AS REAL) - CAST("tracks"."bytes" AS REAL))) / (-7850000.0 - (CAST("tracks"."milliseconds" AS REAL) - CAST("tracks"."bytes" AS REAL)))) + 1.0)), 2) DESC LIMIT 5), "s25" AS (SELECT "s24"."o1" AS "o0", "s24"."o0" AS "o1" FROM "albums" AS "albums" INNER JOIN "artists" AS "artists" ON "albums"."artist_id" = "artists"."id" INNER JOIN "s24" AS "s24" ON "s24"."o0" = "albums"."id" ORDER BY "s24"."o1" DESC LIMIT 10) SELECT "customers"."email" AS "o0", "s25"."o1" AS "o1", "s21"."o1" AS "o2" FROM "tracks" AS "tracks" INNER JOIN "s24" AS "s24" ON "s24"."o0" = "tracks"."album_id" INNER JOIN "s25" AS "s25" ON "s25"."o1" = "tracks"."album_id" INNER JOIN "playlist_tracks" AS "playlist_tracks" ON "tracks"."id" = "playlist_tracks"."track_id" INNER JOIN "playlists" AS "playlists" ON "playlist_tracks"."playlist_id" = "playlists"."id" INNER JOIN "s21" AS "s21" ON "s21"."o0" = "playlist_tracks"."playlist_id" INNER JOIN "genres" AS "genres" ON "tracks"."genre_id" = "genres"."id" LEFT JOIN "invoice_lines" AS "invoice_lines" ON "tracks"."id" = "invoice_lines"."track_id" INNER JOIN "albums" AS "albums" ON "tracks"."album_id" = "albums"."id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" INNER JOIN "artists" AS "artists" ON "albums"."artist_id" = "artists"."id" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "s10" AS "s10" ON "s10"."o0" = "genres"."name"
```

- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `/` case/derived: unknown
- `*` case/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` case/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `-` parameter REFERENCE: unknown (a constant)
- `-` column/column: unknown (disputed (model))

## store_1-20 (attempt 173)

```sql
WITH "s5" AS (SELECT "employees"."city" AS "o0", COUNT(*) AS "o1" FROM "invoices" AS "invoices" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id" WHERE (("invoices"."total" * 2) - (("invoices"."total" * 0.75) - (("invoices"."total" / 3.96) + 1.0))) > 6.95 GROUP BY "employees"."city") SELECT "employees"."country" AS "o0", "invoices"."billing_address" AS "o1", "customers"."state" AS "o2", "tracks"."bytes" AS "o3", "s5"."o0" AS "o4", coalesce(("s5"."o1" / "tracks"."bytes"), 0) AS "o5", CASE WHEN "media_types"."name" > 'AAC audio file' THEN 5 WHEN "tracks"."bytes" = 528499160 THEN 5 WHEN "employees"."fax" = '+1 (403) 263-4289' THEN 4 ELSE 3 END AS "o6", NTILE(4) OVER (ORDER BY "tracks"."bytes" ASC) AS "o7" FROM "playlist_tracks" AS "playlist_tracks" INNER JOIN "tracks" AS "tracks" ON "playlist_tracks"."track_id" = "tracks"."id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" INNER JOIN "genres" AS "genres" ON "tracks"."genre_id" = "genres"."id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "tracks"."id" = "invoice_lines"."track_id" INNER JOIN "playlists" AS "playlists" ON "playlist_tracks"."playlist_id" = "playlists"."id" INNER JOIN "albums" AS "albums" ON "tracks"."album_id" = "albums"."id" LEFT JOIN "artists" AS "artists" ON "albums"."artist_id" = "artists"."id" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" LEFT JOIN "s5" AS "s5" ON "s5"."o0" = "employees"."city" WHERE (NOT ("s5"."o1" IS NULL) AND "s5"."o0" = 'Edmonton' AND "invoices"."billing_address" IN ('Rua Dr. Falcão Filho, 155', '302 S 700 E')) ORDER BY "tracks"."bytes" DESC
```

- `-` derived/derived: plausible (model)
- `-` derived/derived: plausible (model)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/step output: unknown

