"""Política de seguridad del navegador (CSP) en modo SOLO INFORME en los 7 dominios (16/11/2026).
No bloquea nada: el navegador avisa a aurzane.com/ai/csp.php de cualquier script de un origen no previsto.
Tras dos semanas sin avisos legítimos se podrá pasar a modo activo (cambiar Report-Only por la cabecera normal)."""
import os, re, sys, datetime
BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
HOSTS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
POL = ("script-src 'self' 'unsafe-inline' https://aurzane.com https://*.aurzane.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com "
       "https://*.googlesyndication.com https://*.google.com https://*.gstatic.com https://*.doubleclick.net https://*.adtrafficquality.google "
       "https://*.googletagservices.com https://*.googleadservices.com https://*.supabase.co; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; "
       "report-uri https://aurzane.com/ai/csp.php")
def activa():
    if datetime.date.today() < datetime.date(2026, 11, 30): return False
    log = BASE + '/aurzane.com/privado-ai/csp.log'
    if not os.path.exists(log): return True
    lim = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
    return not any(l[:16] >= lim for l in open(log, encoding='utf-8', errors='ignore'))
CAB = 'Content-Security-Policy' if activa() else 'Content-Security-Policy-Report-Only'
BLOQUE = f"""# BEGIN AURZANE-CSP
<IfModule mod_headers.c>
<FilesMatch "\\.(html|php)$">
Header set {CAB} "{POL}"
</FilesMatch>
</IfModule>
# END AURZANE-CSP
"""
for h in HOSTS:
    ht = BASE + '/' + h + '/public_html/.htaccess'
    if not os.path.exists(ht): continue
    t = open(ht, encoding='utf-8').read()
    n = re.sub(r'# BEGIN AURZANE-CSP.*?# END AURZANE-CSP\n?', '', t, flags=re.S) + '\n' + BLOQUE
    n = re.sub(r'\n{3,}', '\n\n', n)
    if n != t: open(ht, 'w', encoding='utf-8').write(n); print('CSP', 'activa' if CAB == 'Content-Security-Policy' else 'en modo informe', h)
