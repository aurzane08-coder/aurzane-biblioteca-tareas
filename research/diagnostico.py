"""Prueba las consultas del Research Hub contra Supabase y cuenta cómo está la biblioteca (para elegir filtros útiles)."""
import time, urllib.request, urllib.error, json
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
def n(f):
    rq = urllib.request.Request(SB + 'biblioteca_unificada?select=id&limit=1' + f, headers={'apikey': KEY, 'Prefer': 'count=exact'})
    t = time.time()
    try:
        with urllib.request.urlopen(rq, timeout=60) as r: return r.headers.get('Content-Range', '').split('/')[-1] + f' ({time.time()-t:.1f}s)'
    except urllib.error.HTTPError as e: return f'ERROR {e.code} {e.read()[:200]}'
for f in ['', '&es_acceso_abierto=eq.true', '&es_acceso_abierto=eq.false', '&abstract=not.is.null', '&abstract=is.null', '&anio=gte.2025', '&anio=gte.2023', '&anio=lt.2015', '&anio=is.null', '&licencia=ilike.cc-by*', '&licencia=is.null', '&search_vector=wfts.anxiety', '&search_vector=wfts.ansiedad%20or%20anxiety']:
    print('cuenta', f or 'total', n(f))
rq = urllib.request.Request(SB + 'biblioteca_unificada?select=licencia,anio&limit=1000&offset=12000', headers={'apikey': KEY})
d = json.load(urllib.request.urlopen(rq, timeout=60)); from collections import Counter
print('cuenta licencias', Counter(x['licencia'] for x in d).most_common(8)); print('cuenta años', sorted(Counter(x['anio'] for x in d).items())[-12:])
