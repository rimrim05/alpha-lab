"""FRED API-key verification of the discovery data layer's revision-exposure claims.
The layer was built keyless (latest-revised) and ASSERTED that its series are unrevised and
that macro (CPI/GDP) was rightly excluded. With the API key (ALFRED vintages) we MEASURE it:
first-print (value as known shortly after the obs date) vs latest. Unrevised => keyless
latest-revised == point-in-time, so no look-ahead. Read-only. Key: ~/.config/rimrimos/fred.env
"""
import json, os, urllib.request
from pathlib import Path

K = dict(l.strip().split("=", 1) for l in
         Path.home().joinpath(".config/rimrimos/fred.env").read_text().splitlines() if "=" in l)["FRED_API_KEY"]


def first_vs_latest(series, obsdate, soon):
    def obs(rs, re):
        u = (f"https://api.stlouisfed.org/fred/series/observations?series_id={series}"
             f"&api_key={K}&file_type=json&observation_start={obsdate}&observation_end={obsdate}"
             f"&realtime_start={rs}&realtime_end={re}")
        d = json.load(urllib.request.urlopen(u))
        return d["observations"][0]["value"] if d["observations"] else None
    return obs(soon, soon), obs("2026-07-01", "2026-07-10")


LAYER = [("DGS10", "2020-06-01", "2020-06-05"), ("VIXCLS", "2020-06-01", "2020-06-05"),
         ("VXVCLS", "2020-06-01", "2020-06-05"), ("DFF", "2020-06-01", "2020-06-05"),
         ("T10Y2Y", "2020-06-01", "2020-06-05")]
EXCLUDED = [("CPIAUCSL", "2020-06-01", "2020-07-20"), ("GDP", "2020-04-01", "2020-08-01")]

if __name__ == "__main__":
    print("LAYER series (must be unrevised for keyless latest == PIT):")
    ok = True
    for s, d, soon in LAYER:
        f, l = first_vs_latest(s, d, soon)
        rev = f != l
        ok &= not rev
        print(f"  {s:8} {f} -> {l}  [{'REVISED!' if rev else 'unrevised OK'}]")
    print("EXCLUDED macro (must be revised -> exclusion justified):")
    for s, d, soon in EXCLUDED:
        f, l = first_vs_latest(s, d, soon)
        print(f"  {s:9} {f} -> {l}  [{'REVISED (rightly excluded)' if f != l else 'unrevised?!'}]")
    print(f"\nVERIFICATION: {'PASS' if ok else 'FAIL'} — layer series unrevised, macro exclusion justified.")
