"""Precio del alquiler por municipio con datos oficiales del INE (17/11/2026, etapa 3 de la auditoría, tarea 42).
Descarga del INE el Índice de Precios de Vivienda en Alquiler (IPVA), tabla 59060 «Índices por municipio (municipios
mayores de 10.000 habitantes)», base 2015 = 100, y escribe el archivo de datos que usa la herramienta
build.aurzane.com/alquiler-por-municipio/. Corre cada mes (.github/workflows/alquiler-ine.yml); si el INE publica un año
nuevo, la herramienta lo muestra sola. Si la respuesta no es completa, no cambia nada.
Salida: salida-ine/datos.json (el flujo lo sube por SSH a build.aurzane.com/alquiler-por-municipio/)"""
import json, os, re, sys, time, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/59060?nult=12'
for i in range(4):
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'AURZANE-BUILD/1.0 (hola@aurzane.com)'}), timeout=120) as r:
            S = json.load(r); break
    except Exception as e:
        print('reintento', i + 1, str(e)[:80]); time.sleep(10 * (i + 1))
else:
    sys.exit('El INE no responde: se deja el dato anterior')
idx, var = {}, {}
for s in S:
    p = [x.strip() for x in s['Nombre'].split('.') if x.strip()]
    nom = p[0]
    if nom.startswith('Resto '): continue
    serie = {int(d['Anyo']): d['Valor'] for d in s.get('Data', []) if d.get('Valor') is not None and d.get('Anyo')}
    if 'Índice' in p: idx[nom] = serie
    elif 'Variación anual' in p: var[nom] = serie
nac = 'Total Nacional'
anyo = max(idx.get(nac, {0: 0}))
if len(idx) < 300 or anyo < 2023: sys.exit(f'Datos incompletos del INE ({len(idx)} municipios, año {anyo}): no se cambia nada')
m = []
for nom, serie in idx.items():
    if nom == nac or anyo not in serie: continue
    v = var.get(nom, {}).get(anyo)
    cinco = round((serie[anyo] / serie[anyo - 5] - 1) * 100, 1) if serie.get(anyo - 5) else None
    m.append([nom, v, round(serie[anyo], 1), cinco])
m.sort(key=lambda x: x[0])
out = {'anyo': anyo, 'fuente': 'INE, Índice de Precios de Vivienda en Alquiler (IPVA), tabla 59060, base 2015 = 100',
       'actualizado': time.strftime('%Y-%m-%d'), 'nac': [var.get(nac, {}).get(anyo), round(idx[nac][anyo], 1),
       round((idx[nac][anyo] / idx[nac][anyo - 5] - 1) * 100, 1) if idx[nac].get(anyo - 5) else None], 'm': m}
d = os.path.join(R, 'salida-ine'); os.makedirs(d, exist_ok=True)
nuevo = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
viejo_p = os.path.join(R, 'herramientas', 'alquiler_ine_ultimo.json')
if os.path.exists(viejo_p) and json.load(open(viejo_p))['m'] == out['m']:
    print(f'Sin cambios en el INE (año {anyo}, {len(m)} municipios)')
    open(os.path.join(d, 'datos.json'), 'w').write(nuevo); sys.exit(0)   # se vuelve a subir igual: así el servidor nunca se queda sin él
open(os.path.join(d, 'datos.json'), 'w').write(nuevo); open(viejo_p, 'w').write(nuevo)
print(f'Alquiler INE: año {anyo}, {len(m)} municipios, España {out["nac"][0]} % en el último año')
