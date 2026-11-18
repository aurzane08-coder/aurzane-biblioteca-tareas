"""Datos oficiales de las universidades de Estados Unidos: College Scorecard (Departamento de Educación de EE. UU.).
Fuente: https://collegescorecard.ed.gov/data/ (archivo «Most-Recent-Cohorts-Institution», datos públicos del Gobierno).
Une cada institución con su ficha de AURZANE por el dominio de su web oficial y, si no, por nombre + ciudad.
Solo se guardan cifras que publica la fuente; ninguna se calcula ni se estima.
Salida: univ/data/scorecard.json  {id de la ficha: {campos}}  +  univ/data/scorecard.log (cobertura)."""
import csv, io, json, gzip, os, re, sys, unicodedata, urllib.request, zipfile

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PAGINA = 'https://collegescorecard.ed.gov/data/'
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AURZANE-datos/1.0 (+https://aurzane.com)'}
CAMPOS = {   # columna oficial -> nombre en AURZANE
    'UNITID': 'unitid', 'INSTNM': 'nombre_oficial', 'CITY': 'ciudad', 'STABBR': 'estado', 'INSTURL': 'web',
    'CONTROL': 'control', 'HIGHDEG': 'grado_max', 'UGDS': 'estudiantes_grado', 'ADM_RATE': 'admision',
    'SATVR25': 'sat_lec_25', 'SATVR75': 'sat_lec_75', 'SATMT25': 'sat_mat_25', 'SATMT75': 'sat_mat_75',
    'ACTCM25': 'act_25', 'ACTCM75': 'act_75', 'TUITIONFEE_IN': 'matricula_estado', 'TUITIONFEE_OUT': 'matricula_fuera',
    'NPT4_PUB': 'precio_neto_pub', 'NPT4_PRIV': 'precio_neto_priv', 'PCTPELL': 'beca_pell', 'C150_4': 'graduacion_6',
    'RET_FT4': 'permanencia', 'MD_EARN_WNE_P10': 'salario_10', 'GRAD_DEBT_MDN': 'deuda_mediana', 'LATITUDE': 'lat', 'LONGITUDE': 'lon',
}


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower()).encode('ascii', 'ignore').decode()
    s = re.sub(r'\b(the|of|at|and|university|college|universidad|de|la|del|el)\b', ' ', s.replace('&', ' '))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def dominio(u):
    u = re.sub(r'^https?://', '', (u or '').strip().lower()).split('/')[0]
    return re.sub(r'^www\d?\.', '', u)


RESERVA = 'https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_11022026.zip'   # la de noviembre de 2026


def bajar(url, t=300):
    # curl con cabeceras de navegador: la web del Departamento de Educación rechaza (403) a urllib
    import subprocess
    r = subprocess.run(['curl', '-sSL', '--fail', '-m', str(t), '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
                        '-H', 'Accept: text/html,application/zip,*/*', url], capture_output=True)
    if r.returncode: raise RuntimeError(f'{url}: {r.stderr.decode()[:200]}')
    return r.stdout


def descargar():
    url = RESERVA
    try:
        m = re.search(r'https://[^"\']+Most-Recent-Cohorts-Institution[^"\']*\.zip', bajar(PAGINA, 60).decode('utf-8', 'replace'))
        if m: url = m.group(0)
    except Exception as e: print('Página de descargas no disponible, uso el último archivo conocido:', e)
    print('Descargando', url, flush=True)
    z = zipfile.ZipFile(io.BytesIO(bajar(url)))
    nombre = next(n for n in z.namelist() if n.lower().endswith('.csv') and 'institution' in n.lower())
    return url, csv.DictReader(io.TextIOWrapper(z.open(nombre), encoding='utf-8-sig'))


def num(v):
    if v in (None, '', 'NULL', 'PrivacySuppressed', 'PS'): return None
    try:
        x = float(v); return int(x) if x.is_integer() else round(x, 4)
    except ValueError: return None


def main():
    U = json.load(gzip.open(os.path.join(D, 'sb_universidades.json.gz')))
    us = [u for u in U if u.get('pais') == 'Estados Unidos']
    url, filas = descargar()
    por_dom, por_nom = {}, {}
    n_total = 0
    for f in filas:
        n_total += 1
        x = {k2: (f.get(k) if k in ('INSTNM', 'CITY', 'STABBR', 'INSTURL') else num(f.get(k))) for k, k2 in CAMPOS.items()}
        if f.get('CURROPER') == '0': continue   # cerrada
        d = dominio(x['web'])
        if d: por_dom.setdefault(d, []).append(x)
        por_nom.setdefault((norm(x['nombre_oficial']), norm(x['ciudad'])), []).append(x)
        por_nom.setdefault((norm(x['nombre_oficial']), ''), []).append(x)
    out, como = {}, {'dominio': 0, 'nombre_ciudad': 0, 'nombre': 0}
    for u in us:
        c = None
        d = dominio(u.get('sitio_web'))
        if d and len(por_dom.get(d, [])) == 1: c = por_dom[d][0]; como['dominio'] += 1
        if not c:
            l = por_nom.get((norm(u['nombre']), norm(u.get('ciudad'))), [])
            if len(l) == 1: c = l[0]; como['nombre_ciudad'] += 1
        if not c:
            l = por_nom.get((norm(u['nombre']), ''), [])
            if len(l) == 1: c = l[0]; como['nombre'] += 1
        if c: out[u['id']] = {k: v for k, v in c.items() if v not in (None, '')}
    json.dump({'fuente': url, 'pagina': PAGINA, 'universidades': out}, open(os.path.join(D, 'scorecard.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    con = lambda k: sum(1 for v in out.values() if k in v)
    log = (f'College Scorecard: {n_total} instituciones en la fuente; {len(out)} de {len(us)} fichas de EE. UU. unidas '
           f'(dominio {como["dominio"]}, nombre y ciudad {como["nombre_ciudad"]}, solo nombre {como["nombre"]}).\n'
           f'Con tasa de admisión {con("admision")}, matrícula {con("matricula_fuera")}, precio neto {con("precio_neto_pub") + con("precio_neto_priv")}, '
           f'SAT {con("sat_mat_25")}, graduación {con("graduacion_6")}, salario a 10 años {con("salario_10")}, becas Pell {con("beca_pell")}.')
    open(os.path.join(D, 'scorecard.log'), 'w', encoding='utf-8').write(log + '\n'); print(log)


if __name__ == '__main__':
    main()
