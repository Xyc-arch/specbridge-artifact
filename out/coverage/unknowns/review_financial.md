# financial: why 20 UNKNOWN calculations are unknown

Causes: 1 = catalogue lacks it, 2 = propagation loses it, 3 = no supported interpretation.

| id | cause | reason |
|---|---|---|
| u1 | 3 | `1 - log(10,10)` is constants only (= 0). |
| u2 | 3 | `loan.payments / loan.payments` is x/x, identically 1. |
| u3 | 3 | `trans.balance - trans.balance` is x - x, identically 0. |
| u4 | 3 | `1 - (round(2,2)/3)*0.25` is constants only. |
| u5 | 3 | `round(amount*(1-amount)) / round(amount*(1-amount))` is x/x, and `amount*(1-amount)` (USD squared minus USD) has no meaning in the first place. |
| u6 | 3 | `trans.balance - trans.balance` is x - x, identically 0 (same query as u3). |
| u7 | 3 | `1 - log(10,10)/3` is constants only. |
| u8 | 3 | `order.amount / order.amount` is x/x, identically 1. |
| u9 | 3 | `loan.payments * loan.amount` multiplies two money amounts on the same loan, giving USD squared; no domain quantity is a product of payment and principal. |
| u10 | 3 | Arithmetic on `CASE WHEN disp.client_id < 1418 THEN 2 ELSE 0 END`: an identifier range turned into a number, then x/x and x - x/x of it. |
| u11 | 1 | `(payments*5*duration) / (amount*2)` is 2.5 x (total repaid / principal), a meaningful repayment ratio; the catalogue has no fact that payments x duration is a total comparable to amount (only a `why` text says "amount = payments x duration"), though the 5/2 scaling is itself unexplained. |
| u12 | 3 | Arithmetic on a CASE comparing a district_id flag with client_id: identifiers compared and used as numbers, then divided by themselves. |
| u13 | 3 | `(2/0.25) * (1 - log(10,10))` is constants only (= 0). |
| u14 | 3 | `(0.2 duration) / (0.1 duration * (payments*amount + 0.2 duration))`: months over months times (USD squared plus months); mixes incompatible units through arbitrary weights. |
| u15 | 3 | `CAST(COUNT(*) AS REAL) / COUNT(*)` over a step output is x/x, identically 1. |
| u16 | 3 | Same x/x of a row count as u15. |
| u17 | 3 | `(amount/2007/0.75/0.75) * (amount/1000*5)` is amount squared times arbitrary constants; USD squared has no meaning. |
| u18 | 3 | `1 - CASE WHEN disp.client_id < 1418 THEN 2 ELSE 0 END`: an identifier threshold used as a number. |
| u19 | 3 | Sum and ratio of CASE scores built by comparing district_id and client_id (identifiers); x/x of the same CASE. |
| u20 | 3 | `amount/2007*10 - (amount^2 chain)/3 + CASE(power(x,1.5) != power(x,1.5))`: USD minus USD squared plus a CASE on a test that is always false. |

## Counts

| cause | count |
|---|---|
| 1 catalogue lacks it | 1 |
| 2 propagation loses it | 0 |
| 3 no supported interpretation | 19 |

## Pattern

The UNKNOWN bucket is filled with degenerate arithmetic: constants only (u1, u4, u7, u13), x/x or x - x (u2, u3, u5, u6, u8, u15, u16), identifiers such as client_id and district_id used as numbers, and products of money with money. Only u11 is a real quantity the catalogue could have supported, and even it carries an unexplained 5/2 factor, so improving the catalogue or propagation would move almost nothing; the fix is upstream in what the generator is allowed to compose.
