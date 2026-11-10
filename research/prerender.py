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
SEL = 'id,mundo,titulo,abstract,autores,anio,licencia,es_acceso_abierto,url_articulo,doi'
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


def tarjeta(p):
    abs_ = E(p['abstract']) if p.get('abstract') else '<em style="color:var(--silver-dim);">Sin resumen disponible.</em>'
    au = p.get('autores') or ''
    au = E(au[:160] + '…' if len(au) > 160 else au) if au else 'Autores no disponibles'
    link = p.get('url_articulo') or (f"https://doi.org/{p['doi']}" if p.get('doi') else '')
    link = link if link.startswith(('http://', 'https://')) else ''
    ml = LABEL.get(p['mundo'], p['mundo'])
    return (f'<div class="paper" style="--mundo-c:var(--{E(p["mundo"])});"><div class="paper-meta"><span class="badge-mundo">{ml}</span><span>{p.get("anio") or "s/f"}</span>'
            + ('<span class="badge-oa">Acceso abierto</span>' if p.get('es_acceso_abierto') else '') + (f'<span>{E(p["licencia"].upper())}</span>' if p.get('licencia') else '')
            + f'</div><h3>{E(p["titulo"])}</h3><div class="autores">{au}</div><div class="abstract">{abs_}</div>'
            + ('<button class="toggle-abs">Ver abstract completo</button>' if p.get('abstract') and len(p['abstract']) > 260 else '')
            + f'<div class="paper-foot"><span class="mono" style="color:var(--silver-dim);">{ml}</span>'
            + (f'<a href="{E(link)}" target="_blank" rel="noopener noreferrer">Ver fuente original</a>' if link else '') + '</div></div>')


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
    n = bloque(n, 'resultCount', f'Novedades de los cinco mundos: {len(papers)} de {mil(total)} papers')
    n = bloque(n, 'totalStat', f'{mil(total)} papers indexados en los 5 mundos')
    nota = ('Todos los papers son de <b>acceso abierto</b>: puedes leerlos completos en su fuente original.' if oa == total
            else f'<b>{mil(oa)}</b> de los {mil(total)} papers son de acceso abierto.')
    n = bloque(n, 'oaNota', nota)
    n = bloque(n, 'sugerencias', '<span class="lbl">Búsquedas populares:</span>' + ''.join(
        f'<a class="chip" href="?q={urllib.parse.quote_plus(q)}" data-q="{E(q)}">{E(et)}<small>{mil(c)}</small></a>' for et, q, c in sug))
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
