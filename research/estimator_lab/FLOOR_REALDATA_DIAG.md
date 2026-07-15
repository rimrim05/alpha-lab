# Phase 6 diagnostics addendum — adversarial-review minimum experiment

Read-only; frozen pipeline untouched. Prescribed in the adversarial review of FLOOR_REALDATA.md; no thresholds tuned (the 0.30 localization cut and q99 recount are descriptive, not new gates).

## (a) Negative-control seed sweep (seeds 1–20)
- pass-rate distribution: min 10.0%, median 14.3%, max 20.0%
- seeds exceeding the 10% bar (would flip verdict to FAIL): 19/20
- seed-0 SUCCESS was a coin flip — the verdict rule is seed-fragile

## (b) Empirical shuffled-quantile recount (pooled per PC rank, 280 shuffled panels)
| PC | shuffled median SNR̂ | shuffled q99 | C4 cut | real passers > q99 |
|---|---|---|---|---|
| 1 | 1.40 | 9.82 | 1.36 | 5/14 |
| 2 | 1.17 | 1.61 | 1.36 | 14/14 |
| 3 | 1.06 | 1.37 | 1.36 | 14/14 |
| 4 | 0.97 | 1.14 | 1.36 | 14/14 |
| 5 | 0.89 | 1.05 | 1.36 | 14/14 |
- honest pass count vs 70/70 under C4: **61/70** clear their rank's empirical q99

## (c) Localization (single-day artifact) scores
- real passers with L > 0.30: 28/70 (diffuse-Gaussian expectation ≈ 0.13)
- real L distribution: median 0.275, max 0.809
- shuffled PASSING slots' L: [0.91 0.88 0.86 0.86 0.83 0.81 0.81 0.8 ] (the artifact class)

- flagged slots (window, PC, L): [('2022-11-21', 1, 0.35), ('2022-11-21', 3, 0.32), ('2023-02-23', 1, 0.33), ('2023-02-23', 3, 0.42), ('2023-05-24', 3, 0.34), ('2023-05-24', 4, 0.7), ('2023-11-22', 2, 0.66), ('2023-11-22', 3, 0.55), ('2023-11-22', 4, 0.39), ('2024-02-26', 1, 0.7), ('2024-02-26', 2, 0.54), ('2024-02-26', 4, 0.76), ('2024-05-24', 2, 0.4), ('2024-05-24', 3, 0.37), ('2024-08-26', 1, 0.76), ('2024-08-26', 3, 0.81), ('2024-08-26', 4, 0.57), ('2024-11-22', 1, 0.35), ('2024-11-22', 5, 0.32), ('2025-02-27', 1, 0.34), ('2025-02-27', 2, 0.48), ('2025-05-29', 2, 0.75), ('2025-05-29', 3, 0.35), ('2025-05-29', 4, 0.5), ('2025-08-28', 1, 0.34), ('2025-08-28', 2, 0.81), ('2025-11-26', 1, 0.37), ('2025-11-26', 4, 0.31)]
