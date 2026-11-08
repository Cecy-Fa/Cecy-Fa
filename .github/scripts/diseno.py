"""
Dibuja las imágenes del perfil (assets/*.svg) a partir de perfil.json.
La GitHub Action "Actualizar diseño" lo ejecuta cada vez que se modifica perfil.json.
Prueba local:  python3 .github/scripts/diseno.py
"""
import json
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "assets"
FONT = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"

try:
    CFG = json.loads((RAIZ / "perfil.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    sys.exit(f"perfil.json tiene un error de formato en la línea {e.lineno}, columna {e.colno}: "
             "revisá que no falte una coma o unas comillas.")

_col = CFG.get("colores", {})
C = dict(bg=_col.get("fondo", "#171323"), morado=_col.get("morado_oscuro", "#542783"),
         violetaP=_col.get("violeta_profundo", "#7136B5"), purpura=_col.get("purpura", "#9635D6"),
         violeta=_col.get("violeta_brillante", "#B44AFF"), magenta=_col.get("magenta", "#D946EF"),
         fucsia=_col.get("fucsia", "#F052B5"), rosaV=_col.get("rosa_vibrante", "#FF80BF"),
         pastel=_col.get("rosa_pastel", "#FFB3D9"), blanco=_col.get("blanco", "#FFF5FB"))


def e(t):
    return escape(str(t), quote=False)


def fit(text, size, max_w, k=0.6):
    """Achica la letra si el texto no entra en max_w píxeles."""
    return round(min(size, max_w / max(1, len(text) * k)), 1)

def defs(u):
    return f"""<defs>
  <linearGradient id="edge{u}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{C['rosaV']}"/><stop offset=".5" stop-color="{C['magenta']}"/><stop offset="1" stop-color="{C['violetaP']}"/>
  </linearGradient>
  <linearGradient id="txt{u}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['rosaV']}"/><stop offset=".55" stop-color="{C['magenta']}"/><stop offset="1" stop-color="{C['violeta']}"/>
  </linearGradient>
  <radialGradient id="panel{u}" cx="50%" cy="50%" r="75%">
    <stop offset="0" stop-color="#3A1A55"/><stop offset=".6" stop-color="#22163A"/><stop offset="1" stop-color="{C['bg']}"/>
  </radialGradient>
  <filter id="glow{u}" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="halo{u}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>
</defs>"""


def svg(w, h, u, body, r=18):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">'
            f'{defs(u)}<rect x="3" y="3" width="{w-6}" height="{h-6}" rx="{r}" fill="url(#panel{u})"/>{body}'
            f'<rect x="3" y="3" width="{w-6}" height="{h-6}" rx="{r}" fill="none" stroke="url(#edge{u})" stroke-width="2.5" filter="url(#glow{u})"/>'
            f'</svg>\n')


def lines(ls, x, y, size, color, lh=1.45, anchor="start", weight=400):
    t = f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">'
    for i, l in enumerate(ls):
        t += f'<tspan x="{x}" dy="{0 if i == 0 else round(size*lh, 1)}">{e(l)}</tspan>'
    return t + "</text>"


def neon_btn(x, y, label, u, w=104, h=38):
    return (f'<g transform="translate({x} {y})"><rect width="{w}" height="{h}" rx="8" fill="{C["bg"]}" fill-opacity=".55" '
            f'stroke="{C["fucsia"]}" stroke-width="1.8" filter="url(#glow{u})"/>'
            f'<text x="{w/2}" y="{h/2+6}" font-size="{fit(label, 16, w-16, .58)}" fill="{C["blanco"]}" text-anchor="middle" font-weight="600">{e(label)}</text></g>')


# ───────── iconos grandes (trazo neón) ─────────
def ic_gamepad(c, c2):
    return (f'<path d="M-50 -10 Q-50 -30 -30 -30 H30 Q50 -30 50 -10 L58 25 Q62 42 46 42 Q36 42 28 28 H-28 Q-36 42 -46 42 Q-62 42 -58 25 Z" '
            f'fill="none" stroke="{c}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M-34 -2 H-18 M-26 -10 V6" stroke="{c2}" stroke-width="5" stroke-linecap="round"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{c2}"/>' for x, y in [(26, -12), (36, -2), (26, 8), (16, -2)]))


def ic_palette(c, c2):
    return (f'<path d="M0 -42 C36 -42 54 -16 48 6 C43 24 22 16 15 27 C8 38 22 46 0 46 C-32 46 -52 22 -52 0 C-52 -25 -29 -42 0 -42Z" '
            f'fill="none" stroke="{c}" stroke-width="4"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="{col}"/>' for x, y, col in
                      [(-28, 4, C['rosaV']), (-20, -20, C['magenta']), (4, -26, C['violeta']), (26, -12, c2)]))


def ic_browser(c, c2):
    return (f'<rect x="-55" y="-40" width="110" height="82" rx="10" fill="none" stroke="{c}" stroke-width="4"/>'
            f'<path d="M-55 -20 H55" stroke="{c}" stroke-width="3"/>'
            + "".join(f'<circle cx="{x}" cy="-30" r="3.5" fill="{c2}"/>' for x in (-42, -31, -20))
            + f'<path d="M-14 0 L-28 12 L-14 24 M14 0 L28 12 L14 24 M5 -4 L-5 28" fill="none" stroke="{c2}" stroke-width="4" '
              f'stroke-linecap="round" stroke-linejoin="round"/>')


def ic_bulb(c, c2):
    return (f'<path d="M-24 6 A32 32 0 1 1 24 6 C16 15 13 20 13 28 H-13 C-13 20 -16 15 -24 6Z" fill="none" stroke="{c}" '
            f'stroke-width="4" stroke-linejoin="round"/><path d="M-11 36 H11 M-7 44 H7" stroke="{c}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M-8 -6 L0 6 L8 -6" fill="none" stroke="{c2}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
            + "".join(f'<path d="{d}" stroke="{c2}" stroke-width="3.5" stroke-linecap="round"/>' for d in
                      ["M-52 -22 L-42 -18", "M52 -22 L42 -18", "M0 -64 V-54", "M-38 -52 L-31 -44", "M38 -52 L31 -44"]))


def big_icon(fn, x, y, u, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle r="58" fill="{C["fucsia"]}" opacity=".18" filter="url(#halo{u})"/>'
            f'<g filter="url(#glow{u})">{fn(C["fucsia"], C["pastel"])}</g></g>')


# ───────── botones superiores ─────────
SMALL = {
    "linkedin": lambda c: f'<rect x="-11" y="-11" width="22" height="22" rx="4" fill="none" stroke="{c}" stroke-width="2"/><text y="6" font-size="14" font-weight="700" fill="{c}" text-anchor="middle">in</text>',
    "email": lambda c: f'<rect x="-12" y="-8" width="24" height="16" rx="3" fill="none" stroke="{c}" stroke-width="2"/><path d="M-11 -6 L0 3 L11 -6" fill="none" stroke="{c}" stroke-width="2"/>',
    "portfolio": lambda c: f'<circle r="11" fill="none" stroke="{c}" stroke-width="2"/><ellipse rx="5" ry="11" fill="none" stroke="{c}" stroke-width="1.6"/><path d="M-11 0H11" stroke="{c}" stroke-width="1.6"/>',
    "proyectos": lambda c: f'<path d="M-12 -8H-3L0 -5H12V10H-12Z" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>',
}


def top_button(key, label, w=150, h=58):
    u = "b" + key
    body = (f'<g transform="translate(32 {h/2})" filter="url(#glow{u})">{SMALL[key](C["fucsia"])}</g>'
            f'<text x="54" y="{h/2+6}" font-size="{fit(label, 17, 86, .6)}" font-weight="600" fill="{C["blanco"]}">{e(label)}</text>')
    return svg(w, h, u, body, r=12)


def top_logo(text, w=150, h=58):
    u = "blogo"
    size = fit(text, 26, 110, .66)
    body = (f'<circle cx="{w/2}" cy="{h/2}" r="24" fill="{C["fucsia"]}" opacity=".35" filter="url(#halo{u})"/>'
            f'<text x="{w/2}" y="{h/2+size*.35:.1f}" font-size="{size}" font-weight="800" fill="url(#txt{u})" text-anchor="middle" filter="url(#glow{u})">{e(text)}</text>')
    return svg(w, h, u, body, r=12)


# ───────── banner ─────────
def split_name(name, max_w=290):
    """Una línea si entra; si no, se parte en dos (ej.: Cecilia / Farias)."""
    if len(name) * 70 * .62 <= max_w:
        return [name], 70
    words = name.split()
    if len(words) == 1:
        return [name], fit(name, 70, max_w, .62)
    best = min(range(1, len(words)), key=lambda i: max(len(" ".join(words[:i])), len(" ".join(words[i:]))))
    ls = [" ".join(words[:best]), " ".join(words[best:])]
    return ls, fit(max(ls, key=len), 64, max_w, .62)


def hero(b, w=830, h=340):
    u = "hero"
    bx, by = 600, 92
    code = "".join(
        f'<rect x="{bx+18+ind}" y="{by+48+i*20}" width="{ln}" height="8" rx="4" fill="{col}"/>'
        for i, (ind, ln, col) in enumerate([(0, 70, C['fucsia']), (16, 110, C['magenta']), (16, 80, C['violeta']),
                                            (32, 90, C['rosaV']), (16, 60, C['purpura']), (0, 40, C['fucsia'])]))
    star = "M0 -10 L3 -3 L10 0 L3 3 L0 10 L-3 3 L-10 0 L-3 -3Z"

    # texto de la izquierda (posiciones calculadas según cuántas líneas ocupa el nombre)
    name_lines, ns = split_name(b.get("nombre", ""))
    y = 96 if len(name_lines) == 1 else 70
    left = f'<text x="42" y="{y}" font-size="15" letter-spacing="4" font-weight="700" fill="{C["violeta"]}">{e(b.get("saludo", ""))}</text>'
    y += ns * .92 + 4
    for ln in name_lines:
        left += f'<text x="38" y="{y:.0f}" font-size="{ns}" font-weight="800" fill="url(#txt{u})" filter="url(#glow{u})">{e(ln)}</text>'
        y += ns * .9
    y += 40 - ns * .9
    rol = b.get("rol", "")
    left += f'<text x="42" y="{y:.0f}" font-size="{fit(rol, 21, 300, .58)}" font-weight="700" fill="{C["blanco"]}">{e(rol)}</text>'
    left += f'<rect x="42" y="{y+16:.0f}" width="70" height="4" rx="2" fill="url(#txt{u})"/>'
    extra = b.get("lineas", [])
    ls = fit(max(extra, key=len) if extra else "", 15, 320, .52)
    left += lines(extra, 42, round(y + 50), ls, C['pastel'], lh=1.6)

    # globo de diálogo
    g = b.get("globo", [])
    gs = fit(max(g, key=len) if g else "", 15, 200, .52)
    gh = round(30 + gs * 1.3 * max(0, len(g) - 1) + 22)
    bubble = (f'<g transform="translate(345 38)">'
              f'<rect width="225" height="{gh}" rx="22" fill="{C["bg"]}" stroke="{C["fucsia"]}" stroke-width="2.5" filter="url(#glow{u})"/>'
              f'<path d="M170 {gh-1} L214 {gh+26} L194 {gh-1}" fill="{C["bg"]}" stroke="{C["fucsia"]}" stroke-width="2.5" stroke-linejoin="round"/>'
              f'<rect x="168" y="{gh-6}" width="28" height="7" fill="{C["bg"]}"/>'
              f'{lines(g, 112, 30, gs, C["blanco"], lh=1.3, anchor="middle")}</g>') if g else ""

    body = f"""
<circle cx="690" cy="200" r="130" fill="{C['magenta']}" opacity=".22" filter="url(#halo{u})"/>
<g filter="url(#glow{u})">
  <rect x="{bx}" y="{by}" width="190" height="160" rx="12" fill="{C['bg']}" stroke="url(#edge{u})" stroke-width="3"/>
  <path d="M{bx} {by+28} H{bx+190}" stroke="{C['magenta']}" stroke-width="2"/>
  <circle cx="{bx+16}" cy="{by+14}" r="4" fill="{C['rosaV']}"/><circle cx="{bx+30}" cy="{by+14}" r="4" fill="{C['magenta']}"/><circle cx="{bx+44}" cy="{by+14}" r="4" fill="{C['violeta']}"/>
</g>
{code}
<rect x="{bx+60}" y="{by+168}" width="8" height="18" fill="{C['fucsia']}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>
<g transform="translate(615 268) scale(.85) rotate(-12)">
  <path d="M-50 -10 Q-50 -30 -30 -30 H30 Q50 -30 50 -10 L58 25 Q62 42 46 42 Q36 42 28 28 H-28 Q-36 42 -46 42 Q-62 42 -58 25 Z" fill="{C['bg']}"/>
  <g filter="url(#glow{u})">{ic_gamepad(C['fucsia'], C['pastel'])}</g>
</g>
<g transform="translate(780 70)" fill="{C['pastel']}"><path d="{star}"><animate attributeName="opacity" values="1;.2;1" dur="2.4s" repeatCount="indefinite"/></path></g>
<g transform="translate(578 120) scale(.6)" fill="{C['violeta']}"><path d="{star}"><animate attributeName="opacity" values=".2;1;.2" dur="2s" repeatCount="indefinite"/></path></g>
{bubble}
{left}"""
    return svg(w, h, u, body)


# ───────── cuadrícula con círculo central ─────────
def grid(g, w=830, h=620):
    u = "grid"
    cx, cy, R = w / 2, h / 2, 148

    def title(t, x, y, anchor="start"):
        return (f'<text x="{x}" y="{y}" font-size="{fit(t, 28, 250, .6)}" font-weight="700" fill="{C["blanco"]}" '
                f'text-anchor="{anchor}">{e(t)}</text>')

    def txt(ls, x, y, anchor="start"):
        return lines(ls, x, y, fit(max(ls, key=len) if ls else "", 15, 230, .52), C['pastel'], anchor=anchor)

    q1, q2 = g.get("arriba_izquierda", {}), g.get("arriba_derecha", {})
    q3, q4 = g.get("abajo_izquierda", {}), g.get("abajo_derecha", {})
    q = [
        title(q1.get("titulo", ""), 34, 66) + txt(q1.get("texto", []), 34, 100)
        + neon_btn(290, 34, q1.get("boton", ""), u) + big_icon(ic_gamepad, 100, 228, u),
        title(q2.get("titulo", ""), w-34, 66, "end") + txt(q2.get("texto", []), w-34, 100, "end")
        + neon_btn(w-394, 34, q2.get("boton", ""), u) + big_icon(ic_palette, w-100, 228, u),
        title(q3.get("titulo", ""), 34, cy+66) + txt(q3.get("texto", []), 34, cy+100)
        + big_icon(ic_browser, 100, cy+212, u) + neon_btn(232, h-62, q3.get("boton", ""), u),
        title(q4.get("titulo", ""), w-34, cy+66, "end") + txt(q4.get("texto", []), w-34, cy+100, "end")
        + big_icon(ic_bulb, w-100, cy+216, u) + neon_btn(w-336, h-62, q4.get("boton", ""), u),
    ]
    centro = g.get("centro", {})
    letras = centro.get("letras", "")
    ls = 104 if len(letras) <= 1 else fit(letras, 92, 190, .68)
    arriba = centro.get("texto_arriba", "")
    asz = fit(arriba, 11, 190, .62 + 3 / 11)

    body = f"""
<path d="M{cx} 3 V{h-3} M3 {cy} H{w-3}" stroke="{C['magenta']}" stroke-width="1.5" opacity=".55"/>
{''.join(q)}
<circle cx="{cx}" cy="{cy}" r="{R+40}" fill="{C['fucsia']}" opacity=".28" filter="url(#halo{u})"/>
<circle cx="{cx}" cy="{cy}" r="{R}" fill="{C['bg']}"/>
<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="url(#edge{u})" stroke-width="4" filter="url(#glow{u})"/>
<circle cx="{cx}" cy="{cy}" r="{R-16}" fill="none" stroke="{C['magenta']}" stroke-width="1.2" opacity=".6"/>
<circle cx="{cx}" cy="{cy}" r="{R-30}" fill="none" stroke="{C['violeta']}" stroke-width="1.5" stroke-dasharray="2 9" opacity=".8">
  <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="30s" repeatCount="indefinite"/>
</circle>
<g>
  <circle cx="{cx}" cy="{cy-R+16}" r="5" fill="{C['pastel']}" filter="url(#glow{u})"/>
  <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="-360 {cx} {cy}" dur="12s" repeatCount="indefinite"/>
</g>
<text x="{cx}" y="{cy+ls*.3:.0f}" font-size="{ls}" font-weight="800" fill="url(#txt{u})" text-anchor="middle" filter="url(#glow{u})">{e(letras)}</text>
<text x="{cx}" y="{cy+66}" font-size="22" font-weight="700" fill="{C['pastel']}" text-anchor="middle" letter-spacing="2">{e(centro.get("texto_abajo", ""))}</text>
<text x="{cx}" y="{cy-62}" font-size="{asz}" font-weight="700" fill="{C['violeta']}" text-anchor="middle" letter-spacing="3">{e(arriba)}</text>"""
    return svg(w, h, u, body)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    bt = CFG.get("botones", {})
    files = {f"btn-{k}.svg": top_button(k, bt.get(k, k.capitalize())) for k in SMALL}
    files["logo.svg"] = top_logo(CFG.get("logo", ""))
    files["hero.svg"] = hero(CFG.get("banner", {}))
    files["grid.svg"] = grid(CFG.get("cuadricula", {}))
    for n, c in files.items():
        (OUT / n).write_text(c, encoding="utf-8")
    print("Imágenes generadas:", ", ".join(files))

