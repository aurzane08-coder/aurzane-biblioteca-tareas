# Se ejecuta por tandas hasta tener las 62 páginas de la API; después solo una vez al mes.
"""Datos oficiales de las universidades de Estados Unidos: College Scorecard (Departamento de Educación de EE. UU.).
Fuente: API oficial del College Scorecard (api.data.gov), los mismos datos públicos que https://collegescorecard.ed.gov/data/.
Une cada institución con su ficha de AURZANE por el dominio de su web oficial y, si no, por nombre + ciudad.
Solo se guardan cifras que publica la fuente; ninguna se calcula ni se estima.
Salida: univ/data/scorecard.json  {id de la ficha: {campos}}  +  univ/data/scorecard.log (cobertura)."""
import json, gzip, os, re, sys, unicodedata, urllib.request, urllib.parse

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


API = 'https://api.data.gov/ed/collegescorecard/v1/schools'
# columna de la API oficial -> nombre en AURZANE (mismas cifras que el archivo descargable)
API_CAMPOS = {
    'id': 'unitid', 'school.name': 'nombre_oficial', 'school.city': 'ciudad', 'school.state': 'estado', 'school.school_url': 'web',
    'school.ownership': 'control', 'school.degrees_awarded.highest': 'grado_max', 'latest.student.size': 'estudiantes_grado',
    'latest.admissions.admission_rate.overall': 'admision',
    'latest.admissions.sat_scores.25th_percentile.critical_reading': 'sat_lec_25', 'latest.admissions.sat_scores.75th_percentile.critical_reading': 'sat_lec_75',
    'latest.admissions.sat_scores.25th_percentile.math': 'sat_mat_25', 'latest.admissions.sat_scores.75th_percentile.math': 'sat_mat_75',
    'latest.admissions.act_scores.25th_percentile.cumulative': 'act_25', 'latest.admissions.act_scores.75th_percentile.cumulative': 'act_75',
    'latest.cost.tuition.in_state': 'matricula_estado', 'latest.cost.tuition.out_of_state': 'matricula_fuera',
    'latest.cost.avg_net_price.public': 'precio_neto_pub', 'latest.cost.avg_net_price.private': 'precio_neto_priv',
    'latest.aid.pell_grant_rate': 'beca_pell', 'latest.completion.completion_rate_4yr_150nt': 'graduacion_6',
    'latest.student.retention_rate.four_year.full_time': 'permanencia', 'latest.earnings.10_yrs_after_entry.median': 'salario_10',
    'latest.aid.median_debt.completers.overall': 'deuda_mediana', 'location.lat': 'lat', 'location.lon': 'lon',
}
CRUDO = os.path.join(D, 'scorecard_crudo.json.gz')   # páginas ya bajadas: sin clave propia la API deja ~10 consultas por hora


def descargar():
    """Baja todas las instituciones abiertas de la API oficial, por páginas de 100, y continúa donde lo dejó.
    Con la clave gratuita de api.data.gov (secreto SCORECARD_KEY) baja todo de una vez; sin ella usa DEMO_KEY poco a poco."""
    import time
    clave = os.environ.get('SCORECARD_KEY') or 'DEMO_KEY'
    estado = json.load(gzip.open(CRUDO)) if os.path.exists(CRUDO) else {'paginas': {}, 'total': None}
    if estado.get('mes') != __import__('datetime').date.today().strftime('%Y-%m'): estado = {'paginas': {}, 'total': None, 'mes': __import__('datetime').date.today().strftime('%Y-%m')}
    hechas = 0
    while True:
        tot = estado['total']; faltan = [p for p in range((tot + 99) // 100 if tot else 1) if str(p) not in estado['paginas']]
        if not faltan: break
        if clave == 'DEMO_KEY' and hechas >= 9: break
        p = faltan[0]
        q = urllib.parse.urlencode({'api_key': clave, 'school.operating': 1, 'per_page': 100, 'page': p, 'fields': ','.join(API_CAMPOS)})
        try: r = json.loads(urllib.request.urlopen(urllib.request.Request(API + '?' + q, headers=UA), timeout=90).read())
        except Exception as e: print('Pausa de la API:', e); break
        estado['total'] = r['metadata']['total']; estado['paginas'][str(p)] = r['results']; hechas += 1
        print(f'Página {p + 1} de {(estado["total"] + 99) // 100}', flush=True)
        time.sleep(1 if clave != 'DEMO_KEY' else 2)
    json.dump(estado, gzip.open(CRUDO, 'wt', encoding='utf-8'), separators=(',', ':'))
    tot = estado['total'] or 0
    completo = tot and len(estado['paginas']) >= (tot + 99) // 100
    filas = [{API_CAMPOS[k]: v for k, v in x.items() if k in API_CAMPOS} for lst in estado['paginas'].values() for x in lst]
    return completo, len(estado['paginas']), (tot + 99) // 100, filas


def num(v):
    if v in (None, '', 'NULL', 'PrivacySuppressed', 'PS'): return None
    try:
        x = float(v); return int(x) if x.is_integer() else round(x, 4)
    except ValueError: return None


def main():
    U = json.load(gzip.open(os.path.join(D, 'sb_universidades.json.gz')))
    us = [u for u in U if u.get('pais') == 'Estados Unidos']
    completo, hechas, total_p, filas = descargar()
    # 19/11/2026: aunque falten páginas, se unen ya las que hay (las fichas ganan datos poco a poco)
    if not completo: print(f'Faltan páginas ({hechas} de {total_p}); se unen las que ya hay y se sigue en la próxima ejecución.')
    url = API
    por_dom, por_nom = {}, {}
    n_total = len(filas)
    for x in filas:
        d = dominio(x.get('web'))
        if d: por_dom.setdefault(d, []).append(x)
        por_nom.setdefault((norm(x.get('nombre_oficial')), norm(x.get('ciudad'))), []).append(x)
        por_nom.setdefault((norm(x.get('nombre_oficial')), ''), []).append(x)
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
    if not completo: log = f'College Scorecard: bajadas {hechas} de {total_p} páginas; se sigue en la próxima hora.\n' + log
    open(os.path.join(D, 'scorecard.log'), 'w', encoding='utf-8').write(log + '\n'); print(log)


if __name__ == '__main__':
    main()
