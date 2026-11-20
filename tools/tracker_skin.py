"""Piel «tracker»: Job Tracker como un programa de escritorio clasico (HTML estatico + assets/tracker.js).

Los datos son de ejemplo y ficticios (data/tracker.json): la app real guarda candidaturas
personales, que no se publican. Todo el HTML estatico se genera aqui; el JS calcula KPIs,
estancados, embudo y graficos y permite anadir, mover y borrar en memoria.
"""
import json
import os
from html import escape as esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "data", "tracker.json"), encoding="utf-8"))

ICON = ('<svg class="ic" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M3 4h18l-7 8v6l-4 2v-8z" fill="#7fd0ff" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>')

K = {
    "es": {
        "skip": "Saltar al contenido", "title": "Job Tracker", "sample": "Datos de ejemplo",
        "t_list": "Candidaturas", "t_stats": "Estadísticas", "t_about": "Acerca de",
        "tabs_aria": "Secciones", "links_aria": "Enlaces", "back": "Resultados", "repo": "Código", "lang": "English", "close": "Cerrar y volver a los resultados",
        "new": "Nueva candidatura", "ph": "Empresa · Puesto @estado", "save": "Guardar", "hint": "Ejemplo: Stripe · Backend Python @entrevista",
        "csv": "CSV", "txt": "TXT", "reset": "Restaurar ejemplo",
        "about_h": "Acerca de Job Tracker", "what": "Qué hace", "facts_h": "Datos clave", "stack_h": "Tecnologías", "limits": "Límites (dichos con claridad)",
        "mock_h": "Qué es esta maqueta", "links_h": "Enlaces",
        "mock_p": "Un programa de escritorio de otra época que reproduce la app: añadir candidaturas en una línea, estados, estancados, KPIs y gráficos, con la misma lógica de la app (tasas de respuesta, embudo, «Sin respuesta» tras 21 días).",
        "mock_data": "Los datos son de ejemplo, con empresas inventadas: la app real guarda candidaturas personales y no se publican. Los cambios que hagas aquí solo viven en esta pestaña.",
        "mock_no": "No incluye: la API de FastAPI, la base de datos PostgreSQL, los filtros por modalidad y versión del CV ni la edición completa de cada campo. Eso solo está en el repositorio.",
        "nodemo": "No hay demo en línea de la app original: necesita su API y una base de datos.",
        "noscript": "Sin JavaScript solo se muestra la lista de ejemplo:",
        "foot": "Maqueta estática con datos de ejemplo",
    },
    "en": {
        "skip": "Skip to content", "title": "Job Tracker", "sample": "Sample data",
        "t_list": "Applications", "t_stats": "Statistics", "t_about": "About",
        "tabs_aria": "Sections", "links_aria": "Links", "back": "Results", "repo": "Code", "lang": "Español", "close": "Close and go back to the results",
        "new": "New application", "ph": "Company · Role @status", "save": "Save", "hint": "Example: Stripe · Python Backend @interview",
        "csv": "CSV", "txt": "TXT", "reset": "Restore sample",
        "about_h": "About Job Tracker", "what": "What it does", "facts_h": "Key facts", "stack_h": "Technologies", "limits": "Limits (stated plainly)",
        "mock_h": "What this mock-up is", "links_h": "Links",
        "mock_p": "A desktop program from another era that reproduces the app: add applications in one line, statuses, stalled ones, KPIs and charts, with the app's own logic (response rates, funnel, “No response” after 21 days).",
        "mock_data": "The data is sample data with made-up companies: the real app stores personal applications and they are not published. Changes you make here only live in this tab.",
        "mock_no": "Not included: the FastAPI API, the PostgreSQL database, the filters by modality and CV version, or full editing of every field. That is only in the repository.",
        "nodemo": "There is no online demo of the original app: it needs its API and a database.",
        "noscript": "Without JavaScript only the sample list is shown:",
        "foot": "Static mock-up with sample data",
    },
}

J = {
    "es": {
        "st": {"enviada": "Enviada", "sinresp": "Sin respuesta", "contactado": "Contactado", "entrevista": "Entrevista", "rechazada": "Rechazada"},
        "all": "Todas", "folders": "Carpetas", "ty": {"backend": "Backend", "analyst": "Data Analyst", "engineer": "Data Engineer", "other": "Otro"},
        "mo": {"r": "Remoto", "h": "Híbrido", "p": "Presencial", "-": "—"},
        "cols": ["Empresa", "Puesto", "Tipo", "Modalidad", "Estado", "Fecha", "Días"], "d1": "día", "dn": "días",
        "stale_h": "Estancados", "stale_p": "Más de {n} días sin novedades", "stale_none": "Nada estancado: todas las candidaturas tienen novedades recientes.",
        "follow": "Hacer seguimiento", "reject": "Rechazar", "view": "Ver", "goal_h": "Objetivos", "today": "Hoy", "week": "Esta semana", "goal_of": "meta",
        "k": ["Total", "Hoy", "Esta semana", "Respuestas", "Contactadas", "Entrevistas", "Rechazadas", "Tasa respuesta", "Tasa entrevista"],
        "search": "Buscar empresa o puesto…", "search_l": "Buscar", "view_l": "Vista", "tbl": "Tabla", "kan": "Kanban", "empty": "No hay candidaturas con ese filtro.",
        "pick": "Selecciona una candidatura para ver su detalle.", "dt_h": "Detalle", "applied": "Enviada el", "news": "Última novedad", "ago": "hace {n} días", "today_l": "hoy",
        "type_l": "Tipo", "mode_l": "Modalidad", "move": "Mover a", "del": "Borrar", "sin_note": "«Sin respuesta» no se pone a mano: la app la asigna tras 21 días sin novedades.",
        "added": "Añadida: {co}", "deleted": "Borrada: {co}", "moved": "{co} → {st}", "followed": "Seguimiento hecho: {co}", "restored": "Datos de ejemplo restaurados", "exported": "Archivo generado",
        "status": "{n} candidaturas · {s} estancadas", "folder_n": "{n} en {f}",
        "c1": "Ritmo de postulaciones", "c1s": "Candidaturas por semana", "c2": "Embudo de selección", "c2s": "Fase máxima alcanzada",
        "c3": "Eficacia por tipo de puesto", "c3s": "Porcentaje de candidaturas con respuesta", "f": ["Enviadas", "Contactadas", "Entrevistas", "Rechazadas"],
        "resp": "{a} de {b}", "nodata": "Sin datos todavía", "wk": "Semana del {d}",
        "ex": "candidaturas", "head": ["empresa", "puesto", "tipo", "modalidad", "estado", "fecha"],
    },
    "en": {
        "st": {"enviada": "Sent", "sinresp": "No response", "contactado": "Contacted", "entrevista": "Interview", "rechazada": "Rejected"},
        "all": "All", "folders": "Folders", "ty": {"backend": "Backend", "analyst": "Data Analyst", "engineer": "Data Engineer", "other": "Other"},
        "mo": {"r": "Remote", "h": "Hybrid", "p": "On-site", "-": "—"},
        "cols": ["Company", "Role", "Type", "Modality", "Status", "Date", "Days"], "d1": "day", "dn": "days",
        "stale_h": "Stalled", "stale_p": "More than {n} days without news", "stale_none": "Nothing stalled: every application has recent news.",
        "follow": "Follow up", "reject": "Reject", "view": "View", "goal_h": "Goals", "today": "Today", "week": "This week", "goal_of": "goal",
        "k": ["Total", "Today", "This week", "Responses", "Contacted", "Interviews", "Rejected", "Response rate", "Interview rate"],
        "search": "Search company or role…", "search_l": "Search", "view_l": "View", "tbl": "Table", "kan": "Kanban", "empty": "No applications match that filter.",
        "pick": "Select an application to see its details.", "dt_h": "Details", "applied": "Sent on", "news": "Last news", "ago": "{n} days ago", "today_l": "today",
        "type_l": "Type", "mode_l": "Modality", "move": "Move to", "del": "Delete", "sin_note": "“No response” cannot be set by hand: the app assigns it after 21 days without news.",
        "added": "Added: {co}", "deleted": "Deleted: {co}", "moved": "{co} → {st}", "followed": "Follow-up done: {co}", "restored": "Sample data restored", "exported": "File generated",
        "status": "{n} applications · {s} stalled", "folder_n": "{n} in {f}",
        "c1": "Application pace", "c1s": "Applications per week", "c2": "Hiring funnel", "c2s": "Furthest stage reached",
        "c3": "Effectiveness by role type", "c3s": "Share of applications that got a response", "f": ["Sent", "Contacted", "Interviews", "Rejected"],
        "resp": "{a} of {b}", "nodata": "No data yet", "wk": "Week of {d}",
        "ex": "applications", "head": ["company", "role", "type", "modality", "status", "date"],
    },
}


def lis(items):
    return "".join(f"<li>{esc(x)}</li>" for x in items)


def tracker(c):
    lang, s = c["lang"], c["s"]
    t, jj = K[lang], J[lang]
    stat = {"enviada": jj["st"]["enviada"], "contactado": jj["st"]["contactado"], "entrevista": jj["st"]["entrevista"], "rechazada": jj["st"]["rechazada"]}
    ns = "".join(
        f"<tr><td>{esc(i['co'])}</td><td>{esc(i['role'])}</td><td>{esc(stat[i['st']])}</td></tr>" for i in DATA["items"])
    jt = json.dumps({"t": jj, "lang": lang, "items": DATA["items"]}, ensure_ascii=False).replace("</", "<\\/")
    tabs = "".join(
        f'<button type="button" role="tab" id="t-{k}" aria-controls="pn-{k}" aria-selected="{"true" if k == "list" else "false"}" data-tab="{k}"{"" if k == "list" else " tabindex=-1"}>{esc(t["t_" + k])}</button>'
        for k in ("list", "stats", "about"))
    kp = "".join(f'<div class="kp"><span class="kl">{esc(x)}</span><b class="kv" id="k{i}">–</b></div>' for i, x in enumerate(jj["k"]))
    return f"""<body class="skin-tracker"><a class="skip" href="#main">{esc(t['skip'])}</a>
<div class="win">
<header><div class="tt">{ICON}<span class="tn">{esc(t['title'])}</span><span class="smp">{esc(t['sample'])}</span><a class="x" href="{c['home']}" aria-label="{esc(t['close'])}" title="{esc(t['close'])}">✕</a></div>
<div class="mb"><div role="tablist" aria-label="{esc(t['tabs_aria'])}">{tabs}</div>
<nav class="lk" aria-label="{esc(t['links_aria'])}"><a href="{c['home']}">{esc(t['back'])}</a><a href="{esc(c['repo'])}" rel="noopener">{esc(t['repo'])}</a><a href="{c['other_h']}" hreflang="{c['other']}" lang="{c['other']}">{esc(t['lang'])}</a></nav></div>
<form id="qa" class="tb" autocomplete="off"><label for="qi">{esc(t['new'])}</label>
<input id="qi" type="text" placeholder="{esc(t['ph'])}" spellcheck="false" aria-describedby="qh"><button type="submit" class="bt p">{esc(t['save'])}</button>
<span id="qh" class="hint">{esc(t['hint'])}</span><span class="sp"></span>
<button type="button" id="xc" class="bt">{esc(t['csv'])}</button><button type="button" id="xt" class="bt">{esc(t['txt'])}</button><button type="button" id="rs" class="bt">{esc(t['reset'])}</button></form>
</header>
<main id="main" tabindex="-1"><h1 class="vh">{esc(t['title'])} · {esc(c['kind'])}</h1>
<section id="pn-list" role="tabpanel" aria-labelledby="t-list">
<div class="sum"><fieldset class="gl"><legend>{esc(jj['goal_h'])}</legend>
<div class="g"><label for="g1">{esc(jj['today'])}</label><progress id="p1" max="5" value="0"></progress><span class="gn"><b id="n1">0</b> / <input id="g1" type="number" min="1" max="99" value="5" aria-label="{esc(jj['today'])} · {esc(jj['goal_of'])}"></span></div>
<div class="g"><label for="g2">{esc(jj['week'])}</label><progress id="p2" max="25" value="0"></progress><span class="gn"><b id="n2">0</b> / <input id="g2" type="number" min="1" max="999" value="25" aria-label="{esc(jj['week'])} · {esc(jj['goal_of'])}"></span></div></fieldset>
<div class="kpis">{kp}</div></div>
<section id="stale" class="stale" aria-labelledby="sth"><h2 id="sth"><span>{esc(jj['stale_h'])}</span> <b id="sn">0</b></h2><p id="sp" class="sm"></p><ul id="sl" class="sl"></ul></section>
<div class="wk"><nav class="fo" aria-label="{esc(jj['folders'])}"><h2>{esc(jj['folders'])}</h2><ul id="fo"></ul></nav>
<section class="ls" aria-label="{esc(t['t_list'])}"><div class="lt"><label class="sr2"><span class="vh">{esc(jj['search_l'])}</span><input id="fq" type="search" placeholder="{esc(jj['search'])}"></label>
<div class="vw" role="group" aria-label="{esc(jj['view_l'])}"><button type="button" id="vt" aria-pressed="true">{esc(jj['tbl'])}</button><button type="button" id="vk" aria-pressed="false">{esc(jj['kan'])}</button></div></div>
<div id="lv"></div></section>
<aside id="dt" class="dt" aria-label="{esc(jj['dt_h'])}"></aside></div>
<noscript><p>{esc(t['noscript'])}</p><table><tbody>{ns}</tbody></table></noscript>
</section>
<section id="pn-stats" role="tabpanel" aria-labelledby="t-stats" hidden><div class="ch">
<section class="gb" aria-labelledby="c1h"><h2 id="c1h">{esc(jj['c1'])}</h2><p class="sm">{esc(jj['c1s'])}</p><div id="c1"></div></section>
<section class="gb" aria-labelledby="c2h"><h2 id="c2h">{esc(jj['c2'])}</h2><p class="sm">{esc(jj['c2s'])}</p><div id="c2"></div></section>
<section class="gb" aria-labelledby="c3h"><h2 id="c3h">{esc(jj['c3'])}</h2><p class="sm">{esc(jj['c3s'])}</p><div id="c3"></div></section></div></section>
<section id="pn-about" role="tabpanel" aria-labelledby="t-about" hidden><div class="ab"><h2>{esc(t['about_h'])}</h2><p class="lead">{esc(c['summary'])}</p>
<h3>{esc(t['what'])}</h3><ul>{lis(c['feats'])}</ul><h3>{esc(t['facts_h'])}</h3><ul>{lis(c['facts'])}</ul>
<h3>{esc(t['stack_h'])}</h3><ul class="chips">{lis(c['stack'])}</ul><h3>{esc(t['limits'])}</h3><p>{esc(c['note'])}</p>
<h3>{esc(t['mock_h'])}</h3><p>{esc(t['mock_p'])}</p><p>{esc(t['mock_data'])}</p><p>{esc(t['mock_no'])}</p>
<h3>{esc(t['links_h'])}</h3><p>{esc(t['nodemo'])}</p><p><a class="bt p" href="{esc(c['repo'])}" rel="noopener">{esc(s['btn_repo'])}</a></p></div></section>
</main>
<footer class="sb"><span id="st" role="status"></span><span class="sp"></span><span>{esc(t['foot'])} · © 2026 {esc(c['name'])}</span></footer>
</div>
<script>window.TJ={jt};</script><script src="{c['asset_tracker']}"></script>
</body></html>"""
