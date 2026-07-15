# Phase 7 — FF+industry arm: vetted residual-factor panel

Descriptive only. Prereg: FLOOR_INDUSTRY_MEMO.md rev 2 (frozen). 14 primary windows, arms A (FF) / B (FF+11 GICS).

## Verdict (pre-committed): **FAIL**

## Controls
- positive: PC1 SNR̂ 21.6 vs rank-1 screen q99 10.63, R² vs Mkt−RF 0.722 (bar 0.7) → PASS
- industry: med sector-R² arm-A 0.607 → arm-B 0.347 (FAIL)
- screen calibration-consistency: held-out exceedance 0.50% (bar ≤ 3%) → PASS; per-rank: [0.007 0.    0.004 0.011 0.004]
- floor validity (detectable slots): 100.0%

## Screen (empirical per-rank q99; C4 kept as descriptive column)
- arm A q99 by rank: [10.11  1.68  1.36  1.2   1.06]
- arm B q99 by rank: [10.63  1.83  1.46  1.25  1.12]
- detectable slots: arm A 60/70, arm B 58/70 (C4 would pass: A 70, B 70)
- screen-fail-high-known-assoc (mostly rank-1 insensitivity): A 9, B 11

## Label counts

| label | arm A | arm B |
|---|---|---|
| noise-like | 10 | 12 |
| explained-by-industry-or-known | 0 | 0 |
| high-known-association | 20 | 28 |
| detectable-candidate-residual-risk | 11 | 5 |
| mixed-uncertain | 29 | 25 |

## Arm-A slot flow under industry
- arm-A detectable: 60; of those explained-by-industry-or-known: 0
- arm-A a_match (vs arm-B top-7): median 0.877

## Vetted panel for Stage 2 (arm-B label 4)
- 5 slots across 4 windows; recurrent: 0
- floors: median 0.385
- L-cut sensitivity (label-4 count at L ≤ 0.25/0.30/0.40/0.50): [2, 2, 3, 5]
- shuffled-panel L quantiles (q50/q90/q99): A [0.22 0.55 0.79], B [0.24 0.59 0.81]

## Story

(appended post-run)

## Errata & adversarial corrections (post-run, 2026-07-14)

The adversarial review materially corrected the story above; the corrections BIND all
downstream use (Stage 2, final memo):

1. **a_match headline RETRACTED.** The correct null for a_match (arm-B top-7 spanning
   arm-A top-5 after removing a RANDOM 11-dim cross-sectional subspace, sector sizes
   preserved) has median 0.991. The observed 0.877 sits BELOW that mechanical floor —
   "factor directions persist nearly intact" was measured against the wrong null and
   carries zero positive information; read correctly, the sector projection removed
   MORE factor content than a random 11-dim projection would.
2. **Null-relative control arithmetic.** Sector-R² on 11 regressors at n=63 has a dof
   baseline ≈ 0.177. As EXCESS over that baseline — the memo's own frozen "levels are
   meaningless" principle — the industry projection removed (0.430−0.169)/0.430 =
   60.6% ≥ the 50% bar: the control PASSES in its own spirit. The FAIL isolates to a
   raw-ratio metric that contradicted the memo's stated principle; this was catchable
   pre-freeze and passed two review rounds — a process defect, recorded.
3. **"Theme structure" downgraded to UNRESOLVED.** Shared-calendar vol-regime coupling
   (sector series built from the same stale-vol-standardized names) explains the same
   three diagnostic facts; the persistence magnitude was also overstated ~2× by quoting
   raw medians (null-relative persistent excess ≈ 0.11–0.17, not "roughly half").
   Split-half + vol-orthogonalized experiment deferred; NO downstream claim may lean on
   the theme identity.
4. **"Not coarse sector risk" downgraded** to: "not annihilated by 11-GICS-sector-MEAN
   projection." Zero label-2 slots partly reflects gate insensitivity (a_match's
   mechanical floor ~0.97–0.99 makes the no-counterpart condition nearly unfireable).
5. **Code fix + rerun:** arm-B SNR̂/floors had used ell from k=7 PCA against a k=5
   null (~6% SNR inflation / floors 6% low). Fixed; rerun; ZERO label changes
   (detectability margins 1.48–2.12× the cut); label-4 floor median 0.365 → 0.385.
6. **Vetted panel evidential value ≈ nil for control purposes** (0/5 recurrent, 2/5 in
   one window, exact-permutation p on D 0.21–0.51). Stage 2 must treat L4 results as
   spot-checks, never as "survived residual controls."
7. Phase 6 log erratum (propagates here): the 14 primary windows span window-starts
   2022-11-21 → 2026-03-02 (ending 2026-05-29), not "2021-11 → 2025-11" as the Phase 6
   research log stated.
8. **Proceed-decision assessment (adversarial):** defensible on content, irregular on
   process — a documented consequence-override, NOT verdict-shopping; its validity
   rests on point 2 above, not on the retracted persistence claims. Conditions (a)-(d)
   of the assessment are adopted as binding and reflected in points 1–6.
