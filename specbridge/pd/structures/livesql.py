"""specbridge.pd.structures.livesql — READING LIVESQLBENCH.

The dataset ships its questions in one file and its gold SQL in another, with the knowledge entries a question was
written against in a third. This pairs them. It is a READER, nothing more — no judgement about the questions is made
here, and `specbridge.pd.structures.mine` and `pd.validate` both come through it so there is one path to the data rather than two that can
drift apart.
"""
from __future__ import annotations
import json, os, re


def load(kb_root="livesqlbench_data", gt="livesql_dbs/livesqlbench_gt_kg_testcases_0528.jsonl",
         qs="livesqlbench_data/livesqlbench_data_sqlite.jsonl"):
    """(question, gold sql, database, the knowledge entries the question was written with) per instance."""
    G = {r["instance_id"]: r for r in (json.loads(l) for l in open(gt))}
    out = []
    kbs = {}
    for r in (json.loads(l) for l in open(qs)):
        g = G.get(r["instance_id"])
        if not g: continue
        sql = g.get("sol_sql")
        sql = " ".join(x for x in sql if isinstance(x, str)) if isinstance(sql, list) else (sql or "")
        if not sql.strip(): continue
        db = r["selected_database"]
        if db not in kbs:
            p = f"{kb_root}/{db}/{db}_kb.jsonl"
            kbs[db] = {e["id"]: e for e in (json.loads(l) for l in open(p))} if os.path.exists(p) else {}
        used = r.get("external_knowledge") or g.get("external_knowledge") or []
        if isinstance(used, str):
            used = [int(x) for x in re.findall(r"\d+", used)]
        # A CONCEPT IS OFTEN DEFINED BY OTHER CONCEPTS, NOT BY COLUMNS. `Observation Quality Factor = AOI x (1 - LIF)
        # x ...` names no column at all; the columns are at the leaves of `children_knowledge`. Taking only the
        # entries a question cites left every column reachable through a chain looking unstated.
        seen, stack = set(), list(used)
        while stack:
            i = stack.pop()
            if i in seen or i not in kbs[db]: continue
            seen.add(i)
            ch = kbs[db][i].get("children_knowledge")
            if isinstance(ch, list): stack += [x for x in ch if isinstance(x, int) and x >= 0]
            elif isinstance(ch, int) and ch >= 0: stack.append(ch)
        out.append({"id": r["instance_id"], "db": db, "question": r.get("query", ""), "sql": sql,
                    "knowledge": [kbs[db][i] for i in used if i in kbs[db]],
                    "closure": [kbs[db][i] for i in seen]})
    return out


def meanings(db, kb_root="livesqlbench_data"):
    p = f"{kb_root}/{db}/{db}_column_meaning_base.json"
    if not os.path.exists(p): return {}
    raw = json.load(open(p))
    # LOWERCASED ON BOTH SIDES. The file writes `alien|Observatories|ObservStation` and a lifted program says
    # `observatories.observstation`, so every lookup missed and every column reached the judge described only by its
    # own cryptic name — `snrratio`, `observstation`. The model cannot tell whether a phrase means THAT, so it said
    # no, and 61% of references came back "unstated" as a property of a failed dictionary lookup.
    out = {}
    for k, v in raw.items():
        parts = k.split("|")
        if len(parts) == 3: out[(parts[1].lower(), parts[2].lower())] = v
    return out


# ---------------------------------------------------------------- the short name a meaning gives
_VERBS = (r"(?:used\s+)?(?:for|representing|indicating|measuring|holding|counting|showing|storing|giving|recording|denoting|"
          r"describing|containing|identifying|listing|marking|noting|reflecting|specifying|tracking|capturing|scoring|rating|"
          r"estimating|quantifying|expressing|stating|flagging|signalling|signaling|assessing|summarizing|summarising|reporting|"
          r"logging|labeling|labelling|tagging|naming|estimating|computing|calculating|enumerating|with|of|that|which|"
          r"to record|to store|to track|to indicate)")
_TYPE = (r"(?:enum\s*\([^)]*\)|[A-Z][A-Za-z0-9_]*(?:\([^)]*\))?(?:\s*\([^)]*\))?)(?:\s+(?:field|value|column|number|float|integer))?")


def short_of(meaning, most=6):
    """A SHORT NAME FROM A DOCUMENTED MEANING, by this source's own formats and nothing else:
        "Full name: 'X'. Explanation: ..."               -> X
        "A TYPE [(range)] <verb> <phrase> (e.g., ...)"   -> the phrase, verb and example stripped
        "TYPE. <phrase> (e.g., ...)"                     -> the phrase
    None where the sentence follows neither, or names a key -- a question computes on no key. The namer
    (`pd.say.Namer`) takes a short name of at most six words over a sentence; LiveSQLBench's sentences
    ("A NUMERIC(5,3) wallet turnover rate (e.g., 5.234).") reached questions as the raw handle
    `wallturnrt`, and 29 of 69 attempts on one database were refused for it."""
    s = str(meaning).strip()
    # THE SOURCE'S OWN TAILS: "; values: 'A', 'B'" and "; possible values include ..." are the enum's list, not
    # its name; "explaining X" and "defining X" lead with a verb that says nothing about which column
    s = re.split(r"\s*[;(,]?\s*(?:possible\s+|allowed\s+)?values\s*(?:include|are|[:=])", s, 1)[0]
    s = re.sub(r"\b(?:explaining|defining)\s+", "", s)
    m = re.match(r"^Full name:\s*'([^']+)'", s)
    if m: return m.group(1).strip()
    m = re.match(r"^(?:(?:A|An)\s+)?%s[.:]?\s+(?:%s\s+)?(.+?)\s*$" % (_TYPE, _VERBS), s)
    if not m: return None
    ph = m.group(1)
    ph = re.split(r"\s*\((?:e\.g\.|i\.e\.|possible values|for example|such as|in |one of|allowed values)", ph)[0]
    ph = re.split(r"\s*[;,]\s*(?:e\.g\.|i\.e\.|such as|for example)", ph)[0]
    ph = re.sub(r"\s*\(e\.g\.,?.*$", "", ph).strip().rstrip(".,;:")
    ph = re.sub(r"^(?:the|a|an)\s+", "", ph)
    ph = re.sub(r"^(?:how many|how much|how|what|whether|if|when|where)\s+", "", ph)
    # A NAME IS A NOUN PHRASE, NOT A CLAUSE: "this disaster event record was created" and "lessons learned
    # documentation is handled" are what the sentence said about the column, not what it is called
    if re.match(r"^(?:this|that|these|those|it|they|there)\b", ph, re.I): return None
    if re.search(r"\b(?:is|are|was|were|be|been|can|could|must|should|will|would|has|have|had)\b", ph): return None
    ph = re.sub(r"\s*\([^)]*\)\s*$", "", ph).strip()
    if re.search(r"\b(?:foreign key|primary key|references|referencing|identifier|unique id|uuid)\b", ph, re.I): return None
    if re.search(r"\b(?:e\.g|i\.e|if and how|whether)\b", ph): return None
    return ph if 1 <= len(ph.split()) <= most else None


def written(db_dir, db, kb_root="livesqlbench_data"):
    """`written.json` beside a source database, from its column meanings: the sentence as `desc` and the
    short name `short_of` reads from it. The sentence is written once; the short name is recomputed from it
    on every run, so the file always carries the current rule's output; other fields are kept."""
    p = os.path.join(db_dir, "written.json")
    old = json.load(open(p)) if os.path.exists(p) else {}
    m = meanings(db, kb_root)
    if not m: return old
    # the short name is recomputed on every run: it is the rule's output, not a fact of the source
    out = dict(old)
    # the meaning file's own table and column spelling, so the key matches the schema
    raw = json.load(open(f"{kb_root}/{db}/{db}_column_meaning_base.json"))
    for k, v in raw.items():
        parts = k.split("|")
        if len(parts) != 3: continue
        key = "%s|%s" % (parts[1], parts[2])
        e = dict(out.get(key) or {})
        e.update({"desc": str(v), "written": False, "source": "livesqlbench column meaning"})
        sh = short_of(v)
        if sh: e["short"] = sh
        else: e.pop("short", None)
        out[key] = e
    with open(p, "w") as fh: json.dump(out, fh, indent=0, sort_keys=True)
    return out
