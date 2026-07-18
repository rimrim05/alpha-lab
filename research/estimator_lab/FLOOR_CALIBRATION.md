# Finite-sample calibration of the observable floor (Phase 2)

slack = (a)_j − floor_j per factor; SNRhat = θ_j/ℓ − 1 observable. C1 = n/(n−k) scaling; C2 = empirical linear calibration (fit even cells, eval odd). Memo: FLOOR_RESIDUAL_MEMO.md Phase 2.

| p | n | med slack (all) | med slack SNRhat>1 | med slack SNRhat≤1 | |C1| | |C2| |
|---|---|---|---|---|---|---|
| 100 | 40 | +0.383 | +0.383 (1000) | +nan (0) | 0.333 | 0.088 |
| 100 | 63 | +0.471 | +0.471 (1000) | +nan (0) | 0.445 | 0.117 |
| 100 | 126 | +0.597 | +0.597 (1000) | +nan (0) | 0.587 | 0.149 |
| 250 | 40 | +0.214 | +0.099 (642) | +0.397 (358) | 0.156 | 0.053 |
| 250 | 63 | +0.314 | +0.313 (998) | +0.475 (2) | 0.276 | 0.079 |
| 250 | 126 | +0.486 | +0.486 (1000) | +nan (0) | 0.472 | 0.131 |
| 500 | 40 | +0.119 | +0.038 (478) | +0.275 (522) | 0.052 | 0.052 |
| 500 | 63 | +0.173 | +0.063 (558) | +0.372 (442) | 0.132 | 0.053 |
| 500 | 126 | +0.327 | +0.327 (1000) | +nan (0) | 0.309 | 0.095 |
| 1000 | 40 | +0.066 | +0.016 (433) | +0.168 (567) | 0.035 | 0.058 |
| 1000 | 63 | +0.090 | +0.025 (465) | +0.239 (535) | 0.048 | 0.053 |
| 1000 | 126 | +0.170 | +0.066 (564) | +0.396 (436) | 0.150 | 0.057 |

- held-out median |slack|: raw 0.193 | C1 0.153 | C2 0.058
- pooled median |slack|: SNRhat>1: 0.198 | ≤1: 0.302
- A1 oracle-resid spot-check (500,63), |slack| above cut: 0.064 (matches the A0 cell, residualization transfer confirmed again)

## Decision (pre-committed): **UNCALIBRATABLE under the frozen corrections**

## Story (the structure behind the verdict)

- **The slack has clean n/p scaling for genuinely detectable factors.** Above-edge |slack| tracks ≈ n/(2p): (1000,40) 0.016, (1000,63) 0.025, (500,63)≈(1000,126) 0.063/0.066, same n/p, same slack. The floor's p→∞ limit converges at rate ~n/p, so 'when is the floor a good approximation' has a quantitative answer: **p/n ≳ 15 for ~5% accuracy**. Practitioner translation: S&P at n=63 (p/n≈8) is borderline (~6% under-report); at n=252 (p/n≈2) the floor is MATERIALLY optimistic. The paper's own US-equity use case sits at the edge of its asymptotics.
- **The naive observable trust cut breaks at moderate n/p, visibly at (500,126) where ALL factors pass the cut with +0.33 slack.** Mechanism: the finite-p noise bulk is Marchenko-Pastur-spread, not flat; its top edge ≈ (δ²/n)(1+√(n/p))², so sub-detection factors ride the inflated edge past SNRhat>1. The trust cut must be n/p-aware (≈ (1+√(n/p))²−1 + margin), not a constant.
- **C2 near-missed the bar** (held-out 0.058 vs 0.05; did satisfy the ≤raw/3 condition): the bias is largely capturable from observables, just not by the frozen linear form. Per the stop-iterating rule, no post-hoc correction is fitted here; the n/p-linear correction + MP-edge-aware cut are the SINGLE pre-registered Phase-3 candidates.
- **Theory candidates for the lab (Kristen's to derive, not fitted here):** the ≈ c·n/p slack law and the MP-edge trust threshold both look closed-form-able, a finite-p refinement of Corollary 1.
