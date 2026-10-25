"""specbridge.comm.diagnose.ambiguity -- the AMBIGUITY MINER. The unit mined is an INTERPRETATION CHOICE the available communication (question,
evidence, database documentation) fails to settle. Not a question variant, not a failure pattern.

TAXONOMY (families; "other" lets it grow):
    referent                patient diagnosis vs examination diagnosis
    population_scope        all accounts vs accounts with transactions
    counting_multiplicity   distinct patients vs examination rows
    aggregation             average of school averages vs student-weighted average
    time                    age now vs age at examination
    matching_boundaries     exact name vs prefix; > vs >=
    missing_values          exclude missing rates vs retain them in ranking
    ordering_selection      one minimum vs all tied minima
    calculation             which denominator / which definition of "increase"
    representation          stored status code vs its documented label
    other

PIPELINE
  1. sites(sql, docs)         DETERMINISTIC decision sites from the gold SQL's syntax tree (sqlglot): counting units, joins,
                              aggregates, divisions, dates, comparisons, text matches, NULL-sensitive operations, ORDER BY/LIMIT,
                              coded outputs, look-alike referents.
  2. classify (a model)       for each site: explicit | recoverable | ambiguous | conflicting | unknown, with an EXACT
                              supporting phrase; it may add sites step 1 missed ("new" -- the measure of extraction coverage).
  3. alternatives (a model)   for an ambiguous/conflicting site: two readings -- the gold's and one other -- each an executable
                              SQLite program, and a clarification question. A different SQL alone is not evidence of ambiguity.
  4. execute                  both programs on the database: do they run, do their answers differ HERE.
  5. review (a separate call) do both readings fit the supplied information (ambiguity), or only one (a contradiction)?
Each record: family, site, supporting text, readings, executable variants, answer difference, clarification, confidence,
review verdict. No finite method certifies it found all ambiguity: coverage and missed cases are measured, not assumed.
"""
import re
import sqlglot
from sqlglot import exp

FAMILIES = ["referent", "population_scope", "counting_multiplicity", "aggregation", "time", "matching_boundaries",
            "missing_values", "ordering_selection", "calculation", "representation", "other"]
STATUS = ["explicit", "recoverable", "ambiguous", "conflicting", "unknown"]


def _txt(node, n=120):
    try: return node.sql(dialect="sqlite")[:n]
    except Exception: return str(node)[:n]


def sites(sql, coded_columns=(), twin_columns=()):
    """Deterministic decision sites of a SQL query: [{id, family, sql, hint}]. `coded_columns`: 'table.col' (or bare 'col')
    names whose documentation lists value codes; `twin_columns`: column names that occur in more than one table in reach."""
    try: tree = sqlglot.parse_one(sql, read="sqlite")
    except Exception: return [{"id": "s1", "family": "other", "sql": sql[:120], "hint": "the SQL does not parse; sites unknown"}]
    out = []
    add = lambda fam, node, hint: out.append({"id": "s%d" % (len(out) + 1), "family": fam, "sql": _txt(node), "hint": hint})
    joins = list(tree.find_all(exp.Join))
    for j in joins:
        add("population_scope", j, "%s join: which records are kept when a match is missing" % (j.side or j.kind or "inner").lower())
    for c in tree.find_all(exp.Count):
        add("counting_multiplicity", c, "counts %s%s" % ("DISTINCT " if c.args.get("this") and isinstance(c.args["this"], exp.Distinct) else "",
                                                       "over joined rows (a join can repeat entities)" if joins else "rows"))
    for a in tree.find_all(exp.Avg, exp.Sum):
        add("aggregation", a, "%s: over which rows / at which level" % a.key.upper())
        add("missing_values", a, "%s ignores missing values" % a.key.upper())
    for d in tree.find_all(exp.Div):
        add("calculation", d, "a ratio: numerator, denominator, integer or real division")
    for f in tree.find_all(exp.Anonymous, exp.CurrentTimestamp, exp.CurrentDate, exp.StrToTime, exp.TimeToStr):
        name = (f.name if isinstance(f, exp.Anonymous) else f.key).lower()
        if isinstance(f, exp.Anonymous) and name not in ("strftime", "date", "datetime", "julianday", "iif"): continue
        if name == "iif": add("calculation", f, "a conditional value"); continue
        add("time", f, "a date/time expression (%s): which date, which granularity, relative to when" % name)
    for c in tree.find_all(exp.GT, exp.GTE, exp.LT, exp.LTE, exp.Between):
        add("matching_boundaries", c, "a boundary (%s): strict or inclusive" % c.key)
    for c in tree.find_all(exp.EQ, exp.Like, exp.ILike, exp.In):
        lit = [x for x in c.find_all(exp.Literal) if x.is_string]
        if lit or isinstance(c, (exp.Like, exp.ILike)):
            add("matching_boundaries", c, "a text match (%s): exact, case, spelling, prefix" % c.key)
    for o in tree.find_all(exp.Order):
        add("missing_values", o, "an ordering: where rows with a missing key go")
        if tree.args.get("limit") is not None or o.parent_select and o.parent_select.args.get("limit") is not None:
            add("ordering_selection", o, "ORDER BY ... LIMIT: one row vs all tied rows")
    for col in tree.find_all(exp.Column):
        full = "%s.%s" % (col.table, col.name) if col.table else col.name
        if col.name in twin_columns: add("referent", col, "a column name that occurs in more than one table in reach")
        if (full in coded_columns or col.name in coded_columns) and col.find_ancestor(exp.Select) is tree and col.find_ancestor(exp.Where) is None \
                and any(col is e or e.find(exp.Column) is col for e in tree.expressions):
            add("representation", col, "an output column with documented value codes: code or its meaning")
    seen, uniq = set(), []
    for s in out:
        k = (s["family"], s["sql"])
        if k not in seen: seen.add(k); uniq.append(dict(s, id="s%d" % (len(uniq) + 1)))
    return uniq


def reads_table(sql):
    """An alternative reading is executable evidence only if it reads the database: 'SELECT 1' is a placeholder, not a reading."""
    try: return sqlglot.parse_one(sql, read="sqlite").find(exp.Table) is not None
    except Exception: return False


def answers_differ(a, b):
    """Do two result sets differ (as sets, BIRD's comparison)? None when either did not run."""
    if a is None or b is None: return None
    return set(map(tuple, a)) != set(map(tuple, b))
