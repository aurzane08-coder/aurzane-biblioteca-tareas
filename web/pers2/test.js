/* AURZANE MIND · Test de personalidad (lógica). Datos en datos.js */
(function () {
  'use strict';
  var B = window.BIG5;
  var ORDEN = ['E', 'A', 'C', 'S', 'O'];
  var DOM120 = ['N', 'E', 'O', 'A', 'C'];
  var NOMBRE_V = { 20: 'Test exprés', 50: 'Test clásico', 120: 'Test completo' };
  var POR_PAG = { 20: 5, 50: 10, 120: 10 };
  var SB_URL = 'https://chtfpqwrrarfdjcivlad.supabase.co';
  var SB_KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw';
  var LIBRO = 'https://aurzane.com/biblioteca/libro/';
  var BASE = '/test-de-personalidad/';
  var SLUG = { EA: 'fogata', EC: 'timon', ES: 'sol', EO: 'cometa', AC: 'raiz', AS: 'remanso', AO: 'puente', CS: 'faro', CO: 'telescopio', SO: 'horizonte', PRISMA: 'prisma' };
  function imgPerfil(k) { return BASE + 'img/' + k.toLowerCase() + '.svg'; }
  var $ = function (id) { return document.getElementById(id); };

  function ls(k, v) {
    try {
      if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null');
      if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v));
    } catch (e) { return null; }
  }
  function ss(k, v) {
    try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; }
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- Ítems por versión ---------- */
  function items(v) {
    if (v === 20) return B.I20_IDX.map(function (i) { var x = B.I50[i]; return { r: x[0], k: x[1], t: x[2] }; });
    if (v === 50) return B.I50.map(function (x) { return { r: x[0], k: x[1], t: x[2] }; });
    return B.I120.map(function (x) {
      return { r: x[0] === 'N' ? 'S' : x[0], k: x[0] === 'N' ? -x[2] : x[2], d: x[0], f: x[1], kf: x[2], t: x[3] };
    });
  }

  /* ---------- Puntuación ---------- */
  function puntuar(v, resp) {
    var its = items(v), suma = {}, n = {}, fs = {}, fn = {};
    ORDEN.forEach(function (r) { suma[r] = 0; n[r] = 0; });
    its.forEach(function (it, i) {
      var x = resp[i]; if (!x) return;
      suma[it.r] += it.k > 0 ? x : 6 - x; n[it.r]++;
      if (v === 120) {
        var key = it.d + it.f;
        fs[key] = (fs[key] || 0) + (it.kf > 0 ? x : 6 - x); fn[key] = (fn[key] || 0) + 1;
      }
    });
    var rasgos = {};
    ORDEN.forEach(function (r) { rasgos[r] = n[r] ? Math.round((suma[r] - n[r]) / (4 * n[r]) * 100) : 50; });
    var facetas = null;
    if (v === 120) {
      facetas = [];
      DOM120.forEach(function (d) { for (var f = 1; f <= 6; f++) { var k = d + f; facetas.push(Math.round((fs[k] - fn[k]) / (4 * fn[k]) * 100)); } });
    }
    return { v: v, rasgos: rasgos, facetas: facetas, perfil: perfilDe(rasgos) };
  }
  function perfilDe(r) {
    var vals = ORDEN.map(function (k) { return r[k]; });
    if (Math.max.apply(null, vals) - Math.min.apply(null, vals) < 15) return 'PRISMA';
    var top = ORDEN.slice().sort(function (a, b) { return r[b] - r[a] || ORDEN.indexOf(a) - ORDEN.indexOf(b); }).slice(0, 2);
    top.sort(function (a, b) { return ORDEN.indexOf(a) - ORDEN.indexOf(b); });
    return top.join('');
  }
  function aHash(res) {
    var p = [res.v].concat(ORDEN.map(function (k) { return res.rasgos[k]; }));
    if (res.facetas) p = p.concat(res.facetas);
    return 'r=' + p.join('.');
  }
  function deHash(h) {
    var m = /r=([\d.]+)/.exec(h || ''); if (!m) return null;
    var p = m[1].split('.').map(Number), v = p[0];
    if ([20, 50, 120].indexOf(v) < 0 || p.length < 6) return null;
    var rasgos = {}, ok = true;
    ORDEN.forEach(function (k, i) { var x = p[i + 1]; if (!(x >= 0 && x <= 100)) ok = false; rasgos[k] = x; });
    if (!ok) return null;
    var facetas = (v === 120 && p.length === 36) ? p.slice(6).map(function (x) { return Math.max(0, Math.min(100, x || 0)); }) : null;
    return { v: v, rasgos: rasgos, facetas: facetas, perfil: perfilDe(rasgos) };
  }
  window.__big5 = { puntuar: puntuar, perfilDe: perfilDe, aHash: aHash, deHash: deHash, items: items };

  /* ---------- Vistas ---------- */
  function mostrar(id) {
    ['inicio', 'test', 'resultados'].forEach(function (x) { $(x).hidden = x !== id; });
    window.scrollTo(0, 0);
  }

  /* ---------- Radar SVG ---------- */
  function radarSVG(svg, vals, opts) {
    opts = opts || {};
    var cx = 150, cy = 150, R = opts.R || 100, NS = 'http://www.w3.org/2000/svg', h = '';
    function pt(i, f) { var a = -Math.PI / 2 + i * 2 * Math.PI / 5; return [cx + Math.cos(a) * R * f, cy + Math.sin(a) * R * f]; }
    var gc = opts.claro ? 'rgba(255,255,255,.22)' : 'var(--border)';
    var tc = opts.claro ? '#fff' : 'var(--text)';
    h += '<defs><linearGradient id="gr' + (opts.id || '') + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffb347" stop-opacity=".85"/><stop offset=".5" stop-color="#ff7a9c" stop-opacity=".75"/><stop offset="1" stop-color="#a35be0" stop-opacity=".85"/></linearGradient></defs>';
    [.25, .5, .75, 1].forEach(function (f) {
      h += '<polygon points="' + [0, 1, 2, 3, 4].map(function (i) { return pt(i, f).join(','); }).join(' ') + '" fill="none" stroke="' + gc + '" stroke-width="1"/>';
    });
    ORDEN.forEach(function (k, i) { var p = pt(i, 1); h += '<line x1="' + cx + '" y1="' + cy + '" x2="' + p[0] + '" y2="' + p[1] + '" stroke="' + gc + '"/>'; });
    var pts = ORDEN.map(function (k, i) { return pt(i, Math.max(.06, vals[k] / 100)).join(','); }).join(' ');
    h += '<polygon class="forma" points="' + pts + '" fill="url(#gr' + (opts.id || '') + ')" stroke="#fff" stroke-width="2" stroke-linejoin="round"/>';
    ORDEN.forEach(function (k, i) {
      var p = pt(i, Math.max(.06, vals[k] / 100));
      h += '<circle class="forma" cx="' + p[0] + '" cy="' + p[1] + '" r="6" fill="' + B.RASGOS[k].color + '" stroke="#fff" stroke-width="2"/>';
    });
    ORDEN.forEach(function (k, i) {
      var p = pt(i, 1.27), anchor = Math.abs(p[0] - cx) < 10 ? 'middle' : (p[0] > cx ? 'start' : 'end');
      if (i === 1 || i === 4) p[0] += (i === 1 ? -14 : 14);
      if (i === 1 || i === 4) anchor = 'middle';
      h += '<text x="' + p[0] + '" y="' + (p[1] - 2) + '" text-anchor="' + anchor + '" font-size="13" font-weight="700" fill="' + tc + '" font-family="Instrument Sans,sans-serif">' + B.RASGOS[k].emoji + ' ' + B.RASGOS[k].corto + '</text>';
      if (opts.numeros) h += '<text x="' + p[0] + '" y="' + (p[1] + 14) + '" text-anchor="' + anchor + '" font-size="13" font-weight="700" fill="' + B.RASGOS[k].color + '" font-family="Instrument Sans,sans-serif">' + vals[k] + '</text>';
    });
    svg.setAttribute('viewBox', '-62 -8 424 318');
    svg.innerHTML = h;
  }

  /* ---------- Portada ---------- */
  function portada() {
    $('rasgos5').innerHTML = ORDEN.map(function (k) {
      var r = B.RASGOS[k];
      return '<div class="r5' + (k === 'S' ? ' claro' : '') + '" style="--c:' + r.color + '"><span class="e">' + r.emoji + '</span><b>' + r.nombre + '</b><span>' + esc(r.que) + '</span></div>';
    }).join('');
    $('perfilesGrid').innerHTML = Object.keys(B.PERFILES).map(function (k) {
      var p = B.PERFILES[k];
      return '<div class="pf" style="--g1:' + p.g[0] + ';--g2:' + p.g[1] + '"><img class="pfi" src="' + imgPerfil(k) + '" alt="" width="84" height="84" loading="lazy"><b>' + p.nombre + '</b><span>' + esc(p.lema) + '</span></div>';
    }).join('');
    var demo = { E: 70, A: 55, C: 80, S: 45, O: 75 };
    radarSVG($('radarHero'), demo, { claro: true, id: 'h' });
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setInterval(function () {
        if ($('inicio').hidden || document.hidden) return;
        ORDEN.forEach(function (k) { demo[k] = 30 + Math.round(Math.random() * 65); });
        radarSVG($('radarHero'), demo, { claro: true, id: 'h' });
      }, 2600);
    }
    var pend = ls('aurzane-big5-pendiente');
    if (pend && ls('aurzane-big5-v' + pend)) {
      $('avisoContinuar').hidden = false;
      $('lnkContinuar').onclick = function (e) { e.preventDefault(); empezar(pend); };
    }
  }

  /* ---------- Test ---------- */
  var st = null;
  function empezar(v) {
    v = Number(v);
    var prev = ls('aurzane-big5-v' + v);
    var its = items(v);
    st = { v: v, its: its, resp: (prev && prev.r && prev.r.length === its.length) ? prev.r : new Array(its.length).fill(0), p: prev ? prev.p || 0 : 0 };
    ls('aurzane-big5-pendiente', v);
    $('txtVersion').textContent = NOMBRE_V[v];
    history.replaceState(null, '', location.pathname);
    mostrar('test');
    pintarPagina();
  }
  function paginas() { return Math.ceil(st.its.length / POR_PAG[st.v]); }
  function guardarProg() { ls('aurzane-big5-v' + st.v, { r: st.resp, p: st.p }); }
  function progreso() {
    var hechas = st.resp.filter(Boolean).length, tot = st.its.length, pct = Math.round(hechas / tot * 100);
    $('txtResp').textContent = hechas + ' de ' + tot + ' · página ' + (st.p + 1) + ' de ' + paginas();
    $('barraRelleno').style.width = pct + '%';
    $('barraProg').setAttribute('aria-valuenow', pct);
  }
  function pintarPagina() {
    var ini = st.p * POR_PAG[st.v], fin = Math.min(ini + POR_PAG[st.v], st.its.length), h = '';
    var etiquetas = ['Totalmente en desacuerdo', 'En desacuerdo', 'Neutral', 'De acuerdo', 'Totalmente de acuerdo'];
    for (var i = ini; i < fin; i++) {
      h += '<fieldset class="preg' + (st.resp[i] ? ' hecha' : '') + '" id="q' + i + '" style="border:0;margin:0;min-width:0">' +
        '<legend class="sr">Pregunta ' + (i + 1) + '</legend><h3>' + esc(st.its[i].t) + '</h3><div class="escala"><span class="ext d" aria-hidden="true">En desacuerdo</span>';
      for (var x = 1; x <= 5; x++) {
        h += '<label class="op" data-v="' + x + '"><input type="radio" name="q' + i + '" value="' + x + '"' + (st.resp[i] === x ? ' checked' : '') + '><span class="c"></span><span class="sr">' + etiquetas[x - 1] + '</span></label>';
      }
      h += '<span class="ext a" aria-hidden="true">De acuerdo</span></div><div class="ext-movil" aria-hidden="true"><span class="d">En desacuerdo</span><span class="a">De acuerdo</span></div></fieldset>';
    }
    $('preguntas').innerHTML = h;
    $('falta').textContent = '';
    $('btnAtras').disabled = st.p === 0;
    $('btnSiguiente').textContent = st.p === paginas() - 1 ? 'Ver mis resultados' : 'Siguiente';
    progreso();
  }
  function onRespuesta(e) {
    var t = e.target; if (t.type !== 'radio') return;
    var i = Number(t.name.slice(1)); st.resp[i] = Number(t.value);
    var fs = $('q' + i); fs.classList.add('hecha');
    guardarProg(); progreso(); $('falta').textContent = '';
    var fin = Math.min((st.p + 1) * POR_PAG[st.v], st.its.length);
    for (var j = i + 1; j < fin; j++) {
      if (!st.resp[j]) { var sig = $('q' + j); setTimeout(function () { sig.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 180); return; }
    }
    setTimeout(function () { $('btnSiguiente').scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 180);
  }
  function onSiguiente(e) {
    e.preventDefault();
    var ini = st.p * POR_PAG[st.v], fin = Math.min(ini + POR_PAG[st.v], st.its.length);
    for (var i = ini; i < fin; i++) {
      if (!st.resp[i]) {
        $('falta').textContent = 'Te falta responder alguna pregunta de esta página.';
        $('q' + i).scrollIntoView({ behavior: 'smooth', block: 'center' });
        var inp = $('q' + i).querySelector('input'); if (inp) inp.focus({ preventScroll: true });
        return;
      }
    }
    if (st.p < paginas() - 1) { st.p++; guardarProg(); pintarPagina(); window.scrollTo(0, 0); return; }
    var res = puntuar(st.v, st.resp);
    ls('aurzane-big5-v' + st.v, null); ls('aurzane-big5-pendiente', null);
    var hash = aHash(res);
    ls('aurzane-big5-ultimo', hash); ss('aurzane-big5-propio', hash);
    history.replaceState(null, '', '#' + hash);
    resultados(res, true, true);
  }

  /* ---------- Resultados ---------- */
  var actual = null;
  function nivel(x) { return x >= 60 ? 'alto' : (x <= 40 ? 'bajo' : 'medio'); }
  function resultados(res, propio, fiesta) {
    actual = res;
    var P = B.PERFILES[res.perfil];
    var hero = $('resHero');
    hero.style.setProperty('--g1', P.g[0]); hero.style.setProperty('--g2', P.g[1]);
    $('resImg').src = imgPerfil(res.perfil); $('resImg').alt = 'Ilustración del perfil ' + P.nombre;
    $('resK').textContent = propio ? 'Tu perfil es' : 'Su perfil es';
    $('resNombre').textContent = P.nombre;
    $('resLema').textContent = P.lema;
    $('resDesc').textContent = P.desc;
    $('avisoCompartido').hidden = propio;
    $('cajaGuardar').hidden = !propio;
    radarSVG($('radarRes'), res.rasgos, { numeros: true, id: 'r' });

    var fIdx = { N: 0, E: 6, O: 12, A: 18, C: 24 };
    $('listaRasgos').innerHTML = ORDEN.map(function (k) {
      var r = B.RASGOS[k], x = res.rasgos[k], n = nivel(x);
      var etiqueta = x >= 50 ? x + '% ' + r.alto : (100 - x) + '% ' + r.bajo;
      var h = '<div class="rasgo" data-r="' + k + '" style="--c:' + r.color + '"><div class="cab"><b>' + r.emoji + ' ' + r.nombre + '</b><span class="pct">' + etiqueta + '</span></div>' +
        '<div class="doble" role="img" aria-label="' + r.nombre + ': ' + x + ' sobre 100"><div class="fill" data-w="' + x + '"></div><div class="mitad"></div></div>' +
        '<div class="polos"><span>' + r.bajo + '</span><span>' + r.alto + '</span></div>' +
        '<p>' + esc(r[n + '_t']) + '</p><p class="tip">📚 ' + esc(r.estudio[n]) + '</p>' +
        '<p class="libros">Para leer: ' + r.libros.map(function (l) { return '<a href="' + LIBRO + l[0] + '.html">' + esc(l[1]) + '</a>'; }).join(' · ') + '</p>';
      if (res.facetas) {
        var d = k === 'S' ? 'N' : k, base = fIdx[d];
        h += '<div class="facetas">' + (d === 'N' ? '<p style="grid-column:1/-1;margin:0;font-size:.8rem;color:var(--text-dim)">En estas facetas, un número más alto indica más intensidad emocional.</p>' : '') +
          B.FACETAS[d].map(function (nom, j) {
            var fx = res.facetas[base + j];
            return '<div class="faceta"><div class="fc"><span>' + nom + '</span><b>' + fx + '</b></div><div class="fb"><div style="width:' + fx + '%"></div></div><small>' + esc(B.FACETAS_DESC[d][j]) + '</small></div>';
          }).join('') + '</div>';
      }
      return h + '</div>';
    }).join('');

    $('listaFort').innerHTML = P.fort.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('');
    $('listaRetos').innerHTML = P.retos.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('');
    $('txtTrab').textContent = P.trabajo;
    $('listaEstudio').innerHTML = ORDEN.map(function (k) { return '<li><b>' + B.RASGOS[k].corto + ':</b> ' + esc(B.RASGOS[k].estudio[nivel(res.rasgos[k])]) + '</li>'; }).join('');
    $('txtRel').textContent = P.rel;
    $('listaCarreras').innerHTML = P.carreras.map(function (s) { return '<span>' + esc(s) + '</span>'; }).join('');
    selTab('t1');
    document.title = (propio ? 'Mi perfil: ' : 'Perfil ') + P.nombre + ' ' + P.emoji + ' | Test de personalidad AURZANE';
    mostrar('resultados');
    requestAnimationFrame(function () { setTimeout(function () {
      Array.prototype.forEach.call(document.querySelectorAll('.doble .fill'), function (f) { f.style.width = f.dataset.w + '%'; });
    }, 60); });
    if (propio) prepararGuardado();
    if (fiesta) confeti(P.g);
  }
  function selTab(id) {
    ['t1', 't2', 't3', 't4'].forEach(function (t) {
      var b = $(t), on = t === id; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1;
      $(b.getAttribute('aria-controls')).hidden = !on;
    });
  }
  function confeti(g) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var cols = [g[0], g[1], '#ffb347', '#ff7a9c', '#5b7cfa', '#2fb37f'];
    for (var i = 0; i < 70; i++) {
      var c = document.createElement('i'); c.className = 'confeti';
      c.style.left = Math.random() * 100 + 'vw'; c.style.background = cols[i % cols.length];
      c.style.animationDuration = (1.8 + Math.random() * 1.6) + 's'; c.style.animationDelay = Math.random() * .5 + 's';
      c.style.borderRadius = i % 3 ? '2px' : '50%';
      document.body.appendChild(c); setTimeout(function (el) { el.remove(); }, 4200, c);
    }
  }

  /* ---------- Compartir ---------- */
  function urlRes() { return location.origin + BASE + 'p/' + SLUG[actual.perfil] + '/#' + aHash(actual); }
  function compartir() {
    var P = B.PERFILES[actual.perfil];
    var txt = 'Mi perfil de personalidad es ' + P.nombre + ' ' + P.emoji + ': «' + P.lema + '». ¿Y el tuyo?';
    if (navigator.share) { navigator.share({ title: 'Test de personalidad AURZANE', text: txt, url: urlRes() }).catch(function () {}); return; }
    var t = txt + ' ' + urlRes();
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () {
      $('msgCompartir').textContent = 'Enlace copiado. Pégalo donde quieras compartirlo.';
    }, function () { window.prompt('Copia este enlace:', urlRes()); });
  }
  function cargarImg(src) {
    return new Promise(function (ok, ko) { var im = new Image(); im.onload = function () { ok(im); }; im.onerror = ko; im.src = src; });
  }
  function envolver(x, txt, maxW) {
    var pal = txt.split(' '), lineas = [], l = '';
    pal.forEach(function (w) { var t = l ? l + ' ' + w : w; if (x.measureText(t).width > maxW && l) { lineas.push(l); l = w; } else l = t; });
    if (l) lineas.push(l); return lineas;
  }
  function tarjeta() {
    var P = B.PERFILES[actual.perfil], W = 1080, H = 1350, c = document.createElement('canvas');
    c.width = W; c.height = H; var x = c.getContext('2d');
    $('btnImagen').disabled = true;
    Promise.all([cargarImg(imgPerfil(actual.perfil)), document.fonts ? document.fonts.ready : null]).then(function (r) {
      var im = r[0];
      var g = x.createLinearGradient(0, 0, W, H); g.addColorStop(0, P.g[0]); g.addColorStop(1, P.g[1]);
      x.fillStyle = g; x.fillRect(0, 0, W, H);
      var rg = x.createRadialGradient(W * .85, 0, 0, W * .85, 0, W); rg.addColorStop(0, 'rgba(255,255,255,.28)'); rg.addColorStop(1, 'rgba(255,255,255,0)');
      x.fillStyle = rg; x.fillRect(0, 0, W, H);
      x.fillStyle = 'rgba(18,12,44,.55)'; rr(x, 60, 650, W - 120, 640, 40);
      x.save(); x.shadowColor = 'rgba(0,0,0,.35)'; x.shadowBlur = 50; x.shadowOffsetY = 20;
      x.drawImage(im, W / 2 - 190, 60, 380, 380); x.restore();
      x.textAlign = 'center'; x.fillStyle = '#fff';
      x.font = '600 38px "Instrument Sans",sans-serif'; x.fillText('Mi perfil de personalidad es', W / 2, 500);
      x.font = '700 112px "Bodoni Moda",Georgia,serif'; x.fillText(P.nombre, W / 2, 610);
      x.font = '600 36px "Instrument Sans",sans-serif';
      envolver(x, P.lema, W - 220).forEach(function (l, i) { x.fillText(l, W / 2, 718 + i * 44); });
      ORDEN.forEach(function (k, i) {
        var rs = B.RASGOS[k], y = 812 + i * 84, v = actual.rasgos[k];
        x.textAlign = 'left'; x.font = '600 30px "Instrument Sans",sans-serif'; x.fillStyle = '#fff';
        x.fillText(rs.nombre, 120, y);
        x.textAlign = 'right'; x.fillText(String(v), W - 120, y);
        x.fillStyle = 'rgba(255,255,255,.18)'; rr(x, 120, y + 16, W - 240, 22, 11);
        x.fillStyle = rs.color; rr(x, 120, y + 16, Math.max(22, (W - 240) * v / 100), 22, 11);
      });
      x.textAlign = 'center'; x.fillStyle = '#fff'; x.font = '700 32px "Instrument Sans",sans-serif';
      x.fillText('¿Y tú? Haz el test gratis en mind.aurzane.com', W / 2, H - 92);
      var a = document.createElement('a'); a.download = 'mi-perfil-' + SLUG[actual.perfil] + '-aurzane.png';
      a.href = c.toDataURL('image/png'); document.body.appendChild(a); a.click(); a.remove();
    }).catch(function () { $('msgCompartir').textContent = 'No se pudo crear la imagen. Inténtalo de nuevo.'; })
      .then(function () { $('btnImagen').disabled = false; });
  }
  function rr(x, X, Y, w, h, r) { x.beginPath(); x.moveTo(X + r, Y); x.arcTo(X + w, Y, X + w, Y + h, r); x.arcTo(X + w, Y + h, X, Y + h, r); x.arcTo(X, Y + h, X, Y, r); x.arcTo(X, Y, X + w, Y, r); x.fill(); }

  /* ---------- Mi AURZANE (Supabase) ---------- */
  var sbPromesa = null;
  function cargarScript(src) {
    return new Promise(function (ok, ko) { var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
  }
  function cliente() {
    if (window.__big5SbMock) return Promise.resolve(window.__big5SbMock);
    if (!sbPromesa) {
      sbPromesa = (window.supabase ? Promise.resolve() : cargarScript('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js'))
        .then(function () { return window.crearClienteAurzaneID ? null : cargarScript('https://aurzane.com/aurzane-id.js'); })
        .then(function () { return window.crearClienteAurzaneID(SB_URL, SB_KEY); });
    }
    return sbPromesa;
  }
  var sesion = null;
  function prepararGuardado() {
    var btn = $('btnGuardar'); btn.disabled = false; $('gMsg').textContent = '';
    var yaGuardado = ss('aurzane-big5-guardado') === aHash(actual);
    cliente().then(function (sb) { return sb.auth.getSession(); }).then(function (r) {
      sesion = r && r.data ? r.data.session : null;
      if (sesion) {
        $('lnkCuenta').textContent = '👤 Mi AURZANE';
        $('gTit').textContent = '💾 Guarda este resultado en Mi AURZANE';
        $('gTxt').textContent = 'Lo tendrás siempre a mano en tu panel. El equipo de AURZANE podrá verlo para orientarte mejor si lo necesitas.';
        btn.textContent = yaGuardado ? 'Guardado ✓' : 'Guardar en Mi AURZANE';
        btn.disabled = yaGuardado;
        if (!yaGuardado && ss('aurzane-big5-auto') === aHash(actual)) { ss('aurzane-big5-auto', ''); guardar(); }
      } else {
        $('gTit').textContent = '💾 Guarda tu resultado en Mi AURZANE';
        $('gTxt').textContent = 'Inicia sesión o crea tu cuenta gratis y consulta tus resultados cuando quieras, desde cualquier dispositivo.';
        btn.textContent = 'Iniciar sesión y guardar';
      }
    }).catch(function () { sesion = null; btn.textContent = 'Iniciar sesión y guardar'; });
  }
  function guardar() {
    if (!sesion) {
      ss('aurzane-big5-auto', aHash(actual));
      location.href = 'https://aurzane.com/mi-aurzane.html?next=' + encodeURIComponent(urlRes());
      return;
    }
    var btn = $('btnGuardar'); btn.disabled = true; btn.textContent = 'Guardando…';
    cliente().then(function (sb) {
      return sb.from('personalidad_resultados').insert({ version: actual.v, rasgos: actual.rasgos, facetas: actual.facetas, perfil: actual.perfil });
    }).then(function (r) {
      if (r && r.error) throw r.error;
      ss('aurzane-big5-guardado', aHash(actual));
      btn.textContent = 'Guardado ✓';
      $('gMsg').innerHTML = 'Listo. Lo verás en <a href="https://aurzane.com/mi-aurzane.html#personalidad">Mi AURZANE</a>.';
    }).catch(function () {
      btn.disabled = false; btn.textContent = 'Guardar en Mi AURZANE';
      $('gMsg').textContent = 'No se pudo guardar. Revisa tu conexión e inténtalo de nuevo.';
    });
  }

  /* ---------- Arranque ---------- */
  function tema() {
    var osc = document.documentElement.getAttribute('data-tema') === 'oscuro';
    if (osc) document.documentElement.removeAttribute('data-tema'); else document.documentElement.setAttribute('data-tema', 'oscuro');
    try { localStorage.setItem('aurzane-tema', osc ? 'claro' : 'oscuro'); } catch (e) {}
    if (actual && !$('resultados').hidden) radarSVG($('radarRes'), actual.rasgos, { numeros: true, id: 'r' });
  }
  function desdeHash(fiesta) {
    var res = deHash(location.hash);
    if (!res) return false;
    var mio = /[&#]mio=1/.test(location.hash);
    if (mio) { ss('aurzane-big5-guardado', aHash(res)); ss('aurzane-big5-propio', aHash(res)); }
    var propio = mio || ss('aurzane-big5-propio') === aHash(res) || ls('aurzane-big5-ultimo') === aHash(res);
    resultados(res, propio, fiesta && propio);
    return true;
  }
  function init() {
    portada();
    Array.prototype.forEach.call(document.querySelectorAll('[data-version]'), function (b) {
      b.addEventListener('click', function () { empezar(b.dataset.version); });
    });
    $('formTest').addEventListener('change', onRespuesta);
    $('formTest').addEventListener('submit', onSiguiente);
    $('btnAtras').addEventListener('click', function () { if (st.p > 0) { st.p--; guardarProg(); pintarPagina(); window.scrollTo(0, 0); } });
    $('btnSalir').addEventListener('click', function () { mostrar('inicio'); portada(); });
    $('btnRepetir').addEventListener('click', function () { history.replaceState(null, '', location.pathname); mostrar('inicio'); document.title = 'Test de personalidad gratis: descubre tu perfil de los Cinco Grandes | AURZANE MIND'; document.querySelector('.versiones').scrollIntoView(); });
    $('lnkHacerTest').addEventListener('click', function (e) { e.preventDefault(); history.replaceState(null, '', location.pathname); mostrar('inicio'); });
    $('btnCompartir').addEventListener('click', compartir);
    $('btnImagen').addEventListener('click', tarjeta);
    $('btnGuardar').addEventListener('click', guardar);
    $('btnTema').addEventListener('click', tema);
    ['t1', 't2', 't3', 't4'].forEach(function (t, i, arr) {
      $(t).addEventListener('click', function () { selTab(t); });
      $(t).addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!d) return;
        var n = arr[(i + d + arr.length) % arr.length]; selTab(n); $(n).focus();
      });
    });
    window.addEventListener('hashchange', function () { if (!desdeHash(false) && !$('resultados').hidden) mostrar('inicio'); });
    var ult = ls('aurzane-big5-ultimo');
    if (ult && !location.hash) {
      var p = document.createElement('p'); p.style.cssText = 'margin-top:12px;color:#e7e2ff';
      p.innerHTML = '<a href="#' + ult + '" style="color:#ffd27f;font-weight:700">Ver tu último resultado</a>';
      $('avisoContinuar').parentNode.appendChild(p);
    }
    desdeHash(false);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
