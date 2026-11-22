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
/* Cifras aproximadas (22/11/2026, pedido de Adrián): los conteos del catálogo se muestran redondeados hacia abajo,
   1.580 artículos → «1.000+ artículos», 748 libros → «700+ libros». Menos de 100 se deja exacto. Solo toca números seguidos
   de lo que se cuenta (artículos, libros, papers, universidades…); nunca puntuaciones, precios, fechas, notas ni porcentajes.
   Las cifras salen de los datos reales y se rellenan solas: esto solo cambia cómo se muestran, también las que llegan después. */
(function (d) {
  var COSAS = '(?:art[íi]culos|libros|papers|estudios|universidades|instituciones|institutos|centros|carreras|grados|titulaciones|frases|autores|fichas|t[íi]tulos|gu[íi]as|lecciones|preguntas|p[áa]ginas|recursos|referencias|fuentes|articles|books|universities|studies)';
  var EN_TEXTO = new RegExp('(^|[^\\d.,+\\-])(\\d{1,3}(?:\\.\\d{3})+|\\d{3,})(?![\\d.,%+€$])(\\s+(?:[a-záéíóúñ]+\\s+){0,2}' + COSAS + '\\b)', 'gi');
  var SOLO = /^\s*(\d{1,3}(?:\.\d{3})+|\d{3,})\s*$/, LUEGO = new RegExp('^\\s*(?:[a-záéíóúñ]+\\s+){0,2}' + COSAS + '\\b', 'i');
  var NO = 'script,style,textarea,input,select,code,pre,[contenteditable],.no-aprox,.az-no-aprox';
  function aprox(t) {
    var n = parseInt(String(t).replace(/\./g, ''), 10); if (!(n >= 100) || n >= 1e9) return null;
    var p = n < 1000 ? 100 : 1000, r = Math.floor(n / p) * p;
    return String(r).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '+';
  }
  function siguiente(nodo) {   // texto que viene justo después (etiqueta de la cifra), subiendo dos niveles como mucho
    for (var x = nodo, k = 0; x && k < 3; x = x.parentNode, k++) {
      for (var s = x.nextSibling; s; s = s.nextSibling) { var t = s.textContent; if (t && t.trim()) return t; }
    }
    return '';
  }
  function pasar(raiz) {
    if (!raiz || !d.body) return;
    var w = d.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, null), nodos = [], n;
    while ((n = w.nextNode())) nodos.push(n);
    nodos.forEach(function (t) {
      var p = t.parentElement; if (!p || p.closest(NO)) return;
      var v = t.nodeValue; if (!v || !/\d{3}/.test(v.replace(/\./g, ''))) return;
      var m = v.match(SOLO);
      if (m) { if (LUEGO.test(siguiente(t))) { var a = aprox(m[1]); if (a) t.nodeValue = v.replace(m[1], a); } return; }
      var nv = v.replace(EN_TEXTO, function (todo, pre, num, resto) { var a = aprox(num); return a ? pre + a + resto : todo; });
      if (nv !== v) t.nodeValue = nv;
    });
  }
  var cola = null;
  function luego() { if (cola) return; cola = setTimeout(function () { cola = null; pasar(d.body); }, 250); }
  function iniciar() { pasar(d.body); try { new MutationObserver(luego).observe(d.body, { childList: true, subtree: true, characterData: true }); } catch (e) {} }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document);
/* Cabeceras oscuras sin foto (universidades, OVP, páginas sueltas): llevan la foto real de la página (su og:image, que ya son
   fotos reales) bajo el velo verde, como en la guía visual. Si la página no tiene foto propia, se queda como está. */
(function (d) {
  function fotoCab() {
    if (d.documentElement.classList.contains('az-v4-herofoto')) return;
    var og = d.querySelector('meta[property="og:image"]'), u = og && og.content;
    if (!u || /og-portada|logo|portadas?\//i.test(u)) return;
    var cab = d.querySelector('main > .hero, section.hero, header.hero, .u-hero, .hero-wrap, .world-header, main > header:first-child'); if (!cab) return;
    var cs = getComputedStyle(cab); if (/url\(/.test(cs.backgroundImage)) return;
    var cols = ((cs.backgroundColor + ' ' + cs.backgroundImage).match(/rgba?\([^)]+\)/g) || []).map(function (x) { return x.replace(/rgba?\(|\)/g, '').split(/[ ,\/]+/).map(Number); })
      .filter(function (c) { return c.length < 4 || c[3] >= .5; });
    var c = cols[0]; if (!c) return;
    if (.2126 * c[0] + .7152 * c[1] + .0722 * c[2] > 90) return;   // solo cabeceras oscuras: el texto claro sigue legible
    cab.style.setProperty('--v4-foto', 'url("' + u.replace(/"/g, '%22') + '")'); cab.setAttribute('data-v4-foto', '1');
    d.documentElement.classList.add('az-v4-cabfoto');
  }
  if (d.readyState === 'complete') setTimeout(fotoCab, 300); else window.addEventListener('load', function () { setTimeout(fotoCab, 300); });
})(document);
