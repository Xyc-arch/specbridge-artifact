"""SMALL POPULATIONS: a comparison or a top-3 cut over too few rows is trivial; a value on one row is not.
Both doors are tested on the same tiny data: the grammar's move check (compose.step_check) and the check read off the SQL
(integrity.trivial). Cases: 0, 1 and several rows left after a filter; groups that are all single rows vs not; a top-3 cut
that keeps every row vs one that drops some; and legitimate one-row results (an overall total, a ratio of two totals).
    python -m specbridge.pd.tests.test_small_populations"""
import sqlite3, sys
from specbridge.pd.structures.compose import step_check
from specbridge.pd.structures.integrity import trivial
from specbridge.pd.structures.algebra import lift

con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE t (id INTEGER PRIMARY KEY, g TEXT, v REAL, w REAL);
INSERT INTO t VALUES (1,'a',10,1),(2,'a',20,2),(3,'b',30,3),(4,'b',50,4),(5,'c',70,5);
""")
# the stage every case filters: per-row values, and a filter threshold that leaves n rows
S1 = lambda thr: [("s1", 'SELECT "t"."id" AS "e", "t"."g" AS "g", "t"."v" AS "m1" FROM "t" AS "t" WHERE "t"."v" > %s' % thr)]
GAP_ALL = lambda thr: ('WITH "s1" AS (SELECT "t"."id" AS "e", "t"."g" AS "g", "t"."v" AS "m1" FROM "t" AS "t" WHERE "t"."v" > %s), '
                       '"s2" AS (SELECT AVG("s1"."m1") AS "v" FROM "s1" AS "s1") '
                       'SELECT "s1"."e" AS "e", ("s1"."m1" - "s2"."v") AS "m2" FROM "s1" AS "s1" INNER JOIN "s2" AS "s2" ON NOT ("s2"."v" IS NULL)' % thr)
GAP_G = lambda thr: ('WITH "s1" AS (SELECT "t"."id" AS "e", "t"."g" AS "g", "t"."v" AS "m1" FROM "t" AS "t" WHERE "t"."v" > %s), '
                     '"s2" AS (SELECT "s1"."g" AS "g", AVG("s1"."m1") AS "v" FROM "s1" AS "s1" GROUP BY "s1"."g") '
                     'SELECT "s1"."e" AS "e", ("s1"."m1" - "s2"."v") AS "m2" FROM "s1" AS "s1" INNER JOIN "s2" AS "s2" ON "s1"."g" = "s2"."g"' % thr)
ref = lambda thr, grouped: ("reference", (S1(thr), 'SELECT COUNT(*), %s FROM "s1"' % ('COUNT(DISTINCT "g")' if grouped else "1")), grouped)
RANKED = lambda: [("s1", 'SELECT "t"."id" AS "e", "t"."g" AS "g", "t"."v" AS "m1", RANK() OVER (PARTITION BY "t"."g" ORDER BY "t"."v" DESC) AS "r" FROM "t" AS "t"')]
rank = lambda: ("rank", (RANKED(), 'SELECT * FROM "s1"'))
RANK_SQL = ('WITH "s1" AS (SELECT "t"."id" AS "e", "t"."g" AS "g", "t"."v" AS "m1", RANK() OVER (PARTITION BY "t"."g" ORDER BY "t"."v" DESC) AS "r" FROM "t" AS "t") '
            'SELECT "s1"."e" AS "e", "s1"."m1" AS "m1" FROM "s1" AS "s1" WHERE "s1"."r" <= %d')
TOTAL = 'SELECT SUM("t"."v") AS "m1", (CAST(SUM("t"."v") AS REAL) / SUM("t"."w")) AS "m2" FROM "t" AS "t"'
derived_one_row = ("derived", "m2", ["m1"], ([], TOTAL), None, None)

tr = lambda sql: bool(trivial(lift(sql, con), con))
CASES = [
    # (name, expected trivial?, grammar's verdict, SQL-side verdict)
    ("gap to the overall average, 0 rows after the filter", True, bool(step_check(con, ref(100, False))), tr(GAP_ALL(100))),
    ("gap to the overall average, 1 row after the filter", True, bool(step_check(con, ref(60, False))), tr(GAP_ALL(60))),
    ("gap to the overall average, 3 rows after the filter", False, bool(step_check(con, ref(20, False))), tr(GAP_ALL(20))),
    ("gap to the group average, every group a single row after the filter (b:50, c:70)", True, bool(step_check(con, ref(40, True))), tr(GAP_G(40))),
    ("gap to the group average, one group has 2 rows", False, bool(step_check(con, ref(5, True))), tr(GAP_G(5))),
    ("top 3 within each group, every group has <= 3 rows (keeps all)", True, bool(step_check(con, rank())), tr(RANK_SQL % 3)),
    ("top 1 within each group (drops rows: not a cut of every row)", False, None, tr(RANK_SQL % 1)),
    ("an overall total and a ratio of two totals on one row (legitimate)", False, bool(step_check(con, derived_one_row)), tr(TOTAL)),
]


def main():
    bad = 0
    for name, want, grammar, sqlside in CASES:
        ok = sqlside == want and (grammar is None or grammar == want)
        bad += not ok
        print("%-4s %-9s grammar %-5s sql %-5s  %s" % ("ok" if ok else "FAIL", "trivial" if want else "kept", grammar, sqlside, name))
    print("\n%d of %d cases failed" % (bad, len(CASES))); return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
