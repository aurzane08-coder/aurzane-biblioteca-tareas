"""AVIF automático en los 7 dominios (16/11/2026).
Las imágenes son siempre las reales de la web (fotos, portadas, escudos): aquí solo se cambia su formato.
Cada foo.jpg / foo.png tiene al lado foo.jpg.avif (lo crea el flujo imagenes-avif.yml). Este parche escribe en cada .htaccess
la regla que sirve el .avif a los navegadores que lo aceptan (cabecera Accept) y el original al resto, con Vary: Accept
para que ninguna caché mezcle versiones. El HTML no cambia, así que vale para todo lo que publiquen los generadores."""
import os, re, sys

BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
HOSTS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
BLOQUE = """# BEGIN AURZANE-AVIF
AddType image/avif .avif
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTP_ACCEPT} image/avif
RewriteCond %{REQUEST_FILENAME}.avif -f
RewriteRule ^(.+\\.(?:jpe?g|png))$ $1.avif [T=image/avif,L]
</IfModule>
<IfModule mod_headers.c>
<FilesMatch "\\.(?i:jpe?g|png|avif)$">
Header merge Vary Accept
Header set Cache-Control "public, max-age=604800"
</FilesMatch>
</IfModule>
# END AURZANE-AVIF
"""
# Codificación en la cabecera HTTP: algunas portadas declaraban UTF-8 después del primer kilobyte (aviso de Lighthouse)
CHARSET = """# BEGIN AURZANE-CHARSET
AddDefaultCharset UTF-8
AddCharset UTF-8 .html .css .js .xml .txt .json
# END AURZANE-CHARSET
"""
for h in HOSTS:
    ht = BASE + '/' + h + '/public_html/.htaccess'
    if not os.path.exists(ht): continue
    t = open(ht, encoding='utf-8').read()
    n = re.sub(r'# BEGIN AURZANE-AVIF.*?# END AURZANE-AVIF\n?', '', t, flags=re.S)
    n = re.sub(r'# BEGIN AURZANE-CHARSET.*?# END AURZANE-CHARSET\n?', '', n, flags=re.S)
    n = BLOQUE + CHARSET + n
    if n != t:
        open(ht, 'w', encoding='utf-8').write(n); print('regla AVIF', h)
