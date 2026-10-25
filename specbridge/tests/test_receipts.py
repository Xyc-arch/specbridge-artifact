"""P's receipts on its source (LiveSQL): the round trip is identical on every program, and exactly the declared 13 decisions
fall outside the language (docs/LANGUAGE.md §1, by rule)."""
import sys, warnings
warnings.filterwarnings("ignore")
EXPECTED_OUTSIDE = 13


def run():
    from specbridge.pd.structures.actions import fit, rebuild, sequence
    from specbridge.pd.structures.sources import programs, typers
    R, T = programs("livesql"), typers("livesql"); law = fit(R, T)
    same, outside = 0, []
    for i, p in enumerate(R):
        s = sequence(p, T[i]); p2, out = rebuild(s, law.caps); outside += out
        same += sequence(p2, lets=True) == s
    fails = []
    for name, ok in (("round trip identical on all %d source programs (%d)" % (len(R), same), same == len(R)),
                     ("source decisions outside the language: %d (declared %d)" % (len(outside), EXPECTED_OUTSIDE), len(outside) == EXPECTED_OUTSIDE)):
        print("  %-100s %s" % (name, "ok" if ok else "FAILED"))
        if not ok: fails.append(name)
    print("%d failed" % len(fails)); return fails


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
