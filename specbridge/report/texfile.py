"""ONE .tex FILE PER DOCUMENT (2026-10-15): paper/tex/specbridge.tex and supplement.tex each hold their whole text. Generated
parts live between marker lines and are replaced in place:
    % >>> <name> ...            first line of a generated region
    % <<< <name>                last line
    python -m specbridge.report.texfile labels <aux> <tex> <region> [prefix]   # \\newlabel lines of an .aux into a region
Used by specbridge.report.tables_tex (generated tables) and paper/tex/Makefile (cross-reference labels)."""
import re, sys


def splice(path, name, body):
    s = open(path).read()
    m = re.search(r"(?m)^% >>> " + re.escape(name) + r"\b.*\n", s); e = re.search(r"(?m)^% <<< " + re.escape(name) + r"\s*$", s)
    assert m and e and m.end() <= e.start(), "no region %r in %s" % (name, path)
    new = s[:m.end()] + body.rstrip("\n") + "\n" + s[e.start():]
    if new != s: open(path, "w").write(new)


def labels(aux, tex, name, prefix=""):
    """The \\newlabel lines of `aux` whose names look like sec:, fig:, tab:, eq:, alg: ..., optionally prefixed, as the region body."""
    L = [l.rstrip("\n") for l in open(aux) if re.match(r"\\newlabel\{[a-z]+:", l)]
    if prefix: L = [l.replace("\\newlabel{", "\\newlabel{" + prefix, 1) for l in L]
    splice(tex, name, "\\AtBeginDocument{%\n" + "\n".join(L) + "\n}")


if __name__ == "__main__":
    if sys.argv[1] == "labels": labels(*sys.argv[2:])
