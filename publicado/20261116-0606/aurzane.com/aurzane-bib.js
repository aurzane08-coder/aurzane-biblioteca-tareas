/* Biblioteca AURZANE: capa común que hace de la biblioteca una plataforma propia.
   La carga aurzane-ds.js en /biblioteca y /libros. No cambia el catálogo ni los libros:
   - Sugerencias al escribir en el buscador (títulos, autores y temas), con teclado.
   - «Leer aquí» y «Ficha» bien diferenciados en tarjetas y en la página de cada libro.
   - «Seguir leyendo»: recuerda en este navegador la página por la que vas de cada libro y te lleva a ella.
   - Estantería con tus libros guardados (los mismos «Guardados» de todo AURZANE).
   - Lector más cómodo en el móvil. */
(function (w, d) {
  'use strict';
  if (w.__azBib) return; w.__azBib = 1;
  var BASE = 'https://aurzane.com/biblioteca/', K_LEIDOS = 'az-bib-leidos';
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var N = function (s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); };
  function lee(k, def) { try { var v = JSON.parse(localStorage.getItem(k) || 'null'); return v == null ? def : v; } catch (e) { return def; } }
  function guarda(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  /* ---------- estilos ---------- */
  var css = d.createElement('style'); css.setAttribute('data-azbib', '1');
  css.textContent = [
    '.chip.ficha{display:inline-block!important;border-color:rgba(160,170,200,.45)!important;color:#C9D0E4!important}',
    '.chip.leer{background:rgba(127,169,104,.16)!important;border-color:rgba(127,169,104,.6)!important;color:#BFE0AE!important;font-weight:600}',
    '.libro .l-meta{min-height:20px}',
    '.az-sug{position:absolute;left:0;right:0;top:calc(100% + 6px);z-index:60;background:#121a3a;border:1px solid rgba(201,162,75,.35);border-radius:14px;box-shadow:0 18px 40px rgba(0,0,0,.45);padding:6px;max-height:min(70vh,520px);overflow:auto}',
    '.az-sug[hidden]{display:none}',
    '.az-sug a{display:flex;gap:12px;align-items:center;padding:8px 10px;border-radius:10px;color:#EEF0F7;text-decoration:none}',
    '.az-sug a[aria-selected="true"],.az-sug a:hover{background:rgba(201,162,75,.14)}',
    '.az-sug img,.az-sug .ph{width:34px;height:48px;object-fit:cover;border-radius:4px;flex-shrink:0;background:#1d2752}',
    '.az-sug .t{display:block;font-size:.92rem;line-height:1.25}',
    '.az-sug .a{display:block;font-size:.78rem;color:#A9B0C8;margin-top:2px}',
    '.az-sug .k{margin-left:auto;font-size:.7rem;font-weight:600;padding:2px 8px;border-radius:99px;white-space:nowrap}',
    '.az-sug .k.leer{color:#BFE0AE;border:1px solid rgba(127,169,104,.6)}.az-sug .k.ficha{color:#C9D0E4;border:1px solid rgba(160,170,200,.45)}.az-sug .k.tema{color:#EACF92;border:1px solid rgba(201,162,75,.5)}',
    '.az-sug .todo{justify-content:center;font-weight:600;color:#EACF92}',
    '.az-bib-tipo{display:inline-flex;align-items:center;gap:8px;font-size:.84rem;font-weight:600;padding:6px 12px;border-radius:99px;margin:0 0 14px}',
    '.az-bib-tipo.leer{color:#BFE0AE;background:rgba(127,169,104,.14);border:1px solid rgba(127,169,104,.5)}',
    '.az-bib-tipo.ficha{color:#C9D0E4;background:rgba(160,170,200,.1);border:1px solid rgba(160,170,200,.4)}',
    '.az-seguir{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin:16px 0 0;padding:12px 16px;border:1px solid rgba(201,162,75,.4);border-radius:14px;background:rgba(201,162,75,.08)}',
    '.az-seguir span{color:#EEF0F7;font-size:.92rem}',
    '.az-estante{margin:8px 0 46px}',
    '.az-estante h2{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.6rem;margin:0 0 4px}',
    '.az-estante>p{color:#A9B0C8;font-size:.9rem;margin:0 0 16px}',
    '.az-fila{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(150px,170px);gap:16px;overflow-x:auto;padding-bottom:8px;scrollbar-width:thin}',
    '.az-fila a{color:#EEF0F7;text-decoration:none;display:flex;flex-direction:column;gap:6px}',
    '.az-fila img,.az-fila .ph{width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:6px;background:#1d2752}',
    '.az-fila b{font-family:"Bodoni Moda",serif;font-weight:500;font-size:.98rem;line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}',
    '.az-fila small{color:#A9B0C8;font-size:.76rem}',
    '.az-barra-p{height:4px;border-radius:4px;background:#26305e;overflow:hidden}.az-barra-p i{display:block;height:100%;background:#C9A24B}',
    '@media(max-width:700px){.lector .barra{padding:8px 0}.lector .barra .grupo{gap:6px}.lector .barra button{min-width:44px;min-height:40px}.paginas .pagina{max-width:100%}.az-fila{grid-auto-columns:minmax(128px,140px)}}'
  ].join('\n');
  d.head.appendChild(css);

  /* ---------- catálogo (se carga solo si hace falta) ---------- */
  var esperando = null;
  function catalogo() {
    if (w.BIBLIOTECA && w.BIBLIOTECA.libros) return Promise.resolve(w.BIBLIOTECA);
    if (esperando) return esperando;
    esperando = new Promise(function (ok) {
      var s = d.createElement('script'); s.src = BASE + 'catalogo.js?d=' + new Date().toISOString().slice(0, 10);
      s.onload = function () { ok(w.BIBLIOTECA || null); }; s.onerror = function () { ok(null); }; d.head.appendChild(s);
    });
    return esperando;
  }
  function fichaUrl(l) { return BASE + 'libro/' + encodeURIComponent(l.id) + '.html'; }
  function portadaUrl(l) { return l && l.portada ? (/^https?:/.test(l.portada) ? l.portada : BASE + l.portada) : ''; }

  /* ---------- 1. sugerencias en el buscador ---------- */
  function sugerencias(inp) {
    if (!inp || inp.__azSug) return; inp.__azSug = 1;
    var caja = inp.closest('form') || inp.parentNode;
    if (getComputedStyle(caja).position === 'static') caja.style.position = 'relative';
    var lista = d.createElement('div'); lista.className = 'az-sug'; lista.id = 'azSug' + Math.random().toString(36).slice(2, 7); lista.setAttribute('role', 'listbox'); lista.hidden = true;
    caja.appendChild(lista);
    inp.setAttribute('role', 'combobox'); inp.setAttribute('aria-autocomplete', 'list'); inp.setAttribute('aria-expanded', 'false'); inp.setAttribute('aria-controls', lista.id);
    var sel = -1, idx = null, temas = [];
    function preparar(B) {
      if (idx || !B) return;
      idx = B.libros.map(function (l) { return { l: l, t: N(l.titulo), a: N(l.autores) }; });
      var macro = {}; (B.macrotemas || []).forEach(function (m) { (m.temas || []).forEach(function (n) { macro[n] = m.id; }); });
      temas = (B.temas || []).map(function (t) { return { n: t.n, nombre: t.nombre, k: N(t.nombre), m: macro[t.n] }; });
    }
    function cerrar() { lista.hidden = true; inp.setAttribute('aria-expanded', 'false'); sel = -1; }
    function buscar() {
      var q = N(inp.value.trim());
      if (q.length < 2 || !idx) return cerrar();
      var pal = q.split(/\s+/);
      var res = idx.map(function (x) {
        var p = 0;
        if (x.t.indexOf(q) === 0) p += 6; else if (x.t.indexOf(q) > -1) p += 4;
        if (x.a.indexOf(q) > -1) p += 3;
        if (!p && pal.every(function (w_) { return x.t.indexOf(w_) > -1 || x.a.indexOf(w_) > -1; })) p += 2;
        if (p && x.l.tipo === 'pdf') p += .5;
        return { x: x, p: p };
      }).filter(function (r) { return r.p; }).sort(function (a, b) { return b.p - a.p; }).slice(0, 7);
      var ts = temas.filter(function (t) { return t.k.indexOf(q) > -1; }).slice(0, 2);
      if (!res.length && !ts.length) { lista.innerHTML = '<a href="#" class="todo" data-todo="1">No hay coincidencias exactas: buscar «' + E(inp.value.trim()) + '» en todo el catálogo</a>'; }
      else lista.innerHTML = ts.map(function (t) { return '<a role="option" href="' + BASE + '#m=' + E(t.m || '') + '&t=' + t.n + '"><span class="ph" aria-hidden="true"></span><span><span class="t">' + E(t.nombre) + '</span><span class="a">Tema de la biblioteca</span></span><span class="k tema">Tema</span></a>'; }).join('') +
        res.map(function (r) { var l = r.x.l, img = portadaUrl(l);
          return '<a role="option" href="' + fichaUrl(l) + '">' + (img ? '<img src="' + E(img) + '" alt="" loading="lazy" onerror="this.outerHTML=\'<span class=ph></span>\'">' : '<span class="ph" aria-hidden="true"></span>') +
            '<span><span class="t">' + E(l.titulo) + '</span><span class="a">' + E(String(l.autores || '').split(';')[0]) + '</span></span><span class="k ' + (l.tipo === 'pdf' ? 'leer">Leer aquí' : 'ficha">Ficha') + '</span></a>'; }).join('') +
        '<a href="#" class="todo" data-todo="1">Ver todos los resultados de «' + E(inp.value.trim()) + '»</a>';
      lista.hidden = false; inp.setAttribute('aria-expanded', 'true'); sel = -1;
    }
    function opciones() { return lista.querySelectorAll('a'); }
    function marcar(i) { var o = opciones(); if (!o.length) return; sel = (i + o.length) % o.length; o.forEach(function (a, j) { a.setAttribute('aria-selected', j === sel ? 'true' : 'false'); }); o[sel].scrollIntoView({ block: 'nearest' }); }
    function todo() { cerrar(); var f = inp.closest('form'); if (f && f.requestSubmit) f.requestSubmit(); else if (f) f.submit(); else location.href = BASE + '#q=' + encodeURIComponent(inp.value.trim()); }
    var t0;
    inp.addEventListener('focus', function () { catalogo().then(preparar); });
    inp.addEventListener('input', function () { clearTimeout(t0); t0 = setTimeout(function () { catalogo().then(function (B) { preparar(B); buscar(); }); }, 120); });
    inp.addEventListener('keydown', function (e) {
      if (lista.hidden) return;
      if (e.key === 'ArrowDown') { e.preventDefault(); marcar(sel + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); marcar(sel - 1); }
      else if (e.key === 'Escape') cerrar();
      else if (e.key === 'Enter' && sel > -1) { e.preventDefault(); var a = opciones()[sel]; if (a.dataset.todo) todo(); else location.href = a.href; }
    });
    lista.addEventListener('click', function (e) { var a = e.target.closest('a'); if (a && a.dataset.todo) { e.preventDefault(); todo(); } });
    d.addEventListener('click', function (e) { if (!caja.contains(e.target)) cerrar(); });
  }

  /* ---------- 2. página de un libro: tipo bien visible y «seguir leyendo» ---------- */
  function paginaLibro() {
    var id = w.LIBRO_ID; if (!id) return;
    var h1 = $('.ficha h1') || $('main h1'); if (!h1) return;
    var lector = d.getElementById('lector');
    var leible = !!lector && !/^ref-/.test(id);
    if (!$('.az-bib-tipo')) {
      var p = d.createElement('p'); p.className = 'az-bib-tipo ' + (leible ? 'leer' : 'ficha');
      p.textContent = leible ? 'Libro completo: se lee gratis aquí' : 'Ficha del libro: aquí no se lee, te contamos de qué trata y dónde conseguirlo';
      h1.parentNode.insertBefore(p, h1);
    }
    if (!leible) return;
    var info = d.getElementById('pag-info');
    var img = $('.ficha .portada img'), aut = $('.ficha .autores');
    var base = { id: id, t: h1.textContent.trim(), a: aut ? aut.textContent.trim() : '', img: img ? img.src : '', u: location.origin + location.pathname };
    var todos = lee(K_LEIDOS, []), yo = todos.filter(function (x) { return x.id === id; })[0];
    function anotar(pg, total) {
      var L = lee(K_LEIDOS, []).filter(function (x) { return x.id !== id; });
      L.unshift(Object.assign({}, base, { p: pg, n: total, ts: Date.now() })); guarda(K_LEIDOS, L.slice(0, 24));
    }
    if (yo && yo.p > 2) {
      var acc = $('.ficha .acciones');
      var b = d.createElement('div'); b.className = 'az-seguir';
      b.innerHTML = '<span>Te quedaste en la página <b>' + yo.p + '</b>' + (yo.n ? ' de ' + yo.n : '') + '.</span><button type="button" class="btn">Seguir en la página ' + yo.p + '</button>';
      (acc || h1).parentNode.insertBefore(b, acc ? acc.nextSibling : h1.nextSibling);
      b.querySelector('button').onclick = function () {
        var intentos = 0;
        (function ir() {
          var pg = d.querySelector('.pagina[data-n="' + yo.p + '"]');
          if (pg) { pg.scrollIntoView({ block: 'start' }); return; }
          if (++intentos < 40) setTimeout(ir, 250);
        })();
      };
    }
    if (info) {
      var t1;
      new MutationObserver(function () {
        var m = /P[áa]gina (\d+) de (\d+)/.exec(info.textContent || ''); if (!m) return;
        clearTimeout(t1); t1 = setTimeout(function () { if (+m[1] > 1 || lee(K_LEIDOS, []).some(function (x) { return x.id === id; })) anotar(+m[1], +m[2]); }, 1200);
      }).observe(info, { childList: true, characterData: true, subtree: true });
    }
    d.addEventListener('click', function (e) { var a = e.target.closest('a[href="#lector"]'); if (a) anotar((yo && yo.p) || 1, yo && yo.n); });
  }

  /* ---------- 3. portada de la biblioteca: seguir leyendo y tus guardados ---------- */
  function estanterias() {
    if (!/^\/biblioteca\/?(index\.html)?$/.test(location.pathname)) return;
    var leidos = lee(K_LEIDOS, []).slice(0, 12);
    var g = lee('az-guardados', { l: [] }), guard = (g.l || []).filter(function (x) { return /\/(biblioteca\/libro|libros)\//.test(x.u || ''); }).slice(0, 12);
    if (!leidos.length && !guard.length) return;
    catalogo().then(function (B) {
      var porId = {}; if (B) B.libros.forEach(function (l) { porId[l.id] = l; });
      function idDe(u) { var m = /libro\/([^/.]+)\.html/.exec(u || ''); return m ? m[1] : ''; }
      function tarjeta(u, t, a, img, extra) {
        return '<a href="' + E(u) + '">' + (img ? '<img src="' + E(img) + '" alt="" loading="lazy">' : '<span class="ph" aria-hidden="true"></span>') + '<b>' + E(t) + '</b>' + (a ? '<small>' + E(a) + '</small>' : '') + (extra || '') + '</a>';
      }
      var html = '';
      if (leidos.length) html += '<section class="az-estante" aria-labelledby="azSeguirT"><h2 id="azSeguirT">Seguir leyendo</h2><p>Los libros que abriste en este navegador, con la página por la que vas.</p><div class="az-fila">' +
        leidos.map(function (x) { var pct = x.n ? Math.round(x.p / x.n * 100) : 0;
          return tarjeta(x.u, x.t, String(x.a || '').split(';')[0], x.img || portadaUrl(porId[x.id]), '<span class="az-barra-p" role="img" aria-label="Vas por la página ' + x.p + (x.n ? ' de ' + x.n : '') + '"><i style="width:' + pct + '%"></i></span><small>Página ' + x.p + (x.n ? ' de ' + x.n : '') + '</small>'); }).join('') + '</div></section>';
      if (guard.length) html += '<section class="az-estante" aria-labelledby="azGuardT"><h2 id="azGuardT">Tus libros guardados</h2><p>Los que guardaste con el botón Guardar. Los tienes también en «Guardados», arriba.</p><div class="az-fila">' +
        guard.map(function (x) { var l = porId[idDe(x.u)]; return tarjeta(x.u, x.t, l ? String(l.autores || '').split(';')[0] : '', portadaUrl(l)); }).join('') + '</div></section>';
      var cont = d.createElement('div'); cont.className = 'wrap az-estantes'; cont.innerHTML = html;
      var dest = null; d.querySelectorAll('main section, main .estante, main h2').forEach(function (s) { if (!dest && /Novedades/.test(s.textContent.slice(0, 60))) dest = s.closest('section') || s; });
      if (dest && dest.parentNode) dest.parentNode.insertBefore(cont, dest); else ($('main') || d.body).appendChild(cont);
    });
  }

  function iniciar() {
    sugerencias(d.getElementById('q'));
    paginaLibro();
    estanterias();
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(window, document);
