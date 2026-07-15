"""Phase 4: leakage detection under misspecified known-factor residualization.

Detector (frozen): D_j = R^2 of the residual factor's return series on the ESTIMATED
known-factor return series f_hat_F = Bt' Y; flag leaked iff F-test p < 0.01.
Ground truth: L_j = ||Proj_col(B_F) h_j||^2; leaked if > 0.5, genuine if < 0.2.
Pipeline: C4 trust screen first, then floor + leakage flag on trusted factors.
Prereg: FLOOR_RESIDUAL_MEMO.md Phase 4. Seed=2, held-out cells (350,90),(750,50).
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

K_F, SNR_F = 4, [40.0, 30.0, 22.0, 16.0]
SNR_R = [3.0, 1.5, 0.8, 0.4, 0.15]
KP = 5                                                    # k' extracted
DELTA2, N_MC, SEED = 1.0, 200, 2
CELLS = [(500, 63), (350, 90), (750, 50)]                 # main + 2 held-out
HELD_OUT = {(350, 90), (750, 50)}
ALPHA, L_HI, L_LO = 0.01, 0.5, 0.2


def edge_cut(p, n):
    return 2 * np.sqrt(n / p) + n / p + 0.5               # C4, frozen (Phase 3)


def draw(p, n, mis, with_R, rng):
    uF = ortho(p, K_F, rng)
    BF = uF * np.sqrt(np.array(SNR_F) * p * DELTA2 / n)
    Y = BF @ rng.standard_normal((K_F, n)) + rng.standard_normal((p, n)) * np.sqrt(DELTA2)
    Sig0 = BF @ BF.T
    if with_R:
        uR = ortho(p, len(SNR_R), rng)
        BR = uR * np.sqrt(np.array(SNR_R) * p * DELTA2 / n)
        Y = Y + BR @ rng.standard_normal((len(SNR_R), n))
        Sig0 = Sig0 + BR @ BR.T
    Bt = uF if mis == 0 else np.linalg.qr(uF + mis * rng.standard_normal((p, K_F)))[0][:, :K_F]
    fhat = Bt.T @ Y                                       # estimated factor returns (k_F x n)
    Yr = Y - Bt @ fhat
    MS = Sig0 - Bt @ (Bt.T @ Sig0)
    Sig_res = MS - (MS @ Bt) @ Bt.T                       # actual residual signal cov
    W = Yr.T @ Yr / (n * p)
    w, V = np.linalg.eigh(W)
    w, V = w[::-1], V[:, ::-1]
    theta, ell = w[:KP], w[KP:].mean()
    H = Yr @ V[:, :KP] / np.sqrt(n * p * theta)
    ww, VV = np.linalg.eigh(Sig_res)
    Bsig = VV[:, ::-1][:, :KP]
    a = np.clip(1.0 - np.einsum("pi,pi->i", Bsig @ (Bsig.T @ H), H), 0, 1)
    L = np.einsum("ki->i", (uF.T @ H) ** 2)               # true leakage magnitude
    X = H.T @ Yr                                          # factor return series (KP x n)
    Pf = fhat.T @ np.linalg.solve(fhat @ fhat.T, fhat)    # projector onto rowspace(fhat)
    r2 = np.einsum("jn,jn->j", X @ Pf, X) / np.einsum("jn,jn->j", X, X)
    F = (r2 / K_F) / ((1 - r2) / (n - K_F))
    pval = stats.f.sf(F, K_F, n - K_F)
    return {"floor": ell / theta, "a": a, "snrhat": theta / ell - 1.0,
            "L": L, "D": r2, "leak_flag": pval < ALPHA}


def run_arm(p, n, mis, with_R, rng):
    out = {k: [] for k in ("floor", "a", "snrhat", "L", "D", "leak_flag")}
    for _ in range(N_MC):
        d = draw(p, n, mis, with_R, rng)
        for k in out:
            out[k].append(d[k])
    return {k: np.concatenate(v) for k, v in out.items()}


def auc(score, label):
    pos, neg = score[label], score[~label]
    if not len(pos) or not len(neg):
        return float("nan")
    return float(np.mean(pos[:, None] > neg[None, :]) + 0.5 * np.mean(pos[:, None] == neg[None, :]))


def main():
    rng = np.random.default_rng(SEED)
    lines = ["# Phase 4 — leakage detection under misspecified residualization", "",
             "Detector D_j = R² of residual-factor returns on estimated known-factor returns; "
             f"flag leaked iff F-test p < {ALPHA}. C4 screen applied first. "
             "Prereg: FLOOR_RESIDUAL_MEMO.md Phase 4.", "",
             "| cell | arm | med D (genuine) | med D (leaked) | trap rate | AUC | FPR | FNR |",
             "|---|---|---|---|---|---|---|---|"]
    ho_auc, ho_fpr, ho_fnr = [], [], []
    for p, n in CELLS:
        arms = {"A1 oracle": run_arm(p, n, 0.0, True, rng),
                "NEG": run_arm(p, n, 0.0, False, rng),
                "LEAK": run_arm(p, n, 0.5, False, rng),
                "MIXED": run_arm(p, n, 0.5, True, rng)}
        for name, r in arms.items():
            trusted = r["snrhat"] > edge_cut(p, n)
            gen = trusted & (r["L"] < L_LO)
            lk = trusted & (r["L"] > L_HI)
            trap = float(np.mean(r["floor"][lk] < 0.3)) if lk.any() else float("nan")
            a_val = auc(r["D"][gen | lk], r["L"][gen | lk] > L_HI) if (gen.any() and lk.any()) else float("nan")
            fpr = float(r["leak_flag"][gen].mean()) if gen.any() else float("nan")
            fnr = float((~r["leak_flag"][lk]).mean()) if lk.any() else float("nan")
            dg = float(np.median(r["D"][gen])) if gen.any() else float("nan")
            dl = float(np.median(r["D"][lk])) if lk.any() else float("nan")
            lines.append(f"| {p},{n} | {name} | {dg:.3f} | {dl:.3f} | {trap:.0%} "
                         f"| {a_val:.3f} | {fpr:.2f} | {fnr:.2f} |")
            if name == "MIXED" and (p, n) in HELD_OUT:
                ho_auc.append(a_val); ho_fpr.append(fpr); ho_fnr.append(fnr)

    A, FP, FN = min(ho_auc), max(ho_fpr), max(ho_fnr)
    if A >= 0.9 and FP <= 0.10 and FN <= 0.10:
        verdict = "SUCCESS — leakage is detectable from observables"
    elif A < 0.7 or FP > 0.25 or FN > 0.25:
        verdict = "FAIL — the time-series detector does not separate leaked from genuine"
    else:
        verdict = "AMBIGUOUS"
    lines += ["", f"## Decision (pre-committed, MIXED arm, held-out cells): **{verdict}**",
              f"- held-out worst: AUC {A:.3f} | FPR {FP:.2f} | FNR {FN:.2f} "
              f"(bars: ≥0.9, ≤0.10, ≤0.10)", ""]
    lines += ["## Story (mechanism diagnosis, no tuning)", "",
              "- See FLOOR_LEAKAGE.md story section (appended post-run per prereg: "
              "diagnose, don't tune).", ""]
    out = HERE / "FLOOR_LEAKAGE.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    stamp_run(track="estimator_lab", variant="floor_leakage",
              params={"alpha": ALPHA, "cells": CELLS, "seed": SEED, "mis": 0.5,
                      "verdict": verdict.split(" — ")[0], "memo": "FLOOR_RESIDUAL_MEMO.md#phase4"},
              n_trials=1)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
