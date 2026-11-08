"""
Genera assets/stats.svg con las estadísticas de GitHub de la usuaria,
en el estilo neón Aurora Bloom del perfil. Lo ejecuta la GitHub Action
"Actualizar estadísticas" (no depende de servicios externos).

Uso local de prueba:  python3 stats.py --demo
"""
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "assets" / "stats.svg"
FONT = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
C = dict(bg="#171323", violetaP="#7136B5", purpura="#9635D6", violeta="#B44AFF",
         magenta="#D946EF", fucsia="#F052B5", rosaV="#FF80BF", pastel="#FFB3D9", blanco="#FFF5FB")
try:  # usa los mismos colores que perfil.json
    _c = json.loads((OUT.parents[1] / "perfil.json").read_text(encoding="utf-8")).get("colores", {})
    C.update({k: _c[v] for k, v in dict(bg="fondo", violetaP="violeta_profundo", purpura="purpura",
              violeta="violeta_brillante", magenta="magenta", fucsia="fucsia", rosaV="rosa_vibrante",
              pastel="rosa_pastel", blanco="blanco").items() if v in _c})
except (OSError, ValueError):
    pass
LANG_COLORS = [C["fucsia"], C["magenta"], C["violeta"], C["rosaV"], C["purpura"], C["violetaP"]]

QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "perfil-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"Error de la API de GitHub: {data['errors']}")
    return data["data"]["user"]


def streaks(days):
    days = sorted(days, key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    today = date.today().isoformat()
    for d in reversed(days):
        if d["date"] == today and d["contributionCount"] == 0:
            continue  # hoy todavía puede sumar
        if d["contributionCount"] > 0:
            current += 1
        else:
            break
    return current, longest


def summarize(u):
    repos = u["repositories"]
    langs = defaultdict(int)
    for r in repos["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:6]
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, best = streaks(days)
    return dict(
        contrib=cc["contributionCalendar"]["totalContributions"],
        commits=cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        repos=repos["totalCount"],
        stars=sum(r["stargazerCount"] for r in repos["nodes"]),
        prs=u["pullRequests"]["totalCount"],
        issues=u["issues"]["totalCount"],
        streak=cur, best=best,
        langs=[(n, s / total * 100) for n, s in top],
    )


def fmt(v):
    return "—" if v is None else f"{v:,}".replace(",", ".")


def render(s):
    w, h = 830, 290
    tiles = [("Aportes del año", s["contrib"]), ("Commits del año", s["commits"]),
             ("Repositorios", s["repos"]), ("Estrellas", s["stars"]),
             ("Pull requests", s["prs"]), ("Issues", s["issues"])]
    t = ""
    for i, (label, val) in enumerate(tiles):
        x, y = 28 + (i % 2) * 146, 30 + (i // 2) * 80
        t += (f'<g transform="translate({x} {y})"><rect width="134" height="68" rx="12" fill="{C["bg"]}" fill-opacity=".6" '
              f'stroke="{C["magenta"]}" stroke-opacity=".55" stroke-width="1.3"/>'
              f'<text x="14" y="34" font-size="24" font-weight="800" fill="url(#txt)">{fmt(val)}</text>'
              f'<text x="14" y="54" font-size="12.5" fill="{C["pastel"]}">{label}</text></g>')

    cx, cy, r = 425, 140, 66
    ring = (f'<circle cx="{cx}" cy="{cy}" r="{r+24}" fill="{C["fucsia"]}" opacity=".25" filter="url(#halo)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["bg"]}" stroke="url(#edge)" stroke-width="4" filter="url(#glow)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r-12}" fill="none" stroke="{C["violeta"]}" stroke-dasharray="2 7" opacity=".7"/>'
            f'<text x="{cx}" y="{cy+12}" font-size="38" font-weight="800" fill="url(#txt)" text-anchor="middle" filter="url(#glow)">{fmt(s["streak"])}</text>'
            f'<text x="{cx}" y="{cy+34}" font-size="11" fill="{C["pastel"]}" text-anchor="middle">días</text>'
            f'<text x="{cx}" y="{cy+r+32}" font-size="14" font-weight="700" fill="{C["blanco"]}" text-anchor="middle">Racha actual</text>'
            f'<text x="{cx}" y="{cy+r+52}" font-size="12" fill="{C["pastel"]}" text-anchor="middle">Mejor racha: {fmt(s["best"])} días</text>')

    lx, ly, lw = 545, 52, 255
    lang = f'<text x="{lx}" y="{ly}" font-size="17" font-weight="700" fill="{C["blanco"]}">Lenguajes más usados</text>'
    if s["langs"]:
        x = lx
        lang += f'<clipPath id="bar"><rect x="{lx}" y="{ly+18}" width="{lw}" height="12" rx="6"/></clipPath><g clip-path="url(#bar)">'
        for i, (_, p) in enumerate(s["langs"]):
            seg = lw * p / sum(q for _, q in s["langs"])
            lang += f'<rect x="{x:.1f}" y="{ly+18}" width="{seg+0.5:.1f}" height="12" fill="{LANG_COLORS[i]}"/>'
            x += seg
        lang += "</g>"
        for i, (n, p) in enumerate(s["langs"]):
            x, y = lx + (i % 2) * 132, ly + 62 + (i // 2) * 30
            lang += (f'<circle cx="{x+6}" cy="{y-4}" r="6" fill="{LANG_COLORS[i]}"/>'
                     f'<text x="{x+18}" y="{y}" font-size="13" fill="{C["blanco"]}">{n} '
                     f'<tspan fill="{C["pastel"]}">{p:.1f}%</tspan></text>')
    else:
        lang += f'<text x="{lx}" y="{ly+40}" font-size="13" fill="{C["pastel"]}">Se completa con la primera actualización.</text>'

    upd = f'<text x="{w-24}" y="{h-16}" font-size="10.5" fill="{C["violeta"]}" text-anchor="end">Actualizado: {s.get("fecha", "—")}</text>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">
<defs>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C['rosaV']}"/><stop offset=".5" stop-color="{C['magenta']}"/><stop offset="1" stop-color="{C['violetaP']}"/></linearGradient>
  <linearGradient id="txt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['rosaV']}"/><stop offset="1" stop-color="{C['violeta']}"/></linearGradient>
  <radialGradient id="panel" cx="50%" cy="50%" r="75%"><stop offset="0" stop-color="#3A1A55"/><stop offset=".6" stop-color="#22163A"/><stop offset="1" stop-color="{C['bg']}"/></radialGradient>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="halo" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="16"/></filter>
</defs>
<rect x="3" y="3" width="{w-6}" height="{h-6}" rx="18" fill="url(#panel)"/>
{t}{ring}{lang}{upd}
<rect x="3" y="3" width="{w-6}" height="{h-6}" rx="18" fill="none" stroke="url(#edge)" stroke-width="2.5" filter="url(#glow)"/>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if "--demo" in sys.argv:
        s = dict(contrib=None, commits=None, repos=None, stars=None, prs=None, issues=None,
                 streak=None, best=None, langs=[], fecha="pendiente")
    else:
        login = os.environ.get("USERNAME") or sys.exit("Falta la variable USERNAME")
        token = os.environ.get("GITHUB_TOKEN") or sys.exit("Falta la variable GITHUB_TOKEN")
        s = summarize(fetch(login, token))
        s["fecha"] = date.today().strftime("%d/%m/%Y")
    OUT.write_text(render(s), encoding="utf-8")
    print("Generado", OUT)
