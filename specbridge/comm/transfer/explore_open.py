"""DOES EXPLORING THE DATABASE HELP A MODEL REPORT AN OPEN CHOICE? (2026-10-28; reviewer-style comment on Sec. 5)
The 204 accepted request sets, open request only, Sonnet and GPT-Sol: the paper's explanation call (disclose.INSTRUCTION, SQLite named
as in the dialect rerun), but before answering the model may run up to 5 read-only queries per round for up to 6 rounds and sees 20 rows
of each result (the solver's budget, common.solve). Scored as the single call: the main query and each alternative executed; both
returned when they include interpretation A and interpretation B. Paired with the single call on the same set (McNemar).
    python -m specbridge.comm.transfer.explore_open run | report"""
import collections, concurrent.futures as cf, json, math, os, re, sys
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X, dialect_rerun as DR

D = "out/transfer/all/render"; OUT = "out/transfer/explore_open"; MODELS = ("sonnet", "gpt-6-sol"); ROUNDS = 6
EXPLORE = """

Before you answer, you may explore the database. To explore, reply with up to 5 lines, each
  QUERY: <one SQLite SELECT statement>
and nothing else; you will see up to 20 rows of each result. You have at most %d rounds; in the last one you must answer.
When you are ready, answer ONLY with the JSON object described above."""


def _cases():
    from specbridge.comm.transfer import reviewed as RV
    C = {c["case"]: c for c in json.load(open(D + "/eval/frozen.json"))["cases"]}; W = json.load(open(D + "/written.json"))
    return [C[k] for k in RV.accepted(list(C))], W


def _f(m, k): return "%s/%s/%s.json" % (OUT, m, k.replace(":", "__").replace("/", "_"))


def run(workers=6):
    from specbridge.pd.ask import ask
    from specbridge.comm.common.llm import parse as jparse
    cases, W = _cases()
    def one(j):
        m, c = j; f = _f(m, c["case"])
        if os.path.exists(f): return
        schema, docs = DB.context(c); con = DB.connect(c["snapshot"])
        base = X.INSTRUCTION.replace(DR.OLD, DR.NEW) % (schema, docs, W[c["case"]]["open"]) + EXPLORE % ROUNDS
        conv, calls, resp, queries = "", 0, None, 0
        for r in range(1, ROUNDS + 1):
            t = ask(base + conv + ("\n\n(Round %d of %d%s.)" % (r, ROUNDS, "; LAST round: answer now with the JSON" if r == ROUNDS else "")), m, timeout=1500, quiet=True) or ""
            calls += 1
            if not t.strip(): return                                    # a failed call is not an answer: rerun asks again
            qs = [x.strip().rstrip(";") for x in re.findall(r"(?m)^\s*QUERY\s*:\s*(.+)$", t)][:5]
            js = jparse(t, "{")
            if isinstance(js, dict) and "sql" in js and not qs: resp = js; break
            if not qs: resp = js if isinstance(js, dict) else {"sql": None}; break
            out = []
            for n, q in enumerate(qs, 1):
                stt, res, cols = DB.execute(con, q, ms=5000); queries += 1
                shown = ("columns %s\n" % cols + "\n".join(str(x) for x in res[:20]) + ("\n... (%d rows)" % len(res) if len(res) > 20 else "")) if stt == "ok" else "ERROR: %s" % res
                out.append("QUERY %d: %s\nRESULT %d:\n%s" % (n, q, n, shown[:2500]))
            conv += "\n\n-- your round %d --\n%s" % (r, "\n\n".join(out))
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"case": c["case"], "model": m, "response": resp, "rounds": r, "explore_queries": queries, "calls": calls}, open(f, "w"), indent=1, default=str)
    jobs = [(m, c) for c in cases for m in MODELS]
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report()


def _both(c, resp):
    con = DB.connect(c["snapshot"]); r = resp or {}
    qs = [r.get("sql")] + [x.get("sql") for x in (r.get("alternatives") or []) if isinstance(x, dict)]
    got = set()
    for q in [q for q in qs if q]:
        rows = DB.rows(con, q)
        if rows is not None: got |= set(X._match(c, rows))
    return {"A", "B"} <= got


def _single(m, c):
    """The paper's single explanation call for this set (the SQLite-named rerun for the four LiveSQLBench databases)."""
    name = "%s__open.json" % c["case"].replace(":", "__").replace("/", "_")
    for d in ((D + "/disclose_sqlite/%s/" % m) if c.get("database") in DR.LIVE else None, D + "/disclose/%s/" % m):
        if d and os.path.exists(d + name): return json.load(open(d + name)).get("response")
    return None


def report():
    cases, _W = _cases(); res = {}
    for m in MODELS:
        e, s = [], []
        for c in cases:
            f = _f(m, c["case"])
            if not os.path.exists(f): continue
            o = json.load(open(f)); e.append(int(_both(c, o["response"]))); s.append(int(_both(c, _single(m, c))))
        b = sum(x and not y for x, y in zip(e, s)); cc = sum(y and not x for x, y in zip(e, s)); n = b + cc
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, cc) + 1)) / 2 ** n) if n else 1.0
        rounds = [json.load(open(_f(m, c["case"])))["rounds"] for c in cases if os.path.exists(_f(m, c["case"]))]
        res[m] = {"sets": len(e), "both_explore": sum(e), "both_single": sum(s), "explore_only": b, "single_only": cc, "p": round(p, 4),
                  "explored": sum(1 for x in rounds if x > 1)}
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(OUT + "/results.json", "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
