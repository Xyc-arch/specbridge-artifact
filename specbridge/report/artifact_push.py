"""UPDATE THE PUBLIC ARTIFACT, INCREMENTALLY (2026-10-28). Builds release/, copies it into the artifact clone, and reruns only the
`make reproduce` steps whose code or data changed, then the full `make check test` (every number, table and figure against the
paper). Pushes only if every check passes and the rerun steps reproduce their committed outputs exactly.
    python -m specbridge.report.artifact_push <artifact clone> <venv bin> "<commit message>" [--full]
A step reruns when its module, a module it imports (transitively, inside specbridge/), or a data path its sources name has
changed. A change to the Makefile, requirements or reproduce/ scripts reruns everything (`make all`)."""
import ast, os, re, subprocess as sp, sys, time

FULL_IF = ("Makefile", "requirements.txt", "reproduce/check.py", "reproduce/collect.py", "reproduce/fetch_bird.sh")


def sh(cmd, cwd, env=None, out=None):
    t = time.time(); r = sp.run(cmd, shell=True, cwd=cwd, env=env, stdout=out or sp.PIPE, stderr=sp.STDOUT, text=True)
    return r.returncode, (r.stdout or ""), time.time() - t


def steps(clone):
    """The `make reproduce` commands, in order."""
    mk = open(os.path.join(clone, "Makefile")).read().split("\nreproduce:")[1].split("\n\n")[0]
    return [l.strip() for l in mk.splitlines()[1:] if l.startswith("\t")]


def module_file(clone, mod):
    p = os.path.join(clone, *mod.split("."))
    return p + ".py" if os.path.exists(p + ".py") else os.path.join(p, "__init__.py")


def sources(clone, cmd):
    """Files a step runs: its module or script and, transitively, the specbridge modules they import."""
    m = re.search(r"-m (specbridge[\w.]*)", cmd); s = re.search(r"python3? (?:-I )?([\w/.]+\.py)", cmd)
    todo = [module_file(clone, m.group(1))] if m else [os.path.join(clone, s.group(1))] if s else []; seen = set()
    while todo:
        f = todo.pop()
        if f in seen or not os.path.exists(f): continue
        seen.add(f)
        for n in ast.walk(ast.parse(open(f).read())):
            names = [a.name for a in n.names] if isinstance(n, ast.Import) else \
                    [n.module] + ["%s.%s" % (n.module, a.name) for a in n.names] if isinstance(n, ast.ImportFrom) and n.module else []
            for x in names:
                if x.startswith("specbridge"):
                    for g in (module_file(clone, x),):
                        if os.path.exists(g): todo.append(g)
    return seen


def affected(clone, cmd, changed):
    src = sources(clone, cmd); rel = {os.path.relpath(f, clone) for f in src}
    if rel & changed: return True
    text = "".join(open(f).read() for f in src)
    paths = set(re.findall(r"""["'](out/[\w./-]+?)["'%]""", text))
    return any(c.startswith(p.rstrip("/")) for c in changed if c.startswith("out/") for p in paths)


def main():
    clone, venv, msg = sys.argv[1:4]; full = "--full" in sys.argv; repo = os.getcwd(); log = []
    say = lambda s: (print(s, flush=True), log.append(s))
    c, o, t = sh("python -m specbridge.report.release", repo); say("release build exit %d in %.0f s" % (c, t))
    if c: print(o[-2000:]); sys.exit(1)
    # keep what `make reproduce` generated (untracked, git-ignored outputs): the steps not rerun read them
    _, keep, _ = sh("git ls-files --others --ignored --exclude-standard --directory", clone); kf = os.path.join(clone, ".git", "keep.txt")
    open(kf, "w").write("".join("/%s\n" % k for k in keep.split()))
    sh("rsync -a --delete --exclude .git --exclude dev_unzipped --exclude results --exclude ambrosia_data --exclude .venv --exclude-from %s release/ %s/" % (kf, clone), repo)
    sh("git add -A", clone); c, o, _ = sh("git diff --cached --name-only", clone); changed = set(o.split())
    if changed: sh("git commit -qm %s" % sp.list2cmdline([msg]), clone)
    else:
        _, ahead, _ = sh("git rev-list --count @{u}..HEAD", clone)
        if ahead.strip() == "0": say("artifact unchanged; nothing to push"); return
        _, o, _ = sh("git diff --name-only @{u} HEAD", clone); changed = set(o.split())   # an unpushed commit: test it
    env = dict(os.environ, PATH=venv + ":" + os.environ["PATH"])
    if full or changed & set(FULL_IF):
        c, o, t = sh("make all", clone, env); say("make all exit %d in %.0f s" % (c, t))
    else:
        run = [s for s in steps(clone) if "collect.py" not in s and affected(clone, s, changed)]
        say("changed files: %d; steps rerun: %d of %d" % (len(changed), len(run), len(steps(clone)) - 1))
        c = 0
        for s in run + ["python reproduce/collect.py"]:
            c1, o1, t = sh(s, clone, env); say("  %-70s exit %d, %.0f s" % (s[:70], c1, t)); c |= c1
            if c1: print(o1[-600:]); break
        if c:                                              # e.g. a generated input is missing: rebuild everything once
            c, o, t = sh("make all", clone, env); say("fallback: make all exit %d in %.0f s" % (c, t))
        else: c, o, t = sh("make check test", clone, env); say("make check test exit %d in %.0f s" % (c, t))
    ok = [l for l in o.splitlines() if re.search("ALL OUTPUTS REPRODUCED|DIFFERENCES|numbers found|reference queries checked|TABLE 5|ALLFOUND", l)]
    for l in ok: say("  " + l[:200])
    _, st, _ = sh("git status --short", clone); tracked = [l for l in st.splitlines() if not l.startswith("??")]
    t5 = any("TABLE 5 (AMBROSIA) MATCHES" in l for l in ok)
    say("tracked files changed: %d; Table 5 matches: %s" % (len(tracked), t5))
    if c == 0 and not tracked and t5:
        sh("git push -q origin HEAD", clone); _, h, _ = sh("git log --oneline -1", clone); say("artifact pushed: " + h.strip())
    else:
        say("ARTIFACT NOT PUSHED"); print("\n".join(tracked[:20])); sys.exit(1)


if __name__ == "__main__":
    main()
