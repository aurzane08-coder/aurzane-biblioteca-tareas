# Cifras reales y al día: toma el número de universidades del catálogo publicado en NEXUS
# (lo genera univ-publicar a partir de la base de datos) y lo copia donde aparece en otras páginas.
# Antes de tocar un archivo guarda una copia en <web>/eliminar/cifras-FECHA/. Uso: python3 cifras.py <carpeta_www>
import re, os, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
cat = open(os.path.join(base, 'nexus.aurzane.com/public_html/universidades/index.html'), encoding='utf-8').read()
m = re.search(r'<li><b>([\d.]+)</b><span>instituciones', cat)
if not m: sys.exit('no encuentro la cifra del catálogo')
N = m.group(1); print('universidades en el catálogo:', N)
R = [(r'(<span class="hv-k">Universidades</span><span class="hv-num">)[\d.]+(</span>)', r'\g<1>' + N + r'\2'),
     (r'Universidades \([\d.]+\)', 'Universidades (' + N + ')'),
     (r'Universidades: [\d.]+ instituciones', 'Universidades: ' + N + ' instituciones'),
     (r'<b>[\d.]+</b> universidades e institutos', '<b>' + N + '</b> universidades e institutos'),
     (r'[\d.]{5} instituciones de 55 países', N + ' instituciones de 55 países'),
     (r'[\d.]{5} instituciones en 55 países', N + ' instituciones en 55 países'),
     (r'[\d.]{5} instituciones · 55 países', N + ' instituciones · 55 países'),
     (r'[\d.]{5} universidades (de|e institutos)', N + r' universidades \1')]
n = 0
for web, rel in [('aurzane.com', 'index.html'), ('aurzane.com', 'aurzane-estilo.js'), ('nexus.aurzane.com', 'index.html'), ('nexus.aurzane.com', 'nexus-biblioteca.html'), ('build.aurzane.com', 'index.html')]:
    f = os.path.join(base, web, 'public_html', rel)
    try: s = open(f, encoding='utf-8').read()
    except Exception: continue
    t = s
    for a, b in R: t = re.sub(a, b, t)
    if t != s:
        copia = os.path.join(base, web, 'eliminar', 'cifras-' + hoy, rel); os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
        open(f, 'w', encoding='utf-8').write(t); n += 1; print('actualizado', web, rel)
print('archivos actualizados:', n)
