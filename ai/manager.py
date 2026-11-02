# -*- coding: utf-8 -*-
"""AURZANE AI Manager · fase 2 (todo gratis).
Revisa el ecosistema, arregla solo lo seguro, anuncia las novedades y deja un informe para el panel (aurzane.com/ai/).
Lo ejecuta .github/workflows/ai-manager.yml cada 6 horas (la medición de PageSpeed, una vez al día).
Entradas por entorno: GITHUB_TOKEN, GITHUB_REPOSITORY, SSH (orden ssh lista), SG_DEST (usuario@host), TELEGRAM_TOKEN, DIARIO=1.
Salidas: /tmp/ai/informe.json, /tmp/ai/novedades/ (página y RSS), ai/historial.json y ai/urls.json en el repositorio."""
import json, os, re, ssl, socket, time, datetime, subprocess, urllib.request, urllib.parse, html, gzip, collections, csv

D = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(D)
OUT = '/tmp/ai'; os.makedirs(OUT + '/novedades', exist_ok=True)
AHORA = datetime.datetime.now(datetime.timezone.utc); HOY = AHORA.date().isoformat()
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 AurzaneAIManager/1.0'
HOSTS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
CLAVE = ['https://aurzane.com/', 'https://mind.aurzane.com/', 'https://mind.aurzane.com/ejercicios/', 'https://mind.aurzane.com/test-de-ansiedad/',
         'https://nexus.aurzane.com/universidades/', 'https://nexus.aurzane.com/universidades/que-puedo-estudiar/', 'https://nexus.aurzane.com/calculadora-nota-pau/',
         'https://live.aurzane.com/', 'https://live.aurzane.com/calculadora-imc/', 'https://learn.aurzane.com/', 'https://build.aurzane.com/', 'https://ovp.aurzane.com/',
         'https://aurzane.com/biblioteca/', 'https://aurzane.com/privacidad.html']
COMPARTIDOS = ['https://aurzane.com/aurzane-paleta.js', 'https://aurzane.com/aurzane-idiomas.js', 'https://aurzane.com/aurzane-id.js']
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
problemas, acciones = [], []

def aviso(nivel, texto): problemas.append({'nivel': nivel, 'texto': texto}); print('::notice title=AI::' + nivel + ' · ' + texto)
def leer(n, d):
    try: return json.load(open(os.path.join(D, n), encoding='utf-8'))
    except Exception: return d
def guardar(n, v): json.dump(v, open(os.path.join(D, n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
def get(url, cab=None, t=30, datos=None, metodo=None):
    h = {'User-Agent': UA}; h.update(cab or {})
    req = urllib.request.Request(url, headers=h, data=datos, method=metodo)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=t) as r:
            b = r.read()
            if r.headers.get('Content-Encoding') == 'gzip': b = gzip.decompress(b)
            return r.status, b, int((time.time() - t0) * 1000), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b'', int((time.time() - t0) * 1000), e.headers
    except Exception as e:
        return 'ERR ' + str(e)[:80], b'', int((time.time() - t0) * 1000), {}
def remoto(orden):
    if not SSH or not DEST: return ''
    try: return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=120).stdout
    except Exception as e: return ''

# ---------- 1. Sitios: respuesta y certificado ----------
def dias_ssl(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=15) as s, ctx.wrap_socket(s, server_hostname=host) as c:
            fin = datetime.datetime.strptime(c.getpeercert()['notAfter'], '%b %d %H:%M:%S %Y %Z')
            return (fin - datetime.datetime.utcnow()).days
    except Exception: return None
sitios = []
for h in HOSTS:
    st, b, ms, _ = get('https://' + h + '/')
    d = dias_ssl(h)
    nivel = 'ok' if st == 200 and ms < 3000 and (d or 0) > 14 else ('mal' if st != 200 or (d is not None and d < 7) else 'medio')
    sitios.append({'host': h, 'codigo': st, 'ms': ms, 'ssl_dias': d, 'nivel': nivel})
    if st != 200: aviso('mal', f'{h} no responde bien ({st}).')
    elif ms >= 3000: aviso('medio', f'{h} tarda {ms} ms en responder.')
    if d is not None and d < 14: aviso('mal' if d < 7 else 'medio', f'El certificado de {h} caduca en {d} días.')

# ---------- 2. Páginas clave ----------
paginas = []
for u in CLAVE:
    st, b, ms, _ = get(u)
    txt = b.decode('utf-8', 'replace')
    falta = [] if st != 200 else [x for x, ok in (('título', '<title>' in txt), ('descripción', 'name="description"' in txt)) if not ok]
    nivel = 'ok' if st == 200 and not falta else ('mal' if st != 200 else 'medio')
    paginas.append({'url': u, 'codigo': st, 'ms': ms, 'nivel': nivel})
    if st != 200: aviso('mal', f'La página {u} devuelve {st}.')
    elif falta: aviso('medio', f'A {u} le falta: {", ".join(falta)}.')

# ---------- 3. Scripts compartidos: si la caché sirve una versión vieja, se vacía ----------
viejos = []
for u in COMPARTIDOS:
    a = get(u, {'Accept-Encoding': 'identity'}); b = get(u, {'Accept-Encoding': 'gzip'})
    if a[0] == 200 and b[0] == 200 and a[1] != b[1]: viejos.append(u)
    elif a[0] != 200: aviso('mal', f'El script compartido {u} no carga ({a[0]}).')
if viejos:
    r = remoto('site-tools-client domain-all update id=aurzane.com flush_cache=1')
    acciones.append(f'Vacié la caché de aurzane.com: servía una versión antigua de {", ".join(x.rsplit("/", 1)[1] for x in viejos)}.' + ('' if 'OK' in r else ' (sin confirmación del servidor)'))

# ---------- 4. Errores de JavaScript de los visitantes ----------
errores = {'total_24h': 0, 'paginas_24h': 0, 'top': []}
log = remoto('tail -n 3000 www/aurzane.com/privado-ai/errores.log 2>/dev/null')
if log:
    corte = (AHORA - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    filas = [l.split('\t') for l in log.splitlines() if l.count('\t') >= 6]
    rec = [f for f in filas if f[0] >= corte and f[-1] != 'bot']
    errores['total_24h'] = len(rec); errores['paginas_24h'] = len({f[1] + f[2] for f in rec})
    c = collections.Counter((f[4], f[5], f[1] + f[2]) for f in rec)
    errores['top'] = [{'mensaje': m, 'archivo': s, 'pagina': p, 'veces': n} for (m, s, p), n in c.most_common(10)]
    for (m, s, p), n in c.most_common(3):
        if n >= 5: aviso('medio', f'Error repetido {n} veces en {p}: {m[:120]}')

# ---------- 5. Automatizaciones (GitHub Actions): fallos y reintento automático ----------
autos = []
GT, REPO = os.environ.get('GITHUB_TOKEN', ''), os.environ.get('GITHUB_REPOSITORY', '')
if GT and REPO:
    cab = {'Authorization': 'Bearer ' + GT, 'Accept': 'application/vnd.github+json'}
    desde = (AHORA - datetime.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
    st, b, _, _ = get(f'https://api.github.com/repos/{REPO}/actions/runs?per_page=100&created=%3E{desde}', cab)
    runs = json.loads(b or b'{}').get('workflow_runs', []) if st == 200 else []
    por = collections.defaultdict(list)
    for r in runs: por[r['name']].append(r)
    for nombre, rs in sorted(por.items()):
        hechos = [r for r in rs if r['status'] == 'completed']
        mal = [r for r in hechos if r['conclusion'] == 'failure']
        ult = hechos[0] if hechos else None
        nivel = 'ok' if not mal else ('medio' if ult and ult['conclusion'] == 'success' else 'mal')
        autos.append({'nombre': nombre, 'nivel': nivel, 'detalle': f'{len(hechos)} ejecuciones, {len(mal)} fallidas'})
        if ult and ult['conclusion'] == 'failure':
            if ult.get('run_attempt', 1) == 1 and 'AI Manager' not in nombre:
                s2, _, _, _ = get(f'https://api.github.com/repos/{REPO}/actions/runs/{ult["id"]}/rerun-failed-jobs', cab, datos=b'', metodo='POST')
                acciones.append(f'Reintenté «{nombre}», que había fallado' + (' (en marcha).' if s2 in (201, 204) else f' (no se pudo: {s2}).'))
            else:
                aviso('mal', f'La automatización «{nombre}» falla y el reintento no lo arregló.')

# ---------- 6. Enlaces rotos (revisión semanal) ----------
enl = leer('../enlaces/informe.json', {})
rotos = enl.get('rotos', []) if isinstance(enl, dict) else []
enlaces = {'rotos': len(rotos), 'revisadas': enl.get('revisadas', 0) if isinstance(enl, dict) else 0,
           'ejemplos': [(r.get('url') if isinstance(r, dict) else str(r))[:140] for r in rotos[:5]]}
if len(rotos) > 0: aviso('medio', f'Hay {len(rotos)} enlaces rotos en la última revisión semanal.')

# ---------- 7. Redes sociales ----------
mk = {'ok_24h': 0, 'fallos_24h': 0, 'por_red': {}}
try:
    ayer = (AHORA - datetime.timedelta(days=1)).date().isoformat()
    for f in csv.reader(open(os.path.join(RAIZ, 'marketing', 'registro.csv'), encoding='utf-8')):
        if len(f) < 5 or f[0] < ayer: continue
        r = mk['por_red'].setdefault(f[2], {'ok': 0, 'fallos': 0})
        if f[4] in ('ok', 'feed'): r['ok'] += 1; mk['ok_24h'] += 1
        else: r['fallos'] += 1; mk['fallos_24h'] += 1
    for red, v in mk['por_red'].items():
        if v['fallos'] and not v['ok']: aviso('mal', f'{red}: todas las publicaciones de las últimas 24 h han fallado.')
except Exception as e: print('marketing', e)

# ---------- 8. Novedades: páginas nuevas del sitemap, anunciadas solas ----------
urls_prev = set(leer('urls.json', []))
st, b, _, _ = get('https://aurzane.com/sitemap.xml')
urls = re.findall(r'<loc>([^<]+)</loc>', b.decode('utf-8', 'replace')) if st == 200 else []
nov = leer('novedades.json', [])
if urls and urls_prev:
    for u in [u for u in urls if u not in urls_prev][:40]:
        s2, b2, _, _ = get(u)
        m = re.search(r'<title>([^<]+)</title>', b2.decode('utf-8', 'replace'))
        t = html.unescape(m.group(1)).split(' | ')[0].strip() if m else u
        nov.insert(0, {'fecha': HOY, 'url': u, 'titulo': t})
if urls: guardar('urls.json', sorted(set(urls)))
nov = nov[:120]; guardar('novedades.json', nov)
def pagina_novedades():
    MUNDO = lambda u: (urllib.parse.urlparse(u).hostname.split('.')[0].upper() if urllib.parse.urlparse(u).hostname != 'aurzane.com' else 'AURZANE')
    items = ''.join(f'<li><span class="f">{datetime.date.fromisoformat(n["fecha"]).strftime("%d/%m/%Y")}</span><span class="m">{MUNDO(n["url"])}</span><a href="{html.escape(n["url"])}">{html.escape(n["titulo"])}</a></li>' for n in nov[:80])
    vacio = '' if nov else '<p>Muy pronto verás aquí todo lo nuevo de AURZANE.</p>'
    pag = f'''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>Novedades de AURZANE: tests, herramientas y contenidos nuevos</title>
<meta name="description" content="Todo lo nuevo de AURZANE: tests, calculadoras, ejercicios guiados, cursos, libros y artículos, actualizado automáticamente.">
<link rel="canonical" href="https://aurzane.com/novedades/"><link rel="alternate" type="application/rss+xml" title="Novedades de AURZANE" href="https://aurzane.com/novedades/feed.xml">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@600;700&family=Instrument+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>body{{margin:0;background:var(--bg,#F6F0E8);color:var(--text,#2E2620);font:16px/1.6 "Instrument Sans",system-ui,sans-serif}}
.h{{background:#0F1530;color:#F5F3EE;padding:46px 20px 40px}}.w{{max-width:860px;margin:0 auto}}h1{{font:700 2.3rem "Bodoni Moda",serif;margin:8px 0}}.h a{{color:#EACF92}}
ul{{list-style:none;padding:0;margin:28px 0}}li{{display:grid;grid-template-columns:100px 80px 1fr;gap:10px;padding:12px 0;border-bottom:1px solid rgba(95,80,68,.16);align-items:baseline}}
.f{{color:#6E6257;font-size:.88rem}}.m{{font-size:.75rem;font-weight:700;letter-spacing:.06em;color:#5F5044}}li a{{color:inherit;font-weight:600;text-decoration:none}}li a:hover{{text-decoration:underline}}
@media(max-width:600px){{li{{grid-template-columns:1fr}}}}</style></head><body>
<div class="h"><div class="w"><a href="https://aurzane.com/">AURZANE</a><h1>Novedades</h1><p>Todo lo nuevo del ecosistema, en cuanto se publica. <a href="/novedades/feed.xml">Suscríbete por RSS</a>.</p></div></div>
<main class="w" style="padding:0 20px">{vacio}<ul>{items}</ul></main></body></html>'''
    open(OUT + '/novedades/index.html', 'w', encoding='utf-8').write(pag)
    rss = ''.join(f'<item><title>{html.escape(n["titulo"])}</title><link>{html.escape(n["url"])}</link><guid>{html.escape(n["url"])}</guid><pubDate>{datetime.datetime.fromisoformat(n["fecha"]).strftime("%a, %d %b %Y 08:00:00 +0000")}</pubDate></item>' for n in nov[:40])
    open(OUT + '/novedades/feed.xml', 'w', encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Novedades de AURZANE</title><link>https://aurzane.com/novedades/</link><description>Lo nuevo de AURZANE</description><language>es</language>{rss}</channel></rss>')
pagina_novedades()

# ---------- 9. Velocidad (PageSpeed Insights, gratis), una vez al día ----------
ps = leer('pagespeed.json', [])
if os.environ.get('DIARIO') == '1':
    ps = []
    for u in ['https://aurzane.com/', 'https://mind.aurzane.com/test-de-ansiedad/', 'https://nexus.aurzane.com/universidades/', 'https://live.aurzane.com/calculadora-imc/']:
        q = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urllib.parse.urlencode([('url', u), ('strategy', 'mobile'), ('category', 'performance'), ('category', 'seo'), ('category', 'accessibility')])
        st, b, _, _ = get(q, t=120)
        if st != 200: continue
        c = json.loads(b).get('lighthouseResult', {}).get('categories', {})
        f = lambda k: round((c.get(k, {}).get('score') or 0) * 100)
        ps.append({'url': u, 'rendimiento': f('performance'), 'seo': f('seo'), 'accesibilidad': f('accessibility')})
        if f('performance') < 50: aviso('medio', f'{u} va lenta en móvil (rendimiento {f("performance")}/100).')
        time.sleep(3)
    if ps: guardar('pagespeed.json', ps)

# ---------- 12. Cola de propuestas: libros abiertos y estudios recientes (aprende de tus decisiones) ----------
INDEXNOW = 'bb5a4930b6afe5c8301aeafd1c898d44'
vistos = set(leer('vistos.json', [])); aprob = leer('aprobados.json', []); apr = leer('aprendizaje.json', {})
def jremoto(f, d):
    t = remoto(f'cat www/aurzane.com/privado-ai/{f} 2>/dev/null')
    try: return json.loads(t) if t.strip() else d
    except Exception: return d
decis = jremoto('decisiones.json', {}); pend = jremoto('propuestas.json', [])
canal, TGT = os.environ.get('TELEGRAM_CANAL', ''), os.environ.get('TELEGRAM_TOKEN', '')
nuevos_pub = []
for p in pend:
    d = (decis.get(p['id']) or {}).get('d')
    if d not in ('aprobar', 'descartar'): continue
    vistos.add(p['id'])
    for k in (p.get('tema') or '', 'ed:' + (p.get('editorial') or ''), 'tipo:' + p['tipo']):
        a = apr.setdefault(k, [0, 0]); a[0 if d == 'aprobar' else 1] += 1
    if d == 'aprobar':
        p = dict(p, publicado=HOY); aprob.insert(0, p); nuevos_pub.append(p)
        nov.insert(0, {'fecha': HOY, 'url': 'https://aurzane.com/biblioteca/recientes/#' + p['id'], 'titulo': ('Libro abierto: ' if p['tipo'] == 'libro' else 'Estudio reciente: ') + p['titulo'][:110]})
if nuevos_pub:
    acciones.append(f'Publiqué {len(nuevos_pub)} propuestas que aprobaste en aurzane.com/biblioteca/recientes.')
    if TGT and canal:
        for p in nuevos_pub[:5]:
            txt = ('📚 Libro abierto y gratuito' if p['tipo'] == 'libro' else '🔬 Estudio reciente en acceso abierto') + f'\n\n<b>{html.escape(p["titulo"])}</b>\n{html.escape(p.get("autores") or "")} ({p.get("anio") or ""})\n\nLéelo gratis: {p.get("pdf") or p["url"]}\nMás en https://aurzane.com/biblioteca/recientes/'
            get(f'https://api.telegram.org/bot{TGT}/sendMessage', {'Content-Type': 'application/json'}, datos=json.dumps({'chat_id': canal, 'text': txt, 'parse_mode': 'HTML'}).encode(), metodo='POST'); time.sleep(2)
pend = [p for p in pend if p['id'] not in vistos]
def puntos(p):
    s = 1.0
    for k in (p.get('tema') or '', 'ed:' + (p.get('editorial') or ''), 'tipo:' + p['tipo']):
        a = apr.get(k, [0, 0]); s *= (a[0] + 1) / (a[0] + a[1] + 2) * 2
    return s * (1.3 if p.get('idioma') == 'es' else 1)
def og_imagen(u):
    st, b, _, _ = get(u, t=15)
    if st != 200: return ''
    m = re.search(rb'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)', b[:200000]) or re.search(rb'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image', b[:200000])
    x = html.unescape(m.group(1).decode('utf-8', 'replace')) if m else ''
    return x if x.startswith('https://') and not re.search(r'logo|favicon|default', x, re.I) else ''
def texto_inv(ii):
    if not ii: return ''
    pos = sorted((i, w) for w, l in ii.items() for i in l); return ' '.join(w for _, w in pos)
ya = {p['id'] for p in pend} | vistos | {p['id'] for p in aprob}
if os.environ.get('DIARIO') == '1' or len(pend) < 8:
    nuevos = []
    BUENAS = ('10.11647', '10.5334', '10.1007', '10.4324', '10.14361', '10.1515', '10.1093', '10.1017', '10.3389', '10.26530', '10.4000', '10.5772', '10.3726', '10.1201', '10.12657', '10.18148', '10.3998', '10.36253', '10.46692', '10.21827', '10.5117', '10.33776', '10.47909', '10.2478')
    desde = (AHORA - datetime.timedelta(days=730)).date().isoformat()
    for idioma in ('es', 'en'):
        st, b, _, _ = get('https://api.openalex.org/works?' + urllib.parse.urlencode({'filter': f'type:book,is_oa:true,primary_topic.field.id:32,language:{idioma},from_publication_date:{desde}', 'sort': 'publication_date:desc', 'per-page': 100, 'mailto': 'hola@aurzane.com'}), t=60)
        for w in (json.loads(b).get('results', []) if st == 200 else []):
            loc = w.get('best_oa_location') or {}; src = loc.get('source') or {}; doi = (w.get('doi') or '').replace('https://doi.org/', '')
            lic = loc.get('license') or ''
            if not lic.startswith('cc') or not doi or src.get('type') == 'repository' or not (doi.startswith(BUENAS) or src.get('type') in ('book series', 'ebook platform')): continue
            pid = 'oa-' + w['id'].rsplit('/', 1)[1]
            if pid in ya or not w.get('title'): continue
            ya.add(pid); res = texto_inv(w.get('abstract_inverted_index'))
            nuevos.append({'id': pid, 'tipo': 'libro', 'titulo': w['title'].strip(), 'autores': ', '.join(a['author']['display_name'] for a in (w.get('authorships') or [])[:3]),
                'anio': w.get('publication_year'), 'editorial': src.get('host_organization_name') or src.get('display_name') or '', 'url': loc.get('landing_page_url') or ('https://doi.org/' + doi),
                'pdf': loc.get('pdf_url') or '', 'lic': lic, 'idioma': idioma, 'tema': (w.get('primary_topic') or {}).get('display_name', ''), 'resumen': res[:900],
                'motivo': 'Libro de psicología en acceso abierto con licencia ' + lic.upper() + ', de ' + (src.get('host_organization_name') or 'una editorial académica') + '.'})
        time.sleep(1)
    for q, idioma, dias in (('(TITLE:"ansiedad" OR TITLE:"depresión" OR TITLE:"psicoterapia" OR TITLE:"estrés" OR TITLE:"salud mental" OR TITLE:"bienestar")', 'es', 120),
                            ('(TITLE:"anxiety" OR TITLE:"depression" OR TITLE:"psychotherapy" OR TITLE:"mindfulness" OR TITLE:"burnout" OR TITLE:"insomnia" OR TITLE:"loneliness" OR TITLE:"resilience" OR TITLE:"self-esteem") AND (PUB_TYPE:"review" OR PUB_TYPE:"systematic-review" OR PUB_TYPE:"meta-analysis")', 'en', 21)):
        desde2 = (AHORA - datetime.timedelta(days=dias)).date().isoformat()
        st, b, _, _ = get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query': f'OPEN_ACCESS:y AND {q} AND FIRST_PDATE:[{desde2} TO {HOY}]', 'format': 'json', 'pageSize': 40, 'resultType': 'core'}), t=60)
        for r in (json.loads(b).get('resultList', {}).get('result', []) if st == 200 else []):
            lic = (r.get('license') or '').lower().replace(' ', '-')
            if not r.get('pmcid') or not lic.startswith('cc'): continue
            pid = 'pmc-' + r['pmcid']
            if pid in ya: continue
            ya.add(pid); revista = ((r.get('journalInfo') or {}).get('journal') or {}).get('title', '')
            au = (r.get('authorString') or '').rstrip('.').split(', '); au = ', '.join(au[:3]) + (' y otros' if len(au) > 3 else '')
            nuevos.append({'id': pid, 'tipo': 'estudio', 'titulo': html.unescape(re.sub('<[^>]+>', '', r.get('title', ''))).strip().strip('[]').rstrip('.'), 'autores': au,
                'anio': r.get('pubYear'), 'editorial': revista, 'url': 'https://europepmc.org/article/PMC/' + r['pmcid'], 'pdf': f'https://europepmc.org/articles/{r["pmcid"]}?pdf=render',
                'lic': lic, 'idioma': idioma, 'tema': 'estudio:' + idioma, 'resumen': html.unescape(re.sub('<[^>]+>', ' ', r.get('abstractText', ''))).strip()[:900],
                'motivo': ('Revisión científica' if idioma == 'en' else 'Artículo') + f' en acceso abierto publicado en {revista} hace poco.'})
        time.sleep(1)
    nuevos.sort(key=puntos, reverse=True)
    lib = [x for x in nuevos if x['tipo'] == 'libro'][:12]; est = [x for x in nuevos if x['tipo'] == 'estudio'][:12]
    for x in lib: x['portada'] = og_imagen(x['url'])
    pend += lib + est
pend.sort(key=puntos, reverse=True); pend = pend[:60]
json.dump(pend, open(OUT + '/propuestas.json', 'w', encoding='utf-8'), ensure_ascii=False)
guardar('vistos.json', sorted(vistos)[-3000:]); guardar('aprobados.json', aprob[:400]); guardar('aprendizaje.json', apr)
nov = nov[:120]; guardar('novedades.json', nov); pagina_novedades()

def pagina_recientes():
    os.makedirs(OUT + '/recientes', exist_ok=True)
    E = html.escape
    def tarjeta(p):
        port = f'<img src="{E(p["portada"])}" alt="" loading="lazy" onerror="this.parentNode.classList.add(\'sin\');this.remove()">' if p.get('portada') else ''
        idi = '' if p.get('idioma') == 'es' else '<span class="i">En inglés</span>'
        datos = ', '.join(str(v) for v in (p.get('autores'), p.get('anio'), p.get('editorial')) if v)
        res = f'<p class="r">{E(p["resumen"][:520])}{"…" if len(p["resumen"]) > 520 else ""}</p>' if p.get('resumen') else ''
        return (f'<article id="{E(p["id"])}" class="t"><div class="p{"" if port else " sin"}">{port}<span>{E(p["titulo"][:70])}</span></div><div class="x">'
                f'<div class="k">{"Libro abierto" if p["tipo"] == "libro" else "Estudio reciente"} · {E(p.get("lic", "").upper())}{idi}</div><h2>{E(p["titulo"])}</h2>'
                f'<p class="a">{E(datos)}</p>{res}'
                f'<p class="b"><a class="lee" href="{E(p.get("pdf") or p["url"])}" target="_blank" rel="noopener">Leer gratis</a> <a href="{E(p["url"])}" target="_blank" rel="noopener">Ficha original</a></p></div></article>')
    cuerpo = ''.join(tarjeta(p) for p in aprob[:200]) or '<p>Muy pronto verás aquí libros abiertos y estudios recientes seleccionados.</p>'
    css = ('body{margin:0;background:var(--bg,#F6F0E8);color:var(--text,#2E2620);font:16px/1.6 "Instrument Sans",system-ui,sans-serif}'
           '.h{background:#0F1530;color:#F5F3EE;padding:46px 20px 40px}.w{max-width:920px;margin:0 auto}h1{font:700 2.2rem/1.15 "Bodoni Moda",serif;margin:8px 0}.h a{color:#EACF92}'
           'main{padding:24px 20px 60px}.t{display:grid;grid-template-columns:120px 1fr;gap:20px;padding:22px 0;border-bottom:1px solid rgba(95,80,68,.16);scroll-margin-top:20px}'
           '.p{width:120px;aspect-ratio:2/3;border-radius:6px;overflow:hidden;background:linear-gradient(160deg,#1C2550,#3B2F6B);position:relative;box-shadow:0 8px 22px -10px rgba(0,0,0,.4)}'
           '.p img{width:100%;height:100%;object-fit:cover;display:block}.p span{display:none}.p.sin span{display:block;position:absolute;inset:12px;color:#F5F3EE;font:600 .8rem/1.3 "Bodoni Moda",serif}'
           '.k{font-size:.8rem;color:#6E6257}.i{margin-left:8px;padding:1px 8px;border-radius:99px;background:rgba(95,80,68,.1)}h2{font:700 1.2rem/1.3 "Bodoni Moda",serif;margin:4px 0}.a{margin:0;color:#5F5044;font-size:.92rem}'
           '.r{font-size:.92rem;margin:8px 0}.b a{color:inherit;font-weight:600;margin-right:14px}.b .lee{display:inline-block;background:#0F1530;color:#F5F3EE;padding:8px 16px;border-radius:99px;text-decoration:none}'
           '@media(max-width:600px){.t{grid-template-columns:80px 1fr;gap:14px}.p{width:80px}}')
    pag = ('<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
           '<script src="https://aurzane.com/aurzane-paleta.js"></script>'
           '<title>Libros abiertos y estudios recientes de psicología | AURZANE</title>'
           '<meta name="description" content="Libros de psicología en acceso abierto y estudios recientes con licencia libre, seleccionados por AURZANE. Gratis y legales para leer y descargar.">'
           '<link rel="canonical" href="https://aurzane.com/biblioteca/recientes/"><meta property="og:title" content="Libros abiertos y estudios recientes de psicología">'
           '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@600;700&family=Instrument+Sans:wght@400;600&display=swap" rel="stylesheet">'
           f'<style>{css}</style></head><body>'
           '<div class="h"><div class="w"><a href="https://aurzane.com/biblioteca/">Biblioteca AURZANE</a><h1>Libros abiertos y estudios recientes</h1>'
           '<p>Selección de psicología en acceso abierto: libros con licencia libre y revisiones científicas recién publicadas. Todo es legal y gratuito. <a href="https://aurzane.com/novedades/">Ver todas las novedades</a>.</p></div></div>'
           f'<main class="w">{cuerpo}</main></body></html>')
    open(OUT + '/recientes/index.html', 'w', encoding='utf-8').write(pag)
pagina_recientes()

# ---------- 13. IndexNow: avisa a Bing, Yandex y otros buscadores de las páginas nuevas (gratis) ----------
nuevas = sorted({n['url'].split('#')[0] for n in nov if n['fecha'] == HOY})
if nuevas:
    por_host = collections.defaultdict(set)
    for u in nuevas: por_host[urllib.parse.urlparse(u).hostname].add(u)
    for h, us in por_host.items():
        st, _, _, _ = get('https://api.indexnow.org/indexnow', {'Content-Type': 'application/json; charset=utf-8'}, datos=json.dumps({'host': h, 'key': INDEXNOW, 'keyLocation': f'https://{h}/{INDEXNOW}.txt', 'urlList': sorted(us)[:1000]}).encode(), metodo='POST')
        print('::notice title=AI::IndexNow ' + h + ' ' + str(st))
        if st in (200, 202): acciones.append(f'Avisé a los buscadores (IndexNow) de {len(us)} páginas nuevas en {h}.')

# ---------- 10. Resumen ----------
nivel = 'mal' if any(p['nivel'] == 'mal' for p in problemas) else ('medio' if problemas else 'ok')
lineas = [f'Revisé {len(HOSTS)} sitios, {len(CLAVE)} páginas clave, {len(autos)} automatizaciones y las publicaciones en redes.',
          'Todo funciona bien.' if nivel == 'ok' else f'Hay {len(problemas)} avisos: ' + '; '.join(p['texto'].rstrip('.') for p in problemas[:4]) + ('…' if len(problemas) > 4 else '.'),
          f'Redes: {mk["ok_24h"]} publicaciones en 24 h' + (f' y {mk["fallos_24h"]} fallos.' if mk['fallos_24h'] else ', sin fallos.'),
          f'Errores de visitantes: {errores["total_24h"]} en 24 h.' if log else 'Errores de visitantes: el registro empieza a contar desde ahora.',
          (f'Arreglé sola {len(acciones)} cosas.' if acciones else 'No hizo falta arreglar nada.'),
          (f'Novedades anunciadas hoy: {sum(1 for n in nov if n["fecha"] == HOY)}.'),
          (f'Cola: {len(pend)} propuestas por revisar en el admin.' if pend else 'Cola de propuestas vacía.')]
informe = {'fecha': AHORA.isoformat(), 'estado': nivel, 'resumen': '\n'.join(lineas), 'resumen_fuente': 'automático', 'problemas': problemas, 'acciones': acciones,
           'sitios': sitios, 'paginas': paginas, 'errores': errores, 'automatizaciones': autos, 'enlaces': enlaces, 'marketing': mk, 'novedades': nov[:30], 'pagespeed': ps, 'cola': len(pend), 'aprobados_total': len(aprob)}
json.dump(informe, open(OUT + '/informe.json', 'w', encoding='utf-8'), ensure_ascii=False)

# historial público, solo con cifras (el repositorio es público)
hist = leer('historial.json', [])
hist.append({'fecha': AHORA.isoformat()[:16], 'estado': nivel, 'avisos': len(problemas), 'arreglos': len(acciones), 'errores_24h': errores['total_24h'], 'redes_ok_24h': mk['ok_24h']})
guardar('historial.json', hist[-400:])

# ---------- 11. Aviso por Telegram (cuando Adrián escribe /aurzane al bot por privado) ----------
TG = os.environ.get('TELEGRAM_TOKEN', '')
if TG:
    chat = remoto('cat www/aurzane.com/privado-ai/telegram_chat 2>/dev/null').strip()
    if not chat:
        st, b, _, _ = get(f'https://api.telegram.org/bot{TG}/getUpdates?allowed_updates=%5B%22message%22%5D')
        for u in reversed(json.loads(b or b'{}').get('result', [])) if st == 200 else []:
            m = u.get('message', {})
            if m.get('chat', {}).get('type') == 'private' and (m.get('text') or '').strip().lower().startswith('/aurzane'):
                chat = str(m['chat']['id']); remoto(f'mkdir -p www/aurzane.com/privado-ai && echo {chat} > www/aurzane.com/privado-ai/telegram_chat')
                break
    if chat and (problemas or acciones or os.environ.get('DIARIO') == '1'):
        txt = '🤖 AURZANE AI Manager\n' + ('✅ ' if nivel == 'ok' else '⚠️ ') + '\n'.join(lineas) + '\n\nPanel: https://aurzane.com/admin.html'
        get(f'https://api.telegram.org/bot{TG}/sendMessage', {'Content-Type': 'application/json'}, datos=json.dumps({'chat_id': chat, 'text': txt[:3900], 'disable_web_page_preview': True}).encode(), metodo='POST')
print('::notice title=AI::' + lineas[1])
