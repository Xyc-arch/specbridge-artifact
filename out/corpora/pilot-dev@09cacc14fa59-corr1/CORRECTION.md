# Correction of pilot task 8ac7dd4f7e (2026-10-02); the frozen pilot (tag pilot-dev-frozen-2026-10-02) is unchanged

**Status: human validation of the pilot is PENDING.** The user's go-ahead (2026-10-02) approved proceeding to the larger
build; it is not an audit verdict.

- Defect: the natural question's output (1) was "step 5's column (1) (player ID)"; V says column (2) (playing hand).
- Root cause: writer and reviewer were the same model (Sonnet). The Sonnet reviewer passed the draft, passed it again
  alone (`recheck`), and on a rewrite demanded the wrong column itself. The requirements and facts given to both were
  correct (checked).
- Fix (code, `specbridge/comm/verbal/precise.py`): `REVIEW_MODEL` = Opus, separate from the writer (Sonnet); Opus is not
  a solver. The Opus reviewer flags the defective draft; the rewrite reviewed by Opus passes on round 1 with output (1) =
  column (2) of step 5.
- Recheck: all 4 solvers right on both arms of the corrected task (`SOLVER_*.md` here).
- Opus recheck of all 47 frozen pilot questions (`opus_recheck_of_frozen_pilot.json`): 3 flagged -- 8ac7dd4f7e (this
  defect); eafd676353 (toxicology; R/avg(R) vs count/avg(count), possibly equal when the total is constant, plus an
  undescribed join; 3 of 4 solvers right on the natural question); b11cb54742 (news; whether a missing author forms its
  own group; 4 of 4 right). Both are on the human sheet; the human audit decides.
