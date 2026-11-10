"""Prepara los datos de RelocationDevs para la web estatica (solo biblioteca estandar).

Uso:  python tools/prep_reloc.py <carpeta-del-repo-RelocationDevs>
Lee  data/processed/cities_processed.csv  y  data/processed/salaries.csv  del repositorio
de RelocationDevs (datos ya procesados por sus notebooks) y escribe:
  data/relocation.json      fuente de verdad para el generador
  assets/reloc-data.js      lo mismo como  window.RD = {...}  (se carga en la pagina)
No entrena ni ejecuta nada del repositorio: solo lee dos CSV.
"""
import csv
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS = ["Europe", "Americas", "Asia", "Oceania", "Middle East", "Africa", "Other"]
MIN_N = 10          # minimo de respuestas para dar una mediana pais x rol
MIN_ROLE = 300      # roles con al menos estas respuestas en total


def num(v, nd=2):
    f = float(v)
    return int(f) if f == int(f) else round(f, nd)


def quart(vals):
    q = statistics.quantiles(sorted(vals), n=4, method="inclusive")
    return [round(q[0]), round(statistics.median(vals)), round(q[2])]


def main(repo):
    proc = os.path.join(repo, "data", "processed")
    cities = []
    with open(os.path.join(proc, "cities_processed.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            lat = r["lat"].strip()
            cities.append([
                r["city_name"], r["country"], REGIONS.index(r["region"]),
                num(r["average_salary"]), num(r["average_rent"]), num(r["tax_rate"]),
                num(r["cost_of_living_index"]), num(r["purchasing_power_index"]),
                num(r["quality_of_life_index"]), num(r["job_market_score"]),
                round(float(lat), 2) if lat else None,
                round(float(r["lon"]), 2) if lat else None,
                round(float(r["relocation_score"]), 2),   # solo para comprobar la formula
            ])
    by = {}
    roles_n = {}
    with open(os.path.join(proc, "salaries.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            g = float(r["gross_salary"])
            by.setdefault(r["city_name"], {}).setdefault(r["role"], []).append(g)
            roles_n[r["role"]] = roles_n.get(r["role"], 0) + 1
    roles = [k for k, v in sorted(roles_n.items(), key=lambda kv: -kv[1]) if v >= MIN_ROLE and not k.startswith('Other')]
    sal = {}
    for country, rd in sorted(by.items()):
        allv = [x for v in rd.values() for x in v]
        entry = {"all": [len(allv)] + quart(allv), "roles": {}}
        for i, role in enumerate(roles):
            v = rd.get(role, [])
            if len(v) >= MIN_N:
                entry["roles"][str(i)] = [len(v)] + quart(v)
        sal[country] = entry
    land = os.path.join(ROOT, "data", "land.txt")      # lo genera tools/prep_land.js
    # nombres de pais distintos entre el dataset de costes de vida y la encuesta
    xmap = {"United Kingdom": "United Kingdom of Great Britain and Northern Ireland", "United States": "United States of America",
            "Bosnia And Herzegovina": "Bosnia and Herzegovina", "Hong Kong": "Hong Kong (S.A.R.)", "Iran": "Iran, Islamic Republic of...",
            "Russia": "Russian Federation", "Venezuela": "Venezuela, Bolivarian Republic of...", "Vietnam": "Viet Nam",
            "Ivory Coast": "Côte d'Ivoire", "North Macedonia": "Republic of North Macedonia", "Syria": "Syrian Arab Republic",
            "Trinidad And Tobago": "Trinidad and Tobago", "Tanzania": "United Republic of Tanzania"}
    xmap = {k: v for k, v in xmap.items() if v in sal}
    out = {"xmap": xmap, "land": open(land, encoding="utf-8").read() if os.path.exists(land) else "", "regions": REGIONS, "roles": roles, "cities": cities, "salaries": sal,
           "meta": {"n_cities": len(cities), "n_geo": sum(1 for c in cities if c[10] is not None),
                    "n_records": sum(e["all"][0] for e in sal.values()), "n_countries": len(sal)}}
    with open(os.path.join(ROOT, "data", "relocation.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(ROOT, "assets", "reloc-data.js"), "w", encoding="utf-8") as f:
        f.write("window.RD=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    # comprobacion de la formula del Relocation Score
    bad = 0
    for c in cities:
        s = c[7] * .30 + c[9] * .25 + c[8] * .25 + max(0, 100 - c[5]) * .20
        if abs(s - c[12]) > 0.01:
            bad += 1
    print(out["meta"], "| roles:", len(roles), "| formula distinta en", bad, "ciudades")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
