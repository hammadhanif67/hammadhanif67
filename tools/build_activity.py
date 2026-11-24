"""Builds assets/activity.svg from the GitHub API: contribution total, streaks and a
year-long contribution grid, drawn in the profile's own style. Runs daily in Actions.

Needs GITHUB_TOKEN (or GH_TOKEN) in the environment. Usage:
    python tools/build_activity.py <login> <output.svg>
"""
import datetime as dt
import json
import os
import sys
import urllib.request

from svgtype import BG, DIM, EDGE, INK, LINE, MUTED, RED, Canvas

LOGIN, OUT = sys.argv[1], sys.argv[2]
TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')

QUERY = """query($login:String!){ user(login:$login){
  repositories(privacy:PUBLIC, ownerAffiliations:OWNER){ totalCount }
  contributionsCollection{ contributionCalendar{ totalContributions
    weeks{ contributionDays{ date contributionCount contributionLevel } } } } } }"""


def fetch():
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode(),
        headers={'Authorization': 'bearer ' + TOKEN, 'Content-Type': 'application/json',
                 'User-Agent': 'profile-activity'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if 'errors' in data:
        raise SystemExit(data['errors'])
    return data['data']['user']


def streaks(days):
    counts = [d['contributionCount'] for d in days]
    longest = run = 0
    for n in counts:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not counted yet: start from yesterday
        i -= 1
    while i >= 0 and counts[i]:
        current, i = current + 1, i - 1
    return current, longest


LEVEL = {'NONE': '#1a1a1a', 'FIRST_QUARTILE': '#4a0b0e', 'SECOND_QUARTILE': '#7d0c12',
         'THIRD_QUARTILE': '#b30a14', 'FOURTH_QUARTILE': RED}


def build(user):
    cal = user['contributionsCollection']['contributionCalendar']
    weeks = cal['weeks']
    days = [d for w in weeks for d in w['contributionDays']]
    current, longest = streaks(days)
    active = sum(1 for d in days if d['contributionCount'])

    W, pad = 960, 48
    cell, gap = 13, 3
    grid_top = 212
    H = grid_top + 7 * (cell + gap) + 62
    c = Canvas(W, H, f"{cal['totalContributions']} contributions in the last year, "
                     f"current streak {current} days, longest streak {longest} days")
    c.rect(0, 0, W, H, BG)
    c.rect(0.5, 0.5, W - 1, H - 1, 'none', EDGE)

    stats = [('CONTRIBUTIONS', str(cal['totalContributions']), 'past 12 months'),
             ('CURRENT STREAK', str(current), 'days in a row' if current != 1 else 'day'),
             ('LONGEST STREAK', str(longest), 'days in a row' if longest != 1 else 'day'),
             ('ACTIVE DAYS', str(active), 'past 12 months'),
             ('PUBLIC REPOS', str(user['repositories']['totalCount']), 'open source')]
    colw = (W - 2 * pad) / len(stats)
    for i, (label, value, unit) in enumerate(stats):
        x = pad + i * colw
        c.text(label, 'Inter', 600, 12, x, 52, MUTED, tracking=0.14)
        c.text(value, 'MinhasDisplay-Bold', 0, 42, x, 104, RED if i == 1 else INK, tracking=0.04)
        c.text(unit, 'Inter', 500, 13, x, 128, DIM)
        if i:
            c.rect(x - 16, 36, 1, 96, LINE)
    c.rect(pad, 160, W - 2 * pad, 1, LINE)

    # month labels + grid (most recent 53 weeks, right-aligned)
    weeks = weeks[-53:]
    gx = W - pad - len(weeks) * (cell + gap) + gap
    last_month = None
    for wi, w in enumerate(weeks):
        x = gx + wi * (cell + gap)
        first = dt.date.fromisoformat(w['contributionDays'][0]['date'])
        if first.month != last_month and first.day <= 7 and wi < len(weeks) - 2:
            c.text(first.strftime('%b'), 'Inter', 500, 11, x, grid_top - 12, DIM)
            last_month = first.month
        for d in w['contributionDays']:
            wd = (dt.date.fromisoformat(d['date']).weekday() + 1) % 7  # Sunday = 0
            c.rect(x, grid_top + wd * (cell + gap), cell, cell, LEVEL.get(d['contributionLevel'], '#1a1a1a'))

    fy = grid_top + 7 * (cell + gap) + 30
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%d %b %Y')
    c.text('UPDATED ' + stamp.upper(), 'Inter', 600, 11, pad, fy, DIM, tracking=0.12)
    mw = c.measure('MORE', 'Inter', 600, 11, tracking=0.12)
    lx = W - pad - mw - 10 - 5 * (cell + gap) + gap
    c.text('LESS', 'Inter', 600, 11, lx - 10, fy, DIM, tracking=0.12, anchor='end')
    for k, col in enumerate(LEVEL.values()):
        c.rect(lx + k * (cell + gap), fy - 11, cell, cell, col)
    c.text('MORE', 'Inter', 600, 11, W - pad, fy, DIM, tracking=0.12, anchor='end')
    c.save(OUT)


if __name__ == '__main__':
    build(fetch())
