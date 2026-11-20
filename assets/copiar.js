/* Correo: boton «Copiar correo» y aviso cuando el enlace mailto: no abre ningun programa.
   Muchos equipos no tienen cliente de correo configurado (y algunos marcos bloquean mailto:),
   asi que, si tras pulsar no pasa nada, se muestra la direccion, se copia y se ofrece Gmail.
   Sin dependencias; no envia nada a ningun sitio salvo que se pulse el enlace a Gmail. */
(function () {
  'use strict';
  var lang = (document.documentElement.lang || 'es').slice(0, 2);
  var T = lang === 'en'
    ? { copied: 'Email copied', miss: "Didn't your email app open? My address (copied): ", gmail: 'Open in Gmail', close: 'Close' }
    : { copied: 'Correo copiado', miss: '¿No se abrió tu programa de correo? Mi dirección (copiada): ', gmail: 'Abrir en Gmail', close: 'Cerrar' };

  function legacy(text) {
    var t = document.createElement('textarea');
    t.value = text; t.setAttribute('readonly', ''); t.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.appendChild(t); t.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(t);
    return ok;
  }
  function copy(text, cb) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { cb(true); }, function () { cb(legacy(text)); });
    } else cb(legacy(text));
  }
  function say(btn, txt) {
    var host = btn.closest('section, .ob, .dym');
    var box = host && host.querySelector('.cpst');
    if (box) box.textContent = txt;
  }

  /* aviso flotante (solo se crea si hace falta) */
  var toast = null, timer = 0;
  function showToast(addr) {
    if (!toast) {
      toast = document.createElement('div');
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      toast.className = 'mailtoast';
      document.body.appendChild(toast);
    }
    toast.textContent = '';
    var p = document.createElement('span');
    p.textContent = T.miss;
    var b = document.createElement('b');
    b.textContent = addr;
    var g = document.createElement('a');
    g.href = 'https://mail.google.com/mail/?view=cm&to=' + encodeURIComponent(addr);
    g.target = '_blank'; g.rel = 'noopener'; g.textContent = T.gmail;
    var x = document.createElement('button');
    x.type = 'button'; x.textContent = T.close;
    x.addEventListener('click', function () { toast.hidden = true; });
    toast.appendChild(p); toast.appendChild(b); toast.appendChild(document.createTextNode(' '));
    toast.appendChild(g); toast.appendChild(x);
    toast.hidden = false;
    clearTimeout(timer);
    timer = setTimeout(function () { if (toast) toast.hidden = true; }, 15000);
  }

  document.addEventListener('click', function (ev) {
    var el = ev.target && ev.target.closest ? ev.target.closest('[data-copy], a[href^="mailto:"]') : null;
    if (!el) return;

    if (el.hasAttribute('data-copy')) {                    /* boton «Copiar correo» */
      var text = el.getAttribute('data-copy');
      copy(text, function (ok) {
        say(el, ok ? el.getAttribute('data-ok') + ': ' + text : el.getAttribute('data-fail') + ' ' + text);
      });
      return;
    }

    /* enlace mailto: si el navegador abre un programa, la pagina pierde el foco o se oculta */
    var addr = decodeURIComponent((el.getAttribute('href') || '').slice(7).split('?')[0]);
    var left = false;
    function gone() { left = true; }
    window.addEventListener('blur', gone, { once: true });
    document.addEventListener('visibilitychange', gone, { once: true });
    setTimeout(function () {
      window.removeEventListener('blur', gone);
      document.removeEventListener('visibilitychange', gone);
      if (left) return;
      copy(addr, function () { showToast(addr); });
    }, 1500);
  });
})();
