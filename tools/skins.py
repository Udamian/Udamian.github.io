"""Pieles retro de las paginas de proyecto.

Cada piel es una funcion que recibe el contexto `c` (ver build.skinned) y devuelve el
HTML del <body>. Los estilos viven en skins/<nombre>.css. Anadir una piel = una funcion
aqui + un CSS + registrarla en SKINS.
"""
from html import escape as esc


def lis(items):
    return "".join(f"<li>{esc(x)}</li>" for x in items)


T = {
    "es": {"prev": "Resultados", "play": "Abrir", "eject": "Código", "tracks": "Lista de reproducción",
           "tags": "Etiquetas del archivo", "t_title": "Título", "t_artist": "Artista", "t_album": "Álbum",
           "t_genre": "Género", "t_tech": "Tecnologías", "t_comment": "Comentario", "t_info": "Información", "shot": "Captura real", "shot_open": "Abrir en tamaño completo"},
    "en": {"prev": "Results", "play": "Open", "eject": "Code", "tracks": "Playlist",
           "tags": "File tags", "t_title": "Title", "t_artist": "Artist", "t_album": "Album",
           "t_genre": "Genre", "t_tech": "Technologies", "t_comment": "Comment", "t_info": "Information", "shot": "Real screenshot", "shot_open": "Open full size"},
}


# --------------------------------------------------------------- reproductor
def player(c):
    t = T[c["lang"]]
    s = c["s"]
    bars = "".join(f'<i style="--d:{(i * 37) % 11}"></i>' for i in range(18))
    play = c["demo"] or c["repo"]
    sh = c.get("shot")
    shot = (f'<section class="box"><h2>{esc(t["shot"])}</h2><figure class="shot"><a href="{esc(sh["src"])}" title="{esc(t["shot_open"])}">'
            f'<img src="{esc(sh["src"])}" alt="{esc(sh["alt"])}" width="{sh["w"]}" height="{sh["h"]}" loading="lazy"></a>'
            f'<figcaption>{esc(sh["cap"])}</figcaption></figure></section>' if sh else "")
    return f"""<body class="skin-player"><main class="pl"><h1 class="vh">{esc(c['title'])} · {esc(c['kind'])}</h1>
<div class="pt"><span>PORTFOLIO PLAYER</span><a href="{c['home']}" aria-label="{esc(s['w_close'])}" title="{esc(s['w_close'])}">✕</a></div>
<div class="dp"><div class="lcd"><div class="mq"><span>{esc(c['title'])} · {esc(c['kind'])}</span></div>
<div class="kb">{esc(' · '.join(c['stack'][:4]))}</div></div><div class="eq" aria-hidden="true">{bars}</div></div>
<div class="ct">
<a class="pb" href="{c['home']}"><b>⏮</b><span>{esc(t['prev'])}</span></a>
<a class="pb" href="{esc(play)}" rel="noopener"><b>▶</b><span>{esc(t['play'])}</span></a>
<a class="pb" href="{esc(c['repo'])}" rel="noopener"><b>⏏</b><span>{esc(t['eject'])}</span></a>
<a class="pb" href="{c['other_h']}" hreflang="{c['other']}" lang="{c['other']}"><b>⏭</b><span>{c['other'].upper()}</span></a></div>
<p class="sm">{esc(c['summary'])}</p>
{shot}
<section class="box"><h2>{esc(t['tracks'])} · {esc(s['what'])}</h2><ol>{lis(c['feats'])}</ol></section>
<section class="box"><h2>{esc(t['tags'])}</h2><dl>
<dt>{esc(t['t_title'])}</dt><dd>{esc(c['title'])}</dd>
<dt>{esc(t['t_artist'])}</dt><dd>{esc(c['name'])}</dd>
<dt>{esc(t['t_album'])}</dt><dd>Portfolio</dd>
<dt>{esc(t['t_genre'])}</dt><dd>{esc(c['kind'])}</dd>
<dt>{esc(t['t_tech'])}</dt><dd>{esc(', '.join(c['stack']))}</dd>
<dt>{esc(t['t_info'])}</dt><dd><ul>{lis(c['facts'])}</ul></dd>
<dt>{esc(t['t_comment'])}</dt><dd>{esc(c['note'])}</dd></dl></section>
</main></body></html>"""


from reloc_skin import reloc  # noqa: E402

SKINS = {"player": player, "reloc": reloc}
