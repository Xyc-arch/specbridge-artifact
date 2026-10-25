"""specbridge.pd.realize.stored — THE FORM A VALUE IS STORED IN, AND THE FORM A PERSON WOULD SAY.

A ported question names its values exactly as the database holds them, and that is the one thing real questions never
do. `time_slot.day` holds 'W'; a person says Wednesday. `Diagnosis` holds 'PM, PSS, RA, SJS'; a person says
"diagnosed with RA". `attacking_work_rate` holds the string 'None' beside real NULLs; a person says "not recorded"
and means both. `Laboratory.DNA` holds its numbers as text; a person says "more than 10" and `> '10'` compares
letter by letter -- on `CRP` that is 5825 rows where the answer is 45.

So four facts about a column, each read from the column's own values and the database's own documentation, and each
turning one leaf into the SQL that makes the natural sentence true. No new program shapes: the same leaf, bound onto
a column that stores its values this way, comes out as the query a person meant.

WHY THE DOCUMENTATION IS THE ONLY SOURCE FOR A CODE'S MEANING, and why that same door decides what counts as
missing: '-' is 10,528 single bonds in `toxicology.bond` and a documented one; '-' in `thrombosis.Laboratory.CRP` is
documented nowhere and means the test was not run. The identical string, a value in one database and a hole in the
other, and nothing but the database's own words separates them. A column whose documentation names a string is
never read as missing, which is the guarantee -- not a list of exceptions.
"""
from __future__ import annotations
import re
from dataclasses import dataclass


MISSING_MARKERS = {"", "n/a", "na", "none", "null", "-", "--", "?", "unknown", "not applicable", "nan"}
_NUM = re.compile(r"^\s*-?\d+(\.\d+)?\s*$")
# `cl: chlorine`, `'=': double bond`, `"+" --> carcinogenic`. One pattern, because these are the same sentence.
# Quotes, INCLUDING the ones a Windows editor left behind. `toxicology` documents its commonest bond as
# “-”: single bond, and reading those bytes as part of the code lost the 10,528 single bonds and kept only the
# rare two. Every quote a description has ever used, in one class, used on both sides.
_Q = "\"'‘’“”\x91\x92\x93\x94`"
# The code starts where a word does. Without `(?<![A-Za-z0-9])` the tail of "evidence:" parsed as the code 'ence'.
_PAIR = re.compile(r"""(?<![A-Za-z0-9])[%(q)s]?([^\s%(q)s,;]{1,4})[%(q)s]?\s*(?::|-->|→)\s*([A-Za-z][A-Za-z ]{1,24}?)(?=\s{2,}|\n|\s*[%(q)s]?[^\s%(q)s,;]{1,4}[%(q)s]?\s*(?::|-->)|\s*$)"""
                   % {"q": re.escape(_Q)})
SEPARATORS = (", ", ",", "; ", "/")
_DDMM = re.compile(r"^(\d\d)/(\d\d)/(\d{4})$")
# AND THE SAME COLUMN MAY HOLD THE OTHER ORDER. `formula_1.drivers.dob` is 834 dates written '14/01/1977' and
# seven written '1899-08-03'. Rearranging every value would turn those seven into '03-0189'; declining the column
# for them would give up the one place a date order can be demonstrated. So both are put in the same order, which
# is correct for each row rather than for the majority.
_ISO = re.compile(r"^\d{4}-\d\d-\d\d$")


@dataclass(frozen=True)
class Stored:
    words: dict = None      # stored value -> how a person says it: this database's own documentation, or the
                            # SAME ROW of a neighbouring column that spells it out
    numeric: bool = False   # a text column holding only numbers: a threshold has to CAST or it sorts letters
    listed: str = None      # the separator, where one cell holds several values
    absent: tuple = ()      # strings standing for missing
    dayfirst: bool = False  # a date written DD/MM/YYYY: it does not sort, and it does not compare

    def __bool__(self):
        return bool(self.words or self.numeric or self.listed or self.absent or self.dayfirst)


def meanings(text):
    """{code: what it means}, from a column's own `value_description`, or {} when it documents no codes.

    Strict on purpose. A code is SHORT and its meaning is a short phrase: `student_club.zip_code.type` documents
    "Standard: the normal codes with which most people are familiar", where the code is already the word and the
    meaning is a sentence -- saying that instead of the value would make the question worse, not more natural.
    Distinct meanings, or two codes answer to one word and the question stops having one answer.
    """
    if not text: return {}
    out = {}
    for code, mean in _PAIR.findall(str(text)):
        mean = " ".join(mean.split()).strip().lower()
        if not (1 <= len(mean.split()) <= 3) or mean == code.lower() or len(mean) < 3: continue
        if code in out and out[code] != mean: return {}
        out[code] = mean
    if len(out) < 2 or len(set(out.values())) != len(out): return {}
    return out


_SINGLED = re.compile(r"[(\[%(q)s]\s*([^\s%(q)s()\[\],;]{1,4})\s*[)\]%(q)s]" % {"q": re.escape(_Q)})


def mentioned(text):
    """Every short string this column's documentation SINGLES OUT — quoted, bracketed, or explained by name.

    Weaker than `meanings` and used for a different decision. `Patient.Admission` is described as "admitted to the
    hospital (+) or followed at the outpatient clinic (-)": that is not a name for '-' short enough to say in a
    question, but it is the database telling us '-' is an answer rather than a hole. Whether a string MEANS
    something and whether it means NOTHING are two questions, and only the second one is settled here.
    """
    if not text: return set()
    return set(_SINGLED.findall(str(text))) | set(meanings(text))


def is_word(vals):
    """Do these values SPELL something, or are they codes? `sakila` shouts its actor names in capitals and a person
    types "Fred"; `schools.EdOpsCode` is 'TRAD' and nobody writes "Trad". A word has a vowel and some length."""
    w = [v for v in vals if isinstance(v, str)]
    return bool(w) and sum(bool(len(v) >= 5 and re.search(r"[AEIOUaeiou]", v)) for v in w) >= 0.8 * len(w)


def of(values, described="", nulls=0, handle=False, table_says="", written_out=None):
    """What this column does with its values, from a sample of them and what the database says about them.

    `values` are the non-null values sampled from the column, `described` its `value_description`, `nulls` how many
    rows of the sample held a real NULL, `handle` whether the column names rows rather than measuring them, and
    `table_says` what the database says about this column's NEIGHBOURS, and `written_out` the map a neighbouring
    column supplies from a stored form to the way the same row spells it out.
    """
    vals = [v for v in values if isinstance(v, str)]
    if len(vals) < 20: return Stored()
    seen = set(vals)
    doc = meanings(described)
    said = mentioned(described)
    # A COLUMN'S VALUES MAY BE EXPLAINED UNDER ITS NEIGHBOUR. `toxicology` explains '+' and '-' in the description
    # of `molecule.molecule_id`, and the column they describe is `molecule.label` -- so `label`'s 191 dashes read
    # as holes when they mean "not carcinogenic". Taken only where the neighbour singles out EXACTLY the values
    # this column takes, which a description of some other column cannot do by accident.
    if seen and seen <= mentioned(table_says): said |= seen

    # A CODE WHERE A WORD IS MEANT -- and only where the documented codes are the values actually stored.
    words = {v: doc[v] for v in seen if v in doc}
    # ...OR A NEIGHBOUR THAT SPELLS THE SAME VALUE OUT. Same door, because it answers the same question: what
    # would a person have said instead of this. One comes from the database's words, one from its rows.
    for v, full in (written_out or {}).items():
        if v in seen: words.setdefault(v, full)
    if len(words) < 2: words = None

    # A NUMBER KEPT AS TEXT. EVERY value must parse, with nothing else in the column: `CAST('-' AS REAL)` is 0.0 in
    # SQLite, so one undocumented dash in a column would sit silently below every positive threshold and the leaf
    # would no longer decide what the question says it decides. Where a column mixes numbers with anything else, a
    # threshold on it is genuinely unclear and the right move is to decline the site, not to guess a reading.
    # A HANDLE IS NOT A MEASUREMENT even when it is spelled with digits. `advisor.s_ID`, `course_id` and `CDSCode`
    # are all text holding only numbers, and "more than 14554" is not a question anyone asks about a student id.
    # ...AND IT MEASURES RATHER THAN NAMES. `NCESSchool` takes 3,266 values and `NCESDist` 357; "how many schools
    # have an NCES number above 611210" is not a question, and `handle` does not catch either name.
    numeric = not handle and 8 < len(seen) <= 200 and all(_NUM.match(v) for v in vals)

    # SEVERAL VALUES IN ONE CELL. The separator has to actually separate: splitting must yield items that RECUR
    # across rows, or a comma inside one free-text note would make every note a list of one.
    listed = None
    if not numeric:
        for sep in SEPARATORS:
            held = [v for v in vals if sep in v]
            if len(held) < 0.15 * len(vals): continue
            items = [i.strip() for v in held for i in v.split(sep) if i.strip()]
            # AN ITEM IS A THING SOMEONE NAMES. Without this, `drivers.dob` "07/01/1985" read as a list of three
            # (the numbers recur across rows) and every Wikipedia url read as a list of five, because "http:" and
            # "wiki" recur in all of them.
            if not items or not all(re.search(r"[A-Za-z]", i) and len(i) <= 40 and not re.search(r"[.:@]", i)
                                    for i in items): continue
            # AND THE ITEMS RECUR, WIDELY. One repeat was enough to call `invoices.billing_address` a list --
            # street addresses that happen to share a town. A list is a vocabulary: most of what it draws from is
            # drawn more than once.
            back = len(items) - len(set(items))
            if back >= 0.3 * len(items): listed = sep; break

    # A WRITTEN "MISSING" BESIDE REAL NULLS -- neither test on its own finds both halves. Excluded the moment the
    # documentation gives the string a meaning, which is what keeps `bond_type`'s 10,528 single bonds out.
    # ...AND THE STRING IS NOT PART OF THE VOCABULARY THE COLUMN OTHERWISE USES. `Laboratory.RA` holds '-' 1684
    # times beside '+' 658 and '2+' 323: there '-' is a negative result, and the giveaway is that it occurs INSIDE
    # other values of the same column. Same for `U-PRO`, where '-' is the minus sign of '-15'. The empty string is
    # the one candidate this cannot ask about, and the one that never needs asking.
    #
    # ASKED WHETHER OR NOT REAL NULLS SIT BESIDE IT, because the version with NO nulls is the bigger one and the
    # worse one: 13 columns of `formula_1.results` are 64-77% empty string and hold not a single NULL, so
    # `WHERE fastestLapSpeed IS NULL` returns 0 and reads as a clean answer, and `AVG(fastestLapSpeed)` comes out
    # 45.44 against a true 200.71 because SQLite casts '' to 0. Nothing errors and nothing is empty.
    # A DATE WRITTEN DAY FIRST. '07/01/1985' does not sort and does not compare: `dob > '1985-01-01'` returns 328
    # drivers where 44 were born after that day. Taken only where some value proves the order -- a first part
    # above 12 is a day and cannot be a month -- because MM/DD and DD/MM look identical until one row says which.
    dd = [v for v in vals if _DDMM.match(v)]
    dayfirst = (len(dd) >= 0.9 * len(vals) and any(int(_DDMM.match(v).group(1)) > 12 for v in dd)
                and all(_DDMM.match(v) or _ISO.match(v) or not v.strip() for v in vals))

    # WHAT THE SUBSTRING GUARD WAS FOR, AND WHAT IT WAS ACTUALLY DOING. It exists so that '-' is not read
    # as missing in a column that also holds '--': there the short one is a code and the long one is another
    # code, and neither is a hole. But it tested the character against EVERY other value, so one hyphenated
    # name -- `Jean-Paul` -- was enough to suppress it, and `superhero.full_name` holds '-' in 125 of its 750
    # rows with nothing to mark them. Eleven per cent of sampled answers opened on a value like that, and
    # `certify` passed all of them because it counts SQL NULLs and these are stored strings.
    #
    # So the guard now asks what it meant to ask: is the longer value a CODE of the same kind -- punctuation,
    # no letters and no digits -- rather than a word that happens to contain the character. A documented value
    # is still never read as missing; that door is `said` and it is untouched.
    def _code(x):
        return bool(x) and not any(ch.isalnum() for ch in x)
    absent = tuple(sorted(v for v in seen if v.strip().lower() in MISSING_MARKERS and v not in said
                          and (not v or not any(v in o for o in seen if o != v and _code(o)))))
    return Stored(words, numeric, listed, absent, dayfirst)


# ---------------------------------------------------------------- the SQL, and the mirror that reads a row the same way
# Each builder below wraps the leaf's SITE so that the natural sentence is true of the rows the query returns, and
# `through` says what that wrapping makes of one stored value. They are defined side by side because they are one
# fact, and `through` reads it off the NODE rather than keeping a second copy — the binder decides whether a leaf
# holds by walking rows in Python and SQLite decides it again over the table, and the two have to agree.

_NUM_TEMPLATE = "CAST(__ARG0__ AS REAL)"


def as_number(expr):
    """`CRP > 10`, not `CRP > '10'`. Wrapped where the literal is chosen, so both sides mean the same thing.

    CARRIES A TEMPLATE SO IT IS OURS AND NOT THE SOURCE'S. A bare `Cast` is what P's own programs are full of, and
    `through` reading one of those as a wrapping turned every window value into a float -- so a leaf over a text
    column that P had already cast stopped holding for any row, and its whole attempt was refused for "no row of
    this join can satisfy the filter". The template is the only mark that distinguishes a wrapping we added from
    an expression that was always there."""
    from specbridge.pd.structures.algebra import Func
    return Func("CAST", (expr,), template=_NUM_TEMPLATE)


_BLANK_TEMPLATE = "NULLIF(__ARG0__, __ARG1__)"


def without(expr, blanks):
    """A written "missing" is missing. `NULLIF(rate, 'None') IS NULL` is true of both halves; `rate IS NULL` finds
    3230 of the 6869 rows a person means and gives no sign that it missed the rest. Templated for the same reason
    `as_number` is: P's own programs guard their divisions with `NULLIF(x, 0)`."""
    from specbridge.pd.structures.algebra import Const, Func
    for b in blanks: expr = Func("NULLIF", (expr, Const(b)), template=_BLANK_TEMPLATE)
    return expr


_LIST_TEMPLATE = "(',' || REPLACE(__ARG0__, ' ', '') || ',')"


def item(v):
    """The pattern matching exactly one item of such a cell."""
    return "%," + "".join(str(v).split()) + ",%"


def through(expr, v):
    """What the leaf's own expression makes of a stored value — the mirror of the three builders above."""
    from specbridge.pd.structures.algebra import Func
    if not isinstance(expr, Func) or not expr.template: return v
    if expr.template == _NUM_TEMPLATE:
        v = through(expr.args[0], v)
        try: return float(v)
        except (TypeError, ValueError): return None
    if expr.template == _BLANK_TEMPLATE:
        v = through(expr.args[0], v)
        return None if v is not None and v == expr.args[1].value else v
    if isinstance(expr, Func) and expr.template == _DATE_TEMPLATE:
        v = through(expr.args[0], v)
        if v is None: return None
        m = _DDMM.match(str(v))
        return m.group(3) + m.group(2) + m.group(1) if m else str(v).replace("-", "")
    if isinstance(expr, Func) and expr.template == _LIST_TEMPLATE:
        v = through(expr.args[0], v)
        return None if v is None else "," + "".join(str(v).split()) + ","
    return v


def wrapping(expr):
    """Is this one of the wrappings above — the thing that puts a stored value in the form the SQL needs?

    The renderer asks, because a wrapping is MACHINERY and a question must not mention it. Without this the list
    wrapper fell through to the generic clause and a question read "replace of expense description includes
    'Water'", which says our implementation out loud and names no column a reader could find.
    """
    from specbridge.pd.structures.algebra import Func
    return isinstance(expr, Func) and expr.template in (_LIST_TEMPLATE, _DATE_TEMPLATE)


def is_list(expr):
    """Is this the wrapping that makes a cell answer to one of its items? The renderer asks, so that it says the
    item and not the pattern the SQL matches it with."""
    from specbridge.pd.structures.algebra import Func
    return isinstance(expr, Func) and expr.template == _LIST_TEMPLATE


_DATE_TEMPLATE = ("(CASE WHEN SUBSTR(__ARG0__,3,1)='/' "
                  "THEN SUBSTR(__ARG0__,7)||SUBSTR(__ARG0__,4,2)||SUBSTR(__ARG0__,1,2) "
                  "ELSE REPLACE(__ARG0__,'-','') END)")


