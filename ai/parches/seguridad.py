# Seguridad del ecosistema. Corre en el servidor cada día y en cada cambio de este archivo.
# 1) Ninguna página pública enlaza al admin (Google no debe encontrarlo).
# 2) Las páginas internas (admin, panel, AI, generar informe, almacén de guardados, WordPress) llevan la cabecera
#    X-Robots-Tag noindex, así Google las quita aunque alguien las enlace desde fuera.
# 3) WordPress (instalado pero sin uso público) no revela usuarios: se bloquean /wp-json/wp/v2/users, ?author= y xmlrpc.php.
# Antes de tocar un archivo guarda una copia en <web>/eliminar/seguridad-FECHA/. Uso: python3 seguridad.py <carpeta_www>
import os, re, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
INTERNAS = re.compile(r'/(admin[a-z-]*\.html|generar-informe\.html|ai/index\.html|panel/index\.html)$')
# enlaces al admin dentro de páginas públicas (pie «Estado del sistema» y similares)
ENLACE = re.compile(r'[ \t]*<a [^>]*href="https://aurzane\.com/admin\.html[^"]*"[^>]*>(?:Estado del sistema|Admin|Panel admin|Administración)</a>[ \t]*\n?', re.I)
MARCA = '# seguridad-aurzane v3'   # v3: Permissions-Policy (auditoría final, 17/11/2026)
BLOQUE = MARCA + r'''
<IfModule mod_headers.c>
<FilesMatch "^(admin[a-z-]*|generar-informe|guardados-almacen|wp-login)\.(html|php)$">
Header set X-Robots-Tag "noindex, nofollow, noarchive"
</FilesMatch>
</IfModule>
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule ^(ai|panel|privado-ai|wp-admin)(/|$) - [E=AZ_PRIV:1]
RewriteCond %{REQUEST_URI} ^/wp-json/wp/v2/users [NC,OR]
RewriteCond %{QUERY_STRING} (^|&)rest_route=/wp/v2/users [NC,OR]
RewriteCond %{QUERY_STRING} (^|&)author=\d+ [NC]
RewriteRule ^ - [F,L]
RewriteRule ^xmlrpc\.php$ - [F,L]
</IfModule>
<IfModule mod_headers.c>
Header set X-Robots-Tag "noindex, nofollow, noarchive" env=AZ_PRIV
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), usb=(), payment=(), magnetometer=(), gyroscope=()"
</IfModule>
# El almacén común de «Guardados» lo abren en un marco invisible los subdominios de aurzane.com:
# a ese archivo solo se le permite enmarcarse dentro de aurzane.com y sus subdominios.
<IfModule mod_headers.c>
<Files "guardados-almacen.html">
Header always unset X-Frame-Options
Header always set Content-Security-Policy "frame-ancestors https://aurzane.com https://*.aurzane.com"
</Files>
</IfModule>
# fin seguridad-aurzane
'''


def copia(web, ruta):
    d = os.path.join(base, web, 'eliminar', 'seguridad-' + hoy, os.path.dirname(ruta)); os.makedirs(d, exist_ok=True)
    shutil.copy2(os.path.join(base, web, 'public_html', ruta), d)


n_enl = 0
for web in WEBS:
    raiz = os.path.join(base, web, 'public_html')
    if not os.path.isdir(raiz): continue
    for dp, dn, fn in os.walk(raiz):
        dn[:] = [x for x in dn if x not in ('eliminar', 'wp-content', 'wp-includes', 'wp-admin', 'node_modules')]
        for f in fn:
            if not f.endswith(('.html', '.js')): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, raiz)
            if INTERNAS.search('/' + rel): continue
            try: s = open(p, encoding='utf-8').read()
            except Exception: continue
            if 'aurzane.com/admin.html' not in s: continue
            t = ENLACE.sub('', s)
            if t != s:
                copia(web, rel); open(p, 'w', encoding='utf-8').write(t); n_enl += 1; print('sin enlace al admin:', web, rel)
    ht = os.path.join(raiz, '.htaccess')
    s = open(ht, encoding='utf-8').read() if os.path.exists(ht) else ''
    if MARCA not in s:
        if s: copia(web, '.htaccess')
        s = re.sub(r'(^|\n)# seguridad-aurzane v\d.*?# fin seguridad-aurzane\n', r'\1', s, flags=re.S)
        open(ht, 'w', encoding='utf-8').write(BLOQUE + '\n' + s); print('cabeceras de seguridad en', web)
print('enlaces al admin quitados:', n_enl)
