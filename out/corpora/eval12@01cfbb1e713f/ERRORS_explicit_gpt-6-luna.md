# Wrong explicit answers by gpt-6-luna on `eval12@01cfbb1e713f`: 75, attributed by code (no model calls)

| what differs | wrong | natural arm right on the same task |
|---|---|---|
| values in output k | 44 | 37 |
| does not execute | 21 | 14 |
| wrong column count | 4 | 4 |
| rows extra | 4 | 3 |
| rows missing | 2 | 1 |

| task | S | A | shape | writer status | what differs | natural right | review flagged before |
|---|---|---|---|---|---|---|---|
| cc8ea36cdf | 4 | 1 | agg > agg > baseline | revised | does not execute  | no | steps |
| 6782deeb9c | 6 | 2 | agg > agg > share > baseline | revised | does not execute  | no | steps |
| e2ae5e3b8f | 4 | 2 | agg > baseline > agg | revised | does not execute  | yes | steps |
| 65eee834c9 | 4 | 1 | agg > baseline > agg | passed | does not execute  | yes |  |
| 12d93c67a7 | 4 | 1 | agg > baseline > agg | passed | does not execute  | yes |  |
| d31fb48995 | 6 | 1 | agg > baseline > baseline > agg | revised | does not execute  | yes | steps |
| e5f4d02a7e | 5 | 1 | agg > share > baseline | revised | does not execute  | yes |  |
| 0b823e7291 | 5 | 2 | agg > share > baseline | passed | does not execute  | no |  |
| baa971e60e | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| 5767740452 | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| 7e75655320 | 5 | 1 | agg > share > baseline | revised | does not execute  | yes | steps |
| 6514cf857d | 5 | 1 | agg > share > baseline | revised | does not execute  | yes | steps |
| 22b0e41865 | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| c1a8ce4d18 | 5 | 2 | agg > share > baseline | revised | does not execute  | yes |  |
| b6c41d0861 | 5 | 2 | agg > share > baseline | passed | does not execute  | no |  |
| 0edaef52cd | 5 | 2 | agg > share > baseline | passed | does not execute  | yes |  |
| 96d38a34f5 | 5 | 2 | agg > share > baseline | passed | does not execute  | no |  |
| 2db71a450e | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| 69c4bd1cc2 | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | no |  |
| 93eb8cae64 | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | no |  |
| 9e932237ed | 6 | 2 | agg > share > baseline > agg | passed | does not execute  | yes |  |
| 4aa1861890 | 6 | 1 | agg > agg > share > baseline | passed | rows extra reference 4 rows, answer 999; lacks 4, adds 999 | yes |  |
| f4c15e680b | 5 | 1 | agg > baseline > baseline | passed | rows extra reference 1 rows, answer 2; lacks 1, adds 2 | yes |  |
| 1490d5931d | 5 | 1 | agg > share > baseline | revised | rows extra reference 2 rows, answer 4; lacks 2, adds 4 | no | output 4, steps |
| 0a50862c56 | 5 | 1 | agg > share > baseline | revised | rows extra reference 5 rows, answer 25; lacks 5, adds 25 | yes | output 4, steps |
| 1d21023bca | 4 | 2 | agg > agg > baseline | passed | rows missing reference 2 rows, answer 0; lacks 2, adds 0 | no |  |
| 8ce7840d75 | 5 | 2 | agg > share > baseline | revised | rows missing reference 5 rows, answer 0; lacks 5, adds 0 | yes |  |
| 11c5e5a85e | 4 | 1 | agg > baseline > agg | passed | values in output 1  | yes |  |
| 97769b0922 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1  | no |  |
| 351fb7579b | 6 | 2 | agg > share > baseline > agg | passed | values in output 1  | yes |  |
| a7bcb3401e | 5 | 1 | agg > agg > baseline > agg | passed | values in output 1,2  | yes |  |
| 0d00bc9e2f | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | no |  |
| 6d0476914f | 6 | 1 | agg > baseline > baseline > agg | revised | values in output 1,2,3  | yes | output 1, output 2, output 3, steps |
| 5ae33e9bfe | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| ed587ea981 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 6069419682 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 1,2,3  | yes |  |
| a83a9b0bf3 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | no | output 3, steps |
| 696a17f661 | 6 | 1 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 00d65781cc | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 3, steps |
| 4f1dd2be29 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 3, steps |
| 297a8510dc | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 3, steps |
| b437ed00a4 | 6 | 2 | agg > share > baseline > agg | passed | values in output 1,2,3  | no |  |
| 4781ec3c60 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 3, steps |
| 3a20179886 | 6 | 1 | agg > share > baseline > agg | revised | values in output 1,2,3  | yes | output 1, output 2, output 3, steps |
| 5f1a57a3d8 | 6 | 1 | agg > share > baseline > agg | passed | values in output 1,2,3  | no |  |
| 55907567ca | 6 | 2 | agg > share > baseline > agg | passed | values in output 1,2,3  | yes |  |
| 4548f50304 | 5 | 1 | agg > share > share | passed | values in output 1,2,3,4,5  | yes |  |
| 12e01a46fb | 6 | 1 | agg > baseline > baseline > agg | revised | values in output 2  | yes | steps |
| 09d7fd413b | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3  | yes |  |
| ae5002d112 | 4 | 1 | agg > share > agg | revised | values in output 2,3  | yes |  |
| e43f59ddb3 | 6 | 1 | agg > baseline > baseline > agg | passed | values in output 2,3,4  | yes |  |
| be554083e6 | 4 | 2 | agg > baseline > agg | passed | values in output 3  | yes |  |
| 594daaf4d2 | 6 | 1 | agg > share > baseline > agg | revised | values in output 3  | yes | output 3, steps |
| 6cae1b0182 | 6 | 1 | agg > share > baseline > agg | revised | values in output 3  | yes | steps |
| c759056a31 | 4 | 1 | agg > agg > baseline | passed | values in output 4  | no |  |
| 661e8a78a6 | 6 | 1 | agg > agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| d58457ff41 | 6 | 1 | agg > agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 1a73aa1ae0 | 3 | 1 | agg > baseline | revised | values in output 4  | yes |  |
| 4bef70d889 | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| 0a25f556c5 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | steps |
| df956358d7 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 4a2d376afa | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 64e48775c7 | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| 356f860727 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4, steps |
| fea75e8f25 | 5 | 1 | agg > baseline > baseline | passed | values in output 4  | yes |  |
| 40434115e8 | 5 | 1 | agg > baseline > baseline | revised | values in output 4  | yes | output 4 |
| 156f4616e3 | 5 | 1 | agg > baseline > share | revised | values in output 4  | no | output 4, steps |
| 1380d1a24f | 6 | 1 | agg > baseline > share > agg | revised | values in output 4  | yes |  |
| 307e76f490 | 5 | 1 | agg > share > baseline | revised | values in output 4  | yes | output 4, steps |
| 65650763a2 | 5 | 1 | agg > share > baseline | revised | values in output 4  | yes | output 4, steps |
| 975469f62b | 5 | 1 | agg > baseline > baseline | revised | values in output 5  | yes | output 5 |
| 372cec96f5 | 4 | 2 | agg > agg > baseline | passed | wrong column count expected 3, got 2 | yes |  |
| 103eb91638 | 4 | 1 | agg > agg > baseline | passed | wrong column count expected 3, got 2 | yes |  |
| 00d645c60b | 4 | 1 | agg > agg > share | passed | wrong column count expected 3, got 2 | yes |  |
| 7bc96052e6 | 4 | 1 | agg > agg > share | passed | wrong column count expected 3, got 2 | yes |  |
