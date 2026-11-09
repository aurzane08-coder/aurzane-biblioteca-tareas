import { cierre, cadena } from './store-local.js?v=f15';
// Progreso del alumno en Supabase (ligado a su cuenta de AURZANE ID).
// Lee sus filas con RLS y escribe solo a través de las funciones del servidor.
export async function createSupabaseStore(sb, data, slug) {
  const C = data.curso();
  const lecKey = new Map(); C.modules.forEach((m) => m.lecciones.forEach((l) => lecKey.set(l.id, `${m.slug}/${l.slug}`)));
  const titulo = (modSlug) => { const m = C.modules.find((x) => x.slug === modSlug); return m ? `Evaluación: ${m.titulo}` : 'Evaluación final integradora'; };
  const LOCAL = `aurzane-curso-${slug}-ultima`;
  let ultima = null; try { ultima = JSON.parse(localStorage.getItem(LOCAL)); } catch (e) {}
  let st = { lecciones: {}, intentos: [], abiertos: {}, repaso: [], ultima, raices: [] };
  let apuntes = {}; // clave de lección -> {texto, fecha}
  let estudio = {}; // módulo -> tipo -> clave -> datos (tarjetas, Feynman, sesión por bloques)
  const modId = (slug) => (C.modules.find((m) => m.slug === slug) || {}).id;

  async function refrescar() {
    const [prog, ints, rep] = await Promise.all([
      sb.from('course_progress').select('lesson_id,visitado_at,completado_at'),
      sb.from('course_attempts').select('id,module_id,modo,estado,nota,question_ids,started_at,finished_at,ronda_de,ronda,cerrado_at').eq('course_id', data.cursoId).order('started_at'),
      sb.from('course_review_queue').select('question_id,due_at,paso,fallos'),
    ]);
    for (const r of [prog, ints, rep]) if (r.error) throw r.error;
    const lecciones = {};
    prog.data.forEach((p) => { const k = lecKey.get(p.lesson_id); if (k) lecciones[k] = { visita: Date.parse(p.visitado_at), completada: p.completado_at ? Date.parse(p.completado_at) : null }; });
    const abiertos = {}; const intentos = []; const raices = [];
    const abiertosIds = ints.data.filter((a) => a.estado === 'abierto').map((a) => a.id);
    let resp = { data: [] };
    if (abiertosIds.length) resp = await sb.from('course_responses').select('attempt_id').in('attempt_id', abiertosIds);
    ints.data.forEach((a) => {
      const clave = a.module_id ? data.moduloSlug(a.module_id) : 'final';
      if (!a.ronda_de) raices.push({ id: a.id, clave, items: a.question_ids, cerrado: a.cerrado_at ? Date.parse(a.cerrado_at) : null, inicio: Date.parse(a.started_at) });
      if (a.estado === 'abierto') abiertos[clave] = { respondidas: (resp.data || []).filter((r) => r.attempt_id === a.id).length, total: a.question_ids.length, ronda: a.ronda || 1 };
      else if (a.nota != null) intentos.push({ id: a.id, raiz: a.ronda_de || a.id, ronda: a.ronda || 1, clave, titulo: titulo(clave), modo: a.modo, nota: Number(a.nota), n: a.question_ids.length, fin: Date.parse(a.finished_at) });
    });
    st = { lecciones, intentos, abiertos, repaso: rep.data.filter((r) => data.item(r.question_id)), ultima: st.ultima, raices };
    // apuntes: si la tabla aún no existe, el curso sigue funcionando sin ellos
    const ap = await sb.from('course_notes').select('lesson_id,texto,updated_at');
    const es = await sb.from('course_study').select('module_id,tipo,clave,datos,updated_at');
    if (!es.error) { estudio = {}; es.data.forEach((r) => { const m = data.moduloSlug(r.module_id); if (!m) return; ((estudio[m] = estudio[m] || {})[r.tipo] = estudio[m][r.tipo] || {})[r.clave] = { ...r.datos, _fecha: Date.parse(r.updated_at) }; }); }
    if (!ap.error) { apuntes = {}; ap.data.forEach((a) => { const k = lecKey.get(a.lesson_id); if (k) apuntes[k] = { texto: a.texto, fecha: Date.parse(a.updated_at) }; }); }
  }
  await refrescar();
  const mark = (key, completada) => {
    const [m, l] = key.split('/'); const id = data.leccionId(m, l);
    if (id) sb.rpc('course_mark_lesson', { p_lesson: id, p_completada: completada }).then(({ error }) => { if (error) console.warn(error.message); });
  };

  return {
    get: () => st,
    refrescar,
    apunte: (key) => apuntes[key] || null,
    apuntes: () => apuntes,
    async guardarApunte(key, texto) {
      const [m, l] = key.split('/'); const id = data.leccionId(m, l);
      if (!id) throw new Error('Lección desconocida');
      const { data: fecha, error } = await sb.rpc('course_save_note', { p_lesson: id, p_texto: texto });
      if (error) throw new Error(error.message);
      if (texto.trim()) apuntes[key] = { texto, fecha: Date.parse(fecha) }; else delete apuntes[key];
      return apuntes[key] || null;
    },
    estudio: (mod, tipo) => ((estudio[mod] || {})[tipo]) || {},
    async guardarEstudio(mod, tipo, clave, datos) {
      const id = modId(mod); if (!id) throw new Error('Tema desconocido');
      const { data: fecha, error } = await sb.rpc('course_save_study', { p_module: id, p_tipo: tipo, p_clave: clave, p_datos: datos });
      if (error) throw new Error(error.message);
      const t = ((estudio[mod] = estudio[mod] || {})[tipo] = estudio[mod][tipo] || {});
      if (datos == null) delete t[clave]; else t[clave] = { ...datos, _fecha: Date.parse(fecha) };
      return t[clave] || null;
    },
    async reset() { const { error } = await sb.rpc('course_reset_my_progress', { p_course: slug }); if (error) throw error; await refrescar(); },
    visitar(key, u) {
      const l = (st.lecciones[key] = st.lecciones[key] || {}); if (!l.visita) { l.visita = Date.now(); mark(key, false); }
      st.ultima = u; try { localStorage.setItem(LOCAL, JSON.stringify(u)); } catch (e) {}
    },
    completar(key) { const l = (st.lecciones[key] = st.lecciones[key] || {}); l.visita = l.visita || Date.now(); l.completada = Date.now(); mark(key, true); },
    pendientesRepaso() { const now = Date.now(); return st.repaso.filter((r) => Date.parse(r.due_at) <= now).sort((a, b) => Date.parse(a.due_at) - Date.parse(b.due_at)).map((r) => r.question_id); },
    proximoRepaso() { const ds = st.repaso.map((r) => Date.parse(r.due_at)); return ds.length ? Math.min(...ds) : null; },
    resumenAbierto: (clave) => st.abiertos[clave] || null,
    intentos: (clave) => st.intentos.filter((i) => i.clave === clave),
    // test del tema cerrado al 100 %: un intento raíz cerrado que cubría todas las preguntas publicadas del tema
    cierreTema(clave) { return cierre(st.raices, clave, data); },
    // última cadena de rondas sin cerrar: {raiz, ultimo intento terminado, falladas pendientes}
    cadenaAbierta(clave) { return cadena(st, clave); },
    mejorNota(clave) { const xs = st.intentos.filter((i) => i.clave === clave && i.modo === 'examen').map((i) => i.nota); return xs.length ? Math.max(...xs) : null; },
  };
}
