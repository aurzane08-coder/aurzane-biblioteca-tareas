"""Retira el WordPress antiguo de aurzane.com sin borrar nada (16/11/2026).
No servía ninguna página pública (solo plantillas de ejemplo: about-us, case-studies...), pero seguía activo con 15 plugins.
1) Copia de la base de datos con wp db export.
2) Mueve el núcleo, wp-content e index.php a www/aurzane.com/eliminar/wordpress-<fecha>/.
3) Quita del .htaccess los bloques de WordPress y de SiteGround Optimizer (el «Header unset Vary» impedía servir AVIF bien).
4) Página 404 propia en los 7 dominios (copia de aurzane.com/404.html) con ErrorDocument.
Se puede ejecutar a diario: si WordPress ya no está, solo comprueba el .htaccess y la 404."""
import os, re, sys, shutil, subprocess, datetime

BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
RAIZ = BASE + '/aurzane.com/public_html'
HOSTS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
F = datetime.date.today().strftime('%Y%m%d')

if os.path.exists(RAIZ + '/wp-config.php'):
    dest = BASE + '/aurzane.com/eliminar/wordpress-' + F
    os.makedirs(dest, exist_ok=True)
    r = subprocess.run(['wp', 'db', 'export', dest + '/base-de-datos-wordpress.sql', '--path=' + RAIZ], capture_output=True, text=True)
    print('copia de la base de datos:', 'ok' if r.returncode == 0 else 'ERROR ' + r.stderr[-300:])
    if r.returncode != 0:
        sys.exit('No se mueve nada sin copia de la base de datos.')
    shutil.copy2(RAIZ + '/.htaccess', dest + '/htaccess-antes.txt')
    for n in sorted(os.listdir(RAIZ)):
        if n.startswith('wp-') or n in ('xmlrpc.php', 'index.php', 'license.txt', 'readme.html', 'licencia.txt'):
            shutil.move(os.path.join(RAIZ, n), os.path.join(dest, n)); print('movido', n)
else:
    print('WordPress ya retirado')

pag404 = RAIZ + '/404.html'
for h in HOSTS:
    raiz = BASE + '/' + h + '/public_html'
    ht = raiz + '/.htaccess'
    t = open(ht, encoding='utf-8').read() if os.path.exists(ht) else ''
    a = t
    t = re.sub(r'\n?# BEGIN WordPress.*?# END WordPress\n?', '\n', t, flags=re.S)
    t = re.sub(r'\n?# SGS XMLRPC Disable Service.*?# SGS XMLRPC Disable Service END\n?', '\n', t, flags=re.S)
    t = re.sub(r'\n?# SGO Unset Vary.*?# SGO Unset Vary END\n?', '\n', t, flags=re.S)
    if os.path.exists(pag404):
        if h != 'aurzane.com': shutil.copy2(pag404, raiz + '/404.html')
        if 'ErrorDocument 404' not in t: t = 'ErrorDocument 404 /404.html\n' + t
    t = re.sub(r'\n{3,}', '\n\n', t)
    if t != a:
        open(ht, 'w', encoding='utf-8').write(t); print('htaccess actualizado', h)
