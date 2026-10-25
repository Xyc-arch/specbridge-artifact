# toxicology: 20 random unknown substantive calculations (of 1422)

## toxicology-u1 (attempt 177) -- mechanical class: NO UNIT

Node: `(CAST(((CASE WHEN "molecule"."label" = '-' THEN 1 WHEN "bond"."bond_type" = '#' THEN 4 WHEN "molecule"."label" = '+' THEN 1 WHEN ("atom"."atom_id" = 'TR001_11' OR "molecule"."label" = '-') THEN 5 ELSE 0 END * 2) / 0.75) AS REAL) * ((CASE WHEN "atom"."element" = 's' THEN 1 WHEN (CASE WHEN "molecule".`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: atom.atom_id [unit '' (-), kind '', scale '']; atom.element [unit '' (-), kind '', scale '']; bond.bond_type [unit '' (-), kind '', scale '']; molecule.label [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "atom"."atom_id" AS "o0", (((CASE WHEN "molecule"."label" = '-' THEN 1 WHEN "bond"."bond_type" = '#' THEN 4 WHEN "molecule"."label" = '+' THEN 1 WHEN ("atom"."atom_id" = 'TR001_11' OR "molecule"."label" = '-') THEN 5 ELSE 0 END + CASE WHEN "molecule"."label" < '+' THEN 1 WHEN CASE WHEN "molecule"."label" = '-' THEN 1 WHEN "bond"."bond_type" = '#' THEN 4 WHEN "molecule"."label" = '+' THEN 1 WHEN ("atom"."atom_id" = 'TR001_11' OR "molecule"."label" = '-') THEN 5 ELSE 0 END < ((CASE WHEN "molecule"."label" = '-' THEN 1 WHEN "bond"."bond_type" = '#' THEN 4 WHEN "molecule"."label" = '+' THEN 1 WHEN ("atom"."atom_id" = 'TR001_11' OR "molecule"."label" = '-') THEN 5 ELSE 0 END * 2) / 0.75) THEN 1 WHEN ("atom"."atom_id" > 'TR002_6' AND ((CASE WHEN "molecule"."label" = '-' THEN 1 WHEN "bond"."bond_type" = '#' THEN 4 WHEN "molecule"."label" = '+' THEN 1 WHEN ("atom"."atom_id" = 'TR001_11' O
```

## toxicology-u2 (attempt 92) -- mechanical class: SCORE

Node: `(CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_ty`

- left operand: unit '', kind 'indicator', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']; bond.molecule_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."molecule_id" AS "o0", (((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) THEN 1 ELSE 0 END) / CAST((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) THEN 1 ELSE 0 END) AS REAL)) * CASE WHEN (((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_t
```

## toxicology-u3 (attempt 108) -- mechanical class: NO UNIT

Node: `((COALESCE("s23"."o1", 1000000) / CAST("s23"."o1" AS REAL)) + CASE WHEN "s17"."o5" > "s17"."o4" THEN (1 - "s23"."o1") WHEN "bond"."bond_type" < '#' THEN 10 WHEN "s17"."o5" = "s17"."o5" THEN 5 ELSE 0 END)`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
WITH "s17" AS (SELECT "atom"."molecule_id" AS "o0", COUNT(*) AS "o1", AVG(((((coalesce(((power((CAST(coalesce(0, 1) AS REAL) / coalesce(0, 1)), 1.5) * coalesce(0, 1)) + ((CASE WHEN coalesce(0, 1) >= 0 THEN 1 END / 0.75) * (1 - (CASE WHEN coalesce(0, 1) >= 0 THEN 1 END / 0.2)))), 1) * 1.5) + 0) / 1.5) * (coalesce(0, 1) * round(CAST(power((CAST(coalesce(0, 1) AS REAL) / coalesce(0, 1)), 1.5) AS REAL), 2)))) AS "o2", AVG((power((CAST(coalesce(0, 1) AS REAL) / coalesce(0, 1)), 1.5) * coalesce(0, 1))) AS "o3", AVG(((((CASE WHEN coalesce(0, 1) >= 0 THEN 1 END / 0.75) * (1 - (CASE WHEN coalesce(0, 1) >= 0 THEN 1 END / 0.2))) / ((CASE WHEN round(CAST(power((CAST(coalesce(0, 1) AS REAL) / coalesce(0, 1)), 1.5) AS REAL), 2) < "atom"."element" THEN 1 WHEN "atom"."element" = 'y' THEN 4 ELSE 0 END * 3) / 0.2)) / ((CASE WHEN round(CAST(power((CAST(coalesce(0, 1) AS REAL) / coalesce(0, 1)), 1.5) AS REA
```

## toxicology-u4 (attempt 193) -- mechanical class: NO UNIT

Node: `((1 - (ROUND(2, 2) / 0.5)) + ((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."bond_id" AS "o0", "atom"."element" AS "o1", ((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25) - ((round((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5)) * 0.25), 2) + ((((CAST(2 AS REAL) / 10) / 3) * (1 - (round(2, 2) / 5))) * 2)) + 0)) AS "o2" FROM "atom" AS "atom" INNER JOIN "connected" AS "connected" ON "atom"."atom_id" = "connected"."atom_id2" INNER JOIN "bond" AS "bond" ON "connected"."bond_id" = "bond"."bond_id" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" WHERE ((((((((CASE WHEN "bond"."bond_type" = '#' THEN 2 END / 2) + 0) / (((((1 - (CAST(0 AS INTEGER) / 0.75)) * (1 - (CAST(0 AS REAL) / 0.2))) * 3) * 2) / 3)) * ((((1 - ((CAST(0 AS REAL) / 0.2) / 0.1)) * (((1 - (round(2, 2) / 0.5)) + ((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER) / 5))) / 3)) * 2) / 0.1)) * (((((CAST(2 AS REAL) / 0.1) / (CAST(0 AS INTEGER)
```

## toxicology-u5 (attempt 188) -- mechanical class: NO UNIT

Node: `(((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75) / (((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) + ((CAST(CASE WHEN "atom"."e`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: atom.element [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "connected"."atom_id" AS "o0", round((((((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) + ((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75)) * 0.5) * (((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75) / (((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) + ((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75)) * 0.5))) + (0.2 / CAST((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) AS REAL)
```

## toxicology-u6 (attempt 158) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - (CAST(2 AS REAL) * 0.1))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "atom"."atom_id" AS "o0", round((((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))) * ((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) + (((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) * 3) + ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * 0.1)))), 0) AS "o1", (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))))) AS "o2", AVG((CAST(((1 - (1 
```

## toxicology-u7 (attempt 15) -- mechanical class: NO UNIT

Node: `(("s2"."o1" * 10) / (CAST(("s2"."o1" / "s2"."o1") AS REAL) / 0.2))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s2" AS (SELECT "bond"."bond_id" AS "o0", AVG((CAST(round(CAST(round(CAST((0.5 / (round(CAST(round(1, 2) AS REAL), 2) + power(CAST(round(1, 2) AS REAL), 1.5))) AS INTEGER), 2) AS REAL), 2) AS INTEGER) + coalesce(CAST(round(CAST((0.5 / (round(CAST(round(1, 2) AS REAL), 2) + power(CAST(round(1, 2) AS REAL), 1.5))) AS INTEGER), 2) AS REAL), 0))) AS "o1" FROM "bond" AS "bond" GROUP BY "bond"."bond_id") SELECT "s2"."o1" AS "o0", "s2"."o0" AS "o1", round(CAST(((("s2"."o1" / "s2"."o1") + (((round(((CAST(("s2"."o1" / "s2"."o1") AS REAL) / "s2"."o1") + 0), 2) * 0.2) + (round((CAST((CAST(("s2"."o1" / "s2"."o1") AS REAL) / "s2"."o1") AS REAL) * 0.1), 2) * 0.25)) * (CAST(("s2"."o1" / "s2"."o1") AS REAL) / 0.2))) * 0.25) AS REAL), 2) AS "o2", "connected"."atom_id2" AS "o3", (CAST(("s2"."o1" / "s2"."o1") AS REAL) / 0.2) AS "o4", coalesce((((coalesce((round(((CAST(("s2"."o1" / "s2"."o1") AS REAL) 
```

## toxicology-u8 (attempt 146) -- mechanical class: WHOLE of SCORE

Node: `(1 - CASE WHEN "s1"."o1" > (CAST("s1"."o1" AS INTEGER) - 0) THEN 5 ELSE 0 END)`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "molecule"."label" AS "o0", round(COUNT(*), 2) AS "o1" FROM "atom" AS "atom" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" WHERE "atom"."element" IN ((SELECT "connected"."atom_id" AS "o0" FROM "connected" AS "connected")) GROUP BY "molecule"."label"), "s2" AS (SELECT "bond"."bond_id" AS "o0", "bond"."bond_type" AS "o1", "molecule"."label" AS "o2" FROM "molecule" AS "molecule" INNER JOIN "bond" AS "bond" ON "molecule"."molecule_id" = "bond"."molecule_id" ORDER BY "molecule"."label" DESC LIMIT 100) SELECT "s1"."o1" AS "o0", abs((((((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) * coalesce(((CASE WHEN "s1"."o1" > (((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) / "s1"."o1") THEN 1 WHEN "s1"."o1" = "molecule"."label" THEN 5 ELSE 0 END / 0.25) * 0.5), 0)) * ((((CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 0.2
```

## toxicology-u9 (attempt 92) -- mechanical class: NO UNIT

Node: `(((ROUND((1 - CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END), 2) + ROUND(CAST((1 - CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) AS INTEGER), 2)) * 1.5) + ((ROUND((1 - CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END), 2) + ROUND(CAST((1 - CASE WHEN "bond"."bond_type" > '-' THEN 0`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."molecule_id" AS "o0", (((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) THEN 1 ELSE 0 END) / CAST((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) THEN 1 ELSE 0 END) AS REAL)) * CASE WHEN (((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_t
```

## toxicology-u10 (attempt 188) -- mechanical class: NO UNIT

Node: `((((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) + ((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75)) * 0.5) * (((CAST(CASE WHEN `

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: atom.element [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "connected"."atom_id" AS "o0", round((((((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) + ((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75)) * 0.5) * (((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75) / (((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) + ((CAST(CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END AS REAL) * 10) * 0.75)) * 0.5))) + (0.2 / CAST((CASE WHEN "atom"."element" BETWEEN 'o' AND "atom"."element" THEN 1 WHEN "atom"."element" > 'zn' THEN 3 ELSE 0 END * 0.25) AS REAL)
```

## toxicology-u11 (attempt 37) -- mechanical class: NO UNIT

Node: `(((CAST(ROUND(2, 2) AS REAL) / ROUND(2, 2)) * 0.75) + (COALESCE(CAST(ROUND(2, 2) AS REAL), 1) * 10))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."bond_id" AS "o0", "bond"."bond_type" AS "o1", "bond"."molecule_id" AS "o2", 1 AS "o3", (((CAST((coalesce(CAST((((CAST(round(2, 2) AS REAL) / round(2, 2)) + 0) + (CAST((CAST(round(2, 2) AS REAL) / round(2, 2)) AS REAL) * 0.1)) AS REAL), 0) + coalesce(CAST(round(2, 2) AS REAL), 1)) AS REAL) / coalesce(CAST(round(2, 2) AS REAL), 1)) * 0.2) + ((((CASE WHEN ((CAST(round(2, 2) AS REAL) / round(2, 2)) + 0) > ((((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.75) + (coalesce(CAST(round(2, 2) AS REAL), 1) * 10)) * 0.25) THEN 2 WHEN ((((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.75) + (coalesce(CAST(round(2, 2) AS REAL), 1) * 10)) * 0.25) > ((((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.75) + (coalesce(CAST(round(2, 2) AS REAL), 1) * 10)) * 0.25) THEN 2 WHEN CAST((((CAST(round(2, 2) AS REAL) / round(2, 2)) * 0.75) + (coalesce(CAST(round(2, 2) AS REAL), 1) * 10)) AS INTEGER) > (((C
```

## toxicology-u12 (attempt 77) -- mechanical class: NO UNIT

Node: `(((CASE WHEN "connected"."bond_id" BETWEEN "connected"."bond_id" AND "connected"."atom_id2" THEN 2 ELSE 0 END / 5) * 1.5) - ((1 - (CAST(2 AS INTEGER) * 0.75)) * 1.5))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: connected.atom_id2 [unit '' (-), kind '', scale '']; connected.bond_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "connected"."atom_id" AS "o0", (((((((CASE WHEN "connected"."bond_id" BETWEEN "connected"."bond_id" AND "connected"."atom_id2" THEN 2 ELSE 0 END / 5) * 1.5) - ((1 - (CAST(2 AS INTEGER) * 0.75)) * 1.5)) / 2) + ((((CASE WHEN "connected"."bond_id" BETWEEN "connected"."bond_id" AND "connected"."atom_id2" THEN 2 ELSE 0 END / 5) * 1.5) - ((1 - (CAST(2 AS INTEGER) * 0.75)) * 1.5)) / 2)) - (CAST((((CASE WHEN "connected"."bond_id" BETWEEN "connected"."bond_id" AND "connected"."atom_id2" THEN 2 ELSE 0 END * 0.75) / ((CAST(2 AS INTEGER) * 0.75) * 0.25)) + (((CAST(2 AS REAL) / 5) + (CAST(2 AS INTEGER) / 10)) / 1.5)) AS REAL) / ((CASE WHEN (CAST(2 AS INTEGER) * 0.75) > (CAST(2 AS INTEGER) / 10) THEN 4 ELSE 0 END + CASE WHEN CASE WHEN "connected"."atom_id2" = 'TR485_6' THEN 3 WHEN "connected"."bond_id" = 'TR501_11_14' THEN 1 ELSE 3 END = CASE WHEN "connected"."atom_id2" = 'TR485_6' THEN 3 WHEN 
```

## toxicology-u13 (attempt 76) -- mechanical class: NO UNIT

Node: `((CAST(2 AS REAL) / 0.5) * (1 - ROUND(1, 2)))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "bond"."bond_id" AS "o0", "atom"."atom_id" AS "o1" FROM "connected" AS "connected" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" INNER JOIN "bond" AS "bond" ON "connected"."bond_id" = "bond"."bond_id" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" ORDER BY "atom"."atom_id" DESC LIMIT 100), "s2" AS (SELECT "connected"."atom_id2" AS "o0", "atom"."molecule_id" AS "o1" FROM "connected" AS "connected" INNER JOIN "atom" AS "atom" ON "connected"."atom_id" = "atom"."atom_id" WHERE ("atom"."element" > 'br' AND "atom"."element" < 'y') ORDER BY "atom"."molecule_id" DESC LIMIT 10) SELECT "s2"."o1" AS "o0", "s1"."o1" AS "o1", (((1 - CAST(((round(CAST(((CAST(round(1, 2) AS REAL) / round(1, 2)) / 0.1) AS REAL), 2) * 1.5) / 5) AS INTEGER)) + ((CAST(((round(CAST(((CAST(round(1, 2) AS REAL) / round(1, 2)) / 0.1) AS REAL
```

## toxicology-u14 (attempt 110) -- mechanical class: NO UNIT

Node: `((CAST((CAST(ROUND(2, 4) AS REAL) / ROUND(2, 4)) AS INTEGER) * 3) + (CAST((CAST(ROUND(2, 4) AS REAL) / ROUND(2, 4)) AS INTEGER) * 0.75))`

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."bond_type" AS "o0", "bond"."molecule_id" AS "o1", (((CAST((CAST(((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)) AS REAL) / ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75))) AS INTEGER) / (CAST(((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)) AS REAL) / ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) + (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75)))) * (((CAST((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 0.75) AS REAL) - CASE WHEN (CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) * 3) > ((CAST((CAST(round(2, 4) AS REAL) / round(2, 4)) AS INTEGER) *
```

## toxicology-u15 (attempt 146) -- mechanical class: NO UNIT

Node: `((((CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 0.2) * (CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 3)) + (1 - CASE WHEN "s1"."o1" > (CAST("s1"."o1" AS INTEGER) - 0) THEN 5 ELSE 0 END)) * ((POWER(CAST((1 - CASE WHEN "s1"."o1" > `

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: none
- catalogue relations among them: none

Whole query:
```sql
WITH "s1" AS (SELECT "molecule"."label" AS "o0", round(COUNT(*), 2) AS "o1" FROM "atom" AS "atom" INNER JOIN "molecule" AS "molecule" ON "atom"."molecule_id" = "molecule"."molecule_id" WHERE "atom"."element" IN ((SELECT "connected"."atom_id" AS "o0" FROM "connected" AS "connected")) GROUP BY "molecule"."label"), "s2" AS (SELECT "bond"."bond_id" AS "o0", "bond"."bond_type" AS "o1", "molecule"."label" AS "o2" FROM "molecule" AS "molecule" INNER JOIN "bond" AS "bond" ON "molecule"."molecule_id" = "bond"."molecule_id" ORDER BY "molecule"."label" DESC LIMIT 100) SELECT "s1"."o1" AS "o0", abs((((((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) * coalesce(((CASE WHEN "s1"."o1" > (((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) / "s1"."o1") THEN 1 WHEN "s1"."o1" = "molecule"."label" THEN 5 ELSE 0 END / 0.25) * 0.5), 0)) * ((((CAST((CAST(((CAST("s1"."o1" AS INTEGER) - 0) / 0.25) AS REAL) / 1.5) AS REAL) * 0.2
```

## toxicology-u16 (attempt 92) -- mechanical class: SCORE

Node: `(ROUND((1 - CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END), 2) + ROUND(CAST((1 - CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) AS INTEGER), 2))`

- left operand: unit 'fraction', kind 'indicator', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."molecule_id" AS "o0", (((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) THEN 1 ELSE 0 END) / CAST((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = "bond"."molecule_id" AND "bond"."bond_type" != '-' AND CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END = CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END) THEN 1 ELSE 0 END) AS REAL)) * CASE WHEN (((CASE WHEN "bond"."bond_type" > '-' THEN 0 ELSE 0 END + CASE WHEN "bond"."molecule_id" < 'TR120' THEN 5 WHEN (CASE WHEN "bond"."bond_t
```

## toxicology-u17 (attempt 115) -- mechanical class: NO UNIT

Node: `(CURRENT_DATE + COALESCE((CASE WHEN "bond"."bond_type" < '#' THEN 1 WHEN "molecule"."label" > '+' THEN 5 ELSE 1 END / 1.5), 0))`

- left operand: unit '', kind 'date', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']; molecule.label [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "connected"."bond_id" AS "o0", "atom"."molecule_id" AS "o1", coalesce("atom"."atom_id", 0) AS "o2", "molecule"."label" AS "o3", round((((CAST((CURRENT_DATE + coalesce((CASE WHEN "bond"."bond_type" < '#' THEN 1 WHEN "molecule"."label" > '+' THEN 5 ELSE 1 END / 1.5), 0)) AS REAL) * 0.1) * ((CAST((CURRENT_DATE + coalesce((CASE WHEN "bond"."bond_type" < '#' THEN 1 WHEN "molecule"."label" > '+' THEN 5 ELSE 1 END / 1.5), 0)) AS REAL) * 0.1) / (CAST((CURRENT_DATE + coalesce((CASE WHEN "bond"."bond_type" < '#' THEN 1 WHEN "molecule"."label" > '+' THEN 5 ELSE 1 END / 1.5), 0)) AS REAL) * 0.1))) / ((((CAST((CURRENT_DATE + coalesce((CASE WHEN "bond"."bond_type" < '#' THEN 1 WHEN "molecule"."label" > '+' THEN 5 ELSE 1 END / 1.5), 0)) AS REAL) * 0.1) * ((CAST((CURRENT_DATE + coalesce((CASE WHEN "bond"."bond_type" < '#' THEN 1 WHEN "molecule"."label" > '+' THEN 5 ELSE 1 END / 1.5), 0)) AS REAL)
```

## toxicology-u18 (attempt 158) -- mechanical class: SCORE

Node: `(CAST(CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END AS REAL) / CASE WHEN ("molecule"."molecule_id" > 'TR022' AND (CAST(2 AS REAL) * 0.1) > (CAST(2 AS REAL) * 0.1)) THEN 3 ELSE 0 END)`

- left operand: unit '', kind 'score', quantity ()
- right operand: unit '', kind 'score', quantity ()
- stored columns under it: molecule.molecule_id [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "atom"."atom_id" AS "o0", round((((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))) * ((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) + (((1 - (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1))))))) * 3) + ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * 0.1)))), 0) AS "o1", (CAST(((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))) AS REAL) / ((1 - (1 - (CAST(2 AS REAL) * 0.1))) * ((1 - (1 - (CAST(2 AS REAL) * 0.1))) / (1 - (1 - (CAST(2 AS REAL) * 0.1)))))) AS "o2", AVG((CAST(((1 - (1 
```

## toxicology-u19 (attempt 69) -- mechanical class: NO UNIT

Node: `(CAST((CAST(COALESCE(CAST((CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN 1 ELSE 0 END * 0.5) AS REAL), 0) AS INTEGER) / (CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN 1 ELSE 0 `

- left operand: unit '', kind '', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."bond_id" AS "o0", (((CAST((CAST(coalesce(CAST((CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN 1 ELSE 0 END * 0.5) AS REAL), 0) AS INTEGER) / (CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN 1 ELSE 0 END * 0.5)) AS REAL) / (CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN 1 ELSE 0 END * 0.5)) * (((CASE WHEN ("bond"."bond_id" = 'TR000_2_3' OR "atom"."element" = 'sn') THEN 5 ELSE 1 END / 0.1) * 0.2) * 0.1)) / CAST((CAST((CAST(coalesce(CAST((CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN 1 ELSE 0 END * 0.5) AS REAL), 0) AS INTEGER) / (CASE WHEN ("bond"."bond_type" = '=' AND "bond"."bond_type" = '#') THEN 5 WHEN "bond"."bond_type" > '-' THEN
```

## toxicology-u20 (attempt 169) -- mechanical class: WHOLE of NO UNIT

Node: `(1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5))`

- left operand: unit '', kind 'const', quantity ()
- right operand: unit '', kind '', quantity ()
- stored columns under it: bond.bond_type [unit '' (-), kind '', scale '']
- catalogue relations among them: none

Whole query:
```sql
SELECT "bond"."bond_id" AS "o0", sqrt((((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * ((((CAST((CAST(CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END AS REAL) / ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) AS REAL) * 0.1) + (CAST(((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5) AS REAL) * 1.5)) + ((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1)) + (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * 0.1) / (1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5))))) * 3)) AS "o1", (((1 - ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) * ((((CAST((CAST(CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END AS REAL) / ((CASE WHEN "bond"."bond_type" = '=' THEN 1 ELSE 2 END * 10) / 5)) AS REAL) * 0.1) + (CAST(((CASE WHEN "bond"."bond_type
```

