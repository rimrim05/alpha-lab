"""Agent 7 — independence / residualization of the 7 live paper books.

Reconstructs each book's daily net return series using the SAME harness the paper
runner uses (compute_book -> _heal_etfs -> harness.run), on panel_2005.parquet.
Then: pairwise corr, beta to SPY/QQQ, residual (SPY+QQQ-orthogonalized) corr,
downside/crisis corr, shared drawdown regimes, effective independent-sample count.

Run: .venv/bin/python research/independent_alpha/independence/compute_independence.py
Outputs CSVs next to this file + prints headline numbers.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HUNT = ROOT / "research" / "hunt2026"
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(HUNT))
sys.path.insert(0, str(ROOT / "scripts"))
import harness  # noqa: E402
from hunt_paper_run import BOOKS, _heal_etfs, SPECS  # noqa: E402


def book_returns(panel: pd.DataFrame) -> pd.DataFrame:
    """Daily net return series per book, exactly as the runner would P&L them."""
    panel = _heal_etfs(panel)
    out = {}
    for name in BOOKS:
        spec = harness.load_spec(SPECS / name)
        out[name] = harness.run(spec, panel)["net_daily"]
    return pd.DataFrame(out)


def factor_returns(panel: pd.DataFrame) -> pd.DataFrame:
    """SPY and QQQ buy-and-hold net series on the identical P&L convention."""
    def bh(tkr):
        class _S:
            @staticmethod
            def target_weights(p):
                c = p["close"]
                df = pd.DataFrame(0.0, index=c.index, columns=[tkr])
                df.loc[c[tkr].notna(), tkr] = 1.0
                return df
        return harness.run(_S, panel)["net_daily"]
    return pd.DataFrame({"SPY": bh("SPY"), "QQQ": bh("QQQ")})


def residualize(books: pd.DataFrame, factors: pd.DataFrame):
    """OLS each book on [1, SPY, QQQ]; return residual frame + beta table."""
    X = np.column_stack([np.ones(len(factors)), factors["SPY"].values, factors["QQQ"].values])
    resid, betas = {}, {}
    for name in books.columns:
        y = books[name].values
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        betas[name] = {"alpha_ann": coef[0] * 252, "beta_SPY": coef[1], "beta_QQQ": coef[2]}
        resid[name] = y - X @ coef
    return pd.DataFrame(resid, index=books.index), pd.DataFrame(betas).T


def main():
    panel = pd.read_parquet(HUNT / "panel_2005.parquet")
    books = book_returns(panel)
    factors = factor_returns(panel)

    # align on common dates where every book + both factors are defined (books start when
    # their signal lookbacks fill; momentum_concentrated needs member stocks populated)
    df = books.join(factors, how="inner").dropna()
    # drop the leading warmup where books sit flat at 0 (no position yet) — those zero rows
    # are not real return observations and would inflate correlations toward the flat book
    active = (books.reindex(df.index).abs().sum(axis=1) > 0)
    first_active = active[active].index.min()
    df = df.loc[first_active:]
    books, factors = df[list(BOOKS)], df[["SPY", "QQQ"]]
    print(f"aligned window: {df.index[0].date()} .. {df.index[-1].date()}  n={len(df)} days")

    # (1) raw pairwise return correlation
    raw_corr = books.corr()
    raw_corr.to_csv(OUT / "corr_raw.csv")

    # (2) betas to SPY / QQQ + alpha
    resid, betas = residualize(books, factors)
    betas.to_csv(OUT / "betas.csv")

    # (3) residual pairwise correlation (after removing SPY+QQQ)
    resid_corr = resid.corr()
    resid_corr.to_csv(OUT / "corr_residual.csv")

    # (4) downside / crisis correlation: worst-decile SPY days
    thresh = factors["SPY"].quantile(0.10)
    crisis = df[factors["SPY"] <= thresh]
    down_corr = crisis[list(BOOKS)].corr()
    down_corr.to_csv(OUT / "corr_downside.csv")

    # (5) shared failure regimes: monthly returns, count months each pair is jointly negative
    monthly = (1 + books).resample("ME").prod() - 1
    neg = monthly < 0
    n_books = len(BOOKS)
    joint_neg = pd.DataFrame(index=BOOKS, columns=BOOKS, dtype=float)
    for a in BOOKS:
        for b in BOOKS:
            both = (neg[a] & neg[b]).sum()
            either = (neg[a] | neg[b]).sum()
            joint_neg.loc[a, b] = both / either if either else np.nan  # Jaccard of down-months
    joint_neg.to_csv(OUT / "shared_failure_jaccard.csv")

    # effective number of independent samples from residual corr eigenvalues
    def n_eff(C):
        ev = np.linalg.eigvalsh(C.values)
        ev = ev[ev > 1e-10]
        p = ev / ev.sum()
        return float(np.exp(-(p * np.log(p)).sum()))  # entropy-based effective rank

    neff_raw, neff_resid = n_eff(raw_corr), n_eff(resid_corr)

    # headline: the 3 vol books
    vol3 = ["vol_managed_qqq", "vol_core_svxy", "trend_vol_qqq"]
    def offdiag_mean(C, cols):
        sub = C.loc[cols, cols].values
        m = ~np.eye(len(cols), dtype=bool)
        return float(sub[m].mean())

    print("\n=== RAW pairwise correlation ===")
    print(raw_corr.round(2).to_string())
    print("\n=== BETAS (alpha annualized) ===")
    print(betas.round(3).to_string())
    print("\n=== RESIDUAL correlation (SPY+QQQ removed) ===")
    print(resid_corr.round(2).to_string())
    print("\n=== DOWNSIDE correlation (worst-decile SPY days, n=%d) ===" % len(crisis))
    print(down_corr.round(2).to_string())
    print("\n=== SHARED down-month Jaccard ===")
    print(joint_neg.astype(float).round(2).to_string())

    print("\n--- HEADLINES ---")
    print(f"3 vol books mean RAW pairwise corr:      {offdiag_mean(raw_corr, vol3):.3f}")
    print(f"3 vol books mean RESIDUAL pairwise corr: {offdiag_mean(resid_corr, vol3):.3f}")
    print(f"3 vol books mean DOWNSIDE corr:          {offdiag_mean(down_corr, vol3):.3f}")
    print(f"n_eff (raw):      {neff_raw:.2f} of {n_books}")
    print(f"n_eff (residual): {neff_resid:.2f} of {n_books}")

    # simple cluster count: greedy on residual corr > 0.5 = same cluster
    thr = 0.5
    clusters, assigned = [], set()
    for a in BOOKS:
        if a in assigned:
            continue
        grp = {a}
        for b in BOOKS:
            if b != a and b not in assigned and resid_corr.loc[a, b] > thr:
                grp.add(b)
        clusters.append(grp)
        assigned |= grp
    print(f"\nresidual-corr clusters (>{thr}): {len(clusters)}")
    for c in clusters:
        print("  ", sorted(c))
    return raw_corr, resid_corr, betas, down_corr, joint_neg, neff_raw, neff_resid, clusters


if __name__ == "__main__":
    main()
