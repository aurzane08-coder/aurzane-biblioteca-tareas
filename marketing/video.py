# Vídeos verticales 1080x1920 (Reels, Shorts, TikTok) hechos solos:
# fondo = vídeo de Pexels (licencia Pexels: uso comercial gratis), encima la frase o el producto con la marca.
# Uso: python3 marketing/video.py generar  (lo llama el flujo después de planificar)
import json, os, sys, hashlib, subprocess, urllib.request, urllib.parse, datetime
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import mk

DUR = {'frase': 12}
V = 'm1-'  # versión de los vídeos: m1 = con música de fondo
# Música de fondo: Kevin MacLeod (incompetech.com), licencia CC BY 4.0. Uso comercial y monetización permitidos citando el tema,
# por eso cada publicación de vídeo lleva el crédito (mk.credito_musica). Calma para frases, más alegre para tests y calculadoras.
MUSICA_CALMA = ['Meditation Impromptu 01', 'Meditation Impromptu 02', 'Meditation Impromptu 03', 'Peaceful Desolation', 'Healing', 'Dreamer',
                'Clean Soul', 'Floating Cities', 'Lasting Hope', 'Relaxing Piano Music', 'Touching Moments Two - Higher', 'Fireflies and Stardust',
                'Heartwarming', 'Perspectives', 'Sincerely']
MUSICA_ALEGRE = ['Carefree', 'Easy Lemon', 'Wholesome', 'Inspired', 'Amazing Plan', 'Dreamer', 'Heartwarming']


def musica_de(p):
    lista = MUSICA_CALMA if p['tipo'] == 'frase' else MUSICA_ALEGRE
    return lista[int(hashlib.md5((p['id'] + 'm').encode()).hexdigest(), 16) % len(lista)]


def bajar_musica(nombre):
    dest = '/tmp/musica-' + hashlib.md5(nombre.encode()).hexdigest()[:8] + '.mp3'
    if not os.path.exists(dest):
        try:
            u = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/' + urllib.parse.quote(nombre) + '.mp3'
            open(dest, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/130.0 Safari/537.36'}), timeout=120).read())
        except Exception as e:
            print('::notice title=Videos::sin música', nombre, e); return ''
    return dest
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
        r = urllib.request.urlopen(urllib.request.Request(mk.SITIO_IMG + f'video/{V}{i}.mp4', method='HEAD'), timeout=20)
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
            req = urllib.request.Request(fondo(p), headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
                                                             'Referer': 'https://www.pexels.com/', 'Accept': 'video/mp4,*/*'})
            open(src, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
        except Exception as e:
            print('::notice title=Videos::sin fondo', i, e); continue
        sal = os.path.join(D, 'salida', 'video', V + i + '.mp4')
        mus = bajar_musica(musica_de(p))
        filtro = ('[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,eq=brightness=-0.05:saturation=1.05[b];'
                  '[1:v]format=rgba,fade=in:st=0.3:d=0.9:alpha=1[c];[b][c]overlay=0:0,format=yuv420p[v]')
        if mus:
            audio_in = ['-ss', str(3 + int(hashlib.md5(i.encode()).hexdigest(), 16) % 20), '-i', mus]
            filtro += f';[2:a]volume=0.55,afade=t=in:st=0:d=1.2,afade=t=out:st={dur - 2.5}:d=2.5[a]'; amap = '[a]'
        else:
            audio_in = ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']; amap = '2:a'
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-i', src, '-loop', '1', '-i', f'/tmp/capa-{i}.png'] + audio_in + [
               '-filter_complex', filtro, '-map', '[v]', '-map', amap,
               '-t', str(dur), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
               '-movflags', '+faststart', sal]
        r = subprocess.run(cmd)
        print('::notice title=Videos::', i, 'ok' if r.returncode == 0 else 'ERROR', round(os.path.getsize(sal) / 1e6, 1) if os.path.exists(sal) else '', 'MB')


if __name__ == '__main__':
    try:
        generar()
    except Exception as e:
        import traceback; print('::notice title=Videos::ERROR', repr(e)[:300]); traceback.print_exc()
