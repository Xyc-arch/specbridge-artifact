"""DATABASES. Frozen snapshots, read-only execution with a time limit, the context a model is given (schema + the
documentation the database ships), result comparison, explicit V of any SQL, and edit/witness helpers."""
import collections, json, math, os, re, sqlite3, time

POOL = "out/gamma_pool/tasks.jsonl"                       # frozen snapshots (one per database) with their sha256
DOCS_DIR = "out/gamma_run/DOCS"
DATABASES = ["california_schools", "financial", "superhero", "thrombosis_prediction", "toxicology", "store_1"]


_SNAPS = {}


def snapshots():
    """{database: (snapshot path, sha256)}; read once per process (the pool file changes only when a snapshot is added)."""
    key = os.path.getmtime(POOL)
    if _SNAPS.get("mtime") != key:
        out = {}
        for l in open(POOL):
            t = json.loads(l); out.setdefault(t["database"], (t["snapshot"], t["snapshot_sha256"]))
        _SNAPS.clear(); _SNAPS.update(mtime=key, out=out)
    return dict(_SNAPS["out"])


_CONS = {}


def connect(snapshot, shared=False):
    """A read-only connection. shared=True reuses one per snapshot in this process (callers that run many queries)."""
    if not shared: return sqlite3.connect("file:%s?mode=ro" % snapshot, uri=True)
    if snapshot not in _CONS: _CONS[snapshot] = sqlite3.connect("file:%s?mode=ro" % snapshot, uri=True, check_same_thread=False)
    return _CONS[snapshot]


def execute(con, sql, ms=20000):
    """("ok", rows, columns) or ("error", message, []). Every row is returned: a cap would truncate answers."""
    t0 = time.time()
    con.set_progress_handler(lambda: 1 if (time.time() - t0) * 1000 > ms else 0, 10000)
    try:
        cur = con.execute(sql)
        return "ok", cur.fetchall(), [c[0] for c in cur.description or []]
    except Exception as e:
        return "error", str(e)[:200], []


def rows(con, sql, ms=600000):
    """The rows as lists, or None when the query does not run."""
    if not sql: return None
    st, res, _ = execute(con, sql, ms)
    return [list(r) for r in res] if st == "ok" else None


def schema(snapshot):
    return "\n".join(r[0] + ";" for r in connect(snapshot).execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND sql IS NOT NULL"))


def docs(db):
    """Every column description and value description the database ships (nothing written by us); cached in DOCS_DIR."""
    f = "%s/%s.txt" % (DOCS_DIR, db)
    if not os.path.exists(f):
        from specbridge.pd.realize.vocab import read
        text = "(this database ships no documentation)"
        from specbridge.pd.corpora import found
        for d in [found(db)] if found(db) else []:
            if os.path.isdir(os.path.join(d, "database_description")):
                lines = []
                for (t, c), x in sorted(read(d).items()):
                    if x.get("written"): continue
                    s = "%s.%s: %s" % (t, c, (x.get("desc") or "").strip())
                    if (x.get("values") or "").strip(): s += " | values: " + " ".join(x["values"].split())
                    lines.append(s)
                text = "\n".join(lines); break
        os.makedirs(DOCS_DIR, exist_ok=True); open(f, "w").write(text)
    return open(f).read() + verified(db)


def verified(db):
    """The confirmed catalogue corrections (catalogues/corrections/<db>.json), each with its evidence: the same facts the
    generator reads, shown to every reviewer, so a wrong shipped description cannot mislead one review and not another."""
    f = "catalogues/corrections/%s.json" % db
    if not os.path.exists(f): return ""
    return "\n\nVERIFIED ON THE DATA (these override the descriptions above):\n" + "\n".join(
        "%s: %s" % (k, (v.get("evidence") or {}).get("note", "")) for k, v in json.load(open(f)).items())


def context(t):
    """(schema, documentation) for a task or {"snapshot", "database"}."""
    return schema(t["snapshot"]), docs(t["database"])


def witness(a_rows, b_rows):
    """How two answers differ: rows only in A / only in B (multiset), and changed values for rows sharing the first column."""
    ca, cb = collections.Counter(map(repr, a_rows)), collections.Counter(map(repr, b_rows))
    oa, ob = list((ca - cb).elements()), list((cb - ca).elements())
    ka = {repr(r[0]): r for r in a_rows if r}
    chg = [(ka[repr(r[0])], r) for r in b_rows if r and repr(r[0]) in ka and repr(ka[repr(r[0])]) != repr(r)]
    return {"rows_A": len(a_rows), "rows_B": len(b_rows), "only_in_A": len(oa), "only_in_B": len(ob), "examples_only_in_A": oa[:3],
            "examples_only_in_B": ob[:3], "changed_value_examples": [{"A": list(x), "B": list(y)} for x, y in chg[:3]]}


from specbridge.comm.common.grade import canon      # comparison lives in specbridge.comm.common.grade


# ---------------------------------------------------------------- explicit V and edits
_CATS = {}


def catalogue(db):
    """One catalogue per database per process. (Was `_CATS.setdefault(db, Catalogue(db))`, which built the catalogue -- about
    300 profiling queries -- on EVERY call, since the default is evaluated first: 97% of the time of freezing a task.)"""
    from specbridge.pd.realize.catalogue import Catalogue
    if db not in _CATS: _CATS[db] = Catalogue(db)
    return _CATS[db]


def explicit(sql, db, conventions=True):
    """Explicit V of an SQL query (specbridge.pd.spec.render): the text, or None when V refuses it. conventions=False drops the shared
    Conventions paragraph (for prompts that show a specification beside other material)."""
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.spec import render as R
    try: text = R.english(R.spec(lift(sql, catalogue(db).con), catalogue(db)))
    except Exception: return None
    return text if conventions else text.split("\nConventions")[0]


def apply_edits(text, edits):
    """Apply exact text edits [{"from", "to"}]: each "from" must occur exactly once and edits must not overlap.
    Returns (new text, [(start, end)]) or (None, None)."""
    spans = []
    for e in edits or []:
        f = e.get("from") or ""
        if not f or text.count(f) != 1: return None, None
        i = text.index(f); spans.append((i, i + len(f), e.get("to", "")))
    spans.sort()
    if any(a[1] > b[0] for a, b in zip(spans, spans[1:])): return None, None
    out, pos = [], 0
    for s, e, to in spans: out += [text[pos:s], to]; pos = e
    return "".join(out) + text[pos:], [(s, e) for s, e, _ in spans]


CLAUSES = ("expressions", "from", "joins", "where", "group", "having", "order", "limit", "distinct")


def changed_clauses(a, b):
    """Which top-level SQL clauses differ between two queries (a locator for reviewers, not proof)."""
    import sqlglot
    try: x, y = sqlglot.parse_one(a, read="sqlite"), sqlglot.parse_one(b, read="sqlite")
    except Exception: return ["unparsed"]
    s = lambda v: "" if v is None else (" ".join(e.sql() for e in v) if isinstance(v, list) else v.sql())
    return [k for k in CLAUSES if s(x.args.get(k)) != s(y.args.get(k))]
