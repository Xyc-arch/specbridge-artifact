"""specbridge.comm.diagnose.inclination -- which way does a benchmark's REFERENCE SQL lean on each open decision?

For each decision kind with a syntactic signature, every reference query where the decision ARISES is put on one side,
read from the SQL alone (sqlglot; no model):

    ties_and_selection   an extreme is picked: ORDER BY .. LIMIT 1 (one row)  vs  = (SELECT MIN/MAX ..) (every tied row)
    counting_unit        COUNT returned over a join: COUNT(DISTINCT ..) (entities)     vs  COUNT(x)/COUNT(*) (rows)
    population_scope     a join: inner                                        vs  LEFT/RIGHT/FULL (keeps unmatched)
    missing_values       ORDER BY <non-aggregate> LIMIT 1: col IS NOT NULL filtered       vs  not filtered (SQLite sorts NULL first ASC)
    calculation_scale    the question says percent/percentage: * 100          vs  a fraction
    calculation_division a division: operand CAST to REAL / * 1.0             vs  no explicit cast (integer division if both operands are INTEGER)
    output_extreme       ORDER BY .. LIMIT 1: the sort expression is also returned vs not
    output_duplicates    a join, no aggregate: SELECT DISTINCT                vs  duplicates kept

Inclination = the share of each side, per split and per database. Train and dev use DIFFERENT databases, so a habit that
holds in both carries over to unseen databases. The library's open records (raise = true) of the same kind are placed
by the same rule: does the reference of a question that leaves the decision open follow the benchmark's majority? A record that follows it is a convention the question did not state; one against it is a choice
the benchmark itself does not make consistently.

AUTHOR GROUPS (measure_groups): the same count among SILENT questions (no wording cue for the decision), by who wrote
the SQL -- BIRD, Spider's own data, and the two families of datasets Spider imported (train_others.json). A default
shared by train and dev of one group is learnable from that group's training data; a group that flips it shows the
reading is set by the authors, not by the words.

    python -m specbridge.comm.diagnose.inclination      -> out/comm_library/inclination.json, INCLINATION.md
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import sqlglot
from sqlglot import exp

BIRD = Path("dev_unzipped/dev_20240627/dev.json")
SPIDER = Path("spider_data/spider_data/dev.json")
LIBRARY = Path("library/examples.jsonl")
OUT = Path("out/comm_library")

# (kind, library type it measures, side A, side B)
KINDS = [
    ("ties_and_selection", "ties_and_selection", "one row (LIMIT 1)", "every tied row (= MIN/MAX)"),
    ("counting_unit", "counting_unit", "distinct entities", "rows"),
    ("population_scope", "population_scope", "inner join", "outer join"),
    ("missing_values", "missing_values", "NULL filtered", "NULL not filtered"),
    ("calculation_scale", "calculation", "times 100", "fraction"),
    ("calculation_division", "calculation", "explicit REAL (CAST or 1.0)", "no explicit cast"),
    ("output_extreme", "output_form", "sort value returned", "sort value not returned"),
    ("output_duplicates", "output_form", "DISTINCT", "duplicates kept"),
    ("boundary_between", "time_scope", "'between' strict", "'between' inclusive"),
    ("boundary_open", "time_scope", "after/before/over/above/under/below strict", "the same, inclusive"),
    ("text_match", "value_representation", "exact match (=)", "loose match (LIKE '%...%')"),
]
TRIG = re.compile(r"\b(between|after|before|over|above|under|below)\b", re.I)


def _str(n):
    """A string value: a string literal, or a bare double-quoted name (Spider writes "texas"; SQLite reads it as a string
    when no column has that name)."""
    if isinstance(n, exp.Literal) and n.is_string:
        return n.this
    if isinstance(n, exp.Column) and not n.table and n.this.args.get("quoted"):
        return n.name
    return None


def _value(n):
    return isinstance(n, exp.Literal) or _str(n) is not None or (isinstance(n, (exp.Neg, exp.Cast)) and isinstance(n.this, exp.Literal))


def _shifted(c, question):
    """A strict bound whose value is one step outside a value the question states: an integer one away, or a date one day away."""
    import datetime
    v = _str(c.right) or _str(c.left) or (c.right.this if isinstance(c.right, exp.Literal) else c.left.this if isinstance(c.left, exp.Literal) else None)
    if v is None: return False
    up = isinstance(c, exp.GT) == isinstance(c.left, exp.Column)          # col > v or v < col: a lower bound, so the stated value is v + 1
    try: return re.search(r"(?<![\d.])%d(?![\d.])" % (int(v) + (1 if up else -1)), question) is not None
    except ValueError: pass
    try: d = datetime.date.fromisoformat(str(v)[:10]) + datetime.timedelta(days=1 if up else -1)
    except ValueError: return False
    return d.isoformat() in question


PERCENT = re.compile(r"\bper ?cent(age)?s?\b|%", re.I)


def _parse(sql):
    try:
        return sqlglot.parse_one(sql, read="sqlite")
    except Exception:
        return None


def _limit_one(sel):
    lim = sel.args.get("limit")
    e = lim and lim.args.get("expression")
    return isinstance(e, exp.Literal) and e.this == "1"


def _selects(tree):
    return [s for s in tree.find_all(exp.Select)]


def _joins(sel):
    return sel.args.get("joins") or []


def _has_join(sel):
    frm = sel.args.get("from")
    comma = frm is not None and len(frm.expressions or []) > 1
    return bool(_joins(sel)) or comma


def _cols(node):
    return {c.name.lower() for c in node.find_all(exp.Column)}


def sides(sql, question):
    """{kind: 'A' | 'B'} for every kind whose decision arises in this reference query."""
    tree = _parse(sql)
    if tree is None:
        return {}
    out = {}
    sels = _selects(tree)
    for sel in sels:
        order = sel.args.get("order")
        if order and _limit_one(sel):
            out.setdefault("ties_and_selection", "A")
            okeys = [o.this for o in order.expressions]
            plain = [k for k in okeys if not k.find(exp.AggFunc)]
            keys = set().union(*(_cols(k) for k in plain)) if plain else set()
            if keys:
                where = sel.args.get("where")
                filtered = where is not None and any(
                    isinstance(n.this, exp.Column) and n.this.name.lower() in keys and isinstance(n.parent, exp.Not)
                    for n in where.find_all(exp.Is))
                out.setdefault("missing_values", "A" if filtered else "B")
            if sel.expressions and not any(isinstance(e, exp.Star) for e in sel.expressions):
                shown = {(e.this if isinstance(e, exp.Alias) else e).sql().lower() for e in sel.expressions}
                aliases = {e.alias.lower() for e in sel.expressions if isinstance(e, exp.Alias)}
                ret = any(k.sql().lower() in shown or k.sql().lower() in aliases for k in okeys)
                out.setdefault("output_extreme", "A" if ret else "B")
        if _has_join(sel):
            kinds = [(j.args.get("side") or "").upper() for j in _joins(sel)]
            out.setdefault("population_scope", "B" if any(k in ("LEFT", "RIGHT", "FULL") for k in kinds) else "A")
            for c in (n for e in sel.expressions for n in e.find_all(exp.Count)):
                if c.find_ancestor(exp.Select) is sel:
                    out.setdefault("counting_unit", "A" if isinstance(c.this, exp.Distinct) else "B")
            if not any(isinstance(n, exp.AggFunc) for e in sel.expressions for n in e.walk()) and not sel.args.get("group"):
                out.setdefault("output_duplicates", "A" if sel.args.get("distinct") else "B")
    for sub in tree.find_all(exp.EQ, exp.GT, exp.LT, exp.GTE, exp.LTE):
        if any(isinstance(s, exp.Subquery) and s.find(exp.Max, exp.Min) for s in (sub.left, sub.right)):
            if isinstance(sub, exp.EQ):
                out["ties_and_selection"] = "B" if "ties_and_selection" not in out else out["ties_and_selection"]
    divs = list(tree.find_all(exp.Div))
    if divs:
        real = any(d.find(exp.Cast) or any(isinstance(l, exp.Literal) and not l.is_string and "." in l.this
                                           for l in d.find_all(exp.Literal)) for d in divs)
        out["calculation_division"] = "A" if real else "B"
        if PERCENT.search(question):
            hundred = any(isinstance(l, exp.Literal) and not l.is_string and float(l.this) == 100
                          for m in tree.find_all(exp.Mul) for l in m.find_all(exp.Literal))
            out["calculation_scale"] = "A" if hundred else "B"
    # boundaries: one trigger word in the question, decided by the comparison operator (silence: CUES)
    trig = [w.lower() for w in TRIG.findall(question)]
    if len(trig) == 1:
        betw = list(tree.find_all(exp.Between))
        cmps = [c for c in tree.find_all(exp.GT, exp.LT, exp.GTE, exp.LTE) if (_value(c.right) or _value(c.left)) and not c.find(exp.Subquery)]
        if trig[0] == "between":
            if betw and not cmps:
                out["boundary_between"] = "B"
            elif not betw and len(cmps) == 2 and len({isinstance(c, (exp.GT, exp.LT)) for c in cmps}) == 1:
                strict = isinstance(cmps[0], (exp.GT, exp.LT))
                # NOT between: "< lo OR > hi" excludes exactly the inclusive range, so its range reading is inclusive
                if cmps[0].find_ancestor(exp.Or) is not None and cmps[0].find_ancestor(exp.Or) is cmps[1].find_ancestor(exp.Or): strict = not strict
                # strict bounds moved one step out (> 1974 AND < 1981 for 1975 to 1980; dates one day out) select the inclusive range
                elif strict and all(_shifted(c, question) for c in cmps): strict = False
                out["boundary_between"] = "A" if strict else "B"
        elif not betw and len(cmps) == 1:
            out["boundary_open"] = "A" if isinstance(cmps[0], (exp.GT, exp.LT)) else "B"
    # text match: a word-like value compared exactly, or matched with LIKE '%...%' (not a date or number pattern)
    loose = [l for l in tree.find_all(exp.Like) if "%" in (_str(l.expression) or "") and not re.fullmatch(r"[\d\-/%:_ ]+", _str(l.expression))]
    exact = [e for e in tree.find_all(exp.EQ) if re.search(r"[A-Za-z]{3}", _str(e.expression) or "")]
    if loose or exact:
        out["text_match"] = "B" if loose else "A"
    return out


SPLITS = {"BIRD train": ("BIRD", lambda: [(r["db_id"], r["SQL"], r["question"] + " " + r.get("evidence", ""))
                                          for r in json.loads(Path("train_meta/train.json").read_text())]),
          "BIRD dev": ("BIRD", lambda: [(r["db_id"], r["SQL"], r["question"] + " " + r.get("evidence", ""))
                                        for r in json.loads(BIRD.read_text())]),
          "Spider train": ("Spider", lambda: [(r["db_id"], r["query"], r["question"]) for f in ("train_spider.json", "train_others.json")
                                              for r in json.loads((SPIDER.parent / f).read_text())]),
          "Spider dev": ("Spider", lambda: [(r["db_id"], r["query"], r["question"]) for r in json.loads(SPIDER.read_text())])}
# AUTHOR GROUPS: who wrote the SQL. Spider's train_others.json is imported from earlier datasets by other teams.
IMPORTED = {"imported: geo, restaurants": {"geo", "restaurants"}, "imported: academic, imdb, yelp": {"academic", "imdb", "yelp"},
            "imported: scholar": {"scholar"}}   # grouped by the earlier dataset each came from (2026-10-05: each group has its own habit)
_others = lambda dbs: lambda: [(r["db_id"], r["query"], r["question"]) for r in json.loads((SPIDER.parent / "train_others.json").read_text())
                               if r["db_id"] in dbs]
GROUPS = {"BIRD train": lambda: SPLITS["BIRD train"][1](), "BIRD dev": lambda: SPLITS["BIRD dev"][1](),
          "Spider train (own)": lambda: [(r["db_id"], r["query"], r["question"]) for r in json.loads((SPIDER.parent / "train_spider.json").read_text())],
          "Spider dev": lambda: SPLITS["Spider dev"][1](), **{g: _others(dbs) for g, dbs in IMPORTED.items()}}
# SILENT: a question counts for a decision only when its wording has none of these cues (read on samples, 2026-10-05:
# "type of"/"kind of" name an attribute, not a counting unit, so they are not cues).
DIST = re.compile(r"\b(distinct|different|unique)\b", re.I)
CUES = {"boundary_open": re.compile(r"\b(inclusive|exclusive|at least|at most|or more|or less|or (above|below|later|earlier|after|before)|"
                                   r"more than|less than|fewer than|greater than|higher than|lower than|exceed\w*)\b|>=|<=", re.I),"counting_unit": DIST, "output_duplicates": DIST,
        "ties_and_selection": re.compile(r"\b(all|every|each|tie[sd]?|any one|one of|a single|top \d+)\b", re.I),
        "missing_values": re.compile(r"\bnot (null|empty|blank|missing)\b|\b(available|recorded|known|non-?null)\b", re.I),
        "population_scope": re.compile(r"\b(including|even if|if any|with no|without|or not)\b", re.I),
        "boundary_between": re.compile(r"\b(inclusive|exclusive|at least|at most|or more|or less|or (above|below|later|earlier|after|before)|"
                                       r"more than|less than|fewer than|greater than|higher than|lower than|exceed\w*)\b|>=|<=", re.I),
        "text_match": re.compile(r"\b(contain\w*|includ\w*|start\w* with|begin\w* with|end\w* with|like|exact\w*|the word|mention\w*|keyword)\b", re.I),
        "output_extreme": re.compile(r"\bwhat (is|was|are|were) the (\w+ ){0,3}?(highest|lowest|maximum|minimum|largest|smallest|most|least|biggest|"
                                     r"greatest|fewest|oldest|youngest|earliest|latest|longest|shortest)\b|\bhow (much|many|long|old)\b", re.I)}
MIN_PER_DB = 5   # a database enters the per-database spread when the decision arises in at least this many of its references


def load():
    """{split: [(database, sql, question)]}"""
    return {name: f() for name, (_b, f) in SPLITS.items()}


def measure():
    """Per split and kind: counts on each side, per-database counts, and the library's open/settled records placed."""
    lib = [json.loads(l) for l in LIBRARY.open()]
    res = {}
    for name, rows in load().items():
        tot, per_db = defaultdict(Counter), defaultdict(lambda: defaultdict(Counter))
        for db, sql, q in rows:
            for k, s in sides(sql, q).items():
                tot[k][s] += 1
                per_db[k][db][s] += 1
        kinds = {}
        for kind, ltype, a, b in KINDS:
            lib_side = {"raise": Counter(), "silent": Counter()}
            for x in lib:
                if x["source"]["benchmark"] == name and x["type"] == ltype:
                    s = sides(x["gold_sql"], x["question"]).get(kind)
                    if s:
                        lib_side["raise" if x["raise"] else "silent"][s] += 1
            kinds[kind] = {"A": a, "B": b, "n_A": tot[kind]["A"], "n_B": tot[kind]["B"],
                           "per_db": {db: [c["A"], c["B"]] for db, c in sorted(per_db[kind].items())},
                           "library_open": dict(lib_side["raise"]), "library_settled": dict(lib_side["silent"])}
        res[name] = {"benchmark": SPLITS[name][0], "questions": len(rows), "databases": len({r[0] for r in rows}), "kinds": kinds}
    return res


def _rejected():
    """Silent references on the less common side that the author review rejected (human_supervision/review-reference-minority.md,
    parsed by specbridge.comm.diagnose.reference_split parse): the rule misread the SQL, the wording settles the choice, or the
    choice cannot arise. They leave every count, here and in Table 2."""
    import hashlib
    p = Path("human_supervision/reference_minority_verdicts.json")
    V = json.loads(p.read_text()) if p.exists() else {}
    return {k for k, v in V.items() if v.get("verdict") == "no"}, \
        lambda g, db, sql, q, k: hashlib.sha1(("%s|%s|%s|%s" % (g, db, sql, q)).encode()).hexdigest()[:10] + ":" + k


def measure_groups(usual=None):
    """Per author group and kind, among SILENT questions (no cue for that decision): counts on each side, per database.
    With usual = {kind: 'A'|'B'}: per group, questions with at least one silent decision among those kinds, and how many of
    them have a reference that goes against the usual reading on at least one. Rejected minority references are left out."""
    rej, rid = _rejected()
    res = {}
    for g, f in GROUPS.items():
        rows = f(); tot, per_db, cued = defaultdict(Counter), defaultdict(lambda: defaultdict(Counter)), defaultdict(Counter)
        qs = Counter()
        for db, sql, q in rows:
            silent = []
            for k, s in sides(sql, q).items():
                if k in CUES and CUES[k].search(q):
                    cued[k][s] += 1
                    continue
                if rej and rid(g, db, sql, q, k) in rej: continue
                tot[k][s] += 1
                per_db[k][db][s] += 1
                silent.append((k, s))
            if usual:
                mine = [(k, s) for k, s in silent if k in usual]
                if mine:
                    qs["with_silent"] += 1
                    qs["against_usual"] += any(s != usual[k] for k, s in mine)
        res[g] = {"questions": len(rows), "databases": len({r[0] for r in rows}), "per_question": dict(qs),
                  "kinds": {k: {"n_A": tot[k]["A"], "n_B": tot[k]["B"], "cued_A": cued[k]["A"], "cued_B": cued[k]["B"], "per_db": {db: [c["A"], c["B"]] for db, c in sorted(per_db[k].items())}}
                            for k, *_ in KINDS}}
    return res


def main():
    res = measure()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "inclination.json").write_text(json.dumps(res, indent=1))
    lines = ["# Inclination of the reference SQL (`python -m specbridge.comm.diagnose.inclination`)", "",
             "Side read from the reference SQL alone (no model). Share A = side A among references where the decision arises.",
             f"Databases mostly A: among databases with >= {MIN_PER_DB} such references. Library: the frozen library's records of",
             "the matching type, placed by the same rule (open = the question leaves the decision open).", ""]
    for name, r in res.items():
        lines += [f"## {name} ({r['questions']} questions, {r['databases']} databases)", "",
                  "| decision | side A | side B | A | B | share A | databases mostly A | library open A / B | settled A / B |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for k, v in r["kinds"].items():
            n = v["n_A"] + v["n_B"]
            dbs = [c for c in v["per_db"].values() if sum(c) >= MIN_PER_DB]
            lo, ls = v["library_open"], v["library_settled"]
            lines.append(f"| {k} | {v['A']} | {v['B']} | {v['n_A']} | {v['n_B']} | " + (
                f"{v['n_A'] / n:.3f} | {sum(c[0] > c[1] for c in dbs)} / {len(dbs)} | {lo.get('A', 0)} / {lo.get('B', 0)} | "
                f"{ls.get('A', 0)} / {ls.get('B', 0)} |" if n else "- | - | - | - |"))
        lines.append("")
    G = measure_groups()
    lines += ["## By author group, silent questions only (no wording cue for the decision)", "",
              "| decision | " + " | ".join(G) + " |", "|---|" + "---|" * len(G)]
    for k, a, *_ in ((k, a) for k, _t, a, _b in KINDS):
        lines.append(f"| {k} (A = {a}) | " + " | ".join(
            f"{v['kinds'][k]['n_A']}/{v['kinds'][k]['n_A'] + v['kinds'][k]['n_B']}" for v in G.values()) + " |")
    (OUT / "INCLINATION.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
