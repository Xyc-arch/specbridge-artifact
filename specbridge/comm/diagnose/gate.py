"""STEP 5: the quality gate. An independent model judges each ungated record from the question, every reading with its SQL
and explicit V, database checks and the communication analysis; earlier verdicts hidden. Earlier judgments are kept.
  high -> eligible for retrieval | medium -> provisional | low -> excluded from ambiguity retrieval
    python -m specbridge.comm.diagnose.gate run | report"""
import collections, concurrent.futures as cf, json, os, sys
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json
from specbridge.comm.diagnose import LIB

GATE = """You are the quality gate for a library of real communication choices in text-to-SQL questions. For each RECORD judge ONE
claim: does it capture a genuine communication choice -- the question and evidence leave one decision open, and the stated
alternative readings are each supported by the text -- with the difference isolated to that decision and verified on the data?
  confidence  high:   the readings fit the text; the difference is isolated and verified; the analysis is consistent
              medium: plausible, but the wording, the evidence or an additional choice remains disputed
              low:    the evidence settles the choice, a reading is unsupported, or the difference is a gold or numerical defect
  category    meaning choice | output form | reference defect | uncertain
  reason      one or two sentences
  decisive    the phrase of the question/evidence, or the database fact, that decides your judgment (quote it)
Judge from the text, the SQL and the checks; the analysis is an earlier model's reading and may be wrong.
Answer ONLY JSON: [{"record": "<id>", "confidence": "...", "category": "...", "reason": "...", "decisive": "..."}]

%s"""


def key(r): return "%s:%s" % (r["source"].split("/")[-1], r["task"])


def checks(r, con):
    out, rs = [], {x["id"]: DB.rows(con, x["sql"]) for x in r["readings"]}
    a = rs.get("A")
    for x in r["readings"]:
        v = rs[x["id"]]
        if v is None: out.append("%s: does not run" % x["id"]); continue
        s = "%s: %d rows, sample %s" % (x["id"], len(v), str(v[:3])[:160])
        if x["id"] != "A" and a is not None:
            ca, cv = collections.Counter(map(repr, a)), collections.Counter(map(repr, v))
            s += "; rows only in A: %d, only in %s: %d; e.g. only-in-%s %s" % (sum((ca - cv).values()), x["id"], sum((cv - ca).values()), x["id"], str(list((cv - ca).elements())[:2])[:120])
        out.append(s)
    return out


def block(i, r):
    con = DB.connect(__import__("specbridge.comm.construct.freeze", fromlist=["snapshot"]).snapshot(r["database"])[0]); a = r.get("analysis") or {}   # snapshot for any benchmark (was BIRD-only)
    s = ["--- RECORD %s  (database %s)" % (i, r["database"]), "ORIGINAL QUESTION + EVIDENCE: %s" % r["original"], "DECISION (as recorded): %s" % r["decision"]]
    for x in r["readings"]:
        s.append("READING %s%s: %s\n  SQL: %s\n  EXPLICIT: %s" % (x["id"], " (the gold)" if x["id"] == "A" else "", x["reading"], x["sql"],
                 (DB.explicit(x["sql"], r["database"], conventions=False) or "(not renderable)")[:900]))
    s.append("DATABASE CHECKS: " + " | ".join(checks(r, con)))
    if a:
        s.append("EARLIER ANALYSIS -- requirements: " + "; ".join("[%s] %s" % (q["real"], q["requirement"]) for q in a.get("requirements", [])))
        s.append("EARLIER ANALYSIS -- open phrase: \"%s\"; why both: %s" % ((a.get("choice") or {}).get("open_phrase"), (a.get("choice") or {}).get("why_both")))
    return "\n".join(s)


def run():
    ALL = [json.loads(l) for l in open(LIB + "/library.jsonl")]; R = [r for r in ALL if not r.get("gate")]
    blocks = {key(r): block(key(r), r) for r in R}; ks = list(blocks)
    def one(b): return ask_json(GATE % "\n\n".join(blocks[k] for k in b), "opus", brace="[") or [{"record": k, "confidence": "UNPARSED"} for k in b]
    with cf.ThreadPoolExecutor(max_workers=6) as ex: got = [x for r in ex.map(one, [ks[i:i + 4] for i in range(0, len(ks), 4)]) for x in r]
    prev = json.load(open(LIB + "/gate.json")) if os.path.exists(LIB + "/gate.json") else []
    json.dump(prev + got, open(LIB + "/gate.json", "w"), indent=1); G = {g["record"]: g for g in got}
    with open(LIB + "/library.jsonl", "w") as f:
        for r in ALL:
            g = G.get(key(r))
            if not r.get("gate") and g:
                r["gate"] = {"version": "gate-1", **{k: g.get(k) for k in ("confidence", "category", "reason", "decisive")},
                             "retrieval": {"high": "eligible", "medium": "provisional"}.get(g.get("confidence"), "excluded")}
            f.write(json.dumps(r, default=str) + "\n")
    report()


def report():
    R = [json.loads(l) for l in open(LIB + "/library.jsonl")]; c = collections.Counter(((r.get("gate") or {}).get("confidence"), (r.get("gate") or {}).get("category")) for r in R)
    L = ["# Quality gate over %d library records\n" % len(R), "| confidence | meaning choice | output form | reference defect | uncertain |", "|---|---|---|---|---|"]
    L += ["| %s | %d | %d | %d | %d |" % (k, c[(k, "meaning choice")], c[(k, "output form")], c[(k, "reference defect")], c[(k, "uncertain")]) for k in ("high", "medium", "low")]
    open(LIB + "/GATE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
