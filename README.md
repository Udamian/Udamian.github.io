# Cambeiro · portfolio de Damián Cambeiro

Portfolio estático para GitHub Pages con forma de buscador clásico. Cada proyecto es un resultado; cada resultado lleva a su página. Español en `/` e inglés en `/en/`.

## Estructura
- `data/projects.json`: los proyectos (textos en `es` y `en`). Es la única fuente de contenido.
- `data/profile.json`: perfil, formación y enlaces. Los enlaces en `null` (LinkedIn, correo, CV) no se muestran hasta que se rellenen.
- `tools/build.py`: genera todas las páginas HTML y las portadas provisionales (`assets/covers/*.svg`). Solo usa la biblioteca estándar de Python.
- `assets/buscador.css`, `assets/buscador.js`: estilos y comportamiento de la portada (filtro en vivo, pestañas, «Voy a tener suerte»).
- `skins/`: pieles de las páginas de proyecto. Cada proyecto elige la suya con el campo `skin` de `projects.json`: `base` (neutra), `player` (Reproductor 2000, en `tools/skins.py`) y `reloc` (RelocationDevs como buscador de los 2000, en `tools/reloc_skin.py` + `assets/reloc.js` + `skins/reloc.css`).
- `tools/prep_reloc.py`: lee dos CSV del repositorio de RelocationDevs (`cities_processed.csv`, `salaries.csv`) y escribe `data/relocation.json` y `assets/reloc-data.js`. `tools/prep_land.js` genera `data/land.txt` (contorno de continentes, Natural Earth 110m, dominio público). Solo hace falta repetirlos si cambian los datos.
- `tests/smoke.py` (portada) y `tests/reloc_smoke.py` (página de RelocationDevs): pruebas con Playwright en escritorio y móvil, ES y EN. `tests/hygiene.py` (solo stdlib) comprueba `hreflang`/canonical absolutos, `og:image`, `h1`/`main`, `robots.txt`, `sitemap.xml` y que no haya enlaces internos rotos.
- `tools/make_og.py`: regenera `assets/og.png` (imagen al compartir el enlace; necesita Playwright). `build.py` también genera `robots.txt` y `sitemap.xml` a partir de `site_host` y `base_path` de `profile.json`.
- `.github/workflows/ci.yml`: en cada subida regenera el sitio (falla si hay cambios sin subir) y lanza las tres pruebas.

## Uso
```
python tools/build.py          # regenera el sitio en esta carpeta
python tests/smoke.py          # pruebas de la portada (necesita playwright)
python tests/reloc_smoke.py    # pruebas de la página de RelocationDevs
python tests/hygiene.py        # higiene: hreflang, sitemap, robots, enlaces
python tools/prep_reloc.py <ruta/RelocationDevs>   # solo si cambian los datos
```
Para publicar: subir la carpeta a un repositorio `Udamian.github.io` (o activar Pages en otro) y comprobar `base_path` en `data/profile.json`.

## Añadir un proyecto
1. Añadir una entrada en `data/projects.json` (slug, textos es/en, stack, enlaces).
2. Ejecutar `python tools/build.py`.

## Vista previa para Artifact
`python tools/build.py --preview <carpeta>` genera el sitio con enlaces explícitos a `index.html` y la portada como fragmento, para publicarlo como Artifact.

## Honestidad de los datos de RelocationDevs
La página reproduce los datos y la fórmula reales (Relocation Score = poder adquisitivo×0,30 + mercado laboral×0,25 + calidad de vida×0,25 + (100−impuestos)×0,20). Solo 324 de las 578 ciudades tienen coordenadas; el salario medio del dataset de costes es por país; los salarios por país y rol son medianas de la encuesta, no el modelo de ML de la app.
