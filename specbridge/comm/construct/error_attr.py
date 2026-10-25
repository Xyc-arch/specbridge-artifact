"""ERROR ATTRIBUTION FOR A SOLVER RUN, BY CODE FIRST (no model calls): where a wrong answer departs from the reference.
    python -m specbridge.comm.construct.error_attr <corpus dir> [--model haiku] [--arm natural]   (reads the delivered corpus.jsonl)   -> <corpus>/ERRORS_<arm>_<model>.md, .json
Per wrong answer, from the stored answer and the reference answer alone:
  kind     no answer | does not execute | wrong column count | rows missing | rows extra | rows differ (same count)
           | values in output k | column order only | within 1% (rounding)
  outputs  which output positions differ (as multisets of values, so row order and ties do not matter)
  rows     reference rows the answer lacks / answer rows the reference lacks, by the columns that do match
  paired   whether the other arm answered the same task correctly, when it was run (solver_eval --explicit, a research arm)
  flagged  whether the writer's review ever flagged the requirement that the differing output belongs to"""
import collections, json, math, re, sys


def _num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def _key(v, rel=1e-6):
    f = _num(v)
    if f is None or isinstance(v, str): return repr(v)
    if not math.isfinite(f): return repr(f)
    return "%.5g" % f if rel >= 1e-3 else "%.9g" % f


def _col(rows, j, rel=1e-6):
    return collections.Counter(_key(r[j], rel) for r in rows if j < len(r))


def attribute(ref, ans, r):
    """-> (kind, differing output positions 1-based, detail)"""
    if not r or not r.get("final"): return "no answer", [], ""
    if str(r.get("executes")) != "True": return "does not execute", [], ""
    ans = ans or []; n = len(ref[0]) if ref else 0
    if ans and len(ans[0]) != n: return "wrong column count", [], "expected %d, got %d" % (n, len(ans[0]))
    diff = [j + 1 for j in range(n) if _col(ref, j) != _col(ans, j)]
    loose = [j + 1 for j in range(n) if _col(ref, j, 1e-3) != _col(ans, j, 1e-3)]
    if len(ans) != len(ref):
        same = [j for j in range(n) if j + 1 not in diff] or list(range(n))
        rk = collections.Counter(tuple(_key(x[j]) for j in same) for x in ref); ak = collections.Counter(tuple(_key(x[j]) for j in same) for x in ans)
        kind = "rows missing" if len(ans) < len(ref) else "rows extra"
        return kind, diff, "reference %d rows, answer %d; lacks %d, adds %d" % (len(ref), len(ans), sum((rk - ak).values()), sum((ak - rk).values()))
    if not diff: return "column order only" if ans != ref else "graded wrong, multisets equal (ties or order)", [], ""
    if not loose: return "within 0.1% (rounding)", diff, ""
    perm = sorted(map(lambda j: tuple(sorted(_col(ref, j).items())), range(n))) == sorted(map(lambda j: tuple(sorted(_col(ans, j).items())), range(n)))
    if perm: return "column order only", diff, ""
    return "values in output %s" % ",".join(map(str, loose)), loose, ""


def run(d, model="haiku", arm="natural"):
    T = {json.loads(l)["id"]: json.loads(l) for l in open(d + "/corpus.jsonl")}
    res = json.load(open("%s/solver_%s.json" % (d, model)))["results"]
    name = d.rstrip("/").split("/")[-1]; base = "out/solver/%s/%s" % (name, model)
    import glob, hashlib, os
    other = "explicit" if arm == "natural" else "natural"
    rows = []
    for k, v in res.items():
        tid, a = k.split("|")[0], k.split("|")[1]
        if a != arm or v["correct"]: continue
        t = T[tid]
        if arm == "natural":
            q = t["question"]; fk = "%s|natural|%s" % (tid, hashlib.sha1(q.encode()).hexdigest()[:8])
        else: fk = "%s|explicit" % tid
        fp = "%s/%s.json" % (base, re.sub(r"[^\w.-]", "_", fk))
        r = json.load(open(fp)) if os.path.exists(fp) else None
        ans = None
        if r and r.get("answer") is not None:
            ans = r["answer"] if isinstance(r["answer"], list) else eval(r["answer"], {"__builtins__": {}}, {"None": None, "nan": float("nan"), "inf": float("inf")})
        kind, outs, det = attribute(t["reference_answer"], ans, r)
        flags = {f.get("id") for h in t["natural_precise"].get("checks", []) for f in (h.get("failures") or [])}
        rows.append({"id": tid, "S": t["S"], "A": t["A"], "shape": " > ".join(p.split(":")[0] for p in t["construction"].split(" > ")),
                     "status": t["natural_precise"]["status"], "kind": kind, "outputs": outs, "detail": det,
                     "other_arm_right": res.get("%s|%s" % (tid, other), {}).get("correct"),
                     "review_flagged": sorted(x for x in flags if x and (x in {"output %d" % o for o in outs} or x == "steps")),
                     "solver_sql": (r or {}).get("final", "")})
    json.dump(rows, open("%s/ERRORS_%s_%s.json" % (d, arm, model), "w"), indent=1)
    kc = collections.Counter(re.sub(r"output [\d,]+", "output k", x["kind"]) for x in rows)
    L = ["# Wrong %s answers by %s on `%s`: %d, attributed by code (no model calls)\n" % (arm, model, name, len(rows)),
         "| what differs | wrong | %s arm right on the same task |" % other, "|---|---|---|"]
    for k, n in kc.most_common():
        L.append("| %s | %d | %s |" % (k, n, sum(bool(x["other_arm_right"]) for x in rows if re.sub(r"output [\d,]+", "output k", x["kind"]) == k) if any(x["other_arm_right"] is not None for x in rows) else "not run"))
    L += ["\n| task | S | A | shape | writer status | what differs | %s right | review flagged before |" % other, "|---|---|---|---|---|---|---|---|"]
    for x in sorted(rows, key=lambda x: (x["kind"], x["shape"])):
        L.append("| %s | %d | %d | %s | %s | %s %s | %s | %s |" % (x["id"][-10:], x["S"], x["A"], x["shape"], x["status"], x["kind"], x["detail"],
                                                              {True: "yes", False: "no", None: "not run"}[x["other_arm_right"]], ", ".join(x["review_flagged"]) or ""))
    open("%s/ERRORS_%s_%s.md" % (d, arm, model), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, v: a[a.index(k) + 1] if k in a else v
    run(a[0], opt("--model", "haiku"), opt("--arm", "natural"))
