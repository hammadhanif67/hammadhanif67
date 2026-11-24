"""Generate the profile's SVG images with text converted to outlines (Inter / Inter Tight),
so they render in the real typeface inside GitHub's <img> tags (which cannot load web fonts)."""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

_cache = {}
def font(family, wght):
    key = (family, wght)
    if key not in _cache:
        f = TTFont(os.path.join(FONT_DIR, family + '.ttf'))
        axes = {a.axisTag: a for a in f['fvar'].axes}
        loc = {'wght': wght}
        if 'opsz' in axes:
            loc['opsz'] = axes['opsz'].maxValue if wght >= 600 else axes['opsz'].defaultValue
        _cache[key] = instancer.instantiateVariableFont(f, loc)
    return _cache[key]

def kern_pairs(f):
    """Pair-adjustment kerning from GPOS (format 1 and 2), best effort."""
    pairs = {}
    if 'GPOS' not in f: return pairs
    for lookup in f['GPOS'].table.LookupList.Lookup:
        if lookup.LookupType not in (2, 9): continue
        for st in lookup.SubTable:
            if lookup.LookupType == 9: st = st.ExtSubTable
            if getattr(st, 'LookupType', 2) != 2: continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for i, g1 in enumerate(cov):
                    for pvr in st.PairSet[i].PairValueRecord:
                        v = pvr.Value1.XAdvance if pvr.Value1 and hasattr(pvr.Value1, 'XAdvance') else 0
                        if v: pairs.setdefault((g1, pvr.SecondGlyph), v)
            elif st.Format == 2:
                cd1, cd2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                for g1 in cov:
                    c1 = cd1.get(g1, 0)
                    rec = st.Class1Record[c1]
                    for g2, c2 in cd2.items():
                        v1 = rec.Class2Record[c2].Value1
                        v = getattr(v1, 'XAdvance', 0) if v1 else 0
                        if v: pairs.setdefault((g1, g2), v)
    return pairs

_kern = {}
def text_path(s, family, wght, size, x, y, fill, tracking=0.0, anchor='start'):
    f = font(family, wght)
    key = (family, wght)
    if key not in _kern: _kern[key] = kern_pairs(f)
    kp = _kern[key]
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f['hmtx']
    upm = f['head'].unitsPerEm
    scale = size / upm
    names = [cmap.get(ord(c), '.notdef') for c in s]
    # total advance
    adv = []
    for i, g in enumerate(names):
        a = hmtx[g][0] + (kp.get((g, names[i + 1]), 0) if i + 1 < len(names) else 0)
        adv.append(a * scale + (tracking * size if i + 1 < len(names) else 0))
    width = sum(adv)
    if anchor == 'end': x -= width
    elif anchor == 'middle': x -= width / 2
    d, cx = [], x
    for g, a in zip(names, adv):
        pen = SVGPathPen(gs, ntos=lambda v: ('%.1f' % v).rstrip('0').rstrip('.'))
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
        if pen.getCommands(): d.append(pen.getCommands())
        cx += a
    return f'<path fill="{fill}" d="{" ".join(d)}"/>', width

def measure(s, family, wght, size, tracking=0.0):
    return text_path(s, family, wght, size, 0, 0, '#000', tracking)[1]

def save(name, w, h, body, label):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="{label}"><title>{label}</title>{body}</svg>')
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(svg)
    print('wrote', name, len(svg) // 1024, 'KB')

BG, EDGE, INK, MUTED, DIM, RED = '#0b0b0b', '#232323', '#f5f5f5', '#a3a3a3', '#6b6b6b', '#E30613'

def logo(x, y, cell=40, gap=6):
    out = []
    for r in range(3):
        for c in range(3):
            col = RED if (r, c) == (1, 1) else ('#1c1c1c' if (r, c) == (1, 2) else INK)
            out.append(f'<rect x="{x + c*(cell+gap)}" y="{y + r*(cell+gap)}" width="{cell}" height="{cell}" fill="{col}"/>')
    return ''.join(out)

# ---------- hero ----------
W, H = 1280, 320
b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{EDGE}"/>',
     logo(72, 91)]
p, _ = text_path('Hammad Minhas', 'InterTight', 800, 68, 262, 148, INK, tracking=-0.02); b.append(p)
b.append(f'<rect x="265" y="170" width="64" height="4" fill="{RED}"/>')
p, _ = text_path('Full-Stack Developer', 'Inter', 600, 25, 264, 214, INK); b.append(p)
p, _ = text_path('React   ·   Next.js   ·   TypeScript   ·   FastAPI', 'Inter', 400, 19, 264, 248, MUTED); b.append(p)
p, _ = text_path('SOFTWARE ENGINEERING · GCUF · FAISALABAD', 'Inter', 600, 12, W - 72, H - 40, DIM, tracking=0.14, anchor='end'); b.append(p)
save('hero.svg', W, H, ''.join(b), 'Hammad Minhas, Full-Stack Developer: React, Next.js, TypeScript, FastAPI')

# ---------- buttons ----------
def button(name, text, primary=False):
    size, h, padx = 14, 40, 20
    arrow_w = measure('↗', 'Inter', 500, size)
    tw = measure(text, 'Inter', 600, size, tracking=0.06)
    w = round(padx + tw + 10 + arrow_w + padx)
    fill, stroke, ink = (RED, RED, '#ffffff') if primary else (BG, '#333333', INK)
    body = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" fill="{fill}" stroke="{stroke}"/>']
    p, _ = text_path(text, 'Inter', 600, size, padx, 25, ink, tracking=0.06); body.append(p)
    p, _ = text_path('↗', 'Inter', 500, size, padx + tw + 10, 25, ink if primary else MUTED); body.append(p)
    save(name, w, h, ''.join(body), text.title())

button('btn-portfolio.svg', 'PORTFOLIO')
button('btn-linkedin.svg', 'LINKEDIN')
button('btn-trenvo.svg', 'TRENVO MEDIA')
button('btn-open.svg', 'OPEN TO WORK', primary=True)

# ---------- stack panel ----------
cols = [('LANGUAGES', ['TypeScript', 'JavaScript', 'Python', 'HTML & CSS', 'C++', 'SQL', '8086 Assembly']),
        ('FRAMEWORKS', ['React 19', 'Next.js 16', 'Vite', 'Tailwind CSS', 'FastAPI', 'Framer Motion', 'GSAP']),
        ('QUALITY', ['Playwright', 'axe-core', 'Lighthouse CI', 'ESLint', 'Prettier', 'Strict TypeScript', 'WCAG 2.2 AA']),
        ('PLATFORM', ['Cloudflare Pages', 'Cloudflare D1 / R2', 'Vercel', 'GitHub Actions', 'Git', 'SQLite', 'Node.js'])]
W, row, top = 1280, 34, 96
H = top + row * max(len(c[1]) for c in cols) + 40
b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{EDGE}"/>']
colw = (W - 144) / 4
for i, (head, items) in enumerate(cols):
    x = 72 + i * colw
    p, _ = text_path(f'0{i+1}', 'Inter', 600, 12, x, 56, RED, tracking=0.12); b.append(p)
    p, _ = text_path(head, 'Inter', 600, 12, x + 30, 56, MUTED, tracking=0.16); b.append(p)
    b.append(f'<rect x="{x}" y="70" width="{colw - 40}" height="1" fill="{EDGE}"/>')
    for j, it in enumerate(items):
        p, _ = text_path(it, 'Inter', 500, 18, x, top + 10 + j * row, INK); b.append(p)
save('stack.svg', W, round(H), ''.join(b), 'Tech stack: ' + '; '.join(h + ': ' + ', '.join(i) for h, i in cols))
