/* Tema único para todo AURZANE (rediseño v4, 22/11/2026)
   - Todas las páginas empiezan en CLARO. Solo se ven en oscuro si la persona lo elige con «Tema».
   - La elección se guarda en una cookie de .aurzane.com (az_tema), así vale en aurzane.com y en todos los mundos.
   - No se sigue el tema del sistema operativo: el sitio se ve igual para todos hasta que alguien lo cambia.
   - Las páginas antiguas leen localStorage('aurzane-tema'); se sincroniza ANTES de que lo lean, y cualquier cambio de
     data-tema que haga su botón se copia a la cookie. */
(function (d, w) {
  var html = d.documentElement, CK = 'az_tema';
  function leer() { var m = d.cookie.match(/(?:^|;\s*)az_tema=(claro|oscuro)/); return m ? m[1] : 'claro'; }
  function guardar(t) {
    try { d.cookie = CK + '=' + t + ';path=/;max-age=31536000;SameSite=Lax' + (/aurzane\.com$/.test(location.hostname) ? ';domain=.aurzane.com' : ''); } catch (e) {}
    try { w.localStorage.setItem('aurzane-tema', t); } catch (e) {}
  }
  var t = leer();
  try { w.localStorage.setItem('aurzane-tema', t); } catch (e) {}
  if (t === 'oscuro') html.setAttribute('data-tema', 'oscuro'); else html.removeAttribute('data-tema');
  html.classList.add('az-v4');
  w.AurzaneTema = { actual: function () { return html.getAttribute('data-tema') === 'oscuro' ? 'oscuro' : 'claro'; },
    poner: function (n) { if (n === 'oscuro') html.setAttribute('data-tema', 'oscuro'); else html.removeAttribute('data-tema'); },
    alternar: function () { this.poner(this.actual() === 'oscuro' ? 'claro' : 'oscuro'); } };
  if (w.MutationObserver) new MutationObserver(function () { var n = w.AurzaneTema.actual(); if (n !== leer()) guardar(n); })
    .observe(html, { attributes: true, attributeFilter: ['data-tema'] });
})(document, window);

/* v4: en las guías de tests y calculadoras se mostraba la imagen de redes (og.jpg, un cartel generado) como si fuera una foto.
   Se sustituye por la foto real de la propia página (Unsplash, la misma de su cabecera); si no hay foto real, el cartel se quita. */
(function (d) {
  function cambiar() {
    var figs = d.querySelectorAll('figure img[src$="/og.jpg"],figure img[src$="/og.png"],figure img[src$="/og.webp"]');
    if (!figs.length) return;
    var ref = d.querySelector('.hero img[src*="images.unsplash.com"],main img[src*="images.unsplash.com"],img[src*="images.unsplash.com"]');
    Array.prototype.forEach.call(figs, function (im) {
      var f = im.closest('figure'); if (!f) return;
      if (!ref) { f.parentNode.removeChild(f); return; }
      im.removeAttribute('srcset'); im.src = ref.src.replace(/([?&])w=\d+/, '$1w=1400'); im.alt = '';
      var c = f.querySelector('figcaption'); if (c) c.parentNode.removeChild(c);
      f.classList.add('az-v4-foto');
    });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', function () { setTimeout(cambiar, 700); }); else setTimeout(cambiar, 700);
})(document);
