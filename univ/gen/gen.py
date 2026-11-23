# -*- coding: utf-8 -*-
"""Generador del portal de universidades de AURZANE NEXUS.

Entrada (carpeta de datos):
  sb_universidades.json.gz, sb_carreras.json.gz  -> exportación de Supabase
  ruct.json                                      -> España completa desde el RUCT (opcional)
  principales.json                               -> universidades principales de países nuevos (opcional)
Salida: carpeta lista para subir a nexus.aurzane.com/universidades/

Uso: python3 gen.py DATOS SALIDA
"""
import json, gzip, re, os, sys, html, unicodedata, collections, shutil, datetime, urllib.parse

DATOS, SALIDA = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(__file__))
HOY = datetime.date.today()
import hashlib
V = hashlib.md5(open(os.path.join(AQUI, 'univ.css'), 'rb').read() + open(os.path.join(AQUI, 'univ.js'), 'rb').read()).hexdigest()[:10]
SITIO = 'https://nexus.aurzane.com'
BASE = '/universidades/'
ADS = 'ca-pub-8763758728010451'

# ---------------------------------------------------------------- países
PAISES = {  # nombre: (iso, continente)
 'España': ('es', 'Europa'), 'Ecuador': ('ec', 'América Latina y el Caribe'), 'México': ('mx', 'América Latina y el Caribe'),
 'Colombia': ('co', 'América Latina y el Caribe'), 'Argentina': ('ar', 'América Latina y el Caribe'), 'Chile': ('cl', 'América Latina y el Caribe'),
 'Perú': ('pe', 'América Latina y el Caribe'), 'Bolivia': ('bo', 'América Latina y el Caribe'), 'Venezuela': ('ve', 'América Latina y el Caribe'),
 'Uruguay': ('uy', 'América Latina y el Caribe'), 'Paraguay': ('py', 'América Latina y el Caribe'), 'Brasil': ('br', 'América Latina y el Caribe'),
 'Costa Rica': ('cr', 'América Latina y el Caribe'), 'Panamá': ('pa', 'América Latina y el Caribe'), 'Guatemala': ('gt', 'América Latina y el Caribe'),
 'Honduras': ('hn', 'América Latina y el Caribe'), 'El Salvador': ('sv', 'América Latina y el Caribe'), 'Nicaragua': ('ni', 'América Latina y el Caribe'),
 'Cuba': ('cu', 'América Latina y el Caribe'), 'República Dominicana': ('do', 'América Latina y el Caribe'), 'Puerto Rico': ('pr', 'América Latina y el Caribe'),
 'Estados Unidos': ('us', 'América del Norte'), 'Canadá': ('ca', 'América del Norte'),
 'Reino Unido': ('gb', 'Europa'), 'Francia': ('fr', 'Europa'), 'Alemania': ('de', 'Europa'), 'Italia': ('it', 'Europa'), 'Portugal': ('pt', 'Europa'),
 'Países Bajos': ('nl', 'Europa'), 'Suiza': ('ch', 'Europa'), 'Bélgica': ('be', 'Europa'), 'Irlanda': ('ie', 'Europa'), 'Austria': ('at', 'Europa'),
 'Suecia': ('se', 'Europa'), 'Dinamarca': ('dk', 'Europa'), 'Noruega': ('no', 'Europa'), 'Finlandia': ('fi', 'Europa'), 'Polonia': ('pl', 'Europa'),
 'Grecia': ('gr', 'Europa'), 'Chequia': ('cz', 'Europa'), 'Rusia': ('ru', 'Europa'),
 'China': ('cn', 'Asia'), 'Japón': ('jp', 'Asia'), 'Corea del Sur': ('kr', 'Asia'), 'India': ('in', 'Asia'), 'Singapur': ('sg', 'Asia'),
 'Filipinas': ('ph', 'Asia'), 'Israel': ('il', 'África y Oriente Medio'), 'Turquía': ('tr', 'Asia'), 'Emiratos Árabes Unidos': ('ae', 'África y Oriente Medio'),
 'Egipto': ('eg', 'África y Oriente Medio'), 'Marruecos': ('ma', 'África y Oriente Medio'), 'Sudáfrica': ('za', 'África y Oriente Medio'),
 'Australia': ('au', 'Oceanía'), 'Nueva Zelanda': ('nz', 'Oceanía'),
}
CONTINENTES = ['América Latina y el Caribe', 'Europa', 'América del Norte', 'Asia', 'África y Oriente Medio', 'Oceanía']
EN_LINEA_ES = {'028', '054', '074', '076', '077', '080', '094', '108'}  # UNED, UOC, UDIMA, VIU, UNIR, Isabel I, UNIE, UNINDE


def slug(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('ñ', 'n')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:90] or 'x'


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def fmt(n):
    return f'{n:,}'.replace(',', '.')


# acentos (Ecuador, Chile, Colombia): univ/gen/acentos.py
from acentos import ACENTOS, acentuar  # noqa: E402


def titulo(t):
    t = re.sub(r'\s+', ' ', str(t or '')).strip()
    if t.isupper() and len(t) > 4:
        menores = {'de', 'del', 'la', 'las', 'los', 'y', 'en', 'e', 'o', 'a', 'el', 'para', 'con'}
        t = ' '.join(w.lower() if w.lower() in menores and i else w.capitalize() for i, w in enumerate(t.lower().split()))
    return t


TIPO_GRUPO = {'pública': 'Pública', 'privada': 'Privada', 'privada cofinanciada': 'Privada', 'privada con fines de lucro': 'Privada'}
TIPO_TXT = {'pública': 'Pública', 'privada': 'Privada', 'privada cofinanciada': 'Privada cofinanciada', 'privada con fines de lucro': 'Privada con fines de lucro'}
NIVEL_TXT = {'Universitario (grado)': 'Grado', 'Técnico/Tecnológico superior': 'Técnico y tecnológico superior'}

# ---------------------------------------------------------------- carga
def cargar_json(n):
    p = os.path.join(DATOS, n)
    if not os.path.exists(p):
        return None
    return json.load(gzip.open(p, 'rt', encoding='utf-8') if n.endswith('.gz') else open(p, encoding='utf-8'))


SBU = cargar_json('sb_universidades.json.gz')
SBC = cargar_json('sb_carreras.json.gz')
RUCT = cargar_json('ruct.json')
PRIN = cargar_json('principales.json')
UNIS = []
# Ranking mundial abierto (OpenAlex, CC0): lo prepara cada mes univ/ranking.py
RANK = cargar_json('ranking.json') or {'dom': {}, 'nom': {}}
# patrocinios (17/11/2026, etapa 4, tarea 46): solo los vigentes hoy; caducan solos
PRECIO = (cargar_json('patrocinios.json') or {}).get('precio') or {}
PINFO = cargar_json('paises_info.json') or {}   # idiomas, moneda y capital (univ/paises_info.py)
PATRO = {x['id']: x for x in ((cargar_json('patrocinios.json') or {}).get('lista') or [])
         if x.get('id') and x.get('url', '').startswith('https://') and str(x.get('desde', '')) <= datetime.date.today().isoformat() <= str(x.get('hasta', '9999'))}


def patro(u):
    return PATRO.get(PSLUG[u['pais']] + '/' + u['slug'])


def utm(url, donde):
    return url + ('&' if '?' in url else '?') + 'utm_source=aurzane&utm_medium=nexus&utm_campaign=patrocinio&utm_content=' + donde


def _dom(u):
    if not u: return ''
    h = urllib.parse.urlparse(u if '//' in u else 'http://' + u).netloc.lower().split(':')[0]
    return re.sub(r'^(www\d?|web|portal|en|es)\.', '', h)


def _nrm(t):
    t = unicodedata.normalize('NFD', (t or '').lower()); t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', t).strip()


def rank_de(u):
    """[posición mundial, posición en su país, índice h, publicaciones, citas, id OpenAlex] o None."""
    r = RANK['dom'].get(_dom(u.get('web')))
    if not r:
        iso = (PAISES.get(u['pais']) or ('',))[0]
        r = RANK['nom'].get(iso.lower() + '|' + _nrm(u['nombre']))
    return r

# Universidades que ya vienen del RUCT en Supabase (tras la importación) se reconocen por fuente
RUCT_EN_SB = any((u.get('fuente') or '') == 'RUCT' for u in SBU)

carr_por_u = collections.defaultdict(list)
for c in SBC:
    carr_por_u[c['universidad_id']].append(c)


def moda(vals):
    vals = [v for v in vals if v]
    return collections.Counter(vals).most_common(1)[0][0] if vals else ''


for u in SBU:
    if u['pais'] == 'España' and RUCT and not RUCT_EN_SB:
        continue  # se sustituye por el RUCT
    if u.get('visible') is False:
        continue
    cs = carr_por_u[u['id']]
    reales = [c for c in cs if c.get('nivel_detalle') in ('programa', 'area_facultad')]
    nivel = 'programas' if any(c.get('nivel_detalle') == 'programa' for c in cs) else ('areas' if reales else 'basico')
    carreras = []
    vistos = {}
    for c in reales:
        nom = titulo(acentuar(c['nombre'])) if u['pais'] == 'Ecuador' else titulo(c['nombre'])
        k = slug(nom)
        area = c.get('rama') or (acentuar(c.get('campo_amplio')) if c.get('campo_amplio') else '')
        grupo = c.get('rama') or (NIVEL_TXT.get(c.get('nivel_categoria') or '', '') if nivel == 'programas' else 'Áreas y facultades')
        sedes_c = [x.strip() for x in (c.get('sedes') or '').split(',') if x.strip()] or ([c['canton']] if c.get('canton') else [])
        cred = c.get('creditos')
        cred = (str(int(cred)) if float(cred) == int(float(cred)) else str(cred)) if cred not in (None, '') else ''
        if k in vistos:
            x = vistos[k]
            x.setdefault('cods', []).append(c.get('codigo_externo') or '')
            if c.get('modalidad') and c['modalidad'] not in x['mod']: x['mod'].append(c['modalidad'])
            for sd in sedes_c:
                if sd not in x['sedes']: x['sedes'].append(sd)
            continue
        x = {'n': nom, 'area': area, 'grupo': grupo or 'Grado', 'campo': c.get('campo_amplio') if c.get('rama') else '', 'mod': [c['modalidad']] if c.get('modalidad') else [], 'sedes': sedes_c, 'cred': cred, 'prof': c.get('profesion_regulada') or '', 'cods': [c.get('codigo_externo') or '']}
        vistos[k] = x
        carreras.append(x)
    UNIS.append({
        'id': u['id'], 'pais': u['pais'], 'nombre': titulo(acentuar(u['nombre'])) if u['pais'] == 'Ecuador' else titulo(u['nombre']), 'tipo_raw': (u.get('tipo') or '').lower(),
        'tipo_ies': u.get('tipo_ies') or 'Universidad', 'web': u.get('sitio_web') or '', 'logo': u.get('logo_url') or '',
        'ciudad': u.get('ciudad') or moda([c.get('canton') for c in cs]), 'region': u.get('region') or moda([c.get('provincia') for c in cs]),
        'nivel': nivel, 'carreras': carreras, 'fuente': u.get('fuente') or 'catalogo', 'descripcion': u.get('descripcion') or '',
        'extra': {'acronimo': u.get('acronimo') or '', 'anio': str(u['anio_creacion']) if u.get('anio_creacion') else '', 'en_linea': bool(u.get('en_linea')), 'cod': u.get('codigo_externo') or ''},
        'destacada': bool(u.get('destacada')),
    })

# --- España desde el RUCT
if RUCT and not RUCT_EN_SB:
    centros = RUCT.get('centros', {})
    for cod, r in RUCT['universidades'].items():
        f = r.get('ficha', {})
        tipo = (f.get('Tipo') or '').lower()
        web = (f.get('URL') or '').split()[0] if f.get('URL') else ''
        if web and not web.startswith('http'): web = 'https://' + web
        region = re.sub(r'^(Comunidad (Autónoma )?(de |del )?|Comunitat |Comunidad Foral de |Principado de |Región de |Illes |Islas )', '', f.get('Comunidad Autónoma') or '').strip()
        region = {'Valenciana': 'Comunidad Valenciana', 'Madrid': 'Comunidad de Madrid', 'Navarra': 'Navarra', 'Balears': 'Islas Baleares', 'Baleares': 'Islas Baleares'}.get(region, region)
        carreras, vistos = [], {}
        for g in r.get('grados', []):
            nom = g.get('denominacion') or g.get('titulo')
            sedes = []
            for c in g.get('centros', []):
                cc = centros.get(c['univ'] + '-' + c['codigo'], {})
                muni = cc.get('Municipio') or ''
                if muni and muni not in sedes: sedes.append(muni)
            k = slug(nom)
            if k in vistos:
                for s in sedes:
                    if s not in vistos[k]['sedes']: vistos[k]['sedes'].append(s)
                continue
            x = {'n': nom, 'area': g.get('rama') or '', 'grupo': g.get('rama') or 'Grado', 'campo': g.get('campo') or '', 'mod': ['En línea'] if cod in EN_LINEA_ES else [],
                 'sedes': sedes, 'cred': g.get('creditos') or '', 'centros': [c['nombre'] for c in g.get('centros', [])]}
            vistos[k] = x
            carreras.append(x)
        anio = f.get('Año publicación') or ''
        UNIS.append({
            'id': 'ruct-' + cod, 'pais': 'España', 'nombre': r['nombre'], 'tipo_raw': 'pública' if tipo.startswith('p') and 'priv' not in tipo else 'privada',
            'tipo_ies': 'Universidad', 'web': web, 'logo': '', 'ciudad': f.get('Municipio') or f.get('Localidad') or '', 'region': region,
            'nivel': 'programas' if carreras else 'basico', 'carreras': carreras, 'fuente': 'RUCT', 'descripcion': '', 'destacada': False,
            'extra': {'acronimo': f.get('Acrónimo') or '', 'anio': anio if re.match(r'^\d{3,4}$', anio) else '', 'cod': cod, 'en_linea': cod in EN_LINEA_ES},
        })

# --- universidades principales de países nuevos
if PRIN:
    ya = {(u['pais'], slug(u['nombre'])) for u in UNIS}
    for p in PRIN:
        if (p['pais'], slug(p['nombre'])) in ya:
            continue
        UNIS.append({'id': 'prin-' + slug(p['pais']) + '-' + slug(p['nombre']), 'pais': p['pais'], 'nombre': p['nombre'], 'tipo_raw': p['tipo'].lower(),
                     'tipo_ies': 'Universidad', 'web': p.get('web_final') or p['web'], 'logo': '', 'ciudad': p['ciudad'], 'region': '', 'nivel': 'basico', 'carreras': [],
                     'fuente': 'principales', 'descripcion': '', 'destacada': False, 'extra': {}})

# --- datos abiertos oficiales por país (univ/oficiales/importar.py → univ/data/oficial_<iso>.json, 23/11/2026)
# Completan las fichas que ya existen (misma dirección: se conserva el nombre y el id) con la oferta oficial vigente y añaden las que faltan.
OFICIAL = {}
for _f in sorted(os.listdir(DATOS)):
    if not re.match(r'^oficial_[a-z]{2}\.json$', _f): continue
    _o = cargar_json(_f)
    if not _o or not _o.get('instituciones'): continue
    _p = _o['pais']; OFICIAL[_p] = _o
    _vie = [u for u in UNIS if u['pais'] == _p]
    _por_dom = {_dom(u['web']): u for u in _vie if u['web'] and _dom(u['web'])}
    _por_nom = {_nrm(re.sub(r'\(.*?\)', '', u['nombre'])): u for u in _vie}
    _usadas, _n_nuevas, _n_casan = set(), 0, 0

    def _pareja(x):
        u = _por_dom.get(_dom(x['web'])) if x.get('web') else None
        k = _nrm(re.sub(r'\(.*?\)', '', x['nombre']))
        u = u or _por_nom.get(k)
        if not u and len(k) > 14:   # «Universidad de Playa Ancha» ↔ «Universidad de Playa Ancha de Ciencias de la Educación»
            c = [v for kk, v in _por_nom.items() if len(kk) > 14 and (kk.startswith(k + ' ') or k.startswith(kk + ' '))]
            u = c[0] if len(c) == 1 else None
        return u if u and u['id'] not in _usadas else None
    for x in _o['instituciones']:
        cs = [{'n': c['n'], 'area': c.get('area', ''), 'grupo': c.get('grupo') or 'Grado', 'campo': '', 'mod': c.get('mod') or [], 'sedes': c.get('sedes') or [],
               'cred': c.get('cred', ''), 'prof': '', 'titulo': c.get('titulo', '')} for c in x['carreras']]
        u = _pareja(x)
        if u:
            _usadas.add(u['id']); _n_casan += 1
            if cs: u['carreras'], u['nivel'] = cs, 'programas'
            u['web'] = u['web'] or x.get('web', '')
            if x.get('tipo'): u['tipo_raw'] = x['tipo']   # el registro oficial manda sobre el dato antiguo (p. ej. la Católica es privada)
            if x.get('tipo_ies'): u['tipo_ies'] = x['tipo_ies']
            u['ciudad'] = u['ciudad'] or x.get('ciudad', ''); u['region'] = u['region'] or x.get('region', '')
            for k2, v2 in (x.get('extra') or {}).items():
                if v2 and not u['extra'].get(k2): u['extra'][k2] = v2
        else:
            _n_nuevas += 1
            u = {'id': f'ofi-{_f[8:10]}-{x["cod"]}', 'pais': _p, 'nombre': x['nombre'], 'tipo_raw': x['tipo'], 'tipo_ies': x['tipo_ies'], 'web': x.get('web', ''), 'logo': '',
                 'ciudad': x.get('ciudad', ''), 'region': x.get('region', ''), 'nivel': 'programas' if cs else 'basico', 'carreras': cs, 'descripcion': '', 'destacada': False,
                 'extra': dict(x.get('extra') or {})}
            UNIS.append(u)
        u['fuente'] = _o['fuente']; u['extra']['fuente_url'] = _o.get('fuente_url', ''); u['extra']['fuente_fecha'] = _o.get('fecha', '')
        if _o.get('nota'): u['extra']['fuente_nota'] = _o['nota']
    print(f'Oficiales {_p}: {_n_casan} fichas completadas · {_n_nuevas} nuevas · {sum(len(x["carreras"]) for x in _o["instituciones"])} carreras')

ORDEN_NIVEL = ['Pregrado universitario', 'Profesional con licenciatura', 'Profesional', 'Licenciatura', 'Bachillerato y plan común', 'Técnico de nivel superior',
               'Tecnológico', 'Técnico profesional', 'Especialización', 'Especialización médico-quirúrgica', 'Especialidad médica u odontológica', 'Magíster',
               'Maestría', 'Doctorado', 'Otros']

# --- slugs únicos por país
por_pais = collections.defaultdict(list)
for u in UNIS:
    if u['pais'] not in PAISES:
        print('AVISO país sin metadatos:', u['pais']); PAISES[u['pais']] = ('', 'Asia')
    u['tipo'] = TIPO_GRUPO.get(u['tipo_raw'], u['tipo_raw'].capitalize())
    u['tipo_txt'] = TIPO_TXT.get(u['tipo_raw'], u['tipo_raw'].capitalize())
    u['n'] = len(u['carreras'])
    por_pais[u['pais']].append(u)
for u in UNIS:
    if u['web'] and not re.match(r'^https?://[^\s<>]+$', u['web']):
        u['web'] = ''

# --- notas de corte oficiales (QEDU) para grados de universidades españolas
NC = cargar_json('notas_corte.json') or {'filas': []}
# Datos oficiales de EE. UU. (College Scorecard, Departamento de Educación): admisión, costes, becas y resultados (19/11/2026)
SC = (cargar_json('scorecard.json') or {}).get('universidades', {})
_PCT = lambda x: f'{round(x * 100)} %'
_USD = lambda x: f'{fmt(int(round(x)))} $'
def bloque_scorecard(u):
    d = SC.get(u['id'])
    if not d: return ''
    neto = d.get('precio_neto_pub') if d.get('control') == 1 else d.get('precio_neto_priv')
    filas = []
    if d.get('admision') is not None: filas.append(('Tasa de admisión', _PCT(d['admision']), f'De cada 100 solicitudes, se admiten {round(d["admision"] * 100)}.'))
    sat = [d.get(k) for k in ('sat_lec_25', 'sat_mat_25', 'sat_lec_75', 'sat_mat_75')]
    if all(v is not None for v in sat): filas.append(('SAT de los admitidos', f'{fmt(int(sat[0] + sat[1]))} a {fmt(int(sat[2] + sat[3]))}', 'La mitad de los admitidos saca una nota en este rango (lectura y matemáticas, sobre 1.600).'))
    if d.get('act_25') is not None and d.get('act_75') is not None: filas.append(('ACT de los admitidos', f'{int(d["act_25"])} a {int(d["act_75"])}', 'La mitad de los admitidos está en este rango (sobre 36).'))
    if d.get('matricula_fuera') is not None:
        filas.append(('Matrícula al año', _USD(d['matricula_fuera']),
                      'Precio oficial de un curso (matrícula y tasas) para quien no reside en el estado; es el que suelen pagar los estudiantes internacionales.' +
                      (f' Para residentes del estado: {_USD(d["matricula_estado"])}.' if d.get('matricula_estado') and d.get('matricula_estado') != d.get('matricula_fuera') else '')))
    if neto is not None: filas.append(('Precio neto medio al año', _USD(neto), 'Lo que paga de media un estudiante de primer curso con ayuda federal, contando alojamiento y comida y restando becas.'))
    if d.get('beca_pell') is not None: filas.append(('Con beca Pell', _PCT(d['beca_pell']), 'Estudiantes de grado que reciben la beca federal Pell.'))
    if d.get('permanencia') is not None: filas.append(('Siguen tras el primer año', _PCT(d['permanencia']), 'Estudiantes de primer curso a tiempo completo que continúan al año siguiente.'))
    if d.get('graduacion_6') is not None: filas.append(('Se gradúan', _PCT(d['graduacion_6']), 'Terminan un grado de 4 años en un máximo de 6.'))
    if d.get('salario_10') is not None: filas.append(('Salario 10 años después', _USD(d['salario_10']) + ' al año', 'Sueldo mediano de quienes empezaron aquí, diez años después de entrar.'))
    if d.get('deuda_mediana') is not None: filas.append(('Deuda al terminar', _USD(d['deuda_mediana']), 'Préstamo federal mediano de quienes terminan los estudios.'))
    if d.get('estudiantes_grado'): filas.append(('Estudiantes de grado', fmt(int(d['estudiantes_grado'])), ''))
    if not filas: return ''
    tipo = {1: 'pública', 2: 'privada sin ánimo de lucro', 3: 'privada con ánimo de lucro'}.get(d.get('control'), '')
    dl = ''.join(f'<div><dt>{e(a)}</dt><dd><b>{e(b)}</b>{f"<small>{e(c)}</small>" if c else ""}</dd></div>' for a, b, c in filas)
    nota = ('<p class="sub" style="margin-top:12px"><b>Si vienes de fuera de EE. UU.:</b> la beca Pell y los préstamos federales son solo para ciudadanos y residentes. '
            'Pregunta a la universidad por sus becas para estudiantes internacionales (<i>international student scholarships</i>) y por el coste total del curso (<i>cost of attendance</i>).</p>')
    return (f'<section class="card" id="admision-costes"><h2>Admisión, costes y becas</h2>' + (f'<p class="sub">Institución {e(tipo)}.</p>' if tipo else '') +
            f'<dl class="datos sc-datos">{dl}</dl>{nota}<p class="fuente" style="margin:10px 0 0">Fuente: <a href="https://collegescorecard.ed.gov/school/?{int(d["unitid"])}" target="_blank" rel="noopener">College Scorecard</a>, Departamento de Educación de EE. UU. (datos oficiales; se actualizan solos cada mes).</p></section>')

NC_COD = collections.defaultdict(list)  # (cod_univ, cod_titulo) -> filas
for f in NC['filas']:
    NC_COD[(f.get('cod_univ') or '', f.get('cod_titulo') or '')].append(f)
NC_CURSO = next((f['curso'] for f in NC['filas'] if f.get('curso')), '')
for u in UNIS:
    if u['pais'] != 'España': continue
    cu = u['extra'].get('cod', '')
    for c in u['carreras']:
        notas = [f['nota'] for cd in c.get('cods', []) for f in NC_COD.get((cu, cd), []) if f.get('nota')]
        if notas: c['nota'] = min(notas)
print('Notas de corte:', sum(1 for u in UNIS for c in u['carreras'] if c.get('nota')), 'grados con nota', NC_CURSO)

# --- imágenes de Wikimedia Commons (univ/data/imagenes.json, lo genera imagenes.py desde Wikidata)
IMG = cargar_json('imagenes.json') or {'u': {}, 'c': {}}
def _n(t):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()
def _dom(w):
    w = re.sub(r'^https?://', '', (w or '').lower()).split('/')[0]
    return re.sub(r'^www\d?\.', '', w)
ANCHOS_WM = (120, 250, 330, 500, 960, 1280, 1920)   # tamaños estándar de Wikimedia: salen de su caché (17/11/2026, auditoría final)


# Espejo propio (22/11/2026, pedido de Adrián): las fotos de Commons se guardan en nuestro servidor en AVIF
# (flujo «Universidades: fotos en nuestro servidor», univ/espejo.py); las que ya están se sirven desde allí.
ESPEJO = cargar_json('espejo.json') or {}
def commons(f, ancho=500, local=False):   # local=True usaría las copias en SiteGround (desactivado el 22/11/2026)
    if local and f and f in ESPEJO:
        return f'https://nexus.aurzane.com/universidades/img/{ESPEJO[f]}-{330 if ancho <= 330 else 960}.avif'
    ancho = min((a for a in ANCHOS_WM if a >= ancho), default=1920)
    return 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(f.replace(' ', '_')) + f'?width={ancho}' if f else ''
IMG_DOM, IMG_NOM = collections.defaultdict(dict), collections.defaultdict(dict)
GEN_UNIV = ['1541339907198-e08756dedf3f', '1562774053-701939374585', '1592280771190-3e2e4d571952', '1607237138185-eedd9c632b0b', '1576495199011-eb94736d05d6', '1606761568499-6d2451b23c66', '1427504494785-3a9ca7044f45']
GEN_INST = ['1580582932707-520aed937b7b', '1524178232363-1fb2b075b655', '1523240795612-9a054b0db644', '1541829070764-84a7d30dd3f3', '1517486808906-6ca8b3f04846', '1498243691581-b145c3f54a5a']
for iso, lst in IMG.get('u', {}).items():
    for nom, dom, foto, logo in lst:
        if dom: IMG_DOM[iso].setdefault(dom, (foto, logo))
        IMG_NOM[iso].setdefault(_n(nom), (foto, logo))
n_foto = n_ciudad = 0
for u in UNIS:
    iso = PAISES.get(u['pais'], ('',))[0]
    d = _dom(u['web'])
    hit = IMG_DOM[iso].get(d) or (IMG_DOM[iso].get(d.split('.', 1)[1]) if d.count('.') >= 2 else None) or IMG_NOM[iso].get(_n(u['nombre']))
    foto, logo = hit if hit else ('', '')
    u['foto_archivo'], u['foto_tipo'] = foto, 'u' if foto else ''
    fc = IMG.get('c', {}).get(iso, {}).get(_n(u['ciudad']))
    u['foto_ciudad'] = fc or ''  # para la cabecera de la ficha; en las tarjetas se usa foto propia o de ambiente para no repetir
    if logo and not u.get('logo'): u['logo'] = commons(logo, 120)
    n_foto += u['foto_tipo'] == 'u'; n_ciudad += u['foto_tipo'] == 'c'
    u['foto'] = commons(u['foto_archivo'])
    if not u['foto']:  # foto genérica de ambiente universitario (Unsplash, uso libre), estable por institución
        pool = GEN_INST if re.match(r'^(instituto|escuela|conservatorio|centro)', (u['tipo_ies'] or '') + ' ' + u['nombre'], re.I) and not re.match(r'^universi', u['nombre'], re.I) else GEN_UNIV
        u['foto'] = 'https://images.unsplash.com/photo-' + pool[int(hashlib.md5(u['nombre'].encode()).hexdigest(), 16) % len(pool)] + '?w=640&q=70&auto=format&fit=crop'
print('Imágenes:', n_foto, 'fotos propias,', n_ciudad, 'fotos de su ciudad')
for p, us in por_pais.items():
    usados = collections.Counter()
    for u in sorted(us, key=lambda x: (-x['n'], x['nombre'])):
        s = slug(u['nombre'])
        if usados[s]:
            s = slug(u['nombre'] + ' ' + (u['ciudad'] or u['region'] or str(usados[s] + 1)))
            while usados[s]: s = s + '-' + str(usados[s] + 1)
        usados[s] += 1
        u['slug'] = s
    us.sort(key=lambda x: x['nombre'].lower())

PSLUG = {p: slug(p) for p in PAISES}
ORDEN_P = sorted(por_pais, key=lambda p: (-len(por_pais[p]), p))
TOTAL_U = len(UNIS)
TOTAL_C = sum(u['n'] for u in UNIS)


def nivel_pais(p):
    c = collections.Counter(u['nivel'] for u in por_pais[p])
    return 'programas' if c['programas'] >= max(1, len(por_pais[p]) * .5) else ('areas' if c['areas'] + c['programas'] >= len(por_pais[p]) * .4 else 'basico')


NIVEL_LBL = {'programas': 'Con todas sus carreras', 'areas': 'Con áreas y facultades', 'basico': 'Universidades principales'}

# ---------------------------------------------------------------- plantillas comunes
def bandera(iso, cls=''):
    return f'<img class="bandera {cls}" src="https://flagcdn.com/w40/{iso}.png" srcset="https://flagcdn.com/w80/{iso}.png 2x" alt="" width="28" height="21" loading="lazy">' if iso else ''


def iniciales(n):
    w = [x for x in re.sub(r'\(.*?\)', '', n).split() if len(x) > 2 and x.lower() not in {'de', 'del', 'la', 'las', 'los', 'y', 'en', 'para', 'the', 'of', 'and', 'for', 'und', 'der', 'di', 'du', 'des'}]
    return (''.join(x[0] for x in w[:2]) or n[:2]).upper()


# títulos y descripciones reescritos a partir de lo que la gente busca en Google (seo/seo.py, Search Console)
try: GSC_T = json.load(open(os.path.join(DATOS, 'gsc_titulos.json'), encoding='utf-8'))
except Exception: GSC_T = {}


# textos ampliados escritos por la IA para las fichas que la gente ve en Google (seo/seo.py)
try: FICHAS_IA = json.load(open(os.path.join(DATOS, 'fichas_ia.json'), encoding='utf-8'))
except Exception: FICHAS_IA = {}


from acceso import acceso as _acceso, ELEGIR as _ELEGIR


def bloque_auto(u, orden_g, grupos):
    """Texto propio de cada ficha a partir de sus datos y del sistema universitario de su país (sin datos inventados)."""
    p, n = u['pais'], u['n']
    lugar = ', '.join(x for x in [u['ciudad'], u['region']] if x) or p
    tipo = (u['tipo_txt'] or '').lower()
    ies = (u['tipo_ies'] or 'institución de educación superior').lower()
    palabra = 'grados' if p == 'España' else 'carreras'
    top = [g for g in orden_g if g and g not in ('Otras', 'Grado', 'Posgrado', 'Máster', 'Doctorado', 'Técnico y tecnológico superior', 'Tecnológico', 'Técnico')][:3]
    masc = re.match(r'(instituto|conservatorio|centro|colegio|seminario|campus)', ies) or 'college' in ies
    tipo_g = (re.sub(r'a$', 'o', tipo) if masc and tipo in ('pública', 'privada', 'cofinanciada') else tipo)
    intro = f'{u["nombre"]} es {"un" if masc else "una"} {ies}' + (f' {tipo_g}' if tipo_g and tipo_g != '-' else '') + f' con sede en {lugar}.'
    if n:
        intro += (f' En el catálogo de AURZANE {"figura 1 " + palabra[:-1] + (" suyo" if palabra == "grados" else " suya") if n == 1 else "figuran " + fmt(n) + " " + palabra + (" suyos" if palabra == "grados" else " suyas")}'
                  + ((f', sobre todo en las áreas de {", ".join(top[:-1])} y {top[-1]}' if len(top) > 1 else f', en el área de {top[0]}') if top else '') + '.')
        intro += f' Puedes buscar dentro de la lista por nombre o filtrar por área para ver todas las opciones.'
    else:
        intro += f' Todavía no tenemos su listado de {palabra}; puedes consultarlo en su web oficial.'
    if u['extra'].get('anio'): intro += f' Fue creada en {u["extra"]["anio"]}.'
    if u['extra'].get('en_linea'): intro += ' Ofrece estudios en línea, lo que permite estudiar sin mudarse a la ciudad.'
    acc = ''.join(f'<p>{e(x)}</p>' for x in _acceso(p))
    faq = [(f'¿{u["nombre"]} es pública o privada?', f'Según los datos oficiales que recogemos, es una institución {tipo}.' if tipo and tipo != '-' else 'No consta en nuestros datos; consúltalo en su web oficial.'),
           (f'¿Dónde está {u["nombre"]}?', f'Su sede está en {lugar}.' + (' También ofrece estudios en línea.' if u['extra'].get('en_linea') else '')),
           (f'¿Qué se puede estudiar en {u["nombre"]}?', (f'En nuestro catálogo tiene {fmt(n)} {palabra if n > 1 else palabra[:-1]}' + (f', con más oferta en {", ".join(top)}' if top and n > 1 else '') + '. La lista completa está más arriba.') if n else 'Consulta su oferta completa en su web oficial.'),
           (f'¿Cómo se entra a la universidad en {p}?', _acceso(p)[0])]
    faq_h = ''.join(f'<details><summary>{e(q)}</summary><p>{e(r)}</p></details>' for q, r in faq)
    return (f'<section class="card guia-auto"><h2>Sobre {e(u["nombre"])}</h2><p>{e(intro)}</p>'
            f'<h3>Cómo es el acceso a la universidad en {e(p)}</h3>{acc}<h3>Cómo elegir carrera</h3><p>{e(_ELEGIR)}</p>'
            f'<h3>Preguntas frecuentes</h3>{faq_h}</section>')


def bloque_ia(url):
    g = FICHAS_IA.get(url)
    if not g: return ''
    par = ''.join(f'<p>{e(x)}</p>' for x in g.get('parrafos', []))
    faq = ''.join(f'<details><summary>{e(f["p"])}</summary><p>{e(f["r"])}</p></details>' for f in g.get('faq', []))
    return (f'<section class="card guia-ia"><h2>{e(g.get("titulo") or "Guía para futuros estudiantes")}</h2>{par}'
            + (f'<h3>Preguntas frecuentes</h3>{faq}' if faq else '') + '<p class="sub" style="font-size:.85rem">Texto orientativo elaborado por AURZANE a partir de los datos de esta ficha. Confirma requisitos, plazos y precios en la web oficial de la institución.</p></section>')


def acortar(t, m=60):
    """Títulos de 60 caracteres como máximo (Google corta a partir de ~60): se quitan primero los sufijos «| …»,
    después los añadidos menos útiles y, si aún sobra, se corta por palabra sin dejar conectores al final."""
    if len(t) <= m: return t
    partes = t.split(' | ')
    while len(partes) > 1 and len(' | '.join(partes)) > m: partes.pop()
    t = ' | '.join(partes)
    for q in (', públicas y privadas', ', ciudad y web', ' y dónde están', ' instituciones'):
        if len(t) > m and q in t: t = t.replace(q, '' if q != ' instituciones' else ' centros')
    if len(t) > m: t = re.sub(r' y (sus )?[\d.]+ (carreras|grados)', '', t)
    if len(t) <= m: return t
    anio = ' (2026)' if t.endswith(' (2026)') else ''
    base = t[:-len(anio)] if anio else t
    pal = base[:m - len(anio) + 1].rsplit(' ', 1)[0]
    pal = re.sub(r'(\s+(y|de|del|la|las|el|los|en|a|e|o|u|sus|[\d.]+))+$', '', pal).rstrip(' ,:;-')
    return pal + anio


CIUDAD_PAISES = collections.defaultdict(set)


ES_CON_EN = set()   # fichas de España que tienen versión en inglés (univ/gen/en.py): se enlazan con hreflang
def _alt_en(canon):
    m = re.match(re.escape(SITIO + BASE) + r'espana/([^/]+)/$', canon)
    en = (f'{SITIO}/en/universities/{m.group(1)}/' if m and m.group(1) in ES_CON_EN else (f'{SITIO}/en/universities/' if canon == SITIO + BASE + 'espana/' else ''))
    return (f'<link rel="alternate" hreflang="es" href="{e(canon)}"><link rel="alternate" hreflang="en" href="{e(en)}"><link rel="alternate" hreflang="x-default" href="{e(canon)}">') if en else ''
ES_CON_EN.update(u['slug'] for u in por_pais.get('España', []) if u['n'])


def cabeza(titulo_pag, desc, canon, og_img=None, jsonld=None, robots=None, precarga=None):
    _o = GSC_T.get(canon) or {}
    titulo_pag = _o.get('titulo') or titulo_pag; desc = _o.get('desc') or desc
    titulo_pag = acortar(titulo_pag)
    og_img = og_img or f'{SITIO}/universidades/og.jpg'
    return f'''<!DOCTYPE html>
<html lang="es" data-v="{V}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>{e(titulo_pag)}</title>
{f'<link rel="preload" as="image" href="{e(precarga)}" fetchpriority="high">' if precarga else ''}
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
{_alt_en(canon)}
{f'<meta name="robots" content="{robots}">' if robots else ''}
<meta property="og:title" content="{e(titulo_pag)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{e(og_img)}">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b1030">
<script>(function(){{try{{if(localStorage.getItem('aurzane-tema')==='oscuro')document.documentElement.setAttribute('data-tema','oscuro');}}catch(e){{}}}})();</script>
{f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@500;700&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}assets/univ.css?v={V}">
<meta name="google-adsense-account" content="{ADS}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>
</head>
<body>
<div class="utility"><div class="wrap"><div class="eco"><a href="https://aurzane.com/">AURZANE</a><a href="https://mind.aurzane.com/">MIND</a><a href="https://ovp.aurzane.com/">OVP</a><a class="activo" href="https://nexus.aurzane.com/">NEXUS</a><a href="https://live.aurzane.com/">LIVE</a><a href="https://learn.aurzane.com/">LEARN</a><a href="https://build.aurzane.com/">BUILD</a></div><button type="button" id="btnTema">🌓 Tema</button></div></div>
'''


def topbar(actual=''):
    def a(href, txt, k):
        return f'<a href="{href}"{" aria-current=page" if k == actual else ""}>{txt}</a>'
    return f'''<header class="topbar"><div class="wrap">
<a class="brand" href="https://nexus.aurzane.com/">AUR<span class="z">Z</span>ANE<small>/ NEXUS</small></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="topnav">☰ Menú</button>
<nav class="topnav" id="topnav" aria-label="Universidades">
{a(BASE, 'Universidades', 'inicio')}
{a(BASE + 'espana/', 'España', 'espana')}
{a(BASE + 'paises/', 'Países', 'paises')}
{a(BASE + 'notas-de-corte/', 'Notas de corte', 'nc')}
{a('/calculadora-nota-pau/', 'Nota PAU', 'pau')}
{a(BASE + 'mi-lista/', 'Mi lista <span class="lista-n" hidden>0</span>', 'lista')}
<a class="cuenta" href="https://aurzane.com/mi-aurzane.html">👤 Mi AURZANE</a>
</nav></div></header>
'''


def pie():
    return f'''<footer><div class="wrap"><span>© {HOY.year} AURZANE NEXUS · Catálogo de universidades</span><span><a href="https://nexus.aurzane.com/">NEXUS</a><a href="{BASE}">Universidades</a><a href="{BASE}acerca/">Fuentes y método</a><a href="{BASE}anunciate/">Destaca tu universidad</a><a href="https://aurzane.com/privacidad.html">Privacidad</a></span></div></footer>
<script src="{BASE}assets/univ.js?v={V}" defer></script>
</body></html>
'''


def escribir(ruta, contenido):
    p = os.path.join(SALIDA, ruta)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(contenido)


def migas(*partes):
    out = []
    for t, h in partes:
        out.append(f'<a href="{h}">{e(t)}</a>' if h else e(t))
    return '<p class="migas">' + '<span>/</span>'.join(out) + '</p>'


URLS = []  # (url, prioridad)

# ---------------------------------------------------------------- datos JSON
def datos():
    pidx = {p: i for i, p in enumerate(ORDEN_P)}
    ind = {'p': [[PSLUG[p], PAISES[p][0], p] for p in ORDEN_P], 'u': []}
    for p in ORDEN_P:
        for u in por_pais[p]:
            ind['u'].append([u['nombre'], pidx[p], u['slug'], u['ciudad'], u['tipo'], u['tipo_ies'], u['n'], 0, u['region']])
    escribir('datos/indice.json', json.dumps(ind, ensure_ascii=False, separators=(',', ':')))
    escribir('datos/webs.json', json.dumps([[PSLUG[p] + '/' + u['slug'], u['web']] for p in ORDEN_P for u in por_pais[p] if u['web']], ensure_ascii=False, separators=(',', ':')))
    for p in ORDEN_P:
        us = por_pais[p]
        areas = sorted({c['area'] for u in us for c in u['carreras'] if c['area']})
        ai = {a: i for i, a in enumerate(areas)}
        filas, carr = [], []
        for i, u in enumerate(us):
            ua = sorted({ai[c['area']] for c in u['carreras'] if c['area']})
            filas.append([u['slug'], u['nombre'], u['ciudad'], u['region'], u['tipo'], u['tipo_ies'], u['n'], u['nivel'], ua, u['extra'].get('acronimo', ''), u['logo'], u.get('foto', ''), (rank_de(u) or [0, 0, 0, 0, 0])[:5], 1 if patro(u) else 0])
            for c in u['carreras']:
                if u['nivel'] == 'programas':
                    carr.append([i, c['n'], ai.get(c['area'], -1)] + ([c['nota']] if c.get('nota') else []))   # 4.º valor: nota de corte (España)
        escribir(f'datos/{PSLUG[p]}.json', json.dumps({'pais': p, 'areas': areas, 'u': filas}, ensure_ascii=False, separators=(',', ':')))
        if carr:
            escribir(f'datos/{PSLUG[p]}-carreras.json', json.dumps({'c': carr}, ensure_ascii=False, separators=(',', ':')))


# ---------------------------------------------------------------- tarjeta estática (SEO, antes del JS)
def hero_foto(archivo, tipo_txt):
    if not archivo: return '', ''
    estilo = f' style="--foto:url(\'{commons(archivo, 960)}\')"'
    credito = f'<a class="credito-foto" href="https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(archivo.replace(" ", "_"))}" target="_blank" rel="noopener">📷 {e(tipo_txt)}: Wikimedia Commons</a>'
    return estilo, credito


def tarjeta(u):
    p = PSLUG[u['pais']]
    url = f'{BASE}{p}/{u["slug"]}/'
    tipo = f'<span class="etq {"pub" if u["tipo"] == "Pública" else "priv"}">{e(u["tipo"])}</span>' if u['tipo'] else ''
    lugar = ', '.join(x for x in [u['ciudad'], u['region']] if x) or u['pais']
    cnt = f'<b>{fmt(u["n"])}</b> {"áreas" if u["nivel"] == "areas" else ("grados" if u["pais"] == "España" else "carreras")}' if u['n'] else 'Carreras en su web'
    foto = f'<div class="uc-foto"><img src="{e(u["foto"])}" alt="" loading="lazy" onerror="this.parentNode.classList.add(\'sin\');this.remove()"><span>{e(iniciales(u["nombre"]))}</span></div>' if u.get('foto') else f'<div class="uc-foto sin"><span>{e(iniciales(u["nombre"]))}</span></div>'
    if patro(u): tipo = '<span class="etq patro">Patrocinado</span>' + tipo
    return (f'<article class="uc{" uc-patro" if patro(u) else ""}">{foto}<div class="top"><span class="mono" aria-hidden="true">{e(iniciales(u["nombre"]))}</span><div style="min-width:0;flex:1"><h3><a href="{url}">{e(u["nombre"])}</a></h3>'
            f'<p class="lugar">📍 {e(lugar)}</p></div><button class="guardar" type="button" data-guardar data-id="{p}/{u["slug"]}" data-n="{e(u["nombre"])}" data-url="{url}" aria-pressed="false">☆</button></div>'
            f'<div class="etqs">{tipo}<span class="etq">{e(u["tipo_ies"])}</span></div><div class="pie"><span>{cnt}</span><span aria-hidden="true">→</span></div></article>')


def panel_listado(p, us, ciudad_fija='', titulo_res=''):
    pslug = PSLUG[p]
    tiene_carr = any(u['nivel'] == 'programas' for u in us)
    tiene_area = any(c['area'] for u in us for c in u['carreras'])
    regiones = len({u['region'] for u in us if u['region']}) > 1
    area_lbl = 'Rama de conocimiento' if p == 'España' else 'Área de estudio'
    ies = len({u['tipo_ies'] for u in us}) > 1
    lbl_q = 'Universidad, ciudad o carrera' if tiene_carr else 'Universidad o ciudad'
    estaticas = ''.join(tarjeta(u) for u in sorted(us, key=lambda x: (0 if patro(x) else 1, 0 if x['tipo_ies'].lower().startswith('universi') else 1, -x['n'], x['nombre']))[:36])
    return f'''<div class="wrap"><div class="app" id="listado" data-pais="{pslug}" data-ciudad="{e(ciudad_fija)}" {"data-carreras=1" if tiene_carr else ""}>
<aside class="filtros cerrado" aria-label="Filtros">
<h2>Filtrar <span><button type="button" id="limpiar">Quitar filtros</button><button type="button" id="togFiltros" aria-expanded="false" aria-controls="cuerpoF">Más filtros ▾</button></span></h2>
<div class="f"><label for="fQ">Buscar</label><input type="search" id="fQ" placeholder="{lbl_q}" autocomplete="off"></div>
<div class="cuerpo" id="cuerpoF">
{'' if not regiones or ciudad_fija else '<div class="f"><label for="fRegion">' + ('Comunidad autónoma' if p == 'España' else 'Región o provincia') + '</label><select id="fRegion"></select></div>'}
{'' if ciudad_fija else '<div class="f"><label for="fCiudad">Ciudad</label><select id="fCiudad"></select></div>'}
<div class="f"><span class="lbl">Tipo</span><div class="seg" id="fTipo" role="group" aria-label="Tipo de universidad"><button type="button" data-v="" aria-pressed="true">Todas</button><button type="button" data-v="Pública" aria-pressed="false">Pública</button><button type="button" data-v="Privada" aria-pressed="false">Privada</button></div></div>
{'<div class="f"><label for="fIes">Tipo de institución</label><select id="fIes"></select></div>' if ies else ''}
{f'<div class="f"><label for="fArea">{area_lbl}</label><select id="fArea"></select></div>' if tiene_area else ''}
{'<div class="f"><label class="chk"><input type="checkbox" id="fCon"> Solo con carreras publicadas</label></div>' if tiene_carr and any(not u["n"] for u in us) else ''}
</div>
</aside>
<div>
<div class="barra-res"><p id="nRes" aria-live="polite"><b>{fmt(len(us))}</b> instituciones</p><label><span class="vh">Ordenar</span><select id="fOrden"><option value="rel">Relevancia</option><option value="az">Nombre (A-Z)</option><option value="carr">Número de carreras</option></select></label></div>
<div class="activos" id="activos"></div>
<div class="coinc" id="coinc" hidden></div>
<div class="grid-u" id="grid">{estaticas}</div>
<div class="mas" id="mas"{" hidden" if len(us) <= 36 else ""}><button type="button" class="btn btn-osc">Ver más</button></div>
</div></div></div>'''


# ---------------------------------------------------------------- portada
def portada():
    desc = f'Buscador de universidades gratis: {fmt(TOTAL_U)} universidades e institutos de {len(ORDEN_P)} países y {fmt(TOTAL_C)} carreras. España completa con todos sus grados oficiales.'
    jl = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Universidades AURZANE NEXUS', 'url': SITIO + BASE,
          'potentialAction': {'@type': 'SearchAction', 'target': SITIO + BASE + '?q={search_term_string}', 'query-input': 'required name=search_term_string'}}
    atajos = ''.join(f'<a href="{BASE}{PSLUG[p]}/">{bandera(PAISES[p][0])}{e(p)}</a>' for p in ['España', 'Ecuador', 'México', 'Colombia', 'Argentina', 'Perú', 'Chile', 'Estados Unidos'] if p in por_pais)
    es = por_pais.get('España', [])
    es_n = sum(u['n'] for u in es)
    top_es = sorted(es, key=lambda u: -u['n'])[:6]
    cont = ''
    for cn in CONTINENTES:
        ps = [p for p in ORDEN_P if PAISES[p][1] == cn]
        if not ps: continue
        cont += f'<div class="continente"><h3>{cn}</h3><div class="paises">' + ''.join(
            f'<a class="pais" href="{BASE}{PSLUG[p]}/">{bandera(PAISES[p][0], "g")}<span><b>{e(p)}</b><small>{fmt(len(por_pais[p]))} instituciones{" · " + fmt(sum(u["n"] for u in por_pais[p])) + " carreras" if nivel_pais(p) == "programas" else ""}</small></span><i class="nivel {nivel_pais(p)}" title="{NIVEL_LBL[nivel_pais(p)]}"></i></a>'
            for p in ps) + '</div></div>'
    h = cabeza('Buscador de universidades y carreras gratis | AURZANE NEXUS', desc, SITIO + BASE, jsonld=jl) + topbar('inicio') + f'''
<main>
<section class="hero" style="padding-bottom:56px"><div class="wrap">
<p class="migas"><a href="https://nexus.aurzane.com/">NEXUS</a><span>/</span>Universidades</p>
<h1>Encuentra tu <em>universidad</em> y tu carrera</h1>
<p class="lead">{fmt(TOTAL_U)} universidades e institutos de {len(ORDEN_P)} países, con {fmt(TOTAL_C)} carreras. España completa con todos sus grados oficiales, Ecuador con todas sus carreras y las universidades principales de toda Latinoamérica.</p>
<div class="busca"><label for="qGlobal" class="vh">Buscar universidad</label><svg class="lupa" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
<input type="search" id="qGlobal" data-buscador placeholder="Busca una universidad o una ciudad: Salamanca, Cuenca, UNAM…" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="sugs" aria-autocomplete="list"><div class="sugs" id="sugs" role="listbox" hidden></div></div>
<div class="atajos">{atajos}</div>
<ul class="stats"><li><b>{fmt(TOTAL_U)}</b><span>instituciones</span></li><li><b>{fmt(TOTAL_C)}</b><span>carreras</span></li><li><b>{len(ORDEN_P)}</b><span>países</span></li><li><b>{fmt(len(es))}</b><span>universidades en España</span></li></ul>
</div></section>

<div class="wrap">
<section class="bloque"><div class="espana">
<div><span class="pre" style="color:var(--accent-text);background:var(--surface-2);border-color:var(--border)">{bandera('es')} Nuevo · España completa</span>
<h3>Todas las universidades de España y sus {fmt(es_n)} grados oficiales</h3>
<p>Datos del Registro de Universidades, Centros y Títulos (RUCT) del Ministerio. Filtra por comunidad autónoma, rama, ciudad o tipo, y calcula si te llega la nota.</p>
<a class="btn btn-osc" href="{BASE}espana/">Ver universidades de España</a> <a class="btn btn-borde" href="/calculadora-nota-pau/" style="color:var(--accent-text)">🧮 Calcular mi nota PAU</a></div>
<ul>{''.join(f'<li><a href="{BASE}espana/{u["slug"]}/">{e(u["nombre"])}<small>{e(u["ciudad"])} · {fmt(u["n"])} grados</small></a></li>' for u in top_es)}</ul>
</div></section>

<section class="bloque" id="paises"><h2 class="t">Universidades por país</h2>
<p class="sub">Elige un país para ver todas sus instituciones con filtros por ciudad, tipo y carrera.</p>
<p class="leyenda"><span><i class="nivel programas"></i>Con todas sus carreras</span><span><i class="nivel areas"></i>Con áreas y facultades</span><span><i class="nivel basico"></i>Universidades principales</span></p>
{cont}
</section>

<section class="bloque"><h2 class="t">Antes de elegir universidad</h2><p class="sub">Herramientas gratuitas de AURZANE para decidir mejor.</p>
<div class="tres">
<a class="scard" href="{BASE}notas-de-corte/" style="background:linear-gradient(135deg,#3a50c4,#0f1538)"><span class="e">📊</span><b>Notas de corte 2025-2026</b><span>La nota oficial de cada carrera en cada universidad pública, ordenada.</span></a>
<a class="scard" href="/calculadora-nota-pau/" style="background:linear-gradient(135deg,#2b3fb8,#0b1030)"><span class="e">🧮</span><b>Calculadora de nota PAU</b><span>Tu nota de acceso y de admisión sobre 14, y si te llega para tu carrera.</span></a>
<a class="scard" href="https://ovp.aurzane.com/" style="background:linear-gradient(135deg,#2b3fb8,#8b7bff)"><span class="e">🧭</span><b>Test vocacional gratis</b><span>Seis instrumentos y un informe con las carreras que encajan contigo.</span></a>
<a class="scard" href="https://mind.aurzane.com/test-de-personalidad/" style="background:linear-gradient(135deg,#ff7a45,#a35be0)"><span class="e">🧠</span><b>Test de personalidad</b><span>Descubre tu perfil entre 11 y las carreras afines a él.</span></a>
</div></section>

<section class="bloque" style="max-width:800px"><h2 class="t">Preguntas frecuentes</h2>
<details class="faq"><summary>¿De dónde salen los datos?</summary><p>España viene del Registro de Universidades, Centros y Títulos (RUCT) del Ministerio de Ciencia, Innovación y Universidades. Ecuador, del registro oficial de la SENESCYT. Estados Unidos, del College Scorecard del Departamento de Educación. Colombia, del SNIES del Ministerio de Educación Nacional. Chile, de la oferta académica del SIES (Mineduc). El resto, de las fuentes oficiales de cada país y de las webs de cada universidad. Más detalles en <a href="{BASE}acerca/">fuentes y método</a>.</p></details>
<details class="faq"><summary>¿Por qué algunas universidades no tienen carreras?</summary><p>En algunos países solo publicamos las universidades principales o sus áreas y facultades. En esos casos te enlazamos a su web oficial, donde está su oferta completa.</p></details>
<details class="faq"><summary>¿Puedo comparar universidades?</summary><p>Sí. Usa el <a href="{BASE}comparar/">comparador</a> para ver hasta tres lado a lado, con las carreras que tienen en común y su nota de corte en España. También puedes pulsar ☆ para guardarlas en <a href="{BASE}mi-lista/">Mi lista</a>.</p></details>
<details class="faq"><summary>He visto un dato que no es correcto</summary><p>Pulsa «Reportar un error» en la ficha de la universidad, o el botón ⚑ que tienes en cualquier página, y lo revisamos. Cada ficha indica su fuente.</p></details>
</section>
</div></main>
''' + pie()
    escribir('index.html', h)
    URLS.append((SITIO + BASE, '1.0'))


# ---------------------------------------------------------------- índice de países
def paises():
    filas = ''
    for cn in CONTINENTES:
        ps = [p for p in ORDEN_P if PAISES[p][1] == cn]
        if not ps: continue
        filas += f'<div class="continente"><h3>{cn}</h3><div class="paises">' + ''.join(
            f'<a class="pais" href="{BASE}{PSLUG[p]}/">{bandera(PAISES[p][0], "g")}<span><b>{e(p)}</b><small>{fmt(len(por_pais[p]))} instituciones · {NIVEL_LBL[nivel_pais(p)].lower()}</small></span><i class="nivel {nivel_pais(p)}"></i></a>' for p in ps) + '</div></div>'
    h = cabeza(f'Universidades por país: {len(ORDEN_P)} países | AURZANE NEXUS', f'Universidades de {len(ORDEN_P)} países organizadas por continente: España, Latinoamérica, Europa, Estados Unidos, Asia y más.', SITIO + BASE + 'paises/') + topbar('paises') + f'''
<main><section class="hero" style="padding-bottom:40px"><div class="wrap">{migas(("NEXUS", "https://nexus.aurzane.com/"), ("Universidades", BASE), ("Países", ""))}
<h1>Universidades por <em>país</em></h1><p class="lead">{len(ORDEN_P)} países y {fmt(TOTAL_U)} instituciones.</p></div></section>
<div class="wrap"><section class="bloque"><p class="leyenda"><span><i class="nivel programas"></i>Con todas sus carreras</span><span><i class="nivel areas"></i>Con áreas y facultades</span><span><i class="nivel basico"></i>Universidades principales</span></p>{filas}</section></div></main>''' + pie()
    escribir('paises/index.html', h)
    URLS.append((SITIO + BASE + 'paises/', '0.7'))


# ---------------------------------------------------------------- página de país
def pagina_pais(p):
    us = por_pais[p]
    iso = PAISES[p][0]
    nc = sum(u['n'] for u in us)
    npub = sum(1 for u in us if u['tipo'] == 'Pública')
    ciudades = collections.Counter(u['ciudad'] for u in us if u['ciudad'])
    nivel = nivel_pais(p)
    if p == 'España':
        tit = f'Universidades de España: las {len(us)} universidades y sus {fmt(nc)} grados | AURZANE NEXUS'
        lead = f'Las {len(us)} universidades del sistema universitario español con sus {fmt(nc)} grados oficiales vigentes, según el Registro de Universidades, Centros y Títulos (RUCT). Filtra por comunidad autónoma, rama, ciudad o tipo.'
    elif nivel == 'basico':
        nombres = [u['nombre'] for u in us[:3]]
        tit = next(t for t in (f'Universidades en {p}: ranking y cómo estudiar allí (2026)', f'Universidades en {p}: ranking y cómo estudiar allí', f'Universidades en {p}: las {len(us)} principales (2026)', f'Universidades en {p}') if len(t) <= 60 or t == f'Universidades en {p}')
        lead = f'Las {len(us)} universidades principales de {p}' + (f', como {", ".join(nombres[:-1])} y {nombres[-1]}' if len(nombres) > 1 else '') + '. Consulta su ciudad, si son públicas o privadas y su web oficial para estudiar en ' + p + '.'
    else:
        tit = next(t for t in (f'Universidades en {p}: ranking, carreras y cómo estudiar allí', f'Universidades en {p}: ranking y carreras', f'Universidades en {p}') if len(t) <= 60 or t == f'Universidades en {p}')
        lead = f'{fmt(len(us))} universidades e institutos de educación superior en {p}' + (f', con {fmt(nc)} carreras.' if nivel == 'programas' else '.') + ' Filtra por ciudad, tipo y área.'
    jl = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': f'Universidades de {p}', 'numberOfItems': len(us),
          'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{SITIO}{BASE}{PSLUG[p]}/{u["slug"]}/', 'name': u['nombre']} for i, u in enumerate(sorted(us, key=lambda x: -x['n'])[:50])]}
    top_c = [c for c, n in ciudades.most_common(12) if n >= 2]
    ciudades_html = ''
    if top_c and p not in ('Estados Unidos',):
        ciudades_html = '<section class="bloque"><h2 class="t">Universidades por ciudad</h2><div class="paises">' + ''.join(
            (lambda fc: f'<a class="pais ciudad{" con-foto" if fc else ""}" href="{BASE}{PSLUG[p]}/ciudad/{slug(c)}/"' + (f' style="--foto:url(\'{commons(fc, 500)}\')"' if fc else '') + f'><span><b>{e(c)}</b><small>{ciudades[c]} instituciones</small></span></a>')(IMG.get('c', {}).get(PAISES[p][0], {}).get(_n(c))) for c in top_c) + '</div></section>'
    todas = ''
    if len(us) <= 600:
        todas = '<details class="todas"><summary>Todas las instituciones de ' + e(p) + ' (A-Z)</summary><ul>' + ''.join(f'<li><a href="{BASE}{PSLUG[p]}/{u["slug"]}/">{e(u["nombre"])}</a></li>' for u in us) + '</ul></details>'
    pau = '<a class="btn btn-luz" href="/calculadora-nota-pau/">🧮 ¿Te llega la nota? Calcúlala</a>' if p == 'España' else ''
    h = cabeza(tit, lead, f'{SITIO}{BASE}{PSLUG[p]}/', jsonld=jl) + topbar('espana' if p == 'España' else 'paises') + f'''
<main><section class="hero" style="padding-bottom:40px"><div class="wrap">{migas(("NEXUS", "https://nexus.aurzane.com/"), ("Universidades", BASE), (p, ""))}
<h1>{bandera(iso, "g")} Universidades {"de" if p in ("España",) else "en"} <em>{e(p)}</em></h1>
<p class="lead">{e(lead)}</p>
<ul class="stats"><li><b>{fmt(len(us))}</b><span>instituciones</span></li>{f"<li><b>{fmt(nc)}</b><span>{'grados' if p == 'España' else 'carreras'}</span></li>" if nc else ""}<li><b>{fmt(npub)}</b><span>públicas</span></li><li><b>{fmt(len(us) - npub)}</b><span>privadas</span></li></ul>
{f'<div class="acc">{pau}</div>' if pau else ''}
</div></section>
{panel_listado(p, us)}
<div class="wrap">{ciudades_html}{todas}
{estudiar_en(p, us)}
<section class="card guia-auto" style="margin-top:24px"><h2>Cómo es el acceso a la universidad en {e(p)}</h2>{''.join('<p>' + e(x) + '</p>' for x in _acceso(p))}<h3>Cómo elegir universidad y carrera</h3><p>{e(_ELEGIR)}</p></section>
<p class="fuente">{fuente_pais(p)}</p></div>
</main>''' + pie()
    escribir(f'{PSLUG[p]}/index.html', h)
    URLS.append((f'{SITIO}{BASE}{PSLUG[p]}/', '0.9' if p in ('España', 'Ecuador') else '0.8'))
    if p not in ('Estados Unidos',):
        for c in [c for c, n in ciudades.items() if n >= 2]:
            pagina_ciudad(p, c, [u for u in us if u['ciudad'] == c])


def estudiar_en(p, us):
    """Estudiar en [país]: lo esencial con datos reales (auditoría final, punto 44): idiomas, moneda, capital,
    las universidades mejor situadas en el ranking mundial abierto y los siguientes pasos dentro de AURZANE."""
    iso = PAISES[p][0].lower(); pi = PINFO.get(iso) or {}
    rk = sorted(((rank_de(u), u) for u in us if rank_de(u)), key=lambda x: x[0][0])[:5]
    filas = []
    if pi.get('idiomas'): filas.append(('Idiomas oficiales', ', '.join(pi['idiomas'])))
    if pi.get('moneda'): filas.append(('Moneda', ', '.join(pi['moneda'])))
    if pi.get('capital'): filas.append(('Capital', pi['capital']))
    npub = sum(1 for u in us if u['tipo'] == 'Pública')
    filas.append(('En el catálogo', f'{fmt(len(us))} instituciones, {fmt(npub)} públicas'))
    datos_h = '<dl class="datos">' + ''.join(f'<dt>{e(a)}</dt><dd>{e(b)}</dd>' for a, b in filas) + '</dl>'
    top = ''
    if rk:
        top = ('<h3>Las mejor situadas en el ranking mundial</h3><ol class="top-rank">' + ''.join(
            f'<li><a href="{BASE}{PSLUG[p]}/{u["slug"]}/">{e(u["nombre"])}</a> <small>n.º {fmt(r[0])} del mundo</small></li>' for r, u in rk) +
            f'</ol><p class="sub">Ranking abierto por citas científicas (OpenAlex). <a href="{BASE}acerca/#ranking">Cómo se calcula</a>.</p>')
    pasos = (f'<p class="pasos"><a class="btn btn-luz" href="https://ovp.aurzane.com/">Haz el test vocacional gratis</a> '
             f'<a class="btn btn-claro" href="{BASE}comparar/">Compara universidades</a></p>')
    return f'<section class="card estudiar-en" style="margin-top:24px"><h2>Estudiar en {e(p)}: lo esencial</h2>{datos_h}{top}{pasos}</section>'


def fuente_pais(p):
    if p == 'España': return 'Fuente: Registro de Universidades, Centros y Títulos (RUCT), Ministerio de Ciencia, Innovación y Universidades. Solo grados oficiales vigentes. Actualizado: ' + HOY.strftime('%d/%m/%Y') + '.'
    if p == 'Ecuador': return 'Fuente: registro oficial de carreras vigentes de la SENESCYT. Los nombres de las carreras aparecen tal como figuran en el registro.'
    if p == 'Estados Unidos': return 'Fuente: College Scorecard, Departamento de Educación de EE. UU. Los nombres de los programas aparecen en inglés, como en la fuente oficial.'
    if p in OFICIAL: return f'Fuente: {OFICIAL[p]["fuente"]}. {OFICIAL[p].get("nota", "")} Se actualiza cada mes.'
    if nivel_pais(p) == 'basico': return 'Selección de las universidades principales del país. Consulta la web oficial de cada una para ver su oferta completa.'
    return 'Fuentes oficiales del país y webs de cada institución. En algunas universidades mostramos áreas o facultades en lugar del listado completo de carreras.'


def pagina_ciudad(p, c, us):
    iso = PAISES[p][0]
    us = sorted(us, key=lambda u: -(u['n'] or 0))
    N, nc = len(us), sum(u['n'] or 0 for u in us)
    npub = sum(1 for u in us if u['tipo'] == 'Pública'); npriv = N - npub
    corto = lambda u: u['extra'].get('acronimo') or u['nombre']
    nombres = [corto(u) for u in us[:3]]
    lista = ', '.join(nombres[:-1]) + (' y ' + nombres[-1] if len(nombres) > 1 else nombres[0]) + (' y más' if N > 3 else '')
    partes = []
    if npub: partes.append(f'{npub} pública' + ('s' if npub > 1 else ''))
    if npriv: partes.append(f'{npriv} privada' + ('s' if npriv > 1 else ''))
    reparto = ' y '.join(partes)
    palabra = 'grados' if p == 'España' else 'carreras'
    cn = f'{c}, {p}' if len(CIUDAD_PAISES.get(c, ())) > 1 else c   # ciudades con el mismo nombre en varios países (La Paz)
    tit = f'Universidades en {cn}: {N} opciones' + (f' y {fmt(nc)} {palabra}' if nc else ', públicas y privadas') + ' (2026)'
    desc = f'¿Cuántas universidades hay en {c}? Hay {N} ({reparto}): {lista}.' + (f' Compara sus {fmt(nc)} {palabra}, modalidades y web oficial.' if nc else ' Compara tipo, ubicación y web oficial.')
    lead = f'En {c} hay {N} universidades e institutos de educación superior ({reparto})' + (f', con {fmt(nc)} {palabra} en total.' if nc else '.') + ' Filtra por tipo o área y entra en cada una para ver su oferta y su web oficial.'
    respuesta = f'En {c} ({p}) hay {N} instituciones de educación superior: {reparto}. ' + ('Las que más ' + palabra + ' ofrecen son ' + ', '.join(f'{u["nombre"]} ({fmt(u["n"])})' for u in us[:3] if u['n']) + '.' if nc else 'Entre ellas están ' + ', '.join(u['nombre'] for u in us[:3]) + '.')
    canon = f'{SITIO}{BASE}{PSLUG[p]}/ciudad/{slug(c)}/'
    jsonld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': f'¿Cuántas universidades hay en {c}?', 'acceptedAnswer': {'@type': 'Answer', 'text': respuesta}}]},
        {'@type': 'ItemList', 'name': f'Universidades en {c}', 'numberOfItems': N, 'itemListElement': [
            {'@type': 'ListItem', 'position': k + 1, 'name': u['nombre'], 'url': f'{SITIO}{BASE}{PSLUG[p]}/{u["slug"]}/'} for k, u in enumerate(us[:30])]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Universidades', 'item': f'{SITIO}{BASE}'},
            {'@type': 'ListItem', 'position': 2, 'name': p, 'item': f'{SITIO}{BASE}{PSLUG[p]}/'},
            {'@type': 'ListItem', 'position': 3, 'name': c, 'item': canon}]}]}
    fc = IMG.get('c', {}).get(iso, {}).get(_n(c))
    hf, cred = hero_foto(fc, 'Foto de ' + c)
    h = cabeza(tit, desc, canon, og_img=commons(fc, 1280, local=False) if fc else None, jsonld=jsonld) + topbar('espana' if p == 'España' else 'paises') + f'''
<main><section class="hero{' con-foto' if hf else ''}" style="padding-bottom:40px"{hf}><div class="wrap">{migas(("Universidades", BASE), (p, f"{BASE}{PSLUG[p]}/"), (c, ""))}
<h1>{bandera(iso, "g")} Universidades en <em>{e(c)}</em></h1><p class="lead">{e(lead)}</p>{cred}</div></section>
{panel_listado(p, us, ciudad_fija=c)}
<div class="wrap"><section class="card" style="margin-top:28px"><h2>¿Cuántas universidades hay en {e(c)}?</h2><p>{e(respuesta)}</p></section>
<p class="fuente">{fuente_pais(p)}</p></div></main>''' + pie()
    escribir(f'{PSLUG[p]}/ciudad/{slug(c)}/index.html', h)
    URLS.append((f'{SITIO}{BASE}{PSLUG[p]}/ciudad/{slug(c)}/', '0.6'))


# ---------------------------------------------------------------- ficha de universidad
def fmt_nota(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.').replace('.', ',')


FINAS = []
def ficha(u, vecinas):
    p = u['pais']; iso = PAISES[p][0]; ps = PSLUG[p]
    url = f'{SITIO}{BASE}{ps}/{u["slug"]}/'
    lugar = ', '.join(x for x in [u['ciudad'], u['region']] if x) or p
    n = u['n']
    es_es = p == 'España'
    palabra = 'grados' if es_es else ('áreas y facultades' if u['nivel'] == 'areas' else 'carreras')
    # carreras agrupadas
    grupos = collections.OrderedDict()
    for c in sorted(u['carreras'], key=lambda c: c['n'].lower()):
        grupos.setdefault(c['grupo'] or 'Otras', []).append(c)
    orden_g = sorted(grupos, key=lambda g: (-len(grupos[g]), g))
    if all(g in ORDEN_NIVEL for g in grupos): orden_g = sorted(grupos, key=ORDEN_NIVEL.index)   # datos oficiales: de pregrado a doctorado
    chips = ''
    if len(orden_g) > 1:
        chips = '<div class="chips" role="group" aria-label="Filtrar por grupo"><button type="button" class="chip" aria-pressed="true" data-area="">Todas</button>' + ''.join(
            f'<button type="button" class="chip" aria-pressed="false" data-area="{e(g)}">{e(g)} ({len(grupos[g])})</button>' for g in orden_g) + '</div>'
    lis = ''
    for g in orden_g:
        items = ''
        for c in grupos[g]:
            det = []
            if c.get('campo'): det.append(c['campo'])
            elif c.get('area') and c['area'] != g: det.append(c['area'])
            if c.get('titulo'): det.append('Título: ' + c['titulo'])
            der = []
            if c.get('cred'): der.append(f'{c["cred"]} ECTS' if es_es else c['cred'])
            if c.get('mod'): der.append(' · '.join(c['mod']))
            if c.get('sedes') and (len(c['sedes']) > 1 or (c['sedes'][0] != u['ciudad'])): der.append(', '.join(c['sedes'][:4]) + ('…' if len(c['sedes']) > 4 else ''))
            prof = f'<em class="prof">Habilita para: {e(c["prof"])}</em>' if c.get('prof') else ''
            if c.get('nota'): der.insert(0, f'Nota de corte {fmt_nota(c["nota"])}')
            items += f'<li><span>{e(c["n"])}{prof}{"<small>" + e(" · ".join(det)) + "</small>" if det else ""}</span>{"<small>" + e(" · ".join(der)) + "</small>" if der else ""}</li>'
        lis += f'<div class="grupo" data-area="{e(g)}"><h3><span>{e(g)}</span><span>{len(grupos[g])}</span></h3><ul class="carreras">{items}</ul></div>'
    if n:
        bloque_c = f'''<section class="card" id="carreras"><div class="carr-cab"><h2>{fmt(n)} {palabra}</h2>{"<input type=search class=carr-busca placeholder='Buscar en sus " + palabra + "' aria-label='Buscar carrera'>" if n > 8 else ""}</div>
{chips}{lis}<p id="carrVacio" class="sub" hidden>No hay {palabra} con esa búsqueda.</p>
{"<p class='aviso'>Esta universidad publica sus áreas y facultades. Consulta su oferta completa de carreras en su web oficial.</p>" if u["nivel"] == "areas" else ""}</section>'''
    else:
        bloque_c = f'<section class="card" id="carreras"><h2>Carreras</h2><p class="aviso">Todavía no tenemos el listado de carreras de esta institución. Puedes consultar su oferta completa en su {"<a href=" + e(u["web"]) + " target=_blank rel=noopener>web oficial</a>" if u["web"] else "web oficial"}.</p></section>'
    if u['extra'].get('fuente_url') and n:   # datos abiertos oficiales: se cita la fuente y la fecha de la descarga
        _ff = u['extra'].get('fuente_fecha', '')
        _ff = f'{int(_ff[8:10])}/{int(_ff[5:7])}/{_ff[:4]}' if re.match(r'^\d{4}-\d\d-\d\d$', _ff) else ''
        bloque_c = bloque_c.replace('</section>', f'<p class="sub fuente-of">Fuente: <a href="{e(u["extra"]["fuente_url"])}" target="_blank" rel="noopener">{e(u["fuente"])}</a>'
                                    f'{", consultada el " + _ff if _ff else ""}. {e(u["extra"].get("fuente_nota", ""))}</p></section>', 1)
    dato = [('País', f'{bandera(iso)} {e(p)}'), ('Ciudad', e(u['ciudad'] or '-'))]
    if u['region']: dato.append(('Comunidad autónoma' if es_es else 'Región', e(u['region'])))
    dato.append(('Tipo', e(u['tipo_txt'] or '-')))
    dato.append(('Institución', e(u['tipo_ies'])))
    if u['extra'].get('acronimo'): dato.append(('Siglas', e(u['extra']['acronimo'])))
    if u['extra'].get('anio'): dato.append(('Creada en', e(u['extra']['anio'])))
    if u['extra'].get('en_linea'): dato.append(('Modalidad', 'En línea'))
    if u['extra'].get('acreditacion'): dato.append(('Acreditación', e(u['extra']['acreditacion'])))
    rk = rank_de(u)
    if rk: dato.append(('Ranking mundial', f'<a href="{BASE}acerca/#ranking" title="Posición por citas científicas en OpenAlex">n.º {fmt(rk[0])} del mundo · n.º {fmt(rk[1])} en {e(p)}</a>'))
    if u['web']:
        dom = re.sub(r'^https?://(www\.)?', '', u['web']).rstrip('/')
        dato.append(('Web', f'<a href="{e(u["web"])}" target="_blank" rel="noopener nofollow">{e(dom)}</a>'))
    datos_html = '<dl class="datos">' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in dato) + '</dl>'
    cerca = ''
    if vecinas:
        cerca = f'<section class="card"><h2>Otras en {e(u["ciudad"] or p)}</h2><ul class="cercanas">' + ''.join(
            f'<li><a href="{BASE}{ps}/{v["slug"]}/">{e(v["nombre"])}</a><small>{e(v["tipo"])}{" · " + fmt(v["n"]) + (" grados" if es_es else " carreras") if v["n"] else ""}</small></li>' for v in vecinas[:6]) + '</ul>' + (
            f'<p style="margin:10px 0 0"><a href="{BASE}{ps}/ciudad/{slug(u["ciudad"])}/">Ver todas en {e(u["ciudad"])} →</a></p>' if u['ciudad'] and len(vecinas) >= 1 and p != 'Estados Unidos' else '') + '</section>'
    cta = ('<section class="cta"><b>¿Te llega la nota?</b><p>Calcula tu nota de admisión de la PAU sobre 14 y compárala con la nota de corte.</p><a class="btn btn-luz" href="/calculadora-nota-pau/">Calcular mi nota</a></section>' if es_es else
           '<section class="cta"><b>¿No sabes qué estudiar?</b><p>Haz el test vocacional gratis y descubre las carreras que encajan contigo.</p><a class="btn btn-luz" href="https://ovp.aurzane.com/">Hacer el test vocacional</a></section>')
    pt = patro(u)
    if pt:
        cta = (f'<section class="cta cta-patro"><span class="etq patro">Patrocinado</span><b>{e(pt.get("texto") or "Admisiones abiertas")}</b>'
               f'<p>Información oficial de admisión de {e(u["nombre"])}.</p><a class="btn btn-luz" href="{e(utm(pt["url"], "ficha"))}" target="_blank" rel="sponsored noopener">Ver admisión ↗</a></section>') + cta
    destaca = '' if pt else f'<p class="destaca"><a href="{BASE}anunciate/?u={ps}/{u["slug"]}">¿Trabajas en {e(u["nombre"])}? Destácala ante estudiantes que buscan carrera</a></p>'
    desc_meta = f'{u["nombre"]} ({lugar}, {p}): ' + (f'sus {fmt(n)} {palabra}, ' if n else '') + f'tipo {u["tipo_txt"].lower() or "-"}, ciudad y web oficial.'
    jl = {'@context': 'https://schema.org', '@type': 'CollegeOrUniversity', 'name': u['nombre'], 'url': u['web'] or url,
          'address': {'@type': 'PostalAddress', 'addressLocality': u['ciudad'] or None, 'addressRegion': u['region'] or None, 'addressCountry': iso.upper()},
          'sameAs': [u['web']] if u['web'] else None}
    if n and u['nivel'] == 'programas':
        jl['hasOfferCatalog'] = {'@type': 'OfferCatalog', 'name': 'Carreras', 'itemListElement': [{'@type': 'Offer', 'itemOffered': {'@type': 'EducationalOccupationalProgram', 'name': c['n']}} for c in u['carreras'][:60]]}
    jl = {k: v for k, v in jl.items() if v}
    jl['address'] = {k: v for k, v in jl['address'].items() if v}
    meta = [f'<li>📍 {e(lugar)}</li>', f'<li>{"🏛️" if u["tipo"] == "Pública" else "🏢"} {e(u["tipo_txt"] or "-")}</li>', f'<li>🎓 {e(u["tipo_ies"])}</li>']
    if u['extra'].get('anio'): meta.append(f'<li>📜 Creada en {e(u["extra"]["anio"])}</li>')
    if n: meta.append(f'<li>📚 {fmt(n)} {palabra}</li>')
    tit = f'{u["nombre"]}: ' + (f'{fmt(n)} {palabra}' if n else 'carreras, ciudad y web') + f' | Universidades de {p}'
    rk_u = rank_de(u)
    if rk_u and not es_es:   # lo que diferencia la ficha de la web oficial: su puesto en el ranking mundial (auditoría final, punto 45)
        tit = next((t for t in (f'{u["nombre"]}: n.º {fmt(rk_u[0])} del mundo y {fmt(n)} {palabra}' if n else '', f'{u["nombre"]}: n.º {fmt(rk_u[0])} del mundo, ranking y carreras',
                                 f'{u["nombre"]}: n.º {fmt(rk_u[0])} del mundo') if t and len(t) <= 65), tit)
    _sc = SC.get(u['id']) if p == 'Estados Unidos' else None
    if _sc:   # 19/11/2026: título y descripción con lo que busca un estudiante (admisión y coste reales)
        _neto = _sc.get('precio_neto_pub') if _sc.get('control') == 1 else _sc.get('precio_neto_priv')
        _ad = f'admisión {round(_sc["admision"] * 100)} %' if _sc.get('admision') is not None else ''
        tit = next((t for t in (f'{u["nombre"]}: {_ad}, costes y becas' if _ad else '', f'{u["nombre"]}: admisión, costes y becas', f'{u["nombre"]}: costes y becas') if t and len(t) <= 65), tit)
        desc_meta = f'{u["nombre"]} ({lugar}): ' + ', '.join(x for x in (f'tasa de admisión del {round(_sc["admision"] * 100)} %' if _sc.get('admision') is not None else '', f'precio neto medio de {_USD(_neto)} al año' if _neto else '', f'{fmt(n)} {palabra}' if n else '') if x) + '. Datos oficiales y cómo estudiar allí siendo de fuera.'
    hf, cred = hero_foto(u.get('foto_archivo') or u.get('foto_ciudad'), 'Foto' if u.get('foto_tipo') == 'u' else 'Foto de ' + (u['ciudad'] or p))
    # ficha casi vacía (sin carreras, descripción ni foto): visible para quien llega, pero fuera de Google y del sitemap
    # hasta que tenga contenido propio (auditoría 16/11/2026: 2.395 páginas «descubiertas, sin indexar» por contenido escaso)
    bloque_sc = bloque_scorecard(u) if p == 'Estados Unidos' else ''
    fina = not n and not u.get('descripcion') and not (u.get('foto_archivo') or u.get('foto_ciudad')) and not bloque_sc
    if fina: FINAS.append(url)
    h = cabeza(tit, desc_meta, url, og_img=commons(u.get('foto_archivo') or u.get('foto_ciudad'), 1280, local=False) if (u.get('foto_archivo') or u.get('foto_ciudad')) else None, jsonld=jl, robots='noindex,follow' if fina else None, precarga=commons(u.get('foto_archivo') or u.get('foto_ciudad'), 960) or None) + topbar('espana' if es_es else 'paises') + f'''
<main><section class="hero ficha-h{' con-foto' if hf else ''}"{hf}><div class="wrap">{migas(("Universidades", BASE), (p, f"{BASE}{ps}/"), *([(u["ciudad"], f"{BASE}{ps}/ciudad/{slug(u['ciudad'])}/")] if u["ciudad"] and vecinas and p != "Estados Unidos" else []), (u["nombre"], ""))}
<div class="fila" style="margin-top:16px"><span class="mono" aria-hidden="true">{e(u["extra"].get("acronimo") or iniciales(u["nombre"]))[:5]}</span><div><h1 style="margin:0">{e(u["nombre"])}</h1></div></div>
<ul class="meta">{''.join(meta)}</ul>{f'<p class="lead" style="margin-top:14px">{e(u["descripcion"])}</p>' if u["descripcion"] else ''}
<div class="acc">{f'<a class="btn btn-luz" href="{e(u["web"])}" target="_blank" rel="noopener nofollow">Web oficial ↗</a>' if u["web"] else ''}<button type="button" class="btn btn-claro" data-guardar data-id="{ps}/{u["slug"]}" data-n="{e(u["nombre"])}" data-url="{BASE}{ps}/{u["slug"]}/" aria-pressed="false">☆ Guardar</button>{'<a class="btn btn-claro" href="#carreras">Ver ' + palabra + '</a>' if n else ''}<a class="btn btn-claro" href="{BASE}comparar/?u={ps}/{u["slug"]}">Comparar con otra</a>{f'<a class="btn btn-claro" href="/en/universities/{u["slug"]}/" hreflang="en" lang="en">English</a>' if es_es and u["slug"] in ES_CON_EN else ''}</div>
{cred}</div></section>
<div class="wrap"><div class="ficha"><div>{bloque_sc}{bloque_c}{bloque_ia(url) or bloque_auto(u, orden_g, grupos)}</div>
<aside><section class="card"><h2>Datos</h2>{datos_html}</section>{cta}{cerca}</aside></div>
<p class="fuente">{fuente_pais(p)} </p>
<div class="reportar"><span>¿Algún dato no es correcto o un enlace no funciona?</span><button type="button" class="btn btn-borde" data-reportar data-tipo="dato" data-ref="{e(u["nombre"] + " (" + p + ")")}">⚑ Reportar un error</button></div>{destaca}</div>
</main>''' + pie()
    escribir(f'{ps}/{u["slug"]}/index.html', h)
    if not fina: URLS.append((url, '0.7' if n else '0.5'))


def limpiar_titulo(t):
    t = re.sub(r'\s+', ' ', t or '').strip()
    t = re.sub(r'^(Doble )?Grado (Universitario )?(en|de) ', '', t, flags=re.I)
    t = re.sub(r'\s*/\s*(Bachelor|Degree|Double).*$', '', t, flags=re.I)
    t = re.sub(r'\s*\((Bachelor|Degree)[^)]*\)', '', t, flags=re.I)
    t = re.sub(r'\s+(por|de) la Universidad.*$', '', t, flags=re.I)
    return t[:1].upper() + t[1:]


def notas_de_corte():
    filas = [f for f in NC['filas'] if f.get('nota')]
    if not filas: return
    u_cod = {u['extra'].get('cod'): u for u in por_pais.get('España', []) if u['extra'].get('cod')}
    grupos = collections.defaultdict(list)
    for f in filas:
        nombre = limpiar_titulo(f['titulo'])
        if f.get('nivel') == 'GRADOD' or ' y ' in nombre and f['titulo'].lower().startswith('doble'):
            nombre = 'Doble grado: ' + nombre
        grupos[slug(nombre)].append((nombre, f))
    idx = []
    for k, lst in grupos.items():
        if len(lst) < 2: continue
        nombre = collections.Counter(n for n, _ in lst).most_common(1)[0][0]
        lst = sorted((f for _, f in lst), key=lambda f: -f['nota'])
        notas = [f['nota'] for f in lst]
        idx.append((nombre, k, len(lst), max(notas), min(notas)))
        filas_html = ''
        for i, f in enumerate(lst):
            u = u_cod.get(f.get('cod_univ'))
            uni = f'<a href="{BASE}espana/{u["slug"]}/">{e(f["universidad"])}</a>' if u else e(f['universidad'])
            filas_html += f'<tr><td class="num">{i + 1}</td><td><b>{uni}</b><small>{e(f["centro"] or "")}{" · centro adscrito" if f.get("tipo_centro") == "Adscrito" else ""}</small></td><td>{e(f["provincia"] or "")}<small>{e(f["ccaa"] or "")}</small></td><td class="nota">{fmt_nota(f["nota"])}</td></tr>'
        mx, mn = lst[0], lst[-1]
        tit = f'Nota de corte de {nombre} {NC_CURSO}: {len(lst)} universidades'
        desc = f'Notas de corte de {nombre} en {len(lst)} universidades públicas de España (curso {NC_CURSO}): la más alta es {fmt_nota(mx["nota"])} en la {mx["universidad"]} y la más baja {fmt_nota(mn["nota"])}. Datos oficiales del Ministerio.'
        resp = f'En el curso {NC_CURSO}, la nota de corte de {nombre} va de {fmt_nota(mn["nota"])} ({mn["universidad"]}) a {fmt_nota(mx["nota"])} ({mx["universidad"]}), sobre 14, en la convocatoria ordinaria y por el cupo general.'
        canon = f'{SITIO}{BASE}notas-de-corte/{k}/'
        jl = {'@context': 'https://schema.org', '@graph': [{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': f'¿Cuál es la nota de corte de {nombre}?', 'acceptedAnswer': {'@type': 'Answer', 'text': resp}}]},
              {'@type': 'Dataset', 'name': tit, 'description': desc, 'url': canon, 'creator': {'@type': 'Organization', 'name': 'Ministerio de Ciencia, Innovación y Universidades'}, 'temporalCoverage': NC_CURSO, 'isAccessibleForFree': True,
               # datos públicos de la Administración General del Estado: reutilización con atribución (CC BY 4.0, licencia por defecto de datos.gob.es)
               'license': 'https://creativecommons.org/licenses/by/4.0/', 'creditText': 'QEDU, Ministerio de Ciencia, Innovación y Universidades'}]}
        h = cabeza(tit, desc, canon, jsonld=jl) + topbar('espana') + f"""
<main><section class="hero" style="padding-bottom:40px"><div class="wrap">{migas(("Universidades", BASE), ("España", BASE + "espana/"), ("Notas de corte", BASE + "notas-de-corte/"), (nombre, ""))}
<h1>Nota de corte de <em>{e(nombre)}</em></h1><p class="lead">{e(resp)}</p>
<div class="acc"><a class="btn btn-luz" href="/calculadora-nota-pau/">🧮 Calcula tu nota sobre 14</a><a class="btn btn-claro" href="{BASE}notas-de-corte/">Todas las notas de corte</a></div></div></section>
<div class="wrap"><section class="card" style="margin-top:24px"><h2>{len(lst)} universidades ordenadas por nota</h2>
<div class="scroll"><table class="tnc"><thead><tr><th>#</th><th>Universidad y centro</th><th>Provincia</th><th>Nota</th></tr></thead><tbody>{filas_html}</tbody></table></div>
<p class="aviso" style="margin-top:14px">Nota de corte final del curso {NC_CURSO} en la convocatoria ordinaria y el cupo general: la nota de admisión del último estudiante que entró. Cambia cada año según plazas y solicitudes. Las universidades privadas no publican nota de corte.</p></section>
<p class="fuente">Fuente: QEDU, Ministerio de Ciencia, Innovación y Universidades. Se actualiza automáticamente cada semana.</p></div></main>""" + pie()
        escribir(f'notas-de-corte/{k}/index.html', h)
        URLS.append((canon, '0.8'))
    idx.sort(key=lambda x: (-x[2], x[0]))
    top = ''.join(f'<li data-n="{e(slug(n))}"><a href="{BASE}notas-de-corte/{k}/">{e(n)}</a><small>{c} universidades · de {fmt_nota(mn)} a {fmt_nota(mx)}</small></li>' for n, k, c, mx, mn in idx)
    tit = f'Notas de corte {NC_CURSO} de todas las carreras en España'
    desc = f'Consulta las notas de corte oficiales del curso {NC_CURSO} de {len(idx)} grados en las universidades públicas de España: Medicina, Psicología, Enfermería, Derecho y más. Busca tu carrera y compara.'
    h = cabeza(tit, desc, f'{SITIO}{BASE}notas-de-corte/') + topbar('espana') + f"""
<main><section class="hero" style="padding-bottom:40px"><div class="wrap">{migas(("Universidades", BASE), ("España", BASE + "espana/"), ("Notas de corte", ""))}
<h1>Notas de corte <em>{NC_CURSO}</em></h1><p class="lead">{e(desc)}</p>
<div class="busca" style="max-width:560px"><input type="search" id="ncBusca" placeholder="Busca una carrera: psicología, medicina, enfermería…" aria-label="Buscar carrera"></div>
<div class="acc" style="margin-top:14px"><a class="btn btn-luz" href="{BASE}que-puedo-estudiar/">🎯 ¿Qué puedo estudiar con mi nota?</a><a class="btn btn-claro" href="/calculadora-nota-pau/">🧮 Calcula tu nota sobre 14</a></div></div></section>
<div class="wrap"><section class="card" style="margin-top:24px"><ul class="nc-lista" id="ncLista">{top}</ul></section>
<p class="fuente">Fuente: QEDU, Ministerio de Ciencia, Innovación y Universidades. Actualización automática semanal.</p></div></main>
<script>(function(){{var i=document.getElementById('ncBusca'),l=document.querySelectorAll('#ncLista li');var n=function(t){{return t.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-');}};i.addEventListener('input',function(){{var q=n(i.value);l.forEach(function(x){{x.hidden=q&&x.getAttribute('data-n').indexOf(q)<0;}});}});}})();</script>""" + pie()
    escribir('notas-de-corte/index.html', h)
    URLS.append((f'{SITIO}{BASE}notas-de-corte/', '0.9'))
    print('Notas de corte:', len(idx), 'páginas de carrera')


def que_puedo_estudiar():
    """Buscador inverso: con tu nota de admisión, qué grados y universidades públicas te habrían admitido el último curso."""
    filas = [f for f in NC['filas'] if f.get('nota')]
    if not filas: return
    tit_l, uni_l, cc_l, ix = [], [], [], {}
    def idx(lista, v, k):
        if (k, v) not in ix: ix[(k, v)] = len(lista); lista.append(v)
        return ix[(k, v)]
    datos = []
    for f in filas:
        nombre = limpiar_titulo(f['titulo'])
        if f.get('nivel') == 'GRADOD': nombre = 'Doble grado: ' + nombre
        datos.append([idx(tit_l, nombre, 't'), idx(uni_l, f['universidad'], 'u'), idx(cc_l, f.get('ccaa') or '', 'c'), round(f['nota'], 3)])
    datos.sort(key=lambda x: -x[3])
    js_datos = json.dumps({'t': tit_l, 'u': uni_l, 'c': cc_l, 'd': datos}, ensure_ascii=False, separators=(',', ':'))
    opc = ''.join(f'<option>{e(c)}</option>' for c in sorted(c for c in cc_l if c))
    tit = f'¿Qué carrera puedo estudiar con mi nota? Buscador {NC_CURSO}'
    desc = f'Pon tu nota de admisión sobre 14 y descubre en qué grados y universidades públicas de España habrías entrado con las notas de corte oficiales del curso {NC_CURSO}. Filtra por comunidad autónoma y carrera.'
    canon = f'{SITIO}{BASE}que-puedo-estudiar/'
    jl = {'@context': 'https://schema.org', '@graph': [{'@type': 'WebApplication', 'name': '¿Qué puedo estudiar con mi nota?', 'url': canon, 'applicationCategory': 'EducationalApplication', 'operatingSystem': 'Web', 'inLanguage': 'es', 'isAccessibleForFree': True},
          {'@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': '¿Qué carreras puedo estudiar con un 8?', 'acceptedAnswer': {'@type': 'Answer', 'text': 'Con una nota de admisión de 8 sobre 14 se entra en muchos grados de ciencias sociales, humanidades, ingenierías y educación en universidades públicas. Pon tu nota en el buscador para ver la lista exacta según las notas de corte del último curso.'}},
              {'@type': 'Question', 'name': '¿Qué nota se pone, la de acceso o la de admisión?', 'acceptedAnswer': {'@type': 'Answer', 'text': 'La nota de admisión, sobre 14: la de acceso (60% Bachillerato y 40% fase general) más las ponderaciones de la fase específica para cada grado. Si no la sabes, calcúlala con la calculadora de nota de la PAU.'}}]}]}
    h = cabeza(tit + ' | AURZANE NEXUS', desc, canon, jsonld=jl) + topbar('espana') + f"""
<main><section class="hero" style="padding-bottom:40px"><div class="wrap">{migas(("Universidades", BASE), ("España", BASE + "espana/"), ("Notas de corte", BASE + "notas-de-corte/"), ("¿Qué puedo estudiar?", ""))}
<h1>¿Qué puedo estudiar <em>con mi nota</em>?</h1><p class="lead">{e(desc)}</p>
<div class="qpe-form">
<label>Tu nota de admisión<span><input type="number" id="qNota" min="5" max="14" step="0.001" value="9" inputmode="decimal"><b>/ 14</b></span></label>
<label>Comunidad<span><select id="qCc"><option value="">Toda España</option>{opc}</select></span></label>
<label>Carrera (opcional)<span><input type="search" id="qTxt" placeholder="psicología, enfermería, ingeniería…"></span></label>
</div>
<div class="acc" style="margin-top:14px"><a class="btn btn-claro" href="/calculadora-nota-pau/">🧮 No sé mi nota: calcúlala</a></div></div></section>
<div class="wrap"><section class="card" style="margin-top:24px">
<div class="qpe-res" id="qRes" aria-live="polite"></div>
<div class="seg qpe-tabs" id="qTab"><button type="button" data-v="si" aria-pressed="true">Te llega la nota</button><button type="button" data-v="casi" aria-pressed="false">Te falta poco (menos de 0,5)</button></div>
<div class="scroll"><table class="tnc"><thead><tr><th>Grado</th><th>Universidad</th><th>Nota de corte</th></tr></thead><tbody id="qTabla"></tbody></table></div>
<button class="btn" id="qMas" type="button" hidden style="margin-top:14px;border:1px solid var(--border);color:var(--text)">Ver más</button>
<p class="aviso" style="margin-top:14px">Notas de corte finales del curso {NC_CURSO}, convocatoria ordinaria y cupo general, en universidades públicas. Cada año cambian según plazas y solicitudes, así que tómalo como orientación. Las privadas no publican nota de corte.</p></section>
<p class="fuente">Fuente: QEDU, Ministerio de Ciencia, Innovación y Universidades. Actualización automática semanal.</p></div></main>
<style>.qpe-form{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:22px;max-width:900px}}
.qpe-form label{{display:block;font-size:.85rem;font-weight:600;opacity:.9}}.qpe-form span{{display:flex;align-items:center;gap:8px;margin-top:6px;background:#fff;border-radius:14px;padding:4px 12px;box-shadow:0 14px 30px -14px rgba(0,0,0,.45)}}
.qpe-form input,.qpe-form select{{flex:1;width:100%;border:0;background:transparent;font:600 1.05rem var(--sans);color:#1d1915;padding:10px 0;min-width:0}}.qpe-form b{{color:#655b50}}
#qNota{{font:700 1.5rem var(--serif,Georgia,serif)}}
.qpe-res{{font-size:1.05rem;margin-bottom:14px}}.qpe-res b{{font:700 1.6rem var(--serif,Georgia,serif);color:var(--accent-text)}}
.qpe-tabs{{display:inline-flex;gap:6px;margin-bottom:12px}}.qpe-tabs button{{border:1px solid var(--border);background:transparent;border-radius:99px;padding:8px 14px;font:600 .9rem var(--sans);color:var(--text-dim);cursor:pointer}}
.qpe-tabs button[aria-pressed="true"]{{background:var(--accent-text);color:#fff;border-color:transparent}}
@media (max-width:760px){{.qpe-form{{grid-template-columns:1fr}}}}</style>
<script>(function(){{var D={js_datos};
var $=function(i){{return document.getElementById(i);}},tab='si',lim=150,n=function(t){{return t.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();}};
var nt=D.t.map(n),f=function(x){{return x.toLocaleString('es-ES',{{maximumFractionDigits:3}});}};
function pintar(){{var nota=parseFloat(String($('qNota').value).replace(',','.'))||0,cc=$('qCc').value,q=n($('qTxt').value.trim());
var si=[],casi=[],grados={{}};D.d.forEach(function(r){{if(cc&&D.c[r[2]]!==cc)return;if(q&&nt[r[0]].indexOf(q)<0)return;if(r[3]<=nota){{si.push(r);grados[r[0]]=1;}}else if(r[3]-nota<=0.5)casi.push(r);}});
$('qRes').innerHTML='Con un <b>'+f(nota)+'</b> habrías entrado en <b>'+si.length.toLocaleString('es-ES')+'</b> '+(si.length===1?'opción':'opciones')+' ('+Object.keys(grados).length.toLocaleString('es-ES')+(Object.keys(grados).length===1?' grado':' grados distintos')+')'+(cc?' en '+cc:'')+'. Te faltó poco en '+casi.length.toLocaleString('es-ES')+'.';
var l=(tab==='si'?si:casi.slice().reverse()),h='';l.slice(0,lim).forEach(function(r){{h+='<tr><td><b>'+D.t[r[0]]+'</b></td><td>'+D.u[r[1]]+'<small>'+D.c[r[2]]+'</small></td><td class="nota">'+f(r[3])+'</td></tr>';}});
$('qTabla').innerHTML=h||'<tr><td colspan="3">No hay resultados con estos filtros.</td></tr>';$('qMas').hidden=l.length<=lim;}}
['qNota','qCc','qTxt'].forEach(function(i){{$(i).addEventListener('input',function(){{lim=150;pintar();}});}});
$('qTab').addEventListener('click',function(e){{var b=e.target.closest('button');if(!b)return;tab=b.getAttribute('data-v');lim=150;$('qTab').querySelectorAll('button').forEach(function(x){{x.setAttribute('aria-pressed',x===b);}});pintar();}});
$('qMas').addEventListener('click',function(){{lim+=150;pintar();}});
var u=new URLSearchParams(location.search);if(u.get('nota'))$('qNota').value=u.get('nota');if(u.get('carrera')||u.get('q'))$('qTxt').value=u.get('carrera')||u.get('q');if(u.get('cc'))$('qCc').value=u.get('cc');pintar();}})();</script>""" + pie()
    escribir('que-puedo-estudiar/index.html', h)
    URLS.append((canon, '0.9'))
    print('Qué puedo estudiar:', len(datos), 'filas')


def mi_lista():
    h = cabeza('Mi lista de universidades | AURZANE NEXUS', 'Tus universidades guardadas, comparadas lado a lado.', SITIO + BASE + 'mi-lista/', robots='noindex,follow') + topbar('lista') + f'''
<main><section class="hero" style="padding-bottom:36px"><div class="wrap">{migas(("Universidades", BASE), ("Mi lista", ""))}<h1>Mi <em>lista</em></h1><p class="lead">Las universidades que guardas, comparadas lado a lado. Se guardan en este dispositivo. Para ver también las carreras que tienen en común, usa el <a href="{BASE}comparar/">comparador</a>.</p></div></section>
<div class="wrap" style="margin-top:26px"><div id="miLista"><p class="sub">Cargando…</p></div></div></main>''' + pie()
    escribir('mi-lista/index.html', h)


def comparar():
    """Comparador de universidades (17/11/2026, etapa 3 de la auditoría, tarea 40): hasta 3 universidades de
    cualquier país lado a lado, con las carreras que tienen en común y, en España, su nota de corte. Enlace
    compartible (?u=pais/slug,pais/slug). Todo sale de los mismos datos oficiales del catálogo."""
    desc = 'Compara gratis hasta 3 universidades de cualquier país: ranking mundial, número de carreras, carreras en común y nota de corte en España.'
    h = cabeza('Comparador de universidades del mundo: ranking y carreras | AURZANE NEXUS', desc, SITIO + BASE + 'comparar/') + topbar('comparar') + f'''
<main><section class="hero" style="padding-bottom:36px"><div class="wrap">{migas(("Universidades", BASE), ("Comparar", ""))}<h1>Compara <em>universidades</em></h1><p class="lead">Elige hasta tres universidades de cualquier país y míralas lado a lado: ranking mundial, cuántas carreras ofrecen y qué carreras tienen en común.</p></div></section>
<div class="wrap" style="margin-top:26px">
<div class="card" id="cmpElegir"><h2 style="margin-top:0">Elige las universidades</h2>
<div class="cmp-campos">{''.join(f'<div class="cmp-campo"><label for="cmpQ{i}">Universidad {i + 1}</label><input id="cmpQ{i}" type="search" autocomplete="off" placeholder="Escribe el nombre o la ciudad" data-i="{i}"><ul class="cmp-sug" id="cmpS{i}" role="listbox" hidden></ul></div>' for i in range(3))}</div>
<p class="sub" style="margin:12px 0 0">Los datos salen de los registros oficiales de cada país. <a href="{BASE}acerca/">Fuentes y método</a>.</p></div>
<div id="comparador" style="margin-top:22px"></div>
</div></main>''' + pie()
    escribir('comparar/index.html', h)
    URLS.append((SITIO + BASE + 'comparar/', '0.8'))


def anunciate():
    """Destaca tu universidad (17/11/2026, etapa 4, tarea 46): página para universidades que quieran aparecer
    destacadas. Cifras reales del catálogo, calculadas en cada publicación. Las solicitudes llegan por el
    formulario de contacto de aurzane.com (mismo buzón y mismo registro privado); no hay pagos en la web."""
    n_pais = len(ORDEN_P); n_rank = sum(1 for u in UNIS if rank_de(u))
    activas = len(PATRO)
    desc = f'Destaca tu universidad en AURZANE NEXUS ante estudiantes que comparan {fmt(TOTAL_U)} universidades de {n_pais} países: etiqueta Patrocinado, primeras posiciones y enlace a admisión.'
    cifras = [(fmt(TOTAL_U), 'universidades e institutos con ficha propia'), (fmt(TOTAL_C), 'carreras y grados en el catálogo'), (str(n_pais), 'países'), (fmt(n_rank), 'fichas con ranking mundial')]
    precio_html = ''
    if PRECIO.get('mes'):
        precio_html = (f'<section class="card" id="precio"><h2>Precio</h2><div class="precios"><div class="precio"><b>{PRECIO["mes"]} €</b><span>al mes por universidad</span></div>'
                       + (f'<div class="precio"><b>{PRECIO["anio"]} €</b><span>al año: {12 * PRECIO["mes"] - PRECIO["anio"]} € menos que pagando mes a mes</span></div>' if PRECIO.get('anio') else '') + '</div>'
                       + (f'<p><b>Los primeros {PRECIO["prueba_dias"]} días son gratis</b> y sin compromiso: si no te convence, no pagas nada y tu ficha vuelve a ser normal sola.</p>' if PRECIO.get('prueba_dias') else '')
                       + '<p class="sub" style="margin:8px 0 0">IVA no incluido. Pagas en línea con tarjeta, Google Pay, Apple Pay, Link, Revolut Pay, adeudo SEPA o transferencia, y recibes la factura al momento. Sin permanencia: la cancelas cuando quieras. Otros portales de estudios cobran entre 100 y 130 € al mes por un solo programa destacado.</p></section>')
    h = cabeza(f'Destaca tu universidad entre {fmt(TOTAL_U)} de {n_pais} países | AURZANE NEXUS', desc, SITIO + BASE + 'anunciate/') + topbar() + f'''
<main><section class="hero" style="padding-bottom:36px"><div class="wrap">{migas(("Universidades", BASE), ("Destaca tu universidad", ""))}<h1>Destaca tu <em>universidad</em></h1><p class="lead">Llega a quien está eligiendo carrera justo cuando compara universidades. Tu ficha sale primero en su país y su ciudad, con la etiqueta «Patrocinado» y un botón directo a tu página de admisión.</p></div></section>
<div class="wrap" style="max-width:900px;margin-top:30px">
<section class="card"><h2>El catálogo hoy</h2><dl class="datos cifras-anun">{''.join(f'<div><dt>{t}</dt><dd><b>{n}</b></dd></div>' for n, t in cifras)}</dl><p class="sub" style="margin:10px 0 0">Datos de hoy, {HOY.strftime('%d/%m/%Y')}: se recalculan solos en cada publicación.</p></section>
<section class="card"><h2>Qué incluye</h2><ul class="lista-anun">
<li><b>Primeras posiciones</b> en el listado de tu país y de tu ciudad.</li>
<li><b>Etiqueta «Patrocinado»</b> visible en la tarjeta y en la ficha. Siempre se indica que es publicidad.</li>
<li><b>Botón a tu página de admisión</b> en la ficha, con UTM para que midas las visitas en tu analítica.</li>
<li><b>Sin tocar los datos</b>: el ranking mundial, las carreras y las notas de corte salen de fuentes oficiales y no se pueden comprar.</li></ul></section>
{precio_html}
<section class="card" id="solicitar"><h2>{"Empieza con tu mes gratis" if PRECIO.get("prueba_dias") else "Solicitar información"}</h2>
<form id="formAnun" class="form-anun"><input type="text" name="web" tabindex="-1" autocomplete="off" class="vh" aria-hidden="true">
<label>Universidad<input name="universidad" id="anunU" required maxlength="160" list="anunL" autocomplete="off" placeholder="Empieza a escribir y elígela de la lista"><datalist id="anunL"></datalist></label><input type="hidden" name="id" id="anunId">
<label>Tu nombre y cargo<input name="nombre" required maxlength="120"></label>
<label>Correo institucional<input type="email" name="correo" required maxlength="160"></label>
<label>Página de admisión<input type="url" name="admision" required maxlength="300" placeholder="https://"></label>
<label>Frase para tu ficha (opcional)<input name="texto" maxlength="90" placeholder="Por ejemplo: Matrícula abierta para septiembre"></label>
<label>Mensaje (opcional)<textarea name="mensaje" rows="4" maxlength="2000" placeholder="Países o ciudades que te interesan, fechas de tu campaña de admisión…"></textarea></label>
<label class="chk"><input type="checkbox" name="acepto" required> Acepto la <a href="https://aurzane.com/privacidad.html" target="_blank" rel="noopener">política de privacidad</a></label>
<button type="submit" class="btn btn-osc">Enviar solicitud</button><p id="anunRes" class="sub" aria-live="polite"></p></form></section>
</div></main>
<script>(function(){{var f=document.getElementById('formAnun'),U=document.getElementById('anunU'),L=document.getElementById('anunL'),I=document.getElementById('anunId'),D=null,m=/[?&]u=([a-z0-9-]+[/][a-z0-9-]+)/.exec(location.search);
function idDe(x){{return D.p[x[1]][0]+'/'+x[2]}}
function norm(t){{return (t||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}}
function resolver(){{I.value='';if(!D)return;var v=U.value.trim();D.u.some(function(x){{if(x[0]===v){{I.value=idDe(x);return true}}}})}}
fetch('{BASE}datos/indice.json').then(function(r){{return r.json()}}).then(function(d){{D=d;if(m){{d.u.some(function(x){{if(idDe(x)===m[1]){{U.value=x[0];I.value=m[1];return true}}}})}}}}).catch(function(){{}});
U.addEventListener('input',function(){{resolver();if(!D||U.value.length<3)return;var q=norm(U.value),n=0,h='';D.u.some(function(x){{if(norm(x[0]).indexOf(q)>=0){{h+='<option value="'+x[0].replace(/"/g,'&quot;')+'">'+D.p[x[1]][2]+'</option>';n++}}return n>=8}});L.innerHTML=h}});
U.addEventListener('change',resolver);
if(/[?&]pagado=1/.test(location.search)){{var ok=document.createElement('div');ok.className='anun-ok';ok.setAttribute('role','status');ok.innerHTML='<b>Pago recibido. Gracias.</b> Tu universidad sigue destacada y te hemos enviado la factura por correo. La suscripción se renueva sola y la puedes cancelar cuando quieras desde el enlace del correo.';var m=document.querySelector('main')||document.body;m.insertBefore(ok,m.firstChild);ok.scrollIntoView();}}
f.addEventListener('submit',function(ev){{ev.preventDefault();resolver();var r=document.getElementById('anunRes');if(!I.value){{r.textContent='Elige tu universidad de la lista que aparece al escribir.';U.focus();return}}
var d=Object.fromEntries(new FormData(f));d.acepto=d.acepto?1:0;r.textContent='Enviando…';
fetch('https://aurzane.com/patrocinio.php',{{method:'POST',headers:{{'Content-Type':'text/plain'}},body:JSON.stringify(d)}}).then(function(x){{return x.json()}}).then(function(j){{r.textContent=j.ok?(j.mensaje||'Recibido.'):(j.error||'No se pudo enviar.');if(j.ok)f.reset()}}).catch(function(){{r.textContent='No se pudo enviar. Escríbenos a hola@aurzane.com.'}})}});}})();</script>''' + pie()
    escribir('anunciate/index.html', h)
    URLS.append((SITIO + BASE + 'anunciate/', '0.3'))
    print('Patrocinios vigentes:', activas)


def acerca():
    filas = ''.join(f'<tr><td>{bandera(PAISES[p][0])} {e(p)}</td><td class="num">{fmt(len(por_pais[p]))}</td><td class="num">{fmt(sum(u["n"] for u in por_pais[p]))}</td><td>{NIVEL_LBL[nivel_pais(p)]}</td></tr>' for p in ORDEN_P)
    h = cabeza('Fuentes y método del catálogo de universidades | AURZANE NEXUS', 'De dónde salen los datos del catálogo de universidades de AURZANE NEXUS y cómo se actualizan.', SITIO + BASE + 'acerca/') + topbar() + f'''
<main><section class="hero" style="padding-bottom:36px"><div class="wrap">{migas(("Universidades", BASE), ("Fuentes y método", ""))}<h1>Fuentes y <em>método</em></h1><p class="lead">Cómo construimos el catálogo y de dónde sale cada dato.</p></div></section>
<div class="wrap" style="max-width:900px;margin-top:30px">
<section class="card" id="ranking"><h2>Ranking mundial</h2><p>El ranking que ves en cada ficha y en el <a href="{BASE}comparar/">comparador</a> sale de <a href="https://openalex.org" target="_blank" rel="noopener">OpenAlex</a>, un índice abierto (licencia CC0) de la producción científica de todas las instituciones del mundo. Ordenamos más de {fmt(RANK.get("_total") or 0)} instituciones educativas por el número de citas que reciben sus publicaciones y mostramos la posición mundial y la posición dentro de su país, junto al índice h. Mide impacto investigador, no la calidad de la docencia ni la empleabilidad, y no es el ranking QS ni el THE. Se actualiza solo cada mes{(" (último dato: " + RANK["_fecha"] + ")") if RANK.get("_fecha") else ""}.</p></section>
<section class="card"><h2>Fuentes</h2>
<p><b>España:</b> Registro de Universidades, Centros y Títulos (RUCT) del Ministerio de Ciencia, Innovación y Universidades. Incluimos los grados oficiales vigentes (publicados en el BOE o autorizados por la comunidad autónoma), con su rama, su campo de estudio, sus créditos y los municipios donde se imparten.</p>
<p><b>Ecuador:</b> registro oficial de instituciones y carreras vigentes de la SENESCYT.</p>
<p><b>Colombia:</b> SNIES del Ministerio de Educación Nacional (datos abiertos en datos.gov.co): instituciones activas y programas activos. En esa base el nombre del programa no viene bien, así que cada programa se muestra con el título oficial que otorga.</p>
<p><b>Chile:</b> base de oferta académica del SIES (Subsecretaría de Educación Superior, mifuturo.cl): carreras y programas vigentes con admisión de estudiantes nuevos, con duración, arancel anual y acreditación.</p>
<p><b>Estados Unidos:</b> College Scorecard del Departamento de Educación.</p>
<p><b>Resto de países:</b> fuentes oficiales de cada país y webs de las propias instituciones. En los países añadidos más recientemente publicamos solo sus universidades principales, con su web oficial comprobada.</p>
<p>Actualizado el {HOY.strftime('%d/%m/%Y')}. ¿Ves un error? Escríbenos a <a href="mailto:hola@aurzane.com">hola@aurzane.com</a>.</p></section>
<section class="card"><h2>Cobertura por país</h2><div class="comp" style="border:0"><table><thead><tr><th>País</th><th>Instituciones</th><th>Carreras</th><th>Nivel de detalle</th></tr></thead><tbody>{filas}</tbody></table></div></section>
</div></main>''' + pie()
    escribir('acerca/index.html', h)
    URLS.append((SITIO + BASE + 'acerca/', '0.4'))


def sitemap():
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'<url><loc>{e(u)}</loc><lastmod>{HOY.isoformat()}</lastmod><priority>{pr}</priority></url>\n' for u, pr in URLS) + '</urlset>\n'
    escribir('../sitemap-universidades.xml', x)


def htaccess():
    reglas = ['# Universidades: redirecciones desde las URL antiguas', 'RewriteEngine On',
              'RewriteRule ^universidades/buscador\\.html$ /universidades/ [R=301,L,QSA]']
    viejo = {'espana': 'espana', 'estados-unidos': 'estados-unidos'}
    for p in ORDEN_P:
        reglas.append(f'RewriteRule ^universidades/pais/{PSLUG[p]}\\.html$ /universidades/{PSLUG[p]}/ [R=301,L]')
    eu = por_pais.get('Ecuador', [])
    ciudades = {slug(u['ciudad']) for u in eu if u['ciudad']}
    multi = {slug(c) for c, n in collections.Counter(u['ciudad'] for u in eu if u['ciudad']).items() if n >= 2}
    for c in sorted(ciudades):
        destino = f'/universidades/ecuador/ciudad/{c}/' if c in multi else '/universidades/ecuador/'
        reglas.append(f'RewriteRule ^universidades/ciudad/{c}\\.html$ {destino} [R=301,L]')
    reglas.append('RewriteRule ^universidades/ciudad/.+\\.html$ /universidades/ecuador/ [R=301,L]')
    reglas.append('RewriteRule ^universidades/pais/.+\\.html$ /universidades/paises/ [R=301,L]')
    escribir('../htaccess-universidades.txt', '\n'.join(reglas) + '\n')


# ---------------------------------------------------------------- ejecutar
if os.path.exists(SALIDA):
    shutil.rmtree(SALIDA)
os.makedirs(os.path.join(SALIDA, 'assets'))
shutil.copy(os.path.join(AQUI, 'univ.css'), os.path.join(SALIDA, 'assets/univ.css'))
shutil.copy(os.path.join(AQUI, 'univ.js'), os.path.join(SALIDA, 'assets/univ.js'))
if os.path.exists(os.path.join(AQUI, 'og.jpg')):
    shutil.copy(os.path.join(AQUI, 'og.jpg'), os.path.join(SALIDA, 'og.jpg'))
datos()
portada()
paises()
for p in ORDEN_P:
    for u in por_pais[p]:
        if u['ciudad']: CIUDAD_PAISES[u['ciudad']].add(p)
for p in ORDEN_P:
    pagina_pais(p)
    us = por_pais[p]
    por_ciudad = collections.defaultdict(list)
    for u in us:
        por_ciudad[u['ciudad']].append(u)
    for u in us:
        vec = [v for v in sorted(por_ciudad[u['ciudad']], key=lambda v: -v['n']) if v is not u] if u['ciudad'] else []
        ficha(u, vec)
notas_de_corte()
que_puedo_estudiar()
mi_lista()
comparar()
anunciate()
acerca()
sitemap()
print('fichas casi vacías fuera de Google:', len(FINAS))
htaccess()
sys.path.insert(0, AQUI)
import en as _en   # versión en inglés «Study in Spain» (nexus.aurzane.com/en/)
_en.generar(globals())
print(f'OK {TOTAL_U} universidades, {TOTAL_C} carreras, {len(ORDEN_P)} países, {len(URLS)} URLs')
