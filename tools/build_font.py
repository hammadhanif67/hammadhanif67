"""Minhas Display: an original geometric, extended, all-caps display typeface.

Design rules
  * Cap height 700 on a 1000-unit em; wide proportions.
  * Uniform stroke (Bold 150, Light 56). Straight lines only.
  * Round forms become chamfered octagons: every outer corner of a bowl is cut at 45 degrees.
  * Diagonals end in horizontal terminals (clipped to the baseline and cap height).
  * Lowercase maps to the capitals.

Usage:  python tools/build_font.py <out_dir>
Writes MinhasDisplay-Bold.ttf / -Light.ttf (and .woff2 when brotli is available).
"""
import math
import os
import sys

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely.affinity import translate
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

H = 700                      # cap height
UPM = 1000
FAMILY = 'Minhas Display'
VERSION = '1.000'


# ---------------------------------------------------------------- primitives
def cbox(x0, y0, x1, y1, c, corners=('tl', 'tr', 'br', 'bl')):
    """Rectangle with 45-degree chamfers on the listed corners."""
    c = max(0.0, min(c, (x1 - x0) / 2 - 1, (y1 - y0) / 2 - 1))
    p = []
    p += [(x0, y0 + c), (x0 + c, y0)] if 'bl' in corners and c else [(x0, y0)]
    p += [(x1 - c, y0), (x1, y0 + c)] if 'br' in corners and c else [(x1, y0)]
    p += [(x1, y1 - c), (x1 - c, y1)] if 'tr' in corners and c else [(x1, y1)]
    p += [(x0 + c, y1), (x0, y1 - c)] if 'tl' in corners and c else [(x0, y1)]
    return Polygon(p)


def ring(x0, y0, x1, y1, s, c, corners=('tl', 'tr', 'br', 'bl')):
    """Chamfered frame with an even stroke along straight and diagonal sides."""
    inner_c = max(1.0, c - s * (math.sqrt(2) - 1))
    return cbox(x0, y0, x1, y1, c, corners).difference(cbox(x0 + s, y0 + s, x1 - s, y1 - s, inner_c, corners))


def stroke(p1, p2, s, x_min=-1e4, x_max=1e4, y_min=0, y_max=H):
    """Straight stroke of width s, extended and clipped so its ends are horizontal."""
    (x1, y1), (x2, y2) = p1, p2
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    ext = s * 2
    line = LineString([(x1 - ux * ext, y1 - uy * ext), (x2 + ux * ext, y2 + uy * ext)])
    shape = line.buffer(s / 2, cap_style='flat', join_style='mitre')
    return shape.intersection(box(x_min, y_min, x_max, y_max))


def cut(g, x, y, c, quadrant):
    """Chamfer an outer corner at (x, y). quadrant: direction pointing into the glyph."""
    dx, dy = {'tl': (1, -1), 'tr': (-1, -1), 'br': (-1, 1), 'bl': (1, 1)}[quadrant]
    return g.difference(Polygon([(x - dx, y - dy), (x + dx * c, y - dy), (x - dx, y + dy * c)]))


def U(*gs):
    return unary_union([g for g in gs if g is not None and not g.is_empty])


# ---------------------------------------------------------------- glyphs
def glyphs(S):
    C = 210                  # outer chamfer
    M = H / 2                # vertical middle
    Ch = C * 0.62            # smaller chamfer for half-height bowls
    g = {}

    def bar(x0, x1, yc):
        return box(x0, yc - S / 2, x1, yc + S / 2)

    w = 780; g['A'] = (U(ring(0, -S - 2, w, H, S, C, ('tl', 'tr')).intersection(box(-1, 0, w + 1, H)),
                         box(0, H * 0.30, w, H * 0.30 + S)), w)
    w = 720; g['B'] = (U(ring(0, M - S / 2, w - 44, H, S, Ch, ('tr', 'br')),
                         ring(0, 0, w, M + S / 2, S, Ch, ('tr', 'br'))), w)
    w = 740; g['C'] = (ring(0, 0, w, H, S, C).difference(box(w - S - 1, S, w + 1, H - S)), w)
    w = 740; g['D'] = (ring(0, 0, w, H, S, C, ('tr', 'br')), w)
    w = 640; g['E'] = (U(box(0, 0, S, H), box(0, H - S, w, H), bar(0, w * 0.84, M), box(0, 0, w, S)), w)
    w = 620; g['F'] = (U(box(0, 0, S, H), box(0, H - S, w, H), bar(0, w * 0.84, M - S * 0.25)), w)
    w = 760; g['G'] = (U(ring(0, 0, w, H, S, C).difference(box(w - S - 1, M, w + 1, H - S)),
                         box(w * 0.46, M - S / 2, w, M + S / 2).intersection(box(0, 0, w, M + S / 2))), w)
    w = 720; g['H'] = (U(box(0, 0, S, H), box(w - S, 0, w, H), bar(0, w, M)), w)
    w = S;   g['I'] = (box(0, 0, S, H), w)
    w = 640; g['J'] = (ring(0, 0, w, H + S + 2, S, C, ('bl', 'br')).intersection(box(-1, 0, w + 1, H))
                       .difference(box(-1, H * 0.36, S + 1, H + 1)), w)
    w = 720; g['K'] = (U(box(0, 0, S, H),
                         stroke((S * 0.4, M - S * 0.55), (w - S * 0.62, H), S, x_min=S * 0.5, x_max=w),
                         stroke((w * 0.34, M + S * 0.05), (w - S * 0.62, 0), S, x_min=S * 0.5, x_max=w)), w)
    w = 600; g['L'] = (U(box(0, 0, S, H), box(0, 0, w, S)), w)
    w = 900; g['M'] = (U(box(0, 0, S, H), box(w - S, 0, w, H),
                         stroke((S * 0.5, H), (w / 2, H * 0.28), S, x_min=0, x_max=w / 2),
                         stroke((w / 2, H * 0.28), (w - S * 0.5, H), S, x_min=w / 2, x_max=w)), w)
    w = 740; g['N'] = (U(box(0, 0, S, H), box(w - S, 0, w, H),
                         stroke((S * 0.5, H), (w - S * 0.5, 0), S, x_min=0, x_max=w)), w)
    w = 760; g['O'] = (ring(0, 0, w, H, S, C), w)
    w = 700; g['P'] = (U(box(0, 0, S, H), ring(0, H * 0.36, w, H, S, C * 0.72, ('tr', 'br'))), w)
    w = 760; g['Q'] = (U(ring(0, 0, w, H, S, C),
                         stroke((w * 0.6, S * 1.7), (w - S * 0.05, -S * 0.55), S, x_min=0, x_max=w + S, y_min=-S * 0.55)), w)
    w = 720; g['R'] = (U(box(0, 0, S, H), ring(0, H * 0.36, w, H, S, C * 0.72, ('tr', 'br')),
                         stroke((w * 0.40, H * 0.40), (w - S * 0.55, 0), S, x_min=S, x_max=w)), w)

    def s_shape(w, top_left_vertical=True):
        upper = box(0, M, S, H) if top_left_vertical else box(w - S, M, w, H)
        lower = box(w - S, 0, w, M) if top_left_vertical else box(0, 0, S, M)
        return U(box(0, H - S, w, H), upper, bar(0, w, M), lower, box(0, 0, w, S))

    w = 700; sg = s_shape(w)
    sg = cut(sg, 0, H, C * 0.85, 'tl'); sg = cut(sg, w, 0, C * 0.85, 'br')
    sg = cut(sg, w, M + S / 2, C * 0.5, 'tr'); sg = cut(sg, 0, M - S / 2, C * 0.5, 'bl')
    g['S'] = (sg, w)
    w = 700; g['T'] = (U(box(0, H - S, w, H), box(w / 2 - S / 2, 0, w / 2 + S / 2, H)), w)
    w = 720; g['U'] = (ring(0, 0, w, H + S + 2, S, C, ('bl', 'br')).intersection(box(-1, 0, w + 1, H)), w)
    w = 780; g['V'] = (U(stroke((S * 0.55, H), (w / 2, 0), S, x_min=0, x_max=w / 2),
                         stroke((w / 2, 0), (w - S * 0.55, H), S, x_min=w / 2, x_max=w)), w)
    w = 1040; pts = [(S * 0.55, H), (w * 0.26, 0), (w * 0.5, H * 0.66), (w * 0.74, 0), (w - S * 0.55, H)]
    cuts = [0, pts[1][0], pts[2][0], pts[3][0], w]
    g['W'] = (U(*[stroke(pts[i], pts[i + 1], S, x_min=cuts[i], x_max=cuts[i + 1]) for i in range(4)]), w)
    w = 760; g['X'] = (U(stroke((S * 0.55, H), (w - S * 0.55, 0), S, x_min=0, x_max=w),
                         stroke((S * 0.55, 0), (w - S * 0.55, H), S, x_min=0, x_max=w)), w)
    w = 740; g['Y'] = (U(stroke((S * 0.55, H), (w / 2, M * 0.98), S, x_min=0, x_max=w / 2, y_min=M * 0.7),
                         stroke((w - S * 0.55, H), (w / 2, M * 0.98), S, x_min=w / 2, x_max=w, y_min=M * 0.7),
                         box(w / 2 - S / 2, 0, w / 2 + S / 2, M * 0.98)), w)
    w = 700; g['Z'] = (U(box(0, H - S, w, H), box(0, 0, w, S),
                         stroke((w - S * 0.6, H - S * 0.5), (S * 0.6, S * 0.5), S, x_min=0, x_max=w)), w)

    # ----- figures (tabular 620)
    w = 620
    zero = U(ring(0, 0, w, H, S, C * 0.9), box(w / 2 - S * 0.45, M - S * 0.45, w / 2 + S * 0.45, M + S * 0.45))
    g['zero'] = (zero, w)
    one = U(box(w * 0.56 - S / 2, 0, w * 0.56 + S / 2, H), box(w * 0.18, H - S, w * 0.56, H))
    g['one'] = (cut(one, w * 0.18, H, S * 0.7, 'tl'), w)
    two = U(box(0, H - S, w, H), box(w - S, M, w, H), bar(0, w, M), box(0, 0, S, M), box(0, 0, w, S))
    two = cut(two, w, H, C * 0.8, 'tr'); two = cut(two, w, M - S / 2, C * 0.5, 'br'); two = cut(two, 0, M + S / 2, C * 0.5, 'tl')
    g['two'] = (two, w)
    three = U(box(0, H - S, w, H), bar(w * 0.26, w, M), box(0, 0, w, S), box(w - S, 0, w, H))
    g['three'] = (cut(cut(three, w, H, C * 0.8, 'tr'), w, 0, C * 0.8, 'br'), w)
    four = U(box(0, H * 0.30, S, H), box(0, H * 0.30, w, H * 0.30 + S), box(w * 0.64, 0, w * 0.64 + S, H * 0.74))
    g['four'] = (four, w)
    five = U(box(0, H - S, w, H), box(0, M, S, H), bar(0, w, M), box(w - S, 0, w, M), box(0, 0, w, S))
    five = cut(cut(five, w, 0, C * 0.8, 'br'), w, M + S / 2, C * 0.5, 'tr')
    g['five'] = (five, w)
    six = U(box(0, 0, S, H), box(0, H - S, w, H), bar(0, w, M), box(w - S, 0, w, M), box(0, 0, w, S))
    for x, y, c, q in [(0, H, C * 0.8, 'tl'), (0, 0, C * 0.8, 'bl'), (w, 0, C * 0.8, 'br'), (w, M + S / 2, C * 0.5, 'tr')]:
        six = cut(six, x, y, c, q)
    g['six'] = (six, w)
    g['seven'] = (U(box(0, H - S, w, H), stroke((w - S * 0.6, H - S * 0.5), (w * 0.26, 0), S, x_min=0, x_max=w)), w)
    eight = U(ring(w * 0.05, M - S / 2, w * 0.95, H, S, Ch), ring(0, 0, w, M + S / 2, S, Ch))
    g['eight'] = (eight, w)
    nine = U(box(w - S, 0, w, H), box(0, H - S, w, H), box(0, M, S, H), bar(0, w, M), box(0, 0, w, S))
    for x, y, c, q in [(0, H, C * 0.8, 'tl'), (w, H, C * 0.8, 'tr'), (w, 0, C * 0.8, 'br'), (0, M - S / 2, C * 0.5, 'bl')]:
        nine = cut(nine, x, y, c, q)
    g['nine'] = (nine, w)

    # ----- punctuation
    g['period'] = (box(0, 0, S, S), S)
    g['comma'] = (U(box(0, 0, S, S), Polygon([(0, 0), (S, 0), (S * 0.25, -S * 0.9), (0, -S * 0.9)])), S)
    g['colon'] = (U(box(0, 0, S, S), box(0, H * 0.52, S, H * 0.52 + S)), S)
    g['hyphen'] = (bar(0, 380, M), 380)
    g['endash'] = (bar(0, 560, M), 560)
    g['periodcentered'] = (box(0, M - S / 2, S, M + S / 2), S)
    g['slash'] = (stroke((S * 0.5, 0), (460 - S * 0.5, H), S, x_min=0, x_max=460), 460)
    g['plus'] = (U(bar(0, 560, M), box(280 - S / 2, M - 280 + S / 2, 280 + S / 2, M + 280 - S / 2)), 560)
    g['exclam'] = (U(box(0, S * 1.7, S, H), box(0, 0, S, S)), S)
    g['ampersand'] = None  # intentionally not drawn
    return {k: v for k, v in g.items() if v is not None}


NAMES = {c: c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
NAMES.update({'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six',
              '7': 'seven', '8': 'eight', '9': 'nine', '.': 'period', ',': 'comma', ':': 'colon',
              '-': 'hyphen', '–': 'endash', '·': 'periodcentered', '/': 'slash', '+': 'plus',
              '!': 'exclam'})


def draw(geom, pen):
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    for p in polys:
        if p.is_empty or p.area < 4:
            continue
        p = orient(p.simplify(0.5), sign=-1.0)  # TrueType: outer contours clockwise
        for ring_ in [p.exterior] + list(p.interiors):
            pts = [(round(x), round(y)) for x, y in list(ring_.coords)[:-1]]
            clean = [pt for i, pt in enumerate(pts) if pt != pts[i - 1]]
            if len(clean) < 3:
                continue
            pen.moveTo(clean[0])
            for pt in clean[1:]:
                pen.lineTo(pt)
            pen.closePath()


def build(style, S, out_dir):
    sb = round(46 + S * 0.22)                 # side bearing
    gl = glyphs(S)
    order = ['.notdef', 'space'] + list(gl)
    pen_glyphs, metrics = {}, {}

    pen = TTGlyphPen(None)
    draw(box(50, 0, 550, H).difference(box(100, 50, 500, H - 50)), pen)
    pen_glyphs['.notdef'] = pen.glyph(); metrics['.notdef'] = (600, 50)
    pen_glyphs['space'] = TTGlyphPen(None).glyph(); metrics['space'] = (round(300 + S * 0.4), 0)

    for name, (geom, w) in gl.items():
        geom = translate(geom, sb, 0)
        pen = TTGlyphPen(None)
        draw(geom, pen)
        pen_glyphs[name] = pen.glyph()
        xmin = int(round(geom.bounds[0])) if not geom.is_empty else 0
        metrics[name] = (round(w + 2 * sb), xmin)

    cmap = {0x20: 'space', 0xA0: 'space'}
    for ch, name in NAMES.items():
        if name in gl:
            cmap[ord(ch)] = name
            if ch.isalpha():
                cmap[ord(ch.lower())] = name

    ps = 'MinhasDisplay-' + style
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(pen_glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-250)
    fb.setupNameTable({'familyName': FAMILY, 'styleName': style, 'uniqueFontIdentifier': ps + ';' + VERSION,
                       'fullName': FAMILY + ' ' + style, 'psName': ps, 'version': 'Version ' + VERSION,
                       'copyright': 'Copyright 2026 Hammad Minhas', 'designer': 'Hammad Minhas'})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, sTypoLineGap=0, usWinAscent=900, usWinDescent=250,
                sxHeight=H, sCapHeight=H, usWeightClass=700 if style == 'Bold' else 300,
                achVendID='HMNS', fsType=0)
    fb.setupPost()
    path = os.path.join(out_dir, ps + '.ttf')
    fb.save(path)
    print('wrote', os.path.basename(path), '%d glyphs' % len(order))
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(path); f.flavor = 'woff2'; f.save(os.path.join(out_dir, ps + '.woff2'))
    except Exception as e:  # brotli missing
        print('woff2 skipped:', e)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(out, exist_ok=True)
    build('Bold', 150, out)
    build('Light', 56, out)
