# -*- coding: utf-8 -*-
"""Descarga los PDF seleccionados (cosecha/seleccion.json), los verifica, une los que vienen
en varias partes, cuenta páginas, hace la portada y los deja en el tránsito de Supabase.
Se ejecuta en GitHub Actions."""
import json, os, subprocess, hashlib, base64, urllib.request, urllib.parse, time, sys, re
DIR = os.environ.get('DIR', 'cosecha')
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/storage/v1/object/biblioteca-transito/'
UA = {'User-Agent': 'Mozilla/5.0 (AURZANE-Biblioteca/1.0; +https://aurzane.com/biblioteca/)'}
LIM = 45 * 1048576
def bajar(url, dest):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r, open(dest, 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b)
                    if f.tell() > 160 * 1048576: raise Exception('demasiado grande')
            return
        except Exception as e:
            err = e; time.sleep(3 + 5 * i)
    raise err
def subir(path, datos, tipo):
    r = urllib.request.Request(SB + path, data=datos, method='POST', headers={'apikey': KEY, 'authorization': 'Bearer ' + KEY, 'content-type': tipo})
    try: return urllib.request.urlopen(r, timeout=300).status
    except urllib.error.HTTPError as e: return '%s %s' % (e.code, e.read()[:120])
def volcar():
    global portadas
    if not portadas: return
    lote = ('v3/' if DIR != 'cosecha' else 'v2/') + 'portadas-%d.json' % int(time.time())
    print('portadas', len(portadas), subir(lote, json.dumps(portadas).encode(), 'application/json'), lote)
    lotes = json.load(open(DIR + '/portadas-lotes.json')) if os.path.exists(DIR + '/portadas-lotes.json') else []
    lotes.append({'lote': lote, 'ids': sorted(portadas)}); json.dump(lotes, open(DIR + '/portadas-lotes.json', 'w'), indent=0)
    portadas = {}

sel = json.load(open(DIR + '/seleccion.json'))
hecho = json.load(open(DIR + '/descargas.json')) if os.path.exists(DIR + '/descargas.json') else {}
INF = DIR + '/portadas-informe.json'
informe = json.load(open(INF)) if os.path.exists(INF) else {}
META = {b['id']: b for b in __import__('nuevos2').NUEVOS2} if DIR != 'cosecha' else {}
def ia_pdf(u):
    m = re.match(r'https://archive\.org/download/([^/]+)/', u)
    if not m: return u
    md = json.loads(urllib.request.urlopen(urllib.request.Request('https://archive.org/metadata/' + m.group(1), headers=UA), timeout=60).read())
    fs = [f for f in md.get('files', []) if f.get('name', '').lower().endswith('.pdf')]
    if not fs: raise Exception('sin PDF')
    f = next((f for f in fs if f.get('format') == 'Text PDF'), None) or max(fs, key=lambda f: int(f.get('size') or 0))
    return 'https://archive.org/download/%s/%s' % (m.group(1), urllib.parse.quote(f['name']))
def html_a_pdf(u, dest):
    subprocess.run(['google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--no-pdf-header-footer', '--virtual-time-budget=20000', '--print-to-pdf=' + dest, u], check=True, timeout=300, capture_output=True)
os.makedirs('/tmp/pdf', exist_ok=True); portadas = {}
PRESUPUESTO = float(os.environ.get('PRESUPUESTO_MB', '700')) * 1048576; subido = 0
for x in sel:
    if hecho.get(x['id'], {}).get('ok') or hecho.get(x['id'], {}).get('definitivo'): continue
    if subido > PRESUPUESTO: print('presupuesto agotado'); break
    res = {'ok': False}
    try:
        partes = []
        if x.get('transito'):
            x['pdfs'] = ['https://chtfpqwrrarfdjcivlad.supabase.co/storage/v1/object/public/biblioteca-transito/' + p for p in x['transito']]
        if not x.get('pdfs'):
            crudo = urllib.request.urlopen(urllib.request.Request(x['bundles'], headers=dict(UA, Accept='application/json')), timeout=60).read()
            try: b = json.loads(crudo)
            except Exception: raise Exception('bundles no JSON: %s | %s' % (x['bundles'][:70], crudo[:150]))
            orig = [z for z in b.get('_embedded', {}).get('bundles', []) if z['name'] == 'ORIGINAL']
            bs = json.loads(urllib.request.urlopen(urllib.request.Request(orig[0]['_links']['bitstreams']['href'] + '?size=100', headers=dict(UA, Accept='application/json')), timeout=60).read())['_embedded']['bitstreams']
            bs = [f for f in bs if f['name'].lower().endswith('.pdf')]
            if not bs: raise Exception('sin PDF')
            mayor = max(bs, key=lambda f: f['sizeBytes'])
            if mayor['sizeBytes'] > 0.7 * sum(f['sizeBytes'] for f in bs): bs = [mayor]
            if sum(f['sizeBytes'] for f in bs) > 150 * 1048576: raise Exception('demasiado grande')
            x['pdfs'] = [f['_links']['content']['href'] for f in bs]
        for i, u in enumerate(x['pdfs']):
            d = '/tmp/pdf/%s-%d.pdf' % (x['id'], i)
            if u.endswith('.html'): html_a_pdf(u, d)
            else: bajar(ia_pdf(u), d)
            if open(d, 'rb').read(5) != b'%PDF-': raise Exception('no es PDF')
            partes.append(d)
        f = '/tmp/pdf/%s.pdf' % x['id']
        if len(partes) == 1: os.rename(partes[0], f)
        else: subprocess.run(['qpdf', '--empty', '--pages'] + partes + ['--', f], check=True)
        if os.path.getsize(f) > 8 * 1048576:
            g = f + '.gs.pdf'
            subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-dPDFSETTINGS=/ebook', '-sOutputFile=' + g, f], timeout=900)
            if os.path.exists(g) and os.path.getsize(g) < 0.8 * os.path.getsize(f): os.replace(g, f)
        tam = os.path.getsize(f); res['mb'] = round(tam / 1048576, 1)
        if tam > LIM: raise Exception('supera 45 MB (%s)' % res['mb'])
        info = subprocess.run(['pdfinfo', f], capture_output=True, text=True).stdout
        res['paginas'] = int(next((l.split()[-1] for l in info.splitlines() if l.startswith('Pages:')), 0))
        from portada_util import mejor_portada, jpg
        b = META.get(x['id'], {})
        im, origen = mejor_portada(f, x.get('isbn', []), b.get('titulo', ''), b.get('autores', ''), b.get('anio', ''))
        informe[x['id']] = {'estado': 'nueva' if origen and not origen.startswith('Primera') else ('portada' if origen else 'tipografica'), 'origen': origen}
        if origen: portadas[x['id']] = base64.b64encode(jpg(im)).decode()
        json.dump(informe, open(INF, 'w'), ensure_ascii=False, indent=0)
        datos = open(f, 'rb').read(); res['sha1'] = hashlib.sha1(datos).hexdigest()
        st = subir(('v3/' if DIR != 'cosecha' else 'v2/') + '%s.pdf' % x['id'], datos, 'application/pdf')
        if st != 200 and not ('409' in str(st) or 'Duplicate' in str(st)): raise Exception('subida %s' % st)
        res['ok'] = True; res['lote'] = os.environ.get('LOTE', '1'); subido += tam; os.remove(f)
    except Exception as e:
        res['err'] = str(e)[:150]; res['definitivo'] = any(k in res['err'] for k in ('no es PDF', 'supera', 'sin PDF', 'demasiado grande', '404'))
    for z in os.listdir('/tmp/pdf'): os.remove('/tmp/pdf/' + z)
    hecho[x['id']] = res; print(x['id'], res, flush=True)
    if len(portadas) >= 30: volcar()
    json.dump(hecho, open(DIR + '/descargas.json', 'w'), ensure_ascii=False, indent=0)
volcar()
print('ok', sum(1 for v in hecho.values() if v.get('ok')), 'fallos', sum(1 for v in hecho.values() if not v.get('ok')))
