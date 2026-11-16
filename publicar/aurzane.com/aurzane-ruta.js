/* AURZANE · «Tu siguiente paso» (16/11/2026). Al terminar un test de MIND o LIVE propone tres pasos que tienen sentido
   con ese test: otro test relacionado, una práctica o calculadora y un curso o la orientación vocacional.
   Lo carga aurzane-paleta.js. No guarda nada ni envía datos: solo enlaces. */
(function (w, d) {
  if (w.__azRuta) return; w.__azRuta = 1;
  if (!/^(mind|live)\.aurzane\.com$/.test(location.hostname)) return;
  var M = 'https://mind.aurzane.com/', L = 'https://live.aurzane.com/', C = 'https://learn.aurzane.com/curso/';
  var T = {
    ansiedad: ['Test de estrés', M + 'test-de-estres/'], depresion: ['Test de estado de ánimo', M + 'test-de-depresion/'], estres: ['Test de estrés', M + 'test-de-estres/'],
    autoestima: ['Test de autoestima', M + 'test-de-autoestima/'], burnout: ['Test de burnout', M + 'test-de-burnout/'], tdah: ['Test de TDAH en adultos', M + 'test-de-tdah/'],
    resiliencia: ['Test de resiliencia', M + 'test-de-resiliencia/'], autocompasion: ['Test de autocompasión', M + 'test-de-autocompasion/'],
    autoeficacia: ['Test de autoeficacia', M + 'test-de-autoeficacia/'], soledad: ['Test de soledad', M + 'test-de-soledad/'],
    satisfaccion: ['Test de satisfacción con la vida', M + 'test-de-satisfaccion-con-la-vida/'], personalidad: ['Test de personalidad', M + 'test-de-personalidad/'],
    bienestar: ['Test de bienestar', L + 'test-de-bienestar/'], sueno: ['Test de sueño', L + 'test-de-sueno/'], habitos: ['Test de hábitos de vida', L + 'test-de-habitos/']
  };
  var P = {
    respiracion: ['Respiración 4-7-8 guiada', M + 'ejercicios/respiracion-4-7-8/', '3 minutos para bajar la activación'],
    tierra: ['Técnica 5-4-3-2-1', M + 'ejercicios/tecnica-5-4-3-2-1/', 'Para volver al presente cuando todo se acelera'],
    escaneo: ['Escaneo corporal guiado', M + 'ejercicios/escaneo-corporal/', '7 minutos para soltar la tensión del cuerpo'],
    pausa: ['Pausa de autocompasión', M + 'ejercicios/pausa-de-autocompasion/', 'Para un momento difícil, en 3 minutos'],
    todos: ['Ejercicios guiados', M + 'ejercicios/', 'Respiración, relajación y atención, de 1 a 8 minutos']
  };
  var K = {
    ansiedad: ['Curso: gestionar la ansiedad en el día a día', C + 'ansiedad-dia-a-dia/', 'Gratis, con certificado al terminar'],
    intro: ['Curso: introducción a la psicología', C + 'introduccion-psicologia/', 'Gratis, para entender mente, cerebro y conducta'],
    ovp: ['Descubre qué estudiar', 'https://ovp.aurzane.com/', 'Evaluación vocacional completa con informe, gratis'],
    calorias: ['Calculadora de calorías e IMC', L + 'calculadora-calorias/', 'Ajusta tus hábitos con números reales']
  };
  /* test -> [test relacionado, práctica, curso u orientación] */
  var R = {
    ansiedad: ['estres', 'respiracion', 'ansiedad'], depresion: ['autocompasion', 'pausa', 'intro'], estres: ['burnout', 'escaneo', 'ansiedad'],
    autoestima: ['autocompasion', 'pausa', 'intro'], burnout: ['estres', 'escaneo', 'ansiedad'], tdah: ['habitos', 'tierra', 'intro'],
    resiliencia: ['autoeficacia', 'todos', 'intro'], autocompasion: ['autoestima', 'pausa', 'intro'], autoeficacia: ['resiliencia', 'todos', 'ovp'],
    soledad: ['satisfaccion', 'pausa', 'intro'], satisfaccion: ['bienestar', 'todos', 'intro'], personalidad: ['autoestima', 'todos', 'ovp'],
    bienestar: ['sueno', 'respiracion', 'calorias'], sueno: ['estres', 'respiracion', 'ansiedad'], habitos: ['bienestar', 'escaneo', 'calorias']
  };
  var slug = (location.pathname.match(/\/test-de-([a-z-]+)\//) || [])[1] || '';
  slug = slug === 'satisfaccion-con-la-vida' ? 'satisfaccion' : slug;
  var r = R[slug]; if (!r) return;
  var E = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  function listo() {
    if (d.body.classList.contains('hecho')) return d.getElementById('azAsis') || d.getElementById('detalle') || d.getElementById('resultado');
    var res = d.getElementById('resultados'); if (res && !res.hidden) return res;
    return null;
  }
  function pintar(sitio) {
    if (d.getElementById('azRuta') || !sitio) return;
    var t = T[r[0]], p = P[r[1]], k = K[r[2]];
    var pasos = [[t[0], t[1], 'Otro cuestionario que completa este resultado'], p, k];
    var s = d.createElement('section'); s.id = 'azRuta'; s.setAttribute('aria-labelledby', 'azRutaT');
    s.style.cssText = 'margin:22px 0;padding:18px 20px;border-radius:16px;border:1px solid rgba(127,127,127,.25);font:inherit';
    s.innerHTML = '<h3 id="azRutaT" style="margin:0 0 10px;font-size:1.05rem">Tu siguiente paso</h3><ol style="list-style:none;margin:0;padding:0;display:grid;gap:8px">' +
      pasos.map(function (x, i) {
        return '<li><a href="' + E(x[1]) + '?utm_source=ruta&amp;utm_medium=' + E(slug) + '" style="display:flex;gap:12px;align-items:center;padding:12px 14px;border-radius:12px;background:rgba(127,127,127,.08);color:inherit;text-decoration:none">' +
          '<span aria-hidden="true" style="flex:none;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-weight:700;background:var(--acento,#0F1530);color:var(--sobre-acento,#fff)">' + (i + 1) + '</span>' +
          '<span><b style="display:block">' + E(x[0]) + '</b><span style="font-size:.9rem;opacity:.75">' + E(x[2]) + '</span></span></a></li>';
      }).join('') + '</ol>';
    sitio.parentNode.insertBefore(s, sitio.nextSibling);
  }
  var n = 0, iv = setInterval(function () { var x = listo(); if (x) { pintar(x); clearInterval(iv); } if (++n > 2400) clearInterval(iv); }, 1500);
})(window, document);
