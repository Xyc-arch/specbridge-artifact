"""THE DISCLOSURE SYSTEM (2026-10-28, out/system/PREREG.md): gate -> wide search only where a choice is open -> each interpretation as an
edit of the request -> execute, drop failures, merge identical results. One rule for AMBROSIA and the request sets; the gate call is
our listing call (arm `ours`) and the wide search is DtP's two listing calls (arm `dtp`), reused from those arms' files when present.
    python -m specbridge.comm.transfer.system pilot | report_pilot"""
import collections, concurrent.futures as cf, json, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import ambrosia as AM, reqmethod as RM, disclose as X, ledger as LG

OUT = "out/system"; MAXW = int(os.environ.get("SB_MAX_WORKERS", 6)); N_CLAUSES = 4


def _call(ask, m, sink):
    def call(p):
        try: t = ask(p, m, timeout=1500, quiet=True) or ""
        except Exception: t = ""; sink["failed"] += 1
        sink["calls"] += 1; sink["chars_in"] += len(p); sink["chars_out"] += len(t); return t
    return call


def answer(q, ctx, sql_ctx, call, gate=None, listing=None, ints=None):
    """One request through the system. gate: the readings of our listing call (saved arm `ours`), else one call. listing: DtP's raw
    [interpretations, missing] (saved arm `dtp`), else two calls. Returns the record to save; queries[0] answers the original request."""
    from specbridge.comm.common.llm import parse as jparse
    P = AM._dtp_prompts(); s = {"gate": "saved" if gate is not None else "called"}
    if gate is None:
        t = call(AM.DETECT % (ctx, q))
        gate = [x for x in ((jparse(t, "{") or {}).get("readings") or []) if isinstance(x, str) and x.strip()] or [q]
    sql = lambda text: AM.parse_one(call(P["user_message_sql"].format(sql_ctx, text)))[:1]
    if len(gate) <= 1: return dict(s, open=False, gate=gate, texts=[q], queries=sql(q))
    if ints is not None: pass                                         # DtP's saved interpretations (checked lines, see truncation)
    elif listing is None:
        t = call(P["user_message_interpr_ambig"].format(ctx, q))
        miss = call(P["user_message_interpr_ambig_missing"].format(ctx, q, "\n".join(AM.item_line(x) for x in t.splitlines() if AM.item_line(x))))
        listing = [t, miss]
    if ints is None:
        t, miss = listing; ints = [AM.item_line(x) for x in t.splitlines() if AM.item_line(x)]
        if "all possible interpretations are covered" not in miss.lower(): ints += [AM.item_line(x) for x in miss.splitlines() if AM.item_line(x)]
    cl = [x.strip() for x in ((jparse(call(RM.EDIT % (q, "\n".join("- " + i for i in gate[:4] + ints[:6]))), "{") or {}).get("clauses") or [])
          if isinstance(x, str) and x.strip()][:N_CLAUSES]
    texts = [q] + [q.rstrip() + " " + c for c in cl]
    return dict(s, open=True, gate=gate, interpretations=ints, clauses=cl, texts=texts, queries=[x for tx in texts for x in sql(tx)])


def _cost_saved(f, n):           # the first n calls of a saved arm's record (gate: 1; DtP listing: 2), at its mean size
    c = json.load(open(f)).get("cost", {}); k = max(1, c.get("calls", 1))
    return {"calls": n, "chars_in": c.get("chars_in", 0) * n // k, "chars_out": c.get("chars_out", 0) * n // k}


def _job_ambrosia(m, r, f, ours_f, dtp_f, ask):
    if os.path.exists(f): return
    s = collections.Counter(); call = _call(ask, m, s); o = json.load(open(ours_f)) if os.path.exists(ours_f) else None
    d = json.load(open(dtp_f)) if dtp_f and os.path.exists(dtp_f) else None
    rec = answer(r["question"], r["dump"], r["dump"], call, gate=o and o.get("readings"), listing=d and d.get("raw"), ints=d and d.get("interpretations"))
    if o: s.update(_cost_saved(ours_f, 1))
    if rec["open"] and d: s.update(_cost_saved(dtp_f, 2))
    os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(dict(rec, row=r["row"], model=m, arm="system", cost=dict(s)), open(f, "w"), indent=1)


def _job_sets(m, k, w, c, q, f, ours_f, dtp_f, ask):
    if os.path.exists(f): return
    s = collections.Counter(); call = _call(ask, m, s); schema, docs = DB.context(c); o = json.load(open(ours_f)) if os.path.exists(ours_f) else None
    d = json.load(open(dtp_f)) if dtp_f and os.path.exists(dtp_f) else None
    rec = answer(q, RM._ctx(c), schema + "\n\n" + docs, call, gate=o and o.get("readings"), listing=d and d.get("raw"), ints=d and d.get("interpretations"))
    if o: s.update(_cost_saved(ours_f, 1))
    if rec["open"] and d: s.update(_cost_saved(dtp_f, 2))
    os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(dict(rec, case=k, wording=w, model=m, arm="system", cost=dict(s)), open(f, "w"), indent=1, default=str)


def _pf(kind, m, key): return "%s/pilot/%s/%s/%s.json" % (OUT, kind, m, str(key).replace(":", "__").replace("/", "_"))


def pilot(workers=6):
    """Dev pilot (PREREG): AMBROSIA dev with Sonnet, the 30 dev request sets with Sonnet and GPT-Sol. The saved dev DtP files have no
    raw listing (parsed before the item_line fix), so the system makes its own two listing calls here."""
    from specbridge.pd.ask import ask
    jobs = [lambda m=m, r=r: _job_ambrosia(m, r, _pf("ambrosia", m, r["row"]), AM._mf("ours", m, r), None, ask)
            for m in ("sonnet",) for r in AM.method_rows()]
    fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, WD = LG.sets()
    base = "out/reqmethod"
    of = lambda arm, m, k, w: "%s/%s/%s/%s__%s.json" % (base, arm, m, k.replace(":", "__").replace("/", "_"), w)
    jobs += [lambda m=m, k=k, w=w: _job_sets(m, k, w, C[k], W[k][w], _pf("sets", m, "%s__%s" % (k, w)), of("ours", m, k, w), None, ask)
             for k in ks for w in WD[k] for m in ("sonnet", "gpt-6-sol")]
    random.Random(28).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, MAXW)) as ex: list(ex.map(lambda j: j(), jobs))
    report_pilot()


def _amb_score(r, qs):
    """The paper's AMBROSIA scoring (ambrosia.report_final): failing SQL dropped, identical results merged, shape-tolerant."""
    from specbridge.comm.common import grade as G
    db = r["db_file"]; P_ = [x for x in (AM._ex_sql(db, q) for q in set(AM._dedup(db, qs))) if x is not None]; gs = [AM._ex_sql(db, g) for g in r["gold"]]
    st = lambda g, p: g is not None and G.shape_tolerant([list(y) for y in g], [list(y) for y in p])
    hit = [any(st(g, p) for p in P_) for g in gs]; good = [any(st(g, p) for g in gs) for p in P_]
    return all(hit), sum(hit) / len(hit), (sum(good) / len(good) if good else 0.0), len(P_)


def report_pilot():
    L = ["# System dev pilot (gate: out/system/PREREG.md)\n", "## AMBROSIA dev, Sonnet (shape-tolerant; merged as every arm)\n",
         "| arm | AllFound | recall | precision (unambiguous) | answers per unambiguous q. | calls per q. |", "|---|---|---|---|---|---|"]
    R = AM.method_rows(); m = "sonnet"; res = {}
    def arm_q(a, r):
        f = _pf("ambrosia", m, r["row"]) if a == "system" else AM._mf(a, m, r)
        return (json.load(open(f))["queries"], json.load(open(f)).get("cost", {}).get("calls", 1)) if os.path.exists(f) else (None, 0)
    rows = [r for r in R if all(arm_q(a, r)[0] is not None for a in ("dtp", "ours", "system"))]
    A = [r for r in rows if r["ambiguous"]]; U = [r for r in rows if not r["ambiguous"]]
    for a in ("dtp", "ours", "system"):
        S = {r["row"]: _amb_score(r, arm_q(a, r)[0]) for r in rows}
        res[a] = {"allfound": sum(S[r["row"]][0] for r in A), "precision": sum(S[r["row"]][2] for r in U) / max(1, len(U))}
        L.append("| %s | %d / %d | %.3f | %.3f | %.2f | %.1f |" % (a, res[a]["allfound"], len(A), sum(S[r["row"]][1] for r in A) / max(1, len(A)), res[a]["precision"],
                 sum(S[r["row"]][3] for r in U) / max(1, len(U)), sum(arm_q(a, r)[1] for r in rows) / max(1, len(rows))))
    ok_a = res["system"]["allfound"] >= res["dtp"]["allfound"] and res["system"]["precision"] >= res["dtp"]["precision"] + 0.10
    L += ["", "AMBROSIA gate: %s (AllFound %d vs DtP %d; precision %.3f vs DtP %.3f + 0.10)." % ("PASS" if ok_a else "FAIL", res["system"]["allfound"],
          res["dtp"]["allfound"], res["system"]["precision"], res["dtp"]["precision"]), ""]
    fz, _wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; ks, WD = LG.sets(); ok_s = True
    for m in ("sonnet", "gpt-6-sol"):
        L += ["## Request sets dev, %s\n" % m, "| arm | open: both interpretations | specific: main right | specific: false alarm |", "|---|---|---|---|"]; got = {}
        for a in ("plain", "samplek", "dtp", "ours", "system"):
            def ans(k, w):
                if a != "system":
                    old = RM.OUT; RM.OUT = "out/reqmethod"
                    try: return RM._answers(a, m, k, w, C)
                    finally: RM.OUT = old
                f = _pf("sets", m, "%s__%s" % (k, w))
                if not os.path.exists(f): return None
                c = C[k]; con = DB.connect(c["snapshot"]); seen, res_ = [], []
                for q in [x for x in json.load(open(f))["queries"] if x]:
                    rows_ = DB.rows(con, q)
                    if rows_ is None: continue
                    key = json.dumps(sorted(map(repr, rows_)))
                    if key in seen: continue
                    seen.append(key); res_.append((q, X._match(c, rows_), rows_))
                return res_
            op = [ans(k, "open") for k in ks]; cov = sum(r is not None and {"A", "B"} <= {y for _q, mt, _r in r for y in mt} for r in op)
            sp = [(w, ans(k, w)) for k in ks for w in WD[k] if w != "open"]; sp = [(w, r) for w, r in sp if r is not None]
            right = sum(bool(r) and w[-1] in r[0][1] for w, r in sp); fa = sum(any(("B" if w.endswith("A") else "A") in mt for _q, mt, _r in r) for w, r in sp)
            got[a] = (cov, right); L.append("| %s | %d / %d | %d / %d | %d |" % (a, cov, sum(r is not None for r in op), right, len(sp), fa))
        ok = got["system"][0] >= got["ours"][0] and got["system"][1] >= got["ours"][1] - 1; ok_s = ok_s and ok
        L += ["", "Request-set gate, %s: %s." % (m, "PASS" if ok else "FAIL"), ""]
    L.append("**Pilot: %s.**" % ("PASS" if ok_a and ok_s else "FAIL"))
    os.makedirs(OUT, exist_ok=True); open(OUT + "/PILOT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


# FINAL (2026-10-28): the system on the existing test items -- the AMBROSIA final test (150 questions per model) and the 111 request
# sets of Table 5 -- reusing every saved arm. Only the system's own new calls are made (clause call, SQL for the original request and
# each edited one; the clear path's one SQL call on the original request). Nothing is tuned.
MODELS = ("sonnet", "gpt-6-sol"); SETS_OUT = "out/reqmethod100"


def _sets():
    RM.OUT = SETS_OUT; RM.N = 130; ks, WD = RM.chosen(); fz, wr, _o = X._paths(LG.D)
    return ks, WD, {c["case"]: c for c in json.load(open(fz))["cases"]}, json.load(open(wr))


def _ffs(kind, m, key): return "%s/final/%s/%s/%s.json" % (OUT, kind, m, str(key).replace(":", "__").replace("/", "_"))


def run_final(workers=6):
    from specbridge.pd.ask import ask
    jobs = [lambda m=m, r=r: _job_ambrosia(m, r, _ffs("ambrosia", m, r["row"]), AM._ff("ours", m, r["row"]), AM._ff("dtp", m, r["row"]), ask)
            for m in MODELS for r in AM.final_rows() if os.path.exists(AM._ff("ours", m, r["row"])) and os.path.exists(AM._ff("dtp", m, r["row"]))]
    ks, WD, C, W = _sets()
    jobs += [lambda m=m, k=k, w=w: _job_sets(m, k, w, C[k], W[k][w], _ffs("sets", m, "%s__%s" % (k, w)), RM._f("ours", m, k, w), RM._f("dtp", m, k, w), ask)
             for k in ks for w in WD[k] for m in MODELS if os.path.exists(RM._f("ours", m, k, w)) and os.path.exists(RM._f("dtp", m, k, w))]
    random.Random(29).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, MAXW)) as ex: list(ex.map(lambda j: j(), jobs))
    report_final()


def _boot(v, B=2000, seed=7):
    g = random.Random(seed); b = sorted(sum(v[g.randrange(len(v))] for _ in v) / len(v) for _ in range(B))
    return [round(100 * sum(v) / len(v), 1), round(100 * b[int(.025 * B)], 1), round(100 * b[int(.975 * B) - 1], 1)]


def report_final():
    JS = {"ambrosia": {}, "sets": {}, "pooled": {}}; L = ["# The disclosure system on the existing test items (out/system/PREREG.md; saved arms reused)\n"]
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    arms = ("plain", "samplek", "dtp", "ours", "gate+dtp", "system"); PA = collections.defaultdict(list); PS = collections.defaultdict(list)
    L += ["## AMBROSIA final test (shape-tolerant; failing SQL dropped and identical results merged, every arm)\n",
          "| model | method | AllFound | recall | precision (clear) | answers per clear q. | calls per q. |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        def load(a, r):
            if a == "system": f = _ffs("ambrosia", m, r["row"])
            elif a == "gate+dtp": f = AM._ff("ours", m, r["row"])
            else: f = AM._ff(a, m, r["row"])
            if not os.path.exists(f): return None
            o = json.load(open(f)); c = o.get("cost", {}).get("calls", 1)
            if a == "gate+dtp":
                if len(o.get("readings") or []) <= 1: return o["queries"], c
                d = json.load(open(AM._ff("dtp", m, r["row"]))); return o["queries"] + d["queries"], c + d.get("cost", {}).get("calls", 0)
            return o["queries"], c
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and all(load(a, r) is not None for a in arms)]
        A = [r for r in R if r["ambiguous"]]; U = [r for r in R if not r["ambiguous"]]; S = {}
        for a in arms:
            S[a] = {r["row"]: _amb_score(r, load(a, r)[0]) for r in R}; calls = sum(load(a, r)[1] for r in R) / len(R)
            x = {"n_amb": len(A), "n_clear": len(U), "allfound": sum(S[a][r["row"]][0] for r in A), "recall": sum(S[a][r["row"]][1] for r in A) / len(A),
                 "precision": sum(S[a][r["row"]][2] for r in U) / len(U), "answers_clear": sum(S[a][r["row"]][3] for r in U) / len(U), "calls": calls}
            JS["ambrosia"].setdefault(m, {})[a] = x
            L.append("| %s | %s | %d / %d | %.3f | %.3f | %.2f | %.1f |" % (m, a, x["allfound"], len(A), x["recall"], x["precision"], x["answers_clear"], calls))
            PA[a + "|af"] += [int(S[a][r["row"]][0]) for r in A]; PA[a + "|rec"] += [S[a][r["row"]][1] for r in A]; PA[a + "|pre"] += [S[a][r["row"]][2] for r in U]
    ks, WD, C, _W = _sets()
    L += ["", "## Request sets (Table 5's 111 sets; identical results merged, every arm)\n",
          "| model | method | open: both interpretations | specific: main right | specific: false alarm | calls per request |", "|---|---|---|---|---|---|"]
    from specbridge.comm.transfer import reviewed as RV
    ks = RV.accepted(ks)
    for m in MODELS:
        def ans(a, k, w):
            if a != "system": return RM._answers(a, m, k, w, C)
            f = _ffs("sets", m, "%s__%s" % (k, w))
            if not os.path.exists(f): return None
            c = C[k]; con = DB.connect(c["snapshot"]); seen, res_ = [], []
            for q in [x for x in json.load(open(f))["queries"] if x]:
                rows_ = DB.rows(con, q)
                if rows_ is None: continue
                key = json.dumps(sorted(map(repr, rows_)))
                if key in seen: continue
                seen.append(key); res_.append((q, X._match(c, rows_), rows_))
            return res_
        sa = ("plain", "samplek", "dtp", "ours", "system"); Rr = {(a, k, w): ans(a, k, w) for a in sa for k in ks for w in WD[k]}
        sets = [k for k in ks if all(Rr[(a, k, w)] is not None for a in sa for w in WD[k])]
        for a in sa:
            cov = [int({"A", "B"} <= {y for _q, mt, _r in Rr[(a, k, "open")] for y in mt}) for k in sets]
            Ps = [(k, w) for k in sets for w in WD[k] if w != "open"]
            right = [int(bool(Rr[(a, k, w)]) and w[-1] in Rr[(a, k, w)][0][1]) for k, w in Ps]
            fa = sum(any(("B" if w.endswith("A") else "A") in mt for _q, mt, _r in Rr[(a, k, w)]) for k, w in Ps)
            cs = [json.load(open(_ffs("sets", m, "%s__%s" % (k, w)) if a == "system" else RM._f(a, m, k, w))).get("cost", {}).get("calls", 1)
                  for k in sets for w in WD[k]] if a != "plain" else [1]
            JS["sets"].setdefault(m, {})[a] = {"sets": len(sets), "both": sum(cov), "right": sum(right), "specific": len(Ps), "false_alarm": fa, "calls": sum(cs) / len(cs)}
            L.append("| %s | %s | %d / %d | %d / %d | %d | %.1f |" % (m, a, sum(cov), len(sets), sum(right), len(Ps), fa, sum(cs) / len(cs)))
            PS[a + "|both"] += cov; PS[a + "|right"] += right
    L += ["", "## Pooled over both models, paired by item (points, 95% bootstrap interval)\n"]
    for b in ("dtp", "ours", "samplek", "gate+dtp"):
        d = {k: _boot([x - y for x, y in zip(PA["system|" + k], PA[b + "|" + k])]) for k in ("af", "rec", "pre")}
        JS["pooled"]["ambrosia_system-" + b] = d
        L.append("- AMBROSIA, system - %s: AllFound %s; recall %s; precision %s." % (b, d["af"], d["rec"], d["pre"]))
    for b in ("dtp", "ours", "samplek"):
        d = {k: _boot([x - y for x, y in zip(PS["system|" + k], PS[b + "|" + k])]) for k in ("both", "right", "prec")}
        JS["pooled"]["sets_system-" + b] = d
        L.append("- Request sets, system - %s: both interpretations %s; specific right %s." % (b, d["both"], d["right"]))
    os.makedirs(OUT, exist_ok=True); json.dump(JS, open(OUT + "/final.json", "w"), indent=1)
    open(OUT + "/FINAL.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# ARM `ask` (PREREG, amended 2026-10-28): the documented built-in behavior of production assistants -- decide before any SQL runs, and
# if the question is ambiguous, stop and ask the user (Cortex Analyst: suggested questions; Genie: a clarifying question). Zero calls:
# the decision is the system's own gate, the answer is the system's answer to the original request (queries[0]); only the action differs.
def report_ask():
    from specbridge.comm.transfer import reviewed as RV
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    JS = {}; L = ["# Decide-then-ask (built-in behavior, same gate) vs the system, same items\n",
                  "| model | data | open: asks the user | open: every interpretation returned, ask / system | clear: wrongly asks | clear: main answer right, ask / system | round trips per 100 requests |",
                  "|---|---|---|---|---|---|---|"]
    ks, WD, C, _W = _sets(); ks = RV.accepted(ks)
    for m in MODELS:
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and os.path.exists(_ffs("ambrosia", m, r["row"]))]
        A = [r for r in R if r["ambiguous"]]; U = [r for r in R if not r["ambiguous"]]; o = {r["row"]: json.load(open(_ffs("ambrosia", m, r["row"]))) for r in R}
        main_ok = lambda r: _amb_score(r, o[r["row"]]["queries"][:1])[2] == 1.0
        x = {"n_open": len(A), "open_asks": sum(o[r["row"]]["open"] for r in A),
             "allfound_ask": sum(not o[r["row"]]["open"] and _amb_score(r, o[r["row"]]["queries"][:1])[0] for r in A),
             "allfound_system": sum(_amb_score(r, o[r["row"]]["queries"])[0] for r in A),
             "n_clear": len(U), "clear_asks": sum(o[r["row"]]["open"] for r in U),
             "clear_right_ask": sum(not o[r["row"]]["open"] and main_ok(r) for r in U), "clear_right_system": sum(main_ok(r) for r in U),
             "round_trips_per_100": 100 * sum(o[r["row"]]["open"] for r in R) / len(R)}
        JS.setdefault(m, {})["ambrosia"] = x
        L.append("| %s | AMBROSIA | %d / %d | %d / %d | %d / %d | %d / %d | %.0f |" % (m, x["open_asks"], len(A), x["allfound_ask"], x["allfound_system"], x["clear_asks"], len(U),
                 x["clear_right_ask"], x["clear_right_system"], x["round_trips_per_100"]))
        n = collections.Counter()
        for k in ks:
            fs = {w: _ffs("sets", m, "%s__%s" % (k, w)) for w in WD[k]}
            if not all(os.path.exists(f) for f in fs.values()): continue
            c = C[k]; con = DB.connect(c["snapshot"])
            def match(qs):
                out = []
                for q in [x for x in qs if x]:
                    rows_ = DB.rows(con, q)
                    if rows_ is not None: out.append(X._match(c, rows_))
                return out
            for w in WD[k]:
                rec = json.load(open(fs[w])); sm = match(rec["queries"])
                if w == "open":
                    n["open"] += 1; n["open_asks"] += rec["open"]; n["both_system"] += int({"A", "B"} <= {y for mt in sm for y in mt})
                else:
                    first = match(rec["queries"][:1]); ok = int(bool(first) and w[-1] in first[0])
                    n["specific"] += 1; n["specific_asks"] += rec["open"]; n["right_ask"] += ok * (not rec["open"]); n["right_system"] += ok
        JS[m]["sets"] = dict(n)
        L.append("| %s | request sets | %d / %d | 0 / %d | %d / %d (specific) | %d / %d (specific) | %.0f |" % (m, n["open_asks"], n["open"], n["both_system"], n["specific_asks"], n["specific"],
                 n["right_ask"], n["right_system"], 100 * (n["open_asks"] + n["specific_asks"]) / max(1, n["open"] + n["specific"])))
    os.makedirs(OUT, exist_ok=True); json.dump(JS, open(OUT + "/ask.json", "w"), indent=1)
    open(OUT + "/ASK.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# THE METHOD (2026-10-28, after the interim system result: the edit step lost coverage on AMBROSIA's short questions): gate + wide
# search + execute = our listing call as the gate; where it finds several interpretations, DtP's wide search; every answer executed,
# failing SQL dropped, identical results merged; the gate's answer first. Built from saved arms, zero calls. Baselines: plain, three
# samples, DtP, and interpret-and-state: the one answer a production assistant returns in the same turn, with its interpretation in
# words (Cortex Analyst: "We interpreted your question as ..."); execution scores the answer, so it is the plain call's main query.
def _plain_main(m, k, w):
    f = RM._plain_f(m, k, w)
    return ((json.load(open(f)).get("response") or {}).get("sql")) if os.path.exists(f) else None


def _arms_amb(m, r):
    o = json.load(open(AM._ff("ours", m, r["row"]))); d = json.load(open(AM._ff("dtp", m, r["row"]))); op = len(o.get("readings") or []) > 1
    q = lambda a: json.load(open(AM._ff(a, m, r["row"])))
    return {"plain": (q("plain")["queries"], 1), "samplek": (q("samplek")["queries"], 3), "dtp": (d["queries"], d["cost"]["calls"]),
            "state": (q("plain")["queries"][:1], 1), "ours": (o["queries"], o["cost"]["calls"]),
            "method": (o["queries"] + (d["queries"] if op else []), o["cost"]["calls"] + (d["cost"]["calls"] if op else 0))}


def _keep_load(f):
    if not os.path.exists(f): return ([], 0)
    o = json.load(open(f)); return (o["queries"], o["cost"].get("calls", 0))


def report_method():
    from specbridge.comm.transfer import reviewed as RV
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    AR = ("plain", "samplek", "dtp", "state", "ours", "method"); PA = collections.defaultdict(list); PS = collections.defaultdict(list); JS = {"ambrosia": {}, "sets": {}, "pooled": {}}
    L = ["# Gate + wide search + execute vs every baseline (saved arms, zero calls)\n", "## AMBROSIA final test\n",
         "| model | method | AllFound | recall | precision (clear) | calls per q. | asks the user per 100 q. |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and all(os.path.exists(AM._ff(a, m, r["row"])) for a in ("plain", "samplek", "dtp", "ours"))]
        A = [r for r in R if r["ambiguous"]]; U = [r for r in R if not r["ambiguous"]]; G = {r["row"]: _arms_amb(m, r) for r in R}
        for a in AR:
            S_ = {r["row"]: _amb_score(r, G[r["row"]][a][0]) for r in R}
            asks = 100 * sum(a == "ask" and not G[r["row"]][a][0] and len(json.load(open(AM._ff("ours", m, r["row"])))["readings"]) > 1 for r in R) / len(R)
            x = {"allfound": sum(S_[r["row"]][0] for r in A), "n_amb": len(A), "recall": sum(S_[r["row"]][1] for r in A) / len(A),
                 "precision": sum(S_[r["row"]][2] for r in U) / len(U), "n_clear": len(U), "calls": sum(G[r["row"]][a][1] for r in R) / len(R), "asks_per_100": asks}
            JS["ambrosia"].setdefault(m, {})[a] = x
            L.append("| %s | %s | %d / %d | %.3f | %.3f | %.1f | %.0f |" % (m, a, x["allfound"], len(A), x["recall"], x["precision"], x["calls"], asks))
            PA[a + "|af"] += [int(S_[r["row"]][0]) for r in A]; PA[a + "|rec"] += [S_[r["row"]][1] for r in A]; PA[a + "|pre"] += [S_[r["row"]][2] for r in U]
    ks, WD, C, _W = _sets(); ks = RV.accepted(ks)
    L += ["", "## Request sets (Table 5's 111 sets)\n", "| model | method | open: both interpretations | specific: main right | specific: false alarm | calls per request | asks per 100 requests |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        T = {a: {"both": [], "right": [], "prec": [], "fa": 0, "calls": [], "asks": 0} for a in AR}
        for k in ks:
            if not all(os.path.exists(RM._f(a, m, k, w)) for a in ("samplek", "dtp", "ours") for w in WD[k]): continue
            c = C[k]; con = DB.connect(c["snapshot"])
            def match(qs):
                seen, out = [], []
                for q in [x for x in qs if x]:
                    r_ = DB.rows(con, q)
                    if r_ is None: continue
                    key = json.dumps(sorted(map(repr, r_)))
                    if key in seen: continue
                    seen.append(key); out.append(X._match(c, r_))
                return out
            for w in WD[k]:
                o = json.load(open(RM._f("ours", m, k, w))); d = json.load(open(RM._f("dtp", m, k, w))); sk = json.load(open(RM._f("samplek", m, k, w))); op = len(o.get("readings") or []) > 1
                pl = RM._answers("plain", m, k, w, C); plq = None
                Q = {"samplek": (sk["queries"], 3), "dtp": (d["queries"], d["cost"]["calls"]), "ours": (o["queries"], o["cost"]["calls"]),
                     "state": ([_plain_main(m, k, w)], 1), "method": (o["queries"] + (d["queries"] if op else []), o["cost"]["calls"] + (d["cost"]["calls"] if op else 0))}
                res = {a: match(qs) for a, (qs, _c) in Q.items()}; res["plain"] = [mt for _q, mt, _r in (pl or [])]
                for a in AR:
                    T[a]["calls"].append(Q[a][1] if a in Q else 1); T[a]["asks"] += int(a == "ask" and op)
                    if w == "open": T[a]["both"].append(int({"A", "B"} <= {y for mt in res[a] for y in mt}))
                    else:
                        T[a]["right"].append(int(bool(res[a]) and w[-1] in res[a][0])); T[a]["fa"] += any(("B" if w.endswith("A") else "A") in mt for mt in res[a])
                        T[a]["prec"].append(sum(w[-1] in mt for mt in res[a]) / len(res[a]) if res[a] else 0.0)   # share of returned answers that are right
        for a in AR:
            t = T[a]; x = {"both": sum(t["both"]), "sets": len(t["both"]), "right": sum(t["right"]), "specific": len(t["right"]), "false_alarm": t["fa"], "precision": 100 * sum(t["prec"]) / max(1, len(t["prec"])),
                           "calls": sum(t["calls"]) / max(1, len(t["calls"])), "asks_per_100": 100 * t["asks"] / max(1, len(t["calls"]))}
            JS["sets"].setdefault(m, {})[a] = x
            L.append("| %s | %s | %d / %d | %d / %d | %d | %.1f | %.0f |" % (m, a, x["both"], x["sets"], x["right"], x["specific"], x["false_alarm"], x["calls"], x["asks_per_100"]))
            PS[a + "|both"] += t["both"]; PS[a + "|right"] += t["right"]; PS[a + "|prec"] += t["prec"]
    L += ["", "## Pooled over both models, method minus each, paired by item (points [95% bootstrap])\n"]
    for b in AR[:-1]:
        d = {k: _boot([x - y for x, y in zip(PA["method|" + k], PA[b + "|" + k])]) for k in ("af", "rec", "pre")}
        e = {k: _boot([x - y for x, y in zip(PS["method|" + k], PS[b + "|" + k])]) for k in ("both", "right", "prec")}
        JS["pooled"][b] = {"ambrosia": d, "sets": e}
        L.append("- vs %s: AMBROSIA AllFound %s, recall %s, precision %s; request sets both %s, specific right %s." % (b, d["af"], d["rec"], d["pre"], e["both"], e["right"]))
    L += ["", "## Pooled, narrow search (ours) minus each baseline, paired by item\n"]; JS["pooled_narrow"] = {}
    for b in ("plain", "samplek", "dtp", "state"):
        d = {k: _boot([x - y for x, y in zip(PA["ours|" + k], PA[b + "|" + k])]) for k in ("af", "rec", "pre")}
        e = {k: _boot([x - y for x, y in zip(PS["ours|" + k], PS[b + "|" + k])]) for k in ("both", "right", "prec")}
        JS["pooled_narrow"][b] = {"ambrosia": d, "sets": e}
        L.append("- vs %s: AMBROSIA AllFound %s, recall %s, precision %s; request sets both %s, specific right %s." % (b, d["af"], d["rec"], d["pre"], e["both"], e["right"]))
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(OUT + "/method.json"):   # kept from report_budget and report_curve
        old = json.load(open(OUT + "/method.json")); JS["budget"] = old.get("budget"); JS["curve"] = old.get("curve"); JS["stream"] = old.get("stream")
    json.dump(JS, open(OUT + "/method.json", "w"), indent=1)
    open(OUT + "/METHOD.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



def report_budget(perms=200):
    """WHERE THE GAIN COMES FROM (2026-10-28), AMBROSIA final test, saved answers, pooled over both models, paired by question.
    Budget = per question, the number of interpretations the first step lists (ours: at most 4). DtP's answers are cut to that budget
    (a) on the same questions and (b) with the budgets shuffled across questions (perms times, seeded). Compares decide-then-answer with
    (a), and (a) with (b): whether the gain is placement and per-call answering, not fewer alternatives. -> method.json["budget"]."""
    from specbridge.comm.common import grade as G
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    EX = {}
    def ex(db, q):
        if (db, q) not in EX: EX[(db, q)] = AM._ex_sql(db, q)
        return EX[(db, q)]
    def sc(r, qs):
        db = r["db_file"]; res = []
        for q in dict.fromkeys(qs):          # in the order returned (as ambrosia._dedup), never set order
            x = ex(db, q)
            if x is None or any(AM.same(x, y, "order by" in q.lower()) and AM.same(y, x, "order by" in q.lower()) for y in res): continue
            res.append(x)
        gs = [ex(db, g) for g in r["gold"]]; st = lambda g, p: g is not None and G.shape_tolerant([list(y) for y in g], [list(y) for y in p])
        good = [any(st(g, p) for g in gs) for p in res]
        return all(any(st(g, p) for p in res) for g in gs), (sum(good) / len(good) if good else 0.0)
    D = collections.defaultdict(list)
    for m in MODELS:
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and all(os.path.exists(AM._ff(a, m, r["row"])) for a in ("dtp", "ours"))]
        O = {r["row"]: json.load(open(AM._ff("ours", m, r["row"]))) for r in R}; T = {r["row"]: json.load(open(AM._ff("dtp", m, r["row"])))["queries"] for r in R}
        n = {k: min(4, len(o.get("readings") or [])) or 1 for k, o in O.items()}; rows = [r["row"] for r in R]
        rng = random.Random(11); P = []
        for _ in range(perms): c = [n[k] for k in rows]; rng.shuffle(c); P.append(dict(zip(rows, c)))
        for r in R:
            k = r["row"]; o = sc(r, O[k]["queries"]); a = sc(r, T[k][:n[k]]); rp = [sc(r, T[k][:p[k]]) for p in P]
            rnd = (sum(x[0] for x in rp) / perms, sum(x[1] for x in rp) / perms)
            if r["ambiguous"]: D["answer_vs_cut|af"].append(int(o[0]) - int(a[0])); D["place_vs_random|af"].append(int(a[0]) - rnd[0])
            else: D["answer_vs_cut|pre"].append(o[1] - a[1]); D["place_vs_random|pre"].append(a[1] - rnd[1])
    out = {k: _boot(v) for k, v in D.items()}
    J = json.load(open(OUT + "/method.json")); J["budget"] = out; json.dump(J, open(OUT + "/method.json", "w"), indent=1); print(json.dumps(out, indent=1))



def report_curve(K=6, B=1000):
    """PRECISION-COVERAGE CURVES (2026-10-28), AMBROSIA final test, saved answers. Threshold k = the most answers a method may show per
    question (k = 1..K), each method in its own order (decide-then-search: the first step's answers, then DtP's). Per k: AllFound on
    ambiguous questions, precision on clear ones. Area = interpolated average precision over coverage 0..1 (precision at coverage c = the
    best precision of any k reaching coverage >= c; 0 if none). Bootstrap over questions (ambiguous and clear resampled separately) for
    the area difference against each baseline. -> method.json["curve"]."""
    from specbridge.comm.common import grade as G
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    EX = {}
    def ex(db, q):
        if (db, q) not in EX: EX[(db, q)] = AM._ex_sql(db, q)
        return EX[(db, q)]
    def sc(r, qs):
        db = r["db_file"]; res = []
        for q in dict.fromkeys(qs):          # in the order returned (as ambrosia._dedup), never set order
            x = ex(db, q)
            if x is None or any(AM.same(x, y, "order by" in q.lower()) and AM.same(y, x, "order by" in q.lower()) for y in res): continue
            res.append(x)
        gs = [ex(db, g) for g in r["gold"]]; st = lambda g, p: g is not None and G.shape_tolerant([list(y) for y in g], [list(y) for y in p])
        good = [any(st(g, p) for g in gs) for p in res]
        return int(all(any(st(g, p) for p in res) for g in gs)), (sum(good) / len(good) if good else 0.0)
    def area(af, pre):                      # af, pre: lists over k (fractions)
        pts = sorted(zip(af, pre)); grid = [i / 100 for i in range(101)]
        return sum(max([p for a, p in pts if a >= c - 1e-12] or [0.0]) for c in grid) / len(grid)
    arms = ("plain", "samplek", "dtp", "ours", "method"); out = {}
    for m in MODELS:
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and all(os.path.exists(AM._ff(a, m, r["row"])) for a in ("plain", "samplek", "dtp", "ours"))]
        Q = {r["row"]: {a: q for a, (q, _c) in _arms_amb(m, r).items()} for r in R}
        A = [r for r in R if r["ambiguous"]]; U = [r for r in R if not r["ambiguous"]]
        S = {a: {k: {r["row"]: sc(r, Q[r["row"]][a][:k]) for r in R} for k in range(1, K + 1)} for a in arms}
        def curve(a, Ai, Ui):
            af = [sum(S[a][k][A[i]["row"]][0] for i in Ai) / len(Ai) for k in range(1, K + 1)]
            pre = [sum(S[a][k][U[i]["row"]][1] for i in Ui) / len(Ui) for k in range(1, K + 1)]
            return af, pre
        allA, allU = list(range(len(A))), list(range(len(U)))
        o = out[m] = {"points": {a: [[round(100 * x, 1), round(100 * y, 1)] for x, y in zip(*curve(a, allA, allU))] for a in arms},
                      "area": {a: round(100 * area(*curve(a, allA, allU)), 1) for a in arms}}
        rng = random.Random(5); D = collections.defaultdict(list)
        for _ in range(B):
            Ai = [rng.randrange(len(A)) for _ in A]; Ui = [rng.randrange(len(U)) for _ in U]
            ar = {a: area(*curve(a, Ai, Ui)) for a in arms}
            for a in ("method", "ours"):
                for b in ("plain", "samplek", "dtp"): D["%s-%s" % (a, b)].append(100 * (ar[a] - ar[b]))
        o["diff_ci"] = {k: [round(sorted(v)[int(.025 * B)], 1), round(sorted(v)[int(.975 * B) - 1], 1)] for k, v in D.items()}
    J = json.load(open(OUT + "/method.json")); J["curve"] = out; json.dump(J, open(OUT + "/method.json", "w"), indent=1); print(json.dumps(out, indent=1))



def _counts(r, qs):
    """(interpretations missed, wrong answers shown) for one AMBROSIA question: failing SQL dropped, identical results merged,
    shape-tolerant matching (as every arm)."""
    from specbridge.comm.common import grade as G
    db = r["db_file"]; res = []
    for q in dict.fromkeys(qs):              # in the order returned (as ambrosia._dedup), never set order
        x = AM._ex_sql(db, q)
        if x is None or any(AM.same(x, y, "order by" in q.lower()) and AM.same(y, x, "order by" in q.lower()) for y in res): continue
        res.append(x)
    gs = [AM._ex_sql(db, g) for g in r["gold"]]; st = lambda g, p: g is not None and G.shape_tolerant([list(y) for y in g], [list(y) for y in p])
    return sum(not any(st(g, p) for p in res) for g in gs), sum(not any(st(g, p) for g in gs) for p in res)


def report_stream(shares=(0.1, 0.2, 0.3, 0.5), main=0.2, B=2000):
    """WHAT A USER GETS PER 100 REQUESTS (2026-10-28), AMBROSIA final test, saved answers, every arm scored the same way.
    Per question: missed = interpretations (gold queries) not returned (a clear question has one); wrong = returned answers matching no
    interpretation; calls = the method's calls. Decide-then-ask returns nothing on a request it flags. For a stream with a share pi of
    ambiguous requests: per 100 = 100 * (pi * mean over ambiguous + (1 - pi) * mean over clear). Bootstrap over questions (ambiguous and
    clear resampled separately, both models pooled) for method minus baseline at pi = main. -> method.json["stream"]."""
    from specbridge.comm.common import grade as G
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    counts = _counts
    arms = ("plain", "samplek", "dtp", "state", "ours", "method"); per = {}; PA = collections.defaultdict(list); PU = collections.defaultdict(list)
    for m in MODELS:
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and all(os.path.exists(AM._ff(a, m, r["row"])) for a in ("plain", "samplek", "dtp", "ours"))]
        A = [r for r in R if r["ambiguous"]]; U = [r for r in R if not r["ambiguous"]]; Gm = {r["row"]: _arms_amb(m, r) for r in R}
        per[m] = {}
        for a in arms:
            V = {r["row"]: counts(r, Gm[r["row"]][a][0]) + (Gm[r["row"]][a][1],) for r in R}
            ma = [sum(V[r["row"]][i] for r in A) / len(A) for i in range(3)]; mu = [sum(V[r["row"]][i] for r in U) / len(U) for i in range(3)]
            per[m][a] = {"%g" % pi: {"missed": round(100 * (pi * ma[0] + (1 - pi) * mu[0]), 1), "wrong": round(100 * (pi * ma[1] + (1 - pi) * mu[1]), 1),
                                     "calls": round(100 * (pi * ma[2] + (1 - pi) * mu[2]))} for pi in shares}
            for r in A: PA[a].append(V[r["row"]])
            for r in U: PU[a].append(V[r["row"]])
    pooled = {}
    for a in arms:
        ma = [sum(v[i] for v in PA[a]) / len(PA[a]) for i in range(3)]; mu = [sum(v[i] for v in PU[a]) / len(PU[a]) for i in range(3)]
        pooled[a] = {"%g" % pi: {"missed": round(100 * (pi * ma[0] + (1 - pi) * mu[0]), 1), "wrong": round(100 * (pi * ma[1] + (1 - pi) * mu[1]), 1),
                                 "calls": round(100 * (pi * ma[2] + (1 - pi) * mu[2]))} for pi in shares}
    rng = random.Random(9); nA, nU = len(PA["plain"]), len(PU["plain"]); D = collections.defaultdict(list)
    for _ in range(B):
        ia = [rng.randrange(nA) for _ in range(nA)]; iu = [rng.randrange(nU) for _ in range(nU)]
        f = lambda a, i: 100 * (main * sum(PA[a][j][i] for j in ia) / nA + (1 - main) * sum(PU[a][j][i] for j in iu) / nU)
        for x in ("method", "ours"):
            for b in ("plain", "samplek", "dtp", "state"):
                for i, k in ((0, "missed"), (1, "wrong")): D["%s-%s|%s" % (x, b, k)].append(f(x, i) - f(b, i))
    ci = {k: [round(sorted(v)[int(.025 * B)], 1), round(sorted(v)[int(.975 * B) - 1], 1)] for k, v in D.items()}
    J = json.load(open(OUT + "/method.json")); J["stream"] = {"per_model": per, "pooled": pooled, "ci_at_%g" % main: ci}
    json.dump(J, open(OUT + "/method.json", "w"), indent=1); print(json.dumps({"pooled": pooled, "ci": ci}, indent=1))



# VARIANT `keep` (PREREG, 2026-10-28): never rewrite the user's request. The saved first call of decide-then-answer (arm `ours`) is
# reused; only the answer calls are new.
KEEP = "\n\nAnswer this interpretation: %s"


def _keep(q, reads, sql_ctx, call):
    P = AM._dtp_prompts(); sql = lambda text: AM.parse_one(call(P["user_message_sql"].format(sql_ctx, text)))[:1]
    if len(reads) <= 1: return {"texts": [q], "queries": sql(q)}
    texts = [q.rstrip() + KEEP % rd for rd in reads[:4]]
    return {"texts": texts, "queries": [x for t in texts for x in sql(t)]}


def run_keep(workers=6):
    from specbridge.pd.ask import ask
    jobs = []
    for m in MODELS:
        for r in AM.final_rows():
            f, of = _ffs("keep_ambrosia", m, r["row"]), AM._ff("ours", m, r["row"])
            if os.path.exists(f) or not os.path.exists(of): continue
            def j(m=m, r=r, f=f, of=of):
                o = json.load(open(of)); sk = collections.Counter(); sk.update(_cost_saved(of, 1))
                rec = _keep(r["question"], o.get("readings") or [r["question"]], r["dump"], _call(ask, m, sk))
                os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(dict(rec, row=r["row"], model=m, arm="keep", cost=dict(sk)), open(f, "w"), indent=1)
            jobs.append(j)
    ks, WD, C, W = _sets()
    for m in MODELS:
        for k in ks:
            for w in WD[k]:
                f, of = _ffs("keep_sets", m, "%s__%s" % (k, w)), RM._f("ours", m, k, w)
                if os.path.exists(f) or not os.path.exists(of): continue
                def j(m=m, k=k, w=w, f=f, of=of):
                    o = json.load(open(of)); c = C[k]; q = W[k][w]; schema, docs = DB.context(c); sk = collections.Counter(); sk.update(_cost_saved(of, 1))
                    rec = _keep(q, o.get("readings") or [q], schema + "\n\n" + docs, _call(ask, m, sk))
                    os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(dict(rec, case=k, wording=w, model=m, arm="keep", cost=dict(sk)), open(f, "w"), indent=1, default=str)
                jobs.append(j)
    random.Random(31).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, MAXW)) as ex: list(ex.map(lambda j: j(), jobs))


# TWO TURNS (2026-10-28): the setting of products that ask (Genie: a clarifying question). A simulated user with one interpretation in
# mind reads turn 1; if no shown answer gives that interpretation (or the product asked instead of answering), the user states it in
# one turn and the product answers the stated request. The second-turn answer is the SAME for every arm: the model's plain answer to
# the specific request (AMBROSIA's unambiguous question; the set's specific wording), so arms differ only in turn 1. Arm `ask` uses the
# decide-then-answer gate (generous to asking) and returns nothing where it is open; `state` is the one answer of interpret-and-state.
# Units: one per (request, interpretation the user means); a unit with no specific request is skipped for every arm.
def report_twoturn(main=0.2, B=2000):
    from specbridge.comm.common import grade as G
    from specbridge.comm.transfer import reviewed as RV
    refused = collections.defaultdict(set)
    if os.path.exists(AM.FINAL + "/refusals.jsonl"):
        for l in open(AM.FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    arms = ("plain", "samplek", "dtp", "state", "ask", "ours", "method"); st = lambda g, p: g is not None and p is not None and G.shape_tolerant([list(y) for y in g], [list(y) for y in p])
    PA, PU, PS = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)   # unit = (right at turn 1, user turn, right at the end, calls)
    def unit(hit1, calls1, right2):
        return (int(hit1), int(not hit1), int(hit1 or right2), calls1 + (0 if hit1 else 1))
    for m in MODELS:
        SP = AM.final_specifics()
        R = [r for r in AM.final_rows() if r["row"] not in refused.get(m, set()) and all(os.path.exists(AM._ff(a, m, r["row"])) for a in ("plain", "samplek", "dtp", "ours"))]
        for r in R:
            db = r["db_file"]; Q = _arms_amb(m, r); o = json.load(open(AM._ff("ours", m, r["row"]))); op = len(o.get("readings") or []) > 1
            Q["ask"] = ([] if op else o["queries"], 1)
            res = {a: [x for x in (AM._ex_sql(db, q) for q in dict.fromkeys(qs)) if x is not None] for a, (qs, _c) in Q.items()}
            if r["ambiguous"]:
                for g in (AM._ex_sql(db, g) for g in r["gold"]):
                    two = None
                    for k in SP.get(r["row"], []):
                        kr = AM._ex_sql(db, k[2]); f = AM._ff("specific", m, "%s__%d" % (r["row"], k[0]))
                        if kr is not None and g is not None and AM.same(kr, g) and AM.same(g, kr) and os.path.exists(f):
                            q = json.load(open(f))["queries"]; two = st(kr, AM._ex_sql(db, q[0]) if q else None)
                    if two is None: continue
                    u = {a: unit(any(st(g, p) for p in res[a]), Q[a][1], two) for a in arms}
                    PA["_n"].append(r["row"]); [PA[a].append(u[a]) for a in arms]
            else:
                g = AM._ex_sql(db, r["gold"][0]); pq = Q["state"][0]; two = st(g, AM._ex_sql(db, pq[0]) if pq else None)
                for a in arms: PU[a].append(unit(any(st(g, p) for p in res[a]), Q[a][1], two))
        ks, WD, C, _W = _sets(); ks = RV.accepted(ks)
        for k in ks:
            if not all(os.path.exists(RM._f(a, m, k, w)) for a in ("samplek", "dtp", "ours") for w in WD[k]): continue
            c = C[k]; con = DB.connect(c["snapshot"])
            def match(qs):
                out = []
                for q in dict.fromkeys(x for x in qs if x):
                    r_ = DB.rows(con, q)
                    if r_ is not None: out.append(X._match(c, r_))
                return out
            for w in WD[k]:
                o = json.load(open(RM._f("ours", m, k, w))); d = json.load(open(RM._f("dtp", m, k, w))); sk = json.load(open(RM._f("samplek", m, k, w))); op = len(o.get("readings") or []) > 1
                Q = {"samplek": (sk["queries"], 3), "dtp": (d["queries"], d["cost"]["calls"]), "ours": (o["queries"], o["cost"]["calls"]), "ask": ([] if op else o["queries"], 1),
                     "state": ([_plain_main(m, k, w)], 1), "method": (o["queries"] + (d["queries"] if op else []), o["cost"]["calls"] + (d["cost"]["calls"] if op else 0))}
                res = {a: match(qs) for a, (qs, _c) in Q.items()}; res["plain"] = [mt for _q, mt, _r in (RM._answers("plain", m, k, w, C) or [])]; Q["plain"] = (None, 1)
                for lab in (("A", "B") if w == "open" else (w[-1],)):
                    ws = [v for v in WD[k] if v != "open" and v[-1] == lab]
                    if not ws: continue
                    sm = match([_plain_main(m, k, ws[0])]); two = bool(sm) and lab in sm[0]
                    for a in arms: PS[a].append(unit(any(lab in mt for mt in res[a]), Q[a][1], two))
    mean = lambda v, i: sum(x[i] for x in v) / len(v)
    amb = lambda a, i, ia=None, iu=None: 100 * (main * mean([PA[a][j] for j in ia] if ia else PA[a], i) + (1 - main) * mean([PU[a][j] for j in iu] if iu else PU[a], i))
    out = {"units": {"ambrosia_open": len(PA["ours"]), "ambrosia_clear": len(PU["ours"]), "sets": len(PS["ours"])}, "ambrosia_per100": {}, "sets_per100": {}, "ci": {}}
    K = ("right_turn1", "user_turns", "right_end", "calls")
    for a in arms:
        out["ambrosia_per100"][a] = {k: round(amb(a, i), 1) for i, k in enumerate(K)}
        out["sets_per100"][a] = {k: round(100 * mean(PS[a], i), 1) for i, k in enumerate(K)}
    rng = random.Random(11); D = collections.defaultdict(list); nA, nU, nS = len(PA["ours"]), len(PU["ours"]), len(PS["ours"])
    for _ in range(B):
        ia = [rng.randrange(nA) for _ in range(nA)]; iu = [rng.randrange(nU) for _ in range(nU)]; isx = [rng.randrange(nS) for _ in range(nS)]
        for x in ("ours", "method"):
            for b in ("ask", "state", "plain", "dtp"):
                for i, k in enumerate(K):
                    D["amb|%s-%s|%s" % (x, b, k)].append(amb(x, i, ia, iu) - amb(b, i, ia, iu))
                    D["sets|%s-%s|%s" % (x, b, k)].append(100 * (mean([PS[x][j] for j in isx], i) - mean([PS[b][j] for j in isx], i)))
    out["ci"] = {k: [round(sorted(v)[int(.025 * B)], 1), round(sorted(v)[int(.975 * B) - 1], 1)] for k, v in D.items()}
    J = json.load(open(OUT + "/method.json")); J["twoturn"] = out; json.dump(J, open(OUT + "/method.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "ci"}, indent=1))
    print(json.dumps({k: v for k, v in out["ci"].items() if "-ask|" in k or "-state|" in k}, indent=0))


if __name__ == "__main__":
    {"pilot": pilot, "report_pilot": report_pilot, "run_final": run_final, "report_final": report_final, "report_ask": report_ask, "report_method": report_method, "report_budget": report_budget, "report_curve": report_curve, "report_stream": report_stream, "run_keep": run_keep, "report_twoturn": report_twoturn}[sys.argv[1]]()
