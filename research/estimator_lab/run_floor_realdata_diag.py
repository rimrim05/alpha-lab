"""Phase 6 diagnostics addendum (read-only, post-run; prescribed by adversarial review).

No pipeline changes, no threshold tuning. Three checks on the frozen Phase 6 run:
(a) negative-control seed sweep (seeds 1-20): distribution of shuffled screen-pass
    rates -> is SUCCESS a seed artifact?
(b) empirical shuffled-quantile recount: per PC rank, pooled shuffled SNR-hat q99
    across all sweep panels; how many of the 70 real passers clear the cut their own
    noise actually produces?
(c) localization score L_j = max_t x_jt^2 / sum_t x_jt^2 per real passer vs shuffled
    slots -> how many passers look like single-day heavy-tail artifacts?
Writes FLOOR_REALDATA_DIAG.md.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
from run_floor_realdata import (  # noqa: E402
    COV_MIN, FACTORS, KP, N_AN, N_BETA, ZERO_MAX, edge_cut, pca)

ROOT = HERE.parents[1]
SEEDS = range(1, 21)


def build_windows():
    px = pd.read_parquet(ROOT / "data/raw/daily_px_statarb_wide.parquet")
    px.index = pd.to_datetime(px.index)
    ff = pd.read_parquet(ROOT / "data/raw/ff_factors_daily.parquet")
    pit = pd.read_parquet(ROOT / "data/raw/sp500_pit.parquet")
    ret = px.pct_change(fill_method=None).iloc[1:]
    dates = ret.index.intersection(ff.index)
    ret, ff = ret.loc[dates], ff.loc[dates]
    bounds, end = [], len(dates)
    while end - N_AN - N_BETA >= 0:
        bounds.append((end - N_AN - N_BETA, end - N_AN, end))
        end -= N_AN
    out = []
    for b0, a0, a1 in bounds[::-1]:
        snap = pit[pit.date <= dates[a0]].iloc[-1]
        members = [m for m in snap.members if m in ret.columns]
        blk = ret.iloc[b0:a1][members]
        bwin, awin = blk.iloc[:N_BETA], blk.iloc[N_BETA:]
        ok = (bwin.notna().all() & (bwin.std() > 0) & ((bwin == 0).mean() <= ZERO_MAX)
              & awin.notna().all() & (awin.std() > 0) & ((awin == 0).mean() <= ZERO_MAX))
        names = list(blk.columns[ok])
        if len(names) / len(snap.members) < COV_MIN:
            continue
        rex = blk[names].sub(ff.iloc[b0:a1]["RF"], axis=0)
        rex = rex / rex.iloc[:N_BETA].std()
        fb = ff.iloc[b0:a1].iloc[:N_BETA][FACTORS].values
        Xb = np.column_stack([np.ones(N_BETA), fb])
        coef, *_ = np.linalg.lstsq(Xb, rex.iloc[:N_BETA].values, rcond=None)
        Q, _ = np.linalg.qr(coef[1:].T)
        Ya = rex.iloc[N_BETA:].values.T
        out.append((str(dates[a0].date()), Ya - Q @ (Q.T @ Ya)))
    return out


def loc_score(X):
    x2 = X ** 2
    return x2.max(axis=1) / x2.sum(axis=1)


def main():
    wins = build_windows()
    n = N_AN
    # (a)+(b)+(c) from one sweep: per seed per window, shuffled SNRs + loc scores
    rates, snr_by_rank, loc_sh = [], [[] for _ in range(KP)], []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        hits = 0
        for _, Yr in wins:
            sh = np.array([row[rng.permutation(n)] for row in Yr])
            _, _, snr, _, X = pca(sh)
            cut = edge_cut(Yr.shape[0], n)
            hits += int((snr > cut).sum())
            for r in range(KP):
                snr_by_rank[r].append(snr[r])
            loc_sh.extend(loc_score(X)[snr > cut])
        rates.append(hits / (KP * len(wins)))
    rates = np.array(rates)
    q99 = [float(np.quantile(v, 0.99)) for v in snr_by_rank]
    med = [float(np.median(v)) for v in snr_by_rank]

    # real passers: recount vs empirical q99 per rank + localization
    real_snr, real_loc, real_win = [], [], []
    for d0, Yr in wins:
        _, _, snr, _, X = pca(Yr)
        real_snr.append(snr)
        real_loc.append(loc_score(X))
        real_win.append(d0)
    real_snr, real_loc = np.array(real_snr), np.array(real_loc)
    cut0 = edge_cut(480, n)
    survive = real_snr > np.array(q99)[None, :]
    loc_flag = real_loc > 0.30                             # indicative; full dist reported

    fail_seeds = int((rates > 0.10).sum())
    lines = ["# Phase 6 diagnostics addendum — adversarial-review minimum experiment", "",
             "Read-only; frozen pipeline untouched. Prescribed in the adversarial review "
             "of FLOOR_REALDATA.md; no thresholds tuned (the 0.30 localization cut and "
             "q99 recount are descriptive, not new gates).", "",
             "## (a) Negative-control seed sweep (seeds 1–20)",
             f"- pass-rate distribution: min {rates.min():.1%}, median "
             f"{np.median(rates):.1%}, max {rates.max():.1%}",
             f"- seeds exceeding the 10% bar (would flip verdict to FAIL): "
             f"{fail_seeds}/20",
             f"- seed-0 SUCCESS was {'a coin flip — the verdict rule is seed-fragile' if fail_seeds >= 6 else 'not strongly seed-dependent' if fail_seeds <= 2 else 'moderately seed-dependent'}", "",
             "## (b) Empirical shuffled-quantile recount (pooled per PC rank, "
             f"{len(SEEDS) * len(wins)} shuffled panels)",
             "| PC | shuffled median SNR̂ | shuffled q99 | C4 cut | real passers > q99 |",
             "|---|---|---|---|---|"]
    for r in range(KP):
        lines.append(f"| {r + 1} | {med[r]:.2f} | {q99[r]:.2f} | {cut0:.2f} "
                     f"| {int(survive[:, r].sum())}/{len(wins)} |")
    lines += [f"- honest pass count vs 70/70 under C4: "
              f"**{int(survive.sum())}/70** clear their rank's empirical q99", "",
              "## (c) Localization (single-day artifact) scores",
              f"- real passers with L > 0.30: {int(loc_flag.sum())}/70 "
              f"(diffuse-Gaussian expectation ≈ {2 * np.log(n) / n:.2f})",
              f"- real L distribution: median {np.median(real_loc):.3f}, "
              f"max {real_loc.max():.3f}",
              f"- shuffled PASSING slots' L: {np.array2string(np.sort(loc_sh)[::-1][:8], precision=2)}"
              " (the artifact class)", ""]
    hi = [(real_win[i], r + 1, round(float(real_loc[i, r]), 2))
          for i in range(len(wins)) for r in range(KP) if loc_flag[i, r]]
    if hi:
        lines.append(f"- flagged slots (window, PC, L): {hi}")
    (HERE / "FLOOR_REALDATA_DIAG.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
