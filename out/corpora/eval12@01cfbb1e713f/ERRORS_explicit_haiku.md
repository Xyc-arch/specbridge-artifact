# Wrong explicit answers by haiku on `eval12@01cfbb1e713f`: 39, attributed by code (no model calls)

| what differs | wrong | natural arm right on the same task |
|---|---|---|
| values in output k | 20 | 19 |
| does not execute | 16 | 16 |
| rows missing | 1 | 0 |
| rows extra | 1 | 0 |
| wrong column count | 1 | 1 |

| task | S | A | shape | writer status | what differs | natural right | review flagged before |
|---|---|---|---|---|---|---|---|
| 661e8a78a6 | 6 | 1 | agg > agg > baseline > baseline | revised | does not execute  | yes |  |
| f74c2bad9d | 3 | 1 | agg > baseline | revised | does not execute  | yes | steps |
| 7fd142e2d9 | 3 | 1 | agg > baseline | passed | does not execute  | yes |  |
| 44b6f11fee | 4 | 1 | agg > baseline > agg | revised | does not execute  | yes | steps |
| 60a79fabd7 | 4 | 2 | agg > baseline > agg | passed | does not execute  | yes |  |
| c752b1c31e | 4 | 1 | agg > baseline > agg | passed | does not execute  | yes |  |
| 9bb5ac76bd | 4 | 1 | agg > baseline > agg | revised | does not execute  | yes | steps |
| 329cb50dc6 | 5 | 2 | agg > baseline > baseline | revised | does not execute  | yes |  |
| d77c2a5427 | 3 | 1 | agg > share | revised | does not execute  | yes | steps |
| 4803115adb | 5 | 1 | agg > share > agg > agg | passed | does not execute  | yes |  |
| 40a0836cfa | 5 | 2 | agg > share > baseline | revised | does not execute  | yes |  |
| 594daaf4d2 | 6 | 1 | agg > share > baseline > agg | revised | does not execute  | yes | steps |
| 4eb2b4a71e | 6 | 2 | agg > share > baseline > agg | revised | does not execute  | yes | steps |
| 9c0b51a6fd | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| d2672cd3d8 | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| f2fce9cad5 | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| 0a50862c56 | 5 | 1 | agg > share > baseline | revised | rows extra reference 5 rows, answer 25; lacks 5, adds 25 | no | output 4, steps |
| eb95650b54 | 3 | 1 | agg > share | passed | rows missing reference 26 rows, answer 25; lacks 26, adds 25 | no |  |
| 6cae1b0182 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | steps |
| 4781ec3c60 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 3, steps |
| 5477f91118 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 1, output 2, output 3, steps |
| 5f1a57a3d8 | 6 | 1 | agg > share > baseline > agg | passed | values in output 1,2,3  | no |  |
| f15bc8b0f4 | 3 | 1 | agg > baseline | revised | values in output 1,2,4  | yes | steps |
| 297a8510dc | 6 | 1 | agg > share > baseline > agg | revised | values in output 3  | yes | output 3, steps |
| 6c21dc4586 | 4 | 1 | agg > agg > share | passed | values in output 4  | yes |  |
| 4aa1861890 | 6 | 1 | agg > agg > share > baseline | passed | values in output 4  | yes |  |
| 76c9060c40 | 3 | 2 | agg > baseline | passed | values in output 4  | yes |  |
| 1d3fc42a2c | 3 | 2 | agg > baseline | passed | values in output 4  | yes |  |
| 0a25f556c5 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | steps |
| de9929d7a2 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4, steps |
| 4a2d376afa | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 64e48775c7 | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| 7c4a89c45b | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| f447a6c8c2 | 6 | 1 | agg > baseline > share > agg | revised | values in output 4  | yes | steps |
| 371d74781b | 5 | 1 | agg > share > baseline | revised | values in output 4  | yes | output 4 |
| 9b4ed1d4af | 5 | 1 | agg > share > baseline | revised | values in output 4  | yes | steps |
| 8f823fb0da | 5 | 1 | agg > share > baseline | revised | values in output 4  | yes | output 4 |
| 65650763a2 | 5 | 1 | agg > share > baseline | revised | values in output 4  | yes | output 4, steps |
| 57a9e7cbbf | 5 | 1 | agg > share > agg > agg | revised | wrong column count expected 3, got 1 | yes | steps |
