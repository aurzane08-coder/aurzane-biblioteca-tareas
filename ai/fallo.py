# -*- coding: utf-8 -*-
"""Si el propio AI Manager se rompe (un error que no conoce), este guardián lo registra, pide a Gemini la causa y te avisa.
Lo ejecuta ai-manager.yml solo cuando manager.py falla. Entrada: /tmp/ai/salida.txt (lo que imprimió el manager)."""
import json, os, re, subprocess, urllib.request, datetime
SSH, DEST = os.environ.get('SSH', ''), os.environ.get('SG_DEST', '')
def remoto(o, entrada=None):
    if not SSH or not DEST: return ''
    try: return subprocess.run(SSH.split() + [DEST, o], input=entrada, capture_output=True, text=True, timeout=120).stdout
    except Exception: return ''
salida = open('/tmp/ai/salida.txt', encoding='utf-8', errors='replace').read() if os.path.exists('/tmp/ai/salida.txt') else ''
traza = salida[salida.rfind('Traceback'):] if 'Traceback' in salida else salida[-3000:]
traza = traza[-3500:]
linea = (re.findall(r'File "[^"]*manager\.py", line (\d+)', traza) or ['?'])[-1]
codigo = ''
try:
    L = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager.py'), encoding='utf-8').read().splitlines(); n = int(linea)
    codigo = '\n'.join(f'{i + 1}: {L[i]}' for i in range(max(0, n - 8), min(len(L), n + 4)))
except Exception: pass
sug, k = '', os.environ.get('GEMINI_API_KEY', '').strip()
if k:
    try:
        cab = {'Content-Type': 'application/json', 'x-goog-api-key': k}
        ms = json.load(urllib.request.urlopen(urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200', headers=cab), timeout=60)).get('models', [])
        ns = [m['name'].split('/')[-1] for m in ms if 'generateContent' in m.get('supportedGenerationMethods', [])]
        ms = [n for n in ('gemini-flash-latest', 'gemini-flash-lite-latest') if n in ns] + sorted([n for n in ns if re.match(r'^gemini-\d[\d.]*-flash$', n)], key=lambda x: [-int(v) for v in re.findall(r'\d+', x)])
        cuerpo = json.dumps({'contents': [{'parts': [{'text': 'El script de mantenimiento AI Manager (Python) de la web AURZANE se ha roto. Explica en español, sin rayas largas y en máximo 8 líneas, '
                 'la causa y el cambio exacto de código que lo arregla.\n\nError:\n' + traza + '\n\nCódigo alrededor de la línea ' + linea + ':\n' + codigo}]}], 'generationConfig': {'temperature': 0.2, 'maxOutputTokens': 3000}}).encode()
        for m in ms[:3]:
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', data=cuerpo, headers=cab), timeout=90))
                sug = ''.join(x.get('text', '') for x in r['candidates'][0]['content']['parts']).strip(); break
            except Exception: continue
    except Exception: pass
ahora = datetime.datetime.now(datetime.timezone.utc).isoformat()[:16]
ult = (traza.strip().splitlines() or ['error desconocido'])[-1][:250]
reg = {'id': 'f' + ahora.replace(':', '').replace('-', ''), 'fecha': ahora, 'clave': 'manager', 'tipo': 'fallo_interno', 'firma': 'fallo_interno|' + re.sub(r'\d+', '#', ult)[:120],
       'problema': f'El propio AI Manager se rompió en la línea {linea}: {ult}', 'receta': 'diagnostico_ia', 'resultado': 'escalado', 'detalle': traza[-600:], 'sugerencia': sug}
try: rep = json.loads(remoto('cat www/aurzane.com/privado-ai/reparaciones.json 2>/dev/null') or '[]')
except Exception: rep = []
rep.insert(0, reg)
remoto('cat > www/aurzane.com/privado-ai/reparaciones.json && chmod 600 www/aurzane.com/privado-ai/reparaciones.json', json.dumps(rep[:500], ensure_ascii=False))
tg = os.environ.get('TELEGRAM_TOKEN', '')
chat = remoto('cat www/aurzane.com/privado-ai/telegram_chat 2>/dev/null').strip()
if tg and chat:
    txt = '🛠 AURZANE AI Manager se ha roto y lo he registrado.\n' + reg['problema'] + ('\n\nDiagnóstico:\n' + sug[:2500] if sug else '') + '\n\nMíralo en el admin, pestaña Reparaciones.'
    try: urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{tg}/sendMessage', data=json.dumps({'chat_id': chat, 'text': txt[:3900]}).encode(), headers={'Content-Type': 'application/json'}), timeout=30)
    except Exception: pass
print('::error title=AI Manager roto::' + reg['problema'])
