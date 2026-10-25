"""ENSURE A DATABASE'S LANGUAGE RESOURCE: human-readable names for its columns, tables and documented codes, grounded in the
catalogue and the database's own documentation. A setup step: after the catalogue, before natural questions are written.
    python -m specbridge.comm.verbal.language <db> [--corpus <dir>]      -> catalogues/language/<db>.json, out/language/<db>/
  1 gaps      write each given task as a natural question by rule (specbridge.comm.verbal.verbalize, gamma natural) and collect every
              column, table or code that fell back to its raw name or came out awkward
  2 propose   ONE model call per database (sonnet) for the gaps not tried before, with only the evidence: documentation,
              schema, catalogue entries, sample values. A code's meaning only when the documentation states it.
  3 accept    by rule, never by the model: a column label is a phrase of at most 8 words, with evidence, not low confidence,
              unique in its table; a table name a plain noun (singular, plural, <= 3 words); a code meaning <= 5 words, the
              code in the column's documentation and a stored value. Everything else is rejected with its reason.
  4 merge     accepted entries join catalogues/language/<db>.json marked "accepted by rule checks; pending human review";
              entries already there (including the six reviewed, FROZEN resources) are never overwritten
CACHE: out/language/<db>/state.json records, per catalogue version and rules version, every item already tried (accepted or
rejected); a rerun proposes only new gaps, and a changed catalogue or rule set starts the tried list afresh.
The prompt and the acceptance rules are the ones of out/verbalize/propose.py and accept.py (2026-09-28), moved here unchanged.
Generation never calls a model; only this step and the writers do."""
import ast, collections, hashlib, json, os, re, sys, time

OUT = "out/language"
MODEL = "sonnet"
GM = {"columns": "natural", "values": "natural"}
KINDS = ("column", "table", "code")

PROMPT = """You are writing reusable labels for a database, used to phrase questions about it in plain English.
For each ITEM below, propose ONE precise label, using only the EVIDENCE given (documentation, schema, catalogue, sample values).

Rules:
- COLUMN: a short noun phrase (at most 8 words) saying what one value of the column is, precise enough to tell it apart
  from every other column of its table. KEEP POPULATION AND SCOPE DISTINCTIONS (e.g. "ages 5-17" vs "K-12", "IgA" vs "IgM",
  "eye" vs "skin"). A label that resembles the column name is fine when it is clear ("eye colour id"). Expand
  abbreviations only when the evidence states the expansion.
- TABLE: the entity one row is, as a plain noun: {"singular": ..., "plural": ...} (e.g. "school meal record").
- CODE: a short phrase (at most 5 words) for what a stored code means -- ONLY when the documentation states that meaning.
  If the documentation does not state it, answer "UNRESOLVED". Never guess a code's meaning from its spelling.
- If the evidence does not support a precise label, answer "UNRESOLVED".

Answer with ONLY a JSON list, one object per item, in the same order:
[{"item": "<item as given>", "kind": "column|table|code", "proposal": <string or {"singular","plural"} or "UNRESOLVED">,
  "evidence": "<the words of the evidence you relied on>", "confidence": "high|medium|low"}]

DATABASE: %s

ITEMS AND EVIDENCE:
%s
"""
RULES_VERSION = hashlib.sha1((PROMPT + "accept-rules-2026-09-28").encode()).hexdigest()[:10]


def gaps(db, sqls):
    """Items (kind, item) whose natural wording fell back or is awkward, over the given SQL, with their current label."""
    from specbridge.pd.structures.algebra import lift
    from specbridge.pd.spec import render as R
    from specbridge.comm.common import db as DB
    from specbridge.comm.verbal import verbalize as VZ
    cat = DB.catalogue(db); out = {}
    for sql in sqls:
        try:
            s = R.spec(lift(sql, cat.con), cat); VZ.V(s, "natural", gamma=GM, cat=cat)
        except Exception: continue
        rep = json.loads(json.dumps(VZ.REPORT, default=list))
        for x in rep.get("fallbacks", []) + rep.get("awkward", []):
            if x.get("kind") in KINDS:
                g = out.setdefault((x["kind"], x["item"]), {"database": db, "kind": x["kind"], "item": x["item"], "current": x.get("label"), "why": x.get("why"), "tasks": 0})
                g["tasks"] += 1
    return list(out.values())


def evidence(db, con, docs, cat, x):
    """The evidence for one item (as in out/verbalize/propose.py)."""
    if x["kind"] == "column":
        t, c = x["item"].split(".", 1)
        d = docs.get((t, c), {})
        sibs = [k.split(".", 1)[1] for k in cat if k.startswith(t + ".") and k != x["item"]]
        try: vals = [r[0] for r in con.execute('SELECT DISTINCT "%s" FROM "%s" WHERE "%s" IS NOT NULL LIMIT 6' % (c, t, c))]
        except Exception: vals = []
        e = cat.get(x["item"], {})
        return {"item": x["item"], "kind": "column", "current label": x["current"], "why it is a gap": x["why"],
                "documentation": {"description": d.get("desc", ""), "values": (d.get("values") or "")[:400]},
                "catalogue": {k: e.get(k) for k in ("quantity", "desc", "population", "entity", "unit", "semantic_role")},
                "other columns of the table": sibs[:40], "sample values": [str(v)[:40] for v in vals]}
    if x["kind"] == "table":
        t = x["item"]
        cols = [k.split(".", 1)[1] for k in cat if k.startswith(t + ".")]
        try: fks = [list(f[2:5]) for f in con.execute('PRAGMA foreign_key_list("%s")' % t)]
        except Exception: fks = []
        return {"item": t, "kind": "table", "why it is a gap": x["why"], "catalogue grain": x.get("grain"), "columns": cols[:40], "declared keys": fks}
    t, rest = x["item"].split(".", 1); c, code = rest.split(" = ", 1)
    d = docs.get((t, c), {})
    try: vals = [r[0] for r in con.execute('SELECT DISTINCT "%s" FROM "%s" LIMIT 25' % (c, t))]
    except Exception: vals = []
    return {"item": x["item"], "kind": "code", "why it is a gap": x["why"], "current documented meaning": x["current"],
            "documentation of the column": {"description": d.get("desc", ""), "values": (d.get("values") or "")[:800]},
            "stored values of the column": [str(v)[:40] for v in vals]}


def accept(db, proposals, ev, lang):
    """The acceptance rules of out/verbalize/accept.py: adds accepted entries to `lang`; returns {item: verdict}."""
    from specbridge.pd.realize.catalogue import Catalogue
    from specbridge.pd.spec.render import _label
    from specbridge.comm.verbal.gamma import _observed, _norm
    cat = Catalogue(db); verdict = {}
    for p in proposals:
        kind, item, prop = p.get("kind"), p.get("item"), p.get("proposal")
        why = None
        if prop in (None, "", "UNRESOLVED"): why = "unresolved"
        elif not (p.get("evidence") or "").strip(): why = "no evidence"
        elif kind == "column":
            t, c = item.split(".", 1)
            others = {_norm(v["label"]) for k, v in lang["columns"].items() if k.startswith(t + ".") and k != item}
            others |= {_norm(_label(cat, t, x.name)[0]) for x in cat.cols.get(t, []) if x.name != c and "%s.%s" % (t, x.name) not in lang["columns"]}
            if not isinstance(prop, str) or len(prop.split()) > 8 or "`" in prop: why = "not a short phrase"
            elif p.get("confidence") == "low": why = "low confidence"
            elif _norm(prop) in others: why = "not unique in its table"
            elif item in lang["columns"]: why = "already labelled (kept)"
            else: lang["columns"][item] = {"label": prop.strip(), "evidence": p["evidence"][:300], "confidence": p.get("confidence"), "status": "accepted by rule checks; pending human review"}
        elif kind == "table":
            ok = isinstance(prop, dict) and all(isinstance(prop.get(k), str) and re.fullmatch(r"[A-Za-z][A-Za-z -]*", prop[k]) and len(prop[k].split()) <= 3 for k in ("singular", "plural"))
            if not ok: why = "not a plain noun"
            elif item in lang["entities"]: why = "already named (kept)"
            else: lang["entities"][item] = {"singular": prop["singular"].strip(), "plural": prop["plural"].strip(), "evidence": p["evidence"][:300], "status": "accepted by rule checks; pending human review"}
        elif kind == "code":
            t, rest = item.split(".", 1); c, code = rest.split(" = ", 1)
            try: code_v = ast.literal_eval(code)
            except Exception: code_v = code.strip("'\"")
            doc = json.dumps(ev.get(item, {}).get("documentation of the column", {}))
            if not isinstance(prop, str) or len(prop.split()) > 5: why = "not a short phrase"
            elif str(code_v) not in doc: why = "the code is not in the documentation (a meaning would be a guess)"
            elif _observed(cat.con, t, c, str(code_v)) is None: why = "not a stored value"
            else: lang["codes"].setdefault("%s.%s" % (t, c), {})[repr(code_v)] = {"label": prop.strip(), "evidence": p["evidence"][:300], "status": "accepted by rule checks; pending human review"}
        else: why = "unknown kind"
        verdict[item] = "accepted" if not why else "rejected: " + why
    return verdict


def ensure(db, sqls, log=print):
    """The language resource of db covers the gaps of these SQL queries as far as the rules allow. -> summary dict."""
    from specbridge.pd.corpora import found
    from specbridge.pd.realize.vocab import read
    from specbridge.comm.construct.freeze import snapshot
    from specbridge.comm.common.llm import ask_json
    import sqlite3
    t0 = time.time(); d = "%s/%s" % (OUT, db); os.makedirs(d, exist_ok=True)
    catv = json.load(open("catalogues/%s.json" % db)).get("version")
    sf = d + "/state.json"; state = json.load(open(sf)) if os.path.exists(sf) else {}
    if state.get("catalogue") != catv or state.get("rules") != RULES_VERSION: state = {"catalogue": catv, "rules": RULES_VERSION, "tried": {}}
    G = gaps(db, sqls); todo = [g for g in G if g["item"] not in state["tried"]]
    res = {"db": db, "gaps": len(G), "new": len(todo), "accepted": 0, "rejected": collections.Counter(), "model_calls": 0}
    if todo:
        lp = "catalogues/language/%s.json" % db
        lang = json.load(open(lp)) if os.path.exists(lp) else {"status": "built by specbridge.comm.verbal.language (accepted by rule checks; pending human review)", "model": MODEL, "columns": {}, "entities": {}, "codes": {}}
        cat = json.load(open("catalogues/%s.json" % db))
        for x in todo:
            if x["kind"] == "table": x["grain"] = cat.get("tables", {}).get(x["item"], {}).get("grain")
        con = sqlite3.connect("file:%s?mode=ro" % snapshot(db)[0], uri=True)
        docs = read(found(db)) if found(db) and os.path.isdir(os.path.join(found(db), "database_description")) else {}
        ev = {x["item"]: evidence(db, con, docs, cat["columns"], x) for x in todo}
        props = []
        for i in range(0, len(todo), 60):                       # one call per database; very large gap lists in chunks of 60
            chunk = [ev[x["item"]] for x in todo[i:i + 60]]
            r = ask_json(PROMPT % (db, json.dumps(chunk, indent=1, default=str)), MODEL, brace="[", cache=d + "/cache") or []
            props += [p for p in r if isinstance(p, dict)]; res["model_calls"] += 1
        verdict = accept(db, props, ev, lang)
        for x in todo: state["tried"][x["item"]] = verdict.get(x["item"], "rejected: no proposal returned")
        res["accepted"] = sum(v == "accepted" for v in verdict.values())
        res["rejected"] = collections.Counter(v.split(": ", 1)[1] for v in state["tried"].values() if v.startswith("rejected"))
        os.makedirs(os.path.dirname(lp), exist_ok=True); json.dump(lang, open(lp, "w"), indent=1)
        json.dump({"database": db, "model": MODEL, "evidence": list(ev.values()), "proposals": props, "verdicts": verdict}, open(d + "/proposals_%s.json" % time.strftime("%Y%m%d-%H%M%S"), "w"), indent=1, default=str)
    json.dump(state, open(sf, "w"), indent=1)
    res["seconds"] = round(time.time() - t0, 1); res["rejected"] = dict(res["rejected"])
    log("language %s: %d gaps, %d new, %d accepted, %d model calls, %.0fs%s" % (db, res["gaps"], res["new"], res["accepted"], res["model_calls"], res["seconds"],
                                                                          "; rejected %s" % res["rejected"] if res["rejected"] else ""))
    return res


def probe_sqls(db, per_cell=3, seed=0):
    """SQL to find a database's gaps at setup time, before any corpus exists: probe programs drawn in every reachable cell."""
    import random
    from specbridge.pd.structures.compose import Space, Sampler
    sp = Space(db); smp = Sampler(sp, random.Random(seed)); out = []
    for c in sorted(sp.reachable()):
        for _ in range(per_cell):
            P = smp.draw(c)
            if P is not None: out.append(P.sql())
    return out


if __name__ == "__main__":
    a = sys.argv[1:]; db = a[0]
    if "--corpus" in a:
        sqls = [json.loads(l)["reference_sql"] for l in open(a[a.index("--corpus") + 1] + "/tasks.jsonl") if json.loads(l)["database"] == db]
    else: sqls = probe_sqls(db)
    ensure(db, sqls)
