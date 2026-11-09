// AURZANE LEARN · Cursos (fase 3: prototipo funcional sobre datos locales)
// La capa de datos (DATA) y el almacén de progreso (STORE) están aislados para
// cambiarlos en la fase 5 por Supabase (lectura por RLS y corrección por RPC)
// sin tocar las vistas ni el motor de preguntas.
import { mountItem, renderFigura, bindFigura, refHTML } from './engine.js?v=f15';
import { createLocalData } from './data-local.js?v=f15';
import { esc, md, labHTML, bloquesHTML, activarMedios } from './contenido.js?v=f15';
import { createLocalStore } from './store-local.js?v=f15';
import { mapaHTML, bindMapa, esquemaHTML, bindEsquema, tablasHTML, bindTablas, resumenTarjetas, nivelTarjeta, calificar, colaTarjetas, evaluarFeynman, BLOQUES, refLink } from './estudio.js?v=f15';

// Varios cursos con la misma aplicación: cursos.html?c=<slug>
const CURSOS = {
  'neuroanatomia-funcional': { portada: 'cursos/portada-neuro.webp', programa: 'Del desarrollo y la médula a la corteza y las grandes vías. Abre un tema para ver sus lecciones; la línea se rellena a medida que avanzas.', apuntes: 'neuroanatomia' },
  'tecnicas-neurociencias': { portada: 'cursos/portada-metodologia.webp', programa: 'De la estereotaxia y la terapia celular a la electrofisiología, la neurofarmacología y las técnicas morfológicas. Abre un tema para ver sus lecciones; la línea se rellena a medida que avanzas.', apuntes: 'metodologia' },
};
// direcciones antiguas de los cursos
const ALIAS = { 'neuro-300260': 'neuroanatomia-funcional', 'metod-300263': 'tecnicas-neurociencias' };
const CURSO = (() => { const c0 = new URLSearchParams(location.search).get('c') || document.documentElement.dataset.curso; const c = ALIAS[c0] || c0; return CURSOS[c] ? c : 'neuroanatomia-funcional'; })();
const CFG = CURSOS[CURSO];
document.documentElement.style.setProperty('--portada', `url(${CFG.portada})`);
const $ = (s, el = document) => el.querySelector(s);
const shuffle = (a) => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const ESTADO_TXT = { nuevo: 'Sin empezar', visitado: 'Visitado', completado: 'Completado', dominado: 'Cerrado al 100 %' };
const TIPO_TXT = {
  seleccion_multiple: 'Selección múltiple', identificacion_imagen: 'Identificación en imagen', arrastrar_soltar: 'Colocar etiquetas',
  relacionar: 'Relacionar', ordenar: 'Ordenar', verdadero_falso_razonado: 'Verdadero o falso razonado', respuesta_breve: 'Respuesta breve',
  caso_clinico: 'Caso clínico', cortes: 'Cortes e imagen',
};

let DATA, STORE, C; let AVISO = '';
const main = () => $('#main');

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.hidden = false;
  clearTimeout(toast.h); toast.h = setTimeout(() => { t.hidden = true; }, 2400);
}

// ---------- tema (mismo almacén que el resto de AURZANE) ----------
function initTema() {
  let tema = null; try { tema = localStorage.getItem('aurzane-tema'); } catch (e) {}
  if (tema === 'oscuro') document.documentElement.dataset.tema = 'oscuro';
  $('#btnTema').addEventListener('click', () => {
    const osc = document.documentElement.dataset.tema === 'oscuro';
    if (osc) delete document.documentElement.dataset.tema; else document.documentElement.dataset.tema = 'oscuro';
    try { localStorage.setItem('aurzane-tema', osc ? 'claro' : 'oscuro'); } catch (e) {}
  });
}

// ---------- estado derivado ----------
function estadoModulo(m) {
  const p = STORE.get();
  const lecs = m.lecciones.map((l) => p.lecciones[`${m.slug}/${l.slug}`] || {});
  const visit = lecs.some((x) => x.visita);
  const done = lecs.length && lecs.every((x) => x.completada);
  const intentado = STORE.intentos(m.slug).length > 0;
  // un tema solo se da por cerrado cuando su test completo se ha cerrado al 100 %
  if (done && STORE.cierreTema(m.slug, DATA).cerrado) return 'dominado';
  if (done && intentado) return 'completado';
  if (visit || intentado) return 'visitado';
  return 'nuevo';
}
// texto corto del estado del test de un tema (o de la final, clave 'final')
function estadoTest(clave) {
  const c = STORE.cierreTema(clave, DATA);
  if (c.cerrado) return `Cerrado al 100 % (${new Date(c.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })})`;
  const ch = STORE.cadenaAbierta(clave);
  if (ch) return `Te ${ch.pendientes === 1 ? 'queda 1 pregunta' : `quedan ${ch.pendientes} preguntas`} por acertar`;
  if (STORE.resumenAbierto(clave)) return 'Ronda sin terminar';
  return STORE.intentos(clave).length ? 'Sin cerrar' : 'Sin empezar';
}
function progresoCurso() {
  const p = STORE.get(); let tot = 0, ok = 0;
  C.modules.forEach((m) => m.lecciones.forEach((l) => { tot++; if ((p.lecciones[`${m.slug}/${l.slug}`] || {}).completada) ok++; }));
  return tot ? ok / tot : 0;
}
const modBySlug = (s) => C.modules.find((m) => m.slug === s);
// imágenes reales del módulo (para portadas): las primeras de cada lección
function fotosModulo(m, n = 3) {
  const out = [];
  for (let ronda = 0; out.length < n && ronda < 4; ronda++) {
    for (const l of m.lecciones) {
      const fs = ((DATA.leccion(m.slug, l.slug) || {}).bloques || []).filter((b) => b.t === 'imagen');
      if (fs[ronda] && !out.some((x) => x.src === fs[ronda].src)) out.push(fs[ronda]);
      if (out.length >= n) break;
    }
  }
  return out;
}
const srcSeguro = (s) => String(s || '').replace(/[^\w./-]/g, '');

// ---------- recursos de estudio y sesión por bloques ----------
const rec = (m) => (m && m.recursos) || {};
const lecHecha = (m, l) => !!(STORE.get().lecciones[`${m.slug}/${l.slug}`] || {}).completada;
function progresoModulo(m) { const ok = m.lecciones.filter((l) => lecHecha(m, l)).length; return { ok, tot: m.lecciones.length }; }
const estTarjetas = (m) => resumenTarjetas(rec(m).tarjetas || [], STORE.estudio(m.slug, 'tarjeta'));
const preguntasHoy = (m) => STORE.pendientesRepaso().filter((id) => (DATA.item(id) || {}).modulo === m.slug).length;
const tarjetasHoyCurso = () => C.modules.reduce((a, m) => a + estTarjetas(m).hoy, 0);
// marca, una sola vez, que el alumno ha abierto un recurso de organización visual
function marcarSesion(m, clave) {
  if (STORE.estudio(m.slug, 'sesion')[clave]) return;
  STORE.guardarEstudio(m.slug, 'sesion', clave, { visto: true }).then(() => renderRail(['m', m.slug, clave])).catch(() => {});
}
// los cinco pasos del método por bloques, con su estado calculado a partir del progreso real
function pasosSesion(m) {
  const r = rec(m); const ses = STORE.estudio(m.slug, 'sesion');
  const p = progresoModulo(m); const tj = estTarjetas(m);
  const fey = Object.keys(STORE.estudio(m.slug, 'feynman')).length; const nFey = (r.feynman || []).length;
  const visuales = [['mapa', 'mapa conceptual'], ['esquema', 'esquema'], ['tablas', 'tablas']].filter(([k]) => k !== 'tablas' || (r.tablas || []).length);
  const vistos = visuales.filter(([k]) => ses[k]).length;
  const cierre = STORE.cierreTema(m.slug, DATA);
  const hoy = preguntasHoy(m) + tj.hoy;
  const sigLec = m.lecciones.find((l) => !lecHecha(m, l)) || m.lecciones[0];
  const pasos = [
    { hecho: p.ok === p.tot, detalle: `${p.ok} de ${p.tot} lecciones completadas`, href: `#/m/${m.slug}/l/${sigLec.slug}`, cta: p.ok ? 'Seguir leyendo' : 'Empezar a leer' },
    { hecho: vistos === visuales.length, detalle: `${vistos} de ${visuales.length} recursos abiertos`, href: `#/m/${m.slug}/${(visuales.find(([k]) => !ses[k]) || visuales[0])[0]}`, cta: 'Organizar el tema' },
    { hecho: tj.total > 0 && tj.nuevas === 0 && fey > 0, detalle: `${tj.total - tj.nuevas} de ${tj.total} tarjetas vistas · ${fey} de ${nFey} explicaciones`, href: `#/m/${m.slug}/${tj.nuevas || !nFey ? 'tarjetas' : 'feynman'}`, cta: tj.nuevas || !nFey ? 'Practicar con tarjetas' : 'Explicar con tus palabras' },
    { hecho: cierre.cerrado, detalle: estadoTest(m.slug), href: `#/m/${m.slug}/evaluacion`, cta: 'Hacer el test' },
    { hecho: cierre.cerrado && hoy === 0, detalle: cierre.cerrado ? (hoy ? `${hoy} ${hoy === 1 ? 'pendiente' : 'pendientes'} hoy` : 'Al día') : 'Empieza al cerrar el test', href: tj.hoy ? `#/m/${m.slug}/tarjetas` : '#/repaso', cta: 'Repasar' },
  ];
  return BLOQUES.map((b, i) => ({ ...b, ...pasos[i] }));
}
function sesionHTML(m) {
  const pasos = pasosSesion(m); const actual = pasos.findIndex((x) => !x.hecho);
  return `<ol class="sesion" aria-label="Sesión de estudio por bloques">${pasos.map((x, i) => `<li class="${x.hecho ? 'hecho' : i === actual ? 'actual' : ''}">
    <span class="sesion-n" aria-hidden="true">${x.hecho ? '✓' : i + 1}</span>
    <div><strong>${esc(x.titulo)}</strong><p>${esc(x.texto)}</p><span class="meta">${esc(x.detalle)}</span>
    ${i === actual ? `<div><a class="btn peq" href="${x.href}">${esc(x.cta)}</a></div>` : ''}</div></li>`).join('')}</ol>`;
}
// pestañas comunes a las páginas de un tema
function tabsTema(m, actual) {
  const r = rec(m); const tj = estTarjetas(m);
  const tabs = [['', 'El tema'], ['mapa', 'Mapa conceptual'], ['esquema', 'Esquema'], (r.tablas || []).length ? ['tablas', 'Tablas'] : null,
    ['tarjetas', 'Tarjetas', tj.hoy], ['feynman', 'Feynman'], ['evaluacion', 'Test']].filter(Boolean);
  return `<nav class="tabs-tema" aria-label="Secciones del tema">${tabs.map(([k, t, n]) => `<a href="#/m/${m.slug}${k ? '/' + k : ''}" ${k === actual ? 'aria-current="page"' : ''}>${t}${n ? `<span class="badge">${n}</span>` : ''}</a>`).join('')}</nav>`;
}
function cabTema(m, actual, titulo) {
  return `${crumbs([['#/', 'Inicio'], [`#/m/${m.slug}`, `Tema ${m.orden}`], [null, titulo]])}
    <p class="tema-sup">Tema ${m.orden} · ${esc(m.titulo)}</p><h1 class="h-curso">${esc(titulo)}</h1>${tabsTema(m, actual)}`;
}

// ---------- marco ----------
function renderRail(ruta) {
  const pend = STORE.pendientesRepaso().length + tarjetasHoyCurso();
  const m = ruta[0] === 'm' ? modBySlug(ruta[1]) : null;
  if (m) return renderRailTema(m, ruta);
  const items = [
    ['#/', 'Inicio'], ['#/programa', 'Programa'], ['#/evaluaciones', 'Evaluaciones'],
    ['#/repaso', 'Repaso', pend], ['#/apuntes', 'Mis apuntes'], ['#/progreso', 'Progreso'], ['#/bibliografia', 'Bibliografía y créditos'], ['#/ayuda', 'Ayuda'],
  ];
  const actual = '#/' + (ruta[0] || '');
  $('#rail').innerHTML = `
    <nav aria-label="Curso">${items.map(([h, t, n]) => `<a href="${h}" ${h === actual ? 'aria-current="page"' : ''}>${t}${n ? `<span class="badge" aria-label="${n} pendientes">${n}</span>` : ''}</a>`).join('')}</nav>
    <h5>Temas</h5>
    <nav class="mods" aria-label="Temas">${C.modules.map((x) => `<a href="#/m/${x.slug}" style="--t:${colorTema(x)}"><span class="dot ${estadoModulo(x)}" aria-hidden="true"></span>${x.orden}. ${esc(x.titulo)}</a>`).join('')}</nav>`;
}
// dentro de un tema el menú lateral es su índice: lecciones, recursos y test, con su estado
function renderRailTema(m, ruta) {
  const [, , c, d] = ruta; const p = progresoModulo(m); const r = rec(m); const tj = estTarjetas(m);
  const ses = STORE.estudio(m.slug, 'sesion'); const fey = STORE.estudio(m.slug, 'feynman');
  const cierre = STORE.cierreTema(m.slug, DATA);
  const fila = (href, txt, hecho, actual, extra = '') => `<a href="${href}" ${actual ? 'aria-current="page"' : ''}><span class="chk${hecho ? ' si' : ''}" aria-label="${hecho ? 'Hecho' : 'Pendiente'}"></span><span class="txt">${txt}</span>${extra}</a>`;
  $('#rail').innerHTML = `
    <a class="rail-volver" href="#/">Todo el curso</a>
    <a class="rail-tema" href="#/m/${m.slug}" ${!c ? 'aria-current="page"' : ''}><span class="meta">Tema ${m.orden}</span><strong>${esc(m.titulo)}</strong>
      <span class="rail-barra" aria-hidden="true"><span style="width:${p.tot ? 100 * p.ok / p.tot : 0}%"></span></span><span class="meta">${p.ok} de ${p.tot} lecciones · ${ESTADO_TXT[estadoModulo(m)].toLowerCase()}</span></a>
    <h5>Lecciones</h5>
    <nav class="outline" aria-label="Lecciones del tema">${m.lecciones.map((l) => fila(`#/m/${m.slug}/l/${l.slug}`, `${esc(l.titulo)}<small>${l.minutos} min</small>`, lecHecha(m, l), c === 'l' && d === l.slug)).join('')}</nav>
    <h5>Organiza y practica</h5>
    <nav class="outline" aria-label="Recursos de estudio">
      ${fila(`#/m/${m.slug}/mapa`, 'Mapa conceptual', !!ses.mapa, c === 'mapa')}
      ${fila(`#/m/${m.slug}/esquema`, 'Esquema jerárquico', !!ses.esquema, c === 'esquema')}
      ${(r.tablas || []).length ? fila(`#/m/${m.slug}/tablas`, 'Tablas comparativas', !!ses.tablas, c === 'tablas') : ''}
      ${fila(`#/m/${m.slug}/tarjetas`, `Tarjetas<small>${tj.dominadas} de ${tj.total} dominadas</small>`, tj.total > 0 && tj.nuevas === 0, c === 'tarjetas', tj.hoy ? `<span class="badge" aria-label="${tj.hoy} para hoy">${tj.hoy}</span>` : '')}
      ${fila(`#/m/${m.slug}/feynman`, `Técnica de Feynman<small>${Object.keys(fey).length} de ${(r.feynman || []).length} explicados</small>`, Object.keys(fey).length > 0, c === 'feynman')}</nav>
    <h5>Evalúa</h5>
    <nav class="outline" aria-label="Evaluación del tema">${fila(`#/m/${m.slug}/evaluacion`, `Test del tema<small>${esc(estadoTest(m.slug))}</small>`, cierre.cerrado, c === 'evaluacion')}</nav>
    <nav class="rail-pie" aria-label="Curso"><a href="#/repaso">Repaso${pend(m)}</a><a href="#/apuntes">Mis apuntes</a><a href="#/progreso">Progreso</a></nav>`;
  function pend() { const n = STORE.pendientesRepaso().length + tarjetasHoyCurso(); return n ? `<span class="badge">${n}</span>` : ''; }
}
function crumbs(parts) {
  return `<div class="crumbs">${parts.map(([h, t], i) => (h ? `<a href="${h}">${esc(t)}</a>` : `<span>${esc(t)}</span>`) + (i < parts.length - 1 ? '<span aria-hidden="true">/</span>' : '')).join('')}</div>`;
}

// ---------- vistas ----------
function vInicio() {
  const pct = progresoCurso(); const p = STORE.get();
  // la última lección visitada solo vale si sigue existiendo en el curso
  const ult = (() => {
    const u = p.ultima && p.ultima.ruta ? p.ultima : null; const mm = u && u.ruta.match(/^#\/m\/([^/]+)\/l\/([^/]+)/);
    const m = mm && modBySlug(mm[1]); return m && m.lecciones.some((l) => l.slug === mm[2]) ? u : null;
  })();
  const R = 62, L = 2 * Math.PI * R;
  const estados = C.modules.map(estadoModulo);
  const hasta = estados.reduce((a, e, i) => (e !== 'nuevo' ? i : a), -1);
  const nLec = C.modules.reduce((a, m) => a + m.lecciones.length, 0); const okLec = C.modules.reduce((a, m) => a + progresoModulo(m).ok, 0);
  const cerrados = C.modules.filter((m) => STORE.cierreTema(m.slug, DATA).cerrado).length;
  const tjHoy = tarjetasHoyCurso(); const qHoy = STORE.pendientesRepaso().length;
  // tema abierto en el programa: el de la última visita o el primero sin cerrar
  const ultMod = ult && (ult.ruta.match(/^#\/m\/([^/]+)/) || [])[1];
  const abierto = ultMod || (C.modules[estados.findIndex((e) => e !== 'dominado')] || C.modules[0]).slug;
  main().innerHTML = `<div class="c-wide">
    ${DATA.modo === 'local' ? '<p class="aviso-proto">Prototipo con datos locales: el progreso se guarda solo en este navegador.</p>' : AVISO ? `<p class="aviso-proto">${esc(AVISO)}</p>` : ''}
    <div class="hero">
      <div><h1 class="h-curso">${esc(C.course.titulo)}</h1><p class="lead">${esc(C.course.subtitulo)}. ${C.modules.length} temas, unas ${Math.round(C.course.horas_estimadas)} horas de estudio.</p>
        <div class="hero-sigue">${ult ? `<span>Continúa donde lo dejaste</span><strong>${esc(ult.titulo)}</strong><a class="btn oro" href="${ult.ruta}">Continuar</a>`
          : `<span>Empieza por el principio</span><strong>Tema ${C.modules[0].orden}. ${esc(C.modules[0].titulo)}</strong><a class="btn oro" href="#/m/${C.modules[0].slug}">Empezar</a>`}</div></div>
      <div class="ring" aria-label="Progreso del curso: ${Math.round(pct * 100)}%">
        <svg viewBox="0 0 150 150" aria-hidden="true"><defs><linearGradient id="anillo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3ec6c0"/><stop offset=".5" stop-color="#8b6cf0"/><stop offset="1" stop-color="#f08a5d"/></linearGradient></defs><circle cx="75" cy="75" r="${R}" fill="none" stroke="var(--surface-2)" stroke-width="8"/>
        <circle cx="75" cy="75" r="${R}" fill="none" stroke="url(#anillo)" stroke-width="10" stroke-linecap="round" stroke-dasharray="${L}" stroke-dashoffset="${L * (1 - pct)}" transform="rotate(-90 75 75)"/></svg>
        <div><div class="pct">${Math.round(pct * 100)}%</div><div class="meta">del curso leído</div></div>
      </div>
    </div>
    <dl class="cifras">
      <div class="cf cf1"><span class="cf-ic" aria-hidden="true">📘</span><dt>Lecciones completadas</dt><dd>${okLec}<small> de ${nLec}</small></dd></div>
      <div class="cf cf2"><span class="cf-ic" aria-hidden="true">🏆</span><dt>Temas cerrados al 100 %</dt><dd>${cerrados}<small> de ${C.modules.length}</small></dd></div>
      <div class="cf cf3"><a href="#/repaso"><span class="cf-ic" aria-hidden="true">🃏</span><dt>Tarjetas para hoy</dt><dd>${tjHoy}</dd></a></div>
      <div class="cf cf4"><a href="#/repaso"><span class="cf-ic" aria-hidden="true">🔁</span><dt>Preguntas de repaso hoy</dt><dd>${qHoy}</dd></a></div>
    </dl>
    <h2 class="h2">Programa del curso</h2>
    <p class="muted">${esc(CFG.programa)}</p>
    <div class="neuroeje" id="eje"><div class="fill" style="height:0"></div>
      ${C.modules.map((m, i) => { const f = fotosModulo(m, 1)[0]; const pm = progresoModulo(m); return `<details class="nodo ${estados[i]}" style="--t:${colorTema(m)}" ${m.slug === abierto ? 'open' : ''}>
        <summary><span class="marca" aria-hidden="true"></span>
        <div><div class="nivel">Tema ${m.orden} · ${m.lecciones.length} lecciones · ${Math.round(m.tiempo_min / 5) * 5} min</div>
        <h3>${esc(m.titulo)}</h3>
        <p>${esc(m.descripcion)}</p>
        <div class="estado">${pm.ok} de ${pm.tot} lecciones · ${estados[i] === 'dominado' ? ESTADO_TXT.dominado : `test: ${estadoTest(m.slug).toLowerCase()}`}</div></div>
        ${f ? `<span class="mini" aria-hidden="true"><img src="${esc(srcSeguro(f.src))}" alt="" loading="lazy" decoding="async"></span>` : '<span></span>'}</summary>
        <div class="nodo-cuerpo">
          <ol class="sil">${m.lecciones.map((l) => `<li class="${lecHecha(m, l) ? 'si' : ''}"><a href="#/m/${m.slug}/l/${l.slug}"><span class="chk${lecHecha(m, l) ? ' si' : ''}" aria-label="${lecHecha(m, l) ? 'Completada' : 'Pendiente'}"></span><span>${esc(l.titulo)}</span><span class="min">${l.minutos} min</span></a></li>`).join('')}
            <li class="sil-extra"><a href="#/m/${m.slug}"><span class="chk ic-rec" aria-hidden="true"></span><span>Mapa, esquema, tablas, tarjetas y Feynman</span><span class="min">Estudio activo</span></a></li>
            <li class="sil-extra"><a href="#/m/${m.slug}/evaluacion"><span class="chk ic-test${STORE.cierreTema(m.slug, DATA).cerrado ? ' si' : ''}" aria-hidden="true"></span><span>Test del tema</span><span class="min">${DATA.itemsDeModulo(m.slug).length} preguntas</span></a></li></ol>
          <a class="btn sec peq" href="#/m/${m.slug}">Ir al tema</a></div>
      </details>`; }).join('')}
    </div></div>`;
  const pintaEje = () => { const eje = $('#eje'); if (!eje) return; const nodos = eje.querySelectorAll('.nodo'); if (hasta >= 0) { const n = nodos[hasta]; $('.fill', eje).style.height = (n.offsetTop + 26) + 'px'; } };
  requestAnimationFrame(pintaEje);
  main().querySelectorAll('.nodo').forEach((d) => d.addEventListener('toggle', pintaEje));
}

function vPrograma() {
  main().innerHTML = `<div class="c-wide">${crumbs([['#/', 'Inicio'], [null, 'Programa']])}
    <h1 class="h-curso">Programa</h1>
    <p class="lead">${esc(C.course.descripcion)}</p>
    <h2 class="h2">Objetivos del curso</h2><ul class="prose objetivos" style="margin-left:1.2rem">${C.course.objetivos_generales.map((o) => `<li>${esc(o)}</li>`).join('')}</ul>
    ${C.modules.map((m) => `<h2 class="h2"><a href="#/m/${m.slug}" style="text-decoration:none">${m.orden}. ${esc(m.titulo)}</a></h2>
      <ol class="lecciones">${m.lecciones.map((l) => lecItem(m, l)).join('')}</ol>`).join('')}
    <p class="meta" style="margin-top:24px">${esc(C.course.nota_fuentes)}</p></div>`;
}
function lecItem(m, l) {
  const d = (STORE.get().lecciones[`${m.slug}/${l.slug}`] || {});
  return `<li><a href="#/m/${m.slug}/l/${l.slug}"><span class="n">${l.orden}</span><span><h4>${esc(l.titulo)}</h4>${d.completada ? '<span class="ok">Completada</span>' : d.visita ? '<span class="meta">Empezada</span>' : ''}</span><span class="min">${l.minutos} min</span></a></li>`;
}

function vModulo(slug) {
  const m = modBySlug(slug); if (!m) return vNoEncontrado();
  const r = rec(m); const est = estadoModulo(m); const p = progresoModulo(m); const tj = estTarjetas(m);
  const nItems = DATA.itemsDeModulo(m.slug).length; const fotos = fotosModulo(m, 1);
  const fey = Object.keys(STORE.estudio(m.slug, 'feynman')).length;
  const recurso = (href, titulo, texto, estado) => `<a class="recurso" href="${href}"><strong>${titulo}</strong><span>${texto}</span>${estado ? `<span class="meta">${estado}</span>` : ''}</a>`;
  main().innerHTML = `<div class="c-wide">${crumbs([['#/', 'Inicio'], ['#/programa', 'Programa'], [null, `Tema ${m.orden}`]])}
    <div class="portada-mod"><div class="txt"><div class="num">Tema ${m.orden}</div><h1 class="h-curso">${esc(m.titulo)}</h1><p class="lead">${esc(m.descripcion)}</p>
      <div class="pm-prog"><span class="rail-barra"><span style="width:${p.tot ? 100 * p.ok / p.tot : 0}%"></span></span><span class="meta">${p.ok} de ${p.tot} lecciones · ${m.tiempo_min} min · ${ESTADO_TXT[est]}</span></div></div>
      ${fotos.length ? `<div class="fotos" aria-hidden="true">${fotos.map((f) => `<img src="${esc(srcSeguro(f.src))}" alt="" loading="lazy" decoding="async">`).join('')}</div>` : ''}</div>
    ${tabsTema(m, '')}
    <div class="tema-grid">
      <section aria-labelledby="t-ses"><h2 class="h2" id="t-ses">Tu sesión de estudio</h2>
        <p class="muted">Cinco bloques, uno detrás de otro. Cada uno se marca solo cuando lo has hecho.</p>${sesionHTML(m)}</section>
      <section aria-labelledby="t-obj"><h2 class="h2" id="t-obj">Qué vas a saber hacer</h2><ul class="prose objetivos" style="margin-left:1.2rem">${m.objetivos.map((o) => `<li>${esc(o)}</li>`).join('')}</ul>
        ${m.conceptos_clave.length ? `<h3 class="h3">Conceptos clave</h3><div class="chips">${m.conceptos_clave.map((c) => `<span class="chip">${esc(c)}</span>`).join('')}</div>` : ''}</section>
    </div>
    <h2 class="h2">Aprende</h2><ol class="lecciones">${m.lecciones.map((l) => lecItem(m, l)).join('')}</ol>
    <h2 class="h2">Organiza</h2><div class="recursos">
      ${recurso(`#/m/${m.slug}/mapa`, 'Mapa conceptual', `${(r.mapa && r.mapa.nodos || []).length} conceptos conectados por sus relaciones.`, STORE.estudio(m.slug, 'sesion').mapa ? 'Abierto' : '')}
      ${recurso(`#/m/${m.slug}/esquema`, 'Esquema jerárquico', 'Del concepto general a los detalles, para plegar y recordar.', STORE.estudio(m.slug, 'sesion').esquema ? 'Abierto' : '')}
      ${(r.tablas || []).length ? recurso(`#/m/${m.slug}/tablas`, 'Tablas comparativas', `${r.tablas.length} ${r.tablas.length === 1 ? 'tabla' : 'tablas'} para distinguir lo que suele confundirse.`, STORE.estudio(m.slug, 'sesion').tablas ? 'Abiertas' : '') : ''}</div>
    <h2 class="h2">Practica</h2><div class="recursos">
      ${recurso(`#/m/${m.slug}/tarjetas`, 'Tarjetas', `${tj.total} tarjetas con repaso espaciado.`, `${tj.hoy ? `${tj.hoy} para hoy · ` : ''}${tj.nuevas} nuevas · ${tj.dominadas} dominadas`)}
      ${recurso(`#/m/${m.slug}/feynman`, 'Técnica de Feynman', `Explica ${(r.feynman || []).length} conceptos con tus palabras y comprueba qué ideas faltan.`, `${fey} de ${(r.feynman || []).length} explicados`)}</div>
    <h2 class="h2">Evalúa</h2>
    <div class="cierre ${STORE.cierreTema(m.slug, DATA).cerrado ? 'ok' : ''}"><strong>Test del tema: ${esc(estadoTest(m.slug))}</strong><p>${nItems} preguntas, solo de este tema. Se cierra cuando las aciertas todas; las falladas vuelven en rondas nuevas.</p>
      <div class="row" style="margin-top:10px"><a class="btn" href="#/m/${m.slug}/evaluacion">Ir al test</a></div></div></div>`;
}

// ---------- páginas de estudio activo ----------
function vMapa(m) {
  main().innerHTML = `<div class="c-wide">${cabTema(m, 'mapa', 'Mapa conceptual')}
    <p class="lead">El tema entero en un vistazo: cada concepto unido a los demás por la relación que los liga. Para practicar, oculta los conceptos e intenta recordarlos antes de destaparlos.</p>
    <div id="mapa">${mapaHTML(rec(m).mapa, m.slug)}</div></div>`;
  if (rec(m).mapa) bindMapa($('#mapa'));
  marcarSesion(m, 'mapa');
}
function vEsquema(m) {
  main().innerHTML = `<div class="c-col">${cabTema(m, 'esquema', 'Esquema jerárquico')}
    <p class="lead">De lo general a lo particular. Pliega un apartado e intenta decir su contenido antes de abrirlo.</p>
    <div id="esq">${esquemaHTML(rec(m).esquema)}</div></div>`;
  bindEsquema($('#esq')); marcarSesion(m, 'esquema');
}
function vTablas(m) {
  main().innerHTML = `<div class="c-wide">${cabTema(m, 'tablas', 'Tablas comparativas')}
    <p class="lead">Lo que se parece y lo que los distingue, lado a lado. Tapa las celdas y destápalas solo cuando las hayas recordado.</p>
    <div id="tablas">${tablasHTML(rec(m).tablas, m.slug)}</div></div>`;
  bindTablas($('#tablas')); marcarSesion(m, 'tablas');
}
const DIAS = (t) => { const d = Math.round((t - Date.now()) / 86400000); return d <= 1 ? 'mañana' : `en ${d} días`; };
function vTarjetas(m) {
  const ts = rec(m).tarjetas || [];
  const pinta = () => {
    const estado = STORE.estudio(m.slug, 'tarjeta'); const s = resumenTarjetas(ts, estado); const cola = colaTarjetas(ts, estado);
    main().innerHTML = `<div class="c-col">${cabTema(m, 'tarjetas', 'Tarjetas')}
      <p class="lead">Lee la pregunta, responde en voz alta o por escrito y solo entonces gira la tarjeta. Según lo bien que la sepas, volverá antes o después.</p>
      <dl class="cifras compacta"><div><dt>Para hoy</dt><dd>${s.hoy}</dd></div><div><dt>Nuevas</dt><dd>${s.nuevas}</dd></div><div><dt>Dominadas</dt><dd>${s.dominadas}<small> de ${s.total}</small></dd></div></dl>
      ${cola.length ? `<div class="row"><button class="btn" id="tjEmpezar">${s.hoy ? `Empezar: ${s.hoy} para hoy${cola.length > s.hoy ? ` y ${cola.length - s.hoy} nuevas` : ''}` : `Empezar con ${cola.length} tarjetas nuevas`}</button></div>`
        : `<div class="cierre ok"><strong>Al día</strong><p>No te toca ninguna tarjeta. ${(() => { const ds = Object.values(estado).map((e) => e.due).filter(Boolean); return ds.length ? `La próxima vuelve ${DIAS(Math.min(...ds))}.` : ''; })()}</p></div>`}
      <div id="tjSesion"></div>
      <details class="tj-todas"><summary>Ver todas las tarjetas (${s.total})</summary><ul>${ts.map((t) => `<li><span class="nivel n-${nivelTarjeta(estado[t.id]).replace(/\s/g, '-').toLowerCase()}">${nivelTarjeta(estado[t.id])}</span>${md(t.frente)}</li>`).join('')}</ul></details></div>`;
    const b = $('#tjEmpezar'); if (b) b.addEventListener('click', () => sesion(cola));
  };
  const sesion = (lista) => {
    const q = lista.map((t) => ({ t, vuelta: false })); let k = 0; let bien = 0;
    const box = $('#tjSesion'); $('#tjEmpezar').closest('.row').remove();
    const ac = new AbortController(); window.addEventListener('hashchange', () => ac.abort(), { signal: ac.signal });
    const una = () => {
      if (k >= q.length) { ac.abort(); box.innerHTML = `<div class="cierre ok"><strong>Sesión terminada</strong><p>${bien} de ${lista.length} a la primera. Las que no sabías vuelven mañana.</p></div><div class="row"><button class="btn sec" id="tjOtra">Volver a las tarjetas</button></div>`; $('#tjOtra').addEventListener('click', pinta); renderRail(['m', m.slug, 'tarjetas']); return; }
      const { t, vuelta } = q[k]; const e = STORE.estudio(m.slug, 'tarjeta')[t.id];
      box.innerHTML = `<div class="tj"><div class="tj-cab meta"><span>Tarjeta ${Math.min(k + 1, lista.length)} de ${lista.length}${vuelta ? ' · otra vez' : ''}</span><span>${nivelTarjeta(e)}</span></div>
        <div class="tj-cara"><p class="tj-frente">${md(t.frente)}</p><div class="tj-reverso" hidden><p>${md(t.reverso)}</p>${t.ref ? `<a class="meta" href="${refLink(m.slug, t.ref)}">Ver dónde lo explica el material</a>` : ''}</div></div>
        <div class="row tj-acc"><button class="btn" id="tjGirar">Mostrar respuesta</button></div>
        <div class="row tj-notas" hidden><button class="btn sec" data-n="otra">No la sabía<small>hoy otra vez</small></button><button class="btn sec" data-n="dificil">Me costó<small>mañana</small></button><button class="btn" data-n="bien">La sabía<small>${DIAS(calificar(e, 'bien').due)}</small></button></div>
        <p class="meta tj-ayuda">Atajos: espacio para girar; 1, 2 y 3 para calificar.</p></div>`;
      const girar = () => { $('.tj-reverso', box).hidden = false; $('.tj-acc', box).hidden = true; $('.tj-notas', box).hidden = false; $('.tj-notas [data-n="bien"]', box).focus(); };
      $('#tjGirar').addEventListener('click', girar); $('#tjGirar').focus();
      const nota = async (n) => {
        $('.tj-notas', box).querySelectorAll('button').forEach((x) => { x.disabled = true; });
        if (!vuelta) { if (n === 'bien') bien++; try { await STORE.guardarEstudio(m.slug, 'tarjeta', t.id, calificar(e, n)); } catch (err) { toast('No se pudo guardar. Revisa tu conexión.'); } }
        if (n === 'otra') q.push({ t, vuelta: true });
        k++; una();
      };
      $('.tj-notas', box).querySelectorAll('button').forEach((x) => x.addEventListener('click', () => nota(x.dataset.n)));
      una.tecla = (ev) => {
        if (ev.target.closest('input,textarea')) return;
        if (ev.key === ' ' && !$('.tj-acc', box).hidden) { ev.preventDefault(); girar(); }
        else if (!$('.tj-notas', box).hidden && ['1', '2', '3'].includes(ev.key)) nota(['otra', 'dificil', 'bien'][+ev.key - 1]);
      };
    };
    document.addEventListener('keydown', (ev) => una.tecla && una.tecla(ev), { signal: ac.signal });
    una();
  };
  pinta();
}
function vFeynman(m, id) {
  const cs = rec(m).feynman || []; const hechos = STORE.estudio(m.slug, 'feynman');
  const c = cs.find((x) => x.id === id) || cs.find((x) => !hechos[x.id]) || cs[0];
  if (!c) { main().innerHTML = `<div class="c-col">${cabTema(m, 'feynman', 'Técnica de Feynman')}<p class="muted">Este tema no tiene conceptos para explicar.</p></div>`; return; }
  const previo = hechos[c.id];
  main().innerHTML = `<div class="c-col">${cabTema(m, 'feynman', 'Técnica de Feynman')}
    <p class="lead">Explica el concepto como si se lo contaras a alguien que no ha estudiado el tema, con frases sencillas y sin mirar el material. Después comprobamos qué ideas clave has incluido y cuáles faltan.</p>
    <nav class="fey-lista" aria-label="Conceptos">${cs.map((x) => `<a href="#/m/${m.slug}/feynman/${x.id}" ${x === c ? 'aria-current="page"' : ''}><span class="chk${hechos[x.id] ? ' si' : ''}" aria-hidden="true"></span>${esc(x.concepto)}</a>`).join('')}</nav>
    <div class="fey">
      <h2 class="h3">${esc(c.concepto)}</h2><p class="fey-preg">${md(c.pregunta)}</p>
      <label for="feyTxt" class="meta">Tu explicación</label>
      <textarea id="feyTxt" class="inp" rows="8" maxlength="3000" placeholder="Empieza por lo más general y ve paso a paso…">${esc(previo ? previo.texto || '' : '')}</textarea>
      <div class="row" style="margin-top:10px"><button class="btn" id="feyComp">Comprobar mi explicación</button></div>
      <div id="feyRes" aria-live="polite"></div></div></div>`;
  $('#feyComp').addEventListener('click', async () => {
    const txt = $('#feyTxt').value.trim();
    if (txt.split(/\s+/).length < 8) { $('#feyRes').innerHTML = '<p class="fb ko">Escribe al menos un par de frases antes de comprobar.</p>'; return; }
    const r = evaluarFeynman(c, txt); const ok = r.filter((x) => x.ok).length;
    $('#feyRes').innerHTML = `<div class="fb ${ok === r.length ? 'ok' : ''}"><strong>${ok} de ${r.length} ideas clave en tu explicación</strong>
      <ul class="fey-ideas">${r.map((x) => `<li class="${x.ok ? 'si' : 'no'}">${esc(x.idea)}</li>`).join('')}</ul>
      ${ok < r.length ? `<p>Repasa lo que falta${c.ref ? ` en <a href="${refLink(m.slug, c.ref)}">el apartado del material</a>` : ''} y vuelve a explicarlo con tus palabras. La comprobación busca términos, así que también puede no reconocer una idea dicha de otra forma: júzgalo tú.</p>` : '<p>Explicación completa. Vuelve a intentarlo dentro de unos días sin mirar la anterior.</p>'}</div>`;
    try { await STORE.guardarEstudio(m.slug, 'feynman', c.id, { texto: txt.slice(0, 3000), cubiertas: ok, total: r.length }); renderRail(['m', m.slug, 'feynman']); $$chk(); } catch (e) { toast('No se pudo guardar. Revisa tu conexión.'); }
  });
  function $$chk() { const a = main().querySelector('.fey-lista [aria-current] .chk'); if (a) a.classList.add('si'); }
}

function vLeccion(ms, ls, blk) {
  const m = modBySlug(ms); const l = m && m.lecciones.find((x) => x.slug === ls);
  if (!l) return vNoEncontrado();
  STORE.visitar(`${m.slug}/${l.slug}`, { ruta: `#/m/${m.slug}/l/${l.slug}`, titulo: `${m.titulo}: ${l.titulo}` });
  const i = m.lecciones.indexOf(l); const prev = m.lecciones[i - 1]; const next = m.lecciones[i + 1];
  const cuerpo = DATA.leccion(m.slug, l.slug);
  const hecho = lecHecha(m, l);
  const secciones = cuerpo ? cuerpo.bloques.filter((b) => b.t === 'h').map((b) => b.texto) : l.secciones;
  const sig = next ? { href: `#/m/${m.slug}/l/${next.slug}`, t: next.titulo, s: 'Siguiente lección' } : { href: `#/m/${m.slug}/mapa`, t: 'Organiza el tema', s: 'Has leído el tema' };
  main().innerHTML = `${crumbs([['#/', 'Inicio'], [`#/m/${m.slug}`, `Tema ${m.orden}`], [null, `Lección ${l.orden}`]])}
  <div class="lectura" aria-hidden="true"><div></div></div>
  <div class="leccion"><article class="prose">
    <header class="lec-banda"><div class="lec-cab"><span class="eyebrow">Tema ${m.orden} · Lección ${i + 1} de ${m.lecciones.length}</span>
      <nav class="lec-puntos" aria-label="Lecciones del tema">${m.lecciones.map((x, j) => `<a href="#/m/${m.slug}/l/${x.slug}" title="${esc(x.titulo)}" aria-label="Lección ${j + 1}: ${esc(x.titulo)}" class="${lecHecha(m, x) ? 'hecha' : ''}" ${x === l ? 'aria-current="page"' : ''}></a>`).join('')}</nav></div>
    <h1 class="h-curso">${esc(l.titulo)}</h1>
    <p class="meta">${l.minutos} min de lectura · ${esc(m.titulo)}</p></header>
    <div class="esencial"><h3>Lo esencial</h3><ul>${l.lo_esencial.map((x) => `<li>${md(x)}</li>`).join('')}</ul></div>
    ${cuerpo ? bloquesHTML(cuerpo.bloques, DATA.figura) : '<p class="borrador">Esta lección todavía no tiene texto.</p>'}
    <h2 class="h2">Comprueba lo aprendido</h2>
    <p class="muted">Tres preguntas rápidas sin mirar el texto. No cuentan para la nota; las que falles pasan a tu repaso.</p>
    <div id="check"></div>
  </article>
  <aside aria-label="En esta lección"><div class="aside-in"><h4>En esta lección</h4><ol>${secciones.map((s, k) => `<li>${cuerpo ? `<a href="#" data-ir="sec-${k}">${esc(s)}</a>` : esc(s)}</li>`).join('')}</ol>
    ${STORE.guardarApunte ? apuntesHTML() : ''}
    <h4 style="margin-top:16px">Objetivos</h4><ul style="margin-left:1.1rem;color:var(--text-dim)">${l.objetivos.map((o) => `<li>${esc(o)}</li>`).join('')}</ul></div></aside></div>
  <nav class="lec-barra" aria-label="Avance de la lección">
    ${prev ? `<a class="lb-prev" href="#/m/${m.slug}/l/${prev.slug}" title="${esc(prev.titulo)}"><small>Anterior</small><span>${esc(prev.titulo)}</span></a>` : `<a class="lb-prev" href="#/m/${m.slug}"><small>Volver</small><span>Inicio del tema</span></a>`}
    <button class="btn ${hecho ? 'hecho' : ''}" id="btnHecho" ${hecho ? 'disabled' : ''}>${hecho ? 'Completada' : 'Marcar como completada'}</button>
    <a class="lb-next ${hecho ? 'listo' : ''}" href="${sig.href}" title="${esc(sig.t)}"><small>${sig.s}</small><span>${esc(sig.t)}</span></a>
  </nav>
  ${STORE.guardarApunte ? '<button type="button" class="ap-fab" aria-controls="apuntes" aria-expanded="false">Mis apuntes</button>' : ''}`;
  main().querySelectorAll('[data-ir]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); const t = document.getElementById(a.dataset.ir); if (t) t.scrollIntoView(); }));
  main().querySelectorAll('[data-fig]').forEach((el) => bindFigura(el, DATA.figura(el.dataset.fig), { modo: 'explorar' }));
  if (STORE.guardarApunte) montarApuntes(`${m.slug}/${l.slug}`);
  { // barra de lectura
    const barra = main().querySelector('.lectura div'); const art = main().querySelector('article'); const ac = new AbortController();
    const pinta = () => { const r = art.getBoundingClientRect(); const tot = r.height - window.innerHeight + 120; barra.style.width = Math.max(0, Math.min(100, (-r.top + 60) / Math.max(1, tot) * 100)) + '%'; };
    window.addEventListener('scroll', pinta, { passive: true, signal: ac.signal }); window.addEventListener('hashchange', () => ac.abort(), { signal: ac.signal }); pinta();
  }
  // enlace a un apartado concreto (desde la corrección, el mapa o una tarjeta): se lleva y se resalta
  if (blk) setTimeout(() => {
    const t = main().querySelector(`[data-blk="${CSS.escape(blk)}"]`);
    if (t) { t.scrollIntoView({ block: 'center' }); t.classList.add('resalta'); setTimeout(() => t.classList.remove('resalta'), 4200); }
  }, 80);
  $('#btnHecho').addEventListener('click', (e) => {
    STORE.completar(`${m.slug}/${l.slug}`); e.target.textContent = 'Completada'; e.target.disabled = true; e.target.classList.add('hecho');
    main().querySelector('.lb-next').classList.add('listo'); renderRail(['m', m.slug, 'l', l.slug]); toast('Lección completada');
  });
  // comprobación rápida
  const todas = DATA.itemsDeModulo(m.slug);
  const qs = shuffle(todas.filter((it) => it.leccion === l.slug)).concat(shuffle(todas.filter((it) => it.leccion !== l.slug))).slice(0, 3);
  const box = $('#check');
  if (!qs.length) { box.innerHTML = '<p class="borrador">Este tema aún no tiene preguntas.</p>'; return; }
  const cola = qs.map((it) => ({ it, vuelta: false })); let k = 0;
  const siguiente = () => {
    if (k >= cola.length) { box.insertAdjacentHTML('beforeend', `<p class="meta" style="margin-top:12px">Las tres acertadas. Para cerrar el tema, haz el <a href="#/m/${m.slug}/evaluacion">test del tema</a>: se cierra cuando aciertas todas sus preguntas.</p>`); return; }
    const d = document.createElement('div'); d.style.marginTop = '14px'; box.append(d);
    const { it, vuelta } = cola[k];
    mountItem(d, it, { modo: 'practica', numero: Math.min(k + 1, qs.length), total: qs.length, data: DATA,
      corregir: (item, resp) => DATA.comprobar(item, resp, !vuelta),
      onResult: (r) => { if (r.correcta === false) cola.push({ it, vuelta: true }); k++; }, onNext: siguiente,
      textoSiguiente: 'Siguiente' });
  };
  siguiente();
}

// ---------- apuntes del alumno ----------
const fechaCorta = (t) => new Date(t).toLocaleString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
function apuntesHTML() {
  return `<section class="apuntes" id="apuntes" aria-labelledby="ap-t">
    <div class="ap-cab"><h4 id="ap-t">Mis apuntes</h4><button type="button" class="ap-cerrar" aria-label="Cerrar apuntes">×</button></div>
    <textarea id="apTexto" maxlength="20000" aria-describedby="ap-ayuda" placeholder="Escribe aquí lo que quieras recordar de esta lección: dudas, resúmenes, reglas mnemotécnicas…"></textarea>
    <div class="ap-pie"><span class="ap-estado" aria-live="polite"></span><a href="#/apuntes">Ver todos</a></div>
    <p class="meta" id="ap-ayuda">Se guardan solos en tu cuenta. Selecciona un texto de la lección para copiarlo aquí.</p></section>`;
}
function montarApuntes(key) {
  const ta = $('#apTexto'); const est = $('.ap-estado'); const panel = $('#apuntes'); const fab = $('.ap-fab');
  const BK = `aurzane-apunte-${CURSO}-${key}`;
  const ac = new AbortController(); const sig = { signal: ac.signal };
  let chip = null; const quitarChip = () => { if (chip) { chip.remove(); chip = null; } };
  const guardado = STORE.apunte(key);
  let ultimo = guardado ? guardado.texto : '';
  let borrador = null; try { borrador = localStorage.getItem(BK); } catch (e) {}
  ta.value = borrador != null ? borrador : ultimo;
  est.textContent = guardado ? `Guardado · ${fechaCorta(guardado.fecha)}` : '';
  let h = null;
  const ajustar = () => { ta.style.height = 'auto'; ta.style.height = Math.min(Math.max(ta.scrollHeight, 150), 520) + 'px'; };
  const guardar = async () => {
    clearTimeout(h); h = null;
    const t = ta.value; if (t === ultimo) { est.textContent = ultimo ? est.textContent : ''; return; }
    est.textContent = 'Guardando…';
    try {
      const r = await STORE.guardarApunte(key, t); ultimo = t;
      try { localStorage.removeItem(BK); } catch (e) {}
      est.textContent = r ? `Guardado · ${fechaCorta(r.fecha)}` : 'Apunte borrado';
      renderRail(location.hash.replace(/^#\/?/, '').split('/').filter(Boolean));
    } catch (e) { est.textContent = 'Sin conexión: se guardará en cuanto vuelva'; h = setTimeout(guardar, 8000); }
  };
  const programar = () => { try { localStorage.setItem(BK, ta.value); } catch (e) {} est.textContent = 'Cambios sin guardar'; clearTimeout(h); h = setTimeout(guardar, 1200); };
  ta.addEventListener('input', () => { ajustar(); programar(); });
  ta.addEventListener('blur', () => { if (h) guardar(); });
  const salir = () => { if (h) guardar(); };
  window.addEventListener('hashchange', () => { salir(); quitarChip(); ac.abort(); }, sig); window.addEventListener('pagehide', salir, sig);
  if (borrador != null && borrador !== ultimo) programar();
  requestAnimationFrame(ajustar);
  // en pantallas estrechas el panel es una hoja que se abre con el botón flotante
  const abrir = (v) => { panel.classList.toggle('abierta', v); fab.setAttribute('aria-expanded', v); if (v) ta.focus({ preventScroll: true }); };
  fab.addEventListener('click', () => abrir(!panel.classList.contains('abierta')));
  $('.ap-cerrar', panel).addEventListener('click', () => { abrir(false); fab.focus(); });
  // copiar al apunte el texto seleccionado en la lección
  const art = main().querySelector('article');
  const mirar = () => {
    const sel = document.getSelection(); const txt = sel && String(sel).trim();
    if (!txt || txt.length > 3000 || !sel.rangeCount || !art.contains(sel.anchorNode) || ta.contains(sel.anchorNode)) return quitarChip();
    const r = sel.getRangeAt(0).getBoundingClientRect();
    if (!chip) {
      chip = document.createElement('button'); chip.type = 'button'; chip.className = 'ap-chip'; chip.textContent = '+ Añadir a mis apuntes';
      chip.addEventListener('mousedown', (e) => e.preventDefault());
      chip.addEventListener('click', () => {
        const t = String(document.getSelection()).trim().replace(/\s+\n/g, '\n');
        ta.value = (ta.value.trim() ? ta.value.replace(/\s*$/, '') + '\n\n' : '') + t.split('\n').map((x) => '> ' + x).join('\n') + '\n';
        ajustar(); programar(); quitarChip(); document.getSelection().removeAllRanges();
        if (getComputedStyle(fab).display !== 'none') abrir(true); else { ta.scrollIntoView({ block: 'nearest' }); }
        toast('Añadido a tus apuntes');
      });
      document.body.append(chip);
    }
    chip.style.left = Math.max(8, Math.min(window.innerWidth - 220, r.left + r.width / 2 - 100)) + 'px';
    chip.style.top = (r.top + window.scrollY - 44 < window.scrollY + 60 ? r.bottom + window.scrollY + 8 : r.top + window.scrollY - 44) + 'px';
  };
  art.addEventListener('mouseup', () => setTimeout(mirar, 0));
  art.addEventListener('keyup', (e) => { if (e.shiftKey) mirar(); });
  document.addEventListener('selectionchange', () => { const s = document.getSelection(); if (!s || s.isCollapsed) setTimeout(() => { if (document.getSelection().isCollapsed) quitarChip(); }, 150); }, sig);
}
function vApuntes() {
  const ap = STORE.apuntes ? STORE.apuntes() : {};
  const grupos = C.modules.map((m) => ({ m, ls: m.lecciones.filter((l) => ap[`${m.slug}/${l.slug}`]) })).filter((g) => g.ls.length);
  const total = grupos.reduce((a, g) => a + g.ls.length, 0);
  main().innerHTML = `<div class="c-col">${crumbs([['#/', 'Inicio'], [null, 'Mis apuntes']])}<h1 class="h-curso">Mis apuntes</h1>
    <p class="lead">${total ? `Tienes apuntes en ${total} ${total === 1 ? 'lección' : 'lecciones'}. Se guardan en tu cuenta y los ves en cualquier dispositivo.` : 'Aún no has escrito apuntes. Abre cualquier lección: el cuaderno está a la derecha del texto (en el móvil, en el botón «Mis apuntes»).'}</p>
    ${total ? '<div class="row" style="margin:16px 0 8px"><button class="btn sec" id="apDescargar">Descargar todos (.txt)</button></div>' : ''}
    ${grupos.map((g) => `<h2 class="h2">${g.m.orden}. ${esc(g.m.titulo)}</h2>${g.ls.map((l) => { const a = ap[`${g.m.slug}/${l.slug}`]; return `<article class="ap-tarjeta">
      <div class="ap-cab"><h3 class="h3" style="margin:0"><a href="#/m/${g.m.slug}/l/${l.slug}">${esc(l.titulo)}</a></h3><span class="meta">${fechaCorta(a.fecha)}</span></div>
      <div class="ap-texto">${esc(a.texto)}</div></article>`; }).join('')}`).join('')}</div>`;
  const b = $('#apDescargar');
  if (b) b.addEventListener('click', () => {
    const txt = [`Mis apuntes · ${C.course.titulo}`, ''].concat(...grupos.map((g) => [`== Tema ${g.m.orden}. ${g.m.titulo} ==`, '', ...g.ls.flatMap((l) => { const a = ap[`${g.m.slug}/${l.slug}`]; return [`-- ${l.titulo} (${fechaCorta(a.fecha)})`, a.texto.trim(), '']; })])).join('\n');
    const url = URL.createObjectURL(new Blob([txt], { type: 'text/plain;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = `mis-apuntes-${CFG.apuntes}.txt`; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
  });
}

function vAtlas(id) {
  if (!id) {
    main().innerHTML = `<div class="c-wide">${crumbs([['#/', 'Inicio'], [null, 'Atlas']])}<h1 class="h-curso">Atlas</h1>
      <p class="lead">Esquemas originales con zonas activas. Explóralos con etiquetas y practica después sin ellas.</p>
      <ul class="lecciones" style="margin-top:20px">${DATA.figuras().map((f) => `<li><a href="#/atlas/${f.id}"><span class="n">${modBySlug(f.modulo)?.orden ?? ''}</span><span><h4>${esc(f.titulo)}</h4><span class="meta">${f.regions.length} estructuras · ${esc(modBySlug(f.modulo)?.titulo || '')}</span></span><span class="min">Abrir</span></a></li>`).join('')}</ul>
      <p class="meta" style="margin-top:14px">Además de estos esquemas, cada lección tiene fotografías e ilustraciones reales; pulsa cualquiera para ampliarla.</p></div>`;
    return;
  }
  const f = DATA.figura(id); if (!f) return vNoEncontrado();
  main().innerHTML = `<div class="c-wide">${crumbs([['#/', 'Inicio'], ['#/atlas', 'Atlas'], [null, f.titulo]])}<h1 class="h-curso">${esc(f.titulo)}</h1>
    ${labHTML(f)}
    <h2 class="h2">Practica sin etiquetas</h2><p class="muted">Te pediremos cada estructura en orden aleatorio.</p>
    <div class="row"><button class="btn" id="btnPract">Empezar práctica</button></div><div id="pract"></div></div>`;
  main().querySelectorAll('[data-fig]').forEach((el) => bindFigura(el, f, { modo: 'explorar' }));
  $('#btnPract').addEventListener('click', () => {
    const items = shuffle(f.regions).map((r, i) => ({ id: `atlas-${f.id}-${r.id}`, tipo: 'identificacion_imagen', enunciado: `Señala: ${r.nombre}.`, figura: f.id, region: r.id, explicacion: r.info, modulo: f.modulo }));
    const box = $('#pract'); box.innerHTML = ''; let k = 0, ok = 0;
    const sig = () => {
      if (k >= items.length) { box.insertAdjacentHTML('beforeend', `<p class="h3">${ok} de ${items.length} estructuras reconocidas.</p>`); return; }
      const d = document.createElement('div'); d.style.marginTop = '14px'; box.append(d);
      mountItem(d, items[k], { modo: 'practica', numero: k + 1, total: items.length, data: DATA,
        corregir: async (item, resp) => ({ correcta: resp.region === item.region, solucion: { region: item.region }, explicacion: item.explicacion }), onResult: (r) => { if (r.correcta) ok++; k++; }, onNext: sig, textoSiguiente: 'Siguiente' });
      d.scrollIntoView({ block: 'nearest' });
    };
    sig();
  });
}

// ---------- evaluación ----------
function vEvaluaciones() {
  main().innerHTML = `<div class="c-wide">${crumbs([['#/', 'Inicio'], [null, 'Evaluaciones']])}<h1 class="h-curso">Evaluaciones</h1>
    <p class="lead">Cada tema tiene su test con preguntas solo de ese tema. Un test se cierra cuando aciertas todas sus preguntas: las que fallas vuelven en rondas nuevas hasta que las aciertes. Lo cerrado pasa al repaso espaciado, que se va apilando tema tras tema.</p>
    <ul class="lecciones" style="margin-top:20px">${C.modules.filter((m) => m.slug !== 'integracion-clinica').map((m) => { const n = DATA.itemsDeModulo(m.slug).length; 
      return `<li><a href="#/m/${m.slug}/evaluacion"><span class="n">${m.orden}</span><span><h4>${esc(m.titulo)}</h4><span class="meta">${n} preguntas · ${estadoTest(m.slug)}</span></span><span class="min">${STORE.cierreTema(m.slug, DATA).cerrado ? '✓' : n ? 'Abrir' : 'Sin preguntas'}</span></a></li>`; }).join('')}
      <li><a href="#/final"><span class="n">★</span><span><h4>Evaluación final integradora</h4><span class="meta">Todos los temas mezclados · ${estadoTest('final')}</span></span><span class="min">Abrir</span></a></li></ul></div>`;
}

function vEvaluacion(modSlug) {
  const final = !modSlug; const m = final ? null : modBySlug(modSlug);
  if (!final && !m) return vNoEncontrado();
  const clave = final ? 'final' : m.slug;
  const pool = final ? DATA.todosLosItems() : DATA.itemsDeModulo(m.slug);
  const titulo = final ? 'Evaluación final integradora' : `Evaluación: ${m.titulo}`;
  const pend = STORE.resumenAbierto(clave);
  const cierre = STORE.cierreTema(clave, DATA); const cadenaP = STORE.cadenaAbierta(clave);
  const tipos = [...new Set(pool.map((i) => i.tipo))];
  main().innerHTML = `<div class="c-col">${crumbs(final ? [['#/', 'Inicio'], ['#/evaluaciones', 'Evaluaciones'], [null, 'Final']] : [['#/', 'Inicio'], [`#/m/${m.slug}`, `Tema ${m.orden}`], [null, 'Test']])}
    ${final ? '' : `<p class="tema-sup">Tema ${m.orden} · ${esc(m.titulo)}</p>`}<h1 class="h-curso">${final ? esc(titulo) : 'Test del tema'}</h1>${final ? '' : tabsTema(m, 'evaluacion')}
    <p class="lead">${pool.length} preguntas${final ? ' de todos los temas' : ', solo de este tema'}. Tipos: ${tipos.map((t) => TIPO_TXT[t]).join(', ')}.</p>
    <div class="cierre ${cierre.cerrado ? 'ok' : ''}"><strong>${cierre.cerrado ? 'Test cerrado al 100 %' : 'Cómo se cierra este test'}</strong>
      <p>${cierre.cerrado ? `Acertaste todas sus preguntas el ${new Date(cierre.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'long' })}. Ahora vuelven en tu <a href="#/repaso">repaso espaciado</a> (1, 3, 7, 16 días…) mezcladas con las de otros temas cerrados. Puedes repetir el test cuando quieras.`
        : `Responde todas las preguntas del tema. Las que falles vuelven en una ronda nueva, con la solución al responder, hasta que las aciertes todas. Solo entonces el test queda cerrado y el tema pasa al repaso espaciado.`}</p></div>
    ${cadenaP ? `<div class="continuar"><div><div class="meta">Ronda ${cadenaP.ronda} terminada</div><strong>Te ${cadenaP.pendientes === 1 ? 'queda 1 pregunta' : `quedan ${cadenaP.pendientes} preguntas`} por acertar de ${cadenaP.total}</strong></div><div class="row"><button class="btn" id="btnRonda">Ronda ${cadenaP.ronda + 1}: repetir las falladas</button></div></div>` : ''}
    ${pend ? `<div class="continuar"><div><div class="meta">Tienes un intento sin terminar</div><strong>${pend.respondidas} de ${pend.total} respondidas</strong></div><div class="row"><button class="btn" id="btnReanudar">Reanudar</button><button class="btn sec" id="btnDescartar">Empezar uno nuevo</button></div></div>` : ''}
    <form class="config" id="cfg" style="margin-top:22px">
      <fieldset><legend>Modo</legend>
        <label><input type="radio" name="modo" value="practica" checked> Práctica: ves la solución al responder cada pregunta</label>
        <label><input type="radio" name="modo" value="examen"> Examen: sin ayuda, con nota al final</label></fieldset>
      <fieldset id="fsSol"><legend>En el examen, ver las soluciones</legend>
        <label><input type="radio" name="sol" value="al_final" checked> Al terminar</label>
        <label><input type="radio" name="sol" value="nunca"> Solo la nota (repetir sin pistas)</label></fieldset>
      <fieldset><legend>Número de preguntas</legend>
        <label><input type="radio" name="n" value="0" checked> Todas (${pool.length}): el test que cierra el ${final ? 'curso' : 'tema'}</label>
        ${[10, 20, 40].filter((n) => n < pool.length).map((n) => `<label><input type="radio" name="n" value="${n}"> ${n}, práctica parcial (no cierra el ${final ? 'curso' : 'tema'})</label>`).join('')}</fieldset>
      <div class="row"><button class="btn" type="submit" ${pool.length ? '' : 'disabled'}>Empezar</button></div>
      <p class="meta" id="cfgErr" role="alert"></p>
    </form></div>`;
  const cfg = $('#cfg');
  const syncSol = () => { $('#fsSol').hidden = cfg.modo.value !== 'examen'; };
  cfg.addEventListener('change', syncSol); syncSol();
  const arrancar = async (params) => {
    cfg.querySelector('button[type=submit]').disabled = true;
    try { const it = await DATA.iniciarIntento({ modulo: final ? null : m.slug, titulo, ...params }); correr({ ...it, clave, titulo }); }
    catch (e) { $('#cfgErr').textContent = 'No se pudo empezar la evaluación. ' + (e.message || 'Inténtalo de nuevo.'); cfg.querySelector('button[type=submit]').disabled = false; }
  };
  cfg.addEventListener('submit', (e) => {
    e.preventDefault();
    arrancar({ modo: cfg.modo.value, mostrar: cfg.modo.value === 'examen' ? cfg.sol.value : 'al_responder', n: +cfg.n.value || pool.length, reanudar: false });
  });
  if (cadenaP) $('#btnRonda').addEventListener('click', async (e) => {
    e.target.disabled = true;
    try { const it = await DATA.reintentar({ id: cadenaP.intento }); correr({ ...it, clave, titulo }); }
    catch (err) { $('#cfgErr').textContent = 'No se pudo abrir la ronda. ' + (err.message || ''); e.target.disabled = false; }
  });
  if (pend) {
    $('#btnReanudar').addEventListener('click', () => arrancar({ reanudar: true }));
    $('#btnDescartar').addEventListener('click', () => { $('.continuar').remove(); });
  }
}
function correr(intento) {
  const items = intento.items.map((id) => DATA.item(id)).filter(Boolean);
  const hechas = new Set(intento.respondidas || []);
  const resultados = {};
  main().innerHTML = `<div class="c-col"><div class="eval-cab"><h1 class="h3" style="margin:0">${esc(intento.titulo)}</h1><span class="meta">${(intento.ronda || 1) > 1 ? `Ronda ${intento.ronda} · solo las falladas` : intento.modo === 'examen' ? 'Examen' : 'Práctica'}${intento.reanudado ? ' · reanudado' : ''}</span></div>
    <div class="prog" role="progressbar" aria-valuemin="0" aria-valuemax="${items.length}"><div id="pbar"></div></div><div id="q"></div></div>`;
  const paso = () => {
    const k = items.findIndex((it) => !hechas.has(it.id));
    $('#pbar').style.width = (100 * hechas.size / items.length) + '%';
    $('.prog').setAttribute('aria-valuenow', hechas.size);
    if (k < 0) return terminar(intento, items);
    const box = $('#q'); box.innerHTML = '';
    mountItem(box, items[k], {
      modo: intento.modo === 'examen' ? 'examen' : 'practica', numero: hechas.size + 1, total: items.length, data: DATA,
      corregir: (item, resp) => DATA.responder(intento, item, resp),
      onResult: (r) => { hechas.add(items[k].id); resultados[items[k].id] = r.correcta; },
      onNext: paso, textoSiguiente: hechas.size + 1 < items.length ? 'Siguiente' : 'Ver resultado',
    });
  };
  paso();
}
async function terminar(intento, items) {
  main().innerHTML = '<div class="c-col"><p class="muted">Calculando el resultado…</p></div>';
  let res;
  try { res = await DATA.terminarIntento(intento); }
  catch (e) { main().innerHTML = `<div class="c-col"><h1 class="h-curso">No se pudo cerrar la evaluación</h1><p class="lead">Tus respuestas están guardadas. Comprueba tu conexión y vuelve a la evaluación para terminarla.</p><a class="btn" href="${location.hash}">Volver</a></div>`; return; }
  await STORE.refrescar(); renderRail(['evaluaciones']);
  const det = new Map(res.detalle.map((d) => [d.question_id, d]));
  const ok = res.n_correctas; const tot = res.n_total; const nota = res.nota;
  const fallos = items.filter((it) => !(det.get(it.id) || {}).correcta);
  const porTipo = {}; items.forEach((it) => { const t = (porTipo[it.tipo] = porTipo[it.tipo] || { ok: 0, n: 0 }); t.n++; if ((det.get(it.id) || {}).correcta) t.ok++; });
  const repasar = {}; fallos.forEach((it) => { const m = modBySlug(it.modulo); const l = m && it.leccion && m.lecciones.find((x) => x.slug === it.leccion); const key = l ? `${m.slug}/${l.slug}` : m ? m.slug : '?'; repasar[key] = repasar[key] || { m, l, n: 0 }; repasar[key].n++; });
  const verSol = res.detalle.some((d) => 'solucion' in d);
  const ronda = res.ronda || intento.ronda || 1; const quedan = fallos.length;
  const msgCierre = res.cerrado
    ? `<div class="cierre ok"><strong>Test cerrado al 100 %${ronda > 1 ? ` en ${ronda} rondas` : ''}</strong><p>Has acertado todas las preguntas. A partir de mañana vuelven en tu repaso espaciado (1, 3, 7, 16 días…), mezcladas con las de los demás temas que cierres: así cada repaso se apoya en el anterior.</p></div>`
    : `<div class="cierre"><strong>Ronda ${ronda}: ${quedan === 1 ? 'te queda 1 pregunta' : `te quedan ${quedan} preguntas`} por acertar</strong><p>El test se cierra cuando las aciertes todas. Repasa las soluciones de abajo y lanza la ronda ${ronda + 1}, que solo trae las falladas.</p></div>`;
  main().innerHTML = `<div class="c-col resultado">
    <h1 class="h-curso">${esc(intento.titulo)}</h1>
    <div class="row" style="gap:28px;margin:12px 0 6px"><div><div class="nota">${ok}/${tot}</div><div class="meta">${Math.round(nota * 100)}% de aciertos · ${(nota * 10).toFixed(1)} sobre 10</div></div></div>
    ${msgCierre}
    <h2 class="h2">Por tipo de pregunta</h2>
    <table class="tabla"><tbody>${Object.entries(porTipo).map(([t, v]) => `<tr><td>${TIPO_TXT[t]}</td><td>${v.ok} de ${v.n}</td></tr>`).join('')}</tbody></table>
    ${fallos.length ? `<h2 class="h2">Qué repasar</h2><ul class="prose">${Object.values(repasar).map((x) => `<li>${x.l ? `<a href="#/m/${x.m.slug}/l/${x.l.slug}">${esc(x.l.titulo)}</a>` : x.m ? `<a href="#/m/${x.m.slug}">${esc(x.m.titulo)}</a>` : ''} (${x.n} ${x.n === 1 ? 'fallo' : 'fallos'})</li>`).join('')}</ul>` : '<p class="h3">Sin fallos.</p>'}
    ${verSol && fallos.length ? `<h2 class="h2">Soluciones de las falladas</h2>${fallos.map((it) => { const d = det.get(it.id) || {}; return `<div class="fb ko" style="margin-bottom:10px"><strong>${esc(it.enunciado)}</strong>${d.respondida ? '' : 'Sin responder. '}${esc(DATA.solucionTexto(it, d.solucion))}<div class="volver">${esc(d.explicacion || '')}</div>${d.referencia ? refHTML(it, d.referencia, true) : ''}</div>`; }).join('')}` : ''}
    <div class="row" style="margin-top:22px">${!res.cerrado && quedan ? `<button class="btn" id="btnRonda">Ronda ${ronda + 1}: repetir las ${quedan === 1 ? 'falladas (1)' : `${quedan} falladas`}</button><a class="btn sec" href="${location.hash}" id="btnRep">Volver al test</a>` : `<a class="btn" href="#/repaso">Ir al repaso</a><a class="btn sec" href="${location.hash}" id="btnRep">Volver al test</a>`}</div><p class="meta" id="rondaErr" role="alert"></p></div>`;
  $('#btnRep').addEventListener('click', (e) => { e.preventDefault(); route(); });
  if ($('#btnRonda')) $('#btnRonda').addEventListener('click', async (e) => {
    e.target.disabled = true;
    try { const it = await DATA.reintentar({ id: res.attempt_id || intento.id }); correr({ ...it, clave: intento.clave, titulo: intento.titulo }); }
    catch (err) { $('#rondaErr').textContent = 'No se pudo abrir la ronda. ' + (err.message || ''); e.target.disabled = false; }
  });
}

// ---------- repaso espaciado ----------
// tarjetas que tocan hoy, tema a tema (cada tema tiene su propia sesión de tarjetas)
function tarjetasRepasoHTML() {
  const ms = C.modules.map((m) => ({ m, s: estTarjetas(m) })).filter((x) => x.s.hoy);
  if (!ms.length) return '';
  return `<h2 class="h2">Tarjetas</h2><ul class="lecciones">${ms.map(({ m, s }) => `<li><a href="#/m/${m.slug}/tarjetas"><span class="n">${m.orden}</span><span><h4>${esc(m.titulo)}</h4><span class="meta">${s.dominadas} de ${s.total} dominadas</span></span><span class="min">${s.hoy} para hoy</span></a></li>`).join('')}</ul>`;
}
function vRepaso() {
  const pend = STORE.pendientesRepaso().map((id) => DATA.item(id)).filter(Boolean);
  const prox = STORE.proximoRepaso();
  main().innerHTML = `<div class="c-col">${crumbs([['#/', 'Inicio'], [null, 'Repaso']])}<h1 class="h-curso">Repaso de hoy</h1>
    <p class="lead">${pend.length ? `${pend.length} ${pend.length === 1 ? 'pregunta toca' : 'preguntas tocan'} hoy, de todos los temas que has cerrado. Las que falles se repiten al final hasta que las aciertes; vuelven mañana. Las acertadas a la primera se espacian más.` : (tarjetasHoyCurso() ? 'Hoy no te toca ninguna pregunta, pero sí tarjetas.' : 'No tienes nada pendiente.')}</p>
    ${tarjetasRepasoHTML()}
    ${pend.length ? '<h2 class="h2">Preguntas</h2>' : ''}
    ${!pend.length ? `<p class="muted">${prox ? `Tu próximo repaso es el ${new Date(prox).toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })}.` : 'Las preguntas que falles en lecciones y evaluaciones aparecerán aquí.'}</p>` : ''}
    <div id="rep"></div></div>`;
  if (!pend.length) return;
  const box = $('#rep'); let k = 0;
  const cola = shuffle(pend).map((it) => ({ it, vuelta: false })); // intercalado entre temas
  const sig = () => {
    if (k >= cola.length) { box.innerHTML = '<p class="h3">Repaso de hoy terminado: todas acertadas.</p>'; renderRail(['repaso']); return; }
    box.innerHTML = ''; const { it, vuelta } = cola[k];
    mountItem(box, it, { modo: 'practica', numero: Math.min(k + 1, pend.length), total: pend.length, data: DATA,
      corregir: (item, resp) => DATA.comprobar(item, resp, !vuelta),
      onResult: (r) => { if (r.correcta === false) cola.push({ it, vuelta: true }); k++; },
      onNext: () => { STORE.refrescar().then(sig); }, textoSiguiente: 'Siguiente' });
  };
  sig();
}

function vProgreso() {
  const p = STORE.get(); const ints = p.intentos || [];
  main().innerHTML = `<div class="c-wide">${crumbs([['#/', 'Inicio'], [null, 'Progreso']])}<h1 class="h-curso">Tu progreso</h1>
    <p class="lead">Visitado: abriste alguna lección. Completado: terminaste todas las lecciones e hiciste el test del tema. Cerrado al 100 %: además acertaste todas las preguntas del test del tema, ronda tras ronda.</p>
    <div style="margin-top:18px">${C.modules.map((m) => { const tot = m.lecciones.length; const ok = m.lecciones.filter((l) => (p.lecciones[`${m.slug}/${l.slug}`] || {}).completada).length; const e = estadoModulo(m);
      return `<div class="barra-mod"><a href="#/m/${m.slug}">${m.orden}. ${esc(m.titulo)}</a><div class="b" aria-label="${ok} de ${tot} lecciones"><div style="width:${100 * ok / tot}%"></div></div><span class="est meta">${e === 'dominado' ? ESTADO_TXT[e] : `${ESTADO_TXT[e]} · test: ${estadoTest(m.slug).toLowerCase()}`}</span></div>`; }).join('')}</div>
    <h2 class="h2">Intentos</h2>
    ${ints.length ? `<div class="scroll-x"><table class="tabla"><thead><tr><th>Fecha</th><th>Evaluación</th><th>Ronda</th><th>Aciertos</th></tr></thead><tbody>${ints.slice().reverse().slice(0, 30).map((i) => `<tr><td>${new Date(i.fin).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })}</td><td>${esc(i.titulo)}</td><td>${i.ronda || 1}${(i.ronda || 1) === 1 ? (i.modo === 'examen' ? ' · examen' : ' · práctica') : ''}</td><td>${Math.round(i.nota * 100)}%</td></tr>`).join('')}</tbody></table></div>` : '<p class="muted">Aún no has hecho ninguna evaluación.</p>'}
    <div class="row" style="margin-top:24px"><button class="btn sec" id="btnReset">Borrar mi progreso de este navegador</button></div><div id="conf"></div></div>`;
  $('#btnReset').addEventListener('click', () => {
    $('#conf').innerHTML = '<div class="continuar"><span>Se borrarán lecciones, intentos y repaso. No se puede deshacer.</span><div class="row"><button class="btn" id="si">Borrar</button><button class="btn sec" id="no">Cancelar</button></div></div>';
    $('#si').addEventListener('click', async () => { try { await STORE.reset(); toast('Progreso borrado'); } catch (e) { toast('No se pudo borrar. Inténtalo de nuevo.'); } route(); });
    $('#no').addEventListener('click', () => { $('#conf').innerHTML = ''; });
  });
}

function vBibliografia() {
  const fuentes = new Set(); Object.values(DATA.todasLecciones()).forEach((l) => (l.fuentes || []).forEach((f) => fuentes.add(f)));
  main().innerHTML = `<div class="c-col prose">${crumbs([['#/', 'Inicio'], [null, 'Bibliografía y créditos']])}<h1 class="h-curso">Bibliografía y créditos</h1>
    <p>${esc(C.course.nota_fuentes)}</p>
    ${fuentes.size ? `<h2 class="h2">Obras de referencia</h2><ul>${[...fuentes].map((f) => `<li>${esc(f)}</li>`).join('')}</ul>` : ''}
    <h2 class="h2">Créditos de las imágenes</h2>
    <h3 class="h3">Imágenes de Wikimedia Commons</h3>
    <p class="meta">Cada imagen lleva su crédito debajo; aquí están todas juntas. Pulsa el nombre para ver el archivo original.</p>
    <div class="scroll-x"><table class="tabla creditos"><thead><tr><th>Archivo</th><th>Autor</th><th>Licencia</th></tr></thead><tbody>${creditosImagenes().map((c) => `<tr><td><a href="${esc(c.pagina)}" target="_blank" rel="noopener">${esc(decodeURIComponent(c.pagina.split('/wiki/File:')[1] || '').replace(/_/g, ' '))}</a></td><td>${esc(c.autor)}</td><td>${c.url_licencia ? `<a href="${esc(c.url_licencia)}" target="_blank" rel="noopener">${esc(c.licencia)}</a>` : esc(c.licencia)}</td></tr>`).join('')}</tbody></table></div>
    <p class="meta">Solo se usan imágenes de Wikimedia Commons con licencia que permite su uso (dominio público, CC0, CC BY o CC BY-SA), con su autor y su licencia indicados. Las imágenes se han convertido a WebP y reducido de tamaño para la web, sin otros cambios.</p>
    <h3 class="h3">Vídeos</h3><p>Los vídeos de repaso son de sus autores y se reproducen desde YouTube. Los marcados como «Recomendado» son del canal <a href="https://www.youtube.com/@anatomiafacil" target="_blank" rel="noopener">Anatomía Fácil por Juan José Sánchez</a>.</p></div>`;
}
function creditosImagenes() {
  const vistos = new Map();
  const add = (b) => { const c = b && b.credito; if (c && /^https:\/\//.test(c.pagina || '') && !vistos.has(c.pagina)) vistos.set(c.pagina, c); };
  Object.values(DATA.todasLecciones()).forEach((l) => (l.bloques || []).forEach((b) => { if (b.t === 'imagen') add(b); }));
  DATA.todosLosItems().forEach((it) => add(it.imagen));
  return [...vistos.values()].sort((a, b) => a.pagina.localeCompare(b.pagina));
}
function vAyuda() {
  main().innerHTML = `<div class="c-col prose">${crumbs([['#/', 'Inicio'], [null, 'Ayuda']])}<h1 class="h-curso">Cómo usar el curso</h1>
    <h2 class="h3">El recorrido de cada tema</h2><p>Cada tema se estudia en cinco bloques, uno detrás de otro, y la página del tema te dice en cuál estás:</p>
    <ol><li><strong>Lectura comprensiva.</strong> Lecciones breves con lo esencial al principio. Marca cada una como completada al terminarla.</li>
    <li><strong>Organización visual.</strong> Mapa conceptual, esquema jerárquico y tablas comparativas del tema. Todos tienen un modo de práctica que oculta el contenido para que lo recuerdes.</li>
    <li><strong>Recuperación activa.</strong> Tarjetas de pregunta y respuesta y la técnica de Feynman: explicas un concepto con tus palabras y ves qué ideas clave faltan.</li>
    <li><strong>Corrección de errores.</strong> El test del tema. Al fallar ves el fragmento del material que da la respuesta, con un enlace al apartado exacto.</li>
    <li><strong>Repaso espaciado.</strong> Tarjetas y preguntas vuelven cuando empiezas a olvidarlas.</li></ol>
    <h2 class="h3">Tarjetas</h2><p>Lee la pregunta, respóndela sin mirar y gira la tarjeta. Si no la sabías vuelve en la misma sesión y mañana; si te costó, mañana; si la sabías, cada vez más tarde (1, 3, 7, 16, 35 y 80 días). Una tarjeta está dominada cuando la has acertado al menos tres veces seguidas espaciadas.</p>
    <h2 class="h3">Tests: se cierran al 100 %</h2><p>Cada tema tiene un test con todas sus preguntas. Las que fallas vuelven en rondas nuevas, con la solución al responder, hasta que las aciertes todas; solo entonces el test queda cerrado. En la primera ronda eliges práctica (ves la solución al responder) o examen (sin ayuda, con la nota al final). Si cierras a mitad, la ronda se guarda y puedes reanudarla.</p>
    <h2 class="h3">Repaso, una técnica encima de otra</h2><p>Al cerrar un test, sus preguntas pasan al repaso espaciado: vuelven al día siguiente y después cada vez más separadas (1, 3, 7, 16 días…), mezcladas con las de los demás temas cerrados. En cada sesión de repaso, lo que falles se repite al final hasta acertarlo y vuelve al día siguiente. Así se suman la práctica de recuperación, el reaprendizaje hasta acertar todo, el espaciado y la mezcla de temas.</p>
    <h2 class="h3">Atajos</h2><ul><li>1 a 4: elegir opción</li><li>Intro: comprobar o pasar a la siguiente</li></ul></div>`;
}
function vNoEncontrado() { main().innerHTML = `<div class="c-col"><h1 class="h-curso">No encontramos esa página</h1><p class="lead">El enlace puede estar mal escrito o el contenido se ha movido.</p><a class="btn" href="#/">Volver al inicio</a></div>`; }

// ---------- router ----------
// vistas que dependen de intentos y repaso: se leen frescos del servidor antes de pintarlas
let rutaN = 0;
function route() {
  const ruta = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  const [a, , c] = ruta; const n = ++rutaN;
  if (['evaluaciones', 'final', 'repaso', 'progreso'].includes(a) || (a === 'm' && c === 'evaluacion')) {
    main().innerHTML = '<div class="c-col"><p class="muted">Cargando…</p></div>';
    STORE.refrescar().catch(() => {}).then(() => { if (n === rutaN) pintar(ruta); });
  } else pintar(ruta);
}
// un color propio por tema: ayuda a situarse y a asociar cada recurso con su tema
const COLORES_TEMA = ['#8a6a28', '#1f7a8c', '#3d5a98', '#6a4c93', '#a8402f', '#2f7a55', '#b5651d', '#b0417a', '#3b6e8f', '#7a5230', '#9c3d54', '#2e6b6b', '#5a6b2e'];
const colorTema = (m) => COLORES_TEMA[C.modules.indexOf(m) % COLORES_TEMA.length];
function pintar(ruta) {
  { const mm = ruta[0] === 'm' && modBySlug(ruta[1]); document.documentElement.style.setProperty('--tema', mm ? colorTema(mm) : 'var(--gold-deep)'); }
  renderRail(ruta);
  $('#rail').classList.remove('abierto');
  const [a, b, c, d, e] = ruta;
  const m = a === 'm' && modBySlug(b);
  const VISTAS = { mapa: vMapa, esquema: vEsquema, tablas: vTablas, tarjetas: vTarjetas, feynman: vFeynman };
  if (!a) vInicio();
  else if (a === 'programa') vPrograma();
  else if (m && c === 'l' && d) vLeccion(b, d, e);
  else if (m && c === 'evaluacion') vEvaluacion(b);
  else if (m && VISTAS[c]) VISTAS[c](m, d);
  else if (a === 'm' && b && !c) vModulo(b);
  else if (a === 'atlas') vAtlas(b);
  else if (a === 'evaluaciones') vEvaluaciones();
  else if (a === 'final') vEvaluacion(null);
  else if (a === 'repaso') vRepaso();
  else if (a === 'progreso') vProgreso();
  else if (a === 'bibliografia') vBibliografia();
  else if (a === 'ayuda') vAyuda();
  else if (a === 'apuntes') vApuntes();
  else vNoEncontrado();
  window.scrollTo(0, 0);
  main().focus({ preventScroll: true });
}

// ---------- arranque ----------
const SUPABASE_URL = 'https://chtfpqwrrarfdjcivlad.supabase.co';
const SUPABASE_KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw';
const FLAG = 'learn.courses.enabled';

function vSinSesion() {
  $('#rail').innerHTML = '';
  main().innerHTML = `<div class="c-col"><h1 class="h-curso">Inicia sesión para entrar al curso</h1>
    <p class="lead">Los cursos de AURZANE LEARN son gratuitos con tu cuenta de AURZANE ID. Así guardamos tu progreso, tus evaluaciones y tu repaso en cualquier dispositivo.</p>
    <div class="row" style="margin-top:18px"><a class="btn" href="https://aurzane.com/mi-aurzane.html?next=${encodeURIComponent(location.href)}">Iniciar sesión o crear cuenta</a></div>
    <p class="meta" style="margin-top:14px">Si ya iniciaste sesión en otra pestaña, <a href="${esc(location.href)}" id="recargar">recarga esta página</a>.</p></div>`;
  $('#recargar').addEventListener('click', (e) => { e.preventDefault(); location.reload(); });
}
function vProximamente() {
  $('#rail').innerHTML = '';
  main().innerHTML = `<div class="c-col"><h1 class="h-curso">Muy pronto</h1>
    <p class="lead">Estamos terminando este curso. Te avisaremos en LEARN cuando abra.</p>
    <div class="row" style="margin-top:18px"><a class="btn sec" href="https://learn.aurzane.com/">Volver a LEARN</a></div></div>`;
}
function vErrorCarga() {
  main().innerHTML = '<div class="c-col"><h1 class="h-curso">No se pudo cargar el curso</h1><p class="lead">Comprueba tu conexión y recarga la página. Si sigue fallando, escríbenos a hola@aurzane.com.</p></div>';
}

async function cargarSupabase() {
  if (!window.supabase || !window.crearClienteAurzaneID) throw new Error('Faltan las librerías de sesión');
  const sb = window.crearClienteAurzaneID(SUPABASE_URL, SUPABASE_KEY);
  window.__aurzaneSb = sb;
  const { data: { session } } = await sb.auth.getSession();
  if (!session) return 'sin-sesion';
  const [{ data: caps }, { data: flag }] = await Promise.all([
    sb.rpc('mis_capacidades'),
    sb.from('configuration').select('key,enabled').eq('key', FLAG).maybeSingle(),
  ]);
  const editor = Array.isArray(caps) && caps.includes('courses.read');
  if (!(flag && flag.enabled) && !editor) return 'cerrado';
  const { createSupabaseData } = await import('./data-supabase.js?v=f15');
  const { createSupabaseStore } = await import('./store-supabase.js?v=f15');
  const data = await createSupabaseData(sb, CURSO);
  if (!data) return 'cerrado';
  const store = await createSupabaseStore(sb, data, CURSO);
  return { data, store, editor, abierto: !!(flag && flag.enabled) };
}

async function init() {
  initTema(); activarMedios();
  $('#menuBtn').addEventListener('click', () => $('#rail').classList.toggle('abierto'));
  const local = document.documentElement.dataset.cursosModo === 'local';
  try {
    if (local) {
      STORE = createLocalStore(CURSO);
      // en local los datos (con soluciones) se sirven desde content/, que nunca se sube a SiteGround
      DATA = await createLocalData(document.documentElement.dataset.cursosDatos || `cursos/data/${CURSO}`, STORE);
    } else {
      const r = await cargarSupabase();
      if (r === 'sin-sesion') return vSinSesion();
      if (r === 'cerrado') return vProximamente();
      DATA = r.data; STORE = r.store;
      AVISO = r.editor && !r.abierto ? 'Vista previa de editor: el curso aún no está abierto a los alumnos.' : '';
    }
  } catch (e) {
    console.error(e); if (window.__aurzaneLogErr) window.__aurzaneLogErr('cursos: ' + (e && e.message));
    return vErrorCarga();
  }
  C = DATA.curso();
  $('#cursoTitulo').textContent = C.course.titulo;
  window.addEventListener('hashchange', route);
  route();
}
init();
