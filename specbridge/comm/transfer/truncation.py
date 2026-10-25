"""WHICH STORED INTERPRETATIONS LOST A TRAILING NUMBER? (2026-10-14; the item_line bug, see ambrosia.item_line)
Arms: AMBROSIA final DtP, request-set DtP (Table 7), Sec 7.4 rewrite (b), BIRD rewrite (b). A line is FLAGGED by an end-word list OR a
Haiku check ("does this line end where a number should follow?"); correctness is never used. An item (question / request / reading)
is flagged when a line it used is flagged (DtP uses its first 6 interpretations).
    python -m specbridge.comm.transfer.truncation flag   -> out/truncation/flags.json, FLAGS.md"""
import collections, concurrent.futures as cf, glob, json, os, re, sys
OUT = "out/truncation"
END = re.compile(r"\b(than|above|below|over|under|at least|at most|top|of|to|before|after|from|exceeding|equal to)\s*[.:]?\s*$", re.I)
ASK = """For each numbered line, answer whether the line ENDS where a number or value should follow (it looks cut off right before a
number, e.g. "... salary is exactly", "... greater than", "... published in"). Answer ONLY JSON: [{"i": <number>, "cut": true|false}]

%s"""


def items():
    """arm -> {item id: [lines it used]}."""
    A = collections.defaultdict(dict)
    for f in glob.glob("out/ambrosia/final/dtp/*/*.json"):
        A["AMBROSIA DtP"]["%s|%s" % (f.split("/")[-2], os.path.basename(f)[:-5])] = json.load(open(f))["interpretations"][:6]
    for f in glob.glob("out/reqmethod/dtp/*/*.json"):
        A["Table 7 DtP"]["%s|%s" % (f.split("/")[-2], os.path.basename(f)[:-5])] = json.load(open(f))["interpretations"][:6]
    for f in glob.glob("out/rewrite/runs/*/*.json"):
        o = json.load(open(f)); A["Sec 7.4 (b)"]["%s|%s|%s" % (o["model"], o["case"], o["reading"])] = [o["b"]["request"] or ""]
    for f in glob.glob("out/rewrite/bird/runs/*/*.json"):
        o = json.load(open(f))
        if o["rule"] != "null_filter": A["BIRD (b)"]["%s|%s" % (f.split("/")[-2], o["id"])] = [o["b"]["request"] or ""]
    return A


def flag(batch=40):
    from specbridge.comm.common.llm import ask_json
    A = items(); lines = sorted({l for arm in A.values() for ls in arm.values() for l in ls if l})
    cf_ = OUT + "/model_check.json"; M = json.load(open(cf_)) if os.path.exists(cf_) else {}
    todo = [l for l in lines if l not in M]
    def one(b):
        got = ask_json(ASK % "\n".join("%d. %s" % (i, l) for i, l in enumerate(b)), "haiku", brace="[") or []
        return {b[g["i"]]: bool(g.get("cut")) for g in got if isinstance(g, dict) and isinstance(g.get("i"), int) and 0 <= g["i"] < len(b)}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d in ex.map(one, [todo[i:i + batch] for i in range(0, len(todo), batch)]): M.update(d)
    os.makedirs(OUT, exist_ok=True); json.dump(M, open(cf_, "w"))
    F = {}; L = ["# Stored lines that likely lost a trailing number (`specbridge.comm.transfer.truncation`)\n",
                 "Flag = end-word list OR Haiku check; correctness not used. Item = what one run used (DtP: first 6 interpretations).\n",
                 "| arm | lines | flagged by words | by model | either | items | items flagged |", "|---|---|---|---|---|---|---|"]
    tot_i = tot_f = 0
    for arm, its in A.items():
        ls = [l for v in its.values() for l in v if l]; w = sum(bool(END.search(l)) for l in ls); m = sum(M.get(l, False) for l in ls)
        e = sum(bool(END.search(l)) or M.get(l, False) for l in ls)
        fl = sorted(k for k, v in its.items() if any(l and (END.search(l) or M.get(l, False)) for l in v)); F[arm] = fl
        tot_i += len(its); tot_f += len(fl)
        L.append("| %s | %d | %d | %d | %d | %d | %d (%.1f%%) |" % (arm, len(ls), w, m, e, len(its), len(fl), 100 * len(fl) / max(1, len(its))))
    L.append("\nTotal items flagged: %d of %d (%.1f%%)." % (tot_f, tot_i, 100 * tot_f / max(1, tot_i)))
    json.dump(F, open(OUT + "/flags.json", "w"), indent=1); open(OUT + "/FLAGS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


AUDIT = """Each item gives an ORIGINAL request and a LINE written from it. Does the LINE end cut off, so that a number or value that
should finish it is missing (for example the request says "more than 500" and the line ends "more than")? Answer ONLY JSON:
[{"id": "...", "cut": true|false}]

%s"""


def audit(batch=20):
    """Unflagged items: rewrite arms -> the WRONG ones; DtP arms -> all unflagged items (their correctness is per question set).
    A question-aware Haiku check for truncations the first pass missed."""
    from specbridge.comm.common.llm import ask_json
    from specbridge.comm.transfer import ambrosia as AM, ledger as LG, disclose as X
    F = json.load(open(OUT + "/flags.json")); A = items(); W = json.load(open(X._paths(LG.D)[1])); R = {str(r["row"]): r for r in AM.final_rows()}
    def question(arm, k):
        if arm == "AMBROSIA DtP": return R[k.split("|")[1]]["question"]
        if arm == "Table 7 DtP":
            base = k.split("|")[1]; case, w = base.rsplit("__", 1)
            for c in W:
                if c.replace(":", "__").replace("/", "_") == case: return W[c][w]
        if arm == "Sec 7.4 (b)": return W[k.split("|")[1]]["open"]
        if arm == "BIRD (b)":
            o = json.load(open("out/rewrite/bird/runs/%s/%s.json" % tuple(k.split("|")))); return o["question"] + " Evidence: " + o["evidence"] + " Clarification: " + o["clarification"]
        return ""
    wrong = {}
    for f in glob.glob("out/rewrite/runs/*/*.json"):
        o = json.load(open(f)); wrong["%s|%s|%s" % (o["model"], o["case"], o["reading"])] = o["reading"] not in o["b"]["matches"]
    for f in glob.glob("out/rewrite/bird/runs/*/*.json"):
        o = json.load(open(f)); wrong["%s|%s" % (f.split("/")[-2], o["id"])] = not o["b"]["right"]
    todo = []
    for arm, its in A.items():
        for k, ls in its.items():
            if k in F[arm]: continue
            if arm.endswith("(b)") and not wrong.get(k, False): continue
            for j, l in enumerate(ls):
                if l: todo.append(("%s#%s#%d" % (arm, k, j), question(arm, k), l))
    got = {}
    def one(b):
        r = ask_json(AUDIT % "\n\n".join("--- %s\nORIGINAL: %s\nLINE: %s" % (i, q[:1500], l) for i, q, l in b), "haiku", brace="[") or []
        return {g["id"]: bool(g.get("cut")) for g in r if isinstance(g, dict) and "id" in g}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d in ex.map(one, [todo[i:i + batch] for i in range(0, len(todo), batch)]): got.update(d)
    json.dump(got, open(OUT + "/audit.json", "w"), indent=1)
    L = ["", "## Audit of unflagged items (question-aware Haiku check; rewrite arms: wrong items only; DtP arms: all unflagged items)\n", "| arm | items checked | lines checked | lines found cut | items found |", "|---|---|---|---|---|"]
    for arm in A:
        ids = [i for i, _q, _l in todo if i.startswith(arm + "#")]; cut = [i for i in ids if got.get(i)]
        L.append("| %s | %d | %d | %d | %d |" % (arm, len({i.split("#")[1] for i in ids}), len(ids), len(cut), len({i.split("#")[1] for i in cut})))
    ex = [(i, l) for i, _q, l in todo if got.get(i)][:6]
    L += ["", "Examples found:"] + ["- %s: %s" % (i.split("#")[0], l[-120:]) for i, l in ex]
    open(OUT + "/FLAGS.md", "a").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"flag": flag, "audit": audit}[sys.argv[1]]()
