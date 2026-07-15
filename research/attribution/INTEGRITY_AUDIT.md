# Integrity audit — EXP-2026-07-14-factor-attribution

Audited 2026-07-14 (Agent F). Scope: `research/attribution/run_attribution.py`,
`attribution.csv`, `ATTRIBUTION.md` vs the frozen prereg
`research/hunt2026/preregistrations/factor-attribution-2026-07-14.md` and
`research/hunt2026/harness.py`. All quantifications rerun with
`.venv/bin/python` against the live panel; no repo file other than this one
was written.

## Bottom line

**The headline conclusions stand.** No book reaches blind-window M2 t ≥ 2
under the as-run numbers, under either defect fix below, or under both
combined. The two real defects found bias in OPPOSITE directions and roughly
cancel: the phantom-row defect UNDERSTATES alpha (defensive_ensemble t
1.77 → 1.83 when fixed), the full-sample QQQ-residual projection OVERSTATES
it (t 1.77 → 1.73 when made PIT). The program verdict "factor-premium
harvesting with some unexplained residual return" is the correct prereg
mapping of the results in every variant tested.

## Findings, ranked by materiality

### F1 — Phantom 2026-05-25 panel row (Memorial Day, ^VIX only) — DEFECT, alpha UNDERSTATED here; corrupts frozen book scores elsewhere

**What.** `holdout.parquet` contains a 2026-05-25 row (US market holiday)
with data for exactly one ticker: ^VIX (16.59). Every tradable close is NaN.
Consequences:

1. In the harness, `pct_change` returns NaN on 05-25 AND 05-26 for every
   asset; `gross.fillna(0.0)` silently zeroes the book P&L both days — the
   real close(05-22)→close(05-26) market return never accrues to any book.
   (defensive_ensemble true 05-26 net: +1.91%; recorded: 0.00%.)
2. In `build_factors`, the NaN poisons `raw.rolling(63).std()`, so TSMOM (and
   hence the whole inner-joined factor frame) ends 2026-05-22 instead of the
   prereg end 2026-05-29 — the regressions silently drop the last 4 FF days
   (n = 219 vs 223 available for blind-1y, 1223 vs 1227 for blind-5y).
3. Worse, downstream of the attribution: the NaN propagates through
   spec-level realized-vol windows, so book weights/leverage AFTER 05-25 are
   corrupted in the frozen scores. defensive_ensemble June daily returns are
   ~3x smaller with the phantom row than without (e.g. 2026-06-05: −1.44%
   recorded vs −5.57% clean). The frozen `results5y/*.json` totals (and the
   hunt2026 "+18%" headline scores, which run to 2026-07-10) embed ~6 weeks
   of these corrupted returns. The attribution itself truncates at
   FF_END = 2026-05-29, so it only loses the 4 days.

**Quantified impact on this experiment** (panel with 05-25 row dropped,
factors rebuilt, book rerun):

| cell | as-run | fixed |
|---|---|---|
| defensive_ensemble blind M2 | +6.72%/yr, t=1.77, n=1223 | +6.93%/yr, t=1.83, n=1227 |
| dual_momentum_gem blind M2 | +15.79%/yr, t=1.12, n=219 | +16.90%/yr, t=1.22, n=223 |

**Direction:** as-run attribution alpha is UNDERSTATED (small). No decision
rule or verdict flips. But the phantom row should be removed from
`holdout.parquet` and the frozen post-05-25 book scores re-derived — that
defect lives in the hunt scorecard, not just here.

### F2 — QQQ-residual full-sample projection — mild look-ahead BY DESIGN (disclosed in prereg), alpha OVERSTATED

**What.** QQQRES is QQQ excess return orthogonalized to M1 with ONE
projection fit on the full 2015–2026 sample, exactly as the prereg wrote it.
This is look-ahead: the blind-window residual uses betas estimated partly
from blind-window data. Stability check: refitting only on pre-blind data
moves CMA (−0.19 → −0.35) and RMW loadings for the 5y cut; the blind-5y mean
of QQQRES is +0.76%/yr (full-sample projection) vs +1.95%/yr (PIT
projection). Since every trend/vol book loads positive on QQQRES, the
full-sample construction attributes LESS of the blind return to the QQQ
spread, i.e. inflates alpha.

**Quantified impact** (QQQRES rebuilt with projection fit ≤ 2021-07-09 only,
same regression):

| cell | full-sample proj (as-run) | PIT proj |
|---|---|---|
| trend_vol_qqq blind M2 | +9.11%/yr, t=1.50 | +8.25%/yr, t=1.36 |
| defensive_ensemble blind M2 | +6.72%/yr, t=1.77 | +6.53%/yr, t=1.73 |

**Direction:** as-run alpha OVERSTATED by ~0.2–0.9%/yr on the 5y books.
Roughly offsets F1. No verdict change. Prereg disclosed the design, so this
is a quantified caveat, not a protocol violation.

### F3 — Survivorship in momentum_concentrated's stock panel — real, but strengthens the negative conclusion

**What.** Membership is PIT (fja05680 change-log) but prices are yfinance:
148 of 777 ever-member names have ZERO price history in the panel, and 12.8%
of member-days (202,884 / 1,585,826) have member=1 with NaN close. Delisted/
acquired names are invisible to the momentum universe, and a held name that
delists simply stops contributing (implicit liquidation at last price, no
delisting loss). Both effects OVERSTATE momentum_concentrated's returns.
Its blind M2 alpha is already −7.5%/yr (t=−0.68); the true number is more
negative. The bias therefore cannot rescue the book — it makes the "no
residual alpha" conclusion for the only stock book conservative in the safe
direction. ETF books unaffected.

### F4 — PASS items (checklist)

1. **Timing / look-ahead alignment — PASS.** Harness `net[d] =
   W.shift(1)·pct_change` puts the close(d−1)→close(d) return at index d;
   FF daily factors use the same convention. Empirical: corr(SPY panel
   return, same-day Mkt−RF) = 0.995; ±1-day shifts drop to −0.11. SPY
   placebo R² = 0.996 confirms no off-by-one deflation.
2. **TSMOM proxy PIT — PASS.** Signal uses close.shift(21)/close.shift(273),
   held via `sig.shift(1)`, vol scale via `rolling(63).std().shift(1)`; all
   information available at the prior close. Blind-1y realized: mean
   +20%/yr at 11.5% ann vol (TSMOM genuinely worked; not an artifact).
3. **RF / excess / financing stress — PASS.** FF parquet is daily decimal
   (RF mean 1.7e-4); regressions use net_daily − RF; stress line implements
   the prereg formula alpha − max(avg_gross−1, 0)×(mean-window RF ann +
   0.50%) exactly. Minor: subperiod rows reuse the full-window avg_gross
   (context-only rows, no decision impact).
4. **NW self-checks — PASS.** `_selfcheck()` executes at import (verified by
   importing the module: betas ≡ lstsq, NW lag-5 SE > OLS SE under AR(1)
   ρ=0.5, lag-0 ≡ White HC0). Hand-rolled Bartlett meat is standard. Minor:
   no small-sample (n/(n−k)) correction — conventional, slightly
   anti-conservative, irrelevant at n ≥ 219.
5. **Blind boundaries / half-split — PASS.** `start="2025-07-10"` with the
   harness's `idx > start` yields first P&L day 2025-07-11; `"2021-07-10"`
   (Saturday) yields 2021-07-12; end truncated at FF_END 2026-05-29 — all
   exactly per prereg. Half-split is a row-count split of the joined
   regression frame (109/110 for the 1y books); faithful to "split in half".
6. **Multiple-testing / verdict mapping — PASS.** Rule 1 requires BOTH M2
   and M1 t ≥ 2 (defensive_ensemble M1 t=2.01 but M2 t=1.77 → correctly
   fails). The Bonferroni-adjusted t ≥ 2.4 bar is applied only in the
   "strong evidence" tier as prereg wrote it. With zero rule-1 passes and
   four books at alpha > 2%/yr with 1 ≤ t < 2, "factor-premium harvesting
   with some unexplained residual return" is the correct mapping.
7. **Controls — PASS.** SPY/QQQ hard gate |t| < 2 holds; the 1.5x-QQQ
   leverage-placebo failure on blind-5y (t=2.09) is correctly propagated as
   a rule-3 failure to all three 5y books (conservative, per prereg), and
   the free-financing mechanism given in the Story section is right
   (~0.5 × RF ≈ 2%/yr of mechanical alpha).
8. **Reproducibility — PASS** (with the F1 caveat). Integrity gate matched
   all 7 frozen total_net/sharpe to <1e-9, i.e. the regressions used exactly
   the frozen books — including their embedded phantom-row artifact.

### Checklist verdicts

| # | item | verdict |
|---|---|---|
| 1 | timing / factor alignment | PASS |
| 2 | TSMOM PIT / QQQ-residual construction | PASS with quantified caveat (F2, overstates ~0.2–0.9%/yr) |
| 3 | RF / excess / financing stress | PASS |
| 4 | NW self-checks | PASS |
| 5 | blind boundaries / half-split | PASS |
| 6 | multiple testing / verdict mapping | PASS |
| 7 | survivorship (momentum_concentrated) | FAIL as data quality, but bias direction strengthens the conclusion (F3) |
| 8 | other | FAIL: phantom 2026-05-25 panel row (F1) — understates attribution alpha; separately corrupts frozen June book scores |

## Recommended follow-ups (outside this experiment)

1. Remove the 2026-05-25 row from `research/hunt2026/holdout.parquet` (or
   drop all-but-^VIX rows at load) and regenerate the frozen results —
   the post-2026-05-25 stretch of every frozen score is contaminated.
2. If this attribution is rerun, drop the phantom row first and prefer the
   pre-blind (or expanding) QQQ-residual projection; both changes together
   move defensive_ensemble to roughly +6.7%/yr, t≈1.8 — same verdict.
3. Note in FLOOR/scorecard docs that momentum_concentrated's panel has
   ~13% member-day price gaps and 148 ever-member names with no history.
