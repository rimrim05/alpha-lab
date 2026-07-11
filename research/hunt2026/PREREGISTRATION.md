# Pre-registration template — fill this in BEFORE running anything

Every experiment gets a copy of the block below, committed before the first scoring run.
No block, no run. Rationale: the trial ledger can only deflate what it can count
(TRIAL_LEDGER.md, "Rules going forward"), and a hypothesis stated after seeing the result
is a description, not a prediction.

Rules:
1. Commit the filled block (and the TRIAL_LEDGER.md row) before touching holdout or
   walk-forward data. Train-data exploration is allowed first; say so in the hypothesis.
2. One layer per experiment (A-D per RESEARCH_OBJECTS.md) against a registered baseline.
3. If the design was influenced by any prior out-of-sample result, flag it — that makes
   the hunt an adaptive loop and it must say so in its hunt-level ledger row.
4. The kill condition must be decidable from numbers the harness already emits.
5. Results get appended to the same block after the run: pass → CONFIDENCE_LADDER.md
   placement; fail → FAILURES.md entry. Either way the block is never edited above the
   Result line.

---

## Template

```markdown
### EXP-YYYY-MM-DD-<slug>

**Hypothesis** (one falsifiable sentence, mechanism included):

**Layer touched** (exactly one — A economic / B estimator / C portfolio / D execution,
per RESEARCH_OBJECTS.md) + registered baseline it is compared against:

**Alpha type tag**: market | estimator | portfolio | execution

**Expected result** (numeric, on which evaluator — blind holdout / walk-forward /
matched-pair delta):

**Alternative result** (what the world looks like if the hypothesis is false — what
number would the null produce?):

**Failure / kill condition** (pre-committed; decidable from harness output; includes
the "stop iterating" rule, not just the "this run failed" rule):

**Trial-ledger row**: TRIAL_LEDGER.md #__ (added in the same commit)

**Derived from prior holdout results?** yes/no — if yes, which, and note the adaptive
loop in the hunt-level table.

---
**Result** (filled after the run, never edited): pass/fail vs kill condition, one line,
link to FAILURES.md entry or CONFIDENCE_LADDER.md placement.
```

## Currently pre-registered (from RESEARCH_OBJECTS.md, open layer experiments)

| exp | layer | tag | one-liner |
|---|---|---|---|
| JSE k=3-5 unconstrained min-var, walk-forward | B | estimator | the Goldberg program's real test; k=1 capped answered direction only (F-010) |
| open+close execution in harness | D | execution | reopens the overnight premium by design (F-006) |
| turnover-penalty (no-trade band) sweep, vol-managed family | C | portfolio | one knob, pre-registered range |
| EWMA vs realized-window vol inside vol_managed_qqq | B | estimator | matched pair, one layer |

Each still needs its own filled template block before running.
