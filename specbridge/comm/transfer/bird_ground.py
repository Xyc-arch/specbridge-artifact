"""BIRD QUICK CHECK OF GROUNDING (2026-10-13, a quick signal, not proof). 120 BIRD dev questions in the VALUE-DEPENDENT slice --
the grounding finds a stored value matching a question term (errors.grounding's "STORED VALUES" line; the rule used on Spider 2.0)
-- chosen by that code rule, seeded, BEFORE any scoring. No provided evidence. Two arms, Sonnet, the Spider 2.0 test prompt
(disclose.PLAIN: schema with three example rows, documentation "(none)", the question): plain vs grounding appended to the
documentation. Scored by BIRD set match and the shape-tolerant grade.
    python -m specbridge.comm.transfer.bird_ground run | report"""
import concurrent.futures as cf, json, math, os, random, sqlite3, sys
from specbridge.comm.transfer import errors as ER, disclose as X
from specbridge.comm.common import db as DB, grade as G

OUT = "out/bird_ground"; ROOT = "dev_unzipped/dev_20240627"; N, SEED, MODEL = 120, 20261023, "sonnet"


def context(path):
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True); L = []
    for name, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL ORDER BY name"):
        L.append(sql.strip() + ";")
        try:
            rows = con.execute('SELECT * FROM "%s" LIMIT 3' % name.replace('"', '""')).fetchall()
            if rows: L.append("-- example rows: " + "; ".join(str(tuple(str(v)[:40] for v in r)) for r in rows))
        except Exception: pass
    con.close(); return "\n".join(L)


def sample():
    f = OUT + "/sample.json"
    if os.path.exists(f): return json.load(open(f))
    dev = json.load(open(ROOT + "/dev.json")); rng = random.Random(SEED); idx = list(range(len(dev))); rng.shuffle(idx); out = []
    for k in idx:
        x = dev[k]; path = "%s/dev_databases/%s/%s.sqlite" % (ROOT, x["db_id"], x["db_id"])
        if "STORED VALUES" not in ER.grounding(x["db_id"], x["question"], dbpath=path): continue      # the slice rule, before scoring
        if DB.rows(DB.connect(path), x["SQL"]) is None: continue
        out.append({"question_id": x["question_id"], "db": x["db_id"], "path": path, "question": x["question"], "sql": x["SQL"]})
        if len(out) == N: break
    os.makedirs(OUT, exist_ok=True); json.dump(out, open(f, "w"), indent=1); return out


def run(workers=6):
    from specbridge.comm.common.llm import call, parse
    Q = sample(); ctx = {}
    for q in Q: ctx.setdefault(q["path"], context(q["path"]))
    def one(j):
        arm, q = j; f = "%s/%s/%d.json" % (OUT, arm, q["question_id"])
        if os.path.exists(f): return
        gr = ER.grounding(q["db"], q["question"], dbpath=q["path"]) if arm == "ground" else ""
        p = X.PLAIN % (ctx[q["path"]], "(none)" + ("\n\nFACTS FROM THE DATABASE (computed by code):\n" + gr if gr else ""), q["question"]); txt = call(p, MODEL)
        if not (txt or "").strip(): return
        r = parse(txt, "{") or {}; con = DB.connect(q["path"]); ref = DB.rows(con, q["sql"]); a = DB.rows(con, r["sql"]) if r.get("sql") else None
        os.makedirs(os.path.dirname(f), exist_ok=True)
        json.dump({"question_id": q["question_id"], "arm": arm, "sql": r.get("sql"), "pass": a is not None and bool(G.bird_ex(ref, a)), "shape": a is not None and bool(G.shape_tolerant(ref, a)),
                   "chars_in": len(p), "chars_out": len(txt), "grounding": gr}, open(f, "w"), indent=1, default=str)
    jobs = [(a, q) for q in Q for a in ("plain", "ground")]; random.Random(SEED).shuffle(jobs)
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))
    report()


def report():
    Q = sample(); ld = lambda a, q: json.load(open("%s/%s/%d.json" % (OUT, a, q["question_id"]))) if os.path.exists("%s/%s/%d.json" % (OUT, a, q["question_id"])) else None
    rows = [(ld("plain", q), ld("ground", q)) for q in Q]; rows = [r for r in rows if all(r)]
    mc = lambda b, c: 1.0 if b + c == 0 else min(1.0, 2 * sum(math.comb(b + c, j) for j in range(min(b, c) + 1)) / 2 ** (b + c))
    L = ["# BIRD quick check of grounding (QUICK SIGNAL, not proof) (`specbridge.comm.transfer.bird_ground`)\n",
         "%d BIRD dev questions in the value-dependent slice (chosen by the code rule before scoring), no evidence, Sonnet, one call each.\n" % len(rows),
         "| grade | plain | grounding | wins / losses | exact McNemar p |", "|---|---|---|---|---|"]
    for g in ("pass", "shape"):
        up = sum(b[g] and not a[g] for a, b in rows); dn = sum(a[g] and not b[g] for a, b in rows)
        L.append("| %s | %d (%.0f%%) | %d (%.0f%%) | +%d / -%d | %.2g |" % ("BIRD set match" if g == "pass" else "shape-tolerant", sum(a[g] for a, _b in rows), 100 * sum(a[g] for a, _b in rows) / max(1, len(rows)),
                 sum(b[g] for _a, b in rows), 100 * sum(b[g] for _a, b in rows) / max(1, len(rows)), up, dn, mc(up, dn)))
    L.append("\nCharacters in / out per question: plain %d / %d; grounding %d / %d." % tuple(sum(r[k][f] for r in rows) / max(1, len(rows)) for k, f in ((0, "chars_in"), (0, "chars_out"), (1, "chars_in"), (1, "chars_out"))))
    os.makedirs(OUT, exist_ok=True); open(OUT + "/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
