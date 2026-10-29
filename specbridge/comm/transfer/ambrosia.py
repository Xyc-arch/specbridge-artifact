"""AMBROSIA (Saparina & Lapata, NeurIPS 2024). Human-written ambiguous questions (scope, attachment, vagueness) on real-looking
databases, each with the SQL of EVERY interpretation, plus unambiguous versions with one SQL. Someone else's benchmark: nothing
here is fitted to it. Prompt: AMBROSIA's own zero-shot prompt (src/prompts/evaluation/prompt) with the database dump.
Parsing and scoring follow AMBROSIA's code (src/evaluation/output_parsers.parse_statements_mixtral, metrics.evaluate_predicted_statements):
an interpretation is found when some predicted query returns the same results (row order checked only when the gold query sorts).
    ambiguous    recall (share of interpretations found), AllFound (every one found), precision (share of predicted queries that match)
    unambiguous  found (the one interpretation) and precision (extra queries lower it)
What the paper uses:
    decomp_run [<model> ...] [conf] / decomp_report   missed interpretations the model computes when asked for each alone (Fig. 7)
    run_final / report_final    Section 7 test on 150 new test questions per model (Sonnet, GPT-Sol): arms plain (the authors'
                                prompt), samplek (it, 3 samples), dtp (disambiguate-then-parse, released prompts) and ours
                                (decide-then-answer) -> out/ambrosia/final/<arm>/<model>/<row>.json; system.py builds the other arms
    run_method / run_variant / report_method   the 60-question development runs of the method (out/ambrosia/method/)
Earlier, not in the paper: run / report compare a checklist in the prompt (raise) with a same-length placebo (placebo) and plain
-> out/ambrosia/<arm>/<model>/<row>.json, RESULTS.md.
The data stays in ambrosia_data/ (git-ignored; the authors ask that it not be uploaded). At most 6 workers."""
import collections, concurrent.futures as cf, json, math, os, random, re, sqlite3, sys, time
from specbridge.comm.transfer import checklist as K

_MARK = __import__("re").compile(r"^\s*(?:[-*\u2022]|\(?\d+[.):])\s*")
def item_line(x):
    """One line of a model's list with only a leading list marker removed ("1.", "2)", "-", "*"). The former
    x.strip(" -*0123456789.") also removed digits and periods at the END of the line, cutting numbers off interpretations
    such as "... salary is exactly 50000" (bug found 2026-10-14)."""
    return _MARK.sub("", x).strip()


DATA = "ambrosia_data"; OUT = "out/ambrosia"; MODELS = K.MODELS; ARMS = ["plain", "placebo", "raise"]
SEED, B, N_AMBIG, N_UNAMBIG = 20261016, 4000, 20, 10          # per ambiguity type: 60 ambiguous + 30 unambiguous questions
PROMPT = open(DATA + "/code/prompt.txt").read() if os.path.exists(DATA + "/code/prompt.txt") else ""


def conf_rows(n=20):
    """CONFIRMATION SAMPLE (2026-10-12): 20 ambiguous test-split questions per type, seeded with a new seed, excluding every dev
    question and every parent of a dev unambiguous question -- used for nothing else."""
    import pandas as pd
    d = pd.read_csv(DATA + "/data/ambrosia.csv"); d = d[d.split == "test"]; dev = rows()
    used_q = {(r["db_file"].replace(DATA + "/", "", 1), r["question"]) for r in dev if r["ambiguous"]}
    used_q |= {(d.loc[d["Unnamed: 0"] == r["row"], "db_file"].iloc[0], d.loc[d["Unnamed: 0"] == r["row"], "ambig_question"].iloc[0]) for r in dev if not r["ambiguous"]}
    out = []
    for typ in ("scope", "attachment", "vague"):
        x = d[(d.ambig_type == typ) & (d.question_type == "ambig")]; idx = [i for i in sorted(x.index) if (x.loc[i, "db_file"], x.loc[i, "question"]) not in used_q]
        random.Random("%d-conf-%s" % (SEED, typ)).shuffle(idx)
        for i in idx[:n]:
            r = d.loc[i]; out.append({"row": int(r["Unnamed: 0"]), "type": typ, "ambiguous": True, "question": r["question"],
                                      "gold": [q.strip() for q in r["gold_queries"].split("\n\n") if q.strip()], "db_file": DATA + "/" + r["db_file"], "dump": r["db_dump"]})
    return out


def rows():
    import pandas as pd
    d = pd.read_csv(DATA + "/data/ambrosia.csv"); d = d[d.split == "test"]; out = []
    for typ in ("scope", "attachment", "vague"):
        for qt, n in (("ambig", N_AMBIG), ("unambig", N_UNAMBIG)):
            x = d[(d.ambig_type == typ) & (d.question_type == qt)]
            idx = sorted(x.index); random.Random("%d-%s-%s" % (SEED, typ, qt)).shuffle(idx)
            for i in idx[:n]:
                r = d.loc[i]; out.append({"row": int(r["Unnamed: 0"]), "type": typ, "ambiguous": qt == "ambig", "question": r["question"],
                                          "gold": [q.strip() for q in r["gold_queries"].split("\n\n") if q.strip()], "db_file": DATA + "/" + r["db_file"].replace("data/", "data/", 1), "dump": r["db_dump"]})
    return out


OLD = "and keep the query as short as it can be\nwhile it still answers the request in full."
PLACEBO = K.PLACEBO.replace(OLD, "and use the same names, quoting and spacing\nthroughout the whole query from start to end.")   # "short" was found active
assert PLACEBO != K.PLACEBO


def prompt(arm, r):
    head, tail = PROMPT.split("\n\nGiven the following SQLite database schema:", 1)
    block = {"plain": "", "placebo": "\n\n" + PLACEBO, "raise": "\n\n" + K.CHECK}[arm]
    return (head + block + "\n\nGiven the following SQLite database schema:" + tail).replace("SQL_DATABASE_DUMP", r["dump"]).replace("QUESTION", r["question"])


# --- AMBROSIA's parser and scorer (verbatim logic from src/evaluation) ---------------------------------------------------------
def parse(text):
    if "```" in text:
        statements = [code for _, code in re.findall(r"```(\w+)\s+(.*?)```", text, re.DOTALL)]
    elif "\n\n" in text or ";" in text:
        statements = [x.strip() for x in re.split(r';|\n\n', text) if x.strip() and (x.strip().lower().startswith("select") or x.strip().lower().startswith("with"))]
    elif text.strip().lower().startswith("select"):
        statements = [text.strip()]
    else: statements = []
    return [s.replace("\\", "") for s in statements]


def _key(x): return (0, "") if x is None else (1, float(x)) if isinstance(x, (int, float)) else (2, str(x))


def same(pred, gold, order_by=False):
    if not pred: return False
    if order_by:
        if len(gold) != len(pred) or any(len(r) != len(gold[0]) for r in gold + pred): return False
        return all(tuple(sorted(g, key=_key)) == tuple(sorted(p, key=_key)) for g, p in zip(gold, pred))
    return collections.Counter(i for r in gold for i in r) == collections.Counter(i for r in pred for i in r)


def score(db, preds, gold):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); G = {}
    for q in gold: G[q] = con.execute(q).fetchall()
    preds = list(set(preds)); P = {}
    for q in preds:
        try: P[q] = con.execute(q).fetchall()
        except sqlite3.DatabaseError: P[q] = None
    con.close(); found = {q: False for q in gold}; good = {q: False for q in preds}
    for pq, pr in P.items():
        if pr is None: continue
        for gq, gr in G.items():
            if same(pr, gr, "order by" in gq.lower()): found[gq] = good[pq] = True
    return {"recall": sum(found.values()) / len(gold), "all_found": all(found.values()), "precision": sum(good.values()) / len(preds) if preds else 0.0, "n_pred": len(preds)}


# --- run and report ----------------------------------------------------------------------------------------------------------
def _f(arm, m, r): return "%s/%s/%s/%d.json" % (OUT, arm, m, r["row"])


def run(models, workers=6):
    from specbridge.comm.common.llm import call
    R = rows(); ids = list(range(len(R))); random.Random(SEED).shuffle(ids)
    jobs = [(R[i], m, a) for i in ids for m in models for a in ARMS]; per = len(models) * len(ARMS)
    def one(job):
        r, m, a = job; f = _f(a, m, r)
        if os.path.exists(f): return
        t0 = time.time(); txt = call(prompt(a, r), m)
        if not (txt or "").strip(): return                      # a failed call is not an answer: asked again on rerun
        preds = parse(txt); s = score(r["db_file"], preds, r["gold"])
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"row": r["row"], "type": r["type"], "ambiguous": r["ambiguous"], "model": m, "arm": a, "raw": txt, "preds": preds, **s, "seconds": round(time.time() - t0, 1)}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for n, _ in enumerate(ex.map(one, jobs), 1):
            if n % (10 * per) == 0: report(quiet=True); print("questions %d/%d, report updated" % (n // per, len(R)), flush=True)
    report(quiet=True); open(OUT + "/run.done", "w").write("ok\n")


def report(quiet=False):
    R = rows(); mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, i) for i in range(min(b, c) + 1)) / 2 ** (b + c))
    res = {"n": len(R), "models": {}}; pool = collections.defaultdict(list)
    L = ["# Raise vs placebo on AMBROSIA (`specbridge.comm.transfer.ambrosia`)\n",
         "Test split, seeded: %d ambiguous and %d unambiguous questions per type (scope, attachment, vague). AMBROSIA's prompt, parser and "
         "scorer. Questions with all three arms saved. AllFound and found: count (raise vs placebo gained/lost, exact McNemar p).\n" % (N_AMBIG, N_UNAMBIG),
         "| solver | ambiguous n | AllFound: plain | placebo | raise | recall: plain / placebo / raise | precision: plain / placebo / raise | unambiguous n | found: plain / placebo / raise | precision: plain / placebo / raise |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        got = []
        for r in R:
            fs = {a: _f(a, m, r) for a in ARMS}
            if all(os.path.exists(f) for f in fs.values()): got.append((r, {a: json.load(open(f)) for a, f in fs.items()}))
        if not got: continue
        A = [(r, o) for r, o in got if r["ambiguous"]]; U = [(r, o) for r, o in got if not r["ambiguous"]]
        mean = lambda xs, k, a: sum(o[a][k] for _r, o in xs) / max(1, len(xs))
        cnt = lambda xs, k, a: sum(bool(o[a][k]) for _r, o in xs)
        b1 = sum(o["raise"]["all_found"] and not o["placebo"]["all_found"] for _r, o in A); c1 = sum(o["placebo"]["all_found"] and not o["raise"]["all_found"] for _r, o in A)
        x = {"n_ambig": len(A), "n_unambig": len(U), "rows": [{"row": r["row"], "type": r["type"], "ambiguous": r["ambiguous"], **{a: {k: o[a][k] for k in ("recall", "all_found", "precision", "n_pred")} for a in ARMS}} for r, o in got],
             "all_found": {a: cnt(A, "all_found", a) for a in ARMS}, "recall": {a: mean(A, "recall", a) for a in ARMS}, "precision_ambig": {a: mean(A, "precision", a) for a in ARMS},
             "found_unambig": {a: cnt(U, "all_found", a) for a in ARMS}, "precision_unambig": {a: mean(U, "precision", a) for a in ARMS}, "raise_vs_placebo_allfound": {"up": b1, "down": c1, "p": mc(b1, c1)},
             "by_type": {t: {a: sum(o[a]["all_found"] for r, o in A if r["type"] == t) for a in ARMS} | {"n": sum(r["type"] == t for r, _o in A)} for t in ("scope", "attachment", "vague")}}
        pool["all_found"] += [int(o["raise"]["all_found"]) - int(o["placebo"]["all_found"]) for _r, o in A]
        pool["recall"] += [o["raise"]["recall"] - o["placebo"]["recall"] for _r, o in A]
        pool["unambig_precision"] += [o["raise"]["precision"] - o["placebo"]["precision"] for _r, o in U]
        res["models"][m] = x; f3 = lambda d, fmt="%.2f": " / ".join(fmt % d[a] for a in ARMS)
        L.append("| %s | %d | %d | %d | %d (+%d/-%d, p %.2g) | %s | %s | %d | %s | %s |" % (m, len(A), x["all_found"]["plain"], x["all_found"]["placebo"], x["all_found"]["raise"], b1, c1, mc(b1, c1),
                 f3(x["recall"]), f3(x["precision_ambig"]), len(U), f3(x["found_unambig"], "%d"), f3(x["precision_unambig"])))
    rng = random.Random(SEED); res["pooled"] = {}
    for k, ds in pool.items():
        if not ds: continue
        obs = sum(ds) / len(ds); null = [sum(d * rng.choice((-1, 1)) for d in ds) / len(ds) for _ in range(B)]
        res["pooled"][k] = {"pairs": len(ds), "mean_diff": obs, "p": (1 + sum(abs(v) >= abs(obs) for v in null)) / (B + 1)}
    L += [""] + ["Pooled raise - placebo, %s: %d pairs, %+.3f, sign-flip p = %.4f." % (k, v["pairs"], v["mean_diff"], v["p"]) for k, v in res["pooled"].items()]
    L += ["", "AllFound by ambiguity type (plain / placebo / raise of n):"] + ["- %s: %s" % (m, "; ".join("%s %d/%d/%d of %d" % (t, *(v[a] for a in ARMS), v["n"]) for t, v in x["by_type"].items())) for m, x in res["models"].items()]
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(OUT + "/results.json", "w"), indent=1); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n")
    if not quiet: print("\n".join(L))



# --- DECOMPOSITION ON AMBROSIA'S OWN ITEMS (2026-10-12): does a solver COMPUTE the readings it does not REPORT? -------------------
# AMBROSIA pairs every ambiguous question with one unambiguous question per reading (column ambig_question). Those are the specific
# requests; the ambiguous question is the open one. Same single call and prompt (the authors' plain prompt) for both. For each
# ambiguous question and reading: covered by the open answer? answered right when asked its unambiguous question? Graded
# shape-tolerant (specbridge.comm.common.grade.shape_tolerant: extra columns, any column order, rows as a set) and strict (AMBROSIA's).
#   python -m specbridge.comm.transfer.ambrosia decomp_run [<model> ...]  -> out/ambrosia/specific/<model>/<row>.json
#   python -m specbridge.comm.transfer.ambrosia decomp_report             -> out/ambrosia/DECOMPOSITION.md, decomposition.json
def sample(name): return [r for r in rows() if r["ambiguous"]] if name == "dev" else conf_rows()


def specifics(name="dev"):
    """Ambiguous question row -> [(unambiguous row, its question, its gold SQL)], one per reading."""
    import pandas as pd
    d = pd.read_csv(DATA + "/data/ambrosia.csv"); u = d[d.question_type == "unambig"]; out = {}
    for r in sample(name):
        kids = u[(u.db_file == r["db_file"].replace(DATA + "/", "", 1)) & (u.ambig_question == r["question"])]
        out[r["row"]] = [(int(k["Unnamed: 0"]), k["question"], k["gold_queries"].strip()) for _i, k in kids.iterrows()]
    return out


def _ex(db, q):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try: return [list(x) for x in con.execute(q).fetchall()]
    except Exception: return None
    finally: con.close()


def decomp_run(models, name="dev", workers=6):
    from specbridge.comm.common.llm import call
    R = {r["row"]: r for r in sample(name)}; SP = specifics(name)
    jobs = [("open", m, R[a], None) for a in SP for m in models] + [("specific", m, R[a], k) for a, ks in SP.items() for k in ks for m in models]
    random.Random(SEED + 9).shuffle(jobs)
    def one(job):
        kind, m, r, k = job
        f = _f("plain", m, r) if kind == "open" else "%s/specific/%s/%d.json" % (OUT, m, k[0])
        if os.path.exists(f): return
        q = r["question"] if kind == "open" else k[1]; txt = call(prompt("plain", dict(r, question=q)), m)
        if not (txt or "").strip(): return
        preds = parse(txt); gold = r["gold"] if kind == "open" else [k[2]]; s = score(r["db_file"], preds, gold)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"row": r["row"] if kind == "open" else k[0], "parent": r["row"], "kind": kind, "model": m, "arm": "plain", "raw": txt, "preds": preds, **s}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    decomp_report(name)


def wilson(k, n, z=1.96):
    if not n: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def decomp_report(name="dev"):
    from specbridge.comm.common import grade as G
    R = {r["row"]: r for r in sample(name)}; SP = specifics(name); res = {"sample": name, "models": {}}
    L = ["# Decomposition on AMBROSIA's own items, %s sample (`specbridge.comm.transfer.ambrosia decomp_report`)\n" % name,
         "%d ambiguous dev questions (test split, seeded) with %d unambiguous versions (one per reading). Same single call and prompt "
         "for open and specific questions. A reading is matched to the open question's gold reading by executing both golds. Grades: shape-tolerant (primary) / strict.\n"
         % (len(SP), sum(len(v) for v in SP.values())),
         "| solver | AMBROSIA recall | AllFound | every specific right | AllFound where every specific right [Wilson 95%%] | readings missed in the open answer | **missed but computed when asked** [Wilson 95%%] |",
         "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        Q = []
        for a, ks in SP.items():
            r = R[a]; fo = _f("plain", m, r); fs = ["%s/specific/%s/%d.json" % (OUT, m, k[0]) for k in ks]
            if not (os.path.exists(fo) and all(os.path.exists(f) for f in fs)): continue
            o = json.load(open(fo)); db = r["db_file"]; P = [x for x in (_ex(db, p) for p in set(o["preds"])) if x is not None]
            per = []
            for k, f in zip(ks, fs):
                g = _ex(db, k[2]); s = json.load(open(f)); SPd = [x for x in (_ex(db, p) for p in set(s["preds"])) if x is not None]
                open_shape = any(G.shape_tolerant(g, p) for p in P); open_strict = any(same(p, g, "order by" in k[2].lower()) for p in P)
                # the specific answer must give THIS reading as its (first) query: a single final SQL
                first = _ex(db, s["preds"][0]) if s["preds"] else None
                spec_shape = first is not None and G.shape_tolerant(g, first); spec_strict = first is not None and same(first, g, "order by" in k[2].lower())
                per.append({"open_shape": open_shape, "open_strict": open_strict, "spec_shape": spec_shape, "spec_strict": spec_strict})
            Q.append({"row": a, "type": r["type"], "readings": per})
        if not Q: continue
        x = {}
        for g in ("shape", "strict"):
            rec = sum(sum(p["open_" + g] for p in q["readings"]) / len(q["readings"]) for q in Q) / len(Q)
            allf = sum(all(p["open_" + g] for p in q["readings"]) for q in Q); allspec = [q for q in Q if all(p["spec_" + g] for p in q["readings"])]
            miss = [p for q in Q for p in q["readings"] if not p["open_" + g]]; comp = sum(p["spec_" + g] for p in miss)
            x[g] = {"n": len(Q), "recall": rec, "all_found": allf, "every_specific_right": len(allspec),
                    "all_found_given_specific": sum(all(p["open_" + g] for p in q["readings"]) for q in allspec), "missed": len(miss), "missed_computed": comp}
        for g in ("shape", "strict"):
            x[g]["ci_all_found_given_specific"] = wilson(x[g]["all_found_given_specific"], x[g]["every_specific_right"]); x[g]["ci_missed_computed"] = wilson(x[g]["missed_computed"], x[g]["missed"])
        res["models"][m] = {**x, "questions": Q}; s_, t_ = x["shape"], x["strict"]; ci = lambda c: "[%.0f, %.0f]" % (100 * c[0], 100 * c[1])
        L.append("| %s | %.2f / %.2f | %d / %d of %d | %d / %d | %d of %d (%.0f%%) %s / %d of %d | %d / %d | **%d of %d (%.0f%%)** %s / %d of %d (%.0f%%) |" % (
            m, s_["recall"], t_["recall"], s_["all_found"], t_["all_found"], s_["n"], s_["every_specific_right"], t_["every_specific_right"],
            s_["all_found_given_specific"], s_["every_specific_right"], 100 * s_["all_found_given_specific"] / max(1, s_["every_specific_right"]), ci(s_["ci_all_found_given_specific"]),
            t_["all_found_given_specific"], t_["every_specific_right"], s_["missed"], t_["missed"],
            s_["missed_computed"], s_["missed"], 100 * s_["missed_computed"] / max(1, s_["missed"]), ci(s_["ci_missed_computed"]), t_["missed_computed"], t_["missed"], 100 * t_["missed_computed"] / max(1, t_["missed"])))
    L.append("\nAMBROSIA's recall and AllFound count only the readings that appear in the open answer; they cannot tell a reading the "
             "model could not compute from one it computed but did not report. The last column makes that split.")
    sfx = "" if name == "dev" else "_" + name
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(OUT + "/decomposition%s.json" % sfx, "w"), indent=1); open(OUT + "/DECOMPOSITION%s.md" % sfx, "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- METHOD PILOT ON AMBROSIA DEV (2026-10-13) ---------------------------------------------------------------------------------
# Data: the 60 ambiguous dev questions (decomposition saved) + the 30 unambiguous dev questions (false alarms). One model.
# Arms (same model, same database dump as context):
#   plain    the authors' prompt (saved answers)
#   dtp      disambiguate-then-parse (Saparina & Lapata 2025, released prompts src/prompts.py): interpretations
#            (user_message_interpr_ambig) -> missing ones (user_message_interpr_ambig_missing; their paper uses a fine-tuned
#            adapter for this step, which cannot run with this model) -> one SQL per interpretation (user_message_sql)
#   samplek  the authors' prompt sampled k times, k = our method's mean calls per question (equal calls)
#   ours     detect: one call says whether the question has more than one reading on this database and, if so, rewrites it once
#            per reading as a fully specified question -> one call per reading with the authors' unambiguous prompt (only when
#            more than one reading) -> readings with identical results dropped by execution -> main answer + alternatives;
#            ours+lib additionally adds library-rule edits of each kept query when they run and change the answer (code only)
GATE = ("GATE (written before the run): continue to the full test only if OURS beats disambiguate-then-parse on AllFound or recall, "
        "recovers >= 30-40%% of the computable misses (decomposition: readings plain missed that the model computes when asked), and "
        "loses <= 3 points of precision on unambiguous questions against plain.")
DTP_INTERP = open(DATA + "/dtp/prompts.py").read() if os.path.exists(DATA + "/dtp/prompts.py") else ""
DETECT = """You are given a database and a question about it. Decide whether the question has more than one reasonable reading on THIS
database -- readings that a careful analyst could each intend and that would give different answers. If it has one reading, return
it unchanged. If it has several, rewrite the question once per reading, each rewrite fully specified so that it has exactly one
reading. Do not invent readings the question rules out.

Database:
%s

Question:
%s

Answer ONLY JSON: {"readings": ["<question rewritten for reading 1>", ...]}"""
SQL_ONE = None   # set from the released prompts


def _dtp_prompts():
    g = {}; exec(DTP_INTERP, g); return g


def _ex_sql(db, q):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try: return con.execute(q).fetchall()
    except Exception: return None
    finally: con.close()


def method_rows():
    R = rows(); return [r for r in R if r["ambiguous"]] + [r for r in R if not r["ambiguous"]]


def _mf(arm, m, r):
    f = "%s/method/%s/%s/%d.json" % (OUT, arm, m, r["row"]); os.makedirs(os.path.dirname(f), exist_ok=True); return f


def run_method(model="sonnet", workers=6):
    from specbridge.comm.common.llm import call, parse as jparse
    os.makedirs(OUT + "/method", exist_ok=True)
    if not os.path.exists(OUT + "/method/RESULTS.md"): open(OUT + "/method/RESULTS.md", "w").write("# AMBROSIA method pilot\n\n" + GATE.replace("%%", "%") + "\n")
    P = _dtp_prompts(); R = method_rows()
    def ask(p, sink):
        t = call(p, model) or ""; sink["calls"] += 1; sink["chars_in"] += len(p); sink["chars_out"] += len(t); return t
    def ours(r):
        f = _mf("ours", model, r)
        if os.path.exists(f): return
        c = collections.Counter(); t = ask(DETECT % (r["dump"], r["question"]), c)
        if not t.strip(): return
        reads = [x for x in ((jparse(t, "{") or {}).get("readings") or []) if isinstance(x, str) and x.strip()] or [r["question"]]
        qs = []
        if len(reads) == 1:                                   # one reading: one SQL for it (the second and last call)
            s = parse_one(ask(P["user_message_sql"].format(r["dump"], reads[0]), c)); qs += s[:1]
        else:
            for rd in reads[:4]: qs += parse_one(ask(P["user_message_sql"].format(r["dump"], rd), c))[:1]
        json.dump({"row": r["row"], "readings": reads, "queries": qs, "cost": dict(c)}, open(f, "w"), indent=1)
    def dtp(r):
        f = _mf("dtp", model, r)
        if os.path.exists(f): return
        c = collections.Counter(); t = ask(P["user_message_interpr_ambig"].format(r["dump"], r["question"]), c)
        if not t.strip(): return
        ints = [item_line(x) for x in t.splitlines() if item_line(x)]
        miss = ask(P["user_message_interpr_ambig_missing"].format(r["dump"], r["question"], "\n".join(ints)), c)
        if "all possible interpretations are covered" not in miss.lower():
            ints += [item_line(x) for x in miss.splitlines() if item_line(x)]
        qs = []
        for it in ints[:6]: qs += parse_one(ask(P["user_message_sql"].format(r["dump"], it), c))[:1]
        json.dump({"row": r["row"], "interpretations": ints, "queries": qs, "cost": dict(c)}, open(f, "w"), indent=1)
    for fn in (ours, dtp):
        with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(fn, R))
    O = [json.load(open(_mf("ours", model, r))) for r in R if os.path.exists(_mf("ours", model, r))]
    k = max(1, round(sum(o["cost"]["calls"] for o in O) / max(1, len(O))))
    def samplek(r):
        f = _mf("samplek", model, r)
        if os.path.exists(f): return
        c = collections.Counter(); qs = []
        for _ in range(k):
            t = ask(prompt("plain", r), c)
            if t.strip(): qs += parse(t)
        json.dump({"row": r["row"], "k": k, "queries": qs, "cost": dict(c)}, open(f, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(samplek, R))
    report_method(model)


DETECT2 = """You are given a database and a question about it. A first reading found ONE interpretation:
%s
Look again, word by word: could a word or phrase reasonably refer to different things in this database, or could a condition or a
quantifier apply to a different part of the question, so that a careful analyst could intend another reading with a different
answer? If so, list EVERY reading -- the first one included -- each rewritten as a fully specified question. If not, return only the
first one. Do not invent readings the question rules out.

Database:
%s

Question:
%s

Answer ONLY JSON: {"readings": ["...", ...]}"""


def run_variant(model="sonnet", workers=6):
    """(1) plain on dev questions it lacks (same questions for precision); (2) RECALL VARIANT ours2: a second detection pass only
    where ours found a single reading; new readings get one SQL call each; everything else is ours unchanged."""
    from specbridge.comm.common.llm import call, parse as jparse
    P = _dtp_prompts(); R = method_rows()
    def plain(r):
        f = _f("plain", model, r)
        if os.path.exists(f): return
        txt = call(prompt("plain", r), model)
        if not (txt or "").strip(): return
        preds = parse(txt); s_ = score(r["db_file"], preds, r["gold"]); os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"row": r["row"], "type": r["type"], "ambiguous": r["ambiguous"], "model": model, "arm": "plain", "raw": txt, "preds": preds, **s_}, open(f, "w"), indent=1)
    def ours2(r):
        f2 = _mf("ours2", model, r); f1 = _mf("ours", model, r)
        if os.path.exists(f2) or not os.path.exists(f1): return
        o = json.load(open(f1)); c = collections.Counter(o["cost"])
        if len(o["readings"]) == 1:
            p = DETECT2 % (o["readings"][0], r["dump"], r["question"]); t = call(p, model) or ""; c["calls"] += 1; c["chars_in"] += len(p); c["chars_out"] += len(t)
            reads = [x for x in ((jparse(t, "{") or {}).get("readings") or []) if isinstance(x, str) and x.strip()]
            new = [x for x in reads if x.strip() != o["readings"][0].strip()]
            qs = list(o["queries"])
            for rd in new[:3]:
                p = P["user_message_sql"].format(r["dump"], rd); t = call(p, model) or ""; c["calls"] += 1; c["chars_in"] += len(p); c["chars_out"] += len(t)
                qs += parse_one(t)[:1]
            o = {"row": r["row"], "readings": o["readings"] + new, "queries": qs, "second_pass": True}
        json.dump(dict(o, cost=dict(c)), open(f2, "w"), indent=1)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(plain, R)); list(ex.map(ours2, R))


def parse_one(text): return parse(text) or ([text.strip()] if text.strip().lower().startswith(("select", "with")) else [])


def _dedup(db, qs):
    """Queries whose results are identical are one reading (AMBROSIA's own comparison); failing queries are dropped."""
    keep, res = [], []
    for q in qs:
        r = _ex_sql(db, q)
        if r is None: continue
        if any(same(r, x, "order by" in q.lower()) and same(x, r, "order by" in q.lower()) for x in res): continue
        keep.append(q); res.append(r)
    return keep


def _with_library(db, qs):
    from specbridge.comm.diagnose import rules as RU
    out = list(qs); base = [_ex_sql(db, q) for q in qs]
    for q, b in zip(qs, base):
        for st in RU.sites(q):
            if st[0] == "dedup": continue
            e = RU.edit(q, st); r = _ex_sql(db, e) if e else None
            if r is not None and b is not None and not same(r, b) and e not in out: out.append(e)
    return out


def report_method(model="sonnet"):
    from specbridge.comm.common import grade as G
    R = method_rows(); dec = json.load(open(OUT + "/decomposition.json"))["models"].get(model, {}).get("shape", {}).get("questions") or \
        json.load(open(OUT + "/decomposition.json"))["models"][model]["questions"]
    # (row, index into the AMBIGUOUS question's gold) -> plain missed it AND the model computes it when asked. The decomposition
    # lists readings in the order of the unambiguous questions; they are matched to the ambiguous gold by executed result.
    comp = {}; SP = specifics("dev"); Rr = {r["row"]: r for r in rows()}
    for q in json.load(open(OUT + "/decomposition.json"))["models"][model]["questions"]:
        r = Rr[q["row"]]; gres = [_ex_sql(r["db_file"], g) for g in r["gold"]]
        for k, p in zip(SP[q["row"]], q["readings"]):
            kr = _ex_sql(r["db_file"], k[2])
            for i, g in enumerate(gres):
                if g is not None and kr is not None and same(kr, g) and same(g, kr): comp[(q["row"], i)] = (not p["open_shape"]) and p["spec_shape"]
    def score(r, qs):
        golds = r["gold"]; db = r["db_file"]; P_ = [x for x in (_ex_sql(db, q) for q in set(qs)) if x is not None]
        hit = [any(G.shape_tolerant([list(y) for y in _ex_sql(db, g)], [list(y) for y in p]) for p in P_) for g in golds]
        hs = [any(same(p, _ex_sql(db, g), "order by" in g.lower()) for p in P_) for g in golds]
        good = [any(G.shape_tolerant([list(y) for y in _ex_sql(db, g)], [list(y) for y in p]) for g in golds) for p in P_]
        return {"hit": hit, "strict": hs, "prec": sum(good) / len(good) if good else 0.0, "n": len(P_)}
    arms = {"plain": lambda r: json.load(open(_f("plain", model, r)))["preds"] if os.path.exists(_f("plain", model, r)) else None}
    for a in ("dtp", "samplek", "ours"):
        arms[a] = (lambda a: lambda r: json.load(open(_mf(a, model, r)))["queries"] if os.path.exists(_mf(a, model, r)) else None)(a)
    arms["ours (dedup)"] = lambda r: _dedup(r["db_file"], arms["ours"](r)) if arms["ours"](r) is not None else None
    arms["ours2 (dedup)"] = lambda r: _dedup(r["db_file"], json.load(open(_mf("ours2", model, r)))["queries"]) if os.path.exists(_mf("ours2", model, r)) else None
    arms["ours+lib (dedup)"] = lambda r: _dedup(r["db_file"], _with_library(r["db_file"], arms["ours"](r))) if arms["ours"](r) is not None else None
    cost = lambda a, r: (json.load(open(_mf(a, model, r))).get("cost") if a in ("dtp", "samplek", "ours", "ours2") and os.path.exists(_mf(a, model, r)) else None)
    prev = open(OUT + "/method/RESULTS.md").read().split("\n## "); keep = [prev[0].rstrip()] + ["## " + x.rstrip() for x in prev[1:] if not x.startswith("Results, ")]
    L = ["\n\n".join(keep), "", "## Results, %s (dev)\n" % model,
         "Shape-tolerant (primary) / strict. Precision: share of returned queries matching a gold reading, on unambiguous questions.\n",
         "| arm | ambiguous n | AllFound | recall | computable misses recovered | unambiguous n | precision | queries per question | calls / chars in per question |", "|---|---|---|---|---|---|---|---|---|"]
    res = {}
    for a, get in arms.items():
        A = [(r, get(r)) for r in R if r["ambiguous"]]; A = [(r, q) for r, q in A if q is not None]
        U = [(r, get(r)) for r in R if not r["ambiguous"]]; U = [(r, q) for r, q in U if q is not None]
        SA = [(r, score(r, q)) for r, q in A]; SU = [score(r, q) for r, q in U]
        af = sum(all(s["hit"]) for _r, s in SA); afs = sum(all(s["strict"]) for _r, s in SA)
        rec = sum(sum(s["hit"]) / len(s["hit"]) for _r, s in SA) / max(1, len(SA)); recs = sum(sum(s["strict"]) / len(s["strict"]) for _r, s in SA) / max(1, len(SA))
        cm = [(r["row"], i) for r, s in SA for i in range(len(s["hit"])) if comp.get((r["row"], i))]
        rcv = sum(dict(((r["row"], i), s["hit"][i]) for r, s in SA for i in range(len(s["hit"])))[k] for k in cm)
        pr = sum(s["prec"] for s in SU) / max(1, len(SU)); nq = sum(s["n"] for _r, s in SA + [(None, x) for x in SU]) / max(1, len(SA) + len(SU))
        base = a.split(" ")[0].replace("+lib", ""); cs = [cost(base, r) for r in R]; cs = [c for c in cs if c]
        res[a] = {"allfound": af, "recall": rec, "recovered": rcv, "computable": len(cm), "precision": pr}
        L.append("| %s | %d | %d / %d | %.2f / %.2f | %d of %d (%.0f%%) | %d | %.2f | %.1f | %s |" % (a, len(SA), af, afs, rec, recs, rcv, len(cm), 100 * rcv / max(1, len(cm)), len(SU), pr, nq,
                 "%.1f / %d" % (sum(c["calls"] for c in cs) / len(cs), sum(c["chars_in"] for c in cs) / len(cs)) if cs else "1 / saved"))
    o, d, p = res.get("ours (dedup)"), res.get("dtp"), res.get("plain")
    if o and d and p:
        ok = (o["allfound"] > d["allfound"] or o["recall"] > d["recall"]) and o["recovered"] >= 0.3 * max(1, o["computable"]) and (p["precision"] - o["precision"]) <= 0.03
        L.append("\n**Gate (ours with dedup): %s.** AllFound %d vs DtP %d; recall %.2f vs %.2f; computable misses recovered %d of %d; precision %.2f vs plain %.2f."
                 % ("PASS" if ok else "FAIL", o["allfound"], d["allfound"], o["recall"], d["recall"], o["recovered"], o["computable"], o["precision"], p["precision"]))
    open(OUT + "/method/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))



# --- FINAL TEST (2026-10-13): frozen method on fresh test-split questions -----------------------------------------------------
# 30 ambiguous + 20 unambiguous per type, seeded, excluding every dev / confirmation question and every unambiguous child of them.
# Arms, all jobs shuffled together (interleaved): plain, dtp, samplek (k = 3, fixed on dev), ours (frozen: no second pass), and the
# specific (unambiguous-version) calls of each ambiguous question, for "computable misses recovered". A call refused by a safety
# filter is logged; that question is then excluded from every arm for that solver.
FINAL = OUT + "/final"; K_FROZEN = 3


def final_rows(n_amb=30, n_un=20):
    import pandas as pd
    d = pd.read_csv(DATA + "/data/ambrosia.csv"); d = d[d.split == "test"]
    used_amb = {(r["db_file"].replace(DATA + "/", "", 1), r["question"]) for r in rows() + conf_rows() if r["ambiguous"]}
    used_rows = {r["row"] for r in rows()}
    out = []
    for typ in ("scope", "attachment", "vague"):
        a = d[(d.ambig_type == typ) & (d.question_type == "ambig")]; ia = [i for i in sorted(a.index) if (a.loc[i, "db_file"], a.loc[i, "question"]) not in used_amb]
        random.Random("%d-final-amb-%s" % (SEED, typ)).shuffle(ia)
        u = d[(d.ambig_type == typ) & (d.question_type == "unambig")]
        iu = [i for i in sorted(u.index) if int(u.loc[i, "Unnamed: 0"]) not in used_rows and (u.loc[i, "db_file"], u.loc[i, "ambig_question"]) not in used_amb]
        random.Random("%d-final-un-%s" % (SEED, typ)).shuffle(iu)
        for idx, amb, n in ((ia, True, n_amb), (iu, False, n_un)):
            for i in idx[:n]:
                r = d.loc[i]; out.append({"row": int(r["Unnamed: 0"]), "type": typ, "ambiguous": amb, "question": r["question"],
                                          "gold": [q.strip() for q in r["gold_queries"].split("\n\n") if q.strip()], "db_file": DATA + "/" + r["db_file"], "dump": r["db_dump"]})
    return out


def final_specifics():
    import pandas as pd
    d = pd.read_csv(DATA + "/data/ambrosia.csv"); u = d[d.question_type == "unambig"]; out = {}
    for r in final_rows():
        if not r["ambiguous"]: continue
        kids = u[(u.db_file == r["db_file"].replace(DATA + "/", "", 1)) & (u.ambig_question == r["question"])]
        out[r["row"]] = [(int(k["Unnamed: 0"]), k["question"], k["gold_queries"].strip()) for _i, k in kids.iterrows()]
    return out


def _ff(arm, m, row):
    f = "%s/%s/%s/%s.json" % (FINAL, arm, m, row); os.makedirs(os.path.dirname(f), exist_ok=True); return f


def run_final(models=("sonnet", "gpt-6-sol"), workers=6):
    from specbridge.pd.ask import ask as raw_ask
    from specbridge.comm.common.llm import parse as jparse
    import threading
    P = _dtp_prompts(); R = {r["row"]: r for r in final_rows()}; SP = final_specifics(); lock = threading.Lock(); os.makedirs(FINAL, exist_ok=True)
    def call(p, m, row, arm, sink):
        try: t = raw_ask(p, m, timeout=1500, quiet=True) or ""
        except Exception as e:
            t = ""
            if "safeguard" in str(e).lower() or "usage policy" in str(e).lower():
                with lock: open(FINAL + "/refusals.jsonl", "a").write(json.dumps({"model": m, "row": row, "arm": arm, "error": str(e)[:200]}) + "\n")
        sink["calls"] += 1; sink["chars_in"] += len(p); sink["chars_out"] += len(t); return t
    def job(j):
        arm, m, row, extra = j; r = R[row]; f = _ff(arm, m, row if extra is None else "%s__%d" % (row, extra[0]))
        if os.path.exists(f): return
        c = collections.Counter()
        if arm == "plain":
            t = call(prompt("plain", r), m, row, arm, c)
            if not t.strip(): return
            out = {"queries": parse(t)}
        elif arm == "specific":
            t = call(prompt("plain", dict(r, question=extra[1])), m, row, arm, c)
            if not t.strip(): return
            out = {"specific_row": extra[0], "queries": parse(t)}
        elif arm == "samplek":
            qs = []
            for _ in range(K_FROZEN):
                t = call(prompt("plain", r), m, row, arm, c); qs += parse(t) if t.strip() else []
            out = {"queries": qs}
        elif arm == "dtp":
            t = call(P["user_message_interpr_ambig"].format(r["dump"], r["question"]), m, row, arm, c)
            if not t.strip(): return
            ints = [item_line(x) for x in t.splitlines() if item_line(x)]
            miss = call(P["user_message_interpr_ambig_missing"].format(r["dump"], r["question"], "\n".join(ints)), m, row, arm, c)
            if "all possible interpretations are covered" not in miss.lower():
                ints += [item_line(x) for x in miss.splitlines() if item_line(x)]
            qs = []
            for it in ints[:6]: qs += parse_one(call(P["user_message_sql"].format(r["dump"], it), m, row, arm, c))[:1]
            out = {"interpretations": ints, "queries": qs, "raw": [t, miss]}
        else:                                                       # ours (frozen)
            t = call(DETECT % (r["dump"], r["question"]), m, row, arm, c)
            if not t.strip(): return
            reads = [x for x in ((jparse(t, "{") or {}).get("readings") or []) if isinstance(x, str) and x.strip()] or [r["question"]]
            qs = []
            for rd in (reads[:1] if len(reads) == 1 else reads[:4]): qs += parse_one(call(P["user_message_sql"].format(r["dump"], rd), m, row, arm, c))[:1]
            out = {"readings": reads, "queries": qs, "raw": [t]}
        json.dump(dict(out, row=row, model=m, arm=arm, cost=dict(c)), open(f, "w"), indent=1)
    jobs = [(a, m, row, None) for row in R for m in models for a in ("plain", "dtp", "samplek", "ours")] + \
           [("specific", m, row, k) for row, ks in SP.items() for k in ks for m in models]
    random.Random(SEED + 31).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(job, jobs))
    report_final(models)


def _pci(v, bsp):
    b = bsp(v) if v else [0, 0]; return (sum(v) / max(1, len(v)), b[int(.025 * len(b))], b[int(.975 * len(b)) - 1])


def _pci_c(v, n, rng, B_=2000):
    b = sorted(sum(v[rng.randrange(len(v))] for _ in v) / max(1, n) for _ in range(B_)) if v else [0, 0]
    return (sum(v) / max(1, n), b[int(.025 * len(b))], b[int(.975 * len(b)) - 1])


def report_final(models=("sonnet", "gpt-6-sol"), B_=2000):
    from specbridge.comm.common import grade as G
    R = final_rows(); SP = final_specifics(); refused = collections.defaultdict(set)
    if os.path.exists(FINAL + "/refusals.jsonl"):
        for l in open(FINAL + "/refusals.jsonl"): x = json.loads(l); refused[x["model"]].add(x["row"])
    ld = lambda arm, m, key: json.load(open(_ff(arm, m, key)))["queries"] if os.path.exists(_ff(arm, m, key)) else None
    def sc(r, qs):
        db = r["db_file"]; P_ = [x for x in (_ex_sql(db, q) for q in set(_dedup(db, qs))) if x is not None]; gs = [_ex_sql(db, g) for g in r["gold"]]
        hit = [any(G.shape_tolerant([list(y) for y in g], [list(y) for y in p]) for p in P_) for g in gs]
        good = [any(G.shape_tolerant([list(y) for y in g], [list(y) for y in p]) for g in gs) for p in P_]
        return hit, (sum(good) / len(good) if good else 0.0), len(P_)
    L = [open(OUT + "/method/RESULTS.md").read().split("\n## Results, final")[0].rstrip(), "", "## Results, final test (fresh test-split questions)\n",
         "Shape-tolerant. Intervals: Wilson (AllFound), paired bootstrap over questions (recall, precision, differences). Items with any refused call are excluded from every arm for that solver.\n"]
    pooled = {"A": [], "R": [], "P": [], "solvers": []}; JS = {"solvers": {}, "pooled": {}}
    for m in models:
        if not os.path.isdir("%s/ours/%s" % (FINAL, m)): continue
        ex = refused.get(m, set()); A = [r for r in R if r["ambiguous"] and r["row"] not in ex]; U = [r for r in R if not r["ambiguous"] and r["row"] not in ex]
        arms = ("plain", "dtp", "samplek", "ours"); S_ = {a: {} for a in arms}
        for a in arms:
            for r in A + U:
                q = ld(a, m, r["row"])
                if q is not None: S_[a][r["row"]] = sc(r, q)
        A = [r for r in A if all(r["row"] in S_[a] for a in arms)]; U = [r for r in U if all(r["row"] in S_[a] for a in arms)]
        comp = {}                                                  # (row, gold index) computable miss: plain missed, specific right
        for r in A:
            gs = [_ex_sql(r["db_file"], g) for g in r["gold"]]
            for k in SP[r["row"]]:
                q = ld("specific", m, "%s__%d" % (r["row"], k[0])); kr = _ex_sql(r["db_file"], k[2])
                if q is None or kr is None: continue
                first = _ex_sql(r["db_file"], q[0]) if q else None; right = first is not None and G.shape_tolerant([list(y) for y in kr], [list(y) for y in first])
                for i, g in enumerate(gs):
                    if g is not None and same(kr, g) and same(g, kr): comp[(r["row"], i)] = (not S_["plain"][r["row"]][0][i]) and right
        cm = [k for k, v in comp.items() if v]
        rng = random.Random(SEED); bs = lambda vals: sorted(sum(vals[rng.randrange(len(vals))] for _ in vals) / len(vals) for _ in range(B_)) if vals else [0, 0]
        ci = lambda v: "[%.2f, %.2f]" % (v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]) if v and len(v) > 2 else ""
        L += ["### %s: %d ambiguous, %d unambiguous (%d excluded for refusals)\n" % (m, len(A), len(U), len(ex)),
              "| arm | AllFound [Wilson 95%] | recall [95%] | computable misses recovered | precision on unambiguous [95%] | calls / chars in per question |", "|---|---|---|---|---|---|"]
        for a in arms:
            af = sum(all(S_[a][r["row"]][0]) for r in A); w = wilson(af, len(A)); rec = [sum(S_[a][r["row"]][0]) / len(S_[a][r["row"]][0]) for r in A]
            pre = [S_[a][r["row"]][1] for r in U]; rv = sum(S_[a][row][0][i] for row, i in cm)
            cs = [json.load(open(_ff(a, m, r["row"]))).get("cost", {}) for r in A + U]
            wr = wilson(rv, len(cm))
            JS["solvers"].setdefault(m, {"n_ambiguous": len(A), "n_unambiguous": len(U), "excluded": len(ex), "computable": len(cm), "arms": {}})["arms"][a] = {
                "allfound": af, "allfound_ci": w, "recall": sum(rec) / max(1, len(rec)), "recovered": rv, "recovered_ci": wr, "precision": sum(pre) / max(1, len(pre)),
                "calls": sum(c.get("calls", 0) for c in cs) / max(1, len(cs)), "chars_in": sum(c.get("chars_in", 0) for c in cs) / max(1, len(cs))}
            L.append("| %s | %d/%d (%.0f%%) [%.0f, %.0f] | %.3f %s | %d of %d (%.0f%%) [%.0f, %.0f] | %.3f %s | %.1f / %d |" % (a, af, len(A), 100 * af / max(1, len(A)), 100 * w[0], 100 * w[1],
                     sum(rec) / max(1, len(rec)), ci(bs(rec)), rv, len(cm), 100 * rv / max(1, len(cm)), 100 * wr[0], 100 * wr[1], sum(pre) / max(1, len(pre)), ci(bs(pre)),
                     sum(c.get("calls", 0) for c in cs) / max(1, len(cs)), sum(c.get("chars_in", 0) for c in cs) / max(1, len(cs))))
        # PAIRED BY QUESTION: ours vs each comparison arm on AllFound, recall, precision, and computable misses recovered (per
        # question, the number of its computable misses the arm recovers; the difference is bootstrapped over questions and divided
        # by the total number of computable misses)
        cmq = collections.defaultdict(list)
        for row, i in cm: cmq[row].append(i)
        def paired(b):
            dA_ = [int(all(S_["ours"][r["row"]][0])) - int(all(S_[b][r["row"]][0])) for r in A]
            dR_ = [sum(S_["ours"][r["row"]][0]) / len(S_["ours"][r["row"]][0]) - sum(S_[b][r["row"]][0]) / len(S_[b][r["row"]][0]) for r in A]
            dP_ = [S_["ours"][r["row"]][1] - S_[b][r["row"]][1] for r in U]
            dC_ = [sum(S_["ours"][r["row"]][0][i] for i in cmq.get(r["row"], [])) - sum(S_[b][r["row"]][0][i] for i in cmq.get(r["row"], [])) for r in A]
            return dA_, dR_, dP_, dC_
        for b in ("dtp", "samplek"):
            dA_, dR_, dP_, dC_ = paired(b); n_cm = max(1, len(cm))
            bC = sorted(sum(dC_[rng.randrange(len(dC_))] for _ in dC_) / n_cm for _ in range(B_)) if dC_ else [0, 0]
            fmt = lambda v, b_: "%+.3f [%.3f, %.3f]" % (sum(v) / max(1, len(v)), b_[int(.025 * len(b_))], b_[int(.975 * len(b_)) - 1])
            L.append("Ours - %s (paired by question): AllFound %s; recall %s; precision %s; computable misses recovered %+.3f [%.3f, %.3f] (share of the %d)." % (
                {"dtp": "DtP", "samplek": "sample-k"}[b], fmt(dA_, bs(dA_)), fmt(dR_, bs(dR_)), fmt(dP_, bs(dP_)), sum(dC_) / n_cm, bC[int(.025 * len(bC))], bC[int(.975 * len(bC)) - 1], len(cm)))
            pooled.setdefault("vs_" + b, {"A": [], "R": [], "P": [], "C": [], "ncm": 0})
            q = pooled["vs_" + b]; q["A"] += dA_; q["R"] += dR_; q["P"] += dP_; q["C"] += dC_; q["ncm"] += len(cm)
        dA = [int(all(S_["ours"][r["row"]][0])) - int(all(S_["dtp"][r["row"]][0])) for r in A]
        dR = [sum(S_["ours"][r["row"]][0]) / len(S_["ours"][r["row"]][0]) - sum(S_["dtp"][r["row"]][0]) / len(S_["dtp"][r["row"]][0]) for r in A]
        dP = [S_["ours"][r["row"]][1] - S_["dtp"][r["row"]][1] for r in U]
        bA, bR, bP = bs(dA), bs(dR), bs(dP); lo = lambda v: v[int(.025 * len(v))]; hi = lambda v: v[int(.975 * len(v)) - 1]
        L += ["", "Ours - DtP (paired, this solver): AllFound %+.3f [%.3f, %.3f]; recall %+.3f [%.3f, %.3f]; precision %+.3f [%.3f, %.3f].\n" % (
            sum(dA) / max(1, len(dA)), lo(bA), hi(bA), sum(dR) / max(1, len(dR)), lo(bR), hi(bR), sum(dP) / max(1, len(dP)), lo(bP), hi(bP))]
        pooled["A"] += dA; pooled["R"] += dR; pooled["P"] += dP; pooled["solvers"].append(m)
    if pooled["A"]:
        rng2 = random.Random(SEED + 1); bsp = lambda v: sorted(sum(v[rng2.randrange(len(v))] for _ in v) / len(v) for _ in range(B_))
        bA, bR, bP = bsp(pooled["A"]), bsp(pooled["R"]), bsp(pooled["P"]); lo = lambda v: v[int(.025 * len(v))]; hi = lambda v: v[int(.975 * len(v)) - 1]
        for k in ("vs_dtp", "vs_samplek"):
            if k in pooled: JS["pooled"][k] = {"allfound": _pci(pooled[k]["A"], bsp), "recall": _pci(pooled[k]["R"], bsp), "precision": _pci(pooled[k]["P"], bsp),
                                              "recovered": _pci_c(pooled[k]["C"], pooled[k]["ncm"], rng2), "computable": pooled[k]["ncm"]}
        JS["pooled"]["claim"] = {"coverage_noninferior": lo(bA) >= -0.10 and lo(bR) >= -0.10, "precision_higher": lo(bP) > 0}
        L += ["### Pooled over %s (the claim is judged here)\n" % " + ".join(pooled["solvers"]),
              "Ours - DtP: AllFound %+.3f [%.3f, %.3f]; recall %+.3f [%.3f, %.3f]; precision %+.3f [%.3f, %.3f]." % (
                  sum(pooled["A"]) / len(pooled["A"]), lo(bA), hi(bA), sum(pooled["R"]) / len(pooled["R"]), lo(bR), hi(bR), sum(pooled["P"]) / max(1, len(pooled["P"])), lo(bP), hi(bP)),
              *["Ours - %s, pooled: AllFound %+.3f [%.3f, %.3f]; recall %+.3f [%.3f, %.3f]; precision %+.3f [%.3f, %.3f]; computable misses recovered %+.3f [%.3f, %.3f] (of %d)." % (
                  {"vs_dtp": "DtP", "vs_samplek": "sample-k"}[k], *_pci(pooled[k]["A"], bsp), *_pci(pooled[k]["R"], bsp), *_pci(pooled[k]["P"], bsp),
                  *_pci_c(pooled[k]["C"], pooled[k]["ncm"], rng2), pooled[k]["ncm"]) for k in ("vs_dtp", "vs_samplek") if k in pooled],
              "Claim: coverage non-inferior (both lower bounds >= -0.10): %s; precision higher (lower bound > 0): %s.%s" % (
                  "yes" if lo(bA) >= -0.10 and lo(bR) >= -0.10 else "no", "yes" if lo(bP) > 0 else "no",
                  "" if len(pooled["solvers"]) == 2 else " (PROVISIONAL: one solver only; the claim is judged on both)")]
    json.dump(JS, open(FINAL + "/final.json", "w"), indent=1)
    open(OUT + "/method/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: run(sys.argv[2:] or MODELS), "report": report, "decomp_run": lambda: decomp_run([x for x in sys.argv[2:] if x not in ("dev", "conf")] or MODELS, "conf" if "conf" in sys.argv else "dev"),
     "decomp_report": lambda: decomp_report("conf" if "conf" in sys.argv else "dev"),
     "run_method": lambda: run_method(*(sys.argv[2:3] or ["sonnet"])), "run_variant": lambda: run_variant(*(sys.argv[2:3] or ["sonnet"])),
     "run_final": lambda: run_final(), "report_final": lambda: report_final(), "report_method": lambda: report_method(*(sys.argv[2:3] or ["sonnet"]))}[sys.argv[1]]()
