"""THE GENERATE-THEN-FILTER PIPELINE, cheapest work first.
    python -m specbridge.comm.construct.research.pipeline <db> [--per-cell 20] [--max-candidates N] [--seconds T] [--package spec|full|none]
                                           [--no-veto] [--seed 11] [--workers 6]      -> out/pipeline/<db>/{candidates,kept}.jsonl, RUN.md
  1 generate   every SQL the grammar (specbridge.pd.structures.dbgrammar) can write, WITHOUT data checks; deduplicated; id = hash of the SQL
  2 select     per (A, S) cell a seeded, diverse order (round robin over table x quantity x construct); walked until --per-cell
               pass the checks, the cell runs out, or a budget is spent
  3 check      dbgrammar.admit: the quantity varies, the intermediate result matters (one scan per quantity, memoised)
  4 package    "spec" (default): lifted SQL + explicit V + features, no execution; "full": + saved answer, tie groups, grader,
               1-2,000 rows; "none": SQL only. Cached by (SQL, level, snapshot + catalogue + code version); bounded processes
  5 veto       the sensibility policy (specbridge.comm.construct.research.veto), verdicts cached per item; skipped with --no-veto or --package none
Budgets: --max-candidates bounds how many selected candidates are checked; --seconds stops starting new checks or packaging.
Progress lines give completed / total, throughput and time left for each stage."""
import collections, concurrent.futures as cf, hashlib, json, os, random, sys, time


def progress(stage, i, n, t0, every=[0.0]):
    now = time.time()
    if i == n or now - every[0] > 5:
        every[0] = now; r = i / max(1e-9, now - t0)
        sys.stderr.write("[%s] %d/%d  %.1f/s  %s left\n" % (stage, i, n, r, "%.0fs" % ((n - i) / r) if r > 0 and i < n else "0s")); sys.stderr.flush()


def order(xs, rng):
    """A seeded, diverse order: round robin over (table, quantity, construct), each group shuffled."""
    by = collections.defaultdict(list)
    for x in xs: by[(x["slots"]["table"], x["slots"]["quantity"], x["construct"])].append(x)
    keys = sorted(by); rng.shuffle(keys)
    for k in keys: rng.shuffle(by[k])
    out = []
    while any(by.values()):
        for k in keys:
            if by[k]: out.append(by[k].pop())
    return out


def _pack(a):
    from specbridge.comm.construct.freeze import packaged
    x, db, level = a
    t, why = packaged(x["id"], db, x["sql"], "grammar A%d S%d %s" % (x["A"], x["S"], x["construct"]), level=level,
                      why=x["why"], A=x["A"], S=x["S"], construct=x["construct"], slots=x["slots"])
    return x["id"], t, why


def admit(S, x, db, cache="out/cache/check"):
    """dbgrammar.admit, cached on disk by (SQL, the database version, the grammar's code)."""
    from specbridge.pd.structures import dbgrammar as G
    from specbridge.comm.construct.freeze import version
    if not hasattr(admit, "code"):
        admit.code = hashlib.sha256(b"".join(open(f, "rb").read() for f in ("specbridge/pd/structures/dbgrammar.py", "specbridge/pd/structures/dbfirst.py"))).hexdigest()[:12]
    f = "%s/%s/%s.json" % (cache, db, hashlib.sha256("\0".join([x["sql"], version(db), admit.code]).encode()).hexdigest()[:24])
    if os.path.exists(f): return tuple(json.load(open(f)))
    r = G.admit(S, x); os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(list(r), open(f, "w")); return r


def run(db, per_cell=20, max_candidates=None, seconds=None, package="spec", veto=True, seed=11, workers=6, out=None):
    from specbridge.pd.structures.dbfirst import Signature
    from specbridge.pd.structures import dbgrammar as G
    from specbridge.comm.common.llm import CALLS
    out = out or "out/pipeline/%s" % db; os.makedirs(out, exist_ok=True); T0 = time.time(); cost = {}
    deadline = T0 + seconds if seconds else None
    # 1 GENERATE (no data checks) and DEDUPLICATE
    t0 = time.time(); S = Signature(db); X = G.instances(S, check=False); seen, U = set(), []
    for x in X:
        if x["sql"] in seen: continue
        seen.add(x["sql"]); x["id"] = "%s-%s" % (db, hashlib.sha1(x["sql"].encode()).hexdigest()[:10]); U.append(x)
    cost["generate_s"] = time.time() - t0
    # 2 SELECT and 3 CHECK, cell by cell
    rng = random.Random(seed); cells = collections.defaultdict(list)
    for x in U: cells[(x["A"], x["S"])].append(x)
    funnel = {c: collections.Counter(enumerated=len(xs)) for c, xs in cells.items()}; picked = []; tried = 0; t0 = time.time()
    total = sum(min(per_cell, len(xs)) for xs in cells.values()); why_not = collections.Counter(); stopped = None
    import threading
    local = threading.local()
    def check(x):   # one read-only signature (connection + memo) per thread; SQLite runs queries outside the GIL
        if not hasattr(local, "S"): local.S = Signature(db)
        return x, admit(local.S, x, db)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for c in sorted(cells):
            queue = order(cells[c], rng)
            while queue and funnel[c]["admitted"] < per_cell:
                if max_candidates and tried >= max_candidates: stopped = "candidate budget (%d)" % max_candidates; break
                if deadline and time.time() > deadline: stopped = "time budget (%ds)" % seconds; break
                k = min(workers, per_cell - funnel[c]["admitted"], len(queue), (max_candidates - tried) if max_candidates else workers)
                batch, queue = queue[:k], queue[k:]
                for x, (ok, why) in ex.map(check, batch):   # in order, so the selection does not depend on timing
                    tried += 1; funnel[c]["tried"] += 1
                    if ok and funnel[c]["admitted"] < per_cell: funnel[c]["admitted"] += 1; picked.append(x); progress("check", len(picked), total, t0)
                    elif not ok: why_not[why.split(" ")[0] if why else "?"] += 1
    cost["check_s"] = time.time() - t0
    # 4 PACKAGE (optional; cached; bounded processes)
    tasks = {}; t0 = time.time(); refused = collections.Counter()
    if package != "none":
        todo = list(picked); i = 0
        with (cf.ProcessPoolExecutor(max_workers=workers) if len(todo) > 30 else cf.ThreadPoolExecutor(max_workers=1)) as ex:
            for j in range(0, len(todo), 4 * workers):     # in chunks, so the time budget can stop between them
                if deadline and time.time() > deadline: stopped = stopped or "time budget (%ds)" % seconds; break
                for k, t, why in ex.map(_pack, [(x, db, package) for x in todo[j:j + 4 * workers]]):
                    i += 1
                    if t: tasks[k] = t
                    else: refused[str(why)[:60]] += 1
                    progress("package:" + package, i, len(todo), t0)
        for x in picked:
            if x["id"] in tasks: funnel[(x["A"], x["S"])]["packaged"] += 1
    cost["package_s"] = time.time() - t0
    # 5 VETO (cached per item)
    V = {}; t0 = time.time()
    if veto and tasks:
        from specbridge.comm.construct.research.veto import judge
        V = judge([{"id": k, "sql": t["reference_sql"], "spec": t["instruction"].split("\nConventions")[0], "snapshot": t["snapshot"], "database": db}
                   for k, t in tasks.items()], cache="out/cache/veto/%s" % db)
        for k, v in V.items():
            if v["kept"]: funnel[(tasks[k]["A"], tasks[k]["S"])]["kept"] += 1
    cost["veto_s"] = time.time() - t0; cost["total_s"] = time.time() - T0
    with open(out + "/candidates.jsonl", "w") as f:
        for x in picked: f.write(json.dumps(dict(tasks.get(x["id"]) or x, veto=V.get(x["id"])), default=str) + "\n")
    with open(out + "/kept.jsonl", "w") as f:
        for k, t in tasks.items():
            if V.get(k, {}).get("kept"): f.write(json.dumps(dict(t, veto=V[k]), default=str) + "\n")
    L = ["# Pipeline run on `%s`\n" % db, "per cell %d, package %s, veto %s, seed %d%s.\n" % (per_cell, package, "on" if veto else "off", seed, "; STOPPED by " + stopped if stopped else ""),
         "| A | S | enumerated | tried | passed checks | packaged | kept |", "|---|---|---|---|---|---|---|"]
    for c in sorted(funnel):
        f = funnel[c]; L.append("| %d | %d | %d | %d | %d | %d | %d |" % (c + (f["enumerated"], f["tried"], f["admitted"], f["packaged"], f["kept"])))
    s = sum(funnel.values(), collections.Counter())
    L.append("| all | | %d | %d | %d | %d | %d |" % (s["enumerated"], s["tried"], s["admitted"], s["packaged"], s["kept"]))
    L.append("\nGenerated %d SQL, %d distinct. Check failures: %s. Packaging refusals: %s." % (len(X), len(U), dict(why_not) or "-", dict(refused) or "-"))
    L.append("\nTime (s): " + ", ".join("%s %.1f" % (k[:-2], v) for k, v in cost.items()) + (". Per kept task: %.1fs." % (cost["total_s"] / max(1, s["kept"])) if veto and s["kept"] else "."))
    open(out + "/RUN.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
    json.dump({"funnel": {"%d,%d" % c: dict(f) for c, f in funnel.items()}, "cost": cost, "stopped": stopped, "model_calls": dict(CALLS)}, open(out + "/run.json", "w"))
    return funnel, cost


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    for db in [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]:
        run(db, int(opt("--per-cell", 20)), int(opt("--max-candidates", 0)) or None, int(opt("--seconds", 0)) or None, opt("--package", "spec"),
            "--no-veto" not in a, int(opt("--seed", 11)), int(opt("--workers", 6)), opt("--out", None))
