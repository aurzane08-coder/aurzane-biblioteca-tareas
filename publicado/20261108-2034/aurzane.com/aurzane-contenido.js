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
  function iniciar() {
    hub();
    enganche();
    if (MUNDO || (host === 'aurzane.com' && /^\/articulos\/?(index\.html)?$/.test(ruta)))
    { var sc = d.createElement('script'); sc.src = 'https://aurzane.com/articulos/ai.js?d=' + new Date().toISOString().slice(0, 13); sc.async = true;   // script (no fetch) para que funcione desde todos los subdominios
      sc.onload = function () { articulos(w.__azArticulos || []); }; (d.head || d.documentElement).appendChild(sc); }
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document, window);
