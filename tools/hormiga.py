"""
La hormiga real de Ant Farm Idle (mismo dibujo, en morado {IA}) cruzando el README.
Uso: ANT_FARM=~/ruta/Ant-Farm-Idle python3 tools/hormiga.py   (hace falta pygame)
"""
import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("ANT_FARM", os.path.join(HERE, "..", "..", "Ant-Farm-Idle")))
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from pixel import hormiga_arte as H
from pixel.base import CLAVE

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "hormiga.svg")
PX = 3                     # tamaño de cada píxel en el SVG
W, HGT = 960, 72
MORADO = (135, 82, 243)

frames = H.fotogramas(MORADO)


def rects(surf):
    out = []
    w, h = surf.get_size()
    for y in range(h):
        x = 0
        while x < w:
            c = surf.get_at((x, y))[:3]
            if c == CLAVE:
                x += 1
                continue
            run = 1
            while x + run < w and surf.get_at((x + run, y))[:3] == c:
                run += 1
            out.append(f'<rect x="{x*PX}" y="{y*PX}" width="{run*PX}" height="{PX}" fill="#{c[0]:02x}{c[1]:02x}{c[2]:02x}"/>')
            x += run
    return "".join(out)


ant_h = H.ALTO * PX
ground_y = HGT - 12
groups = "".join(
    f'<g class="f f{i}">{rects(frames[(1, i)])}</g>' for i in range(4)
)

# tierra en píxeles, con algo de variación (igual que en el hormiguero)
random.seed(27)
soil = []
browns = ["#8a6a4a", "#7a5c3f", "#9a7856", "#6d5138"]
for x in range(0, W, PX):
    soil.append(f'<rect x="{x}" y="{ground_y}" width="{PX}" height="{PX}" fill="{random.choice(browns)}"/>')
    if random.random() < .45:
        soil.append(f'<rect x="{x}" y="{ground_y+PX}" width="{PX}" height="{PX}" fill="{random.choice(browns)}" opacity=".6"/>')
    if random.random() < .12:
        soil.append(f'<rect x="{x}" y="{ground_y+2*PX}" width="{PX}" height="{PX}" fill="{random.choice(browns)}" opacity=".35"/>')
# la hierba
for x in random.sample(range(0, W, PX * 4), 18):
    h = random.choice([1, 2, 2, 3])
    for k in range(h):
        soil.append(f'<rect x="{x}" y="{ground_y - (k+1)*PX}" width="{PX}" height="{PX}" fill="#5f8f3e"/>')

dur = 16  # segundos en cruzar
css = (
    f".walk{{animation:walk {dur}s linear infinite}}"
    f"@keyframes walk{{from{{transform:translateX(-{H.ANCHO*PX+10}px)}}to{{transform:translateX({W+10}px)}}}}"
    ".f{opacity:0;animation:leg .48s steps(1,end) infinite}"
    "@keyframes leg{0%{opacity:1}25%{opacity:0}100%{opacity:0}}"
    + "".join(f".f{i}{{animation-delay:-{((4-i)%4)*0.12:.2f}s}}" for i in range(4))
    + "@media (prefers-reduced-motion:reduce){.walk{animation:none;transform:translateX(440px)}"
      ".f{animation:none}.f1{opacity:1}}"
)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {HGT}" width="{W}" height="{HGT}" '
       f'role="img" aria-label="Una hormiga de Ant Farm Idle cruzando la pantalla">'
       f'<style>{css}</style>'
       + "".join(soil)
       + f'<g class="walk"><g transform="translate(0 {ground_y - ant_h})" shape-rendering="crispEdges">{groups}</g></g>'
       + "</svg>")
with open(OUT, "w") as fh:
    fh.write(svg)
print(OUT, len(svg) // 1024, "KB")
