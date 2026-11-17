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
    else if (!lista.length) { pon('statTests', 'Ninguno todavía'); sig = 'Siguiente paso: <a href="https://mind.aurzane.com/test-de-ansiedad/">haz tu primer test</a> con la sesión iniciada y verás aquí cómo evolucionas.'; }
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
    var p = d.getElementById('comoVoySig'); if (p && sig) { p.innerHTML = sig; p.hidden = false; }
  }
  function esperar() {
    var p = d.getElementById('vistaPanel');
    if (p && !p.classList.contains('panel-hide')) { iniciar(); return; }
    if (p) new MutationObserver(function (m, o) { if (!p.classList.contains('panel-hide')) { o.disconnect(); iniciar(); } }).observe(p, { attributes: true, attributeFilter: ['class'] });
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', esperar); else esperar();
})(window, document);
