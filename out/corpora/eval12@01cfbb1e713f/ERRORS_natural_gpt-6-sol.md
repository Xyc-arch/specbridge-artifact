# Wrong natural answers by gpt-6-sol on `eval12@01cfbb1e713f`: 18, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| values in output k | 14 | 14 |
| rows extra | 2 | 2 |
| does not execute | 1 | 1 |
| rows missing | 1 | 1 |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| fecab5d065 | 3 | 2 | agg > baseline | revised | does not execute  | yes | steps |
| 6c1b7822e6 | 3 | 1 | agg > baseline | passed | rows extra reference 8 rows, answer 10; lacks 0, adds 2 | yes |  |
| bd51f2bd3c | 3 | 2 | agg > baseline | passed | rows extra reference 9 rows, answer 10; lacks 0, adds 1 | yes |  |
| 91cfb4e1db | 6 | 2 | agg > baseline > baseline > agg | revised | rows missing reference 4 rows, answer 1; lacks 4, adds 1 | yes | steps |
| 227771660b | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 0d00bc9e2f | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| ef4d2acbf1 | 6 | 2 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 6ec8137fd3 | 4 | 2 | agg > agg > baseline | passed | values in output 1,2,3,4  | yes |  |
| 5ae33e9bfe | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2  | yes |  |
| 568a31721e | 4 | 2 | agg > baseline > agg | passed | values in output 2,3  | yes |  |
| 69dd47a5b6 | 4 | 2 | agg > agg > baseline | passed | values in output 3  | yes |  |
| 156f4616e3 | 5 | 1 | agg > baseline > share | revised | values in output 3  | yes | output 3, steps |
| 69c4bd1cc2 | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| 97769b0922 | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| bbce981d7b | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| 5f1a57a3d8 | 6 | 1 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| c759056a31 | 4 | 1 | agg > agg > baseline | passed | values in output 4  | yes |  |
| c94de1efe9 | 3 | 2 | agg > baseline | passed | values in output 4,5  | yes |  |
