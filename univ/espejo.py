"""Fotos de universidades en nuestro servidor (22/11/2026, pedido de Adrián): cada foto de Wikimedia Commons que usa el catálogo
(campus, ciudad y logos en mapa de bits) se descarga una vez en tamaños estándar, se convierte a AVIF (330 y 960 px de ancho)
y se guarda en salida/<hash>-330.avif / -960.avif. Índice univ/data/espejo.json {archivo de Commons: hash}.
Las licencias de Commons permiten copiarlas; la ficha de cada universidad mantiene el crédito a Wikimedia Commons.
Uso: python3 univ/espejo.py salida/ [LOTE]"""
import os, sys, io, json, time, hashlib, urllib.request, urllib.parse
from PIL import Image

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
sal = sys.argv[1]; LOTE = int(sys.argv[2]) if len(sys.argv) > 2 else 600
img = json.load(open(os.path.join(D, 'imagenes.json'), encoding='utf-8'))
esp_p = os.path.join(D, 'espejo.json')
esp = json.load(open(esp_p, encoding='utf-8')) if os.path.exists(esp_p) else {}
fall_p = os.path.join(D, 'espejo-fallos.json')
fall = json.load(open(fall_p, encoding='utf-8')) if os.path.exists(fall_p) else {}

archivos = []
for pais, lista in img.get('u', {}).items():
    for r in lista:
        for f in (r[2] if len(r) > 2 else '', r[3] if len(r) > 3 else ''):
            if f and not f.lower().endswith('.svg'): archivos.append(f)
for pais, cs in img.get('c', {}).items():
    for f in cs.values():
        if f and not f.lower().endswith('.svg'): archivos.append(f)
archivos = list(dict.fromkeys(archivos))
pend = [f for f in archivos if f not in esp and fall.get(f, 0) < 3]
print(f'Fotos en el catálogo: {len(archivos)} · ya en el servidor: {len(esp)} · pendientes: {len(pend)}')
os.makedirs(sal, exist_ok=True)
hechas = 0
for f in pend[:LOTE]:
    u = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(f.replace(' ', '_')) + '?width=960'
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AURZANE universidades (https://nexus.aurzane.com/universidades/; bot@aurzane.com)'}), timeout=60).read()
        im = Image.open(io.BytesIO(b)); im.load()
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        h = hashlib.sha1(f.encode()).hexdigest()[:16]
        for w in (960, 330):
            x = im.copy(); x.thumbnail((w, w * 3)); x.save(os.path.join(sal, f'{h}-{w}.avif'), 'AVIF', quality=50, speed=6)
        esp[f] = h; hechas += 1
    except Exception as e:
        fall[f] = fall.get(f, 0) + 1; print('  no se pudo', f[:70], str(e)[:80])
    time.sleep(0.6)   # sin saturar a Wikimedia
json.dump(esp, open(esp_p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(fall, open(fall_p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'Guardadas ahora: {hechas} · en total: {len(esp)} de {len(archivos)}')
