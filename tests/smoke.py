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
GOAT = r'**/gc.zgo.at/**'
GOAT2 = r'**/*.goatcounter.com/**'
def stub_goat(c):
    for pat in (GOAT, GOAT2):
        c.route(pat, lambda r: r.fulfill(status=200, content_type='application/javascript', body=''))  # GOATSTUB: sin red, GoatCounter no se carga en las pruebas

def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c: fails.append(msg)

with sync_playwright() as p:
    br = p.chromium.launch()
    for name, vp in (("d", {"width": 1280, "height": 720}), ("m", {"width": 390, "height": 844})):
        ctx = br.new_context(viewport=vp, device_scale_factor=1)
        stub_goat(ctx)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=B)
        ctx.add_init_script("history.replaceState=function(){throw new Error('blocked')}")
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        for lang, path in (("es", "/"), ("en", "/en/")):
            pg.goto(B + path); pg.wait_for_load_state("networkidle")
            tag = f"{name}-{lang}"
            check(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f"{tag} sin overflow horizontal")
            check(pg.locator("article.res:visible").count() == 3, f"{tag} 3 resultados visibles")
            check(pg.evaluate("[...document.querySelectorAll('.res .th img')].every(i=>i.getAttribute('src').includes('previews/') && i.complete && i.naturalWidth>0)"), f"{tag} miniaturas = capturas de las paginas interiores")
            check(pg.locator(".ads a[href^=mailto]:visible").count() == 1 and pg.locator(".ads a[href*=linkedin]:visible").count() == 1, f"{tag} anuncios de perfil con contacto visible")
            check(pg.locator("a[href*='streamlit.app'], a:text-is('Demo')").count() == 0, f"{tag} sin enlaces a demo")
            check(pg.locator("#ob:visible").count() == 1 and pg.locator("#ob a[href$='.pdf']:visible").count() == 1, f"{tag} ficha destacada con CV y contacto")
            pg.screenshot(path=f"{OUT}/{tag}_home.png")
            pg.locator("#ob [data-copy]").click()
            em = pg.locator("#ob [data-copy]").get_attribute("data-copy")
            pg.wait_for_function("document.querySelector('#ob .cpst').textContent.length>0")
            check(em and "@" in em and em in pg.locator("#ob .cpst").inner_text(), f"{tag} boton copiar correo avisa de la direccion copiada")
            check(pg.evaluate("navigator.clipboard.readText()") == em, f"{tag} el portapapeles contiene el correo")
            pg.locator("#ob a[href^=mailto]").dispatch_event("click")
            pg.wait_for_selector(".mailtoast:not([hidden])", timeout=5000)
            check(em in pg.inner_text(".mailtoast") and pg.locator(".mailtoast a[href*='mail.google.com']").count() == 1, f"{tag} si mailto no abre nada, aviso con la direccion y Gmail")
            check(pg.locator("link[rel=apple-touch-icon]").count() == 1, f"{tag} icono tactil")
            check("Escribir a" not in pg.inner_text("body") and "Write to him" not in pg.inner_text("body"), f"{tag} textos en primera persona")
            pg.fill("#q", "docker"); pg.press("#q", "Enter")
            check(pg.locator("#ob:visible").count() == 0, f"{tag} ficha oculta al buscar otra cosa")
            pg.fill("#q", "docker"); 
            check(pg.locator("article.res:visible").count() == 1, f"{tag} filtro docker -> 1")
            pg.fill("#q", "zzzz")
            check(pg.locator("#none:visible").count() == 1, f"{tag} mensaje sin resultados")
            pg.screenshot(path=f"{OUT}/{tag}_none.png")
            pg.fill("#q", "python")
            check(pg.locator("article.res:visible").count() == 3, f"{tag} filtro 'python' -> 3")
            pg.click("[data-tab=imagenes]")
            check(pg.locator(".fig:visible").count() == 3, f"{tag} pestaña Imagenes")
            pg.screenshot(path=f"{OUT}/{tag}_img.png")
            pg.click("[data-tab=codigo]")
            check(pg.locator(".code:visible").count() == 3, f"{tag} pestaña Codigo")
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
        for lang, path in (("es", "/about/"), ("en", "/en/about/")):
            pg.goto(B + path); pg.wait_for_load_state("networkidle")
            tag = f"{name}-{lang}"
            check(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f"{tag} about sin overflow horizontal")
            check(pg.locator(".cv mark").count() > 5 and pg.locator(".terms .chip").count() == 2, f"{tag} folio con terminos resaltados y chips")
            pg.fill(".terms input", "docker"); pg.press(".terms input", "Enter")
            check(pg.locator(".terms .chip").count() == 3, f"{tag} termino nuevo anadido")
            pg.click(".terms .chip >> nth=2")
            check(pg.locator(".terms .chip").count() == 2, f"{tag} termino quitado")
            pg.hover(".lft [data-s=exp] >> nth=0")
            check(pg.locator(".cv section.on[data-s=exp]").count() == 1, f"{tag} seccion del folio sincronizada")
            check("+34" not in pg.inner_text(".cv") and pg.locator("a[href$='.pdf']:visible").count() >= 1, f"{tag} folio sin telefono y con PDF")
            pg.goto(B + path + "../" + "?q=proyectos%20con%20docker" if lang == "es" else B + "/en/?q=projects%20with%20docker"); pg.wait_for_load_state("networkidle")
            check(pg.locator("article.res:visible").count() == 1, f"{tag} ?q= filtra la portada")
        pg.goto(B + "/404.html"); pg.screenshot(path=f"{OUT}/{name}_404.png")
        check(pg.locator("form[role=search] input[name=q]").count() == 1 and pg.locator(".none:visible").count() == 2, f"{name} 404 como pagina de resultados vacia (ES+EN)")
        check(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f"{name} 404 sin overflow")
        check(not errs, f"{name} sin errores de consola {errs}")
        ctx.close()
    br.close()
print("\nFALLOS:", fails if fails else "ninguno")
sys.exit(1 if fails else 0)
