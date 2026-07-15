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
- floors: median 0.365
- L-cut sensitivity (label-4 count at L ≤ 0.25/0.30/0.40/0.50): [2, 2, 3, 5]
- shuffled-panel L quantiles (q50/q90/q99): A [0.22 0.55 0.79], B [0.24 0.59 0.81]

## Story

The pre-committed verdict is FAIL — the industry control missed its bar (sector-R² of
detectable non-PC1 slots dropped 0.607 → 0.347 = 43%, bar ≥ 50%) — and the mechanism
diagnosis says the bar was mis-set, not that the projection malfunctioned. Three facts,
established read-only, no tuning:

1. Market embedding refuted: FF-orthogonalizing the sector regressors moves med_B only
   0.347 → 0.285. The persistent association is genuinely sector-linked, not leaked
   market inside the sector series.
2. Sector-MEAN content of arm-B slots is zero BY CONSTRUCTION (residuals are
   cross-sectionally orthogonal to the dummies), so the 0.285 must ride on
   within-sector loading heterogeneity — structure finer than the 11-dummy span.
3. The slots are diffuse, not sector tilts: median top-sector loading mass 24%
   (uniform reference 16%); only 7% of slots put >40% mass in one sector. The
   persistence is cross-sector THEME structure (e.g., cyclical/defensive,
   rate-sensitivity complexions) that co-moves with sector returns without living
   inside any sector.

So the 50% bar implicitly assumed residual-PC sector association was mostly removable
sector-mean content; roughly half of it is theme/sub-sector structure that the memo's
own coarseness limitation said the model could not remove. Rule-drafting
miscalibration, owned (third in project history). The verdict stands as recorded.

Main-line findings that survive this:
- The Phase-6 fork question is answered: detectable FF-residual factors are NOT coarse
  sector risk. Zero arm-A slots were "explained-by-industry"; median a_match 0.877 —
  the factor directions persist nearly intact under 11-sector removal; only their
  sector-mean component (the 43%) was absorbed.
- The vetted Stage-2 panel is thin and fragile: 5 label-4 slots across 4 windows, zero
  recurrent, L-cut sensitivity 2→5 slots over L ∈ [0.25, 0.50]. As pre-stated, the
  gate is exclusion-biased; Stage 2 receives scores alongside labels.
- Arm-B "high-known-association" (28/70) exceeds arm A (20/70) — consistent with the
  pre-stated label-3 inflation caveat plus 15 regressors carrying more of the panel.

**Research Lead decision (documented, adversarial review invited to attack it):**
Stage 2 proceeds using this panel. Rationale: the FAIL isolates to a control whose bar
encoded a wrong assumption; the plumbing controls passed (positive; calibration 0.5%
vs 3% bar; rank asserts; floors 100% valid), and the label machinery is intact with
caveats pre-stated. Binding language for Stage 2: "industry-controlled" means
"11-GICS-sector-MEAN-controlled" — nothing finer. No rerun, no re-verdict, no bar
adjustment: the mechanistically-correct control (sector-mean removal, verifiable as an
identity) cannot be swapped in post-hoc without exactly the tuning the process forbids.

## Research log (Phase 7)

- Verdict: FAIL on the industry control by a mis-set bar (43% vs 50%); mechanism
  diagnosed as pre-stated model coarseness (theme/sub-sector persistence), not
  pipeline malfunction.
- Supported: sector-mean removal (by construction, verified); factor persistence under
  industry projection (a_match 0.877); thin vetted panel (5 slots, 0 recurrent);
  screen calibration-consistency.
- Not supported: "detectable residual factors are sector risk" (refuted at 11-sector
  granularity); any provenance claim; label-3 prevalence as a leakage RATE (inflation
  caveats); the industry control's original bar as a meaningful test.
- Validity: descriptive; same 14 primary windows; sectors non-PIT (2023-03 GICS
  restructure backfilled pre-2023 windows); labels mean association w.r.t. THIS model.
- Next per decision rule + documented judgment: Stage 2 attribution with this panel,
  FAIL context carried; Stage-1 adversarial review runs alongside Stage-2 prereg
  review.
