# Earnings-lane checkpoint (armed, dormant) — 2026-07-10

The Discovery Program is in maintenance mode. The earnings lane (EXP-IC-EARNINGS-FWD) is the highest-
value unresolved lane but **data-gated**. This checkpoint is **armed**: it fires the IC report ONLY
when all six pre-registered conditions hold, and stays silent otherwise. Gate:
[earnings_checkpoint.py](earnings_checkpoint.py) (read-only; no scheduler; no deployment change).

## Arming conditions (ALL must be true)
1. **≥300 eligible point-in-time events fully MATURED through the 20-trading-day horizon** — maturity
   = reaction_date + 20 trading days ≤ today on the panel calendar. **NOT the raw collector count**:
   the gate does not surface merely because the store reaches 300 rows.
2. event timestamps / estimates / actuals / availability (`pulled_at`) fields pass the data-quality audit.
3. sector and issuer concentration are reported (issuer HHI + top-5 share; sector shares via
   `sectors.parquet`, unmapped count flagged).
4. missing-event and API-failure rates are quantified.
5. the pre-registered pass/kill thresholds are unchanged — N_PRIMARY=300, N_KILL=600, 20d rank
   IC ≥ 0.03 with t ≥ 2 (pass); n≥600 & (IC<0.01 or t<1) (kill). The gate asserts the collector's
   constants still equal these; a mismatch fails condition 5.
6. no portfolio construction before the IC result (no earnings-based book in `BOOKS`).

Current status (2026-07-11): **NOT ARMED — 0/300 matured. Maintaining silently.**

## When armed, the checkpoint returns ONLY
- eligible event count by horizon (5/20/60);
- rank IC (frozen Spearman) and Pearson IC where applicable;
- pre-registered uncertainty (the frozen t = IC·√(n−2)/√(1−IC²); events are largely non-overlapping,
  so HAC is not required — noted, not silently assumed);
- hit rate;
- IC decay across 5, 20, 60 days;
- sector and regime dependence;
- turnover implications;
- data-quality exceptions;
- verdict: **measurement supported / inconclusive / killed** (from the frozen collector thresholds).

## Discipline
- The verdict and thresholds come from the FROZEN EXP-IC-EARNINGS-FWD prereg + `earnings_collect.py`
  (`report()`, `compute_sue`, `rank_ic`). The gate reuses them; it does not redefine SUE, horizons,
  or thresholds.
- No portfolio is built before the IC result. A KILL sends the hypothesis to FAILURES.md and no
  earnings-surprise spec is proposed; the dataset keeps accruing as infrastructure either way.
- Evaluated read-only (run the gate, or fold its one-line status into the collector's existing nightly
  health review — no new scheduler added in maintenance mode). Do not surface the lane early.
