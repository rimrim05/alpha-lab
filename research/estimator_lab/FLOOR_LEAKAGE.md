# Phase 4 — leakage detection under misspecified residualization

Detector D_j = R² of residual-factor returns on estimated known-factor returns; flag leaked iff F-test p < 0.01. C4 screen applied first. Prereg: FLOOR_RESIDUAL_MEMO.md Phase 4.

| cell | arm | med D (genuine) | med D (leaked) | trap rate | AUC | FPR | FNR |
|---|---|---|---|---|---|---|---|
| 500,63 | A1 oracle | 0.054 | nan | nan% | nan | 0.01 | nan |
| 500,63 | NEG | nan | nan | nan% | nan | nan | nan |
| 500,63 | LEAK | nan | 0.625 | 100% | nan | nan | 0.04 |
| 500,63 | MIXED | 0.061 | 0.612 | 100% | 0.988 | 0.07 | 0.04 |
| 350,90 | A1 oracle | 0.042 | nan | nan% | nan | 0.01 | nan |
| 350,90 | NEG | nan | nan | nan% | nan | nan | nan |
| 350,90 | LEAK | nan | 0.542 | 100% | nan | nan | 0.02 |
| 350,90 | MIXED | 0.058 | 0.533 | 100% | 0.987 | 0.12 | 0.04 |
| 750,50 | A1 oracle | 0.067 | nan | nan% | nan | 0.01 | nan |
| 750,50 | NEG | nan | nan | nan% | nan | nan | nan |
| 750,50 | LEAK | nan | 0.668 | 100% | nan | nan | 0.05 |
| 750,50 | MIXED | 0.090 | 0.657 | 100% | 0.981 | 0.05 | 0.07 |

## Decision (pre-committed, MIXED arm, held-out cells): **AMBIGUOUS**
- held-out worst: AUC 0.981 | FPR 0.12 | FNR 0.07 (bars: ≥0.9, ≤0.10, ≤0.10)
## Story (mechanism diagnosis, no tuning)

- **Substantively this works; the miss is one number.** AUC 0.98+ in every cell; FNR ≤ 0.07
  everywhere; the single bar violation is FPR 0.12 at (350,90) vs the 0.10 bar.
- **Mechanism of the false positives (diagnosed, not patched):** the estimated factor
  returns f̂_F = B̃_FᵀY are noise-contaminated, and the residual factor series share the
  SAME noise realization, so genuine factors' R² sits slightly above the F-null (med D
  0.058–0.090 vs null ≈ k_F/n), worst where n/p is largest (350,90 = 0.26). The F-test
  assumes an independent null; the shared-noise term violates it mildly. A split-sample
  detector (estimate f̂_F on half the window, test on the other half) is the principled fix:
  a NEW detector requiring a new prereg, not a threshold tweak.
- **The trap is real and maximal: trap rate 100% in every LEAK/MIXED cell**: every truly
  leaked factor passes the trust screen with floor < 0.3, i.e. leaked structure looks
  PERFECTLY reliable to the floor+screen pipeline. Without a leakage check, a practitioner
  would trust exactly the wrong factors. The floor itself is not fooled about (a), the
  leaked factors genuinely ARE well-estimated directions, but their PROVENANCE is wrong.
- **NEG arm validates the pipeline order:** with no residual factors at all, the C4 screen
  rejects everything before the leak test ever runs (all-nan row = nothing survived to test).
