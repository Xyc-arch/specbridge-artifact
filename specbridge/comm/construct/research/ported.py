"""PORTED P: freeze the queries a run of pd's generator ACCEPTED, then select a sample spread over databases and structural
families (not by any solver outcome).
Accepted: a row of `specbridge.pd.realize.crossdb` / `specbridge.pd.realize.generate` output with verdict "valid", status "ok", at least one row and no policy flag,
or a row of the funnel log format with stage "passed the checks". The experiment tasks under out/gamma_pool came from the
latest generator's run (commit 51b6a28, logs out/funnel/where_t_filter_<db>.jsonl).
    python -m specbridge.comm.construct.research.ported build [out_dir] [run files ...]   -> <out_dir>/tasks.jsonl  (default out/gamma_pool)
    python -m specbridge.comm.construct.research.ported select <n per db json> [pool] [out]   e.g. '{"financial": 8}'"""
import collections, json, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.construct.freeze import freeze

GENERATOR_LOG = "out/funnel/where_t_filter_%s.jsonl"
QUOTA = {"california_schools": 10, "thrombosis_prediction": 10, "superhero": 9, "store_1": 8, "financial": 8, "toxicology": 5}


def accepted(r):
    if "stage" in r: return r["stage"] == "passed the checks" and r.get("task") == "task"
    return r.get("verdict") == "valid" and r.get("status") == "ok" and int(r.get("rows") or 0) > 0 and not r.get("policies")


def build(out="out/gamma_pool", files=None):
    files = files or [GENERATOR_LOG % db for db in DB.DATABASES if os.path.exists(GENERATOR_LOG % db)]
    os.makedirs(out, exist_ok=True); n, skipped = 0, collections.Counter()
    with open(out + "/tasks.jsonl", "w") as f:
        for path in files:
            for k, r in enumerate(map(json.loads, open(path))):
                if "sql" not in r or not accepted(r): continue
                db = r.get("db") or path.split("_")[-1].split(".")[0]; i = int(r.get("i", k))
                try: t, why = freeze("%s-%03d" % (db, i), db, r["sql"], "generator run %s, attempt %d" % (os.path.basename(path), i), trivial=r.get("trivial", []))
                except Exception as e: t, why = None, type(e).__name__
                if t is None: skipped[why] += 1; continue
                f.write(json.dumps(t, default=str) + "\n"); n += 1
    print("frozen %d ported tasks; not frozen %s" % (n, dict(skipped)))


def select(quota=QUOTA, pool="out/gamma_pool/tasks.jsonl", out="out/p_gamma/tasks.jsonl", seed=20261003):
    """Round robin over structural families within each database, seeded."""
    T = [json.loads(l) for l in open(pool)]; rng = random.Random(seed)
    fam = lambda t: (t["features"]["step"], t["features"]["window"], t["features"]["aggregates"] > 0, t["features"]["joins"] > 0, t["features"]["arith_depth"] >= 3)
    pick = []
    for db, n in quota.items():
        by = collections.defaultdict(list)
        for t in T:
            if t["database"] == db: by[fam(t)].append(t)
        for v in by.values(): rng.shuffle(v)
        keys = sorted(by, key=str); i = 0
        while sum(1 for p in pick if p["database"] == db) < n and any(by.values()):
            k = keys[i % len(keys)]; i += 1
            if by[k]: pick.append(by[k].pop())
    with open(out, "w") as f:
        for t in pick: f.write(json.dumps(t, default=str) + "\n")
    print("selected %d: %s" % (len(pick), dict(collections.Counter(t["database"] for t in pick))))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "build": build(*(a[1:2] or ["out/gamma_pool"]), files=a[2:] or None)
    else: select(json.loads(a[1]) if len(a) > 1 else QUOTA, *a[2:4])
