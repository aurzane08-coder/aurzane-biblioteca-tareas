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

# 1. nivel de precios por país (Banco Mundial), una vez por pasada
w = get('https://api.worldbank.org/v2/country/all/indicator/PA.NUS.PPPC.RF?format=json&per_page=20000&date=2018:2025', 120)
if not (w and len(w) > 1 and w[1]): print('::warning::Banco Mundial no respondió; se mantiene el dato anterior')
if w and len(w) > 1 and w[1]:
    pre = {}
    for x in sorted(w[1], key=lambda x: x.get('date') or ''):
        if x.get('value'): pre[x['countryiso3code']] = [round(x['value'], 3), x['date']]
    paises = get('https://api.worldbank.org/v2/country?format=json&per_page=400', 60)
    iso3 = {c['id']: c['iso2Code'].lower() for c in (paises[1] if paises and len(paises) > 1 else [])}
    info['_precios'] = {iso3[k]: v for k, v in pre.items() if k in iso3}
    print('precios:', len(info['_precios']), 'países; España', info['_precios'].get('es'))


def vigente(x):
    try: return (HOY - datetime.date.fromisoformat(x.get('fecha', '2000-01-01'))).days < 120
    except Exception: return False


def buscar_lote(iso, nombres):
    """Varias ciudades de un país en una sola consulta a Wikidata (por su nombre en español, inglés o el propio)."""
    vals = ' '.join(f'"{n.replace(chr(92), "").replace(chr(34), "")}"@{l}' for n in nombres for l in ('es', 'en', 'mul'))
    sp = f'''SELECT ?c ?n ?pop ?alt ?coord ?es ?en ?pt ?fr WHERE {{
  VALUES ?n {{ {vals} }} ?pais wdt:P297 "{iso.upper()}". ?c rdfs:label ?n; wdt:P17 ?pais; wdt:P1082 ?pop.
  OPTIONAL {{ ?c wdt:P2044 ?alt }} OPTIONAL {{ ?c wdt:P625 ?coord }}
  OPTIONAL {{ ?es schema:about ?c; schema:isPartOf <https://es.wikipedia.org/> }} OPTIONAL {{ ?en schema:about ?c; schema:isPartOf <https://en.wikipedia.org/> }}
  OPTIONAL {{ ?pt schema:about ?c; schema:isPartOf <https://pt.wikipedia.org/> }} OPTIONAL {{ ?fr schema:about ?c; schema:isPartOf <https://fr.wikipedia.org/> }} }}'''
    r = get('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': sp, 'format': 'json'}), 90)
    mejor = {}
    for b in (r or {}).get('results', {}).get('bindings') or []:
        v = lambda k: (b.get(k) or {}).get('value')
        k = norm(v('n'))
        try: pop = int(float(v('pop') or 0))
        except Exception: pop = 0
        if k in mejor and mejor[k]['pop'] >= pop: continue
        out = {'q': v('c').rsplit('/', 1)[-1], 'pop': pop}
        if v('alt'):
            try: out['alt'] = round(float(v('alt')))
            except Exception: pass
        m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', v('coord') or '')
        if m: out['lon'], out['lat'] = round(float(m.group(1)), 4), round(float(m.group(2)), 4)
        for l in ('es', 'en', 'pt', 'fr'):
            if v(l): out['wiki_' + l] = urllib.parse.unquote(v(l).rsplit('/wiki/', 1)[-1])
        mejor[k] = out
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
            x['fecha'] = str(HOY); pais[norm(nombre)] = x; n += 1
        json.dump(info, open(F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':')); print(f'  {iso}: {n} ciudades', flush=True)
        time.sleep(1)
json.dump(info, open(F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
total = sum(len(v) for k, v in info.items() if k != '_precios')
con = sum(1 for k, v in info.items() if k != '_precios' for x in v.values() if x.get('q'))
print(f'Ciudades: {n} revisadas en esta pasada; {con} de {total} encontradas en Wikidata; páginas de ciudad: {len(paginas)}')
