"""Build the paper's figures from these sources: python3 build.py [name ...]   (no name: every col_*.tex and diag_*.tex)

Each figure is a standalone pdfLaTeX file that reads sbstyle.tex and its files in data/. A figure with a line
'\\def\\axw{...}% fit k' is rebuilt until it is exactly one column wide ('fit k wide': two columns); k is how many times the
axis width appears across the figure. The finished PDF is copied to the parent folder (figures/); nothing else is written here.
Needs pdfLaTeX (TeX Live with pgfplots, libertine, zi4, newtx) and Ghostscript (to measure the width).
"""
import glob, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = {"col": 241.14749, "wide": 506.295}           # acmart sigconf \columnwidth and \textwidth, pt
FIT = re.compile(r"\\def\\axw\{([\d.]+)\}% fit ([\d.]+)( wide)?")


def compile_(name, tmp):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", tmp, name + ".tex"],
                       cwd=HERE, capture_output=True, text=True)
    if r.returncode:
        log = open(os.path.join(tmp, name + ".log"), errors="replace").read(); i = log.find("\n!")
        sys.exit("%s failed:%s" % (name, log[i:i + 600]))
    box = subprocess.run(["gs", "-q", "-dNODISPLAY", "-dNOSAFER", "-c",
                          "(%s) (r) file runpdfbegin 1 pdfgetpage /MediaBox pget pop == quit" % os.path.join(tmp, name + ".pdf")],
                         capture_output=True, text=True).stdout.strip("[]\n ").split()
    b = [float(x) for x in box]
    return (b[2] - b[0]) * 72.27 / 72, (b[3] - b[1]) * 72.27 / 72


def build(name, tmp):
    path = os.path.join(HERE, name + ".tex")
    for _ in range(4):
        w, h = compile_(name, tmp)
        src = open(path).read(); m = FIT.search(src)
        if not m: break
        target = TARGET["wide" if m.group(3) else "col"]
        if abs(w - target) < 0.02: break
        src = src[:m.start(1)] + "%.2f" % (float(m.group(1)) + (target - w) / float(m.group(2))) + src[m.end(1):]
        open(path, "w").write(src)
    shutil.copy(os.path.join(tmp, name + ".pdf"), os.path.join(HERE, "..", name + ".pdf"))
    print("%-18s %.2f x %.2f pt -> figures/%s.pdf" % (name, w, h, name))


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(HERE, "col_*.tex")) + glob.glob(os.path.join(HERE, "diag_*.tex")))
    with tempfile.TemporaryDirectory() as tmp:
        for n in names: build(n, tmp)
