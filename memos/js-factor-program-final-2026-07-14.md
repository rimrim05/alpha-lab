# Final memo — James-Stein / factor-risk program on the live hunt2026 book (2026-07-14)

Autonomous program run per Kristen's 2026-07-14 directive. Preregs:
`factor-attribution-2026-07-14.md`, `jse-benchrel-2026-07-14.md` (both frozen pre-run);
JSE evidence otherwise from the 9 completed preregistered estimator-lab experiments (no reruns).
Working papers: `research/attribution/` (ATTRIBUTION, RESIDUAL_FACTORS, JSE_SYNTHESIS,
INTEGRITY_AUDIT, ADVERSARIAL_REVIEW), `research/estimator_lab/BENCHREL.md`. Ledger updated.

## 1. Bottom-line verdict (Q1 — residual alpha)

**Factor-premium harvesting with some unexplained residual return.**

The label fires mechanically from the pre-committed mapping (no book reaches blind-window
M2 alpha t ≥ 2; three books sit in the >2%/yr, 1 ≤ t < 2 band) and carries four mandatory
riders from the adversarial review:

- Each of the four best cells decomposes away post-hoc: defensive_ensemble (+6.7%, t=1.77)
  → −0.15%/yr after the missing gold factor (β_GLD 0.22, t=9.5) and the 1.92x financing
  stress; dual_momentum_gold (+13.0%, t=1.32) → +2.0%, t=0.26 after gold beta (β 0.79), on
  a hindsight-flagged menu; trend_vol_qqq (+9.1%, t=1.50) → +3.8%, t=0.57 excluding 2022,
  and its naive parent has a LARGER blind alpha (+12.4%, t=1.55) — under-spanned trend
  premium, not engineering; dual_momentum_gem's 1y cell is statistically empty (half-split
  −9.4%/+39.7%).
- The verdict is conditional on classifying TSMOM harvest as factor exposure:
  defensive_ensemble clears t=2.01 under FF5+MOM alone; adding the published, investable
  TSMOM proxy (and the QQQ-residual, whose full-sample fit biases alpha UP, not down)
  pulls it under. Timing known premia well is what this book demonstrably does.
- Power: minimum detectable alpha at t=2 is 7.6%/yr (best cell) to 28%/yr (worst). "Not
  detected" ≠ "absent" — but the burden of proof sits with the alpha claim, and nothing
  cleared it.
- Best-of-family t=1.77 against ≥18 registered adaptive trials ≈ familywise p ≈ 0.11.

## 2. JSE verdict (Q2)

**No practical JSE value in this system** (reviewer's precise wording: no
deployment-material JSE value on any book tested).

- The one real effect: long-only min-var realized-vol reduction, statistically solid at
  every window length (p < 0.0001), economically capped at ≈ 2.6 bps/yr at n=42, shrinking
  as ≈ −0.24 bps per unit p/n. Every pre-committed materiality bar was missed.
- Harmful with shorts at every k and n (+14 to +72 bps vol); hedging tests: statarb
  factor-1 hedge NO EFFECT (F-028), beta-overlay regime map HARMFUL via turnover (F-029);
  eq.-13 calibration WRONG TARGET (F-027); per-factor gating REDUNDANT (gate never binds,
  min ψ̂ 0.826).
- The last untested cell — benchmark-relative / tracking error — was adjudicated today
  under a frozen prereg: jse5 vs pca5 ΔTE = −0.04 bps ann (p=0.42), rel −0.02% vs the
  −0.5% overturn bar. VERDICT STANDS. Mechanism: ψ̂₁ ≈ 0.98–1.00 on every accessible
  universe — there is nothing for the correction to correct at S&P scale; TE, like
  min-var vol, is a subspace-and-spectrum functional.
- What survives is research value, not system value: the boundary map, the ψ̂ regime
  diagnosis, and the drift-not-noise reframing of step 4 (drift-aware subspace estimation
  is the real open problem; shrinking eigenvectors toward any fixed target is not).
- If risk-model quality ever matters here operationally: MP eigenvalue clipping won every
  unconstrained and benchmark-relative cell (and LW second); both beat every factor model.

## 3. Evidence table by book (blind windows; M2 = FF5+MOM+TSMOM+QQQ-residual, NW lag 5)

| book | blind window | raw net | M1 α (t) | M2 α (t) | M3 α (t) | stress α | key exposures | validity flags |
|---|---|---|---|---|---|---|---|---|
| vol_managed_qqq | 1y | +42.5% | +2.6% (0.32) | +1.4% (0.25) | n/a (ETF) | −0.6% | Mkt/QQQ, TSMOM; R² 0.97 | 219 obs; MDA ≈ 12%/yr |
| vol_core_svxy | 1y | +36.1% | +1.1% (0.19) | +0.5% (0.10) | n/a | −3.1% | Mkt/QQQ, short-vol unmodeled | SVXY carry not in factor set |
| dual_momentum_gem | 1y | +58.6% | +19.2% (1.32) | +15.8% (1.12) | n/a | +13.4% | regime-switch, MOM, TSMOM; R² 0.82 | half-split −9.4%/+39.7% — cell empty; MDA 28%/yr |
| momentum_concentrated | 1y | +35.4% | −5.8% (−0.54) | −7.5% (−0.68) | −10.7% (−0.64) | −7.5% | MOM, Mkt; R² 0.75 | survivorship overstates raw (audit FAIL-2); strengthens negative |
| trend_vol_qqq | 5y | +24.7%/yr | +11.7% (1.63) | +9.1% (1.50) | n/a | +7.6% | QQQ, TSMOM; R² 0.62 | ex-2022: +3.8% (0.57); naive parent α larger |
| defensive_ensemble | 5y | +19.9%/yr | +9.5% (2.01) | +6.7% (1.77) | n/a | +2.9% | Mkt, TSMOM, GLD (β 0.22 unmodeled in M2) | +GLD: +3.7% (1.09); +GLD+financing: −0.15% |
| dual_momentum_gold | 5y | +29.1%/yr | +17.4% (1.63) | +13.0% (1.32) | n/a | +11.2% | GLD β 0.79, QQQ switch; R² 0.37 | +GLD: +2.0% (0.26); ex-2025: −1.5%; menu hindsight (ledger) |

Controls: SPY/QQQ buy-hold M1 placebo pass (t 0.44–1.55); 1.5x QQQ 5y t=2.09 —
mechanical financing artifact (harness charges no financing), which is exactly what the
stress line removes; QQQ-based controls under M2 show degenerate t's by construction
(QQQ-residual is built from QQQ) — placebo gate is defined on M1 per prereg.
Integrity audit: two defects (phantom 2026-05-25 panel row, understates α; full-sample
QQQ-residual projection, overstates α) roughly cancel; no conclusion flips under either
fix or both.

## 4. Raw vs JSE table (all completed + today's adjudication)

| experiment | k | n | book | JSE − raw | significance | status |
|---|---|---|---|---|---|---|
| hunt2026 blind 1y | 1 | 60 | long-only min-var 2% cap | +15 bps net return | n/r | muted, direction + |
| hunt2026 5y | 1 | 60 | same | +10 bps CAGR | n/r | muted |
| hunt2026 44-window WF | 1 | 60 | same | median excess favors RAW by 0.1pp | n/r | "direction right" talking point retired |
| lab, n=252 unconstrained | 1/3/5 | 252 | shorts, cap 5% | +31/+18/+14 bps VOL (worse) | t 8–12, p<0.001 | JSE harmful |
| lab, n=252 long-only | 1/3/5 | 252 | long-only | +0.0/−0.6/−0.5 bps vol | t −8 | real, immaterial |
| lab, n=63 long-only | 1/3/5 | 63 | long-only | −1.3/−2.0/−1.6 bps vol | t −2 to −6.5 | designed regime, still bps |
| crossover | 3 | 42–252 | both | long-only −2.6→−0.5 bps; no crossover; ψ̂ no timing content | p<0.0001 | ceiling 2.6 bps/yr |
| factor gate | 5 | 63/252 | both | median +0.00 | — | redundant, gate never binds |
| theorem-complete (eq. 13) | 5 | 63/252 | both | +1.85 bps decisive; +30–50 unconstr. | p=0.0092 | wrong target (F-027) |
| hedge pair (statarb) | 1 | 63/252 | β-hedged L/S | Δ|β_SPY| −0.0004 | p=0.13 | no effect (F-028) |
| regime map (turnover) | 1 | 63/252 | 3 universes | +0.4–0.6 %-wt turnover, Δvol≈0 | t 6–12 | harmful (F-029) |
| **benchrel (NEW, one-shot)** | **1/3/5** | **63** | **tracking basket vs EW bench** | **ΔTE −0.04 bps (k=5)** | **p=0.42** | **verdict stands; MP best (2.33% TE)** |

Realized residual vol and concentration were never separately recorded (gap, disclosed);
tracking error is now covered by benchrel. Horse race: MP clipping best unconstrained
(11.27%) and best TE (2.33%); LW second; long-only pca1≈jse1 best (11.69%).

## 5. What is actually supported (hard evidence vs interpretation)

Hard: frozen-spec blind protocol integrity (bit-exact reproduction); placebo-calibrated
attribution pipeline; no live book clears preregistered alpha significance on its blind
window under any model M0–M3; the four best alpha cells decompose into gold beta,
financing, one 2022 regime, or an empty 1y cell; JSE effects bounded to bps in its best
regime and harmful outside it, across 10 preregistered experiments incl. today's
benchmark-relative adjudication; MP/LW dominate wherever shorts or tracking matter.

Interpretation (defensible, not proven): the books are competent implementations of
published premia (vol-managed equity, TSMOM, dual momentum, diversification); the
"unexplained residual" is most plausibly premia mis-measurement (no daily low-vol,
liquidity, or gold factor in the baseline set) plus regime luck, not idiosyncratic alpha;
JSE's null is structural (ψ̂→1 at S&P scale), so no amount of further S&P testing will
revive it — thin panels or a different asset class would be a different question.

## 6. What remains unknown

- Power: 1y cells cannot detect < ~12–28%/yr alpha; 5y cells < ~7.6%/yr. A true small
  alpha would be invisible. Only forward accumulation fixes this.
- No daily low-volatility, liquidity, or quality-beyond-RMW factor; gold entered only via
  the adversarial fix. A Barra-style cross-sectional model was not available.
- Residual statistical factors: vetted panel covers 61% of days, rank-chained, n=63
  windows, ~14% real-data false-pass on the C4 screen — usable as controls (they changed
  nothing), not as economic factors, and momentum_concentrated's M3 x2 cell is empty.
- Survivorship: momentum_concentrated's raw returns are overstated by missing delisted
  names (direction strengthens the negative verdict, but magnitude unquantified).
- The phantom 2026-05-25 panel row corrupts frozen book returns after that date (~6 weeks)
  — flagged for its own fix session; attribution conclusions verified robust to it.
- Economic identification: attribution proves exposure, not mechanism. Whether
  vol-managed timing is "skill in known premia" or "known premium, period" is a naming
  choice the t-stats cannot settle.

## 7. One recommended production action

**Keep the live book as a factor-premium harvesting strategy — no JSE deployment, no
allocation change — and re-base the standing 12-month paper review on factor-adjusted
NAV:** each book's kill/demote rule should be evaluated against its M2 factor replication
(betas frozen from this run's blind-window estimates, financing-stressed), not raw
excess-vs-SPY. The attribution pipeline (research/attribution/run_attribution.py) runs on
forward paper NAV as-is. This converts the power limitation into a live, pre-registered
forward test at zero additional trading risk; everything else (books, weights, JSE
non-deployment) stays frozen.

*Rejected reviewer recommendations: none — all adversarial riders were adopted verbatim.
Stop conditions honored: one adjudication run only; no post-result parameter changes.*
