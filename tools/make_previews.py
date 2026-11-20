"""Genera las miniaturas de la portada: una captura de cada pagina interior (ES y EN).

Uso (desde la raiz del sitio):  python tools/make_previews.py
Necesita playwright y Pillow. Escribe assets/previews/<slug>-<es|en>.webp (480x360) y reconstruye el sitio.
Repetirlo solo cuando cambie el aspecto de una pagina de proyecto.
"""
import functools, http.server, io, os, subprocess, sys, threading
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SLUGS = ["relocationdevs", "job-tracker", "ytm-sync"]
OUT = os.path.join(ROOT, "assets", "previews")
SIZE = (480, 360)

subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build.py")], check=True, stdout=subprocess.DEVNULL)
os.makedirs(OUT, exist_ok=True)
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
h.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_address[1]}"
with sync_playwright() as p:
    br = p.chromium.launch()
    for lang, base in (("es", ""), ("en", "/en")):
        for slug in SLUGS:
            pg = br.new_page(viewport={"width": 1280, "height": 960}, device_scale_factor=1, reduced_motion="reduce")
            pg.goto(f"{B}{base}/p/{slug}/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
            im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB").resize(SIZE, Image.LANCZOS)
            im.save(os.path.join(OUT, f"{slug}-{lang}.webp"), "WEBP", quality=84, method=6)
            pg.close()
    br.close()
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build.py")], check=True)
print("Miniaturas en", OUT)
