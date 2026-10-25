# store_1: why are 20 calculations UNKNOWN? (manual review)

Causes: 1 = catalogue lacks it; 2 = propagation loses it; 3 = no supported interpretation.

| id | cause | reason |
|---|---|---|
| u1 | 3 | `(1 - CASE addr > '700 W Pender' ...) + (1 - CASE ...) * ROUND(count / o1)`: score CASEs on billing-address string order, times a count divided by an arbitrary bytes x ms x currency average. |
| u2 | 3 | `(bytes/8107896) * (1-(1-ms/255634)) + (bytes*0.25)^2 + (ms/ms)*5 / bytes`: squared bytes, x/x and a relative-size x relative-duration product; the bytes-per-ms rate fact is not what is computed. |
| u3 | 3 | Score CASEs over `total / (2*total + total/3.96)` (a constant 0.44 for every row) and postal-code string order, multiplied together; arbitrary. |
| u4 | 3 | `COALESCE(ROUND(1,2))/COALESCE(ROUND(1,2))` and CASEs on it: arithmetic on constants only (x/x on a literal). |
| u5 | 3 | Every leaf is `CAST(0 AS REAL)` times weights: arithmetic on constants only (evaluates to 0 or NULL). |
| u6 | 3 | `(1 - CASE addr > 'Av. Paulista' THEN 4 ...) * ROUND(count / o1)`: an address-order score times a count per (bytes x ms x currency). |
| u7 | 3 | `1 - POWER(1.5, 2)`: arithmetic on constants only. |
| u8 | 3 | `(o0/o0) + CASE (o0/o0) > ROUND(o0/o0)*0.5`: x/x on a step output (itself a constants-only score); arbitrary. |
| u9 | 3 | `1 - ROUND(bytes)`: subtracting a file size in bytes from 1 has no meaning; the unit survived, the operation is the problem. |
| u10 | 3 | `(CAST(1.5 AS INTEGER)*10) * (ROUND(2,2) + SQRT(2))`: arithmetic on constants only. |
| u11 | 3 | `(0.5/(o1*0.2)) / ((1 - o1/COALESCE(o1,0))*1.5 * CASE ...)`: x/x on a constants-only step output, then a genre-id-thresholded CASE; arbitrary. |
| u12 | 3 | `((1 - (bytes/8107896)*(ms*3))/2) * (total*3)`: relative size times duration, subtracted from 1, times an invoice total; unrelated quantities (a track's size/length and a whole invoice's amount). |
| u13 | 3 | Same as u10: `(CAST(1.5 AS INTEGER)*10) * (ROUND(2,2) + SQRT(2))`, constants only. |
| u14 | 3 | `(ms*0.2)/ms`: x/x scaled, equal to 0.2 for every row. |
| u15 | 3 | `count / AVG((1 - bytes x ms)/2 * total*3)`: a row count divided by an arbitrary bytes x ms x currency product. |
| u16 | 3 | `CASE COALESCE(0,0)=0 THEN 3 ...` divided through x/x of the same CASE: constants only. |
| u17 | 3 | `(bytes*ms*2/10) * (bytes*ms*2)`: squares a bytes x ms product; the catalogue fact is bytes PER ms, and the product has no meaning. |
| u18 | 3 | `(1 - ms/255634) * (1 - 0.2/ms)`: one minus a relative duration times one minus 0.2 per millisecond; no interpretation. |
| u19 | 3 | `((bytes/8107896 + 1) * (1280000 - ms*5))^2 * (ms / same)`: arbitrary polynomial in relative size and shifted duration. |
| u20 | 3 | `1 - CASE (employee last_name > 'Peacock' AND postal code = '1000' AND bytes/8107896 > 1) THEN 1 ELSE 3`: a score from names and a postal code joined with track size; arbitrary. |

## Counts

| cause | n |
|---|---|
| 1 catalogue lacks it | 0 |
| 2 propagation loses it | 0 |
| 3 no supported interpretation | 20 |

## Pattern

All twenty UNKNOWN calculations in store_1 are incoherent by construction: seven are constants-only or x/x, and the rest combine bytes, milliseconds, invoice totals, counts and string-ordered score CASEs in ways no domain fact could support. The UNKNOWN bucket here is not a gap in the catalogue or in propagation; the one real rate fact (bytes per ms) is never what the generator computes.
