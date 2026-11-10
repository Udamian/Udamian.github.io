/* Guugle: filtro en vivo, pestanas, "estoy de suerte" y busquedas relacionadas. */
(function () {
  var d = document;
  d.documentElement.classList.add('js');
  var q = d.getElementById('q'), main = d.querySelector('main'), cnt = d.getElementById('cnt'), none = d.getElementById('none');
  var cfg = {};
  try { cfg = JSON.parse(d.getElementById('cfg').textContent); } catch (e) { return; }
  var items = Array.prototype.slice.call(d.querySelectorAll('[data-hay]'));
  var arts = Array.prototype.slice.call(d.querySelectorAll('article.res'));
  var stop = {}; cfg.stop.forEach(function (w) { stop[w] = 1; });

  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function terms(v) { return norm(v).split(/[^a-z0-9+#.]+/).filter(function (t) { return t && !stop[t]; }); }

  function run() {
    var t = terms(q.value), n = 0;
    items.forEach(function (el) {
      var ok = t.every(function (x) { return el.getAttribute('data-hay').indexOf(x) > -1; });
      el.hidden = !ok;
      if (ok && el.tagName === 'ARTICLE') n++;
    });
    cnt.textContent = n === 1 ? cfg.one : cfg.many.replace('{n}', n);
    none.hidden = n > 0;
  }

  function setTab(name) {
    if (['todo', 'imagenes', 'codigo'].indexOf(name) < 0) name = 'todo';
    main.setAttribute('data-tab', name);
    d.querySelectorAll('[role=tab]').forEach(function (a) {
      a.setAttribute('aria-selected', a.getAttribute('data-tab') === name ? 'true' : 'false');
    });
  }

  d.querySelectorAll('[role=tab]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var name = a.getAttribute('data-tab');
      setTab(name);
      try { history.replaceState(null, '', '#' + name); } catch (_) { /* vista previa aislada */ }
    });
  });

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
