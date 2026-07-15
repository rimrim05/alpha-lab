# Pre-registration — open+close execution: is the overnight premium exploitable at frozen costs?

### EXP-2026-07-14-open-close

**Hypothesis** (one falsifiable sentence, mechanism included):
Under real open+close execution (buy the close, sell the next open), the equity overnight
premium — the fact that most of the close-to-close return accrues outside regular hours —
survives the frozen 2 bps/side ETF cost model on SPY and QQQ, because the premium
(~9%/yr per F-006's stock-panel estimate) exceeds the ~10.1%/yr cost of two trades per day.
The arithmetic already makes this doubtful; this experiment closes F-006 with a measured
answer instead of a guess.

**Layer touched** (exactly one) + registered baseline:
Layer D — execution convention only. A research-lane open+close P&L engine is added in the
robustness script; **harness.py is NOT modified** (the frozen books' published results
depend on it). Registered baseline = buy-and-hold SPY/QQQ through the same engine.
Engine gates before any variant counts:
(a) nesting — the new engine in close-executed mode reproduces harness.run on the frozen
    vol_managed_qqq spec exactly (net series max abs diff < 1e-12);
(b) composition identity — per day, (1+r_overnight)(1+r_intraday) = (1+r_close-to-close)
    to < 1e-12 on both ETFs;
(c) data validity (already verified pre-registration, data-quality only, no P&L computed):
    100% open coverage, opens ≠ closes (real opens), open/close adjustment basis consistent
    across the AAPL 2020 4:1 split.

**Alpha type tag**: execution

**Expected result** (numeric, on which evaluator):
Full panel 2005→2026, full-period stats gross and net. Expected: overnight-only gross
captures 50–75% of buy-and-hold's gross total return on both ETFs (premium confirmed,
consistent with F-006's ~9/13.1 share on stocks), but net of 2 bps/side × 2 trades/day the
overnight-only book returns ≈ 0%/yr or worse and its net Sharpe falls clearly below
buy-and-hold's. Break-even per-side cost lands near premium/(504) ≈ 1.5–2 bps.

**Alternative result** (what the world looks like if the hypothesis is true):
Overnight-only net Sharpe exceeds buy-and-hold net Sharpe on BOTH ETFs — requiring the ETF
overnight premium to exceed buy-and-hold total return plus ~10%/yr of costs. That world
would justify pre-registering a follow-up on cheaper execution or partial-notional overlays.

**Registered variants** (4 strategy books + 2 controls, all reported, gross and net):
overnight-only {SPY, QQQ} (long close t → open t+1, flat intraday; weights decided on
information through close t — no look-ahead), intraday-only {SPY, QQQ} (long open t →
close t), buy-and-hold {SPY, QQQ} (controls). No other assets, timing hybrids, or
partial-notional variants may be added after results are seen.

**Decisive statistic (pre-committed)**:
1. Premium confirmation (gross): overnight-only gross total return ≥ 60% of buy-and-hold
   gross on both ETFs → "premium real under our engine"; below on either → "premium weaker
   on ETFs than F-006's stock estimate", reported as measured.
2. Exploitability (net, frozen 2 bps/side): overnight-only net Sharpe > buy-and-hold net
   Sharpe on BOTH ETFs = EXPLOITABLE; anything else = NOT EXPLOITABLE at frozen costs.
   (Repo bar also applies: net Sharpe < 0.5 is dead as a book regardless.)
3. Descriptive only: measured break-even per-side bps; per-year overnight share table;
   intraday-only stats.

**Failure / kill condition** (pre-committed; includes the stop-iterating rule):
One run of the 6 registered books. The frozen cost model is THE cost model — no "but at
0.5 bps it works" relaxations, no timing hybrids, no partial-notional overlays from this
data. The stock cross-section tilt (F-006's original form) stays closed by arithmetic:
10 bps/side × 2 trades/day ≈ 50%/yr — untestable under the frozen model and not run here.
If NOT EXPLOITABLE → F-006 closes finally (new FAILURES.md entry); the harness keeps its
close-to-close convention and the open+close engine remains a research tool only.

**Trial-ledger row**: TRIAL_LEDGER.md — Robustness experiments table, added in the same
commit.

**Derived from prior holdout results?** YES — adaptive loop: F-006 (a prior experiment on
this panel) is the reason this exists and supplies the premium estimate. Flagged.

---
**Result** (filled after the run, never edited above this line):
