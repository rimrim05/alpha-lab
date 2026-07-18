# Preregistration — benchmark-relative (tracking) JSE vs PCA adjudication (EXP-2026-07-14-jse-benchrel)

FROZEN 2026-07-14 before the run. This is the single pre-specified adjudication test named
by the adversarial review (research/attribution/ADVERSARIAL_REVIEW.md): the only cell in
JSE_BOUNDARY_MAP.md §5 marked UNTESTED that could overturn the program's JSE verdict
("no deployment-material JSE value on any book tested"). One run, no variants, no reruns.
Stage-0 authorization: Kristen's 2026-07-14 program directive (Phase 3 requires tracking
error as a primary outcome; execution rule 6 permits exactly this smallest adjudication).

## Question

Does the JSE eigenvector correction reduce realized tracking error in a benchmark-relative
(index-tracking) construction, where TE — unlike total min-var vol — depends on active
positions and might be sensitive to the eigenvector directions?

## Design (mirrors run_minvar.py conventions exactly; only the objective is new)

- Panel, month loop, eligibility, exclusions, START=2015-01-01: identical to
  research/estimator_lab/run_minvar.py with EL_WINDOW=63 (the decisive weak-factor cell).
- Benchmark w_b: equal weight over ALL eligible names that month (PIT, no caps).
- Tracking basket B: every 5th eligible name in sorted-ticker order (deterministic,
  estimator-independent, ≈90–97 names) — the basket cannot replicate the benchmark, so
  the problem is non-degenerate.
- Optimization per estimator: minimize (w − w_b)ᵀ Σ̂ (w − w_b) over w supported on B,
  1ᵀw = 1 (closed form via Σ̂_BB solve with Lagrange sum constraint), then the house
  single-pass long-only clip + 5% cap + renormalize.
- Estimators: decisive pair jse5 vs pca5; context rows pca1/jse1, pca3/jse3, lw, mp,
  sample (same ESTIMATORS dict, no new estimator code).
- Hold: next month (weights at close d earn d+1..next first trading day), delisted → 0.
- Primary metric: realized annualized TE = std(daily basket − benchmark return)·√252,
  paired per month, jse5 − pca5, two-sided paired t over ~138 months.
- Secondary: monthly one-side L1 turnover of w per estimator; TE for the context rows.

## Decision rule (pre-committed, from the adversarial review, verbatim thresholds)

- OVERTURN (JSE has deployment-relevant benchmark-relative value) iff:
  mean relative ΔTE = mean((TE_jse5 − TE_pca5)/TE_pca5) ≤ −0.5% with paired p < 0.05
  AND mean absolute ΔTE ≤ −10 bps annualized.
- Anything else: the verdict "no deployment-material JSE value on any book tested" stands
  and the benchmark-relative cell moves from UNTESTED to tested in the boundary map's
  successor documents. No parameter changes, no second run, regardless of outcome.

## Trial accounting

One registered adjudication run. Cumulative JSE-line registered chances: 9 (8 prior per
jse-theorem-complete prereg + this). Adaptive-loop flag: yes (reacts to the adversarial
review of completed results).

## Outputs

research/estimator_lab/run_benchrel.py, benchrel.csv, BENCHREL.md (result vs this file),
run stamp artifacts/estimator_lab/benchrel_run.json.
