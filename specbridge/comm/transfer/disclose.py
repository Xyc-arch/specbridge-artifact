"""ASSUMPTION DISCLOSURE on frozen synthetic cases: does a model compute a supported reading, flag the choice its request leaves
open (and only then), describe its own SQL faithfully, and offer the other supported reading?
    python -m specbridge.comm.transfer.disclose <render dir> sample [--n 30]
    python -m specbridge.comm.transfer.disclose <render dir> run <model> [<model> ...]
    python -m specbridge.comm.transfer.disclose <render dir> judge
    python -m specbridge.comm.transfer.disclose <render dir> report
CASES: a seeded sample of the frozen cases (<render dir>/eval/frozen.json), balanced across decision kinds and step depths; each in
three wordings: precise A, precise B, open (written.json). One call per (case, wording, model); the same frozen instruction for every
model; the model sees the request, schema and documentation -- never the readings, the decision, the reference SQL or the intent.
SCORING BY CODE: the primary query and each alternative executed and matched against reading A and reading B (the case's own graders).
SCORING BY RUBRIC (judge opus, blind to the model): does the response flag the SEEDED decision as unresolved; does it claim that a
decision the wording settles is open; does the stated assumption describe the primary SQL. Judge verdicts are evidence, not proof."""
import collections, concurrent.futures as cf, hashlib, json, os, random, sys, time
from specbridge.comm.common import db as DB

INSTRUCTION = """Answer the request with SQL for the database below. Briefly state any consequential assumption that the request and
the supplied context do not settle. If another interpretation is supported, describe it and give its SQL. Do not invent alternatives
when the context settles the choice.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

Answer ONLY JSON: {"sql": "your primary query", "assumptions": [{"assumption": "what your primary query assumes", "unresolved": true|false}],
"alternatives": [{"interpretation": "another supported reading, in words", "sql": "..."}]}
At most two alternatives; an empty list when the request settles its meaning."""
PROMPT_SHA = hashlib.sha256(INSTRUCTION.encode()).hexdigest()[:12]
WORDINGS = ("precise_A", "precise_B", "open")

JUDGE = """You judge responses to data requests. For each RESPONSE you get the request, one specific DECISION the request may or may
not settle (with its two readings), and the response: its primary SQL, its stated assumptions, its alternatives. You are not told who
wrote the response. Answer per response:
  flags_decision     does the response identify THIS decision as something the request leaves open (in an assumption marked
                     unresolved, or by offering the other reading as an alternative)? true|false
  claims_open_wrongly  does the response claim that THIS decision is unsettled although the REQUEST explicitly settles it? true|false
                     (judge from the request text only)
  faithful           do the stated assumptions describe what the PRIMARY SQL actually computes for this decision? yes|no|not stated
Answer ONLY JSON: [{"id": "...", "flags_decision": ..., "claims_open_wrongly": ..., "faithful": "...", "why": "one sentence"}]

%s"""


# PLAIN SINGLE-CALL CONTROL (2026-10-03): the same call as INSTRUCTION -- same schema, documentation, request, one sealed call,
# no exploration -- without the disclosure sentences, so disclosure overhead is measured like for like.
PLAIN = INSTRUCTION.split("Briefly state")[0].rstrip() + """

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION:
%s

REQUEST:
%s

Answer ONLY JSON: {"sql": "your query"}"""

ALTJUDGE = """You judge ALTERNATIVE interpretations that a response offered for a data request. For each item you get the request
and one alternative (its interpretation in words and its SQL). Is this alternative a reading a careful analyst could
reasonably take from the request and the database context? supported | unsupported. It is unsupported when the request
explicitly settles the point, or the alternative contradicts it, or it changes what is asked rather than interpreting it.
Answer ONLY JSON: [{"id": "...", "verdict": "supported|unsupported", "why": "one sentence"}]

%s"""


def _paths(D): return D + "/eval/frozen.json", D + "/written.json", D + "/disclose"


def bucket(kind):
    k = kind.lower()
    return "signed vs absolute" if "signed" in k else "counting unit" if ("unit" in k or "duplicate" in k) else \
        "missing / sentinel" if ("sentinel" in k or "missing" in k) else "aggregation level"


def sample(D, n=30):
    fz, wr, out = _paths(D); C = json.load(open(fz))["cases"]; rng = random.Random(20261005)
    by = collections.defaultdict(list)
    for c in C: by[bucket(c["kind"])].append(c)
    want = {"aggregation level": n - 3 * (n // 5), "signed vs absolute": n // 5, "counting unit": n // 5, "missing / sentinel": n // 5}
    pick = []
    for b, k in want.items():
        xs = sorted(by[b], key=lambda c: c["case"]); rng.shuffle(xs)
        xs.sort(key=lambda c: c.get("S_depth") or 0)                              # spread across depths: take every k-th
        step = max(1, len(xs) // max(1, k)); pick += xs[::step][:k]
    os.makedirs(out, exist_ok=True)
    json.dump({"seed": 20261005, "prompt_sha": PROMPT_SHA, "cases": [c["case"] for c in pick],
               "by_kind": dict(collections.Counter(bucket(c["kind"]) for c in pick)), "by_depth": dict(collections.Counter("S%s" % c.get("S_depth") for c in pick))},
              open(out + "/sample.json", "w"), indent=1)
    print(len(pick), collections.Counter(bucket(c["kind"]) for c in pick), collections.Counter(c.get("S_depth") for c in pick))


def sample_all(D, seed=20261003, judge_share=0.25):
    """EVERY frozen family (2026-10-03): its OPEN wording plus ONE precise wording, A or B, allocated balanced by a seeded draw
    and the same for every model. A stratified share (by decision type) of the open wordings is marked for the rubric judge
    (decision detection, faithfulness); both-reading coverage and false alternatives are scored by execution on all."""
    fz, wr, out = _paths(D); C = json.load(open(fz))["cases"]; rng = random.Random(seed)
    ks = sorted(c["case"] for c in C); rng.shuffle(ks); half = len(ks) // 2
    prec = {k: ("precise_A" if i < half else "precise_B") for i, k in enumerate(ks)}
    if len(ks) % 2: prec[ks[-1]] = rng.choice(["precise_A", "precise_B"])
    if os.path.exists(out + "/sample.json"):     # EXTEND (2026-10-03): earlier allocations are kept (answers depend on them);
        old = json.load(open(out + "/sample.json"))["wordings"]           # new cases alternate toward balance
        n = collections.Counter(v[1] for k, v in old.items() if k in prec)
        for k in sorted(k for k in prec if k not in old):
            prec[k] = "precise_A" if n["precise_A"] <= n["precise_B"] else "precise_B"; n[prec[k]] += 1
        prec.update({k: v[1] for k, v in old.items() if k in prec})
    typ = {c["case"]: c.get("type") or bucket(c["kind"]) for c in C}; by = collections.defaultdict(list)
    for k in ks: by[typ[k]].append(k)
    judge = sorted(k for t, xs in by.items() for k in xs[:max(1, round(judge_share * len(xs)))])
    os.makedirs(out, exist_ok=True)
    json.dump({"seed": seed, "prompt_sha": PROMPT_SHA, "cases": sorted(ks), "wordings": {k: ["open", prec[k]] for k in ks}, "judge_open": judge,
               "by_type": dict(collections.Counter(typ.values())), "precise_allocation": dict(collections.Counter(prec.values()))},
              open(out + "/sample.json", "w"), indent=1)
    print(len(ks), "cases;", dict(collections.Counter(prec.values())), "; judge", len(judge))


def _match(c, answer):
    from specbridge.comm.transfer.evaluate import matches
    return matches(c, answer) if answer is not None else []


def run(D, models, workers=24):
    from specbridge.comm.common.llm import call, parse
    fz, wr, out = _paths(D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr))
    S = json.load(open(out + "/sample.json")); assert S["prompt_sha"] == PROMPT_SHA, "the instruction changed after sampling"
    def one(job):
        k, w, m = job; f = "%s/%s/%s__%s.json" % (out, m, k.replace(":", "__").replace("/", "_"), w)
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); con = DB.connect(c["snapshot"]); t0 = time.time()
        txt = call(INSTRUCTION % (schema, docs, W[k][w]), m); r = parse(txt, "{") or {}
        prim = r.get("sql"); a = DB.rows(con, prim) if prim else None
        alts = []
        for x in (r.get("alternatives") or [])[:2]:
            if isinstance(x, dict) and x.get("sql"):
                b = DB.rows(con, x["sql"]); alts.append({"interpretation": x.get("interpretation"), "sql": x["sql"], "executes": b is not None, "matches": _match(c, b)})
        o = {"case": k, "wording": w, "model": m, "prompt_sha": PROMPT_SHA, "response": r, "raw": None if r else txt, "primary_executes": a is not None,
             "primary_matches": _match(c, a), "alternatives": alts, "seconds": round(time.time() - t0, 1), "chars_out": len(txt or "")}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    jobs = [(k, w, m) for k in S["cases"] for w in (S.get("wordings", {}).get(k) or WORDINGS) for m in models]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(one, jobs))


def plain(D, models, workers=24):
    """The plain single-call control on exactly the disclosure sample's (case, wording) pairs -> <disclose>/plain/<model>/."""
    from specbridge.comm.common.llm import call, parse
    fz, wr, out = _paths(D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); S = json.load(open(out + "/sample.json"))
    def one(job):
        k, w, m = job; f = "%s/plain/%s/%s__%s.json" % (out, m, k.replace(":", "__").replace("/", "_"), w)
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); t0 = time.time(); txt = call(PLAIN % (schema, docs, W[k][w]), m)
        if not txt: return                                   # a failed call is not an answer: not saved, retried on rerun
        r = parse(txt, "{") or {}; prim = r.get("sql"); a = DB.rows(DB.connect(c["snapshot"]), prim) if prim else None
        o = {"case": k, "wording": w, "model": m, "response": r, "primary_executes": a is not None, "primary_matches": _match(c, a),
             "seconds": round(time.time() - t0, 1), "chars_out": len(txt)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    jobs = [(k, w, m) for k in S["cases"] for w in S["wordings"][k] for m in models]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(one, jobs))


def judge_alternatives(D, workers=8):
    """Every offered alternative (all wordings, all models), judged for support -> <disclose>/judge_alternatives.json."""
    from specbridge.comm.common.llm import ask_json
    fz, wr, out = _paths(D); W = json.load(open(wr)); R = _load(D); jf = out + "/judge_alternatives.json"
    J = json.load(open(jf)) if os.path.exists(jf) else {}
    items = [("%s|%s|%s|%d" % (k[0], k[1], k[2], i), k, a) for k, o in R.items() for i, a in enumerate(o["alternatives"])]
    items = [x for x in items if x[0] not in J]
    anon = {x[0]: hashlib.sha1(x[0].encode()).hexdigest()[:10] for x in items}
    rng = random.Random(7); rng.shuffle(items)
    def one(b):
        body = "\n\n".join("--- %s\nREQUEST: %s\nALTERNATIVE: %s\nSQL: %s" % (anon[i], W[k[0]][k[1]], a.get("interpretation"), (a.get("sql") or "")[:600]) for i, k, a in b)
        got = ask_json(ALTJUDGE % body, "opus", brace="[") or []; back = {anon[i]: i for i, _k, _a in b}
        return {back[g["id"]]: g for g in got if isinstance(g, dict) and g.get("id") in back}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for d in ex.map(one, [items[i:i + 5] for i in range(0, len(items), 5)]): J.update(d)
    json.dump(J, open(jf, "w"), indent=1); print("alternatives judged", len(J))


def _load(D):
    fz, wr, out = _paths(D); R = {}
    for m in os.listdir(out):
        if not os.path.isdir(os.path.join(out, m)) or m in ("judge", "plain", "complement", "topk", "incontext"): continue
        for f in os.listdir(os.path.join(out, m)):
            o = json.load(open(os.path.join(out, m, f))); R[(o["case"], o["wording"], m)] = o
    return R


def judge(D, workers=8, scope="sample"):
    from specbridge.comm.common.llm import ask_json
    fz, wr, out = _paths(D); W = json.load(open(wr)); R = _load(D); jf = out + "/judge.json"
    J = json.load(open(jf)) if os.path.exists(jf) else {}
    S = json.load(open(out + "/sample.json")); only = set(S.get("judge_open") or [])
    if scope == "all": only = set()                          # EVERY saved response (2026-10-03): full-population rates
    keys = sorted(k for k in R if "%s|%s|%s" % k not in J and (not only or (k[0] in only and k[1] == "open") or (k[1] != "open" and R[k]["alternatives"])))
    # precise wordings are judged only where the model offered an alternative: candidates for a false "open" claim
    anon = {k: hashlib.sha1(("%s|%s|%s" % k).encode()).hexdigest()[:10] for k in keys}        # the judge never sees the model
    def block(k):
        o = R[k]; r = o["response"] or {}; w = W[k[0]]
        return "--- %s\nREQUEST: %s\nDECISION: reading A = %s | reading B = %s\nPRIMARY SQL: %s\nASSUMPTIONS: %s\nALTERNATIVES: %s" % (
            anon[k], w[k[1]], w["reading_A"], w["reading_B"], (r.get("sql") or "")[:900], json.dumps(r.get("assumptions"))[:900],
            json.dumps([{"interpretation": a.get("interpretation"), "sql": (a.get("sql") or "")[:400]} for a in (r.get("alternatives") or [])[:2]])[:1400])
    rng = random.Random(5); keys = keys[:]; rng.shuffle(keys)                               # models interleaved within a judge call
    def one(b):
        got = ask_json(JUDGE % "\n\n".join(block(k) for k in b), "opus", brace="[") or []
        back = {anon[k]: k for k in b}
        return {"%s|%s|%s" % back[g["id"]]: g for g in got if isinstance(g, dict) and g.get("id") in back}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for d in ex.map(one, [keys[i:i + 5] for i in range(0, len(keys), 5)]): J.update(d)
    json.dump(J, open(jf, "w"), indent=1); print("judged", len(J))


def report(D):
    fz, wr, out = _paths(D); R = _load(D); J = json.load(open(out + "/judge.json")) if os.path.exists(out + "/judge.json") else {}
    S = json.load(open(out + "/sample.json")); models = sorted({k[2] for k in R}, key=lambda m: ["haiku", "sonnet", "opus"].index(m) if m in ("haiku", "sonnet", "opus") else 9)
    pct = lambda a, b: "%d/%d" % (a, b)
    L = ["# Assumption disclosure: %d frozen cases x 3 wordings x %d models (one call each; prompt %s)\n" % (len(S["cases"]), len(models), PROMPT_SHA),
         "Code: the primary query and alternatives executed and matched to reading A / B. Rubric (opus, blind to the model): flags the seeded "
         "decision; claims a settled decision is open; assumptions describe the primary SQL.\n",
         "| model | precise: primary = its reading | open: primary = A or B | open: A and B both in the answer set | open: flags the seeded decision | precise: claims it open wrongly | precise: offers any alternative | assumptions faithful (all) | sec/call |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in models:
        pr = [R[(k, w, m)] for k in S["cases"] for w in ("precise_A", "precise_B") if (k, w, m) in R]
        op = [R[(k, "open", m)] for k in S["cases"] if (k, "open", m) in R]
        own = sum(o["wording"][-1] in o["primary_matches"] for o in pr)
        either = sum(bool(o["primary_matches"]) for o in op)
        both = sum({"A", "B"} <= set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]} for o in op)
        jget = lambda o, f: (J.get("%s|%s|%s" % (o["case"], o["wording"], m)) or {}).get(f)
        flag = sum(jget(o, "flags_decision") is True for o in op); wrong = sum(jget(o, "claims_open_wrongly") is True for o in pr)
        anyalt = sum(bool(o["alternatives"]) for o in pr)
        allo = pr + op; fa = [jget(o, "faithful") for o in allo]; fy = sum(x == "yes" for x in fa); fd = sum(x in ("yes", "no") for x in fa)
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %.1f |" % (m, pct(own, len(pr)), pct(either, len(op)), pct(both, len(op)), pct(flag, len(op)),
                 pct(wrong, len(pr)), pct(anyalt, len(pr)), pct(fy, fd), sum(o["seconds"] for o in allo) / max(1, len(allo))))
    L += ["\nBy decision kind (open wording): flags the seeded decision / A and B both covered\n", "| model | " + " | ".join(sorted({bucket(c) for c in []}) or ["kind"]) + " |"]
    kinds = sorted({bucket(json.load(open(fz)) and next(c["kind"] for c in json.load(open(fz))["cases"] if c["case"] == k)) for k in S["cases"]})
    K = {c["case"]: bucket(c["kind"]) for c in json.load(open(fz))["cases"]}
    L[-1] = "| model | " + " | ".join(kinds) + " |"; L.append("|---|" + "---|" * len(kinds))
    for m in models:
        cells = []
        for kd in kinds:
            op = [R[(k, "open", m)] for k in S["cases"] if K[k] == kd and (k, "open", m) in R]
            fl = sum((J.get("%s|open|%s" % (o["case"], m)) or {}).get("flags_decision") is True for o in op)
            bo = sum({"A", "B"} <= set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]} for o in op)
            cells.append("%d / %d of %d" % (fl, bo, len(op)))
        L.append("| %s | %s |" % (m, " | ".join(cells)))
    open(out + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]; D = a[0]
    if a[1] == "sample": sample(D, int(a[a.index("--n") + 1]) if "--n" in a else 30)
    elif a[1] == "sample-all": sample_all(D)
    elif a[1] == "run": run(D, a[2:], int(os.environ.get("TRANSFER_WORKERS", 24)))
    elif a[1] == "judge": judge(D)
    elif a[1] == "judge-all": judge(D, scope="all")
    elif a[1] == "judge-alternatives": judge_alternatives(D)
    elif a[1] == "plain": plain(D, a[2:], int(os.environ.get("TRANSFER_WORKERS", 24)))
    else: report(D)
