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
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skins import SKINS as EXTRA  # noqa: E402  (pieles de proyecto: player, reloc)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ("es", "en")
OUT = ROOT      # carpeta de salida
SUFFIX = ""     # "index.html" en la vista previa (hosts sin indice de carpeta)
SITE = "https://udamian.github.io"  # origen + base_path; build() lo fija desde data/profile.json
ANALYTICS = ""  # codigo de GoatCounter (data/profile.json -> analytics.goatcounter); vacio = sin analitica

STR = {
    "es": {
        "lang_name": "Español", "other_name": "English",
        "bar_one": "Resultado 1 - 1 de 1 de", "bar_many": "Resultados 1 - {n} de {n} de", "bar_tail": "(0,00 segundos)",
        "none_q": "Tu búsqueda - {q} - no obtuvo ningún resultado.", "similar": "Páginas similares", "ads_h": "Enlaces patrocinados",
        "pager_res": "Página de resultados:", "sz_px": "{w} x {h} píxeles - {k}k", "more_about": "Sobre mí »",
        "ad1_t": "{name}: desarrollador junior", "ad1_a": "Python, SQL y datos.", "ad1_b": "Máster en Big Data e IA y ciclo DAM.",
        "ad2_t": "CV de {name} (PDF)", "ad2_a": "Perfil, competencias y proyectos", "ad2_b": "en una sola página.",
        "ad3_t": "Escríbeme", "ad3_a": "Busco mi primer puesto en backend,", "ad3_b": "análisis o ingeniería de datos.",
        "ad4_t": "{name} en LinkedIn", "ad4_a": "Experiencia, formación y contacto", "ad4_b": "profesional.",
        "copy_mail": "Copiar correo", "copied": "Correo copiado", "copy_fail": "No se pudo copiar. Selecciónalo:",
        "ob_cv": "Descargar CV (PDF)", "ob_mail": "Escríbeme", "ob_more": "Más sobre mí »",
        "didyou": "Quizás quisiste decir:", "didyou_link": "contratar a Damián",
        "didyou_txt": "Escríbeme por correo o por LinkedIn: busco mi primer puesto en backend, análisis o ingeniería de datos.",
        "p_label": "Perfil de Damián Cambeiro", "p_cache": "En caché · {date}", "p_more": "Ver el perfil completo y el CV en caché",
        "f_edu": "Formación", "f_exp": "Experiencia", "f_lang": "Idiomas", "f_tools": "Herramientas", "f_loc": "Ubicación",
        "next": "Siguiente", "nav_top": "Enlaces", "nav_foot": "Pie de página", "pager_label": "Cambeiro, página 1", "cv_img_alt": "Cabecera del CV de Damián Cambeiro: nombre, puesto, contacto y perfil.",
        "cap_img": "Captura de {t}", "stats_label": "Datos clave",
        "ab_back": "← Resultados", "ab_path": "Trayectoria", "ab_tools": "Herramientas", "ab_tools_p": "Búsquedas relacionadas con este perfil. Cada una abre los proyectos que la usan.",
        "ab_lang": "Idiomas", "n_proj_one": "1 proyecto", "n_proj_many": "{n} proyectos", "ab_hire_p": "Escríbeme por correo o por LinkedIn. El CV está a un clic, a la derecha.",
        "ab_mail": "Escríbeme un correo", "ab_li": "Abrir LinkedIn",
        "cache_banner": "Esta es la copia en caché de Cambeiro de <a href=\"{url}\">{file}</a>. Es una instantánea de la página tal y como se veía el {date}. La página actual puede haber cambiado desde entonces.<br>Se han resaltado estos términos de búsqueda:",
        "terms_label": "Resaltar en el CV:", "term_ph": "escribe otro término", "term_rm": "quitar", "term_add": "Resaltar",
        "open_pdf": "Abrir el PDF", "dl_pdf": "Descargar · {size}", "dl_cv": "Descargar CV · PDF · {size}", "folio_label": "Copia del CV de Damián Cambeiro (en español)", "see_cv": "Ver el CV completo",
        "months": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
        "default_q": "proyectos de {name}",
        "search_label": "Buscar en el portfolio", "search_btn": "Buscar",
        "tab_all": "Web", "tab_img": "Imágenes", "tab_code": "Código",
        "tabs_label": "Tipo de resultado", "og_alt": "Cambeiro, el buscador del portfolio de Damián Cambeiro", "home_h1": "Cambeiro: portfolio de {name}",
        "count_one": "Cambeiro encontró 1 resultado (0,00 segundos)", "count_many": "Cambeiro encontró {n} resultados (0,00 segundos)",
        "lucky": "Voy a tener suerte",
        "related": "Búsquedas relacionadas", "related_q": "proyectos con {x}",
        "none_title": "Tu búsqueda no ha obtenido ningún resultado.", "none_sug": "Sugerencias:",
        "none_tips": ["Revisa que las palabras estén bien escritas.",
                      "Prueba con otras palabras, por ejemplo «Python» o «Docker».",
                      "Vuelve a escribir «proyectos de {name}» para ver todos."],
        "stop": ["proyecto", "proyectos", "de", "del", "con", "en", "y", "los", "las", "el", "la", "un", "una", "por"],
        "view_page": "Ver página", "repo": "Repositorio",
        "about_kind": "Perfil", "about_slug": "sobre-mi", "util_about": "Sobre mí", "pager_note": "Resultados de la búsqueda", "card_about": "Sobre mí", "card_edu": "Formación", "card_exp": "Experiencia",
        "card_lang": "Idiomas", "card_tools": "Herramientas", "card_links": "Perfiles",
        "link_github": "GitHub", "link_linkedin": "LinkedIn", "link_email": "Correo", "link_cv": "CV (PDF)",
        "code_hint": "Repositorios públicos",
        "footer_note": "Este buscador es ficticio y forma parte del portfolio de Damián Cambeiro. No está afiliado a ningún buscador real.",
        "privacy": "Estadísticas de visitas anónimas con GoatCounter: sin cookies ni datos personales.",
        "back": "← Volver a los resultados",
        "what": "Qué hace", "facts": "Datos clave", "stack": "Tecnologías", "notes": "Notas y límites",
        "btn_repo": "Ver código en GitHub",
        "meta_home": "Portfolio de {name}: proyectos de Python, backend e ingeniería de datos, presentados como resultados de un buscador.",
        "nf_title": "404. No se ha encontrado la página",
        "nf_text": "La dirección que has escrito no coincide con ningún documento de este sitio.",
        "nf_back": "Volver al buscador",
        "cover_alt": "Portada de {t}",
        "w_addr": "Dirección", "w_back": "Atrás", "w_ready": "Listo", "w_start": "Inicio", "w_props": "Propiedades", "w_type": "Tipo", "w_tech": "Tecnologías", "w_close": "Cerrar y volver a los resultados",
    },
    "en": {
        "lang_name": "English", "other_name": "Español",
        "bar_one": "Results 1 - 1 of 1 for", "bar_many": "Results 1 - {n} of {n} for", "bar_tail": "(0.00 seconds)",
        "none_q": "Your search - {q} - did not match any documents.", "similar": "Similar pages", "ads_h": "Sponsored Links",
        "pager_res": "Result Page:", "sz_px": "{w} x {h} pixels - {k}k", "more_about": "About me »",
        "ad1_t": "{name}: junior developer", "ad1_a": "Python, SQL and data.", "ad1_b": "Big Data and AI master's, DAM diploma.",
        "ad2_t": "{name}'s CV (PDF)", "ad2_a": "Profile, skills and projects", "ad2_b": "on a single page.",
        "ad3_t": "Write to me", "ad3_a": "Looking for my first role in backend,", "ad3_b": "data analysis or data engineering.",
        "ad4_t": "{name} on LinkedIn", "ad4_a": "Experience, education and", "ad4_b": "professional contact.",
        "copy_mail": "Copy email", "copied": "Email copied", "copy_fail": "Could not copy. Select it:",
        "ob_cv": "Download CV (PDF)", "ob_mail": "Email me", "ob_more": "More about me »",
        "didyou": "Did you mean:", "didyou_link": "hire Damián",
        "didyou_txt": "Write to me by email or LinkedIn: I'm looking for my first role in backend, data analysis or data engineering.",
        "p_label": "Damián Cambeiro's profile", "p_cache": "Cached · {date}", "p_more": "See the full profile and the cached CV",
        "f_edu": "Education", "f_exp": "Experience", "f_lang": "Languages", "f_tools": "Tools", "f_loc": "Location",
        "next": "Next", "nav_top": "Links", "nav_foot": "Footer", "pager_label": "Cambeiro, page 1", "cv_img_alt": "Top of Damián Cambeiro's CV: name, title, contact details and profile.",
        "cap_img": "Screenshot of {t}", "stats_label": "Key figures",
        "ab_back": "← Results", "ab_path": "Background", "ab_tools": "Tools", "ab_tools_p": "Searches related to this profile. Each one opens the projects that use it.",
        "ab_lang": "Languages", "n_proj_one": "1 project", "n_proj_many": "{n} projects", "ab_hire_p": "Write to me by email or LinkedIn. The CV is one click away, on the right.",
        "ab_mail": "Email me", "ab_li": "Open LinkedIn",
        "cache_banner": "This is Cambeiro's cache of <a href=\"{url}\">{file}</a>. It is a snapshot of the page as it appeared on {date}. The current page could have changed in the meantime.<br>These search terms have been highlighted:",
        "terms_label": "Highlight in the CV:", "term_ph": "type another term", "term_rm": "remove", "term_add": "Highlight",
        "open_pdf": "Open the PDF", "dl_pdf": "Download · {size}", "dl_cv": "Download CV · PDF · {size}", "folio_label": "Copy of Damián Cambeiro's CV (in Spanish)", "see_cv": "See the full CV",
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "default_q": "projects by {name}",
        "search_label": "Search the portfolio", "search_btn": "Search",
        "tab_all": "Web", "tab_img": "Images", "tab_code": "Code",
        "tabs_label": "Result type", "og_alt": "Cambeiro, the search engine of Damián Cambeiro's portfolio", "home_h1": "Cambeiro: {name}'s portfolio",
        "count_one": "Cambeiro found 1 result (0.00 seconds)", "count_many": "Cambeiro found {n} results (0.00 seconds)",
        "lucky": "I'm feeling lucky",
        "related": "Related searches", "related_q": "projects with {x}",
        "none_title": "Your search did not match any results.", "none_sug": "Suggestions:",
        "none_tips": ["Make sure all words are spelled correctly.",
                      "Try different keywords, for example “Python” or “Docker”.",
                      "Type “projects by {name}” again to see everything."],
        "stop": ["project", "projects", "by", "of", "with", "in", "and", "the", "a", "an", "for"],
        "view_page": "View page", "repo": "Repository",
        "about_kind": "Profile", "about_slug": "about", "util_about": "About me", "pager_note": "Search results", "card_about": "About me", "card_edu": "Education", "card_exp": "Experience",
        "card_lang": "Languages", "card_tools": "Tools", "card_links": "Profiles",
        "link_github": "GitHub", "link_linkedin": "LinkedIn", "link_email": "Email", "link_cv": "CV (PDF, in Spanish)",
        "code_hint": "Public repositories",
        "footer_note": "This search engine is fictional and part of Damián Cambeiro's portfolio. It is not affiliated with any real search engine.",
        "privacy": "Anonymous visit statistics with GoatCounter: no cookies, no personal data.",
        "back": "← Back to results",
        "what": "What it does", "facts": "Key facts", "stack": "Tech stack", "notes": "Notes and limits",
        "btn_repo": "View code on GitHub",
        "meta_home": "Portfolio of {name}: Python, backend and data engineering projects, shown as search results.",
        "nf_title": "404. Page not found",
        "nf_text": "The address you typed does not match any document on this site.",
        "nf_back": "Back to the search engine",
        "cover_alt": "Cover of {t}",
        "w_addr": "Address", "w_back": "Back", "w_ready": "Ready", "w_start": "Start", "w_props": "Properties", "w_type": "Type", "w_tech": "Technologies", "w_close": "Close and go back to results",
    },
}

LOGO_COLORS = ["#0033cc", "#cc0000", "#ffcc00", "#0033cc", "#009900", "#cc0000", "#0033cc", "#ffcc00"]
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0' stop-color='%23fff'/%3E%3Cstop offset='1' stop-color='%23dfe6f5'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect x='.8' y='1.2' width='30.4' height='30' rx='7' fill='%23000' fill-opacity='.22'/%3E%3Crect x='.5' y='.5' width='30.4' height='30' rx='7' fill='url(%23g)' stroke='%23aab4cc' stroke-width='.8'/%3E%3Cpath d=%22M23.49 22.83A8.6 8.6 0 1 1 23.49 11.77%22 fill=%22none%22 stroke=%22%23000%22 stroke-width=%226.4%22 stroke-opacity=%220.28%22/%3E%3Cpath d=%22M22.59 21.53A8.6 8.6 0 0 1 13.06 24.08%22 fill=%22none%22 stroke=%22%2334a853%22 stroke-width=%226.4%22/%3E%3Cpath d=%22M13.06 24.08A8.6 8.6 0 0 1 7.40 16.00%22 fill=%22none%22 stroke=%22%23fbbc05%22 stroke-width=%226.4%22/%3E%3Cpath d=%22M7.40 16.00A8.6 8.6 0 0 1 14.51 7.53%22 fill=%22none%22 stroke=%22%23ea4335%22 stroke-width=%226.4%22/%3E%3Cpath d=%22M14.51 7.53A8.6 8.6 0 0 1 22.59 10.47%22 fill=%22none%22 stroke=%22%234285f4%22 stroke-width=%226.4%22/%3E%3C/svg%3E")


# ---------------------------------------------------------------- utilidades
def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def with_analytics(rel, text):
    """Inyecta GoatCounter (sin cookies) y el script de eventos en cada HTML. Nada si no hay codigo o es la vista previa."""
    if not ANALYTICS or SUFFIX or not rel.endswith(".html") or "</head>" not in text:
        return text
    ev = posixpath.relpath("assets/eventos.js", posixpath.dirname(rel) or ".")
    gc = (f'<script data-goatcounter="https://{ANALYTICS}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
          f'<script src="{ev}" defer></script>')
    return text.replace("</head>", gc + "</head>", 1)


def preview_targets(text):
    """Solo vista previa: el marco del Artifact no navega dentro de si mismo, asi que los enlaces externos y mailto se abren aparte."""
    def fix(m):
        tag = m.group(0)
        if "target=" in tag:
            return tag
        if "rel=" not in tag:
            tag = tag[:-1] + ' rel="noopener">'
        return tag[:-1] + ' target="_blank">'
    return re.sub(r'<a\b[^>]*href="https?://[^"]*"[^>]*>', fix, text)


def write(rel, text):
    if SUFFIX and rel.endswith(".html"):
        text = preview_targets(text)
    text = with_analytics(rel, text)
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
    return "".join(f'<span style="color:{LOGO_COLORS[i]}">{c}</span>' for i, c in enumerate("Cambeiro"))


def rich(t):
    """Texto con **negrita** y *cursiva* minimos (datos propios, ya de confianza)."""
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)


def fmt_date(lang, iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {STR[lang]['months'][m - 1]} {y}"


def file_kb(path):
    return f"{round(os.path.getsize(os.path.join(ROOT, path)) / 1024)} KB"


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
        '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="strict-origin-when-cross-origin">'
        f"<title>{esc(title)}</title>"
        f'<meta name="description" content="{esc(desc)}">'
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
        '<meta property="og:type" content="website">'
        f'{social}<link rel="icon" href="{FAVICON}"><link rel="apple-touch-icon" href="{asset(lang, rel, "assets/icon-180.png")}">{links}'
        f"{extra}{csslinks}</head>"
    )


def font_preload(lang, rel):
    return (f'<link rel="preload" href="{asset(lang, rel, "assets/fonts/fraunces-latin-800-normal.woff2")}" '
            'as="font" type="font/woff2" crossorigin>')


def header(lang, rel, prof, qvalue, switch_href):
    """Cabecera clasica: fila de pestanas, logo + formulario con botones grises de sistema."""
    s = STR[lang]
    gh = prof["links"]["github"]
    other = "en" if lang == "es" else "es"
    return f"""<nav class="gt" aria-label="{esc(s['nav_top'])}">
<div role="tablist" aria-label="{esc(s['tabs_label'])}">
<a role="tab" id="tab-todo" aria-controls="p-todo" href="#todo" data-tab="todo" aria-selected="true">{s['tab_all']}</a>
<a role="tab" id="tab-imagenes" aria-controls="p-imagenes" href="#imagenes" data-tab="imagenes" aria-selected="false">{s['tab_img']}</a>
<a role="tab" id="tab-codigo" aria-controls="p-codigo" href="#codigo" data-tab="codigo" aria-selected="false">{s['tab_code']}</a></div>
<a class="more" href="{href(lang, rel, lang, 'about')}">{esc(s['more_about'])}</a>
<span class="gr"><a href="{switch_href}" hreflang="{other}" lang="{other}">{esc(s['other_name'])}</a><a href="{esc(gh)}" rel="noopener">GitHub</a></span>
</nav>
<header class="top">
<a class="logo" href="{href(lang, rel, lang, '')}" aria-label="Cambeiro">{logo()}</a>
<form id="f" class="box" role="search" autocomplete="off">
<input id="q" name="q" type="search" value="{esc(qvalue)}" aria-label="{esc(s['search_label'])}" spellcheck="false" size="38">
<button type="submit" class="sb">{esc(s['search_btn'])}</button>
<button type="button" id="lucky" class="sb lucky">{esc(s['lucky'])}</button>
</form>
</header>"""


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
        ln.append(f'<a href="{asset(lang, rel, cvf(L, lang))}">{s["link_cv"]}</a>')
    return ln


PREVIEW = (480, 360)


def preview_path(lang, slug):
    """Miniatura = captura de la propia pagina interior (tools/make_previews.py)."""
    return f"assets/previews/{slug}-{lang}.webp"


def cover_of(lang, rel, p):
    """Captura de la pagina interior si existe; si no, la de la app real o la portada abstracta."""
    if os.path.exists(os.path.join(ROOT, preview_path(lang, p["slug"]))):
        return asset(lang, rel, preview_path(lang, p["slug"]))
    if p.get("shot"):
        return asset(lang, rel, p["shot"]["thumb"])
    return asset(lang, rel, f"assets/covers/{p['slug']}.svg")


def hay_of(p):
    return norm(" ".join([p["title"], p["kind"][LANGS[0]], p["kind"][LANGS[1]], p["summary"][LANGS[0]], p["summary"][LANGS[1]],
                          " ".join(p["stack"]), " ".join(p["features"][LANGS[0]]), " ".join(p["features"][LANGS[1]])]))


def kbytes(n):
    return max(1, round(n / 1024))


def result(lang, rel, p, prof, sizes):
    """Resultado al estilo de 2004: titulo azul subrayado, fragmento, URL verde - tamano - enlaces."""
    s = STR[lang]
    page = href(lang, rel, lang, f"p/{p['slug']}")
    hay = norm(" ".join([p["title"], p["kind"][lang], p["summary"][lang], " ".join(p["stack"]), " ".join(p["features"][lang])]))
    disp = f"{prof['site_host']}/{page_dir(lang, 'p/' + p['slug'])}/"
    sim = fill(s["related_q"], x=p["stack"][0])
    snippet = f"{esc(p['summary'][lang])} ... {esc(', '.join(p['stack'][:8]))}"
    sls = ""
    if p.get("featured"):
        cells = ""
        for (lab, desc), h in zip(p["sitelinks"][lang], p["sitelink_hrefs"]):
            target = esc(p["links"]["repo"]) if h == "repo" else page + h
            ext = ' rel="noopener"' if h == "repo" else ""
            cells += f'<div><a href="{target}"{ext}>{esc(lab)}</a><br><span>{esc(desc)}</span></div>'
        sls = f'<div class="sls">{cells}</div>'
    return f"""<article class="res" data-hay="{esc(hay)}">
<a class="th" href="{page}" tabindex="-1" aria-hidden="true"><img src="{cover_of(lang, rel, p)}" alt="" width="{PREVIEW[0]}" height="{PREVIEW[1]}" loading="lazy"></a>
<h2><a href="{page}" data-b>{esc(p['title'])} - {esc(p['kind'][lang])}</a></h2>
<p class="sn" data-b>{snippet}</p>
{sls}<p class="ul"><span class="a">{esc(disp)} - {sizes[(lang, p['slug'])]}k - </span><a class="fl" href="{esc(p['links']['repo'])}" rel="noopener">{esc(s['repo'])}</a> - <a class="fl" href="?q={quote(sim)}" data-q="{esc(sim)}">{esc(s['similar'])}</a></p>
</article>"""


def figure(lang, rel, p, prof):
    """Celda de busqueda de imagenes clasica: miniatura, nombre, dimensiones y URL."""
    s = STR[lang]
    page = href(lang, rel, lang, f"p/{p['slug']}")
    hay = norm(" ".join([p["title"], p["kind"][lang], p["summary"][lang], " ".join(p["stack"])]))
    sh = p.get("shot")
    thumb = sh["thumb"] if sh else f"assets/covers/{p['slug']}.svg"
    w, h = (400, 300) if not sh else (sh["w"], sh["h"])
    if os.path.exists(os.path.join(ROOT, preview_path(lang, p["slug"]))):
        thumb, (w, h) = preview_path(lang, p["slug"]), PREVIEW
    path = os.path.join(ROOT, thumb)
    dims = fill(s["sz_px"], w=w, h=h, k=kbytes(os.path.getsize(path)) if os.path.exists(path) else 1)
    return (f'<figure class="fig" data-hay="{esc(hay)}"><a href="{page}"><img src="{cover_of(lang, rel, p)}" alt="{esc(fill(s["cover_alt"], t=p["title"]))}" width="{PREVIEW[0]}" height="{PREVIEW[1]}" loading="lazy"></a>'
            f'<figcaption><a href="{page}" data-b>{esc(p["title"])}</a><span class="d">{esc(dims)}</span>'
            f'<span class="a">{esc(prof["site_host"])}</span></figcaption></figure>')


def code_row(lang, p):
    hay = norm(" ".join([p["title"], p["kind"][lang], p["summary"][lang], " ".join(p["stack"])]))
    repo = p["links"]["repo"]
    path = repo.replace("https://github.com/", "")
    return (f'<div class="code" data-hay="{esc(hay)}"><a href="{esc(repo)}" rel="noopener" data-b>{esc(path)}</a>'
            f'<p data-b>{esc(p["summary"][lang])}</p><p class="stk" data-b>{esc(" · ".join(p["stack"]))}</p></div>')


def ads(lang, rel, prof):
    """Columna de 'enlaces patrocinados': el perfil de Damian como anuncios (contacto, CV, LinkedIn)."""
    s, L = STR[lang], prof["links"]
    host = prof["site_host"]
    kw = dict(name=prof["name"], first=prof["first_name"])
    items = [
        (href(lang, rel, lang, "about"), "ad1", f"{host}/{page_dir(lang, 'about')}/", ""),
        (asset(lang, rel, cvf(L, lang)), "ad2", f"{host}/{cvf(L, lang)} - {file_kb(cvf(L, lang)).replace(' KB', 'k')}", ""),
        (f"mailto:{L['email']}", "ad3", L["email"], ""),
        (L["linkedin"], "ad4", L["linkedin"].replace("https://www.", ""), ' rel="noopener"'),
    ]
    out = ""
    for url, k, disp, ext in items:
        out += (f'<div class="ad"><p class="adt"><a href="{esc(url)}"{ext}>{esc(fill(s[k + "_t"], **kw))}</a></p>'
                f'<p>{esc(s[k + "_a"])}<br>{esc(s[k + "_b"])}</p><p class="au">{esc(disp)}</p></div>')
    return f'<aside class="ads" aria-label="{esc(s["ads_h"])}"><p class="adh">{esc(s["ads_h"])}</p>{out}</aside>'


def copybtn(lang, prof, cls):
    """Boton «Copiar correo»: mucha gente no tiene cliente de correo configurado, asi que el mailto no basta."""
    s = STR[lang]
    return (f'<button type="button" class="{cls}" data-copy="{esc(prof["links"]["email"])}" data-ok="{esc(s["copied"])}" '
            f'data-fail="{esc(s["copy_fail"])}">{esc(s["copy_mail"])}</button>')


def onebox(lang, rel, prof):
    """Ficha destacada (como los cuadros destacados del buscador clasico): quien es, rol, CV y contacto."""
    s, L = STR[lang], prof["links"]
    kw = dict(first=prof["first_name"])
    return (f'<section class="ob" id="ob" aria-label="{esc(prof["name"])}">'
            f'<h2><a href="{href(lang, rel, lang, "about")}">{esc(prof["name"])}</a> <span>- {esc(prof["role_short"][lang])}</span></h2>'
            f'<p>{esc(prof["intro"][lang])}</p>'
            f'<p class="obb"><a class="obtn" href="{asset(lang, rel, cvf(L, lang))}">{esc(s["ob_cv"])}</a>'
            f'<a class="obtn" href="mailto:{esc(L["email"])}">{esc(fill(s["ob_mail"], **kw))}</a>'
            f'{copybtn(lang, prof, "obtn")}'
            f'<a href="{href(lang, rel, lang, "about")}">{esc(fill(s["ob_more"], **kw))}</a></p><p class="cpst" role="status" aria-live="polite"></p></section>')


def cvf(L, lang):
    """Ruta del PDF del CV segun el idioma (cv_en si existe)."""
    return L.get("cv_en") if lang == "en" and L.get("cv_en") else L["cv"]


def priv(lang):
    """Aviso de privacidad de la analitica (solo si esta activa)."""
    return f'<p class="fn">{esc(STR[lang]["privacy"])}</p>' if ANALYTICS and not SUFFIX else ""


def classic_footer(lang, rel, prof, alt_href):
    s, L = STR[lang], prof["links"]
    nav = " - ".join([
        f'<a href="{href(lang, rel, lang, "about")}">{esc(s["util_about"])}</a>',
        f'<a href="{alt_href}" hreflang="{"en" if lang == "es" else "es"}">{esc(s["other_name"])}</a>',
        f'<a href="{esc(L["linkedin"])}" rel="noopener">{s["link_linkedin"]}</a>',
        f'<a href="mailto:{esc(L["email"])}">{s["link_email"]}</a>',
        f'<a href="{asset(lang, rel, cvf(L, lang))}">{s["link_cv"]}</a>',
        f'<a href="{esc(L["github"])}" rel="noopener">GitHub</a>'])
    return f"""<footer class="ft"><p class="fnav">{nav}</p>
<p class="cp">© 2026 {esc(prof['name'])}</p><p class="fn">{esc(s['footer_note'])}</p>{priv(lang)}</footer>"""


def home(lang, prof, projects, sizes):
    s = STR[lang]
    rel = ""
    qdef = fill(s["default_q"], name=prof["first_name"])
    alt_href = href(lang, rel, "en" if lang == "es" else "es", "")
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, "assets/buscador.css")]
    stop = sorted(set(norm(w) for w in s["stop"]) | set(norm(prof["name"]).split()))
    n = len(projects)
    cfg = {"stop": stop, "def": qdef, "one": s["bar_one"], "many": s["bar_many"], "tail": s["bar_tail"], "none": s["none_q"]}

    counts, shown = {}, {}
    for p in projects:
        for t in p["stack"]:
            k = t.lower()
            shown.setdefault(k, t)
            counts[k] = counts.get(k, 0) + 1
    rel_terms = [shown[k] for k in sorted(counts, key=lambda k: (-counts[k], k))[:8]]
    related = "".join(
        f'<li><a href="?q={quote(fill(s["related_q"], x=t))}" data-q="{esc(fill(s["related_q"], x=t))}">{esc(fill(s["related_q"], x=t))}</a></li>' for t in rel_terms
    )
    results = "".join(result(lang, rel, p, prof, sizes) for p in projects)
    figs = "".join(figure(lang, rel, p, prof) for p in projects)
    codes = "".join(code_row(lang, p) for p in projects)
    tips = "".join(f"<li>{esc(fill(t, name=prof['first_name']))}</li>" for t in s["none_tips"])
    L = prof["links"]
    cols = LOGO_COLORS[:5] + [LOGO_COLORS[5]] * 5 + LOGO_COLORS[6:]
    pager = (f'<div class="pager"><p class="pw" role="img" aria-label="{esc(s["pager_label"])}">'
             + "".join(f'<span aria-hidden="true" style="color:{c}">{ch}</span>' for ch, c in zip("Cambeiiiiiro", cols))
             + f'</p><p class="pn">{esc(s["pager_res"])} <b>1</b></p></div>')
    count0 = f'{fill(s["bar_many"], n=n)}'

    body = f"""<body>
<div class="sr">
{header(lang, rel, prof, qdef, alt_href)}
<section class="bar" aria-label="{esc(s['pager_note'])}"><b id="tabname">{s['tab_all']}</b><p id="cnt" class="cnt" aria-live="polite">{esc(count0)} <b>{esc(qdef)}</b>. {esc(s['bar_tail'])}</p></section>
<div class="cols">
<main data-tab="todo">
<h1 class="vh">{esc(fill(s['home_h1'], name=prof['name']))}</h1>
{onebox(lang, rel, prof)}
<p class="dyp"><span>{esc(s['didyou'])}</span> <a href="mailto:{esc(L['email'])}"><b><i>{esc(s['didyou_link'])}</i></b></a></p>
<div id="none" class="none" hidden><p id="nonetxt"></p><p>{esc(s['none_sug'])}</p><ul>{tips}</ul></div>
<section id="p-todo" role="tabpanel" aria-labelledby="tab-todo">{results}</section>
<section id="p-imagenes" class="igrid" role="tabpanel" aria-labelledby="tab-imagenes">{figs}</section>
<section id="p-codigo" role="tabpanel" aria-labelledby="tab-codigo">{codes}</section>
<section class="rel" id="rel"><h2>{esc(s['related'])}</h2><ul>{related}</ul></section>
{pager}
</main>
{ads(lang, rel, prof)}
</div>
{classic_footer(lang, rel, prof, alt_href)}
</div>
<script type="application/json" id="cfg">{json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="{asset(lang, rel, 'assets/buscador.js')}" defer></script>
<script src="{asset(lang, rel, 'assets/copiar.js')}" defer></script>
</body></html>"""
    desc = fill(s["meta_home"], name=prof["name"])
    title = f"{qdef} - Cambeiro"
    return head(lang, rel, title, desc, alts, css, font_preload(lang, rel)) + body


# ----------------------------------------------------------------------- Sobre mi
def render_cv(cv, terms=("python", "sql")):
    """Folio HTML con el texto real del CV; resalta terminos (como las copias en cache)."""
    pat = re.compile("(?i)(" + "|".join(re.escape(t) for t in terms) + ")")
    idx = {t.lower(): i for i, t in enumerate(terms)}

    def mark(text):
        parts = re.split(r"(<[^>]+>)", rich(text))
        return "".join(p if p.startswith("<") else pat.sub(lambda m: f'<mark class="m{idx[m.group(1).lower()]}">{m.group(1)}</mark>', p) for p in parts)

    out = [f'<p class="nm">{esc(cv["name"])}</p><p class="rl">{mark(cv["role"])}</p>'
           f'<p class="ct">{esc(cv["contact"])}</p><p class="lc">{esc(cv["loc"])}</p>']
    for sec in cv["sections"]:
        out.append(f'<section id="cv-{sec["id"]}" data-s="{sec["id"]}"><p class="h">{esc(sec["title"])}</p>')
        for b in sec["blocks"]:
            if "p" in b:
                out.append(f"<p>{mark(b['p'])}</p>")
            elif "row" in b:
                out.append(f'<p class="row"><span>{mark(b["row"][0])}</span><span>{esc(b["row"][1])}</span></p>')
            elif "ul" in b:
                out.append("<ul>" + "".join(f"<li>{mark(x)}</li>" for x in b["ul"]) + "</ul>")
            elif "sub" in b:
                out.append(f'<p class="sub">{esc(b["sub"])}</p>')
        out.append("</section>")
    return "".join(out)


def about_page(lang, prof, projects):
    s = STR[lang]
    rel = "about"
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, "assets/buscador.css"), asset(lang, rel, "assets/perfil.css")]
    other = "en" if lang == "es" else "es"
    L = prof["links"]
    cv_url = asset(lang, rel, cvf(L, lang))
    size = file_kb(cvf(L, lang))
    home_h = href(lang, rel, lang, "")
    cv = load("cv.json" if lang == "es" else "cv.en.json")

    path = ""
    for it in prof["path"][lang]:
        txt = f'<p class="sn">{esc(it["text"])}</p>' if it.get("text") else ""
        path += (f'<div class="tr" data-s="{it["s"]}"><p class="u">{esc(it["when"])}</p>'
                 f'<h3><a href="#cv-{it["s"]}">{esc(it["title"])}</a></h3>{txt}</div>')
    counts, shown = {}, {}
    for p in projects:
        for t in p["stack"]:
            k = t.lower()
            shown.setdefault(k, t)
            counts[k] = counts.get(k, 0) + 1
    tools = ""
    for key in sorted(counts, key=lambda k: (-counts[k], k))[:8]:
        t, k = shown[key], counts[key]
        q = fill(s["related_q"], x=t)
        c = s["n_proj_one"] if k == 1 else fill(s["n_proj_many"], n=k)
        tools += (f'<li><a class="rq" href="{home_h}?q={quote(q)}"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
                  f'<circle cx="10" cy="10" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15 15l6 6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'
                  f'<span>{esc(t.lower())} · {esc(c)}</span></a></li>')
    banner = fill(s["cache_banner"], url=cv_url, file=esc(os.path.basename(cvf(L, lang))), date=esc(fmt_date(lang, prof["cv_date"])))
    data = (f'data-terms="python,sql" data-label="{esc(s["terms_label"])}" data-ph="{esc(s["term_ph"])}" '
            f'data-rm="{esc(s["term_rm"])}" data-add="{esc(s["term_add"])}"')
    body = f"""<body class="ab">
<div class="split">
<div class="lft">
<header class="abar"><a class="logo sm" href="{home_h}" aria-label="Cambeiro">{logo()}</a>
<p class="nav"><a href="{home_h}">{esc(s['ab_back'])}</a><a href="{href(lang, rel, other, rel)}" hreflang="{other}" lang="{other}">{esc(s['other_name'])}</a></p></header>
<main>
<section class="hero" data-s="perfil"><h1>{esc(prof['name'])}</h1>
<p class="rl">{esc(prof['role_short'][lang])}. {esc(prof['location'][lang])}.</p>
<p class="in">{esc(prof['intro'][lang])}</p>
<p class="bs"><a class="pbtn p" href="{cv_url}" download>{esc(fill(s['dl_cv'], size=size))}</a><a class="pbtn" href="{esc(L['linkedin'])}" rel="noopener">{s['link_linkedin']}</a><a class="pbtn" href="mailto:{esc(L['email'])}">{s['link_email']}</a><a class="pbtn" href="{esc(L['github'])}" rel="noopener">GitHub</a></p></section>
<section class="blk"><h2>{esc(s['ab_path'])}</h2>{path}</section>
<section class="blk" data-s="tecnicas"><h2>{esc(s['ab_tools'])}</h2><p class="sn mut">{esc(s['ab_tools_p'])}</p><ul class="rels">{tools}</ul></section>
<section class="blk tr" data-s="idiomas"><h2>{esc(s['ab_lang'])}</h2><p class="sn">{esc(prof['languages'][lang])}</p></section>
<section class="dym"><p class="fr">{esc(s['didyou'])} <a href="mailto:{esc(L['email'])}">{esc(s['didyou_link'])}</a></p><p class="sn">{esc(s['ab_hire_p'])}</p>
<p class="sn eml"><a href="mailto:{esc(L['email'])}">{esc(L['email'])}</a></p>
<p class="bs"><a class="pbtn p" href="mailto:{esc(L['email'])}">{esc(s['ab_mail'])}</a>{copybtn(lang, prof, "pbtn")}<a class="pbtn" href="{esc(L['linkedin'])}" rel="noopener">{esc(s['ab_li'])}</a></p><p class="sn cpst" role="status" aria-live="polite"></p></section>
</main>
</div>
<aside class="stage" aria-label="{esc(s['folio_label'])}"><div class="sin">
<p class="banner">{banner}</p>
<div class="terms" {data} hidden></div>
<p class="bs"><a class="sbtn p" href="{cv_url}">{esc(s['open_pdf'])}</a><a class="sbtn" href="{cv_url}" download>{esc(fill(s['dl_pdf'], size=size))}</a></p>
<div class="paper"><article class="sheet" lang="{lang}" aria-label="{esc(s['folio_label'])}"><div class="cv">{render_cv(cv)}</div></article></div>
<p class="seecv"><a class="sbtn p" href="{cv_url}">{esc(s['see_cv'])}</a></p>
</div></aside>
</div>
<script src="{asset(lang, rel, 'assets/perfil.js')}" defer></script>
<script src="{asset(lang, rel, 'assets/copiar.js')}" defer></script>
</body></html>"""
    title = f"{prof['name']} - {s['about_kind']} - Cambeiro"
    return head(lang, rel, title, prof["bio"][lang], alts, css, font_preload(lang, rel)) + body


def project_extra(lang, prof, p, skin):
    """Pieles de tools/skins.py (reproductor, teletexto, hoja de calculo)."""
    s = STR[lang]
    rel = f"p/{p['slug']}"
    other = "en" if lang == "es" else "es"
    c = dict(lang=lang, s=s, slug=p["slug"], title=p["title"], kind=p["kind"][lang], summary=p["summary"][lang],
             feats=p["features"][lang], facts=p["facts"][lang], stack=p["stack"], note=p["note"][lang],
             repo=p["links"]["repo"], home=href(lang, rel, lang, ""), other=other,
             other_h=href(lang, rel, other, rel), name=prof["name"], author=prof["first_name"], initials=prof["initials"],
             asset_js=asset(lang, rel, "assets/reloc.js"), shot=(dict(src=asset(lang, rel, p["shot"]["full"]), w=p["shot"]["w"], h=p["shot"]["h"], alt=p["shot"]["alt"][lang], cap=p["shot"]["cap"][lang]) if p.get("shot") else None), asset_data=asset(lang, rel, "assets/reloc-data.js"), asset_tracker=asset(lang, rel, "assets/tracker.js"))
    alts = {l: absurl(l, rel) for l in LANGS}
    css = [asset(lang, rel, f"skins/{skin}.css")]
    return head(lang, rel, f"{p['title']} - {prof['name']} - Cambeiro", p["summary"][lang], alts, css) + EXTRA[skin](c)


def legalize(html, *langs):
    """Aviso de parodia en el pie de las paginas que no son la portada (la portada ya lo lleva)."""
    notes = "<br>".join(f'<span lang="{l}">{esc(STR[l]["footer_note"])}</span>' for l in langs)
    if ANALYTICS and not SUFFIX:
        notes += "<br>" + "<br>".join(f'<span lang="{l}">{esc(STR[l]["privacy"])}</span>' for l in langs)
    label = "Aviso legal" if langs == ("es",) else "Legal notice" if langs == ("en",) else "Aviso legal / Legal notice"
    bar = (f'<section class="legal" aria-label="{label}" style="margin:12px 0 0;padding:10px 12px;background:#fff;color:#595959;'
           f'font:12px/1.45 Arial,Helvetica,sans-serif;text-align:center;flex:1 0 100%">{notes}</section>')
    return html.replace("</body>", bar + "</body>", 1)


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
    """404 como pagina de resultados vacia del buscador (sirve desde cualquier ruta: rutas absolutas con base_path)."""
    bp = prof.get("base_path", "").rstrip("/")
    blocks = ""
    for l in LANGS:
        s = STR[l]
        tips = "".join(f"<li>{esc(fill(t, name=prof['first_name']))}</li>" for t in s["none_tips"])
        blocks += (f'<section class="none" lang="{l}"><h1>{esc(s["nf_title"])}</h1>'
                   f'<p>{esc(fill(s["none_q"], q="404"))}</p><p>{esc(s["nf_text"])}</p><p>{esc(s["none_sug"])}</p>'
                   f'<ul>{tips}</ul>'
                   f'<p class="dyp"><span>{esc(s["didyou"])}</span> <a href="{bp}{"/" if l == "es" else "/en/"}"><b><i>'
                   f'{esc(fill(s["default_q"], name=prof["first_name"]))}</i></b></a></p></section>')
    s = STR["es"]
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="robots" content="noindex"><title>404 - Cambeiro</title>
<link rel="icon" href="{FAVICON}"><link rel="apple-touch-icon" href="{bp}/assets/icon-180.png"><link rel="stylesheet" href="{bp}/assets/buscador.css"></head>
<body><div class="sr">
<nav class="gt" aria-label="{esc(s['nav_top'])}"><span></span><span class="gr"><a href="{bp}/" hreflang="es" lang="es">Español</a><a href="{bp}/en/" hreflang="en" lang="en">English</a></span></nav>
<header class="top"><a class="logo" href="{bp}/" aria-label="Cambeiro">{logo()}</a>
<form class="box" role="search" action="{bp}/" method="get"><input name="q" type="search" value="{esc(fill(s['default_q'], name=prof['first_name']))}" aria-label="{esc(s['search_label'])}" spellcheck="false" size="38"><button type="submit" class="sb">{esc(s['search_btn'])}</button></form></header>
<section class="bar" aria-label="{esc(s['pager_note'])}"><b>Web</b></section>
<main>{blocks}</main>
</div></body></html>"""


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
    global SITE, ANALYTICS
    prof = load("profile.json")
    code = (prof.get("analytics") or {}).get("goatcounter", "").strip().lower()
    if code and not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,30}", code):
        sys.exit(f"analytics.goatcounter no valido: {code!r}")
    ANALYTICS = code
    projects = load("projects.json")
    SITE = f"https://{prof['site_host']}{prof.get('base_path', '').rstrip('/')}"
    for p in projects:
        if not p.get("shot"):
            write(f"assets/covers/{p['slug']}.svg", cover_svg(p["cover"], p["slug"]))
    sizes = {}
    for lang in LANGS:
        for p in projects:
            html = legalize(project_page(lang, prof, p), lang)
            sizes[(lang, p["slug"])] = kbytes(len(html.encode("utf-8")))
            write(posixpath.join(page_dir(lang, f"p/{p['slug']}"), "index.html"), html)
    for lang in LANGS:
        write(posixpath.join(page_dir(lang, "about"), "index.html"), legalize(about_page(lang, prof, projects), lang))
        write(posixpath.join(page_dir(lang, ""), "index.html"), home(lang, prof, projects, sizes))
    write("404.html", legalize(not_found(prof), "es", "en"))
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
