"""Enlaces de idioma entre las versiones de cada página (23/11/2026).
Recorre las páginas en inglés y portugués (www/<dominio>/public_html/en/... y /pt/...). Cada una declara su versión en español
con <link rel="alternate" hreflang="es">; si la página española no enlaza todavía a esa traducción, se le añade el enlace
(y el suyo propio y el x-default, si faltan). Así Google muestra a cada visitante la versión de su idioma y el selector de idioma
lleva a la página traducida de verdad. Antes de cambiar una página se guarda una copia en www/eliminar/hreflang-FECHA/.
Uso en el servidor: python3 - www < hreflang.py"""
import os, re, sys, glob, shutil, datetime

BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
HOY = datetime.date.today().strftime('%Y%m%d')
LANG = {'en': 'en', 'pt': 'pt-BR'}
cambios = 0


def local(url):
    m = re.match(r'https://([^/]+)/(.*)$', url)
    if not m: return ''
    f = os.path.join(BASE, m.group(1), 'public_html', m.group(2))
    if f.endswith('/'): f += 'index.html'
    return f if os.path.isfile(f) else ''


for dom in ['mind.aurzane.com']:   # NEXUS enlaza sus idiomas desde univ/gen (gen.py y en.py)
    for idioma, codigo in LANG.items():
        for f in glob.glob(os.path.join(BASE, dom, 'public_html', idioma, '**', 'index.html'), recursive=True):
            try: t = open(f, encoding='utf-8', errors='ignore').read()
            except Exception: continue
            es = re.search(r'<link[^>]+hreflang="es"[^>]+href="([^"]+)"', t)
            yo = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', t)
            if not es or not yo: continue
            f_es = local(es.group(1))
            if not f_es: continue
            h = open(f_es, encoding='utf-8').read()
            if yo.group(1) in h: continue   # ya enlaza a esta traducción
            nuevo = f'<link rel="alternate" hreflang="{codigo}" href="{yo.group(1)}">'
            if 'hreflang="es"' not in h: nuevo = f'<link rel="alternate" hreflang="es" href="{es.group(1)}">' + nuevo
            if 'hreflang="x-default"' not in h: nuevo += f'<link rel="alternate" hreflang="x-default" href="{es.group(1)}">'
            m = re.search(r'<link[^>]+rel="canonical"[^>]*>', h)
            if not m: continue
            copia = os.path.join(BASE, 'eliminar', 'hreflang-' + HOY, os.path.relpath(f_es, BASE))
            os.makedirs(os.path.dirname(copia), exist_ok=True)
            if not os.path.exists(copia): shutil.copy2(f_es, copia)
            open(f_es, 'w', encoding='utf-8').write(h[:m.end()] + '\n' + nuevo + h[m.end():])
            cambios += 1
            print('  ', os.path.relpath(f_es, BASE), '→', yo.group(1))
print('Páginas en español enlazadas con su traducción:', cambios)
