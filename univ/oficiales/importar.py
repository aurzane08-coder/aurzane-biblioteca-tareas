# -*- coding: utf-8 -*-
"""Importa de fuentes oficiales de datos abiertos las instituciones de educación superior y su oferta vigente (23/11/2026).
Cada país se guarda en univ/data/oficial_<iso>.json con el mismo formato; univ/gen/gen.py lo une al catálogo
(completa las fichas que ya existen, sin cambiar su dirección, y añade las que faltan). Solo se guardan datos que publica la fuente.

  Colombia  SNIES, Ministerio de Educación Nacional (datos.gov.co, CC BY-SA 4.0): instituciones (n5yy-8nav) y programas (upr9-nkiz).
            En el conjunto de programas la columna del nombre trae el departamento, así que cada programa se muestra con el
            título oficial que otorga («Abogado», «Ingeniero Ambiental») y su núcleo básico de conocimiento.
  Chile     SIES, Subsecretaría de Educación Superior (mifuturo.cl): base de oferta académica del año, con duración, arancel y vacantes.
Uso: python3 univ/oficiales/importar.py [co cl]"""
import io, os, re, sys, json, time, datetime, collections, unicodedata, urllib.request, urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, '..', 'data')
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AURZANE-datos/1.0 (+https://aurzane.com)'}
LOG = []


def log(*a):
    t = ' '.join(str(x) for x in a); print(t, flush=True); LOG.append(t)


def get(url, binario=False, intentos=5):
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                b = r.read()
                return b if binario else b.decode('utf-8', 'replace')
        except Exception as e:
            log('  reintento', i + 1, url[:120], e); time.sleep(5 * (i + 1))
    raise RuntimeError('No responde: ' + url)


def limpio(t):
    return re.sub(r'\s+', ' ', str(t or '')).strip()


def nrm(t):
    t = unicodedata.normalize('NFD', (t or '').lower()); t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', t).strip()


def guardar(iso, d):
    p = os.path.join(DATOS, f'oficial_{iso}.json')
    viejo = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    n_i, n_c = len(d['instituciones']), sum(len(x['carreras']) for x in d['instituciones'])
    if viejo and not os.environ.get('FORZAR') and n_c < 0.6 * sum(len(x['carreras']) for x in viejo['instituciones']):
        log(f'::warning::{iso}: la fuente devuelve muchas menos carreras que la última vez ({n_c}); se mantiene el archivo anterior'); return
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    log(f'{iso}: {n_i} instituciones · {n_c} carreras y programas vigentes → {os.path.basename(p)}')


def socrata(dom, i, where='', orden=':id'):
    out, off = [], 0
    while True:
        q = f'https://{dom}/resource/{i}.json?$limit=20000&$offset={off}&$order={orden}' + (f'&$where={urllib.parse.quote(where)}' if where else '')
        lote = json.loads(get(q)); out += lote; off += len(lote)
        if len(lote) < 20000: return out


# ------------------------------------------------------------------------------------------------ Colombia
NIVEL_CO = {'Universitaria': 'Pregrado universitario', 'Tecnológica': 'Tecnológico', 'Formación técnica profesional': 'Técnico profesional',
            'Especialización universitaria': 'Especialización', 'Especialización tecnológica': 'Especialización', 'Especialización técnico profesional': 'Especialización',
            'Especialización médico quirúrgica': 'Especialización médico-quirúrgica', 'Maestría': 'Maestría', 'Doctorado': 'Doctorado'}
IES_CO = {'Universidad': 'Universidad', 'Institución Universitaria/Escuela Tecnológica': 'Institución universitaria',
          'Institución Tecnológica': 'Institución tecnológica', 'Institución Técnica Profesional': 'Institución técnica profesional'}


def cap(t):
    """«INGENIERO AMBIENTAL» → «Ingeniero Ambiental» (mayúsculas de la fuente), respetando partículas, números romanos y «(a)»."""
    t = limpio(t)
    letras = [c for c in t if c.isalpha()]
    if not letras or sum(c.isupper() for c in letras) < 0.8 * len(letras): return arreglar(t)
    menores = {'de', 'del', 'la', 'las', 'los', 'y', 'e', 'en', 'o', 'u', 'a', 'el', 'para', 'con', 'por', 'al', 'as', 'os'}
    n = [0]
    def r(m):
        w = m.group(0); i = n[0]; n[0] += 1
        if re.fullmatch(r'[ivx]{1,4}', w) and w not in ('vi',) or w in ('uc', 'tic', 'ii'): return w.upper()
        if i and w in menores: return w
        return w[:1].upper() + w[1:]
    return arreglar(re.sub(r'[a-záéíóúñü]+', r, t.lower()))


def arreglar(t):
    """Erratas frecuentes de las fuentes."""
    return re.sub(r'\bMa(e)?gister\b', 'Magíster', t)


def colombia():
    log('Colombia: SNIES en datos.gov.co')
    ies = socrata('www.datos.gov.co', 'n5yy-8nav')
    prog = socrata('www.datos.gov.co', 'upr9-nkiz', "nombreestadoprograma='Activo'")
    log(f'  {len(ies)} registros de instituciones · {len(prog)} programas activos')
    por_cod, inst = {}, collections.OrderedDict()
    # la sede principal primero: da nombre, ciudad y web a la institución; las seccionales suman sus programas
    for r in sorted(ies, key=lambda r: (r.get('principal_seccional') != 'Principal', r.get('c_digo_instituci_n', ''))):
        if 'Activa' not in (r.get('estado') or ''): continue
        k = nrm(r.get('nombre_instituci_n'))
        if not k: continue
        if k not in inst:
            web = limpio(r.get('p_gina_web')).split()[0] if limpio(r.get('p_gina_web')) else ''
            if web and not web.startswith('http'): web = 'https://' + web.lstrip('/')
            if web and not re.match(r'^https?://[a-z0-9.-]+\.[a-z]{2,}', web, re.I): web = ''
            f = (r.get('fecha_norma_de_creaci_n') or '')[:4]
            extra = {'cod': r.get('c_digo_instituci_n', '')}
            if f.isdigit() and 1500 < int(f) <= datetime.date.today().year and not (r.get('fecha_norma_de_creaci_n') or '').startswith('1899-12-30'): extra['anio'] = f
            if (r.get('acreditada_alta_calidad') or '').upper() == 'SI': extra['acreditacion'] = 'Acreditación institucional de alta calidad (Ministerio de Educación Nacional)'
            inst[k] = {'cod': r.get('c_digo_instituci_n', ''), 'nombre': acentuar(cap(r.get('nombre_instituci_n'))), 'tipo': 'pública' if (r.get('sector') or '').startswith('Oficial') else 'privada',
                       'tipo_ies': IES_CO.get(r.get('car_cter_acad_mico'), limpio(r.get('car_cter_acad_mico')) or 'Institución de educación superior'),
                       'ciudad': limpio(r.get('municipio_domicilio')).replace('Bogotá, D.C.', 'Bogotá').replace('Bogotá D.C.', 'Bogotá'),
                       'region': limpio(r.get('departamento_domicilio')), 'web': web, 'extra': extra, 'carreras': [], '_v': {}}
        por_cod[r.get('c_digo_instituci_n', '')] = k
    sin = collections.Counter()
    for p in prog:
        k = por_cod.get(p.get('codigoinstitucion')) or nrm(p.get('nombreinstitucion'))
        u = inst.get(k)
        if not u: sin[p.get('nombreinstitucion')] += 1; continue
        tit = acentuar(cap(p.get('nombretituloobtenido')))
        if not tit or tit.upper() in ('NA', 'N/A', 'SIN DATO'): continue
        grupo = NIVEL_CO.get(p.get('nombrenivelformacion'), limpio(p.get('nombrenivelformacion')) or 'Otros')
        sede = limpio(p.get('nombremunicipioprograma')).replace('Bogotá, D.C.', 'Bogotá').replace('Bogotá D.C.', 'Bogotá')
        if re.match(r'(?i)no (especifica|aplica|informa)|sin dato', sede): sede = ''
        mod = limpio(p.get('nombremetodologia'))
        cred = p.get('cantidadcreditos') or ''
        per, tper = p.get('cantidadperiodos') or '', (p.get('nombreperiodicidad') or '').lower()
        dur = f'{per} {"semestres" if tper.startswith("semestr") else ("años" if tper.startswith("anual") else "periodos")}' if per.isdigit() and int(per) > 1 else ''
        clave = (nrm(tit), grupo)
        x = u['_v'].get(clave)
        if x:
            if sede and sede not in x['sedes']: x['sedes'].append(sede)
            if mod and mod not in x['mod']: x['mod'].append(mod)
            continue
        x = {'n': tit, 'grupo': grupo, 'area': arreglar(limpio(p.get('nombrenbc'))), 'mod': [mod] if mod else [], 'sedes': [sede] if sede else [],
             'cred': ' · '.join(v for v in [f'{cred} créditos' if cred.isdigit() else '', dur] if v)}
        u['_v'][clave] = x; u['carreras'].append(x)
    if sin: log('  programas de instituciones que no están en el registro de instituciones:', sum(sin.values()), sin.most_common(5))
    lista = []
    for u in inst.values():
        u.pop('_v'); lista.append(u)
    guardar('co', {'pais': 'Colombia', 'fuente': 'SNIES, Ministerio de Educación Nacional de Colombia', 'fuente_url': 'https://www.datos.gov.co/d/upr9-nkiz',
                   'fecha': datetime.date.today().isoformat(), 'nota': 'Cada programa aparece con el título oficial que otorga.', 'instituciones': lista})


# ------------------------------------------------------------------------------------------------ Chile
NIVEL_CL = {'Profesional Con Licenciatura': 'Profesional con licenciatura', 'Profesional Sin Licenciatura': 'Profesional', 'Técnico de Nivel Superior': 'Técnico de nivel superior',
            'Licenciatura No Conducente a Título': 'Licenciatura', 'Bachillerato, Ciclo Inicial o Plan Común': 'Bachillerato y plan común', 'Magister': 'Magíster',
            'Doctorado': 'Doctorado', 'Especialidad Médica U Odontológica': 'Especialidad médica u odontológica', 'Diplomado (desde un semestre)': 'Diplomado', 'Postítulo': 'Postítulo'}
IES_CL = {'Universidades': 'Universidad', 'Institutos Profesionales': 'Instituto profesional', 'Centros de Formación Técnica': 'Centro de formación técnica', 'FFAA': 'Institución de las Fuerzas Armadas'}
REG_CL = {"Lib. Gral. B. O'Higgins": "O'Higgins", 'Metropolitana': 'Región Metropolitana', 'Aysén': 'Aysén'}


def chile():
    import openpyxl
    log('Chile: SIES (mifuturo.cl)')
    html = get('https://www.mifuturo.cl/bases-de-datos-de-oferta-academica/')
    urls = re.findall(r'https?://(?:www\.)?mifuturo\.cl/wp-content/uploads/[^"\'\s]*Oferta_Academica_\d{4}_SIES[^"\'\s]*\.xlsx', html)
    if not urls: raise RuntimeError('No encuentro la base de oferta académica en mifuturo.cl')
    url = sorted(urls, key=lambda u: re.search(r'Oferta_Academica_(\d{4})', u).group(1))[-1]
    anio = re.search(r'Oferta_Academica_(\d{4})', url).group(1)
    log('  base', anio, url)
    ws = openpyxl.load_workbook(io.BytesIO(get(url, binario=True)), read_only=True).worksheets[0]
    filas = ws.iter_rows(values_only=True)
    cab = [limpio(x) for x in next(filas)]
    I = {k: cab.index(k) for k in cab}
    def v(f, k): return f[I[k]] if k in I and I[k] < len(f) else None
    inst, n_f = collections.OrderedDict(), 0
    for f in filas:
        if not f or not v(f, 'Nombre IES'): continue
        if not str(v(f, 'Vigencia') or '').startswith('Vigente con estudiantes nuevos'): continue
        if v(f, 'Nivel Carrera') in ('Diplomado (desde un semestre)', 'Postítulo'): continue   # formación continua: no son carreras
        n_f += 1
        cod = str(v(f, 'Código IES'))
        u = inst.get(cod)
        if not u:
            t3 = str(v(f, 'Tipo Institución 3') or '')
            tipo = 'pública' if re.search(r'Estatal|FFAA', t3) else 'privada'
            u = inst[cod] = {'cod': cod, 'nombre': acentuar(cap(limpio(v(f, 'Nombre IES')))), 'tipo': tipo, 'tipo_ies': IES_CL.get(v(f, 'Tipo Institución 1'), 'Institución de educación superior'),
                             'ciudad': '', 'region': '', 'web': '', 'extra': {'cod': cod, 'cruch': 'CRUCH' in t3}, 'carreras': [], '_v': {}, '_c': collections.Counter(), '_r': collections.Counter()}
        comuna = acentuar(cap(limpio(v(f, 'Comuna Sede'))))
        region = REG_CL.get(limpio(v(f, 'Región Sede')), limpio(v(f, 'Región Sede')))
        peso = 50 if 'CASA CENTRAL' in str(v(f, 'Nombre Sede') or '').upper() else 1
        u['_c'][comuna] += peso; u['_r'][region] += peso
        nom = acentuar(cap(limpio(v(f, 'Nombre Carrera'))))
        grupo = NIVEL_CL.get(limpio(v(f, 'Nivel Carrera')), limpio(v(f, 'Nivel Carrera')) or 'Otros')
        clave = (nrm(nom), grupo)
        mod = limpio(v(f, 'Modalidad')); jor = limpio(v(f, 'Jornada'))
        modj = mod if mod != 'Presencial' or not jor else f'{mod} {jor.lower()}'
        aran = v(f, 'Arancel Anual')   # solo importes en pesos; la fuente marca con «Formato Valor» los que vienen en otra unidad
        aran = int(aran) if isinstance(aran, (int, float)) and aran >= 50000 and 'Pesos' in str(v(f, 'Formato Valor') or '') else 0
        dur = v(f, 'Duración Total'); dur = int(dur) if isinstance(dur, (int, float)) and dur > 0 else 0
        x = u['_v'].get(clave)
        if x:
            if comuna and comuna not in x['sedes']: x['sedes'].append(comuna)
            if modj and modj not in x['mod']: x['mod'].append(modj)
            if aran: x['_a'].append(aran)
            if dur: x['_d'].append(dur)
            continue
        acred = str(v(f, 'Acreditación Carrera o Programa') or '') == 'Acreditada'
        x = {'n': nom, 'grupo': grupo, 'area': arreglar(limpio(v(f, 'Área Carrera Genérica'))), 'mod': [modj] if modj else [], 'sedes': [comuna] if comuna else [],
             'titulo': acentuar(cap(limpio(v(f, 'Nombre Título')))), 'acreditada': acred, '_a': [aran] if aran else [], '_d': [dur] if dur else []}
        u['_v'][clave] = x; u['carreras'].append(x)
    lista = []
    for u in inst.values():
        u['ciudad'] = u.pop('_c').most_common(1)[0][0] if u['carreras'] else ''
        u['region'] = u.pop('_r').most_common(1)[0][0] if u['carreras'] else ''
        u.pop('_v')
        for x in u['carreras']:
            a, d = sorted(set(x.pop('_a'))), sorted(set(x.pop('_d')))
            partes = []
            if d: partes.append((f'{d[0]} semestre' + ('s' if d[0] > 1 else '')) if len(d) == 1 else f'{d[0]}-{d[-1]} semestres')
            if a: partes.append(f'arancel {anio}: ' + ('$' + f'{a[0]:,}'.replace(',', '.') if len(a) == 1 else 'desde $' + f'{a[0]:,}'.replace(',', '.')) + ' al año')
            if x.pop('acreditada'): partes.append('acreditada')
            x['cred'] = ' · '.join(partes)
            if not x['titulo'] or nrm(x['titulo']) == nrm(x['n']) or re.search(r'no otorga|sin informacion|^titulo$', nrm(x['titulo'])): x.pop('titulo')
        lista.append(u)
    log(f'  {n_f} filas vigentes con estudiantes nuevos')
    guardar('cl', {'pais': 'Chile', 'fuente': f'SIES, Subsecretaría de Educación Superior de Chile (oferta académica {anio})', 'fuente_url': 'https://www.mifuturo.cl/bases-de-datos-de-oferta-academica/',
                   'fecha': datetime.date.today().isoformat(), 'nota': f'Oferta vigente con admisión de estudiantes nuevos en {anio}; aranceles en pesos chilenos.', 'instituciones': lista})


sys.path.insert(0, os.path.join(AQUI, '..', 'gen'))
from acentos import acentuar as _acentuar  # noqa: E402


def acentuar(t): return _acentuar(t, forzar=True)   # mismo diccionario que gen.py, palabra a palabra

if __name__ == '__main__':
    paises = sys.argv[1:] or ['co', 'cl']
    for iso, f in (('co', colombia), ('cl', chile)):
        if iso not in paises: continue
        try: f()
        except Exception as e: log(f'::warning::{iso}: no se pudo importar: {e}')
    open(os.path.join(DATOS, 'oficiales.log'), 'w', encoding='utf-8').write('\n'.join(LOG) + '\n')
