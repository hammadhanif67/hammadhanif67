"""Builds the static profile images: hero, link buttons, tech stack and avatar.

Run from the repo root:  python tools/build_static.py
"""
import os

from svgtype import BG, DIM, EDGE, INK, LINE, MUTED, PANEL, RED, Canvas, logo

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
os.makedirs(OUT, exist_ok=True)


BOLD, LIGHT = 'MinhasDisplay-Bold', 'MinhasDisplay-Light'


def brand_defs(c):
    """Paint servers shared by the wordmark: brushed silver, red metal and a red glow."""
    c.define('<linearGradient id="silver" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#7d838c"/><stop offset=".38" stop-color="#c9ced4"/>'
             '<stop offset=".5" stop-color="#ffffff"/><stop offset=".56" stop-color="#b4bac1"/>'
             '<stop offset="1" stop-color="#f7f8fa"/></linearGradient>')
    c.define('<linearGradient id="redmetal" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#8a0008"/><stop offset=".45" stop-color="#E30613"/>'
             '<stop offset=".55" stop-color="#ff2b2b"/><stop offset="1" stop-color="#ff5a52"/></linearGradient>')
    c.define('<filter id="glow" x="-15%" y="-80%" width="130%" height="260%">'
             '<feGaussianBlur in="SourceGraphic" stdDeviation="90" result="b1"/>'
             '<feGaussianBlur in="SourceGraphic" stdDeviation="28" result="b2"/>'
             '<feMerge><feMergeNode in="b1"/><feMergeNode in="b2"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    c.define('<filter id="sheen" x="-5%" y="-20%" width="110%" height="140%">'
             '<feGaussianBlur in="SourceAlpha" stdDeviation="40" result="s"/>'
             '<feOffset in="s" dy="-60" result="o"/><feFlood flood-color="#000" flood-opacity=".55"/>'
             '<feComposite in2="o" operator="in" result="sh"/>'
             '<feMerge><feMergeNode in="sh"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    c.define('<linearGradient id="lineL" x1="0" x2="1"><stop offset="0" stop-color="#E30613" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#E30613"/></linearGradient>')
    c.define('<linearGradient id="lineR" x1="0" x2="1"><stop offset="0" stop-color="#E30613"/>'
             '<stop offset="1" stop-color="#E30613" stop-opacity="0"/></linearGradient>')
    c.define('<radialGradient id="vignette" cx=".62" cy=".45" r=".7">'
             '<stop offset="0" stop-color="#1a0204"/><stop offset=".55" stop-color="#070707"/>'
             '<stop offset="1" stop-color="#030303"/></radialGradient>')


def wordmark(c, cx, baseline, size, gap_ratio=0.38, tracking=0.06):
    """HAMMAD in silver, MINHAS in glowing red metal, centred on cx. Returns total width."""
    w1 = c.measure('HAMMAD', BOLD, 0, size, tracking)
    w2 = c.measure('MINHAS', BOLD, 0, size, tracking)
    gap = size * gap_ratio
    x = cx - (w1 + gap + w2) / 2
    c.text('HAMMAD', BOLD, 0, size, x, baseline, 'url(#silver)', tracking, attrs='filter="url(#sheen)"')
    c.text('MINHAS', BOLD, 0, size, x + w1 + gap, baseline, 'url(#redmetal)', tracking, attrs='filter="url(#glow)"')
    return w1 + gap + w2


def tagline(c, cx, baseline, size, left, right, rule):
    """Widely tracked line in the light weight, white then red, between fading red rules."""
    t = 0.42
    lw = c.measure(left + '  ', LIGHT, 0, size, t)
    rw = c.measure(right, LIGHT, 0, size, t)
    x = cx - (lw + rw) / 2
    c.text(left, LIGHT, 0, size, x, baseline, INK, t)
    c.text(right, LIGHT, 0, size, x + lw, baseline, RED, t)
    y = baseline - size * 0.36
    c.rect(x - 32 - rule, y - 1, rule, 2, 'url(#lineL)')
    c.rect(x + lw + rw + 32 - size * t, y - 1, rule, 2, 'url(#lineR)')


def hero():
    W, H = 1280, 360
    c = Canvas(W, H, 'Hammad Minhas, Full-Stack Developer: React, Next.js, TypeScript, FastAPI')
    brand_defs(c)
    c.rect(0, 0, W, H, 'url(#vignette)')
    c.rect(0.5, 0.5, W - 1, H - 1, 'none', '#1d1d1d')
    wordmark(c, W / 2, 196, 96)
    tagline(c, W / 2, 262, 19, 'FULL-STACK', 'DEVELOPER', 150)
    c.text('REACT  ·  NEXT.JS  ·  TYPESCRIPT  ·  FASTAPI', LIGHT, 0, 13, W / 2, 314, MUTED, tracking=0.32, anchor='middle')
    c.save(os.path.join(OUT, 'banner.svg'))


def button(fname, label, primary=False):
    size, h, pad = 14, 40, 20
    probe = Canvas(1, 1, '')
    tw = probe.measure(label, 'Inter', 600, size, tracking=0.06)
    aw = probe.measure('↗', 'Inter', 500, size)
    w = round(pad + tw + 10 + aw + pad)
    c = Canvas(w, h, label.title())
    fill, stroke, ink = (RED, RED, '#ffffff') if primary else (BG, '#333333', INK)
    c.rect(0.5, 0.5, w - 1, h - 1, fill, stroke)
    c.text(label, 'Inter', 600, size, pad, 25, ink, tracking=0.06)
    c.text('↗', 'Inter', 500, size, pad + tw + 10, 25, ink if primary else MUTED)
    c.save(os.path.join(OUT, fname))


STACK = [
    ('LANGUAGES', [('TypeScript', 'typescript'), ('JavaScript', 'javascript'), ('Python', 'python'),
                   ('HTML5', 'html5'), ('CSS', 'css'), ('C++', 'cplusplus'), ('SQL', 'sqlite')]),
    ('FRAMEWORKS', [('React 19', 'react'), ('Next.js 16', 'nextdotjs'), ('Vite', 'vite'),
                    ('Tailwind CSS', 'tailwindcss'), ('FastAPI', 'fastapi'), ('Framer Motion', 'framer'),
                    ('GSAP', 'greensock')]),
    ('QUALITY', [('Playwright', None), ('axe-core', None), ('Lighthouse CI', 'lighthouse'),
                 ('ESLint', 'eslint'), ('Prettier', 'prettier'), ('Strict TypeScript', 'typescript'),
                 ('WCAG 2.2 AA', None)]),
    ('PLATFORM', [('Cloudflare Pages', 'cloudflarepages'), ('Cloudflare D1 / R2', 'cloudflare'),
                  ('Vercel', 'vercel'), ('GitHub Actions', 'githubactions'), ('Git', 'git'),
                  ('SQLite', 'sqlite'), ('Node.js', 'nodedotjs')]),
]


def tech_stack():
    W, top, row, pad = 960, 104, 42, 48
    rows = max(len(items) for _, items in STACK)
    H = top + row * (rows - 1) + 48
    label = 'Tech stack. ' + '. '.join(h.title() + ': ' + ', '.join(n for n, _ in items) for h, items in STACK)
    c = Canvas(W, H, label)
    c.rect(0, 0, W, H, BG)
    c.rect(0.5, 0.5, W - 1, H - 1, 'none', EDGE)
    colw = (W - 2 * pad) / 4
    for i, (head, items) in enumerate(STACK):
        x = pad + i * colw
        c.text('0%d' % (i + 1), 'Inter', 600, 13, x, 56, RED, tracking=0.12)
        c.text(head, 'Inter', 600, 13, x + 30, 56, MUTED, tracking=0.14)
        c.rect(x, 72, colw - 24, 1, LINE)
        for j, (name, icon) in enumerate(items):
            y = top + j * row
            if icon:
                c.icon(icon, x, y - 15, 18, '#d4d4d4')
            else:
                c.rect(x + 5, y - 10, 8, 8, RED)
            c.text(name, 'Inter', 500, 19, x + 30, y, INK)
    c.save(os.path.join(OUT, 'tech.svg'))


def avatar():
    """Square profile picture: the wordmark stacked, centred for GitHub's circular crop."""
    S = 800
    c = Canvas(S, S, 'Hammad Minhas')
    brand_defs(c)
    c.rect(0, 0, S, S, 'url(#vignette)')
    size, t = 112, 0.05
    for word, fill, attrs, base in [('HAMMAD', 'url(#silver)', 'filter="url(#sheen)"', 372),
                                    ('MINHAS', 'url(#redmetal)', 'filter="url(#glow)"', 512)]:
        c.text(word, BOLD, 0, size, S / 2, base, fill, t, anchor='middle', attrs=attrs)
    c.rect(S / 2 - 120, 566, 240, 2, 'url(#lineL)')
    c.rect(S / 2, 566, 120, 2, RED)
    c.save(os.path.join(OUT, 'avatar.svg'))


if __name__ == '__main__':
    hero()
    button('btn-portfolio.svg', 'PORTFOLIO')
    button('btn-linkedin.svg', 'LINKEDIN')
    button('btn-trenvo.svg', 'TRENVO MEDIA')
    button('btn-open.svg', 'OPEN TO WORK', primary=True)
    tech_stack()
    avatar()
