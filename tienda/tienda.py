"""Tienda de libros de AURZANE (aurzane.com/libros/), con enlaces de afiliado de Amazon.

Cada semana:
  1. Comprueba en Google Books cada libro de la semilla (título y autor reales, portada, ISBN). Si no aparece, no se publica.
  2. Lee lo que más se busca en España (tendencias públicas de Google) y la IA propone libros reales relacionados
     o propios de la temporada. También rellena las secciones con menos libros, para que la tienda crezca variada.
     Todo pasa por la misma comprobación en Google Books antes de entrar.
  3. Genera la página de la tienda y libros.json (lo usan los tests y artículos para recomendar libros del tema).
No se copia nada de Amazon (sus normas de afiliados lo prohíben): los enlaces son búsquedas por ISBN con la etiqueta.
"""
import json, os, re, sys, time, html, datetime, unicodedata, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', '/tmp/tienda')
TAG = 'z5464099v-21'
HOY = datetime.date.today().isoformat()
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][datetime.date.today().month - 1]
os.makedirs(OUT, exist_ok=True)


def get(url, datos=None, cab=None, t=40):
    err = ''
    for i in range(2):
        try:
            rq = urllib.request.Request(url, data=datos, headers={'User-Agent': 'AURZANE-tienda/1.0', **(cab or {})})
            with urllib.request.urlopen(rq, timeout=t) as r: return r.status, r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code in (429, 503): err = f'HTTP {e.code}'; time.sleep(3); continue
            return e.code, e.read().decode('utf-8', 'replace')
        except Exception as e:
            err = str(e); time.sleep(3)
    return 0, err


def norm(t):
    t = unicodedata.normalize('NFD', str(t or '').lower())
    return re.sub(r'[^a-z0-9 ]', ' ', ''.join(c for c in t if unicodedata.category(c) != 'Mn')).split()


def slug(t): return '-'.join(norm(t))[:70]


def verificar(titulo, autor):
    """Busca el libro en Open Library y, si no, en Google Books; devuelve sus datos si el título y el autor coinciden de verdad."""
    ape = [w for w in norm(autor) if len(w) > 3 and w not in ('y', 'and')]
    pal = [w for w in norm(titulo) if len(w) > 2][:4]
    v = verificar_ol(titulo, autor, pal, ape)
    if v and v.get('portada'): return v
    g = verificar_gb(titulo, autor, pal, ape)
    if g and not g.get('portada') and v: g['portada'] = v['portada']
    return g or v


def verificar_gb(titulo, autor, pal, ape):
    for lang in ('&langRestrict=es', ''):
        q = urllib.parse.quote(f'intitle:{titulo} inauthor:{" ".join(ape[-1:]) or autor}')
        st, b = get(f'https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=8&printType=books{lang}')
        if st != 200: continue
        for it in (json.loads(b).get('items') or []):
            v = it.get('volumeInfo', {})
            tv = set(norm(v.get('title', '') + ' ' + v.get('subtitle', '')))
            av = set(norm(' '.join(v.get('authors', []))))
            if not pal or not all(w in tv for w in pal[:3]) or (ape and not any(a in av for a in ape)): continue
            isbn = {x.get('type'): x.get('identifier') for x in v.get('industryIdentifiers', [])}
            img = (v.get('imageLinks') or {}).get('thumbnail', '')
            return {'isbn': isbn.get('ISBN_13') or isbn.get('ISBN_10') or '', 'portada': img.replace('http://', 'https://').replace('&edge=curl', ''),
                    'anio': (v.get('publishedDate') or '')[:4], 'editorial': v.get('publisher', ''), 'idioma': v.get('language', ''),
                    'resumen': re.sub(r'<[^>]+>', ' ', v.get('description', '') or '')[:420].strip()}
        time.sleep(1)
    return None


def verificar_ol(titulo, autor, pal, ape):
    """Respaldo: Open Library (si Google Books limita las consultas)."""
    st, b = get('https://openlibrary.org/search.json?' + urllib.parse.urlencode({'title': titulo, 'author': autor, 'limit': 8, 'fields': 'title,author_name,isbn,cover_i,first_publish_year,publisher,language'}))
    if st != 200: return None
    for v in json.loads(b).get('docs', []):
        tv, av = set(norm(v.get('title', ''))), set(norm(' '.join(v.get('author_name', []))))
        if not pal or not all(w in tv for w in pal[:3]) or (ape and not any(a in av for a in ape)): continue
        isbns = v.get('isbn') or []
        isbn = next((i for i in isbns if len(i) == 13 and i.startswith(('97884', '97884', '97898', '97895', '97896', '97897'))), '') or next((i for i in isbns if len(i) == 13), '')
        return {'isbn': isbn, 'portada': f'https://covers.openlibrary.org/b/id/{v["cover_i"]}-M.jpg?default=false' if v.get('cover_i') else '',
                'anio': str(v.get('first_publish_year', '')), 'editorial': (v.get('publisher') or [''])[0], 'idioma': 'spa' if 'spa' in (v.get('language') or []) else '', 'resumen': ''}
    return None


def ia(prompt):
    """Gemini y, si agota su cupo, los modelos gratuitos de GitHub."""
    k = os.environ.get('GEMINI_API_KEY', '')
    for m in ('gemini-flash-latest', 'gemini-flash-lite-latest'):
        if not k: break
        st, b = get(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}',
                    json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.4, 'responseMimeType': 'application/json'}}).encode(),
                    {'Content-Type': 'application/json'}, 90)
        if st == 200:
            try: return json.loads(b)['candidates'][0]['content']['parts'][0]['text']
            except Exception: pass
    tk = os.environ.get('GITHUB_TOKEN', '')
    for m in ('openai/gpt-4.1-mini', 'openai/gpt-4o-mini'):
        if not tk: break
        st, b = get('https://models.github.ai/inference/chat/completions', json.dumps({'model': m, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.4}).encode(),
                    {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tk}, 90)
        if st == 200:
            try: return json.loads(b)['choices'][0]['message']['content']
            except Exception: pass
    return ''


def leer(n, d):
    try: return json.load(open(os.path.join(D, n), encoding='utf-8'))
    except Exception: return d


semilla = leer('semilla.json', {})
SECC = semilla['secciones']
cat = {x['id']: x for x in leer('catalogo.json', [])}
descartes = set(leer('descartes.json', []))
nuevos = []

# 1) semilla
INICIO = time.time()
pendientes_s = [l for l in semilla['libros'] if slug(l['titulo'] + ' ' + l['autor']) not in cat]
for l in pendientes_s[:25]:
    i = slug(l['titulo'] + ' ' + l['autor'])
    v = verificar(l['titulo'], l['autor']); time.sleep(0.4)
    if not v: print('sin verificar (se reintenta en la próxima pasada):', l['titulo']); continue
    cat[i] = {'id': i, 'titulo': l['titulo'], 'autor': l['autor'], 'temas': l['temas'], 'origen': 'semilla', 'fecha': HOY, **v}; nuevos.append(i)

# 2) tendencias de búsqueda + secciones con pocos libros
tend = []
st, b = get('https://trends.google.com/trending/rss?geo=ES')
if st == 200:
    try: tend = [x.text for x in ET.fromstring(b.encode()).iter('title')][1:31]
    except Exception as e: print('tendencias', e)
print('tendencias:', len(tend))
cuenta = {}
for x in cat.values():
    for t in x['temas']: cuenta[SECC.get(t, t)] = cuenta.get(SECC.get(t, t), 0) + 1
flojas = sorted(set(SECC.values()), key=lambda s: cuenta.get(s, 0))[:4]
ya = '; '.join(f'{x["titulo"]} ({x["autor"]})' for x in list(cat.values())[:150])
r = ia(f'Eres el librero de AURZANE, una web española de psicología y bienestar que también vende libros variados con enlace de Amazon. Estamos en {MES}.\n'
       f'Lo que más se busca hoy en Google España: {"; ".join(tend) or "(no disponible)"}.\n'
       f'Propón libros REALES (título y autor exactos, publicados y a la venta en español) para dos listas:\n'
       f'A) "tendencia": hasta 6 libros que alguien que busca esos temas, o en esta época del año (regalos, temporada, efemérides), querría comprar. Ignora tendencias de sucesos trágicos.\n'
       f'B) "crecer": 2 libros muy vendidos o muy recomendados para cada una de estas secciones con pocos libros: {", ".join(flojas)}.\n'
       f'No repitas estos: {ya}.\n'
       f'Claves de tema válidas: {", ".join(SECC)}.\n'
       'Responde solo JSON: {"tendencia":[{"titulo":"","autor":"","temas":["clave"],"motivo":"<por qué ahora, 1 frase corta>"}],"crecer":[{"titulo":"","autor":"","temas":["clave"]}]}')
try: prop = json.loads(re.search(r'\{.*\}', r, re.S).group(0)) if r else {}
except Exception: prop = {}
for tipo in ('tendencia', 'crecer'):
    for l in (prop.get(tipo) or [])[:10]:
        if time.time() - INICIO > 900: break
        if not l.get('titulo') or not l.get('autor'): continue
        i = slug(l['titulo'] + ' ' + l['autor'])
        if i in cat:
            if tipo == 'tendencia': cat[i].update(tendencia=l.get('motivo', ''), tendencia_fecha=HOY)
            continue
        if i in descartes: continue
        v = verificar(l['titulo'], l['autor']); time.sleep(0.6)
        if not v: descartes.add(i); print('la IA propuso uno que no aparece en Google Books:', l['titulo'], '·', l['autor']); continue
        temas = [t for t in (l.get('temas') or []) if t in SECC] or ['ensayo']
        cat[i] = {'id': i, 'titulo': l['titulo'], 'autor': l['autor'], 'temas': temas, 'origen': tipo, 'fecha': HOY, **v}
        if tipo == 'tendencia': cat[i].update(tendencia=l.get('motivo', ''), tendencia_fecha=HOY)
        nuevos.append(i)

# 2b) «por qué lo recomendamos»: un párrafo breve por libro (una sola vez), para la ficha
sin_porque = [x for x in cat.values() if not x.get('porque')][:15]
if sin_porque and time.time() - INICIO < 1100:
    r = ia('Para cada libro escribe 2 frases en español de España, cálidas y concretas, sobre para quién es y qué aporta. '
           'Solo lo que se sabe con seguridad del libro; nada de cifras ni citas inventadas; sin rayas largas. '
           'Responde solo JSON {"<id>": "<texto>"}.\n' + '\n'.join(f'{x["id"]}: {x["titulo"]} de {x["autor"]}. {x.get("resumen", "")[:200]}' for x in sin_porque))
    try:
        pq = json.loads(re.search(r'\{.*\}', r, re.S).group(0)) if r else {}
        for k, v in pq.items():
            if k in cat and isinstance(v, str) and 40 < len(v) < 600: cat[k]['porque'] = v.replace('—', ',').strip()
    except Exception as e: print('porque', e)

# 3) salida
def amazon(x): return 'https://www.amazon.es/s?' + urllib.parse.urlencode({'k': x.get('isbn') or f'{x["titulo"]} {x["autor"]}', 'i': 'stripbooks', 'tag': TAG})

# Secciones de la tienda: una sola clasificación para los libros de pago elegidos y los de la biblioteca
TIENDA_S = {'ansiedad': 'Emociones, ansiedad y estrés', 'estres': 'Emociones, ansiedad y estrés', 'depresion': 'Emociones, ansiedad y estrés', 'burnout': 'Emociones, ansiedad y estrés',
            'emociones': 'Emociones, ansiedad y estrés', 'autoestima': 'Autoestima y desarrollo personal', 'autocompasion': 'Autoestima y desarrollo personal',
            'resiliencia': 'Autoestima y desarrollo personal', 'satisfaccion': 'Autoestima y desarrollo personal', 'bienestar': 'Autoestima y desarrollo personal',
            'habitos': 'Hábitos, salud y productividad', 'productividad': 'Hábitos, salud y productividad', 'autoeficacia': 'Hábitos, salud y productividad',
            'tdah': 'Hábitos, salud y productividad', 'sueno': 'Hábitos, salud y productividad', 'soledad': 'Relaciones y familia', 'relaciones': 'Relaciones y familia',
            'crianza': 'Relaciones y familia', 'personalidad': 'Mente y personalidad', 'duelo': 'Duelo y pérdidas', 'vocacional': 'Estudiar y aprender',
            'finanzas': 'Dinero y vivienda', 'vivienda': 'Dinero y vivienda', 'ciencia': 'Ciencia y tecnología', 'novela': 'Novela y relatos', 'ensayo': 'Ensayo e ideas',
            # macrotemas de la biblioteca
            'mente': 'Mente y personalidad', 'psicologia': 'Mente y personalidad', 'desarrollo': 'Autoestima y desarrollo personal', 'relatos': 'Novela y relatos',
            'desarrollo-humano': 'Relaciones y familia', 'clinica': 'Clínica y salud mental', 'aprendizaje': 'Estudiar y aprender', 'rendimiento': 'Hábitos, salud y productividad',
            'mente-digital': 'Ciencia y tecnología'}
ORDEN_S = list(dict.fromkeys(TIENDA_S.values()))

lista = sorted(cat.values(), key=lambda x: (x.get('tendencia_fecha', ''), x['fecha']), reverse=True)
json.dump(lista, open(os.path.join(D, 'catalogo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(sorted(descartes), open(os.path.join(D, 'descartes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
hace35 = (datetime.date.today() - datetime.timedelta(days=35)).isoformat()
pub = [{'id': x['id'], 't': x['titulo'], 'a': x['autor'], 'temas': x['temas'], 's': TIENDA_S.get(x['temas'][0], 'Ensayo e ideas'), 'img': x.get('portada', ''),
        'u': amazon(x), 'f': f'https://aurzane.com/libros/{x["id"]}/', 'r': (x.get('resumen') or '')[:220], 'y': x.get('anio', ''), 'd': x['fecha'],
        'tend': x.get('tendencia', '') if x.get('tendencia_fecha', '') >= hace35 else ''} for x in lista]
json.dump(pub, open(os.path.join(OUT, 'libros.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
# versión .js para que los tests y artículos de los subdominios la carguen sin problemas de CORS
open(os.path.join(OUT, 'libros.js'), 'w', encoding='utf-8').write('window.__azLibros=' + json.dumps(pub, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')

# catálogo completo de la tienda: los elegidos (de pago) + la biblioteca (gratis para leer aquí, y fichas de libros actuales con Amazon)
todo = [{'t': x['t'], 'a': x['a'], 'img': x['img'], 'f': x['f'], 'c': x['u'], 'p': 'p', 's': x['s'], 'd': x['d'], 'tend': x['tend'], 'y': x['y'], 'top': 1} for x in pub]
clave = lambda t: ' '.join([w for w in norm(t) if len(w) > 2][:3])
vistos = {clave(x['t']) for x in todo}
st, js = get('https://aurzane.com/biblioteca/catalogo.js', t=90)
n_gratis = n_ref = 0
if st == 200:
    try:
        B = json.loads(js[js.index('{'):js.rstrip().rstrip(';').rindex('}') + 1])
        macro = {}
        for m in B['macrotemas']:
            for t in m['temas']: macro[str(t)] = m['id']
        for l in B['libros']:
            k = clave(l['titulo'])
            if k in vistos: continue
            vistos.add(k)
            aut = (l.get('autores') or '').split(';')[0].strip()
            if ',' in aut and aut.count(',') == 1: a_, b_ = aut.split(','); aut = f'{b_.strip()} {a_.strip()}'
            gratis = l.get('tipo') == 'pdf'
            todo.append({'t': l['titulo'], 'a': aut, 'img': ('https://aurzane.com/biblioteca/' + l['portada']) if l.get('portada') else '',
                         'f': f'https://aurzane.com/biblioteca/libro/{l["id"]}.html', 'c': l.get('buscar') or '', 'p': 'g' if gratis else 'p',
                         's': TIENDA_S.get(macro.get(str(l.get('principal')), ''), 'Mente y personalidad'), 'd': l.get('alta', ''), 'tend': '', 'y': l.get('anio') or '',
                         'lic': l.get('licencia', '') if gratis else ''})
            if gratis: n_gratis += 1
            else: n_ref += 1
    except Exception as e: print('biblioteca', e)
open(os.path.join(OUT, 'tienda.js'), 'w', encoding='utf-8').write('window.__azTienda=' + json.dumps(todo, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')

E = html.escape
def tarjeta(x):
    img = f'<img src="{E(x["img"])}" alt="Portada de {E(x["t"])}" loading="lazy" width="128" height="192">' if x['img'] else f'<span class="sin">{E(x["t"])}</span>'
    return (f'<a class="libro" href="{E(x["f"])}"><span class="por">{img}</span><span class="dat"><span class="et pago">Amazon</span><b>{E(x["t"])}</b><span class="au">{E(x["a"])}</span>'
            + (f'<span class="tend">{E(x["tend"])}</span>' if x['tend'] else '') + '</span></a>')

# fichas de los libros elegidos: páginas propias para que Google las encuentre («libro X», «de qué trata X»)
TEST_S = {'ansiedad': ('https://mind.aurzane.com/test-de-ansiedad/', 'el test de ansiedad'), 'estres': ('https://mind.aurzane.com/test-de-estres/', 'el test de estrés'),
          'depresion': ('https://mind.aurzane.com/test-de-depresion/', 'el test de depresión'), 'burnout': ('https://mind.aurzane.com/test-de-burnout/', 'el test de burnout'),
          'autoestima': ('https://mind.aurzane.com/test-de-autoestima/', 'el test de autoestima'), 'autocompasion': ('https://mind.aurzane.com/test-de-autocompasion/', 'el test de autocompasión'),
          'resiliencia': ('https://mind.aurzane.com/test-de-resiliencia/', 'el test de resiliencia'), 'satisfaccion': ('https://mind.aurzane.com/test-de-satisfaccion-con-la-vida/', 'el test de satisfacción con la vida'),
          'bienestar': ('https://live.aurzane.com/test-de-bienestar/', 'el test de bienestar'), 'habitos': ('https://live.aurzane.com/test-de-habitos/', 'el test de hábitos'),
          'sueno': ('https://live.aurzane.com/test-de-sueno/', 'el test de sueño'), 'soledad': ('https://mind.aurzane.com/test-de-soledad/', 'el test de soledad'),
          'tdah': ('https://mind.aurzane.com/test-de-tdah/', 'el test de TDAH en adultos'), 'personalidad': ('https://mind.aurzane.com/test-de-personalidad/', 'el test de personalidad'),
          'vocacional': ('https://ovp.aurzane.com/portal.html', 'el test vocacional OVP'), 'autoeficacia': ('https://mind.aurzane.com/test-de-autoeficacia/', 'el test de autoeficacia'),
          'finanzas': ('https://build.aurzane.com/calculadora-sueldo-neto/', 'la calculadora de sueldo neto'), 'vivienda': ('https://build.aurzane.com/calculadora-hipoteca/', 'la calculadora de hipoteca')}
ficha_t = open(os.path.join(D, 'ficha.html'), encoding='utf-8').read()
urls = ['https://aurzane.com/libros/']
for x, c in zip(pub, lista):
    rel = [y for y in pub if y['s'] == x['s'] and y['id'] != x['id']][:4]
    tk = next((TEST_S[t] for t in x['temas'] if t in TEST_S), None)
    datos = ' · '.join(v for v in (x['y'], c.get('editorial', ''), ('ISBN ' + c['isbn']) if c.get('isbn') else '') if v)
    jl = json.dumps({'@context': 'https://schema.org', '@type': 'Book', 'name': x['t'], 'author': {'@type': 'Person', 'name': x['a']}, 'isbn': c.get('isbn') or None,
                     'image': x['img'] or None, 'datePublished': x['y'] or None, 'publisher': c.get('editorial') or None, 'inLanguage': 'es', 'url': x['f']}, ensure_ascii=False)
    rep = {'{{T}}': E(x['t']), '{{A}}': E(x['a']), '{{URL}}': x['f'], '{{AMZ}}': E(x['u']), '{{SECCION}}': E(x['s']), '{{DATOS}}': E(datos),
           '{{IMG}}': (f'<img src="{E(x["img"])}" alt="Portada de {E(x["t"])}" width="260" height="390">' if x['img'] else f'<span class="sin">{E(x["t"])}</span>'),
           '{{OG}}': E(x['img'] or 'https://aurzane.com/og-portada.jpg'), '{{DESC}}': E((c.get('porque') or x['r'] or f'{x["t"]}, de {x["a"]}.')[:155]),
           '{{PORQUE}}': (f'<h2>Por qué lo recomendamos</h2><p>{E(c["porque"])}</p>' if c.get('porque') else ''),
           '{{RESUMEN}}': (f'<h2>De qué trata</h2><p>{E(c["resumen"])}</p>' if c.get('resumen') else ''),
           '{{TEND}}': (f'<p class="tend">Muy buscado este mes: {E(x["tend"])}</p>' if x['tend'] else ''),
           '{{TEST}}': (f'<aside class="test">¿Te interesa este tema? Haz <a href="{tk[0]}">{E(tk[1])}</a>: gratis, anónimo y con tu resultado explicado.</aside>' if tk else ''),
           '{{REL}}': ''.join(tarjeta(y) for y in rel), '{{JSONLD}}': jl.replace('</', '<\\/')}
    h_ = ficha_t
    for k_, v_ in rep.items(): h_ = h_.replace(k_, v_)
    os.makedirs(os.path.join(OUT, x['id']), exist_ok=True)
    open(os.path.join(OUT, x['id'], 'index.html'), 'w', encoding='utf-8').write(h_); urls.append(x['f'])
open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                                                    + ''.join(f'<url><loc>{u}</loc><lastmod>{HOY}</lastmod></url>' for u in urls) + '</urlset>\n')

tendencia = [x for x in pub if x['tend']][:12]
estrella = next((x for x in tendencia if x['img']), None) or next((x for x in pub if x['img']), None)
jl = json.dumps({'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Tienda de libros AURZANE', 'numberOfItems': len(todo),
                 'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'url': x['f'], 'name': x['t']} for k, x in enumerate(pub[:60])]}, ensure_ascii=False)
pag = open(os.path.join(D, 'plantilla.html'), encoding='utf-8').read()
for k, v in {'{{N}}': f'{len(todo):,}'.replace(',', '.'), '{{NG}}': f'{n_gratis:,}'.replace(',', '.'), '{{NP}}': f'{len(pub) + n_ref:,}'.replace(',', '.'),
             '{{MES}}': MES, '{{FECHA}}': HOY, '{{JSONLD}}': jl.replace('</', '<\\/'), '{{SECCIONES_JS}}': json.dumps(ORDEN_S, ensure_ascii=False),
             '{{ESTRELLA}}': (f'<a class="estrella" href="{E(estrella["f"])}"><span class="por">{"<img src=" + chr(34) + E(estrella["img"]) + chr(34) + " alt=" + chr(34) + "Portada de " + E(estrella["t"]) + chr(34) + ">" if estrella["img"] else ""}</span>'
                              f'<span class="dat"><small>LIBRO DE LA SEMANA</small><b>{E(estrella["t"])}</b><span class="au">{E(estrella["a"])}</span>'
                              f'<span class="txt">{E(estrella["tend"] or (cat.get(estrella["id"], {}).get("porque") or estrella["r"])[:200])}</span><span class="ver">Ver el libro</span></span></a>' if estrella else ''),
             '{{TENDENCIA}}': (f'<section class="sec destacada"><h2>Lo más buscado en {MES}</h2><p class="nota">Elegidos a partir de lo que más se busca en España estas semanas.</p><div class="rejilla">{"".join(tarjeta(x) for x in tendencia)}</div></section>' if tendencia else ''),
             '{{ESTATICO}}': ''.join(tarjeta(x) for x in pub)}.items():
    pag = pag.replace(k, v)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(pag)
print(f'::notice title=Tienda::{len(todo)} libros en la tienda ({len(pub)} elegidos, {n_ref} de la biblioteca con Amazon, {n_gratis} gratis); {len(nuevos)} nuevos esta vez ({sum(1 for i in nuevos if cat[i]["origen"] == "tendencia")} por tendencias)')
