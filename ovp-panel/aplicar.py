# -*- coding: utf-8 -*-
"""Panel OVP v3: más claro y visual, con «Dónde estudiar» enlazado a NEXUS.
Uso: python3 ovp-panel/aplicar.py <portal.html original> <portal.html nuevo>
No cambia preguntas, puntuaciones, informes ni datos: solo la presentación del panel."""
import sys, re

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)


def rep_re(pat, b):
    global s
    s2, c = re.subn(pat, b, s, count=1, flags=re.S)
    assert c == 1, pat[:90]
    s = s2


# ---------- 1. Barra lateral: sin repetir la cabecera común ----------
rep_re(r'\n    <div class="sidebar-brand">.*?\n    </div>\n', '\n')
rep_re(r'      <div class="sidebar-eco-label">Ecosistema AURZANE</div>\n.*?(      <div class="sidebar-paleta">)', r'\1')
rep_re(r'\n      <nav class="aur-breadcrumb".*?</nav>\n', '\n')

NAV = '''    <div class="nav-items" id="navItems" role="navigation" aria-label="Secciones de tu proceso">
      <div class="nav-item active" data-page="resumen" role="link" tabindex="0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/></svg>
        <span class="nav-label">Inicio</span>
      </div>
      <div class="nav-item" data-page="tests" role="link" tabindex="0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
        <span class="nav-label">Evaluaciones</span>
        <span class="nav-badge" id="navTestsBadge" style="display:none;"></span>
      </div>
      <div class="nav-item" data-page="informe" role="link" tabindex="0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/></svg>
        <span class="nav-label">Mi informe</span>
      </div>
      <div class="nav-item" data-page="estudiar" role="link" tabindex="0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M22 10L12 5 2 10l10 5 10-5z"/><path d="M6 12v5c0 1.66 2.69 3 6 3s6-1.34 6-3v-5"/></svg>
        <span class="nav-label">Dónde estudiar</span>
      </div>
      <div class="nav-item" data-page="cuenta" role="link" tabindex="0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
        <span class="nav-label">Mi cuenta</span>
      </div>
    </div>
'''
rep_re(r'    <div class="nav-items" id="navItems">.*?\n    </div>\n(    <div class="sidebar-eco">)', NAV.replace('\\', '\\\\') + r'\1')

# ---------- 2. Inicio ----------
RESUMEN = '''      <div class="page active" id="page-resumen">
        <section class="ov-hero" aria-labelledby="ovHola">
          <div class="ov-hero-txt">
            <p class="ov-hola" id="ovHola">Hola, <span id="clienteNombre"></span></p>
            <div id="nextStepWrap"></div>
          </div>
          <div class="ov-anillo" id="ovAnillo" aria-live="polite"></div>
        </section>
        <section class="ov-sec" aria-labelledby="ovRutaT">
          <h3 class="ov-sec-t" id="ovRutaT">Tu recorrido</h3>
          <div class="step-flow" id="stepFlow"></div>
        </section>
        <section class="ov-sec" aria-labelledby="ovEvT">
          <div class="ov-sec-head"><h3 class="ov-sec-t" id="ovEvT">Tus evaluaciones</h3><button type="button" class="ov-link" onclick="goToPage('plan')">Añadir o quitar</button></div>
          <div class="ov-mosaico" id="evalsProgressList"></div>
        </section>
        <section class="ov-sec" aria-labelledby="ovEstT">
          <div class="ov-sec-head"><h3 class="ov-sec-t" id="ovEstT">Carreras que encajan contigo</h3><button type="button" class="ov-link" onclick="goToPage('estudiar')">Dónde estudiarlas</button></div>
          <div id="ovEstudiarResumen"></div>
        </section>
      </div>
'''
rep_re(r'      <div class="page active" id="page-resumen">.*?\n      </div>\n\n', RESUMEN + '\n')

# ---------- 3. Evaluaciones = lista + elegir (antes «Mi Proceso») ----------
m = re.search(r'\n        <div class="panel" id="panelElegir">.*?\n        </div>\n(?=        <div class="panel">\n          <div class="panel-head"><h3>¿Qué ocurre después\?)', s, re.S)
assert m
elegir = m.group(0).replace('<h3>Elegir o añadir evaluaciones</h3>', '<h3>Añadir o quitar evaluaciones</h3>')
rep_re(r'\n      <!-- MI PLAN -->\n      <div class="page" id="page-plan">.*?\n      </div>\n', '\n')
rep('<h2>Mis Evaluaciones</h2><p>Completa tus evaluaciones a tu ritmo. Con cada evaluación que terminas, tu informe en «Mi Informe» se actualiza.</p>',
    '<h2>Evaluaciones</h2><p>Hazlas a tu ritmo: lo que respondes se guarda solo. Con cada una que terminas, tu informe se actualiza.</p>')
rep('        <div class="tests-grid" id="testsGrid"></div>\n      </div>\n',
    '        <div class="tests-grid" id="testsGrid"></div>' + elegir + '      </div>\n')

# ---------- 4. Informe y nueva página «Dónde estudiar» ----------
rep('<h2>Mi Informe</h2><p>El resultado integrado de tu proceso de evaluación.</p>',
    '<h2>Mi informe</h2><p>Todas tus evaluaciones juntas en un solo informe, listo para leer y descargar.</p>')
ESTUDIAR = '''
      <!-- DÓNDE ESTUDIAR -->
      <div class="page" id="page-estudiar">
        <div class="page-head"><div><h2>Dónde estudiar</h2><p>Las carreras que salen en tu informe, dónde se estudian en España y con qué nota se entró el último curso.</p></div></div>
        <div class="ov-nota">
          <label for="ovNota">Tu nota de admisión <small>(sobre 14, si ya la sabes)</small></label>
          <span><input type="number" id="ovNota" min="5" max="14" step="0.01" inputmode="decimal" placeholder="Ej. 10,5"><a href="https://nexus.aurzane.com/calculadora-nota-pau/" target="_blank" rel="noopener">No la sé: calcúlala</a></span>
        </div>
        <div id="ovEstudiar"></div>
        <h3 class="ov-sec-t" style="margin:34px 0 14px;">Herramientas de NEXUS</h3>
        <div class="ov-herr">
          <a class="ov-h" id="ovHQue" href="https://nexus.aurzane.com/universidades/que-puedo-estudiar/" target="_blank" rel="noopener"><b>¿Qué puedo estudiar con mi nota?</b><span>Todas las carreras públicas a las que llegas, por comunidad.</span></a>
          <a class="ov-h" href="https://nexus.aurzane.com/universidades/notas-de-corte/" target="_blank" rel="noopener"><b>Notas de corte</b><span>La nota oficial de cada grado en cada universidad.</span></a>
          <a class="ov-h" href="https://nexus.aurzane.com/universidades/espana/" target="_blank" rel="noopener"><b>Universidades de España</b><span>Fichas con titulaciones, precios y ubicación.</span></a>
          <a class="ov-h" href="https://nexus.aurzane.com/calculadora-nota-pau/" target="_blank" rel="noopener"><b>Calculadora de nota de la PAU</b><span>Tu nota de admisión sobre 14 con las ponderaciones.</span></a>
        </div>
        <p class="ov-pie">Datos de notas de corte del Ministerio de Ciencia, Innovación y Universidades (QEDU), cupo general y universidades públicas. Cambian cada año: tómalas como orientación.</p>
      </div>
'''
rep('\n      <!-- MI CUENTA -->', ESTUDIAR + '\n      <!-- MI CUENTA -->')

# ---------- 5. JavaScript ----------
rep("const BC_PAGE_LABELS = { resumen:'Resumen', tests:'Mis Evaluaciones', plan:'Mi Proceso', informe:'Mi Informe', cuenta:'Mi Cuenta' };\n  function goToPage(key){\n",
    "const BC_PAGE_LABELS = { resumen:'Inicio', tests:'Evaluaciones', informe:'Mi informe', estudiar:'Dónde estudiar', cuenta:'Mi cuenta' };\n"
    "  function goToPage(key){\n"
    "    const aElegir = key === 'plan';\n"
    "    if(aElegir || !document.getElementById('page-'+key)) key = aElegir ? 'tests' : 'resumen';\n"
    "    if(key === 'estudiar') pintarEstudiar();\n")
rep("    window.scrollTo({top:0, behavior:'instant'});\n    closeMobileNav();\n  }\n",
    "    window.scrollTo({top:0, behavior:'instant'});\n"
    "    if(aElegir){ const pe = document.getElementById('panelElegir'); if(pe) setTimeout(()=>pe.scrollIntoView({behavior:'smooth', block:'start'}), 30); }\n"
    "    closeMobileNav();\n  }\n"
    "  document.getElementById('navItems').addEventListener('keydown', (e)=>{\n"
    "    const item = e.target.closest('.nav-item');\n"
    "    if(item && item.dataset.page && (e.key === 'Enter' || e.key === ' ')){ e.preventDefault(); goToPage(item.dataset.page); }\n"
    "  });\n")

rep("      { key:'evals-completas', label:'Evaluaciones completadas', done: activos.length > 0 && pendientes.length === 0 },\n    ];",
    "      { key:'evals-completas', label:'Evaluaciones completadas', done: activos.length > 0 && pendientes.length === 0 },\n"
    "      { key:'estudiar', label:'Dónde estudiar', done:false, ir:'estudiar' },\n    ];")
rep("""      <div class="step-item ${s.done?'done':''} ${i===currentIdx?'current':''}">""",
    """      <div class="step-item ${s.done?'done':''} ${i===currentIdx?'current':''}" ${s.ir?`role="link" tabindex="0" onclick="goToPage('${s.ir}')" onkeydown="if(event.key==='Enter')goToPage('${s.ir}')"`:''}>""")

# Siguiente paso: una acción clara y una secundaria, y anillo de progreso
m = re.search(r"  function renderNextStep\(cliente\)\{.*?\n  \}\n\n\n  function renderEvalsProgress\(cliente\)\{.*?\n  \}\n", s, re.S)
assert m
NUEVO_JS = open(__file__.replace('aplicar.py', 'panel.js'), encoding='utf-8').read()
s = s[:m.start()] + NUEVO_JS + s[m.end():]

rep("  function renderPlanPage(cliente){\n", "  function renderPlanPage(cliente){\n    if(!document.getElementById('planSummaryWrap')) return;\n")

# iconos en las tarjetas de Evaluaciones
rep("""          <div class="tc-top">
            <h3>${escapeHtml(info.nombre)}</h3>""",
    """          <div class="tc-top">
            ${ovIcono(a.test_key)}<h3>${escapeHtml(info.nombre)}</h3>""")
rep("${done ? 'Completado ✓' : (started ? 'Continuar evaluación →' : 'Comenzar evaluación →')}",
    "${done ? 'Completada' : (started ? 'Continuar' : 'Comenzar')}")
rep("""<button class="btn ${done?'btn-secondary':'btn-primary'} btn-block" ${done?'disabled':''} onclick="irAlTest('${info.url}')">""",
    """<button class="btn ${done?'btn-secondary':'btn-primary'} btn-block" ${done?'disabled':''} onclick="irAlTest('${info.url}')" aria-label="${done ? 'Completada' : (started ? 'Continuar' : 'Comenzar')} ${escapeHtml(info.nombre)}">""")

# Informe: llevar a «Dónde estudiar» al terminar de leer
rep("""      <div id="clientReportWrap" style="border-top:1px solid var(--line);"></div>
    `;""",
    """      <div id="clientReportWrap" style="border-top:1px solid var(--line);"></div>
      <div class="ov-banda" id="ovBandaInforme" hidden>
        <div><h4>¿Y ahora, dónde lo estudio?</h4><p>Mira en qué universidades se imparten las carreras de tu informe y con qué nota se entró el último curso.</p></div>
        <button class="btn btn-primary" type="button" onclick="goToPage('estudiar')">Ver dónde estudiar</button>
      </div>
    `;""")
rep("""      quitarDevolucionDelInforme(document.getElementById('reportContent'));
    };""",
    """      quitarDevolucionDelInforme(document.getElementById('reportContent'));
      ovCarrerasListas = true;
      pintarEstudiar();
    };""")
rep("      ['mi informe', () => renderInformePage(cliente)],\n",
    "      ['mi informe', () => renderInformePage(cliente)],\n      ['dónde estudiar', () => pintarEstudiar()],\n")

# ---------- 6. Estilos ----------
CSS = open(__file__.replace('aplicar.py', 'panel.css'), encoding='utf-8').read()
rep('}\n</style>\n', '}\n' + CSS + '\n</style>\n')

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
