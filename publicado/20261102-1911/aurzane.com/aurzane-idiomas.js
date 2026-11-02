/*
 * AURZANE · Selector de idioma para todo el ecosistema (aurzane.com, los 5 mundos y OVP).
 * Lo carga aurzane-paleta.js en todas las páginas. Las páginas en español son el original;
 * al elegir otro idioma se traducen al vuelo con Google Traductor, que solo se carga si el visitante lo pide.
 * - Botón 🌐 flotante y aviso automático cuando el navegador está en otro idioma.
 * - La elección se guarda en cookies de .aurzane.com, así se mantiene al pasar de un mundo a otro.
 * - Una página puede excluirse con <meta name="aurzane-idiomas" content="no"> (p. ej. paneles con datos clínicos).
 * - Si el traductor no carga, se abre la versión traducida en translate.goog como alternativa.
 */
(function (w, d) {
  'use strict';
  if (w.AurzaneIdiomas) return;
  var meta = d.querySelector('meta[name="aurzane-idiomas"]');
  if (meta && meta.content === 'no') return;
  if (/(^|\/)(admin|admin-ovp|generar-informe)(\.html)?$/.test(location.pathname)) return; // datos sensibles: nunca se envían a un traductor
  var IDI = [['es', 'Español', '🇪🇸'], ['en', 'English', '🇬🇧'], ['pt', 'Português', '🇧🇷'], ['fr', 'Français', '🇫🇷'], ['it', 'Italiano', '🇮🇹'], ['de', 'Deutsch', '🇩🇪'],
             ['ca', 'Català', '🏳️'], ['gl', 'Galego', '🏳️'], ['eu', 'Euskara', '🏳️'], ['nl', 'Nederlands', '🇳🇱'], ['pl', 'Polski', '🇵🇱'], ['ro', 'Română', '🇷🇴'],
             ['uk', 'Українська', '🇺🇦'], ['ru', 'Русский', '🇷🇺'], ['ar', 'العربية', '🇸🇦'], ['zh-CN', '中文', '🇨🇳'], ['ja', '日本語', '🇯🇵'], ['ko', '한국어', '🇰🇷'], ['hi', 'हिन्दी', '🇮🇳']];
  var DOM = /(^|\.)aurzane\.com$/.test(location.hostname) ? '.aurzane.com' : '';
  function cookie(n) { var m = d.cookie.match(new RegExp('(?:^|; )' + n + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : null; }
  function poner(n, v, dias) {
    var base = n + '=' + v + '; path=/; max-age=' + (dias * 86400) + '; samesite=lax';
    d.cookie = base; if (DOM) d.cookie = base + '; domain=' + DOM;
  }
  function borrarGT() {
    var x = 'googtrans=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    d.cookie = x; if (DOM) { d.cookie = x + '; domain=' + DOM; d.cookie = x + '; domain=' + location.hostname; }
  }
  function actual() { return cookie('aurzane-idioma') || 'es'; }
  function nombre(c) { for (var i = 0; i < IDI.length; i++) if (IDI[i][0] === c) return IDI[i]; return IDI[0]; }

  function cargarGoogle(c) {
    poner('googtrans', '/es/' + c, 365);
    w.azGT = function () {
      try { new w.google.translate.TranslateElement({ pageLanguage: 'es', autoDisplay: false, includedLanguages: IDI.map(function (x) { return x[0]; }).join(',') }, 'az-gt'); } catch (e) {}
    };
    var div = d.createElement('div'); div.id = 'az-gt'; div.style.display = 'none'; d.body.appendChild(div);
    var s = d.createElement('script'); s.src = 'https://translate.google.com/translate_a/element.js?cb=azGT'; s.async = true;
    s.onerror = function () { alternativa(c); };
    d.head.appendChild(s);
    setTimeout(function () { if (!d.documentElement.classList.contains('translated-ltr') && !d.documentElement.classList.contains('translated-rtl') && !(w.google && w.google.translate)) alternativa(c); }, 8000);
    d.documentElement.setAttribute('lang', c);
  }
  function alternativa(c) {
    if (sessionStorage.getItem('az-gt-alt') === location.href) return;
    try { sessionStorage.setItem('az-gt-alt', location.href); } catch (e) {}
    var host = location.hostname.replace(/-/g, '--').replace(/\./g, '-') + '.translate.goog';
    location.href = 'https://' + host + location.pathname + (location.search ? location.search + '&' : '?') + '_x_tr_sl=es&_x_tr_tl=' + c + '&_x_tr_hl=' + c + location.hash;
  }
  function elegir(c) {
    poner('aurzane-idioma', c, 365);
    if (c === 'es') { borrarGT(); } else { poner('googtrans', '/es/' + c, 365); }
    location.reload();
  }

  function estilos() {
    var st = d.createElement('style');
    st.textContent = '.azi-btn{position:fixed;left:16px;bottom:128px;z-index:9988;width:46px;height:46px;border-radius:50%;border:1px solid rgba(255,255,255,.25);cursor:pointer;background:#1B1F3A;color:#fff;box-shadow:0 10px 24px -8px rgba(0,0,0,.5);display:grid;place-items:center;font-size:20px;line-height:1;transition:transform .15s}' +
      '.azi-btn:hover{transform:scale(1.07)}.azi-btn b{position:absolute;right:-4px;bottom:-4px;font:700 10px/1 system-ui,sans-serif;background:#E2AE55;color:#1B1F3A;border-radius:99px;padding:3px 5px;text-transform:uppercase}' +
      '.azi-pop{position:fixed;left:70px;bottom:128px;z-index:9991;width:min(300px,calc(100vw - 90px));max-height:min(420px,70vh);overflow:auto;background:#150D33;color:#F5F3EE;border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:12px;box-shadow:0 20px 50px -15px rgba(0,0,0,.6);font:500 14px/1.4 "Instrument Sans",system-ui,sans-serif}' +
      '.azi-pop h4{margin:2px 4px 8px;font-size:13px;opacity:.75;font-weight:600}.azi-pop ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:4px}' +
      '.azi-pop button{width:100%;text-align:left;border:0;background:transparent;color:inherit;border-radius:10px;padding:8px 9px;font:inherit;cursor:pointer}.azi-pop button:hover,.azi-pop button[aria-current="true"]{background:rgba(255,255,255,.12)}' +
      '.azi-pop p{margin:10px 4px 2px;font-size:11.5px;opacity:.6}' +
      '.azi-aviso{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:9992;width:min(520px,calc(100vw - 32px));background:#150D33;color:#F5F3EE;border:1px solid rgba(255,255,255,.16);border-radius:16px;padding:14px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;box-shadow:0 20px 50px -15px rgba(0,0,0,.6);font:500 14.5px/1.4 "Instrument Sans",system-ui,sans-serif}' +
      '.azi-aviso span{flex:1 1 220px}.azi-aviso button{border:0;border-radius:99px;padding:9px 15px;font:700 14px system-ui,sans-serif;cursor:pointer}.azi-aviso .si{background:#E2AE55;color:#1B1F3A}.azi-aviso .no{background:transparent;color:#F5F3EE;border:1px solid rgba(255,255,255,.3)}' +
      // ocultar la barra y los globos de Google
      '.goog-te-banner-frame,.skiptranslate>iframe,#goog-gt-tt,.goog-te-balloon-frame,.VIpgJd-ZVi9od-ORHb-OEVmcd,.VIpgJd-ZVi9od-aZ2wEe-wOHMyf{display:none!important}body{top:0!important}.goog-text-highlight{background:none!important;box-shadow:none!important}' +
      '@media print{.azi-btn,.azi-pop,.azi-aviso{display:none!important}}';
    d.head.appendChild(st);
  }

  function ui() {
    estilos();
    var c = actual(), n = nombre(c);
    var btn = d.createElement('button'); btn.type = 'button'; btn.className = 'azi-btn notranslate'; btn.setAttribute('translate', 'no');
    btn.setAttribute('aria-label', 'Idioma / Language'); btn.setAttribute('aria-expanded', 'false'); btn.title = 'Idioma / Language';
    btn.innerHTML = '<span aria-hidden="true">🌐</span>' + (c !== 'es' ? '<b>' + c.slice(0, 2) + '</b>' : '');
    var pop = d.createElement('div'); pop.className = 'azi-pop notranslate'; pop.setAttribute('translate', 'no'); pop.hidden = true; pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', 'Idioma');
    pop.innerHTML = '<h4>Idioma · Language</h4><ul>' + IDI.map(function (x) {
      return '<li><button type="button" data-l="' + x[0] + '" lang="' + x[0] + '"' + (x[0] === c ? ' aria-current="true"' : '') + '>' + x[2] + ' ' + x[1] + '</button></li>';
    }).join('') + '</ul><p>Original en español. Otros idiomas: traducción automática de Google.</p>';
    d.body.appendChild(pop); d.body.appendChild(btn);
    btn.addEventListener('click', function () { pop.hidden = !pop.hidden; btn.setAttribute('aria-expanded', String(!pop.hidden)); });
    pop.addEventListener('click', function (e) { var b = e.target.closest('[data-l]'); if (b) elegir(b.getAttribute('data-l')); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !pop.hidden) { pop.hidden = true; btn.focus(); } });
    d.addEventListener('click', function (e) { if (!pop.hidden && !pop.contains(e.target) && !btn.contains(e.target)) pop.hidden = true; });

    if (c !== 'es') { cargarGoogle(c); return; }
    // Aviso automático la primera vez si el navegador está en otro idioma
    if (cookie('aurzane-idioma')) return;
    var nav = (navigator.languages && navigator.languages[0] || navigator.language || 'es').toLowerCase();
    if (/^es/.test(nav)) return;
    var cod = nav.indexOf('zh') === 0 ? 'zh-CN' : nav.slice(0, 2), sug = null;
    for (var i = 1; i < IDI.length; i++) if (IDI[i][0] === cod) sug = IDI[i];
    if (!sug) sug = IDI[1];
    var TXT = { en: ['This page is in Spanish. Translate it into English?', 'Translate', 'No, thanks'], pt: ['Esta página está em espanhol. Traduzir para português?', 'Traduzir', 'Não, obrigado'],
      fr: ['Cette page est en espagnol. La traduire en français ?', 'Traduire', 'Non, merci'], it: ['Questa pagina è in spagnolo. Tradurla in italiano?', 'Traduci', 'No, grazie'],
      de: ['Diese Seite ist auf Spanisch. Auf Deutsch übersetzen?', 'Übersetzen', 'Nein, danke'] };
    var t = TXT[sug[0]] || ['This page is in Spanish. Translate it into ' + sug[1] + '?', 'Translate', 'No, thanks'];
    var av = d.createElement('div'); av.className = 'azi-aviso notranslate'; av.setAttribute('translate', 'no'); av.setAttribute('role', 'region'); av.setAttribute('aria-label', 'Idioma');
    av.innerHTML = '<span>' + sug[2] + ' ' + t[0] + '</span><button type="button" class="si">' + t[1] + '</button><button type="button" class="no">' + t[2] + '</button>';
    d.body.appendChild(av);
    av.querySelector('.si').addEventListener('click', function () { elegir(sug[0]); });
    av.querySelector('.no').addEventListener('click', function () { poner('aurzane-idioma', 'es', 365); av.remove(); });
  }

  w.AurzaneIdiomas = { elegir: elegir, actual: actual };
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', ui); else ui();
})(window, document);
