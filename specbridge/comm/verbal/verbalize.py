"""specbridge.comm.verbal.verbalize -- the VERBALIZER V(S; s, gamma): a task's specification S in words. (R is reserved for realization.)

    s = "explicit"   specbridge.pd.spec.render.english: every clause in SQL's logical order (level 0)
    s = "natural"    RESULT-FOCUSED, from the SAME specification (never by shortening the explicit text):
                     "For each district, show ... . Use every transaction, with its account, and the account's district."
    gamma            the communication controls (specbridge.comm.verbal.gamma, docs/GAMMA.md), the same under either style

The natural style, in three layers:
  1. READ THE RESULT: what one output row is -- a group of key values, a single summary row, or one record, named by
     its ENTITY ("transaction") when the table's catalogue grain gives a plain noun.
  2. TEMPLATES: the result's rows and columns (in column order), the records used and how they combine -- a VERIFIED
     RELATIONSHIP as "each transaction with its account" --, record and group filters, duplicates, sorting, limits;
     CONCISE AGGREGATES ("the number of transactions", "the average of amount") with the missing-value rule stated once.
  3. ACCOUNT FOR EVERY REQUIREMENT: a ledger claims each element of the specification; an unclaimed one is refused.
     A short DEFINITIONS section keeps the exact details: what each entity is (its table), each relationship's exact
     condition, the missing-value rule, the letters. Steps and windows keep the explicit wording.

VERIFIED, and otherwise the exact wording:
  entity noun   the catalogue's grain for the table, "one <noun> [qualifier]", reduced to a plain noun of at most three
                words (no possessive, slash or parenthesis); the definitions say which table it is
  relationship  an equality join on a foreign key the database declares, with the referenced column unique in the rows:
                from the referencing side it is "its <parent>" (at most one match: no record is multiplied); from the
                referenced side "each of its <children>" (one row per match). Whether an unmatched record is dropped or
                kept is always stated.
Every column, value and formula is written by the explicit renderer's own phrase functions: under gamma = explicit
the handles, stored codes and formulas are exact.
"""
import json, os, re
from specbridge.pd.spec import render as R
from specbridge.pd.spec.render import Unrenderable


def V(S, s="explicit", gamma=None, cat=None):
    if s == "explicit": return R.english(S, gamma)
    if s == "natural": return natural(S, gamma, cat)
    raise ValueError("style %r" % s)


class _Ledger:
    """Which template stated which element of the specification, and WHERE: each element is a stable component ID
    ("records", "join 2", "record filter", "grouping", "output 3", "ordering", "limit", ...) and keeps the exact phrases
    that state it, so a component of the SQL can be traced to its span in the question. `check` refuses any element
    left unstated."""
    def __init__(self): self.claims, self.phrases = {}, {}
    def claim(self, element, template, phrase=None):
        self.claims.setdefault(element, template)
        if phrase: self.phrases.setdefault(element, []).append(phrase)
    def check(self, elements):
        missing = [e for e in elements if e not in self.claims]
        if missing: raise Unrenderable("the natural style states nothing for: %s" % ", ".join(missing))


def _elements(q):
    el = ["records"] + ["join %d" % (i + 1) for i in range(len(q["joins"]))]
    if q["where"] is not None: el.append("record filter")
    if q["group"]: el.append("grouping")
    if q["single_group"]: el.append("one summary row")
    if q["having"] is not None: el.append("group filter")
    el += ["output %d" % o["position"] for o in q["outputs"]]
    if q["distinct"]: el.append("duplicates removed")
    if q["order"]: el.append("ordering")
    if q["limit"] is not None: el.append("limit")
    if q["offset"]: el.append("offset")
    return el


# ================================================================ verified names and relationships
_CUT = re.compile(r"\s+(?:\(|issued|taken|posted|for|on|of|within|in|belonging|joined|having|with|from|to)\b.*$")


_PARTICIPLE = re.compile(r"(ed|sold|made|held|paid|taken|given|written|shown)$")


def _plural(n):
    w = n.split(" ")
    if len(w) > 1 and _PARTICIPLE.search(w[-1]):          # "track sold" -> "tracks sold": the head noun takes the plural
        return " ".join([_plural(w[0])] + w[1:])
    last = w[-1]
    last = last[:-1] + "ies" if re.search(r"[^aeiou]y$", last) else last + "es" if re.search(r"(s|x|ch|sh|[^aeiou]o)$", last) else last + "s"
    return " ".join(w[:-1] + [last])


def entities(cat):
    """{table: (singular, plural)} for tables whose catalogue grain gives a plain noun."""
    if cat is None: return {}
    if "_entities" in cat.__dict__: return cat.__dict__["_entities"]
    out = {}
    try: tables = json.load(open(os.path.join("catalogues", "%s.json" % cat.db)))["tables"]
    except Exception: tables = {}
    for t, x in tables.items():
        m = re.match(r"^one\s+(.+)$", (x.get("grain") or "").strip())
        if not m: continue
        n = _CUT.sub("", m.group(1)).strip()
        if "'" in n or "/" in n or "(" in n or not re.fullmatch(r"[A-Za-z][A-Za-z ]*", n) or len(n.split()) > 3: continue
        out[t] = (n, _plural(n))
    from specbridge.comm.verbal.gamma import language
    for t, x in language(cat.db).get("entities", {}).items(): out[t] = (x["singular"], x["plural"])   # accepted names
    cat.__dict__["_entities"] = out
    return out


def _fk(cat, child, ccol, parent, pcol):
    """Is child.ccol -> parent.pcol a relationship: parent.pcol unique in the rows, and either a key the database
    DECLARES or one the ROWS show (every non-missing child.ccol occurs in parent.pcol)? A missing declaration does not
    prove a relationship unknown; the rows can establish it."""
    if cat is None: return False
    memo = cat.__dict__.setdefault("_fk_memo", {})
    k = (child, ccol, parent, pcol)
    if k not in memo:
        ok = False
        try:
            n, d = cat.con.execute('SELECT COUNT("%s"), COUNT(DISTINCT "%s") FROM "%s"' % (pcol, pcol, parent)).fetchone()
            if n and n == d:
                fks = cat.con.execute('PRAGMA foreign_key_list("%s")' % child).fetchall()
                if any(f[2] == parent and f[3] == ccol and (f[4] or pcol) == pcol for f in fks): ok = True
                elif ccol != pcol or child != parent:
                    # inclusion shown by the rows: every non-missing child value occurs among the (unique) parent values
                    miss = cat.con.execute('SELECT 1 FROM "%s" WHERE "%s" IS NOT NULL AND "%s" NOT IN (SELECT "%s" FROM "%s") LIMIT 1'
                                           % (child, ccol, ccol, pcol, parent)).fetchone()
                    m = cat.con.execute('SELECT COUNT("%s") FROM "%s"' % (ccol, child)).fetchone()[0]
                    ok = miss is None and m > 0
        except Exception:
            ok = False
        memo[k] = ok
    return memo[k]


def relation(cat, j, scope):
    """How join j relates to a table already in scope: ("its", that table) when j's table is the one referenced (at most
    one match), ("each of its", that table) when j's table references it (one row per match); None if not verified."""
    on = j["on"]
    if j["step"] or on.get("op") != "compare" or on.get("cmp") != "=": return None
    l, r = on["left"], on["right"]
    if l.get("op") != "column" or r.get("op") != "column": return None
    (lt, lc), (rt, rc) = l["ref"].split(".", 1), r["ref"].split(".", 1)
    for (a, ac, an), (b, bc, bn) in (((lt, lc, l), (rt, rc, r)), ((rt, rc, r), (lt, lc, l))):
        if b == j["table"] and a in scope and _fk(cat, a, ac, b, bc): return ("its", a, an, _keys_to(cat, a, b) > 1)
        if b == j["table"] and a in scope and _fk(cat, b, bc, a, ac): return ("each of its", a, bn, _keys_to(cat, b, a) > 1)
    return None


def _keys_to(cat, child, parent):
    """How many declared keys of `child` refer to `parent`: with more than one, "its <parent>" does not say which."""
    try: return sum(1 for f in cat.con.execute('PRAGMA foreign_key_list("%s")' % child).fetchall() if f[2] == parent)
    except Exception: return 0


# ================================================================ the natural style
_STATE = {}


def _concise_aggregate(y):
    """An aggregate as the natural style says it; the missing-value rule is stated once, in the definitions."""
    noun = _STATE["noun"]
    filt = ", counting only the %s for which %s" % (noun, R.cond(y["filter"])) if y.get("filter") else ""
    a = y["arg"]
    if a is None: return "the number of %s%s" % (noun, filt)
    v = R.value(a)
    if y["fn"] == "COUNT":
        if y["distinct"]: return "the number of distinct values of %s%s" % (v, filt)
        return "the number of %s whose %s is not missing%s" % (noun, v, filt)
    _STATE["missing_rule"] = True
    words = {"SUM": "the total of", "AVG": "the average of", "MIN": "the smallest", "MAX": "the largest"}[y["fn"]]
    if y["fn"] in ("MIN", "MAX") and a["type"] == "text": words += " (in character order)"
    return "%s%s %s%s" % (words, " the distinct values of" if y["distinct"] else "", v, filt)


def _a(n):
    """The indefinite article for a noun phrase: 'an' before a vowel sound (by its first letter)."""
    return ("an " if n[:1].lower() in "aeiou" else "a ") + n


def _order_key(o):
    text = o["expr"]["type"] == "text"
    if o["dir"] == "asc": return "%s, %s, missing values first" % (R.value(o["expr"]), "in character order" if text else "lowest first")
    return "%s, %s, missing values last" % (R.value(o["expr"]), "in reverse character order" if text else "highest first")


def _natural_query(q, L, cat):
    ents = entities(cat)
    level = "group" if (q["group"] or q["single_group"]) else "row"
    R._CTX.append({"level": level, "legend": [], "keys": {}})
    _STATE.clear(); _STATE["missing_rule"] = False
    try:
        src = q["source"]
        e = ents.get(src["table"]) if not src["step"] else None
        name = lambda t: ents[t][0] if t in ents else "`%s` record" % t
        # ---- the records: the source, then each join -- a verified relationship, or the exact pairing
        scope, rels, multiplied, defs = [src["table"]], [], False, []
        hide = R._GAMMA.get("columns") == "natural"
        if e and not hide: defs.append("%s is one `%s` record" % (_a(e[0]), src["table"]))
        if hide and not e and not src["step"] and "REPORT" in globals():
            REPORT["fallbacks"].append({"kind": "table", "item": src["table"], "label": None, "why": "no verified entity name (the table is named)"})
        # THE UNIT a join can drop or keep is the records built so far: the source's entity until a join multiplies them
        if src["step"]: unit = "rows of step %d" % R._STEPNO[src["table"]]
        elif e: unit = e[1]
        else: unit = "`%s` records" % src["table"]
        def fate(side, target, left, once=False, keyphrase=None):
            """What happens to a record of UNIT whose match is missing -- the unit named, never 'left out' alone."""
            if keyphrase: miss = "whose %s refers to no %s" % (keyphrase, target)
            elif side == src["table"]: miss = "without %s" % _a(target)
            else: miss = "whose %s has no %s" % (name(side), target)
            return "%s %s are %s" % (unit, miss, "left out" if not left else
                                     "kept%s, with the %s's values missing" % (" once" if once else "", target))
        for i, j in enumerate(q["joins"]):
            rel = relation(cat, j, scope) if j["table"] in ents else None
            left = j["kind"] == "left"
            if rel:
                how, side, keycol, several = rel
                whose = "its" if side == src["table"] else "the %s's" % name(side)
                pe = ents[j["table"]]
                kp = R.value(keycol) if several else None
                # GAMMA relationships = "implicit": the join KEY is left to the schema when the relationship is unambiguous
                # (verified, a single key); its FATE is left out only when the rows show it cannot change the answer
                # (gamma "fate_irrelevant": the joins, by number, where no carried record lacks a match)
                implicit = R._GAMMA.get("relationships") == "implicit" and not several
                fate_ok = implicit and (i + 1) in set(R._GAMMA.get("fate_irrelevant", ()))
                if how == "its":
                    # several keys to the same table: "its colour" does not say which, so the key is named
                    what = ("the %s %s %s refers to" % (pe[0], whose, kp)) if several else "%s %s" % (whose, pe[0])
                    rels.append(("with %s" % what) if fate_ok else "with %s (%s)" % (what, fate(side, pe[0], left, keyphrase=kp)))
                    L.claim("join %d" % (i + 1), "verified relationship", rels[-1])
                    if not implicit:
                        defs.append("%s's %s is the %s for which %s" % (_a(name(side)), pe[0], pe[0] if hide else "`%s` record" % j["table"], R.cond(j["on"])))
                        L.claim("join %d" % (i + 1), "verified relationship", defs[-1])
                else:
                    what = ("each %s whose %s refers to %s" % (pe[0], kp, "it" if side == src["table"] else "the %s" % name(side))) if several \
                        else "each of %s %s" % (whose, pe[1])
                    # ONE ROW PER CARRIED RECORD AND MATCH: the records carried so far (the source's entity, or combined records
                    # once a join has multiplied them) -- never the joining entity: "one row per patient and visit" would
                    # read as a patient-visit pair when the rows are lab panels (the 2026-09-28 fresh run, t000)
                    carried = ("row of step %d" % R._STEPNO[src["table"]]) if src["step"] else "combined record" if multiplied else \
                              (e[0] if e else "`%s` record" % src["table"])
                    rels.append(("paired with %s, one row per %s and %s" % (what, carried, pe[0])) if fate_ok else
                                "paired with %s, one row per %s and %s (%s)" % (what, carried, pe[0], fate(side, pe[0], left, once=True)))
                    L.claim("join %d" % (i + 1), "verified relationship", rels[-1])
                    if not implicit:
                        defs.append("the %s of %s are the %s for which %s" % (pe[1], _a(name(side)), pe[1] if hide else "`%s` records" % j["table"], R.cond(j["on"])))
                        L.claim("join %d" % (i + 1), "verified relationship", defs[-1])
                    multiplied = True
                d = "%s is one `%s` record" % (_a(pe[0]), j["table"])
                if d not in defs and not hide: defs.append(d)
                L.claim("join %d" % (i + 1), "verified relationship")
            else:
                if hide and not j["step"]:
                    REPORT["fallbacks"].append({"kind": "table", "item": j["table"], "label": None, "why": "joined without a verified relationship (the table is named)"})
                target = ("row of step %d" % R._STEPNO[j["table"]]) if j["step"] else "`%s` record" % j["table"]
                rels.append("paired with every %s for which %s, one row per match (%s with no matching %s are %s)" % (
                    target, R.cond(j["on"]), unit, target, "left out" if not left else "kept once, with those values missing"))
                L.claim("join %d" % (i + 1), "exact pairing", rels[-1])
                multiplied = True
            if multiplied: unit = "combined records"
            scope.append(j["table"])
        if src["step"]: base, noun, one = "the rows of step %d" % R._STEPNO[src["table"]], "rows", "row"
        elif e: base, noun, one = "every %s" % e[0], e[1], e[0]
        else: base, noun, one = "the `%s` records" % src["table"], "records", "record"
        if multiplied: noun, one = "combined records", "combined record"
        _STATE["noun"] = noun
        R._STYLE["aggregate"] = _concise_aggregate
        uses = "Use %s%s" % (base, ((", each " if not e else ", ") + ", and ".join(rels)) if rels else "")
        L.claim("records", "use", "Use %s" % base)
        # ---- what one row is, and its columns in order
        colp = ["(%d) %s" % (o["position"], R.value(o["expr"])) for o in q["outputs"]]
        cols = "; ".join(colp)
        for o, p in zip(q["outputs"], colp): L.claim("output %d" % o["position"], "column", p)
        if q["group"]:
            lead = "For each %s, show one row with these columns, in this order: %s" % (" and ".join(R.value(g) for g in q["group"]), cols)
            L.claim("grouping", "for each key", "For each %s, show one row" % " and ".join(R.value(g) for g in q["group"]))
        elif q["single_group"]:
            lead = "Over all the %s described below, show one row with these columns, in this order: %s" % (noun, cols)
            L.claim("one summary row", "over all", "Over all the %s described below, show one row" % noun)
        else:
            lead = "For each %s described below, show one row with these columns, in this order: %s" % (one, cols)
        out = [lead, uses]
        if q["where"] is not None: out.append("Include only the %s for which %s" % (noun, R.cond(q["where"]))); L.claim("record filter", "include only", out[-1])
        if q["having"] is not None:
            out.append("Keep only the %s for which %s" % ("groups" if q["group"] else "summary row", R.cond(q["having"]))); L.claim("group filter", "keep only groups", out[-1])
        if q["distinct"]: out.append("Leave out rows that duplicate an earlier row"); L.claim("duplicates removed", "distinct", out[-1])
        if q["order"]: out.append("Sort the rows by %s" % ", then by ".join(_order_key(o) for o in q["order"])); L.claim("ordering", "sort", out[-1])
        if q["limit"] is not None:
            if q["offset"]: out.append("Skip the first %d rows and return the next %s" % (q["offset"], q["limit"])); L.claim("offset", "skip", out[-1])
            else: out.append("Return only the first %s rows" % q["limit"])
            L.claim("limit", "first n", out[-1])
        text = ". ".join(out) + "."
        # ---- definitions: the exact details
        i = 0
        while i < len(R._ctx()["legend"]):
            nm, y = R._ctx()["legend"][i]; defs.append("%s is %s" % (nm, R.noun(y))); i += 1
            L.claim("definition %s" % nm, "letter", defs[-1])        # each formula symbol: its own component ID
            _STATE.setdefault("symbols", []).append(nm)
        if _STATE["missing_rule"]: defs.append("totals, averages, smallest and largest values ignore missing values, and are missing when there are none")
        if hide and cat is not None:
            from specbridge.comm.verbal import interpret
            if interpret.record({"query": q}, cat)["representation"]:
                defs.append("a coded value may be shown as stored or as its documented meaning, word for word")
        if defs: text += " Definitions: " + "; ".join(defs) + "."
        return text
    finally:
        R._CTX.pop(); R._STYLE.pop("aggregate", None)


REPORT = {}          # the last natural rendering's gamma report: fallbacks, awkward labels, codes, what the agent needs


def natural(S, gamma=None, cat=None):
    """With gamma {"columns": "natural", "values": "natural"}: columns by their meaning checked in context, codes by their
    documented meaning, no handle or code mapping anywhere in the question; every place that stays explicit is in
    REPORT["fallbacks"], every usable-but-poor label in REPORT["awkward"] (one later batch of proposals)."""
    gamma = dict(gamma or {})
    REPORT.clear(); REPORT.update(fallbacks=[], awkward=[], codes=[], needs=set())
    if cat is not None and (gamma.get("columns") == "natural" or gamma.get("values") == "natural"):
        from specbridge.comm.verbal import gamma as G
        labels = cat.__dict__.setdefault("_value_labels", None) or G.value_labels(cat.db, cat.con)
        cat.__dict__["_value_labels"] = labels
        if gamma.get("values") == "natural":
            G.annotate(S, labels)
            REPORT["codes"] = G.code_sites(S, cat, labels)
            REPORT["fallbacks"] += [x for x in REPORT["codes"] if x["why"]]
            REPORT["awkward"] += [dict(x, why="a documented meaning longer than five words") for x in REPORT["codes"] if x["awkward"]]
            if any(x["label"] for x in REPORT["codes"]): REPORT["needs"].add("the database's value documentation")
        if gamma.get("columns") == "natural":
            fb, aw = G.column_labels(S, cat, entities(cat))
            REPORT["fallbacks"] += fb; REPORT["awkward"] += aw
            REPORT["needs"].add("the database's column descriptions")
    R._GAMMA.clear(); R._GAMMA.update(gamma)
    R._STEPNO.clear(); R._STEPNO.update({st["name"]: st["number"] for st in S["steps"]})
    cap = lambda t: t[:1].upper() + t[1:]
    lines = ["Step %d. %s." % (st["number"], cap(R._instruction(st["query"]))) for st in S["steps"]]   # steps: exact
    if gamma.get("columns") == "natural" and '"op": "in_query"' in __import__("json").dumps(S["query"]) or \
       gamma.get("columns") == "natural" and '"op": "exists"' in __import__("json").dumps(S["query"]) or \
       gamma.get("columns") == "natural" and '"op": "subquery"' in __import__("json").dumps(S["query"]):
        REPORT["fallbacks"].append({"kind": "subquery", "item": "a nested query", "label": None,
                                    "why": "a nested query keeps the explicit wording, with its table names"})
    if S["steps"] and gamma.get("columns") == "natural":
        REPORT["fallbacks"].append({"kind": "step", "item": "%d step(s)" % len(S["steps"]), "label": None,
                                    "why": "a step keeps the explicit wording, with its table names"})
    L = _Ledger()
    body = _natural_query(S["query"], L, cat)
    L.check(_elements(S["query"]))
    lines.append(("Step %d (the answer). " % (len(S["steps"]) + 1) + body) if S["steps"] else body)
    text = "\n".join(lines) + "\n" + R.NOTES
    # PHRASE SPANS: each component ID -> [start, end) of every phrase that states it, in the question as returned
    spans, base = {}, len("\n".join(lines[:-1])) + (1 if S["steps"] else 0)
    for el, ps in L.phrases.items():
        for p in ps:
            k = text.find(p, base)
            if k >= 0: spans.setdefault(el, []).append([k, k + len(p)])
    if S["steps"]:                                      # the steps keep the explicit wording: one span each
        pos = 0
        for i, ln in enumerate(lines[:-1]):
            spans.setdefault("steps", []).append([pos, pos + len(ln)]); pos += len(ln) + 1
    REPORT["spans"] = spans
    REPORT["symbols"] = list(_STATE.get("symbols", []))
    return text


SYMBOL_GATE_VERSION = "structural-2"      # 2026-09-28: V's legend only (structural-1 also read '(Y/N)' as symbols)


def undefined_symbols(requirements, symbols=None):
    """Formula symbols with no definition, found from FORMULA STRUCTURE, not from capital letters in prose:
      1. `symbols` -- the letters V's legend assigned while writing formulas (REPORT["symbols"]): each needs its own
         'definition X' requirement, wherever and however it is written (so A-B is covered);
      2. a single capital letter written as a formula operand -- directly beside ×, ÷, −, +, (, ), or a comma inside a
         formula -- that is not in `symbols` and has no definition.
    Prose like "grades K-12" is neither. Empty = every symbol is defined."""
    import re as _re
    defined = {k.split(" ", 1)[1] for k in requirements if k.startswith("definition ")}
    # A symbol defined INLINE by explicit V's own legend inside a requirement ("... A - B. Here A is column (3) of step 1; B is
    # ...") is defined: multi-step tasks carry their steps, legend included, as one requirement (2026-10-01: without this,
    # every multi-step task fell back before the writer saw it)
    for v in requirements.values():
        if isinstance(v, str):
            for leg in _re.findall(r"Here ((?:[A-Z]|X\d+) is .*?)(?:\.\s|\.$|$)", v):
                defined |= set(_re.findall(r"(?:^|;\s*)([A-Z]|X\d+) is ", leg))
    if symbols is not None:          # STRUCTURAL: V creates every formula symbol, and its legend lists them all
        return sorted(set(symbols) - defined)
    missing = set()                  # no legend given (a hand-written requirement set): letters beside arithmetic operators
    for k, v in requirements.items():
        if k.startswith("definition "): v = v.split(" is ", 1)[-1]
        for x in _re.findall(r"(?<![A-Za-z0-9_`'./-])([A-Z]|X\d+)(?=\s?[×÷−+])", v) + _re.findall(r"(?<=[×÷−+] )([A-Z]|X\d+)(?![A-Za-z0-9_`'/])", v):
            if x not in defined: missing.add(x)
    return sorted(missing)


def task(S, s="natural", gamma=None, cat=None):
    """V as a task: the question AND its interpretation record (specbridge.comm.verbal.interpret), from which the grader is derived.
    The record depends on the specification, not on the wording."""
    from specbridge.comm.verbal import interpret
    q = V(S, s, gamma, cat)
    unresolved = [x for x in REPORT.get("fallbacks", [])] if s == "natural" else []
    return {"question": q, "record": interpret.record(S, cat, unresolved) if cat is not None else {}}


def ledger(S, cat=None):
    R._STEPNO.clear(); R._STEPNO.update({st["name"]: st["number"] for st in S["steps"]})
    L = _Ledger(); _natural_query(S["query"], L, cat)
    return L.claims, _elements(S["query"])
