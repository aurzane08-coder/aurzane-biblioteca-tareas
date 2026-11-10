"""Muestra las columnas disponibles en biblioteca_unificada y unos valores de ejemplo (para diseñar filtros y tarjetas)."""
import json, urllib.request
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
def get(q):
    with urllib.request.urlopen(urllib.request.Request(SB + q, headers={'apikey': KEY}), timeout=60) as r: return json.load(r)
fila = get('biblioteca_unificada?select=*&limit=1&abstract=not.is.null')[0]
print('columnas', {k: (str(v)[:80] if v is not None else None) for k, v in fila.items() if k != 'search_vector'})
for m in ['mind', 'live']:
    f = get(f'{m}_biblioteca?select=*&limit=1')[0]
    print('columnas', m, {k: (str(v)[:60] if v is not None else None) for k, v in f.items() if k != 'search_vector'})
