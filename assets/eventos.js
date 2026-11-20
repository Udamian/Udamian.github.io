/* Eventos de analitica (solo se carga si hay analitica activa). Sin cookies ni datos personales:
   cuenta clics en contacto/CV/repositorios y el uso del buscador, nunca lo que se escribe. */
(function () {
  'use strict';
  function count(path, title) {
    try {
      var g = window.goatcounter;
      if (g && typeof g.count === 'function') g.count({ path: 'evt/' + path, title: title || path, event: true });
    } catch (e) { /* la analitica nunca debe romper la pagina */ }
  }
  function slugOf(a) {
    var m = /^\/?(?:[^/]+\/)([^/?#]+)/.exec(a.pathname.replace(/^\/+/, '')); // /usuario/repo
    return m ? m[1].toLowerCase() : 'otro';
  }
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href],button') : null;
    if (!a) return;
    if (a.id === 'lucky') return count('buscador/me-siento-con-suerte');
    if (a.getAttribute('role') === 'tab' && a.getAttribute('data-tab')) return count('buscador/pestana-' + a.getAttribute('data-tab'));
    if (a.hasAttribute('data-copy')) return count('contacto/correo-copiado');
    var h = a.getAttribute('href') || '';
    if (/\.pdf($|[?#])/i.test(h)) return count('contacto/cv-pdf');
    if (/^mailto:/i.test(h)) return count('contacto/correo');
    if (/linkedin\.com/i.test(h)) return count('contacto/linkedin');
    if (a.hasAttribute('hreflang') && a.closest('nav,header,footer,.pt,.ptop')) return count('idioma/' + a.getAttribute('hreflang'));
    if (/^https?:/i.test(h) && /(^|\.)github\.com$/i.test(a.hostname)) {
      var s = a.pathname.split('/').filter(Boolean);
      return count(s.length > 1 ? 'repo/' + s[1].toLowerCase() : 'contacto/github');
    }
  }, true);
  document.addEventListener('submit', function (ev) {
    if (ev.target && ev.target.id === 'f') count('buscador/busqueda');
  }, true);
})();
