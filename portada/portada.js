/* ---------- Tema claro u oscuro (misma clave que el resto del ecosistema) ---------- */
(function () { try { if (localStorage.getItem('aurzane-tema') === 'oscuro') document.documentElement.setAttribute('data-tema', 'oscuro'); } catch (e) {} })();
function alternarTema() {
  var h = document.documentElement, osc = h.getAttribute('data-tema') === 'oscuro';
  if (osc) h.removeAttribute('data-tema'); else h.setAttribute('data-tema', 'oscuro');
  try { localStorage.setItem('aurzane-tema', osc ? 'claro' : 'oscuro'); } catch (e) {}
}
(function () {
  'use strict';
  var d = document, $ = function (i) { return d.getElementById(i); };
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* Buscador de la cabecera: abre el buscador común con lo escrito */
  $('pBusca').addEventListener('submit', function (e) {
    e.preventDefault();
    var q = $('pQ').value.trim();
    if (window.AurzaneBuscar) window.AurzaneBuscar($('pQ'), q);
    else location.href = '/research.html' + (q ? '?q=' + encodeURIComponent(q) : '');
  });

  /* Cifras reales: tests del índice del ecosistema, artículos del texto que actualiza la tarea diaria de cifras */
  function cifras() {
    var I = window.AurzaneIndice;
    if (I) { var n = I.filter(function (x) { return x[3] === 'Test' && x[5] === 'es' && x[2] !== 'ovp'; }).length; if (n) $('cTests').textContent = n; }
    var m = ((($('rhTxt') || {}).textContent || '').match(/(\d{1,3}(?:\.\d{3})+)\s+artículos/) || [])[1]; if (m) $('cArt').textContent = m;
  }
  if (d.readyState === 'complete') cifras(); else window.addEventListener('load', cifras);
  d.addEventListener('aurzane-indice', cifras);

  /* Biblioteca: cifras, estantería y colecciones reales (biblioteca/resumen.js) */
  d.addEventListener('DOMContentLoaded', function () {
    var R = window.BIBLIOTECA_RESUMEN; if (!R) return;
    $('cLibros').textContent = Number(R.libros).toLocaleString('es-ES');
    if ($('bhCifras')) $('bhCifras').textContent = 'Biblioteca: ' + Number(R.libros).toLocaleString('es-ES') + ' libros para leer gratis';
    if ($('bhCats')) $('bhCats').innerHTML = (R.colecciones || R.categorias || []).map(function (c) { return '<a href="/biblioteca/#' + (R.colecciones ? 'c=' : 'm=') + E(c.id) + '">' + E(c.nombre) + '</a>'; }).join('');
    if ($('bhEstante')) $('bhEstante').innerHTML = (R.destacados || []).slice(0, 6).map(function (x) { return '<a href="/biblioteca/libro/' + encodeURIComponent(x.id) + '.html" tabindex="-1"><img src="/biblioteca/' + E(x.portada) + '" alt="" loading="lazy" width="200" height="300"></a>'; }).join('');
  });

  /* Hoy en AURZANE: frase, curiosidad, ejercicio, test del día, libro de la semana y música (hoy/hoy.json) */
  fetch('/hoy/hoy.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (h) {
    if (!h || !h.frase) return;
    try { $('hoyDia').textContent = new Date(h.fecha + 'T12:00:00').toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' }); } catch (e) {}
    $('hoyFrase').textContent = h.frase.texto;
    var a = h.frase.autor ? E(h.frase.autor) : '';
    if (h.frase.obra) a += (a ? ', ' : '') + (h.frase.url ? '<a href="' + E(h.frase.url) + '">' + E(h.frase.obra) + '</a>' : '<i>' + E(h.frase.obra) + '</i>');
    if (h.mas_frases) a += (a ? ' · ' : '') + '<a href="/frases/">Más frases</a>';
    $('hoyAutor').innerHTML = a;
    var li = [];
    if (h.curiosidad) li.push(['Curiosidad del día', h.curiosidad.titulo, h.curiosidad.texto.split('. ')[0] + '.', h.curiosidad.url]);
    if (h.ejercicio) li.push(['Ejercicio de hoy', h.ejercicio.titulo, 'Unos minutos guiados para bajar el ritmo.', h.ejercicio.url]);
    if (h.test) li.push(['Test del día', h.test.titulo, 'Gratis, orientativo y con resultado al momento.', h.test.url]);
    $('hoyLista').innerHTML = li.map(function (x) { return '<li><a href="' + E(x[3] || '#') + '"><span class="hoy-k">' + E(x[0]) + '</span><span class="hoy-t">' + E(x[1]) + '</span><span class="hoy-d">' + E(x[2]) + '</span></a></li>'; }).join('');
    var sl = d.createElement('script'); sl.src = '/libros/libros.js?d=' + (h.fecha || ''); sl.async = true;
    sl.onload = function () {
      var L = (window.__azLibros || []).filter(function (x) { return x.img; }); if (!L.length) return;
      var sem = Math.floor(Date.now() / 6048e5), x = L.filter(function (y) { return y.tend; })[0] || L[sem % L.length];
      var el = d.createElement('li'); el.innerHTML = '<a href="' + E(x.f || '/libros/') + '"><span class="hoy-k">Libro de la semana</span><span class="hoy-t">' + E(x.t) + '</span><span class="hoy-d">De ' + E(x.a) + '. Mira de qué trata y más libros recomendados.</span></a>';
      $('hoyLista').appendChild(el);
    };
    d.head.appendChild(sl);
    if (h.musica && h.musica.url) {
      var b = $('hoyPlay'), au = $('hoyAudio');
      $('hoyCred').textContent = 'Música: ' + h.musica.credito; $('hoyMusica').hidden = false; au.volume = .45;
      b.addEventListener('click', function () {
        if (!au.src) au.src = h.musica.url;
        if (au.paused) au.play().then(function () { b.setAttribute('aria-pressed', 'true'); b.textContent = 'Pausar la música'; }).catch(function () {});
        else { au.pause(); b.setAttribute('aria-pressed', 'false'); b.textContent = 'Escuchar música tranquila'; }
      });
    }
    $('hoy').hidden = false;
  }).catch(function () {});

  /* Lo último: el feed de novedades que publica la IA de AURZANE */
  fetch('/novedades/feed.xml', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.text() : ''; }).then(function (x) {
    if (!x) return;
    var doc = new DOMParser().parseFromString(x, 'application/xml'), it = Array.prototype.slice.call(doc.querySelectorAll('item'), 0, 8);
    if (!it.length || !$('nLista')) return;
    $('nLista').innerHTML = it.map(function (i) {
      var t = (i.querySelector('title') || {}).textContent || '', l = (i.querySelector('link') || {}).textContent || '/novedades/', f = new Date((i.querySelector('pubDate') || {}).textContent || '');
      var tipo = (t.match(/^([^:]{3,20}):\s*/) || [])[1] || 'Novedad';
      return '<li><a href="' + E(l) + '"><small>' + E(tipo) + (isNaN(f) ? '' : ' · ' + f.toLocaleDateString('es-ES', { day: 'numeric', month: 'long' })) + '</small><b>' + E(t.replace(/^[^:]{3,20}:\s*/, '')) + '</b></a></li>';
    }).join('');
  }).catch(function () {});
})();
