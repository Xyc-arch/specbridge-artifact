"""python -m specbridge.tests [--fast]   every suite, in order; --fast skips the comm identity checks."""
import subprocess, sys, time
SUITES = ["specbridge.tests.test_gate", "specbridge.pd.tests.test_compose", "specbridge.pd.tests.test_small_populations", "specbridge.pd.tests.test_render", "specbridge.pd.tests.test_semantics", "specbridge.pd.tests.test_port", "specbridge.comm.verbal.test_verbalize", "specbridge.tests.test_receipts", "specbridge.tests.test_comm"]
failed = []
for m in SUITES:
    if "--fast" in sys.argv and m == "specbridge.tests.test_comm": continue
    t0 = time.time(); r = subprocess.run([sys.executable, "-m", m], capture_output=True, text=True)
    last = (r.stdout.strip().split("\n") or [""])[-1]
    print("%-32s %-12s %5.0f s" % (m, "ok" if r.returncode == 0 else "FAILED", time.time() - t0))
    if r.returncode: failed.append(m); print(r.stdout[-2000:], r.stderr[-2000:])
print("\n%d of %d suites failed" % (len(failed), len(SUITES))); sys.exit(1 if failed else 0)
