# The objective, and how it is pursued

Six parts. Nothing else. When a design question comes up, ask which of the six it serves.

Governing all six, before the list: **read the generator, not the output -- and fix a defect where
the decision was made, not where it shows.** Both halves are spelled out under *The organising
spirit* below; they decide HOW each of the six is pursued, so read them first.

1. **P and COMMUNICATION are estimatable from a source corpus.**
2. **The renderer is VERIFIABLE and GUARANTEED on a new database** — the words, the notes and the
   schema determine the ANSWER, and we never manufacture an ambiguity a free wording would have
   avoided.
3. **It is FAST ENOUGH.**
4. **MEANINGFUL** (redefined 2026-09-24) — every column, value, category and bound the question uses is
   the database's own; and a computed quantity is a STATED CALCULATION over real columns: the question
   defines it, the reader executes it, and that is all it has to mean. We care about the AST. The
   arithmetic's shape is the source's; which columns fill it is the target's (a family the model grouped
   once, else any columns of the class); its constants are values the source wrote under that operator.
5. **PRECISE AND WELL-FORMED ENGLISH** (reworded 2026-09-24) — every question is a sentence a grammar
   accepts, and its words determine the answer: every column, constant, table, sort key and cut-off is
   said or defined, no phrase is a claim a model made, and a computed quantity is said as its words or
   carries its definition. Both properties are decided where the phrase is composed, from a finite set of
   templates each read once, so a malformed or underdetermined question cannot be built. That a person
   would have written it the same way is not required; where a plainer word does the same job, it is
   preferred, and a note never props up a vague one.
6. **MODULAR AND PORTABLE** (added 2026-09-24) — a new gold source is one registry entry and one
   command (`specbridge.pd.structures.sources`, `python -m specbridge.pd.structures.mine <source>`): P, the signature table and the English frames
   are fitted from it, nothing else changes. A new target is a path to its `.sqlite`: its profile,
   vetoes and knowledge base are written beside it on first touch, in one schema for every database,
   and the same code builds on it. No code per source, no code per database, and every per-database
   fact lives in an editable file next to the database, never in `pd/`.

The practical purpose underneath them: **sound labelled data for a database that has none** — an
uncontaminated test set on any schema, and training data for domain adaptation where nobody has
written queries.

Parts 1–3 were set 2026-09-11. Parts 4 and 5 were added 2026-09-20, each because something passed
every existing check and was still wrong: part 4 because `Show country name and league name` is
determinate and worthless, part 5 because `(the number of rows counting only those where (x)) as a
fraction of (the number of rows)` is determinate and is not a sentence.

**Part 5 is its own goal and not polish, because it CONFLICTS with part 2 and nothing else does.**
Both sides of that trade were hit within an hour on 2026-09-20. Made determinate, the phrase above.
Made readable, "the share of rows where x" — which is silent between a FRACTION and a PERCENTAGE,
and a solver wrote `* 100.0` on 26 of 39 failures. The resolution is usually better than the trade:
"the fraction of rows where x" is natural AND unambiguous AND shorter than either.

---

## The organising spirit: READ THE GENERATOR, NOT THE OUTPUT

**We control the whole generation, so every property is decidable from the code. Guarantee it there.
Do not sample output and check afterwards.**

Checking output is sampling. You see a defect only when a draw happens to expose it, which is why
the defects of 2026-09-20 took a day and five solver runs to surface one at a time. The generator is
finite and we wrote it, so the set of things it CAN emit is enumerable — and enumerating beats
sampling.

**The worked example.** All the English a question can contain comes from templates in `specbridge/pd/say.py`,
not from the data. Extracted from the AST that is **92 prose fragments — one screen.** Reading it
found in a minute what a day of reading output had not:

- `_REL_PART` still said "as a share of", the same fraction-vs-percentage silence already fixed
  hours earlier on the row-share
- that clause had never fired at all: it reads `part_of` from a cache only the ported path fills, so
  every sampled composite rendered as a bare division
- "per" was the same defect one step back, propped up by the decimals note — now "divided by", and
  the note is deleted, because the phrase says what the note said
- most remaining awkward fragments (NTILE, window ranks, CTE steps, HAVING, CASE) are UNREACHABLE
  from the sampler, so the live vocabulary is far smaller than 92

**How to apply it, per goal:**

- **part 5** — enumerate the phrase templates, read them all, fix the WORD. Never add a note: a note
  propping up a vague word is a patch; "fraction" instead of "share" is construction.
- **part 2** — a phrase must contain the words of what it computes. `pd.say._said` already enforces
  this, and every ambiguity found on 2026-09-20 came from SILENCING it.
- **part 4** — make the unwanted question unrepresentable at the choice point, never filter it after.

**And it bounds the work.** "Read output until you stop finding defects" has no end. "Read the
reachable vocabulary" is a finite task that finishes. That is what lets a goal be closed rather than
inspected forever.

### The sharper form: A DEFECT IN THE OUTPUT WAS SETTLED MUCH EARLIER IN THE INPUT

Reading the generator tells you THAT something is wrong. It does not tell you WHERE to fix it, and
the wrong place is almost always the place the defect shows. **Fix it where the decision is made --
once -- not where it appears -- many times.**

Measured 2026-09-21. One column name was adopted badly: `chanceCreationPositioningClass` was split on
its lowercased key, so it had no capitals left to split on and became a single unreadable word. That
one choice made **149 of 1,444 questions** unreadable. At the far end of the pipeline I was catching
the same single mistake 149 separate times and throwing away a whole question each time. The fix is
one invariant in `Namer.__init__`: a name is handed out only if it reads as a noun phrase, with three
tries -- the database's own description, the column name split on capitals, `pd.english.rephrase`.
After it, the check finds nothing, because nothing bad is ever named.

The same day, **six of the thirteen reading properties in `specbridge/pd/reads.py` turned out to be decisions in
the wrong place rather than checks**: four were the naming invariant above, `lists_a_thing_twice` was
a missing dedupe in `_one`, and `note_is_a_sentence` was a note built from a sentence where a phrase
was wanted. Seven remain, and those are genuinely sentence-level.

**APPLIED, 2026-09-21, and this is the whole of the evidence for it.** 450 draws across all fifteen
databases, counting every reading flag that fired -- not on the shipped rows, which carry none by
construction, but on the attempts the generator threw away. **40 fired. Each one was a decision made
somewhere earlier, and after moving the nine of them to where the decision is, 1 fires.**

| what fired | where the decision actually was |
|---|---|
| `not_a_sentence` x35 | a column whose name is shared by two tables returned BEFORE the naming ladder ran, so it was said as its raw key with a possessive -- `sets' isOnlineOnly`. Now the ladder names it and the table is appended as "in sets", with no apostrophe a later reader can mistake for a quote |
| `raw_handle` x10 | `specbridge/pd/derive.py` and `specbridge/pd/quantity.py` each had their OWN copy of "what do we call this column", with worse fallbacks. One name table is now handed to both, and a column with no readable name is not in the alphabet |
| `raw_handle` (short keys) | the naming ladder asked "is this description too LONG", never "is this a HANDLE", so `baseSetSize` walked past it. `reads.is_handle` is now one door: the same test decides whether to MAKE a name and whether one was made |
| `handle_over_content`, `says_nothing_of_the_database` | both counted the database's RAW KEYS in the finished text -- the very thing the namer exists to keep out of it -- so they threw away questions that named two columns. Deleted; `pd.say.question` refuses where both numbers are exact |
| `not_a_sentence` (values) x17 | brackets counted across quoted values, so `admission is '+('` was an unclosed bracket. The renderer settled which characters are a VALUE when it quoted them |
| `repeats_a_phrase` x28, `bracketed_quantity` x7 | two `ROUND` clauses in `specbridge/pd/say.py`, the second UNREACHABLE. I improved the dead one, re-measured, and nothing moved |
| `doubled_word` | the aggregate's noun in front of the column's: "the total total bilirubin", now "the total OF total bilirubin" |
| `run_together_name` | a name the MODEL invented -- `DribbleSkill` -- which no check for the database's handles could ever catch. `pd.english` now splits what it hands back |

Note what the table is mostly made of: **not one of these was a bad rule. Eight of the nine were the
right rule in the wrong place, and two were a second copy of a rule that had drifted from the first.**

**The test for where a fix belongs.** Ask how many output rows ONE wrong choice can spoil. If the
answer is "many", the fix belongs at the choice. Then the check at the end should become dead code --
and that is the receipt: a guarantee that holds is a check that never fires. A check that still fires
is a decision still sitting in the wrong place.

This is why "guarantee it in the code" is not enough on its own. Code can hold a check too. The
guarantee has to sit at the earliest point where the fact is settled, so that one fix covers every
row the fact reaches.

**PART 5 IS GUARANTEED BY ENUMERATION AND A VETO, NOT BY SAMPLING (2026-09-22).** Everything the
renderer can say is a program shape filled with things of a dozen kinds -- a count, a money amount, a
score, a measure, a date, a category, a value, a table, a label. `pd.reachable` writes that list from a
stand-in schema with no database, the real renderer says every cell, and a READER model -- allowed only
to answer OK, or NO with six words -- reads each cell once (`pd.english.veto_cells`). A NO names the
template or the kind rule where the decision is; the fix is made there, never in a question, and the
model's words never enter one. Verdicts are cached by skeleton, so a new slot, kind or template costs
only its new cells. The receipt is the count of vetoes on the cell list, which should read zero; a
corpus read (`python -m specbridge.pd.english out/x`) and a solver's failures are then checks that the enumeration
is complete, not the way defects are found. This is what ends the loop of build, read, fix, build.

**PART 5 WAS JUDGED SUFFICIENT (user, 2026-09-20), and the rule above is what keeps it so.** After the prose was rebuilt from R -- openings at
R's own frequencies, constraints as their own sentences, no note propping up a vague word -- the corpus
was called fine for evaluation. What remains is readability, not correctness: nested superlatives ("the
lowest of the highest X"), the label indirection when a long phrase repeats three times, column names
the database itself writes badly (`isForeignOnly`), and terse sorts. DO NOT REOPEN THESE unless a
measurement shows they cost something. The work that matters is now the two experiments below.

---

## What is guaranteed, and what is not

> **Note, 2026-09-26.** The list below describes the engine deleted on 2026-09-24 (`pd.bind`, `certify`); it is
> kept as the statement of intent. What the current generator guarantees is stated in `docs/LANGUAGE.md` (the
> language, its contracts, and meaning in §6) and measured in `out/crossdb/REPORT.md`.

Guaranteed at construction, and verified by an instrument outside the code that enforces it:

- the SQL is built, not written; the answer is whatever the database returns for it
- zero flags from `pd.certify`'s twelve conditions — non-empty, no all-null column, the grouping
  aggregates, the filter removes rows, the computed value varies, no tie across a cut-off, at least
  one load-bearing decision. **Since 2026-09-22 each of these is decided where the choice is made:**
  `pd.bind` reads the relation once per decision context (`Facts`/`View`) and a grouping, an
  aggregate, a filter, a cut-off or a lookup is a candidate only if the finished answer would pass.
  `certify` still runs on every program and refuses a flagged one — the receipt — and across all
  fifteen databases it refuses nothing (the record, `docs/session-2026-09-22/BOUND.md`, is in git history).
- every table a query reads is named by the question — a lookup is grown only if a column of it is
  used, and COUNT(*) says which table's rows it counts
- every column and constant the query uses is named or defined in the question (`reached`)
- every quantity is over the database's own columns: a share of rows in a category, a bound the
  documentation states, a code it explains, or a stated calculation (goal 4) present on the rows
- joins are many-to-one only, so no count is silently weighted by fan-out
- no invented threshold, category, or name
- the arithmetic is the source's AST projected onto the target (decided 2026-09-24, replacing "no
  invented formula"): the law is fitted over four leaf classes -- amount, ratio, time, constant -- and
  each draw is masked by the columns the target can supply, so every drawn shape is filled and the
  realised tree IS the drawn one; no shape is pruned to a shallower one afterwards

**Not guaranteed, and no checker exists:**

- that the words admit only ONE query. `reached` proves nothing was left unsaid, not that nothing is
  ambiguous. The working instrument is empirical: give the words to a solver and read the SQL it
  writes. A solve rate is not evidence of difficulty until the failures have been read.
- that a person would want the answer. A judgement, approximated by making the unwanted
  unrepresentable.
- that the database's own documentation is accurate. We take it on trust.

---

## What would turn this from "sound data" into "a benchmark"

Two experiments, neither long, and the only place the evidence is genuinely thin.

**DOES IT SEPARATE MODELS?** One second solver over the same items. A single point -- qwen2.5-coder:14b
at 36%, 96% of its SQL running -- is data, not a benchmark. If a stronger model lands above it in the
way it does on human-built benchmarks, the ordering is evidence the corpus measures ability rather than
our idiosyncrasies.

**IS DIFFICULTY DECOMPOSABLE?** Hold the databases, the alphabet and the prose fixed, vary ONE
structural feature -- `Compose` on versus off -- and measure what it costs a solver. This is what the
conditional law buys and what annotation cannot do: you cannot ask a human to write the same question
twice with one feature removed. It is also the claim no point estimate of a solve rate can make.

A solve rate is not evidence of difficulty until the failed SQL has been read. Twice on 2026-09-20 a
number looked like a finding about the model and was a finding about our own wording.
