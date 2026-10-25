# Wrong natural answers by gpt-6-luna on `eval12@01cfbb1e713f`: 49, attributed by code (no model calls)

| what differs | wrong | explicit arm right on the same task |
|---|---|---|
| does not execute | 28 | 22 |
| values in output k | 17 | 9 |
| rows missing | 2 | 0 |
| column order only | 1 | 1 |
| wrong column count | 1 | 1 |

| task | S | A | shape | writer status | what differs | explicit right | review flagged before |
|---|---|---|---|---|---|---|---|
| aed8b6c38d | 4 | 2 | agg > baseline > agg | passed | column order only  | yes |  |
| cc8ea36cdf | 4 | 1 | agg > agg > baseline | revised | does not execute  | no | steps |
| 6782deeb9c | 6 | 2 | agg > agg > share > baseline | revised | does not execute  | no | steps |
| f74c2bad9d | 3 | 1 | agg > baseline | revised | does not execute  | yes | steps |
| fecab5d065 | 3 | 2 | agg > baseline | revised | does not execute  | yes | steps |
| dabca577ba | 3 | 1 | agg > baseline | passed | does not execute  | yes |  |
| 47e074c369 | 4 | 1 | agg > baseline > agg | revised | does not execute  | yes | steps |
| 4a5a98cb42 | 4 | 1 | agg > baseline > agg | revised | does not execute  | yes | steps |
| 7b6fd5bf32 | 4 | 1 | agg > baseline > agg | passed | does not execute  | yes |  |
| 43277f1d9e | 4 | 2 | agg > baseline > agg | revised | does not execute  | yes | steps |
| ff5d7b5c34 | 5 | 1 | agg > baseline > rank | passed | does not execute  | yes |  |
| f447a6c8c2 | 6 | 1 | agg > baseline > share > agg | revised | does not execute  | yes | steps |
| 3c7c06f41c | 3 | 1 | agg > share | revised | does not execute  | yes | steps |
| 6d98a71a6f | 3 | 1 | agg > share | revised | does not execute  | yes | steps |
| b77a784ee8 | 3 | 1 | agg > share | passed | does not execute  | yes |  |
| e6f24d2438 | 3 | 1 | agg > share | passed | does not execute  | yes |  |
| 3cc388876c | 3 | 1 | agg > share | passed | does not execute  | yes |  |
| 6060d223ca | 4 | 1 | agg > share > agg | passed | does not execute  | yes |  |
| 1490d5931d | 5 | 1 | agg > share > baseline | revised | does not execute  | no | steps |
| 19bf5ec0c7 | 5 | 1 | agg > share > baseline | revised | does not execute  | yes |  |
| 7cea9b27d7 | 5 | 2 | agg > share > baseline | revised | does not execute  | yes | steps |
| 62ba8997e3 | 5 | 2 | agg > share > baseline | revised | does not execute  | yes | steps |
| 1d32493574 | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| b6c41d0861 | 5 | 2 | agg > share > baseline | passed | does not execute  | no |  |
| 96d38a34f5 | 5 | 2 | agg > share > baseline | passed | does not execute  | no |  |
| a83a9b0bf3 | 6 | 1 | agg > share > baseline > agg | revised | does not execute  | no | steps |
| 7d77e789e0 | 6 | 2 | agg > share > baseline > agg | revised | does not execute  | yes | steps |
| 9b5fcd3c98 | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| 6c0edf283c | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| 1d21023bca | 4 | 2 | agg > agg > baseline | passed | rows missing reference 2 rows, answer 0; lacks 2, adds 0 | no |  |
| 0b823e7291 | 5 | 2 | agg > share > baseline | passed | rows missing reference 2 rows, answer 0; lacks 2, adds 0 | no |  |
| f4c20a1c18 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1  | yes |  |
| 93eb8cae64 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1,2  | no |  |
| 227771660b | 5 | 2 | agg > agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| cd6c8a9de0 | 4 | 2 | agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 0d00bc9e2f | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | no |  |
| 6ec8137fd3 | 4 | 2 | agg > agg > baseline | passed | values in output 1,2,3,4  | yes |  |
| 6ffe9412f1 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1,3  | yes |  |
| 7ae2c8dd86 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3  | yes |  |
| 6e06ef65bb | 4 | 1 | agg > baseline > agg | passed | values in output 3  | yes |  |
| 27a1576683 | 4 | 1 | agg > baseline > agg | passed | values in output 3  | yes |  |
| 156f4616e3 | 5 | 1 | agg > baseline > share | revised | values in output 3  | no | output 3, steps |
| 69c4bd1cc2 | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | no |  |
| 97769b0922 | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | no |  |
| bbce981d7b | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | yes |  |
| b437ed00a4 | 6 | 2 | agg > share > baseline > agg | passed | values in output 3  | no |  |
| 5f1a57a3d8 | 6 | 1 | agg > share > baseline > agg | passed | values in output 3  | no |  |
| c759056a31 | 4 | 1 | agg > agg > baseline | passed | values in output 4  | no |  |
| b06ce2f77f | 3 | 1 | agg > share | passed | wrong column count expected 3, got 4 | yes |  |
