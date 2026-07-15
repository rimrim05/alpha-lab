"""Phase 6: real FF-residualized S&P — descriptive floor + leakage-score prototype.

Frozen prereg: FLOOR_REALDATA_MEMO.md (Part B). Per 63-return-day window:
PIT universe + screens -> vol-standardize by beta-window vol -> trailing-252d FF3+MOM
betas (intercept) -> cross-sectional residualization off col(Bhat) -> dual-space PCA
(k'=5, sim conventions) -> C4 screen -> floor (+n/(2p) IFF realized p/n >= 7) ->
D_j vs published FF (primary) and vs Bhat-implied factor returns (secondary), bucketed
by the window's circular-shift empirical null (material >= q99, low < q75).
Controls: positive (no residualization, PC1 C4 + R2 vs Mkt-RF >= 0.7); negative
(per-asset independent time permutation, screen-pass <= 10% of primary slots).
Descriptive only — no oracle truth, no genuine/leaked claims, no portfolio claims.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
from core.eval.run_manifest import stamp_run  # noqa: E402

ROOT = HERE.parents[1]
N_AN, N_BETA, KP, K_F = 63, 252, 5, 4
Q_HI, Q_LO = 0.99, 0.75          # null-quantile bucket boundaries (frozen)
COV_MIN = 0.90
ZERO_MAX = 0.20                  # max fraction of zero-return days
SEED = 0                         # negative-control permutations only
FACTORS = ["Mkt-RF", "SMB", "HML", "Mom"]
INPUTS = ["data/raw/daily_px_statarb_wide.parquet", "data/raw/ff_factors_daily.parquet",
          "data/raw/sp500_pit.parquet"]


def edge_cut(p, n):
    return 2 * np.sqrt(n / p) + n / p + 0.5               # C4, frozen (Phase 3)


def pca(Y):
    """Sim conventions. Y: p x n. Returns theta, ell, snrhat, floor_raw, X (KP x n)."""
    p, n = Y.shape
    W = Y.T @ Y / (n * p)
    w, V = np.linalg.eigh(W)
    w, V = w[::-1], V[:, ::-1]
    theta, ell = w[:KP], w[KP:].mean()
    X = (Y @ V[:, :KP] / np.sqrt(n * p * theta)).T @ Y
    return theta, ell, theta / ell - 1.0, ell / theta, X


def r2_centered(X, F):
    """Centered R2 of each row of X (KP x n) on columns of F (n x q), with intercept."""
    Xc = X - X.mean(axis=1, keepdims=True)
    Fc = (F - F.mean(axis=0)).T                           # q x n
    P = Fc.T @ np.linalg.solve(Fc @ Fc.T, Fc)
    return np.einsum("jn,jn->j", Xc @ P, Xc) / np.einsum("jn,jn->j", Xc, Xc)


def shift_null(X, F):
    """Circular-shift null: R2 of every nontrivial shift of each factor series."""
    n = X.shape[1]
    vals = [r2_centered(np.roll(X, s, axis=1), F) for s in range(1, n)]
    return np.concatenate(vals)


def principal_angles(Q1, Q2):
    s = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    return np.degrees(np.arccos(np.clip(s, -1, 1)))


def main():
    rng = np.random.default_rng(SEED)
    px = pd.read_parquet(ROOT / INPUTS[0])
    px.index = pd.to_datetime(px.index)
    ff = pd.read_parquet(ROOT / INPUTS[1])
    pit = pd.read_parquet(ROOT / INPUTS[2])
    ret = px.pct_change(fill_method=None).iloc[1:]
    dates = ret.index.intersection(ff.index)
    ret, ff = ret.loc[dates], ff.loc[dates]

    # non-overlapping windows of N_BETA + N_AN return days, stepping back from the end
    bounds, end = [], len(dates)
    while end - N_AN - N_BETA >= 0:
        bounds.append((end - N_AN - N_BETA, end - N_AN, end))
        end -= N_AN
    bounds = bounds[::-1]

    rows, ctrl, neg_pass, neg_total, prev_Q, prev_names = [], {}, 0, 0, None, None
    for wi, (b0, a0, a1) in enumerate(bounds):
        d0 = dates[a0].date()
        snap = pit[pit.date <= dates[a0]].iloc[-1]
        members = [m for m in snap.members if m in ret.columns]
        blk = ret.iloc[b0:a1][members]
        bwin, awin = blk.iloc[:N_BETA], blk.iloc[N_BETA:]
        ok_b = bwin.notna().all() & (bwin.std() > 0) & ((bwin == 0).mean() <= ZERO_MAX)
        ok_a = awin.notna().all() & (awin.std() > 0) & ((awin == 0).mean() <= ZERO_MAX)
        names = list(blk.columns[ok_b & ok_a])
        drop_b, drop_a = int((~ok_b).sum()), int((ok_b & ~ok_a).sum())
        p, n = len(names), N_AN
        cov = p / len(snap.members)
        f = ff.iloc[b0:a1]
        rex = blk[names].sub(f["RF"], axis=0)
        # vol-standardize by beta-window vol (pre-analysis info only)
        vol = rex.iloc[:N_BETA].std()
        rex = rex / vol
        fb, fa = f.iloc[:N_BETA][FACTORS].values, f.iloc[N_BETA:][FACTORS].values
        Xb = np.column_stack([np.ones(N_BETA), fb])
        coef, *_ = np.linalg.lstsq(Xb, rex.iloc[:N_BETA].values, rcond=None)
        B = coef[1:].T                                    # p x K_F
        Q, _ = np.linalg.qr(B)
        # common-universe principal angles (restrict both B's to shared names)
        ang = np.nan
        if prev_Q is not None:
            common = [m for m in names if m in prev_names]
            i_prev = [prev_names.index(m) for m in common]
            i_cur = [names.index(m) for m in common]
            q1, _ = np.linalg.qr(prev_B[i_prev])
            q2, _ = np.linalg.qr(B[i_cur])
            ang = float(np.median(principal_angles(q1, q2)))
        prev_Q, prev_B, prev_names = Q, B, names

        Ya = rex.iloc[N_BETA:].values.T                   # p x n
        Yr = Ya - Q @ (Q.T @ Ya)
        theta, ell, snrhat, floor_raw, X = pca(Yr)
        trusted = snrhat > edge_cut(p, n)
        pn_ok = p / n >= 7
        floor_rep = floor_raw + (0.5 * n / p if pn_ok else 0.0)
        D = r2_centered(X, fa)
        fhat = (rex.iloc[N_BETA:].values @ B) @ np.linalg.inv(B.T @ B)  # n x K_F
        D2 = r2_centered(X, fhat)
        Fstat = (D / K_F) / ((1 - D) / (n - 1 - K_F))
        pval = stats.f.sf(Fstat, K_F, n - 1 - K_F)
        null = shift_null(X, fa)
        q_hi, q_lo = np.quantile(null, Q_HI), np.quantile(null, Q_LO)
        primary = cov >= COV_MIN
        for j in range(KP):
            if not trusted[j]:
                b = "noise-like"
            elif D[j] >= q_hi:
                b = "material-known-assoc"
            elif D[j] < q_lo:
                b = "low-known-assoc"
            else:
                b = "mixed"
            rows.append({"window": str(d0), "pc": j + 1, "p": p, "n": n,
                         "coverage": round(cov, 3), "primary": primary,
                         "pn_ok": pn_ok, "drop_beta": drop_b, "drop_an": drop_a,
                         "univ_hash": hashlib.sha256(",".join(names).encode()).hexdigest()[:12],
                         "snrhat": round(float(snrhat[j]), 4),
                         "floor_raw": round(float(floor_raw[j]), 4),
                         "floor_rep": round(float(floor_rep[j]), 4),
                         "corrected": pn_ok,
                         "D": round(float(D[j]), 4), "D2": round(float(D2[j]), 4),
                         "pval": round(float(pval[j]), 5),
                         "null_q75": round(float(q_lo), 4), "null_q99": round(float(q_hi), 4),
                         "angle_med": round(ang, 2) if ang == ang else np.nan,
                         "trusted": bool(trusted[j]), "bucket": b})
        # negative control on every primary window
        if primary:
            sh = np.array([row[rng.permutation(n)] for row in Yr])
            _, _, snr_sh, _, _ = pca(sh)
            neg_pass += int((snr_sh > edge_cut(p, n)).sum())
            neg_total += KP
        # positive control on the most recent window
        if wi == len(bounds) - 1:
            _, _, snr_pos, _, Xp = pca(Ya)
            r2_mkt = float(r2_centered(Xp[:1], fa[:, :1])[0])
            ctrl = {"pos_pc1_snr": float(snr_pos[0]), "pos_cut": edge_cut(p, n),
                    "pos_r2_mkt": r2_mkt,
                    "pos_pass": bool(snr_pos[0] > edge_cut(p, n) and r2_mkt >= 0.7)}

    ctrl["neg_rate"] = neg_pass / neg_total
    ctrl["neg_pass"] = ctrl["neg_rate"] <= 0.10
    df = pd.DataFrame(rows)
    df.to_csv(HERE / "floor_realdata.csv", index=False)

    pri_tr = df[df.primary & df.trusted]
    valid = (pri_tr.floor_rep.notna() & (pri_tr.floor_rep >= 0)
             & (pri_tr.floor_rep <= 1)).mean() if len(pri_tr) else float("nan")
    if not (ctrl["pos_pass"] and ctrl["neg_pass"]):
        verdict = "FAIL"
    elif valid >= 0.95:
        verdict = "SUCCESS"
    else:
        verdict = "AMBIGUOUS"
    write_report(df, ctrl, valid, verdict)
    stamp_run(track="estimator_lab", variant="floor_realdata",
              params={"n_an": N_AN, "n_beta": N_BETA, "kp": KP, "factors": FACTORS,
                      "q_hi": Q_HI, "q_lo": Q_LO, "cov_min": COV_MIN,
                      "zero_max": ZERO_MAX, "seed": SEED, "verdict": verdict,
                      "input_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()[:16]
                                       for f in INPUTS},
                      "memo": "FLOOR_REALDATA_MEMO.md#part-b"},
              n_trials=1)


def write_report(df, ctrl, valid, verdict):
    pri = df[df.primary]
    tr = pri[pri.trusted]
    far = df[~df.primary]
    lines = ["# Phase 6 — real FF-residualized S&P: floor + leakage-score prototype", "",
             "Descriptive only. Prereg: FLOOR_REALDATA_MEMO.md Part B (frozen). "
             f"{df.window.nunique()} windows, {pri.window.nunique()} primary "
             f"(coverage ≥ 90%), k′={KP}, FF3+MOM, n={N_AN}, betas {N_BETA}d, "
             "vol-standardized.", "",
             f"## Verdict (pre-committed rule): **{verdict}**", "",
             "## Controls",
             f"- positive: PC1 SNR̂ {ctrl['pos_pc1_snr']:.1f} vs cut {ctrl['pos_cut']:.2f}, "
             f"R² x₁ vs Mkt−RF {ctrl['pos_r2_mkt']:.3f} (bar ≥ 0.7) → "
             f"{'PASS' if ctrl['pos_pass'] else 'FAIL'}",
             f"- negative: shuffled-residual screen-pass rate {ctrl['neg_rate']:.1%} "
             f"(bar ≤ 10%) → {'PASS' if ctrl['neg_pass'] else 'FAIL'}",
             f"- floor validity among primary screen-passers: {valid:.1%} in [0,1] "
             f"(bar ≥ 95%)", "",
             "## Bucket counts (primary windows)", "", "| bucket | count | share |",
             "|---|---|---|"]
    for b, c in pri.bucket.value_counts().items():
        lines.append(f"| {b} | {c} | {c / len(pri):.0%} |")
    lines += ["", "## Screen-passers (primary windows)", "",
              f"- {len(tr)}/{len(pri)} factor-windows pass C4; "
              f"{int(tr.corrected.sum())} corrected (p/n ≥ 7), "
              f"{int((~tr.corrected).sum())} raw-floor-flagged",
              f"- reported floor: median {tr.floor_rep.median():.3f}, "
              f"IQR [{tr.floor_rep.quantile(.25):.3f}, {tr.floor_rep.quantile(.75):.3f}]",
              f"- D (vs published FF): median {tr.D.median():.3f}; "
              f"null q75 med {tr.null_q75.median():.3f}, q99 med {tr.null_q99.median():.3f}",
              f"- D′ (vs B̂-implied factors, secondary): median {tr.D2.median():.3f}",
              f"- adjacent-window subspace angle (median °, primary windows): "
              f"{pri.groupby('window').angle_med.first().median():.1f}", "",
              "## Non-primary (coverage < 90%, flagged) windows: "
              f"{far.window.nunique()} — reported in CSV only, survivorship-tilted", "",
              "## Bucket recurrence",
              f"- windows ≥ 4 apart (disjoint beta windows) reported in CSV; "
              "adjacent-window recurrence is mechanically inflated by ~189 shared "
              "beta-window days (memo A8).", "",
              "## Story", "", "(appended post-run — mechanism notes, no tuning)", ""]
    (HERE / "FLOOR_REALDATA.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
