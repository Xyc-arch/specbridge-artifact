# Inclination of the reference SQL (`python -m specbridge.comm.diagnose.inclination`)

Side read from the reference SQL alone (no model). Share A = side A among references where the decision arises.
Databases mostly A: among databases with >= 5 such references. Library: the frozen library's records of
the matching type, placed by the same rule (open = the question leaves the decision open).

## BIRD train (9428 questions, 69 databases)

| decision | side A | side B | A | B | share A | databases mostly A | library open A / B | settled A / B |
|---|---|---|---|---|---|---|---|---|
| ties_and_selection | one row (LIMIT 1) | every tied row (= MIN/MAX) | 1554 | 175 | 0.899 | 63 / 65 | 0 / 0 | 0 / 0 |
| counting_unit | distinct entities | rows | 239 | 1715 | 0.122 | 4 / 67 | 0 / 0 | 0 / 0 |
| population_scope | inner join | outer join | 7167 | 45 | 0.994 | 69 / 69 | 0 / 0 | 0 / 0 |
| missing_values | NULL filtered | NULL not filtered | 16 | 1034 | 0.015 | 0 / 55 | 0 / 0 | 0 / 0 |
| calculation_scale | times 100 | fraction | 512 | 67 | 0.884 | 44 / 46 | 0 / 0 | 0 / 0 |
| calculation_division | explicit REAL (CAST or 1.0) | no explicit cast | 786 | 141 | 0.848 | 55 / 59 | 0 / 0 | 0 / 0 |
| output_extreme | sort value returned | sort value not returned | 158 | 1396 | 0.102 | 2 / 65 | 0 / 0 | 0 / 0 |
| output_duplicates | DISTINCT | duplicates kept | 659 | 3240 | 0.169 | 6 / 68 | 0 / 0 | 0 / 0 |

## BIRD dev (1534 questions, 11 databases)

| decision | side A | side B | A | B | share A | databases mostly A | library open A / B | settled A / B |
|---|---|---|---|---|---|---|---|---|
| ties_and_selection | one row (LIMIT 1) | every tied row (= MIN/MAX) | 243 | 25 | 0.907 | 11 / 11 | 6 / 1 | 6 / 0 |
| counting_unit | distinct entities | rows | 55 | 242 | 0.185 | 0 / 11 | 2 / 2 | 11 / 48 |
| population_scope | inner join | outer join | 1139 | 1 | 0.999 | 11 / 11 | 0 / 0 | 110 / 0 |
| missing_values | NULL filtered | NULL not filtered | 17 | 164 | 0.094 | 0 / 10 | 0 / 2 | 1 / 5 |
| calculation_scale | times 100 | fraction | 101 | 6 | 0.944 | 11 / 11 | 0 / 0 | 4 / 0 |
| calculation_division | explicit REAL (CAST or 1.0) | no explicit cast | 155 | 16 | 0.906 | 11 / 11 | 0 / 0 | 5 / 0 |
| output_extreme | sort value returned | sort value not returned | 42 | 201 | 0.173 | 1 / 11 | 2 / 7 | 1 / 1 |
| output_duplicates | DISTINCT | duplicates kept | 147 | 547 | 0.212 | 0 / 11 | 4 / 19 | 1 / 4 |

## Spider train (8659 questions, 146 databases)

| decision | side A | side B | A | B | share A | databases mostly A | library open A / B | settled A / B |
|---|---|---|---|---|---|---|---|---|
| ties_and_selection | one row (LIMIT 1) | every tied row (= MIN/MAX) | 1046 | 310 | 0.771 | 77 / 82 | 0 / 0 | 0 / 0 |
| counting_unit | distinct entities | rows | 180 | 511 | 0.260 | 6 / 36 | 0 / 0 | 0 / 0 |
| population_scope | inner join | outer join | 3812 | 0 | 1.000 | 138 / 138 | 0 / 0 | 0 / 0 |
| missing_values | NULL filtered | NULL not filtered | 0 | 379 | 0.000 | 0 / 28 | 0 / 0 | 0 / 0 |
| calculation_scale | times 100 | fraction | 0 | 0 | - | - | - | - |
| calculation_division | explicit REAL (CAST or 1.0) | no explicit cast | 0 | 1 | 0.000 | 0 / 0 | 0 / 0 | 0 / 0 |
| output_extreme | sort value returned | sort value not returned | 98 | 946 | 0.094 | 1 / 79 | 0 / 0 | 0 / 0 |
| output_duplicates | DISTINCT | duplicates kept | 575 | 1711 | 0.252 | 3 / 101 | 0 / 0 | 0 / 0 |

## Spider dev (1034 questions, 20 databases)

| decision | side A | side B | A | B | share A | databases mostly A | library open A / B | settled A / B |
|---|---|---|---|---|---|---|---|---|
| ties_and_selection | one row (LIMIT 1) | every tied row (= MIN/MAX) | 179 | 4 | 0.978 | 13 / 13 | 0 / 0 | 13 / 0 |
| counting_unit | distinct entities | rows | 4 | 74 | 0.051 | 0 / 7 | 0 / 0 | 0 / 4 |
| population_scope | inner join | outer join | 408 | 0 | 1.000 | 19 / 19 | 0 / 0 | 26 / 0 |
| missing_values | NULL filtered | NULL not filtered | 0 | 76 | 0.000 | 0 / 6 | 0 / 0 | 0 / 9 |
| calculation_scale | times 100 | fraction | 0 | 0 | - | - | - | - |
| calculation_division | explicit REAL (CAST or 1.0) | no explicit cast | 0 | 0 | - | - | - | - |
| output_extreme | sort value returned | sort value not returned | 16 | 163 | 0.089 | 1 / 13 | 1 / 2 | 0 / 0 |
| output_duplicates | DISTINCT | duplicates kept | 35 | 171 | 0.170 | 1 / 13 | 2 / 0 | 0 / 0 |

## By author group, silent questions only (no wording cue for the decision)

| decision | BIRD train | BIRD dev | Spider train (own) | Spider dev | imported: geo, restaurants | imported: academic, imdb, scholar, yelp |
|---|---|---|---|---|---|---|
| ties_and_selection (A = one row (LIMIT 1)) | 1431/1590 | 229/251 | 940/983 | 170/174 | 21/281 | 35/36 |
| counting_unit (A = distinct entities) | 228/1934 | 37/278 | 20/369 | 1/74 | 0/14 | 138/276 |
| population_scope (A = inner join) | 7125/7170 | 1129/1130 | 2761/2761 | 406/406 | 161/161 | 880/880 |
| missing_values (A = NULL filtered) | 13/1033 | 15/170 | 0/353 | 0/76 | 0/12 | 0/14 |
| calculation_scale (A = times 100) | 512/579 | 101/107 | 0/0 | 0/0 | 0/0 | 0/0 |
| calculation_division (A = explicit REAL (CAST or 1.0)) | 786/927 | 155/171 | 0/0 | 0/0 | 0/1 | 0/0 |
| output_extreme (A = sort value returned) | 96/1324 | 28/212 | 73/896 | 8/158 | 0/14 | 0/34 |
| output_duplicates (A = DISTINCT) | 646/3882 | 144/691 | 129/1526 | 22/193 | 1/134 | 348/525 |