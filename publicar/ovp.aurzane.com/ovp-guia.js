/* Guía de AURZANE OVP: qué evaluaciones hacer según tu objetivo (rutas Básica, Estándar y Premium).
   Todas las evaluaciones están abiertas: la guía solo orienta y, si quieres, marca las de una ruta con un clic.
   En la portada (index.html) se muestra antes de las preguntas frecuentes; en portal.html, encima del selector. */
(function (d, w) {
  if (w.__ovpGuia) return; w.__ovpGuia = 1;
  var RUTAS = [
    { id: 'basico', nombre: 'Ruta Básica', meta: 'Descubrir hacia dónde ir', min: 47, tests: ['chaside', 'holland', 'chte'],
      para: 'Si todavía no sabes qué área o carrera te encaja.',
      porque: 'Cruza dos miradas sobre tus intereses (si coinciden, la recomendación es más sólida) y te dice qué hábitos de estudio reforzar para que te vaya bien en lo que elijas.' },
    { id: 'estandar', nombre: 'Ruta Estándar', meta: 'Elegir con seguridad', min: 55, tests: ['chaside', 'holland', 'af5', 'chte'],
      para: 'Si dudas entre opciones o no te sientes capaz de la que te gusta.',
      porque: 'Añade cómo te ves a ti mismo en lo académico, social, emocional, familiar y físico. Ayuda a entender de dónde vienen las dudas y a elegir algo que encaje contigo, no solo con tus gustos.' },
    { id: 'premium', nombre: 'Ruta Premium', meta: 'Decidir con datos completos', min: 196, tests: ['chaside', 'holland', 'af5', 'chte', 'apt_b', 'apt_a'],
      para: 'Si apuntas a una carrera exigente o quieres comparar lo que te gusta con lo que hoy se te da bien.',
      porque: 'Suma las aptitudes (verbal, numérica, abstracta, mecánica, espacial, lenguaje y rapidez). Es la lectura más completa: ideal para ingenierías, ciencias de la salud o arquitectura, y para decidir entre dos caminos. Hazla en varias sesiones y descansado.' }
  ];
  var TESTS = {
    chaside: ['CHASIDE', 'Señala las áreas (ciencias, salud, arte, administración...) donde tus intereses y aptitudes coinciden, con carreras afines.'],
    holland: ['Holland (RIASEC)', 'Describe tu perfil de trabajo (realista, investigador, artístico, social, emprendedor o convencional) y confirma CHASIDE desde otro ángulo.'],
    chte: ['Hábitos de estudio', 'Muestra cómo planificas, te concentras y estudias, y qué mejorar para rendir en la carrera que elijas.'],
    af5: ['AF5 (autoconcepto)', 'Mide cómo te valoras en cinco áreas de tu vida. Explica dudas y bloqueos a la hora de decidir.'],
    apt_a: ['APT-A', 'Aptitudes verbal, numérica, abstracta y mecánica: qué tipo de tareas resuelves con más facilidad.'],
    apt_b: ['APT-B', 'Ortografía, lenguaje, relaciones espaciales y velocidad y precisión: útil para carreras técnicas, de diseño o administrativas.']
  };
  var hm = function (m) { return m >= 60 ? Math.floor(m / 60) + ' h' + (m % 60 ? ' ' + (m % 60) + ' min' : '') : m + ' min'; };
  var css = '.og{margin:0 0 26px;font:inherit;color:inherit}.og h3{font-family:"Bodoni Moda",serif;font-size:1.35rem;margin:0 0 6px;font-weight:600}' +
    '.og>p{margin:0 0 16px;color:var(--ink-2,var(--text-dim,inherit));font-size:.93rem;max-width:68ch}' +
    '.og-rutas{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}' +
    '.og-r{border:1.5px solid var(--line-2,var(--border,rgba(127,127,127,.3)));border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:8px;background:var(--navy-2,var(--surface,transparent))}' +
    '.og-r.sel{border-color:var(--gold,#c9a24b)}.og-n{font-size:.8rem;color:var(--accent-text,var(--gold-light,#8a6a28));font-weight:600}' +
    '.og-m{font-family:"Bodoni Moda",serif;font-size:1.15rem;line-height:1.25}.og-r p{margin:0;font-size:.86rem;line-height:1.5;color:var(--ink-2,var(--text-dim,inherit))}' +
    '.og-t{font-size:.8rem;color:var(--ink-3,var(--text-dim,inherit))}.og-r button,.og-r a.og-b{margin-top:auto;min-height:44px;border-radius:99px;border:1px solid var(--gold,#c9a24b);background:transparent;color:inherit;font:inherit;font-weight:600;cursor:pointer;text-align:center;text-decoration:none;display:flex;align-items:center;justify-content:center;padding:0 14px}' +
    '.og-r button:hover,.og-r a.og-b:hover,.og-r.sel button{background:var(--gold,#c9a24b);color:var(--navy,#0f1530)}.og-r button:focus-visible,.og-r a.og-b:focus-visible{outline:2px solid var(--gold-light,#e8cd8f);outline-offset:2px}' +
    '.og details{margin-top:14px;border-top:1px solid var(--line-2,var(--border,rgba(127,127,127,.3)));padding-top:10px}.og summary{cursor:pointer;font-weight:600;font-size:.92rem;min-height:32px}' +
    '.og dl{margin:8px 0 0;display:grid;grid-template-columns:minmax(120px,170px) 1fr;gap:6px 14px;font-size:.86rem}.og dt{font-weight:600}.og dd{margin:0;color:var(--ink-2,var(--text-dim,inherit))}' +
    '@media(max-width:760px){.og-rutas{grid-template-columns:1fr}.og dl{grid-template-columns:1fr}.og dd{margin-bottom:6px}}';
  function guia(enPortal, selId) {
    var s = d.createElement('section'); s.className = 'og'; s.setAttribute('aria-label', 'Guía para elegir tus evaluaciones');
    s.innerHTML = '<h3>¿Qué evaluaciones hacer?</h3><p>Todas están abiertas y son gratis: elige las que quieras. Si no sabes por dónde empezar, estas tres rutas te orientan según lo que buscas. Cada evaluación que añades hace tu informe más completo.</p>' +
      '<div class="og-rutas">' + RUTAS.map(function (r) {
        return '<div class="og-r" data-ruta="' + r.id + '"><span class="og-n">' + r.nombre + '</span><span class="og-m">' + r.meta + '</span><p><b>Para quién:</b> ' + r.para + '</p><p><b>Por qué te ayuda:</b> ' + r.porque + '</p>' +
          '<span class="og-t">' + r.tests.map(function (k) { return TESTS[k][0]; }).join(' + ') + ' · unos ' + hm(r.min) + '</span>' +
          (enPortal ? '<button type="button" data-og="' + r.id + '">Elegir esta ruta</button>' : '<a class="og-b" href="https://ovp.aurzane.com/portal.html?ruta=' + r.id + '">Empezar esta ruta</a>') + '</div>';
      }).join('') + '</div><details><summary>Para qué sirve cada evaluación</summary><dl>' +
      Object.keys(TESTS).map(function (k) { return '<dt>' + TESTS[k][0] + '</dt><dd>' + TESTS[k][1] + '</dd>'; }).join('') + '</dl></details>';
    if (enPortal) s.addEventListener('click', function (e) { var b = e.target.closest('[data-og]'); if (b) marcar(selId, b.dataset.og, s); });
    return s;
  }
  function marcar(selId, ruta, s) {
    var r = RUTAS.filter(function (x) { return x.id === ruta; })[0]; if (!r) return;
    var ins = d.querySelectorAll('#' + selId + ' input[type=checkbox]:not(:disabled)'); if (!ins.length) return;
    ins.forEach(function (i) { var q = r.tests.indexOf(i.value) >= 0; if (i.checked !== q) { i.checked = q; i.dispatchEvent(new Event('change', { bubbles: true })); } });
    if (s) s.querySelectorAll('.og-r').forEach(function (c) { c.classList.toggle('sel', c.dataset.ruta === ruta); });
  }
  function iniciar() {
    var st = d.createElement('style'); st.textContent = css; d.head.appendChild(st);
    if (/portal\.html/.test(location.pathname)) {
      var ruta = new URLSearchParams(location.search).get('ruta');
      ['selectorInicio', 'selectorProceso'].forEach(function (id) {
        var sel = d.getElementById(id); if (!sel) return;
        var g = guia(true, id); sel.parentNode.insertBefore(g, sel);
        if (ruta && id === 'selectorInicio') {
          var hecho = false, mo = new MutationObserver(function () { if (!hecho && sel.querySelector('input')) { hecho = true; mo.disconnect(); marcar(id, ruta, g); } });
          mo.observe(sel, { childList: true }); if (sel.querySelector('input')) { hecho = true; mo.disconnect(); marcar(id, ruta, g); }
        }
      });
    } else {
      var faq = d.getElementById('preguntas'); if (!faq) return;
      var sec = d.createElement('div'); sec.className = 'section'; sec.id = 'guia';
      var w_ = d.createElement('div'); w_.appendChild(guia(false)); sec.appendChild(w_);
      faq.parentNode.insertBefore(sec, faq);
    }
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})(document, window);
