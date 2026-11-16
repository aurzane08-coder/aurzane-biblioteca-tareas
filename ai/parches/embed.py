"""Calculadoras insertables en otras webs (16/11/2026).
Con ?embed=1, las calculadoras de LIVE, BUILD y NEXUS se pueden mostrar dentro de otra web (marco), sin indexarse
dos veces en Google. Sin ese parámetro siguen protegidas como hasta ahora (solo se enmarcan dentro de aurzane.com).
La página https://aurzane.com/insertar/ da el código para copiar."""
import os, re, sys
BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
BLOQUE = """# BEGIN AURZANE-EMBED
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{QUERY_STRING} (^|&)embed=1(&|$)
RewriteRule ^calculadora- - [E=AZ_EMBED:1]
</IfModule>
<IfModule mod_headers.c>
Header always set Content-Security-Policy "frame-ancestors *" env=AZ_EMBED
Header always set Content-Security-Policy "frame-ancestors *" env=REDIRECT_AZ_EMBED
Header always set X-Robots-Tag "noindex, follow" env=AZ_EMBED
Header always set X-Robots-Tag "noindex, follow" env=REDIRECT_AZ_EMBED
</IfModule>
# END AURZANE-EMBED
"""
for h in ['live.aurzane.com', 'build.aurzane.com', 'nexus.aurzane.com']:
    ht = BASE + '/' + h + '/public_html/.htaccess'
    if not os.path.exists(ht): continue
    t = open(ht, encoding='utf-8').read()
    n = re.sub(r'\n?# BEGIN AURZANE-EMBED.*?# END AURZANE-EMBED\n?', '\n', t, flags=re.S).rstrip('\n') + '\n\n' + BLOQUE   # siempre al final: manda sobre las reglas anteriores
    if n != t: open(ht, 'w', encoding='utf-8').write(n); print('insertables', h)
