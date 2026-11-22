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
