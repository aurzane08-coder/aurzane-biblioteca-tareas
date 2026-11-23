"""Exporta universidades y carreras de Supabase (lectura pública) a univ/data/*.json.gz

23/11/2026: Supabase avisó de que el proyecto pasó el límite gratuito de tráfico de salida (5 GB al mes). La causa principal era
esta exportación: bajaba la tabla de carreras entera (unos 60 MB) en cada publicación del portal, y el portal se publica dos veces
al día y con cada cambio de univ/gen (hasta 14 veces en un día). Ahora:
  - Antes de bajar nada mira una huella barata de cada tabla (número de filas, último id y última fecha). Si no cambió desde la
    última exportación, usa la copia guardada en univ/data y no baja nada.
  - Una vez a la semana (lunes) baja todo igualmente, por si alguien editó una fila sin cambiar la huella.
  - Pide los datos comprimidos (gzip): el mismo contenido ocupa unas 8 veces menos.
FORZAR=1 baja todo siempre."""
import json, gzip, urllib.request, os, time, datetime
U = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
K = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
D = 'univ/data'
F_HUELLAS = os.path.join(D, 'sb_huellas.json')
CAB = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Accept-Encoding': 'gzip'}
FECHAS = {'universidades': 'actualizado', 'carreras': 'created_at'}


def pedir(url, extra=None):
    for t in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=dict(CAB, **(extra or {}))), timeout=60) as r:
                b = r.read()
                if r.headers.get('Content-Encoding') == 'gzip': b = gzip.decompress(b)
                return json.loads(b), r.headers
        except Exception as e:
            print('reintento', url[:80], e); time.sleep(3 + 3 * t)
    raise SystemExit('No pude leer ' + url[:80])


def huella(tabla):
    """Filas, último id y última fecha: unos pocos bytes en vez de la tabla entera."""
    _, h = pedir(f'{U}{tabla}?select=id&limit=1', {'Prefer': 'count=exact'})
    ult, _ = pedir(f'{U}{tabla}?select=id&order=id.desc&limit=1')
    f = FECHAS[tabla]
    fec, _ = pedir(f'{U}{tabla}?select={f}&order={f}.desc.nullslast&limit=1')
    return {'filas': h.get('Content-Range', '*/0').split('/')[-1], 'ultimo_id': ult[0]['id'] if ult else None, 'ultima_fecha': fec[0][f] if fec else None}


def todo(tabla, orden='id'):
    out, i, n = [], 0, 1000
    while True:
        lote, _ = pedir(f'{U}{tabla}?select=*&order={orden}', {'Range-Unit': 'items', 'Range': f'{i}-{i+n-1}'})
        out += lote; print(tabla, len(out), flush=True)
        if len(lote) < n: return out
        i += n


os.makedirs(D, exist_ok=True)
previas = json.load(open(F_HUELLAS, encoding='utf-8')) if os.path.exists(F_HUELLAS) else {}
semanal = datetime.date.today().weekday() == 0
forzar = os.environ.get('FORZAR') == '1'
for t in ['universidades', 'carreras']:
    h = huella(t)
    archivo = f'{D}/sb_{t}.json.gz'
    if not forzar and os.path.exists(archivo) and previas.get(t, {}).get('huella') == h and not (semanal and previas.get(t, {}).get('fecha') != str(datetime.date.today())):
        print(f'{t}: sin cambios desde {previas[t].get("fecha")} ({h["filas"]} filas), se usa la copia guardada')
        continue
    d = todo(t)
    # sin fecha dentro del .gz y con orden fijo: si los datos no cambian, el archivo es idéntico y no se guarda otra copia
    # (19/11/2026: cada exportación guardaba 9 MB nuevos en el historial aunque nada hubiera cambiado)
    with open(archivo, 'wb') as fb, gzip.GzipFile(fileobj=fb, mode='wb', mtime=0, filename='') as g:
        g.write(json.dumps(d, ensure_ascii=False, sort_keys=True).encode('utf-8'))
    previas[t] = {'huella': h, 'fecha': str(datetime.date.today())}
    print('OK', t, len(d))
json.dump(previas, open(F_HUELLAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
