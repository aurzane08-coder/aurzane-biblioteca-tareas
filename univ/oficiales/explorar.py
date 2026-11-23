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




def detalle():
    """Segunda vuelta: columnas del Excel de Chile y reparto de estados y niveles en Colombia."""
    import io, openpyxl, collections
    t, _ = get('https://www.datos.gov.co/resource/upr9-nkiz.json?$select=nombreestadoprograma,nombrenivelacademico,nombrenivelformacion,count(*)&$group=nombreestadoprograma,nombrenivelacademico,nombrenivelformacion&$limit=200')
    print('\n===== Colombia reparto\n', t[:4000])
    t, _ = get('https://www.datos.gov.co/resource/n5yy-8nav.json?$select=car_cter_acad_mico,principal_seccional,estado,count(*)&$group=car_cter_acad_mico,principal_seccional,estado&$limit=100')
    print('\n===== Colombia IES reparto\n', t[:3000])
    b = urllib.request.urlopen(urllib.request.Request('https://www.mifuturo.cl/wp-content/uploads/2026/06/Oferta_Academica_2026_SIES_05_06_2026_WEB_E.xlsx', headers=UA), timeout=120).read()
    wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True)
    for ws in wb.worksheets:
        print('\n===== Chile hoja', ws.title, ws.max_row, ws.max_column)
        filas = list(ws.iter_rows(max_row=8, values_only=True))
        for f in filas: print(f)
    ws = wb.worksheets[0]; rows = ws.iter_rows(values_only=True); cab = None
    for f in rows:
        if f and sum(1 for x in f if x) > 10: cab = [str(x) for x in f]; break
    cnt = {k: collections.Counter() for k in cab if re.search(r'tipo|nivel|vigencia|estado|modalidad|jornada|regi|clasif|area|carrera gen', k, re.I)}
    n = 0
    for f in rows:
        n += 1
        for k in cnt: cnt[k][f[cab.index(k)]] += 1
    print('\n===== Chile filas:', n)
    for k, c in cnt.items(): print(k, c.most_common(15))


def detalle2():
    import io, openpyxl
    for q in ["$where=nombreestadoprograma='Activo' AND nombrenivelformacion='Universitaria'&$limit=4&$offset=1000",
              "$select=nombreprograma,count(*)&$group=nombreprograma&$order=count(*) DESC&$limit=25"]:
        t, _ = get('https://www.datos.gov.co/resource/upr9-nkiz.json?' + q.replace(' ', '%20').replace("'", '%27'))
        print('\n===== Colombia', q, '\n', t[:5000])
    for i in ('2p93-tnnf', 'fvbn-24bf'):
        t, _ = get(f'https://www.datos.gov.co/api/views/{i}.json')
        try:
            m = json.loads(t); print('\n=====', i, m.get('name'), '|', m.get('attribution'), '| actualizado', m.get('rowsUpdatedAt'), '\n', [c.get('fieldName') for c in m.get('columns', [])])
        except Exception: print(i, t[:300])
        t, _ = get(f'https://www.datos.gov.co/resource/{i}.json?$limit=2'); print(t[:2500])
        t, _ = get(f'https://www.datos.gov.co/resource/{i}.json?$select=count(*)'); print(t[:200])
    b = urllib.request.urlopen(urllib.request.Request('https://www.mifuturo.cl/wp-content/uploads/2026/06/Oferta_Academica_2026_SIES_05_06_2026_WEB_E.xlsx', headers=UA), timeout=120).read()
    ws = openpyxl.load_workbook(io.BytesIO(b), read_only=True).worksheets[0]
    print('\n===== Chile cabecera'); [print(i, c) for i, c in enumerate(next(ws.iter_rows(values_only=True)))]


def detalle3():
    for u in ['https://www.datosabiertos.gob.pe/api/3/action/package_show?id=sunedu-programas-acad%C3%A9micos',
              'https://datosabiertos.gob.pe/dataset/sunedu-programas-acad%C3%A9micos',
              'https://www.datosabiertos.gob.pe/api/3/action/package_show?id=sunedu-licenciamiento-institucional']:
        t, ct = get(u, 600000)
        print('\n=====', u, ct); print(t[:300])
        try:
            for r in json.loads(t)['result'][0].get('resources', []):
                print('  RECURSO', r.get('format'), '|', r.get('name'), '|', r.get('url'), '|', r.get('last_modified') or r.get('created'))
            print('  NOTAS', (json.loads(t)['result'][0].get('notes') or '')[:400])
        except Exception as e: print('  sin recursos', e)
        for h in sorted(set(re.findall(r'https?://[^"\'\s<>]+\.(?:csv|xlsx?|zip)(?:\?[^"\'\s<>]*)?', t))): print('   ', h)
    import subprocess
    for u in ('https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_2024.zip',):
        print('\n===== BR curl', subprocess.run(['curl', '-sSI', '--max-time', '60', u], capture_output=True, text=True).stdout[:600])
        print(subprocess.run('echo | openssl s_client -connect download.inep.gov.br:443 -servername download.inep.gov.br 2>/dev/null | openssl x509 -noout -text | grep -A2 "Authority Information"', shell=True, capture_output=True, text=True).stdout)
    return
    for q in ['fq=organization:spu&rows=40', 'q=oferta%20academica&rows=20', 'q=titulos%20universitarios&rows=20', 'q=instituciones%20universitarias&rows=20']:
        t, _ = get('https://datos.gob.ar/api/3/action/package_search?' + q)
        print('\n===== AR', q)
        try:
            for p in json.loads(t)['result']['results']:
                print('-', p.get('name'), '|', p.get('title'), '|', p.get('metadata_modified', '')[:10])
                for r in p.get('resources', [])[:8]: print('     ·', r.get('format'), r.get('name'), r.get('url'))
        except Exception as e: print('ERROR', e, t[:300])
    for a in (2025, 2024, 2023):
        u = f'https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_{a}.zip'
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA, method='HEAD'), timeout=60)
            print('\n===== BR', u, r.status, r.headers.get('Content-Length'))
        except Exception as e: print('\n===== BR', u, e)
    t, _ = get('https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior', 1500000)
    print('\n===== BR página'); [print('   ', h) for h in sorted(set(re.findall(r'https?://[^"\'\s<>]+\.zip', t)))[:20]]


def detalle4():
    import subprocess, csv, io, collections
    for u in ('https://www.datosabiertos.gob.pe/sites/default/files/Programas%20de%20Universidades_9.csv',
              'https://www.datosabiertos.gob.pe/sites/default/files/Licenciamiento%20Institucional_18.csv'):
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
        for enc in ('utf-8-sig', 'latin-1'):
            try: t = b.decode(enc); break
            except Exception: pass
        sep = '|' if t[:500].count('|') > t[:500].count(',') else (';' if t[:500].count(';') > t[:500].count(',') else ',')
        filas = list(csv.reader(io.StringIO(t), delimiter=sep))
        print('\n===== PE', u, enc, repr(sep), len(filas)); [print('  ', f) for f in filas[:4]]
        cab = filas[0]
        for i, k in enumerate(cab):
            c = collections.Counter(f[i] for f in filas[1:] if len(f) > i)
            if len(c) < 40: print('   ', k, c.most_common(12))
    r = subprocess.run('''set -e
      curl -sS http://secure.globalsign.com/cacert/rnpicpedugr46ovtlsca2025.crt -o /tmp/int.der
      openssl x509 -inform DER -in /tmp/int.der -out /tmp/int.pem
      cat /etc/ssl/certs/ca-certificates.crt /tmp/int.pem > /tmp/ca.pem
      for a in 2024 2023; do echo "== $a"; curl -sSI --cacert /tmp/ca.pem --max-time 60 https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_$a.zip | head -8; done
    ''', shell=True, capture_output=True, text=True)
    print('\n===== BR', r.stdout[:2000], r.stderr[:800])


if len(sys.argv) > 1 and sys.argv[1] == 'detalle4':
    detalle4(); sys.exit(0)
if len(sys.argv) > 1 and sys.argv[1] == 'detalle3':
    detalle3(); sys.exit(0)
if len(sys.argv) > 1 and sys.argv[1] == 'detalle2':
    detalle2(); sys.exit(0)
if len(sys.argv) > 1 and sys.argv[1] == 'detalle':
    detalle(); sys.exit(0)


if __name__ == "__main__" and len(sys.argv) == 1:
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
