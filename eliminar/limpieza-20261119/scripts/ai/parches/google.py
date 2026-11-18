# Lo que muestra Google: las barras de navegación no salen como descripción («AURZANEMINDOVP…») y los paneles privados no se indexan.
# Antes de tocar archivos guarda los originales en <web>/eliminar/google-FECHA.tar.gz. Uso: python3 google.py <carpeta_www>
import os, sys, re, tarfile, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M'); total = 0
CAMBIOS = [('<div class="utility">', '<div class="utility" data-nosnippet>'), ('<header class="topbar">', '<header class="topbar" data-nosnippet>'), ('<div class="topbar">', '<div class="topbar" data-nosnippet>')]
PRIVADAS = {'aurzane.com': ['admin.html', 'mi-aurzane.html'], 'learn.aurzane.com': ['admin-cursos.html'], 'ovp.aurzane.com': ['restablecer-contrasena.html']}
for web in ['aurzane.com', 'mind.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'nexus.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']:
    pub = os.path.join(base, web, 'public_html')
    if not os.path.isdir(pub): continue
    tocados = {}
    for raiz, dirs, archivos in os.walk(pub):
        dirs[:] = [x for x in dirs if x not in ('eliminar', 'wp-admin', 'wp-includes', 'wp-content')]
        for a in archivos:
            if not a.endswith('.html'): continue
            f = os.path.join(raiz, a)
            try: s = open(f, encoding='utf-8').read()
            except Exception: continue
            t = s
            for x, y in CAMBIOS: t = t.replace(x, y)
            rel = os.path.relpath(f, pub)
            if rel in PRIVADAS.get(web, []) and 'name="robots"' not in t:
                t = re.sub(r'(<head[^>]*>)', r'\1\n<meta name="robots" content="noindex,nofollow">', t, count=1)
            if t != s: tocados[f] = (s, t)
    if not tocados: continue
    os.makedirs(os.path.join(base, web, 'eliminar'), exist_ok=True)
    with tarfile.open(os.path.join(base, web, 'eliminar', f'google-{hoy}.tar.gz'), 'w:gz') as tar:
        for f in tocados: tar.add(f, arcname=os.path.relpath(f, pub))
    for f, (s, t) in tocados.items(): open(f, 'w', encoding='utf-8').write(t)
    print(web, 'archivos corregidos:', len(tocados)); total += len(tocados)
print('total', total)
