"""specbridge.pd.realize.semantic — ONE REUSABLE SEMANTIC CATALOGUE PER DATABASE, built once, read by every generation run.

    python -m specbridge.pd.realize.semantic <db> [--force] [--model sonnet]

Three steps, then a file:

  MERGE     what already exists, keeping each fact's source: types, roles and keys read from the ROWS;
            kind, unit, population and part-of from profile.json (its own record of which fields a model filled
            marks those MODEL, the rest DOC); families from families.json (MODEL); descriptions (DOC).
  REVIEW    one bounded model call: a compact summary of the database goes in, and the model is asked only for
            (a) what one row of each table represents, (b) scale, unit or entity where missing or in conflict, and
            (c) at most MAX_REL relationships worth having -- comparable quantities, a part and its whole, a rate.
            Not every column pair; not a formula catalogue.
  VALIDATE  mechanically: every referenced column exists; every field uses the fixed vocabulary; a relationship
            joins two numeric columns. What the model adds is recorded MODEL -- the generator treats it as
            PLAUSIBLE support, never as an established fact, and a contradiction resting on it excludes nothing.
  SAVE      catalogues/<db>.json in the repository, versioned by a hash of the schema, profile, families and
            documentation. Rebuilt only when one of those changes. THE ONE CATALOGUE FORMAT: generation reads
            meaning only from this file (`load`), never from profile.json or families.json, and never calls a model.
"""
from __future__ import annotations
import hashlib, json, os, re, sys, time

MAX_REL = 20
SCALES = ("nominal", "ordinal", "interval", "ratio", "unknown")
REL_KINDS = ("comparable", "part_of", "rate", "product")
ROLES = ("identifier", "category", "ordinal", "measure", "count", "date", "duration", "indicator", "unknown")
NUMERIC_ROLES = ("measure", "count", "duration", "indicator")
TYPE_OF_ROLE = {"measure": "NUM", "count": "NUM", "duration": "NUM", "indicator": "NUM", "identifier": "KEY",
                "category": "TEXT"}                 # applied only to numeric-stored columns (a text code stays TEXT)
SCALE_OF_ROLE = {"identifier": "nominal", "category": "nominal", "ordinal": "ordinal", "count": "ratio",
                 "date": "interval", "duration": "ratio", "indicator": "ratio"}
AXES = ("entities", "time")

# THE UNIT VOCABULARY: unit -> (base dimensions with exponents, factor to the base). A catalogue unit is one of these,
# a quotient "a/b" or product "a*b" of two, optionally with a number ("count/1000 count"), or unknown. Dimension and
# factor are DERIVED here, never proposed. Currencies are separate bases (no conversion rate is a fact of the data).
UNITS = {
    "fraction": ({}, 1.0), "percent": ({}, 0.01), "ratio": ({}, 1.0),
    "count": ({"count": 1}, 1.0),
    "mm": ({"length": 1}, 0.001), "cm": ({"length": 1}, 0.01), "m": ({"length": 1}, 1.0), "km": ({"length": 1}, 1000.0),
    "ug": ({"mass": 1}, 1e-9), "mg": ({"mass": 1}, 1e-6), "g": ({"mass": 1}, 1e-3), "kg": ({"mass": 1}, 1.0),
    "mL": ({"length": 3}, 1e-6), "dL": ({"length": 3}, 1e-4), "L": ({"length": 3}, 1e-3),
    "ms": ({"time": 1}, 0.001), "s": ({"time": 1}, 1.0), "min": ({"time": 1}, 60.0), "h": ({"time": 1}, 3600.0),
    "day": ({"time": 1}, 86400.0), "week": ({"time": 1}, 604800.0), "month": ({"time": 1}, 2629800.0),
    "year": ({"time": 1}, 31557600.0),
    "USD": ({"currency:USD": 1}, 1.0), "EUR": ({"currency:EUR": 1}, 1.0), "CZK": ({"currency:CZK": 1}, 1.0),
    "GBP": ({"currency:GBP": 1}, 1.0),
    "celsius": ({"temperature": 1}, 1.0), "degree": ({"angle": 1}, 1.0),
    "byte": ({"information": 1}, 1.0), "KB": ({"information": 1}, 1e3), "MB": ({"information": 1}, 1e6),
    "GB": ({"information": 1}, 1e9),
    "U": ({"activity": 1}, 1.0), "mmol": ({"substance": 1}, 1e-3), "mol": ({"substance": 1}, 1.0),
    "points": ({"score": 1}, 1.0),
}


def parse_unit(u):
    """(dimension as a sorted tuple of (base, exponent), factor) of a vocabulary unit, a quotient or product of two, or
    None when the unit is not in the vocabulary (unknown, never guessed)."""
    u = re.sub(r"\s+", " ", str(u or "").strip())
    if not u: return None
    def one(x):
        x = x.strip(); n = 1.0
        m = re.match(r"^([0-9.]+)\s*(.*)$", x)
        if m and m.group(2): n, x = float(m.group(1)), m.group(2).strip()
        if x not in UNITS: return None
        d, f = UNITS[x]; return dict(d), f * n
    for sep, sign in (("/", -1), (" per ", -1), ("*", 1), (" x ", 1)):
        if sep in u:
            a, b = u.split(sep, 1); pa, pb = one(a), one(b)
            if pa is None or pb is None: return None
            d = dict(pa[0])
            for k, e in pb[0].items(): d[k] = d.get(k, 0) + sign * e
            return tuple(sorted((k, e) for k, e in d.items() if e)), (pa[1] / pb[1] if sign < 0 else pa[1] * pb[1])
    p = one(u)
    return None if p is None else (tuple(sorted(p[0].items())), p[1])


def path(db):
    """catalogues/<db>.json at the repository root: tracked, so a clone reproduces every run that read it."""
    from specbridge import ROOT
    return os.path.join(ROOT, "catalogues", db + ".json")


class Source:
    """A database as the builder and the generator read it: its rows (`World`), its documentation, a connection."""
    def __init__(self, db, con=None):
        import sqlite3
        from specbridge.pd.corpora import sqlite as sq, docs
        from specbridge.pd.realize.world import World
        from specbridge.pd.realize.vocab import read
        self.db = db
        self.path = sq(db)
        self.con = con or sqlite3.connect("file:%s?mode=ro" % self.path, uri=True)
        self.docs = docs(db)
        self.meta = read(self.docs) or {}
        self.world = World(self.con, db, self.meta)

    def inputs(self, name):
        """A build input kept beside the database (profile.json, families.json), if present."""
        f = os.path.join(self.docs, name)
        return json.load(open(f)) if os.path.exists(f) else {}

    def sample(self, t, c, k=3):
        from specbridge.pd.structures.algebra import qname
        try:
            return [r[0] for r in self.con.execute('SELECT %s, COUNT(*) n FROM %s WHERE %s IS NOT NULL GROUP BY 1 ORDER BY n DESC LIMIT %d'
                                                   % (qname(c), qname(t), qname(c), k))]
        except Exception: return []


def slot_of(c):
    """A column's computational type, read off its rows."""
    # A DATE IS A DATE BEFORE IT IS A KEY (v2, 2026-09-30): dates unique per row (one race per day) were read as handles, so a
    # table placed in time looked timeless and a stock could be summed across times.
    return ("DATE" if c.role == "date" else "KEY" if c.handle else "NUM" if c.aff == "numeric" and c.role == "num" else
            "TEXT" if c.role in ("cat", "text") else "ANY")


RATIO_KINDS = {"count", "money", "share", "percent", "duration", "thousands"}
INTERVAL_UNITS = ("celsius", "fahrenheit", "degree", "°")


def scale_of(p, slot):
    """A column's measurement scale from EVIDENCE, never from the values it happens to hold: the profile's kind
    (ratio for counts, money, shares, durations), a documented interval unit, or a date (interval by type)."""
    kind = str(p.get("kind", "")).split()[0] if p.get("kind") else ""
    unit = str(p.get("unit", "")).lower()
    if slot == "DATE" or kind == "date": return "interval", "rows"
    if any(u in unit for u in INTERVAL_UNITS): return "interval", "model" if "unit" in set(p.get("filled", [])) else "doc"
    if kind in RATIO_KINDS: return "ratio", "doc"
    return "", ""


def corrections_path(db):
    """catalogues/corrections/<db>.json: confirmed corrections of catalogue facts, each with its evidence -- tracked,
    so a rebuild does not depend on any untracked input."""
    return os.path.join(os.path.dirname(path(db)), "corrections", db + ".json")


def _version(src):
    """A hash of everything the catalogue is derived from, so it is rebuilt exactly when an input changes."""
    h = hashlib.sha256()
    h.update(json.dumps(sorted((t, sorted(c.name for c in r.cols.values())) for t, r in src.world.rel.items())).encode())
    h.update(json.dumps(sorted(src.world.fks)).encode())
    for f in ("profile.json", "families.json"):
        p = os.path.join(src.docs, f)
        if os.path.exists(p): h.update(open(p, "rb").read())
    h.update(json.dumps(sorted((str(k), str(v.get("desc", "")) if isinstance(v, dict) else str(v)) for k, v in src.meta.items())).encode())
    if os.path.exists(corrections_path(src.db)): h.update(open(corrections_path(src.db), "rb").read())
    return h.hexdigest()[:16]


def load(src):
    """The saved catalogue of a database, checked against its inputs. The only form in which generation reads
    meaning; a missing or stale catalogue is an error that names the command that builds it."""
    f = path(src.db)
    if not os.path.exists(f):
        raise FileNotFoundError("no catalogue for %s: run  python -m specbridge.pd.realize.semantic %s" % (src.db, src.db))
    c = json.load(open(f))
    if c.get("version") != _version(src):
        raise ValueError("catalogue for %s is stale (its schema, profile or documentation changed): run  python -m specbridge.pd.realize.semantic %s --force" % (src.db, src.db))
    return c


def _parses(src, t, c):
    """Does every stored (distinct, up to 500) value of a column read as a number? A fact of the values only."""
    from specbridge.pd.structures.algebra import qname
    try: vals = [r[0] for r in src.con.execute("SELECT DISTINCT %s FROM %s WHERE %s IS NOT NULL LIMIT 500" % (qname(c), qname(t), qname(c)))]
    except Exception: return False
    def num(x):
        try: float(x); return True
        except Exception: return False
    return bool(vals) and all(num(x) for x in vals)


def _repeats(src, t):
    """Does one entity have several rows of table t: some foreign-key column of t repeats a value in the rows?"""
    from specbridge.pd.structures.algebra import qname
    for c, cc, _p, _pc in src.world.fks:
        if c != t: continue
        try:
            n, d = src.con.execute("SELECT COUNT(%s), COUNT(DISTINCT %s) FROM %s" % (qname(cc), qname(cc), qname(t))).fetchone()
            if n and d < n: return True
        except Exception: pass
    return False


def _values(src, t, c, k=200):
    from specbridge.pd.structures.algebra import qname
    try: return {str(r[0]) for r in src.con.execute("SELECT DISTINCT %s FROM %s WHERE %s IS NOT NULL LIMIT %d" % (qname(c), qname(t), qname(c), k))}
    except Exception: return set()


def merge(src):
    """What already exists, with provenance per field: types from the rows; kind, unit, population and part-of from
    profile.json (its own record of model-filled fields marks those MODEL, the rest DOC); families as comparable
    relations (MODEL); descriptions (DOC)."""
    prof, fams = src.inputs("profile.json"), src.inputs("families.json")
    cols, tables, relations = {}, {}, []
    for t, r in src.world.rel.items():
        keys = [c.name for c in r.cols.values() if c.key or c.role == "id"]
        tables[t] = {"rows": r.n, "keys": keys, "grain": "", "axes": ["entities"], "evidence": {"rows": "rows", "keys": "rows", "axes": "rule"}}
        for c in r.cols.values():
            key = "%s.%s" % (t, c.name)
            p = prof.get(key, {})
            filled = set(p.get("filled", []))
            src_of = lambda f: "model" if f in filled else "doc"
            slot = slot_of(c)
            scale, scale_ev = scale_of(p, slot)
            kind, unit, pop = p.get("kind", ""), p.get("unit", ""), p.get("population", "")
            m = src.meta.get((t, c.name)) or {}
            k0 = str(kind).split()[0] if kind else ""
            srole = ("identifier" if slot == "KEY" else "date" if slot == "DATE" else
                     {"count": "count", "money": "measure", "share": "measure", "percent": "measure", "duration": "duration",
                      "indicator": "indicator", "thousands": "count"}.get(k0, "unknown"))
            parsed = parse_unit(unit)
            sc = SCALE_OF_ROLE.get(srole) or scale or "unknown"
            cols[key] = {
                "type": slot, "storage": c.aff, "parses": _parses(src, t, c.name), "semantic_role": srole, "role": c.role,
                "key": bool(c.key), "kind": kind, "quantity": "",
                "unit": unit if parsed else "", "unit_text": unit if unit and not parsed else "",
                "scale": sc, "order": None, "additive": {ax: None for ax in AXES},
                "entity": "", "population": pop, "period": "", "desc": (m.get("desc") or "")[:160] if isinstance(m, dict) else "",
                "evidence": {"type": "rows", "role": "rows", "semantic_role": "schema" if srole in ("identifier", "date") else "doc" if srole != "unknown" else "",
                             "kind": "doc" if kind else "", "unit": src_of("unit") if unit and parsed else "",
                             "scale": "rule" if srole in SCALE_OF_ROLE else scale_ev if scale else "", "population": src_of("population") if pop else ""},
                "confidence": {}, "alternatives": {}}
            for whole in p.get("part_of", []):
                relations.append({"a": key, "b": whole, "kind": "part_of", "evidence": src_of("part_of")})
    # CONFIRMED CORRECTIONS (tracked), applied over every other input with their own evidence
    fix_file = corrections_path(src.db)
    for key, fx in (json.load(open(fix_file)) if os.path.exists(fix_file) else {}).items():
        c = cols.get(key)
        if c is None: continue
        ev = fx.get("evidence") or {}
        for f, val in fx.items():
            if f == "evidence": continue
            if f == "unit" and parse_unit(val) is None: continue
            c[f] = val; c["evidence"][f] = ev.get("source", "doc"); c.setdefault("corrected", []).append(f)
            if f == "unit": c["unit_text"] = ""
        c.setdefault("corrections", []).append(ev.get("note", ""))
    for name, f in fams.items():
        members = f.get("members", [])
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                relations.append({"a": members[i], "b": members[j], "kind": "comparable", "evidence": "model", "family": name})
    return {"columns": cols, "tables": tables, "relations": relations}


def summary(src, merged, samples=3):
    """The compact description the model reviews: schema, keys, known annotations, a few values."""
    lines = []
    for t, info in merged["tables"].items():
        lines.append("TABLE %s (%d rows; keys: %s)" % (t, info["rows"], ", ".join(info["keys"]) or "none"))
        for key, c in merged["columns"].items():
            if not key.startswith(t + "."): continue
            vals = [str(v)[:24] for v in src.sample(t, key.split(".", 1)[1], samples)]
            known = ", ".join("%s=%s" % (f, c.get(f)) for f in ("semantic_role", "kind", "unit", "unit_text", "scale", "population")
                              if c.get(f) and c.get(f) != "unknown" and c["evidence"].get(f, "x") != "")
            lines.append("  %s: %s%s%s%s | e.g. %s" % (key.split(".", 1)[1], c["type"], " (stored as number)" if c.get("storage") == "numeric" and c["type"] != "NUM" else "",
                                                     " [" + known + "]" if known else "",
                                                     " -- " + c["desc"] if c["desc"] else "", "; ".join(vals)))
    for c, cc, p, pc in src.world.fks: lines.append("LINK %s.%s -> %s.%s" % (c, cc, p, pc))
    return "\n".join(lines)


PROMPT = """You are describing what the columns of a SQL database mean. Facts already established are shown in
[brackets]; do not contradict them. Answer ONLY with one JSON object, no prose, with exactly these keys:

"tables": {"<table>": {"grain": "<what one row is, a few words>", "axes": ["entities"] or ["entities", "time"]}}
   for every table. "time" only when one entity has several rows over time (a transaction log, repeated lab tests).
"columns": {"<table>.<column>": {...}} for EVERY column not marked KEY, each with:
   "role": one of identifier | category | ordinal | measure | count | date | duration | indicator | unknown
      identifier names a thing (codes, phone numbers); category = unordered classes; ordinal = ordered classes
      (grades, severity levels, '-' < '+' < '++'); measure = a quantity (money, a lab value, a length, a share);
      count = a number of things; duration = a length of time; indicator = 0/1 yes/no.
   "quantity": what is measured or named, a few words (not the unit).
   "unit": ONE of %s, or a quotient "a/b" or product "a*b" of two of them, a number allowed ("count/1000 count"),
      or "" when not a measure/count/duration or you cannot tell. Counts of any kind of thing are "count".
   "scale": nominal | ordinal | interval | ratio | unknown (ratio: a true zero; interval: differences only).
   "order": for an ordinal only: its stored values in increasing order (as stored), or "numeric"; else null.
   "additive": {"entities": true|false|null, "time": true|false|null} -- is a SUM meaningful across different
      entities, and across one entity's rows over time? (a transaction amount: true, true; an account balance:
      true, false; an average or a percentage: false, false). null when unknown or not a measure.
   "population": whom the value is about; "period": the period it covers ("" when none).
   "confidence": "high" or "low"; "alternatives": other readings you considered, a few words each ([] if none).
"relations": at most %d objects {"a": "<table>.<column>", "b": "<table>.<column>", "kind": "comparable|part_of|rate|product",
   "result": "<what the combination is, with its unit>", "condition": "<when it holds, e.g. same school and year>"}
   comparable = the same kind of quantity (adding or subtracting is meaningful); part_of = a is a part of b (same
   population); rate = a / b is itself a meaningful quantity; product = a * b is. Only relationships a domain
   expert would use; do not connect every pair.

Use "unknown", null or "" whenever the name, description and values do not support a fact.

DATABASE:
%s
"""


def review(src, merged, model, log=print):
    from specbridge.pd.ask import ask
    prompt = PROMPT % (", ".join(sorted(UNITS)), MAX_REL, summary(src, merged))
    t0 = time.time()
    raw = ask(prompt, model, n=16000, timeout=900, strip=True, quiet=True)
    log("   model review: %d prompt chars, %.0fs" % (len(prompt), time.time() - t0))
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m: return {}, "no JSON in the reply"
    try: return json.loads(m.group(0)), ""
    except Exception as e: return {}, "unparsable JSON: %s" % str(e)[:80]


def refuted_by_rows(src, a, b):
    """A part cannot exceed its whole. For two columns of one table the rows decide it: refuted when more than 1% of
    the rows holding both have a > b. Across tables there is no row pairing to read, so nothing is refuted."""
    (ta, ca), (tb, cb) = a.split(".", 1), b.split(".", 1)
    if ta != tb: return False
    from specbridge.pd.structures.algebra import qname
    q = "SELECT AVG(CASE WHEN %s > %s THEN 1.0 ELSE 0 END) FROM %s WHERE %s IS NOT NULL AND %s IS NOT NULL" % (
        qname(ca), qname(cb), qname(ta), qname(ca), qname(cb))
    try: v = src.con.execute(q).fetchone()[0]
    except Exception: return False
    return v is not None and v > 0.01


def validate(merged, proposal, src=None):
    """Keep only what the vocabulary, the schema and the rows allow; everything kept is recorded MODEL with its
    confidence and alternatives. Established facts (rows, schema, doc) are never overridden; what cannot be checked
    and is not supported stays unknown."""
    cols, tables, rejected, accepted = merged["columns"], merged["tables"], [], 0
    for t, v in (proposal.get("tables") or {}).items():
        if t not in tables or not isinstance(v, dict): rejected.append(("table", t)); continue
        g = str(v.get("grain") or "").strip()
        if g: tables[t]["grain"] = g[:80]; tables[t]["evidence"]["grain"] = "model"; accepted += 1
        ax = v.get("axes")
        has_date = any(k.startswith(t + ".") and c["type"] == "DATE" for k, c in cols.items())
        if isinstance(ax, list) and set(ax) <= set(AXES) and "entities" in ax:
            if "time" in ax and not has_date: rejected.append(("time axis without a date column", t))
            elif "time" in ax and src is not None and not _repeats(src, t):
                rejected.append(("time axis: no entity repeats in the rows", t))
            else: tables[t]["axes"] = list(ax); tables[t]["evidence"]["axes"] = "model"; accepted += 1
    # THE TIME AXIS FROM THE ROWS: a table has a date column and one entity has several rows (a repeating foreign
    # key) -- its rows vary over time, whatever was proposed. A column's own additivity then decides a SUM.
    if src is not None:
        for t in tables:
            if "time" not in tables[t]["axes"] and any(k.startswith(t + ".") and c["type"] == "DATE" for k, c in cols.items()) and _repeats(src, t):
                tables[t]["axes"] = tables[t]["axes"] + ["time"]; tables[t]["evidence"]["axes"] = "rows"
    for key, v in (proposal.get("columns") or {}).items():
        c = cols.get(key)
        if c is None or not isinstance(v, dict): rejected.append(("column", key)); continue
        ev, conf = c["evidence"], v.get("confidence") if v.get("confidence") in ("high", "low") else "low"
        def keep(f, val):
            nonlocal accepted
            if f in c.get("corrected", ()): return      # a confirmed correction outranks the model review
            c[f] = val; ev[f] = "model"; c["confidence"][f] = conf; accepted += 1
        numeric = c.get("storage") == "numeric" or c.get("parses")
        role = v.get("role")
        if role in ROLES and role != "unknown" and ev.get("semantic_role") not in ("schema", "rows"):
            if role in NUMERIC_ROLES and not numeric: rejected.append(("numeric role of non-numeric values", key, role))
            elif role == "date" and c["type"] != "DATE": rejected.append(("date role without date values", key))
            else:
                keep("semantic_role", role)
                if c.get("storage") == "numeric" and not c["key"] and role in TYPE_OF_ROLE and ev.get("type") != "doc":
                    c["type"] = TYPE_OF_ROLE[role]; ev["type"] = "model"
                if role == "indicator": c["kind"] = c["kind"] or "indicator"
                if role in SCALE_OF_ROLE: c["scale"] = SCALE_OF_ROLE[role]; ev["scale"] = "rule"
        elif role not in ROLES and role is not None: rejected.append(("role", key, role))
        q = str(v.get("quantity") or "").strip()
        if q: keep("quantity", q[:60])
        u = str(v.get("unit") or "").strip()
        if u:
            if c["semantic_role"] not in NUMERIC_ROLES: rejected.append(("unit on a non-quantity", key, u))
            elif parse_unit(u) is None: rejected.append(("unit outside the vocabulary", key, u))
            elif not c["unit"] or ev.get("unit") not in ("doc", "rows"): keep("unit", u); c["unit_text"] = ""
        sc = v.get("scale")
        if sc in SCALES and sc != "unknown" and c["semantic_role"] not in SCALE_OF_ROLE and ev.get("scale") not in ("rows", "doc", "rule"):
            keep("scale", sc)
        order = v.get("order")
        if order is not None:
            if c["semantic_role"] != "ordinal": rejected.append(("order on a non-ordinal", key))
            elif order == "numeric":
                if numeric: keep("order", "numeric")
                else: rejected.append(("numeric order of non-numeric values", key))
            elif isinstance(order, list) and order and src is not None:
                seen = _values(src, *key.split(".", 1))
                if all(str(x) in seen for x in order): keep("order", [str(x) for x in order])
                else: rejected.append(("order names values not in the rows", key))
        add = v.get("additive")
        if isinstance(add, dict) and c["semantic_role"] in NUMERIC_ROLES:
            vals = {ax: add.get(ax) for ax in AXES if add.get(ax) in (True, False)}
            if vals: c["additive"].update(vals); ev["additive"] = "model"; c["confidence"]["additive"] = conf; accepted += 1
        for f in ("population", "period"):
            x = str(v.get(f) or "").strip()
            if x and not (f == "population" and c["population"]): keep(f, x[:60])
        alts = v.get("alternatives")
        if isinstance(alts, list) and alts: c["alternatives"] = [str(a)[:60] for a in alts[:3]]
    for r in (proposal.get("relations") or [])[:MAX_REL]:
        a, b, k = r.get("a"), r.get("b"), r.get("kind")
        if k == "part_of" and src is not None and a in cols and b in cols and refuted_by_rows(src, a, b):
            rejected.append(("part_of refuted by rows", (a, b))); continue
        if a in cols and b in cols and a != b and k in REL_KINDS and cols[a]["type"] == "NUM" and cols[b]["type"] == "NUM":
            merged["relations"].append({"a": a, "b": b, "kind": k, "evidence": "model", "result": str(r.get("result", ""))[:60],
                                        "condition": str(r.get("condition", ""))[:60]}); accepted += 1
        else: rejected.append(("relation", (a, b, k)))
    return accepted, rejected


def build(db, force=False, model=None, log=print, revalidate=False):
    from specbridge.pd.models import PROFILER
    model = model or PROFILER
    src = Source(db)
    v = _version(src)
    p = path(db)
    if os.path.exists(p) and not force and not revalidate:
        old = json.load(open(p))
        if old.get("version") == v:
            log("%s: catalogue is current (version %s); nothing to do" % (db, v)); return old
    merged = merge(src)
    if revalidate and os.path.exists(p) and json.load(open(p)).get("proposal"):
        proposal, err = json.load(open(p))["proposal"], ""            # the saved model proposal, validated again
        log("   revalidating the saved proposal (no model call)")
    else:
        proposal, err = review(src, merged, model, log)
    accepted, rejected = validate(merged, proposal, src) if not err else (0, [("review", err)])
    out = {"version": v, "built": time.strftime("%Y-%m-%d %H:%M"), "model": model, **merged,
           "review": {"accepted": accepted, "rejected": rejected[:30], "error": err}, "proposal": proposal}
    json.dump(out, open(p, "w"), indent=1)
    n_model = sum(1 for c in merged["columns"].values() if "model" in c["evidence"].values())
    log("%s: catalogue %s written: %d columns (%d with a model annotation), %d tables, %d relations; review accepted %d, rejected %d%s" % (
        db, v, len(merged["columns"]), n_model, len(merged["tables"]), len(merged["relations"]), accepted, len(rejected),
        " (" + err + ")" if err else ""))
    return out


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else None
    if model in args: args.remove(model)
    for db in args or ["california_schools"]:
        build(db, force="--force" in sys.argv, model=model, revalidate="--revalidate" in sys.argv)
