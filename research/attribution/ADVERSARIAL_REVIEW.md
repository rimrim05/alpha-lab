# Adversarial review — residual-alpha verdict + JSE verdict (Agent G, 2026-07-14)

Mandate: destroy the tentative conclusions before the final memo. Read-only except this
file. New numbers below were computed with the repo's own machinery
(`research/attribution/run_attribution.py` factor builder + NW-OLS, `harness.run` on the
frozen specs, `.venv/bin/python`; scratch scripts outside the repo). Diagnostic
regressions that add a regressor (GLD) are marked POST-HOC: the prereg's ambiguity rule
forbids them for the *decision*, and the decision (no candidate) does not change — they
attack only the *story wording* ("unexplained").

Conventions: MDA = minimum detectable alpha at NW-t = 2 = 2 × SE_ann(alpha).
Financing stress = the prereg's own line: alpha − max(gross−1,0) × (RF_ann + 0.50%).

---

## Part A/B — residual-alpha verdict

### Finding 1 — defensive_ensemble "+6.7%/yr, t=1.77 (best cell)" — KILLED as "unexplained"

**Target claim.** The program's best residual cell: defensive_ensemble blind-5y M2 alpha
+6.72%/yr, t=1.77 — the anchor of "some unexplained residual return".

**Attack.** Decompose it into (i) an asset exposure the factor menu omits (gold) and
(ii) financing the harness does not charge.

**Evidence (computed).**
- M2 + GLD excess return (POST-HOC diagnostic): alpha +6.72% → **+3.66%, t=1.09**;
  beta_GLD = +0.22 with t=+9.48; R² 0.686 → 0.754. GLD excess did **+16.44%/yr** over
  the blind-5y window — the book (sleeves B and C both hold GLD) rode it.
- Financing: gross 1.92, blind-5y RF 3.64%/yr → prereg stress charge = 0.92 × 4.14% =
  **3.81%/yr**. Applied to the GLD-controlled alpha: 3.66 − 3.81 = **−0.15%/yr**.
- The stress-adjusted t of the as-run cell is +2.91%/6.72% × 1.77 ≈ **t=0.77** (the
  ATTRIBUTION table reports the stressed *point estimate* next to the *unstressed* t;
  the honest pair is +2.91%, t≈0.77).
- Regime checks (M2, same machinery): excluding calendar 2022 → +4.99%, t=1.14
  (n=972); excluding 2025→ → +2.73%, t=0.65 (n=875). No single-regime exclusion leaves
  even t=1.2.
- Cross-check: the two audit corrections (F1 phantom row +, F2 PIT QQQRES −) net to
  t≈1.8 and do not rescue any of this.

**Outcome: KILLED.** Replacement claim: *"defensive_ensemble's blind-5y M2 alpha is
fully accounted for by unmodeled static gold exposure (+~3.1%/yr) plus uncharged
financing on 1.92x gross (+~3.8%/yr); the remainder is ≈ 0 (−0.2%/yr under the prereg
stress line). No unexplained residual."* (Note: β_GLD×(GLD−RF) and the gross−1
financing charge do not double-count — the first is the gold notional's excess-return
attribution, the second is the cash leg the harness gives away free.)

**Smallest falsification test.** Rerun the frozen attribution with (a) GLD excess in
the factor set and (b) financing charged in the harness at RF+50bp on (gross−1),
blind-5y window, same NW lag. The kill is wrong iff alpha ≥ +2%/yr with t ≥ 1.
One script, existing data, <5 min.

### Finding 2 — dual_momentum_gold "+13.0%/yr, t=1.32" — KILLED

**Target claim.** Second-largest 5y residual: +12.98%/yr, t=1.32.

**Attack.** Same gold hole in the model, plus single-regime dependence, plus documented
design hindsight.

**Evidence (computed + on the record).**
- M2 + GLD (POST-HOC): alpha +12.98% → **+2.03%, t=0.26**; beta_GLD = +0.79, t=+9.29;
  R² 0.373 → 0.628. The model without a gold factor calls a 0.79 gold beta "alpha"
  during a +16%/yr gold market.
- Regime: excluding 2025→ → alpha **−1.46%, t=−0.22**. The entire residual is the 2025
  gold rally (subperiod 2025→: +38.3%/yr, t=1.66, beta_TSMOM 4.1; blind half2 +33.6%
  vs half1 −6.8%). Rule 2 already failed; this is why.
- Selection: TRIAL_LEDGER flags the spec "gold-menu design hindsight", Hunt 2 was an
  adaptive loop, and the registered defensive-asset robustness experiment already ruled
  the GLD menu a **REGIME ARTIFACT** (GLD wins 13% of pre-2024 windows).
- TSMOM's own menu contains GLD, so M2 absorbs only sign-of-trend gold, not the level
  loading — hence the leak.

**Outcome: KILLED.** Replacement claim: *"dual_momentum_gold's residual is static gold
beta in a gold bull, on a menu chosen with hindsight; controlled for GLD it is
+2%/yr, t=0.3, and it is negative excluding 2025."*

**Smallest falsification test.** Same as Finding 1 (GLD in the factor set), this book:
kill is wrong iff M2+GLD blind alpha ≥ +4%/yr with t ≥ 1. Additionally forward: 12
months of paper NAV in which the book beats a static 0.8×GLD + 0.3×SPY replication net
of costs by ≥ 3pp.

### Finding 3 — trend_vol_qqq "+9.1%/yr, t=1.50" — WEAKENED to a one-regime trend-premium read

**Target claim.** +9.11%/yr, t=1.50, passes half-split and stress (+7.59%).

**Attack.** Single-regime (2022) dependence + the prereg's own naive-parent control.

**Evidence (computed + in file).**
- Excluding calendar 2022: alpha **+3.75%, t=0.57** (n=972). Subperiods: 2023–24
  +0.12% (t=0.02), 2025→ +1.46% (t=0.12). Everything is one bear.
- Not gold, not financing: beta_GLD −0.05 (t=−1.6); stress leaves +7.59%.
- The prereg's naive-parent control cuts the other way: bench_qqq_sma200_2x blind-5y M2
  alpha +12.42%, t=1.55 — the *naive* parent's residual is LARGER than the book's, and
  the walk-forward memo already showed the combo's median excess is below its parents
  (F-014). Per the prereg's own logic ("if a vol/trend book's alpha ≈ its naive
  parent's, the alpha is the trend premium, not engineering"), this cell is trend
  premium that M2's 6-ETF TSMOM proxy under-spans, not book engineering.
- Instability the other way: excluding 2025→ gives t=2.04 — the estimate swings ±0.5t
  on window choice; that is evidence of regime concentration, not of alpha.

**Outcome: WEAKENED.** Replacement claim: *"trend_vol_qqq's residual is a single 2022
bear-regime payoff shared with (and exceeded by) its naive trend parent — consistent
with imperfectly-spanned trend premium; no independent evidence of engineering alpha
(ex-2022: +3.8%/yr, t=0.6)."*

**Smallest falsification test.** Next SPY drawdown ≥ 15% peak-to-trough: book must beat
bench_qqq_sma200_2x by ≥ 3pp net over the drawdown window (mechanism claim), OR 3 years
of forward paper NAV with M2 alpha ≥ 4%/yr — whichever comes first.

### Finding 4 — dual_momentum_gem "+15.8%/yr, t=1.12 (1y)" — KILLED as evidence (uninformative cell)

**Target claim.** Largest point estimate among the four best cells.

**Attack.** Power arithmetic + sign instability.

**Evidence (computed).** SE_ann = 14.05% → **MDA at t=2 is 28.1%/yr**: this cell cannot
distinguish zero from +28%/yr. P(t≥2 | true alpha = 10%/yr) ≈ 10%. Half-split is
−9.4% / +39.7% (rule 2 fail); the verdict memo itself attributes the year to one April
switch month; n=219; GLD control moves nothing (−0.8pp).

**Outcome: KILLED as evidence.** Replacement claim: *"gem's 1y cell is statistically
empty — a +15.8% point estimate with a 14% standard error and a sign flip across
halves; it neither supports nor damages a residual-alpha claim."*

**Smallest falsification test.** None available in-sample — the cell is information-
free. Forward only: 24 months of paper NAV; M2 alpha t ≥ 2 on the accumulated window
(SE shrinks to ~9.5% at n≈470; still only detects >19%/yr — state this in the memo).

### Finding 5 — "No book clears t ≥ 2" carries almost no weight against moderate alpha — SURVIVES only with the MDA table attached

**Target claim (direction B).** The implicit negative reading of "no book clears
blind-window M2 NW-t ≥ 2".

**Attack.** Compute what the test could have seen.

**Evidence (computed, as-run NW SEs).**

| cell | SE_ann | MDA (t=2) | P(t≥2 \| true α=5%/yr) |
|---|---|---|---|
| defensive_ensemble 5y | 3.79% | **7.6%/yr** | ≈ 0.25 |
| trend_vol_qqq 5y | 6.07% | **12.2%/yr** | ≈ 0.12 |
| dual_momentum_gold 5y | 9.83% | **19.7%/yr** | ≈ 0.07 |
| dual_momentum_gem 1y | 14.05% | **28.1%/yr** | ≈ 0.05 |

Even the best-powered cell detects a true 5%/yr alpha only one time in four. A 10%/yr
alpha would be missed in the gem cell 90% of the time.

**Outcome: SURVIVES, WEAKENED in scope.** The program may say "not detected"; it may
NOT say or imply "absent". Any memo sentence of the form "no residual alpha exists"
must be replaced by *"no residual alpha was detectable, and the design could not have
detected less than ~7.6%/yr in its best-powered cell"*. (Direction A and B meet here:
Findings 1–4 explain the point estimates; Finding 5 caps what the t-stats ever proved.)

**Smallest falsification test.** Not falsifiable retrospectively; the binding forward
test is the live paper book: at ~2x the observations (n≈2500, 5y book) the defensive
cell's MDA drops to ~5.3%/yr — pre-register that number now.

### Finding 6 — "Is alpha-vs-M2 the right null for a factor-timing strategy?" — SURVIVES, with a mandatory disclosure

**Target claim (direction B).** M2 (adding TSMOM + QQQRES) is the deciding model; the
worry is that it absorbs the books' own claimed skill by construction.

**Attack + evidence.**
- The direct check the task asked for: **timing skill would show as positive alpha in a
  static-factor regression — and it did.** Under M1 (FF5+MOM only, no TSMOM/QQQRES),
  defensive_ensemble's blind alpha is +9.52%/yr with **t=2.01** — it clears the static-
  premia bar. It fails only when TSMOM (a strategy return, the book's own mechanism
  class) enters (t=1.77) and rule 1 demands both.
- However: (a) TSMOM is a published, investable premium (Moskowitz-Ooi-Pedersen 2012)
  and was pre-registered as a *known* factor — charging a trend book for generic trend
  exposure is precisely what attribution is for; (b) the TSMOM proxy is PIT and nearly
  costless to trade (6 ETFs, 2 bps); (c) the residual left AFTER M2 is the book's
  timing-beyond-generic-trend, and per Finding 1 that residual is gold + financing;
  (d) the QQQRES look-ahead (audit F2) biases alpha UP, not down — PIT construction
  lowers the best cells to t=1.73/1.36. So M2 is not stealing genuine skill; if
  anything it is slightly generous.
- Residual scale sanity: defensive_ensemble M2 residual vol is 8.2%/yr on a 1.92x-gross
  book — the model leaves plenty of room for alpha to show; it just isn't there after
  Findings 1–2.

**Outcome: SURVIVES.** Mandatory disclosure for the memo: *"the verdict is conditional
on classifying TSMOM harvest as factor exposure rather than skill; under known static
premia alone (M1) defensive_ensemble clears t=2."* Omitting that sentence would be the
one way this finding becomes a kill.

**Smallest falsification test.** If anyone claims M2 over-absorbs: re-estimate M2 with
TSMOM beta FIXED at its pre-blind (≤2021-07) value instead of in-window; skill absorbed
by in-window beta fitting would reappear as alpha. Overturn iff defensive_ensemble M2
alpha t ≥ 2 under fixed betas. One regression.

### Finding 7 — Selection over ≥18 adaptive trials makes t=1.77 unremarkable — SURVIVES (strengthens the null reading)

**Target claim.** The four "best cells" as noteworthy residuals.

**Attack + evidence.** They are the max over 7 books (≈3 independent clusters per the
prereg's own INDEPENDENCE_MATRIX) from a process TRIAL_LEDGER scores at ">18 effective
trials" with Hunt 2 explicitly adaptive (5y books designed after seeing Hunt-1 2022
stress — the same 2022 window that drives Finding 3, and the gold menu of Finding 2).
Under the null, P(max t of 3 independent cells ≥ 1.77) ≈ **0.11** (≈ 0.24 with 7).
A best-of-family t=1.77 is the expected outcome of no alpha plus selection.

**Outcome: SURVIVES** as an argument; it removes any residual enthusiasm the phrase
"some unexplained residual return" might smuggle into the memo.

### Finding 8 — Data artifacts (phantom row, survivorship) — cannot rescue OR sink the verdict; scorecard contamination stands

The audit's quantifications are confirmed as directionally offsetting at this
experiment's level (F1 understates: t 1.77→1.83 fixed; F2 overstates: t 1.77→1.73
PIT); both fixes together ≈ t 1.8, same verdict. The real exposure is upstream: the
frozen results5y/holdout headline scores embed ~6 weeks of corrupted post-2026-05-25
returns — the hunt "+18%" numbers in memos/hunt2026-verdict.md carry that asterisk
until holdout.parquet is fixed and re-frozen. Survivorship (F3) only makes the one
negative-alpha stock book more negative. No change to either verdict; the memo should
cite the audit rather than re-litigate.

---

## Part C — JSE verdict

### Finding 9 — "No practical JSE value in this system" — WEAKENED (two words too strong, one cell untested)

**Target claim.** Verdict lean: "no practical JSE value in this system".

**Attack.**
1. *"No value" vs the record:* the long-only vol reduction is statistically real at
   every window (−2.6→−0.5 bps/yr, all p<0.0001, monotone in p/n, mechanism-confirmed).
   "No practical value" is defensible only if "practical" is pinned to the
   pre-committed materiality bars — every one of which (−0.2 bps gate, ±0.3 bps
   calibration, 0.5 net-Sharpe revival, turnover rule, F-021 deployment lock) was
   missed by an order of magnitude. Say that, not "no value".
2. *"In this system" vs coverage:* JSE_BOUNDARY_MAP §5 concedes a benchmark-relative /
   tracking-error min-var book was **never run** ("Untested — no claim"), and the gap
   table shows tracking error and residual vol MISSING at every k. A partially
   sign-constrained book sits between the long-only (tiny help) and unconstrained
   (real harm) endpoints — the prior is unfavorable but it is a prior, not a result.
3. *Overstated support line:* the "direction right in every eval mode" talking point
   (hunt2026-walkforward item 6, echoed in JSE_SYNTHESIS §6(i)-against) is wrong on its
   own numbers — the 44-window median excess favors RAW by 0.1pp (+3.4 vs +3.5;
   synthesis C2). Both sides of the JSE argument should stop citing the hunt pair;
   ±10–15 bps with no t-stat is noise-grade in every direction.

**Outcome: WEAKENED-to:** *"No deployment-material JSE value on any book tested:
the only real effect is a long-only min-var vol reduction ≤ 2.6 bps/yr — statistically
robust, an order of magnitude below every pre-committed materiality bar; JSE is
significantly harmful wherever shorts are allowed (+14 to +49 bps) and in every direct
hedging/regime/calibration extension (F-026→F-031); ψ̂₁ ≈ 1 on all accessible S&P
panels means there is nothing for the correction to fix at this scale. One book class —
benchmark-relative/tracking-error — was never run and carries no claim."*

**Smallest falsification test (the cheap overturn the task asked for).** One run on the
existing 138-month cached panel: benchmark-relative min-var (active weights vs SPY,
same 5%-cap harness, k ∈ {1,3,5}), jse vs pca matched pair, decisive cell large-cap
n=63 k=5. Overturn the verdict iff median paired Δ(tracking error or realized vol) ≤
−0.5% relative with p < 0.05 AND the implied annual benefit ≥ 10 bps (a materiality
bar consistent with the program's existing ones). Anything smaller confirms the verdict
and closes BOUNDARY_MAP §5. Cost: one script on cached data.

### Finding 10 — The JSE program's remaining live claim is correctly scoped — SURVIVES

The defensible scientific residue ("JSE improves long-only min-var realized vol —
statistically real, economically immaterial — and nothing else in this system",
JSE_SYNTHESIS §6(iii)) survives attack: it is backed by monotone dose-response across
six window lengths, an audit that reconciled the one prose contradiction (C1) to
byte-identical pipelines, and two independent mechanism closures (subspace-invariance +
robust-rotation both showing the rotation term has no min-var value). I could not
construct a data-supported attack on it. The only rider: the −2.6 bps ceiling was
measured at n=42 on ONE panel/p-range (§5 honesty note), so "ceiling" means "ceiling
observed on S&P-scale panels", not a theorem.

---

## Verdict wording I would accept

**Q1 — residual alpha.** The prereg mapping fires mechanically and may not be
relabeled post-hoc: *"factor-premium harvesting with some unexplained residual
return"* is the correct pre-committed label. But the memo must carry it with these
riders, without which I dissent:

> Factor-premium harvesting; no residual-alpha candidate (0 of 7 books pass rule 1).
> The prereg label "some unexplained residual return" refers to four cells with
> alpha > 2%/yr at 1 ≤ t < 2; on post-hoc decomposition each is accounted for:
> defensive_ensemble = unmodeled gold beta + uncharged financing (residual −0.2%/yr);
> dual_momentum_gold = gold beta on a hindsight menu (+2%/yr, t=0.3 after GLD;
> negative ex-2025); trend_vol_qqq = one 2022 bear regime shared with and exceeded by
> its naive parent (ex-2022 t=0.6); dual_momentum_gem = an information-free 1y cell
> (MDA 28%/yr). Conditional on classifying TSMOM harvest as factor exposure (M1-only,
> defensive_ensemble clears t=2). Power caveat: the design could not detect true alpha
> below ~7.6%/yr in its best cell, so this is "largely explained and not detected",
> not "proven absent". Best-of-family t=1.77 has familywise p ≈ 0.11 under the null
> given ≥18 adaptive trials.

**Q2 — JSE.** Replace "no practical JSE value in this system" with:

> No deployment-material JSE value on any book tested. The long-only vol reduction is
> statistically real (all p < 0.0001) but ≤ 2.6 bps/yr — an order of magnitude below
> every pre-committed materiality bar; JSE is significantly harmful with shorts and in
> every hedging/regime/calibration extension; ψ̂₁ ≈ 1 on all accessible S&P panels.
> Untested: the benchmark-relative/tracking-error book (BOUNDARY_MAP §5) — one cheap
> pre-registered run on the cached 138-month panel closes it and is the only in-system
> test that could overturn this verdict. Retire the "direction right in every eval
> mode" hunt-pair talking point (the 44-window median favors raw by 0.1pp).
