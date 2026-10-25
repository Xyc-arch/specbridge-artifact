# The language, the state, the constraints, and the sampling law

This is the specification the generator is derived from. Every restriction the generator applies must
be traceable to one clause here: the language (§1, §2), a constructor's contract (§3), a proven
property of the current state under one constraint mechanism (§5), or the declared benchmark policy
(`history/REDESIGN.md`, meaning and row facts). A failed sample is evidence that one of these is wrong or
incompletely implemented; it is never a reason to add a rule that is not one of them.

The standing rule: **fixing a bug restores a stated invariant. It never adds a preference.** A
structural frequency that differs from R is a finding about the fitted model and is reported, not
corrected by generation.

## 1. The language L

A program is a tree over the IR of `specbridge.pd.structures.algebra`: Program, SetOp, Scan, Join, and the expression and
predicate nodes. L is the IR minus the following, each with a declared status. A status is changed
only here, by decision, never because a sample or a source program fell on the other side of it.

| construct | status | reason |
|---|---|---|
| a constant expression: both operands of an arithmetic node constants | out | its value does not depend on the data; the IR refuses `x - x` for the same reason |
| LIMIT without ORDER | out | the subset is arbitrary; the IR refuses it in the root and we refuse it everywhere |
| a scalar subquery anywhere except a WHERE or HAVING predicate, or inside an aggregate's argument | out | its determinacy under grouping is not decidable from the outer prefix |
| a read of a step output the step does not list (SELECT *, a pass-through) | out | the reference cannot be resolved by position; `inline_lets` now keeps every listed name |
| a step defined and read by nothing | out | the IR refuses it |
| a step that summarises nothing (no grouping, aggregate, window, DISTINCT, HAVING, cut or inner step) | out | representation choice: such a step only names expressions and is inlined (§2); the steps of 5 of R's programs that cannot be inlined (read from a subquery, or through a rewrite the inliner cannot express) are outside L, 9 decisions (2026-09-30) |
| an aggregate or window in WHERE | out | SQL forbids it |
| nesting deeper than R's maximum, arithmetic deeper than R's maximum, a list longer than R's maximum | out | the termination guarantee; the caps are read from R at fit time |
| two structurally identical siblings (branches of AND/OR/CASE, operands of `-` or `/`, items of a list) | out | degenerate; decided by identity at the choice (§5) and by structure at construction, the residue reported |

Source coverage is measured: the receipts (`python -m specbridge.pd.structures.actions livesql`) list every decision of R outside L,
each with the rule that refuses it. Today (2026-09-30) it is 13 of 13,547, in 8 of 107 programs:

| decisions | programs | rule |
|---|---|---|
| 9 | 5 | a step that summarises nothing and cannot be inlined must end in a cut (the step row of the table above) |
| 2 | 1 | a constant times a constant (policy, §5): the left literal's role is fixed by its slot, the right completes a constant expression |
| 1 | 1 | a LIMIT without ORDER (policy, §5) |
| 1 | 1 | a subquery as a denominator inside an aggregate, which §1 admits and the decoder does not yet (a reconciliation item, §8) |

Until 2026-09-30 the receipts showed 17: four more were REFs refused by the depth cap because the cap was fitted in
different units from the ones legality charges (a reuse counted as a leaf when fitting, at its own depth when checked).
The cap is now fitted in legality's units, so R is never refused by its own maximum. Effect on samples from P with no database (n = 500): depth per program 3.06 -> 3.43 (R 3.39), arithmetic 7.36 -> 8.38 (R 6.80), refused by the IR 12 -> 22 (8 of them longer than any source program). Depth now matches R; arithmetic drifts further above it; both are findings about the fitted law, reported, not corrected by a rule. An earlier count here ("three of
13,869") had not been updated as the decoder changed.

## 2. Canonical forms

Applied to every program before it is read, whether it comes from a source, a target's gold or the
sampler, by one function (`actions.encode`). None of these changes meaning.

- A step that groups nothing, aggregates nothing (at any depth), windows nothing, cuts nothing and defines no
  step only names per-row expressions; it is inlined wherever it stands, and every listed name is kept
  (`grammar.inline_lets`).
- A conjunction is flattened at every depth.
- `NULLIF(y, 0)` as a denominator is `y`; the division convention is stated once (§7).
- A constant stands on the right of `+` and `*`. On the left of `-` and `/` it stays.
- A conjunction in WHERE or HAVING is its list of conjuncts.
- Joins are ordered: this query's steps not yet read by anything, then its other steps, then tables.
  Join conditions are not part of the abstract program; the binder writes them.

## 3. Constructor contracts

Every constructor has inputs with an accepted class, an output class, what it introduces into the
scope, and what obligations it creates. Classes of an expression:

- BARE: a stored column, possibly through CAST or a unit-preserving function (coalesce, abs, round,
  nullif, ifnull, greatest, least, ceil, floor).
- COMPOUND: any other non-aggregating expression.
- AGG: an expression containing an aggregate outside a window.
- WIN: a window expression (per row; does not collapse).
- CONST(role): a literal with one of the roles of §7.
- STAR: only as COUNT's argument.

| constructor | inputs | output | introduces | obligations |
|---|---|---|---|---|
| QUERY | steps*, from, joins*, where*, group*, select+, having*, order*, limit? | a relation with its outputs | a scope | every own step read (§5) |
| STEP | a QUERY | a named relation | its name into the scope of the defining query | to be read |
| RELATION / STEP_REL | — | a relation in FROM | the step as read | — |
| JOIN | relation, kind | — | — | — |
| COL:t | — | BARE of type t | itself | — |
| REF(kind, i) | an object already introduced and admissible (§5) | that object's class | nothing | — |
| STEP_OUT(step, i) | a step read in this scope's FROM, an output not yet introduced | BARE | itself | — |
| LIT:role | — | CONST(role); the role is fixed by the slot (§7) | nothing | — |
| ARITH(op) | l, r: anything but two CONSTs; r ≠ l for `-` and `/` | COMPOUND, or AGG if an operand is | itself | — |
| AGG(fn) | arg: BARE or COMPOUND (no AGG inside, STAR only for COUNT), filter?: predicate | AGG | itself | collapses the query |
| WINDOW(fn) | fn: rank family or AGG; partition*, order* | WIN | itself | an AGG window needs a partition or an ordering |
| CASE | whens+: (predicate, expr), else? | class of its branches | itself | branches distinct |
| FUNC(name) | args*: arity by name | BARE if unit-preserving and its first argument is BARE, else COMPOUND | itself | — |
| CAST | expr | class of expr | nothing | — |
| SUBQUERY | a QUERY | COMPOUND | nothing | allowed only where §1 says |
| predicates CMP, AND, OR, NOT, ISNULL, LIKE, IN, BETWEEN, EXISTS | expressions and predicates | predicate | nothing | AND/OR need two distinct branches; CMP and BETWEEN never ORDER a stored text value against a number (SQLite compares them as text: '100' < '30'; equality is exact and kept; a CAST converts deliberately); a quoted constant is text; a date is not compared with a computed number; IN is equality |

**Determinacy.** A query is COLLAPSED once it groups or an AGG stands in its output; PER-ROW once a
bare column stands in its output; UNDECIDED before either; FREE outside its output clauses (FROM,
WHERE). In a collapsed query an output, sort key or HAVING leaf must be DETERMINED: a grouping key, an
AGG, or an expression all of whose column leaves are grouping keys. In a per-row query no AGG may
stand in an output clause. Inside an aggregate's argument (not a window's) a bare column is fine and a
nested aggregate is not. This is the IR's own invariant, restated as a property of the prefix.

## 3a. The semantic profile and the operator contracts

MEANING IS DESCRIBED ONCE PER DATABASE; COMPATIBILITY IS DECIDED BY CONTRACTS. The catalogue (`catalogues/<db>.json`,
built by `specbridge.pd.realize.semantic`) records facts about columns, tables and relationships; the checker (`specbridge.pd.realize.semantics`) derives
every operation's verdict from them. A model may propose facts; it never lists which operations are allowed.
Every field may be UNKNOWN, and every field carries its provenance: `source` (rows, schema, doc, model),
`confidence` (high, low) and any unresolved `alternatives`. A missing fact is unknown, never compatible.

COLUMN PROFILE

| field | values | source |
|---|---|---|
| storage, parses | SQLite affinity; whether every stored value reads as a number | rows |
| role | identifier, category, ordinal, measure, count, date, duration, indicator, unknown | schema, doc, model |
| quantity | what is measured, a few words ("K-12 enrollment", "total bilirubin"); meaning, not dimension | doc, model |
| unit | a unit of the fixed vocabulary (`specbridge.pd.realize.semantic.UNITS`), a quotient or product of two of them, or unknown | doc, model |
| dimension, factor | DERIVED from the unit by the vocabulary: base dimensions with exponents, and the factor to them | rule |
| scale | nominal, ordinal, interval, ratio, unknown | role, doc, model |
| order | for an ordinal: its values in order (each must occur in the rows), or "numeric" | model, rows |
| additive | per aggregation axis, whether a SUM is meaningful: {"entities": yes/no/unknown, "time": yes/no/unknown} | doc, model |
| population, period | whom the value is about; the period it covers | doc, model |

TABLE PROFILE: `grain` (what one row is), `axes` (the aggregation axes its rows vary over: "entities", and "time"
when one entity has several rows over time; "time" needs a date column), keys. RELATIONSHIP: `a`, `b`, `kind`
(comparable, part_of, rate, product), `result`, `condition` ("same school and year"); part_of is refuted by the rows
when a > b on more than 1% of rows. Join cardinality comes from the schema and the rows (a unique child key is one to
one), never from a model.

Numeric parseability never changes a role: an account code "00123" is an identifier.

OPERATOR CONTRACTS -- each returns (result record, verdict, basis); nested expressions and step outputs use the same
contracts, so the result record of one is the operand record of the next.

| operation | contradicted when | result record |
|---|---|---|
| + and - | both dimensions known and different, or equal with different factors (a conversion is missing); a nominal operand; two dates added | the shared dimension; dates: date - date is a duration |
| * and / | a nominal operand; a date multiplied or divided | dimensions composed (exponents add or subtract), factors multiplied; never "units must be equal" |
| WHOLE - x | x is known and is not a share or percentage with that whole (1 for a fraction, 100 for a percentage) | a share of the same whole |
| SUM | the column is not additive along an axis its table's rows vary over; a nominal or date operand; rows repeated by joins | the same dimension |
| AVG, MIN, MAX | a nominal operand (MIN and MAX order: see comparisons); rows repeated by joins (AVG) | the same dimension |
| COUNT | rows repeated by joins (COUNT of a repeated table's column) | a count of rows |
| comparisons | an ordering (<, >, BETWEEN, MIN, MAX) of a nominal value; of an ordinal whose declared order is not the order SQLite compiles (characters for text); of a text value against a number; a date against a computed number | a predicate |
| CAST, functions | a numeric cast or numeric function of an identifier or a category; a numeric function of a date (a CAST of a date to a number reads its year in SQLite and is kept); a cast does not make an identifier a measure (the role is kept) | by the function |
| CASE | branches of different known dimensions where a number is required | the branches' common record, else unknown |
| REF, step output | never | exactly the referenced expression's record |

Supported (a relationship or rule explains it) is preferred by the binder; unknown is allowed; contradicted is
refused. Optional preferences (no redundancy, a non-empty and non-constant answer) are not contracts
(`specbridge.pd.realize.diagnostics`).

## 4. The state

One record per scope, a stack of them for nested queries, plus two facts shared across scopes.

- `intro`: objects introduced in this scope, in order (columns, step outputs, compounds).
- `outputs`, `keys`: this query's select expressions so far, and its grouping keys.
- `steps`: (name, program) in scope, including the enclosing scopes'; `mine`: this query's own.
- `read`: steps in this scope's FROM. `consumed` (shared): steps read by any scope, by name.
- `mode`: FREE, UNDECIDED, COLLAPSED, PER-ROW; `in_agg`, `in_window`; `clause`.
- `nest`, `depth`; the caps.
- the current slot's accepted classes and its identity exclusions (§5).

Every element is known from the prefix on both sides: the encoder computes it from the program as it
walks, the decoder from what it has built. The round trip is the receipt that they agree.

## 5. One constraint mechanism: legality, then feasibility

Two functions, kept distinct, and `allow` is the second.

**Legality** `legal(s, a)`: three predicates on the candidate at the current slot.

1. **Type.** The candidate's output class is in the slot's accepted set (§3), including a literal's
   role fixed by the slot (§7) and, after a constant on the left of a subtraction, the class its role
   demands of the right operand: bare for UNIT_PARAM, compound for FORMULA_PARAM, unconstrained for
   CLOCK.
2. **Determinacy.** Under the query's mode (§3), for the object itself when it is a REF or a leaf.
3. **Identity.** The slot carries a set of objects it may not be: the left operand of `-` or `/`; the
   items already in a distinct list (outputs, keys, sort keys, partitions); the objects already
   null-tested in this conjunction. A REF to such an object is not legal. Structural equality of an
   independently built compound with a sibling is decided at the LAST leaf of that compound: the leaf
   that would complete a node equal to an existing sibling is not legal. This closes the residue the
   IR used to catch at construction; until it is implemented the residue is a gap and is counted.

**Feasibility** `feasible(s, a)`: after `a`, every outstanding obligation can still be discharged
within the caps. Obligations are countable and so is the room, so this is arithmetic, not search:

- a step of this query is unconsumed: it needs one FROM or JOIN slot; introducing a step, or spending
  a join on a table, is feasible only if `unconsumed steps ≤ join slots left`;
- a list is below its minimum: it needs that many MORE; a compound is feasible only if its required
  slots can each take a leaf at the next nesting level, and the nesting and depth left allow it;
- an aggregate window has neither partition nor ordering: it needs one ordering item;
- a collapsed query's remaining output slots need a determined leaf: a grouping key or an aggregate
  must be constructible, which holds whenever a key exists or an aggregate is legal there.

STOP is feasible exactly when no obligation of its list is outstanding. With the canonical join order
(§2) these rules cost R nothing, and they are what make the minimal completion valid after every
action.

**What allow is.** `allow(s) = {a : legal(s, a) ∧ feasible(s, a)}`. The claim of exactness is the
claim that, within L, `feasible` is complete: every legal action with a valid completion passes it.
That is not proved by construction and not verified by search (§9); it rests on
the argument that each obligation is a count against a known room and nothing else in L can block a
completion. Two gaps are open today and are counted as such, not called exact: structural equality
(the last-leaf rule above is specified and not yet implemented) and a nested scope that reaches its
join cap with a step unconsumed (the step-introduction rule above is specified and not yet
implemented). Anything else that refuses a built program is a bug in this mechanism, and the fix
restores the clause for its whole class, never adds a case.

**Every clause classified.** What each restriction is, and the source coverage it costs on R
(13,869 decisions in 107 programs).

| clause | kind | lost on R |
|---|---|---|
| determinacy under grouping; no aggregate in WHERE; no nested aggregate; window needs partition or ordering | SQL semantics | 0 |
| every step read; two distinct branches; `x - x` and `x / x` refused; constant expressions out | benchmark policy (the answer must depend on the data) | 2 decisions (`1 * 5`: both literals) |
| LIMIT without ORDER out | benchmark policy (the answer must be determined) | 1 decision |
| subquery only in predicates or inside an aggregate | implementation limit (determinacy of a correlated subquery is not decided from the outer prefix) | 0 |
| unlisted step outputs out | representation choice (a reference is by position) | 0 since `inline_lets` keeps names |
| canonical forms: inlining, NULLIF, constant on the right, join order, flattened conjunctions | representation choice | 0 |
| caps at R's maxima on nesting, depth, list length; the depth cap in the units legality charges (a reuse at its own depth) | implementation limit (termination) | 0 |
| the backoff and the pool; the uniform fallback over R's tokens | modelling choice, stated in §6 | not a restriction |

## 6. The sampling law, and what is measured

`pi(a | s) ∝ P(a | s) · 1[a ∈ allow(s)]`, with P the fitted counts in the context stated in
`specbridge.pd.structures.actions`, backed off through the context's prefixes and then a pool by slot. Every masked decision
records `Z = mass of allow(s) under the counts used`; the ledger is reported by context.

P is over the abstract program and every decision P makes is emitted. Bindings (a relation, a column,
a data value, a threshold, a unit parameter's value) are not decisions of P; when they become
decisions of the binder they carry their own Z against their own reference law.

Receipts, every run: the round trip on R (identical sequences); R's decisions outside L (each named);
draws refused by the IR (each named); per-program means with denominators; the divergence of a law
refitted on the samples from P, per context. Differences in frequency between P's samples and R
(today: aggregates 1.19 against 0.99 per program, limits 0.18 against 0.24) are findings about the
fitted model and its context, reported as such and never corrected by a generation rule.

### The projection law used for generation (decided 2026-09-25)

HIERARCHICAL. At an expression or predicate decision, P's split between leaf and compound is preserved whenever
both categories remain feasible; masking and renormalisation happen within the chosen category; if one
category has nothing admissible, the other takes all. Flat renormalisation across all actions is kept only as
an experimental baseline (`specbridge.pd.realize.sampler.PROJECTION`). Evidence, same P, databases and seeds, 200 draws each,
optional policies off: mean size 238 -> 183 (California) and 319 -> 228 (financial) against P's 129; about 30%
faster; execution success unchanged within noise. Known limitation, under investigation: aggregates per
program rise on financial (2.45 -> 5.01). The hierarchy is two levels and frozen. This is a practical default,
not a claim that it preserves every aspect of P.

### Meaning: one checker, one record per expression, one contract per operator (2026-09-26)

(2026-10-01: this section describes the earlier route; `pd.structures.compose`, the current one, does not call these contracts --
see CLAUDE.md.) MEANING IS INTERPRETED IN ONE PLACE, `specbridge/pd/realize/semantics.py`. Every expression has a RECORD: computational type, unit,
kind, measurement scale, grain (the entity a value belongs to), the stored QUANTITY it measures and its FORM (the
value itself, or SUM/AVG/MIN/MAX of it), a constant's value, and per property its provenance (rows, doc, rule,
model). Every operator has a CONTRACT: it takes its operands' records and returns the result's record and a
verdict -- supported, contradicted or unknown -- with its basis. Support and contradiction alike are established
(rows, documentation, a declared rule) or plausible (the model's one-time reading saved in the catalogue): both
kinds of contradiction exclude (2026-09-26; before, a model-sourced contradiction was downgraded to "unknown" and
allowed, so `weight_kg - height_cm` passed although the catalogue says kg and cm), both kinds of support are
preferred, and only missing evidence is unknown. Contracts are
per operator, never per formula, and the module's docstring lists them. A reuse (REF) is the same object and so
the same record; a step output exposes exactly the record of the expression that produced it.

GENERATION AND VERIFICATION USE THE SAME CONTRACTS. Construction branches build expressions; they carry no
meaning rule. While a program is built, the checker is incremental: a candidate at a slot is judged by the
nearest open operator (with its partner, if drawn) and the casts and functions between them
(`Semantics.at_slot`), verdicts are cached by that chain, records of built expressions are stored once, and a
choice whose result is fixed by the choice itself (a cast's type, a function's name) is judged by the record it
yields. Operators further out judge an expression when it closes. After construction, `Semantics.check` walks
every node of the finished program once per scope (`Semantics.nodes`) and applies every contract; the report reads
the same walk. Feasibility looks one level into what a decision opens (`check.LOOK`), not a recursive search.

GRAIN, a declared intention: SUM, AVG and COUNT of a value count each row of that value's table once. A join
repeats a table's rows when, along the join tree from it, a step goes from a parent to its child (the child
holds the foreign key); the aggregate contract then contradicts a value of that table. The multiplicity is
computed from the join conditions (`Semantics.repeated`), the same way on a FROM being built and a finished one.
COUNT(*) counts the query's rows, as SQL says; MIN, MAX and DISTINCT aggregates are insensitive to repetition; a
join to a step has no established direction. P cannot express the other intention (weighting by joined rows).

USEFULNESS IS NOT MEANING. Whether an expression is informative to a person -- `x - x`, `AVG(2)`, a repeated
branch -- is measured by `verify.policies` and reported apart; none is enforced in the baseline. The checker
records `x - x` as a constant; it does not ban it.

THE CATALOGUE, ONE FORMAT (`specbridge/pd/realize/semantic.py`). A database's meaning is one file, `catalogues/<db>.json`, built
once by `python -m specbridge.pd.realize.semantic <db>`. The build merges what exists beside the database, keeping each fact's
source (rows; documentation; the profile's and families' fields, model-filled ones marked model), then one
bounded model review adds what one row of each table is, a scale or unit where none is known, and at most 20
relationships between numeric columns (comparable, part of, rate), checked mechanically (the columns exist, the
words come from a fixed vocabulary, a part-of within one table is refused when over 1% of rows have the part above
the whole). Model additions are plausible support and never exclude. The file carries a hash of its inputs;
generation reads only this file (`semantic.load`), refuses a missing or stale one, and never calls a model.

## 7. Literals and division

A literal's role is fixed by its slot. DATA_VALUE and DATA_THRESHOLD: the target's data, no value
decision. The binder adapts a constant to its ROLE, OPERATOR and the query so far, never by one universal rule:
an equality = (and DATA_VALUE) takes a value that is observed there, since a match is required; != needs no match: an
observed value when other rows remain, else an unobserved one (trivial); a THRESHOLD of < or >
is read from the rows the conditions so far keep and splits them when it can, else it is a boundary just outside
their range -- it need not occur in the data -- which keeps every row and is labelled TRIVIAL (reported beside the
task, never refused). A search failure ("no allowed candidate found", a probe that errs or times out) is reported
apart from a proven impossibility (rows confirmed empty under the conditions so far). UNIT_PARAM (beside a bare operand) and FORMULA_PARAM (beside a computed one) are the two
ARITHMETIC PARAMETERS; on the left of a subtraction the role is drawn and then fixes what the right operand
must be (bare for UNIT, compound for FORMULA), which is the type predicate applied one slot later. TOP_K and
PARAM carry their values because the values are emitted. CLOCK is the snapshot.

AN ARITHMETIC PARAMETER IS A SLOT, NOT A NUMBER (2026-09-26). P decides its KIND; the binder chooses its
value by the kind's declared rule; the source's number is evidence beside the law and never reaches a
target program. Source `0.3 * revenue` is P's `WEIGHT * A`; the target binds A and the weight.

| kind | where | value on the target | what explains it |
|---|---|---|---|
| ZERO | + and - | 0 | nothing: reported unknown |
| WHOLE | left of - | 100 for a percentage, 1 for a share | the operand's unit (supported); any other unit is reported unknown |
| REFERENCE | + and -, divisor of a bare column | the operand's typical value from the rows | GROUNDED: the value is the data's; the purpose, a difference from or ratio to the typical value, is the kind's |
| CONVERT | right of * and / | a factor from the declared conversion table (`catalogue.CONVERSIONS`) for the operand's unit | the operand's unit (supported) |
| WEIGHT | * and /, and % | a plain number the question states | STATED: the question's reason, not the database's |

On the right the operand is known, so a kind whose rule cannot succeed is not offered: CONVERT needs a
declared conversion for the operand's unit, REFERENCE a typical value from its rows. On the left the
operand is drawn after, so the parameter is bound again against it and the outcome is reported.

HOW A WEIGHT IS SELECTED. Uniformly from a declared list of plain numbers (`catalogue.WEIGHTS`: 0.1, 0.2,
0.25, 0.5, 0.75, 1.5, 2, 3, 5, 10; for `%`, `MODULI`), independent of the source's number and of the data.
The question states it; that is its only reason, and the report calls it STATED, never supported.

CASE SCORES (role SCORE). A number in a CASE result is a parameter too: ZERO and ONE (together an indicator,
whose SUM counts rows and whose AVG is a share), SCORE (a number of a scoring rule, drawn from
`catalogue.SCORES` and stated by the question), or LABEL (text; a target never takes the source's text).

A COMPLEMENT IS A CONTRACT, NOT A REQUIREMENT. WHOLE on the left of a subtraction is bound once its right
operand is known: 1 for a fraction, 100 for a percentage, 1 otherwise. The subtraction contract calls `1 - x`
a supported complement only when x is a fraction (or `100 - x` a percentage); otherwise it is ordinary
arithmetic, recorded unknown. `1 - AVG(2)` is not a complement: `AVG(2)` is a constant under the aggregate
contract, not a share.

MEANING IS CARRIED THROUGH EVERY EXPRESSION. A record names the QUANTITY it measures -- a stored column --
and its FORM: `value` (the column, rounded, cast, coalesced, or passed through a step) or SUM, AVG, MIN,
MAX of it. A step output carries the record of the expression that produced it, with the step as its
grain. Relationships of the catalogue apply to quantities, respecting the form: + and - need levels
(value, AVG, MIN, MAX) against levels or a total against a total; a quotient of related quantities needs
both in the same form over the same rows. So AVG(enrollment) keeps enrollment's unit and is comparable
with enrollment, but is not a part of a total. A supported quotient is itself a share (part over whole)
or a rate, and a conversion factor changes the unit by the table; the rest of arithmetic carries a unit
and a kind but no single quantity.

Division: SQLite returns NULL on a zero denominator, so the convention "missing when the denominator
is zero" is the language's, stated once; the compiler casts to REAL because SQLite truncates integer
quotients.

## 8. Reconciliation of the current decoder with this specification

Each rule in `actions.Decoder` today and the clause it must be derived from. A rule with no clause is
removed when the decoder is rebuilt from this document; a rule that is a patch is not promoted to a
clause to preserve it.

| rule in the decoder today | clause |
|---|---|
| mode collapsed/per-row, `_ok_target`, COL masked in collapsed, AGG masked per-row; `in_agg`, `in_window` | §5 legality: determinacy |
| `clause == "where"` masks AGG/WINDOW; STAR only under COUNT | §5 type, §1 |
| SUBQUERY masked unless FREE or inside an aggregate | §1 implementation limit |
| LIT roles by the left operand; `need` after a left constant, three-way by role | §7, §5 type |
| no LIT after a LIT left operand | §1 constant expression |
| REF needs an admissible target; `forbid`; distinct lists; `nulltested` | §5 identity |
| steps by global name; `consumed`; forced unconsumed step; `more_only` | §5 feasibility: step obligations (partial: the introduction rule is missing) |
| STEP_OUT only from a step in this scope's FROM, outputs not yet introduced | §3 STEP_OUT |
| LIMIT needs ORDER | §1 |
| window AGG needs partition or order | §5 feasibility: window obligation |
| list minima and caps; depth and nest caps | §1 caps, §5 feasibility |
| a compound offered only if a non-constant leaf can fill it | §5 feasibility: leaf availability |
| `only=` overrides on LIMIT k and the window's aggregate | §3 slot types; to be expressed as accepted classes, not overrides |

Program 21 was a clause bug of this kind: the role rule had two branches where §7 has three, so a
CLOCK on the left of a subtraction demanded a compound right operand. The three-way rule restores §7
for every program with a date literal on the left of a subtraction; nothing names program 21.

## 9. Exactness of `allow` is not verified by search

A brute-force oracle (enumerate completions on a tiny catalogue and compare with `allow`) was specified here and never
run with recorded results; it was removed on 2026-09-30 (recoverable at commit 53e1ef76, `specbridge/pd/oracle.py`). Correctness of
emitted SQL does not depend on it: every emitted program is judged on the finished program by `specbridge.pd.realize.verify` and executed.
A checker error can only cost dead ends (counted, e.g. "no admissible action") or bias the law away from the intended
projection (measured from the output side by `specbridge.pd.realize.fidelity` and `specbridge.pd.realize.split`). The exactness claim of §5 is therefore an
argument, not a verified property.
