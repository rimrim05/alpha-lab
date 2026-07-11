"""Experiment 5 — the PERMANENT Orthogonality Benchmark for the Additional Discovery Program.

v2 (2026-07-10): pre-registered dimensions frozen BEFORE EXP-A/EXP-B are evaluated. Thresholds
below are frozen; do NOT retune after seeing any experiment. A candidate must not pass merely
because full-period correlation is low — it must stay independent WHEN THE BOOKS ARE LOSING
(downside corr, tail dependence, drawdown overlap all gate independence).

Control set X = [1, SPY, QQQ, the 7 live books]. Reuses the frozen independence harness so the
control returns are identical to the runner's P&L convention.

FROZEN GATES (pre-registered):
  independence (ALL must hold):
    max_corr_to_book      < 0.50   full-period |corr| to any single book
    max_partial_corr      < 0.35   partial |corr| to any book, controlling for market + other books
    max_resid_corr_mkt    < 0.35   |corr| after removing SPY+QQQ from both
    downside_corr_ens     < 0.50   corr to the ensemble on negative-SPY days
    tail_dep_ens          < 0.40   co-exceedance in the worst 10% SPY days
    dd_overlap_lift       < 1.30   P(cand in DD | ensemble in DD) / P(cand in DD) — co-drawdown beyond base rate
    roll_corr_max_ens     < 0.65   worst 63d rolling |corr| to the ensemble (never spikes)
  edge:            resid_alpha_t > 2.0
  portfolio value: P(incr ensemble ΔSharpe > 0) > 0.90  OR  (incr ΔmaxDD < -0.02 AND incr ΔSharpe >= -0.02)
                   (the DD path requires not harming Sharpe, so pure dilution cannot pass)

FOUR OUTCOMES:
  NOT INDEPENDENT           — fails any independence gate (it's the cluster, esp. when books lose)
  INDEPENDENT BUT NO EDGE   — independent, no residual alpha, no portfolio value
  EDGE BUT NO PORTFOLIO VALUE— independent + residual alpha, but adds no ensemble Sharpe/DD benefit
  PORTFOLIO CANDIDATE       — independent + portfolio value (alpha OR pure diversification)

Run: .venv/bin/python research/discovery/orthogonality_benchmark.py   (frozen self-check)
Import: from orthogonality_benchmark import score_candidate
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
IND = ROOT / "research" / "independent_alpha" / "independence"
HUNT = ROOT / "research" / "hunt2026"
sys.path.insert(0, str(IND))
from compute_independence import book_returns, factor_returns, BOOKS  # noqa: E402

PROMOTED = ["vol_managed_qqq", "vol_core_svxy", "trend_vol_qqq", "defensive_ensemble"]

# ---- FROZEN thresholds (pre-registered 2026-07-10; do not retune after seeing EXP-A/B) ----
T_CORR, T_PARTIAL, T_RESID = 0.50, 0.35, 0.35
T_DOWN, T_TAIL, T_DD_LIFT, T_ROLL = 0.50, 0.40, 1.30, 0.65
T_ALPHA_T, T_INCR_P, T_DD_CUT = 2.0, 0.90, -0.02


def _load_panel_frames():
    panel = pd.read_parquet(HUNT / "panel_2005.parquet")
    books = book_returns(panel)
    factors = factor_returns(panel)
    df = books.join(factors, how="inner").dropna()
    active = (books.reindex(df.index).abs().sum(axis=1) > 0)
    df = df.loc[active[active].index.min():]
    return df[list(BOOKS)], df[["SPY", "QQQ"]]


def _ann_sharpe(r):
    s = np.std(r)
    return float(np.mean(r) / s * np.sqrt(252)) if s > 0 else 0.0


def _max_dd(r):
    nav = (1 + pd.Series(np.asarray(r))).cumprod()
    return float((nav / nav.cummax() - 1).min())


def _ols_resid(y, Z):
    coef, *_ = np.linalg.lstsq(Z, y, rcond=None)
    return y - Z @ coef, coef


def _block_bootstrap(ens, cand, block=21, reps=2000, seed=0):
    w = ens.std() / cand.std() if cand.std() > 0 else 0.0
    treat = ens + w * cand
    treat = treat * (ens.std() / treat.std()) if treat.std() > 0 else treat
    d_sharpe = _ann_sharpe(treat) - _ann_sharpe(ens)
    d_maxdd = _max_dd(treat) - _max_dd(ens)     # negative = candidate reduces drawdown
    rng = np.random.default_rng(seed)
    n = len(ens); nb = int(np.ceil(n / block)); e, t = ens.values, treat.values
    wins = sum(_ann_sharpe(t[(idx := (rng.integers(0, n - block, nb)[:, None] + np.arange(block)).ravel()[:n])])
                          - _ann_sharpe(e[idx]) > 0 for _ in range(reps))
    return d_sharpe, d_maxdd, wins / reps


def score_candidate(candidate: pd.Series, label: str = "candidate") -> dict:
    books, factors = _load_panel_frames()
    df = pd.concat([candidate.rename("cand"), books, factors], axis=1, join="inner").dropna()
    if len(df) < 252:
        raise ValueError(f"{label}: {len(df)} overlapping days < 252")
    cand = df["cand"]
    ens = df[PROMOTED].mean(axis=1)

    # (1) full-period corr to each book
    corr_to_books = df[list(BOOKS)].apply(lambda c: cand.corr(c))
    max_corr = float(corr_to_books.abs().max())

    # (2) partial corr to each book, controlling for market + the other books
    mkt = df[["SPY", "QQQ"]].values
    partials = {}
    for b in BOOKS:
        others = [x for x in BOOKS if x != b]
        Z = np.column_stack([np.ones(len(df)), mkt, df[others].values])
        rc, _ = _ols_resid(cand.values, Z)
        rb, _ = _ols_resid(df[b].values, Z)
        partials[b] = float(np.corrcoef(rc, rb)[0, 1])
    max_partial = max(abs(v) for v in partials.values())

    # (3) residual alpha after [1, SPY, QQQ, 7 books] + residual-vs-market corr
    Xcols = ["SPY", "QQQ"] + list(BOOKS)
    X = np.column_stack([np.ones(len(df)), df[Xcols].values])
    resid, coef = _ols_resid(cand.values, X)
    dof = len(df) - X.shape[1]
    se = np.sqrt((resid @ resid) / dof * np.linalg.inv(X.T @ X)[0, 0])
    alpha_ann, alpha_t = coef[0] * 252, (coef[0] / se if se > 0 else 0.0)
    resid_sharpe = _ann_sharpe(resid)
    fX = np.column_stack([np.ones(len(df)), mkt])
    cand_rm, _ = _ols_resid(cand.values, fX)
    max_resid_corr = max(abs(np.corrcoef(cand_rm, _ols_resid(df[b].values, fX)[0])[0, 1]) for b in BOOKS)

    # (4) downside corr to ensemble on negative-SPY days
    neg = df[df["SPY"] < 0]
    downside_corr = float(neg["cand"].corr(neg[PROMOTED].mean(axis=1)))

    # (5) tail dependence: worst-10% SPY days, co-exceedance of candidate lower decile
    worst = df[df["SPY"] <= df["SPY"].quantile(0.10)]
    cand_low = cand <= cand.quantile(0.10)
    tail_dep = float(cand_low.reindex(worst.index).mean())  # P(cand in its low decile | worst SPY day)

    # (6) drawdown overlap as LIFT: co-drawdown beyond the candidate's own base rate
    #     (raw overlap is contaminated — a zero-drift series is in DD ~always; lift ~1 = independent)
    def _in_dd(r):
        nav = (1 + r).cumprod(); return nav < nav.cummax()
    ens_dd = _in_dd(ens); cand_dd = _in_dd(cand)
    p_cand = float(cand_dd.mean())
    p_cand_given_ens = float((cand_dd & ens_dd).sum() / ens_dd.sum()) if ens_dd.sum() else 0.0
    dd_overlap_lift = (p_cand_given_ens / p_cand) if p_cand > 0 else 0.0

    # (7) rolling 63d corr stability to the ensemble + breach diagnostics (frozen verdict unchanged;
    #     these are REPORTING fields for future reports, not new gates)
    roll = cand.rolling(63).corr(ens).dropna()
    roll_abs = roll.abs()
    roll_corr_max = float(roll_abs.max()) if len(roll) else 0.0
    roll_corr_median = float(roll.median()) if len(roll) else 0.0
    breach = roll_abs >= T_ROLL
    breach_count = int(breach.sum())
    # longest consecutive run of breaches (in trading days)
    breach_max_run = int(breach.groupby((~breach).cumsum()).sum().max()) if breach.any() else 0
    # which single book the candidate co-moves with most in its worst 63d window (failure attribution)
    per_book_worst = {b: float(cand.rolling(63).corr(df[b]).abs().max()) for b in BOOKS}
    worst_book = max(per_book_worst, key=per_book_worst.get)

    # (8) incremental ensemble Sharpe + maxDD effect; marginal contribution to risk
    d_sharpe, d_maxdd, p_incr = _block_bootstrap(ens, cand)
    w = ens.std() / cand.std() if cand.std() > 0 else 0.0
    port = ens + w * cand
    mcr_share = float(w * np.cov(cand, port)[0, 1] / port.var()) if port.var() > 0 else 0.0

    gate_checks = [
        ("max_corr_to_book", max_corr, T_CORR), ("max_partial_corr", max_partial, T_PARTIAL),
        ("max_resid_corr_mkt", max_resid_corr, T_RESID), ("downside_corr_ens", downside_corr, T_DOWN),
        ("tail_dep_ens", tail_dep, T_TAIL), ("dd_overlap_lift", dd_overlap_lift, T_DD_LIFT),
        ("roll_corr_max_ens", roll_corr_max, T_ROLL),
    ]
    failed = [name for name, v, thr in gate_checks if not (v < thr)]
    indep = not failed
    binding_gate = failed[0] if failed else None
    edge = alpha_t > T_ALPHA_T
    pval = (p_incr > T_INCR_P) or (d_maxdd < T_DD_CUT and d_sharpe >= -0.02)
    if not indep:
        tag = "NOT INDEPENDENT"
    elif pval:
        tag = "PORTFOLIO CANDIDATE"
    elif edge:
        tag = "EDGE BUT NO PORTFOLIO VALUE"
    else:
        tag = "INDEPENDENT BUT NO EDGE"

    return {
        "label": label, "n_days": len(df), "window": f"{df.index[0].date()}..{df.index[-1].date()}",
        "max_corr_to_book": round(max_corr, 3), "argmax_corr_book": corr_to_books.abs().idxmax(),
        "max_partial_corr": round(max_partial, 3), "max_resid_corr_mkt": round(max_resid_corr, 3),
        "downside_corr_ens": round(downside_corr, 3), "tail_dep_ens": round(tail_dep, 3),
        "dd_overlap_lift": round(dd_overlap_lift, 3),
        "roll_corr_max_ens": round(roll_corr_max, 3), "roll_corr_median_ens": round(roll_corr_median, 3),
        "roll_breach_count": breach_count, "roll_breach_max_run_days": breach_max_run,
        "worst_book": worst_book, "binding_gate": binding_gate,
        "responsible_book": (worst_book if not indep else None),
        "resid_alpha_ann": round(float(alpha_ann), 4), "resid_alpha_t": round(float(alpha_t), 2),
        "resid_sharpe": round(resid_sharpe, 2), "mcr_share": round(mcr_share, 3),
        "incr_ens_dSharpe": round(float(d_sharpe), 3), "incr_ens_dMaxDD": round(float(d_maxdd), 3),
        "incr_ens_P_gt0": round(float(p_incr), 3),
        "gates": {"independent": indep, "edge": edge, "portfolio_value": pval},
        "outcome": tag,
    }


def _selfcheck():
    books, factors = _load_panel_frames()
    idx = books.join(factors, how="inner").dropna().index
    spy = factors["SPY"].reindex(idx)
    rng = np.random.default_rng(7)

    # 1) existing book -> NOT INDEPENDENT
    dup = score_candidate(books["vol_core_svxy"].reindex(idx), "dup:vol_core_svxy")
    assert dup["outcome"] == "NOT INDEPENDENT", dup

    # 2) orthogonal noise -> INDEPENDENT BUT NO EDGE
    noise = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    n = score_candidate(noise, "noise")
    assert n["outcome"] == "INDEPENDENT BUT NO EDGE", n

    # 3) orthogonal noise + drift -> PORTFOLIO CANDIDATE
    e = score_candidate(pd.Series(rng.normal(0.0006, 0.008, len(idx)), index=idx), "noise+drift")
    assert e["outcome"] == "PORTFOLIO CANDIDATE", e

    # 4) LOW full-period corr but co-crashes with the ensemble in the worst decile -> NOT INDEPENDENT
    #    (proves the tail gate bites even when full-period corr is well under 0.50)
    ens = books.reindex(idx)[PROMOTED].mean(axis=1)
    worst10 = spy <= spy.quantile(0.10)
    downonly = pd.Series(rng.normal(0, 0.012, len(idx)), index=idx)   # noise dominates most days
    downonly[worst10] = ens[worst10]                                  # co-crash only in worst decile
    d = score_candidate(downonly, "tail-co-crash")
    assert d["outcome"] == "NOT INDEPENDENT", d
    assert d["max_corr_to_book"] < T_CORR, d       # full-period corr passes...
    assert d["tail_dep_ens"] >= T_TAIL, d           # ...but the tail gate fires

    print("SELF-CHECK PASSED (v2, 8 dimensions, 4 outcomes)")
    for r in (dup, n, e, d):
        print(f"  {r['label']:22s} {r['outcome']:28s} corr={r['max_corr_to_book']:.2f} "
              f"partial={r['max_partial_corr']:.2f} down={r['downside_corr_ens']:.2f} "
              f"tail={r['tail_dep_ens']:.2f} αt={r['resid_alpha_t']:.1f} P(incr)={r['incr_ens_P_gt0']:.2f}")


if __name__ == "__main__":
    _selfcheck()
