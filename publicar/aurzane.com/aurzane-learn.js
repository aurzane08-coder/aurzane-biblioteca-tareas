/* AURZANE LEARN: «dónde estoy, qué he completado y qué me toca después».
   La carga aurzane-ds.js en learn.aurzane.com. No cambia cursos, lecciones, tests ni certificados:
   - En la portada de LEARN y en el catálogo: panel «Tu aprendizaje» con cada curso empezado (lecciones abiertas,
     evaluación final, certificado), el botón para seguir donde lo dejaste y los cursos completados.
   - En la página de cada curso: tu avance y «Continuar» en lugar de «Empezar» si ya lo empezaste.
   Los datos salen de tu cuenta AURZANE ID (course_certificate_status) y de la última lección guardada en este navegador. */
(function (w, d) {
  'use strict';
  if (w.__azLearn) return; w.__azLearn = 1;
  var SB_URL = 'https://chtfpqwrrarfdjcivlad.supabase.co', SB_KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', AULA = 'https://learn.aurzane.com/cursos.html?c=';
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var p = location.pathname, esCurso = /^\/curso\/([a-z0-9-]+)\/?/.exec(p), esPortada = p === '/' || p === '/index.html', esCatalogo = /^\/cursos\/?(index\.html)?$/.test(p);
  if (!esCurso && !esPortada && !esCatalogo) return;

  function haySesion() { return /(?:^|; )aurzane-id-auth(?:\.0)?=/.test(d.cookie); }
  function script(src) { return new Promise(function (ok, ko) { var s = d.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; d.head.appendChild(s); }); }
  function cliente() {
    var a = w.supabase && w.supabase.createClient ? Promise.resolve() : script('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js');
    return a.then(function () { return w.crearClienteAurzaneID ? null : script('https://aurzane.com/aurzane-id.js'); })
      .then(function () { return w.crearClienteAurzaneID ? w.crearClienteAurzaneID(SB_URL, SB_KEY) : w.supabase.createClient(SB_URL, SB_KEY); });
  }
  function ultima(slug) { try { var u = JSON.parse(localStorage.getItem('aurzane-curso-' + slug + '-ultima') || 'null'); return u && u.ruta ? u : null; } catch (e) { return null; } }

  var css = d.createElement('style');
  css.textContent = [
    '.az-ln{max-width:1100px;margin:24px auto 8px;padding:0 20px;font-family:"Instrument Sans",system-ui,sans-serif;color:#141a33}',
    '.az-ln-caja{background:#fffdf8;border:1px solid #e2dccd;border-radius:18px;padding:22px 24px}',
    '.az-ln h2{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.55rem;margin:0 0 4px}',
    '.az-ln .sub{color:#5b5d6e;font-size:.92rem;margin:0 0 16px}',
    '.az-ln-curso{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px 20px;align-items:center;padding:14px 0;border-top:1px solid #ece6d8}',
    '.az-ln-curso:first-of-type{border-top:0}',
    '.az-ln-curso h3{font-size:1.02rem;font-weight:600;margin:0 0 6px}',
    '.az-ln-barra{height:8px;border-radius:8px;background:#efe7d4;overflow:hidden;max-width:520px}.az-ln-barra i{display:block;height:100%;background:#2e7d5b;border-radius:8px}',
    '.az-ln-dat{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:.84rem;color:#5b5d6e}',
    '.az-ln-dat b{color:#141a33;font-weight:600}',
    '.az-ln-ok{color:#1f6b4a!important;font-weight:600}',
    '.az-ln-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 18px;border-radius:999px;background:#141a3a;color:#fff!important;font-weight:600;font-size:.9rem;text-decoration:none;white-space:nowrap}',
    '.az-ln-btn.sec{background:transparent;color:#141a3a!important;border:1px solid #141a3a}',
    '.az-ln-acc{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}',
    '.az-ln-sig{font-size:.84rem;color:#5b5d6e;margin-top:6px}',
    '.az-ln-curso-pag{margin:18px 0 0;background:#fffdf8;border:1px solid #e2dccd;border-radius:14px;padding:14px 16px;color:#141a33;font-size:.92rem}',
    '@media(max-width:640px){.az-ln-curso{grid-template-columns:1fr}.az-ln-acc{justify-content:flex-start}.az-ln-caja{padding:18px 16px}}'
  ].join('\n');
  d.head.appendChild(css);

  function estadoTexto(c, st) {
    var lec = st.lecciones || 0, vis = Math.min(st.visitadas || 0, lec), pct = lec ? Math.round(vis / lec * 100) : 0;
    var min = Math.round((st.nota_minima || 0.8) * 100), nota = st.mejor_nota == null ? null : Math.round(st.mejor_nota * 100);
    var hecho = !!st.codigo;
    var datos = '<span><b>' + vis + '</b> de ' + lec + ' lecciones abiertas (' + pct + ' %)</span>';
    if (st.certificable) datos += hecho ? '<span class="az-ln-ok">Certificado obtenido</span>'
      : '<span>Evaluación final: ' + (nota == null ? 'sin hacer' : '<b>' + nota + ' %</b> (necesitas ' + min + ' %)') + '</span>';
    return { pct: pct, hecho: hecho || (!st.certificable && lec && vis >= lec), listo: !!st.listo && !hecho, datos: datos };
  }

  function filaCurso(c, st) {
    var e = estadoTexto(c, st), u = ultima(c.slug);
    var acc = '';
    if (e.hecho && st.codigo) acc = '<a class="az-ln-btn" href="https://learn.aurzane.com/certificado/?c=' + encodeURIComponent(st.codigo) + '">Ver mi certificado</a><a class="az-ln-btn sec" href="' + AULA + c.slug + '#/repaso">Repasar</a>';
    else if (e.listo) acc = '<a class="az-ln-btn" href="https://learn.aurzane.com/certificado/?curso=' + encodeURIComponent(c.slug) + '">Obtener mi certificado</a>';
    else acc = '<a class="az-ln-btn" href="' + AULA + c.slug + (u ? u.ruta : '') + '">' + (u ? 'Continuar' : 'Seguir con el curso') + '</a>';
    return '<div class="az-ln-curso"><div><h3>' + E(c.titulo) + '</h3><div class="az-ln-barra" role="img" aria-label="Avance ' + e.pct + ' %"><i style="width:' + e.pct + '%"></i></div>' +
      '<div class="az-ln-dat">' + e.datos + '</div>' + (u && !e.hecho ? '<p class="az-ln-sig">Te quedaste en: ' + E(u.titulo || 'tu última lección') + '</p>' : '') +
      (e.listo ? '<p class="az-ln-sig az-ln-ok">Ya cumples los requisitos del certificado.</p>' : '') + '</div><div class="az-ln-acc">' + acc + '</div></div>';
  }

  function insertarArriba(nodo) {
    // portada: justo después de la cabecera, antes de los cursos; catálogo: bajo el título
    var antes = esPortada ? d.getElementById('cursos') : null;
    if (antes && antes.parentNode) { antes.parentNode.insertBefore(nodo, antes); return; }
    var h1 = d.querySelector('main h1, h1'), tras = h1 && h1.nextElementSibling && /lead/.test(h1.nextElementSibling.className) ? h1.nextElementSibling : h1;
    if (tras && tras.parentNode) { nodo.style.padding = '0'; tras.parentNode.insertBefore(nodo, tras.nextSibling); }
    else (d.querySelector('main') || d.body).appendChild(nodo);
  }

  function panel(sb, cursos) {
    return Promise.all(cursos.map(function (c) { return sb.rpc('course_certificate_status', { p_course: c.slug }).then(function (r) { return { c: c, st: r.data || {} }; }, function () { return { c: c, st: {} }; }); }))
      .then(function (L) {
        if (!L.length || (L[0].st && L[0].st.sesion === false)) return;
        var emp = L.filter(function (x) { return (x.st.visitadas || 0) > 0 || ultima(x.c.slug); });
        var en = emp.filter(function (x) { return !estadoTexto(x.c, x.st).hecho; }), fin = emp.filter(function (x) { return estadoTexto(x.c, x.st).hecho; });
        var caja = d.createElement('section'); caja.className = 'az-ln'; caja.id = 'mis-cursos'; caja.setAttribute('aria-labelledby', 'azLnT');
        var html = '<div class="az-ln-caja"><h2 id="azLnT">Tu aprendizaje</h2>';
        if (!emp.length) {
          var rec = cursos.filter(function (c) { return c.nivel !== 'Avanzado'; })[0] || cursos[0];
          html += '<p class="sub">Todavía no has empezado ningún curso. Tu avance se guardará aquí, con tu cuenta.</p>' +
            (rec ? '<a class="az-ln-btn" href="' + AULA + rec.slug + '">Empezar «' + E(rec.titulo) + '»</a>' : '');
        } else {
          html += '<p class="sub">' + (en.length ? 'Sigue donde lo dejaste. ' : '') + (fin.length ? 'Has completado ' + fin.length + (fin.length === 1 ? ' curso.' : ' cursos.') : '') + '</p>';
          html += en.map(function (x) { return filaCurso(x.c, x.st); }).join('');
          if (fin.length) html += '<h3 style="font-family:Bodoni Moda,serif;font-weight:500;font-size:1.15rem;margin:18px 0 0">Completados</h3>' + fin.map(function (x) { return filaCurso(x.c, x.st); }).join('');
        }
        caja.innerHTML = html + '</div>';
        insertarArriba(caja);
        if (location.hash === '#mis-cursos') caja.scrollIntoView();
      });
  }

  function paginaCurso(sb, slug) {
    var btn = d.querySelector('a.btn[href*="cursos.html?c=' + slug + '"]');
    var u = ultima(slug);
    var poner = function (st) {
      var cont = btn ? btn.parentNode : null; if (!cont) return;
      var caja = d.createElement('div'); caja.className = 'az-ln-curso-pag';
      if (!sb) { caja.innerHTML = 'Tu avance se guarda con tu cuenta AURZANE ID. <a href="https://aurzane.com/mi-aurzane.html?next=' + encodeURIComponent(location.href) + '">Iniciar sesión</a>'; cont.parentNode.insertBefore(caja, cont.nextSibling); return; }
      if (!st || !((st.visitadas || 0) > 0 || u)) return;
      var e = estadoTexto({ slug: slug }, st);
      if (btn) { btn.textContent = e.hecho ? 'Repasar el curso' : 'Continuar el curso'; if (u && !e.hecho) btn.href = AULA + slug + u.ruta; }
      caja.innerHTML = '<div class="az-ln-barra" role="img" aria-label="Avance ' + e.pct + ' %" style="margin-bottom:8px"><i style="width:' + e.pct + '%"></i></div><div class="az-ln-dat" style="margin:0">' + e.datos + '</div>' +
        (u && !e.hecho ? '<p class="az-ln-sig">Te quedaste en: ' + E(u.titulo || 'tu última lección') + '</p>' : '') +
        (st.codigo ? '<p class="az-ln-sig"><a href="https://learn.aurzane.com/certificado/?c=' + encodeURIComponent(st.codigo) + '">Ver mi certificado</a></p>' : e.listo ? '<p class="az-ln-sig"><a href="https://learn.aurzane.com/certificado/?curso=' + encodeURIComponent(slug) + '">Obtener mi certificado</a></p>' : '');
      cont.parentNode.insertBefore(caja, cont.nextSibling);
    };
    if (!sb) return poner(null);
    sb.rpc('course_certificate_status', { p_course: slug }).then(function (r) { poner(r.data); }, function () {});
  }

  function iniciar() {
    if (esCurso) {
      if (!haySesion()) return paginaCurso(null, esCurso[1]);
      return cliente().then(function (sb) { paginaCurso(sb, esCurso[1]); }, function () {});
    }
    if (!haySesion()) {
      if (location.hash === '#mis-cursos') {
        var c = d.createElement('section'); c.className = 'az-ln'; c.id = 'mis-cursos';
        c.innerHTML = '<div class="az-ln-caja"><h2>Tu aprendizaje</h2><p class="sub">Inicia sesión con tu cuenta AURZANE ID para ver los cursos que llevas, lo que te queda y tus certificados.</p><a class="az-ln-btn" href="https://aurzane.com/mi-aurzane.html?next=' + encodeURIComponent(location.href) + '">Iniciar sesión</a></div>';
        insertarArriba(c); c.scrollIntoView();
      }
      return;
    }
    cliente().then(function (sb) {
      return sb.rpc('course_catalog_public').then(function (r) { if (!r.error && r.data && r.data.length) return panel(sb, r.data); });
    }).catch(function () {});
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(window, document);
