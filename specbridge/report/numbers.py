"""NUMBER LEDGER FOR THE PAPER (2026-10-17): every number printed in paper/tex/specbridge.tex and paper/tex/supplement.tex
(body text, table cells, captions, figure descriptions) is found by code and tied to the data file it comes from.
    python -m specbridge.report.numbers check [--release]   # exit 1 on a mismatch, an unledgered number, a lost anchor or missing data
    python -m specbridge.report.numbers report [--all]      # table: line, printed, recomputed, source, status (--all: also the ok rows)

The ledger is LEDGER below: one entry per place in the tex. An entry is (file, anchor, specs): the anchor is a piece of the tex
source in which each `#` stands for one printed number, and each spec says where that number comes from. The key of a number is
file + anchor + its position in the anchor, so it stays the same when the value changes. A spec is one of
    d(name, path)    a field of out/paper/data/<name>.json ('/'-separated path)
    j(file, path)    a field of any JSON file
    x(src, fn)       a small computation over data files (src says which), e.g. a percentage
    K(reason)        a constant that has no data file (design parameter, literature value, quoted example), with the reason
    U(note)          UNSOURCED: the number was computed ad hoc and no file holds it (reported, not checked)
and may carry a comparison: eq (default: equal at the printed precision), lt / le / gt / ge (the paper states a bound).
What is NOT extracted: comments, the preamble and the bibliography, \\cite/\\ref/\\label arguments, \\texttt and \\sql text, column
specifications, display math and symbolic inline math, the algorithm, model and software versions (Haiku 4.5, GPT-6, 3.11.5),
dataset names (Spider 2.0, Formula 1), enumerators like (1), and numbers spelled as words.
--release: data files absent from the release package are reported as skipped, not as failures (the release ships only the
inputs that the figure and table rebuild reads; run `make reproduce` first so out/paper/data exists)."""
import glob, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX = {"P": "paper/tex/specbridge.tex", "S": "paper/tex/supplement.tex"}
M = ["haiku", "sonnet", "gpt-6-sol", "gpt-6-luna"]
_C = {}


class Missing(Exception):
    pass


def _path(p):
    q = os.path.join(ROOT, p)
    if not os.path.exists(q): raise Missing(p)
    return q


def jl(p):
    if p not in _C: _C[p] = json.load(open(_path(p)))
    return _C[p]


def tx(p):
    k = "text:" + p
    if k not in _C: _C[k] = open(_path(p)).read()
    return _C[k]


def P(name): return jl("out/paper/data/%s.json" % name)


def g(o, path):
    """Field at a '/'-separated path; a key that itself contains '/' (e.g. 'development/Spider') is matched greedily."""
    ks = path.split("/"); i = 0
    while i < len(ks):
        if isinstance(o, list): o = o[int(ks[i])]; i += 1; continue
        for k in range(len(ks), i, -1):
            if "/".join(ks[i:k]) in o: o = o["/".join(ks[i:k])]; i = k; break
        else: raise KeyError("/".join(ks[i:]))
    return o


def pc(k, n): return 100.0 * k / n


def rx(p, pattern, section=None, group=1):
    """A number from a generated Markdown file: the first match of pattern (in the '## section' part when given)."""
    t = tx(p)
    if section:
        i = t.index(section); e = t.find("\n## ", i + 1); t = t[i:e if e > 0 else None]
    m = re.search(pattern, t)
    if not m: raise KeyError("pattern not found in %s: %s" % (p, pattern))
    return float(m.group(group))


def rw(part, table, col):
    """out/rewrite/RESULTS.md (rewrite.report): the pooled row of the primary (table 0) or secondary (table 1) table, in the
    main part (0) or the filter-set part (1); col indexes the cells; 'x, p' cells give their p after the comma."""
    t = tx(RW); i = t.find("## Filter sets"); t = t[:i] if part == 0 else t[i:]
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in t.splitlines() if l.startswith("| pooled |")]
    c = rows[table][col]
    return float(c.split(",")[-1]) if "," in c else float(c)


def code(p, pattern, group=1):
    """A design parameter read from the source code that sets it."""
    return rx(p, pattern, group=group)


# ------------------------------------------------------------------------------------------------ specs
class Spec:
    def __init__(self, kind, src, fn=None, cmp="eq", tol=None):
        self.kind, self.src, self.fn, self.cmp, self.tol = kind, src, fn, cmp, tol

    def c(self, cmp, tol=None):
        self.cmp, self.tol = cmp, tol; return self


def d(name, path, f=None):
    return Spec("data", "out/paper/data/%s.json:%s" % (name, path), lambda: (f or (lambda v: v))(g(P(name), path)))


def j(p, path, f=None):
    return Spec("data", "%s:%s" % (p, path), lambda: (f or (lambda v: v))(g(jl(p), path)))


def x(src, fn, cmp="eq", tol=None): return Spec("data", src, fn, cmp, tol)
def K(reason): return Spec("const", reason)
def U(note): return Spec("unsourced", note)


# ------------------------------------------------------------------------------------------------ shared computations
F5 = lambda: P("fig5_tab4_disclosure")["models"]
NF = lambda: P("fig5_tab4_disclosure")["n_families"]
ACC = lambda: P("accepted")["scopes"]["accepted"]
CONV = lambda: P("conventions")
FIL = lambda: P("filter_sets")
RSC = lambda: jl("out/rescore/results.json")


def _rs_run(qid, which):
    from specbridge.report import impact as IM
    it = {i["id"]: i for i in jl("out/rewrite/bird/items.json")}[qid]; return IM.run(it["path"], it[which], limit=60)
def rs_rows(qid, which): return len(_rs_run(qid, which))
def rs_val(qid, which): return float(_rs_run(qid, which)[0][0])
LIB = lambda: {t["type"]: t for t in P("tab2_library")["types"]}
REF = lambda: P("tab2_references")["table2"]
F6 = lambda: P("fig6_inclination")["groups"]
IMP = lambda: P("fig_impact")
FIN = lambda: jl("out/ambrosia/final/final.json")
RQ = lambda: jl("out/reqmethod100/results.json")
RQMD = "out/reqmethod100/RESULTS.md"
RW = "out/rewrite/RESULTS.md"
TOPK = lambda: jl("out/transfer/all/render/disclose/topk/results.json")["models"]
FROZEN_ALL = "out/transfer/all/render/eval/frozen.json"
INV_EXT = "out/transfer/ext/cp/INVENTORY.md"

cbp = lambda m: pc(F5()[m]["covers_both_given_both_precise"]["k"], F5()[m]["covers_both_given_both_precise"]["n"])
exb = lambda m: pc(F5()[m]["covers_both_given_both_precise"]["n"], NF())
faith = lambda m: pc(F5()[m]["faithful_given_stated"]["k"], F5()[m]["faithful_given_stated"]["n"])
conv = lambda m: pc(CONV()["models"][m]["conventional"], CONV()["models"][m]["conventional"] + CONV()["models"][m]["other"])
grp = lambda m, g_, v: F5()[m]["by_group"][g_][v]
grpct = lambda m, g_, v: pc(grp(m, g_, v)["k"], grp(m, g_, v)["n"])
LIB13 = ["aggregation_level", "calculation", "comparison_quantifier", "condition_linkage", "counting_unit", "missing_values", "negated_membership_scope",
         "population_scope", "referent_column", "relationship_role", "ties_and_selection", "time_scope", "value_representation"]
SETTYPE = {"ties_and_selection": "tie"}


def accepted_cases():
    V = jl("human_supervision/verdicts.json")
    return [c for c in jl(FROZEN_ALL)["cases"] if (V.get(c["case"].split("-")[-1]) or {}).get("verdict") == "yes"]


def sets_of(t):
    """Accepted request sets of one library type (all/render frozen cases x human_supervision/verdicts.json)."""
    if t == "other": return sum(1 for c in accepted_cases() if c["type"] not in [SETTYPE.get(k, k) for k in LIB13])
    return sum(1 for c in accepted_cases() if c["type"] == SETTYPE.get(t, t))


def part_cases(i):
    return {c["case"] for c in jl(("out/transfer/eval12-v2/render", "out/transfer/ext/render")[i] + "/eval/frozen.json")["cases"]}


def rewrite_runs(m, part):
    ks = part_cases(part); fs = glob.glob(os.path.join(ROOT, "out/rewrite/runs/%s/*.json" % m))
    if not fs: raise Missing("out/rewrite/runs/%s" % m)
    return sum(1 for f in fs if json.load(open(f))["case"] in ks)


def mcnemar(b, c):
    n = b + c
    return 1.0 if not n else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def bird_clar():
    """Simulated clarification on BIRD dev (out/rewrite/bird/runs), without the 6 null_filter questions whose gold is defective
    (exclusion recorded in out/rewrite/bird/GATE.md)."""
    fs = glob.glob(os.path.join(ROOT, "out/rewrite/bird/runs/*/*.json"))
    if not fs: raise Missing("out/rewrite/bird/runs")
    from specbridge.comm.diagnose.rules import edit_ok
    ok = {}
    return [r for r in (json.load(open(f)) for f in fs) if r["rule"] != "null_filter" and ok.setdefault(r["id"], edit_ok(r))]


def bird_acc(v): R = bird_clar(); return pc(sum(r[v]["right"] for r in R), len(R))
def bird_p(v): R = bird_clar(); return mcnemar(sum(r["c"]["right"] and not r[v]["right"] for r in R), sum(r[v]["right"] and not r["c"]["right"] for r in R))


def amb_decomp():
    A = [jl("out/ambrosia/%s.json" % f)["models"] for f in ("decomposition", "decomposition_conf")]
    s = lambda m, k: sum(a[m]["shape"][k] for a in A)
    return {m: {"n": s(m, "n"), "readings": sum(len(q["readings"]) for a in A for q in a[m]["questions"]),
                "computed": pc(s(m, "missed_computed"), s(m, "missed")), "allfound": pc(s(m, "all_found_given_specific"), s(m, "every_specific_right"))} for m in A[0]}


def exchange_md():
    X = {}
    for l in tx("out/ambrosia/final/EXCHANGE.md").splitlines():
        m = re.match(r"\| (sonnet|gpt-6-sol) \| (plain|samplek|dtp|ours) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", l)
        if m: X[(m.group(1), m.group(2))] = tuple(float(v) for v in m.group(3, 4, 5))
    return X


def pool_by(source):
    rows = [r for r in jl("out/paper/data/tab1_construction.json")["pool"] if source in (None, r["source"])]
    return {k: sum(r[k] for r in rows) for k in ("requested", "delivered", "constructions", "seconds")} | {"dbs": len(rows)}


def f6_share(g_, k): v = F6()[g_]["kinds"][k]; return pc(v["k"], v["n"])


def f6_others_min(min_n=10):
    """figures_col.defaults: the five decisions other than ties and counting, smallest share read the usual way in any group (n >= 10)."""
    G = F6(); ks = [k for k in P("fig6_inclination")["figure_kinds"] if k not in ("ties_and_selection", "counting_unit")]
    return min(pc(G[g_]["kinds"][k]["k"], G[g_]["kinds"][k]["n"]) for g_ in G for k in ks if G[g_]["kinds"][k]["n"] >= min_n)


OWN = ("BIRD train", "BIRD dev", "Spider train (own)", "Spider dev")


def impact_example(q):
    for e in jl("out/impact/impact.json")["examples"]:
        if q in e["question"]: return e
    raise KeyError(q)


def lib_record(rid):
    for l in tx("library/examples.jsonl").splitlines():
        o = json.loads(l)
        if o["id"] == rid: return o
    raise KeyError(rid)


def in_text(src_file, rid):
    """The printed number must appear in the record's text (an example value quoted from a library record)."""
    return Spec("text", "%s record %s (value appears in the record)" % (src_file, rid), lambda: json.dumps(lib_record(rid)))


def methods_cells(m, arm):
    F = FIN()["solvers"][m]["arms"][arm]; R = RQ()[m]["arms"][arm]; X = exchange_md()[(m, arm)]
    return [100 * F["precision"], F["allfound"], X[1], X[2], X[0], F["calls"], R["both"], R["names"], R["recovered"], R["right"]]




def E(f, anchor, *specs, occ=None):
    return {"file": f, "anchor": anchor, "specs": list(specs), "occ": occ}


# ------------------------------------------------------------------------------------------------ generated tables
def main_table():
    """Table tab:main (tables_tex.main_results), one entry per row."""
    f2 = lambda: P("fig2_explicit_vs_precise"); C = lambda: P("fig3_real_benchmarks")["confirmation"]
    out = [E("P", r"\textit{Generated tasks (# DBs)}", x("tab1_construction.json:pool (databases)", lambda: pool_by(None)["dbs"])),
           E("P", r"\textit{Request sets (#), scored by execution}", d("fig5_tab4_disclosure", "n_families"))]
    def row(label, nspec, val, src, low=False):
        specs = (nspec if isinstance(nspec, list) else [nspec]) + [x(src % m, (lambda m=m: val(m))) for m in M]
        out.append(E("P", "& %s & %s & # & # & # & #\\\\" % (label, "#--#" if isinstance(nspec, list) and len(nspec) == 2 else "#"), *specs))
    row("exact description", d("fig2_explicit_vs_precise", "n_tasks"), lambda m: pc(*f2()["overall"][m]["explicit"]), "fig2_explicit_vs_precise.json:overall/%s/explicit k/n")
    row("natural request", d("fig2_explicit_vs_precise", "n_tasks"), lambda m: pc(*f2()["overall"][m]["precise_v2"]), "fig2_explicit_vs_precise.json:overall/%s/precise_v2 k/n")
    for split, occ in (("bird_heldout100", 0), ("spider_confirm50", 1)):
        for lab, key in (("original question", "original_strict"), ("\\quad extra columns allowed", "original_shape"), ("exact description of reference", "explicit_strict")):
            out.append(E("P", "& %s & # & # & # & # & #\\\\" % lab, d("fig3_real_benchmarks", "confirmation/%s/n" % split),
                         *[x("fig3_real_benchmarks.json:confirmation/%s/%s/%s k/n" % (split, m, key), (lambda m=m, key=key, split=split: pc(*C()[split][m][key]))) for m in M], occ=occ))
    for lab, key in (("specific request right", "precise_correct"), ("open request: A or B", "open_admissible"), ("names the open choice", "recognises"),
                     ("returns both A and B", "covers_both"), ("settled request called open", "false_open")):
        row(lab, d("fig5_tab4_disclosure", "n_families"), (lambda m, key=key: pc(F5()[m][key]["k"], F5()[m][key]["n"])), "fig5_tab4_disclosure.json:models/%s/" + key + " k/n")
    row("\\quad if both specific right", [x("fig5:models/*/covers_both_given_both_precise/n (min)", lambda: min(F5()[m]["covers_both_given_both_precise"]["n"] for m in M)),
                                          x("fig5:models/*/covers_both_given_both_precise/n (max)", lambda: max(F5()[m]["covers_both_given_both_precise"]["n"] for m in M))],
        cbp, "fig5_tab4_disclosure.json:models/%s/covers_both_given_both_precise k/n")
    row("stated reading matches SQL", [x("fig5:models/*/faithful_given_stated/n (min)", lambda: min(F5()[m]["faithful_given_stated"]["n"] for m in M)),
                                                  x("fig5:models/*/faithful_given_stated/n (max)", lambda: max(F5()[m]["faithful_given_stated"]["n"] for m in M))],
        faith, "fig5_tab4_disclosure.json:models/%s/faithful_given_stated k/n")
    row("SQL only", d("fig5_tab4_disclosure", "n_families"), lambda m: F5()[m]["overhead"]["median_seconds_plain"], "fig5_tab4_disclosure.json:models/%s/overhead/median_seconds_plain")
    row("SQL and explanation", d("fig5_tab4_disclosure", "n_families"), lambda m: F5()[m]["overhead"]["median_seconds_disclosure"], "fig5_tab4_disclosure.json:models/%s/overhead/median_seconds_disclosure")
    return out


def methods_table():
    """Table tab:methods (tables_tex.methods, compact): AMBROSIA final.json, request sets out/reqmethod100/results.json."""
    F = lambda: FIN()["solvers"]; R = lambda: jl("out/reqmethod100/results.json")
    out = [E("P", r"on the AMBROSIA final test and on # request sets. Bold", j("out/reqmethod100/results.json", "sonnet/sets")),
           E("P", r"Model & Method & (\%) & (of #) & per q. & (of #) & right", j("out/ambrosia/final/final.json", "solvers/sonnet/n_ambiguous"), j("out/reqmethod100/results.json", "sonnet/sets"))]
    lab = {"plain": "Plain", "samplek": "Three samples", "dtp": "DtP", "ours": "Ours"}
    get = {0: lambda m, a: 100 * F()[m]["arms"][a]["precision"], 1: lambda m, a: F()[m]["arms"][a]["allfound"], 2: lambda m, a: F()[m]["arms"][a]["calls"],
           3: lambda m, a: R()[m]["arms"][a]["both"], 4: lambda m, a: R()[m]["arms"][a]["right"]}
    names = ["precision %", "allfound", "calls", "both", "specific right"]
    for oi, (m, ml) in enumerate((("sonnet", "Sonnet"), ("gpt-6-sol", "GPT-Sol"))):
        for a in ("plain", "samplek", "dtp", "ours"):
            first = a == "plain"
            anc = ("%s & %s & " % (ml, lab[a]) if first else "& %s & " % lab[a]) + " & ".join(["#"] * 5) + " \\\\"
            out.append(E("P", anc, *[x("final.json/reqmethod100: %s %s %s" % (m, a, names[i]), (lambda m=m, a=a, i=i: get[i](m, a))) for i in range(5)],
                         occ=None if first else oi))
    return out


def comparison_table():
    """Table tab:comparison (tables_tex.comparison): check marks only, no numbers."""
    return []


def library_table():
    """Table tab:librarycounts: Library (tab2_library.json types: raise / settled_from_failures), References (tab2_references.json
    table2 {type: [usual, other]}), Sets (accepted request sets by type: all/render frozen.json x verdicts.json)."""
    rows = [("Aggregation level", "aggregation_level"), ("Calculation", "calculation"), ("Quantifier", "comparison_quantifier"),
            ("Condition linkage", "condition_linkage"), ("Counting unit", "counting_unit"), ("Missing values", "missing_values"),
            ("Negation", "negated_membership_scope"), ("Population scope", "population_scope"), ("Referent column", "referent_column"),
            ("Relationship role", "relationship_role"), ("Ties and selection", "ties_and_selection"), ("Time scope", "time_scope"),
            ("Value matching", "value_representation")]
    out = []
    for lab, t in rows:
        lib = [x("tab2_library.json:types[%s]/raise" % t, (lambda t=t: LIB()[t]["raise"])), x("tab2_library.json:types[%s]/settled_from_failures" % t, (lambda t=t: LIB()[t]["settled_from_failures"]))] \
            if t != "value_representation" else [d("tab2_library", "value_split/value_matching/raise"), d("tab2_library", "value_split/value_matching/settled")]
        st = x("accepted sets of type %s (%s x verdicts.json)" % (t, FROZEN_ALL), (lambda t=t: sets_of(t))) if t != "value_representation" else \
            K("value-representation sets all test strict cutoffs; they are counted on the strict-cutoff row")
        if t == "referent_column":
            out.append(E("S", r"%s & Which column is meant? & # & # & -- & -- & #\\" % lab, *lib, st)); continue
        ref = [x("tab2_references.json:table2/%s[0]" % t, (lambda t=t: REF()[t][0])), x("tab2_references.json:table2/%s[1]" % t, (lambda t=t: REF()[t][1])),
               x("tab2_references.json:table2/%s other/(usual+other) %%" % t, (lambda t=t: pc(REF()[t][1], sum(REF()[t]))))]
        out.append(E("S", r"%s & # & # & # & # (#) & #\\" % (lab + " & " + {"aggregation_level": "Rows or group averages?", "calculation": "Which formula is meant?",
                     "comparison_quantifier": "``Than any'': one or all?", "condition_linkage": "Conditions on one row?", "counting_unit": "Count rows or entities?",
                     "missing_values": "Keep or skip missing?", "negated_membership_scope": "Some non-match, or none?", "population_scope": "Keep unmatched rows?",
                     "relationship_role": "Which link to follow?", "ties_and_selection": "One tied row, or all?", "time_scope": "Period? Ends included?",
                     "value_representation": "Exact or loose match?"}[t]), *lib, *ref, st))
    cut = [x("tab2_references.json:table2/strict_cutoff[0]", lambda: REF()["strict_cutoff"][0]), x("tab2_references.json:table2/strict_cutoff[1]", lambda: REF()["strict_cutoff"][1]),
           x("tab2_references.json:table2/strict_cutoff share", lambda: pc(REF()["strict_cutoff"][1], sum(REF()["strict_cutoff"])))]
    out.append(E("S", r"Strict cutoff & Strict or inclusive? & # & # & # & # (#) & #\\", d("tab2_library", "value_split/strict_cutoff/raise"), d("tab2_library", "value_split/strict_cutoff/settled"),
                 *cut, x("accepted sets of type value_representation (cutoffs)", lambda: sets_of("value_representation"))))
    out.append(E("S", r"\multicolumn{2}{@{}l}{Total} & # & # & & & #\\", d("tab2_library", "table1_meaning_from_failures/open"),
                 d("tab2_library", "table1_meaning_from_failures/settled"), d("fig5_tab4_disclosure", "n_families")))
    out.append(E("S", r"Sets: the # accepted request sets, of the types whose other reading at least #\% of silent references take", d("fig5_tab4_disclosure", "n_families"),
                 K("design rule: the 1% type threshold")))
    return out



def compact_table():
    """Table tab:librarycounts (paper): the major types; the full table is supplement tab:librarydetail (library_table)."""
    sil = lambda t: sum(REF()[t]); sh = lambda t: pc(REF()[t][1], sum(REF()[t]))
    lib = lambda t: [x("tab2_library.json:types[%s]/raise" % t, (lambda: LIB()[t]["raise"])), x("tab2_library.json:types[%s]/settled_from_failures" % t, (lambda: LIB()[t]["settled_from_failures"]))]
    out = []
    for lab, t, st in (("Aggregation level & Rows or group averages?", "aggregation_level", "aggregation_level"), ("Ties & One tied row, or all?", "ties_and_selection", "ties_and_selection"),
                       ("Counting unit & Rows or entities?", "counting_unit", "counting_unit"), ("Missing values & Keep or skip missing?", "missing_values", "missing_values")):
        out.append(E("P", lab + r" & # & # & # & #\% & #\\", *lib(t), x("tab2_references.json:table2/%s usual+other" % t, (lambda t=t: sil(t))),
                     x("tab2_references.json:table2/%s other share" % t, (lambda t=t: sh(t))), x("accepted sets of type %s" % st, (lambda st=st: sets_of(st)))))
    out.append(E("P", r"Strict cutoff & Strict or inclusive? & # & # & # & #\% & #\\", d("tab2_library", "value_split/strict_cutoff/raise"), d("tab2_library", "value_split/strict_cutoff/settled"),
                 x("tab2_references.json:table2/strict_cutoff usual+other", lambda: sil("strict_cutoff")), x("tab2_references.json:table2/strict_cutoff other share", lambda: sh("strict_cutoff")),
                 x("accepted sets of type value_representation (cutoffs)", lambda: sets_of("value_representation"))))
    out.append(E("P", r"Referent column & Which column is meant? & # & # & -- & -- & #\\", *lib("referent_column"), x("accepted sets of type referent_column", lambda: sets_of("referent_column"))))
    MAJ = ("aggregation_level", "ties_and_selection", "counting_unit", "missing_values", "referent_column")
    rest = lambda k: sum(v[k] for t, v in LIB().items() if t in LIB13 and t not in MAJ and t != "value_representation") + P("tab2_library")["value_split"]["value_matching"]["raise" if k == "raise" else "settled"]
    out.append(E("P", r"Other types (seven) & & # & # & & & #\\", x("tab2_library.json: raise of the seven minor types (value matching part of value_representation)", lambda: rest("raise")),
                 x("tab2_library.json: settled of the seven minor types", lambda: rest("settled_from_failures")),
                 x("accepted sets of the other types", lambda: P("fig5_tab4_disclosure")["n_families"] - sum(sets_of(t) for t in ("aggregation_level", "ties_and_selection", "counting_unit", "missing_values", "value_representation")))))
    out.append(E("P", r"\multicolumn{2}{@{}l}{Total} & # & # & & & #\\", d("tab2_library", "table1_meaning_from_failures/open"),
                 d("tab2_library", "table1_meaning_from_failures/settled"), d("fig5_tab4_disclosure", "n_families")))
    return out

def funnel_table():
    inv = lambda i: int(P("tab3_generation")["funnel"]["inventory"].split("|")[i + 2].strip())
    I = lambda i, what: x("tab3_generation.json:funnel/inventory column %d (%s)" % (i, what), (lambda i=i: inv(i)))
    return [E("S", r"Tasks with natural requests & #\\", d("tab3_generation", "funnel/tasks")),
            E("S", r"Proposed decisions & #\\", I(1, "proposed")),
            E("S", r"Alternative executes and changes the answer & #\\", I(2, "load-bearing")),
            E("S", r"Alternative also has an exact description & #\\", I(3, "renders")),
            E("S", r"Supported by at least one model reviewer & #\\", x("tab3_generation.json:funnel/inventory mutual + disputed", lambda: inv(4) + inv(5))),
            E("S", r"\quad Supported by both / one & # / #\\", I(4, "mutually recognized"), I(5, "disputed")),
            E("S", r"Selected, at most one per task & #\\", d("tab3_generation", "funnel/selected")),
            E("S", r"Retained after wording checks & #\\", d("tab3_generation", "funnel/frozen")),
            E("S", r"Choices in a filter, from the same tasks & #\\", x("filter_sets.json:verdicts (yes + no)", lambda: sum(FIL()["verdicts"].values()))),
            E("S", r"Request sets: all / accepted by an author & # / #\\", d("fig5_tab4_disclosure", "n_constructed"), d("fig5_tab4_disclosure", "n_families"))]


def construction_table():
    out = []
    for lab, s in (("Spider", "Spider"), ("BIRD", "BIRD"), ("LiveSQLBench", "LiveSQLBench"), ("Total", None)):
        src = "tab1_construction.json:pool (source %s) " % (s or "all")
        sec = x(src + "seconds (summed, then rounded)", (lambda s=s: pool_by(s)["seconds"]))
        out.append(E("S", "%s & # & #/# & # & #\\\\" % lab, x(src + "databases", (lambda s=s: pool_by(s)["dbs"])), x(src + "delivered", (lambda s=s: pool_by(s)["delivered"])),
                     x(src + "requested", (lambda s=s: pool_by(s)["requested"])), x(src + "constructions", (lambda s=s: pool_by(s)["constructions"])), sec))
    rb = lambda k: g(P("tab1_construction"), "reviewed_build/" + k)
    out.append(E("S", r"Separate task review delivers #/# tasks, and language generation supplies #/# requests",
                 d("tab1_construction", "reviewed_build/delivered"), x("tab1_construction.json:reviewed_build/requested_cells (sum)", lambda: sum(rb("requested_cells").values())),
                 d("fig2_explicit_vs_precise", "n_tasks"), d("tab1_construction", "reviewed_build/delivered")))
    out.append(E("S", r"Program construction on # databases", x("tab1_construction.json:pool (databases)", lambda: pool_by(None)["dbs"])))
    return out


def filter_table():
    out = [E("S", r"Filter request sets (# accepted)", d("filter_sets", "accepted"))]
    for m, lab in zip(M, ("Haiku", "Sonnet", "GPT-Sol", "GPT-Luna")):
        out.append(E("S", "%s & # & # & # & # & # / #\\\\" % lab, *[d("filter_sets", "models/%s/%s" % (m, k)) for k in
                     ("both_specific", "covers_if_both", "names", "specific_right", "misses_computable", "misses")]))
    return out


# ------------------------------------------------------------------------------------------------ the ledger
LIT = "literature value from the cited source (Table S-cases)"
EX = "quoted example value"


def ledger():
    L = []
    rng = lambda fn, src: [x(src + " (min)", lambda: min(fn(m) for m in M)), x(src + " (max)", lambda: max(fn(m) for m in M))]
    L += [
        # ---------------- abstract
        E("P", r"On # hand-validated request sets", d("fig5_tab4_disclosure", "n_families")),
        E("P", r"they return both readings in only #--#\% of those sets, and they seldom", *rng(cbp, "fig5:models/*/covers_both_given_both_precise k/n")),
        E("P", r"which is # points more precise than rewriting the request", x("out/ambrosia/final/final.json:pooled/vs_dtp/precision[0] x100", lambda: 100 * FIN()["pooled"]["vs_dtp"]["precision"][0])),
        # ---------------- introduction
        E("P", r"For two films priced at \$# for two days and \$# for six days, the first reading gives \$# per day and the second \$#.",
          K("illustrative input of the worked arithmetic"), K("illustrative input of the worked arithmetic"),
          x("arithmetic of the example: mean(6/2, 6/6)", lambda: (6 / 2 + 6 / 6) / 2), x("arithmetic of the example: mean(6,6)/mean(2,6)", lambda: 6 / ((2 + 6) / 2))),
        E("P", r"On # accepted request sets, the models answer", d("fig5_tab4_disclosure", "n_families")),
        E("P", r"on the open request they return both readings in only #--#\% of those sets. Most", *rng(cbp, "fig5:models/*/covers_both_given_both_precise k/n")),
        E("P", r"is # points more precise on AMBROSIA than", x("final.json:pooled/vs_dtp/precision[0] x100", lambda: 100 * FIN()["pooled"]["vs_dtp"]["precision"][0])),
        E("P", r"We release the generator, the # request sets", d("fig5_tab4_disclosure", "n_constructed")),
        # ---------------- worked example
        # ---------------- library
        E("P", r"\textbf{Finding #: Models make choices", K("label")), E("P", r"\textbf{Finding #: Benchmarks cannot", K("label")), E("P", r"\textbf{Finding #: Two design rules", K("label")),
        E("P", r"For # of the # choice types, code reads", x("tab2_references.json:table2 library types (strict_cutoff is a part of value_representation)", lambda: len([t for t in REF() if t != "strict_cutoff"])), d("tab2_library", "table1_meaning_from_failures/types")),
        E("P", r"The split is real: #\% of silent tie questions return every tied row, and #\% of silent counts over a join count",
          x("ties other share", lambda: pc(REF()["ties_and_selection"][1], sum(REF()["ties_and_selection"]))),
          x("counting other share", lambda: pc(REF()["counting_unit"][1], sum(REF()["counting_unit"])))),
        # ---------------- applying a choice / filters
        E("P", r"which keeps #--#\% of the rows", x("specbridge/pd/structures/compose.py: _predicates lo x100", lambda: 100 * code("specbridge/pd/structures/compose.py", r"_predicates\(self, t, lo=([\d.]+)")),
          x("specbridge/pd/structures/compose.py: _predicates hi x100", lambda: 100 * code("specbridge/pd/structures/compose.py", r"_predicates\(self, t, lo=[\d.]+, hi=([\d.]+)"))),
        E("P", r"; every result below uses these #.", d("fig5_tab4_disclosure", "n_families")),
        # ---------------- setup
        E("P", r"Request sets use # databases", x("accepted.json:per_database (count)", lambda: len(ACC()["per_database"]))),
        E("P", r"request arithmetic depth #--# and step depth #--#, and each database contributes # to # accepted request sets.",
          x("tab1_construction.json:reviewed_build/requested_cells keys, min A", lambda: min(int(k.split(",")[0]) for k in P("tab1_construction")["reviewed_build"]["requested_cells"])),
          x("max A", lambda: max(int(k.split(",")[0]) for k in P("tab1_construction")["reviewed_build"]["requested_cells"])),
          x("min S", lambda: min(int(k.split(",")[1]) for k in P("tab1_construction")["reviewed_build"]["requested_cells"])),
          x("max S", lambda: max(int(k.split(",")[1]) for k in P("tab1_construction")["reviewed_build"]["requested_cells"])),
          x("accepted.json:scopes/accepted/per_database (min)", lambda: min(ACC()["per_database"].values())),
          x("accepted.json:scopes/accepted/per_database (max)", lambda: max(ACC()["per_database"].values()))),
        E("P", r"uses # development questions on five databases and holds out # before the final evaluation",
          x("out/diagnose_coverage/COVERAGE.md: BIRD total unique questions attempted", lambda: rx("out/diagnose_coverage/COVERAGE.md", r"\*\*total\*\*[^|]*\| \*\*(\d+)\*\*")),
          x("out/comm_library/heldout_eval.json:question_ids (count)", lambda: len(jl("out/comm_library/heldout_eval.json")["question_ids"]))),
        E("P", r"the Spider analysis uses # development questions and holds out #.", x("out/comm_library/spider_split.json:development (count)", lambda: len(jl("out/comm_library/spider_split.json")["development"])),
          x("out/comm_library/spider_split.json:confirmation (count)", lambda: len(jl("out/comm_library/spider_split.json")["confirmation"]))),
        E("P", r"Intervals resample tasks # times", K("design parameter: bootstrap resamples (B = 2000 in the report modules)")),
        # ---------------- checks on the tests
        E("P", r"The pipeline keeps # request sets", d("fig5_tab4_disclosure", "n_constructed")),
        E("P", r"This leaves # of the # sets; they test", d("fig5_tab4_disclosure", "n_families"), d("fig5_tab4_disclosure", "n_constructed")),
        E("P", r"fewer than #\% of silent references read the other way", K("design rule: a type is kept when at least 1% of silent references take its other reading")),
        E("P", r"request sets on # databases, and an author accepts # of them by hand", x("accepted.json:per_database (count)", lambda: len(ACC()["per_database"])), d("fig5_tab4_disclosure", "n_families")),
        E("P", r"and # of the # BIRD and Spider references whose question says", x("fig6_inclination.json: boundary_between k summed over groups", lambda: sum(v["kinds"]["boundary_between"]["k"] for v in F6().values())),
          x("fig6_inclination.json: boundary_between n summed over groups", lambda: sum(v["kinds"]["boundary_between"]["n"] for v in F6().values()))),
        E("P", r"so the author rejects all # date-range sets", x(FROZEN_ALL + " x verdicts: filter-run time_scope sets rejected", lambda: sum(1 for c in jl(FROZEN_ALL)["cases"] if c["case"] in part_cases(1) and c["type"] == "time_scope" and c not in accepted_cases()))),
        E("P", r"on # fixed tasks, it keeps the shared requirements in # drafts, against # for direct generation ($p=#$), and passes all checks in # against #.",
          x("tab3_generation.json:pairs (count)", lambda: len(P("tab3_generation")["pairs"])), d("tab3_generation", "ablation_60_pairs/fidelity/final/full"),
          d("tab3_generation", "ablation_60_pairs/fidelity/final/direct"), d("tab3_generation", "ablation_60_pairs/fidelity/final/full_vs_direct/mcnemar_exact_p"),
          d("tab3_generation", "ablation_60_pairs/pass/final/full"), d("tab3_generation", "ablation_60_pairs/pass/final/direct")),
        E("P", r"Its rules find usable queries on # of # databases", d("fig1_coverage", "n_buildable"), d("fig1_coverage", "n_tried")),
        E("P", r"On the # evaluation databases it delivers # of # requested queries", x("tab1_construction.json:pool (databases)", lambda: pool_by(None)["dbs"]),
          d("fig1_coverage", "n_pool"), x("tab1_construction.json:pool requested (sum)", lambda: pool_by(None)["requested"])),
        E("P", r"(# attempts). Labels:", d("fig1_coverage", "ablation/full/attempts")),
        E("P", r"GPT-Sol wrote a second version of # random tasks", j("out/writer_swap/calib200/results.json", "n_calibration")),
        E("P", r"Exact description versus natural request on # generated tasks", d("fig2_explicit_vs_precise", "n_tasks")),
        # ---------------- finding 1
        E("P", r"change by at most three of # per model", d("fig5_tab4_disclosure", "n_families")),   # three = max |precise_plain_single - precise_disclosure| over models (fig5 overhead)
        E("P", r"at most two of # responses to specific requests", d("fig5_tab4_disclosure", "n_families")),
        E("P", r"Answering and communicating on # request sets (#\% intervals)", d("fig5_tab4_disclosure", "n_families"), K("confidence level")),
        E("P", r"in only #\% for Sonnet, #\% for GPT-Sol, #\% for Haiku and #\% for GPT-Luna.",
          *[x("fig5:models/%s/covers_both_given_both_precise k/n" % m, (lambda m=m: cbp(m))) for m in ("sonnet", "gpt-6-sol", "haiku", "gpt-6-luna")]),
        E("P", r"On the # sets built without a filter the range is #--#\%, and on all # sets before the #\% rule on choice types #--#\%.",
          d("accepted", "scopes/accepted_no_filter/n"),
          *rng(lambda m: pc(*P("accepted")["scopes"]["accepted_no_filter"]["models"][m]["covers_given_explore_both"]), "accepted.json:scopes/accepted_no_filter/models/*/covers_given_explore_both"),
          d("accepted", "scopes/accepted_all_types/n"), K("design rule: a type is kept when at least 1% of silent references take its other reading"),
          *rng(lambda m: pc(*P("accepted")["scopes"]["accepted_all_types"]["models"][m]["covers_given_explore_both"]), "accepted.json:scopes/accepted_all_types/models/*/covers_given_explore_both")),
        E("P", r"a stated reading matches the model's SQL in #--#\% of responses. The models describe", *rng(faith, "fig5:models/*/faithful_given_stated k/n")),
        E("P", r"in # of the # sets, the two readings return different rows, and in the other # the same rows",
          d("accepted", "scopes/accepted/readings_differ/row_keys_differ"), d("accepted", "scopes/accepted/readings_differ/sets"),
          x("accepted.json readings_differ sets - row_keys_differ", lambda: ACC()["readings_differ"]["sets"] - ACC()["readings_differ"]["row_keys_differ"])),
        E("P", r"and on AMBROSIA (Wilson #\% intervals)", K("confidence level")),
        E("P", r"in #--#\% of the missed sets (Figure",
          *rng(lambda m: pc(ACC()["models"][m]["misses_computable_single"], ACC()["models"][m]["misses"]), "accepted.json:models/* misses_computable_single/misses")),
        E("P", r"for four models with # percent intervals", K("confidence level")),
        E("P", r"most markers lie between # and # percent", *[x("figures_col.decomposition points: fig5 decomposition matched/exploration + AMBROSIA shares (%s)" % w,
          (lambda f=f: f([pc(F5()[m]["decomposition"][s_]["all"]["both_specific_right"], F5()[m]["decomposition"][s_]["all"]["not_covered"]) for m in M for s_ in ("matched", "exploration")]
                         + [amb_decomp()[m]["computed"] for m in M])), "ge" if w == "min" else "le", 5) for w, f in (("min", min), ("max", max))]),
        E("P", r"in parentheses; Wilson #\% intervals)", K("confidence level")),
        E("P", r"On the # vagueness questions per model, which ask which column or value a phrase means, models compute #--#\% of the readings they miss",
          d("ambrosia_types", "vague/haiku/questions"), *rng(lambda m: P("ambrosia_types")["vague"][m]["computed_pct"], "ambrosia_types.json:vague/*/computed_pct")),
        E("P", r"no model returns both readings for more than #\% of the sets from any source", x("fig5: max over models and sources of by_group/source k/n", lambda: max(grpct(m, "source", v) for m in M for v in ("Spider", "BIRD", "LiveSQLBench")), "le")),
        E("P", r"over our method per # questions", K("definition: rates are per 100 questions")),
        E("P", r"the median request takes #--# seconds per model with it, against #--# seconds for SQL alone",
          *rng(lambda m: F5()[m]["overhead"]["median_seconds_disclosure"], "fig5:models/*/overhead/median_seconds_disclosure"),
          *rng(lambda m: F5()[m]["overhead"]["median_seconds_plain"], "fig5:models/*/overhead/median_seconds_plain")),
        E("P", r"What each model does with the # open requests", d("accepted", "scopes/accepted/n")),
        E("P", r"returns both readings for #\% of aggregation-level sets", x("fig5:models/sonnet/by_group/type/aggregation_level k/n", lambda: grpct("sonnet", "type", "aggregation_level"))),
        E("P", r"Main answer to the open request on # tie and counting sets", d("conventions", "sets")),
        E("P", r"In # tie and counting sets, one reading", d("conventions", "sets")),
        E("P", r"The conventional reading is the intended one in # of these sets", d("conventions", "intended_conventional")),
        E("P", r"it is the conventional one in #--#\% of cases for every model", *rng(conv, "conventions.json:models/* conventional/(conventional+other)")),
        E("P", r"five SQL-only samples contain both readings in at most # of # sets for any model, while one explained response from Sonnet does so in #:",
          x("topk/results.json:models/*/topk (max)", lambda: max(TOPK()[m]["topk"] for m in M)),
          x("topk/results.json:n_sets", lambda: jl("out/transfer/all/render/disclose/topk/results.json")["n_sets"]),
          x("topk/results.json:models/sonnet/explain_cover", lambda: TOPK()["sonnet"]["explain_cover"])),
        E("P", r"it still returns only one reading in #--#\% of them",
          *rng(lambda m: pc(*ACC()["models"][m]["named_and_computable"]), "accepted.json:scopes/accepted/models/*/named_and_computable")),
        E("P", r"On # ambiguous test questions per model, the model computes #--#\% of the readings it misses",
          x("out/ambrosia/decomposition{,_conf}.json:models/haiku/shape/n (sum)", lambda: amb_decomp()["haiku"]["n"]),
          *rng(lambda m: amb_decomp()[m]["computed"], "out/ambrosia/decomposition{,_conf}.json shape missed_computed/missed")),
        E("P", r"in only #--#\% of questions.", *rng(lambda m: amb_decomp()[m]["allfound"], "out/ambrosia/decomposition{,_conf}.json shape all_found_given_specific/every_specific_right")),
        # ---------------- finding 2
        E("P", r"the four models answer #--#\% of BIRD questions correctly as worded but #--#\% from the exact description",
          
          *rng(lambda m: pc(*P("fig3_real_benchmarks")["confirmation"]["bird_heldout100"][m]["original_strict"]), "fig3:confirmation/bird_heldout100/*/original_strict"),
          *rng(lambda m: pc(*P("fig3_real_benchmarks")["confirmation"]["bird_heldout100"][m]["explicit_strict"]), "fig3:confirmation/bird_heldout100/*/explicit_strict")),
        E("P", r"GPT-Sol answers # of # original BIRD questions correctly without it and # with it",
          *[x("out/confirmation/bird_heldout100/noexplore_report.txt: original question row (%s)" % w, (lambda i=i: rx("out/confirmation/bird_heldout100/noexplore_report.txt",
            r"\| original question \| (\d+) \| (\d+) \| (\d+) \|", group=i))) for w, i in (("without", 3), ("n", 1), ("with", 2))]),
        E("P", r"original question versus the exact description of the reference SQL (#\% intervals)", K("confidence level")),
        E("P", r"Open choices cause #\% of BIRD and #\% of Spider failures", *[x("fig3:causes/development/%s reading choice / total" % k, (lambda k=k: pc(P("fig3_real_benchmarks")["causes"]["development/" + k]["reading choice"],
          sum(P("fig3_real_benchmarks")["causes"]["development/" + k].values())))) for k in ("BIRD batches 3-8", "Spider")]),
        E("P", r"in at least #\% of silent questions", x("fig6_inclination.json:groups/*/kinds (five other decisions, n >= 10): min share usual", f6_others_min, "ge")),
        E("P", r"return one row in over #\% of silent questions", x("fig6_inclination.json:groups BIRD/Spider own, ties_and_selection k/n (min)", lambda: min(f6_share(g_, "ties_and_selection") for g_ in OWN), "gt")),
        E("P", r"return one row in # of #.", d("fig6_inclination", "groups/imported: geo, restaurants/kinds/ties_and_selection/k"), d("fig6_inclination", "groups/imported: geo, restaurants/kinds/ties_and_selection/n")),
        E("P", r"in none of #. Each group", d("fig6_inclination", "groups/imported: academic, imdb, yelp/kinds/counting_unit/n")),
        E("P", r"BIRD and Spider bars are at # to # percent; the imported Spider groups are at # percent (ties) and # percent (counting).",
          x("fig6: BIRD/Spider own, ties and counting shares (min, rounded)", lambda: min(f6_share(g_, k) for g_ in OWN for k in ("ties_and_selection", "counting_unit"))),
          x("fig6: BIRD/Spider own, ties and counting shares (max)", lambda: max(f6_share(g_, k) for g_ in OWN for k in ("ties_and_selection", "counting_unit"))),
          x("fig6: imported geo, restaurants ties share", lambda: f6_share("imported: geo, restaurants", "ties_and_selection")),
          x("fig6: imported academic, imdb, yelp counting share", lambda: f6_share("imported: academic, imdb, yelp", "counting_unit"))),
        E("P", r"Of # such questions, # (#\%) change their answer", d("fig_impact", "BIRD dev/questions/questions"), d("fig_impact", "BIRD dev/questions/any_change"),
          x("fig_impact.json:BIRD dev any_change/questions", lambda: pc(IMP()["BIRD dev"]["questions"]["any_change"], IMP()["BIRD dev"]["questions"]["questions"]))),
        E("P", r"the reference counts joined rows and returns #, while counting each account once returns #.",
          x("out/impact/impact.json:examples[North Bohemia]/ref_head", lambda: float(re.findall(r"\d+", impact_example("North Bohemia")["ref_head"])[0])),
          x("out/impact/impact.json:examples[North Bohemia]/alt_head", lambda: float(re.findall(r"\d+", impact_example("North Bohemia")["alt_head"])[0]))),
        E("P", r"inclusive bounds change # percent of answers and counting rows versus entities # percent",
          x("fig_impact.json:BIRD dev/kinds/boundary changed/edits", lambda: pc(IMP()["BIRD dev"]["kinds"]["boundary"]["changed"], IMP()["BIRD dev"]["kinds"]["boundary"]["edits"])),
          x("fig_impact.json:BIRD dev/kinds/count_unit changed/edits", lambda: pc(IMP()["BIRD dev"]["kinds"]["count_unit"]["changed"], IMP()["BIRD dev"]["kinds"]["count_unit"]["edits"]))),
        E("P", r"every one of the # evaluation databases", x("accepted.json:per_database (count)", lambda: len(ACC()["per_database"]))),
        # ---------------- BIRD scored with both readings (specbridge.comm.transfer.rescore)
        E("P", r"We ask the four models # BIRD development questions", x("out/rescore/runs/haiku (count)", lambda: len(glob.glob("out/rescore/runs/haiku/*.json")))),
        E("P", r"reproduces all # verdicts", x("out/rescore/results.json:rule_vs_author agree (= verdicts)", lambda: RSC()["rule_vs_author"]["agree"] if RSC()["rule_vs_author"]["agree"] == RSC()["rule_vs_author"]["verdicts"] else -1)),
        E("P", r"Of the # answers BIRD marks wrong on the # questions the rule keeps, # return the other reading", j("out/rescore/results.json", "pooled/wrong_by_bird"), j("out/rescore/results.json", "questions"), j("out/rescore/results.json", "pooled/B_only")),
        E("P", r"match the edited reference (#) than the reference itself (#)", x("out/rescore/results.json:by_type_pooled ties+count_unit B_only", lambda: sum(RSC()["by_type_pooled"][t]["B_only"] for t in ("ties", "count_unit"))),
          x("out/rescore/results.json:by_type_pooled ties+count_unit A", lambda: sum(RSC()["by_type_pooled"][t]["A"] for t in ("ties", "count_unit")))),
        E("P", r"raises accuracy on these questions from #\% to #\%", x("out/rescore/results.json:pooled A/n", lambda: pc(RSC()["pooled"]["A"], RSC()["pooled"]["n"])),
          x("out/rescore/results.json:pooled either/n", lambda: pc(RSC()["pooled"]["either"], RSC()["pooled"]["n"]))),
        # ---------------- method
        E("P", r"We developed the method on # AMBROSIA questions", j("out/ambrosia/decomposition.json", "models/sonnet/shape/n")),
        E("P", r"The final test uses # new test questions per model (# ambiguous, # unambiguous)",
          x("final.json:solvers/sonnet n_ambiguous + n_unambiguous", lambda: FIN()["solvers"]["sonnet"]["n_ambiguous"] + FIN()["solvers"]["sonnet"]["n_unambiguous"]),
          j("out/ambrosia/final/final.json", "solvers/sonnet/n_ambiguous"), j("out/ambrosia/final/final.json", "solvers/sonnet/n_unambiguous")),
        E("P", r"Disclosure methods on # new AMBROSIA test questions per model, with calls per question beside each point (Wilson #\% intervals).",
          x("final.json:solvers/sonnet n_ambiguous + n_unambiguous", lambda: FIN()["solvers"]["sonnet"]["n_ambiguous"] + FIN()["solvers"]["sonnet"]["n_unambiguous"]), K("confidence level")),
        E("P", r"Six of the # BIRD questions on which all four models", x("out/rescore/results.json:all_models_other (count)", lambda: len(RSC()["all_models_other"]))),
        E("P", r"and on # questions every model returns the other reading", x("out/rescore/results.json:all_models_other (count)", lambda: len(RSC()["all_models_other"]))),
        E("P", r"``Who is the tallest superhero?'' & # hero & # tied heroes", x("q802 reference rows", lambda: rs_rows("q802", "gold0")), x("q802 edited rows", lambda: rs_rows("q802", "gold"))),
        E("P", r"highest converted mana cost.'' & # card & # tied cards", x("q476 reference rows", lambda: rs_rows("q476", "gold0")), x("q476 edited rows", lambda: rs_rows("q476", "gold"))),
        E("P", r"lowest remaining?'' & # expense & # tied expenses", x("q1365 reference rows", lambda: rs_rows("q1365", "gold0")), x("q1365 edited rows", lambda: rs_rows("q1365", "gold"))),
        E("P", r"white border?'' & # rows & # cards", x("q383 reference value", lambda: rs_val("q383", "gold0")), x("q383 edited value", lambda: rs_val("q383", "gold"))),
        E("P", r"how many of them are male?'' & # lab records & # patients", x("q1283 reference value", lambda: rs_val("q1283", "gold0")), x("q1283 edited value", lambda: rs_val("q1283", "gold"))),
        E("P", r"normal level of total protein?'' & # lab records & # patients", x("q1289 reference value", lambda: rs_val("q1289", "gold0")), x("q1289 edited value", lambda: rs_val("q1289", "gold"))),
        E("P", r"on Formula~#, Haiku's rewrite", K("database name (Formula 1)")),
        E("P", r"it is # points more precise than DtP ($[#, #]$)", *[x("final.json:pooled/vs_dtp/precision[%d] x100" % i, (lambda i=i: 100 * FIN()["pooled"]["vs_dtp"]["precision"][i])) for i in range(3)]),
        E("P", r"only # of the held-out BIRD failures are open choices", d("fig3_real_benchmarks", "causes/confirmation/bird_heldout100/reading choice")),
        E("P", r"DtP shows about # wrong alternatives for each extra reading", j("out/ambrosia/final/exchange.json", "models/gpt-6-sol/rates/0.2/ratio")),
        E("P", r"DtP breaks even only if #\% of questions", j("out/ambrosia/final/exchange.json", "models/pooled/break_even", lambda v: 100 * v)),
        E("P", r"by # points pooled, mainly with GPT-Sol", x("final.json:pooled/vs_dtp/allfound[0] x -100", lambda: -100 * FIN()["pooled"]["vs_dtp"]["allfound"][0])),
        E("P", r"On # request sets (Table~\ref{tab:methods})", j("out/reqmethod100/results.json", "sonnet/sets")),
        E("P", r"by # points for Sonnet and # for GPT-Sol, and answers more specific requests correctly",
          *[x(RQMD + ": %s ours - dtp both readings x100" % m, (lambda m=m: 100 * rx(RQMD, r"ours - dtp \(paired\): both readings \+?([-\d.]+) \[([-\d.]+), ([-\d.]+)\]", "## %s " % m, 1))) for m in ("sonnet", "gpt-6-sol")]),
        E("P", r"the lead is small and not significant, # points for Sonnet and # for GPT-Sol",
          *[x(RQMD + ": %s ours - samplek both readings x100" % m, (lambda m=m: 100 * rx(RQMD, r"ours - samplek \(paired\): both readings \+?([-\d.]+) \[([-\d.]+), ([-\d.]+)\]", "## %s " % m, 1))) for m in ("sonnet", "gpt-6-sol")]),
        # ---------------- rewrite
        E("P", r"We report the # readings from accepted sets.", x(RW + ": pooled readings", lambda: rw(0, 0, 1))),
        E("P", r"Editing versus rewriting a request (# readings)", x(RW + ": pooled readings", lambda: rw(0, 0, 1))),
        E("P", r"computes #\% of the readings correctly", x(RW + ": pooled (c)", lambda: rw(0, 0, 4))),
        E("P", r"# points fewer for the interpretation rewrite and # for the standalone question", x(RW + ": pooled (c) - (b)", lambda: rw(0, 1, 1)), x(RW + ": pooled (c) - (d)", lambda: rw(0, 1, 5))),
        E("P", r"the judge finds the choice lost in only #\%", x(RW + ": 'the choice' share of what (b) lost", lambda: rx(RW, r"the choice \d+ \((\d+)%\)"))),
        E("P", r"comparison on # BIRD development questions where one library edit", x("out/rewrite/bird/runs: distinct question ids, null_filter excluded (GATE.md)", lambda: len({r["id"] for r in bird_clar()}))),
        E("P", r"Over # question--model pairs with Sonnet and GPT-Sol, adding the clause beats the standalone question, #\% against #\%.",
          x("out/rewrite/bird/runs pairs, null_filter excluded", lambda: len(bird_clar())), x("bird runs (c) right %", lambda: bird_acc("c")), x("bird runs (d) right %", lambda: bird_acc("d"))),
        # ---------------- related work, conclusion
        E("P", r"yet return both for the open request in only #--#\% of those sets", *rng(cbp, "fig5:models/*/covers_both_given_both_precise k/n")),
    ]
    L += comparison_table() + methods_table() + library_table()   # funnel: a figure since 2026-10-24   # 2026-10-24: Tables main, methods and the compact library table left the paper
    # ---------------- supplement
    lt = LIT
    L += [
        E("S", r"the share of # databases whose schema allows it", d("fig1_coverage", "n_buildable")),
        E("S", r"the queries delivered on the # evaluation databases", x("tab1_construction.json:pool (databases)", lambda: pool_by(None)["dbs"])),
        E("S", r"as a share of # databases: possible", d("fig1_coverage", "n_buildable")),
        E("S", r"(# with two accepted readings, # with one)", x("tab2_library.json:types[output_form]/raise", lambda: LIB()["output_form"]["raise"]),
          x("tab2_library.json:types[output_form]/settled_from_failures", lambda: LIB()["output_form"]["settled_from_failures"])),
        E("S", r"Possible reference errors (#) and", d("tab2_library", "n_defects")),
        E("S", r"counts the # accepted request sets by type, # of them with a choice in a filter", d("fig5_tab4_disclosure", "n_families"), d("filter_sets", "accepted")),
        E("S", r"Over the # sets whose choice a model proposes, aggregation level contributes #, ties #, missing values #, counting unit #, calculation #,",
          d("tab3_generation", "funnel/frozen"), *[d("tab3_generation", "funnel/frozen_types/" + t) for t in ("aggregation_level", "tie", "missing_values", "counting_unit", "calculation")]),
        E("S", r"The other # test per-entity counts", x("verdicts.json: filter sets rejected by the type rule", lambda: sum("rare in real data" in v.get("note", "") and k in {c.split("-")[-1] for c in part_cases(1)} for k, v in jl("human_supervision/verdicts.json").items()))),
        E("S", r"applied to the # library records of the twelve types, the rules find the choice in #, including all ties and quantifier records, # of # counting records and # of # relationship records",
          d("tab2_references", "library_check/all/1"), d("tab2_references", "library_check/all/0"),
          d("tab2_references", "library_check/counting_unit/0"), d("tab2_references", "library_check/counting_unit/1"),
          d("tab2_references", "library_check/relationship_role/0"), d("tab2_references", "library_check/relationship_role/1")),
        E("S", r"with ends at the #th and #th percentile of a date column",
          x("specbridge/pd/structures/compose.py: date range ends (0.3) x100", lambda: 100 * code("specbridge/pd/structures/compose.py", r"vs\[int\(len\(vs\) \* ([\d.]+)\)\], vs")),
          x("specbridge/pd/structures/compose.py: date range ends (0.7) x100", lambda: 100 * code("specbridge/pd/structures/compose.py", r"vs\[int\(len\(vs\) \* [\d.]+\)\], vs\[int\(len\(vs\) \* ([\d.]+)\)\]"))),
        E("S", r"only if it keeps #--#\% of the stage's rows", x("compose.py _predicates lo x100", lambda: 100 * code("specbridge/pd/structures/compose.py", r"_predicates\(self, t, lo=([\d.]+)")),
          x("compose.py _predicates hi x100", lambda: 100 * code("specbridge/pd/structures/compose.py", r"_predicates\(self, t, lo=[\d.]+, hi=([\d.]+)"))),
        E("S", r"The seed is #; # of # requested queries are delivered, # of them have readings with different answers, and # request sets pass all checks.",
          j("out/transfer/ext/request.json", "seed"), x(INV_EXT + ": ext row, tasks", lambda: rx(INV_EXT, r"\| ext \| (\d+) \|")), j("out/transfer/ext/request.json", "count"),
          x(INV_EXT + ": ext row, load-bearing", lambda: rx(INV_EXT, r"\| ext \| \d+ \| \d+ \| (\d+) \|")),
          x(INV_EXT + ": ext row, tasks with an open point", lambda: rx(INV_EXT, r"\| ext \|(?: \d+ \|){7} (\d+) \|"))),
        E("S", r"gives the results per model on the # accepted filter sets", d("filter_sets", "accepted")),
        E("S", r"The author rejects all # date-range sets.", x(FROZEN_ALL + " x verdicts: filter-run time_scope sets rejected", lambda: sum(1 for c in jl(FROZEN_ALL)["cases"] if c["case"] in part_cases(1) and c["type"] == "time_scope" and c not in accepted_cases()))),
        E("S", r"and so do # of the # BIRD and Spider references", x("fig6_inclination.json: boundary_between k summed over groups", lambda: sum(v["kinds"]["boundary_between"]["k"] for v in F6().values())),
          x("fig6_inclination.json: boundary_between n summed over groups", lambda: sum(v["kinds"]["boundary_between"]["n"] for v in F6().values()))),
        E("S", r"Forty of the # cutoff requests", d("filter_sets", "per_type_sets/value_representation")),
        E("S", r"in # of the # cases where they compute both", d("filter_sets", "by_type_pooled/value_representation/covers_if_both"), d("filter_sets", "by_type_pooled/value_representation/both_specific")),
        E("S", r"Filter request sets (#), four models pooled", d("filter_sets", "accepted")),
        E("S", r"choice in the filter and the wording of the open request (Wilson #\% intervals)", K("confidence level")),
        E("S", r"Of the # rejected sets, # are the date ranges, # are cutoffs", d("filter_sets", "verdicts/no"),
          x("filter-run rejected sets of type time_scope", lambda: sum(1 for c in jl(FROZEN_ALL)["cases"] if c["case"] in part_cases(1) and c["type"] == "time_scope" and c not in accepted_cases())),
          x("filter-run rejected sets of type value_representation", lambda: sum(1 for c in jl(FROZEN_ALL)["cases"] if c["case"] in part_cases(1) and c["type"] == "value_representation" and c not in accepted_cases()))),
        # cases table: literature values
        E("S", r"high-debt countries grew #\% a year, not $#\%$.", K(lt + ": Herndon et al. 2014"), K(lt + ": Herndon et al. 2014")),
        E("S", r"from #\% to #\%. & which column", K(lt + ": Obermeyer et al. 2019"), K(lt + ": Obermeyer et al. 2019")),
        E("S", r"given the same # million discharges, included #--#\% of them. # of # hospitals", *[K(lt + ": Shahian et al. 2010")] * 5),
        E("S", r"Public health & # UK contraceptive pill warning", K(lt + ": year of the event (Furedi 1999)")),
        E("S", r"pill use among under-#s falling from #\% to #\%, and by estimated NHS costs of \pounds # million for maternity care and \pounds # million for abortions",
          *[K(lt + ": Furedi 1999")] * 5),
        E("S", r"# teams analysed the same data. Their odds ratios ranged from # to #; # teams found a significant effect and # did not, using # combinations",
          *[K(lt + ": Silberzahn et al. 2018")] * 6),
        E("S", r"# teams analysed one dataset to test the same # hypotheses.", *[K(lt + ": Botvinik-Nezer et al. 2020")] * 2),
        E("S", r"Engineering & Ariane # flight #", *[K(lt + ": name of the launch, Lions 1996")] * 2),
        E("S", r"A #-bit floating-point value was converted to a #-bit signed integer that could not hold it; the launcher broke up about # seconds after lift-off.",
          *[K(lt + ": Lions 1996")] * 3),
        E("S", r"answered times # or as a fraction", K("definition: a percentage is a fraction times 100")),
        E("S", r"Of # such references, # are dropped", x("tab2_references.json: kept + dropped (summed)", lambda: sum(v[1] for v in REF().values()) + sum(P("tab2_references")["dropped"].values())),
          x("tab2_references.json: dropped (summed)", lambda: sum(P("tab2_references")["dropped"].values()))),
        # further details: seeds and versions
        E("S", r"use seed #; BIRD holdout selection uses #; the paired wording comparison uses #. Coverage uses seed # and depth-control runs seeds #--#.",
          j("out/comm_library/spider_split.json", "seed"), x("specbridge/comm/diagnose/tasks.py: split(seed=...)", lambda: code("specbridge/comm/diagnose/tasks.py", r"def split\(seed=(\d+)")),
          *[K("design parameter: random seed")] * 4),
        E("S", r"the Codex client from # to #.", K("software version (Codex client)"), K("software version (Codex client)")),
        # examples
    ]
    L += construction_table() + filter_table()
    return L


# ------------------------------------------------------------------------------------------------ the tex side
NUM = r"-?\d+(?:(?:\{,\}|,)\d{3}(?!\d))*(?:\.\d+)?|10\^\{-?\d+\}"
TOKEN = re.compile(r"10\^\{-?\d+\}|(?<![\w.\\{,])\d+(?:(?:\{,\}|,)\d{3}(?!\d))*(?:\.\d+)?")
SKIP = [r"(?:Haiku|Sonnet|Opus)~\d+(?:\.\d+)?", r"GPT-6", r"Spider[ ~]2\.0", r"Formula 1\b", r"\b\d+(?:\.\d+){2,}\b", r"\(\d\)(?=\s)"]
MASK_CMDS = {"cite": 1, "ref": 1, "extref": 1, "ext": 1, "eqref": 1, "label": 1, "url": 1, "texttt": 1, "sql": 1, "includegraphics": 1, "cmidrule": 1,
             "multicolumn": 2, "specialrule": 3, "setlength": 2, "renewcommand": 2, "providecommand": 2, "hspace": 1, "vspace": 1, "settopmatter": 1,
             "begin": 3, "end": 1, "bibliography": 1, "bibliographystyle": 1, "graphicspath": 1}
ENVS = ("equation", "align", "algorithmic")


def _group(t, i, open_, close):
    """End index (exclusive) of the balanced group starting at t[i] == open_, or i when there is none."""
    if i >= len(t) or t[i] != open_: return i
    depth = 0
    for k in range(i, len(t)):
        if t[k] == open_ and (k == 0 or t[k - 1] != "\\"): depth += 1
        elif t[k] == close and t[k - 1] != "\\":
            depth -= 1
            if depth == 0: return k + 1
    return len(t)


def _blank(s, a, b):
    s[a:b] = [c if c == "\n" else " " for c in s[a:b]]


def masks(t):
    """(clean, masked): clean blanks the preamble, bibliography and comments (anchors match it); masked also blanks what is not a
    claimed number (numbers are extracted from it). Both keep every character position."""
    s = list(t)
    a = t.find("\\begin{document}"); _blank(s, 0, a + len("\\begin{document}"))
    b = t.find("\\bibliographystyle"); _blank(s, b, len(t))
    for m in re.finditer(r"(?<!\\)%[^\n]*", t): _blank(s, m.start(), m.end())
    clean = "".join(s)
    for env in ENVS:
        for m in re.finditer(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), clean, re.S): _blank(s, m.start(), m.end())
    for m in re.finditer(r"\\([a-zA-Z]+)\*?", clean):
        n = MASK_CMDS.get(m.group(1))
        if not n: continue
        i = m.end()
        for _ in range(n):
            while i < len(clean) and clean[i] in " \t": i += 1
            j_ = _group(clean, i, "[", "]"); j_ = _group(clean, j_, "(", ")") if m.group(1) == "cmidrule" else j_
            k = _group(clean, j_, "{", "}")
            if k == j_ and j_ == i: break
            i = k
        _blank(s, m.start(), i)
    cur = "".join(s)
    for m in re.finditer(r"(?<!\\)\$(.+?)(?<!\\)\$", cur):                  # symbolic inline math: subscripts, function arguments
        if re.search(r"_|\(|\\mathcal|\\llbracket|\\operatorname", m.group(1)): _blank(s, m.start(), m.end())
    cur = "".join(s)
    for p in SKIP:
        for m in re.finditer(p, cur): _blank(s, m.start(), m.end())
    return clean, "".join(s)


def tokens(masked):
    out = []
    for m in TOKEN.finditer(masked):
        a = m.start()
        if masked[a - 1:a] == "-" and (a < 2 or not re.match(r"[\w\-}]", masked[a - 2])): a -= 1   # a minus sign, not a range dash or hyphen
        out.append((a, m.end(), masked[a:m.end()]))
    return out


def value_of(s):
    m = re.match(r"10\^\{(-?\d+)\}", s)
    if m: return 10.0 ** int(m.group(1)), None
    s = s.replace("{,}", "").replace(",", "")
    return float(s), (len(s.split(".")[1]) if "." in s else 0)


def anchor_re(a):
    r = re.escape(a).replace("\\ ", r"\s+").replace("\\\n", r"\s+")
    return re.compile(r.replace("\\#", r"(?:\\textbf\{(%s)\}|(%s))" % (NUM, NUM)))


def compare(printed, v, cmp, tol):
    p, dec = value_of(printed)
    t = tol if tol is not None else (0.5 * 10 ** -dec + 1e-9 if dec is not None else 0)
    return {"eq": abs(v - p) <= t, "lt": v < p, "le": v <= p + t, "gt": v > p, "ge": v >= p - t}[cmp]


def line_of(t, i): return t.count("\n", 0, i) + 1


def run(release=False):
    texts = {f: open(os.path.join(ROOT, p)).read() for f, p in TEX.items()}
    M_ = {f: masks(t) for f, t in texts.items()}
    rows, covered, problems = [], {f: {} for f in TEX}, []
    for e in ledger():
        f = e["file"]; clean = M_[f][0]; ms = list(anchor_re(e["anchor"]).finditer(clean))
        key = "%s:%s" % (TEX[f].split("/")[-1], e["anchor"][:70])
        if not ms or (e["occ"] is None and len(ms) > 1) or (e["occ"] is not None and e["occ"] >= len(ms)):
            problems.append(("ANCHOR", key, "anchor found %d times%s" % (len(ms), "" if e["occ"] is None else " (occ %d)" % e["occ"]))); continue
        m = ms[e["occ"] or 0]; n = len(m.groups()) // 2
        if n != len(e["specs"]):
            problems.append(("ANCHOR", key, "%d placeholders but %d specs" % (n, len(e["specs"])))); continue
        for i, sp in enumerate(e["specs"]):
            gi = 2 * i + 1 if m.group(2 * i + 1) is not None else 2 * i + 2
            printed, a = m.group(gi), m.start(gi)
            covered[f][a] = key
            r = {"key": "%s#%d" % (key, i), "file": TEX[f], "line": line_of(texts[f], a), "printed": printed.replace("{,}", ","), "src": sp.src, "kind": sp.kind, "value": ""}
            if sp.kind == "const": r["status"] = "const"
            elif sp.kind == "unsourced": r["status"] = "UNSOURCED"
            else:
                try:
                    v = sp.fn()
                    if sp.kind == "text":
                        pv = printed.replace("{,}", "").replace(",", ""); r["value"] = "in text" if pv in v else "absent"; r["status"] = "ok" if pv in v else "MISMATCH"
                    else:
                        vs = v if isinstance(v, list) else [v]
                        r["value"] = ", ".join("%.6g" % float(z) for z in vs)
                        r["status"] = "ok" if all(compare(printed, float(z), sp.cmp, sp.tol) for z in vs) else "MISMATCH"
                        if sp.cmp != "eq": r["value"] += " (%s %s)" % ({"lt": "<", "le": "<=", "gt": ">", "ge": ">="}[sp.cmp], printed)
                except Missing as ex:
                    r["status"] = "skipped" if release else "MISSING-DATA"; r["value"] = "missing " + str(ex)
                except Exception as ex:
                    r["status"] = "ERROR"; r["value"] = "%s: %s" % (type(ex).__name__, ex)
            rows.append(r)
    unledgered = []
    for f, (clean, masked) in M_.items():
        for a, b, s in tokens(masked):
            if a not in covered[f] and (a + 1) not in covered[f]:
                ln = line_of(texts[f], a); ctx = re.sub(r"\s+", " ", texts[f][max(0, a - 45):b + 25])
                unledgered.append({"file": TEX[f], "line": ln, "printed": s, "context": ctx})
    return rows, unledgered, problems


def main():
    args = sys.argv[1:]; mode = args[0] if args else "check"; release = "--release" in args
    rows, unl, probs = run(release)
    bad = [r for r in rows if r["status"] in ("MISMATCH", "ERROR", "MISSING-DATA")]
    if mode == "report":
        show = rows if "--all" in args else [r for r in rows if r["status"] != "ok"]
        print("%-28s %5s  %-12s %-26s %-11s %s" % ("file", "line", "printed", "recomputed", "status", "source"))
        for r in sorted(show, key=lambda r: (r["file"], r["line"])):
            print("%-28s %5d  %-12s %-26s %-11s %s" % (r["file"].split("/")[-1], r["line"], r["printed"], r["value"][:26], r["status"], r["src"]))
    else:
        for r in sorted(bad, key=lambda r: (r["file"], r["line"])):
            print("%s %s:%d printed %s, data %s  [%s]" % (r["status"], r["file"], r["line"], r["printed"], r["value"], r["src"]))
    for u in unl: print("UNLEDGERED %s:%d %s  ...%s..." % (u["file"], u["line"], u["printed"], u["context"]))
    for p in probs: print("%s %s: %s" % p)
    from collections import Counter
    c = Counter(r["status"] for r in rows)
    print("\nnumbers found: %d; in the ledger: %d (data %d, constants %d, unsourced %d); ok %d, mismatch %d, error %d, missing data %d, skipped %d; unledgered %d; anchor problems %d"
          % (len(rows) + len(unl), len(rows), sum(1 for r in rows if r["kind"] in ("data", "text")), c["const"], c["UNSOURCED"], c["ok"], c["MISMATCH"], c["ERROR"], c["MISSING-DATA"],
             c["skipped"], len(unl), len(probs)))
    if release and c["skipped"]: print("(--release: %d numbers whose data files are not in the release package were skipped)" % c["skipped"])
    sys.exit(1 if (bad or unl or probs) else 0)


if __name__ == "__main__":
    main()
