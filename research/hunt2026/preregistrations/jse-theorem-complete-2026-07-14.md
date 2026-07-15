# Pre-registration — theorem-complete JSE: shrinkage calibrated by floor + rotation (eq. 13)

### EXP-2026-07-14-jse-theorem-complete

**Stage-0 + override note.** Kristen's call, 2026-07-14 (evening): she explicitly overrode
EXP-2026-07-14-jse-factor-gate's stop-iterating clause as repo owner, on the grounds that
the F-026 run predated material new information from the 2026-07-14 CDAR lab meeting
(vault: `14-Lab/meetings/2026-07-14 — portfolio variance (James-Stein + factor models).md`):
the complete Theorem-1/eq.-13 error decomposition
sin²∠(hⱼ,bⱼ) → δ²/(nλⱼ+δ²)  [floor, out-of-subspace]
              + (nλⱼ/(nλⱼ+δ²))·sin²∠(νⱼ,eⱼ)  [weight × in-subspace rotation],
where νⱼ are eigenvectors of the k×k factor-return Gram matrix, the rotation term is not
pointwise estimable but is Monte-Carlo-boundable from the assumed factor-return
distribution (Φ ~ t₆; Kristen's own lab assignment, Davis–Kahan route), and the floor is
Ethan's ℓ/θ observable-floor lane. This is registered as a NEW hypothesis (shrinkage
INTENSITY calibration), not a re-run of the F-026 gate grid; the override and the
cumulative trial accounting are recorded here so the ledger stays honest.

**Hypothesis** (one falsifiable sentence, mechanism included):
Blanket JSE under-shrinks: it rotates each eigenvector toward q by the floor-implied
ψ̂ⱼ = √(1 − floorⱼ) only, but eq. 13 says total misalignment is floorⱼ + ψ̂ⱼ²·rotⱼ, so
setting the shrinkage from the theorem-complete misalignment
ψ̃ⱼ = √(max(τ, 1 − floorⱼ − ψ̂ⱼ²·rot̄ⱼ)) — with rot̄ⱼ the Monte-Carlo mean of
sin²∠(νⱼ,eⱼ) under Φ ~ t₆ scaled to the sample factor strengths — lowers realized min-var
volatility, most where factors are near-degenerate (f4/f5), because that is where the
uncorrected rotation error concentrates (F-026's separation finding, made continuous).

**Known alternative mechanism (stated up front):** the JSE rotation target q (equal-weight)
is the market factor's target; factors 2–5 have population directions roughly orthogonal to
q, so shrinking them HARDER toward q could hurt even when the misalignment estimate is
right — magnitude-calibration with a wrong target. A worse-than-blanket result is evidence
for this, and the fix (per-factor targets) would be a separate future prereg, not a rescue
of this one.

**Layer touched** (exactly one) + registered baseline:
Layer B — estimator only, Estimator Lab machinery held fixed (same 138 months, same
point-in-time S&P panel, same minvar_weights, monthly rebalance, paired deltas). Matched
pair: the variant differs from blanket jse5 ONLY in per-factor shrinkage intensity
(ψ̃ⱼ replaces ψ̂ⱼ); same SVD, λ, D, δ̂², τ floor, rotation-toward-q construction.
Baselines: jse5 (blanket, direct parent), pca5 (context).

**Alpha type tag**: estimator

**Rotation Monte Carlo (frozen procedure):** per (month, window): ρ̂ⱼ = (sⱼ²/p)·ψ̂ⱼ²
(debiased per-factor signal strength, Lemma A.2′ normalization); draw R = 500 sims of
Φ (k×n) i.i.d. from the registered distribution, standardized to unit variance and scaled
by √ρ̂ⱼ; M̂ = ΦΦᵀ/n (k×k, rows demeaned); eigendecompose, order descending so column j
pairs with axis eⱼ; rotⱼ = 1 − (Wⱼⱼ/‖wⱼ‖)² (the lab's sin2_angle_to_axis convention,
re-implemented in alpha-lab — factor_lab code untouched); rot̄ⱼ = mean over R. Seeded
(seed=0), fully deterministic.

**Registered variants** (2, all reported):
Φ-distribution ∈ {t₆ (decisive — the lab's empirical choice), normal (robustness)},
both at k=5, R=500. Decisive cell: **long-only, n=63** (JSE's confirmed live regime).
Diagnostics (reported, not decisive): n=252 long-only; unconstrained at both windows.
Baseline gates before any variant counts: (a) rot̄ ≡ 0 through the same code path
reproduces blanket jse5 exactly; (b) recomputed holdout Sharpe of the frozen
pca_minvar_jse book matches published (tol 0.01) — same gates as F-026.

**Expected result** (numeric, on which evaluator):
Paired monthly realized-vol deltas over the 138 months. Unlike the F-026 gate, ψ̃ⱼ < ψ̂ⱼ
in EVERY month (rot̄ⱼ > 0 always), so the median is a live statistic — the F-026 design
lesson applied. Expected if the hypothesis is true: t₆ variant median paired delta
(theorem-complete − blanket) ≤ −0.3 bps vol, p < 0.05, with the improvement concentrated
in months where rot̄₄/rot̄₅ are largest; normal variant same sign, smaller. Expected if
the wrong-target alternative dominates: median ≥ +0.3 bps (worse), p < 0.05.

**Decisive statistic (pre-committed)**: on the decisive cell, for the t₆ variant:
median paired monthly delta (theorem-complete − blanket jse5) and paired t.
- "calibration helps" if median ≤ −0.3 bps AND p < 0.05;
- "wrong target" if median ≥ +0.3 bps AND p < 0.05 (evidence for the alternative
  mechanism — informative failure, goes to FAILURES.md with that reading);
- "flat" if |median| < 0.3 bps or p ≥ 0.05 — the calibration is a wash at S&P top-5
  factor strengths; FAILURES.md, program closes again.
Normal-variant and diagnostic cells inform the story only.

**Failure / kill condition** (pre-committed; stop-iterating):
One run of the 2 registered variants. No new rotation distributions, no R changes, no
per-factor target redesign, no k or window additions after seeing results. Any follow-up
(e.g., per-factor shrinkage targets) is a separate prereg requiring Kristen's Stage-0.
No live spec change from this run regardless of outcome; deployment remains gated by the
F-021 FINAL bar and a separate Stage-4.

**Trial-ledger row**: TRIAL_LEDGER.md — Robustness experiments table, same commit.
Cumulative accounting for the estimator-overlay line: 6 (F-026 gate configs) + 2 (this) =
8 registered chances since the program "closed"; this run stamps n_trials=2 and notes the
cumulative count.

**Derived from prior holdout results?** YES — adaptive loop: reacts to F-026 (separation
is the binding quality dimension; median-stat design lesson) and to F-021 FINAL (long-only
n=63 as the live regime). Additionally informed by NEW external information (2026-07-14
lab meeting), which is the stated basis for Kristen's override.

**factor_lab scope guard**: eq.-13 structure, ψ̂ form, and the sin²-to-axis convention are
cited from factor_lab docs/code (read-only); all implementation lives in
research/estimator_lab/. This experiment is NOT Kristen's lab deliverable to Alex (her
Davis–Kahan bound notebook) and must not be represented as it.

---
**Result** (filled after the run, never edited above this line): **WRONG TARGET
(informative failure)** by the pre-committed rule: decisive cell (long-only n=63, t6)
median +1.85 bps vs blanket, t=+2.64, p=0.0092 — worse, and worse in EVERY cell (both
distributions, both books, both windows; unconstrained +30–50 bps). Both gates passed
(rot=0 path == jse5 exactly; holdout Sharpe == published). The rotation diagnosis itself
validates (f1 ~0.02, f2–f5 0.13–0.55, t6 > normal, n=63 > n=252); the failure is the
response — extra shrinkage toward q collapses non-market factors toward the market
direction, with clean dose-response (more rotation estimate → more harm; direction-
sensitive book harmed 10–30x more). Empirical evidence that multifactor JSE requires
per-factor TARGETS (the lab arc's open step 4), not just intensity calibration.
FAILURES.md F-027; program returns to closed; cumulative overlay-line chances 8.
Full tables + story: research/estimator_lab/THEOREM_COMPLETE.md.
