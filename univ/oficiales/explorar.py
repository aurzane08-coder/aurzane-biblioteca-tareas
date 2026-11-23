"""Explora las fuentes oficiales de datos abiertos de educación superior (23/11/2026) y muestra su estructura en el registro.
No guarda nada: sirve para escribir los importadores con los campos reales de cada fuente."""
import json, re, sys, urllib.request, urllib.parse

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AURZANE-datos/1.0 (+https://aurzane.com)'}


def get(url, n=400000):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            return r.read(n).decode('utf-8', 'replace'), r.headers.get('Content-Type', '')
    except Exception as e:
        return 'ERROR ' + str(e), ''


def ver(titulo, url, n=1500):
    t, ct = get(url)
    print(f'\n===== {titulo}\n{url}\n[{ct}]\n{t[:n]}')
    return t


def socrata(dom, i):
    ver(f'{dom} {i} metadatos', f'https://{dom}/api/views/{i}.json', 600)
    t, _ = get(f'https://{dom}/api/views/{i}.json')
    try:
        m = json.loads(t); print('Filas aprox:', m.get('rowsUpdatedAt'), '· columnas:', [c.get('fieldName') for c in m.get('columns', [])])
    except Exception: pass
    ver(f'{dom} {i} filas', f'https://{dom}/resource/{i}.json?$limit=3', 3000)
    ver(f'{dom} {i} recuento', f'https://{dom}/resource/{i}.json?$select=count(*)', 200)


def ckan(base, q, n=12):
    t, _ = get(f'{base}/api/3/action/package_search?rows={n}&q=' + urllib.parse.quote(q))
    print(f'\n===== CKAN {base} «{q}»')
    try:
        for p in json.loads(t)['result']['results']:
            print('-', p.get('name'), '|', p.get('title'), '|', p.get('metadata_modified'))
            for r in p.get('resources', [])[:6]:
                print('     ·', r.get('format'), r.get('name'), r.get('url'))
    except Exception as e:
        print('ERROR', e, t[:300])


def enlaces(titulo, url, pat):
    t, _ = get(url, 2000000)
    print(f'\n===== {titulo}\n{url}')
    for h in sorted(set(re.findall(r'href="([^"]+)"', t))):
        if re.search(pat, h, re.I): print('  ', h)


# Colombia: SNIES (Ministerio de Educación) en datos.gov.co
socrata('www.datos.gov.co', 'upr9-nkiz')
socrata('www.datos.gov.co', 'n5yy-8nav')
# Chile: SIES / Mi Futuro (Mineduc)
enlaces('Chile Mi Futuro bases de datos', 'https://www.mifuturo.cl/bases-de-datos-de-oferta-academica/', r'\.(xlsx?|csv|zip|rar)|oferta')
enlaces('Chile Mi Futuro buscador', 'https://www.mifuturo.cl/bases-de-datos/', r'\.(xlsx?|csv|zip|rar)')
ckan('https://datos.gob.cl', 'oferta academica educacion superior')
# Perú: SUNEDU / Minedu
ckan('https://www.datosabiertos.gob.pe', 'sunedu universidades')
ckan('https://www.datosabiertos.gob.pe', 'programas de estudio universidades licenciadas')
# Argentina: Ministerio de Capital Humano (SIU / Departamento de Información Universitaria)
ckan('https://datos.gob.ar', 'oferta academica universitaria')
ckan('https://datos.gob.ar', 'instituciones universitarias')
# México: SEP / ANUIES
ckan('https://www.datos.gob.mx', 'instituciones de educacion superior')
ckan('https://www.datos.gob.mx', 'anuies programas licenciatura')
# Brasil: e-MEC (Ministério da Educação)
ckan('https://dados.gov.br/dados', 'e-mec cursos instituicoes')
enlaces('Brasil dados abertos MEC', 'https://dadosabertos.mec.gov.br/indicadores-sobre-ensino-superior', r'\.(csv|zip|xlsx?)')
