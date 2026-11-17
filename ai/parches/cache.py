"""Caché del navegador para los archivos estáticos (17/11/2026, etapa 2 de la auditoría, tarea 27: carga lenta).
Hasta ahora todo salía con «no-cache, must-revalidate»: cada visita volvía a preguntar al servidor por cada hoja de
estilos y cada script, con unos 500 ms de espera cada vez. Ahora:
- CSS y JS pedidos con ?v=N (versionados): un año, porque al cambiar el archivo cambia el número.
- Fuentes woff2: un año (tienen nombre fijo por versión).
- Imágenes: 7 días.
- aurzane-paleta.js (el cargador, sin versión): 10 minutos, para que los cambios lleguen rápido.
Las páginas HTML no se tocan. El bloque va al final del .htaccess; si una web deja de responder 200 se quita solo.
Copia previa en <web>/eliminar/cache-FECHA/."""
import os, re, sys, shutil, datetime, subprocess
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
BLOQUE = '''# BEGIN AURZANE-CACHE
<IfModule mod_headers.c>
<If "%{QUERY_STRING} =~ /(^|&)v=[0-9A-Za-z._-]+/ && %{REQUEST_URI} =~ /\\.(css|js)$/">
Header set Cache-Control "public, max-age=31536000, immutable"
</If>
<FilesMatch "\\.woff2$">
Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>
<FilesMatch "\\.(webp|avif|jpe?g|png|gif|svg|ico)$">
Header set Cache-Control "public, max-age=604800"
</FilesMatch>
<Files "aurzane-paleta.js">
Header set Cache-Control "public, max-age=600"
</Files>
</IfModule>
# END AURZANE-CACHE
'''


def codigo(url):
    try:
        return subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-m', '20', url], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception: return 'ERR'


for web in WEBS:
    ht = os.path.join(base, web, 'public_html', '.htaccess')
    if not os.path.exists(ht): continue
    s = open(ht, encoding='utf-8').read()
    limpio = re.sub(r'# BEGIN AURZANE-CACHE.*?# END AURZANE-CACHE\n?', '', s, flags=re.S)
    n = limpio.rstrip('\n') + '\n\n' + BLOQUE
    if n == s: continue
    c = os.path.join(base, web, 'eliminar', 'cache-' + hoy); os.makedirs(c, exist_ok=True); shutil.copy2(ht, c)
    open(ht, 'w', encoding='utf-8').write(n)
    r1 = codigo(f'https://{web}/'); r2 = codigo('https://aurzane.com/aurzane-paleta.js') if web == 'aurzane.com' else '200'
    if r1 != '200' or r2 != '200':
        open(ht, 'w', encoding='utf-8').write(s); print(f'::warning::REVERTIDO {web}: respondía {r1}/{r2}')
    else: print('caché del navegador activada en', web)
