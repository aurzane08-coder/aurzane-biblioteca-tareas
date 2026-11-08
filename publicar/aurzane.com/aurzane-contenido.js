/* AURZANE · contenido vivo que prepara AURZANE AI. Lo carga aurzane-paleta.js.
   1) Artículos: en la portada de cada mundo muestra sus artículos más recientes y en aurzane.com/articulos/ los añade a su mundo.
      Los datos salen de aurzane.com/articulos/ai.js (los publica la IA cuando la revisión les da 8 o más).
   2) Tests: bajo la cabecera de cada test explica qué te llevas al hacerlo (el «enganche»). */
(function (d, w) {
  if (w.__azContenido) return; w.__azContenido = 1;
  var host = location.hostname, ruta = location.pathname;
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var MUNDO = { 'mind.aurzane.com': 'mind', 'live.aurzane.com': 'live', 'learn.aurzane.com': 'learn', 'nexus.aurzane.com': 'nexus', 'build.aurzane.com': 'build' }[host];
  var NOMBRE = { mind: 'MIND', live: 'LIVE', learn: 'LEARN', nexus: 'NEXUS', build: 'BUILD' };

  /* ---------- 2) enganche de los tests ---------- */
  var ENG = {
    'test-de-ansiedad': ['Sabrás si tus nervios están en un nivel esperable o conviene atenderlos', 'Ideas concretas para bajar la ansiedad desde hoy', 'Cuándo merece la pena pedir ayuda profesional'],
    'test-de-depresion': ['Una foto clara de cómo está tu ánimo estas dos semanas', 'Qué significa tu puntuación sin etiquetas', 'Pasos pequeños para sentirte mejor y cuándo consultar'],
    'test-de-autoestima': ['Cómo te valoras de verdad, más allá del día a día', 'Qué fortalece y qué debilita tu autoestima', 'Ejercicios sencillos para tratarte mejor'],
    'test-de-autocompasion': ['Si te hablas con dureza o con amabilidad cuando fallas', 'Por qué la autocompasión protege del estrés', 'Una práctica breve para empezar hoy'],
    'test-de-autoeficacia': ['Cuánto confías en tu capacidad para resolver problemas', 'Cómo influye esa confianza en tus metas', 'Ideas para reforzarla paso a paso'],
    'test-de-burnout': ['Si el cansancio del trabajo o los estudios se está volviendo desgaste', 'Qué parte te pesa más: agotamiento, distancia o eficacia', 'Cambios realistas para recuperar energía'],
    'test-de-estres': ['Cuánto estrés llevas encima este último mes', 'Cómo se compara con la mayoría de personas', 'Técnicas rápidas para soltar tensión'],
    'test-de-resiliencia': ['Cuánto tardas en recuperarte de los golpes', 'Qué recursos ya tienes a tu favor', 'Cómo entrenar la resiliencia como un músculo'],
    'test-de-satisfaccion-con-la-vida': ['Cómo valoras tu vida en conjunto', 'Qué áreas tiran hacia arriba y cuáles hacia abajo', 'Ideas para dar pasos hacia lo que te importa'],
    'test-de-soledad': ['Si te sientes solo o sola aunque tengas gente cerca', 'Por qué la soledad no depende de cuántas personas te rodean', 'Formas sencillas de reconectar'],
    'test-de-tdah': ['Si tu forma de concentrarte encaja con lo que se ve en el TDAH adulto', 'Qué hacer con el resultado, sin autodiagnosticarte', 'Trucos de organización que ayudan a cualquiera'],
    'test-de-bienestar': ['Cómo has estado de verdad estas dos semanas', 'Una puntuación fácil de seguir con el tiempo', 'Ideas para cuidarte esta semana'],
    'test-de-habitos': ['Una nota a tu estilo de vida: sueño, comida, ejercicio y más', 'Qué hábito te dará más beneficio si lo cambias', 'Consejos adaptados a tus respuestas'],
    'test-de-sueno': ['Si duermes lo que tu cuerpo necesita', 'Qué está robándote descanso', 'Un plan de 7 días para dormir mejor']
  };
  function enganche() {
    var slug = ruta.split('/').filter(Boolean)[0]; var e = ENG[slug];
    if (!e || d.getElementById('azEng')) return;
    var chips = d.querySelector('.hero ul.chips'); if (!chips) return;
    var c = d.createElement('div'); c.id = 'azEng';
    c.style.cssText = 'margin:18px 0 0;padding:14px 18px;border-radius:14px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);max-width:640px';
    c.innerHTML = '<p style="margin:0 0 6px;font-weight:700">Qué te llevas al hacerlo</p><ul style="margin:0;padding-left:20px;line-height:1.55">' +
      e.map(function (x) { return '<li>' + E(x) + '</li>'; }).join('') + '<li>Al terminar puedes preguntarle a la IA de AURZANE sobre tu resultado</li></ul>';
    chips.parentNode.insertBefore(c, chips.nextSibling);
  }

  /* ---------- 1) artículos ---------- */
  function tarjeta(a, estilo) {
    var url = 'https://aurzane.com/articulos/' + encodeURIComponent(a.slug) + '/';
    if (estilo === 'indice') return '<a class="tema-card" href="' + url + '">' + (a.imagen ? '<img src="' + E(a.imagen) + '" alt="" loading="lazy">' : '') +
      '<div class="tema-card-body"><span class="cat">' + E(NOMBRE[a.mundo]) + ' · ' + E(a.categoria || 'Divulgación') + '</span><h3>' + E(a.titulo) + '</h3><p>' + E(a.resumen) + '</p></div></a>';
    return '<a href="' + url + '" style="display:block;padding:16px 18px;border-radius:14px;border:1px solid rgba(127,127,127,.25);color:inherit;text-decoration:none;background:rgba(127,127,127,.05)">' +
      '<span style="display:block;font-size:.8rem;opacity:.7">' + E(a.categoria || 'Divulgación') + ' · ' + E(a.fecha) + '</span>' +
      '<strong style="display:block;font-size:1.05rem;line-height:1.3;margin:4px 0">' + E(a.titulo) + '</strong><span style="display:block;font-size:.9rem;opacity:.8;line-height:1.45">' + E(a.resumen) + '</span></a>';
  }
  function articulos(lista) {
    if (!lista || !lista.length) return;
    if (host === 'aurzane.com' && /^\/articulos\/?(index\.html)?$/.test(ruta)) {   // índice general: cada artículo en su mundo
      Object.keys(NOMBRE).forEach(function (m) {
        var h = d.getElementById(m), suyos = lista.filter(function (a) { return a.mundo === m; });
        if (!h || !suyos.length) return;
        var g = h.nextElementSibling; while (g && !g.classList.contains('tema-grid')) g = g.nextElementSibling;
        if (g) g.insertAdjacentHTML('afterbegin', suyos.map(function (a) { return tarjeta(a, 'indice'); }).join(''));
      });
      if (w.__azIdxAplicar) w.__azIdxAplicar();
      var cont = d.querySelector('.tema-count'); if (cont) { var n = parseInt(cont.textContent, 10); if (n) cont.textContent = (n + lista.length) + ' artículos publicados'; }
      return;
    }
    if (!MUNDO || !/^\/(index\.html)?$/.test(ruta) || d.getElementById('azArt')) return;
    var suyos = lista.filter(function (a) { return a.mundo === MUNDO; }).slice(0, 6); if (!suyos.length) return;
    var pie = d.querySelector('footer'); if (!pie) return;
    var s = d.createElement('section'); s.id = 'azArt'; s.setAttribute('aria-labelledby', 'azArtT');
    s.style.cssText = 'max-width:1160px;margin:0 auto;padding:48px 20px';
    s.innerHTML = '<h2 id="azArtT" style="font-family:\'Bodoni Moda\',serif;font-size:clamp(1.5rem,3vw,2rem);margin:0 0 6px">Artículos recientes de ' + NOMBRE[MUNDO] + '</h2>' +
      '<p style="margin:0 0 18px;opacity:.75">Divulgación basada en estudios, con su fuente al final. <a href="https://aurzane.com/articulos/#' + MUNDO + '" style="color:inherit">Ver todos</a></p>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px">' + suyos.map(function (a) { return tarjeta(a); }).join('') + '</div>';
    pie.parentNode.insertBefore(s, pie);
  }
  /* ---------- 3) Research Hub: los artículos de AURZANE (los de cada mundo y los de la IA) junto a los papers ---------- */
  function hub() {
    if (!(host === 'aurzane.com' && /^\/research(\.html)?\/?$/.test(ruta)) || d.getElementById('azHub')) return;
    var ancla = d.querySelector('.wrap #loadState'); if (!ancla) return;
    var caja = d.createElement('section'); caja.id = 'azHub'; caja.setAttribute('aria-labelledby', 'azHubT');
    caja.style.cssText = 'margin:8px 0 34px';
    ancla.parentNode.insertBefore(caja, ancla);
    var todos = [], mundoSel = 'todos', q = '';
    var COL = { mind: 'var(--mind,#5B43B8)', live: 'var(--live,#B4542C)', nexus: 'var(--nexus,#2F5FA8)', learn: 'var(--learn,#2F7A55)', build: 'var(--build,#8A5A32)' };
    function sinTilde(t) { return String(t || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
    function pintar() {
      var l = todos.filter(function (a) { return (mundoSel === 'todos' || a.mundo === mundoSel) && (!q || sinTilde(a.titulo + ' ' + (a.resumen || '') + ' ' + (a.categoria || '')).indexOf(sinTilde(q)) >= 0); });
      if (!todos.length) { caja.innerHTML = ''; return; }
      caja.innerHTML = '<h2 id="azHubT" style="font-family:\'Bodoni Moda\',serif;font-size:1.5rem;margin:0 0 4px">Artículos de AURZANE</h2>' +
        '<p style="margin:0 0 14px;opacity:.75;font-size:.92rem">Divulgación escrita a partir de estos estudios, ordenada por mundo. ' + l.length + ' de ' + todos.length + '.</p>' +
        (l.length ? '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px">' + l.slice(0, 12).map(function (a) {
          return '<a href="' + E(a.url) + '" style="display:block;padding:14px 16px;border-radius:14px;border:1px solid rgba(127,127,127,.25);border-left:4px solid ' + COL[a.mundo] + ';color:inherit;text-decoration:none;background:rgba(127,127,127,.05)">' +
            '<span style="display:block;font-size:.75rem;font-weight:700;letter-spacing:.04em;color:' + COL[a.mundo] + '">' + E(NOMBRE[a.mundo]) + (a.categoria ? ' · ' + E(String(a.categoria).replace(/[-_]+/g, ' ')) : '') + '</span>' +
            '<strong style="display:block;font-size:1rem;line-height:1.3;margin:4px 0">' + E(a.titulo) + '</strong>' + (a.resumen ? '<span style="display:block;font-size:.86rem;opacity:.8;line-height:1.45">' + E(String(a.resumen).length > 150 ? String(a.resumen).slice(0, 150).replace(/\s+\S*$/, '') + '…' : a.resumen) + '</span>' : '') + '</a>';
        }).join('') + '</div>' + (l.length > 12 ? '<p style="margin:12px 0 0"><a href="https://aurzane.com/articulos/" style="color:inherit">Ver los ' + l.length + ' artículos</a></p>' : '')
        : '<p style="opacity:.7">Ningún artículo de AURZANE coincide con esta búsqueda; abajo tienes los papers.</p>');
    }
    function sumar(lista) { var vistos = {}; todos = todos.concat(lista).filter(function (a) { var k = a.mundo + a.slug; if (vistos[k]) return false; vistos[k] = 1; return true; }).sort(function (x, y) { return String(y.fecha || '').localeCompare(String(x.fecha || '')); }); pintar(); }
    var sc = d.createElement('script'); sc.src = 'https://aurzane.com/articulos/ai.js?d=' + new Date().toISOString().slice(0, 13); sc.async = true;
    sc.onload = function () { sumar((w.__azArticulos || []).map(function (a) { return { mundo: a.mundo, slug: a.slug, titulo: a.titulo, resumen: a.resumen, categoria: a.categoria, fecha: a.fecha, url: 'https://aurzane.com/articulos/' + encodeURIComponent(a.slug) + '/' }; })); };
    (d.head || d.documentElement).appendChild(sc);
    var cli = (typeof sb !== 'undefined' && sb && sb.from) ? sb : null;   // el cliente de Supabase que ya crea research.html
    if (cli) Object.keys(NOMBRE).forEach(function (m) {
      cli.from(m + '_articulos').select('*').limit(200).then(function (r) {
        if (!r || r.error || !r.data) return;
        sumar(r.data.filter(function (a) { return a.slug && a.titulo && (!a.estado || a.estado === 'publicado'); }).map(function (a) {
          return { mundo: m, slug: a.slug, titulo: a.titulo, resumen: a.resumen || a.descripcion || a.extracto || '', categoria: a.categoria, fecha: a.publicado_at || a.created_at || '', url: 'https://' + m + '.aurzane.com/#/articulo/' + encodeURIComponent(a.slug) };
        }));
      }, function () {});
    });
    d.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('[data-mundo]'); if (b) { mundoSel = b.getAttribute('data-mundo'); pintar(); } });
    var inp = d.getElementById('searchInput'); if (inp) inp.addEventListener('input', function () { q = inp.value.trim(); pintar(); });
  }

  /* ---------- 4) «Haz el test» al final de cada artículo (los escritos a mano y los de la IA), según el tema ---------- */
  var TEMAS_T = [[/ansiedad|ansios|p[áa]nico|preocupaci/i, 'https://mind.aurzane.com/test-de-ansiedad/', 'Test de ansiedad'], [/depresi|[áa]nimo|tristeza/i, 'https://mind.aurzane.com/test-de-depresion/', 'Test de depresión'],
    [/burnout|agotamiento|desgaste/i, 'https://mind.aurzane.com/test-de-burnout/', 'Test de burnout'], [/estr[ée]s/i, 'https://mind.aurzane.com/test-de-estres/', 'Test de estrés'],
    [/autoestima/i, 'https://mind.aurzane.com/test-de-autoestima/', 'Test de autoestima'], [/autocompasi/i, 'https://mind.aurzane.com/test-de-autocompasion/', 'Test de autocompasión'],
    [/sue[ñn]o|dormir|insomnio|descanso/i, 'https://live.aurzane.com/test-de-sueno/', 'Test de sueño'], [/soledad|aislamiento/i, 'https://mind.aurzane.com/test-de-soledad/', 'Test de soledad'],
    [/tdah|atenci[óo]n|concentra|distrac/i, 'https://mind.aurzane.com/test-de-tdah/', 'Test de TDAH en adultos'], [/resilien/i, 'https://mind.aurzane.com/test-de-resiliencia/', 'Test de resiliencia'],
    [/h[áa]bito|ejercicio|alimentaci|nutrici|deporte/i, 'https://live.aurzane.com/test-de-habitos/', 'Test de hábitos'], [/personalidad|rasgo/i, 'https://mind.aurzane.com/test-de-personalidad/', 'Test de personalidad'],
    [/carrera|vocaci|universidad|estudiar|grado|selectividad|pau\b/i, 'https://ovp.aurzane.com/portal.html', 'Test vocacional OVP'], [/autoeficacia|confianza en ti|metas/i, 'https://mind.aurzane.com/test-de-autoeficacia/', 'Test de autoeficacia'],
    [/satisfacci|felicidad|prop[óo]sito|sentido de la vida/i, 'https://mind.aurzane.com/test-de-satisfaccion-con-la-vida/', 'Test de satisfacción con la vida'],
    [/bienestar|salud mental|emocion/i, 'https://live.aurzane.com/test-de-bienestar/', 'Test de bienestar'], [/hipoteca|vivienda|alquiler/i, 'https://build.aurzane.com/calculadora-hipoteca/', 'Calculadora de hipoteca']];
  function cajaTest(dentro, antes) {
    if (!dentro || dentro.querySelector('.az-cta-test')) return;
    var h = dentro.querySelector('h1') || d.querySelector('h1'); if (!h) return;
    var txt = h.textContent;   // solo el título: el primer párrafo mezcla temas y daba tests poco relacionados
    var t = null; for (var i = 0; i < TEMAS_T.length && !t; i++) if (TEMAS_T[i][0].test(txt)) t = TEMAS_T[i];
    if (!t) {   // sin tema claro: lo más útil de su mundo
      var mm = MUNDO || ((d.title.match(/AURZANE (MIND|LIVE|LEARN|NEXUS|BUILD)/) || [])[1] || '').toLowerCase();
      t = { nexus: [0, 'https://ovp.aurzane.com/portal.html', 'Test vocacional OVP'], learn: [0, 'https://ovp.aurzane.com/portal.html', 'Test vocacional OVP'],
            build: [0, 'https://build.aurzane.com/calculadora-hipoteca/', 'Calculadora de hipoteca'], mind: [0, 'https://mind.aurzane.com/test-de-personalidad/', 'Test de personalidad'] }[mm] ||
          [0, 'https://live.aurzane.com/test-de-bienestar/', 'Test de bienestar'];
    }
    var es = /^Calculadora/.test(t[2]);
    var c = d.createElement('aside'); c.className = 'az-cta-test';
    c.style.cssText = 'margin:34px 0;padding:22px 24px;border-radius:18px;background:linear-gradient(150deg,#2a1f63,#5B43B8);color:#fff';
    c.innerHTML = '<p style="margin:0 0 4px;font-size:.8rem;font-weight:700;letter-spacing:.05em;opacity:.8">PONLO A PRUEBA</p><p style="margin:0 0 14px;font-size:1.15rem;font-weight:600;line-height:1.35;color:#fff">' +
      (es ? 'Haz tus números con la ' + E(t[2]) + ': gratis y al momento.' : 'Haz el ' + E(t[2]) + ': gratis, anónimo y con tu resultado explicado al momento.') + '</p>' +
      '<a href="' + t[1] + '" style="display:inline-block;background:#FFD9A0;color:#1b1440;font-weight:700;text-decoration:none;padding:11px 20px;border-radius:99px">' + (es ? 'Abrir la calculadora' : 'Hacer el test') + '</a>';
    if (antes && antes.parentNode) antes.parentNode.insertBefore(c, antes); else dentro.appendChild(c);
  }
  function articulosConTest() {
    if (host === 'aurzane.com' && /^\/articulos\/[^/]+\/?$/.test(ruta) && !/recientes/.test(ruta)) {
      var m = d.querySelector('main.article') || d.querySelector('main'); if (m) cajaTest(m, m.querySelector('.sources'));
    }
    var ac = d.getElementById('articleContent');
    if (MUNDO && ac) {
      var pon = function () { if (ac.querySelector('h1') && !ac.querySelector('.az-cta-test')) cajaTest(ac, ac.querySelector('.sources,.fuentes,.art-sources')); };
      new MutationObserver(pon).observe(ac, { childList: true }); pon();
    }
  }

  /* ---------- 5) índice de artículos: buscador, filtro por mundo, destacado y listas que no se hacen eternas ---------- */
  function indiceArticulos() {
    if (!(host === 'aurzane.com' && /^\/articulos\/?(index\.html)?$/.test(ruta)) || d.getElementById('azIdx')) return;
    var hero = d.querySelector('.tema-hero'); if (!hero) return;
    var COL = { mind: '#5B43B8', nexus: '#2F5FA8', live: '#B4542C', learn: '#2F7A55', build: '#8A5A32' };
    var css = d.createElement('style');
    css.textContent = '#azIdx{position:sticky;top:0;z-index:20;padding:14px 0;margin:6px 0 10px;background:var(--bg,#0b0e1d);border-bottom:1px solid rgba(127,127,127,.2)}' +
      '#azIdx input{width:100%;max-width:520px;box-sizing:border-box;padding:12px 16px;border-radius:99px;border:1px solid rgba(127,127,127,.35);background:rgba(127,127,127,.08);color:inherit;font:inherit}' +
      '#azIdx .ch{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}#azIdx button{cursor:pointer;border-radius:99px;padding:7px 14px;border:1px solid rgba(127,127,127,.35);background:transparent;color:inherit;font:600 .85rem/1 inherit}' +
      '#azIdx button[aria-pressed="true"]{background:var(--c,#C9A24B);border-color:var(--c,#C9A24B);color:#fff}' +
      '.az-dest{display:grid;grid-template-columns:1.3fr 1fr;border-radius:22px;overflow:hidden;margin:18px 0 34px;text-decoration:none;color:#fff;background:#151a36;min-height:300px}' +
      '.az-dest img{width:100%;height:100%;object-fit:cover;display:block}.az-dest div{padding:30px 32px;display:flex;flex-direction:column;justify-content:center}' +
      '.az-dest small{font-weight:700;letter-spacing:.06em;font-size:.75rem;opacity:.85}.az-dest h2{font:700 clamp(1.4rem,2.6vw,2rem)/1.2 "Bodoni Moda",Georgia,serif;margin:8px 0 10px;color:#fff}.az-dest p{margin:0;opacity:.85;line-height:1.5}' +
      '.az-mas{display:block;margin:14px 0 30px;cursor:pointer;border-radius:99px;padding:11px 20px;border:1px solid rgba(127,127,127,.4);background:transparent;color:inherit;font:600 .9rem inherit}' +
      '.az-oculta{display:none!important}@media(max-width:760px){.az-dest{grid-template-columns:1fr}.az-dest img{height:200px}}';
    d.head.appendChild(css);
    var grids = Array.prototype.slice.call(d.querySelectorAll('.tema-grid'));
    function mundoDe(g) { var t = g.previousElementSibling; while (t && !t.classList.contains('mundo-titulo')) t = t.previousElementSibling; return t ? t.id : ''; }
    var barra = d.createElement('div'); barra.id = 'azIdx'; barra.setAttribute('data-nosnippet', '');
    barra.innerHTML = '<input type="search" placeholder="Busca un tema: ansiedad, sueño, estudiar, hipoteca…" aria-label="Buscar artículos"><div class="ch"><button type="button" data-m="" aria-pressed="true">Todos</button>' +
      Object.keys(COL).map(function (m) { return '<button type="button" data-m="' + m + '" style="--c:' + COL[m] + '" aria-pressed="false">' + NOMBRE[m] + '</button>'; }).join('') + '</div>';
    hero.parentNode.insertBefore(barra, hero.nextSibling);
    /* destacado: el artículo más reciente con imagen */
    var primera = d.querySelector('.tema-grid .tema-card img');
    if (primera) {
      var card = primera.closest('a'), dest = d.createElement('a'); dest.className = 'az-dest'; dest.href = card.href;
      var cat = card.querySelector('.cat'), h3 = card.querySelector('h3'), pp = card.querySelector('p');
      dest.innerHTML = '<img src="' + E(primera.src) + '" alt="" loading="lazy"><div><small>DESTACADO · ' + E(cat ? cat.textContent : '') + '</small><h2>' + E(h3 ? h3.textContent : '') + '</h2><p>' + E(pp ? pp.textContent : '') + '</p></div>';
      barra.parentNode.insertBefore(dest, barra.nextSibling);
    }
    var mundo = '', q = '', abiertos = {};
    function sinT(t) { return String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
    function aplicar() {
      grids.forEach(function (g) {
        var m = mundoDe(g), tit = d.getElementById(m), cards = Array.prototype.slice.call(g.children), vis = 0;
        var muestra = !mundo || mundo === m;
        cards.forEach(function (c) {
          var ok = muestra && (!q || sinT(c.textContent).indexOf(q) >= 0);
          var cabe = q || mundo || abiertos[m] || vis < 6;
          c.classList.toggle('az-oculta', !(ok && cabe)); if (ok) vis++;
        });
        var hay = vis > 0; g.classList.toggle('az-oculta', !hay); if (tit) tit.classList.toggle('az-oculta', !hay);
        var b = g.nextElementSibling && g.nextElementSibling.classList.contains('az-mas') ? g.nextElementSibling : null;
        if (!b) { b = d.createElement('button'); b.type = 'button'; b.className = 'az-mas'; g.parentNode.insertBefore(b, g.nextSibling);
          b.addEventListener('click', function () { abiertos[m] = true; aplicar(); }); }
        b.textContent = 'Ver los ' + vis + ' artículos de ' + (NOMBRE[m] || m);
        b.classList.toggle('az-oculta', !hay || q || mundo || abiertos[m] || vis <= 6);
      });
    }
    barra.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-m]'); if (!b) return; mundo = b.getAttribute('data-m');
      Array.prototype.forEach.call(barra.querySelectorAll('button[data-m]'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); aplicar();
    });
    var inp = barra.querySelector('input'); inp.addEventListener('input', function () { q = sinT(inp.value.trim()); aplicar(); });
    if (location.hash && NOMBRE[location.hash.slice(1)]) { mundo = location.hash.slice(1); Array.prototype.forEach.call(barra.querySelectorAll('button[data-m]'), function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-m') === mundo ? 'true' : 'false'); }); }
    aplicar(); w.__azIdxAplicar = aplicar;
  }
  function iniciar() {
    hub(); articulosConTest(); indiceArticulos();
    enganche();
    if (MUNDO || (host === 'aurzane.com' && /^\/articulos\/?(index\.html)?$/.test(ruta)))
    { var sc = d.createElement('script'); sc.src = 'https://aurzane.com/articulos/ai.js?d=' + new Date().toISOString().slice(0, 13); sc.async = true;   // script (no fetch) para que funcione desde todos los subdominios
      sc.onload = function () { articulos(w.__azArticulos || []); }; (d.head || d.documentElement).appendChild(sc); }
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document, window);
