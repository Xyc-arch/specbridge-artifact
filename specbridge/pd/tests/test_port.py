"""specbridge.pd.tests.test_port -- regression cases for defects found porting P to databases (2026-09-30).   python -m specbridge.pd.tests.test_port [--replay]
  1  a table or column name containing '%' crashed the aggregate-FILTER probe (ValueError, catalogue.py) -- 2 of 100
     attempts on california_schools ("Percent (%) Eligible FRPM (K-12)")
  2  a window function's own aggregate (AVG(f(AVG(x))), legal only inside its window) was reused as a bare ORDER BY key:
     SQLite "misuse of aggregate function AVG()" on an emitted program (out/crossdb/california_schools.jsonl, attempt 163)
--replay also regenerates california_schools attempts with the committed seed and requires no bug verdict and no emitted
program that fails to execute."""
import sys, warnings
warnings.filterwarnings("ignore")


def run(replay=False):
    from specbridge.pd.structures.algebra import lift, nested_aggregate
    from specbridge.pd.realize.catalogue import Catalogue, filter_probe
    from specbridge.pd.realize.verify import judge
    fails = []
    def check(name, ok):
        print("  %-100s %s" % (name, "ok" if ok else "FAILED"))
        if not ok: fails.append(name)
    cal = Catalogue("california_schools")
    # ---- 1: the probe with a '%' in a name
    q = filter_probe("", 'FROM "frpm" AS "frpm"', ['"frpm"."Percent (%) Eligible FRPM (K-12)" > 0.5'], '"frpm"."Enrollment (K-12)" > 10')
    ok = True
    try: cal.con.execute(q).fetchall()
    except Exception: ok = False
    check("1  the FILTER probe runs with a '%' in a column name", ok and "(%)" in q)
    # ---- 2: nested aggregates
    legal = 'SELECT "County Code", AVG(power(AVG("FRPM Count (K-12)"), 1.5)) OVER (PARTITION BY "County Code") FROM frpm GROUP BY "County Code"'
    bad = ('SELECT "County Code", AVG(power(AVG("FRPM Count (K-12)"), 1.5)) OVER (PARTITION BY "County Code" ORDER BY AVG(power(AVG("FRPM Count (K-12)"), 1.5))) '
           'FROM frpm GROUP BY "County Code"')
    runs = lambda sql: (lambda: (cal.con.execute(sql).fetchall(), True))
    def sqlite_ok(sql):
        try: cal.con.execute(sql).fetchall(); return True
        except Exception: return False
    check("2a SQLite accepts a window over an aggregate, and rejects the same aggregate nested outside it", sqlite_ok(legal) and not sqlite_ok(bad))
    pl = lift(legal, cal.con); pb = lift(bad, cal.con)
    check("2b nested_aggregate: the window over an aggregate is not nested; the bare ORDER BY key is", not nested_aggregate(pl.select) and nested_aggregate(pb.select))
    w = pl.select[1][0]                                   # the legal window: its function is only valid inside it
    check("2c the window's own aggregate is nested on its own (so the checker refuses to reuse it outside a window)", nested_aggregate(w.fn) and not nested_aggregate(w))
    check("2d the verifier refuses the program with the nested key", judge(pb, None) == "nested aggregate")
    if replay:
        import json, os, tempfile
        from specbridge.pd.realize.crossdb import one
        d = tempfile.mkdtemp(); one("california_schools", 170, 11, d)
        rows = [json.loads(l) for l in open(os.path.join(d, "california_schools.jsonl"))][1:]
        bugs = [r for r in rows if str(r.get("verdict", "")).startswith("bug")]
        broken = [r for r in rows if r.get("verdict") == "valid" and r.get("status") != "ok"]
        check("replay: 170 california_schools attempts (seed 11): no bug verdict (%d) and no emitted program that fails (%d)" % (len(bugs), len(broken)), not bugs and not broken)
    print("%d failed" % len(fails)); return fails


if __name__ == "__main__":
    sys.exit(1 if run("--replay" in sys.argv) else 0)
