# Stage 2 prereg — alpha-book attribution vs known / industry / vetted-residual risk

Written 2026-07-14, before any attribution code, before seeing any Stage-1 label-4
output. Reviewed (statistical / implementation / backtest-integrity) before freeze;
dispositions in Part C. Consumes the Stage-1 vetted panel (FLOOR_INDUSTRY_MEMO.md);
uses ONLY label-4 ("detectable-candidate-residual-risk") slots as residual controls.

Inherited Stage-1 caveats (binding on interpretation here): label-4 slots mean "not
explained by FF3+MOM + 11 GICS sectors", NOT "not industry risk" — surviving slots are
plausibly sub-sector structure; the label-4 gate is exclusion-biased by design, so the
residual control set is UNDER-COMPLETE (an omitted-control direction: L4 alphas may
still contain unvetted residual common risk) and systematically the most diffuse slots;
Stage 2 receives and reports the D/D′/L/recurrence scores alongside labels.

## Question
For each live hunt2026 book, does its return survive controls for (1) known factors,
(2) industry, (3) vetted residual statistical factors — and what is the honest
classification: known-factor premium / industry exposure / hidden residual-risk
exposure / promising-but-unproven residual alpha / insufficient evidence?

## Books (the 7 with live ledgers, frozen specs 2026-07-10, n_trials = 18 registered)
defensive_ensemble, dual_momentum_gem, dual_momentum_gold, momentum_concentrated,
trend_vol_qqq, vol_core_svxy, vol_managed_qqq.

## Return series (pre-stated honesty)
Net daily returns reconstructed by the hunt2026 harness (frozen specs on the full
panel; net of per-side bps costs; weights set at close t earn t+1 — no look-ahead in
accounting). WARNINGS carried on every output: (a) pre-2026-07-10 history is
SELECTION-TAINTED — these 7 specs were chosen from 18 registered trials on overlapping
data; alpha levels inherit that bias; deflated stats use n_trials = 18; (b) live OOS is
~2 trading days — statistically worthless, reported but unused; (c) the hunt2026 panel
is a recent yfinance pull → book universes are survivorship-tilted; (d) financing costs
of levered books are NOT modeled by the harness (gross exposure reported; flagged where
avg gross > 1.2); (e) attribution measures the factor COMPOSITION of the track record,
which is more selection-robust than its alpha LEVEL — but both are reported.

## Attribution design (frozen)
Span: the 14 Stage-1 primary windows (2021-11 → 2025-11, 63 return days each, 882 days).
All four levels computed PER WINDOW then aggregated, so level differences are never an
artifact of mixed estimation schemes. Full-span OLS for levels 1–3 reported as context.
Excess returns: book net daily minus RF (Ken French).
- L1 raw: per-window mean daily net excess return; annualized; Sharpe; deflated-Sharpe
  probability (n_trials = 18, full-span).
- L2 +known: per-window OLS on [Mkt−RF, SMB, HML, Mom]; alpha = intercept.
- L3 +industry: add the 11 equal-weighted panel sector return series (15 regressors,
  63 obs per window — dof-thin; that is WHY aggregation is across 14 windows).
- L4 +vetted residual: add that window's Stage-1 label-4 x_j series (0–5 per window;
  windows with zero label-4 slots contribute their L3 alpha to L4 unchanged, counted
  and reported).
Aggregation: mean window alpha; t-stat = mean/(sd/√14) across windows (windows are
non-overlapping; residual dependence through shared beta windows acknowledged, not
modeled). Exposures: per-window betas, reported as medians.
- Vol-ETP caveat (pre-committed): for each book, compute |ρ| of its L3 per-window
  residual series vs SVXY net returns; if |ρ| ≥ 0.5 the book's surviving return is
  classified "known-premium exposure (variance risk premium)" REGARDLESS of L4 t-stat —
  the equity factor set cannot span VRP and surviving alpha there is a known premium,
  not residual alpha.
- Stability: (i) calendar halves (first 7 vs last 7 windows); (ii) regime split —
  windows above/below median realized SPY vol. A classification of "promising" requires
  same-sign L4 alpha in both calendar halves.
- Costs/implementation: harness turnover, avg gross exposure, cost drag, max drawdown
  reported per book.

## Classification rules (numeric, frozen; applied in order, first match wins)
Let t_k = cross-window t-stat of level-k alpha; "significant" = t ≥ 2 AND same-sign in
≥ 60% of windows.
0. insufficient-evidence: < 10 valid windows, or the book's panel data starts after
   2021-11, or L1 mean excess return t < 1 (nothing to attribute).
1. vol-ETP override: |ρ(L3 resid, SVXY)| ≥ 0.5 → known-premium (VRP) exposure.
2. known-factor premium: L1 significant but L2 not.
3. industry / sector exposure: L2 significant but L3 not.
4. hidden residual-risk exposure: L3 significant but L4 not (only meaningful if ≥ 7
   windows had ≥ 1 label-4 control; else fall through to 5 with a flag).
5. promising-but-unproven residual alpha: L4 significant AND same-sign both calendar
   halves AND deflated-Sharpe probability ≥ 0.5. NEVER upgraded past "unproven" — 18
   trials, tainted history, 2 days of OOS.
6. insufficient-evidence (residual case): none of the above fire.
NO tuning after seeing results; the only post-run additions are mechanism notes.

## Controls (numeric)
- Benchmark positive control: run the full ladder on bench_qqq_buyhold (not a trial).
  Passes iff L2 kills it: |t_2| < 2 while L1 t ≥ 1 (a beta book must die at the known-
  factor level; if it survives L2, the regression plumbing is broken).
- Null book control: a zero-skill book (SPY buy-and-hold from the panel) must classify
  as known-factor premium or insufficient-evidence, never labels 4–5.

## Verdict rule (exhaustive)
FAIL: either control misclassifies. SUCCESS: controls pass AND ≥ 10 valid windows for
≥ 5 of 7 books. AMBIGUOUS: controls pass, coverage condition fails.

## Final deliverable (per the program spec)
One memo: per-book classification; factor-control table (FF status / industry status /
residual-factor status / leakage-detectability status from Stage 1); before/after
table (L1–L4, annualized alpha + t); supported vs not supported; single best next
action. No "proven alpha" language anywhere.

## Part C — review dispositions
(pending review)
