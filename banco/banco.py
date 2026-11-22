"""Catálogo de imágenes de AURZANE (v2, 22/11/2026, pedido de Adrián: muchas fotos distintas y SIN ocupar espacio en SiteGround).
Solo se guarda el ÍNDICE (banco/banco.json, en GitHub; la web lo lee por jsDelivr). Las fotos se sirven directamente desde el CDN
de Pexels, que las entrega en AVIF al navegador que lo admite (comprobado: image/avif), con el tamaño que pide cada página.
Fotos reales de Pexels (su licencia y sus normas de la API permiten enlazarlas desde su CDN; se guarda el autor y se acredita a Pexels).
Nunca imágenes creadas por Claude. Cada ejecución completa hasta MAX fotos por tema; para crecer, subir MAX.
Uso: PEXELS_API_KEY=… python3 banco/banco.py banco/banco.json"""
import os, sys, json, time, urllib.request, urllib.parse

TEMAS = {
  'mind': {'ansiedad': 'anxious person', 'tristeza': 'sad person window', 'estres': 'stressed work desk', 'cerebro': 'brain neuroscience',
           'terapia': 'therapy session conversation', 'meditacion': 'meditation calm', 'sueno': 'sleeping bed night', 'pareja': 'couple talking',
           'familia': 'family together home', 'infancia': 'children playing', 'adolescentes': 'teenagers friends', 'mayores': 'elderly people smiling',
           'emociones': 'emotional face portrait', 'autoestima': 'confident woman', 'soledad': 'person alone', 'calma': 'calm lake morning',
           'amistad': 'friends laughing', 'esperanza': 'sunrise hope', 'resiliencia': 'plant growing through crack'},
  'nexus': {'campus': 'university campus', 'estudiantes': 'university students', 'biblioteca': 'university library', 'graduacion': 'graduation ceremony',
            'clase': 'lecture hall', 'laboratorio': 'science laboratory', 'tecnologia': 'technology computer code', 'investigacion': 'scientist research',
            'edificio-historico': 'old university building', 'orientacion': 'young person thinking future', 'ciudad-universitaria': 'european old town street'},
  'live': {'alimentacion': 'healthy food', 'correr': 'running outdoors', 'yoga': 'yoga', 'agua': 'drinking water glass', 'embarazo': 'pregnant woman',
           'medico': 'doctor patient', 'descanso': 'relaxing hammock', 'bosque': 'forest path', 'deporte': 'sport team', 'cocina': 'cooking vegetables'},
  'learn': {'estudiar': 'studying desk', 'libros': 'books shelf', 'lectura': 'reading book', 'aula': 'classroom', 'apuntes': 'notebook writing',
            'online': 'online course laptop', 'idiomas': 'language learning', 'memoria': 'sticky notes wall', 'escritura': 'hand writing pen', 'concentracion': 'focus work'},
  'build': {'vivienda': 'house exterior', 'llaves': 'house keys', 'dinero': 'money coins', 'ahorro': 'savings piggy bank', 'arquitectura': 'modern architecture',
            'obra': 'construction site', 'ciudad': 'city skyline', 'oficina': 'office work', 'trabajo': 'workers', 'jubilacion': 'retired couple',
            'pisos': 'apartment building', 'energia': 'solar panels'},
  'general': {'paisaje': 'landscape', 'cielo': 'sky clouds', 'mar': 'ocean waves', 'montana': 'mountains', 'naturaleza': 'nature green',
              'textura': 'paper texture', 'frases': 'sunset silhouette', 'camino': 'road journey', 'luz': 'window light'},
}
MAX = int(os.environ.get('MAX', '80'))
PK = os.environ.get('PEXELS_API_KEY', '')
ruta = sys.argv[1]
viejo = json.load(open(ruta)) if os.path.exists(ruta) else {}
idx = {m: {t: [x for x in l if 'p' in x] for t, l in ts.items()} for m, ts in viejo.items()} if viejo else {}   # el formato v1 (fotos en SiteGround) se descarta

def pedir(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'AURZANE catalogo de imagenes', 'Authorization': PK})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())

usados = {x['p'] for ts in idx.values() for l in ts.values() for x in l}   # una foto no se repite entre temas
total = 0
for mundo, temas in TEMAS.items():
    for tema, q in temas.items():
        lista = idx.setdefault(mundo, {}).setdefault(tema, [])
        pag = 1
        while len(lista) < MAX and pag <= 4:
            try: d = pedir('https://api.pexels.com/v1/search?' + urllib.parse.urlencode({'query': q, 'orientation': 'landscape', 'per_page': 80, 'page': pag, 'size': 'medium'}))
            except Exception as e: print('pexels', q, e); break
            fotos = d.get('photos', [])
            for p in fotos:
                if len(lista) >= MAX: break
                if p['id'] in usados or p.get('width', 0) < 1200: continue
                lista.append({'p': p['id'], 'a': p.get('photographer', ''), 'c': p.get('avg_color', ''), 't': (p.get('alt') or '')[:90]})
                usados.add(p['id']); total += 1
            if not d.get('next_page'): break
            pag += 1; time.sleep(0.4)
        print(f'{mundo}/{tema}: {len(lista)}')
json.dump(idx, open(ruta, 'w'), ensure_ascii=False, separators=(',', ':'))
print('Fotos nuevas:', total, '· en el catálogo:', sum(len(l) for ts in idx.values() for l in ts.values()))
