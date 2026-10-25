# Figures used in the manuscript


> **2026-10-15:** the paper now has four tables, all numeric: Table 1 (every result per model, with reliability rows and a breakdown by type and source), Table 2 (construction counts), Table 3 (the four methods on AMBROSIA and request sets; was Tables 6-7) and Table 4 (benchmark comparison, numbers and check marks). The example tables (old 4, 5, 8) are Tables S4-S6 of the supplement; old Tables 1 and 10 became prose. Figure 3 is now the second worked example, so later figures are numbered one higher. Sections below may use the earlier numbering.


> **2026-10-14:** every result on request sets now uses the 178 sets an author's review accepted (of 215; `human_supervision/`, `specbridge/comm/transfer/reviewed.py`). Counts below that cite 215 sets, 480 readings or 30 sets are from before that change; the paper and `out/paper/data/` hold the current numbers.

Manuscript: *Text-to-SQL Models Know More Than They Tell* (`paper/tex/specbridge.tex`).

The thirteen figures included by `paper/tex/specbridge.tex`, in manuscript order. Every figure is one column wide and printed at 1:1 (text 7–8 pt).
Two kinds of source:

- **Diagrams** (Figures 1, 2, 13) are TikZ in `tikz/<name>.tex`, built with XeLaTeX (Arial) into `diag_<name>.pdf`, with Font Awesome 5
  icons (package `fontawesome5`; free, SIL OFL 1.1 / CC BY 4.0). `<name>.tex` holds the caption and includes the PDF.
- **Data figures** (Figures 3–12) are `col_<name>.pdf`, drawn by `specbridge/report/figures_col.py` from `out/paper/data/`. The
  caption and inclusion code are in `specbridge.tex` (or `supplement.tex`). 

The figures report saved experiments; no new model runs. Execution decides query matches; Opus (blind to the solver) judges explanations.
The wide multi-panel originals (`fig1_coverage` … `fig6_inclination`) are kept for the Markdown records (`../result.md`,
`../../out/paper/explain/fig_explain.md`) and are not used by the manuscript.

## Figure 1 — One request, two correct calculations (`teaser.tex`, TikZ)

The request "For each film rating, what is the average rental price per day?" on `sakila_1`. Reading A averages each film's daily price,
`AVG(rental_rate / rental_duration)`; reading B divides two averages, `AVG(rental_rate) / AVG(rental_duration)`. The values are **real**,
computed on the `film` table: G 0.668 vs 0.597, PG 0.642 vs 0.600, R 0.662 vs 0.616 dollars per day (NC-17 0.632 vs 0.578 and PG-13 0.646 vs
0.601 are not shown). Below: the three requests (wording shortened), and the four solvers' recorded single-call responses to the open request
(`out/transfer/eval12-v2/render/disclose/<solver>/eval12__eval12@01cfbb1e713f-06768b2b94__open.json`, judge in `judge.json`). All four return A;
Sonnet and GPT-Luna name the choice; only Sonnet gives SQL that runs and returns B. The full request also asks for replacement cost and a ratio
across ratings (Section 5, verbatim).

## Figure 2 — The pipeline (`pipeline.tex`, TikZ)

Three swimlanes. Construct: catalogue (one model review per database) → generate SQL with requested depth and operations (1,198 of 1,200
delivered) → describe it as $V$ by code. Mine benchmarks: BIRD 581 and Spider 200 questions, original question vs $V$ of the reference → diagnose
why the original failed → decision library (14 kinds, 624 examples, frozen before held-out runs). Test: apply one choice as an SQL edit that runs
and changes the answer → write $q_A$, $q_B$, $q_\circ$ with two reviewers (215 request sets) → evaluate by execution and by the judge. Counts:
`../result.md` R1, R3–R5.

## Figure 4 — What each construction mechanism contributes (`col_ablation`)

Data: `fig1_coverage.json` (`ablation`). 2,350 attempts per configuration on the 12 evaluation databases. With all mechanisms, 2,341 (99.6%) are
valid, on target and sound. Removing one mechanism: deduplication 92%, "must vary" 92%, step data checks 89%, restatement rules 60%, column profile
31%, type rules 28%, look-ahead 3.3% (most attempts miss the requested depth); none 0.1%. The checker uses the full rules as its reference, so this
shows enforcement of the rules, not an independent judgment of meaning.

## Figure 5 — Description $V$ vs natural request (`col_specification`)

Data: `fig2_explicit_vs_precise.json`. Left: share of 382 generated tasks answered right, with task-bootstrap 95% intervals; above, natural minus
$V$ in points. Correct counts ($V$ → natural): Haiku 343→353, Sonnet 380→371, GPT-Sol 378→370, GPT-Luna 307→345. Right: errors from $V$ by step
depth 3–6; GPT-Luna 1/100, 13/86, 29/100, 32/96 (within-database permutation p = 0.0002); Haiku p = 0.0402; Sonnet and GPT-Sol make few errors.
Natural requests include eleven repairs after the read-back test.

## Figure 6 — Answering and communicating on 178 request sets (`col_disclosure`)

Data: `fig5_tab4_disclosure.json`. One single call per request that asks for SQL, unsettled assumptions and up to two alternatives. Rows: specific
request answered right; open request returns A or B; names the open choice (judge); states its reading truthfully (judge); returns both A and B
(execution). Diamonds: both returned, among sets where the solver answered both specific requests right with exploration: Haiku 20/144 (13.9%),
Sonnet 83/171 (48.5%), GPT-Sol 63/171 (36.8%), GPT-Luna 13/138 (9.4%). When a solver states a reading it is true of its SQL in 98–100% of cases;
the weak links are naming the choice and supplying the other reading.

## Figure 7 — Why a reading was missed (`col_decomposition`, generated)

Source: `fig5_tab4_disclosure.json` (request sets: same single call, exploration) and `out/ambrosia/decomposition*.json` (AMBROSIA dev + confirmation, 120 questions per model). Share of missed readings the model computes when asked for that reading alone, Wilson 95% intervals: request sets single call 66–95% (178 accepted sets), AMBROSIA 49–66%. Replaces the former decomposition table.

## Figure 8 — What each model does with the 178 open requests (`col_outcomes`)

Source: `accepted.json`, `scopes.accepted.models.<model>.outcomes` (`specbridge.report.accepted`). Each open request gets exactly one
outcome: both readings returned; choice named (Opus judge) but one reading; one reading, choice not named, although the same single
call answers both specific requests right; a reading the single call does not compute. Haiku 25/13/95/45, Sonnet 86/26/61/5,
GPT-Sol 63/14/66/35, GPT-Luna 15/34/73/56.

## Figure 9 — Held-out benchmark questions (`col_real`)

Data: `fig3_real_benchmarks.json` (`confirmation`). BIRD 96 and Spider 50 held-out questions; per solver, the original question (strict), the
original allowing extra or reordered columns, and the description $V$ of the reference SQL; question-bootstrap 95% intervals. BIRD strict:
49.0–74.0% (47–71 of 96); with column differences allowed: 65–76 of 96; from $V$: 95.8–100%. Spider strict 64–82%, column-tolerant 84–92%, $V$
96–100%. $V$ also supplies column mappings and calculation steps, so the gap is not an ambiguity rate. Exploration ablation (GPT-Sol, exploration off): $V$ 96/96 with and without; original 61 vs 59 of 100 (p = 0.73); `out/confirmation/bird_heldout100/runs_noexplore/gpt_6_sol/RESULTS.md`.

## Figure 10 — Why the original question failed (`col_causes`)

Data: `fig3_real_benchmarks.json` (`causes`, development). One cause per case (Opus) for development questions Haiku answered right from $V$ and
wrong from the original: BIRD 162 cases (batches 3–8), Spider 51. Shares are printed where at least 7%. BIRD: run variation 30%, column or value
mapping 19%, output columns 17%, unstated requirement 17%, added steps 8%, open choice 6%. Spider: output columns 31%, run variation 25%, open
choice 14%. Two development runs make run variation visible; the held-out confirmation (one run) cannot show it.

## Figure 11 — The reference's reading of a silent question is its authors' convention (`col_defaults`)

Source: `fig6_inclination.json`. Two panels, one per decision with a clear split: ties at an extreme (% returning one row) and
counting over a join (% counting joined rows). Bars by author family: BIRD (blue), Spider's own authors (green), Spider questions
imported from older datasets (orange; for each decision, the imported group that reverses it). Ties: BIRD train 90% (1431/1590),
dev 91% (229/251); Spider train 96% (940/983), dev 98% (170/174); Geo, Restaurants 7% (21/281). Counting: BIRD 88% (1706/1934),
87% (241/278); Spider 95% (349/369), 99% (73/74); Academic, IMDB, Yelp 0% (0/96). Five other decisions: every group >= 91%
usual reading (n >= 10). Redrawn 2026-10-14.

## Figure 12 — Silent BIRD questions whose answer changes under the other reading (`col_impact`)

Source: `out/impact/impact.json` (`specbridge.report.impact impact`, no model calls) -> `fig_impact.json`. For each BIRD dev question
whose reference settles a choice with no cue in the question or evidence (the word list of Figure 10), the library edit for the
other reading is applied to the reference SQL and both are run. One stacked bar per choice type, all segments over the questions
silent on it: single value moves > 50%, moves 10-50%, other change (row set or order, or a value moving < 10%). Totals: bound 8/20,
rows vs entities 99/268 (86 > 50%), ties 56/217, missing values 15/155, join kind 68/1130. Per question (text): 222 of 1,187 change
(169 without join edits), single value > 10% in 101; ties change the top-k set in 33 of 215 ordered answers. Spider 2.0: 14 of 82.

## Figure 13 — The disclosure method's trade-off on AMBROSIA (`col_method`, generated)

Source: `out/ambrosia/final/final.json` (`specbridge.comm.transfer.ambrosia`; figure `specbridge.report.figures_col method`). 150 fresh test questions per solver (90 ambiguous, 60 unambiguous), Sonnet and GPT-Sol, four arms interleaved, 0 safety refusals. x: precision on unambiguous questions; y: AllFound on ambiguous questions with Wilson 95% intervals; label: calls per question. Pooled paired differences (in the text): ours - DtP precision +18.0 [11.4, 24.4], AllFound -7.2 [-14.4, -0.6] (pre-written coverage claim failed); ours - Sample-3 better on every measure. Full record: `out/ambrosia/method/RESULTS.md`, `TRADEOFF.md`.

## Figure 14 — Editing versus rewriting a request (`col_rewrite`, generated)

Source: `out/rewrite/runs` and `out/rewrite/classify.json` (`specbridge.comm.transfer.rewrite`; gate `out/rewrite/GATE.md`). 401 readings from accepted sets (of the first 120 per model in a fixed random order, 480). Pooled accuracy: original specific 86.5, open + clause 86.0, interpretation rewrite 77.8, standalone question 75.1. Right panel: what the interpretation rewrite lost on its 58 failures (output columns 33%, formula 21%, join 17%, grouping 12%, filter 7%, the choice 7%, other 3%).

## Supplement only — Which features the generator can build (`col_coverage`)

Data: `fig1_coverage.json` (`support_all_buildable`, `meaning.features`). For each of eleven features, the share of 152 usable databases (of 190
examined) whose schema allows it (light bars) and where a generated program with it was accepted by both model reviewers (dark bars); the labels
give both counts. Aggregation, baseline comparison, share of total and the two depth thresholds are possible on all 152; top-k within group on
104 but accepted on 69; ratio and difference of two measures are possible on 21 and accepted on 8 and 3. The gap is reviewer judgment on the data,
not a schema limit; it describes the implemented rules, not every SQL program.

## Figure 3 — A second worked example (`worked.tex`, TikZ)

Source: `fig4_worked_example.json`, `../example.md` E1, `../../library/examples.jsonl` (`bird_pairs:b034`). On `insider` (arithmetic depth 1,
step depth 3), step 2 computes a per-order-type baseline. A averages the transaction means (each transaction once); B averages all snapshots
(each snapshot once). Both run; all ten output rows change (transaction IT183513: ratio 2.04796 vs 2.05000). The writer was shown a BIRD case of
the same kind (`california_schools`: rank districts by their best school's score or by the average over their schools). The three requests
differ only in the phrases shown; all checks passed and both reviewers accepted the open request for both readings. Chosen by fixed identifier
order among 39 eligible sets, before any model answer was seen.

## Reproduction

From the repository root: `python -m specbridge.report.figures_col` (data figures), then `make -C paper/tex` (diagrams and both PDFs).
Earlier notes are under `paper/archive/`.
