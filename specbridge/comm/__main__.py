"""THE PIPELINE, ONE DOOR. Every stage in order; each command names the module that does the work (docs/PIPELINE.md).

  SETUP, once per database and version (the expensive part; cached and resumable)
    python -m specbridge.comm setup <db> [<db> ...]
        1 catalogue     specbridge.pd.realize.semantic       meaning of every column: roles, units, additivity (one model review)
        2 feasibility   specbridge.comm.construct.feasibility what the grammar can build: exact cells, operations per cell, probes
        3 language      specbridge.comm.verbal.language      human-readable names for columns, tables, codes (one model call; by rule)

  A CORPUS, per request (from the explorer's saved request, or a JSON file)
    python -m specbridge.comm build <request.json>
        4 generate      specbridge.pd.structures.compose     SQL toward the requested cells, without duplicates, with variety
        5 check         (compose.check)           runs on the data; drops empty, constant, restating, oversized answers
        6 review        specbridge.comm.construct.rubric     coherent meaning and a determined answer, two reviewers, each task alone
        7 package       specbridge.comm.construct.freeze     explicit instructions, reference answer, tie groups, grader -- kept tasks only
        (all four in specbridge.comm.construct.corpus_build; report: requested vs delivered, diversity, cost, shortfalls)

  NATURAL QUESTIONS, per corpus
    python -m specbridge.comm natural <corpus dir>
        8 language      specbridge.comm.verbal.language      ensured for the corpus's own gaps first (cached)
        9 write         specbridge.comm.verbal.precise       one precise natural question per task (frozen writer), reviewed against
                                                  its requirements, one task per review call; status passed | revised |
                                                  not rendered -> corpus.jsonl, the DELIVERED corpus (natural question only)

  INSPECT
    python -m specbridge.comm compare <corpus A> <corpus B>   specbridge.comm.construct.corpus_compare
    python -m specbridge.comm status [<db> ...]               what each database has: catalogue, feasibility, language resource"""
import json, os, subprocess, sys


def run(mod, *args): return subprocess.run([sys.executable, "-m", mod, *args]).returncode


def setup(dbs):
    from specbridge.comm.construct.feasibility import run as feas
    from specbridge.comm.verbal.language import ensure, probe_sqls
    feas(dbs)                                       # catalogue (if missing) + feasibility, per database, in child processes
    for db in dbs:
        f = json.load(open("out/feasibility/%s.json" % db))
        if f.get("error"): print("%s: setup failed: %s" % (db, f["error"])); continue
        ensure(db, probe_sqls(db))


def status(dbs):
    from specbridge.pd.structures.compose import VERSION
    dbs = dbs or sorted(f[:-5] for f in os.listdir("out/feasibility"))
    print("%-24s %-10s %-12s %-10s %s" % ("database", "catalogue", "feasibility", "cells", "language resource"))
    for db in dbs:
        cat = os.path.exists("catalogues/%s.json" % db); fp = "out/feasibility/%s.json" % db
        f = json.load(open(fp)) if os.path.exists(fp) else {}
        lp = "catalogues/language/%s.json" % db; lang = json.load(open(lp)) if os.path.exists(lp) else None
        print("%-24s %-10s %-12s %-10s %s" % (db, "yes" if cat else "no", "error" if f.get("error") else ("yes" if f.get("grammar") == VERSION else "no"),
              len(f.get("cells") or {}), ("%d columns, %d tables, %d codes" % (len(lang["columns"]), len(lang["entities"]), sum(len(v) for v in lang["codes"].values()))) if lang else "none (catalogue labels)"))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    cmd, rest = a[0], a[1:]
    if cmd == "setup": setup(rest)
    elif cmd == "build": sys.exit(run("specbridge.comm.construct.corpus_build", *rest))
    elif cmd == "natural": sys.exit(run("specbridge.comm.verbal.precise", *rest))
    elif cmd == "compare": sys.exit(run("specbridge.comm.construct.corpus_compare", *rest))
    elif cmd == "status": status(rest)
    else: print(__doc__); sys.exit(2)
