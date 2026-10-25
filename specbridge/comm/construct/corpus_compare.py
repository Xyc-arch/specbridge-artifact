"""COMPARE TWO BUILT CORPORA (configuration -> corpus): requested vs delivered depth, operation mix, shape diversity, table
coverage, quantities, runtime and model calls. Everything is read from the corpora's own files.
    python -m specbridge.comm.construct.corpus_compare <corpus dir A> <corpus dir B>   -> <B>/COMPARE.md"""
import collections, json, sys


def load(d):
    T = [json.loads(l) for l in open(d + "/tasks.jsonl")]; R = json.load(open(d + "/report.json")); return T, R


def stats(T, R):
    shape = collections.Counter(" > ".join(p.split(":")[0] for p in t["construction"].split(" > ")) for t in T)
    return {"tasks": len(T), "requested": R.get("requested_cells", {}), "delivered": R.get("delivered_cells", {}),
            "ops": collections.Counter(o for t in T for o in set(p.split(":")[0] for p in t["construction"].split(" > "))),
            "shapes": shape, "largest": shape.most_common(1)[0] if shape else ("-", 0),
            "tables": collections.Counter(x for t in T for x in t["tables_read"]), "multi": sum(len(t["tables_read"]) > 1 for t in T),
            "quantities": len({q for t in T for q in t["quantities"]}), "computations": len({(t["construction"], tuple(sorted(t["quantities"]))) for t in T}),
            "seconds": R.get("seconds"), "calls": R.get("model_calls"), "request": R.get("request") or {}}


def main(a, b):
    A, B = [stats(*load(d)) for d in (a, b)]; na, nb = a.rstrip("/").split("/")[-1], b.rstrip("/").split("/")[-1]
    pct = lambda n, s: "%d (%d%%)" % (n, 100 * n // max(1, s["tasks"]))
    L = ["# %s vs %s\n" % (na, nb), "Same database (wta_1), same standard, same seed; only the configuration differs. Measured from the corpora's files.\n",
         "| | %s | %s |" % (na, nb), "|---|---|---|"]
    row = lambda k, f: L.append("| %s | %s | %s |" % (k, f(A), f(B)))
    row("delivered / requested", lambda s: "%d / %d" % (s["tasks"], sum(s["requested"].values()) if s["requested"] else s["tasks"]))
    row("depth cells requested", lambda s: ", ".join("A%s S%s×%d" % (k.split(",")[0], k.split(",")[1], v) for k, v in sorted(s["requested"].items(), key=lambda kv: tuple(map(int, kv[0].split(","))))))
    row("depth cells delivered", lambda s: ", ".join("A%s S%s×%d" % (k.split(",")[0], k.split(",")[1], v) for k, v in sorted(s["delivered"].items(), key=lambda kv: tuple(map(int, kv[0].split(","))))))
    for o in ("agg", "baseline", "share", "rank", "diff", "ratio"):
        row("tasks using %s" % {"agg": "aggregation", "baseline": "comparison with an average", "share": "shares", "rank": "rankings", "diff": "differences (between steps)", "ratio": "ratios (between steps)"}[o], lambda s, o=o: pct(s["ops"].get(o, 0), s))
    row("construction shapes", lambda s: str(len(s["shapes"])))
    row("largest shape", lambda s: "%s (%d%%)" % (s["largest"][0], 100 * s["largest"][1] // max(1, s["tasks"])))
    row("tables read (tasks)", lambda s: ", ".join("%s %d" % kv for kv in s["tables"].most_common()))
    row("multi-table tasks", lambda s: pct(s["multi"], s))
    row("distinct computations / base quantities", lambda s: "%d / %d" % (s["computations"], s["quantities"]))
    row("runtime", lambda s: "%s s (%.1f s per task)" % (s["seconds"], (s["seconds"] or 0) / max(1, s["tasks"])))
    row("model calls", lambda s: "%s (%.1f per task)" % (s["calls"], (s["calls"] or 0) / max(1, s["tasks"])))
    L.append("\nConfigurations: A `%s`; B `%s`." % (json.dumps({k: v for k, v in A["request"].items() if k not in ("name",)}), json.dumps({k: v for k, v in B["request"].items() if k not in ("name",)})))
    L.append("\nThe first corpus was built by the earlier builder (full packaging before review, oversampling at an assumed 50%); its runtime is not comparable with the second's as a measure of configuration.")
    open(b + "/COMPARE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
