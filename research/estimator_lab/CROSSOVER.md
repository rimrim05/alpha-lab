# EXP-EST-CROSSOVER — JSE benefit vs window length n, and does ψ̂ predict it? (run 2026-07-10)

jse3 vs pca3 matched pair, 138 months (2015-01 → 2026-06, identical month set for all n:
every month requires 252d history), PIT S&P 500 members, 5% cap, one-month holds.
Per-month data: `crossover.csv` (paired vols both books + per-factor ψ̂, eigengap, p/n,
all computed from the estimation window only). Runner: `run_crossover.py`.
Prereg: `../hunt2026/preregistrations/est-crossover-2026-07-10.md`.
Consistency: the n=63 and n=252 endpoints reproduce the prior standalone runs
(63: −2.0 bps t=−6.0 both times; 252: −0.5 t=−7.4 here vs −0.6 t=−8.2 on the 137-month set).

## Crossover table (paired Δ = jse3 − pca3 realized next-month ann. vol, bps)

| n | p/n | median ψ̂_med | long-only Δ | t | p | unconstrained Δ | t | p |
|---|---|---|---|---|---|---|---|---|
| 42 | 10.6 | 0.925 | **−2.6** | −5.4 | <0.0001 | +49 | +6.6 | <0.0001 |
| 63 | 7.0 | 0.948 | **−2.0** | −6.0 | <0.0001 | +37 | +8.1 | <0.0001 |
| 90 | 4.9 | 0.960 | **−1.4** | −5.4 | <0.0001 | +32 | +8.5 | <0.0001 |
| 126 | 3.5 | 0.970 | **−1.0** | −5.8 | <0.0001 | +27 | +9.3 | <0.0001 |
| 189 | 2.3 | 0.978 | **−0.7** | −5.9 | <0.0001 | +22 | +9.5 | <0.0001 |
| 252 | 1.8 | 0.983 | **−0.5** | −7.4 | <0.0001 | +18 | +9.7 | <0.0001 |

**Headline: there is no crossover.** Long-only JSE helps at EVERY n, always significant;
the benefit decays monotonically (−2.6 → −0.5 bps) but never crosses zero. Unconstrained
JSE hurts at every n, also monotone, worst at small n (+49 bps at n=42). The two books
are mirror images: the same rotation that stabilizes a long-only book amplifies noise
whenever shorts let the weights follow the perturbed eigenvectors.

The long-only benefit is close to linear in p/n: Δ ≈ −0.24 bps per unit p/n
(in-sample fit across the 6 points; −2.6 at p/n≈10.6, −0.5 at 1.75).

Context (mean realized vol, %): long-only is flat in n (11.85–11.96 for both estimators);
unconstrained pca3 *degrades* as n grows (11.71 → 13.08), so short windows are not
penalized in level, only in the JSE delta.

## Predictor test (the real prize) — ψ̂ predicts the regime, not the month

Pooled across all 6×138 month-configs (state from the estimation window only):

| book | Δ vs ψ̂_med | Δ vs eigengap | Δ vs p/n |
|---|---|---|---|
| long-only | ρ = +0.177, p = 3.1e-07 | ρ = +0.03, p = 0.32 | ρ = −0.183, p = 1.1e-07 |
| unconstrained | ρ = −0.189, p = 4.2e-08 | ρ = +0.09, p = 0.009 | ρ = +0.175, p = 4.0e-07 |

The pooled correlation is significant in the pre-registered direction, but it is
**entirely the across-n effect**. Within each fixed n, ψ̂_med has zero predictive power
for the month's delta (Spearman ρ ∈ [−0.01, +0.09], all p > 0.3, six out of six).
The per-n ψ̂_med distributions barely overlap (n=42 spans 0.876–0.970; n=252 spans
0.968–0.992), so pooled ψ̂ is just an observable re-parameterization of p/n.
Eigengap adds nothing (long-only p = 0.32).

### Pre-committed thresholds (0.90 / 0.95) — both rejected as stated

| bucket | N | mean Δ (bps) | t | hit rate (Δ<0) |
|---|---|---|---|---|
| ψ̂_med < 0.90 | 26 | −0.4 | −0.3 (n.s.) | 65% |
| 0.90 ≤ ψ̂_med < 0.95 | 209 | −2.5 | −7.9 | 73% |
| ψ̂_med ≥ 0.95 | 593 | −1.0 | −11.0 | 77% |

- "ψ̂ < 0.90 → JSE helps": the bucket is 26 configs (25 of them n=42, mostly calm
  2017–2018 / 2023–2025 months where a 42d window sees weak factor signal-to-noise);
  mean Δ is negative but insignificant and SMALLER than the rest. Rejected.
- "ψ̂ ≥ 0.95 → no improvement": still −1.0 bps at t=−11. Rejected: JSE keeps helping
  (slightly) even at ψ̂ ≈ 0.98.
- In-sample threshold scan (color only, never a finding): best X = 0.94, mean −2.5 bps
  over 167 configs, hit 70.7%: barely different from "always apply".

## Verdict vs pre-registration

| expectation | outcome |
|---|---|
| long-only helps for n ≤ ~90 | **Confirmed** (−2.6 to −1.4 bps, t ≥ 5.4) |
| neutral by 126–189, harmless-to-worse at 252 | **Rejected** — never neutral, never worse; −1.0/−0.7/−0.5 bps, all p < 0.0001 |
| monotone in n | **Confirmed** (6/6 ordered, both books) |
| unconstrained ≥ pca at all n, worst at small n | **Confirmed** (+18 to +49 bps) |
| pooled Spearman(Δ, ψ̂) > 0, significant | **Confirmed formally** (ρ=+0.177, p=3e-07) — but entirely across-n; within-n content is zero |
| ψ̂<0.90 helps / ψ̂≥0.95 none | **Both rejected** (table above) |

**Kill condition: NOT triggered**: (a) long-only significant at every n, (b) pooled
Spearman significant. But the interesting half of the hypothesis dies anyway: ψ̂ has no
month-level timing content. The deployable rule is book- and window-level, not month-level:

> **Apply JSE in long-only min-var at any window length; expected benefit ≈ −0.24 bps of
> realized vol per unit p/n (so it only pays meaningfully when p/n ≳ 5, i.e. n ≤ ~90 on a
> ~470-name book). Never apply it unconstrained.** A month-level ψ̂ gate adds nothing over
> "always on": hit rates are 65–77% everywhere because the delta is negative on average
> everywhere in long-only.

Honesty labels: the −0.24 bps/(p/n) slope and the X=0.94 scan are in-sample descriptions
of this one panel; the six windows and the 0.90/0.95 cuts were pre-registered, everything
else in this file is reporting.

Runtime: ~3 min single-core for 6 windows × 138 months × 2 books.
