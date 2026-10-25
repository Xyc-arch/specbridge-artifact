"""specbridge.pd.realize.world — D, AS THE BINDER SEES IT.

One type describes anything a program can read: a `Relation` with rows and columns, each column carrying what the
binder needs in order to CHOOSE it — affinity, how many values it takes, how often it is missing, what kind of thing
it is, and whether the schema uses it as a key.

A table is a Relation. **So is a step's output** — and that is the point of having one type. The old binder profiled
tables only, so the moment a filter, a threshold or a value mapping landed on a named intermediate result it was
choosing blind: 15% of all attempts were refused for `literal on a CTE column`, `value mapping over a step's output`
or `no table links to this step's output`. A step is a relation whose rows we can read; profiling its sample costs
one query we already run.
"""
from __future__ import annotations
import re, sqlite3
from dataclasses import dataclass, replace

SAMPLE = 5000                       # rows read to describe a relation: enough to rank columns, bounded on every D
_DATEISH = re.compile(r"^\d{4}[-/]\d{1,2}([-/]\d{1,2})?")
# ...ANYWHERE IN THE NAME, not only at its end: `mcmIdExtras` is an identifier and the corpus
# averaged it. A separator on both sides, so "Bid" and "Decode" are not caught.
# ...BUT "NUM" AND "NO" NAME A ROW ONLY AT THE END: as a prefix they mean "number of" (`NumTstTakr`, `NumGE1500`),
# and the anywhere rule made every such count a handle -- `satscores` lost all its measures.
_IDISH   = re.compile(r"(^|[_ ])(id|ids|code|codes|uuid|guid|key)([_ ]|$)|(^|[_ ])(no|num)$", re.I)
_YEARISH = re.compile(r"(^|[_ ])(year|yr|yyyy)([_ ]|$)", re.I)
_PLACEISH = re.compile(r"(^|[_ ])(lat|lon|lng|latitude|longitude)([_ ]|$)", re.I)


@dataclass(frozen=True)
class ColStat:
    name: str
    aff: str            # numeric | text | none
    distinct: int       # values it takes, over the sample
    nonnull: int        # rows where it is present, over the sample
    role: str           # id | date | json | cat | num | text | other
    key: bool = False   # the schema joins on it
    nonzero: int = 0    # rows where it is neither null nor zero — what a DENOMINATOR needs
    counts: bool = False  # a non-negative WHOLE quantity — what can sensibly sit under a division
    lo: float = None    # the range this column covers, over the sample — what a ported constant is redrawn against
    hi: float = None    # the NINE-TENTHS point, not the maximum: one superhero weighs 90,000,000 and another is
                        # 30,480 tall, so `1 minus (height cm divided by 31000)` was a whole database's formulas
                        # decided by one row.
    mid: float = None   # …and the MIDDLE value, not the mean, which that same row drags to 144,518, and not the
                        # midpoint of [lo, hi], which school enrolment (1 to 44,000, typically a few hundred)
                        # turns into "enrolment minus 22000".

    @property
    def idish(self):
        # A NAME IS SEPARATED BY WHATEVER THE SCHEMA SEPARATES IT BY. This tested `_` only, so `district_code` was
        # recognised as an identifier and `District Code` — the same thing, in a schema that writes names with spaces
        # — was handed to an arithmetic slot as a quantity. BIRD's california_schools writes every column that way.
        # AND A CAPITAL IS A SEPARATOR TOO. `statusId`, `raceId`, `qualifyId`, `constructorStandingsId` — Spider's
        # formula_1 writes every key in camelCase, and none of them declare a foreign key, so all of them read as
        # plain numbers. `results.statusId` reached an arithmetic slot and a question asked for "the average Status
        # code". The same sentence above, with the separator this schema uses.
        return self.key or bool(_IDISH.search(re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", self.name)))
    @property
    def yearish(self): return bool(_YEARISH.search(self.name))
    @property
    def placeish(self): return bool(_PLACEISH.search(self.name))

    @property
    def handle(self):
        """It names a row rather than measuring it. `role != "id" and not idish` was written out at five sites in
        `can`, which is five chances for them to drift apart — and they did, on WORD."""
        return self.idish or self.role == "id"

    @property
    def amount(self):
        """A number with a TRUE ZERO, so adding it up, scaling it and dividing by it mean something.

        `can(s, QUANTITY)` asked only for "numeric, and not an identifier", and a latitude is both of those. So the
        corpus computed "the total Latitude", "1 minus half of latitude" and "1 minus a hundredth of magnet" — and
        the rule that catches `latitude * longitude` could not see any of them, because it only looks at arithmetic
        whose two operands are both COLUMNS, and every one of these is a column against a constant.

        Three kinds of number measure nothing you can scale:
          - a handle numbers the row;
          - a latitude and a year sit on a scale whose zero is a convention, so differences mean something and
            ratios do not: half of latitude 40 is not half of anything;
          - a column with two values is a flag, and a hundredth of a flag is nothing.

        Comparing and ordering them is fine — "latitude is more than 35" and "ordered by year" are good questions —
        which is why this is a separate demand from NUMBER and ORDERABLE rather than a wider `idish`.
        """
        return (self.aff == "numeric" and not self.handle
                and not self.yearish and not self.placeish and self.distinct > 2)


@dataclass(frozen=True)
class Relation:
    name: str
    n: int
    cols: dict          # name -> ColStat
    table: bool = True  # a real table, or a step's output


def _aff(decl):
    d = (decl or "").upper()
    if any(x in d for x in ("INT", "REAL", "FLOA", "DOUB", "NUM", "DEC")): return "numeric"
    if any(x in d for x in ("CHAR", "TEXT", "CLOB")): return "text"
    return "none"


# A NUMBER WITH THIS MANY VALUES IS A FLAG, NOT A MEASUREMENT -- and TWO is the whole of it. At three,
# `Match.away_player_Y11` (a position on the pitch, sampled as 10, 11 and a stray) came back as a category
# and the corpus asked "for each away_player_Y11". A binary column is a flag BY CONSTRUCTION; a
# three-valued number is just a number that happens to be coarse, and nothing distinguishes a coordinate
# from a code at that width except what the database SAYS, which is what `coded` is for.
FLAG_VALUES = 2


def _role(aff, n, distinct, nonnull, sample, coded=False):
    """WHAT KIND OF THING THIS COLUMN IS, from its own distribution. Identity first (a column with a different value
    in every row names rows, it does not describe them), then the two kinds that are recognisable from the VALUES —
    a date, a document — then cardinality: a handful of values groups, many numbers measure.

    A NUMBER IS A MEASUREMENT UNLESS THE DATABASE SAYS ITS VALUES ARE CODES. Cardinality used to decide this
    first, so any number with under sixty values was a category -- and `player's reactions score` became one,
    which is how the corpus came to ask "the share of players whose attacking work rate is medium, counting
    only the ones where reactions score is 96". Nobody asks about a rating being exactly 96. A category's
    values are labels and its predicate is equality; a measurement's values are ordered and its predicate is
    a threshold, and no count of distinct values separates them -- `credits` takes four values and
    `Charter School (Y/N)` two, and only one of them is a number.

    So the database decides: `coded` is true when the documentation explains what the values MEAN ("0: N;
    1: Y"), and a two- or three-valued number is a flag either way. Everything else numeric measures.

    This is the one place that answers the question. `vouch.says_what_it_is`, the grouping and the filter all
    used to re-derive a piece of it with a distinct-count of their own, which is how the same rule ended up
    written in three places and still missed this case.
    """
    if not nonnull: return "other"
    # AMONG THE ROWS THAT HAVE ONE. `customers.phone` is 58 distinct values in 58 present rows of 59, and
    # compared to the row count it read as a category -- so a question filtered on a phone number.
    # A DATE IS A DATE BEFORE IT IS AN IDENTIFIER (2026-09-30): dates unique per row (one race per day) were read as ids, so
    # a table placed in time looked timeless and a stock could be summed across times.
    if sample and all(isinstance(v, str) and _DATEISH.match(v.strip()) for v in sample): return "date"
    if distinct == nonnull and nonnull > 20: return "id"
    if aff == "text" and sample and all(isinstance(v, str) and (
            (v.strip()[:1] in "{[<" and v.strip()[-1:] in "}]>") or len(v) > 120) for v in sample): return "json"
    if aff == "numeric" and not coded and distinct > FLAG_VALUES: return "num"
    if 2 <= distinct <= 60: return "cat"
    if aff == "numeric" and distinct > 5: return "num"
    if aff == "text": return "text"
    return "other"


class World:
    """A database, described once. Profiles are read-only and cached per connection: D does not change under us."""

    def __init__(self, con, name="", meta=None):
        """`meta` is the database's own documentation (`vocab.read`). Without it a number is a measurement
        unless it takes two or three values; with it, a number whose values the documentation EXPLAINS is a
        category however many it takes."""
        from specbridge.pd.realize.stored import meanings
        self.coded = set()
        for (t, c), v in (meta or {}).items():
            if meanings(str(v.get("values") or "")): self.coded.add((str(t).lower(), str(c).lower()))
        self.con, self.name, self.rel, self.fks = con, name, {}, []
        keys = set()
        tabs = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for t in tabs:
            for fk in con.execute(f'PRAGMA foreign_key_list("{t}")'):
                to = fk[4]
                # A KEY DECLARED WITHOUT A TARGET COLUMN POINTS AT THE PARENT'S PRIMARY KEY -- that is what
                # SQL means by it. `debit_card_specializing` declares `yearmonth(CustomerID) REFERENCES
                # customers`, and read as None the link was dropped and the database had no lookups at all.
                if to is None:
                    pk = [r[1] for r in con.execute(f'PRAGMA table_info("{fk[2]}")') if r[5]]
                    if len(pk) != 1: continue
                    to = pk[0]
                self.fks.append((t, fk[3], fk[2], to))
        low = {t.lower(): t for t in tabs}
        self.fks = [(low.get(c.lower(), c), cc, low.get(p.lower(), p), pc) for c, cc, p, pc in self.fks
                    if c.lower() in low and p.lower() in low]
        self.declared = set(self.fks)                    # links the schema declares; the rest below are inferred
        self.pk = {t: [r[1] for r in con.execute(f'PRAGMA table_info("{t}")') if r[5]] for t in tabs}
        # AN UNDECLARED KEY THE VALUES BEAR OUT IS A KEY. `debit_card_specializing` declares no foreign key
        # at all, and `transactions_1k.CustomerID` is every bit the key of `customers` that its name says:
        # unique there, and every value here is found there. Read off the values, like a containment: a
        # column named like another table's unique column, whose non-null values that column holds.
        declared = {(c, cc) for c, cc, _p, _pc in self.fks}
        cols_of = {t: [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')] for t in tabs}
        uniq = {}
        def unique(p, pc):
            if (p, pc) not in uniq:
                n, d = con.execute(f'SELECT COUNT("{pc}"), COUNT(DISTINCT "{pc}") FROM "{p}"').fetchone()
                uniq[(p, pc)] = n >= 2 and n == d
            return uniq[(p, pc)]
        for t in tabs:
            for c in cols_of[t]:
                if (t, c) in declared: continue
                for p in tabs:
                    if p == t: continue
                    pc = next((x for x in cols_of[p] if x.lower() == c.lower()), None)
                    if pc is None or not unique(p, pc) or unique(t, c): continue
                    try:
                        n, miss = con.execute(f'SELECT COUNT(*), SUM(CASE WHEN "{c}" NOT IN (SELECT "{pc}" FROM "{p}") THEN 1 ELSE 0 END) '
                                              f'FROM "{t}" WHERE "{c}" IS NOT NULL').fetchone()
                    except Exception:
                        continue
                    if n and (miss or 0) <= 0.01 * n:
                        self.fks.append((t, c, p, pc)); declared.add((t, c))
        for c, cc, p, pc in self.fks: keys |= {(c, cc), (p, pc)}
        for t in tabs:
            n, cols = self.describe(t, keys)
            self.rel[t] = Relation(t, n, cols)

    # ---- the schema's links, asked ONE way so no caller can spell them differently
    def describe(self, t, keys=()):
        """A relation's row count and the statistics of every column, read from the rows (a sample of
        SAMPLE); the same door for a base table and for a step registered as a view."""
        con = self.con
        n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        cols = {}
        for r in con.execute(f'PRAGMA table_info("{t}")'):
            c, aff = r[1], _aff(r[2])
            try:
                # THE RANGE COMES FREE. A ported formula's constants are calibrated to the SOURCE's
                # columns — "minus 20", "divided by 180" — and redrawing them needs to know what this column
                # actually covers. Asked in the query that was already being run, so a build pays nothing:
                # the range is a fact about the column, not about any one program's join.
                nd, nn, lo, hi = con.execute(
                    f'SELECT COUNT(DISTINCT "{c}"), COUNT("{c}"), MIN("{c}"), MAX("{c}") '
                    f'FROM (SELECT "{c}" FROM "{t}" LIMIT {SAMPLE})').fetchone()
                mid = None
                if aff == "numeric" and nn > 2:
                    # TWO POSITIONS IN THE COLUMN, NOT TWO EXTREMES. One ordering of the sample, read at the
                    # half and nine-tenths marks — a sort of at most 5,000 rows, once per numeric column per
                    # database, against constants that were otherwise decided by whichever row is strangest.
                    srt = (f'SELECT "{c}" FROM (SELECT "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL '
                           f'ORDER BY "{c}" LIMIT {SAMPLE}) LIMIT 1 OFFSET ')
                    mid, hi = con.execute(f'SELECT ({srt}{nn // 2}), ({srt}{nn * 9 // 10})').fetchone()
                smp = [x[0] for x in con.execute(
                    f'SELECT "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL LIMIT 5')] if nn else []
            except sqlite3.Error:
                continue
            try:
                nz = con.execute(f'SELECT COUNT(*) FROM (SELECT "{c}" FROM "{t}" LIMIT {SAMPLE}) '
                                 f'WHERE "{c}" IS NOT NULL AND "{c}" <> 0').fetchone()[0]
            except sqlite3.Error:
                nz = nn
            # CAN THIS COLUMN SIT UNDER A DIVISION — asked of the VALUES, not of the description.
            # A rate is a quantity over a quantity of something else: "score per test taker", "free meals per
            # pupil". Deciding it from the description alone recognised 6 columns of 243 and starved every
            # relation that needs a denominator. Whole, never negative, more than a handful of values, not an
            # identifier. That is weaker than "counts things" — a height in centimetres passes — but it is the
            # part that matters, because it EXCLUDES what makes a ratio meaningless: coordinates (negative and
            # fractional), percentages (fractional), flags (two values) and keys.
            cnt = False
            if aff == "numeric" and nd > 2:
                try:
                    bad = con.execute(
                        f'SELECT COUNT(*) FROM (SELECT "{c}" FROM "{t}" LIMIT {SAMPLE}) '
                        f'WHERE "{c}" IS NOT NULL AND ("{c}" < 0 OR "{c}" <> CAST("{c}" AS INTEGER))'
                    ).fetchone()[0]
                    cnt = bad == 0 and nn > 0
                except sqlite3.Error:
                    cnt = False
            num = lambda v: v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
            st = ColStat(c, aff, nd, nn,
                         _role(aff, min(n, SAMPLE), nd, nn, smp,
                               (t.lower(), c.lower()) in self.coded),
                         (t, c) in keys, nz, cnt,
                         num(lo), num(hi), num(mid))
            # THE SAMPLE CAN MAKE A NUMBER LOOK BINARY WHEN IT IS NOT. `Match.away_player_Y11` holds
            # four values and the sample saw two, so the flag rule fired and the corpus asked "for
            # each away_player_Y11" -- a position on the pitch. Every other use of `distinct` is a
            # rough size and a sample is fine for it; THIS one is a boundary, and being one value out
            # changes the kind. So it is counted exactly, over the whole column, and only in the rare
            # case where the sample already says two -- which is why it costs one query on almost no
            # columns rather than one per column.
            if st.role == "cat" and st.aff == "numeric" and (t.lower(), c.lower()) not in self.coded:
                try:
                    exact = con.execute('SELECT COUNT(DISTINCT "%s") FROM "%s"'
                                        % (c.replace('"', '""'), t.replace('"', '""'))).fetchone()[0]
                except Exception:
                    exact = nd
                if exact > FLAG_VALUES: st = replace(st, role="num", distinct=exact)
            cols[c] = replace(st, counts=st.counts and not st.idish and st.role != "id")
        return n, cols

    def add_view(self, name, links, unique):
        """A STEP AS A RELATION OF THE WORLD. `links` are (column of the view, base table, base column) for
        every column the step projects verbatim; an edge is declared from the base to the step where the
        step holds that column once (a base row meets one step row), and from the step to the base where
        the base does (the step's rows meet one base row). Keys are inferred from the rows, never assumed:
        a grouped step is unique on its keys, a listing step usually is not."""
        n, cols = self.describe(name)
        if not n or not cols: return False
        self.rel[name] = Relation(name, n, cols, table=False)
        for out, t, c in links:
            if unique(name, out): self.fks.append((t, c, name, out))
            if unique(t, c): self.fks.append((name, out, t, c))
        return True

    def drop(self, name):
        self.rel.pop(name, None)
        self.fks = [f for f in self.fks if f[0] != name and f[2] != name]

    def link(self, t, u):
        """The declared link joining `t` to `u` as (table, col, table, col), or None."""
        for c, cc, p, pc in self.fks:
            if (c, p) == (t, u): return (c, cc, p, pc)
        for c, cc, p, pc in self.fks:
            if (c, p) == (u, t): return (p, pc, c, cc)
        return None


    def neighbours(self, t):
        return {p for c, _cc, p, _pc in self.fks if c == t} | {c for c, _cc, p, _pc in self.fks if p == t}


