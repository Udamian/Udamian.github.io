/* Sobre mi: resalta en el folio la seccion que se lee y los terminos que elijas (como las copias en cache de antes). */
(function () {
  var d = document;
  d.documentElement.classList.add('js');
  var cv = d.querySelector('.cv'), stage = d.querySelector('.sin');
  if (!cv) return;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- seccion activa ---- */
  var secs = {};
  Array.prototype.forEach.call(cv.querySelectorAll('section[data-s]'), function (s) { secs[s.getAttribute('data-s')] = s; });
  var items = Array.prototype.slice.call(d.querySelectorAll('.lft [data-s]'));
  var cur = null, first = true;
  function activate(name) {
    if (name === cur) return;
    cur = name;
    Object.keys(secs).forEach(function (k) { secs[k].classList.toggle('on', k === name); });
    items.forEach(function (el) { el.classList.toggle('on', el.getAttribute('data-s') === name && el.classList.contains('tr')); });
    var s = secs[name], wasFirst = first;
    first = false;
    if (!wasFirst && s && stage && stage.scrollHeight > stage.clientHeight + 4 && getComputedStyle(stage).position === 'sticky') {
      var sr = s.getBoundingClientRect(), br = stage.getBoundingClientRect();
      if (sr.top < br.top + 60 || sr.bottom > br.bottom - 20) {
        var top = sr.top - br.top + stage.scrollTop - 90;
        stage.scrollTo({ top: Math.max(0, top), behavior: reduce ? 'auto' : 'smooth' });
      }
    }
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) activate(e.target.getAttribute('data-s')); });
    }, { rootMargin: '-40% 0px -50% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }
  items.forEach(function (el) {
    el.addEventListener('mouseenter', function () { activate(el.getAttribute('data-s')); });
    el.addEventListener('focusin', function () { activate(el.getAttribute('data-s')); });
  });

  /* ---- terminos resaltados ---- */
  var box = d.querySelector('.terms');
  if (!box) return;
  var terms = (box.getAttribute('data-terms') || '').split(',').filter(Boolean);
  function esc(t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function clear() {
    Array.prototype.forEach.call(cv.querySelectorAll('mark'), function (m) { m.replaceWith(d.createTextNode(m.textContent)); });
    cv.normalize();
  }
  function mark(t, i) {
    var re = new RegExp(esc(t), 'gi'), w = d.createTreeWalker(cv, NodeFilter.SHOW_TEXT, null), nodes = [];
    while (w.nextNode()) nodes.push(w.currentNode);
    nodes.forEach(function (n) {
      var s = n.nodeValue, last = 0, m, frag = d.createDocumentFragment(), any = false;
      re.lastIndex = 0;
      while ((m = re.exec(s))) {
        any = true;
        frag.appendChild(d.createTextNode(s.slice(last, m.index)));
        var mk = d.createElement('mark'); mk.className = 'm' + (i % 4); mk.textContent = m[0]; frag.appendChild(mk);
        last = m.index + m[0].length;
        if (!m[0].length) re.lastIndex++;
      }
      if (any) { frag.appendChild(d.createTextNode(s.slice(last))); n.parentNode.replaceChild(frag, n); }
    });
  }
  function draw() {
    clear();
    terms.forEach(mark);
    box.textContent = '';
    var lab = d.createElement('span'); lab.textContent = box.getAttribute('data-label'); box.appendChild(lab);
    terms.forEach(function (t, i) {
      var b = d.createElement('button'); b.type = 'button'; b.className = 'chip m' + (i % 4); b.textContent = t + ' ×';
      b.setAttribute('aria-label', t + ' × (' + box.getAttribute('data-rm') + ')');
      b.addEventListener('click', function () { terms.splice(i, 1); draw(); });
      box.appendChild(b);
    });
    if (terms.length < 4) {
      var inp = d.createElement('input'); inp.type = 'text'; inp.spellcheck = false; inp.maxLength = 24;
      inp.placeholder = box.getAttribute('data-ph'); inp.setAttribute('aria-label', box.getAttribute('data-add'));
      inp.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter') return;
        e.preventDefault();
        var v = inp.value.trim().toLowerCase();
        if (v && terms.indexOf(v) < 0) { terms.push(v); draw(); var n = box.querySelector('input'); if (n) n.focus(); }
      });
      box.appendChild(inp);
    }
  }
  box.hidden = false;
  draw();
})();
