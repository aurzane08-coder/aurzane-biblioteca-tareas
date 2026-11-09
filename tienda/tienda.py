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
    for i in range(3):
        try:
            rq = urllib.request.Request(url, data=datos, headers={'User-Agent': 'AURZANE-tienda/1.0', **(cab or {})})
            with urllib.request.urlopen(rq, timeout=t) as r: return r.status, r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code in (429, 503): time.sleep(4 * (i + 1)); continue
            return e.code, e.read().decode('utf-8', 'replace')
        except Exception as e:
            err = str(e); time.sleep(3)
    return 0, err


def norm(t):
    t = unicodedata.normalize('NFD', str(t or '').lower())
    return re.sub(r'[^a-z0-9 ]', ' ', ''.join(c for c in t if unicodedata.category(c) != 'Mn')).split()


def slug(t): return '-'.join(norm(t))[:70]


def verificar(titulo, autor):
    """Busca el libro en Google Books; devuelve sus datos si el título y el autor coinciden de verdad."""
    ape = [w for w in norm(autor) if len(w) > 3 and w not in ('y', 'and')]
    pal = [w for w in norm(titulo) if len(w) > 2][:4]
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
for l in semilla['libros']:
    i = slug(l['titulo'] + ' ' + l['autor'])
    if i in cat or i in descartes: continue
    v = verificar(l['titulo'], l['autor']); time.sleep(0.6)
    if not v: descartes.add(i); print('sin verificar:', l['titulo']); continue
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

# 3) salida
def amazon(x): return 'https://www.amazon.es/s?' + urllib.parse.urlencode({'k': x.get('isbn') or f'{x["titulo"]} {x["autor"]}', 'i': 'stripbooks', 'tag': TAG})

lista = sorted(cat.values(), key=lambda x: (x.get('tendencia_fecha', ''), x['fecha']), reverse=True)
json.dump(lista, open(os.path.join(D, 'catalogo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(sorted(descartes), open(os.path.join(D, 'descartes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
pub = [{'t': x['titulo'], 'a': x['autor'], 'temas': x['temas'], 's': SECC.get(x['temas'][0], 'Ensayo e ideas'), 'img': x.get('portada', ''),
        'u': amazon(x), 'r': (x.get('resumen') or '')[:220], 'y': x.get('anio', ''), 'tend': x.get('tendencia', '') if x.get('tendencia_fecha', '') >= (datetime.date.today() - datetime.timedelta(days=35)).isoformat() else ''}
       for x in lista]
json.dump(pub, open(os.path.join(OUT, 'libros.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
# versión .js para que los tests y artículos de los subdominios la carguen sin problemas de CORS
open(os.path.join(OUT, 'libros.js'), 'w', encoding='utf-8').write('window.__azLibros=' + json.dumps(pub, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')

E = html.escape
def tarjeta(x):
    img = f'<img src="{E(x["img"])}" alt="Portada de {E(x["t"])}" loading="lazy" width="128" height="192">' if x['img'] else f'<span class="sin">{E(x["t"])}</span>'
    return (f'<a class="libro" href="{E(x["u"])}" target="_blank" rel="sponsored nofollow noopener" data-s="{E(x["s"])}" data-q="{E(" ".join(norm(x["t"] + " " + x["a"] + " " + x["s"])))}">'
            f'<span class="por">{img}</span><span class="dat"><b>{E(x["t"])}</b><span class="au">{E(x["a"])}</span>'
            + (f'<span class="tend">{E(x["tend"])}</span>' if x['tend'] else '') + '<span class="ver">Ver en Amazon</span></span></a>')

secciones = []
for s in dict.fromkeys(SECC.values()):
    ls = [x for x in pub if x['s'] == s]
    if ls: secciones.append(f'<section class="sec" data-sec="{E(s)}"><h2>{E(s)} <small>{len(ls)}</small></h2><div class="rejilla">{"".join(tarjeta(x) for x in ls)}</div></section>')
tendencia = [x for x in pub if x['tend']][:12]
chips = ''.join(f'<button type="button" data-f="{E(s)}">{E(s)}</button>' for s in dict.fromkeys(SECC.values()) if any(x['s'] == s for x in pub))
jl = json.dumps({'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Tienda de libros AURZANE', 'numberOfItems': len(pub),
                 'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'item': {'@type': 'Book', 'name': x['t'], 'author': x['a']}} for k, x in enumerate(pub[:60])]}, ensure_ascii=False)
pag = open(os.path.join(D, 'plantilla.html'), encoding='utf-8').read()
for k, v in {'{{N}}': str(len(pub)), '{{CHIPS}}': chips, '{{SECCIONES}}': ''.join(secciones), '{{MES}}': MES, '{{FECHA}}': HOY, '{{JSONLD}}': jl.replace('</', '<\\/'),
             '{{TENDENCIA}}': (f'<section class="sec destacada"><h2>Lo más buscado en {MES}</h2><p class="nota">Elegidos a partir de lo que más se busca en España estas semanas.</p><div class="rejilla">{"".join(tarjeta(x) for x in tendencia)}</div></section>' if tendencia else '')}.items():
    pag = pag.replace(k, v)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(pag)
print(f'::notice title=Tienda::{len(pub)} libros en la tienda, {len(nuevos)} nuevos esta vez ({sum(1 for i in nuevos if cat[i]["origen"] == "tendencia")} por tendencias)')
