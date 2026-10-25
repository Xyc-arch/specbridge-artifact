"""DATABASE-CENTRED TASKS: every admissible instance of specbridge.pd.structures.dbfirst's families (docs/DBFIRST.md), frozen like any task, then
a sample drawn by the law (balanced over family and database).
    python -m specbridge.comm.construct.research.dbfirst build [n] [out]        -> out/p_gamma/dbfirst_tasks.jsonl (default n = 50)"""
import collections, json, sys
from specbridge.comm.common import db as DB
from specbridge.comm.construct.freeze import freeze
from specbridge.pd.structures import dbfirst as P


def build(n=50, out="out/p_gamma/dbfirst_tasks.jsonl", seed=20261004):
    cand, skipped = [], collections.Counter()
    for db in DB.DATABASES:
        try: S = P.Signature(db)
        except Exception as e: skipped["no database: %s" % type(e).__name__] += 1; continue
        k = collections.Counter()
        for fam, slots, sql in P.families(S):
            ok, why, _rows = P.matters(S, fam, slots, sql)
            if not ok: skipped["does not matter: " + why.split(":")[0][:40]] += 1; continue
            k[fam] += 1
            t, why = freeze("%s-%s%02d" % (db, fam, k[fam]), db, sql, "database-first family %s" % fam, family=fam, slots=slots)
            if t is None: k[fam] -= 1; skipped[why] += 1; continue
            cand.append(t)
    pick = P.law(cand, n, seed)
    with open(out, "w") as f:
        for t in pick: f.write(json.dumps(t, default=str) + "\n")
    print("admissible %d; selected %d: families %s; databases %s; not admissible %s" % (len(cand), len(pick), dict(collections.Counter(t["family"] for t in pick)),
          dict(collections.Counter(t["database"] for t in pick)), dict(skipped)))


if __name__ == "__main__":
    a = sys.argv[1:]
    build(int(a[1]) if len(a) > 1 else 50, *a[2:3])
