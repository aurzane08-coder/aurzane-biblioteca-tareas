/* Biblioteca AURZANE: portada con estanterías, menú de categorías y catálogo con filtros. */
(function(){
  'use strict';
  var B = window.BIBLIOTECA;
  var $ = function(id){ return document.getElementById(id); };
  var esc = function(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
  var norm = function(s){ return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
  var plural = function(n, uno, varios){ return n.toLocaleString('es') + ' ' + (n === 1 ? uno : varios); };
  var POR_PAGINA = 24;

  /* ---------- preparación de datos ---------- */
  var temaPorN = {}; B.temas.forEach(function(t){ temaPorN[t.n] = t; });
  var macroPorId = {}; B.macrotemas.forEach(function(m){ macroPorId[m.id] = m; });
  var macroDeTema = {}; B.macrotemas.forEach(function(m){ m.temas.forEach(function(n){ macroDeTema[n] = m.id; }); });
  var LIC = function(l){ if(!l.licencia) return ''; if(/dominio/i.test(l.licencia)) return 'Dominio público'; var m = l.licencia.match(/CC\s+BY(-[A-Z]+)*(-[A-Z]+)?/i); return m ? m[0].toUpperCase().replace(/\s+/,' ') : 'Otra licencia'; };
  var ANIOS = [['a1', 'Antes de 1950', 0, 1949], ['a2', '1950 a 1999', 1950, 1999], ['a3', '2000 a 2014', 2000, 2014], ['a4', 'Desde 2015', 2015, 9999]];
  var EXT = [['e1', 'Hasta 50 páginas', 0, 50], ['e2', '51 a 150 páginas', 51, 150], ['e3', '151 a 300 páginas', 151, 300], ['e4', 'Más de 300 páginas', 301, 99999]];
  var rango = function(tabla, v){ if(!v) return ''; for(var i = 0; i < tabla.length; i++) if(v >= tabla[i][2] && v <= tabla[i][3]) return tabla[i][0]; return ''; };

  B.libros.forEach(function(l, i){
    l._i = i;
    l._temas = Object.keys(l.temas).map(Number);
    l._macros = l._temas.map(function(n){ return macroDeTema[n]; });
    l._subs = []; l._temas.forEach(function(n){ (l.temas[n] || []).forEach(function(s){ l._subs.push(n + '|' + s); }); });
    l._anio = parseInt(String(l.anio || '').slice(0, 4), 10) || 0;
    l._pag = +l.paginas || 0;
    l._lic = LIC(l);
    l._a = rango(ANIOS, l._anio); l._e = rango(EXT, l._pag);
    l._disp = l.tipo === 'pdf' ? 'aqui' : 'ficha';
    l._tit = norm(l.titulo); l._aut = norm(l.autores);
    l._texto = norm([l.titulo, l.autores, l.resumen, l.editorial || '', l.repo || ''].concat(l._temas.map(function(n){ return temaPorN[n].nombre + ' ' + (l.temas[n] || []).join(' '); })).join(' '));
  });
  var PDFS = B.libros.filter(function(l){ return l.tipo === 'pdf'; });

  /* Lo nuevo deja de serlo solo: la etiqueta y el estante de novedades duran 30 días desde el alta. */
  var DIAS_NUEVO = 30, HOY = Date.now();
  function esNuevo(l){ var t = Date.parse((l.alta || '') + 'T00:00:00'); return !isNaN(t) && HOY - t < DIAS_NUEVO * 864e5 && HOY >= t; }

  /* Colecciones temáticas: lo que se ve en las estanterías de la portada. */
  var COLECCIONES = [
    { id: 'hoy', nombre: 'Títulos que se leen hoy', desc: 'Libros actuales de psicología y crecimiento personal. Te contamos de qué tratan y dónde conseguirlos.', f: function(l){ return !!l.actual; } },
    { id: 'autoestima', nombre: 'Autoestima y superación personal', desc: 'Quererte mejor, poner límites, dejar de exigirte tanto y volver a empezar.', t: [38] },
    { id: 'relatos', nombre: 'Relatos de vida', desc: 'Historias, memorias y cuentos que enseñan psicología sin decirlo.', t: [39] },
    { id: 'duelo', nombre: 'Duelo y pérdidas', desc: 'Para atravesar una pérdida y para acompañar a quien la vive.', t: [37] },
    { id: 'emociones', nombre: 'Emociones', desc: 'Entender lo que sientes y aprender a regularlo.', t: [3] },
    { id: 'resiliencia', nombre: 'Resiliencia y trauma', desc: 'Adversidad, trauma y la manera en que las personas se recuperan.', t: [22] },
    { id: 'calma', nombre: 'Mindfulness y calma', desc: 'Atención plena, meditación y autocompasión.', t: [23] },
    { id: 'bienestar', nombre: 'Ansiedad, estrés y bienestar', desc: 'Dormir mejor, bajar el estrés y cuidar tu salud mental.', t: [13] },
    { id: 'familia', nombre: 'Familia y crianza', desc: 'Infancia, crianza, límites y vínculos en casa.', t: [14] },
    { id: 'relaciones', nombre: 'Relaciones y pareja', desc: 'Vínculos, pareja, amistad e influencia.', t: [11, 25, 34] },
    { id: 'sentido', nombre: 'Sentido de la vida y filosofía', desc: 'Propósito, valores y los clásicos que pensaron cómo vivir.', t: [24, 36, 41] },
    { id: 'mente', nombre: 'Mente y cerebro', desc: 'Cómo pensamos, recordamos y percibimos.', t: [1, 2, 19, 40, 47] },
    { id: 'clinica', nombre: 'Psicología clínica y terapia', desc: 'Trastornos, evaluación y tratamientos psicológicos.', t: [8, 9] },
    { id: 'aprender', nombre: 'Aprender y estudiar', desc: 'Educación, técnicas de estudio y orientación vocacional.', t: [12, 31] },
    { id: 'vejez', nombre: 'Envejecer bien', desc: 'Memoria, cuidados y calidad de vida en la vejez.', t: [48] }
  ];
  var colPorId = {}; COLECCIONES.forEach(function(c){ colPorId[c.id] = c; });
  function enCol(l, c){ c = colPorId[c] || c; if(!c) return false; if(c.f) return c.f(l); for(var i = 0; i < c.t.length; i++) if(l._temas.indexOf(c.t[i]) !== -1) return true; return false; }

  /* ---------- estado en la URL ---------- */
  var estado;
  function vacio(){ return { v: '', c: '', m: '', t: 0, s: '', q: '', r: [], l: [], a: [], e: [], d: '', o: 'rel', p: 1, vista: 'grid' }; }
  function leerHash(){
    estado = vacio();
    var p = new URLSearchParams(location.hash.slice(1));
    estado.v = p.get('v') || ''; estado.c = colPorId[p.get('c')] ? p.get('c') : ''; estado.m = p.get('m') || ''; estado.t = +(p.get('t') || 0); estado.s = p.get('s') || ''; estado.q = p.get('q') || '';
    ['r', 'l', 'a', 'e'].forEach(function(k){ estado[k] = p.get(k) ? p.get(k).split('~') : []; });
    estado.d = p.get('d') || ''; estado.o = p.get('o') || 'rel'; estado.p = +(p.get('p') || 1); estado.vista = p.get('vista') || leerPref() || 'grid';
    if(p.get('pdf') === '1') estado.d = 'aqui';
    if(estado.t && !estado.m) estado.m = macroDeTema[estado.t] || '';
  }
  function hashDe(e){
    var p = new URLSearchParams();
    if(e.c) p.set('c', e.c); if(e.m) p.set('m', e.m); if(e.t) p.set('t', e.t); if(e.s) p.set('s', e.s); if(e.q) p.set('q', e.q);
    ['r', 'l', 'a', 'e'].forEach(function(k){ if(e[k].length) p.set(k, e[k].join('~')); });
    if(e.d) p.set('d', e.d); if(e.o && e.o !== 'rel') p.set('o', e.o); if(e.p > 1) p.set('p', e.p);
    if(!p.toString() && e.v) p.set('v', e.v);
    return p.toString();
  }
  function escribirHash(){ var h = hashDe(estado); history.replaceState(null, '', h ? '#' + h : location.pathname); }
  function hayFiltros(e){ e = e || estado; return !!(e.v || e.c || e.m || e.t || e.q || e.r.length || e.l.length || e.a.length || e.e.length || e.d); }
  function leerPref(){ try{ return localStorage.getItem('bib-vista'); }catch(_){ return null; } }
  function guardarPref(v){ try{ localStorage.setItem('bib-vista', v); }catch(_){} }

  /* ---------- filtrado ---------- */
  function pasa(l, e, ignorar){
    var q = norm(e.q).split(/\s+/).filter(Boolean);
    if(ignorar !== 'd' && e.d && l._disp !== e.d) return false;
    if(ignorar !== 'c' && e.c && !enCol(l, e.c)) return false;
    if(ignorar !== 'm' && e.m && l._macros.indexOf(e.m) === -1) return false;
    if(ignorar !== 't' && e.t && l._temas.indexOf(e.t) === -1) return false;
    if(ignorar !== 's' && e.s && l._subs.indexOf(e.t + '|' + e.s) === -1) return false;
    if(ignorar !== 'r' && e.r.length && e.r.indexOf(l.repo) === -1) return false;
    if(ignorar !== 'l' && e.l.length && e.l.indexOf(l._lic) === -1) return false;
    if(ignorar !== 'a' && e.a.length && e.a.indexOf(l._a) === -1) return false;
    if(ignorar !== 'e' && e.e.length && e.e.indexOf(l._e) === -1) return false;
    for(var i = 0; i < q.length; i++) if(l._texto.indexOf(q[i]) === -1) return false;
    return true;
  }
  function puntos(l, q){
    var s = 0; q.forEach(function(w){ if(l._tit.indexOf(w) !== -1) s += 6; if(l._aut.indexOf(w) !== -1) s += 3; });
    return s;
  }
  function ordenar(lista, e){
    var q = norm(e.q).split(/\s+/).filter(Boolean);
    var cmpT = function(a, b){ return a.titulo.localeCompare(b.titulo, 'es'); };
    var f = {
      rel: function(a, b){ if(!e.c && a.tipo !== b.tipo) return a.tipo === 'pdf' ? -1 : 1; if(q.length){ var d = puntos(b, q) - puntos(a, q); if(d) return d; } if(e.t){ var sa = (a.temas[e.t] || []).length, sb = (b.temas[e.t] || []).length; if(sa !== sb) return sb - sa; } var pa = a.principal === e.t ? 1 : 0, pb = b.principal === e.t ? 1 : 0; if(pa !== pb) return pb - pa; return cmpT(a, b); },
      nuevo: function(a, b){ return String(b.alta || '').localeCompare(String(a.alta || '')) || (b._anio - a._anio) || cmpT(a, b); },
      az: cmpT, za: function(a, b){ return cmpT(b, a); },
      reciente: function(a, b){ return (b._anio - a._anio) || cmpT(a, b); },
      antiguo: function(a, b){ return ((a._anio || 9999) - (b._anio || 9999)) || cmpT(a, b); },
      largo: function(a, b){ return (b._pag - a._pag) || cmpT(a, b); },
      corto: function(a, b){ return ((a._pag || 99999) - (b._pag || 99999)) || cmpT(a, b); }
    }[e.o] || cmpT;
    return lista.slice().sort(f);
  }
  function filtrar(e, ignorar){ return B.libros.filter(function(l){ return pasa(l, e, ignorar); }); }

  /* ---------- piezas ---------- */
  function portada(l){
    var img = l.portada ? '<img src="' + esc(l.portada) + '" alt="" loading="lazy" onerror="this.remove()">' : '';
    return '<div class="portada tipo m-' + (macroDeTema[l.principal] || 'x') + '"><span class="lomo"></span><span class="pt-tit">' + esc(l.titulo) + '</span><span class="pt-aut">' + esc(l.autores) + '</span>' + img + '</div>';
  }
  function temaVisible(l, e){ return temaPorN[e && e.t && l.temas[e.t] ? e.t : (l.principal || l._temas[0])]; }
  function enlace(l){ return 'libro/' + encodeURIComponent(l.id) + '.html'; }
  function tarjeta(l, e){
    var t = temaVisible(l, e);
    return '<a class="libro" href="' + enlace(l) + '">' + portada(l) +
      '<span class="l-tit">' + esc(l.titulo) + '</span><span class="l-aut">' + esc(l.autores) + '</span>' +
      '<span class="l-meta">' + (esNuevo(l) ? '<span class="chip nuevo">Nuevo</span>' : '') + (l.tipo === 'pdf' ? '<span class="chip leer">Leer aquí</span>' : '<span class="chip ficha">Ficha</span>') +
      (t ? '<span class="chip">' + esc(t.nombre) + '</span>' : '') + '</span></a>';
  }
  function fila(l, e){
    var t = temaVisible(l, e);
    var meta = [l.repo, l._anio || '', l._pag ? l._pag + ' páginas' : '', l._lic].filter(Boolean).map(esc).join('<span class="sep" aria-hidden="true">/</span>');
    var res = String(l.resumen || '').replace(/^\s*\[[a-z]{2}\]\s*/i, ''); if(norm(res).indexOf(norm(l.titulo).slice(0, 30)) === 0) res = '';
    if(res.length > 260) res = res.slice(0, 250).replace(/\s+\S*$/, '') + '…';
    return '<a class="libro fila" href="' + enlace(l) + '">' + portada(l) + '<div class="f-txt">' +
      '<span class="l-tit">' + esc(l.titulo) + '</span><span class="l-aut">' + esc(l.autores) + '</span>' +
      (res ? '<p class="f-res">' + esc(res) + '</p>' : '') +
      '<p class="f-meta">' + meta + '</p>' +
      '<span class="l-meta">' + (esNuevo(l) ? '<span class="chip nuevo">Nuevo</span>' : '') + (l.tipo === 'pdf' ? '<span class="chip leer">Leer aquí</span>' : '<span class="chip ficha">Ficha</span>') + (t ? '<span class="chip">' + esc(t.nombre) + '</span>' : '') + '</span>' +
      '</div></a>';
  }
  function irA(cambios){ var e = vacio(); for(var k in cambios) e[k] = cambios[k]; return '#' + (hashDe(e) || 'v=todo'); }

  /* ---------- cabecera: departamentos y menú ---------- */
  function cuentaMacro(id){ return B.libros.filter(function(l){ return l._macros.indexOf(id) !== -1; }).length; }
  function cuentaTema(n){ return B.libros.filter(function(l){ return l._temas.indexOf(n) !== -1; }).length; }
  function pintarDeptos(){
    var html = '<a class="depto todo" href="#v=todo" data-depto="">Todo</a>';
    B.macrotemas.forEach(function(m){ html += '<button type="button" class="depto" data-depto="' + m.id + '" aria-expanded="false">' + esc(m.nombre) + '</button>'; });
    $('deptos').innerHTML = html;
  }
  function pintarMega(id){
    var m = macroPorId[id]; if(!m) return;
    var temas = m.temas.map(function(n){
      var t = temaPorN[n], c = cuentaTema(n);
      var subs = t.subtemas.map(function(s){ return [s, B.libros.filter(function(l){ return l._subs.indexOf(n + '|' + s) !== -1; }).length]; })
        .filter(function(x){ return x[1]; }).sort(function(a, b){ return b[1] - a[1]; }).slice(0, 6);
      return '<div class="mega-col"><a class="mega-tema" href="' + irA({ m: id, t: n }) + '">' + esc(t.nombre) + ' <span>' + c + '</span></a>' +
        subs.map(function(x){ return '<a class="mega-sub" href="' + irA({ m: id, t: n, s: x[0] }) + '">' + esc(x[0]) + '</a>'; }).join('') + '</div>';
    }).join('');
    $('mega').innerHTML = '<div class="wrap mega-in"><div class="mega-cab"><a class="mega-macro" href="' + irA({ m: id }) + '">' + esc(m.nombre) + '</a><p>' + esc(m.descripcion) + '</p><a class="btn sec peq" href="' + irA({ m: id }) + '">Ver los ' + cuentaMacro(id) + ' libros</a></div><div class="mega-cols">' + temas + '</div></div>';
  }
  var megaAbierto = '';
  function abrirMega(id){
    megaAbierto = id; pintarMega(id); $('mega').hidden = false;
    document.querySelectorAll('.depto[data-depto]').forEach(function(b){ if(b.tagName === 'BUTTON') b.setAttribute('aria-expanded', b.dataset.depto === id ? 'true' : 'false'); });
  }
  function cerrarMega(){ megaAbierto = ''; $('mega').hidden = true; document.querySelectorAll('button.depto').forEach(function(b){ b.setAttribute('aria-expanded', 'false'); }); }

  /* ---------- portada de la biblioteca ---------- */
  function estante(titulo, desc, libros, verHref, verTxt){
    if(!libros.length) return '';
    return '<section class="estante wrap"><div class="est-cab"><div><h2>' + esc(titulo) + '</h2>' + (desc ? '<p>' + esc(desc) + '</p>' : '') + '</div>' +
      (verHref ? '<a class="ver-todo" href="' + verHref + '">' + esc(verTxt) + '</a>' : '') + '</div>' +
      '<div class="est-fila"><button type="button" class="est-flecha izq" aria-label="Anteriores">‹</button><div class="est-libros">' +
      libros.map(function(l){ return tarjeta(l); }).join('') + '</div><button type="button" class="est-flecha der" aria-label="Siguientes">›</button></div></section>';
  }
  function mezclar(lista, semilla){ var a = lista.slice(), s = semilla || 7; for(var i = a.length - 1; i > 0; i--){ s = (s * 9301 + 49297) % 233280; var j = Math.floor(s / 233280 * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function pintarInicio(){
    var nTemas = B.temas.filter(function(t){ return cuentaTema(t.n); }).length;
    $('cifras').innerHTML = plural(PDFS.length, 'libro para leer aquí', 'libros para leer aquí') + ' y ' + plural(B.libros.length - PDFS.length, 'ficha', 'fichas') + ' de libros actuales, en ' + nTemas + ' temas. Gratis y sin registro.';
    $('tipos').innerHTML = COLECCIONES.filter(function(c){ return B.libros.some(function(l){ return enCol(l, c); }); }).slice(0, 8)
      .map(function(c){ return '<a class="tipo-c" href="' + irA({ c: c.id }) + '">' + esc(c.nombre) + '</a>'; }).join('');
    var conPortada = PDFS.filter(function(l){ return l.portada && l.portada_ok !== false; });
    $('abanico').innerHTML = mezclar(conPortada, 11).slice(0, 5).map(function(l, i){ return '<a class="ab-libro ab' + i + '" href="' + enlace(l) + '" tabindex="-1">' + portada(l) + '</a>'; }).join('');

    var html = '';
    var nuevos = B.libros.filter(esNuevo);
    if(nuevos.length >= 4) html += estante('Novedades', 'Lo que entró en la biblioteca en los últimos 30 días.', mezclar(nuevos, 3).slice(0, 18), irA({ o: 'nuevo', v: 'todo' }), 'Ver todas las novedades');
    var semana = Math.floor(HOY / (7 * 864e5));
    COLECCIONES.forEach(function(c, i){
      var libros = B.libros.filter(function(l){ return enCol(l, c); });
      if(libros.length < 4) return;
      // primero los que tienen portada; el orden cambia cada semana para que la portada no se vea siempre igual
      var con = libros.filter(function(l){ return l.portada; }), sin = libros.filter(function(l){ return !l.portada; });
      html += estante(c.nombre, c.desc, mezclar(con, semana + 17 + i).concat(sin).slice(0, 16), irA({ c: c.id }), 'Ver todo');
    });
    $('estantes').innerHTML = html;

    $('mapa-temas').innerHTML = B.macrotemas.map(function(m){
      return '<div class="mt-grupo"><a class="mt-macro" href="' + irA({ m: m.id }) + '">' + esc(m.nombre) + '</a><ul>' +
        m.temas.map(function(n){ var c = cuentaTema(n); return '<li><a href="' + irA({ m: m.id, t: n }) + '"' + (c ? '' : ' class="sin"') + '>' + esc(temaPorN[n].nombre) + '</a></li>'; }).join('') + '</ul></div>';
    }).join('');
  }

  /* ---------- facetas ---------- */
  function grupo(id, titulo, opciones, abierto, extra){
    var visibles = opciones.filter(function(o){ return o.n || o.sel; });
    if(!visibles.length) return '';
    var muchas = visibles.length > 10;
    return '<details class="fac" ' + (abierto ? 'open' : '') + ' data-fac="' + id + '"><summary>' + esc(titulo) + '</summary>' + (extra || '') +
      (muchas ? '<input class="fac-busca" type="search" placeholder="Filtrar ' + esc(titulo.toLowerCase()) + '" data-filtra="' + id + '">' : '') +
      '<ul class="fac-op' + (muchas ? ' larga' : '') + '">' + visibles.map(function(o){
        return '<li><button type="button" class="op' + (o.sel ? ' sel' : '') + (o.multi ? ' multi' : '') + '" data-k="' + id + '" data-val="' + esc(o.val) + '" aria-pressed="' + !!o.sel + '"><span class="op-n">' + esc(o.txt) + '</span><span class="op-c">' + o.n + '</span></button></li>';
      }).join('') + '</ul></details>';
  }
  function cuentaPor(base, clave){ var c = {}; base.forEach(function(l){ [].concat(l[clave]).forEach(function(v){ if(v) c[v] = (c[v] || 0) + 1; }); }); return c; }
  function pintarFacetas(){
    var e = estado, html = '';
    var bD = filtrar(e, 'd'), cD = cuentaPor(bD, '_disp');
    html += grupo('d', 'Disponibilidad', [{ val: 'aqui', txt: 'Para leer aquí', n: cD.aqui || 0, sel: e.d === 'aqui' }, { val: 'ficha', txt: 'Fichas de referencia', n: cD.ficha || 0, sel: e.d === 'ficha' }], true);
    var bM = filtrar(Object.assign({}, e, { t: 0, s: '' }), 'm'), cM = cuentaPor(bM, '_macros');
    html += grupo('m', 'Categoría', B.macrotemas.map(function(m){ return { val: m.id, txt: m.nombre, n: cM[m.id] || 0, sel: e.m === m.id }; }), !e.t);
    var bT = filtrar(Object.assign({}, e, { s: '' }), 't'), cT = cuentaPor(bT, '_temas');
    var temas = (e.m ? macroPorId[e.m].temas : B.temas.map(function(t){ return t.n; }));
    html += grupo('t', e.m ? 'Tema' : 'Tema (todos)', temas.map(function(n){ return { val: n, txt: temaPorN[n].nombre, n: cT[n] || 0, sel: e.t === n }; }).sort(function(a, b){ return b.sel - a.sel || b.n - a.n; }), true);
    if(e.t){
      var bS = filtrar(e, 's'), cS = {}; bS.forEach(function(l){ (l.temas[e.t] || []).forEach(function(s){ cS[s] = (cS[s] || 0) + 1; }); });
      var t = temaPorN[e.t];
      var vacios = t.subtemas.filter(function(s){ return !cS[s]; }).length;
      html += grupo('s', 'Subtema', t.subtemas.map(function(s){ return { val: s, txt: s, n: cS[s] || 0, sel: e.s === s }; }).sort(function(a, b){ return b.sel - a.sel || b.n - a.n || a.txt.localeCompare(b.txt, 'es'); }), true,
        vacios ? '<p class="fac-nota">' + plural(t.subtemas.length - vacios, 'subtema tiene', 'subtemas tienen') + ' libros; los otros ' + vacios + ' se irán llenando.</p>' : '');
    }
    var bR = filtrar(e, 'r'), cR = cuentaPor(bR, 'repo');
    html += grupo('r', 'Procedencia', Object.keys(cuentaPor(PDFS, 'repo')).map(function(r){ return { val: r, txt: r, n: cR[r] || 0, sel: e.r.indexOf(r) !== -1, multi: true }; }).sort(function(a, b){ return b.n - a.n; }), e.r.length > 0);
    var bL = filtrar(e, 'l'), cL = cuentaPor(bL, '_lic');
    html += grupo('l', 'Licencia', Object.keys(cuentaPor(PDFS, '_lic')).map(function(r){ return { val: r, txt: r, n: cL[r] || 0, sel: e.l.indexOf(r) !== -1, multi: true }; }).sort(function(a, b){ return b.n - a.n; }), e.l.length > 0);
    var bA = filtrar(e, 'a'), cA = cuentaPor(bA, '_a');
    html += grupo('a', 'Año de publicación', ANIOS.map(function(x){ return { val: x[0], txt: x[1], n: cA[x[0]] || 0, sel: e.a.indexOf(x[0]) !== -1, multi: true }; }), e.a.length > 0);
    var bE = filtrar(e, 'e'), cE = cuentaPor(bE, '_e');
    html += grupo('e', 'Extensión', EXT.map(function(x){ return { val: x[0], txt: x[1], n: cE[x[0]] || 0, sel: e.e.indexOf(x[0]) !== -1, multi: true }; }), e.e.length > 0);
    $('facetas-cont').innerHTML = html;
  }
  function etiqueta(k, v){
    if(k === 'm') return macroPorId[v] ? macroPorId[v].nombre : v;
    if(k === 't') return temaPorN[v] ? temaPorN[v].nombre : v;
    if(k === 'd') return v === 'aqui' ? 'Para leer aquí' : 'Fichas de referencia';
    if(k === 'a') return (ANIOS.filter(function(x){ return x[0] === v; })[0] || [0, v])[1];
    if(k === 'e') return (EXT.filter(function(x){ return x[0] === v; })[0] || [0, v])[1];
    if(k === 'q') return 'Búsqueda: «' + v + '»';
    if(k === 'c') return colPorId[v] ? colPorId[v].nombre : v;
    return v;
  }
  function pintarActivos(){
    var e = estado, ch = [];
    if(e.q) ch.push(['q', e.q]); if(e.c) ch.push(['c', e.c]); if(e.d) ch.push(['d', e.d]); if(e.m) ch.push(['m', e.m]); if(e.t) ch.push(['t', e.t]); if(e.s) ch.push(['s', e.s]);
    ['r', 'l', 'a', 'e'].forEach(function(k){ e[k].forEach(function(v){ ch.push([k, v]); }); });
    $('activos').innerHTML = ch.length ? ch.map(function(c){ return '<button type="button" class="activo" data-quitar="' + c[0] + '" data-val="' + esc(c[1]) + '">' + esc(etiqueta(c[0], c[1])) + '<span aria-hidden="true">×</span><span class="vh">Quitar filtro</span></button>'; }).join('') +
      (ch.length > 1 ? '<button type="button" class="limpiar" id="limpiar">Quitar todos</button>' : '') : '';
  }

  /* ---------- resultados ---------- */
  function pintarResultados(){
    var e = estado, m = macroPorId[e.m], col = colPorId[e.c];
    var lista = ordenar(filtrar(e), e);
    var titulo = e.s ? e.s : e.t ? temaPorN[e.t].nombre : m ? m.nombre : col ? col.nombre : e.q ? 'Resultados para «' + e.q + '»' : e.r.length === 1 ? e.r[0] : e.o === 'nuevo' ? 'Novedades' : 'Todo el catálogo';
    $('res-titulo').textContent = titulo;
    document.title = titulo + ' | Biblioteca AURZANE';
    var nPdf = lista.filter(function(l){ return l.tipo === 'pdf'; }).length;
    $('res-desc').textContent = (lista.length ? (!nPdf ? plural(lista.length, 'ficha de referencia', 'fichas de referencia') : plural(lista.length, 'libro', 'libros') + (lista.length - nPdf ? ' (' + nPdf + ' para leer aquí y ' + plural(lista.length - nPdf, 'ficha', 'fichas') + ')' : ', todos para leer aquí')) + '.' : '') + (m && !e.t ? ' ' + m.descripcion : col && !m ? ' ' + col.desc : '');
    var miga = '<a href="https://aurzane.com/">Inicio</a><span class="sep">/</span><a href="#">Biblioteca</a>';
    if(m) miga += '<span class="sep">/</span>' + (e.t ? '<a href="' + irA({ m: e.m }) + '">' + esc(m.nombre) + '</a>' : '<span class="current">' + esc(m.nombre) + '</span>');
    if(e.t) miga += '<span class="sep">/</span>' + (e.s ? '<a href="' + irA({ m: e.m, t: e.t }) + '">' + esc(temaPorN[e.t].nombre) + '</a><span class="sep">/</span><span class="current">' + esc(e.s) + '</span>' : '<span class="current">' + esc(temaPorN[e.t].nombre) + '</span>');
    if(!m) miga += '<span class="sep">/</span><span class="current">' + esc(titulo) + '</span>';
    $('miga').innerHTML = miga;
    var hasta = Math.min(lista.length, e.p * POR_PAGINA);
    $('grid').className = e.vista === 'lista' ? 'lista' : 'grid';
    $('grid').innerHTML = lista.slice(0, hasta).map(function(l){ return e.vista === 'lista' ? fila(l, e) : tarjeta(l, e); }).join('');
    $('vacio').hidden = lista.length > 0;
    $('mas').hidden = hasta >= lista.length;
    $('mas-info').textContent = lista.length ? 'Mostrando ' + hasta + ' de ' + lista.length : '';
    $('orden').value = e.o;
    document.querySelectorAll('.vista-tog button').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.v === e.vista ? 'true' : 'false'); });
  }

  /* ---------- ciclo ---------- */
  function pintar(){
    var res = hayFiltros();
    $('vista-inicio').hidden = res; $('vista-res').hidden = !res;
    document.querySelectorAll('.depto').forEach(function(b){ b.classList.toggle('actual', !!b.dataset.depto && b.dataset.depto === estado.m); });
    if(res){ pintarFacetas(); pintarActivos(); pintarResultados(); } else document.title = 'Biblioteca | AURZANE';
    escribirHash();
  }
  function cambiar(fn, arriba){ fn(estado); estado.p = 1; pintar(); if(arriba) window.scrollTo({ top: 0, behavior: 'smooth' }); }

  /* eventos */
  $('busca').addEventListener('submit', function(ev){ ev.preventDefault(); var v = $('q').value.trim(); cambiar(function(e){ e.q = v; e.v = v ? '' : 'todo'; }, true); $('q').blur(); });
  var tq; $('q').addEventListener('input', function(){ var v = this.value.trim(); clearTimeout(tq); if(!hayFiltros() && !v) return; tq = setTimeout(function(){ cambiar(function(e){ e.q = v; if(!v && !hayFiltros(e)) e.v = 'todo'; }); }, 220); });
  $('deptos').addEventListener('click', function(ev){
    var b = ev.target.closest('button.depto'); if(!b) return;
    if(megaAbierto === b.dataset.depto && !window.matchMedia('(hover:hover)').matches) cerrarMega(); else abrirMega(b.dataset.depto);
  });
  $('deptos').addEventListener('mouseover', function(ev){ var b = ev.target.closest('button.depto'); if(b && window.matchMedia('(hover:hover)').matches) abrirMega(b.dataset.depto); });
  document.querySelector('.cabecera').addEventListener('mouseleave', function(){ if(window.matchMedia('(hover:hover)').matches) cerrarMega(); });
  $('mega').addEventListener('click', function(ev){ if(ev.target.closest('a')) cerrarMega(); });
  document.addEventListener('keydown', function(ev){ if(ev.key === 'Escape'){ cerrarMega(); cerrarFiltros(); } });
  document.addEventListener('click', function(ev){ if(!ev.target.closest('.cabecera')) cerrarMega(); });

  $('facetas-cont').addEventListener('click', function(ev){
    var b = ev.target.closest('.op'); if(!b) return;
    var k = b.dataset.k, v = b.dataset.val;
    cambiar(function(e){
      if(k === 'm'){ e.m = e.m === v ? '' : v; e.t = 0; e.s = ''; }
      else if(k === 't'){ v = +v; if(e.t === v){ e.t = 0; e.s = ''; } else { e.t = v; e.s = ''; e.m = macroDeTema[v]; } }
      else if(k === 's'){ e.s = e.s === v ? '' : v; }
      else if(k === 'd'){ e.d = e.d === v ? '' : v; }
      else { var i = e[k].indexOf(v); if(i === -1) e[k].push(v); else e[k].splice(i, 1); }
      if(!hayFiltros(e)) e.v = 'todo';
    });
  });
  $('facetas-cont').addEventListener('input', function(ev){
    var inp = ev.target.closest('[data-filtra]'); if(!inp) return;
    var q = norm(inp.value);
    inp.parentNode.querySelectorAll('.op').forEach(function(b){ b.parentNode.hidden = q && norm(b.textContent).indexOf(q) === -1; });
  });
  $('activos').addEventListener('click', function(ev){
    if(ev.target.closest('#limpiar')){ cambiar(function(e){ var o = e.o, vi = e.vista; estado = vacio(); estado.v = 'todo'; estado.o = o; estado.vista = vi; }); return; }
    var b = ev.target.closest('[data-quitar]'); if(!b) return;
    var k = b.dataset.quitar, v = b.dataset.val;
    cambiar(function(e){
      if(k === 'q'){ e.q = ''; $('q').value = ''; } else if(k === 'm'){ e.m = ''; e.t = 0; e.s = ''; } else if(k === 't'){ e.t = 0; e.s = ''; } else if(k === 's') e.s = ''; else if(k === 'd') e.d = ''; else if(k === 'c') e.c = '';
      else e[k] = e[k].filter(function(x){ return x !== v; });
      if(!hayFiltros(e)) e.v = 'todo';
    });
  });
  $('limpiar-vacio').addEventListener('click', function(){ $('q').value = ''; cambiar(function(){ var vi = estado.vista; estado = vacio(); estado.v = 'todo'; estado.vista = vi; }, true); });
  $('orden').addEventListener('change', function(){ var v = this.value; cambiar(function(e){ e.o = v; }); });
  document.querySelector('.vista-tog').addEventListener('click', function(ev){ var b = ev.target.closest('[data-v]'); if(!b) return; estado.vista = b.dataset.v; guardarPref(estado.vista); pintarResultados(); });
  $('mas').addEventListener('click', function(){ estado.p += 1; pintarResultados(); escribirHash(); });

  function abrirFiltros(){ $('facetas').classList.add('abierto'); document.body.classList.add('sin-scroll'); }
  function cerrarFiltros(){ $('facetas').classList.remove('abierto'); document.body.classList.remove('sin-scroll'); }
  $('abrir-filtros').addEventListener('click', abrirFiltros);
  $('cerrar-filtros').addEventListener('click', cerrarFiltros);
  $('ver-res').addEventListener('click', cerrarFiltros);

  document.addEventListener('click', function(ev){
    var f = ev.target.closest('.est-flecha'); if(!f) return;
    var cont = f.parentNode.querySelector('.est-libros');
    cont.scrollBy({ left: (f.classList.contains('der') ? 1 : -1) * cont.clientWidth * 0.85, behavior: 'smooth' });
  });

  window.addEventListener('hashchange', function(){ leerHash(); $('q').value = estado.q; pintar(); if(hayFiltros()) window.scrollTo(0, 0); });

  pintarDeptos();
  pintarInicio();
  leerHash();
  $('q').value = estado.q;
  pintar();
})();
