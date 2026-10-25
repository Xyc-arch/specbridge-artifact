# Simulated user clarification on real BIRD questions (`specbridge.comm.transfer.rewrite` run_bird), written 2026-10-14 BEFORE output
Why: on our request sets, rewriting kept the choice but lost OTHER requirements (output columns, formula, join). Here: a real BIRD
dev question (+ its evidence) is followed by a simulated user turn that settles one library choice, as in a conversation.
Questions: BIRD dev questions where a library edit of the reference SQL changes the answer (out/impact/impact.json), first applicable
edit per question, excluding edits whose result is empty, all NULL or turns a column into constant 1, and count edits on a GROUP BY
key. Clarification: code template per choice type, naming the column/table/value of the edit. Gold for the clarified reading: the
edited reference SQL, executed.
Texts (Sonnet and GPT-Sol; same plain SQL prompt with schema; one call each; random order per question):
  (c) ADD: question + evidence + the clarification appended;  (b) REWRITE: DtP interpretation prompt told the clarification;
  (d) STANDALONE: condense prompt, question + evidence as the first turn, the clarification as the follow-up.
Right = matches the clarified gold (BIRD execution comparison). Failure cause by execution: equals the unclarified gold
(clarification lost) | neither (another requirement lost) | does not run.
GATE (pooled over both models): (c) - (b) >= 3 points with exact McNemar p < 0.05; the same for (c) - (d). Per model reported.
Resumed 2026-10-14 ~09:00 after a crash (a gold query timed out); questions whose gold does not run within 60 s are skipped and listed in skipped.txt.

EXCLUSION after the run (2026-10-14): the 6 null_filter questions (12 pairs) have a defective gold -- the edit did not add the
NOT NULL filter, so the "clarified" gold equals the unclarified reference (e.g. q1178: gold 'M', clarified answer 'F'). They score 0
in every arm, so the McNemar counts are unchanged. Reported numbers exclude them: 143 questions, 286 pairs.

BUG (found 2026-10-14): the DtP interpretation / rewrite lines were parsed with x.strip(" -*0123456789."), which also removed digits
and periods at the END of a line, cutting off final numbers (about half of ~120 flagged AMBROSIA-final interpretations). Every DtP
arm and every rewrite arm (b) is affected; add, standalone, plain, sample-3 and our method are not. Fixed by ambrosia.item_line.
