// Genera data/land.txt: contorno de continentes (Natural Earth 110m, dominio publico) como path SVG
// en el mismo sistema del mapa: x = lon + 180, y = 90 - lat.
// Uso: NODE_PATH=<carpeta con node_modules de world-atlas y topojson-client> node tools/prep_land.js
const fs = require('fs'), path = require('path');
const topo = require('world-atlas/land-110m.json');
const { feature } = require('topojson-client');
const f = feature(topo, topo.objects.land);
const polys = f.type === 'FeatureCollection' ? f.features.flatMap(x => x.geometry.type === 'Polygon' ? [x.geometry.coordinates] : x.geometry.coordinates)
  : (f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates);
let d = '';
for (const poly of polys) for (const ring of poly) {
  if (ring.every(p => p[1] < -58)) continue;            // Antartida fuera del encuadre
  let last = '', seg = '';
  ring.forEach((p, i) => {
    const s = (p[0] + 180).toFixed(1).replace(/\.0$/, '') + ',' + (90 - p[1]).toFixed(1).replace(/\.0$/, '');
    if (s === last) return; last = s;
    seg += (seg ? 'L' : 'M') + s;
  });
  d += seg + 'Z';
}
fs.writeFileSync(path.join(__dirname, '..', 'data', 'land.txt'), d);
console.log('land.txt', d.length, 'bytes');
