# Wrong natural answers by haiku on `my-corpus-variety-demo@47f34e43a300`: 17, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| values in output k | 9 | 5 |
| does not execute | 6 | 1 |
| wrong column count | 1 | 0 |
| rows missing | 1 | 1 |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| ffd7f9ee30 | 4 | 2 | agg > agg > baseline | passed | does not execute  | no |  |
| 661790a587 | 5 | 2 | agg > agg > baseline > agg | passed | does not execute  | no |  |
| 57ab16ed07 | 4 | 1 | agg > agg > share | passed | does not execute  | yes |  |
| 712f74ccc0 | 4 | 2 | agg > baseline > agg | passed | does not execute  | no |  |
| acfe87cb18 | 6 | 1 | agg > baseline > baseline > agg | revised | does not execute  | no | steps |
| 9ebf452be6 | 6 | 1 | agg > baseline > baseline > agg | revised | does not execute  | no | steps |
| e24b1d1c17 | 5 | 2 | agg > baseline > baseline | passed | rows missing reference 10 rows, answer 9; lacks 1, adds 0 | yes |  |
| 4eb64e671e | 4 | 1 | agg > share > agg | revised | values in output 1  | yes | output 1 |
| 31c31588d4 | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | no |  |
| 08c7aee74a | 6 | 2 | agg > baseline > agg > baseline | passed | values in output 1,2,3,4  | yes |  |
| b9c241ade0 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | no |  |
| be79b32ae0 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | no |  |
| add45b7fea | 4 | 2 | agg > baseline > agg | passed | values in output 3  | yes |  |
| 6eee64ddd2 | 6 | 1 | agg > share > baseline > agg | revised | values in output 3  | no | output 3, steps |
| dadb9a0c56 | 6 | 1 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| 976fc78103 | 5 | 2 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| a022a78cb1 | 5 | 2 | agg > baseline > baseline | passed | wrong column count expected 4, got 3 | no |  |
