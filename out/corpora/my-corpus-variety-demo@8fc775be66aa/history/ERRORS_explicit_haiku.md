# Wrong explicit answers by haiku on `my-corpus-variety-demo@8fc775be66aa`: 51, attributed by code (no model calls)

| what differs | wrong | natural arm right on the same task |
|---|---|---|
| values in output k | 37 | 27 |
| does not execute | 11 | 9 |
| wrong column count | 2 | 2 |
| rows missing | 1 | 0 |

| task | S | A | shape | writer status | what differs | natural right | review flagged before |
|---|---|---|---|---|---|---|---|
| d0123c871e | 4 | 2 | agg > agg > baseline | revised | does not execute  | yes |  |
| 9f7d84bf19 | 4 | 2 | agg > agg > baseline | revised | does not execute  | yes |  |
| e378517cdf | 6 | 1 | agg > agg > baseline > baseline | passed | does not execute  | yes |  |
| ca113ce007 | 6 | 1 | agg > agg > baseline > baseline | revised | does not execute  | no | steps |
| 1d62ac6cea | 3 | 2 | agg > baseline | passed | does not execute  | yes |  |
| 672c725f5a | 3 | 2 | agg > baseline | passed | does not execute  | yes |  |
| f482716d03 | 4 | 1 | agg > baseline > agg | explicit fallback | does not execute  | no |  |
| 9e016a001c | 6 | 1 | agg > baseline > baseline > agg | passed | does not execute  | yes |  |
| 9f90069e77 | 6 | 1 | agg > baseline > baseline > agg | passed | does not execute  | yes |  |
| 0543fb1ebd | 3 | 2 | agg > rank | revised | does not execute  | yes |  |
| 26762e0f16 | 3 | 2 | agg > rank | revised | does not execute  | yes |  |
| fd7413b80d | 6 | 1 | agg > agg > baseline > baseline | passed | rows missing reference 2 rows, answer 1; lacks 2, adds 1 | no |  |
| 37e4c0f680 | 5 | 1 | agg > agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 78242eb3f8 | 4 | 1 | agg > baseline > agg | passed | values in output 1,2,3  | yes |  |
| d9f384b2ce | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 42374d3f1e | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 38d58a9711 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 4a40af25a7 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| f7eb354486 | 6 | 1 | agg > baseline > baseline > agg | revised | values in output 1,2,3  | yes | steps |
| f5e17f7da2 | 6 | 2 | agg > baseline > baseline > agg | revised | values in output 1,2,3  | yes | steps |
| 27a141590a | 6 | 2 | agg > baseline > baseline > agg | revised | values in output 1,2,3  | no | steps |
| 627e0ff6e6 | 5 | 2 | agg > baseline > baseline | revised | values in output 1,2,3,4  | yes | output 4 |
| 57328c6d64 | 5 | 1 | agg > share > share | revised | values in output 1,2,3,4  | yes | output 4 |
| fcc84eafa1 | 3 | 2 | agg > baseline | passed | values in output 1,3,4,5  | yes |  |
| 3ed1291214 | 6 | 2 | agg > share > baseline > agg | passed | values in output 2,3  | yes |  |
| 9d0d0db660 | 6 | 2 | agg > share > baseline > agg | passed | values in output 2,3  | yes |  |
| 35ee5e7a6e | 4 | 1 | agg > agg > baseline | passed | values in output 2,3,4  | yes |  |
| e2adbcdff5 | 3 | 1 | agg > baseline | passed | values in output 3  | yes |  |
| abd8c575d1 | 3 | 2 | agg > baseline | passed | values in output 3  | yes |  |
| dedf0dbd5d | 3 | 2 | agg > baseline | passed | values in output 3  | yes |  |
| 1e4e3c462b | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 3  | no |  |
| 105c9f7d31 | 6 | 2 | agg > baseline > baseline > agg | revised | values in output 3  | no | output 3, steps |
| 9fc3f477f1 | 6 | 2 | agg > baseline > baseline > agg | revised | values in output 3  | no | output 3, steps |
| 8af7834097 | 6 | 2 | agg > baseline > baseline > agg | explicit fallback | values in output 3  | no | steps |
| d3baf8c043 | 6 | 2 | agg > baseline > baseline > agg | explicit fallback | values in output 3  | no | steps |
| 260c4c8123 | 6 | 2 | agg > baseline > baseline > agg | explicit fallback | values in output 3  | no | steps |
| 6f76b59bda | 6 | 2 | agg > baseline > baseline > agg | explicit fallback | values in output 3  | no | steps |
| 3af108cd81 | 5 | 2 | agg > share > baseline | passed | values in output 3,4  | yes |  |
| 271a65995e | 4 | 2 | agg > agg > baseline | passed | values in output 4  | yes |  |
| fbf0148292 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | steps |
| 5e08d6f4b3 | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| 4562ca048c | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| 29b13bc023 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 4a5ae5f1d8 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 6f1a5291c3 | 5 | 2 | agg > baseline > baseline | revised | values in output 4  | yes | output 4, steps |
| 6a390fa9c1 | 5 | 2 | agg > baseline > baseline | revised | values in output 4  | yes | output 4, steps |
| 416681ae00 | 5 | 2 | agg > baseline > baseline | explicit fallback | values in output 4  | no | output 4 |
| 00dafda0c2 | 5 | 2 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| eca5fe7474 | 5 | 1 | agg > share > baseline | revised | values in output 4  | no | output 4 |
| 1451198f10 | 5 | 1 | agg > baseline > baseline | passed | wrong column count expected 4, got 3 | yes |  |
| 556dbe9401 | 5 | 1 | agg > baseline > baseline | passed | wrong column count expected 4, got 3 | yes |  |
