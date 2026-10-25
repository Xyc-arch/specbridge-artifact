# The decision library

624 calculation choices found where BIRD and Spider development questions failed (464 BIRD, 160 Spider), in 14 types, plus 27
possible errors in reference SQL kept apart (`defects.jsonl`). Each record was frozen before the held-out runs. The counts are not
prevalence estimates.

| Field | Meaning |
|---|---|
| `id`, `source` | record id; benchmark, database and question id |
| `question`, `gold_sql` | the benchmark question (with BIRD's evidence) and its reference SQL |
| `type` | one of 14 types, e.g. `value_representation`, `population_scope`, `counting_unit`, `ties_and_selection`, `aggregation_level` |
| `decision` | the choice in one sentence |
| `readings` | the readings, each with its SQL (an edit of the reference) |
| `status`, `action`, `raise` | `resolved` (the question settles it), `unresolved` or `contested` (reviewers disagree); whether a system should raise it |
| `evidence`, `review`, `provenance` | why, the two reviewers' verdicts, and how the record was made |

Types: value_representation 148, population_scope 136, counting_unit 118, output_form 61, missing_values 52, ties_and_selection 30,
referent_column 25, aggregation_level 23, time_scope 14, calculation 6, relationship_role 6, comparison_quantifier 3,
condition_linkage 1, negated_membership_scope 1. Status: resolved 516, contested 69, unresolved 39.
