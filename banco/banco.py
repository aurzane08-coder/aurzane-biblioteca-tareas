"""Banco de imágenes de AURZANE (22/11/2026, pedido de Adrián): fotos reales de Pexels y Pixabay (licencias que permiten guardarlas
y usarlas en la web sin atribución obligatoria; se guarda el autor igualmente), descargadas a NUESTRO servidor en AVIF y ordenadas
por mundo y tema, para usarlas en todo el sitio sin depender de webs ajenas. Nunca imágenes creadas por Claude.
Cada ejecución añade fotos hasta MAX por tema (crece solo con el tiempo). Salida:
  salida/img/banco/<mundo>/<tema>/<origen>-<id>-1600.avif y -640.avif   (ancho 1600 para cabeceras, 640 para tarjetas)
  salida/img/banco/banco.json  índice {mundo: {tema: [{f, autor, origen, enlace, w, h, color}]}}
Uso: PEXELS_API_KEY=… PIXABAY_KEY=… python3 banco/banco.py banco.json(anterior, puede no existir) salida/"""
import os, sys, json, time, io, urllib.request, urllib.parse
from PIL import Image

TEMAS = {
  'mind': {'ansiedad': 'anxious person', 'tristeza': 'sad person window', 'estres': 'stressed work desk', 'cerebro': 'brain neuroscience',
           'terapia': 'therapy session conversation', 'meditacion': 'meditation calm', 'sueno': 'sleeping bed night', 'pareja': 'couple talking',
           'familia': 'family together home', 'infancia': 'children playing', 'adolescentes': 'teenagers friends', 'mayores': 'elderly people smiling',
           'emociones': 'emotional face portrait', 'autoestima': 'confident woman', 'soledad': 'person alone', 'calma': 'calm lake morning'},
  'nexus': {'campus': 'university campus', 'estudiantes': 'university students', 'biblioteca': 'university library', 'graduacion': 'graduation ceremony',
            'clase': 'lecture hall', 'laboratorio': 'science laboratory', 'tecnologia': 'technology computer code', 'investigacion': 'scientist research',
            'edificio-historico': 'old university building', 'orientacion': 'young person thinking future'},
  'live': {'alimentacion': 'healthy food', 'correr': 'running outdoors', 'yoga': 'yoga', 'agua': 'drinking water glass', 'embarazo': 'pregnant woman',
           'medico': 'doctor patient', 'descanso': 'relaxing hammock', 'bosque': 'forest path', 'deporte': 'sport team', 'cocina': 'cooking vegetables'},
  'learn': {'estudiar': 'studying desk', 'libros': 'books shelf', 'lectura': 'reading book', 'aula': 'classroom', 'apuntes': 'notebook writing',
            'online': 'online course laptop', 'idiomas': 'language learning', 'memoria': 'sticky notes wall', 'escritura': 'hand writing pen', 'concentracion': 'focus work'},
  'build': {'vivienda': 'house exterior', 'llaves': 'house keys', 'dinero': 'money coins', 'ahorro': 'savings piggy bank', 'arquitectura': 'modern architecture',
            'obra': 'construction site', 'ciudad': 'city skyline', 'oficina': 'office work', 'trabajo': 'workers', 'jubilacion': 'retired couple',
            'pisos': 'apartment building', 'energia': 'solar panels'},
  'general': {'paisaje': 'landscape', 'cielo': 'sky clouds', 'mar': 'ocean waves', 'montana': 'mountains', 'naturaleza': 'nature green', 'textura': 'paper texture', 'frases': 'sunset silhouette'},
}
MAX = int(os.environ.get('MAX', '24'))           # fotos por tema (subirlo con el tiempo para tener más)
NUEVAS = int(os.environ.get('NUEVAS', '24'))     # fotos nuevas por tema y ejecución
PK, XK = os.environ.get('PEXELS_API_KEY', ''), os.environ.get('PIXABAY_KEY', '')
previo, sal = sys.argv[1], sys.argv[2]
idx = json.load(open(previo)) if os.path.exists(previo) and os.path.getsize(previo) > 2 else {}

def pedir(u, h=None):
    r = urllib.request.Request(u, headers=dict({'User-Agent': 'AURZANE banco de imagenes'}, **(h or {})))
    return urllib.request.urlopen(r, timeout=60).read()

def pexels(q, pag):
    if not PK: return []
    d = json.loads(pedir('https://api.pexels.com/v1/search?' + urllib.parse.urlencode({'query': q, 'orientation': 'landscape', 'per_page': 40, 'page': pag, 'size': 'large'}), {'Authorization': PK}))
    return [{'origen': 'pexels', 'id': str(p['id']), 'url': p['src']['original'] + '?auto=compress&cs=tinysrgb&w=1800', 'autor': p.get('photographer', ''),
             'enlace': p.get('url', ''), 'color': p.get('avg_color', '')} for p in d.get('photos', []) if p.get('width', 0) >= 1600]

def pixabay(q, pag):
    if not XK: return []
    d = json.loads(pedir('https://pixabay.com/api/?' + urllib.parse.urlencode({'key': XK, 'q': q, 'image_type': 'photo', 'orientation': 'horizontal', 'per_page': 40, 'page': pag, 'safesearch': 'true', 'min_width': 1600})))
    return [{'origen': 'pixabay', 'id': str(p['id']), 'url': p.get('largeImageURL', ''), 'autor': p.get('user', ''), 'enlace': p.get('pageURL', ''), 'color': ''} for p in d.get('hits', [])]

def guardar(img, ruta, ancho, q):
    im = img.copy(); im.thumbnail((ancho, ancho * 2)); os.makedirs(os.path.dirname(ruta), exist_ok=True)
    im.save(ruta, 'AVIF', quality=q, speed=6)
    return im.size

total = 0
for mundo, temas in TEMAS.items():
    for tema, q in temas.items():
        lista = idx.setdefault(mundo, {}).setdefault(tema, [])
        vistos = {f"{x['origen']}-{x['id']}" for x in lista}
        falta = min(MAX - len(lista), NUEVAS)
        if falta <= 0: continue
        pe, px = [], []
        for pag in (1, 2):
            try: pe += pexels(q, pag)
            except Exception as e: print('pexels', q, e)
            try: px += pixabay(q, pag)
            except Exception as e: print('pixabay', q, e)
            if len([c for c in pe + px if f"{c['origen']}-{c['id']}" not in vistos]) >= falta * 2: break
        cand = [c for par in zip(pe, px) for c in par] + pe[len(px):] + px[len(pe):]   # alterna Pexels y Pixabay para variar estilos
        hechas = 0
        for c in cand:
            if hechas >= falta: break
            k = f"{c['origen']}-{c['id']}"
            if k in vistos or not c['url']: continue
            try:
                img = Image.open(io.BytesIO(pedir(c['url']))).convert('RGB')
                if img.width < 1200 or img.width < img.height: continue
                base = f'{sal}/img/banco/{mundo}/{tema}/{k}'
                w, h = guardar(img, base + '-1600.avif', 1600, 52); guardar(img, base + '-640.avif', 640, 50)
                lista.append({'f': f'{mundo}/{tema}/{k}', 'autor': c['autor'], 'origen': c['origen'], 'enlace': c['enlace'], 'w': w, 'h': h, 'color': c['color']})
                vistos.add(k); hechas += 1; total += 1
            except Exception as e:
                print('  no se pudo', k, e)
        print(f'{mundo}/{tema}: +{hechas} (total {len(lista)})'); time.sleep(1)
os.makedirs(f'{sal}/img/banco', exist_ok=True)
json.dump(idx, open(f'{sal}/img/banco/banco.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('Fotos nuevas:', total, '· en el banco:', sum(len(t) for m in idx.values() for t in m.values()))
