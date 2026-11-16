  /* ===================== PANEL v3: inicio visual y «Dónde estudiar» ===================== */
  const OV_ICONOS = {
    chaside: { c:'#C9A24B', d:'<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>' },
    holland: { c:'#7C93C9', d:'<path d="M12 3l7.8 4.5v9L12 21l-7.8-4.5v-9z"/><path d="M12 3v18M4.2 7.5l15.6 9M19.8 7.5l-15.6 9"/>' },
    af5:     { c:'#C98BB0', d:'<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>' },
    chte:    { c:'#7FA968', d:'<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 19V5M8 7h7M8 11h5"/>' },
    apt_b:   { c:'#D0905A', d:'<path d="M4 20l5-14h1l5 14M6 15h7"/><path d="M17 9v11M14.5 16.5L17 20l2.5-3.5"/>' },
    apt_a:   { c:'#6FB3C2', d:'<path d="M9 3h6v4a2 2 0 104 0h2v6h-2a2 2 0 100 4h2v4H3V3h2a2 2 0 104 0z"/>' }
  };
  function ovIcono(k){
    const i = OV_ICONOS[k] || { c:'#C9A24B', d:'<circle cx="12" cy="12" r="8"/>' };
    return `<span class="ov-ico" style="--c:${i.c}" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${i.d}</svg></span>`;
  }

  function renderNextStep(cliente){
    const { activos, completados, pendientes } = getEvalStats(cliente);
    const wrap = document.getElementById('nextStepWrap');
    let title = '', body = '', actions = '';

    if(activos.length === 0){
      title = 'Elige tus evaluaciones';
      body = 'Es gratis. Con una sola ya tienes informe; para saber qué carreras encajan contigo, incluye CHASIDE u Holland.';
      actions = `<button class="btn btn-primary" onclick="goToPage('plan')">Elegir evaluaciones</button>`;
    } else if(pendientes.length > 0){
      const first = pendientes[0];
      const info = TEST_INFO[first.test_key];
      const empezada = startedTestKeys.has(first.test_key);
      title = info ? `${empezada ? 'Sigue con' : 'Ahora toca'} ${info.nombre}` : 'Sigue con tus evaluaciones';
      body = (info ? `${info.proposito} Unos ${formatoMinutos(info.tiempoMin)}, y puedes pararla y seguir otro día.` : '') +
        (completados.length > 0 ? ' Tu informe ya está disponible y se completa con cada evaluación.' : '');
      actions = `<button class="btn btn-primary" onclick="irAlTest('${info ? info.url : '#'}')">${empezada ? 'Continuar' : 'Comenzar'} ${info ? escapeHtml(info.nombre) : ''}</button>` +
        (completados.length > 0 ? `<button class="btn btn-ghost" onclick="goToPage('informe')">Ver mi informe</button>` : '');
    } else {
      title = 'Tu informe está listo';
      body = `Terminaste ${completados.length === 1 ? 'tu evaluación' : 'tus ' + completados.length + ' evaluaciones'}. Léelo, descárgalo y mira dónde estudiar las carreras que encajan contigo.`;
      actions = `<button class="btn btn-primary" onclick="goToPage('informe')">Ver mi informe</button>` +
        `<button class="btn btn-ghost" onclick="goToPage('estudiar')">Dónde estudiar</button>`;
    }

    wrap.innerHTML = `
      <h2 class="ov-titulo">${title}</h2>
      <p class="ov-texto">${body}</p>
      ${actions ? `<div class="nc-actions">${actions}</div>` : ''}
    `;
    renderAnillo(cliente);
  }

  function renderAnillo(cliente){
    const el = document.getElementById('ovAnillo');
    if(!el) return;
    const { activos, completados, pendientes } = getEvalStats(cliente);
    if(activos.length === 0){ el.innerHTML = ''; el.hidden = true; return; }
    el.hidden = false;
    const r = 52, C = 2 * Math.PI * r, f = completados.length / activos.length;
    const min = pendientes.reduce((t, a) => t + ((TEST_INFO[a.test_key] || {}).tiempoMin || 0), 0);
    el.innerHTML = `
      <svg viewBox="0 0 128 128" width="148" height="148" role="img" aria-label="${completados.length} de ${activos.length} evaluaciones completadas">
        <circle cx="64" cy="64" r="${r}" fill="none" stroke="var(--navy-4)" stroke-width="11"/>
        <circle cx="64" cy="64" r="${r}" fill="none" stroke="url(#ovGrad)" stroke-width="11" stroke-linecap="round"
          stroke-dasharray="${(C * f).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 64 64)"/>
        <defs><linearGradient id="ovGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="var(--gold-light)"/><stop offset="1" stop-color="var(--gold)"/></linearGradient></defs>
        <text x="64" y="62" text-anchor="middle" class="ov-anillo-n">${completados.length}/${activos.length}</text>
        <text x="64" y="82" text-anchor="middle" class="ov-anillo-l">completadas</text>
      </svg>
      <p>${pendientes.length ? 'Te quedan unos <b>' + formatoMinutos(min) + '</b>' : '<b>¡Todo hecho!</b>'}</p>`;
  }

  function renderEvalsProgress(cliente){
    const { activos } = getEvalStats(cliente);
    const list = document.getElementById('evalsProgressList');
    if(activos.length === 0){
      list.innerHTML = `<div class="empty-state">
        <h4>Todavía no has elegido evaluaciones</h4>
        <p>Elígelas en «Evaluaciones»; el acceso es gratuito.</p>
      </div>`;
      return;
    }
    const orden = activos.slice().sort((a, b) => (a.completado - b.completado) || (ALL_TEST_KEYS.indexOf(a.test_key) - ALL_TEST_KEYS.indexOf(b.test_key)));
    const siguiente = orden.find(a => !a.completado);
    list.innerHTML = orden.map(a => {
      const info = TEST_INFO[a.test_key] || { nombre:a.test_key, proposito:'', tiempoMin:0, url:'#' };
      const estado = a.completado ? 'Completada' : (startedTestKeys.has(a.test_key) ? 'Empezada' : 'Pendiente');
      const accion = a.completado ? `goToPage('informe')` : `irAlTest('${info.url}')`;
      const etiqueta = a.completado ? `Ver ${info.nombre} en el informe` : `${startedTestKeys.has(a.test_key) ? 'Continuar' : 'Comenzar'} ${info.nombre}`;
      return `<button type="button" class="ov-tile ${a.completado ? 'hecha' : ''} ${a === siguiente ? 'sig' : ''}" onclick="${accion}" aria-label="${escapeHtml(etiqueta)}">
        ${ovIcono(a.test_key)}
        <span class="ov-tile-n">${escapeHtml(info.nombre)}</span>
        <span class="ov-tile-m">${a.completado ? 'Ver en el informe' : formatoMinutos(info.tiempoMin) + ' · ' + info.preguntas + ' preguntas'}</span>
        <span class="ov-est ${a.completado ? 'ok' : (estado === 'Empezada' ? 'mid' : '')}">${estado}</span>
      </button>`;
    }).join('') + (activos.length < ALL_TEST_KEYS.length
      ? `<button type="button" class="ov-tile ov-add" onclick="goToPage('plan')"><span class="ov-plus" aria-hidden="true">+</span><span class="ov-tile-n">Añadir evaluaciones</span><span class="ov-tile-m">Tienes ${ALL_TEST_KEYS.length - activos.length} más disponibles</span></button>`
      : '');
  }

  /* ---------- Carreras del informe → NEXUS ---------- */
  // Las carreras salen tal cual del informe (CHASIDE u Holland). Para buscarlas en
  // NEXUS se usa el nombre con el que aparecen en los grados españoles.
  const OV_BUSQUEDA = {
    'Contabilidad y Auditoría':'contabilidad', 'Turismo y Hotelería':'turismo', 'Comunicación Social':'comunicación',
    'Educación / Pedagogía':'pedagogía', 'Artes Plásticas':'bellas artes', 'Diseño de Modas':'moda', 'Cine y Audiovisuales':'cine',
    'Danza y Artes Escénicas':'artes escénicas', 'Fisioterapia / Rehabilitación':'fisioterapia', 'Obstetricia':'enfermería',
    'Cultura Física y Deportes':'actividad física', 'Ingeniería en Sistemas / Software':'ingeniería del software',
    'Ingeniería Industrial':'tecnologías industriales', 'Ciencias de la Computación':'informática', 'Ciencias Militares':'militar',
    'Seguridad y Defensa':'defensa', 'Ciencias Policiales':'policial', 'Gestión de Riesgos y Emergencias':'seguridad',
    'Marina Mercante':'náutica', 'Aeronáutica':'aeroespacial', 'Agronomía':'agrícola', 'Ingeniería Agroindustrial':'agroalimentaria',
    'Medicina Veterinaria':'veterinaria', 'Tecnologías en electricidad y electrónica':'eléctrica',
    'Carreras técnicas y militares de campo':'militar', 'Ingeniería de Software':'ingeniería del software', 'Artes Visuales':'bellas artes',
    'Fonoaudiología':'logopedia', 'Orientación y consejería':'educación social', 'Comercio Exterior':'comercio'
  };
  let ovCarrerasListas = false;
  function ovBusqueda(c){ return OV_BUSQUEDA[c] || c.replace(/\s*\/.*$/, ''); }
  function ovNota(){ try{ return localStorage.getItem('aurzane-ovp-nota') || ''; }catch(e){ return ''; } }
  function ovUrlCarrera(c){
    const n = ovNota();
    return 'https://nexus.aurzane.com/universidades/que-puedo-estudiar/?carrera=' + encodeURIComponent(ovBusqueda(c)) + (n ? '&nota=' + encodeURIComponent(n) : '');
  }
  function carrerasDelInforme(){
    const rc = document.getElementById('reportContent');
    if(!rc) return [];
    return [...rc.querySelectorAll('.career-card')].map(card => {
      const h = card.querySelector('h4');
      const t = h && h.firstChild ? h.firstChild.textContent.trim() : '';
      const m = t.match(/^(Prioridad|Alternativa):\s*(.*)$/);
      let area = (m ? m[2] : t).trim();
      area = area.charAt(0).toUpperCase() + area.slice(1);
      const bloque = [...card.querySelectorAll('.career-list')].find(d => /^Carreras/.test(((d.querySelector('b') || {}).textContent) || ''));
      const carreras = bloque ? bloque.textContent.replace(/^[^:]*:\s*/, '').replace(/\.\s*$/, '').split(/,\s*/).map(x => x.trim()).filter(Boolean) : [];
      return { tipo: m ? m[1] : '', area, carreras };
    }).filter(a => a.carreras.length);
  }
  function ovChips(lista, max){
    return lista.slice(0, max || lista.length).map(c =>
      `<a class="ov-chip" href="${ovUrlCarrera(c)}" target="_blank" rel="noopener" aria-label="Dónde estudiar ${escapeHtml(c)} (abre NEXUS)">${escapeHtml(c)}</a>`).join('');
  }
  function pintarEstudiar(){
    const res = document.getElementById('ovEstudiarResumen'), pag = document.getElementById('ovEstudiar');
    if(!res || !pag || !clienteCache) return;
    const areas = carrerasDelInforme();
    const banda = document.getElementById('ovBandaInforme');
    if(banda) banda.hidden = !areas.length;
    const incluidos = (typeof ovpTestsDelInforme === 'function') ? ovpTestsDelInforme(clienteCache) : [];
    const conIntereses = incluidos.includes('chaside') || incluidos.includes('holland');
    const n = ovNota();
    const q = document.getElementById('ovHQue');
    if(q) q.href = 'https://nexus.aurzane.com/universidades/que-puedo-estudiar/' + (n ? '?nota=' + encodeURIComponent(n) : '');

    if(areas.length){
      res.innerHTML = `<div class="ov-areas-mini">${areas.map(a => `
        <div class="ov-area-mini"><span class="ov-tipo">${a.tipo === 'Alternativa' ? 'También encaja' : 'Tu área principal'}</span><b>${escapeHtml(a.area)}</b>
          <div class="ov-chips">${ovChips(a.carreras, 5)}</div></div>`).join('')}</div>`;
      pag.innerHTML = areas.map(a => `
        <section class="ov-area ${a.tipo === 'Alternativa' ? '' : 'principal'}">
          <span class="ov-tipo">${a.tipo === 'Alternativa' ? 'También encaja contigo' : 'Tu área principal'}</span>
          <h3>${escapeHtml(a.area)}</h3>
          <p>Toca una carrera para ver en qué universidades se estudia y su nota de corte${n ? ' comparada con tu ' + escapeHtml(n.replace('.', ',')) : ''}.</p>
          <div class="ov-chips">${ovChips(a.carreras)}</div>
        </section>`).join('');
      return;
    }
    const cha = (clienteCache.activaciones || []).find(a => a.test_key === 'chaside' && a.activo);
    const accion = conIntereses
      ? '<p class="ov-cargando">Preparando tus carreras…</p>'
      : (cha ? `<button class="btn btn-primary btn-sm" onclick="irAlTest('${TEST_INFO.chaside.url}')">${startedTestKeys.has('chaside') ? 'Continuar' : 'Hacer'} CHASIDE</button>`
             : `<button class="btn btn-primary btn-sm" onclick="goToPage('plan')">Añadir CHASIDE u Holland</button>`);
    const vacio = conIntereses && !ovCarrerasListas ? accion : `
      <div class="ov-vacio">
        <div><h4>Aquí verás tus carreras</h4><p>Aparecen cuando completas CHASIDE u Holland, las evaluaciones de intereses. Después podrás ver dónde se estudian y con qué nota.</p></div>
        ${conIntereses ? '' : accion}
      </div>`;
    res.innerHTML = vacio;
    pag.innerHTML = vacio;
  }
  (function(){
    const inp = document.getElementById('ovNota');
    if(!inp) return;
    inp.value = ovNota();
    inp.addEventListener('input', () => {
      const v = String(inp.value || '').replace(',', '.');
      const ok = v && !isNaN(v) && +v >= 5 && +v <= 14;
      try{ ok ? localStorage.setItem('aurzane-ovp-nota', v) : localStorage.removeItem('aurzane-ovp-nota'); }catch(e){}
      pintarEstudiar();
    });
  })();

  /* ---------- Compartir el informe con el colegio (lo decide el estudiante) ---------- */
  async function pintarColegio(){
    const w = document.getElementById('ovColegio');
    if(!w) return;
    const { data, error } = await sb.rpc('ovp_mi_colegio');
    const c = !error && data && data[0];
    if(!c){ w.hidden = true; return; }
    w.hidden = false;
    const nombre = escapeHtml(c.nombre + (c.subtitulo ? ' ' + c.subtitulo : ''));
    w.innerHTML = `<div class="panel-head"><h3>Tu colegio</h3></div><div class="panel-body ov-col">
      <p>Entraste con el enlace de <b>${nombre}</b>. Tu colegio ve cuántas evaluaciones llevas. Tu informe solo lo ve si tú lo compartes.</p>
      <label class="ov-sw"><input type="checkbox" id="ovComparte" ${c.comparte ? 'checked' : ''}><span>Compartir mi informe con ${nombre}</span></label>
      <small id="ovComparteMsg" aria-live="polite"></small></div>`;
    document.getElementById('ovComparte').addEventListener('change', async (e) => {
      const msg = document.getElementById('ovComparteMsg');
      const { error } = await sb.rpc('ovp_compartir_colegio', { p: e.target.checked });
      if(error){ e.target.checked = !e.target.checked; msg.textContent = 'No se pudo guardar. Inténtalo de nuevo.'; return; }
      msg.textContent = e.target.checked ? 'Compartido. Puedes dejar de compartirlo cuando quieras.' : 'Ya no se comparte.';
    });
  }
