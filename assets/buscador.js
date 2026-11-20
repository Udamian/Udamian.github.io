/* Cambeiro: filtro en vivo, pestanas, "voy a tener suerte", negrita en los terminos buscados y barra de resultados. */
(function () {
  var d = document;
  d.documentElement.classList.add('js');
  var q = d.getElementById('q'), main = d.querySelector('main'), cnt = d.getElementById('cnt'), none = d.getElementById('none');
  var nonetxt = d.getElementById('nonetxt'), tabname = d.getElementById('tabname');
  var cfg = {};
  try { cfg = JSON.parse(d.getElementById('cfg').textContent); } catch (e) { return; }
  var items = Array.prototype.slice.call(d.querySelectorAll('[data-hay]'));
  var arts = Array.prototype.slice.call(d.querySelectorAll('article.res'));
  var bolds = Array.prototype.slice.call(d.querySelectorAll('[data-b]'));
  bolds.forEach(function (el) { el.setAttribute('data-orig', el.innerHTML); });
  var stop = {}; cfg.stop.forEach(function (w) { stop[w] = 1; });

  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function terms(v) { return norm(v).split(/[^a-z0-9+#.]+/).filter(function (t) { return t && !stop[t]; }); }

  var ACC = { a: 'aàáâãä', e: 'eèéêë', i: 'iìíîï', o: 'oòóôõö', u: 'uùúûü', n: 'nñ', c: 'cç' };
  function accRe(t) {
    return new RegExp(t.split('').map(function (ch) {
      var e = ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      return ACC[ch] ? '[' + ACC[ch] + ']' : e;
    }).join(''), 'gi');
  }
  function bold(el, ts) {
    el.innerHTML = el.getAttribute('data-orig');
    ts.forEach(function (t) {
      var re = accRe(t), w = d.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), nodes = [];
      while (w.nextNode()) nodes.push(w.currentNode);
      nodes.forEach(function (n) {
        if (n.parentNode.tagName === 'B') return;
        var s = n.nodeValue, last = 0, m, frag = d.createDocumentFragment(), any = false;
        re.lastIndex = 0;
        while ((m = re.exec(s))) {
          if (!m[0].length) { re.lastIndex++; continue; }
          any = true;
          frag.appendChild(d.createTextNode(s.slice(last, m.index)));
          var b = d.createElement('b'); b.textContent = m[0]; frag.appendChild(b);
          last = m.index + m[0].length;
        }
        if (any) { frag.appendChild(d.createTextNode(s.slice(last))); n.parentNode.replaceChild(frag, n); }
      });
    });
  }

  function bar(n, qs) {
    cnt.textContent = (n === 1 ? cfg.one : cfg.many.replace(/\{n\}/g, n)) + ' ';
    var b = d.createElement('b'); b.textContent = qs; cnt.appendChild(b);
    cnt.appendChild(d.createTextNode('. ' + cfg.tail));
  }

  function run() {
    var t = terms(q.value), n = 0, qs = q.value.trim();
    items.forEach(function (el) {
      var ok = t.every(function (x) { return el.getAttribute('data-hay').indexOf(x) > -1; });
      el.hidden = !ok;
      if (ok && el.tagName === 'ARTICLE') n++;
    });
    bolds.forEach(function (el) { bold(el, t); });
    bar(n, qs);
    var ob = d.getElementById('ob'); if (ob) ob.hidden = qs !== cfg.def;
    none.hidden = n > 0;
    if (n === 0) {
      var parts = cfg.none.split('{q}');
      nonetxt.textContent = parts[0];
      var b = d.createElement('b'); b.textContent = qs; nonetxt.appendChild(b);
      nonetxt.appendChild(d.createTextNode(parts[1] || ''));
    }
  }

  function setTab(name) {
    if (['todo', 'imagenes', 'codigo'].indexOf(name) < 0) name = 'todo';
    main.setAttribute('data-tab', name);
    d.querySelectorAll('[role=tab]').forEach(function (a) {
      var on = a.getAttribute('data-tab') === name;
      a.setAttribute('aria-selected', on ? 'true' : 'false');
      a.tabIndex = on ? 0 : -1; // patron de pestanas: solo la activa entra por tabulador
      if (on && tabname) tabname.textContent = a.textContent;
    });
  }

  var tabs = Array.prototype.slice.call(d.querySelectorAll('[role=tab]'));
  tabs.forEach(function (a, n) {
    a.addEventListener('keydown', function (e) {
      var to = e.key === 'ArrowRight' ? n + 1 : e.key === 'ArrowLeft' ? n - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : -1;
      if (to < 0) return;
      e.preventDefault();
      var t = tabs[(to + tabs.length) % tabs.length];
      t.focus(); t.click();
    });
  });
  d.querySelectorAll('[role=tab]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var name = a.getAttribute('data-tab');
      setTab(name);
      try { history.replaceState(null, '', '#' + name); } catch (_) { /* vista previa aislada */ }
    });
  });

  try { var iq = new URLSearchParams(location.search).get('q'); if (iq) q.value = iq; } catch (_) { /* sin parametros */ }
  d.getElementById('f').addEventListener('submit', function (e) { e.preventDefault(); run(); q.blur(); });
  q.addEventListener('input', run);
  q.addEventListener('focus', function () { q.select(); });

  d.querySelectorAll('[data-q]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      q.value = a.getAttribute('data-q');
      setTab('todo');
      run();
      window.scrollTo(0, 0);
    });
  });

  var lucky = d.getElementById('lucky');
  if (lucky) lucky.addEventListener('click', function () {
    var vis = arts.filter(function (a) { return !a.hidden; });
    if (!vis.length) vis = arts;
    var pick = vis[Math.floor(Math.random() * vis.length)];
    var a = pick && pick.querySelector('h2 a');
    if (a) window.location.href = a.getAttribute('href');
  });

  window.addEventListener('hashchange', function () { setTab(location.hash.slice(1)); });
  setTab(location.hash.slice(1));
  run();
})();
