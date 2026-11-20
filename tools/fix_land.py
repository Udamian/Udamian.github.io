"""Corrige los poligonos de data/land.txt que cruzan el antimeridiano (franjas horizontales en el mapa).

Desenrolla la longitud de cada anillo y lo dibuja tambien desplazado +-360 (el svg recorta lo que sobra).
Uso: python tools/fix_land.py   (idempotente; actualiza land.txt, relocation.json y assets/reloc-data.js)
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fix(d):
    out = []
    for ring in re.findall(r"M[^M]*", d):
        pts = [tuple(map(float, p.split(","))) for p in re.findall(r"(-?[\d.]+,-?[\d.]+)", ring)]
        if not pts:
            continue
        xs = [pts[0][0]]
        for (x, _), (px, _) in zip(pts[1:], pts[:-1]):
            dx = (x - px + 180) % 360 - 180
            xs.append(xs[-1] + dx)
        wrapped = max(abs(a - b) for a, b in zip([p[0] for p in pts[1:]], [p[0] for p in pts[:-1]]) ) > 180 if len(pts) > 1 else False
        shifts = (0, -360, 360) if wrapped else (0,)
        for sh in shifts:
            seg = [(x + sh, y) for x, (_, y) in zip(xs, pts)]
            if sh and not any(-20 <= x <= 380 for x, _ in seg):
                continue
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}".replace(".0,", ",").replace(".0", "") if False else f"{x:g},{y:g}" for x, y in seg) + "Z")
    return "".join(out)


land_p = os.path.join(ROOT, "data", "land.txt")
old = open(land_p, encoding="utf-8").read()
new = fix(old)
if new == old:
    print("sin cambios")
else:
    open(land_p, "w", encoding="utf-8").write(new)
    rj = os.path.join(ROOT, "data", "relocation.json")
    j = json.load(open(rj, encoding="utf-8")); j["land"] = new
    json.dump(j, open(rj, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    rd = os.path.join(ROOT, "assets", "reloc-data.js")
    s = open(rd, encoding="utf-8").read()
    o = json.dumps(old, ensure_ascii=False); n = json.dumps(new, ensure_ascii=False)
    assert o in s or old in s, "land no encontrado en reloc-data.js"
    s = s.replace(o, n) if o in s else s.replace(old, new)
    open(rd, "w", encoding="utf-8").write(s)
    print("land.txt", len(old), "->", len(new))
