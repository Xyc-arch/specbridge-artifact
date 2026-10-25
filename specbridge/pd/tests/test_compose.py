"""REGRESSION CASES FOR compose-v3.2 (v3.1 cases plus the recomputed-aggregate cases): identities are blocked, legitimate compositions are kept.
For each case, the grammar's decision (is the move offered?) AND a direct computation on student_club that shows why:
a prohibited composition really is constant on the data, a legitimate one really varies.
    python -m specbridge.pd.tests.test_compose"""
import sys
from specbridge.pd.structures.compose import Space, Stage, M

sp = Space("student_club"); con = sp.S.con
G = ("g", "event", "type"); ALL = ("all",)
EG = ("eg", "link_to_event", "event", "type")
base = Stage(EG, (M("", "USD", True, True, 0, slots=frozenset({"q0"}), name="SUM"),), 1)


def after(st, pred):
    """The stage after the first move satisfying pred (or None when the grammar does not offer it)."""
    for mv, nxt in sp.moves(st):
        if pred(mv): return nxt
    return None


def offered(st, pred): return after(st, pred) is not None


gap_g = after(base, lambda mv: mv[0] == "baseline" and mv[2] == G and mv[3] == "gap" and not mv[4])
gap_g_above = after(base, lambda mv: mv[0] == "baseline" and mv[2] == G and mv[3] == "gap" and mv[4])
idx_all = after(base, lambda mv: mv[0] == "baseline" and mv[2] == ALL and mv[3] == "index")
share_g = after(base, lambda mv: mv[0] == "share" and mv[2] == G)
share_all = after(base, lambda mv: mv[0] == "share" and mv[2] == ALL)
gap_all = after(base, lambda mv: mv[0] == "baseline" and mv[2] == ALL and mv[3] == "gap" and not mv[4])
agg_to = lambda L: (lambda mv: mv[0] == "agg" and mv[1] == L)
cmp_on = lambda i, op, K: (lambda mv: (mv[0] == "baseline" and mv[1] == i and mv[3] == op and mv[2] == K) or (op == "share" and mv[0] == "share" and mv[1] == i and mv[2] == K))

# per-event totals with the event type: the stage every case starts from, on the data
PER = ('WITH per AS (SELECT b.link_to_event AS e, ev.type AS g, SUM(b.spent) AS v FROM budget b JOIN event ev ON ev.event_id = b.link_to_event '
       'GROUP BY b.link_to_event, ev.type), ga AS (SELECT g, AVG(v) AS av, SUM(v) AS tv FROM per GROUP BY g), oa AS (SELECT AVG(v) AS ov FROM per) ')
q = lambda sql: con.execute(PER + sql).fetchall()

CASES = [
    # (name, grammar must offer it?, grammar decision, data evidence -> True when the evidence agrees)
    ("mean over each type of the gap to the type average (always 0)", False, offered(gap_g, agg_to(G)),
     lambda: max(abs(r[0]) for r in q("SELECT AVG(per.v - ga.av) FROM per JOIN ga ON per.g = ga.g GROUP BY per.g")) < 1e-9),
    ("mean over everything of the gap to the type average (always 0)", False, offered(gap_g, agg_to(ALL)),
     lambda: abs(q("SELECT AVG(per.v - ga.av) FROM per JOIN ga ON per.g = ga.g")[0][0]) < 1e-9),
    ("mean of the index against the overall average (always 1)", False, offered(idx_all, agg_to(ALL)),
     lambda: abs(q("SELECT AVG(per.v / oa.ov) FROM per JOIN oa ON oa.ov IS NOT NULL")[0][0] - 1) < 1e-9),
    ("sum of shares of the type total within each type (always 1; mean = 1/n)", False, offered(share_g, agg_to(G)),
     lambda: max(abs(r[0] - 1) for r in q("SELECT SUM(CAST(per.v AS REAL) / ga.tv) FROM per JOIN ga ON per.g = ga.g GROUP BY per.g")) < 1e-9),
    ("gap to the overall average of a gap to the type average (restates it: that average is 0)", False, offered(gap_g, cmp_on(1, "gap", ALL)),
     lambda: abs(q("SELECT AVG(per.v - ga.av) FROM per JOIN ga ON per.g = ga.g")[0][0]) < 1e-9),
    ("index of a gap at its own level (divides by 0)", False, offered(gap_g, cmp_on(1, "index", G)), lambda: True),
    ("share of a share at a covering level (a count rescaling)", False, offered(share_g, cmp_on(1, "share", ALL)), lambda: True),
    # v3.2: a second comparison of the SAME measure at the SAME level over the SAME rows recomputes its average (or total)
    ("gap of a measure to the overall average after its index against it (recomputes the overall average)", False, offered(idx_all, cmp_on(0, "gap", ALL)),
     lambda: abs(q("SELECT AVG(v) FROM per")[0][0] - q("SELECT ov FROM oa")[0][0]) < 1e-9),
    ("share of a measure in the type total after its share in it (recomputes the type total)", False, offered(share_g, cmp_on(0, "share", G)), lambda: True),
    ("gap of a measure to the type average after the gap to it, ABOVE filter (recomputes it on the same rows)", False,
     offered(gap_g, lambda mv: mv[0] == "baseline" and mv[1] == 0 and mv[2] == G and mv[4]), lambda: True),
    ("gap to the type average after a share in the type total (AVG vs SUM: a different aggregation)", True, offered(share_g, cmp_on(0, "gap", G)),
     lambda: q("SELECT COUNT(*) FROM ga WHERE ABS(av - tv) > 1e-9")[0][0] >= 1),
    ("gap to the type average among the above-average events (the rows changed)", True, offered(gap_g_above, cmp_on(0, "gap", G)),
     lambda: q("SELECT COUNT(*) FROM (SELECT per.g, AVG(per.v) AS a2 FROM per JOIN ga ON per.g = ga.g WHERE per.v > ga.av GROUP BY per.g) x JOIN ga ON x.g = ga.g WHERE ABS(x.a2 - ga.av) > 1e-9")[0][0] >= 1),
    # legitimate: population, grouping or weights make them vary
    ("mean gap of the ABOVE-average events per type (a different population)", True, offered(gap_g_above, agg_to(G)),
     lambda: len({round(r[0], 6) for r in q("SELECT AVG(per.v - ga.av) FROM per JOIN ga ON per.g = ga.g WHERE per.v > ga.av GROUP BY per.g")}) >= 2),
    ("mean per type of the gap to the OVERALL average (a finer grouping than the reference)", True, offered(gap_all, agg_to(G)),
     lambda: len({round(r[0], 6) for r in q("SELECT AVG(per.v - oa.ov) FROM per JOIN oa ON oa.ov IS NOT NULL GROUP BY per.g")}) >= 2),
    ("mean over types of the type means of the overall gap (weights changed: one per type)", True,
     offered(after(gap_all, agg_to(G)), agg_to(ALL)) if after(gap_all, agg_to(G)) else False,
     lambda: abs(q("SELECT AVG(m) FROM (SELECT AVG(per.v - oa.ov) AS m FROM per JOIN oa ON oa.ov IS NOT NULL GROUP BY per.g)")[0][0]) > 1e-6),
    ("mean per type of the share of the OVERALL total", True, offered(share_all, agg_to(G)),
     lambda: len({round(r[0], 9) for r in q("SELECT AVG(CAST(per.v AS REAL) / (SELECT SUM(v) FROM per)) FROM per GROUP BY per.g")}) >= 2),
    ("gap of an overall share to the type average (not proven constant)", True, offered(share_all, cmp_on(1, "gap", G)), lambda: True),
]


def main():
    bad = 0
    for name, want, got, evidence in CASES:
        ev = evidence(); ok = (got == want) and ev
        bad += not ok
        print("%-4s %-9s %s%s" % ("ok" if ok else "FAIL", "allowed" if want else "blocked", name, "" if ev else "   <- the data does not show it"))
    print("\n%d of %d cases failed" % (bad, len(CASES))); return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
