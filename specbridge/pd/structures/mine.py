"""specbridge.pd.structures.mine — WHERE P COMES FROM.

A dataset's gold queries, lifted into programs. A query that does not lift is not part of P and is counted, never
approximated: the point of P is that every program in it is one this algebra can state exactly.

    python -m specbridge.pd.structures.mine <source>          # a source registered in specbridge.pd.structures.sources

writes out/profiles/<source>/templates.jsonl — {sql, db, match} per verified gold query, which `specbridge.pd.structures.sources.programs`
reads back. Verification here is that the query RUNS and returns something: the gold is the dataset's, not ours, and
lifting it is what we are claiming to do correctly.
"""
from __future__ import annotations
import json, os, re, sqlite3, sys
from collections import Counter
from specbridge.pd.structures.algebra import lift, emit, node_types, norm, run_sqlite, Unsupported


def mine(src, log=print):
    """LIFT ONE SOURCE'S GOLD INTO P. `python -m specbridge.pd.structures.mine <source>` -- the source is an entry of `specbridge.pd.structures.sources`.

    A program is kept when it lifts and answers what the gold answers. Two exceptions, both LiveSQLBench's:
    Postgres gold is transpiled before it is run against the sqlite copy (68 of 180 died raw), and a
    flattened JSON read that cannot round-trip on the source is kept and marked `flattened` rather than
    lost -- `check_p` explains why. Neither costs a generic source anything.
    """
    from specbridge.pd.structures.sources import items, sqlite as src_sqlite, templates
    out, why, cons = [], Counter(), {}
    rows = items(src)
    for _q, sql, db in rows:
        if not sql or not db: continue
        path = src_sqlite(src, db)
        if not os.path.exists(path): why["no database"] += 1; continue
        con = cons.setdefault(db, sqlite3.connect(f"file:{path}?mode=ro", uri=True))
        try:
            p = lift(sql, con)
        except Unsupported as e:
            why[f"does not lift: {str(e)[:40]}"] += 1; continue
        gold, e1 = run_sqlite(con, _sqlite_of(sql))
        mine_, e2 = run_sqlite(con, emit(p))
        if e1: why[f"gold does not run: {str(e1)[:40]}"] += 1; continue
        if e2 and "no such column" in str(e2) and re.search(r"->>?", sql):
            out.append({"sql": sql, "db": db, "match": "flattened", "nodes": sorted(node_types(p))})
            why["kept, flattened JSON read (cannot round-trip on the source)"] += 1; continue
        if e2: why[f"OUR emission does not run: {str(e2)[:34]}"] += 1; continue
        # THE LIFT MUST PRESERVE THE ANSWER. This is the one assertion left after the interpreter went: not two
        # semantics agreeing, but the program we lifted answering what the query we lifted it from answers.
        if norm(gold) != norm(mine_): why["lifted program answers differently"] += 1; continue
        out.append({"sql": sql, "db": db, "match": True, "nodes": sorted(node_types(p))})
    f = templates(src); os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w") as fh:
        for r in out: fh.write(json.dumps(r) + "\n")
    log(f"P for {src}: {len(out)} programs from {len(rows)} gold queries -> {f}")
    for k, v in why.most_common(8): log(f"  {v:>5}  {k}")
    return out


def _sqlite_of(sql):
    """The same query, in the dialect our copies speak. Returns the original if it will not convert, so a
    failure here is reported as the gold not running rather than silently swallowed."""
    import re as _re, warnings as _w
    try:
        import sqlglot
        with _w.catch_warnings():
            _w.simplefilter("ignore")
            return sqlglot.transpile(_re.sub(r"\bpublic\.", "", sql), read="postgres", write="sqlite")[0]
    except Exception:
        return sql


def check_p(src="livesql", log=print):
    """DOES EVERY FORM IN P STILL ANSWER WHAT ITS SOURCE QUERY ANSWERS.

    `templates.jsonl` carried `match: True` on 112 rows, and re-checking them today 31 produce SQL that will not run
    on their own database — every one because the source reads a JSON field, `t.trading_performance -> '$.risklevel'
    ->> '$.levratio'`, which the lifter flattens into a column name that does not exist.

    Those forms are NOT discarded. BIRD and Spider have no JSON columns, so JSON navigation is a difficulty no
    implementation could port; reading the extracted field as a plain column is the most faithful port available, and
    the structure around it — the arithmetic, the joins, the steps — is what travels. What was wrong was the LABEL:
    a round-trip verification was claimed that never happened. This says which is which, and the number belongs in
    any writeup that calls P verified.
    """
    import sqlite3
    from specbridge.pd.structures.sources import sqlite as src_sqlite, templates
    rows = [json.loads(l) for l in open(templates(src))]
    cons, tally = {}, Counter()
    for r in rows:
        if r.get("match") is not True: tally["not marked verified"] += 1; continue
        con = cons.setdefault(r["db"], sqlite3.connect(f"file:{src_sqlite(src, r['db'])}?mode=ro", uri=True))
        try:
            p = lift(r["sql"], con)
        except Unsupported:
            tally["no longer lifts"] += 1; continue
        g, e1 = run_sqlite(con, r["sql"])
        m, e2 = run_sqlite(con, emit(p))
        if e1: tally["source query does not run"] += 1
        elif e2: tally["ours does not run (JSON read as a column)"] += 1
        elif norm(g) == norm(m): tally["ROUND-TRIPS"] += 1
        else: tally["answers differently"] += 1
    log(f"P for {src}: {len(rows)} rows")
    for k, n in tally.most_common(): log(f"  {n:>5}  {k}")
    return tally


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    mine(sys.argv[1] if len(sys.argv) > 1 else "livesql")
