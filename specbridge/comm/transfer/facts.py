"""DECISION-RELEVANT DATA FACTS, BY CODE (2026-10-13). Grounding redesigned around the library's choice types: each fact is a
property of the data that decides between two readings, computed from the database (no model, no gold) and shown only when it is
consequential. Database-level facts are cached per database file; request-level facts (term matches) are computed per request.
  MAPPING facts   a request term matching stored values in SEVERAL columns; the stored form of request terms
  CHOICE facts    join fan-out (> 1.1 rows per key); unmatched-row share per join (> 1%); NULL share of measure columns (> 1%);
                  real ties at the extreme of ranking candidates; low-cardinality flag/status columns with minority values
                  (>= 2%); fields cumulative within groups (non-decreasing in >= 95% of groups, over time); date coverage and gaps
    facts(dbpath, request, kinds=("mapping", "choice")) -> text block (empty when nothing is consequential)
    tables_for(dbpath, request) -> the relevant tables (request words vs names, plus foreign-key neighbours)"""
import collections, hashlib, json, os, re, sqlite3, time

CACHE = "out/facts"
GENERIC = {"other", "two", "one", "three", "first", "last", "year", "years", "month", "months", "day", "days", "most", "least", "common",
           "different", "each", "total", "number", "average", "count", "value", "values", "type", "types", "name", "names", "all", "any",
           "per", "with", "from", "for", "and", "the", "that", "which", "their", "there", "than", "more", "less", "top", "high", "low", "new",
           "show", "list", "find", "give", "what", "how", "many", "much", "where", "who", "when", "into", "based", "only", "also", "please"}


def _words(s): return {w for w in re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", s or "").lower().replace("_", " ")) if len(w) > 2}


def _con(dbpath, limit=10):
    con = sqlite3.connect("file:%s?mode=ro" % dbpath, uri=True); t0 = [time.time()]
    con.set_progress_handler(lambda: 1 if time.time() - t0[0] > limit else 0, 100000); return con, t0


def _q1(con, t0, sql):
    t0[0] = time.time()
    try: return con.execute(sql).fetchone()
    except Exception: return None


def _qa(con, t0, sql):
    t0[0] = time.time()
    try: return con.execute(sql).fetchall()
    except Exception: return None


def schema(con):
    tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    cols = {t: [(r[1], (r[2] or "").upper()) for r in con.execute('PRAGMA table_info("%s")' % t)] for t in tabs}
    fks = [(t, r[3], r[2], r[4]) for t in tabs for r in con.execute('PRAGMA foreign_key_list("%s")' % t)]      # (child, col, parent, pcol)
    names = collections.defaultdict(list)                        # undeclared links: same column name ending in id/key/code
    for t in tabs:
        for c, _ty in cols[t]:
            if re.search(r"(id|key|code)$", c.lower()): names[c.lower()].append((t, c))
    for _n, tc in names.items():
        for (a, ca), (b, cb) in zip(tc, tc[1:]):
            if not any({x[0], x[2]} == {a, b} for x in fks): fks.append((a, ca, b, cb))
    return tabs, cols, fks


def numeric(ty): return any(k in ty for k in ("INT", "REAL", "NUM", "FLOA", "DOUB", "DEC"))


def idlike(c): return bool(re.search(r"(^id$|_id$|id$|_code$|code$|_no$|_num$|number$|_key$|key$|^index$)", c.lower()))


def tables_for(dbpath, request, k=5):
    con, _t0 = _con(dbpath); tabs, cols, fks = schema(con); con.close(); q = _words(request) - GENERIC
    score = {t: 2 * len(_words(t) & q) + sum(len(_words(c) & q) for c, _ty in cols[t]) for t in tabs}
    rel = [t for t in sorted(tabs, key=lambda t: -score[t]) if score[t] > 0][:k]
    nb = [x for t in rel for f in fks for x in (f[0], f[2]) if t in (f[0], f[2]) and x not in rel and x in cols]   # a declared key may name a missing table
    return rel + [t for t in dict.fromkeys(nb)][:2]


def _db_facts(dbpath):
    """Database-level choice facts for every table (cached per database file)."""
    os.makedirs(CACHE, exist_ok=True); st = os.stat(dbpath)
    f = "%s/%s.json" % (CACHE, hashlib.sha1(("%s|%d|%d" % (dbpath, st.st_size, int(st.st_mtime))).encode()).hexdigest()[:16])
    if os.path.exists(f): return json.load(open(f))
    con, t0 = _con(dbpath); tabs, cols, fks = schema(con); F = collections.defaultdict(list)
    n = {t: (_q1(con, t0, 'SELECT COUNT(*) FROM "%s"' % t) or [0])[0] or 0 for t in tabs}
    for c, cc, p, pc in fks:                                         # fan-out and unmatched rows per join
        if c not in cols or p not in cols or not n.get(c) or not n.get(p) or not pc: continue
        r = _q1(con, t0, 'SELECT AVG(k), MAX(k) FROM (SELECT COUNT(*) AS k FROM "%s" WHERE "%s" IS NOT NULL GROUP BY "%s")' % (c, cc, cc))
        if r and r[0] and r[0] > 1.1: F[c].append(F[p].append(None) or "joining %s to %s on %s.%s repeats each %s row: %.1f rows per key on average, up to %d" % (c, p, c, cc, p, r[0], r[1]))
        u = _q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" NOT IN (SELECT "%s" FROM "%s" WHERE "%s" IS NOT NULL)' % (p, pc, cc, c, cc))
        if u and u[0] and u[0] / n[p] > 0.01: F[p].append("%.0f%% of %s rows have no matching %s row (an inner join drops them)" % (100 * u[0] / n[p], p, c))
        d = _q1(con, t0, 'SELECT SUM("%s" IS NULL OR "%s" NOT IN (SELECT "%s" FROM "%s")) FROM "%s"' % (cc, cc, pc, p, c))
        if d and d[0] and d[0] / n[c] > 0.01: F[c].append("%.0f%% of %s rows have no %s match on %s (missing or dangling key)" % (100 * d[0] / n[c], c, p, cc))
    for t in tabs:
        if not n[t]: continue
        dates = []
        for c, ty in cols[t]:
            nn = _q1(con, t0, 'SELECT SUM("%s" IS NULL), COUNT(DISTINCT "%s") FROM "%s"' % (c, c, t))
            if not nn: continue
            share, dist = (nn[0] or 0) / n[t], nn[1] or 0
            if numeric(ty) and share > 0.01: F[t].append("%s.%s is NULL in %.0f%% of rows" % (t, c, 100 * share))
            if numeric(ty) and dist > 20 and not idlike(c):           # ties at the extreme of a ranking candidate
                for fn in ("MAX", "MIN"):
                    r = _q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" = (SELECT %s("%s") FROM "%s")' % (t, c, fn, c, t))
                    if r and r[0] and r[0] > 1: F[t].append("%d rows of %s tie at the %s of %s.%s" % (r[0], t, "largest" if fn == "MAX" else "smallest", t, c))
            if 2 <= dist <= 10 and not idlike(c):                     # flag / status column with a minority value
                vs = _qa(con, t0, 'SELECT "%s", COUNT(*) FROM "%s" GROUP BY 1 ORDER BY 2' % (c, t)) or []
                mino = [(v, k / n[t]) for v, k in vs if 0.02 <= k / n[t] <= 0.5 and v is not None]
                if mino and len(vs) <= 10: F[t].append("%s.%s takes %d values; minority: %s" % (t, c, len(vs), ", ".join("%r %.0f%%" % (v, 100 * s) for v, s in mino[:4])))
            if not numeric(ty):
                smp = _qa(con, t0, 'SELECT "%s" FROM "%s" WHERE "%s" IS NOT NULL LIMIT 20' % (c, t, c)) or []
                if smp and all(isinstance(v[0], str) and re.match(r"^\d{4}[-/]\d{2}", v[0]) for v in smp): dates.append(c)
        for c in dates[:2]:                                           # date coverage and gaps (months without rows)
            r = _qa(con, t0, 'SELECT substr("%s", 1, 7) FROM "%s" WHERE "%s" IS NOT NULL GROUP BY 1 ORDER BY 1' % (c, t, c))
            ms = [x[0] for x in (r or []) if isinstance(x[0], str) and re.match(r"^\d{4}[-/]\d{2}$", x[0])]   # numeric year-month only
            if len(ms) >= 2:
                y0, m0 = int(ms[0][:4]), int(ms[0][5:7]); y1, m1 = int(ms[-1][:4]), int(ms[-1][5:7]); span = (y1 - y0) * 12 + m1 - m0 + 1
                gap = span - len(ms)
                F[t].append("%s.%s runs from %s to %s%s" % (t, c, ms[0], ms[-1], "; %d of %d months have no rows" % (gap, span) if gap > 0 else ""))
        keys = [cc for ch, cc, _p, _pc in fks if ch == t]
        for k in keys[:1]:                                            # cumulative-looking fields within an entity, over time
            for c, ty in cols[t]:
                if not numeric(ty) or c == k or not dates: continue
                r = _q1(con, t0, 'SELECT AVG(ok) FROM (SELECT "%s" AS g, MIN(CASE WHEN d >= 0 THEN 1 ELSE 0 END) AS ok FROM (SELECT "%s", "%s" - LAG("%s") OVER (PARTITION BY "%s" ORDER BY "%s") AS d FROM "%s") WHERE d IS NOT NULL GROUP BY "%s")' % (k, k, c, c, k, dates[0], t, k))
                if r and r[0] is not None and r[0] >= 0.95: F[t].append("%s.%s never decreases within %s over %s: it looks cumulative (a running total), not a per-period value" % (t, c, k, dates[0]))
    con.close(); F = {t: [x for x in v if x][:6] for t, v in F.items()}; json.dump(F, open(f, "w"), indent=1); return F


def _mapping(dbpath, request, rel):
    con, t0 = _con(dbpath); tabs, cols, _fks = schema(con); q = _words(request) - GENERIC; hits = collections.defaultdict(set); forms = []
    for t in rel:
        for c, ty in cols[t]:
            if numeric(ty): continue
            vs = _qa(con, t0, 'SELECT DISTINCT "%s" FROM "%s" WHERE "%s" IS NOT NULL LIMIT 300' % (c, t, c)) or []
            if len(vs) >= 300: continue
            wc = collections.Counter(w for (v,) in vs if isinstance(v, str) for w in (_words(v) & q))
            for (v,) in vs:
                if not isinstance(v, str) or len(v) > 60: continue
                ws = _words(v) & q
                if ws and all(wc[w] <= 3 for w in ws):
                    for w in ws: hits[w].add("%s.%s" % (t, c))
                    if len(forms) < 20: forms.append("%s.%s = %r" % (t, c, v))
    con.close(); L = []
    multi = {w: cs for w, cs in hits.items() if len(cs) > 1}
    if multi: L.append("REQUEST TERMS FOUND IN SEVERAL COLUMNS: " + "; ".join("'%s' in %s" % (w, ", ".join(sorted(cs))) for w, cs in sorted(multi.items())))
    if forms: L.append("STORED FORM OF REQUEST TERMS: " + "; ".join(forms))
    return L


def facts(dbpath, request, kinds=("mapping", "choice")):
    rel = tables_for(dbpath, request); L = []
    if "mapping" in kinds: L += _mapping(dbpath, request, rel)
    if "choice" in kinds:
        F = _db_facts(dbpath); ch = list(dict.fromkeys(x for t in rel for x in F.get(t, [])))[:20]
        if ch: L.append("DATA FACTS THAT DECIDE BETWEEN READINGS:\n- " + "\n- ".join(ch))
    return ("RELEVANT TABLES: %s\n" % ", ".join(rel) + "\n".join(L)) if L else ""
