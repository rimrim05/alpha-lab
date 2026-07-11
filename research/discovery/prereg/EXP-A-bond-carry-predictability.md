# PREREG EXP-A — Bond-carry predictability (measurement, not a portfolio)

*Frozen 2026-07-10 (Discovery Program). Unlocked by DATA_QUALITY_REPORT.md = PASS. Nothing above
the Result line may be edited after the first scoring run. This is a Stage-1 MEASUREMENT test — no
portfolio is constructed and no book is proposed until the predictive + orthogonality gates pass.*

- **Experiment ID:** EXP-2026-07-10-bond-carry-predictability
- **Layer touched (one):** A — economic phenomenon (does a carry MEASURE predict future returns?)
- **Alpha type:** market (carry), low-frequency, small cross-section. NEW information source
  (FRED PIT rates), not a price/volume transform.

**Hypothesis (one falsifiable sentence, mechanism):** A point-in-time bond carry+roll-down measure
— yield minus financing plus roll-down — ranks future returns across the Treasury duration ladder
(SHY 1-3y, IEF 7-10y, TLT 20+y), because carry compensates holders for bearing duration/term risk
that is not arbitraged away at monthly frequency; and this predictability is **economically
orthogonal** to the US-equity/QQQ/trend/vol cluster (low equity beta is the whole point).

**Who pays / why it persists / what kills it:** duration-averse liability holders and rate-hedgers
pay the term premium; it persists because carry is a risk premium, not a free lunch; it disappears
in rate-shock regimes (2022) and when the curve inverts (negative carry). Pre-registered so a 2022
in-sample stress cannot be hidden.

**Data:** `../data/state_aligned.parquet` (PIT, avail-lagged) for yields (DGS2→SHY, DGS10→IEF,
DGS30→TLT mapping), DFF (financing), and the roll-down proxy; `panel_2005.parquet` for ETF returns.
Rates enter at their availability lag (1 BDay) — the decision at close t uses rates dated ≤ t−1.

**Carry measure (fixed, un-tuned):** for bucket i, `carry_i = yield_i − DFF + rolldown_i`, with
`rolldown_i` the layer's transparent slope proxy. Cross-sectional z-score across the 3 buckets each
month. No parameter is fit.

**Control:** unconditional — equal-weight duration ladder (and single-bucket buy-hold), no carry input.
**Treatment:** carry-ranked exposure — long the highest-carry bucket, underweight the lowest (or
carry-z-weighted), monthly.

**Primary statistic:** pooled predictive regression of forward 21d bucket return on carry z-score,
Newey-West t (overlap-robust); AND monthly rank IC of carry vs forward return across the 3 buckets.
**Secondary:** residual return after duration beta; rolling stability; cost-adjusted effect (ETF
spreads, monthly turnover); **equity beta** (regress the carry-sleeve daily return on SPY+QQQ);
**orthogonality** — run the carry-sleeve daily return through
`../orthogonality_benchmark.py` (must read INDEPENDENT: max_corr_to_book < 0.5).

**Universe / sample / holdout:** SHY, IEF, TLT (+ BIL cash), 2005-01-03 → 2026-07. Parameter-free ⇒
primary runs full-sample; **blind holdout = last 24 months (2024-07→2026-06)** — carry coefficient
and IC sign must not flip. Inspect only pre-2024-07 first.

**Forecast + execution timestamps:** carry known at close t (rates dated ≤ t−1); forward return
t+1…t+21. Monthly rebalance at close.

**Expected effect:** carry coefficient > 0 (t > 2); equity beta ≈ 0 (|β_SPY| < 0.1); orthogonality
PASS. Honest prior P(supported) ≈ 0.5 — bond carry is real but decayed and rate-regime-sensitive.
**Alternative:** significant carry predictability but with material equity/duration beta ⇒ NOT
independent, not a discovery.

**Failure / kill condition (decidable, stop-iterating):** carry coefficient |t| < 2 (no
predictability) OR material equity beta OR fails the orthogonality gate → **REJECTED / BLOCKED**;
do NOT build a carry portfolio, and do not test further carry proxies on the Treasury ladder without
a materially different instrument set (FX/commodity carry stays BLOCKED BY DATA per CARRY_FEASIBILITY.md).

**Cost model:** ETF bid/ask + commission per rebalance; monthly cadence keeps turnover low. No borrow
if long-only ladder; if long/short, model TLT/SHY borrow.

**Leakage / survivorship:** rates lagged 1 BDay; forward returns start t+1; ETF-only (no delisting).
`state_aligned.parquet` passed future-poison + truncation audits (DATA_QUALITY_REPORT.md).

**Parameter count:** 0 fit (fixed carry formula, fixed ladder). **Complexity:** 2/5. **Information
gain:** HIGH — the first non-price/volume *market* source Alpha Lab has measured; a clean PASS is a
genuine independent-candidate, a clean kill closes the free-data carry lane.

**Decision changed by success:** advance to Stage-2 replication (era/instrument) then the
orthogonality/portfolio gates → SHADOW-PAPER CANDIDATE (never funded without Stage-4).
**Decision changed by failure:** bond carry joins the Failure DB; the only remaining carry reopen is
vendor-gated FX/commodity term structure.

**Trial-ledger entry:** TRIAL_LEDGER #23 (Discovery / measurement) at first score.

---
**Result** (filled after the run, never edited above this line):
