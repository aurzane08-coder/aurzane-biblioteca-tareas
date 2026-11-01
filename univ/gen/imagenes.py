# -*- coding: utf-8 -*-
"""Busca en Wikidata fotos y logos de universidades y fotos de ciudades para el catálogo.
Uso: python3 imagenes.py SALIDA.json
Guarda {"u": {ISO: [[nombre, dominio, foto, logo], ...]}, "c": {ISO: {ciudad_normalizada: foto}}}.
Las imágenes son de Wikimedia Commons (licencias libres); el portal enlaza la ficha de cada archivo."""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = sys.argv[1]
src = open(os.path.join(AQUI, 'gen.py'), encoding='utf-8').read()
bloque = src[src.index('PAISES = {'):src.index('}', src.index('PAISES = {'))]
ISOS = list(dict.fromkeys(re.findall(r"\('([a-z]{2})'", bloque)))
print(len(ISOS), 'países')

EP = 'https://query.wikidata.org/sparql'
UA = 'AURZANE-catalogo/1.0 (https://nexus.aurzane.com/universidades/; hola@aurzane.com)'


def q(sparql, intentos=2):
    url = EP + '?' + urllib.parse.urlencode({'query': sparql, 'format': 'json'})
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json'})
            with urllib.request.urlopen(req, timeout=55) as r:
                return json.load(r)['results']['bindings']
        except Exception as ex:
            print('  reintento', i + 1, str(ex)[:120]); time.sleep(5)
    return []


def norm(t):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


def dominio(w):
    w = re.sub(r'^https?://', '', (w or '').lower()).split('/')[0]
    return re.sub(r'^www\d?\.', '', w)


def archivo(v):
    return urllib.parse.unquote(v.rsplit('/', 1)[-1]) if v else ''


CLASES = 'wd:Q3918 wd:Q38723 wd:Q902104 wd:Q875538 wd:Q15936437 wd:Q1371037 wd:Q189004 wd:Q23002054 wd:Q1664720 wd:Q4671277 wd:Q2467461 wd:Q62078547'
out = {'u': {}, 'c': {}}
for iso in ISOS:
    I = iso.upper()
    filas = q(f'''SELECT ?item ?itemLabel ?web ?img ?logo WHERE {{
  ?pais wdt:P297 "{I}". ?item wdt:P17 ?pais; wdt:P31/wdt:P279? ?cl. VALUES ?cl {{ {CLASES} }}
  OPTIONAL {{ ?item wdt:P856 ?web }} OPTIONAL {{ ?item wdt:P18 ?img }} OPTIONAL {{ ?item wdt:P154 ?logo }}
  FILTER(BOUND(?img) || BOUND(?logo))
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }} }}''')
    vistos, us = set(), []
    for f in filas:
        it = f['item']['value']
        if it in vistos: continue
        vistos.add(it)
        us.append([f.get('itemLabel', {}).get('value', ''), dominio(f.get('web', {}).get('value')), archivo(f.get('img', {}).get('value')), archivo(f.get('logo', {}).get('value'))])
    out['u'][iso] = us
    time.sleep(1.5)
    cs = q(f'''SELECT ?c ?cLabel ?img ?pop WHERE {{
  ?pais wdt:P297 "{I}". ?c wdt:P17 ?pais; wdt:P18 ?img; wdt:P1082 ?pop. FILTER(?pop > 15000)
  ?c wdt:P31/wdt:P279? ?t. VALUES ?t {{ wd:Q515 wd:Q1549591 wd:Q486972 wd:Q3957 wd:Q1637706 wd:Q5119 wd:Q2074737 wd:Q747074 wd:Q15284 wd:Q1093829 }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }} }}''')
    mapa = {}
    for f in sorted(cs, key=lambda f: -float(f.get('pop', {}).get('value') or 0)):
        n = norm(f.get('cLabel', {}).get('value'))
        if n and n not in mapa: mapa[n] = archivo(f['img']['value'])
    out['c'][iso] = mapa
    print(iso, len(us), 'universidades con imagen,', len(mapa), 'ciudades', flush=True)
    json.dump(out, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))  # guarda el avance
    time.sleep(1)

json.dump(out, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('OK', sum(len(v) for v in out['u'].values()), 'universidades,', sum(len(v) for v in out['c'].values()), 'ciudades')
