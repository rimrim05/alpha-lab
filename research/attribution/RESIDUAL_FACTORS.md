# Vetted residual-factor panel (M3 regressors)

Built 2026-07-14 by build_residual_factors.py from the frozen Phase 6 floor pipeline (research/estimator_lab/run_floor_realdata.py; results FLOOR_REALDATA.md; diagnostics FLOOR_REALDATA_DIAG.md). Binding downstream prereg: research/hunt2026/preregistrations/factor-attribution-2026-07-14.md §M3.

Panel: residual_factors.parquet: daily returns x2..x5, 2021-07-01 → 2026-05-29 (1233 trading days), NaN where no vetted factor. 14 windows with membership coverage ≥ 90% (63-return-day non-overlapping analysis windows, grid inherited from the pipeline).

## Vetting rules (hard, frozen before build)
- residual PC1 excluded ALWAYS (leakage footprint, FLOOR_REALDATA.md Story #3)
- PC2–5 kept iff: passes C4 in that window AND reported floor in [0,1] AND not leakage-flagged (leak = D ≥ window circular-shift null q99 AND F-test p < 0.01) AND localization L ≤ 0.30 (one-day-event artifact guard)

## Chaining / sign rule
A factor is only defined within its 63-day window; x2..x5 are RANK-CHAINED series (PC rank 2..5 per window), not persistent economic factors. Sign alignment: each window's rank-j loading vector is correlated with the previous window's aligned rank-j loading on shared names; corr < 0 flips the sign of loading and returns (applied to every window for continuity; 23 flips total). Returns are in vol-standardized units (inherited from the pipeline), fine as regressors.

## Coverage
- vetted windows span 2022-11-21 → 2026-03-02 (window starts). NOTE: the memo's 'coverage ≥ 90% ≈ 2021 onward' estimate was optimistic: in the frozen run the gate first passes at the 2022-11-21 window (2021-05→2022-08 windows sit at 0.867–0.899), so 2021-07-01 → 2022-11-18 is structurally all-NaN.
- days with ≥ 1 vetted factor: 61.3% of the full 2021-07-01→2026-05-29 range; 85.7% of days from the first vetted window onward
- x2: 15.3% of days
- x3: 15.3% of days
- x4: 40.9% of days
- x5: 56.2% of days

## Bucket counts (all (window, PC) slots, pipeline bucket logic)

| bucket | count |
|---|---|
| likely-leaked-known-risk | 32 |
| mixed-uncertain | 22 |
| candidate-residual-risk | 16 |

## Kept vs excluded: 25 kept / 45 excluded

Top exclusion reasons:

- localized (L>0.30): 15
- PC1-always-excluded (leakage footprint): 14
- leakage (D≥q99 & F-p<0.01): 11
- leakage (D≥q99 & F-p<0.01); localized (L>0.30): 5

## Factor-quality table

| window | PC | SNR̂ | floor | floor ok | D | leak | L | bucket | kept | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| 2022-11-21 | 1 | 5.697 | 0.218 | y | 0.437 | y | 0.352 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2022-11-21 | 2 | 3.371 | 0.298 | y | 0.275 | y | 0.128 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2022-11-21 | 3 | 2.365 | 0.366 | y | 0.103 | n | 0.316 | mixed-uncertain | excl | localized (L>0.30) |
| 2022-11-21 | 4 | 2.063 | 0.395 | y | 0.075 | n | 0.161 | candidate-residual-risk | KEPT |  |
| 2022-11-21 | 5 | 1.898 | 0.414 | y | 0.178 | n | 0.169 | likely-leaked-known-risk | KEPT |  |
| 2023-02-23 | 1 | 10.667 | 0.154 | y | 0.508 | y | 0.33 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2023-02-23 | 2 | 6.122 | 0.209 | y | 0.447 | y | 0.092 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2023-02-23 | 3 | 2.954 | 0.321 | y | 0.133 | n | 0.424 | mixed-uncertain | excl | localized (L>0.30) |
| 2023-02-23 | 4 | 2.345 | 0.367 | y | 0.133 | n | 0.217 | mixed-uncertain | KEPT |  |
| 2023-02-23 | 5 | 2.206 | 0.38 | y | 0.043 | n | 0.216 | candidate-residual-risk | KEPT |  |
| 2023-05-24 | 1 | 5.663 | 0.218 | y | 0.427 | y | 0.185 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2023-05-24 | 2 | 3.242 | 0.303 | y | 0.163 | n | 0.196 | mixed-uncertain | KEPT |  |
| 2023-05-24 | 3 | 2.63 | 0.343 | y | 0.081 | n | 0.343 | candidate-residual-risk | excl | localized (L>0.30) |
| 2023-05-24 | 4 | 2.371 | 0.364 | y | 0.075 | n | 0.702 | candidate-residual-risk | excl | localized (L>0.30) |
| 2023-05-24 | 5 | 2.023 | 0.399 | y | 0.072 | n | 0.299 | candidate-residual-risk | KEPT |  |
| 2023-08-24 | 1 | 5.984 | 0.211 | y | 0.537 | y | 0.139 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2023-08-24 | 2 | 4.354 | 0.254 | y | 0.142 | n | 0.286 | mixed-uncertain | KEPT |  |
| 2023-08-24 | 3 | 3.801 | 0.276 | y | 0.106 | n | 0.296 | mixed-uncertain | KEPT |  |
| 2023-08-24 | 4 | 2.571 | 0.348 | y | 0.033 | n | 0.284 | candidate-residual-risk | KEPT |  |
| 2023-08-24 | 5 | 2.387 | 0.363 | y | 0.143 | n | 0.182 | mixed-uncertain | KEPT |  |
| 2023-11-22 | 1 | 7.137 | 0.19 | y | 0.559 | y | 0.133 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2023-11-22 | 2 | 3.495 | 0.29 | y | 0.374 | y | 0.664 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01); localized (L>0.30) |
| 2023-11-22 | 3 | 2.404 | 0.361 | y | 0.295 | y | 0.551 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01); localized (L>0.30) |
| 2023-11-22 | 4 | 2.082 | 0.392 | y | 0.096 | n | 0.392 | mixed-uncertain | excl | localized (L>0.30) |
| 2023-11-22 | 5 | 1.97 | 0.404 | y | 0.121 | n | 0.214 | mixed-uncertain | KEPT |  |
| 2024-02-26 | 1 | 10.815 | 0.152 | y | 0.053 | n | 0.698 | candidate-residual-risk | excl | PC1-always-excluded (leakage footprint) |
| 2024-02-26 | 2 | 3.593 | 0.285 | y | 0.161 | n | 0.541 | mixed-uncertain | excl | localized (L>0.30) |
| 2024-02-26 | 3 | 2.904 | 0.323 | y | 0.359 | y | 0.289 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2024-02-26 | 4 | 2.192 | 0.38 | y | 0.063 | n | 0.758 | candidate-residual-risk | excl | localized (L>0.30) |
| 2024-02-26 | 5 | 1.91 | 0.411 | y | 0.195 | n | 0.14 | likely-leaked-known-risk | KEPT |  |
| 2024-05-24 | 1 | 7.282 | 0.187 | y | 0.569 | y | 0.237 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2024-05-24 | 2 | 4.71 | 0.241 | y | 0.189 | n | 0.395 | mixed-uncertain | excl | localized (L>0.30) |
| 2024-05-24 | 3 | 3.695 | 0.279 | y | 0.241 | y | 0.375 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01); localized (L>0.30) |
| 2024-05-24 | 4 | 2.77 | 0.332 | y | 0.146 | n | 0.169 | mixed-uncertain | KEPT |  |
| 2024-05-24 | 5 | 2.186 | 0.38 | y | 0.079 | n | 0.265 | candidate-residual-risk | KEPT |  |
| 2024-08-26 | 1 | 8.034 | 0.177 | y | 0.644 | y | 0.759 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2024-08-26 | 2 | 4.916 | 0.235 | y | 0.146 | n | 0.243 | mixed-uncertain | KEPT |  |
| 2024-08-26 | 3 | 4.508 | 0.248 | y | 0.097 | n | 0.808 | mixed-uncertain | excl | localized (L>0.30) |
| 2024-08-26 | 4 | 2.456 | 0.355 | y | 0.057 | n | 0.568 | candidate-residual-risk | excl | localized (L>0.30) |
| 2024-08-26 | 5 | 2.256 | 0.373 | y | 0.019 | n | 0.192 | candidate-residual-risk | KEPT |  |
| 2024-11-22 | 1 | 6.029 | 0.208 | y | 0.306 | y | 0.348 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2024-11-22 | 2 | 4.988 | 0.233 | y | 0.521 | y | 0.179 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2024-11-22 | 3 | 3.34 | 0.296 | y | 0.054 | n | 0.285 | candidate-residual-risk | KEPT |  |
| 2024-11-22 | 4 | 2.502 | 0.351 | y | 0.1 | n | 0.139 | mixed-uncertain | KEPT |  |
| 2024-11-22 | 5 | 2.245 | 0.374 | y | 0.063 | n | 0.321 | candidate-residual-risk | excl | localized (L>0.30) |
| 2025-02-27 | 1 | 14.502 | 0.13 | y | 0.634 | y | 0.339 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2025-02-27 | 2 | 7.237 | 0.187 | y | 0.68 | y | 0.479 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01); localized (L>0.30) |
| 2025-02-27 | 3 | 4.094 | 0.262 | y | 0.543 | y | 0.198 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2025-02-27 | 4 | 3.342 | 0.296 | y | 0.03 | n | 0.115 | candidate-residual-risk | KEPT |  |
| 2025-02-27 | 5 | 2.777 | 0.33 | y | 0.088 | n | 0.159 | mixed-uncertain | KEPT |  |
| 2025-05-29 | 1 | 5.298 | 0.223 | y | 0.041 | n | 0.091 | candidate-residual-risk | excl | PC1-always-excluded (leakage footprint) |
| 2025-05-29 | 2 | 4.505 | 0.246 | y | 0.231 | y | 0.753 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01); localized (L>0.30) |
| 2025-05-29 | 3 | 3.721 | 0.276 | y | 0.118 | n | 0.353 | mixed-uncertain | excl | localized (L>0.30) |
| 2025-05-29 | 4 | 3.338 | 0.295 | y | 0.184 | n | 0.501 | likely-leaked-known-risk | excl | localized (L>0.30) |
| 2025-05-29 | 5 | 2.615 | 0.341 | y | 0.257 | y | 0.29 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2025-08-28 | 1 | 6.665 | 0.194 | y | 0.34 | y | 0.339 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2025-08-28 | 2 | 3.515 | 0.285 | y | 0.044 | n | 0.809 | candidate-residual-risk | excl | localized (L>0.30) |
| 2025-08-28 | 3 | 2.466 | 0.352 | y | 0.289 | y | 0.149 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2025-08-28 | 4 | 2.148 | 0.382 | y | 0.146 | n | 0.208 | mixed-uncertain | KEPT |  |
| 2025-08-28 | 5 | 1.958 | 0.402 | y | 0.092 | n | 0.205 | mixed-uncertain | KEPT |  |
| 2025-11-26 | 1 | 10.04 | 0.155 | y | 0.476 | y | 0.369 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2025-11-26 | 2 | 4.225 | 0.256 | y | 0.242 | y | 0.186 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2025-11-26 | 3 | 3.445 | 0.289 | y | 0.263 | y | 0.203 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2025-11-26 | 4 | 2.868 | 0.323 | y | 0.199 | n | 0.31 | mixed-uncertain | excl | localized (L>0.30) |
| 2025-11-26 | 5 | 2.718 | 0.333 | y | 0.263 | y | 0.242 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2026-03-02 | 1 | 11.948 | 0.141 | y | 0.614 | y | 0.125 | likely-leaked-known-risk | excl | PC1-always-excluded (leakage footprint) |
| 2026-03-02 | 2 | 6.28 | 0.201 | y | 0.711 | y | 0.096 | likely-leaked-known-risk | excl | leakage (D≥q99 & F-p<0.01) |
| 2026-03-02 | 3 | 3.817 | 0.271 | y | 0.2 | n | 0.24 | likely-leaked-known-risk | KEPT |  |
| 2026-03-02 | 4 | 2.581 | 0.343 | y | 0.084 | n | 0.149 | mixed-uncertain | KEPT |  |
| 2026-03-02 | 5 | 2.393 | 0.358 | y | 0.092 | n | 0.162 | mixed-uncertain | KEPT |  |

## Deviations from the frozen pipeline (documented, methodology unchanged)
- `pca_loadings` duplicates run_floor_realdata.pca's math to also return loadings U (needed for sign alignment); per-(window,PC) SNR̂/floor/D asserted equal to the frozen floor_realdata.csv at build time.
- window construction adapted from run_floor_realdata.main (a script entry point, not importable); identical grid, screens, standardization, betas, residualization.
- L ≤ 0.30 and the leakage cut are DESCRIPTIVE in FLOOR_REALDATA_DIAG.md; here they are hard gates, as required by prereg M3's vetting spec.

## LIMITS (read before using x2..x5)
- These are rank-chained STATISTICAL factors, not economic factors. Rank j in one window need not be the same risk source as rank j in the next; identity is only sign-continuity via loadings on shared names.
- C4 has a ~14% false-pass rate on real S&P residuals (heteroskedastic, heavy-tailed noise consumes the isotropic safety margin, FLOOR_REALDATA.md Story #1); some kept slots are plausibly noise despite passing every gate.
- Only 14 dependent windows, n = 63 obs each; adjacent windows share up to ~189 beta-window days, so buckets are correlated across neighbors (memo A8) and bucket shares are not stable population numbers.
- Low D means low association with FF3+MOM ONLY: industry/sector structure is invisible to the detector (memo A7); candidate-residual-risk factors are plausibly sector risk, not risk beyond standard models.
- Returns are vol-standardized units, window-level universe completeness is a known look-ahead (memo A3); descriptive regressor use only, no portfolio claims.
