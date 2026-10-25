# Wrong natural answers by haiku on `eval12@01cfbb1e713f`: 33, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| values in output k | 16 | 15 |
| does not execute | 6 | 6 |
| within 0.1% (rounding) | 4 | 4 |
| rows missing | 4 | 3 |
| wrong column count | 2 | 2 |
| rows extra | 1 | 0 |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| 6b346d7be2 | 4 | 1 | agg > agg > share | passed | does not execute  | yes |  |
| 6c50e3c2db | 4 | 2 | agg > baseline > agg | passed | does not execute  | yes |  |
| 40434115e8 | 5 | 1 | agg > baseline > baseline | revised | does not execute  | yes |  |
| 0535af1821 | 3 | 2 | agg > rank | passed | does not execute  | yes |  |
| 31caaab8c7 | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| 989c45ebd2 | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| 0a50862c56 | 5 | 1 | agg > share > baseline | revised | rows extra reference 5 rows, answer 6; lacks 5, adds 6 | no | output 4, steps |
| eb95650b54 | 3 | 1 | agg > share | passed | rows missing reference 26 rows, answer 25; lacks 26, adds 25 | no |  |
| 5767740452 | 5 | 2 | agg > share > baseline | passed | rows missing reference 2 rows, answer 0; lacks 2, adds 0 | yes |  |
| f55d097c07 | 5 | 2 | agg > share > baseline | passed | rows missing reference 3 rows, answer 0; lacks 3, adds 0 | yes |  |
| 70ea90e305 | 5 | 2 | agg > share > baseline | passed | rows missing reference 4 rows, answer 3; lacks 4, adds 3 | yes |  |
| 568a31721e | 4 | 2 | agg > baseline > agg | passed | values in output 1  | yes |  |
| 4e90c69b8d | 5 | 1 | agg > agg > baseline > agg | passed | values in output 1,2  | yes |  |
| 227771660b | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 0f4fb81d6a | 6 | 1 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 9b5fcd3c98 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 6ec8137fd3 | 4 | 2 | agg > agg > baseline | passed | values in output 1,2,3,4  | yes |  |
| 6a3d55f581 | 3 | 2 | agg > baseline | passed | values in output 1,3,4  | yes |  |
| 7e75655320 | 5 | 1 | agg > share > baseline | revised | values in output 1,3,4  | yes | output 4, steps |
| 00d65781cc | 6 | 1 | agg > share > baseline > agg | revised | values in output 2  | yes | steps |
| 69dd47a5b6 | 4 | 2 | agg > agg > baseline | passed | values in output 3  | yes |  |
| dcc30e7f72 | 3 | 2 | agg > baseline | passed | values in output 3  | yes |  |
| 27a1576683 | 4 | 1 | agg > baseline > agg | passed | values in output 3  | yes |  |
| 5f1a57a3d8 | 6 | 1 | agg > share > baseline > agg | passed | values in output 3  | no |  |
| fea75e8f25 | 5 | 1 | agg > baseline > baseline | passed | values in output 3,4  | yes |  |
| c759056a31 | 4 | 1 | agg > agg > baseline | passed | values in output 4  | yes |  |
| 4cabfc6bd3 | 5 | 2 | agg > share > baseline | passed | values in output 4  | yes |  |
| e91472f3f0 | 3 | 1 | agg > baseline | passed | within 0.1% (rounding)  | yes |  |
| 5afc1a8b5c | 3 | 1 | agg > share | passed | within 0.1% (rounding)  | yes |  |
| 6d6f7152eb | 5 | 2 | agg > share > baseline | passed | within 0.1% (rounding)  | yes |  |
| a0375d75e0 | 6 | 2 | agg > share > baseline > agg | passed | within 0.1% (rounding)  | yes |  |
| cc063db953 | 5 | 1 | agg > agg > baseline > agg | passed | wrong column count expected 2, got 3 | yes |  |
| 01410c6c11 | 5 | 2 | agg > share > baseline | passed | wrong column count expected 4, got 5 | yes |  |
