# Vídeos verticales 1080x1920 (Reels, Shorts, TikTok) hechos solos:
# fondo = vídeo de Pexels (licencia Pexels: uso comercial gratis), encima la frase o el producto con la marca.
# Uso: python3 marketing/video.py generar  (lo llama el flujo después de planificar)
import json, os, sys, hashlib, subprocess, urllib.request, datetime
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import mk

DUR = {'frase': 12}
VQ = {  # producto -> ambiente del vídeo de fondo
    'test-sueno': 'starry night', 'test-ansiedad': 'woman meditating', 'test-depresion': 'rain window', 'test-bienestar': 'sunrise sky',
    'test-autoestima': 'flowers field', 'test-tdah': 'writing notebook', 'test-autocompasion': 'candle light', 'test-satisfaccion': 'sunrise sky',
    'test-habitos': 'running sunrise', 'test-personalidad': 'person walking nature', 'calc-calorias': 'coffee morning', 'calc-embarazo': 'flowers field',
    'calc-hipoteca': 'city lights night', 'calc-sueldo': 'coffee morning', 'calc-reforma': 'city lights night', 'calc-pau': 'student studying',
    'ovp': 'university campus', 'curso-neuro': 'brain', 'curso-metod': 'laboratory',
}
NATURALEZA = ['calm nature', 'ocean waves', 'forest light', 'sunrise sky', 'clouds timelapse', 'mountains mist', 'flowers field',
              'starry night', 'autumn leaves', 'snow falling', 'rain window', 'candle light']


def fondo(p):
    lib = mk.leer('biblioteca_videos.json', {})
    q = VQ.get(p['id']) or (NATURALEZA[int(hashlib.md5(p['id'].encode()).hexdigest(), 16) % len(NATURALEZA)] if p['tipo'] == 'frase' else 'calm nature')
    lista = lib.get(q) or lib['calm nature']
    return lista[int(hashlib.md5((p['id'] + 'v').encode()).hexdigest(), 16) % len(lista)]


def capa_de(p):
    if p['tipo'] == 'frase':
        return dict(titulo=p['titulo'], cita=True, autor='' if p.get('autor') == 'AURZANE' else p.get('autor'), pie='aurzane.com · psicología y bienestar')
    kick = {'test': 'Test gratis', 'calculadora': 'Calculadora gratis', 'curso': 'Curso gratis'}.get(p['tipo'], 'Gratis')
    return dict(kicker=kick, titulo=p['ganchos'][0], sub=mk.recorta(p['texto'], 120), pie=mk.pie_de(p['url']))


def existe_en_web(i):
    try:
        r = urllib.request.urlopen(urllib.request.Request(mk.SITIO_IMG + f'video/{i}.mp4', method='HEAD'), timeout=20)
        return r.status == 200
    except Exception:
        return False


def generar(dias=2):
    cat = {p['id']: p for p in mk.leer('catalogo.json')['productos']}
    est = mk.leer('estado.json')
    hoy = mk.HOY
    ids = sorted({i for d in range(dias) for i in est['calendario'].get((hoy + datetime.timedelta(days=d)).isoformat(), {}).get('4', {}).values()})
    os.makedirs(os.path.join(D, 'salida', 'video'), exist_ok=True)
    capas, pend = [], []
    for i in ids:
        if i not in cat or existe_en_web(i): continue
        p = cat[i]
        capas.append(dict(capa_de(p), id=i, capa=True, mundo=p['mundo'], salida=f'/tmp/capa-{i}.png'))
        pend.append(p)
    if not pend:
        print('::notice title=Videos::nada nuevo', ids); return
    json.dump(capas, open('/tmp/capas.json', 'w'), ensure_ascii=False)
    subprocess.run(['node', os.path.join(D, 'tarjeta.js'), '/tmp/capas.json', os.environ.get('FUENTES', '/tmp/f/node_modules/@fontsource')], check=True)
    for p in pend:
        i = p['id']; dur = DUR.get(p['tipo'], 15)
        src = f'/tmp/fondo-{i}.mp4'
        try:
            urllib.request.urlretrieve(fondo(p), src)
        except Exception as e:
            print('::notice title=Videos::sin fondo', i, e); continue
        sal = os.path.join(D, 'salida', 'video', i + '.mp4')
        filtro = ('[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,eq=brightness=-0.05:saturation=1.05[b];'
                  '[1:v]format=rgba,fade=in:st=0.3:d=0.9:alpha=1[c];[b][c]overlay=0:0,format=yuv420p[v]')
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-i', src, '-loop', '1', '-i', f'/tmp/capa-{i}.png',
               '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-filter_complex', filtro, '-map', '[v]', '-map', '2:a',
               '-t', str(dur), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '96k',
               '-movflags', '+faststart', sal]
        r = subprocess.run(cmd)
        print('::notice title=Videos::', i, 'ok' if r.returncode == 0 else 'ERROR', round(os.path.getsize(sal) / 1e6, 1) if os.path.exists(sal) else '', 'MB')


if __name__ == '__main__':
    try:
        generar()
    except Exception as e:
        import traceback; print('::notice title=Videos::ERROR', repr(e)[:300]); traceback.print_exc()
