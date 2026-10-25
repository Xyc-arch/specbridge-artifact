"""REVIEW OF DATABASE-CENTRED P (specbridge.pd.structures.dbgrammar) ACROSS DEPTHS: does meaning survive increasing complexity?
Per database, per (arithmetic depth A, step depth S) cell: every instance enumerated -> checked on the data (dbgrammar.matters)
-> a seeded sample of up to K per cell frozen (executable SQL, explicit V, decidable grader) -> blind review (the sensibility
veto's two reviewers, who see the SQL and its specification, never the construction's WHY).
Three measures, reported SEPARATELY and never merged:
  1 coverage        what the grammar reaches on the database, table by table (dbgrammar.coverage); a zero is a finding
  2 execution/spec  of the instances tried per cell, how many froze (ran, 1-2,000 rows, explicit V rendered), with refusals
  3 sensibility     of the frozen sample, how many both blind reviewers call sensible, by arithmetic depth and by step depth
    python -m specbridge.comm.construct.research.grammar_review <db> [--k 4]      -> out/grammar/<db>/REVIEW.md, sample.jsonl"""
import collections, json, os, random, sys
from specbridge.comm.construct.freeze import freeze
from specbridge.comm.construct.research.veto import judge
from specbridge.comm.common import db as DB


def run(db, k=4, seed=30):
    from specbridge.pd.structures.dbfirst import Signature
    from specbridge.pd.structures import dbgrammar as G
    out = "out/grammar/%s" % db; os.makedirs(out, exist_ok=True)
    S = Signature(db); X = G.instances(S)
    cells = collections.defaultdict(list)
    for x in X: cells[(x["A"], x["S"])].append(x)
    rng = random.Random(seed); stats = {}; sample = []
    for cell in sorted(cells):
        xs = cells[cell]; ok = [x for x in xs if G.matters(S, x)[0]]; rng.shuffle(ok)
        frozen = []; tried = 0; refused = collections.Counter()
        for x in ok:
            if len(frozen) >= k: break
            tried += 1
            t, why = freeze(x["id"], db, x["sql"], "grammar A%d S%d %s" % (cell[0], cell[1], x["construct"]), why=x["why"], A=x["A"], S=x["S"], construct=x["construct"], slots=x["slots"])
            if t: frozen.append(t)
            else: refused[str(why)[:80]] += 1
        stats[cell] = {"enumerated": len(xs), "matters": len(ok), "tried": tried, "frozen": len(frozen), "refused": refused}
        sample += frozen
    V = judge([{"id": t["id"], "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0], "snapshot": t["snapshot"], "database": db} for t in sample],
              cache=out + "/cache")
    for t in sample: t["veto"] = V.get(t["id"], {"kept": False, "labels": {}})
    with open(out + "/sample.jsonl", "w") as f:
        for t in sample: f.write(json.dumps(t, default=str) + "\n")
    C = G.coverage(S)
    L = ["# Database-centred P across depths on `%s`\n" % db,
         "Grammar: specbridge.pd.structures.dbgrammar (v2). Three measures, reported separately.\n",
         "## 1. Coverage\n",
         "%d tables; %d single-column foreign keys in the join graph; %d composite foreign keys EXCLUDED (never a partial join)%s.\n"
         % (len(C["tables"]), C["fk"], len(C["composite"]), (": " + "; ".join("%s(%s) -> %s" % (c, ", ".join(cs), p) for c, cs, p in C["composite"])) if C["composite"] else ""),
         "| table | rows | record table | numeric (measure/count) | summable | time-indexed | quantities that vary (by depth) | groups | only composite links |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in C["tables"]:
        L.append("| %s | %d | %s | %s | %s | %s | %d %s | %d | %s |" % (r["table"], r["rows"] or 0, "yes" if r["record"] else "no", ", ".join(r["numeric"]) or "-",
                 ", ".join(r["summable"]) or "-", "yes" if r["time_indexed"] else "no", r["quantities"], dict(sorted(r["by_depth"].items())) if r["by_depth"] else "",
                 r["groups"], "yes" if r["composite_only"] else ""))
    L += ["\nInstances enumerated: %d. Per (A, S) cell:\n" % len(X), "| A | S | enumerated | intermediate result matters |", "|---|---|---|---|"]
    for a in range(0, 4):
        for s_ in range(0, 4):
            st = stats.get((a, s_))
            L.append("| %d | %d | %d | %d |" % (a, s_, st["enumerated"] if st else 0, st["matters"] if st else 0))
    L += ["\n## 2. Execution and specification\n", "Tried in seeded order until %d froze (ran, 1-2,000 rows, decidable grader, explicit V rendered).\n" % k,
          "| A | S | tried | frozen | refusals |", "|---|---|---|---|---|"]
    for cell in sorted(stats):
        st = stats[cell]; L.append("| %d | %d | %d | %d | %s |" % (cell[0], cell[1], st["tried"], st["frozen"], dict(st["refused"]) or "-"))
    L.append("\nTotal: %d/%d tried froze." % (sum(st["frozen"] for st in stats.values()), sum(st["tried"] for st in stats.values())))
    L += ["\n## 3. Sensibility (blind review)\n",
          "Two reviewers (opus, sonnet) see the SQL and its explicit specification, not the construction's reasons; 'sensible' = both say sensible.\n",
          "| A | S | frozen | sensible (both) | labels (opus / sonnet) |", "|---|---|---|---|---|"]
    for cell in sorted(stats):
        ts = [t for t in sample if (t["A"], t["S"]) == cell]
        lab = collections.Counter("%s/%s" % (t["veto"]["labels"].get("opus"), t["veto"]["labels"].get("sonnet")) for t in ts)
        L.append("| %d | %d | %d | %d | %s |" % (cell[0], cell[1], len(ts), sum(t["veto"]["kept"] for t in ts), dict(lab) or "-"))
    L.append("\nTotal (from the review records): %d/%d sensible (both reviewers)." % (sum(t["veto"]["kept"] for t in sample), len(sample)))
    byA = collections.defaultdict(list)
    for t in sample: byA[t["A"]].append(t)
    L.append("\nBy arithmetic depth: " + "; ".join("A%d %d/%d sensible" % (a, sum(t["veto"]["kept"] for t in ts), len(ts)) for a, ts in sorted(byA.items())))
    byS = collections.defaultdict(list)
    for t in sample: byS[t["S"]].append(t)
    L.append("By step depth: " + "; ".join("S%d %d/%d sensible" % (s, sum(t["veto"]["kept"] for t in ts), len(ts)) for s, ts in sorted(byS.items())))
    L.append("\n## Not kept (all)\n")
    for t in sample:
        if not t["veto"]["kept"]:
            L += ["- **%s** A%d S%d %s: %s" % (t["id"], t["A"], t["S"], t["construct"], t["instruction"].split("\nConventions")[0][:400]),
                  "  - reviewers: " + " | ".join("%s: %s" % (m, (t["veto"].get("reasons") or {}).get(m)) for m in ("opus", "sonnet"))]
    L.append("\n## Examples, one per cell (first frozen)\n")
    for cell in sorted(stats):
        ts = [t for t in sample if (t["A"], t["S"]) == cell]
        if not ts: continue
        t = ts[0]
        L += ["### A%d S%d -- %s (%s)" % (cell[0], cell[1], t["construct"], "sensible" if t["veto"]["kept"] else "not kept: " + str(t["veto"]["labels"])),
              "- why: " + " | ".join(t["why"]), "- specification: " + t["instruction"].split("\nConventions")[0][:700], "- SQL: `%s`" % t["reference_sql"][:400],
              "- reviewers: " + " | ".join("%s: %s" % (m, (t["veto"].get("reasons") or {}).get(m)) for m in ("opus", "sonnet")), ""]
    open(out + "/REVIEW.md", "w").write("\n".join(L) + "\n"); print("\n".join(l for l in L if not l.startswith(("- ", "  - "))))


if __name__ == "__main__":
    a = sys.argv[1:]
    run(a[0], int(a[a.index("--k") + 1]) if "--k" in a else 4)
