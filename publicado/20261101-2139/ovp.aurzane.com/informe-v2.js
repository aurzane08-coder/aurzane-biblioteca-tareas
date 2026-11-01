/* =====================================================================
   informe-v2.js — AURZANE OVP
   Informe integrado que se arma con las evaluaciones que la persona
   eligió y completó (de 1 a 6), en lugar de exigir el plan completo.
   Se carga DESPUÉS de informe-shared.js: reutiliza sus tablas, claves,
   baremos, funciones compute* y gráficos SVG, y reemplaza
   generateReportFromData por esta versión.

   También expone la descarga del informe en PDF y en Word (.docx)
   (ver informe-export.js).
   ===================================================================== */
(function(global){
  'use strict';

  var ORDEN = ['chaside','holland','af5','chte','apt_b','apt_a'];
  var NOMBRE_TEST = {
    chaside: 'CHASIDE',
    holland: 'Holland (RIASEC)',
    af5: 'AF5 (autoconcepto)',
    chte: 'Hábitos de Estudio',
    apt_b: 'APT-B',
    apt_a: 'APT-A'
  };

  // Ejemplos de carreras por tipo RIASEC, usados solo cuando la persona
  // hizo Holland pero no CHASIDE (CHASIDE ya trae su propio catálogo).
  var HOLLAND_CARRERAS = {
    R: ['Ingeniería Civil','Ingeniería Mecánica','Mecatrónica','Agronomía','Ingeniería Ambiental','Tecnologías en electricidad y electrónica','Carreras técnicas y militares de campo'],
    I: ['Medicina','Biología','Bioquímica','Química','Física','Ingeniería de Software','Ciencia de Datos'],
    A: ['Arquitectura','Diseño Gráfico','Artes Visuales','Música','Comunicación Audiovisual','Diseño de Interiores','Literatura'],
    S: ['Psicología','Educación','Enfermería','Trabajo Social','Fisioterapia','Fonoaudiología','Orientación y consejería'],
    E: ['Administración de Empresas','Derecho','Marketing','Relaciones Internacionales','Ciencias Políticas','Comercio Exterior','Emprendimiento'],
    C: ['Contabilidad y Auditoría','Finanzas','Economía','Estadística','Administración Pública','Gestión de la Información','Logística']
  };

  function esc(v){ return (typeof escapeHtml === 'function') ? escapeHtml(v) : String(v == null ? '' : v); }
  function txt(v, f){ return (typeof safeText === 'function') ? safeText(v, f) : esc(v || f || ''); }
  function lista(arr, conj){
    conj = conj || 'y';
    if(arr.length <= 1) return arr.join('');
    return arr.slice(0, -1).join(', ') + ' ' + conj + ' ' + arr[arr.length - 1];
  }
  function cen(c){ return c == null ? '—' : c; }
  // Baremo del AF5 según la edad cuando el profesional no fijó uno.
  function grupoPorEdad(edad){
    var e = parseInt(edad, 10);
    if(!e) return 'adulto';
    if(e <= 12) return 'primaria';
    if(e <= 14) return 'eso12';
    if(e <= 16) return 'eso34';
    if(e <= 18) return 'bach';
    if(e <= 25) return 'universitario';
    return 'adulto';
  }
  function sexoNorma(s){
    var v = String(s || '').trim().toLowerCase();
    if(v === 'f' || v.indexOf('fem') === 0 || v === 'mujer') return 'F';
    if(v === 'm' || v.indexOf('mas') === 0 || v === 'hombre' || v === 'varon' || v === 'varón') return 'M';
    return '';
  }
  function romano(i){ return ['i','ii','iii','iv','v','vi','vii','viii','ix','x'][i] || '·'; }

  // Evaluaciones que entran al informe: las completadas, en orden fijo.
  function testsDelInforme(cliente){
    var acts = (cliente && cliente.activaciones) || [];
    return ORDEN.filter(function(k){
      return acts.some(function(a){ return a.test_key === k && a.completado; });
    });
  }

  function generar(cliente, membrete, incluidosParam, profesional){
    membrete = membrete || {};
    profesional = profesional || global.__ovpProfesionalActual || (global.OVPOpciones && global.OVPOpciones.FIRMA_RESPALDO) ||
      { nombre: 'Psi. Cl. Adrian Sánchez Samaniego', titulo: 'Psicólogo Clínico', registro: 'Registro SENESCYT N.º 1033-2023-2618464' };
    var firmaNombre = txt(profesional.nombre);
    var firmaLinea = txt(String(profesional.nombre || '').replace(/^((Psi|Psic|Ps|Cl|Lic|Dr|Dra|Mgs|Msc|Mg|PhD)\.?\s+)+/i, ''));
    var firmaTitulo = profesional.titulo ? txt(profesional.titulo) : '';
    var firmaRegistro = profesional.registro ? txt(profesional.registro) : '';
    // El profesional predeterminado firma con su firma manuscrita en lugar de su nombre
    var conFirma = /S[aá]nchez Samaniego/i.test(String(profesional.nombre || ''));
    var aCargo = conFirma ? (firmaTitulo || 'Psicólogo clínico') : firmaNombre;
    var incluidos = Array.isArray(incluidosParam) && incluidosParam.length ? incluidosParam : testsDelInforme(cliente);
    var tiene = function(k){ return incluidos.indexOf(k) !== -1; };
    var report = document.getElementById('reportContent');
    if(!report) return;

    if(incluidos.length === 0){
      report.innerHTML = '<p style="padding:28px;">Todavía no hay evaluaciones completadas para armar el informe.</p>';
      return;
    }

    // ---------------- datos de la persona ----------------
    var nombreRaw = cliente.nombre || '';
    var primerNombreRaw = nombreRaw.split(' ')[0] || '';
    var nombre = txt(nombreRaw, '—');
    var primerNombre = txt(primerNombreRaw, 'la persona evaluada');
    var edad = cliente.edad ? txt(cliente.edad) + ' años' : '—';
    var fechaNac = cliente.fecha_nacimiento ? esc(new Date(cliente.fecha_nacimiento).toLocaleDateString('es-EC')) : '—';
    var ultimaFecha = (cliente.activaciones || []).filter(function(a){ return incluidos.indexOf(a.test_key) !== -1; })
      .map(function(a){ return a.completado_at; }).filter(Boolean).sort().pop();
    var fecha = ultimaFecha ? new Date(ultimaFecha).toLocaleDateString('es-EC') : new Date().toLocaleDateString('es-EC');
    var institucion = txt(cliente.institucion || membrete.institucion, '—');
    var curso = txt(cliente.curso, '—');
    var motivo = esc(cliente.motivo_consulta || '');
    var expectativas = esc(cliente.expectativas || '');
    var dudas = esc(cliente.dudas_iniciales || '');
    var entrevista = cliente.entrevista_realizada || '';
    var ENTREVISTA_LABEL = { estudiante: 'al estudiante', familia: 'a la familia', ambos: 'al estudiante y a su familia' };
    var marca = txt(membrete.nombre_marca, 'AURZANE');

    // ---------------- cálculos por instrumento ----------------
    var cha = null, holland = null, af5 = null, cht = null, aptB = null, aptA = null;

    if(tiene('chaside')){
      var ranked = computeChaside();
      cha = { ranked: ranked, gap: ranked[0].total - ranked[1].total, top2: ranked.slice(0, 2) };
      cha.top = CHA_AREA_INFO[ranked[0].letter];
    }
    if(tiene('holland')){
      var hr = computeHolland(holland_rows);
      holland = { codigo: hr.codigo, rows: hr.rows.map(function(d){ return Object.assign({}, d, { band: hollandBand(d.score) }); }) };
      holland.top = holland.rows[0];
    }
    if(tiene('af5')){
      var sexoAf5 = sexoNorma(cliente.sexo);
      var dims = computeAF5(cliente.grupo_normativo || grupoPorEdad(cliente.edad), sexoAf5);
      var sorted = Object.values(dims).sort(function(a, b){ return (b.centil == null ? 0 : b.centil) - (a.centil == null ? 0 : a.centil); })
        .map(function(d){ return Object.assign({}, d, { band: af5Band(d.centil) }); });
      af5 = { dims: dims, sorted: sorted,
        bajas: sorted.filter(function(d){ return d.band === 'low'; }),
        altas: sorted.filter(function(d){ return d.band === 'high'; }) };
      af5.academicoBand = af5Band(dims.academico.centil);
      af5.familiarBand = af5Band(dims.familiar.centil);
      af5.sinBaremo = sorted.every(function(d){ return d.centil == null; });
    }
    if(tiene('chte')){
      var areas = computeCHTE();
      var cs = Object.values(areas).sort(function(a, b){ return b.pct - a.pct; });
      cht = { areas: areas, sorted: cs,
        bajas: cs.filter(function(d){ return d.band === 'low'; }),
        altas: cs.filter(function(d){ return d.band === 'high'; }) };
    }
    if(tiene('apt_b')){
      var rb = computeAPTB(apt_b_rows);
      var bb = [rb.O, rb.L, rb.RE, rb.VP].sort(function(a, b){ return b.pct - a.pct; })
        .map(function(d){ return Object.assign({}, d, { band: aptBand(d.pct) }); });
      aptB = { r: rb, banded: bb,
        bajas: bb.filter(function(d){ return d.band === 'low'; }),
        altas: bb.filter(function(d){ return d.band === 'high'; }) };
    }
    if(tiene('apt_a')){
      var ra = computeAPTA(apt_a_rows);
      var ab = [ra.V, ra.N, ra.AB, ra.ME].sort(function(a, b){ return b.pct - a.pct; })
        .map(function(d){ return Object.assign({}, d, { band: aptBand(d.pct) }); });
      aptA = { r: ra, banded: ab,
        bajas: ab.filter(function(d){ return d.band === 'low'; }),
        altas: ab.filter(function(d){ return d.band === 'high'; }) };
    }

    // ---------------- numeración ----------------
    var secN = 0, modN = 0;
    function sec(){ secN++; return String(secN).padStart(2, '0'); }
    function mod(){ modN++; return modN; }
    function h2(titulo){ return '<h2 class="section-title"><span class="st-num">' + sec() + '</span> ' + titulo + '</h2>'; }
    function divisor(t){ return '<div class="module-divider"><span>' + t + '</span></div>'; }
    function dimRow(name, band, right, width){
      return '<div class="dim-row ' + (band || '') + '">' +
        '<div class="dim-top"><span class="dim-name">' + name + (band ? '<span class="dim-tag">' + BAND_LABEL[band] + '</span>' : '') + '</span><span class="dim-pd">' + right + '</span></div>' +
        '<div class="dim-bar-track"><div class="dim-bar-fill" style="width:' + Math.max(0, Math.min(100, width)) + '%;"></div></div>' +
        '</div>';
    }

    // ---------------- encabezado (membrete) ----------------
    var conBanda = !!membrete.color_banda;
    var estiloBanda = conBanda
      ? ' style="--banda:' + esc(membrete.color_banda) + ';--banda-texto:' + esc(membrete.color_texto_banda || '#14213D') + ';"'
      : '';
    var head =
      '<div class="report-head' + (conBanda ? ' rh-banda' : '') + '"' + estiloBanda + '>' +
        '<div class="rh-top">' +
          '<div class="rh-id">' +
            (membrete.escudo_url ? '<img class="rh-escudo" src="' + esc(membrete.escudo_url) + '" alt="Escudo de ' + marca + '" crossorigin="anonymous">' : '') +
            '<div><div class="rh-brand">' + marca + '</div>' +
            (membrete.subtitulo ? '<div class="rh-brand-sub">' + txt(membrete.subtitulo) + '</div>' : '') + '</div>' +
          '</div>' +
          '<div class="rh-meta"><div class="rh-meta-lbl">Fecha de la evaluación</div><div class="rh-meta-val">' + fecha + '</div></div>' +
        '</div>' +
        '<div class="rh-sub">Informe Integrado de Orientación Vocacional-Profesional</div>' +
        '<div class="rh-rule"></div>' +
      '</div>';

    var applicant =
      '<div class="applicant-box">' +
        '<div class="a-item"><div class="a-lbl">Postulante</div><div class="a-val">' + nombre + '</div></div>' +
        '<div class="a-item"><div class="a-lbl">Edad</div><div class="a-val">' + edad + '</div></div>' +
        '<div class="a-item"><div class="a-lbl">Fecha de nacimiento</div><div class="a-val">' + fechaNac + '</div></div>' +
        '<div class="a-item"><div class="a-lbl">Institución</div><div class="a-val">' + institucion + '</div></div>' +
        '<div class="a-item"><div class="a-lbl">Curso</div><div class="a-val">' + curso + '</div></div>' +
      '</div>' +
      '<p class="section-note" style="margin-top:-24px;margin-bottom:32px;">Profesional a cargo: <b>' + firmaNombre + '</b>' + (firmaRegistro ? ', ' + firmaRegistro : '') + '.</p>';

    // ---------------- motivo / observación / metodología ----------------
    var html = head + applicant;

    html += h2('Motivo de la consulta') +
      '<div class="brief-row" style="grid-template-columns:1fr;"><div class="brief-col">' +
      '<p>' + (motivo || 'Proceso de orientación vocacional-profesional para apoyar la decisión de carrera de ' + nombre + ', a partir de los instrumentos que eligió completar.') + '</p>' +
      (expectativas ? '<p style="margin-top:12px;"><b>Expectativas de la persona y su familia:</b> ' + expectativas + '</p>' : '') +
      (dudas ? '<p style="margin-top:12px;"><b>Dudas o conflictos iniciales:</b> ' + dudas + '</p>' : '') +
      '</div></div>';

    if(cliente.observacion_conducta){
      html += h2('Observación de conducta durante la evaluación') +
        '<p class="section-note">' + esc(cliente.observacion_conducta) + '</p>';
    }

    var fichas = {
      chaside: ['CHASIDE: Evaluación de Orientación Vocacional', 'identificar hacia qué áreas de formación profesional se orienta con mayor fuerza el perfil.', 'intereses y aptitudes autopercibidas en siete áreas ocupacionales (Administrativas, Humanidades, Artísticas, Salud, Ingeniería, Defensa y Ciencias Exactas), mediante 98 preguntas Sí/No.'],
      holland: ['Holland: Intereses Vocacionales (RIASEC)', 'identificar qué tipos de actividades resultan más atractivas, como ángulo de intereses complementario.', 'preferencia por actividades de tipo Realista, Investigador, Artístico, Social, Emprendedor y Convencional, mediante 60 preguntas Sí/No, con un instrumento propio de AURZANE.'],
      af5: ['AF5: Autoconcepto Forma 5', 'conocer cómo se percibe a sí mismo/a en distintas áreas de su vida.', 'autoconcepto académico/laboral, social, emocional, familiar y físico, mediante 30 frases de respuesta graduada (1-99), contrastadas con baremos por edad y sexo.'],
      chte: ['Cuestionario AURZANE de Hábitos de Estudio', 'identificar con qué herramientas prácticas cuenta hoy para sostener el estudio.', 'actitud, lugar de estudio, estado físico, plan de trabajo, técnicas de estudio, exámenes y trabajos académicos, mediante 56 preguntas Sí/No.'],
      apt_b: ['APT-B: Ortografía, Lenguaje, Relaciones Espaciales y Velocidad', 'medir aptitudes de desempeño real (no autopercibidas) con un instrumento propio de AURZANE.', 'Ortografía, Lenguaje, Relaciones Espaciales y Velocidad y Precisión perceptiva, mediante 410 ítems cronometrados, corregidos por adivinación y expresados en una escala propia (Bajo/Medio/Alto).'],
      apt_a: ['APT-A: Batería de Aptitudes', 'medir aptitudes de desempeño real con un instrumento propio de AURZANE.', 'Razonamiento Verbal, Numérico, Abstracto y Comprensión Mecánica, mediante 160 ítems cronometrados, corregidos por adivinación y expresados en una escala propia (Bajo/Medio/Alto).']
    };
    var noIncluidos = ORDEN.filter(function(k){ return !tiene(k); });

    html += h2('Metodología y herramientas') +
      '<p class="section-note">' + (entrevista && ENTREVISTA_LABEL[entrevista] ? 'Entrevista realizada ' + ENTREVISTA_LABEL[entrevista] + '. ' : '') +
      'Evaluación aplicada en línea a través de <b>AURZANE OVP</b>' + (membrete.nombre_marca && membrete.nombre_marca !== 'AURZANE' ? ' para <b>' + marca + '</b>' : '') +
      '. ' + (incluidos.length === 6 ? 'Se completó la batería completa de seis instrumentos.' : 'La persona eligió y completó ' + incluidos.length + ' de los 6 instrumentos disponibles; este informe se basa solo en ellos.') +
      ' No se aplicaron técnicas proyectivas.</p>' +
      '<div class="data-status">' +
        incluidos.map(function(k){ return '<span class="complete">' + NOMBRE_TEST[k] + ': incluido</span>'; }).join('') +
        noIncluidos.map(function(k){ return '<span>' + NOMBRE_TEST[k] + ': no aplicado</span>'; }).join('') +
      '</div>' +
      '<div class="interpretive-disclaimer"><strong>Alcance de la interpretación.</strong> Este informe es un apoyo para la orientación vocacional. Los resultados describen patrones de respuesta y desempeño en los instrumentos aplicados; no establecen por sí solos una carrera ideal, un diagnóstico clínico ni una predicción del futuro académico o laboral. ' +
      (incluidos.length < 6 ? 'Al no incluir toda la batería, algunas conclusiones son más acotadas que en un proceso completo. ' : '') +
      'La interpretación debe contextualizarse con la historia personal, el contexto educativo y las condiciones reales de cada opción formativa.</div>' +
      '<div class="como-leer"><b>Cómo leer los resultados.</b> Cada dimensión aparece con una barra y un nivel: <span class="nivel high">Alto</span> indica una fortaleza o preferencia marcada, <span class="nivel medium">Medio</span> un nivel dentro de lo esperable y <span class="nivel low">Bajo</span> un aspecto a reforzar o una preferencia menor. Los niveles comparan a la persona consigo misma o con la escala de cada instrumento, no con sus compañeros.</div>' +
      '<div class="career-grid fichas-grid">' + incluidos.map(function(k){
        var f = fichas[k];
        return '<div class="career-card"><h4>' + f[0] + '</h4>' +
          '<p class="career-list"><b>Objetivo:</b> ' + f[1] + '</p>' +
          '<p class="career-list"><b>Qué mide:</b> ' + f[2] + '</p></div>';
      }).join('') + '</div>';

    // ---------------- resumen ejecutivo ----------------
    var cards = [], filas = [];
    if(cha){
      cards.push(['Área vocacional prioritaria (CHASIDE)', cha.top.name]);
      filas.push(['CHASIDE', cha.top.name, cha.ranked[0].total + '/14', cha.gap <= 2 ? 'Perfil compartido con una segunda área muy cercana' : 'Preferencia clara y consolidada']);
    }
    if(holland){
      cards.push(['Código Holland (RIASEC)', holland.codigo + ' · ' + HOLLAND_INFO[holland.top.key].name]);
      var conv = cha ? hayConvergencia() : null;
      filas.push(['Holland (RIASEC)', HOLLAND_INFO[holland.top.key].name, holland.codigo,
        conv === null ? 'Tipo de interés más marcado' : (conv ? 'Converge con el área CHASIDE prioritaria' : 'Aporta un ángulo adicional al perfil vocacional')]);
    }
    if(af5){
      var af5Top = af5.sinBaremo ? af5.sorted.slice().sort(function(a, b){ return b.pd - a.pd; })[0] : af5.sorted[0];
      cards.push(['Autoconcepto: dimensión más alta', af5Top.name + (af5.sinBaremo ? ' (PD ' + af5Top.pd.toFixed(2) + ')' : ' (Centil ' + cen(af5Top.centil) + ')')]);
      filas.push(['AF5', af5.bajas.length ? af5.bajas.map(function(d){ return d.name; }).join(', ') : af5Top.name,
        af5.bajas.length ? 'Centil ' + af5.bajas.map(function(d){ return cen(d.centil); }).join('/') : (af5.sinBaremo ? 'PD ' + af5Top.pd.toFixed(2) : 'Centil ' + cen(af5Top.centil)),
        af5.bajas.length ? 'Área de autoconcepto a reforzar' : 'Fortaleza de autoconcepto a capitalizar']);
    }
    if(cht){
      cards.push(['Hábitos de estudio', cht.bajas.length ? cht.bajas.length + ' área' + (cht.bajas.length > 1 ? 's' : '') + ' por reforzar' : 'Perfil consolidado']);
      filas.push(['Hábitos de Estudio', cht.bajas.length ? cht.bajas.map(function(d){ return d.name; }).join(', ') : cht.sorted[0].name,
        cht.bajas.length ? cht.bajas.map(function(d){ return d.pct + '%'; }).join('/') : cht.sorted[0].pct + '%',
        cht.bajas.length ? 'Área práctica a fortalecer' : 'Hábitos ya consolidados']);
    }
    if(aptB){
      cards.push(['APT-B: mejor desempeño relativo', aptB.banded[0].name + ' (' + aptB.banded[0].pct + '%)']);
      filas.push(['APT-B', aptB.banded[0].name, aptB.banded[0].pct + '%', aptB.bajas.length ? 'Con ' + aptB.bajas.length + ' área' + (aptB.bajas.length > 1 ? 's' : '') + ' a reforzar' : 'Perfil de aptitudes consolidado']);
    }
    if(aptA){
      cards.push(['APT-A: mejor desempeño relativo', aptA.banded[0].name + ' (' + aptA.banded[0].pct + '%)']);
      filas.push(['APT-A', aptA.banded[0].name, aptA.banded[0].pct + '%', aptA.bajas.length ? 'Con ' + aptA.bajas.length + ' área' + (aptA.bajas.length > 1 ? 's' : '') + ' a reforzar' : 'Perfil de aptitudes consolidado']);
    }

    function hayConvergencia(){
      if(!cha || !holland) return null;
      var MAP = { C:['E','C'], H:['S','A'], A:['A'], S:['S','I'], I:['I','R'], D:['R','E'], E:['I','C'] };
      var af = MAP[cha.ranked[0].letter] || [];
      var top2 = holland.rows.slice(0, 2).map(function(d){ return d.key; });
      return af.some(function(k){ return top2.indexOf(k) !== -1; });
    }

    html += divisor('Resultados de la evaluación') + h2('Resumen ejecutivo') +
      '<div class="exec-summary" style="grid-template-columns:repeat(' + Math.min(cards.length, 3) + ',1fr);">' + cards.map(function(c){
        return '<div class="exec-card"><div class="ec-lbl">' + c[0] + '</div><div class="ec-val">' + c[1] + '</div></div>';
      }).join('') + '</div>' +
      '<table class="summary-table"><thead><tr><th>Instrumento</th><th>Hallazgo principal</th><th>Resultado</th><th>Lectura breve</th></tr></thead><tbody>' +
      filas.map(function(f){ return '<tr><td>' + f[0] + '</td><td>' + f[1] + '</td><td class="mono">' + f[2] + '</td><td>' + f[3] + '</td></tr>'; }).join('') +
      '</tbody></table>';

    // ---------------- módulos ----------------
    if(cha){
      var chaMax = Math.max.apply(null, cha.ranked.map(function(r){ return r.total; }).concat([1]));
      var chart = buildBarChartSVG(cha.ranked.map(function(r, i){
        return { label: CHA_AREA_INFO[r.letter].name, value: r.total / 14 * 100, valueLabel: r.total + '/14', band: i < 2 ? 'high' : undefined };
      }));
      html += divisor('Módulo ' + mod() + ': Orientación Vocacional (CHASIDE)') + h2('Perfil consolidado por área') +
        '<div class="chart-box">' + chart + '</div>' +
        '<div class="dim-list">' + cha.ranked.map(function(r, i){
          return '<div class="dim-row ' + (i < 2 ? 'high' : '') + '"><div class="dim-top"><span class="dim-name">' + CHA_AREA_INFO[r.letter].name +
            (i < 2 ? '<span class="dim-tag">Top</span>' : '') + '</span><span class="dim-pd">' + r.total + ' / 14 · Interés ' + r.interes + ' + Aptitud ' + r.aptitud +
            '</span></div><div class="dim-bar-track"><div class="dim-bar-fill" style="width:' + (r.total / chaMax * 100) + '%;"></div></div></div>';
        }).join('') + '</div>' +
        '<h3 class="sub-title">Áreas de mayor afinidad</h3>' +
        cha.top2.map(function(r){
          var info = CHA_AREA_INFO[r.letter];
          return '<div class="finding-block high"><div class="fb-head"><h4>' + info.name + '</h4><span class="fb-total">' + r.total + ' / 14 pts</span></div>' +
            '<div class="fb-body"><p><b>Intereses asociados:</b> ' + info.interesTraits.join(', ') + '.</p>' +
            '<p><b>Aptitudes asociadas:</b> ' + info.aptitudTraits.join(', ') + '.</p>' +
            '<p>' + info.workStyle + '</p></div></div>';
        }).join('');
    }

    if(holland){
      var top3 = holland.rows.slice(0, 3);
      var hi = '<p>El código Holland resultante es <b>' + holland.codigo + '</b>: ' + top3.map(function(d){ return HOLLAND_INFO[d.key].name; }).join(' – ') +
        '. Las actividades que más atraen a ' + primerNombre + ' combinan rasgos de estos tres tipos, con <b>' + HOLLAND_INFO[top3[0].key].name + '</b> como el más marcado (' + top3[0].score + '/10).</p>' +
        '<p>' + HOLLAND_INFO[top3[0].key].desc + ' En términos vocacionales, este tipo ' + HOLLAND_INFO[top3[0].key].fieldsNote + '</p>';
      if(top3[0].score - top3[1].score <= 1){
        hi += '<p>Los dos primeros tipos (<b>' + HOLLAND_INFO[top3[0].key].name + '</b> y <b>' + HOLLAND_INFO[top3[1].key].name + '</b>) aparecen prácticamente empatados: un perfil de intereses combinado más que una única inclinación dominante.</p>';
      }
      var hb = holland.rows.filter(function(d){ return d.band === 'low'; });
      if(hb.length){
        hi += '<p>Las actividades de tipo <b>' + hb.map(function(d){ return HOLLAND_INFO[d.key].name; }).join('</b> y <b>') + '</b> son las que menos atraen a ' + primerNombre + '. No es una limitación, sino una preferencia útil para descartar opciones.</p>';
      }
      html += divisor('Módulo ' + mod() + ': Intereses Vocacionales (Holland/RIASEC)') + h2('Perfil de intereses RIASEC') +
        '<p class="section-note">Instrumento propio de AURZANE inspirado en la teoría pública de John Holland. Es una medida ipsativa (compara preferencias dentro de la misma persona), por lo que no reporta percentiles poblacionales.</p>' +
        '<div class="chart-box">' + buildBarChartSVG(holland.rows.map(function(d){ return { label: d.name, value: d.pct, valueLabel: d.score + '/10', band: d.band }; })) + '</div>' +
        '<div class="dim-list">' + holland.rows.map(function(d){ return dimRow(d.name, d.band, d.score + ' / 10 · ' + d.pct + '%', d.pct); }).join('') + '</div>' + hi;
    }

    if(af5){
      var af5Max = 9.90;
      var af5Interp = af5.sorted.map(function(d){
        var info = (typeof AF5_DIM_INFO !== 'undefined') ? AF5_DIM_INFO[d.key] : null;
        if(!info) return '';
        if(af5.sinBaremo) return '<div class="interp-item"><h4>' + d.name + '</h4><p class="interp-def">' + info.def + '</p></div>';
        return '<div class="interp-item"><h4>' + d.name + ' <span class="reco-band ' + d.band + '">' + BAND_LABEL[d.band] + '</span></h4>' +
          '<p class="interp-def">' + info.def + '</p><p>' + info[d.band] + '</p></div>';
      }).join('');
      html += divisor('Módulo ' + mod() + ': Autoconcepto (AF5)') + h2('Perfil por dimensión') +
        (af5.sinBaremo ? '<p class="section-note">Para convertir las puntuaciones en centiles hace falta conocer el sexo y la edad de la persona evaluada (se completan en «Mi Cuenta»). Mientras tanto se muestran las puntuaciones directas (PD, escala de 0 a 9,9).</p>' : '') +
        '<div class="chart-box">' + buildRadarChartSVG(af5.sorted.map(function(d){ return { name: d.name, value: af5.sinBaremo ? Math.round(d.pd / af5Max * 100) : d.centil, band: af5.sinBaremo ? undefined : d.band }; })) + '</div>' +
        '<div class="dim-list">' + af5.sorted.map(function(d){ return dimRow(d.name, af5.sinBaremo ? '' : d.band, 'PD ' + d.pd.toFixed(2) + ' · Centil ' + cen(d.centil), d.pd / af5Max * 100); }).join('') + '</div>' +
        (af5Interp ? '<h3 class="sub-title">Qué significa cada dimensión</h3><div class="interp-list">' + af5Interp + '</div>' : '');
    }

    if(cht){
      var chtInterp = cht.sorted.map(function(d){
        var def = (typeof CHT_AREA_DEF !== 'undefined') ? CHT_AREA_DEF[d.key] : '';
        var it = (typeof CHT_AREA_INTERP !== 'undefined' && CHT_AREA_INTERP[d.key]) ? CHT_AREA_INTERP[d.key][d.band] : '';
        if(!def && !it) return '';
        return '<div class="interp-item"><h4>' + d.name + ' <span class="reco-band ' + d.band + '">' + BAND_LABEL[d.band] + '</span></h4>' +
          (def ? '<p class="interp-def">' + def + '</p>' : '') + (it ? '<p>' + primerNombre + ' ' + it + '</p>' : '') + '</div>';
      }).join('');
      var chtReco = cht.sorted.filter(function(d){ return d.band !== 'high'; }).map(function(d){
        var items = CHT_REC_LIBRARY[d.key][d.band];
        return '<div class="reco-area"><div class="reco-area-head"><h4>' + d.name + '</h4><span class="reco-band ' + d.band + '">' + BAND_LABEL[d.band] + '</span></div>' +
          '<ul class="reco-list">' + items.slice(0, 4).map(function(t){ return '<li><span class="reco-mark">›</span><span>' + t + '</span></li>'; }).join('') + '</ul></div>';
      }).join('');
      html += divisor('Módulo ' + mod() + ': Hábitos de Estudio') + h2('Perfil por área') +
        '<div class="chart-box">' + buildBarChartSVG(cht.sorted.map(function(d){ return { label: d.name, value: d.pct, valueLabel: d.pct + '%', band: d.band }; }), { suffix: '%' }) + '</div>' +
        '<div class="dim-list">' + cht.sorted.map(function(d){ return dimRow(d.name, d.band, d.si + '/' + d.total + ' · ' + d.pct + '%', d.pct); }).join('') + '</div>' +
        (chtInterp ? '<h3 class="sub-title">Lectura por área</h3><div class="interp-list">' + chtInterp + '</div>' : '') +
        (chtReco ? '<h3 class="sub-title">Recomendaciones prioritarias</h3>' + chtReco : '');
    }

    var NOTA_APT = '<p class="section-note">Instrumento propio de AURZANE. El puntaje se corrige por adivinación y se expresa en una escala interpretativa de tres niveles (Bajo/Medio/Alto). No corresponde a un percentil poblacional externo, ya que el instrumento todavía no cuenta con un estudio de tipificación con muestra de referencia.</p>';

    if(aptB){
      var APTB_MAX = { O:100, L:50, RE:60, VP:200 };
      var r = aptB.r, top = aptB.banded[0], bot = aptB.banded[aptB.banded.length - 1];
      var bi = '<p>En la batería APT-B, ' + primerNombre + ' muestra su mejor desempeño relativo en <b>' + top.name + '</b> (nivel ' + top.pct + '%)' +
        (bot.pct < top.pct ? ', frente a un desempeño más bajo en <b>' + bot.name + '</b> (nivel ' + bot.pct + '%)' : ', con un perfil parejo entre las cuatro áreas') + '.</p>';
      if(r.O.pct >= 70 && r.L.pct >= 70) bi += '<p>Ortografía y Lenguaje consolidados indican una base sólida de manejo del idioma escrito, relevante en carreras con alta carga de lectura, redacción o comunicación formal.</p>';
      else if(r.O.pct < 40 && r.L.pct < 40) bi += '<p>Ortografía y Lenguaje aparecen como un área a reforzar. No limita por sí solo ninguna elección, pero conviene trabajarlo si la carrera exige producción escrita frecuente.</p>';
      if(r.RE.pct >= 70) bi += '<p>Relaciones Espaciales es un punto fuerte, útil en carreras que exigen visualizar objetos, estructuras o planos en tres dimensiones (diseño, arquitectura, ingeniería).</p>';
      else if(r.RE.pct < 40) bi += '<p>Relaciones Espaciales aparece más baja. Conviene tenerlo presente si la carrera depende de la visualización tridimensional, sin que esto la descarte.</p>';
      if(r.VP.pct >= 70) bi += '<p>Velocidad y Precisión perceptiva alta sugiere agilidad y exactitud para tareas de revisión de detalle o control bajo presión de tiempo.</p>';
      else if(r.VP.pct < 40) bi += '<p>Velocidad y Precisión perceptiva aparece como un área a reforzar si la carrera exige revisión de detalle bajo presión de tiempo.</p>';
      html += divisor('Módulo ' + mod() + ': Ortografía, Lenguaje, Relaciones Espaciales y Velocidad (APT-B)') + h2('Perfil de aptitudes APT-B') + NOTA_APT +
        '<div class="chart-box">' + buildBarChartSVG(aptB.banded.map(function(d){ return { label: d.name, value: d.pct, valueLabel: d.pct + '%', band: d.band }; })) + '</div>' +
        '<div class="dim-list">' + aptB.banded.map(function(d){
          return dimRow(d.name, d.band, 'Puntaje corregido: ' + d.corregido + ' / ' + APTB_MAX[d.key] + ' (' + d.aciertos + ' aciertos − ' + d.errores + ' errores) · Nivel ' + d.pct + '%', d.pct);
        }).join('') + '</div>' + bi;
    }

    if(aptA){
      var ra2 = aptA.r, topA = aptA.banded[0], botA = aptA.banded[aptA.banded.length - 1];
      var ai = '<p>En la batería APT-A, ' + primerNombre + ' muestra su mejor desempeño relativo en <b>' + topA.name + '</b> (nivel ' + topA.pct + '%)' +
        (botA.pct < topA.pct ? ', frente a un desempeño más bajo en <b>' + botA.name + '</b> (nivel ' + botA.pct + '%)' : ', con un perfil parejo entre las cuatro áreas') + '.</p>';
      var TXT = {
        V: ['Razonamiento Verbal alto sugiere buen manejo de relaciones de significado entre conceptos, valioso en carreras con lectura, argumentación o comunicación.', 'Razonamiento Verbal aparece como un área a reforzar si la carrera exige comprensión lectora o argumentación frecuente.'],
        N: ['Razonamiento Numérico alto indica facilidad para el cálculo y el razonamiento cuantitativo, relevante en carreras con carga matemática, económica o técnica.', 'Razonamiento Numérico aparece más bajo. Conviene tenerlo presente si la formación elegida tiene alta carga de cálculo.'],
        AB: ['Razonamiento Abstracto alto sugiere buena capacidad para identificar patrones y reglas no verbales, útil en programación, diseño, ingeniería y disciplinas analíticas.', 'Razonamiento Abstracto aparece como un área a reforzar dentro del perfil.'],
        ME: ['Comprensión Mecánica alta indica buen entendimiento intuitivo de principios físicos aplicados, relevante en ingenierías y oficios técnicos.', 'Comprensión Mecánica aparece más baja, sin que esto descarte por sí solo ninguna elección.']
      };
      ['V','N','AB','ME'].forEach(function(k){
        if(ra2[k].pct >= 70) ai += '<p>' + TXT[k][0] + '</p>';
        else if(ra2[k].pct < 40) ai += '<p>' + TXT[k][1] + '</p>';
      });
      html += divisor('Módulo ' + mod() + ': Batería de Aptitudes APT-A') + h2('Perfil de aptitudes APT-A') + NOTA_APT +
        '<div class="chart-box">' + buildBarChartSVG(aptA.banded.map(function(d){ return { label: d.name, value: d.pct, valueLabel: d.pct + '%', band: d.band }; })) + '</div>' +
        '<div class="dim-list">' + aptA.banded.map(function(d){
          return dimRow(d.name, d.band, 'Puntaje corregido: ' + d.corregido + ' / 40 (' + d.aciertos + ' aciertos − ' + d.errores + ' errores) · Nivel ' + d.pct + '%', d.pct);
        }).join('') + '</div>' + ai;
    }

    // ---------------- síntesis integradora ----------------
    html += divisor('Síntesis integradora');

    // Fortalezas y aspectos a trabajar, reunidos de todos los instrumentos.
    var fortalezas = [], trabajar = [];
    if(cha) fortalezas.push('Interés y aptitud hacia <b>' + cha.top.name + '</b> (CHASIDE, ' + cha.ranked[0].total + '/14).');
    if(holland) fortalezas.push('Intereses de tipo <b>' + HOLLAND_INFO[holland.top.key].name + '</b> (Holland, código ' + holland.codigo + ').');
    if(af5){
      af5.altas.forEach(function(d){ fortalezas.push('Autoconcepto ' + d.name.toLowerCase() + ' alto (AF5, centil ' + d.centil + ').'); });
      af5.bajas.forEach(function(d){ trabajar.push('Autoconcepto ' + d.name.toLowerCase() + ' bajo (AF5, centil ' + d.centil + ').'); });
    }
    if(cht){
      cht.altas.forEach(function(d){ fortalezas.push(d.name + ' (Hábitos de Estudio, ' + d.pct + '%).'); });
      cht.bajas.forEach(function(d){ trabajar.push(d.name + ' (Hábitos de Estudio, ' + d.pct + '%).'); });
    }
    [[aptB, 'APT-B'], [aptA, 'APT-A']].forEach(function(p){
      if(!p[0]) return;
      p[0].altas.forEach(function(d){ fortalezas.push(d.name + ' (' + p[1] + ', nivel ' + d.pct + '%).'); });
      p[0].bajas.forEach(function(d){ trabajar.push(d.name + ' (' + p[1] + ', nivel ' + d.pct + '%).'); });
    });
    if(!trabajar.length) trabajar.push('No aparecen áreas en nivel bajo en los instrumentos aplicados.');
    if(!fortalezas.length) fortalezas.push('El perfil se ubica principalmente en niveles medios, una base estable sobre la cual construir.');

    html += h2('Fortalezas y aspectos a trabajar') +
      '<div class="balance-grid">' +
        '<div class="balance-col fuerte"><h4>Fortalezas</h4><ul>' + fortalezas.map(function(t){ return '<li>' + t + '</li>'; }).join('') + '</ul></div>' +
        '<div class="balance-col reforzar"><h4>Aspectos a trabajar</h4><ul>' + trabajar.map(function(t){ return '<li>' + t + '</li>'; }).join('') + '</ul></div>' +
      '</div>';

    // Áreas y carreras
    var MAP_CH = { C:['E','C'], H:['S','A'], A:['A'], S:['S','I'], I:['I','R'], D:['R','E'], E:['I','C'] };
    function notasPreparacion(){
      var n = [];
      if(af5 && af5.academicoBand === 'low') n.push('reforzar la confianza académica antes de comenzar');
      if(cht && cht.areas.tecnicas.band === 'low') n.push('desarrollar técnicas de estudio activo');
      if(cht && cht.areas.plan.band === 'low') n.push('construir un sistema de planificación del tiempo');
      if(n.length) return 'Antes de comenzar, se recomienda especialmente: ' + n.join('; ') + '.';
      if(af5 || cht) return primerNombre + ' cuenta con una base de autoconcepto y hábitos favorable para sostener esta carrera desde el inicio.';
      return '';
    }
    var carrerasHtml = '';
    if(cha){
      carrerasHtml = cha.top2.map(function(r, idx){
        var info = CHA_AREA_INFO[r.letter];
        var hl = '';
        if(holland){
          var resp = holland.rows.slice(0, 2).filter(function(d){ return (MAP_CH[r.letter] || []).indexOf(d.key) !== -1; })[0];
          hl = '<div class="career-list"><b>Respaldo cruzado:</b> ' + (resp
            ? 'El código Holland (<b>' + holland.codigo + '</b>) respalda esta afinidad: el tipo <b>' + HOLLAND_INFO[resp.key].name + '</b> encaja con este perfil de carreras.'
            : 'El código Holland (<b>' + holland.codigo + '</b>) no marca esta área como su tipo más fuerte, pero no la descarta. Vale la pena considerar ambos resultados juntos.') + '</div>';
        }
        var nota = notasPreparacion();
        return '<div class="career-card"><h4>' + (idx === 1 ? 'Alternativa: ' : 'Prioridad: ') + info.name +
          ' <span class="mono" style="font-size:0.72rem;color:#8A6A28;font-weight:400;">(' + r.total + '/14 en CHASIDE)</span></h4>' +
          '<div class="career-list"><b>Por qué se ajusta al perfil:</b> ' + info.workStyle + '</div>' + hl +
          '<div class="career-list"><b>Carreras específicas a explorar:</b> ' + info.careers.join(', ') + '.</div>' +
          '<div class="career-list"><b>A qué te puede llevar a futuro:</b> ' + (info.futureRoles || '') + '</div>' +
          (nota ? '<div class="career-note">' + nota + '</div>' : '') + '</div>';
      }).join('');
    } else if(holland){
      carrerasHtml = holland.rows.slice(0, 2).map(function(d, idx){
        var info = HOLLAND_INFO[d.key];
        var nota = notasPreparacion();
        return '<div class="career-card"><h4>' + (idx === 1 ? 'Alternativa: ' : 'Prioridad: ') + 'perfil ' + info.name +
          ' <span class="mono" style="font-size:0.72rem;color:#8A6A28;font-weight:400;">(' + d.score + '/10 en Holland)</span></h4>' +
          '<div class="career-list"><b>Por qué se ajusta al perfil:</b> ' + info.desc + '</div>' +
          '<div class="career-list"><b>Entornos de trabajo afines:</b> ' + info.fieldsNote.charAt(0).toUpperCase() + info.fieldsNote.slice(1) + '</div>' +
          '<div class="career-list"><b>Carreras a explorar (ejemplos):</b> ' + HOLLAND_CARRERAS[d.key].join(', ') + '.</div>' +
          (nota ? '<div class="career-note">' + nota + '</div>' : '') + '</div>';
      }).join('');
    }
    if(carrerasHtml){
      html += h2('Áreas y carreras para explorar') +
        '<p class="section-note">Las áreas con mayor puntaje, consideradas junto con el resto de los instrumentos aplicados, sirven como punto de partida para explorar opciones. No constituyen una recomendación definitiva.</p>' +
        '<div class="career-grid">' + carrerasHtml + '</div>';
    } else {
      html += h2('Áreas y carreras para explorar') +
        '<p class="section-note">Este informe no incluye instrumentos de intereses vocacionales (CHASIDE u Holland), por lo que no propone áreas de carrera. Para obtener una orientación de carrera, conviene completar al menos uno de ellos; el resto de los resultados igualmente ayuda a conocer fortalezas y hábitos de base.</p>';
    }

    // Conclusión integrada
    var nombresInst = incluidos.map(function(k){ return '<b>' + NOMBRE_TEST[k] + '</b>'; });
    var conc = '<p>Este informe integra ' + (incluidos.length === 1 ? 'un instrumento: ' : incluidos.length + ' instrumentos complementarios: ') + lista(nombresInst) + '.</p>';
    if(cha){
      conc += '<p>El área vocacional con mayor puntuación relativa es <b>' + cha.top.name + '</b>' + (cha.gap <= 2
        ? ', con una diferencia pequeña frente a <b>' + CHA_AREA_INFO[cha.ranked[1].letter].name + '</b>. Conviene mantener abiertas ambas líneas de exploración.</p>'
        : '. Este resultado orienta la exploración, pero no debe interpretarse como una elección predeterminada.</p>');
    }
    if(cha && af5){
      if(af5.academicoBand === 'low' && cha.ranked[0].total >= 8){
        conc += '<p>Un cruce relevante: aunque el CHASIDE muestra un interés y aptitud consolidados hacia <b>' + cha.top.name + '</b>, el AF5 revela una autopercepción académica baja (centil ' + (af5.dims.academico.centil == null ? '—' : af5.dims.academico.centil) + '). Esto sugiere que la limitación no es de capacidad, sino de confianza, y conviene reforzarla antes de que opaque un interés genuino.</p>';
      } else if(af5.academicoBand === 'high' && cha.ranked[0].total >= 8){
        conc += '<p>Los instrumentos convergen: el interés del CHASIDE hacia <b>' + cha.top.name + '</b> se sostiene sobre una autopercepción académica sólida en el AF5 (centil ' + af5.dims.academico.centil + '), una combinación que da seguridad a la decisión.</p>';
      }
    }
    if(cha && holland){
      conc += hayConvergencia()
        ? '<p>El código Holland (<b>' + holland.codigo + '</b>) es coherente con la orientación hacia <b>' + cha.top.name + '</b>: dos instrumentos distintos apuntan en la misma dirección.</p>'
        : '<p>El código Holland (<b>' + holland.codigo + '</b>) aporta un ángulo adicional: su tipo dominante (<b>' + HOLLAND_INFO[holland.top.key].name + '</b>) no coincide de forma directa con el área líder del CHASIDE. No es contradictorio; vale la pena explorar si ambas preferencias pueden combinarse dentro de una misma carrera.</p>';
    } else if(holland && !cha){
      conc += '<p>El perfil de intereses se resume en el código <b>' + holland.codigo + '</b>, con predominio del tipo <b>' + HOLLAND_INFO[holland.top.key].name + '</b>, que orienta hacia entornos donde ' + primerNombre + ' puede sentirse más motivado/a.</p>';
    }
    if(cht){
      var tec = cht.areas.tecnicas, pla = cht.areas.plan;
      if(tec.band === 'low' || pla.band === 'low'){
        var cuales = [tec.band === 'low' ? 'las técnicas de estudio' : null, pla.band === 'low' ? 'la planificación del tiempo' : null].filter(Boolean);
        conc += '<p>En lo práctico, ' + lista(cuales) + ' ' + (cuales.length > 1 ? 'están' : 'está') + ' en un nivel bajo. Conviene fortalecer estos hábitos antes de iniciar la carrera para que el esfuerzo se sostenga durante el primer año.</p>';
      } else if(tec.band === 'high' && pla.band === 'high'){
        conc += '<p>El cuestionario de hábitos confirma que ' + primerNombre + ' ya cuenta con técnicas de estudio y planificación sólidas para sostener la exigencia universitaria.</p>';
      }
    }
    if(aptA || aptB){
      var mejores = [].concat(aptA ? [aptA.banded[0]] : [], aptB ? [aptB.banded[0]] : []).map(function(d){ return '<b>' + d.name + '</b>'; });
      conc += '<p>En las pruebas de desempeño, los mejores resultados relativos aparecen en ' + lista(mejores) + ', un dato objetivo para contrastar con los intereses al elegir carrera.</p>';
    }
    conc += '<p>En conjunto, los resultados no apuntan a una única respuesta cerrada, sino a un punto de partida estructurado: hacia dónde mirar primero, con qué fortalezas se cuenta y qué conviene fortalecer.</p>';
    html += h2('Conclusión integrada') + '<div class="conclusion-box">' + conc + '</div>';

    // Recomendaciones
    var recoE = [];
    if(cha){
      recoE.push('Investigar en detalle la malla curricular, duración y campo laboral real de las carreras señaladas en <b>' + cha.top.name + '</b> y ' + CHA_AREA_INFO[cha.ranked[1].letter].name + ', antes de tomar una decisión final.');
    } else if(holland){
      recoE.push('Investigar carreras vinculadas al perfil <b>' + HOLLAND_INFO[holland.top.key].name + '</b> (malla curricular, duración y campo laboral real) antes de decidir.');
    }
    if(holland && cha){
      recoE.push('Tener presente el código Holland (<b>' + holland.codigo + '</b>) al investigar carreras: complementa el enfoque por áreas del CHASIDE y ayuda a afinar la búsqueda.');
    }
    if(cha || holland){
      recoE.push('Conversar con profesionales en ejercicio de estas áreas para contrastar el perfil con la experiencia práctica del día a día.');
      recoE.push('Comparar varias universidades o institutos que ofrezcan estas carreras: cada institución puede tener requisitos de admisión propios (examen de ingreso, nota mínima, entrevista, cupos) y difieren en duración, modalidad y costo. Revisarlo en la página oficial de cada institución evita sorpresas al postular.');
    }
    if(cht){
      var prio = cht.sorted.filter(function(d){ return d.band !== 'high'; }).slice(0, 3);
      prio.forEach(function(d){ recoE.push('<b>' + d.name + ':</b> ' + CHT_REC_LIBRARY[d.key][d.band][0]); });
      if(!prio.length) recoE.push('Los hábitos de estudio están consolidados: el enfoque ahora es de refinamiento durante el primer año de carrera, cuando la exigencia aumenta.');
    }
    if(aptB && aptB.bajas.length) recoE.push('Practicar de forma regular las áreas de APT-B con nivel bajo (' + aptB.bajas.map(function(d){ return d.name; }).join(', ') + ') con ejercicios breves y frecuentes.');
    if(aptA && aptA.bajas.length) recoE.push('Reforzar ' + aptA.bajas.map(function(d){ return d.name.toLowerCase(); }).join(', ') + ' con ejercicios graduados, sobre todo si la carrera elegida depende de esas habilidades.');
    if(noIncluidos.length){
      recoE.push('Para una mirada más completa, se puede completar también: ' + noIncluidos.map(function(k){ return NOMBRE_TEST[k]; }).join(', ') + '. El informe se actualiza al terminarlas.');
    }

    var recoF = [
      'Acompañar el proceso de decisión sin imponer una carrera basada en expectativas propias. El rol más útil de la familia es sostener la exploración de ' + primerNombre + ', no decidir por adelantado.',
      'Reconocer explícitamente las fortalezas que arrojó esta evaluación. El refuerzo de lo que sí funciona acelera la confianza necesaria para decidir.',
      'Generar espacios de conversación regulares sobre el proceso vocacional, sin presión de "decidir ya". La indecisión en esta etapa es normal.'
    ];
    if(af5 && af5.familiarBand === 'low'){
      recoF.push('El AF5 sugiere que ' + primerNombre + ' percibe cierta distancia o crítica en el ámbito familiar. Es recomendable mostrar apoyo explícito e incondicional durante este proceso, independientemente de la carrera que se elija.');
    }
    if(cht && cht.bajas.some(function(d){ return ['lugar','fisico','plan'].indexOf(d.key) !== -1; })){
      recoF.push('Facilitar en casa un espacio y horario fijo de estudio, y respetar ese tiempo sin interrupciones, apoya directamente los hábitos que salieron más bajos.');
    }

    html += h2('Recomendaciones') +
      '<p class="section-note">Recomendaciones específicas organizadas por destinatario, para que cada una se traduzca en una acción concreta.</p>' +
      '<h3 class="sub-title">Para el estudiante</h3>' +
      '<ul class="reco-list reco-box">' + recoE.map(function(t, i){ return '<li><span class="reco-mark">' + romano(i) + '</span><span>' + t + '</span></li>'; }).join('') + '</ul>' +
      '<h3 class="sub-title">Para la familia</h3>' +
      '<ul class="reco-list reco-box">' + recoF.map(function(t, i){ return '<li><span class="reco-mark">' + romano(i) + '</span><span>' + t + '</span></li>'; }).join('') + '</ul>';

    // Bienestar
    var bien = '<p>Elegir una carrera es, además de una decisión académica, un momento que pone a prueba la seguridad personal. Es normal que aparezcan dudas, comparaciones o miedo a equivocarse. Cuidar el bienestar emocional durante este proceso es parte de la orientación vocacional.</p>';
    if(af5){
      if(af5.bajas.length){
        var SUG = {
          academico: 'reconocer logros académicos concretos y recientes, por pequeños que sean, en vez de centrarse en comparaciones.',
          social: 'proponer pequeños pasos de exposición social (un grupo de estudio, una actividad extracurricular) sin forzar un cambio drástico.',
          emocional: 'practicar una técnica breve de respiración o pausa consciente antes de evaluaciones o exposiciones, para reducir el nerviosismo anticipado.',
          familiar: 'abrir una conversación familiar honesta y de bajo riesgo sobre cómo se siente cada uno en la relación, antes que forzar el tema vocacional.',
          fisico: 'enfocar la actividad física en el disfrute y el bienestar, y evitar comentarios comparativos sobre el cuerpo en el entorno cercano.'
        };
        bien += '<p><b>Áreas a reforzar:</b> el AF5 señala ' + (af5.bajas.length > 1 ? 'niveles bajos' : 'un nivel bajo') + ' en ' + af5.bajas.map(function(d){ return d.name; }).join(', ') +
          '. No es un diagnóstico ni una etiqueta fija: es una fotografía de cómo se percibe ' + primerNombre + ' hoy, y las percepciones se pueden trabajar.</p>' +
          af5.bajas.map(function(d){ return '<p style="margin-left:6px;">→ <b>' + d.name + ':</b> ' + (SUG[d.key] || '') + '</p>'; }).join('');
      } else {
        bien += '<p>El perfil de autoconcepto de ' + primerNombre + ' no muestra áreas debilitadas, una base sólida para enfrentar la incertidumbre normal de esta etapa.</p>';
      }
      if(af5.altas.length){
        bien += '<p><b>Recurso a capitalizar:</b> <b>' + af5.altas.map(function(d){ return d.name; }).join(', ') + '</b> ya funciona' + (af5.altas.length > 1 ? 'n' : '') + ' como un ancla emocional real. Nombrarlo explícitamente ayuda a sostener la confianza mientras se trabaja el resto.</p>';
      }
    } else {
      bien += '<p>Es útil recordar que la indecisión vocacional es una etapa esperable y no una falla personal, y que buscar apoyo si la incertidumbre genera ansiedad significativa es una decisión válida en cualquier momento.</p>';
    }
    html += '<h3 class="sub-title">Bienestar emocional y autoestima</h3><div class="conclusion-box" style="margin-bottom:36px;">' + bien + '</div>';

    html += '<div class="methodology"><b>Sobre este informe.</b> Este documento integra ' + (incluidos.length === 1 ? 'una fuente de información' : incluidos.length + ' fuentes de información independientes') +
      ' para ofrecer una lectura del perfil vocacional de ' + primerNombre + '. Su mayor valor se obtiene al leerlo con calma y conversarlo en familia o con un profesional de orientación, para que cada hallazgo se contextualice con la historia y las circunstancias de cada caso.</div>' +
      '<div class="signature-block">' +
        (conFirma ? '<img class="sig-img" src="/img/firma.png" alt="Firma del psicólogo clínico" width="240" height="91">' : '<div class="sig-line">' + firmaLinea + '</div>' +
        '<div class="sig-name">' + firmaNombre + '</div>') +
        (firmaTitulo ? '<div class="sig-title">' + firmaTitulo + '</div>' : '') +
        (firmaRegistro ? '<div class="sig-reg">' + firmaRegistro + '</div>' : '') +
        (membrete.nota_legal ? '<div class="sig-reg" style="margin-top:4px;">' + txt(membrete.nota_legal) + '</div>' : '') +
      '</div>' +
      '<div class="report-footer"><span>' + marca + (membrete.subtitulo ? ' · ' + txt(membrete.subtitulo) : '') + '</span><span>Documento confidencial</span></div>';

    report.innerHTML = html;
    report.dataset.incluidos = incluidos.join(',');
    global.__ovpMembreteActual = membrete;
    global.__ovpProfesionalActual = profesional;
    global.__ovpClienteActual = { nombre: cliente.nombre || '', fecha: fecha };
  }

  global.ovpTestsDelInforme = testsDelInforme;
  global.ovpNombreTest = NOMBRE_TEST;
  global.ovpOrdenTests = ORDEN;
  global.generarInformeOVP = generar;
  // Reemplaza la versión de informe-shared.js (que exigía el plan completo).
  global.generateReportFromData = generar;
})(window);
