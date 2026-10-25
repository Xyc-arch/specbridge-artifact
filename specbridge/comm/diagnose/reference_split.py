"""specbridge.comm.diagnose.reference_split -- for EVERY library type with a syntactic signature, how do BIRD and Spider
references split between its two readings? (2026-10-17, Table 2 of the paper.)

The seven choices of specbridge.comm.diagnose.inclination are pooled as they are. This adds the library types inclination
does not read, each decided from the reference SQL and the schema (sqlglot, tables.json; no model), among SILENT questions
(no wording cue in CUES):

    comparison_quantifier  the question says "than any": exceeds every value (> MAX, < MIN, ALL)  vs  at least one (> MIN, < MAX, ANY)
    negated_membership     a negated question with a join: no matching record (NOT IN, NOT EXISTS, EXCEPT)  vs  some non-matching
                           record (<> on a joined child table)
    aggregation_level      an entity ranked over a one-to-many join: by one row's value (ORDER BY a column)  vs  by a group value
                           (GROUP BY, ORDER BY an aggregate)
    condition_linkage      two or more conditions on a joined child table: on the same row (AND in one alias)  vs  on separate rows
                           (INTERSECT, or the table joined twice with conditions on each)
    relationship_role      two child tables of one parent, also linked by a third table: joined through the shared parent  vs
                           through the link table
    referent_column        a column named in the question exists in two tables of the query: the first table's  vs  a joined one's
    calculation            the question says percent: times 100 vs a fraction (inclination's calculation_scale)

    python -m specbridge.comm.diagnose.reference_split    -> out/paper/data/tab2_references.json
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

from sqlglot import exp
from specbridge.comm.diagnose import inclination as I

OUT = Path("out/paper/data/tab2_references.json"); LIB = Path("library/examples.jsonl")
SCHEMAS = ("dev_unzipped/dev_20240627/dev_tables.json", "train_meta/train_tables.json", "spider_data/spider_data/tables.json")
# (kind, library type, side A, side B)
KINDS = [("comparison_quantifier", "comparison_quantifier", "exceeds every value", "exceeds at least one"),
         ("negated_membership", "negated_membership_scope", "no matching record", "some non-matching record"),
         ("aggregation_level", "aggregation_level", "one row's value", "a group value"),
         ("condition_linkage", "condition_linkage", "same row", "separate rows"),
         ("relationship_role", "relationship_role", "through the shared parent", "through the link table"),
         ("referent_column", "referent_column", "first table's column", "a joined table's column")]
ANY = re.compile(r"\bthan (that of |those of )?any\b", re.I)
NEG = re.compile(r"\b(not|no|never|without|none)\b|n't\b", re.I)
CUES = {"comparison_quantifier": re.compile(r"\bthan (all|every|each)\b|\bat least one\b", re.I),
        "negated_membership": re.compile(r"\b(at all|none of|any)\b", re.I),
        "aggregation_level": re.compile(r"\b(total|sum|summed|combined|altogether|overall|in all|each|per|average|mean)\b", re.I),
        "condition_linkage": re.compile(r"\b(both|same|at the same time|simultaneously|also|as well|either)\b", re.I),
        "relationship_role": None, "referent_column": None}   # these two are silenced per query (the link or the table named)


def _nat(s):
    return re.sub(r"[_\s]+", " ", s.lower()).strip()


def schemas():
    S = {}
    for f in SCHEMAS:
        for d in json.loads(Path(f).read_text()):
            t = [x.lower() for x in d["table_names_original"]]; c = d["column_names_original"]
            col = lambda i: (t[c[i][0]], c[i][1].lower())
            cols, num = defaultdict(set), set()
            for i, (ti, n) in enumerate(c):
                if ti >= 0:
                    cols[t[ti]].add(n.lower())
                    if d["column_types"][i] in ("number", "integer", "real"): num.add((t[ti], n.lower()))
            pks = set()
            for p in d["primary_keys"]:
                if not isinstance(p, list) or len(p) == 1: pks.add(col(p[0] if isinstance(p, list) else p))   # sole keys only
            S.setdefault(d["db_id"], {"cols": cols, "pk": pks, "fk": [(col(a), col(b)) for a, b in d["foreign_keys"]], "num": num})
    return S


def _tables(sel):
    """alias -> table for the tables in this SELECT's FROM and JOINs (not inside subqueries), in order."""
    out = []
    frm = sel.args.get("from_") or sel.args.get("from")
    for n in ([frm.this] + list(frm.expressions or []) if frm else []) + [j.this for j in sel.args.get("joins") or []]:
        if isinstance(n, exp.Table): out.append(((n.alias_or_name or n.name).lower(), n.name.lower()))
    return out


def _own(node, sel):
    return node.find_ancestor(exp.Select) is sel


def _table_of(c, al, sch):
    if c.table: return al.get(c.table.lower())
    hit = [t for t in dict.fromkeys(al.values()) if c.name.lower() in sch["cols"].get(t, ())]
    return hit[0] if len(hit) == 1 else None


def _join_col(sel, alias, al, sch):
    """The column by which `alias` is joined in this SELECT (its side of an ON equality), or None."""
    for j in sel.args.get("joins") or []:
        on = j.args.get("on")
        for e in (on.find_all(exp.EQ) if on else []):
            for c in (e.left, e.right):
                if isinstance(c, exp.Column) and (c.table or "").lower() == alias: return (al[alias], c.name.lower())
    return None


def _join_pair(sel, alias):
    """Both column names of the ON equality that joins `alias`: which relation it is joined by."""
    for j in sel.args.get("joins") or []:
        on = j.args.get("on")
        for e in (on.find_all(exp.EQ) if on else []):
            if isinstance(e.left, exp.Column) and isinstance(e.right, exp.Column):
                for a, b in ((e.left, e.right), (e.right, e.left)):
                    if (a.table or "").lower() == alias: return (a.name.lower(), b.name.lower())
    return None


def _child(sel, alias, al, sch, fk_ref):
    """The alias is the many side of its join: joined by a foreign key that is not its primary key."""
    jc = _join_col(sel, alias, al, sch)
    return jc is not None and jc in fk_ref and jc not in sch["pk"]


def _value(n):
    return isinstance(n, exp.Literal) or I._str(n) is not None


def sides(db, sql, q, S):
    tree = I._parse(sql); sch = S.get(db)
    if tree is None or sch is None: return {}
    out = {}
    fk_ref = defaultdict(set)                                   # (table, col) -> parents it references
    for a, b in sch["fk"]: fk_ref[a].add(b)
    # quantifier: "than any", decided by the aggregate the comparison uses
    if ANY.search(q):
        for c in tree.find_all(exp.GT, exp.GTE, exp.LT, exp.LTE):
            sub = c.right if isinstance(c.right, (exp.Subquery, exp.Any, exp.All)) else c.left if isinstance(c.left, (exp.Subquery, exp.Any, exp.All)) else None
            if sub is None: continue
            up = isinstance(c, (exp.GT, exp.GTE)) == (sub is c.right)          # value > the subquery's values
            if isinstance(sub, exp.All): out["comparison_quantifier"] = "A"
            elif isinstance(sub, exp.Any): out["comparison_quantifier"] = "B"
            elif sub.find(exp.Max) or sub.find(exp.Min):
                out["comparison_quantifier"] = "A" if bool(sub.find(exp.Max)) == up else "B"
    top = tree.find(exp.Select); top_first = (_tables(top) or [(None, None)])[0][1] if top else None
    if NEG.search(q):
        negs = [n.args.get("query") for n in tree.find_all(exp.In) if isinstance(n.parent, exp.Not) and n.args.get("query")] + \
               [n for n in tree.find_all(exp.Exists) if isinstance(n.parent, exp.Not)] + [x.expression for x in tree.find_all(exp.Except)]
        if any(t.name.lower() != top_first for n in negs if n is not None for t in n.find_all(exp.Table)):
            out["negated_membership"] = "A"
    for sel in tree.find_all(exp.Select):
        tl = _tables(sel); al = dict(tl)
        if len(tl) < 2: continue
        first = tl[0][1]; where = sel.args.get("where")
        # negation over a join
        if NEG.search(q) and any(_own(n, sel) and isinstance(n.left, exp.Column) and _value(n.right)       # in WHERE, CASE or HAVING
                                 and (n.left.table or "").lower() in al and _child(sel, n.left.table.lower(), al, sch, fk_ref)
                                 for n in sel.find_all(exp.NEQ)):
            out.setdefault("negated_membership", "B")
        # aggregation level: rank an entity of one table by values of another
        order, grp = sel.args.get("order"), sel.args.get("group")
        if order and sel.args.get("limit"):
            key = order.expressions[0].this
            kt = {_table_of(c, al, sch) for c in key.find_all(exp.Column)}
            rt = {_table_of(c, al, sch) for e in sel.expressions for c in e.find_all(exp.Column)}
            kc = [c for c in key.find_all(exp.Column)]
            ka = {a for a, t in tl if t in kt}
            many = any(_child(sel, a, al, sch, fk_ref) for a in ka) or any((c.table or "").lower() in al and _child(sel, c.table.lower(), al, sch, fk_ref) for c in kc)
            numeric = kc and all((_table_of(c, al, sch), c.name.lower()) in sch["num"] and not c.name.lower().endswith("id") for c in kc)
            if len(kt) == 1 and None not in kt and rt and None not in rt and not (kt & rt) and many and numeric:
                if not key.find(exp.AggFunc) and not grp: out.setdefault("aggregation_level", "A")
                elif key.find(exp.Sum, exp.Avg) and grp: out.setdefault("aggregation_level", "B")
        # condition linkage: conditions on a child table, one row or separate rows
        names = [t for _, t in tl]
        conds = defaultdict(set)              # alias -> columns it is filtered on
        if where is not None and not where.find(exp.Or):
            for n in where.find_all(exp.EQ, exp.GT, exp.LT, exp.GTE, exp.LTE, exp.Like, exp.NEQ):
                if _own(n, sel) and isinstance(n.left, exp.Column) and _value(n.right):
                    conds[(n.left.table or "").lower()].add(n.left.name.lower())
        # separate rows: one table joined twice by the same relation, filtered on DIFFERENT columns (the same column with two
        # values cannot hold on one row, so there is no choice)
        twice = False
        for t in set(names):
            als = [a for a, tt in tl if tt == t and conds[a]]
            if len(als) > 1 and len({_join_pair(sel, a) for a in als}) == 1 and len({frozenset(conds[a]) for a in als}) == len(als) \
                    and not set.intersection(*(conds[a] for a in als)):
                twice = True
        if twice: out["condition_linkage"] = "B"
        else:
            for a, t in tl[1:]:
                if len(conds.get(a, ())) >= 2 and names.count(t) == 1 and _child(sel, a, al, sch, fk_ref): out.setdefault("condition_linkage", "A")
        # relationship role: two children of one parent that a third table also links
        for j in sel.args.get("joins") or []:
            on = j.args.get("on")
            for e in (on.find_all(exp.EQ) if on else []):
                if not (isinstance(e.left, exp.Column) and isinstance(e.right, exp.Column)): continue
                x, y = (_table_of(e.left, al, sch), e.left.name.lower()), (_table_of(e.right, al, sch), e.right.name.lower())
                if None in (x[0], y[0]) or x[0] == y[0]: continue
                par = fk_ref.get(x, set()) & fk_ref.get(y, set())
                links = [l for l in sch["cols"] if l not in (x[0], y[0]) and any(p[0] == x[0] for (lt, _), p in sch["fk"] if lt == l)
                         and any(p[0] == y[0] for (lt, _), p in sch["fk"] if lt == l)]
                if par and links and not any(_nat(l) in _nat(q) for l in links):
                    out.setdefault("relationship_role", "B" if any(l in names for l in links) else "A")
        # referent column: a named column that two tables of the query have
        for c in sel.find_all(exp.Column):
            if not _own(c, sel) or not c.table: continue
            n = c.name.lower(); has = [t for t in dict.fromkeys(names) if n in sch["cols"].get(t, ())]
            if len(has) < 2 or any((t, n) in sch["pk"] or (t, n) in fk_ref for t in has) or len(n) < 3: continue
            if not re.search(r"\b%s\b" % re.escape(_nat(n)), _nat(q)): continue
            if any(re.search(r"\b%s %s\b|\b%s of (the )?%s\b" % (re.escape(_nat(t)), re.escape(_nat(n)), re.escape(_nat(n)), re.escape(_nat(t))), _nat(q)) for t in has): continue
            out.setdefault("referent_column", "A" if _table_of(c, al, sch) == first else "B")
    for x in tree.find_all(exp.Intersect):
        l, r = ({t.name.lower() for t in side.find_all(exp.Table)} for side in (x.this, x.expression))
        cl, cr = ({c.this.name.lower() for c in side.find_all(exp.EQ, exp.GT, exp.LT, exp.Like) if isinstance(c.this, exp.Column) and _value(c.expression)}
                  for side in (x.this, x.expression))
        if l == r and len(l) >= 2 and cl and cr and not (cl & cr): out["condition_linkage"] = "B"
    out.pop("referent_column", None)   # read on samples: the question usually names the table in other words; not measurable from SQL
    return out


def measure():
    S = schemas(); res = {}
    for g, f in I.GROUPS.items():
        tot = defaultdict(Counter); ex = defaultdict(list)
        for db, sql, q in f():
            for k, s in sides(db, sql, q, S).items():
                if CUES.get(k) is not None and CUES[k].search(q): continue
                tot[k][s] += 1
                if len(ex[(k, s)]) < 4: ex[(k, s)].append({"db": db, "question": q[:200], "sql": sql[:300]})
        res[g] = {"kinds": {k: {"n_A": tot[k]["A"], "n_B": tot[k]["B"]} for k, *_ in KINDS},
                  "examples": {"%s|%s" % kk: v for kk, v in ex.items()}}
    return res


# THE MINORITY READINGS ARE REVIEWED (2026-10-17): every silent reference that takes the less common reading is listed in
# human_supervision/review-reference-minority.md; a case marked "no" there (the rule misread the SQL, the question is not
# silent, or the choice does not arise) is dropped from Table 2. Parsed into VERDICTS by `minority parse`.
MINORITY = Path("out/paper/data/tab2_minority.jsonl"); SHEET = Path("human_supervision/review-reference-minority.md")
VERDICTS = Path("human_supervision/reference_minority_verdicts.json")
INC_USUAL = {"ties_and_selection": "A", "counting_unit": "B", "population_scope": "A", "missing_values": "B", "calculation_scale": "A",
             "boundary_between": "B", "boundary_open": "A", "text_match": "A"}            # = exhibit_data.USUAL
INC_TYPE = {"ties_and_selection": "ties_and_selection", "counting_unit": "counting_unit", "population_scope": "population_scope",
            "missing_values": "missing_values", "calculation_scale": "calculation", "boundary_between": "time_scope",
            "boundary_open": "value_representation", "text_match": "value_representation"}
READING = {"ties_and_selection": "every tied row (= MIN/MAX)", "counting_unit": "distinct entities", "population_scope": "outer join keeps unmatched",
           "missing_values": "NULL filtered before the extreme", "calculation_scale": "a fraction, not times 100",
           "boundary_between": "'between' excludes its ends", "boundary_open": "'after/over/under...' inclusive", "text_match": "loose match (LIKE)"}


def _id(g, db, sql, q):
    import hashlib
    return hashlib.sha1(("%s|%s|%s|%s" % (g, db, sql, q)).encode()).hexdigest()[:10]


def minority():
    """Every silent reference on the less common side, for the inclination choices and the choices read here."""
    S = schemas(); new_usual = {}
    pool = Counter()
    rows = []
    for g, f in I.GROUPS.items():
        for db, sql, q in f():
            a = {k: v for k, v in I.sides(sql, q).items() if k in INC_USUAL and not (k in I.CUES and I.CUES[k].search(q))}
            b = {k: v for k, v in sides(db, sql, q, S).items() if not (CUES.get(k) is not None and CUES[k].search(q))}
            for k, v in b.items(): pool[(k, v)] += 1
            rows.append((g, db, sql, q, a, b))
    for k, *_ in KINDS: new_usual[k] = "A" if pool[(k, "A")] >= pool[(k, "B")] else "B"
    lab = {k: (t, a, b) for k, t, a, b in KINDS}
    out = []
    for g, db, sql, q, a, b in rows:
        for k, v in a.items():
            if v != INC_USUAL[k]: out.append({"kind": k, "type": INC_TYPE[k], "reading": READING[k]})
        for k, v in b.items():
            if v != new_usual[k]: out.append({"kind": k, "type": lab[k][0], "reading": lab[k][1 if v == "A" else 2]})
        for x in out:
            if "id" not in x: x.update({"id": _id(g, db, sql, q) + ":" + x["kind"], "group": g, "db": db, "question": q, "sql": sql})
    MINORITY.write_text("".join(json.dumps(x) + "\n" for x in out))
    print("minority cases:", len(out), dict(Counter(x["type"] for x in out)))
    return out


def sheet(prefill):
    """Write the review sheet; `prefill` = {id: {"verdict", "reason"}} from a first reading, which the author confirms or changes."""
    X = [json.loads(l) for l in MINORITY.open()]
    esc = lambda t: re.sub(r"\s+", " ", t).replace("|", "\\|")
    L = ["# Review: silent references that take the less common reading (Table 2)", "",
         "Each row is a BIRD or Spider question whose wording a code rule finds silent on a choice, and whose reference SQL takes the",
         "less common reading. Verdict **yes**: the SQL takes that reading, the wording leaves the choice open, and the choice can change",
         "the answer. **no**: drop the row (the rule misread the SQL, the wording settles the choice, or the choice cannot arise).",
         "The verdicts were first filled by a reading against fixed criteria; edit any verdict, then run",
         "`python -m specbridge.comm.diagnose.reference_split parse` and `python -m specbridge.comm.diagnose.reference_split`.", ""]
    for t in sorted({x["type"] for x in X}):
        xs = [x for x in X if x["type"] == t]
        L += ["## %s (%d)" % (t, len(xs)), "", "| id | source | question | reference SQL | reading | verdict | reason |", "|---|---|---|---|---|---|---|"]
        for x in xs:
            v = prefill.get(x["id"], {})
            L.append("| %s | %s %s | %s | `%s` | %s | %s | %s |" % (x["id"], x["group"], x["db"], esc(x["question"]), esc(x["sql"]).replace("`", "'"),
                                                              x["reading"], v.get("verdict", ""), esc(v.get("reason", ""))))
        L.append("")
    SHEET.write_text("\n".join(L)); print("sheet:", SHEET, len(X), "rows")


def parse():
    V = {}
    for l in SHEET.read_text().splitlines():
        c = [x.strip() for x in re.split(r"(?<!\\)\|", l)]
        if len(c) >= 9 and ":" in c[1] and c[6] in ("yes", "no"): V[c[1]] = {"verdict": c[6], "reason": c[7]}
    VERDICTS.write_text(json.dumps(V, indent=1)); print("verdicts:", dict(Counter(v["verdict"] for v in V.values())))


def dropped():
    """{kind: number of minority cases an author review marked "no"}"""
    if not VERDICTS.exists(): return Counter()
    V = json.loads(VERDICTS.read_text())
    return Counter(k.split(":")[-1] for k, v in V.items() if v.get("verdict") == "no")


def library_check(S):
    """Do the rules find the choice in the library's own records (mined from failures by a model)? {type: [found, records]}"""
    inc = {"counting_unit": ["counting_unit"], "missing_values": ["missing_values"], "population_scope": ["population_scope"],
           "ties_and_selection": ["ties_and_selection"], "time_scope": ["boundary_between", "boundary_open"], "calculation": ["calculation_scale"],
           "value_representation": ["text_match", "boundary_open"]}
    new = {t: [k] for k, t, *_ in KINDS}
    R = defaultdict(lambda: [0, 0])
    for l in LIB.open():
        e = json.loads(l)
        if e["type"] in ("output_form", "referent_column") or "decision site" in str(e.get("provenance", {}).get("from")): continue
        a = I.sides(e["gold_sql"], e["question"]); b = sides(e["source"]["database"], e["gold_sql"], e["question"], S)
        R[e["type"]][1] += 1; R[e["type"]][0] += any(k in a or k in b for k in inc.get(e["type"], []) + new.get(e["type"], []))
    R = dict(R); R["all"] = [sum(v[0] for v in R.values()), sum(v[1] for v in R.values())]
    return R


def main():
    res = measure()
    pool = {k: [sum(r["kinds"][k]["n_" + s] for r in res.values()) for s in "AB"] for k, *_ in KINDS}
    out = {"kinds": {k: {"type": t, "A": a, "B": b, "n_A": pool[k][0], "n_B": pool[k][1]} for k, t, a, b in KINDS}, "groups": res,
           "note": "silent questions only (CUES); read from reference SQL + tables.json (sqlglot, no model); pooled over the author "
                   "groups of specbridge.comm.diagnose.inclination.GROUPS"}
    # Table 2: every library type -> [usual, other] (usual = the reading most silent references take); the inclination
    # choices pooled from fig6_inclination.json (value matching = exact match + strict cutoff, time scope = "between")
    F = json.loads(Path("out/paper/data/fig6_inclination.json").read_text())["groups"]
    inc = lambda k: [sum(v["kinds"][k]["k"] for v in F.values()), sum(v["kinds"][k]["n"] - v["kinds"][k]["k"] for v in F.values())]
    T = {"counting_unit": inc("counting_unit"), "missing_values": inc("missing_values"), "population_scope": inc("population_scope"),
         "ties_and_selection": inc("ties_and_selection"), "time_scope": inc("boundary_between"), "calculation": inc("calculation_scale"),
         "value_representation": inc("text_match"), "strict_cutoff": inc("boundary_open")}   # cutoffs apart: the sets test them
    for k, t, *_ in KINDS:
        if pool[k] != [0, 0]: T[t] = sorted(pool[k], reverse=True)
    D = dropped()      # minority cases rejected in the author review leave the "other" count (inclination kinds: by kind)
    inc_kind = {"counting_unit": ["counting_unit"], "missing_values": ["missing_values"], "population_scope": ["population_scope"],
                "ties_and_selection": ["ties_and_selection"], "time_scope": ["boundary_between"], "calculation": ["calculation_scale"],
                "value_representation": ["text_match"], "strict_cutoff": ["boundary_open"]}
    for t in T:
        if t in inc_kind: continue          # fig6_inclination.json is built by measure_groups, which already leaves them out
        ks = [k for k, tt, *_ in KINDS if tt == t]
        T[t] = [T[t][0], T[t][1] - sum(D[k] for k in ks)]
    out["table2"] = T; out["dropped"] = dict(D); out["library_check"] = library_check(S=schemas())
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=1))
    for t, (u, o) in sorted(T.items()): print("  table2 %-26s usual %6d  other %5d (%.1f%%)" % (t, u, o, 100 * o / (u + o)))
    for k, v in out["kinds"].items(): print("%-22s A %-28s %6d | B %-28s %6d" % (k, v["A"], v["n_A"], v["B"], v["n_B"]))


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1:2]
    if cmd == ["minority"]: minority()
    elif cmd == ["sheet"]: sheet(json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {})
    elif cmd == ["parse"]: parse()
    else: main()
