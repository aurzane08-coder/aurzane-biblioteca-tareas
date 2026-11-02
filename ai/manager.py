# -*- coding: utf-8 -*-
"""AURZANE AI Manager · fase 1 (todo gratis).
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

# ---------- 10. Resumen ----------
nivel = 'mal' if any(p['nivel'] == 'mal' for p in problemas) else ('medio' if problemas else 'ok')
lineas = [f'Revisé {len(HOSTS)} sitios, {len(CLAVE)} páginas clave, {len(autos)} automatizaciones y las publicaciones en redes.',
          'Todo funciona bien.' if nivel == 'ok' else f'Hay {len(problemas)} avisos: ' + '; '.join(p['texto'].rstrip('.') for p in problemas[:4]) + ('…' if len(problemas) > 4 else '.'),
          f'Redes: {mk["ok_24h"]} publicaciones en 24 h' + (f' y {mk["fallos_24h"]} fallos.' if mk['fallos_24h'] else ', sin fallos.'),
          f'Errores de visitantes: {errores["total_24h"]} en 24 h.' if log else 'Errores de visitantes: el registro empieza a contar desde ahora.',
          (f'Arreglé sola {len(acciones)} cosas.' if acciones else 'No hizo falta arreglar nada.'),
          (f'Novedades anunciadas hoy: {sum(1 for n in nov if n["fecha"] == HOY)}.')]
informe = {'fecha': AHORA.isoformat(), 'estado': nivel, 'resumen': '\n'.join(lineas), 'resumen_fuente': 'automático', 'problemas': problemas, 'acciones': acciones,
           'sitios': sitios, 'paginas': paginas, 'errores': errores, 'automatizaciones': autos, 'enlaces': enlaces, 'marketing': mk, 'novedades': nov[:30], 'pagespeed': ps}
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
        txt = '🤖 AURZANE AI Manager\n' + ('✅ ' if nivel == 'ok' else '⚠️ ') + '\n'.join(lineas) + '\n\nPanel: https://aurzane.com/ai/'
        get(f'https://api.telegram.org/bot{TG}/sendMessage', {'Content-Type': 'application/json'}, datos=json.dumps({'chat_id': chat, 'text': txt[:3900], 'disable_web_page_preview': True}).encode(), metodo='POST')
print('::notice title=AI::' + lineas[1])
