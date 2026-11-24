"""«Vivir en [ciudad]» para las páginas de ciudad de NEXUS (24/11/2026). Todo automático y con fuente:
- Wikidata: población, altitud, coordenadas y el nombre del artículo de Wikipedia en español, inglés, portugués y francés.
- Wikipedia: el primer párrafo en español y en inglés (licencia CC BY-SA, se cita en la página).
- Banco Mundial: nivel de precios de cada país (indicador PA.NUS.PPPC.RF), para comparar el coste de vida con España.
Qué ciudades: las que tienen página (gen.py deja la lista en univ/data/ciudades_paginas.json en cada publicación).
Se completa poco a poco (MAX ciudades nuevas por pasada) y se refresca cada 120 días. Si algo falla, la página sale sin ese dato.
Salida: univ/data/ciudades_info.json {iso: {ciudad_normalizada: {...}}, "_precios": {iso: [valor, año]}}"""
import json, os, re, sys, time, datetime, unicodedata, urllib.parse, urllib.request
D = sys.argv[1] if len(sys.argv) > 1 else 'univ/data'
F, LISTA = os.path.join(D, 'ciudades_info.json'), os.path.join(D, 'ciudades_paginas.json')
MAX = int(os.environ.get("MAX_CIUDADES") or 1500)
HOY = datetime.date.today()
UA = {'User-Agent': 'AURZANE-NEXUS/1.0 (https://nexus.aurzane.com/universidades/; hola@aurzane.com)'}


def get(url, t=40):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=dict(UA, Accept='application/json')), timeout=t) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(3 * (i + 1))
        except Exception: time.sleep(3 * (i + 1))
    return None


def norm(t):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


info = json.load(open(F, encoding='utf-8')) if os.path.exists(F) else {}
paginas = json.load(open(LISTA, encoding='utf-8')) if os.path.exists(LISTA) else []

# 1. nivel de precios por país (Banco Mundial): factor de conversión PPA / tipo de cambio oficial, último año con los dos datos
def serie(ind):
    w = get(f'https://api.worldbank.org/v2/country/all/indicator/{ind}?format=json&per_page=20000&date=2018:2025', 120)
    out = {}
    for x in sorted((w[1] if w and len(w) > 1 and w[1] else []), key=lambda x: x.get('date') or ''):
        if x.get('value'): out.setdefault(x['countryiso3code'], {})[x['date']] = x['value']
    return out


ppa, cambio = serie('PA.NUS.PPP'), serie('PA.NUS.FCRF')
paises = get('https://api.worldbank.org/v2/country?format=json&per_page=400', 60)
iso3 = {c['id']: c['iso2Code'].lower() for c in (paises[1] if paises and len(paises) > 1 else [])}
pre = {}
for k, a in ppa.items():
    anios = sorted(set(a) & set(cambio.get(k, {})))
    if anios and k in iso3: y = anios[-1]; pre[iso3[k]] = [round(a[y] / cambio[k][y], 3), y]
if len(pre) > 100: info['_precios'] = pre; print('precios:', len(pre), 'países; España', pre.get('es'))
else: print('::warning::Banco Mundial sin datos suficientes; se mantiene el dato anterior')


def vigente(x):
    try: return (HOY - datetime.date.fromisoformat(x.get('fecha', '2000-01-01'))).days < (120 if x.get('q') else 7) and x.get('v') == 2   # v2: población buena (la preferida o la más reciente)   # sin encontrar: se reintenta a la semana
    except Exception: return False


PAIS_Q = {}


def buscar_lote(iso, nombres):
    """1) Qué elementos de Wikidata del país se llaman así (consulta ligera); 2) sus datos con la API de entidades (rápida)."""
    if iso not in PAIS_Q:
        r = get('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': f'SELECT ?p WHERE {{ ?p wdt:P297 "{iso.upper()}" }} LIMIT 1', 'format': 'json'}), 60)
        b = (r or {}).get('results', {}).get('bindings') or []
        PAIS_Q[iso] = b[0]['p']['value'].rsplit('/', 1)[-1] if b else ''
    if not PAIS_Q[iso]: return {}
    vals = ' '.join(f'"{n.replace(chr(92), "").replace(chr(34), "")}"@{l}' for n in nombres for l in ('es', 'en'))
    sp = f'SELECT ?c ?n WHERE {{ VALUES ?n {{ {vals} }} ?c rdfs:label ?n. ?c wdt:P17 wd:{PAIS_Q[iso]}. }}'
    r = get('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': sp, 'format': 'json'}), 60)
    cand = {}
    for b in (r or {}).get('results', {}).get('bindings') or []:
        cand.setdefault(b['c']['value'].rsplit('/', 1)[-1], set()).add(norm(b['n']['value']))
    if not cand: return {}
    mejor, ids = {}, list(cand)
    for a in range(0, len(ids), 50):
        e = get('https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode({'action': 'wbgetentities', 'ids': '|'.join(ids[a:a + 50]), 'props': 'claims|sitelinks',
                                                                                 'sitefilter': 'eswiki|enwiki|ptwiki|frwiki', 'format': 'json'}), 60) or {}
        for q, ent in (e.get('entities') or {}).items():
            cl = ent.get('claims') or {}
            def val(p):
                for c in cl.get(p, []):
                    dv = c.get('mainsnak', {}).get('datavalue', {}).get('value')
                    if dv is not None and c.get('rank') != 'deprecated': return dv
            pop = 0   # la cifra de población preferida o, si no, la más reciente (por su fecha)
            cs = [c for c in cl.get('P1082', []) if c.get('rank') != 'deprecated' and c.get('mainsnak', {}).get('datavalue')]
            if cs:
                fecha = lambda c: ((c.get('qualifiers') or {}).get('P585') or [{}])[0].get('datavalue', {}).get('value', {}).get('time', '')
                c = sorted(cs, key=lambda c: (c.get('rank') == 'preferred', fecha(c)))[-1]
                try: pop = int(float(c['mainsnak']['datavalue']['value']['amount']))
                except Exception: pop = 0
            if not pop: continue   # sin población: no es una ciudad (o no sirve)
            out = {'q': q, 'pop': pop}
            alt = val('P2044')
            try: out['alt'] = round(float(alt['amount'])) if alt else None
            except Exception: pass
            if out.get('alt') is None: out.pop('alt', None)
            co = val('P625')
            if co: out['lat'], out['lon'] = round(co['latitude'], 4), round(co['longitude'], 4)
            for l in ('es', 'en', 'pt', 'fr'):
                t = (ent.get('sitelinks') or {}).get(l + 'wiki', {}).get('title')
                if t: out['wiki_' + l] = t
            for k in cand.get(q, ()):
                if k not in mejor or mejor[k]['pop'] < pop: mejor[k] = out
        time.sleep(0.5)
    return mejor


def resumen(lengua, titulo):
    if not titulo: return ''
    r = get(f'https://{lengua}.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(titulo.replace(' ', '_'), safe=''), 30)
    t = (r or {}).get('extract') or ''
    t = re.sub(r'\s*\([^()]*\)', '', t) if len(t) > 700 else t   # quita paréntesis largos de pronunciación cuando es muy largo
    return t[:900].rsplit('. ', 1)[0] + '.' if len(t) > 900 else t


pend = {}
for iso, nombre in paginas:
    x = info.get(iso, {}).get(norm(nombre))
    if not (x and vigente(x)): pend.setdefault(iso, []).append(nombre)
n = 0
for iso, nombres in pend.items():
    pais = info.setdefault(iso, {})
    for a in range(0, len(nombres), 40):
        if n >= MAX: break
        lote = nombres[a:a + 40]; hall = buscar_lote(iso, lote)
        for nombre in lote:
            x = hall.get(norm(nombre)) or {}
            if x:
                x['txt_es'] = resumen('es', x.get('wiki_es')); x['txt_en'] = resumen('en', x.get('wiki_en'))
            x['fecha'] = str(HOY); x['v'] = 2; pais[norm(nombre)] = x; n += 1
        json.dump(info, open(F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':')); print(f'  {iso}: {n} ciudades', flush=True)
        time.sleep(1)
json.dump(info, open(F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
total = sum(len(v) for k, v in info.items() if k != '_precios')
con = sum(1 for k, v in info.items() if k != '_precios' for x in v.values() if x.get('q'))
print(f'Ciudades: {n} revisadas en esta pasada; {con} de {total} encontradas en Wikidata; páginas de ciudad: {len(paginas)}')
