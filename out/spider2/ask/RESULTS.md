# Ask mechanism on Spider 2.0-lite, sonnet

STEP 0 RULE (written before the run): continue to Step 1-2 only if the oracle beats plain by at least 15 points per instance (tolerant score) with exact paired McNemar p < 0.05. Otherwise stop and report.

## Step 0, oracle ceiling

33 strict meaning tasks not in the pilot; 87 (task, meaning group) instances. Right = the one answer matches an accepted answer of THAT group (tolerant: official comparison; strict: also the same number of columns).

| arm | instances right, tolerant | strict | tasks with every group right, tolerant |
|---|---|---|---|
| plain | 15/87 (17.2%) | 10/87 | 0/33 |
| oracle | 20/87 (23.0%) | 14/87 | 3/33 |

Oracle - plain (tol): +5.7 points; +11/-6 instances, exact McNemar p = 0.33.

Oracle - plain (strict): +4.6 points; +8/-4 instances, exact McNemar p = 0.39.

**Step 0 decision: STOP** (tolerant gain +5.7 points, p = 0.33; rule: >= 15 points and p < 0.05).
