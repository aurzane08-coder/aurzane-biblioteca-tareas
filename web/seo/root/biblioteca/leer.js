/* Ficha y lector de la Biblioteca AURZANE. El PDF se muestra aquí mismo con
   pdf.js (funciona también en móviles, donde el visor nativo no se integra). */
const B = window.BIBLIOTECA;
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const temaPorN = Object.fromEntries(B.temas.map(t => [t.n, t]));
const macroDeTema = {}; B.macrotemas.forEach(m => m.temas.forEach(n => { macroDeTema[n] = m.id; }));

// En las páginas fijas de cada libro (biblioteca/libro/<id>.html) la ficha ya viene escrita en el HTML
// y BIB_BASE apunta a la carpeta de la biblioteca.
const BASE = window.BIB_BASE || '';
const ESTATICA = !!window.LIBRO_ID;
const INICIO = BASE || './';
const id = window.LIBRO_ID || new URLSearchParams(location.search).get('libro');
const libro = B.libros.find(l => l.id === id);

if (libro && !ESTATICA) {
  // leer.html?libro=<id> es la dirección antigua: lleva a la página fija del libro.
  location.replace('libro/' + encodeURIComponent(libro.id) + '.html' + location.hash);
} else if (ESTATICA) {
  if (libro && libro.tipo === 'pdf') abrirLector();
} else if (!libro) {
  $('ficha').innerHTML = '<h1>No encontramos ese libro</h1><p class="lead" style="margin:12px 0 24px">Puede que el enlace esté incompleto.</p><a class="btn" href="./">Volver a la biblioteca</a>';
} else {
  document.title = libro.titulo + ' | Biblioteca AURZANE';
  $('bc-libro').textContent = libro.titulo.length > 60 ? libro.titulo.slice(0, 57) + '…' : libro.titulo;
  const meta = document.querySelector('meta[name="description"]');
  if (meta) meta.content = libro.resumen;
  pintarFicha();
  if (libro.tipo === 'pdf') abrirLector();
}

function pintarFicha() {
  const temas = Object.keys(libro.temas).map(Number);
  const chips = temas.map(n => {
    const t = temaPorN[n];
    return `<a class="chip leer" href="${INICIO}#m=${macroDeTema[n]}&t=${n}">${esc(t.nombre)}</a>` +
      libro.temas[n].map(s => `<a class="chip" href="${INICIO}#m=${macroDeTema[n]}&t=${n}&s=${encodeURIComponent(s)}">${esc(s)}</a>`).join('');
  }).join('');
  const portada = `<div class="portada tipo m-${macroDeTema[libro.principal] || 'x'}"><span class="lomo"></span><span class="pt-tit">${esc(libro.titulo)}</span><span class="pt-aut">${esc(libro.autores)}</span>${libro.portada ? `<img src="${esc(BASE + libro.portada)}" alt="Portada de ${esc(libro.titulo)}" onerror="this.remove()">` : ''}</div>`;
  let cuerpo;
  if (libro.tipo === 'pdf') {
    cuerpo = `
      <dl class="datos">
        <dt>Obtenido de</dt><dd><a href="${esc(libro.url)}" target="_blank" rel="noopener">${esc(libro.fuente)}</a></dd>
        <dt>Editorial</dt><dd>${esc(libro.editorial)}${libro.anio ? ', ' + esc(libro.anio) : ''}</dd>
        <dt>Licencia</dt><dd><a href="${esc(libro.licencia_url)}" target="_blank" rel="noopener license">${esc(libro.licencia)}</a></dd>
        <dt>Tipo</dt><dd>${esc(libro.nivel)}${libro.paginas ? ' · ' + libro.paginas + ' páginas' : ''}</dd>
      </dl>
      <div class="acciones">
        <a class="btn" href="#lector">Leer ahora</a>
        <a class="btn sec" href="${esc(BASE + libro.pdf)}" download>Descargar PDF</a>
        <a class="btn sec" href="${esc(BASE + libro.pdf)}" target="_blank" rel="noopener">Abrir en pantalla completa</a>
      </div>`;
  } else {
    const ed = [libro.editorial, libro.anio, libro.isbn ? 'ISBN ' + libro.isbn : ''].filter(Boolean).map(esc).join(' · ');
    cuerpo = `${ed ? `<p class="meta-ed">Edición en español: ${ed}</p>` : ''}
      <p class="nota-ref">Este libro tiene derechos de autor, así que no lo alojamos. Te dejamos la ficha para que sepas de qué trata y lo busques en una librería o biblioteca.</p>
      <div class="acciones"><a class="btn" href="${esc(libro.buscar)}" target="_blank" rel="noopener">Ver dónde conseguirlo</a><a class="btn sec" href="./">Volver a la biblioteca</a></div>`;
  }
  $('ficha').innerHTML = `
    <article class="ficha">
      ${portada}
      <div>
        <h1>${esc(libro.titulo)}</h1>
        <p class="autores">${esc(libro.autores)}</p>
        <p class="resumen">${esc(libro.resumen)}</p>
        ${cuerpo}
        <div class="temas-libro" aria-label="Temas">${chips}</div>
      </div>
    </article>`;
}

async function abrirLector() {
  $('lector').hidden = false;
  if (!Promise.withResolvers) Promise.withResolvers = function(){ let a, b; const p = new Promise((r, j) => { a = r; b = j; }); return { promise: p, resolve: a, reject: b }; };
  let pdfjs;
  try {
    pdfjs = await import('https://cdn.jsdelivr.net/npm/pdfjs-dist@4.2.67/build/pdf.min.mjs');
    pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.2.67/build/pdf.worker.min.mjs';
  } catch (e) { return falloLector(); }
  let doc;
  try { doc = await pdfjs.getDocument({ url: BASE + libro.pdf, rangeChunkSize: 262144 }).promise; }
  catch (e) { return falloLector(); }

  const cont = $('paginas');
  cont.innerHTML = '';
  let zoom = 1;
  const ancho = () => Math.min(cont.clientWidth || 800, 900) * zoom;
  const p1 = await doc.getPage(1);
  const v1 = p1.getViewport({ scale: 1 });
  const ratio = v1.height / v1.width;
  const huecos = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const d = document.createElement('div');
    d.className = 'pagina'; d.dataset.n = i;
    d.style.width = ancho() + 'px'; d.style.height = Math.round(ancho() * ratio) + 'px';
    cont.appendChild(d); huecos.push(d);
  }
  const hechas = new Map();
  async function pintar(d) {
    const n = +d.dataset.n, w = ancho();
    if (hechas.get(n) === w) return;
    hechas.set(n, w);
    const pg = await doc.getPage(n);
    const vp = pg.getViewport({ scale: 1 });
    const sc = (w / vp.width) * Math.min(window.devicePixelRatio || 1, 1.6);
    const v = pg.getViewport({ scale: sc });
    const c = document.createElement('canvas');
    c.width = Math.floor(v.width); c.height = Math.floor(v.height);
    c.setAttribute('aria-label', 'Página ' + n);
    await pg.render({ canvasContext: c.getContext('2d'), viewport: v }).promise;
    d.style.height = 'auto';
    d.replaceChildren(c);
  }
  const io = new IntersectionObserver(ents => ents.forEach(e => { if (e.isIntersecting) pintar(e.target); }), { rootMargin: '900px 0px' });
  // Libera la memoria de las páginas que quedan muy lejos (libros de 400+ páginas).
  const lejos = new IntersectionObserver(ents => ents.forEach(e => {
    const d = e.target;
    if (!e.isIntersecting && d.firstChild) { d.style.height = d.getBoundingClientRect().height + 'px'; d.replaceChildren(); hechas.delete(+d.dataset.n); }
  }), { rootMargin: '4000px 0px' });
  huecos.forEach(d => { io.observe(d); lejos.observe(d); });
  const info = () => {
    const y = window.innerHeight / 2;
    const vis = huecos.find(d => { const r = d.getBoundingClientRect(); return r.top <= y && r.bottom >= y; });
    $('pag-info').textContent = 'Página ' + (vis ? vis.dataset.n : 1) + ' de ' + doc.numPages;
  };
  window.addEventListener('scroll', () => requestAnimationFrame(info), { passive: true });
  info();
  const rezoom = f => {
    zoom = Math.max(0.6, Math.min(2.2, zoom * f));
    hechas.clear();
    huecos.forEach(d => { d.style.width = ancho() + 'px'; if (!d.firstChild) d.style.height = Math.round(ancho() * ratio) + 'px'; });
    huecos.forEach(d => { const r = d.getBoundingClientRect(); if (r.bottom > -900 && r.top < window.innerHeight + 900) pintar(d); });
  };
  $('mas').onclick = () => rezoom(1.15);
  $('menos').onclick = () => rezoom(1 / 1.15);
  $('arriba').onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
}
function falloLector() {
  $('paginas').innerHTML = `<p class="cargando">No pudimos mostrar el libro aquí. <a href="${esc(BASE + libro.pdf)}" target="_blank" rel="noopener" style="color:var(--gold-light)">Ábrelo directamente en PDF</a>.</p>`;
  $('pag-info').textContent = '';
}
