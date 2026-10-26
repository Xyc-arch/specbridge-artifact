"""SAME-FAMILY CHECK ON THE OPEN REQUESTS (2026-10-26, co-author comment). Opus wrote every request set and Opus and Sonnet
reviewed them; Haiku and Sonnet are evaluated. On 60 random accepted sets, GPT-Sol writes the open request again from the SAME
plan (shared requirements, the two readings, the two specific requests) with the writer's own step-4 instruction; the new open
request passes the same review (Opus and Sonnet: fidelity to the shared requirements, both readings acceptable to at least one
reviewer); the four models answer it with the same explanation call as the original open request; the same blind Opus judge
decides whether a response names the choice. Both versions are compared on the same sets, paired.
    python -m specbridge.comm.transfer.writer_swap_open sample | write | review | answer | judge | report   -> out/writer_swap_open/
At most 6 workers per step unless stated."""
import collections, concurrent.futures as cf, hashlib, json, os, random, re, sys
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json, call, parse
from specbridge.comm.transfer import combined as CB, disclose as X, reviewed as RV, render as RN, dialect_rerun as DR

OUT = "out/writer_swap_open"; N, SEED, WRITER = 60, 20261026, "gpt-6-sol"; MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
R = CB.D; WORKERS = int(os.environ.get("SWAP_WORKERS", 6))
STEP4 = RN.WRITE.split("4. OPEN:")[1].split("\n%s")[0]
WRITE_OPEN = """You render a data question for a task where ONE interpretation choice is to be left open. The plan and the two precise
questions are given. Write only the OPEN question.
OPEN:""" + STEP4 + """
Answer ONLY JSON: {"favouring_phrases": [{"phrase": "...", "favours": "A|B", "handling": "..."}], "open": "..."}

DATABASE %s -- SCHEMA:
%s

DOCUMENTATION:
%s

SHARED REQUIREMENTS:
%s
READING A: %s
READING B: %s
PRECISE A: %s
PRECISE B: %s"""


def _C(): return {c["case"]: c for c in json.load(open(R + "/eval/frozen.json"))["cases"]}
def _W(): return json.load(open(R + "/written.json"))
def _S(): return json.load(open(OUT + "/sample.json"))["cases"]
def _J(name, default=None): p = "%s/%s" % (OUT, name); return json.load(open(p)) if os.path.exists(p) else default
def _save(name, obj): os.makedirs(OUT, exist_ok=True); json.dump(obj, open("%s/%s" % (OUT, name), "w"), indent=1, default=str)
def _name(k): return k.replace(":", "__").replace("/", "_")


def sample():
    ks = RV.accepted(sorted(_C())); pick = sorted(random.Random(SEED).sample(ks, N))
    _save("sample.json", {"seed": SEED, "n": N, "from": len(ks), "cases": pick}); print(len(pick), "of", len(ks))


def write():
    C, W = _C(), _W(); out = _J("written.json", {})
    def one(k):
        if k in out and out[k].get("open"): return
        c, w = C[k], W[k]; schema, docs = DB.context(c)
        r = ask_json(WRITE_OPEN % (c["database"], schema, docs, RN.reqs(w["shared"]), w["reading_A"], w["reading_B"], w["precise_A"], w["precise_B"]), WRITER) or {}
        out[k] = {"open": r.get("open"), "favouring_phrases": r.get("favouring_phrases"), "writer": WRITER}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex: list(ex.map(one, _S()))
    _save("written.json", out); print("written", sum(1 for v in out.values() if v.get("open")), "of", len(_S()))


def review():
    """Same prompts and acceptance rule as render.review / render.judge, for the open request only."""
    C, W, NW = _C(), _W(), _J("written.json"); ks = [k for k in _S() if (NW.get(k) or {}).get("open")]
    rng = random.Random(11); items = collections.defaultdict(list)
    for k in ks:
        w = W[k]; q = NW[k]["open"]; swap = rng.random() < 0.5; r1, r2 = (w["reading_B"], w["reading_A"]) if swap else (w["reading_A"], w["reading_B"])
        items[(C[k]["database"], "interp")].append((k, swap, "--- ITEM %s\nREQUEST: \"\"\"%s\"\"\"\n   R1: %s\n   R2: %s" % (k, q, r1, r2)))
        items[(C[k]["database"], "fidelity")].append((k, None, "--- ITEM %s\nQUESTION: \"\"\"%s\"\"\"\nREQUIREMENTS: %s" % (k, q, RN.reqs(w["shared"]))))
    jobs = []
    for (db, kind), its in items.items():
        schema, docs = DB.context(next(C[k] for k, _s, _t in its))
        for i in range(0, len(its), 6):
            ch = its[i:i + 6]
            for m in ("opus", "sonnet"): jobs.append((kind, m, ch, (RN.INTERPB if kind == "interp" else RN.FIDEL) % ("\n\n".join(c[2] for c in ch), schema, docs)))
    def one(j):
        kind, m, ch, p = j; got = {d.get("item"): d for d in (ask_json(p, m, brace="[") or []) if isinstance(d, dict)}; res = []
        for k, swap, _t in ch:
            g = got.get(k)
            if kind == "fidelity": res.append((k, kind, m, {"parsed": g is not None, "fail": [x for x in (g or {}).get("requirements", []) if x.get("verdict") != "preserved"], "added": (g or {}).get("added") or []}))
            else:
                rd = {x.get("reading"): x for x in (g or {}).get("readings", []) if isinstance(x, dict)}; a, b = ("R2", "R1") if swap else ("R1", "R2")
                res.append((k, kind, m, {"parsed": g is not None, "A": rd.get(a, {}), "B": rd.get(b, {})}))
        return res
    rec = {k: {"interp": {}, "fidelity": {}} for k in ks}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for res in ex.map(one, jobs):
            for k, kind, m, r in res: rec[k][kind][m] = r
    for k, r in rec.items():
        v = lambda m, x: (r["interp"].get(m) or {}).get(x, {}).get("verdict")
        acc = [m for m in ("opus", "sonnet") if RN.fits(v(m, "A")) and RN.fits(v(m, "B"))]
        r["label"] = "mutually recognized open" if len(acc) == 2 else "disputed open" if acc else "not supported"
        r["fidelity_ok"] = len(r["fidelity"]) == 2 and all(x["parsed"] and not x["fail"] and not x["added"] for x in r["fidelity"].values())
        r["accepted"] = r["fidelity_ok"] and r["label"] != "not supported"
    _save("review.json", rec); print(collections.Counter((r["label"], r["fidelity_ok"]) for r in rec.values()))


def _prompt(c):
    """The explanation call the original open request of this set was answered with (SQLite named on the LiveSQLBench sets)."""
    base = X.INSTRUCTION if DR.NEW not in X.INSTRUCTION else X.INSTRUCTION.replace(DR.NEW, DR.OLD)
    return base.replace(DR.OLD, DR.NEW) if c["database"] in DR.LIVE else base


def answer():
    C, NW, RVW = _C(), _J("written.json"), _J("review.json"); ks = [k for k in _S() if (RVW.get(k) or {}).get("accepted")]
    def one(job):
        k, m = job; f = "%s/answers/%s/%s.json" % (OUT, m, _name(k))
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); con = DB.connect(c["snapshot"])
        txt = call(_prompt(c) % (schema, docs, NW[k]["open"]), m)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; prim = r.get("sql"); a = DB.rows(con, prim) if prim else None
        alts = [{"interpretation": x.get("interpretation"), "sql": x["sql"], "matches": X._match(c, DB.rows(con, x["sql"]))}
                for x in (r.get("alternatives") or [])[:2] if isinstance(x, dict) and x.get("sql")]
        o = {"case": k, "model": m, "response": r, "primary_executes": a is not None, "primary_matches": X._match(c, a), "alternatives": alts}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex: list(ex.map(one, [(k, m) for k in ks for m in MODELS]))


def judge():
    """The disclosure judge (disclose.JUDGE, Opus, blind to the model) on every new answer: does it name the choice?"""
    W, NW = _W(), _J("written.json"); J = _J("judge.json", {}); A = {}
    for m in MODELS:
        d = "%s/answers/%s" % (OUT, m)
        for f in (os.listdir(d) if os.path.isdir(d) else []):
            o = json.load(open(os.path.join(d, f))); A["%s|%s" % (o["case"], m)] = o
    keys = [k for k in A if k not in J]; anon = {k: hashlib.sha1(k.encode()).hexdigest()[:10] for k in keys}
    def block(key):
        o = A[key]; k = o["case"]; r = o["response"] or {}; w = W[k]
        return "--- %s\nREQUEST: %s\nDECISION: reading A = %s | reading B = %s\nPRIMARY SQL: %s\nASSUMPTIONS: %s\nALTERNATIVES: %s" % (
            anon[key], NW[k]["open"], w["reading_A"], w["reading_B"], (r.get("sql") or "")[:900], json.dumps(r.get("assumptions"))[:900],
            json.dumps([{"interpretation": a.get("interpretation"), "sql": (a.get("sql") or "")[:400]} for a in (r.get("alternatives") or [])[:2]])[:1400])
    random.Random(5).shuffle(keys)
    def one(b):
        got = ask_json(X.JUDGE % "\n\n".join(block(k) for k in b), "opus", brace="[") or []; back = {anon[k]: k for k in b}
        return {back[g["id"]]: g for g in got if isinstance(g, dict) and g.get("id") in back}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for d in ex.map(one, [keys[i:i + 5] for i in range(0, len(keys), 5)]): J.update(d)
    _save("judge.json", J); print("judged", len(J))


def report():
    """Paired, on the sets whose GPT-written open request is accepted and answered by every model: both interpretations returned
    and the choice named, Opus-written original vs GPT-Sol-written, per model; and the model ranking under each writer."""
    C, RVW = _C(), _J("review.json"); J0 = json.load(open(R + "/disclose/judge.json")); J1 = _J("judge.json", {})
    ks = [k for k in _S() if (RVW.get(k) or {}).get("accepted") and all(os.path.exists("%s/answers/%s/%s.json" % (OUT, m, _name(k))) for m in MODELS)]
    got = lambda o: set(o["primary_matches"]) | {x for a in o.get("alternatives", []) for x in a.get("matches", [])}
    res = {"sampled": N, "written": sum(1 for v in _J("written.json").values() if v.get("open")), "accepted": sum(1 for r in RVW.values() if r["accepted"]),
           "labels": dict(collections.Counter(r["label"] for r in RVW.values())), "compared": len(ks), "models": {}}
    for m in MODELS:
        o0 = {k: json.load(open("%s/disclose/%s/%s__open.json" % (R, m, _name(k)))) for k in ks}
        o1 = {k: json.load(open("%s/answers/%s/%s.json" % (OUT, m, _name(k)))) for k in ks}
        b0 = {k: {"A", "B"} <= got(o0[k]) for k in ks}; b1 = {k: {"A", "B"} <= got(o1[k]) for k in ks}
        n0 = {k: (J0.get("%s|open|%s" % (k, m)) or {}).get("flags_decision") is True for k in ks}; n1 = {k: (J1.get("%s|%s" % (k, m)) or {}).get("flags_decision") is True for k in ks}
        res["models"][m] = {"both_opus_written": sum(b0.values()), "both_gpt_written": sum(b1.values()),
                            "both_only_opus": sum(b0[k] and not b1[k] for k in ks), "both_only_gpt": sum(b1[k] and not b0[k] for k in ks),
                            "named_opus_written": sum(n0.values()), "named_gpt_written": sum(n1.values()),
                            "mcnemar_both_p": RN_mcnemar(sum(b0[k] and not b1[k] for k in ks), sum(b1[k] and not b0[k] for k in ks))}
    rank = lambda key: [m for m, _v in sorted(res["models"].items(), key=lambda kv: -kv[1][key])]
    res["ranking_opus_written"] = rank("both_opus_written"); res["ranking_gpt_written"] = rank("both_gpt_written")
    _save("results.json", res)
    L = ["# Same-family check: open requests rewritten by GPT-Sol (`specbridge.comm.transfer.writer_swap_open`)\n",
         "%(sampled)d sets drawn at random (seed %%d) from the accepted sets; %(written)d written; %(accepted)d pass the review; %(compared)d answered by every model.\n" % res % SEED,
         "| model | both returned, Opus-written | both returned, GPT-Sol-written | only Opus / only GPT | McNemar p | named, Opus / GPT |", "|---|---|---|---|---|---|"]
    for m, v in res["models"].items():
        L.append("| %s | %d | %d | %d / %d | %.3g | %d / %d |" % (m, v["both_opus_written"], v["both_gpt_written"], v["both_only_opus"], v["both_only_gpt"], v["mcnemar_both_p"], v["named_opus_written"], v["named_gpt_written"]))
    L.append("\nRanking by both returned: Opus-written %s; GPT-Sol-written %s." % (res["ranking_opus_written"], res["ranking_gpt_written"]))
    open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


def RN_mcnemar(b, c):
    from math import comb
    n = b + c
    return 1.0 if not n else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


if __name__ == "__main__":
    {"sample": sample, "write": write, "review": review, "answer": answer, "judge": judge, "report": report}[sys.argv[1]]()
