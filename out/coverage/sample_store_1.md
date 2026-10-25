# store_1: 20 random delivered programs

## store_1-1 (attempt 50)

```sql
WITH "s8" AS (SELECT "invoices"."billing_postal_code" AS "o0", log(10, round(((("invoices"."total" / 3.96) * round(CAST((((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) + ("invoices"."total" / 3.96)) AS INTEGER), 2)) - ((round(CAST("invoices"."invoice_date" AS REAL), 2) + log(10, (((CAST(((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) AS REAL) * 0.5) * 0.1) + 0))) * (((((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) * (((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) + ("invoices"."total" / 3.96))) * 2) * 0.75))), 2)) AS "o1" FROM "customers" AS "customers" LEFT JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" WHERE (((((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) * (((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) + ("invoices"."total" / 3.96))) * 2) > 0.48 AND "invoices"."billing_country" IN ('Belgium', 'Canada')) ORDER BY (round(CAST("invoices"."invoice_date" AS REAL), 2) + log(10, (((CAST(((("invoices"."total" / 3.96) / ("invoices"."total" / 3.96)) / 5) AS REAL) * 0.5) * 0.1) + 0))) DESC LIMIT 100), "s23" AS (SELECT "artists"."name" AS "o0", AVG(((((CAST((((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5)) AS REAL) / (((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5))) + 0) + (((CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) > (CAST(round(CAST(round(2, 2) AS REAL)) AS INTEGER) / CAST(round(2, 4) AS REAL)) THEN 5 ELSE 0 END + CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) = (1 - round(2, 4)) THEN 10 ELSE 1 END) / 0.5) + 0)) / 0.2)) AS "o1" FROM "artists" AS "artists" INNER JOIN "albums" AS "albums" ON "artists"."id" = "albums"."artist_id" WHERE (((((CAST((((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5)) AS REAL) / (((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5))) + 0) + (((CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) > (CAST(round(CAST(round(2, 2) AS REAL)) AS INTEGER) / CAST(round(2, 4) AS REAL)) THEN 5 ELSE 0 END + CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) = (1 - round(2, 4)) THEN 10 ELSE 1 END) / 0.5) + 0)) / 0.2) < ((((CAST((((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5)) AS REAL) / (((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5))) + 0) + (((CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) > (CAST(round(CAST(round(2, 2) AS REAL)) AS INTEGER) / CAST(round(2, 4) AS REAL)) THEN 5 ELSE 0 END + CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) = (1 - round(2, 4)) THEN 10 ELSE 1 END) / 0.5) + 0)) / 0.2) AND (CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) > (CAST(round(CAST(round(2, 2) AS REAL)) AS INTEGER) / CAST(round(2, 4) AS REAL)) THEN 5 ELSE 0 END + CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) = (1 - round(2, 4)) THEN 10 ELSE 1 END) < ((((CAST((((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5)) AS REAL) / (((CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) * 0.2) + (((1 - ((round(2, 4) / 0.5) * (1 - round(2, 4)))) * 0.5) + 2.5))) + 0) + (((CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) > (CAST(round(CAST(round(2, 2) AS REAL)) AS INTEGER) / CAST(round(2, 4) AS REAL)) THEN 5 ELSE 0 END + CASE WHEN (CAST(round(CAST(round(2, 2) AS REAL)) AS REAL) / round(CAST(round(2, 2) AS REAL))) = (1 - round(2, 4)) THEN 10 ELSE 1 END) / 0.5) + 0)) / 0.2)) GROUP BY "artists"."name") SELECT "s8"."o1" AS "o0", "employees"."last_name" AS "o1", "s8"."o0" AS "o2", (("s8"."o1" + (("tracks"."bytes" / 8107896) * ((1 - CASE WHEN ("employees"."last_name" > 'Peacock' AND "s8"."o0" = '1000' AND ("tracks"."bytes" / 8107896) > 1.0) THEN 1 ELSE 3 END) * 0.2))) + ("tracks"."milliseconds" * 5)) AS "o3" FROM "playlist_tracks" AS "playlist_tracks" INNER JOIN "playlists" AS "playlists" ON "playlist_tracks"."playlist_id" = "playlists"."id" INNER JOIN "tracks" AS "tracks" ON "playlist_tracks"."track_id" = "tracks"."id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "tracks"."id" = "invoice_lines"."track_id" INNER JOIN "genres" AS "genres" ON "tracks"."genre_id" = "genres"."id" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" INNER JOIN "s8" AS "s8" ON "s8"."o0" = "invoices"."billing_postal_code" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" INNER JOIN "albums" AS "albums" ON "tracks"."album_id" = "albums"."id" LEFT JOIN "artists" AS "artists" ON "albums"."artist_id" = "artists"."id" INNER JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "s23" AS "s23" ON "s23"."o0" = "artists"."name"
```

- `+` column/function: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `/` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` case/case: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` derived/derived: unknown
- `+` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/step output: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)

## store_1-2 (attempt 119)

```sql
WITH "s1" AS (SELECT "albums"."title" AS "o0" FROM "artists" AS "artists" INNER JOIN "albums" AS "albums" ON "artists"."id" = "albums"."artist_id" INNER JOIN "tracks" AS "tracks" ON "albums"."id" = "tracks"."album_id" WHERE "tracks"."composer" IN ((SELECT "invoices"."total" AS "o0" FROM "invoices" AS "invoices")) ORDER BY "albums"."title" DESC LIMIT 5) SELECT "playlist_tracks"."playlist_id" AS "o0", "s1"."o0" AS "o1", "media_types"."name" AS "o2", ((CAST("tracks"."bytes" AS REAL) / CAST("tracks"."bytes" AS REAL)) - (round(CAST((CAST("tracks"."bytes" AS REAL) / CAST("tracks"."bytes" AS REAL)) AS INTEGER), 1) * 2)) AS "o3", "tracks"."milliseconds" AS "o4" FROM "playlist_tracks" AS "playlist_tracks" INNER JOIN "playlists" AS "playlists" ON "playlist_tracks"."playlist_id" = "playlists"."id" INNER JOIN "tracks" AS "tracks" ON "playlist_tracks"."track_id" = "tracks"."id" LEFT JOIN "albums" AS "albums" ON "tracks"."album_id" = "albums"."id" INNER JOIN "s1" AS "s1" ON "s1"."o0" = "albums"."title" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id"
```

- `-` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` column/column: unknown (equal operands)

## store_1-3 (attempt 111)

```sql
SELECT "media_types"."name" AS "o0", "tracks"."genre_id" AS "o1", exp((((CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END * exp(((((CAST(CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END AS REAL) * 0.5) + (1 - (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10))) * ((CAST(CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END AS REAL) * 0.5) + (1 - (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10)))) + (CAST((CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10) AS REAL) * 0.1)))) * (exp(((((CAST(CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END AS REAL) * 0.5) + (1 - (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10))) * ((CAST(CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END AS REAL) * 0.5) + (1 - (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10)))) + (CAST((CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10) AS REAL) * 0.1))) / 5)) / (1 - round(CAST(round(CAST(coalesce(CAST(max(CAST("tracks"."genre_id" AS REAL), (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 3), 0) AS REAL), 0) AS REAL), 1) AS REAL), 2)))) AS "o2", abs(((round(CAST(coalesce(CAST(max(CAST("tracks"."genre_id" AS REAL), (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 3), 0) AS REAL), 0) AS REAL), 1) * exp(((((CAST(CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END AS REAL) * 0.5) + (1 - (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10))) * ((CAST(CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END AS REAL) * 0.5) + (1 - (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10)))) + (CAST((CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 10) AS REAL) * 0.1)))) * coalesce(CAST(max(CAST("tracks"."genre_id" AS REAL), (CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END / 3), 0) AS REAL), 0))) AS "o3" FROM "invoice_lines" AS "invoice_lines" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" INNER JOIN "playlist_tracks" AS "playlist_tracks" ON "tracks"."id" = "playlist_tracks"."track_id" WHERE ("tracks"."name" IN ('The Wizard', 'Whole Lotta Love') AND "tracks"."name" = 'The Evil That Men Do' AND (((abs((("tracks"."bytes" + CASE WHEN "tracks"."milliseconds" = 192653 THEN 1 ELSE 0 END) * ((1 - "tracks"."milliseconds") * (CASE WHEN "tracks"."milliseconds" = 192653 THEN 1 ELSE 0 END * 0.5)))) / (((abs((("tracks"."bytes" + CASE WHEN "tracks"."milliseconds" = 192653 THEN 1 ELSE 0 END) * ((1 - "tracks"."milliseconds") * (CASE WHEN "tracks"."milliseconds" = 192653 THEN 1 ELSE 0 END * 0.5)))) * 3) / ((CASE WHEN (abs(("tracks"."milliseconds" - "tracks"."milliseconds")) = 0 AND abs(("tracks"."milliseconds" - "tracks"."milliseconds")) = ("tracks"."milliseconds" - "tracks"."milliseconds")) THEN 3 ELSE 0 END / 1.5) / 0.5)) / 5)) + (round(CAST((((1 - "tracks"."bytes") / ((1 - "tracks"."bytes") * 2)) / 0.25) AS REAL), 2) * 1000)) * 10) = (round(CAST((((1 - "tracks"."bytes") / ((1 - "tracks"."bytes") * 2)) / 0.25) AS REAL), 2) * 1000)) GROUP BY "tracks"."genre_id", "media_types"."name", CASE WHEN "media_types"."name" < 'Protected MPEG-4 video file' THEN 3 ELSE 0 END
```

- `*` derived/function: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` function/function: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` case/function: unknown
- `*` parameter CONVERT: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` column/column: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` case/column: unknown

## store_1-4 (attempt 20)

```sql
SELECT "customers"."id" AS "o0", "employees"."birth_date" AS "o1", CAST("invoices"."total" AS REAL) AS "o2", CAST("invoices"."total" AS REAL) AS "o3", CAST("invoices"."total" AS INTEGER) AS "o4", "employees"."state" AS "o5", "invoices"."total" AS "o6" FROM "customers" AS "customers" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" ORDER BY "invoices"."total" DESC
```


## store_1-5 (attempt 79)

```sql
WITH "s4" AS (SELECT "customers"."last_name" AS "o0", "customers"."country" AS "o1", CASE WHEN CAST("customers"."first_name" AS REAL) > 'Eduardo' THEN 2 WHEN "customers"."company" > 'Telus' THEN 1 ELSE 0 END AS "o2" FROM "customers" AS "customers" WHERE ("customers"."first_name" > 'Michelle' AND CAST("customers"."first_name" AS INTEGER) < 'Ladislav' AND NOT ("customers"."fax" IS NULL)) ORDER BY "customers"."country" DESC LIMIT 10), "s12" AS (SELECT "s4"."o1" AS "o0", (1 - coalesce(CAST("s4"."o2" AS REAL), 0)) AS "o1", round(((((sqrt(((1 - coalesce(CAST("s4"."o2" AS REAL), 0)) / 10)) * 0.1) + 0) * (CAST(sqrt(((1 - coalesce(CAST("s4"."o2" AS REAL), 0)) / 10)) AS INTEGER) / (1 - coalesce(CAST("s4"."o2" AS REAL), 0)))) * 1.5), 2) AS "o2", "s4"."o0" AS "o3" FROM "s4" AS "s4" WHERE "s4"."o2" < (((1 - coalesce(CAST("s4"."o2" AS REAL), 0)) / 10) * (((1 - coalesce(CAST("s4"."o2" AS REAL), 0)) * 0.2) * 0.75)) ORDER BY round(((((sqrt(((1 - coalesce(CAST("s4"."o2" AS REAL), 0)) / 10)) * 0.1) + 0) * (CAST(sqrt(((1 - coalesce(CAST("s4"."o2" AS REAL), 0)) / 10)) AS INTEGER) / (1 - coalesce(CAST("s4"."o2" AS REAL), 0)))) * 1.5), 2) DESC LIMIT 100) SELECT "s12"."o0" AS "o0", ("s4"."o2" * 0.5) AS "o1", (("s12"."o1" * 0.2) * 10) AS "o2", (((1 - coalesce((CAST(((("s12"."o1" * 0.2) * 10) + ("s4"."o2" * 0.5)) AS REAL) / 1.5), 0)) * ((("s12"."o1" * 0.2) * 10) / (("s12"."o1" * 0.2) * 10))) * 2) AS "o3", CASE WHEN "s12"."o0" > 'Belgium' THEN 5 ELSE 0 END AS "o4", "s4"."o1" AS "o5", CASE WHEN "s4"."o1" < 'Czech Republic' THEN 10 WHEN "s4"."o2" > (((round(CAST(("s12"."o1" * 0.2) AS REAL), 2) * 0.2) * ((coalesce((round((CAST((round("s4"."o2", 2) + 0) AS REAL) * 2), 2) * 10), 0) * 0.75) + (CAST((round("s4"."o2", 2) + 0) AS REAL) / 3))) / 5) THEN 5 WHEN (((round(CAST(("s12"."o1" * 0.2) AS REAL), 2) * 0.2) * ((coalesce((round((CAST((round("s4"."o2", 2) + 0) AS REAL) * 2), 2) * 10), 0) * 0.75) + (CAST((round("s4"."o2", 2) + 0) AS REAL) / 3))) / 5) BETWEEN round(CAST((CAST((round("s4"."o2", 2) + 0) AS REAL) * 2) AS REAL), 2) AND RANK() OVER (ORDER BY coalesce((round((CAST((round("s4"."o2", 2) + 0) AS REAL) * 2), 2) * 10), 0) DESC) THEN 0 WHEN (("s12"."o1" * 0.2) * 10) > ((CAST(coalesce((CAST(((("s12"."o1" * 0.2) * 10) + ("s4"."o2" * 0.5)) AS REAL) / 1.5), 0) AS REAL) / 3) + ((RANK() OVER (ORDER BY coalesce((round((CAST((round("s4"."o2", 2) + 0) AS REAL) * 2), 2) * 10), 0) DESC) / (("s12"."o1" * 0.2) * 10)) * ((power(((1 - CASE WHEN ("s4"."o1" > 'Spain' AND round("s4"."o2", 2) > "s4"."o1") THEN 5 WHEN round("s4"."o2", 2) > (("s4"."o2" * 0.5) * 2) THEN 2 ELSE 0 END) + (CAST(((1 - ("s12"."o2" / "s12"."o1")) * 1.5) AS REAL) * 10)), 1.5) * 0.25) + 0))) THEN 4 ELSE 0 END AS "o6" FROM "s4" AS "s4" INNER JOIN "s12" AS "s12" ON "s12"."o0" = "s4"."o1" WHERE ("s12"."o2" = "s12"."o2" OR "s12"."o3" < ((("s12"."o1" * 0.2) * 10) + ("s4"."o2" * 0.5))) ORDER BY ((CAST(coalesce((CAST(((("s12"."o1" * 0.2) * 10) + ("s4"."o2" * 0.5)) AS REAL) / 1.5), 0) AS REAL) / 3) + ((RANK() OVER (ORDER BY coalesce((round((CAST((round("s4"."o2", 2) + 0) AS REAL) * 2), 2) * 10), 0) DESC) / (("s12"."o1" * 0.2) * 10)) * ((power(((1 - CASE WHEN ("s4"."o1" > 'Spain' AND round("s4"."o2", 2) > "s4"."o1") THEN 5 WHEN round("s4"."o2", 2) > (("s4"."o2" * 0.5) * 2) THEN 2 ELSE 0 END) + (CAST(((1 - ("s12"."o2" / "s12"."o1")) * 1.5) AS REAL) * 10)), 1.5) * 0.25) + 0))) DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/function: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` step output/step output: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/window: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `-` parameter WHOLE: unknown (a constant)

## store_1-6 (attempt 185)

```sql
SELECT DISTINCT "tracks"."media_type_id" AS "o0", "tracks"."album_id" AS "o1", "tracks"."bytes" AS "o2" FROM "artists" AS "artists" INNER JOIN "albums" AS "albums" ON "artists"."id" = "albums"."artist_id" INNER JOIN "tracks" AS "tracks" ON "albums"."id" = "tracks"."album_id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "tracks"."id" = "invoice_lines"."track_id" INNER JOIN "invoices" AS "invoices" ON "invoice_lines"."invoice_id" = "invoices"."id" ORDER BY "tracks"."album_id" DESC
```


## store_1-7 (attempt 125)

```sql
SELECT "customers"."postal_code" AS "o0", "customers"."fax" AS "o1", round((CAST("invoices"."total" AS REAL) * (CAST("invoices"."total" AS INTEGER) * ("invoices"."total" / 3.96))), 2) AS "o2", "invoices"."total" AS "o3" FROM "employees" AS "employees" INNER JOIN "customers" AS "customers" ON "employees"."id" = "customers"."support_rep_id" LEFT JOIN "invoices" AS "invoices" ON "customers"."id" = "invoices"."customer_id" WHERE ("customers"."fax" > '+1 (604) 688-8756' AND "customers"."fax" = '+55 (61) 3363-7855' AND NOT ("employees"."first_name" IS NULL)) ORDER BY round((CAST("invoices"."total" AS REAL) * (CAST("invoices"."total" AS INTEGER) * ("invoices"."total" / 3.96))), 2) DESC, "invoices"."total" ASC
```

- `*` column/derived: unknown
- `*` column/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)

## store_1-8 (attempt 99)

```sql
SELECT "customers"."support_rep_id" AS "o0", round(CAST(((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) AS REAL), 1) AS "o1", CAST((round(CAST(((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) AS REAL), 1) / CAST(((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) AS INTEGER)) AS REAL) AS "o2", (((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) AS "o3", "customers"."fax" AS "o4", sqrt((((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) / CAST(((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) AS REAL)) + (round(CAST(((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) AS REAL), 1) * 2))) AS "o5", CASE WHEN "customers"."city" = 'Madrid' THEN 2 WHEN (round(CAST(((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) AS REAL), 1) * 2) = ((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) - (((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2)) THEN 3 WHEN ((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) / CAST(((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) AS REAL)) = ((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) * (CAST((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) AS REAL) / (((0.75 / power(1.5, 1.5)) - CASE WHEN "customers"."city" = 'Montréal' THEN 1 ELSE 0 END) * 0.5))) THEN 10 WHEN ((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) * (CAST((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) AS REAL) / (((0.75 / power(1.5, 1.5)) - CASE WHEN "customers"."city" = 'Montréal' THEN 1 ELSE 0 END) * 0.5))) > "customers"."state" THEN 3 WHEN (((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) >= (((CAST((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) AS REAL) / (((0.75 / power(1.5, 1.5)) - CASE WHEN "customers"."city" = 'Montréal' THEN 1 ELSE 0 END) * 0.5)) * 3) * (((1 - CASE WHEN "customers"."state" > 'ON' THEN 3 ELSE 0 END) * ((1 - CASE WHEN "customers"."state" > 'ON' THEN 3 ELSE 0 END) / CASE WHEN "customers"."city" = 'Montréal' THEN 1 ELSE 0 END)) * 0.2)) THEN 3 ELSE 0 END AS "o6" FROM "customers" AS "customers" WHERE (((((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) * 10) * 0.2) * 0.2) * ((((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) * 10) * 0.2) * 0.2)) = (((((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) * 10) * 0.2) * 0.2) * ((((((((((0.75 / power(1.5, 1.5)) / (CAST(0 AS REAL) / 2)) * (1 - (CAST(2 AS REAL) / 0.2))) / 10) * 0.1) * 2) / 2) * 10) * 0.2) * 0.2))
```

- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` case/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` case/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `-` derived/derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## store_1-9 (attempt 130)

```sql
SELECT "albums"."title" AS "o0", "albums"."artist_id" AS "o1", "albums"."id" AS "o2", 1 AS "o3" FROM "albums" AS "albums" WHERE NOT ("albums"."artist_id" IS NULL) ORDER BY "albums"."title" DESC
```


## store_1-10 (attempt 117)

```sql
SELECT "playlist_tracks"."playlist_id" AS "o0", (1 - ((CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0)) * ((CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0)) / (CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0))))) AS "o1", ((CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0)) * ((CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0)) / (CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0)))) AS "o2", ((CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0)) / (CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END + ((CAST(CASE WHEN "playlist_tracks"."playlist_id" = 13 THEN 1 ELSE 0 END AS REAL) / 1.5) + 0))) AS "o3" FROM "playlist_tracks" AS "playlist_tracks"
```

- `/` derived/derived: unknown (equal operands)
- `+` case/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)

## store_1-11 (attempt 10)

```sql
SELECT "tracks"."genre_id" AS "o0", coalesce((1 - (("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5)))), 0) AS "o1", (1 - (("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5)))) AS "o2", CAST(((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5) AS REAL) AS "o3", coalesce("tracks"."media_type_id", 0) AS "o4", RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) AS "o5", round(((0.2 / CAST((("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5))) AS REAL)) / CAST((0.2 / CAST((("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5))) AS REAL)) AS REAL)), 2) AS "o6", ((CAST((("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5))) AS REAL) * ("tracks"."milliseconds" * 3)) / 0.5) AS "o7", power((((CAST((("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5))) AS REAL) * ("tracks"."milliseconds" * 3)) / 0.5) - ((CAST((("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5))) AS REAL) * ("tracks"."milliseconds" * 3)) / 0.5)), 1.5) AS "o8", CASE WHEN (RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) < "tracks"."unit_price" AND "tracks"."unit_price" > 0.99 AND ((CAST((("tracks"."bytes" / 8107896) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) + ((CASE WHEN NOT ("tracks"."milliseconds" IS NULL) THEN 1 WHEN "tracks"."genre_id" >= 3 THEN 2 WHEN ("tracks"."genre_id" > 1 AND "tracks"."genre_id" > 3 AND "tracks"."bytes" = 534343985) THEN 4 ELSE 2 END * 3) * 1.5))) AS REAL) * ("tracks"."milliseconds" * 3)) / 0.5) = ((sqrt((RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) * 10)) - sqrt((RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) * 10))) * ((sqrt((RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) * 10)) / (sqrt((RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) * 10)) - sqrt((RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) * 10)))) * 3))) THEN 2 WHEN RANK() OVER (PARTITION BY "tracks"."media_type_id" ORDER BY "tracks"."genre_id" DESC) = "tracks"."name" THEN 1 ELSE 0 END AS "o9" FROM "tracks" AS "tracks" ORDER BY "tracks"."name" DESC
```

- `*` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `-` function/function: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)

## store_1-12 (attempt 1)

```sql
SELECT "genres"."id" AS "o0", coalesce((((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) + (((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1))) - ((((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1)) * 0.25)), 0) AS "o1", (((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1)) AS "o2", (1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) AS "o3", (((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) + (((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1))) - ((((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1)) * 0.25)) AS "o4", (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) AS "o5", CASE WHEN ((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) > 0.0 AND (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) = (((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1) - (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)))) THEN 1 WHEN (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) = (1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) THEN ((((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) - ((((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) + ((CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END / 3) * (CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5))) + ((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) * 0.1)) * 0.25)) WHEN (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) > ((CAST((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) AS REAL) / CAST((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) AS REAL)) * ((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) * (1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))))) THEN 3 WHEN ((1 - ((((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))) / (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))) > 0.0 AND CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END < CASE WHEN (((power(1.5, 2) / 10) / 0.5) * 0.1) != 0.03 THEN 1 WHEN "genres"."id" > 7 THEN 1 ELSE 0 END AND (CAST((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) AS REAL) / CAST((CASE WHEN (power(1.5, 2) / 10) = 0.15 THEN 4 WHEN "genres"."id" >= 13 THEN 2 WHEN ((((power(1.5, 2) / 10) / 2) / 2) >= 0.04 AND "genres"."id" > 19) THEN 10 WHEN (power(1.5, 2) / 10) > 0.15 THEN 10 ELSE 0 END / 0.5) AS REAL)) != ((0.75 / CAST((CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5) AS REAL)) * (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) * ((CAST((1 - (((power(1.5, 2) / 10) / 2) / 2)) AS REAL) * 5) / (((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)))))) THEN 5 ELSE 0 END AS "o6" FROM "genres" AS "genres" WHERE ((((((CASE WHEN ((((power(1.5, 2) / 0.2) / 1.5) * 3) * (((round(1, 2) / 10) + 0.1) + 0.2)) > 6.0 THEN 10 WHEN ((((power(1.5, 2) / 0.2) / 1.5) * 3) * (((round(1, 2) / 10) + 0.1) + 0.2)) = 6.0 THEN 5 WHEN (round(CAST(round(CAST(0 AS REAL), 2) AS REAL), 2) * CASE WHEN (coalesce(0, 0) * 0.75) >= 0.0 THEN 1 ELSE 0 END) < (coalesce(0, 0) * 0.75) THEN 2 WHEN (round(CAST(round(CAST(0 AS REAL), 2) AS REAL), 2) * CASE WHEN (coalesce(0, 0) * 0.75) >= 0.0 THEN 1 ELSE 0 END) > round(CAST(round(CAST(0 AS REAL), 2) AS REAL), 2) THEN 5 ELSE 0 END * 5) / 2) / 0.5) + 0) * (1 - (((CASE WHEN (CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL) / CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL)) = (CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL) / CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL)) THEN 1 ELSE 1 END + CASE WHEN coalesce(CAST(round(1, 2) AS REAL), 0) = coalesce(CAST(round(1, 2) AS REAL), 0) THEN 10 ELSE 1 END) / 0.25) * round(((((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) * (((1 - ((power(1.5, 2) / 10) / 0.5)) + (CAST(((power(1.5, 2) / 10) / 0.5) AS INTEGER) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END)) * (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))), 2)))) = (((((CASE WHEN ((((power(1.5, 2) / 0.2) / 1.5) * 3) * (((round(1, 2) / 10) + 0.1) + 0.2)) > 6.0 THEN 10 WHEN ((((power(1.5, 2) / 0.2) / 1.5) * 3) * (((round(1, 2) / 10) + 0.1) + 0.2)) = 6.0 THEN 5 WHEN (round(CAST(round(CAST(0 AS REAL), 2) AS REAL), 2) * CASE WHEN (coalesce(0, 0) * 0.75) >= 0.0 THEN 1 ELSE 0 END) < (coalesce(0, 0) * 0.75) THEN 2 WHEN (round(CAST(round(CAST(0 AS REAL), 2) AS REAL), 2) * CASE WHEN (coalesce(0, 0) * 0.75) >= 0.0 THEN 1 ELSE 0 END) > round(CAST(round(CAST(0 AS REAL), 2) AS REAL), 2) THEN 5 ELSE 0 END * 5) / 2) / 0.5) + 0) * (1 - (((CASE WHEN (CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL) / CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL)) = (CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL) / CAST(coalesce(CAST(round(1, 2) AS REAL), 0) AS REAL)) THEN 1 ELSE 1 END + CASE WHEN coalesce(CAST(round(1, 2) AS REAL), 0) = coalesce(CAST(round(1, 2) AS REAL), 0) THEN 10 ELSE 1 END) / 0.25) * round(((((CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END / 2) / 0.25) / ((CAST(CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END AS REAL) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END) / 5)) * (((1 - ((power(1.5, 2) / 10) / 0.5)) + (CAST(((power(1.5, 2) / 10) / 0.5) AS INTEGER) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END)) * (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2))))), 2)))) AND NOT ((((1 - ((power(1.5, 2) / 10) / 0.5)) + (CAST(((power(1.5, 2) / 10) / 0.5) AS INTEGER) / CASE WHEN coalesce(0, 0) = 0 THEN 3 ELSE 1 END)) * (((((power(1.5, 2) / 10) / 0.5) * 0.1) * 5) * (1 - (((power(1.5, 2) / 10) / 2) / 2)))) IS NULL))
```

- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` case/case: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `*` derived/derived: unknown
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `-` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `/` case/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` case/case: unknown
- `/` constant-derived: unknown (equal operands)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` parameter REFERENCE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## store_1-13 (attempt 182)

```sql
SELECT "tracks"."media_type_id" AS "o0", "invoice_lines"."unit_price" AS "o1", "invoice_lines"."id" AS "o2", log(10, "tracks"."bytes") AS "o3", "tracks"."bytes" AS "o4" FROM "genres" AS "genres" INNER JOIN "tracks" AS "tracks" ON "genres"."id" = "tracks"."genre_id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "tracks"."id" = "invoice_lines"."track_id" ORDER BY "tracks"."bytes" DESC
```


## store_1-14 (attempt 170)

```sql
SELECT "media_types"."id" AS "o0", "genres"."name" AS "o1", "tracks"."milliseconds" AS "o2", "tracks"."bytes" AS "o3", ((("tracks"."milliseconds" * 2) * ("tracks"."milliseconds" / 255634)) / CAST((("tracks"."milliseconds" * 2) * ("tracks"."milliseconds" / 255634)) AS REAL)) AS "o4" FROM "genres" AS "genres" INNER JOIN "tracks" AS "tracks" ON "genres"."id" = "tracks"."genre_id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id"
```

- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## store_1-15 (attempt 56)

```sql
SELECT "customers"."email" AS "o0", "invoices"."billing_country" AS "o1", AVG((coalesce(CAST(log(10, "tracks"."bytes") AS REAL), 0) - "employees"."birth_date")) FILTER (WHERE (coalesce(CAST(log(10, "tracks"."bytes") AS REAL), 0) - "employees"."birth_date") = "employees"."address") AS "o2" FROM "invoices" AS "invoices" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id" LEFT JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "tracks" AS "tracks" ON "invoice_lines"."track_id" = "tracks"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "playlist_tracks" AS "playlist_tracks" ON "tracks"."id" = "playlist_tracks"."track_id" GROUP BY "customers"."email", "invoices"."billing_country" ORDER BY "invoices"."billing_country" DESC
```

- `-` column/function: unknown

## store_1-16 (attempt 112)

```sql
WITH "s32" AS (SELECT "customers"."phone" AS "o0", abs(((round(CAST(((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1))) AS INTEGER), 2) - round(CAST(((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1))) AS INTEGER), 2)) + (1 - ((round(CAST(((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1))) AS INTEGER), 2) - round(CAST(((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1))) AS INTEGER), 2)) / round(CAST(((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1))) AS INTEGER), 2))))) AS "o1" FROM "invoices" AS "invoices" LEFT JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id" WHERE (NOT ("customers"."email" IS NULL) AND (((coalesce((((("invoices"."total" / 3.96) + 1.0) * 0.1) * (((("invoices"."total" / 3.96) + 1.0) * 0.75) * 0.25)), 0) / 5) * (((((round(((("invoices"."total" / 3.96) / 5) / 0.5), 2) + (((1.58 - (("invoices"."total" + 3.96) / 5)) * (1 - (("invoices"."total" + "invoices"."total") / 0.75))) / 10)) * 3) * (((1 - ((("invoices"."total" + "invoices"."total") / 0.75) / 3)) * (1 - ((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1))))) * 3)) + (CASE WHEN ((("invoices"."total" + "invoices"."total") / 0.75) / 3) > 3.52 THEN 3 WHEN (1 - ((round(CAST("invoices"."total" AS REAL), 2) / 3.96) + (79.2 - (("invoices"."total" + 3.96) / 0.1)))) >= -0.0 THEN 3 ELSE 0 END * 0.75)) + 0)) * CASE WHEN "invoices"."billing_country" = "invoices"."invoice_date" THEN 2 ELSE 0 END) > ((round(((("invoices"."total" / 3.96) / 5) / 0.5), 2) + (((1.58 - (("invoices"."total" + 3.96) / 5)) * (1 - (("invoices"."total" + "invoices"."total") / 0.75))) / 10)) * 3)) ORDER BY "customers"."phone" DESC LIMIT 100) SELECT "s32"."o1" AS "o0", "s32"."o0" AS "o1", CASE WHEN "s32"."o0" = '+55 (12) 3923-5555' THEN 1 WHEN "s32"."o0" > '+1 (801) 531-7272' THEN 1 ELSE ("s32"."o1" / abs("s32"."o1")) END AS "o2" FROM "s32" AS "s32" ORDER BY abs("s32"."o1") DESC
```

- `+` constant-derived: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `+` derived/derived: plausible (model)
- `-` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` column/column: plausible (model)
- `-` parameter REFERENCE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` case/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` step output/step output: unknown

## store_1-17 (attempt 47)

```sql
WITH "s16" AS (SELECT "customers"."last_name" AS "o0", (((CAST((CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) AS REAL) / (CAST(round(2, 2) AS REAL) * 0.5)) * 5) * CASE WHEN (CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) > "customers"."first_name" THEN 1 END) AS "o1", "customers"."fax" AS "o2", "customers"."first_name" AS "o3", coalesce((((CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) * 0.1) - ((round(CAST(sqrt(round(2, 2)) AS REAL), 2) + coalesce((round(round(CAST(sqrt(round(2, 2)) AS REAL), 2), 2) + coalesce(CAST(round(2, 2) AS REAL), 0)), 1)) * ((round(CAST(sqrt(round(2, 2)) AS REAL), 2) + coalesce((round(round(CAST(sqrt(round(2, 2)) AS REAL), 2), 2) + coalesce(CAST(round(2, 2) AS REAL), 0)), 1)) / round(CAST(sqrt(round(2, 2)) AS REAL), 2)))), 1) AS "o4", (CAST((((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5)) AS INTEGER) / (((((round(2, 2) + sqrt(round(2, 2))) / 0.25) * 3) * 0.5) + (CAST(round(2, 2) AS REAL) * 0.5))) AS "o5", CASE WHEN coalesce((round(round(CAST(sqrt(round(2, 2)) AS REAL), 2), 2) + coalesce(CAST(round(2, 2) AS REAL), 0)), 1) > (((((round(2, 2) + sqrt(round(2, 2))) * 5) + 20.0) * (((((round(2, 2) + sqrt(round(2, 2))) * 5) + 20.0) / (((round(2, 2) + sqrt(round(2, 2))) * 5) + 20.0)) * 0.75)) + CASE WHEN "customers"."company" = 'Riotur' THEN 2 ELSE 1 END) THEN 1 WHEN "customers"."first_name" > 'Lucas' THEN 3 ELSE 0 END AS "o6", (((((round(2, 2) + sqrt(round(2, 2))) * 5) + 20.0) * (((((round(2, 2) + sqrt(round(2, 2))) * 5) + 20.0) / (((round(2, 2) + sqrt(round(2, 2))) * 5) + 20.0)) * 0.75)) + CASE WHEN "customers"."company" = 'Riotur' THEN 2 ELSE 1 END) AS "o7", round(CAST(CASE WHEN "customers"."company" = 'Riotur' THEN 2 ELSE 1 END AS INTEGER), 0) AS "o8" FROM "customers" AS "customers" WHERE NOT ("customers"."postal_code" IS NULL) ORDER BY CASE WHEN "customers"."company" = 'Riotur' THEN 2 ELSE 1 END DESC LIMIT 50), "s25" AS (SELECT "s16"."o1" AS "o0", SUM(((((0.2 / (((CAST("s16"."o1" AS REAL) / "s16"."o1") + 0) + 0)) * 5) * CAST("s16"."o1" AS INTEGER)) - (round((("s16"."o8" * 3) / 2), 2) * 0.25))) AS "o1", AVG(((log(10, round(CAST("s16"."o1" AS REAL), 2)) * 0.1) + sqrt(round(CAST("s16"."o1" AS REAL), 2)))) AS "o2" FROM "s16" AS "s16" GROUP BY "s16"."o1") SELECT COUNT(*) AS "o0", COUNT(*) FILTER (WHERE ((((((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) * 0.5) * 10) - ("s25"."o1" * 3)) = ((((((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) * 0.5) * 10) - ("s25"."o1" * 3))) AS "o1", AVG(CASE WHEN (((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) > ((((((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) * 0.5) * 10) - ("s25"."o1" * 3)) THEN (((((((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) * 0.5) * 10) - ("s25"."o1" * 3)) - ((((((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) * 0.5) * 10) - ("s25"."o1" * 3))) WHEN ("s25"."o1" * 3) = (0.25 / ((((CAST(("s25"."o1" * 3) AS REAL) * 5) + ((CAST(("s25"."o1" * 3) AS REAL) * 5) - CASE WHEN (("s25"."o0" / "s25"."o0") + 0) = (0.25 / (1 - "s25"."o1")) THEN 1 ELSE 0 END)) * 0.1) / (((((CAST((0.25 / (1 - "s25"."o1")) AS REAL) * 3) * (CAST((0.25 / (1 - "s25"."o1")) AS REAL) / 0.2)) * 0.2) + (CAST((0.25 / (1 - "s25"."o1")) AS REAL) * 3)) * 0.5))) THEN 1 ELSE 4 END) AS "o2", AVG(((round((1 - round(CAST("s25"."o1" AS INTEGER), 2)), 2) * 1.5) * round((round((CAST((0.25 / (1 - "s25"."o1")) AS REAL) / 0.2), 2) * 0.5), 2))) AS "o3" FROM "s25" AS "s25" WHERE "s25"."o2" = ((((((("s25"."o0" / "s25"."o0") + 0) + CASE WHEN (("s25"."o0" / "s25"."o0") + 0) > (round(("s25"."o0" / "s25"."o0"), 2) * 0.5) THEN 1 ELSE 0 END) * 0.2) * 0.5) * 10) - ("s25"."o1" * 3))
```

- `+` case/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `+` constant-derived: unknown (a constant)
- `/` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `/` derived/function: unknown
- `+` derived/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `+` derived/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/step output: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` step output/step output: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `-` case/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` step output/step output: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown (equal operands)
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)

## store_1-18 (attempt 35)

```sql
SELECT DISTINCT "customers"."last_name" AS "o0", "employees"."birth_date" AS "o1", CASE WHEN "employees"."birth_date" = '1970-05-29 00:00:00' THEN 1 ELSE 0 END AS "o2", abs(((CAST(CASE WHEN "employees"."birth_date" = '1970-05-29 00:00:00' THEN 1 ELSE 0 END AS REAL) / (("invoices"."total" * 5) * 1.5)) * 0.5)) AS "o3" FROM "invoices" AS "invoices" LEFT JOIN "customers" AS "customers" ON "invoices"."customer_id" = "customers"."id" INNER JOIN "employees" AS "employees" ON "customers"."phone" = "employees"."phone" INNER JOIN "invoice_lines" AS "invoice_lines" ON "invoices"."id" = "invoice_lines"."invoice_id" WHERE ("employees"."address" > '11120 Jasper Ave NW' AND "customers"."fax" > '+1 (212) 221-4679' AND NOT ("employees"."birth_date" IS NULL)) ORDER BY "employees"."birth_date" DESC LIMIT 100
```

- `*` parameter WEIGHT: unknown (a constant)
- `/` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)

## store_1-19 (attempt 148)

```sql
SELECT "tracks"."media_type_id" AS "o0", CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END AS "o1", (CAST((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) AS REAL) / CAST(((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) AS REAL)) AS "o2", CAST(round(((((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) / 2) * 1000), 1) AS REAL) AS "o3", round((round(((((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) / 2) * 1000), 1) * CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END), 2) AS "o4", ((round(((((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) / 2) * 1000), 1) * CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END) - CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END) AS "o5", "tracks"."name" AS "o6" FROM "albums" AS "albums" LEFT JOIN "tracks" AS "tracks" ON "albums"."id" = "tracks"."album_id" INNER JOIN "media_types" AS "media_types" ON "tracks"."media_type_id" = "media_types"."id" WHERE (("tracks"."bytes" / "tracks"."milliseconds") > (round(((((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) / 2) * 1000), 1) * CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END) AND (round(((((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) / 2) * 1000), 1) * CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END) = (round(((((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) / 2) * 1000), 1) * CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END) AND (CAST((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) AS REAL) / CAST(((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) AS REAL)) = CASE WHEN (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) < (255634 - "tracks"."milliseconds") AND ((((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds")) / 5) = (((round(CAST(("tracks"."bytes" / "tracks"."milliseconds") AS REAL), 2) + 0) * (((round(CAST("tracks"."milliseconds" AS REAL), 2) / 255634) * 2) * (((1.0 - ("tracks"."milliseconds" / 255634)) * (1 - (0.2 / "tracks"."milliseconds"))) * 1.5))) * (255634 - "tracks"."milliseconds"))) THEN 1 WHEN "tracks"."name" = 'Collision' THEN 1 ELSE 1 END)
```

- `-` case/derived: unknown
- `*` derived/derived: unknown
- `-` parameter REFERENCE: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` column/column: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `*` case/derived: unknown
- `*` parameter CONVERT: plausible (model)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown

## store_1-20 (attempt 83)

```sql
WITH "s1" AS (SELECT "genres"."name" AS "o0", "tracks"."milliseconds" AS "o1", "tracks"."bytes" AS "o2" FROM "genres" AS "genres" INNER JOIN "tracks" AS "tracks" ON "genres"."id" = "tracks"."genre_id" INNER JOIN "playlist_tracks" AS "playlist_tracks" ON "tracks"."id" = "playlist_tracks"."track_id" WHERE (CAST("tracks"."milliseconds" AS REAL) > 207229 AND "tracks"."bytes" > 8107896) ORDER BY "tracks"."milliseconds" DESC LIMIT 5) SELECT "s1"."o1" AS "o0", "s1"."o2" AS "o1", (((1 - CAST(("s1"."o2" / 8110000.0) AS INTEGER)) * ((1 - CASE WHEN ("s1"."o2" / 8110000.0) BETWEEN 1.0 AND 1.0 THEN 1 ELSE 1 END) * round(CAST(CASE WHEN ("s1"."o2" / 8110000.0) BETWEEN 1.0 AND 1.0 THEN 1 ELSE 1 END AS REAL), 2))) - (((((CAST((1 - CAST(("s1"."o2" / 8110000.0) AS INTEGER)) AS REAL) * 3) + ((CAST((CAST((1 - CAST(("s1"."o2" / 8110000.0) AS INTEGER)) AS REAL) * 3) AS REAL) / 10) + 0)) + ((CAST((CAST((1 - CAST(("s1"."o2" / 8110000.0) AS INTEGER)) AS REAL) * 3) AS REAL) * 0.5) + (1 - CASE WHEN "s1"."o1" = 189675 THEN 5 WHEN "s1"."o2" = 555244214 THEN 10 ELSE 1 END))) * (round(CAST(round(CAST(CASE WHEN ("s1"."o2" / 8110000.0) BETWEEN 1.0 AND 1.0 THEN 1 ELSE 1 END AS REAL), 2) AS REAL), 2) * 5)) * (1 - CASE WHEN ("s1"."o2" IN (FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC), CASE WHEN (FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC) > FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC) AND FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC) > ("s1"."o1" / "s1"."o2") AND "s1"."o2" < 6342021) THEN 1 WHEN ("s1"."o1" / "s1"."o2") > 0.03 THEN 5 WHEN ("s1"."o1" / "s1"."o2") = 0.03 THEN 1 WHEN ("s1"."o1" / "s1"."o2") = "s1"."o2" THEN (((1 - coalesce((CAST("s1"."o1" AS REAL) / 256000.0), 0)) * ("s1"."o2" / 8110000.0)) / 0.5) ELSE 0 END) AND CASE WHEN (FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC) > FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC) AND FIRST_VALUE(("s1"."o2" / 8110000.0)) OVER (ORDER BY "s1"."o1" DESC) > ("s1"."o1" / "s1"."o2") AND "s1"."o2" < 6342021) THEN 1 WHEN ("s1"."o1" / "s1"."o2") > 0.03 THEN 5 WHEN ("s1"."o1" / "s1"."o2") = 0.03 THEN 1 WHEN ("s1"."o1" / "s1"."o2") = "s1"."o2" THEN (((1 - coalesce((CAST("s1"."o1" AS REAL) / 256000.0), 0)) * ("s1"."o2" / 8110000.0)) / 0.5) ELSE 0 END = "s1"."o1") THEN 0 WHEN "s1"."o2" > 6342021 THEN 2 ELSE 0 END))) AS "o2" FROM "s1" AS "s1" ORDER BY "s1"."o2" DESC
```

- `-` derived/derived: unknown
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter REFERENCE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter REFERENCE: unknown (a constant)
- `/` step output/step output: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: plausible (model)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` case/derived: unknown
- `-` parameter WHOLE: strong (rule)

