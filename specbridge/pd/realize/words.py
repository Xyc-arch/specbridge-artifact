"""specbridge.pd.realize.words — EVERY WORD A QUESTION CAN CONTAIN, ON ONE SCREEN.

WHY THIS FILE EXISTS. Part 5 of the objective -- the question reads as English -- felt endless, and the
reason was not that English is hard. The vocabulary was SCATTERED: three copies of the operator words
(`say._OPW`, `say._REL`, and a third grown in `pd.quantity`), disagreeing, so `*` read as "multiplied by"
or "times" and `-` as "minus" or "less" depending which path the renderer took. Every fix was local and
the next draw exposed another copy.

`docs/OBJECTIVE.md` already said the cure: the set of things the generator CAN emit is enumerable, and
enumerating beats sampling. But it can only be enumerated if it is in one place. So this is that place,
and the rule is: A PHRASE A QUESTION CAN CONTAIN IS DEFINED HERE OR IT IS A BUG.

Two consequences worth stating, because they are the point rather than side effects:

  * A WORD CAN BE JUDGED AGAINST ITS NEIGHBOURS. "less" for subtraction looked fine alone and is a
    determinacy risk beside "is less than" for `<` -- one word apart, and a single question carries both.
    Nothing but seeing them together finds that.
  * DUPLICATES BECOME VISIBLE. Three spellings of one filter clause, two of one comparison, are obvious
    on one screen and invisible across sixteen hundred lines.

Nothing here is a decision about WHEN to say something -- that stays in `pd.say`, which knows the query.
This is only WHAT the words are.
"""
from __future__ import annotations

# ---------------------------------------------------------------- operators
# ONE MAP. `-` is "minus" and not "less": `<` renders "is less than", so "A less B" (a subtraction) sits
# one word from "A is less than B" (a comparison), and a question can carry both.
OPERATOR = {"/": "divided by", "*": "multiplied by", "+": "plus", "-": "minus"}

# A DIVISION WHOSE OPERANDS ARE A PART AND ITS WHOLE has a better word than "divided by", and it is only
# better where the alphabet has established the part-whole relation -- otherwise it asserts one.
OPERATOR_PART = {"/": "as a fraction of"}

# SCALING BY A PLAIN NUMBER HAS A WORD, and the word takes ONE argument, so it needs no bracket.
SCALE = {("*", 0.5): "half of",  ("/", 2): "half of",
         ("*", 0.25): "a quarter of", ("/", 4): "a quarter of",
         ("*", 0.1): "a tenth of", ("/", 10): "a tenth of",
         ("*", 0.01): "a hundredth of", ("/", 100): "a hundredth of",
         ("*", 2): "twice", ("*", 3): "three times", ("*", 10): "ten times"}

# ---------------------------------------------------------------- comparisons
# WHETHER THE BOUND IS INCLUDED IS A DECISION a question may state or leave open, so there are two sets
# and `pd.say.SILENT` chooses. Silenced, "at least" and "more than" both become "over", which is what a
# question that does not care about the boundary looks like.
OPPOSITE = {"=": "!=", "!=": "=", ">": "<=", "<=": ">", "<": ">=", ">=": "<"}   # a negated comparison, said
COMPARE = {">": "is more than", ">=": "is at least", "<": "is less than", "<=": "is at most",
           "=": "is", "!=": "is not"}
COMPARE_SILENT = {">": "is over", ">=": "is over", "<": "is under", "<=": "is under",
                  "=": "is", "!=": "is not"}

# ---------------------------------------------------------------- clauses of a sentence
# The query-level clauses, in the order `pd.say._one` may append them. A filter reads one of two ways --
# leading the sentence or trailing it -- and that is variety R itself shows, not a duplicate.
FILTER_LEADS = "Among the rows where %s, "
FILTER_TRAILS = ", counting only the ones where %s"
FILTER_INSIDE = "counting only those where"          # inside an aggregate: "the number of rows ..."
HAVING = ", keeping the groups where %s"
GROUP = " for each %s"
ORDER = ", ordered by %s"
ORDER_DIR = ", ordered by %s %s"
ORDER_SAME = ", %s"
LIMIT_BY = ", giving %s by %s"
LIMIT_PLAIN = ", at most %s of them"
OFFSET = ", skipping the first %s"

# MINED FROM R'S OWN QUESTIONS, not chosen. 62 recovered LiveSQLBench questions say "from highest to
# lowest" twelve times and never once say "highest first", which was ours. Both are English; only one is
# what the source writes, and the openers in `pd.frames` were fitted from the same text for the same
# reason -- the renderer should sound like R rather than like me.
HIGHEST, LOWEST = "from highest to lowest", "from lowest to highest"
ALPHA, ALPHA_REV = "in alphabetical order", "in reverse alphabetical order"   # a text key
EARLIEST, LATEST = "from earliest to latest", "from latest to earliest"          # a date key

# AND "TOP N", which R uses twelve times over: "top 100 facilities", "top 10 users", "top 5 positions".
# Ours was "giving the ten with the highest X" -- five words longer and not a phrase anyone reaches for.
# The ordering word stays, because the cut and the order are one decision and dropping it would leave
# "the top ten" silent about ten of WHAT.
TOP = ", the top %s by %s"
BOTTOM = ", the bottom %s by %s"
EARLIEST_N, LATEST_N = ", the earliest %s by %s", ", the latest %s by %s"     # a cut on a date key


DIFFERENCE, SUM_OF = "the difference between %s and %s", "the sum of %s and %s"   # an aggregate over a +/-
THOSE_VALUES = "those values"          # the one value column of the step just described
TOTAL = "the total"
AVERAGE = "the average"
# The mean of the SAME column the clause is already about. "Enrolment is more than its average" says in
# three words what "more than the average enrolment" says in five, and does not double the word on a
# column the database already describes as an average.
ITS_AVERAGE = "its average"

GAP_TO_MEAN = "%s minus its mean"
RELATIVE_GAP = "%s above its mean as a fraction of it"   # no comma: a comma makes the
                                                         # renderer bracket it as a phrase
WITHIN = "%s within the same %s"

# EVERY QUANTITY THE PROFILE CAN ENUMERATE NEEDS ONE PHRASE THAT NAMES BOTH ITS OPERANDS AND ITS ROW
# SET. That is the admission rule for the alphabet -- not whether R happens to use the shape, which is
# the LAW's business. A quantity with no such phrase is not in the alphabet; a quantity with one is,
# and the law decides how often it is drawn.
SHARE_OF_GROUP = "%s as a fraction of the total %s for its %s"
DAYS_BETWEEN = "the number of days from %s to %s"

# THE SAME WORDS `pd.say.window` ALREADY USES, because a seeded name and a rendered phrase must not be
# two descriptions of one thing. "Percentile" is deliberately NOT the word: PERCENT_RANK returns 0 to 1
# and "percentile" invites 0 to 100 -- the fraction-versus-percentage ambiguity that cost 26 of 39
# failures on 2026-09-20. The phrase states the range instead.
# ONE PHRASE PER WINDOW, USED BY BOTH THE RENDERER AND THE ALPHABET. `pd.say.window` had these as
# f-string literals and `pd.derive` needed the same words to seed a name with; two copies of one phrase
# is how "its mean" and "its average" came to denote different numbers. `%s` is the ordering column,
# then the "within the same X" tail (or "").
#
# "PERCENTILE" IS DELIBERATELY NOT THE WORD: PERCENT_RANK returns 0 to 1 and "percentile" invites 0 to
# 100 -- the fraction-versus-percentage ambiguity that caused 26 of 39 failures on 2026-09-20. The
# phrase states the range instead.
PERCENT_RANK_SAYS = "how far up the order by %s it sits%s — as a fraction from 0 for the first to 1 for the last"
RANK_SAYS = "its rank by %s%s (tied rows share a rank and the next rank skips)"
FRACTION_OF_ROWS = "the fraction of rows where %s"
FRACTION_OF_ROWS_IN = "the fraction of rows in %s where %s"     # ...in a named table
YEAR_OF, MONTH_OF = "the year of", "the month of"
IS_RECORDED, IS_MISSING = " is recorded", " is missing"


# ---------------------------------------------------------------- comparing two names
def plain(s):
    """A name reduced to what it IS, for comparing one against another.

    THREE COPIES, TWO IDENTICAL AND ONE DIFFERENT IN A WAY NOBODY CHOSE. `solve._norm` and `vocab._norm`
    were the same regex; `vouch._plain` used `str.isalnum()`, which is Unicode-aware, so it kept "café"
    as "café" where the others gave "caf". Two modules could therefore disagree about whether a
    description repeats a column's own name -- the test that decides whether a column can be talked
    about at all.

    Checked before merging: across all fifteen target databases the two agree on every one of 1,081
    column names, so this changes nothing today. It would have, on the first database with an accent in
    it, and silently.
    """
    import re
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


# ---------------------------------------------------------------- words that carry no content
# TWO LISTS OF ENGLISH STOPWORDS, once a set in the deleted `pd.channel` and a regex in `specbridge.pd.realize.vocab`, overlapping but not
# equal -- so two modules disagreed about whether "per" or "each" says anything. One list; a caller that
# needs a pattern builds it here.
# A NOUN PHRASE DOES NOT END ON ONE OF THESE. `wedding` has a column `Organized_by`, which splits into
# two ordinary words and was adopted as the name "organized by" -- so a question read "show me organized
# by, open date and year", which is a clause left open, not a thing being asked for. Used where a name is
# MADE, not where a sentence is checked: a name ending here is not a name.
DANGLING_TAIL = frozenset(
    "by of in on for to with at from and or as into over under between per about after before".split())


STOPWORDS = frozenset(
    "the a an of for in on at to and or with by from is are was were this that its it their there "
    "each whose per".split())


def stop_pattern():
    """The same list as a regex, for matching inside prose."""
    import re
    return re.compile(r"\b(%s)\b" % "|".join(sorted(STOPWORDS)), re.I)


# ---------------------------------------------------------------- the rest of the sentence
# MOVED HERE from the renderer: every phrase it can emit that this file did not
# define. Part 5 stays endless for exactly as long as that list is non-empty: a phrase outside this file
# cannot be read against its neighbours, and reading them together is the only way to notice that "less"
# for subtraction sits one word from "is less than" for a comparison.
STEP_VERB = "make a table of"
STEP_VERB_ING = "making a table of"
ACROSS_ALL = "across all rows"
OTHERWISE = "for anything else"
IS_BETWEEN = "is between"
IS_ONE_OF = "is one of"
CONTAINS = "contains '"
ITS_POSITION = "its position"
ITS_RANK = "its rank"
THE_HIGHEST, THE_LOWEST = "the highest", "the lowest"

# THREE WAYS TO SAY "DO NOT REPEAT A ROW", chosen by `WORDING`. Measured, not preference: the plain one
# solves 67.5% and "each distinct combination once" 40%, so the wording is a condition the corpus can
# vary rather than a style to settle.
REPEATS = (", and do not repeat a row", ", listing each one only once",
           ", each distinct combination once")
