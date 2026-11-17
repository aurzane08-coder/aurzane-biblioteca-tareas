/* Mi AURZANE · «¿Cómo voy?» (17/11/2026, etapa 3 de la auditoría, tarea 38).
   Resumen de todo lo que la persona hace en el ecosistema, con datos reales de su cuenta:
   tests guardados (aurzane.com/mi/tests.php), cursos y certificados de LEARN y guardados (Supabase con RLS:
   cada persona solo lee lo suyo). Debajo, el siguiente paso que más sentido tiene. Las cifras no se inventan:
   si algo no se puede leer, el recuadro dice «Sin datos». */
(function (w, d) {
  function cli() { try { return typeof sbId !== 'undefined' ? sbId : null; } catch (e) { return null; } }
  function pon(id, t) { var e = d.getElementById(id); if (e) e.textContent = t; }
  function fecha(f) { try { return new Date(f.length <= 16 ? f + 'Z' : f).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }); } catch (e) { return ''; } }
  function q(b) { return Promise.resolve(b).then(function (r) { return r; }, function () { return { error: 1 }; }); }   // las consultas de Supabase no traen .catch
  async function iniciar() {
    var sb = cli(); if (!sb || !d.getElementById('statTests')) return;
    var s = (await sb.auth.getSession()).data.session; if (!s) return;
    var tests = await fetch('/mi/tests.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ accion: 'listar', token: s.access_token }) })
      .then(function (r) { return r.json(); }).catch(function () { return null; });
    var cert = await q(sb.from('course_certificates').select('course_id', { count: 'exact', head: true }));
    var guard = await q(sb.from('guardados').select('url', { count: 'exact', head: true }));
    var lecs = await q(sb.from('course_progress').select('lesson_id', { count: 'exact', head: true }).not('completado_at', 'is', null));
    var lista = tests && tests.tests ? tests.tests : null, sig = '';
    if (!lista) pon('statTests', 'Sin datos');
    else if (!lista.length) { pon('statTests', '0'); sig = 'Siguiente paso: <a href="https://mind.aurzane.com/test-de-ansiedad/">haz tu primer test</a> con la sesión iniciada y verás aquí cómo evolucionas.'; }
    else {
      var claves = {}; lista.forEach(function (t) { claves[t.clave] = t; });
      var ult = lista.slice().sort(function (a, b) { return a.fecha.localeCompare(b.fecha); }).pop();
      pon('statTests', lista.length + (lista.length === 1 ? ' resultado' : ' resultados') + ' en ' + Object.keys(claves).length + (Object.keys(claves).length === 1 ? ' test' : ' tests'));
      var dias = (Date.now() - Date.parse(ult.fecha + 'Z')) / 864e5;
      if (dias > 30 && ult.url) sig = 'Siguiente paso: tu último test fue «' + ult.titulo.replace(/[<>]/g, '') + '» el ' + fecha(ult.fecha) + '. <a href="' + ult.url.replace(/"/g, '') + '">Repítelo</a> para ver si algo ha cambiado.';
    }
    pon('statCert', cert && !cert.error ? String(cert.count || 0) : 'Sin datos');
    pon('statGuardados', guard && !guard.error ? String(guard.count || 0) : 'Sin datos');
    if (!sig && lecs && !lecs.error && lecs.count > 0 && (!cert || !cert.count)) sig = 'Siguiente paso: llevas ' + lecs.count + (lecs.count === 1 ? ' lección completada' : ' lecciones completadas') + '. <a href="#secCursos">Continúa tu curso</a> hasta el certificado.';
    if (!sig && lecs && !lecs.error && !lecs.count) sig = 'Siguiente paso: los cursos de LEARN son gratis y con certificado. <a href="#secCursos">Empieza uno</a>.';
    if (lista && lista.length) evolucion(lista);
    var p = d.getElementById('comoVoySig'), st = d.getElementById('statTests'), caja = st && st.closest('.stats-resumen');
    if (p && sig) {
      // el panel recoloca las cifras dentro de la cabecera: el siguiente paso va justo debajo de ellas, donde se ve
      if (caja && caja.parentNode && p.previousElementSibling !== caja) { caja.parentNode.insertBefore(p, caja.nextSibling); }
      p.innerHTML = '<b>¿Cómo voy?</b> ' + sig.replace(/^Siguiente paso: /, 'Tu siguiente paso: '); p.hidden = false;
      p.style.cssText = 'margin:12px 0 0;font-size:.95rem;padding:10px 14px;border-radius:12px;background:rgba(127,127,127,.12)';
    }
  }
  /* Tu evolución (17/11/2026, plan de la auditoría final, punto 49): para cada test repetido, una línea con sus
     resultados en el tiempo. Solo muestra los datos (puntuación y nivel que dio el propio test); no juzga si es mejor o peor. */
  function evolucion(lista) {
    if (d.getElementById('azEvolucion')) return;
    var por = {}; lista.forEach(function (t) { if (t.valor != null && t.max) (por[t.clave] = por[t.clave] || []).push(t); });
    var claves = Object.keys(por).filter(function (k) { return por[k].length >= 2; });
    var unico = Object.keys(por).filter(function (k) { return por[k].length === 1; });
    if (!claves.length && !unico.length) return;
    var esc = function (x) { return String(x == null ? '' : x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var html = '<h2 style="margin:0 0 4px;font-size:1.15rem">Tu evolución en los tests</h2><p style="margin:0 0 14px;opacity:.75;font-size:.9rem">Cada punto es una vez que hiciste el test con la sesión iniciada. Es orientativo: no sustituye una valoración profesional.</p>';
    claves.forEach(function (k) {
      var r = por[k].slice().sort(function (a, b) { return a.fecha.localeCompare(b.fecha); }).slice(-12);
      var W = 260, H = 64, n = r.length, pts = r.map(function (t, i) { return [12 + i * (W - 24) / Math.max(1, n - 1), H - 10 - (t.valor / t.max) * (H - 20)]; });
      var svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" height="' + H + '" role="img" aria-label="Resultados de ' + esc(r[0].titulo) + ' en el tiempo" style="max-width:340px;display:block">' +
        '<polyline fill="none" stroke="currentColor" stroke-opacity=".55" stroke-width="2" points="' + pts.map(function (q) { return q[0].toFixed(1) + ',' + q[1].toFixed(1); }).join(' ') + '"/>' +
        pts.map(function (q, i) { return '<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="' + (i === n - 1 ? 5 : 3.5) + '" fill="currentColor"><title>' + esc(fecha(r[i].fecha) + ': ' + r[i].valor + ' de ' + r[i].max + (r[i].nivel ? ', ' + r[i].nivel : '')) + '</title></circle>'; }).join('') + '</svg>';
      var a = r[0], z = r[n - 1];
      html += '<div style="padding:12px 0;border-top:1px solid rgba(127,127,127,.2)"><b>' + esc(z.titulo) + '</b>' + svg +
        '<p style="margin:4px 0 0;font-size:.88rem;opacity:.85">Primera vez (' + esc(fecha(a.fecha)) + '): ' + esc(a.valor) + ' de ' + esc(a.max) + (a.nivel ? ', ' + esc(a.nivel) : '') +
        '. Última (' + esc(fecha(z.fecha)) + '): ' + esc(z.valor) + ' de ' + esc(z.max) + (z.nivel ? ', ' + esc(z.nivel) : '') + '.' + (z.url ? ' <a href="' + esc(z.url) + '">Repetirlo</a>' : '') + '</p></div>';
    });
    if (unico.length) html += '<p style="margin:12px 0 0;font-size:.9rem;border-top:1px solid rgba(127,127,127,.2);padding-top:12px">Has hecho ' + unico.length + (unico.length === 1 ? ' test una vez' : ' tests una vez') + ': repítelos dentro de unas semanas y aquí verás cómo cambian.</p>';
    var sec = d.createElement('section'); sec.id = 'azEvolucion'; sec.className = 'panel';
    sec.style.cssText = 'margin:18px 0;padding:18px 20px;border-radius:16px;border:1px solid rgba(127,127,127,.25)'; sec.innerHTML = html;
    var st = d.getElementById('statTests'), caja = st && st.closest('.stats-resumen'), sig = d.getElementById('comoVoySig');
    var tras = (sig && !sig.hidden ? sig : caja) || st; if (!tras || !tras.parentNode) return;
    tras.parentNode.insertBefore(sec, tras.nextSibling);
  }
  function esperar() {
    var p = d.getElementById('vistaPanel');
    if (p && !p.classList.contains('panel-hide')) { iniciar(); return; }
    if (p) new MutationObserver(function (m, o) { if (!p.classList.contains('panel-hide')) { o.disconnect(); iniciar(); } }).observe(p, { attributes: true, attributeFilter: ['class'] });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', esperar); else esperar();
})(window, document);
