# "Enumerate broadly, compute faithfully" (arm `edit`), written 2026-10-13 BEFORE any edit-arm output
Arm: DtP's saved interpretation listing (interpretations + missing, out/reqmethod/dtp) -> ONE call turns each interpretation into a
short clause that states only what it decides (duplicates dropped) -> each clause appended to the ORIGINAL request (no word removed)
-> one SQL call per edited request (the same SQL prompt as dtp/ours) -> execute, merge identical results (as every arm).
Step 1 (signal sweep): open wording only, 30 dev sets, Sonnet and GPT-Sol. Continue to step 2 only if both-readings coverage is
>= sample-3 + 3 sets for at least one model.
Step 2: the specific wordings through the same arm.
GATE (both models): open both-readings >= sample-3 + 5 sets (Sonnet >= 22/30, GPT-Sol >= 20/30) AND specific main right >= ours
(Sonnet >= 29/30, GPT-Sol >= 26/30). Pass -> AMBROSIA dev, then the rewrite experiment and frozen final tests. Fail -> report, and
go to the rewrite experiment (#2) only as a stand-alone controlled test.
Saved arms (out/reqmethod/RESULTS.md): both readings sonnet plain 13, sample-3 17, dtp 1, ours 16; gpt-6-sol 10, 15, 9, 14.

BUG (found 2026-10-14): the DtP interpretation / rewrite lines were parsed with x.strip(" -*0123456789."), which also removed digits
and periods at the END of a line, cutting off final numbers (about half of ~120 flagged AMBROSIA-final interpretations). Every DtP
arm and every rewrite arm (b) is affected; add, standalone, plain, sample-3 and our method are not. Fixed by ambrosia.item_line.
