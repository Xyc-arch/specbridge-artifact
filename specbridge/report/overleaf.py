"""OVERLEAF <-> GITHUB <-> paper/tex, IN ONE COMMAND (2026-10-30). The co-authors' Overleaf edits always win.
    python -m specbridge.report.overleaf pull            Overleaf -> GitHub (Xyc-arch/specbridge) -> paper/tex
    python -m specbridge.report.overleaf push "<msg>"    pull first, then paper/tex -> GitHub and Overleaf
The clone paper/overleaf-git has two remotes: origin (GitHub) and overleaf (git.overleaf.com, token in the local .git/config only).
Overleaf keeps its own history, so files are compared by content: after every push both hold the same tree, and any later difference
is an Overleaf edit. A file that Overleaf changed and paper/tex also changed stops the command: nothing is overwritten."""
import os, re, subprocess as sp, sys

CLONE, TEX = "paper/overleaf-git", "paper/tex"
WHO = ["-c", "user.name=Xyc-arch", "-c", "user.email=yichen_xu@berkeley.edu"]


def git(*a, check=True):
    r = sp.run(["git", "-C", CLONE, *a], capture_output=True, text=True, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    if check and r.returncode: sys.exit("git %s failed: %s" % (a[0], re.sub(r"olp_\w+", "***", r.stderr.strip())))
    return r.stdout


def same(a, b):
    return os.path.exists(a) and os.path.exists(b) and open(a, "rb").read() == open(b, "rb").read()


def pull():
    git("fetch", "-q", "origin"); git("fetch", "-q", "overleaf"); git("checkout", "-q", "main"); git("reset", "-q", "--hard", "origin/main")
    changed = [f for f in git("diff", "--name-only", "origin/main", "overleaf/main").split() if f]
    if not changed: print("Overleaf: no new edits"); return
    # a file is ours-changed when paper/tex differs from what GitHub last held; then both sides edited it
    both = [f for f in changed if os.path.exists(os.path.join(TEX, f)) and not same(os.path.join(TEX, f), os.path.join(CLONE, f))]
    if both: sys.exit("STOP: edited on Overleaf and in paper/tex: %s\nmerge these by hand (Overleaf's text wins), then rerun" % ", ".join(both))
    git("checkout", "overleaf/main", "--", "."); git("add", "-A")
    gone = [f for f in git("diff", "--name-only", "--diff-filter=D", "--cached").split() if f]
    git(*WHO, "commit", "-qm", "Overleaf edits: " + ", ".join(changed[:8]) + (" and %d more" % (len(changed) - 8) if len(changed) > 8 else ""))
    git("push", "-q", "origin", "main")
    for f in changed:
        dst = os.path.join(TEX, f)
        if f in gone:
            if os.path.exists(dst): os.remove(dst)
        else:
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True); open(dst, "wb").write(open(os.path.join(CLONE, f), "rb").read())
    print("Overleaf edits pulled to GitHub and paper/tex:\n  " + "\n  ".join(changed))
    marks = sp.run(["grep", "-rln", "HAND-EDITED", TEX], capture_output=True, text=True).stdout.split()
    if marks: print("HAND-EDITED generated parts (update their generators before regenerating):\n  " + "\n  ".join(marks))


def push(msg):
    pull()
    tracked = git("ls-files").split()
    for f in tracked:                                         # only the files Overleaf holds; paper/tex is the source
        src = os.path.join(TEX, f)
        if os.path.exists(src) and not same(src, os.path.join(CLONE, f)):
            open(os.path.join(CLONE, f), "wb").write(open(src, "rb").read())
    git("add", "-A")
    if not git("diff", "--cached", "--name-only").strip(): print("nothing to push"); return
    files = git("diff", "--cached", "--name-only").split()
    git(*WHO, "commit", "-qm", msg); git("push", "-q", "origin", "main")
    git("branch", "-f", "olpush", "overleaf/main"); git("checkout", "-q", "olpush"); git("checkout", "main", "--", ".")
    git("add", "-A"); git(*WHO, "commit", "-qm", msg); git("push", "-q", "overleaf", "olpush:main"); git("checkout", "-q", "main")
    assert not git("diff", "--name-only", "main", "olpush").strip(), "Overleaf and GitHub differ after the push"
    print("pushed to GitHub and Overleaf:\n  " + "\n  ".join(files))


if __name__ == "__main__":
    {"pull": pull, "push": lambda: push(sys.argv[2])}[sys.argv[1]]()
