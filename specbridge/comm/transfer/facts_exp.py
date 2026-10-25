"""DECISION-RELEVANT FACTS: the experiment (2026-10-13). Facts by code (specbridge.comm.transfer.facts), added to the documentation
part of the same one call. Sonnet.
  Spider 2.0 dev (65; errors.split): plain (saved), generic grounding (saved), mapping facts, choice facts, both, agentic (saved);
                                     accuracy and characters in/out; which fact kinds appear in tasks that turn wrong -> right
  30 dev request sets (ledger.sets): the explanation call (saved) vs the same call + mapping / choice / both facts; coverage of both
                                     readings and false alternatives by execution, naming of the planted choice by the Opus judge
    python -m specbridge.comm.transfer.facts_exp run | report"""
import collections, concurrent.futures as cf, hashlib, json, math, os, random, re, sys, time
from specbridge.comm.transfer import facts as FA, errors as ER, spider2 as S, disclose as X, ledger as LG
from specbridge.comm.common import db as DB

OUT = "out/facts_exp"; MODEL = "sonnet"; KINDS = {"mapping": ("mapping",), "choice": ("choice",), "both": ("mapping", "choice")}


def _f(*p): f = "%s/%s.json" % (OUT, "/".join(p)); os.makedirs(os.path.dirname(f), exist_ok=True); return f


def run(workers=6):
    from specbridge.comm.common.llm import call, parse
    T = S.tasks(); E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; dev = ER.split()["dev"]; ctx = {}
    for i in dev: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    fz, wr, _o = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, WD = LG.sets()
    def sp(job):
        arm, iid = job; f = _f("spider2", arm, iid)
        if os.path.exists(f): return
        t = T[iid]; fx = FA.facts("%s/%s.sqlite" % (S.DBDIR, t["db"]), t["question"], KINDS[arm])
        p = X.PLAIN % (ctx[t["db"]], S.docs(t) + ("\n\nFACTS FROM THE DATABASE (computed by code):\n" + fx if fx else ""), t["question"]); txt = call(p, MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; G, io = S.golds(iid, E); df = S.run_sql(t["db"], r.get("sql")) if r.get("sql") else None
        json.dump({"instance_id": iid, "arm": arm, "facts": fx, "sql": r.get("sql"), "matches": S.matches(df, G, io), "chars_in": len(p), "chars_out": len(txt)}, open(f, "w"), indent=1, default=str)
    def rs(job):
        arm, k, w = job; f = _f("sets", arm, ("%s__%s" % (k, w)).replace(":", "__").replace("/", "_"))
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); fx = FA.facts(c["snapshot"], W[k][w], KINDS[arm])
        p = X.INSTRUCTION % (schema, docs + ("\n\nFACTS FROM THE DATABASE (computed by code):\n" + fx if fx else ""), W[k][w]); txt = call(p, MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; con = DB.connect(c["snapshot"]); prim = r.get("sql"); a = DB.rows(con, prim) if prim else None; alts = []
        for x in (r.get("alternatives") or [])[:2]:
            if isinstance(x, dict) and x.get("sql"): alts.append({"interpretation": x.get("interpretation"), "matches": X._match(c, DB.rows(con, x["sql"]))})
        json.dump({"case": k, "wording": w, "arm": arm, "facts": fx, "response": r, "primary_matches": X._match(c, a), "alternatives": alts, "chars_in": len(p), "chars_out": len(txt)}, open(f, "w"), indent=1, default=str)
    jobs = [("sp", a, i) for a in KINDS for i in dev] + [("rs", a, k, w) for a in KINDS for k in ks for w in WD[k]]
    random.Random(7).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(lambda j: sp(j[1:]) if j[0] == "sp" else rs(j[1:]), jobs))
    judge(); report()


def judge(batch=6):
    """Naming of the planted choice on OPEN wordings, Opus judge blind to the arm and model (disclose.JUDGE), for the saved
    explanation-call answers and the three fact arms."""
    from specbridge.comm.common.llm import ask_json
    fz, wr, out = X._paths(LG.D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, _WD = LG.sets()
    jf = OUT + "/judge.json"; J = json.load(open(jf)) if os.path.exists(jf) else {}
    items = []
    for k in ks:
        base = "%s/%s/%s__open.json" % (out, MODEL, k.replace(":", "__").replace("/", "_"))
        srcs = {"explanation": base, **{a: _f("sets", a, ("%s__open" % k).replace(":", "__").replace("/", "_")) for a in KINDS}}
        for a, f in srcs.items():
            key = "%s|%s" % (k, a)
            if key in J or not os.path.exists(f): continue
            items.append((key, k, json.load(open(f)).get("response") or {}))
    rng = random.Random(3); rng.shuffle(items); anon = {i[0]: hashlib.sha1(i[0].encode()).hexdigest()[:10] for i in items}
    def one(b):
        body = "\n\n".join("--- %s\nREQUEST: %s\nDECISION: %s (reading A vs reading B)\nPRIMARY SQL: %s\nASSUMPTIONS: %s\nALTERNATIVES: %s" % (
            anon[key], W[k]["open"], C[k]["kind"], (r.get("sql") or "")[:1200], json.dumps(r.get("assumptions"))[:800],
            json.dumps([x.get("interpretation") for x in (r.get("alternatives") or []) if isinstance(x, dict)])[:600]) for key, k, r in b)
        got = ask_json(X.JUDGE % body, "opus", brace="[") or []; back = {anon[key]: key for key, _k, _r in b}
        return {back[g["id"]]: g for g in got if isinstance(g, dict) and g.get("id") in back}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for d in ex.map(one, [items[i:i + batch] for i in range(0, len(items), batch)]): J.update(d)
    json.dump(J, open(jf, "w"), indent=1)


def _kinds(fx):
    """The fact kinds present in a facts block (for the wrong -> right analysis)."""
    K = []
    for pat, name in ((r"SEVERAL COLUMNS", "term in several columns"), (r"STORED FORM", "stored form of a term"), (r"repeats each", "join fan-out"),
                      (r"no matching|no .* match", "unmatched rows"), (r"is NULL in", "NULL share"), (r"tie at the", "ties at an extreme"),
                      (r"minority", "flag / status minority"), (r"cumulative", "cumulative field"), (r"runs from", "date coverage / gaps")):
        if re.search(pat, fx or ""): K.append(name)
    return K


def report():
    T = S.tasks(); dev = ER.split()["dev"]; ld = lambda *p: json.load(open(p[0])) if os.path.exists(p[0]) else None
    A = {"plain": lambda i: ld("%s/plain/%s.json" % (ER.OUT, i)), "generic grounding": lambda i: ld("%s/grounded/%s.json" % (ER.OUT, i)),
         "agentic": lambda i: ld("%s/agent/%s.json" % (ER.OUT, i)), **{a: (lambda a: lambda i: ld(_f("spider2", a, i)))(a) for a in KINDS}}
    rows = [i for i in dev if all(A[a](i) for a in A)]
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    L = ["# Decision-relevant facts by code (`specbridge.comm.transfer.facts_exp`), Sonnet\n", "## Spider 2.0 dev (%d tasks with every arm)\n" % len(rows),
         "| arm | right | vs plain | chars in / out per task |", "|---|---|---|---|"]
    for a, g in A.items():
        r_ = sum(bool(g(i)["matches"]) for i in rows); up = sum(bool(g(i)["matches"]) and not A["plain"](i)["matches"] for i in rows); dn = sum(bool(A["plain"](i)["matches"]) and not g(i)["matches"] for i in rows)
        ci = [g(i).get("chars_in") for i in rows if g(i).get("chars_in")]; co = [g(i).get("chars_out") for i in rows if g(i).get("chars_out")]
        L.append("| %s | %d | +%d / -%d (p %.2g) | %s |" % (a, r_, up, dn, mc(up, dn), "%d / %d" % (sum(ci) / len(ci), sum(co) / max(1, len(co))) if ci else ("about 10,000 / 1,150 (measured)" if a == "agentic" else "-")))
    kw = collections.Counter(); kr = collections.Counter(); nwr = 0
    for i in rows:
        b = A["both"](i)
        if b["matches"] and not A["plain"](i)["matches"]: nwr += 1; kw.update(_kinds(b["facts"]))
        kr.update(_kinds(b["facts"]))
    L += ["", "Fact kinds in the 'both' block: in tasks that turn wrong -> right (%d) vs in all %d tasks:" % (nwr, len(rows))] + ["- %s: %d / %d" % (k, kw[k], kr[k]) for k in sorted(kr, key=lambda k: -kr[k])]
    fz, wr, out = X._paths(LG.D); ks, WD = LG.sets(); J = json.load(open(OUT + "/judge.json")) if os.path.exists(OUT + "/judge.json") else {}
    base = lambda k, w: ld("%s/%s/%s__%s.json" % (out, MODEL, k.replace(":", "__").replace("/", "_"), w))
    src = {"explanation (saved)": base, **{a: (lambda a: lambda k, w: ld(_f("sets", a, ("%s__%s" % (k, w)).replace(":", "__").replace("/", "_"))))(a) for a in KINDS}}
    jk = {"explanation (saved)": "explanation", **{a: a for a in KINDS}}
    sets = [k for k in ks if all(src[a](k, w) for a in src for w in WD[k])]
    L += ["", "## %d dev request sets\n" % len(sets), "| arm | open: both readings | open: names the choice (Opus judge) | specific: main right | specific: false alternative |", "|---|---|---|---|---|"]
    for a, g in src.items():
        cov = sum({"A", "B"} <= set(g(k, "open")["primary_matches"]) | {x for al in g(k, "open")["alternatives"] for x in al["matches"]} for k in sets)
        nm = sum(bool((J.get("%s|%s" % (k, jk[a])) or {}).get("flags_decision")) for k in sets)
        P = [(k, w) for k in sets for w in WD[k] if w != "open"]
        right = sum(w[-1] in g(k, w)["primary_matches"] for k, w in P); fa = sum(any(("B" if w.endswith("A") else "A") in al["matches"] for al in g(k, w)["alternatives"]) for k, w in P)
        L.append("| %s | %d / %d | %d / %d | %d / %d | %d |" % (a, cov, len(sets), nm, len(sets), right, len(P), fa))
    os.makedirs(OUT, exist_ok=True); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "report": report, "judge": judge}[sys.argv[1]]()
