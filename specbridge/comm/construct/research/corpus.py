"""A MEANINGFUL CORPUS FOR ANY P ON ANY D, end to end.
    python -m specbridge.comm.construct.research.corpus <db> [--source ported|dbfirst|both] [--n 100] [--attempts 400] [--seed 11] [--no-veto] [--out DIR]
  1 catalogue   catalogues/<db>.json (specbridge.pd.realize.semantic: built once, one bounded model review) -- any D under specbridge.pd.corpora
  2 generate    ported: pd's generator with the frozen law fitted on LiveSQL (specbridge.pd.realize.crossdb.one), accepted rows only
                dbfirst: every admissible family instance (specbridge.pd.structures.dbfirst)
  3 freeze      lift, execute, 1-2,000 rows, a decidable grader, explicit V                      (specbridge.comm.construct.freeze)
  4 dedupe      identical SQL once
  5 veto        the sensibility policy (specbridge.comm.construct.research.veto; declared, switchable with --no-veto)
  6 select      a seeded sample of n, balanced over source and structure (step, arithmetic, join, aggregate)
  7 report      <out>/REPORT.md: funnel by stage and source, structure against P and D's own gold (when D has gold), a random
                sample of tasks; <out>/corpus.jsonl the tasks (each with its source, its veto labels and explicit V)
Every stage writes its file as it finishes; a rerun resumes (model calls cached in <out>/cache)."""
import collections, json, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.construct.freeze import freeze
from specbridge.comm.construct.research.veto import judge

BIRD_DEV = "dev_unzipped/dev_20240627/dev.json"


def J(p, d=None): return json.load(open(p)) if os.path.exists(p) else d


def catalogue(db):
    from specbridge.pd.realize.semantic import build, path
    if not os.path.exists(path(db)): build(db)
    return path(db)


def generate(db, source, attempts, seed, out):
    """[(source, sql)] of accepted candidates."""
    cands = []
    if source in ("ported", "both"):
        f = "%s/generator/%s.jsonl" % (out, db)
        if not os.path.exists(f):
            from specbridge.pd.realize.crossdb import one
            os.makedirs(out + "/generator", exist_ok=True); one(db, attempts, seed, out + "/generator")
        from specbridge.comm.construct.research.ported import accepted
        cands += [("ported", r["sql"]) for r in map(json.loads, open(f)) if "sql" in r and accepted(r)]
    if source in ("dbfirst", "both"):
        from specbridge.pd.structures import dbfirst as P
        S = P.Signature(db)
        for fam, slots, sql in P.families(S):
            ok, _why, _rows = P.matters(S, fam, slots, sql)
            if ok: cands.append(("dbfirst:" + fam, sql))
    return cands


def structure(t):
    f = t.get("features") or {}
    return (t["source"].split(":")[0], f.get("step", 0) > 0, f.get("arith_depth", 0) > 0, f.get("joins", 0) > 0, f.get("aggregates", 0) > 0)


def features_of(sql, db):
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.realize.fidelity import features
    from specbridge.pd.structures.grammar import inline_lets
    try:
        p = lift(sql, DB.catalogue(db).con)
        try: f = features(inline_lets(p))
        except Exception: f = features(p)
        return f
    except Exception: return None


def row(name, fs):
    m = max(1, len(fs)); g = lambda k: [(f.get(k) if f.get(k) is not None else f.get({"step": "step_chain"}.get(k, k), 0)) or 0 for f in fs]
    return "| %s | %d | %.0f%% | %.2f | %.0f%% | %.2f | %.2f |" % (name, len(fs), 100.0 * sum(1 for x in g("arith_depth") if x) / m, sum(g("arith_depth")) / m,
                                                              100.0 * sum(1 for x in g("step") if x) / m, sum(g("joins")) / m, sum(g("aggregates")) / m)


def build(db, source="both", n=100, attempts=400, seed=11, veto=True, out=None):
    out = out or "out/corpus/%s" % db; os.makedirs(out, exist_ok=True); funnel = collections.OrderedDict()
    catalogue(db)
    cands = generate(db, source, attempts, seed, out); funnel["candidates"] = collections.Counter(s.split(":")[0] for s, _ in cands)
    ff = out + "/frozen.jsonl"
    if not os.path.exists(ff):
        with open(ff, "w") as f:
            for i, (src, sql) in enumerate(cands):
                t, why = freeze("%s-%04d" % (db, i), db, sql, src)
                f.write(json.dumps(t if t else {"id": "%s-%04d" % (db, i), "source": src, "refused": why}, default=str) + "\n")
    T = [t for t in map(json.loads, open(ff)) if "refused" not in t]
    funnel["frozen"] = collections.Counter(t["source"].split(":")[0] for t in T)
    seen, U = set(), []
    for t in T:
        if t["reference_sql"] not in seen: seen.add(t["reference_sql"]); U.append(t)
    funnel["unique"] = collections.Counter(t["source"].split(":")[0] for t in U)
    if veto:
        V = judge([{"id": t["id"], "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0], "snapshot": t["snapshot"], "database": db} for t in U], cache=out + "/cache")
        for t in U: t["veto"] = V.get(t["id"], {"kept": False})
        K = [t for t in U if t["veto"]["kept"]]
    else: K = U
    funnel["sensible (veto)" if veto else "no veto"] = collections.Counter(t["source"].split(":")[0] for t in K)
    rng = random.Random(seed); by = collections.defaultdict(list)
    for t in K: by[structure(t)].append(t)
    for v in by.values(): rng.shuffle(v)
    keys = sorted(by, key=str); pick = []; i = 0
    while len(pick) < n and any(by.values()):
        k = keys[i % len(keys)]; i += 1
        if by[k]: pick.append(by[k].pop())
    funnel["selected"] = collections.Counter(t["source"].split(":")[0] for t in pick)
    with open(out + "/corpus.jsonl", "w") as f:
        for t in pick: f.write(json.dumps(t, default=str) + "\n")
    report(db, out, funnel, U, K, pick, veto)


def report(db, out, funnel, U, K, pick, veto):
    srcs = sorted({s for c in funnel.values() for s in c})
    L = ["# Corpus on `%s`\n" % db, "## Funnel\n", "| stage | " + " | ".join(srcs) + " | all |", "|---|" + "---|" * (len(srcs) + 1)]
    for st, c in funnel.items(): L.append("| %s | %s | %d |" % (st, " | ".join(str(c.get(s, 0)) for s in srcs), sum(c.values())))
    gold = []
    if os.path.exists(BIRD_DEV):
        gold = [f for f in (features_of(x["SQL"], db) for x in json.load(open(BIRD_DEV)) if x["db_id"] == db) if f]
    L += ["\n## Structure\n", "| population | n | with arithmetic | mean arithmetic depth | with a step | joins | aggregates |", "|---|---|---|---|---|---|---|"]
    if gold: L.append(row("R_t real: %s's own gold" % db, gold))
    for s in srcs:
        L.append(row("%s, unique" % s, [t["features"] for t in U if t["source"].startswith(s)]))
        if veto: L.append(row("%s, sensible" % s, [t["features"] for t in K if t["source"].startswith(s)]))
    L.append(row("corpus (selected)", [t["features"] for t in pick]))
    L.append("\n## A random sample of the corpus\n")
    for t in random.Random(7).sample(pick, min(8, len(pick))):
        L += ["- **%s** (%s): %s" % (t["id"], t["source"], t["instruction"].split("\nConventions")[0][:600]), "  - `%s`" % t["reference_sql"][:300]]
    open(out + "/REPORT.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:30]))


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    build(a[0], opt("--source", "both"), int(opt("--n", 100)), int(opt("--attempts", 400)), int(opt("--seed", 11)), "--no-veto" not in a, opt("--out", None))
