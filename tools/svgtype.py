"""Tiny typesetting helper: draws text as vector outlines of a real font inside an SVG.

Every glyph is written once in <defs> and placed with <use>, so repeated letters cost a
few bytes instead of a full outline. That keeps the images small and fast to load.
"""
import os
import re
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'fonts')
ICON_DIR = os.path.join(HERE, 'icons')

# Palette (shared by every image)
BG, PANEL, EDGE, LINE = '#0b0b0b', '#111111', '#232323', '#2e2e2e'
INK, MUTED, DIM, RED = '#f5f5f5', '#a3a3a3', '#6b6b6b', '#E30613'

_fonts, _kerns = {}, {}


def _num(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def _font(family, wght):
    key = (family, wght)
    if key not in _fonts:
        f = TTFont(os.path.join(FONT_DIR, family + '.ttf'))
        if 'fvar' not in f:            # static font (e.g. MinhasDisplay-Bold)
            _fonts[key] = f
            return f
        axes = {a.axisTag: a for a in f['fvar'].axes}
        loc = {'wght': wght}
        if 'opsz' in axes:
            loc['opsz'] = axes['opsz'].maxValue if wght >= 600 else axes['opsz'].defaultValue
        _fonts[key] = instancer.instantiateVariableFont(f, loc)
    return _fonts[key]


def _kern(f, key):
    if key in _kerns:
        return _kerns[key]
    pairs = {}
    if 'GPOS' in f:
        for lookup in f['GPOS'].table.LookupList.Lookup:
            if lookup.LookupType not in (2, 9):
                continue
            for st in lookup.SubTable:
                if lookup.LookupType == 9:
                    st = st.ExtSubTable
                if getattr(st, 'LookupType', 2) != 2:
                    continue
                cov = st.Coverage.glyphs
                if st.Format == 1:
                    for i, g1 in enumerate(cov):
                        for pvr in st.PairSet[i].PairValueRecord:
                            v = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                            if v:
                                pairs.setdefault((g1, pvr.SecondGlyph), v)
                elif st.Format == 2:
                    cd1, cd2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                    for g1 in cov:
                        rec = st.Class1Record[cd1.get(g1, 0)]
                        for g2, c2 in cd2.items():
                            v1 = rec.Class2Record[c2].Value1
                            v = getattr(v1, 'XAdvance', 0) if v1 else 0
                            if v:
                                pairs.setdefault((g1, g2), v)
    _kerns[key] = pairs
    return pairs


class Canvas:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.defs, self.ids, self.body = [], {}, []

    # -- primitives -------------------------------------------------------
    def rect(self, x, y, w, h, fill, stroke=None):
        s = f' stroke="{stroke}"' if stroke else ''
        self.body.append(f'<rect x="{_num(x)}" y="{_num(y)}" width="{_num(w)}" height="{_num(h)}" fill="{fill}"{s}/>')

    def raw(self, svg):
        self.body.append(svg)

    def define(self, svg):
        """Add a gradient, filter or other paint server to <defs>."""
        self.defs.append(svg)

    # -- text -------------------------------------------------------------
    def _glyph_id(self, family, wght, name, f):
        key = (family, wght, name)
        if key not in self.ids:
            gid = 'g%d' % len(self.ids)
            pen = SVGPathPen(f.getGlyphSet(), ntos=lambda v: str(int(round(v))))
            f.getGlyphSet()[name].draw(pen)
            d = pen.getCommands()
            self.ids[key] = gid if d else None
            if d:
                self.defs.append(f'<path id="{gid}" d="{d}"/>')
        return self.ids[key]

    def measure(self, s, family, wght, size, tracking=0.0):
        return self.text(s, family, wght, size, 0, 0, None, tracking, draw=False)

    def text(self, s, family, wght, size, x, y, fill, tracking=0.0, anchor='start', draw=True, attrs=''):
        f = _font(family, wght)
        kp = _kern(f, (family, wght))
        cmap, hmtx = f.getBestCmap(), f['hmtx']
        sc = size / f['head'].unitsPerEm
        names = [cmap.get(ord(c), '.notdef') for c in s]
        adv = []
        for i, g in enumerate(names):
            nxt = names[i + 1] if i + 1 < len(names) else None
            a = (hmtx[g][0] + (kp.get((g, nxt), 0) if nxt else 0)) * sc
            adv.append(a + (tracking * size if nxt else 0))
        width = sum(adv)
        if not draw:
            return width
        if anchor == 'end':
            x -= width
        elif anchor == 'middle':
            x -= width / 2
        uses, cx = [], x
        for g, a in zip(names, adv):
            gid = self._glyph_id(family, wght, g, f)
            if gid:
                uses.append(f'<use href="#{gid}" x="{_num(cx / sc)}"/>')
            cx += a
        self.body.append(f'<g fill="{fill}"{(" " + attrs) if attrs else ""} transform="translate({_num(0)} {_num(y)}) scale({sc:.5f} {-sc:.5f})">{"".join(uses)}</g>')
        return width

    # -- icons (Simple Icons, 24x24) -------------------------------------
    def icon(self, name, x, y, size, fill):
        key = ('icon', name)
        if key not in self.ids:
            path = os.path.join(ICON_DIR, name + '.svg')
            d = re.search(r'<path d="([^"]+)"', open(path, encoding='utf-8').read()).group(1)
            gid = 'i%d' % len(self.ids)
            self.ids[key] = gid
            self.defs.append(f'<path id="{gid}" d="{d}"/>')
        s = size / 24
        self.body.append(f'<use href="#{self.ids[key]}" fill="{fill}" transform="translate({_num(x)} {_num(y)}) scale({s:.4f})"/>')

    def svg(self):
        label = escape(self.label, {'"': '&quot;'})
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}"><title>{label}</title>'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')

    def save(self, path):
        data = self.svg()
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(data)
        print('wrote', os.path.basename(path), '%.1f KB' % (len(data) / 1024))


def logo(c, x, y, cell=40, gap=6, ink=INK, hole='#1c1c1c'):
    """The 3x3 grid mark: a C with a red core."""
    for r in range(3):
        for col in range(3):
            fill = RED if (r, col) == (1, 1) else (hole if (r, col) == (1, 2) else ink)
            c.rect(x + col * (cell + gap), y + r * (cell + gap), cell, cell, fill)
