"""Versiones automáticas de los archivos comunes (17/11/2026, plan de la auditoría final, punto 28).
aurzane-paleta.js carga en todas las páginas la hoja común y los scripts comunes con «?v=…», y el navegador los guarda
un año (ai/parches/cache.py). Antes el número se subía a mano y, si se olvidaba, la gente veía la versión vieja.
Ahora la versión es la huella (md5) del archivo tal como está en el servidor: cambia sola cuando cambia el archivo,
lo cambie un despliegue, un parche o la IA. Corre tras cada despliegue, tras las cifras y cada día.
Copia previa del cargador en aurzane.com/eliminar/versiones-FECHA/."""
import os, re, sys, hashlib, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
raiz = os.path.join(base, 'aurzane.com', 'public_html'); pal = os.path.join(raiz, 'aurzane-paleta.js')
s = open(pal, encoding='utf-8').read()


def huella(m):
    nombre = m.group(1); f = os.path.join(raiz, nombre)
    if not os.path.isfile(f): return m.group(0)
    return nombre + '?v=h' + hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]


t = re.sub(r'(aurzane-[a-z0-9-]+\.(?:js|css))\?v=[0-9A-Za-z._-]+', huella, s)
if t != s:
    c = os.path.join(base, 'aurzane.com', 'eliminar', 'versiones-' + hoy); os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, 'aurzane-paleta.js')): shutil.copy2(pal, c)
    open(pal + '.tmp', 'w', encoding='utf-8').write(t); os.replace(pal + '.tmp', pal)
    print('::notice::Versiones al día:', ', '.join(sorted(set(re.findall(r'aurzane-[a-z0-9-]+\.(?:js|css)\?v=h[0-9a-f]{8}', t)) - set(re.findall(r'aurzane-[a-z0-9-]+\.(?:js|css)\?v=h[0-9a-f]{8}', s)))))
else:
    print('versiones sin cambios')
