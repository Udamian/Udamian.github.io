#!/usr/bin/env python3
"""Genera assets/og.png (1200x630, imagen al compartir el enlace). Dev-only: necesita Playwright.
Uso: python tools/make_og.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

prof = json.load(open(os.path.join(build.ROOT, "data", "profile.json"), encoding="utf-8"))
html = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{margin:0;width:1200px;height:630px;background:#fff;font-family:Arial,Helvetica,sans-serif;
display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px}}
.logo{{font:700 150px/1 Georgia,'Times New Roman',serif;letter-spacing:-.04em}}
.box{{width:760px;height:64px;border:1px solid #dfe1e5;border-radius:32px;box-shadow:0 1px 6px rgba(32,33,36,.28);
display:flex;align-items:center;padding:0 26px;font-size:26px;color:#202124}}
.name{{font-size:34px;color:#202124;font-weight:700}}.role{{font-size:26px;color:#5f6368;margin-top:-22px}}
</style><div class="logo">{build.logo()}</div><div class="box">proyectos de {prof['first_name']}</div>
<div class="name">{prof['name']}</div><div class="role">{prof['role']['en']}</div>"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.set_content(html)
    pg.screenshot(path=os.path.join(build.ROOT, "assets", "og.png"))
    b.close()
print("assets/og.png generado")
