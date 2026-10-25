"""WRONG ALTERNATIVES PER EXTRA READING (2026-10-14), from the saved AMBROSIA final-test runs (after the truncation rerun), scored
exactly as ambrosia.report_final (identical results merged, shape-tolerant). Per model and arm: on unambiguous questions the mean number
of returned queries and of wrong ones (not returning the single correct result); on ambiguous questions the mean number of readings
found. For ambiguity rates r: per 100 questions, extra readings DtP finds vs ours = 100 r (f_dtp - f_ours), extra wrong alternatives
DtP shows vs ours = 100 (1 - r) (w_dtp - w_ours), their ratio, and the break-even rate r* where the two are equal. Bootstrap over
questions (ambiguous and unambiguous resampled separately). Also three unambiguous questions with a plausible wrong DtP query.
    python -m specbridge.comm.transfer.exchange   -> out/ambrosia/final/EXCHANGE.md (+ .json; examples stay local)"""
import json, random
from specbridge.comm.common import grade as G
from specbridge.comm.transfer import ambrosia as AM

MODELS = ("sonnet", "gpt-6-sol"); ARMS = ("plain", "samplek", "dtp", "ours"); RATES = (0.1, 0.2, 0.3, 0.5); B = 2000; SEED = 20261027


def score():
    R = AM.final_rows(); S = {}
    for m in MODELS:
        for r in R:
            for a in ARMS:
                f = AM._ff(a, m, r["row"])
                try: qs = json.load(open(f))["queries"]
                except FileNotFoundError: continue
                db = r["db_file"]; P_ = [(q, x) for q, x in ((q, AM._ex_sql(db, q)) for q in set(AM._dedup(db, qs))) if x is not None]
                gs = [AM._ex_sql(db, g) for g in r["gold"]]
                ok = lambda g, p: g is not None and G.shape_tolerant([list(y) for y in g], [list(y) for y in p])
                S[(m, a, r["row"])] = {"amb": r["ambiguous"], "n": len(P_), "found": sum(any(ok(g, p) for _q, p in P_) for g in gs),
                                       "wrong": sum(not any(ok(g, p) for g in gs) for _q, p in P_), "wrong_q": [(q, p) for q, p in P_ if not any(ok(g, p) for g in gs)], "row": r}
    return S


def main():
    S = score(); out = {"models": {}}; L = ["# Wrong alternatives per extra reading on AMBROSIA (`specbridge.comm.transfer.exchange`)\n",
        "Final test after the truncation rerun; scoring as the final report (identical results merged, shape-tolerant). Wrong = a returned query that does not return the single correct result of an unambiguous question.\n",
        "| model | arm | unambiguous: queries per question | wrong per question | ambiguous: readings found per question |", "|---|---|---|---|---|"]
    rows = {m: sorted({k[2] for k in S if k[0] == m and all((m, a, k[2]) in S for a in ARMS)}) for m in MODELS}
    for m in MODELS:
        U = [x for x in rows[m] if not S[(m, "ours", x)]["amb"]]; A = [x for x in rows[m] if S[(m, "ours", x)]["amb"]]
        for a in ARMS:
            L.append("| %s | %s | %.2f | %.2f | %.2f |" % (m, a, sum(S[(m, a, x)]["n"] for x in U) / len(U), sum(S[(m, a, x)]["wrong"] for x in U) / len(U), sum(S[(m, a, x)]["found"] for x in A) / len(A)))
    def deltas(pairs_u, pairs_a):
        dw = sum(S[(m, "dtp", x)]["wrong"] - S[(m, "ours", x)]["wrong"] for m, x in pairs_u) / len(pairs_u)
        df = sum(S[(m, "dtp", x)]["found"] - S[(m, "ours", x)]["found"] for m, x in pairs_a) / len(pairs_a); return dw, df
    def table(name, pu, pa):
        dw, df = deltas(pu, pa); rng = random.Random(SEED); bs = []
        for _ in range(B): bs.append(deltas([pu[rng.randrange(len(pu))] for _ in pu], [pa[rng.randrange(len(pa))] for _ in pa]))
        ci = lambda v: (sorted(v)[int(.025 * B)], sorted(v)[int(.975 * B) - 1])
        L.extend(["", "## %s: DtP minus ours (%d unambiguous, %d ambiguous questions)\n" % (name, len(pu), len(pa)),
                  "Per question: wrong alternatives %+.2f [%.2f, %.2f]; readings found %+.2f [%.2f, %.2f]." % (dw, *ci([b[0] for b in bs]), df, *ci([b[1] for b in bs])), "",
                  "| ambiguity rate | extra readings DtP finds per 100 questions | extra wrong alternatives DtP shows per 100 | wrong alternatives per extra reading [95%] |", "|---|---|---|---|"])
        res = {"dw": dw, "df": df, "rates": {}}
        for r in RATES:
            er, ew = 100 * r * df, 100 * (1 - r) * dw; rat = sorted(100 * (1 - r) * b[0] / (100 * r * b[1]) for b in bs if b[1] > 0)
            civ = "[%.1f, %.1f]" % (rat[int(.025 * len(rat))], rat[int(.975 * len(rat)) - 1]) if er > 0 and len(rat) > 20 else ""
            note = "" if len(rat) == B else " (DtP finds no extra reading in %d%% of resamples)" % round(100 * (B - len(rat)) / B)
            L.append("| %d%% | %.1f | %.1f | %s %s%s |" % (100 * r, er, ew, "%.1f" % (ew / er) if er > 0 else "undefined: DtP finds no extra readings", civ, note if er > 0 else ""))
            res["rates"][r] = {"extra_readings": er, "extra_wrong": ew, "ratio": ew / er if er > 0 else None}
        be = dw / (dw + df) if dw > 0 and df > 0 else None; bes = [b[0] / (b[0] + b[1]) for b in bs if b[0] > 0 and b[1] > 0]
        L.append("\nBreak-even ambiguity rate (one wrong alternative per extra reading): %s%s." % ("%.0f%%" % (100 * be) if be is not None else "none (DtP does not find more readings)",
                 " [%.0f%%, %.0f%%] over resamples where DtP finds more readings" % (100 * sorted(bes)[int(.025 * len(bes))], 100 * sorted(bes)[int(.975 * len(bes)) - 1]) if be is not None and len(bes) > 20 else ""))
        res["break_even"] = be; out["models"][name] = res
    for m in MODELS:
        table(m, [(m, x) for x in rows[m] if not S[(m, "ours", x)]["amb"]], [(m, x) for x in rows[m] if S[(m, "ours", x)]["amb"]])
    table("pooled", [(m, x) for m in MODELS for x in rows[m] if not S[(m, "ours", x)]["amb"]], [(m, x) for m in MODELS for x in rows[m] if S[(m, "ours", x)]["amb"]])
    ex = []
    for (m, a, x), v in sorted(S.items(), key=lambda kv: str(kv[0])):
        if a != "dtp" or v["amb"] or not v["wrong_q"]: continue
        for q, p in v["wrong_q"]:
            if p and any(c is not None for row_ in p for c in row_) and len(p) <= 50:
                r = v["row"]; g = AM._ex_sql(r["db_file"], r["gold"][0]); ex.append({"model": m, "row": x, "question": r["question"], "gold_sql": r["gold"][0], "gold_rows": str(g[:4]), "dtp_sql": q, "dtp_rows": str(p[:4])}); break
        if len(ex) >= 3: break
    json.dump(out, open(AM.FINAL + "/exchange.json", "w"), indent=1); json.dump(ex, open(AM.FINAL + "/exchange_examples.json", "w"), indent=1)
    open(AM.FINAL + "/EXCHANGE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
    for e in ex: print("\n--", e["model"], e["row"], "|", e["question"]); print("  gold:", e["gold_sql"][:250], "->", e["gold_rows"][:150]); print("  DtP :", e["dtp_sql"][:250], "->", e["dtp_rows"][:150])


if __name__ == "__main__":
    main()
