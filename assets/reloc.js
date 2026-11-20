/* RelocationDevs como buscador de los 2000. Datos: window.RD (assets/reloc-data.js). Textos: window.RT / window.RM. */
(function () {
  document.documentElement.classList.add('js');
  'use strict';
  var RD = window.RD, T = window.RT, M = window.RM, LANG = M.lang;
  if (!RD || !T) return;
  var COL = ['#4a90d9', '#e8593c', '#2ecc71'];            // colores del comparador de la app
  var W0 = { p: 0.30, j: 0.25, q: 0.25, t: 0.20 };         // pesos del Relocation Score del proyecto
  var PER = 10;
  var ALIAS = { 'espana': 'spain', 'alemania': 'germany', 'francia': 'france', 'reino unido': 'united kingdom', 'inglaterra': 'united kingdom',
    'estados unidos': 'united states', 'eeuu': 'united states', 'paises bajos': 'netherlands', 'holanda': 'netherlands', 'suiza': 'switzerland',
    'italia': 'italy', 'irlanda': 'ireland', 'japon': 'japan', 'canada': 'canada', 'mexico': 'mexico', 'suecia': 'sweden', 'noruega': 'norway',
    'dinamarca': 'denmark', 'finlandia': 'finland', 'polonia': 'poland', 'belgica': 'belgium', 'brasil': 'brazil', 'rumania': 'romania',
    'grecia': 'greece', 'turquia': 'turkey', 'corea del sur': 'south korea', 'nueva zelanda': 'new zealand', 'republica checa': 'czech republic',
    'emiratos': 'united arab emirates', 'sudafrica': 'south africa', 'hungria': 'hungary', 'austria': 'austria', 'singapur': 'singapore' };

  function $(s, r) { return (r || document).querySelector(s); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function norm(s) { return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  var nf0 = new Intl.NumberFormat(LANG, { maximumFractionDigits: 0, useGrouping: 'always' });
  var nf1 = new Intl.NumberFormat(LANG, { maximumFractionDigits: 1, minimumFractionDigits: 1, useGrouping: 'always' });
  var nf2 = new Intl.NumberFormat(LANG, { maximumFractionDigits: 2, minimumFractionDigits: 2, useGrouping: 'always' });
  function eur(v) { return LANG === 'es' ? nf0.format(v) + ' €' : '€' + nf0.format(v); }
  function fill(s, o) { return s.replace(/\{(\w+)\}/g, function (_, k) { return o[k] === undefined ? '' : o[k]; }); }

  /* ---- datos ---- */
  var C = RD.cities.map(function (r, i) {
    var net = r[3] * (1 - r[5] / 100);
    var o = { i: i, name: r[0], country: r[1], reg: r[2], sal: r[3], rent: r[4], tax: r[5], col: r[6], ppi: r[7], qol: r[8], job: r[9],
      lat: r[10], lon: r[11], net: net, pp: net / r[6], sav: net * 0.3, label: r[0] + ', ' + r[1] };
    var extra = [];
    Object.keys(ALIAS).forEach(function (k) { if (ALIAS[k] === norm(r[1])) extra.push(k); });
    o.hay = norm(o.label + ' ' + RD.regions[r[2]] + ' ' + M.reg[r[2]] + ' ' + extra.join(' '));
    return o;
  });
  var MAX = {};
  ['sal', 'net', 'rent', 'tax', 'col', 'pp', 'qol', 'job', 'sav', 'ppi'].forEach(function (k) {
    MAX[k] = Math.max.apply(null, C.map(function (c) { return c[k]; }));
  });
  function score(c, w) { return Math.round((c.ppi * w.p + c.job * w.j + c.qol * w.q + Math.max(0, 100 - c.tax) * w.t) * 100) / 100; }  // redondeo a 2 decimales, como indicators.py
  C.forEach(function (c) { c.sc = score(c, W0); });
  var RANK = C.slice().sort(function (a, b) { return b.sc - a.sc; });
  RANK.forEach(function (c, k) { c.rank = k + 1; });
  var CTRY = {}, XMAP = RD.xmap || {}, XREV = {};
  C.forEach(function (c) { (CTRY[c.country] = CTRY[c.country] || []).push(c); });
  Object.keys(XMAP).forEach(function (k) { XREV[XMAP[k]] = k; });
  function survey(country) { return RD.salaries[country] ? country : (RD.salaries[XMAP[country]] ? XMAP[country] : null); }
  function cityCountry(sv) { return CTRY[sv] ? sv : (CTRY[XREV[sv]] ? XREV[sv] : null); }

  /* ---- ruta ---- */
  var views = ['home', 'res', 'city', 'adv', 'cmp', 'map', 'sal', 'about'];
  var cur = null, selRegion = -1, mapReg = -1;
  function go(path) {
    path = path.replace(/^#/, '');
    try { location.hash = path; } catch (e) { /* vista previa aislada */ }
    if (cur !== path) route(path);
  }
  function parse(h) {
    var m = h.split('?');
    return { path: m[0] || '/', qs: new URLSearchParams(m[1] || '') };
  }
  var lastView = null, booted = false;
  function show(name) {
    views.forEach(function (v) { var e = $('#v-' + v); if (e) e.hidden = v !== name; });
    $('#hd').hidden = name === 'home';
    window.scrollTo(0, 0);
    // al cambiar de vista (no en la carga inicial ni al reordenar/filtrar), el foco pasa a la vista nueva
    if (booted && lastView !== name) {
      var el = $('#v-' + name), b = el && el.querySelector('.bar b');
      if (el) { if (b) el.setAttribute('aria-label', b.textContent); el.setAttribute('tabindex', '-1'); el.focus({ preventScroll: true }); }
    }
    lastView = name;
  }
  function live(t) { $('#live').textContent = t; }
  function route(h) {
    h = (h === undefined ? location.hash.replace(/^#/, '') : h) || '/';
    cur = h;
    var r = parse(h), p = r.path;
    if (p === '/' || p === '') { show('home'); document.title = 'RelocationDevs'; return; }
    if (p === '/b') return results(r.qs);
    var m = p.match(/^\/c\/(\d+)$/);
    if (m && C[+m[1]]) return city(C[+m[1]]);
    if (p === '/adv') { show('adv'); document.title = T.adv_h || M.about; return; }
    m = p.match(/^\/cmp\/?([\d,]*)$/);
    if (m) return compare((m[1] || '').split(',').filter(Boolean).map(Number).filter(function (i) { return C[i]; }).slice(0, 3));
    if (p === '/map') return mapView(r.qs.get('c'));
    if (p === '/sal') return salary(r.qs);
    if (p === '/about') { show('about'); document.title = M.about; return; }
    show('home');
  }
  window.addEventListener('hashchange', function () { var h = location.hash.replace(/^#/, '') || '/'; if (h !== cur) route(h); });

  /* ---- busqueda ---- */
  function weights(s) {
    if (!s) return W0;
    var a = s.split(',').map(Number);
    if (a.length !== 4 || a.some(function (x) { return !isFinite(x) || x < 0; })) return W0;
    var t = a[0] + a[1] + a[2] + a[3];
    if (!t) return W0;
    return { p: a[0] / t, j: a[1] / t, q: a[2] / t, t: a[3] / t };
  }
  function isDefault(wstr) { return !wstr || wstr === '3,2.5,2.5,2'; }
  function search(o) {
    var toks = norm(o.q || '').split(/\s+/).filter(Boolean), w = weights(o.w), out = [];
    C.forEach(function (c) {
      if (o.r >= 0 && c.reg !== o.r) return;
      for (var k = 0; k < toks.length; k++) if (c.hay.indexOf(toks[k]) < 0) return;
      if (o.mn && c.net < o.mn) return;
      if (o.mr && c.rent > o.mr) return;
      if (o.mt && c.tax > o.mt) return;
      c.cs = score(c, w);
      out.push(c);
    });
    var key = { score: function (c) { return -c.cs; }, net: function (c) { return -c.net; }, pp: function (c) { return -c.pp; },
      rent: function (c) { return c.rent; }, sal: function (c) { return -c.sal; } }[o.o] || function (c) { return -c.cs; };
    out.sort(function (a, b) { return key(a) - key(b) || a.i - b.i; });
    return { list: out, toks: toks };
  }
  function hl(text, toks) {
    var s = esc(text);
    toks.forEach(function (t) {
      if (t.length < 2) return;
      s = s.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')(?![^<]*>)', 'ig'), '<b>$1</b>');
    });
    return s;
  }
  function pnum(v) { var n = parseFloat(v); return isFinite(n) && n > 0 ? n : 0; }
  function opts(qs) {
    var o = qs.get('o'), w = qs.get('w'), r = qs.get('r') === null ? -1 : parseInt(qs.get('r'), 10);
    // El hash lo controla quien envie el enlace: solo se aceptan valores conocidos (el resto se descarta).
    return { q: qs.get('q') || '', r: isFinite(r) ? r : -1, p: Math.max(1, parseInt(qs.get('p'), 10) || 1),
      o: ['score', 'net', 'pp', 'rent', 'sal'].indexOf(o) > -1 ? o : 'score',
      mn: pnum(qs.get('mn')), mr: pnum(qs.get('mr')), mt: pnum(qs.get('mt')), w: /^[\d.,]{1,40}$/.test(w || '') ? w : '' };
  }
  function qstr(o, ch) {
    var p = [], x = Object.assign({}, o, ch || {});
    if (x.q) p.push('q=' + encodeURIComponent(x.q));
    if (x.r >= 0) p.push('r=' + x.r);
    if (x.o && x.o !== 'score') p.push('o=' + encodeURIComponent(x.o));
    if (x.mn) p.push('mn=' + x.mn);
    if (x.mr) p.push('mr=' + x.mr);
    if (x.mt) p.push('mt=' + x.mt);
    if (x.w && !isDefault(x.w)) p.push('w=' + encodeURIComponent(x.w));
    if (x.p > 1) p.push('p=' + x.p);
    return '#/b' + (p.length ? '?' + p.join('&') : '');
  }
  var lastCmp = [];
  function cmpHref(i) {
    var l = lastCmp.filter(function (x) { return x !== i; }).slice(-2).concat([i]);
    return '#/cmp/' + l.join(',');
  }
  function results(qs) {
    var o = opts(qs), t0 = performance.now();
    var res = search(o), L = res.list, n = L.length;
    var pages = Math.max(1, Math.ceil(n / PER)), pg = Math.min(o.p, pages), a = (pg - 1) * PER;
    var secs = ((performance.now() - t0) / 1000).toFixed(3).replace('.', LANG === 'es' ? ',' : '.');
    show('res');
    $('#hq').value = o.q; $('#hr').value = String(o.r);
    document.title = (o.q || T.cities) + ' - RelocationDevs';
    $('#rc').textContent = n ? fill(T.res, { a: a + 1, b: Math.min(n, a + PER), n: nf0.format(n) }) + ' ' + fill(T.secs, { t: secs }) : fill(T.secs, { t: secs });
    var note = $('#rn'), custom = !isDefault(o.w), w = weights(o.w);
    note.hidden = !custom;
    if (custom) note.textContent = fill(T.w_on, { p: pc(w.p), j: pc(w.j), q: pc(w.q), t: pc(w.t) });
    var h = '';
    h += '<p class="so">' + T.sort + ': ' + Object.keys(T.sort_l).map(function (k) {
      return k === o.o || (k === 'score' && !o.o) ? '<b>' + T.sort_l[k] + '</b>' : '<a href="' + qstr(o, { o: k, p: 1 }) + '">' + T.sort_l[k] + '</a>';
    }).join(' · ') + '</p>';
    if (!n) {
      h += '<p class="none">' + esc(fill(T.none, { q: o.q })) + '</p><p class="sm">' + esc(T.none_tip) + '</p>';
    } else {
      h += '<ol class="rl2">' + L.slice(a, a + PER).map(function (c) {
        var sc = custom ? c.cs : c.sc;
        return '<li class="rs"><h2><a href="#/c/' + c.i + '">' + hl(c.name, res.toks) + ', ' + hl(c.country, res.toks) + '</a></h2>' +
          '<p class="sn">' + T.avg + ' <b>' + eur(c.sal) + '</b> · ' + T.net + ' ' + eur(c.net) + ' · ' + T.rent + ' ' + eur(c.rent) + T.mo +
          ' · ' + T.tax + ' ' + nf1.format(c.tax) + ' %. ' + (custom ? T.custom : T.score) + ': <b>' + nf1.format(sc) + '</b>.</p>' +
          '<p class="ur">' + T.crumb + ' › ' + esc(M.reg[c.reg]) + ' - <a href="' + cmpHref(c.i) + '">' + T.cmp_add + '</a>' +
          (c.lat === null ? '' : ' - <a href="#/map?c=' + c.i + '">' + T.on_map + '</a>') + '</p></li>';
      }).join('') + '</ol>';
      h += pager(o, pg, pages);
    }
    $('#rs').innerHTML = h;
    live($('#rc').textContent);
  }
  function pc(v) { return Math.round(v * 100) + ' %'; }
  function pager(o, pg, pages) {
    if (pages < 2) return '';
    var from = Math.max(1, Math.min(pg - 4, pages - 9)), to = Math.min(pages, from + 9), s = '<nav class="pg" aria-label="' + T.page + '">';
    if (pg > 1) s += '<a class="pn" href="' + qstr(o, { p: pg - 1 }) + '">‹ ' + T.prev + '</a>';
    s += '<span class="pl">Rel<span class="r1">o</span>';
    for (var k = from; k <= to; k++) {
      s += '<span class="po"><i style="color:' + COL[(k + 1) % 3] + '">o</i>' +
        (k === pg ? '<b aria-current="page">' + k + '</b>' : '<a href="' + qstr(o, { p: k }) + '">' + k + '</a>') + '</span>';
    }
    s += '<span class="r1">cation</span></span>';
    if (pg < pages) s += '<a class="pn" href="' + qstr(o, { p: pg + 1 }) + '">' + T.next + ' ›</a>';
    return s + '</nav>';
  }

  /* ---- ciudad ---- */
  var KEYS = ['sal', 'net', 'rent', 'tax', 'col', 'pp', 'qol', 'job', 'sav'];
  function city(c) {
    show('city');
    document.title = c.label + ' - RelocationDevs';
    var tinv = Math.max(0, 100 - c.tax);
    var parts = [[T.m.ppi, c.ppi, W0.p], [T.m.job, c.job, W0.j], [T.m.qol, c.qol, W0.q], [T.w_t_lbl || M.w.t + ' (100 − ' + nf1.format(c.tax) + ')', tinv, W0.t]];
    var tot = parts.reduce(function (a, r) { return a + r[1] * r[2]; }, 0) || 1;
    var shades = ['#f5f5f7', '#c7c7cc', '#8e8e93', '#48484a'];
    var h = '<div class="fh"><div class="ftop"><div><h2 class="fn">' + esc(c.label) + '</h2><p class="fs">' + esc(M.reg[c.reg]) + '</p></div>' +
      '<div class="fsc"><p class="fnum">' + nf2.format(c.sc) + '</p><p class="fcap">' + esc(T.m.score) + '<br><b>' + esc(fill(T.rank, { r: c.rank, n: C.length })) + '</b></p></div></div>' +
      '<div class="fbar" role="img" aria-label="' + esc(T.f_aria) + '">' + parts.map(function (r, k) {
        return '<i style="flex:' + (r[1] * r[2] / tot * 100).toFixed(2) + ';background:' + shades[k] + '"></i>';
      }).join('') + '</div><div class="fleg">' + parts.map(function (r, k) {
        return '<div style="border-top-color:' + shades[k] + '"><b>' + esc(r[0]) + '</b><br>' + nf2.format(r[1]) + ' × ' + nf2.format(r[2]) + ' = ' + nf2.format(r[1] * r[2]) + '</div>';
      }).join('') + '</div><p class="fsum">' + esc(T.f_sum) + ' ' + parts.map(function (r) { return nf2.format(r[1] * r[2]); }).join(' + ') +
      ' = <b>' + nf2.format(c.sc) + '</b>. ' + esc(T.f_note) + '</p></div>';
    h += '<table class="tb"><tbody>';
    KEYS.forEach(function (k) {
      var v = c[k], txt = (k === 'tax') ? nf1.format(v) + ' %' : (k === 'qol' || k === 'job' || k === 'col') ? nf1.format(v) :
        (k === 'pp') ? nf1.format(v) : eur(v);
      var low = (k === 'rent' || k === 'tax' || k === 'col');
      h += '<tr><th scope="row">' + T.m[k] + (low ? ' <span class="dim">' + T.lower + '</span>' : '') + '</th><td>' + txt +
        '</td><td class="bc" aria-hidden="true"><i style="width:' + Math.max(2, v / MAX[k] * 100).toFixed(1) + '%"></i></td></tr>';
    });
    h += '</tbody></table>';
    h += '<p class="ln"><a href="' + cmpHref(c.i) + '">' + T.add_cmp + '</a>' +
      (c.lat === null ? ' · <span class="dim">' + T.no_geo + '</span>' : ' · <a href="#/map?c=' + c.i + '">' + T.see_map + '</a>') +
      (survey(c.country) ? ' · <a href="#/sal?c=' + encodeURIComponent(survey(c.country)) + '">' + esc(fill(T.sal_link, { c: c.country })) + '</a>' : '') + '</p>';
    h += '<h2>' + T.sim_h + '</h2><ul class="sim">' + similar(c).map(function (s) {
      return '<li><a href="#/c/' + s.i + '">' + esc(s.label) + '</a> <span class="dim">' + nf1.format(s.sc) + '</span></li>';
    }).join('') + '</ul>';
    $('#cy').innerHTML = h;
    lastCmp = [c.i];
    live(c.label);
  }
  var SD = ['ppi', 'qol', 'job', 'tax', 'col'].map(function (k) {
    var m = C.reduce(function (a, c) { return a + c[k]; }, 0) / C.length;
    return { k: k, s: Math.sqrt(C.reduce(function (a, c) { return a + Math.pow(c[k] - m, 2); }, 0) / C.length) || 1 };
  });
  function similar(c) {
    return C.filter(function (x) { return x !== c; }).map(function (x) {
      var d = SD.reduce(function (a, f) { return a + Math.pow((x[f.k] - c[f.k]) / f.s, 2); }, 0);
      return { c: x, d: d };
    }).sort(function (a, b) { return a.d - b.d; }).slice(0, 5).map(function (r) { return r.c; });
  }

  /* ---- comparador ---- */
  var CK = [['score', 1], ['sal', 1], ['net', 1], ['rent', -1], ['tax', -1], ['col', -1], ['pp', 1], ['qol', 1], ['job', 1], ['sav', 1]];
  var byLabel = {};
  C.forEach(function (c) { byLabel[norm(c.label)] = c; });
  function compare(ids) {
    show('cmp');
    document.title = T.cities + ' - ' + M.about;
    lastCmp = ids.slice();
    if (!$('#dl').children.length) $('#dl').innerHTML = C.map(function (c) { return '<option value="' + esc(c.label) + '">'; }).join('');
    for (var k = 0; k < 3; k++) $('#c' + k).value = ids[k] !== undefined ? C[ids[k]].label : '';
    var el = $('#cp');
    if (ids.length < 2) { el.innerHTML = '<p class="none">' + T.cmp_need + '</p>'; return; }
    var cs = ids.map(function (i) { return C[i]; });
    var h = '<div class="tw"><table class="tb cmpt"><thead><tr><th scope="col">' + T.metric + '</th>' + cs.map(function (c, k) {
      return '<th scope="col" style="border-color:' + COL[k] + '"><a href="#/c/' + c.i + '">' + esc(c.name) + '</a><span class="dim">' + esc(c.country) + '</span></th>';
    }).join('') + '</tr></thead><tbody>';
    CK.forEach(function (r) {
      var k = r[0], vals = cs.map(function (c) { return k === 'score' ? c.sc : c[k]; }), mx = Math.max.apply(null, vals);
      var best = r[1] > 0 ? mx : Math.min.apply(null, vals);
      h += '<tr><th scope="row">' + T.m[k] + (r[1] < 0 ? ' <span class="dim">' + T.lower + '</span>' : '') + '</th>' + vals.map(function (v, j) {
        var txt = (k === 'tax') ? nf1.format(v) + ' %' : (k === 'qol' || k === 'job' || k === 'col' || k === 'score' || k === 'pp') ? nf1.format(v) : eur(v);
        var isB = v === best;
        return '<td class="' + (isB ? 'best' : '') + '"><span>' + (isB ? '<b>' + txt + '</b><span class="sr"> (' + T.best + ')</span>' : txt) + '</span><i class="cb" aria-hidden="true"><u style="width:' +
          Math.max(2, v / mx * 100).toFixed(1) + '%;background:' + COL[j] + '"></u></i></td>';
      }).join('') + '</tr>';
    });
    el.innerHTML = h + '</tbody></table></div>';
  }

  /* ---- mapa ---- */
  var GEO = C.filter(function (c) { return c.lat !== null; });
  var mapSel = null;
  function drawMap() {
    var s = RD.land ? '<path class="ld" d="' + RD.land + '"/>' : '';
    for (var lon = -180; lon <= 180; lon += 30) s += '<line class="gr" x1="' + (lon + 180) + '" y1="15" x2="' + (lon + 180) + '" y2="140"/>';
    for (var lat = -60; lat <= 90; lat += 30) if (90 - lat >= 15 && 90 - lat <= 140) s += '<line class="gr' + (lat === 0 ? ' eq' : '') + '" x1="0" y1="' + (90 - lat) + '" x2="360" y2="' + (90 - lat) + '"/>';
    GEO.slice().sort(function (a, b) { return a.sc - b.sc; }).forEach(function (c) {
      if (mapReg >= 0 && c.reg !== mapReg) return;
      var k = c.sc >= 90 ? 'hi' : c.sc >= 60 ? 'md' : 'lo';
      s += '<circle class="d ' + k + (mapSel === c ? ' sel' : '') + '" data-i="' + c.i + '" cx="' + (c.lon + 180).toFixed(2) + '" cy="' + (90 - c.lat).toFixed(2) + '" r="' + (k === 'hi' ? 1.9 : k === 'md' ? 1.4 : 1.1) + '"/>';
    });
    $('#mp').innerHTML = s;
    var top = GEO.filter(function (c) { return mapReg < 0 || c.reg === mapReg; }).sort(function (a, b) { return b.sc - a.sc; }).slice(0, 10);
    $('#mt').innerHTML = '<h2>' + T.map_top + '</h2><ol class="sim">' + top.map(function (c) {
      return '<li><a href="#/map?c=' + c.i + '">' + esc(c.label) + '</a> <span class="dim">' + nf1.format(c.sc) + '</span></li>';
    }).join('') + '</ol><p class="lg2"><span class="d hi"></span> ≥ 90 <span class="d md"></span> 60–90 <span class="d lo"></span> &lt; 60 · ' + T.map_leg + '</p>';
    $('#mi').innerHTML = mapSel ? '<b>' + esc(mapSel.label) + '</b> · ' + T.score + ' ' + nf1.format(mapSel.sc) + ' · ' + eur(mapSel.net) + ' · <a href="#/c/' + mapSel.i + '">' + esc(T.cities) + ' ›</a>' : esc(T.map_pick);
  }
  function mapView(sel) {
    show('map');
    document.title = T.cities + ' - ' + M.about;
    var rad = $('#mrad');
    if (!rad.children.length) {
      rad.innerHTML = [-1, 0, 1, 2, 3, 4, 5, 6].map(function (r) {
        return '<label><input type="radio" name="mr" value="' + r + '"' + (r === -1 ? ' checked' : '') + '> ' + (r < 0 ? M.all : M.reg[r]) + '</label>';
      }).join('');
      rad.addEventListener('change', function (e) { mapReg = +e.target.value; drawMap(); });
      $('#mp').addEventListener('click', function (e) {
        var i = e.target.getAttribute && e.target.getAttribute('data-i');
        if (i === null || i === undefined) return;
        mapSel = C[+i]; drawMap();
      });
    }
    mapSel = sel !== null && sel !== undefined && C[+sel] && C[+sel].lat !== null ? C[+sel] : mapSel;
    if (mapSel && mapReg >= 0 && mapSel.reg !== mapReg) mapReg = -1;
    var radios = rad.querySelectorAll('input');
    for (var k = 0; k < radios.length; k++) radios[k].checked = +radios[k].value === mapReg;
    drawMap();
  }

  /* ---- portada: mapa de puntos (las ciudades con coordenadas se encienden al escribir) ---- */
  (function () {
    var hm = $('#hm'), box = $('#dots');
    if (!hm || !box) return;
    var s = RD.land ? '<path class="ld" d="' + RD.land + '"/>' : '';
    GEO.forEach(function (c) { s += '<circle class="hd" data-i="' + c.i + '" cx="' + (c.lon + 180).toFixed(2) + '" cy="' + (90 - c.lat).toFixed(2) + '" r="1.3"/>'; });
    var vigo = GEO.filter(function (c) { return c.name === 'Vigo'; })[0], mk = '';
    if (vigo) {
      var x = vigo.lon + 180, y = 90 - vigo.lat;
      mk = '<g class="vg"><circle cx="' + x.toFixed(2) + '" cy="' + y.toFixed(2) + '" r="4.2"/><path d="M' + x.toFixed(2) + ' ' + (y - 4.2).toFixed(2) + 'V' + (y - 20).toFixed(2) + '"/>' +
        '<text x="' + (x + 2.5).toFixed(2) + '" y="' + (y - 21.5).toFixed(2) + '">' + esc(fill(T.hm_rank, { c: vigo.name, r: vigo.rank, n: C.length })) + '</text></g>';
    }
    hm.innerHTML = s + mk;
    box.hidden = false;
    var dots = hm.querySelectorAll('.hd'), note = $('#hmn'), base = note.textContent;
    function paint() {
      var q = $('#pq').value.trim(), r = document.querySelector('input[name=hr]:checked'), rv = r ? +r.value : -1;
      if (!q && rv < 0) { hm.classList.remove('q'); for (var i = 0; i < dots.length; i++) dots[i].classList.remove('on'); note.textContent = base; return; }
      var lit = {}, n = 0;
      search({ q: q, r: rv, o: 'score' }).list.forEach(function (c) { lit[c.i] = 1; });
      for (var k = 0; k < dots.length; k++) { var on = !!lit[dots[k].getAttribute('data-i')]; dots[k].classList.toggle('on', on); if (on) n++; }
      hm.classList.add('q');
      note.textContent = n ? fill(T.dots_hit, { k: n }) : T.dots_none;
    }
    $('#pq').addEventListener('input', paint);
    Array.prototype.forEach.call(document.querySelectorAll('input[name=hr]'), function (el) { el.addEventListener('change', paint); });
  })();

  /* ---- salarios ---- */
  var SALMAX = 0;
  Object.keys(RD.salaries).forEach(function (k) { if (RD.salaries[k].all[0] >= 10) SALMAX = Math.max(SALMAX, RD.salaries[k].all[2]); });
  SALMAX = Math.ceil(SALMAX * 1.25 / 10000) * 10000;
  function salary(qs) {
    show('sal');
    document.title = T.cities + ' - ' + M.about;
    var sc = $('#sc'), sr = $('#sr');
    if (!sc.children.length) {
      sc.innerHTML = Object.keys(RD.salaries).map(function (k) { return '<option value="' + esc(k) + '">' + esc(k) + '</option>'; }).join('');
      sr.innerHTML = '<option value="-1">' + esc(M.role_all) + '</option>' + RD.roles.map(function (r, i) { return '<option value="' + i + '">' + esc(r) + '</option>'; }).join('');
      sc.addEventListener('change', drawS); sr.addEventListener('change', drawS);
      sc.value = RD.salaries.Spain ? 'Spain' : sc.value;
    }
    var q = qs.get('c');
    if (q && Object.prototype.hasOwnProperty.call(RD.salaries, q)) sc.value = q;
    drawS();
    function drawS() {
      var c = sc.value, role = +sr.value, e = RD.salaries[c], st = e.all, few = false;
      if (role >= 0) { if (e.roles[role]) st = e.roles[role]; else few = true; }
      var pct = function (v) { return Math.min(100, v / SALMAX * 100).toFixed(1); };
      var h = '<div class="sal"><p class="sn big2">' + T.median + ': <b>' + eur(st[2]) + '</b> <span class="dim">· ' + fill(T.n_resp, { n: nf0.format(st[0]) }) + '</span></p>';
      if (few) h += '<p class="note">' + esc(fill(T.few, { c: c })) + '</p>';
      h += '<p class="sm">' + T.iqr + ': ' + eur(st[1]) + ' – ' + eur(st[3]) + '</p>' +
        '<div class="rg" role="img" aria-label="' + T.iqr + '"><i class="rb" style="left:' + pct(st[1]) + '%;width:' + (pct(st[3]) - pct(st[1])).toFixed(1) + '%"></i><i class="md2" style="left:' + pct(st[2]) + '%"></i></div>' +
        '<div class="sc2"><span>0</span><span>' + eur(SALMAX / 2) + '</span><span>' + eur(SALMAX) + '</span></div>';
      var cc = cityCountry(c), n = cc ? CTRY[cc].length : 0;
      h += '<p class="ln">' + (n ? '<a href="#/b?q=' + encodeURIComponent(cc) + '">' + esc(fill(T.see_cities, { n: n, c: c })) + '</a>' : '<span class="dim">' + esc(fill(T.no_cities, { c: c })) + '</span>') + '</p>';
      var rows = Object.keys(RD.salaries).map(function (k) { var x = role >= 0 ? RD.salaries[k].roles[role] : RD.salaries[k].all; return x && x[0] >= 10 ? { k: k, x: x } : null; })
        .filter(Boolean).sort(function (a, b) { return b.x[2] - a.x[2]; }).slice(0, 10);
      h += '<h2>' + T.top_c + '</h2><table class="tb"><tbody>' + rows.map(function (r) {
        return '<tr class="' + (r.k === c ? 'me' : '') + '"><th scope="row">' + esc(r.k) + '</th><td>' + eur(r.x[2]) + '</td><td class="bc" aria-hidden="true"><i style="width:' + (r.x[2] / rows[0].x[2] * 100).toFixed(1) + '%"></i></td></tr>';
      }).join('') + '</tbody></table><p class="sm">' + esc(T.sal_note) + '</p></div>';
      $('#so').innerHTML = h;
    }
  }

  /* ---- formularios y arranque ---- */
  function submitSimple(q, r) { go(qstr({ q: q.trim(), r: r, o: 'score', p: 1 })); }
  $('#pf').addEventListener('submit', function (e) {
    e.preventDefault();
    var r = document.querySelector('input[name=hr]:checked');
    submitSimple($('#pq').value, r ? +r.value : -1);
  });
  $('#hf').addEventListener('submit', function (e) { e.preventDefault(); submitSimple($('#hq').value, +$('#hr').value); });
  $('#lucky').addEventListener('click', function () {
    var r = document.querySelector('input[name=hr]:checked'), res = search({ q: $('#pq').value, r: r ? +r.value : -1, o: 'score' });
    go('/c/' + (res.list.length ? res.list[0].i : RANK[0].i));
  });
  var wids = ['wp', 'wj', 'wq', 'wt'], wdef = [3, 2.5, 2.5, 2];
  wids.forEach(function (id) {
    var el = $('#' + id), out = el.nextElementSibling;
    el.addEventListener('input', function () { out.textContent = el.value; });
  });
  $('#areset').addEventListener('click', function () {
    wids.forEach(function (id, k) { var el = $('#' + id); el.value = wdef[k]; el.nextElementSibling.textContent = wdef[k]; });
  });
  $('#af').addEventListener('submit', function (e) {
    e.preventDefault();
    var w = wids.map(function (id) { return $('#' + id).value; }).join(',');
    go(qstr({ q: $('#aq').value.trim(), r: +$('#ar').value, o: 'score', p: 1, mn: pnum($('#an').value), mr: pnum($('#am').value), mt: pnum($('#at').value), w: w }));
  });
  ['c0', 'c1', 'c2'].forEach(function (id) {
    $('#' + id).addEventListener('change', function () {
      var ids = ['c0', 'c1', 'c2'].map(function (x) { var c = byLabel[norm($('#' + x).value.trim())]; return c ? c.i : null; }).filter(function (x) { return x !== null; });
      var u = ids.filter(function (x, k) { return ids.indexOf(x) === k; });
      go('#/cmp/' + u.join(','));
    });
  });
  document.documentElement.className += ' js';
  route();
  booted = true;
})();
