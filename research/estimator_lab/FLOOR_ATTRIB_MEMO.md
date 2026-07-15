# Stage 2 prereg (rev 2, FROZEN) — alpha-book attribution vs known / industry / vetted-residual risk

Written 2026-07-14 before attribution code; rev 2 after the three-reviewer round
(statistical / implementation / backtest-integrity, all approve-with-changes) and the
Stage-1 adversarial corrections (FLOOR_INDUSTRY.md errata). Dispositions in Part C.

Inherited Stage-1 caveats (BINDING): label-4 slots mean "not explained by FF3+MOM + 11
GICS sector MEANS" — not "not industry risk" (sub-sector structure survives by
construction); the label-4 gate is exclusion-biased, the panel is UNDER-COMPLETE, and
per the adversarial errata its evidential value for control purposes is ≈ nil (5 slots,
4/14 windows, 0 recurrent, exact-permutation p 0.21–0.51, floors ~6%-corrected).
"Industry-controlled" here ALWAYS means "11-GICS-sector-MEAN-controlled". The Stage-1
"not sector risk" reading is downgraded to "not annihilated by sector-mean projection"
(random-projection a_match null 0.991 vs observed 0.877).

## Question
For each live hunt2026 book, does its return survive controls for (1) known factors,
(2) sector means, (3) the thin vetted residual panel — and what honest classification
follows?

## Books (7 live ledgers, frozen specs 2026-07-10) — with provenance (STATUS.md,
TRIAL_LEDGER.md, FAILURES.md; carried into the final memo's table)
| book | tier | provenance flags |
|---|---|---|
| vol_managed_qqq | promoted L3 | hunt-1 |
| vol_core_svxy | promoted L3 | hunt-1; SVXY ETP-menu survivorship (post-2018 deleveraged product) |
| trend_vol_qqq | promoted L3 | hunt-2 ADAPTIVE loop |
| defensive_ensemble | promoted L3 | hunt-2 ADAPTIVE loop |
| momentum_concentrated | sleeve-only | WF-demoted (F-015, −4.6pp median excess); only stock book — heaviest survivorship |
| dual_momentum_gem | watch/retired-to-forward | whipsaw-fragile |
| dual_momentum_gold | watch | HINDSIGHT-DISCOUNTED (gold-menu design hindsight; regime artifact per robustness probe) |

## Return series & honesty warnings
Harness-reconstructed net daily returns (weights at close t earn t+1; net of 10/2 bps
per side; gross capped 2.0). Warnings on every output:
(a) SELECTION: pre-freeze history is selection-tainted. n_trials = 18 is a REGISTERED-
    TRIAL FLOOR — TRIAL_LEDGER.md says effective N > 18 (hunt-2 books came from an
    adaptive loop) — so any deflated-Sharpe probability is an UPPER bound. Sensitivity
    pair mandated: DSR at N=18 AND N=36; rule 5 requires ≥ 0.5 at BOTH.
(b) SPAN: all classification statistics use ONLY the 14 Stage-1 primary windows —
    window-starts 2022-11-21 → 2026-03-02, each 63 return days on the statarb∩FF
    calendar, ending 2026-05-29 (span corrected in rev 2; rule-0 cutoff = 2022-11-21).
    Live OOS (post-2026-07-10) and any other dates NEVER enter any classifying
    statistic; context-only stats must carry their endpoint label.
(c) SURVIVORSHIP (decomposed): heaviest on momentum_concentrated L1/L2 LEVELS (only
    stock book; delisted losers absent from the recent yfinance panel inflate
    momentum); ETF books largely levels-immune; SVXY ETP-menu survivorship noted;
    composition estimates partially protected (panel-derived regressors share the tilt).
(d) FINANCING: harness models no financing. MANDATED (formula reused from the sibling
    prereg, research/hunt2026/preregistrations/factor-attribution-2026-07-14.md):
    alpha_stress = alpha − max(avg_gross − 1, 0) × (mean RF + 0.50%/yr), reported next
    to EVERY alpha; rule 5 additionally requires L4 alpha_stress > 0.
(e) Attribution measures factor COMPOSITION of the track record (more selection-robust
    than the alpha LEVEL — selection biased which rules were examined, not each rule's
    exposure); alpha levels inherit selection bias. Both reported, so labeled.
(f) SIBLING EXPERIMENT: the hunt2026 blind-window attribution prereg above runs a
    parallel classification (different models/spans; not yet run). Doubled-look
    multiplicity acknowledged. Adjudication pre-committed: THIS memo's ladder is
    authoritative for the program's final memo; if the sibling runs, both labels are
    reported side by side and disagreements flagged, never averaged.

## Attribution design (frozen)
Per book × window (window VALID iff all 63 dates have book net return and RF; assert):
excess = net − RF. L1 = window mean. L2 = OLS intercept on [Mkt−RF, SMB, HML, Mom].
L3 = + the 11 Stage-1 sec_ret series EXACTLY as Stage 1 computed them (EW standardized
excess returns of the window's screened PIT universe, pre-residualization; regenerated
deterministically with the univ_hash assert). L4 = + that window's arm-B label-4 x_j
series (regenerated the same deterministic way; the 5 (window, pc) slots of
floor_industry.csv). Windows without label-4 slots: L4 := L3 (counted, reported).
lstsq throughout; per-window design condition numbers reported. dof: worst realized
case 18 params on 63 obs (window 2023-05-24).
- KNOWN DEGENERACY (pre-stated): with this panel, L4 ≈ L3 in 10/14 windows;
  classification rule 4 CANNOT fire (its ≥7-window gate is known-unmet); the L4 column
  carries the annotation "controls applied in 4/14 windows — spot-checks, not residual-
  control robustness; L4 survival is NOT evidence of absence of residual common risk."
  Same-window-estimated x_j regressors mechanically attenuate L4 alpha in covered
  windows (in-sample absorption): attenuation there is an UPPER bound on true
  absorption and will not be read as evidence of hidden residual risk.
- Aggregation & significance: mean window alpha; SIGN-FLIP PERMUTATION engine (10,000
  draws, flip signs of window alphas jointly ACROSS BOOKS to preserve cross-book
  correlation; exact under symmetry): p_k = fraction of draws with |mean| ≥ observed.
  "Significant" = p ≤ 0.05 AND same-sign share of windows ≥ 60% (sign of the MEAN
  defines direction; all tests two-sided via |mean|). The permutation run also yields
  the EXPECTED count of false rule-5 classifications under the joint null, reported
  next to the observed count (multiplicity line, mandated).
- Vol-ETP override (frozen): ρ = Pearson correlation of the POOLED concatenation of
  per-window L3 residuals (14 × 63 obs) vs SVXY close-to-close adjusted returns from
  the hunt panel minus RF on the same dates (assert zero missing). ρ ≥ +0.5 →
  "known-premium (VRP harvesting)"; ρ ≤ −0.5 → noted "long-vol / VRP-paying" (same
  class, direction noted). vol_core_svxy is EXPECTED to trip this by construction.
- Stability: calendar halves (first 7 / last 7 windows) and SPY-realized-vol median
  split; "promising" requires same-sign L4 alpha in both halves.
- Suppression path (L2 not significant but L3 significant) flagged descriptively if it
  occurs.

## Classification ladder (first match wins; t/p from the permutation engine)
0. insufficient-evidence: < 10 valid windows, or cross-window L1 |t| < 1.
1. known-premium-VRP: |ρ_SVXY| ≥ 0.5 (direction noted).
2. known-factor-premium: L1 significant, L2 not.
3. industry-sector-exposure: L2 significant, L3 not. (Means SECTOR-MEAN exposure.)
4. hidden-residual-risk-exposure: L3 significant, L4 not, AND ≥ 7 windows with ≥ 1
   label-4 control — KNOWN UNREACHABLE with this panel; retained for future panels.
5. promising-but-unproven-residual-alpha: L4 significant AND same-sign both halves AND
   DSR ≥ 0.5 at BOTH N=18 and N=36 AND L4 alpha_stress > 0. Carries the sparse-controls
   annotation verbatim. Never upgraded past "unproven."
6. insufficient-evidence (fall-through).

## Controls (split verdicts per review)
- bench_qqq_buyhold ladder: PLUMBING passes iff |t₂| < 2 (given L2 ran) AND per-window
  median market beta ∈ [0.9, 1.2] AND median L2 R² ≥ 0.9. If its L1 |t| < 1, the
  control is "uninformative" (verdict AMBIGUOUS-CONTROL), NOT a plumbing FAIL.
- SPY null book (harness spy_benchmark): must classify to labels 0/1/2, never 4/5
  (label 3 also acceptable-benign if it fires; flagged).

## Verdict rule (exhaustive)
FAIL: plumbing control fails. AMBIGUOUS-CONTROL: benchmark uninformative. SUCCESS:
plumbing passes AND ≥ 5 books have ≥ 10 valid windows. AMBIGUOUS: otherwise.

## Repro stamp (stamp_run, n_trials = 18)
git SHA; SHA-256 of: ff_factors_daily.parquet, daily_px_statarb_wide.parquet,
sp500_pit.parquet, sp_composite_named.parquet, floor_industry.csv, the 7 spec dirs +
bench_qqq_buyhold (dir content hashes), hunt sandbox_meta.json; the 5 label-4
(window, pc) ids; permutation seed; all thresholds; memo pointer.

## Part C — dispositions (all three reviewers + Stage-1 adversarial conditions)
Accepted: span correction (impl blocking); L4-degeneracy pre-statement + rule-4
unreachability + sparse-controls annotation (stat blocking, impl, integrity); DSR floor
language + N=18/N=36 sensitivity gate (stat blocking, integrity); financing
alpha_stress formula + rule-5 gate (integrity blocking); |t| semantics → two-sided
sign-flip permutation engine + joint false-promising expectation (stat); same-window
x_j attenuation direction pre-stated (stat); SVXY override frozen pooled-882-obs
definition + directional note + vol_core_svxy expectation (stat, impl); per-book
provenance table (integrity); survivorship decomposition (integrity); full-span
definition → classification uses windows only (integrity); sibling-experiment
cross-ref + adjudication + doubled-look note (integrity); repro stamp clause (impl);
window-validity definition + asserts (impl); sector-series and x_j regeneration pinned
to Stage-1 machinery (impl); positive-control split verdict + plumbing asserts (stat,
impl, integrity); suppression-path flag (stat); Stage-1 adversarial conditions (a)–(d)
adopted (binding language, no theme-identity reliance, corrected floors via rerun,
panel-as-spot-checks).
Rejected/deferred: none material; block-wise permutation variant (stat, optional)
deferred — plain sign-flip retained with the beta-window dependence caveat carried.
