"""Surgical rerun of the 75 flagged items (out/truncation/flags.json), each with its paired comparison arm; old files archived in
out/truncation/old/ (never deleted); raw model output saved in the new files. Marker: out/truncation/RERUN.done"""
import json, os, shutil
from specbridge.comm.transfer import ledger as LG, disclose as X, reqmethod as RM, rewrite as RW, ambrosia as AM
F = json.load(open("out/truncation/flags.json")); OLD = "out/truncation/old"
def arch(p):
    if os.path.exists(p): d = os.path.join(OLD, p); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.move(p, d)
for f in ("out/ambrosia/final/final.json", "out/reqmethod/results.json", "out/reqmethod/judge.json", "out/rewrite/RESULTS.md", "out/rewrite/bird/RESULTS.md"):
    if os.path.exists(f): d = os.path.join(OLD, f); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy(f, d)
# BIRD (b): whole item (c, b, d together)
for k in F["BIRD (b)"]: m, q = k.split("|"); arch("out/rewrite/bird/runs/%s/%s.json" % (m, q))
RW.run_bird(); print("BIRD done", flush=True)
# Sec 7.4 (b): whole reading (a, b, c, d together)
only = set(F["Sec 7.4 (b)"])
for k in only: m, c, x = k.split("|"); arch(RW._f(m, c, x))
RW.run(only=only); RW.run_d(); RW.report(); print("7.4 done", flush=True)
# Table 7 DtP + ours (paired), and their naming judgments
ks, WD = LG.sets(); J = json.load(open(RM.OUT + "/judge.json"))
for key in F["Table 7 DtP"]:
    m, base = key.split("|")
    for k in ks:
        for w in WD[k]:
            if os.path.basename(RM._f("dtp", m, k, w))[:-5] == base:
                for a in ("dtp", "ours"):
                    arch(RM._f(a, m, k, w))
                    if w == "open": J.pop("%s|%s|%s" % (k, m, a), None)
json.dump(J, open(RM.OUT + "/judge.json", "w"), indent=1)
RM.run(); print("Table 7 done", flush=True)
# AMBROSIA final DtP + ours (paired)
for key in F["AMBROSIA DtP"]:
    m, row = key.split("|")
    for a in ("dtp", "ours"): arch("%s/%s/%s/%s.json" % (AM.FINAL, a, m, row))
AM.run_final(); AM.report_final(); print("AMBROSIA done", flush=True)
open("out/truncation/RERUN.done", "w").write("done\n")
