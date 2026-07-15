"""Vetted residual-factor daily return panel for prereg M3 (factor-attribution-2026-07-14).

Methodology is REUSED, not rewritten, from the frozen Phase 6 pipeline
(research/estimator_lab/run_floor_realdata.py): same window grid, PIT universe +
screens, vol-standardization, trailing-252d FF3+MOM betas, cross-sectional
residualization, dual-space PCA, C4 screen, floor correction rule, D vs published FF,
F-test, and circular-shift null. Localization L is imported from
run_floor_realdata_diag.py.

Added on top (the M3 vetting layer — new GATES, not new methodology):
- PC1 excluded always (leakage footprint, FLOOR_REALDATA.md Story #3)
- keep PC2-5 iff passes C4, floor_rep in [0,1], NOT leakage-flagged
  (leak = D >= window null q99 AND F-test p < 0.01), and L <= 0.30
- surviving per-window factor returns chained into rank series x2..x5, sign-aligned
  window-to-window by loading correlation on shared names

Self-check: recomputed (window, PC) snrhat / floor_rep / D are asserted equal to the
frozen run's floor_realdata.csv before anything is written.

Outputs (research/attribution/): residual_factors.parquet, RESIDUAL_FACTORS.md,
plus artifacts/attribution/residual_factors_run.json via stamp_run.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
EL = ROOT / "research" / "estimator_lab"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(EL))
import run_floor_realdata as rf  # noqa: E402  (frozen pipeline — read-only reuse)
from run_floor_realdata_diag import loc_score  # noqa: E402
from core.eval.run_manifest import stamp_run  # noqa: E402

START, END = "2021-07-01", "2026-05-29"
L_MAX = 0.30
RANKS = range(2, rf.KP + 1)  # x2..x5


def pca_loadings(Y):
    """Deviation (documented): identical math to run_floor_realdata.pca, but also
    returns the loading matrix U (p x KP) needed for cross-window sign alignment."""
    p, n = Y.shape
    W = Y.T @ Y / (n * p)
    w, V = np.linalg.eigh(W)
    w, V = w[::-1], V[:, ::-1]
    theta, ell = w[:rf.KP], w[rf.KP:].mean()
    U = Y @ V[:, :rf.KP] / np.sqrt(n * p * theta)
    return theta, ell, theta / ell - 1.0, ell / theta, U.T @ Y, U


def windows():
    """Window construction adapted verbatim from run_floor_realdata.main (deviation:
    main() is a script entry point, not importable as a library; identical screens,
    grid, standardization, betas, residualization). Yields primary windows only."""
    px = pd.read_parquet(ROOT / rf.INPUTS[0])
    px.index = pd.to_datetime(px.index)
    ff = pd.read_parquet(ROOT / rf.INPUTS[1])
    pit = pd.read_parquet(ROOT / rf.INPUTS[2])
    ret = px.pct_change(fill_method=None).iloc[1:]
    dates = ret.index.intersection(ff.index)
    ret, ff = ret.loc[dates], ff.loc[dates]
    bounds, end = [], len(dates)
    while end - rf.N_AN - rf.N_BETA >= 0:
        bounds.append((end - rf.N_AN - rf.N_BETA, end - rf.N_AN, end))
        end -= rf.N_AN
    wins = []
    for b0, a0, a1 in bounds[::-1]:
        snap = pit[pit.date <= dates[a0]].iloc[-1]
        members = [m for m in snap.members if m in ret.columns]
        blk = ret.iloc[b0:a1][members]
        bwin, awin = blk.iloc[:rf.N_BETA], blk.iloc[rf.N_BETA:]
        ok_b = bwin.notna().all() & (bwin.std() > 0) & ((bwin == 0).mean() <= rf.ZERO_MAX)
        ok_a = awin.notna().all() & (awin.std() > 0) & ((awin == 0).mean() <= rf.ZERO_MAX)
        names = list(blk.columns[ok_b & ok_a])
        if len(names) / len(snap.members) < rf.COV_MIN:
            continue
        f = ff.iloc[b0:a1]
        rex = blk[names].sub(f["RF"], axis=0)
        rex = rex / rex.iloc[:rf.N_BETA].std()
        fb = f.iloc[:rf.N_BETA][rf.FACTORS].values
        fa = f.iloc[rf.N_BETA:][rf.FACTORS].values
        Xb = np.column_stack([np.ones(rf.N_BETA), fb])
        coef, *_ = np.linalg.lstsq(Xb, rex.iloc[:rf.N_BETA].values, rcond=None)
        Q, _ = np.linalg.qr(coef[1:].T)
        Ya = rex.iloc[rf.N_BETA:].values.T
        wins.append((str(dates[a0].date()), dates[a0:a1], names, Ya - Q @ (Q.T @ Ya), fa))
    return dates, wins


def main():
    csv_ref = pd.read_csv(EL / "floor_realdata.csv")
    dates, wins = windows()
    rows, kept_series, ref_load, flips = [], [], {}, 0
    for d0, an_dates, names, Yr, fa in wins:
        p, n = Yr.shape
        theta, ell, snrhat, floor_raw, X, U = pca_loadings(Yr)
        trusted = snrhat > rf.edge_cut(p, n)
        floor_rep = floor_raw + (0.5 * n / p if p / n >= 7 else 0.0)
        D = rf.r2_centered(X, fa)
        Fstat = (D / rf.K_F) / ((1 - D) / (n - 1 - rf.K_F))
        pval = stats.f.sf(Fstat, rf.K_F, n - 1 - rf.K_F)
        null = rf.shift_null(X, fa)
        q_hi, q_lo = np.quantile(null, rf.Q_HI), np.quantile(null, rf.Q_LO)
        L = loc_score(X)
        # self-check against the frozen run before trusting anything
        ref = csv_ref[csv_ref.window == d0].sort_values("pc")
        assert len(ref) == rf.KP and bool(ref.primary.all()), f"{d0}: window mismatch vs frozen CSV"
        assert np.allclose(ref.snrhat.values, np.round(snrhat, 4), atol=1e-3), f"{d0}: snrhat drift"
        assert np.allclose(ref.floor_rep.values, np.round(floor_rep, 4), atol=1e-3), f"{d0}: floor drift"
        assert np.allclose(ref.D.values, np.round(D, 4), atol=1e-3), f"{d0}: D drift"
        # sign alignment (ranks 2..5), applied even in excluded windows for continuity
        name_ix = {m: i for i, m in enumerate(names)}
        for r in range(1, rf.KP):
            u = U[:, r].copy()
            prev = ref_load.get(r)
            if prev is not None:
                shared = [m for m in names if m in prev]
                if len(shared) >= 10:
                    a = np.array([prev[m] for m in shared])
                    if np.corrcoef(a, u[[name_ix[m] for m in shared]])[0, 1] < 0:
                        u, X[r] = -u, -X[r]
                        flips += 1
            ref_load[r] = dict(zip(names, u))
        for j in range(rf.KP):
            floor_ok = 0.0 <= floor_rep[j] <= 1.0
            leak = bool(D[j] >= q_hi and pval[j] < 0.01)
            bucket = ("noise-like" if not trusted[j]
                      else "likely-leaked-known-risk" if D[j] >= q_hi
                      else "candidate-residual-risk" if D[j] < q_lo
                      else "mixed-uncertain")
            reasons = []
            if j == 0:
                reasons.append("PC1-always-excluded (leakage footprint)")
            else:
                if not trusted[j]:
                    reasons.append("fails-C4")
                if not floor_ok:
                    reasons.append("floor-outside-[0,1]")
                if leak:
                    reasons.append("leakage (D≥q99 & F-p<0.01)")
                if L[j] > L_MAX:
                    reasons.append("localized (L>0.30)")
            kept = not reasons
            rows.append({"window": d0, "pc": j + 1, "snrhat": round(float(snrhat[j]), 3),
                         "floor": round(float(floor_rep[j]), 3), "floor_ok": floor_ok,
                         "D": round(float(D[j]), 3), "leak": leak,
                         "L": round(float(L[j]), 3), "bucket": bucket,
                         "kept": kept, "reason": "; ".join(reasons)})
            if kept:
                kept_series.append((an_dates, j + 1, X[j].copy()))

    qual = pd.DataFrame(rows)
    idx = dates[(dates >= START) & (dates <= END)]
    out = pd.DataFrame(np.nan, index=idx, columns=[f"x{r}" for r in RANKS])
    out.index.name = "date"
    for an_dates, rank, vals in kept_series:
        s = pd.Series(vals, index=an_dates)
        s = s[(s.index >= idx[0]) & (s.index <= idx[-1])]
        out.loc[s.index, f"x{rank}"] = s.values
    out.to_parquet(HERE / "residual_factors.parquet")
    write_report(qual, out, idx, len(wins), flips)
    stamp_run(track="attribution", variant="residual_factors",
              params={"source_pipeline": "research/estimator_lab/run_floor_realdata.py (frozen)",
                      "range": [START, END], "cov_min": rf.COV_MIN, "l_max": L_MAX,
                      "vetting": "PC1 excluded; PC2-5 need C4 + floor in [0,1] + "
                                 "not(D>=q99 & F-p<0.01) + L<=0.30",
                      "sign_rule": "loading corr on shared names vs previous window, flip if < 0",
                      "input_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()[:16]
                                       for f in rf.INPUTS},
                      "prereg": "research/hunt2026/preregistrations/factor-attribution-2026-07-14.md#M3"},
              n_trials=1)


def write_report(qual, out, idx, n_win, flips):
    cov_any = out.notna().any(axis=1).mean()
    kept = qual[qual.kept]
    excl = qual[~qual.kept]
    lines = ["# Vetted residual-factor panel (M3 regressors)", "",
             f"Built {pd.Timestamp.now():%Y-%m-%d} by build_residual_factors.py from the frozen "
             "Phase 6 floor pipeline (research/estimator_lab/run_floor_realdata.py; results "
             "FLOOR_REALDATA.md; diagnostics FLOOR_REALDATA_DIAG.md). Binding downstream prereg: "
             "research/hunt2026/preregistrations/factor-attribution-2026-07-14.md §M3.", "",
             f"Panel: residual_factors.parquet — daily returns x2..x5, {idx[0].date()} → "
             f"{idx[-1].date()} ({len(idx)} trading days), NaN where no vetted factor. "
             f"{n_win} windows with membership coverage ≥ {rf.COV_MIN:.0%} "
             "(63-return-day non-overlapping analysis windows, grid inherited from the pipeline).", "",
             "## Vetting rules (hard, frozen before build)",
             "- residual PC1 excluded ALWAYS (leakage footprint — FLOOR_REALDATA.md Story #3)",
             "- PC2–5 kept iff: passes C4 in that window AND reported floor in [0,1] AND not "
             "leakage-flagged (leak = D ≥ window circular-shift null q99 AND F-test p < 0.01) "
             "AND localization L ≤ 0.30 (one-day-event artifact guard)", "",
             "## Chaining / sign rule",
             "A factor is only defined within its 63-day window; x2..x5 are RANK-CHAINED series "
             "(PC rank 2..5 per window), not persistent economic factors. Sign alignment: each "
             "window's rank-j loading vector is correlated with the previous window's aligned "
             "rank-j loading on shared names; corr < 0 flips the sign of loading and returns "
             f"(applied to every window for continuity; {flips} flips total). Returns are in "
             "vol-standardized units (inherited from the pipeline), fine as regressors.", "",
             "## Coverage",
             f"- vetted windows span {qual.window.min()} → {qual.window.max()} (window starts). "
             "NOTE: the memo's 'coverage ≥ 90% ≈ 2021 onward' estimate was optimistic — in the "
             "frozen run the gate first passes at the 2022-11-21 window (2021-05→2022-08 windows "
             "sit at 0.867–0.899), so 2021-07-01 → 2022-11-18 is structurally all-NaN.",
             f"- days with ≥ 1 vetted factor: {cov_any:.1%} of the full {idx[0].date()}→"
             f"{idx[-1].date()} range; "
             f"{out.loc[qual.window.min():].notna().any(axis=1).mean():.1%} of days from the "
             "first vetted window onward"]
    for c in out.columns:
        lines.append(f"- {c}: {out[c].notna().mean():.1%} of days")
    lines += ["", "## Bucket counts (all (window, PC) slots, pipeline bucket logic)", "",
              "| bucket | count |", "|---|---|"]
    for b, c in qual.bucket.value_counts().items():
        lines.append(f"| {b} | {c} |")
    lines += ["", f"## Kept vs excluded: {len(kept)} kept / {len(excl)} excluded", "",
              "Top exclusion reasons:", ""]
    for r, c in excl.reason.value_counts().head(8).items():
        lines.append(f"- {r}: {c}")
    lines += ["", "## Factor-quality table", "",
              "| window | PC | SNR̂ | floor | floor ok | D | leak | L | bucket | kept | reason |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in qual.iterrows():
        lines.append(f"| {r.window} | {r.pc} | {r.snrhat} | {r.floor} | "
                     f"{'y' if r.floor_ok else 'n'} | {r.D} | {'y' if r.leak else 'n'} | "
                     f"{r.L} | {r.bucket} | {'KEPT' if r.kept else 'excl'} | {r.reason} |")
    lines += ["", "## Deviations from the frozen pipeline (documented, methodology unchanged)",
              "- `pca_loadings` duplicates run_floor_realdata.pca's math to also return loadings U "
              "(needed for sign alignment); per-(window,PC) SNR̂/floor/D asserted equal to the "
              "frozen floor_realdata.csv at build time.",
              "- window construction adapted from run_floor_realdata.main (a script entry point, "
              "not importable); identical grid, screens, standardization, betas, residualization.",
              "- L ≤ 0.30 and the leakage cut are DESCRIPTIVE in FLOOR_REALDATA_DIAG.md; here they "
              "are hard gates, as required by prereg M3's vetting spec.", "",
              "## LIMITS (read before using x2..x5)",
              "- These are rank-chained STATISTICAL factors, not economic factors. Rank j in one "
              "window need not be the same risk source as rank j in the next; identity is only "
              "sign-continuity via loadings on shared names.",
              "- C4 has a ~14% false-pass rate on real S&P residuals (heteroskedastic, heavy-tailed "
              "noise consumes the isotropic safety margin — FLOOR_REALDATA.md Story #1); some kept "
              "slots are plausibly noise despite passing every gate.",
              f"- Only {qual.window.nunique()} dependent windows, n = 63 obs each; adjacent windows "
              "share up to ~189 beta-window days, so buckets are correlated across neighbors "
              "(memo A8) and bucket shares are not stable population numbers.",
              "- Low D means low association with FF3+MOM ONLY — industry/sector structure is "
              "invisible to the detector (memo A7); candidate-residual-risk factors are plausibly "
              "sector risk, not risk beyond standard models.",
              "- Returns are vol-standardized units, window-level universe completeness is a known "
              "look-ahead (memo A3); descriptive regressor use only, no portfolio claims.", ""]
    (HERE / "RESIDUAL_FACTORS.md").write_text("\n".join(lines))
    print("\n".join(lines[:40]))
    print(f"...\nkept {len(kept)} / excluded {len(excl)}; coverage any-factor {cov_any:.1%}")


if __name__ == "__main__":
    main()
