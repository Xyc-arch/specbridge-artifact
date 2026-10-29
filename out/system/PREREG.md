# The disclosure system (arm `system`), written 2026-10-28 BEFORE any output

Motivation (saved answers, AMBROSIA final test, no new calls; scratchpad rescore): merging identical results does not change
our precision (+0.2 [-0.6, +1.3]); at our budget our method beats DtP on AllFound by +15.0 [9.4, 20.6]; our first step used as a
gate in front of DtP keeps DtP's coverage (AllFound -1.1 [-7.2, +5.0]) and raises its precision by +14.3 [+7.7, +20.4].
On request sets DtP's rewrites lose other requirements (Section 5.3), so the wide search must carry each interpretation as an
edit of the request, not a rewrite.

## The system (one fixed rule; nothing tuned on test data)
1. Gate: our listing call (ambrosia.DETECT). One interpretation -> the ORIGINAL request, unchanged, one SQL call. Stop.
2. Open (several interpretations): wide search with DtP's two listing calls (interpretations, then missing ones; released prompts).
3. Edit, do not rewrite: one call (reqmethod.EDIT) turns the gate's interpretations and DtP's into short clauses, merging those that
   decide the same thing (at most 6). Each interpretation = the original request verbatim + " " + its clause.
4. One SQL call for the original request (the main answer: what the system returns today) and one per edited request.
5. Execute; drop SQL that fails; merge identical results; main answer first, then the alternatives that differ.
Same SQL prompt as DtP and ours (DtP's released SQL prompt). The gate call is shared with arm `ours` and the two listing calls with
arm `dtp` (same prompts, same model, same item); their calls are counted in `system`'s cost.

Ablations, from the same outputs: gate + DtP rewrites (= `ours` gate + `dtp` queries where open); no gate (= `dtp`); no merge
(rescore).

## Dev pilot (questions and sets already used for development; the saved DtP raw listings are re-parsed with item_line)
AMBROSIA dev (Sonnet, 60 ambiguous + 30 unambiguous, method_rows) and the 30 dev request sets (Sonnet and GPT-Sol).
PASS (all must hold):
- AMBROSIA dev: AllFound >= DtP and precision on unambiguous >= DtP + 10 points.
- Request sets dev, each model: open both-interpretations >= ours, and specific main right >= ours - 1.
Pass -> freeze, then the final test on fresh items: 150 AMBROSIA test questions per model never used (30 ambiguous + 20
unambiguous per type), and the accepted request sets not in out/reqmethod100/sets.json; arms plain, three samples, DtP, ours,
system; Sonnet and GPT-Sol. Claims judged there, pooled, with paired bootstrap intervals:
(a) system - DtP: AllFound and recall non-inferior (lower bound >= -10 points), precision higher (lower bound > 0);
(b) system - ours: AllFound higher (lower bound > 0);
(c) request sets, system - ours: both interpretations non-inferior (>= -10 points) and specific main right non-inferior.
Fail -> no final run; the paper uses the saved-answer analysis only.

## Added 2026-10-28, before any output: arm `ask` (the documented built-in behavior of production assistants, rebuilt with the same model)
Snowflake Cortex Analyst's classification agent marks ambiguous questions and returns suggested questions instead of an answer
(Snowflake engineering blog, 2024-08-14); Databricks AI/BI Genie asks a clarifying question when intent is ambiguous (Genie best
practices). Both decide before any SQL runs, then stop. Arm `ask`: one classification call (CLASSIFY) -> "ambiguous": no SQL, a
question to the user (counted as flagged; no answer returned) -> "clear": one SQL call on the original request (DtP's SQL prompt).
Measures, same items as `system`: open requests flagged (asks); open requests answered silently; clear requests flagged (wasted user
turn, no answer); clear requests answered right; user round trips per 100 requests. Not the products themselves.

## Decision 2026-10-28 (user), before any final output
The final test reuses the existing items (AMBROSIA final test, 150 questions per model; Table 5's request sets) with every saved arm,
instead of fresh items: the system has no tuned part. Claims (a)-(c) are judged there. Report: out/system/FINAL.md.

## Amendment 2026-10-28, before any `ask` output (user: fewer calls)
Arm `ask` uses the system's own gate as the classifier and the system's answer to the original request as its answer: open -> ask the
user, no answer returned; clear -> the system's main answer. Zero new calls. The decision is identical in both arms; only the action
differs (stop and ask vs answer and show alternatives that differ). CLASSIFY is not used.

## Amendment 2026-10-28, before any final score (user: time and tokens)
At most 4 clauses (as `ours`, at most 4 interpretations), not 6. Items already run keep their first 4 clauses when every SQL call
parsed (queries align with texts; identical to a run with the cap); the others are rerun.

## Variant `keep` (2026-10-28, written BEFORE any output): never rewrite the user's request
Same first call as decide-then-answer (its saved readings are reused). Clear (one reading): the ORIGINAL request, unchanged, one SQL
call. Open (several readings, at most four): for each reading, the ORIGINAL request unchanged followed by
"\n\nAnswer this interpretation: " + the reading (Sec. 5.3's text (c): the request kept, the interpretation added), one SQL call each.
Same SQL prompt, execution, merging and scoring as decide-then-answer. Items: AMBROSIA final test and the 111 request sets, Sonnet and
GPT-Sol. DECISION RULE: `keep` replaces decide-then-answer as the method if, pooled, it is not worse on missed and wrong per 100
requests (upper bound of keep - answer <= +5 each) and not worse on request-set specific right (lower bound >= -3 points); otherwise
decide-then-answer stays and the paper says its first call rewrites the request.
Stopped 2026-10-28 after about 100 items at the user's request (early tie with decide-then-answer: AMBROSIA AllFound 9 vs 9 of 19,
request-set specific right 31 vs 31); not used in the paper.
