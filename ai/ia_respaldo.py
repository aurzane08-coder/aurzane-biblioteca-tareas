"""IA de respaldo común (24/11/2026). GitHub Models dejó de responder (devuelve «OK» a todo), así que el respaldo es ahora
la misma clave de Gemini con varios modelos por turnos: cada modelo tiene su propio cupo gratuito y, cuando uno está
saturado (503) o sin cupo (429), se pasa al siguiente. Si todos fallan, se espera y se reintenta (hasta 3 rondas).
Uso: from ia_respaldo import generar; texto = generar(prompt, json_mode=True)"""
import json, os, time, urllib.request, urllib.error

MODELOS = ['gemini-flash-latest', 'gemini-3.5-flash', 'gemini-flash-lite-latest', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-3-flash-preview']
_FUERA = set()   # modelos que no existen o se quedaron sin cupo en esta ejecución


def _post(url, cab, datos, t):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=datos, headers=cab, method='POST'), timeout=t) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
    except Exception as e: return 0, str(e).encode()


def generar(prompt, json_mode=False, temp=0.3, maxt=8192, rondas=3, t=150, primero=None):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if not k: return ''
    cab = {'Content-Type': 'application/json', 'x-goog-api-key': k}
    gc = {'temperature': temp, 'maxOutputTokens': maxt}
    if json_mode: gc['responseMimeType'] = 'application/json'
    cuerpo = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': gc}).encode()
    orden = ([primero] if primero else []) + [m for m in MODELOS if m != primero]
    for ronda in range(rondas):
        for m in orden:
            if m in _FUERA: continue
            st, b = _post(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', cab, cuerpo, t)
            if st == 200:
                try:
                    c = json.loads(b)['candidates'][0]
                    txt = ''.join(x.get('text', '') for x in c['content'].get('parts', []) if not x.get('thought')).strip()
                    if txt: return txt
                    print(f'  IA {m}: respuesta vacía ({c.get("finishReason")})')
                except Exception as e: print(f'  IA {m}: respuesta no legible', str(e)[:80])
                continue
            print(f'  IA {m}: error {st}', b[:120].decode('utf-8', 'ignore').replace('\n', ' '))
            if st in (404, 400) or (st == 429 and b'quota' in b.lower()): _FUERA.add(m)
        if all(m in _FUERA for m in orden): break
        if ronda < rondas - 1: time.sleep(20 * (ronda + 1))
    return ''
