"""EXTRACT THE METHOD FROM THE CODE, so the paper's protocol cannot drift from what ran.
    python -m specbridge.report.methods   -> out/paper/methods/PROMPTS.md (every prompt verbatim, file:line, sha256[:12])
                                         out/paper/methods/PARAMETERS.md (grammar bounds, budgets, models, seeds, limits, versions)
Reads module attributes and source lines; makes no model calls."""
import hashlib, importlib, inspect, json, os, platform, re, sqlite3, subprocess, sys
sys.path.insert(0, ".")
OUT = "out/paper/methods"; os.makedirs(OUT, exist_ok=True)

PROMPTS = [  # (module, attribute, role in the pipeline)
    ("specbridge.pd.realize.semantic", "PROMPT", "catalogue: one model review per database"),
    ("specbridge.comm.construct.rubric", "RUBRIC", "task review (benchmark rubric), Opus and Sonnet each alone"),
    ("specbridge.comm.verbal.precise", "WRITER", "precise natural question: writer (Sonnet)"),
    ("specbridge.comm.verbal.precise", "REVIEWER", "precise natural question: reviewer (Opus, one task per call); also the read-back repair's reviewer"),
    ("specbridge.comm.common.solve", "HEAD", "solver: every solver call (explicit V, natural, real benchmarks, families)"),
    ("specbridge.comm.diagnose.inspect", "INSPECT", "diagnosis: inspector (Opus)"),
    ("specbridge.comm.diagnose.record", "PAIR", "diagnosis: two-reading record (Opus)"),
    ("specbridge.comm.diagnose.record", "REVIEWN", "diagnosis: blind reviewers of readings (Opus, Sonnet)"),
    ("specbridge.comm.diagnose.record", "ANALYZE", "diagnosis: communication analysis (Opus)"),
    ("specbridge.comm.diagnose.gate", "GATE", "diagnosis: quality gate (Opus)"),
    ("specbridge.comm.diagnose.repair", "REVISE", "diagnosis: isolate one choice (Opus)"),
    ("specbridge.comm.diagnose.repair", "REREVIEW", "diagnosis: re-review after repair"),
    ("specbridge.comm.common.decisions", "MATCH", "library: place unplaced candidates (Opus)"),
    ("specbridge.comm.common.decisions", "REVIEW", "library: review a placement (Sonnet)"),
    ("specbridge.comm.common.decisions", "TYPE_REQS", "library: type requirements (Opus)"),
    ("specbridge.comm.common.decisions", "REVIEW_REQS", "library: check the typing (Sonnet)"),
    ("specbridge.comm.diagnose.library", "RETRIEVED", "families: retrieved real example shown to the writer"),
    ("specbridge.comm.transfer.choice_points", "PROPOSE", "families: choice-point proposer (Opus)"),
    ("specbridge.comm.transfer.choice_points", "REPAIR", "families: repair of failed points (Opus)"),
    ("specbridge.comm.transfer.choice_points", "REVIEW", "families: blind review of points (Opus, Sonnet)"),
    ("specbridge.comm.transfer.render", "WRITE", "families: plan + precise A + precise B + open (Opus)"),
    ("specbridge.comm.transfer.render", "FIDEL", "families: fidelity review (Opus, Sonnet)"),
    ("specbridge.comm.transfer.render", "INTERPB", "families: interpretation review (Opus, Sonnet)"),
    ("specbridge.comm.transfer.render", "DIRECT", "ablation: direct generation (Opus)"),
    ("specbridge.comm.transfer.disclose", "INSTRUCTION", "disclosure: the frozen instruction (all solvers)"),
    ("specbridge.comm.transfer.disclose", "PLAIN", "disclosure: matched plain single-call control"),
    ("specbridge.comm.transfer.disclose", "JUDGE", "disclosure: rubric judge (Opus, blind to the model)"),
    ("specbridge.comm.transfer.disclose", "ALTJUDGE", "disclosure: alternative-support judge (Opus)"),
]


def where(mod, attr):
    src, start = inspect.getsourcelines(mod)
    for i, line in enumerate(src):
        if re.match(r"^%s\s*=" % re.escape(attr), line): return "%s:%d" % (os.path.relpath(inspect.getsourcefile(mod)), start + i if start else i + 1)
    return os.path.relpath(inspect.getsourcefile(mod))


L = ["# Prompts, verbatim from the code (extracted by specbridge.report.methods)\n",
     "Each block is the exact template string; `%s` slots are filled with schema, documentation, the task and the like. The sha256 prefix identifies the version.\n"]
index = []
for modname, attr, role in PROMPTS:
    mod = importlib.import_module(modname); txt = getattr(mod, attr, None)
    if not isinstance(txt, str): L.append("## %s.%s -- NOT FOUND\n" % (modname, attr)); continue
    sha = hashlib.sha256(txt.encode()).hexdigest()[:12]; loc = where(mod, attr)
    index.append((attr, role, loc, sha, len(txt)))
    L += ["## %s -- %s\n" % (attr, role), "`%s` · sha256 `%s` · %d characters\n" % (loc, sha, len(txt)), "```text", txt.rstrip(), "```\n"]
# THE DEFAULTS NOTE (R8.1) is built from BIRD train at run time (prior.note); the text as run is the frozen NOTE.md.
_nf = "out/prior/bird600/NOTE.md"
if os.path.exists(_nf):
    txt = open(_nf).read(); sha = hashlib.sha256(txt.encode()).hexdigest()[:12]
    index.append(("NOTE", "telling the solver the defaults: placed before every question (all four solvers), as run", _nf, sha, len(txt)))
    L += ["## NOTE -- telling the solver the defaults: placed before every question (all four solvers), as run\n",
          "`%s` (built by `specbridge.comm.diagnose.prior.note` from BIRD train) · sha256 `%s` · %d characters\n" % (_nf, sha, len(txt)), "```text", txt.rstrip(), "```\n"]
L.insert(2, "| prompt | role | location | sha256 |\n|---|---|---|---|\n" + "\n".join("| %s | %s | `%s` | `%s` |" % (a, r, l, s) for a, r, l, s, _n in index) + "\n")
open(OUT + "/PROMPTS.md", "w").write("\n".join(L) + "\n")


def const(modname, names):
    mod = importlib.import_module(modname); return {n: getattr(mod, n) for n in names if hasattr(mod, n)}


def sh(cmd):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip().splitlines()[0]
    except Exception as e: return "unavailable (%s)" % type(e).__name__


P = {
    "grammar (specbridge.pd.structures.compose)": const("specbridge.pd.structures.compose", ["VERSION", "A_MAX", "S_MAX", "M_MAX", "BATCH"]),
    "precise wording (specbridge.comm.verbal.precise)": const("specbridge.comm.verbal.precise", ["MODEL", "REVIEW_MODEL", "REVIEW_STAGES", "BUDGET", "BATCH", "WORKERS", "VARIANT", "CHECK_VERSION", "REVIEW_MODE"]),
    "disclosure (specbridge.comm.transfer.disclose)": const("specbridge.comm.transfer.disclose", ["PROMPT_SHA", "WORDINGS"]),
    "transfer evaluation (specbridge.comm.transfer.evaluate)": const("specbridge.comm.transfer.evaluate", ["BSIZE"]),
    "diagnosis (specbridge.comm.diagnose.batches)": const("specbridge.comm.diagnose.batches", ["MODEL", "REPEATS"]),
    "codex sealing (specbridge.pd.ask)": const("specbridge.pd.ask", ["CODEX_EFFORT", "_CODEX_OFF"]),
}
P["hidden defaults (specbridge.comm.diagnose.inclination)"] = {**const("specbridge.comm.diagnose.inclination", ["MIN_PER_DB", "IMPORTED"]),
    "minimum silent references for a group to be drawn (figures.MIN_SPLIT_N)": const("specbridge.report.figures", ["MIN_SPLIT_N"]).get("MIN_SPLIT_N"),
    "cue word lists": "inclination.CUES (verbatim in the module)"}
P["telling the solver the defaults (specbridge.comm.diagnose.prior)"] = {**const("specbridge.comm.diagnose.prior", ["N", "SEED", "OUT"]),
    "solvers": const("specbridge.report.exhibit_data", ["NOTE_MODELS"]).get("NOTE_MODELS"), "questions per call": 1, "rounds": 6, "runs per arm": 1}
sig = lambda f: str(inspect.signature(f))
from specbridge.comm.common import solve as SV, db as DBM
P["solver (specbridge.comm.common.solve)"] = {"solve signature": sig(SV.solve), "exploration query limit": "5000 ms (solve.py, DB.execute(..., ms=5000))", "rows shown per query": 20,
                                              "final query limit": "60000 ms (db.rows default)", "db.rows signature": sig(DBM.rows), "db.execute signature": sig(DBM.execute)}
P["seeds and splits"] = {"BIRD held-out": "out/comm_library/heldout_eval.json (fixed 2026-10-01, seed 20261001 in tasks.split)",
                         "Spider split": json.load(open("out/comm_library/spider_split.json"))["seed"],
                         "eval12 request seed": json.load(open("out/corpora/request_eval12-1.json"))["seed"],
                         "coverage seeds": "pool 1; control 1-3; preferences 1; requirements 1 (coverage.py)",
                         "family selection seed (RENDER_SEED default)": 20261003, "ablation pairs seed": 20261004,
                         "disclosure allocation seed": json.load(open("out/transfer/eval12-v2/render/disclose/sample.json"))["seed"],
                         "bootstrap": "B=2000, seed 20261003 (specbridge.report.exhibit_data)"}
P["environment at extraction"] = {"git commit": sh(["git", "rev-parse", "--short", "HEAD"]), "claude CLI": sh(["claude", "--version"]), "codex CLI": sh(["codex", "--version"]),
                                  "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                                  "note": "versions used by past runs are not logged per run (claude 2.1.287 -> 2.1.289, codex 0.147 -> 0.160 over the work); resolved model ids not logged"}
L = ["# Parameters, budgets, seeds and versions (extracted from the code by specbridge.report.methods)\n"]
for k, v in P.items():
    L += ["## %s\n" % k, "| name | value |", "|---|---|"] + ["| %s | `%s` |" % (n, json.dumps(x, default=str) if not isinstance(x, str) else x) for n, x in v.items()] + [""]
open(OUT + "/PARAMETERS.md", "w").write("\n".join(L) + "\n")
print("prompts: %d; parameter groups: %d" % (len(index), len(P)))
