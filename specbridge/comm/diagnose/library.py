"""STEP 7: the collections a renderer retrieves from, and the helpers that retrieve.
  meaning_retrieval.jsonl   gate high + meaning choice   -> examples for conditioned rendering
  form_retrieval.jsonl      gate high + output form      -> a separate category
  review_pool.jsonl         everything else              -> kept for review, never retrieved as an ambiguity example
    python -m specbridge.comm.diagnose.library build"""
import collections, json, os, sys
from specbridge.comm.diagnose import LIB

RETRIEVED = """RETRIEVED EXAMPLE from a library of reviewed real questions with the same kind of choice (a different database). It
shows HOW a real asker communicated such a choice. Use it for how to phrase the open choice naturally; do NOT copy its content
or its other open aspects.
REAL QUESTION + EVIDENCE: %s
ITS TWO READINGS: A: %s | B: %s
HOW EACH REQUIREMENT OF ITS EXPLICIT SPECIFICATION IS CARRIED:
%s
THE OPEN CHOICE: %s -- open phrase: "%s" -- why both readings fit: %s
PATTERN:
%s
"""


def build():
    Lb = [json.loads(l) for l in open(LIB + "/library.jsonl")]; g = lambda r: r.get("gate") or {}
    meaning = [r for r in Lb if g(r).get("confidence") == "high" and g(r).get("category") == "meaning choice"]
    form = [r for r in Lb if g(r).get("confidence") == "high" and g(r).get("category") == "output form"]
    review = [r for r in Lb if r not in meaning and r not in form]
    for fn, rs in (("meaning_retrieval.jsonl", meaning), ("form_retrieval.jsonl", form), ("review_pool.jsonl", review)):
        with open(os.path.join(LIB, fn), "w") as f:
            for r in rs: f.write(json.dumps(r, default=str) + "\n")
    ch = lambda r: (r.get("tags") or {}).get("choice")
    L = ["# Library collections\n", "- meaning retrieval: %d records %s" % (len(meaning), dict(collections.Counter(map(ch, meaning)))),
         "- output-form retrieval: %d" % len(form), "- review pool: %d (suspected reference defects %d)" % (len(review), sum(g(r).get("category") == "reference defect" for r in review))]
    open(LIB + "/COLLECTIONS.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


SEEDS = None      # a frozen copy of the retrieval records (freeze_seeds); when set, every retrieval reads only it


def meaning(): return [json.loads(l) for l in open(SEEDS or (LIB + "/meaning_retrieval.jsonl"))]


def freeze_seeds(out):
    """Copy the retrieval records into <out>/seeds.jsonl with a manifest: each record's id (source:task), record version, gate
    verdict and choice tag, the file hash and the date. A run then reads only this copy, whatever the library becomes."""
    import hashlib, time
    os.makedirs(out, exist_ok=True); src = LIB + "/meaning_retrieval.jsonl"; raw = open(src, "rb").read()
    open(out + "/seeds.jsonl", "wb").write(raw); R = [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
    json.dump({"source": src, "sha256": hashlib.sha256(raw).hexdigest(), "frozen": time.strftime("%Y-%m-%d %H:%M"), "records": [
        {"id": "%s:%s" % (r["source"].split("/")[-1], r["task"]), "version": r.get("version"), "choice": (r.get("tags") or {}).get("choice"),
         "gate": {k: (r.get("gate") or {}).get(k) for k in ("confidence", "category")}} for r in R]}, open(out + "/seeds_manifest.json", "w"), indent=1)
    print("froze %d seed records -> %s/seeds.jsonl" % (len(R), out))


def retrieve(target, lib):
    """Choice tag, then structure Jaccard, then semantics Jaccard, then library order."""
    jac = lambda a, b: len(set(a) & set(b)) / max(1, len(set(a) | set(b)))
    cands = [r for r in lib if (r.get("tags") or {}).get("choice") == target["choice"]]
    return max(enumerate(cands), key=lambda ir: (jac(ir[1]["tags"].get("structure") or [], target.get("structure", [])),
                                                  jac(ir[1]["tags"].get("semantics") or [], target.get("semantics", [])), -ir[0]))[1] if cands else None


def example_text(r):
    a = r.get("analysis") or {}; A = next(x for x in r["readings"] if x["id"] == "A"); B = next(x for x in r["readings"] if x["id"] == "B")
    reqs = "\n".join("- [%s] %s | \"%s\"" % (q["real"], q["requirement"], q["phrase"]) for q in a.get("requirements", []))
    c = a.get("choice") or {}
    return RETRIEVED % (r["original"], A["reading"], B["reading"], reqs, c.get("decision"), c.get("open_phrase"), c.get("why_both"), "\n".join("- " + s for s in a.get("pattern", [])))


def example_for(kind):
    """(example text, id) of the retrieved meaning record for a choice kind, or ("", None)."""
    ex = retrieve({"choice": kind}, meaning())
    return (example_text(ex), "%s:%s" % (ex["source"].split("/")[-1], ex["task"])) if ex else ("", None)


def summary():
    """One line per meaning record: the kinds of choice real askers leave open (for proposers)."""
    return "\n".join("- [%s] real question: %s | open phrase: \"%s\" | why both fit: %s" % (r["tags"]["choice"], r["original"].split("\n")[0][:160],
                     ((r.get("analysis") or {}).get("choice") or {}).get("open_phrase"), (((r.get("analysis") or {}).get("choice") or {}).get("why_both") or "")[:200]) for r in meaning())


if __name__ == "__main__":
    build()
