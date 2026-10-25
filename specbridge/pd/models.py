"""specbridge.pd.models — WHICH MODEL PLAYS WHICH PART. One place, one variable each.

There were four `MODEL` constants, in `pd.agent`, `pd.say`, `pd.solve` and `specbridge.pd.realize.vocab`, and three of them
read the SAME environment variable. So `PD_MODEL=...` moved three unrelated jobs at once: you could not
change the solver without also changing the thing that NAMES quantities, which is a different decision
with different stakes -- a bad solver scores worse, a bad namer corrupts the corpus.

Four parts, and what each is allowed to do. The asymmetry is the whole safety argument:

    SOLVER      answers the question. Never touches generation; it is the thing being measured.
    CHOOSER     picks among candidates the generator has ALREADY established are legal (`bind.CHOOSE`).
                It can only pick, so a wrong answer costs a worse question and never an unsound one.
    DESCRIBER   writes a column description from the schema and five values, where the database gives
                none (`vocab.describe_missing`). A fact about the database, checkable against it.
    NAMER       names a computed quantity (`say.NAME`). Off by default, and adjudicated: a name that
                collides with a column, repeats, or runs long is refused.

EACH KEEPS ITS OWN VARIABLE and falls back to `PD_MODEL`, so existing invocations still work and a new
one can move a single part.

RECORDED DISAGREEMENT, not silently resolved: the session notes say the solver default is
`qwen2.5-coder:14b`, and the code has said `7b` since it was written. Every eval this project has run
sets the variable explicitly, so the default has not been load-bearing -- but the two disagree, and
changing a default quietly would invalidate comparisons against everything measured before. Left as it
is, written down here instead.
"""
from __future__ import annotations
import os


def _pick(own, default):
    """This part's own variable, else the shared one, else the default."""
    return os.environ.get(own) or os.environ.get("PD_MODEL") or default


SOLVER = _pick("PD_SOLVER", "qwen2.5-coder:7b")        # see the note above: the record says 14b
CHOOSER = os.environ.get("PD_AGENT") or _pick("PD_CHOOSER", "qwen2.5-coder:14b")
DESCRIBER = _pick("PD_DESCRIBER", "qwen2.5-coder:7b")
NAMER = _pick("PD_NAMER", "qwen2.5-coder:7b")
# READER vetoes the English of a SKELETON -- a question with its names and values blanked -- and can only
# say "a person would not write this". Nothing it says enters a question; see `pd.english.veto`.
READER = _pick("PD_READER", "haiku")
# PROFILER fills the blanks of a database's column profile (`pd.profile.complete`): a unit, a population,
# a whole, a containment -- fields of a fixed schema, once per table, cached in the profile file. A
# containment it claims is checked on the values before it is kept.
PROFILER = _pick("PD_PROFILER", "sonnet")
# VETO answers Y/N per candidate quantity (`pd.profile.veto`) -- a judgment, batched, cached; the fast model.
VETO = _pick("PD_VETO", "sonnet")           # it must NAME the quantity; the fast model named chains of percents

CLI = ("haiku", "sonnet", "opus")     # names that go through the `claude -p` CLI, not ollama
