# FRED revision-exposure verification (API key, 2026-07-11)

The discovery data layer (`DATA_QUALITY_REPORT.md`, VERDICT PASS) was built **keyless**
(fredgraph.csv, latest-revised) and *asserted* that its series are unrevised and that macro
series were rightly excluded. With the FRED API key (ALFRED vintages;
`~/.config/rimrimos/fred.env`, chmod 600, not in repo) this is now **measured**, not asserted
— `fred_revision_verification.py` compares first-print (value as known ~days after the obs
date) vs latest.

| series | role | first-print | latest | verdict |
|---|---|---|---|---|
| DGS10 | layer | 0.66 | 0.66 | unrevised ✓ |
| VIXCLS | layer | 28.23 | 28.23 | unrevised ✓ |
| VXVCLS | layer | 30.92 | 30.92 | unrevised ✓ |
| DFF | layer | 0.05 | 0.05 | unrevised ✓ |
| T10Y2Y | layer | 0.52 | 0.52 | unrevised ✓ |
| CPIAUCSL | excluded | 257.214 | 257.042 | REVISED (exclusion justified) |
| GDP | excluded | 19408.759 | 19958.291 | REVISED +2.8% (exclusion justified) |

**Result: PASS.** Every series the layer uses is empirically unrevised → keyless
latest-revised data **equals** point-in-time for these series, so there is no revision
look-ahead. The excluded macro series are confirmed revised → using their latest-revised
values *would* have been look-ahead; the sibling layer was right to drop them. This upgrades
the layer's revision-exposure claim from asserted to measured; the PASS verdict stands and is
now harder.

**Forward value of the key:** if any future preregistration wants to *use* a revised macro
series (e.g. CPI/GDP surprise for a bond-carry regime filter), the API key enables true
point-in-time vintage retrieval (`realtime_start` = as-of date) that keyless CSV cannot — the
value as it was actually known on each date. Until then, the key is only used for this
read-only verification; no strategy is built, nothing is promoted.
