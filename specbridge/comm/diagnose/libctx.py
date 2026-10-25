"""LEARNING THE USERS' COMMUNICATION FROM THE AMBIGUITY LIBRARY, IN CONTEXT (2026-10-12). The library's full records are past requests
of the same users (BIRD dev, Spider dev) where a model misread what the request left unsaid: the request, the choice it hid, the
reading the users meant (their reference), and the reading that was wrong. For a NEW question on a database the library never used,
records are put before the question by a VARIANT (a function of the retrieved records); no model, no gold of the new question.

CHEAP ITERATION LOOP. The 361 BIRD dev questions from the 6 databases the library never used are split ONCE (seeded): DEV (80) for
trying variants, HOLD (the next 80) for a quick held-out signal on a few chosen variants, TEST (the other 201) touched only
once, to confirm the final variant. One solver, one round by default, so a variant costs
80 calls; the plain baseline and every variant are cached per (split, rounds, variant, model) and never rerun.
    python -m specbridge.comm.diagnose.libctx run <variant> [<variant> ...] [--model haiku] [--split dev] [--rounds 1]
    python -m specbridge.comm.diagnose.libctx report [--model haiku] [--split dev] [--rounds 1]
    -> out/libctx/<split>/r<rounds>/<variant>/<model>/<id>.json, out/libctx/<split>/r<rounds>/RESULTS_<model>.md
Every variant is compared with plain and with fewshot on the same questions (exact McNemar; BIRD set match, shape-tolerant beside it).
At most 6 workers."""
import concurrent.futures as cf, json, math, os, random, re, sys
from specbridge.comm.diagnose import prior as P

LIB, OUT, K, SEED, NDEV = "library/examples.jsonl", "out/libctx", 3, 20261015, 80


def records():
    """Full records only: a reading equal to the reference and one that differs."""
    R = [json.loads(l) for l in open(LIB)]
    return [r for r in R if any(x.get("differs_from_gold") is False for x in r.get("readings") or []) and any(x.get("differs_from_gold") is True for x in r.get("readings") or [])]


class Retriever:
    def __init__(self, R):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.R = R; self.v = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
        self.X = self.v.fit_transform([r["question"] for r in R])
    def top(self, text, k=K):
        s = (self.X @ self.v.transform([text]).T).toarray().ravel()
        return [self.R[i] for i in sorted(range(len(self.R)), key=lambda i: (-s[i], self.R[i]["id"]))[:k]]


def _meant(r): return next(x for x in r["readings"] if x.get("differs_from_gold") is False)
def _wrong(r): return next(x for x in r["readings"] if x.get("differs_from_gold") is True)
HEAD = "PAST REQUESTS FROM THE SAME USERS (other databases). %s Read the new request the way these users write and mean their requests.\n\n"


# --- VARIANTS: name -> block(records). Add a variant here; never edit one that has results (its cache would no longer match). ---
def v_plain(recs): return ""
def v_fewshot(recs):
    return HEAD % "Each shows the request and the SQL they accepted." + "\n\n".join(
        "Past request %d: %s\nTheir SQL: %s" % (i, r["question"], r["gold_sql"]) for i, r in enumerate(recs, 1)) + "\n\nNEW REQUEST:\n"
def v_library(recs):
    return HEAD % "Each shows what the request left unsaid, what these users meant, and the misreading to avoid." + "\n\n".join(
        "Past request %d: %s\nWhat it left unsaid: %s\nWhat these users meant: %s\nThe misreading: %s\nTheir SQL: %s"
        % (i, r["question"], r["decision"], _meant(r)["reading"], _wrong(r)["reading"], r["gold_sql"]) for i, r in enumerate(recs, 1)) + "\n\nNEW REQUEST:\n"
def _first(t): return re.split(r"(?<=[.;])\s", t.strip())[0]
def v_short(recs):
    """fewshot + one short line per record: the choice it left unsaid and the reading these users meant (first sentence)."""
    return HEAD % "Each shows the request, the choice it left unsaid with the reading these users meant, and the SQL they accepted." + "\n\n".join(
        "Past request %d: %s\nLeft unsaid: %s -> these users meant: %s\nTheir SQL: %s" % (i, r["question"], _first(r["decision"]), _first(_meant(r)["reading"]), r["gold_sql"])
        for i, r in enumerate(recs, 1)) + "\n\nNEW REQUEST:\n"
def v_fewshot5(recs): return v_fewshot(recs)                    # k = 5 is set in run() by name
FORM = ("HOW THESE USERS WANT ANSWERS (measured on their own training requests): return only what the request asks for, in the order "
        "it asks; when it asks for the highest or lowest item, return the item, not the value used to sort it (93%% of their answers); "
        "keep duplicate rows of a join unless the request says distinct, different or unique (83%%); do not add identifiers, counts or "
        "columns used only to filter.\n\n")
def v_form(recs): return FORM.replace("%%", "%") + v_fewshot(recs)
def v_formonly(recs): return FORM.replace("%%", "%")
def v_formshort(recs): return FORM.replace("%%", "%") + v_short(recs)
NEUTRAL = ("HOW THESE USERS WANT QUERIES WRITTEN (their own habits when they write SQL): write keywords such as SELECT, FROM and "
           "WHERE in upper case; give each joined table a short alias and use it for every column from that table; write joins with "
           "explicit JOIN ... ON; put each major clause on its own line; use single quotes for text values; leave one space around each "
           "operator and after each comma; indent a subquery and give it a readable alias; do not add comments.\n\n")
def v_placebo(recs): return NEUTRAL + v_fewshot(recs)          # length control for form: same examples, same position, neutral text
VARIANTS = {"plain": v_plain, "plain_s2": v_plain, "plain_s3": v_plain, "placebo": v_placebo, "fewshot": v_fewshot, "library": v_library, "short": v_short, "fewshot5": v_fewshot5, "form": v_form, "formonly": v_formonly, "formshort": v_formshort}


NHOLD2 = 200


def build_hold2():
    """HOLD2 (2026-10-12): 200 more held-out questions, drawn (seeded) from the clean-database BIRD dev questions OUTSIDE the
    600-question sample, so no variant was ever tried on them. Same task format as prior.build; references that do not run are skipped."""
    from specbridge.comm.common import db as DB
    from specbridge.comm.diagnose.tasks import BIRD_DBS
    f = OUT + "/hold2_tasks.jsonl"
    if os.path.exists(f): return [json.loads(l) for l in open(f)]
    dev = json.load(open(P.ROOT + "/dev.json")); used = {t["question_id"] for t in P.tasks()}; snaps = DB.snapshots()
    xs = sorted((x for x in dev if x["db_id"] not in BIRD_DBS and x["question_id"] not in used), key=lambda x: x["question_id"])
    random.Random(SEED + 2).shuffle(xs); T = []
    for x in xs:
        if len(T) == NHOLD2: break
        db = x["db_id"]; snap = snaps.get(db, ("%s/dev_databases/%s/%s.sqlite" % (P.ROOT, db, db), None))[0]; ref = DB.rows(DB.connect(snap), x["SQL"])
        if ref is None: continue
        T.append({"id": "q%04d" % x["question_id"], "question_id": x["question_id"], "database": db, "snapshot": snap, "difficulty": x["difficulty"],
                  "instruction": x["question"] + ("\nEvidence: " + x["evidence"] if x.get("evidence") else ""), "reference_sql": x["SQL"], "reference_answer": ref})
    os.makedirs(OUT, exist_ok=True)
    with open(f, "w") as fh:
        for t in T: fh.write(json.dumps(t, default=str) + "\n")
    return T


def split(name):
    if name == "hold2": return build_hold2()
    from specbridge.comm.diagnose.tasks import BIRD_DBS
    T = [t for t in P.tasks() if t["database"] not in BIRD_DBS]; ids = sorted(t["id"] for t in T); random.Random(SEED).shuffle(ids)
    keep = set({"dev": ids[:NDEV], "hold": ids[NDEV:2 * NDEV], "test": ids[2 * NDEV:]}[name])   # dev: try variants; hold: quick
    return [t for t in T if t["id"] in keep]                                                     # held-out signal; test: final only


def _dir(sp, rounds): return "%s/%s/r%d" % (OUT, sp, rounds)
def _out(sp, rounds, v, m): return "%s/%s/%s" % (_dir(sp, rounds), v, re.sub(r"\W", "_", m))


def run(variants, model="haiku", sp="dev", rounds=1, workers=6):
    from specbridge.comm.common.solve import solve
    T = split(sp); ret = Retriever(records()); ctx = {t["id"]: ret.top(t["instruction"]) for t in T}; ctx5 = {t["id"]: ret.top(t["instruction"], 5) for t in T}
    os.makedirs(_dir(sp, rounds), exist_ok=True)
    json.dump({t["id"]: [r["id"] for r in ctx[t["id"]]] for t in T}, open(_dir(sp, rounds) + "/retrieved.json", "w"), indent=1)   # auditable
    jobs = [(t, v) for t in T for v in ["plain"] + [v for v in variants if v != "plain"]]
    def one(job):
        t, v = job; out = _out(sp, rounds, v, model); f = "%s/%s.json" % (out, t["id"])
        if os.path.exists(f) and "pass" in json.load(open(f)): return
        try:
            r = solve([{"key": t["id"], "text": VARIANTS[v]((ctx5 if v.endswith("5") else ctx)[t["id"]]) + t["instruction"], "snapshot": t["snapshot"], "database": t["database"]}],
                      model, out, bsize=1, rounds=rounds, workers=1)
            if t["id"] in r: P._grade_save(r[t["id"]], t, out)
        except Exception as e: print("failed", v, t["id"], e, flush=True)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report(model, sp, rounds)


def report(model="haiku", sp="dev", rounds=1, quiet=False):
    T = split(sp); d = _dir(sp, rounds); vs = [v for v in VARIANTS if os.path.isdir(_out(sp, rounds, v, model))]
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, i) for i in range(min(b, c) + 1)) / 2 ** (b + c))
    G = {}
    for v in vs:
        for t in T:
            f = "%s/%s.json" % (_out(sp, rounds, v, model), t["id"])
            if os.path.exists(f):
                o = json.load(open(f))
                if "pass" in o: G[(v, t["id"])] = (bool(o["pass"]), bool(o["shape"]))
    L = ["# Library in context, %s split, %s, %d round(s) (`specbridge.comm.diagnose.libctx`)\n" % (sp, model, rounds),
         "%d questions from BIRD databases the library never used; k = %d retrieved records. Per variant, on the questions graded for it "
         "and for the comparison arm: correct (BIRD set match) [shape-tolerant]; vs plain and vs fewshot: questions gained / lost, exact McNemar p.\n" % (len(T), K),
         "| variant | n | correct [shape] | vs plain | vs fewshot | vs placebo |", "|---|---|---|---|---|---|"]
    res = {"split": sp, "model": model, "rounds": rounds, "n": len(T), "variants": {}}
    for v in vs:
        ids = [t["id"] for t in T if (v, t["id"]) in G]; x = {"n": len(ids), "pass": sum(G[(v, i)][0] for i in ids), "shape": sum(G[(v, i)][1] for i in ids)}
        cells = []
        for b in ("plain", "fewshot", "placebo"):
            if v == b or b not in vs: cells.append(""); continue
            both = [i for i in ids if (b, i) in G]; u = sum(G[(v, i)][0] and not G[(b, i)][0] for i in both); dn = sum(G[(b, i)][0] and not G[(v, i)][0] for i in both)
            x["vs_" + b] = {"n": len(both), "up": u, "down": dn, "p": mc(u, dn), "base": sum(G[(b, i)][0] for i in both)}
            cells.append("+%d/-%d of %d (p %.2g)" % (u, dn, len(both), mc(u, dn)))
        res["variants"][v] = x; L.append("| %s | %d | %d [%d] | %s | %s | %s |" % (v, x["n"], x["pass"], x["shape"], *cells))
    json.dump(res, open("%s/results_%s.json" % (d, re.sub(r"\W", "_", model)), "w"), indent=1); open("%s/RESULTS_%s.md" % (d, re.sub(r"\W", "_", model)), "w").write("\n".join(L) + "\n")
    if not quiet: print("\n".join(L))



# --- SUMMARY over held-out splits (2026-10-12): per solver, plain's output-form errors vs form's gain over the placebo -------------
SOLVERS = ["haiku", "gpt-6-luna", "gpt-6-sol", "sonnet"]


def summary(splits=("hold", "hold2"), rounds=1, Bs=4000):
    """Per solver on the pooled held-out questions: plain's output-form errors (shape-tolerant minus strict), form - placebo with a
    paired bootstrap 95% CI, exact McNemar; pooled McNemar over solvers (the main test). -> out/libctx/SUMMARY.md, summary.json, form_gain.png"""
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, i) for i in range(min(b, c) + 1)) / 2 ** (b + c))
    def g(sp, v, m, i):
        f = "%s/%s.json" % (_out(sp, rounds, v, m), i)
        if not os.path.exists(f): return None
        o = json.load(open(f)); return (bool(o["pass"]), bool(o["shape"])) if "pass" in o else None
    res = {"splits": list(splits), "solvers": {}}; W = Lo = 0
    L = ["# Form vs placebo on held-out BIRD questions (`specbridge.comm.diagnose.libctx summary`)\n",
         "Splits %s; questions with plain, placebo and form all graded. Format errors = plain's shape-tolerant minus strict correct. "
         "Gain = form minus placebo, points, paired bootstrap 95%% CI; p exact McNemar.\n" % ", ".join(splits),
         "| solver | n | plain | placebo | form | plain format errors | form format errors | form - placebo [95% CI] | wins/losses | p |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for m in SOLVERS:
        rows = []
        for sp in splits:
            for t in split(sp):
                x = {v: g(sp, v, m, t["id"]) for v in ("plain", "placebo", "form")}
                if all(x.values()): rows.append(x)
        if not rows: continue
        n = len(rows); c = {v: sum(r[v][0] for r in rows) for v in ("plain", "placebo", "form")}
        fe = {v: sum(r[v][1] and not r[v][0] for r in rows) for v in ("plain", "form")}
        d = [int(r["form"][0]) - int(r["placebo"][0]) for r in rows]; rng = random.Random(SEED)
        bs = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(Bs)); ci = (100 * bs[int(.025 * Bs)], 100 * bs[int(.975 * Bs) - 1])
        w, lo = sum(x > 0 for x in d), sum(x < 0 for x in d); W += w; Lo += lo
        res["solvers"][m] = {"n": n, "correct": c, "format_errors": fe, "gain_points": 100 * sum(d) / n, "ci95": ci, "wins": w, "losses": lo, "p": mc(w, lo)}
        L.append("| %s | %d | %d | %d | %d | %d | %d | %+.1f [%+.1f, %+.1f] | %d/%d | %.2g |" % (m, n, c["plain"], c["placebo"], c["form"], fe["plain"], fe["form"],
                 100 * sum(d) / n, ci[0], ci[1], w, lo, mc(w, lo)))
    res["pooled"] = {"wins": W, "losses": Lo, "p": mc(W, Lo)}
    L += ["", "Pooled over solvers (main test): form wins %d, loses %d against the placebo; exact McNemar p = %.2g." % (W, Lo, mc(W, Lo))]
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        S = res["solvers"]; fig, ax = plt.subplots(figsize=(4, 3.2))
        for m, x in S.items():
            fx = 100 * x["format_errors"]["plain"] / x["n"]; ax.errorbar(fx, x["gain_points"], yerr=[[x["gain_points"] - x["ci95"][0]], [x["ci95"][1] - x["gain_points"]]], fmt="o", capsize=3, color="#2a6fbb")
            ax.annotate(m, (fx, x["gain_points"]), textcoords="offset points", xytext=(6, 4), fontsize=8)
        ax.axhline(0, color="#999", lw=.8); ax.set_xlabel("plain: questions lost to output form (%)"); ax.set_ylabel("form - placebo (points)")
        fig.tight_layout(); fig.savefig(OUT + "/form_gain.png", dpi=200); plt.close(fig)
    except Exception as e: L.append("(plot failed: %s)" % e)
    json.dump(res, open(OUT + "/summary.json", "w"), indent=1); open(OUT + "/SUMMARY.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


# --- CAUSES of the remaining failures (2026-10-12): two independent labels per failure, then compare ------------------------------
CAUSES = ["column mapping", "value representation", "unstated convention", "output form", "wrong logic", "reference problem", "other"]
LABEL = """You classify why a text-to-SQL answer was scored wrong on BIRD. For each item you get the request (with BIRD's evidence), the
reference SQL, the model's SQL, and a short preview of both results. Pick the ONE main cause:
  column mapping        a different column or table for what the request names (e.g. name vs full_name, wrong table)
  value representation  the right column but the stored value written differently (case, code vs label, format, date form)
  unstated convention   a choice the request leaves open and the reference settles by habit: ties at a limit, counting rows vs
                        distinct entities, missing values kept or dropped, inner vs outer join, inclusive vs strict bounds, rounding
  output form           the same answer returned in a different form (extra or missing columns, order, duplicates)
  wrong logic           the model's SQL computes something the request does not ask for (wrong filter, wrong aggregate, missing step)
  reference problem     the reference itself looks wrong or does not follow the request and evidence
  other                 none of these
Also say whether the cause is LEARNABLE FROM TRAINING HISTORY: would seeing the same users' earlier requests and SQL (other
databases) likely fix it? yes | no.
Answer ONLY JSON: [{"id": "...", "cause": "...", "learnable": "yes|no", "why": "one sentence"}]

%s"""


def failures(model="sonnet", splits=("hold", "hold2"), n=20, rounds=1):
    """A seeded sample of `model`'s held-out failures under form (the method's remaining errors)."""
    F = []
    for sp in splits:
        for t in split(sp):
            f = "%s/%s.json" % (_out(sp, rounds, "form", model), t["id"])
            if os.path.exists(f):
                o = json.load(open(f))
                if "pass" in o and not o["pass"]: F.append((t, o))
    random.Random(SEED + 3).shuffle(F); return F[:n]


def label(model="sonnet", labelers=("opus", "gpt-6-sol"), n=20):
    from specbridge.comm.common.llm import ask_json
    F = failures(model, n=n); prev = lambda a: str(a)[:300]
    body = "\n\n".join("--- %s\nREQUEST: %s\nREFERENCE SQL: %s\nREFERENCE RESULT: %s\nMODEL SQL: %s\nMODEL RESULT: %s" % (t["id"], t["instruction"], t["reference_sql"],
                       prev(t["reference_answer"]), o.get("final"), prev(o.get("answer"))) for t, o in F)
    out = {}
    for lab in labelers:
        got = ask_json(LABEL % body, lab, brace="[") or []; out[lab] = {x["id"]: x for x in got if isinstance(x, dict) and "id" in x}
    ids = [t["id"] for t, _ in F]; agree = sum(out[labelers[0]].get(i, {}).get("cause") == out[labelers[1]].get(i, {}).get("cause") for i in ids)
    import collections
    L = ["# Causes of %s's remaining held-out failures under form (`libctx label`)\n" % model,
         "%d failures, seeded sample; two independent labelers (%s). Agreement on the cause: %d/%d.\n" % (len(ids), " and ".join(labelers), agree, len(ids)),
         "| cause | " + " | ".join(labelers) + " | both agree |", "|---|---|---|---|"]
    for c in CAUSES:
        L.append("| %s | %s | %d |" % (c, " | ".join(str(sum(out[l].get(i, {}).get("cause") == c for i in ids)) for l in labelers),
                 sum(all(out[l].get(i, {}).get("cause") == c for l in labelers) for i in ids)))
    L += ["", "Learnable from training history (yes): " + ", ".join("%s %d" % (l, sum(out[l].get(i, {}).get("learnable") == "yes" for i in ids)) for l in labelers), "",
          "| id | " + " | ".join(labelers) + " |", "|---|---|---|"]
    L += ["| %s | %s |" % (i, " | ".join("%s (%s): %s" % (out[l].get(i, {}).get("cause"), out[l].get(i, {}).get("learnable"), (out[l].get(i, {}).get("why") or "")[:140]) for l in labelers)) for i in ids]
    json.dump({"ids": ids, "labels": out}, open(OUT + "/causes_%s.json" % model, "w"), indent=1); open(OUT + "/CAUSES_%s.md" % model, "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, dft: a[a.index(k) + 1] if k in a else dft
    vals = {opt(k, None) for k in ("--model", "--split", "--rounds")}
    pos = [x for x in a[1:] if not x.startswith("--") and x not in vals]
    kw = dict(model=opt("--model", "haiku"), sp=opt("--split", "dev"), rounds=int(opt("--rounds", 1)))
    {"run": lambda: run(pos, **kw), "report": lambda: report(**kw), "summary": lambda: summary(), "label": lambda: label()}[a[0]]()
