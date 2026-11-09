/* Librero de AURZANE (IA): ayuda a elegir libro, resuelve dudas de la tienda y recoge avisos de fallos.
   Aparece en la tienda (/libros/), en cada ficha y en la biblioteca. Lo carga aurzane-estilo.js. Responde aurzane.com/ai/librero.php. */
(function (w, d) {
  if (w.__azLibrero) return; w.__azLibrero = 1;
  var p = location.pathname;
  if (location.hostname !== 'aurzane.com' || !/^\/(libros|biblioteca)(\/|$)/.test(p)) return;
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var API = 'https://aurzane.com/ai/librero.php';
  var SUG = /^\/libros\/[^/]+\/$/.test(p) && !/regalar/.test(p)
    ? ['¿Es buena idea para regalar?', 'Recomiéndame algo parecido', '¿Cómo lo compro?']
    : ['Algo para la ansiedad', 'Un regalo para mi madre', 'Una novela que enganche', '¿Los libros gratis son legales?'];
  var css = d.createElement('style');
  css.textContent = '.az-lib{margin:26px 0;padding:22px 22px 18px;border-radius:20px;background:linear-gradient(150deg,rgba(91,67,184,.25),rgba(20,26,51,.9));border:1px solid rgba(255,255,255,.12);color:#f3efe6}' +
    '.az-lib h2{font:700 1.3rem/1.25 "Bodoni Moda",Georgia,serif;margin:0 0 4px;color:#f3efe6}.az-lib .s{margin:0 0 12px;font-size:.88rem;opacity:.78}' +
    '.az-lib .ch{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}.az-lib .ch button{border:1px solid rgba(255,255,255,.25);background:transparent;color:inherit;border-radius:99px;padding:7px 12px;font:600 .82rem inherit;cursor:pointer}' +
    '.az-lib form{display:flex;gap:8px;flex-wrap:wrap}.az-lib input,.az-lib textarea{flex:1;min-width:200px;padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.06);color:#fff;font:inherit}' +
    '.az-lib .bt{border:0;border-radius:99px;padding:12px 20px;background:#E2BF6A;color:#1b1440;font:700 .95rem inherit;cursor:pointer}' +
    '.az-lib .r{margin-top:14px;line-height:1.6}.az-lib .ls{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:12px}' +
    '.az-lib .ls a{display:flex;gap:12px;align-items:center;text-decoration:none;color:inherit;background:rgba(255,255,255,.06);border-radius:12px;padding:10px}.az-lib .ls img{width:46px;height:68px;object-fit:cover;border-radius:4px}' +
    '.az-lib .ls b{display:block;font-size:.9rem;line-height:1.3}.az-lib .ls small{opacity:.7}.az-lib .fallo{display:inline-block;margin-top:12px;font-size:.82rem;opacity:.75;background:none;border:0;color:inherit;text-decoration:underline;cursor:pointer;padding:0}' +
    '.az-lib .inc{display:none;margin-top:10px}.az-lib .inc.ab{display:flex}';
  d.head.appendChild(css);
  function colocar() {
    if (d.querySelector('.az-lib')) return;
    var c = d.createElement('section'); c.className = 'az-lib'; c.setAttribute('aria-labelledby', 'azLibT'); c.setAttribute('data-nosnippet', '');
    c.innerHTML = '<h2 id="azLibT">¿No sabes qué leer? Pregúntale al librero de AURZANE</h2>' +
      '<p class="s">Cuéntale qué te pasa, qué te gusta o para quién es, y te recomienda libros de la tienda. También responde dudas sobre cómo comprar o leer gratis.</p>' +
      '<div class="ch">' + SUG.map(function (s) { return '<button type="button">' + E(s) + '</button>'; }).join('') + '</div>' +
      '<form class="pq"><input maxlength="400" placeholder="Ej.: algo para dormir mejor, una novela corta, un regalo para mi pareja" aria-label="Tu pregunta al librero"><button class="bt">Preguntar</button></form>' +
      '<div class="r" aria-live="polite"></div>' +
      '<button type="button" class="fallo">¿Algo no funciona? Avísanos</button>' +
      '<form class="inc"><textarea rows="2" maxlength="600" placeholder="Qué ha fallado: un enlace que no abre, una portada que no carga, un PDF…" aria-label="Describe el problema"></textarea><button class="bt">Enviar aviso</button></form>';
    var sitio = d.querySelector('.comprar') || d.querySelector('.barra') || d.querySelector('main .hero') || d.querySelector('main');
    if (!sitio) return;
    if (sitio.classList && (sitio.classList.contains('comprar') || sitio.classList.contains('hero'))) sitio.parentNode.insertBefore(c, sitio.nextSibling);
    else if (sitio.classList && sitio.classList.contains('barra')) sitio.parentNode.insertBefore(c, sitio);
    else sitio.insertBefore(c, sitio.firstChild);
    var r = c.querySelector('.r'), inp = c.querySelector('.pq input');
    function enviar(datos, fn) {
      fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(datos) })
        .then(function (x) { return x.json(); }).then(fn).catch(function () { fn({ error: 'No se pudo conectar. Inténtalo en un momento.' }); });
    }
    function preguntar(q) {
      q = (q || '').trim(); if (q.length < 3) return;
      r.innerHTML = '<p style="opacity:.7">Buscando en la tienda…</p>';
      enviar({ pregunta: q }, function (j) {
        if (j.error) { r.innerHTML = '<p>' + E(j.error) + '</p>'; return; }
        r.innerHTML = '<p>' + E(j.respuesta) + '</p>' + (j.libros && j.libros.length ? '<div class="ls">' + j.libros.map(function (l) {
          return '<a href="' + E(l.f || l.u) + '">' + (l.img ? '<img src="' + E(l.img) + '" alt="" loading="lazy">' : '') + '<span><b>' + E(l.t) + '</b><small>' + E(l.a) + '</small></span></a>';
        }).join('') + '</div>' : '');
      });
    }
    c.querySelector('.ch').addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) { inp.value = b.textContent; preguntar(b.textContent); } });
    c.querySelector('.pq').addEventListener('submit', function (e) { e.preventDefault(); preguntar(inp.value); });
    var inc = c.querySelector('.inc');
    c.querySelector('.fallo').addEventListener('click', function () { inc.classList.toggle('ab'); inc.querySelector('textarea').focus(); });
    inc.addEventListener('submit', function (e) {
      e.preventDefault(); var t = inc.querySelector('textarea');
      enviar({ tipo: 'incidencia', texto: t.value, pagina: location.href }, function (j) { r.innerHTML = '<p>' + E(j.respuesta || j.error) + '</p>'; if (j.respuesta) { t.value = ''; inc.classList.remove('ab'); } });
    });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', colocar); else colocar();
})(window, document);
