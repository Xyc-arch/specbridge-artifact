"""specbridge.pd.realize.vocab — WHAT D SAYS ABOUT ITSELF.

A database ships its own description of its columns, and that is not gold: it is documentation, the thing anyone
reading the schema would read. From it, and from the rows, this derives the relationships that decide whether a
computation MEANS anything here.

    NumGE1500   "Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500"  -> count of "test takers"
    NumTstTakr  "Number of Test Takers in this school"                                       -> count of "test takers"
    AvgScrMath  "average scores in Math"                                                     -> average of "scores"

Two columns are SIBLINGS when they measure the same kind of thing the same way — comparing or differencing them says
something. One is PART OF another when its values sit inside the other's in every row: their ratio is a share, which
is the most common thing a real question asks for. `AvgScrMath / NumTstTakr` is neither — a score over a headcount,
arithmetic nobody asks for — and it is what the binder picks without this.

The description gives the MEANING and the data gives the DIRECTION. No similarity between phrases can say which of two
near-identical ones contains the other; containment in the rows can, and it is verified rather than guessed.
"""
from __future__ import annotations
import csv, json, os, re, sqlite3, urllib.request

_KIND = [("count", r"^\s*(the\s+)?(number|count|total number|num)\b|^\s*num\b"),
         ("average", r"^\s*(the\s+)?(average|avg|mean)\b"),
         ("share", r"^\s*(the\s+)?(percent|percentage|rate|ratio|share|proportion)\b|%"),
         ("total", r"^\s*(the\s+)?(total|sum)\b"),
         ("date", r"\b(date|year|time|day|month)\b")]
from specbridge.pd.realize.words import stop_pattern
_STOP_RE = stop_pattern()   # one list; see specbridge.pd.realize.words.STOPWORDS
_NO_USE = re.compile(r"unuseful|not useful|no use", re.I)


from specbridge.pd.realize.words import plain as _norm    # one door; see specbridge.pd.realize.words.plain


def read(db_dir):
    """{(table, column): {desc, values, kind, head, useless}} from D's own description files.

    AND FROM `written.json` BESIDE THEM, where `describe_missing` puts what it wrote. Five of the fifteen
    target databases -- every Spider one -- describe NOTHING: 0 of 94 columns, 0 of 84, 0 of 89. So
    `says_what_it_is` rejects every column, `pd.derive` builds no quantity at all, and those databases
    produce thin repetitive corpora that saturate at two dozen questions. The tool to fix it has existed
    the whole time and had nowhere to put its output, so nobody ran it.

    A written description is a fact about the database read off its schema and five of its values --
    checkable against it, and involving no question, no gold and no source dataset. It is marked
    `written` so anything that wants only what the DATABASE says can tell them apart.
    """
    out = {}
    d = os.path.join(db_dir, "database_description")
    written = os.path.join(db_dir, "written.json")
    if os.path.exists(written):
        try:
            for k, v in json.load(open(written)).items():
                t, c = k.split("|", 1)
                out[(t, c)] = v
        except Exception:
            pass
    if not os.path.isdir(d): return out
    for f in os.listdir(d):
        if not f.endswith(".csv"): continue
        table = f[:-4]
        try:
            rows = list(csv.DictReader(open(os.path.join(d, f), encoding="utf-8-sig", errors="replace")))
        except OSError:
            continue
        for r in rows:
            col = (r.get("original_column_name") or "").strip()
            if not col: continue
            desc = (r.get("column_description") or r.get("column_name") or "").strip()
            short = (r.get("column_name") or "").strip()
            vals = (r.get("value_description") or "").strip()
            if not vals:                      # a row with more fields than its header (or a trailing unnamed one): spilled over
                spill = ([r.get("")] if r.get("") else []) + list(r.get(None) or [])
                vals = " ".join(x for x in spill if x).strip()
            kind, head = _parse(desc or col)
            # THE DATABASE'S OWN DESCRIPTION WINS -- UNLESS IT SAYS NOTHING. `california_schools` describes
            # `CDSCode` as "CDSCode", `describe_missing` writes a real phrase for it, and this loop then
            # put the empty one back on top of it -- so every build asked the model for the same 45
            # descriptions again, 42 seconds a database, and `written.json` was rewritten unchanged. The
            # test is `describe_missing`'s own: a description that is only the column's name is missing.
            have = out.get((table, col))
            if have and have.get("written") and \
                    desc.strip().lower().replace(" ", "") in ("", col.lower().replace("_", "").replace(" ", "")):
                if vals and not have.get("values"): have["values"] = vals
                continue
            # ...AND A ROW THAT GIVES NO SHORT NAME DOES NOT ERASE ONE. The source's meanings written beside the
            # database carry the short name its own format gives ("wallet turnover rate"); a description file
            # generated from the same meanings with an empty `column_name` was putting the handle back.
            if not short and have and have.get("short"): short = have["short"]
            out[(table, col)] = {"desc": desc, "short": short, "values": vals, "kind": kind, "head": head,
                                 "useless": bool(_NO_USE.search(vals or "") or _NO_USE.search(desc or ""))}
    # A DESCRIPTION MAY NOT BE THE NAME OF ANOTHER COLUMN OF THE SAME TABLE.
    #
    # BIRD describes `frpm."County Name"` as "County Code", and `frpm."County Code"` is a real column of that same
    # table holding '01'. So the question said "counting only the ones where County Code is one of 'Humboldt',
    # 'Inyo'" — a reader does exactly the right thing, reads the column the words name, and gets codes instead of
    # names. The sentence names a real column and the wrong one, which no check on OUR wording can see, because
    # our wording is faithful.
    #
    # THE SAME TABLE, and only there. `schools.County` reads as "County name" while `frpm."County Name"` exists
    # too — the same county, reached through the join, so a reader landing on either gets the same answer. It is
    # when both columns sit in one table that the choice changes the value. Five of the six matches in these ten
    # databases are the harmless kind; refusing those would cost the good names for nothing.
    by_table = {}
    for (t, c) in out: by_table.setdefault(t, set()).add(_norm(c))
    for (t, c), x in out.items():
        for field in ("short", "desc"):
            n = _norm(x.get(field) or "")
            if n and n != _norm(c) and n in by_table.get(t, ()): x[field] = ""
    return out


def _parse(desc):
    """(what kind of measure this is, what it is a measure OF) — the head phrase, stripped of function words."""
    low = desc.lower()
    kind = next((k for k, pat in _KIND if re.search(pat, low)), "")
    head = low
    for _k, pat in _KIND: head = re.sub(pat, " ", head)
    head = re.sub(r"\(.*?\)", " ", head)                      # "(1st-12nd grade)", "(Y/N)": a qualifier, not the noun
    head = _STOP_RE.sub(" ", head)
    head = re.sub(r"[^a-z0-9 ]+", " ", head)
    return kind, " ".join([w for w in head.split() if len(w) > 2][:3])


# WHAT KIND OF QUANTITY A COLUMN HOLDS. "Numeric" is not enough to decide whether two columns may be combined:
# `charter school (Y/N) x longitude` is arithmetic between a flag and a coordinate, and reached delivered questions
# because both are stored as numbers. The kind comes from the description's own words first, and from the shape of
# the data where the words say nothing.
_KINDW = [("id", r"\bidentifier\b|\bid\b|\bids\b|\buuid\b|\bcode\b|\bcodes\b"),   # the database says it names, not measures
          ("flag", r"\(y/n\)|\byes/no\b|\b0: |\bboolean\b|whether\b"),
          ("coordinate", r"\blatitude\b|\blongitude\b|angular distance|\bdegrees\b|prime meridian|equator"),
          ("share", r"percent|percentage|\brate\b|\bratio\b|proportion|\bshare\b|%"),
          # COUNT BEFORE MONEY: "Free or Reduced Price Meal Count" is a count that mentions a price.
          ("count", r"\bcount\b|\bnumber\b|\benrollment\b|\btakers\b|\btally\b"),
          ("money", r"\bdollar|\bcost\b|\bprice\b|\bamount\b|\bbudget|\bspent\b|\bpaid\b|usd|\beuro"),
          ("score", r"\bscores?\b|\bratings?\b|\bindex\b|\bgrade\b"),
          ("measure", r"\bheight\b|\bweight\b|\blength\b|\bdistance\b|\bage\b|\bduration\b|\bin (cm|kg|m|metres|meters)\b"),
          ("year", r"\byear\b|\byyyy\b")]


def kind_of(desc, stat):
    """The kind of quantity, from the words the database uses and then from its values."""
    if stat is not None and (stat.idish or stat.role == "id"): return "id"
    d = (desc or "").lower()
    for k, pat in _KINDW:
        if re.search(pat, d): return k
    if stat is None: return ""
    if stat.distinct <= 2: return "flag"
    if stat.aff == "numeric" and stat.distinct > 20: return "measure"
    return ""


def relations(con, world, meta):
    """The relationships, VERIFIED ON THE ROWS. A claim the descriptions suggest and the data refuses is dropped —
    which is the point of asking the data at all."""
    part, sib = [], []
    for t, rel in world.rel.items():
        # A FLAG IS NOT A PART OF ANYTHING. `Charter School (Y/N)` is stored as 0/1, so it never exceeds any count
        # in its table and the containment test called it a part of all six of them. Two values is a yes/no, whatever
        # its affinity, and the question "what share of the enrolment is charter-school-ness" does not exist.
        nums = [s.name for s in rel.cols.values()
                if s.aff == "numeric" and not s.idish and s.role != "id" and s.nonnull > 0 and s.distinct > 2]
        for i, a in enumerate(nums):
            ma = meta.get((t, a), {})
            for b in nums[i + 1:]:
                mb = meta.get((t, b), {})
                ha, hb = (ma.get("head") or "").split(), (mb.get("head") or "").split()
                same = bool(set(ha) & set(hb))                 # the same noun, however the two phrases qualify it
                if same and ma.get("kind") and ma.get("kind") == mb.get("kind"):
                    sib.append((t, a, b))
                # THE DATA GIVES DIRECTION; IT CANNOT GIVE KIND. Containment alone made `Percent (%) Eligible Free`
                # a part of `Enrollment` (a percentage is simply a smaller number) and paired 172 lab assays in
                # thrombosis_prediction whose only relation is that one is measured in smaller units than the other.
                # A part and its whole must be the same KIND of thing counted over the same NOUN — which the
                # descriptions say — and the rows then say which of the two contains the other.
                if not (same and ma.get("kind") in ("count", "total") and mb.get("kind") in ("count", "total")):
                    continue
                for x, y in ((a, b), (b, a)):                  # part inside whole: never exceeds, sometimes less
                    try:
                        over, under, n = con.execute(
                            f'SELECT SUM("{x}" > "{y}"), SUM("{x}" < "{y}"), COUNT(*) FROM "{t}" '
                            f'WHERE "{x}" IS NOT NULL AND "{y}" IS NOT NULL').fetchone()
                    except sqlite3.Error:
                        continue
                    if n and n >= 20 and not over and under and under > 0.05 * n:
                        part.append((t, x, y, round(under / n, 2)))
    return {"part_of": part, "siblings": sib}


def build(db_dir, con, world, cache=None):
    meta = read(db_dir)
    out = {"columns": {f"{t}.{c}": v for (t, c), v in meta.items()}, **relations(con, world, meta)}
    if cache:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        json.dump(out, open(cache, "w"), indent=1)
    return out


from specbridge.pd.models import DESCRIBER as MODEL  # one door; see specbridge.pd.models


def _ask(prompt, n=20):
    """See `specbridge.pd.ask`. Uncached: `describe_missing` asks once per column and the result is written out."""
    from specbridge.pd.ask import ask as _a
    return _a(prompt, MODEL, n=n)


def ensure_described(db_dir, con, meta=None, log=None, ask=True):
    """THE ONE CALL THAT MAKES AN UNREAD DATABASE USABLE, and the only per-database step there is.

    `read` returns what the database says about itself. A Spider database says NOTHING -- 0 of 94
    columns, 0 of 84 -- so every column comes back unnamed, `pd.say` refuses every draw it is handed,
    and the build yields zero rows. That is the guarantee working (it will not invent a name into a
    question), but it means the generator cannot be pointed at an undocumented database at all.

    `describe_missing` has always been the fix and nothing called it: it was run by hand for the ten
    listed databases, its output left beside them in `written.json`, and a database nobody had run it
    for produced nothing. A step that must be done by hand for each database is exactly the
    per-database tuning `.claude/skills/scales-to-any-database` says must not exist -- so it is done
    HERE, once, the first time anyone asks for this database's vocabulary, and cached beside it.

    Returns the meta, described. Writes `written.json` only when it learned something new, and only
    when the directory can be written to.
    """
    meta = dict(meta if meta is not None else read(db_dir))
    if not ask: return meta
    meta, added = describe_missing(db_dir, con, meta, log=log)
    if not added: return meta
    try:
        out = {"%s|%s" % (t, c): v for (t, c), v in meta.items() if (v or {}).get("written")}
        with open(os.path.join(db_dir, "written.json"), "w") as fh:
            json.dump(out, fh, indent=1)
        if log: log("   wrote %d descriptions to %s/written.json" % (added, db_dir))
    except OSError as e:
        if log: log("   (could not save descriptions: %s)" % e)
    return meta


def describe_missing(db_dir, con, meta=None, log=None):
    """WHERE THE DATABASE DOES NOT DESCRIBE ITSELF, DESCRIBE IT — from the schema and the data, never from gold.

    BIRD's databases document between 14% and 100% of their columns, and an undescribed column leaves the question
    reading its own schema name aloud, which is the opposite of how real questions ask. The model is handed the table,
    its column list, the column, and five of its values — and nothing else. One call per undescribed column, once per
    database, cached beside the rest of the vocabulary.

    A description written this way is a fact about the database, so it is gold-free in the sense that matters: no
    question, no gold query and no source dataset is involved.

    ASKED A TABLE AT A TIME, NOT A COLUMN AT A TIME. One call per column is fine for the fifteen
    databases someone chose and is the reason this could not be pointed at an arbitrary one:
    `baseball_1` has 352 columns, so a database nobody had read cost 352 model calls before it produced
    a single question, and a sweep of 25 databases stalled on the fifth. A table is the natural unit --
    the model sees its columns together, which is strictly more context than it had per column -- and it
    is ~12x fewer calls. Chunked, because a 22-column table's answer runs long and a truncated answer
    must not silently lose the tail.

    A DESCRIPTION IS ONLY ACCEPTED FOR A COLUMN WE ASKED ABOUT. The answer is lines of `column: phrase`,
    matched back against the exact set that went out; anything else the model returns is dropped, so a
    misaligned or invented row cannot become a column's name. A column the batch does not answer for is
    asked about on its own, which is the old path, kept for the tail."""
    meta = dict(meta if meta is not None else read(db_dir))
    added = 0
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]
        want = []
        for c in cols:
            k = (t, c)
            d = (meta.get(k) or meta.get((t.lower(), c.lower())) or {}).get("desc", "")
            if d and d.strip().lower().replace(" ", "") != c.lower().replace("_", "").replace(" ", ""):
                continue                                      # it already says more than the column's own name
            try:
                vals = [str(r[0])[:22] for r in con.execute(
                    f'SELECT DISTINCT "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL LIMIT 5')]
            except sqlite3.Error:
                continue
            if vals: want.append((c, vals))
        for i in range(0, len(want), BATCH):
            chunk = want[i:i + BATCH]
            got = _describe_batch(t, cols, chunk)
            for c, vals in chunk:
                a = got.get(c.lower())
                if not a:                                     # the tail the batch did not answer for
                    a = _ask(f'A table named "{t}" has columns: {", ".join(cols)}.\n'
                             f'One of them, "{c}", contains values like: {", ".join(vals)}.\n\n'
                             f"What does that column hold? Answer in one short phrase, nothing else.")
                    a = str(a).strip().strip('".').split("\n")[0]
                if not a: continue
                kind, head = _parse(a)
                meta[(t, c)] = {"desc": a, "values": "", "kind": kind, "head": head,
                                "useless": False, "written": True}
                added += 1
                if log: log(f"   {t}.{c}: {a[:60]}")
    return meta, added


BATCH = 12          # columns per call; a longer answer is where a model starts dropping the tail


def _describe_batch(table, cols, chunk):
    """One call for several columns of one table. {column.lower(): phrase} for the ones it answered."""
    body = "\n".join('  "%s": %s' % (c, ", ".join(v)) for c, v in chunk)
    a = _ask('A table named "%s" has columns: %s.\n\n'
             "Some of them contain values like this:\n%s\n\n"
             "What does each of those columns hold? Give one line per column, in the form\n"
             "  column: short phrase\n"
             "Use the column names exactly as written above. No other text." % (table, ", ".join(cols), body),
             n=40 + 12 * len(chunk))
    asked = {c.lower() for c, _v in chunk}
    out = {}
    for line in str(a or "").splitlines():
        name, sep, phrase = line.partition(":")
        if not sep: continue
        name = name.strip().strip('"\'`*-[] ').lower()
        phrase = phrase.strip().strip('".').split("\n")[0]
        # ONLY A COLUMN WE ASKED ABOUT, and only once: a model that repeats itself or renames a column
        # must not be able to put a description on something we never sent.
        if name in asked and phrase and name not in out: out[name] = phrase
    return out


# ---------------------------------------------------------------- numbers the database STATES about a column
# A DRAWN NUMBER IS A QUANTITY OF NOTHING. A threshold taken from a column's own quantiles always lands in range
# and always means nothing: `C-reactive protein > 0.47` is a fact about our sampling, not about C-reactive protein.
# Some databases say what the number should be -- `thrombosis_prediction` documents a reference range on 33 of its
# 64 columns ("Normal range: N < 60") -- and a threshold taken from THERE is a question a person would ask.
#
# Only the forms these files actually use, read off them rather than imagined: `N < 60`, `N > 8.0`, `40 < N < 400`,
# `6.0 < N < 8.5`. Anything else is left alone, because a number appearing in prose is usually a digit count
# ("the 7-digit NCES identifier") or a unit, and using those would be worse than drawing.
_RANGE = re.compile(r"(?:(\d+(?:\.\d+)?)\s*<\s*)?N\s*([<>]=?)\s*(\d+(?:\.\d+)?)", re.I)


def stated_bounds(text):
    """The numbers this column's own documentation gives as bounds on it, as (comparator, value)."""
    out = []
    for lo, op, hi in _RANGE.findall(str(text or "")):
        out.append((op, float(hi)))
        if lo: out.append((">" if "<" in op else "<", float(lo)))
    return out
