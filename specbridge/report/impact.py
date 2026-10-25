"""DOES A SILENT CHOICE MATTER TO THE USER? (2026-10-13; zero model calls.)
IMPACT. For BIRD dev questions where the convention detector (specbridge.comm.diagnose.inclination) finds a choice the reference
settles but no cue in the question or evidence does, apply the matching library-rule edit (specbridge.comm.diagnose.rules) to the
REFERENCE SQL, execute both and measure how far the answer moves. Spider 2.0 SQLite: the same on reference-equivalent queries (the
released gold queries that reproduce an accepted answer, plus Sonnet answers the official scorer accepts), with the same cue check.
  changed      the result changes at all
  value > 10% / > 50%   single-value answers: relative change of the value
  top item / top-k set  ordered answers: the first row's first column / the set of first-column values changes
  row set      the set of returned rows changes (different entities included)
AUDIT. For the 12 evaluation databases plus 3 Spider 2.0 databases: joins with fan-out > 1.1 or > 5% unmatched rows, measure
columns > 5% NULL, ranking columns tied at the top, flag/status columns with a minority value >= 2%.
    python -m specbridge.report.impact impact | audit   -> out/impact/IMPACT.md, AUDIT.md (+ .json)"""
import collections, glob, json, os, re, sqlite3, sys, time
from specbridge.comm.diagnose import inclination as I, rules as RU

OUT = "out/impact"; BIRD = "dev_unzipped/dev_20240627"
TO_RULE = {"ties_and_selection": "ties", "counting_unit": "count_unit", "population_scope": "join_kind", "missing_values": "null_filter",
           "boundary_between": "boundary", "boundary_open": "boundary"}
NAME = {"ties": "ties at an extreme", "count_unit": "rows vs distinct entities", "join_kind": "unmatched rows kept or dropped",
        "null_filter": "missing values filtered", "boundary": "inclusive vs strict bound"}


def run(path, sql, limit=15):
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True); t0 = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - t0 > limit else 0, 100000)
    try: return con.execute(sql).fetchall()
    except Exception: return None
    finally: con.close()


def silent(sql, question):
    try: sd = I.sides(sql, question)
    except Exception: return set()
    return {TO_RULE[k] for k in sd if k in TO_RULE and not (k in I.CUES and I.CUES[k].search(question or ""))}


def num(v):
    try: return float(v)
    except Exception: return None


def compare(a, b, ordered):
    out = {"changed": set(map(tuple, a)) != set(map(tuple, b)) or (ordered and a != b), "row_set": {tuple(r) for r in a} != {tuple(r) for r in b}}
    if len(a) == 1 and len(b) == 1 and a[0] and b[0]:
        x, y = num(a[0][-1]), num(b[0][-1])
        if x is not None and y is not None:
            rel = abs(x - y) / max(abs(x), 1e-9) if x != 0 else (0.0 if y == 0 else float("inf"))
            out["value"] = rel
    if ordered and a and b:
        out["top_item"] = a[0][0] != b[0][0]; out["topk_set"] = {r[0] for r in a} != {r[0] for r in b}
    return out


def cases():
    """(source, db path, question, reference SQL, question id): BIRD dev (Spider 2.0 was dropped with its section, 2026-10-25)."""
    out = []
    for x in json.load(open(BIRD + "/dev.json")):
        out.append(("BIRD dev", "%s/dev_databases/%s/%s.sqlite" % (BIRD, x["db_id"], x["db_id"]), x["question"] + " " + (x.get("evidence") or ""), x["SQL"], x["question_id"]))
    return out


def impact():
    R = collections.defaultdict(lambda: collections.defaultdict(list)); nq = collections.Counter(); nsil = collections.Counter(); ex = []
    QL = collections.defaultdict(list)
    changed_ids = collections.defaultdict(list)
    for src, path, q, sql, qid in cases():
        nq[src] += 1; sil = silent(sql, q)
        if not sil: continue
        base = run(path, sql)
        if base is None: continue
        nsil[src] += 1; ordered = bool(re.search(r"\border\s+by\b", sql, re.I))
        done = set(); qc = []
        for st in RU.sites(sql):
            if st[0] not in sil or st[0] in done: continue
            if not RU.alternative_ok(sql, st, path): continue
            e = RU.edit(sql, st); alt = run(path, e) if e else None
            if alt is None: continue
            done.add(st[0]); c = compare(base, alt, ordered); R[src][st[0]].append(c); R[src]["all"].append(c); qc.append((st[0], c))
            if c["changed"] and len(ex) < 400: ex.append({"source": src, "question": q[:200], "rule": st[0], "ref_rows": len(base), "alt_rows": len(alt), "value_change": c.get("value"),
                                                           "ref_head": str(base[:2])[:160], "alt_head": str(alt[:2])[:160]})
        if qc: QL[src].append(qc)
        if any(c["changed"] for _k, c in qc): changed_ids[src].append({"id": qid, "rules": sorted({k for k, c in qc if c["changed"]})})
    L = ["# Does a silent choice change the answer? (`specbridge.report.impact`, zero model calls)\n",
         "Per question with a silent choice (the reference settles it, no cue in the question or evidence), the matching library edit is applied "
         "to the reference(-equivalent) SQL and both are executed. One edit per choice type and question. Only edits that give a valid reading "
         "count (rules.alternative_ok).\n"]
    res = {}
    for src in ("BIRD dev",):
        L += ["## %s: %d questions, %d with a silent choice the edit can express\n" % (src, nq[src], nsil[src]),
              "| choice | edits | answer changes | value > 10% (single values) | value > 50% | top item changes (ordered) | top-k set changes | row set changes |",
              "|---|---|---|---|---|---|---|---|"]
        res[src] = {}
        Qs = QL[src]; anyc = lambda qc, f: any(f(k, c) for k, c in qc)
        qrow = {"questions": len(Qs), "any_change": sum(anyc(qc, lambda k, c: c["changed"]) for qc in Qs),
                "any_change_not_join": sum(anyc(qc, lambda k, c: c["changed"] and k != "join_kind") for qc in Qs),
                "value_gt10": sum(anyc(qc, lambda k, c: c.get("value", 0) > 0.10) for qc in Qs), "top_item": sum(anyc(qc, lambda k, c: c.get("top_item", False)) for qc in Qs)}
        res[src]["questions"] = qrow
        L.insert(len(L) - 2, "Per question (of %d with an applicable edit): the answer changes under some other reading in %d (%.0f%%); excluding join-type edits, %d; a single value moves by more than 10%% in %d; the top-ranked item changes in %d.\n" % (
            qrow["questions"], qrow["any_change"], 100 * qrow["any_change"] / max(1, qrow["questions"]), qrow["any_change_not_join"], qrow["value_gt10"], qrow["top_item"]))
        for k in ["all"] + sorted(x for x in R[src] if x != "all"):
            cs = R[src][k]; n = len(cs); v = [c["value"] for c in cs if "value" in c]; o = [c for c in cs if "top_item" in c]
            pc = lambda a, b: "%d / %d (%.0f%%)" % (a, b, 100 * a / b) if b else "-"
            row = {"edits": n, "changed": sum(c["changed"] for c in cs), "single": len(v), "gt10": sum(x > 0.10 for x in v), "gt50": sum(x > 0.50 for x in v),
                   "ordered": len(o), "top": sum(c["top_item"] for c in o), "topk": sum(c["topk_set"] for c in o), "rowset": sum(c["row_set"] for c in cs)}
            res[src][k] = row
            L.append("| %s | %d | %s | %s | %s | %s | %s | %s |" % ("all choices" if k == "all" else NAME.get(k, k), n, pc(row["changed"], n), pc(row["gt10"], row["single"]), pc(row["gt50"], row["single"]),
                     pc(row["top"], row["ordered"]), pc(row["topk"], row["ordered"]), pc(row["rowset"], n)))
        L.append("")
    os.makedirs(OUT, exist_ok=True); json.dump({"results": res, "examples": ex, "changed_questions": changed_ids}, open(OUT + "/impact.json", "w"), indent=1, default=str)
    open(OUT + "/IMPACT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


def audit_db(path, limit=10):
    from specbridge.comm.transfer import facts as FA
    con, t0 = FA._con(path, limit); tabs, cols, fks = FA.schema(con); A = collections.defaultdict(list)
    n = {t: (FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s"' % t) or [0])[0] or 0 for t in tabs}
    for c, cc, p, pc in fks:
        if c not in cols or p not in cols or not n.get(c) or not n.get(p) or not pc: continue
        r = FA._q1(con, t0, 'SELECT AVG(k), MAX(k) FROM (SELECT COUNT(*) AS k FROM "%s" WHERE "%s" IS NOT NULL GROUP BY "%s")' % (c, cc, cc))
        if r and r[0] and r[0] > 1.1: A["join fan-out > 1.1"].append("%s.%s -> %s: %.1f rows per %s row (max %d)" % (c, cc, p, r[0], p, r[1]))
        u = FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" NOT IN (SELECT "%s" FROM "%s" WHERE "%s" IS NOT NULL)' % (p, pc, cc, c, cc))
        if u and u[0] and u[0] / n[p] > 0.05: A["join drops > 5% unmatched"].append("%.0f%% of %s rows have no %s row" % (100 * u[0] / n[p], p, c))
    for t in tabs:
        if not n[t]: continue
        for c, ty in cols[t]:
            if FA.idlike(c): continue
            r = FA._q1(con, t0, 'SELECT SUM("%s" IS NULL), COUNT(DISTINCT "%s") FROM "%s"' % (c, c, t))
            if not r: continue
            share, dist = (r[0] or 0) / n[t], r[1] or 0
            if FA.numeric(ty) and share > 0.05: A["measure column > 5% NULL"].append("%s.%s %.0f%% NULL" % (t, c, 100 * share))
            if FA.numeric(ty) and dist > 20:
                k = FA._q1(con, t0, 'SELECT COUNT(*) FROM "%s" WHERE "%s" = (SELECT MAX("%s") FROM "%s")' % (t, c, c, t))
                if k and k[0] and k[0] > 1: A["ranking column tied at the top"].append("%s.%s: %d rows share the maximum" % (t, c, k[0]))
            if 2 <= dist <= 10:
                vs = FA._qa(con, t0, 'SELECT "%s", COUNT(*) FROM "%s" GROUP BY 1 ORDER BY 2' % (c, t)) or []
                mino = [(v, k / n[t]) for v, k in vs if v is not None and 0.02 <= k / n[t] <= 0.5]
                if mino: A["flag/status with a minority >= 2%"].append("%s.%s: %r is %.0f%%" % (t, c, mino[0][0], 100 * mino[0][1]))
    con.close(); return A


def audit():
    from specbridge.comm.transfer import spider2 as S
    from specbridge.pd.corpora import found
    E12 = ["baseball_1", "sakila_1", "customers_and_invoices", "chinook_1", "financial", "student_club", "thrombosis_prediction", "formula_1",
           "archeology", "insider", "crypto", "alien"]
    dbs = [(d, "%s/%s.sqlite" % (found(d), d)) for d in E12 if found(d)] + [(d, "%s/%s.sqlite" % (S.DBDIR, d)) for d in ("Brazilian_E_Commerce", "IPL", "bank_sales_trading")]
    K = ["join fan-out > 1.1", "join drops > 5% unmatched", "measure column > 5% NULL", "ranking column tied at the top", "flag/status with a minority >= 2%"]
    L = ["# Schema audit: where answers can silently depend on an unstated choice (`specbridge.report.impact audit`)\n",
         "| database | " + " | ".join(K) + " | total |", "|---|" + "---|" * (len(K) + 1)]; J = {}
    for d, p in dbs:
        A = audit_db(p); J[d] = A
        L.append("| %s | %s | %d |" % (d, " | ".join(str(len(A[k])) for k in K), sum(len(A[k]) for k in K)))
    L += ["", "Examples:"] + ["- %s: %s" % (d, "; ".join(J[d][k][0] for k in K if J[d][k])[:600]) for d in ("sakila_1", "Brazilian_E_Commerce") if d in J]
    os.makedirs(OUT, exist_ok=True); json.dump(J, open(OUT + "/audit.json", "w"), indent=1); open(OUT + "/AUDIT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"impact": impact, "audit": audit}[sys.argv[1]]()
