/* AURZANE NEXUS · Universidades (lógica compartida) */
(function () {
  'use strict';
  var BASE = '/universidades/';
  var V = document.documentElement.getAttribute('data-v') || '1';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ ]+/g, ' ').replace(/\s+/g, ' ').trim(); }
  function fmt(n) { return Number(n || 0).toLocaleString('es-ES'); }
  function ls(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null'); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  var cache = {};
  function json(ruta) {
    if (!cache[ruta]) cache[ruta] = fetch(BASE + ruta + '?v=' + V).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    return cache[ruta];
  }
  function iniciales(n) {
    var w = String(n).replace(/\(.*?\)/g, '').split(/\s+/).filter(function (x) { return x.length > 2 && !/^(de|del|la|las|los|y|en|para|the|of|and|for|und|der|di|du|des)$/i.test(x); });
    return (w.slice(0, 2).map(function (x) { return x[0]; }).join('') || String(n).slice(0, 2)).toUpperCase();
  }
  function bandera(iso, cls) { return iso ? '<img class="bandera ' + (cls || '') + '" src="https://flagcdn.com/w40/' + iso + '.png" srcset="https://flagcdn.com/w80/' + iso + '.png 2x" alt="" width="28" height="21" loading="lazy">' : ''; }

  /* ---------- tema y menú ---------- */
  var bt = $('#btnTema');
  if (bt) bt.addEventListener('click', function () {
    var osc = document.documentElement.getAttribute('data-tema') === 'oscuro';
    if (osc) document.documentElement.removeAttribute('data-tema'); else document.documentElement.setAttribute('data-tema', 'oscuro');
    try { localStorage.setItem('aurzane-tema', osc ? 'claro' : 'oscuro'); } catch (e) {}
  });
  var mb = $('.menu-btn');
  if (mb) mb.addEventListener('click', function () { var n = $('.topnav'); var a = n.classList.toggle('abierto'); mb.setAttribute('aria-expanded', String(a)); });

  /* ---------- mi lista (guardadas y comparar) ---------- */
  var CL = 'aurzane-univ-lista';
  function lista() { return ls(CL) || []; }
  function enLista(id) { return lista().some(function (x) { return x.id === id; }); }
  function alternar(u) {
    var l = lista(), i = l.findIndex(function (x) { return x.id === u.id; });
    if (i >= 0) l.splice(i, 1); else { if (l.length >= 30) l.shift(); l.push(u); }
    ls(CL, l); pintarLista(); return i < 0;
  }
  function pintarLista() {
    var n = lista().length;
    $$('.lista-n').forEach(function (e) { e.textContent = n; e.hidden = !n; });
    $$('[data-guardar]').forEach(function (b) {
      var on = enLista(b.getAttribute('data-id'));
      b.setAttribute('aria-pressed', String(on));
      if (b.hasAttribute('data-fijo')) return;
      if (b.classList.contains('btn')) b.innerHTML = on ? '★ Guardada' : '☆ Guardar';
      else b.textContent = on ? '★' : '☆';
      b.setAttribute('aria-label', (on ? 'Quitar de mi lista: ' : 'Guardar en mi lista: ') + b.getAttribute('data-n'));
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-guardar]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    alternar({ id: b.getAttribute('data-id'), n: b.getAttribute('data-n'), u: b.getAttribute('data-url') });
  });
  pintarLista();

  /* favoritos del buscador anterior: se pasan a Mi lista una sola vez */
  (function () {
    var viejos = ls('aurzane_favoritos_universidades');
    if (!viejos || !viejos.length || ls('aurzane-univ-migrada')) return;
    json('datos/indice.json').then(function (d) {
      var l = lista();
      viejos.forEach(function (f) {
        var nn = norm(f.universidad), pn = norm(f.pais);
        var u = d.u.find(function (x) { return norm(x[0]) === nn && norm(d.p[x[1]][2]) === pn; });
        if (!u) return;
        var id = d.p[u[1]][0] + '/' + u[2];
        if (!l.some(function (x) { return x.id === id; })) l.push({ id: id, n: u[0], u: BASE + id + '/' });
      });
      ls(CL, l.slice(-30)); ls('aurzane-univ-migrada', 1); pintarLista();
      if (document.getElementById('miLista') && typeof window.__univPintarMiLista === 'function') window.__univPintarMiLista();
    });
  })();

  /* ---------- buscador global (portada y cabeceras) ---------- */
  function buscador(input) {
    var caja = input.parentNode.querySelector('.sugs'), sel = -1, items = [];
    function pinta(q) {
      json('datos/indice.json').then(function (d) {
        var nq = norm(q);
        if (nq.length < 2) { caja.hidden = true; return; }
        var palabras = nq.split(' ');
        var res = [];
        for (var i = 0; i < d.u.length; i++) {
          var u = d.u[i], k = u[7] || (u[7] = norm(u[0] + ' ' + u[3] + ' ' + (u[8] || '')));
          var ok = palabras.every(function (p) { return k.indexOf(p) >= 0; });
          if (!ok) continue;
          var nn = norm(u[0]), s = nn.indexOf(nq) === 0 ? 0 : (nn.indexOf(' ' + nq) >= 0 ? 1 : (nn.indexOf(nq) >= 0 ? 2 : 3));
          res.push([s, -u[6], u]);
        }
        res.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
        items = res.slice(0, 9).map(function (r) { return r[2]; });
        sel = -1;
        var p = d.p;
        caja.innerHTML = items.length ? items.map(function (u, i) {
          var pa = p[u[1]];
          return '<a href="' + BASE + pa[0] + '/' + u[2] + '/" role="option" id="sg' + i + '">' + bandera(pa[1]) + '<span><b>' + resaltar(u[0], palabras) + '</b><small>' + esc(u[3] ? u[3] + ', ' : '') + esc(pa[2]) + (u[6] ? ' · ' + fmt(u[6]) + (pa[0] === 'espana' ? ' grados' : ' carreras') : '') + '</small></span></a>';
        }).join('') + (res.length > 9 ? '<div class="vacio">' + fmt(res.length) + ' resultados. Sigue escribiendo para afinar.</div>' : '') + carr(q) :
          '<div class="vacio">No encontramos universidades con ese nombre.</div>' + carr(q);
        caja.hidden = false;
        input.setAttribute('aria-expanded', 'true');
      });
    }
    function carr(q) {
      if (norm(q).length < 3) return '';
      return '<a class="sug-carr" href="' + BASE + 'espana/?q=' + encodeURIComponent(q) + '"><span aria-hidden="true">🎓</span><span><b>Buscar «' + esc(q) + '» como grado en España</b><small>Universidades que imparten esa carrera</small></span></a>' +
        '<a class="sug-carr" href="' + BASE + 'ecuador/?q=' + encodeURIComponent(q) + '"><span aria-hidden="true">🎓</span><span><b>Buscar «' + esc(q) + '» como carrera en Ecuador</b><small>Universidades e institutos que la ofrecen</small></span></a>';
    }
    function resaltar(t, ps) {
      var out = esc(t), nt = norm(t);
      // resaltado sencillo por coincidencia sin acentos
      ps.forEach(function (p) {
        if (!p) return;
        var i = nt.indexOf(p);
        if (i >= 0) { var orig = t.substr(i, p.length); out = out.replace(esc(orig), '<mark>' + esc(orig) + '</mark>'); }
      });
      return out;
    }
    input.addEventListener('focus', function () { json('datos/indice.json'); if (input.value) pinta(input.value); });
    try { var q0 = new URLSearchParams(location.search).get('q'); if (q0 && !input.value) { input.value = q0; pinta(q0); } } catch (e) {}
    input.addEventListener('input', function () { pinta(input.value); });
    input.addEventListener('keydown', function (e) {
      var as = $$('a', caja);
      if (e.key === 'ArrowDown') { sel = Math.min(as.length - 1, sel + 1); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { sel = Math.max(-1, sel - 1); e.preventDefault(); }
      else if (e.key === 'Enter') { if (as[sel >= 0 ? sel : 0]) { location.href = as[sel >= 0 ? sel : 0].href; e.preventDefault(); } return; }
      else if (e.key === 'Escape') { caja.hidden = true; return; }
      else return;
      as.forEach(function (a, i) { a.classList.toggle('sel', i === sel); });
      if (as[sel]) { input.setAttribute('aria-activedescendant', as[sel].id); as[sel].scrollIntoView({ block: 'nearest' }); }
    });
    document.addEventListener('click', function (e) { if (!input.parentNode.contains(e.target)) caja.hidden = true; });
    var q = new URLSearchParams(location.search).get('q');
    if (q) { input.value = q; pinta(q); }
  }
  $$('[data-buscador]').forEach(buscador);

  /* ---------- listado de país / ciudad ---------- */
  var L = $('#listado');
  if (L) (function () {
    var pais = L.getAttribute('data-pais'), ciudadFija = L.getAttribute('data-ciudad') || '';
    var st = { q: '', region: '', ciudad: ciudadFija, tipo: '', ies: '', area: '', con: false, orden: 'rel', vistas: 36 };
    var D = null, C = null, cargandoC = null, porArea = null;
    var qs = new URLSearchParams(location.search);
    ['q', 'region', 'ciudad', 'tipo', 'ies', 'area'].forEach(function (k) { if (qs.get(k)) st[k] = qs.get(k); });
    if (qs.get('con') === '1') st.con = true;
    function carreras() {
      if (!L.getAttribute('data-carreras')) return Promise.resolve(null);
      if (!cargandoC) cargandoC = json('datos/' + pais + '-carreras.json').then(function (c) { C = c; return c; });
      return cargandoC;
    }
    json('datos/' + pais + '.json').then(function (d) {
      D = d;
      D.u.forEach(function (u, i) { u.i = i; u.k = norm(u[1] + ' ' + u[2] + ' ' + u[3] + ' ' + (u[9] || '')); });
      llenarSelects(); leerControles(); pintar();
      if (st.q.length >= 3 || st.area) carreras().then(pintar);
    });
    function opcs(sel, vals, actual, todos) {
      if (!sel) return;
      sel.innerHTML = '<option value="">' + todos + '</option>' + vals.map(function (v) { return '<option' + (v[0] === actual ? ' selected' : '') + ' value="' + esc(v[0]) + '">' + esc(v[0]) + ' (' + v[1] + ')</option>'; }).join('');
    }
    function conteo(fn, filtro) {
      var m = {};
      D.u.forEach(function (u) { if (filtro && !filtro(u)) return; var v = fn(u); if (v) (Array.isArray(v) ? v : [v]).forEach(function (x) { m[x] = (m[x] || 0) + 1; }); });
      return Object.keys(m).sort(function (a, b) { return a.localeCompare(b, 'es'); }).map(function (k) { return [k, m[k]]; });
    }
    function llenarSelects() {
      opcs($('#fRegion'), conteo(function (u) { return u[3]; }), st.region, 'Todas');
      opcs($('#fCiudad'), conteo(function (u) { return u[2]; }, function (u) { return !st.region || u[3] === st.region; }), st.ciudad, 'Todas');
      opcs($('#fIes'), conteo(function (u) { return u[5]; }), st.ies, 'Todos');
      if ($('#fArea')) opcs($('#fArea'), conteo(function (u) { return (u[8] || []).map(function (a) { return D.areas[a]; }); }), st.area, 'Todas');
    }
    function leerControles() {
      if ($('#fQ')) $('#fQ').value = st.q;
      $$('#fTipo button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === st.tipo)); });
      if ($('#fCon')) $('#fCon').checked = st.con;
      if ($('#fOrden')) $('#fOrden').value = st.orden;
    }
    function filtrar() {
      var nq = norm(st.q), ps = nq ? nq.split(' ') : [], hitsCarr = {};
      if (C && nq.length >= 3) {
        C.c.forEach(function (c) {
          var k = c[3] || (c[3] = norm(c[1]));
          if (ps.every(function (p) { return k.indexOf(p) >= 0; })) (hitsCarr[c[0]] = hitsCarr[c[0]] || []).push(c);
        });
      }
      var areaIdx = st.area ? D.areas.indexOf(st.area) : -1;
      var r = D.u.filter(function (u) {
        if (st.region && u[3] !== st.region) return false;
        if (st.ciudad && u[2] !== st.ciudad) return false;
        if (st.tipo && u[4] !== st.tipo) return false;
        if (st.ies && u[5] !== st.ies) return false;
        if (st.con && !u[6]) return false;
        if (areaIdx >= 0 && (u[8] || []).indexOf(areaIdx) < 0) return false;
        if (ps.length && !ps.every(function (p) { return u.k.indexOf(p) >= 0; }) && !hitsCarr[u.i]) return false;
        return true;
      });
      if (st.orden === 'az') r.sort(function (a, b) { return a[1].localeCompare(b[1], 'es'); });
      else if (st.orden === 'carr') r.sort(function (a, b) { return b[6] - a[6]; });
      else {
        var esU = function (u) { return /^universi/i.test(u[5] || 'Universidad') ? 0 : 1; };
        var coin = function (u) { return !ps.length || ps.every(function (p) { return u.k.indexOf(p) >= 0; }) ? 0 : 1; };
        r.sort(function (a, b) { return coin(a) - coin(b) || esU(a) - esU(b) || b[6] - a[6] || a[1].localeCompare(b[1], 'es'); });
      }
      return { r: r, hits: hitsCarr };
    }
    function tarjeta(u, hits) {
      var tipo = u[4] ? '<span class="etq ' + (/^p[uú]blica/i.test(u[4]) ? 'pub' : 'priv') + '">' + esc(u[4]) + '</span>' : '';
      var url = BASE + pais + '/' + u[0] + '/';
      var extra = hits ? '<p class="lugar" style="margin-top:8px">🎓 ' + hits.slice(0, 2).map(function (c) { return esc(c[1]); }).join(' · ') + (hits.length > 2 ? ' y ' + (hits.length - 2) + ' más' : '') + '</p>' : '';
      return '<article class="uc"><div class="top"><span class="mono" aria-hidden="true">' + (u[10] ? '<img src="' + esc(u[10]) + '" alt="" loading="lazy" onerror="this.remove()">' : '') + esc(iniciales(u[1])) + '</span><div style="min-width:0;flex:1"><h3><a href="' + url + '">' + esc(u[1]) + '</a></h3><p class="lugar">📍 ' + esc([u[2], u[3]].filter(Boolean).join(', ') || D.pais) + '</p></div><button class="guardar" type="button" data-guardar data-id="' + esc(pais + '/' + u[0]) + '" data-n="' + esc(u[1]) + '" data-url="' + url + '" aria-pressed="false">☆</button></div>' +
        extra + '<div class="etqs">' + tipo + (u[5] ? '<span class="etq">' + esc(u[5]) + '</span>' : '') + '</div>' +
        '<div class="pie"><span>' + (u[6] ? '<b>' + fmt(u[6]) + '</b> ' + (u[7] === 'areas' ? 'áreas' : (pais === 'espana' ? 'grados' : 'carreras')) : 'Carreras en su web') + '</span><span aria-hidden="true">→</span></div></article>';
    }
    function pintar() {
      if (!D) return;
      var f = filtrar(), r = f.r;
      $('#nRes').innerHTML = '<b>' + fmt(r.length) + '</b> ' + (r.length === 1 ? 'institución' : 'instituciones');
      var act = [];
      if (st.q) act.push(['q', '«' + st.q + '»']);
      if (st.region && !L.getAttribute('data-fija-region')) act.push(['region', st.region]);
      if (st.ciudad && !ciudadFija) act.push(['ciudad', st.ciudad]);
      if (st.tipo) act.push(['tipo', st.tipo]);
      if (st.ies) act.push(['ies', st.ies]);
      if (st.area) act.push(['area', st.area]);
      if (st.con) act.push(['con', 'Con carreras']);
      $('#activos').innerHTML = act.map(function (a) { return '<button type="button" data-quitar="' + a[0] + '">' + esc(a[1]) + '</button>'; }).join('');
      var coinc = $('#coinc');
      var nh = Object.keys(f.hits).length;
      if (coinc) {
        if (st.q.length >= 3 && nh) {
          var lista = [];
          r.forEach(function (u) { (f.hits[u.i] || []).forEach(function (c) { lista.push([u, c]); }); });
          coinc.hidden = false;
          coinc.innerHTML = '<h3>🎓 ' + fmt(lista.length) + ' carreras coinciden con «' + esc(st.q) + '»</h3><ul>' + lista.slice(0, 8).map(function (x) {
            return '<li><a href="' + BASE + pais + '/' + x[0][0] + '/#carreras">' + esc(x[1][1]) + '</a> <small>· ' + esc(x[0][1]) + (x[0][2] ? ', ' + esc(x[0][2]) : '') + '</small></li>';
          }).join('') + '</ul>' + (lista.length > 8 ? '<p class="sub" style="margin:8px 0 0;font-size:.85rem">Las universidades que las ofrecen aparecen abajo.</p>' : '');
        } else coinc.hidden = true;
      }
      var g = $('#grid');
      if (!r.length) { g.innerHTML = '<div class="vacio-res">No hay instituciones con estos filtros. <button class="btn btn-sm btn-osc" type="button" id="limpiar2">Quitar filtros</button></div>'; $('#mas').hidden = true; return; }
      g.innerHTML = r.slice(0, st.vistas).map(function (u) { return tarjeta(u, f.hits[u.i]); }).join('');
      $('#mas').hidden = r.length <= st.vistas;
      $('#mas button').textContent = 'Ver ' + fmt(Math.min(36, r.length - st.vistas)) + ' más de ' + fmt(r.length - st.vistas);
      pintarLista();
      var p = new URLSearchParams();
      ['q', 'region', 'tipo', 'ies', 'area'].forEach(function (k) { if (st[k]) p.set(k, st[k]); });
      if (st.ciudad && !ciudadFija) p.set('ciudad', st.ciudad);
      if (st.con) p.set('con', '1');
      history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : ''));
    }
    var tq;
    L.addEventListener('input', function (e) {
      var t = e.target;
      if (t.id === 'fQ') { st.q = t.value.trim(); st.vistas = 36; clearTimeout(tq); tq = setTimeout(function () { if (st.q.length >= 3) carreras().then(pintar); pintar(); }, 160); return; }
      if (t.id === 'fRegion') { st.region = t.value; st.ciudad = ciudadFija; llenarSelects(); }
      if (t.id === 'fCiudad') st.ciudad = t.value;
      if (t.id === 'fIes') st.ies = t.value;
      if (t.id === 'fArea') { st.area = t.value; }
      if (t.id === 'fCon') st.con = t.checked;
      if (t.id === 'fOrden') st.orden = t.value;
      st.vistas = 36; pintar();
    });
    L.addEventListener('click', function (e) {
      var b = e.target.closest('#fTipo button');
      if (b) { st.tipo = b.getAttribute('data-v'); leerControles(); st.vistas = 36; pintar(); return; }
      var q = e.target.closest('[data-quitar]');
      if (q) { var k = q.getAttribute('data-quitar'); st[k] = k === 'con' ? false : ''; if (k === 'region') llenarSelects(); leerControles(); llenarSelects(); pintar(); return; }
      if (e.target.closest('#limpiar') || e.target.closest('#limpiar2')) { st = { q: '', region: '', ciudad: ciudadFija, tipo: '', ies: '', area: '', con: false, orden: 'rel', vistas: 36 }; llenarSelects(); leerControles(); pintar(); return; }
      if (e.target.closest('#mas button')) { st.vistas += 36; pintar(); return; }
      if (e.target.closest('#togFiltros')) { var f = $('.filtros'); var c = f.classList.toggle('cerrado'); e.target.closest('#togFiltros').setAttribute('aria-expanded', String(!c)); }
    });
  })();

  /* ---------- ficha: filtrar carreras ---------- */
  var FC = $('#carreras');
  if (FC) (function () {
    var q = '', area = '';
    function aplicar() {
      var nq = norm(q), total = 0;
      $$('.grupo', FC).forEach(function (g) {
        var vis = 0, okArea = !area || g.getAttribute('data-area') === area;
        $$('li', g).forEach(function (li) {
          var ok = okArea && (!nq || (li.k || (li.k = norm(li.textContent))).indexOf(nq) >= 0);
          li.hidden = !ok; if (ok) vis++;
        });
        g.hidden = !vis; total += vis;
      });
      var v = $('#carrVacio'); if (v) v.hidden = total > 0;
    }
    var inp = $('.carr-busca', FC);
    if (inp) inp.addEventListener('input', function () { q = inp.value; aplicar(); });
    FC.addEventListener('click', function (e) {
      var c = e.target.closest('.chip');
      if (!c) return;
      area = c.getAttribute('data-area') || '';
      $$('.chip', FC).forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); });
      aplicar();
    });
  })();

  /* ---------- mi lista ---------- */
  var ML = $('#miLista');
  if (ML) (function () {
    function pintar() {
      var l = lista();
      if (!l.length) {
        ML.innerHTML = '<div class="vacio-res"><p style="margin:0 0 12px">Todavía no has guardado universidades.</p><p style="margin:0 0 14px">Pulsa ☆ en cualquier universidad para guardarla aquí y compararla con otras.</p><a class="btn btn-osc" href="' + BASE + '">Buscar universidades</a></div>';
        return;
      }
      json('datos/indice.json').then(function (d) {
        var mapa = {};
        d.u.forEach(function (u) { mapa[d.p[u[1]][0] + '/' + u[2]] = u; });
        var cols = l.map(function (x) { return [x, mapa[x.id]]; });
        var fila = function (t, fn) { return '<tr><th scope="row">' + t + '</th>' + cols.map(function (c) { return '<td>' + (c[1] ? fn(c[1], c[0]) : '-') + '</td>'; }).join('') + '</tr>'; };
        ML.innerHTML = '<div class="comp"><table><thead><tr><th scope="col">Universidad</th>' + cols.map(function (c) {
          return '<td><a href="' + esc(c[0].u) + '">' + esc(c[0].n) + '</a><br><button type="button" class="btn btn-sm btn-borde" style="margin-top:8px" data-guardar data-fijo data-id="' + esc(c[0].id) + '" data-n="' + esc(c[0].n) + '" data-url="' + esc(c[0].u) + '">Quitar</button></td>';
        }).join('') + '</tr></thead><tbody>' +
          fila('País', function (u) { var p = d.p[u[1]]; return bandera(p[1]) + ' ' + esc(p[2]); }) +
          fila('Ciudad', function (u) { return esc(u[3] || '-'); }) +
          fila('Región', function (u) { return esc(u[8] || '-'); }) +
          fila('Tipo', function (u) { return esc(u[4] || '-'); }) +
          fila('Institución', function (u) { return esc(u[5] || '-'); }) +
          fila('Carreras', function (u) { return u[6] ? fmt(u[6]) : 'Consultar en su web'; }) +
          '</tbody></table></div>';
        pintarLista();
      });
    }
    pintar(); window.__univPintarMiLista = pintar;
    document.addEventListener('click', function (e) { if (e.target.closest('#miLista [data-guardar]')) setTimeout(pintar, 0); });
  })();
})();
