# Real-data readiness memo + Phase 6 prereg — FF-residualized S&P residual factors

Written 2026-07-14 before any real-data code; revised same day after Statistical,
Implementation, and Quant reviews (all approve-with-changes; dispositions in Part C).
FROZEN as of this revision — no further design changes; anything post-run goes to the
Story section of FLOOR_REALDATA.md.

## Part A — data-readiness assessment

### A1. Universe and sample period
- Prices: `data/raw/daily_px_statarb_wide.parquet` — 1,103 tickers, daily adjusted
  closes (adjustment status verified pre-run by a split spot-check, see B-sanity),
  2018-01-02 → 2026-07-06 (2,137 rows).
- Factors: `data/raw/ff_factors_daily.parquet` — Ken French daily FF3 + MOM + RF,
  manifest-logged pull 2026-07-14, ends 2026-05-29 (binds the last window).
- Membership: `data/raw/sp500_pit.parquet` — point-in-time S&P 500 member lists,
  1996 → 2026-06, snapshots every ~9 trading days (238 since 2018). Snapshot staleness
  at window start costs < 1 name per window at ~25 changes/yr — negligible (quant review).
- Coverage caveat (measured): fraction of PIT members present as price columns rises
  386/506 (2018-06) → 438/505 (2021-06) → 478/503 (2024-06) → 501/504 (2026-06).
  The price panel was pulled on a recent universe, so **early windows are
  survivorship-tilted**. Mitigation: report per-window coverage; primary analysis
  restricted to windows with coverage ≥ 90% (≈ 2021 onward); earlier windows flagged.

### A2. p/n under candidate rolling windows
Usable p per window ≈ PIT members ∩ price columns ∩ data screens ≈ 440–500.
- n = 63 return obs (quarter): p/n ≈ 6.98–7.9. Near or above the validated C3 boundary;
  see the PER-WINDOW correction rule in the Procedure (correction only when realized
  p/n ≥ 7; low-coverage windows can fall in the 4–7 bend and then get the raw floor
  with an under-report flag — slack direction known from Phase 2).
- n = 126: p/n ≈ 3.5–4.0 → C3 OVERcorrects (validated failure mode); not used.
- n = 252: p/n ≈ 1.8 → outside everything; not used.
Choice: **n = 63**, non-overlapping windows. (p, n) matches the (500, 63) main sim cell
of Phases 3–5. Honesty note (stat + impl reviews): the match is in (p, n) ONLY — the
C4 cut and the n/(2p) slack law were calibrated on ISOTROPIC noise. Real residual
returns are cross-sectionally heteroskedastic; mitigation is vol-standardization (A5),
and if the negative control still fails, residual noise anisotropy is the PRE-STATED
expected mechanism (not plumbing).

### A3. Missing returns, zero returns, changing membership
- Within-window missingness among covered names is negligible (mean NaN fraction 0.4%
  over a sample 252d window; 478/478 names had ≤1 NaN).
- Screens per window: require complete returns over beta + analysis windows; drop names
  with zero variance or > 20% zero-return days in either window (stale/halted names).
  Counts reported per window, analysis-window drops separately from beta-window drops.
- KNOWN LOOK-AHEAD LIMITATION (impl review): requiring complete ANALYSIS-window returns
  conditions the universe on trading through the window — window-level survivorship.
  Accepted for this descriptive prototype; the separately-reported drop count bounds
  its size; carried in A8's CANNOT list context.

### A4. Point-in-time construction
Membership from the PIT snapshot at window start only. Betas and vol-standardization
constants come from the trailing window strictly preceding the analysis window — no
analysis-window information enters the known-factor model or the scaling. Prices are a
single recent pull, so corporate-action adjustment is as-of pull date — acceptable for
a descriptive diagnostic, noted as a limitation (not fully PIT prices).

### A5. Factors, exposures, standardization, residualization, timing
- Known factors: Ken French daily FF3 (Mkt−RF, SMB, HML) + MOM, k_F = 4, matching the
  sims' k_F = 4. Stock and factor returns both close-to-close same-day; no lag.
- Vol-standardization (impl-review blocking fix): each asset's excess returns are
  divided by its beta-window realized vol before beta estimation, residualization, and
  PCA. Restores approximate isotropy — the regime the C4/C3 calibrations assume — using
  only pre-analysis-window information.
- Exposures: per-asset time-series OLS (with intercept) of standardized excess returns
  on the 4 factors over the trailing 252 return days.
- Residualization: **cross-sectional projection** off col(B̂) each analysis day:
  E_t = (I − Q_B̂Q_B̂ᵀ)r̃_t. Per-asset time-series OLS residualization on the analysis
  window is PROHIBITED — it forces D_j ≡ 0 vs the estimated-factor regressors by
  construction. (Impl review verified algebraically that BOTH D_j variants below are
  non-degenerate under cross-sectional projection.)
- Detector-regressor deviation from Phase 4 (all three reviews): Phase 4 regressed on
  ESTIMATED factor returns; here the primary D_j regresses on the PUBLISHED FF series
  (the observable analogue of true factor returns). Phase-4/5 operating characteristics
  (AUC 0.98, FNR ≤ 0.07, FPR ≤ 0.12) are NOT claimed for this detector. Pre-committed
  secondary: D_j′ vs B̂-implied factor returns f̂_t = (B̂ᵀB̂)⁻¹B̂ᵀr̃_t, the bridge to the
  validated detector.
- Misalignment diagnostic (quant review, reported not gating): per adjacent window
  pair, the principal angles between col(B̂) — read next to the D_j distributions; D_j
  conflates beta sampling error with genuine beta drift and the real misalignment level
  was never mapped onto the sim's `mis` parameter.

### A6. Is the MP-edge / floor-calibration regime satisfied?
In (p, n): yes at n = 63 (see A2, per-window rule). In noise DGP: only after
vol-standardization, and imperfectly — anisotropy/heavy tails remain a named threat
adjudicated by the negative control (which preserves per-asset marginal distributions,
so it does test this). k_F/p ≈ 0.9% rank deficiency: negligible per Phase 1.

### A7. Interpreting leakage scores without oracle truth
No L_j exists. D_j is a continuous score (Phase-5 adjudication: provenance is mixed).
- Primary empirical null (impl review): per window, the 62 circular time-shifts of each
  x_j regressed on the real FF series — 310 null R² values per window, deterministic,
  preserving each series' marginal distribution and autocorrelation while breaking
  alignment. The k_F/n ≈ 0.063 level is reported for context only.
- Bucket boundaries (stat review — BOTH from the null, frozen): among screen-passers,
  D_j ≥ 99th percentile of the window's null → "material known-factor association";
  D_j < 75th percentile → "low known-factor association"; else "mixed". Screen-failers
  → "noise-like". The F-test (intercept, centered R², dof (4, 58)) is reported as a
  SECONDARY descriptive only; its iid assumptions are violated by vol clustering.
- INDUSTRY BLINDNESS (quant review): low D_j means low association with THESE 4 series
  only. Sector/industry structure is invisible to the detector by construction, and
  low-D residual factors on an FF-residualized S&P panel are EXPECTED to be largely
  sector risk. They must not be read as "risk beyond standard models" — a Barra-style
  industry model would absorb most of them. (Sector-proxy correlation check deferred —
  see Part C rejections; FF+industries, not FF5, is the relevant robustness extension.)
- High D_j is "high in-window linear association with the known-factor returns" (stat
  review) — the population risk-spanning reading is a HYPOTHESIS, listed under CANNOT.

### A8. Claims that can and cannot be made
CAN (descriptive): per-window screen-pass counts; distribution of (raw or corrected,
per the p/n rule) floors of screen-passers; D_j and D_j′ distributions vs the circular-
shift null; bucket counts; cross-window recurrence read net of the beta-window
dependence below.
CANNOT: that any factor IS genuine residual risk (no oracle); that low-D factors are
non-sector risk (industry blindness); that high-D factors are spanned by known risk in
population (in-sample R², 63 obs); anything causal; anything about portfolio
performance; that D_j equals Theorem 1's in-subspace rotation term.
DEPENDENCE (stat + quant reviews): adjacent windows share up to ~189 of 252 beta-window
days, so B̂ — hence buckets — is mechanically correlated across neighbors, and pooled
counts are not independent draws. Stability is additionally reported between windows
≥ 4 apart (disjoint beta windows) as the honest version.

### A9. Readiness verdict
Conditions met at n = 63 with the A1 coverage restriction, the A5 standardization, and
the per-window correction rule. Blocking-condition sim not required: the two design
risks (D_j degeneracy, heteroskedasticity) are resolved by construction (A5), with the
negative control as the empirical adjudicator and anisotropy pre-stated as the expected
failure mechanism. Proceed.

## Part B — Phase 6 prereg (FROZEN)

### Question
On real FF-residualized S&P daily returns, what fraction of extracted residual
statistical factors (k′ = 5 per window) fall into each bucket — noise-like / material /
low / mixed known-factor association — and what are the floor and D_j distributions of
the screen-passers?

### Data
As Part A. Non-overlapping 63-return-day analysis windows stepping back from
2026-05-29 (FF edge); trailing 252-return-day beta window each. Primary set = coverage
≥ 90%; earlier windows reported flagged.

### Procedure (observable only; one pass, no iteration)
Per window: universe (A3 screens) → vol-standardize by beta-window vol → betas (A5) →
cross-sectional residualization → dual-space PCA (sim conventions: W = YᵀY/(np), k′=5,
θ_j, ℓ = bulk mean, floor = ℓ/θ_j, SNR̂_j = θ_j/ℓ − 1) → C4 screen
(SNR̂ > 2√(n/p) + n/p + 0.5) → floor correction +n/(2p) IFF realized p/n ≥ 7, else raw
floor with under-report flag → D_j (primary, vs published FF; centered R²) and D_j′
(secondary, vs B̂-implied factor returns) → circular-shift null (62 shifts × 5 factors)
→ bucket per A7. Adjacent-window principal angles reported.

### Primary metrics
(1) Per-window bucket counts; (2) pooled floor distribution among screen-passers
(raw/corrected per rule, primary windows); (3) pooled D_j vs null-quantile exceedance
rates; (4) recurrence of buckets across windows, reported both adjacent and ≥ 4 apart.

### Sanity checks (pre-committed, run before the pipeline)
- Split check: flag |daily return| > 40% in the panel; spot-check NVDA (2024-06 10:1),
  AMZN (2022-06), GOOGL (2022-07) around their splits. Any unadjusted split found →
  fix the data before running, document in the report.
- Floors in [0, 1] by construction of ℓ/θ; corrected floors reported with the rule.

### Controls (pre-committed, numeric)
- POSITIVE (plumbing): pipeline WITHOUT residualization on the most recent window.
  Passes iff PC1 passes C4 AND centered R² of x₁ vs Mkt−RF alone ≥ 0.7.
- NEGATIVE (screen size): per-asset INDEPENDENT time-permutation of the residual panel
  (seeded, stamped) on every primary window. Passes iff screen-pass rate ≤ 10% of all
  k′ × (primary windows) factor slots. Preserves per-asset marginals, so a failure
  indicts anisotropy (pre-stated mechanism), not calendar plumbing.

### Verdict rule (exhaustive — every run lands in exactly one)
- FAIL: either control fails its numeric bar.
- SUCCESS: both controls pass AND ≥ 95% of screen-passer floors (primary windows) are
  finite, non-NaN, in [0, 1].
- AMBIGUOUS: both controls pass, the floor-validity condition fails.
No bucket-composition condition: all-noise-like is a legitimate market answer, not a
pipeline failure (stat review).

### Decision that follows
SUCCESS → descriptive write-up + story; next fork (FF+industry known model vs
consolidate-and-stop) goes to Kristen — research-direction choice. FAIL → mechanism
diagnosis memo addendum before any rerun; no threshold tuning. AMBIGUOUS → report
as-is, adversarial review before any interpretation.

### Multiplicity / dependence note
Bucket calls use empirical-null quantiles, so the expected "material" rate under the
global null is 1% of slots BY CONSTRUCTION (the 99th-percentile cut), before accounting
for cross-window dependence through shared beta windows, which makes effective
multiplicity lower than the slot count. Parametric-α arithmetic is not used.

### Reproducibility (stamped via stamp_run + CSV)
Git SHA; SHA-256 of the three input parquets; FF pull manifest row; permutation seed;
window boundary dates, per-window universe hash + coverage + p + drop counts (CSV
columns); k′, α-quantiles, C4 formula, correction rule in params.

## Part C — review dispositions

All findings incorporated as above, EXCEPT (documented rejections):
1. Cheap heteroskedastic pre-sim (stat review, offered as one of two alternatives):
   superseded by adopting the other alternative — vol-standardization + pre-stated
   anisotropy mechanism + the negative control as adjudicator.
2. Sector-proxy correlation for low-D factors (quant review, optional): deferred —
   needs a GICS mapping not in-repo; the A7 industry-blindness caveat carries the
   interpretive load; candidate first step of the FF+industry robustness arm.
3. Mid-window entrant/delisting inclusion with fill rules (impl review, option 1):
   took option 2 (exclude + report counts + label as look-ahead limitation) — fill
   rules would put imputed numbers into a spectrum-sensitive pipeline.
4. PIT snapshot-gap audit column (quant review, optional): skipped, impact bounded
   < 1 name/window.
