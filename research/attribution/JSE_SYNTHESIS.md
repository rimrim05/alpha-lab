# JSE Evidence Synthesis — every completed James-Stein / shrinkage experiment in alpha-lab

Compiled 2026-07-14 (Agent D-synth). Collation only — no reruns, no new experiments.
Numbers quoted exactly as recorded in the source files. Sources: research/estimator_lab/
(PLAN, RESULTS, CROSSOVER, FACTOR_GATE, THEOREM_COMPLETE, HEDGE_PAIR, REGIME_MAP,
SUBSPACE_INVARIANCE, SUBSPACE_AVERAGING, ROBUST_ROTATION, STEP4_SYNTHESIS,
JSE_BOUNDARY_MAP, AUDIT_JSE_RECONCILIATION, FLOOR_PIPELINE_HANDOFF + summary/results CSVs);
research/hunt2026/ (TRIAL_LEDGER, FAILURES F-021/F-026..F-031, results5y/pca_minvar_*.json);
memos/hunt2026-verdict.md, memos/hunt2026-walkforward.md.

Scope note: the FLOOR_* line (floor-diagnostic pipeline, FLOOR_PIPELINE_HANDOFF.md) is a
separate exposure-error-diagnostics project, explicitly "NOT a minimum-variance portfolio
project"; it is cited here only for mechanism context (Theorem 1 floor / rotation split),
not as a JSE portfolio experiment.

---

## 1. Master raw-vs-JSE table

JSE effect = jse − pca(raw) on the primary metric, signed (negative = JSE better when the
metric is vol/turnover; positive = JSE better when the metric is return/Sharpe).

| experiment | k | window n | book | primary metric | JSE effect (signed) | t / p | prereg? | verdict | file |
|---|---|---|---|---|---|---|---|---|---|
| hunt2026 pair, 1y blind holdout | 1 | 60 (est.) | long-only min-var, 2% cap, 2x lever | net 1y return | **+15 bps** (JSE +12.96% vs raw +12.81%); Sharpe 0.71 vs 0.70; maxDD −14.77% vs −14.84%; identical turnover | not reported | yes (frozen spec) | direction right, "too muted to measure in one year" | memos/hunt2026-verdict.md |
| hunt2026 pair, 44-window walk-forward | 1 | 60 | same | median SPY-excess | **+3.4 (JSE) vs +3.5 (raw) pp**, "marginally better worst" | not reported | yes (frozen spec, walk-forward protocol) | "JSE ≥ raw again … direction has now been right in every eval mode" — see contradiction C2 | memos/hunt2026-walkforward.md item 6 |
| hunt2026 pair, 5y sandbox (non-blind) | 1 | 60 | same | CAGR / Sharpe | **+10 bps CAGR** (0.11329 vs 0.11226); Sharpe 0.5527 vs 0.5487; ann vol 25.26% vs 25.28%; maxDD −31.80% vs −31.83%; avg daily turnover 0.00809 vs 0.00808 | not reported | yes | direction right, muted (ledger row #14: "watch") | results5y/pca_minvar_{jse,raw}.json; TRIAL_LEDGER rows 13–14 |
| 9-estimator lab, n=252 | 1 | 252 | unconstrained (shorts, \|w\|≤5%) | realized ann vol (137 mo) | **+31 bps** | +11.7 / <0.001 | yes (PLAN.md) | JSE worse | RESULTS.md |
| 9-estimator lab, n=252 | 3 | 252 | unconstrained | realized ann vol | **+18 bps** | +9.6 / <0.001 | yes | JSE worse | RESULTS.md |
| 9-estimator lab, n=252 | 5 | 252 | unconstrained | realized ann vol | **+14 bps** | +7.9 / <0.001 | yes | JSE worse; gap *shrinks* in k (prereg expected it to grow) | RESULTS.md |
| 9-estimator lab, n=252 | 1 | 252 | long-only | realized ann vol | **+0.0 bps** | +0.2 / 0.84 | yes | no-op (ψ̂≈1) | RESULTS.md |
| 9-estimator lab, n=252 | 3 | 252 | long-only | realized ann vol | **−0.6 bps** | −8.2 / <0.001 | yes | tiny real help (audit-corrected: −0.53 bps t=−7.39 on 138-mo panel) | RESULTS.md; AUDIT_JSE_RECONCILIATION.md |
| 9-estimator lab, n=252 | 5 | 252 | long-only | realized ann vol | **−0.5 bps** | −8.7 / <0.001 | yes | tiny real help | RESULTS.md |
| n=63 reopen (H-jse-weakfactor) | 1/3/5 | 63 | long-only | realized ann vol | **−1.3 / −2.0 / −1.6 bps** (−0.013/−0.020/−0.016 vol%pts) | t −2.2/−6.0/−6.5, p ≤ 0.03 | yes (queue #1) | JSE significantly improves in its designed regime | summary_w63.csv; FAILURES.md F-021 RESOLVED |
| n=63 reopen | 1/3/5 | 63 | unconstrained | realized ann vol | **+72 / +37 / +25 bps** | t > 6 | yes | JSE still worse | summary_w63.csv; FAILURES.md |
| EXP-EST-CROSSOVER | 3 | 42/63/90/126/189/252 | long-only | paired realized vol | **−2.6 / −2.0 / −1.4 / −1.0 / −0.7 / −0.5 bps** (monotone in p/n; ≈ −0.24 bps per unit p/n) | t −5.4…−7.4, all p<0.0001 | yes (est-crossover-2026-07-10.md) | NO CROSSOVER — helps at every n, never material; ψ̂ has zero within-n timing content | CROSSOVER.md |
| EXP-EST-CROSSOVER | 3 | same 6 | unconstrained | paired realized vol | **+49 / +37 / +32 / +27 / +22 / +18 bps** | t +6.6…+9.7, all p<0.0001 | yes | hurts at every n, worst at small n | CROSSOVER.md |
| jse-factor-gate (F-026) | 5 | 63 (decisive), 252 | long-only + unconstr. | median paired Δ vol, gated vs blanket jse5 | **+0.00 bps median** (decisive cell); where gate binds: mean −0.36 bps, 65% hit | pooled t −2.81 / 0.0057 (g_min=0.1) | yes (Kristen Stage-0) | **REDUNDANT** (0/6 configs); ψ̂ gate never binds (min ψ̂ 0.826); separation (eigengap) is the binding quality axis | FACTOR_GATE.md |
| jse-theorem-complete (F-027) | 5 | 63 (decisive), 252 | long-only + unconstr. | median paired Δ vol, eq.-13-calibrated vs blanket jse5 | **+1.85 bps** decisive (long-only n=63 t6); unconstrained **+29.76 bps median (+49.98 mean)** | +2.64 / 0.0092 (decisive); +7.26 / 0.0000 (unconstr.) | yes (Stage-0 + F-026 override) | **WRONG TARGET** — rotation diagnosis validates, q-target response fails with dose-response | THEOREM_COMPLETE.md |
| jse-hedge-pair (F-028, HYP-005b reopen) | 1 | 63 (decisive), 252 | statarb A&L book, factor-1 hedge | median monthly \|β_SPY\| | **−0.0004** (jse1 0.057 vs pca1 0.059); gross Sharpe Δ **−0.023**; net Sharpe −0.43 vs −0.40; n=252 books identical to 2dp | −1.53 / 0.1305 | yes (Stage-0) | **NO EFFECT**; revival gate (net ≥ 0.5) NOT HIT; ψ̂₁≈1 ⇒ nothing to correct | HEDGE_PAIR.md |
| jse-regime-map (F-029) | 1 | 63 (decisive), 252 | long-only 1-factor min-var, 3 universes | monthly L1 weight turnover | turnover **+0.0044 (large) / +0.0045 (mid) / +0.0064 (small)** at n=63; Δ realized vol ≈ 0 (−0.0002…−0.0011) | t +5.99…+12.06, all p=0.0000 | yes (Stage-0) | **HARMFUL** — churns the hedge for no vol payoff, worst on noisiest universe | REGIME_MAP.md |
| subspace-invariance | 1/3/5 | 63, 252 | unconstrained | rotation-CV vs projector-gap | rot CV 0.0138 vs rand-subspace +0.26 (decisive: large n=63 k=5); projector within +1.9% of full | pre-committed thresholds all met | yes | **SUBSPACE FUNCTIONAL CONFIRMED** — within-subspace rotation irrelevant to min-var | SUBSPACE_INVARIANCE.md |
| subspace-averaging (F-030, Avenue 2) | 1/3/5 | 63, 252 | unconstrained | paired rel Δ vol vs L=1 | decisive (small n=63 k=5): −4.09% best (p=0.130); elsewhere **+1.4% to +14.64% worse** (large k=3 L=12: +14.64%, p=0.000) | see table | yes (Stage-0) | **NO EFFECT** decisive, net HARMFUL broadly; drift, not noise | SUBSPACE_AVERAGING.md |
| robust-rotation SOCP (F-031, Avenue 3) | 5 | 63, 252 | unconstrained | paired rel Δ vol vs raw PCA | decisive (large n=63 κ=1): **+10.36%** (p=0.003); harmful 5/6 cells (small n=63 **+48.07%**); monotone in κ | see table | yes | **HARMFUL** — acting on the rotation bound costs vol; per-factor beats uniform (−12% to −23%) but κ→0 is best | ROBUST_ROTATION.md |

Not experiments, but part of the record: AUDIT_JSE_RECONCILIATION.md (forensic — pipelines
byte-identical, conflict was prose; see §Contradictions) and STEP4_SYNTHESIS.md /
JSE_BOUNDARY_MAP.md (syntheses of the above, no new runs).

---

## 2. The estimator horse-race — where LW and MP landed vs JSE and PCA

Mean realized ann vol, min-var walk-forward (summary.csv 137 mo n=252; summary_w63.csv 138 mo n=63):

| book / window | winner | LW | MP | best PCA | best JSE | sample |
|---|---|---|---|---|---|---|
| unconstrained, n=252 | **MP 11.27%** | 11.64% (2nd) | **11.27%** | pca5 12.08% | jse5 12.22% | 14.40% (turnover 8.66 — unusable) |
| long-only, n=252 | **pca1 11.69%** | 13.70% | 13.13% | 11.69% | jse1 11.69% | 14.16% |
| unconstrained, n=63 | **LW 10.60%** | **10.60%** | 11.31% | pca5 11.04% | jse5 11.29% | 12.04% |
| long-only, n=63 | **jse1 11.57%** (pca1 11.58%) | 13.27% | 12.67% | 11.58% | 11.57% | 13.76% |

Read: unconstrained books are won by spectrum-level shrinkage (MP clipping at n=252, LW at
n=63) — both beat every factor model, and JSE never beats LW there. Long-only books are won
by low-k factor models (pca1/jse1, a coin flip between them); LW/MP fall ~1.5–2 vol points
behind. RESULTS.md prereg line "lw competitive, mp ≈ lw" was scored "Held, understated."
Side note from ROBUST_ROTATION.md: LW vs full-PCA is mixed across universes (−3.3% large
n=252, p=0.006 helping, +8.63% small n=63 hurting).

---

## 3. Mechanism conclusions (all checked, not assumed)

1. **ψ̂ ≈ 1 on S&P-scale panels.** n=252, ~450 strong names: per-factor ψ̂ 0.93–0.997
   (RESULTS.md). Factor 1 specifically: ψ̂₁ ≈ 0.976–0.996 on ALL cached universes including
   S&P 600 small-cap (REGIME_MAP.md), ≈1 at p≈500–1000 (HEDGE_PAIR.md). The dispersion bias
   the correction targets is nearly absent; the rotation only perturbs already-good
   eigenvectors. F-027+F-028 bracket the correction completely on these panels: *the factor
   JSE can validly correct (f1) has no bias worth correcting; the factors with real bias
   (f2–f5, MC rotation 0.13–0.55) have no valid target* (q is the market factor's target;
   pushing f2–f5 toward q collapses the factor block toward multiple market copies).
2. **Subspace-invariance diagnosis.** Min-var is a subspace functional: realized vol is
   invariant to within-subspace frame rotation (CV 1.4% decisive cell) and sensitive only to
   the projector P (+26% for a random subspace); the pure-projector portfolio w∝(I−P)1 lands
   within 1.9% of full min-var. Combined with F-031 (acting on the rotation bound raises vol,
   monotone in κ): **the within-subspace rotation — Theorem 1's hard term, the Davis-Kahan/t₆
   object — has no positive min-var value**, from two independent directions (ignoring it is
   free; hedging it costs).
3. **Drift, not noise.** F-030: the single-window subspace error is drift-dominated — the
   k-th eigenvalue of the L-window projector mean drops to 0.30–0.45 in short-window
   multi-factor cells, and averaging (which fixes variance, not bias) makes vol significantly
   worse there (up to +14.6%, p<0.001). The distilled open problem is a drift-aware subspace
   estimator; no tool tested addresses a moving subspace.
4. **Where the theory's live regime actually is.** The correction's sign is set by the BOOK
   (long-only: always a small help; unconstrained/shorts: always a hurt), and its magnitude
   by the design constant p/n (≈ −0.24 bps realized vol per unit p/n, so it pays meaningfully
   only when p/n ≳ 5, i.e. n ≤ ~90 on a ~470-name book). No month-level state variable (ψ̂,
   eigengap) has timing content within a fixed n. Nothing in S&P large/mid/small reaches the
   regime where the correction earns its keep — that requires genuinely thin panels (tens of
   names) or much shorter windows, i.e. a different asset class (REGIME_MAP.md,
   JSE_BOUNDARY_MAP.md). Max realized benefit ever observed: −2.6 bps ann vol (n=42,
   long-only).

---

## 4. GAPS vs required reporting spec

Spec: k ∈ {1,3,5} × {realized residual vol, tracking error, exposure stability, turnover,
concentration, drawdown, net return after costs}.

| metric | k=1 | k=3 | k=5 |
|---|---|---|---|
| realized residual vol | **MISSING** (see note a) | **MISSING** | **MISSING** |
| tracking error | **MISSING** (see note b) | **MISSING** | **MISSING** |
| exposure stability | COVERED — median monthly \|β_SPY\| paired series, HEDGE_PAIR.md (k=1 only) | **MISSING** | **MISSING** |
| turnover | COVERED — summary.csv / summary_w63.csv `mean_turnover` (both books); REGIME_MAP.md L1 weight turnover by universe | COVERED — summary*.csv | COVERED — summary*.csv |
| concentration | **MISSING** (see note c) | **MISSING** | **MISSING** |
| drawdown | COVERED — maxDD for the hunt2026 pair only: −14.77% vs −14.84% (1y, hunt2026-verdict.md), −31.80% vs −31.83% (5y, results5y/pca_minvar_*.json) | **MISSING** | **MISSING** |
| net return after costs | COVERED — per-month `ret_net` in results.csv / results_w63.csv and `sharpe_net` in summary*.csv (10 bps/side) | COVERED — same files | COVERED — same files |

Notes:
- (a) Every estimator-lab experiment reports realized **total portfolio** vol (that IS the
  pre-registered primary metric), not realized **residual** vol relative to a factor model.
  Residual vol was never computed or recorded anywhere in these files.
- (b) **Tracking error was never reported by any experiment.** No benchmark-relative book was
  ever run — JSE_BOUNDARY_MAP.md §5 states it explicitly: "A tracking-error /
  benchmark-relative min-var was never run. Untested — no claim." Per instruction, no
  substitute is derived here. (The hunt2026 walk-forward reports median SPY *excess return*,
  which is a return statistic, not a tracking error.)
- (c) A 5% (estimator lab) / 2% (hunt2026) per-name cap was *enforced by construction*, but
  no realized concentration statistic (HHI, effective N, max weight) was ever recorded.
- Exposure stability at k=3/5: REGIME_MAP-style turnover exists only at k=1; the k=3/5
  experiments report weight turnover but no factor-exposure stability measure.

---

## 5. Contradictions found between documents (flagged, not resolved)

- **C1 (resolved on the record by the audit):** RESULTS.md line 59 prose ("statistically
  significant at k=3,5 but economically zero") contradicts its own table (−0.6 bps, t=−8.2,
  p<0.001); the F-021 "sign flip at n=63" narrative inherited the error.
  AUDIT_JSE_RECONCILIATION.md verdict: REPORTING DRIFT — pipelines byte-identical (max
  per-month diff 2.7e-16), divergence was prose only; corrected numbers −0.53 bps t=−7.39
  (n=252) / −1.98 bps t=−5.99 (n=63) on the 138-month panel. Both readings are kept above.
- **C2 (unresolved wording):** memos/hunt2026-walkforward.md item 6 says "JSE ≥ raw again
  over 44 windows (+3.4 vs +3.5 median excess, marginally better worst)". +3.4 (JSE) is
  *lower* than +3.5 (raw) on the median; the "≥" claim apparently rests on the worst-window
  comparison. Quoted as written; the median favors raw by 0.1pp.
- **C3 (superseded, both kept):** RESULTS.md's original bottom line "economically zero at
  n=252 long-only" is explicitly superseded by its own Follow-ups section and CROSSOVER.md
  ("tiny but real and significant at every window").
- **C4 (metric subtlety, self-documented):** FACTOR_GATE.md reports median Δ = +0.00 with
  pooled t = −2.81 (p=0.0057) in the same row — not an error (treatment == control in most
  months, so the median cannot move), but the verdict REDUNDANT is driven by the
  pre-committed median rule while the mean where the gate binds is −0.36 bps.

---

## 6. Verdict inputs — which statement does the evidence support?

Candidate statements, assessed against the full table:

### (i) "No practical JSE value in this system" — SUPPORTED as the deployment reading
For (strongest three):
1. Ceiling of the entire program: −2.6 bps ann vol (n=42 long-only), and F-021 FINAL /
   Director closure locked "below deployment materiality on ~470-name S&P books"; 8
   cumulative registered overlay chances since closure, best outcome "tiny help, far below
   any deployment bar" (THEOREM_COMPLETE.md).
2. Everywhere shorts are allowed JSE is significantly harmful (+14 to +49 bps, t 6.6–12) —
   and this system's alpha books are the short-enabled kind.
3. As a risk overlay it is a small net negative on every accessible universe: raises turnover
   (t=6–12) for Δvol ≈ 0 (F-029); no effect on hedge β (F-028); ψ̂₁≈1 means there is nothing
   to correct at S&P scale.
Against:
1. The long-only benefit is real, significant at every n (all p<0.0001), monotone, and
   mechanism-confirmed — "no value" overstates; "no material value" is exact.
2. The hunt2026 pair went the right direction in all three eval modes (+15 bps 1y blind,
   +10 bps CAGR 5y, marginally better worst over 44 windows) — never hurt.
3. The program produced deployable knowledge (the boundary, the p/n rule, the drift
   diagnosis) even if not deployable P&L.

### (ii) "JSE improves risk diagnostics only" — PARTIALLY SUPPORTED, wrong emphasis
For: the validated outputs are diagnostic — rotation-MC diagnosis matches the theorem
(f1 ~0.02, f2–f5 0.13–0.55, t₆>normal); the subspace-stability metric (F-030) is "kept for
reuse"; ψ̂ is a clean regime descriptor. Against: ψ̂ has ZERO month-level timing content
(6/6 windows, all p>0.3); the rotation bound has "no positive min-var value" from both
directions; and JSE does slightly improve realized *risk* (not just diagnostics) in
long-only books — so "diagnostics only" is simultaneously too generous (the diagnostics
don't time anything) and too stingy (there is a real, tiny risk reduction).

### (iii) "JSE improves hedging/risk control but not alpha" — SUPPORTED as the literal
scientific reading, with a materiality asterisk
For (strongest three):
1. Long-only min-var realized vol: JSE < PCA at every window n=42→252, −2.6→−0.5 bps,
   always p<0.0001, monotone in p/n, mechanism proven by construction (CROSSOVER.md).
2. It never improved returns anywhere: hunt2026 deltas (+15 bps 1y / +10 bps CAGR / −0.1pp
   median excess) are noise-grade; net Sharpe deltas in the lab are ~0 at matched k.
3. The effect is exactly where risk-control theory says: pays ∝ p/n, dies as ψ̂→1.
Against (strongest three):
1. The direct hedging tests FAILED: F-028 NO EFFECT on |β_SPY| (p=0.13, gross Sharpe Δ
   −0.023); F-029 HARMFUL to hedge-weight stability on all three universes. "Improves
   hedging" is contradicted by the two experiments that tested hedging specifically.
2. In the unconstrained (risk-control-relevant, shorts-on) book it *raises* realized vol at
   every k and every n.
3. The improvement it does deliver is ≤2.6 bps/yr — an order of magnitude below the
   pre-committed deployment bars, and plain LW/MP shrinkage beats it wherever it matters.
So the defensible form is: **"JSE improves long-only min-var risk control — statistically
real, economically immaterial — and nothing else in this system."**

### (iv) "JSE materially improves risk-adjusted implementation" — NOT SUPPORTED
No experiment supports it. Every pre-committed materiality bar was missed: −0.2 bps median
gate bar (F-026), ±0.3 bps calibration bar (F-027), 0.5 net-Sharpe revival gate (F-028),
turnover-stabilization rule (F-029), and the deployment-materiality lock in F-021 FINAL.
No evidence lines "for" exist at recorded thresholds.

### Bottom line for the verdict memo
The evidence supports (iii) restricted to long-only min-var realized vol, with (i) as the
correct operational conclusion: statistically real, economically immaterial, book-sign-
dependent, ψ̂/p-n-bounded — and every attempt to enlarge it (gating, eq.-13 calibration,
hedging, regime targeting, averaging, robust rotation) either did nothing or hurt. The
publishable object is the boundary map, not a deployment.
