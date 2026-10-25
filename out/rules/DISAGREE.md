# Base SQL vs the gold's side at sites where the choice changes the answer (BIRD hold + hold2, plain)

| solver | rule | gold sites that matter | model takes the other side | ... and is wrong |
|---|---|---|---|---|
| gpt-6-luna | boundary | 13 | 1 | 1 |
| gpt-6-luna | count_unit | 24 | 4 | 2 |
| gpt-6-luna | division | 7 | 0 | 0 |
| gpt-6-luna | join_kind | 16 | 2 | 2 |
| gpt-6-luna | null_filter | 6 | 1 | 1 |
| gpt-6-luna | ties | 8 | 0 | 0 |
| gpt-6-sol | boundary | 6 | 1 | 1 |
| gpt-6-sol | count_unit | 7 | 0 | 0 |
| gpt-6-sol | division | 2 | 0 | 0 |
| gpt-6-sol | join_kind | 2 | 1 | 1 |
| gpt-6-sol | null_filter | 1 | 0 | 0 |
| haiku | boundary | 14 | 0 | 0 |
| haiku | count_unit | 27 | 8 | 6 |
| haiku | division | 7 | 0 | 0 |
| haiku | join_kind | 18 | 3 | 3 |
| haiku | null_filter | 7 | 2 | 2 |
| haiku | ties | 8 | 0 | 0 |
| sonnet | boundary | 6 | 1 | 1 |
| sonnet | count_unit | 7 | 1 | 1 |
| sonnet | division | 2 | 0 | 0 |
| sonnet | join_kind | 2 | 1 | 1 |
| sonnet | null_filter | 1 | 0 | 0 |
