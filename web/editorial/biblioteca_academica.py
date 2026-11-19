"""Rediseño editorial de las bibliotecas académicas de cada mundo (mind/live/nexus/build/learn-biblioteca.html), 19/11/2026.
Toma la versión del servidor (traer/servidor/...), cambia SOLO la presentación de los artículos y deja la copia en publicar/.
- Los resúmenes muestran bien sus apartados (<h4>Background</h4>…) y las cursivas o subíndices, sin etiquetas como texto.
- PMID sin «.0», DOI discreto, enlace al original destacado, autores abreviados, lista editorial con separadores finos.
No toca consultas, filtros, datos ni textos."""
import os, re, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSS = r'''
  /* AZ-EDITORIAL 19/11/2026: lista editorial (sin cajas), jerarquía clara y resúmenes legibles */
  #list{border-top:1px solid var(--border);}
  .paper{border:0;border-bottom:1px solid var(--border);border-radius:0;padding:26px 2px 24px;margin:0;background:none;}
  .paper:hover{border-color:var(--border);}
  .paper-meta{font-family:'Instrument Sans',sans-serif;font-size:.74rem;letter-spacing:.01em;color:var(--text-dim);gap:6px 10px;margin-bottom:10px;}
  .paper-meta .pm-sep{opacity:.5}
  .badge-oa{font-size:.7rem;color:var(--accent-text);border:1px solid var(--line-accent);border-radius:999px;padding:1px 9px;}
  .badge-fuente{border:0;padding:0;border-radius:0;}
  .paper h3{font-family:'Bodoni Moda',serif;font-size:1.2rem;font-weight:600;line-height:1.32;letter-spacing:-.005em;margin:0 0 8px;max-width:62ch;}
  .paper .autores{font-size:.84rem;color:var(--text-dim);margin-bottom:14px;}
  .paper .abstract{font-size:.93rem;line-height:1.68;color:var(--text);opacity:.86;max-width:72ch;max-height:5.1em;overflow:hidden;
    -webkit-mask-image:linear-gradient(#000 60%,transparent);mask-image:linear-gradient(#000 60%,transparent);}
  .paper .abstract.expanded{max-height:none;-webkit-mask-image:none;mask-image:none;}
  .paper .abstract p{margin:0 0 .6em}
  .paper .abstract .abs-h{display:block;font-family:'Instrument Sans',sans-serif;font-size:.72rem;font-weight:600;letter-spacing:.04em;color:var(--accent-text);margin:.7em 0 .15em}
  .paper .abstract .abs-h:first-child{margin-top:0}
  .paper .toggle-abs{font-family:'Instrument Sans',sans-serif;font-size:.8rem;text-decoration:none;margin-top:8px;display:inline-flex;align-items:center;gap:6px}
  .paper .toggle-abs::after{content:'';width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg) translateY(-2px);transition:transform .2s}
  .paper .toggle-abs[aria-expanded="true"]::after{transform:rotate(-135deg) translateY(-1px)}
  .paper .paper-foot{margin-top:16px;padding-top:0;border-top:0;gap:10px 16px;}
  .paper .ids{font-family:'Instrument Sans',sans-serif;font-size:.74rem;color:var(--text-dim);display:flex;gap:14px;flex-wrap:wrap}
  .paper .ids a{color:inherit;text-decoration:none;border-bottom:1px dotted currentColor}
  .paper .paper-foot a.ir{font-family:'Instrument Sans',sans-serif;font-size:.82rem;font-weight:600;color:var(--accent-text);border:1px solid var(--line-accent);border-radius:999px;padding:7px 14px;display:inline-flex;align-items:center;gap:8px;transition:background .2s,border-color .2s}
  .paper .paper-foot a.ir:hover{text-decoration:none;background:rgba(var(--gold-rgb),.08);border-color:var(--accent-text)}
  .paper .paper-foot a.ir svg{width:13px;height:13px}
  .result-count{font-family:'Instrument Sans',sans-serif;font-size:.8rem;margin-bottom:14px}
  .empty-state p,.load-state p{font-size:.95rem;line-height:1.6}
  @media(max-width:640px){.paper{padding:22px 0}.paper h3{font-size:1.08rem}.paper .paper-foot{flex-direction:column;align-items:flex-start}}
'''
JS = r'''function limpiarAbstract(t){
  /* AZ-EDITORIAL: los resúmenes de Europe PMC traen etiquetas (<h4>, <i>, <sup>, <jats:p>…). Se escapan todas y solo se
     recuperan las seguras; los encabezados pasan a etiquetas discretas. */
  let s = escapeHtml(String(t || '')).replace(/&lt;\/?jats:/g, m => m.replace('jats:', ''));
  s = s.replace(/&lt;h[1-6][^&]*?&gt;([\s\S]*?)&lt;\/h[1-6]&gt;/gi, (m, x) => `<span class="abs-h">${x.replace(/[:.]\s*$/, '')}</span>`);
  s = s.replace(/&lt;(\/?)(i|em|b|strong|sup|sub|p)&gt;/gi, (m, c, n) => `<${c}${n.toLowerCase()}>`);
  s = s.replace(/&lt;(title|sec|italic|bold)[^&]*?&gt;|&lt;\/(title|sec|italic|bold)&gt;/gi, ' ');
  return s.replace(/\s{2,}/g, ' ').trim();
}
function autoresCortos(a){
  const l = String(a || '').split(/;\s*|,\s+(?=[A-ZÁÉÍÓÚ][a-záéíóú'-]+\s[A-Z]{1,3}\b)/).map(x => x.trim()).filter(Boolean);
  return l.length > 4 ? escapeHtml(l.slice(0, 3).join(', ')) + ` y ${l.length - 3} más` : escapeHtml(l.join(', '));
}
function renderPapers(papers, append){
  const list = document.getElementById('list');
  const html = papers.map(p => {
    const abs = p.abstract ? limpiarAbstract(p.abstract) : '<em style="color:var(--text-dim);">Sin resumen disponible.</em>';
    const autores = p.autores ? autoresCortos(p.autores) : 'Autores no disponibles';
    const oa = p.es_acceso_abierto ? `<span class="badge-oa">Acceso abierto</span>` : '';
    const doi = p.doi ? String(p.doi).replace(/^https?:\/\/(dx\.)?doi\.org\//i, '') : '';
    const link = p.url_articulo || (doi ? 'https://doi.org/' + doi : '');
    const pmid = p.pmid != null && p.pmid !== '' ? String(p.pmid).replace(/\.0$/, '') : '';
    const meta = [p.anio || 's/f', p.fuente ? escapeHtml(p.fuente) : '', p.licencia ? escapeHtml(String(p.licencia).toUpperCase()) : ''].filter(Boolean).join('<span class="pm-sep">·</span>');
    return `
      <article class="paper">
        <div class="paper-meta">${oa}<span>${meta}</span></div>
        <h3>${escapeHtml(p.titulo)}</h3>
        <div class="autores">${autores}</div>
        <div class="abstract">${abs}</div>
        ${p.abstract && p.abstract.length > 260 ? `<button class="toggle-abs" aria-expanded="false">Leer el resumen completo</button>` : ''}
        <div class="paper-foot">
          <span class="ids">${pmid ? `<span>PMID ${escapeHtml(pmid)}</span>` : ''}${doi ? `<a href="${escapeHtml(urlSegura('https://doi.org/' + doi))}" target="_blank" rel="noopener noreferrer">DOI ${escapeHtml(doi)}</a>` : ''}</span>
          ${link ? `<a class="ir" href="${escapeHtml(urlSegura(link))}" target="_blank" rel="noopener noreferrer">Leer el artículo original <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 3h7v7M13 3L4 12"/></svg></a>` : ''}
        </div>
      </article>
    `;
  }).join('');

  if(append){ list.insertAdjacentHTML('beforeend', html); } else { list.innerHTML = html; }

  list.querySelectorAll('.toggle-abs').forEach(btn => {
    if(btn.dataset.wired) return;
    btn.dataset.wired = '1';
    btn.addEventListener('click', () => {
      const absEl = btn.previousElementSibling;
      const abierto = absEl.classList.toggle('expanded');
      btn.setAttribute('aria-expanded', abierto ? 'true' : 'false');
      btn.textContent = abierto ? 'Mostrar menos' : 'Leer el resumen completo';
    });
  });
}
'''
for h in ('mind', 'live', 'nexus', 'build', 'learn'):
    src = os.path.join(R, 'traer', 'servidor', f'{h}.aurzane.com', f'{h}-biblioteca.html')
    if not os.path.exists(src): continue
    s = open(src, encoding='utf-8').read()
    s = re.sub(r'\n  /\* AZ-EDITORIAL 19/11/2026.*?(?=\n</style>)', '', s, flags=re.S)
    s = s.replace('\n</style>', CSS.rstrip() + '\n</style>', 1)
    i = s.find('function limpiarAbstract(') if 'function limpiarAbstract(' in s else s.index('function renderPapers(')
    j = s.index('\nasync function cargarResultados(', i)
    s = s[:i] + JS + s[j:]
    dst = os.path.join(R, 'publicar', f'{h}.aurzane.com', f'{h}-biblioteca.html')
    os.makedirs(os.path.dirname(dst), exist_ok=True); open(dst, 'w', encoding='utf-8').write(s); print('listo', dst)
