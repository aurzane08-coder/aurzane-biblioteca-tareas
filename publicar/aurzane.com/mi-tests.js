/* Mi AURZANE · «Mis tests»: historial de resultados, evolución y recordatorio mensual.
   Los resultados se guardan desde cada test (aurzane-estilo.js) en aurzane.com/mi/tests.php. */
(function (w, d) {
  var API = '/mi/tests.php';
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var TESTS = [['https://mind.aurzane.com/test-de-ansiedad/', 'Ansiedad'], ['https://mind.aurzane.com/test-de-estres/', 'Estrés'], ['https://mind.aurzane.com/test-de-autoestima/', 'Autoestima'], ['https://live.aurzane.com/test-de-sueno/', 'Sueño'], ['https://live.aurzane.com/test-de-bienestar/', 'Bienestar']];
  var css = d.createElement('style');
  css.textContent = '#cardMisTests{grid-column:1/-1}.mt-lista{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin-top:6px}' +
    '.mt-item{border:1px solid var(--border);border-radius:12px;padding:14px;background:rgba(127,127,127,.04)}.mt-item h4{font-size:.95rem;margin:0 0 4px}' +
    '.mt-item .v{font-size:1.4rem;font-weight:700;font-variant-numeric:tabular-nums}.mt-item .v small{font-size:.8rem;font-weight:400;color:var(--text-dim)}' +
    '.mt-item .n{font-size:.85rem;color:var(--text-dim);margin:2px 0 8px}.mt-item svg{display:block;width:100%;height:46px;margin:6px 0}' +
    '.mt-item .acc{display:flex;gap:12px;font-size:.82rem}.mt-item .acc a,.mt-item .acc button{color:inherit;background:none;border:0;padding:0;cursor:pointer;text-decoration:underline;font:inherit}' +
    '.mt-rec{display:flex;gap:10px;align-items:flex-start;margin-top:16px;font-size:.88rem}.mt-rec input{margin-top:3px}.mt-vacio{font-size:.9rem;color:var(--text-dim)}.mt-vacio a{color:inherit}';
  d.head.appendChild(css);

  function sesionYCliente() { try { return typeof sbId !== 'undefined' ? sbId : null; } catch (e) { return null; } }
  function ck(n) { var m = d.cookie.match(new RegExp('(?:^|; )' + n + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : null; }
  function llamar(tk, datos) {
    datos.token = tk;
    return fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(datos) }).then(function (r) { return r.json(); });
  }
  function linea(vals, max) {
    if (vals.length < 2) return '';
    var W = 240, H = 46, mx = max || Math.max.apply(null, vals) || 1;
    var pts = vals.map(function (v, i) { return (i * W / (vals.length - 1)).toFixed(1) + ',' + (H - 4 - v / mx * (H - 8)).toFixed(1); });
    return '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img" aria-label="Evolución: ' + vals.join(', ') + '"><polyline points="' + pts.join(' ') + '" fill="none" stroke="currentColor" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>';
  }
  function pintar(card, tk, datos) {
    var cuerpo = card.querySelector('.mt-cuerpo'), grupos = {};
    (datos.tests || []).forEach(function (t) { (grupos[t.clave] = grupos[t.clave] || []).push(t); });
    var claves = Object.keys(grupos).sort(function (a, b) { return grupos[b][grupos[b].length - 1].fecha.localeCompare(grupos[a][grupos[a].length - 1].fecha); });
    var html = claves.length ? '<div class="mt-lista">' + claves.map(function (k) {
      var g = grupos[k].sort(function (a, b) { return a.fecha.localeCompare(b.fecha); }), u = g[g.length - 1];
      var nums = g.map(function (t) { return t.valor; }).filter(function (v) { return typeof v === 'number'; });
      var dif = nums.length > 1 ? Math.round((nums[nums.length - 1] - nums[nums.length - 2]) * 10) / 10 : null;
      return '<div class="mt-item"><h4>' + E(u.titulo) + '</h4>' +
        (u.valor != null ? '<div class="v">' + E(String(u.valor).replace('.', ',')) + (u.max ? ' <small>de ' + E(u.max) + '</small>' : '') + (dif ? ' <small>(' + (dif > 0 ? '+' : '') + String(dif).replace('.', ',') + ' desde la vez anterior)</small>' : '') + '</div>' : '') +
        '<p class="n">' + E(u.nivel) + ' · ' + new Date(u.fecha + 'Z').toLocaleDateString('es-ES') + ' · ' + g.length + (g.length === 1 ? ' vez' : ' veces') + '</p>' +
        linea(nums.slice(-12), u.max) +
        '<div class="acc">' + (u.url ? '<a href="' + E(u.url) + '">Repetir el test</a>' : '') + '<button type="button" data-borrar="' + E(k) + '">Borrar historial</button></div></div>';
    }).join('') + '</div>' : '<p class="mt-vacio">Todavía no hay resultados guardados. Haz un test con tu sesión iniciada y aparecerá aquí, para que puedas ver tu evolución con el tiempo. Por ejemplo: ' +
      TESTS.map(function (t) { return '<a href="' + t[0] + '">' + t[1] + '</a>'; }).join(', ') + '.</p>';
    html += '<label class="mt-rec"><input type="checkbox" id="mtRec"' + (datos.recordatorio ? ' checked' : '') + '> <span>Recordarme por correo cuando haya pasado un mes desde mi último test, para repetirlo y ver si hay cambios.</span></label>' +
      '<p class="mt-vacio" style="margin-top:8px;font-size:.8rem">Solo tú ves tus resultados. Los tests son orientativos y no sustituyen una valoración profesional.</p>';
    cuerpo.innerHTML = html;
    cuerpo.querySelector('#mtRec').addEventListener('change', function (e) { llamar(tk, { accion: 'recordatorio', activo: e.target.checked }); });
    cuerpo.querySelectorAll('[data-borrar]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (b.dataset.ok !== '1') { b.dataset.ok = '1'; b.textContent = '¿Seguro? Pulsa otra vez'; return; }
        llamar(tk, { accion: 'borrar', clave: b.dataset.borrar }).then(function () { return llamar(tk, { accion: 'listar' }); }).then(function (j) { pintar(card, tk, j); });
      });
    });
  }
  async function iniciar() {
    var grid = d.getElementById('gridCuenta'), sb = sesionYCliente();
    if (!grid || !sb || d.getElementById('cardMisTests')) return;
    var s = (await sb.auth.getSession()).data.session; if (!s) return;
    var card = d.createElement('div');
    card.className = 'card cuenta-card acc-mind'; card.id = 'cardMisTests'; card.setAttribute('data-categoria', 'Herramientas'); card.setAttribute('data-texto', 'tests resultados evolucion historial recordatorio');
    card.innerHTML = '<a id="tests"></a><div class="card-body" style="padding:0"><h3>Mis tests y mi evolución</h3><p class="card-sub">Tus resultados guardados, cómo han cambiado y cuándo repetirlos.</p><div class="mt-cuerpo"><p class="mt-vacio">Cargando…</p></div></div>';
    var ref = d.getElementById('cardProcesoOVP');
    ref ? ref.parentNode.insertBefore(card, ref.nextSibling) : grid.insertBefore(card, grid.firstChild);
    var pend = []; try { pend = JSON.parse(ck('azPend') || '[]'); } catch (e) {}
    if (pend.length) {
      var r = await llamar(s.access_token, { accion: 'guardar', resultados: pend }).catch(function () { return {}; });
      if (r.ok) d.cookie = 'azPend=; domain=.aurzane.com; path=/; max-age=0; secure; samesite=lax';
    }
    var j = await llamar(s.access_token, { accion: 'listar' }).catch(function () { return { error: 1 }; });
    if (j.error) { card.querySelector('.mt-cuerpo').innerHTML = '<p class="mt-vacio">No se pudo cargar tu historial ahora mismo. Recarga la página en un momento.</p>'; return; }
    pintar(card, s.access_token, j);
    if (location.hash === '#tests') card.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function esperar() {
    var p = d.getElementById('vistaPanel');
    if (p && !p.classList.contains('panel-hide')) { iniciar(); return; }
    if (p) new MutationObserver(function (m, o) { if (!p.classList.contains('panel-hide')) { o.disconnect(); iniciar(); } }).observe(p, { attributes: true, attributeFilter: ['class'] });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', esperar); else esperar();
})(window, document);
