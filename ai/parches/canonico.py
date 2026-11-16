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

# Imagen para compartir (og.jpg, 1200x630) de las calculadoras nuevas: foto real de Unsplash, la misma que su tarjeta.
OG = {'build.aurzane.com/calculadora-gastos-compra-vivienda': '1570129477492-45c003edd2be', 'build.aurzane.com/calculadora-rentabilidad-alquiler': '1460317442991-0ec209397118',
      'build.aurzane.com/calculadora-finiquito': '1586281380349-632531db7ed4', 'build.aurzane.com/calculadora-ahorro': '1559526324-4b87b5e36e44',
      'build.aurzane.com/calculadora-jubilacion': '1473186578172-c141e6798cf4', 'live.aurzane.com/calculadora-ovulacion': '1505751172876-fa1923c5c528',
      'live.aurzane.com/calculadora-peso-ideal': '1517836357463-d25dfeac3438', 'live.aurzane.com/calculadora-sueno': '1520206183501-b80df61043c2'}
for ruta, fid in OG.items():
    web, carpeta = ruta.split('/', 1)
    f = os.path.join(base, web, 'public_html', carpeta, 'og.jpg')
    if not os.path.isdir(os.path.dirname(f)) or (os.path.exists(f) and os.path.getsize(f) > 5000): continue
    u = f'https://images.unsplash.com/photo-{fid}?w=1200&h=630&fit=crop&q=75&fm=jpg'
    r = subprocess.run(['curl', '-sL', '-m', '60', '-o', f, '-w', '%{http_code}', u], capture_output=True, text=True)
    if r.stdout.strip() == '200' and os.path.exists(f) and os.path.getsize(f) > 5000: print('og.jpg descargada', ruta)
    elif os.path.exists(f):   # descarga fallida: se aparta a eliminar (nunca se borra)
        c = os.path.join(base, web, 'eliminar', 'canonico-' + hoy); os.makedirs(c, exist_ok=True); shutil.move(f, os.path.join(c, carpeta.replace('/', '_') + '-og.jpg'))
for ruta in OG:
    web, carpeta = ruta.split('/', 1)
    f = os.path.join(base, web, 'public_html', carpeta, 'index.html'); og = os.path.join(base, web, 'public_html', carpeta, 'og.jpg')
    if not (os.path.exists(f) and os.path.exists(og)): continue
    s = open(f, encoding='utf-8').read()
    t = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")https://' + re.escape(web) + r'/[a-z0-9-]+/og\.jpg(")', lambda m: m.group(1) + f'https://{web}/{carpeta}/og.jpg' + m.group(2), s)
    if t != s: open(f, 'w', encoding='utf-8').write(t); print('og:image propia en', ruta)

# Tipos generales de ITP/AJD de 2026 revisados (auditoría 16/11/2026): Cantabria 9 %, Comunitat Valenciana 9 % (desde el 1/6/2026) y AJD 1,4 %,
# Galicia 8 % y Región de Murcia 7,75 %. Se corrigen en la calculadora de hipoteca y en la de gastos de compra, que comparten la tabla.
ITP = [("['Cantabria',10,1.5,10]", "['Cantabria',9,1.5,10]"), ("['Comunidad Valenciana',10,1.5,10]", "['Comunidad Valenciana',9,1.4,10]"),
       ("['Galicia',10,1.5,10]", "['Galicia',8,1.5,10]"), ("['Región de Murcia',8,1.5,10]", "['Región de Murcia',7.75,1.5,10]")]
for carpeta in ('calculadora-hipoteca', 'calculadora-gastos-compra-vivienda'):
    f = os.path.join(base, 'build.aurzane.com', 'public_html', carpeta, 'index.html')
    if not os.path.exists(f): continue
    s = open(f, encoding='utf-8').read(); t = s
    for a, b in ITP: t = t.replace(a, b)
    if t != s:
        c = os.path.join(base, 'build.aurzane.com', 'eliminar', 'canonico-' + hoy); os.makedirs(c, exist_ok=True); shutil.copy2(f, os.path.join(c, carpeta + '.html'))
        open(f, 'w', encoding='utf-8').write(t); print('tipos de ITP de 2026 en', carpeta)
