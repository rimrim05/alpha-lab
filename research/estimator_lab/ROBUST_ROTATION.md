# Rotation-bound robust min-var — per-factor trust (EXP-2026-07-14-robust-rotation-socp)

Σ_rob down-weights factor j's confident loading by cos²θ_j and inflates off-factor cross-risk by λ_j sin²θ_j; sin²θ_j = MC rotation bound (κ scale). Unconstrained min-var, paired monthly realized vol vs raw PCA (full). Decisive: large n63 k5, κ=1. Prereg: preregistrations/robust-rotation-socp-2026-07-14.md.

| universe | n | months | pf(κ=1) vs full | uniform vs full | pf vs uniform | lw vs full | rot spread |
|---|---|---|---|---|---|---|---|
| large | 63 | 99 | +10.36% (0.003) | +28.41% (0.000) | -12.07% (0.000) | -2.76% (0.078) | 0.49 |
| large | 252 | 90 | -10.34% (0.000) | +0.31% (0.733) | -8.94% (0.000) | -3.33% (0.006) | 0.24 |
| mid | 63 | 99 | +31.34% (0.000) | +60.43% (0.000) | -17.04% (0.000) | +3.56% (0.070) | 0.53 |
| mid | 252 | 90 | +6.20% (0.188) | +29.16% (0.000) | -18.96% (0.000) | +3.69% (0.523) | 0.34 |
| small | 63 | 99 | +48.07% (0.000) | +72.17% (0.000) | -15.57% (0.000) | +8.63% (0.001) | 0.57 |
| small | 252 | 90 | +15.03% (0.001) | +44.93% (0.000) | -22.83% (0.000) | -3.69% (0.034) | 0.47 |

## Decisive cell (large-cap, n=63, k=5, κ=1)

- (A) rob_perfactor vs full: +10.36% (p=0.003)
- (B) rob_perfactor vs uniform: -12.07% (p=0.000)
- κ-curve (pf vs full median): κ=0.5: +4.43%, κ=1.0: +10.36%, κ=2.0: +15.94%  → best κ=0.5
- median rotation-bound spread (max−min over factors): 0.49 (large ⇒ per-factor θ genuinely varies — the novelty precondition holds)

## Verdict (pre-committed rule): **HARMFUL**

## Story (this closes the step-4 loop)

- **Acting on the rotation bound HURTS min-var** — decisive cell +10.4% vol (p=0.003), harmful in 5 of 6 cells (up to +48% small-cap n=63), and monotone in κ (κ=0.5 +4.4% → κ=2 +15.9%): more robustness = more harm, so κ→0 (=raw PCA) is best. The rotation-bound distrust is pure cost. (One exception: large-cap n=252, the well-conditioned long-window regime, where a gentle correction acts like mild shrinkage and helps −10% — but that is not the HDLSS regime the program targets, and Ledoit-Wolf also helps there.)
- **Per-factor beats uniform everywhere (−12% to −23%, all p<0.001)** — trusting the well-estimated market factor and distrusting only the weak ones is far better than distrusting all factors equally. So the bound's per-factor structure IS informative about *where* to place distrust; it's just that placing ANY distrust on the within-subspace rotation costs realized vol.
- **This closes the loop with subspace-invariance, from the opposite side.** That experiment showed the within-subspace rotation is HARMLESS to min-var (ignoring it is free); this one shows it is HARMFUL to act on (hedging against it distorts the covariance and raises vol). Two independent directions, one conclusion: **the rotation bound — Theorem 1's hard term, Kristen's Davis-Kahan/t₆ object — has no positive min-var value.** min-var needs the subspace + eigenvalues right; the within-subspace rotation is neither recoverable nor useful for this objective.
- **Where that leaves step 4** (see STEP4_SYNTHESIS.md): all three tractable constructive avenues are now ruled out on real data — eigenvalue shrinkage (Avenue 1, already-published dead), subspace averaging (Avenue 2 constructive, F-030: killed by drift), rotation-bound robustness (Avenue 3, this: harmful). The one confirmed positive is the DIAGNOSTIC (min-var is a subspace functional), and F-030 localized the residual error to subspace DRIFT. The distilled open problem is a **drift-aware subspace estimator** — none of the standard shrinkage/robustness tools address a moving subspace, which is what the data says actually limits multifactor min-var.
