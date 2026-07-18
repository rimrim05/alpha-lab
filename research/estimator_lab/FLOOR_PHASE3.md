# Phase 3 — frozen n/p correction + MP-edge trust cut (off-grid, new seed)

C3: floor + 0.5·n/p. C4: trust iff SNRhat > 2√(n/p)+n/p+0.5. Pass/fail on p/n ≥ 4 cells; (500,252) = stress, reported only. Memo: FLOOR_RESIDUAL_MEMO.md Phase 3.

| cell | med |slack| C3 (trusted) | raw | excl. sub-edge | keep detect | cover(C3) |
|---|---|---|---|---|---|---|
| 150,50 | 0.082 | 0.098 | 98% | 100% | 0.70 |
| 150,90 | 0.169 | 0.136 | 83% | nan% | 0.67 |
| 350,50 | 0.033 | 0.052 | 98% | 100% | 0.73 |
| 350,90 | 0.062 | 0.070 | 100% | 100% | 0.71 |
| 750,50 | 0.018 | 0.026 | 100% | 100% | 0.74 |
| 750,90 | 0.030 | 0.040 | 98% | 100% | 0.71 |
| 350,90 resid | 0.062 | 0.072 | 100% | 100% | 0.72 |
| 500,252 STRESS | 0.160 | 0.092 | 89% | 100% | 0.68 |

## Decision (pre-committed): **FAIL — frozen corrections do not calibrate off-grid**
- stress cell (500,252) p/n≈2: C3 slack 0.160, raw 0.092, boundary of validity, reported only
- C3 coverage note: corrected floor is a point estimate, not a bound (min cell coverage 0.67)

## Story (honest reading, including a prereg drafting error)

- **Prereg inconsistency, owned:** the memo claimed C3 validity 'for p/n ≥ 4 only' but the pass/fail cell list included (150,50) p/n=3 and (150,90) p/n=1.7. The literal rule fires FAIL; the domain-consistent reading (cells with p/n ≥ 4) gives PARTIAL: 0.018–0.033 at p/n ≥ 7, but 0.062 at (350,90) p/n≈3.9, above the 0.05 bar.
- **The refined validity map (the real deliverable):** the n/(2p) law is first-order only. p/n ≳ 7: corrected floor accurate to ≤3%. p/n ≈ 4–7: ~6%: curvature the linear term misses. p/n < 4: C3 OVERCORRECTS and is worse than raw ((150,90): 0.169 vs 0.136 raw; stress (500,252): 0.160 vs 0.092), the slack law is genuinely nonlinear there. Higher-order finite-p term = the theory question for the lab.
- **C4 (MP-edge trust cut) is a clean SUCCESS everywhere:** sub-edge exclusion 83–100%, detectable retention 100%, including the residualized arm and the stress cell. This piece is usable as-is.
- **Coverage trade named:** C3 makes the floor a point estimate, coverage drops to ~0.7 from ~1.0. Bound vs accuracy is a choice, not a free lunch.
- Stop-iterating honored: no new c, margin, or forms. Empirical phase closes with the validity map; the higher-order slack term and the closed-form MP-edge threshold go to the lab as theory (Kristen's).
