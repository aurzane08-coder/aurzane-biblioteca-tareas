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
    /* 19/11/2026 (rediseño editorial): la «imagen» de los artículos de la IA es la primera página escaneada del estudio; en la
       tarjeta no aporta y rompía el ritmo de la cuadrícula, así que la tarjeta va solo con texto (la imagen sigue en el artículo) */
    var img = a.imagen && !/\/biblioteca\/recientes\//.test(a.imagen) ? a.imagen : '';
    /* FOTO_V4 (rediseño v4, 22/11/2026): sin imagen propia, foto real según el tema; nunca una imagen creada */
    if (!img) { var tx = ((a.categoria || '') + ' ' + (a.titulo || '')).toLowerCase(), F = [[/ansiedad|p[áa]nico|preocupa/, '1505142468610-359e7d316be0'], [/estr[ée]s|burnout|agotamiento/, '1541199249251-f713e6145474'], [/depresi|[áa]nimo|triste/, '1529665253569-6d01c0eaf7b6'], [/sue[ñn]o|insomnio|dormir|descans/, '1541781774459-bb2af2f05b55'], [/h[áa]bito|aliment|nutric|ejercicio|deporte/, '1490645935967-10de6ba17061'], [/autoestima|identidad|personalidad/, '1517841905240-472988babdf9'], [/pareja|relaci|amistad|famil|v[íi]nculo|cuidado/, '1544027993-37dbfe43562a'], [/soledad|aislamiento/, '1512438248247-f0f2a5a8b7f0'], [/duelo|p[ée]rdida|muerte|resilien|trauma/, '1466692476868-aef1dfb1e735'], [/bienestar|felicidad|satisfacc|prop[óo]sito|mindful|calma/, '1506126613408-eca07ce68773'], [/carrera|vocaci|universidad|oferta|acceso|elegir/, '1541339907198-e08756dedf3f'], [/aprend|estudi|memoria|metacog|educa|ense[ñn]|tdah|atenci/, '1434030216411-0b793f4b4173'], [/curso|formaci|certific/, '1522202176988-66273c2fd55f'], [/hipoteca|vivienda|dinero|ahorro|inmobil|finanz|sueldo|inver/, '1579621970563-ebec7560ff3e'], [/libro|lectura|biblioteca/, '1532012197267-da84d127e765']], M = { mind: '1559757175-5700dde675bc', nexus: '1541339907198-e08756dedf3f', live: '1454496522488-7a8e488e8606', learn: '1481627834876-b7833e8f5570', build: '1461360370896-922624d12aa1' }, id = '';
      for (var q = 0; q < F.length && !id; q++) if (F[q][0].test(tx)) id = F[q][1];
      img = 'https://images.unsplash.com/photo-' + (id || M[a.mundo] || M.mind) + '?w=800&h=450&q=70&fit=crop&auto=format'; }
    if (estilo === 'indice') return '<a class="tema-card' + (img ? '' : ' sin-img') + '" href="' + url + '">' + (img ? '<img src="' + E(img) + '" alt="" loading="lazy">' : '') +
      '<div class="tema-card-body"><span class="cat">' + E(NOMBRE[a.mundo]) + ' · ' + E(a.categoria || 'Divulgación') + '</span><h3>' + E(a.titulo) + '</h3><p>' + E(a.resumen) + '</p></div></a>';
    return '<a class="az-art-c" href="' + url + '">' + (img ? '<img src="' + E(img) + '" alt="" loading="lazy" width="800" height="450">' : '') + '<span class="az-art-t">' +
      '<span style="display:block;font-size:.8rem;opacity:.7">' + E(a.categoria || 'Divulgación') + ' · ' + E(a.fecha) + '</span>' +
      '<strong style="display:block;font-size:1.05rem;line-height:1.3;margin:4px 0">' + E(a.titulo) + '</strong><span style="display:block;font-size:.9rem;opacity:.8;line-height:1.45">' + E(a.resumen) + '</span></span></a>';
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
    c.style.cssText = 'margin:34px 0;padding:22px 24px;border-radius:18px;background:linear-gradient(150deg,#1B352D,#5B43B8);color:#fff';
    c.innerHTML = '<p style="margin:0 0 4px;font-size:.8rem;font-weight:700;letter-spacing:.05em;opacity:.8">PONLO A PRUEBA</p><p style="margin:0 0 14px;font-size:1.15rem;font-weight:600;line-height:1.35;color:#fff">' +
      (es ? 'Haz tus números con la ' + E(t[2]) + ': gratis y al momento.' : 'Haz el ' + E(t[2]) + ': gratis, anónimo y con tu resultado explicado al momento.') + '</p>' +
      '<a href="' + t[1] + '" style="display:inline-block;background:#EADEC6;color:#132A23;font-weight:700;text-decoration:none;padding:11px 20px;border-radius:99px">' + (es ? 'Abrir la calculadora' : 'Hacer el test') + '</a>';
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
    css.textContent = '#azIdx{position:sticky;top:0;z-index:20;padding:14px 0;margin:6px 0 10px;background:var(--bg,#151F1B);border-bottom:1px solid rgba(127,127,127,.2)}' +
      '#azIdx input{width:100%;max-width:520px;box-sizing:border-box;padding:12px 16px;border-radius:99px;border:1px solid rgba(127,127,127,.35);background:rgba(127,127,127,.08);color:inherit;font:inherit}' +
      '#azIdx .ch{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}#azIdx button{cursor:pointer;border-radius:99px;padding:7px 14px;border:1px solid rgba(127,127,127,.35);background:transparent;color:inherit;font:600 .85rem/1 inherit}' +
      '#azIdx button[aria-pressed="true"]{background:var(--c,#C7B99B);border-color:var(--c,#C7B99B);color:#fff}' +
      '.az-dest{display:grid;grid-template-columns:1.3fr 1fr;border-radius:22px;overflow:hidden;margin:18px 0 34px;text-decoration:none;color:#fff;background:#172923;min-height:300px}' +
      '.az-dest img{width:100%;height:100%;object-fit:cover;display:block}.az-dest div{padding:30px 32px;display:flex;flex-direction:column;justify-content:center}' +
      '.az-dest small{font-weight:700;letter-spacing:.06em;font-size:.75rem;opacity:.85}.az-dest h2{font:700 clamp(1.4rem,2.6vw,2rem)/1.2 "Bodoni Moda",Georgia,serif;margin:8px 0 10px;color:#fff}.az-dest p{margin:0;opacity:.85;line-height:1.5}' +
      '.az-mas{display:block;margin:14px 0 30px;cursor:pointer;border-radius:99px;padding:11px 20px;border:1px solid rgba(127,127,127,.4);background:transparent;color:inherit;font:600 .9rem inherit}' +
      '.az-oculta{display:none!important}@media(max-width:760px){.az-dest{grid-template-columns:1fr}.az-dest img{height:200px}}' +
      /* rediseño editorial: tarjetas que no se estiran, imagen con proporción fija, resumen de 3 líneas y tarjetas de texto más ligeras */
      '.tema-grid{align-items:start;gap:18px}.tema-card{transition:border-color .2s}.tema-card:hover{border-color:var(--c,rgba(199,185,155,.5))}' +
      '.tema-card img{display:block;width:100%;aspect-ratio:16/9;height:auto;object-fit:cover}' +
      '.tema-card-body{padding:18px 20px 20px}.tema-card-body .cat{font-size:.72rem;letter-spacing:.06em}' +
      '.tema-card-body h3{font-family:"Bodoni Moda",Georgia,serif;font-size:1.12rem;line-height:1.3;margin:8px 0 8px}' +
      '.tema-card-body p{margin:0;line-height:1.55;font-size:.9rem;opacity:.85;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}' +
      '.tema-card.sin-img{background:transparent;border-style:solid}.tema-card.sin-img .tema-card-body{padding:22px 22px 24px}';
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

  /* ---------- 6) libros recomendados del tema (tienda aurzane.com/libros/, enlaces de afiliado de Amazon) ---------- */
  var TEMA_LIB = [[/ansiedad|ansios|p[áa]nico|preocupaci/i, 'ansiedad'], [/depresi|[áa]nimo|tristeza/i, 'depresion'], [/burnout|agotamiento|desgaste/i, 'burnout'],
    [/estr[ée]s/i, 'estres'], [/autoestima/i, 'autoestima'], [/autocompasi/i, 'autocompasion'], [/sue[ñn]o|dormir|insomnio/i, 'sueno'], [/soledad|aislamiento/i, 'soledad'],
    [/tdah|atenci[óo]n|concentra|distrac/i, 'tdah'], [/resilien|trauma/i, 'resiliencia'], [/h[áa]bito|ejercicio|deporte|nutrici|alimentaci/i, 'habitos'],
    [/personalidad|rasgo|introvert/i, 'personalidad'], [/duelo|p[ée]rdida|muerte/i, 'duelo'], [/pareja|amor|relaci[óo]n|apego|amistad/i, 'relaciones'],
    [/hijo|crianza|infancia|ni[ñn]o|adolescen/i, 'crianza'], [/carrera|vocaci|universidad|estudiar|aprend|grado/i, 'vocacional'],
    [/hipoteca|vivienda|alquiler|sueldo|dinero|ahorro|inversi/i, 'finanzas'], [/felicidad|satisfacci|prop[óo]sito|bienestar/i, 'bienestar'], [/emoci/i, 'emociones']];
  var POR_SLUG = { 'test-de-satisfaccion-con-la-vida': 'satisfaccion', 'calculadora-hipoteca': 'vivienda', 'calculadora-reforma': 'vivienda', 'calculadora-sueldo-neto': 'finanzas',
    'calculadora-imc': 'habitos', 'calculadora-calorias': 'habitos', 'calculadora-agua': 'habitos', 'calculadora-embarazo': 'crianza', 'calculadora-nota-pau': 'vocacional' };
  var POR_MUNDO = { mind: 'personalidad', live: 'bienestar', learn: 'vocacional', nexus: 'vocacional', build: 'finanzas' };
  function temaLibros(texto) {
    var slug = (ruta.split('/').filter(Boolean)[0] || '');
    if (POR_SLUG[slug]) return POR_SLUG[slug];
    if (/^test-de-/.test(slug)) return slug.replace(/^test-de-/, '');
    for (var i = 0; i < TEMA_LIB.length; i++) if (TEMA_LIB[i][0].test(texto || '')) return TEMA_LIB[i][1];
    var mm = MUNDO || ((d.title.match(/AURZANE (MIND|LIVE|LEARN|NEXUS|BUILD)/) || [])[1] || '').toLowerCase();
    return POR_MUNDO[mm] || 'bienestar';
  }
  var libPend = [];
  function conLibros(fn) {
    if (w.__azLibros) return fn(w.__azLibros);
    libPend.push(fn); if (libPend.length > 1) return;
    var sc = d.createElement('script'); sc.src = 'https://aurzane.com/libros/libros.js?d=' + new Date().toISOString().slice(0, 10); sc.async = true;
    sc.onload = function () { var l = w.__azLibros || []; libPend.splice(0).forEach(function (f) { f(l); }); };
    (d.head || d.documentElement).appendChild(sc);
  }
  function cajaLibros(dentro, antes, texto) {
    if (!dentro || dentro.querySelector('.az-libros') || d.querySelector('.az-libros')) return;
    var tema = temaLibros(texto);
    conLibros(function (todos) {
      if (d.querySelector('.az-libros')) return;
      /* si faltan libros del tema se completa con temas cercanos, nunca con otros que no tengan que ver (17/11/2026: en la hipoteca salían libros de perros) */
      var CERCA = { vivienda: ['finanzas', 'productividad'], finanzas: ['vivienda', 'productividad'], crianza: ['relaciones', 'emociones'], vocacional: ['productividad', 'habitos'],
        habitos: ['productividad', 'sueno'], sueno: ['habitos', 'estres'], ansiedad: ['estres', 'emociones'], estres: ['ansiedad', 'burnout'], depresion: ['emociones', 'resiliencia'],
        burnout: ['estres', 'productividad'], autoestima: ['autocompasion', 'emociones'], autocompasion: ['autoestima', 'emociones'], soledad: ['relaciones', 'emociones'],
        tdah: ['productividad', 'habitos'], satisfaccion: ['bienestar', 'resiliencia'], personalidad: ['emociones', 'ciencia'] };
      var pref = [tema].concat(CERCA[tema] || ['bienestar']), l = [];
      pref.forEach(function (t) { todos.forEach(function (x) { if (l.length < 3 && x.img && x.temas.indexOf('novela') < 0 && x.temas.indexOf(t) >= 0 && l.indexOf(x) < 0) l.push(x); }); });
      if (l.length < 2) return;
      var c = d.createElement('aside'); c.className = 'az-libros'; c.setAttribute('data-nosnippet', '');
      c.style.cssText = 'margin:34px auto;max-width:1120px;padding:22px 24px;border-radius:20px;background:#182823;color:#f3efe6;border:1px solid rgba(255,255,255,.1)';
      c.innerHTML = '<p style="margin:0 0 4px;font:700 1.25rem/1.25 \'Bodoni Moda\',Georgia,serif;color:#f3efe6">Libros para seguir profundizando</p>' +
        '<p style="margin:0 0 16px;font-size:.88rem;opacity:.75">Elegidos por AURZANE sobre este tema.</p>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:16px">' + l.map(function (x) {
          return '<a href="' + E(x.u) + '" target="_blank" rel="sponsored nofollow noopener" style="display:flex;gap:12px;align-items:flex-start;text-decoration:none;color:inherit">' +
            '<img src="' + E(x.img) + '" alt="Portada de ' + E(x.t) + '" loading="lazy" width="64" height="96" style="width:64px;height:96px;object-fit:cover;border-radius:6px;flex:none;box-shadow:0 10px 20px -10px #000">' +
            '<span><b style="display:block;font-size:.92rem;line-height:1.3">' + E(x.t) + '</b><span style="display:block;font-size:.8rem;opacity:.7;margin:2px 0 6px">' + E(x.a) + '</span>' +
            '<span style="display:inline-block;font-size:.75rem;font-weight:700;color:#132A23;background:#D1C2A3;border-radius:99px;padding:3px 10px">Ver en Amazon</span></span></a>';
        }).join('') + '</div>' +
        '<p style="margin:16px 0 0;font-size:.78rem;opacity:.6">Enlaces de afiliado de Amazon: si compras, AURZANE recibe una pequeña comisión sin coste para ti. <a href="https://aurzane.com/libros/" style="color:inherit">Ver toda la tienda de libros</a></p>';
      if (antes && antes.parentNode) antes.parentNode.insertBefore(c, antes); else dentro.appendChild(c);
    });
  }
  function librosEnPaginas() {
    var slug = (ruta.split('/').filter(Boolean)[0] || '');
    if (MUNDO && /^(test-de-|calculadora-)/.test(slug)) {   // tests y calculadoras: antes de «Sigue explorando» o del pie
      var colocar = function () { var ant = d.querySelector('.az-explorar') || d.querySelector('footer'); if (ant) cajaLibros(ant.parentNode, ant, (d.querySelector('h1') || {}).textContent); };
      if (d.querySelector('.az-explorar')) colocar(); else setTimeout(colocar, 1200);
      return;
    }
    if (host === 'aurzane.com' && /^\/articulos\/[^/]+\/?$/.test(ruta)) {
      var m = d.querySelector('main.article') || d.querySelector('main'); if (m) setTimeout(function () { cajaLibros(m, m.querySelector('.sources'), (m.querySelector('h1') || {}).textContent); }, 300);
    }
    var ac = d.getElementById('articleContent');
    if (MUNDO && ac) new MutationObserver(function () {
      var h = ac.querySelector('h1'); if (!h) return; var v = ac.querySelector('.az-libros'); if (v && v.getAttribute('data-h') === h.textContent) return;
      if (v) v.remove(); cajaLibros(ac, ac.querySelector('.sources,.fuentes,.art-sources'), h.textContent);
      setTimeout(function () { var n = ac.querySelector('.az-libros'); if (n) n.setAttribute('data-h', h.textContent); }, 1500);
    }).observe(ac, { childList: true });
  }
  function iniciar() {
    hub(); articulosConTest(); indiceArticulos(); librosEnPaginas();
    enganche();
    if (MUNDO || (host === 'aurzane.com' && /^\/articulos\/?(index\.html)?$/.test(ruta)))
    { var sc = d.createElement('script'); sc.src = 'https://aurzane.com/articulos/ai.js?d=' + new Date().toISOString().slice(0, 13); sc.async = true;   // script (no fetch) para que funcione desde todos los subdominios
      sc.onload = function () { articulos(w.__azArticulos || []); }; (d.head || d.documentElement).appendChild(sc); }
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document, window);
