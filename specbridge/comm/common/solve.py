"""THE SOLVER: an agent answers questions over one read-only database, batched -- one sealed call serves up to `bsize`
questions of ONE database; each question has up to `rounds` rounds of at most 5 exploration queries (20 result rows shown)
before a FINAL query. Every question is written to its own file as soon as its batch finishes, so a rerun resumes.
The caller decides what shares a batch (e.g. never two versions of the same task)."""
import collections, concurrent.futures as cf, json, os, re
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import call

HEAD = """You are a data analyst with read-only access to one SQLite database. You are working on SEVERAL independent
questions about it at once; treat each separately.
For EVERY open question below, write a section that starts with a line "### <question id>" and then EITHER up to 5 exploration
queries, each on its own line:
  QUERY: <one SQLite SELECT statement>
OR exactly one answer:
  FINAL: <one SQLite SELECT statement>    -- the rows it returns are your answer to that question
You see up to 20 rows of each query's result. Each question has at most %d rounds; in its last round it must be FINAL.

DATABASE SCHEMA:
%s

DATABASE DOCUMENTATION (as the database ships it):
%s
"""


def clean(q):
    """The SQL of a QUERY/FINAL line: fences and wrapping backticks removed, only up to the first blank line (explanations are not SQL)."""
    q = re.sub(r"^```(sql)?|```$", "", q.strip(), flags=re.M).strip()
    q = re.sub(r"^`+|`+$", "", q).strip()             # 2026-10-01: a query wrapped in single backticks (inline code) is SQL too
    return re.split(r"\n\s*\n", q, 1)[0].strip().rstrip(";")


def solve(items, model, outdir, bsize=8, rounds=6, group=lambda it: None, workers=6):
    """items: [{"key", "text", "snapshot", "database", ...}]. Writes <outdir>/<key>.json = {"key", "final", "turns",
    "executes", "rows_answer", "answer"} and returns {key: record}. `group` puts items in separate batches."""
    os.makedirs(outdir, exist_ok=True)
    path = lambda k: "%s/%s.json" % (outdir, re.sub(r"[^\w.-]", "_", k))
    todo = collections.defaultdict(list)
    for it in items:
        if not os.path.exists(path(it["key"])): todo[(it["database"], group(it))].append(it)
    jobs = [v[i:i + bsize] for v in todo.values() for i in range(0, len(v), bsize)]
    def one(job):
        con = DB.connect(job[0]["snapshot"]); head = HEAD % (rounds, DB.schema(job[0]["snapshot"]), DB.docs(job[0]["database"]))
        st = {"t%03d" % i: {"it": it, "conv": "", "round": 0, "final": None} for i, it in enumerate(job)}
        while True:
            op = [(q, s) for q, s in st.items() if s["final"] is None and s["round"] < rounds]
            if not op: break
            body = "".join("\n\n==================== QUESTION %s (round %d of %d%s)\n%s%s" % (q, s["round"] + 1, rounds,
                           "; LAST round: answer with FINAL" if s["round"] + 1 == rounds else "", s["it"]["text"], s["conv"]) for q, s in op)
            reply = call(head + body + "\n\nNow write one section per open question (%s)." % ", ".join(q for q, _ in op), model) or ""
            # A FAILED CALL IS NOT AN ANSWER (2026-10-03): an empty reply (usage limit, spawn failure) used to cost a round, and
            # after six of them the question was SAVED as unanswered -- scored wrong, and never retried on a rerun (335 of 382
            # read-back answers on 2026-10-02). Now the batch stops and writes nothing, so a rerun asks again.
            if not reply.strip(): return 0
            secs = dict(re.findall(r"###\s*(t\d{3})\s*\n(.*?)(?=\n###\s*t\d{3}|\Z)", reply, re.S))
            for q, s in op:
                s["round"] += 1
                parts = re.findall(r"(?:^|\n)\s*(QUERY|FINAL)\s*:\s*(.*?)(?=\n\s*(?:QUERY|FINAL)\s*:|\Z)", secs.get(q, ""), re.S)
                fin = [clean(x) for k, x in parts if k == "FINAL"]; qs = [clean(x) for k, x in parts if k == "QUERY"][:5]
                if fin: s["final"] = fin[0]
                elif qs:
                    out = []
                    for n, x in enumerate(qs, 1):
                        stt, res, cols = DB.execute(con, x, ms=5000)
                        shown = ("columns %s\n" % cols + "\n".join(str(r) for r in res[:20]) + ("\n... (%d rows)" % len(res) if len(res) > 20 else "")) if stt == "ok" else "ERROR: %s" % res
                        out.append("QUERY %d: %s\nRESULT %d:\n%s" % (n, x, n, shown[:2500]))
                    s["conv"] += "\n-- your round %d --\n%s" % (s["round"], "\n\n".join(out))
                else: s["conv"] += "\n-- your round %d: no valid section --" % s["round"]
        for q, s in st.items():
            o = {"key": s["it"]["key"], "final": s["final"], "turns": s["round"], "batch_size": len(job), "model": model}
            if s["final"]:
                a = DB.rows(con, s["final"]); o["executes"] = a is not None
                if a is not None: o["answer"] = a; o["rows_answer"] = len(a)
            json.dump(o, open(path(o["key"]), "w"), default=str)
        return len(job)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for n in ex.map(one, jobs): print("solver batch done: %d questions" % n if n else "solver batch FAILED (empty reply): not saved, retried on rerun", flush=True)
    return {it["key"]: json.load(open(path(it["key"]))) for it in items if os.path.exists(path(it["key"]))}
