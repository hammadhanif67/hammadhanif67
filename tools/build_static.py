"""Builds the static profile images: hero, link buttons, tech stack and avatar.

Run from the repo root:  python tools/build_static.py
"""
import os

from svgtype import BG, DIM, EDGE, INK, LINE, MUTED, PANEL, RED, Canvas, logo

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
os.makedirs(OUT, exist_ok=True)


def hero():
    W, H = 1280, 320
    c = Canvas(W, H, 'Hammad Minhas, Full-Stack Developer: React, Next.js, TypeScript, FastAPI')
    c.rect(0, 0, W, H, BG)
    c.rect(0.5, 0.5, W - 1, H - 1, 'none', EDGE)
    logo(c, 72, 91)
    c.text('Hammad Minhas', 'InterTight', 800, 68, 262, 148, INK, tracking=-0.02)
    c.rect(265, 170, 64, 4, RED)
    c.text('Full-Stack Developer', 'Inter', 600, 25, 264, 214, INK)
    c.text('React   ·   Next.js   ·   TypeScript   ·   FastAPI', 'Inter', 400, 19, 264, 248, MUTED)
    c.text('SOFTWARE ENGINEERING · GCUF · FAISALABAD', 'Inter', 600, 12, W - 72, H - 40, DIM, tracking=0.14, anchor='end')
    c.save(os.path.join(OUT, 'hero.svg'))


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
    """Square profile picture: the name set in Inter Tight, centred for GitHub's circular crop."""
    S = 800
    c = Canvas(S, S, 'Hammad Minhas')
    c.rect(0, 0, S, S, BG)
    c.text('Hammad', 'InterTight', 800, 132, S / 2, 382, INK, tracking=-0.03, anchor='middle')
    c.text('Minhas', 'InterTight', 800, 132, S / 2, 512, INK, tracking=-0.03, anchor='middle')
    c.rect(S / 2 - 44, 560, 88, 8, RED)
    c.save(os.path.join(OUT, 'avatar.svg'))


if __name__ == '__main__':
    hero()
    button('btn-portfolio.svg', 'PORTFOLIO')
    button('btn-linkedin.svg', 'LINKEDIN')
    button('btn-trenvo.svg', 'TRENVO MEDIA')
    button('btn-open.svg', 'OPEN TO WORK', primary=True)
    tech_stack()
    avatar()
