"""STEP-CHECKED SQL, ZERO-CALL GATES (2026-10-13). Before building the method, measure on SAVED answers (no model calls):
    gate 1  execution failures, and the share a dialect rewrite table makes run (and right)
    gate 2  per detector, the firing rate on WRONG vs RIGHT answers (a useful detector fires far more on wrong ones)
    gate 3  the share of wrong answers that ONE rule edit (specbridge.comm.diagnose.rules) makes right -- an upper bound for edit fixes
Detectors: empty step (each CTE run alone, and the final result), mostly-NULL aggregate input (> 50% NULL in a column some
aggregate reads), NULL in the output of a query that divides, "top/first N" asked but not N rows, answer-changing decision point.
Data: BIRD hold + hold2 plain answers (libctx), Spider 2.0 Sonnet SQL-only answers (rgv sample3 first sample; ask plain2).
    python -m specbridge.comm.diagnose.stepcheck gates  -> out/stepcheck/GATES.md"""
import collections, json, os, re, sqlite3, sys, time
import sqlglot
from sqlglot import exp
from specbridge.comm.diagnose import rules as RU

OUT = "out/stepcheck"
REWRITES = [(r"::\s*(numeric|decimal|float8?|double precision|real)\b", " * 1.0"), (r"::\s*(int|integer|bigint)\b", ""), (r"::\s*(text|varchar)\b", ""),
            (r"\bILIKE\b", "LIKE"), (r"EXTRACT\s*\(\s*YEAR\s+FROM\s+([^)]+)\)", r"CAST(strftime('%Y', \1) AS INTEGER)"),
            (r"EXTRACT\s*\(\s*MONTH\s+FROM\s+([^)]+)\)", r"CAST(strftime('%m', \1) AS INTEGER)"),
            (r"DATE_TRUNC\s*\(\s*'month'\s*,\s*([^)]+)\)", r"strftime('%Y-%m-01', \1)"), (r"\bTRUE\b", "1"), (r"\bFALSE\b", "0"),
            (r"\bCURRENT_DATE\b", "date('now')"), (r"\bNULLS\s+(FIRST|LAST)\b", "")]


def run(db, sql, timeout=20):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); t0 = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - t0 > timeout else 0, 100000)
    try: return con.execute(sql).fetchall(), None
    except Exception as e: return None, str(e)
    finally: con.close()


def rewrite(sql):
    out = sql
    for a, b in REWRITES: out = re.sub(a, b, out, flags=re.I)
    return out


def detectors(db, sql, question, rows):
    """Names of the detectors that fire on an executable query."""
    fired = set(); q = RU.parse(sql)
    if rows is not None and len(rows) == 0: fired.add("empty_step")
    if q is not None:
        w = q.args.get("with") or q.args.get("with_")
        if w:                                                                  # each CTE alone
            ctes = w.expressions
            for i, c in enumerate(ctes):
                body = "WITH " + ", ".join(x.sql(dialect="sqlite") for x in ctes[:i + 1]) + " SELECT 1 FROM %s LIMIT 1" % c.alias
                r, _e = run(db, body, 10)
                if r is not None and len(r) == 0: fired.add("empty_step"); break
        cols = {c.name for a in q.find_all(exp.AggFunc) for c in a.find_all(exp.Column)}
        if cols:
            con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
            try:
                for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                    tc = {r[1] for r in con.execute('PRAGMA table_info("%s")' % t)}
                    for c in cols & tc:
                        n, nn = con.execute('SELECT COUNT(*), SUM("%s" IS NULL) FROM "%s"' % (c, t)).fetchone()
                        if n and (nn or 0) / n > 0.5: fired.add("mostly_null_input")
            except Exception: pass
            finally: con.close()
        if list(q.find_all(exp.Div)) and rows and any(v is None for r in rows for v in r): fired.add("null_from_division")
    m = re.search(r"\b(?:top|first|highest|lowest|best|worst)\s+(\d+|three|five|ten|two)\b", question or "", re.I)
    if m and rows is not None:
        n = {"two": 2, "three": 3, "five": 5, "ten": 10}.get(m.group(1).lower()) or int(m.group(1)) if not m.group(1).isdigit() else int(m.group(1))
        if len(rows) != n: fired.add("top_n_count")
    return fired


def answers():
    """(source, db path, question, sql, check(rows) -> bool) for every saved answer."""
    from specbridge.comm.diagnose import libctx as LC
    from specbridge.comm.common import grade as G
    from specbridge.comm.transfer import spider2 as S2, rgv as RG, ask as AK
    out = []
    for sp in ("hold", "hold2"):
        for t in LC.split(sp):
            for m in ("haiku", "gpt-6-luna", "gpt-6-sol", "sonnet"):
                f = "%s/%s.json" % (LC._out(sp, 1, "plain", m), t["id"])
                if os.path.exists(f):
                    o = json.load(open(f))
                    if o.get("final"): out.append(("BIRD", t["snapshot"], t["instruction"], o["final"], (lambda ref: lambda rows: rows is not None and bool(G.bird_ex(ref, rows)))(t["reference_answer"])))
    T = S2.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S2.GOLD + "/spider2lite_eval.jsonl")}
    def chk(iid):
        G2, io = S2.golds(iid, E)
        def c(rows, sql=None): return bool(S2.matches(S2.run_sql(T[iid]["db"], sql), G2, io)) if sql else False
        return c
    for iid in RG.pick()[0]:
        f = RG._f("sample3", "sonnet", iid, 0)
        if os.path.exists(f):
            a = json.load(open(f))["answers"]
            if a and a[0].get("sql"): out.append(("Spider 2.0", "%s/%s.sqlite" % (S2.DBDIR, T[iid]["db"]), T[iid]["question"], a[0]["sql"], ("spider", chk(iid))))
    for iid in AK.tasks_strict():
        f = AK._f("plain2", "sonnet", iid)
        if os.path.exists(f):
            o = json.load(open(f))
            if o.get("sql"): out.append(("Spider 2.0", "%s/%s.sqlite" % (S2.DBDIR, T[iid]["db"]), T[iid]["question"], o["sql"], ("spider", chk(iid))))
    return out


def correct(check, rows, sql):
    if isinstance(check, tuple): return check[1](rows, sql)
    return check(rows)


def gates():
    A = answers(); R = collections.defaultdict(lambda: collections.Counter()); F = collections.defaultdict(lambda: collections.Counter())
    for src, db, q, sql, check in A:
        r = R[src]; rows, err = run(db, sql); r["answers"] += 1
        if rows is None:
            r["fails"] += 1; rw = rewrite(sql)
            if rw != sql:
                r2, _e = run(db, rw)
                if r2 is not None: r["rewrite_runs"] += 1; r["rewrite_right"] += correct(check, r2, rw)
            continue
        ok = correct(check, rows, sql); r["right" if ok else "wrong"] += 1
        fired = detectors(db, sql, q, rows)
        for st in RU.sites(sql):                                                # answer-changing decision point
            if st[0] == "dedup": continue
            e = RU.edit(sql, st); r2, _e = run(db, e) if e else (None, None)
            if r2 is not None and set(map(tuple, r2)) != set(map(tuple, rows)):
                fired.add("decision_point")
                if not ok and correct(check, r2, e): r["one_edit_fixes"] += 1; break
        for d in fired: F[(src, d)]["right" if ok else "wrong"] += 1
    L = ["# Step-checked SQL: zero-call gates on saved answers (`specbridge.comm.diagnose.stepcheck`)\n",
         "| source | answers | run fails | fails made to run by rewrite table | ... and then right | right | wrong | wrong answers fixed by one rule edit |", "|---|---|---|---|---|---|---|---|"]
    for src, r in R.items():
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d (%.0f%%) |" % (src, r["answers"], r["fails"], r["rewrite_runs"], r["rewrite_right"], r["right"], r["wrong"], r["one_edit_fixes"], 100 * r["one_edit_fixes"] / max(1, r["wrong"])))
    L += ["", "Detector firing rate on wrong vs right answers (executable answers only):\n", "| source | detector | fires on wrong | fires on right | ratio |", "|---|---|---|---|---|"]
    for (src, d), c in sorted(F.items()):
        w, rt = c["wrong"] / max(1, R[src]["wrong"]), c["right"] / max(1, R[src]["right"])
        L.append("| %s | %s | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %.1f |" % (src, d, c["wrong"], R[src]["wrong"], 100 * w, c["right"], R[src]["right"], 100 * rt, w / rt if rt else float("inf")))
    os.makedirs(OUT, exist_ok=True); open(OUT + "/GATES.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"gates": gates}[sys.argv[1]]()
