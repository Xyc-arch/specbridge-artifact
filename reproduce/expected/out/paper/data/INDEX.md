# Exhibit data (built by specbridge.report.exhibit_data; model-free)

- `fig1_coverage.json` (+ .csv) -- radar data: support (12 / all buildable) vs generated
- `tab1_construction.json` (+ .csv) -- construction and control tables (pool per database, depth control min-max over seeds, preferences, required operations, reviewed build)
- `fig2_explicit_vs_precise.json` -- explicit vs precise v2: overall with paired bootstrap, per database, depth (Wilson), within-database permutation test for step depth
- `fig3_real_benchmarks.json` -- confirmation per solver (strict, shape-tolerant, explicit) with paired bootstrap; cause composition dev vs confirmation
- `tab2_library.json` (+ .csv) -- decision types with counts and one rule-selected example each; reference-defect examples
- `fig4_worked_example.json` -- worked synthetic-generation example (rule-selected)
- `families_retrieved_examples.json` -- which library example each selected family's writer was shown (recomputed; deterministic) and what retrieval actually was
- `tab3_generation.json` -- family funnel, distributions, ablation with exact McNemar and paired bootstrap
- `fig5_tab4_disclosure.json` -- disclosure: every dimension per model with bootstrap over families; conditional coverage; alternative validity; matched overhead
- `fig6_inclination.json` (+ .csv) -- silent-question defaults per meaning decision and author group (Wilson), per database, and the library's open meaning records placed
- `fig_impact.json` -- per silent choice: the library edit applied to the reference SQL; answers that change, single values that move > 10% / > 50% (Wilson)
