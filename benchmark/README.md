# The request-set benchmark

A request set tests one calculation choice on one database. It holds two SQL queries that differ only in that choice and return
different answers, and three requests: `specific_A` asks for interpretation A, `specific_B` for interpretation B, and `open` leaves the choice
open. A model is scored by execution: does it compute each interpretation when asked for it, and does it report both when the request
leaves the choice open?

- `request_sets.jsonl`: 307 sets, 215 with `"family": "main"` and 92 with `"family": "filter"` (an added filter condition,
  Section 2). **204 have `"accepted": true`**: two authors cross-checked every set independently and kept 232 where a reasonable
  analyst could mean either interpretation; of these, 204 are of a choice type whose other interpretation at least 1% of
  references of open BIRD and Spider questions take (Section 4.2). All results in the paper use these 204.
- `databases/`: the 12 SQLite databases (Spider: baseball_1, sakila_1, customers_and_invoices, chinook_1; BIRD: financial,
  student_club, thrombosis_prediction, formula_1; LiveSQLBench: archeology, insider, crypto, alien).
- `score.py`: the scorer. `python benchmark/score.py answers.jsonl` scores a model; `--self-test` checks that every reference
  query matches its own interpretation.
- `examples/<model>_single_call.jsonl`: the four models' single-call answers from the paper, in the scorer's input format.
  `python benchmark/score.py benchmark/examples/sonnet_single_call.jsonl` reproduces Sonnet's single-call bars of Figure 8.

## Fields of one set

| Field | Meaning |
|---|---|
| `id`, `database`, `source` | set id, database, the benchmark the database comes from |
| `choice_type`, `choice_kind` | the type of choice (e.g. `aggregation_level`, `tie`, `missing_values`) and its finer kind |
| `review`, `accepted` | the final verdict (`yes` 204, `no` 97, `unsure` 6) and whether the set is in the reported population (`yes`). `no` includes the 28 sets the authors kept that the type-frequency rule removes; their verdicts are kept in `human_supervision/verdicts.json` with a note that starts "No: the type is rare in real data" |
| `requests` | `specific_A`, `specific_B`, `open` |
| `readings` | the two interpretations in one sentence each |
| `sql` | `A` and `B`: the two reference queries (they differ in one step) |
| `shared_requirements`, `choice_components` | what the three requests share, and the part that changes |
| `context` | `schema` and `documentation`: exactly the text the models were given |
| `grading` | the graders and reference answers used by `score.py` (column positions, numeric tolerance, ties at a cut-off) |
| `depth` | arithmetic and step depth of the generated query |

## Answer format for `score.py`

One JSON object per line: `{"id": ..., "request": "specific_A" | "specific_B" | "open", "sql": ..., "alternatives": [...]}`.
`alternatives` is optional and counts only for the open request.
