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
    if (!u || /og-portada|logo|portadas?\//i.test(u)) return;
    var cab = d.querySelector('main > .hero, section.hero, header.hero, .u-hero, .hero-wrap, .world-header, main > header:first-child'); if (!cab) return;
    var cs = getComputedStyle(cab); if (/url\(/.test(cs.backgroundImage)) return;
    var cols = ((cs.backgroundColor + ' ' + cs.backgroundImage).match(/rgba?\([^)]+\)/g) || []).map(function (x) { return x.replace(/rgba?\(|\)/g, '').split(/[ ,\/]+/).map(Number); })
      .filter(function (c) { return c.length < 4 || c[3] >= .5; });
    var c = cols[0]; if (!c) return;
    if (.2126 * c[0] + .7152 * c[1] + .0722 * c[2] > 90) return;   // solo cabeceras oscuras: el texto claro sigue legible
    cab.style.setProperty('--v4-foto', 'url("' + u.replace(/"/g, '%22') + '")'); cab.setAttribute('data-v4-foto', '1');
    d.documentElement.classList.add('az-v4-cabfoto');
  }
  if (d.readyState === 'complete') setTimeout(fotoCab, 300); else window.addEventListener('load', function () { setTimeout(fotoCab, 300); });
})(document);
/* Catálogo de imágenes (índice banco/banco.json en GitHub, servido por jsDelivr; las fotos salen del CDN de Pexels en AVIF, sin ocupar
   espacio en SiteGround): elige una foto real según el mundo y el tema del texto, distinta para cada texto.
   AurzaneBanco.foto(mundo, texto, ancho) devuelve la URL (o null si el índice aún no cargó); AurzaneBanco.listo(fn) avisa al cargar. */
(function (w, d) {
  if (w.AurzaneBanco) return;
  var idx = null, cola = [], INDICE = 'https://cdn.jsdelivr.net/gh/aurzane08-coder/aurzane-biblioteca-tareas@main/banco/banco.json';
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
  function h(s) { var x = 2166136261; s = String(s || ''); for (var i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; }
  function foto(mundo, texto, ancho) {
    if (!idx) return null;
    var t = String(texto || ''), m = null, tema = null;
    for (var i = 0; i < CLAVES.length; i++) if (CLAVES[i][0].test(t)) { m = CLAVES[i][1]; tema = CLAVES[i][2]; break; }
    var lista = m && idx[m] && idx[m][tema];
    if (!lista || !lista.length) {   // sin tema reconocible: cualquier foto del mundo (o general), siempre la misma para el mismo texto
      var mm = idx[mundo] || idx.general || {}; lista = [];
      Object.keys(mm).forEach(function (k) { lista = lista.concat(mm[k]); });
    }
    if (!lista.length) return null;
    var x = lista[h(t + mundo) % lista.length], w = (ancho || 640) > 800 ? 1600 : 640;
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
      var t = (a.textContent || '') + ' ' + (a.getAttribute('data-obj') || '') + ' meditación calma';
      var u = window.AurzaneBanco.foto('mind', t, 640); if (!u) return;
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
