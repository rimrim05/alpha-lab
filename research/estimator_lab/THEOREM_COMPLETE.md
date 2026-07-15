# Theorem-complete JSE — eq.-13-calibrated shrinkage (EXP-2026-07-14-jse-theorem-complete)

psi_tilde_j = sqrt(max(tau, 1 - floor_j - psi_hat_j^2 * rotbar_j)); rotbar from seeded MC (R=500) of the k x k factor Gram under the registered distribution, scaled to sample factor strengths. Matched pair vs blanket jse5. Decisive cell: long-only n=63, t6 variant. Prereg: preregistrations/jse-theorem-complete-2026-07-14.md.

## Rotation MC means per factor (median across months, n=63)

| dist | f1 | f2 | f3 | f4 | f5 |
|---|---|---|---|---|---|
| t6 | 0.019 | 0.192 | 0.449 | 0.547 | 0.396 |
| normal | 0.016 | 0.130 | 0.370 | 0.483 | 0.356 |

## n=63 long_only — 138 months

| variant | med Δ vs jse5 (bps vol) | mean Δ | paired t | p | med Δ vs pca5 |
|---|---|---|---|---|---|
| tc_t6 **(decisive)** | +1.85 | +5.93 | +2.64 | 0.0092 | +1.25 |
| tc_normal | +1.25 | +5.25 | +2.43 | 0.0164 | +0.33 |

## n=63 unconstrained — 138 months

| variant | med Δ vs jse5 (bps vol) | mean Δ | paired t | p | med Δ vs pca5 |
|---|---|---|---|---|---|
| tc_t6 | +29.76 | +49.98 | +7.26 | 0.0000 | +51.48 |
| tc_normal | +24.30 | +34.38 | +6.94 | 0.0000 | +46.23 |

## n=252 long_only — 138 months

| variant | med Δ vs jse5 (bps vol) | mean Δ | paired t | p | med Δ vs pca5 |
|---|---|---|---|---|---|
| tc_t6 | +0.53 | +1.01 | +6.43 | 0.0000 | +0.34 |
| tc_normal | +0.22 | +0.52 | +4.36 | 0.0000 | +0.06 |

## n=252 unconstrained — 138 months

| variant | med Δ vs jse5 (bps vol) | mean Δ | paired t | p | med Δ vs pca5 |
|---|---|---|---|---|---|
| tc_t6 | +8.28 | +10.67 | +10.36 | 0.0000 | +20.61 |
| tc_normal | +6.63 | +8.74 | +9.99 | 0.0000 | +17.98 |

## Verdict (pre-committed rule, decisive cell): **WRONG TARGET (informative failure)**

## Story

- **The diagnosis is right; the response is wrong.** The rotation MC says exactly what the theorem predicts: f1 is nearly clean (rot ~0.02) while f2-f5 are heavily rotated (0.13-0.55), more under t6 than normal (the fourth moment drives Gram wobble), more at n=63 than n=252. That part validates. The failure is the JSE *response*: shrinking harder toward q.
- **q is the market factor's target.** Rotating f2-f5 further toward the equal-weight direction pushes several eigenvectors toward the SAME vector, collapsing the factor block toward multiple copies of the market — a structurally worse covariance even when the misalignment estimate is correct. Dose-response evidence on all four cells: t6 (larger rotbar) hurts more than normal, and the direction-sensitive unconstrained book is hurt 10-30x more (+30-50 bps) than long-only (+1-6 bps).
- **What this means for the program:** intensity calibration via eq. 13 is not wrong in principle — it is starved of the one thing the single-factor machinery cannot provide: a per-factor shrinkage TARGET for the non-market factors. That is precisely step 4 of the lab's research arc (multifactor JSE, the open next-paper problem). This experiment is empirical evidence from a real panel that the multifactor generalization cannot be target-free; worth bringing to Alex/Lisa as motivation.
- Cumulative overlay-line accounting: 8 registered chances since F-021 FINAL closed the program (6 gate configs + 2 here); best outcome across all 8 remains 'tiny help, far below any deployment bar'. The program closes again. Any per-factor-target design is a NEW prereg requiring Kristen's Stage-0 — not a rescue of this one.
