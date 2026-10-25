"""STRUCTURAL FEATURES OF SQL, CORPUS AGAINST CORPUS (2026-10-13): what Spider 2.0's computations look like, and what the generator
still lacks. Code only (sqlglot); no model. Sets: Spider 2.0-lite SQLite queries that compute an accepted answer (the valid released
gold queries + Sonnet's correct baseline answers, out/spider2/errors/plain), the generated eval12 corpus (sql_A of the frozen
request sets + the single-task corpus), and BIRD dev gold.
    python -m specbridge.report.sqlshape   -> out/sqlshape/SHAPE.md, shape.json"""
import collections, glob, json, os, re, statistics, sys
import sqlglot
from sqlglot import exp

OUT = "out/sqlshape"
WINDOW_FNS = ("RANK", "DENSE_RANK", "ROW_NUMBER", "NTILE", "LAG", "LEAD", "FIRST_VALUE", "LAST_VALUE", "SUM", "AVG", "COUNT", "MIN", "MAX", "PERCENT_RANK", "CUME_DIST")


def features(sql):
    try: q = sqlglot.parse_one(sql, read="sqlite")
    except Exception: return None
    w = q.args.get("with") or q.args.get("with_")
    ctes = len(w.expressions) if w else 0
    def depth(n, d=0):
        subs = [x for x in n.iter_expressions()]
        return max([depth(x, d + (1 if isinstance(x, exp.Subquery) else 0)) for x in subs] + [d])
    wins = list(q.find_all(exp.Window)); wn = collections.Counter()
    for x in wins:
        f = x.this; name = (f.sql_name() if hasattr(f, "sql_name") else type(f).__name__).upper()
        frame = x.args.get("spec") is not None
        wn["frame (moving window)" if frame else ("lag/lead" if name in ("LAG", "LEAD") else ("rank/row_number" if name in ("RANK", "DENSE_RANK", "ROW_NUMBER", "NTILE", "PERCENT_RANK", "CUME_DIST") else "running aggregate"))] += 1
    def arith(n):
        if isinstance(n, (exp.Add, exp.Sub, exp.Mul, exp.Div)): return 1 + max(arith(n.this), arith(n.expression))
        return max([arith(x) for x in n.iter_expressions()] + [0])
    datef = sum(1 for f in q.find_all(exp.Func) if re.search(r"strftime|date|julianday|time", f.sql_name().lower()) or isinstance(f, (exp.TimeToStr, exp.StrToTime)))
    return {"chars": len(sql), "ctes": ctes, "subquery_depth": depth(q), "joins": len(list(q.find_all(exp.Join))),
            "aggregates": len(list(q.find_all(exp.AggFunc))), "windows": len(wins), "window_kinds": dict(wn), "case": len(list(q.find_all(exp.Case))),
            "date_functions": datef, "arith_depth": arith(q), "set_ops": len(list(q.find_all(exp.Union))) + len(list(q.find_all(exp.Intersect))) + len(list(q.find_all(exp.Except))),
            "weighted_avg": bool(re.search(r"SUM\s*\([^()]*\*[^()]*\)\s*/\s*(NULLIF\s*\()?\s*SUM", sql, re.I))}


def corpora():
    from specbridge.comm.transfer import spider2 as S
    T = S.tasks(); sp = []
    for f in sorted(glob.glob(S.GOLD + "/sql/*.sql")):
        iid = os.path.basename(f)[:-4]
        if iid in T and os.path.exists("out/spider2/errors/spec/%s.json" % iid): sp.append(open(f).read())       # valid released gold
    for f in sorted(glob.glob("out/spider2/errors/plain/*.json")):
        o = json.load(open(f))
        if o.get("matches") and o.get("sql"): sp.append(o["sql"])
    gen = [c["sql_A"] for c in json.load(open("out/transfer/eval12-v2/render/eval/frozen.json"))["cases"] if c.get("sql_A")]
    bird = [x["SQL"] for x in json.load(open("dev_unzipped/dev_20240627/dev.json"))]
    return {"Spider 2.0 (SQL computing an accepted answer)": sp, "SpecBridge generated (request sets)": gen, "BIRD dev gold": bird}


def summarize(F):
    F = [f for f in F if f]; n = len(F); med = lambda k: statistics.median(f[k] for f in F); share = lambda fn: 100 * sum(1 for f in F if fn(f)) / n
    wk = collections.Counter()
    for f in F:
        for k, v in f["window_kinds"].items(): wk[k] += 1 if v else 0
    return {"n": n, "median chars": med("chars"), "median CTEs": med("ctes"), "with >= 3 CTEs (%)": share(lambda f: f["ctes"] >= 3),
            "median joins": med("joins"), "median aggregates": med("aggregates"), "with a window (%)": share(lambda f: f["windows"] > 0),
            **{"window: %s (%%)" % k: 100 * wk[k] / n for k in ("frame (moving window)", "lag/lead", "rank/row_number", "running aggregate")},
            "with CASE (%)": share(lambda f: f["case"] > 0), "with date functions (%)": share(lambda f: f["date_functions"] > 0),
            "median arithmetic depth": med("arith_depth"), "weighted average (%)": share(lambda f: f["weighted_avg"]), "set operation (%)": share(lambda f: f["set_ops"] > 0)}


def main():
    C = corpora(); R = {k: summarize([features(s) for s in v]) for k, v in C.items()}
    keys = list(next(iter(R.values())).keys()); names = list(R)
    L = ["# SQL structure: Spider 2.0 vs the generated corpus vs BIRD (`specbridge.report.sqlshape`)\n",
         "| feature | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for k in keys: L.append("| %s | %s |" % (k, " | ".join(("%.0f" % R[n][k]) if isinstance(R[n][k], float) and R[n][k] >= 10 or k == "n" else "%.1f" % R[n][k] for n in names)))
    os.makedirs(OUT, exist_ok=True); json.dump(R, open(OUT + "/shape.json", "w"), indent=1); open(OUT + "/SHAPE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
