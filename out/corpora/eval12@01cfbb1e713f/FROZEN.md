# Frozen evaluation sample: eval12@01cfbb1e713f (2026-10-02)

384 of 400 requested reviewed tasks, frozen for evaluation as delivered. The 16-task shortfall is reported, not filled:
moving tasks to other cells or databases would change the requested workload.

Shortfall (this run could not supply them -- the build stopped after 6 rounds with these cells short; exhaustion of the
cells was NOT shown): insider A2 S3 -2, A2 S4 -4; alien A2 S3 -4, A2 S4 -4; baseball_1 A2 S3 -1; thrombosis_prediction
A2 S3 -1. In these builds most generated programs failed the semantic review (insider 114 of 148, alien 111 of 142);
the sampled review reasons are mostly arithmetic on incompatible quantities.

Depth: built-for cell = measured cell on 384 of 384. Grammar compose-v3.4 (no `require`), rubric v1.1.
Human validation: pending (none of the 384 audited yet).
