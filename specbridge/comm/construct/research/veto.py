"""THE SENSIBILITY VETO: a declared, switchable policy on frozen tasks (never a language rule). Two blind model reviewers
judge each query against the rubric of the accepted-dataset review (out/review/REVIEW.md); a task is kept only if BOTH call
it sensible. It can only remove tasks, never create or change one.
Its agreement with the earlier three-reviewer labels is measured by `calibrate`; its precision is measured by reading a
sample of what it keeps.
    python -m specbridge.comm.construct.research.veto calibrate          -> out/corpus/VETO_CALIBRATION.md"""
import collections, concurrent.futures as cf, json, os, sys
from specbridge.comm.common import db as DB
from specbridge.comm.common.llm import ask_json

VETO = """Each ITEM is a SQL query over the database below, with its explicit specification. Judge whether it is a SENSIBLE
analytical request on this data: a coherent calculation or retrieval over the target data. Explicit hypothetical arithmetic
on compatible quantities is acceptable. Not sensible: an invented purpose for unrelated quantities, incompatible populations,
accidental row multiplication (a join that repeats the rows being counted or summed), incoherent filters (e.g. an
alphabetical cut on a code or identifier), or arithmetic of a quantity with itself. Judge each item alone.
  label    sensible | uncertain | nonsensical
  defects  short tags, e.g. unrelated-arithmetic, self-arithmetic, row-multiplication, alphabetical-cut, unused-join
  reason   one sentence
%s
Answer ONLY JSON: [{"item": "<id>", "label": "...", "defects": [], "reason": "..."}]

SCHEMA:
%s

DOCUMENTATION:
%s"""
REVIEWERS = ("opus", "sonnet")


def judge(items, cache=None, batch=1, workers=6):
    """items: [{"id", "sql", "spec", "snapshot", "database"}] -> {id: {"labels": {reviewer: label}, "kept": bool, ...}}
    Each task is judged ALONE by default (batch=1): a verdict must not depend on which other tasks share the prompt (in
    batches of six, 24 of 113 verdicts changed with the batch). With `cache`, each item's verdict per reviewer is stored under the hash of (reviewer, rubric, SQL, specification, the
    database's review context), so a rerun sends only items whose SQL, wording or context changed."""
    import hashlib
    by = collections.defaultdict(list)
    for x in items: by[x["database"]].append(x)
    got, jobs = {}, []
    for db, xs in by.items():
        schema, docs = DB.context(xs[0])
        ctx = hashlib.sha256((VETO + schema + docs).encode()).hexdigest()
        for m in REVIEWERS:
            key = lambda x: hashlib.sha256("\0".join([m, ctx, x["sql"], x.get("spec") or ""]).encode()).hexdigest()[:24]
            todo = []
            for x in xs:
                f = cache and "%s/item-%s.json" % (cache, key(x))
                if f and os.path.exists(f): got[(x["id"], m)] = json.load(open(f))
                else: todo.append((x, f))
            for i in range(0, len(todo), batch):
                ch = todo[i:i + batch]
                body = "\n\n".join("--- ITEM %s\nSQL: %s\nSPECIFICATION: %s" % (x["id"], x["sql"], (x.get("spec") or "")[:2500]) for x, _f in ch)
                jobs.append((m, ch, VETO % (body, schema, docs)))
    def one(j):
        m, ch, p = j; r = ask_json(p, m, brace="[", cache=None) or []
        d = {e.get("item"): e for e in r if isinstance(e, dict)}
        res = []
        for x, f in ch:
            v = d.get(x["id"])
            if v and f: os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(v, open(f, "w"))
            res.append((x["id"], m, v or {"label": "unparsed"}))
        return res
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(one, jobs):
            for k, m, d in res: got[(k, m)] = d
    out = collections.defaultdict(lambda: {"labels": {}, "reasons": {}, "defects": {}})
    for (k, m), d in got.items():
        out[k]["labels"][m] = d.get("label"); out[k]["reasons"][m] = d.get("reason"); out[k]["defects"][m] = d.get("defects")
    for k, v in out.items(): v["kept"] = all(v["labels"].get(m) == "sensible" for m in REVIEWERS)
    return dict(out)


def recheck(items, repeats=3, out=None):
    """REMAINING DISAGREEMENT of single-task judging: the same fixed items judged `repeats` times, uncached. Per reviewer,
    the share of items whose label is not the same in every repeat; and the share whose kept/vetoed decision flips."""
    runs = [judge(items, cache=None) for _ in range(repeats)]
    ids = [x["id"] for x in items]
    lab = {m: sum(len({r.get(i, {}).get("labels", {}).get(m) for r in runs}) > 1 for i in ids) for m in REVIEWERS}
    flip = sum(len({r.get(i, {}).get("kept") for r in runs}) > 1 for i in ids)
    res = {"items": len(ids), "repeats": repeats, "label_changes": lab, "decision_flips": flip, "flip_rate": flip / max(1, len(ids)),
           "runs": [{i: r.get(i) for i in ids} for r in runs]}
    if out: json.dump(res, open(out, "w"), default=str)
    return res


def calibrate(out_dir="out/corpus"):
    """Against the earlier blind review (three reviewers, out/review): 180 random accepted queries with a label each."""
    os.makedirs(out_dir, exist_ok=True); items, gold = [], {}
    snaps = DB.snapshots()
    for f in sorted(os.listdir("out/review")):
        if not f.startswith("review_"): continue
        db = f[len("review_"):-5]
        inp = {x["id"]: x for x in json.load(open("out/review/input_%s.json" % db))}
        for r in json.load(open("out/review/" + f)):
            if r.get("set") != "random": continue
            x = inp[r["id"]]; gold[r["id"]] = r["label"]
            items.append({"id": r["id"], "sql": x["sql"], "spec": DB.explicit(x["sql"], db, conventions=False), "snapshot": snaps[db][0], "database": db})
    V = judge(items, cache=out_dir + "/cache")
    c = collections.Counter((gold[k], "kept" if V[k]["kept"] else "vetoed") for k in gold if k in V)
    kept = [k for k in gold if V.get(k, {}).get("kept")]
    L = ["# Sensibility veto: agreement with the earlier three-reviewer labels\n",
         "180 random accepted queries (out/review). Veto: opus and sonnet, kept only if both say sensible.\n",
         "| earlier label | kept | vetoed |", "|---|---|---|"] + ["| %s | %d | %d |" % (g, c[(g, "kept")], c[(g, "vetoed")]) for g in ("sensible", "uncertain", "nonsensical")]
    L.append("\nOf the kept, earlier-labelled sensible: %d/%d (%.0f%%); earlier-sensible retained: %d/%d." % (
        sum(gold[k] == "sensible" for k in kept), len(kept), 100.0 * sum(gold[k] == "sensible" for k in kept) / max(1, len(kept)),
        c[("sensible", "kept")], c[("sensible", "kept")] + c[("sensible", "vetoed")]))
    open(out_dir + "/VETO_CALIBRATION.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    calibrate()
