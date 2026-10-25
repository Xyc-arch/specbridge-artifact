"""ASSUMPTION LEDGER, SINGLE PASS + CODE (2026-10-12 pilot, Sonnet). One call returns the final SQL as CTEs s1, s2, ... and a
ledger: one line per decision point, tagged to a step, with the reading taken, its RULE SIDE (specbridge.comm.diagnose.rules), its
evidence (a quoted request phrase, a document line, a data claim, or none) and settled/open. The ledger replaces free reasoning.
Then CODE ONLY -- the schema and long context are never sent again:
    tier 0  every rule site in the SQL agrees with its ledger side and every data claim holds          -> done
    tier 1  ledger and SQL disagree on a rule construct                                                 -> apply the rule edit (SQL follows the ledger)
    tier 2  a data claim fails when queried                                                             -> mark open; the other reading by edit
    tier 3  a rule site in the SQL has no ledger entry                                                  -> mark open; the other reading by edit
    tier 4  an open / failed item no rule edit can build                                                -> counted only (would be one small call)
Answer = main SQL + the alternatives built for OPEN items (at most 2). Data: 30 request sets (open + one specific wording, scored
as in disclose: both readings; a false alternative on the specific wording) and the 30 Spider 2.0 pilot tasks (rgv.pick; official
comparison). Baselines are the saved answers of the same calls without a ledger (disclose explanation call; rgv plain, sample3).
Size: characters in / out per call (about 4 characters per token).
    python -m specbridge.comm.transfer.ledger run      -> out/ledger/<set|spider2>/<id>.json
    python -m specbridge.comm.transfer.ledger report   -> out/ledger/RESULTS.md"""
import collections, concurrent.futures as cf, json, os, random, sqlite3, sys, time
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X, spider2 as S, rgv as RG, combined as CB
from specbridge.comm.diagnose import rules as RU

OUT = "out/ledger"; D = CB.D; SEED, N_SETS, MODEL = 20261020, 30, "sonnet"
SIDES = "rows | entities | drop_unmatched | keep_unmatched | cut | all_ties | unfiltered | filtered | integer | real | strict | inclusive | other"
RULE_OF = {"rows": "count_unit", "entities": "count_unit", "drop_unmatched": "join_kind", "keep_unmatched": "join_kind", "cut": "ties",
           "all_ties": "ties", "unfiltered": "null_filter", "filtered": "null_filter", "integer": "division", "real": "division",
           "strict": "boundary", "inclusive": "boundary"}

LEDGER = """Answer the request with SQL for the database below. Write the final query as named steps: a WITH clause whose CTEs are
s1, s2, ... and a final SELECT from them. Instead of free-form reasoning, keep an ASSUMPTION LEDGER: one entry for every decision
point in your query -- what is counted (rows or distinct entities), whether unmatched rows are kept, ties at a limit, missing values,
the aggregation level, boundaries, and any formula or weighting. For each entry give the step it governs, the reading you took, its
side from this list (%s), the evidence, and whether the request settles it. Evidence is one of: a phrase quoted from the request; a
line quoted from the documentation; a data claim {"column": "table.column", "fact": "has_null|no_null|repeats|unique"} that you
expect to hold in the data; or none. If an entry is not settled, give the other reading's full SQL as an alternative.

DATABASE SCHEMA:
%%s

DATABASE DOCUMENTATION:
%%s

REQUEST:
%%s

Answer ONLY JSON: {"sql": "WITH s1 AS (...), s2 AS (...) SELECT ...", "ledger": [{"step": "s2", "decision": "...", "reading": "...",
"side": "...", "evidence": {"kind": "quote|doc|data|none", "text": "...", "data": {"column": "...", "fact": "..."}}, "status": "settled|open",
"alternative_sql": "only when open"}]}""" % SIDES


# --- the code tiers ------------------------------------------------------------------------------------------------------------
def _claim_holds(con, d):
    try:
        t, c = d["column"].split(".", 1); q = lambda x: '"%s"' % x.strip('"`[] ')
        if d["fact"] in ("has_null", "no_null"):
            n = con.execute("SELECT COUNT(*) FROM %s WHERE %s IS NULL" % (q(t), q(c))).fetchone()[0]; return (n > 0) == (d["fact"] == "has_null")
        if d["fact"] in ("repeats", "unique"):
            n = con.execute("SELECT COUNT(*) FROM (SELECT %s FROM %s WHERE %s IS NOT NULL GROUP BY %s HAVING COUNT(*) > 1)" % (q(c), q(t), q(c), q(c))).fetchone()[0]
            return (n > 0) == (d["fact"] == "repeats")
    except Exception: return None
    return None


def tiers(sql, ledger, dbpath):
    """Apply tiers 0-3 by code. Returns (main SQL, [alternative SQL], tier record)."""
    rec = collections.Counter(); main = sql; alts = []; con = sqlite3.connect("file:%s?mode=ro" % dbpath, uri=True)
    led = [e for e in (ledger or []) if isinstance(e, dict)]
    want = collections.defaultdict(set)
    for e in led:
        if e.get("side") in RULE_OF: want[RULE_OF[e["side"]]].add(e["side"])
        ev = e.get("evidence") or {}
        if isinstance(ev, dict) and ev.get("kind") == "data" and isinstance(ev.get("data"), dict):
            h = _claim_holds(con, ev["data"])
            if h is False: rec["tier2_claim_failed"] += 1; e["status"] = "open"; e["_claim_failed"] = True
            elif h is True: rec["claims_hold"] += 1
            else: rec["claims_uncheckable"] += 1
    con.close()
    for _ in range(4):                                                           # tier 1: SQL follows the ledger (re-detect after each edit)
        fixed = False
        for st in RU.sites(main):
            rule, side, _i = st
            if rule in want and side not in want[rule] and len(want[rule]) == 1:
                e = RU.edit(main, st)
                if e: main = e; rec["tier1_edit"] += 1; fixed = True; break
        if not fixed: break
    seen = {RULE_OF[e["side"]] for e in led if e.get("side") in RULE_OF}
    opened = []
    for st in RU.sites(main):                                                   # tier 3: a rule site the ledger does not mention
        if st[0] != "dedup" and st[0] not in seen: opened.append(st); rec["tier3_unledgered"] += 1
    for e in led:                                                               # open entries (model's or tier 2): alternative by edit
        if e.get("status") != "open": continue
        r = RULE_OF.get(e.get("side")); st = next((x for x in RU.sites(main) if x[0] == r), None) if r else None
        if st: opened.append(st)
        elif e.get("alternative_sql"): alts.append(e["alternative_sql"]); rec["model_alternative"] += 1
        else: rec["tier4_needed"] += 1
    for st in opened:
        a = RU.edit(main, st)
        if a and a != main and a not in alts: alts.append(a)
    rec["tier0_clean"] = int(not any(rec[k] for k in ("tier1_edit", "tier2_claim_failed", "tier3_unledgered", "tier4_needed")))
    return main, alts[:2], dict(rec)


# --- run ----------------------------------------------------------------------------------------------------------------------
def sets():
    """The 30 development sets, drawn from the first construction run; wordings for the whole combined collection."""
    S0 = json.load(open(X._paths(CB.PARTS[0])[2] + "/sample.json")); ks = sorted(S0["cases"]); random.Random(SEED).shuffle(ks)
    return ks[:N_SETS], json.load(open(X._paths(D)[2] + "/sample.json"))["wordings"]


def _f(kind, key): return "%s/%s/%s.json" % (OUT, kind, key.replace(":", "__").replace("/", "_"))


def run(workers=6):
    from specbridge.comm.common.llm import call, parse
    fz, wr, _o = X._paths(D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr)); ks, WD = sets()
    T = S.tasks(); ids = RG.pick()[0]; E = {json.loads(l)["instance_id"]: json.loads(l) for l in open(S.GOLD + "/spider2lite_eval.jsonl")}; ctx = {}
    for i in ids: ctx.setdefault(T[i]["db"], S.context(T[i]["db"]))
    jobs = [("set", k, w) for k in ks for w in WD[k]] + [("spider2", i, None) for i in ids]; random.Random(SEED).shuffle(jobs)
    def one(job):
        kind, k, w = job; f = _f(kind, k + ("__" + w if w else ""))
        if os.path.exists(f): return
        if kind == "set":
            c = C[k]; schema, docs = DB.context(c); prompt = LEDGER % (schema, docs, W[k][w]); dbpath = c["snapshot"]
        else:
            t = T[k]; prompt = LEDGER % (ctx[t["db"]], S.docs(t), t["question"]); dbpath = "%s/%s.sqlite" % (S.DBDIR, t["db"])
        t0 = time.time(); txt = call(prompt, MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; sql = r.get("sql") or ""
        main, alts, rec = tiers(sql, r.get("ledger"), dbpath) if sql else (sql, [], {"no_sql": 1})
        raw_alts = [e.get("alternative_sql") for e in (r.get("ledger") or []) if isinstance(e, dict) and e.get("alternative_sql")][:2]
        def score(q):
            if kind == "set": return X._match(C[k], DB.rows(DB.connect(dbpath), q)) if q else []
            G, io = S.golds(k, E); return S.matches(S.run_sql(T[k]["db"], q), G, io) if q else []
        o = {"kind": kind, "key": k, "wording": w, "chars_in": len(prompt), "chars_out": len(txt), "seconds": round(time.time() - t0, 1), "tiers": rec,
             "ledger": r.get("ledger"), "sql_first_pass": sql, "first_pass": {"main": score(sql), "alts": [score(a) for a in raw_alts]},
             "after_code": {"main_sql": main, "main": score(main), "alts_sql": alts, "alts": [score(a) for a in alts]}}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report()


def report():
    fz, wr, out = X._paths(D); ks, WD = sets(); L = ["# Assumption ledger, single pass + code (`specbridge.comm.transfer.ledger`), Sonnet\n"]
    base = lambda k, w: "%s/%s/%s__%s.json" % (out, MODEL, k.replace(":", "__").replace("/", "_"), w)
    rows = []
    for k in ks:
        for w in WD[k]:
            f = _f("set", k + "__" + w); b = base(k, w)
            if not (os.path.exists(f) and os.path.exists(b)): continue
            o = json.load(open(f)); B = json.load(open(b)); rows.append((k, w, o, B))
    def cov(main, alts): return {"A", "B"} <= set(main) | {x for a in alts for x in a}
    def fa(w, alts): other = "B" if w.endswith("A") else "A"; return any(other in a for a in alts)
    O = [r for r in rows if r[1] == "open"]; P = [r for r in rows if r[1] != "open"]
    L += ["## Request sets (%d open, %d specific wordings)\n" % (len(O), len(P)), "| arm | open: both readings | specific: main right | specific: false alternative | chars in / out per call |", "|---|---|---|---|---|"]
    Cc = {c["case"]: c for c in json.load(open(fz))["cases"]}; Ww = json.load(open(wr))
    L.append("| explanation call (saved baseline) | %d/%d | %d/%d | %d | %d / %d |" % (sum(cov(r[3]["primary_matches"], [a["matches"] for a in r[3]["alternatives"]]) for r in O), len(O),
             sum(r[1][-1] in r[3]["primary_matches"] for r in P), len(P), sum(fa(r[1], [a["matches"] for a in r[3]["alternatives"]]) for r in P),
             sum(len(X.INSTRUCTION % (*DB.context(Cc[r[0]]), Ww[r[0]][r[1]])) for r in rows) / max(1, len(rows)), sum(r[3].get("chars_out", 0) for r in rows) / max(1, len(rows))))
    for lab, key in (("ledger, first pass", "first_pass"), ("ledger + code tiers", "after_code")):
        L.append("| %s | %d/%d | %d/%d | %d | %d / %d |" % (lab, sum(cov(r[2][key]["main"], r[2][key]["alts"]) for r in O), len(O), sum(r[1][-1] in r[2][key]["main"] for r in P), len(P),
                 sum(fa(r[1], r[2][key]["alts"]) for r in P), sum(r[2]["chars_in"] for r in rows) / max(1, len(rows)), sum(r[2]["chars_out"] for r in rows) / max(1, len(rows))))
    # Spider 2.0
    ids = RG.pick()[0]; R2 = []
    for i in ids:
        f = _f("spider2", i); p = RG._f("plain", MODEL, i); s3 = [RG._f("sample3", MODEL, i, k) for k in range(3)]
        if os.path.exists(f) and os.path.exists(p) and all(os.path.exists(x) for x in s3): R2.append((i, json.load(open(f)), json.load(open(p)), [json.load(open(x)) for x in s3]))
    L += ["", "## Spider 2.0 pilot tasks (%d)\n" % len(R2), "| arm | main correct | answer set | answers per task |", "|---|---|---|---|"]
    an = lambda A: (bool(A and A[0]["matches"]), bool(any(a["matches"] for a in A)), len(A))
    rows2 = {"plain explanation call (saved)": [an(r[2]["answers"]) for r in R2],
             "sample-3, SQL only (saved)": [(bool(r[3][0]["answers"] and r[3][0]["answers"][0]["matches"]), any(x["answers"] and x["answers"][0]["matches"] for x in r[3]), 3) for r in R2],
             "ledger, first pass": [(bool(r[1]["first_pass"]["main"]), bool(r[1]["first_pass"]["main"] or any(r[1]["first_pass"]["alts"])), 1 + len(r[1]["first_pass"]["alts"])) for r in R2],
             "ledger + code tiers": [(bool(r[1]["after_code"]["main"]), bool(r[1]["after_code"]["main"] or any(r[1]["after_code"]["alts"])), 1 + len(r[1]["after_code"]["alts"])) for r in R2]}
    for lab, v in rows2.items(): L.append("| %s | %d | %d | %.2f |" % (lab, sum(x[0] for x in v), sum(x[1] for x in v), sum(x[2] for x in v) / max(1, len(v))))
    allr = [r[2] for r in rows] + [r[1] for r in R2]; T = collections.Counter()
    for o in allr:
        for kk, v in o["tiers"].items(): T[kk] += v
    L += ["", "## Code tiers over all %d ledger calls\n" % len(allr), "- " + ", ".join("%s %d" % kv for kv in sorted(T.items())),
          "- calls ending at tier 0: %d of %d" % (sum(o["tiers"].get("tier0_clean", 0) for o in allr), len(allr)),
          "- Spider 2.0 chars in / out per ledger call: %d / %d" % (sum(r[1]["chars_in"] for r in R2) / max(1, len(R2)), sum(r[1]["chars_out"] for r in R2) / max(1, len(R2)))]
    os.makedirs(OUT, exist_ok=True); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
