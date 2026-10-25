# Semantic coverage: what it shows (2026-09-26)

Sources: `REPORT.md` (automated; since 2026-09-26 evening it describes the run AFTER model-sourced contradictions
were made to exclude, see the last section) and `review/review_<db>.md` (20 random
delivered queries per database, judged by hand against one question: does the query express a coherent calculation
over the target data, with its parameters and assumptions explicit?).

## The claim "most outputs have usable semantics" is not supported

| database | substantive ops supported | queries with all substantive ops supported | manual review: yes / uncertain / no |
|---|---|---|---|
| california_schools | 15% | 6% | 3 / 3 / 14 |
| financial | 12% | 1% | 1 / 4 / 15 |
| thrombosis_prediction | 5% | 2% | 2 / 1 / 17 |
| toxicology | 1% | 0% | 3 / 2 / 15 |
| superhero | 6% | 1% | 5 / 3 / 12 |
| store_1 | 5% | 1% | 2 / 2 / 16 |
| all six | | | **16 / 15 / 89 of 120** |

The 16 "yes" are almost all plain lookups with no arithmetic. Of the 104 "uncertain" or "no", reviewers attributed
101 to arbitrary calculation, 2 to meaning lost in propagation (a date cast to a number), and 1 to missing catalogue
evidence.

## The gap is arbitrary construction, not missing evidence or propagation

What the reviewers found, across databases:

- **Declared numbers everywhere.** Stated weights are 342–496 parameter nodes per database against 1–43 unit
  conversions. Chains such as `x * 0.75 / 0.25 * 3` and `power(count, 1.5)` are defined but mean nothing.
- **Complements of non-fractions.** `1 - x` on counts, bytes or durations: 65–100 per database, against 2–24
  complements of an actual share.
- **Degenerate expressions.** `x / x`, `x - x`, `+ 0`, CASE with identical branches, arithmetic on constants only.
  These are measured as usefulness, not excluded.
- **Unrelated quantities combined.** Latitude added to SAT scores, weight minus height, unemployment times salary
  times a city count. Their units are unknown or differ in ways the catalogue marks only as model-proposed, so the
  contract says "unknown", and unknown is allowed.
- **Predicates without meaning.** Identifiers and labels compared by string order (`molecule_id > 'TR131'`),
  contradictory ranges (`BETWEEN 60 AND 38`, `x = 2.8 AND x = 4.4`). Comparisons have no semantic contract at all.
- **Databases with little numeric data.** Toxicology has no numeric column, yet P draws arithmetic there; the
  expressions are built from constants, CASE codes and cast identifiers.

The catalogue already records most of the facts that make these meaningless: the columns are keys, text or dates,
or carry different units. The mechanism only EXCLUDES established contradictions and ALLOWS everything unknown; it
never requires support. With 85–99% of substantive operations unknown, allowing unknown means allowing almost
anything numeric.

## What the checker does prevent

Final refusals are 15–36 of 200 attempts per database (a function on an identifier or date, a grain-violating
aggregate, arithmetic on identifiers). At decisions, the contracts reject many candidates, mostly identifiers and
text offered to arithmetic ("rows").

## Where support exists

Direct column/column operations are supported 20–42% of the time on the four databases with catalogue relations
(9% on superhero, none on toxicology). Support largely does not survive composition: derived/derived operations
are supported 0–5%. Parameters that are justified by unit (conversions, complements of shares) are a small share
of all parameters.

## After: model-sourced contradictions exclude (2026-09-26, evening)

Traced failures showed the catalogue's units were never used to reject: most units come from the model review, and a
contradiction resting on them was downgraded to "unknown" and allowed (`weight_kg - height_cm`: kg vs cm passed;
`Latitude * x`: an interval scale passed), and the downgraded result lost its record, so later sums could not be
judged. Now contradictions, like support, are established or plausible, and both exclude. Same P, seed and attempts.

| database | accepted before -> after | substantive ops supported before -> after | refused by the final check after | time per accepted SQL |
|---|---|---|---|---|
| california_schools | 163 -> 128 | 15% -> 15% | 49 | 0.60 s |
| financial | 137 -> 128 | 12% -> 11% | 42 | 0.77 s |
| thrombosis_prediction | 138 -> 116 | 5% -> 7% | 55 | 0.48 s |
| toxicology | 97 -> 97 | 1% -> 1% | 15 | 0.76 s |
| superhero | 118 -> 125 | 6% -> 5% | 33 | 0.50 s |
| store_1 | 129 -> 126 | 5% -> 3% | 33 | 0.55 s |

The unit contradictions are now caught (the final check's refusals are led by `+` and `*` on model-sourced units),
but support coverage does not rise: 85-99% of substantive operations are UNKNOWN, not contradicted, and unknown is
still allowed. The review files describe the earlier run's samples.

## Why calculations are unknown, and a fresh review (2026-09-26, after the change)

Same run as the section above; P, projection and generation unchanged. `unknowns/SUMMARY.txt` splits every unknown
substantive calculation mechanically; `unknowns/review_<db>.md` classifies 20 random ones per database by hand;
`review2/review_<db>.md` reviews 20 fresh accepted queries per database.

Mechanical split of unknown substantive calculations: both operands carry units 22-43% (toxicology 2%); an operand's
unit is missing 19-61%; a unit lost on the way 0-16%; a CASE score 4-14%; the rest are `1 - x` of those kinds.

Hand classification of 120 unknown calculations:

| database | 1: catalogue lacks it | 2: propagation loses it | 3: no supported interpretation |
|---|---|---|---|
| california_schools | 0 | 1 | 19 |
| financial | 1 | 0 | 19 |
| thrombosis_prediction | 0 | 1 | 19 |
| toxicology | 0 | 0 | 20 |
| superhero | 1 | 0 | 19 |
| store_1 | 0 | 0 | 20 |
| all | 2 | 2 | 116 |

The four exceptions: `height_cm / weight_kg` and `payments * duration / amount` are meaningful ratios the catalogue does
not record (cause 1); `FRPM Count / (Enrollment + 1)` written as `CAST(FRPM)/FRPM + Enrollment`, and fibrinogen times a
CASE that is always 1, hide a meaning the facts support (cause 2). The rest: x - x, x / x, arithmetic on constants,
identifiers as numbers, `1 - COUNT(*)`, a count cubed, money squared, sums across units, weight chains.

Fresh review of 120 accepted queries:

| database | yes / uncertain / no | queries with arithmetic: yes / uncertain / no |
|---|---|---|
| california_schools | 5 / 1 / 14 | 0 / 1 / 13 |
| financial | 4 / 5 / 11 | 0 / 0 / 11 |
| thrombosis_prediction | 3 / 3 / 14 | 0 / 1 / 12 |
| toxicology | 3 / 2 / 15 | 0 / 0 / 12 |
| superhero | 1 / 6 / 13 | 0 / 0 / 12 |
| store_1 | 3 / 0 / 17 | 1 / 0 / 16 |
| all | 19 / 17 / 84 | 1 / 2 / 76 of 79 |

Every uncertain or no was attributed to arbitrary construction. Only one query with arithmetic (the log of a file
size) is coherent; every other "yes" is a listing or lookup.

Multiplication does not require matching units: all 739 delivered products of two different known units were
unknown, none rejected. The 22 refused products rest on an identifier, text or date (15) or an interval scale (7).

Catalogue defects found along the way (not fixed): store_1 `unit_price` is typed TEXT and `quantity` ANY because
they hold few distinct values, so price times quantity is refused; financial `trans.account` (a partner's account
number) is typed as a numeric measure and marked comparable to `trans.amount`.

Conclusion: the unknowns are overwhelmingly calculations that have no interpretation, not missing catalogue facts or
lost propagation. More profiling or better propagation would change little. What would change it is where the
generator chooses arithmetic: drawing operands and parameters from supported relationships, and not drawing
arithmetic where the database has nothing to compute.
