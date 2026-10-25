# Our method with edited readings (arm `ours_edit`), written 2026-10-13 BEFORE any output
Same as `ours` (one listing call, then one SQL call per reading, merge identical results), except the form of a reading: the
listing call returns, per reading, ONE short clause that states that reading; the reading given to the SQL call is the ORIGINAL
request verbatim + " " + that clause. One reading -> the original request unchanged, one SQL call. At most 4 readings.
Pilot: 30 dev request sets (ledger.sets), all three wordings, Sonnet and GPT-Sol; same SQL prompt as `ours`.
GATE (each model): open both-readings >= sample-3 + 3 sets (Sonnet >= 20/30, GPT-Sol >= 18/30) AND specific main right >= ours
(Sonnet >= 29/30, GPT-Sol >= 26/30) AND mean calls <= 3 per request (all wordings).
Pass -> run the 115 untouched sets with plain, sample-3, ours and ours_edit, report in Sec 5.4 as a result. Fail -> Sec 5.4 as written.
