# toxicology: fresh review of 20 delivered queries

Question: does this query express a coherent calculation over the target data, with its parameters and assumptions explicit? Judged from the SQL and `catalogues/toxicology.json` (no numeric columns, no relations).

| id | verdict | has arithmetic (y/n) | cause | reason |
|---|---|---|---|---|
| 1 | no | y | arbitrary | The output column is arithmetic on constants only (`round(1,2)/round(1,2)/0.1 ...`, division by `coalesce(0,0)*1.5`) plus a CASE on atom_id ranges and one specific atom. |
| 2 | no | y | arbitrary | Constants-only output (`1 - (1 - 2*0.1)` ...); the filter uses `element BETWEEN (bond_id subquery) AND molecule_id` (identifier ranges) and an always-false `2*0.1 > 2*0.1`. |
| 3 | uncertain | n | arbitrary | Bond types for the bonds of atom TR502_1 is sensible, but `CURRENT_DATE` is output and used as the sort key for no purpose. |
| 4 | no | y | arbitrary | `CASE(bond_id = 'TR496_9_10' THEN 1 ELSE 1)*10` is the constant 10; the output is `10 + 1.5/10`, a constant per row. |
| 5 | uncertain | n | arbitrary | Non-carcinogenic molecules containing F or Zn is sensible, but `PERCENT_RANK()` over the molecule identifier ranks by an ID string, with one row per atom. |
| 6 | no | n | arbitrary | `CAST(bond_id AS REAL) = 'TR496_8_33'` is an impossible comparison; the 4/10 score has no purpose. |
| 7 | no | y | arbitrary | Constants only (`power(2*2,1.5)`, `sqrt(0)*5` as a divisor); the filter compares a number to `element`. |
| 8 | no | y | arbitrary | Constant chains (`round(2,2)/round(2,2)`, x/x) times a CASE score on lexicographic `label > '+'`. |
| 9 | no | y | arbitrary | CASE codes for bond_type (10/2/1 by lexicographic ranges), `AVG(2) OVER` of a constant, x/x, all multiplied by a CASE that is always 0. |
| 10 | yes | n | - | Lists each atom that is the second atom of a bond, with its molecule. |
| 11 | yes | n | - | Lists bonds with their molecule and carcinogenic label, ordered by label. |
| 12 | no | y | arbitrary | Constants only with division by zero (`(1/0.75) / (coalesce(0,0) + 0)`). |
| 13 | no | y | arbitrary | Weight chains on a per-label atom count (`(count - 0)/0.25`, `power(1 - CASE,1.5)`), a count compared to the text `label`, and an `element IN (atom_id)` filter comparing element symbols with atom identifiers. |
| 14 | no | n | arbitrary | The score `CASE WHEN molecule_id > 'TR131' THEN 4 WHEN bond_type = '#' THEN 2` thresholds a molecule identifier and gives arbitrary codes. |
| 15 | no | n | arbitrary | `CAST(atom_id AS REAL)` (always 0) is output and `CAST(molecule_id AS REAL)` is the sort key for LIMIT 5, so identifiers are used as numbers and which 5 rows come back is undefined. |
| 16 | no | y | arbitrary | Constants only (`(2/0.1)/(0/5)`, division by zero) in both output and filter. |
| 17 | no | y | arbitrary | Constants only (`round(2,4)/round(2,4)`, x/x, weight chains). |
| 18 | no | y | arbitrary | `sqrt((1 - CASE(bond_type = '=' THEN 1 ELSE 2)*10/5) ...)`: bond type coded 1/2 (double bond coded lower than single) in a weight chain with x/x. |
| 19 | no | y | arbitrary | Bond-type CASE code divided by itself (x/x), `CAST(bond_type AS REAL) = '#'` impossible comparison, weight chains. |
| 20 | yes | n | - | Lists molecule ids (one row per atom). |

## Counts

Overall (20): yes 3, uncertain 2, no 15.

With arithmetic (12): yes 0, uncertain 0, no 12.

Causes (17 non-yes): missing evidence 0, lost in propagation 0, arbitrary 17.

## Pattern

Toxicology has no numeric column, so every piece of arithmetic in this sample is built from constants, counts or CASE codes over identifiers and categories; all 12 queries with arithmetic are incoherent, and the 3 acceptable queries are plain join listings. Most of the non-arithmetic failures also treat identifiers as numbers or ranges (`CAST(id AS REAL)`, `molecule_id > 'TR131'`), which the catalogue marks as keys.
