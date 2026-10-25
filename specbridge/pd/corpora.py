"""specbridge.pd.corpora — WHICH DATABASES, AND WHERE THEY ARE. One fact, one door.

This was three doors. `TARGETS` -- the list of target databases and the path to each `.sqlite` -- lived
at the bottom of `specbridge/pd/port.py`, four hundred lines of PORTING machinery, and twelve modules imported that
file to reach a constant. `DIRS` -- the directory holding a database's own documentation -- lived in
`specbridge/pd/gaps.py`, an audit tool, and a second copy had grown in `specbridge/pd/traps.py`. Nothing in the dependency
graph said "these modules are about porting"; they were about needing a list of databases.

A shared fact inside an unrelated heavy module is the folder-scale version of the defect this codebase
kept turning up all day: one fact, several doors, and the copies drift.

    sqlite(db)   the database file
    docs(db)     the directory of description CSVs beside it, and the knowledge base if it ships one
    group(db)    which corpus it belongs to

WHY `unseen` IS ITS OWN GROUP and not folded into `bird`, which it shares a path with: nothing in `pd/`
may be developed against those five. The whole claim is that a database nobody has read yields sound gold
with no per-database tuning, and a target list holding only databases we tuned on cannot test it.
"""
from __future__ import annotations

# group -> (path template for the sqlite file, the databases in it)
TARGETS = {
    "bird":   ("dev_unzipped/dev_20240627/dev_databases/{d}/{d}.sqlite",
               ["superhero", "thrombosis_prediction", "california_schools", "student_club", "toxicology"]),
    "unseen": ("dev_unzipped/dev_20240627/dev_databases/{d}/{d}.sqlite",
               ["card_games", "codebase_community", "debit_card_specializing", "european_football_2",
                "financial"]),
    "spider": ("spider_data/spider_data/database/{d}/{d}.sqlite",
               ["formula_1", "soccer_1", "sakila_1", "store_1", "college_2"]),
}

# group -> the directory holding a database's own documentation. The same directory the sqlite sits in,
# which is why this was easy to write twice and get subtly different: one copy used "%s" and one "{d}".
DIRS = {"bird": "dev_unzipped/dev_20240627/dev_databases/%s",
        "unseen": "dev_unzipped/dev_20240627/dev_databases/%s",
        "spider": "spider_data/spider_data/database/%s"}

SOURCE = "livesql_dbs/{d}/{d}.sqlite"      # R, the corpus P is fitted from -- never a target


# WHERE A DATABASE MAY LIVE, whether or not anyone listed it. `TARGETS` is the fifteen we MEASURE on;
# these are the roots any database can be FOUND under, and the difference matters: the whole claim of
# this generator is that it works on a database nobody has read, and a resolver that only answers for
# a hand-written list cannot even be pointed at one. 166 databases sit under the spider root and five
# are named above.
ROOTS = ["spider_data/spider_data/database/%s", "dev_unzipped/dev_20240627/dev_databases/%s", "livesql_dbs/%s"]   # 2026-10-01: LiveSQL databases as targets (their gold is never read)


def found(db):
    """The directory of any database under the known roots, or None. Not restricted to TARGETS."""
    import os
    for r in ROOTS:
        d = r % db
        if os.path.exists("%s/%s.sqlite" % (d, db)): return d
    return None


def unlisted(root=0):
    """Every database under a root that is NOT a target -- the ones nothing here was developed against."""
    import os
    d = ROOTS[root] % ""
    d = d.rstrip("/")
    named = set(every())
    return sorted(x for x in os.listdir(d) if x not in named and found(x))


def group(db):
    """Which corpus this database belongs to, or None if it is not a target."""
    return next((t for t, (_p, ns) in TARGETS.items() if db in ns), None)


def is_path(db):
    """A target may be given as the path to its `.sqlite` -- the door for a database nobody has listed."""
    import os
    return str(db).endswith(".sqlite") and os.path.exists(db)


def name(db):
    """The database's name: a listed target's own, or a path's file name without its extension."""
    import os
    return os.path.basename(db)[:-7] if is_path(db) else db


def sqlite(db):
    """The path to this database's file -- a path given as such, a named target, or any database under the roots."""
    if is_path(db): return db
    t = group(db)
    if t: return TARGETS[t][0].format(d=db)
    d = found(db)
    return "%s/%s.sqlite" % (d, db) if d else None


def docs(db):
    """The directory holding what this database says about itself, whether or not it says anything --
    for a path, the directory the file sits in."""
    import os
    if is_path(db): return os.path.dirname(os.path.abspath(db))
    t = group(db)
    return (DIRS[t] % db) if t else found(db)


def every():
    """Every target database, in a stable order: the five developed against, then the ten not."""
    return [d for t in ("bird", "unseen", "spider") for d in TARGETS[t][1]]
