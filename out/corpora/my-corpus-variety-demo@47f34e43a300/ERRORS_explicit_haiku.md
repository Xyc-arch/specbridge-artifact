# Wrong explicit answers by haiku on `my-corpus-variety-demo@47f34e43a300`: 19, attributed by code (no model calls)

| what differs | wrong | natural arm right on the same task |
|---|---|---|
| values in output k | 16 | 8 |
| does not execute | 2 | 1 |
| wrong column count | 1 | 0 |

| task | S | A | shape | writer status | what differs | natural right | review flagged before |
|---|---|---|---|---|---|---|---|
| 661790a587 | 5 | 2 | agg > agg > baseline > agg | passed | does not execute  | no |  |
| 7ecd0ccf12 | 5 | 2 | agg > baseline > baseline | passed | does not execute  | yes |  |
| ab3bdecde5 | 5 | 1 | agg > agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 31c31588d4 | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | no |  |
| 2cb0c36697 | 5 | 1 | agg > baseline > agg > agg | passed | values in output 1,2,3  | yes |  |
| acfe87cb18 | 6 | 1 | agg > baseline > baseline > agg | revised | values in output 1,2,3  | no | output 1, output 2, output 3, steps |
| 9ebf452be6 | 6 | 1 | agg > baseline > baseline > agg | revised | values in output 1,2,3  | no | output 1, output 2, output 3, steps |
| 4ac33e8753 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 3 |
| 6eee64ddd2 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | no | output 1, output 2, output 3, steps |
| 712f74ccc0 | 4 | 2 | agg > baseline > agg | passed | values in output 2  | no |  |
| b9c241ade0 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | no |  |
| be79b32ae0 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | no |  |
| ffd7f9ee30 | 4 | 2 | agg > agg > baseline | passed | values in output 3  | no |  |
| 7a7de1cae1 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 3  | yes |  |
| 70110b7f8f | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 3  | yes |  |
| e8217c6ad8 | 4 | 1 | agg > agg > baseline | passed | values in output 4  | yes |  |
| 0e7f239d43 | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| d5c3d5a503 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| a022a78cb1 | 5 | 2 | agg > baseline > baseline | passed | wrong column count expected 4, got 3 | no |  |
