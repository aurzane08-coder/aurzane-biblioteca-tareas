// Capa de datos en Supabase (producción). Misma interfaz que data-local.js.
// Lee solo contenido publicado gracias a RLS y corrige siempre en el servidor
// (course_check_answer, course_submit_answer, course_finish_attempt): las
// soluciones no se descargan nunca antes de responder.
import { textoSolucion } from './data-local.js?v=f15';

const PAGE = 1000;
async function todas(q) {
  const out = [];
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await q().range(from, from + PAGE - 1);
    if (error) throw error;
    out.push(...data);
    if (data.length < PAGE) return out;
  }
}
const rpc = async (sb, fn, args) => { const { data, error } = await sb.rpc(fn, args); if (error) throw new Error(error.message); return data; };

export async function createSupabaseData(sb, slug) {
  const { data: curso, error } = await sb.from('course_courses').select('*').eq('slug', slug).maybeSingle();
  if (error) throw error;
  if (!curso) return null; // no publicado o sin permiso
  const modulos = await todas(() => sb.from('course_modules').select('*').eq('course_id', curso.id).order('orden'));
  const modIds = modulos.map((m) => m.id);
  const [lecciones, media, regiones, preguntas] = await Promise.all([
    todas(() => sb.from('course_lessons').select('id,module_id,orden,slug,titulo,minutos,objetivos,secciones,lo_esencial,bloques,figuras_previstas,correlacion_clinica,origen,fuentes').in('module_id', modIds.length ? modIds : ['00000000-0000-0000-0000-000000000000']).order('orden')),
    todas(() => sb.from('course_media').select('*').eq('course_id', curso.id).neq('estado', 'archivado')),
    todas(() => sb.from('course_media_regions').select('*').order('orden')),
    todas(() => sb.from('course_questions').select('id,module_id,lesson_id,tipo,enunciado,caso,payload,media_id,dificultad').eq('course_id', curso.id).order('id')),
  ]);

  const modSlug = new Map(modulos.map((m) => [m.id, m.slug]));
  const lecPorId = new Map(lecciones.map((l) => [l.id, l]));
  const mediaSlug = new Map(media.map((m) => [m.id, m.slug]));

  // misma forma que curriculum.json, para que las vistas no cambien
  const C = {
    course: { slug: curso.slug, titulo: curso.titulo, subtitulo: curso.subtitulo, descripcion: curso.descripcion, nivel: curso.nivel,
      horas_estimadas: Number(curso.horas_estimadas || 0), objetivos_generales: curso.objetivos || [], nota_fuentes: curso.nota_fuentes || '' },
    modules: modulos.map((m) => ({
      id: m.id, orden: m.orden, slug: m.slug, titulo: m.titulo, descripcion: m.descripcion, objetivos: m.objetivos, requisitos: m.requisitos,
      relacion: m.relacion, tiempo_min: m.tiempo_min, recursos: m.recursos || {}, conceptos_clave: m.conceptos_clave, terminologia: m.terminologia, confusiones: m.confusiones,
      lecciones: lecciones.filter((l) => l.module_id === m.id).map((l) => ({ id: l.id, orden: l.orden, slug: l.slug, titulo: l.titulo, minutos: l.minutos,
        objetivos: l.objetivos, secciones: l.secciones, lo_esencial: l.lo_esencial, figuras: l.figuras_previstas, correlacion_clinica: l.correlacion_clinica, origen: l.origen })),
    })),
  };
  const cuerpos = {};
  lecciones.forEach((l) => { if (l.bloques && l.bloques.length) cuerpos[`${modSlug.get(l.module_id)}/${l.slug}`] = { bloques: l.bloques, fuentes: l.fuentes }; });

  // imágenes subidas: enlaces firmados del bucket privado (6 horas)
  const rutas = media.filter((m) => m.tipo === 'imagen' && m.storage_path).map((m) => m.storage_path);
  const firmadas = new Map();
  if (rutas.length) {
    const { data: urls, error: e2 } = await sb.storage.from('course-media').createSignedUrls(rutas, 21600);
    if (!e2) (urls || []).forEach((u) => { if (u.signedUrl) firmadas.set(u.path, u.signedUrl); });
  }
  const tam = (vb) => { const p = String(vb || '0 0 100 100').split(/\s+/).map(Number); return { w: p[2], h: p[3] }; };
  const figuras = new Map(media.map((m) => [m.slug, {
    id: m.slug, titulo: m.titulo, modulo: modSlug.get(m.module_id), viewBox: m.view_box, dibujo: m.dibujo, etiquetas: m.etiquetas, credito: m.credito, alt: m.alt,
    imagen: m.tipo === 'imagen' ? { url: firmadas.get(m.storage_path) || '', ...tam(m.view_box) } : null,
    regions: regiones.filter((r) => r.media_id === m.id).map((r) => ({ id: r.region_key, nombre: r.nombre, latin: r.latin, info: r.info, shape: r.forma,
      ...(r.forma === 'circle' ? { c: r.coords.c, r: r.coords.r } : { pts: r.coords }), ...(r.coords_espejo ? { pts2: r.coords_espejo } : {}) })),
  }]));

  const items = new Map(preguntas.map((q) => {
    const p = q.payload || {};
    const lec = q.lesson_id ? lecPorId.get(q.lesson_id) : null;
    return [q.id, {
      id: q.id, modulo: modSlug.get(q.module_id) || null, leccion: lec ? lec.slug : null, tipo: q.tipo, enunciado: q.enunciado, caso: q.caso,
      figura: q.media_id ? mediaSlug.get(q.media_id) : (p.figura || null),
      opciones: p.opciones, multiple: !!p.multiple, razones: p.razones, elementos: p.elementos, izquierda: p.izquierda, derecha: p.derecha, etiquetas: p.etiquetas, imagen: p.imagen || null,
    }];
  }));
  const conDetalle = (it, r) => r; // el servidor ya devuelve {correcta, solucion, explicacion}

  return {
    modo: 'supabase',
    cursoId: curso.id,
    curso: () => C,
    item: (id) => items.get(id),
    itemsDeModulo: (slug) => [...items.values()].filter((i) => i.modulo === slug),
    todosLosItems: () => [...items.values()].filter((i) => i.modulo),
    leccion: (m, l) => cuerpos[`${m}/${l}`] || null,
    todasLecciones: () => cuerpos,
    leccionId: (m, l) => { const mm = C.modules.find((x) => x.slug === m); const ll = mm && mm.lecciones.find((x) => x.slug === l); return ll ? ll.id : null; },
    moduloSlug: (id) => modSlug.get(id),
    figura: (id) => figuras.get(id),
    figuras: () => [...figuras.values()],
    solucionTexto: (item, sol) => textoSolucion(item, sol, figuras.get(item.figura)),

    // registrar = false: reintento dentro de la misma sesión, no mueve el calendario de repaso
    async comprobar(item, resp, registrar = true) { return conDetalle(item, await rpc(sb, 'course_check_answer', { p_question: item.id, p_respuesta: resp, p_registrar: registrar })); },
    async iniciarIntento({ modulo = null, modo, mostrar, n, reanudar = true }) {
      const r = await rpc(sb, 'course_start_attempt', { p_course: slug, p_module: modulo, p_modo: modo || 'practica', p_mostrar: mostrar || 'al_responder', p_n: n || 20, p_reanudar: reanudar });
      return { id: r.attempt_id, items: r.question_ids, modo: r.modo, mostrar: r.mostrar_solucion, reanudado: r.reanudado, respondidas: r.respondidas, ronda: r.ronda || 1, raiz: r.raiz || r.attempt_id };
    },
    // ronda nueva solo con las falladas de un intento terminado (hasta cerrar el test al 100 %)
    async reintentar(intento) {
      const r = await rpc(sb, 'course_retry_attempt', { p_attempt: intento.id });
      return { id: r.attempt_id, items: r.question_ids, modo: r.modo, mostrar: r.mostrar_solucion, reanudado: false, respondidas: [], ronda: r.ronda, raiz: r.raiz };
    },
    async responder(intento, item, resp) { return rpc(sb, 'course_submit_answer', { p_attempt: intento.id, p_question: item.id, p_respuesta: resp }); },
    async terminarIntento(intento) { const r = await rpc(sb, 'course_finish_attempt', { p_attempt: intento.id }); return { ...r, nota: Number(r.nota), cerrado: !!r.cerrado, ronda: r.ronda || 1 }; },
  };
}
