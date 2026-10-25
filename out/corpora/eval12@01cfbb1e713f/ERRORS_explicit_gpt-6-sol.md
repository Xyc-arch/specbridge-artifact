# Wrong explicit answers by gpt-6-sol on `eval12@01cfbb1e713f`: 4, attributed by code (no model calls)

| what differs | wrong | natural arm right on the same task |
|---|---|---|
| values in output k | 2 | 2 |
| does not execute | 1 | 1 |
| rows missing | 1 | 1 |

| task | S | A | shape | writer status | what differs | natural right | review flagged before |
|---|---|---|---|---|---|---|---|
| 5767740452 | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| 4548f50304 | 5 | 1 | agg > share > share | passed | rows missing reference 10 rows, answer 1; lacks 10, adds 1 | yes |  |
| 69f4c578b6 | 5 | 2 | agg > baseline > baseline | revised | values in output 1,2,3,4,5  | yes | output 1, steps |
| 6f2aa8e36b | 5 | 2 | agg > baseline > baseline | revised | values in output 5  | yes |  |
