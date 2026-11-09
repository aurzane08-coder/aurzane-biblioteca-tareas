# Marketing automático de AURZANE (0 €). Redes: Telegram, Bluesky, Mastodon, Instagram, Facebook, YouTube, TikTok, Pinterest y YouTube.
#   python3 marketing/mk.py catalogo     -> catalogo.json (fijos + libros abiertos + notas de corte + páginas nuevas del sitemap)
#   python3 marketing/mk.py planificar   -> calendario de los próximos 14 días, tarjetas que falten, enlaces cortos y feed
#   python3 marketing/mk.py publicar N   -> publica la franja N (1 mañana, 2 tarde) de hoy en las redes con secretos configurados
#   python3 marketing/mk.py clics LOG    -> suma los clics del registro del servidor a clics.csv
# Reglas: cada red recibe un producto distinto en cada franja y recorre todo el catálogo antes de repetir;
# los productos nuevos salen primero; nada se publica en grupos ni comunidades de terceros.
import socket; socket.setdefaulttimeout(90)   # ninguna descarga puede colgar la ejecución
import time
import json, os, re, sys, hashlib, datetime, collections, urllib.request, urllib.parse, html, csv

D = os.path.dirname(os.path.abspath(__file__))
REDES = ['telegram', 'bluesky', 'mastodon', 'instagram', 'facebook', 'threads', 'pinterest']  # X desactivada: cobra por publicar
REDES_VIDEO = ['instagram', 'facebook', 'youtube', 'tiktok', 'telegram']  # franja 4: vídeo vertical
TIPOS_VIDEO = ('frase', 'test', 'calculadora', 'curiosidad')
VID = ('4', '5', '6')   # franjas de vídeo vertical: 4 (tarde, de todo), 5 (mañana, frases y curiosidades) y 6 (media tarde, solo YouTube y TikTok)
REDES_V6 = ['youtube', 'tiktok']
def redes_de(fr): return REDES_V6 if fr == '6' else REDES_VIDEO
SITIO_IMG = 'https://aurzane.com/marketing/'
IR = 'https://aurzane.com/ir/'
HOY = datetime.date.today()


def leer(n, defecto=None):
    p = os.path.join(D, n)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else defecto


def guardar(n, d):
    json.dump(d, open(os.path.join(D, n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def get(url, t=60):
    ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
    for intento in range(3):
        try:
            r = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': '*/*'})
            return urllib.request.urlopen(r, timeout=t).read().decode('utf-8', 'replace')
        except Exception:
            if intento == 2: raise
            import time; time.sleep(5)


def recorta(t, n):
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= n: return t
    c = t[:n]
    m = max(c.rfind('. '), c.rfind('? '), c.rfind('! '))
    return c[:m + 1] if m > n * .5 else c[:c.rfind(' ')].rstrip(',;:') + '…'


def camel(s):
    s = re.sub(r'[^\wáéíóúñü ]', ' ', s, flags=re.I)
    t = ''.join(w[:1].upper() + w[1:] for w in s.split() if len(w) > 2)
    return t if len(t) <= 24 else ''


# ------------------------------------------------------------------ catálogo
def catalogo():
    fijos = leer('fijos.json')['productos']
    prev = {p['id']: p for p in (leer('catalogo.json', {'productos': []})['productos'])}
    out = []
    for p in fijos: out.append(dict(p, origen='fijo'))
    # libros con lectura directa (licencia abierta y PDF propio)
    try:
        src = os.environ.get('CATALOGO_JS') or 'https://aurzane.com/biblioteca/catalogo.js'
        js = open(src, encoding='utf-8').read() if os.path.exists(src) else get(src)
        B = json.loads(js[js.index('{'):js.rstrip().rstrip(';').rindex('}') + 1])
        temas = {str(t.get('n', t.get('id'))): t['nombre'] for t in B['temas']}
        for l in B['libros']:
            if not l.get('pdf') or not l.get('licencia'): continue
            aut = (l.get('autores') or '').split(';')[0].strip()
            if ',' in aut: a, b = aut.split(',', 1); aut = f'{b.strip()} {a.strip()}'
            tit = l['titulo'].strip()
            tn = [temas.get(k) for k in (l.get('temas') or {})][:2]
            out.append(dict(id='libro-' + l['id'], tipo='libro', mundo='aurzane', origen='biblioteca',
                            url=f"https://aurzane.com/biblioteca/libro/{l['id']}.html", titulo=tit,
                            ganchos=[f'Libro gratis: {tit}', f'{tit}, de {aut}' if aut else tit, f'Para leer hoy: {tit}'],
                            texto=recorta(l.get('resumen'), 230), autor=aut, paginas=l.get('paginas'), licencia=l['licencia'],
                            hashtags=['LibrosGratis'] + [c for c in (camel(t) for t in tn if t) if c], aviso='', img=None, emoji='📖',
                            alta=l.get('alta', '')))
    except Exception as e:
        print('Biblioteca no disponible, uso la copia anterior:', e)
        out += [p for p in prev.values() if p.get('tipo') == 'libro']
    # libros de la tienda (de pago, con ficha propia en aurzane.com/libros/): entran en la rotación de libros para dar a conocer la tienda
    try:
        for x in json.load(open(os.path.join(os.path.dirname(D), 'tienda', 'catalogo.json'), encoding='utf-8')):
            if not x.get('portada'): continue
            gancho_t = (x.get('tendencia') or '').strip()
            out.append(dict(id='lectura-' + x['id'], tipo='lectura', mundo='aurzane', origen='tienda', url=f'https://aurzane.com/libros/{x["id"]}/',
                            titulo=x['titulo'], autor=x['autor'],
                            ganchos=[f'Libro recomendado: {x["titulo"]}', f'{x["titulo"]}, de {x["autor"]}', f'¿Qué leer este mes? {x["titulo"]}'],
                            texto=recorta(x.get('porque') or gancho_t or x.get('resumen') or f'{x["titulo"]}, de {x["autor"]}.', 230),
                            hashtags=['LibrosRecomendados', 'QueLeer', 'Lectura', 'Libros'], aviso='Contiene enlace de afiliado.', img=None, emoji='📚',
                            alta=x.get('fecha', '')))
    except FileNotFoundError: pass
    except Exception as e: print('tienda', e)
    # notas de corte: carreras con muchas universidades
    try:
        NC = json.load(open(os.path.join(D, '..', 'univ', 'data', 'notas_corte.json'), encoding='utf-8'))
        g = collections.defaultdict(list)
        for f in NC['filas']:
            if f.get('nota') and f.get('nivel') == 'GRADO':
                t = re.sub(r'^Grado (Universitario )?(en|de) ', '', f['titulo'].strip(), flags=re.I)
                t = re.sub(r'\s*/\s*(Bachelor|Degree).*$', '', t, flags=re.I)
                g[t[:1].upper() + t[1:]].append(f)
        for t, fs in g.items():
            if len(fs) < 10: continue
            s = re.sub(r'[^a-z0-9]+', '-', t.lower().translate(str.maketrans('áéíóúüñ', 'aeiouun'))).strip('-')
            mx = max(fs, key=lambda f: f['nota']); mn = min(fs, key=lambda f: f['nota'])
            nota = lambda x: f"{x:.3f}".rstrip('0').rstrip('.').replace('.', ',')
            out.append(dict(id='nc-' + s, tipo='notas', mundo='nexus', origen='notas',
                            url=f'https://nexus.aurzane.com/universidades/notas-de-corte/{s}/', titulo=f'Nota de corte de {t}',
                            ganchos=[f'¿Qué nota piden para {t}?', f'Nota de corte de {t}: de {nota(mn["nota"])} a {nota(mx["nota"])}', f'{t}: las notas de corte de {len(fs)} universidades'],
                            texto=f'Curso {fs[0].get("curso", "")}: la más alta es {nota(mx["nota"])} en la {mx["universidad"]}. Consulta las {len(fs)} universidades públicas ordenadas por nota, con datos oficiales.',
                            hashtags=['NotasDeCorte', 'PAU', camel(t)], aviso='', img=None, emoji='📊'))
    except Exception as e:
        print('Notas de corte no disponibles:', e)
    # frases de superación (sobre todo para Instagram)
    import frases
    lista = [(t, 'AURZANE') for t in frases.ORIGINALES] + list(frases.CLASICAS)
    mundos = ['mind', 'live', 'learn', 'aurzane', 'nexus', 'build']
    for t, a in lista:
        fid = 'frase-' + hashlib.md5(t.encode()).hexdigest()[:8]
        out.append(dict(id=fid, tipo='frase', mundo=mundos[int(fid[-2:], 16) % len(mundos)], origen='frases',
                        url='https://mind.aurzane.com/', titulo=t, autor=a, ganchos=[t, t, t], texto=t,
                        hashtags=['FrasesMotivadoras', 'Superación', 'SaludMental', 'CrecimientoPersonal', 'Psicología', 'Bienestar', 'Motivación', 'FrasesDeLaVida'],
                        aviso='', img=None, emoji='',
                        foto_q=frases.FOTOS[int(fid[6:12], 16) % len(frases.FOTOS)]))
    # frases de libros de la biblioteca que la IA propuso y Adrián aprobó en el admin (ai/citas.json)
    try:
        for c in json.load(open(os.path.join(os.path.dirname(D), 'ai', 'citas.json'), encoding='utf-8')):
            if c.get('nota', 0) < 7: continue   # solo frases revisadas por la IA (Gemini) con nota 7 o más
            fid = 'frase-' + hashlib.md5(c['texto'].encode()).hexdigest()[:8]
            out.append(dict(id=fid, tipo='frase', mundo='aurzane', origen='citas', url=c['url'], titulo=c['texto'],
                            autor=', '.join(x for x in (c.get('autor'), c.get('libro')) if x) or 'AURZANE', libro=c.get('libro') or '',
                            ganchos=[c['texto']] * 3, texto=c['texto'],
                            hashtags=['FrasesDeLibros', 'Lectura', 'LibrosGratis', 'Psicología', 'Motivación', 'Bienestar', 'CrecimientoPersonal', 'Frases'],
                            aviso='', img=None, emoji='', foto_q=frases.FOTOS[int(fid[6:12], 16) % len(frases.FOTOS)]))
    except FileNotFoundError: pass
    except Exception as e: print('citas', e)
    # frases célebres de autores clásicos (dominio público) que AURZANE AI va publicando en aurzane.com/frases/ (ai/frases_web.json)
    try:
        for c in json.load(open(os.path.join(os.path.dirname(D), 'ai', 'frases_web.json'), encoding='utf-8')):
            if not c.get('publicada'): continue
            fid = 'frase-' + hashlib.md5(c['texto'].encode()).hexdigest()[:8]
            out.append(dict(id=fid, tipo='frase', mundo='aurzane', origen='frases_web', url='https://aurzane.com/frases/#' + c['id'], titulo=c['texto'],
                            autor=c.get('autor') or 'Proverbio', libro='', ganchos=[c['texto']] * 3, texto=c['texto'],
                            hashtags=['FrasesCélebres', 'FrasesDelDía', 'Reflexión', 'Psicología', 'Motivación', 'Bienestar', 'CrecimientoPersonal', 'Frases'],
                            aviso='', img=None, emoji='', foto_q=frases.FOTOS[int(fid[6:12], 16) % len(frases.FOTOS)]))
    except FileNotFoundError: pass
    except Exception as e: print('frases_web', e)
    # curiosidades escritas por la IA (Gemini) y aprobadas en el admin (ai/curiosidades.json): vídeos cortos para YouTube, Reels y TikTok
    try:
        for c in json.load(open(os.path.join(os.path.dirname(D), 'ai', 'curiosidades.json'), encoding='utf-8')):
            out.append(dict(id=c['id'], tipo='curiosidad', mundo='mind', origen='curiosidades', url=c['url'], titulo=c['titulo'],
                            ganchos=[c['titulo'], c['titulo'] + ' 🧠', c['dato'][:90]], texto=c['resumen'] + (f"\n\nFuente: {c['fuente']}" if c.get('fuente') else ''),
                            hashtags=(c.get('hashtags') or []) + ['Psicología', 'Curiosidades'], aviso='', img=None, emoji='🧠', dato=c['dato']))
    except FileNotFoundError: pass
    except Exception as e: print('curiosidades', e)
    # páginas nuevas del sitemap que aún no están: entran solas
    urls = {p['url'].rstrip('/') for p in out}
    try:
        sm = get('https://aurzane.com/sitemap.xml')
        for u in re.findall(r'<loc>([^<]+)</loc>', sm):
            if u.rstrip('/') in urls or re.search(r'/(biblioteca|universidades)/|\.html$|portal|aurzane\.com/$', u): continue
            pid = 'auto-' + re.sub(r'[^a-z0-9]+', '-', u.split('//')[1].lower()).strip('-')
            if pid in prev: out.append(prev[pid]); continue
            try:
                h = get(u)
                meta = lambda k: html.unescape((re.search(rf'<meta[^>]+(?:property|name)="{k}"[^>]+content="([^"]*)"', h) or [None, ''])[1])
                tit = meta('og:title') or html.unescape((re.search(r'<title>([^<|]*)', h) or [None, u])[1]).strip()
                desc = meta('og:description') or meta('description')
                mundo = (re.match(r'https://(\w+)\.aurzane', u) or [None, 'aurzane'])[1]
                tipo = 'test' if '/test-' in u else 'calculadora' if '/calculadora-' in u else 'seccion'
                out.append(dict(id=pid, tipo=tipo, mundo=mundo, origen='sitemap', url=u, titulo=tit,
                                ganchos=[tit, tit, tit], texto=recorta(desc, 230), hashtags=['AURZANE'],
                                aviso='No es un diagnóstico: es una orientación.' if tipo == 'test' else '', img=None,
                                emoji='🧠' if mundo == 'mind' else '✨', alta=HOY.isoformat()))
                print('Nuevo producto detectado:', u)
            except Exception as e:
                print('No se pudo leer', u, e)
    except Exception as e:
        print('Sitemap no disponible:', e)
    for p in out:
        p.setdefault('alta', (prev.get(p['id']) or {}).get('alta') or p.get('alta') or HOY.isoformat())
        if p['id'] in prev and prev[p['id']].get('alta'): p['alta'] = prev[p['id']]['alta']
    guardar('catalogo.json', {'generado': HOY.isoformat(), 'productos': out})
    print('Catálogo:', len(out), dict(collections.Counter(p['tipo'] for p in out)))


# ------------------------------------------------------------------ planificación
# franja 1 (mañana): herramientas; franja 2 (tarde): rota entre libros, creatividades, notas y secciones
TARDE = ['libro', 'creativo', 'notas', 'libro', 'seccion', 'creativo', 'libro']
GRUPO = {'test': 'herr', 'calculadora': 'herr', 'curso': 'herr', 'libro': 'libro', 'lectura': 'libro', 'creativo': 'creativo',
         'notas': 'notas', 'seccion': 'seccion', 'frase': 'frase'}


def planificar(dias=14):
    cat = {p['id']: p for p in leer('catalogo.json')['productos']}
    est = leer('estado.json', {'calendario': {}, 'historial': {}})
    cal, hist = est['calendario'], est['historial']
    # quitar del calendario futuro lo que ya no existe
    for f in list(cal):
        if f < (HOY - datetime.timedelta(days=60)).isoformat(): del cal[f]
    ultimo = collections.defaultdict(dict)  # red -> id -> fecha
    for r, h in hist.items():
        for f, i in h: ultimo[r][i] = max(ultimo[r].get(i, ''), f)
    for f, franjas in sorted(cal.items()):
        for fr, por_red in franjas.items():
            for r, i in por_red.items():
                r = r + '-video' if fr in VID else r
                ultimo[r][i] = max(ultimo[r].get(i, ''), f)
    for d in range(dias):
        f = (HOY + datetime.timedelta(days=d)).isoformat()
        pass  # cada franja se completa abajo si falta
        dia = cal.setdefault(f, {})
        for fr in ('1', '2', '3', '4', '5', '6'):
            if fr in dia and all(i in cat for i in dia[fr].values()) and set(dia[fr]) >= set(redes_de(fr) if fr in VID else [x for x in REDES if not (x == 'pinterest' and fr == '1')]): continue
            grupo = 'herr' if fr == '1' else 'frase' if fr == '3' else 'video' if fr in ('4', '6') else 'video5' if fr == '5' else TARDE[datetime.date.fromisoformat(f).toordinal() % len(TARDE)]
            usados = set(); dia[fr] = {}
            for r0 in (redes_de(fr) if fr in VID else REDES):
                if r0 == 'pinterest' and fr == '1': continue
                r = r0 + '-video' if fr in VID else r0
                if grupo == 'video':
                    cand = [p for p in cat.values() if p['tipo'] in TIPOS_VIDEO and p['id'] not in usados and p['id'] not in dia.get('5', {}).values() and p['id'] not in dia.get('4' if fr == '6' else '6', {}).values()]
                elif grupo == 'video5':
                    cand = [p for p in cat.values() if p['tipo'] in ('frase', 'curiosidad') and p['id'] not in usados and p['id'] not in dia.get('4', {}).values()]
                else:
                    cand = [p for p in cat.values() if GRUPO.get(p['tipo']) == grupo and p['id'] not in usados]
                if r in ('instagram', 'pinterest'): cand = [p for p in cand if p['tipo'] != 'notas' or True]
                if not cand: cand = [p for p in cat.values() if p['id'] not in usados]
                # nuevos primero (alta en los últimos 14 días y nunca publicados en esa red), luego el que lleva más sin salir
                nuevo = lambda p: p.get('alta', '') >= (HOY - datetime.timedelta(days=14)).isoformat() and p['id'] not in ultimo[r]
                desempate = lambda p: hashlib.md5((r + p['id']).encode()).hexdigest()
                # aprende de los clics: lo que más clics trajo vuelve antes (hasta 3 semanas antes que el resto)
                def antig(p):
                    u = ultimo[r].get(p['id'], '')
                    if not u: return ''
                    return (datetime.date.fromisoformat(u[:10]) - datetime.timedelta(days=min(21, 3 * EXITO.get(p['id'], 0)))).isoformat()
                p = min(cand, key=lambda p: (not nuevo(p), antig(p), -EXITO.get(p['id'], 0), desempate(p)))
                dia[fr][r0] = p['id']; usados.add(p['id']); ultimo[r][p['id']] = f
    guardar('estado.json', est)
    # tarjetas que faltan y enlaces cortos
    necesarios = {i for f, fr in cal.items() if f >= HOY.isoformat() for k, x in fr.items() if k not in VID for i in x.values()}
    lista = []
    os.makedirs(os.path.join(D, 'img', 'auto'), exist_ok=True)
    fotos = leer('fotos.json', {}); usadas = {str(f['pid']) for f in fotos.values()}
    for i in sorted(necesarios):
        p = cat[i]
        if p.get('img'): continue
        foto = foto_para(p, fotos, usadas)
        sal = os.path.join(D, imagen_de(p, fotos))
        if os.path.exists(sal): continue
        kick = {'test': 'Test gratis', 'calculadora': 'Calculadora gratis', 'curso': 'Curso gratis', 'libro': 'Libro gratis · licencia abierta',
                'notas': 'Notas de corte 2025-2026', 'seccion': 'Gratis en AURZANE', 'lectura': 'Libro recomendado'}.get(p['tipo'], 'AURZANE')
        sub = (f"{p.get('autor')} · {p.get('paginas')} páginas · {p.get('licencia')}" if p['tipo'] == 'libro' else p.get('autor', '') if p['tipo'] == 'lectura'
               else recorta(p['texto'], 150))
        if p['tipo'] == 'frase':
            lista.append(dict(id=i, mundo=p['mundo'], frase=p['titulo'], autor='' if p['autor'] == 'AURZANE' else p['autor'], salida=sal,
                              foto=foto['src'] if foto else '', credito='Foto: Pexels' if foto else ''))
            continue
        lista.append(dict(id=i, mundo=p['mundo'], kicker=kick, titulo=p['titulo'] if p['tipo'] in ('libro', 'lectura') else p['ganchos'][0],
                          sub=sub, pie=pie_de(p['url']), emoji='' if foto else p.get('emoji', ''), salida=sal,
                          foto=foto['src'] if foto else '', credito='Foto: Pexels' if foto else ''))
    guardar('fotos.json', fotos)
    json.dump(lista, open('/tmp/tarjetas.json', 'w'), ensure_ascii=False)
    print('Tarjetas por generar:', len(lista))
    enlaces()


def pie_de(u):
    h, _, ruta = re.sub(r'^https?://', '', u).partition('/')
    seg = re.sub(r'\?.*$|\.html$', '', ruta.split('/')[0])
    return h + ('/' + seg if seg else '')


# ------------------------------------------------------------------ fotos de Pexels (licencia libre, uso comercial permitido)
FOTO_Q = {
 'test-personalidad': 'person thinking window light', 'test-ansiedad': 'calm woman breathing nature', 'test-depresion': 'person rainy window',
 'test-autoestima': 'confident woman portrait smile', 'test-tdah': 'busy desk sticky notes', 'test-autocompasion': 'hands holding warm light',
 'test-satisfaccion': 'happy person sunset field', 'test-bienestar': 'morning sunlight coffee calm', 'test-sueno': 'cozy bed sleeping',
 'test-habitos': 'healthy breakfast fruit', 'calc-calorias': 'healthy meal plate vegetables', 'calc-embarazo': 'pregnant woman sunlight',
 'calc-hipoteca': 'house keys new home', 'calc-sueldo': 'calculator coins desk', 'calc-reforma': 'apartment renovation interior',
 'calc-pau': 'student studying exam desk', 'notas-corte': 'university students campus', 'universidades': 'university building campus',
 'ovp': 'young student thinking future', 'biblioteca': 'library bookshelves', 'articulos': 'reading tablet coffee',
 'curso-neuro': 'brain anatomy model', 'curso-metod': 'scientist microscope laboratory', 'biblio-mind': 'psychology books',
 'biblio-live': 'wellness nature yoga', 'biblio-nexus': 'technology data network', 'biblio-learn': 'students learning classroom',
 'biblio-build': 'ancient architecture columns',
}
NC_Q = {'medicina': 'medical students stethoscope', 'enfermer': 'nurse hospital', 'psicolog': 'therapy session', 'derecho': 'law books',
        'ingenier': 'engineering blueprint', 'odontolog': 'dentist clinic', 'biolog': 'biology laboratory', 'fisioterap': 'physiotherapy',
        'farmacia': 'pharmacy', 'veterinar': 'veterinarian dog', 'arquitect': 'architecture model', 'magisterio': 'teacher classroom children',
        'educaci': 'teacher classroom', 'econom': 'economics charts', 'empresa': 'business meeting', 'periodis': 'journalist microphone',
        'química': 'chemistry lab', 'matem': 'mathematics blackboard', 'física': 'physics experiment', 'historia': 'historical archive',
        'informática': 'programmer code screen', 'datos': 'data analysis screen', 'deporte': 'athletics track', 'turismo': 'travel tourism'}
LIBRO_Q = [('duelo', 'grief candle'), ('sueño', 'sleep night'), ('infantil', 'child playing parent'), ('aprendizaje', 'student reading notes'),
           ('neuro', 'brain illustration'), ('trauma', 'resilience sunrise'), ('mindfulness', 'meditation'), ('filosof', 'philosophy statue'),
           ('adicci', 'recovery support group'), ('laboral', 'office team'), ('deport', 'athlete training'), ('emoci', 'emotions face portrait'),
           ('social', 'friends talking'), ('personalidad', 'portrait thoughtful'), ('salud', 'health wellbeing'), ('clínica', 'therapist office'),
           ('vocacional', 'career path'), ('sexualidad', 'couple holding hands'), ('jurídica', 'courthouse'), ('música', 'music instrument'),
           ('lenguaje', 'conversation'), ('desarrollo', 'family generations'), ('investigaci', 'research papers'), ('historia', 'old books')]


def consulta_foto(p):
    if p.get('foto_q'): return p['foto_q']
    if p['id'] in FOTO_Q: return FOTO_Q[p['id']]
    if p['tipo'] == 'notas':
        t = p['titulo'].lower()
        return next((q for k, q in NC_Q.items() if k in t), 'university lecture hall')
    if p['tipo'] in ('libro', 'lectura'):
        t = (' '.join(p.get('hashtags', [])) + ' ' + p['titulo']).lower()
        return next((q for k, q in LIBRO_Q if k in t), 'open book reading')
    return {'test': 'person reflecting', 'calculadora': 'desk planning notebook'}.get(p['tipo'], 'books learning')


def foto_para(p, fotos, usadas):
    """Foto de Pexels (licencia Pexels: uso comercial gratis, sin atribución obligatoria) para el producto.
    Sale de biblioteca_fotos.json (fotos elegidas por tema en pexels.com); se guarda en fotos.json para no cambiarla."""
    if p['id'] in fotos: return fotos[p['id']]
    lib = leer('biblioteca_fotos.json', {})
    q = consulta_foto(p)
    ids = lib.get(q) or lib.get('open book reading') or []
    libres = [i for i in ids if i.split('.')[0] not in usadas] or ids
    if not libres: return None
    sel = libres[int(hashlib.md5(p['id'].encode()).hexdigest(), 16) % len(libres)]
    pid, _, ext = sel.partition('.')
    ext = ext or 'jpeg'
    fotos[p['id']] = {'pid': pid, 'q': q, 'autor': 'Pexels', 'url': f'https://www.pexels.com/photo/{pid}/',
                      'src': f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.{ext}?auto=compress&cs=tinysrgb&w=1080&h=1350&fit=crop'}
    usadas.add(pid)
    return fotos[p['id']]


def codigo(r, i):
    return hashlib.sha1(f'{r}:{i}'.encode()).hexdigest()[:6]


def enlaces():
    cat = {p['id']: p for p in leer('catalogo.json')['productos']}
    mapa = {}
    for r in sorted(set(REDES) | set(REDES_VIDEO)):
        for i, p in cat.items():
            sep = '&' if '?' in p['url'] else '?'
            mapa[codigo(r, i)] = p['url'] + f'{sep}utm_source={r}&utm_medium=social&utm_campaign={p["tipo"]}'
    os.makedirs(os.path.join(D, 'salida', 'ir'), exist_ok=True)
    json.dump(mapa, open(os.path.join(D, 'salida', 'ir', 'mapa.json'), 'w'), separators=(',', ':'))


def imagen_de(p, fotos=None):
    if p.get('img'): return p['img']
    fotos = leer('fotos.json', {}) if fotos is None else fotos
    return f'img/auto/{p["id"]}' + ('-f' if p['id'] in fotos else '') + '-s.jpg'   # -s: sin la dirección web en el pie (va en la descripción)


def feed():
    """RSS con imagen para Pinterest (pinea solo desde el feed) y lectores RSS."""
    cat = {p['id']: p for p in leer('catalogo.json')['productos']}
    est = leer('estado.json')
    items = []
    for f, fr in sorted(est['calendario'].items(), reverse=True):
        if f > HOY.isoformat(): continue
        for k in ('3', '2'):
            i = fr.get(k, {}).get('pinterest')
            if i and i in cat: items.append((f, cat[i]))
        if len(items) >= 60: break
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>',
         '<title>AURZANE: tests, calculadoras y libros gratis</title><link>https://aurzane.com/</link>',
         '<description>Lo nuevo de AURZANE cada día: tests psicológicos, calculadoras y libros de psicología gratis.</description><language>es</language>']
    for f, p in items:
        img = SITIO_IMG + imagen_de(p)
        d = datetime.datetime.combine(datetime.date.fromisoformat(f), datetime.time(17, 0)).strftime('%a, %d %b %Y %H:%M:%S +0000')
        if p['tipo'] == 'frase':
            x.append(f'<item><title>{html.escape(p["titulo"])}</title><link>{IR}{codigo("pinterest", p["id"])}</link>'
                     f'<guid isPermaLink="false">{f}-{p["id"]}</guid><pubDate>{d}</pubDate>'
                     f'<description>{html.escape(p["titulo"] + " Más recursos gratis para tu bienestar en AURZANE.")}</description>'
                     f'<enclosure url="{img}" type="image/jpeg" length="0"/><media:content url="{img}" medium="image"/></item>')
            continue
        x.append(f'<item><title>{html.escape(p["ganchos"][0])}</title><link>{IR}{codigo("pinterest", p["id"])}</link>'
                 f'<guid isPermaLink="false">{f}-{p["id"]}</guid><pubDate>{d}</pubDate>'
                 f'<description>{html.escape(p["texto"])}</description><enclosure url="{img}" type="image/jpeg" length="0"/>'
                 f'<media:content url="{img}" medium="image"/></item>')
    x.append('</channel></rss>')
    os.makedirs(os.path.join(D, 'salida'), exist_ok=True)
    open(os.path.join(D, 'salida', 'feed.xml'), 'w', encoding='utf-8').write('\n'.join(x))


# ------------------------------------------------------------------ textos por red
PREGUNTAS = ['¿Qué te dice esta frase hoy?', 'Guárdala para cuando la necesites.', 'Compártela con alguien que la necesite hoy.',
             '¿Con qué parte te quedas?', 'Escríbela donde la veas cada mañana.', 'Etiqueta a quien te recuerda esto.']


def texto_frase(r, p, n):
    t = p['titulo'] + ('' if p['autor'] == 'AURZANE' else f"\n\n{p['autor']}")
    q = PREGUNTAS[(int(p['id'][-4:], 16) + n) % len(PREGUNTAS)]
    if p.get('libro'): q += f"\n\n📖 Del libro «{p['libro'][:90]}», gratis en la Biblioteca AURZANE."
    url = IR + codigo(r, p['id'])
    if r == 'instagram':
        tags = ' '.join('#' + h for h in p['hashtags'] + ['AURZANE', 'PsicologíaPositiva', 'Autoestima', 'Resiliencia'])
        return f'{t}\n\n{q}\n\n🧠 Tests de bienestar y lecturas de psicología gratis en aurzane.com (enlace en la bio).\n\n{tags}'
    if r == 'telegram':
        return f'<b>{html.escape(p["titulo"])}</b>' + ('' if p['autor'] == 'AURZANE' else f'\n<i>{html.escape(p["autor"])}</i>') + f'\n\n{q}\n\n🧠 Más para tu bienestar: {url}'
    if r == 'bluesky':
        s_ = f'{t}\n\n{q}\n\n{url} #FrasesMotivadoras'
        return s_ if len(s_) <= 300 else f'{t}\n\n{url}'[:300]
    if r == 'facebook':
        return f'{t}\n\n{q}\n\nTests de bienestar y lecturas de psicología gratis 👉 {url}'
    return f'{t}\n\n{q}\n\n{url}\n\n#FrasesMotivadoras #Superación #SaludMental #Psicología'


def texto(r, p, n):
    if p['tipo'] == 'frase': return texto_frase(r, p, n)
    g = p['ganchos'][n % len(p['ganchos'])]
    url = IR + codigo(r, p['id'])
    tags = ' '.join('#' + h for h in p.get('hashtags', [])[:4])
    av = p.get('aviso', '')
    tx = p['texto']
    if p['tipo'] == 'libro': tx = f"{p['texto']}\n\n{p.get('paginas')} páginas · {p.get('licencia')} · lectura directa y gratis"
    if r == 'telegram':
        return f'<b>{html.escape(g)}</b>\n\n{html.escape(tx)}' + (f'\n\n<i>{html.escape(av)}</i>' if av else '') + f'\n\n👉 {url}'
    if r in ('bluesky', 'x'):
        lim = 300 if r == 'bluesky' else 280
        base = f'{g}\n\n'; cola = f'\n\n{url}'
        t2 = tags.split(' ')[0] if tags else ''
        if p['tipo'] == 'test': cola = '\n\nNo es un diagnóstico.' + cola
        cuerpo = recorta(p['texto'], lim - len(base) - len(cola) - len(t2) - 8 - (23 - len(url) if r == 'x' else 0))
        return f'{base}{cuerpo}{cola} {t2}'.strip()
    if r in ('mastodon', 'threads'):
        s = f'{g}\n\n{tx}' + (f'\n\n{av}' if av else '') + f'\n\n{url}\n\n{tags}'
        return s if len(s) <= 500 else f'{g}\n\n{recorta(p["texto"], 500 - len(g) - len(url) - len(tags) - 12)}\n\n{url}\n\n{tags}'
    if r == 'facebook':
        return f'{g}\n\n{tx}' + (f'\n\n{av}' if av else '') + f'\n\n👉 {url}'
    if r == 'instagram':
        dom = re.sub(r'^https?://|/$|\?.*$', '', p['url'])
        mas = ' '.join('#' + h for h in (p.get('hashtags', []) + ['AURZANE', 'Gratis'])[:8])
        return f'{g}\n\n{tx}' + (f'\n\n{av}' if av else '') + f'\n\n🔗 Enlace en la bio o en {dom}\n\n{mas}'
    return f'{g}\n\n{tx}\n\n{url}'


# ------------------------------------------------------------------ publicación
def bloqueada(r):
    """Meta (Instagram y Facebook) puede bloquear el acceso a la API. Si los 2 últimos intentos de esa red fallaron por bloqueo,
    se pausa el resto del día para no insistir (insistir empeora la revisión de Meta); al día siguiente se prueba una vez."""
    try: L = [l.split(',') for l in open(os.path.join(D, 'registro.csv'), encoding='utf-8') if f',{r},' in l][-2:]
    except Exception: return False
    # TikTok: con la app sin auditar los vídeos llegan como borradores a la bandeja; si hay demasiados sin publicar
    # responde spam_risk_too_many_pending_share. Se espera al día siguiente en vez de reintentar cada hora.
    if r == 'tiktok' and any(x[0] == HOY.isoformat() and 'spam_risk' in ','.join(x) for x in L): return True
    return len(L) == 2 and all('access blocked' in ','.join(x).lower() or 'temporarily blocked' in ','.join(x).lower() for x in L) and L[-1][0] == HOY.isoformat()


def publicar_video(franja='4'):
    import redes
    cat = {p['id']: p for p in leer('catalogo.json')['productos']}
    est = leer('estado.json'); hoy = HOY.isoformat()
    plan = est['calendario'].get(hoy, {}).get(franja, {})
    hist = est.setdefault('historial', {})
    reg = open(os.path.join(D, 'registro.csv'), 'a', encoding='utf-8')
    for n, r in enumerate(REDES_VIDEO):
        i = plan.get(r); h = r + '-video'
        if not i or i not in cat or not redes.configurada(r): continue
        if bloqueada(r): print('Pausada (bloqueo de Meta):', r); continue
        if any(f == hoy and x == i for f, x in hist.get(h, [])): continue
        p = cat[i]
        import video as _v
        url = SITIO_IMG + f'video/{_v.V}{i}.mp4'
        local = os.path.join(D, 'salida', 'video', _v.V + i + '.mp4')
        try:
            if not os.path.exists(local):
                os.makedirs(os.path.dirname(local), exist_ok=True); urllib.request.urlretrieve(url, local)
            tx = texto(r if r in REDES else 'mastodon', p, n + 4) + f'\n\n🎵 {_v.credito(p)}'
            ref = redes.publicar_video(r, tx, url, local, IR + codigo(r, i), p)
            hist.setdefault(h, []).append([hoy, i]); reg.write(f'{hoy},{franja},{r},{i},ok,{ref}\n'); print('OK vídeo', r, i, ref)
        except Exception as e:
            reg.write(f'{hoy},{franja},{r},{i},error,{str(e)[:150].replace(",", " ")}\n'); print('ERROR vídeo', r, i, e)
    guardar('estado.json', est)


HORAS = {'1': (8, 37), '5': (10, 47), '3': (12, 13), '6': (15, 23), '2': (17, 41), '4': (19, 29)}  # UTC


def _exito():
    """Clics de los últimos 60 días por producto (marketing/clics.csv): el plan da más salida a lo que funciona."""
    out = collections.Counter()
    try:
        lim = (HOY - datetime.timedelta(days=60)).isoformat()
        for f in csv.DictReader(open(os.path.join(D, 'clics.csv'), encoding='utf-8')):
            if f.get('fecha', '') >= lim: out[f['producto']] += int(f.get('clics') or 0)
    except Exception: pass
    return out
EXITO = _exito()


def pendientes():
    """Publica las franjas de hoy cuya hora ya pasó y aún no salieron (por si GitHub retrasa o salta un cron)."""
    ahora = datetime.datetime.now(datetime.timezone.utc)
    for fr, (h, m) in sorted(HORAS.items(), key=lambda x: x[1]):
        if (ahora.hour, ahora.minute) >= (h, m):
            print('Franja', fr); publicar(fr)


def publicar(franja):
    if franja in VID: return publicar_video(franja)
    import redes
    cat = {p['id']: p for p in leer('catalogo.json')['productos']}
    est = leer('estado.json')
    hoy = HOY.isoformat()
    plan = est['calendario'].get(hoy, {}).get(franja, {})
    hist = est.setdefault('historial', {})
    reg = open(os.path.join(D, 'registro.csv'), 'a', encoding='utf-8')
    for n, r in enumerate(REDES):
        i = plan.get(r)
        if not i or i not in cat: continue
        if any(f == hoy and x == i for f, x in hist.get(r, [])): continue
        if r == 'pinterest':  # sale solo en el feed
            hist.setdefault(r, []).append([hoy, i]); reg.write(f'{hoy},{franja},{r},{i},feed,\n'); continue
        if not redes.configurada(r): continue
        if bloqueada(r): print('Pausada (bloqueo de Meta):', r); continue
        p = cat[i]
        img_url = SITIO_IMG + imagen_de(p)
        img_local = os.path.join(D, imagen_de(p))
        if not os.path.exists(img_local):   # si aurzane.com tarda, se reintenta y, si no, se salta esta red sin tumbar las demás
            os.makedirs(os.path.dirname(img_local), exist_ok=True)
            for k_ in range(3):
                try: urllib.request.urlretrieve(img_url, img_local); break
                except Exception as e_img: print('imagen no disponible', i, e_img); time.sleep(10)
            if not os.path.exists(img_local):
                reg.write(f'{hoy},{franja},{r},{i},error,imagen no disponible\n'); continue
        try:
            if r in ('instagram', 'facebook'):   # Reel con música si ya está preparado en aurzane.com (video.generar_imagenes)
                import video as _v
                vurl = SITIO_IMG + f'video/{_v.V}img-{i}.mp4'; vlocal = os.path.join(D, 'salida', 'video', f'{_v.V}img-{i}.mp4')
                try:
                    urllib.request.urlopen(urllib.request.Request(vurl, method='HEAD'), timeout=20)
                    if not os.path.exists(vlocal): os.makedirs(os.path.dirname(vlocal), exist_ok=True); urllib.request.urlretrieve(vurl, vlocal)
                    cred = _v.mk.leer('musica_usada.json', {}).get('img-' + i, '')
                    ref = redes.publicar_video(r, texto(r, p, n + int(franja)) + (f'\n\n🎵 {cred}' if cred else ''), vurl, vlocal, IR + codigo(r, i), p)
                    hist.setdefault(r, []).append([hoy, i]); reg.write(f'{hoy},{franja},{r},{i},ok,{ref}\n'); print('OK reel', r, i, ref); continue
                except Exception as e_:
                    print('Reel no disponible, sale como imagen', r, i, str(e_)[:120])
            ref = redes.publicar(r, texto(r, p, n + int(franja)), img_url, img_local, IR + codigo(r, i), p)
            hist.setdefault(r, []).append([hoy, i]); reg.write(f'{hoy},{franja},{r},{i},ok,{ref}\n'); print('OK', r, i, ref)
        except Exception as e:
            reg.write(f'{hoy},{franja},{r},{i},error,{str(e)[:150].replace(",", " ")}\n'); print('ERROR', r, i, e)
    for r in hist: hist[r] = hist[r][-800:]
    guardar('estado.json', est)
    feed()


def clics(log):
    cat = leer('catalogo.json')['productos']
    inv = {codigo(r, p['id']): (r, p['id']) for r in REDES for p in cat}
    cuenta = collections.Counter()
    for l in open(log, encoding='utf-8', errors='replace'):
        c = l.rstrip('\n').split('\t')
        if len(c) >= 3 and c[2] == 'h' and c[1] in inv: cuenta[(c[0][:10],) + inv[c[1]]] += 1
    with open(os.path.join(D, 'clics.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(['fecha', 'red', 'producto', 'clics'])
        for k, v in sorted(cuenta.items()): w.writerow(list(k) + [v])
    por_red = collections.Counter(); por_prod = collections.Counter()
    for (f, r, i), v in cuenta.items(): por_red[r] += v; por_prod[i] += v
    pub = collections.Counter(l.split(',')[2] for l in open(os.path.join(D, 'registro.csv'), encoding='utf-8') if ',ok,' in l or ',feed,' in l) if os.path.exists(os.path.join(D, 'registro.csv')) else {}
    md = ['# Informe de marketing', '', f'Actualizado: {HOY.isoformat()}. Clics de personas (sin bots ni vistas previas) que entraron por los enlaces de las publicaciones.', '',
          '| Red | Publicaciones | Clics |', '|---|---|---|']
    md += [f'| {r} | {pub.get(r, 0)} | {por_red.get(r, 0)} |' for r in REDES]
    md += ['', '## Productos con más clics', '', '| Producto | Clics |', '|---|---|']
    md += [f'| {i} | {v} |' for i, v in por_prod.most_common(25)]
    open(os.path.join(D, 'INFORME.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('Clics:', sum(cuenta.values()))


if __name__ == '__main__':
    sys.path.insert(0, D)
    a = sys.argv[1]
    if a == 'catalogo': catalogo()
    elif a == 'planificar': planificar(); feed()
    elif a == 'publicar': publicar(sys.argv[2])
    elif a == 'pendientes': pendientes()
    elif a == 'clics': clics(sys.argv[2])
    elif a == 'renovar-ig':
        import redes; print(redes.renovar_instagram())
    elif a == 'perfiles':
        import redes
        for r, v in redes.perfiles().items(): print(f'{r}: {v}')
    elif a == 'verificar':
        import redes; out = redes.verificar() or {}
        # se guarda para que la IA sepa que una red ya funciona aunque las últimas publicaciones fallaran
        json.dump({'fecha': datetime.datetime.utcnow().isoformat(timespec='minutes'), 'redes': {k: str(v)[:160] for k, v in out.items()}},
                  open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verificacion.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    elif a == 'seguidores':
        import redes; hoy = datetime.date.today().isoformat()
        f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seguidores.json')
        h = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {}
        h[hoy] = {k: v for k, v in redes.seguidores().items()}
        h = dict(sorted(h.items())[-400:])
        json.dump(h, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('Seguidores', h[hoy])
    elif a == 'muestra':
        cat = {p['id']: p for p in leer('catalogo.json')['productos']}
        p = cat[sys.argv[2]]
        for n, r in enumerate(REDES): print(f'===== {r} ({len(texto(r, p, n))})\n{texto(r, p, n)}\n')


# ------------------------------------------------------------------ IndexNow (Bing, Yandex, Seznam, Naver): aviso inmediato de páginas nuevas
def indexnow():
    clave = open(os.path.join(D, 'indexnow.key')).read().strip()
    enviados = set(leer('indexnow.json', []))
    urls = set()
    for sm in ['https://aurzane.com/sitemap.xml', 'https://aurzane.com/sitemap-biblioteca.xml', 'https://nexus.aurzane.com/sitemap-universidades.xml']:
        try: urls |= set(re.findall(r'<loc>([^<]+)</loc>', get(sm)))
        except Exception as e: print('Sitemap', sm, e)
    nuevos = sorted(urls - enviados)
    por_host = collections.defaultdict(list)
    for u in nuevos: por_host[urllib.parse.urlparse(u).netloc].append(u)
    for h, lista in por_host.items():
        for k in range(0, len(lista), 9000):
            cuerpo = json.dumps({'host': h, 'key': clave, 'urlList': lista[k:k + 9000]}).encode()
            req = urllib.request.Request('https://api.indexnow.org/indexnow', data=cuerpo, headers={'Content-Type': 'application/json; charset=utf-8'})
            try:
                cod = urllib.request.urlopen(req, timeout=60).status
            except urllib.error.HTTPError as e:
                cod = e.code
            print('IndexNow', h, len(lista[k:k + 9000]), cod)
            if cod in (200, 202): enviados |= set(lista[k:k + 9000])
    guardar('indexnow.json', sorted(enviados))


if __name__ == '__main__' and sys.argv[1] == 'indexnow':
    indexnow()
