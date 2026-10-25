"""Resume of truncation_rerun after it was killed during the Table 7 stage (2026-10-14 10:22): Table 7 files are already archived."""
import json, os, shutil
from specbridge.comm.transfer import reqmethod as RM, ambrosia as AM
F = json.load(open("out/truncation/flags.json")); OLD = "out/truncation/old"
def arch(p):
    if os.path.exists(p): d = os.path.join(OLD, p); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.move(p, d)
RM.run(); print("Table 7 done", flush=True)
for key in F["AMBROSIA DtP"]:
    m, row = key.split("|")
    for a in ("dtp", "ours"): arch("%s/%s/%s/%s.json" % (AM.FINAL, a, m, row))
AM.run_final(); AM.report_final(); print("AMBROSIA done", flush=True)
open("out/truncation/RERUN.done", "w").write("done\n")
