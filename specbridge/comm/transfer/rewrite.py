"""REWRITING vs EDITING A REQUEST (2026-10-13; gate: out/rewrite/GATE.md). For every reading of the 215 request sets and four
solvers, the same plain SQL prompt on three request texts: (a) the original specific request, (b) a DtP-style short interpretation
written by the solver (DtP's interpretation prompt, told the reading), (c) the open request verbatim + the reading description.
    python -m specbridge.comm.transfer.rewrite run | classify | report   -> out/rewrite/"""
import collections, concurrent.futures as cf, json, math, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X, ledger as LG, ambrosia as AM
from specbridge.comm.diagnose import rules as RU

CAP = 120                                          # readings per model (GATE.md amendment 22:15)
OUT = "out/rewrite"; MODELS = ("haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"); SEED = 20261026; VARIANTS = ("a", "b", "c", "d")
TELL = """

The question is meant in this way: {}
Write exactly ONE interpretation: the one with this meaning. One line, no explanation."""
CATS = ("filter", "time window", "exclusion", "grouping", "join", "output columns", "formula", "the choice", "other")
CLASSIFY = """Each item: a REFERENCE query and a model's ANSWER query for the same request, each given as an exact description (V) of
the SQL (or the SQL itself). The answer returns the wrong result. Name the ONE main requirement the answer lost or changed:
filter (a condition on which rows count) | time window (a date or period limit) | exclusion (a stated
exclusion such as 'ignore missing' or 'drop unmatched') | grouping (what is grouped by) | join (tables or join condition) | output columns (which or how
many columns) | formula (an aggregate or arithmetic expression) | the choice (it takes the other reading of: {choice}) | other.
Also give "dropped": the number of the item's LISTED SHARED REQUIREMENT that the answer violates (0 if none applies).
Answer ONLY JSON: [{{"id": "...", "lost": "<one category>", "dropped": <number>, "why": "one sentence"}}]

%s"""


def _f(m, k, x): f = "%s/runs/%s/%s__%s.json" % (OUT, m, k.replace(":", "__").replace("/", "_"), x); os.makedirs(os.path.dirname(f), exist_ok=True); return f


def _data():
    fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); return C, W


def run(workers=6, only=None):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    C, W = _data(); P = AM._dtp_prompts()
    def job(j):
        m, k, x = j; f = _f(m, k, x)
        if os.path.exists(f): return
        if only is not None and "%s|%s|%s" % (m, k, x) not in only: return
        with lock:
            p = k in second
            if only is None and started[(m, p)] >= (CAP2 if p else CAP): return
            started[(m, p)] += 1
        c = C[k]; w = W[k]; rd = w.get("reading_" + x); schema, docs = DB.context(c); con = DB.connect(c["snapshot"])
        if not rd: return
        out = {"case": k, "model": m, "reading": x, "description": rd}; order = list(VARIANTS); random.Random(hash((m, k, x)) & 0xffff).shuffle(order); calls = 0
        for v in order:
            if v == "a": req = w["precise_" + x]
            elif v == "c": req = w["open"].rstrip() + " " + rd
            else:
                t = ask(P["user_message_interpr_ambig"].format("DATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s" % (schema, docs), w["open"]) + TELL.format(rd), m, timeout=1500, quiet=True) or ""
                calls += 1; lines = [AM.item_line(s) for s in t.splitlines() if AM.item_line(s)]; req = lines[0] if lines else ""; raw_b = t
            sql = None
            if req:
                try: sql = (jparse(ask(X.PLAIN % (schema, docs, req), m, timeout=1500, quiet=True) or "", "{") or {}).get("sql")
                except Exception: sql = None
                calls += 1
            rows = DB.rows(con, sql) if sql else None
            out[v] = {"request": req, "sql": sql, "executes": rows is not None, "matches": X._match(c, rows) if rows is not None else []}
            if v == "b": out[v]["raw"] = raw_b
        out["calls"] = calls; json.dump(out, open(f, "w"), indent=1, default=str)
    # the readings of the first construction run in their seeded order (capped at CAP per model), then the filter sets' readings
    # at the same rate (CAP2 per model), so the first draw is unchanged
    from specbridge.comm.transfer import combined as CB
    second = set(CB.part_cases(1)); CAP2 = round(CAP * len(second) / len(CB.part_cases(0)))
    jobs = [(m, k, x) for k in CB.part_cases(0) for x in ("A", "B") for m in MODELS]; random.Random(SEED).shuffle(jobs)
    j2 = [(m, k, x) for k in sorted(second) for x in ("A", "B") for m in MODELS]; random.Random(SEED).shuffle(j2); jobs += j2
    import threading; lock = threading.Lock(); started = collections.Counter((m, k in second) for m, k, x in jobs if os.path.exists(_f(m, k, x)))
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(job, jobs))
    if only is None: classify(); report()


CONDENSE = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
Human: {}
Follow Up Input: {}
Standalone question:"""


def run_d(workers=6):
    """Arm (d) on the readings already run: the conversational-retrieval condense prompt, then the same SQL prompt."""
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    C, W = _data()
    def job(f):
        o = json.load(open(f))
        if "d" in o: return
        c = C[o["case"]]; w = W[o["case"]]; schema, docs = DB.context(c); con = DB.connect(c["snapshot"])
        t = (ask(CONDENSE.format(w["open"], o["description"]), o["model"], timeout=1500, quiet=True) or "").strip()
        req = t.split("Standalone question:")[-1].strip(); sql = None
        if req:
            try: sql = (jparse(ask(X.PLAIN % (schema, docs, req), o["model"], timeout=1500, quiet=True) or "", "{") or {}).get("sql")
            except Exception: sql = None
        rows = DB.rows(con, sql) if sql else None
        o["d"] = {"request": req, "sql": sql, "executes": rows is not None, "matches": X._match(c, rows) if rows is not None else []}
        o["calls"] = o.get("calls", 0) + 2; json.dump(o, open(f, "w"), indent=1, default=str)
    import glob
    fs = sorted(glob.glob(OUT + "/runs/*/*.json")); random.Random(SEED).shuffle(fs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(job, fs))


def _rows(part=0):
    """Accepted readings of one construction run: 0 = sets built without a filter (the primary result), 1 = the filter sets."""
    from specbridge.comm.transfer import reviewed as RV, combined as CB
    C, _W = _data(); keep = set(CB.part_cases(part)); C = {k: v for k, v in C.items() if RV.keep(k) and k in keep}; R = []
    for m in MODELS:
        for k in sorted(C):
            for x in ("A", "B"):
                f = _f(m, k, x)
                if os.path.exists(f): o = json.load(open(f)); R.append(dict(o, right={v: x in o[v]["matches"] for v in VARIANTS if v in o}))
    return R


def classify(batch=8):
    from specbridge.comm.common.llm import ask_json
    C, W = _data(); jf = OUT + "/classify.json"; J = json.load(open(jf)) if os.path.exists(jf) else {}
    items = [r for r in _rows() if r["right"]["a"] and not r["right"]["b"] and "%s|%s|%s" % (r["model"], r["case"], r["reading"]) not in J]
    def V(sql, c):
        if not sql: return "(no SQL)"
        return DB.explicit(sql, c["snapshot"], conventions=False) or "SQL: " + sql
    def one(b):
        body = "\n\n".join("--- %s|%s|%s\nLISTED SHARED REQUIREMENTS:\n%s\nREFERENCE: %s\nANSWER: %s" % (r["model"], r["case"], r["reading"],
            "\n".join("%d. %s" % (i + 1, q["requirement"]) for i, q in enumerate(W[r["case"]]["shared"])), V(C[r["case"]]["sql_" + r["reading"]], C[r["case"]])[:2500], V(r["b"]["sql"], C[r["case"]])[:2500]) for r in b)
        got = ask_json(CLASSIFY.replace("{choice}", "; ".join(sorted({C[r["case"]]["kind"] for r in b}))) % body, "opus", brace="[") or []
        return {g["id"]: g for g in got if isinstance(g, dict) and "id" in g}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for d in ex.map(one, [items[i:i + batch] for i in range(0, len(items), batch)]): J.update(d)
    json.dump(J, open(jf, "w"), indent=1)


def _mcnemar(b, c):
    n = b + c
    return 1.0 if not n else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def report():
    R = _rows(); J = json.load(open(OUT + "/classify.json")) if os.path.exists(OUT + "/classify.json") else {}
    L = ["# Rewriting vs editing a request (`specbridge.comm.transfer.rewrite`; gate: out/rewrite/GATE.md)\n",
         "Accuracy per reading: (a) original specific request, (b) solver's DtP-style interpretation, (c) open request + the reading description. Same plain SQL prompt.\n",
         "| model | readings | (a) | (b) | (c) | (c) - (a) | (b) - (a) | McNemar (b) vs (a): lost / gained, p | (c) vs (a): lost / gained, p | gate |", "|---|---|---|---|---|---|---|---|---|---|"]
    def line(name, rs):
        n = len(rs); acc = {v: 100 * sum(r["right"][v] for r in rs) / max(1, n) for v in "abc"}
        bl = sum(r["right"]["a"] and not r["right"]["b"] for r in rs); bg = sum(r["right"]["b"] and not r["right"]["a"] for r in rs)
        cl = sum(r["right"]["a"] and not r["right"]["c"] for r in rs); cg = sum(r["right"]["c"] and not r["right"]["a"] for r in rs)
        pb, pc = _mcnemar(bl, bg), _mcnemar(cl, cg); ok = abs(acc["c"] - acc["a"]) <= 3 and acc["a"] - acc["b"] >= 10 and pb < 0.05
        L.append("| %s | %d | %.1f | %.1f | %.1f | %+.1f | %+.1f | %d / %d, %.2g | %d / %d, %.2g | %s |" % (name, n, acc["a"], acc["b"], acc["c"], acc["c"] - acc["a"], acc["b"] - acc["a"], bl, bg, pb, cl, cg, pc, "PASS" if ok else "fail"))
    for m in MODELS: line(m, [r for r in R if r["model"] == m])
    line("pooled", R)
    L += ["", "Secondary tests (GATE.md amendment 22:25), exact McNemar on paired readings:", "", "| model | (c) - (b) | lost / gained, p | readings with (d) | (d) | (c) - (d) | lost / gained, p |", "|---|---|---|---|---|---|---|"]
    def sec(name, rs):
        n = len(rs); cb = 100 * (sum(r["right"]["c"] for r in rs) - sum(r["right"]["b"] for r in rs)) / max(1, n)
        l1 = sum(r["right"]["c"] and not r["right"]["b"] for r in rs); g1 = sum(r["right"]["b"] and not r["right"]["c"] for r in rs)
        rd = [r for r in rs if "d" in r["right"]]; nd = len(rd)
        acc_d = 100 * sum(r["right"]["d"] for r in rd) / max(1, nd); cd = 100 * (sum(r["right"]["c"] for r in rd) - sum(r["right"]["d"] for r in rd)) / max(1, nd)
        l2 = sum(r["right"]["c"] and not r["right"]["d"] for r in rd); g2 = sum(r["right"]["d"] and not r["right"]["c"] for r in rd)
        L.append("| %s | %+.1f | %d / %d, %.2g | %d | %.1f | %+.1f | %d / %d, %.2g |" % (name, cb, l1, g1, _mcnemar(l1, g1), nd, acc_d, cd, l2, g2, _mcnemar(l2, g2)))
    for m in MODELS: sec(m, [r for r in R if r["model"] == m])
    sec("pooled", R)
    lost = collections.Counter((J.get("%s|%s|%s" % (r["model"], r["case"], r["reading"])) or {}).get("lost", "unclassified") for r in R if r["right"]["a"] and not r["right"]["b"])
    tot = sum(lost.values())
    L += ["", "What (b) lost, on readings right under (a) and wrong under (b) (%d; Opus, V of reference vs V of answer): " % tot + ", ".join("%s %d (%.0f%%)" % (k, v, 100 * v / max(1, tot)) for k, v in lost.most_common()),
          "", "Request length (characters, mean): (a) %.0f, (b) %.0f, (c) %.0f. (b) answers that do not execute: %d of %d." % tuple(
              [sum(len(r[v]["request"] or "") for r in R) / max(1, len(R)) for v in "abc"] + [sum(not r["b"]["executes"] for r in R), len(R)])]
    F = _rows(1)                                                  # reported apart: readings of the filter sets
    L += ["", "## Filter sets (reported apart; %d readings)\n" % len(F), "| model | readings | (a) | (b) | (c) | (c) - (a) | (b) - (a) | McNemar (b) vs (a): lost / gained, p | (c) vs (a): lost / gained, p | gate |", "|---|---|---|---|---|---|---|---|---|---|"]
    line("pooled", F)
    L += ["", "| model | (c) - (b) | lost / gained, p | readings with (d) | (d) | (c) - (d) | lost / gained, p |", "|---|---|---|---|---|---|---|"]
    sec("pooled", F)
    ex = [r for r in R if r["right"]["a"] and not r["right"]["b"]][:2]
    L += ["", "## Two (b) rewrites that lost the answer\n"] + ["- %s, %s: (b) \"%s\" -- lost: %s" % (r["model"], r["case"][-10:], r["b"]["request"][:300], (J.get("%s|%s|%s" % (r["model"], r["case"], r["reading"])) or {}).get("why", "?")) for r in ex]
    open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


def detail(B=20000):
    """GATE.md amendment 22:45: (a)-(b) and (a)-(c) loss by the number of listed shared requirements (median split), one-sided
    permutation test on the difference of mean paired losses (labels permuted across readings)."""
    C, W = _data(); R = _rows(); n = {r["case"]: len(W[r["case"]]["shared"]) for r in R}; med = sorted(n.values())[len(n) // 2]
    L = ["", "## Loss by request detail (listed shared requirements; median %d; GATE.md amendment 22:45)\n" % med,
         "| model | readings, fewer / more | (a)-(b) loss, fewer | (a)-(b) loss, more | one-sided p | (a)-(c) loss, fewer | (a)-(c) loss, more | (a)-(d), fewer / more |", "|---|---|---|---|---|---|---|---|"]
    rng = random.Random(SEED)
    def row(name, rs):
        hi = [r for r in rs if n[r["case"]] > med]; lo = [r for r in rs if n[r["case"]] <= med]
        loss = lambda xs, v: 100 * sum(int(r["right"]["a"]) - int(r["right"].get(v, r["right"]["a"])) for r in xs) / max(1, len(xs))
        d = [int(r["right"]["a"]) - int(r["right"]["b"]) for r in rs]; lab = [n[r["case"]] > med for r in rs]
        obs = loss(hi, "b") - loss(lo, "b"); k = 0
        for _ in range(B):
            rng.shuffle(lab); h = [x for x, l in zip(d, lab) if l]; o = [x for x, l in zip(d, lab) if not l]
            k += (100 * sum(h) / max(1, len(h)) - 100 * sum(o) / max(1, len(o))) >= obs - 1e-9
        dl = [r for r in lo if "d" in r["right"]]; dh = [r for r in hi if "d" in r["right"]]
        L.append("| %s | %d / %d | %.1f | %.1f | %.3f | %.1f | %.1f | %.1f / %.1f |" % (name, len(lo), len(hi), loss(lo, "b"), loss(hi, "b"), k / B, loss(lo, "c"), loss(hi, "c"), loss(dl, "d"), loss(dh, "d")))
    for m in MODELS: row(m, [r for r in R if r["model"] == m])
    row("pooled", R)
    J = json.load(open(OUT + "/classify.json")) if os.path.exists(OUT + "/classify.json") else {}
    comp = collections.Counter()
    for r in R:
        g = J.get("%s|%s|%s" % (r["model"], r["case"], r["reading"])) or {}
        try: i = int(g.get("dropped") or 0)
        except Exception: i = 0
        if r["right"]["a"] and not r["right"]["b"] and 0 < i <= len(W[r["case"]]["shared"]): comp[W[r["case"]]["shared"][i - 1]["component"].split(" ")[0]] += 1
    L.append("\nListed requirement dropped by (b), by component: " + ", ".join("%s %d" % kv for kv in comp.most_common()))
    open(OUT + "/RESULTS.md", "a").write("\n".join(L) + "\n"); print("\n".join(L))


def run_s2(model="sonnet", workers=6):
    """Spider 2.0 (out/rewrite/spider2/GATE.md): PART B on all 135 tasks, PART A on the clarification instances."""
    from specbridge.comm.common.llm import call, parse
    from specbridge.comm.transfer import spider2 as S, ask as AK
    P = AM._dtp_prompts(); T = S.tasks(); E = AK._E(); D = json.load(open(AK.OUT + "/readings.json")); ctx = {}
    ids = sorted(i for i in T if os.path.exists("out/spider2/errors/plain/%s.json" % i)) or sorted(T)
    jobs = [("B", i, "") for i in ids] + [("A", i, r) for i in AK.tasks_meaning() if i in D for r in sorted(D[i])]; random.Random(SEED).shuffle(jobs)
    lock = __import__("threading").Lock()
    def C(db):
        with lock:
            if db not in ctx: ctx[db] = S.context(db)
        return ctx[db]
    def one(job):
        part, iid, rid = job; f = "%s/spider2/%s/%s/%s%s.json" % (OUT, model, part, iid, ("__" + rid) if rid else "")
        if os.path.exists(f): return
        t = T[iid]; sch = C(t["db"]); docs = S.docs(t); q = t["question"]; line = D[iid][rid] if rid else None
        def sql_for(req):
            txt = call(X.PLAIN % (sch, docs, req), model) if req else ""
            r = parse(txt or "", "{") or {}; df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
            G, io = S.golds(iid, E); return {"request": req, "sql": r.get("sql"), "runs": df is not None, "matches": S.matches(df, G, io) if df is not None else []}
        def first_line(t_): ls = [AM.item_line(x) for x in (t_ or "").splitlines() if AM.item_line(x)]; return ls[0] if ls else ""
        ctxt = "DATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s" % (sch, docs)
        texts = {}
        order = ["a" if part == "B" else "c", "b", "d"]; random.Random(hash(job) & 0xffff).shuffle(order); out = {"part": part, "task": iid, "reading": rid, "line": line}
        for v in order:
            if v == "a": req = q
            elif v == "c": req = q + "\nWhat I mean: " + line
            elif v == "b":
                tell = TELL.format(line) if line else "\n\nWrite exactly ONE interpretation: the most likely meaning. One line, no explanation."
                req = first_line(call(P["user_message_interpr_ambig"].format(ctxt, q) + tell, model))
            else:
                req = (call(CONDENSE.format(q, line or "Write the SQL for this."), model) or "").split("Standalone question:")[-1].strip()
            out[v] = sql_for(req)
        if part == "A":
            R, _G, _io = AK.readings(iid, E); js = set(R.get(rid, []))
            for v in ("c", "b", "d"): out[v]["right"] = bool(set(out[v]["matches"]) & js)
        else:
            for v in ("a", "b", "d"): out[v]["right"] = bool(out[v]["matches"])
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(out, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report_s2(model)


def report_s2(model="sonnet"):
    import glob
    L = ["# Rewriting vs editing on Spider 2.0-lite (gate: out/rewrite/spider2/GATE.md), %s\n" % model]
    for part, base, vs in (("B", "a", ("b", "d")), ("A", "c", ("b", "d"))):
        R = [json.load(open(f)) for f in glob.glob("%s/spider2/%s/%s/*.json" % (OUT, model, part))]; n = len(R)
        L.append("## Part %s (%d %s)\n" % (part, n, "tasks, any accepted answer" if part == "B" else "task-reading instances, that reading"))
        L.append("| text | right | vs (%s): lost / gained, p |" % base); L.append("|---|---|---|")
        L.append("| (%s) %s | %d / %d (%.1f%%) | |" % (base, "original task" if base == "a" else "task + clarification", sum(r[base]["right"] for r in R), n, 100 * sum(r[base]["right"] for r in R) / max(1, n)))
        for v in vs:
            lo = sum(r[base]["right"] and not r[v]["right"] for r in R); ga = sum(r[v]["right"] and not r[base]["right"] for r in R)
            L.append("| (%s) %s | %d / %d (%.1f%%) | %d / %d, %.2g |" % (v, "rewritten as one interpretation" if v == "b" else "standalone question", sum(r[v]["right"] for r in R), n, 100 * sum(r[v]["right"] for r in R) / max(1, n), lo, ga, _mcnemar(lo, ga)))
        L.append("")
    open(OUT + "/spider2/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


def clarification(sql, site):
    """The simulated user's turn for one library edit (code template naming the column, table or value of the site)."""
    from sqlglot import exp
    import re as _re
    q = RU.parse(sql); node = list(q.walk())[site[2]]; rule, side, _i = site
    plain = lambda e: _re.sub(r"\b\w+\.(\w+)", r"\1", e.sql(dialect="sqlite")).replace('"', "").replace("`", "")
    if rule == "count_unit":
        a = node.this.expressions[0] if isinstance(node.this, exp.Distinct) else node.this; c = plain(a)
        return "Count each distinct %s only once." % c if side == "rows" else "Count every row, including repeated %s values." % c
    if rule == "join_kind":
        t = node.this.name if isinstance(node.this, exp.Table) else "the joined table"
        return "Also keep rows that have no matching %s record." % t if side == "drop_unmatched" else "Only keep rows that have a matching %s record." % t
    if rule == "ties": return "If several rows tie at the cut-off, return all of them."
    if rule == "boundary":
        v = node.expression.sql(dialect="sqlite"); return "Count the value %s itself as included." % v if side == "strict" else "Do not include the value %s itself." % v
    if rule == "null_filter":
        k = plain(node.args["order"].expressions[0].this); return "Ignore rows where %s is missing." % k
    return None


def bird_items():
    from specbridge.report import impact as IM, linter as LI
    from specbridge.comm.common import grade as G
    dev = {x["question_id"]: x for x in json.load(open(IM.BIRD + "/dev.json"))}
    out = []
    for c in json.load(open("out/impact/impact.json"))["changed_questions"]["BIRD dev"]:
        x = dev[c["id"]]; path = "%s/dev_databases/%s/%s.sqlite" % (IM.BIRD, x["db_id"], x["db_id"]); sql = x["SQL"]
        base = IM.run(path, sql); q = RU.parse(sql)
        if base is None or q is None: continue
        for st in RU.sites(sql):
            if st[0] not in c["rules"] or (st[0] == "count_unit" and not LI.count_ok(q, st, x["question"])): continue
            e = RU.edit(sql, st); alt = IM.run(path, e) if e else None
            if alt is None or LI.degenerate(base, alt) or G.bird_ex(base, alt) or not RU.alternative_ok(sql, st, path): continue
            cl = clarification(sql, st)
            if cl: out.append({"id": "q%d" % c["id"], "db": x["db_id"], "path": path, "question": x["question"], "evidence": x.get("evidence") or "", "rule": st[0], "clarification": cl, "gold": e, "gold0": sql}); break
    return out


def run_bird(models=("sonnet", "gpt-6-sol"), workers=6):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    from specbridge.comm.common import grade as G
    from specbridge.report import impact as IM
    P = AM._dtp_prompts(); items = bird_items(); json.dump(items, open(OUT + "/bird/items.json", "w"), indent=1)
    jobs = [(m, it) for it in items for m in models]; random.Random(SEED).shuffle(jobs)
    def one(j):
        m, it = j; f = "%s/bird/runs/%s/%s.json" % (OUT, m, it["id"])
        if os.path.exists(f): return
        schema = _schema(it["path"])
        q0 = it["question"] + ("\nEvidence: " + it["evidence"] if it["evidence"] else "")
        g1 = IM.run(it["path"], it["gold"], limit=60); g0 = IM.run(it["path"], it["gold0"], limit=60); out = dict(it)
        if g1 is None or g0 is None:                                         # gold did not run in time: recorded, not scored
            with open(OUT + "/bird/skipped.txt", "a") as fh: fh.write("%s %s gold timed out\n" % (m, it["id"]))
            return
        order = ["c", "b", "d"]; random.Random(hash((m, it["id"])) & 0xffff).shuffle(order)
        for v in order:
            if v == "c": req = q0 + "\n" + it["clarification"]
            elif v == "b":
                t = ask(P["user_message_interpr_ambig"].format("DATABASE SCHEMA:\n" + schema, q0) + TELL.format(it["clarification"]), m, timeout=1500, quiet=True) or ""
                ls = [AM.item_line(x) for x in t.splitlines() if AM.item_line(x)]; req = ls[0] if ls else ""; raw_b = t
            else:
                req = (ask(CONDENSE.format(q0, it["clarification"]), m, timeout=1500, quiet=True) or "").split("Standalone question:")[-1].strip()
            sql = None
            if req:
                try: sql = (jparse(ask(X.PLAIN % (schema, "", req), m, timeout=1500, quiet=True) or "", "{") or {}).get("sql")
                except Exception: sql = None
            rows = IM.run(it["path"], sql) if sql else None
            out[v] = {"request": req, "sql": sql, "runs": rows is not None, "right": rows is not None and G.bird_ex(g1, rows),
                      "unclarified": rows is not None and G.bird_ex(g0, rows)}
            if v == "b": out[v]["raw"] = raw_b
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(out, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report_bird(models)


def _schema(path):
    import sqlite3
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    s = "\n".join(r[0] for r in con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")); con.close(); return s


def report_bird(models=("sonnet", "gpt-6-sol")):
    import glob
    R = {m: [json.load(open(f)) for f in glob.glob("%s/bird/runs/%s/*.json" % (OUT, m))] for m in models}
    L = ["# Simulated user clarification on BIRD dev (gate: out/rewrite/bird/GATE.md)\n",
         "| model | questions | (c) add | (b) rewrite | (d) standalone | (c)-(b): lost / gained, p | (c)-(d): lost / gained, p |", "|---|---|---|---|---|---|---|"]
    def line(name, rs):
        n = len(rs); a = lambda v: 100 * sum(r[v]["right"] for r in rs) / max(1, n)
        mc = lambda v: (sum(r["c"]["right"] and not r[v]["right"] for r in rs), sum(r[v]["right"] and not r["c"]["right"] for r in rs))
        (b1, b2), (d1, d2) = mc("b"), mc("d")
        L.append("| %s | %d | %.1f | %.1f | %.1f | %d / %d, %.2g | %d / %d, %.2g |" % (name, n, a("c"), a("b"), a("d"), b1, b2, _mcnemar(b1, b2), d1, d2, _mcnemar(d1, d2)))
    for m in models: line(m, R[m])
    allr = [r for m in models for r in R[m]]; line("pooled", allr)
    L += ["", "Why answers failed (pooled; execution): " + "; ".join("%s: clarification lost %d, other requirement lost %d, does not run %d" % (
        {"c": "add", "b": "rewrite", "d": "standalone"}[v], sum(r[v]["runs"] and not r[v]["right"] and r[v]["unclarified"] for r in allr),
        sum(r[v]["runs"] and not r[v]["right"] and not r[v]["unclarified"] for r in allr), sum(not r[v]["runs"] for r in allr)) for v in "cbd")]
    by = collections.defaultdict(list)
    for r in allr: by[r["rule"]].append(r)
    L += ["", "By choice type (pooled): " + "; ".join("%s n=%d add %.0f / rewrite %.0f / standalone %.0f" % (k, len(v), *[100 * sum(r[x]["right"] for r in v) / len(v) for x in "cbd"]) for k, v in sorted(by.items()))]
    open(OUT + "/bird/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "classify": classify, "report": report, "detail": detail, "s2": lambda: run_s2(), "report_s2": lambda: report_s2(), "bird": lambda: run_bird(), "report_bird": lambda: report_bird()}[sys.argv[1]]()
