# The pipeline

One entry point, `python -m specbridge.comm`, runs every stage in order. Each stage is one module, and its docstring gives the details.
Expensive work happens once per database at setup. A corpus request reuses that work, and spends model calls only on tasks it
keeps.

```
Database
 └─ SETUP  (once per database and version)                        python -m specbridge.comm setup <db> ...
     1 catalogue      specbridge.pd.realize.semantic          what each column means
     2 feasibility    specbridge.comm.construct.feasibility   what the grammar can build
     3 language       specbridge.comm.verbal.language         readable names for columns, tables, codes

Request (the explorer's saved request, or a JSON file)
 └─ CORPUS                                                         python -m specbridge.comm build <request.json>
     4 generate       specbridge.pd.structures.compose        SQL toward the requested depth cells
     5 check          compose.check                the data checks
     6 review         specbridge.comm.construct.rubric        coherent meaning, determined answer
     7 package        specbridge.comm.construct.freeze        explicit instructions (V), reference answer, grader (kept tasks only)
     (orchestrated by specbridge.comm.construct.corpus_build)

Corpus
 └─ NATURAL QUESTIONS                                              python -m specbridge.comm natural <corpus dir>
     8 language       specbridge.comm.verbal.language         ensured for this corpus's own gaps
     9 write          specbridge.comm.verbal.precise          one precise natural question per task -> corpus.jsonl (delivered)

Evaluate                                                           python -m specbridge.comm.construct.solver_eval <corpus dir> | specbridge.comm.construct.error_attr
Inspect                                                            python -m specbridge.comm compare A B | python -m specbridge.comm status
```

## Setup (once per database)

| stage | what it does | model calls | output and cache |
|---|---|---|---|
| 1 catalogue | Gives every column its role, unit, additivity, population and description, from the schema, the data and the documentation. Confirmed corrections in `catalogues/corrections/<db>.json` override the rest. | one review | `catalogues/<db>.json`, with a version hash of its inputs |
| 2 feasibility | Finds the depth cells the grammar can build (exact), which operations each cell supports (exact), and the data-valid share of probe programs (an estimate). | none | `out/feasibility/<db>.json`, resumable; redone only when the grammar or catalogue changes |
| 3 language | Collects the columns, tables and codes whose natural wording falls back to raw names, then proposes labels from evidence only. Labels are accepted by rule, never by the model. | one per database, for new gaps only | `catalogues/language/<db>.json`; `out/language/<db>/state.json` records the items already tried |

## A corpus (per request)

`specbridge.comm.construct.corpus_build`. The steps run cheapest first, so nothing costly is spent on a task that will not be kept.

1. **Generate:** plan the tasks per database and per depth cell. A cell the database cannot build moves within the allowed
   depth difference; anything further is reported as a shortfall.
2. **Generate (sampling):** draw SQL without replacement, so a duplicate can never be drawn. Preferences (operations,
   multi-table, grouping) and the Variety setting weight each choice by its kind. A choice weighted 0 is never offered.
3. **Check:** run each program on the data. Drop answers that are empty, constant, restate an operand, have a non-positive
   denominator, or exceed 2,000 rows. No model is called before this point.
4. **Review:** give each task's instructions to two reviewers, each judging alone. A task passes the benchmark standard when
   both say its meaning is coherent and its answer is determined. Earlier verdicts on the same SQL are reused.
5. **Package:** only for kept tasks, in parallel. This adds the reference answer, tie groups, grader, snapshot hash and
   provenance.
6. **Rounds:** each round asks only for what is still missing, divided by the pass rate measured so far.
7. **Report:** requested vs delivered per cell, operations, shapes, tables, model calls, runtime, and the reason for every
   shortfall.

## Natural questions (per corpus)

`specbridge.comm.verbal.precise` is the frozen writer (tag `lm-writer-frozen-2026-09-28`):

- **Input:** exact requirements plus structured facts, batched by database.
- **Writing:** batched by database (up to 8 tasks per call).
- **Review:** one task per call (since 2026-10-01), short pass/fail per requirement, then one revision for failures only.
  `--rereview` applies this review to an already paired corpus.
- **Status per task:** passed, revised, deterministic (a simple task, worded by rule), or not rendered.
- **Renderings delivered:** the natural question, and the explicit instructions (V): deterministic from the SQL, read by
  the review, and the reference the natural question is checked against. A task without a natural question is not
  delivered (`NOT_RENDERED.json`, with the reason).
- **What stays unchanged:** SQL, answers and graders.
- **Output:** `<corpus>/corpus.jsonl` (delivered), `tasks_paired.jsonl` (every task with its writer status and review history), `NATURAL.md`.

## Corpora

The active version of each corpus is described by `docs/corpora/<name>.FROZEN.json` (files and hashes, bindings, review,
solver results). Superseded versions are kept in `<corpus>/history/` and `docs/corpora/history/`, never listed as active (history: the v3.1 build
`@8fc775be66aa`, 43 of 200 tasks recomputed an aggregate; the v3.2 build `@b223964d8a45`, 10 trivial comparisons, replaced by a top-up).

| corpus | delivered tasks | built | not rendered | review | haiku |
|---|---|---|---|---|---|
| my-corpus-variety-demo@47f34e43a300 (wta_1; v3.3 top-up of @b223964d8a45) | 196 | 200 of 200 | 4 | one task per call | natural 179/196 (91%), explicit 177/196 (90%) |

## Serving reviewed tasks without new generation

`specbridge.comm.construct.serve` and `specbridge.comm.construct.pool` (stock from the v3.1 reviews):

- **Serve:** select stocked tasks closest to an intent. Hard constraints filter first, then depth deviation is minimised
  within a per-axis limit. No model calls.
- **Pool:** keep the reviewed stock per database and version.

## Research and paused modules (not on the corpus path)

| module | status |
|---|---|
| `specbridge.comm.construct.research.adapt` | adaptation of a catalogue by a fixed procedure: paused; the acceptance rule is to be replaced (docs/COMPOSE.md) |
| `specbridge.comm.construct.research.depth_eval`, `recheck`, `filtered`, `grammar_review`, `veto` | evaluations of earlier grammar versions and of the old veto |
| `specbridge.comm.construct.research.ported`, `dbfirst`, `corpus`, `pipeline`, `profile`, `config`, `serve_eval` | the earlier ported-P and v2 paths, and the single-database configuration tools |
| `specbridge.comm.diagnose`, `specbridge.comm.transfer` | the communication research: diagnosing benchmark wording against explicit V; A/B choice points and open questions |

## What is guaranteed, and what is not

| guaranteed by construction | measured, not guaranteed |
|---|---|
| depth, measured on the SQL; no recomputed aggregate; no trivial comparison or cut (refused at each move, read back off the SQL) | coherent meaning: two reviewers, about 5% of decisions flip |
| no duplicate programs | natural-question fidelity: reviewed, evidence not proof |
| hard constraints never crossed | other redundancy: not assessed |
| every shortfall has its reason | |

A requested depth cell is either built, moved within your limit, or reported short.
