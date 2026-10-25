"""Checks of the verbalizer V(S; s, gamma).  python -m specbridge.comm.verbal.test_verbalize [tasks.jsonl ...]

TEMPLATE MEANING, on small queries written for each case: each natural template states its requirement with the
SQL's scope and meaning (a record filter before grouping, a group filter after; an unmatched record dropped or kept;
where missing values sort; text in character order; duplicates; skip-then-take).
OVER FROZEN TASKS: V(S; explicit) is the frozen instruction; V(S; natural) either states every requirement (the
ledger) or is refused by name; every filter, column, sort key and limit the explicit style states is stated, word for
word, in the natural one (gamma explicit: handles, codes and formulas unchanged).
"""
import json, sqlite3, sys, warnings
warnings.filterwarnings("ignore")
from specbridge.pd.structures.algebra import lift
from specbridge.pd.realize.catalogue import Catalogue
from specbridge.pd.spec import render as R
from specbridge.comm.verbal.verbalize import V, ledger, _Ledger, _elements, _plural

FAILED = []


def check(name, ok):
    print("  %-100s %s" % (name, "ok" if ok else "FAILED"))
    if not ok: FAILED.append(name)


def S(cat, sql): return R.spec(lift(sql, cat.con), cat)


def templates():
    fin = Catalogue("financial")
    N = lambda sql: V(S(fin, sql), "natural", cat=fin)
    t = N("SELECT a.district_id, COUNT(*) FROM account AS a WHERE a.frequency = 'POPLATEK MESICNE' "
          "GROUP BY a.district_id HAVING COUNT(*) > 5 ORDER BY 2 DESC LIMIT 3")
    check("record filter stated on the entity, before the group filter", "Include only the bank accounts for which" in t and
          t.index("Include only the bank accounts") < t.index("Keep only the groups for which"))
    check("a concise count names the entity", "the number of bank accounts" in t)
    check("group filter stated as groups, with the same concise count", "Keep only the groups for which the number of bank accounts is greater than 5" in t)
    check("the entity is defined by its table", "a bank account is one `account` record" in t)
    check("grouping: for each key value", "For each location of branch (`account.district_id`), show one row" in t)
    check("descending number: highest first, missing values last (SQLite: NULL is smallest)", "highest first, missing values last" in t)
    check("limit stated", "Return only the first 3 rows" in t)
    check("the stored code stays exact under gamma explicit", "'POPLATEK MESICNE'" in t)
    t = N("SELECT d.A3, COUNT(*), AVG(t.amount) FROM trans AS t INNER JOIN account AS a ON t.account_id = a.account_id "
          "INNER JOIN district AS d ON a.district_id = d.district_id GROUP BY d.A3")
    check("a verified relationship from the referencing side: its parent, unmatched dropped", "Use every transaction, with its bank account (transactions without a bank account are left out)" in t)
    check("a chained relationship: the parent's parent", "with the bank account's district (transactions whose bank account has no district are left out)" in t)
    check("each relationship's exact condition in the definitions", "a transaction's bank account is the `account` record for which" in t)
    check("no record multiplied through its parent: the count is of the entity", "the number of transactions" in t)
    check("a concise average, the missing-value rule stated exactly once", "the average of transaction amount (`trans.amount`)" in t and
          t.count("ignore missing values") == 1 and "missing values ignored" not in t)
    t = N("SELECT a.account_id, COUNT(*) FROM account AS a LEFT JOIN loan AS l ON l.account_id = a.account_id GROUP BY a.account_id")
    check("from the referenced side: each of its children, one row per match, unmatched kept once",
          "paired with each of its loans, one row per bank account and loan (bank accounts without a loan are kept once, with the loan's values missing)" in t)
    check("rows multiplied: counts are of combined records, not of the entity", "the number of combined records" in t)
    t = N("SELECT d.A2, l.amount FROM loan AS l LEFT JOIN account AS a ON l.account_id = a.account_id "
          "INNER JOIN district AS d ON a.district_id = d.district_id ORDER BY d.A2 ASC LIMIT 5 OFFSET 2")
    check("a left join to the parent keeps the record, parent values missing", "with its bank account (loans without a bank account are kept, with the bank account's values missing)" in t)
    check("ascending text in character order, missing values first", "in character order, missing values first" in t)
    check("offset: skip, then take", "Skip the first 2 rows and return the next 5" in t)
    cs = Catalogue("california_schools")
    t = V(S(cs, "SELECT f.\"County Code\" FROM frpm AS f"), "natural", cat=cs)
    check("an unnamed entity keeps its table (grain with a possessive, no accepted name)", "Use the `frpm` records" in t)
    t = N("SELECT l.amount FROM loan AS l INNER JOIN account AS a ON l.amount = a.account_id")
    check("a join that is not a relationship stays the exact pairing, one row per match", "paired with every `account` record for which" in t and "one row per match" in t)
    sh = Catalogue("superhero")
    t = V(S(sh, "SELECT s.superhero_name FROM superhero AS s INNER JOIN colour AS c ON s.eye_colour_id = c.id"), "natural", cat=sh)
    check("several keys to one table: the key is named, not 'its colour'", "the colour value its eye colour id (`superhero.eye_colour_id`) refers to" in t)
    check("plural of hero", _plural("superhero") == "superheroes")
    t = V(S(cs, "SELECT s.School FROM frpm AS f INNER JOIN schools AS s ON f.CDSCode = s.CDSCode"), "natural", cat=cs)
    check("a plural base without an entity: each with its parent", "Use the `frpm` records, each with its" in t)
    check("participle nouns take the plural on the head", _plural("track sold") == "tracks sold")
    t = N("SELECT DISTINCT a.frequency FROM account AS a ORDER BY a.frequency DESC")
    check("duplicates removed, before sorting", t.index("Leave out rows") < t.index("Sort the rows"))
    t = N("SELECT COUNT(*), AVG(l.amount) FROM loan AS l WHERE l.duration >= 24")
    check("no grouping but aggregates: one row over all the entities", "Over all the loans described below, show one row" in t)
    # ---- COMPETING MEANINGS of an unmatched record: the wording must name WHICH records are dropped or kept
    t = N("SELECT t.amount FROM trans AS t INNER JOIN account AS a ON t.account_id = a.account_id")
    check("inner join: the unit dropped is named (not 'left out' alone)", "transactions without a bank account are left out" in t and "kept" not in t)
    t = N("SELECT t.amount FROM trans AS t LEFT JOIN account AS a ON t.account_id = a.account_id")
    check("left join: the unit kept is named, the missing values said", "transactions without a bank account are kept, with the bank account's values missing" in t)
    t = N("SELECT d.A3 FROM trans AS t INNER JOIN account AS a ON t.account_id = a.account_id INNER JOIN district AS d ON a.district_id = d.district_id")
    check("a chained join drops the source record whose parent has no match", "transactions whose bank account has no district are left out" in t)
    t = N("SELECT a.account_id FROM account AS a INNER JOIN loan AS l ON l.account_id = a.account_id")
    check("a multiplying join: one row per pair, the unmatched unit named", "one row per bank account and loan" in t and "bank accounts without a loan are left out" in t)
    th = Catalogue("thrombosis_prediction")
    t = V(S(th, "SELECT p.Diagnosis, e.Thrombosis FROM Examination AS e INNER JOIN Patient AS p ON e.ID = p.ID"), "natural",
          gamma={"columns": "natural", "values": "natural"}, cat=th)
    check("a column whose name another table in reach also has is qualified by its entity (whose diagnosis)",
          "patient master record's primary diagnosed disease" in t)
    # ---- AMBIGUITY, decided once (specbridge.comm.verbal.interpret): representation tolerated, unresolved meaning kept precise
    GMN = {"columns": "natural", "values": "natural"}
    from specbridge.comm.verbal.verbalize import task
    r = task(S(th, 'SELECT l.ID, l."DNA-II", l.DNA FROM Laboratory AS l'), "natural", GMN, th)
    check("two columns of one table documented identically: the handles stay, flagged UNRESOLVED",
          "`Laboratory.DNA-II`" in r["question"] and any(x["why"].startswith("UNRESOLVED") for x in r["record"]["unresolved"]))
    r = task(S(fin, "SELECT l.loan_id, l.status FROM loan AS l"), "natural", GMN, fin)
    check("a coded output with documented meanings: the record accepts code or meaning at its position",
          r["record"]["representation"] and r["record"]["representation"][0]["position"] == 2)
    check("...and the question says so once", r["question"].count("may be shown as stored or as its documented meaning") == 1)
    from specbridge.comm.verbal import interpret
    tk = {"grader": {"columns": 2, "tolerance": [None, None], "ordered": False, "limit": None}, "reference_answer": [[1, "A"], [2, "C"]],
          "tie_groups": None, "last_pool": None, "record": r["record"]}
    check("the record's grader accepts the documented meaning in place of the code", interpret.grade(tk, [(1, "contract finished, no problems"), (2, "C")])[0])
    check("...and still refuses a meaning of the agent's own", not interpret.grade(tk, [(1, "finished/paid"), (2, "C")])[0])
    from specbridge.comm.verbal.verbalize import REPORT, undefined_symbols
    q = V(S(fin, "SELECT l.loan_id, ROUND(AVG(l.amount) * 1.5, 2) FROM loan AS l GROUP BY l.loan_id"), "natural", cat=fin)
    req = {k: " | ".join(q[a:b] for a, b in v) for k, v in REPORT["spans"].items()}
    check("each formula symbol has its own component ID and span ('definition A')", any(k.startswith("definition ") for k in req))
    check("every formula symbol in the requirements is defined", undefined_symbols(req) == [])
    check("an undefined symbol is found", undefined_symbols({"output 1": "(1) round(A, 2) + B", "definition A": "A is weight"}) == ["B"])
    check("a prose letter is not a symbol ('grades K-12')", undefined_symbols({"output 1": "(1) students eligible for free meals, grades K-12"}) == [])
    check("a label '(Y/N)' is not a symbol", undefined_symbols({"output 1": "(1) Charter School (Y/N)"}) == [] and undefined_symbols({"output 1": "(1) Charter School (Y/N)"}, symbols=[]) == [])
    import math as _m
    check("the grader compares an infinite value (a division by zero) without crashing",
          R.grade({"columns": 1, "tolerance": [None], "ordered": False, "limit": None}, [(float("inf"),), (1.0,)], [(1.0,), (float("inf"),)])[0])
    check("a legend symbol without a definition is found however it is written ('A-B')", undefined_symbols({"output 1": "(1) A-B"}, symbols=["A", "B"]) == ["A", "B"])
    check("...and passes once both are defined", undefined_symbols({"output 1": "(1) A-B", "definition A": "A is x", "definition B": "B is y"}, symbols=["A", "B"]) == [])
    t = V(S(th, "SELECT e.ID FROM Laboratory AS l INNER JOIN Patient AS p ON l.ID = p.ID INNER JOIN Examination AS e ON p.ID = e.ID"), "natural", cat=th)
    check("a chained one-to-many join: one row per CARRIED record and match (lab test panel), not per the joining entity (patient)",
          "one row per lab test panel and clinical examination visit" in t and "one row per patient master record and" not in t)
    sql = "SELECT d.A3, COUNT(*) FROM trans AS t INNER JOIN account AS a ON t.account_id = a.account_id INNER JOIN district AS d ON a.district_id = d.district_id GROUP BY d.A3"
    t1 = V(S(fin, sql), "natural", gamma={"relationships": "implicit", "fate_irrelevant": [1, 2]}, cat=fin)
    check("relationships implicit: no join key in the question, entities and grouping kept",
          "is the bank account for which" not in t1 and "with its bank account" in t1 and "district" in t1 and "For each region name" in t1)
    t2 = V(S(fin, sql), "natural", gamma={"relationships": "implicit", "fate_irrelevant": []}, cat=fin)
    check("...a fate the rows do not make irrelevant is kept", "transactions without a bank account are left out" in t2 and "is the bank account for which" not in t2)
    t3 = V(S(sh, "SELECT s.superhero_name FROM superhero AS s INNER JOIN colour AS c ON s.eye_colour_id = c.id"), "natural", gamma={"relationships": "implicit", "fate_irrelevant": [1]}, cat=sh)
    check("...several keys to one table: not implicit, the key stays named", "eye colour id" in t3)
    L = _Ledger(); L.claim("records", "use")
    try: L.check(["records", "output 1"]); check("an unstated requirement is refused", False)
    except R.Unrenderable: check("an unstated requirement is refused", True)


def over_tasks(path):
    n = same = nat = refused = dropped = 0
    reasons = {}
    for line in open(path):
        t = json.loads(line); cat = Catalogue(t["database"])
        s = R.spec(lift(t["reference_sql"], cat.con), cat)
        n += 1; same += V(s, "explicit") == t["instruction"]
        try: text = V(s, "natural", cat=cat)
        except R.Unrenderable as e:
            refused += 1; reasons[str(e)[:60]] = reasons.get(str(e)[:60], 0) + 1; continue
        nat += 1
        # every filter, join condition, column, group key and sort key appears word for word, rendered in the natural
        # style's own order and with its aggregate phrase, so the letters and phrases are the natural text's own
        from specbridge.comm.verbal import verbalize as VZ
        q = s["query"]
        R._CTX.append({"level": "group" if (q["group"] or q["single_group"]) else "row", "legend": [], "keys": {}})
        R._STYLE["aggregate"] = VZ._concise_aggregate
        try:
            frags = [R.cond(j["on"]) for j in q["joins"]] + [R.value(o["expr"]) for o in q["outputs"]] + [R.value(g) for g in q["group"]]
            frags += [R.cond(q["where"])] if q["where"] is not None else []
            frags += [R.cond(q["having"])] if q["having"] is not None else []
            frags += [R.value(o["expr"]) for o in q["order"]]
        finally: R._CTX.pop(); R._STYLE.pop("aggregate", None)
        miss = [f for f in frags if f not in text]
        if miss: dropped += 1; print("    %s: not stated word for word: %s" % (t["id"], miss[0][:90]))
        claims, els = ledger(s, cat)
        if set(els) - set(claims): dropped += 1
    check("%s: V(S; explicit) is the frozen instruction (%d of %d)" % (path, same, n), same == n)
    check("%s: natural states every requirement or is refused by name (%d natural, %d refused %s)" % (path, nat, refused, reasons), nat + refused == n)
    check("%s: no requirement's phrase dropped (%d tasks with one)" % (path, dropped), dropped == 0)


def symbols():
    """The fail-closed symbol check: explicit V's inline legend defines a symbol; a symbol with no definition still fails."""
    from specbridge.comm.verbal.verbalize import undefined_symbols as U
    for req, want, name in [({"steps": "the average of A − B in the group. Here A is loser height (`m.lh`); B is winner height (`m.wh`)."}, [], "inline legend"),
                            ({"steps": "return (5) A − B. Here A is column (4) of step 3; B is column (2) of step 4. Step 4 ..."}, [], "legend of step columns"),
                            ({"output 1": "(1) A − B"}, ["A", "B"], "no definition"),
                            ({"steps": "... A ÷ C. Here A is column (2) of step 1."}, ["C"], "one of two undefined")]:
        check("undefined symbols, %s: %s" % (name, U(req)), U(req) == want)


if __name__ == "__main__":
    print("symbol definitions"); symbols()
    print("template meaning"); templates()
    for p in sys.argv[1:] or ["out/pilot100/tasks.jsonl", "out/gamma_pool/tasks.jsonl"]:
        print(p); over_tasks(p)
    print("%d failed" % len(FAILED))
