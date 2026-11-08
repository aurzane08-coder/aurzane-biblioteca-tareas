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
    'main>.hero{position:relative}.world-header{position:relative;background-image:linear-gradient(180deg,var(--mundo-suave),transparent 85%)!important}' +
    '.world-header::before,main>.hero::before{background:' + svg(C[0]) + ' center/contain no-repeat!important;opacity:.55;filter:none!important}' +
    '.world-header .eyebrow,main>.hero .eyebrow{color:var(--mundo)!important}' +
    '.world-header h1 span{color:var(--mundo-osc)}html[data-tema="oscuro"] .world-header h1 span{color:inherit}' +
    '.trust-strip{border-top:3px solid var(--mundo)}' +
    '.filter-bar button.active,.filter-bar .activo,.chip.active{background:var(--mundo)!important;color:#fff!important;border-color:var(--mundo)!important}' +
    'a:focus-visible,button:focus-visible{outline:2px solid var(--mundo);outline-offset:2px}' +
    /* panel «Empieza por aquí» a la derecha de la cabecera */
    '.az-empieza{position:absolute;right:max(28px,calc((100% - 1200px)/2));top:50%;transform:translateY(-50%);width:340px;z-index:2;background:var(--surface,#fffdf9);border:1px solid rgba(60,45,30,.12);border-radius:18px;padding:18px 18px 10px;box-shadow:0 24px 50px -30px rgba(30,20,10,.45);text-align:left}' +
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
    '@media(max-width:1099px){.az-empieza{display:none}.world-header::before,main>.hero::before{opacity:.12!important}}' +
    '.az-portada{position:absolute;top:44px;right:16px;width:330px;border-radius:24px;overflow:hidden;color:#fff;background:linear-gradient(165deg,rgba(28,22,60,.72),rgba(12,10,30,.82));border:1px solid rgba(255,255,255,.16);box-shadow:0 30px 60px -30px rgba(0,0,0,.65);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:2}' +
    '.az-portada .ilu{height:200px;background-repeat:no-repeat;background-position:center;background-size:88% auto,100% 100%;border-bottom:1px solid rgba(255,255,255,.1)}' +
    '.az-portada .dat{padding:16px 20px 18px}.az-portada .esc{display:inline-block;font-size:.76rem;font-weight:700;letter-spacing:.03em;background:rgba(255,217,160,.16);color:#FFD9A0;border-radius:99px;padding:3px 10px;margin-bottom:10px}' +
    '.az-portada b{display:block;font-size:.95rem;margin-bottom:2px}.az-portada p{margin:0 0 12px;font-size:.9rem;line-height:1.45;opacity:.85}' +
    '.az-portada ul{display:flex;gap:8px;list-style:none;margin:0;padding:0}.az-portada li{flex:1;text-align:center;font-size:.72rem;opacity:.85;background:rgba(255,255,255,.07);border-radius:12px;padding:8px 4px}' +
    '.az-portada li i{display:block;font-style:normal;font-family:"Bodoni Moda",Georgia,serif;font-size:1.25rem;font-weight:700;opacity:1;color:#fff}' +
    '@media(min-width:1100px){html.az-con-portada .hero>.wrap>h1,html.az-con-portada .hero>.wrap>.lead,html.az-con-portada .hero>.wrap>.chips,html.az-con-portada #azEng{max-width:calc(100% - 380px)!important}}' +
    '@media(max-width:1099px){.az-portada{position:relative;top:auto;right:auto;width:auto;max-width:520px;margin:22px 0 0;display:grid;grid-template-columns:150px 1fr}.az-portada .ilu{height:auto;min-height:150px;border-bottom:0;border-right:1px solid rgba(255,255,255,.1);background-size:96% auto,100% 100%}}' +
    '@media(max-width:520px){.az-portada{grid-template-columns:1fr}.az-portada .ilu{height:140px;border-right:0;border-bottom:1px solid rgba(255,255,255,.1)}}' +
    '@media print{.az-empieza,.az-portada{display:none}}';
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
      if (b) it.push([e ? e.textContent.trim() : '•', b.textContent.trim(), s ? corto(s.textContent.trim().split(/[.:,;(]/)[0]) : '', a.getAttribute('href')]);
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

  /* ---------- portada ilustrada de cada test y calculadora: imagen principal + qué mide + datos clave ---------- */
  var ILU = {
    olas: '<circle cx="160" cy="105" r="62" fill="#fff" fill-opacity=".07"/><circle cx="160" cy="105" r="40" fill="#fff" fill-opacity=".08"/><circle cx="160" cy="105" r="16" fill="#FFD9A0" stroke="none"/><path d="M0 70c40-30 80 30 120 0s80 30 120 0 60-25 80-10" opacity=".35"/><path d="M0 150c40-20 80 20 120 0s80 20 120 0 60-15 80-6" opacity=".55"/><path d="M0 182c40-10 80 10 120 0s80 10 120 0 60-8 80-3" opacity=".8"/><path d="M0 206h320" opacity=".9"/>',
    nube: '<circle cx="190" cy="92" r="44" fill="#FFD9A0" stroke="none"/><path d="M190 22v14M240 42l-10 10M260 92h-14M140 42l10 10" stroke="#FFD9A0"/><path d="M70 170c-22 0-34-26-14-40 2-26 34-34 48-16 14-24 56-18 58 12 24 0 32 34 8 44z" fill="#2a2350" fill-opacity=".85"/><path d="M60 196h200M100 210h120" opacity=".4"/>',
    espejo: '<ellipse cx="160" cy="105" rx="58" ry="80" fill="#fff" fill-opacity=".07"/><ellipse cx="160" cy="105" rx="46" ry="66" opacity=".6"/><circle cx="160" cy="88" r="16" fill="#FFD9A0" stroke="none"/><path d="M134 140c6-20 46-20 52 0" stroke="#FFD9A0"/><path d="M60 50l6 12 12 6-12 6-6 12-6-12-12-6 12-6zM262 140l4 8 8 4-8 4-4 8-4-8-8-4 8-4z" fill="#fff" fill-opacity=".8" stroke="none"/>',
    corazon: '<path d="M160 178s-70-40-70-88c0-26 20-42 40-42 14 0 24 8 30 18 6-10 16-18 30-18 20 0 40 16 40 42 0 48-70 88-70 88z" fill="#FFD9A0" fill-opacity=".9" stroke="none"/><path d="M40 200c30-60 60-70 90-60M280 200c-30-60-60-70-90-60" opacity=".7"/><circle cx="160" cy="105" r="96" opacity=".18"/>',
    montana: '<path d="M10 200l90-120 50 60 40-40 120 100z" fill="#fff" fill-opacity=".08"/><path d="M10 200l90-120 50 60 40-40 120 100" /><path d="M190 100V52" /><path d="M190 52h34l-8 9 8 9h-34" fill="#FFD9A0" stroke="#FFD9A0"/><path d="M40 200c30-30 60-20 80-50s50-40 70-50" stroke-dasharray="4 7" opacity=".7"/>',
    vela: '<rect x="138" y="100" width="44" height="96" rx="6" fill="#fff" fill-opacity=".12"/><path d="M160 100v-10"/><path d="M160 90c-16-14-10-34 0-48 10 14 16 34 0 48z" fill="#FFD9A0" stroke="none"/><circle cx="160" cy="70" r="46" opacity=".2"/><path d="M110 196h100" opacity=".6"/><path d="M60 150c10-20 0-40-10-50M262 150c-10-20 0-40 10-50" opacity=".35"/>',
    espiral: '<path d="M90 110c0-22 18-40 40-40s36 16 36 34-14 30-30 30-26-12-26-24 8-20 18-20 16 6 16 14" opacity=".75"/><path d="M166 104c30 0 40 36 154 36" stroke="#FFD9A0" stroke-width="3"/><circle cx="300" cy="140" r="6" fill="#FFD9A0" stroke="none"/><path d="M20 190h280" opacity=".3"/>',
    brote: '<path d="M30 196h260" /><path d="M120 196l20-16 14 10 18-14" opacity=".5"/><path d="M160 196v-70" stroke="#FFD9A0" stroke-width="3"/><path d="M160 150c-30 0-46-20-46-40 26 0 46 14 46 40zM160 132c26-2 44-22 42-46-24 2-42 20-42 46z" fill="#FFD9A0" fill-opacity=".85" stroke="none"/><circle cx="250" cy="56" r="20" fill="#fff" fill-opacity=".2"/>',
    sol: '<circle cx="160" cy="140" r="56" fill="#FFD9A0" stroke="none"/><path d="M160 60V40M218 84l14-14M102 84 88 70M240 140h20M60 140h20" stroke="#FFD9A0"/><path d="M0 170c60-30 120-30 160 0s100 30 160 0v50H0z" fill="#2a2350" fill-opacity=".9" stroke="none"/><path d="M0 170c60-30 120-30 160 0s100 30 160 0" />',
    puntos: '<circle cx="70" cy="110" r="12" fill="#FFD9A0" stroke="none"/><g fill="#fff" fill-opacity=".85" stroke="none"><circle cx="220" cy="80" r="10"/><circle cx="252" cy="104" r="10"/><circle cx="214" cy="126" r="10"/><circle cx="246" cy="148" r="10"/></g><path d="M86 110c40-10 80-20 120-26" stroke-dasharray="5 8" opacity=".8"/><circle cx="70" cy="110" r="34" opacity=".25"/>',
    foco: '<circle cx="160" cy="110" r="80" opacity=".25"/><circle cx="160" cy="110" r="54" opacity=".45"/><circle cx="160" cy="110" r="28" opacity=".7"/><circle cx="160" cy="110" r="9" fill="#FFD9A0" stroke="none"/><g fill="#fff" stroke="none" fill-opacity=".8"><circle cx="40" cy="40" r="4"/><circle cx="290" cy="60" r="4"/><circle cx="270" cy="190" r="4"/><circle cx="50" cy="180" r="4"/></g><path d="M48 46l60 34M282 64l-62 26M262 184l-56-40M58 174l56-36" stroke-dasharray="3 6" opacity=".6"/>',
    luna: '<path d="M196 50a62 62 0 1 0 50 98 52 52 0 1 1-50-98z" fill="#FFD9A0" stroke="none"/><g fill="#fff" stroke="none"><circle cx="70" cy="60" r="3"/><circle cx="110" cy="30" r="2"/><circle cx="270" cy="40" r="2.5"/><circle cx="60" cy="150" r="2"/><circle cx="290" cy="170" r="3"/></g><path d="M86 110h18l-18 18h18M120 86h12l-12 12h12" opacity=".7"/>',
    habitos: '<g opacity=".9"><rect x="50" y="50" width="56" height="56" rx="14" fill="#FFD9A0" fill-opacity=".9" stroke="none"/><rect x="132" y="50" width="56" height="56" rx="14" fill="#fff" fill-opacity=".14"/><rect x="214" y="50" width="56" height="56" rx="14" fill="#FFD9A0" fill-opacity=".9" stroke="none"/><rect x="50" y="128" width="56" height="56" rx="14" fill="#fff" fill-opacity=".14"/><rect x="132" y="128" width="56" height="56" rx="14" fill="#FFD9A0" fill-opacity=".9" stroke="none"/><rect x="214" y="128" width="56" height="56" rx="14" fill="#fff" fill-opacity=".14"/></g><path d="M64 78l10 10 20-20M228 78l10 10 20-20M146 156l10 10 20-20" stroke="#2a2350" stroke-width="4"/>',
    grafica: '<path d="M30 196h270M30 196V30" opacity=".5"/><g fill="#fff" fill-opacity=".14" stroke="none"><rect x="54" y="140" width="34" height="56" rx="6"/><rect x="104" y="116" width="34" height="80" rx="6"/><rect x="154" y="96" width="34" height="100" rx="6"/><rect x="204" y="70" width="34" height="126" rx="6"/></g><path d="M60 140l52-30 50-18 52-34 50-22" stroke="#FFD9A0" stroke-width="3"/><circle cx="264" cy="36" r="7" fill="#FFD9A0" stroke="none"/>',
    casa: '<g opacity=".25"><path d="M20 60h280M20 110h280M20 160h280M70 20v190M140 20v190M210 20v190M280 20v190"/></g><path d="M90 196V112l70-54 70 54v84z" fill="#fff" fill-opacity=".1"/><path d="M76 120l84-66 84 66" stroke="#FFD9A0" stroke-width="3"/><path d="M140 196v-48h40v48"/><path d="M40 196h240"/>'
  };
  var TEMA = { 'test-de-ansiedad': 'olas', 'test-de-depresion': 'nube', 'test-de-autoestima': 'espejo', 'test-de-autocompasion': 'corazon', 'test-de-autoeficacia': 'montana',
    'test-de-burnout': 'vela', 'test-de-estres': 'espiral', 'test-de-resiliencia': 'brote', 'test-de-satisfaccion-con-la-vida': 'sol', 'test-de-soledad': 'puntos',
    'test-de-tdah': 'foco', 'test-de-bienestar': 'sol', 'test-de-habitos': 'habitos', 'test-de-sueno': 'luna', 'calculadora-hipoteca': 'casa', 'calculadora-reforma': 'casa' };
  var MIDE = { 'test-de-ansiedad': 'Cuánta ansiedad y preocupación has sentido en las dos últimas semanas.', 'test-de-depresion': 'Cómo ha estado tu estado de ánimo en las dos últimas semanas.',
    'test-de-autoestima': 'Cómo te valoras a ti mismo en general.', 'test-de-autocompasion': 'Cómo te tratas cuando algo sale mal o te sientes mal.',
    'test-de-autoeficacia': 'Cuánto confías en tu capacidad para afrontar retos y problemas.', 'test-de-burnout': 'El agotamiento físico y mental que te dejan el trabajo o los estudios.',
    'test-de-estres': 'Tu nivel de tensión e irritabilidad de la última semana.', 'test-de-resiliencia': 'Lo rápido que te recuperas después de momentos difíciles.',
    'test-de-satisfaccion-con-la-vida': 'Cómo valoras tu vida en conjunto.', 'test-de-soledad': 'Con qué frecuencia te sientes aislado o sin compañía.',
    'test-de-tdah': 'Si tus despistes e inquietud encajan con el patrón del TDAH adulto.', 'test-de-bienestar': 'Tu bienestar emocional en las dos últimas semanas.',
    'test-de-habitos': 'Tu estilo de vida: alimentación, actividad física, descanso y más.', 'test-de-sueno': 'Cuánto y cómo duermes, y qué te puede estar quitando descanso.' };
  function portada() {
    var slug = location.pathname.split('/').filter(Boolean)[0] || '';
    if (!/^(test-de-|calculadora-)/.test(slug) || slug === 'test-de-personalidad' || d.querySelector('.az-portada')) return;
    var wrap = d.querySelector('.hero > .wrap'), pre = wrap && wrap.querySelector('.pre');
    if (!wrap || !pre) return;
    var ilu = ILU[TEMA[slug] || 'grafica'];
    var img = 'url("data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 220" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' + ilu + '</svg>') + '")';
    var chips = Array.prototype.map.call(wrap.querySelectorAll('.chips li'), function (x) { return x.textContent; }).join(' ');
    var min = (chips.match(/(\d+)\s*min/) || [])[1];
    var preg = ((d.body.innerText || '').match(/\b0 de (\d{1,2})\b/) || [])[1];
    var escala = pre.textContent.replace(/^[^A-Za-zÁÉÍÓÚÑáéíóúñ0-9]+/, '').trim();
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var datos = [];
    if (preg) datos.push('<li><i>' + preg + '</i>preguntas</li>');
    if (min) datos.push('<li><i>' + min + '</i>minutos</li>');
    datos.push('<li><i>0 €</i>sin registro</li>');
    var a = d.createElement('aside'); a.className = 'az-portada'; a.setAttribute('aria-label', 'Sobre este ' + (/^test/.test(slug) ? 'test' : 'cálculo'));
    a.innerHTML = '<div class="ilu" role="img" aria-label="Ilustración de ' + esc(escala) + '" style="background-image:' + img.replace(/"/g, '&quot;') + ',radial-gradient(70% 80% at 50% 45%,rgba(255,217,160,.2),transparent 70%)"></div>' +
      '<div class="dat"><span class="esc">' + esc(escala) + '</span>' + (MIDE[slug] ? '<b>Qué mide</b><p>' + esc(MIDE[slug]) + '</p>' : '<p>Resultado al instante, calculado en tu navegador.</p>') +
      '<ul>' + datos.join('') + '</ul></div>';
    wrap.style.position = 'relative'; wrap.appendChild(a); html.classList.add('az-con-portada');
  }
  /* la barra de mundos no debe aparecer en los resultados de Google como texto («AURZANEMINDOVP…») */
  function sinFragmento() { Array.prototype.forEach.call(d.querySelectorAll('.utility,.topbar,.todo-panel'), function (e) { e.setAttribute('data-nosnippet', ''); }); }
  function iniciar() { panel(); portada(); sinFragmento(); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(window, document);
