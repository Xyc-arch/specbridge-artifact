"""CARRY A CLARIFICATION BY EDITING THE REQUEST, NOT BY REWRITING IT (Section 7.3 of the paper).

Given an open request and the description of one reading, four request texts go to the same SQL prompt:
  (a) original   the benchmark's specific request for that reading (the reference)
  (b) interpret  the open request rewritten by the model as one interpretation (DtP's interpretation prompt, told the reading)
  (c) edit       the open request unchanged, followed by the one-sentence reading description   <- the recommended design
  (d) condense   the open request condensed into a standalone question (LangChain's condense-question prompt)
The paper finds (c) within 0.5 points of (a), and (b) and (d) 8.2 and 11.0 points below (c), pooled over four models; the rewrites
mostly drop another requirement (an output column, a formula, a join), not the choice.

    from methods.clarify import edit
    request = edit(open_request, reading)                      # no model call

    python methods/clarify.py --model sonnet [--n 120]          # rerun the test on accepted benchmark sets (needs model access)"""
import json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
from prompts import PLAIN, TELL, CONDENSE
from third_party import dtp_prompts as DTP

_MARK = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s*")


def edit(open_request, reading):
    """(c): the request unchanged, plus one clause."""
    return open_request.rstrip() + " " + reading


def interpret(open_request, reading, schema, docs, ask):
    """(b): one interpretation written by the model with DtP's prompt, told the intended meaning."""
    t = ask(DTP.user_message_interpr_ambig.format("DATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s" % (schema, docs), open_request) + TELL.format(reading)) or ""
    lines = [_MARK.sub("", x).strip() for x in t.splitlines() if _MARK.sub("", x).strip()]
    return lines[0] if lines else ""


def condense(open_request, reading, ask):
    """(d): the conversational-retrieval condense step, with the open request as the earlier turn and the reading as the follow-up."""
    return (ask(CONDENSE.format(open_request, reading)) or "").strip().split("Standalone question:")[-1].strip()


def answer(request, schema, docs, ask):
    m = re.search(r"\{.*\}", ask(PLAIN % (schema, docs, request)) or "", re.S)
    try: return json.loads(m.group(0)).get("sql")
    except Exception: return None


if __name__ == "__main__":
    import argparse
    from benchmark.score import load, run, matches
    from methods.models import make_ask
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20261026); ap.add_argument("--out", default="clarify_results.jsonl")
    a = ap.parse_args(); ask = make_ask(a.model); S = load()
    jobs = [(sid, r) for sid in sorted(S) for r in "AB"]; random.Random(a.seed).shuffle(jobs)
    right = {v: 0 for v in "abcd"}; n = 0
    with open(a.out, "w") as f:
        for sid, r in jobs[:a.n]:
            s = S[sid]; c = s["context"]; reading = s["readings"][r]; op = s["requests"]["open"]
            texts = {"a": s["requests"]["specific_" + r], "b": interpret(op, reading, c["schema"], c["documentation"], ask),
                     "c": edit(op, reading), "d": condense(op, reading, ask)}
            o = {"id": sid, "reading": r}
            for v, t in texts.items():
                sql = answer(t, c["schema"], c["documentation"], ask) if t else None; ok = r in matches(s, run(s, sql))
                o[v] = {"request": t, "sql": sql, "right": ok}; right[v] += ok
            n += 1; f.write(json.dumps(o) + "\n")
    print("readings %d: " % n + ", ".join("(%s) %.1f%%" % (v, 100 * right[v] / max(1, n)) for v in "abcd"))
