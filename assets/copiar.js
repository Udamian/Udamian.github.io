/* Boton «Copiar correo»: copia la direccion al portapapeles (sin cliente de correo hace falta).
   Si el navegador no deja copiar, muestra la direccion para seleccionarla. Sin dependencias. */
(function () {
  'use strict';
  function say(btn, txt) {
    var box = btn.closest('section, .ob, .dym') && btn.closest('section, .ob, .dym').querySelector('.cpst');
    if (box) box.textContent = txt;
  }
  function legacy(text) {
    var t = document.createElement('textarea');
    t.value = text; t.setAttribute('readonly', ''); t.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.appendChild(t); t.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(t);
    return ok;
  }
  document.addEventListener('click', function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest('[data-copy]') : null;
    if (!b) return;
    var text = b.getAttribute('data-copy');
    function done(ok) {
      say(b, ok ? b.getAttribute('data-ok') + ': ' + text : b.getAttribute('data-fail') + ' ' + text);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(legacy(text)); });
    } else done(legacy(text));
  });
})();
