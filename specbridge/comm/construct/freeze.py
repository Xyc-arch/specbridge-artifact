"""FREEZE a query into a task: lift into P's algebra (semantic compatibility), explicit V (specbridge.pd.spec.render), the grader (refuses
an answer it cannot decide), the full reference answer with tie groups at a cut, 1-2,000 rows, structural features."""
import hashlib, os, shutil
from specbridge.comm.common import db as DB

SNAP_DIR = "out/gamma_pool/snapshot"


def snapshot(db):
    """The frozen copy of a database (created once) and its sha256."""
    known = DB.snapshots()
    if db in known: return known[db]
    if db in _SHA: return _SHA[db]
    os.makedirs(SNAP_DIR, exist_ok=True); dst = "%s/%s.sqlite" % (SNAP_DIR, db)
    if not os.path.exists(dst): shutil.copyfile(DB.catalogue(db).path, dst)
    _SHA[db] = (dst, hashlib.sha256(open(dst, "rb").read()).hexdigest()); return _SHA[db]


_SHA = {}


def freeze(tid, db, sql, source, **extra):
    """(task, None) or (None, why it was not frozen)."""
    from specbridge.pd.structures.algebra import emit, lift
    from specbridge.pd.realize.fidelity import features
    from specbridge.pd.structures.grammar import inline_lets
    from specbridge.pd.spec import render as R
    cat = DB.catalogue(db)
    try: p = lift(sql, cat.con); s = R.spec(p, cat)
    except Exception as e: return None, "not in the language: %s" % type(e).__name__
    g = R.grader(s)
    if "declined" in g: return None, "grader refused"
    snap, sha = snapshot(db); con = DB.connect(snap, shared=True)
    rows, groups, pool = R.reference(p, con, lambda c, q: (lambda st, res, _c: (st, res))(*DB.execute(c, q, ms=60000)))
    if not (1 <= len(rows) <= 2000): return None, "answer has %d rows" % len(rows)
    try: f = features(inline_lets(p))
    except Exception: f = features(p)
    return dict({"id": tid, "database": db, "snapshot": snap, "snapshot_sha256": sha, "source": source, "instruction": R.english(s),
                 "reference_sql": emit(p), "grader": g, "reference_answer": [list(r) for r in rows], "tie_groups": groups,
                 "last_pool": [list(r) for r in pool] if pool else None,
                 "features": {"arith_depth": f["arith_depth"], "step": int(f["step_chain"] > 0), "window": f["has_window"],
                              "case": f["has_case"], "joins": f["joins"], "aggregates": f["aggregates"], "size": f["size"]}}, **extra), None


def candidate(tid, db, sql, source, **extra):
    """(candidate, None) or (None, why): the SQL lifted into the language, re-emitted, with its explicit specification and
    structural features -- what a reviewer needs. No execution, no saved answer, no grader (those are `freeze`)."""
    from specbridge.pd.structures.algebra import emit, lift
    from specbridge.pd.realize.fidelity import features
    from specbridge.pd.structures.grammar import inline_lets
    from specbridge.pd.spec import render as R
    cat = DB.catalogue(db)
    try: p = lift(sql, cat.con); s = R.spec(p, cat)
    except Exception as e: return None, "not in the language: %s" % type(e).__name__
    snap, sha = snapshot(db)
    try: f = features(inline_lets(p))
    except Exception: f = features(p)
    return dict({"id": tid, "database": db, "snapshot": snap, "snapshot_sha256": sha, "source": source, "instruction": R.english(s),
                 "reference_sql": emit(p), "features": {"arith_depth": f["arith_depth"], "step": int(f["step_chain"] > 0), "window": f["has_window"],
                 "case": f["has_case"], "joins": f["joins"], "aggregates": f["aggregates"], "size": f["size"]}}, **extra), None


# ---------------------------------------------------------------- cache of completed packaging
CODE = ["specbridge/comm/construct/freeze.py", "specbridge/pd/spec/render.py", "specbridge/pd/structures/algebra.py", "specbridge/pd/realize/fidelity.py", "specbridge/pd/structures/grammar.py",
        "specbridge/pd/realize/catalogue.py", "specbridge/pd/realize/semantic.py", "specbridge/pd/realize/world.py"]
_VER = {}


def version(db):
    """What a packaged task depends on besides its SQL: the snapshot, the catalogue and its corrections, and the code that
    lifts, renders, grades and executes. A change to any of them makes a new key, so a rerun redoes exactly the changed work."""
    if db not in _VER:
        h = hashlib.sha256(snapshot(db)[1].encode())
        for f in CODE + ["catalogues/%s.json" % db, "catalogues/corrections/%s.json" % db]:
            if os.path.exists(f): h.update(f.encode()); h.update(open(f, "rb").read())
        _VER[db] = h.hexdigest()[:16]
    return _VER[db]


def packaged(tid, db, sql, source, level="spec", cache="out/cache/package", **extra):
    """`candidate` (level "spec") or `freeze` (level "full"), cached on disk by (SQL, level, version(db))."""
    import json
    key = hashlib.sha256("\0".join([db, sql, level, version(db)]).encode()).hexdigest()[:24]
    f = "%s/%s/%s.json" % (cache, db, key)
    if os.path.exists(f):
        r = json.load(open(f)); t = r["task"]
        return (dict(t, id=tid, source=source, **extra) if t else None), r["why"]
    t, why = (freeze if level == "full" else candidate)(tid, db, sql, source)
    os.makedirs(os.path.dirname(f), exist_ok=True); json.dump({"task": t, "why": why}, open(f, "w"), default=str)
    return (dict(t, **extra) if t else None), why
