"""THE AUTHOR'S REVIEW TABLE (human_supervision/review-307-author-approve.md, completed 2026-10-16; its first 215 rows are the
main sets, reviewed first): one row per request set, read by a person, and the verdicts parsed from it
(human_supervision/verdicts.json, read by specbridge.comm.transfer.reviewed).
    python -m specbridge.comm.transfer.review_table append <render dir>   add the sets of <render dir>/eval/frozen.json not yet in
                                                                           the table, numbered on, with the verdict left to fill
    python -m specbridge.comm.transfer.review_table parse [table]          verdicts.json from every row whose verdict is filled
A row's verdict answers: could a reasonable analyst mean either reading? (yes / no / unsure)."""
import json, os, sys

TABLE = "human_supervision/review-307-author-approve.md"   # the author's completed review of all 307 sets
VERDICTS = "human_supervision/verdicts.json"
VALID = ("yes", "no", "unsure")


def rows(path=TABLE):
    """[(cells)] of the table body: split on ' | ' between the outer bars (no cell contains ' | ')."""
    out = []
    for l in open(path).read().split("\n")[2:]:
        if l.startswith("|"): out.append([c.strip() for c in l.strip().strip("|").split(" | ")])
    return out


def parse(path=TABLE):
    V = {}
    for r in rows(path):
        v = r[8].lower()
        if v in VALID: V[r[2]] = {"verdict": v, "type": r[1], "note": r[9]}
    old = json.load(open(VERDICTS)) if os.path.exists(VERDICTS) else {}
    changed = [k for k in old if k in V and V[k] != old[k]] + [k for k in old if k not in V]
    json.dump(V, open(VERDICTS, "w"), indent=1)
    print("verdicts %d (%s); changed or removed from the earlier file: %d %s" % (len(V), dict(__import__("collections").Counter(x["verdict"] for x in V.values())), len(changed), changed[:5]))


def differ(a, b):
    """How the two readings' answers differ, in the table's words."""
    ka, kb = {tuple(map(str, r[:1])) for r in a}, {tuple(map(str, r[:1])) for r in b}
    s = "A: %d rows, B: %d rows" % (len(a), len(b))
    if a and b and a[0] != b[0]: s += "; first row differs"
    only = len(ka ^ kb)
    if only: s += "; %d row keys in only one answer" % only
    best = None
    ia = {tuple(map(str, r[:1])): r for r in a}
    for r in b:
        x = ia.get(tuple(map(str, r[:1])))
        if not x: continue
        for u, v in zip(x, r):
            if isinstance(u, (int, float)) and isinstance(v, (int, float)) and u != v:
                rel = abs(u - v) / max(abs(u), abs(v))
                if best is None or rel > best[2]: best = (u, v, rel)
    s += "; largest value change: %.4g (A) vs %.4g (B), %.2g%%" % (best[0], best[1], 100 * best[2]) if best else "; no shared value changes"
    return s


def append(rd):
    F = json.load(open(rd + "/eval/frozen.json"))["cases"]; W = json.load(open(rd + "/written.json"))
    lines = open(TABLE).read().rstrip("\n").split("\n"); have = {r[2] for r in rows()}; n = len(rows())
    width = [len(c) for c in lines[1].strip("|").split("|")]
    cell = lambda x: " ".join(str(x).split()).replace("|", "/")
    new = []
    for c in sorted(F, key=lambda c: (c["type"], c["database"], c["case"])):
        sid = c["case"].split("-")[-1]
        if sid in have: continue
        w = W[c["case"]]; n += 1
        new.append("| " + " | ".join(cell(x) for x in [n, c["type"].replace("_", " "), sid, c["database"], c["texts"]["open"], w["reading_A"], w["reading_B"],
                                                     differ(c["answer_A"], c["answer_B"] or []), "", "", "new"]) + " |")
    open(TABLE, "w").write("\n".join(lines + new) + "\n")
    print("appended %d sets (rows %d-%d); fill the column 'Could a reasonable analyst mean either reading?' with yes / no / unsure, then run parse" % (len(new), n - len(new) + 1, n))


if __name__ == "__main__":
    a = sys.argv[1:]
    {"parse": lambda: parse(*a[1:]), "append": lambda: append(a[1])}[a[0]]()
