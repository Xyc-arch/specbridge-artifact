# Wrong natural answers by sonnet on `eval12@01cfbb1e713f`: 19, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| values in output k | 12 | 11 |
| does not execute | 6 | 6 |
| rows extra | 1 | 1 |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| 372cec96f5 | 4 | 2 | agg > agg > baseline | passed | does not execute  | yes |  |
| 95f2f15de7 | 3 | 2 | agg > baseline | passed | does not execute  | yes |  |
| e2ae5e3b8f | 4 | 2 | agg > baseline > agg | revised | does not execute  | yes | steps |
| 60a79fabd7 | 4 | 2 | agg > baseline > agg | passed | does not execute  | yes |  |
| 5afc1a8b5c | 3 | 1 | agg > share | passed | does not execute  | yes |  |
| 19bf5ec0c7 | 5 | 1 | agg > share > baseline | revised | does not execute  | yes |  |
| 6c1b7822e6 | 3 | 1 | agg > baseline | passed | rows extra reference 8 rows, answer 10; lacks 0, adds 2 | yes |  |
| 796562a668 | 4 | 2 | agg > baseline > agg | passed | values in output 1  | yes |  |
| 351fb7579b | 6 | 2 | agg > share > baseline > agg | passed | values in output 1  | yes |  |
| 227771660b | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| e97b0fb6be | 4 | 2 | agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| cd6c8a9de0 | 4 | 2 | agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| b3691a7c41 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 6ec8137fd3 | 4 | 2 | agg > agg > baseline | passed | values in output 1,2,3,4  | yes |  |
| 6f949de77e | 4 | 2 | agg > baseline > agg | passed | values in output 1,3  | yes |  |
| 568a31721e | 4 | 2 | agg > baseline > agg | passed | values in output 2,3  | yes |  |
| 5f1a57a3d8 | 6 | 1 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| c759056a31 | 4 | 1 | agg > agg > baseline | passed | values in output 4  | no |  |
| c94de1efe9 | 3 | 2 | agg > baseline | passed | values in output 4,5  | yes |  |
