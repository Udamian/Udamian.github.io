#!/usr/bin/env python3
"""Higiene del sitio generado (solo stdlib): hreflang/canonical absolutos, robots, sitemap, og:image y enlaces internos.
Uso: primero python tools/build.py y luego python tests/hygiene.py"""
import glob
import os
import re
import sys
from urllib.parse import urldefrag, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


pages = [p for p in glob.glob(ROOT + "/**/index.html", recursive=True) if "/tests/" not in p and "/node_modules/" not in p]
check(len(pages) == 10, f"10 paginas generadas (hay {len(pages)})")
for p in sorted(pages):
    h = open(p, encoding="utf-8").read()
    rel = os.path.relpath(p, ROOT)
    alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h)
    check({a for a, _ in alts} == {"es", "en", "x-default"} and all(u.startswith("https://") for _, u in alts), f"{rel}: hreflang es/en/x-default absolutos")
    check(len(re.findall(r'<link rel="canonical" href="https://', h)) == 1, f"{rel}: canonical absoluto")
    check('og:image" content="https://' in h, f"{rel}: og:image absoluto")
    check(len(re.findall(r"<h1[ >]", h)) >= 1 and "<main" in h, f"{rel}: h1 y main")
    # enlaces internos relativos: el destino debe existir
    for u in re.findall(r'(?:href|src)="([^"#:?][^"]*)"', h):
        if u.startswith(("http", "mailto", "data:", "javascript")):
            continue
        t = urldefrag(urlparse(u).path)[0]
        dest = os.path.normpath(os.path.join(os.path.dirname(p), t))
        if os.path.isdir(dest):
            dest = os.path.join(dest, "index.html")
        if not os.path.exists(dest):
            check(False, f"{rel}: enlace roto -> {u}")
check(os.path.exists(ROOT + "/assets/og.png"), "assets/og.png existe")
for rel in ("index.html", "en/index.html"):
    h = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    check("linkedin.com/in/" in h and "mailto:" in h and ".pdf" in h, f"{rel}: LinkedIn, correo y CV visibles")
cv = glob.glob(ROOT + "/assets/cv/*.pdf")
check(len(cv) == 1 and open(cv[0], "rb").read(5) == b"%PDF-", "CV en PDF presente y valido")
robots = open(ROOT + "/robots.txt").read()
check("Sitemap: https://" in robots, "robots.txt apunta al sitemap")
sm = open(ROOT + "/sitemap.xml", encoding="utf-8").read()
check(len(re.findall(r"<url><loc>", sm)) == 10, "sitemap con 10 URLs")
print("\nFALLOS:", fails or "ninguno")
sys.exit(1 if fails else 0)
