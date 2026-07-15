# Phase 7 prereg — FF+industry known-model arm (Stage 1 of the attribution program)

Written 2026-07-14 before code. Rev 2 after review round 1 (statistical: BLOCK;
implementation, factor-model: approve-with-changes) — all blocking findings resolved
below; dispositions in Part C. Statistical re-review of rev 2 required before freeze.

## Question
Which FF3+MOM residual statistical factors are explained by industry/sector structure,
which remain detectable after removing it, and of those, which carry low association
with the known model — yielding a vetted residual-factor panel for Stage 2 with labels
(applied in numeric order, FIRST MATCH WINS):
1 noise-like · 2 explained-by-industry-or-known (arm-A slots only) ·
3 high-known-association · 4 detectable-candidate-residual-risk · 5 mixed-uncertain.
Label names are association language, not provenance claims (Phase 6 log: provenance
is not establishable without oracle truth). Label 3 corresponds to the program's
"likely leaked known risk" bucket; "consistent with the Phase-4/6 leakage mechanism"
is interpretive text only. Stage 2 receives the D/D′/L/recurrence SCORES alongside
labels — the label cliff must not destroy information.

## Data
Prices, PIT membership, FF3+MOM: as Phase 6. Industry: 11 GICS sectors from
`data/raw/sp_composite_named.parquet` (100% coverage of checked PIT∩panel universes).
LIMITATIONS (pre-stated):
- Non-PIT snapshot; specifically the 2023-03 GICS restructure (~14 S&P names incl.
  V, MA, PYPL, TGT, ADP moved sectors) is backfilled into the ~6 primary windows before
  2023-03. Accepted for a descriptive diagnostic; affected windows flagged in CSV.
- 11 sectors is coarse vs practitioner models (~60 industries). **Label 4 means "not
  explained by FF3+MOM + 11 GICS sectors" — explicitly NOT "not industry risk"; sub-
  sector structure (semis vs software, biotech vs pharma) survives by construction and
  is a plausible identity of surviving slots.** Propagated to the Stage-2 prereg.
- Unit-exposure dummies misfit conglomerates and (non-PIT) misclassified names —
  a further source of leftover sector comovement in arm-B residuals.

## Design (frozen)
Windows, screens, vol-standardization, trailing betas: identical to Phase 6 main
runner (NOT the diag script's merged-mask variant); the arm-A rerun asserts per-window
univ_hash equality against floor_realdata.csv and aborts on mismatch. Primary = 14
coverage-≥90% windows.
- Arm B (FF+IND): project off col([B̂_FF (p×4) | S (p×11)]) via QR/SVD only (never
  normal equations); the 11 dummies sum to 1⃗ and the market-beta column is ≈ constant,
  so assert numerical rank 15 and log cond([B̂_FF|S]) per window.
- Arm A (FF-only): Phase 6 pipeline rerun with the empirical screen below replacing C4.
  Phase 6 outputs are not reinterpreted.
- Sector return series (frozen; both arms' D_j regressors): equal-weighted averages of
  the vol-standardized RAW excess returns (PRE-residualization) of the screened
  analysis-universe names per sector. Computing them post-residualization would give
  identically-zero series (residuals are cross-sectionally orthogonal to col(S));
  EW matches the unweighted projection; cap-weighted variant skipped (no cap data
  in-panel). Per-window sector member counts in CSV; sectors with < 15 screened
  members flagged (their EW series are idio-noise-dominated).
- Detectability screen (both arms): per PC rank r, detectable iff SNR̂ > pooled
  shuffled q99 for rank r — 50 per-asset-independent time permutations per primary
  window of that arm's residual panel (700 panels/arm; seed = base_seed·1000 +
  window_index, base seeds stamped, per arm; raised from 20 per re-review to thicken
  the q99 tail). Pooled-null caveats (pre-stated): size is marginal over the 14-window
  mixture (per-window size varies with tail heaviness; p varies 458–496 shifting scale
  ~3–4%). Per-window shuffled maxima reported in CSV. C4 kept as a descriptive
  column. RANK-1 (pre-stated from Phase 6): the rank-1 shuffled null is dominated by
  single-day heavy-tail artifacts (q99 ≈ 9.8), so most arm-A PC1 slots will fail the
  screen — that is screen insensitivity at rank 1, NOT evidence against Phase 6's
  leakage finding; slots failing the screen with D_j ≥ its null q99 get a
  "screen-fail-high-known-assoc" annotation in the CSV.
- Floor: raw ℓ/θ_j; +n/(2p) iff realized p/n ≥ 7 (else raw + flag).
- Association scores per slot: D_j = centered R² of x_j on the arm's known return
  series (arm A: 4 FF; arm B: 4 FF + 11 sector series; lstsq/pinv, R² clipped to [0,1]
  with logged warning, Gram condition number logged, F-dof parameterized by regressor
  count and reported as descriptive only). Secondary D′_j vs B̂-implied factor returns.
  Localization L_j = max_t x²_jt / Σ_t x²_jt.
- **Null distributions and quantile scope (frozen).** For each score (D, D′, sector-R²,
  a_match), the null = circular shifts of x_j (62 per slot, regressors fixed so their
  mutual correlation structure is preserved), POOLED ACROSS THE 14 PRIMARY WINDOWS PER
  PC RANK AND ARM → 868 draws per rank; label gates use these pooled per-rank
  quantiles. Exchangeability across windows is assumed and stated as a caveat (regime
  mixing: heavy-tailed windows dominate the tail). Within-window shift draws are
  DEPENDENT (shifts of one series), so the pooled q99's effective resolution is bounded
  by the 14 window blocks; the per-slot exact-permutation column is the
  dependence-robust check. Shift nulls also destroy shared calendar structure (common
  heavy-tail days) between x_j and the fixed regressors — conservative for label 2
  (biases against "no counterpart") but INFLATIONARY for label 3 on heavy-tail windows;
  Stage 2 must not over-read label-3 prevalence. The label-4 clean-yield formula
  assumes D/D′ null independence (stated approximation). Per-slot exact permutation p
  ("D_j exceeds all 62 own-window shifts", p ≤ 1/63) reported as a descriptive column.
  The dof note stands: arm-B raw R² baseline ≈ 15/62 ≈ 0.24 — levels are meaningless,
  only null-relative position is interpreted.
- Cross-arm matching (revised per reviews; Phase-5 lesson — provenance MIXES, matching
  must be subspace-aware): a_match(j) = centered R² of x_j^A on the return series of
  arm B's top k′+2 = 7 PCs (matching only; screening/labels stay on top 5). "No arm-B
  counterpart" iff a_match(j) < its pooled per-rank null q95. Max pairwise |corr| kept
  as a descriptive column. "Disappears under industry" = no counterpart AND
  R²_sector(x_j^A) ≥ its pooled per-rank null q99.

## Labels (numeric, frozen; first match wins)
1. noise-like: fails the detectability screen.
2. explained-by-industry-or-known (arm-A only): detectable in A AND disappears under
   industry (rule above). (Named "-or-known" because raw EW sector returns embed the
   market; precedence over 3/4 is intentional.)
3. high-known-association: detectable; D_j ≥ pooled per-rank null q99.
4. detectable-candidate-residual-risk: detectable; D_j < null q75 AND D′_j < its null
   q99 AND L_j ≤ 0.50.
5. mixed-uncertain: everything else.
Label-4 gate honesty (pre-stated): the conjunction is EXCLUSION-BIASED by design — the
D<q75 arm alone rejects ~25% of genuinely clean slots; expected yield on clean slots
≈ 0.75·0.99·P(L≤0.5) — the accepted trade is FP contamination of Stage-2 controls
being worse than FN starvation, and the surviving set is systematically the most
diffuse slots (selection effect Stage 2 must treat as an UNDER-COMPLETE control set;
omitted-control implication named in the Stage-2 memo). The L cut: 0.50 splits the
Phase-6 real-passer median (0.275) from the shuffled artifact class (0.8–0.9); it was
chosen from Phase 6 diagnostics computed on THESE SAME WINDOWS — frozen before Phase 7
code, mild circularity accepted and flagged. MANDATORY sensitivity table: label-4
counts at L ∈ {0.25, 0.30, 0.40, 0.50}, plus shuffled-null L quantiles (descriptive).
Recurrence (descriptive, for Stage 2): each label-4 slot's max |corr| with the
adjacent primary window's label-4 slots (≥ 0.5 = "recurrent").

## Primary metrics
(1) Arm-A slot flow under industry (disappear / persist / relabel), with the rank-1
screen-insensitivity caveat; (2) arm-B label counts (qualitative under beta-window
dependence); (3) floor and D_j distributions of label-4 slots; (4) label-4 slots per
window available to Stage 2 (+ recurrence).

## Controls (numeric, frozen)
- Positive (plumbing, arm B): unresidualized PC1 on the most recent primary window —
  detected by the screen AND centered R² of x₁ vs Mkt−RF ≥ 0.7.
- Industry control (evaluation order fixed per re-review): among DETECTABLE non-PC1
  slots, med_A = median R²_sector(arm A), med_B = median R²_sector(arm B).
  (i) VALIDITY FIRST: if the arm-A detectable non-PC1 set is empty, OR med_A < the q75
  of the sector-R² null draws POOLED ACROSS RANKS 2–5 (arm A) — the frozen reference
  for this one comparison — the control is "not testable" and the verdict falls back
  to the remaining controls. (ii) Only if testable: empty arm-B detectable set ⇒ PASS;
  else PASS iff (med_A − med_B)/med_A ≥ 0.5.
- Screen calibration-consistency (plumbing only — certifies "size within ~3× nominal,
  internally consistent", NOT real-data calibration): 5 fresh base seeds; pooled
  exceedance of the frozen per-rank q99 ≤ 3%; MANDATORY per-rank exceedance table
  (5 numbers), rank 1 read against its artifact class.

## Verdict rule (exhaustive)
FAIL: any evaluable control fails. SUCCESS: all evaluable controls pass AND ≥ 95% of
detectable primary-slot floors finite and in [0,1]. AMBIGUOUS: controls pass,
floor-validity fails. Label counts (including zero label-4) are outputs, not failures.

## Decision that follows
SUCCESS → vetted panel feeds Stage 2 (FLOOR_ATTRIB_MEMO.md; zero label-4 ⇒ Stage-2 L4
runs with empty residual control set and says so). FAIL → mechanism diagnosis, no
tuning. AMBIGUOUS → adversarial review before use.

## Reproducibility
stamp_run: base seeds (screen + 5 held-out), input SHA-256s incl. sector file (as-of
date asserted 2026-07, no embedded date field), all thresholds, memo pointer. CSV: per
slot — universe hash, coverage, p, arm, rank, SNR̂, C4 flag, screen q99, per-window
shuffled max, floor raw/reported/corrected-flag, D, D′, L, sector-R², exact-permutation
p, a_match, max|corr|, label, screen-fail-high-known-assoc annotation, recurrence,
sector member counts, cond numbers, GICS-restructure flag.

## Part C — review dispositions (round 1)
Accepted and incorporated: all three statistical blocking findings (null resolution →
pooled per-rank 868-draw quantiles with stated scope + exact-permutation descriptive;
industry-control well-posedness → empty-set PASS, explicit formula, validity
precondition; label precedence → first match wins). Statistical should-fixes: label-4
FNR pre-stated + L cut moved 0.30 → 0.50 + sensitivity table + scores passed to
Stage 2; L-circularity acknowledged; matching → multivariate R² vs null (max|corr|
descriptive); calibration control reframed + per-rank table; label 3 renamed to
association language. Implementation should-fixes: GICS 2023-03 named + windows
flagged; sector-series construction frozen pre-residualization; lstsq/pinv + clipping
+ cond logging + dof parameterization; stamp list fixed (no "negative shuffles" —
Phase 7 has no negative control; sector date asserted + SHA; seed scheme stated);
arm-A window-construction assert. Factor-model should-fixes: sub-sector honesty into
label-4 definition + Stage-2 propagation; recurrence metric added; exclusion-bias
sentence added; dummy-misfit clause added.
Rejected/deferred (documented): hand-coded pre-2023 sector robustness rerun (deferred —
affected set small, flagged instead); cap-weighted sector D column (no cap data
in-panel); industry-group granularity column (no sub-sector codes in the file).

## Part D — post-run addendum (2026-07-14, after FAIL; diagnosis only, no tuning)
Verdict FAIL (industry control 43% vs ≥50% bar). Mechanism (FLOOR_INDUSTRY.md story):
the bar assumed removable sector-mean content dominates residual-PC sector association;
diagnosis shows ~half is diffuse cross-sector theme structure outside the 11-dummy span
(market embedding refuted; sector means zero by construction; loading concentration
median 24%). Bar mis-set against the memo's own coarseness limitation — rule-drafting
error owned. No rerun/re-verdict. Research Lead decision: Stage 2 proceeds with the
panel, "industry-controlled" = "sector-MEAN-controlled" binding language, FAIL context
carried; decision exposed to adversarial review.

## Part C.2 — re-review (round 2, statistical): approve-with-changes, all applied
(1) industry-control evaluation order + empty-arm-A "not testable" case; (2) validity
reference frozen as ranks-2–5-pooled sector-R² null q75; (3) screen permutations
raised 20 → 50 per window; (4) within-window shift-dependence and shared-calendar
caveats added. FROZEN as of these edits, 2026-07-14.
