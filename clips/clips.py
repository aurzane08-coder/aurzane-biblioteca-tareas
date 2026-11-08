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
MAX_DIA = int(E('CLIPS_MAX_DIA') or '6')          # el cupo gratis de la API de YouTube da para unas 6 subidas al día por proyecto
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
    return ''

def transcribir(video):
    from faster_whisper import WhisperModel
    modelo = WhisperModel(E('WHISPER') or 'small', device='cpu', compute_type='int8')
    segs, info = modelo.transcribe(video, vad_filter=True, word_timestamps=True)
    out = []
    for s in segs:
        out.append({'i': round(s.start, 2), 'f': round(s.end, 2), 't': s.text.strip(), 'w': [(round(w.start, 2), round(w.end, 2), w.word) for w in (s.words or [])]})
    return out, info.language

def elegir_momentos(segs, fuente, n):
    texto = '\n'.join(f'[{s["i"]:.1f}-{s["f"]:.1f}] {s["t"]}' for s in segs)[:60000]
    r = gemini(f'Eres editor de clips virales para TikTok y YouTube Shorts. Vídeo: «{fuente.get("titulo", "")}» de {fuente.get("creador", "")}. '
               f'Reglas de la campaña: {fuente.get("reglas", "ninguna especial")}. A partir de la transcripción con tiempos, elige los {n} mejores momentos '
               'que funcionen solos: empiezan con un gancho fuerte en los 2 primeros segundos, tienen una idea completa y duran entre 20 y 55 segundos. '
               'Evita insultos, temas sensibles sin contexto y cortes a mitad de frase. Responde SOLO un JSON: '
               '[{"inicio": segundos, "fin": segundos, "titulo": "<título corto y llamativo, sin clickbait falso>", "hashtags": ["<4 hashtags sin #>"]}]\n\n' + texto)
    try: return json.loads(re.search(r'\[.*\]', r, re.S).group(0))[:n]
    except Exception: return []

def ass_subtitulos(segs, ini, fin, ruta):
    """Subtítulos grandes por grupos de 3 palabras, centrados en el tercio inferior (estilo Shorts)."""
    palabras = [w for s in segs for w in s['w'] if w[0] >= ini - 0.05 and w[1] <= fin + 0.05]
    cab = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, '
           'Alignment, MarginV, Outline, Shadow\nStyle: S,DejaVu Sans,78,&H00FFFFFF,&H00000000,&H80000000,1,2,560,6,2\n\n[Events]\nFormat: Layer, Start, End, Style, Text\n')
    ts = lambda x: f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'
    lineas = []
    for k in range(0, len(palabras), 3):
        g = palabras[k:k + 3]
        txt = ' '.join(w[2].strip() for w in g).upper().replace('{', '').replace('}', '')
        lineas.append(f'Dialogue: 0,{ts(g[0][0] - ini)},{ts(g[-1][1] - ini)},S,{txt}')
    open(ruta, 'w', encoding='utf-8').write(cab + '\n'.join(lineas) + '\n')

def cortar(video, ini, fin, ass, sal):
    filtro = ('[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[f];'
              '[b]scale=1080:-2[p];[f][p]overlay=(W-w)/2:(H-h)/2,ass=' + ass + '[v]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ini), '-to', str(fin), '-i', video, '-filter_complex', filtro,
                    '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart', sal], check=True)

def subir_youtube(ruta, titulo, desc, tags):
    tk = pedir('https://oauth2.googleapis.com/token', {'client_id': E('CLIPS_YT_CLIENT_ID') or E('YT_CLIENT_ID'), 'client_secret': E('CLIPS_YT_CLIENT_SECRET') or E('YT_CLIENT_SECRET'),
                                                        'refresh_token': E('CLIPS_YT_REFRESH_TOKEN'), 'grant_type': 'refresh_token'})['access_token']
    meta = {'snippet': {'title': (titulo[:90] + ' #Shorts'), 'description': desc[:4900], 'tags': tags[:10] + ['Shorts', 'clips'], 'categoryId': '24'},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
    datos = open(ruta, 'rb').read()
    req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', data=json.dumps(meta).encode(), method='POST',
                                 headers={'Authorization': 'Bearer ' + tk, 'Content-Type': 'application/json; charset=UTF-8', 'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(len(datos))})
    sesion = urllib.request.urlopen(req, timeout=60).headers['Location']
    r = pedir(sesion, crudo=datos, cab={'Authorization': 'Bearer ' + tk, 'Content-Type': 'video/mp4'}, metodo='PUT', t=600)
    return 'https://youtube.com/shorts/' + r['id']

def subir_tiktok(ruta):
    rt = E('CLIPS_TIKTOK_REFRESH_TOKEN')
    r = pedir('https://open.tiktokapis.com/v2/oauth/token/', {'client_key': E('TIKTOK_CLIENT_KEY'), 'client_secret': E('TIKTOK_CLIENT_SECRET'), 'grant_type': 'refresh_token', 'refresh_token': rt})
    if r.get('refresh_token') and r['refresh_token'] != rt: open('/tmp/clips_tiktok_refresh', 'w').write(r['refresh_token'])
    cab = {'Authorization': 'Bearer ' + r['access_token'], 'Content-Type': 'application/json; charset=UTF-8'}
    datos = open(ruta, 'rb').read()
    ini = pedir('https://open.tiktokapis.com/v2/post/publish/inbox/video/init/', {'source_info': {'source': 'FILE_UPLOAD', 'video_size': len(datos), 'chunk_size': len(datos), 'total_chunk_count': 1}}, cab)['data']
    pedir(ini['upload_url'], crudo=datos, metodo='PUT', t=600, cab={'Content-Type': 'video/mp4', 'Content-Range': f'bytes 0-{len(datos) - 1}/{len(datos)}'})
    return ini['publish_id'] + ' (borrador en la bandeja de TikTok)'

def main():
    fuentes = [f for f in leer('fuentes.json', []) if f.get('autorizado') is True and f.get('url')]
    hechos = leer('hechos.json', [])
    hoy_n = sum(1 for h in hechos if h.get('fecha') == HOY and h.get('youtube'))
    if not fuentes: print('::notice title=Clips::No hay vídeos autorizados en clips/fuentes.json'); return
    if not E('CLIPS_YT_REFRESH_TOKEN'): print('::notice title=Clips::Falta el secreto CLIPS_YT_REFRESH_TOKEN (permiso del canal Clips-All)')
    os.makedirs('/tmp/clips', exist_ok=True)
    for f in fuentes:
        if hoy_n >= MAX_DIA: break
        fid = hashlib.md5(f['url'].encode()).hexdigest()[:10]
        ya = [h for h in hechos if h['fuente'] == fid]
        if len(ya) >= int(f.get('max_clips', 5)): continue
        video = f'/tmp/clips/{fid}.mp4'
        if not os.path.exists(video):
            subprocess.run(['yt-dlp', '-f', 'bv*[height<=1080]+ba/b', '--merge-output-format', 'mp4', '-o', video, f['url']], check=False)
        if not os.path.exists(video): print('::warning title=Clips::no se pudo descargar', f['url']); continue
        cache = os.path.join(D, 'transcripciones', fid + '.json')
        if os.path.exists(cache): segs = json.load(open(cache, encoding='utf-8'))
        else:
            segs, _ = transcribir(video); os.makedirs(os.path.dirname(cache), exist_ok=True); json.dump(segs, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
        usados = [(h['inicio'], h['fin']) for h in ya]
        for m in elegir_momentos(segs, f, int(f.get('max_clips', 5)) - len(ya) + 2):
            if hoy_n >= MAX_DIA: break
            ini, fin = float(m['inicio']), float(m['fin'])
            if not (15 <= fin - ini <= 60) or any(not (fin <= a or ini >= b) for a, b in usados): continue
            cid = f'{fid}-{int(ini)}'; sal = f'/tmp/clips/{cid}.mp4'; ass = f'/tmp/clips/{cid}.ass'
            ass_subtitulos(segs, ini, fin, ass); cortar(video, ini, fin, ass, sal)
            desc = (m.get('titulo', '') + '\n\nClip de ' + f.get('creador', '') + (' · Original: ' + f['original'] if f.get('original') else '') +
                    '\n' + ' '.join('#' + h for h in m.get('hashtags', [])[:4]) + ' #Shorts')
            h = {'id': cid, 'fuente': fid, 'campana': f.get('campana', ''), 'inicio': ini, 'fin': fin, 'titulo': m.get('titulo', ''), 'fecha': HOY}
            if E('CLIPS_YT_REFRESH_TOKEN'):
                try: h['youtube'] = subir_youtube(sal, m.get('titulo', 'Clip'), desc, m.get('hashtags', []))
                except Exception as e: h['error_youtube'] = str(e)[:200]
            if E('CLIPS_TIKTOK_REFRESH_TOKEN'):
                try: h['tiktok'] = subir_tiktok(sal)
                except Exception as e: h['error_tiktok'] = str(e)[:200]
            hechos.append(h); usados.append((ini, fin)); hoy_n += 1 if h.get('youtube') else 0
            print('::notice title=Clips::', json.dumps(h, ensure_ascii=False)[:300])
            guardar('hechos.json', hechos)

if __name__ == '__main__':
    main()
