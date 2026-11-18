# Mueve a eliminar/ los restos de instalación del hosting que no forman parte de AURZANE
# (página «Under construction», archivos de WordPress sin WordPress). Nunca borra: solo mueve.
import os, sys, shutil, datetime
base = sys.argv[1] if len(sys.argv) > 1 else 'www'
hoy = datetime.date.today().isoformat()
RESTOS = ['Default.html', 'default.html', 'wp-config-sample.php', 'readme.html', 'license.txt', 'wp-login.php']
for dom in sorted(os.listdir(base)):
    pub = os.path.join(base, dom, 'public_html')
    if not os.path.isdir(pub): continue
    mover = [f for f in RESTOS if os.path.isfile(os.path.join(pub, f))]
    ip = os.path.join(pub, 'index.php')
    if os.path.isfile(ip) and 'wp-blog-header.php' in open(ip, errors='ignore').read() and not os.path.exists(os.path.join(pub, 'wp-blog-header.php')):
        mover.append('index.php')
    for f in mover:
        dst = os.path.join(base, dom, 'eliminar', 'limpieza-' + hoy); os.makedirs(dst, exist_ok=True)
        shutil.move(os.path.join(pub, f), os.path.join(dst, f)); print('movido', dom, f)
print('limpieza terminada')
