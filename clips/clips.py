# -*- coding: utf-8 -*-
"""Fábrica de clips (canal Clips-All de YouTube y cuenta de clips de TikTok). Todo gratis en GitHub Actions.

Solo trabaja con vídeos AUTORIZADOS: los que aparecen en clips/fuentes.json, que deben venir de una campaña de clipping
(Clipeamos, Whop, Vyro…) o de un creador que lo permite por escrito. Nunca recorta contenido sin permiso.

Para cada vídeo fuente pendiente:
 1. lo descarga (yt-dlp), 2. lo transcribe con Whisper (faster-whisper, en el propio runner),
 3. Gemini elige los mejores momentos (20 a 55 s, con gancho al inicio), 4. ffmpeg los corta en vertical 1080x1920 con fondo
 desenfocado y subtítulos grandes, 5. los sube a YouTube (Shorts) y a TikTok, respetando el cupo diario.
Registro: clips/hechos.json (qué clip salió, dónde y con qué enlace) para declarar las vistas en la campaña.

Secretos: GEMINI_API_KEY, CLIPS_YT_CLIENT_ID, CLIPS_YT_CLIENT_SECRET, CLIPS_YT_REFRESH_TOKEN (canal Clips-All),
          TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, CLIPS_TIKTOK_REFRESH_TOKEN (cuenta de clips; opcional)."""
import json, os, re, subprocess, time, hashlib, urllib.request, urllib.parse, datetime

D = os.path.dirname(os.path.abspath(__file__))
E = lambda k: os.environ.get(k, '').strip()
HOY = datetime.date.today().isoformat()
MAX_DIA = int(E('CLIPS_MAX_DIA') or '3')            # 3 clips al día, uno por pasada (mañana, tarde y noche)
POR_PASADA = int(E('CLIPS_POR_PASADA') or '1')          # el cupo gratis de la API de YouTube da para unas 6 subidas al día por proyecto
def leer(n, d):
    try: return json.load(open(os.path.join(D, n), encoding='utf-8'))
    except Exception: return d
def guardar(n, v): json.dump(v, open(os.path.join(D, n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
def pedir(url, datos=None, cab=None, metodo=None, crudo=None, t=60):
    h = {'User-Agent': 'AurzaneClips/1.0'}; h.update(cab or {})
    if crudo is not None: cuerpo = crudo
    elif datos is not None and h.get('Content-Type', '').startswith('application/json'): cuerpo = json.dumps(datos).encode()
    elif datos is not None: cuerpo = urllib.parse.urlencode(datos).encode()
    else: cuerpo = None
    r = urllib.request.urlopen(urllib.request.Request(url, data=cuerpo, headers=h, method=metodo), timeout=t)
    b = r.read(); return json.loads(b) if b[:1] in (b'{', b'[') else {'_cabeceras': dict(r.headers)}

def gemini(prompt):
    cuerpo = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.4, 'maxOutputTokens': 8192}}).encode()
    for m in ('gemini-flash-latest', 'gemini-flash-lite-latest'):
        try:
            r = pedir(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', crudo=cuerpo,
                      cab={'Content-Type': 'application/json', 'x-goog-api-key': E('GEMINI_API_KEY')}, t=120)
            t = ''.join(x.get('text', '') for x in r['candidates'][0]['content']['parts'])
            if t.strip(): return t
        except Exception as e: print('gemini', m, str(e)[:120]); time.sleep(5)
    for m in ('openai/gpt-4.1-mini', 'openai/gpt-4o-mini'):   # respaldo gratuito: modelos de GitHub con el token del flujo
        try:
            r = pedir('https://models.github.ai/inference/chat/completions', crudo=json.dumps({'model': m, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.4, 'max_tokens': 4000}).encode(),
                      cab={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + E('GITHUB_TOKEN')}, t=120)
            t = r['choices'][0]['message']['content']
            if t.strip(): print('IA de respaldo:', m); return t
        except Exception as e: print('respaldo', m, str(e)[:120])
    return ''

def transcribir(video):
    from faster_whisper import WhisperModel
    modelo = WhisperModel(E('WHISPER') or 'base', device='cpu', compute_type='int8')
    import numpy as np   # el audio se decodifica con ffmpeg (evita incompatibilidades de PyAV)
    pcm = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', video, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segs, info = modelo.transcribe(audio, vad_filter=True, word_timestamps=True, language=E('IDIOMA') or 'es')
    out = []
    for s in segs:
        out.append({'i': round(s.start, 2), 'f': round(s.end, 2), 't': s.text.strip(), 'w': [(round(w.start, 2), round(w.end, 2), w.word) for w in (s.words or [])]})
    return out, info.language

def elegir_momentos(segs, fuente, n):
    texto = '\n'.join(f'[{s["i"]:.1f}-{s["f"]:.1f}] {s["t"]}' for s in segs)[:60000]
    r = gemini(f'Eres editor de clips virales para TikTok y YouTube Shorts. Vídeo: «{fuente.get("titulo", "")}» de {fuente.get("creador", "")}. '
               f'Reglas de la campaña: {fuente.get("reglas", "ninguna especial")}. Protagonista que debe hablar en el clip: {fuente.get("protagonista", "el invitado principal")}. A partir de la transcripción con tiempos, elige los {n} mejores momentos '
               'que funcionen solos: empiezan con un gancho fuerte en los 2 primeros segundos, tienen una idea completa y duran entre 20 y 55 segundos. '
               'Evita insultos, temas sensibles sin contexto y cortes a mitad de frase. Responde SOLO un JSON: '
               '[{"inicio": segundos, "fin": segundos, "titulo": "<título corto y llamativo, sin clickbait falso>", "gancho": "<cartel de 3 a 7 palabras que despierte curiosidad>", "hashtags": ["<4 hashtags sin #>"]}]\n\n' + texto)
    try: return json.loads(re.search(r'\[.*\]', r, re.S).group(0))[:n]
    except Exception: return []

def ass_subtitulos(segs, ini, fin, ruta, gancho=''):
    """Subtítulos grandes por grupos de 3 palabras, centrados en el tercio inferior (estilo Shorts)."""
    palabras = [w for s in segs for w in s['w'] if w[0] >= ini - 0.05 and w[1] <= fin + 0.05]
    cab = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, '
           'Alignment, MarginV, Outline, Shadow\nStyle: S,DejaVu Sans,78,&H00FFFFFF,&H00000000,&H80000000,1,2,560,6,2\n'
           'Style: G,DejaVu Sans,64,&H0000E5FF,&H00000000,&HC0000000,1,8,260,5,3\n\n[Events]\nFormat: Layer, Start, End, Style, Text\n')
    ts = lambda x: f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'
    lineas = []
    for k in range(0, len(palabras), 3):
        g = palabras[k:k + 3]
        txt = ' '.join(w[2].strip() for w in g).upper().replace('{', '').replace('}', '')
        lineas.append(f'Dialogue: 0,{ts(g[0][0] - ini)},{ts(g[-1][1] - ini)},S,{txt}')
    if gancho:   # cartel de gancho arriba durante los primeros segundos (lo piden las campañas)
        g = re.sub(r'[{}]', '', gancho.upper())[:70]
        lineas.insert(0, f'Dialogue: 1,0:00:00.00,0:00:03.80,G,{g}')
    open(ruta, 'w', encoding='utf-8').write(cab + '\n'.join(lineas) + '\n')

def cortar(video, ini, fin, ass, sal, musica=None):
    filtro = ('[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[f];'
              '[b]scale=1080:-2[p];[f][p]overlay=(W-w)/2:(H-h)/2,ass=' + ass + '[v]')
    ent = ['-ss', str(ini), '-to', str(fin), '-i', video]
    if musica:   # música de fondo suave bajo la voz
        ent += ['-stream_loop', '-1', '-i', musica]
        filtro += f';[1:a]volume=0.10,afade=t=out:st={max(1, fin - ini - 2)}:d=2[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[au]'; amap = '[au]'
    else: amap = '0:a?'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ent + ['-filter_complex', filtro, '-map', '[v]', '-map', amap, '-shortest',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', sal], check=True)

BANCO = 'https://aurzane.com/marketing/musica/'
def musica_fondo(cid):
    """Pista CC BY tranquila del banco de AURZANE (Jamendo); devuelve (ruta, crédito)."""
    try:
        banco = [b for b in json.load(open(os.path.join(os.path.dirname(D), 'marketing', 'musica_banco.json'), encoding='utf-8')) if b.get('calma')]
        b = banco[int(hashlib.md5(cid.encode()).hexdigest(), 16) % len(banco)]
        ruta = f'/tmp/clips/m-{b["id"]}.mp3'
        if not os.path.exists(ruta):
            open(ruta, 'wb').write(urllib.request.urlopen(urllib.request.Request(BANCO + b['id'] + '.mp3', headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())
        return ruta, b.get('credito', '')
    except Exception as e:
        print('música', str(e)[:100]); return None, ''

def subir_youtube(ruta, titulo, desc, tags):
    tk = pedir('https://oauth2.googleapis.com/token', {'client_id': E('CLIPS_YT_CLIENT_ID') or E('YT_CLIENT_ID'), 'client_secret': E('CLIPS_YT_CLIENT_SECRET') or E('YT_CLIENT_SECRET'),
                                                        'refresh_token': E('CLIPS_YT_REFRESH_TOKEN'), 'grant_type': 'refresh_token'})['access_token']
    canal = (pedir('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true', cab={'Authorization': 'Bearer ' + tk}).get('items') or [{}])[0].get('snippet', {}).get('title', '')
    if not canal or 'aurzane' in canal.lower():   # identificador de destino: los clips nunca van al canal de AURZANE
        raise RuntimeError(f'El YouTube conectado para clips es «{canal or "desconocido"}», no Clips-All: vuelve a conectarlo en aurzane.com/youtube/')
    meta = {'snippet': {'title': (titulo[:90] + ' #Shorts'), 'description': desc[:4900], 'tags': tags[:10] + ['Shorts', 'clips'], 'categoryId': '24'},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
    datos = open(ruta, 'rb').read()
    req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', data=json.dumps(meta).encode(), method='POST',
                                 headers={'Authorization': 'Bearer ' + tk, 'Content-Type': 'application/json; charset=UTF-8', 'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(len(datos))})
    sesion = urllib.request.urlopen(req, timeout=60).headers['Location']
    r = pedir(sesion, crudo=datos, cab={'Authorization': 'Bearer ' + tk, 'Content-Type': 'video/mp4'}, metodo='PUT', t=600)
    return 'https://youtube.com/shorts/' + r['id'] + f' (canal «{canal}»)'

def subir_tiktok(ruta):
    rt = E('CLIPS_TIKTOK_REFRESH_TOKEN')
    r = pedir('https://open.tiktokapis.com/v2/oauth/token/', {'client_key': E('TIKTOK_CLIENT_KEY'), 'client_secret': E('TIKTOK_CLIENT_SECRET'), 'grant_type': 'refresh_token', 'refresh_token': rt})
    if r.get('refresh_token') and r['refresh_token'] != rt: open('/tmp/clips_tiktok_refresh', 'w').write(r['refresh_token'])
    cab = {'Authorization': 'Bearer ' + r['access_token'], 'Content-Type': 'application/json; charset=UTF-8'}
    # identificador fiable: el usuario (@...) de la cuenta, no el nombre visible (el de AURZANE es «🇪🇸Aur» y se colaba)
    nombre = pedir('https://open.tiktokapis.com/v2/post/publish/creator_info/query/', {}, cab).get('data', {}).get('creator_username', '')
    if 'clip' not in nombre.lower():
        raise RuntimeError(f'El TikTok conectado para clips es @{nombre}, no la cuenta de clips: conéctala con @clipsall16 en aurzane.com/tiktok/?inicio=1 (ventana privada)')
    datos = open(ruta, 'rb').read()
    ini = pedir('https://open.tiktokapis.com/v2/post/publish/inbox/video/init/', {'source_info': {'source': 'FILE_UPLOAD', 'video_size': len(datos), 'chunk_size': len(datos), 'total_chunk_count': 1}}, cab)['data']
    pedir(ini['upload_url'], crudo=datos, metodo='PUT', t=600, cab={'Content-Type': 'video/mp4', 'Content-Range': f'bytes 0-{len(datos) - 1}/{len(datos)}'})
    return ini['publish_id'] + f' (enviado a la bandeja de TikTok de @{nombre})'

def verificar_cuentas():
    """Solo comprueba a qué cuentas van los clips, sin subir nada."""
    try:
        tk = pedir('https://oauth2.googleapis.com/token', {'client_id': E('CLIPS_YT_CLIENT_ID') or E('YT_CLIENT_ID'), 'client_secret': E('CLIPS_YT_CLIENT_SECRET') or E('YT_CLIENT_SECRET'),
                                                            'refresh_token': E('CLIPS_YT_REFRESH_TOKEN'), 'grant_type': 'refresh_token'})['access_token']
        c = (pedir('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true', cab={'Authorization': 'Bearer ' + tk}).get('items') or [{}])[0].get('snippet', {}).get('title', '')
        print(f'::notice title=Clips::YouTube de clips: «{c}» ' + ('(correcto)' if c and 'aurzane' not in c.lower() else '(NO es Clips-All)'))
    except Exception as e: print('::notice title=Clips::YouTube de clips: error', str(e)[:150])
    try:
        rt = E('CLIPS_TIKTOK_REFRESH_TOKEN')
        r = pedir('https://open.tiktokapis.com/v2/oauth/token/', {'client_key': E('TIKTOK_CLIENT_KEY'), 'client_secret': E('TIKTOK_CLIENT_SECRET'), 'grant_type': 'refresh_token', 'refresh_token': rt})
        if r.get('refresh_token') and r['refresh_token'] != rt: open('/tmp/clips_tiktok_refresh', 'w').write(r['refresh_token'])
        u = pedir('https://open.tiktokapis.com/v2/post/publish/creator_info/query/', {}, {'Authorization': 'Bearer ' + r['access_token'], 'Content-Type': 'application/json; charset=UTF-8'}).get('data', {}).get('creator_username', '')
        print(f'::notice title=Clips::TikTok de clips: {"·".join(u)} ' + ('(correcto)' if 'clip' in u.lower() else '(NO es la cuenta de clips: hay que conectar @clipsall16)'))
    except Exception as e: print('::notice title=Clips::TikTok de clips: error', str(e)[:150])

def main():
    if os.environ.get('SOLO_VERIFICAR') == '1': return verificar_cuentas()
    fuentes = [f for f in leer('fuentes.json', []) if f.get('autorizado') is True and f.get('url')]
    hechos = leer('hechos.json', [])
    hoy_n = sum(1 for h in hechos if h.get('fecha') == HOY and h.get('youtube'))
    if not fuentes: print('::notice title=Clips::No hay vídeos autorizados en clips/fuentes.json'); return
    if not E('CLIPS_YT_REFRESH_TOKEN'): print('::notice title=Clips::Falta el secreto CLIPS_YT_REFRESH_TOKEN (permiso del canal Clips-All)')
    os.makedirs('/tmp/clips', exist_ok=True)
    nuevas_tr = 0; subidos = 0
    for f in fuentes:
        if hoy_n >= MAX_DIA or subidos >= POR_PASADA: break
        fid = hashlib.md5(f['url'].encode()).hexdigest()[:10]
        ya = [h for h in hechos if h['fuente'] == fid and (h.get('youtube') or h.get('tiktok'))]   # los que no se subieron se rehacen
        if len(ya) >= int(f.get('max_clips', 5)): continue
        video = f'/tmp/clips/{fid}.mp4'
        yt = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', f['url'])
        local = f'/tmp/material/{f.get("material") or (yt.group(1) if yt else "")}.mp4'
        if not os.path.exists(video) and local and os.path.exists(local): os.replace(local, video)   # descargado en el ordenador de Adrián (rama material-clips)
        if not os.path.exists(video) and f.get('archivo'):   # vídeo descargado en el ordenador de Adrián y subido a GitHub (YouTube bloquea los servidores)
            subprocess.run(['curl', '-sSL', '--fail', '-o', video, f['archivo']], check=False)
        if not os.path.exists(video):
            subprocess.run(['yt-dlp', '-f', 'bv*[height<=1080]+ba/b', '--merge-output-format', 'mp4', '-o', video, f['url']], check=False)
        if not os.path.exists(video): print('::warning title=Clips::no se pudo descargar', f['url']); continue
        cache = os.path.join(D, 'transcripciones', fid + '.json')
        if os.path.exists(cache): segs = json.load(open(cache, encoding='utf-8'))
        else:
            if nuevas_tr >= 1: continue   # una transcripción nueva por pasada para no pasar del tiempo límite
            nuevas_tr += 1
            segs, _ = transcribir(video); os.makedirs(os.path.dirname(cache), exist_ok=True); json.dump(segs, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
        usados = [(h['inicio'], h['fin']) for h in ya]
        if not (E('CLIPS_YT_REFRESH_TOKEN') or E('CLIPS_TIKTOK_REFRESH_TOKEN')):
            print('::notice title=Clips::Transcrito', f['titulo'][:60], '(se publicará cuando conectes Clips-All o TikTok)'); continue
        for m in elegir_momentos(segs, f, int(f.get('max_clips', 5)) - len(ya) + 2):
            if hoy_n >= MAX_DIA or subidos >= POR_PASADA or len(ya) >= int(f.get('max_clips', 5)): break
            ini, fin = float(m['inicio']), float(m['fin'])
            if not (15 <= fin - ini <= 60) or any(not (fin <= a or ini >= b) for a, b in usados): continue
            cid = f'{fid}-{int(ini)}'; sal = f'/tmp/clips/{cid}.mp4'; ass = f'/tmp/clips/{cid}.ass'
            ass_subtitulos(segs, ini, fin, ass, m.get('gancho') or m.get('titulo', ''))
            mus, cred = musica_fondo(cid) if f.get('musica', True) else (None, '')
            cortar(video, ini, fin, ass, sal, mus)
            desc = (m.get('titulo', '') + ' ' + f.get('mencion_tiktok', '') + '\n\nClip de ' + f.get('creador', '') + (' · Original: ' + f['original'] if f.get('original') else '') +
                    ('\n🎵 ' + cred if cred else '') + '\n' + ' '.join('#' + h for h in m.get('hashtags', [])[:4]) + ' #Shorts')
            m['titulo'] = (m.get('titulo', 'Clip')[:70] + ' ' + f.get('mencion_youtube', '')).strip()
            h = {'id': cid, 'fuente': fid, 'campana': f.get('campana', ''), 'inicio': ini, 'fin': fin, 'titulo': m.get('titulo', ''), 'fecha': HOY}
            if E('CLIPS_YT_REFRESH_TOKEN'):
                try: h['youtube'] = subir_youtube(sal, m.get('titulo', 'Clip'), desc, m.get('hashtags', []))
                except Exception as e: h['error_youtube'] = str(e)[:200]
            if E('CLIPS_TIKTOK_REFRESH_TOKEN'):
                try: h['tiktok'] = subir_tiktok(sal)
                except Exception as e: h['error_tiktok'] = str(e)[:200]
            if h.get('youtube') or h.get('tiktok'): hechos.append(h)
            usados.append((ini, fin)); hoy_n += 1 if h.get('youtube') else 0
            if h.get('youtube') or h.get('tiktok'): subidos += 1; ya.append(h)
            print('::notice title=Clips::', json.dumps(h, ensure_ascii=False)[:300])
            guardar('hechos.json', hechos)

if __name__ == '__main__':
    main()
