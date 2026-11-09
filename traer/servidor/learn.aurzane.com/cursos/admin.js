// Panel de cursos de AURZANE LEARN. Separado del panel de OVP: solo trabaja con
// tablas course_* y exige el permiso courses.write (publicar exige courses.publish).
// Las soluciones se leen y guardan con course_admin_get_question / course_admin_save_question.
import { mountItem, renderFigura, bindFigura } from './engine.js?v=f15';
import { esc, bloquesHTML, textoABloques, bloquesATexto, activarMedios } from './contenido.js?v=f15';
activarMedios();
import { corregirConClave, textoSolucion } from './data-local.js';

const SUPABASE_URL = 'https://chtfpqwrrarfdjcivlad.supabase.co';
const SUPABASE_KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw';
const CURSO = (() => { const c = new URLSearchParams(location.search).get('c'); return /^[a-z0-9-]{3,40}$/.test(c || '') ? c : 'neuro-300260'; })();
const TIPOS = {
  seleccion_multiple: 'Selección múltiple', caso_clinico: 'Caso clínico', cortes: 'Cortes e imagen', verdadero_falso_razonado: 'Verdadero o falso razonado',
  ordenar: 'Ordenar', relacionar: 'Relacionar', respuesta_breve: 'Respuesta breve', identificacion_imagen: 'Identificación en imagen', arrastrar_soltar: 'Colocar etiquetas',
};
const LICENCIAS = { 'propia-cc-by-4.0': 'Propia (CC BY 4.0)', 'dominio-publico': 'Dominio público', cc0: 'CC0', 'cc-by-4.0': 'CC BY 4.0', 'cc-by-sa-4.0': 'CC BY-SA 4.0', 'permiso-escrito': 'Permiso escrito del autor' };
const $ = (s, el = document) => el.querySelector(s);
const main = () => $('#main');
const slugify = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'imagen';
const lineas = (t) => String(t || '').split('\n').map((x) => x.trim()).filter(Boolean);
let sb, S = {};

function toast(m) { const t = $('#toast'); t.textContent = m; t.hidden = false; clearTimeout(toast.h); toast.h = setTimeout(() => { t.hidden = true; }, 2600); }
async function q(p) { const { data, error } = await p; if (error) throw new Error(error.message); return data; }
const puede = (c) => S.caps.includes(c);

// ---------- carga ----------
async function cargar() {
  S.curso = await q(sb.from('course_courses').select('*').eq('slug', CURSO).maybeSingle());
  if (!S.curso) throw new Error('No se encontró el curso ' + CURSO + '. ¿Se cargó la carga inicial?');
  const [mods, lecs, media, regs, pregs] = await Promise.all([
    q(sb.from('course_modules').select('*').eq('course_id', S.curso.id).order('orden')),
    q(sb.from('course_lessons').select('*').order('orden')),
    q(sb.from('course_media').select('*').eq('course_id', S.curso.id).order('titulo')),
    q(sb.from('course_media_regions').select('*').order('orden')),
    todas(() => sb.from('course_questions').select('id,legacy_id,module_id,lesson_id,tipo,enunciado,estado,dificultad,etiquetas,media_id,updated_at').eq('course_id', S.curso.id).order('updated_at', { ascending: false })),
  ]);
  const ids = new Set(mods.map((m) => m.id));
  Object.assign(S, { mods, lecs: lecs.filter((l) => ids.has(l.module_id)), media, regs, pregs });
  S.mod = new Map(mods.map((m) => [m.id, m]));
  await firmar();
}
async function todas(f) { const out = []; for (let i = 0; ; i += 1000) { const d = await q(f().range(i, i + 999)); out.push(...d); if (d.length < 1000) return out; } }
async function firmar() {
  const rutas = S.media.filter((m) => m.tipo === 'imagen' && m.storage_path).map((m) => m.storage_path);
  S.urls = new Map();
  if (rutas.length) { const { data } = await sb.storage.from('course-media').createSignedUrls(rutas, 21600); (data || []).forEach((u) => u.signedUrl && S.urls.set(u.path, u.signedUrl)); }
}
function figura(slugOrId) {
  const m = S.media.find((x) => x.slug === slugOrId || x.id === slugOrId); if (!m) return null;
  const vb = String(m.view_box || '0 0 100 100').split(/\s+/).map(Number);
  return { id: m.slug, titulo: m.titulo, alt: m.alt, viewBox: m.view_box, dibujo: m.dibujo, etiquetas: m.etiquetas, credito: m.credito,
    imagen: m.tipo === 'imagen' ? { url: S.urls.get(m.storage_path) || '', w: vb[2], h: vb[3] } : null,
    regions: S.regs.filter((r) => r.media_id === m.id).map((r) => ({ id: r.region_key, nombre: r.nombre, latin: r.latin, info: r.info, shape: r.forma,
      ...(r.forma === 'circle' ? { c: r.coords.c, r: r.coords.r } : { pts: r.coords }), ...(r.coords_espejo ? { pts2: r.coords_espejo } : {}) })) };
}

// ---------- marco ----------
function rail(r) {
  const items = [['#/', 'Resumen'], ['#/preguntas', 'Preguntas'], ['#/pregunta/nueva', 'Nueva pregunta'], ['#/imagenes', 'Imágenes y zonas'], ['#/lecciones', 'Lecciones']];
  $('#rail').innerHTML = `<nav aria-label="Panel">${items.map(([h, t]) => `<a href="${h}" ${('#/' + (r || '')) === h ? 'aria-current="page"' : ''}>${t}</a>`).join('')}</nav>
    <h5>Tu acceso</h5><p class="meta" style="padding:0 24px">${S.caps.includes('admin') ? 'Administrador' : S.caps.filter((c) => c.startsWith('courses.')).join(', ')}</p>`;
}
const estado = (e) => `<span class="estado ${esc(e)}">${esc(e)}</span>`;
const opcModulos = (sel, vacio = true) => (vacio ? '<option value="">Sin módulo</option>' : '') + S.mods.map((m) => `<option value="${m.id}" ${m.id === sel ? 'selected' : ''}>${m.orden}. ${esc(m.titulo)}</option>`).join('');
const opcLecciones = (mod, sel) => '<option value="">Todo el módulo</option>' + S.lecs.filter((l) => l.module_id === mod).map((l) => `<option value="${l.id}" ${l.id === sel ? 'selected' : ''}>${l.orden}. ${esc(l.titulo)}</option>`).join('');
const opcMedia = (sel) => '<option value="">Elige una imagen</option>' + S.media.map((m) => `<option value="${m.id}" ${m.id === sel ? 'selected' : ''}>${esc(m.titulo)}</option>`).join('');

// ---------- resumen ----------
function vResumen() {
  const cuenta = (f) => S.pregs.filter(f).length;
  const revisar = cuenta((p) => (p.etiquetas || []).includes('revisar-redaccion'));
  main().innerHTML = `<div class="c-wide"><h1 class="h-curso">${esc(S.curso.titulo)}</h1>
    <p class="lead">Estado del curso: ${estado(S.curso.estado)}. ${S.curso.estado === 'publicado' ? 'Lo ven todas las cuentas cuando el interruptor learn.courses.enabled está activo.' : 'Solo lo ven los editores.'}</p>
    <div class="cifras"><div><b>${S.pregs.length}</b>preguntas</div><div><b>${cuenta((p) => p.estado === 'publicada')}</b>publicadas</div><div><b>${cuenta((p) => p.estado === 'borrador')}</b>en borrador</div><div><b>${revisar}</b>por revisar redacción</div><div><b>${S.media.length}</b>imágenes</div><div><b>${S.lecs.filter((l) => (l.bloques || []).length).length} de ${S.lecs.length}</b>lecciones con texto</div></div>
    ${puede('courses.publish') ? `<div class="row" style="margin:14px 0">${S.curso.estado === 'publicado' ? '<button class="btn sec" id="cursoEstado" data-e="borrador">Retirar el curso (volver a borrador)</button>' : '<button class="btn" id="cursoEstado" data-e="publicado">Publicar el curso</button>'}<span class="meta">El interruptor learn.courses.enabled se activa en Configuración del panel de aurzane.com.</span></div>` : ''}
    <h2 class="h2">Preguntas por módulo</h2>
    <div class="scroll-x"><table class="adm-tabla"><thead><tr><th>Módulo</th><th>Publicadas</th><th>Borrador</th><th>Archivadas</th><th>Tipos</th></tr></thead><tbody>
    ${S.mods.map((m) => { const ps = S.pregs.filter((p) => p.module_id === m.id); return `<tr><td><a href="#/preguntas?m=${m.id}">${m.orden}. ${esc(m.titulo)}</a></td><td class="num">${ps.filter((p) => p.estado === 'publicada').length}</td><td class="num">${ps.filter((p) => p.estado === 'borrador').length}</td><td class="num">${ps.filter((p) => p.estado === 'archivada').length}</td><td>${[...new Set(ps.map((p) => TIPOS[p.tipo]))].join(', ')}</td></tr>`; }).join('')}
    </tbody></table></div>
    ${revisar ? `<p style="margin-top:14px"><a class="btn sec" href="#/preguntas?e=revisar-redaccion">Revisar las ${revisar} preguntas que mencionan la clase</a></p>` : ''}</div>`;
  const b = $('#cursoEstado');
  if (b) b.addEventListener('click', async () => { try { await q(sb.from('course_courses').update({ estado: b.dataset.e }).eq('id', S.curso.id)); S.curso.estado = b.dataset.e; toast('Curso actualizado'); vResumen(); } catch (e) { toast(e.message); } });
}

// ---------- lista de preguntas ----------
function vPreguntas(params) {
  const f = { m: params.get('m') || '', t: params.get('t') || '', s: params.get('s') || '', e: params.get('e') || '', q: params.get('q') || '' };
  main().innerHTML = `<div class="c-wide"><h1 class="h-curso">Preguntas</h1>
    <form class="filtros" id="fil">
      <select name="m" aria-label="Módulo"><option value="">Todos los módulos</option>${opcModulos(f.m, false)}</select>
      <select name="t" aria-label="Tipo"><option value="">Todos los tipos</option>${Object.entries(TIPOS).map(([k, v]) => `<option value="${k}" ${k === f.t ? 'selected' : ''}>${v}</option>`).join('')}</select>
      <select name="s" aria-label="Estado"><option value="">Todos los estados</option>${['publicada', 'borrador', 'archivada'].map((x) => `<option ${x === f.s ? 'selected' : ''}>${x}</option>`).join('')}</select>
      <input name="e" placeholder="Etiqueta" value="${esc(f.e)}" aria-label="Etiqueta"><input name="q" placeholder="Buscar en el enunciado" value="${esc(f.q)}" aria-label="Buscar">
      <button class="btn sec">Filtrar</button></form>
    <div id="lista"></div></div>`;
  $('#fil').addEventListener('submit', (e) => { e.preventDefault(); const p = new URLSearchParams([...new FormData(e.target)].filter(([, v]) => v)); location.hash = '#/preguntas' + (p.toString() ? '?' + p : ''); });
  const norm = (x) => String(x).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const res = S.pregs.filter((p) => (!f.m || p.module_id === f.m) && (!f.t || p.tipo === f.t) && (!f.s || p.estado === f.s) && (!f.e || (p.etiquetas || []).includes(f.e)) && (!f.q || norm(p.enunciado).includes(norm(f.q))));
  let pag = 0;
  const pinta = () => {
    const vis = res.slice(0, (pag + 1) * 50);
    $('#lista').innerHTML = `<p class="meta">${res.length} preguntas</p><div class="scroll-x"><table class="adm-tabla"><thead><tr><th>Enunciado</th><th>Tipo</th><th>Módulo</th><th>Estado</th></tr></thead><tbody>
      ${vis.map((p) => `<tr><td><a href="#/pregunta/${p.id}">${esc(p.enunciado.slice(0, 110))}${p.enunciado.length > 110 ? '…' : ''}</a></td><td>${TIPOS[p.tipo]}</td><td>${S.mod.get(p.module_id) ? S.mod.get(p.module_id).orden : ''}</td><td>${estado(p.estado)}</td></tr>`).join('')}</tbody></table></div>
      ${vis.length < res.length ? '<button class="btn sec" id="mas" style="margin-top:12px">Ver más</button>' : ''}`;
    const mas = $('#mas'); if (mas) mas.addEventListener('click', () => { pag++; pinta(); });
  };
  pinta();
}

// ---------- editor de preguntas ----------
async function vPregunta(id) {
  let p = { tipo: 'seleccion_multiple', module_id: S.mods[0]?.id, lesson_id: null, enunciado: '', caso: '', payload: { opciones: ['', ''] }, clave: { correcta: [0] }, dificultad: 2, objetivo: '', etiquetas: [], fuente: '', explicacion: '', estado: 'borrador', problemas: [] };
  if (id !== 'nueva') {
    try { p = await q(sb.rpc('course_admin_get_question', { p_id: id })); } catch (e) { main().innerHTML = `<p class="problemas">${esc(e.message)}</p>`; return; }
    if (!p) { main().innerHTML = '<p class="problemas">La pregunta no existe.</p>'; return; }
  }
  const M = modeloDesde(p);
  main().innerHTML = `<div class="dos-col"><form class="form" id="fp" novalidate>
    <div class="row" style="justify-content:space-between"><h1 class="h3" style="margin:0">${id === 'nueva' ? 'Nueva pregunta' : 'Editar pregunta'}</h1>${id !== 'nueva' ? estado(p.estado) : ''}</div>
    <div class="grid2"><label>Módulo<select name="module_id">${opcModulos(p.module_id, false)}</select></label><label>Lección<select name="lesson_id">${opcLecciones(p.module_id, p.lesson_id)}</select></label></div>
    <div class="grid2"><label>Tipo<select name="tipo">${Object.entries(TIPOS).map(([k, v]) => `<option value="${k}" ${k === p.tipo ? 'selected' : ''}>${v}</option>`).join('')}</select></label><label>Dificultad<select name="dificultad">${[1, 2, 3].map((n) => `<option ${n === p.dificultad ? 'selected' : ''}>${n}</option>`).join('')}</select></label></div>
    <label id="lcaso">Caso clínico<textarea name="caso">${esc(p.caso || '')}</textarea></label>
    <label>Enunciado<textarea name="enunciado" required>${esc(p.enunciado)}</textarea></label>
    <div class="caja" id="tipoBox"></div>
    <label>Explicación de la solución<textarea name="explicacion">${esc(p.explicacion || '')}</textarea></label>
    <div class="grid2"><label>Objetivo de aprendizaje<input type="text" name="objetivo" value="${esc(p.objetivo || '')}"></label><label>Etiquetas (separadas por comas)<input type="text" name="etiquetas" value="${esc((p.etiquetas || []).join(', '))}"></label></div>
    <label>Fuente o referencia<input type="text" name="fuente" value="${esc(p.fuente || '')}"></label>
    <div id="prob"></div>
    <div class="row"><button class="btn" type="submit">Guardar</button><button class="btn sec" type="button" id="bPrev">Vista previa</button>
      ${id !== 'nueva' ? `${p.estado !== 'publicada' ? '<button class="btn sec" type="button" data-estado="publicada">Publicar</button>' : '<button class="btn sec" type="button" data-estado="borrador">Pasar a borrador</button>'}${p.estado !== 'archivada' ? '<button class="btn sec" type="button" data-estado="archivada">Archivar</button>' : ''}` : ''}
      <a class="btn sec" href="#/preguntas">Volver</a></div>
  </form><div><h2 class="h3" style="margin-top:0">Vista previa</h2><div class="vista" id="vista"><p class="meta">Pulsa «Vista previa» para probar la pregunta como la verá el alumno.</p></div></div></div>`;
  const fp = $('#fp');
  const sync = () => { $('#lcaso').hidden = fp.tipo.value !== 'caso_clinico'; };
  fp.module_id.addEventListener('change', () => { fp.lesson_id.innerHTML = opcLecciones(fp.module_id.value, null); });
  fp.tipo.addEventListener('change', () => { M.tipo = fp.tipo.value; M.reset(); editorTipo(M); sync(); });
  sync(); editorTipo(M); problemas(p.problemas || []);

  const recoger = () => {
    const { payload: base, clave } = M.construir();
    // la imagen real de la pregunta (fase 9) no se edita aquí: se conserva tal cual
    const payload = (p.payload || {}).imagen ? { ...base, imagen: p.payload.imagen } : base;
    return { id: id === 'nueva' ? null : id, course_id: S.curso.id, module_id: fp.module_id.value || null, lesson_id: fp.lesson_id.value || null, tipo: fp.tipo.value,
      enunciado: fp.enunciado.value.trim(), caso: fp.caso.value.trim(), payload, clave, media_id: M.media || null, dificultad: +fp.dificultad.value,
      objetivo: fp.objetivo.value.trim(), etiquetas: fp.etiquetas.value.split(',').map((x) => x.trim()).filter(Boolean), fuente: fp.fuente.value.trim(), explicacion: fp.explicacion.value.trim() };
  };
  fp.addEventListener('submit', async (e) => {
    e.preventDefault(); const d = recoger();
    if (d.enunciado.length < 5) return problemas(['Escribe un enunciado de al menos 5 caracteres']);
    try {
      const nid = await q(sb.rpc('course_admin_save_question', { p: d }));
      const r = await q(sb.rpc('course_admin_get_question', { p_id: nid }));
      await recargarPregunta(nid); toast('Pregunta guardada');
      if (id === 'nueva') { location.hash = '#/pregunta/' + nid; return; }
      problemas(r.problemas || [], true);
    } catch (err) { problemas([err.message]); }
  });
  $('#bPrev').addEventListener('click', () => {
    const d = recoger(); const item = { id: 'vista', tipo: d.tipo, enunciado: d.enunciado || '(sin enunciado)', caso: d.caso, figura: M.media ? (S.media.find((m) => m.id === M.media) || {}).slug : null, ...d.payload };
    const fig = item.figura ? figura(item.figura) : null;
    const data = { figura: () => fig, solucionTexto: (it, sol) => textoSolucion(it, sol, fig), comprobar: async (it, resp) => ({ ...corregirConClave(d.tipo, d.clave, resp), explicacion: d.explicacion }) };
    try { mountItem($('#vista'), item, { modo: 'practica', numero: 1, total: 1, data, onResult: () => {}, onNext: () => $('#bPrev').click(), textoSiguiente: 'Probar otra vez' }); }
    catch (err) { $('#vista').innerHTML = `<p class="problemas">No se puede mostrar todavía: completa los campos del tipo de pregunta.</p>`; }
  });
  fp.querySelectorAll('[data-estado]').forEach((b) => b.addEventListener('click', async () => {
    try {
      const r = await q(sb.rpc('course_admin_set_question_state', { p_id: id, p_estado: b.dataset.estado }));
      if (!r.ok) return problemas(r.problemas);
      await recargarPregunta(id); toast('Estado cambiado'); vPregunta(id);
    } catch (err) { problemas([err.message]); }
  }));
}
function problemas(lista, mostrarOk) {
  const box = $('#prob'); if (!box) return;
  box.innerHTML = lista.length ? `<div class="problemas" role="alert"><strong>Antes de publicar falta:</strong><ul>${lista.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>` : mostrarOk ? '<div class="problemas ok">La pregunta está completa y se puede publicar.</div>' : '';
}
async function recargarPregunta(id) {
  const r = await q(sb.from('course_questions').select('id,legacy_id,module_id,lesson_id,tipo,enunciado,estado,dificultad,etiquetas,media_id,updated_at').eq('id', id).maybeSingle());
  S.pregs = S.pregs.filter((x) => x.id !== id); if (r) S.pregs.unshift(r);
}

// Modelo editable de la parte específica de cada tipo
function modeloDesde(p) {
  const pl = p.payload || {}; const k = p.clave || {};
  const M = { tipo: p.tipo, media: p.media_id || null };
  M.reset = () => { M.ops = [{ t: '', ok: true }, { t: '', ok: false }]; M.valor = true; M.razones = [{ t: '', ok: true }, { t: '', ok: false }]; M.pasos = ['', '', '']; M.pares = [['', ''], ['', '']]; M.acept = ''; M.sol = ''; M.region = ''; M.etqs = [{ t: '', r: '' }]; };
  M.reset();
  if (['seleccion_multiple', 'caso_clinico', 'cortes'].includes(p.tipo)) M.ops = (pl.opciones || []).map((t, i) => ({ t, ok: (k.correcta || []).includes(i) }));
  if (p.tipo === 'verdadero_falso_razonado') { M.valor = !!k.valor; M.razones = (pl.razones || []).map((t, i) => ({ t, ok: String(i) === String(k.razon) })); }
  if (p.tipo === 'ordenar') M.pasos = k.orden || pl.elementos || M.pasos;
  if (p.tipo === 'relacionar') M.pares = Object.entries(k.pares || {});
  if (p.tipo === 'respuesta_breve') { M.acept = (k.aceptadas || []).join('\n'); M.sol = k.solucion || ''; }
  if (p.tipo === 'identificacion_imagen') M.region = k.region || '';
  if (p.tipo === 'arrastrar_soltar') M.etqs = Object.entries(k.asignaciones || {}).map(([t, r]) => ({ t, r }));
  M.construir = () => {
    const t = M.tipo;
    if (['seleccion_multiple', 'caso_clinico', 'cortes'].includes(t)) { const ops = M.ops.filter((o) => o.t.trim()); const c = ops.map((o, i) => (o.ok ? i : -1)).filter((i) => i >= 0); return { payload: { opciones: ops.map((o) => o.t.trim()), ...(c.length > 1 ? { multiple: true } : {}) }, clave: { correcta: c } }; }
    if (t === 'verdadero_falso_razonado') { const rs = M.razones.filter((o) => o.t.trim()); return { payload: { razones: rs.map((o) => o.t.trim()) }, clave: { valor: M.valor, razon: Math.max(0, rs.findIndex((o) => o.ok)) } }; }
    if (t === 'ordenar') { const ps = M.pasos.map((x) => x.trim()).filter(Boolean); return { payload: { elementos: [...ps].sort() }, clave: { orden: ps } }; }
    if (t === 'relacionar') { const ps = M.pares.filter(([a, b]) => a.trim() && b.trim()).map(([a, b]) => [a.trim(), b.trim()]); return { payload: { izquierda: ps.map((x) => x[0]).sort(), derecha: ps.map((x) => x[1]).sort() }, clave: { pares: Object.fromEntries(ps) } }; }
    if (t === 'respuesta_breve') { const ac = lineas(M.acept); return { payload: {}, clave: { aceptadas: ac, solucion: M.sol.trim() || ac[0] || '' } }; }
    if (t === 'identificacion_imagen') return { payload: {}, clave: { region: M.region } };
    if (t === 'arrastrar_soltar') { const es = M.etqs.filter((e) => e.t.trim()); return { payload: { etiquetas: es.map((e) => e.t.trim()).sort() }, clave: { asignaciones: Object.fromEntries(es.map((e) => [e.t.trim(), e.r])) } }; }
    return { payload: {}, clave: {} };
  };
  return M;
}

function editorTipo(M) {
  const box = $('#tipoBox'); const t = M.tipo;
  const filas = (arr, render, add) => `<div class="filas">${arr.map(render).join('')}</div><div><button type="button" class="btn-mini" data-add="${add}">Añadir</button></div>`;
  if (['seleccion_multiple', 'caso_clinico', 'cortes'].includes(t)) {
    box.innerHTML = `<h3>Opciones (marca la correcta; si marcas varias, el alumno deberá elegirlas todas)</h3>${filas(M.ops, (o, i) => `<div class="fila"><input type="checkbox" data-ok="${i}" ${o.ok ? 'checked' : ''} aria-label="Correcta"><input type="text" data-op="${i}" value="${esc(o.t)}" aria-label="Opción ${i + 1}"><button type="button" data-del="${i}">Quitar</button></div>`, 'op')}`;
    box.oninput = (e) => { if (e.target.dataset.op) M.ops[+e.target.dataset.op].t = e.target.value; if (e.target.dataset.ok) M.ops[+e.target.dataset.ok].ok = e.target.checked; };
    box.onclick = (e) => { if (e.target.dataset.add) { M.ops.push({ t: '', ok: false }); editorTipo(M); } if (e.target.dataset.del) { M.ops.splice(+e.target.dataset.del, 1); editorTipo(M); } };
  } else if (t === 'verdadero_falso_razonado') {
    box.innerHTML = `<h3>La afirmación es</h3><div class="row"><label class="inline"><input type="radio" name="vfv" value="1" ${M.valor ? 'checked' : ''}> Verdadera</label><label class="inline"><input type="radio" name="vfv" value="0" ${!M.valor ? 'checked' : ''}> Falsa</label></div>
      <h3>Razones (marca la correcta)</h3>${filas(M.razones, (o, i) => `<div class="fila"><input type="radio" name="vfr" data-ok="${i}" ${o.ok ? 'checked' : ''} aria-label="Razón correcta"><input type="text" data-op="${i}" value="${esc(o.t)}" aria-label="Razón ${i + 1}"><button type="button" data-del="${i}">Quitar</button></div>`, 'r')}`;
    box.oninput = (e) => { if (e.target.name === 'vfv') M.valor = e.target.value === '1'; if (e.target.dataset.op) M.razones[+e.target.dataset.op].t = e.target.value; if (e.target.dataset.ok) M.razones.forEach((o, i) => { o.ok = i === +e.target.dataset.ok; }); };
    box.onclick = (e) => { if (e.target.dataset.add) { M.razones.push({ t: '', ok: false }); editorTipo(M); } if (e.target.dataset.del) { M.razones.splice(+e.target.dataset.del, 1); editorTipo(M); } };
  } else if (t === 'ordenar') {
    box.innerHTML = `<h3>Elementos en el orden correcto (el alumno los verá desordenados)</h3>${filas(M.pasos, (x, i) => `<div class="fila"><span class="meta" style="width:1.4rem">${i + 1}</span><input type="text" data-op="${i}" value="${esc(x)}" aria-label="Paso ${i + 1}"><button type="button" data-up="${i}" ${i === 0 ? 'disabled' : ''} aria-label="Subir">↑</button><button type="button" data-del="${i}">Quitar</button></div>`, 'p')}`;
    box.oninput = (e) => { if (e.target.dataset.op) M.pasos[+e.target.dataset.op] = e.target.value; };
    box.onclick = (e) => { const d = e.target.dataset; if (d.add) M.pasos.push(''); else if (d.del) M.pasos.splice(+d.del, 1); else if (d.up) { const i = +d.up; [M.pasos[i - 1], M.pasos[i]] = [M.pasos[i], M.pasos[i - 1]]; } else return; editorTipo(M); };
  } else if (t === 'relacionar') {
    box.innerHTML = `<h3>Parejas correctas</h3>${filas(M.pares, ([a, b], i) => `<div class="fila"><input type="text" data-a="${i}" value="${esc(a)}" aria-label="Elemento ${i + 1}"><span class="meta">con</span><input type="text" data-b="${i}" value="${esc(b)}" aria-label="Pareja ${i + 1}"><button type="button" data-del="${i}">Quitar</button></div>`, 'pa')}`;
    box.oninput = (e) => { if (e.target.dataset.a) M.pares[+e.target.dataset.a][0] = e.target.value; if (e.target.dataset.b) M.pares[+e.target.dataset.b][1] = e.target.value; };
    box.onclick = (e) => { if (e.target.dataset.add) { M.pares.push(['', '']); editorTipo(M); } if (e.target.dataset.del) { M.pares.splice(+e.target.dataset.del, 1); editorTipo(M); } };
  } else if (t === 'respuesta_breve') {
    box.innerHTML = `<h3>Respuestas aceptadas</h3><p class="meta">Una por línea. No importan mayúsculas, tildes ni signos.</p><textarea data-acept style="min-height:90px">${esc(M.acept)}</textarea>
      <label>Respuesta que se muestra como solución<input type="text" data-sol value="${esc(M.sol)}"></label>`;
    box.oninput = (e) => { if ('acept' in e.target.dataset) M.acept = e.target.value; if ('sol' in e.target.dataset) M.sol = e.target.value; };
    box.onclick = null;
  } else if (t === 'identificacion_imagen' || t === 'arrastrar_soltar') {
    const fig = M.media ? figura(M.media) : null;
    box.innerHTML = `<h3>Imagen</h3><label>Imagen con zonas<select data-media>${opcMedia(M.media)}</select></label>
      ${fig ? `<div class="lab-fig" style="border:1px solid var(--border);border-radius:10px">${renderFigura(fig, { etiquetas: false })}</div>` : '<p class="meta">Elige una imagen. Las zonas se dibujan en «Imágenes y zonas».</p>'}
      ${fig && t === 'identificacion_imagen' ? `<p class="meta">Toca la zona correcta. Elegida: <strong>${esc((fig.regions.find((r) => r.id === M.region) || {}).nombre || 'ninguna')}</strong></p>` : ''}
      ${fig && t === 'arrastrar_soltar' ? `<h3>Etiquetas y su zona</h3>${filas(M.etqs, (e, i) => `<div class="fila"><input type="text" data-et="${i}" value="${esc(e.t)}" aria-label="Etiqueta ${i + 1}"><select data-er="${i}" aria-label="Zona de la etiqueta ${i + 1}"><option value="">Zona…</option>${fig.regions.map((r) => `<option value="${esc(r.id)}" ${r.id === e.r ? 'selected' : ''}>${esc(r.nombre)}</option>`).join('')}</select><button type="button" data-del="${i}">Quitar</button></div>`, 'e')}` : ''}`;
    const svg = box.querySelector('svg');
    if (svg && t === 'identificacion_imagen') svg.querySelectorAll('.reg').forEach((r) => r.classList.toggle('sel', r.dataset.region === M.region));
    box.oninput = (e) => { if (e.target.dataset.et) M.etqs[+e.target.dataset.et].t = e.target.value; };
    box.onchange = (e) => { if ('media' in e.target.dataset) { M.media = e.target.value || null; M.region = ''; M.etqs = [{ t: '', r: '' }]; editorTipo(M); } if (e.target.dataset.er) M.etqs[+e.target.dataset.er].r = e.target.value; };
    box.onclick = (e) => {
      const reg = e.target.closest && e.target.closest('.reg');
      if (reg && t === 'identificacion_imagen') { M.region = reg.dataset.region; editorTipo(M); return; }
      if (e.target.dataset.add) { M.etqs.push({ t: '', r: '' }); editorTipo(M); } if (e.target.dataset.del) { M.etqs.splice(+e.target.dataset.del, 1); editorTipo(M); }
    };
  }
}

// ---------- imágenes ----------
function vImagenes() {
  main().innerHTML = `<div class="c-wide"><h1 class="h-curso">Imágenes y zonas</h1>
    <p class="lead">Cada imagen necesita autor, fuente y una licencia que permita usarla. Las zonas se dibujan sobre la imagen y sirven para el atlas y para las preguntas de identificación.</p>
    <div class="scroll-x"><table class="adm-tabla"><thead><tr><th>Imagen</th><th>Zonas</th><th>Licencia</th><th>Estado</th></tr></thead><tbody>
    ${S.media.map((m) => `<tr><td><a href="#/imagen/${m.id}">${esc(m.titulo)}</a></td><td class="num">${S.regs.filter((r) => r.media_id === m.id).length}</td><td>${esc(LICENCIAS[m.licencia] || m.licencia)}</td><td>${estado(m.estado)}</td></tr>`).join('')}</tbody></table></div>
    <h2 class="h2">Subir una imagen</h2>
    <form class="form" id="fu">
      <label>Archivo (JPG, PNG o WebP; se convierte a WebP de 1600 px como máximo)<input type="file" name="archivo" accept="image/png,image/jpeg,image/webp" required></label>
      <div class="grid2"><label>Título<input type="text" name="titulo" required></label><label>Módulo<select name="module_id">${opcModulos(null)}</select></label></div>
      <label>Texto alternativo (qué muestra la imagen)<input type="text" name="alt" required minlength="10"></label>
      <div class="grid2"><label>Autor<input type="text" name="autor" required></label><label>Fuente<input type="text" name="fuente" required></label></div>
      <div class="grid2"><label>Enlace a la fuente<input type="url" name="fuente_url"></label><label>Licencia<select name="licencia" required>${Object.entries(LICENCIAS).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></label></div>
      <label>Cambios hechos sobre el original<input type="text" name="cambios"></label>
      <div id="prob"></div><div class="row"><button class="btn">Subir y dibujar zonas</button></div></form></div>`;
  $('#fu').addEventListener('submit', async (e) => {
    e.preventDefault(); const f = e.target; const btn = f.querySelector('button'); btn.disabled = true;
    try {
      const file = f.archivo.files[0]; if (!file) throw new Error('Elige un archivo');
      const { blob, w, h } = await aWebp(file);
      const slug = slugify(f.titulo.value) + '-' + Date.now().toString(36);
      const ruta = `${CURSO}/${slug}.webp`;
      const up = await sb.storage.from('course-media').upload(ruta, blob, { contentType: 'image/webp', upsert: false });
      if (up.error) throw new Error(up.error.message);
      const lic = LICENCIAS[f.licencia.value];
      const fila = await q(sb.from('course_media').insert({ course_id: S.curso.id, module_id: f.module_id.value || null, slug, titulo: f.titulo.value.trim(), alt: f.alt.value.trim(), tipo: 'imagen', storage_path: ruta, view_box: `0 0 ${w} ${h}`,
        autor: f.autor.value.trim(), fuente: f.fuente.value.trim(), fuente_url: f.fuente_url.value.trim() || null, licencia: f.licencia.value, cambios: f.cambios.value.trim() || null,
        credito: `${f.autor.value.trim()}, ${f.fuente.value.trim()} (${lic})${f.cambios.value.trim() ? '. ' + f.cambios.value.trim() : ''}.`, estado: 'borrador' }).select().single());
      S.media.push(fila); await firmar(); toast('Imagen subida'); location.hash = '#/imagen/' + fila.id;
    } catch (err) { $('#prob').innerHTML = `<div class="problemas">${esc(err.message)}</div>`; btn.disabled = false; }
  });
}
async function aWebp(file) {
  const bmp = await createImageBitmap(file); const k = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
  const w = Math.round(bmp.width * k), h = Math.round(bmp.height * k);
  const c = document.createElement('canvas'); c.width = w; c.height = h; c.getContext('2d').drawImage(bmp, 0, 0, w, h);
  const blob = await new Promise((r) => c.toBlob(r, 'image/webp', 0.86));
  if (!blob) throw new Error('El navegador no pudo convertir la imagen');
  return { blob, w, h };
}

function vImagen(id) {
  const m = S.media.find((x) => x.id === id); if (!m) { main().innerHTML = '<p class="problemas">La imagen no existe.</p>'; return; }
  let zonas = S.regs.filter((r) => r.media_id === id).map((r) => ({ ...r, coords: r.coords }));
  let actual = zonas[0] ? zonas[0].region_key : null; const borradas = new Set();
  const base = () => { const f = figura(m.id); return { ...f, regions: [], etiquetas: [] }; };
  const pinta = () => {
    const f = base(); const vb = String(m.view_box).split(/\s+/).map(Number); const r0 = Math.max(vb[2], vb[3]) / 160;
    const svg = renderFigura(f, { etiquetas: false }).replace('</svg>', zonas.map((z) => {
      const cls = `reg ${z.region_key === actual ? 'actual' : ''}`;
      if (z.forma === 'circle') return `<circle class="${cls}" data-k="${esc(z.region_key)}" cx="${z.coords.c[0]}" cy="${z.coords.c[1]}" r="${z.coords.r}"/>`;
      const pts = (z.coords || []).map((p) => p.join(',')).join(' ');
      return `<polygon class="${cls}" data-k="${esc(z.region_key)}" points="${pts}"/>` + (z.region_key === actual ? (z.coords || []).map((p) => `<circle class="punto" cx="${p[0]}" cy="${p[1]}" r="${r0}"/>`).join('') : '');
    }).join('') + '</svg>');
    const z = zonas.find((x) => x.region_key === actual);
    main().innerHTML = `<div class="c-wide"><h1 class="h3">${esc(m.titulo)} ${estado(m.estado)}</h1>
      <p class="meta">Elige o crea una zona y haz clic sobre la imagen para añadir sus vértices. Guarda al terminar.</p>
      <div class="editor-img"><div class="lienzo" id="lienzo">${svg}</div>
      <div class="form"><div class="caja"><h3>Zonas</h3><ul class="zonas">${zonas.map((x) => `<li><button type="button" data-z="${esc(x.region_key)}" aria-current="${x.region_key === actual}">${esc(x.nombre || x.region_key)} <span class="meta">(${x.forma === 'circle' ? 'círculo' : (x.coords || []).length + ' puntos'})</span></button></li>`).join('')}</ul>
        <div class="row"><button type="button" class="btn-mini" id="zNueva">Nueva zona</button>${z ? '<button type="button" class="btn-mini" id="zDeshacer">Quitar último punto</button><button type="button" class="btn-mini" id="zVaciar">Borrar puntos</button><button type="button" class="btn-mini" id="zEliminar">Eliminar zona</button>' : ''}</div></div>
      ${z ? `<div class="caja"><h3>Zona seleccionada</h3>
        <label>Clave (minúsculas y guiones bajos)<input type="text" id="zk" value="${esc(z.region_key)}"></label>
        <label>Nombre<input type="text" id="zn" value="${esc(z.nombre || '')}"></label>
        <label>Término latino<input type="text" id="zl" value="${esc(z.latin || '')}"></label>
        <label>Qué es y qué hace<textarea id="zi">${esc(z.info || '')}</textarea></label></div>` : ''}
      <div id="prob"></div>
      <div class="row"><button class="btn" id="zGuardar" type="button">Guardar zonas</button>
        ${m.estado !== 'publicado' ? '<button class="btn sec" id="mPub" type="button">Publicar imagen</button>' : ''}<a class="btn sec" href="#/imagenes">Volver</a></div>
      <p class="meta">${esc(m.credito)}</p></div></div></div>`;
    const svgEl = $('#lienzo svg');
    svgEl.addEventListener('click', (e) => {
      const zz = zonas.find((x) => x.region_key === actual);
      const hit = e.target.closest('[data-k]');
      if (hit && hit.dataset.k !== actual) { guardaCampos(); actual = hit.dataset.k; pinta(); return; }
      if (!zz || zz.forma === 'circle') return;
      const pt = svgEl.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; const p = pt.matrixTransform(svgEl.getScreenCTM().inverse());
      guardaCampos(); zz.coords = [...(zz.coords || []), [Math.round(p.x * 10) / 10, Math.round(p.y * 10) / 10]]; pinta();
    });
    main().querySelectorAll('[data-z]').forEach((b) => b.addEventListener('click', () => { guardaCampos(); actual = b.dataset.z; pinta(); }));
    $('#zNueva').addEventListener('click', () => { guardaCampos(); let n = zonas.length + 1; while (zonas.some((x) => x.region_key === 'zona_' + n)) n++; zonas.push({ region_key: 'zona_' + n, nombre: '', forma: 'poly', coords: [], orden: zonas.length }); actual = 'zona_' + n; pinta(); });
    const zz = zonas.find((x) => x.region_key === actual);
    if (zz) {
      $('#zDeshacer').addEventListener('click', () => { guardaCampos(); zz.coords = (zz.coords || []).slice(0, -1); pinta(); });
      $('#zVaciar').addEventListener('click', () => { guardaCampos(); zz.coords = []; pinta(); });
      $('#zEliminar').addEventListener('click', () => { if (zz.id) borradas.add(zz.id); zonas = zonas.filter((x) => x !== zz); actual = zonas[0] ? zonas[0].region_key : null; pinta(); });
    }
    $('#zGuardar').addEventListener('click', guardar);
    const pub = $('#mPub'); if (pub) pub.addEventListener('click', async () => { try { await q(sb.from('course_media').update({ estado: 'publicado' }).eq('id', m.id)); m.estado = 'publicado'; toast('Imagen publicada'); pinta(); } catch (err) { $('#prob').innerHTML = `<div class="problemas">${esc(err.message)}</div>`; } });
  };
  const guardaCampos = () => {
    const z = zonas.find((x) => x.region_key === actual); if (!z || !$('#zk')) return;
    const k = $('#zk').value.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
    z.nombre = $('#zn').value.trim(); z.latin = $('#zl').value.trim(); z.info = $('#zi').value.trim();
    if (k && k !== z.region_key && !zonas.some((x) => x.region_key === k)) { z.region_key = k; actual = k; }
  };
  const guardar = async () => {
    guardaCampos();
    const mal = zonas.filter((z) => !z.nombre || (z.forma !== 'circle' && (z.coords || []).length < 3));
    if (mal.length) { $('#prob').innerHTML = `<div class="problemas">Cada zona necesita nombre y al menos tres puntos: ${mal.map((z) => esc(z.region_key)).join(', ')}.</div>`; return; }
    try {
      if (borradas.size) await q(sb.from('course_media_regions').delete().in('id', [...borradas]));
      const filas = zonas.map((z, i) => ({ ...(z.id ? { id: z.id } : {}), media_id: m.id, region_key: z.region_key, nombre: z.nombre, latin: z.latin || null, info: z.info || null, forma: z.forma, coords: z.coords, coords_espejo: z.coords_espejo || null, orden: i }));
      const res = filas.length ? await q(sb.from('course_media_regions').upsert(filas, { onConflict: 'media_id,region_key' }).select()) : [];
      S.regs = S.regs.filter((r) => r.media_id !== m.id).concat(res); borradas.clear();
      zonas = res.map((r) => ({ ...r })); toast('Zonas guardadas'); pinta();
    } catch (err) { $('#prob').innerHTML = `<div class="problemas">${esc(err.message)}</div>`; }
  };
  pinta();
}

// ---------- lecciones ----------
function vLecciones() {
  main().innerHTML = `<div class="c-wide"><h1 class="h-curso">Lecciones</h1>${S.mods.map((m) => `<h2 class="h3">${m.orden}. ${esc(m.titulo)}</h2>
    <table class="adm-tabla"><tbody>${S.lecs.filter((l) => l.module_id === m.id).map((l) => `<tr><td><a href="#/leccion/${l.id}">${l.orden}. ${esc(l.titulo)}</a></td><td>${(l.bloques || []).length ? 'Con texto' : '<span class="meta">Solo guion</span>'}</td><td>${estado(l.estado)}</td></tr>`).join('')}</tbody></table>`).join('')}</div>`;
}
function vLeccion(id) {
  const l = S.lecs.find((x) => x.id === id); if (!l) { main().innerHTML = '<p class="problemas">La lección no existe.</p>'; return; }
  const figuraPorSlug = (s) => figura(s);
  main().innerHTML = `<div class="dos-col"><form class="form" id="fl">
    <h1 class="h3" style="margin:0">${esc(l.titulo)} ${estado(l.estado)}</h1>
    <div class="grid2"><label>Título<input type="text" name="titulo" value="${esc(l.titulo)}"></label><label>Minutos<input type="number" name="minutos" min="1" max="120" value="${l.minutos || 10}"></label></div>
    <div class="grid2"><label>Origen<select name="origen">${[['clase', 'Material de clase'], ['ampliado', 'Ampliado con bibliografía'], ['mixto', 'Clase y bibliografía']].map(([k, v]) => `<option value="${k}" ${k === l.origen ? 'selected' : ''}>${v}</option>`).join('')}</select></label>
      <label>Estado<select name="estado">${['borrador', 'publicado', 'archivado'].map((x) => `<option ${x === l.estado ? 'selected' : ''}>${x}</option>`).join('')}</select></label></div>
    <label>Objetivos (uno por línea)<textarea name="objetivos">${esc((l.objetivos || []).join('\n'))}</textarea></label>
    <label>Lo esencial (uno por línea; **negrita** permitida)<textarea name="lo_esencial">${esc((l.lo_esencial || []).join('\n'))}</textarea></label>
    <label>Contenido<textarea class="codigo" name="contenido" spellcheck="true">${esc(bloquesATexto(l.bloques || []))}</textarea></label>
    <p class="meta">## Sección · párrafos separados por una línea en blanco · - lista · | tabla | · &gt; correlación clínica · [figura: ${esc(S.media[0] ? S.media[0].slug : 'slug-de-la-imagen')}]</p>
    <label>Correlación clínica del guion<textarea name="correlacion_clinica">${esc(l.correlacion_clinica || '')}</textarea></label>
    <label>Fuentes (una por línea)<textarea name="fuentes">${esc((l.fuentes || []).join('\n'))}</textarea></label>
    <div id="prob"></div><div class="row"><button class="btn">Guardar</button><a class="btn sec" href="#/lecciones">Volver</a></div></form>
    <div><h2 class="h3" style="margin-top:0">Vista previa</h2><div class="vista prose" id="vista"></div></div></div>`;
  const fl = $('#fl');
  const preview = () => {
    $('#vista').innerHTML = `<div class="esencial"><h3>Lo esencial</h3><ul>${lineas(fl.lo_esencial.value).map((x) => `<li>${esc(x).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}</li>`).join('')}</ul></div>` + bloquesHTML(textoABloques(fl.contenido.value), figuraPorSlug);
    $('#vista').querySelectorAll('[data-fig]').forEach((el) => bindFigura(el, figura(el.dataset.fig), { modo: 'explorar' }));
  };
  let tmr; fl.addEventListener('input', () => { clearTimeout(tmr); tmr = setTimeout(preview, 300); }); preview();
  fl.addEventListener('submit', async (e) => {
    e.preventDefault();
    const bloques = textoABloques(fl.contenido.value);
    const faltan = bloques.filter((b) => b.t === 'figura' && !figura(b.id)).map((b) => b.id);
    if (faltan.length) { $('#prob').innerHTML = `<div class="problemas">No existe la imagen: ${faltan.map(esc).join(', ')}.</div>`; return; }
    const cambios = { titulo: fl.titulo.value.trim(), minutos: +fl.minutos.value || null, origen: fl.origen.value, estado: fl.estado.value, objetivos: lineas(fl.objetivos.value),
      lo_esencial: lineas(fl.lo_esencial.value), bloques, secciones: bloques.filter((b) => b.t === 'h').map((b) => b.texto), correlacion_clinica: fl.correlacion_clinica.value.trim() || null, fuentes: lineas(fl.fuentes.value) };
    if (!cambios.secciones.length) delete cambios.secciones;
    try { const r = await q(sb.from('course_lessons').update(cambios).eq('id', l.id).select().single()); Object.assign(l, r); toast('Lección guardada'); $('#prob').innerHTML = ''; }
    catch (err) { $('#prob').innerHTML = `<div class="problemas">${esc(err.message)}</div>`; }
  });
}

// ---------- router y arranque ----------
function route() {
  const [ruta, qs] = location.hash.replace(/^#\/?/, '').split('?');
  const [a, b] = ruta.split('/');
  rail(a === 'pregunta' && b === 'nueva' ? 'pregunta/nueva' : a);
  $('#rail').classList.remove('abierto');
  if (!a) vResumen();
  else if (a === 'preguntas') vPreguntas(new URLSearchParams(qs || ''));
  else if (a === 'pregunta' && b) vPregunta(b);
  else if (a === 'imagenes') vImagenes();
  else if (a === 'imagen' && b) vImagen(b);
  else if (a === 'lecciones') vLecciones();
  else if (a === 'leccion' && b) vLeccion(b);
  else vResumen();
  window.scrollTo(0, 0);
}

async function init() {
  let tema = null; try { tema = localStorage.getItem('aurzane-tema'); } catch (e) {}
  if (tema === 'oscuro') document.documentElement.dataset.tema = 'oscuro';
  $('#btnTema').addEventListener('click', () => { const o = document.documentElement.dataset.tema === 'oscuro'; if (o) delete document.documentElement.dataset.tema; else document.documentElement.dataset.tema = 'oscuro'; try { localStorage.setItem('aurzane-tema', o ? 'claro' : 'oscuro'); } catch (e) {} });
  try {
    sb = window.crearClienteAurzaneID(SUPABASE_URL, SUPABASE_KEY); window.__aurzaneSb = sb;
    const { data: { session } } = await sb.auth.getSession();
    if (!session) { main().innerHTML = `<div class="c-col"><h1 class="h-curso">Inicia sesión</h1><p class="lead">El panel de cursos usa tu cuenta de AURZANE ID.</p><a class="btn" href="https://aurzane.com/mi-aurzane.html?next=${encodeURIComponent(location.href)}">Iniciar sesión</a></div>`; return; }
    S.caps = (await q(sb.rpc('mis_capacidades'))) || [];
    if (!S.caps.includes('courses.write')) { main().innerHTML = '<div class="c-col"><h1 class="h-curso">Sin acceso</h1><p class="lead">Tu cuenta no tiene permiso para editar cursos. Pide al administrador el permiso de editor de cursos.</p></div>'; return; }
    await cargar();
  } catch (e) { main().innerHTML = `<div class="c-col"><h1 class="h-curso">No se pudo abrir el panel</h1><p class="lead">${esc(e.message)}</p></div>`; return; }
  window.addEventListener('hashchange', route);
  route();
}
init();
