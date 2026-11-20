/* Job Tracker (maqueta): candidaturas de ejemplo en memoria. Sin dependencias.
   Misma logica que la app: «Sin respuesta» tras 21 dias sin novedades, tasas, embudo y eficacia por tipo. */
(function () {
  var d = document, TJ = window.TJ, T = TJ.t, LANG = TJ.lang, STALE = 21;
  var ORDER = ['enviada', 'sinresp', 'contactado', 'entrevista', 'rechazada'];
  var seed = JSON.parse(JSON.stringify(TJ.items));
  var items = JSON.parse(JSON.stringify(seed));
  var nextId = 100, sel = null, folder = 'all', q = '', view = 'tbl', sortK = 'ago', sortD = 1;
  var goals = { g1: 5, g2: 25 };
  try { var gs = JSON.parse(localStorage.getItem('jt-goals')); if (gs && gs.g1 > 0 && gs.g2 > 0) goals = gs; } catch (e) { /* sin almacenamiento */ }

  function $(id) { return d.getElementById(id); }
  function h(tag, attrs, kids) {
    var el = d.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'class') el.className = attrs[k];
      else if (k === 'text') el.textContent = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else el.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (k) { if (k != null) el.appendChild(typeof k === 'string' ? d.createTextNode(k) : k); });
    return el;
  }
  function fill(s, o) { return s.replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function stOf(it) { return it.st === 'enviada' && it.news > STALE ? 'sinresp' : it.st; }
  function dateOf(ago) { var x = new Date(); x.setHours(12, 0, 0, 0); x.setDate(x.getDate() - ago); return x; }
  function fmt(ago, long) { return dateOf(ago).toLocaleDateString(LANG, long ? { day: 'numeric', month: 'long' } : { day: 'numeric', month: 'short' }); }
  function days(n) { return n === 0 ? T.today_l : n + ' ' + (n === 1 ? T.d1 : T.dn); }
  function say(msg) { $('st').textContent = msg; }
  function pct(a, b) { return b ? Math.round(a * 1000 / b) / 10 : 0; }
  function nf(v) { return v.toLocaleString(LANG, { maximumFractionDigits: 1 }); }

  /* ------------------------------------------------ metricas */
  function stats() {
    var n = items.length, c = { enviada: 0, sinresp: 0, contactado: 0, entrevista: 0, rechazada: 0 };
    items.forEach(function (i) { c[stOf(i)]++; });
    var dow = (new Date().getDay() + 6) % 7;
    var today = items.filter(function (i) { return i.ago === 0; }).length;
    var week = items.filter(function (i) { return i.ago <= dow; }).length;
    var resp = c.contactado + c.entrevista + c.rechazada;
    return { n: n, c: c, today: today, week: week, resp: resp, rr: pct(resp, n), ir: pct(c.entrevista, n) };
  }

  function bar(cls, pc, label) { return h('span', { class: 'bar ' + cls, style: 'width:' + Math.max(pc, 0) + '%', title: label }); }

  /* ------------------------------------------------ resumen */
  function renderSummary(S) {
    var v = [S.n, S.today, S.week, S.resp, S.c.contactado, S.c.entrevista, S.c.rechazada, nf(S.rr) + '%', nf(S.ir) + '%'];
    v.forEach(function (x, i) { $('k' + i).textContent = x; });
    $('n1').textContent = S.today; $('p1').max = goals.g1; $('p1').value = Math.min(S.today, goals.g1);
    $('n2').textContent = S.week; $('p2').max = goals.g2; $('p2').value = Math.min(S.week, goals.g2);
    $('g1').value = goals.g1; $('g2').value = goals.g2;
    say(fill(T.status, { n: S.n, s: S.c.sinresp }));
  }

  /* ------------------------------------------------ estancados */
  function renderStale(S) {
    var st = items.filter(function (i) { return stOf(i) === 'sinresp'; }).sort(function (a, b) { return b.news - a.news; });
    $('sn').textContent = st.length;
    $('sp').textContent = st.length ? fill(T.stale_p, { n: STALE }) : T.stale_none;
    var ul = $('sl'); ul.textContent = '';
    st.forEach(function (i) {
      ul.appendChild(h('li', null, [
        h('div', { class: 'si' }, [h('b', { text: i.co }), h('span', { text: i.role + ' · ' + T.st.enviada + ' ' + fmt(i.ago) })]),
        h('span', { class: 'dg', text: days(i.news) }),
        h('span', { class: 'sa' }, [
          h('button', { type: 'button', class: 'bt', text: T.follow, 'aria-label': T.follow + ': ' + i.co, onclick: function () { follow(i.id); } }),
          h('button', { type: 'button', class: 'bt', text: T.reject, 'aria-label': T.reject + ': ' + i.co, onclick: function () { move(i.id, 'rechazada'); } })])]));
    });
  }

  /* ------------------------------------------------ carpetas */
  function renderFolders(S) {
    var ul = $('fo'); ul.textContent = '';
    [['all', T.all, S.n]].concat(ORDER.map(function (k) { return [k, T.st[k], S.c[k]]; })).forEach(function (f) {
      var b = h('button', { type: 'button', 'aria-pressed': folder === f[0] ? 'true' : 'false', 'data-k': f[0], onclick: function () { folder = f[0]; renderList(); renderFolders(stats()); } },
        [h('span', { class: 'dot s-' + f[0] }), h('span', { class: 'fn', text: f[1] }), h('b', { text: String(f[2]) })]);
      ul.appendChild(h('li', null, [b]));
    });
  }

  /* ------------------------------------------------ lista */
  function visible() {
    var t = norm(q.trim());
    var v = items.filter(function (i) {
      return (folder === 'all' || stOf(i) === folder) && (!t || norm(i.co + ' ' + i.role).indexOf(t) > -1);
    });
    v.sort(function (a, b) {
      var x, y;
      if (sortK === 'co' || sortK === 'role') { x = norm(a[sortK]); y = norm(b[sortK]); }
      else if (sortK === 'type' || sortK === 'mode') { x = T[sortK === 'type' ? 'ty' : 'mo'][a[sortK]]; y = T[sortK === 'type' ? 'ty' : 'mo'][b[sortK]]; }
      else if (sortK === 'st') { x = ORDER.indexOf(stOf(a)); y = ORDER.indexOf(stOf(b)); }
      else { x = a[sortK]; y = b[sortK]; }
      return (x < y ? -1 : x > y ? 1 : 0) * sortD || a.id - b.id;
    });
    return v;
  }
  function badge(i) { var k = stOf(i); return h('span', { class: 'bd s-' + k, text: T.st[k] }); }

  function renderList() {
    var v = visible(), box = $('lv'); box.textContent = '';
    $('vt').setAttribute('aria-pressed', view === 'tbl'); $('vk').setAttribute('aria-pressed', view === 'kan');
    if (!v.length) { box.appendChild(h('p', { class: 'empty', text: T.empty })); return; }
    if (view === 'kan') {
      var kb = h('div', { class: 'kan' });
      ORDER.forEach(function (k) {
        var col = v.filter(function (i) { return stOf(i) === k; });
        var ul = h('ul');
        col.forEach(function (i) {
          ul.appendChild(h('li', null, [h('button', { type: 'button', class: 'cd', 'aria-pressed': sel === i.id ? 'true' : 'false', onclick: function () { pick(i.id); } },
            [h('b', { text: i.co }), h('span', { text: i.role }), h('small', { text: fmt(i.ago) + ' · ' + T.ty[i.type] })])]));
        });
        kb.appendChild(h('section', { class: 'kc s-' + k, 'aria-label': T.st[k] }, [h('h3', null, [T.st[k], ' ', h('b', { text: String(col.length) })]), ul]));
      });
      box.appendChild(kb); return;
    }
    var keys = ['co', 'role', 'type', 'mode', 'st', 'ago', 'news'], cls = ['', 'ro', 'ty', 'mo', '', 'dt2', 'nw'];
    var tr = h('tr');
    T.cols.forEach(function (c, n) {
      var k = keys[n], th = h('th', { scope: 'col', class: cls[n], 'aria-sort': sortK === k ? (sortD > 0 ? 'ascending' : 'descending') : 'none' },
        [h('button', { type: 'button', text: c + (sortK === k ? (sortD > 0 ? ' ▲' : ' ▼') : ''), onclick: function () { if (sortK === k) sortD = -sortD; else { sortK = k; sortD = 1; } renderList(); } })]);
      tr.appendChild(th);
    });
    var tb = h('tbody');
    v.forEach(function (i) {
      tb.appendChild(h('tr', { class: sel === i.id ? 'on' : '' }, [
        h('th', { scope: 'row' }, [h('button', { type: 'button', text: i.co, 'aria-pressed': sel === i.id ? 'true' : 'false', onclick: function () { pick(i.id); } }), h('small', { class: 'rs', text: i.role })]),
        h('td', { class: 'ro', text: i.role }), h('td', { class: 'ty', text: T.ty[i.type] }), h('td', { class: 'mo', text: T.mo[i.mode] }),
        h('td', null, [badge(i)]), h('td', { class: 'dt2', text: fmt(i.ago) }), h('td', { class: 'nw', text: days(i.news) })]));
    });
    box.appendChild(h('div', { class: 'tw' }, [h('table', null, [h('thead', null, [tr]), tb])]));
  }

  /* ------------------------------------------------ detalle */
  function renderDetail() {
    var box = $('dt'); box.textContent = '';
    var it = items.filter(function (i) { return i.id === sel; })[0];
    box.appendChild(h('h2', { text: T.dt_h }));
    if (!it) { box.appendChild(h('p', { class: 'sm', text: T.pick })); return; }
    var dl = h('dl', null, [
      h('dt', { text: T.cols[0] }), h('dd', null, [h('b', { text: it.co })]),
      h('dt', { text: T.cols[1] }), h('dd', { text: it.role }),
      h('dt', { text: T.cols[4] }), h('dd', null, [badge(it)]),
      h('dt', { text: T.applied }), h('dd', { text: fmt(it.ago, true) + ' · ' + (it.ago === 0 ? T.today_l : fill(T.ago, { n: it.ago })) }),
      h('dt', { text: T.news }), h('dd', { text: it.news === 0 ? T.today_l : fill(T.ago, { n: it.news }) }),
      h('dt', { text: T.type_l }), h('dd', { text: T.ty[it.type] }),
      h('dt', { text: T.mode_l }), h('dd', { text: T.mo[it.mode] })]);
    var info = h('div', { class: 'di' }, [dl]);
    var acts = h('p', { class: 'ac' });
    ['contactado', 'entrevista', 'rechazada', 'enviada'].forEach(function (k) {
      acts.appendChild(h('button', { type: 'button', class: 'bt', 'aria-pressed': it.st === k ? 'true' : 'false', text: T.st[k], onclick: function () { move(it.id, k); } }));
    });
    var side = h('div', { class: 'da' }, [h('p', { class: 'mv', text: T.move }), acts,
      h('p', { class: 'ac' }, [h('button', { type: 'button', class: 'bt', text: T.follow, onclick: function () { follow(it.id); } }),
        h('button', { type: 'button', class: 'bt dn', text: T.del, onclick: function () { del(it.id); } })]),
      h('p', { class: 'sm', text: T.sin_note })]);
    box.appendChild(h('div', { class: 'dtb' }, [info, side]));
  }

  /* ------------------------------------------------ estadisticas */
  function renderCharts(S) {
    // semanas
    var wk = {}, monday = function (ago) { var x = dateOf(ago), g = (x.getDay() + 6) % 7; x.setDate(x.getDate() - g); return x.getTime(); };
    items.forEach(function (i) { var k = monday(i.ago); wk[k] = (wk[k] || 0) + 1; });
    var ks = Object.keys(wk).map(Number).sort(function (a, b) { return a - b; }).slice(-8), mx = Math.max.apply(null, ks.map(function (k) { return wk[k]; }).concat([1]));
    var c1 = $('c1'); c1.textContent = '';
    var cols = h('div', { class: 'cols' });
    ks.forEach(function (k) {
      var lab = new Date(k).toLocaleDateString(LANG, { day: 'numeric', month: 'short' });
      cols.appendChild(h('div', { class: 'col', title: fill(T.wk, { d: lab }) + ': ' + wk[k] }, [h('b', { text: String(wk[k]) }), h('span', { class: 'cb', style: 'height:' + Math.round(wk[k] * 100 / mx) + '%' }), h('small', { text: lab })]));
    });
    c1.appendChild(cols);
    // embudo
    var fv = [S.n, S.c.contactado + S.c.entrevista, S.c.entrevista, S.c.rechazada], c2 = $('c2'); c2.textContent = '';
    var cl = ['s-enviada', 's-contactado', 's-entrevista', 's-rechazada'];
    fv.forEach(function (n, i) {
      c2.appendChild(h('div', { class: 'row' }, [h('span', { class: 'rl', text: T.f[i] }), h('span', { class: 'rb' }, [bar(cl[i], S.n ? n * 100 / S.n : 0, '')]), h('b', { class: 'rv', text: String(n) })]));
    });
    // eficacia por tipo
    var c3 = $('c3'); c3.textContent = '';
    var g = {}; items.forEach(function (i) { var o = g[i.type] || (g[i.type] = { n: 0, r: 0 }); o.n++; if (i.st !== 'enviada') o.r++; });
    var tk = Object.keys(g).sort(function (a, b) { return pct(g[b].r, g[b].n) - pct(g[a].r, g[a].n) || g[b].n - g[a].n; });
    if (!tk.length) c3.appendChild(h('p', { class: 'sm', text: T.nodata }));
    tk.forEach(function (k) {
      var p = pct(g[k].r, g[k].n);
      c3.appendChild(h('div', { class: 'row' }, [h('span', { class: 'rl', text: T.ty[k] }), h('span', { class: 'rb' }, [bar('s-contactado', p, '')]),
        h('b', { class: 'rv', text: nf(p) + '%' }), h('small', { class: 'rn', text: fill(T.resp, { a: g[k].r, b: g[k].n }) })]));
    });
  }

  function all() { var S = stats(); renderSummary(S); renderStale(S); renderFolders(S); renderList(); renderDetail(); renderCharts(S); }

  /* ------------------------------------------------ acciones */
  function byId(id) { return items.filter(function (i) { return i.id === id; })[0]; }
  function pick(id) {
    sel = id; renderList(); renderDetail();
    // el listado se repinta: devolver el foco al elemento elegido y asegurar que el detalle se ve
    var b = document.querySelector('.ls [aria-pressed=true]'); if (b) b.focus({ preventScroll: true });
    var dt = document.querySelector('.dt');
    if (dt && dt.getBoundingClientRect().top > window.innerHeight - 80 && dt.scrollIntoView) dt.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }
  function move(id, st) { var it = byId(id); if (!it) return; it.st = st; it.news = 0; sel = id; all(); say(fill(T.moved, { co: it.co, st: T.st[stOf(it)] })); }
  function follow(id) { var it = byId(id); if (!it) return; it.news = 0; all(); say(fill(T.followed, { co: it.co })); }
  function del(id) { var it = byId(id); if (!it) return; items = items.filter(function (i) { return i.id !== id; }); sel = null; all(); say(fill(T.deleted, { co: it.co })); }

  var KEYS = { enviada: 'enviada sent', contactado: 'contactado contacted', entrevista: 'entrevista interview', rechazada: 'rechazada rejected' };
  function parse(txt) {
    var st = 'enviada', m = txt.match(/(?:^|\s)@(\S+)/);
    if (m) {
      var w = norm(m[1]);
      Object.keys(KEYS).forEach(function (k) { if (KEYS[k].split(' ').some(function (a) { return a.indexOf(w) === 0 && w.length > 1; })) st = k; });
      txt = txt.replace(m[0], ' ');
    }
    var parts = txt.split(/\s*[·–—|]\s*|\s+-\s+/).map(function (x) { return x.trim(); }).filter(Boolean);
    var co = parts[0] || '', role = parts.slice(1).join(' · ') || '—';
    var r = norm(role), type = 'other';
    if (/data engineer|ingenier\w* de datos|pyspark|spark/.test(r)) type = 'engineer';
    else if (/analyst|analista|\bbi\b|datos|data/.test(r)) type = 'analyst';
    else if (/backend|python|fastapi|django|flask|api/.test(r)) type = 'backend';
    var mode = /remot/.test(r) ? 'r' : /hibrid|hybrid/.test(r) ? 'h' : /presencial|on-?site/.test(r) ? 'p' : '-';
    return co ? { id: nextId++, co: co, role: role, type: type, mode: mode, st: st, ago: 0, news: 0 } : null;
  }

  function download(name, mime, text) {
    try {
      var a = h('a', { href: URL.createObjectURL(new Blob([text], { type: mime })), download: name });
      d.body.appendChild(a); a.click(); a.remove(); say(T.exported);
    } catch (e) { say(T.exported); }
  }
  function rowsOut() { return visible().map(function (i) { return [i.co, i.role, T.ty[i.type], T.mo[i.mode], T.st[stOf(i)], dateOf(i.ago).toISOString().slice(0, 10)]; }); }
  function csv(v) {
    v = String(v);
    if (/^[=+\-@\t\r]/.test(v)) v = "'" + v; // evita que Excel/Calc interprete la celda como formula
    return /[",\n;\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }

  /* ------------------------------------------------ eventos */
  $('qa').addEventListener('submit', function (e) {
    e.preventDefault();
    var it = parse($('qi').value);
    if (!it) { $('qi').focus(); return; }
    items.unshift(it); sel = it.id; $('qi').value = ''; folder = 'all'; q = ''; $('fq').value = ''; showTab('list'); all(); say(fill(T.added, { co: it.co }));
  });
  $('fq').addEventListener('input', function () { q = this.value; renderList(); });
  $('vt').addEventListener('click', function () { view = 'tbl'; renderList(); });
  $('vk').addEventListener('click', function () { view = 'kan'; renderList(); });
  ['g1', 'g2'].forEach(function (k) {
    $(k).addEventListener('change', function () {
      var n = parseInt(this.value, 10); if (!(n > 0)) n = goals[k];
      goals[k] = n; try { localStorage.setItem('jt-goals', JSON.stringify(goals)); } catch (e) { /* sin almacenamiento */ }
      renderSummary(stats());
    });
  });
  $('xc').addEventListener('click', function () {
    var rows = [T.head].concat(rowsOut());
    download('job-tracker.csv', 'text/csv;charset=utf-8', rows.map(function (r) { return r.map(csv).join(','); }).join('\n') + '\n');
  });
  $('xt').addEventListener('click', function () {
    var n = T.ex, lines = rowsOut().map(function (r) { return '- ' + r[0] + ' · ' + r[1] + ' [' + r[4] + '] ' + r[5]; });
    download('job-tracker.txt', 'text/plain;charset=utf-8', n.toUpperCase() + '\n' + lines.join('\n') + '\n');
  });
  $('rs').addEventListener('click', function () { items = JSON.parse(JSON.stringify(seed)); sel = null; folder = 'all'; q = ''; $('fq').value = ''; all(); say(T.restored); });

  /* ------------------------------------------------ pestanas */
  var tabs = Array.prototype.slice.call(d.querySelectorAll('[role=tab]'));
  function showTab(k) {
    if (['list', 'stats', 'about'].indexOf(k) < 0) k = 'list';
    tabs.forEach(function (t) {
      var on = t.getAttribute('data-tab') === k;
      t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1;
      $('pn-' + t.getAttribute('data-tab')).hidden = !on;
    });
    try { history.replaceState(null, '', '#' + k); } catch (e) { /* vista previa aislada */ }
  }
  tabs.forEach(function (t, n) {
    t.addEventListener('click', function () { showTab(t.getAttribute('data-tab')); });
    t.addEventListener('keydown', function (e) {
      var m = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!m) return;
      var nx = tabs[(n + m + tabs.length) % tabs.length]; nx.focus(); showTab(nx.getAttribute('data-tab')); e.preventDefault();
    });
  });
  d.documentElement.classList.add('js');
  window.addEventListener('hashchange', function () { showTab(location.hash.slice(1)); });
  showTab(location.hash.slice(1));
  var first = items.filter(function (i) { return i.news; })[0] || items[0]; if (first) sel = first.id;
  all();
})();
