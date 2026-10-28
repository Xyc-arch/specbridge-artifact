"""DISCLOSE THE READINGS A REQUEST LEAVES OPEN (Section 7.1 and Figure 17 of the paper).

One call lists the readings of the request, each rewritten as a request with exactly one reading. With one reading, one more call
answers it and nothing else runs. Otherwise each reading is answered in its own call. All answers are executed, readings with
identical results are merged, and the first answer is returned with the others as alternatives.

Merging uses equal results on the CURRENT database: two readings that tie today may differ after the data changes.

    from methods.disclose import disclose
    out = disclose(question, schema_text, "path/to/db.sqlite", ask)     # ask(prompt) -> model reply text
    out["main"], out["alternatives"], out["readings"], out["calls"]

This is the frozen version run on the AMBROSIA final test (specbridge.comm.transfer.ambrosia.run_final, arm "ours")."""
import collections, json, os, re, sys
try: import sqlean as sqlite3                # SQLite 3.42, as for the paper (requirements.txt)
except ImportError: import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from prompts import DETECT
from third_party import dtp_prompts as DTP          # the SQL prompt: DtP's released user_message_sql

MAX_READINGS = 4


def _json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try: return json.loads(m.group(0))
    except Exception: return None


def parse_sql(text):
    """AMBROSIA's parser of SQL in a reply (fenced code, statements split on ';' or blank lines, or one SELECT)."""
    if "```" in text: st = [code for _, code in re.findall(r"```(\w+)\s+(.*?)```", text, re.DOTALL)]
    elif "\n\n" in text or ";" in text:
        st = [x.strip() for x in re.split(r";|\n\n", text) if x.strip() and x.strip().lower().startswith(("select", "with"))]
    elif text.strip().lower().startswith("select"): st = [text.strip()]
    else: st = []
    st = [s.replace("\\", "") for s in st]
    return st or ([text.strip()] if text.strip().lower().startswith(("select", "with")) else [])


def _key(x): return (0, "") if x is None else (1, float(x)) if isinstance(x, (int, float)) else (2, str(x))


def same(a, b, order_by=False):
    """AMBROSIA's result comparison: multisets of values, or row by row when the query orders its rows."""
    if not a: return False
    if order_by:
        if len(b) != len(a) or any(len(r) != len(b[0]) for r in b + a): return False
        return all(tuple(sorted(g, key=_key)) == tuple(sorted(p, key=_key)) for g, p in zip(b, a))
    return collections.Counter(i for r in b for i in r) == collections.Counter(i for r in a for i in r)


def _run(db, q):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try: return con.execute(q).fetchall()
    except Exception: return None
    finally: con.close()


def merge(db, queries):
    """Drop queries that fail; keep one query per distinct result."""
    keep, res = [], []
    for q in queries:
        r = _run(db, q)
        if r is None: continue
        o = "order by" in q.lower()
        if any(same(r, x, o) and same(x, r, o) for x in res): continue
        keep.append(q); res.append(r)
    return keep


def disclose(question, schema, db, ask):
    calls = 1
    reads = [x for x in ((_json(ask(DETECT % (schema, question))) or {}).get("readings") or []) if isinstance(x, str) and x.strip()] or [question]
    reads = reads[:1] if len(reads) == 1 else reads[:MAX_READINGS]
    queries = []
    for r in reads:
        calls += 1; queries += parse_sql(ask(DTP.user_message_sql.format(schema, r)))[:1]
    kept = merge(db, queries)
    return {"readings": reads, "queries": queries, "main": kept[0] if kept else None, "alternatives": kept[1:], "calls": calls}
