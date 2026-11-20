#!/usr/bin/env python3
"""Genera los PDF del CV (es/en) desde data/cv.json y data/cv.en.json, con el mismo texto que el folio de la web.
Uso: python tools/make_cv.py   (necesita Playwright + Chromium; la fuente Carlito ya esta en assets/fonts)."""
import json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from pypdf import PdfReader, PdfWriter  # noqa: E402

ROOT = build.ROOT
OUTS = {"es": ("cv.json", "assets/cv/Damian_Cambeiro_CV.pdf", "Damián Cambeiro - CV Junior Python / Data Developer"),
        "en": ("cv.en.json", "assets/cv/Damian_Cambeiro_CV_EN.pdf", "Damián Cambeiro - Junior Python / Data Developer CV")}
LINKS = {"dcambeiro15@gmail.com": "mailto:dcambeiro15@gmail.com",
         "linkedin.com/in/damian-cambeiro": "https://www.linkedin.com/in/damian-cambeiro/",
         "github.com/Udamian": "https://github.com/Udamian"}

CSS = """
@font-face{font-family:C;font-weight:400;src:url(file://%(f)s/carlito-latin-400-normal.woff2)}
@font-face{font-family:C;font-weight:700;src:url(file://%(f)s/carlito-latin-700-normal.woff2)}
@page{size:A4;margin:0}
*{box-sizing:border-box}html,body{margin:0}
body{font:%(fs)spt/1.28 C,Carlito,Calibri,sans-serif;color:#111;padding:13mm 17mm}
p{margin:0}a{color:inherit;text-decoration:none}
.nm{font-size:24pt;line-height:1.1;font-weight:700;color:#1d4f79}
.rl{font-size:12.5pt;font-weight:700;margin-top:.1em}
.ct{color:#1d4f79;margin-top:.35em}.ct a{color:#1d4f79}
.lc{margin-bottom:.15em}
section{break-inside:avoid-page}
.h{margin:.75em 0 .25em;font-weight:700;color:#1d4f79;border-bottom:1px solid #1d4f79;padding-bottom:.05em;letter-spacing:.01em}
.row{display:flex;justify-content:space-between;gap:.8em;margin-top:.2em}.row span:last-child{flex:none;color:#444}
.sub{margin:.65em 0 .1em;font-size:11.5pt;color:#1d4f79}
ul+.row{margin-top:.5em}section[data-s=idiomas] p:not(.h){white-space:pre}
ul{margin:.1em 0 0;padding-left:1.3em}li{margin:.02em 0}li::marker{color:#1d4f79}
"""

def html(lang, fs):
    cv = json.load(open(os.path.join(ROOT, "data", OUTS[lang][0]), encoding="utf-8"))
    body = build.render_cv(cv, terms=("\u0001",))
    for text, url in LINKS.items():
        body = body.replace(text, f'<a href="{url}">{text}</a>', 1)
    body = re.sub(r'(github\.com/Udamian/[A-Za-z0-9._-]+)</span>', lambda m: f'<a href="https://{m.group(1)}">{m.group(1)}</a></span>', body)
    css = CSS % {"f": os.path.join(ROOT, "assets", "fonts"), "fs": fs}
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{OUTS[lang][2]}</title><style>{css}</style></head><body>{body}</body></html>'

def make(pw, lang):
    _, out, title = OUTS[lang]
    for fs in (10.5, 10.25, 10, 9.75, 9.5):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as t:
            t.write(html(lang, fs)); tmp = t.name
        b = pw.chromium.launch(); pg = b.new_page(); pg.goto("file://" + tmp); pg.wait_for_timeout(300)
        pg.pdf(path=tmp + ".pdf", format="A4", print_background=True, prefer_css_page_size=True); b.close()
        r = PdfReader(tmp + ".pdf")
        if len(r.pages) == 1: break
    else:
        sys.exit(f"{lang}: no cabe en una pagina")
    w = PdfWriter(clone_from=r)
    w.add_metadata({"/Title": title, "/Author": "Damián Cambeiro", "/Subject": "CV"})
    with open(os.path.join(ROOT, out), "wb") as fh: w.write(fh)
    os.unlink(tmp); os.unlink(tmp + ".pdf")
    print(f"{out}: 1 pagina, {fs}pt, {os.path.getsize(os.path.join(ROOT, out)) // 1024} KB")

if __name__ == "__main__":
    with sync_playwright() as pw:
        for lang in ("es", "en"): make(pw, lang)
