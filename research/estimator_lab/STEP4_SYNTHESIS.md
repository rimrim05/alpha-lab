# Step-4 (multifactor JSE) — what the estimator lab settled, 2026-07-14

Empirical exploration of the Goldberg group's open "step 4" (generalize the single-factor
James-Stein eigenvector correction to k factors), run on real S&P panels (PIT membership,
walk-forward, unconstrained min-var realized vol). Four candidate avenues from a design
sweep; each tested and closed. All code in research/estimator_lab/; factor_lab untouched.

## The scoreboard

| # | avenue | result | ref |
|---|---|---|---|
| — | **DIAGNOSIS: min-var is a subspace functional** | **CONFIRMED**, vol invariant to within-subspace frame rotation (CV 1.4%), sensitive to the subspace P (+26%); pure projector w∝(I−P)1 within 1.9% of full | EXP-subspace-invariance, CONFIDENCE_LADDER |
| 1 | eigenvalue-only shrinkage | DEAD, target-free but fixes the error min-var is insensitive to; the group already published "little value vs JSE" in this regime | (subagent memo; Goldberg-Kercheval) |
| 2 | subspace averaging (target-free variance reduction) | NO EFFECT / net HARMFUL, the subspace disagreement is DRIFT not noise; averaging blurs drifted subspaces | F-030 |
| 3 | rotation-bound robust min-var (per-factor trust) | HARMFUL, acting on the within-subspace rotation raises vol, monotone in intensity | F-031 |
| 4 | external anchors (Barra/FF / long-window) | untested; FF alignment weak, long-window-anchor is drift-relevant (see below) | (subagent memo) |

## The single conclusion the data forces

**The rotation bound, Theorem 1's hard in-subspace-rotation term, the object of Kristen's
Davis-Kahan/t₆ assignment, has no positive value for minimum-variance portfolios.** Proven
from two independent directions:
- *Ignoring it is free* (subspace-invariance: min-var doesn't use the within-subspace directions).
- *Acting on it costs* (F-031: hedging against it distorts the covariance and raises realized vol).

So min-var needs the **subspace projector P and the eigenvalues** estimated well, not the
individual eigenvector directions. That much is a solved reframing.

## What actually limits multifactor min-var (the real open problem)

F-030 localized the residual error: the single-window subspace estimate P̂ is not
variance-limited (which averaging would fix), it is **drift-limited**. The factor subspace
genuinely moves month to month (the k-th eigenvalue of the L-window projector mean drops to
0.30–0.45 in the multi-factor short-window regime), and every target-free / robustness tool
tested either ignores drift (harmless at best) or worsens it (averaging, robustness).

**Distilled step-4 problem: a drift-aware subspace estimator**, de-bias/track the subspace
projector P over time under a model of its drift, rather than shrinking eigenvectors toward a
target (no valid target exists) or averaging (drift ≠ noise). None of the standard
shrinkage/robustness machinery addresses a moving subspace. The two untested leads that are
drift-relevant: Avenue 4's long-window anchor (a lower-drift-variance reference for P) and an
explicit state-space / smoothing model of P_t. Both are new preregs.

## Honest note for the lab

Kristen's rotation-bound work (the Davis-Kahan/t₆ Monte Carlo) is correct and its DIAGNOSIS
validated on real data (F-027: f1 clean ~0.02, f2-5 rotated 0.13–0.55, t₆>normal, n=63>n=252).
This program shows only that the bound is not the *min-var* lever, its value is in
understanding/quantifying the error, or for a downstream objective other than min-var. Worth
knowing before investing more compute in it as a portfolio tool.
