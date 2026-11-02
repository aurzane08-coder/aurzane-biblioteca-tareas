# Clientes mínimos (solo biblioteca estándar) para publicar en las cuentas propias de AURZANE.
# Cada red se activa sola cuando existen sus secretos en GitHub (Settings > Secrets and variables > Actions).
import os, json, time, uuid, urllib.request, urllib.parse, hmac, hashlib, base64, datetime, re

def E(k, d=None):
    v = os.environ.get(k, d)
    return v.strip() if isinstance(v, str) else v
SECRETOS = {
    'telegram': ['TELEGRAM_TOKEN', 'TELEGRAM_CANAL'],
    'bluesky': ['BSKY_USUARIO', 'BSKY_CLAVE_APP'],
    'mastodon': ['MASTODON_SERVIDOR', 'MASTODON_TOKEN'],
    'facebook': ['FB_PAGINA_ID', 'IG_TOKEN'],
    'youtube': ['YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'],
    'tiktok': ['TIKTOK_CLIENT_KEY', 'TIKTOK_CLIENT_SECRET', 'TIKTOK_REFRESH_TOKEN'],
    'instagram': ['IG_TOKEN'],
    'threads': ['THREADS_TOKEN'],
    'x': ['X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 'X_ACCESS_SECRET'],
}


def configurada(r):
    return all(E(k) for k in SECRETOS.get(r, ['-']))


def pedir(url, datos=None, cab=None, metodo=None, crudo=None, t=60):
    cab = dict(cab or {})
    cuerpo = crudo
    if datos is not None and crudo is None:
        if cab.get('Content-Type') == 'application/json': cuerpo = json.dumps(datos).encode()
        else:
            cuerpo = urllib.parse.urlencode(datos, doseq=True).encode(); cab.setdefault('Content-Type', 'application/x-www-form-urlencoded')
    req = urllib.request.Request(url, data=cuerpo, headers=cab, method=metodo or ('POST' if cuerpo is not None else 'GET'))
    try:
        with urllib.request.urlopen(req, timeout=t) as r:
            s = r.read().decode('utf-8', 'replace')
            return json.loads(s) if s.strip().startswith(('{', '[')) else s
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{e.code} {e.read().decode("utf-8", "replace")[:300]}')


def multipart(campos, archivo=None):
    b = uuid.uuid4().hex; out = b''
    for k, v in campos.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    if archivo:
        nombre, ruta = archivo
        out += f'--{b}\r\nContent-Disposition: form-data; name="{nombre}"; filename="img.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode()
        out += open(ruta, 'rb').read() + b'\r\n'
    out += f'--{b}--\r\n'.encode()
    return out, {'Content-Type': f'multipart/form-data; boundary={b}'}


# ---------------------------------------------------------------- redes
def telegram(texto, img_url, img_local, enlace, p):
    T = E('TELEGRAM_TOKEN'); canal = E('TELEGRAM_CANAL')
    cuerpo, cab = multipart({'chat_id': canal, 'caption': texto[:1024], 'parse_mode': 'HTML'}, ('photo', img_local))
    r = pedir(f'https://api.telegram.org/bot{T}/sendPhoto', crudo=cuerpo, cab=cab)
    return r['result']['message_id']


def bluesky(texto, img_url, img_local, enlace, p):
    S = 'https://bsky.social/xrpc/'
    s = pedir(S + 'com.atproto.server.createSession', {'identifier': E('BSKY_USUARIO'), 'password': E('BSKY_CLAVE_APP')},
              {'Content-Type': 'application/json'})
    auth = {'Authorization': 'Bearer ' + s['accessJwt']}
    blob = pedir(S + 'com.atproto.repo.uploadBlob', crudo=open(img_local, 'rb').read(), cab=dict(auth, **{'Content-Type': 'image/jpeg'}))['blob']
    b = texto.encode('utf-8'); facets = []
    for m in re.finditer(r'https?://\S+', texto):
        i = len(texto[:m.start()].encode()); facets.append({'index': {'byteStart': i, 'byteEnd': i + len(m.group(0).encode())},
                                                            'features': [{'$type': 'app.bsky.richtext.facet#link', 'uri': m.group(0)}]})
    for m in re.finditer(r'(?<!\w)#(\w+)', texto):
        i = len(texto[:m.start()].encode()); facets.append({'index': {'byteStart': i, 'byteEnd': i + len(m.group(0).encode())},
                                                            'features': [{'$type': 'app.bsky.richtext.facet#tag', 'tag': m.group(1)}]})
    rec = {'$type': 'app.bsky.feed.post', 'text': texto, 'langs': ['es'], 'facets': facets,
           'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
           'embed': {'$type': 'app.bsky.embed.images', 'images': [{'alt': p['titulo'][:300], 'image': blob}]}}
    r = pedir(S + 'com.atproto.repo.createRecord', {'repo': s['did'], 'collection': 'app.bsky.feed.post', 'record': rec},
              dict(auth, **{'Content-Type': 'application/json'}))
    return r['uri']


def mastodon(texto, img_url, img_local, enlace, p):
    base = E('MASTODON_SERVIDOR').rstrip('/');
    if not base.startswith('http'): base = 'https://' + base
    auth = {'Authorization': 'Bearer ' + E('MASTODON_TOKEN')}
    cuerpo, cab = multipart({'description': p['titulo'][:1400]}, ('file', img_local))
    m = pedir(base + '/api/v2/media', crudo=cuerpo, cab=dict(auth, **cab))
    time.sleep(3)
    r = pedir(base + '/api/v1/statuses', {'status': texto, 'media_ids[]': [m['id']], 'language': 'es', 'visibility': 'public'}, auth)
    return r['url']


GRAPH = 'https://graph.facebook.com/v21.0/'


_PT = {}


def pagina_token():
    """Token de la página AURZANE sacado del token del usuario del sistema (no caduca)."""
    if E('FB_PAGINA_TOKEN'): return E('FB_PAGINA_TOKEN')
    if 'tk' not in _PT:
        _PT['tk'] = pedir(GRAPH + E('FB_PAGINA_ID') + '?' + urllib.parse.urlencode({'fields': 'access_token', 'access_token': E('IG_TOKEN')}))['access_token']
    return _PT['tk']


def facebook(texto, img_url, img_local, enlace, p):
    r = pedir(GRAPH + E('FB_PAGINA_ID') + '/photos', {'url': img_url, 'message': texto, 'access_token': pagina_token()})
    return r.get('post_id') or r.get('id')


IG = 'https://graph.instagram.com/v21.0/'


def instagram(texto, img_url, img_local, enlace, p):
    """Instagram API con inicio de sesión de Instagram (cuenta profesional, sin página de Facebook)."""
    tk = E('IG_TOKEN')
    base = ig_base(tk)
    ig = ig_cuenta(tk)
    c = pedir(base + f'{ig}/media', {'image_url': img_url, 'caption': texto[:2200], 'access_token': tk})
    for _ in range(12):
        s = pedir(base + c['id'] + '?' + urllib.parse.urlencode({'fields': 'status_code', 'access_token': tk}))
        if s.get('status_code') == 'FINISHED': break
        if s.get('status_code') == 'ERROR': raise RuntimeError('Instagram rechazó la imagen')
        time.sleep(5)
    return pedir(base + f'{ig}/media_publish', {'creation_id': c['id'], 'access_token': tk})['id']


def ig_base(tk):
    # token de Instagram Login (empieza por IG) -> graph.instagram.com; token de usuario del sistema de Meta (EAA...) -> graph.facebook.com
    return IG if tk.startswith('IG') else GRAPH


def ig_cuenta(tk):
    if E('IG_USUARIO_ID'): return E('IG_USUARIO_ID')
    if tk.startswith('IG'):
        return pedir(IG + 'me?' + urllib.parse.urlencode({'fields': 'user_id', 'access_token': tk}))['user_id']
    # usuario del sistema: busca la cuenta de Instagram asignada a través de sus cuentas o del porfolio
    neg = pedir(GRAPH + 'me/businesses?' + urllib.parse.urlencode({'access_token': tk})).get('data', [])
    for b in neg:
        for campo in ('owned_instagram_accounts', 'instagram_accounts'):
            try:
                d = pedir(GRAPH + f"{b['id']}/{campo}?" + urllib.parse.urlencode({'fields': 'id,username', 'access_token': tk})).get('data', [])
                if d: return d[0]['id']
            except Exception: pass
    raise RuntimeError('No encuentro la cuenta de Instagram asignada al usuario del sistema')


def renovar_instagram():
    """Renueva el token largo (dura 60 días). Imprime el nuevo para guardarlo en el servidor."""
    r = pedir('https://graph.instagram.com/refresh_access_token?' + urllib.parse.urlencode({'grant_type': 'ig_refresh_token', 'access_token': E('IG_TOKEN')}))
    return r['access_token']


def threads(texto, img_url, img_local, enlace, p):
    tk = E('THREADS_TOKEN'); G = 'https://graph.threads.net/v1.0/me/'
    c = pedir(G + 'threads', {'media_type': 'IMAGE', 'image_url': img_url, 'text': texto[:500], 'access_token': tk})
    time.sleep(30)  # Meta recomienda esperar a que procese el contenedor
    return pedir(G + 'threads_publish', {'creation_id': c['id'], 'access_token': tk})['id']


def x(texto, img_url, img_local, enlace, p):
    url = 'https://api.x.com/2/tweets'
    o = {'oauth_consumer_key': E('X_API_KEY'), 'oauth_nonce': uuid.uuid4().hex, 'oauth_signature_method': 'HMAC-SHA1',
         'oauth_timestamp': str(int(time.time())), 'oauth_token': E('X_ACCESS_TOKEN'), 'oauth_version': '1.0'}
    q = lambda s: urllib.parse.quote(str(s), safe='')
    base = 'POST&' + q(url) + '&' + q('&'.join(f'{q(k)}={q(v)}' for k, v in sorted(o.items())))
    clave = q(E('X_API_SECRET')) + '&' + q(E('X_ACCESS_SECRET'))
    o['oauth_signature'] = base64.b64encode(hmac.new(clave.encode(), base.encode(), hashlib.sha1).digest()).decode()
    cab = {'Authorization': 'OAuth ' + ', '.join(f'{q(k)}="{q(v)}"' for k, v in sorted(o.items())), 'Content-Type': 'application/json'}
    return pedir(url, {'text': texto}, cab)['data']['id']


def publicar(r, texto, img_url, img_local, enlace, p):
    return globals()[r](texto, img_url, img_local, enlace, p)


def verificar():
    """Comprueba las credenciales sin publicar nada."""
    out = {}
    if configurada('telegram'):
        try:
            T = E('TELEGRAM_TOKEN'); me = pedir(f'https://api.telegram.org/bot{T}/getMe')['result']
            m = pedir(f'https://api.telegram.org/bot{T}/getChatMember?' + urllib.parse.urlencode({'chat_id': E('TELEGRAM_CANAL'), 'user_id': me['id']}))['result']
            out['telegram'] = f"bot @{me['username']} en {E('TELEGRAM_CANAL')}: {m['status']}" + (' (puede publicar)' if m.get('can_post_messages') else ' (NO puede publicar: hazlo administrador)')
        except Exception as e: out['telegram'] = 'ERROR ' + str(e)[:200]
    if configurada('bluesky'):
        try:
            s = pedir('https://bsky.social/xrpc/com.atproto.server.createSession', {'identifier': E('BSKY_USUARIO'), 'password': E('BSKY_CLAVE_APP')}, {'Content-Type': 'application/json'})
            out['bluesky'] = 'ok ' + s['handle']
        except Exception as e: out['bluesky'] = 'ERROR ' + str(e)[:200]
    if configurada('instagram'):
        try:
            tk = E('IG_TOKEN'); ig = ig_cuenta(tk)
            me = pedir(ig_base(tk) + ig + '?' + urllib.parse.urlencode({'fields': 'username', 'access_token': tk}))
            out['instagram'] = f"ok @{me.get('username')} (cuenta {ig})"
        except Exception as e: out['instagram'] = 'ERROR ' + str(e)[:200]
    if configurada('mastodon'):
        try:
            base = E('MASTODON_SERVIDOR').rstrip('/'); base = base if base.startswith('http') else 'https://' + base
            a = pedir(base + '/api/v1/apps/verify_credentials', cab={'Authorization': 'Bearer ' + E('MASTODON_TOKEN')})
            out['mastodon'] = 'ok app ' + a['name']
        except Exception as e: out['mastodon'] = 'ERROR ' + str(e)[:200]
    if configurada('facebook'):
        try:
            n = pedir(GRAPH + E('FB_PAGINA_ID') + '?' + urllib.parse.urlencode({'fields': 'name', 'access_token': pagina_token()}))
            out['facebook'] = 'ok página ' + n.get('name', '')
        except Exception as e: out['facebook'] = 'ERROR ' + str(e)[:200]
    if configurada('youtube'):
        try:
            tk = _google_token(); c = pedir('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true', cab={'Authorization': 'Bearer ' + tk})
            out['youtube'] = 'ok canal ' + c['items'][0]['snippet']['title']
        except Exception as e: out['youtube'] = 'ERROR ' + str(e)[:200]
    if configurada('tiktok'):
        try:
            tk = _tiktok_token(); i = pedir('https://open.tiktokapis.com/v2/post/publish/creator_info/query/', {}, {'Authorization': 'Bearer ' + tk, 'Content-Type': 'application/json; charset=UTF-8'})['data']
            out['tiktok'] = 'ok @' + i.get('creator_username', '') + ' privacidad ' + ','.join(i.get('privacy_level_options', []))
        except Exception as e: out['tiktok'] = 'ERROR ' + str(e)[:200]
    for r in SECRETOS:
        out.setdefault(r, 'sin configurar' if not configurada(r) else out.get(r))
    for k, v in out.items(): print(f'{k}: {v}')
    return out



# ---------------------------------------------------------------- vídeos verticales (franja 4)
def publicar_video(r, texto, video_url, video_local, enlace, p):
    return globals()['video_' + r](texto, video_url, video_local, enlace, p)


def video_telegram(texto, url, local, enlace, p):
    cuerpo, cab = multipart({'chat_id': E('TELEGRAM_CANAL'), 'caption': texto[:1024], 'parse_mode': 'HTML', 'supports_streaming': 'true'}, None)
    b = cab['Content-Type'].split('boundary=')[1]
    cuerpo = cuerpo[:-len(f'--{b}--\r\n')] + f'--{b}\r\nContent-Disposition: form-data; name="video"; filename="v.mp4"\r\nContent-Type: video/mp4\r\n\r\n'.encode() + open(local, 'rb').read() + f'\r\n--{b}--\r\n'.encode()
    return pedir(f"https://api.telegram.org/bot{E('TELEGRAM_TOKEN')}/sendVideo", crudo=cuerpo, cab=cab, t=180)['result']['message_id']


def video_instagram(texto, url, local, enlace, p):
    tk = E('IG_TOKEN'); base = ig_base(tk); ig = ig_cuenta(tk)
    c = pedir(base + f'{ig}/media', {'media_type': 'REELS', 'video_url': url, 'caption': texto[:2200], 'share_to_feed': 'true', 'access_token': tk})
    for _ in range(36):
        time.sleep(10)
        s = pedir(base + c['id'] + '?' + urllib.parse.urlencode({'fields': 'status_code,status', 'access_token': tk}))
        if s.get('status_code') == 'FINISHED': break
        if s.get('status_code') == 'ERROR': raise RuntimeError('Instagram rechazó el vídeo: ' + str(s.get('status')))
    return pedir(base + f'{ig}/media_publish', {'creation_id': c['id'], 'access_token': tk})['id']


def video_facebook(texto, url, local, enlace, p):
    r = pedir(GRAPH + E('FB_PAGINA_ID') + '/videos', {'file_url': url, 'description': texto, 'access_token': pagina_token()}, t=300)
    return r.get('id')


def _google_token():
    r = pedir('https://oauth2.googleapis.com/token', {'client_id': E('YT_CLIENT_ID'), 'client_secret': E('YT_CLIENT_SECRET'),
                                                     'refresh_token': E('YT_REFRESH_TOKEN'), 'grant_type': 'refresh_token'})
    return r['access_token']


def video_youtube(texto, url, local, enlace, p):
    tk = _google_token()
    titulo = (p['titulo'] if p['tipo'] == 'frase' else p['ganchos'][0])[:90] + ' #Shorts'
    desc = texto + '\n\nAURZANE: tests psicológicos, calculadoras y libros gratis. https://aurzane.com'
    meta = {'snippet': {'title': titulo, 'description': desc[:4900], 'tags': [h for h in p.get('hashtags', [])][:10] + ['AURZANE', 'Shorts'],
                        'categoryId': '27', 'defaultLanguage': 'es', 'defaultAudioLanguage': 'es'},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
    datos = open(local, 'rb').read()
    req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                                 data=json.dumps(meta).encode(), method='POST',
                                 headers={'Authorization': 'Bearer ' + tk, 'Content-Type': 'application/json; charset=UTF-8',
                                          'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(len(datos))})
    sesion = urllib.request.urlopen(req, timeout=60).headers['Location']
    r = pedir(sesion, crudo=datos, cab={'Authorization': 'Bearer ' + tk, 'Content-Type': 'video/mp4'}, metodo='PUT', t=600)
    return 'https://youtu.be/' + r['id']


def _tiktok_token():
    rt = E('TIKTOK_REFRESH_TOKEN')
    r = pedir('https://open.tiktokapis.com/v2/oauth/token/', {'client_key': E('TIKTOK_CLIENT_KEY'), 'client_secret': E('TIKTOK_CLIENT_SECRET'),
                                                             'grant_type': 'refresh_token', 'refresh_token': rt})
    if r.get('refresh_token') and r['refresh_token'] != rt:
        open('/tmp/tiktok_refresh', 'w').write(r['refresh_token'])  # el flujo lo guarda en el servidor
    return r['access_token']


def video_tiktok(texto, url, local, enlace, p):
    tk = _tiktok_token(); cab = {'Authorization': 'Bearer ' + tk, 'Content-Type': 'application/json; charset=UTF-8'}
    info = pedir('https://open.tiktokapis.com/v2/post/publish/creator_info/query/', {}, cab)['data']
    # Hasta que TikTok apruebe la app, solo se puede publicar en privado (SELF_ONLY). Tras la aprobación: variable TIKTOK_PUBLICO=1.
    opciones = info.get('privacy_level_options', [])
    priv = 'PUBLIC_TO_EVERYONE' if E('TIKTOK_PUBLICO') == '1' and 'PUBLIC_TO_EVERYONE' in opciones else ('SELF_ONLY' if 'SELF_ONLY' in opciones else opciones[0])
    datos = open(local, 'rb').read()
    titulo = (p['titulo'] if p['tipo'] == 'frase' else p['ganchos'][0]) + ' ' + ' '.join('#' + h for h in p.get('hashtags', [])[:4]) + ' #AURZANE'
    ini = pedir('https://open.tiktokapis.com/v2/post/publish/video/init/', {
        'post_info': {'title': titulo[:2200], 'privacy_level': priv, 'disable_comment': False, 'disable_duet': False, 'disable_stitch': False},
        'source_info': {'source': 'FILE_UPLOAD', 'video_size': len(datos), 'chunk_size': len(datos), 'total_chunk_count': 1}}, cab)['data']
    pedir(ini['upload_url'], crudo=datos, metodo='PUT', t=600,
          cab={'Content-Type': 'video/mp4', 'Content-Range': f'bytes 0-{len(datos) - 1}/{len(datos)}'})
    return ini['publish_id'] + ('' if priv == 'PUBLIC_TO_EVERYONE' else ' (privado hasta la auditoría de TikTok)')


def perfiles():
    """Pone foto de perfil, portada y descripción en las redes que lo permiten por API (Bluesky y Telegram).
    Imágenes de marketing/marca/ (marca.js) y textos de marketing/perfiles.json."""
    D = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(D, 'marca')
    txt = json.load(open(os.path.join(D, 'perfiles.json'), encoding='utf-8')); out = {}
    if configurada('bluesky'):
        try:
            S = 'https://bsky.social/xrpc/'
            s = pedir(S + 'com.atproto.server.createSession', {'identifier': E('BSKY_USUARIO'), 'password': E('BSKY_CLAVE_APP')}, {'Content-Type': 'application/json'})
            auth = {'Authorization': 'Bearer ' + s['accessJwt']}
            av = pedir(S + 'com.atproto.repo.uploadBlob', crudo=open(os.path.join(M, 'perfil.png'), 'rb').read(), cab=dict(auth, **{'Content-Type': 'image/png'}))['blob']
            ba = pedir(S + 'com.atproto.repo.uploadBlob', crudo=open(os.path.join(M, 'portada-bluesky-mastodon.jpg'), 'rb').read(), cab=dict(auth, **{'Content-Type': 'image/jpeg'}))['blob']
            try: rec = pedir(S + 'com.atproto.repo.getRecord?' + urllib.parse.urlencode({'repo': s['did'], 'collection': 'app.bsky.actor.profile', 'rkey': 'self'}), cab=auth)['value']
            except Exception: rec = {'$type': 'app.bsky.actor.profile'}
            rec.update({'displayName': txt['nombre'], 'description': txt['bluesky'][:256], 'avatar': av, 'banner': ba})
            pedir(S + 'com.atproto.repo.putRecord', {'repo': s['did'], 'collection': 'app.bsky.actor.profile', 'rkey': 'self', 'record': rec},
                  dict(auth, **{'Content-Type': 'application/json'}))
            out['bluesky'] = 'ok perfil, portada y descripción'
        except Exception as e: out['bluesky'] = 'ERROR ' + str(e)[:200]
    if configurada('telegram'):
        try:
            T = 'https://api.telegram.org/bot' + E('TELEGRAM_TOKEN') + '/'
            cuerpo, cab = multipart({'chat_id': E('TELEGRAM_CANAL')}, ('photo', os.path.join(M, 'perfil.png')))
            pedir(T + 'setChatPhoto', crudo=cuerpo, cab=cab)
            try: pedir(T + 'setChatDescription', {'chat_id': E('TELEGRAM_CANAL'), 'description': txt['telegram'][:255]})
            except RuntimeError as e:
                if 'not modified' not in str(e): raise
            out['telegram'] = 'ok foto y descripción'
        except Exception as e: out['telegram'] = 'ERROR ' + str(e)[:200]
    return out
