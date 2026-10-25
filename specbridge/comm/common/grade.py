"""COMPARING ANSWERS -- every comparison in comm goes through here.
  spec(g, ref, rows, ties, pool)   the task's own grader (specbridge.pd.spec.render.grade: positional columns, rounding tolerance, tie groups
                                   and the pool at a cut); rows as lists or tuples
  bird_ex(ref, ans)                BIRD's execution accuracy: the SETS of result rows are equal
  tol_match(ref, ans, tol)         sets equal with numbers compared within an absolute tolerance
  canon(rows)                      a multiset of rows, reals rounded to 6 places (for "do two answers differ?")"""
import collections, math


def _t(xs): return [tuple(r) for r in xs] if xs is not None else None


def spec(g, ref, rows, ties=None, pool=None):
    from specbridge.pd.spec.render import grade
    return grade(g, _t(ref), _t(rows), ties, _t(pool))[0]


def canon(rs):
    return collections.Counter(repr([round(v, 6) if isinstance(v, float) else v for v in r]) for r in rs)


def bird_ex(ref, ans):
    return set(map(tuple, ref)) == set(map(tuple, ans))


def tol_match(ref, ans, tol=0.005):
    norm = lambda r: tuple(round(v / tol) if isinstance(v, float) and math.isfinite(v) else v for v in r)
    return set(map(norm, ref)) == set(map(norm, ans))


def shape_tolerant(ref, ans):
    """OUTPUT SHAPE TOLERATED (2026-10-01): correct when some one-to-one choice of the answer's columns, one per gold column,
    reproduces the gold rows as a set (BIRD's comparison), whatever the column order and with extra columns allowed. Row content
    must still match: a DISTINCT that collapses rows, a missing row or a wrong value is still wrong. Values compared exactly."""
    import itertools
    if not ref: return not ans
    if not ans: return False
    n, m = len(ref[0]), len(ans[0])
    if m < n: return False
    target = set(map(tuple, ref))
    cols = [{r[j] for r in ref} for j in range(n)]
    acols = [{r[k] for r in ans} for k in range(m)]
    cand = [[k for k in range(m) if acols[k] == cols[j]] for j in range(n)]     # a column can only stand for one with the same values
    if any(not c for c in cand): return False
    for pick in itertools.product(*cand):
        if len(set(pick)) == n and {tuple(r[k] for k in pick) for r in ans} == target: return True
    return False
