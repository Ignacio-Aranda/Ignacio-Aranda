"""
Cabecera del perfil (banner-light.svg / banner-dark.svg).
El texto se convierte a trazos: GitHub muestra los SVG como <img> y no carga fuentes.
Uso: python3 tools/banner.py   (hace falta pip install fonttools brotli)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgtext import Font

FD = os.path.join(HERE, "fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets")

THEMES = { # Paleta de Colores
    "dark": dict(bg="#0E0B15", edge="#2A2338", ink="#F4F1FA", muted="#A79FB8",
                 dim="#544B66", hex="#7E7592", accent="#9B6BFF", logo="#8752F3",
                 logo_edge="#0E0B15", pill_bg="#1A1426", rule="#251E33", dot="#1C1628"),
    "light": dict(bg="#FBFAFE", edge="#E6E0F1", ink="#16111F", muted="#5F586E",
                  dim="#B3ABC2", hex="#857D95", accent="#6D35E0", logo="#8752F3",
                  logo_edge="#16111F", pill_bg="#F2EDFC", rule="#ECE6F6", dot="#EEE9F6"),
}

W, H = 960, 352
PHRASE = "{IA} abro cosas, las entiendo y monto otras."


def build(theme):
    t = THEMES[theme]
    anton = Font(f"{FD}/anton-latin-400-normal.woff2", "a")
    grot = Font(f"{FD}/space-grotesk-latin-700-normal.woff2", "g")
    mono = Font(f"{FD}/jetbrains-mono-latin-400-normal.woff2", "m")
    monob = Font(f"{FD}/jetbrains-mono-latin-700-normal.woff2", "b")

    body = []
    # fondo de la tarjeta y textura de puntos encima
    body.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{t["bg"]}" stroke="{t["edge"]}" stroke-width="2"/>')
    body.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#dots)"/>')

    # logo {IA} (igual que el avatar: morado y con un contorno grueso)
    lx, ly, ls = 52, 184, 146
    body.append(anton.outline("{IA}", lx, ly, ls,
                              attrs=f'fill="{t["logo"]}" stroke="{t["logo_edge"]}" stroke-width="70" '
                                    f'stroke-linejoin="round" paint-order="stroke"', tracking=4))
    logo_w = anton.width("{IA}", ls, 4)

    # nombre y rol
    nx = lx + logo_w + 52
    body.append(f'<rect x="{nx - 24}" y="58" width="2" height="132" fill="{t["rule"]}"/>')
    body.append(mono.text("~/ignacio-aranda $ whoami", nx, 82, 17, "dim"))
    body.append(grot.text("Ignacio Aranda", nx, 146, 64, "ink", tracking=-1.2))
    body.append(mono.text("Ingeniero en ciberseguridad e IA · Málaga", nx, 184, 19, "muted"))

    # cápsulas
    px, py = nx, 202
    for label in ["ciberseguridad", "ingeniería inversa", "maker"]:
        w = mono.width(label, 15) + 30
        body.append(f'<rect x="{px}" y="{py}" width="{w:.1f}" height="30" rx="15" fill="{t["pill_bg"]}" stroke="{t["accent"]}" stroke-opacity=".55"/>')
        body.append(mono.text(label, px + 15, py + 20, 15, "acc"))
        px += w + 10

    # franja del hexdump
    hy = 262
    body.append(f'<rect x="32" y="{hy - 14}" width="{W - 64}" height="1.5" fill="{t["rule"]}"/>')
    data = PHRASE.encode()
    size = 18
    cw = mono.width("0", size)
    row_h = 27
    rows = [data[i:i + 16] for i in range(0, len(data), 16)]
    ox = 52
    hex_x = ox + cw * 10
    asc_x = hex_x + cw * (16 * 3 + 2)
    # solo se enseñan 3 filas para que la franja sea compacta; la última lleva el cursor
    for r, chunk in enumerate(rows[:4]):
        y = hy + 12 + r * row_h
        if r == 3:
            break
        body.append(mono.text(f"{r*16:08x}", ox, y, size, "dim"))
        for i, byte in enumerate(chunk):
            x = hex_x + cw * (i * 3 + (1 if i >= 8 else 0))
            cls = "accb" if (r == 0 and i < 4) else "hex"
            f = monob if cls == "accb" else mono
            body.append(f.text(f"{byte:02x}", x, y, size, cls))
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        body.append(mono.text("|", asc_x - cw, y, size, "dim"))
        if r == 0:
            body.append(monob.text(asc[:4], asc_x, y, size, "accb"))
            body.append(mono.text(asc[4:], asc_x + cw * 4, y, size, "ink"))
        else:
            body.append(mono.text(asc, asc_x, y, size, "ink"))
        body.append(mono.text("|", asc_x + cw * 16, y, size, "dim"))
    return t, body, [anton, grot, mono, monob], (asc_x, hy, cw, row_h, rows)


def render(theme):
    t, body, fonts, (asc_x, hy, cw, row_h, rows) = build(theme)
    # cursor parpadeante justo después del texto (final de la fila 3)
    shown = rows[:3]
    last = shown[-1]
    cx = asc_x + cw * len(last)
    cy = hy + 12 + 2 * row_h
    # si la fila está llena, el cursor va detrás de la barra de cierre
    if len(last) == 16:
        cx = asc_x + cw * 17.4
    body.append(f'<rect class="cur" x="{cx + 3:.1f}" y="{cy - 16}" width="{cw * 0.62:.1f}" height="21" fill="{t["accent"]}"/>')

    defs = "".join(f.defs() for f in fonts)
    css = (f'.ink{{fill:{t["ink"]}}}.muted{{fill:{t["muted"]}}}.dim{{fill:{t["dim"]}}}'
           f'.hex{{fill:{t["hex"]}}}.acc{{fill:{t["accent"]}}}.accb{{fill:{t["accent"]}}}'
           '.cur{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}'
           '@media (prefers-reduced-motion:reduce){.cur{animation:none}}')
    pattern = (f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
               f'<circle cx="2" cy="2" r="1.3" fill="{t["dot"]}"/></pattern>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'role="img" aria-label="{{IA}} Ignacio Aranda — Ingeniero en ciberseguridad e IA, Málaga">'
           f'<title>Ignacio Aranda</title><style>{css}</style><defs>{pattern}{defs}</defs>'
           + "".join(body) + "</svg>")
    path = f"{OUT}/banner-{theme}.svg"
    with open(path, "w") as fh:
        fh.write(svg)
    print(path, len(svg) // 1024, "KB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for th in THEMES:
        render(th)