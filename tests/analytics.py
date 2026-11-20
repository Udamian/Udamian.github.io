#!/usr/bin/env python3
"""Analitica opcional: sin codigo no se inyecta nada; con codigo, GoatCounter + eventos + aviso en todas las paginas
(salvo vista previa). Construye en una carpeta temporal, no toca el repositorio. Uso: python tests/analytics.py"""
import glob, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import build  # noqa: E402

fails = []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

real = build.load
def run(code, suffix=""):
    out = tempfile.mkdtemp()
    def load(n):
        d = real(n)
        if n == "profile.json": d = dict(d, analytics={"goatcounter": code})
        return d
    build.load, build.OUT, build.SUFFIX = load, out, suffix
    try: build.build()
    finally: build.load, build.SUFFIX = real, ""
    import shutil
    for d in ("assets", "skins"): shutil.copytree(os.path.join(build.ROOT, d), os.path.join(out, d), ignore=shutil.ignore_patterns("covers"), dirs_exist_ok=True)
    return out

def pages(out): return sorted(glob.glob(out + "/**/*.html", recursive=True))

off = run("")
check(all("goatcounter" not in open(p, encoding="utf-8").read() for p in pages(off)), "sin codigo: ninguna pagina carga analitica")
on = run("cambeiro-demo")
P = pages(on)
check(len(P) == 11, f"con codigo: 11 paginas ({len(P)})")
for p in P:
    h = open(p, encoding="utf-8").read(); r = os.path.relpath(p, on)
    check(h.count('data-goatcounter="https://cambeiro-demo.goatcounter.com/count"') == 1, f"{r}: GoatCounter una vez")
    check("eventos.js" in h and h.index("goatcounter") < h.index("</head>"), f"{r}: eventos.js en head")
    check("GoatCounter" in h, f"{r}: aviso de privacidad visible")
    check("document.cookie" not in h, f"{r}: sin cookies")
prev = run("cambeiro-demo", "index.html")
check(all("goatcounter" not in open(p, encoding="utf-8").read() for p in pages(prev)), "vista previa: sin analitica")
try:
    build.load = lambda n: dict(real(n), analytics={"goatcounter": "x y;<"}) if n == "profile.json" else real(n)
    build.build(); check(False, "codigo invalido rechazado")
except SystemExit:
    check(True, "codigo invalido rechazado")
finally:
    build.load = real

# --- eventos en navegador (count.js se sustituye por un doble que registra las llamadas)
import functools, http.server, threading
from playwright.sync_api import sync_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("H", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=on))
threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_address[1]}"
STUB = "window.goatcounter={count:function(o){var c=JSON.parse(sessionStorage.gc||'[]');c.push(o.path+'|'+o.event);sessionStorage.gc=JSON.stringify(c)}};"
with sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context()
    ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith(B) else r.fulfill(status=204, body=""))
    ctx.route("https://gc.zgo.at/**", lambda r: r.fulfill(body=STUB, content_type="text/javascript"))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "/"); pg.wait_for_timeout(300)
    def calls(): return pg.evaluate("JSON.parse(sessionStorage.gc||'[]')")
    pg.add_init_script("""document.addEventListener('click', e => {
        const a = e.target.closest('a'); const h = a && a.getAttribute('href') || '';
        if (/^(https?:|mailto:)|\\.pdf$/.test(h)) e.preventDefault(); })""")
    pg.fill("#q", "secreto-privado"); pg.press("#q", "Enter"); pg.wait_for_timeout(200)
    pg.click("a[data-tab=codigo]")
    for sel in ("a[href^='mailto:']", "a[href$='.pdf']", "a[href*='linkedin.com']"):
        pg.locator(sel).first.dispatch_event("click")
    pg.locator("a[href^='https://github.com/Udamian/']").first.dispatch_event('click')
    c = calls()
    for want in ("evt/buscador/busqueda|true", "evt/buscador/pestana-codigo|true", "evt/contacto/correo|true", "evt/contacto/cv-pdf|true", "evt/contacto/linkedin|true"):
        check(want in c, f"evento {want}")
    check(any(x.startswith("evt/repo/") or x.startswith("evt/contacto/github") for x in c), "evento de GitHub/repositorio")
    check(not any("secreto" in x for x in c), "no se registra lo que se escribe en el buscador")
    check(pg.evaluate("document.cookie") == "", "sin cookies")
    check(not errs, f"sin errores JS {errs}")
    br.close()
sys.exit(1 if fails else 0)
