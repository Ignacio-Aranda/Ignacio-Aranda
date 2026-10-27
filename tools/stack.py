"""
Fila de herramientas (stack-light.svg / stack-dark.svg), mismo estilo que la cabecera.
Para cambiarla hay que editar ITEMS (slug de simple-icons, etiqueta) y copiar el icono a tools/icons/
(de simple-icons, CC0; impresion3d.svg es de Material Design Icons).
Hay que usar python3 tools/stack.py
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgtext import Font
from banner import THEMES, FD

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets")
SI = os.path.join(HERE, "icons")  # iconos de simple-icons (CC0); añade aquí el .svg de cada herramienta nueva
ITEMS = [("cplusplus", "C/C++"), ("python", "Python"), ("arduino", "Arduino"), ("espressif", "ESP32"),
         ("raspberrypi", "Raspberry Pi"), ("impresion3d", "Impresión 3D"), ("autodesk", "Fusion 360")]
PER_ROW = 4
W = 960
CH, GAP, ICON, PAD, FS = 44, 12, 20, 16, 17


def icon_path(slug):
    return re.search(r'<path d="([^"]+)"', open(f"{SI}/{slug}.svg").read()).group(1)


def render(theme):
    t = THEMES[theme]
    mono = Font(f"{FD}/jetbrains-mono-latin-500-normal.woff2", "m")
    rows = [ITEMS[i:i + PER_ROW] for i in range(0, len(ITEMS), PER_ROW)]
    body = []
    for r, row in enumerate(rows):
        widths = [PAD + ICON + 10 + mono.width(lbl, FS) + PAD for _, lbl in row]
        total = sum(widths) + GAP * (len(row) - 1)
        x = (W - total) / 2
        y = r * (CH + GAP) + 1
        for (slug, lbl), w in zip(row, widths):
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{CH}" rx="12" fill="{t["pill_bg"]}" stroke="{t["edge"]}" stroke-width="1.5"/>')
            s = ICON / 24
            body.append(f'<path transform="translate({x + PAD:.1f} {y + (CH - ICON) / 2:.1f}) scale({s:.4f})" d="{icon_path(slug)}" fill="{t["accent"]}"/>')
            body.append(mono.text(lbl, x + PAD + ICON + 10, y + CH / 2 + 6, FS, "ink"))
            x += w + GAP
    H = len(rows) * (CH + GAP) - GAP + 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="Herramientas: {", ".join(l for _, l in ITEMS)}"><style>.ink{{fill:{t["ink"]}}}</style>'
           f'<defs>{mono.defs()}</defs>' + "".join(body) + "</svg>")
    with open(f"{OUT}/stack-{theme}.svg", "w") as fh:
        fh.write(svg)
    print(theme, len(svg) // 1024, "KB")


for th in THEMES:
    render(th)
