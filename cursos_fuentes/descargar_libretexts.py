"""Descarga un libro de LibreTexts Español con licencia CC BY para adaptarlo como curso de AURZANE LEARN.
Guarda cada sección como HTML limpio en cursos_fuentes/<carpeta>/ con su URL y licencia.
Uso: LIBRO=<url del índice> CARPETA=<nombre> python cursos_fuentes/descargar_libretexts.py"""
import os, re, time, json, urllib.request, html
from urllib.parse import urljoin, unquote
LIBRO = os.environ['LIBRO'].rstrip('/'); CARPETA = os.environ['CARPETA']
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), CARPETA); os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'AURZANE-cursos/1.0 (hola@aurzane.com; adaptación CC BY con atribución)'}
def get(u):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r: return r.read().decode('utf-8', 'replace')
        except Exception as e: print('reintento', u, e); time.sleep(5)
    return ''
def enlaces(pagina, base):
    hijos = []
    for m in re.finditer(r'href="(https://espanol\.libretexts\.org[^"#?]+)"', pagina):
        u = m.group(1)
        if u.startswith(base + '/') and u not in hijos and '/' not in u[len(base) + 1:].strip('/'): hijos.append(u)
    return hijos
def contenido(pagina):
    m = re.search(r'<div[^>]+class="[^"]*mt-content-container[^"]*"[^>]*>(.*?)<footer', pagina, re.S)
    t = m.group(1) if m else ''
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    return t
if os.environ.get('CRUDO'):
    # diagnóstico: guarda una página tal cual para ver dónde está el texto
    open(os.path.join(OUT, 'crudo.html'), 'w', encoding='utf-8').write(get(os.environ['CRUDO'])); raise SystemExit
indice = get(LIBRO)
lic = re.findall(r'CC BY[^"<]{0,20}', indice)[:3]
print('licencia detectada:', lic)
assert lic and not any('NC' in x for x in lic), 'El libro no es CC BY o CC BY-SA: no se descarga'
caps = enlaces(indice, LIBRO)
print(len(caps), 'capítulos')
meta = {'libro': LIBRO, 'licencia': lic[0], 'secciones': []}
for i, cap in enumerate(caps, 1):
    pc = get(cap); time.sleep(1)
    secs = enlaces(pc, cap) or [cap]
    for j, sec in enumerate(secs, 1):
        ps = pc if sec == cap else get(sec); time.sleep(1)
        tit = html.unescape((re.search(r'<title>(.*?)</title>', ps, re.S) or [None, ''])[1]).split(' - ')[0].strip()
        nom = f'{i:02d}-{j:02d}.html'
        open(os.path.join(OUT, nom), 'w', encoding='utf-8').write(f'<!-- {sec} -->\n<h1>{html.escape(tit)}</h1>\n' + contenido(ps))
        meta['secciones'].append({'archivo': nom, 'capitulo': i, 'titulo': tit, 'url': sec})
        print(nom, tit)
json.dump(meta, open(os.path.join(OUT, 'indice.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
