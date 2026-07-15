"""Phase 5: split-sample leakage detector (mechanism adjudication).

Half 1: residual PCA (h_j, floor, C4). Half 2: x_j = h_j'Yr regressed on f_hat = Bt'Y,
F-test q=K_F, n2 obs, alpha=0.01. Fresh seed=3. Prereg: FLOOR_RESIDUAL_MEMO.md Phase 5.
"""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
from core.eval.run_manifest import stamp_run              # noqa: E402
from run_floor_calibration import ortho                   # noqa: E402
from run_floor_leakage import (ALPHA, CELLS, HELD_OUT, K_F, KP, L_HI, L_LO,  # noqa: E402
                               SNR_F, SNR_R, DELTA2, N_MC, auc, edge_cut)

SEED = 3


def draw_split(p, n, mis, with_R, rng):
    uF = ortho(p, K_F, rng)
    BF = uF * np.sqrt(np.array(SNR_F) * p * DELTA2 / n)
    Y = BF @ rng.standard_normal((K_F, n)) + rng.standard_normal((p, n)) * np.sqrt(DELTA2)
    if with_R:
        uR = ortho(p, len(SNR_R), rng)
        BR = uR * np.sqrt(np.array(SNR_R) * p * DELTA2 / n)
        Y = Y + BR @ rng.standard_normal((len(SNR_R), n))
    Bt = uF if mis == 0 else np.linalg.qr(uF + mis * rng.standard_normal((p, K_F)))[0][:, :K_F]
    Yr = Y - Bt @ (Bt.T @ Y)
    n1 = n // 2
    Y1, Y2 = Yr[:, :n1], Yr[:, n1:]
    W = Y1.T @ Y1 / (n1 * p)
    w, V = np.linalg.eigh(W)
    w, V = w[::-1], V[:, ::-1]
    theta, ell = w[:KP], w[KP:].mean()
    H = Y1 @ V[:, :KP] / np.sqrt(n1 * p * theta)
    L = np.einsum("ki->i", (uF.T @ H) ** 2)
    X = H.T @ Y2                                          # half-2 factor returns
    fhat2 = Bt.T @ Y[:, n1:]
    Pf = fhat2.T @ np.linalg.solve(fhat2 @ fhat2.T, fhat2)
    r2 = np.einsum("jn,jn->j", X @ Pf, X) / np.einsum("jn,jn->j", X, X)
    n2 = n - n1
    F = (r2 / K_F) / ((1 - r2) / (n2 - K_F))
    return {"snrhat": theta / ell - 1.0, "L": L, "D": r2,
            "leak_flag": stats.f.sf(F, K_F, n2 - K_F) < ALPHA, "n1": n1}


def main():
    rng = np.random.default_rng(SEED)
    lines = ["# Phase 5 — split-sample leakage detector", "",
             "Half-1 PCA/screen, half-2 F-test. Prereg: FLOOR_RESIDUAL_MEMO.md Phase 5.", "",
             "| cell | arm | med D gen | med D leak | AUC | FPR | FNR |",
             "|---|---|---|---|---|---|---|"]
    ho = {"auc": [], "fpr": [], "fnr": []}
    for p, n in CELLS:
        for name, (mis, wr) in {"A1 oracle": (0.0, True), "LEAK": (0.5, False),
                                "MIXED": (0.5, True)}.items():
            out = {k: [] for k in ("snrhat", "L", "D", "leak_flag")}
            for _ in range(N_MC):
                d = draw_split(p, n, mis, wr, rng)
                for k in out:
                    out[k].append(d[k])
            r = {k: np.concatenate(v) for k, v in out.items()}
            cut = edge_cut(p, n // 2)                     # screen on half-1 stats
            trusted = r["snrhat"] > cut
            gen, lk = trusted & (r["L"] < L_LO), trusted & (r["L"] > L_HI)
            a_val = auc(r["D"][gen | lk], r["L"][gen | lk] > L_HI) if (gen.any() and lk.any()) else float("nan")
            fpr = float(r["leak_flag"][gen].mean()) if gen.any() else float("nan")
            fnr = float((~r["leak_flag"][lk]).mean()) if lk.any() else float("nan")
            dg = float(np.median(r["D"][gen])) if gen.any() else float("nan")
            dl = float(np.median(r["D"][lk])) if lk.any() else float("nan")
            lines.append(f"| {p},{n} | {name} | {dg:.3f} | {dl:.3f} | {a_val:.3f} | {fpr:.2f} | {fnr:.2f} |")
            if name == "MIXED" and (p, n) in HELD_OUT:
                ho["auc"].append(a_val); ho["fpr"].append(fpr); ho["fnr"].append(fnr)

    A, FP, FN = min(ho["auc"]), max(ho["fpr"]), max(ho["fnr"])
    if FP <= 0.10 and FN <= 0.10 and A >= 0.9:
        verdict = ("SUCCESS — split-sample detector clean; Phase-4 shared-noise/overfit "
                   "mechanism CONFIRMED; pipeline complete → real FF-residualized S&P next")
    elif FN > 0.25:
        verdict = "FAIL — split cost too high (FNR)"
    elif FP > 0.10:
        verdict = ("AMBIGUOUS/ADJUDICATED — FPR persists ⇒ mechanism is PARTIAL MIXING "
                   "(labels, not detector); leakage is a continuum")
    else:
        verdict = "AMBIGUOUS"
    lines += ["", f"## Decision (pre-committed): **{verdict}**",
              f"- held-out worst: AUC {A:.3f} | FPR {FP:.2f} | FNR {FN:.2f} (bars ≥0.9, ≤0.10, ≤0.10)", ""]
    out_f = HERE / "FLOOR_SPLIT.md"
    out_f.write_text("\n".join(lines))
    print("\n".join(lines))
    stamp_run(track="estimator_lab", variant="floor_split",
              params={"seed": SEED, "alpha": ALPHA, "cells": CELLS,
                      "verdict": verdict.split(" — ")[0], "memo": "FLOOR_RESIDUAL_MEMO.md#phase5"},
              n_trials=1)
    print(f"wrote {out_f}")


if __name__ == "__main__":
    main()
