# FORECAST_SCOREBOARD.md — predictive-content evidence, by signal class (Agent 6)

Auditor: Agent 6 (IC & Forecast scoreboard), 2026-07-10. This is a **summary of evidence
that already exists** — no new runs. Every number is transcribed from the cited artifact;
where a doc and a ledger disagree, the ledger/code wins. Reuse, do not rebuild.

Purpose: answer one question per candidate — **does the measured predictive statistic clear
the pre-registered gate that earns a portfolio?** The gate differs by alpha type, so the
right statistic differs too. An estimator or portfolio-construction win is NOT a market
forecast and is scored on its own axis.

---

## The gates (what each alpha type must clear before it earns a book)

| Alpha type | Right statistic | Pre-registered gate | Source of gate |
|---|---|---|---|
| **Market — cross-sectional (XS)** | Spearman rank IC vs forward return, t = mean/std·√n | **\|t\| ≥ 2** at a tested horizon, and a **sign stable across half-decades** | `robustness/ic_screen.md` verdict; FAILURES rule after F-016 ("every future XS signal reports rank IC before any portfolio is built") |
| **Market — event (earnings/news)** | Conditional abnormal return in an event window, PIT-flagged | **n ≥ 300** PIT events before scoring (pre-committed) | `preregistrations/exp-ic-earnings-fwd-2026-07-10.md`; DATA_GAP_MAP §2.6 |
| **Market — time-series (TS) / risk-mgmt** | Forecast-return: WF median excess vs the book's **own naive** benchmark + DSR | **Positive WF median excess across the 82-window walk-forward** + DSR clears luck-max | CONFIDENCE_LADDER level 3; `walkforward/summary.md`; `robustness/deflated.md` |
| **Estimator** | Matched-pair realized-risk delta (jse−pca), paired t | Significant delta **in the designed regime only** | `research/estimator_lab/` (F-021 chain) |
| **Portfolio** | Sleeve WF role delta (drawdown/hit-rate vs excess) | Positive median excess + role confirmed | CONFIDENCE_LADDER (defensive_ensemble = level 3) |
| **Execution** | Spread capture / open-vs-close fill delta | **Not measurable on current data** | DATA_GAP_MAP §2.15 (daily O/C only, no intraday/auction/tick) |

---

## 1. Cross-sectional (XS) rank-IC scoreboard — the headline

**10 price/volume signals screened, monthly rank IC, PIT S&P 500 members 2015-01→2026-03
(135 months). Sign pre-oriented so IC > 0 = works as hypothesized. `robustness/ic_screen.md`,
`ic_screen_stats.csv`.** Pipeline validated against `ic.md`: 12-1 momentum reproduces to the
4th decimal (mean IC −0.0014, t −0.07) before screening.

| # | Signal | Family | IC 21d | t 21d | IC 63d | t 63d | Sign stable across ½-decades? | Gate \|t\|≥2? | F-entry |
|---|---|---|---|---|---|---|---|---|---|
| 1 | st_reversal_21d | reversal | +0.005 | 0.34 | +0.005 | 0.32 | No (+0.036 → −0.011 → −0.053) | **FAIL** | F-017 |
| 2 | sector_rel_mom_12_1 | momentum | +0.001 | 0.03 | +0.009 | 0.59 | No | **FAIL** | F-016 add. |
| 3 | residual_mom_12_1 | momentum | +0.004 | 0.27 | +0.017 | **1.22** | No | **FAIL** (best of 10 = expected max of 10 noise draws) | F-016 add. |
| 4 | ivol_60d_low | vol | +0.002 | 0.16 | +0.005 | 0.31 | No (−0.05 to −0.10 in 2025) | **FAIL** | F-018 |
| 5 | dispersion_resid_21d | reversal | −0.001 | −0.09 | −0.006 | −0.61 | No | **FAIL** | F-017 |
| 6 | volume_shock | microstructure | +0.001 | 0.13 | −0.003 | −0.43 | No | **FAIL** | F-019 |
| 7 | overnight_share_126d | microstructure | −0.002 | −0.21 | −0.006 | −0.48 | No | **FAIL** | F-019 |
| 8 | gap_persistence_63d | microstructure | +0.002 | 0.25 | +0.003 | 0.52 | No | **FAIL** | F-019 |
| 9 | low_vol_60d | vol | −0.006 | −0.29 | −0.010 | −0.50 | No | **FAIL** | F-018 |
| 10 | high_52w_prox | momentum | −0.000 | −0.02 | +0.006 | 0.32 | No | **FAIL** | F-016 add. |

n = 135 months (residual_mom 133). **0/10 clear \|t\| ≥ 2 at either horizon; none holds a
stable sign across 2015-19 / 2020-24 / 2025-26** (`ic_screen_byhalf.csv`). This is not weak
alpha — it is regime-flipping noise. The three momentum variants are ~0.97-correlated by-year
with raw 12-1 momentum: F-016's corpse with a sector hedge, not new information.

**XS verdict:** the cross-sectional stock-selection track on daily open/close/volume, S&P 500
large caps, post-2015, is **CLOSED**. Corroborated in return space by F-015 (momentum_concentrated
WF −4.6pp median excess) → aggregated as **NR-2, STRONG against**. Do not build a portfolio on
any row. Reopen only per F-016: a different universe (small caps — blocked by the survivorship
gap, DATA_GAP_MAP §2.4), interaction conditioning (momentum × dispersion / × earnings), or IC
returning in live regime monitoring.

---

## 2. Event alpha (earnings / news) — CANNOT be IC-tested now, forward-collect only

No point-in-time earnings/analyst data exists in the repo (CANONICAL_STATE; DATA_GAP_MAP §§2.6-2.9).

- **EPS-surprise drift (PEAD):** the honest PIT collector (`earnings_collect.py`, Finnhub) has
  **8 events / 2 names** as of 2026-07-10 vs a pre-registered **n ≥ 300** gate. Months from
  testable. The existing `statarb_earnings.parquet` surprise is **look-ahead** (current-vintage
  consensus, revised after the fact) and is excluded from scoring. `gap_drift` (F-009) is the
  price-only PEAD proxy — WATCH tier, never tested against *real* surprises.
- **Revenue surprise, analyst revisions, coverage/dispersion:** **BLOCKED-WITHOUT-VENDOR**
  (need I/B/E/S / WRDS). Un-testable at any n on free data.
- **News sentiment:** FORWARD-COLLECTABLE — `news.parquet` is only ~10 months deep (2025-09→).

**Event verdict:** 0 pass today; **none is even scoreable** — this lane is forward-collected,
not failed. Do not read the absence of a pass as a negative result.

---

## 3. Time-series / risk-management (forecast-return) — the only market lane with passes

These are **not** rank-IC signals. They forecast the *return of an exposure through time*
(lever/de-lever beta on a vol or trend state), scored by WF median excess vs the book's own
naive benchmark + DSR (`walkforward/summary.md`, `deflated.md`). Passing here earns a book but
is **market-timing / risk-management alpha, mostly "vol-managed beta" honestly priced — not a
cross-sectional forecast.**

| Book | ann Sharpe | DSR | WF median excess vs SPY | Gate (positive WF median + DSR) | Ladder |
|---|---|---|---|---|---|
| vol_managed_qqq | 0.94 | 81.5% | +13.4pp (78% beat-SPY) | **PASS** | 3 |
| vol_core_svxy | 0.93 | 81.2% | +12.4pp (85% beat-SPY) | **PASS** | 3 |
| trend_vol_qqq | 1.11 | 89.8% | +8.0pp median (combo halves either parent's +13.4pp — F-014) | **PASS (robustness), tail-hedge value only** | 3 |

Caps on this lane:
- **Cross-market replication was RUN and FAILED** (F-020, `xmarket.md`): frozen params on 28
  assets / 7 clusters → vol-mgmt improves 3/7 (sign-test p=0.77), trend gate 4/7 (p=0.50) —
  a coin flip. Edge is **CONFIRMED US-large-cap-equity-specific**; ladder capped at level 3
  with a penalty (level 4 refused, not merely unattempted).
- **F-014:** trend+vol combo halves median excess; claim it as a priced tail hedge (worst
  window −31% → −22%), never as additive alpha.
- Watch-tier TS/cross-asset momentum books (dual_momentum_gold DSR 87.7%, dual_momentum_gem
  68.2%, tsmom_multi_asset 79.8%) are held for **forward** evidence, not promoted.

**TS verdict:** 3 books clear the forecast-return gate, all one US-equity vol/trend
risk-management cluster. This is Market alpha of the risk-management kind, not independent
cross-sectional forecasting.

---

## 4. Estimator alpha — improvement, not a market forecast (F-021 chain)

The Goldberg/JSE dispersion-bias correction (`research/estimator_lab/`): matched-pair realized-vol
delta. Final bounded form — **long-only always helps, monotone in p/n** (−2.6 bps vol at n=42 →
−0.5 bps at n=252, always p<0.0001); **unconstrained always hurts** (+18 to +49 bps). No
month-level ψ̂ timing signal exists. Real but tiny (max ~2.6 bps vol/yr); confirmed and
correctly bounded. **This is Estimator alpha (a better covariance) — it forecasts nothing about
the market and earns no standalone book.**

---

## 5. Execution alpha — NOT MEASURABLE on current data

Daily open/close only; no minute bars, no auction cross, no tick (DATA_GAP_MAP §2.15). Spread
capture / open-vs-close fill deltas cannot be computed. **No book here may claim execution
alpha.** F-006 (overnight premium) is explicitly reopened *only* when an open+close execution
harness exists — the effect is real, the daily convention was the constraint.

---

## Bottom line

| Lane | Statistic | Passing the gate today |
|---|---|---|
| XS market (rank IC) | \|t\| ≥ 2 rank IC, stable sign | **0 of 10** |
| Event market | n≥300 PIT conditional return | 0 (un-scoreable: 8/300 events; rest vendor-blocked) |
| TS market (forecast-return) | WF median excess + DSR | 3 books (one US-equity vol/trend cluster) |
| Estimator | matched-pair vol delta | improvement only, not a forecast, no book |
| Portfolio | sleeve WF role delta | defensive_ensemble (level 3), portfolio not forecast |
| Execution | spread capture | not measurable |

**Signals passing the IC gate today: 0.** Zero of ten cross-sectional price/volume signals
clear \|t\| ≥ 2 rank IC — the cross-sectional forecasting track is closed pending a new
information source. The three promoted TS books are risk-management (market-timing) alpha, not
independent cross-sectional forecasts, and the event lane cannot yet be scored for lack of PIT
data.
