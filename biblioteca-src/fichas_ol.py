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
        for d in docs:
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
                for it in get('https://www.googleapis.com/books/v1/volumes?' + gq).get('items', []):
                    vi = it['volumeInfo']
                    if vi.get('language') != 'es' or parecido(f['titulo'], vi.get('title', '')) < 0.6 or not vi.get('imageLinks'): continue
                    isbn = next((x['identifier'] for x in vi.get('industryIdentifiers', []) if x['type'] == 'ISBN_13'), '')
                    mejor = dict(edicion='gb:' + it['id'], titulo_ed=vi['title'], isbn=isbn, editorial=vi.get('publisher', ''), anio=vi.get('publishedDate', '')[:4],
                                 cover='https://books.google.com/books/content?id=%s&printsec=frontcover&img=1&zoom=1' % it['id'], via='google'); break
            except Exception as e:
                print('google', str(e)[:80])
        if not mejor and docs and docs[0].get('cover_i'):
            mejor = dict(edicion=docs[0]['key'], titulo_ed=docs[0]['title'], isbn='', editorial='', anio='', cover=docs[0]['cover_i'], solo_obra=True)
        if mejor:
            img = portada(mejor['cover'])
            if img:
                open('%s/fichas/%s.jpg' % (SALIDA, f['id']), 'wb').write(img)
                r = dict(mejor, ok=True)
            else:
                r = dict(mejor, ok=False, err='portada no válida')
        else:
            r['err'] = 'sin edición en español con portada'
    except Exception as e:
        r['err'] = str(e)[:150]
    res[f['id']] = r; print(f['id'], r, flush=True)
    time.sleep(0.5)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('ok', sum(1 for v in res.values() if v.get('ok')), 'de', len(res))
