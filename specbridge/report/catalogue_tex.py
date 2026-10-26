"""THE SUPPLEMENT'S CATALOGUE (2026-10-25): how widely each choice type occurs (every library choice and every accepted request
set, counted by source and database), and selected examples of each, chosen by a fixed rule so that a reader can check them by
hand. The full lists are in the package (library/examples.jsonl, benchmark/request_sets.jsonl). Generated from the same files as
the paper's numbers; no model calls.
    python -m specbridge.report.catalogue_tex   -> paper/tex/cat_breadth.tex, cat_library.tex, cat_sets.tex"""
import collections, json, re
from specbridge.report import accepted as AC
from specbridge.comm.transfer import combined as CB

OUT = "paper/tex/"
TYPE = {"aggregation_level": "Aggregation level", "calculation": "Calculation", "comparison_quantifier": "Quantifier",
        "condition_linkage": "Condition linkage", "counting_unit": "Counting unit", "missing_values": "Missing values",
        "negated_membership_scope": "Negation", "population_scope": "Population scope", "referent_column": "Referent column",
        "relationship_role": "Relationship role", "strict_cutoff": "Strict cutoff", "ties_and_selection": "Ties and selection",
        "time_scope": "Time scope", "value_matching": "Value matching",
        "tie": "Ties and selection", "value_representation": "Strict cutoff"}          # the request sets' names for the same types
SOURCE = {"sakila_1": "Spider", "baseball_1": "Spider", "chinook_1": "Spider", "customers_and_invoices": "Spider", "financial": "BIRD",
          "formula_1": "BIRD", "student_club": "BIRD", "thrombosis_prediction": "BIRD"}             # the rest are LiveSQLBench
UNI = {"−": "$-$", "÷": "$\\div$", "–": "--", "—": "---", "→": "$\\rightarrow$", "×": "$\\times$",
       " ": "~", "≤": "$\\leq$", "≥": "$\\geq$", "“": "``", "”": "''", "‘": "`", "’": "'"}
N_LIB, N_SETS = 3, 4                                        # examples per type


def esc(s):
    """Plain text to LaTeX: special characters escaped, `code` set in typewriter type with break points after _ and ."""
    def plain(t):
        t = t.replace("\\", "\\textbackslash{}")
        for a, b in (("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"), ("_", "\\_"), ("{", "\\{"), ("}", "\\}"),
                     ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"), ("<", "\\textless{}"), (">", "\\textgreater{}")):
            t = t.replace(a, b)
        t = t.replace("\\textbackslash\\{\\}", "\\textbackslash{}")
        return "".join(UNI.get(c, c) for c in t)
    out = []
    for i, part in enumerate(re.split(r"`([^`]*)`", (s or "").strip())):
        out.append("\\texttt{%s}" % plain(part).replace("\\_", "\\_\\allowbreak{}").replace(".", ".\\allowbreak{}") if i % 2 else plain(part))
    return re.sub(r"\s*\n\s*", " ", "".join(out))


def tt(s):
    return "\\texttt{%s}" % esc(s).replace("\\_", "\\_\\allowbreak{}")


def _strict_only(a, b):                                     # as specbridge.report.exhibit_data.tab2 splits value representation
    n = lambda q: re.sub(r"\s+", " ", re.sub(r"(\S+) BETWEEN (\S+) AND (\S+)", r"\1 > \2 AND \1 < \3", q, flags=re.I)).replace(">=", ">").replace("<=", "<").strip().rstrip(";")
    return a != b and n(a) == n(b)


def lib_rows():
    """The choices of meaning from failures that Table S2 counts, with their display type."""
    rows = []
    for e in map(json.loads, open("library/examples.jsonl")):
        if e["type"] == "output_form" or "decision site" in str(e.get("provenance", {}).get("from")): continue
        R = {r.get("id"): r for r in e.get("readings", [])}; t = e["type"]
        if t == "value_representation":
            t = "strict_cutoff" if R.get("A") and R.get("B") and _strict_only(R["A"].get("sql", ""), R["B"].get("sql", "")) else "value_matching"
        rows.append(dict(e, display=TYPE[t]))
    return rows


def set_rows():
    C, per = AC.per_set()
    V = json.load(open("human_supervision/verdicts.json")); W = json.load(open(CB.D + "/written.json")); main = set(CB.part_cases(0))
    keys = sorted(k for k in C if V[k.split("-")[-1]]["verdict"] == "yes")
    return [dict(key=k, id=k.split("-")[-1], case=C[k], written=W[k], display=TYPE[C[k]["type"]], source=SOURCE.get(C[k]["database"], "LiveSQLBench"),
                 filter=k not in main, outcomes=[per[(m, k)] for m in AC.MODELS]) for k in keys]


def pick(xs, n, key, group, prefer=lambda x: 0):
    """Up to n items with distinct `group` values: first one per preferred class in turn (prefer gives the class order), then the
    rest, each time the smallest `key` among the groups not yet used."""
    out, used = [], set()
    classes = sorted({prefer(x) for x in xs})
    for c in classes + [None]:
        for x in sorted(xs, key=key):
            if len(out) >= n: return out
            if (c is None or prefer(x) == c) and group(x) not in used and x not in out:
                out.append(x); used.add(group(x))
                if c is not None: break
    return out


def short_diff(a, b):
    """How the two reference answers differ, in a few words."""
    if len(a) != len(b): return "%d vs %d rows" % (len(a), len(b))
    ka, kb = [r[:1] for r in a], [r[:1] for r in b]
    if set(map(str, ka)) != set(map(str, kb)): return "%d rows; %d differ" % (len(a), len(set(map(str, ka)) ^ set(map(str, kb))) // 2 or 1)
    best = None
    ia = {str(r[:1]): r for r in a}
    for r in b:
        for u, v in zip(ia.get(str(r[:1]), []), r):
            if isinstance(u, (int, float)) and isinstance(v, (int, float)) and u != v:
                rel = abs(u - v) / max(abs(u), abs(v))
                if best is None or rel > best[2]: best = (u, v, rel)
    if best: return "value %.4g vs %.4g" % (best[0], best[1])
    return "same rows, other order" if ka != kb else "same rows"


def breadth(L, S):
    """Two blocks, each over its own types: library choices by the benchmark that revealed them, and accepted request sets by
    the source of their database. Each block lists only the types it has, so no column is mostly empty."""
    BN = {"BIRD dev": "BIRD", "Spider dev": "Spider"}
    T = ["% generated by python -m specbridge.report.catalogue_tex; do not edit",
         "\\begin{tabular*}{\\columnwidth}{@{}l@{\\extracolsep{\\fill}}rrl@{}}", "\\toprule",
         "Library choice type & Choices & DBs & Found in\\\\", "\\midrule"]
    for t in sorted({r["display"] for r in L}):
        xs = [r for r in L if r["display"] == t]
        found = ", ".join(b for b in ("BIRD", "Spider") if any(BN[r["source"]["benchmark"]] == b for r in xs))
        T.append("%s & %d & %d & %s\\\\" % (t, len(xs), len({r["source"]["database"] for r in xs}), found))
    T += ["\\midrule", "Total & %d & %d & BIRD, Spider\\\\" % (len(L), len({r["source"]["database"] for r in L})), "\\bottomrule",
          "\\end{tabular*}", "", "\\vspace{6pt}", "",
          "\\begin{tabular*}{\\columnwidth}{@{}l@{\\extracolsep{\\fill}}rrrrr@{}}", "\\toprule",
          "Request set type & Sets & DBs & Spider & BIRD & LiveSQL\\\\", "\\midrule"]
    st = lambda xs, s: sum(1 for x in xs if x["source"] == s)
    for t in sorted({x["display"] for x in S}):
        xs = [x for x in S if x["display"] == t]
        T.append("%s & %d & %d & %d & %d & %d\\\\" % (t, len(xs), len({x["case"]["database"] for x in xs}), st(xs, "Spider"), st(xs, "BIRD"), st(xs, "LiveSQLBench")))
    T += ["\\midrule", "Total & %d & %d & %d & %d & %d\\\\" % (len(S), len({x["case"]["database"] for x in S}), st(S, "Spider"), st(S, "BIRD"), st(S, "LiveSQLBench")),
          "\\bottomrule", "\\end{tabular*}"]
    open(OUT + "cat_breadth.tex", "w").write("\n".join(T) + "\n")


def library(L):
    order = sorted({r["display"] for r in L})
    T = ["% generated by python -m specbridge.report.catalogue_tex; do not edit",
         "\\begin{xltabular}{\\textwidth}{@{}>{\\raggedright\\arraybackslash}p{2.3cm}>{\\hsize=1.15\\hsize\\raggedright\\arraybackslash}X"
         ">{\\hsize=0.85\\hsize\\raggedright\\arraybackslash}X>{\\raggedright\\arraybackslash}p{1.2cm}@{}}",
         "\\caption{Selected library choices, up to %d per type.}\\label{tab:catlibrary}\\\\" % N_LIB,
         "\\toprule", "Source & Question & The choice & Wording\\\\", "\\midrule", "\\endfirsthead",
         "\\toprule", "Source & Question & The choice & Wording\\\\", "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    for i, t in enumerate(order):
        xs = [r for r in L if r["display"] == t]
        sel = pick(xs, N_LIB, key=lambda r: (not r["raise"], len(r["question"]), r["id"]), group=lambda r: r["source"]["database"],
                   prefer=lambda r: r["source"]["benchmark"] != "BIRD dev")
        sel.sort(key=lambda r: (not r["raise"], r["source"]["benchmark"] != "BIRD dev", r["source"]["database"]))
        if i: T.append("\\midrule")
        T.append("\\multicolumn{4}{@{}l}{\\textbf{%s} (%d of %d shown)}\\\\[1pt]" % (t, len(sel), len(xs)))
        for r in sel:
            s = r["source"]
            T.append("%s, %s & %s & %s & %s\\\\[2pt]" % (s["benchmark"].replace(" dev", ""), tt(s["database"]), esc(r["question"]),
                                                        esc(r["decision"]), "open" if r["raise"] else "settles it"))
    T.append("\\end{xltabular}")
    open(OUT + "cat_library.tex", "w").write("\n".join(T) + "\n")


def sets(S):
    code = lambda x: "B" if x["covers"] else ("N" if x["single_both"] and x["names"] else ("S" if x["single_both"] else "-"))
    rank = {"Spider": 0, "BIRD": 1, "LiveSQLBench": 2}
    T = ["% generated by python -m specbridge.report.catalogue_tex; do not edit",
         "\\begin{xltabular}{\\textwidth}{@{}>{\\raggedright\\arraybackslash}p{1.95cm}>{\\hsize=1.1\\hsize\\raggedright\\arraybackslash}X"
         ">{\\hsize=0.9\\hsize\\raggedright\\arraybackslash}X>{\\raggedright\\arraybackslash}p{1.45cm}>{\\centering\\arraybackslash}p{1.0cm}@{}}",
         "\\caption{Selected accepted request sets, up to %d per type.}\\label{tab:catsets}\\\\" % N_SETS,
         "\\toprule", "Set & Open request & Interpretations & Answers & Models\\\\", "\\midrule", "\\endfirsthead",
         "\\toprule", "Set & Open request & Interpretations & Answers & Models\\\\", "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    for i, t in enumerate(sorted({x["display"] for x in S})):
        xs = [x for x in S if x["display"] == t]
        sel = pick(xs, N_SETS, key=lambda x: (len(x["written"]["open"]), x["id"]), group=lambda x: x["case"]["database"], prefer=lambda x: rank[x["source"]])
        sel.sort(key=lambda x: (rank[x["source"]], x["case"]["database"]))
        if i: T.append("\\midrule")
        T.append("\\multicolumn{5}{@{}l}{\\textbf{%s} (%d of %d shown)}\\\\[1pt]" % (t, len(sel), len(xs)))
        for x in sel:
            c, w = x["case"], x["written"]
            T.append("%s\\newline %s%s & %s & \\textbf{A:} %s\\newline \\textbf{B:} %s & %s & \\texttt{%s}\\\\[2pt]" % (
                tt(c["database"]), tt(x["id"]), "\\newline (filter)" if x["filter"] else "", esc(w["open"]), esc(w["reading_A"]),
                esc(w["reading_B"]), esc(short_diff(c["answer_A"], c["answer_B"] or [])), "\\,".join(code(o) for o in x["outcomes"])))
    T.append("\\end{xltabular}")
    open(OUT + "cat_sets.tex", "w").write("\n".join(T) + "\n")


if __name__ == "__main__":
    L, S = lib_rows(), set_rows()
    breadth(L, S); library(L); sets(S)
    print("library choices: %d | accepted request sets: %d" % (len(L), len(S)))
