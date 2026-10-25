# Wrong natural answers by haiku on `my-corpus-variety-demo@b223964d8a45`: 19, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| values in output k | 8 | not run |
| does not execute | 8 | not run |
| rows missing | 2 | not run |
| wrong column count | 1 | not run |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| ffd7f9ee30 | 4 | 2 | agg > agg > baseline | passed | does not execute  | not run |  |
| 661790a587 | 5 | 2 | agg > agg > baseline > agg | passed | does not execute  | not run |  |
| 2d4318d213 | 6 | 1 | agg > agg > baseline > baseline | revised | does not execute  | not run |  |
| 0439b4e7ae | 6 | 1 | agg > agg > baseline > baseline | revised | does not execute  | not run |  |
| 57ab16ed07 | 4 | 1 | agg > agg > share | passed | does not execute  | not run |  |
| 712f74ccc0 | 4 | 2 | agg > baseline > agg | passed | does not execute  | not run |  |
| acfe87cb18 | 6 | 1 | agg > baseline > baseline > agg | revised | does not execute  | not run | steps |
| 9ebf452be6 | 6 | 1 | agg > baseline > baseline > agg | revised | does not execute  | not run | steps |
| b3bf0189b5 | 6 | 1 | agg > agg > baseline > baseline | passed | rows missing reference 1 rows, answer 0; lacks 1, adds 0 | not run |  |
| e24b1d1c17 | 5 | 2 | agg > baseline > baseline | passed | rows missing reference 10 rows, answer 9; lacks 1, adds 0 | not run |  |
| 4eb64e671e | 4 | 1 | agg > share > agg | revised | values in output 1  | not run | output 1 |
| 31c31588d4 | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | not run |  |
| 08c7aee74a | 6 | 2 | agg > baseline > agg > baseline | passed | values in output 1,2,3,4  | not run |  |
| b9c241ade0 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | not run |  |
| be79b32ae0 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | not run |  |
| add45b7fea | 4 | 2 | agg > baseline > agg | passed | values in output 3  | not run |  |
| 6eee64ddd2 | 6 | 1 | agg > share > baseline > agg | revised | values in output 3  | not run | output 3, steps |
| 976fc78103 | 5 | 2 | agg > baseline > baseline | passed | values in output 4  | not run |  |
| a022a78cb1 | 5 | 2 | agg > baseline > baseline | passed | wrong column count expected 4, got 3 | not run |  |
