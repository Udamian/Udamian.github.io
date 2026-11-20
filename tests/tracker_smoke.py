"""Prueba de la pagina de Job Tracker: python tests/tracker_smoke.py (desde la raiz del sitio).
Opcional: AXE=/ruta/a/axe.min.js para pasar axe-core en varias vistas."""
import os, sys, json, http.server, threading, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "tracker.json"), encoding="utf-8"))
AXE = os.environ.get("AXE")
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
def kv(pg, i): return pg.inner_text(f"#k{i}").strip()

n = len(D["items"])
stale = sum(1 for i in D["items"] if i["st"] == "enviada" and i["news"] > 21)
inter = sum(1 for i in D["items"] if i["st"] == "entrevista")
with sync_playwright() as p:
    br = p.chromium.launch()
    for tag, base, vp in (("d-es", "/p/job-tracker/", {"width": 1280, "height": 800}), ("m-es", "/p/job-tracker/", {"width": 390, "height": 844}),
                          ("s-es", "/p/job-tracker/", {"width": 320, "height": 640}), ("d-en", "/en/p/job-tracker/", {"width": 1280, "height": 800})):
        ctx = br.new_context(viewport=vp, accept_downloads=True)
        stub_goat(ctx)
        ctx.add_init_script("history.replaceState=function(){throw new Error('blocked')}")
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(B + base); pg.wait_for_selector("#lv table")
        ov = lambda: pg.evaluate("document.documentElement.scrollWidth<=innerWidth")
        check(ov(), f"{tag} sin overflow horizontal")
        check(kv(pg, 0) == str(n), f"{tag} total = {n}")
        check(pg.inner_text("#sn").strip() == str(stale), f"{tag} estancados = {stale}")
        check(pg.locator("#lv tbody tr").count() == n, f"{tag} tabla con {n} filas")
        # tasas
        resp = sum(1 for i in D["items"] if i["st"] != "enviada")
        check(abs(float(kv(pg, 7).replace("%", "").replace(",", ".")) - round(resp * 100 / n, 1)) < .06, f"{tag} tasa de respuesta")
        # carpeta + busqueda
        pg.click("#fo button[data-k=sinresp]"); check(pg.locator("#lv tbody tr").count() == stale, f"{tag} carpeta sin respuesta")
        pg.click("#fo button[data-k=all]"); pg.fill("#fq", "data"); c = pg.locator("#lv tbody tr").count()
        check(0 < c < n, f"{tag} busqueda filtra ({c})"); pg.fill("#fq", "zzzz"); check(pg.locator(".empty").count() == 1, f"{tag} sin resultados"); pg.fill("#fq", "")
        # orden
        pg.click("#lv thead th >> nth=0 >> button"); first = pg.inner_text("#lv tbody tr >> nth=0 >> th")
        check(first.strip().startswith("Á") or first.strip().startswith("Alt") or first.strip().startswith("B"), f"{tag} ordena por empresa ({first.strip()})")
        # alta rapida
        pg.fill("#qi", "Stripe · Backend Python @entrevista"); pg.press("#qi", "Enter")
        check(kv(pg, 0) == str(n + 1) and kv(pg, 5) == str(inter + 1) and kv(pg, 1) == "1", f"{tag} alta rapida: total, entrevista y hoy")
        check("Stripe" in pg.inner_text("#dt"), f"{tag} detalle de la nueva")
        # mover
        pg.click("#dt .da button >> nth=2"); check(kv(pg, 6) == str(sum(1 for i in D['items'] if i['st']=='rechazada') + 1), f"{tag} mover a rechazada")
        # borrar
        pg.click("#dt .da .dn"); check(kv(pg, 0) == str(n), f"{tag} borrar")
        # seguimiento
        pg.click("#sl li >> nth=0 >> button >> nth=0"); check(pg.inner_text("#sn").strip() == str(stale - 1), f"{tag} seguimiento saca de estancados")
        # kanban
        pg.click("#vk"); check(pg.locator(".kc").count() == 5 and pg.locator(".cd").count() == n, f"{tag} kanban 5 columnas")
        check(ov(), f"{tag} kanban sin overflow"); pg.click("#vt")
        # meta
        pg.fill("#g2", "10"); pg.press("#g2", "Tab"); check(pg.get_attribute("#p2", "max") == "10", f"{tag} meta semanal editable")
        # estadisticas y acerca
        pg.click("#t-stats"); check(pg.locator("#c1 .col").count() >= 1 and pg.locator("#c2 .row").count() == 4 and pg.locator("#c3 .row").count() >= 1, f"{tag} graficos")
        check(ov(), f"{tag} estadisticas sin overflow")
        if AXE and tag in ("d-es", "d-en"):
            pg.add_script_tag(path=AXE); r = pg.evaluate("axe.run().then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))"); check(not r, f"{tag} axe estadisticas {r}")
        pg.click("#t-about"); check("Datos de ejemplo" in pg.inner_text("#pn-about") or "Sample data" in pg.inner_text("#pn-about") or "ficticias" in pg.inner_text("#pn-about") or "made-up" in pg.inner_text("#pn-about") or "inventadas" in pg.inner_text("#pn-about"), f"{tag} acerca de explica los datos")
        check(pg.locator("a[href*='streamlit.app']").count() == 0, f"{tag} sin demo")
        check(ov(), f"{tag} acerca sin overflow")
        if AXE and tag in ("d-es", "d-en"):
            r = pg.evaluate("axe.run().then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))"); check(not r, f"{tag} axe acerca {r}")
        pg.click("#t-list")
        if AXE and tag in ("d-es", "d-en"):
            pg.click("#vk"); pg.click(".cd >> nth=0"); r = pg.evaluate("axe.run().then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))"); check(not r, f"{tag} axe kanban+detalle {r}"); pg.click("#vt")
            r = pg.evaluate("axe.run().then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))"); check(not r, f"{tag} axe tabla {r}")
        # exportar
        with pg.expect_download() as dl: pg.click("#xc")
        check(dl.value.suggested_filename == "job-tracker.csv", f"{tag} exporta CSV")
        txt = open(dl.value.path(), encoding="utf-8").read()
        check(not any(l[:1] in "=+-@" for l in txt.splitlines()[1:] if l), f"{tag} CSV sin celdas que parezcan formulas")
        pg.fill("#qi", "=HYPERLINK(\"http://x\") · @cmd"); pg.press("#qi", "Enter")
        with pg.expect_download() as dl2: pg.click("#xc")
        t2 = open(dl2.value.path(), encoding="utf-8").read()
        check("\"'=HYPERLINK" in t2 or "'=HYPERLINK" in t2, f"{tag} CSV neutraliza formulas ('=...)")
        # restaurar
        pg.click("#rs"); check(kv(pg, 0) == str(n) and pg.inner_text("#sn").strip() == str(stale), f"{tag} restaurar")
        check(not errs, f"{tag} sin errores de consola {errs}")
        ctx.close()
    br.close()
print("\nFALLOS:", fails or "ninguno"); sys.exit(1 if fails else 0)
