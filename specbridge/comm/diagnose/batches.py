"""THE REMAINING BATCHES: plan them once, run each through the fixed pipeline, summarise each.
    python -m specbridge.comm.diagnose.batches plan [size]       add batch3, batch4, ... to out/comm_library/batches.json (never held-out ids)
    python -m specbridge.comm.diagnose.batches run <batch> ...   tasks -> compare (haiku, 2 repeats) -> inspect -> record -> gate -> library,
                                                       then SUMMARY.md / summary.json in the batch directory; a finished batch is skipped
    python -m specbridge.comm.diagnose.batches summary <batch>
    python -m specbridge.comm.diagnose.batches totals <batch> ...  all batches together, BIRD's grade and the shape-tolerant grade side by side
                                                       (specbridge.comm.common.grade.shape_tolerant, from the stored answers: no model calls)
The protocol is the existing one, unchanged: specbridge.comm.diagnose.{tasks, compare, inspect, record, gate, library} with their own models
(solver haiku; inspector, recorder and gate opus; blind reviewers opus and sonnet) and grading (BIRD set match; tolerance 0.005
reported beside it). Each step's outputs are files, so an interrupted batch resumes where it stopped."""
import collections, json, os, subprocess, sys
from specbridge.comm.diagnose import LIB

MODEL, REPEATS = "haiku", 2


def plan(size=60):
    B = json.load(open(LIB + "/batches.json")); held = set(json.load(open(LIB + "/heldout_eval.json"))["question_ids"])
    used = {q for k, v in B.items() if k.startswith("batch") for q in v}
    dev = {q["question_id"]: q["db_id"] for q in json.load(open("dev_unzipped/dev_20240627/dev.json"))}
    left = [q for q in B["remaining"] if q not in used]
    assert not (set(left) & held), "a held-out question is in the remaining pool"
    per = collections.defaultdict(list)
    for q in left: per[dev[q]].append(q)
    n = max([int(k[5:]) for k in B if k.startswith("batch")] + [0])
    while any(per.values()):
        n += 1; batch = []
        while len(batch) < size and any(per.values()):           # round robin over databases: as balanced as the pool allows
            for db in sorted(per):
                if per[db] and len(batch) < size: batch.append(per[db].pop(0))
        B["batch%d" % n] = sorted(batch)
    json.dump(B, open(LIB + "/batches.json", "w"), indent=1)
    print({k: len(v) for k, v in B.items()})


def sh(*a):
    p = subprocess.run([sys.executable, "-m"] + list(a), capture_output=True, text=True)
    if p.returncode: raise RuntimeError("%s failed: %s" % (" ".join(a), (p.stderr or p.stdout)[-600:]))
    return p.stdout


def run(batch):
    d = "%s/%s" % (LIB, batch)
    if os.path.exists(d + "/summary.json"): print(batch, "already done"); return
    if not os.path.exists(d + "/tasks_original.jsonl"): sh("specbridge.comm.diagnose.tasks", "build", batch, d)
    if not os.path.exists("%s/%s.done" % (d, MODEL)):
        sh("specbridge.comm.diagnose.compare", "run", d, MODEL, str(REPEATS)); open("%s/%s.done" % (d, MODEL), "w").write("done")
    sh("specbridge.comm.diagnose.compare", "report", d, MODEL)
    if not os.path.exists(d + "/inspection.json"): sh("specbridge.comm.diagnose.inspect", "run", d, MODEL)
    sh("specbridge.comm.diagnose.inspect", "report", d)
    if not os.path.exists(d + "/records.json"): sh("specbridge.comm.diagnose.record", "run", d, MODEL)
    sh("specbridge.comm.diagnose.gate", "run"); sh("specbridge.comm.diagnose.library", "build")
    summary(batch)


def _all(rs): return bool(rs) and all(rs)


def summary(batch):
    from specbridge.comm.diagnose.compare import runs, tasks
    d = "%s/%s" % (LIB, batch)
    O = {t["id"]: t for t in tasks(d, "original")}; E = {t["id"]: t for t in tasks(d, "explicit")}
    refused = json.load(open(d + "/refused.json")) if os.path.exists(d + "/refused.json") else []
    out = collections.Counter(); tool = collections.Counter(); per = {}
    for i in O:
        o = runs(d, MODEL, "original", i); e = runs(d, MODEL, "explicit", i) if i in E else []
        for arm, rs in (("original", o), ("explicit", e)):
            for g in rs:
                if not g.get("final"): tool["%s: no final query" % arm] += 1
                elif not g.get("executes"): tool["%s: final query does not execute" % arm] += 1
                if g.get("final_raw"): tool["%s: answer re-graded after the backtick fix" % arm] += 1
        if i not in E: k = "explicit refused (no explicit V)"
        else:
            op, ep = [g["pass"] for g in o], [g["pass"] for g in e]
            if len(op) < REPEATS or len(ep) < REPEATS: k = "incomplete runs"
            elif _all(op) and _all(ep): k = "both correct"
            elif _all(ep) and not any(op): k = "explicit only correct"
            elif _all(op) and not any(ep): k = "real question only correct"
            elif not any(op) and not any(ep): k = "neither correct"
            else: k = "mixed across repeats"
        out[k] += 1; per[i] = k
    ins = json.load(open(d + "/inspection.json")) if os.path.exists(d + "/inspection.json") else []
    causes = collections.Counter(g.get("cause", "").split(" (")[0] for g in ins)
    rec = json.load(open(d + "/records.json")) if os.path.exists(d + "/records.json") else {}
    gate = {g["record"]: g for g in (json.load(open(LIB + "/gate.json")) if os.path.exists(LIB + "/gate.json") else [])}   # a list; later verdicts win
    keys = ["%s:%s" % (batch, r.get("task")) for r in rec.get("library", [])]
    G = {k: gate.get(k, {}) for k in keys}
    acc = collections.Counter((g.get("confidence"), g.get("category")) for g in G.values())
    accepted = [k for k, g in G.items() if g.get("confidence") == "high"]
    unresolved = {"mixed across repeats": [i for i, k in per.items() if k == "mixed across repeats"],
                  "inspection unparsed or uncertain": [g["task"] for g in ins if g.get("cause") in ("UNPARSED", "other") or g.get("confidence") == "low"],
                  "records gated medium/low or uncertain": [k for k, g in G.items() if g.get("confidence") != "high" or g.get("category") == "uncertain"],
                  "not recorded (not_library)": [r.get("task") for r in rec.get("not_library", [])]}
    S = {"batch": batch, "tasks": len(O), "explicit_rendered": len(E), "rendering_failures": len(refused), "outcomes": dict(out),
         "runs": {"original": sum(len(runs(d, MODEL, "original", i)) for i in O), "explicit": sum(len(runs(d, MODEL, "explicit", i)) for i in E)},
         "tool": dict(tool), "inspected": len(ins), "causes": dict(causes), "records": len(rec.get("library", [])),
         "gate": {"%s / %s" % k: n for k, n in acc.items()}, "accepted_high": accepted, "unresolved": unresolved}
    json.dump(S, open(d + "/summary.json", "w"), indent=1)
    L = ["# %s: real question vs explicit V (haiku, %d repeats)\n" % (batch, REPEATS),
         "%d tasks; explicit V rendered for %d (%d refused by the renderer); runs: original %d, explicit %d.\n" % (S["tasks"], S["explicit_rendered"], S["rendering_failures"], S["runs"]["original"], S["runs"]["explicit"]),
         "| outcome (every repeat) | tasks |", "|---|---|"] + ["| %s | %d |" % kv for kv in sorted(out.items(), key=lambda kv: -kv[1])]
    L += ["\nTool failures (runs): %s\n" % (dict(tool) or "none"), "Inspected disagreements: %d; causes: %s\n" % (len(ins), dict(causes)),
          "Library records from this batch: %d; gate: %s; accepted (high): %d\n" % (S["records"], S["gate"], len(accepted)),
          "## Unresolved\n"] + ["- %s: %s" % (k, ", ".join(map(str, v)) or "none") for k, v in unresolved.items()]
    open(d + "/SUMMARY.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
    return S


def totals(batches):
    """(2026-10-03) Written to a file named after the batches: the BIRD batches 3-8 keep remaining_totals.json /
    REMAINING_RESULTS.md; any other set (e.g. spider_dev) gets <names>_totals.json / <names>_RESULTS.md, so one report
    never overwrites another's cited file."""
    if sorted(batches) == ["batch%d" % i for i in range(3, 9)]: paths = (LIB + "/remaining_totals.json", LIB + "/REMAINING_RESULTS.md")
    else: paths = (LIB + "/%s_totals.json" % "+".join(batches), LIB + "/%s_RESULTS.md" % "+".join(batches))
    return _totals(batches, paths)


def _totals(batches, paths):
    from specbridge.comm.diagnose.compare import runs, tasks
    from specbridge.comm.common.grade import shape_tolerant
    def outcome(o, e):
        if len(o) < REPEATS or len(e) < REPEATS: return "incomplete runs"
        if _all(o) and _all(e): return "both correct"
        if _all(e) and not any(o): return "explicit only correct"
        if _all(o) and not any(e): return "real question only correct"
        if not any(o) and not any(e): return "neither correct"
        return "mixed across repeats"
    agg = {"bird": collections.Counter(), "shape": collections.Counter()}; runs_ = collections.Counter(); out = {"bird": collections.Counter(), "shape": collections.Counter()}
    S = [json.load(open("%s/%s/summary.json" % (LIB, b))) for b in batches]; flips = []
    for b in batches:
        d = "%s/%s" % (LIB, b); O = {t["id"]: t for t in tasks(d, "original")}; E = {t["id"] for t in tasks(d, "explicit")}
        for i in E:
            ref = O[i]["reference_answer"]; g = {}
            for arm in ("original", "explicit"):
                rs = runs(d, MODEL, arm, i); runs_[arm] += len(rs)
                g[arm] = {"bird": [x["pass"] for x in rs], "shape": [x["pass"] or (x.get("answer") is not None and shape_tolerant(ref, x["answer"])) for x in rs]}
                for k in ("bird", "shape"): agg[k][arm] += sum(g[arm][k])
            for k in ("bird", "shape"): out[k][outcome(g["original"][k], g["explicit"][k])] += 1
            if outcome(g["original"]["bird"], g["explicit"]["bird"]) != outcome(g["original"]["shape"], g["explicit"]["shape"]): flips.append("%s:%s" % (b, i))
    tot = lambda k: sum(x[k] for x in S)
    causes = collections.Counter(); gate = collections.Counter(); tool = collections.Counter()
    for x in S: causes.update(x["causes"]); gate.update(x["gate"]); tool.update(x["tool"])
    pct = lambda a, n: "%d/%d (%.0f%%)" % (a, n, 100.0 * a / max(1, n))
    L = ["# Real question vs explicit V (%s)\n" % ", ".join(batches),
         "Haiku, %d repeats; grading: BIRD set match, and beside it the shape-tolerant grade (column order and extra columns tolerated, rows must match).\n" % REPEATS,
         "**Denominators:** %d tasks; explicit V rendered for %d; refused by the renderer %d; runs: original %d, explicit %d (on the rendered tasks).\n" % (
             tot("tasks"), tot("explicit_rendered"), tot("rendering_failures"), runs_["original"], runs_["explicit"]),
         "| runs correct | BIRD grade | shape tolerated |", "|---|---|---|",
         "| real question + evidence | %s | %s |" % (pct(agg["bird"]["original"], runs_["original"]), pct(agg["shape"]["original"], runs_["original"])),
         "| explicit V | %s | %s |" % (pct(agg["bird"]["explicit"], runs_["explicit"]), pct(agg["shape"]["explicit"], runs_["explicit"])),
         "\n| outcome per task (every repeat) | BIRD grade | shape tolerated |", "|---|---|---|"]
    for k in ("both correct", "explicit only correct", "real question only correct", "neither correct", "mixed across repeats", "incomplete runs"):
        L.append("| %s | %d | %d |" % (k, out["bird"][k], out["shape"][k]))
    L.append("| explicit refused (no explicit V) | %d | %d |" % (tot("rendering_failures"), tot("rendering_failures")))
    L += ["\nTasks whose outcome changes when shape is tolerated: %d.\n" % len(flips),
          "**Tool failures (runs):** %s\n" % dict(tool), "**Diagnosed causes (%d inspected):** %s\n" % (tot("inspected"), dict(causes.most_common())),
          "**Library records:** %d; gate: %s; accepted (high): %d\n" % (tot("records"), dict(gate), sum(len(x["accepted_high"]) for x in S)),
          "## Unresolved (per batch)\n"]
    for x in S:
        L.append("- **%s**: " % x["batch"] + "; ".join("%s: %d" % (k, len(v)) for k, v in x["unresolved"].items()))
    json.dump({"batches": batches, "runs": dict(runs_), "correct": {k: dict(v) for k, v in agg.items()}, "outcomes": {k: dict(v) for k, v in out.items()},
               "flips": flips}, open(paths[0], "w"), indent=1)
    open(paths[1], "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "plan": plan(int(a[1]) if len(a) > 1 else 60)
    elif a[0] == "run":
        for b in a[1:]: run(b)
    elif a[0] == "totals": totals(a[1:])
    else: summary(a[1])
