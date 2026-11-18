"""Hoja de fotos candidatas para portadas: busca en Wikimedia Commons fotos reales (JPEG) con licencia libre y hace
una lámina numerada por curso en cursos/candidatas/<slug>.jpg con sus datos en <slug>.json, para elegir a ojo."""
import json, os, io, re, urllib.request, urllib.parse
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(R, 'candidatas'); os.makedirs(D, exist_ok=True)
UA = {'User-Agent': 'AURZANE-cursos/1.0 (hola@aurzane.com)'}
LIC = re.compile(r'^(CC BY(-SA)? [0-9.]+|CC0|Public domain|PD)', re.I)
BUSQ = json.loads(os.environ.get('BUSQUEDAS', '{}'))
for slug, qs in BUSQ.items():
    cand = {}
    for q in qs:
        u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
            'gsrsearch': q + ' filetype:bitmap', 'gsrlimit': 40, 'prop': 'imageinfo', 'iiprop': 'url|size|mime|extmetadata', 'iiurlwidth': 400})
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r: pags = (json.load(r).get('query') or {}).get('pages', {}).values()
        for pg in pags:
            ii = (pg.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata') or {}
            lic = (md.get('LicenseShortName') or {}).get('value', ''); w, h = ii.get('width', 0), ii.get('height', 0)
            if ii.get('mime') != 'image/jpeg' or not LIC.match(lic) or w < 1600 or not h or not 1.3 <= w / h <= 2.0: continue
            cand[pg['title']] = {'titulo': pg['title'], 'licencia': lic, 'autor': re.sub(r'<[^>]+>', '', (md.get('Artist') or {}).get('value', '')).strip()[:100], 'thumb': ii.get('thumburl'), 'pagina': ii.get('descriptionurl')}
    cand = list(cand.values())[:24]
    tiles = []
    for i, c in enumerate(cand):
        try:
            with urllib.request.urlopen(urllib.request.Request(c['thumb'], headers=UA), timeout=60) as r: im = Image.open(io.BytesIO(r.read())).convert('RGB')
            im.thumbnail((400, 260)); t = Image.new('RGB', (400, 290), 'white'); t.paste(im, (0, 0)); ImageDraw.Draw(t).text((6, 266), f'{i}', fill='black'); tiles.append(t)
        except Exception as e: tiles.append(Image.new('RGB', (400, 290), 'gray'))
    if tiles:
        cols = 4; hoja = Image.new('RGB', (400 * cols, 290 * ((len(tiles) + cols - 1) // cols)), 'white')
        for i, t in enumerate(tiles): hoja.paste(t, (400 * (i % cols), 290 * (i // cols)))
        hoja.save(os.path.join(D, slug + '.jpg'), quality=70)
    json.dump(cand, open(os.path.join(D, slug + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(slug, len(cand), 'candidatas')
