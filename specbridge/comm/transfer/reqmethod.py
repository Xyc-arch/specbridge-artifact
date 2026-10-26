"""AMBIGUITY METHODS ON THE REQUEST SETS (2026-10-13): data-side choices (the planted choice of each set), 30 dev sets (ledger.sets),
the open wording and the set's specific wording. Sonnet and GPT-Sol. Arms (context = the same schema and documentation):
    plain     the explanation call (saved, disclose)
    samplek   the explanation call 3 times, answers combined (k = 3, as on AMBROSIA)
    dtp       disambiguate-then-parse, released prompts: interpretations -> missing ones -> one SQL per interpretation
    ours      detect readings (ambrosia.DETECT) -> one SQL per reading -> drop identical results -> answer set
    ours+lib  ours + library-rule edits of the main SQL that run and change the answer (code only)
Metrics: open -- both readings covered (execution), names the choice (Opus judge, blind to arm and model); specific -- main SQL
right, false alarm (an answer returns the other reading); computable misses recovered (readings the plain open answer missed that
the solver computes from its specific request in one call: disclose + complement runs); calls and characters per wording.
    python -m specbridge.comm.transfer.reqmethod run | report"""
import collections, concurrent.futures as cf, hashlib, json, math, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X, ledger as LG, ambrosia as AM, combined as CB
from specbridge.comm.diagnose import rules as RU

OUT = os.environ.get("REQMETHOD_OUT", "out/reqmethod"); MODELS = ("sonnet", "gpt-6-sol"); K = 3; SEED = 20261022
N = int(os.environ.get("REQMETHOD_N", 0))       # 0: the 30 dev sets of ledger.sets (the paper's Table 4); else N ACCEPTED sets
MAXW = int(os.environ.get("SB_MAX_WORKERS", 6))  # the machine's limit on concurrent calls (6 unless the user allows more)


def chosen():
    """The sets and their wordings. With N: the accepted sets among the 30 dev sets first, then the other accepted sets in a
    seeded order, up to N -- so a larger run contains the smaller one. Both from the first construction run; the filter sets
    then join at the same rate (combined.extend_accepted)."""
    ks, WD = LG.sets()
    if not N: return ks, WD
    frozen = OUT + "/sets.json"            # the draw is frozen once run: a later verdict change removes sets, never redraws
    if os.path.exists(frozen): return json.load(open(frozen))["sets"], WD
    from specbridge.comm.transfer import reviewed as RV
    rest = sorted(k for k in CB.part_cases(0) if k not in ks); random.Random(SEED).shuffle(rest)
    return CB.extend_accepted((RV.accepted(ks) + RV.accepted(rest))[:N], SEED), WD


def _f(arm, m, k, w):
    f = "%s/%s/%s/%s__%s.json" % (OUT, arm, m, k.replace(":", "__").replace("/", "_"), w); os.makedirs(os.path.dirname(f), exist_ok=True); return f


def _ctx(c):
    schema, docs = DB.context(c); return "DATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s" % (schema, docs)


def run(workers=6):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    P = AM._dtp_prompts(); fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, WD = chosen()
    def call(p, m, sink):
        try: t = ask(p, m, timeout=1500, quiet=True) or ""
        except Exception as e: t = ""; sink["failed"] += 1
        sink["calls"] += 1; sink["chars_in"] += len(p); sink["chars_out"] += len(t); return t
    def sqls_expl(t):
        r = jparse(t, "{") or {}; return [r.get("sql")] + [x.get("sql") for x in (r.get("alternatives") or []) if isinstance(x, dict)], r
    def job(j):
        arm, m, k, w = j; f = _f(arm, m, k, w)
        if os.path.exists(f): return
        c = C[k]; q = W[k][w]; schema, docs = DB.context(c); s = collections.Counter(); out = {}
        if arm == "samplek":
            qs = []; resp = []
            for _ in range(K):
                a, r = sqls_expl(call(X.INSTRUCTION % (schema, docs, q), m, s)); qs += [x for x in a if x]; resp.append(r)
            out = {"queries": qs, "responses": resp}
        elif arm == "dtp":
            t = call(P["user_message_interpr_ambig"].format(_ctx(c), q), m, s)
            if not t.strip(): return
            ints = [AM.item_line(x) for x in t.splitlines() if AM.item_line(x)]
            miss = call(P["user_message_interpr_ambig_missing"].format(_ctx(c), q, "\n".join(ints)), m, s)
            if "all possible interpretations are covered" not in miss.lower():
                ints += [AM.item_line(x) for x in miss.splitlines() if AM.item_line(x)]
            qs = [x for it in ints[:6] for x in AM.parse_one(call(P["user_message_sql"].format(schema + "\n\n" + docs, it), m, s))[:1]]
            out = {"interpretations": ints, "queries": qs, "raw": [t, miss]}
        else:                                                         # ours
            t = call(AM.DETECT % (_ctx(c), q), m, s)
            if not t.strip(): return
            reads = [x for x in ((jparse(t, "{") or {}).get("readings") or []) if isinstance(x, str) and x.strip()] or [q]
            qs = [x for rd in (reads[:1] if len(reads) == 1 else reads[:4]) for x in AM.parse_one(call(P["user_message_sql"].format(schema + "\n\n" + docs, rd), m, s))[:1]]
            out = {"readings": reads, "queries": qs, "raw": [t]}
        json.dump(dict(out, case=k, wording=w, model=m, arm=arm, cost=dict(s)), open(f, "w"), indent=1, default=str)
    jobs = [(a, m, k, w) for k in ks for w in WD[k] for m in MODELS for a in ("samplek", "dtp", "ours")]
    random.Random(SEED).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, MAXW)) as ex: list(ex.map(job, jobs))
    judge(); report()


def _plain_f(m, k, w):
    """The explanation-call answer this comparison was run against. The LiveSQLBench sets were later re-answered with the SQLite
    dialect named (dialect_rerun.merge); every other arm here used the first prompt, so the first-run answer is kept for them."""
    f = "%s/%s/%s__%s.json" % (X._paths(LG.D)[2], m, k.replace(":", "__").replace("/", "_"), w)
    a = os.path.join("out/archive/first-run-livesql", f)
    return a if os.path.exists(a) else f


def _answers(arm, m, k, w, C):
    """The answer set an arm returns: [(sql, matches)]; None when not available."""
    c = C[k]; con = DB.connect(c["snapshot"])
    if arm == "plain":
        f = _plain_f(m, k, w)
        if not os.path.exists(f): return None
        o = json.load(open(f)); r = o.get("response") or {}
        qs = [r.get("sql")] + [x.get("sql") for x in (r.get("alternatives") or []) if isinstance(x, dict)]
    else:
        f = _f("ours" if arm == "ours+lib" else arm, m, k, w)
        if not os.path.exists(f): return None
        qs = json.load(open(f))["queries"]
    qs = [q for q in qs if q]; res = []
    seen = []
    for q in qs:                                                      # drop identical results (for every arm: equal footing)
        rows = DB.rows(con, q)
        if rows is None: continue
        key = json.dumps(sorted(map(repr, rows)))
        if key in seen: continue
        seen.append(key); res.append((q, X._match(c, rows), rows))
    if arm == "ours+lib" and res:
        base = res[0]
        for st in RU.sites(base[0]):
            if st[0] == "dedup": continue
            e = RU.edit(base[0], st); rows = DB.rows(con, e) if e else None
            if rows is None: continue
            key = json.dumps(sorted(map(repr, rows)))
            if key not in seen: seen.append(key); res.append((e, X._match(c, rows), rows))
    return res


def judge(batch=6):
    from specbridge.comm.common.llm import ask_json
    fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, _WD = chosen()
    jf = OUT + "/judge.json"; J = json.load(open(jf)) if os.path.exists(jf) else {}; items = []
    for m in MODELS:
        for k in ks:
            for a in ("plain", "samplek", "dtp", "ours"):
                key = "%s|%s|%s" % (k, m, a)
                if key in J: continue
                if a == "plain":
                    f = _plain_f(m, k, "open")
                    if not os.path.exists(f): continue
                    r = json.load(open(f)).get("response") or {}; said = {"assumptions": r.get("assumptions"), "alternatives": [x.get("interpretation") for x in (r.get("alternatives") or []) if isinstance(x, dict)]}
                else:
                    f = _f(a, m, k, "open")
                    if not os.path.exists(f): continue
                    o = json.load(open(f))
                    said = {"readings offered": o.get("interpretations") or o.get("readings")} if a != "samplek" else {
                        "assumptions": [x.get("assumptions") for x in o.get("responses", [])], "alternatives": [[y.get("interpretation") for y in (x.get("alternatives") or []) if isinstance(y, dict)] for x in o.get("responses", [])]}
                items.append((key, k, said))
    rng = random.Random(3); rng.shuffle(items); anon = {i[0]: hashlib.sha1(i[0].encode()).hexdigest()[:10] for i in items}
    def one(b):
        body = "\n\n".join("--- %s\nREQUEST: %s\nDECISION: %s (reading A vs reading B)\nWHAT THE RESPONSE SAID: %s" % (anon[key], W[k]["open"], C[k]["kind"], json.dumps(said, ensure_ascii=False)[:1800]) for key, k, said in b)
        got = ask_json(X.JUDGE % body, "opus", brace="[") or []; back = {anon[key]: key for key, _k, _s in b}
        return {back[g["id"]]: g for g in got if isinstance(g, dict) and g.get("id") in back}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for d in ex.map(one, [items[i:i + batch] for i in range(0, len(items), batch)]): J.update(d)
    json.dump(J, open(jf, "w"), indent=1)


def report(B=2000):
    from specbridge.comm.transfer import reviewed as RV
    fz, wr, out = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; ks, WD = chosen(); ks = RV.accepted(ks)
    J = json.load(open(OUT + "/judge.json")) if os.path.exists(OUT + "/judge.json") else {}; comp = out + "/complement"
    JS = {}
    L = ["# Ambiguity methods on %s request sets (`specbridge.comm.transfer.reqmethod`)\n" % (N or "30 dev"),
         "Answer sets after dropping identical results (every arm). Computable miss: a reading the plain open answer missed that the solver "
         "computes from its specific request in one call. Paired bootstrap over sets for ours vs each arm.\n"]
    for m in MODELS:
        def computable(k, x):
            for d in ("%s/%s" % (out, m), "%s/%s" % (comp, m)):
                f = "%s/%s__precise_%s.json" % (d, k.replace(":", "__").replace("/", "_"), x)
                if os.path.exists(f): return x in json.load(open(f)).get("primary_matches", [])
            return False
        arms = ("plain", "samplek", "dtp", "ours", "ours+lib"); R = {}
        for a in arms:
            for k in ks:
                for w in WD[k]: R[(a, k, w)] = _answers(a, m, k, w, C)
        sets = [k for k in ks if all(R[(a, k, w)] is not None for a in arms for w in WD[k])]
        cm = [(k, x) for k in sets for x in ("A", "B") if computable(k, x) and x not in {y for _q, mt, _r in R[("plain", k, "open")] for y in mt}]
        L += ["## %s (%d sets; %d computable misses)\n" % (m, len(sets), len(cm)),
              "| arm | open: both readings | open: names the choice | computable misses recovered | specific: main right | specific: false alarm | answers per wording | calls / chars in per wording |", "|---|---|---|---|---|---|---|---|"]
        per = {}
        for a in arms:
            cov = [int({"A", "B"} <= {y for _q, mt, _r in R[(a, k, "open")] for y in mt}) for k in sets]
            nm = [int(bool((J.get("%s|%s|%s" % (k, m, a.replace("+lib", ""))) or {}).get("flags_decision"))) for k in sets]
            rc = sum(x in {y for _q, mt, _r in R[(a, k, "open")] for y in mt} for k, x in cm)
            Ps = [(k, w) for k in sets for w in WD[k] if w != "open"]
            right = sum(bool(R[(a, k, w)]) and w[-1] in R[(a, k, w)][0][1] for k, w in Ps)
            fa = sum(any(("B" if w.endswith("A") else "A") in mt for _q, mt, _r in R[(a, k, w)]) for k, w in Ps)
            nq = sum(len(R[(a, k, w)]) for k in sets for w in WD[k]) / max(1, sum(len(WD[k]) for k in sets))
            cs = []
            if a not in ("plain",):
                for k in sets:
                    for w in WD[k]:
                        f = _f("ours" if a == "ours+lib" else a, m, k, w)
                        if os.path.exists(f): cs.append(json.load(open(f)).get("cost", {}))
            cost = "%.1f / %d" % (sum(c.get("calls", 0) for c in cs) / len(cs), sum(c.get("chars_in", 0) for c in cs) / len(cs)) if cs else "1 / saved"
            per[a] = {"cov": cov, "nm": nm, "rc": [int(x in {y for _q, mt, _r in R[(a, k, "open")] for y in mt}) for k, x in cm]}
            JS.setdefault(m, {"sets": len(sets), "computable": len(cm), "arms": {}})["arms"][a] = {"both": sum(cov), "names": sum(nm), "recovered": rc, "right": right,
                "specific": len(Ps), "false_alarm": fa, "answers": nq, "cost": cost}
            L.append("| %s | %d / %d | %d / %d | %d of %d | %d / %d | %d | %.1f | %s |" % (a, sum(cov), len(sets), sum(nm), len(sets), rc, len(cm), right, len(Ps), fa, nq, cost))
        rng = random.Random(SEED)
        def pci(d):
            if not d: return "n/a"
            b = sorted(sum(d[rng.randrange(len(d))] for _ in d) / len(d) for _ in range(B)); return "%+.2f [%.2f, %.2f]" % (sum(d) / len(d), b[int(.025 * B)], b[int(.975 * B) - 1])
        def mcnemar(x, y):          # exact two-sided McNemar on paired 0/1 lists: (ours only, other only, p)
            b_, c_ = sum(1 for u, v in zip(x, y) if u and not v), sum(1 for u, v in zip(x, y) if v and not u); n = b_ + c_
            p = min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b_, c_) + 1)) / 2 ** n) if n else 1.0
            return [b_, c_, round(p, 5)]
        rt = lambda a: [int(bool(R[(a, k, w)]) and w[-1] in R[(a, k, w)][0][1]) for k in sets for w in WD[k] if w != "open"]
        JS[m]["mcnemar"] = {"both_ours_vs_samplek": mcnemar(per["ours"]["cov"], per["samplek"]["cov"]),
                            "right_ours_vs_samplek": mcnemar(rt("ours"), rt("samplek"))}
        for o in ("ours", "ours+lib"):
            for b in ("dtp", "samplek", "plain"):
                L.append("%s - %s (paired): both readings %s; names the choice %s; computable misses recovered %s." % (o, b, pci([x - y for x, y in zip(per[o]["cov"], per[b]["cov"])]),
                         pci([x - y for x, y in zip(per[o]["nm"], per[b]["nm"])]), pci([x - y for x, y in zip(per[o]["rc"], per[b]["rc"])])))
        L.append("")
    os.makedirs(OUT, exist_ok=True); json.dump(JS, open(OUT + "/results.json", "w"), indent=1)
    open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


EDIT = """A data request and a list of interpretations of it. For EACH interpretation, write ONE short clause (at most 15 words) that
states only what this interpretation decides that the request leaves open, phrased so it can be appended to the request unchanged
(e.g. "Count each customer once."). Do not restate the rest of the request. Merge interpretations that decide the same thing.
Answer ONLY JSON: {"clauses": ["...", "..."]}

REQUEST: %s

INTERPRETATIONS:
%s"""


def run_edit(wordings=("open",), workers=6):
    """Arm `edit` (out/reqmethod/edit/GATE.md): DtP's saved interpretations -> one clause each (one call) -> original request + clause
    -> one SQL call per edited request."""
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    P = AM._dtp_prompts(); fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, WD = LG.sets()
    def call(p, m, sink):
        try: t = ask(p, m, timeout=1500, quiet=True) or ""
        except Exception: t = ""; sink["failed"] += 1
        sink["calls"] += 1; sink["chars_in"] += len(p); sink["chars_out"] += len(t); return t
    def job(j):
        m, k, w = j; f = _f("edit", m, k, w); d = _f("dtp", m, k, w)
        if os.path.exists(f) or not os.path.exists(d): return
        c = C[k]; q = W[k][w]; schema, docs = DB.context(c); s = collections.Counter(json.load(open(d)).get("cost", {}))  # listing cost counted
        ints = json.load(open(d))["interpretations"][:6]
        cl = [x.strip() for x in ((jparse(call(EDIT % (q, "\n".join("- " + i for i in ints)), m, s), "{") or {}).get("clauses") or []) if isinstance(x, str) and x.strip()][:4]
        if len(cl) <= 1: cl = cl or [""]
        edited = [(q.rstrip() + " " + x).strip() for x in cl]
        qs = [x for e in edited for x in AM.parse_one(call(P["user_message_sql"].format(schema + "\n\n" + docs, e), m, s))[:1]]
        json.dump({"clauses": cl, "edited": edited, "queries": qs, "case": k, "wording": w, "model": m, "arm": "edit", "cost": dict(s)}, open(f, "w"), indent=1, default=str)
    jobs = [(m, k, w) for k in ks for w in WD[k] if w in wordings for m in MODELS]; random.Random(SEED).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(job, jobs))
    report_edit()


def report_edit():
    fz, _wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; ks, WD = LG.sets(); L = ["# Arm `edit` vs saved arms, 30 dev request sets (gate: out/reqmethod/edit/GATE.md)\n"]
    for m in MODELS:
        L += ["## %s\n" % m, "| arm | open: both readings | specific: main right | specific: false alarm | calls per open wording |", "|---|---|---|---|---|"]
        for a in ("plain", "samplek", "dtp", "ours", "edit"):
            op = [_answers(a, m, k, "open", C) for k in ks]; cov = sum(r is not None and {"A", "B"} <= {y for _q, mt, _r in r for y in mt} for r in op); n = sum(r is not None for r in op)
            sp = [(w, _answers(a, m, k, w, C)) for k in ks for w in WD[k] if w != "open"]; sp = [(w, r) for w, r in sp if r is not None]
            right = sum(bool(r) and w[-1] in r[0][1] for w, r in sp); fa = sum(any(("B" if w.endswith("A") else "A") in mt for _q, mt, _r in r) for w, r in sp)
            cs = [json.load(open(_f(a, m, k, "open"))).get("cost", {}) for k in ks if a != "plain" and os.path.exists(_f(a, m, k, "open"))]
            if a == "edit":                                                  # own calls + DtP's two listing calls (not DtP's SQL calls)
                cs = [{"calls": json.load(open(_f(a, m, k, "open")))["cost"]["calls"] - json.load(open(_f("dtp", m, k, "open")))["cost"]["calls"] + 2} for k in ks if os.path.exists(_f(a, m, k, "open"))]
            L.append("| %s | %d / %d | %s | %s | %s |" % (a, cov, n, "%d / %d" % (right, len(sp)) if sp else "-", fa if sp else "-", "%.1f" % (sum(c.get("calls", 0) for c in cs) / len(cs)) if cs else "1"))
        L.append("")
    open(OUT + "/edit/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


DETECT_EDIT = """You are given a database and a question about it. Decide whether the question has more than one reasonable reading on THIS
database -- readings that a careful analyst could each intend and that would give different answers. If it has one reading, return
an empty list. If it has several, give ONE short clause per reading (at most 20 words) that states only what that reading decides,
written so it can be appended to the question unchanged (e.g. "Count each customer once."). Do not invent readings the question
rules out.

Database:
%s

Question:
%s

Answer ONLY JSON: {"clauses": ["<clause for reading 1>", ...]}"""


def run_ours_edit(workers=6):
    """Arm `ours_edit` (out/reqmethod/ours_edit/GATE.md): the listing call gives one clause per reading; each reading = the original
    request verbatim + the clause; one SQL call per reading; merge as every arm."""
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    P = AM._dtp_prompts(); fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, WD = LG.sets()
    def call(p, m, sink):
        try: t = ask(p, m, timeout=1500, quiet=True) or ""
        except Exception: t = ""; sink["failed"] += 1
        sink["calls"] += 1; sink["chars_in"] += len(p); sink["chars_out"] += len(t); return t
    def job(j):
        m, k, w = j; f = _f("ours_edit", m, k, w)
        if os.path.exists(f): return
        c = C[k]; q = W[k][w]; schema, docs = DB.context(c); s = collections.Counter()
        t = call(DETECT_EDIT % (_ctx(c), q), m, s)
        if not t.strip(): return
        cl = [x.strip() for x in ((jparse(t, "{") or {}).get("clauses") or []) if isinstance(x, str) and x.strip()]
        reads = [q] if len(cl) <= 1 else [q.rstrip() + " " + x for x in cl[:4]]
        qs = [x for rd in reads for x in AM.parse_one(call(P["user_message_sql"].format(schema + "\n\n" + docs, rd), m, s))[:1]]
        json.dump({"clauses": cl, "readings": reads, "queries": qs, "case": k, "wording": w, "model": m, "arm": "ours_edit", "cost": dict(s)}, open(f, "w"), indent=1, default=str)
    jobs = [(m, k, w) for k in ks for w in WD[k] for m in MODELS]; random.Random(SEED).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(job, jobs))
    report_ours_edit()


def report_ours_edit():
    fz, _wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; ks, WD = LG.sets()
    L = ["# Arm `ours_edit` vs saved arms, 30 dev request sets (gate: out/reqmethod/ours_edit/GATE.md)\n"]
    for m in MODELS:
        L += ["## %s\n" % m, "| arm | open: both readings | specific: main right | specific: false alarm | calls per request (all wordings) |", "|---|---|---|---|---|"]
        for a in ("plain", "samplek", "ours", "ours_edit"):
            op = [_answers(a, m, k, "open", C) for k in ks]; cov = sum(r is not None and {"A", "B"} <= {y for _q, mt, _r in r for y in mt} for r in op); n = sum(r is not None for r in op)
            sp = [(w, _answers(a, m, k, w, C)) for k in ks for w in WD[k] if w != "open"]; sp = [(w, r) for w, r in sp if r is not None]
            right = sum(bool(r) and w[-1] in r[0][1] for w, r in sp); fa = sum(any(("B" if w.endswith("A") else "A") in mt for _q, mt, _r in r) for w, r in sp)
            cs = [json.load(open(_f(a, m, k, w))).get("cost", {}) for k in ks for w in WD[k] if a != "plain" and os.path.exists(_f(a, m, k, w))]
            L.append("| %s | %d / %d | %d / %d | %d | %s |" % (a, cov, n, right, len(sp), fa, "%.1f" % (sum(c.get("calls", 0) for c in cs) / len(cs)) if cs else "1"))
        L.append("")
    os.makedirs(OUT + "/ours_edit", exist_ok=True); open(OUT + "/ours_edit/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: run(int(os.environ.get("REQMETHOD_WORKERS", 6))), "report": report, "judge": judge, "edit": lambda: run_edit(tuple(sys.argv[2:]) or ("open",)), "report_edit": report_edit, "ours_edit": run_ours_edit, "report_ours_edit": report_ours_edit}[sys.argv[1]]()
