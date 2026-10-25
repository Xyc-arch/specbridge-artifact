# BIRD scored with both readings -- protocol written 2026-10-25 before any call

Question: when a BIRD question is silent on a choice that changes its answer, how often does a model's answer give the other
reading, which BIRD scores as wrong?
Items: out/rewrite/bird/items.json (one library edit of the reference SQL changes the answer; degenerate edits excluded), types
ties, count_unit, join_kind only (boundary: "over"/"under" settle the bound; null_filter: defective edits, see out/rewrite/bird/GATE.md).
Solvers: haiku, sonnet, gpt-6-sol, gpt-6-luna; original question + evidence; the plain SQL prompt and schema of the clarification
study (disclose.PLAIN); one call per question; no exploration; at most 6 in parallel. ONE run, no repeats, no prompt changes.
Scoring: BIRD execution match against the reference (A) and the edited reference (B). Reported per model and pooled: right by
BIRD; other reading only; either; share of BIRD-wrong answers that give the other reading.
