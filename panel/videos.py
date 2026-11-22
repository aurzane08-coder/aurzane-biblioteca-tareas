"""Lista de vídeos ya publicados en YouTube por AURZANE para la sección «Vídeo del día» (aurzane-estilo.js)."""
import csv, json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = {p['id']: p for p in json.load(open(os.path.join(R, 'marketing', 'catalogo.json'), encoding='utf-8'))['productos']}
vistos, out = set(), []
for f in csv.reader(open(os.path.join(R, 'marketing', 'registro.csv'), encoding='utf-8')):
    if len(f) < 6 or f[2] != 'youtube' or f[4] != 'ok': continue
    m = re.search(r'(?:youtu\.be/|v=|shorts/)([A-Za-z0-9_-]{11})', f[5])
    if not m or m.group(1) in vistos: continue
    vistos.add(m.group(1)); p = cat.get(f[3], {})
    out.append({'id': m.group(1), 'fecha': f[0], 't': re.sub(r'\s+', ' ', p.get('titulo') or 'Vídeo de AURZANE')[:110], 'mundo': p.get('mundo', ''), 'u': p.get('url', '')})
# Solo los vídeos públicos: los privados o retirados no tienen miniatura y dejaban un hueco gris en «Vídeo del día» (22/11/2026)
import urllib.request, urllib.parse
def publico(i):
    try:
        u = 'https://www.youtube.com/oembed?format=json&url=' + urllib.parse.quote('https://www.youtube.com/watch?v=' + i)
        return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AURZANE'}), timeout=15).status == 200
    except Exception:
        return False
out = [v for v in out[-200:] if publico(v['id'])]
open('/tmp/videos.js', 'w', encoding='utf-8').write('window.AZ_VIDEOS=' + json.dumps(out[-120:], ensure_ascii=False) + ';\n')
print(len(out), 'vídeos')
