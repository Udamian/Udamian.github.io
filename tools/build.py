#!/usr/bin/env python3
"""Genera el sitio estatico del portfolio (buscador Cambeiro) a partir de data/*.json.

Uso:  python tools/build.py
Solo usa la biblioteca estandar. Escribe en la raiz del repositorio:
  index.html, en/index.html, p/<slug>/index.html, en/p/<slug>/index.html,
  404.html, assets/covers/<slug>.svg
"""
import json
import os
import posixpath
import random
import re
import shutil
import sys
import unicodedata
from html import escape as esc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skins import SKINS as EXTRA  # noqa: E402  (pieles de proyecto: player, reloc)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ("es", "en")
OUT = ROOT      # carpeta de salida
SUFFIX = ""     # "index.html" en la vista previa (hosts sin indice de carpeta)
SITE = "https://udamian.github.io"  # origen + base_path; build() lo fija desde data/profile.json

STR = {
    "es": {
        "lang_name": "Español", "other_name": "English",
        "default_q": "proyectos de {name}",
        "search_label": "Buscar en el portfolio", "search_btn": "Buscar",
        "tab_all": "Todo", "tab_img": "Imágenes", "tab_code": "Código",
        "tabs_label": "Tipo de resultado", "og_alt": "Cambeiro, el buscador del portfolio de Damián Cambeiro", "home_h1": "Cambeiro: portfolio de {name}",
        "count_one": "1 resultado", "count_many": "{n} resultados",
        "lucky": "Voy a tener suerte",
        "related": "Búsquedas relacionadas", "related_q": "proyectos con {x}",
        "none_title": "Tu búsqueda no ha obtenido ningún resultado.",
        "none_tips": ["Revisa que las palabras estén bien escritas.",
                      "Prueba con otras palabras, por ejemplo «Python» o «Docker».",
                      "Vuelve a escribir «proyectos de {name}» para ver todos."],
        "stop": ["proyecto", "proyectos", "de", "del", "con", "en", "y", "los", "las", "el", "la", "un", "una", "por"],
        "view_page": "Ver página", "repo": "Repositorio", "demo": "Demo",
        "about_kind": "Perfil", "about_slug": "sobre-mi", "util_about": "Sobre mí", "pager_note": "Resultados de la búsqueda", "card_about": "Sobre mí", "card_edu": "Formación", "card_exp": "Experiencia",
        "card_lang": "Idiomas", "card_tools": "Herramientas", "card_links": "Perfiles",
        "link_github": "GitHub", "link_linkedin": "LinkedIn", "link_email": "Correo", "link_cv": "CV (PDF)",
        "code_hint": "Repositorios públicos",
        "footer_note": "Este buscador es ficticio y forma parte del portfolio de Damián Cambeiro. No está afiliado a ningún buscador real.",
        "back": "← Volver a los resultados",
        "what": "Qué hace", "facts": "Datos clave", "stack": "Tecnologías", "notes": "Notas y límites",
        "btn_repo": "Ver código en GitHub", "btn_demo": "Abrir demo",
        "meta_home": "Portfolio de {name}: proyectos de Python, backend e ingeniería de datos, presentados como resultados de un buscador.",
        "nf_title": "404. No se ha encontrado la página",
        "nf_text": "La dirección que has escrito no coincide con ningún documento de este sitio.",
        "nf_back": "Volver al buscador",
        "cover_alt": "Portada de {t}",
        "w_addr": "Dirección", "w_back": "Atrás", "w_ready": "Listo", "w_start": "Inicio", "w_props": "Propiedades", "w_type": "Tipo", "w_tech": "Tecnologías", "w_close": "Cerrar y volver a los resultados",
    },
    "en": {
        "lang_name": "English", "other_name": "Español",
        "default_q": "projects by {name}",
        "search_label": "Search the portfolio", "search_btn": "Search",
        "tab_all": "All", "tab_img": "Images", "tab_code": "Code",
        "tabs_label": "Result type", "og_alt": "Cambeiro, the search engine of Damián Cambeiro's portfolio", "home_h1": "Cambeiro: {name}'s portfolio",
        "count_one": "1 result", "count_many": "{n} results",
        "lucky": "I'm feeling lucky",
        "related": "Related searches", "related_q": "projects with {x}",
        "none_title": "Your search did not match any results.",
        "none_tips": ["Make sure all words are spelled correctly.",
                      "Try different keywords, for example “Python” or “Docker”.",
                      "Type “projects by {name}” again to see everything."],
        "stop": ["project", "projects", "by", "of", "with", "in", "and", "the", "a", "an", "for"],
        "view_page": "View page", "repo": "Repository", "demo": "Demo",
        "about_kind": "Profile", "about_slug": "about", "util_about": "About me", "pager_note": "Search results", "card_about": "About me", "card_edu": "Education", "card_exp": "Experience",
        "card_lang": "Languages", "card_tools": "Tools", "card_links": "Profiles",
        "link_github": "GitHub", "link_linkedin": "LinkedIn", "link_email": "Email", "link_cv": "CV (PDF, in Spanish)",
        "code_hint": "Public repositories",
        "footer_note": "This search engine is fictional and part of Damián Cambeiro's portfolio. It is not affiliated with any real search engine.",
        "back": "← Back to results",
        "what": "What it does", "facts": "Key facts", "stack": "Tech stack", "notes": "Notes and limits",
        "btn_repo": "View code on GitHub", "btn_demo": "Open demo",
        "meta_home": "Portfolio of {name}: Python, backend and data engineering projects, shown as search results.",
        "nf_title": "404. Page not found",
        "nf_text": "The address you typed does not match any document on this site.",
        "nf_back": "Back to the search engine",
        "cover_alt": "Cover of {t}",
        "w_addr": "Address", "w_back": "Back", "w_ready": "Ready", "w_start": "Start", "w_props": "Properties", "w_type": "Type", "w_tech": "Technologies", "w_close": "Close and go back to results",
    },
}

LOGO_COLORS = ["#3b6fd4", "#d93025", "#f4b400", "#3b6fd4", "#0f9d58", "#d93025", "#3b6fd4", "#f4b400"]
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%234d90fe'/%3E"
           "%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='21' font-weight='700' "
           "text-anchor='middle' fill='white'%3EC%3C/text%3E%3C/svg%3E")


# ---------------------------------------------------------------- utilidades
def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def page_dir(lang, rel):
    """Carpeta (desde la raiz del sitio) de una pagina. rel: '' o 'p/<slug>'."""
    return posixpath.join("en", rel) if lang == "en" else rel


def href(from_lang, from_rel, to_lang, to_rel):
    """Enlace relativo entre dos paginas del sitio."""
    a = page_dir(from_lang, from_rel) or "."
    b = page_dir(to_lang, to_rel) or "."
    r = posixpath.relpath(b, a)
    return ("./" if r == "." else r + "/") + SUFFIX


def absurl(lang, rel):
    """URL absoluta (canonical, hreflang, sitemap) de una pagina."""
    d = page_dir(lang, rel).strip("/")
    return f"{SITE}/{d}/" if d else f"{SITE}/"


def asset(from_lang, from_rel, path):
    a = page_dir(from_lang, from_rel) or "."
    return posixpath.relpath(path, a)


def fill(s, **kw):
    return s.format(**kw)


# -------------------------------------------------------------------- portadas
def cover_svg(kind, seed):
    """Portada abstracta provisional (hasta tener capturas reales)."""
    rnd = random.Random(seed)
    W, H = 400, 300
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">']
    if kind == "map":
        out.append(f'<rect width="{W}" height="{H}" fill="#0f1a2e"/>')
        for _ in range(110):
            x, y, r = rnd.uniform(14, 386), rnd.uniform(14, 286), rnd.uniform(1.5, 4.5)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#6aa7ff" opacity="{rnd.uniform(.25, .8):.2f}"/>')
        pts = []
        for i in range(5):
            import math
            ang = -math.pi / 2 + i * 2 * math.pi / 5
            rad = rnd.uniform(60, 110)
            pts.append(f"{200 + rad * math.cos(ang):.1f},{150 + rad * math.sin(ang):.1f}")
        out.append(f'<polygon points="{" ".join(pts)}" fill="#ffd166" fill-opacity=".18" stroke="#ffd166" stroke-width="3"/>')
    elif kind == "funnel":
        out.append(f'<rect width="{W}" height="{H}" fill="#1b1626"/>')
        widths = [300, 240, 170, 105, 60]
        for i, w in enumerate(widths):
            y = 36 + i * 48
            out.append(f'<rect x="{200 - w / 2:.0f}" y="{y}" width="{w}" height="34" rx="4" fill="#c084fc" opacity="{1 - i * .15:.2f}"/>')
        out.append('<polyline points="20,280 90,262 160,270 230,246 300,252 380,226" fill="none" stroke="#f0abfc" stroke-width="3"/>')
    else:  # sync
        out.append(f'<rect width="{W}" height="{H}" fill="#10161c"/>')
        for i in range(7):
            w1 = rnd.uniform(70, 130)
            y = 36 + i * 34
            out.append(f'<rect x="30" y="{y}" width="{w1:.0f}" height="16" rx="3" fill="#5ac8a8"/>')
            out.append(f'<rect x="{W - 30 - w1:.0f}" y="{y}" width="{w1:.0f}" height="16" rx="3" fill="#e8a14c"/>')
            out.append(f'<line x1="{30 + w1 + 8:.0f}" y1="{y + 8}" x2="{W - 30 - w1 - 8:.0f}" y2="{y + 8}" stroke="#ffffff" stroke-opacity=".28" stroke-dasharray="4 5"/>')
    out.append("</svg>")
    return "".join(out)


# -------------------------------------------------------------------- plantillas
def logo(small=False):
    letters = "".join(f'<span style="color:{LOGO_COLORS[i]}">{c}</span>' for i, c in enumerate("Cambeiro"))
    return letters


def head(lang, rel, title, desc, alts, css, extra=""):
    s = STR[lang]
    links = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in alts.items()
    ) + f'<link rel="alternate" hreflang="x-default" href="{alts["es"]}">'
    links += f'<link rel="canonical" href="{alts[lang]}">'
    img = f"{SITE}/assets/og.png"
    social = (
        f'<meta property="og:url" content="{alts[lang]}">'
        f'<meta property="og:site_name" content="Cambeiro">'
        f'<meta property="og:locale" content="{"es_ES" if lang == "es" else "en_GB"}">'
        f'<meta property="og:image" content="{img}">'
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        f'<meta property="og:image:alt" content="{esc(s["og_alt"])}">'
        '<meta name="twitter:card" content="summary_large_image">'
    )
    csslinks = "".join('<link rel="stylesheet" href="%s">' % c for c in css)
    return (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title>"
        f'<meta name="description" content="{esc(desc)}">'
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
        '<meta property="og:type" content="website">'
        f'{social}<link rel="icon" href="{FAVICON}">{links}'
        f"{csslinks}{extra}</head>"
    )


def header(lang, rel, prof, qvalue, switch_href):
    s = STR[lang]
    gh = prof["links"]["github"]
    other = "en" if lang == "es" else "es"
    return f"""<nav class="util" aria-label="Links"><a href="{href(lang, rel, lang, 'about')}">{esc(s['util_about'])}</a><a href="{switch_href}" hreflang="{other}" lang="{other}">{esc(s['other_name'])}</a><a href="{esc(gh)}" rel="noopener">GitHub</a></nav>
<header class="top">
<a class="logo" href="{href(lang, rel, lang, '')}" aria-label="Cambeiro">{logo()}</a>
<form id="f" class="box" role="search" autocomplete="off">
<input id="q" name="q" type="search" value="{esc(qvalue)}" aria-label="{esc(s['search_label'])}" spellcheck="false">
<button type="submit" aria-label="{esc(s['search_btn'])}"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="10" cy="10" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15 15l6 6" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg></button>
</form>
</header>"""


def profile_hay(lang, prof):
    return norm(" ".join([prof["name"], prof["role"][lang], prof["bio"][lang], " ".join(prof["skills"]),
                          " ".join(prof["education"][lang]), " ".join(prof["experience"][lang])]))


def contact_links(lang, rel, prof, email_text=False):
    """Enlaces de contacto (GitHub, LinkedIn, correo, CV) con las rutas relativas a la pagina."""
    L, s, ln = prof["links"], STR[lang], []
    if L.get("github"):
        ln.append(f'<a href="{esc(L["github"])}" rel="noopener">{s["link_github"]}</a>')
    if L.get("linkedin"):
        ln.append(f'<a href="{esc(L["linkedin"])}" rel="noopener">{s["link_linkedin"]}</a>')
    if L.get("email"):
        ln.append(f'<a href="mailto:{esc(L["email"])}">{esc(L["email"]) if email_text else s["link_email"]}</a>')
    if L.get("cv"):
        ln.append(f'<a href="{asset(lang, rel, L["cv"])}">{s["link_cv"]}</a>')
    return ln


def profile_result(lang, rel, prof):
    s = STR[lang]
    page = href(lang, rel, lang, "about")
    sl = [f'<a href="{page}">{esc(s["view_page"])}</a>'] + contact_links(lang, rel, prof)
    return f"""<article class="res" data-hay="{esc(profile_hay(lang, prof))}">
<div class="rt"><div class="u">{esc(prof['site_host'])} › {s['about_slug']}</div>
<h2><a href="{page}">{esc(prof['name'])} · {esc(s['about_kind'])}</a></h2>
<p>{esc(prof['bio'][lang])}</p>
<p class="stk">{esc(prof['role'][lang])}</p>
<p class="sl">{' · '.join(sl)}</p></div>
<a class="th" href="{page}" tabindex="-1" aria-hidden="true"><img src="{asset(lang, rel, 'assets/covers/perfil.svg')}" alt="" width="400" height="300" loading="lazy"></a>
</article>"""


def cover_of(lang, rel, p):
    """Miniatura real si el proyecto tiene captura; si no, la portada abstracta provisional."""
    if p.get("shot"):
        return asset(lang, rel, p["shot"]["thumb"])
    return asset(lang, rel, f"assets/covers/{p['slug']}.svg")


def result(lang, rel, p, prof):
    s = STR[lang]
    page = href(lang, rel, lang, f"p/{p['slug']}")
    cover = cover_of(lang, rel, p)
    hay = norm(" ".join([p["title"], p["kind"][lang], p["summary"][lang], " ".join(p["stack"]), " ".join(p["features"][lang])]))
    sl = [f'<a href="{page}">{esc(s["view_page"])}</a>', f'<a href="{esc(p["links"]["repo"])}" rel="noopener">{esc(s["repo"])}</a>']
    if p["links"]["demo"]:
        sl.append(f'<a href="{esc(p["links"]["demo"])}" rel="noopener">{esc(s["demo"])}</a>')
    return f"""<article class="res" data-hay="{esc(hay)}">
<div class="rt"><div class="u">{esc(prof['site_host'])} › {'proyectos' if lang == 'es' else 'projects'} › {esc(p['slug'])}</div>
<h2><a href="{page}">{esc(p['title'])} · {esc(p['kind'][lang])}</a></h2>
<p>{esc(p['summary'][lang])}</p>
<p class="stk">{esc(' · '.join(p['stack'][:5]))}</p>
<p class="sl">{' · '.join(sl)}</p></div>
<a class="th" href="{page}" tabindex="-1" aria-hidden="true"><img src="{cover}" alt="" width="400" height="300" loading="lazy"></a>
</article>"""


def figure(lang, rel, p):
    s = STR[lang]
    page = href(lang, rel, lang, f"p/{p['slug']}")
    cover = cover_of(lang, rel, p)
    hay = norm(" ".join([p["title"], p["kind"][lang], p["summary"][lang], " ".join(p["stack"])]))
    return (f'<figure class="fig" data-hay="{esc(hay)}"><a href="{page}"><img src="{cover}" alt="{esc(fill(s["cover_alt"], t=p["title"]))}" width="400" height="300" loading="lazy"></a>'
            f'<figcaption><a href="{page}">{esc(p["title"])}</a><span>{esc(p["kind"][lang])}</span></figcaption></figure>')


def code_row(lang, p):
    hay = norm(" ".join([p["title"], p["kind"][lang], p["summary"][lang], " ".join(p["stack"])]))
    repo = p["links"]["repo"]
    path = repo.replace("https://github.com/", "")
    return (f'<div class="code" data-hay="{esc(hay)}"><a href="{esc(repo)}" rel="noopener">{esc(path)}</a>'
            f'<p>{esc(p["summary"][lang])}</p><p class="stk">{esc(" · ".join(p["stack"]))}</p></div>')


def profile_figure(lang, rel, prof):
    s = STR[lang]
    page = href(lang, rel, lang, "about")
    return (f'<figure class="fig" data-hay="{esc(profile_hay(lang, prof))}"><a href="{page}"><img src="{asset(lang, rel, "assets/covers/perfil.svg")}" alt="" width="400" height="300" loading="lazy"></a>'
            f'<figcaption><a href="{page}">{esc(prof["name"])}</a><span>{esc(s["about_kind"])}</span></figcaption></figure>')


def profile_code(lang, prof):
    gh = prof["links"]["github"]
    return (f'<div class="code" data-hay="{esc(profile_hay(lang, prof))}"><a href="{esc(gh)}" rel="noopener">{esc(gh.replace("https://", ""))}</a>'
            f'<p>{esc(prof["role"][lang])}</p><p class="stk">{esc(" · ".join(prof["skills"]))}</p></div>')


def avatar_svg(initials):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img"><rect width="400" height="300" fill="#4d90fe"/>'
            f'<text x="200" y="198" font-family="Georgia,serif" font-weight="700" font-size="140" text-anchor="middle" fill="#fff">{esc(initials)}</text></svg>')


def about_page(lang, prof):
    s = STR[lang]
    rel = "about"
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, "assets/buscador.css"), asset(lang, rel, "skins/base.css")]
    other = "en" if lang == "es" else "es"
    ln = contact_links(lang, rel, prof, email_text=True)
    edu = "".join(f"<li>{esc(x)}</li>" for x in prof["education"][lang])
    exp = "".join(f"<li>{esc(x)}</li>" for x in prof["experience"][lang])
    chips = "".join(f"<li>{esc(t)}</li>" for t in prof["skills"])
    body = f"""<body class="skin-base">
<header class="ptop"><a href="{href(lang, rel, lang, '')}">{esc(s['back'])}</a>
<a class="lang" href="{href(lang, rel, other, rel)}" hreflang="{other}" lang="{other}">{esc(s['other_name'])}</a></header>
<main class="proj">
<p class="kind">{esc(s['about_kind'])}</p>
<h1>{esc(prof['name'])}</h1>
<p class="lead">{esc(prof['role'][lang])}</p>
<p>{esc(prof['bio'][lang])}</p>
<h2>{esc(s['card_edu'])}</h2><ul>{edu}</ul>
<h2>{esc(s['card_exp'])}</h2><ul>{exp}</ul>
<h2>{esc(s['card_lang'])}</h2><p>{esc(prof['languages'][lang])}</p>
<h2>{esc(s['card_tools'])}</h2><ul class="chips">{chips}</ul>
<h2>{esc(s['card_links'])}</h2><p>{' · '.join(ln)}</p>
</main>
<footer class="ft"><p>© 2026 {esc(prof['name'])}</p></footer>
</body></html>"""
    title = f"{prof['name']} - {s['about_kind']} - Cambeiro"
    return head(lang, rel, title, prof["bio"][lang], alts, css) + body


def home(lang, prof, projects):
    s = STR[lang]
    rel = ""
    qdef = fill(s["default_q"], name=prof["first_name"])
    alt_href = href(lang, rel, "en" if lang == "es" else "es", "")
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, "assets/buscador.css")]
    stop = sorted(set(norm(w) for w in s["stop"]) | set(norm(prof["name"]).split()))
    cfg = {"stop": stop, "def": qdef, "one": s["count_one"], "many": s["count_many"]}

    # busquedas relacionadas: tecnologias mas repetidas, luego las primeras de cada proyecto
    counts = {}
    for p in projects:
        for t in p["stack"]:
            counts[t] = counts.get(t, 0) + 1
    rel_terms = sorted(counts, key=lambda t: (-counts[t], t.lower()))[:8]
    related = "".join(
        f'<li><a href="#" data-q="{esc(fill(s["related_q"], x=t))}">{esc(fill(s["related_q"], x=t))}</a></li>' for t in rel_terms
    )
    results = profile_result(lang, rel, prof) + "".join(result(lang, rel, p, prof) for p in projects)
    figs = profile_figure(lang, rel, prof) + "".join(figure(lang, rel, p) for p in projects)
    codes = profile_code(lang, prof) + "".join(code_row(lang, p) for p in projects)
    tips = "".join(f"<li>{esc(fill(t, name=prof['first_name']))}</li>" for t in s["none_tips"])
    n = len(projects) + 1  # proyectos + perfil
    count = s["count_one"] if n == 1 else fill(s["count_many"], n=n)

    body = f"""<body>
<div class="sr">
{header(lang, rel, prof, qdef, alt_href)}
<section class="tabs2" aria-label="{esc(s['tabs_label'])}"><div role="tablist" aria-label="{esc(s['tabs_label'])}">
<a role="tab" href="#todo" data-tab="todo" aria-selected="true">{s['tab_all']}</a>
<a role="tab" href="#imagenes" data-tab="imagenes" aria-selected="false">{s['tab_img']}</a>
<a role="tab" href="#codigo" data-tab="codigo" aria-selected="false">{s['tab_code']}</a></div>
<button type="button" id="lucky" class="lucky">{esc(s['lucky'])}</button></section>
<main data-tab="todo">
<h1 class="vh">{esc(fill(s['home_h1'], name=prof['name']))}</h1>
<p id="cnt" class="cnt" aria-live="polite">{esc(count)}</p>
<div id="none" class="none" hidden><p><b>{esc(s['none_title'])}</b></p><ul>{tips}</ul></div>
<section id="p-todo">{results}</section>
<section id="p-imagenes" class="igrid" aria-label="{esc(s['tab_img'])}">{figs}</section>
<section id="p-codigo" aria-label="{esc(s['code_hint'])}">{codes}</section>
<section class="rel" id="rel"><h2>{esc(s['related'])}</h2><ul>{related}</ul></section>
</main>
<footer class="ft">
<p class="pager" aria-label="{esc(s['pager_note'])}"><span class="pl">{logo()}</span><span class="pn">1</span></p>
<p><a href="{href(lang, rel, lang, 'about')}">{esc(s['util_about'])}</a> · <a href="{alt_href}" hreflang="{'en' if lang == 'es' else 'es'}">{esc(s['other_name'])}</a> · {' · '.join(contact_links(lang, rel, prof)[:3])}</p>
<p>{esc(s['footer_note'])}</p><p>© 2026 {esc(prof['name'])}</p>
</footer>
</div>
<script type="application/json" id="cfg">{json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="{asset(lang, rel, 'assets/buscador.js')}" defer></script>
</body></html>"""
    desc = fill(s["meta_home"], name=prof["name"])
    title = f"{qdef} - Cambeiro"
    return head(lang, rel, title, desc, alts, css) + body


def project_extra(lang, prof, p, skin):
    """Pieles de tools/skins.py (reproductor, teletexto, hoja de calculo)."""
    s = STR[lang]
    rel = f"p/{p['slug']}"
    other = "en" if lang == "es" else "es"
    c = dict(lang=lang, s=s, slug=p["slug"], title=p["title"], kind=p["kind"][lang], summary=p["summary"][lang],
             feats=p["features"][lang], facts=p["facts"][lang], stack=p["stack"], note=p["note"][lang],
             repo=p["links"]["repo"], demo=p["links"]["demo"], home=href(lang, rel, lang, ""), other=other,
             other_h=href(lang, rel, other, rel), name=prof["name"], author=prof["first_name"], initials=prof["initials"],
             asset_js=asset(lang, rel, "assets/reloc.js"), shot=(dict(src=asset(lang, rel, p["shot"]["full"]), w=p["shot"]["w"], h=p["shot"]["h"], alt=p["shot"]["alt"][lang], cap=p["shot"]["cap"][lang]) if p.get("shot") else None), asset_data=asset(lang, rel, "assets/reloc-data.js"))
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, f"skins/{skin}.css")]
    return head(lang, rel, f"{p['title']} - {prof['name']} - Cambeiro", p["summary"][lang], alts, css) + EXTRA[skin](c)


def project_page(lang, prof, p):
    skin = p.get("skin")
    if skin in EXTRA:
        return project_extra(lang, prof, p, skin)
    s = STR[lang]
    rel = f"p/{p['slug']}"
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, "assets/buscador.css"), asset(lang, rel, "skins/base.css")]
    other = "en" if lang == "es" else "es"
    feats = "".join(f"<li>{esc(x)}</li>" for x in p["features"][lang])
    facts = "".join(f"<li>{esc(x)}</li>" for x in p["facts"][lang])
    chips = "".join(f"<li>{esc(t)}</li>" for t in p["stack"])
    btns = f'<a class="btn" href="{esc(p["links"]["repo"])}" rel="noopener">{esc(s["btn_repo"])}</a>'
    if p["links"]["demo"]:
        btns += f' <a class="btn alt" href="{esc(p["links"]["demo"])}" rel="noopener">{esc(s["btn_demo"])}</a>'
    cover = cover_of(lang, rel, p)
    body = f"""<body class="skin-base">
<header class="ptop"><a href="{href(lang, rel, lang, '')}">{esc(s['back'])}</a>
<a class="lang" href="{href(lang, rel, other, rel)}" hreflang="{other}" lang="{other}">{esc(s['other_name'])}</a></header>
<main class="proj">
<p class="kind">{esc(p['kind'][lang])}</p>
<h1>{esc(p['title'])}</h1>
<p class="lead">{esc(p['summary'][lang])}</p>
<p class="btns">{btns}</p>
<img class="hero" src="{cover}" alt="{esc(fill(s['cover_alt'], t=p['title']))}" width="400" height="300">
<h2>{esc(s['what'])}</h2><ul>{feats}</ul>
<h2>{esc(s['facts'])}</h2><ul>{facts}</ul>
<h2>{esc(s['stack'])}</h2><ul class="chips">{chips}</ul>
<h2>{esc(s['notes'])}</h2><p>{esc(p['note'][lang])}</p>
</main>
<footer class="foot"><div class="wrap"><p>© 2026 {esc(prof['name'])}</p></div></footer>
</body></html>"""
    title = f"{p['title']} - {prof['name']} - Cambeiro"
    return head(lang, rel, title, p["summary"][lang], alts, css) + body


def not_found(prof):
    # 404 sirve desde cualquier ruta: usa base_path absoluto
    bp = prof.get("base_path", "").rstrip("/")
    s = STR["es"]
    e = STR["en"]
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>404 - Cambeiro</title>
<link rel="icon" href="{FAVICON}"><link rel="stylesheet" href="{bp}/assets/buscador.css"><link rel="stylesheet" href="{bp}/skins/base.css"></head>
<body class="skin-base"><main class="proj"><p class="logo big">{logo()}</p>
<h1>{esc(s['nf_title'])}</h1><p class="lead">{esc(s['nf_text'])}</p>
<p><a class="btn" href="{bp}/">{esc(s['nf_back'])}</a></p>
<h1 lang="en">{esc(e['nf_title'])}</h1><p class="lead" lang="en">{esc(e['nf_text'])}</p>
<p><a class="btn alt" href="{bp}/en/" lang="en">{esc(e['nf_back'])}</a></p></main></body></html>"""


def preview(out):
    """Vista previa: enlaces explicitos a index.html y portada como fragmento (para publicarla como Artifact)."""
    global OUT, SUFFIX
    OUT, SUFFIX = os.path.abspath(out), "index.html"
    shutil.rmtree(OUT, ignore_errors=True)
    for d in ("assets", "skins"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(OUT, d), ignore=shutil.ignore_patterns("covers"))
    build()
    p = os.path.join(OUT, "index.html")
    h = open(p, encoding="utf-8").read()
    keep = re.findall(r'<meta name="description"[^>]*>|<link rel="stylesheet"[^>]*>', h)
    body = re.search(r"<body>(.*)</body>", h, re.S).group(1)
    frag = "<title>Portfolio Cambeiro</title>\n" + "\n".join(keep) + "\n" + body
    open(p, "w", encoding="utf-8").write(frag)
    print("Vista previa en", OUT)


def sitemap(projects):
    """sitemap.xml con las paginas de ambos idiomas y sus alternativas hreflang."""
    rels = ["", "about"] + [f"p/{p['slug']}" for p in projects]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for rel in rels:
        for lang in LANGS:
            alt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{absurl(l, rel)}"/>' for l in LANGS)
            alt += f'<xhtml:link rel="alternate" hreflang="x-default" href="{absurl("es", rel)}"/>'
            out.append(f"<url><loc>{absurl(lang, rel)}</loc>{alt}</url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def build():
    global SITE
    prof = load("profile.json")
    projects = load("projects.json")
    SITE = f"https://{prof['site_host']}{prof.get('base_path', '').rstrip('/')}"
    for p in projects:
        if not p.get("shot"):
            write(f"assets/covers/{p['slug']}.svg", cover_svg(p["cover"], p["slug"]))
    write("assets/covers/perfil.svg", avatar_svg(prof["initials"]))
    for lang in LANGS:
        write(posixpath.join(page_dir(lang, "about"), "index.html"), about_page(lang, prof))
        write(posixpath.join(page_dir(lang, ""), "index.html"), home(lang, prof, projects))
        for p in projects:
            write(posixpath.join(page_dir(lang, f"p/{p['slug']}"), "index.html"), project_page(lang, prof, p))
    write("404.html", not_found(prof))
    write(".nojekyll", "")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("sitemap.xml", sitemap(projects))
    print(f"OK: {len(projects)} proyectos x {len(LANGS)} idiomas")


def main():
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    else:
        build()


if __name__ == "__main__":
    main()
