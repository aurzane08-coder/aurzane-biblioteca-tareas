"""Anuncios con criterio (17/11/2026; cambiado el mismo día por decisión de Adrian).
- OVP (ovp.aurzane.com) va SIN anuncios en todas sus páginas: ahí se tratan datos sensibles (evaluaciones psicológicas,
  informe, portal). Se quita el script de AdSense y los bloques <ins>; se deja la verificación de la cuenta.
- Los tests de salud de MIND SÍ llevan anuncios y socios (público general), con buena experiencia: la mañana del 17/11
  se les quitaron y aquí se les devuelven desde la copia que se guardó en eliminar/sin-anuncios-*.
Corre cada día y tras cada despliegue. Copia previa de cada página cambiada en <web>/eliminar/."""
import os, re, sys, glob, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
ADS = re.compile(r'<script[^>]*src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^"]*"[^>]*></script>\s*', re.I)
INS = re.compile(r'<ins class="adsbygoogle".*?</ins>\s*(<script>\s*\(adsbygoogle[^<]*</script>)?\s*', re.I | re.S)
MARCA = '<meta name="az-sin-anuncios" content="datos sensibles">\n'
FUERA = {'eliminar', 'node_modules', '.well-known'}


def guardar(web, raiz, p, t):
    c = os.path.join(base, web, 'eliminar', 'sin-anuncios-' + hoy, os.path.relpath(p, raiz))
    os.makedirs(os.path.dirname(c), exist_ok=True)
    if not os.path.exists(c): shutil.copy2(p, c)
    open(p + '.tmp', 'w', encoding='utf-8').write(t); os.replace(p + '.tmp', p)


# 1) OVP sin anuncios
n = 0; raiz = os.path.join(base, 'ovp.aurzane.com', 'public_html')
for d, sub, fs in os.walk(raiz):
    sub[:] = [s for s in sub if s not in FUERA and not s.startswith('.')]
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.join(d, f)
        try: t = open(p, encoding='utf-8').read()
        except Exception: continue
        nuevo = INS.sub('', ADS.sub('', t))
        if 'name="az-sin-anuncios"' not in nuevo and '</head>' in nuevo: nuevo = nuevo.replace('</head>', MARCA + '</head>', 1)
        if nuevo != t: guardar('ovp.aurzane.com', raiz, p, nuevo); n += 1
# 2) tests de MIND: devolver los anuncios quitados por la versión anterior de este parche
dev = 0; raiz_m = os.path.join(base, 'mind.aurzane.com', 'public_html')
for p in glob.glob(os.path.join(raiz_m, '**', 'index.html'), recursive=True):
    if '/eliminar/' in p: continue
    t = open(p, encoding='utf-8').read()
    if 'name="az-sin-anuncios" content="salud mental"' not in t: continue
    rel = os.path.relpath(p, raiz_m)
    copias = sorted(glob.glob(os.path.join(base, 'mind.aurzane.com', 'eliminar', 'sin-anuncios-*', rel)))
    if not copias: continue
    nuevo = open(copias[-1], encoding='utf-8').read()   # la página tal como estaba antes de quitarle los anuncios
    if not ADS.search(nuevo) or 'az-sin-anuncios' in nuevo: continue
    guardar('mind.aurzane.com', raiz_m, p, nuevo); dev += 1
print(f'::notice::OVP sin anuncios: {n} páginas cambiadas. Tests de MIND con anuncios de nuevo: {dev}')
