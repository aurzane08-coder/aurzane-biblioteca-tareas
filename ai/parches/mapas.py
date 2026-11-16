"""Sitemaps y robots.txt de los 7 dominios, cada día (16/11/2026).
- sitemap-paginas.xml en cada dominio: todas sus páginas indexables (sin noindex, sin zonas privadas), con la URL canónica
  que declara la propia página y la fecha real de modificación del archivo.
- robots.txt: quita líneas Sitemap que no apuntan a un .xml y declara todos los sitemaps que existen en ese dominio.
No toca el resto de líneas del robots ni los sitemaps que escriben otros generadores."""
import os, re, sys, datetime, html

BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
HOSTS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
FUERA_DIR = {'eliminar', 'wp-admin', 'wp-content', 'wp-includes', 'node_modules', '.well-known', 'marketing', 'privado-ai', 'ai', 'panel',
             'tiktok', 'youtube', 'ir', 'core', 'mi', 'img', 'boletin'}
FUERA_ARCH = re.compile(r'^(404|admin.*|google[0-9a-f]+|guardados-almacen|mi-aurzane|portal|generar-informe|colegio|.*-cliente|informe-ejemplo|leer|articulo)\.html$')
OTROS = {'aurzane.com': ['biblioteca/recientes/sitemap.xml']}

for h in HOSTS:
    raiz = BASE + '/' + h + '/public_html'
    if not os.path.isdir(raiz): continue
    urls = {}
    for dp, dn, fn in os.walk(raiz):
        rel = os.path.relpath(dp, raiz)
        dn[:] = sorted(d for d in dn if d not in FUERA_DIR and not d.startswith('carga-') and not d.startswith('.')
                       and not (h == 'nexus.aurzane.com' and rel == '.' and d == 'universidades'))   # ya van en sitemap-universidades.xml
        for f in fn:
            if not f.endswith('.html') or FUERA_ARCH.match(f): continue
            p = os.path.join(dp, f)
            try: t = open(p, encoding='utf-8', errors='ignore').read(12000)
            except Exception: continue
            if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', t, re.I) or '<title' not in t.lower(): continue
            ruta = ('' if rel == '.' else rel + '/') + ('' if f == 'index.html' else f)
            u = 'https://' + h + '/' + ruta
            c = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', t, re.I) or re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical', t, re.I)
            if c:
                cu = html.unescape(c.group(1).strip())
                if not cu.startswith('https://' + h + '/'): continue   # duplicada de otra: no va al sitemap
                u = cu
            urls[u] = max(urls.get(u, ''), datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat())
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'<url><loc>{html.escape(u)}</loc><lastmod>{d}</lastmod></url>\n' for u, d in sorted(urls.items())) + '</urlset>\n'
    dest = raiz + '/sitemap-paginas.xml'
    if not os.path.exists(dest) or open(dest, encoding='utf-8').read() != x:
        open(dest, 'w', encoding='utf-8').write(x)
    # robots.txt
    rb = raiz + '/robots.txt'
    t = open(rb, encoding='utf-8').read() if os.path.exists(rb) else 'User-agent: *\nAllow: /\n'
    lineas = [l for l in t.splitlines() if not (l.lower().startswith('sitemap:') and not l.strip().lower().endswith('.xml'))]
    mapas = sorted(f for f in os.listdir(raiz) if re.match(r'sitemap.*\.xml$', f)) + [m for m in OTROS.get(h, []) if os.path.exists(raiz + '/' + m)]
    tiene = {l.split(':', 1)[1].strip() for l in lineas if l.lower().startswith('sitemap:')}
    for m in mapas:
        u = f'https://{h}/{m}'
        if u not in tiene: lineas.append('Sitemap: ' + u)
    nuevo = '\n'.join(l for l in lineas).strip() + '\n'
    if nuevo != t:
        open(rb, 'w', encoding='utf-8').write(nuevo); print('robots actualizado', h)
    print(h, len(urls), 'páginas en sitemap-paginas.xml')
