"""PERSONALIZATION ON SPIDER 2.0-LITE (SQLite part, 2026-10-12). The same two in-context blocks as checklist.py (personalization: the
kinds of choice the user wants raised; placebo: the user's SQL writing style), the same explanation call (disclose.INSTRUCTION), on
the 135 local tasks of Spider 2.0-lite -- databases, questions and accepted gold answers we did not build, and choice types that were
not mined from them. Many tasks accept several gold answers (the benchmark's own record of more than one valid reading).
Scoring by the official comparison (copied below from spider2-lite/evaluation_suite/evaluate.py, which imports BigQuery modules):
    accuracy        the primary SQL matches some accepted gold answer (the benchmark's own score)
    answer set      the primary SQL or an offered alternative matches some accepted gold answer
    readings        on tasks whose accepted answers include >= 2 mutually distinct ones: how many distinct ones the answer set covers
    python -m specbridge.comm.transfer.spider2 run [<model> ...]  -> out/spider2/incontext/<arm>/<model>/<instance>.json
    python -m specbridge.comm.transfer.spider2 report              -> out/spider2/incontext/RESULTS.md, results.json
Tasks run one at a time with every (model, arm) side by side; the report is rewritten every 5 tasks. At most 6 workers."""
import collections, concurrent.futures as cf, json, math, os, random, re, sqlite3, sys, threading, time
import pandas as pd
from specbridge.comm.transfer import checklist as K

ROOT = "spider2_data/spider2-lite"; DBDIR = ROOT + "/resource/databases/spider2-localdb"; GOLD = ROOT + "/evaluation_suite/gold"
OUT = "out/spider2/incontext"; MODELS = K.MODELS; SEED, B, TIMEOUT = 20261014, 4000, 120
LIB = "library/examples.jsonl"; FACTS = OUT + "/facts"

# FOUR IN-CONTEXT STRATEGIES, each one step of the paper's analysis (the request, the database, the library):
#   placebo   the user's SQL writing style (checklist.PLACEBO)                       -- control
#   raise     which kinds of choice the user wants raised (checklist.CHECK)          -- models compute but do not raise
#   facts     raise + this database's data facts where readings can differ           -- choices matter only where the data differs
#   examples  raise + one reviewed library example per kind (BIRD / Spider 1 only)   -- the library of real disagreements
ARMS = ["placebo", "raise", "facts", "examples"]
LIBTYPE = {"aggregation_level": "Level of aggregation", "counting_unit": "Unit counted", "missing_values": "Missing values",
           "ties_and_selection": "Ties at a limit", "calculation": "Signed or absolute amounts / calculation", "relationship_role": "Relationship role",
           "population_scope": "Baseline and population", "time_scope": "Boundaries and time scope"}


# --- official Spider 2.0 comparison (verbatim logic) ---------------------------------------------------------------------------
def compare_pandas_table(pred, gold, condition_cols=None, ignore_order=False):
    tolerance = 1e-2
    def normalize(value): return 0 if pd.isna(value) else value
    def vectors_match(v1, v2, tol=tolerance, ignore_order_=False):
        v1 = [normalize(x) for x in v1]; v2 = [normalize(x) for x in v2]
        if ignore_order_:
            v1 = sorted(v1, key=lambda x: (x is None, str(x), isinstance(x, (int, float))))
            v2 = sorted(v2, key=lambda x: (x is None, str(x), isinstance(x, (int, float))))
        if len(v1) != len(v2): return False
        for a, b in zip(v1, v2):
            if pd.isna(a) and pd.isna(b): continue
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                if not math.isclose(float(a), float(b), abs_tol=tol): return False
            elif a != b: return False
        return True
    if condition_cols:
        if not isinstance(condition_cols, (list, tuple)): condition_cols = [condition_cols]
        gold_cols = gold.iloc[:, condition_cols]
    else: gold_cols = gold
    t_gold, t_pred = gold_cols.transpose().values.tolist(), pred.transpose().values.tolist()
    return int(all(any(vectors_match(g, p, ignore_order_=ignore_order) for p in t_pred) for g in t_gold))


def golds(iid, E):
    """Accepted gold answers with their condition columns (resolve_gold_paths + compare_multi_pandas_table conventions)."""
    d = GOLD + "/exec_result"; one = "%s/%s.csv" % (d, iid)
    ps = [one] if os.path.exists(one) else sorted("%s/%s" % (d, f) for f in os.listdir(d) if re.match(r"^%s(_[a-z])?\.csv$" % re.escape(iid), f))
    G = [pd.read_csv(p) for p in ps]; cc = E[iid].get("condition_cols")
    if cc in (None, [], [[]], [None]): cc = [[] for _ in G]
    elif len(G) > 1 and not all(isinstance(x, list) for x in cc): cc = [cc for _ in G]
    elif len(G) == 1 and not (cc and isinstance(cc[0], list)): cc = [cc]
    return [(g, cc[i]) for i, g in enumerate(G)], bool(E[iid].get("ignore_order"))


def matches(df, G, io):
    """Indices of the accepted gold answers this result matches."""
    if df is None: return []
    out = []
    for i, (g, c) in enumerate(G):
        try:
            if compare_pandas_table(df, g, c, io): out.append(i)
        except Exception: pass
    return out


def distinct(G, io):
    """Groups of accepted answers that match each other in both directions; each group is one reading."""
    reps, label = [], {}
    for j, (g, c) in enumerate(G):
        for r in reps:
            try: same = compare_pandas_table(G[r][0], g, c, io) and compare_pandas_table(g, G[r][0], G[r][1], io)
            except Exception: same = False
            if same: label[j] = r; break
        else: reps.append(j); label[j] = j
    return label


# --- context and execution ---------------------------------------------------------------------------------------------------
def context(db):
    """CREATE statements and three example rows per table, plus nothing else; documentation = the task's external-knowledge file."""
    con = sqlite3.connect("file:%s/%s.sqlite?mode=ro" % (DBDIR, db), uri=True); L = []
    for name, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE type IN ('table','view') AND sql IS NOT NULL ORDER BY name"):
        L.append(sql.strip() + ";")
        try:
            rows = con.execute('SELECT * FROM "%s" LIMIT 3' % name.replace('"', '""')).fetchall()
            if rows: L.append("-- example rows: " + "; ".join(str(tuple(str(v)[:40] for v in r)) for r in rows))
        except Exception: pass
    con.close(); return "\n".join(L)


def docs(task):
    f = task.get("external_knowledge")
    return open(ROOT + "/resource/documents/" + f).read() if f and os.path.exists(ROOT + "/resource/documents/" + f) else "(none)"


def run_sql(db, sql):
    """Result as a DataFrame, None on error or after TIMEOUT seconds (read-only connection)."""
    con = sqlite3.connect("file:%s/%s.sqlite?mode=ro" % (DBDIR, db), uri=True, check_same_thread=False); t0 = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - t0 > TIMEOUT else 0, 100000)
    try: df = pd.read_sql_query(sql, con)
    except Exception: return None
    finally: con.close()
    import io                                                  # the official evaluator saves the result as CSV and reads it back
    try: return pd.read_csv(io.StringIO(df.to_csv(index=False)))   # (types as in the gold CSVs: '2001' -> 2001)
    except Exception: return df.iloc[0:0] if df.empty else df


def db_facts(db):
    """Code-computed data facts for the whole database (gold-free; the facts choice_points.profile reads for one query), cached
    under FACTS/<db>.txt: per column the NULL, zero, empty-string and negative counts that are not zero, and per join key the rows per
    key value when a value repeats. Only columns with such a fact are listed."""
    f = "%s/%s.txt" % (FACTS, db)
    if os.path.exists(f): return open(f).read()
    con = sqlite3.connect("file:%s/%s.sqlite?mode=ro" % (DBDIR, db), uri=True); L = []
    tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    cols = {t: [r[1] for r in con.execute('PRAGMA table_info("%s")' % t)] for t in tabs}
    keys = {(t, r[3]) for t in tabs for r in con.execute('PRAGMA foreign_key_list("%s")' % t)}
    names = collections.Counter(c.lower() for t in tabs for c in cols[t])
    keys |= {(t, c) for t in tabs for c in cols[t] if names[c.lower()] > 1 and re.search(r"(id|key|code)$", c.lower())}
    q = lambda c: '"%s"' % c.replace('"', '""')
    for t in tabs:
        if not cols[t]: continue
        parts = ", ".join("SUM(%s IS NULL), SUM(%s = 0), SUM(%s = ''), SUM(typeof(%s) IN ('integer','real') AND %s < 0)" % ((q(c),) * 5) for c in cols[t])
        try: row = con.execute("SELECT COUNT(*), %s FROM %s" % (parts, q(t))).fetchone()
        except Exception: continue
        n = row[0]; facts = []
        for i, c in enumerate(cols[t]):
            nl, z, e, ng = (v or 0 for v in row[1 + 4 * i: 5 + 4 * i])
            bits = ["%d NULL" % nl] * bool(nl) + ["%d zero" % z] * bool(z) + ["%d empty" % e] * bool(e) + ["%d negative" % ng] * bool(ng)
            if (t, c) in keys:
                try:
                    mx, av = con.execute("SELECT MAX(k), AVG(k) FROM (SELECT COUNT(*) AS k FROM %s WHERE %s IS NOT NULL GROUP BY %s)" % (q(t), q(c), q(c))).fetchone()
                    if mx and mx > 1: bits.append("join key, up to %d rows per value (average %.1f)" % (mx, av))
                except Exception: pass
            if bits: facts.append("%s: %s" % (c, ", ".join(bits)))
        if facts: L.append("%s (%d rows): %s" % (t, n, "; ".join(facts)))
    con.close(); txt = "\n".join(L); txt = txt if len(txt) <= 4000 else txt[:txt.rfind("\n", 0, 4000)]   # whole lines only
    os.makedirs(FACTS, exist_ok=True); open(f, "w").write(txt); return txt


def lib_examples():
    """One reviewed example per kind: the first record by id with raise=true, status unresolved, from BIRD or Spider 1 (never Spider 2)."""
    R = sorted((json.loads(l) for l in open(LIB)), key=lambda r: r["id"]); out = []
    for ty, name in LIBTYPE.items():
        r = next((r for r in R if r["type"] == ty and r.get("raise") and r.get("status") == "unresolved" and len(r.get("readings") or []) >= 2), None)
        if not r: continue
        a, b = r["readings"][:2]
        out.append("- %s. Request: %s\n  Open choice: %s\n  Reading 1: %s\n  Reading 2: %s" % (name, r["question"].split("\n")[0], r["decision"], a["reading"], b["reading"]))
    return "\n".join(out)


def block(arm, db):
    if arm == "placebo": return K.PLACEBO
    if arm == "raise": return K.CHECK
    if arm == "facts": return K.CHECK + "\n\nDATA FACTS OF THIS DATABASE (computed from the data; a choice matters only where the data makes the readings differ):\n" + db_facts(db)
    return K.CHECK + "\n\nEXAMPLES OF SUCH CHOICES FROM OTHER DATABASES (the request, the open choice, and two readings):\n" + lib_examples()


def prompt(arm, db):
    head, tail = disclose_instruction().split("\n\nDATABASE SCHEMA:", 1)
    return head + "\n\n" + block(arm, db).replace("%", "%%") + "\n\nDATABASE SCHEMA:" + tail


def disclose_instruction():
    from specbridge.comm.transfer import disclose as X
    return X.INSTRUCTION


# --- run and report ----------------------------------------------------------------------------------------------------------
def tasks():
    T = [json.loads(l) for l in open(ROOT + "/spider2-lite.jsonl")]
    return {t["instance_id"]: t for t in T if t["instance_id"].startswith("local")}


def _f(arm, m, iid): return "%s/%s/%s/%s.json" % (OUT, arm, m, iid)


def run(models, workers=6):
    from specbridge.comm.common.llm import call, parse
    T = tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(GOLD + "/spider2lite_eval.jsonl")}
    ctx = {}; lock = threading.Lock()
    def one(job):
        iid, m, arm = job; f = _f(arm, m, iid)
        if os.path.exists(f): return
        t = T[iid]
        with lock:
            if t["db"] not in ctx: ctx[t["db"]] = context(t["db"])
            pr = prompt(arm, t["db"])
        t0 = time.time(); txt = call(pr % (ctx[t["db"]], docs(t), t["question"]), m)
        if not (txt or "").strip(): return                      # a failed call is not an answer: asked again on rerun
        r = parse(txt, "{") or {}; G, io = golds(iid, E); prim = r.get("sql")
        alts = [{"interpretation": x.get("interpretation"), "sql": x["sql"], "matches": matches(run_sql(t["db"], x["sql"]), G, io)}
                for x in (r.get("alternatives") or [])[:2] if isinstance(x, dict) and x.get("sql")]
        df = run_sql(t["db"], prim) if prim else None
        o = {"instance_id": iid, "db": t["db"], "model": m, "arm": arm, "response": r, "raw": None if r else txt, "primary_executes": df is not None,
             "primary_matches": matches(df, G, io), "alternatives": alts, "n_gold": len(G), "seconds": round(time.time() - t0, 1)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    ids = sorted(T); random.Random(SEED).shuffle(ids)
    jobs = [(i, m, a) for i in ids for m in models for a in ARMS]; per = len(models) * len(ARMS)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for n, _ in enumerate(ex.map(one, jobs), 1):
            if n % (5 * per) == 0: report(quiet=True); print("tasks %d/%d, report updated" % (n // per, len(ids)), flush=True)
    report(quiet=True); open(OUT + "/run.done", "w").write("ok\n")


def report(quiet=False):
    """Per solver and strategy: accuracy (primary matches an accepted answer), answer set (primary or an alternative does), and, on
    tasks with >= 2 distinct accepted answers, >= 2 readings covered. Each strategy against the placebo on the tasks where every
    strategy is saved: exact McNemar per solver, sign-flip over tasks x solvers pooled."""
    T = tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(GOLD + "/spider2lite_eval.jsonl")}
    D = {iid: distinct(*golds(iid, E)) for iid in T}; multi = {i for i, lab in D.items() if len(set(lab.values())) >= 2}
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, i) for i in range(min(b, c) + 1)) / 2 ** (b + c))
    MET = [("acc", "accuracy", False), ("set", "answer set", False), ("two", ">= 2 readings", True)]
    res = {"n_tasks": len(T), "n_multi_reading": len(multi), "arms": ARMS, "models": {}, "pooled": {}}; pool = collections.defaultdict(list)
    for m in MODELS:
        rows = []
        for iid in sorted(T):
            fs = {a: _f(a, m, iid) for a in ARMS}
            if not all(os.path.exists(f) for f in fs.values()): continue
            row = {"instance_id": iid, "multi": iid in multi}
            for a, f in fs.items():
                o = json.load(open(f)); got = set(o["primary_matches"]) | {x for al in o["alternatives"] for x in al["matches"]}
                row[a] = {"acc": bool(o["primary_matches"]), "set": bool(got), "two": len({D[iid][g] for g in got}) >= 2, "n_alts": len(o["alternatives"])}
            rows.append(row)
        x = {"n": len(rows), "n_multi": sum(r["multi"] for r in rows), "rows": rows, "metrics": {}}
        for k, _name, only_multi in MET:
            rs = [r for r in rows if r["multi"] or not only_multi]; x["metrics"][k] = {"n": len(rs)}
            for a in ARMS:
                cell = {"count": sum(r[a][k] for r in rs)}
                if a != "placebo":
                    b1 = sum(r[a][k] and not r["placebo"][k] for r in rs); c1 = sum(r["placebo"][k] and not r[a][k] for r in rs)
                    cell.update(gain=b1, loss=c1, p=mc(b1, c1)); pool[(a, k)] += [int(r[a][k]) - int(r["placebo"][k]) for r in rs]
                x["metrics"][k][a] = cell
        res["models"][m] = x
    rng = random.Random(SEED)
    for (a, k), ds in pool.items():
        if not ds: continue
        obs = sum(ds) / len(ds); null = [sum(d * rng.choice((-1, 1)) for d in ds) / len(ds) for _ in range(B)]
        res["pooled"]["%s|%s" % (a, k)] = {"pairs": len(ds), "points": 100 * obs, "p": (1 + sum(abs(v) >= abs(obs) for v in null)) / (B + 1)}
    L = ["# In-context strategies on Spider 2.0-lite, SQLite tasks (`specbridge.comm.transfer.spider2`)\n",
         "%d tasks; %d accept >= 2 mutually distinct gold answers. Tasks with all strategies saved. Cells: count (gain/loss vs placebo, "
         "exact McNemar p). Strategies: %s.\n" % (len(T), len(multi), ", ".join(ARMS))]
    for k, name, _ in MET:
        L += ["## %s\n" % name, "| solver | tasks | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)]
        for m, x in res["models"].items():
            c = x["metrics"][k]
            L.append("| %s | %d | " % (m, c["n"]) + " | ".join("%d" % c[a]["count"] if a == "placebo" else "%d (+%d/-%d, %.2g)" % (c[a]["count"], c[a]["gain"], c[a]["loss"], c[a]["p"]) for a in ARMS) + " |")
        L.append("| pooled vs placebo | | | " + " | ".join("%+.1f pts (p %.4f)" % (res["pooled"]["%s|%s" % (a, k)]["points"], res["pooled"]["%s|%s" % (a, k)]["p"])
                                                      if "%s|%s" % (a, k) in res["pooled"] else "" for a in ARMS[1:]) + " |\n")
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(OUT + "/results.json", "w"), indent=1); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n")
    if not quiet: print("\n".join(L))

if __name__ == "__main__":
    {"run": lambda: run(sys.argv[2:] or MODELS), "report": report}[sys.argv[1]]()
