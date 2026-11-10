"""Prueba de la pagina de RelocationDevs: python tests/reloc_smoke.py (desde la raiz del sitio)."""
import os, sys, http.server, threading, functools, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/shots"
os.makedirs(OUT, exist_ok=True)
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
h.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_address[1]}"
D = json.load(open(os.path.join(ROOT, "data", "relocation.json"), encoding="utf-8"))
fails = []
def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c: fails.append(msg)

with sync_playwright() as p:
    br = p.chromium.launch()
    for name, vp in (("d", {"width": 1280, "height": 720}), ("m", {"width": 390, "height": 844})):
        for lang, base in (("es", "/p/relocationdevs/"), ("en", "/en/p/relocationdevs/")):
            tag = f"{name}-{lang}"
            ctx = br.new_context(viewport=vp)
            ctx.add_init_script("history.replaceState=function(){throw new Error('blocked')}")
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            ov = lambda: pg.evaluate("document.documentElement.scrollWidth<=innerWidth")
            pg.goto(B + base); pg.wait_for_load_state("networkidle")
            check(ov(), f"{tag} portada sin overflow")
            check(pg.locator("#v-home").is_visible() and not pg.locator("#hd").is_visible(), f"{tag} portada visible")
            # busqueda desde la portada
            pg.fill("#pq", "spain"); pg.click("#pf button[type=submit]")
            check(pg.locator("li.rs").count() == 10, f"{tag} 10 resultados por pagina")
            check("15" in pg.inner_text("#rc"), f"{tag} 15 ciudades de Spain")
            check(ov(), f"{tag} resultados sin overflow")
            pg.click(".pg a >> text=2"); pg.wait_for_function("document.querySelectorAll('li.rs').length==5"); check(pg.locator("li.rs").count() == 5, f"{tag} pagina 2 con 5")
            # orden por defecto = formula del proyecto
            pg.goto(B + base + "#/b"); top = pg.inner_text("li.rs >> nth=0")
            best = max(D["cities"], key=lambda c: c[7]*.30 + c[9]*.25 + c[8]*.25 + max(0, 100-c[5])*.20)
            check(best[0] in top, f"{tag} primera ciudad = {best[0]}")
            check("119,8" in top or "119.8" in top, f"{tag} puntuacion 119,8 (CSV: {best[12]})")
            # alias en espanol
            pg.goto(B + base + "#/b?q=espana"); check(pg.locator("li.rs").count() == 10, f"{tag} alias espana")
            # sin resultados
            pg.goto(B + base + "#/b?q=zzzz"); check(pg.locator(".none").count() == 1, f"{tag} sin resultados")
            # pesos propios cambian el orden
            pg.goto(B + base + "#/b?w=0,0,0,10"); first_tax = pg.inner_text("li.rs >> nth=0")
            check(first_tax != top, f"{tag} pesos propios reordenan")
            pg.goto(B + base + "#/adv"); pg.fill("#aq", "germany"); pg.fill("#wt", "10") if False else None
            pg.click("#af button[type=submit]"); check(pg.locator("li.rs").count() > 0 and "germany" in pg.url.lower(), f"{tag} avanzada")
            # filtros: alquiler maximo
            pg.goto(B + base + "#/b?mr=300"); check(pg.locator("li.rs").count() > 0, f"{tag} filtro alquiler")
            # ciudad
            pg.goto(B + base + "#/c/1"); check("Zurich" in pg.inner_text("#cy") and "94" in pg.inner_text("#cy"), f"{tag} detalle Zurich")
            check(ov(), f"{tag} ciudad sin overflow")
            # suerte
            pg.goto(B + base); pg.fill("#pq", "tokyo"); pg.click("#lucky")
            check("#/c/" in pg.url and "Tokyo" in pg.inner_text("#cy"), f"{tag} suerte -> Tokyo")
            # comparador
            pg.goto(B + base + "#/cmp/0,1,2"); check(pg.locator(".cmpt tbody tr").count() == 10, f"{tag} comparador 10 filas")
            check(ov(), f"{tag} comparador sin overflow")
            pg.goto(B + base + "#/cmp/0"); check(pg.locator("#cp .none").count() == 1, f"{tag} comparador pide 2")
            # mapa
            pg.goto(B + base + "#/map")
            check(pg.locator("#mp circle").count() == D["meta"]["n_geo"], f"{tag} mapa {D['meta']['n_geo']} puntos")
            pg.locator("#mp circle.hi").first.click(force=True)
            check("Puntuaci" in pg.inner_text("#mi") or "Score" in pg.inner_text("#mi"), f"{tag} mapa selecciona ciudad")
            pg.check("#mrad input[value='0']"); n_eu = pg.locator("#mp circle").count()
            check(0 < n_eu < D["meta"]["n_geo"], f"{tag} filtro region mapa ({n_eu})")
            check(ov(), f"{tag} mapa sin overflow")
            # salarios
            pg.goto(B + base + "#/sal?c=Spain"); check("55.502" in pg.inner_text("#so") or "55,502" in pg.inner_text("#so"), f"{tag} mediana Spain")
            pg.select_option("#sr", "1"); check("#so .sal" and pg.locator("#so .sal").count() == 1, f"{tag} salario por rol")
            pg.goto(B + base + "#/c/%d" % [i for i, c in enumerate(D["cities"]) if c[1] == "United States"][0])
            check(pg.locator("#cy a[href*='#/sal?c=United%20States%20of%20America']").count() == 1, f"{tag} enlace salarios EE.UU.")
            check(ov(), f"{tag} salarios sin overflow")
            # acerca de
            pg.goto(B + base + "#/about"); check(ov() and pg.locator(".ab .btn").count() == 1 and pg.locator("a[href*=streamlit]").count() == 0, f"{tag} acerca de (solo repo, sin demo)")
            pg.wait_for_function("document.querySelector('.shot img').complete"); check(pg.evaluate("document.querySelector('.shot img').naturalWidth") == 1200, f"{tag} captura real cargada")
            pg.screenshot(path=f"{OUT}/reloc_{tag}_about.png", full_page=True)
            check(errs == [], f"{tag} sin errores de consola {errs}")
            ctx.close()
    br.close()
print("\nFALLOS:", fails if fails else "ninguno")
sys.exit(1 if fails else 0)
