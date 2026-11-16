"""Una sola dirección por página y OVP tan protegido como el resto (16/11/2026, fase 1 de la auditoría).
- http:// y www. redirigen con 301 a https:// sin www, en los 7 dominios (antes respondían 200 y duplicaban).
- leer.html?libro=X redirige con 301 a la ficha del libro (antes lo hacía un script que ensuciaba el registro de errores).
- ovp.aurzane.com recibe HSTS y la protección contra marcos que ya tenían los otros 6 dominios.
El bloque va al principio del .htaccess para que se aplique antes que las demás reglas. Copia previa en <web>/eliminar/canonico-FECHA/.
Si una web dejara de responder, el bloque se quita solo (prueba con curl tras escribirlo)."""
import os, re, sys, shutil, datetime, subprocess
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']


def bloque(web):
    b = ['# BEGIN AURZANE-CANONICO', '<IfModule mod_rewrite.c>', 'RewriteEngine On',
         'RewriteCond %{HTTPS} off [OR]', 'RewriteCond %{HTTP_HOST} ^www\\. [NC]',
         f'RewriteRule ^ https://{web}%{{REQUEST_URI}} [R=301,L,NE]']
    if web == 'aurzane.com':
        b += ['RewriteCond %{QUERY_STRING} (^|&)libro=([a-z0-9-]+)(&|$)', 'RewriteRule ^biblioteca/leer\\.html$ /biblioteca/libro/%2.html? [R=301,L]']
    b += ['</IfModule>']
    if web == 'ovp.aurzane.com':
        b += ['<IfModule mod_headers.c>', 'Header always set Strict-Transport-Security "max-age=31536000"',
              'Header always set X-Frame-Options "SAMEORIGIN"',
              'Header always set Content-Security-Policy "frame-ancestors \'self\' https://aurzane.com https://*.aurzane.com"', '</IfModule>']
    return '\n'.join(b + ['# END AURZANE-CANONICO']) + '\n'


def responde(web):
    try:
        o = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-m', '20', f'https://{web}/'], capture_output=True, text=True, timeout=30).stdout
        return o.strip()
    except Exception: return 'ERR'


for web in WEBS:
    ht = os.path.join(base, web, 'public_html', '.htaccess')
    if not os.path.exists(ht): continue
    s = open(ht, encoding='utf-8').read()
    limpio = re.sub(r'# BEGIN AURZANE-CANONICO.*?# END AURZANE-CANONICO\n?', '', s, flags=re.S)
    n = bloque(web) + limpio
    if n == s: continue
    c = os.path.join(base, web, 'eliminar', 'canonico-' + hoy); os.makedirs(c, exist_ok=True); shutil.copy2(ht, c)
    open(ht, 'w', encoding='utf-8').write(n)
    r = responde(web)
    if r != '200':
        open(ht, 'w', encoding='utf-8').write(s); print('REVERTIDO', web, 'respondía', r)
    else: print('canónico y cabeceras en', web)

# Plantillas articulo.html de cada mundo (lector de artículos de la base de datos): sin rayas largas en el título,
# imagen con alt y noindex cuando se abre sin ?slug= (la plantilla vacía no debe aparecer en Google).
NOIDX = "<script>if(!/[?&]slug=/.test(location.search)){var m=document.createElement('meta');m.name='robots';m.content='noindex, follow';document.head.appendChild(m);}</script>"
for web in WEBS:
    f = os.path.join(base, web, 'public_html', 'articulo.html')
    if not os.path.exists(f): continue
    s = open(f, encoding='utf-8').read()
    t = s.replace('<img class="portada" id="artImg" hidden>', '<img class="portada" id="artImg" alt="" hidden>')
    t = t.replace('Artículo — AURZANE</title>', 'Artículo | AURZANE</title>').replace("' — AURZANE '", "' | AURZANE '")
    if NOIDX not in t: t = re.sub(r'(<title id="pageTitle">[^<]*</title>)', lambda m: m.group(1) + '\n' + NOIDX, t, count=1)
    if t != s:
        c = os.path.join(base, web, 'eliminar', 'canonico-' + hoy); os.makedirs(c, exist_ok=True); shutil.copy2(f, c)
        open(f, 'w', encoding='utf-8').write(t); print('plantilla de artículo arreglada en', web)
