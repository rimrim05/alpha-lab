# Experiment 5 — Orthogonality Benchmark (permanent gate, v2 frozen 2026-07-10)

The permanent Stage-4 residual-independence test. Every discovery candidate clears it before it
can be called independent. Implementation: [orthogonality_benchmark.py](orthogonality_benchmark.py).
**v2 thresholds are frozen BEFORE EXP-A / EXP-B are evaluated — not retuned after seeing results.**

## Control set
`X = [1, SPY, QQQ, the 7 live books]` on the runner's exact P&L convention (reuses the frozen
`compute_independence` reconstruction).

## Frozen dimensions & thresholds
Independence requires **all** of these (a candidate must stay independent *when the books lose*,
so the downside/tail/drawdown gates can fail it even at low full-period correlation):

| dimension | field | gate |
|---|---|---|
| full-period corr to any book | `max_corr_to_book` | < 0.50 |
| partial corr to any book (control market + other books) | `max_partial_corr` | < 0.35 |
| corr after removing SPY+QQQ | `max_resid_corr_mkt` | < 0.35 |
| downside corr to ensemble (negative-SPY days) | `downside_corr_ens` | < 0.50 |
| tail dependence (worst 10% SPY days) | `tail_dep_ens` | < 0.40 |
| drawdown-overlap **lift** P(cand DD\|ens DD)/P(cand DD) | `dd_overlap_lift` | < 1.30 |
| rolling 63d corr stability (worst) | `roll_corr_max_ens` | < 0.65 |

- **Edge:** `resid_alpha_t` > 2.0 (alpha after the full control set).
- **Portfolio value:** `incr_ens_P_gt0` > 0.90 **or** (`incr_ens_dMaxDD` < −0.02 **and**
  `incr_ens_dSharpe` ≥ −0.02). The DD path requires not harming Sharpe, so pure dilution can't pass.
- Also reported (not gated): `resid_sharpe`, `mcr_share` (marginal risk contribution),
  `incr_ens_dSharpe`, `incr_ens_dMaxDD`.

**Diagnostic context (report these in every future candidate report — frozen verdict unchanged):**
`roll_breach_count` and `roll_breach_max_run_days` (number and duration of rolling-corr breaches),
`roll_corr_median_ens` and `roll_corr_max_ens` (median and worst rolling corr), `downside_corr_ens`
and `tail_dep_ens` (downside/tail correlation), `dd_overlap_lift` (drawdown-overlap lift),
`binding_gate` (which gate failed first) and `responsible_book`/`worst_book` (the existing book the
candidate co-moves with most in its worst window). These explain *why* a candidate failed, not just
that it did — e.g. EXP-A failed on `roll_corr_max_ens` driven by the vol/trend books in risk-off windows.

## Four outcomes
1. **NOT INDEPENDENT** — fails any independence gate.
2. **INDEPENDENT BUT NO EDGE** — independent, no residual α, no portfolio value.
3. **EDGE BUT NO PORTFOLIO VALUE** — independent + residual α, but no ensemble Sharpe/DD benefit.
4. **PORTFOLIO CANDIDATE** — independent + portfolio value (from α *or* pure diversification).

## Self-check (runnable) — passed v2, 2026-07-10
- existing book (`vol_core_svxy`) → **NOT INDEPENDENT** (corr 1.00) ✓
- orthogonal noise → **INDEPENDENT BUT NO EDGE** (corr 0.02, α t −1.3, P(incr) 0.01) ✓
- orthogonal noise + drift → **PORTFOLIO CANDIDATE** (corr 0.03, α t 5.5, P(incr) 1.00) ✓
- **tail-co-crash** (co-losing only in the worst decile) → **NOT INDEPENDENT** despite full-period
  corr 0.36 < 0.50, caught by `tail_dep_ens` 0.50 ≥ 0.40 ✓ — proves low full-period corr does not buy a pass.

## Usage
```python
from orthogonality_benchmark import score_candidate
report = score_candidate(candidate_daily_returns, label="my-candidate")  # -> dict incl. "outcome"
```
Candidate = daily net returns, DatetimeIndex overlapping the panel (≥252 days). Fixed bootstrap
seed → reproducible.

## Limits (honest)
- Control set is SPY+QQQ+7 books; sector factors are a noted future extension.
- Equal-weight promoted ensemble for the incremental test (each book is already vol-shaped).
- A pass is necessary, not sufficient — Stage-5 Red Team (cost stress, execution delay, regime,
  clean-room replication) still follows.
