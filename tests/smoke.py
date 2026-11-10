"""Prueba de humo con Playwright: python tests/smoke.py (desde la raiz del sitio)."""
import os, sys, http.server, threading, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/shots"
os.makedirs(OUT, exist_ok=True)
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
h.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_address[1]}"
fails = []
def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c: fails.append(msg)

with sync_playwright() as p:
    br = p.chromium.launch()
    for name, vp in (("d", {"width": 1280, "height": 720}), ("m", {"width": 390, "height": 844})):
        ctx = br.new_context(viewport=vp, device_scale_factor=1)
        ctx.add_init_script("history.replaceState=function(){throw new Error('blocked')}")
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        for lang, path in (("es", "/"), ("en", "/en/")):
            pg.goto(B + path); pg.wait_for_load_state("networkidle")
            tag = f"{name}-{lang}"
            check(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f"{tag} sin overflow horizontal")
            check(pg.locator("article.res:visible").count() == 4, f"{tag} 4 resultados visibles")
            pg.screenshot(path=f"{OUT}/{tag}_home.png")
            pg.fill("#q", "docker"); 
            check(pg.locator("article.res:visible").count() == 2, f"{tag} filtro docker -> 2")
            pg.fill("#q", "zzzz")
            check(pg.locator("#none:visible").count() == 1, f"{tag} mensaje sin resultados")
            pg.screenshot(path=f"{OUT}/{tag}_none.png")
            pg.fill("#q", "python")
            check(pg.locator("article.res:visible").count() == 4, f"{tag} filtro 'python' -> 3")
            pg.click("[data-tab=imagenes]")
            check(pg.locator(".fig:visible").count() == 4, f"{tag} pestaña Imagenes")
            pg.screenshot(path=f"{OUT}/{tag}_img.png")
            pg.click("[data-tab=codigo]")
            check(pg.locator(".code:visible").count() == 4, f"{tag} pestaña Codigo")
            pg.screenshot(path=f"{OUT}/{tag}_code.png")
            pg.click("[data-tab=todo]")
            pg.click("a[data-q]:first-of-type >> nth=0")
            check(pg.locator("article.res:visible").count() >= 1, f"{tag} busqueda relacionada")
            pg.click("#lucky")
            pg.wait_for_load_state("networkidle")
            check(("/p/" in pg.url or "/about/" in pg.url), f"{tag} 'de suerte' lleva a un proyecto ({pg.url.replace(B,'')})")
            check(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f"{tag} proyecto sin overflow")
            pg.screenshot(path=f"{OUT}/{tag}_proj.png", full_page=True)
            other = pg.locator("a[hreflang]:visible")
            check(other.count() >= 1, f"{tag} proyecto tiene selector de idioma")
            other.first.click(); pg.wait_for_load_state("networkidle")
            check(("/en/" in pg.url) == (lang == "es"), f"{tag} idioma alterno correcto ({pg.url.replace(B,'')})")
        pg.goto(B + "/404.html"); pg.screenshot(path=f"{OUT}/{name}_404.png")
        check(not errs, f"{name} sin errores de consola {errs}")
        ctx.close()
    br.close()
print("\nFALLOS:", fails if fails else "ninguno")
sys.exit(1 if fails else 0)
