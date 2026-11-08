/* AURZANE · capa visual común de los mundos (color propio por mundo, emblema, panel «Empieza por aquí», logo y favicon).
   Se carga desde aurzane-paleta.js. No cambia contenidos: solo presentación. */
(function (w, d) {
  if (w.AurzaneEstilo) return; w.AurzaneEstilo = 1;
  var host = location.hostname, m = (host.match(/^(mind|live|nexus|learn|build|ovp)\.aurzane\.com$/) || [])[1] || (host === 'aurzane.com' ? 'portada' : '');
  if (!m) return;
  var C = {
    mind:  ['#5B43B8', '#3B2A7E', 'rgba(91,67,184,.08)'],
    live:  ['#B4542C', '#7D3519', 'rgba(180,84,44,.08)'],
    nexus: ['#2F5FA8', '#1D3E73', 'rgba(47,95,168,.08)'],
    learn: ['#2F7A55', '#1C5338', 'rgba(47,122,85,.08)'],
    build: ['#8A5A32', '#5E3B1F', 'rgba(138,90,50,.08)'],
    ovp:   ['#5B43B8', '#3B2A7E', 'rgba(91,67,184,.08)'],
    portada: ['#B08A3A', '#7A5E22', 'rgba(176,138,58,.08)']
  }[m];
  var html = d.documentElement; html.classList.add('az-m-' + m);

  /* emblema de cada mundo: dibujo de líneas con su color */
  function svg(c) {
    var s = { mind: '<circle cx="200" cy="200" r="40"/><circle cx="200" cy="200" r="80" opacity=".7"/><circle cx="200" cy="200" r="120" opacity=".5"/><circle cx="200" cy="200" r="160" opacity=".32"/><circle cx="200" cy="200" r="196" opacity=".18"/><circle cx="200" cy="200" r="8" fill="C" stroke="none"/>',
      live: '<path d="M10 260h380" /><path d="M60 260a140 140 0 0 1 280 0" opacity=".8"/><path d="M110 260a90 90 0 0 1 180 0" opacity=".6"/><path d="M160 260a40 40 0 0 1 80 0" opacity=".45"/><path d="M200 80v-50M84 128 50 94M316 128l34-34" opacity=".5"/><path d="M40 300h320M90 336h220" opacity=".3"/>',
      nexus: '<g opacity=".55"><path d="M80 110 200 70l120 50-40 130-130 40-60-110z"/><path d="M200 70l-10 130 90 50M80 110l110 90-60 90M320 120 190 200"/></g><g fill="C" stroke="none"><circle cx="80" cy="110" r="9"/><circle cx="200" cy="70" r="9"/><circle cx="320" cy="120" r="9"/><circle cx="280" cy="250" r="9"/><circle cx="150" cy="290" r="9"/><circle cx="190" cy="200" r="13"/></g>',
      learn: '<path d="M40 340h80v-60h80v-60h80v-60h80" /><path d="M40 340h320" opacity=".35"/><path d="M360 100l-30-20M360 100l-30 20" /><circle cx="80" cy="310" r="7" fill="C" stroke="none"/><path d="M40 300h80M120 240h80M200 180h80" opacity=".3"/>',
      build: '<g opacity=".28"><path d="M40 80h320M40 140h320M40 200h320M40 260h320M40 320h320M80 40v320M140 40v320M200 40v320M260 40v320M320 40v320"/></g><path d="M100 300V160l100-70 100 70v140z"/><path d="M170 300v-70h60v70"/><path d="M60 300h280"/>',
      ovp: '<circle cx="200" cy="200" r="150" opacity=".35"/><circle cx="200" cy="200" r="100" opacity=".55"/><circle cx="200" cy="200" r="50"/><circle cx="200" cy="200" r="10" fill="C" stroke="none"/><path d="M200 20v80M200 300v80M20 200h80M300 200h80" opacity=".5"/>' }[m];
    if (!s) return '';
    return 'url("data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" fill="none" stroke="' + c + '" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">' + s.replace(/"C"/g, '"' + c + '"') + '</svg>') + '")';
  }

  var css =
    ':root{--mundo:' + C[0] + ';--mundo-osc:' + C[1] + ';--mundo-suave:' + C[2] + '}' +
    /* logo: «AURZANE» sin huecos y con su mundo al lado */
    '.topbar .brand{gap:0!important;white-space:nowrap}.topbar .brand .z{display:inline!important}' +
    '.topbar .brand .tag,.topbar .brand .world-tag,.topbar .brand small{margin-left:10px!important}' +
    '.utility .eco a.activo,.utility a[aria-current]{color:var(--mundo)!important}' +
    'html[data-tema="oscuro"] .utility .eco a.activo{color:#fff!important;text-decoration:underline;text-decoration-color:var(--mundo);text-underline-offset:4px}' +
    /* cabecera de cada mundo: color propio y emblema en lugar de la mancha dorada */
    '.world-header,main>.hero{position:relative;background-image:linear-gradient(180deg,var(--mundo-suave),transparent 85%)!important}' +
    '.world-header::before,main>.hero::before{background:' + svg(C[0]) + ' center/contain no-repeat!important;opacity:.55;filter:none!important}' +
    '.world-header .eyebrow,main>.hero .eyebrow{color:var(--mundo)!important}' +
    '.world-header h1 span{color:var(--mundo-osc)}html[data-tema="oscuro"] .world-header h1 span{color:inherit}' +
    '.trust-strip{border-top:3px solid var(--mundo)}' +
    '.filter-bar button.active,.filter-bar .activo,.chip.active{background:var(--mundo)!important;color:#fff!important;border-color:var(--mundo)!important}' +
    'a:focus-visible,button:focus-visible{outline:2px solid var(--mundo);outline-offset:2px}' +
    /* panel «Empieza por aquí» a la derecha de la cabecera */
    '.az-empieza{position:absolute;right:max(28px,calc((100% - 1200px)/2));top:50%;transform:translateY(-50%);width:340px;z-index:2;background:var(--surface,#fffdf9);border:1px solid rgba(60,45,30,.12);border-radius:18px;padding:18px 18px 10px;box-shadow:0 24px 50px -30px rgba(30,20,10,.45)}' +
    'html[data-tema="oscuro"] .az-empieza{background:#151a33;border-color:rgba(255,255,255,.12)}' +
    '.az-empieza h2{font:600 1.05rem/1.3 "Instrument Sans",system-ui,sans-serif;margin:0 0 4px;color:inherit}' +
    '.az-empieza p{margin:0 0 10px;font-size:.86rem;opacity:.75}' +
    '.az-empieza a{display:flex;gap:12px;align-items:center;padding:11px 8px;border-top:1px solid rgba(60,45,30,.1);text-decoration:none;color:inherit;border-radius:10px}' +
    '.az-empieza a:hover{background:var(--mundo-suave)}' +
    '.az-empieza a .ic{flex:none;width:38px;height:38px;border-radius:11px;display:grid;place-items:center;font-size:1.15rem;background:var(--mundo-suave);border:1px solid var(--mundo-suave)}' +
    '.az-empieza a b{display:block;font-weight:600;font-size:.95rem;line-height:1.25}.az-empieza a small{display:block;font-size:.8rem;opacity:.7;line-height:1.3}' +
    '.az-empieza a::after{content:"›";margin-left:auto;font-size:1.3rem;color:var(--mundo)}' +
    '@media(min-width:1100px){html.az-con-panel main>.hero .hero-in{text-align:left!important}html.az-con-panel main>.hero .hero-in>*{margin-left:0!important;justify-content:flex-start!important}' +
    'html.az-con-panel .world-header::before,html.az-con-panel main>.hero::before{opacity:.18}}' +
    '@media(max-width:1099px){.az-empieza{display:none}}' +
    '@media print{.az-empieza{display:none}}';
  var st = d.createElement('style'); st.id = 'az-estilo'; st.textContent = css; (d.head || html).appendChild(st);

  /* favicon y logo para pestañas, móviles y Google */
  function icono(rel, href, sizes) {
    if (d.querySelector('link[rel="' + rel + '"]' + (sizes ? '[sizes="' + sizes + '"]' : ''))) return;
    var l = d.createElement('link'); l.rel = rel; l.href = href; if (sizes) l.sizes = sizes; d.head.appendChild(l);
  }

  var FIJOS = {
    nexus: [['🧮', 'Calculadora de nota PAU', 'Tu nota de acceso y de admisión', '/calculadora-nota-pau/'], ['🎓', 'Buscador de universidades', '6.409 instituciones en 55 países', '/universidades/'], ['🎯', '¿Qué puedo estudiar con mi nota?', 'Grados a tu alcance', '/universidades/que-puedo-estudiar/']],
    learn: [['🧠', 'Curso de neurociencias', 'Metodología e investigación, paso a paso', 'cursos.html?c=metod-300263'], ['📚', 'Todos los cursos', 'Gratis y a tu ritmo', 'cursos.html'], ['🎯', 'Test vocacional OVP', 'Descubre qué estudiar', 'https://ovp.aurzane.com/portal.html']]
  };
  function corto(t) { return t.length <= 48 ? t : t.slice(0, 48).replace(/\s+\S*$/, '') + '…'; }
  function panel() {
    icono('icon', 'https://aurzane.com/favicon-48.png', '48x48'); icono('apple-touch-icon', 'https://aurzane.com/apple-touch-icon.png');
    if (m === 'portada' || m === 'ovp' || location.pathname.replace(/index\.html$/, '') !== '/') return;
    var cab = d.querySelector('.world-header') || d.querySelector('main>.hero');
    if (!cab || d.querySelector('.az-empieza')) return;
    var it = FIJOS[m] || [];
    if (!it.length) Array.prototype.slice.call(d.querySelectorAll('.az-herr a'), 0, 3).forEach(function (a) {
      var e = a.querySelector('.e'), b = a.querySelector('b'), s = a.querySelector('span:not(.e)');
      if (b) it.push([e ? e.textContent.trim() : '•', b.textContent.trim(), s ? corto(s.textContent.trim().split(/[.:]/)[0]) : '', a.getAttribute('href')]);
    });
    if (it.length < 2) return;
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var p = d.createElement('aside'); p.className = 'az-empieza'; p.setAttribute('aria-label', 'Empieza por aquí'); p.setAttribute('data-nosnippet', '');
    p.innerHTML = '<h2>Empieza por aquí</h2><p>Lo más usado en este mundo. Gratis y sin registro.</p>' + it.map(function (x) {
      return '<a href="' + esc(x[3]) + '"><span class="ic" aria-hidden="true">' + esc(x[0]) + '</span><span><b>' + esc(x[1]) + '</b><small>' + esc(x[2]) + '</small></span></a>';
    }).join('');
    cab.appendChild(p); html.classList.add('az-con-panel');
    /* el texto de la cabecera deja sitio al panel (se mide, porque cada mundo tiene su propia maqueta) */
    var dentro = cab.querySelector('.world-header-in,.hero-in') || cab.firstElementChild;
    function ajustar() {
      if (!dentro) return; dentro.style.paddingRight = ''; dentro.style.boxSizing = 'border-box';
      if (w.innerWidth < 1100) return;
      var r = dentro.getBoundingClientRect(), pl = p.getBoundingClientRect().left;
      if (r.right > pl - 32) dentro.style.paddingRight = Math.ceil(r.right - pl + 40) + 'px';
    }
    ajustar(); w.addEventListener('resize', ajustar); if (d.fonts && d.fonts.ready) d.fonts.ready.then(ajustar);
    /* cifras muy bajas («7 guías») restan más que suman: se ocultan hasta que crezcan */
    Array.prototype.forEach.call(d.querySelectorAll('.world-meta-row .wm'), function (x) {
      var n = parseInt((x.querySelector('b') || {}).textContent, 10); if (!isNaN(n) && n < 20) x.style.display = 'none';
    });
    var fila = d.querySelector('.world-meta-row'); if (fila && !Array.prototype.some.call(fila.children, function (x) { return x.style.display !== 'none'; })) fila.style.display = 'none';
  }
  /* la barra de mundos no debe aparecer en los resultados de Google como texto («AURZANEMINDOVP…») */
  function sinFragmento() { Array.prototype.forEach.call(d.querySelectorAll('.utility,.topbar,.todo-panel'), function (e) { e.setAttribute('data-nosnippet', ''); }); }
  function iniciar() { panel(); sinFragmento(); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(window, document);
