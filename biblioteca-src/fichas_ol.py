# -*- coding: utf-8 -*-
"""Busca en Open Library la edición en español de cada ficha (ISBN, editorial, año) y su portada.
Escribe cosecha3/fichas-ol.json y deja las portadas en $SALIDA/fichas/<id>.jpg. Se ejecuta en GitHub Actions."""
import json, os, re, time, urllib.request, urllib.parse, unicodedata, io
from PIL import Image
MOD = os.environ.get('FICHAS', 'fichas3')  # fichas3 o fichas4
FICHAS3 = getattr(__import__(MOD), MOD.upper())
OUT = {'fichas3': 'cosecha3/fichas-ol.json'}.get(MOD, 'cosecha4/%s-ol.json' % MOD)
UA = {'User-Agent': 'AURZANE-Biblioteca/1.0 (+https://aurzane.com/biblioteca/)'}
SALIDA = os.environ.get('SALIDA', '/tmp/transito')
os.makedirs(SALIDA + '/fichas', exist_ok=True)
def get(u, raw=False):
    for i in range(3):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
            return b if raw else json.loads(b)
        except Exception as e:
            err = e; time.sleep(2 + 3 * i)
    raise err
def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    return re.sub(r'[^a-z0-9 ]', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))
def pal(s): return [w for w in norm(s).split() if len(w) > 2]
def parecido(a, b):
    pa, pb = pal(a.split('.')[0]), set(pal(b))
    return sum(1 for w in pa if w in pb) / max(1, len(pa))
HISP = ('97884', '97895', '97896', '97897', '978607', '978612', '9789942', '9789978', '9789972', '9789974', '9789992', '9789993', '9789994', '9789996', '9789929', '9789968', '9789945', '9789962')
def hisp(i):
    i = re.sub(r'[^0-9X]', '', str(i))
    if len(i) == 10: i = '978' + i
    return i.startswith(HISP) and not i.startswith(('97895', '97896', '97897')) or i.startswith(('978950', '978956', '978958', '978959', '978968', '978970', '978980', '978987', '9789500'))
def ttl(f, autor):
    # catálogo de Todos tus libros (librerías CEGAL): ediciones a la venta en España
    import html as H
    s = get('https://www.todostuslibros.com/busquedas?keyword=' + urllib.parse.quote(f['titulo'].split('.')[0] + ' ' + (pal(autor)[-1] if pal(autor) else '')), raw=True).decode('utf-8', 'replace')
    for li in re.findall(r'<li\s+class="book-col"(.*?)</li>', s, re.S):
        t = H.unescape((re.search(r'data-gtm-titulo="([^"]*)"', li) or [None, ''])[1])
        a = H.unescape(re.sub(r'<[^>]+>', ' ', (re.search(r'<p class="author">(.*?)</p>', li, re.S) or [None, ''])[1]))
        if parecido(f['titulo'], t) < 0.6 or parecido(t, f['titulo']) < 0.5: continue
        if not any(w in norm(a) for w in pal(autor)[-1:]): continue
        isbn = re.sub(r'-', '', (re.search(r'data-gtm-isbn="([^"]*)"', li) or [None, ''])[1])
        link = (re.search(r'href="(https://www\.todostuslibros\.com/libros/[^"]+)"', li) or [None, ''])[1]
        img = (re.search(r'<img src="(https://static\.cegal\.es/[^"]+)"', li) or [None, ''])[1]
        ed = H.unescape((re.search(r'data-gtm-editorial="([^"]*)"', li) or [None, ''])[1])
        anio = ''
        try:
            dt = get(link, raw=True).decode('utf-8', 'replace'); time.sleep(1)
            m = re.search(r'(?:Fecha de publicaci[oó]n|A[nñ]o de edici[oó]n|Publicaci[oó]n)[^0-9]{0,80}?((?:19|20)\d\d)', re.sub(r'<[^>]+>', ' ', dt))
            if m: anio = m.group(1)
        except Exception: pass
        return dict(edicion='ttl:' + link, titulo_ed=t, isbn=isbn, editorial=ed, anio=anio, cover=img or ('https://covers.openlibrary.org/b/isbn/%s-L.jpg?default=false' % isbn), via='todostuslibros')
    return None
def portada(cid):
    try:
        u = cid if str(cid).startswith('http') else 'https://covers.openlibrary.org/b/id/%s-L.jpg?default=false' % cid
        b = get(u, raw=True)
        im = Image.open(io.BytesIO(b)); im.load()
        if im.size[0] < 110 or im.size[1] < 160: return None
        im = im.convert('RGB')
        if im.size[0] > 420: im = im.resize((420, round(im.size[1] * 420 / im.size[0])), Image.LANCZOS)
        o = io.BytesIO(); im.save(o, 'JPEG', quality=84, optimize=True); return o.getvalue()
    except Exception:
        return None
PREV = json.load(open(OUT)) if os.path.exists(OUT) else {}
res = {}
for f in FICHAS3:
    if PREV.get(f['id'], {}).get('ok') and not PREV[f['id']].get('solo_obra') and os.path.exists('%s/fichas/%s.jpg' % (SALIDA, f['id'])):
        res[f['id']] = PREV[f['id']]; continue
    r = {'ok': False}
    try:
        autor = f['autores'].split(' y ')[0].split(',')[0]
        q = urllib.parse.urlencode({'title': f['titulo'].split('.')[0], 'author': autor, 'limit': 10, 'fields': 'key,title,author_name,cover_i,language,edition_count'})
        docs = get('https://openlibrary.org/search.json?' + q).get('docs', [])
        docs = [d for d in docs if parecido(f['titulo'], d.get('title', '')) >= 0.6 or parecido(d.get('title', ''), f['titulo']) >= 0.6]
        docs = [d for d in docs if any(w in norm(' '.join(d.get('author_name', []))) for w in pal(autor)[-1:])]
        mejor = None
        # 1) búsqueda con ediciones: OL devuelve la edición que mejor encaja (título en español aunque la obra esté en otro idioma)
        try:
            q0 = urllib.parse.urlencode({'q': '%s %s' % (f['titulo'].split('.')[0], pal(autor)[-1] if pal(autor) else ''), 'limit': 8,
                                         'fields': 'key,title,author_name,editions,editions.key,editions.title,editions.subtitle,editions.language,editions.isbn,editions.publisher,editions.publish_date,editions.cover_i'})
            for d in get('https://openlibrary.org/search.json?' + q0).get('docs', []):
                if not any(w in norm(' '.join(d.get('author_name', []))) for w in pal(autor)[-1:]): continue
                for e in (d.get('editions') or {}).get('docs', []):
                    if 'spa' not in (e.get('language') or []) and not any(hisp(i) for i in e.get('isbn', [])): continue
                    if parecido(f['titulo'], e.get('title', '') + ' ' + e.get('subtitle', '')) < 0.6: continue
                    isbn = next((i for i in e.get('isbn', []) if len(i) == 13), '') or (e.get('isbn') or [''])[0]
                    cov = e.get('cover_i') or ('https://covers.openlibrary.org/b/isbn/%s-L.jpg?default=false' % isbn if isbn else None)
                    if not cov: continue
                    mejor = dict(edicion=e['key'], titulo_ed=e.get('title'), isbn=isbn, editorial=(e.get('publisher') or [''])[0],
                                 anio=(re.search(r'(1[89]|20)\d\d', ' '.join(e.get('publish_date') or [])) or [''])[0], cover=cov, via='ediciones-es')
                    break
                if mejor: break
        except Exception as ex:
            print('ediciones', str(ex)[:80])
        for d in ([] if mejor else docs):
            eds = get('https://openlibrary.org%s/editions.json?limit=100' % d['key']).get('entries', [])
            for e in eds:
                langs = [l.get('key', '') for l in e.get('languages', [])]
                if '/languages/spa' not in langs or not e.get('covers'): continue
                if parecido(f['titulo'], e.get('title', '') + ' ' + e.get('subtitle', '')) < 0.6: continue
                isbn = (e.get('isbn_13') or e.get('isbn_10') or [''])[0]
                cand = dict(edicion=e.get('key'), titulo_ed=e.get('title'), isbn=isbn, editorial=(e.get('publishers') or [''])[0],
                            anio=(re.search(r'(1[89]|20)\d\d', e.get('publish_date', '') or '') or [''])[0], cover=e['covers'][0])
                if not mejor or (isbn and not mejor['isbn']) or (cand['anio'] > mejor['anio'] and bool(isbn) == bool(mejor['isbn'])): mejor = cand
            time.sleep(0.5)
        if not mejor:  # búsqueda directa de ediciones en español
            q2 = urllib.parse.urlencode({'q': f['titulo'].split('.')[0] + ' ' + autor, 'language': 'spa', 'limit': 10,
                                         'fields': 'key,title,author_name,cover_i,cover_edition_key,publisher,first_publish_year,isbn'})
            for d in get('https://openlibrary.org/search.json?' + q2).get('docs', []):
                if not d.get('cover_i') or parecido(f['titulo'], d.get('title', '')) < 0.6: continue
                if not any(w in norm(' '.join(d.get('author_name', []))) for w in pal(autor)[-1:]): continue
                isbn = next((i for i in d.get('isbn', []) if len(i) == 13 and i.startswith('97884')), '') or next((i for i in d.get('isbn', []) if len(i) == 13), '')
                mejor = dict(edicion=d['key'], titulo_ed=d['title'], isbn=isbn, editorial=(d.get('publisher') or [''])[0], anio=str(d.get('first_publish_year') or ''), cover=d['cover_i'], via='busqueda-es'); break
        if not mejor:  # Google Books, solo ediciones en español
            try:
                gq = urllib.parse.urlencode({'q': 'intitle:' + f['titulo'].split('.')[0] + ' inauthor:' + pal(autor)[-1], 'langRestrict': 'es', 'maxResults': 10, 'printType': 'books'})
                time.sleep(2)
                for it in get('https://www.googleapis.com/books/v1/volumes?' + gq).get('items', []):
                    vi = it['volumeInfo']
                    if vi.get('language') != 'es' or parecido(f['titulo'], vi.get('title', '')) < 0.6 or not vi.get('imageLinks'): continue
                    isbn = next((x['identifier'] for x in vi.get('industryIdentifiers', []) if x['type'] == 'ISBN_13'), '')
                    mejor = dict(edicion='gb:' + it['id'], titulo_ed=vi['title'], isbn=isbn, editorial=vi.get('publisher', ''), anio=vi.get('publishedDate', '')[:4],
                                 cover='https://books.google.com/books/content?id=%s&printsec=frontcover&img=1&zoom=1' % it['id'], via='google'); break
            except Exception as e:
                print('google', str(e)[:80])
        if not mejor:
            try: mejor = ttl(f, autor); time.sleep(1)
            except Exception as ex: print('ttl', str(ex)[:80])
        if not mejor and docs and docs[0].get('cover_i'):
            mejor = dict(edicion=docs[0]['key'], titulo_ed=docs[0]['title'], isbn='', editorial='', anio='', cover=docs[0]['cover_i'], solo_obra=True)
        if mejor:
            img = portada(mejor['cover'])
            if img:
                open('%s/fichas/%s.jpg' % (SALIDA, f['id']), 'wb').write(img)
                r = dict(mejor, ok=True)
            else:
                alt = None
                if mejor.get('via') != 'todostuslibros':
                    try: alt = ttl(f, autor)
                    except Exception: alt = None
                img2 = portada(alt['cover']) if alt else None
                if img2:
                    open('%s/fichas/%s.jpg' % (SALIDA, f['id']), 'wb').write(img2)
                    r = dict(mejor, ok=True, portada_de=alt.get('edicion'))
                else:
                    r = dict(mejor, ok=True, sin_portada=True)
        else:
            r['err'] = 'sin edición en español con portada'
    except Exception as e:
        r['err'] = str(e)[:150]
    res[f['id']] = r; print(f['id'], r, flush=True)
    time.sleep(0.5)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('ok', sum(1 for v in res.values() if v.get('ok')), 'de', len(res))
