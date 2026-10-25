"""A DETERMINISTIC ANSWER LINTER FROM THE LIBRARY AND THE AUDIT (2026-10-13; v2 after out/linter/BAR.md).
OFFLINE, per database: a hotspot map (specbridge.comm.transfer.facts helpers) -- joins with fan-out > 1.1, joins that drop > 5% of
rows, measure columns > 5% NULL, ranking columns tied at the top, flag/status columns with a minority >= 2%. Flags have no library
edit: they are mapped but cannot trigger. HABITS: per choice type, the side that past queries choose (BIRD train references,
out/rules/priors.json); any other set of past queries can be summarised the same way (`habits(sqls)`).
RUNTIME, on one model SQL: parse; find the library rule sites (specbridge.comm.diagnose.rules) that touch a hotspot; apply the edit;
execute both; keep the DECISIVE site (the edit that moves the answer most) and WARN with both answers, the clause, and the habit
hint, when a single value moves > 10%, the top-1 item or the top-k set changes, or the row set changes; otherwise stay silent.
Count edits are never made on a GROUP BY key, never when the question names the counted unit, and an alternative that is empty,
all NULL or turns a column into constant 1 is rejected.
EVALUATION on the saved Sonnet and GPT-Sol answers to the 600 BIRD dev questions (out/prior/bird600, plain): see BAR.md.
    python -m specbridge.report.linter run | judge | report   -> out/linter/"""
import collections, concurrent.futures as cf, csv, json, math, os, random, re, sys, time
from sqlglot import exp
from specbridge.comm.diagnose import rules as RU, inclination as I
from specbridge.comm.transfer import facts as FA
from specbridge.comm.common import db as DB, grade as G
from specbridge.report import impact as IM

OUT = "out/linter"; SEED = 20261025; MODELS = ("sonnet", "gpt_6_sol")
KIND_TO_INCL = {"ties": "ties_and_selection", "count_unit": "counting_unit", "join_kind": "population_scope", "null_filter": "missing_values"}
NAME = {"ties": "ties at the top of a ranking", "count_unit": "counting rows or distinct entities over a fan-out join",
        "join_kind": "keeping or dropping unmatched rows", "null_filter": "rows with missing values in a sort column"}
SIDE = {"rows": "count every joined row", "entities": "count each entity once", "drop_unmatched": "drop rows without a match",
        "keep_unmatched": "keep rows without a match", "unfiltered": "keep rows with a missing sort value", "filtered": "drop rows with a missing sort value", "cut": "cut at the limit"}


def habits(side_counts=None, share=0.8):
    """{rule: (side, share, n)} for rules where one side has >= share of past sites and the other side was observed."""
    if side_counts is None: side_counts = {k: v["bird_sides"] for k, v in json.load(open("out/rules/priors.json"))["rules"].items()}
    out = {}
    for r, c in side_counts.items():
        n = sum(c.values())
        if len(c) < 2 or not n: continue
        s, k = max(c.items(), key=lambda x: x[1])
        if k / n >= share: out[r] = (s, round(k / n, 3), n)
    return out


def summarise(sqls):
    """Habits from any list of past SQL queries (an organisation's own log): side counts per rule."""
    c = collections.defaultdict(collections.Counter)
    for s in sqls:
        for r, side, _i in RU.sites(s): c[r][side] += 1
    return habits({r: dict(v) for r, v in c.items()})


def hotspots(path):
    f = "%s/hotspots/%s.json" % (OUT, os.path.basename(path)[:-7])
    if os.path.exists(f): return json.load(open(f))
    con, t0 = FA._con(path, 15); tabs, cols, fks = FA.schema(con); H = {"fanout": [], "drop": [], "null": [], "tie": [], "flag": []}
    n = {t: (FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s"' % t) or [0])[0] or 0 for t in tabs}
    for c, cc, p, pc in fks:
        if c not in cols or p not in cols or not n.get(c) or not n.get(p) or not pc: continue
        r = FA._q1(con, t0, 'SELECT AVG(k) FROM (SELECT COUNT(*) AS k FROM "%s" WHERE "%s" IS NOT NULL GROUP BY "%s")' % (c, cc, cc))
        if r and r[0] and r[0] > 1.1: H["fanout"].append([c, p, round(r[0], 2)])
        u = FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" NOT IN (SELECT "%s" FROM "%s" WHERE "%s" IS NOT NULL)' % (p, pc, cc, c, cc))
        if u and u[0] and u[0] / n[p] > 0.05: H["drop"].append([p, c, round(u[0] / n[p], 3)])
    for t in tabs:
        if not n[t]: continue
        for c, ty in cols[t]:
            r = FA._q1(con, t0, 'SELECT SUM("%s" IS NULL), COUNT(DISTINCT "%s") FROM "%s"' % (c, c, t))
            if not r: continue
            share, dist = (r[0] or 0) / n[t], r[1] or 0
            if FA.numeric(ty) and share > 0.05: H["null"].append([t, c, round(share, 3)])
            if not FA.idlike(c) and dist > 1:
                k = FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" = (SELECT MAX("%s") FROM "%s")' % (t, c, c, t))
                k2 = FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" = (SELECT MIN("%s") FROM "%s")' % (t, c, c, t))
                if (k and k[0] and k[0] > 1) or (k2 and k2[0] and k2[0] > 1): H["tie"].append([t, c])
            if 2 <= dist <= 10 and not FA.idlike(c):
                vs = FA._qa(con, t0, 'SELECT "%s", COUNT(*) FROM "%s" GROUP BY 1' % (c, t)) or []
                if any(v is not None and 0.02 <= k / n[t] <= 0.5 for v, k in vs): H["flag"].append([t, c])
    con.close(); os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(H, open(f, "w"), indent=1); return H


def _tables(q):
    return {(tb.alias_or_name or "").lower(): (tb.name or "").lower() for tb in q.find_all(exp.Table)}


def touched(q, site, H):
    """Does this rule site touch a hotspot? (names resolved through aliases; case-insensitive)"""
    al = _tables(q); T = set(al.values()); rule, _side, idx = site; node = list(q.walk())[idx]
    low = lambda xs: {tuple(str(v).lower() for v in x[:2]) for x in xs}
    fan, drop, nul, tie = low(H["fanout"]), low(H["drop"]), low(H["null"]), low(H["tie"])
    if rule == "join_kind":
        t = (node.this.name if isinstance(node.this, exp.Table) else "").lower()
        if any(t in pair and (pair - {t}) & T for pair in ({a, b} for a, b in fan | drop)): return "join"
    elif rule == "count_unit":
        if any(p in T and c in T for c, p in fan): return "fan-out under the count"
    elif rule in ("ties", "null_filter"):
        o = node.args.get("order")
        if o is None: return None
        key = {(al.get((c.table or "").lower(), (c.table or "").lower()), c.name.lower()) for c in o.find_all(exp.Column)}
        key = {(t or (next(iter(T)) if len(T) == 1 else ""), c) for t, c in key}
        if rule == "ties" and key & tie: return "tied sort column"
        if rule == "null_filter" and key & nul: return "NULL-heavy sort column"
    return None


def _words(s):
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s or ""); return {w for w in re.split(r"[^a-z]+", s.lower()) if len(w) > 2 and w not in ("id", "ids", "key", "num", "code")}


def _stem(w): return w[:-3] + "y" if w.endswith("ies") else w[:-1] if w.endswith("s") and not w.endswith("ss") else w


def count_ok(q, site, question):
    """Count edit allowed: not on a GROUP BY key, and the question does not name the counted unit."""
    node = list(q.walk())[site[2]]; a = node.this.expressions[0] if isinstance(node.this, exp.Distinct) else node.this
    sel = node.find_ancestor(exp.Select); g = sel.args.get("group") if sel else None
    if g is not None and isinstance(a, exp.Column) and any(isinstance(x, exp.Column) and x.name.lower() == a.name.lower() for x in g.expressions): return False
    al = _tables(q); unit = set()
    for c in a.find_all(exp.Column) if not isinstance(a, exp.Column) else [a]:
        unit |= _words(c.name) | _words(al.get((c.table or "").lower(), c.table or ""))
    if not unit and len(set(al.values())) >= 1: unit = set()
    unit = {_stem(w) for w in unit}
    for m in re.finditer(r"\b(how many|number of|count of|total|amount of)\s+((?:\w+\s+){0,3})", (question or "").lower()):
        if {_stem(w) for w in m.group(2).split()} & unit: return False
    return True


def degenerate(base, alt):
    """An alternative that is empty, all NULL, or turns a column into constant 1."""
    if not alt or all(v is None for r in alt for v in r): return True
    w = min(len(r) for r in alt)
    for j in range(w):
        col = [r[j] for r in alt]; bcol = [r[j] for r in base if len(r) > j]
        if all(v == 1 for v in col) and not all(v == 1 for v in bcol): return True
    return False


def _size(c, base, alt):
    if "value" in c: return min(c["value"], 1e6)
    a, b = {tuple(r) for r in base}, {tuple(r) for r in alt}
    return len(a ^ b) / max(1, len(a | b)) + (0.5 if c.get("top_item") else 0)


def lint(sql, path, H, question, HB=None):
    """The decisive warning for one model SQL, or None."""
    HB = habits() if HB is None else HB
    base = IM.run(path, sql); q = RU.parse(sql)
    if base is None or q is None: return None
    ordered = bool(re.search(r"\border\s+by\b", sql, re.I)); C = []
    for st in RU.sites(sql):
        if st[0] not in KIND_TO_INCL: continue
        h = touched(q, st, H)
        if not h or (st[0] == "count_unit" and not count_ok(q, st, question)): continue
        e = RU.edit(sql, st); alt = IM.run(path, e) if e else None
        if alt is None or (st[0] == "count_unit" and degenerate(base, alt)): continue
        c = IM.compare(base, alt, ordered)
        if c.get("value", 0) > 0.10 or c.get("top_item") or c.get("topk_set") or c["row_set"]:
            hb = HB.get(st[0]); other = [s for s in SIDE if s != st[1] and (st[0], s) in {("count_unit", "rows"), ("count_unit", "entities"), ("join_kind", "drop_unmatched"), ("join_kind", "keep_unmatched"), ("null_filter", "filtered"), ("null_filter", "unfiltered")}]
            C.append({"rule": st[0], "side": st[1], "alt_side": other[0] if other else None, "hotspot": h, "clause": list(q.walk())[st[2]].sql(dialect="sqlite")[:200], "alt_sql": e,
                      "change": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()}, "size": round(_size(c, base, alt), 4),
                      "habit": ({"side": hb[0], "share": hb[1], "n": hb[2], "model_follows": hb[0] == st[1]} if hb else None),
                      "base_head": str(base[:3])[:240], "alt_head": str(alt[:3])[:240], "base_rows": len(base), "alt_rows": len(alt)})
    return max(C, key=lambda w: w["size"]) if C else None


def message(w):
    """The text a user sees."""
    s = "This answer depends on a choice the request leaves open: %s (%s).\n  As written: %s -> %s\n  Other reading: %s -> %s" % (
        NAME[w["rule"]], w["clause"], SIDE.get(w["side"], w["side"]), w["base_head"], SIDE.get(w["alt_side"], "the other side"), w["alt_head"])
    if w["habit"]: s += "\n  Past queries on this source choose '%s' in %.0f%% of %d cases%s." % (SIDE[w["habit"]["side"]], 100 * w["habit"]["share"], w["habit"]["n"], "" if w["habit"]["model_follows"] else "; this answer does not")
    return s


def _tasks():
    from specbridge.comm.diagnose import prior as P
    return {t["id"]: t for t in P.tasks()}


def run(workers=6):
    T = _tasks(); HB = habits(); os.makedirs(OUT, exist_ok=True)
    for t in T.values(): hotspots(t["snapshot"])
    def one(j):
        m, k = j; f = "%s/runs/%s/%s.json" % (OUT, m, k)
        if os.path.exists(f): return
        o = json.load(open("out/prior/bird600/runs/%s/plain/%s.json" % (m, k))); t = T[k]; t0 = time.time()
        w = lint(o["final"], t["snapshot"], hotspots(t["snapshot"]), t["instruction"], HB) if o.get("final") else None
        hab = None
        if w and w["habit"] and not w["habit"]["model_follows"]:                     # the habit reading, graded like the plain answer
            a = DB.rows(DB.connect(t["snapshot"]), w["alt_sql"]); hab = {"pass": a is not None and G.bird_ex(t["reference_answer"], a)}
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"id": k, "model": m, "sql": o.get("final"), "pass": o.get("pass"), "warning": w, "habit_answer": hab, "seconds": round(time.time() - t0, 3)}, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, [(m, k) for m in MODELS for k in sorted(T)]))
    report()


JUDGE = """For each item: a data question (with its evidence), the SQL a model wrote, an ALTERNATIVE SQL that settles one choice the
other way, and the first rows of both. Would a careful analyst, reading only the question and evidence, accept the ALTERNATIVE as a
reading the user could have meant? yes | no. Answer ONLY JSON: [{"id": "...", "permitted": "yes|no", "why": "one sentence"}]

%s"""


def _warned():
    T = _tasks(); out = []
    for m in MODELS:
        for k in sorted(T):
            f = "%s/runs/%s/%s.json" % (OUT, m, k)
            if os.path.exists(f):
                o = json.load(open(f))
                if o["warning"]: out.append(("%s|%s" % (m, k), T[k], o))
    return out


def _item(key, t, o):
    w = o["warning"]
    return "--- %s\nQUESTION: %s\nCHOICE: %s\nMODEL SQL: %s\nMODEL ROWS: %s\nALTERNATIVE SQL: %s\nALTERNATIVE ROWS: %s" % (
        key, t["instruction"], NAME[w["rule"]], (o["sql"] or "")[:900], w["base_head"], (w["alt_sql"] or "")[:900], w["alt_head"])


def judge(batch=8):
    from specbridge.comm.common.llm import ask_json
    old = {"|".join(k.split("|")[:2]) for k in json.load(open(OUT + "/v1/sample50.json"))}
    Wn = [x for x in _warned() if x[0] not in old]; rng = random.Random(SEED); sample = rng.sample(Wn, min(50, len(Wn)))
    by = collections.Counter(x[2]["warning"]["rule"] for x in sample); rest = [x for x in Wn if x not in sample]; rng.shuffle(rest)
    topup = []
    for x in rest:                                                           # top up each type to >= 10 judged, per BAR.md
        r = x[2]["warning"]["rule"]
        if by[r] < 10: topup.append(x); by[r] += 1
    jf = OUT + "/judge.json"; J = json.load(open(jf)) if os.path.exists(jf) else {}
    todo = [x for x in sample + topup if x[0] not in J]
    def one(b):
        got = ask_json(JUDGE % "\n\n".join(_item(*x) for x in b), "opus", brace="[") or []
        return {g["id"]: g for g in got if isinstance(g, dict) and "id" in g}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for d in ex.map(one, [todo[i:i + batch] for i in range(0, len(todo), batch)]): J.update(d)
    json.dump(J, open(jf, "w"), indent=1); json.dump({"sample": [x[0] for x in sample], "topup": [x[0] for x in topup]}, open(OUT + "/sample.json", "w"), indent=1)
    with open(OUT + "/handcheck_15.csv", "w", newline="") as fh:
        wr = csv.writer(fh); wr.writerow(["key", "question", "choice", "model_sql", "model_rows", "alternative_sql", "alternative_rows", "LABEL permitted (yes/no)", "notes"])
        for key, t, o in sample[:15]: w = o["warning"]; wr.writerow([key, t["instruction"], NAME[w["rule"]], o["sql"], w["base_head"], w["alt_sql"], w["alt_head"], "", ""])
    report()


def _wilson(y, n, z=1.96):
    if not n: return (0, 0)
    p = y / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * max(0, c - h), 100 * min(1, c + h))


def _mcnemar(b, c):
    n = b + c
    if not n: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def report():
    T = _tasks(); W = _warned(); HB = habits()
    J = json.load(open(OUT + "/judge.json")) if os.path.exists(OUT + "/judge.json") else {}
    S = json.load(open(OUT + "/sample.json")) if os.path.exists(OUT + "/sample.json") else {"sample": [], "topup": []}
    imp = json.load(open("out/impact/impact.json"))["changed_questions"]["BIRD dev"]; imp = {"q%d" % x["id"]: set(x["rules"]) for x in imp if "q%d" % x["id"] in T}
    cue = lambda t, w: bool(I.CUES.get(KIND_TO_INCL[w["rule"]]) and I.CUES[KIND_TO_INCL[w["rule"]]].search(t["instruction"]))
    L = ["# Answer linter v2 on BIRD dev (`specbridge.report.linter`; bar: out/linter/BAR.md)\n",
         "Saved plain answers of Sonnet and GPT-Sol to the 600-question BIRD dev sample. One warning per answer, at the decisive site.\n",
         "Habits from BIRD train references: " + "; ".join("%s: %s (%.0f%% of %d)" % (NAME[r], SIDE[s], 100 * sh, n) for r, (s, sh, n) in HB.items() if r in KIND_TO_INCL) + "; ties: no habit (one side observable).\n",
         "| model | answers | with a warning | on wrong / right answers | false alarms (cue settles) | seconds per answer |", "|---|---|---|---|---|---|"]
    for m in MODELS:
        O = [json.load(open("%s/runs/%s/%s.json" % (OUT, m, k))) for k in sorted(T) if os.path.exists("%s/runs/%s/%s.json" % (OUT, m, k))]
        Wm = [o for o in O if o["warning"]]; fa = sum(cue(T[o["id"]], o["warning"]) for o in Wm)
        L.append("| %s | %d | %d (%.0f%%) | %d / %d | %d of %d (%.1f%%) | %.2f |" % (m, len(O), len(Wm), 100 * len(Wm) / max(1, len(O)), sum(not o["pass"] for o in Wm), sum(bool(o["pass"]) for o in Wm),
                 fa, len(Wm), 100 * fa / max(1, len(Wm)), sum(o["seconds"] for o in O) / max(1, len(O))))
    rules = sorted({x[2]["warning"]["rule"] for x in W})
    yes = lambda k: J.get(k, {}).get("permitted") == "yes"
    s = [k for k in S["sample"] if k in J]; y = sum(map(yes, s)); lo, hi = _wilson(y, len(s))
    fa_all = sum(cue(t, o["warning"]) for _k, t, o in W); fa_pct = 100 * fa_all / max(1, len(W))
    passed = len(s) >= 50 and 100 * y / max(1, len(s)) >= 70 and fa_pct <= 5
    L += ["", "**Overall bar:** precision on the fresh random 50 = %d of %d (%.0f%%, 95%% CI %.0f-%.0f); false alarms %d of %d warnings (%.1f%%). -> %s" % (
        y, len(s), 100 * y / max(1, len(s)), lo, hi, fa_all, len(W), fa_pct, "PASS" if passed else "FAIL"), "",
          "| choice | warnings (both models) | judged (random + top-up) | precision | 95% CI | false alarms | impact questions with this choice | covered (Sonnet / GPT-Sol) | kept by the bar |", "|---|---|---|---|---|---|---|---|---|"]
    kept = []
    for r in rules:
        Wr = [x for x in W if x[2]["warning"]["rule"] == r]; jr = [x[0] for x in Wr if x[0] in J and (x[0] in S["sample"] or x[0] in S["topup"])]
        yr = sum(map(yes, jr)); l2, h2 = _wilson(yr, len(jr)); far = sum(cue(t, o["warning"]) for _k, t, o in Wr)
        iq = [k for k, rs in imp.items() if r in rs]
        cov = ["%d" % sum(os.path.exists("%s/runs/%s/%s.json" % (OUT, m, k)) and (json.load(open("%s/runs/%s/%s.json" % (OUT, m, k)))["warning"] or {}).get("rule") == r for k in iq) for m in MODELS]
        ok = len(Wr) >= 10 and len(jr) >= 10 and yr / max(1, len(jr)) >= 0.7 and far / max(1, len(Wr)) <= 0.05
        if ok: kept.append(r)
        L.append("| %s | %d | %d | %d of %d (%.0f%%) | %.0f-%.0f | %d (%.0f%%) | %d | %s | %s |" % (NAME[r], len(Wr), len(jr), yr, len(jr), 100 * yr / max(1, len(jr)), l2, h2, far, 100 * far / max(1, len(Wr)), len(iq), " / ".join(cov), "yes" if ok else "no"))
    L += ["", "Kept types: %s." % (", ".join(NAME[r] for r in kept) or "none"), "", "## Habit hint (BAR: adopt only if McNemar p < 0.05 gain for both models)\n",
          "| model | warned answers against the habit | habit reading right, model wrong | model right, habit wrong | p | adopted |", "|---|---|---|---|---|---|"]
    adopt = []
    for m in MODELS:
        O = [json.load(open("%s/runs/%s/%s.json" % (OUT, m, k))) for k in sorted(T) if os.path.exists("%s/runs/%s/%s.json" % (OUT, m, k))]
        H = [o for o in O if o["habit_answer"] is not None]; b = sum(o["habit_answer"]["pass"] and not o["pass"] for o in H); c = sum(bool(o["pass"]) and not o["habit_answer"]["pass"] for o in H)
        p = _mcnemar(b, c); adopt.append(b > c and p < 0.05)
        L.append("| %s | %d | %d | %d | %.3f | %s |" % (m, len(H), b, c, p, "yes" if b > c and p < 0.05 else "no"))
    L += ["", "Habit hint: %s." % ("ADOPTED as the recommended main answer" if all(adopt) else "information only")]
    ex = [x for x in W if x[0] in S["sample"] and yes(x[0])][:2]
    L += ["", "## Two warnings as a user sees them\n"] + ["```\n%s\nQ: %s\n%s\n```" % (k, t["instruction"][:200], message(o["warning"])) for k, t, o in ex]
    os.makedirs(OUT, exist_ok=True); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "judge": judge, "report": report}[sys.argv[1]]()
