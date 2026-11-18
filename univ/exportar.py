"""Exporta universidades y carreras de Supabase (lectura pública) a univ/data/*.json.gz"""
import json, gzip, urllib.request, os, time
U = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
K = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
def todo(tabla, orden='id'):
    out, i, n = [], 0, 1000
    while True:
        req = urllib.request.Request(f'{U}{tabla}?select=*&order={orden}', headers={'apikey': K, 'Authorization': 'Bearer ' + K, 'Range-Unit': 'items', 'Range': f'{i}-{i+n-1}'})
        for t in range(5):
            try:
                with urllib.request.urlopen(req, timeout=60) as r: lote = json.load(r); break
            except Exception as e:
                print('reintento', tabla, i, e); time.sleep(3)
        out += lote; print(tabla, len(out), flush=True)
        if len(lote) < n: return out
        i += n
os.makedirs('univ/data', exist_ok=True)
for t in ['universidades', 'carreras']:
    d = todo(t)
    # sin fecha dentro del .gz y con orden fijo: si los datos no cambian, el archivo es idéntico y no se guarda otra copia
    # (19/11/2026: cada exportación guardaba 9 MB nuevos en el historial aunque nada hubiera cambiado)
    with open(f'univ/data/sb_{t}.json.gz', 'wb') as fb, gzip.GzipFile(fileobj=fb, mode='wb', mtime=0, filename='') as g:
        g.write(json.dumps(d, ensure_ascii=False, sort_keys=True).encode('utf-8'))
    print('OK', t, len(d))
