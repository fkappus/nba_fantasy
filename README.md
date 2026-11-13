# NBA Europe Luck Report

A weekly page for our ESPN fantasy league: who earned their wins and who got the schedule.

- `ingest.py` pulls each week's category totals from ESPN
- `metrics.py` works out all-play records, expected wins and luck
- `build.py` writes `index.html`, the page GitHub Pages serves

The page rebuilds every Monday through GitHub Actions. It needs three repository secrets: `ESPN_S2`, `SWID` and `LEAGUE_ID`.
