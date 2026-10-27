# -*- coding: utf-8 -*-
"""Generador del portal de universidades de AURZANE NEXUS.

Entrada (carpeta de datos):
  sb_universidades.json.gz, sb_carreras.json.gz  -> exportación de Supabase
  ruct.json                                      -> España completa desde el RUCT (opcional)
  principales.json                               -> universidades principales de países nuevos (opcional)
Salida: carpeta lista para subir a nexus.aurzane.com/universidades/

Uso: python3 gen.py DATOS SALIDA
"""
import json, gzip, re, os, sys, html, unicodedata, collections, shutil, datetime

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


# ---------------------------------------------------------------- acentos (Ecuador)
ACENTOS = {w.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u'): w for w in '''
Administración Agronomía Agropecuaria Agrícola Analítica Análisis Antropología Arqueología Artística Artísticas Auditoría Automatización Biología Biotecnología Biomédica Bioquímica Comunicación Contabilidad Construcción Criminalística Criminología Diseño Dirección Docencia Ecología Economía Educación Electricidad Eléctrica Electromecánica Electrónica Energía Enfermería Estética Física Fisioterapia Fonoaudiología Gastronomía Geografía Geología Gestión Gráfico Gráfica Hidráulica Historia Hotelería Información Informática Ingeniería Inglés Innovación Investigación Jurídica Jurídicas Lingüística Logística Matemática Matemáticas Mecánica Mecatrónica Medicina Metalmecánica Minería Música Nutrición Odontología Óptica Optometría Pedagogía Periodismo Petróleos Petroquímica Política Políticas Producción Programación Psicología Psicopedagogía Publicidad Química Radiología Recreación Rehabilitación Relaciones Seguridad Sociología Software Técnica Técnico Tecnología Tecnologías Telecomunicaciones Telemática Terapéutica Topografía Traducción Turística Turismo Veterinaria Zootecnia Acuicultura Cerámica Fotografía Cinematografía Animación Mecánico Electrónico Cosmetología Podología Atención Promoción Prevención Planificación Organización Comercialización Construcción Edificación Pública Público Inclusión Mediación Gerontología Logopedia Neuropsicología Psicorrehabilitación Rehabilitación Física Tecnológico Tecnológica Teología Filosofía Lógica Biomédicas Ciencias Química Farmacia Bioquímica Clínica Clínico Clínicas Diagnóstico Imagenología Imágenes Cirugía Agroindustrial Industrialización Cartografía Climatización Refrigeración Instalación Instalaciones Panadería Pastelería Cocina Bebidas Acústica Escénicas Plásticas Lenguas Idiomas Comunicación Educativa Educativo Básica Inicial Atención Integral Aeronáutica Náutica Marítima Pesquería Forestal Agroforestal Biomecánica Robótica Inteligencia Artificial Cibernética Ciberseguridad Electromédica Higiene Odontológica Mecánica Automotriz Prótesis Dental Química Laboratorio Analítico Analíticos Técnicas
'''.split()}
for _w in 'Católica Politécnica Amazónica Bolívar Simón Península Ibérica Pedagógico Académico Académica Manabí Tecnológicos Estatal Técnico Educación Agrícola Pacífico Atlántico Caribe Guayaquil Milagro Andrés Martín Ángel Ramón Hernández Martínez Pérez Gómez Rodríguez Bilingüe Indígena Marítimo Politécnico Médica Médicas'.split():
    ACENTOS[unicodedata.normalize('NFD', _w.lower()).encode('ascii', 'ignore').decode()] = _w
ACENTOS.update({'y': 'y', 'en': 'en', 'de': 'de', 'del': 'del'})


def acentuar(t):
    if not t or any(c in t for c in 'áéíóúÁÉÍÓÚñ'):
        return t
    def r(m):
        w = m.group(0); k = w.lower()
        if k in ACENTOS and len(k) > 3:
            a = ACENTOS[k]
            return a[0].upper() + a[1:] if w[0].isupper() else a.lower()
        return w
    return re.sub(r'[A-Za-z]+', r, t)


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
            if c.get('modalidad') and c['modalidad'] not in x['mod']: x['mod'].append(c['modalidad'])
            for sd in sedes_c:
                if sd not in x['sedes']: x['sedes'].append(sd)
            continue
        x = {'n': nom, 'area': area, 'grupo': grupo or 'Grado', 'campo': c.get('campo_amplio') if c.get('rama') else '', 'mod': [c['modalidad']] if c.get('modalidad') else [], 'sedes': sedes_c, 'cred': cred, 'prof': c.get('profesion_regulada') or ''}
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


def cabeza(titulo_pag, desc, canon, og_img=None, jsonld=None, robots=None):
    og_img = og_img or f'{SITIO}/universidades/og.jpg'
    return f'''<!DOCTYPE html>
<html lang="es" data-v="{V}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>{e(titulo_pag)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
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
{a('/calculadora-nota-pau/', 'Nota PAU', 'pau')}
{a(BASE + 'mi-lista/', 'Mi lista <span class="lista-n" hidden>0</span>', 'lista')}
<a class="cuenta" href="https://aurzane.com/mi-aurzane.html">👤 Mi AURZANE</a>
</nav></div></header>
'''


def pie():
    return f'''<footer><div class="wrap"><span>© {HOY.year} AURZANE NEXUS · Catálogo de universidades</span><span><a href="https://nexus.aurzane.com/">NEXUS</a><a href="{BASE}">Universidades</a><a href="{BASE}acerca/">Fuentes y método</a><a href="https://aurzane.com/privacidad.html">Privacidad</a></span></div></footer>
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
            filas.append([u['slug'], u['nombre'], u['ciudad'], u['region'], u['tipo'], u['tipo_ies'], u['n'], u['nivel'], ua, u['extra'].get('acronimo', ''), u['logo']])
            for c in u['carreras']:
                if u['nivel'] == 'programas':
                    carr.append([i, c['n'], ai.get(c['area'], -1)])
        escribir(f'datos/{PSLUG[p]}.json', json.dumps({'pais': p, 'areas': areas, 'u': filas}, ensure_ascii=False, separators=(',', ':')))
        if carr:
            escribir(f'datos/{PSLUG[p]}-carreras.json', json.dumps({'c': carr}, ensure_ascii=False, separators=(',', ':')))


# ---------------------------------------------------------------- tarjeta estática (SEO, antes del JS)
def tarjeta(u):
    p = PSLUG[u['pais']]
    url = f'{BASE}{p}/{u["slug"]}/'
    tipo = f'<span class="etq {"pub" if u["tipo"] == "Pública" else "priv"}">{e(u["tipo"])}</span>' if u['tipo'] else ''
    lugar = ', '.join(x for x in [u['ciudad'], u['region']] if x) or u['pais']
    cnt = f'<b>{fmt(u["n"])}</b> {"áreas" if u["nivel"] == "areas" else ("grados" if u["pais"] == "España" else "carreras")}' if u['n'] else 'Carreras en su web'
    return (f'<article class="uc"><div class="top"><span class="mono" aria-hidden="true">{e(iniciales(u["nombre"]))}</span><div style="min-width:0;flex:1"><h3><a href="{url}">{e(u["nombre"])}</a></h3>'
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
    estaticas = ''.join(tarjeta(u) for u in sorted(us, key=lambda x: (0 if x['tipo_ies'].lower().startswith('universi') else 1, -x['n'], x['nombre']))[:36])
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
<a class="scard" href="/calculadora-nota-pau/" style="background:linear-gradient(135deg,#2b3fb8,#0b1030)"><span class="e">🧮</span><b>Calculadora de nota PAU</b><span>Tu nota de acceso y de admisión sobre 14, y si te llega para tu carrera.</span></a>
<a class="scard" href="https://ovp.aurzane.com/" style="background:linear-gradient(135deg,#2b3fb8,#8b7bff)"><span class="e">🧭</span><b>Test vocacional gratis</b><span>Seis instrumentos y un informe con las carreras que encajan contigo.</span></a>
<a class="scard" href="https://mind.aurzane.com/test-de-personalidad/" style="background:linear-gradient(135deg,#ff7a45,#a35be0)"><span class="e">🧠</span><b>Test de personalidad</b><span>Descubre tu perfil entre 11 y las carreras afines a él.</span></a>
</div></section>

<section class="bloque" style="max-width:800px"><h2 class="t">Preguntas frecuentes</h2>
<details class="faq"><summary>¿De dónde salen los datos?</summary><p>España viene del Registro de Universidades, Centros y Títulos (RUCT) del Ministerio de Ciencia, Innovación y Universidades. Ecuador, del registro oficial de la SENESCYT. Estados Unidos, del College Scorecard del Departamento de Educación. El resto, de las fuentes oficiales de cada país y de las webs de cada universidad. Más detalles en <a href="{BASE}acerca/">fuentes y método</a>.</p></details>
<details class="faq"><summary>¿Por qué algunas universidades no tienen carreras?</summary><p>En algunos países solo publicamos las universidades principales o sus áreas y facultades. En esos casos te enlazamos a su web oficial, donde está su oferta completa.</p></details>
<details class="faq"><summary>¿Puedo comparar universidades?</summary><p>Sí. Pulsa ☆ en cualquier universidad para guardarla en <a href="{BASE}mi-lista/">Mi lista</a>, donde puedes compararlas lado a lado.</p></details>
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
        tit = f'Mejores universidades de {p}: las principales | AURZANE NEXUS'
        lead = f'Las universidades principales de {p}, con su ciudad, tipo y web oficial.'
    else:
        tit = f'Universidades en {p}: {fmt(len(us))} instituciones{" y " + fmt(nc) + " carreras" if nivel == "programas" else ""} | AURZANE NEXUS'
        lead = f'{fmt(len(us))} universidades e institutos de educación superior en {p}' + (f', con {fmt(nc)} carreras.' if nivel == 'programas' else '.') + ' Filtra por ciudad, tipo y área.'
    jl = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': f'Universidades de {p}', 'numberOfItems': len(us),
          'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{SITIO}{BASE}{PSLUG[p]}/{u["slug"]}/', 'name': u['nombre']} for i, u in enumerate(sorted(us, key=lambda x: -x['n'])[:50])]}
    top_c = [c for c, n in ciudades.most_common(12) if n >= 2]
    ciudades_html = ''
    if top_c and p not in ('Estados Unidos',):
        ciudades_html = '<section class="bloque"><h2 class="t">Universidades por ciudad</h2><div class="paises">' + ''.join(
            f'<a class="pais" href="{BASE}{PSLUG[p]}/ciudad/{slug(c)}/"><span><b>{e(c)}</b><small>{ciudades[c]} instituciones</small></span></a>' for c in top_c) + '</div></section>'
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
<p class="fuente">{fuente_pais(p)}</p></div>
</main>''' + pie()
    escribir(f'{PSLUG[p]}/index.html', h)
    URLS.append((f'{SITIO}{BASE}{PSLUG[p]}/', '0.9' if p in ('España', 'Ecuador') else '0.8'))
    if p not in ('Estados Unidos',):
        for c in [c for c, n in ciudades.items() if n >= 2]:
            pagina_ciudad(p, c, [u for u in us if u['ciudad'] == c])


def fuente_pais(p):
    if p == 'España': return 'Fuente: Registro de Universidades, Centros y Títulos (RUCT), Ministerio de Ciencia, Innovación y Universidades. Solo grados oficiales vigentes. Actualizado: ' + HOY.strftime('%d/%m/%Y') + '.'
    if p == 'Ecuador': return 'Fuente: registro oficial de carreras vigentes de la SENESCYT. Los nombres de las carreras aparecen tal como figuran en el registro.'
    if p == 'Estados Unidos': return 'Fuente: College Scorecard, Departamento de Educación de EE. UU. Los nombres de los programas aparecen en inglés, como en la fuente oficial.'
    if nivel_pais(p) == 'basico': return 'Selección de las universidades principales del país. Consulta la web oficial de cada una para ver su oferta completa.'
    return 'Fuentes oficiales del país y webs de cada institución. En algunas universidades mostramos áreas o facultades en lugar del listado completo de carreras.'


def pagina_ciudad(p, c, us):
    iso = PAISES[p][0]
    tit = f'Universidades en {c} ({p}): {len(us)} instituciones | AURZANE NEXUS'
    lead = f'Las {len(us)} universidades e institutos con sede en {c}, {p}' + (f', con {fmt(sum(u["n"] for u in us))} carreras.' if any(u['n'] for u in us) else '.')
    h = cabeza(tit, lead, f'{SITIO}{BASE}{PSLUG[p]}/ciudad/{slug(c)}/') + topbar('espana' if p == 'España' else 'paises') + f'''
<main><section class="hero" style="padding-bottom:40px"><div class="wrap">{migas(("Universidades", BASE), (p, f"{BASE}{PSLUG[p]}/"), (c, ""))}
<h1>{bandera(iso, "g")} Universidades en <em>{e(c)}</em></h1><p class="lead">{e(lead)}</p></div></section>
{panel_listado(p, us, ciudad_fija=c)}
<div class="wrap"><p class="fuente">{fuente_pais(p)}</p></div></main>''' + pie()
    escribir(f'{PSLUG[p]}/ciudad/{slug(c)}/index.html', h)
    URLS.append((f'{SITIO}{BASE}{PSLUG[p]}/ciudad/{slug(c)}/', '0.6'))


# ---------------------------------------------------------------- ficha de universidad
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
            der = []
            if c.get('cred'): der.append(f'{c["cred"]} ECTS' if es_es else c['cred'])
            if c.get('mod'): der.append(' · '.join(c['mod']))
            if c.get('sedes') and (len(c['sedes']) > 1 or (c['sedes'][0] != u['ciudad'])): der.append(', '.join(c['sedes'][:4]) + ('…' if len(c['sedes']) > 4 else ''))
            prof = f'<em class="prof">Habilita para: {e(c["prof"])}</em>' if c.get('prof') else ''
            items += f'<li><span>{e(c["n"])}{prof}{"<small>" + e(" · ".join(det)) + "</small>" if det else ""}</span>{"<small>" + e(" · ".join(der)) + "</small>" if der else ""}</li>'
        lis += f'<div class="grupo" data-area="{e(g)}"><h3><span>{e(g)}</span><span>{len(grupos[g])}</span></h3><ul class="carreras">{items}</ul></div>'
    if n:
        bloque_c = f'''<section class="card" id="carreras"><div class="carr-cab"><h2>{fmt(n)} {palabra}</h2>{"<input type=search class=carr-busca placeholder='Buscar en sus " + palabra + "' aria-label='Buscar carrera'>" if n > 8 else ""}</div>
{chips}{lis}<p id="carrVacio" class="sub" hidden>No hay {palabra} con esa búsqueda.</p>
{"<p class='aviso'>Esta universidad publica sus áreas y facultades. Consulta su oferta completa de carreras en su web oficial.</p>" if u["nivel"] == "areas" else ""}</section>'''
    else:
        bloque_c = f'<section class="card" id="carreras"><h2>Carreras</h2><p class="aviso">Todavía no tenemos el listado de carreras de esta institución. Puedes consultar su oferta completa en su {"<a href=" + e(u["web"]) + " target=_blank rel=noopener>web oficial</a>" if u["web"] else "web oficial"}.</p></section>'
    dato = [('País', f'{bandera(iso)} {e(p)}'), ('Ciudad', e(u['ciudad'] or '-'))]
    if u['region']: dato.append(('Comunidad autónoma' if es_es else 'Región', e(u['region'])))
    dato.append(('Tipo', e(u['tipo_txt'] or '-')))
    dato.append(('Institución', e(u['tipo_ies'])))
    if u['extra'].get('acronimo'): dato.append(('Siglas', e(u['extra']['acronimo'])))
    if u['extra'].get('anio'): dato.append(('Creada en', e(u['extra']['anio'])))
    if u['extra'].get('en_linea'): dato.append(('Modalidad', 'En línea'))
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
    h = cabeza(tit, desc_meta, url, jsonld=jl) + topbar('espana' if es_es else 'paises') + f'''
<main><section class="hero ficha-h"><div class="wrap">{migas(("Universidades", BASE), (p, f"{BASE}{ps}/"), *([(u["ciudad"], f"{BASE}{ps}/ciudad/{slug(u['ciudad'])}/")] if u["ciudad"] and vecinas and p != "Estados Unidos" else []), (u["nombre"], ""))}
<div class="fila" style="margin-top:16px"><span class="mono" aria-hidden="true">{e(u["extra"].get("acronimo") or iniciales(u["nombre"]))[:5]}</span><div><h1 style="margin:0">{e(u["nombre"])}</h1></div></div>
<ul class="meta">{''.join(meta)}</ul>{f'<p class="lead" style="margin-top:14px">{e(u["descripcion"])}</p>' if u["descripcion"] else ''}
<div class="acc">{f'<a class="btn btn-luz" href="{e(u["web"])}" target="_blank" rel="noopener nofollow">Web oficial ↗</a>' if u["web"] else ''}<button type="button" class="btn btn-claro" data-guardar data-id="{ps}/{u["slug"]}" data-n="{e(u["nombre"])}" data-url="{BASE}{ps}/{u["slug"]}/" aria-pressed="false">☆ Guardar</button>{'<a class="btn btn-claro" href="#carreras">Ver ' + palabra + '</a>' if n else ''}</div>
</div></section>
<div class="wrap"><div class="ficha"><div>{bloque_c}</div>
<aside><section class="card"><h2>Datos</h2>{datos_html}</section>{cta}{cerca}</aside></div>
<p class="fuente">{fuente_pais(p)} </p>
<div class="reportar"><span>¿Algún dato no es correcto o un enlace no funciona?</span><button type="button" class="btn btn-borde" data-reportar data-tipo="dato" data-ref="{e(u["nombre"] + " (" + p + ")")}">⚑ Reportar un error</button></div></div>
</main>''' + pie()
    escribir(f'{ps}/{u["slug"]}/index.html', h)
    URLS.append((url, '0.7' if n else '0.5'))


def mi_lista():
    h = cabeza('Mi lista de universidades | AURZANE NEXUS', 'Tus universidades guardadas, comparadas lado a lado.', SITIO + BASE + 'mi-lista/', robots='noindex,follow') + topbar('lista') + f'''
<main><section class="hero" style="padding-bottom:36px"><div class="wrap">{migas(("Universidades", BASE), ("Mi lista", ""))}<h1>Mi <em>lista</em></h1><p class="lead">Las universidades que guardas, comparadas lado a lado. Se guardan en este dispositivo.</p></div></section>
<div class="wrap" style="margin-top:26px"><div id="miLista"><p class="sub">Cargando…</p></div></div></main>''' + pie()
    escribir('mi-lista/index.html', h)


def acerca():
    filas = ''.join(f'<tr><td>{bandera(PAISES[p][0])} {e(p)}</td><td class="num">{fmt(len(por_pais[p]))}</td><td class="num">{fmt(sum(u["n"] for u in por_pais[p]))}</td><td>{NIVEL_LBL[nivel_pais(p)]}</td></tr>' for p in ORDEN_P)
    h = cabeza('Fuentes y método del catálogo de universidades | AURZANE NEXUS', 'De dónde salen los datos del catálogo de universidades de AURZANE NEXUS y cómo se actualizan.', SITIO + BASE + 'acerca/') + topbar() + f'''
<main><section class="hero" style="padding-bottom:36px"><div class="wrap">{migas(("Universidades", BASE), ("Fuentes y método", ""))}<h1>Fuentes y <em>método</em></h1><p class="lead">Cómo construimos el catálogo y de dónde sale cada dato.</p></div></section>
<div class="wrap" style="max-width:900px;margin-top:30px">
<section class="card"><h2>Fuentes</h2>
<p><b>España:</b> Registro de Universidades, Centros y Títulos (RUCT) del Ministerio de Ciencia, Innovación y Universidades. Incluimos los grados oficiales vigentes (publicados en el BOE o autorizados por la comunidad autónoma), con su rama, su campo de estudio, sus créditos y los municipios donde se imparten.</p>
<p><b>Ecuador:</b> registro oficial de instituciones y carreras vigentes de la SENESCYT.</p>
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
    pagina_pais(p)
    us = por_pais[p]
    por_ciudad = collections.defaultdict(list)
    for u in us:
        por_ciudad[u['ciudad']].append(u)
    for u in us:
        vec = [v for v in sorted(por_ciudad[u['ciudad']], key=lambda v: -v['n']) if v is not u] if u['ciudad'] else []
        ficha(u, vec)
mi_lista()
acerca()
sitemap()
htaccess()
print(f'OK {TOTAL_U} universidades, {TOTAL_C} carreras, {len(ORDEN_P)} países, {len(URLS)} URLs')
