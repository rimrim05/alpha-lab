# JSE_BOUNDARY_MAP — where the Goldberg/JSE dispersion-bias correction beats raw PCA (2026-07-10)

**Branch:** Estimator alpha, NOT market alpha. JSE and PCA see identical information; JSE
differs from PCA *only* by the ψ̂ rotation of each factor eigenvector toward the equal-weight
direction q (`estimators._pca_parts`). Any JSE win is a **better covariance estimate → lower
realized portfolio risk**, not an independent forecast of returns. Highest evidence level
reachable here is **Level 2 (residual/estimator improvement)**; it is not and cannot be a
market-forecast claim. Paper-only, min-var risk metric, never a return headline.

This file **synthesizes** the already-run experiments; it does not re-run anything. Sources:
`RESULTS.md`, `CROSSOVER.md`, `PLAN.md`, `estimators.py`, `run_minvar.py`, `run_crossover.py`,
`{summary,summary_w63,crossover}.csv`, and hunt2026 `FAILURES.md` F-010 / F-020 / F-021 (+ its
three follow-up entries). Where a doc and the CSV/code disagreed, the CSV/code won (noted inline).

---

## 1. The estimator, stated as a rotation

For factor i: ψ̂ᵢ² = max(τ, 1 − p·δ²/σᵢ²), τ=0.01, δ² = mean idiosyncratic residual variance,
σᵢ² = i-th singular value². The eigenvector hᵢ is rotated toward q = 1/√p so that its projection
onto q grows by 1/ψ̂ᵢ (`estimators.py:35-40`). Consequences that pin the whole boundary:

- **ψ̂ → 1 ⇒ JSE → PCA.** When the top factors are strong relative to idiosyncratic noise
  (large σᵢ², small p·δ²/σᵢ²), ψ̂ ≈ 1 and the rotation is a no-op. The correction only exists
  when ψ̂ is meaningfully below 1.
- **ψ̂ is a deterministic function of (p, n, spectrum),** available from the estimation window
  *before* portfolio construction, so it is a legitimate candidate state variable (tested in §4).
- **A significant JSE−PCA delta is by construction proof that ψ̂ < 1 that month.** No separate
  mechanism check is needed; the delta *is* the mechanism.

---

## 2. The boundary, one table

Paired jse−pca realized next-month ann. vol (negative = JSE helps). k=3 unless noted.
All rows are pre-registered runs, verified by independent re-run at the n=63/252 endpoints.

| axis | regime | JSE vs PCA | evidence |
|---|---|---|---|
| **constraint = long-only** | any n | **helps**, monotone in p/n, always p<0.0001 | CROSSOVER.md; summary*.csv |
| **constraint = unconstrained (shorts, |w|≤5%)** | any n | **hurts**, +18→+49 bps, worst at small n | CROSSOVER.md; summary*.csv |
| **n (window), long-only** | 42 / 63 / 90 / 126 / 189 / 252 | −2.6 / −2.0 / −1.4 / −1.0 / −0.7 / −0.5 bps | crossover.csv |
| **k (factors), n=252 unconstr.** | 1 / 3 / 5 | +31 / +18 / +14 bps (gap *shrinks* in k) | RESULTS.md §"pre-registered test" |
| **k, n=252 long-only** | 1 / 3 / 5 | +0.0 / −0.6 / −0.5 bps (k=1 is pure noise) | RESULTS.md; F-010 |
| **p/n ratio, long-only** | 1.8 → 10.6 | benefit ≈ −0.24 bps per unit p/n (in-sample slope) | CROSSOVER.md |

**Reading:** the sign of the JSE effect is set by the **book (constraint), not the window.**
Long-only: always a small help. Unconstrained: always a hurt. n only modulates *magnitude*
within each book, via p/n.

---

## 3. Why the constraint flips the sign (mechanism)

Same rotation, opposite outcome, because the two books respond differently to a perturbed
eigenvector:

- **Long-only** (`run_minvar.py:42-44`, negatives clipped then capped+renormed): the constraint
  is itself a heavy shrinkage. Pulling factor loadings toward equal-weight q *adds* stability that
  survives the clip; the small dispersion-bias correction nets out as a genuine (tiny) risk
  reduction. The clip absorbs the rotation's noise and keeps its signal.
- **Unconstrained** (shorts allowed, |w|≤5%): weights can follow the rotated eigenvector into the
  short book. The ψ̂ rotation perturbs eigenvectors that at n=252 were *already good* (ψ̂≈0.98),
  so it injects estimation noise the shorts then lever. Cost grows as the eigenvectors get noisier
  (smaller n) → worst at n=42 (+49 bps). This is the F-011 lesson in miniature: unconstrained
  min-var is fragile, and JSE feeds the fragility.

At **k=1, n=252, long-only** the delta is +0.0 bps at t=0.2 (RESULTS.md line 49): the single top
S&P factor is so strong (ψ̂≈0.98–0.997) the rotation does essentially nothing. This is the same
"delta ≈ noise" cell F-010 flagged from the hunt2026 side, now confirmed as a **regime artifact
(ψ̂≈1), not a null of the theory.** Shorten the window (raise p·δ²/σ² → lower ψ̂) and the same
long-only book shows a significant help.

---

## 4. Can observable estimation-state predict when JSE helps? — **No, at month level**

The prize question: given ψ̂, eigengap, condition-number-proxy, p/n from the estimation window,
can we *time* JSE month-to-month? Pre-registered predictor test (CROSSOVER.md §predictor,
`run_crossover.py:118-140`), pooled over 6 windows × 138 months:

| predictor | long-only Δ | unconstrained Δ | verdict |
|---|---|---|---|
| median ψ̂ (pooled) | ρ=+0.18, p=3e-07 | ρ=−0.19, p=4e-08 | significant **but entirely across-n** |
| median ψ̂ (**within fixed n**) | ρ∈[−0.01,+0.09], all p>0.3 (6/6) | same | **zero timing content** |
| eigengap (λ₁−λ₂)/λ₁ | ρ=+0.03, p=0.32 | ρ=+0.09, p=0.009 | no long-only content |
| p/n | ρ=−0.18, p=1e-07 | ρ=+0.18 | this IS the real axis |

Pre-committed ψ̂ thresholds **both rejected**: "ψ̂<0.90 ⇒ helps" bucket (N=26, ~all n=42 calm
months) is insignificant at −0.4 bps and *smaller* than the rest; "ψ̂≥0.95 ⇒ no help" still shows
−1.0 bps at t=−11.

**Interpretation:** ψ̂'s per-n distributions barely overlap (n=42: 0.876–0.970; n=252: 0.968–0.992),
so pooled ψ̂ is just a re-parameterization of p/n, an *across-regime* dial, not a *within-regime*
timer. The correct predictor is the design constant **p/n**, known before any month runs; there is
no month-level state variable (of the ones tested) that fires "JSE will help *this* month."
Eigengap and the condition-number direction add nothing over p/n.

---

## 5. Axes the task names but that were NOT experimentally varied (honesty)

Do not over-read the boundary: three of the requested axes have **no evidence** yet:

- **Benchmark-relative book:** `run_minvar.py` implements only `unconstrained` and `long_only`.
  A tracking-error / benchmark-relative min-var was never run. **Untested, no claim.** Prior would
  be "between the two" (partial sign constraint), but that is a hypothesis, not a result.
- **Universe dimension p in isolation:** p is fixed at the PIT S&P 500 (~369–487 names). Dimension
  enters *only* through p/n by shrinking n. A same-p/n, different-p test (e.g. n=126 on a 100-name
  vs 470-name universe) was not run. The −0.24 bps/(p/n) slope is fit on one panel, one p-range.
- **Turnover penalties:** cost (10 bps/side) is applied *post-hoc* to net Sharpe only
  (`run_minvar.py:113`); it is never in the min-var objective. JSE and PCA have near-identical
  turnover long-only (0.11 vs 0.11 at n=252, summary.csv), so a turnover-penalized objective would
  not change the long-only sign, but this is inference from the turnover columns, not a run.

**Factor strength / eigengap** were observed (logged per month) but never *manipulated*, the panel
supplies whatever spectrum the market had. So "weak-factor regime" is reached only via short n, and
is confounded with estimation noise. A synthetic-factor study (control σᵢ²/δ² directly) is the clean
way to isolate factor strength from n; not done.

---

## 6. Domain-of-validity summary

```
                     unconstrained (shorts)      long-only (sign-constrained)
   n=42  (p/n≈10.6)   +49 bps  ✗ worst           −2.6 bps  ✓ best help
   n=63  (p/n≈7.0)    +37 bps  ✗                  −2.0 bps  ✓
   n=90  (p/n≈4.9)    +32 bps  ✗                  −1.4 bps  ✓
   n=126 (p/n≈3.5)    +27 bps  ✗                  −1.0 bps  ✓
   n=189 (p/n≈2.3)    +22 bps  ✗                  −0.7 bps  ✓
   n=252 (p/n≈1.8)    +18 bps  ✗                  −0.5 bps  ✓ (k=1: ≈0, ψ̂≈1)
   benchmark-relative:  UNTESTED
```

- **Prefer JSE:** long-only min-var, k≥3, and it *pays* only when p/n is high (n short relative to
  universe). Max realized benefit seen: 2.6 bps ann. vol at n=42, real (t≥5), robust (monotone,
  6/6), but small.
- **Never JSE:** unconstrained / short-enabled min-var, at any n. Strictly worse.
- **Indifferent:** k=1 at n=252 long-only (ψ̂≈1, rotation is a no-op).
- **No timing gate:** a month-level ψ̂ or eigengap switch adds nothing over "always-on in long-only."
- **Deploy call (F-021 CLOSED):** mechanism confirmed and bounded on all sides; not worth deploying
  on a ~470-name S&P book (ceiling ~2.6 bps), but it is the correct scientific home for the Goldberg
  program, the publishable object is *the boundary*, not a return.

---

## One-line rule

**Prefer JSE over PCA only in a sign-constrained (long-only) min-var book, where the benefit scales
as ≈ −0.24 bps realized vol per unit p/n and is thus meaningful only when p/n ≳ 5 (n ≤ ~90 on a
~470-name universe); never use JSE unconstrained, and use no month-level ψ̂ gate, p/n (a design
constant), not any per-month state variable, is the only predictor that carries.**
