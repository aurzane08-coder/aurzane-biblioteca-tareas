"""Revisa enlaces internos de todos los sitios AURZANE. Salida: enlaces/informe.json"""
import re, json, random, urllib.request, urllib.parse, html, concurrent.futures as cf, threading, collections
SITIOS = ['https://aurzane.com/', 'https://mind.aurzane.com/', 'https://ovp.aurzane.com/', 'https://nexus.aurzane.com/',
          'https://live.aurzane.com/', 'https://learn.aurzane.com/', 'https://build.aurzane.com/']
UA = 'Mozilla/5.0 (compatible; AurzaneLinkCheck/1.0)'
estado, lock = {}, threading.Lock()
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=30)
        ct = r.headers.get('content-type', '')
        body = r.read(3_000_000).decode('utf-8', 'replace') if 'html' in ct else ''
        return r.status, r.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, u, ''
    except Exception as e:
        return 'ERR ' + str(e)[:60], u, ''
def interno(u):
    h = urllib.parse.urlparse(u).hostname or ''
    return h == 'aurzane.com' or h.endswith('.aurzane.com')
def muestra(path):
    # páginas masivas: revisar una muestra
    if re.match(r'^/universidades/[^/]+/[^/]+/$', path) and '/ciudad/' not in path and path.split('/')[2] not in ('paises','acerca','mi-lista'):
        return random.random() < 0.02
    if re.match(r'^/(biblioteca|articulos|temas)/.+', path):
        return random.random() < 0.08
    return True
paginas, cola, vistos = 0, list(SITIOS), set(SITIOS)
roto = []
origen = collections.defaultdict(list)
with cf.ThreadPoolExecutor(16) as ex:
    while cola and paginas < 2500:
        lote, cola = cola[:64], cola[64:]
        for u, (st, final, body) in zip(lote, ex.map(get, lote)):
            estado[u] = st
            if st != 200:
                continue
            if not body:
                continue
            paginas += 1
            for m in re.finditer(r'(?:href|src)\s*=\s*"([^"#]+)', body):
                h = html.unescape(m.group(1)).strip()
                if h.startswith(('mailto:', 'tel:', 'javascript:', 'data:')) or '${' in h or '{{' in h or "' +" in h or '" +' in h or '<' in h:
                    continue
                v = urllib.parse.urljoin(final, h).split('#')[0]
                if not interno(v):
                    continue
                if len(origen[v]) < 3:
                    origen[v].append(final)
                if v in vistos:
                    continue
                vistos.add(v)
                p = urllib.parse.urlparse(v).path
                es_pag = p.endswith('/') or p.endswith('.html')
                if es_pag and not muestra(p):
                    continue
                cola.append(v)
    # los rotos de la semana pasada se vuelven a comprobar siempre
    try:
        for r in json.load(open('enlaces/informe.json'))['rotos']:
            if r['url'] not in vistos and interno(r['url']):
                vistos.add(r['url']); origen[r['url']] = r.get('desde', [])
    except Exception:
        pass
    # recursos y páginas pendientes sin rastrear: solo estado
    pend = [v for v in vistos if v not in estado]
    for v, (st, _, _) in zip(pend, ex.map(get, pend)):
        estado[v] = st
for u, st in estado.items():
    if st != 200:
        roto.append({'url': u, 'estado': st, 'desde': origen.get(u, [])})
json.dump({'paginas': paginas, 'revisadas': len(estado), 'rotos': sorted(roto, key=lambda x: x['url'])}, open('enlaces/informe.json', 'w'), ensure_ascii=False, indent=1)
print(paginas, len(estado), len(roto))

# Enviar al buzón de reportes de AURZANE (admin > Reportes). Cierra solo los que ya funcionan.
K = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
reales = [{'url': r['url'], 'estado': str(r['estado'])[:40], 'desde': (r['desde'] or [''])[0]} for r in roto
          if re.match(r'^https://([a-z]+\.)?aurzane\.com/', r['url'])][:400]
try:
    req = urllib.request.Request('https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/rpc/reportes_robot', method='POST',
                                 data=json.dumps({'p_rotos': reales}).encode(),
                                 headers={'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'})
    print('buzón:', urllib.request.urlopen(req, timeout=60).read()[:200])
except Exception as e:
    print('buzón: no se pudo enviar', e)
