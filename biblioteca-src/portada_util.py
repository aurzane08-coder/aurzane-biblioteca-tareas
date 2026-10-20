# -*- coding: utf-8 -*-
"""Búsqueda de la mejor portada para un libro (se ejecuta en GitHub Actions).
Orden: portada en la web por ISBN (Open Library, Google Books), portada en la web por título y autor
(solo si el título coincide), y si no, la primera de las 4 primeras páginas del PDF que parezca una portada
(con imagen o color), no una página de texto."""
import json, re, os, subprocess, urllib.request, urllib.parse, unicodedata, io, time
from PIL import Image, ImageStat
UA = {'User-Agent': 'Mozilla/5.0 (AURZANE-Biblioteca/1.0; +https://aurzane.com/biblioteca/)'}

def get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    return re.sub(r'[^a-z0-9 ]', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))

def palabras(s): return [w for w in norm(s).split() if len(w) > 2 and w not in ('del', 'las', 'los', 'una', 'para', 'con', 'por', 'the', 'and')]

def parecido(a, b):
    """Coincidencia del título: proporción de palabras del título corto contenidas en el otro."""
    pa, pb = palabras(a.split(':')[0]), set(palabras(b))
    return sum(1 for w in pa if w in pb) / max(1, len(pa))

def medir(img):
    """Devuelve (blanco, color, oscuro): proporción de píxeles casi blancos, con color vivo y oscuros."""
    im = img.convert('RGB').resize((90, 128))
    px = list(im.getdata())
    blanco = sum(1 for r, g, b in px if min(r, g, b) > 215) / len(px)
    oscuro = sum(1 for r, g, b in px if max(r, g, b) < 90) / len(px)
    color = sum(1 for r, g, b in px if max(r, g, b) > 60 and (max(r, g, b) - min(r, g, b)) / max(r, g, b) > 0.35) / len(px)
    return blanco, color, oscuro

def en_blanco(img): return medir(img)[0] > 0.985

def es_portada(img):
    """Una página de texto es casi toda blanca, sin color y con poca tinta. Todo lo demás cuenta como portada."""
    blanco, color, oscuro = medir(img)
    return not (blanco > 0.78 and color < 0.02 and oscuro < 0.10)

def imagen_valida(datos, minimo=110):
    try:
        im = Image.open(io.BytesIO(datos)); im.load()
        return im if im.size[0] >= minimo and im.size[1] >= minimo * 1.2 else None
    except Exception:
        return None

def por_isbn(isbns, titulo=''):
    for i in isbns:
        i = re.sub(r'[^0-9Xx]', '', i)
        if len(i) not in (10, 13): continue
        try:
            ed = json.loads(get('https://openlibrary.org/isbn/%s.json' % i))
            if titulo and parecido(titulo, ed.get('title', '') + ' ' + ed.get('subtitle', '')) < 0.7: continue
            if ed.get('covers'):
                im = imagen_valida(get('https://covers.openlibrary.org/b/id/%s-L.jpg' % ed['covers'][0]))
                if im and es_portada(im): return im, 'Open Library (ISBN %s)' % i
        except Exception: pass
        try:
            r = json.loads(get('https://www.googleapis.com/books/v1/volumes?q=isbn:%s' % i))
            for v in r.get('items', [])[:1]:
                if titulo and parecido(titulo, v['volumeInfo'].get('title', '')) < 0.7: continue
                u = (v['volumeInfo'].get('imageLinks') or {}).get('thumbnail')
                if u:
                    im = imagen_valida(get(u.replace('http:', 'https:').replace('&edge=curl', '').replace('zoom=1', 'zoom=0')), 100) or imagen_valida(get(u.replace('http:', 'https:')), 100)
                    if im: return im, 'Google Books (ISBN %s)' % i
        except Exception: pass
        time.sleep(0.5)
    return None, ''

def por_titulo(titulo, autores, anio=''):
    ap = palabras((autores or '').split(';')[0].split(',')[0])
    try:
        q = urllib.parse.urlencode({'title': titulo.split(':')[0][:120], 'author': ' '.join(ap[:2]), 'limit': 8, 'fields': 'title,author_name,cover_i,language,edition_count,first_publish_year,publish_year'})
        r = json.loads(get('https://openlibrary.org/search.json?' + q))
        for d in r.get('docs', []):
            if not d.get('cover_i'): continue
            if parecido(titulo, d.get('title', '')) < 0.85 or parecido(d.get('title', ''), titulo) < 0.6: continue
            if not ap or not any(w in norm(' '.join(d.get('author_name', []))) for w in ap[:1]): continue
            if anio and str(anio)[:4].isdigit() and not any(abs(int(str(anio)[:4]) - y) <= 1 for y in d.get('publish_year', []) or [0]): continue
            im = imagen_valida(get('https://covers.openlibrary.org/b/id/%s-L.jpg' % d['cover_i']))
            if im and es_portada(im): return im, 'Open Library (búsqueda por título)'
    except Exception: pass
    try:
        q = 'intitle:' + titulo.split(':')[0][:100] + (' inauthor:' + ap[0] if ap else '')
        r = json.loads(get('https://www.googleapis.com/books/v1/volumes?' + urllib.parse.urlencode({'q': q, 'maxResults': 5})))
        for v in r.get('items', []):
            vi = v['volumeInfo']
            if parecido(titulo, vi.get('title', '')) < 0.85 or parecido(vi.get('title', ''), titulo) < 0.6: continue
            if not ap or not any(w in norm(' '.join(vi.get('authors', []))) for w in ap[:1]): continue
            if anio and str(anio)[:4].isdigit() and vi.get('publishedDate', '')[:4].isdigit() and abs(int(str(anio)[:4]) - int(vi['publishedDate'][:4])) > 1: continue
            u = (vi.get('imageLinks') or {}).get('thumbnail')
            if not u: continue
            im = imagen_valida(get(u.replace('http:', 'https:').replace('&edge=curl', '').replace('zoom=1', 'zoom=0')), 100) or imagen_valida(get(u.replace('http:', 'https:')), 100)
            if im and es_portada(im): return im, 'Google Books (búsqueda por título)'
    except Exception: pass
    return None, ''

def paginas_pdf(pdf, n=4, ancho=420):
    out = []
    for p in range(1, n + 1):
        base = '/tmp/pp-%d' % p
        r = subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-scale-to-x', str(ancho), '-scale-to-y', '-1', '-jpeg', '-singlefile', pdf, base], capture_output=True, timeout=120)
        if r.returncode or not os.path.exists(base + '.jpg'): break
        out.append(Image.open(base + '.jpg').convert('RGB')); os.remove(base + '.jpg')
    return out

def mejor_portada(pdf=None, isbns=(), titulo='', autores='', anio=''):
    """Devuelve (imagen PIL, origen). origen vacío si no hay portada con imagen (se usará la portada tipográfica)."""
    pags = paginas_pdf(pdf, 2) if pdf else []
    if pags and es_portada(pags[0]): return pags[0], 'Primera página del libro'
    if len(pags) > 1 and en_blanco(pags[0]) and es_portada(pags[1]): return pags[1], 'Segunda página del libro'
    im, o = por_isbn(isbns, titulo)
    if im: return im, o
    im, o = por_titulo(titulo, autores, anio)
    if im: return im, o
    return (pags[0] if pags else None), ''

def jpg(im, ancho=420):
    im = im.convert('RGB')
    if im.size[0] > ancho: im = im.resize((ancho, round(im.size[1] * ancho / im.size[0])), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=84, optimize=True); return b.getvalue()
