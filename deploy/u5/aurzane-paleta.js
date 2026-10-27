/*
 * AURZANE · Paleta de color compartida por todo el ecosistema
 * Se carga en <head> de cada página (aurzane.com y todos los mundos):
 *   <script src="https://aurzane.com/aurzane-paleta.js"></script>
 * - Guarda la elección en una cookie de .aurzane.com, así se mantiene al pasar de un mundo a otro.
 * - Aplica la paleta sobre las variables CSS que usan las páginas (--gold, --navy-*, --accent...).
 * - Pinta las opciones en los paneles .paleta-swatches que tenga la página
 *   y añade un botón flotante 🎨 para elegir el color desde cualquier sitio.
 */
(function (w, d) {
  'use strict';
  if (w.AurzanePaleta) return;
  var PALETAS = {
    dorado:    { nombre: 'Dorado clásico', n950: '#080B17', n900: '#0F1530', n800: '#151C3D', n700: '#1E2650', gold: '#C9A24B', goldLight: '#EACF92', goldDeep: '#8A6A28' },
    aurora:    { nombre: 'Aurora', n950: '#0D0820', n900: '#150D33', n800: '#1F1347', n700: '#2A1660', gold: '#FF8F70', goldLight: '#FFC38A', goldDeep: '#C2456E',
                 grad: 'linear-gradient(90deg,#FFB347,#FF7A9C,#A35BE0)', nuevo: true },
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
    '@media print{.azp-btn,.azp-pop{display:none!important}}'
  ].join('\n');

  function muestra(k) { return PALETAS[k].grad ? 'linear-gradient(135deg,#FFB347,#FF7A9C,#A35BE0)' : PALETAS[k].gold; }

  function montarUI() {
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
      d.body.appendChild(pop); d.body.appendChild(btn);
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
