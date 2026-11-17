"""Rastreo SEO técnico de todo el ecosistema (17/11/2026, auditoría final). Lee los sitemaps de robots.txt de cada
dominio, revisa una muestra amplia de páginas (todas si hay pocas) con pocas peticiones a la vez para no cargar el
servidor y guarda auditoria/rastreo/AAAA-MM-DD.json con los datos por página y un resumen de problemas."""
import re, json, gzip, random, time, datetime, collections, urllib.request, concurrent.futures as cf
DOM = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
POR_SITEMAP = 250
UA = {'User-Agent': 'Mozilla/5.0 (AURZANE auditoria)'}


def get(u, t=30):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t)
        b = r.read(); b = gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
        return r.status, r.geturl(), b.decode('utf-8', 'replace')
    except urllib.error.HTTPError as e: return e.code, u, ''
    except Exception as e: return 0, u, str(e)[:80]


def sitemaps(dom):
    st, _, t = get(f'https://{dom}/robots.txt')
    sm = re.findall(r'(?im)^sitemap:\s*(\S+)', t) or [f'https://{dom}/sitemap.xml']
    urls, vistos = {}, set()
    while sm:
        s = sm.pop()
        if s in vistos: continue
        vistos.add(s); st, _, x = get(s)
        locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', x)
        if '<sitemapindex' in x: sm += locs
        else: urls[s] = locs
    return urls


filas = []


def revisar(u):
    t0 = time.time(); st, fin, h = get(u); ms = int((time.time() - t0) * 1000)
    head = h[:200000]
    m = lambda p: (re.search(p, head, re.I | re.S) or [None, None])[1]
    f = {'u': u, 'st': st, 'fin': fin if fin != u else '', 'ms': ms, 'kb': len(h.encode()) // 1024,
         'title': re.sub(r'\s+', ' ', m(r'<title[^>]*>(.*?)</title>') or '').strip(),
         'desc': (m(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)') or m(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description') or '').strip(),
         'canon': m(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)') or m(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical') or '',
         'robots': (m(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)') or '').lower(),
         'h1': len(re.findall(r'<h1[\s>]', head, re.I)), 'lang': m(r'<html[^>]+lang=["\']([^"\']+)') or '',
         'img_sin_alt': len([i for i in re.findall(r'<img\b[^>]*>', head, re.I) if not re.search(r'\balt=', i, re.I)]),
         'jsonld': sorted(set(re.findall(r'"@type"\s*:\s*"([^"]+)"', head)))[:6], 'og': bool(re.search(r'property=["\']og:image', head)),
         'emdash': head.count('—'), 'ads': 'adsbygoogle' in head, 'palabras': len(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', head)).split())}
    filas.append(f)


hoy = datetime.date.today().isoformat(); todas = []
for d in DOM:
    for s, locs in sitemaps(d).items():
        random.seed(s); muestra = locs if len(locs) <= POR_SITEMAP else random.sample(locs, POR_SITEMAP)
        print(d, s, len(locs), 'URLs, se revisan', len(muestra)); todas += [(u, s, len(locs)) for u in muestra]
total_sitemaps = collections.Counter()
for u, s, n in todas: total_sitemaps[s] = n
with cf.ThreadPoolExecutor(4) as ex: list(ex.map(revisar, [u for u, _, _ in todas]))
# resumen
P = collections.defaultdict(list)
tit = collections.Counter(f['title'] for f in filas if f['title'])
des = collections.Counter(f['desc'] for f in filas if f['desc'])
for f in filas:
    u = f['u']
    if f['st'] != 200: P['estado_no_200'].append([u, f['st']])
    if f['fin']: P['redirige'].append([u, f['fin']])
    if f['st'] != 200: continue
    if not f['title']: P['sin_title'].append(u)
    elif len(f['title']) > 65: P['title_largo'].append([u, len(f['title'])])
    elif len(f['title']) < 25: P['title_corto'].append([u, f['title']])
    if f['title'] and tit[f['title']] > 1: P['title_duplicado'].append([u, f['title']])
    if not f['desc']: P['sin_desc'].append(u)
    elif len(f['desc']) > 165: P['desc_larga'].append([u, len(f['desc'])])
    elif len(f['desc']) < 70: P['desc_corta'].append([u, f['desc']])
    if f['desc'] and des[f['desc']] > 1: P['desc_duplicada'].append(u)
    if f['h1'] != 1: P['h1_no_uno'].append([u, f['h1']])
    if not f['canon']: P['sin_canonical'].append(u)
    elif f['canon'].rstrip('/') != u.rstrip('/'): P['canonical_distinto'].append([u, f['canon']])
    if 'noindex' in f['robots']: P['noindex_en_sitemap'].append(u)
    if f['img_sin_alt']: P['img_sin_alt'].append([u, f['img_sin_alt']])
    if not f['og']: P['sin_og_image'].append(u)
    if f['emdash']: P['raya_em'].append([u, f['emdash']])
    if f['palabras'] < 250: P['poco_texto'].append([u, f['palabras']])
    if f['ms'] > 2500: P['lenta'].append([u, f['ms']])
    if f['kb'] > 400: P['pesada'].append([u, f['kb']])
res = {'fecha': hoy, 'paginas_revisadas': len(filas), 'sitemaps': dict(total_sitemaps), 'urls_en_sitemaps': sum(total_sitemaps.values()),
       'tiempo_medio_ms': int(sum(f['ms'] for f in filas) / max(1, len(filas))), 'problemas_n': {k: len(v) for k, v in P.items()},
       'problemas': {k: v[:60] for k, v in P.items()}, 'jsonld': collections.Counter(t for f in filas for t in f['jsonld']).most_common(25)}
import os; os.makedirs('auditoria/rastreo', exist_ok=True)
json.dump(res, open(f'auditoria/rastreo/{hoy}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(filas, open(f'auditoria/rastreo/{hoy}-paginas.json', 'w'), ensure_ascii=False)
print(json.dumps({k: res[k] for k in ('paginas_revisadas', 'urls_en_sitemaps', 'tiempo_medio_ms', 'problemas_n')}, ensure_ascii=False, indent=1))
