"""Checks of the released benchmark and methods (no model calls).    python tests/test_release.py"""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from methods import prompts as P
from methods.disclose import disclose
from methods.clarify import edit
from benchmark.score import load, run, matches

def test_prompts_match_experiment_code():
    from specbridge.comm.transfer import disclose as X, rewrite as RW, ambrosia as AM
    assert P.DETECT == AM.DETECT and P.PLAIN == X.PLAIN and P.INSTRUCTION == X.INSTRUCTION and P.TELL == RW.TELL and P.CONDENSE == RW.CONDENSE

def test_disclose_splits_and_merges():
    S = load(); s = S[sorted(S)[0]]; db = os.path.join("benchmark", "databases", s["database"] + ".sqlite")
    A, B = s["requests"]["specific_A"], s["requests"]["specific_B"]
    def ask(p):
        if '"readings"' in p: return json.dumps({"readings": [A, B, A]})          # a duplicate reading must be merged by execution
        return s["sql"]["A"] if p.rstrip().endswith(A.rstrip()) else s["sql"]["B"]
    out = disclose(s["requests"]["open"], s["context"]["schema"], db, ask)
    assert out["calls"] == 4 and len(out["alternatives"]) == 1
    assert "A" in matches(s, run(s, out["main"])) and "B" in matches(s, run(s, out["alternatives"][0]))

def test_edit_reproduces_the_experiment_texts():
    S = load(accepted_only=False); n = 0
    for f in sorted(glob.glob("out/rewrite/runs/*/*.json"))[:200]:
        o = json.load(open(f)); s = S[o["case"].split("-")[-1]]
        assert edit(s["requests"]["open"], o["description"]) == o["c"]["request"]; n += 1
    assert n > 0

if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"): f(); print("ok  ", k)
