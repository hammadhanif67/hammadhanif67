"""H logo concepts. Each function returns SVG markup on a 100x100 grid.
Pick one in build_static.py with MARK = '<name>'.
"""
W, R, K = '#f5f5f5', '#E30613', '#0b0b0b'


def grid():
    """01 Grid: the H built from a 3x3 module grid; the centre module is the red crossbar."""
    cells = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    out = ''.join(f'<rect x="{10 + c * 28}" y="{10 + r * 28}" width="24" height="24" fill="{W}"/>' for c, r in cells)
    return out + f'<rect x="38" y="38" width="24" height="24" fill="{R}"/>'


def tile():
    """02 Tile: a red chamfered tile with the H cut out of it."""
    return (f'<path fill="{R}" fill-rule="evenodd" d="M20 6H94V80L80 94H6V20Z '
            f'M28 24V76H40V56H60V76H72V24H60V44H40V24Z"/>')


def frame():
    """03 Frame: an H inside a chamfered octagon outline; red crossbar."""
    return (f'<path fill="none" stroke="{W}" stroke-width="4" d="M30 4H70L96 30V70L70 96H30L4 70V30Z"/>'
            f'<rect x="30" y="26" width="10" height="48" fill="{W}"/><rect x="60" y="26" width="10" height="48" fill="{W}"/>'
            f'<rect x="40" y="46" width="20" height="8" fill="{R}"/>')


def stencil():
    """04 Stencil: heavy stems split by a hairline gap, red bar across the gap."""
    return (f'<path fill="{W}" d="M10 10H38V44H10Z M10 56H38V90H10Z M62 10H90V44H62Z M62 56H90V90H62Z"/>'
            f'<rect x="10" y="46.5" width="80" height="7" fill="{R}"/>')


def slant():
    """05 Slant: italic parallelogram stems with a red bar; reads as speed and forward motion."""
    return (f'<path fill="{W}" d="M24 10H44L32 90H12Z M68 10H88L76 90H56Z"/>'
            f'<path fill="{R}" d="M32 42H74L71 58H29Z"/>')


def mono():
    """06 Monogram HM: the H's right stem doubles as the first stroke of an M."""
    return (f'<path fill="{W}" d="M6 14H20V86H6Z M38 14H52V86H38Z '
            f'M58 14H69L76 40L83 14H94V86H84V46L76 70L68 46V86H58Z"/>'
            f'<rect x="20" y="44" width="18" height="12" fill="{R}"/>')


CONCEPTS = [('01 GRID', grid), ('02 TILE', tile), ('03 FRAME', frame),
            ('04 STENCIL', stencil), ('05 SLANT', slant), ('06 HM MONOGRAM', mono)]


def place(name, x, y, size):
    fn = dict((n.split(' ', 1)[1].split()[0].lower(), f) for n, f in CONCEPTS)[name]
    return f'<g transform="translate({x} {y}) scale({size / 100:.4f})">{fn()}</g>'
