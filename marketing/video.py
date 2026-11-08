# Vídeos verticales 1080x1920 (Reels, Shorts, TikTok) hechos solos:
# fondo = vídeo de Pexels (licencia Pexels: uso comercial gratis), encima la frase o el producto con la marca.
# Uso: python3 marketing/video.py generar  (lo llama el flujo después de planificar)
import json, os, re, sys, hashlib, subprocess, urllib.request, urllib.parse, datetime
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import mk

DUR = {'frase': 12, 'curiosidad': 14}
V = 'm1-'  # versión de los vídeos: m1 = con música de fondo
# Música de fondo: Kevin MacLeod (incompetech.com), licencia CC BY 4.0. Uso comercial y monetización permitidos citando el tema,
# por eso cada publicación de vídeo lleva el crédito (mk.credito_musica). Calma para frases, más alegre para tests y calculadoras.
MUSICA_CALMA = ['Meditation Impromptu 01', 'Meditation Impromptu 02', 'Meditation Impromptu 03', 'Peaceful Desolation', 'Healing', 'Dreamer',
                'Clean Soul', 'Floating Cities', 'Lasting Hope', 'Relaxing Piano Music', 'Touching Moments Two - Higher', 'Fireflies and Stardust',
                'Heartwarming', 'Perspectives', 'Sincerely']
MUSICA_ALEGRE = ['Carefree', 'Easy Lemon', 'Wholesome', 'Inspired', 'Amazing Plan', 'Dreamer', 'Heartwarming']


def musica_de(p):
    lista = MUSICA_CALMA if p['tipo'] in ('frase', 'curiosidad') else MUSICA_ALEGRE
    return lista[int(hashlib.md5((p['id'] + 'm').encode()).hexdigest(), 16) % len(lista)]


# Variedad: cada vídeo elige un estilo distinto (rotando por día y por publicación) y nunca repite un tema reciente.
ESTILOS_CALMA = ['indie+acoustic', 'piano+melancholic', 'dreampop', 'lofi+chill', 'cinematic+emotional', 'folk+acoustic', 'ambient+piano',
                 'singer+songwriter', 'soft+pop', 'chillout', 'neoclassical', 'indie+folk']
ESTILOS_ALEGRE = ['indie+pop', 'upbeat+pop', 'electropop', 'funk+groove', 'happy+acoustic', 'synthpop', 'pop+rock', 'tropical+house', 'feelgood']
BANCO = 'musica_banco.json'   # temas ya usados que se guardan en aurzane.com/marketing/musica/ como reserva si Jamendo falla


def jamendo(p):
    """Si hay JAMENDO_CLIENT_ID, elige un tema CC BY o CC BY-SA (sin NC ni ND: se puede usar en vídeos monetizados citando al autor),
    de un estilo distinto cada vez y sin repetir los últimos 80. Devuelve (ruta_mp3, crédito, id) o None."""
    cid = os.environ.get('JAMENDO_CLIENT_ID', '').strip()
    if not cid: return None
    calma = p['tipo'] in ('frase', 'curiosidad')
    h = int(hashlib.md5((p['id'] + mk.HOY.isoformat()).encode()).hexdigest(), 16)
    estilos = ESTILOS_CALMA if calma else ESTILOS_ALEGRE
    usados = set(mk.leer('musica_ids.json', [])[-80:])
    for k in range(3):
        tags = estilos[(h + k) % len(estilos)]
        try:
            q = {'client_id': cid, 'format': 'json', 'limit': 80, 'fuzzytags': tags, 'include': 'licenses musicinfo', 'audioformat': 'mp32', 'ccnc': 'false',
                 'order': ['popularity_month', 'popularity_week', 'popularity_total'][(h + k) % 3], 'audiodlformat': 'mp32'}
            if (h >> 3) % 3 == 0: q['vocalinstrumental'] = 'instrumental'
            res = json.load(urllib.request.urlopen('https://api.jamendo.com/v3.0/tracks/?' + urllib.parse.urlencode(q), timeout=60)).get('results', [])
            res = [t for t in res if t.get('audiodownload_allowed', True) and (t.get('audiodownload') or t.get('audio')) and str(t['id']) not in usados
                   and 'creativecommons.org/licenses/by' in (t.get('license_ccurl') or '') and '-nc' not in t['license_ccurl'] and '-nd' not in t['license_ccurl']
                   and 60 <= int(t.get('duration') or 0) <= 420]
            if not res: continue
            t = res[(h >> 5) % len(res)]
            dest = f'/tmp/jamendo-{t["id"]}.mp3'
            open(dest, 'wb').write(urllib.request.urlopen(urllib.request.Request(t.get('audiodownload') or t['audio'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=120).read())
            lic = re.search(r'licenses/([a-z-]+)/', t.get('license_ccurl') or ''); lic = ('CC ' + lic.group(1).upper()) if lic else 'Creative Commons'
            cred = f'«{t["name"]}», {t["artist_name"]} (Jamendo), {lic}'
            ids = mk.leer('musica_ids.json', []); ids.append(str(t['id'])); mk.guardar('musica_ids.json', ids[-300:])
            banco = mk.leer(BANCO, [])
            if len(banco) < 120 and str(t['id']) not in {b_['id'] for b_ in banco}:   # se guarda como reserva (se sube al servidor en el flujo)
                os.makedirs(os.path.join(D, 'salida', 'musica'), exist_ok=True)
                import shutil; shutil.copy(dest, os.path.join(D, 'salida', 'musica', f'{t["id"]}.mp3'))
                banco.append({'id': str(t['id']), 'credito': cred, 'calma': calma, 'estilo': tags}); mk.guardar(BANCO, banco)
            return dest, cred, str(t['id'])
        except Exception as e:
            print('::notice title=Videos::Jamendo no disponible', str(e)[:120])
    return None


def de_banco(p):
    """Reserva: un tema del banco propio (aurzane.com/marketing/musica/), distinto de los últimos usados."""
    calma = p['tipo'] in ('frase', 'curiosidad')
    banco = [b_ for b_ in mk.leer(BANCO, []) if b_['calma'] == calma] or mk.leer(BANCO, [])
    if not banco: return None
    usados = mk.leer('musica_ids.json', [])[-40:]
    libres = [b_ for b_ in banco if b_['id'] not in usados] or banco
    b_ = libres[int(hashlib.md5((p['id'] + 'b').encode()).hexdigest(), 16) % len(libres)]
    dest = f'/tmp/banco-{b_["id"]}.mp3'
    try:
        if not os.path.exists(dest):
            open(dest, 'wb').write(urllib.request.urlopen(urllib.request.Request(mk.SITIO_IMG + f'musica/{b_["id"]}.mp3', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/130.0 Safari/537.36'}), timeout=120).read())
        return dest, b_['credito'], b_['id']
    except Exception as e:
        print('::notice title=Videos::banco de música no disponible', str(e)[:100]); return None


def elegir_musica(p):
    """Jamendo (variado) → banco propio → Kevin MacLeod como último recurso."""
    r = jamendo(p) or de_banco(p)
    if r: return r[0], r[1]
    return bajar_musica(musica_de(p)), f'«{musica_de(p)}», Kevin MacLeod (incompetech.com), CC BY 4.0'


def credito(p):
    """Crédito de la música del vídeo de p (lo guarda generar en musica_usada.json)."""
    c = mk.leer('musica_usada.json', {}).get(p['id'])
    return c or f'«{musica_de(p)}», Kevin MacLeod (incompetech.com), CC BY 4.0'


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
    if os.environ.get('PIXABAY_KEY') and int(hashlib.md5((p['id'] + 'px').encode()).hexdigest(), 16) % 2 == 0:
        q0 = VQ.get(p['id']) or (NATURALEZA[int(hashlib.md5(p['id'].encode()).hexdigest(), 16) % len(NATURALEZA)] if p['tipo'] in ('frase', 'curiosidad') else 'calm nature')
        u = pixabay(q0, p['id'])
        if u: return u
    lib = mk.leer('biblioteca_videos.json', {})
    q = VQ.get(p['id']) or (NATURALEZA[int(hashlib.md5(p['id'].encode()).hexdigest(), 16) % len(NATURALEZA)] if p['tipo'] in ('frase', 'curiosidad') else 'calm nature')
    lista = lib.get(q) or lib['calm nature']
    return lista[int(hashlib.md5((p['id'] + 'v').encode()).hexdigest(), 16) % len(lista)]


def pixabay(q, semilla):
    """Si hay PIXABAY_KEY, busca un vídeo de fondo en Pixabay (licencia de Pixabay: uso comercial gratis, sin atribución obligatoria).
    Prefiere vídeos verticales y de calidad media. Devuelve la URL o None."""
    k = os.environ.get('PIXABAY_KEY', '').strip()
    if not k: return None
    try:
        u = 'https://pixabay.com/api/videos/?' + urllib.parse.urlencode({'key': k, 'q': q, 'per_page': 50, 'safesearch': 'true', 'video_type': 'film'})
        hits = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60)).get('hits', [])
        cands = []
        for h in hits:
            v = h.get('videos', {}); m = v.get('medium') or v.get('small') or {}
            if m.get('url') and 8 <= h.get('duration', 0) <= 60: cands.append((m.get('height', 0) > m.get('width', 1), m['url']))
        vert = [u for e, u in cands if e]; lista = vert or [u for _, u in cands]
        return lista[int(hashlib.md5(semilla.encode()).hexdigest(), 16) % len(lista)] if lista else None
    except Exception as e:
        print('::notice title=Videos::Pixabay no disponible', str(e)[:100]); return None


def capa_de(p):
    if p['tipo'] == 'frase':
        return dict(titulo=p['titulo'], cita=True, autor='' if p.get('autor') == 'AURZANE' else p.get('autor'), pie='aurzane.com · psicología y bienestar')
    if p['tipo'] == 'curiosidad':
        return dict(kicker='¿Sabías que…?', titulo=p['titulo'], sub=mk.recorta(p.get('dato') or p['texto'], 150), pie='aurzane.com · psicología')
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
    ids = sorted({i for d in range(dias) for i in est['calendario'].get((hoy + datetime.timedelta(days=d)).isoformat(), {}).get('4', {}).values()} | {i for d in range(dias) for i in est['calendario'].get((hoy + datetime.timedelta(days=d)).isoformat(), {}).get('5', {}).values()})
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
        mus, cred = elegir_musica(p)
        usada = mk.leer('musica_usada.json', {}); usada[i] = cred; mk.guardar('musica_usada.json', usada)
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


def generar_imagenes(dias=2):
    """Las publicaciones de imagen de Instagram y Facebook salen como Reel de 9 s con música: la imagen con un zoom lento
    sobre su propio fondo desenfocado. Se preparan con 2 días de margen para que ya estén en aurzane.com al publicar."""
    cat = {p['id']: p for p in mk.leer('catalogo.json')['productos']}
    est = mk.leer('estado.json'); hoy = mk.HOY
    ids = sorted({x[r] for d in range(dias) for fr, x in est['calendario'].get((hoy + datetime.timedelta(days=d)).isoformat(), {}).items() if fr not in ('4', '5')
                  for r in ('instagram', 'facebook') if r in x})
    hechos = 0
    for i in ids:
        if i not in cat or hechos >= 8: continue
        p = cat[i]; nombre = V + 'img-' + i
        try:
            urllib.request.urlopen(urllib.request.Request(mk.SITIO_IMG + f'video/{nombre}.mp4', method='HEAD'), timeout=20); continue
        except Exception: pass
        img = os.path.join(D, mk.imagen_de(p))
        if not os.path.exists(img):
            try: os.makedirs(os.path.dirname(img), exist_ok=True); urllib.request.urlretrieve(mk.SITIO_IMG + mk.imagen_de(p), img)
            except Exception as e: print('::notice title=Videos::sin imagen', i, e); continue
        mus, cred = elegir_musica(p)
        usada = mk.leer('musica_usada.json', {}); usada['img-' + i] = cred; mk.guardar('musica_usada.json', usada)
        sal = os.path.join(D, 'salida', 'video', nombre + '.mp4'); os.makedirs(os.path.dirname(sal), exist_ok=True)
        dur = 9
        filtro = ('[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:2,eq=brightness=-0.12[bg];'
                  f"[0:v]scale=1000:-2,zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur * 30}:s=1000x1250:fps=30[fg];"
                  '[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]')
        audio_in = ['-ss', str(3 + int(hashlib.md5(i.encode()).hexdigest(), 16) % 20), '-i', mus] if mus else ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']
        filtro += f';[1:a]volume=0.6,afade=t=in:st=0:d=1,afade=t=out:st={dur - 2}:d=2[a]'
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', img] + audio_in + ['-filter_complex', filtro, '-map', '[v]', '-map', '[a]',
               '-t', str(dur), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-movflags', '+faststart', sal]
        r = subprocess.run(cmd); hechos += 1
        print('::notice title=Videos::Reel de imagen', i, 'ok' if r.returncode == 0 else 'ERROR')


if __name__ == '__main__':
    try:
        generar_imagenes()
    except Exception as e:
        import traceback; print('::notice title=Videos::ERROR imágenes', repr(e)[:300]); traceback.print_exc()
    try:
        generar()
    except Exception as e:
        import traceback; print('::notice title=Videos::ERROR', repr(e)[:300]); traceback.print_exc()
