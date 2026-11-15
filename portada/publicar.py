"""Regenera la portada de aurzane.com con los datos del día y la sube si cambió.
Corre dentro de cursos-cifras.yml (cada día y después de cada despliegue), antes de corregir cifras,
así un curso nuevo, una cifra nueva o un cambio en portada/ aparecen solos.
Entradas: SSH, SG_DEST. Guarda la versión anterior en www/aurzane.com/eliminar/portada-FECHA/."""
import os, subprocess, sys, tempfile, datetime
R = os.path.dirname(os.path.abspath(__file__))
SSH, DEST = os.environ.get('SSH', ''), os.environ.get('SG_DEST', '')
HOY = datetime.datetime.now().strftime('%Y%m%d-%H%M')
ARCH = 'www/aurzane.com/public_html/index.html'


def remoto(orden, entrada=None):
    return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=120, input=entrada).stdout


actual = remoto(f'cat {ARCH}')
if '<head>' not in actual or 'class="portada"' not in actual: sys.exit('::warning title=Portada::no pude leer la portada actual; no toco nada')
d = tempfile.mkdtemp(); a, b = os.path.join(d, 'a.html'), os.path.join(d, 'b.html')
open(a, 'w', encoding='utf-8').write(actual)
subprocess.run([sys.executable, os.path.join(R, 'generar.py'), a, b], check=True)
nueva = open(b, encoding='utf-8').read()
if len(nueva) < len(actual) * 0.6: sys.exit('::warning title=Portada::la nueva portada es demasiado corta; no la subo')
# las cifras del día las pone después cifras.py; aquí solo se compara la estructura
if nueva == actual: print('portada sin cambios'); sys.exit(0)
r = remoto(f'mkdir -p www/aurzane.com/eliminar/portada-{HOY} && cp -p {ARCH} www/aurzane.com/eliminar/portada-{HOY}/ && cat > {ARCH}.nuevo && mv {ARCH}.nuevo {ARCH} && echo OK', nueva)
print('::notice title=Portada::' + ('portada regenerada con los datos del día' if 'OK' in r else 'no se pudo subir'))
