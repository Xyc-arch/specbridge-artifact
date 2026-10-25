"""IN-CONTEXT CHOICE CHECKLIST vs A PLACEBO CHECKLIST (2026-10-12). The disclosure call (disclose.INSTRUCTION: same schema,
documentation, request and JSON answer) with one block added before the schema: either a checklist of the computational choices
that requests often leave open (CHECK; types from the interpretation library, no example, no target SQL), or a checklist of the
same length and the same procedure about SQL writing style only (PLACEBO). The two arms are interleaved in one run, so the only
difference is the content of the block. Scoring by execution only, as in disclose:
    open request     both readings returned (primary or an alternative)
    specific request primary returns the specified reading; an alternative returns the other reading (a false open claim)
    python -m specbridge.comm.transfer.checklist run [<model> ...]   -> <disclose>/incontext/<arm>/<model>/<case>__<wording>.json
    python -m specbridge.comm.transfer.checklist report               -> <disclose>/incontext/RESULTS.md, results.json
The sample is nested (seeded order, first N), so a larger N keeps every earlier answer. At most 6 workers (machine rule)."""
import concurrent.futures as cf, json, math, os, random, sys, time
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X

SOURCE = {**{d: "BIRD" for d in ("financial", "student_club", "thrombosis_prediction", "formula_1")},
          **{d: "Spider" for d in ("baseball_1", "sakila_1", "customers_and_invoices", "chinook_1")},
          **{d: "LiveSQLBench" for d in ("archeology", "insider", "crypto", "alien")}}       # the benchmark each database comes from
D = "out/transfer/eval12-v2/render"; MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]; N, SEED, B = 100, 20261013, 4000

CHECK = """CHECKLIST BEFORE YOU ANSWER. Requests for calculations often leave one of the following choices open. Go through each item
and decide whether the request and the documentation settle it:
- Level of aggregation: an average of per-row values (such as an average of ratios) or a ratio of totals; an average over records or over entities.
- Unit counted: rows or distinct entities; rows that a join repeats.
- Missing values and missing matches: rows or groups with NULL or with no matching row kept (as zero or as their own group) or dropped; codes that stand for unknown.
- Ties at a limit: when a top-k or highest-value request has ties at the cutoff, exactly k rows or every tied row.
- Signed or absolute amounts: whether negative values (refunds, losses, decreases) count with their sign or by their size.
- Relationship role: which of several links between two tables gives the attribute.
- Baseline and population: what the comparison value or the denominator is computed over.
- Boundaries and time scope: inclusive or strict limits; which period is meant.
For each item that the request does not settle and that changes the answer on this database, use one reading in your primary SQL,
mark that assumption unresolved, and give the other reading with its SQL as an alternative. If the request settles an item, follow it."""

PLACEBO = """CHECKLIST BEFORE YOU ANSWER. Requests often leave the writing style of the query open. Go through each item and decide
whether the request and the documentation settle it:
- Keyword case: SQL keywords such as SELECT, FROM, WHERE, GROUP BY and ORDER BY in upper case; names as they appear in the schema.
- Aliases: a short alias of one to three letters for each table in a join, used for every column taken from that table.
- Join syntax: explicit JOIN ... ON syntax, not a comma-separated list of tables with the condition in WHERE.
- Layout: each major clause (SELECT, FROM, each JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT) on its own line.
- Endings and comments: no semicolon at the end of the query and no comments inside it.
- Quotes: single quotes for text values; double quotes only for names that contain spaces or symbols.
- Spacing: one space on each side of operators such as =, <, > and +, and after each comma in a list.
- Subqueries: indented, each with a short alias that says what it holds.
- Line length: at most 100 characters on a line, with each break after a comma or before a keyword.
For each item that the request does not settle, write the query in the style above, and keep the query as short as it can be
while it still answers the request in full. If the request settles an item, follow it."""

ARMS = {"check": CHECK, "placebo": PLACEBO}


def prompt(arm):
    head, tail = X.INSTRUCTION.split("\n\nDATABASE SCHEMA:", 1)
    return head + "\n\n" + ARMS[arm].replace("%", "%%") + "\n\nDATABASE SCHEMA:" + tail


def subset(n=N):
    _fz, _wr, out = X._paths(D); ks = sorted(json.load(open(out + "/sample.json"))["cases"])
    random.Random(SEED).shuffle(ks); return sorted(ks[:n])


def _f(out, arm, m, k, w): return "%s/incontext/%s/%s/%s__%s.json" % (out, arm, m, k.replace(":", "__").replace("/", "_"), w)


def run(models, n=N, workers=6):
    from specbridge.comm.common.llm import call, parse
    fz, wr, out = X._paths(D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr))
    S = json.load(open(out + "/sample.json")); P = {a: prompt(a) for a in ARMS}
    def one(job):
        k, w, m, arm = job; f = _f(out, arm, m, k, w)
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); con = DB.connect(c["snapshot"]); t0 = time.time()
        txt = call(P[arm] % (schema, docs, W[k][w]), m)
        if not (txt or "").strip(): return                      # a failed call is not an answer: not saved, asked again on rerun
        r = parse(txt, "{") or {}; prim = r.get("sql"); a = DB.rows(con, prim) if prim else None; alts = []
        for x in (r.get("alternatives") or [])[:2]:
            if isinstance(x, dict) and x.get("sql"):
                b = DB.rows(con, x["sql"]); alts.append({"interpretation": x.get("interpretation"), "sql": x["sql"], "executes": b is not None, "matches": X._match(c, b)})
        o = {"case": k, "wording": w, "model": m, "arm": arm, "response": r, "raw": None if r else txt, "primary_executes": a is not None,
             "primary_matches": X._match(c, a), "alternatives": alts, "seconds": round(time.time() - t0, 1), "chars_out": len(txt)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    ks = subset(n); random.Random(SEED + 1).shuffle(ks)         # SET BY SET: every pair completes early, so the report is
    jobs = [(k, w, m, a) for k in ks for w in S["wordings"][k] for m in models for a in ARMS]     # auditable at any point;
    per = len(jobs) // len(ks)                                  # both arms of one request run side by side (same time, same load)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex:
        for i, _ in enumerate(ex.map(one, jobs), 1):
            if i % (5 * per) == 0: report(n, quiet=True); print("sets %d/%d, report updated" % (i // per, len(ks)), flush=True)
    report(n, quiet=True); open(out + "/incontext/run.done", "w").write("ok\n")


def _score(o):
    got = set(o["primary_matches"]) | {x for a in o["alternatives"] for x in a["matches"]}
    if o["wording"] == "open": return {"cover": {"A", "B"} <= got}
    w = o["wording"][-1]; other = "B" if w == "A" else "A"
    return {"right": w in o["primary_matches"], "false_alt": any(other in a["matches"] for a in o["alternatives"])}


def _mcnemar(b, c):
    """Exact two-sided McNemar p from the discordant pairs (b: check only, c: placebo only)."""
    n = b + c
    if n == 0: return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / 2 ** n)


def report(n=N, quiet=False):
    fz, _wr, out = X._paths(D); S = json.load(open(out + "/sample.json")); ks = subset(n); res = {"n_sets": n, "models": {}}
    base = lambda m, k, w: "%s/%s/%s__%s.json" % (out, m, k.replace(":", "__").replace("/", "_"), w)
    L = ["# In-context choice checklist vs placebo checklist (`specbridge.comm.transfer.checklist`)\n",
         "%d request sets (seed %d). Same disclosure call; one block before the schema: the choice checklist or a same-length style "
         "checklist. Sets with all arms saved. `none` = the earlier disclosure run without a block (different day; reference only). "
         "p: exact McNemar, check vs placebo.\n" % (n, SEED),
         "| solver | sets | open, both readings: none | placebo | check | check-only / placebo-only | p | specific right: placebo | check | false alternative on specific: placebo | check |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    pool = []
    for m in MODELS:
        rows = []
        for k in ks:
            ws = S["wordings"][k]; fs = {(a, w): _f(out, a, m, k, w) for a in ARMS for w in ws}
            if not all(os.path.exists(f) for f in fs.values()): continue
            g = {aw: _score(json.load(open(f))) for aw, f in fs.items()}; p = [w for w in ws if w != "open"][0]
            nb = _score(json.load(open(base(m, k, "open"))))["cover"] if os.path.exists(base(m, k, "open")) else None
            rows.append({"case": k, "none": nb, "placebo": g[("placebo", "open")]["cover"], "check": g[("check", "open")]["cover"],
                         "right_placebo": g[("placebo", p)]["right"], "right_check": g[("check", p)]["right"],
                         "false_placebo": g[("placebo", p)]["false_alt"], "false_check": g[("check", p)]["false_alt"]})
        c = lambda key: sum(bool(r[key]) for r in rows); b1 = sum(r["check"] and not r["placebo"] for r in rows); c1 = sum(r["placebo"] and not r["check"] for r in rows)
        pv = _mcnemar(b1, c1); pool += [(int(r["check"]) - int(r["placebo"])) for r in rows]
        res["models"][m] = {"n": len(rows), **{key: c(key) for key in ("none", "placebo", "check", "right_placebo", "right_check", "false_placebo", "false_check")},
                            "check_only": b1, "placebo_only": c1, "p": pv, "rows": rows}
        L.append("| %s | %d | %d | %d | %d | %d / %d | %.3g | %d | %d | %d | %d |" % (m, len(rows), c("none"), c("placebo"), c("check"), b1, c1, pv,
                 c("right_placebo"), c("right_check"), c("false_placebo"), c("false_check")))
    def flip(diffs):                                            # mean paired difference, sign-flip test over sets x solvers
        rng = random.Random(SEED); obs = sum(diffs) / len(diffs)
        null = [sum(d * rng.choice((-1, 1)) for d in diffs) / len(diffs) for _ in range(B)]
        return {"pairs": len(diffs), "mean_diff": obs, "p": (1 + sum(abs(x) >= abs(obs) for x in null)) / (B + 1)}
    if pool:
        res["pooled"] = flip(pool)
        L += ["", "Pooled over solvers: %d pairs, check - placebo = %+.1f points of open requests with both readings, sign-flip p = %.4f."
              % (len(pool), 100 * res["pooled"]["mean_diff"], res["pooled"]["p"])]
        db = {c["case"]: c["database"] for c in json.load(open(fz))["cases"]}; res["by_source"] = {}
        L += ["", "| source | sets | " + " | ".join("%s placebo -> check (p)" % m for m in MODELS) + " | pooled | specific right, placebo -> check |",
              "|---|---|" + "---|" * (len(MODELS) + 2)]
        for src in ("BIRD", "Spider", "LiveSQLBench"):
            o = {"models": {}}; diffs = []; cells = []
            for m in MODELS:
                rs = [r for r in res["models"][m]["rows"] if SOURCE[db[r["case"]]] == src]
                b1, c1 = sum(r["check"] and not r["placebo"] for r in rs), sum(r["placebo"] and not r["check"] for r in rs)
                o["models"][m] = {"n": len(rs), "placebo": sum(r["placebo"] for r in rs), "check": sum(r["check"] for r in rs), "check_only": b1,
                                  "placebo_only": c1, "p": _mcnemar(b1, c1), "right_placebo": sum(r["right_placebo"] for r in rs), "right_check": sum(r["right_check"] for r in rs)}
                diffs += [int(r["check"]) - int(r["placebo"]) for r in rs]; x = o["models"][m]; cells.append("%d -> %d (%.2g)" % (x["placebo"], x["check"], x["p"]))
            o["pooled"] = flip(diffs); res["by_source"][src] = o; X_ = o["models"].values()
            L.append("| %s | %d | %s | %+.1f (p %.4f) | %d -> %d |" % (src, len(diffs) // len(MODELS), " | ".join(cells), 100 * o["pooled"]["mean_diff"], o["pooled"]["p"],
                     sum(x["right_placebo"] for x in X_), sum(x["right_check"] for x in X_)))
    os.makedirs(out + "/incontext", exist_ok=True)
    json.dump(res, open(out + "/incontext/results.json", "w"), indent=1); open(out + "/incontext/RESULTS.md", "w").write("\n".join(L) + "\n")
    if not quiet: print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]; n = int(a[a.index("--n") + 1]) if "--n" in a else N; ms = [x for x in a[1:] if not x.startswith("--") and not x.isdigit()] or MODELS
    {"run": lambda: run(ms, n), "report": lambda: report(n)}[a[0]]()
