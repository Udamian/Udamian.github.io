"""Piel «reloc»: RelocationDevs como un buscador de los 2000 (HTML estatico + assets/reloc.js).

Los datos son los reales del proyecto (ver tools/prep_reloc.py). La pagina es una sola
URL con varias vistas por hash (#/b?q=..., #/c/12, #/adv, #/cmp/1,2, #/map, #/sal, #/about).
Todo el HTML estatico (portada, formularios, "Acerca de") se genera aqui; el JS solo
calcula resultados y dibuja las vistas dinamicas.
"""
import json
import os
from html import escape as esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "data", "relocation.json"), encoding="utf-8"))

LOGO_PIN = (
    '<svg class="pin" viewBox="0 0 512 512" width="{w}" height="{w}" aria-hidden="true" fill="none">'
    '<rect width="512" height="512" rx="100" fill="#111"/>'
    '<path d="M256 60C178.7 60 116 122.7 116 200C116 305 256 452 256 452C256 452 396 305 396 200C396 122.7 333.3 60 256 60Z" stroke="#F5F5F7" stroke-width="20" stroke-linejoin="round"/>'
    '<circle cx="256" cy="200" r="80" stroke="#F5F5F7" stroke-width="12"/>'
    '<path d="M256 120V280M176 200H336" stroke="#8E8E93" stroke-width="8"/>'
    '<path d="M230 175L210 200L230 225M282 175L302 200L282 225" stroke="#F5F5F7" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)
LETTER_COLORS = ["#4a90d9", "#e8593c", "#2ecc71", "#f39c12", "#9b59b6"]  # los de comparison.py


def wordmark():
    out = []
    for i, ch in enumerate("Relocation"):
        col = "#1c1c1e" if i % 2 == 0 else LETTER_COLORS[(i // 2) % len(LETTER_COLORS)]
        out.append(f'<span style="color:{col}">{ch}</span>')
    return "".join(out) + '<span class="dv">Devs</span>'


R = {
    "es": {
        "skip": "Saltar al contenido", "tag": "by a Cambeiro", "ph": "ciudad, país o región…", "search": "Buscar ciudad", "lucky": "Voy a tener suerte",
        "all": "Todo el mundo", "regions": ["Europa", "América", "Asia", "Oceanía", "Oriente Medio", "África", "Otras"],
        "adv": "Búsqueda avanzada", "cmp": "Comparar ciudades", "map": "Mapa de ciudades", "sal": "Salarios dev",
        "about": "Acerca de RelocationDevs", "in": "RelocationDevs en", "pop": "Búsquedas populares",
        "pop_l": ["Houston", "Zurich", "Lisbon", "Spain", "Germany", "Singapore"],
        "foot": "Maqueta estática con datos reales del proyecto", "repo": "Código",
        "back": "← Resultados de Cambeiro", "lang": "English", "region": "Región", "words": "Con las palabras",
        "min_net": "Salario neto mínimo (€/año)", "max_rent": "Alquiler máximo (€/mes)", "max_tax": "Impuestos máximos (%)",
        "weights": "Importancia de cada factor", "w_p": "Poder adquisitivo", "w_j": "Mercado laboral",
        "w_q": "Calidad de vida", "w_t": "Impuestos bajos", "reset": "Valores del proyecto",
        "w_note": "Con los valores por defecto (3 · 2,5 · 2,5 · 2) la puntuación es idéntica a la de la app. Se normalizan para sumar 1.",
        "adv_h": "Búsqueda avanzada", "adv_go": "Buscar con estos criterios",
        "cmp_h": "Comparar ciudades", "cmp_p": "Elige de 2 a 3 ciudades (empieza a escribir y elige de la lista).",
        "cmp_ph": "Ciudad {n}", "map_h": "Mapa de ciudades", "sal_h": "Salarios de desarrolladores",
        "sal_country": "País", "sal_role": "Rol", "sal_all": "Todos los roles",
        "about_h": "Acerca de RelocationDevs", "what": "Qué es", "mods": "Módulos de la app original",
        "facts_h": "Datos clave", "stack_h": "Tecnologías", "limits": "Límites (dichos con claridad)",
        "static_h": "Qué hay y qué no hay en esta maqueta", "links_h": "Enlaces",
        "nodemo": "La demo en línea de la app original ya no está disponible (han caducado claves de API). Esta maqueta estática, con los datos y la fórmula reales, la sustituye.",
        "static_yes": "Sí: ranking, búsqueda con pesos propios, comparador, mapa y salarios, con los datos y la fórmula reales.",
        "static_no": "El salario medio del dataset de costes de vida es por país (igual para todas sus ciudades), no por ciudad. No incluye: el modelo de predicción salarial (Gradient Boosting), el asistente de 3 pasos con radar ni el informe PDF. Eso solo está en el repositorio.",
        "noscript": "Sin JavaScript solo se muestra el ranking base. Estas son las 10 primeras ciudades por puntuación:",
        "js": {
            "res": "Resultados {a} - {b} de aproximadamente {n}", "secs": "({t} segundos)", "cities": "Ciudades",
            "none": "No se ha encontrado ninguna ciudad para «{q}».", "none_tip": "Sugerencias: prueba con menos palabras, con el país (en inglés o español: España, Germany…) o quita filtros.",
            "avg": "Salario medio", "net": "neto estimado", "rent": "alquiler", "mo": "/mes", "tax": "impuestos",
            "score": "Puntuación", "custom": "Puntuación personalizada", "cmp_add": "Comparar", "on_map": "En el mapa",
            "similar": "Similares", "prev": "Anterior", "next": "Siguiente", "sort": "Ordenar por", "page": "Página",
            "sort_l": {"score": "puntuación", "net": "salario neto", "pp": "poder adquisitivo", "rent": "alquiler (bajo)", "sal": "salario medio"},
            "crumb": "relocationdevs › ciudades", "w_on": "Pesos propios: poder adq. {p} · mercado {j} · calidad {q} · impuestos {t}",
            "m": {"score": "Puntuación de reubicación", "sal": "Salario medio (€/año)", "net": "Salario neto estimado (€/año)",
                  "rent": "Alquiler (€/mes)", "tax": "Impuestos (%)", "col": "Coste de vida (índice)", "pp": "Poder adquisitivo (neto ÷ coste de vida)",
                  "qol": "Calidad de vida", "job": "Mercado laboral", "sav": "Ahorro anual estimado (30 % del neto)", "ppi": "Poder adquisitivo (índice)"},
            "rank": "Puesto {r} de {n} por puntuación", "how": "Cómo sale la puntuación", "total": "Total",
            "lower": "(mejor si es menor)", "best": "mejor", "sim_h": "Ciudades parecidas", "sal_link": "Salarios de desarrolladores en {c}",
            "no_geo": "Esta ciudad no tiene coordenadas en los datos.", "see_map": "Ver en el mapa", "add_cmp": "Añadir a comparar",
            "cmp_need": "Añade al menos dos ciudades para ver la comparación.", "metric": "Métrica",
            "map_n": "{g} de {n} ciudades tienen coordenadas en los datos del proyecto; el resto no aparece en el mapa.",
            "map_top": "Las 10 mejores del mapa", "map_leg": "Puntuación", "map_pick": "Pulsa un punto para ver la ciudad.",
            "n_resp": "{n} respuestas", "median": "Mediana", "iqr": "Rango intercuartílico (25 %–75 %)", "few": "Menos de 10 respuestas para este rol en {c}: se muestran todos los roles.",
            "sal_note": "Son medianas de la encuesta (Stack Overflow 2023), no la predicción del modelo ML de la app (MAE 29.022 €, R² 0,53).",
            "top_c": "Países con mayor mediana (mínimo 10 respuestas)", "see_cities": "Ver las {n} ciudades de {c}", "no_cities": "No hay ciudades de {c} en el dataset de costes de vida.",
            "survey": "encuesta", "country": "País", "mid": "Mediana",
        },
    },
    "en": {
        "skip": "Skip to content", "tag": "by a Cambeiro", "ph": "city, country or region…", "search": "Search cities", "lucky": "I'm feeling lucky",
        "all": "Worldwide", "regions": ["Europe", "Americas", "Asia", "Oceania", "Middle East", "Africa", "Other"],
        "adv": "Advanced search", "cmp": "Compare cities", "map": "City map", "sal": "Dev salaries",
        "about": "About RelocationDevs", "in": "RelocationDevs in", "pop": "Popular searches",
        "pop_l": ["Houston", "Zurich", "Lisbon", "Spain", "Germany", "Singapore"],
        "foot": "Static mock-up with the project's real data", "repo": "Code",
        "back": "← Cambeiro results", "lang": "Español", "region": "Region", "words": "With the words",
        "min_net": "Minimum net salary (€/year)", "max_rent": "Maximum rent (€/month)", "max_tax": "Maximum tax (%)",
        "weights": "How much each factor matters", "w_p": "Purchasing power", "w_j": "Job market",
        "w_q": "Quality of life", "w_t": "Low taxes", "reset": "Project defaults",
        "w_note": "With the defaults (3 · 2.5 · 2.5 · 2) the score is identical to the app's. Weights are normalised to sum to 1.",
        "adv_h": "Advanced search", "adv_go": "Search with these criteria",
        "cmp_h": "Compare cities", "cmp_p": "Pick 2 or 3 cities (start typing and choose from the list).",
        "cmp_ph": "City {n}", "map_h": "City map", "sal_h": "Developer salaries",
        "sal_country": "Country", "sal_role": "Role", "sal_all": "All roles",
        "about_h": "About RelocationDevs", "what": "What it is", "mods": "Modules of the original app",
        "facts_h": "Key facts", "stack_h": "Tech stack", "limits": "Limits (stated plainly)",
        "static_h": "What this mock-up has and what it doesn't", "links_h": "Links",
        "nodemo": "The original app's online demo is no longer available (some API keys expired). This static mock-up, with the real data and formula, replaces it.",
        "static_yes": "Yes: ranking, search with your own weights, comparison, map and salaries, using the real data and formula.",
        "static_no": "The average salary in the cost-of-living dataset is per country (the same for every city in it), not per city. Not included: the salary prediction model (Gradient Boosting), the 3-step finder with radar, or the PDF report. Those only exist in the repository.",
        "noscript": "Without JavaScript only the base ranking is shown. These are the top 10 cities by score:",
        "js": {
            "res": "Results {a} - {b} of about {n}", "secs": "({t} seconds)", "cities": "Cities",
            "none": "No city found for “{q}”.", "none_tip": "Tips: try fewer words, a country name (English or Spanish: Spain, España…) or remove filters.",
            "avg": "Average salary", "net": "est. net", "rent": "rent", "mo": "/mo", "tax": "tax",
            "score": "Score", "custom": "Custom score", "cmp_add": "Compare", "on_map": "On the map",
            "similar": "Similar", "prev": "Previous", "next": "Next", "sort": "Sort by", "page": "Page",
            "sort_l": {"score": "score", "net": "net salary", "pp": "purchasing power", "rent": "rent (low)", "sal": "average salary"},
            "crumb": "relocationdevs › cities", "w_on": "Own weights: purchasing power {p} · job market {j} · quality of life {q} · taxes {t}",
            "m": {"score": "Relocation score", "sal": "Average salary (€/year)", "net": "Estimated net salary (€/year)",
                  "rent": "Rent (€/month)", "tax": "Tax (%)", "col": "Cost of living (index)", "pp": "Purchasing power (net ÷ cost of living)",
                  "qol": "Quality of life", "job": "Job market", "sav": "Estimated annual savings (30% of net)", "ppi": "Purchasing power (index)"},
            "rank": "Rank {r} of {n} by score", "how": "How the score is made", "total": "Total",
            "lower": "(lower is better)", "best": "best", "sim_h": "Similar cities", "sal_link": "Developer salaries in {c}",
            "no_geo": "This city has no coordinates in the data.", "see_map": "See on the map", "add_cmp": "Add to compare",
            "cmp_need": "Add at least two cities to see the comparison.", "metric": "Metric",
            "map_n": "{g} of {n} cities have coordinates in the project's data; the rest are not on the map.",
            "map_top": "Top 10 on the map", "map_leg": "Score", "map_pick": "Click a dot to see the city.",
            "n_resp": "{n} responses", "median": "Median", "iqr": "Interquartile range (25%–75%)", "few": "Fewer than 10 responses for this role in {c}: showing all roles.",
            "sal_note": "These are survey medians (Stack Overflow 2023), not the app's ML model prediction (MAE €29,022, R² 0.53).",
            "top_c": "Countries with the highest median (at least 10 responses)", "see_cities": "See the {n} cities in {c}", "no_cities": "There are no cities for {c} in the cost-of-living dataset.",
            "survey": "survey", "country": "Country", "mid": "Median",
        },
    },
}


def fmt(lang, v):
    s = f"{v:,.0f}"
    return s.replace(",", ".") if lang == "es" else s


def top10():
    rows = []
    for c in DATA["cities"]:
        sc = c[7] * .30 + c[9] * .25 + c[8] * .25 + max(0, 100 - c[5]) * .20
        rows.append((sc, c[0], c[1]))
    rows.sort(reverse=True)
    return rows[:10]


def form(prefix, t, home):
    opts = f'<option value="-1">{esc(t["all"])}</option>' + "".join(
        f'<option value="{i}">{esc(n)}</option>' for i, n in enumerate(t["regions"]))
    reg = (f'<select id="{prefix}r" aria-label="{esc(t["region"])}">{opts}</select>' if not home else "")
    return (f'<form id="{prefix}f" class="sf" role="search" autocomplete="off">'
            f'<input id="{prefix}q" type="search" placeholder="{esc(t["ph"])}" aria-label="{esc(t["ph"])}" spellcheck="false">{reg}'
            f'<button type="submit" class="b">{esc(t["search"])}</button></form>')


def reloc(c):
    lang, s = c["lang"], c["s"]
    t = R[lang]
    meta = DATA["meta"]
    n_c, n_geo = meta["n_cities"], meta["n_geo"]
    radios = f'<label><input type="radio" name="hr" value="-1" checked> {esc(t["all"])}</label>' + "".join(
        f'<label><input type="radio" name="hr" value="{i}"> {esc(n)}</label>' for i, n in enumerate(t["regions"][:3]))
    pops = " · ".join(f'<a href="#/b?q={esc(x)}">{esc(x)}</a>' for x in t["pop_l"])
    nav = (f'<a href="#/adv">{esc(t["adv"])}</a><a href="#/cmp/">{esc(t["cmp"])}</a><a href="#/map">{esc(t["map"])}</a>'
           f'<a href="#/sal">{esc(t["sal"])}</a><a href="#/about">{esc(t["about"])}</a>')
    util = (f'<a href="{c["home"]}">{esc(t["back"])}</a><a href="{c["other_h"]}" hreflang="{c["other"]}" lang="{c["other"]}">{esc(t["lang"])}</a>'
            f'<a href="{esc(c["repo"])}" rel="noopener">GitHub</a>')
    foot = (f'<footer class="ft"><p><a href="#/adv">{esc(t["adv"])}</a> · <a href="#/about">{esc(t["about"])}</a> · '
            f'<a href="{esc(c["repo"])}" rel="noopener">{esc(t["repo"])}</a> · '
            f'<a href="{c["home"]}">{esc(t["back"])}</a></p>'
            f'<p class="sm">{esc(t["foot"])} · © 2026 {esc(c["name"])} · {n_c} {"ciudades" if lang == "es" else "cities"}</p></footer>')
    wsl = "".join(
        f'<label class="wr"><span>{esc(t[k])}</span><input type="range" id="w{k[2]}" min="0" max="10" step="0.5" value="{v}">'
        f'<output for="w{k[2]}">{v}</output></label>'
        for k, v in (("w_p", 3), ("w_j", 2.5), ("w_q", 2.5), ("w_t", 2)))
    ropt = f'<option value="-1">{esc(t["all"])}</option>' + "".join(
        f'<option value="{i}">{esc(n)}</option>' for i, n in enumerate(t["regions"]))
    mods = "".join(f"<li>{esc(x)}</li>" for x in c["feats"])
    facts = "".join(f"<li>{esc(x)}</li>" for x in c["facts"])
    chips = "".join(f"<li>{esc(x)}</li>" for x in c["stack"])
    ns = "".join(f"<li>{esc(n)}, {esc(k)} — {sc:.1f}</li>" for sc, n, k in top10())
    sh = c.get("shot")
    shot = (f'<figure class="shot"><img src="{esc(sh["src"])}" alt="{esc(sh["alt"])}" width="{sh["w"]}" height="{sh["h"]}" loading="lazy"><figcaption>{esc(sh["cap"])}</figcaption></figure>' if sh else "")
    jt = json.dumps(t["js"], ensure_ascii=False).replace("</", "<\\/")
    return f"""<body class="skin-reloc"><a class="skip" href="#main">{esc(t['skip'])}</a>
<div class="rl">
<nav class="ut" aria-label="Links">{util}</nav>
<header id="hd" class="hd" hidden><a class="lg" href="#/" aria-label="RelocationDevs">{LOGO_PIN.format(w=34)}<span class="wm">{wordmark()}</span></a>{form('h', t, False)}
<nav class="mn" aria-label="Menu">{nav}</nav></header>
<main id="main" tabindex="-1">
<h1 class="sr">RelocationDevs</h1>
<section id="v-home" class="view home"><div class="big"><div class="lgb">{LOGO_PIN.format(w=64)}<span class="wm big">{wordmark()}</span></div>
<p class="by">{esc(t['tag'])}</p></div>
{form('p', t, True)}
<p class="act"><button type="button" id="lucky" class="b alt">{esc(t['lucky'])}</button></p>
<p class="rad" role="group" aria-label="{esc(t['region'])}">{radios}</p>
<p class="lk">{nav}</p>
<p class="pp">{esc(t['pop'])}: {pops}</p>
<p class="inl">{esc(t['in'])}: <a href="{c['other_h']}" hreflang="{c['other']}" lang="{c['other']}">{esc(t['lang'])}</a></p>
<noscript><p>{esc(t['noscript'])}</p><ol>{ns}</ol></noscript></section>

<section id="v-res" class="view" hidden><div class="bar"><b>{esc(t['js']['cities'])}</b><span id="rc"></span></div>
<div id="rn" class="note" hidden></div><div id="rs"></div></section>

<section id="v-city" class="view" hidden><div id="cy"></div></section>

<section id="v-adv" class="view" hidden><div class="bar"><b>{esc(t['adv_h'])}</b></div>
<form id="af" class="af" autocomplete="off"><table><tbody>
<tr><th scope="row"><label for="aq">{esc(t['words'])}</label></th><td><input id="aq" type="text" spellcheck="false"></td></tr>
<tr><th scope="row"><label for="ar">{esc(t['region'])}</label></th><td><select id="ar">{ropt}</select></td></tr>
<tr><th scope="row"><label for="an">{esc(t['min_net'])}</label></th><td><input id="an" type="number" min="0" step="1000" inputmode="numeric"></td></tr>
<tr><th scope="row"><label for="am">{esc(t['max_rent'])}</label></th><td><input id="am" type="number" min="0" step="100" inputmode="numeric"></td></tr>
<tr><th scope="row"><label for="at">{esc(t['max_tax'])}</label></th><td><input id="at" type="number" min="0" max="100" step="1" inputmode="numeric"></td></tr>
<tr><th scope="row">{esc(t['weights'])}</th><td>{wsl}<p class="sm">{esc(t['w_note'])}</p></td></tr>
</tbody></table><p><button type="submit" class="b">{esc(t['adv_go'])}</button> <button type="button" id="areset" class="b alt">{esc(t['reset'])}</button></p></form></section>

<section id="v-cmp" class="view" hidden><div class="bar"><b>{esc(t['cmp_h'])}</b></div><p class="sm">{esc(t['cmp_p'])}</p>
<form id="cf" class="cf" autocomplete="off">{''.join(f'<input list="dl" id="c{i}" placeholder="{esc(t["cmp_ph"].format(n=i + 1))}" aria-label="{esc(t["cmp_ph"].format(n=i + 1))}">' for i in range(3))}
<datalist id="dl"></datalist></form><div id="cp"></div></section>

<section id="v-map" class="view" hidden><div class="bar"><b>{esc(t['map_h'])}</b></div>
<p class="sm">{esc(t['js']['map_n'].format(g=n_geo, n=n_c))}</p>
<p class="rad" role="group" aria-label="{esc(t['region'])}" id="mrad"></p>
<div class="mapw"><svg id="mp" viewBox="0 15 360 125" role="img" aria-label="{esc(t['map_h'])}"></svg></div>
<div id="mi" class="mi" aria-live="polite">{esc(t['js']['map_pick'])}</div><div id="mt"></div></section>

<section id="v-sal" class="view" hidden><div class="bar"><b>{esc(t['sal_h'])}</b></div>
<form class="cf" onsubmit="return false"><label>{esc(t['sal_country'])} <select id="sc"></select></label>
<label>{esc(t['sal_role'])} <select id="sr"></select></label></form><div id="so"></div></section>

<section id="v-about" class="view" hidden><div class="bar"><b>{esc(t['about_h'])}</b></div>
<div class="ab"><p class="lead">{esc(c['summary'])}</p>{shot}
<h2>{esc(t['facts_h'])}</h2><ul>{facts}</ul>
<h2>{esc(t['mods'])}</h2><ul>{mods}</ul>
<h2>{esc(t['stack_h'])}</h2><ul class="chips">{chips}</ul>
<h2>{esc(t['limits'])}</h2><p>{esc(c['note'])}</p>
<h2>{esc(t['static_h'])}</h2><p>{esc(t['static_yes'])}</p><p>{esc(t['static_no'])}</p>
<h2>{esc(t['links_h'])}</h2><p>{esc(t['nodemo'])}</p><p><a class="btn" href="{esc(c['repo'])}" rel="noopener">{esc(s['btn_repo'])}</a></p></div></section>
</main>{foot}
<div id="live" class="sr" aria-live="polite"></div></div>
<script>window.RT={jt};window.RM={{lang:{json.dumps(lang)},about:{json.dumps(t['about'])},reg:{json.dumps(t['regions'], ensure_ascii=False)},all:{json.dumps(t['all'])},w:{{p:{json.dumps(t['w_p'])},j:{json.dumps(t['w_j'])},q:{json.dumps(t['w_q'])},t:{json.dumps(t['w_t'])}}},role_all:{json.dumps(t['sal_all'])}}};</script>
<script src="{c['asset_data']}"></script><script src="{c['asset_js']}"></script>
</body></html>"""
