import urllib.request, urllib.parse, os, time
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36', 'Accept-Language': 'es-ES,es;q=0.9'}
os.makedirs('/tmp/sondeo', exist_ok=True)
U = {
 'ttl': 'https://www.todostuslibros.com/busquedas?keyword=' + urllib.parse.quote('Compórtate Sapolsky'),
 'gb': 'https://www.googleapis.com/books/v1/volumes?q=' + urllib.parse.quote('intitle:Compórtate inauthor:Sapolsky') + '&langRestrict=es',
 'bne': 'https://datos.bne.es/find?s=' + urllib.parse.quote('Compórtate Sapolsky'),
 'ol': 'https://openlibrary.org/search.json?q=' + urllib.parse.quote('Compórtate Sapolsky') + '&fields=key,title,editions,editions.title,editions.language,editions.isbn',
 'casadellibro': 'https://www.casadellibro.com/?query=' + urllib.parse.quote('Compórtate Sapolsky'),
 'isbnes': 'https://www.cultura.gob.es/webISBN/tituloSimpleFilter.do?cache=init&layout=busquedaisbn&language=es&prev_layout=busquedaisbn&params.cisbnExt=&params.forma=gl&params.liConceptosExt%5B0%5D.texto=' + urllib.parse.quote('Compórtate') + '&action=Buscar',
}
for k, u in U.items():
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        open('/tmp/sondeo/%s.html' % k, 'wb').write(b); print(k, 'ok', len(b))
    except Exception as e:
        print(k, 'ERR', str(e)[:100])
    time.sleep(2)
