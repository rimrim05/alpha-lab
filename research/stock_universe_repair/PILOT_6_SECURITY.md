# Six-security manual pilot — Capital IQ Pro & Finaeon (2026-07-11)

*Run manually by Kristen (browser automation can't drive these SPAs — access confirmed, extraction not).
Both tabs left open. The project/panel stays UNCHANGED until this pilot produces actual entitlement
evidence. This is the survivorship-continuity acid test: the six names are chosen as identity traps.*

## The six securities (each is a trap)
| security | the trap — a platform FAILS if it… |
|---|---|
| **GM / MTLQQ** | joins pre-2009 GM (→ Motors Liquidation Co, MTLQQ) to the post-2010 "new GM" security |
| **WAMUQ** | can't reach Washington Mutual's final 2008 trade / doesn't show the bankruptcy |
| **CELG** | appends BMY prices to Celgene (acquired by Bristol-Myers Squibb 2019-11, + CVR) |
| **KD** | treats Kyndryl (spun from IBM 2021-11) as continuous IBM history |
| **XLNX** | appends AMD prices to Xilinx (acquired by AMD 2022-02, exchange ratio) |
| **HTZ** | joins pre-bankruptcy Hertz (2020 Ch.11) to the relisted 2021 Hertz security |

## Fields to record (per security, per platform)
| field | what to capture |
|---|---|
| search term that worked | ticker / old ticker / company name / CUSIP / other ID |
| entity/security found | exact company + security name |
| earliest price date | first daily observation |
| final price date | last actual trading date |
| identity continuity | old vs successor kept **separate**? (Y/N) |
| corporate action | bankruptcy / acquisition / spinoff / relisting / exchange ratio / CVR |
| adjusted series | available or not |
| unadjusted series | available or not |
| permanent ID | CIQ ID / CUSIP / ISIN / SEDOL / GFD ID |
| export | CSV / Excel / download / copy-only / none |
| export limit | rows / securities / date range / visible restriction |
| evidence | screenshot or exported sample |

## Hard pass/fail
**Immediate FAIL** if a platform: joins old GM to post-2010 GM · joins pre-bankruptcy Hertz to relisted
Hertz · appends BMY to CELG · appends AMD to XLNX · treats KD as continuous IBM · cannot reach the actual
last trading date · shows charts but offers no structured export.
**PASS** only if: zero material identity-continuity errors · ≥5/6 have complete terminal histories ·
corporate-action treatment documented · data exportable in a reproducible format.

## Capital IQ Pro sequence (per name)
Search order: (1) old ticker → (2) full historical company name → (3) CUSIP → (4) Company Screener
inactive-company filter → (5) a result marked inactive/acquired/bankrupt. Inside the company: open
historical pricing; check the security/trading-item selector; verify the last date before acquisition/
delisting; find corporate actions / transaction history; test Download / Export to Excel.
**For CELG and XLNX, verify the historical security ENDS rather than continuing under BMY / AMD.**

### CIQ estimates — PIT test (one event, separate)
Do NOT accept a normal "historical estimates" chart as PIT. Look specifically for: **As Of Date ·
Snapshot Date · Estimate Date · Revision Date · Point-in-Time · Estimates Snapshot.** Only a
revision-timestamped as-was consensus (reconstructable immediately before a historical release) passes.

## Finaeon sequence (per name)
After **Log in Anonymously**: (1) search the historical **company name**, not only the ticker →
(2) choose **U.S. Stocks** or **U.S. Delisted Equities** if a database selector appears → (3) open the
price series → (4) record first + last dates → (5) inspect notes/metadata for merger / bankruptcy /
ticker change / relisting → (6) test export/download.
**Decisive case: WAMUQ or GM/MTLQQ.** If those aren't findable under the institutional module, Berkeley
likely does NOT license the delisted-equities product.

## Result template (send back — compact is fine)
```
Platform: Capital IQ Pro
GM/MTLQQ — PASS/FAIL
  resolved using: | first date: | last date: | old/new GM separate: |
  corporate action: | adjusted/unadjusted: | permanent ID: | export format: | export limit: | evidence:
[repeat for WAMUQ, CELG, KD, XLNX, HTZ]

Platform: Finaeon
[same six]
```
Send those and I fill this grid + document provenance. **No panel change until the pilot produces evidence.**
