# toxicology: semantic coherence review (20 delivered queries)

| query id | verdict | cause (if not yes) | reason |
|---|---|---|---|
| toxicology-1 | no | arbitrary | The output is arithmetic on constants only (`round(1,2)/round(1,2)/0.1*1.5/5 ...`), and the filters order atom IDs and elements alphabetically. |
| toxicology-2 | no | arbitrary | The outputs are constant arithmetic on `2*0.1`, and the filter uses `element BETWEEN bond_id AND molecule_id` plus molecule-ID thresholds. |
| toxicology-3 | uncertain | arbitrary | The bond types linked to atom TR502_1 are sensible, but the output and the ordering on `CURRENT_DATE` have no purpose. |
| toxicology-4 | no | arbitrary | `CASE ... THEN 1 ELSE 1 END * 10` makes `1-(1-10) + 1.5/…` a constant with no meaning. |
| toxicology-5 | uncertain | arbitrary | Non-carcinogenic molecules with F or Zn is a sensible filter, but `PERCENT_RANK() OVER (ORDER BY molecule_id)` ranks an identifier. |
| toxicology-6 | no | arbitrary | `CAST(bond_id AS REAL) = 'TR496_8_33'` casts an identifier to a number and compares it to text, and the 4/10 score has no purpose. |
| toxicology-7 | no | arbitrary | Every aggregate is over constants (`power(2*2,1.5)`), and the query divides by `sqrt(0)*5` and compares `2*2 > element`. |
| toxicology-8 | no | arbitrary | The outputs are constant chains (`round(2,2)/round(2,2)`, `/0.1/0.5`) and alphabetical comparisons such as `label > '+'`. |
| toxicology-9 | no | arbitrary | `bond_type > '#'` scores feed chains multiplied by `CASE ... THEN 0 ELSE 0` and by `AVG(2)/AVG(2)`, which are degenerate. |
| toxicology-10 | yes | | Lists each atom that is the second atom of a connection, with its molecule. |
| toxicology-11 | yes | | Lists each bond with its molecule and carcinogenic label. |
| toxicology-12 | no | arbitrary | The output is constant arithmetic that divides by `coalesce(0,0)+0`. |
| toxicology-13 | no | arbitrary | `element IN (atom_id)` compares an element to an ID, `count = label` compares a number to text, and the count then goes through arbitrary weights. |
| toxicology-14 | no | arbitrary | `CASE WHEN molecule_id > 'TR131' THEN 4` scores rows by alphabetical identifier order. |
| toxicology-15 | no | arbitrary | `CAST(atom_id AS REAL)` and `ORDER BY CAST(molecule_id AS REAL)` use text identifiers as numbers. |
| toxicology-16 | no | arbitrary | The output is constant arithmetic that divides by `CAST(0 AS INTEGER)/5`. |
| toxicology-17 | no | arbitrary | The output is built only from `round(2,4)/round(2,4)` and constant weights. |
| toxicology-18 | no | arbitrary | A 1/2 code for bond type passes through `1 - x*10/5`, weights and `sqrt`, a chain that means nothing. |
| toxicology-19 | no | arbitrary | `CAST(bond_type AS REAL) = '#'`, `x*100/(x*100)`, and `label > '-'` are degenerate or meaningless. |
| toxicology-20 | yes | | Lists the molecule ID for every atom (one row per atom). |

## Totals

- yes: 3
- uncertain: 2
- no: 15
- Causes: missing evidence 0, lost in propagation 0, arbitrary 17

## Dominant pattern

toxicology has no numeric column, so every arithmetic expression is built from literal constants (`round(2,2)`, `CAST(0 AS INTEGER)`), from CASE codes over text categories, or from identifiers cast to numbers. None of these can mean anything, and several divide by zero. The rest of the incoherence comes from alphabetical comparisons on IDs and labels (`molecule_id > 'TR131'`, `label > '+'`). Only the plain join-and-list queries (10, 11, 20) are coherent. The generator should not draw arithmetic at all on a database with no numeric quantities.
