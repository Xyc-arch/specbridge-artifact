# Wrong natural answers by haiku on `my-corpus-variety-demo@8fc775be66aa`: 28, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| values in output k | 18 | 17 |
| does not execute | 5 | 2 |
| rows extra | 2 | 0 |
| within 0.1% (rounding) | 2 | 2 |
| rows missing | 1 | 0 |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| c9a6394a59 | 4 | 2 | agg > baseline > agg | revised | does not execute  | yes |  |
| b26a81fe5b | 5 | 1 | agg > baseline > agg > agg | revised | does not execute  | yes | steps |
| 105c9f7d31 | 6 | 2 | agg > baseline > baseline > agg | revised | does not execute  | no | steps |
| 9fc3f477f1 | 6 | 2 | agg > baseline > baseline > agg | revised | does not execute  | no | steps |
| 27a141590a | 6 | 2 | agg > baseline > baseline > agg | revised | does not execute  | no | steps |
| ca113ce007 | 6 | 1 | agg > agg > baseline > baseline | revised | rows extra reference 2 rows, answer 4; lacks 0, adds 2 | no | steps |
| eca5fe7474 | 5 | 1 | agg > share > baseline | revised | rows extra reference 21 rows, answer 23; lacks 21, adds 23 | no | output 4 |
| fd7413b80d | 6 | 1 | agg > agg > baseline > baseline | passed | rows missing reference 2 rows, answer 1; lacks 1, adds 0 | no |  |
| cebaf61275 | 5 | 1 | agg > agg > baseline > agg | revised | values in output 1,2,3  | yes | output 1 |
| 1e4e3c462b | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | no |  |
| dbbe89e0c4 | 6 | 1 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| e566b11c72 | 6 | 1 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 2f2bdd36c4 | 4 | 2 | agg > baseline > agg | revised | values in output 2,3  | yes | steps |
| deed201a1f | 6 | 2 | agg > share > baseline > agg | revised | values in output 2,3  | yes | output 2 |
| 68ec5734b8 | 4 | 2 | agg > agg > baseline | revised | values in output 2,3,4  | yes | output 4 |
| 588d6214f4 | 4 | 2 | agg > agg > baseline | revised | values in output 2,3,4  | yes | output 4 |
| ff78ae7e78 | 5 | 2 | agg > agg > baseline > agg | revised | values in output 3  | yes | steps |
| 2b8247c61d | 4 | 2 | agg > baseline > agg | revised | values in output 3  | yes | steps |
| 00ad2e2f6c | 5 | 2 | agg > baseline > baseline | revised | values in output 3  | yes |  |
| c1de691148 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 3  | yes |  |
| a4126a616c | 4 | 1 | agg > agg > baseline | revised | values in output 3,4  | yes | output 4 |
| 5ced20d0a8 | 3 | 2 | agg > baseline | passed | values in output 3,4  | yes |  |
| b46cc124bf | 3 | 2 | agg > baseline | revised | values in output 3,4  | yes |  |
| 0a3260ce79 | 4 | 2 | agg > agg > baseline | passed | values in output 4  | yes |  |
| 3311e9b075 | 4 | 2 | agg > agg > baseline | passed | values in output 4  | yes |  |
| 7c18795a4c | 5 | 1 | agg > share > baseline | passed | values in output 4  | yes |  |
| 6580de1893 | 4 | 2 | agg > baseline > agg | revised | within 0.1% (rounding)  | yes | output 1 |
| dfcfe36c7e | 6 | 2 | agg > baseline > baseline > agg | revised | within 0.1% (rounding)  | yes | steps |
