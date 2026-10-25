"""Score answers on the SpecBridge request sets by execution.

    python benchmark/score.py --self-test             # every reference query must match its own reading and only it
    python benchmark/score.py answers.jsonl [--all]   # score a model's answers (accepted sets only, unless --all)

answers.jsonl, one line per answered request:
    {"id": "<set id>", "request": "specific_A" | "specific_B" | "open", "sql": "<main query>", "alternatives": ["<sql>", ...]}
"alternatives" is optional and only used for the open request.

Reported: specific requests answered with their own reading; open requests whose main answer is reading A or B; open requests
whose main answer plus alternatives return both readings; and both readings returned among sets whose two specific requests
are answered right (the gap the paper reports)."""
import json, os, sqlite3, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from specbridge.pd.spec.render import grade      # the graders used for every number in the paper


def load(path=os.path.join(HERE, "request_sets.jsonl"), accepted_only=True, families=("main", "filter")):
    """Request sets by id. family "main": the 215 sets of the paper's main results; "filter": the 92 sets with an added filter."""
    S = [json.loads(l) for l in open(path)]
    return {s["id"]: s for s in S if (s["accepted"] or not accepted_only) and s["family"] in families}


def run(s, sql, ms=60000):
    """The rows of `sql` on the set's database, or None when it does not run (read-only, time limit `ms`)."""
    if not sql: return None
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(HERE, "databases", s["database"] + ".sqlite"), uri=True); t0 = time.time()
    con.set_progress_handler(lambda: 1 if (time.time() - t0) * 1000 > ms else 0, 10000)
    try: return [list(r) for r in con.execute(sql).fetchall()]
    except Exception: return None
    finally: con.close()


def _t(xs): return [tuple(r) for r in xs] if xs is not None else None


def matches(s, rows):
    """Which readings an answer returns: A with the task's grader and tie pool; B with its own grader when B has one, else a
    multiset comparison without order or limit. Same rule as specbridge.comm.transfer.evaluate.matches."""
    if rows is None: return []
    g = s["grading"]; m = []
    if grade(g["grader"], _t(g["answer_A"]), _t(rows), g["tie_groups"], _t(g["last_pool"]))[0]: m.append("A")
    b = g.get("B")
    ok = grade(b["grader"], _t(b["answer"]), _t(rows), b["tie_groups"], _t(b["last_pool"]))[0] if b else \
        grade(dict(g["grader"], ordered=False, limit=None), _t(g["answer_B"]), _t(rows), None, None)[0]
    if ok: m.append("B")
    return m


def self_test(sets):
    bad = 0
    for s in sets.values():
        for r in "AB":
            got = matches(s, run(s, s["sql"][r]))
            if r not in got: bad += 1; print("reference %s of %s does not match its reading: %s" % (r, s["id"], got))
    print("%d sets, %d reference queries checked, %d failures" % (len(sets), 2 * len(sets), bad)); return bad == 0


def score(sets, answers):
    by = {}
    for a in answers:
        if a["id"] in sets: by[(a["id"], a["request"])] = a
    spec = {r: [] for r in ("specific_A", "specific_B")}; adm = []; both = []; both_given = []
    for sid, s in sets.items():
        right = {}
        for r in ("specific_A", "specific_B"):
            a = by.get((sid, r))
            if a is None: continue
            ok = r[-1] in matches(s, run(s, a.get("sql"))); spec[r].append(ok); right[r] = ok
        a = by.get((sid, "open"))
        if a is None: continue
        main = set(matches(s, run(s, a.get("sql")))); allm = set(main)
        for q in a.get("alternatives") or []: allm |= set(matches(s, run(s, q)))
        adm.append(bool(main)); both.append({"A", "B"} <= allm)
        if right.get("specific_A") and right.get("specific_B"): both_given.append({"A", "B"} <= allm)
    pc = lambda xs: "%d/%d (%.1f%%)" % (sum(xs), len(xs), 100 * sum(xs) / len(xs)) if xs else "-"
    print("sets scored:                                   %d" % len({sid for sid, _ in by}))
    for r in spec: print("%-46s %s" % (r + " right:", pc(spec[r])))
    print("open: main answer is A or B:                   %s" % pc(adm))
    print("open: both readings returned:                  %s" % pc(both))
    print("open: both returned, if both specific right:   %s" % pc(both_given))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sets = load(accepted_only="--all" not in sys.argv)
    if "--self-test" in sys.argv: sys.exit(0 if self_test(sets) else 1)
    if not args: print(__doc__); sys.exit(2)
    score(sets, [json.loads(l) for l in open(args[0])])
