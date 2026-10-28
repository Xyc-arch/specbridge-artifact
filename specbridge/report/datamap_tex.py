"""DATA MAP FOR THE SUPPLEMENT (2026-10-25): which data each experiment uses, how the request sets are built from the sources,
and every sample size. Writes paper/tex/figures/src/diag_datamap.tex, Figure S1 in the style of every figure (figures/src/sbstyle.tex;
built by paper/tex/Makefile into figures/diag_datamap.pdf). Run it after a build of the paper: it reads the .aux files.
    python -m specbridge.report.datamap_tex
Every count the paper prints is read through the number ledger (specbridge.report.numbers), from the same entry that checks the
paper's text, so the map cannot disagree with the paper. The library counts come from specbridge.report.catalogue_tex.lib_rows; the
two draw sizes the paper no longer prints come from the files that hold the draws (topk.subset(), out/reqmethod100/sets.json).
paper/tex/figures/tikz/datamap.tex is the legacy XeLaTeX version this script wrote before 2026-10-27."""
from specbridge.report import numbers as N, catalogue_tex as C

OUT = "paper/tex/figures/src/diag_datamap.tex"
REWRITE_PER_MODEL = 120          # design parameter: first 120 readings per model in the pre-shuffled order (out/rewrite/GATE.md)


def V(anchor, i=0):
    """The value of placeholder i of the one ledger entry whose anchor contains `anchor`."""
    E = [e for e in N.ledger() if anchor in e["anchor"]]
    assert len(E) == 1, (anchor, len(E))
    sp = E[0]["specs"][i]; assert sp.kind == "data", (anchor, i, sp.kind)
    v = sp.fn(); return int(round(float(v[0] if isinstance(v, list) else v)))


def n(v): return "{:,}".format(v)


def F(*labels):
    """Several labels in one reference: 'Figs.~8, 10, 11'; mixed kinds stay separate: 'Fig.~18, Table~5'."""
    out = []
    for l in labels:
        r = R(l); k, num = r.split("~")
        if out and out[-1][0] == k: out[-1][1].append(num)
        else: out.append((k, [num]))
    return ", ".join(("%ss.~%s" % (k[:-1], ", ".join(v)) if len(v) > 1 and k == "Fig." else "%s~%s" % (k, ", ".join(v))) for k, v in out)


def R(label):
    """'Fig. 8', 'Table S1', 'Sec. 5': the number LaTeX gave a label, from the paper's or the supplement's .aux file."""
    import re
    for aux, pre in (("paper/tex/specbridge.aux", ""), ("paper/tex/supplement.aux", "")):
        m = re.search(r"\\newlabel\{%s\}\{\{([^}]*)\}" % re.escape(label), open(aux).read())
        if m:
            num = m.group(1); kind = label.split(":")[0]
            return {"fig": "Fig.~", "tab": "Table~", "sec": "Sec.~"}[kind] + num
    raise KeyError(label)


def values():
    from specbridge.comm.transfer import topk
    L = C.lib_rows()
    S = dict(tried=V("Its rules find usable queries on", 1), usable=V("Its rules find usable queries on", 0),
             dbs=V("Request sets use # databases"), delivered=V("it delivers # of # requested", 1), requested=V("it delivers # of # requested", 2),
             tasks=V("Exact description versus natural request on #"), swap=V("natural requests of # random generated tasks"),
             plan=V("tasks drawn at random across choice types"), attempts=V("(# attempts). The labels"),
             configs=len(N.P("fig1_coverage")["ablation"]),
             main=N.P("tab3_generation")["funnel"]["frozen"], filt=sum(N.FIL()["verdicts"].values()),
             checked=V("in each of the # sets that pass all checks"), author=V("They keep # of the # sets", 0), final=V("of them pass the authors' review", 1),
             filt_acc=N.FIL()["accepted"],
             lib=len(L), lib_open=sum(1 for r in L if r["raise"]), lib_types=len({r["display"] for r in L}), lib_dbs=len({r["source"]["database"] for r in L}),
             bird_mine=V("BIRD development questions on five databases and", 0), bird_held=V("Spider development questions, never used for mining", 0),
             spider_mine=V("BIRD development questions on five databases and", 1), spider_held=V("Spider development questions, never used for mining", 1),
             amb_dev=V("We developed the method on # AMBROSIA"), amb_test=V("The final test uses # new test questions", 0),
             amb_ambig=V("The final test uses # new test questions", 1), amb_clear=V("The final test uses # new test questions", 2),
             conv=V("In # tie and counting sets"), samp=V("randomly drawn sets, five SQL-only", 0), samp_draw=len(topk.subset()),
             impact=V("Of # such questions", 0), changed=V("Of # such questions", 1), rescore=V("We ask the four models # BIRD"),
             meth=V("The final test uses # new test questions", 3), meth_draw=len(N.jl("out/reqmethod100/sets.json")["sets"]),
             rw=V("we report # interpretations drawn at random", 0), bird_rw=V("comparison on # BIRD development questions"))
    S["main_acc"] = S["final"] - S["filt_acc"]; S["lib_settled"] = S["lib"] - S["lib_open"]
    assert S["main"] + S["filt"] == S["checked"], S
    return S


def tex(S):
    s = {k: n(v) for k, v in S.items()}
    X = ("0", "\\X", "2*\\X", "3*\\X")                                       # the four columns; rows r2, r3 hang below the boxes above
    at = lambda i, row: "(%s,0)" % X[i] if row is None else "(%s)" % row if i == 0 else "(%s,0 |- %s)" % (X[i], row)
    box = lambda name, i, row, h, head, body, style="sb box": (                # h: height of the text block, so the boxes of a row align
        "\\node[%s] (%s) at %s {\\card{%dpt}{%s}{%s}};" % (style, name, at(i, row), h, head, body))
    ex = lambda e, txt: "\\ex{%s}{%s}" % (e, txt)                             # one exhibit; its number from the paper's or the supplement's .aux file
    exp = lambda name, i, head, *lines: box(name, i, "r3", 98, head, "%\n  " + "%\n  ".join("".join(l) for l in lines), "sb box, fill=sbPale")
    T = [r"% Figure S1 (diag_datamap, two columns): sources, data built from them, experiments with their sample sizes.",
         r"% generated by python -m specbridge.report.datamap_tex (counts from the number ledger, exhibit numbers from the .aux files); do not edit",
         r"\documentclass[border=0pt]{standalone}",
         r"\input{sbstyle}",
         r"% a card: bold heading on its own line, then the text; #1 height of the text block",
         r"\newcommand{\card}[3]{\parbox[t][#1][t]{115.57pt}{\hyphenpenalty=10000\exhyphenpenalty=10000\raggedright\textbf{#2}\\[1pt]#3}}",
         r"\newcommand{\ex}[2]{\hangindent=0.8em\hangafter=1 \textbf{#1}\enspace #2\par}% one exhibit of an experiment",
         r"\begin{document}",
         r"\begin{tikzpicture}[sb diagram, x=1pt, y=1pt, band/.style={sb head, anchor=south west}]",
         r"\def\X{128.075}% column pitch: (506.295 - 3 x 6) / 4 + 6",
         # ---- sources
         r"% ---- sources", r"\node[band] at (0,4) {Sources};",
         box("dbs", 0, None, 72, "Databases",
             "Spider, BIRD development, LiveSQLBench: %(tried)s tried, %(usable)s usable for the generator.\\\\%(dbs)s evaluation databases, four per source" % s),
         box("mod", 1, None, 72, "Models",
             "Evaluated: Haiku, Sonnet, GPT-Sol, GPT-Luna.\\\\Opus writes and reviews request sets with Sonnet, reviews Sonnet's natural requests, and judges explanations; it is not evaluated"),
         box("qs", 2, None, 72, "BIRD and Spider questions",
             "BIRD development: %(bird_mine)s questions on five databases to mine choices, %(bird_held)s held out.\\\\"
             "Spider development: %(spider_mine)s to mine, %(spider_held)s held out.\\\\References of all silent questions, training and development" % s),
         box("amb", 3, None, 72, "AMBROSIA",
             "%(amb_dev)s development questions; %(amb_test)s new test questions per model (%(amb_ambig)s ambiguous, %(amb_clear)s unambiguous)" % s),
         # ---- built data
         r"% ---- built from them", r"\path (0,0 |- dbs.south) ++(0,-20) coordinate (r2);", r"\node[band] at ([yshift=4pt]r2) {Built from them};",
         box("gen", 0, "r2", 45, "Generated tasks",
             "on the %(dbs)s evaluation databases: %(delivered)s of %(requested)s queries delivered; %(tasks)s tasks with a natural request" % s),
         box("rs", 1, "r2", 45, "Request sets (%s)" % F("fig:funnel"),
             "main run %(main)s and filter run %(filt)s pass all checks (%(checked)s); the author keeps %(author)s; the 1\\%% rule leaves \\textbf{%(final)s} (%(main_acc)s without, %(filt_acc)s with a filter)" % s),
         box("lib", 2, "r2", 45, "Choice library (%s)" % F("fig:choices", "tab:librarydetail"),
             "%(lib)s choices (%(lib_open)s open, %(lib_settled)s settled) in %(lib_types)s types, from benchmark failures on %(lib_dbs)s databases" % s),
         # ---- experiments: one exhibit of the paper per \ex, in two source lines per box
         r"% ---- experiments", r"\path (0,0 |- gen.south) ++(0,-20) coordinate (r3);", r"\node[band] at ([yshift=4pt]r3) {Experiments: exhibit and sample size};",
         exp("e1", 0, "Generator (%s)" % R("sec:specresults"),
             [ex(F("fig:coverage"), "coverage on %(tried)s databases" % s),
              ex(F("tab:construction"), "%(delivered)s of %(requested)s queries" % s),
              ex(F("fig:ablation"), "rules removed, %(configs)s configurations $\\times$ %(attempts)s attempts" % s)],
             [ex(F("fig:specification"), "exact vs.\\ natural request, %(tasks)s tasks $\\times$ 4 models" % s),
              ex(R("sec:specresults"), "second writer, %(swap)s random tasks" % s),
              ex(R("sec:specresults"), "plan vs.\\ direct writing, %(plan)s tasks" % s)]),
         exp("e2", 1, "Do models report the choice? (%s)" % R("sec:disclosure"),
             [ex(F("fig:disclosure", "fig:outcomes", "fig:bytype"), "%(final)s sets $\\times$ 4 models" % s),
              ex(F("fig:decomposition"), "missed interpretations; also AMBROSIA"),
              ex(F("fig:conventions"), "%(conv)s tie and counting sets" % s)],
             [ex(R("sec:disclosure"), "five samples, %(samp)s sets (draw of %(samp_draw)s)" % s),
              ex(R("sec:setup"), "exploration, %(bird_held)s held-out BIRD questions" % s),
              ex(F("tab:filtersets"), "%(filt_acc)s filter sets" % s)]),
         exp("e3", 2, "Can benchmarks see it? (%s)" % R("sec:diagnosis"),
             [ex(F("fig:real"), "held-out %(bird_held)s BIRD, %(spider_held)s Spider $\\times$ 4 models" % s),
              ex(F("fig:causes"), "failures among the mining questions")],
             [ex(F("fig:defaults"), "silent references, by author group"),
              ex(F("fig:impact"), "%(impact)s silent BIRD questions, %(changed)s change" % s),
              ex(F("tab:answers"), "%(rescore)s BIRD questions $\\times$ 4 models" % s)]),
         exp("e4", 3, "Two design rules (%s)" % R("sec:method"),
             [ex(F("fig:method", "tab:methods"), "AMBROSIA, %(amb_test)s per model, Sonnet and GPT-Sol" % s),
              ex(F("tab:methods"), "%(meth)s request sets (draw of %(meth_draw)s)" % s)],
             [ex(F("fig:breakeven"), "AMBROSIA, both models pooled"),
              ex(F("fig:rewrite"), "%(rw)s interpretations (draw of %(rwpm)s per model) $\\times$ 4 models" % dict(s, rwpm=n(REWRITE_PER_MODEL))),
              ex(R("sec:rewrite"), "%(bird_rw)s BIRD questions, Sonnet and GPT-Sol" % s)]),
         r"% ---- arrows: what is built from what, and what each experiment uses",
         r"\draw[sb arrow] (dbs.south) -- (gen.north);",
         r"\draw[sb arrow] (qs.south) -- (lib.north);",
         r"\draw[sb arrow] (gen.east) -- (rs.west);",
         r"\draw[sb arrow] (lib.west) -- (rs.east);",
         r"\draw[sb arrow] (gen.south) -- (e1.north);",
         r"\draw[sb arrow] (rs.south) -- (e2.north);",
         r"\draw[sb arrow] (lib.south) -- (e3.north);",
         r"\draw[sb arrow] (amb.south) -- (e4.north);",
         r"\draw[sb arrow] (rs.south east) .. controls +(34,-10) and +(-45,13) .. (e4.north west);",
         r"\end{tikzpicture}", r"\end{document}"]
    return "\n".join(T) + "\n"


if __name__ == "__main__":
    S = values(); open(OUT, "w").write(tex(S)); print("data map:", OUT, "| request sets %(checked)d -> %(author)d -> %(final)d" % S)
