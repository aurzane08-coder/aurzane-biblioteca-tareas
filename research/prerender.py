"""Research Hub con contenido real dentro del HTML (sin esperar a JavaScript).

La página aurzane.com/research.html pintaba los papers con JavaScript: sin él (Google, AdSense, lectores) solo se veía
«Cargando Research Hub...» y «No encontramos papers con esa búsqueda» sin haber buscado nada. Este paso escribe en la página:
las novedades de los cinco mundos (las mismas que pide la página al entrar), el total real, la nota de acceso abierto,
búsquedas sugeridas que de verdad dan resultados (se comprueban una a una) y los años de los filtros.
Se ejecuta cada día y después de cada despliegue. Antes de cambiar la página guarda una copia en www/aurzane.com/eliminar/research-FECHA/.
Entradas: SSH, SG_DEST.
"""
import json, os, re, html, subprocess, datetime, urllib.request, urllib.parse

R = os.path.dirname(os.path.abspath(__file__))
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/biblioteca_unificada'
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'  # solo lectura de lo publicado
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
HOY = datetime.date.today(); ANIO = HOY.year
SEL = 'id,mundo,titulo,abstract,autores,anio,licencia,es_acceso_abierto,url_articulo,doi,fuente'
MUNDOS = ['mind', 'nexus', 'live', 'learn', 'build']
LABEL = {'mind': 'Mind', 'nexus': 'Nexus', 'live': 'Live', 'learn': 'Learn', 'build': 'Build'}
POR_MUNDO = 4
# (texto del botón, búsqueda en inglés): solo se muestran las que dan resultados
SUGERENCIAS = [('Salud mental', 'mental health'), ('Ansiedad', 'anxiety'), ('Sueño', 'sleep'), ('Educación', 'education'),
               ('Inteligencia artificial', 'artificial intelligence'), ('Cambio climático', 'climate change'), ('Nutrición', 'nutrition'),
               ('Adolescentes', 'adolescents'), ('Ejercicio', 'exercise'), ('Arqueología', 'archaeology'), ('Ciudades', 'urban'),
               ('Economía', 'economics'), ('Memoria', 'memory'), ('Redes sociales', 'social media')]
E = lambda s: html.escape('' if s is None else str(s), quote=True)
mil = lambda n: f'{n:,}'.replace(',', '.')


def pedir(q, contar=False):
    h = {'apikey': KEY}
    if contar: h['Prefer'] = 'count=exact'
    with urllib.request.urlopen(urllib.request.Request(f'{SB}?{q}', headers=h), timeout=60) as r:
        return json.load(r), int(r.headers.get('Content-Range', '*/0').split('/')[-1] or 0) if contar else None


def cuenta(f=''): return pedir('select=id&limit=1' + f, True)[1]


def remoto(orden, entrada=None):
    return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=120, input=entrada).stdout


def abstract_legible(t):
    """Igual que en la página: los <h4>Importance</h4> se vuelven párrafos con su título en negrita, sin HTML ajeno."""
    t = re.sub(r'<h[1-6][^>]*>([\s\S]*?)</h[1-6]>', '\u0001\\1\u0002', str(t))
    t = re.sub(r'</?(p|br|div)[^>]*>', '\n', t, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    t = re.sub(r'\u0001\s*([^\u0002]*?)\s*\u0002', lambda m: '\n\u0003' + m.group(1) + '\u0004 ', E(t))
    out = []
    for x in [x.strip() for x in t.split('\n') if x.strip()]:
        out.append('<p>' + re.sub(r'\u0003([^\u0004]*)\u0004', lambda m: '<b>' + re.sub(r'[.:]$', '', m.group(1)) + '.</b>', x, count=1) + '</p>')
    return ''.join(out)


def autores_html(a):
    if not a: return '<span class="mas">Autores no disponibles</span>'
    l = [x for x in re.split(r'\s*;\s*', a) if x]
    if len(l) <= 4: return E(', '.join(l))
    return f'{E(", ".join(l[:3]))} <button type="button" class="link-btn ver-autores" data-todos="{E(", ".join(l))}">y {len(l) - 3} autores más</button>'


def cita(p):
    l = [x for x in re.split(r'\s*;\s*', p.get('autores') or '') if x]
    aut = ', '.join(l[:3]) + ' et al.' if len(l) > 3 else ', '.join(l)
    enlace = f"https://doi.org/{p['doi']}" if p.get('doi') else (p.get('url_articulo') or '')
    return f"{aut + ' ' if aut else ''}({p.get('anio') or 's. f.'}). {re.sub(r'[.]$', '', p.get('titulo') or '')}. {enlace}".strip()


def tarjeta(p):
    link = p.get('url_articulo') or (f"https://doi.org/{p['doi']}" if p.get('doi') else '')
    link = link if link.startswith(('http://', 'https://')) else ''
    ml = LABEL.get(p['mundo'], p['mundo'])
    largo = bool(p.get('abstract')) and len(re.sub(r'<[^>]+>', '', p['abstract'])) > 320
    ida = f"abs-{E(p['id'])}-{E(p['mundo'])}"
    h = (f'<article class="paper" style="--mundo-c:var(--{E(p["mundo"])});" data-cita="{E(cita(p))}"><div class="paper-meta"><span class="badge-mundo">{ml}</span><span>{E(p.get("anio") or "s. f.")}</span>'
         + (f'<span class="sep">·</span><span>{E(p["fuente"])}</span>' if p.get('fuente') else '')
         + ('<span class="badge-oa"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>Acceso abierto</span>' if p.get('es_acceso_abierto') else '')
         + (f'<span>{E(p["licencia"].upper())}</span>' if p.get('licencia') else '') + '</div>'
         + '<h3>' + (f'<a href="{E(link)}" target="_blank" rel="noopener noreferrer">{E(p["titulo"])}</a>' if link else E(p['titulo'])) + '</h3>'
         + f'<div class="autores">{autores_html(p.get("autores"))}</div>')
    if p.get('abstract'):
        h += f'<div class="abstract{"" if largo else " corto"}" id="{ida}">{abstract_legible(p["abstract"])}</div>'
        if largo: h += f'<button type="button" class="toggle-abs" aria-expanded="false" aria-controls="{ida}">Leer resumen completo <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>'
    else:
        h += '<div class="abstract corto"><p><em>Este paper no tiene resumen disponible.</em></p></div>'
    h += '<div class="paper-foot">' + (f'<a class="doi" href="https://doi.org/{E(p["doi"])}" target="_blank" rel="noopener noreferrer">DOI {E(p["doi"])}</a>' if p.get('doi') else '<span class="doi">Sin DOI</span>')
    h += '<div class="acciones">' + (f'<button type="button" class="accion" data-copiar="{E(p["doi"])}">Copiar DOI</button>' if p.get('doi') else '') + '<button type="button" class="accion" data-copiar-cita>Copiar cita</button>'
    h += (f'<a class="accion prim" href="{E(link)}" target="_blank" rel="noopener noreferrer">Leer artículo</a>' if link else '') + '</div></div></article>'
    return h


# ---------- datos ----------
total, oa = cuenta(), cuenta('&es_acceso_abierto=eq.true')
lotes = [pedir(f'select={SEL}&mundo=eq.{m}&abstract=not.is.null&order=anio.desc.nullslast,id.desc&limit={POR_MUNDO}')[0] for m in MUNDOS]
papers = [l[i] for i in range(POR_MUNDO) for l in lotes if i < len(l)]
sug = []
for et, q in SUGERENCIAS:
    try: n = cuenta('&search_vector=wfts.' + urllib.parse.quote(q))
    except Exception as e: print('sugerencia', q, e); continue
    if n >= 20: sug.append((et, q, n))
sug = sug[:10]
info = {'fecha': HOY.isoformat(), 'total': total, 'acceso_abierto': oa, 'novedades': len(papers), 'sugerencias': {q: n for _, q, n in sug},
        'por_mundo': {m: cuenta(f'&mundo=eq.{m}') for m in MUNDOS}}
json.dump(info, open(os.path.join(R, 'research.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(info, ensure_ascii=False))
if not papers or not total: raise SystemExit('::error::sin papers: no se toca la página')


# ---------- página ----------
def bloque(t, ident, contenido):
    return re.sub(r'(id="' + ident + r'"[^>]*>)<!--az-pre-->[\s\S]*?<!--/az-pre-->', lambda x: x.group(1) + '<!--az-pre-->' + contenido + '<!--/az-pre-->', t, count=1)


def transforma(t):
    n = bloque(t, 'list', ''.join(map(tarjeta, papers)))
    n = re.sub(r'(<div id="list" data-total=")\d*(")', lambda x: x.group(1) + str(total) + x.group(2), n, count=1)
    n = bloque(n, 'resultCount', f'Novedades de los cinco mundos · <b>{len(papers)}</b> de {mil(total)} papers')
    n = bloque(n, 'totalStat', f'{mil(total)} papers indexados en los 5 mundos')
    nota = ('Hoy <b>todos</b> los papers del índice son de acceso abierto: puedes leerlos completos en su fuente.' if oa == total
            else f'<b>{mil(oa)}</b> de los {mil(total)} papers son de acceso abierto.')
    n = bloque(n, 'oaNota', nota)
    n = bloque(n, 'sugerencias', '<span class="lbl">Búsquedas populares:</span>' + ''.join(
        f'<a class="chip" href="?q={urllib.parse.quote_plus(q)}" data-q="{E(q)}">{E(et)}<small>{mil(c)}</small></a>' for et, q, c in sug))
    DESC = {'mind': 'Psicología y mente', 'nexus': 'Universidades y sociedad', 'live': 'Vida, salud y bienestar', 'learn': 'Educación y aprendizaje', 'build': 'Tecnología y ciudades'}
    for m, c in info['por_mundo'].items():
        n = re.sub(r'(<small data-n="' + m + r'">)[^<]*(</small>)', lambda x, m=m, c=c: x.group(1) + f'{DESC[m]} · {mil(c)} papers' + x.group(2), n, count=1)
    años = iter([ANIO - 1, ANIO - 3])
    n = re.sub(r'data-desde="\d{4}">Desde \d{4}', lambda x: (lambda a: f'data-desde="{a}">Desde {a}')(next(años)), n, count=2)
    return n


if SSH:
    arch = 'www/aurzane.com/public_html/research.html'
    t = remoto(f'cat {arch} 2>/dev/null')
    if 'id="list" data-total=' not in t: raise SystemExit('::warning::research.html todavía no tiene los huecos de prerender')
    n = transforma(t)
    if n != t:
        copia = f'www/aurzane.com/eliminar/research-{HOY.isoformat()}/research.html'
        r = remoto(f'mkdir -p "$(dirname {copia})" && cp -p {arch} {copia} && cat > {arch}.pre && mv {arch}.pre {arch} && echo OK', n)
        if 'OK' in r:
            remoto('site-tools-client domain-all update id=aurzane.com flush_cache=1 >/dev/null 2>&1; true')
            print(f'research.html: {len(papers)} novedades y {len(sug)} búsquedas sugeridas dentro de la página')
    else: print('research.html: sin cambios')
