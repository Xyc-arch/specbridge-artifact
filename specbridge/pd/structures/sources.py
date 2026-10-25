"""specbridge.pd.structures.sources — WHERE GOLD COMES FROM. One registry, and the two things fitted from it.

A gold source is a set of databases and the (question, SQL) pairs written against them. Two things are
fitted from one: the TREE LAW `specbridge.pd.structures.grammar` reads its programs (P -- which shapes a question takes and how
often), and the ENGLISH `pd.frames` reads its questions (how a question opens and lays itself out). Both
were wired to LiveSQLBench by path in five modules; here the path is written once, and a new source is a
new entry, mined with one command:

    python -m specbridge.pd.structures.mine <source>          # lifts its gold into out/profiles/<source>/templates.jsonl

and then any build can be fitted on it: `python -m specbridge.pd.corpus 60 out/x --law <source>`.

THE GOLD-FREE RULE. Synthetic data for a database never uses that database's own gold: a source's databases
can never be targets of a build fitted on it. `covers(src)` is that set. (2026-10-01: its caller `pd.bind.build` was
deleted and the current route, `pd.structures.compose`, fits nothing on a source's gold, so nothing calls it now.)

A generic source is a JSON or JSONL file of records with a SQL field, a database field and a question
field, over databases at `dbs.format(d=name)`. That describes BIRD and Spider exactly; LiveSQLBench keeps
its SQL in a second file and its questions in a third, so it has a reader of its own (`specbridge.pd.structures.livesql`).
"""
from __future__ import annotations
import functools, json, os, re, sqlite3

SOURCES = {
    # THE SOURCE P WAS BUILT FROM. Postgres gold over sqlite copies; only the "Query" category lifts.
    "livesql":    {"dbs": "livesql_dbs/{d}/{d}.sqlite", "reader": "livesql",
                   "kb": "livesqlbench_data/{d}/{d}_kb.jsonl"},          # the knowledge base beside its gold
    # BIRD's dev set and Spider's dev set, as EXAMPLES of the generic form. Their databases are targets
    # of this project, so a build on one of them must not be fitted here: `covers` says so.
    "bird_dev":   {"dbs": "dev_unzipped/dev_20240627/dev_databases/{d}/{d}.sqlite",
                   "gold": "dev_unzipped/dev_20240627/dev.json",
                   "sql": "SQL", "db": "db_id", "question": "question"},
    "spider_dev": {"dbs": "spider_data/spider_data/database/{d}/{d}.sqlite",
                   "gold": "spider_data/spider_data/dev.json",
                   "sql": "query", "db": "db_id", "question": "question"},
}


def names():
    return list(SOURCES)


def _records(gold):
    return json.load(open(gold)) if gold.endswith(".json") else [json.loads(l) for l in open(gold)]


def items(src):
    """(question, sql, db) for every gold record of this source, straight from its files."""
    s = SOURCES[src]
    if s.get("reader") == "livesql":
        from specbridge.pd.structures.livesql import load
        cat = {r["instance_id"]: r.get("category")
               for r in (json.loads(l) for l in open("livesqlbench_data/livesqlbench_data_sqlite.jsonl"))}
        return [(it["question"], it["sql"], it["db"]) for it in load() if cat.get(it["id"]) == "Query"]
    return [(r.get(s["question"], ""), r.get(s["sql"], ""), r.get(s["db"], "")) for r in _records(s["gold"])]


def sqlite(src, db):
    return SOURCES[src]["dbs"].format(d=db)


def kb_file(db):
    """A source's knowledge-base file for one of its databases, if a registered source ships one."""
    for s in SOURCES.values():
        p = s.get("kb", "").format(d=db) if s.get("kb") else ""
        if p and os.path.exists(p): return p
    return None


def any_sqlite(db):
    """The file of a database any registered source holds -- for a validation corpus built on a source."""
    for s in SOURCES.values():
        p = s["dbs"].format(d=db)
        if os.path.exists(p): return p
    return None


def covers(src):
    """The databases this source's gold was written against -- never a target of a build fitted on it."""
    return {db for _q, _s, db in items(src) if db}


def templates(src):
    return "out/profiles/%s/templates.jsonl" % src


def programs(src):
    """R, lifted: every mined gold query of this source as a program. Mine it first (`python -m specbridge.pd.structures.mine`)."""
    return [p for p, _db in _programs(src)]


def meanings(src, db):
    """What the source documents about a database's columns: (table, column) -> description. LiveSQLBench
    ships a meaning file per database; a generic source has the descriptions beside its sqlite file, read
    by `specbridge.pd.realize.vocab.read` -- the same door a target's descriptions come through."""
    if SOURCES[src].get("reader") == "livesql":
        from specbridge.pd.structures.livesql import meanings as m
        return m(db)
    from specbridge.pd.realize.vocab import read
    meta = read(os.path.dirname(sqlite(src, db)))
    return {k: v.get("desc", "") for k, v in meta.items()} if isinstance(meta, dict) else {}


def written(src, db_dir, db):
    """The source's descriptions written beside a database it covers, in the form the namer reads
    (`desc` and a short name) -- the source's own door for its documentation format."""
    if SOURCES[src].get("reader") == "livesql":
        from specbridge.pd.structures.livesql import written as w
        return w(db_dir, db)
    return None


def typers(src):
    """One `specbridge.pd.structures.meaning.Typer` per program of the source, over that program's database documentation."""
    from specbridge.pd.structures.meaning import Typer
    ms = {}
    return [Typer(ms.setdefault(db, meanings(src, db)), p) for p, db in _programs(src)]


@functools.lru_cache(maxsize=None)
def _programs(src):
    from specbridge.pd.structures.algebra import lift
    f = templates(src)
    if not os.path.exists(f):
        raise SystemExit("%s is not mined yet: python -m specbridge.pd.structures.mine %s" % (src, src))
    out, cons = [], {}
    held = os.environ.get("PD_HOLDOUT", "")           # PD_HOLDOUT=<db>: that database's gold is left out of the fit
    for r in (json.loads(l) for l in open(f)):
        if held and r["db"] == held: continue
        con = cons.setdefault(r["db"], sqlite3.connect("file:%s?mode=ro" % sqlite(src, r["db"]), uri=True))
        try: out.append((lift(r["sql"], con), r["db"]))
        except Exception: pass
    for c in cons.values(): c.close()
    return tuple(out)


def questions(src):
    """The questions of this source, as written."""
    return [q for q, _s, _d in items(src) if q]


def law(srcs):
    """The tree law fitted on one source or several -- `("livesql", "bird_dev")` pools their programs."""
    from specbridge.pd.structures.grammar import fit
    srcs = (srcs,) if isinstance(srcs, str) else tuple(srcs)
    ps = [p for s in srcs for p in programs(s)]
    ts = [t for s in srcs for t in typers(s)]
    return fit(ps, ts)
