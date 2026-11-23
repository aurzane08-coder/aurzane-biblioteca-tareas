/*
 * AURZANE · Paleta de color compartida por todo el ecosistema
 * Se carga en <head> de cada página (aurzane.com y todos los mundos):
 *   <script src="https://aurzane.com/aurzane-paleta.js"></script>
 * - Guarda la elección en una cookie de .aurzane.com, así se mantiene al pasar de un mundo a otro.
 * - Aplica la paleta sobre las variables CSS que usan las páginas (--gold, --navy-*, --accent...).
 * - Pinta las opciones en los paneles .paleta-swatches que tenga la página
 *   y añade un botón flotante 🎨 para elegir el color desde cualquier sitio.
 */

/* Calculadoras insertables en otras webs (16/11/2026): con ?embed=1 la calculadora se muestra sola, sin cabecera,
   anuncios ni textos largos, con un enlace a AURZANE y su altura avisada a la web que la inserta (aurzane.com/insertar/) */
(function (d, w) {
  if (!/(^|[?&])embed=1(&|$)/.test(location.search) || !/^\/calculadora-/.test(location.pathname)) return;
  w.__azEmbed = 1; d.documentElement.classList.add('az-embed');
  var st = d.createElement('style');
  st.textContent = 'html.az-embed .utility,html.az-embed .topbar,html.az-embed .az-cab,html.az-embed .az-subnav,html.az-embed footer,html.az-embed .az-pie,' +
    'html.az-embed ins.adsbygoogle,html.az-embed section.bloque,html.az-embed .az-guia,html.az-embed .movil-barra,html.az-embed .az-dock,html.az-embed #azDock,' +
    'html.az-embed .az-empieza,html.az-embed .az-boletin,html.az-embed .az-socio,html.az-embed .az-explorar,html.az-embed .az-curso-rel,html.az-embed .eco,' +
    'html.az-embed aside.firma,html.az-embed .az-saltar,html.az-embed .migas,html.az-embed .az-libros,html.az-embed aside[data-nosnippet]{display:none!important}' +
    'html.az-embed body>*:not(section.hero):not(main):not(.wrap:has(.app)):not(.az-embed-pie):not(script):not(style){display:none!important}' +
    'html.az-embed body::before{display:none!important}html.az-embed section.hero{padding:14px 0 6px!important;min-height:0!important}' +
    'html.az-embed section.hero p{display:none}html.az-embed h1{font-size:1.5rem!important;margin:0!important}' +
    '.az-embed-pie{margin:14px auto 10px;max-width:1100px;padding:0 16px;font:600 13px/1.4 system-ui,sans-serif;opacity:.85}.az-embed-pie a{color:inherit}';
  (d.head || d.documentElement).appendChild(st);
  function alto() { try { var pie = d.querySelector('.az-embed-pie'); var h = pie ? Math.ceil(pie.getBoundingClientRect().bottom + w.scrollY + 12) : d.documentElement.scrollHeight; w.parent.postMessage({ az: 'alto', h: h, u: location.pathname }, '*'); } catch (e) {} }
  d.addEventListener('DOMContentLoaded', function () {
    var c = d.querySelector('link[rel="canonical"]'), u = (c && c.href) || (location.origin + location.pathname);
    var p = d.createElement('p'); p.className = 'az-embed-pie';
    p.innerHTML = 'Calculadora gratuita de <a href="' + u + '?utm_source=insertada&amp;utm_medium=' + encodeURIComponent(d.referrer ? new URL(d.referrer).hostname : 'web') + '" target="_blank" rel="noopener">AURZANE</a>';
    d.body.appendChild(p);
    Array.prototype.forEach.call(d.querySelectorAll('a[href]'), function (a) { if (!a.target) a.target = '_blank'; });
    alto(); if (w.ResizeObserver) new ResizeObserver(alto).observe(d.body); w.addEventListener('load', alto);
  });
})(document, window);

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
  // v4 tiene una sola identidad (verde y champán): las paletas del diseño anterior que alguien eligiera (grafito, púrpura…) ya no se aplican
  function paleta() { var c = html.className, n = c.replace(/\bpaleta-(?!dorado\b)[a-z]+\b/g, '').replace(/\s+/g, ' ').trim(); if (!/\bpaleta-dorado\b/.test(n)) n += ' paleta-dorado'; if (n !== c) html.className = n; }
  paleta(); if (w.MutationObserver) new MutationObserver(paleta).observe(html, { attributes: true, attributeFilter: ['class'] });
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
    var cab = d.querySelector('main > .hero, section.hero, header.hero, .u-hero, .hero-wrap, .world-header, main > header:first-child, body > div.h, .tx-hero, main > .tema-hero'); if (!cab) return;
    var cs = getComputedStyle(cab); if (/url\(/.test(cs.backgroundImage)) return;
    var cols = ((cs.backgroundColor + ' ' + cs.backgroundImage).match(/rgba?\([^)]+\)|color\(srgb [^)]+\)/g) || []).map(function (x) {
        var k = /^color/.test(x), v = x.replace(/rgba?\(|color\(srgb |\)/g, '').split(/[ ,\/]+/).filter(Boolean).map(Number);
        return k ? [v[0] * 255, v[1] * 255, v[2] * 255, v.length > 3 ? v[3] : 1] : v; })
      .filter(function (c) { return c.length < 4 || c[3] >= .5; });
    var c = cols[0]; if (!c) return;
    if (.2126 * c[0] + .7152 * c[1] + .0722 * c[2] > 90) return;   // solo cabeceras oscuras: el texto claro sigue legible (también con foto del catálogo)
    if (!u || /og-portada|logo|portadas?\//i.test(u)) {   // sin foto propia: una del catálogo según el título de la página
      if (window.AurzaneBanco && !cab.__v4b) { cab.__v4b = 1; window.AurzaneBanco.listo(function () { var f = window.AurzaneBanco.foto((d.documentElement.className.match(/az-ds-(mind|nexus|live|learn|build|ovp)/) || [0, 'general'])[1], d.title, 1600); if (f) { var m = d.querySelector('meta[property="og:image"]'); cab.style.setProperty('--v4-foto', 'url("' + f + '")'); cab.setAttribute('data-v4-foto', '1'); d.documentElement.classList.add('az-v4-cabfoto'); } }); }
      return;
    }
    cab.style.setProperty('--v4-foto', 'url("' + u.replace(/"/g, '%22') + '")'); cab.setAttribute('data-v4-foto', '1');
    d.documentElement.classList.add('az-v4-cabfoto');
  }
  if (d.readyState === 'complete') setTimeout(fotoCab, 300); else window.addEventListener('load', function () { setTimeout(fotoCab, 300); });
})(document);
/* Catálogo de imágenes (índice aurzane.com/catalogo/imagenes.json, unos cientos de KB; las fotos salen de los CDN de Unsplash y Pexels
   en AVIF, sin ocupar espacio en SiteGround): elige una foto real según el mundo y el tema del texto, distinta para cada texto.
   AurzaneBanco.foto(mundo, texto, ancho) devuelve la URL (o null si el índice aún no cargó); AurzaneBanco.listo(fn) avisa al cargar. */
(function (w, d) {
  if (w.AurzaneBanco) return;
  var idx = null, cola = [], INDICE = 'https://aurzane.com/catalogo/imagenes.json';
  var CLAVES = [
    [/ansiedad|anxi|p[áa]nico|panic|worry|preocupa/i, 'mind', 'ansiedad'], [/depres|tristeza|sadness|mood|[áa]nimo/i, 'mind', 'tristeza'],
    [/estr[ée]s|stress|burnout|agotamiento/i, 'mind', 'estres'], [/cerebr|brain|neuro|cognit/i, 'mind', 'cerebro'],
    [/terapia|therap|counsel|psicoterap/i, 'mind', 'terapia'], [/mindful|medita|atenci[óo]n plena/i, 'mind', 'meditacion'],
    [/sue[ñn]o|sleep|insomn|dormir/i, 'mind', 'sueno'], [/pareja|couple|marital|romantic|amor/i, 'mind', 'pareja'],
    [/famil|parent|padres|madre|padre|crianza/i, 'mind', 'familia'], [/ni[ñn]|child|infan|kid|beb[ée]/i, 'mind', 'infancia'],
    [/adolesc|teen|youth|j[óo]ven/i, 'mind', 'adolescentes'], [/older|elder|aging|envejec|mayores|dementia|demencia|alzheimer/i, 'mind', 'mayores'],
    [/emoci|emotion|feeling|sentimiento/i, 'mind', 'emociones'], [/autoestima|self-esteem|self-efficacy|autoeficacia|confianza/i, 'mind', 'autoestima'],
    [/soledad|loneli|isolat|aislamiento/i, 'mind', 'soledad'],
    [/universi|higher education|college|campus|facultad/i, 'nexus', 'campus'], [/estudiante|student|alumn/i, 'nexus', 'estudiantes'],
    [/graduat|career|carrera|employab|vocaci/i, 'nexus', 'graduacion'], [/teach|docen|profesor|lecture|ense[ñn]/i, 'nexus', 'clase'],
    [/laborator|experiment/i, 'nexus', 'laboratorio'], [/artificial|machine learning|software|algorit|digital|comput|tecnolog|internet/i, 'nexus', 'tecnologia'],
    [/research|investigaci|scien|cienc/i, 'nexus', 'investigacion'],
    [/diet|nutri|food|aliment|obes|comida/i, 'live', 'alimentacion'], [/exercis|ejercicio|physical activity|actividad f[íi]sica|running|correr|fitness/i, 'live', 'correr'],
    [/yoga/i, 'live', 'yoga'], [/water|hidrat|agua/i, 'live', 'agua'], [/pregnan|embaraz|maternal|birth|parto/i, 'live', 'embarazo'],
    [/clinic|patient|paciente|hospital|medical|m[ée]dic|salud|health/i, 'live', 'medico'], [/sport|deport|athlet|atleta/i, 'live', 'deporte'],
    [/lectura|reading|literacy|libro|book/i, 'learn', 'lectura'], [/aprend|learning|study|estudi/i, 'learn', 'estudiar'],
    [/aula|classroom|school|escuela|colegio/i, 'learn', 'aula'], [/online|e-learning|mooc|virtual/i, 'learn', 'online'],
    [/idioma|language|bilingu|lengua/i, 'learn', 'idiomas'], [/memoria|memory/i, 'learn', 'memoria'], [/escritura|writing|escribir/i, 'learn', 'escritura'],
    [/atenci[óo]n|attention|focus|concentr|tdah|adhd/i, 'learn', 'concentracion'],
    [/hipoteca|mortgage/i, 'build', 'llaves'], [/alquiler|rent/i, 'build', 'pisos'], [/vivienda|housing|home|house|hogar/i, 'build', 'vivienda'],
    [/ahorro|saving|pensi[óo]n|retire|jubil/i, 'build', 'jubilacion'], [/financ|money|dinero|income|ingreso|econom|sueldo|salario/i, 'build', 'dinero'],
    [/architect|arquitect|urban|ciudad|city/i, 'build', 'arquitectura'], [/construct|obra|reforma/i, 'build', 'obra'],
    [/energ|solar|climat|emisi|emission/i, 'build', 'energia'], [/trabaj|work|employ|labor|empleo/i, 'build', 'trabajo']
  ];
  var VISTAS = {}, VETO = /\b(rally|protest|demonstrat|placard|signs?\b|banner|poster|graffiti|weapon|guns?\b|sword|knife|blood|cigar|smok|alcohol|beer|wine|drunk|politic|flag|police|military|text|words?\b|quote|newspaper|skull)/i;
  function h(s) { var x = 2166136261; s = String(s || ''); for (var i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; }
  function foto(mundo, texto, ancho) {
    if (!idx) return null;
    var t = String(texto || ''), m = null, tema = null;
    for (var i = 0; i < CLAVES.length; i++) if (CLAVES[i][0].test(t)) { m = CLAVES[i][1]; tema = CLAVES[i][2]; break; }
    var lista = m && idx[m] && idx[m][tema];
    if (!lista || !lista.length) {   // sin tema reconocible: cualquier foto del mundo (o general), siempre la misma para el mismo texto
      var mm = idx[mundo] || idx.general || {}; lista = [];
      Object.keys(mm).forEach(function (k) { if (k !== 'textura') lista = lista.concat(mm[k]); });   // las texturas lisas no sirven de foto principal
    }
    if (!lista.length) return null;
    var i0 = h(t + mundo) % lista.length, k = 0, x = lista[i0], w = (ancho || 640) > 800 ? 1600 : 640;
    while (k < lista.length && (VISTAS[x.r || x.p] || VETO.test(x.t || '')) && (VISTAS[x.r || x.p] !== t)) { k++; x = lista[(i0 + k) % lista.length]; }   // no repetir foto en la misma página
    VISTAS[x.r || x.p] = t;
    if (x.r) return x.r + '?w=' + w + '&h=' + Math.round(w * .625) + '&fit=crop&q=70&auto=format';
    return 'https://images.pexels.com/photos/' + x.p + '/pexels-photo-' + x.p + '.jpeg?auto=compress&cs=tinysrgb&w=' + w + '&h=' + Math.round(w * .625) + '&fit=crop';
  }
  w.AurzaneBanco = { foto: foto, listo: function (f) { if (idx) f(); else cola.push(f); } };
  try {
    fetch(INDICE).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (!j) return; idx = j; cola.splice(0).forEach(function (f) { try { f(); } catch (e) {} }); }).catch(function () {});
  } catch (e) {}
})(window, document);
/* Research Hub: cada paper lleva una foto del banco acorde a su tema (antes la misma miniatura para todo un mundo) */
(function (d) {
  function fotos() {
    var l = d.getElementById('list'); if (!l || !window.AurzaneBanco) return;
    var M = { mind: 1, nexus: 1, live: 1, learn: 1, build: 1 };
    [].forEach.call(l.querySelectorAll('.paper:not([data-v4f])'), function (p) {
      var mu = ((p.getAttribute('style') || '').match(/--(mind|nexus|live|learn|build)\)/) || [])[1] || 'general';
      var t = ((p.querySelector('h3') || {}).textContent || '') + ' ' + ((p.querySelector('.abstract') || {}).textContent || '').slice(0, 300);
      var u = window.AurzaneBanco.foto(M[mu] ? mu : 'general', t, 640); if (!u) return;
      p.style.setProperty('--img', 'url("' + u + '")'); p.setAttribute('data-v4f', '1');
    });
  }
  function iniciar() {
    var l = d.getElementById('list'); if (!l) return;
    window.AurzaneBanco && window.AurzaneBanco.listo(fotos);
    try { new MutationObserver(function () { fotos(); }).observe(l, { childList: true }); } catch (e) {}
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document);
/* Research Hub con ?mundo=: es la biblioteca de ese mundo (las bibliotecas de cada mundo redirigen aquí). Título y foto del mundo. */
(function (d) {
  if (!/\/research\.html$/.test(location.pathname)) return;
  var m = (new URLSearchParams(location.search).get('mundo') || '').toLowerCase();
  var N = { mind: 'MIND', nexus: 'NEXUS', live: 'LIVE', learn: 'LEARN', build: 'BUILD' };
  var F = { mind: '1559757175-5700dde675bc', nexus: '1541339907198-e08756dedf3f', live: '1454496522488-7a8e488e8606', learn: '1481627834876-b7833e8f5570', build: '1461360370896-922624d12aa1' };
  if (!N[m]) return;
  function poner() {
    var h = d.querySelector('.hero-wrap'); if (h) h.style.setProperty('--v4-rh-foto', 'url("https://images.unsplash.com/photo-' + F[m] + '?q=70&w=2000&auto=format&fit=crop")');
    var t = d.querySelector('.hero-wrap h1'); if (t && !t.hasAttribute('data-v4')) { t.setAttribute('data-v4', '1'); t.innerHTML = 'Biblioteca científica de <span>' + N[m] + '</span>'; }
    var pp = d.querySelector('.hero-wrap .hero p'); if (pp && !pp.hasAttribute('data-v4')) { pp.setAttribute('data-v4', '1'); pp.textContent = 'Los papers de acceso abierto de ' + N[m] + ': título, resumen oficial y enlace directo a la fuente. Puedes buscar también en los otros cuatro mundos.'; }
    if (!/Biblioteca de /.test(d.title)) d.title = 'Biblioteca científica de ' + N[m] + ' | AURZANE';
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', poner); else poner();
})(document);
/* Tarjetas de ejercicios y herramientas sin foto (a.scard): foto real del banco según el ejercicio, arriba de la tarjeta */
(function (d) {
  function poner() {
    if (!window.AurzaneBanco) return;
    [].forEach.call(d.querySelectorAll('a.scard:not(.az-cf):not([data-v4f])'), function (a) {
      var cm = (d.documentElement.className.match(/az-ds-(mind|nexus|live|learn|build|ovp)/) || [])[1] || 'general';   // el mundo de la página decide el banco
      var t = (a.textContent || '') + ' ' + (a.getAttribute('data-obj') || '') + (cm === 'mind' ? ' meditación calma' : '');
      var u = window.AurzaneBanco.foto(cm, t, 640); if (!u) return;
      var im = d.createElement('img'); im.className = 'v4-foto'; im.src = u; im.alt = ''; im.loading = 'lazy'; im.width = 640; im.height = 400;
      a.insertBefore(im, a.firstChild); a.setAttribute('data-v4f', '1');
    });
  }
  function iniciar() { if (d.querySelector('a.scard') && window.AurzaneBanco) window.AurzaneBanco.listo(poner); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document);
/* OVP: cada instrumento con una foto real del banco (orientación, estudiantes, estudio) */
(function (d) {
  if (!/(^|\.)ovp\.aurzane\.com$/.test(location.hostname)) return;
  var T = ['orientación vocacional carrera', 'estudiantes universidad', 'autoestima confianza', 'estudiar hábitos aula', 'concentración atención memoria', 'graduación carrera universidad'];
  function poner() {
    [].forEach.call(d.querySelectorAll('.instrumento:not([data-v4f])'), function (el, i) {
      var u = window.AurzaneBanco && window.AurzaneBanco.foto('nexus', T[i % T.length] + ' ' + el.textContent.slice(0, 80), 640); if (!u) return;
      var im = d.createElement('img'); im.className = 'v4-foto'; im.src = u; im.alt = ''; im.loading = 'lazy'; im.width = 640; im.height = 360;
      el.insertBefore(im, el.firstChild); el.setAttribute('data-v4f', '1');
    });
  }
  function iniciar() { if (window.AurzaneBanco) window.AurzaneBanco.listo(poner); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document);
/* Calculadoras: el panel del formulario se estira hasta el del resultado y rellena el hueco con la foto de la portada */
(function (d) {
  function poner(n) {
    var app = d.querySelector('.app'), hv = d.querySelector('[data-v4-foto]');
    var f = hv && (hv.style.getPropertyValue('--v4-foto') || getComputedStyle(hv).getPropertyValue('--v4-foto'));
    var fo = app && app.querySelector(':scope > .panel:not(.res)'), re = app && app.querySelector(':scope > .res');
    if (app && f && f.trim() && fo && re) {   // solo si al formulario le sobra hueco frente al resultado
      if (re.offsetHeight - fo.offsetHeight > 140) { app.style.setProperty('--v4-app-foto', f.trim()); app.classList.add('v4-app-foto'); return; } }
    if (n < 20) setTimeout(function () { poner(n + 1); }, 300);
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', function () { poner(0); }); else poner(0);
})(document);
/* Páginas informativas y legales: cada una con su propia foto en la columna lateral (del catálogo, según el título) */
(function (d) {
  function poner() {
    var m = d.querySelector('body > div.h ~ main.w'); if (!m || d.querySelector('.ficha, .rt') || !window.AurzaneBanco) return;
    window.AurzaneBanco.listo(function () {
      var t = (d.querySelector('body > div.h h1') || {}).textContent || d.title;
      var f = window.AurzaneBanco.foto('general', t + ' ' + location.pathname, 900); if (f) m.style.setProperty('--v4-info-foto', 'url("' + f + '")');
    });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', poner); else poner();
})(document);
/* Tarjetas con la misma foto repetida en una página (artículos que comparten imagen, etc.): la repetida se cambia por otra del catálogo según su texto */
(function (d) {
  function base(u) { return String(u || '').split('?')[0]; }
  function quitar() {
    if (!window.AurzaneBanco) return;
    window.AurzaneBanco.listo(function () {
      var vistas = {}, cm = (d.documentElement.className.match(/az-ds-(mind|nexus|live|learn|build|ovp)/) || [0, 'general'])[1];
      [].forEach.call(d.querySelectorAll('main img, .wrap img, section img'), function (im) {
        var b = base(im.currentSrc || im.src); if (!b || /logo|portada|cover|avatar|icon/i.test(b + ' ' + im.className)) return;
        var card = im.closest('a, article, li'); if (!card || im.closest('.libro, .portada, .rp, .book')) return;
        var r = im.getBoundingClientRect(); if (r.width && r.width < 120) return;
        if (!vistas[b]) { vistas[b] = 1; return; }
        var m = (card.getAttribute('href') || '').match(/(mind|nexus|live|learn|build)\.aurzane|mundo=(mind|nexus|live|learn|build)/);
        var u = window.AurzaneBanco.foto(m ? (m[1] || m[2]) : cm, (card.textContent || '').slice(0, 220), 640);
        if (u && !vistas[base(u)]) { vistas[base(u)] = 1; im.removeAttribute('srcset'); im.src = u; }
      });
    });
  }
  function ir() { quitar(); setTimeout(quitar, 2500); }   // también tras cargar las tarjetas que llegan por JS
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', ir); else ir();
})(document);

(function (w, d) {
  'use strict';
  if (w.AurzanePaleta) return;
  var PALETAS = {
    moca:      { nombre: 'Moca', n950: '#2D2F2C', n900: '#393B38', n800: '#525450', n700: '#60625E', gold: '#C7B99B', goldLight: '#DBCFB7', goldDeep: '#525450',
                 muestra: 'linear-gradient(135deg,#525450 0 58%,#1F7A70 58% 100%)', nuevo: true },
    dorado:    { nombre: 'Dorado clásico', n950: '#141C19', n900: '#12251F', n800: '#152C24', n700: '#19332B', gold: '#C7B99B', goldLight: '#DDD1B9', goldDeep: '#7C6E52' },
    aurora:    { nombre: 'Aurora', n950: '#0E1F19', n900: '#12251F', n800: '#142C24', n700: '#19322A', gold: '#FF8F70', goldLight: '#FFC38A', goldDeep: '#C2456E',
                 grad: 'linear-gradient(90deg,#CFC3AB,#FF7A9C,#A35BE0)' },
    esmeralda: { nombre: 'Esmeralda',      n950: '#071510', n900: '#0D1F19', n800: '#132B22', n700: '#1B3A2E', gold: '#4BA97C', goldLight: '#8FE0BB', goldDeep: '#1F6B4A' },
    purpura:   { nombre: 'Púrpura real',   n950: '#131E1A', n900: '#12251F', n800: '#142C24', n700: '#1A342B', gold: '#9A7DD1', goldLight: '#C9B4EE', goldDeep: '#5B3F94' },
    grafito:   { nombre: 'Grafito plata',  n950: '#0A0B09', n900: '#131411', n800: '#1B1C18', n700: '#252724', gold: '#BDBEBB', goldLight: '#E9E4DB', goldDeep: '#6F706D' },
    cobre:     { nombre: 'Cobre rosa',     n950: '#150B0C', n900: '#211215', n800: '#2E181C', n700: '#3D2126', gold: '#C97D6B', goldLight: '#E8AE9F', goldDeep: '#7A4436' }
  };
  var CLAVE = 'aurzane-paleta';
  var html = d.documentElement;

  function leerCookie() {
    var m = d.cookie.match(/(?:^|; )aurzane-paleta=([^;]*)/);
    return m ? decodeURIComponent(m[1]) : null;
  }
  function guardar(clave) {
    try {
      var dominio = /(^|\.)aurzane\.com$/.test(location.hostname) ? 'domain=.aurzane.com; ' : '';
      d.cookie = CLAVE + '=' + encodeURIComponent(clave) + '; ' + dominio + 'path=/; max-age=31536000; samesite=lax' + (location.protocol === 'https:' ? '; secure' : '');
    } catch (e) {}
    try { localStorage.setItem(CLAVE, clave); } catch (e) {}
  }
  function leer() {
    var c = leerCookie();
    if (!c) { try { c = localStorage.getItem(CLAVE); } catch (e) {} }
    return PALETAS[c] ? c : 'dorado';
  }
  function rgb(hex) {
    var h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)].join(',');
  }
  var VARS = ['--navy-950', '--navy-900', '--navy-800', '--navy-700', '--navy', '--navy-2', '--navy-3', '--navy-4',
    '--gold', '--gold-light', '--gold-deep', '--gold-rgb', '--accent', '--accent-light', '--accent-dark', '--accent-dim', '--acento-grad'];

  function aplicar(clave, persistir) {
    var p = PALETAS[clave] || PALETAS.dorado, s = html.style;
    // La paleta por defecto deja intacto el diseño propio de cada página.
    VARS.forEach(function (v) { s.removeProperty(v); });
    if (clave !== 'dorado') {
      s.setProperty('--navy-950', p.n950); s.setProperty('--navy-900', p.n900);
      s.setProperty('--navy-800', p.n800); s.setProperty('--navy-700', p.n700);
      s.setProperty('--navy', p.n950); s.setProperty('--navy-2', p.n900);
      s.setProperty('--navy-3', p.n800); s.setProperty('--navy-4', p.n700);
      s.setProperty('--gold', p.gold); s.setProperty('--gold-light', p.goldLight);
      s.setProperty('--gold-deep', p.goldDeep); s.setProperty('--gold-rgb', rgb(p.gold));
      s.setProperty('--accent', p.gold); s.setProperty('--accent-light', p.goldLight);
      s.setProperty('--accent-dark', p.goldDeep); s.setProperty('--accent-dim', 'rgba(' + rgb(p.gold) + ',.14)');
      s.setProperty('--acento-grad', p.grad || p.gold);
    }
    Object.keys(PALETAS).forEach(function (k) { html.classList.toggle('paleta-' + k, k === clave); });
    if (persistir) guardar(clave);
    var sws = d.querySelectorAll('.paleta-swatch[data-clave], .azp-sw[data-clave]');
    for (var i = 0; i < sws.length; i++) {
      var on = sws[i].getAttribute('data-clave') === clave;
      sws[i].classList.toggle('activo', on);
      sws[i].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
    w.__aurzanePaleta = clave;
  }

  // Estilos extra: botones con degradado en Aurora y el selector flotante.
  var css = [
    'html.paleta-aurora .btn-gold,html.paleta-aurora .btn.btn-gold,html.paleta-aurora .btn-primary,html.paleta-aurora .btn.btn-primary{background:linear-gradient(90deg,#CFC3AB,#FF7A9C)!important;color:#12251F!important;border-color:transparent!important}',
    '.azp-btn{position:fixed;left:16px;bottom:16px;z-index:9990;width:46px;height:46px;border-radius:50%;border:0;padding:0;cursor:pointer;background:conic-gradient(#CFC3AB,#FF7A9C,#A35BE0,#5B7CFA,#2FB37F,#C7B99B,#CFC3AB);box-shadow:0 10px 24px -8px rgba(0,0,0,.5);display:grid;place-items:center;transition:transform .15s}',
    '.azp-btn:hover{transform:scale(1.07)} .azp-btn span{width:36px;height:36px;border-radius:50%;background:#12251F;display:grid;place-items:center;font-size:18px;line-height:1}',
    '.azp-btn:focus-visible,.azp-sw:focus-visible{outline:3px solid #CFC3AB;outline-offset:3px}',
    '.azp-pop{position:fixed;left:16px;bottom:72px;z-index:9991;width:248px;background:#12251F;color:#F5F3EE;border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:14px;box-shadow:0 20px 50px -15px rgba(0,0,0,.6);font:500 14px/1.4 "Instrument Sans",system-ui,sans-serif}',
    '.azp-pop[hidden]{display:none!important} .azp-pop b{display:block;font-size:14px;margin:0 0 10px} .azp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}',
    '.azp-sw{display:flex;flex-direction:column;align-items:center;gap:5px;background:none;border:1px solid transparent;border-radius:12px;padding:8px 4px;color:inherit;font:inherit;font-size:11.5px;cursor:pointer}',
    '.azp-sw i{width:30px;height:30px;border-radius:50%;box-shadow:0 0 0 1px rgba(255,255,255,.18)} .azp-sw.activo{border-color:rgba(255,255,255,.45);background:rgba(255,255,255,.06)}',
    '.azp-sw small{font-size:9.5px;font-weight:700;color:#12251F;background:linear-gradient(90deg,#CFC3AB,#FF7A9C);border-radius:99px;padding:0 6px}',
    '.paleta-swatch[data-clave="aurora"]{background:linear-gradient(135deg,#CFC3AB,#FF7A9C,#A35BE0)!important}',
    '.paleta-swatch[data-clave="moca"]{background:linear-gradient(135deg,#525450 0 58%,#1F7A70 58% 100%)!important}',
    '@media print{.azp-btn,.azp-pop{display:none!important}}'
  ].join('\n');

  // El blanco no se queda solo: en modo claro con la paleta por defecto (o con Moca), los fondos y textos
  // se combinan con el tono moca #525450. Con las demás paletas y en modo oscuro todo queda como siempre.
  // Solo en páginas claras (clase az-claro, que se decide al cargar); el test de personalidad conserva sus colores.
  var cssBase = [
    'html.az-claro:is(.paleta-dorado,.paleta-moca):not([data-tema="oscuro"]){--vanilla:#F2F1ED;--bg:#F2F1ED;--surface:#FFFCF8;--surface-2:#E9E4DB;--surface-3:#DFDDD6;--text:#252724;--paper-ink:#252724;--ink:#252724;--text-dim:#636561;--border:rgba(82,84,80,.18);--line:rgba(82,84,80,.16)}',
    'html[class*="paleta-"]:not(.paleta-dorado){--n1:var(--navy-900);--n2:var(--navy-700);--n3:var(--gold-deep);--cian:var(--gold-light);--violeta:var(--gold)}',
    'html.az-claro:is(.paleta-dorado,.paleta-moca):not([data-tema="oscuro"]){--accent-text:#525450}',
    'html.paleta-moca:not([data-tema="oscuro"]) :is(.btn-gold,.btn.btn-gold,.btn-primary,.btn.btn-primary,.btn-luz,.cta-final){background:#1F7A70!important;color:#fff!important;border-color:transparent!important;box-shadow:0 10px 24px -12px rgba(31,122,112,.65)}',
    'html.paleta-moca:not([data-tema="oscuro"]) :is(.btn-gold,.btn-primary,.btn-luz,.cta-final):hover{background:#17655C!important}',
    // Un solo color de acción por pantalla: el botón principal va relleno y los secundarios, en contorno del mismo color (jerarquía clara, efecto de aislamiento).
    'html.az-claro:is(.paleta-dorado,.paleta-moca):not([data-tema="oscuro"]) .btn-osc{background:transparent!important;color:var(--acento-texto,#525450)!important;border:2px solid currentColor!important;box-shadow:none!important}',
    'html.paleta-moca:not([data-tema="oscuro"]) .btn-osc{background:transparent!important;color:#1F7A70!important;border:2px solid #1F7A70!important;box-shadow:none!important}',
    'html.paleta-moca:not([data-tema="oscuro"]) .btn-osc:hover{background:rgba(31,122,112,.08)!important}',
    // Botones de acción: tamaño táctil mínimo de 44 px, respuesta al pasar el ratón y foco visible para teclado (en todas las paletas, sin cambiar sus colores).
    ':is(.btn-gold,.btn-primary,.btn-luz,.cta-final){min-height:44px;transition:transform .15s ease,box-shadow .15s ease,background-color .15s ease}',
    ':is(.btn-gold,.btn-primary,.btn-luz,.cta-final):hover{transform:translateY(-1px)}',
    ':is(.btn-gold,.btn-primary,.btn-luz,.btn-osc,.cta-final,.btn-ghost,.btn-linea):focus-visible{outline:3px solid #1F7A70;outline-offset:3px}',
    'html[data-tema="oscuro"] :is(.btn-gold,.btn-primary,.btn-luz,.btn-osc,.cta-final,.btn-ghost,.btn-linea):focus-visible{outline-color:#DBCFB7}',
    '@media (prefers-reduced-motion:reduce){:is(.btn-gold,.btn-primary,.btn-luz,.cta-final){transition:none}:is(.btn-gold,.btn-primary,.btn-luz,.cta-final):hover{transform:none}}'
  ].join('\n');
  try { var stB = d.createElement('style'); stB.id = 'azp-base'; stB.textContent = cssBase; (d.head || html).appendChild(stB); } catch (e) {}

  // ¿Es una página clara? (tiene modo claro/oscuro, o su fondo es claro)
  function detectarClaro() {
    if (/\/test-de-personalidad\//.test(location.pathname) || d.querySelector('[data-sin-moca]')) { html.classList.remove('az-claro'); return; }
    var tieneTema = false;
    try {
      for (var i = 0; i < d.styleSheets.length && !tieneTema; i++) {
        var r; try { r = d.styleSheets[i].cssRules; } catch (e) { continue; }
        for (var j = 0; j < r.length; j++) { if (r[j].selectorText && r[j].selectorText.indexOf('data-tema="oscuro"') >= 0 && r[j].selectorText.indexOf(':root') >= 0) { tieneTema = true; break; } }
      }
    } catch (e) {}
    var claro = tieneTema;
    if (!claro && html.getAttribute('data-tema') !== 'oscuro' && d.body) {
      var m = getComputedStyle(d.body).backgroundColor.match(/\d+(\.\d+)?/g);
      if (m && (m.length < 4 || +m[3] > 0)) { claro = (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255 > 0.75; }
    }
    html.classList.toggle('az-claro', claro);
  }

  function muestra(k) { return PALETAS[k].muestra || (PALETAS[k].grad ? 'linear-gradient(135deg,#CFC3AB,#FF7A9C,#A35BE0)' : PALETAS[k].gold); }

  function montarUI() {
    detectarClaro();
    var st = d.createElement('style'); st.textContent = css; d.head.appendChild(st);
    var actual = leer();
    var paneles = d.querySelectorAll('#paletaSwatches, .paleta-swatches');
    Array.prototype.forEach.call(paneles, function (panel) {
      panel.innerHTML = Object.keys(PALETAS).map(function (k) {
        return '<button type="button" class="paleta-swatch" data-clave="' + k + '" style="background:' + muestra(k) + '" title="' + PALETAS[k].nombre + '" aria-label="' + PALETAS[k].nombre + '"></button>';
      }).join('');
      panel.addEventListener('click', function (e) {
        var b = e.target.closest('[data-clave]'); if (b) aplicar(b.getAttribute('data-clave'), true);
      });
    });
    if (!d.querySelector('[data-sin-paleta]')) {
      var btn = d.createElement('button');
      btn.type = 'button'; btn.className = 'azp-btn'; btn.setAttribute('aria-label', 'Elegir el color de AURZANE');
      btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'azpPop'); btn.title = 'Elegir color';
      btn.innerHTML = '<span aria-hidden="true">🎨</span>';
      var pop = d.createElement('div');
      pop.className = 'azp-pop'; pop.id = 'azpPop'; pop.hidden = true; pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', 'Color de AURZANE');
      pop.innerHTML = '<b>Elige el color de AURZANE</b><div class="azp-grid">' + Object.keys(PALETAS).map(function (k) {
        return '<button type="button" class="azp-sw" data-clave="' + k + '" aria-pressed="false"><i style="background:' + muestra(k) + '"></i>' + PALETAS[k].nombre + (PALETAS[k].nuevo ? ' <small>Nuevo</small>' : '') + '</button>';
      }).join('') + '</div>';
      var cuerpo = d.body || d.documentElement; if (!cuerpo) return;
      cuerpo.appendChild(pop); cuerpo.appendChild(btn);
      btn.addEventListener('click', function () {
        pop.hidden = !pop.hidden; btn.setAttribute('aria-expanded', String(!pop.hidden));
      });
      pop.addEventListener('click', function (e) {
        var b = e.target.closest('[data-clave]'); if (b) aplicar(b.getAttribute('data-clave'), true);
      });
      d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !pop.hidden) { pop.hidden = true; btn.setAttribute('aria-expanded', 'false'); btn.focus(); } });
      d.addEventListener('click', function (e) { if (!pop.hidden && !pop.contains(e.target) && !btn.contains(e.target)) { pop.hidden = true; btn.setAttribute('aria-expanded', 'false'); } });
    }
    aplicar(actual, false);
  }

  // Compatibilidad con el código antiguo de las páginas (aplicarPaleta / PALETAS).
  w.PALETAS = PALETAS;
  w.aplicarPaleta = function (clave) { aplicar(clave, true); };
  w.AurzanePaleta = { PALETAS: PALETAS, aplicar: function (k) { aplicar(k, true); }, actual: leer };

  aplicar(leer(), false); // lo antes posible, sin parpadeo
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', montarUI); else montarUI();
})(window, document);

/* Buzón de reportes en todos los mundos */
(function (d) {
  if (window.AurzaneReportar || d.querySelector('script[data-azr]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-reportes.js?v=h76845e41'; s.defer = true; s.setAttribute('data-azr', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* Selector de idioma en todos los mundos */
(function (d) {
  if (window.AurzaneIdiomas || d.querySelector('script[data-azi]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-idiomas.js?v=h709aab54'; s.defer = true; s.setAttribute('data-azi', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* AURZANE AI · asistente de resultados en los tests de MIND y LIVE */
(function (d) {
  if (!/^(mind|live)\.aurzane\.com$/.test(location.hostname) || d.querySelector('script[data-azasis]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-asistente.js?v=h7558509f'; s.defer = true; s.setAttribute('data-azasis', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* Tu siguiente paso: al terminar un test, tres pasos con sentido (otro test, una práctica y un curso u orientación) */
(function (d) {
  if (!/^(mind|live)\.aurzane\.com$/.test(location.hostname) || !/\/test-de-/.test(location.pathname) || d.querySelector('script[data-azruta]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-ruta.js?v=h363bee0a'; s.defer = true; s.setAttribute('data-azruta', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* AURZANE AI · artículos recientes en cada mundo y explicación de qué te llevas en cada test */
(function (d) {
  var h = location.hostname, p = location.pathname;
  if (!(/^(mind|live|learn|nexus|build)\.aurzane\.com$/.test(h) || (h === 'aurzane.com' && /^\/(articulos(\/[^/]*)?\/?(index\.html)?|research(\.html)?\/?)$/.test(p))) || d.querySelector('script[data-azcont]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-contenido.js?v=hbe5867d8'; s.defer = true; s.setAttribute('data-azcont', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* AURZANE AI · aviso de errores de JavaScript (sin datos personales: página, mensaje, archivo y línea) */
(function (w) {
  if (w.__azErr || !/(^|\.)aurzane\.com$/.test(location.hostname) || !navigator.sendBeacon) return;
  w.__azErr = 1; var n = 0, vistos = {};
  function enviar(t, m, s, l) {
    m = String(m || '').slice(0, 300); s = String(s || '').slice(0, 200);
    if (n >= 5 || !m || m === 'Script error.' || /extension:\/\/|^chrome:|translate\.goog|googletag|adsbygoogle|pagead/.test(s + m)) return;
    var k = m + s + l; if (vistos[k]) return; vistos[k] = 1; n++;
    try { navigator.sendBeacon('https://aurzane.com/ai/registro.php', new Blob([JSON.stringify({ h: location.hostname, p: location.pathname, t: t, m: m, s: s, l: l || 0 })], { type: 'text/plain' })); } catch (e) {}
  }
  w.addEventListener('error', function (e) { if (e && e.message) enviar('error', e.message, e.filename, e.lineno); });
  w.addEventListener('unhandledrejection', function (e) { var r = e && e.reason; enviar('promesa', r && (r.message || r), r && r.stack && String(r.stack).split('\n')[1], 0); });
})(window);

/* AURZANE · un solo botón de opciones: idioma, reportar un problema y colores quedan recogidos en «⋯» para no tapar el contenido */
(function (d) {
  if (d.getElementById('azDockCss')) return;
  var st = d.createElement('style'); st.id = 'azDockCss';
  st.textContent =
    '.az-dock{position:fixed;left:14px;bottom:14px;z-index:9995;width:40px;height:40px;border-radius:50%;border:1px solid rgba(255,255,255,.28);background:rgba(18,37,31,.86);color:#F5F3EE;font:700 18px/1 system-ui,sans-serif;cursor:pointer;display:grid;place-items:center;box-shadow:0 8px 20px -8px rgba(0,0,0,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}' +
    '.az-dock:focus-visible{outline:2px solid #C7B99B;outline-offset:2px}' +
    'html:not(.az-dock-abierto) .azp-btn,html:not(.az-dock-abierto) .azi-btn,html:not(.az-dock-abierto) .azr-btn,html:not(.az-dock-abierto) .azr-tip{opacity:0!important;pointer-events:none!important;transform:translateY(10px) scale(.85)!important}' +
    '.azp-btn,.azi-btn,.azr-btn{transition:opacity .18s,transform .18s!important;width:40px!important;height:40px!important;left:14px!important}' +
    '.azp-btn{bottom:62px!important}.azr-btn{bottom:110px!important}.azi-btn{bottom:158px!important}' +
    '.azp-pop{bottom:62px!important;left:62px!important}' +
    '@media (prefers-reduced-motion:reduce){.azp-btn,.azi-btn,.azr-btn{transition:none!important}}@media print{.az-dock{display:none!important}}';
  (d.head || d.documentElement).appendChild(st);
  function poner() {
    if (!d.body || d.querySelector('.az-dock')) return;
    var b = d.createElement('button'); b.type = 'button'; b.className = 'az-dock'; b.textContent = '⋯';
    b.setAttribute('aria-label', 'Opciones: idioma, colores y reportar un problema'); b.setAttribute('aria-expanded', 'false'); b.title = 'Idioma, colores y reportar un problema';
    b.addEventListener('click', function () { var a = d.documentElement.classList.toggle('az-dock-abierto'); b.setAttribute('aria-expanded', a); b.textContent = a ? '×' : '⋯'; });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.documentElement.classList.contains('az-dock-abierto')) b.click(); });
    d.body.appendChild(b);
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', poner); else poner();
})(document);

/* Capa visual común: color propio de cada mundo, panel «Empieza por aquí», logo e icono */
(function (d) {
  if (window.AurzaneEstilo || d.querySelector('script[data-azest]')) return;
  /* diferido: escrito en la cabecera retrasaba la primera pintura (PageSpeed, 16/11/2026) */
  var src = 'https://aurzane.com/aurzane-estilo.js?v=h5de5daa9';
  var s = d.createElement('script');
  s.src = src; s.defer = true; s.setAttribute('data-azest', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* Hueco reservado para la cabecera común mientras carga aurzane-ds.js (16/11/2026).
   La cabecera se inserta al terminar de leer la página; sin hueco, todo el contenido bajaba de golpe (CLS de 0,1 a 0,5).
   Aquí se ocultan ya las barras antiguas que la cabecera sustituye y se reserva su alto exacto (53 px, o 102 px con la
   fila del mundo en pantallas de más de 900 px). Si la cabecera no llega en 5 s, se deshace y la página queda como estaba. */
(function (d, w) {
  var h = location.hostname;
  if (!/(^|\.)aurzane\.com$/.test(h)) return;
  var mundo = /^(www\.)?aurzane\.com$/.test(h) ? 'aurzane' : h.split('.')[0], ruta = location.pathname;
  if (mundo === 'learn' && /^\/cursos\.html$/.test(ruta)) return;
  if (window.__azEmbed) return;
  var portada = mundo === 'aurzane' && /^\/(index\.html)?$/.test(ruta);
  var sinFila = mundo === 'aurzane' && !/^\/(biblioteca|libros|articulos|articulos-ai|research|frases|novedades|temas|mapa)\b/.test(ruta);
  var viejas = ['body > .utility', '.utility[data-nosnippet]', '#utilityBar', 'body > header.topbar', 'body > header.top', 'body > .w > nav.top', 'header.principal', '.btn-todo'];
  if (!/^\/research(\.html)?$/.test(ruta)) viejas.push('body > div.topbar:has(.brand)');
  viejas.push('body > header:not([class]):has(> .w > .logo)');
  var P = 'html.az-pre:not(.az-ds) ';
  var css = viejas.map(function (s) { return P + s; }).join(',') + '{display:none!important}' +
    P + 'body::before{content:"";display:block;height:53px}' +
    (!portada && !sinFila ? '@media (min-width:901px){' + P + 'body::before{height:102px}}' : '') +
    /* cifras que llegan después (NEXUS): ancho fijo para que al rellenarse no recoloquen la cabecera */
    '#statArticulos,#statBiblioteca{display:inline-block;min-width:6ch}' +
    /* tests y calculadoras en tableta: hueco para la ficha con foto que añade aurzane-estilo.js (en el móvil no se añade), así nada salta al cargar */
    '@media (min-width:700px) and (max-width:1099px){html.az-calc:not(.az-con-portada) .hero>.wrap::after{content:"";display:block;height:192px}}';
  if (/^\/(test-de-|calculadora-)/.test(ruta) && !/^\/test-de-personalidad/.test(ruta)) d.documentElement.classList.add('az-calc');
  /* portada de cada mundo: su foto de cabecera se pide ya (era el LCP y llegaba tarde) y su maquetación se aplica desde el principio */
  var FOTO = { mind: '1559757175-5700dde675bc', nexus: '1518770660439-4636190af475', live: '1454496522488-7a8e488e8606', learn: '1481627834876-b7833e8f5570', build: '1461360370896-922624d12aa1', ovp: '1523240795612-9a054b0db644' };
  if (mundo !== 'aurzane' && /^\/(index\.html)?$/.test(ruta)) {
    d.documentElement.classList.add('az-ds-' + mundo, 'az-pm');
    if (FOTO[mundo]) [['(max-width:760px)', 900], ['(min-width:761px)', 1600]].forEach(function (m) {
      var k = d.createElement('link'); k.rel = 'preload'; k.as = 'image'; k.media = m[0]; k.setAttribute('fetchpriority', 'high');
      k.href = 'https://images.unsplash.com/photo-' + FOTO[mundo] + '?w=' + m[1] + '&q=70&auto=format&fit=crop'; (d.head || d.documentElement).appendChild(k);
    });
  }
  try { var st = d.createElement('style'); st.setAttribute('data-azpre', '1'); st.textContent = css; (d.head || d.documentElement).appendChild(st); d.documentElement.classList.add('az-pre'); } catch (e) { return; }
  setTimeout(function () { if (!d.documentElement.classList.contains('az-ds')) d.documentElement.classList.remove('az-pre'); }, 5000);
})(document, window);

/* Sistema de diseño compartido: barra común del ecosistema, buscador global (Ctrl+K) y base accesible */
(function (d) {
  if (d.querySelector('link[data-azds]') || !/(^|\.)aurzane\.com$/.test(location.hostname)) return;
  /* la hoja común se escribe en el documento mientras se lee la cabecera: así se aplica antes de pintar y la página
     no cambia de aspecto ni salta cuando llega (16/11/2026); si la página ya está leída, se añade como antes */
  var css = 'https://aurzane.com/aurzane-ds.css?v=hcc5174f5';
  if (d.readyState === 'loading' && d.currentScript && d.currentScript.parentNode === d.head) d.write('<link rel="stylesheet" href="' + css + '" data-azds="1">');
  else { var l = d.createElement('link'); l.rel = 'stylesheet'; l.href = css; l.setAttribute('data-azds', '1'); (d.head || d.documentElement).appendChild(l); }
  var s = d.createElement('script'); s.src = 'https://aurzane.com/aurzane-ds.js?v=hf2bf9f82'; s.defer = true; s.setAttribute('data-azds', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* Tests: la barra móvil «Ver resultado» aparece al bajar y lleva siempre al resultado (16/11/2026) */
(function (w, d) {
  function iniciar() {
    var barra = d.getElementById('movilBarra'), res = d.getElementById('resultado');
    if (!barra || !res || barra.__az) return; barra.__az = 1;
    var visible = function () { var r = res.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; };
    var poner = function () { barra.classList.toggle('ver', w.scrollY > 300 && !visible()); };
    w.addEventListener('scroll', poner, { passive: true }); w.addEventListener('resize', poner); poner();
    var a = barra.querySelector('a[href="#resultado"]');
    if (a) a.addEventListener('click', function (e) {
      e.preventDefault();
      var cab = d.querySelector('.az-cab'), alto = cab && getComputedStyle(cab).position === 'sticky' ? cab.offsetHeight : 0;
      w.scrollTo({ top: res.getBoundingClientRect().top + w.scrollY - alto - 12, behavior: 'smooth' });
      try { history.replaceState(null, '', '#resultado'); } catch (x) {}
      setTimeout(function () { res.setAttribute('tabindex', '-1'); res.focus({ preventScroll: true }); }, 500);
    });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
  setTimeout(iniciar, 2000);
})(window, document);

/* Medición sin cookies (16/11/2026): una vista por página y los clics que importan (socios, salidas, cambios de mundo).
   Solo se suman contadores en el servidor; no se guarda IP ni ningún identificador. */
(function (d, w) {
  if (w.__azMide || w.__azEmbed || navigator.webdriver || !/(^|\.)aurzane\.com$/.test(location.hostname)) return; w.__azMide = 1;
  var U = 'https://aurzane.com/ai/visitas.php';
  function envia(o) { try { var b = JSON.stringify(o); if (!(navigator.sendBeacon && navigator.sendBeacon(U, b))) fetch(U, { method: 'POST', body: b, keepalive: true, mode: 'no-cors' }); } catch (e) {} }
  var ref = ''; try { var r = d.referrer ? new URL(d.referrer).hostname : ''; ref = !r ? 'directo' : /aurzane\.com$/.test(r) ? '' : /google\./.test(r) ? 'google' : /bing\./.test(r) ? 'bing' : /facebook|fb\./.test(r) ? 'facebook' : /instagram/.test(r) ? 'instagram' : /t\.co$|twitter|x\.com/.test(r) ? 'x' : /tiktok/.test(r) ? 'tiktok' : /telegram|t\.me/.test(r) ? 'telegram' : /pinterest/.test(r) ? 'pinterest' : 'otros'; } catch (e) {}
  var base = { h: location.hostname.replace(/^www\./, ''), p: location.pathname };
  function vista() { envia({ h: base.h, p: base.p, o: ref }); }
  if (d.visibilityState === 'prerender') d.addEventListener('visibilitychange', vista, { once: true }); else vista();
  d.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest && ev.target.closest('a[href]'); if (!a) return;
    var u; try { u = new URL(a.href, location.href); } catch (e) { return; }
    var e = '';
    if (a.closest('.az-socio')) e = 'socio:' + (a.closest('.az-socio').getAttribute('data-socio') || u.hostname.replace(/^www\./, ''));
    else if (!/aurzane\.com$/.test(u.hostname)) e = 'sale:' + u.hostname.replace(/^www\./, '');
    else if (u.hostname !== location.hostname) e = 'mundo:' + u.hostname.split('.')[0];
    if (e) envia({ h: base.h, p: base.p, e: e });
  }, true);
})(document, window);
