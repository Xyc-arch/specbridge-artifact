# toxicology: 20 random delivered programs

## toxicology-1 (attempt 76)

```sql
WITH "s1" AS (SELECT "bond"."bond_id" AS "o0", "atom"."atom_id" AS "o1" FROM "connected" AS "connected" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" INNER JOIN "bond" AS "bond" ON "connected"."bond_id" = "bond"."bond_id" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" ORDER BY "atom"."atom_id" DESC LIMIT 100), "s2" AS (SELECT "connected"."atom_id2" AS "o0", "atom"."molecule_id" AS "o1" FROM "connected" AS "connected" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" WHERE ("atom"."element" > 'br' AND "atom"."element" < 'y') ORDER BY "atom"."molecule_id" DESC LIMIT 10) SELECT "s2"."o1" AS "o0", "s1"."o1" AS "o1", (((1 - CAST(((round(CAST(((CAST(round(1, 2) AS REAL) / round(1, 2)) / 0.1) AS REAL), 2) * 1.5) / 5) AS INTEGER)) + ((CAST(((round(CAST(((CAST(round(1, 2) AS REAL) / round(1, 2)) / 0.1) AS REAL), 2) * 1.5) / 5) AS REAL) / 0.1) + (round(CAST(((CAST(round(1, 2) AS REAL) / round(1, 2)) / 0.1) AS REAL), 2) - (round(CAST(((CAST(round(1, 2) AS REAL) / round(1, 2)) / 0.1) AS REAL), 2) * 1.5)))) - (1 - (((CASE WHEN ((CAST(round(1, 2) AS REAL) / round(1, 2)) > ((CAST(round(1, 2) AS INTEGER) / 0.5) / 0.2) AND ((CAST(round(1, 2) AS INTEGER) / 0.5) / 0.2) = ((((CAST(2 AS REAL) / 0.5) * (1 - round(1, 2))) + ((CAST(2 AS REAL) / 2) + 0)) * 0.5) AND ((CAST(2 AS REAL) / 0.5) * (1 - round(1, 2))) = ((((round(2, 2) * 5) + (round(2, 1) + 2.0)) * ((round(2, 1) + 2.0) / (coalesce(0, 0) * 1.5))) * 0.25) AND "s1"."o1" > 'TR001_11' AND "s1"."o1" > 'TR001_17') THEN 2 WHEN "s1"."o1" = 'TR002_1' THEN 10 ELSE 0 END / 0.75) / 2) + (round(CAST(round(2, 2) AS REAL), 2) * 0.5)))) AS "o2" FROM "s2" AS "s2" INNER JOIN "s1" AS "s1" ON "s1"."o1" = "s2"."o0"
```

- `-` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `-` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)

## toxicology-2 (attempt 158)

```sql
SELECT "atom"."atom_id" AS "o0", round((((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))) * ((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) + (((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) * 3) + ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * 0.1)))), 0) AS "o1", (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))))) AS "o2", AVG((CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) OVER (ORDER BY (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))))) DESC) AS "o3" FROM "atom" AS "atom" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" INNER JOIN "bond" AS "bond" ON "molecule"."molecule_id" = "bond"."molecule_id" WHERE (NOT (CAST((((((CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END * 100) * (CASE WHEN "molecule"."molecule_id" > 'TR036' THEN 2 WHEN "molecule"."molecule_id" < 'TR051' THEN 2 WHEN "molecule"."molecule_id" > 'TR055' THEN 1 WHEN CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END = "molecule"."molecule_id" THEN 4 ELSE 0 END + CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)) * 5) * ((CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END) + 0)) * (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3)) AS REAL) IS NULL) AND CASE WHEN (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3) > (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3) THEN 4 WHEN (((((CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END * 100) * (CASE WHEN "molecule"."molecule_id" > 'TR036' THEN 2 WHEN "molecule"."molecule_id" < 'TR051' THEN 2 WHEN "molecule"."molecule_id" > 'TR055' THEN 1 WHEN CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END = "molecule"."molecule_id" THEN 4 ELSE 0 END + CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)) * 5) * ((CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END) + 0)) * (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3)) > CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END THEN 5 WHEN "molecule"."label" < '+' THEN 5 ELSE 1 END = (((((CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END * 100) * (CASE WHEN "molecule"."molecule_id" > 'TR036' THEN 2 WHEN "molecule"."molecule_id" < 'TR051' THEN 2 WHEN "molecule"."molecule_id" > 'TR055' THEN 1 WHEN CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END = "molecule"."molecule_id" THEN 4 ELSE 0 END + CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)) * 5) * ((CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END) + 0)) * (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3)) AND CASE WHEN (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3) > (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3) THEN 4 WHEN (((((CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END * 100) * (CASE WHEN "molecule"."molecule_id" > 'TR036' THEN 2 WHEN "molecule"."molecule_id" < 'TR051' THEN 2 WHEN "molecule"."molecule_id" > 'TR055' THEN 1 WHEN CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END = "molecule"."molecule_id" THEN 4 ELSE 0 END + CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)) * 5) * ((CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END) + 0)) * (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3)) > CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END THEN 5 WHEN "molecule"."label" < '+' THEN 5 ELSE 1 END < ((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) AND CASE WHEN (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3) > (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3) THEN 4 WHEN (((((CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END * 100) * (CASE WHEN "molecule"."molecule_id" > 'TR036' THEN 2 WHEN "molecule"."molecule_id" < 'TR051' THEN 2 WHEN "molecule"."molecule_id" > 'TR055' THEN 1 WHEN CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END = "molecule"."molecule_id" THEN 4 ELSE 0 END + CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)) * 5) * ((CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END) + 0)) * (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3)) > CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END THEN 5 WHEN "molecule"."label" < '+' THEN 5 ELSE 1 END = (CAST((((((CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END * 100) * (CASE WHEN "molecule"."molecule_id" > 'TR036' THEN 2 WHEN "molecule"."molecule_id" < 'TR051' THEN 2 WHEN "molecule"."molecule_id" > 'TR055' THEN 1 WHEN CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END = "molecule"."molecule_id" THEN 4 ELSE 0 END + CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)) * 5) * ((CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END) + 0)) * (((CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END / CASE WHEN "atom"."element" BETWEEN (SELECT "bond"."bond_id" AS "o0" FROM "bond" AS "bond") AND "molecule"."molecule_id" THEN 1 ELSE 0 END) * 2) * 3)) AS REAL) * 3)) ORDER BY round((((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))) * ((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) + (((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) * 3) + ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * 0.1)))), 0) ASC LIMIT 100
```

- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `*` constant-derived: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` case/case: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` case/case: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` case/case: unknown
- `*` parameter CONVERT: strong (rule)

## toxicology-3 (attempt 144)

```sql
SELECT "bond"."bond_type" AS "o0", CURRENT_DATE AS "o1" FROM "bond" AS "bond" INNER JOIN "connected" AS "connected" ON "bond"."bond_id" = "connected"."bond_id" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" INNER JOIN "molecule" AS "molecule" ON "bond"."molecule_id" = "molecule"."molecule_id" WHERE (NOT ("connected"."atom_id2" IS NULL) AND "connected"."atom_id2" = 'TR502_1') ORDER BY CURRENT_DATE DESC
```


## toxicology-4 (attempt 40)

```sql
SELECT "connected"."atom_id" AS "o0", "connected"."bond_id" AS "o1", coalesce(((1 - (1 - CAST((CASE WHEN "connected"."bond_id" = 'TR496_9_10' THEN 1 ELSE 1 END * 10) AS INTEGER))) + (1.5 / CAST((1 - (1 - CAST((CASE WHEN "connected"."bond_id" = 'TR496_9_10' THEN 1 ELSE 1 END * 10) AS INTEGER))) AS REAL))), 0) AS "o2" FROM "connected" AS "connected" ORDER BY "connected"."bond_id" DESC, (1 - (1 - CAST((CASE WHEN "connected"."bond_id" = 'TR496_9_10' THEN 1 ELSE 1 END * 10) AS INTEGER))) DESC
```

- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)

## toxicology-5 (attempt 107)

```sql
SELECT "molecule"."molecule_id" AS "o0", "atom"."molecule_id" AS "o1", PERCENT_RANK() OVER (ORDER BY "molecule"."molecule_id" DESC) AS "o2" FROM "atom" AS "atom" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" WHERE ("molecule"."label" = '-' AND ("atom"."element" = 'f' OR "atom"."element" LIKE 'zn') AND NOT ("atom"."molecule_id" IS NULL)) ORDER BY PERCENT_RANK() OVER (ORDER BY "molecule"."molecule_id" DESC) DESC, "molecule"."molecule_id" DESC
```


## toxicology-6 (attempt 160)

```sql
SELECT "atom"."atom_id" AS "o0", "atom"."element" AS "o1", "connected"."bond_id" AS "o2", "connected"."atom_id" AS "o3", CASE WHEN (CAST("connected"."bond_id" AS REAL) = 'TR496_8_33' OR "atom"."element" = 'i') THEN 4 ELSE 10 END AS "o4" FROM "connected" AS "connected" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" ORDER BY CASE WHEN (CAST("connected"."bond_id" AS REAL) = 'TR496_8_33' OR "atom"."element" = 'i') THEN 4 ELSE 10 END DESC LIMIT 100
```


## toxicology-7 (attempt 129)

```sql
SELECT "atom"."atom_id" AS "o0", AVG(round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2)) AS "o1", AVG(round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2)) FILTER (WHERE (((((((((round(2, 2) / 0.25) / 10) * 0.1) + 0.08) / ((((round(2, 1) + 2.0) * 2) * ((round(2, 1) * 1.5) / 2)) * 0.75)) + (CASE WHEN ((CAST(2 AS REAL) * 2) <= (CAST(2 AS REAL) * 2) AND (round(2, 2) - round(2, 1)) = 0) THEN 0 WHEN "atom"."element" >= 's' THEN 1 WHEN ((CAST(2 AS REAL) * 2) > "atom"."element" AND (sqrt(0) * 5) = 0) THEN 10 ELSE 0 END + CASE WHEN (sqrt(0) * 5) >= 0 THEN 4 WHEN (sqrt(0) * 5) = 0 THEN 10 ELSE 0 END)) + 0) - (1 - power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5))) / 0.1) < ((((((((round(2, 2) / 0.25) / 10) * 0.1) + 0.08) / ((((round(2, 1) + 2.0) * 2) * ((round(2, 1) * 1.5) / 2)) * 0.75)) + (CASE WHEN ((CAST(2 AS REAL) * 2) <= (CAST(2 AS REAL) * 2) AND (round(2, 2) - round(2, 1)) = 0) THEN 0 WHEN "atom"."element" >= 's' THEN 1 WHEN ((CAST(2 AS REAL) * 2) > "atom"."element" AND (sqrt(0) * 5) = 0) THEN 10 ELSE 0 END + CASE WHEN (sqrt(0) * 5) >= 0 THEN 4 WHEN (sqrt(0) * 5) = 0 THEN 10 ELSE 0 END)) + 0) - (1 - power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5)))) AS "o2", round(CAST(AVG(round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2)) AS REAL), 2) AS "o3", AVG((CAST(round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2) AS REAL) / (sqrt(0) * 5))) AS "o4", round(CAST(AVG((CAST(round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2) AS REAL) / (sqrt(0) * 5))) AS REAL), 2) AS "o5" FROM "atom" AS "atom" WHERE (round(CAST((((((((((round(2, 2) / 0.25) / 10) * 0.1) + 0.08) / ((((round(2, 1) + 2.0) * 2) * ((round(2, 1) * 1.5) / 2)) * 0.75)) + (CASE WHEN ((CAST(2 AS REAL) * 2) <= (CAST(2 AS REAL) * 2) AND (round(2, 2) - round(2, 1)) = 0) THEN 0 WHEN "atom"."element" >= 's' THEN 1 WHEN ((CAST(2 AS REAL) * 2) > "atom"."element" AND (sqrt(0) * 5) = 0) THEN 10 ELSE 0 END + CASE WHEN (sqrt(0) * 5) >= 0 THEN 4 WHEN (sqrt(0) * 5) = 0 THEN 10 ELSE 0 END)) + 0) - (1 - power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5))) / 0.1) AS INTEGER), 2) = CASE WHEN (sqrt(0) * 5) >= 0 THEN 4 WHEN (sqrt(0) * 5) = 0 THEN 10 ELSE 0 END AND round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2) = ((((((round(2, 2) / 0.25) / 10) * 0.1) + 0.08) / ((((round(2, 1) + 2.0) * 2) * ((round(2, 1) * 1.5) / 2)) * 0.75)) + (CASE WHEN ((CAST(2 AS REAL) * 2) <= (CAST(2 AS REAL) * 2) AND (round(2, 2) - round(2, 1)) = 0) THEN 0 WHEN "atom"."element" >= 's' THEN 1 WHEN ((CAST(2 AS REAL) * 2) > "atom"."element" AND (sqrt(0) * 5) = 0) THEN 10 ELSE 0 END + CASE WHEN (sqrt(0) * 5) >= 0 THEN 4 WHEN (sqrt(0) * 5) = 0 THEN 10 ELSE 0 END))) GROUP BY "atom"."atom_id" ORDER BY round(CAST(AVG((CAST(round(CAST(power(CAST((CAST(2 AS REAL) * 2) AS REAL), 1.5) AS REAL), 2) AS REAL) / (sqrt(0) * 5))) AS REAL), 2) DESC LIMIT 10
```

- `/` derived/function: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `+` case/case: unknown
- `-` constant-derived: unknown (a constant)
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `+` parameter REFERENCE: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## toxicology-8 (attempt 167)

```sql
SELECT "molecule"."molecule_id" AS "o0", "molecule"."label" AS "o1", CAST(((CAST(((CAST((((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.25) + ((CAST(round(2, 2) AS REAL) / 0.1) / 0.5)) AS REAL) / (((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.25) + ((CAST(round(2, 2) AS REAL) / 0.1) / 0.5))) * 2) AS REAL) / (((CAST((((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.25) + ((CAST(round(2, 2) AS REAL) / 0.1) / 0.5)) AS REAL) / (((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.25) + ((CAST(round(2, 2) AS REAL) / 0.1) / 0.5))) * 2) / ((CAST(round(2, 2) AS REAL) / 0.1) / 0.5))) * ((1 - ((CASE WHEN "molecule"."label" > '+' THEN 2 WHEN "molecule"."label" > '-' THEN 4 WHEN ("molecule"."label" > '+' OR (CAST(round(2, 2) AS REAL) / 0.1) >= ((0.2 / CAST(round(2, 2) AS REAL)) * (CAST(round(2, 2) AS REAL) / CAST(round(2, 2) AS REAL)))) THEN 4 ELSE 0 END / 3) + 0)) * 0.2)) AS REAL) AS "o2", ((1 - ((CASE WHEN "molecule"."label" > '+' THEN 2 WHEN "molecule"."label" > '-' THEN 4 WHEN ("molecule"."label" > '+' OR (CAST(round(2, 2) AS REAL) / 0.1) >= ((0.2 / CAST(round(2, 2) AS REAL)) * (CAST(round(2, 2) AS REAL) / CAST(round(2, 2) AS REAL)))) THEN 4 ELSE 0 END / 3) + 0)) * 0.2) AS "o3", NTILE(10) OVER (ORDER BY (CASE WHEN "molecule"."label" > '+' THEN 2 WHEN "molecule"."label" > '-' THEN 4 WHEN ("molecule"."label" > '+' OR (CAST(round(2, 2) AS REAL) / 0.1) >= ((0.2 / CAST(round(2, 2) AS REAL)) * (CAST(round(2, 2) AS REAL) / CAST(round(2, 2) AS REAL)))) THEN 4 ELSE 0 END / 3) DESC) AS "o4", 1 AS "o5", ((0.2 / CAST(round(2, 2) AS REAL)) * (CAST(round(2, 2) AS REAL) / CAST(round(2, 2) AS REAL))) AS "o6" FROM "molecule" AS "molecule"
```

- `*` constant-derived: unknown (a constant)
- `/` constant-derived: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)

## toxicology-9 (attempt 156)

```sql
SELECT "bond"."bond_id" AS "o0", "bond"."bond_type" AS "o1", coalesce((((1 - CAST((CASE WHEN "bond"."bond_type" > '#' THEN 10 WHEN "bond"."bond_type" = '-' THEN 2 WHEN "bond"."bond_type" < '-' THEN 2 WHEN "bond"."bond_type" > '=' THEN 1 ELSE 0 END * 2) AS REAL)) * (((CASE WHEN (CASE WHEN "bond"."bond_type" > '#' THEN 10 WHEN "bond"."bond_type" = '-' THEN 2 WHEN "bond"."bond_type" < '-' THEN 2 WHEN "bond"."bond_type" > '=' THEN 1 ELSE 0 END * 2) < (CASE WHEN "bond"."bond_type" > '#' THEN 10 WHEN "bond"."bond_type" = '-' THEN 2 WHEN "bond"."bond_type" < '-' THEN 2 WHEN "bond"."bond_type" > '=' THEN 1 ELSE 0 END * 0.75) THEN 1 ELSE 0 END / 0.1) / 10) * ((CASE WHEN ("bond"."bond_type" > '#' AND "bond"."bond_type" > '-') THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '#' THEN 10 WHEN "bond"."bond_type" = '-' THEN 2 WHEN "bond"."bond_type" < '-' THEN 2 WHEN "bond"."bond_type" > '=' THEN 1 ELSE 0 END * 2) = ((CASE WHEN "bond"."bond_type" > '#' THEN 10 WHEN "bond"."bond_type" = '-' THEN 2 WHEN "bond"."bond_type" < '-' THEN 2 WHEN "bond"."bond_type" > '=' THEN 1 ELSE 0 END * (CASE WHEN "bond"."bond_type" > '#' THEN 10 WHEN "bond"."bond_type" = '-' THEN 2 WHEN "bond"."bond_type" < '-' THEN 2 WHEN "bond"."bond_type" > '=' THEN 1 ELSE 0 END * 0.75)) - (((CAST(1 AS INTEGER) * 0.25) * (1 - AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC))) * (AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) * 2))) THEN 10 WHEN "bond"."bond_type" > '=' THEN 5 WHEN (((CAST(1 AS INTEGER) * 0.25) * (1 - AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC))) * (AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) * 2)) > ((1 - (AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) / AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC))) * 3) THEN 1 WHEN ((1 - (AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) / AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC))) * 3) = ((AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) / AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC)) * 0.2) THEN 5 END / 0.25) + (((AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) / AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC)) * 0.2) * (CAST((CAST(1 AS INTEGER) * 0.25) AS INTEGER) * 0.1))))) * CASE WHEN "bond"."bond_type" = '-' THEN 0 ELSE 0 END), 0) AS "o2", CASE WHEN "bond"."bond_type" = '-' THEN 0 ELSE 0 END AS "o3", ((AVG(2) OVER (PARTITION BY "bond"."bond_type" ORDER BY "bond"."bond_type" DESC) * 2) * 1.5) AS "o4" FROM "bond" AS "bond"
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` case/derived: unknown
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (equal operands)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `-` derived/derived: unknown
- `*` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter REFERENCE: unknown (a constant)

## toxicology-10 (attempt 19)

```sql
SELECT "molecule"."molecule_id" AS "o0", "atom"."atom_id" AS "o1", "connected"."atom_id2" AS "o2" FROM "atom" AS "atom" INNER JOIN "connected" AS "connected" ON "atom"."atom_id" = "connected"."atom_id2" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" INNER JOIN "bond" AS "bond" ON "connected"."bond_id" = "bond"."bond_id" ORDER BY "atom"."atom_id" DESC, "connected"."atom_id2" DESC
```


## toxicology-11 (attempt 8)

```sql
SELECT "atom"."molecule_id" AS "o0", "connected"."bond_id" AS "o1", "molecule"."label" AS "o2" FROM "connected" AS "connected" INNER JOIN "bond" AS "bond" ON "connected"."bond_id" = "bond"."bond_id" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" INNER JOIN "molecule" AS "molecule" ON "bond"."molecule_id" = "molecule"."molecule_id" ORDER BY "molecule"."label" ASC, "connected"."bond_id" DESC
```


## toxicology-12 (attempt 80)

```sql
SELECT "atom"."atom_id" AS "o0", "atom"."element" AS "o1", (((((CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5) / 0.1) + 0) * 0.1) - ((round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) + (CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5)) + 0)) AS "o2", ((round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) + (CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5)) + 0) AS "o3", CASE WHEN CAST((round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) + (CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5)) AS INTEGER) > (((round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) + (CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5)) + 0) / ((round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) + (CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5)) + 0)) THEN 4 ELSE 0 END AS "o4", round(CAST(((((CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5) / 0.1) + 0) * 0.1) AS REAL), 2) AS "o5", "molecule"."label" AS "o6" FROM "molecule" AS "molecule" INNER JOIN "atom" AS "atom" ON "molecule"."molecule_id" = "atom"."molecule_id" WHERE (((((CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5) / 0.1) + 0) * 0.1) - ((round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) + (CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5)) + 0)) < ((((CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5) / 0.1) + 0) * 0.1) ORDER BY round(CAST(((((CASE WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = ((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) THEN 10 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) = round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) THEN 2 WHEN round(CAST(((CAST(1.5 AS INTEGER) / 0.75) / (coalesce(0, 0) + 0)) AS REAL), 2) < coalesce(0, 0) THEN 10 ELSE 1 END * 1.5) / 0.1) + 0) * 0.1) AS REAL), 2) DESC
```

- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown (equal operands)
- `+` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `-` derived/derived: unknown

## toxicology-13 (attempt 146)

```sql
WITH "s1" AS (SELECT "molecule"."label" AS "o0", round(COUNT(*), 2) AS "o1" FROM "atom" AS "atom" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" WHERE "atom"."element" IN ((SELECT "connected"."atom_id" AS "o0" FROM "connected" AS "connected")) GROUP BY "molecule"."label"), "s2" AS (SELECT "bond"."bond_id" AS "o0", "bond"."bond_type" AS "o1", "molecule"."label" AS "o2" FROM "molecule" AS "molecule" INNER JOIN "bond" AS "bond" ON "molecule"."molecule_id" = "bond"."molecule_id" ORDER BY "molecule"."label" DESC LIMIT 100) SELECT "s1"."o1" AS "o0", abs((((((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) * coalesce(((CASE WHEN "s1"."o1" > (((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) / "s1"."o1") THEN 1 WHEN "s1"."o1" = "molecule"."label" THEN 5 ELSE 0 END / 0.25) * 0.5), 0)) * ((((CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 0.2) * (CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 3)) + (1 - CASE WHEN "s1"."o1" > (CAST("s1"."o1" AS INTEGER) - 0) THEN 5 ELSE 0 END)) * ((power(CAST((1 - CASE WHEN "s1"."o1" > (CAST("s1"."o1" AS INTEGER) - 0) THEN 5 ELSE 0 END) AS REAL), 1.5) * 0.1) / 0.5))) / 0.5)) AS "o1", (((((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) * coalesce(((CASE WHEN "s1"."o1" > (((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) / "s1"."o1") THEN 1 WHEN "s1"."o1" = "molecule"."label" THEN 5 ELSE 0 END / 0.25) * 0.5), 0)) * ((((CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 0.2) * (CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 3)) + (1 - CASE WHEN "s1"."o1" > (CAST("s1"."o1" AS INTEGER) - 0) THEN 5 ELSE 0 END)) * ((power(CAST((1 - CASE WHEN "s1"."o1" > (CAST("s1"."o1" AS INTEGER) - 0) THEN 5 ELSE 0 END) AS REAL), 1.5) * 0.1) / 0.5))) / 0.5) AS "o2" FROM "atom" AS "atom" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" INNER JOIN "s1" AS "s1" ON "s1"."o0" = "molecule"."label" INNER JOIN "connected" AS "connected" ON "atom"."atom_id" = "connected"."atom_id2" INNER JOIN "s2" AS "s2" ON "s2"."o0" = "connected"."bond_id"
```

- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/step output: unknown

## toxicology-14 (attempt 75)

```sql
SELECT "bond"."molecule_id" AS "o0", "atom"."element" AS "o1", "molecule"."label" AS "o2", CASE WHEN "bond"."molecule_id" > 'TR131' THEN 4 WHEN "bond"."bond_type" = '#' THEN 2 ELSE 0 END AS "o3" FROM "molecule" AS "molecule" INNER JOIN "atom" AS "atom" ON "molecule"."molecule_id" = "atom"."molecule_id" INNER JOIN "bond" AS "bond" ON "molecule"."molecule_id" = "bond"."molecule_id"
```


## toxicology-15 (attempt 58)

```sql
SELECT "connected"."atom_id2" AS "o0", "atom"."element" AS "o1", CAST("atom"."atom_id" AS REAL) AS "o2", "atom"."atom_id" AS "o3" FROM "connected" AS "connected" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" ORDER BY CAST("atom"."molecule_id" AS REAL) DESC, CAST("atom"."molecule_id" AS REAL) DESC LIMIT 5
```


## toxicology-16 (attempt 193)

```sql
SELECT "bond"."bond_id" AS "o0", "atom"."element" AS "o1", ((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25) - ((round((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25), 2) + ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2)) + 0)) AS "o2" FROM "atom" AS "atom" INNER JOIN "connected" AS "connected" ON "atom"."atom_id" = "connected"."atom_id2" INNER JOIN "bond" AS "bond" ON "connected"."bond_id" = "bond"."bond_id" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" WHERE ((((((((CASE WHEN "bond"."bond_type" = '#' THEN 2 END / 2) + 0) / (((((1 - (CAST(0 AS INTEGER) / 0.75)) * (1 - (CAST(0 AS REAL) / 0.2))) * 3) * 2) / 3)) * ((((1 - ((CAST(0 AS REAL) / 0.2) / 0.1)) * (((1 - (round(2, 2) / 0.5)) + ((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5))) / 3)) * 2) / 0.1)) * (((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25) - ((round((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25), 2) + ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2)) + 0)) + (CASE WHEN ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2) = (((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) THEN 5 END * 0.75))) / 0.75) / 1.5) = CASE WHEN ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2) = (((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) THEN 5 END AND (((((((CASE WHEN "bond"."bond_type" = '#' THEN 2 END / 2) + 0) / (((((1 - (CAST(0 AS INTEGER) / 0.75)) * (1 - (CAST(0 AS REAL) / 0.2))) * 3) * 2) / 3)) * ((((1 - ((CAST(0 AS REAL) / 0.2) / 0.1)) * (((1 - (round(2, 2) / 0.5)) + ((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5))) / 3)) * 2) / 0.1)) * (((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25) - ((round((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25), 2) + ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2)) + 0)) + (CASE WHEN ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2) = (((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) THEN 5 END * 0.75))) / 0.75) / 1.5) > ((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25) - ((round((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25), 2) + ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2)) + 0))) GROUP BY "bond"."bond_id", "atom"."element" ORDER BY ((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25) - ((round((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25), 2) + ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2)) + 0)) DESC
```

- `-` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)

## toxicology-17 (attempt 110)

```sql
SELECT "bond"."bond_type" AS "o0", "bond"."molecule_id" AS "o1", (((CAST((CAST(((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)) AS REAL) / ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75))) AS INTEGER) / (CAST(((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)) AS REAL) / ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)))) * (((CAST((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75) AS REAL) - CASE WHEN (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) > ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) * 3) THEN 4 ELSE 1 END) + 0) + 0)) * (CAST((CAST(((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)) AS REAL) / ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75))) AS REAL) / (((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)) * 0.2))) AS "o2", 1 AS "o3" FROM "bond" AS "bond" WHERE NOT ("bond"."bond_id" IS NULL) ORDER BY "bond"."molecule_id" ASC
```

- `*` derived/derived: unknown
- `/` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` constant-derived: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown
- `*` derived/derived: unknown
- `+` parameter ZERO: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `-` case/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `/` derived/derived: unknown

## toxicology-18 (attempt 169)

```sql
SELECT "bond"."bond_id" AS "o0", sqrt((((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * ((((CAST((CAST(CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END AS REAL) / ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) AS REAL) * 0.1) + (CAST(((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5) AS REAL) * 1.5)) + ((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1)) + (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1) / (1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5))))) * 3)) AS "o1", (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * ((((CAST((CAST(CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END AS REAL) / ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) AS REAL) * 0.1) + (CAST(((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5) AS REAL) * 1.5)) + ((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1)) + (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1) / (1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5))))) * 3) AS "o2" FROM "bond" AS "bond" ORDER BY sqrt((((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * ((((CAST((CAST(CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END AS REAL) / ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) AS REAL) * 0.1) + (CAST(((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5) AS REAL) * 1.5)) + ((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1)) + (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1) / (1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5))))) * 3)) ASC, (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * ((((CAST((CAST(CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END AS REAL) / ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) AS REAL) * 0.1) + (CAST(((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5) AS REAL) * 1.5)) + ((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1)) + (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1) / (1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5))))) * 3) ASC
```

- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `+` derived/derived: unknown
- `/` derived/derived: unknown
- `-` parameter WHOLE: unknown (a constant)
- `/` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `/` case/derived: unknown

## toxicology-19 (attempt 47)

```sql
WITH "s9" AS (SELECT "bond"."bond_id" AS "o0", coalesce((((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)) * ((round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4)) * 0.75)) + ((((round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4)) * 5) + 0) + ((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END - (round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4))) * 1.5))), 0) AS "o1", (((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)) * ((round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4)) * 0.75)) + ((((round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4)) * 5) + 0) + ((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END - (round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4))) * 1.5))) AS "o2" FROM "molecule" AS "molecule" INNER JOIN "bond" AS "bond" ON "molecule"."molecule_id" = "bond"."molecule_id" WHERE (("molecule"."label" > '+' AND "molecule"."label" LIKE '+') OR "molecule"."label" > '-') ORDER BY (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END - (round((CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL) / (CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100)), 2) + round(CAST((CASE WHEN "bond"."bond_type" = '-' THEN 1 WHEN CAST("bond"."bond_type" AS REAL) = '#' THEN 1 ELSE 0 END * 100) AS REAL), 4))) DESC LIMIT 5) SELECT "s9"."o0" AS "o0", "s9"."o2" AS "o1" FROM "s9" AS "s9" ORDER BY "s9"."o2" DESC LIMIT 100
```

- `-` case/derived: unknown
- `+` derived/derived: unknown
- `*` parameter CONVERT: strong (rule)
- `/` derived/derived: unknown
- `+` derived/derived: unknown
- `+` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)
- `+` parameter ZERO: unknown (a constant)
- `*` parameter WEIGHT: unknown (a constant)
- `*` derived/derived: unknown
- `*` parameter WEIGHT: unknown (a constant)

## toxicology-20 (attempt 140)

```sql
SELECT "molecule"."molecule_id" AS "o0" FROM "molecule" AS "molecule" INNER JOIN "atom" AS "atom" ON "molecule"."molecule_id" = "atom"."molecule_id"
```


