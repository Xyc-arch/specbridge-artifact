"""STEP 1: benchmark tasks in two wordings. The held-out split is fixed once and never run or inspected.
    python -m specbridge.comm.diagnose.tasks split
    python -m specbridge.comm.diagnose.tasks build <batch name> <out dir>      (question ids from out/comm_library/batches.json)"""
import collections, json, os, random, sys
from specbridge.comm.common import db as DB
from specbridge.comm.diagnose import LIB
ROOT = "dev_unzipped/dev_20240627"
BIRD_DBS = ["california_schools", "financial", "superhero", "thrombosis_prediction", "toxicology"]


def split(seed=20261001, held=20, first=12, used=()):
    """held out per database, then a first collection batch; the rest stays for later batches."""
    dev = [x for x in json.load(open(ROOT + "/dev.json")) if x["db_id"] in BIRD_DBS and x["question_id"] not in set(used)]
    rng = random.Random(seed); rng.shuffle(dev); hold, rest = [], []
    for db in BIRD_DBS:
        xs = [x for x in dev if x["db_id"] == db]; hold += xs[:held]; rest += xs[held:]
    rng.shuffle(rest); batch1 = []
    for db in BIRD_DBS: batch1 += [x for x in rest if x["db_id"] == db][:first]
    json.dump({"note": "held-out evaluation set: never run, inspected or used for retrieval", "question_ids": sorted(x["question_id"] for x in hold)},
              open(LIB + "/heldout_eval.json", "w"), indent=1)
    json.dump({"batch1": sorted(x["question_id"] for x in batch1), "remaining": sorted(x["question_id"] for x in rest if x not in batch1)},
              open(LIB + "/batches.json", "w"), indent=1)


def build(ids, out):
    """tasks_original.jsonl (question + evidence) and tasks_explicit.jsonl (explicit V of the reference); refused.json."""
    os.makedirs(out, exist_ok=True); SNAP = DB.snapshots(); orig, exp, refused = [], [], []
    dev = [x for x in json.load(open(ROOT + "/dev.json")) if x["question_id"] in set(ids)]
    for n, x in enumerate(sorted(dev, key=lambda x: x["question_id"])):
        db = x["db_id"]; snap, sha = SNAP[db]
        res = DB.rows(DB.connect(snap), x["SQL"])
        if res is None: refused.append({"id": "b%03d" % n, "qid": x["question_id"], "reason": "reference does not run"}); continue
        t = {"id": "b%03d" % n, "question_id": x["question_id"], "database": db, "snapshot": snap, "snapshot_sha256": sha, "difficulty": x["difficulty"],
             "instruction": x["question"] + ("\nEvidence: " + x["evidence"] if x.get("evidence") else ""), "reference_sql": x["SQL"],
             "reference_answer": res, "grader": {"bird_set": True}, "tie_groups": None, "last_pool": None, "category": "unaudited", "arm": "original"}
        orig.append(t)
        e = DB.explicit(x["SQL"], db)
        if e: exp.append(dict(t, instruction=e, arm="explicit"))
        else: refused.append({"id": t["id"], "qid": x["question_id"], "reason": "explicit V refuses the reference"})
    for arm, rs in (("original", orig), ("explicit", exp)):
        with open("%s/tasks_%s.jsonl" % (out, arm), "w") as f:
            for t in rs: f.write(json.dumps(t, default=str) + "\n")
    json.dump(refused, open(out + "/refused.json", "w"), indent=1)
    print("%s: original %d, explicit %d, refused %d" % (out, len(orig), len(exp), len(refused)))


SPIDER = "spider_data/spider_data/dev.json"


def spider_split(seed=20261003, dev_n=150, confirm_n=50):
    """SPIDER (2026-10-03): a seeded, disjoint split of the usable dev questions (gold runs here AND explicit V renders,
    out/diagnose_coverage/coverage.json), stratified by database in proportion to its usable questions. The confirmation
    questions are never run, inspected or used for prompts or the library before the protocol is frozen."""
    cov = json.load(open("out/diagnose_coverage/coverage.json"))["spider"]
    usable = [r["id"] for r in cov if r.get("gold_runs") and r.get("explicit")]
    dbof = {r["id"]: r["db"] for r in cov}; rng = random.Random(seed); per = collections.defaultdict(list)
    for i in usable: per[dbof[i]].append(i)
    for db in per: rng.shuffle(per[db])
    def take(n, pool):                      # largest remainder over databases, by their remaining usable counts
        tot = sum(len(v) for v in pool.values()); raw = {db: n * len(v) / tot for db, v in pool.items()}
        k = {db: int(x) for db, x in raw.items()}
        for db in sorted(raw, key=lambda d: -(raw[d] - k[d]))[: n - sum(k.values())]: k[db] += 1
        out = []
        for db, v in pool.items(): out += v[:k[db]]; del v[:k[db]]
        return sorted(out)
    dev, conf = take(dev_n, per), take(confirm_n, per)
    assert not set(dev) & set(conf)
    json.dump({"seed": seed, "usable": len(usable), "development": dev, "confirmation": conf,
               "note": "confirmation: never run, inspected or used for prompts or the library before the protocol is frozen"},
              open(LIB + "/spider_split.json", "w"), indent=1)
    return dev, conf


def build_spider(split, out):
    """tasks_original.jsonl (the Spider question) and tasks_explicit.jsonl (explicit V of the gold), as build() does for BIRD."""
    from specbridge.comm.construct import freeze
    os.makedirs(out, exist_ok=True); ids = set(json.load(open(LIB + "/spider_split.json"))[split])
    orig, exp, refused = [], [], []
    for i, x in enumerate(json.load(open(SPIDER))):
        qid = "spider_dev_%04d" % i
        if qid not in ids: continue
        db = x["db_id"]; snap, sha = freeze.snapshot(db)
        res = DB.rows(DB.connect(snap), x["query"])
        if res is None: refused.append({"id": qid, "reason": "reference does not run"}); continue
        t = {"id": qid, "question_id": qid, "database": db, "snapshot": snap, "snapshot_sha256": sha, "difficulty": None,
             "instruction": x["question"], "reference_sql": x["query"], "reference_answer": res, "grader": {"bird_set": True},
             "tie_groups": None, "last_pool": None, "category": "unaudited", "arm": "original", "benchmark": "spider_dev"}
        orig.append(t); e = DB.explicit(x["query"], db)
        if e: exp.append(dict(t, instruction=e, arm="explicit"))
        else: refused.append({"id": qid, "reason": "explicit V refuses the reference"})
    for arm, rs in (("original", orig), ("explicit", exp)):
        with open("%s/tasks_%s.jsonl" % (out, arm), "w") as f:
            for t in rs: f.write(json.dumps(t, default=str) + "\n")
    json.dump(refused, open(out + "/refused.json", "w"), indent=1)
    print("%s: original %d, explicit %d, refused %d" % (out, len(orig), len(exp), len(refused)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "split": split()
    elif a[0] == "spider-split": print([len(x) for x in spider_split()])
    elif a[0] == "spider-build": build_spider(a[1], a[2])
    else: build(json.load(open(LIB + "/batches.json"))[a[1]], a[2])
