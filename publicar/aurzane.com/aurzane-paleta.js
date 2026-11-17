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

(function (w, d) {
  'use strict';
  if (w.AurzanePaleta) return;
  var PALETAS = {
    moca:      { nombre: 'Moca', n950: '#352C25', n900: '#43382F', n800: '#5F5044', n700: '#6E5E50', gold: '#E2AE55', goldLight: '#F2C98A', goldDeep: '#5F5044',
                 muestra: 'linear-gradient(135deg,#5F5044 0 58%,#1F7A70 58% 100%)', nuevo: true },
    dorado:    { nombre: 'Dorado clásico', n950: '#080B17', n900: '#0F1530', n800: '#151C3D', n700: '#1E2650', gold: '#C9A24B', goldLight: '#EACF92', goldDeep: '#8A6A28' },
    aurora:    { nombre: 'Aurora', n950: '#0D0820', n900: '#150D33', n800: '#1F1347', n700: '#2A1660', gold: '#FF8F70', goldLight: '#FFC38A', goldDeep: '#C2456E',
                 grad: 'linear-gradient(90deg,#FFB347,#FF7A9C,#A35BE0)' },
    esmeralda: { nombre: 'Esmeralda',      n950: '#071510', n900: '#0D1F19', n800: '#132B22', n700: '#1B3A2E', gold: '#4BA97C', goldLight: '#8FE0BB', goldDeep: '#1F6B4A' },
    purpura:   { nombre: 'Púrpura real',   n950: '#0E0A1A', n900: '#171029', n800: '#211640', n700: '#2E1E58', gold: '#9A7DD1', goldLight: '#C9B4EE', goldDeep: '#5B3F94' },
    grafito:   { nombre: 'Grafito plata',  n950: '#0A0A0C', n900: '#131316', n800: '#1B1B20', n700: '#26262C', gold: '#B8BEC7', goldLight: '#E4E7EB', goldDeep: '#6B7078' },
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
    'html.paleta-aurora .btn-gold,html.paleta-aurora .btn.btn-gold,html.paleta-aurora .btn-primary,html.paleta-aurora .btn.btn-primary{background:linear-gradient(90deg,#FFB347,#FF7A9C)!important;color:#1B0B2E!important;border-color:transparent!important}',
    '.azp-btn{position:fixed;left:16px;bottom:16px;z-index:9990;width:46px;height:46px;border-radius:50%;border:0;padding:0;cursor:pointer;background:conic-gradient(#FFB347,#FF7A9C,#A35BE0,#5B7CFA,#2FB37F,#E3B23C,#FFB347);box-shadow:0 10px 24px -8px rgba(0,0,0,.5);display:grid;place-items:center;transition:transform .15s}',
    '.azp-btn:hover{transform:scale(1.07)} .azp-btn span{width:36px;height:36px;border-radius:50%;background:#150D33;display:grid;place-items:center;font-size:18px;line-height:1}',
    '.azp-btn:focus-visible,.azp-sw:focus-visible{outline:3px solid #FFB347;outline-offset:3px}',
    '.azp-pop{position:fixed;left:16px;bottom:72px;z-index:9991;width:248px;background:#150D33;color:#F5F3EE;border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:14px;box-shadow:0 20px 50px -15px rgba(0,0,0,.6);font:500 14px/1.4 "Instrument Sans",system-ui,sans-serif}',
    '.azp-pop[hidden]{display:none!important} .azp-pop b{display:block;font-size:14px;margin:0 0 10px} .azp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}',
    '.azp-sw{display:flex;flex-direction:column;align-items:center;gap:5px;background:none;border:1px solid transparent;border-radius:12px;padding:8px 4px;color:inherit;font:inherit;font-size:11.5px;cursor:pointer}',
    '.azp-sw i{width:30px;height:30px;border-radius:50%;box-shadow:0 0 0 1px rgba(255,255,255,.18)} .azp-sw.activo{border-color:rgba(255,255,255,.45);background:rgba(255,255,255,.06)}',
    '.azp-sw small{font-size:9.5px;font-weight:700;color:#1B0B2E;background:linear-gradient(90deg,#FFB347,#FF7A9C);border-radius:99px;padding:0 6px}',
    '.paleta-swatch[data-clave="aurora"]{background:linear-gradient(135deg,#FFB347,#FF7A9C,#A35BE0)!important}',
    '.paleta-swatch[data-clave="moca"]{background:linear-gradient(135deg,#5F5044 0 58%,#1F7A70 58% 100%)!important}',
    '@media print{.azp-btn,.azp-pop{display:none!important}}'
  ].join('\n');

  // El blanco no se queda solo: en modo claro con la paleta por defecto (o con Moca), los fondos y textos
  // se combinan con el tono moca #5F5044. Con las demás paletas y en modo oscuro todo queda como siempre.
  // Solo en páginas claras (clase az-claro, que se decide al cargar); el test de personalidad conserva sus colores.
  var cssBase = [
    'html.az-claro:is(.paleta-dorado,.paleta-moca):not([data-tema="oscuro"]){--vanilla:#F6F0E8;--bg:#F6F0E8;--surface:#FFFCF8;--surface-2:#EEE5DA;--surface-3:#E6DBCE;--text:#2E2620;--paper-ink:#2E2620;--ink:#2E2620;--text-dim:#6E6257;--border:rgba(95,80,68,.18);--line:rgba(95,80,68,.16)}',
    'html[class*="paleta-"]:not(.paleta-dorado){--n1:var(--navy-900);--n2:var(--navy-700);--n3:var(--gold-deep);--cian:var(--gold-light);--violeta:var(--gold)}',
    'html.az-claro:is(.paleta-dorado,.paleta-moca):not([data-tema="oscuro"]){--accent-text:#5F5044}',
    'html.paleta-moca:not([data-tema="oscuro"]) :is(.btn-gold,.btn.btn-gold,.btn-primary,.btn.btn-primary,.btn-luz,.cta-final){background:#1F7A70!important;color:#fff!important;border-color:transparent!important;box-shadow:0 10px 24px -12px rgba(31,122,112,.65)}',
    'html.paleta-moca:not([data-tema="oscuro"]) :is(.btn-gold,.btn-primary,.btn-luz,.cta-final):hover{background:#17655C!important}',
    // Un solo color de acción por pantalla: el botón principal va relleno y los secundarios, en contorno del mismo color (jerarquía clara, efecto de aislamiento).
    'html.az-claro:is(.paleta-dorado,.paleta-moca):not([data-tema="oscuro"]) .btn-osc{background:transparent!important;color:var(--acento-texto,#5F5044)!important;border:2px solid currentColor!important;box-shadow:none!important}',
    'html.paleta-moca:not([data-tema="oscuro"]) .btn-osc{background:transparent!important;color:#1F7A70!important;border:2px solid #1F7A70!important;box-shadow:none!important}',
    'html.paleta-moca:not([data-tema="oscuro"]) .btn-osc:hover{background:rgba(31,122,112,.08)!important}',
    // Botones de acción: tamaño táctil mínimo de 44 px, respuesta al pasar el ratón y foco visible para teclado (en todas las paletas, sin cambiar sus colores).
    ':is(.btn-gold,.btn-primary,.btn-luz,.cta-final){min-height:44px;transition:transform .15s ease,box-shadow .15s ease,background-color .15s ease}',
    ':is(.btn-gold,.btn-primary,.btn-luz,.cta-final):hover{transform:translateY(-1px)}',
    ':is(.btn-gold,.btn-primary,.btn-luz,.btn-osc,.cta-final,.btn-ghost,.btn-linea):focus-visible{outline:3px solid #1F7A70;outline-offset:3px}',
    'html[data-tema="oscuro"] :is(.btn-gold,.btn-primary,.btn-luz,.btn-osc,.cta-final,.btn-ghost,.btn-linea):focus-visible{outline-color:#F2C98A}',
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

  function muestra(k) { return PALETAS[k].muestra || (PALETAS[k].grad ? 'linear-gradient(135deg,#FFB347,#FF7A9C,#A35BE0)' : PALETAS[k].gold); }

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
  s.src = 'https://aurzane.com/aurzane-reportes.js?v=1'; s.defer = true; s.setAttribute('data-azr', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* Selector de idioma en todos los mundos */
(function (d) {
  if (window.AurzaneIdiomas || d.querySelector('script[data-azi]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-idiomas.js?v=1'; s.defer = true; s.setAttribute('data-azi', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* AURZANE AI · asistente de resultados en los tests de MIND y LIVE */
(function (d) {
  if (!/^(mind|live)\.aurzane\.com$/.test(location.hostname) || d.querySelector('script[data-azasis]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-asistente.js?v=3'; s.defer = true; s.setAttribute('data-azasis', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* Tu siguiente paso: al terminar un test, tres pasos con sentido (otro test, una práctica y un curso u orientación) */
(function (d) {
  if (!/^(mind|live)\.aurzane\.com$/.test(location.hostname) || !/\/test-de-/.test(location.pathname) || d.querySelector('script[data-azruta]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-ruta.js?v=1'; s.defer = true; s.setAttribute('data-azruta', '1');
  (d.head || d.documentElement).appendChild(s);
})(document);

/* AURZANE AI · artículos recientes en cada mundo y explicación de qué te llevas en cada test */
(function (d) {
  var h = location.hostname, p = location.pathname;
  if (!(/^(mind|live|learn|nexus|build)\.aurzane\.com$/.test(h) || (h === 'aurzane.com' && /^\/(articulos(\/[^/]*)?\/?(index\.html)?|research(\.html)?\/?)$/.test(p))) || d.querySelector('script[data-azcont]')) return;
  var s = d.createElement('script');
  s.src = 'https://aurzane.com/aurzane-contenido.js?v=6'; s.defer = true; s.setAttribute('data-azcont', '1');
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
    '.az-dock{position:fixed;left:14px;bottom:14px;z-index:9995;width:40px;height:40px;border-radius:50%;border:1px solid rgba(255,255,255,.28);background:rgba(21,13,51,.86);color:#F5F3EE;font:700 18px/1 system-ui,sans-serif;cursor:pointer;display:grid;place-items:center;box-shadow:0 8px 20px -8px rgba(0,0,0,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}' +
    '.az-dock:focus-visible{outline:2px solid #E2AE55;outline-offset:2px}' +
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
  var src = 'https://aurzane.com/aurzane-estilo.js?v=33';
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
  var css = 'https://aurzane.com/aurzane-ds.css?v=14';
  if (d.readyState === 'loading' && d.currentScript && d.currentScript.parentNode === d.head) d.write('<link rel="stylesheet" href="' + css + '" data-azds="1">');
  else { var l = d.createElement('link'); l.rel = 'stylesheet'; l.href = css; l.setAttribute('data-azds', '1'); (d.head || d.documentElement).appendChild(l); }
  var s = d.createElement('script'); s.src = 'https://aurzane.com/aurzane-ds.js?v=15'; s.defer = true; s.setAttribute('data-azds', '1');
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
