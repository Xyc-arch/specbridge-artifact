# toxicology: why 20 UNKNOWN calculations are unknown

Judged from the SQL and `catalogues/toxicology.json`. The catalogue has no numeric column at all (only keys, `element`, `bond_type`, `label`) and no relations, so every number in these queries is a count, a constant, or a CASE code.

| id | cause (1/2/3) | reason |
|---|---|---|
| u1 | 3 | Product of CASE scores keyed on `label`, `bond_type` and a specific `atom_id` ('TR001_11'), scaled by 2/0.75: identifiers and codes turned into arbitrary numbers. |
| u2 | 3 | `CASE(bond_type > '-' THEN 0 ELSE 0) + CASE(molecule_id < 'TR120' THEN 5 ...)`: a constant zero plus a score from a lexicographic range on the molecule identifier. |
| u3 | 3 | `coalesce(o1,1e6)/o1 + CASE(... THEN 1 - o1 ... WHEN o5 = o5 THEN 5)` is x/x plus a CASE mixing a count and constant codes. |
| u4 | 3 | `(1 - round(2,2)/0.5) + (2/0.1)/(0/5)`: constants only, with division by zero. |
| u5 | 3 | A ratio of two linear forms in the same `element` CASE code (1/3/0 from lexicographic ranges 'o'..'zn'): a code used as a quantity. |
| u6 | 3 | `1 - (2*0.1)`: arithmetic on constants only. |
| u7 | 3 | `(o1*10) / ((o1/o1)/0.2)` where o1 is an average of a constant expression: x/x on a constant. |
| u8 | 3 | `1 - CASE WHEN o1 > CAST(o1 AS INTEGER) THEN 5 ELSE 0 END`: one minus a score testing whether a rounded count has a fraction. |
| u9 | 3 | Sums and weights of `1 - CASE(bond_type > '-' THEN 0 ELSE 0)`, which is the constant 1. |
| u10 | 3 | Same `element` CASE code as u5, combined with itself through weights 0.25, 10, 0.75, 0.5. |
| u11 | 3 | `(round(2,2)/round(2,2))*0.75 + round(2,2)*10`: constants only. |
| u12 | 3 | CASE on `bond_id BETWEEN bond_id AND atom_id2` (identifier range) scaled, minus `(1 - 2*0.75)*1.5`: identifier comparison plus constants. |
| u13 | 3 | `(2/0.5) * (1 - round(1,2))`: constants only, equal to 0. |
| u14 | 3 | `CAST(2/2 AS INTEGER)*3 + CAST(2/2 AS INTEGER)*0.75`: constants only. |
| u15 | 3 | Polynomial in a count scaled by 0.25/1.5/0.2/3, plus the u8 fractional-part score, times a power of it: arbitrary weight chain on a count. |
| u16 | 3 | `round(1 - 0) + round(CAST(1 - 0 AS INTEGER))`, where each CASE is constant 0: constants only. |
| u17 | 3 | `CURRENT_DATE + CASE(bond_type, label codes)/1.5`: adds a code-derived fraction to today's date. |
| u18 | 3 | `CASE(...)/CASE(...)` with the same CASE, whose condition `2*0.1 > 2*0.1` is always false: x/x (in fact 0/0). |
| u19 | 3 | Ratio of `bond_type` CASE codes to themselves (the first branch requires bond_type to be '=' and '#' at once): x/x on a code. |
| u20 | 3 | `1 - (CASE(bond_type = '=' THEN 1 ELSE 2)*10/5)`: bond type coded 1/2 (inverting single/double) and scaled. |

## Counts

| cause | n |
|---|---|
| 1 catalogue lacks it | 0 |
| 2 propagation loses it | 0 |
| 3 no supported interpretation | 20 |

## Pattern

Toxicology has no measured quantity at all, so every calculation the generator draws is made from constants, counts, or CASE codes over identifiers and categories; all 20 have no interpretation, and no catalogue fact could support them. The UNKNOWN verdict here marks a database with nothing to compute on, and the decision that is wrong is drawing arithmetic for it at all, not the checker's lack of evidence.
