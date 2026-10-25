"""MATCHED RESOURCES for the coverage decomposition. The explanation runs (specbridge.comm.transfer.disclose) gave each family its
open wording and ONE specific wording, all as one call without exploration. This runs the OTHER specific wording under exactly the
same single call, so both specific readings and the open request are answered with identical resources and instruction.
    python -m specbridge.comm.transfer.matched run <model> [<model> ...]   -> <render>/disclose/complement/<model>/
    python -m specbridge.comm.transfer.matched report                       -> <render>/disclose/complement/RESULTS.md, results.json
A failed call (empty reply) is not saved, so a rerun asks again. At most 6 workers (machine rule)."""
import concurrent.futures as cf, json, os, sys, time
from specbridge.comm.common import db as DB
from specbridge.comm.transfer import disclose as X, combined as CB

D = CB.D
MODELS = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]


def _f(out, m, k, w): return "%s/%s/%s__%s.json" % (out, m, k.replace(":", "__").replace("/", "_"), w)


def run(models, workers=6):
    from specbridge.comm.common.llm import call, parse
    fz, wr, out = X._paths(D); C = {c["case"]: c for c in json.load(open(fz))["cases"]}; W = json.load(open(wr))
    S = json.load(open(out + "/sample.json")); assert S["prompt_sha"] == X.PROMPT_SHA
    comp = out + "/complement"
    other = {k: ("precise_B" if "precise_A" in S["wordings"][k] else "precise_A") for k in S["cases"]}
    def one(job):
        k, m = job; w = other[k]; f = _f(comp, m, k, w)
        if os.path.exists(f): return
        c = C[k]; schema, docs = DB.context(c); con = DB.connect(c["snapshot"]); t0 = time.time()
        txt = call(X.INSTRUCTION % (schema, docs, W[k][w]), m)
        if not (txt or "").strip(): return                       # a failed call is not an answer
        r = parse(txt, "{") or {}; prim = r.get("sql"); a = DB.rows(con, prim) if prim else None
        o = {"case": k, "wording": w, "model": m, "prompt_sha": X.PROMPT_SHA, "response": r, "raw": None if r else txt,
             "primary_executes": a is not None, "primary_matches": X._match(c, a), "seconds": round(time.time() - t0, 1)}
        os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(o, open(f, "w"), indent=1, default=str)
    jobs = [(k, m) for k in S["cases"] for m in models]
    with cf.ThreadPoolExecutor(max_workers=min(workers, 6)) as ex: list(ex.map(one, jobs))


def report():
    """Per solver: open requests not covered (both readings returned by main + alternatives), split by whether the SAME single call
    answers both specific wordings right (the sampled one from disclose/, the other from complement/)."""
    from specbridge.comm.transfer import reviewed as RV
    fz, _wr, out = X._paths(D); S = json.load(open(out + "/sample.json")); S["cases"] = RV.accepted(S["cases"]); res = {}
    mutual = {c["case"] for c in json.load(open(fz))["cases"] if c.get("label") == "mutually recognized open"}
    L = ["# Coverage decomposition under matched resources (one call, no exploration, same instruction)\n",
         "| solver | sets with all three answered | not covered | of which both specific right | share | cannot (one or both specific wrong) |",
         "|---|---|---|---|---|---|"]
    for m in MODELS:
      for scope, keep in (("all", None), ("both reviewers accept the open request", mutual)):
          n = miss = can = 0
          for k in S["cases"]:
              if keep is not None and k not in keep: continue
              fo = _f(out, m, k, "open"); ws = [w for w in S["wordings"][k] if w != "open"]
              if not ws: continue
              f1 = _f(out, m, k, ws[0]); w2 = "precise_B" if ws[0] == "precise_A" else "precise_A"; f2 = _f(out + "/complement", m, k, w2)
              if not all(os.path.exists(x) for x in (fo, f1, f2)): continue
              o, p1, p2 = (json.load(open(x)) for x in (fo, f1, f2))
              got = set(o.get("primary_matches") or []) | {r for a in (o.get("alternatives") or []) for r in (a.get("matches") or [])}
              covered = {"A", "B"} <= got
              both_spec = ws[0][-1] in (p1.get("primary_matches") or []) and w2[-1] in (p2.get("primary_matches") or [])
              n += 1
              if not covered:
                  miss += 1; can += both_spec
          res.setdefault(m, {})[scope] = {"n": n, "not_covered": miss, "both_specific_right": can}
          L.append("| %s (%s) | %d | %d | %d | %s | %d |" % (m, scope, n, miss, can, ("%.0f%%" % (100 * can / miss)) if miss else "-", miss - can))
    json.dump(res, open(out + "/complement/results.json", "w"), indent=1)
    open(out + "/complement/RESULTS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    {"run": lambda: run(sys.argv[2:] or MODELS), "report": lambda: report()}[sys.argv[1]]()
