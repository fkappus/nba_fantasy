"""Pull both seasons from ESPN. Credentials come from environment variables
(ESPN_S2, SWID, LEAGUE_ID) or a local .env file. Never commit them."""
import json, os, requests
env = {}
if os.path.exists('.env'):
    env = dict(l.strip().split('=', 1) for l in open('.env') if '=' in l)
get = lambda k: os.environ.get(k) or env[k]
ck = {'espn_s2': get('ESPN_S2'), 'SWID': get('SWID')}
for yr in [2026, 2027]:
    u = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/{yr}/segments/0/leagues/{get('LEAGUE_ID')}"
    r = requests.get(u, params={'view': ['mMatchup', 'mTeam', 'mSettings', 'mStandings']}, cookies=ck, timeout=60)
    r.raise_for_status()
    d = r.json()
    json.dump(d, open(f'raw_{yr}.json', 'w'))
    print(yr, 'ok', len(d['schedule']))
