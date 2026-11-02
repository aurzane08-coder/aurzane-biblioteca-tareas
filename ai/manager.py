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
ESTADO = json.load(open(os.path.join(D, 'estado.json'), encoding='utf-8')) if os.path.exists(os.path.join(D, 'estado.json')) else {}
DIARIO = os.environ.get('DIARIO') == '1' or (ESTADO.get('diario') != HOY and AHORA.hour >= 6)

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
if DIARIO:
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
# Cada propuesta se comprueba antes de llegar a la cola: tiene que tener un PDF libre que se pueda descargar,
# y si dice ser un libro tiene que tener al menos 50 páginas. Si no, la IA la descarta sola y lo apunta.
# Al aprobarla, descarga el PDF, saca la portada de la primera página y publica una ficha con lector propio.
INDEXNOW = 'bb5a4930b6afe5c8301aeafd1c898d44'
REC = OUT + '/recientes'; os.makedirs(REC + '/portadas', exist_ok=True); os.makedirs(REC + '/pdf', exist_ok=True)
TMP = '/tmp/ai/pdf'; os.makedirs(TMP, exist_ok=True)
vistos = set(leer('vistos.json', [])); aprob = leer('aprobados.json', []); apr = leer('aprendizaje.json', {})
autodesc = leer('autodescartes.json', [])
ALOJABLE = lambda lic: lic in ('cc-by', 'cc-by-sa', 'cc-by-nd', 'cc0', 'public-domain', 'pd')
def jremoto(f, d):
    t = remoto(f'cat www/aurzane.com/privado-ai/{f} 2>/dev/null')
    try: return json.loads(t) if t.strip() else d
    except Exception: return d
INTENTOS = []
def descargar(u, dest, maxmb=80):
    try:
        req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': 'application/pdf,*/*'})
        with urllib.request.urlopen(req, timeout=90) as r, open(dest, 'wb') as f:
            INTENTOS.append(f'{r.status} {r.headers.get("Content-Type", "")[:20]} {u[:110]}')
            n = 0
            while True:
                b = r.read(1 << 16)
                if not b: break
                n += len(b)
                if n > maxmb * 1048576: return 'grande'
                f.write(b)
        return 'ok' if open(dest, 'rb').read(5) == b'%PDF-' else 'nopdf'
    except Exception as e: INTENTOS.append(f'{str(e)[:40]} {u[:110]}'); return 'error'
def paginas_pdf(f):
    try:
        out = subprocess.run(['pdfinfo', f], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r'Pages:\s+(\d+)', out); return int(m.group(1)) if m else 0
    except Exception: return 0
def portada_pdf(f, dest):
    try:
        subprocess.run(['pdftoppm', '-jpeg', '-jpegopt', 'quality=82', '-f', '1', '-l', '1', '-scale-to', '600', '-singlefile', f, dest[:-4]], capture_output=True, timeout=90)
        return os.path.exists(dest) and os.path.getsize(dest) > 3000
    except Exception: return False
def pdf_en_pagina(u):
    """Busca el PDF dentro de la página del editor (meta citation_pdf_url y enlaces de descarga), siguiendo redirecciones."""
    if not u: return []
    try:
        req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'})
        with urllib.request.urlopen(req, timeout=30) as r: base = r.geturl(); b = r.read(600000)
    except Exception: return []
    if b[:5] == b'%PDF-': return [base]
    t = b.decode('utf-8', 'replace')
    c = re.findall(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', t) + re.findall(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url', t)
    c += re.findall(r'href=["\']([^"\']+(?:\.pdf(?:\?[^"\']*)?|/download/[^"\']*|bitstream/[^"\']+|/pdf/?|/epdf/?))["\']', t, re.I)[:8]
    return [urllib.parse.urljoin(base, html.unescape(x)) for x in c]
def candidatos_pdf(p):
    c = [x for x in [p.get('pdf')] + p.get('pdfs', []) if x and 'europepmc.org/articles' not in x and 'ncbi.nlm.nih.gov' not in x]
    if p['tipo'] == 'estudio' and p['id'].startswith('pmc-'):
        st, b, _, _ = get('https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=' + p['id'][4:] + '.', t=30)
        ks = sorted(re.findall(r'<Key>([^<]+\.pdf)</Key>', b.decode('utf-8', 'replace'))) if st == 200 else []
        if ks: c.insert(0, 'https://pmc-oa-opendata.s3.amazonaws.com/' + ks[-1])
    if p.get('ia'):
        st, b, _, _ = get('https://archive.org/metadata/' + p['ia'], t=30)
        try:
            fs = [f for f in json.loads(b).get('files', []) if f.get('name', '').lower().endswith('.pdf')]
            fs.sort(key=lambda f: (f.get('format') != 'Text PDF', -int(f.get('size') or 0)))
            if fs: c.insert(0, f'https://archive.org/download/{p["ia"]}/' + urllib.parse.quote(fs[0]['name']))
        except Exception: pass
    doi = p.get('doi') or ''
    if doi.startswith('10.1007/') or doi.startswith('10.1186/'): c.append(f'https://link.springer.com/content/pdf/{doi}.pdf')
    if doi.startswith('10.3389/'): c.append(f'https://www.frontiersin.org/articles/{doi}/pdf')
    if doi.startswith('10.1371/'): c.append(f'https://journals.plos.org/plosone/article/file?id={doi}&type=printable')
    return list(dict.fromkeys(c))
def verificar(p, guardar_pdf=False):
    """Devuelve (ok, motivo). Rellena p['paginas'], p['portada'] y, si se pide, deja el PDF listo para publicar."""
    dest = f'{TMP}/{p["id"]}.pdf'; estado = 'nopdf'; INTENTOS.clear()
    paginas_ed = ([p['url']] + p.get('landings', []) if p['tipo'] == 'libro' and not p.get('ia') else []) + ([f'https://doi.org/{p["doi"]}'] if p.get('doi') and not p.get('ia') else [])
    for u in list(dict.fromkeys(candidatos_pdf(p) + [x for w in paginas_ed for x in pdf_en_pagina(w)]))[:10]:
        estado = descargar(u, dest)
        if estado == 'ok': p['pdf_origen'] = u; break
    if estado == 'grande': return False, 'el PDF pesa más de 80 MB'
    if estado != 'ok': return False, 'no tiene un PDF libre que se pueda descargar'
    n = paginas_pdf(dest); p['paginas'] = n
    if p['tipo'] == 'libro' and n < 50: return False, f'dice ser un libro pero el PDF solo tiene {n} páginas (es un capítulo, artículo o resumen)'
    if n < 3: return False, f'el PDF solo tiene {n} páginas'
    if portada_pdf(dest, f'{REC}/portadas/{p["id"]}.jpg'): p['portada'] = f'https://aurzane.com/biblioteca/recientes/portadas/{p["id"]}.jpg'
    if guardar_pdf and ALOJABLE(p.get('lic', '')):
        os.replace(dest, f'{REC}/pdf/{p["id"]}.pdf'); p['pdf_local'] = f'https://aurzane.com/biblioteca/recientes/pdf/{p["id"]}.pdf'
    else:
        try: os.remove(dest)
        except Exception: pass
    return True, ''
def descartar_solo(p, motivo):
    vistos.add(p['id']); autodesc.insert(0, {'fecha': HOY, 'id': p['id'], 'tipo': p['tipo'], 'titulo': p['titulo'][:160], 'url': p['url'], 'motivo': motivo, 'probados': INTENTOS[:6]})
    for k in ('ed:' + (p.get('editorial') or ''),):
        a = apr.setdefault(k, [0, 0]); a[1] += 1

decis = jremoto('decisiones.json', {}); pend = jremoto('propuestas.json', [])
if ESTADO.get('reintento_pdf_1') != 'v3':
    otra = {a['id'] for a in autodesc if a['motivo'].startswith('No tiene un PDF')}
    vistos -= otra; autodesc = [a for a in autodesc if a['id'] not in otra]; ESTADO['reintento_pdf_1'] = 'v3'

canal, TGT = os.environ.get('TELEGRAM_CANAL', ''), os.environ.get('TELEGRAM_TOKEN', '')
nuevos_pub, corregidas = [], 0
for p in pend:
    d = (decis.get(p['id']) or {}).get('d')
    if d not in ('aprobar', 'descartar'): continue
    vistos.add(p['id'])
    for k in (p.get('tema') or '', 'ed:' + (p.get('editorial') or ''), 'tipo:' + p['tipo']):
        a = apr.setdefault(k, [0, 0]); a[0 if d == 'aprobar' else 1] += 1
    if d != 'aprobar': continue
    p = dict(p); ok, motivo = verificar(p, guardar_pdf=True)
    if not ok:
        descartar_solo(p, 'Aprobada, pero al publicarla ' + motivo); corregidas += 1; continue
    p['publicado'] = HOY; aprob.insert(0, p); nuevos_pub.append(p)
    nov.insert(0, {'fecha': HOY, 'url': f'https://aurzane.com/biblioteca/recientes/{p["id"]}/', 'titulo': ('Libro abierto: ' if p['tipo'] == 'libro' else 'Estudio reciente: ') + p['titulo'][:110]})
if corregidas: acciones.append(f'Frené {corregidas} aprobaciones porque al publicarlas no cumplían (sin PDF o no eran libros completos).')
if nuevos_pub:
    acciones.append(f'Publiqué {len(nuevos_pub)} propuestas que aprobaste, con portada y lector propio en aurzane.com/biblioteca/recientes.')
    if TGT and canal:
        for p in nuevos_pub[:5]:
            txt = ('📚 Libro abierto y gratuito' if p['tipo'] == 'libro' else '🔬 Estudio reciente en acceso abierto') + f'\n\n<b>{html.escape(p["titulo"])}</b>\n{html.escape(p.get("autores") or "")} ({p.get("anio") or ""})\n\nLéelo gratis en AURZANE: https://aurzane.com/biblioteca/recientes/{p["id"]}/'
            if p.get('portada'):
                get(f'https://api.telegram.org/bot{TGT}/sendPhoto', {'Content-Type': 'application/json'}, datos=json.dumps({'chat_id': canal, 'photo': p['portada'], 'caption': txt[:1000], 'parse_mode': 'HTML'}).encode(), metodo='POST')
            else:
                get(f'https://api.telegram.org/bot{TGT}/sendMessage', {'Content-Type': 'application/json'}, datos=json.dumps({'chat_id': canal, 'text': txt, 'parse_mode': 'HTML'}).encode(), metodo='POST')
            time.sleep(2)
pend = [p for p in pend if p['id'] not in vistos]
revisadas = []
for p in pend:
    if 'paginas' in p: revisadas.append(p); continue
    ok, motivo = verificar(p)
    if ok: revisadas.append(p)
    else: descartar_solo(p, motivo[0].upper() + motivo[1:])
if len(revisadas) < len(pend): acciones.append(f'Revisé de nuevo la cola y saqué {len(pend) - len(revisadas)} propuestas que no tenían PDF o no eran libros completos.')
pend = revisadas
def puntos(p):
    s = 1.0
    for k in (p.get('tema') or '', 'ed:' + (p.get('editorial') or ''), 'tipo:' + p['tipo']):
        a = apr.get(k, [0, 0]); s *= (a[0] + 1) / (a[0] + a[1] + 2) * 2
    return s * (1.3 if p.get('idioma') == 'es' else 1) * (1.2 if ALOJABLE(p.get('lic', '')) else 1)
def texto_inv(ii):
    if not ii: return ''
    pos = sorted((i, w) for w, l in ii.items() for i in l); return ' '.join(w for _, w in pos)
ya = {p['id'] for p in pend} | vistos | {p['id'] for p in aprob}
BASURA = r'resumos|anais|actas|proceedings|abstracts|congres|cadernos|libro de resúmenes|memorias del|book of abstracts|programa|boletín|newsletter|editorial board|front matter|índice'
nuevos_auto = 0
if DIARIO or len(pend) < 8:
    nuevos = []
    BUENAS = ('10.11647', '10.5334', '10.1007', '10.4324', '10.14361', '10.1515', '10.1093', '10.1017', '10.3389', '10.26530', '10.4000', '10.5772', '10.3726', '10.1201', '10.12657', '10.18148', '10.3998', '10.36253', '10.46692', '10.21827', '10.5117', '10.33776', '10.47909', '10.2478')
    desde = (AHORA - datetime.timedelta(days=5 * 365)).date().isoformat()
    MALOS = ('zenodo.org', 'figshare', 'osf.io', 'researchgate', 'academia.edu', 'preprints.org', 'ssrn.com', 'scribd')
    BIEN_HOST = re.compile(r'(\.edu(\.[a-z]{2})?|\.ac\.[a-z]{2}|uji\.es|ub\.edu|us\.es|uoc\.edu|ucm\.es|uam\.es|usal\.es|unam\.mx|uba\.ar|clacso|scielo|archive\.org|libretexts|oapen|doabooks|openedition|repositori|repositorio|ruc\.udc|digibug|riull|rua\.ua|addi\.ehu|eprints|dspace)', re.I)
    def loc_buena(l):
        u = (l.get('pdf_url') or l.get('landing_page_url') or '').lower()
        return u and not any(m in u for m in MALOS) and (l.get('pdf_url') or BIEN_HOST.search(u))
    for idioma in ('es', 'en'):
        for pag in (1, 2):
            st, b, _, _ = get('https://api.openalex.org/works?' + urllib.parse.urlencode({'filter': f'type:book,is_oa:true,primary_topic.field.id:32,language:{idioma},from_publication_date:{desde}', 'sort': 'publication_date:desc', 'per-page': 100, 'page': pag, 'mailto': 'hola@aurzane.com'}), t=60)
            for w in (json.loads(b).get('results', []) if st == 200 else []):
                doi = (w.get('doi') or '').replace('https://doi.org/', '')
                locs = [l for l in (w.get('locations') or []) if (l.get('license') or '').startswith('cc') or ((w.get('best_oa_location') or {}).get('license') or '').startswith('cc')]
                editorial_ok = doi.startswith(BUENAS) and not doi.startswith('10.5281')
                buenas = [l for l in locs if loc_buena(l)] or ([w['best_oa_location']] if editorial_ok and w.get('best_oa_location') else [])
                if not buenas: continue
                loc = buenas[0]; src = loc.get('source') or {}
                lic = loc.get('license') or (w.get('best_oa_location') or {}).get('license') or ''
                if not lic.startswith('cc'): continue
                pid = 'oa-' + w['id'].rsplit('/', 1)[1]
                if pid in ya or not w.get('title'): continue
                ya.add(pid)
                base = {'id': pid, 'tipo': 'libro', 'titulo': w['title'].strip(), 'url': loc.get('landing_page_url') or ('https://doi.org/' + doi)}
                if re.search(BASURA, w['title'], re.I): descartar_solo(base, 'el título indica actas, resúmenes o material que no es un libro'); nuevos_auto += 1; continue
                nuevos.append(dict(base, autores=', '.join(a['author']['display_name'] for a in (w.get('authorships') or [])[:3]),
                    anio=w.get('publication_year'), editorial=(w.get('primary_location') or {}).get('source', {}) and ((w['primary_location'].get('source') or {}).get('host_organization_name') or '') or src.get('display_name') or '', doi=doi,
                    pdf=loc.get('pdf_url') or '', pdfs=[l.get('pdf_url') for l in buenas if l.get('pdf_url')][:4], landings=[l.get('landing_page_url') for l in buenas if l.get('landing_page_url')][:3], lic=lic, idioma=idioma,
                    tema=(w.get('primary_topic') or {}).get('display_name', ''), resumen=texto_inv(w.get('abstract_inverted_index'))[:900],
                    motivo='Libro de psicología en acceso abierto con licencia ' + lic.upper() + ', de ' + (src.get('display_name') or 'una editorial académica') + '.'))
            time.sleep(1)
    # Internet Archive: libros de psicología con licencia Creative Commons (descargas fiables)
    for lang in ('spa', 'eng'):
        q = f'mediatype:texts AND licenseurl:*creativecommons* AND (subject:psicolog* OR subject:psychology) AND language:{lang} AND year:[2010 TO 2030]'
        st, b, _, _ = get('https://archive.org/advancedsearch.php?' + urllib.parse.urlencode([('q', q), ('fl[]', 'identifier'), ('fl[]', 'title'), ('fl[]', 'creator'), ('fl[]', 'year'), ('fl[]', 'licenseurl'), ('fl[]', 'publisher'), ('fl[]', 'description'), ('sort[]', 'addeddate desc'), ('rows', '60'), ('output', 'json')]), t=60)
        for d in (json.loads(b).get('response', {}).get('docs', []) if st == 200 else []):
            pid = 'ia-' + re.sub(r'[^A-Za-z0-9._-]', '', d['identifier'])[:80]
            if pid in ya: continue
            ya.add(pid); lu = d.get('licenseurl') or ''
            m = re.search(r'licenses/([a-z-]+)/', lu); lic = ('cc-' + m.group(1)) if m else ('cc0' if 'zero' in lu or 'publicdomain' in lu else '')
            if not lic: continue
            t = d.get('title') if isinstance(d.get('title'), str) else (d.get('title') or [''])[0]
            if not t or re.search(BASURA, t, re.I): continue
            cr = d.get('creator') or ''; cr = ', '.join(cr[:3]) if isinstance(cr, list) else cr
            ds = d.get('description') or ''; ds = ' '.join(ds) if isinstance(ds, list) else ds
            nuevos.append({'id': pid, 'tipo': 'libro', 'titulo': t.strip(), 'autores': cr, 'anio': d.get('year'), 'editorial': (d.get('publisher') if isinstance(d.get('publisher'), str) else '') or 'Internet Archive',
                'url': 'https://archive.org/details/' + d['identifier'], 'ia': d['identifier'], 'pdf': '', 'lic': lic, 'idioma': 'es' if lang == 'spa' else 'en', 'tema': 'archive:psicologia',
                'resumen': html.unescape(re.sub('<[^>]+>', ' ', ds)).strip()[:900], 'motivo': f'Libro de psicología con licencia {lic.upper()} conservado en Internet Archive.'})
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
                'anio': r.get('pubYear'), 'editorial': revista, 'doi': r.get('doi') or '', 'url': 'https://europepmc.org/article/PMC/' + r['pmcid'], 'pdf': '',
                'pdfs': [f['url'] for f in ((r.get('fullTextUrlList') or {}).get('fullTextUrl') or []) if f.get('documentStyle') == 'pdf' and f.get('site') not in ('Europe_PMC', 'PubMedCentral')][:3] + [f['url'] for f in ((r.get('fullTextUrlList') or {}).get('fullTextUrl') or []) if f.get('documentStyle') == 'doi'][:1],
                'lic': lic, 'idioma': idioma, 'tema': 'estudio:' + idioma, 'resumen': html.unescape(re.sub('<[^>]+>', ' ', r.get('abstractText', ''))).strip()[:900],
                'motivo': ('Revisión científica' if idioma == 'en' else 'Artículo') + f' en acceso abierto publicado en {revista} hace poco.'})
        time.sleep(1)
    nuevos.sort(key=puntos, reverse=True)
    lib = [x for x in nuevos if x['tipo'] == 'libro'][:22]; est = [x for x in nuevos if x['tipo'] == 'estudio'][:12]
    for x in lib + est:
        ok, motivo = verificar(x)
        if ok: pend.append(x)
        else: descartar_solo(x, motivo[0].upper() + motivo[1:]); nuevos_auto += 1
if nuevos_auto: acciones.append(f'Descarté sola {nuevos_auto} propuestas que no servían (sin PDF, capítulos sueltos o actas). Están en el admin por si quieres revisarlas.')
pend.sort(key=puntos, reverse=True); pend = pend[:60]
print('::notice title=AI::Cola ' + str(len(pend)) + ' propuestas (' + str(sum(1 for x in pend if x['tipo'] == 'libro')) + ' libros, ' + str(sum(1 for x in pend if x.get('portada'))) + ' con portada), ' + str(nuevos_auto) + ' descartadas solas')
json.dump(pend, open(OUT + '/propuestas.json', 'w', encoding='utf-8'), ensure_ascii=False)
guardar('vistos.json', sorted(vistos)[-4000:]); guardar('aprobados.json', aprob[:400]); guardar('aprendizaje.json', apr); guardar('autodescartes.json', autodesc[:300])
nov = nov[:120]; guardar('novedades.json', nov); pagina_novedades()

# ---------- Páginas públicas: índice de recientes y una ficha con lector para cada obra ----------
E = html.escape
LIC_TXT = {'cc-by': 'CC BY', 'cc-by-sa': 'CC BY-SA', 'cc-by-nd': 'CC BY-ND', 'cc-by-nc': 'CC BY-NC', 'cc-by-nc-sa': 'CC BY-NC-SA', 'cc-by-nc-nd': 'CC BY-NC-ND', 'cc0': 'CC0'}
LIC_URL = lambda l: 'https://creativecommons.org/publicdomain/zero/1.0/deed.es' if l == 'cc0' else f'https://creativecommons.org/licenses/{l[3:]}/4.0/deed.es'
CSS = ('body{margin:0;background:var(--bg,#F6F0E8);color:var(--text,#2E2620);font:16px/1.6 "Instrument Sans",system-ui,sans-serif}'
       '.h{background:#0F1530;color:#F5F3EE;padding:46px 20px 40px}.w{max-width:960px;margin:0 auto}h1{font:700 clamp(1.7rem,4vw,2.3rem)/1.15 "Bodoni Moda",serif;margin:8px 0}.h a{color:#EACF92}'
       'main{padding:24px 20px 60px}.t{display:grid;grid-template-columns:120px 1fr;gap:20px;padding:22px 0;border-bottom:1px solid rgba(95,80,68,.16)}'
       '.p{width:120px;aspect-ratio:2/3;border-radius:6px;overflow:hidden;background:linear-gradient(160deg,#1C2550,#3B2F6B);position:relative;box-shadow:0 8px 22px -10px rgba(0,0,0,.4);display:block}'
       '.p img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}.p span{position:absolute;inset:12px;color:#F5F3EE;font:600 .8rem/1.3 "Bodoni Moda",serif}.p img+span{display:none}'
       '.k{font-size:.8rem;color:#6E6257}.i{margin-left:8px;padding:1px 8px;border-radius:99px;background:rgba(95,80,68,.1)}h2{font:700 1.2rem/1.3 "Bodoni Moda",serif;margin:4px 0}h2 a{color:inherit;text-decoration:none}.a{margin:0;color:#5F5044;font-size:.92rem}'
       '.r{font-size:.92rem;margin:8px 0}.b a{color:inherit;font-weight:600;margin-right:14px}.lee{display:inline-block;background:#0F1530;color:#F5F3EE!important;padding:9px 18px;border-radius:99px;text-decoration:none}'
       '.ficha{display:grid;grid-template-columns:200px 1fr;gap:28px;align-items:start}.ficha .p{width:200px}.cred{font-size:.84rem;background:rgba(95,80,68,.07);border-radius:10px;padding:12px 14px;margin:14px 0}'
       '#lector{margin-top:28px;background:#2A2E3A;border-radius:14px;padding:12px;position:relative}#lector .bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;color:#E8E6F0;font-size:.88rem;padding:4px 4px 12px}'
       '#lector button,#lector .bar a{background:#454B5E;color:#fff;border:0;border-radius:8px;padding:7px 12px;font:600 .85rem sans-serif;cursor:pointer;text-decoration:none}#lector .pg{flex:1}'
       '#hojas{height:min(80vh,1100px);overflow:auto;border-radius:8px;background:#3A3F4E}#hojas canvas{display:block;margin:0 auto 10px;background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.35);max-width:100%;height:auto}'
       '#lector:fullscreen #hojas{height:calc(100vh - 70px)}.ext{color:#E8E6F0;padding:30px;text-align:center}.ext a{color:#EACF92}'
       '@media(max-width:640px){.t{grid-template-columns:80px 1fr;gap:14px}.p{width:80px}.ficha{grid-template-columns:1fr}.ficha .p{width:150px}}')
CAB = lambda titulo, desc, canon, img: ('<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
    '<script src="https://aurzane.com/aurzane-paleta.js"></script>'
    f'<title>{E(titulo)}</title><meta name="description" content="{E(desc[:158])}"><link rel="canonical" href="{canon}">'
    f'<meta property="og:title" content="{E(titulo)}"><meta property="og:description" content="{E(desc[:200])}"><meta property="og:url" content="{canon}">' + (f'<meta property="og:image" content="{E(img)}">' if img else '') +
    '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@600;700&family=Instrument+Sans:wght@400;600&display=swap" rel="stylesheet">'
    f'<style>{CSS}</style></head><body>')
def portada_html(p): return (f'<img src="{E(p["portada"])}" alt="Portada de {E(p["titulo"][:80])}" loading="lazy" onerror="this.remove()">' if p.get('portada') else '') + f'<span>{E(p["titulo"][:70])}</span>'
def datos(p): return ', '.join(str(v) for v in (p.get('autores'), p.get('anio'), p.get('editorial')) if v)
def pagina_recientes():
    def tarjeta(p):
        idi = '' if p.get('idioma') == 'es' else '<span class="i">En inglés</span>'
        res = f'<p class="r">{E(p["resumen"][:420])}{"…" if len(p["resumen"]) > 420 else ""}</p>' if p.get('resumen') else ''
        f = f'/biblioteca/recientes/{p["id"]}/'
        return (f'<article class="t"><a class="p" href="{f}">{portada_html(p)}</a><div>'
                f'<div class="k">{"Libro abierto" if p["tipo"] == "libro" else "Estudio reciente"} · {LIC_TXT.get(p.get("lic"), p.get("lic", "").upper())}' + (f' · {p["paginas"]} páginas' if p.get('paginas') else '') + f'{idi}</div>'
                f'<h2><a href="{f}">{E(p["titulo"])}</a></h2><p class="a">{E(datos(p))}</p>{res}<p class="b"><a class="lee" href="{f}">Leer en AURZANE</a></p></div></article>')
    cuerpo = ''.join(tarjeta(p) for p in aprob[:200]) or '<p>Muy pronto verás aquí libros abiertos y estudios recientes seleccionados.</p>'
    open(REC + '/index.html', 'w', encoding='utf-8').write(CAB('Libros abiertos y estudios recientes de psicología | AURZANE', 'Libros de psicología en acceso abierto y estudios recientes con licencia libre, seleccionados por AURZANE. Gratis y legales, para leer en la web.', 'https://aurzane.com/biblioteca/recientes/', aprob[0].get('portada', '') if aprob else '') +
        '<div class="h"><div class="w"><a href="https://aurzane.com/biblioteca/">Biblioteca AURZANE</a><h1>Libros abiertos y estudios recientes</h1>'
        '<p>Psicología en acceso abierto: libros con licencia libre y revisiones científicas recién publicadas, para leer aquí mismo. Todo es legal y gratuito. <a href="https://aurzane.com/novedades/">Ver todas las novedades</a>.</p></div></div>'
        f'<main class="w">{cuerpo}</main></body></html>')
    mapa = ''.join(f'<url><loc>https://aurzane.com/biblioteca/recientes/{p["id"]}/</loc><lastmod>{p.get("publicado", HOY)}</lastmod></url>' for p in aprob[:400])
    open(REC + '/sitemap.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aurzane.com/biblioteca/recientes/</loc></url>' + mapa + '</urlset>')
    for p in aprob[:400]:
        d = f'{REC}/{p["id"]}'; os.makedirs(d, exist_ok=True)
        lic = p.get('lic', ''); lt = LIC_TXT.get(lic, lic.upper())
        pdf = p.get('pdf_local') or ''
        lector = ('<div id="lector"><div class="bar"><span class="pg" id="pg">Cargando el libro…</span><button id="menos" aria-label="Reducir">−</button><button id="mas" aria-label="Ampliar">+</button>'
                  f'<button id="full">Pantalla completa</button><a href="{E(pdf)}" download>Descargar PDF</a></div><div id="hojas" tabindex="0" aria-label="Páginas del documento"></div></div>'
                  '<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script><script>'
                  "(function(){var L=window.pdfjsLib;if(!L){document.getElementById('pg').textContent='No se pudo cargar el lector. Puedes descargar el PDF.';return;}"
                  "L.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';"
                  "var H=document.getElementById('hojas'),pg=document.getElementById('pg'),esc=1,doc,obs,hechas={};"
                  "function ancho(){return Math.min(H.clientWidth-16,1000);}"
                  "function pinta(c){var n=+c.dataset.n;if(hechas[n]===esc)return;hechas[n]=esc;doc.getPage(n).then(function(p){var v=p.getViewport({scale:1}),s=ancho()*esc/v.width*(window.devicePixelRatio||1),vp=p.getViewport({scale:s});c.width=vp.width;c.height=vp.height;c.style.width=(ancho()*esc)+'px';p.render({canvasContext:c.getContext('2d'),viewport:vp});});}"
                  "function monta(){H.innerHTML='';hechas={};if(obs)obs.disconnect();obs=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){pinta(e.target);pg.textContent='Página '+e.target.dataset.n+' de '+doc.numPages;}});},{root:H,rootMargin:'600px 0px'});"
                  "doc.getPage(1).then(function(p){var v=p.getViewport({scale:1}),h=ancho()*esc*v.height/v.width;for(var i=1;i<=doc.numPages;i++){var c=document.createElement('canvas');c.dataset.n=i;c.style.width=(ancho()*esc)+'px';c.style.height=h+'px';c.setAttribute('aria-label','Página '+i);H.appendChild(c);obs.observe(c);}});}"
                  f"L.getDocument({json.dumps(pdf)}).promise.then(function(d){{doc=d;pg.textContent=d.numPages+' páginas';monta();}}).catch(function(){{pg.textContent='No se pudo abrir el PDF aquí. Usa Descargar PDF.';}});"
                  "document.getElementById('mas').onclick=function(){esc=Math.min(esc+.25,3);monta();};document.getElementById('menos').onclick=function(){esc=Math.max(esc-.25,.5);monta();};"
                  "document.getElementById('full').onclick=function(){var l=document.getElementById('lector');(document.fullscreenElement?document.exitFullscreen():l.requestFullscreen&&l.requestFullscreen());};"
                  "})();</script>") if pdf else (
                  f'<div id="lector"><div class="ext">Esta obra tiene licencia {E(lt)} (uso no comercial), así que la enlazamos en su sitio original en lugar de alojarla.<br><br>'
                  f'<a class="lee" href="{E(p.get("pdf_origen") or p["url"])}" target="_blank" rel="noopener">Leer gratis en el sitio original</a></div></div>')
        desc = (p.get('resumen') or f'{p["titulo"]}. {datos(p)}. Gratis y en acceso abierto.')
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'Book' if p['tipo'] == 'libro' else 'ScholarlyArticle', 'name': p['titulo'], 'author': [{'@type': 'Person', 'name': a} for a in (p.get('autores') or '').split(', ') if a and a != 'y otros'],
                         'datePublished': str(p.get('anio') or ''), 'publisher': p.get('editorial') or None, 'license': LIC_URL(lic) if lic.startswith('cc') else None, 'isAccessibleForFree': True, 'image': p.get('portada') or None, 'url': f'https://aurzane.com/biblioteca/recientes/{p["id"]}/'}, ensure_ascii=False)
        open(d + '/index.html', 'w', encoding='utf-8').write(CAB(f'{p["titulo"][:90]} | Leer gratis en AURZANE', desc, f'https://aurzane.com/biblioteca/recientes/{p["id"]}/', p.get('portada', '')) +
            f'<script type="application/ld+json">{ld}</script>'
            f'<div class="h"><div class="w"><a href="/biblioteca/recientes/">Libros abiertos y estudios recientes</a></div></div><main class="w"><div class="ficha"><div class="p">{portada_html(p)}</div><div>'
            f'<div class="k">{"Libro abierto" if p["tipo"] == "libro" else "Estudio reciente"} · {E(lt)}' + (f' · {p["paginas"]} páginas' if p.get('paginas') else '') + ('' if p.get('idioma') == 'es' else '<span class="i">En inglés</span>') + '</div>'
            f'<h1 style="color:inherit">{E(p["titulo"])}</h1><p class="a">{E(datos(p))}</p>' + (f'<p class="r">{E(p["resumen"])}</p>' if p.get('resumen') else '') +
            f'<div class="cred">Obra de {E(p.get("autores") or "sus autores")}' + (f', publicada por {E(p["editorial"])}' if p.get('editorial') else '') + f' con licencia <a href="{LIC_URL(lic)}" target="_blank" rel="noopener license">{E(lt)}</a>. '
            f'AURZANE la ofrece sin modificaciones. <a href="{E(p["url"])}" target="_blank" rel="noopener">Ficha original</a>.</div>'
            f'<p class="b"><a class="lee" href="#lector">Empezar a leer</a></p></div></div>{lector}</main></body></html>')
pagina_recientes()

# ---------- 13. IndexNow: avisa a Bing, Yandex y otros buscadores de las páginas nuevas (gratis) ----------
nuevas = sorted({n['url'].split('#')[0] for n in nov if n['fecha'] == HOY})
if nuevas:
    por_host = collections.defaultdict(set)
    for u in nuevas: por_host[urllib.parse.urlparse(u).hostname].add(u)
    for h, us in por_host.items():
        st, _, _, _ = get('https://api.indexnow.org/indexnow', {'Content-Type': 'application/json; charset=utf-8'}, datos=json.dumps({'host': h, 'key': INDEXNOW, 'keyLocation': f'https://{h}/{INDEXNOW}.txt', 'urlList': sorted(us)[:1000]}).encode(), metodo='POST')
        print('::notice title=AI::IndexNow ' + h + ' ' + str(st))

# ---------- 14. Dominio, seguridad y SEO básico (gratis) ----------
dominio = {}
st, b, _, _ = get('https://rdap.org/domain/aurzane.com', t=30)
try:
    ev = {e['eventAction']: e['eventDate'] for e in json.loads(b).get('events', [])} if st == 200 else {}
    if ev.get('expiration'):
        fin = datetime.datetime.fromisoformat(ev['expiration'].replace('Z', '+00:00')); dominio = {'caduca': fin.date().isoformat(), 'dias': (fin - AHORA).days}
        if dominio['dias'] < 30: aviso('mal' if dominio['dias'] < 10 else 'medio', f'El dominio aurzane.com caduca en {dominio["dias"]} días. Renuévalo.')
except Exception as e: print('rdap', e)
seguridad = []
CABS = [('strict-transport-security', 'Obliga a usar HTTPS (HSTS)'), ('x-content-type-options', 'Evita que el navegador adivine tipos de archivo'), ('referrer-policy', 'Controla qué datos de origen se comparten'), ('x-frame-options', 'Impide que otras webs incrusten la tuya')]
for h in HOSTS[:6]:
    st, _, _, cab = get(f'https://{h}/')
    faltan = [d for k, d in CABS if not (cab or {}).get(k)] if st == 200 else []
    seguridad.append({'host': h, 'faltan': faltan, 'nivel': 'ok' if not faltan else ('medio' if len(faltan) < 3 else 'mal')})
seo = []
for u in CLAVE:
    st, b, _, _ = get(u); t = b.decode('utf-8', 'replace') if st == 200 else ''
    if not t: continue
    m = re.search(r'<title>([^<]*)</title>', t); tl = len(html.unescape(m.group(1))) if m else 0
    f = [x for x, ok in (('imagen para redes (og:image)', 'og:image' in t), ('un título H1', re.search(r'<h1[\s>]', t)), ('URL canónica', 'rel="canonical"' in t), ('título de longitud correcta', 15 <= tl <= 70)) if not ok]
    seo.append({'url': u, 'faltan': f, 'nivel': 'ok' if not f else 'medio'})

# ---------- 10. Resumen ----------
nivel = 'mal' if any(p['nivel'] == 'mal' for p in problemas) else ('medio' if problemas else 'ok')
lineas = [f'Revisé {len(HOSTS)} sitios, {len(CLAVE)} páginas clave, {len(autos)} automatizaciones y las publicaciones en redes.',
          'Todo funciona bien.' if nivel == 'ok' else f'Hay {len(problemas)} avisos: ' + '; '.join(p['texto'].rstrip('.') for p in problemas[:4]) + ('…' if len(problemas) > 4 else '.'),
          f'Redes: {mk["ok_24h"]} publicaciones en 24 h' + (f' y {mk["fallos_24h"]} fallos.' if mk['fallos_24h'] else ', sin fallos.'),
          f'Errores de visitantes: {errores["total_24h"]} en 24 h.' if log else 'Errores de visitantes: el registro empieza a contar desde ahora.',
          (f'Arreglé sola {len(acciones)} cosas.' if acciones else 'No hizo falta arreglar nada.'),
          (f'Novedades anunciadas hoy: {sum(1 for n in nov if n["fecha"] == HOY)}.'),
          (f'Cola: {len(pend)} propuestas por revisar en el admin.' if pend else 'Cola de propuestas vacía.')]
hist = leer('historial.json', [])
hist.append({'fecha': AHORA.isoformat()[:16], 'estado': nivel, 'avisos': len(problemas), 'arreglos': len(acciones), 'errores_24h': errores['total_24h'], 'redes_ok_24h': mk['ok_24h'], 'cola': len(pend), 'publicados': len(aprob)})
guardar('historial.json', hist[-400:])
if DIARIO: ESTADO['diario'] = HOY
guardar('estado.json', ESTADO)
informe = {'fecha': AHORA.isoformat(), 'estado': nivel, 'resumen': '\n'.join(lineas), 'resumen_fuente': 'automático', 'problemas': problemas, 'acciones': acciones,
           'sitios': sitios, 'paginas': paginas, 'errores': errores, 'automatizaciones': autos, 'enlaces': enlaces, 'marketing': mk, 'novedades': nov[:30], 'pagespeed': ps,
           'cola': len(pend), 'aprobados_total': len(aprob), 'publicados': [{k: x.get(k) for k in ('id', 'tipo', 'titulo', 'portada', 'publicado', 'paginas', 'lic', 'pdf_local')} for x in aprob[:40]],
           'autodescartes': autodesc[:60], 'dominio': dominio, 'seguridad': seguridad, 'seo': seo, 'historial': hist[-120:], 'diario': DIARIO}
json.dump(informe, open(OUT + '/informe.json', 'w', encoding='utf-8'), ensure_ascii=False)

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
    if chat and (problemas or acciones or DIARIO):
        txt = '🤖 AURZANE AI Manager\n' + ('✅ ' if nivel == 'ok' else '⚠️ ') + '\n'.join(lineas) + '\n\nPanel: https://aurzane.com/admin.html'
        get(f'https://api.telegram.org/bot{TG}/sendMessage', {'Content-Type': 'application/json'}, datos=json.dumps({'chat_id': chat, 'text': txt[:3900], 'disable_web_page_preview': True}).encode(), metodo='POST')
print('::notice title=AI::' + lineas[1])
