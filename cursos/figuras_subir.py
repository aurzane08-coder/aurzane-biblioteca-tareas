"""Figuras reales (OpenStax, CC BY 4.0) para los cursos: descarga, convierte a webp y sube a learn.aurzane.com/cursos/img/.
Entrada: cursos/figuras-<curso>.json con [{clave, src}]. Salida: cursos/figuras-<curso>-tam.json con {clave: {w, h}}.
Solo sube las que faltan en el servidor. Entradas de entorno: SSH, SG_DEST, LISTA.
"""
import json, os, io, sys, time, subprocess, tarfile, urllib.request
from PIL import Image
LISTA = os.environ.get('LISTA', 'cursos/figuras-psi.json')
SSH = os.environ['SSH'].split(); DEST = os.environ['SG_DEST']
RUTA = 'www/learn.aurzane.com/public_html/cursos/img'
sal = LISTA.replace('.json', '-tam.json')
tam = json.load(open(sal)) if os.path.exists(sal) else {}
hay = set(subprocess.run(SSH + [DEST, f'mkdir -p {RUTA} && ls {RUTA}'], capture_output=True, text=True).stdout.split())
buf = io.BytesIO(); tar = tarfile.open(fileobj=buf, mode='w'); nuevas = 0; fallos = []
for f in json.load(open(LISTA)):
    nombre = f"{f['clave']}.webp"
    if nombre in hay and f['clave'] in tam: continue
    try:
        datos = None
        for intento, url in enumerate([f['src'], f['src'] + '?revision=1', f['src'], f['src'] + '?origin=mt-web']):
            try:
                rq = urllib.request.Request(url, headers={'User-Agent': 'AURZANE-cursos/1.0 (aurzane.com)'})
                datos = urllib.request.urlopen(rq, timeout=150).read(); break
            except Exception as e:
                print('reintento', f['clave'], intento, e); time.sleep(5 + 5 * intento)
        if datos is None: raise RuntimeError('sin respuesta del servidor de origen')
        im = Image.open(io.BytesIO(datos))
        im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
        if im.mode == 'RGBA':
            fondo = Image.new('RGB', im.size, 'white'); fondo.paste(im, mask=im.split()[3]); im = fondo
        if im.width > 1400: im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'WEBP', quality=82); d = b.getvalue()
        ti = tarfile.TarInfo(nombre); ti.size = len(d); tar.addfile(ti, io.BytesIO(d))
        tam[f['clave']] = {'w': im.width, 'h': im.height}; nuevas += 1
    except Exception as e:
        fallos.append(f['clave']); print('fallo', f['clave'], e)
    time.sleep(0.4)
tar.close()
if nuevas:
    r = subprocess.run(SSH + [DEST, f'tar -xf - -C {RUTA} && echo OK'], input=buf.getvalue(), capture_output=True)
    print('subidas', nuevas, r.stdout.decode().strip(), r.stderr.decode()[:300])
json.dump(tam, open(sal, 'w'), indent=0)
print(f'::notice title=Figuras::{len(tam)} figuras listas, {nuevas} nuevas, {len(fallos)} fallos')
