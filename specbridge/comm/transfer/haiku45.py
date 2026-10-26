"""ONE HAIKU (2026-10-26). The short name "haiku" was resolved by the Claude CLI to claude-haiku-4-5-20251001 up to 2026-10-03 and
to claude-haiku-5-5 from 2026-10-11 (CLI session logs; no Haiku call in between), so the paper's Haiku numbers mixed two models.
specbridge.pd.ask now pins claude-haiku-4-5-20251001. This moves every Haiku answer written from 2026-10-11 on (and the judge and
classification entries of those answers) to out/archive/haiku-5-5/<same path>, never deleting, then asks Haiku 4.5 again for exactly
those answers, with each run's own code, and rebuilds the judges and reports.
    python -m specbridge.comm.transfer.haiku45 archive          -> out/archive/haiku-5-5/MANIFEST.json
    python -m specbridge.comm.transfer.haiku45 answer <group>    (wave 1: disclose plain eval sqlite; wave 2: matched topk rescore rewrite swap ambrosia)
    python -m specbridge.comm.transfer.haiku45 finish            judges, classification, reports
At most 6 workers per process."""
import datetime, glob, json, os, shutil, sys

SWITCH = datetime.datetime(2026, 10, 11).timestamp()
A = "out/archive/haiku-5-5"; R = "out/transfer/all/render"; S = R + "/disclose_sqlite"
DIRS = [R + "/disclose/haiku", R + "/disclose/plain/haiku", R + "/disclose/complement/haiku", R + "/disclose/topk/haiku",
        R + "/eval/runs/haiku_b1", S + "/haiku", S + "/plain/haiku", S + "/complement/haiku", S + "/topk/haiku",
        "out/rescore/runs/haiku", "out/rewrite/runs/haiku", "out/writer_swap/calib200/solver/haiku",
        "out/ambrosia/plain/haiku", "out/ambrosia/specific/haiku"]
JUDGES = [R + "/disclose/judge.json", R + "/disclose/judge_alternatives.json", S + "/judge.json", S + "/judge_alternatives.json"]


def archive(dry=False):
    if dry:
        for d in DIRS: print(sum(os.path.getmtime(f) >= SWITCH for f in glob.glob(d + "/*.json")), "of", len(glob.glob(d + "/*.json")), d)
        return
    moved = []
    for d in DIRS:
        for f in sorted(glob.glob(d + "/*.json")):
            if os.path.getmtime(f) < SWITCH: continue                        # a Haiku 4.5 answer: kept in place
            o = json.load(open(f)); dst = os.path.join(A, f); os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(f, dst); moved.append({"path": f, "case": o.get("case") or o.get("key", "").rsplit("|", 1)[0] or o.get("id"),
                                               "wording": o.get("wording") or (o.get("key", "|").rsplit("|", 1)[1] if "key" in o else None),
                                               "reading": o.get("reading")})
    # judge entries of moved answers: "case|wording|haiku" and "case|wording|haiku|i"
    gone = {(m["case"], m["wording"]) for m in moved if m["wording"]}
    jout = {}
    for jf in JUDGES:
        if not os.path.exists(jf): continue
        J = json.load(open(jf)); keep, drop = {}, {}
        for k, v in J.items():
            p = k.split("|")
            (drop if len(p) >= 3 and p[2] == "haiku" and (p[0], p[1]) in gone else keep)[k] = v
        dst = os.path.join(A, jf); os.makedirs(os.path.dirname(dst), exist_ok=True); json.dump(drop, open(dst, "w"), indent=1)
        json.dump(keep, open(jf, "w"), indent=1); jout[jf] = len(drop)
    cf_ = "out/rewrite/classify.json"; J = json.load(open(cf_))
    rw = {(m["case"], m["reading"]) for m in moved if m["path"].startswith("out/rewrite/")}
    drop = {k: v for k, v in J.items() if k.split("|")[0] == "haiku" and (k.split("|")[1], k.split("|")[2]) in rw}
    os.makedirs(os.path.join(A, "out/rewrite"), exist_ok=True); json.dump(drop, open(os.path.join(A, cf_), "w"), indent=1)
    json.dump({k: v for k, v in J.items() if k not in drop}, open(cf_, "w"), indent=1); jout[cf_] = len(drop)
    man = {"reason": __doc__.split("\n")[0], "switch": "2026-10-11", "moved": moved, "judge_entries_moved": jout,
           "by_dir": {d: sum(m["path"].startswith(d + "/") for m in moved) for d in DIRS}}
    json.dump(man, open(A + "/MANIFEST.json", "w"), indent=1); print(json.dumps(man["by_dir"], indent=1), jout)


def answer(group):
    H = ["haiku"]
    if group == "disclose":
        from specbridge.comm.transfer import disclose as X; X.run(R, H, 6)
    elif group == "plain":
        from specbridge.comm.transfer import disclose as X; X.plain(R, H, 6)
    elif group == "eval":
        os.environ["TRANSFER_WORKERS"] = "6"; os.system("python -m specbridge.comm.transfer.evaluate %s run haiku" % R)
    elif group == "sqlite":
        from specbridge.comm.transfer import dialect_rerun as DR; DR.MODELS[:] = H
        for st in DR.STAGES[:4]: DR.run(st, 6)
    elif group == "matched":
        from specbridge.comm.transfer import matched as MT; MT.run(H, 6)
    elif group == "topk":
        from specbridge.comm.transfer import topk as TK; TK.run(H, 6)
    elif group == "rescore":
        from specbridge.comm.transfer import rescore as RS; RS.run(H, 6); RS.report()
    elif group == "rewrite":
        from specbridge.comm.transfer import rewrite as RW
        M = json.load(open(A + "/MANIFEST.json"))["moved"]
        RW.run(6, only={"haiku|%s|%s" % (m["case"], m["reading"]) for m in M if m["path"].startswith("out/rewrite/")})
    elif group == "swap":
        from specbridge.comm.construct import writer_swap as WS; WS.SOLVERS[:] = H; WS.solve(6)
    elif group == "ambrosia":
        from specbridge.comm.transfer import ambrosia as AM; AM.decomp_run(H, "dev", 6); AM.decomp_run(H, "conf", 6)
    open("%s/%s.done" % (A, group), "w").write("ok\n")


def finish():
    from specbridge.comm.transfer import disclose as X, matched as MT, topk as TK, rewrite as RW, ambrosia as AM, dialect_rerun as DR
    from specbridge.comm.construct import writer_swap as WS
    X.judge(R, 6, scope="all"); X.judge_alternatives(R, 6)
    DR.run("judge", 6); DR.run("judge_alternatives", 6)
    RW.classify()
    MT.report(); TK.report(); RW.report(); WS.report(); AM.decomp_report("dev"); AM.decomp_report("conf")
    open(A + "/finish.done", "w").write("ok\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"archive": lambda: archive("--dry" in a), "answer": lambda: answer(a[1]), "finish": finish}[a[0]]()
