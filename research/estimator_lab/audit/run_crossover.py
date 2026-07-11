"""EXP-EST-CROSSOVER: jse3 vs pca3 matched pair across estimation windows
n in {42,63,90,126,189,252}, same 137 months (all require >=252d history so the
month set is identical across n). Logs per month: paired realized-vol delta per
book, per-factor psi-hat, eigengap, p/n — state computed from the estimation
window ONLY (predictor available before construction).
Prereg: research/hunt2026/preregistrations/est-crossover-2026-07-10.md."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from estimators import ESTIMATORS, IDIO_FLOOR, TAU
from run_minvar import EXCLUDE, PANEL, START, minvar_weights

HERE = Path(__file__).parent
WINDOWS = (252,)  # audit copy: n=252 only (MAXW unchanged: 252)
K = 3
MAXW = max(WINDOWS)


def pca_jse_state(R, k=K):
    """One SVD -> (Sigma_pca, Sigma_jse, psi[k], eigengap). Mirrors
    estimators._pca_parts exactly (equivalence asserted in main)."""
    Y = (R - R.mean(axis=0)).T
    p, n = Y.shape
    U, sv, _ = np.linalg.svd(Y, full_matrices=False)
    H, sig = U[:, :k], sv[:k]
    lam = sig**2 / n
    resid = Y - H @ (H.T @ Y)
    D = np.maximum((resid**2).sum(axis=1) / n, IDIO_FLOOR)
    S_pca = (H * lam) @ H.T + np.diag(D)
    delta2 = (resid**2).sum() / ((p - k) * n)
    q = np.full(p, 1.0 / np.sqrt(p))
    V = np.empty_like(H)
    psi = np.empty(k)
    for i in range(k):
        h = H[:, i] if H[:, i].sum() >= 0 else -H[:, i]
        psi2 = max(TAU, 1.0 - p * delta2 / sig[i] ** 2)
        psi[i] = np.sqrt(psi2)
        hq = float(h @ q)
        c = np.clip(hq / np.sqrt(psi2), -1.0, 1.0)
        r = h - hq * q
        rn = np.linalg.norm(r)
        V[:, i] = q if rn < 1e-12 else c * q + np.sqrt(max(0.0, 1.0 - c**2)) * (r / rn)
    S_jse = (V * lam) @ V.T + np.diag(D)
    gap = (lam[0] - lam[1]) / lam[0]
    return S_pca, S_jse, psi, gap


def main():
    panel = pd.read_parquet(PANEL)
    close, member = panel["close"], panel["member"].fillna(0.0)
    stocks = [t for t in close.columns if t not in EXCLUDE]
    rets = close[stocks].pct_change(fill_method=None)
    idx = close.index

    firsts = pd.Series(idx, index=idx).groupby(idx.to_period("M")).first()
    firsts = firsts[firsts >= pd.Timestamp(START)]
    pos = {d: i for i, d in enumerate(idx)}

    checked = False
    rows = []
    for m, (per, d) in enumerate(firsts.items()):
        i = pos[d]
        if i < MAXW:  # same month set for every n
            continue
        nxt = firsts.iloc[m + 1] if m + 1 < len(firsts) else pd.Timestamp("2100-01-01")
        hold = rets.loc[(rets.index > d) & (rets.index <= nxt)]
        if len(hold) < 10:
            continue
        for W in WINDOWS:
            win = rets.iloc[i - W + 1: i + 1]
            elig = (member.loc[d, stocks] > 0) & win.notna().all()
            names = list(elig.index[elig])
            if len(names) < 100:
                continue
            R = win[names].to_numpy()
            Hret = hold[names].fillna(0.0).to_numpy()
            S_pca, S_jse, psi, gap = pca_jse_state(R)
            if not checked:  # equivalence with estimators.py, once
                assert np.allclose(S_pca, ESTIMATORS[f"pca{K}"](R), atol=1e-12)
                assert np.allclose(S_jse, ESTIMATORS[f"jse{K}"](R), atol=1e-12)
                checked = True
            row = {"date": d, "n": W, "p": len(names), "p_over_n": len(names) / W,
                   "psi1": psi[0], "psi2": psi[1], "psi3": psi[2],
                   "psi_med": float(np.median(psi)), "eigengap": gap}
            ok = True
            for book, lo in (("unconstrained", False), ("long_only", True)):
                wp = minvar_weights(S_pca, lo)
                wj = minvar_weights(S_jse, lo)
                if wp is None or wj is None:
                    ok = False
                    break
                vp = (Hret @ wp).std(ddof=1) * np.sqrt(252)
                vj = (Hret @ wj).std(ddof=1) * np.sqrt(252)
                row[f"vol_pca_{book}"] = vp
                row[f"vol_jse_{book}"] = vj
                row[f"delta_{book}"] = vj - vp
            if ok:
                rows.append(row)
        if m % 24 == 0:
            print(f"  {d.date()}")

    df = pd.DataFrame(rows)
    df.to_csv(HERE / "crossover.csv", index=False)

    print("\n=== crossover table: paired jse3-pca3 delta (vol %-pts; negative = JSE helps) ===")
    for W in WINDOWS:
        g = df[df["n"] == W]
        line = f"n={W:3d}  months={len(g):3d}  psi_med(median)={g['psi_med'].median():.4f}  p/n={g['p_over_n'].mean():.2f}"
        for book in ("long_only", "unconstrained"):
            dd = g[f"delta_{book}"] * 100
            t, pv = stats.ttest_rel(g[f"vol_jse_{book}"], g[f"vol_pca_{book}"])
            line += f"  | {book} {dd.mean():+.3f} t={t:+.2f} p={pv:.4f}"
        print(line)

    print("\n=== predictor test: pooled across all n x months (state from estimation window only) ===")
    for book in ("long_only", "unconstrained"):
        dlt = df[f"delta_{book}"]
        for var in ("psi_med", "eigengap", "p_over_n"):
            rho, pv = stats.spearmanr(df[var], dlt)
            print(f"  {book:13} delta vs {var:9}: spearman rho={rho:+.3f} p={pv:.2e}")
        b, a = np.polyfit(df["psi_med"], dlt * 100, 1)
        print(f"  {book:13} OLS: delta(vol%pts) = {a:+.3f} {b:+.3f}*psi_med")

    print("\n=== pre-committed decision rule (long-only): apply JSE when psi_med < X ===")
    for X in (0.90, 0.95):
        sel = df[df["psi_med"] < X]
        out = df[df["psi_med"] >= X]
        hr = (sel["delta_long_only"] < 0).mean() if len(sel) else np.nan
        print(f"  X={X}: {len(sel)} month-configs selected, mean delta={sel['delta_long_only'].mean()*100:+.3f} "
              f"vol%pts, hit rate(delta<0)={hr:.1%}; unselected mean delta={out['delta_long_only'].mean()*100:+.3f}")
    # in-sample-only threshold scan (color, not a finding)
    best = max((round(x, 2) for x in np.arange(0.5, 1.0, 0.01)),
               key=lambda x: -df.loc[df["psi_med"] < x, "delta_long_only"].mean()
               if (df["psi_med"] < x).sum() >= 50 else -np.inf)
    sel = df[df["psi_med"] < best]
    print(f"  [in-sample scan] best X={best}: mean delta={sel['delta_long_only'].mean()*100:+.3f} "
          f"vol%pts over {len(sel)} month-configs, hit rate={(sel['delta_long_only']<0).mean():.1%}")


if __name__ == "__main__":
    main()
