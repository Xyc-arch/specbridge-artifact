"""THE AMBIGUITY LIBRARY AS RULES (2026-10-12): SQL construct -> the choice it settles -> an exact edit producing the other reading,
with priors mined from TRAINING golds only (never from dev / held-out / test tasks).
Each rule detects SITES in a query (sqlglot AST), says which SIDE the query takes at each site, and edits the site to the other side.
    ties          ORDER BY e LIMIT k  (one row at the cut)          -> keep every row tied at the cut (RANK() <= k)
    count_unit    COUNT(x) (rows)  <->  COUNT(DISTINCT x) (entities)
    join_kind     INNER JOIN (drop unmatched)  <->  LEFT JOIN (keep unmatched)
    null_filter   ORDER BY c LIMIT without c IS NOT NULL  <->  with it
    division      a / b without a real cast (integer division)  <->  CAST(a AS REAL) / b
    dedup         SELECT (duplicates kept)  <->  SELECT DISTINCT
    boundary      x > c / x < c (strict)  <->  x >= c / x <= c (inclusive)
    python -m specbridge.comm.diagnose.rules mine         -> out/rules/priors.json, MINE.md   (Spider train: execute; BIRD train: syntax)
    python -m specbridge.comm.diagnose.rules disagree     -> base SQL vs gold side on BIRD hold + hold2 (libctx plain answers)
    python -m specbridge.comm.diagnose.rules coverage     -> variants of saved base answers vs N samples at equal count"""
import collections, json, os, random, re, sqlite3, sys, time
import sqlglot
from sqlglot import exp

OUT = "out/rules"; SPIDER = "spider_data/spider_data"; SEED = 20261019
RULES = ["ties", "count_unit", "join_kind", "null_filter", "division", "dedup", "boundary"]


def _real(x):
    """A real-valued operand: CAST(.. AS REAL/FLOAT/DOUBLE/NUMERIC), a * 1.0 product, or a real literal."""
    if isinstance(x, exp.Cast): return x.to.this in (exp.DataType.Type.FLOAT, exp.DataType.Type.DOUBLE, exp.DataType.Type.DECIMAL)
    if isinstance(x, exp.Mul): return any(isinstance(y, exp.Literal) and "." in y.name for y in (x.this, x.expression))
    return isinstance(x, exp.Literal) and "." in x.name


def parse(sql):
    try: return sqlglot.parse_one(sql, read="sqlite")
    except Exception: return None


def _top(q):
    return q if isinstance(q, exp.Select) else None


# --- sites: (rule, side, path) where path locates the node in a fresh parse -------------------------------------------------
def sites(sql):
    q = parse(sql)
    if q is None: return []
    out = []
    for i, n in enumerate(q.walk()):
        node = n
        if isinstance(node, exp.Count):
            a = node.this
            if isinstance(a, exp.Distinct): out.append(("count_unit", "entities", i))
            elif a is not None and not isinstance(a, exp.Star): out.append(("count_unit", "rows", i))
        elif isinstance(node, exp.Join):
            side = (node.args.get("side") or "").upper()
            if side == "LEFT": out.append(("join_kind", "keep_unmatched", i))
            elif side in ("", "INNER") and not (node.args.get("kind") or "").upper() == "CROSS" and node.args.get("on") is not None: out.append(("join_kind", "drop_unmatched", i))
        elif isinstance(node, exp.Div):
            casted = any(_real(x) for x in (node.this, node.expression))
            out.append(("division", "real" if casted else "integer", i))
        elif isinstance(node, (exp.GT, exp.LT)) and isinstance(node.expression, exp.Literal): out.append(("boundary", "strict", i))
        elif isinstance(node, (exp.GTE, exp.LTE)) and isinstance(node.expression, exp.Literal): out.append(("boundary", "inclusive", i))
        elif isinstance(node, exp.Select):
            lim = node.args.get("limit"); order = node.args.get("order")
            if node.args.get("distinct"): out.append(("dedup", "distinct", i))
            elif node.args.get("joins") and not any(isinstance(x, exp.AggFunc) for x in node.expressions for x in x.walk()) and not node.args.get("group"):
                out.append(("dedup", "duplicates", i))
            if lim is not None and order is not None and len(order.expressions) == 1:
                try: k = int(lim.expression.name)
                except Exception: k = None
                if k is not None and k <= 10:
                    out.append(("ties", "cut", i))
                    key = order.expressions[0].this; w = node.args.get("where")
                    filt = w is not None and any(isinstance(x, exp.Not) and isinstance(x.this, exp.Is) and x.this.this.sql() == key.sql() for x in w.walk())
                    if isinstance(key, exp.Column): out.append(("null_filter", "filtered" if filt else "unfiltered", i))
    return out


def edit(sql, site):
    """The query with ONE site moved to the other side; None when the edit cannot be made."""
    rule, side, idx = site; q = parse(sql)
    if q is None: return None
    node = list(q.walk())[idx]
    try:
        if rule == "count_unit":
            a = node.this; node.set("this", a.expressions[0] if side == "entities" else exp.Distinct(expressions=[a.copy()]))
        elif rule == "join_kind":
            node.set("side", "INNER" if side == "keep_unmatched" else "LEFT"); node.set("kind", None)
        elif rule == "division":
            if side == "integer": node.set("this", exp.Cast(this=node.this.copy(), to=exp.DataType.build("REAL")))
            else:
                for arg in ("this", "expression"):
                    x = node.args[arg]
                    if isinstance(x, exp.Cast) and _real(x): node.set(arg, x.this.copy())
                    elif isinstance(x, exp.Mul) and _real(x): node.set(arg, x.expression.copy() if isinstance(x.this, exp.Literal) else x.this.copy())
        elif rule == "boundary":
            m = {exp.GT: exp.GTE, exp.LT: exp.LTE, exp.GTE: exp.GT, exp.LTE: exp.LT}[type(node)]
            node.replace(m(this=node.this.copy(), expression=node.expression.copy()))
        elif rule == "dedup":
            node.set("distinct", None if side == "distinct" else exp.Distinct())
        elif rule == "null_filter":
            key = node.args["order"].expressions[0].this
            if side == "unfiltered": node.where(exp.Not(this=exp.Is(this=key.copy(), expression=exp.Null())), copy=False)
            else:
                w = node.args["where"].this
                preds = [p for p in (w.flatten() if isinstance(w, exp.And) else [w]) if not (isinstance(p, exp.Not) and isinstance(p.this, exp.Is) and p.this.this.sql() == key.sql())]
                node.set("where", exp.Where(this=exp.and_(*preds)) if preds else None)
        elif rule == "ties":
            o = node.args["order"].expressions[0]; k = int(node.args["limit"].expression.name); inner = node.copy()
            inner.set("order", None); inner.set("limit", None)
            outs = [e.copy() for e in inner.expressions]; names = ["c%d" % j for j in range(len(outs))]
            inner.set("expressions", [exp.alias_(e, n) for e, n in zip(outs, names)] +
                      [exp.alias_(exp.Window(this=exp.Anonymous(this="RANK"), order=exp.Order(expressions=[o.copy()])), "__r")])
            new = exp.select(*names).from_(exp.Subquery(this=inner, alias=exp.TableAlias(this=exp.to_identifier("__t")))).where("__r <= %d" % k)
            if node is q: return new.sql(dialect="sqlite")
            node.replace(new)
        else: return None
        return q.sql(dialect="sqlite")
    except Exception: return None


def alternative_ok(sql, site, db=None):
    """Whether the edit at SITE yields a valid other reading, decided on the query (and, for joins under an aggregate, on the
    database DB). Author review 2026-10-25 (human_supervision/bird-other-reading.csv): every rejected edit broke one of these.
      count_unit  only rows -> entities (removing DISTINCT counts join copies, never a reading of "how many X"); inside a
                  division only when the other side already counts distinct values (else the ratio mixes units)
      join_kind   the joined table supplies an output column and appears in no condition, grouping or ordering (otherwise the
                  join IS a condition, and keeping unmatched rows drops it); under an aggregate its join key must be unique in
                  the database, so keeping unmatched rows adds no copies"""
    rule, side, idx = site; q = parse(sql)
    if q is None: return False
    node = list(q.walk())[idx]
    if rule == "count_unit":
        if side != "rows": return False
        d = node.find_ancestor(exp.Div)
        if d is None: return True
        other = d.expression if any(x is node for x in d.this.walk()) else d.this
        return any(isinstance(c.this, exp.Distinct) for c in other.find_all(exp.Count))
    if rule == "join_kind":
        t = node.this; sel = node.find_ancestor(exp.Select)
        if not isinstance(t, exp.Table) or sel is None: return False
        alias = (t.alias_or_name or "").lower(); own = lambda c: (c.table or "").lower() == alias
        projected = under_agg = False
        for c in sel.find_all(exp.Column):
            if not own(c) or c.find_ancestor(exp.Join) is not None: continue
            top = c
            while top.parent is not None and top.parent is not sel: top = top.parent
            if top not in sel.expressions: return False
            projected = True; under_agg |= c.find_ancestor(exp.AggFunc) is not None
        if not projected: return False
        if under_agg or any(isinstance(x, exp.AggFunc) for e in sel.expressions for x in e.walk()):
            keys = [c.name for c in (node.args.get("on") or exp.Null()).find_all(exp.Column) if own(c)]
            if db is None or not keys: return False
            r = run(db, 'SELECT COUNT(*) = COUNT(DISTINCT "%s") FROM "%s" WHERE "%s" IS NOT NULL' % (keys[0], t.name, keys[0]))
            return bool(r and r[0][0])
        return True
    return True


def edit_ok(item):
    """alternative_ok for a saved item {"gold0": reference, "gold": edited reference, "rule", "path"}: the site whose edit
    reproduces the edited reference must pass."""
    for st in sites(item["gold0"]):
        if st[0] != item["rule"]: continue
        e = edit(item["gold0"], st)
        if e and parse(e).sql() == parse(item["gold"]).sql(): return alternative_ok(item["gold0"], st, item["path"])
    return False


def run(db, sql, timeout=20):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); t0 = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - t0 > timeout else 0, 100000)
    try: return con.execute(sql).fetchall()
    except Exception: return None
    finally: con.close()


def same(a, b): return a is not None and b is not None and set(map(tuple, a)) == set(map(tuple, b))


# --- (1) mine priors from training golds -----------------------------------------------------------------------------------
def mine(n_spider=2500, workers=6):
    import concurrent.futures as cf
    T = [(r["db_id"], r["query"]) for f in ("train_spider.json", "train_others.json") for r in json.load(open("%s/%s" % (SPIDER, f)))]
    random.Random(SEED).shuffle(T); T = T[:n_spider]
    def one(x):
        db, sql = x; path = "%s/database/%s/%s.sqlite" % (SPIDER, db, db)
        if not os.path.exists(path): return []
        base = run(path, sql)
        if base is None: return []
        rec = []
        for s in sites(sql):
            e = edit(sql, s); alt = run(path, e) if e else None
            rec.append({"rule": s[0], "gold_side": s[1], "edit_ok": alt is not None, "changes": alt is not None and not same(base, alt)})
        return rec
    R = collections.defaultdict(list)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for rs in ex.map(one, T):
            for r in rs: R[r["rule"]].append(r)
    B = collections.defaultdict(collections.Counter)                       # BIRD train: syntax only (its databases are not local)
    for r in json.load(open("train_meta/train.json")):
        for s in sites(r["SQL"]): B[s[0]][s[1]] += 1
    res = {"spider_train_queries": len(T), "rules": {}}
    L = ["# Rule priors from training golds (`specbridge.comm.diagnose.rules mine`)\n",
         "Spider train (seeded %d queries; executed): sites, share where the edit runs and CHANGES the answer, the gold's side among "
         "sites where it changes. BIRD train (9,428 queries): syntax only -- sites and the gold's side.\n" % len(T),
         "| rule | Spider sites | edit runs | edit changes answer | gold side when it changes | BIRD sites | BIRD gold side |", "|---|---|---|---|---|---|---|"]
    for k in RULES:
        rs = R.get(k, []); ch = [r for r in rs if r["changes"]]; gs = collections.Counter(r["gold_side"] for r in ch)
        res["rules"][k] = {"spider_sites": len(rs), "edit_runs": sum(r["edit_ok"] for r in rs), "changes": len(ch), "gold_side_when_changes": dict(gs), "bird_sides": dict(B[k])}
        L.append("| %s | %d | %d | %d (%.0f%%) | %s | %d | %s |" % (k, len(rs), sum(r["edit_ok"] for r in rs), len(ch), 100 * len(ch) / max(1, len(rs)),
                 ", ".join("%s %d" % kv for kv in gs.most_common()), sum(B[k].values()), ", ".join("%s %d" % kv for kv in B[k].most_common())))
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(OUT + "/priors.json", "w"), indent=1); open(OUT + "/MINE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


# --- priors: P(the gold takes `side`) per rule, per benchmark family --------------------------------------------------------
OTHER = {"cut": "all_ties", "rows": "entities", "entities": "rows", "drop_unmatched": "keep_unmatched", "keep_unmatched": "drop_unmatched",
         "unfiltered": "filtered", "filtered": "unfiltered", "integer": "real", "real": "integer", "duplicates": "distinct",
         "distinct": "duplicates", "strict": "inclusive", "inclusive": "strict"}


def prior(rule, target, family):
    P = json.load(open(OUT + "/priors.json"))["rules"][rule]
    c = P["gold_side_when_changes"] if family == "spider" and P["changes"] else P["bird_sides"]
    tot = sum(c.values()); return (c.get(target, 0) + 0.5) / (tot + 1.0)     # smoothed; 'all_ties' is never detected -> small


def variants(sql, family):
    """Every single-site edit of `sql`, ranked by the prior that the gold takes the edited side."""
    out = []
    for st in sites(sql):
        if st[0] == "dedup": continue                                         # set comparison: never changes a graded answer
        e = edit(sql, st)
        if e and e != sql: out.append((prior(st[0], OTHER[st[1]], family), st[0], e))
    return [x for x in sorted(out, key=lambda x: -x[0])]


# --- (1b) base SQL vs gold side, BIRD hold + hold2 ---------------------------------------------------------------------------
def disagree(models=("haiku", "gpt-6-luna", "gpt-6-sol", "sonnet")):
    from specbridge.comm.diagnose import libctx as LC
    from specbridge.comm.common import grade as G
    C = collections.defaultdict(collections.Counter)
    for sp in ("hold", "hold2"):
        for t in LC.split(sp):
            gs = [x for x in sites(t["reference_sql"]) if x[0] != "dedup"]; matter = []
            for x in gs:
                e = edit(t["reference_sql"], x); alt = run(t["snapshot"], e) if e else None
                if alt is not None and not G.bird_ex(t["reference_answer"], alt): matter.append(x)
            for m in models:
                f = "%s/%s.json" % (LC._out(sp, 1, "plain", m), t["id"])
                if not os.path.exists(f): continue
                o = json.load(open(f)); ms = sites(o.get("final") or "") if o.get("final") else []
                for rule, side, _i in matter:
                    sides_m = {sd for r_, sd, _ in ms if r_ == rule}; c = C[(m, rule)]; c["gold_site_matters"] += 1
                    if sides_m and side not in sides_m: c["model_other_side"] += 1; c["other_side_and_wrong"] += (not o.get("pass"))
    L = ["# Base SQL vs the gold's side at sites where the choice changes the answer (BIRD hold + hold2, plain)\n",
         "| solver | rule | gold sites that matter | model takes the other side | ... and is wrong |", "|---|---|---|---|---|"]
    for (m, rule), c in sorted(C.items()): L.append("| %s | %s | %d | %d | %d |" % (m, rule, c["gold_site_matters"], c["model_other_side"], c["other_side_and_wrong"]))
    open(OUT + "/DISAGREE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


# --- (2) coverage: rule variants of the saved base answer vs extra samples, at equal count -----------------------------------
def coverage():
    from specbridge.comm.diagnose import libctx as LC
    from specbridge.comm.common import grade as G
    from specbridge.comm.transfer import spider2 as S2, rgv as RG
    L = ["# Coverage: rule variants of the base answer vs extra samples at equal count (`rules coverage`)\n",
         "Right = some answer in the set matches the gold. +2 variants = the base plus its two highest-prior single-site edits; +2 samples = "
         "the base plus two more samples of the same prompt; all variants = the base plus every edit (count in brackets).\n",
         "| set | solver | n | base | +2 variants | +2 samples | all variants [mean count] | variants right where base wrong |", "|---|---|---|---|---|---|---|---|"]
    res = {}
    for m in ("haiku", "sonnet"):                                              # BIRD hold: libctx plain, plain_s2, plain_s3
        rows = []
        for t in LC.split("hold"):
            fs = ["%s/%s.json" % (LC._out("hold", 1, v, m), t["id"]) for v in ("plain", "plain_s2", "plain_s3")]
            if not all(os.path.exists(f) for f in fs): continue
            O = [json.load(open(f)) for f in fs]
            if not all("pass" in o for o in O): continue
            V = variants(O[0].get("final") or "", "bird") if O[0].get("final") else []
            ok = [bool(G.bird_ex(t["reference_answer"], a)) if a is not None else False for a in (run(t["snapshot"], e) for _p, _r, e in V)]
            rows.append({"base": bool(O[0]["pass"]), "v2": bool(O[0]["pass"]) or any(ok[:2]), "s2": any(bool(o["pass"]) for o in O), "vall": bool(O[0]["pass"]) or any(ok), "nv": len(V),
                         "rescue": (not O[0]["pass"]) and any(ok)})
        res[("bird", m)] = rows
    S = S2.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S2.GOLD + "/spider2lite_eval.jsonl")}; rows = []
    for iid in RG.pick()[0]:                                                   # Spider 2.0 pilot tasks (dev): rgv sample3, Sonnet
        fs = [RG._f("sample3", "sonnet", iid, k) for k in range(3)]
        if not all(os.path.exists(f) for f in fs): continue
        A = [json.load(open(f))["answers"] for f in fs]; base = A[0][0] if A[0] else None
        if base is None: continue
        G2, io = S2.golds(iid, E); V = variants(base["sql"], "spider")
        ok = [bool(S2.matches(S2.run_sql(S[iid]["db"], e), G2, io)) for _p, _r, e in V]
        b = bool(base["matches"]); s2 = b or any(a and a[0]["matches"] for a in A[1:])
        rows.append({"base": b, "v2": b or any(ok[:2]), "s2": s2, "vall": b or any(ok), "nv": len(V), "rescue": (not b) and any(ok)})
    res[("spider2", "sonnet")] = rows
    for (fam, m), rows in res.items():
        n = len(rows); c = lambda k: sum(r[k] for r in rows)
        L.append("| %s | %s | %d | %d | %d | %d | %d [%.1f] | %d |" % ("BIRD hold" if fam == "bird" else "Spider 2.0 pilot", m, n, c("base"), c("v2"), c("s2"), c("vall"), sum(r["nv"] for r in rows) / max(1, n), c("rescue")))
    open(OUT + "/COVERAGE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"mine": lambda: mine(), "disagree": lambda: disagree(), "coverage": lambda: coverage()}[sys.argv[1]]()
