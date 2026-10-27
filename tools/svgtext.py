"""
Compone texto con los contornos reales de la fuente para que los SVG
se vean igual en todas partes (GitHub sirve los SVG del README como <img>, que no puede
cargar fuentes web).
"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen


class Font:
    def __init__(self, path, key):
        self.f = TTFont(path)
        self.key = key
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]
        self.used = {}
        os2 = self.f["OS/2"]
        self.cap = getattr(os2, "sCapHeight", 0) or int(self.upm * 0.7)

    def gname(self, ch):
        return self.cmap.get(ord(ch), ".notdef")

    def adv(self, ch):
        return self.hmtx[self.gname(ch)][0]

    def width(self, text, size, tracking=0):
        s = size / self.upm
        return sum(self.adv(c) * s + tracking for c in text) - (tracking if text else 0)

    def gid(self, ch):
        g = self.gname(ch)
        ident = f"{self.key}{ord(ch):x}"
        if ident not in self.used:
            pen = SVGPathPen(self.gs) # Dibuja la letra
            self.gs[g].draw(pen)
            self.used[ident] = pen.getCommands() # Devuelve el path SVG
        return ident

    def text(self, text, x, y, size, cls="", tracking=0, anchor="start"):
        """Return an SVG group drawing `text` with baseline at y."""
        s = size / self.upm
        w = self.width(text, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        parts = []
        cx = 0.0
        for c in text:
            if c != " ":
                d = self.gid(c)
                if self.used[d]:
                    parts.append(f'<use href="#{d}" x="{cx:.0f}"/>')
            cx += self.adv(c) + tracking / s
        c_attr = f' class="{cls}"' if cls else ""
        return (f'<g{c_attr} transform="translate({x:.2f} {y:.2f}) scale({s:.5f} {-s:.5f})">'
                + "".join(parts) + "</g>")

    def outline(self, text, x, y, size, attrs="", tracking=0):
        """Single combined <path> (lets strokes and paint-order work on the whole word)."""
        s = size / self.upm
        cmds = []
        cx = 0.0
        for c in text:
            pen = SVGPathPen(self.gs)
            self.gs[self.gname(c)].draw(pen)
            d = pen.getCommands()
            if d:
                cmds.append(f'<path transform="translate({cx:.0f} 0)" d="{d}"/>')
            cx += self.adv(c) + tracking / s
        return (f'<g {attrs} transform="translate({x:.2f} {y:.2f}) scale({s:.5f} {-s:.5f})">'
                + "".join(cmds) + "</g>")

    def defs(self):
        return "".join(f'<path id="{k}" d="{d}"/>' for k, d in self.used.items() if d)
