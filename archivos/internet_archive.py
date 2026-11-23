"""Mudanza de archivos pesados de SiteGround a Internet Archive (22/11/2026, pedido de Adrián: el servidor se quedaba sin espacio).
Qué se muda:
  - PDF de la biblioteca con licencia que permite redistribuir (dominio público y Creative Commons). Los de licencia desconocida se quedan.
  - Vídeos y música de marketing con más de DIAS_MARKETING días (los recientes los usan las redes al publicar).
Cómo, en dos pasos por archivo (manifiesto www/.ia-archivos.tsv en el servidor):
  1. subido:  se sube a archive.org (un elemento por libro; vídeo y música en elementos por mes) y se anota.
  2. movido:  en una ejecución posterior, si archive.org lo sirve entero (mismo tamaño) y con CORS, se quita del servidor.
              La web no cambia de enlaces: el .htaccess redirige cada archivo que ya no está en el servidor a su copia en archive.org.
Uso: S='ssh ...' python3 archivos/internet_archive.py lista.tsv catalogo.js manifiesto.tsv"""
import os, re, sys, json, time, subprocess, urllib.request
import internetarchive as ia

ACC, SEC = os.environ['IA_ACCESS'], os.environ['IA_SECRET']
LOTE = int(os.environ.get('LOTE', '20'))            # archivos por ejecución (archive.org frena si se crean demasiados seguidos)
DIAS_MARKETING = int(os.environ.get('DIAS_MARKETING', '21'))
lista, catalogo, manif = sys.argv[1:4]

def lic_ok(l):
    l = (l or '').lower()
    return 'dominio p' in l or 'public domain' in l or l.startswith('cc ') or l.startswith('cc0')

def lic_url(l, u):
    if u: return u
    if 'dominio' in (l or '').lower(): return 'https://creativecommons.org/publicdomain/mark/1.0/'
    return ''

# catálogo de la biblioteca: id → datos (window.BIBLIOTECA = {...};)
txt = open(catalogo, encoding='utf-8').read()
cat = json.loads(txt[txt.index('{'):txt.rindex('}') + 1])
libros = {os.path.basename(l.get('pdf') or ''): l for l in cat.get('libros', []) if l.get('pdf')}

hecho = {}
if os.path.exists(manif):
    for l in open(manif, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 4: hecho[p[0]] = p   # ruta, estado, identificador, tamaño

def ident(ruta):
    b = os.path.basename(ruta); n = re.sub(r'\.[^.]+$', '', b)
    if ruta.startswith('biblioteca/pdf/'): return 'aurzane-bib-' + n
    if ruta.startswith('biblioteca/recientes/pdf/'): return 'aurzane-rec-' + n
    m = re.match(r'marketing/(video|musica)/', ruta)
    return f'aurzane-marketing-{m.group(1)}' if m else None

def url_ia(i, ruta): return f'https://archive.org/download/{i}/{os.path.basename(ruta)}'

def comprobar(i, ruta, tam):
    """archive.org sirve el archivo entero y con CORS (el lector de PDF de la web lo necesita).
    Se pide solo el primer byte con GET: archive.org no siempre manda las cabeceras CORS a una petición HEAD."""
    try:
        r = urllib.request.Request(url_ia(i, ruta), headers={'Origin': 'https://aurzane.com', 'User-Agent': 'AURZANE', 'Range': 'bytes=0-0'})
        with urllib.request.urlopen(r, timeout=60) as x:
            total = (x.headers.get('Content-Range') or '').rpartition('/')[2] or x.headers.get('Content-Length')
            ok_tam = str(total) == str(tam)
            cors = x.headers.get('Access-Control-Allow-Origin') in ('*', 'https://aurzane.com')
            if not cors and not getattr(comprobar, 'visto', 0):
                comprobar.visto = 1; print('  cabeceras de archive.org (sin CORS):', dict(x.headers))
            return ok_tam, cors
    except Exception as e:
        print('  aún no disponible:', ruta, e); return False, False

nuevos, para_quitar, sin_cors = [], [], 0
filas = [l.rstrip('\n').split('\t') for l in open(lista, encoding='utf-8') if l.strip()]   # ruta, tamaño, días de antigüedad
# 1) lo ya subido: ¿se puede quitar del servidor?
for ruta, tam, dias in filas:
    h = hecho.get(ruta)
    if h and h[1] == 'subido':
        ok, cors = comprobar(h[2], ruta, tam)
        # archive.org no manda CORS: los lectores de la web (biblioteca/leer.js y las fichas de recientes) usan entonces el lector de archive.org
        if ok: para_quitar.append(ruta); h[1] = 'movido'
        if ok and not cors: sin_cors += 1
open('quitar.txt', 'w').write(''.join(r + '\n' for r in para_quitar))   # se escribe ya, por si la subida se alarga
print(f'Comprobados: listos para quitar del servidor {len(para_quitar)}, sin CORS {sin_cors}.', flush=True)
# 2) subir un lote nuevo, con tiempo tasado para que siempre quede margen para quitar lo comprobado
subidos, T0 = 0, time.time()
for ruta, tam, dias in filas:
    if subidos >= LOTE or time.time() - T0 > 40 * 60: break
    if ruta in hecho: continue
    i = ident(ruta)
    if not i or not re.fullmatch(r'[A-Za-z0-9._-]{1,100}', i): continue
    md = {'mediatype': 'texts', 'collection': 'opensource', 'creator': 'AURZANE', 'language': 'spa'}
    if ruta.startswith('biblioteca/pdf/'):
        l = libros.get(os.path.basename(ruta))
        if not l or not lic_ok(l.get('licencia')): continue
        md.update({'title': l.get('titulo', ''), 'creator': l.get('autores') or 'AURZANE', 'date': str(l.get('anio') or ''),
                   'publisher': l.get('editorial', ''), 'source': l.get('url', ''), 'licenseurl': lic_url(l.get('licencia'), l.get('licencia_url')),
                   'rights': l.get('licencia', ''), 'subject': 'psicología; AURZANE biblioteca', 'description': (l.get('resumen') or '') + ' Copia de la Biblioteca AURZANE (aurzane.com/biblioteca).'})
    elif ruta.startswith('biblioteca/recientes/pdf/'):
        # «Libros abiertos y estudios recientes»: solo se alojan en AURZANE los que tienen licencia libre que lo permite
        md.update({'title': 'AURZANE · ' + os.path.basename(ruta), 'subject': 'psicología; acceso abierto; AURZANE biblioteca',
                   'description': 'Obra en acceso abierto con licencia libre, alojada por la Biblioteca AURZANE (aurzane.com/biblioteca/recientes).'})
    else:
        if int(dias) < DIAS_MARKETING: continue
        tipo = 'video' if '/video/' in ruta else 'musica'
        md.update({'mediatype': 'movies' if tipo == 'video' else 'audio', 'collection': 'opensource_movies' if tipo == 'video' else 'opensource_audio',
                   'title': f'AURZANE marketing ({tipo})', 'description': 'Material de difusión de AURZANE (aurzane.com).'})
    local = os.path.join('bajados', ruta); os.makedirs(os.path.dirname(local), exist_ok=True)
    with open(local, 'wb') as f:   # se trae del servidor justo antes de subirlo (el disco del runner es limitado)
        subprocess.run(os.environ['S'] + ' ' + "'cat ~/www/aurzane.com/public_html/" + ruta.replace("'", "") + "'", shell=True, stdout=f)
    if str(os.path.getsize(local)) != str(tam): print('descarga incompleta', ruta); os.remove(local); continue
    try:
        r = ia.upload(i, {os.path.basename(ruta): local}, metadata=md, access_key=ACC, secret_key=SEC, retries=5, retries_sleep=20, verbose=False, checksum=True)
        if all(getattr(x, 'status_code', 200) in (200, None) for x in r):
            hecho[ruta] = [ruta, 'subido', i, tam]; subidos += 1; print('subido', ruta, '→', i)
            open(manif, 'w', encoding='utf-8').write(''.join('\t'.join(v) + '\n' for v in hecho.values()))   # se guarda tras cada archivo
    except Exception as e:
        print('fallo al subir', ruta, e)
    finally:
        if os.path.exists(local): os.remove(local)
open(manif, 'w', encoding='utf-8').write(''.join('\t'.join(v) + '\n' for v in hecho.values()))
open('quitar.txt', 'w').write(''.join(r + '\n' for r in para_quitar))
print(f'Subidos ahora: {subidos}. Listos para quitar del servidor: {len(para_quitar)}. Sin CORS (se quedan): {sin_cors}.')
