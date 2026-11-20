# Cambeiro · portfolio de Damián Cambeiro

Portfolio estático para GitHub Pages con forma de buscador clásico. Cada proyecto es un resultado; cada resultado lleva a su página. Español en `/` e inglés en `/en/`.

## Estructura
- `data/projects.json`: los proyectos (textos en `es` y `en`). Es la única fuente de contenido.
- `data/profile.json`: perfil, trayectoria, enlaces, fecha de la copia en caché del CV (`cv_date`) y textos del panel. `data/cv.json` y `data/cv.en.json`: el texto real del CV (es/en). Dibuja el folio de «Sobre mí» y, con `tools/make_cv.py`, genera los PDF (`assets/cv/Damian_Cambeiro_CV.pdf` y `..._EN.pdf`).
- `tools/build.py`: genera todas las páginas HTML y las portadas provisionales (`assets/covers/*.svg`). Solo usa la biblioteca estándar de Python.
- `assets/buscador.css`, `assets/buscador.js`: la portada como una página de resultados del Google de 2004: pestañas Web/Imágenes/Código arriba, logo con botones de sistema, barra azul «Resultados 1 - 3 de 3 de …», «Quizás quisiste decir», resultados con título azul subrayado, fragmento con los términos buscados en negrita, URL verde con tamaño real de la página («16k»), «Repositorio - Páginas similares», enlaces de sección en dos columnas, columna de «Enlaces patrocinados» (tu contacto, CV y LinkedIn como anuncios), «Cambeiiiiiro» y pie centrado. Filtro en vivo, `?q=` y «Voy a tener suerte». Única concesión moderna: una miniatura pequeña por resultado.
- `assets/perfil.css`, `assets/perfil.js`: «Sobre mí» como escenario partido. A la izquierda la trayectoria; a la derecha el folio del CV (HTML con el texto real) sobre mesa azul noche, con resaltado de términos (python y sql de serie, editable) y sincronizado con la sección que se lee.
- `assets/eventos.js`: eventos de analítica (clics en CV, correo, LinkedIn, repos y buscador; solo se carga si hay código de GoatCounter).
- `assets/copiar.js`: botón «Copiar correo» (portada y «Sobre mí»); muchas personas no tienen cliente de correo configurado y el `mailto:` solo no basta.
- `assets/fonts/`: Fraunces, Arimo y Carlito (latin, woff2) alojadas en el repositorio, con sus licencias (OFL/Apache). Ninguna petición a terceros.
- `skins/`: pieles de las páginas de proyecto. Cada proyecto elige la suya con el campo `skin` de `projects.json`: `base` (neutra), `player` (Reproductor 2000, en `tools/skins.py`) `reloc` (RelocationDevs como buscador de los 2000, en `tools/reloc_skin.py` + `assets/reloc.js` + `skins/reloc.css`) y `tracker` (Job Tracker como programa de escritorio clásico, en `tools/tracker_skin.py` + `assets/tracker.js` + `skins/tracker.css` + `data/tracker.json`).
- `tools/prep_reloc.py`: lee dos CSV del repositorio de RelocationDevs (`cities_processed.csv`, `salaries.csv`) y escribe `data/relocation.json` y `assets/reloc-data.js`. `tools/prep_land.js` genera `data/land.txt` (contorno de continentes, Natural Earth 110m, dominio público). Solo hace falta repetirlos si cambian los datos.
- `tests/smoke.py` (portada), `tests/reloc_smoke.py` (RelocationDevs) y `tests/tracker_smoke.py` (Job Tracker; con `AXE=ruta/axe.min.js` pasa también axe-core): pruebas con Playwright en escritorio y móvil, ES y EN. `tests/hygiene.py` (solo stdlib) comprueba `hreflang`/canonical absolutos, `og:image`, `h1`/`main`, `robots.txt`, `sitemap.xml` y que no haya enlaces internos rotos.
- `tools/make_og.py`: regenera `assets/og.png` (imagen al compartir el enlace; necesita Playwright). `build.py` también genera `robots.txt` y `sitemap.xml` a partir de `site_host` y `base_path` de `profile.json`.
- `tests/analytics.py`: comprueba la analítica (sin cookies, eventos, no registra lo que se escribe). Las pruebas de navegador simulan GoatCounter, así que no necesitan red ni cuentan visitas.
- `.github/workflows/ci.yml`: en cada subida regenera el sitio (falla si hay cambios sin subir), pasa la higiene y lanza las cuatro pruebas de navegador (portada, RelocationDevs, Job Tracker y analítica).

## Uso
```
python tools/build.py          # regenera el sitio en esta carpeta
python tests/smoke.py          # pruebas de la portada (necesita playwright)
python tests/reloc_smoke.py    # pruebas de la página de RelocationDevs
python tests/tracker_smoke.py  # pruebas de la página de Job Tracker
python tests/hygiene.py        # higiene: hreflang, sitemap, robots, enlaces, PDF
python tests/analytics.py      # analítica y eventos
python tools/make_cv.py        # regenera los dos PDF del CV (necesita playwright y pypdf)
python tools/prep_reloc.py <ruta/RelocationDevs>   # solo si cambian los datos
```
Para publicar: subir la carpeta a un repositorio `Udamian.github.io` (o activar Pages en otro) y comprobar `base_path` en `data/profile.json`.

## Añadir un proyecto
1. Añadir una entrada en `data/projects.json` (slug, textos es/en, stack, enlace al repositorio y, si hay, `shot` con la captura real). No hay enlaces a demos.
2. Ejecutar `python tools/build.py` y las pruebas.

## Vista previa para Artifact
`python tools/build.py --preview <carpeta>` genera el sitio con enlaces explícitos a `index.html` y la portada como fragmento, para publicarlo como Artifact.

## Honestidad de los datos de RelocationDevs
La página reproduce los datos y la fórmula reales (Relocation Score = poder adquisitivo×0,30 + mercado laboral×0,25 + calidad de vida×0,25 + (100−impuestos)×0,20). Solo 324 de las 578 ciudades tienen coordenadas; el salario medio del dataset de costes es por país; los salarios por país y rol son medianas de la encuesta, no el modelo de ML de la app.

## Honestidad de los datos de Job Tracker
La página es una maqueta con datos de ejemplo e inventados (`data/tracker.json`): la app real guarda candidaturas personales y no se publican. Reproduce la lógica de la app (tasas, embudo, «Sin respuesta» tras 21 días sin novedades); los cambios hechos en la página solo viven en la pestaña, salvo las metas, que se guardan en el navegador.

## Publicar en GitHub Pages (paso a paso)
1. En GitHub, crea un repositorio **público** llamado `Udamian.github.io` (sin README ni licencia iniciales).
2. En esta carpeta: `git init -b main`, `git add .`, `git commit -m "Portfolio"`, `git remote add origin https://github.com/Udamian/Udamian.github.io.git` y `git push -u origin main`. El `.gitignore` ya excluye `__pycache__`, `.env` y copias `.bak`.
3. En el repositorio: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save**. En uno o dos minutos estará en `https://udamian.github.io/`.
4. Comprueba la pestaña **Actions** (el CI debe salir en verde) y abre `/`, `/en/`, `/about/` y las tres páginas de proyecto.
5. Antes de anunciarlo, abre en una ventana de incógnito los repositorios enlazados (RelocationDevs, job-tracker, YTM Sync) y comprueba que son públicos y que no contienen `.env`, volcados de base de datos ni candidaturas reales.

Si algún día usas otra ruta (por ejemplo `usuario.github.io/portfolio/`), cambia `site_host` y `base_path` en `data/profile.json` y ejecuta `python tools/build.py`.

## CV (web y PDF)
El texto del CV vive en `data/cv.json` (es) y `data/cv.en.json` (en). Alimenta el folio de «Sobre mí» y, con `python tools/make_cv.py`, genera los PDF de una página (`assets/cv/Damian_Cambeiro_CV.pdf` y `..._EN.pdf`). Tras cambiar el CV: editar el JSON, ejecutar `make_cv.py` y `build.py`.

## Analítica de visitas (opcional)
GitHub Pages no ofrece estadísticas ni logs, así que se usa un contador externo sin cookies: [GoatCounter](https://www.goatcounter.com/) (gratuito para uso personal, no necesita aviso de cookies).
1. Crea una cuenta en goatcounter.com y elige un código (por ejemplo `cambeiro`; tu panel será `https://cambeiro.goatcounter.com`).
2. En `data/profile.json` pon `"analytics": {"goatcounter": "tu-codigo"}` y ejecuta `python tools/build.py`. Este sitio usa el código `udamian` (panel en `https://udamian.goatcounter.com`).
3. Haz commit y push. Sin código no se carga nada; la vista previa nunca lo carga; localhost no cuenta visitas. No pegues a mano el `<script>` de GoatCounter: el generador lo inserta y lo contarías dos veces.
Qué mide: visitas por página e idioma, país, referrer, dispositivo y eventos (`assets/eventos.js`): descarga del CV, clic en correo, LinkedIn, GitHub/repositorios, búsquedas y pestañas del buscador. No guarda lo que se escribe en el buscador. Cuando está activa, las páginas muestran una línea de privacidad. Test: `python tests/analytics.py`.

## Datos y licencias
- RelocationDevs: Stack Overflow Developer Survey 2023 (ODbL 1.0, https://opendatacommons.org/licenses/odbl/1-0/), Kaggle «Cost of Living Index» 2022, OECD Tax Database, Kaggle «World Cities Database» y Natural Earth 110m (dominio público, mapa de esta web). Confirma la licencia de cada dataset de Kaggle/OECD antes de publicar. Los agregados que se publican (medianas por país y rol, índices por ciudad) derivan de esos datos; la atribución está en «Datos clave» de la página del proyecto.
- Job Tracker: datos de ejemplo inventados (`data/tracker.json`); la app real no publica candidaturas.
- Fuentes tipográficas: ver `assets/fonts/*.LICENSE`.
- Analítica: GoatCounter (opcional, sin cookies; ver arriba).
- Aviso de parodia: todas las páginas indican que Cambeiro es un buscador ficticio, no afiliado a ninguno real.

## Lista de comprobación
**Antes de publicar:** repos enlazados (RelocationDevs, job-tracker, YTM Sync) públicos y sin `.env`, volcados ni candidaturas reales; licencias de Kaggle y OECD confirmadas; README de RelocationDevs sin enlace a la demo caída; CV al día (`python tools/make_cv.py`); `python tools/build.py` sin cambios pendientes y las pruebas en verde.

**Después de publicar:** abrir `/`, `/en/`, `/about/` y las 3 páginas de proyecto; descargar el CV (es/en); probar el correo y «Copiar correo»; comprobar que el CI sale en verde en la pestaña Actions; visitar el sitio y ver la visita en el panel de GoatCounter; pegar el enlace en LinkedIn para ver la vista previa (imagen Open Graph).
