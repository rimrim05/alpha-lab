# PREREG EXP-B — Conditional volatility-management mechanism (explanation, not a switch)

*Frozen 2026-07-10 (Discovery Program). Unlocked by DATA_QUALITY_REPORT.md = PASS. Nothing above
the Result line may be edited after the first scoring run. This EXPLAINS where vol-management helps;
it does NOT optimize a trading switch and builds no portfolio. Conditions and expected signs are
frozen here BEFORE any evaluation (charter: do not discover the regime after seeing results).*

- **Experiment ID:** EXP-2026-07-10-conditional-vol-mechanism
- **Layer touched (one):** A — mechanism/phenomenon (which observable asset properties explain the
  cross-asset variation in vol-management benefit?)
- **Alpha type:** mechanism test — re-grades the **generality** of the promoted vol family. NOT a
  new market forecast; it cannot itself become a book.

**Hypothesis (one falsifiable sentence, mechanism):** Volatility management improves an asset's
geometric growth in proportion to four **pre-registered, fixed-sign** observable properties —
(1) positive risk premium, (2) volatility clustering, (3) negative return–volatility asymmetry
(leverage effect), (4) volatility-linked drawdown convexity — and does NOT help universally
(F-020); so the cross-asset variation in vol-management benefit is *explained* by these properties
with the signs below, at the cluster level.

**Why this is the sanctioned reopen of F-020:** F-020 rejected *uniform* cross-market vol-management
(3/7 clusters) but could not test *why* — it lacked the macro/vol state now provided by the PASSed
data layer. This asks the mechanism question, not "which ETF performed best."

**Data:** `panel_2005.parquet` ETF returns for the cross-asset set; `../data/state_aligned.parquet`
for VIX/VIX3M and rate/curve state (**STATE variables only** — no vol-carry return is claimed).

**Unit of analysis:** each cross-asset ETF (SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, USO, VNQ,
plus sector XLK/XLE/XLF/XLU/XLP/XLV/XLY/XLI), from each ETF's inception. **Inference is at the
CLUSTER level** (equities / intl-equity / rates / commodities / sectors-within-equity are correlated
— correlated ETFs count as ONE observation, not N). No per-asset parameter tuning.

**Response (measured, fixed rule):** `benefit_i` = geometric growth of the 21d-realized-vol-targeted
version of asset i (target vol + cap **frozen at the vol_managed_qqq spec** — identical for every
asset) minus buy-hold, net of a fixed turnover cost.

**Predictors (pre-registered, fixed, with EXPECTED SIGNS — no combination search):**
1. risk premium = full-sample mean excess return — **expect +**
2. vol clustering = AR(1) of 21d realized vol (or of squared daily returns) — **expect +**
3. return–vol asymmetry = leverage-effect coef corr(r_t, Δσ_{t+1}) — **expect benefit rises as this is more negative**
4. drawdown convexity = ratio of realized vol in worst-return-decile months to overall vol — **expect +**
5. (context, not scored for sign) funding sensitivity = β to ΔDFF/curve; curve/vol-state exposure — reported for interpretation only.

**Control:** universal vol-management applied to all assets (F-020's rejected uniform rule — the null
that properties don't matter). **Treatment:** regress `benefit` on the 4 fixed-sign properties;
test sign + joint significance at cluster level.

**Primary statistic:** cross-asset (cluster-level) regression of `benefit` on the 4 pre-registered
properties — do the coefficient **signs match the predictions** and is the model **jointly
significant** with n = number of clusters? **Secondary:** leave-one-cluster-out sign stability; a
walk-forward variant (properties from an expanding window predict next-period benefit) as the only
tradability-relevant check. Report R² but NEVER select predictors on it.

**Sample / holdout:** full history per asset. The primary is a descriptive cross-sectional
*explanation* (properties are stable asset characteristics); the walk-forward secondary is the
look-ahead-safe version. Freeze the property list + signs now (done, above).

**Expected effect:** ≥3 of 4 signs hold at cluster level with joint significance. Honest prior
P(supported) ≈ 0.55. **Alternative:** benefit is explained but by risk-premium/beta ALONE (properties
2-4 add nothing) ⇒ narrows the claim to "vol-management helps high-premium equity beta," not a
general mechanism.

**Failure / kill condition (decidable, stop-iterating):** properties do not explain cross-asset
benefit (joint insignificant at cluster level OR the majority of signs wrong) → **MECHANISM
UNSUPPORTED**; vol-management stays an empirical US-large-cap fact, not a mechanistically
generalizable rule. This CLOSES the conditional-vol reopen — do not test further property sets on
this ETF panel (the reopen is then new markets/instruments, not new features here).

**Cost model:** benefit computed net of a fixed per-rebalance turnover cost so the ranking is
implementable-relevant; no live trading (mechanism study).

**Leakage / survivorship:** VIX/rates STATE only, availability-lagged in the PASSed data layer;
the primary is descriptive (stable characteristics), the secondary is walk-forward. ETF-only, from
real inception (no synthetic pre-inception history).

**Parameter count:** 0 fit (vol-target frozen from the live spec; property list frozen).
**Complexity:** 3/5. **Information gain:** HIGH — adjudicates the trend-alpha-vs-levered-beta
generality question F-020 could not, and tells the lab whether the promoted family's edge is a
transportable mechanism or a single-market fact.

**Decision changed by success:** a validated property model tells us WHERE to look for the next
vol-management application (and whether the promoted family generalizes) — a research-direction
result, not a book. **Decision changed by failure:** stop trying to export vol-management; treat it
as US-large-cap-specific (consistent with F-020), and the promoted family's generality is capped.

**Trial-ledger entry:** TRIAL_LEDGER #24 (Discovery / mechanism) at first score.

---
**Result** (filled after the run, never edited above this line):
