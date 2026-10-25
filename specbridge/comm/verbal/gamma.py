"""specbridge.comm.verbal.gamma -- COMMUNICATION (gamma): where a task's wording may say less than the SQL, and what the agent must then
figure out. The intended SQL, its answer and its grader never change; only the rendering of a located SITE does.

Six angles (docs/GAMMA.md). This module LOCATES every site of every angle in a rendered task (`sites`), and for the
first angle it varies -- VALUE RESOLUTION -- supplies the verified natural label of a stored value (`value_labels`)
and marks the specification with it (`annotate`), so `specbridge.pd.spec.render.english(s, gamma={"values": "natural"})` can say
"the stored code for 'monthly issuance'" where the explicit rendering says 'POPLATEK MESICNE'.

A natural label is VERIFIED when (1) the database's own documentation states it for that stored value (BIRD's
database_description files, read by `specbridge.pd.realize.vocab.read` -- the database's documentation, never a gold query), (2) the
value is observed in the column, and (3) the label names exactly one stored value of the column. Anything else keeps
its explicit wording: an unverified label would turn difficulty into ambiguity.

    python -m specbridge.comm.verbal.gamma scan out/pilot100/tasks.jsonl out/gamma      # SITES.md: every site, by angle
    python -m specbridge.comm.verbal.gamma values out/pilot100/tasks.jsonl out/gamma    # explicit and natural-label versions
"""
import collections, json, os, re, sqlite3, sys

ANGLES = ("column identification", "value resolution", "entity matching", "relationship guidance",
          "calculation expression", "procedure disclosure")
_DOC_DIRS = ("dev_unzipped/dev_20240627/dev_databases/{d}", "spider_data/spider_data/database/{d}")
_LINE = re.compile(r'^\s*[·•\x95\u2022\-\*]?\s*"?(?P<key>[^"=:]{1,40}?)"?\s*(?::|=|\bstands for\b|\bmeans\b)\s*(?P<label>.+?)\s*$', re.I)


# ================================================================ value resolution: verified labels
def value_labels(db, con):
    """{(table, column): {stored value: label}} -- documented, observed, one-to-one (see the module note)."""
    from specbridge.pd.realize.vocab import read
    out = {}
    for pat in _DOC_DIRS:
        d = pat.format(d=db)
        if not os.path.isdir(os.path.join(d, "database_description")): continue
        for (t, c), x in read(d).items():
            text = x.get("values") or ""
            pairs = {}
            for line in re.split(r"[\n;]", text):
                m = _LINE.match(line.strip())
                if not m: continue
                key = m.group("key").strip().strip("'\"")
                label = re.sub(r"^(stands for|means)\s+", "", m.group("label").strip().strip("'\"."), flags=re.I).strip()
                label = label.split(". ")[0][:80]
                # a label is a MEANING: a phrase of three letters or more, not another code ("0: N", "1: Y")
                if key and label and key.lower() != label.lower() and len(re.findall(r"[A-Za-z]", label)) >= 3: pairs[key] = label
            ok = {}
            for key, label in pairs.items():
                stored = _observed(con, t, c, key)
                if stored is not None: ok[stored] = label
            short = language(db)["codes"].get("%s.%s" % (t, c), {})
            for k in list(ok):
                if repr(k) in short: ok[k] = short[repr(k)]["label"]
            for k, v in short.items():                          # a documented code the parser missed, accepted by rule
                try: kv = __import__("ast").literal_eval(k)
                except Exception: continue
                if kv not in ok and _observed(con, t, c, str(kv)) is not None: ok[_observed(con, t, c, str(kv))] = v["label"]
            by_label = collections.Counter(l.lower() for l in ok.values())
            ok = {k: l for k, l in ok.items() if by_label[l.lower()] == 1}
            if ok: out[(t, c)] = ok
        break
    return out


def _observed(con, t, c, key):
    """The stored value the documented key names, if the column holds it: as written, else as a number."""
    q = 'SELECT %s FROM "%s" WHERE %s = ? LIMIT 1' % ('"%s"' % c, t, '"%s"' % c)
    for k in (key, _num(key)):
        if k is None: continue
        try:
            r = con.execute(q, (k,)).fetchone()
        except Exception:
            r = None
        if r is not None: return r[0]
    return None


def _num(s):
    try: return int(s) if re.fullmatch(r"-?\d+", s.strip()) else float(s)
    except Exception: return None


# ================================================================ the sites of every angle
def _queries(s):
    """(where, query) for every query in a specification: the steps, the answer, and each nested one."""
    for st in s["steps"]: yield "step %d" % st["number"], st["query"]
    yield "answer", s["query"]
    def nested(x, where):
        if isinstance(x, dict):
            if x.get("op") in ("in_query", "exists"): yield where + " > subquery", x["query"]
            for v in x.values(): yield from nested(v, where)
        elif isinstance(x, list):
            for v in x: yield from nested(v, where)
    for st in s["steps"]: yield from nested(st["query"], "step %d" % st["number"])
    yield from nested(s["query"], "answer")


def _walk(x):
    if isinstance(x, dict):
        yield x
        for v in x.values(): yield from _walk(v)
    elif isinstance(x, list):
        for v in x: yield from _walk(v)


def _value_sites(c):
    """(column node, value node) pairs a condition MATCHES: = and != and IN. A stored code names a category, so
    only a match can be said by its meaning; a threshold (<, >, BETWEEN) is not a value-resolution site."""
    col = lambda y: y if isinstance(y, dict) and y.get("op") == "column" else None
    if c.get("op") == "compare" and c.get("cmp") in ("=", "!=", "<>"):
        l, r = c["left"], c["right"]
        if col(l) and r.get("op") == "value": yield l, r
        if col(r) and l.get("op") == "value": yield r, l
    elif c.get("op") == "one_of" and col(c["arg"]):
        for v in c["values"]:
            if v.get("op") == "value": yield c["arg"], v


def sites(s, labels=None):
    """Every place in the specification where a gamma angle can vary, by angle. Each site: where it is, what the
    explicit rendering states, and (value resolution) whether a verified natural label exists."""
    from specbridge.pd.spec.render import ARITH, FUNCS
    labels = labels or {}
    out = []
    add = lambda angle, where, what, **kw: out.append({"angle": angle, "where": where, "explicit": what, **kw})
    seen_cols = set()
    for where, q in _queries(s):
        for n in _walk(q):
            op = n.get("op")
            if op == "column" and n["ref"] not in seen_cols:
                seen_cols.add(n["ref"]); add("column identification", where, "%s (`%s`)" % (n["label"], n["ref"]), ref=n["ref"])
            if op in ("compare", "one_of", "between"):
                for colnode, v in _value_sites(n):
                    t, c = colnode["ref"].split(".", 1)
                    lab = labels.get((t, c), {}).get(v["value"])
                    add("value resolution", where, "%s = %r" % (colnode["ref"], v["value"]), ref=colnode["ref"], stored=v["value"],
                        label=lab, verified=lab is not None, numeric=not isinstance(v["value"], str))
            if op == "matches": add("entity matching", where, "a pattern match", pattern=n["pattern"].get("value"))
            if op == "fn" and str(n.get("name", "")).lower() in ("substr", "instr", "lower", "upper", "trim", "replace"):
                add("entity matching", where, "a text function %s" % n["name"])
            if op == "aggregate" and n.get("filter"): add("procedure disclosure", where, "an aggregate counting only some records")
            if op in ("within", "window", "rank", "ntile", "row_number", "lag", "lead", "first_value"):
                add("procedure disclosure", where, "a value computed over other result rows (%s)" % op)
        for j in q.get("joins") or []:
            add("relationship guidance", where, "a join to %s" % (j.get("table") or j.get("source", {}).get("table", "?")))
        if q["source"].get("step"): add("relationship guidance", where, "reads an earlier step")
        if q.get("group"): add("procedure disclosure", where, "grouping by %d key(s)" % len(q["group"]))
        if q.get("having"): add("procedure disclosure", where, "a condition on groups")
        for o in q["outputs"]:
            if o["expr"].get("op") in ARITH | FUNCS - {"as_real", "as_text"}:
                add("calculation expression", where, "output %d is a formula" % o["position"])
        for c in [q.get("where"), q.get("having")]:
            for n in _walk(c or {}):
                if n.get("op") == "compare" and any(isinstance(y, dict) and y.get("op") in ARITH for y in (n["left"], n["right"])):
                    add("calculation expression", where, "a condition on a formula")
    if s["steps"]: add("procedure disclosure", "task", "%d numbered step(s)" % len(s["steps"]))
    return out


def annotate(s, labels):
    """Marks each value-resolution site's value node with its verified label (`gamma_label`); nothing else changes."""
    for _where, q in _queries(s):
        for n in _walk(q):
            if n.get("op") in ("compare", "one_of", "between"):
                for colnode, v in _value_sites(n):
                    t, c = colnode["ref"].split(".", 1)
                    lab = labels.get((t, c), {}).get(v["value"])
                    if lab: v["gamma_label"] = lab
    return s


# ================================================================ column identification: labels checked in context
def _norm(x): return re.sub(r"[^a-z0-9]", "", str(x).lower())


def language(db):
    """The accepted language resource of a database (catalogues/language/<db>.json): column labels, entity names and
    short code meanings that passed out/verbalize/accept.py. Empty when there is none."""
    p = os.path.join("catalogues", "language", "%s.json" % db)
    return json.load(open(p)) if os.path.exists(p) else {"columns": {}, "entities": {}, "codes": {}}


def column_labels(s, cat, ents=None):
    """Marks each column node of the specification with the label it may be called by (`gamma_col`), checked IN
    CONTEXT against every column of every table the task reaches; returns the fallbacks (the column keeps its handle)
    and the awkward labels, for one later batch of proposals.
      refused   the catalogue marks the meaning low-confidence; the label is only the column's raw name ("A3")
      qualified the label is shared by another column in reach: qualified by its table's entity ("the district's
                location of branch"), kept only if that is unique
      awkward   used, but worth a better proposal: a slash or parenthesis, or a label with no confidence recorded"""
    from specbridge.pd.spec.render import _label
    from specbridge.pd.realize.semantic import load
    ents = ents or {}
    meta = load(cat)["columns"]
    tables = set()
    for _w, q in _queries(s):
        if not q["source"]["step"]: tables.add(q["source"]["table"])
        tables |= {j["table"] for j in q["joins"] if not j["step"]}
    lang = language(cat.db)["columns"]
    from specbridge.pd.realize.vocab import read
    docs = next((read(p.format(d=cat.db)) for p in _DOC_DIRS if os.path.isdir(os.path.join(p.format(d=cat.db), "database_description"))), {})
    equated = set()                                            # column pairs the task's joins make equal
    for _w, q in _queries(s):
        for j in q["joins"]:
            on = j["on"]
            if on.get("op") == "compare" and on.get("cmp") == "=" and on["left"].get("op") == "column" and on["right"].get("op") == "column":
                a, b = on["left"]["ref"].split(".", 1), on["right"]["ref"].split(".", 1)
                equated.add(frozenset([tuple(a), tuple(b)]))
    reach = {(t, c.name): (lang.get("%s.%s" % (t, c.name), {}).get("label") or _label(cat, t, c.name)[0]) for t in tables for c in cat.cols.get(t, [])}
    by = collections.defaultdict(list)
    for k, lab in reach.items(): by[_norm(lab)].append(k)
    fallbacks, awkward, done = [], [], {}
    for _w, q in _queries(s):
        for n in _walk(q):
            if n.get("op") != "column" or "." not in n.get("ref", ""): continue
            t, c = n["ref"].split(".", 1)
            if (t, c) not in done:
                lab = reach.get((t, c)) or n["label"]
                conf = "accepted" if "%s.%s" % (t, c) in lang else (meta.get("%s.%s" % (t, c), {}).get("confidence") or {}).get("quantity")
                why, final = None, lab
                if "%s.%s" % (t, c) not in lang and len(lab) == 60 and not lab.endswith((".", ")")):
                    why = "the catalogue label is cut at 60 characters"           # specbridge.pd.realize.semantic keeps quantity[:60]
                elif conf == "low": why = "the catalogue marks this meaning low-confidence"
                elif _norm(lab) == _norm(c) and " " not in lab.strip(): why = "the label is only the column's raw name"
                elif len(by[_norm(lab)]) > 1:
                    e = ents.get(t)
                    q_lab = "the %s's %s" % (e[0], lab) if e and _norm(e[0]) not in _norm(lab) else None
                    others = [k for k in by[_norm(lab)] if k != (t, c)]
                    if q_lab and all(not ents.get(o[0]) or _norm(ents[o[0]][0]) != _norm(e[0]) for o in others): final = q_lab
                    else: why = "the label is shared by %s in reach" % ", ".join("`%s.%s`" % o for o in others)
                # UNRESOLVED: another column in reach that the database DOCUMENTS IDENTICALLY (Laboratory.DNA and DNA-II are
                # both "anti-DNA"). Identical documentation is uncertainty, not interchangeability: unless the task's own
                # join equates the two (then either reading gives the same rows), the precise identifier stays.
                d = _norm(docs.get((t, c), {}).get("desc", ""))
                doc_twins = [k for k in reach if k != (t, c) and d and _norm(docs.get(k, {}).get("desc", "")) == d and frozenset([k, (t, c)]) not in equated]
                same_table = [k for k in doc_twins if k[0] == t]
                if why is None and same_table:             # no qualifier can tell two columns of one table apart
                    why = "UNRESOLVED: documented exactly as %s in the same table; no justification that both readings hold" % ", ".join("`%s.%s`" % k for k in same_table)
                # A COLUMN OF THE SAME NAME in another table in reach (Patient.Diagnosis, Examination.Diagnosis): the
                # label must say whose, or a reader takes the other one
                # ...or DOCUMENTED IDENTICALLY in another table: the entity names the table, and so the reading
                twins = [k for k in reach if k[0] != t and _norm(k[1]) == _norm(c)] + [k for k in doc_twins if k[0] != t]
                if why is None and twins:
                    e = ents.get(t)
                    if e and _norm(e[0]) not in _norm(final): final = "the %s's %s" % (e[0], final)
                    elif not e: why = "a column of the same name is in %s, and this table has no entity name to say whose" % ", ".join("`%s`" % k[0] for k in twins)
                done[(t, c)] = (final if why is None else None, why)
                if why: fallbacks.append({"kind": "column", "item": "%s.%s" % (t, c), "label": lab, "why": why})
                elif re.search(r"[/()]", lab) or conf is None:
                    awkward.append({"kind": "column", "item": "%s.%s" % (t, c), "label": lab,
                                    "why": "a slash or parenthesis" if re.search(r"[/()]", lab) else "no confidence recorded"})
            if done[(t, c)][0]: n["gamma_col"] = done[(t, c)][0]
    return fallbacks, awkward


def code_sites(s, cat, labels):
    """Matched values of a CATEGORY column (codes) and whether each is said by a documented meaning; names, thresholds,
    dates and weights are task parameters and stay as they are (not listed)."""
    from specbridge.pd.realize.semantic import load
    meta = load(cat)["columns"]
    out = []
    for _w, q in _queries(s):
        for n in _walk(q):
            if n.get("op") not in ("compare", "one_of"): continue
            for colnode, v in _value_sites(n):
                t, c = colnode["ref"].split(".", 1)
                role = meta.get("%s.%s" % (t, c), {}).get("semantic_role")
                if role not in ("category", "indicator"): continue
                lab = labels.get((t, c), {}).get(v["value"])
                out.append({"kind": "code", "item": "%s.%s = %r" % (t, c, v["value"]), "label": lab,
                            "why": None if lab else "no documented meaning (kept explicit)",
                            "awkward": bool(lab) and len(lab.split()) > 5, "needs": "the database's value documentation" if lab else None})
    return out


# ================================================================ over frozen tasks
def _load(path):
    for l in open(path):
        yield json.loads(l)


def _spec(t):
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.spec.render import spec
    cat = Catalogue(t["database"])
    con = sqlite3.connect("file:%s?mode=ro" % t["snapshot"], uri=True)
    return spec(lift(t["reference_sql"], cat.con), cat), con


def scan(path, outdir):
    """SITES.md + sites.jsonl: every site of every angle in every frozen task."""
    os.makedirs(outdir, exist_ok=True)
    per_task, labels_by_db = [], {}
    with open(os.path.join(outdir, "sites.jsonl"), "w") as f:
        for t in _load(path):
            s, con = _spec(t)
            if t["database"] not in labels_by_db: labels_by_db[t["database"]] = value_labels(t["database"], con)
            ss = sites(s, labels_by_db[t["database"]])
            per_task.append((t, ss)); f.write(json.dumps({"id": t["id"], "database": t["database"], "sites": ss}, default=str) + "\n")
    n = len(per_task)
    L = ["# Where communication (gamma) can vary: every site in %d frozen tasks\n" % n,
         "Located by `specbridge.comm.verbal.gamma.sites` on each task's rendered specification (out/pilot100/tasks.jsonl). The SQL, answer "
         "and grader are fixed; a site is a place where the wording may say less than the SQL. docs/GAMMA.md defines the angles.\n",
         "| angle | sites | tasks with at least one | what the agent would have to figure out |", "|---|---|---|---|"]
    what = {"column identification": "which column a meaning refers to", "value resolution": "which stored code a meaning refers to",
            "entity matching": "how to implement a stated matching requirement", "relationship guidance": "which tables and keys connect",
            "calculation expression": "the formula behind a stated quantity", "procedure disclosure": "the grouping, windowing and steps"}
    for a in ANGLES:
        k = [ss for _t, ss in per_task if any(x["angle"] == a for x in ss)]
        L.append("| %s | %d | %d | %s |" % (a, sum(1 for _t, ss in per_task for x in ss if x["angle"] == a), len(k), what[a]))
    vs = [x for _t, ss in per_task for x in ss if x["angle"] == "value resolution"]
    vt = [x for x in vs if not x["numeric"]]
    L.append("\n## Value resolution in detail\n")
    L.append("Value sites: %d (text %d, numeric %d). With a verified natural label: %d (text %d). Tasks where the natural "
             "version differs from the explicit one: %d of %d.\n" % (len(vs), len(vt), len(vs) - len(vt), sum(x["verified"] for x in vs),
             sum(x["verified"] for x in vt), sum(1 for _t, ss in per_task if any(x["angle"] == "value resolution" and x["verified"] for x in ss)), n))
    L.append("Verified labels per database: " + ", ".join("%s %d columns / %d values" % (db, len(v), sum(len(x) for x in v.values()))
                                                          for db, v in sorted(labels_by_db.items())) + ".\n")
    L.append("| column | stored value | verified label | sites |"); L.append("|---|---|---|---|")
    c = collections.Counter((x["ref"], repr(x["stored"]), x["label"] or "-- none (stays explicit)") for x in vt)
    L += ["| `%s` | %s | %s | %d |" % (k[0], k[1], k[2], v) for k, v in c.most_common(25)]
    open(os.path.join(outdir, "SITES.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def values(path, outdir):
    """Explicit and natural-label versions of the same frozen tasks (value resolution only). The explicit version
    must reproduce the frozen instruction exactly; each version records the frozen task's SQL and grader unchanged."""
    from specbridge.pd.spec.render import english
    os.makedirs(outdir, exist_ok=True)
    labels_by_db, rows, same = {}, 0, 0
    with open(os.path.join(outdir, "values_versions.jsonl"), "w") as f:
        for t in _load(path):
            s, con = _spec(t)
            if t["database"] not in labels_by_db: labels_by_db[t["database"]] = value_labels(t["database"], con)
            annotate(s, labels_by_db[t["database"]])
            explicit, natural = english(s), english(s, gamma={"values": "natural"})
            rows += 1; same += explicit == t["instruction"]
            f.write(json.dumps({"id": t["id"], "database": t["database"], "reference_sql": t["reference_sql"], "grader": t["grader"],
                                "explicit": explicit, "natural": natural, "changed": explicit != natural,
                                "explicit_equals_frozen": explicit == t["instruction"]}) + "\n")
    print("tasks %d | explicit version identical to the frozen instruction: %d | natural differs: see values_versions.jsonl" % (rows, same))


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    a = sys.argv[1:]
    {"scan": scan, "values": values}[a[0]](a[1], a[2])
