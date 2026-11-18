/* AURZANE · Buzón de reportes
 * Botón flotante en todos los mundos para avisar de un problema: enlace roto, dato incorrecto,
 * página que no funciona o sugerencia. Se carga desde aurzane-paleta.js.
 * Otras páginas pueden abrirlo con: AurzaneReportar({ tipo: 'dato', referencia: 'Universidad de X', mensaje: '' })
 * o con cualquier elemento [data-reportar] (atributos opcionales data-tipo y data-ref).
 */
(function (w, d) {
  if (w.AurzaneReportar) return;
  var SB = 'https://chtfpqwrrarfdjcivlad.supabase.co';
  var KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw';
  var TIPOS = [
    ['enlace', 'Un enlace no funciona'],
    ['dato', 'Hay un dato incorrecto'],
    ['pagina', 'La página no carga o se ve mal'],
    ['sugerencia', 'Tengo una sugerencia'],
    ['otro', 'Otro']
  ];
  var css = [
    '.azr-btn{position:fixed;left:16px;bottom:72px;z-index:9989;width:46px;height:46px;border-radius:50%;border:1px solid rgba(255,255,255,.25);cursor:pointer;background:#1B1F3A;color:#fff;box-shadow:0 10px 24px -8px rgba(0,0,0,.5);display:grid;place-items:center;font-size:19px;line-height:1;transition:transform .15s}',
    '.azr-btn:hover{transform:scale(1.07)} .azr-btn:focus-visible{outline:3px solid #FFB347;outline-offset:3px}',
    '.azr-tip{position:fixed;left:70px;bottom:80px;z-index:9989;background:#1B1F3A;color:#fff;font:600 13px system-ui,sans-serif;padding:7px 11px;border-radius:9px;pointer-events:none;opacity:0;transition:opacity .15s}',
    '.azr-btn:hover + .azr-tip,.azr-btn:focus-visible + .azr-tip{opacity:1}',
    '.azr-fondo{position:fixed;inset:0;z-index:10000;background:rgba(6,8,20,.55);display:grid;place-items:center;padding:16px}',
    '.azr-caja{width:min(460px,100%);max-height:calc(100vh - 32px);overflow:auto;background:#fff;color:#141a33;border-radius:18px;padding:22px;box-shadow:0 30px 60px -20px rgba(0,0,0,.6);font:15px/1.5 system-ui,-apple-system,sans-serif}',
    '.azr-caja h2{margin:0 0 4px;font:700 1.25rem Georgia,serif}',
    '.azr-caja p.sub{margin:0 0 14px;color:#5b6380;font-size:.9rem}',
    '.azr-caja label{display:block;font-weight:600;font-size:.85rem;margin:12px 0 5px}',
    '.azr-caja select,.azr-caja textarea,.azr-caja input{width:100%;box-sizing:border-box;font:inherit;color:inherit;background:#eef0f7;border:1.5px solid transparent;border-radius:11px;padding:10px 12px}',
    '.azr-caja select:focus,.azr-caja textarea:focus,.azr-caja input:focus{outline:none;border-color:#2b3fb8}',
    '.azr-caja textarea{min-height:110px;resize:vertical}',
    '.azr-ref{font-size:.8rem;color:#5b6380;background:#f5f4ef;border-radius:9px;padding:7px 10px;margin-top:10px;word-break:break-all}',
    '.azr-acc{display:flex;gap:10px;justify-content:flex-end;margin-top:18px;flex-wrap:wrap}',
    '.azr-acc button{font:700 .95rem system-ui,sans-serif;border-radius:11px;padding:10px 16px;cursor:pointer;border:1.5px solid #d5d9e8;background:#fff;color:#141a33}',
    '.azr-acc button.prim{background:#14206a;border-color:#14206a;color:#fff}',
    '.azr-acc button:disabled{opacity:.6;cursor:wait}',
    '.azr-msg{margin-top:10px;font-size:.88rem;font-weight:600}',
    '.azr-msg.err{color:#b4541a} .azr-ok{text-align:center;padding:10px 0}',
    '.azr-ok b{display:block;font:700 1.2rem Georgia,serif;margin:8px 0 4px}',
    '.azr-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}',
    '@media (prefers-color-scheme:dark){.azr-caja{background:#0f1530;color:#f3f1ea}.azr-caja p.sub,.azr-ref{color:#a3a9c2}.azr-caja select,.azr-caja textarea,.azr-caja input{background:#161d42}.azr-ref{background:#161d42}.azr-acc button{background:#0f1530;color:#f3f1ea;border-color:#2a335c}.azr-acc button.prim{background:#9fb4ff;border-color:#9fb4ff;color:#0b1030}}',
    '@media print{.azr-btn,.azr-tip{display:none!important}}'
  ].join('\n');

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var abierto = null, ultimoFoco = null;
  function cerrar() {
    if (!abierto) return;
    abierto.remove(); abierto = null;
    if (ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
  }

  function abrir(op) {
    op = op || {};
    if (abierto) cerrar();
    ultimoFoco = d.activeElement;
    var url = op.url || location.href;
    var ref = op.referencia || '';
    var f = d.createElement('div');
    f.className = 'azr-fondo';
    f.innerHTML = '<div class="azr-caja" role="dialog" aria-modal="true" aria-labelledby="azrT">' +
      '<form novalidate>' +
      '<h2 id="azrT">Reportar un problema</h2>' +
      '<p class="sub">Cuéntanos qué falla y lo revisamos. Nos ayudas a mejorar AURZANE para todos.</p>' +
      '<label for="azrTipo">¿Qué ocurre?</label><select id="azrTipo">' +
      TIPOS.map(function (t) { return '<option value="' + t[0] + '"' + (op.tipo === t[0] ? ' selected' : '') + '>' + t[1] + '</option>'; }).join('') + '</select>' +
      '<label for="azrMsg">Descríbelo</label><textarea id="azrMsg" maxlength="2000" required placeholder="Por ejemplo: el enlace a la web de la universidad no abre, o el número de grados no es correcto.">' + esc(op.mensaje || '') + '</textarea>' +
      '<label for="azrMail">Tu correo (opcional, solo para responderte)</label><input type="email" id="azrMail" maxlength="200" autocomplete="email" placeholder="nombre@correo.com">' +
      '<div class="azr-hp" aria-hidden="true"><label for="azrWeb">No rellenar</label><input id="azrWeb" tabindex="-1" autocomplete="off"></div>' +
      '<div class="azr-ref">Página: ' + esc(url) + (ref ? '<br>Sobre: ' + esc(ref) : '') + '</div>' +
      '<div class="azr-msg" aria-live="polite"></div>' +
      '<div class="azr-acc"><button type="button" data-cerrar>Cancelar</button><button type="submit" class="prim">Enviar reporte</button></div>' +
      '</form></div>';
    d.body.appendChild(f); abierto = f;
    var form = f.querySelector('form'), msg = f.querySelector('.azr-msg'), txt = f.querySelector('#azrMsg');
    setTimeout(function () { (op.tipo ? txt : f.querySelector('#azrTipo')).focus(); }, 30);
    f.addEventListener('click', function (e) { if (e.target === f || e.target.closest('[data-cerrar]')) cerrar(); });
    f.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); cerrar(); }
      if (e.key === 'Tab') {
        var fs = f.querySelectorAll('select,textarea,input:not([tabindex="-1"]),button');
        var a = fs[0], z = fs[fs.length - 1];
        if (e.shiftKey && d.activeElement === a) { e.preventDefault(); z.focus(); }
        else if (!e.shiftKey && d.activeElement === z) { e.preventDefault(); a.focus(); }
      }
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (f.querySelector('#azrWeb').value) { cerrar(); return; }
      var texto = txt.value.trim(), mail = f.querySelector('#azrMail').value.trim();
      msg.className = 'azr-msg err';
      if (texto.length < 3) { msg.textContent = 'Escribe qué ocurre para que podamos revisarlo.'; txt.focus(); return; }
      if (mail && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail)) { msg.textContent = 'Revisa el correo, o déjalo vacío.'; f.querySelector('#azrMail').focus(); return; }
      var b = form.querySelector('.prim'); b.disabled = true; b.textContent = 'Enviando…'; msg.textContent = '';
      fetch(SB + '/rest/v1/rpc/reportar_problema', {
        method: 'POST',
        headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' },
        body: JSON.stringify({ p_tipo: f.querySelector('#azrTipo').value, p_mensaje: texto, p_url: url, p_referencia: ref || null, p_email: mail || null, p_navegador: navigator.userAgent.slice(0, 300) })
      }).then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j && j.message || 'error'); }, function () { throw new Error('error'); });
        form.innerHTML = '<div class="azr-ok"><span style="font-size:34px" aria-hidden="true">✅</span><b>Reporte enviado</b><p class="sub">Gracias. Lo revisaremos lo antes posible' + (mail ? ' y te escribiremos si hace falta.' : '.') + '</p><div class="azr-acc" style="justify-content:center"><button type="button" class="prim" data-cerrar>Cerrar</button></div></div>';
        form.querySelector('[data-cerrar]').focus();
      }).catch(function (err) {
        b.disabled = false; b.textContent = 'Enviar reporte';
        msg.textContent = /Demasiados/.test(err.message) ? 'Has enviado varios reportes seguidos. Prueba de nuevo en un rato.' : 'No se pudo enviar. Revisa tu conexión e inténtalo otra vez.';
      });
    });
  }
  w.AurzaneReportar = abrir;

  function montar() {
    if (/\/admin\.html$/.test(location.pathname)) return;
    var st = d.createElement('style'); st.textContent = css; d.head.appendChild(st);
    var btn = d.createElement('button');
    btn.type = 'button'; btn.className = 'azr-btn'; btn.setAttribute('aria-label', 'Reportar un problema');
    btn.innerHTML = '<span aria-hidden="true">⚑</span>';
    var tip = d.createElement('span'); tip.className = 'azr-tip'; tip.textContent = 'Reportar un problema'; tip.setAttribute('aria-hidden', 'true');
    d.body.appendChild(btn); d.body.appendChild(tip);
    btn.addEventListener('click', function () { abrir({}); });
    d.addEventListener('click', function (e) {
      var t = e.target.closest('[data-reportar]');
      if (!t) return;
      e.preventDefault();
      abrir({ tipo: t.getAttribute('data-tipo') || 'dato', referencia: t.getAttribute('data-ref') || '' });
    });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', montar); else montar();
})(window, document);
