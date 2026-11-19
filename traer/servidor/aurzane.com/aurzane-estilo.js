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
    '.world-header::before,main>.hero::before{display:none!important}' +
    '.world-header .eyebrow,main>.hero .eyebrow{color:var(--mundo)!important}' +
    '.world-header h1 span{color:var(--mundo-osc)}html[data-tema="oscuro"] .world-header h1 span{color:inherit}' +
    '.trust-strip{border-top:3px solid var(--mundo)}' +
    '.filter-bar button.active,.filter-bar .activo,.chip.active{background:var(--mundo)!important;color:#fff!important;border-color:var(--mundo)!important}' +
    'a:focus-visible,button:focus-visible{outline:2px solid var(--mundo);outline-offset:2px}' +
    /* panel «Empieza por aquí» a la derecha de la cabecera */
    '.az-empieza{position:absolute;right:max(28px,calc((100% - 1200px)/2));top:50%;transform:translateY(-50%);width:340px;z-index:2;background:var(--surface,#fffdf9);border:1px solid rgba(60,45,30,.12);border-radius:18px;padding:18px 18px 10px;box-shadow:0 24px 50px -30px rgba(30,20,10,.45);text-align:left}' +
    'html[data-tema="oscuro"] .az-empieza{background:#151a33;border-color:rgba(255,255,255,.12)}' +
    '@media(min-width:1100px){.world-header:has(> .az-empieza){min-height:380px}}' +   /* el panel no se corta arriba (auditoría 16/11/2026) */
    '.az-empieza h2{font:600 1.05rem/1.3 "Instrument Sans",system-ui,sans-serif;margin:0 0 4px;color:inherit}' +
    '.az-empieza p{margin:0 0 10px;font-size:.86rem}' +
    '.az-empieza a{display:flex;gap:12px;align-items:center;padding:11px 8px;border-top:1px solid rgba(60,45,30,.1);text-decoration:none;color:inherit;border-radius:10px}' +
    '.az-empieza a:hover{background:var(--mundo-suave)}' +
    '.az-empieza a .ic{flex:none;width:38px;height:38px;border-radius:11px;display:grid;place-items:center;font-size:1.15rem;background:var(--mundo-suave);border:1px solid var(--mundo-suave)}' +
    '.az-empieza a b{display:block;font-weight:600;font-size:.95rem;line-height:1.25}.az-empieza a small{display:block;font-size:.8rem;opacity:.7;line-height:1.3}' +
    '.az-empieza a::after{content:"›";margin-left:auto;font-size:1.3rem;color:var(--mundo)}' +
    '@media(min-width:1100px){html.az-con-panel main>.hero .hero-in{text-align:left!important}html.az-con-panel main>.hero .hero-in>*{margin-left:0!important;justify-content:flex-start!important}' +
    'html.az-con-panel .world-header::before,html.az-con-panel main>.hero::before{opacity:.18}}' +
    '@media(max-width:1099px){.az-empieza{display:none}.world-header::before,main>.hero::before{opacity:.12!important}}' +
    '.az-portada{position:absolute;top:44px;right:16px;width:330px;border-radius:24px;overflow:hidden;color:#fff;background:linear-gradient(165deg,rgba(28,22,60,.72),rgba(12,10,30,.82));background:linear-gradient(165deg,color-mix(in srgb,var(--mundo-osc) 60%,rgba(10,8,24,.7)),rgba(10,8,24,.85));border:1px solid rgba(255,255,255,.16);box-shadow:0 30px 60px -30px rgba(0,0,0,.65);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:2}' +
    '.az-portada .ilu{height:200px;background-repeat:no-repeat;background-position:center;background-size:88% auto,100% 100%;border-bottom:1px solid rgba(255,255,255,.1)}' +
    '.az-portada .dat{padding:16px 20px 18px}.az-portada .esc{display:inline-block;font-size:.76rem;font-weight:700;letter-spacing:.03em;background:rgba(255,217,160,.16);color:#FFD9A0;border-radius:99px;padding:3px 10px;margin-bottom:10px}' +
    '.az-portada b{display:block;font-size:.95rem;margin-bottom:2px}.az-portada p{margin:0 0 12px;font-size:.9rem;line-height:1.45;opacity:.85}' +
    '.az-portada ul{display:flex;gap:8px;list-style:none;margin:0;padding:0}.az-portada li{flex:1;text-align:center;font-size:.72rem;opacity:.85;background:rgba(255,255,255,.07);border-radius:12px;padding:8px 4px}' +
    '.az-portada li i{display:block;font-style:normal;font-family:"Bodoni Moda",Georgia,serif;font-size:1.15rem;font-weight:700;opacity:1;color:#fff}' +
    '@media(min-width:1100px){html.az-con-portada .hero>.wrap>h1,html.az-con-portada .hero>.wrap>.lead,html.az-con-portada .hero>.wrap>.chips,html.az-con-portada #azEng{max-width:calc(100% - 380px)!important}}' +
    '.az-portada.compacta .ilu{height:130px}.az-portada.compacta p,.az-portada.compacta ul,.az-portada.compacta b{display:none}.az-portada.compacta .esc{margin:0}'+
    '@media(max-width:1099px){.az-portada{position:relative;top:auto;right:auto;width:auto;max-width:520px;margin:22px 0 0;display:grid;grid-template-columns:150px 1fr}.az-portada .ilu{height:auto;min-height:150px;border-bottom:0;border-right:1px solid rgba(255,255,255,.1);background-size:96% auto,100% 100%}}' +
    '@media(max-width:520px){.az-portada{grid-template-columns:1fr}.az-portada .ilu{height:140px;border-right:0;border-bottom:1px solid rgba(255,255,255,.1)}}' +
    '.az-explorar{padding:56px 20px;background:var(--mundo-suave)}.az-explorar .in{max-width:1120px;margin:0 auto}' +
    '.az-explorar h2{font:700 clamp(1.5rem,3vw,2rem)/1.2 "Bodoni Moda",Georgia,serif;margin:0 0 6px}.az-explorar>.in>p{margin:0 0 20px;opacity:.75}' +
    '.az-explorar .g{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}' +
    '.az-explorar .c{display:flex;flex-direction:column;border-radius:18px;overflow:hidden;text-decoration:none;color:#fff;background:#2a2350;box-shadow:0 18px 36px -24px rgba(0,0,0,.6);transition:transform .2s}' +
    '.az-explorar .c:hover{transform:translateY(-3px)}.az-explorar .az-c-mind{background:linear-gradient(160deg,#5B43B8,#2a1f63)}.az-explorar .az-c-live{background:linear-gradient(160deg,#B4542C,#5a2610)}' +
    '.az-explorar .i{height:120px;background-repeat:no-repeat;background-position:center;background-size:78% auto;border-bottom:1px solid rgba(255,255,255,.12)}' +
    '.az-explorar .t{padding:14px 16px 16px}.az-explorar small{display:block;font-size:.72rem;font-weight:700;letter-spacing:.06em;opacity:.7}.az-explorar b{display:block;font-size:1.05rem;margin:2px 0 4px}' +
    '.az-explorar em{display:block;font-style:normal;font-size:.86rem;line-height:1.4;opacity:.82}' +
    '@media (prefers-reduced-motion:reduce){.az-explorar .c{transition:none}}' +
    '.az-boletin{background:#0f1530;color:#f3efe6;padding:44px 20px}.az-boletin .in{max-width:1120px;margin:0 auto;display:grid;grid-template-columns:1.1fr 1fr;gap:28px;align-items:center}' +
    '.az-boletin h2{font:700 clamp(1.35rem,2.6vw,1.8rem)/1.2 "Bodoni Moda",Georgia,serif;margin:0 0 8px;color:#f3efe6}.az-boletin p{margin:0;opacity:.8}' +
    '.az-boletin form{display:grid;grid-template-columns:1fr auto;gap:10px}.az-boletin input[type=email]{padding:13px 16px;border-radius:99px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.06);color:#fff;font:inherit;min-width:0}' +
    '.az-boletin button{padding:13px 22px;border:0;border-radius:99px;background:#E2BF6A;color:#1b1440;font:700 1rem inherit;cursor:pointer}' +
    '.az-boletin label{grid-column:1/-1;font-size:.84rem;opacity:.8}.az-boletin label a{color:#E2BF6A}.az-boletin .trampa{position:absolute;left:-9999px}' +
    '@media(max-width:760px){.az-boletin .in{grid-template-columns:1fr}.az-boletin form{grid-template-columns:1fr}}' +
    '.az-bol-pop{position:fixed;right:16px;bottom:16px;z-index:9995;width:min(380px,calc(100vw - 32px));padding:18px 18px 16px!important;border-radius:18px;box-shadow:0 24px 60px -20px rgba(0,0,0,.7)}' +
    '.az-bol-pop form,.az-bol-res form{grid-template-columns:1fr!important}.az-bol-pop .cerrar{position:absolute;top:6px;right:10px;background:none;border:0;color:#fff;font-size:1.5rem;cursor:pointer;opacity:.7}' +
    '@media (prefers-reduced-motion:no-preference){.az-bol-pop{animation:azsube .35s ease-out}}@keyframes azsube{from{transform:translateY(20px);opacity:0}to{transform:none;opacity:1}}' +
    '@media print{.az-empieza,.az-portada,.az-explorar,.az-boletin{display:none}}';
  var st = d.createElement('style'); st.id = 'az-estilo'; st.textContent = css; (d.head || html).appendChild(st);

  /* favicon y logo para pestañas, móviles y Google */
  function icono(rel, href, sizes) {
    if (d.querySelector('link[rel="' + rel + '"]' + (sizes ? '[sizes="' + sizes + '"]' : ''))) return;
    var l = d.createElement('link'); l.rel = rel; l.href = href; if (sizes) l.sizes = sizes; d.head.appendChild(l);
  }

  var FIJOS = {
    nexus: [['🧮', 'Calculadora de nota PAU', 'Tu nota de acceso y de admisión', '/calculadora-nota-pau/'], ['🎓', 'Buscador de universidades', '6.411 instituciones en 55 países', '/universidades/'], ['🎯', '¿Qué puedo estudiar con mi nota?', 'Grados a tu alcance', '/universidades/que-puedo-estudiar/']],
    learn: [['🧠', 'Curso de neurociencias', 'Metodología e investigación, paso a paso', 'cursos.html?c=tecnicas-neurociencias'], ['📚', 'Todos los cursos', 'Gratis y a tu ritmo', 'cursos.html'], ['🎯', 'Test vocacional OVP', 'Descubre qué estudiar', 'https://ovp.aurzane.com/portal.html']]
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

  /* Fotos reales (Unsplash, licencia libre) para cada test y calculadora: sustituyen a los dibujos propios */
  var FOTO = { olas: '1505142468610-359e7d316be0', nube: '1529665253569-6d01c0eaf7b6', espejo: '1517841905240-472988babdf9', corazon: '1544027993-37dbfe43562a',
    montana: '1464822759023-fed622ff2c3b', vela: '1499750310107-5fef28a66643', espiral: '1541199249251-f713e6145474', brote: '1466692476868-aef1dfb1e735',
    sol: '1507525428034-b723cf961d3e', bienestar: '1506126613408-eca07ce68773', puntos: '1512438248247-f0f2a5a8b7f0', foco: '1434030216411-0b793f4b4173',
    luna: '1541781774459-bb2af2f05b55', habitos: '1490645935967-10de6ba17061', grafica: '1554224155-6726b3ff858f', casa: '1560518883-ce09059eeffa', ahorro: '1579621970563-ebec7560ff3e',
    agua: '1548839140-29a749e1cf4d', comida: '1512621776951-a57141f2eefd', ejercicio: '1571019613454-1cb2f99b2d8b', embarazo: '1493894473891-10fc1e5dbd22',
    tarta: '1464349095431-e9a21285b5f3', calendario: '1506784983877-45594efa4cbe', graficos: '1434626881859-194d67b2b86f', estudio: '1427504494785-3a9ca7044f45', impuestos: '1554224154-26032ffc0d07',
    chalet: '1570129477492-45c003edd2be', pisos: '1460317442991-0ec209397118', curriculum: '1586281380349-632531db7ed4', hucha: '1559526324-4b87b5e36e44',
    playa: '1473186578172-c141e6798cf4', manos: '1505751172876-fa1923c5c528', pesas: '1517836357463-d25dfeac3438', dormir: '1520206183501-b80df61043c2', viaje: '1603792835233-f4f7c2497d4f' };
  function foto(clave, ancho) { return 'url("https://images.unsplash.com/photo-' + (FOTO[clave] || FOTO.grafica) + '?w=' + (ancho || 640) + '&q=70&auto=format&fit=crop")'; }
  var TEMA = { 'test-de-ansiedad': 'olas', 'test-de-depresion': 'nube', 'test-de-autoestima': 'espejo', 'test-de-autocompasion': 'corazon', 'test-de-autoeficacia': 'montana',
    'test-de-burnout': 'vela', 'test-de-estres': 'espiral', 'test-de-resiliencia': 'brote', 'test-de-satisfaccion-con-la-vida': 'sol', 'test-de-soledad': 'puntos',
    'test-de-tdah': 'foco', 'test-de-bienestar': 'bienestar', 'test-de-habitos': 'habitos', 'test-de-sueno': 'luna', 'calculadora-hipoteca': 'casa', 'calculadora-reforma': 'casa', 'calculadora-interes-compuesto': 'ahorro', 'calculadora-sueldo-neto': 'impuestos',
    'calculadora-agua': 'agua', 'calculadora-calorias': 'comida', 'calculadora-imc': 'ejercicio', 'calculadora-embarazo': 'embarazo', 'calculadora-edad': 'tarta',
    'calculadora-dias-entre-fechas': 'calendario', 'calculadora-porcentajes': 'graficos', 'calculadora-nota-pau': 'estudio',
    'calculadora-gastos-compra-vivienda': 'chalet', 'calculadora-rentabilidad-alquiler': 'pisos', 'calculadora-finiquito': 'curriculum', 'calculadora-ahorro': 'hucha',
    'calculadora-jubilacion': 'playa', 'calculadora-ovulacion': 'manos', 'calculadora-peso-ideal': 'pesas', 'calculadora-sueno': 'dormir' };
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
    if (w.innerWidth < 700) return;   /* en el móvil la ficha empujaba la calculadora fuera de la pantalla y movía la página al cargar (CLS) */
    var wrap = d.querySelector('.hero > .wrap'), pre = wrap && wrap.querySelector('.pre');
    if (!wrap || !pre) return;
    var img = foto(TEMA[slug] || 'grafica', 680);
    var chips = Array.prototype.map.call(wrap.querySelectorAll('.chips li'), function (x) { return x.textContent; }).join(' ');
    var min = (chips.match(/(\d+)\s*min/) || [])[1];
    var preg = ((d.body.innerText || '').match(/\b0 de (\d{1,2})\b/) || [])[1];
    var escala = pre.textContent.replace(/^[^A-Za-zÁÉÍÓÚÑáéíóúñ0-9]+/, '').trim();
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var datos = [];
    if (preg) datos.push('<li><i>' + preg + '</i>preguntas</li>');
    if (min) datos.push('<li><i>' + min + '</i>minutos</li>');
    datos.push('<li><i>Gratis</i>sin registro</li>');
    var a = d.createElement('aside'); a.className = 'az-portada'; a.setAttribute('aria-label', 'Sobre este ' + (/^test/.test(slug) ? 'test' : 'cálculo'));
    a.innerHTML = '<div class="ilu" role="img" aria-label="Ilustración de ' + esc(escala) + '" style="background-image:' + img.replace(/"/g, '&quot;') + '"></div>' +
      '<div class="dat"><span class="esc">' + esc(escala) + '</span>' + (MIDE[slug] ? '<b>Qué mide</b><p>' + esc(MIDE[slug]) + '</p>' : '<p>Resultado al instante, calculado en tu navegador.</p>') +
      '<ul>' + datos.join('') + '</ul></div>';
    wrap.style.position = 'relative'; wrap.appendChild(a); html.classList.add('az-con-portada');
    /* si la cabecera es baja (calculadoras), la portada se compacta o se quita para no tapar nada */
    function encaje() {
      a.classList.remove('compacta'); a.style.display = '';
      if (w.innerWidth < 1100) return;
      var hero = wrap.parentElement, sig = hero.nextElementSibling, lim = hero.getBoundingClientRect().bottom;
      if (sig) lim = Math.min(lim, sig.getBoundingClientRect().top); lim -= 16;
      if (a.getBoundingClientRect().bottom > lim) a.classList.add('compacta');
      if (a.getBoundingClientRect().bottom > lim) a.style.display = 'none';
    }
    encaje(); w.addEventListener('resize', encaje); if (d.fonts && d.fonts.ready) d.fonts.ready.then(encaje); setTimeout(encaje, 1500);
  }

  /* ---------- «Sigue explorando»: cada test enlaza con otros relacionados, también de otros mundos ---------- */
  var TESTS = { ansiedad: ['mind', 'Test de ansiedad'], depresion: ['mind', 'Test de depresión'], autoestima: ['mind', 'Test de autoestima'], autocompasion: ['mind', 'Test de autocompasión'],
    autoeficacia: ['mind', 'Test de autoeficacia'], burnout: ['mind', 'Test de burnout'], estres: ['mind', 'Test de estrés'], resiliencia: ['mind', 'Test de resiliencia'],
    'satisfaccion-con-la-vida': ['mind', 'Satisfacción con la vida'], soledad: ['mind', 'Test de soledad'], tdah: ['mind', 'Test de TDAH en adultos'], personalidad: ['mind', 'Test de personalidad'],
    bienestar: ['live', 'Test de bienestar'], habitos: ['live', 'Test de hábitos'], sueno: ['live', 'Test de sueño'] };
  var REL = { ansiedad: 'estres depresion sueno resiliencia', depresion: 'ansiedad autoestima bienestar soledad', autoestima: 'autocompasion autoeficacia satisfaccion-con-la-vida personalidad',
    autocompasion: 'autoestima estres resiliencia bienestar', autoeficacia: 'autoestima resiliencia personalidad burnout', burnout: 'estres sueno autocompasion habitos',
    estres: 'ansiedad burnout sueno resiliencia', resiliencia: 'estres autoeficacia autocompasion satisfaccion-con-la-vida', 'satisfaccion-con-la-vida': 'bienestar autoestima soledad habitos',
    soledad: 'depresion satisfaccion-con-la-vida autoestima bienestar', tdah: 'ansiedad estres sueno personalidad', bienestar: 'depresion sueno habitos satisfaccion-con-la-vida',
    habitos: 'sueno bienestar estres burnout', sueno: 'estres ansiedad habitos bienestar' };
  function explorar() {
    var slug = (location.pathname.split('/').filter(Boolean)[0] || '').replace(/^test-de-/, '');
    var rel = REL[slug], pie = d.querySelector('footer');
    if (!rel || !pie || d.querySelector('.az-explorar')) return;
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var sec = d.createElement('section'); sec.className = 'az-explorar'; sec.setAttribute('aria-labelledby', 'azExT');
    sec.innerHTML = '<div class="in"><h2 id="azExT">Sigue explorando</h2><p>Otros tests que suelen ir de la mano con este. Gratis, anónimos y con el resultado explicado.</p><div class="g">' +
      rel.split(' ').map(function (k) {
        var t = TESTS[k], url = 'https://' + t[0] + '.aurzane.com/test-de-' + k + '/';
        var img = foto(TEMA['test-de-' + k] || 'grafica', 480).replace(/"/g, '&quot;');
        return '<a class="c az-c-' + t[0] + '" href="' + url + '"><span class="i" style="background-image:' + img + '" aria-hidden="true"></span><span class="t"><small>' + t[0].toUpperCase() + '</small><b>' + esc(t[1]) + '</b>' +
          (MIDE['test-de-' + k] ? '<em>' + esc(MIDE['test-de-' + k]) + '</em>' : '') + '</span></a>';
      }).join('') + '</div></div>';
    pie.parentNode.insertBefore(sec, pie);
  }

  /* ---------- compartir el resultado como imagen en los tests que aún no tenían el botón (p. ej. TDAH) ---------- */
  function compartirImagen() {
    var acc = d.getElementById('accRes');
    if (!acc || d.getElementById('imgRes') || !w.AZ || typeof w.AZ.imagen !== 'function') return;
    var b = d.createElement('button'); b.type = 'button'; b.className = 'btn btn-luz'; b.id = 'imgRes'; b.textContent = '📸 Compartir mi resultado';
    acc.insertBefore(b, acc.firstChild);
    b.addEventListener('click', function () {
      if (w.__res) return w.AZ.imagen(w.__res, d.getElementById('msg'));
      var med = d.getElementById('medidor'), val = med && med.querySelector('.valor b'), de = med && med.querySelector('.valor span');
      var niv = d.querySelector('#nivel > span'), fr = d.querySelector('#detalle p');
      var max = parseInt(((de && de.textContent) || '').replace(/^\D*(\d+).*$/, '$1'), 10) || 10;
      w.AZ.imagen({ titulo: (d.querySelector('h1') || {}).textContent ? d.title.split('|')[0].split(':')[0].replace(/\s+gratis.*$/i, '').trim() : 'Mi resultado',
        valor: val ? val.textContent.trim() : '', max: max, unidad: de ? de.textContent.trim() : '', nivel: niv ? niv.textContent.trim() : '',
        frase: fr ? fr.textContent.trim().split(/(?<=\.)\s/)[0] : '' }, d.getElementById('msg'));
    });
  }

  /* ---------- boletín semanal: un formulario sencillo antes del pie (portada, mundos, tests, artículos y tienda) ---------- */
  function formBol(origen, boton) {
    return '<form method="post" action="https://aurzane.com/boletin/"><input type="email" name="email" required placeholder="tu@correo.com" aria-label="Tu correo">' +
      '<input type="text" name="web" tabindex="-1" autocomplete="off" class="trampa" aria-hidden="true"><input type="hidden" name="origen" value="' + origen + '">' +
      '<button type="submit">' + (boton || 'Suscribirme') + '</button><label><input type="checkbox" name="acepto" value="1" required> Acepto la <a href="https://aurzane.com/privacidad.html">política de privacidad</a></label></form>';
  }
  function yaSuscrito() { try { return !!localStorage.getItem('azBolOk'); } catch (e) { return false; } }
  d.addEventListener('submit', function (e) { if (e.target.action && /\/boletin\/$/.test(e.target.action)) try { localStorage.setItem('azBolOk', '1'); } catch (x) {} }, true);
  /* 1) al terminar un test: justo después del resultado, que es cuando más interés hay */
  function boletinResultado() {
    var acc = d.getElementById('accRes'); if (!acc || d.querySelector('.az-bol-res') || yaSuscrito()) return;
    function poner() {
      if (d.querySelector('.az-bol-res') || !d.body.classList.contains('hecho')) return;
      var c = d.createElement('div'); c.className = 'az-boletin az-bol-res';
      c.innerHTML = '<div class="in" style="display:block"><h2 style="font-size:1.15rem">¿Quieres seguir cuidándote cada semana?</h2><p style="margin:0 0 12px">Te mandamos un test, un artículo y un libro recomendado cada domingo. Gratis y te das de baja cuando quieras.</p>' + formBol('resultado-' + location.pathname, 'Quiero recibirlo') + '</div>';
      c.style.cssText = 'margin:18px 0;padding:20px;border-radius:16px'; acc.parentNode.insertBefore(c, acc.nextSibling);
    }
    poner(); new MutationObserver(poner).observe(d.body, { attributes: true, attributeFilter: ['class'] });
  }
  /* 2) aviso discreto al leer más de la mitad de un artículo, una ficha o la tienda (como mucho una vez cada 14 días) */
  function boletinLectura() {
    var p = location.pathname;
    var vale = (m === 'portada' && /^\/(articulos|libros|biblioteca\/libro)\//.test(p)) || (m !== 'portada' && m !== 'ovp' && p === '/');
    if (!vale || yaSuscrito()) return;
    try { if (Date.now() - (+localStorage.getItem('azBolVisto') || 0) < 14 * 864e5) return; } catch (e) {}
    function mirar() {
      var h = d.documentElement, frac = (w.scrollY + w.innerHeight) / h.scrollHeight;
      if (frac < .55 || d.querySelector('.az-bol-pop')) return;
      w.removeEventListener('scroll', mirar);
      try { localStorage.setItem('azBolVisto', String(Date.now())); } catch (e) {}
      var c = d.createElement('aside'); c.className = 'az-boletin az-bol-pop'; c.setAttribute('role', 'dialog'); c.setAttribute('aria-label', 'Boletín semanal');
      c.innerHTML = '<button type="button" class="cerrar" aria-label="Cerrar">×</button><div class="in" style="display:block"><h2 style="font-size:1.1rem">¿Te está gustando?</h2><p style="margin:0 0 10px">Cada domingo, un libro, un artículo y un test en tu correo. Gratis.</p>' + formBol('lectura-' + location.pathname) + '</div>';
      d.body.appendChild(c);
      c.querySelector('.cerrar').addEventListener('click', function () { c.remove(); });
    }
    w.addEventListener('scroll', mirar, { passive: true });
  }
  function boletin() {
    var p = location.pathname, pie = d.querySelector('footer');
    var vale = (m === 'portada' && (p === '/' || /^\/(articulos|libros)\//.test(p))) || (m !== 'portada' && m !== 'ovp' && (p === '/' || /^\/(test-de-|calculadora-)/.test(p)));
    if (!vale || !pie || d.querySelector('.az-boletin:not(.az-bol-res):not(.az-bol-pop)') || yaSuscrito()) return;
    var f = d.createElement('section'); f.className = 'az-boletin'; f.setAttribute('aria-labelledby', 'azBolT'); f.setAttribute('data-nosnippet', '');
    f.innerHTML = '<div class="in"><div><h2 id="azBolT">Una vez por semana, lo mejor de AURZANE</h2><p>Un libro recomendado, el artículo nuevo y un test gratis. Un correo corto, sin publicidad de terceros, y te das de baja con un clic.</p></div>' +
      formBol(location.host + location.pathname) + '</div>';
    pie.parentNode.insertBefore(f, pie);
  }
  /* la barra de mundos no debe aparecer en los resultados de Google como texto («AURZANEMINDOVP…») */
  // Curso relacionado: tras los tests y ejercicios de ansiedad o estrés, el curso gratuito con certificado.
  // Curso relacionado al final de tests y ejercicios. [ruta, curso, título, texto, dominio, solo si está publicado]
  // Los cursos nuevos solo se anuncian cuando ya están publicados (lista que genera cada día cursos/catalogo.py).
  var CURSOS_REL = [
    [/^\/(test-de-ansiedad|test-de-estres|ejercicios\/(respiracion|relajacion|respiracion-[a-z-]+|relajacion-[a-z-]+))/, 'ansiedad-dia-a-dia',
      'Curso gratis: Gestionar la ansiedad en el día a día', 'Entiende tu ansiedad, calma el cuerpo, revisa los pensamientos que la alimentan y construye tu plan. 4 temas y certificado gratuito al terminar.', 'mind.aurzane.com', false],
    [/^\/(test-de-autoestima|test-de-autocompasion|ejercicios\/pausa-de-autocompasion)/, 'autoestima-dia-a-dia',
      'Curso gratis: Autoestima en el día a día', 'Reconoce la voz crítica, trátate con más amabilidad y actúa según lo que te importa. Mini curso con certificado gratuito al terminar.', 'mind.aurzane.com', true],
    [/^\/(test-de-sueno|calculadora-sueno)/, 'dormir-mejor',
      'Curso gratis: Dormir mejor', 'Cómo funciona el sueño, qué hábitos lo ordenan y qué hacer cuando no llega, con un diario de sueño. Mini curso con certificado gratuito al terminar.', 'live.aurzane.com', true]];
  function cursoRelacionado() {
    if (d.querySelector('.az-curso-rel')) return;
    for (var i = 0; i < CURSOS_REL.length; i++) {
      var c = CURSOS_REL[i]; if (location.hostname !== c[4] || !c[0].test(location.pathname)) continue;
      var pintar = function (img) {
        var ref = d.querySelector('section[data-guia]') || d.querySelector('aside.firma') || d.querySelector('footer'); if (!ref || d.querySelector('.az-curso-rel')) return;
        var w = ref.closest('.wrap') || ref;
        var box = d.createElement('div'); box.className = 'wrap az-curso-rel';
        box.innerHTML = '<a href="https://learn.aurzane.com/curso/' + c[1] + '/?utm_source=' + c[4].split('.')[0] + '&amp;utm_medium=test" style="display:flex;gap:18px;align-items:center;text-decoration:none;color:inherit;border:1px solid #c9a24b;border-radius:16px;padding:18px 20px;margin:28px 0;background:rgba(201,162,75,.07)">' +
          '<img src="' + img + '" alt="" width="160" height="90" loading="lazy" style="width:160px;height:auto;border-radius:10px;flex:none">' +
          '<span><strong style="display:block;font-size:1.08rem;margin-bottom:4px">' + c[2] + '</strong><span style="opacity:.85">' + c[3] + '</span><span class="az-cr-ver" style="display:block;margin-top:8px;font-weight:600;color:#7E6020">Ver el curso</span></span></a>';
        w.parentNode.insertBefore(box, w);
      };
      if (!c[5]) { pintar('https://learn.aurzane.com/cursos/portada-ansiedad.webp'); return; }
      var s = d.createElement('script'); s.src = 'https://learn.aurzane.com/cursos/publicados.js?d=' + new Date().toISOString().slice(0, 10); s.async = true;
      s.onload = function () { var P = w.AZ_CURSOS_PUB || {}; if (P[c[1]]) pintar(P[c[1]].img); };
      d.head.appendChild(s); return;
    }
  }
  // Recordatorios en tu calendario (17/11/2026, etapa 3, tarea 42): regla prevista y citas del embarazo como archivo .ics
  // que se crea en el propio dispositivo. AURZANE no recibe ni guarda ninguna fecha (son datos de salud).
  function calendarioIcs() {
    var esOvu = /^\/calculadora-ovulacion\/?$/.test(location.pathname), esEmb = /^\/calculadora-embarazo\/?$/.test(location.pathname);
    if ((!esOvu && !esEmb) || d.querySelector('.az-ics')) return;
    var ancla = d.getElementById(esOvu ? 'tablaCiclos' : 'hitosBloque') || d.getElementById('hitos'); if (!ancla) return;
    if (ancla.tagName === 'TABLE' || ancla.tagName === 'TBODY') ancla = ancla.closest('table') || ancla;
    var DIA = 864e5;
    function dIso(t) { var x = new Date(t); return x.getUTCFullYear() + ('0' + (x.getUTCMonth() + 1)).slice(-2) + ('0' + x.getUTCDate()).slice(-2); }
    function utc(v) { var p = String(v || '').split('-'); return p.length === 3 ? Date.UTC(+p[0], +p[1] - 1, +p[2]) : NaN; }
    function num(id, def, a, b) { var e = d.getElementById(id), v = e ? Math.round(+e.value) : NaN; return isFinite(v) && v ? Math.min(Math.max(v, a), b) : def; }
    function eventos() {
      var fur = utc((d.getElementById('fur') || {}).value); if (!isFinite(fur)) return [];
      var hoy = new Date(), h0 = Date.UTC(hoy.getFullYear(), hoy.getMonth(), hoy.getDate()), ev = [];
      if (esOvu) {
        var c = num('ciclo', 28, 20, 45), pr = fur, n = 0;
        while (pr <= h0 && n < 200) { pr += c * DIA; n++; }
        for (var i = 0; i < 6; i++) ev.push([pr + i * c * DIA, 'Regla prevista', 'Fecha calculada con un ciclo de ' + c + ' días. Es una estimación: los ciclos varían.']);
      } else {
        var cic = num('ciclo', 28, 21, 40), base = fur + (cic - 28) * DIA, H = w.HITOS || [[4,5,'Prueba de embarazo','Ya puede dar positivo en casa. Pide cita con tu centro de salud y empieza con ácido fólico si aún no lo tomas.'],[6,10,'Primera visita y analítica','Grupo sanguíneo, serologías y análisis de sangre y orina del primer trimestre.'],[11,13,'Ecografía del primer trimestre','Confirma la edad gestacional y, junto con la analítica, el cribado combinado.'],[18,22,'Ecografía morfológica','La de la semana 20: revisa con detalle la anatomía del bebé.'],[24,28,'Test de O’Sullivan','Cribado de diabetes gestacional con una prueba de glucosa.'],[32,36,'Ecografía del tercer trimestre','Valora el crecimiento y la posición del bebé.'],[35,37,'Cultivo de estreptococo','Muestra vaginal y rectal para prevenir infecciones en el parto.'],[37,42,'A término','El bebé puede nacer en cualquier momento. Revisa tu plan de parto.']];   // mismas citas que la calculadora de embarazo de LIVE
        H.forEach(function (x) { var a = base + x[0] * 7 * DIA; if (a + 7 * DIA >= h0) ev.push([a, x[2] + ' (semanas ' + x[0] + ' a ' + x[1] + ')', x[3]]); });
        ev.push([base + 280 * DIA, 'Fecha probable de parto', 'Fecha estimada: solo una pequeña parte de los bebés nace justo ese día.']);
      }
      return ev;
    }
    var box = d.createElement('div'); box.className = 'az-ics';
    box.style.cssText = 'margin:18px 0;padding:14px 16px;border-radius:12px;border:1px solid rgba(127,127,127,.3);font-size:.93rem';
    box.innerHTML = '<button type="button" style="min-height:44px;padding:10px 18px;border-radius:99px;border:1px solid currentColor;background:transparent;color:inherit;font:inherit;font-weight:600;cursor:pointer">📅 ' +
      (esOvu ? 'Añadir mis próximas reglas a mi calendario' : 'Añadir las citas del embarazo a mi calendario') + '</button>' +
      '<p style="margin:8px 0 0;opacity:.8">Se descarga un archivo de calendario con aviso la víspera. Se crea en tu dispositivo: AURZANE no recibe ni guarda tus fechas.</p>';
    box.querySelector('button').addEventListener('click', function () {
      var ev = eventos(); if (!ev.length) { box.querySelector('p').textContent = 'Primero indica la fecha de tu última regla.'; return; }
      var st = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
      var esc = function (t) { return String(t).replace(/[\\,;]/g, function (m) { return '\\' + m; }).replace(/\n/g, '\\n'); };
      var ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//AURZANE//Recordatorios//ES', 'CALSCALE:GREGORIAN'];
      ev.forEach(function (e, i) {
        ics.push('BEGIN:VEVENT', 'UID:' + dIso(e[0]) + '-' + i + '-' + Math.random().toString(36).slice(2, 8) + '@aurzane.com', 'DTSTAMP:' + st,
          'DTSTART;VALUE=DATE:' + dIso(e[0]), 'DTEND;VALUE=DATE:' + dIso(e[0] + DIA), 'SUMMARY:' + esc(e[1]), 'DESCRIPTION:' + esc(e[2] + ' ' + location.href.split('#')[0]),
          'BEGIN:VALARM', 'TRIGGER:-PT12H', 'ACTION:DISPLAY', 'DESCRIPTION:' + esc(e[1]), 'END:VALARM', 'END:VEVENT');
      });
      ics.push('END:VCALENDAR');
      var a = d.createElement('a'); a.href = URL.createObjectURL(new Blob([ics.join('\r\n')], { type: 'text/calendar' }));
      a.download = esOvu ? 'reglas-previstas.ics' : 'citas-embarazo.ics'; d.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
      box.querySelector('p').textContent = 'Listo: abre el archivo descargado para añadir ' + ev.length + ' fechas a tu calendario.';
    });
    ancla.parentNode.insertBefore(box, ancla.nextSibling);
  }
  function sinFragmento() { Array.prototype.forEach.call(d.querySelectorAll('.utility,.topbar,.todo-panel'), function (e) { e.setAttribute('data-nosnippet', ''); }); }
  function librero() {   // IA de la tienda y la biblioteca
    if (m !== 'portada' || !/^\/(libros|biblioteca)(\/|$)/.test(location.pathname) || d.querySelector('script[data-azlib]')) return;
    var s = d.createElement('script'); s.src = 'https://aurzane.com/aurzane-librero.js?v=2'; s.defer = true; s.setAttribute('data-azlib', '1'); d.head.appendChild(s);
  }
  function avisoFallo() {   // en todas las páginas: cualquier visitante puede avisar de un fallo; la IA lo revisa en su próxima ronda
    var pie = d.querySelector('footer'); if (!pie || d.querySelector('.az-fallo')) return;
    var b = d.createElement('button'); b.type = 'button'; b.className = 'az-fallo'; b.textContent = '¿Algo no funciona en esta página? Avísanos';
    b.style.cssText = 'display:block;margin:14px auto;background:none;border:0;color:inherit;font:inherit;font-size:.9rem;text-decoration:underline;text-underline-offset:3px;cursor:pointer;min-height:24px;padding:4px 8px';
    b.addEventListener('click', function () {
      var t = w.prompt('Cuéntanos qué ha fallado (un enlace, un test, un botón…). No incluyas datos personales.'); if (!t || t.trim().length < 5) return;
      fetch('https://aurzane.com/ai/librero.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tipo: 'incidencia', texto: t, pagina: location.href }) })
        .then(function (r) { return r.json(); }).then(function (j) { b.textContent = j.respuesta ? 'Gracias, la IA de AURZANE lo revisará.' : (j.error || 'No se pudo enviar'); })
        .catch(function () { b.textContent = 'No se pudo enviar. Escríbenos a hola@aurzane.com'; });
    });
    pie.appendChild(b);
  }
  /* ofertas de socios (Awin) junto a la herramienta que encaja; solo aparecen cuando el programa nos ha aceptado */
  var SOCIO = { 
    /* SaludOnNet en LIVE (16/11/2026): la consulta que encaja con cada calculadora o test, con enlace directo a la especialidad; va primero para tener prioridad */
    'consulta-embarazo': [/^\/calculadora-(embarazo|ovulacion)/, 'live', 'Revisiones y ecografías del embarazo sin seguro', 'Consultas de obstetricia y ecografías en clínicas privadas a precio cerrado, hasta un 70 % más baratas que la tarifa oficial del centro.', 'Ver precios en', 'consulta', 'https://www.saludonnet.com/servicios-medicos/obstetricia-y-ginecologia'],
    'consulta-nutricion': [/^\/calculadora-(calorias|imc|peso-ideal)/, 'live', '¿Prefieres que te guíe un especialista?', 'Consulta de endocrinología y nutrición en clínicas privadas o por videoconsulta, con precio cerrado y sin seguro médico.', 'Ver especialistas en', 'consulta', 'https://www.saludonnet.com/servicios-medicos/endocrinologia-y-nutricion'],
    'consulta-sueno': [/^\/(test-de-sueno|calculadora-sueno)/, 'live', '¿Duermes mal desde hace semanas?', 'Habla con un médico por videoconsulta o pide cita con un especialista, con precio cerrado y sin seguro médico.', 'Hablar con un médico en', 'consulta', 'https://www.saludonnet.com/video-consulta'],
    /* más sitios para SaludOnNet (18/11/2026): ejercicios guiados de MIND y artículos de salud de LIVE */
    'consulta-ejercicios': [/^\/ejercicios/, 'mind', '¿Necesitas algo más que respirar?', 'Si el estrés o la ansiedad no bajan con los ejercicios, hablarlo con un psicólogo puede ayudarte: en clínica o por videoconsulta, con precio cerrado y sin seguro médico.', 'Ver psicólogos en', 'consulta', 'https://www.saludonnet.com/servicios-medicos/psicologia'],
    'consulta-articulo': [/^\/articulo\.html/, 'live', '¿Te ha surgido alguna duda sobre tu salud?', 'Habla con un médico por videoconsulta o pide cita con un especialista, con precio cerrado y sin seguro médico.', 'Hablar con un médico en', 'consulta', 'https://www.saludonnet.com/video-consulta'],
    'consulta-chequeo': [/^\/(test-de-(habitos|bienestar)|calculadora-agua)/, 'live', 'Un chequeo para saber cómo estás', 'Análisis clínicos y revisiones en clínicas cerca de ti, a precio cerrado y sin necesidad de seguro.', 'Ver análisis en', 'consulta', 'https://www.saludonnet.com/servicios-medicos/analisis-clinicos'],
    hipoteca: [/^\/calculadora-(hipoteca|gastos-compra-vivienda)/, 'build', '¿Quieres que te estudien la hipoteca?', 'Un intermediario hipotecario compara bancos por ti y te dice cuánto te pueden prestar. Estudio sin compromiso.', 'Pedir estudio a'],
    reforma: [/^\/calculadora-reforma/, 'build', '¿Lo pasamos a presupuestos reales?', 'Pide presupuestos a profesionales de tu zona y compáralos con lo que te ha salido aquí.', 'Pedir presupuestos en'],
    /* Simbye (Awin 107814, 19/11/2026): eSIM de datos en las fichas de universidades de países a los que se va a estudiar desde España o Latinoamérica
       (no en las de España ni Latinoamérica, donde quien mira suele vivir allí). EE. UU. lleva a su eSIM; el resto, a la tienda en español */
    'esim-eeuu': [/^\/universidades\/estados-unidos\//, 'nexus', 'Llega a EE. UU. con internet desde el primer minuto', 'eSIM de datos para Estados Unidos: la instalas en el móvil antes de salir, sin tarjeta física ni roaming, y la recibes por correo en minutos.', 'Ver la eSIM de EE. UU. en', 'esim', 'https://simbye.com/es/products/usa-data-esim'],
    esim: [/^\/universidades\/(?!(espana|argentina|bolivia|brasil|chile|colombia|costa-rica|cuba|ecuador|el-salvador|guatemala|honduras|mexico|nicaragua|panama|paraguay|peru|puerto-rico|republica-dominicana|uruguay|venezuela|acerca|anunciate|assets|comparar|datos|mi-lista|notas-de-corte|paises|que-puedo-estudiar)\/)[a-z-]+\//, 'nexus', '¿Te vas a estudiar fuera? Llega con internet', 'eSIM de datos para más de 190 países: la instalas en el móvil antes de salir, sin tarjeta física ni roaming, y la recibes por correo en minutos.', 'Ver eSIM en', 'esim', 'https://simbye.com/es/'],
    universidades: [/^\/(universidades|calculadora-nota-pau)/, 'nexus', '¿Vas a estudiar fuera de casa?', 'Busca habitación o piso de estudiantes cerca de tu universidad.', 'Buscar alojamiento en'],
    crianza: [/^\/calculadora-(embarazo|ovulacion)/, 'live', 'Juguetes que acompañan el desarrollo', 'Juguetes educativos por edad para aprender jugando.', 'Ver juguetes en'],
    nutricion: [/^\/calculadora-(calorias|imc|peso-ideal)/, 'live', '¿Te ayudas con la alimentación?', 'Si entrenas o quieres cuidar tu alimentación, aquí tienes nutrición deportiva y comida saludable. Consulta con un profesional si tienes alguna condición de salud.', 'Ver productos en'],
    sueno: [/^\/(test-de-sueno|calculadora-sueno)/, 'live', 'Descansar mejor también es cuestión de cama', 'Colchones, almohadas y textiles de descanso. Si tus problemas de sueño duran semanas, habla con un profesional.', 'Ver en'],
    cursos: [/^\/.+/, 'learn', '¿Quieres seguir aprendiendo?', 'Cursos online en español para aprender nuevas habilidades a tu ritmo.', 'Ver cursos en'],
    bienestar: [/^\/(test-de-habitos|calculadora-agua)/, 'live', 'Para llevar tus hábitos a la compra', 'Alimentación saludable y productos para el día a día. Ningún producto sustituye a dormir bien, moverte y comer variado.', 'Ver en'],
    /* si el socio principal de un sitio aún no nos ha aceptado, se muestra el siguiente que encaje (16/11/2026) */
    bricolaje: [/^\/calculadora-reforma/, 'build', 'Materiales para tu reforma', 'Materiales, herramientas e instalación para llevar a cabo la reforma que acabas de calcular.', 'Ver en'],
    muebles: [/^\/calculadora-(reforma|hipoteca|gastos-compra-vivienda)/, 'build', 'Amuebla tu nueva casa', 'Muebles y decoración con envío a domicilio para cuando termines la reforma o la mudanza.', 'Ver muebles en'],
    'negocio-alquiler': [/^\/calculadora-rentabilidad-alquiler/, 'build', '¿Y si en lugar de un piso compras un negocio?', 'Negocios en venta con su facturación y su precio: otra forma de invertir para tener ingresos cada mes, sin depender de un inquilino.', 'Ver negocios en venta en', 'negocio'],
    'negocio-propio': [/^\/calculadora-finiquito/, 'build', '¿Y si tu siguiente paso es tu propio negocio?', 'Negocios en venta que ya funcionan, con clientes y facturación: una forma de emprender sin empezar de cero, también con tu indemnización.', 'Ver negocios en venta en', 'negocio'],
    'negocio-ahorro': [/^\/calculadora-(ahorro|jubilacion)/, 'build', 'Otra forma de poner a trabajar tus ahorros', 'Negocios en venta en España y en todo el mundo, con su facturación y su precio, para quien quiere generar ingresos además de su sueldo o su pensión.', 'Ver negocios en venta en', 'negocio'],
    negocio: [/^\/(index\.html)?$/, 'build', '¿Y si compras un negocio que ya funciona?', 'Negocios en venta en España y en todo el mundo, con su facturación y su precio, para quien quiere invertir o emprender sin empezar de cero.', 'Ver negocios en venta en'],
    deporte: [/^\/(calculadora-(calorias|imc)|test-de-habitos)/, 'live', 'Muévete más, a tu manera', 'Material deportivo para empezar o seguir entrenando, a cualquier nivel.', 'Ver en'],
    aventura: [/^\/((index\.html)?|test-de-bienestar\/?)$/, 'live', 'Una aventura cerca de ti', 'Excursiones y actividades guiadas en tu ciudad o en tu próximo viaje: moverte, descubrir y desconectar también es cuidarte.', 'Ver actividades en'],
    viajes: [/^\/((index\.html)?|test-de-bienestar\/?)$/, 'live', 'Desconecta con un viaje', 'Escapadas y viajes para descansar de verdad y volver con energía.', 'Ver viajes en'],
    consulta: [/^\/test-de-(ansiedad|depresion|estres|burnout|autoestima|soledad|tdah|resiliencia|autocompasion|autoeficacia|satisfaccion-con-la-vida)/, 'mind', '¿Quieres hablarlo con un profesional?', 'Si tu resultado te preocupa, una consulta con un psicólogo puede ayudarte: en clínica o por videoconsulta, con precio cerrado y sin seguro médico. Si estás en peligro, llama al 112 o al 024.', 'Ver psicólogos en', 'consulta', 'https://www.saludonnet.com/servicios-medicos/psicologia'],
    'seguro-viaje': [/^\/(universidades|calculadora-nota-pau)/, 'nexus', '¿Te vas a estudiar fuera?', 'Seguro de viaje y de estudiantes para estancias en el extranjero, con asistencia médica.', 'Ver seguros en'] };
  var SOCIO_FOTO = { 'consulta-embarazo': 'embarazo', 'consulta-nutricion': 'comida', 'consulta-sueno': 'dormir', 'consulta-chequeo': 'bienestar', 'consulta-ejercicios': 'vela', 'consulta-articulo': 'bienestar', hipoteca: 'casa', reforma: 'chalet',
    universidades: 'estudio', crianza: 'manos', nutricion: 'comida', sueno: 'dormir', cursos: 'foco', bienestar: 'habitos', bricolaje: 'casa', muebles: 'chalet',
    'negocio-alquiler': 'pisos', 'negocio-propio': 'curriculum', 'negocio-ahorro': 'hucha', negocio: 'graficos', deporte: 'ejercicio', aventura: 'montana', viajes: 'playa',
    consulta: 'vela', 'seguro-viaje': 'viaje', 'esim-eeuu': 'viaje', esim: 'viaje' };
  function socios() {
    var p = location.pathname, cands = [];
    Object.keys(SOCIO).forEach(function (k) { if (SOCIO[k][1] === m && SOCIO[k][0].test(p)) cands.push(k); });
    if (!cands.length || d.querySelector('.az-socio')) return;
    var sc = d.createElement('script'); sc.src = 'https://aurzane.com/libros/afiliados.js?d=' + new Date().toISOString().slice(0, 10); sc.async = true;
    sc.onload = function () {
      var A = w.__azAfil || {}, cual = null, id = null;
      cands.some(function (c) { var dd = SOCIO[c][5] || c; id = Object.keys(A).filter(function (k) { return A[k].d === dd; })[0]; if (id) cual = c; return !!id; });
      if (!id) return;
      var x = SOCIO[cual], pie = d.querySelector('.az-explorar') || d.querySelector('.az-libros') || d.querySelector('footer'); if (!pie) return;
      var c = d.createElement('aside'); c.className = 'az-socio'; c.setAttribute('data-nosnippet', '');
      /* tarjeta con foto real (Unsplash) del tema de la oferta (17/11/2026): más clara y atractiva que un banner, sin cargar publicidad de terceros */
      var fk = SOCIO_FOTO[cual] || 'grafica', href = (x[6] ? A[id].u.replace(/([?&]ued=)[^&]*/, '$1' + encodeURIComponent(x[6])) : A[id].u).replace(/"/g, '&quot;');
      c.style.cssText = 'max-width:1120px;margin:30px auto;border-radius:18px;background:#141a33;color:#f3efe6;border:1px solid rgba(255,255,255,.12);overflow:hidden;display:flex;flex-wrap:wrap';
      c.innerHTML = '<a href="' + href + '" target="_blank" rel="sponsored nofollow noopener" tabindex="-1" aria-hidden="true" style="flex:1 1 260px;min-height:170px;max-height:260px;display:block;background:#1d2547">' +
        '<img src="https://images.unsplash.com/photo-' + (FOTO[fk] || FOTO.grafica) + '?w=720&q=60&auto=format&fit=crop" alt="" loading="lazy" decoding="async" width="720" height="480" style="width:100%;height:100%;object-fit:cover;display:block"></a>' +
        '<div style="flex:2 1 320px;padding:22px 24px"><p style="margin:0 0 6px;font-size:.72rem;letter-spacing:.02em;opacity:.6"><a href="https://aurzane.com/aviso-legal.html" style="color:inherit">Publicidad</a> · ' + A[id].n + '</p>' +
        '<p style="margin:0 0 6px;font:700 1.25rem/1.3 \'Bodoni Moda\',Georgia,serif">' + x[2] + '</p><p style="margin:0 0 16px;opacity:.82">' + x[3] + '</p>' +
        '<a href="' + href + '" target="_blank" rel="sponsored nofollow noopener" style="display:inline-flex;align-items:center;min-height:44px;background:#E2BF6A;color:#1b1440;font-weight:700;text-decoration:none;padding:10px 22px;border-radius:99px">' + x[4] + ' ' + A[id].n + ' ↗</a>' +
        '</div>';
      pie.parentNode.insertBefore(c, pie);
      /* SaludOnNet (18/11/2026): al ver el resultado, la consulta sube justo debajo, que es cuando más ayuda; si no hay resultado, se queda abajo */
      if (/^consulta/.test(cual)) {
        var subir = function () {
          var r = d.getElementById('accRes'), bt = d.getElementById('calcular'), an = (r && !r.hidden) ? r : (bt && bt.closest('.acciones'));
          if (!an || !an.parentNode || an.nextSibling === c) return;
          c.style.margin = '18px auto'; an.parentNode.insertBefore(c, an.nextSibling);
        };
        if (d.body.classList.contains('hecho')) subir();
        try { new MutationObserver(function () { if (d.body.classList.contains('hecho')) subir(); }).observe(d.body, { attributes: true, attributeFilter: ['class'] }); } catch (e) {}
        var btc = d.getElementById('calcular'); if (btc) btc.addEventListener('click', function () { setTimeout(subir, 400); });
      }
    };
    d.head.appendChild(sc);
  }
  // Mi AURZANE: cada resultado de test se guarda en la cuenta (o queda pendiente hasta que la persona entre)
  function guardarTest() {
    var acc = d.getElementById('accRes'); if (!acc || !w.CFG || !w.CFG.clave) return;
    var hecho = false;
    function ck(n) { var m = d.cookie.match(new RegExp('(?:^|; )' + n.replace(/\./g, '\\.') + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : null; }
    function ponCk(n, v) { d.cookie = n + '=' + encodeURIComponent(v) + '; domain=.aurzane.com; path=/; max-age=' + 60 * 864e2 + '; secure; samesite=lax'; }
    function aviso(html) { var a = d.querySelector('.az-mi-aviso') || d.createElement('p'); a.className = 'az-mi-aviso'; a.style.cssText = 'margin:14px 0;padding:12px 16px;border-radius:12px;background:rgba(201,162,75,.12);border:1px solid rgba(201,162,75,.35);font-size:.93rem'; a.innerHTML = html; acc.parentNode.insertBefore(a, acc.nextSibling); }
    function cargar(src, fn) { var s = d.createElement('script'); s.src = src; s.onload = fn; d.head.appendChild(s); }
    function sesion(fn) {
      if (!ck('aurzane-id-auth') && !ck('aurzane-id-auth.0')) return fn(null);
      var seguir = function () { try { w.crearClienteAurzaneID('https://chtfpqwrrarfdjcivlad.supabase.co', 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw').auth.getSession().then(function (r) { fn(r.data.session); }, function () { fn(null); }); } catch (e) { fn(null); } };
      var conId = function () { w.crearClienteAurzaneID ? seguir() : cargar('https://aurzane.com/aurzane-id.js', seguir); };
      w.supabase && w.supabase.createClient ? conId() : cargar('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js', conId);
    }
    function guardar() {
      if (hecho || !d.body.classList.contains('hecho') || !w.__res) return; hecho = true;
      var r = w.__res, v = parseFloat(String(r.valor).replace(',', '.'));
      var item = { clave: w.CFG.clave, titulo: r.titulo || w.CFG.titulo, valor: isNaN(v) ? null : v, max: r.max || null, nivel: r.nivel || '', url: location.origin + location.pathname, fecha: new Date().toISOString().slice(0, 16) };
      var pend = []; try { pend = JSON.parse(ck('azPend') || '[]'); } catch (e) {}
      pend.push(item); pend = pend.slice(-6); ponCk('azPend', JSON.stringify(pend));
      sesion(function (s) {
        if (!s) { aviso('📈 <b>¿Quieres ver cómo evolucionas?</b> <a href="https://aurzane.com/mi-aurzane.html?next=' + encodeURIComponent('https://aurzane.com/mi-aurzane.html#tests') + '">Crea tu cuenta gratis</a> y este resultado se guardará en Mi AURZANE para compararlo la próxima vez.'); return; }
        fetch('https://aurzane.com/mi/tests.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ accion: 'guardar', token: s.access_token, resultados: pend }) })
          .then(function (x) { return x.json(); }).then(function (j) {
            if (j.ok) { ponCk('azPend', '[]'); aviso('✅ Resultado guardado en tu cuenta. <a href="https://aurzane.com/mi-aurzane.html#tests">Ver tu evolución en Mi AURZANE</a>'); }
          }).catch(function () {});
      });
    }
    guardar(); new MutationObserver(guardar).observe(d.body, { attributes: true, attributeFilter: ['class'] });
  }
  // Vídeo del día: en la portada de cada mundo, un vídeo corto de AURZANE que cambia cada día.
  // Se muestra la miniatura y el reproductor de YouTube (sin cookies) solo se carga si la persona pulsa.
  function videoDia() {
    if (location.pathname !== '/' && location.pathname !== '/index.html') return;
    if (!/(^|\.)aurzane\.com$/.test(location.hostname) || /^(ovp|panel)\./.test(location.hostname)) return;
    var s = d.createElement('script'); s.src = 'https://aurzane.com/videos.js?d=' + new Date().toISOString().slice(0, 10);
    s.onload = function () {
      var L = w.AZ_VIDEOS || []; if (!L.length) return;
      var dia = Math.floor(Date.now() / 864e5), v = L[dia % L.length];
      var c = d.createElement('section'); c.className = 'az-video-dia'; c.setAttribute('aria-labelledby', 'azVidT');
      c.innerHTML = '<style>.az-video-dia{max-width:1080px;margin:40px auto;padding:0 20px}.az-video-dia .in{display:grid;grid-template-columns:minmax(0,340px) 1fr;gap:28px;align-items:center;background:rgba(127,127,127,.07);border:1px solid rgba(127,127,127,.18);border-radius:20px;padding:22px}' +
        '.az-video-dia .rep{position:relative;aspect-ratio:9/16;max-height:520px;border-radius:14px;overflow:hidden;background:#000;cursor:pointer}.az-video-dia .rep img{width:100%;height:100%;object-fit:cover;opacity:.9}' +
        '.az-video-dia .rep b{position:absolute;inset:0;margin:auto;width:68px;height:68px;border-radius:50%;background:rgba(0,0,0,.6);display:grid;place-items:center;color:#fff;font-size:26px}' +
        '.az-video-dia iframe{width:100%;height:100%;border:0}.az-video-dia h2{margin:0 0 8px;font-family:"Bodoni Moda",Georgia,serif}.az-video-dia p{margin:0 0 12px;line-height:1.6}' +
        '@media(max-width:700px){.az-video-dia .in{grid-template-columns:1fr}.az-video-dia .rep{max-width:300px;margin:0 auto}}</style>' +
        '<div class="in"><div class="rep" role="button" tabindex="0" aria-label="Reproducir el vídeo del día"><img src="https://i.ytimg.com/vi/' + v.id + '/hqdefault.jpg" alt="" loading="lazy"><b>▶</b></div>' +
        '<div><h2 id="azVidT">Vídeo del día</h2><p>' + String(v.t).replace(/[&<>"]/g, function (x) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[x]; }) + '</p>' +
        '<p style="opacity:.75;font-size:.92rem">Cada día, un vídeo corto distinto de AURZANE sobre psicología, bienestar y hábitos.</p>' +
        '<p><a href="https://www.youtube.com/@AURZANE?sub_confirmation=1" target="_blank" rel="noopener">Suscríbete en YouTube</a></p></div></div>';
      var rep = c.querySelector('.rep');
      var play = function () { rep.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + v.id + '?autoplay=1&rel=0" title="Vídeo del día de AURZANE" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>'; };
      rep.addEventListener('click', play); rep.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); } });
      var pie = d.querySelector('footer'); pie ? pie.parentNode.insertBefore(c, pie) : d.body.appendChild(c);
    };
    d.head.appendChild(s);
  }
  // Enlaces legales y de confianza en todas las páginas (si la página no los trae ya en su pie)
  function piesLegales() {
    if (!/(^|\.)aurzane\.com$/.test(location.hostname) || d.querySelector('a[href*="/contacto.html"]') || d.querySelector('.az-legal')) return;
    var L = [['sobre-aurzane.html', 'Sobre AURZANE'], ['contacto.html', 'Contacto'], ['politica-editorial.html', 'Política editorial'], ['privacidad.html', 'Privacidad'], ['cookies.html', 'Cookies'], ['aviso-legal.html', 'Aviso legal'], ['condiciones.html', 'Condiciones de uso']];
    var n = d.createElement('nav'); n.className = 'az-legal'; n.setAttribute('aria-label', 'Información legal');
    n.style.cssText = 'display:flex;flex-wrap:wrap;justify-content:center;gap:4px 16px;flex:1 1 100%;width:100%;max-width:100%;box-sizing:border-box;min-width:0;font-size:.85rem;padding:14px 16px 22px;line-height:1.6';
    n.innerHTML = L.map(function (x) { return '<a href="https://aurzane.com/' + x[0] + '" style="color:inherit;white-space:nowrap;padding:4px 0;text-underline-offset:3px">' + x[1] + '</a>'; }).join('');
    var pie = d.querySelector('footer'); pie ? pie.appendChild(n) : d.body.appendChild(n);
  }
  // Clics en enlaces de compra: se cuentan (sin datos personales) para el panel de resultados
  // Amazon por país: quien nos visita desde EE. UU. va a Amazon.com con nuestro código de allí.
  var ZONAS_US = /^(America\/(New_York|Detroit|Chicago|Denver|Phoenix|Boise|Los_Angeles|Anchorage|Juneau|Sitka|Nome|Adak|Metlakatla|Yakutat|Menominee|Indiana\/.+|Kentucky\/.+|North_Dakota\/.+)|Pacific\/Honolulu|US\/.+)$/;
  function paisAmazon() {
    try { return ZONAS_US.test(Intl.DateTimeFormat().resolvedOptions().timeZone || '') ? 'us' : ''; } catch (e) { return ''; }
  }
  function amazonLocal(a) {
    if (paisAmazon() !== 'us' || !/(^|\.)amazon\.es$/.test(a.hostname || '')) return false;
    a.href = a.href.replace(/^https?:\/\/(www\.)?amazon\.es\//, 'https://www.amazon.com/').replace(/tag=z5464099v-21/, 'tag=z5464099v-20');
    if (!/tag=/.test(a.href)) a.href += (a.href.indexOf('?') < 0 ? '?' : '&') + 'tag=z5464099v-20';
    for (var n = a.firstChild; n; n = n.nextSibling) if (n.nodeType === 3) n.nodeValue = n.nodeValue.replace(/Amazon\.es/g, 'Amazon.com');
    return true;
  }
  function amazonPais() {
    if (paisAmazon() !== 'us') return;
    Array.prototype.forEach.call(d.querySelectorAll('a[href*="amazon.es"]'), amazonLocal);
    d.addEventListener('click', function (e) { var a = e.target.closest && e.target.closest('a[href*="amazon.es"]'); if (a) amazonLocal(a); }, true);
    d.addEventListener('auxclick', function (e) { var a = e.target.closest && e.target.closest('a[href*="amazon.es"]'); if (a) amazonLocal(a); }, true);
  }
  function clicsCompra() {
    d.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]'); if (!a) return;
      var h = a.hostname || '';
      var t = /(^|\.)amazon\.|amzn\.to$/.test(h) ? (/amazon\.com$/.test(h) ? 'amazon-us' : 'amazon') : /awin1\.com$/.test(h) ? 'awin-' + ((a.href.match(/awinmid=(\d+)/) || [])[1] || 'x') : /sponsored/.test(a.rel || '') ? h : '';
      if (!t) return;
      var datos = JSON.stringify({ t: t, p: location.hostname + location.pathname });
      try { if (!(navigator.sendBeacon && navigator.sendBeacon('https://aurzane.com/ai/clic.php', new Blob([datos], { type: 'text/plain' })))) throw 0; }
      catch (x) { try { fetch('https://aurzane.com/ai/clic.php', { method: 'POST', body: datos, keepalive: true, mode: 'no-cors' }); } catch (y) {} }
    }, true);
  }
  /* Tarjetas de tests y calculadoras con foto real en lugar de emoji: misma imagen que la portada de cada herramienta */
  function tarjetasConFoto() {
    var css = d.createElement('style');
    css.textContent = 'a.az-cf{position:relative;overflow:hidden;padding-top:128px!important}' +
      'a.az-cf .az-cf-img{position:absolute;left:0;right:0;top:0;height:112px;background-size:cover;background-position:center}' +
      'a.az-cf .az-cf-img::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.35))}' +
      'a.az-cf > .e{display:none!important}';
    d.head.appendChild(css);
    Array.prototype.forEach.call(d.querySelectorAll('a[href] > span.e'), function (e) {
      var a = e.parentNode, p = (a.getAttribute('href') || '').replace(/^https?:\/\/[^/]+/, '').split('/').filter(Boolean)[0] || '';
      if (!TEMA[p] || a.classList.contains('az-cf')) return;
      var i = d.createElement('span'); i.className = 'az-cf-img'; i.setAttribute('aria-hidden', 'true'); i.style.backgroundImage = foto(TEMA[p], 480);
      a.insertBefore(i, a.firstChild); a.classList.add('az-cf');
    });
  }

  /* tablas con desplazamiento horizontal: accesibles con el teclado (WCAG 2.1.1) */
  function desplazables() { Array.prototype.forEach.call(d.querySelectorAll('.scroll'), function (s) { if (s.scrollWidth > s.clientWidth + 1 && !s.hasAttribute('tabindex')) { s.tabIndex = 0; s.setAttribute('role', 'region'); s.setAttribute('aria-label', 'Tabla desplazable'); } }); }
  function iniciar() { setTimeout(desplazables, 800); panel(); portada(); explorar(); tarjetasConFoto(); compartirImagen(); boletin(); boletinResultado(); boletinLectura(); librero(); avisoFallo(); socios(); sinFragmento(); amazonPais(); clicsCompra(); cursoRelacionado(); calendarioIcs(); guardarTest(); videoDia(); piesLegales(); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(window, document);
