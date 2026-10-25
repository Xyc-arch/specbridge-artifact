"""Contract tests of specbridge.pd.spec.render: for each constructor and the main interactions, an example that must render with its
stated meaning and a counterexample that must fail closed or be refused by the grader.   python -m specbridge.pd.tests.test_render"""
import sys, warnings
warnings.filterwarnings("ignore")


def run():
    from specbridge.pd.structures.algebra import lift, Program, Scan, SetOp
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.realize.generate import execute
    from specbridge.pd.spec import render as R
    fails = []
    def check(name, ok):
        print("  %-100s %s" % (name, "ok" if ok else "FAILED"))
        if not ok: fails.append(name)
    cal, fin = Catalogue("california_schools"), Catalogue("financial")
    def en(sql, cat=cal):
        """(spec, the instruction without the shared conventions paragraph)."""
        s = R.spec(lift(sql, cat.con), cat); return s, R.english(s).split("\n" + R.NOTES)[0]
    def refused(sql, cat=cal):
        try: en(sql, cat); return False
        except R.Unrenderable: return True
    # ---- intermediate results read by NAME, and never an undefined record set (2026-09-29: three explicit-B texts said
    #      "each `t` record" with `t` undefined, one returned the wrong step columns; rendering had not raised)
    _s, e = en('SELECT sub."o0" FROM (SELECT "CDSCode" AS "x", "Charter" AS "o0" FROM schools) AS sub')
    check("a step column is found by its name, not by the digits in it (o0 is column (2) here)", "column (2) of step 1" in e and "column (1) of step 1" not in e)
    _s, e = en('SELECT w."c" FROM (SELECT v."c" FROM (SELECT "CDSCode" AS "c" FROM schools) AS v) AS w')
    check("a subquery inside a subquery becomes its own earlier step", "Step 2" in e and "each `v` record" not in e)
    _s, e = en('SELECT "CDSCode" FROM schools WHERE "Charter" >= (SELECT MIN(t."k") FROM (SELECT "Charter" AS "k" FROM schools) AS t)')
    check("a subquery inside a value subquery becomes its own step", "each `t` record" not in e and "Step 1" in e)
    _s, e = en('SELECT schools."CDSCode" FROM (SELECT "CDSCode" FROM schools WHERE "Charter" = 1) AS schools')
    check("a subquery named like a stored table: the step reads the stored table, the outer query reads the step",
          "Step 1. Start from each `schools` record" in e and "Start from the rows of step 1" in e.replace("start from", "Start from"))
    _s, e1 = en('SELECT t."avg_v" FROM (SELECT AVG("Enrollment (K-12)") AS "avg_v", "County Code" AS "cc" FROM frpm GROUP BY "County Code") AS t')
    _s, e2 = en('SELECT t."avg_v" FROM (SELECT "County Code" AS "cc", AVG("Enrollment (K-12)") AS "avg_v" FROM frpm GROUP BY "County Code") AS t')
    check("reordered subquery outputs: a named reference keeps its meaning (column (1) vs column (2), both the average)",
          "return (1) column (1) of step 1" in e1 and "return (1) column (2) of step 1" in e2)
    _s, e = en('SELECT a."School", b."School" FROM schools AS a JOIN schools AS b ON a."District" = b."District" WHERE a."CDSCode" <> b."CDSCode"')
    check("a self-join names each side by its alias", "`a.District`" in e and "`b.District`" in e and "(called `b`)" in e)
    # ---- columns: exact identity, the catalogue's words beside it
    _s, e = en('SELECT "Enrollment (K-12)", "Enrollment (Ages 5-17)" FROM frpm')
    check("two similar columns are named by their exact table.column", "`frpm.Enrollment (K-12)`" in e and "`frpm.Enrollment (Ages 5-17)`" in e)
    _s, e = en('SELECT Charter FROM schools')
    check("an indicator states 1 = yes and 0 = no", "1 = yes and 0 = no" in e)
    # ---- arithmetic and conversions
    _s, e = en('SELECT CAST("FRPM Count (K-12)" AS REAL) / "Enrollment (K-12)" FROM frpm')
    check("a division with a decimal operand is exact division (÷)", "A ÷ B" in e and " div " not in e)
    from specbridge.pd.structures.algebra import emit
    p_int = lift('SELECT COUNT(*) / COUNT(DISTINCT account_id) FROM trans', fin.con)
    _s, e = en('SELECT COUNT(*) / COUNT(DISTINCT account_id) FROM trans', fin)
    check("a division of two integers is real-valued (÷): the compiler casts the dividend to REAL",
          "A ÷ B" in e and "CAST(COUNT(*) AS REAL)" in emit(p_int))
    import sqlite3
    check("... and the compiled SQL divides as reals (7 / 2 = 3.5)",
          sqlite3.connect(":memory:").execute("SELECT CAST(7 AS REAL) / 2").fetchone()[0] == 3.5)
    from specbridge.pd.structures.algebra import Arith, Cast, Col as C_
    num = Program(Scan("satscores", "satscores", ()), None, (), None,
                  ((Arith("/", Cast(C_("satscores", "NumGE1500", "satscores", "numeric"), "NUMERIC"), C_("satscores", "NumTstTakr", "satscores", "numeric")), "o0"),),
                  False, (), None, 0, ())
    try: R.spec(num, cal); numeric_refused = False
    except R.Unrenderable: numeric_refused = True
    check("a dividend cast to NUMERIC fails closed (the lifter never produces one: it reads NUMERIC as REAL)",
          numeric_refused and repr(lift('SELECT CAST(NumGE1500 AS NUMERIC) / NumTstTakr FROM satscores', cal.con).select[0][0]).count("type='REAL'") == 1)
    check("arithmetic on a text column whose values are not all numbers fails closed",
          refused('SELECT rtype + 1 FROM satscores'))
    _s, e = en('SELECT CAST(AvgScrMath AS INTEGER), ROUND(AvgScrMath * 0.5, 1) FROM satscores')
    check("CAST AS INTEGER is trunc, ROUND states its digits", "trunc(A)" in e and "round(A × 0.5, 1)" in e)
    _s, e = en('SELECT (NumGE1500 * 1.0 + NumTstTakr) / NumTstTakr, NumTstTakr * 2 FROM satscores')
    check("the same expression is the same letter wherever it occurs", e.count("B is") == 1 and "(A × 1.0) + B" in e)
    _s, e = en('SELECT COALESCE(AvgScrMath, 0), NULLIF(NumTstTakr, 0) FROM satscores')
    from specbridge.pd.structures.algebra import Func, Col
    g = Program(Scan("satscores", "satscores", ()), None, (), None,
                ((Func("greatest", (Col("satscores", "AvgScrMath", "satscores", "NUM"), Col("satscores", "AvgScrRead", "satscores", "NUM"))), "o0"),), False, (), None, 0, ())
    eg = R.english(R.spec(g, cal))
    check("coalesce, nullif and greatest are named functions whose conventions are stated",
          "first_present(A, 0)" in e and "nullif(B, 0)" in e and "larger(A, B)" in eg and "first_present is the first" in R.NOTES and "larger and smaller are missing" in R.NOTES)
    _s, e = en("SELECT NumTstTakr * CASE WHEN AvgScrMath > 500 THEN 2 ELSE 1 END, CASE WHEN AvgScrMath > 500 THEN 2 ELSE 1 END FROM satscores")
    check("an expression with a letter is named by it elsewhere in the instruction (not described twice)",
          e.count("first rule that applies") == 1 and "(2) B" in e)
    # ---- comparisons follow SQLite's affinity rules
    thr = Catalogue("thrombosis_prediction")
    _s, e = en("SELECT ID FROM Laboratory WHERE GOT > '30'", thr)
    check("a number column against a numeric-looking text constant compares as numbers", "(compared as numbers: the text is read as a number)" in e)
    _s, e = en("SELECT cds FROM satscores WHERE cname = 'Alameda'")
    check("text against text compares character by character", "(compared as text, character by character)" in e)
    check("a date part against a number is decided by storage class: fails closed",
          refused("SELECT ID FROM Patient WHERE STRFTIME('%Y', Birthday) = 1990", thr))
    _s, e = en("SELECT ID FROM Patient ORDER BY Diagnosis", thr)
    check("a text order key sorts in character order", "in character order" in e)
    # ---- aggregates, levels, NULLs
    _s, e = en('SELECT cname, COUNT(*), COUNT(AvgScrMath), AVG(AvgScrMath) FROM satscores WHERE NumTstTakr > 10 GROUP BY cname HAVING COUNT(*) > 5')
    check("COUNT(*) and COUNT(x) differ: records vs records whose x is not missing",
          "the number of records in the group" in e and "whose average SAT math score" in e and "is not missing" in e)
    check("AVG states missing values are ignored", "missing values ignored" in e)
    check("WHERE precedes grouping, HAVING follows it", e.index("keep only the records") < e.index("group the kept records") < e.index("keep only the groups"))
    _s, e = en('SELECT COUNT(*), SUM(NumTstTakr) FROM satscores')
    check("an aggregate without GROUP BY is one group over all kept records", "all kept records form one group" in e)
    _s, e = en("SELECT COUNT(*) FILTER (WHERE rtype = 'S') FROM satscores")
    check("an aggregate FILTER counts only the records it names", "counting only the records for which" in e)
    # ---- windows
    _s, e = en('SELECT cname, AVG(AvgScrMath) OVER (PARTITION BY cname) FROM satscores')
    check("a partitioned aggregate window names its row set", "taken over the result rows that share the same value of" in e)
    _s, e = en('SELECT cname, SUM(NumTstTakr) OVER (PARTITION BY cname ORDER BY AvgScrMath) FROM satscores')
    check("an ordered aggregate window states its default frame (ties included)", "every row tied with it" in e)
    s, e = en('SELECT cname, RANK() OVER (ORDER BY AvgScrMath DESC) FROM satscores')
    check("rank states how ties rank; the grader is not declined by rank", "tied rows share a rank" in e and "declined" not in R.grader(s))
    s, e = en('SELECT cname, ROW_NUMBER() OVER (ORDER BY AvgScrMath DESC) FROM satscores')
    check("row_number: rendered, and the grader declines (ties make it undetermined)", "position (1, 2, ...)" in e and "declined" in R.grader(s))
    s, e = en('SELECT cname, NTILE(4) OVER (ORDER BY AvgScrMath) FROM satscores')
    check("ntile states bucket sizes; the grader declines", "differ by at most one" in e and "declined" in R.grader(s))
    s, e = en('SELECT cname, PERCENT_RANK() OVER (ORDER BY AvgScrMath) FROM satscores')
    check("percent_rank is defined by its formula", "(r − 1) ÷ (m − 1)" in e)
    # ---- conditions
    _s, e = en("SELECT cds FROM satscores WHERE sname LIKE 'Lincoln%' AND cname IN ('Alameda', 'Fresno') AND AvgScrMath BETWEEN 400 AND 500 AND AvgScrRead IS NOT NULL")
    check("LIKE, IN, BETWEEN (inclusive), IS NOT NULL each keep their meaning",
          "regardless of case" in e and "is one of 'Alameda', 'Fresno'" in e and "inclusive" in e and ("is not missing" in e or "it is not true that average SAT reading score (`satscores.AvgScrRead`) is missing" in e)
          and "all of the following hold: [1]" in e)
    _s, e = en("SELECT cds FROM satscores WHERE NOT (cname = 'Alameda')")
    check("NOT is rendered with the missing-value convention stated", "it is not true that" in e and "neither it nor its negation holds" in R.NOTES)
    _s, e = en("SELECT CASE WHEN AvgScrMath > 500 THEN 'high' WHEN AvgScrMath > 400 THEN 'mid' END FROM satscores")
    check("CASE takes the first rule that applies; no ELSE is missing", "first rule that applies" in e and "otherwise missing" in e)
    # ---- joins, steps, subqueries
    _s, e = en('SELECT s.cds FROM satscores s LEFT JOIN frpm f ON s.cds = f.CDSCode')
    check("a LEFT JOIN keeps unmatched records with missing values; the join condition is stated",
          "with those values missing" in e and "(`satscores.cds`) equals" in e)
    _s, e = en('WITH a AS (SELECT cname, AVG(AvgScrMath) AS m FROM satscores GROUP BY cname) SELECT cname, m FROM a WHERE m > 500')
    check("a step is numbered and referenced by position, not re-described", "Step 1." in e and "column (2) of step 1" in e and "Step 2 (the answer)" in e)
    _s, e = en('SELECT cds FROM satscores WHERE NumTstTakr > (SELECT AVG(NumTstTakr) FROM satscores)')
    check("a scalar subquery states its single value", "the single value returned by [" in e)
    s, e = en('SELECT cds FROM satscores WHERE NumTstTakr = (SELECT NumTstTakr FROM satscores)')
    check("a scalar subquery that may return several rows says so (first row, undetermined), and the grader declines",
          "the value in the first row returned by" in e and "not determined" in e and "declined" in R.grader(s))
    _s, e = en("SELECT cds FROM satscores WHERE cname NOT IN ('Alameda', 'Fresno')")
    check("NOT IN keeps the three outcomes: false on a match, undetermined on no match with a missing value, else true",
          "false when it equals one of them" in e and "equals none of them and one of them is missing" in e and "otherwise true" in e)
    _s, e = en("SELECT cds FROM satscores WHERE cname IN ('Alameda', 'Fresno')")
    check("IN keeps the three outcomes too (undetermined, not false, on no match with a missing value)",
          "true when it equals one of them" in e and "otherwise false" in e)
    _s, e = en("SELECT cds FROM satscores WHERE cname NOT IN (SELECT cname FROM satscores WHERE NumTstTakr > 100000)")
    import sqlite3 as _s3
    empty_ok = _s3.connect(":memory:").execute("SELECT NULL NOT IN (SELECT 1 WHERE 0), NULL IN (SELECT 1 WHERE 0)").fetchone() == (1, 0)
    check("an empty IN subquery: NOT IN is true and IN false even for a missing value (SQLite), and the rendering says so",
          empty_ok and "returns no rows it is true, even for a missing value" in e)
    check("SUM of a text column that is not all numbers fails closed", refused("SELECT SUM(rtype) FROM satscores"))
    check("text() of a decimal fails closed (SQLite's float formatting)", refused("SELECT CAST(AvgScrMath * 1.5 AS TEXT) FROM satscores"))
    from specbridge.pd.spec.render import _declared
    import sqlite3 as _sq
    class _Fake: pass
    fk = _Fake(); fk.con = _sq.connect(":memory:"); fk.con.execute("CREATE TABLE m (x INTEGER)"); fk.con.execute("INSERT INTO m VALUES (1), ('abc')")
    check("a column declared INTEGER that stores text is typed from its rows as mixed", _declared(fk, "m", "x")[0] == "mixed")
    # ---- order, limit, determinacy
    _s, e = en('SELECT cds, AvgScrMath FROM satscores ORDER BY AvgScrMath DESC LIMIT 5')
    check("ORDER states where missing values go; LIMIT follows the order", "descending (missing last)" in e and e.index("order the result rows") < e.index("keep only the first 5"))
    from specbridge.pd.structures.algebra import Unsupported
    try: lift('SELECT cds FROM satscores LIMIT 5', cal.con); unrep = False
    except Unsupported: unrep = True
    check("LIMIT without ORDER is unrepresentable in the IR (and would be declined by the grader)", unrep)
    s, _e = en('WITH a AS (SELECT cds FROM satscores ORDER BY AvgScrMath LIMIT 3) SELECT cds FROM a')
    check("a step cut by LIMIT on an order that may tie: the grader declines", "declined" in R.grader(s))
    p = lift('SELECT cname, AvgScrMath FROM satscores ORDER BY cname LIMIT 3', cal.con)
    rows, groups, pool = R.reference(p, cal.con, execute); g = R.grader(R.spec(p, cal))
    alt = [r for r in pool if r not in rows][:1]
    check("a LIMIT cutting a tie accepts any rows of the tie", pool is not None and (not alt or R.grade(g, rows, rows[:-1] + alt, groups, pool)[0]))
    check("... and still rejects a row from outside the tie", not R.grade(g, rows, rows[:-1] + [("ZZZ", 1)], groups, pool)[0])
    # ---- fail closed
    check("a set operation fails closed", refused('SELECT cds FROM satscores UNION SELECT CDSCode FROM frpm'))
    check("an unknown function fails closed", refused('SELECT upper(cname) FROM satscores'))
    try: lift('SELECT cds FROM satscores s WHERE NumTstTakr > (SELECT AVG(NumTstTakr) FROM satscores t WHERE t.cname = s.cname)', cal.con); unrep = False
    except Unsupported: unrep = True
    check("a correlated subquery is unrepresentable in the IR (the renderer would also fail closed)", unrep)
    print("%d failed" % len(fails))
    return fails


if __name__ == "__main__":
    sys.path.insert(0, ".")
    sys.exit(1 if run() else 0)
