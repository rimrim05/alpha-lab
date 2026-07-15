# Phase 6 — real FF-residualized S&P: floor + leakage-score prototype

Descriptive only. Prereg: FLOOR_REALDATA_MEMO.md Part B (frozen). 29 windows, 14 primary (coverage ≥ 90%), k′=5, FF3+MOM, n=63, betas 252d, vol-standardized.

## Verdict (pre-committed rule): **SUCCESS**

## Controls
- positive: PC1 SNR̂ 21.6 vs cut 1.34, R² x₁ vs Mkt−RF 0.722 (bar ≥ 0.7) → PASS
- negative: shuffled-residual screen-pass rate 10.0% (bar ≤ 10%) → PASS
- floor validity among primary screen-passers: 100.0% in [0,1] (bar ≥ 95%)

## Bucket counts (primary windows)

| bucket | count | share |
|---|---|---|
| material-known-assoc | 32 | 46% |
| mixed | 22 | 31% |
| low-known-assoc | 16 | 23% |

## Screen-passers (primary windows)

- 70/70 factor-windows pass C4; 70 corrected (p/n ≥ 7), 0 raw-floor-flagged
- reported floor: median 0.296, IQR [0.233, 0.360]
- D (vs published FF): median 0.162; null q75 med 0.085, q99 med 0.199
- D′ (vs B̂-implied factors, secondary): median 0.212
- adjacent-window subspace angle (median °, primary windows): 17.2 (corrected post-run — the generator averaged over all 29 windows; bug fixed in code, see Story)

## Non-primary (coverage < 90%, flagged) windows: 15 — reported in CSV only, survivorship-tilted

## Bucket recurrence
- windows ≥ 4 apart (disjoint beta windows) reported in CSV; adjacent-window recurrence is mechanically inflated by ~189 shared beta-window days (memo A8).

## Story

The SUCCESS verdict is procedurally valid and scientifically fragile, and the post-run
diagnostics (FLOOR_REALDATA_DIAG.md, prescribed by adversarial review) say exactly where.

1. **The negative control passing was a coin flip.** At the stamped seed 0 the shuffled
   screen-pass rate landed at exactly the 10.0% bar; across seeds 1–20 the rate is
   10.0–20.0% (median 14.3%) and 19/20 seeds would have returned FAIL. The pre-stated
   mechanism is confirmed: even after vol-standardization, real residual noise is
   heteroskedastic and heavy-tailed, and its shuffled PC-wise SNR̂ medians
   [1.33, 1.18, 1.08, 0.97, 0.91] sit at the C4 cut (1.356) instead of the isotropic
   ~0.86 the cut was calibrated over — the screen's 0.5 safety margin is fully consumed.
   The honest statement: on real S&P daily residuals, C4's false-pass rate is ~14%, not
   the sim-validated near-zero.

2. **But the recount mostly survives.** Against each PC rank's own empirical shuffled
   q99 (280 shuffled panels), real PC2–5 pass 14/14 at every rank — real cross-sectional
   structure clearly exceeds what structure-free noise produces at those ranks. The rank-1
   comparison (5/14) is not evidence against real PC1: the shuffled rank-1 null is
   dominated by the single-day heavy-tail artifact class (shuffled q99 = 9.8, max L ≈ 0.9),
   which grabs rank 1 of a shuffled panel by construction. Net honest pass count: 61/70,
   with the caveat that 28/70 passers have localization L > 0.30 (max 0.81) — a
   nontrivial fraction of "factors" at n = 63 are substantially one-day market events,
   the same statistical class as the artifacts, even when the event itself is real.

3. **PC1's row is the leakage footprint, and that is the finding, not a discovery of new
   risk.** High D and low floor on PC1 are one mechanical event: beta estimation error
   plus real drift (median adjacent-window subspace angle 17.2° on primary windows)
   leaves known-factor structure in the residuals; it becomes the dominant residual PC —
   hence high θ, low floor, high D simultaneously (corr(D, floor) = −0.70 among passers;
   all 5 lowest floors are PC1-material). Windows where D is low but D′ is high
   (2025-05-29: D 0.04, D′ 0.54) show leftover ESTIMATED-factor structure the published
   FF series can't see. This is Phase 4's trap materializing on real data, caught by the
   detector as designed: **residual PC1's low floors are not trustworthy-as-genuine.**

4. **Bucket shares are not stable numbers.** Under the memo's own dependence-honest
   restriction (windows ≥ 4 apart, disjoint beta windows), the material share ranges
   27–60% across the four stride-4 offsets, and PC-slot bucket agreement is 0.43
   adjacent / 0.44 at ≥ 4 apart (adversarial-review computation). Fourteen dependent
   windows do not pin down population shares; only the qualitative PC1-vs-tail pattern
   is stable.

5. Report errata: the subspace-angle line originally printed the all-29-window median
   (15.8) inside the primary-windows section; corrected to the primary-only 17.2 and the
   generator fixed. The prereg's bucket-recurrence metric was not emitted by the runner
   (only per-window buckets in the CSV); the agreement numbers above fill that gap.

**Transferable lesson:** the C4 cut's isotropic safety margin does not survive real
cross-sectional heteroskedasticity — on real panels the screen needs an empirical
per-rank shuffled null (as in the recount), not the closed-form edge. And the
full-window D_j detector's real-data value is exactly its sim-validated role: flagging
leaked known-factor risk masquerading as low-floor residual structure.

## Research log (Phase 6)

- **Verdict (one sentence):** The pipeline ran clean end-to-end on real
  FF-residualized S&P data and its qualitative outputs are informative — PC1 = flagged
  known-factor leakage, PC2–3 = detectable structure (plausibly sector), PC4–5 =
  detectable but near the real-data noise edge — while the preregistered SUCCESS
  verdict itself is seed-fragile because the C4 screen's isotropic calibration does not
  transfer to heteroskedastic heavy-tailed residuals (false-pass ~14% vs 10% bar).
- **Supported:** floors computable and in [0,1] (100%); p/n ≥ 7 regime held in all
  primary windows; positive control passed; D_j flags PC1 leakage exactly as the
  Phase-4 mechanism predicts; real PC2–5 structure exceeds rank-matched shuffled noise
  (14/14 per rank).
- **Not supported:** C4's sim-calibrated size on real data; quantitative bucket shares
  (27–60% range under honest dependence handling); any genuine/leaked truth claim; any
  "risk beyond standard models" reading of low-D factors (industry blindness, memo A7);
  Phase-4/5 error rates for the published-FF variant of D_j.
- **Validity regime:** descriptive; 14 primary windows (window-starts 2022-11-21 → 2026-03-02, ending 2026-05-29; span mislabeled "2021-11→2025-11" in the original log — erratum 2026-07-14), p ≈ 458–496,
  n = 63, FF3+MOM, S&P 500 PIT universe with window-level completeness look-ahead
  (memo A3); pre-2021 windows survivorship-tilted and excluded from all claims.
- **Next decision (per prereg):** SUCCESS branch → the fork goes to Kristen:
  (i) FF + industry known-factor model arm (quant review: the relevant extension —
  would test whether PC2–3 are absorbed as sector risk), possibly with an
  empirical-null screen replacing C4 on real data, or (ii) consolidate and stop —
  write the whole floor-pipeline arc up. A C4-recalibration THEORY claim (new edge
  formula under heteroskedasticity) would be hers to take to the lab, not a sim
  deliverable.
