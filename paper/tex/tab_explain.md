# Tables used in the manuscript


> **2026-10-15:** the paper now has four tables, all numeric: Table 1 (every result per model, with reliability rows and a breakdown by type and source), Table 2 (construction counts), Table 3 (the four methods on AMBROSIA and request sets; was Tables 6-7) and Table 4 (benchmark comparison, numbers and check marks). The example tables (old 4, 5, 8) are Tables S4-S6 of the supplement; old Tables 1 and 10 became prose. Figure 3 is now the second worked example, so later figures are numbered one higher. Sections below may use the earlier numbering.


> **2026-10-14:** every result on request sets now uses the 178 sets an author's review accepted (of 215; `human_supervision/`, `specbridge/comm/transfer/reviewed.py`). Counts below that cite 215 sets, 480 readings or 30 sets are from before that change; the paper and `out/paper/data/` hold the current numbers.

Manuscript: *Text-to-SQL Models Know More Than They Tell* (`paper/tex/specbridge.tex`).

The 9 tables included by `paper/tex/specbridge.tex`, in manuscript order. Each `.tex` file here is the exact table source. Three are **generated
from data** by `specbridge/report/tables_tex.py` (do not edit them by hand): `main_results`, `comparison`, `method_reqsets`. The others are hand-written sources whose numbers come from `paper/result.md` and `paper/example.md`. Counts of matching answers are
execution measurements; explanation labels are Opus judgments.

## Table 1 — Documented cases where one calculation choice changed a consequential result (in `specbridge.tex`, label `tab:casesshort`)

Six of the nine cases of the supplement's survey (`supplement.tex`, `tab:cases`), each checked against its primary
source: Herndon et al. 2014, Obermeyer et al. 2019, Shahian et al. 2010, Silberzahn et al. 2018, Ziemann et al. 2016, NASA MCO board 1999.

## Table 2 — All accuracy results (`main_results`, generated)

Sources: `fig2_explicit_vs_precise.json`, `fig3_real_benchmarks.json`, `fig5_tab4_disclosure.json`, `fig6_inclination.json`. Rows are conditions,
columns the four solvers (Haiku / Sonnet / GPT-Sol / GPT-Luna); bold marks the best solver in a row; no cell is missing. Generated tasks (382):
$V$ 89.8 / 99.5 / 99.0 / 80.4, natural 92.4 / 97.1 / 96.9 / 90.3. BIRD held-out (96): original 49.0–74.0, extra columns allowed 67.7–79.2, $V$
95.8–100. Spider held-out (50): original 64–82, column-tolerant 84–92, $V$ 96–100. Request sets (178 accepted, one call that also asks for an
explanation): specific right 72.5 / 98.9 / 82.6 / 74.2; names the choice (judge) 25.8 / 64.0 / 50.6 / 36.5; both returned 14.0 / 48.3 / 35.4 /
8.4, and among sets with both specific right under exploration 13.9 / 48.5 / 36.8 / 9.4.

## Table 3 — Construction of request sets (`funnel`)

Source: `../../out/paper/data/tab3_generation.json`, `../result.md` R5. Starting from 382 tasks, the pipeline proposes 704 choices. Of these, 660 execute and change the answer, 633 can be described by the SQL-to-text function, and 606 receive support from at least one reviewer (357 both, 249 one). Balancing selects 240 tasks. Wording checks retain 215 sets, with both reviewers accepting the open request in 195 and one reviewer in twenty. These are successive filters, not independent sample counts. An author's review by hand then accepts 178 sets (31 no, 6 unsure; `human_supervision/`).

## Table 4 — What recorded explanation responses supply (`disclosure_examples`)

Source: `../example.md` E8; full requests verbatim in Section 5. Film (GPT-Sol): computes A, does not name the choice, no alternative. Film
(GPT-Luna): A, names the choice, no alternative. Awards (Sonnet): `COUNT(*)` (A), names the choice, and an alternative with
`COUNT(DISTINCT player_id)` that returns B. Fees, specific request (Haiku): follows the request, but also offers a mean of channel means that
returns B and contradicts the request. An alternative counts only when its SQL runs and returns the other stored answer.

## Table 5 — Four decisions and what they change (`library_examples`)

Sources: `../example.md` E5 (rows 1–3, library) and E7 (row 4, generated). Each row gives the phrase that leaves the choice open, the database,
and the executed answers of both readings. `superhero`: `LIMIT 1` returns 1 hero, every tied maximum returns 40. `thrombosis_prediction`:
averaging joined laboratory records gives 74.69 years, averaging distinct patients 71.95 (the reviewers disagree whether both readings are
supported). `cre_Doc_Template_Mgt`: keeping unused templates adds 8 rows with count 0. `sakila_1` (generated): all customer records give 326 and
273 per store; `active = 1` gives 318 and 266. The remaining library cases are explained in Appendix I.

## Table 6 — Wrong alternatives on clear questions (in `specbridge.tex`, label `tab:exchange`)

AMBROSIA final test, per question, Sonnet / GPT-Sol: queries returned and wrong queries on unambiguous questions, readings found on ambiguous ones (plain, Sample-3, DtP, ours). Source: `out/ambrosia/final/EXCHANGE.md` (`specbridge.comm.transfer.exchange`). DtP 2.27 / 1.90 wrong per clear question vs ours 0.73 / 0.48.

## Table 7 — The same arms on 24 accepted development request sets (`method_reqsets`, generated)

Source: `out/reqmethod/results.json` (`specbridge.comm.transfer.reqmethod`). Data-side choices; DtP names the planted choice most
often but computes worst (Sonnet: both readings 1/24, specific right 12/24); library edits add one set for GPT-Sol.
## Table 8 — Three readings lost by the interpretation rewrite (in `specbridge.tex`, label `tab:rewriteex`)

Three of the 58 readings that were right from the original request (a) and wrong from the DtP-style interpretation rewrite (b), from
`out/rewrite/runs/<model>/<case>__<reading>.json` and the loss labels in `out/rewrite/classify.json`: financial `4548f50304` B (Haiku,
output columns), insider `91cfb4e1db` A (Sonnet, formula: the rewrite drops the signed deviation), Formula 1 `1e89ccdc51` B (Haiku, grouping). The last column
is arm (c); it is also wrong for the insider example. (The earlier thrombosis example came from a set the author's review rejected.)

## Table 9 — How SpecBridge differs from AmbiQT and AMBROSIA (`comparison`, generated)

Short cells (2026-10-12 revision). "Our decisions covered": the 57 open decisions of meaning in the library whose kind falls in each
taxonomy; the mapping (column/table ambiguity and vagueness -> which column; scope -> any vs. all; attachment -> how conditions link) is
in Appendix D. The compute-vs-report row is marked for AMBROSIA: its scores do not split misses, but its items (one unambiguous
question per reading, linked by `ambig_question`) allow it; Section 4.3 applies the split (`specbridge.comm.transfer.ambrosia
decomp_run`, out/ambrosia/DECOMPOSITION.md and DECOMPOSITION_conf.md): pooled over two disjoint samples of 60 ambiguous test
questions, 49-66% of missed readings are computed correctly when asked separately.

## Table 10 — Reliability when a request leaves a choice open (in `specbridge.tex`)

Six properties (transparent, consistent, honest about itself, not alarmist, stable under revision, evaluated faithfully), what each means for an analyst, the evidence from the paper, and a status (not met, mostly, met, met by our method, mixed, not met). Numbers only from Sections 5-7 and Appendix K.

## Supplement only — Query construction (`construction`)

Source: `../../out/paper/data/tab1_construction.json`, `../result.md` R1. On four databases from each source, the generator delivers Spider 398/400, BIRD 400/400, and LiveSQLBench 400/400 queries. All 1,198 delivered queries are distinct, meet the requested depths, and pass the two structural checks. The recorded construction counts are 289, 270, and 309 (868 total). Source-level seconds are rounded individually (127, 274, 37), while the total 437 is rounded from the unrounded sum. The difference from summing rounded entries is not a missing run. No model calls occur after catalogue preparation.

## Supplement only — Library counts (`library_counts`)

Source: `../../out/paper/data/tab2_library.json`. There are 624 examples in fourteen categories: 108 labeled for raising the decision and 516 for remaining silent because the wording settles it. Possible reference errors (27) and unplaced cases (four) are kept apart. Two sparsely represented categories are provisional. Counts describe a selected diagnostic library, not ambiguity prevalence.

## Removed from the manuscript (2026-10-13; the numbers stay in the text or the figure they repeated)

- Why the open request was not covered (`decomposition`, generated)
- Depth, sampling and required operations (`controls`, appendix)
- Wording construction (`generation_comparison`, appendix)
- Writer self-preference (`writer_swap`, generated, appendix)
- Exact explanation outcomes (`disclosure_counts`, appendix)
- Matched single-call control (`disclosure_controls`, appendix)
- Reference conventions, counts (`reference_conventions`, appendix)
- Results by database (`per_database`, appendix)
- Development error categories (`development_causes`, appendix)
- Shared defaults of BIRD and Spider (`conventions`, generated, appendix)
- Recorded answers for the worked example (`worked_outcomes`, appendix)
- Recorded behavior on two generated questions (`generated_choices`, appendix)

## Files

`disaggregated.tex` (per-database, reference conventions, development causes) is no longer included. `generated_examples.tex` (customer counts) is no longer
included. The `tab1a_*` … `tab5_*` files are written by `specbridge.report.figures` for the Markdown records and are not used here.
Earlier notes are under `paper/archive/pre_academic_layout/`.
