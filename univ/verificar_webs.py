"""Comprueba que la web oficial de cada universidad principal responde. Salida univ/data/principales.json"""
import json, sys, urllib.request, ssl, concurrent.futures
sys.path.insert(0, 'univ')
from principales import P, ISO
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
def probar(w):
    err = ''
    for url in [w, w.replace('https://', 'http://')]:
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=25, context=ctx)
            return r.status, r.geturl()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 405, 429, 503): return e.code, url  # el sitio existe pero bloquea bots
            err = 'HTTP %d' % e.code
        except Exception as e:
            err = str(e)[:80]
    return 0, err
items = [(p, n, c, t, w) for p, l in P.items() for (n, c, t, w) in l]
with concurrent.futures.ThreadPoolExecutor(16) as ex:
    res = list(ex.map(lambda it: probar(it[4]), items))
out = []
for (p, n, c, t, w), (st, fin) in zip(items, res):
    out.append({'pais': p, 'iso': ISO[p], 'nombre': n, 'ciudad': c, 'tipo': t, 'web': w, 'estado_web': st, 'web_final': fin})
    print(st, p, n, w, fin)
json.dump(out, open('univ/data/principales.json', 'w'), ensure_ascii=False, indent=1)
print('KO', sum(1 for o in out if not o['estado_web']))
