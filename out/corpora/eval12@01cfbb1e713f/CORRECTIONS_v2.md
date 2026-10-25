# Corrected precise questions, version 2 (2026-10-03); the frozen version (corpus.jsonl, tag eval12-tasks-frozen-2026-10-02) is unchanged

`corpus.v2.jsonl`: 382 tasks; 11 questions replaced ("repaired after read-back"), the rest identical.

1. READ-BACK (execution, not opinion): Opus -- not one of the four evaluated solvers -- answered every natural question
   alone through the solver harness: 371 of 382 right (`SOLVER_opus.md`). (A first attempt was cut by a usage limit: 335
   empty answers had been saved as wrong; they were removed and redone, and the harness now refuses to save a failed call.)
2. The 11 failures: Opus right on explicit V for all 11 (`../eval12@01cfbb1e713f-readback11/`), so the wording was at fault.
3. REPAIR (`specbridge.comm.verbal.repair`): the writer (Sonnet) revised each with the reader's SQL as the finding, the
   reviewer (Opus) reviewed it alone; one task needed a second round ("product price per unit" read as price ÷ quantity).
   Read back again: 11 of 11 right.
4. Four solvers on the 11 repaired questions, natural before -> after: haiku 6 -> 10, sonnet 3 -> 11, gpt-6-sol 6 -> 11,
   gpt-6-luna 7 -> 10 (`../eval12@01cfbb1e713f-v2-changed/`).

Defect kinds seen: a measure renumbered between steps and the wrong one named; a catalogue label carrying a unit cue
("hematocrit fraction", "product price per unit") that the question passes on without the column. A single reader
misses some (568a31721e, "hematocrit fraction", was read correctly by Opus). Hence the human audit.

HUMAN AUDIT (pending): https://claude.ai/artifact/LqyS8UdgokBPrnEt1ZjkRw, collection `eval12_fidelity`: 63 tasks, blind
to group -- 11 repaired, 22 solver suspects not caught by the read-back, 30 stratified random (`audit_groups_v2.json`).
