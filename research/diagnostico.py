"""Prueba las consultas del Research Hub contra Supabase (lo mismo que hace la página) y mide el tiempo."""
import time, urllib.request, urllib.error, json
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
SEL = 'id,mundo,titulo,abstract,autores,anio,licencia,es_acceso_abierto,url_articulo,doi'
P = [
 ('sin término, count exact', f'biblioteca_unificada?select={SEL}&order=anio.desc.nullslast&limit=20', 'exact'),
 ('sin término, sin count', f'biblioteca_unificada?select={SEL}&order=anio.desc.nullslast&limit=20', None),
 ('sin término, count estimated', f'biblioteca_unificada?select=id&limit=1', 'estimated'),
 ('total exact limit 1', f'biblioteca_unificada?select=id&limit=1', 'exact'),
 ('acceso abierto', f'biblioteca_unificada?select={SEL}&es_acceso_abierto=eq.true&order=anio.desc.nullslast&limit=20', 'exact'),
 ('mundo live', f'biblioteca_unificada?select={SEL}&mundo=eq.live&order=anio.desc.nullslast&limit=20', 'exact'),
 ('offset 20', f'biblioteca_unificada?select={SEL}&order=anio.desc.nullslast&limit=20&offset=20', 'exact'),
 ('búsqueda mental health', f'biblioteca_unificada?select={SEL}&search_vector=wfts.mental%20health&order=anio.desc.nullslast&limit=20', 'exact'),
 ('búsqueda ansiedad', f'biblioteca_unificada?select={SEL}&search_vector=wfts.ansiedad&order=anio.desc.nullslast&limit=20', 'exact'),
]
for n, q, c in P:
    h = {'apikey': KEY}
    if c: h['Prefer'] = f'count={c}'
    t = time.time()
    try:
        with urllib.request.urlopen(urllib.request.Request(SB + q, headers=h), timeout=60) as r:
            d = json.load(r); print(f'{n}: {len(d)} filas, total {r.headers.get("Content-Range")}, {time.time()-t:.1f}s', (d[0]['anio'], d[0]['mundo'], (d[0]['titulo'] or '')[:60]) if d else '')
    except urllib.error.HTTPError as e: print(f'{n}: ERROR {e.code} {time.time()-t:.1f}s', e.read()[:300])
    except Exception as e: print(f'{n}: ERROR {e}')
