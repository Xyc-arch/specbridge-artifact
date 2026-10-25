"""specbridge.pd.tests.test_semantics — the properties of the one semantic checker (specbridge.pd.realize.semantics), on real catalogues.

    python -m specbridge.pd.tests.test_semantics

Each test states a property of the construction and fails loudly: the contracts on the cases a reviewer named,
the absence of source numbers in P, and that generation and final verification agree because they are one checker.
"""
from __future__ import annotations
import collections, random, sys, warnings


def run():
    warnings.filterwarnings("ignore")
    from specbridge.pd.structures.actions import fit, rebuild, sequence
    from specbridge.pd.structures.algebra import Agg, Arith, Cast, Cmp, Col, Const, Func, Join, Program, Scan
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.realize.generate import attempt
    from specbridge.pd.structures.sources import programs, typers
    fails = []
    def check(name, cond):
        print("  %-86s %s" % (name, "ok" if cond else "FAILED"))
        if not cond: fails.append(name)

    R, T = programs("livesql"), typers("livesql"); law = fit(R, T)
    same = sum(1 for i, p in enumerate(R) if sequence(rebuild(sequence(p, T[i]), law.caps)[0], lets=True) == sequence(p, T[i]))
    check("round trip: every program of R reads back to the same actions (%d/%d)" % (same, len(R)), same == len(R))
    check("no constant of R is a value decision of P (arithmetic parameters and CASE scores)", not any(
        len(c) == 3 and c[2] in ("UNIT_PARAM", "FORMULA_PARAM", "SCORE") and not isinstance(a, str) for c in law.next for a in law.next[c]))

    cal, fin = Catalogue("california_schools"), Catalogue("financial")
    S = cal.sem
    free, enr = Col("frpm", "Free Meal Count (K-12)", "frpm", "NUM"), Col("frpm", "Enrollment (K-12)", "frpm", "NUM")
    pct = Col("frpm", "Percent (%) Eligible Free (K-12)", "frpm", "NUM")
    rec = lambda e, steps=None: S.record(e, steps)
    avg2 = rec(Agg("AVG", Const(2), False, None))
    check("AVG(2) follows the aggregate contract: a constant, not a share (kind %r)" % avg2.kind, avg2.kind == "const" and avg2.unit == "")
    check("1 - AVG(2) is not a supported complement", S.arith("-", S.const(1), avg2)[1] != "supported")
    c1 = rec(Agg("COUNT", Const(1), False, None))
    check("COUNT(1) counts rows (kind %s, unit %s)" % (c1.kind, c1.unit), c1.kind == "count" and c1.unit == "rows")
    check("1 - x is a supported complement for a fraction (%s)" % rec(pct).unit, S.arith("-", S.const(1), rec(pct))[1] == "supported")
    check("1 - x is not a supported complement for a count", S.arith("-", S.const(1), rec(enr))[1] != "supported")
    xx = S.arith("-", rec(enr), rec(enr), equal=True)
    check("x - x: structurally equal operands give a constant, recorded, not a contradiction", xx[0].kind == "const" and xx[1] == "unknown")
    q = rec(Arith("/", Func("round", (free, Const(0))), enr))
    check("round(part) / whole is a share (kind %s, unit %s)" % (q.kind, q.unit), q.kind == "share" and q.unit == "fraction")
    check("CAST(share AS INTEGER) is no longer a share", rec(Cast(Arith("/", free, enr), "INTEGER")).kind != "share")
    inner = Program(Scan("frpm", "frpm", ()), None, (), None, ((Agg("AVG", free, False, None), "o0"),), False, (), None, 0, ())
    so = rec(Col("s1", "o0", "s1", "ANY"), {"s1": inner})
    check("a step output exposes exactly its expression's record", so is rec(Agg("AVG", free, False, None)) or so == S.record(inner.select[0][0], {}))
    shared = Arith("/", free, enr)
    check("a reuse of an object is the same record", rec(shared) is rec(shared))
    avg = fin.sem.record(Agg("AVG", Col("trans", "amount", "trans", "NUM"), False, None))
    check("AVG(amount) keeps its unit and names its quantity and form", avg.quantity == ("trans.amount", "AVG"))
    check("SUM(amount) / COUNT(*) is not excluded", fin.sem.arith("/", fin.sem.record(Agg("SUM", Col("trans", "amount", "trans", "NUM"), False, None)),
                                                                 fin.sem.record(Agg("COUNT", None, False, None)))[1] != "contradicted")
    # a join that repeats a table's rows: account -> trans (many transactions per account), COUNT over account's rows.
    # (account -> loan does NOT: loan.account_id is unique in the rows, the link is one to one.)
    j = Join("trans", "trans", Cmp("=", Col("trans", "account_id", "trans", "KEY"), Col("account", "account_id", "account", "KEY")))
    dist = Col("account", "district_id", "account", "KEY")
    pj = Program(Scan("account", "account", (j,)), None, (), None, ((Agg("COUNT", dist, False, None), "o0"),), False, (), None, 0, ())
    check("a join updates multiplicity: COUNT of a repeated table's column is contradicted (grain)", any(b == "grain" for *_x, b in fin.sem.check(pj)))
    st = Catalogue("store_1")
    check("a join on matching values alone (customers.phone = employees.phone) is contradicted",
          st.sem.join("employees", "phone", "customers", "phone")[0] == "contradicted")
    fk = next(f for f in st.world.declared)
    check("a declared foreign key %s.%s -> %s.%s is a supported join" % fk, st.sem.join(*fk)[0] == "supported")
    check("the binder never offers a contradicted link", all(st.sem.join(*f)[0] != "contradicted" for f in st.links))
    idrec = st.ann[("invoices", "id")] if ("invoices", "id") in st.ann else next(a for a in st.ann.values() if a.slot == "KEY")
    check("an identifier cast to a number is contradicted", st.sem.cast("REAL", idrec)[1] == "contradicted")
    check("BETWEEN 3300 AND 598 is contradicted (an empty range)", S.between(S.const(3300), S.const(598))[0] == "contradicted")
    check("BETWEEN 598 AND 3300 is not", S.between(S.const(598), S.const(3300))[0] != "contradicted")
    txt = next(a for a in cal.ann.values() if a.slot == "TEXT"); numc = next(a for a in cal.ann.values() if a.slot == "NUM")
    check("a text column ordered against a number is contradicted", S.compare(txt, S.const(27), ">")[0] == "contradicted"
          and S.compare(numc, txt, "<")[0] == "contradicted")
    check("a text column compared with text, a number with a text constant, are not",
          S.compare(txt, S.const("Elementary"))[0] != "contradicted" and S.compare(numc, S.const("41.5"))[0] != "contradicted"
          and S.compare(txt, S.const("1655"))[0] != "contradicted")
    check("a comparison's other side is judged at the slot (frame CMP)",
          S.at_slot([("STOP",), ("CMP", txt, ">")], numc, frozenset())[0] == "contradicted" and S.at_slot([("STOP",), ("CMP", txt, "=")], txt, frozenset())[0] != "contradicted")
    # ---- the three traced saved queries (out/review/trace_05dceb7_trace_pick3.json)
    from specbridge.pd.realize.semantics import same_operands
    from specbridge.pd.realize.verify import policies
    enr = cal.ann[("satscores", "enroll12")]
    check("1 - enroll12 (WHOLE of a count, california_schools r14) is contradicted",
          S.arith("-", S.const(1), enr)[1] == "contradicted" and S.arith("-", S.const("WHOLE"), enr)[1] == "contradicted")
    shr = next(a for a in cal.ann.values() if a.unit == "fraction")
    check("1 - share is still a supported complement; 100 - share is contradicted (the wrong whole)",
          S.arith("-", S.const(1), shr)[1] == "supported" and S.arith("-", S.const(100), shr)[1] == "contradicted")
    thr = Catalogue("thrombosis_prediction"); tb, un = thr.ann[("Laboratory", "T-BIL")], thr.ann[("Laboratory", "UN")]
    v = thr.sem.arith("-", tb, un)
    check("T-BIL - UN (same unit mg/dL, thrombosis r22) is unknown, not supported", v[1] == "unknown" and "same unit" in v[2])
    avg_, min_ = S.agg("AVG", False, enr)[0], S.agg("MIN", False, enr)[0]
    check("AVG(x) - MIN(x): one quantity at two levels stays supported", S.arith("-", avg_, min_)[1] == "supported")
    so = Col("s10", "o1", "s10", "NUM")
    check("CAST(s10.o1 AS REAL) / s10.o1 is the same operand (california_schools r6); CAST(x AS INTEGER) / x is not",
          same_operands(Arith("/", Cast(so, "REAL"), so)) and not same_operands(Arith("/", Cast(so, "INTEGER"), so)))
    xx = Arith("*", Arith("/", so, so), Const(2))
    pxx = Program(Scan("frpm", "frpm", ()), None, (), None, ((xx, "o0"),), False, (), None, 0, ())
    check("the duplicate policy finds an x / x nested inside a larger calculation", "duplicate" in policies(pxx, []))
    # ---- the remaining reviewed failures, checked against the targets' gold (out/review)
    hg = cal.ann[("frpm", "High Grade")]
    check("High Grade = 12 (text column, equality with a number, used by BIRD gold) is not contradicted",
          S.compare(hg, S.const(12), "=")[0] != "contradicted")
    check("a text column ordered against a number (compared as text: '100' < '30') is contradicted",
          S.compare(hg, S.const(12), ">")[0] == "contradicted" and S.compare(S.const(30), hg, "<")[0] == "contradicted")
    check("identifier ranges are not judged for order (BIRD gold: account_id BETWEEN 1 AND 10); a text category is",
          fin.sem.compare(fin.ann[("disp", "account_id")], fin.sem.const(1), "BETWEEN")[0] != "contradicted"
          and S.compare(cal.ann[("satscores", "rtype")], S.const("S"), ">")[0] == "contradicted")
    ay = cal.ann[("frpm", "Academic Year")]
    check("sqrt(Academic Year) (california_schools r30) is contradicted", S.func("sqrt", [ay])[1] == "contradicted")
    check("a computed number > Academic Year is contradicted", S.compare(S.case([S.const(1)])[0], ay, ">")[0] == "contradicted")
    check("the left of an ordering comparison is judged at its slot, with or without a partner",
          S.at_slot([("STOP",), ("CMP", S.const(12), ">")], hg, frozenset())[0] == "contradicted"
          and S.at_slot([("STOP",), ("CMP", None, ">")], hg, frozenset())[0] == "contradicted")
    from specbridge.pd.structures.algebra import In as In_
    pin = In_(Col("frpm", "High Grade", "frpm", "TEXT"), (Const(12),))
    check("IN is equality: High Grade IN (12) is not contradicted", S.verdict(pin)[0] != "contradicted")
    # ---- three false rejections of target gold (out/review/gold_check.txt), with counterexamples
    from specbridge.pd.structures.algebra import Join as J_, Strftime as SF
    one = (J_("satscores", "satscores", Cmp("=", Col("schools", "CDSCode", "schools", "KEY"), Col("satscores", "cds", "satscores", "KEY"))),)
    check("schools JOIN satscores on a unique child key is one to one: nothing repeated", S.repeated(one) == frozenset())
    many = (J_("trans", "trans", Cmp("=", Col("account", "account_id", "account", "KEY"), Col("trans", "account_id", "trans", "KEY"))),)
    check("counterexample: account JOIN trans (many transactions per account) repeats account, not trans",
          fin.sem.repeated(many) == frozenset({"account"}))
    check("satscores.cds = frpm.CDSCode (two keys of the same school) is a supported join",
          S.join("satscores", "cds", "frpm", "CDSCode")[0] == "supported")
    yr = lambda c: SF("%Y", Col("schools", c, "schools", "DATE"))
    ya, yb = S.record(yr("OpenDate")), S.record(yr("ClosedDate"))
    check("strftime('%Y', a) - strftime('%Y', b) is a supported duration in years",
          S.arith("-", ya, yb)[1] == "supported" and S.arith("-", ya, yb)[0].unit == "years")
    check("counterexamples: two years added, and a '%Y-%m' text in arithmetic, are contradicted",
          S.arith("+", ya, yb)[1] == "contradicted" and S.arith("-", S.record(SF("%Y-%m", Col("schools", "OpenDate", "schools", "DATE"))), yb)[1] == "contradicted")
    check("strftime('%Y', a) = 1996 is contradicted (no affinity: text vs number); = '1996' and stored High Grade = 12 are not",
          S.compare(ya, S.const(1996), "=")[0] == "contradicted" and S.compare(ya, S.const("1996"), "=")[0] != "contradicted"
          and S.compare(cal.ann[("frpm", "High Grade")], S.const(12), "=")[0] != "contradicted")
    # ---- ordering needs an ordered operand (R orders no text column); the diagnostics' top columns
    tox = Catalogue("toxicology"); lab_, mid = tox.ann[("molecule", "label")], tox.ann[("atom", "molecule_id")]
    check("molecule.label > '+' (a category ordered as text) is contradicted; label = '+' is not",
          tox.sem.compare(lab_, tox.sem.const("+"), ">")[0] == "contradicted" and tox.sem.compare(lab_, tox.sem.const("+"), "=")[0] != "contradicted")
    check("identifier ranges stay: molecule_id BETWEEN 'TR000' AND 'TR099' (BIRD gold)",
          tox.sem.compare(mid, tox.sem.const("TR000"), "BETWEEN")[0] != "contradicted")
    check("a date part may be ordered: strftime('%Y', OpenDate) >= '1995'",
          S.compare(S.record(SF("%Y", Col("schools", "OpenDate", "schools", "DATE"))), S.const("1995"), ">=")[0] != "contradicted")
    check("the left operand of an ordering is judged at its slot: a text column is refused, a number is not",
          tox.sem.at_slot([("STOP",), ("CMP", None, ">")], lab_, frozenset())[0] == "contradicted"
          and S.at_slot([("STOP",), ("CMP", None, ">")], cal.ann[("satscores", "AvgScrRead")], frozenset())[0] != "contradicted")
    # ---- interval scale: explicit weighting is defined, a ratio reading is not; dates stay points in time
    mth_, rd_, tk_ = cal.ann[("satscores", "AvgScrMath")], cal.ann[("satscores", "AvgScrRead")], cal.ann[("satscores", "NumTstTakr")]
    if mth_.scale == "interval":
        w = lambda x, k: S.arith("*", x, S.const(k))[0]
        check("0.5 x math + 0.5 x reading (an explicitly weighted composite of interval scores) is not contradicted",
              S.arith("*", mth_, S.const(0.5))[1] != "contradicted" and S.arith("/", mth_, S.const(2))[1] != "contradicted"
              and S.arith("+", w(mth_, 0.5), w(rd_, 0.5))[1] != "contradicted")
        check("a ratio reading of an interval score is contradicted: math / takers, math * takers, 100 / math",
              S.arith("/", mth_, tk_)[1] == "contradicted" and S.arith("*", mth_, tk_)[1] == "contradicted"
              and S.arith("/", S.const(100), mth_)[1] == "contradicted")
    od = cal.ann[("schools", "OpenDate")]
    check("dates stay points in time: date * 2 and date + date are contradicted",
          S.arith("*", od, S.const(2))[1] == "contradicted" and S.arith("+", od, cal.ann[("schools", "ClosedDate")])[1] == "contradicted")
    nested = Arith("+", Arith("*", Func("current_date", ()), Const(2)), free)
    pn = Program(Scan("frpm", "frpm", ()), None, (), None, ((nested, "o0"),), False, (), None, 0, ())
    check("the final check reaches arithmetic nested inside arithmetic", bool(S.check(pn)))

    rng = random.Random(4); n_ok, contra, refused, t_all, unsupported = 0, 0, collections.Counter(), 0, 0
    for i in range(60):
        p, v, b = attempt(law, cal, rng, law.caps)
        t_all += 1
        if "meaning:" in v: refused[v] += 1
        if p is None: continue
        n_ok += 1
        contra += sum(k for x, k in b.node_report(p).items() if "| contradicted" in x or x.split(" | ")[1].startswith("contradicted"))
        unsupported += sum(1 for e, st, rp in cal.sem.nodes(p) if isinstance(e, Arith) and cal.sem.verdict(e, st, rp)[0] != "supported")
    check("delivered programs (%d): no node the checker calls contradicted" % n_ok, contra == 0)
    print("  (attempts the final check refused for meaning after construction: %d of %d -- compounds judged when closed)" % (sum(refused.values()), t_all))
    print("%d failed" % len(fails))
    return not fails


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
