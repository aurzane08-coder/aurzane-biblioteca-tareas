"""Carga más rápida del admin (24/11/2026). El panel usa unos 30 módulos de /core/ que se piden en cascada: un archivo
importa otros, que importan otros... y cada nivel espera al anterior (cerca de medio segundo por nivel, unos 4-5 s en
total). Este parche recorre los imports desde admin.html y pone al principio de <head> un <link rel="modulepreload">
por cada módulo, con la misma dirección exacta, para que el navegador los pida todos a la vez desde el principio.
Además deja que el navegador guarde /core/ y /panel/ una hora sin volver a preguntar (core/.htaccess, panel/.htaccess).
Repetible: quita y vuelve a poner su bloque. Copia previa en aurzane.com/eliminar/admin-precarga-FECHA/."""
import os, re, sys, shutil, datetime, posixpath
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
web = os.path.join(base, 'aurzane.com', 'public_html')
f = os.path.join(web, 'admin.html')
s = open(f, encoding='utf-8').read(); t0 = s

REF = re.compile(r'''(?:import\s*\(\s*|from\s+|import\s+)["'](\.{0,2}/[^"']+?\.js(?:\?[^"']*)?)["']''')
ENTRADA = re.compile(r'''["'](?:\.?/)?((?:core|panel)/[^"'\s)]+?\.js(?:\?[^"'\s)]*)?)["']''')


def leer(url):
    p = os.path.join(web, url.split('?')[0].lstrip('/'))
    try: return open(p, encoding='utf-8').read()
    except Exception: return None


vistos, cola = [], ['/' + u for u in dict.fromkeys(ENTRADA.findall(s)) if u.startswith('core/')]
for js in re.findall(r'<script[^>]+src=["\'](/panel/[^"\']+)["\']', s): cola.append(js)
while cola:
    u = cola.pop(0)
    if u in vistos: continue
    src = leer(u)
    if src is None: continue
    if u.startswith('/core/'): vistos.append(u)
    carpeta = posixpath.dirname(u.split('?')[0])
    for r in REF.findall(src) + ['/' + x for x in ENTRADA.findall(src)]:
        ab = r if r.startswith('/') else posixpath.normpath(posixpath.join(carpeta, r.split('?')[0])) + ('?' + r.split('?', 1)[1] if '?' in r else '')
        if ab.startswith('/core/') and ab not in vistos: cola.append(ab)

BLOQUE = '<!--az-precarga-->' + ''.join(f'<link rel="modulepreload" href="{u}">' for u in vistos) + '<!--/az-precarga-->'
s = re.sub(r'<!--az-precarga-->.*?<!--/az-precarga-->\n?', '', s, flags=re.S)
s = re.sub(r'(<head[^>]*>)', lambda m: m.group(1) + '\n' + BLOQUE + '\n', s, count=1)
if s != t0:
    copia = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-precarga-' + hoy, 'admin.html')
    os.makedirs(os.path.dirname(copia), exist_ok=True)
    if not os.path.exists(copia): shutil.copy2(f, copia)
    open(f, 'w', encoding='utf-8').write(s)
print(f'admin.html: {len(vistos)} módulos precargados')

HT = '''# az-cache (24/11/2026): el navegador guarda estos scripts una hora sin volver a preguntar
<IfModule mod_headers.c>
<FilesMatch "\\.js$">
Header set Cache-Control "public, max-age=3600, stale-while-revalidate=86400"
</FilesMatch>
</IfModule>
'''
for d in ('core', 'panel'):
    h = os.path.join(web, d, '.htaccess')
    if not os.path.isdir(os.path.dirname(h)): continue
    v = open(h, encoding='utf-8').read() if os.path.exists(h) else ''
    if 'az-cache' in v: continue
    if v:
        c = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-precarga-' + hoy, d + '.htaccess'); os.makedirs(os.path.dirname(c), exist_ok=True); shutil.copy2(h, c)
    open(h, 'w', encoding='utf-8').write(v + ('\n' if v and not v.endswith('\n') else '') + HT)
    print(f'{d}/.htaccess: caché de una hora para los .js')
