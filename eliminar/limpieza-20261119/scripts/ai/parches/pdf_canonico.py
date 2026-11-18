# Search Console: «Duplicada: el usuario no ha indicado ninguna versión canónica» eran los PDF de la biblioteca.
# A un PDF no se le puede poner etiqueta canónica en el HTML, así que se manda por cabecera HTTP (Google la acepta):
#   /biblioteca/pdf/<id>.pdf           -> https://aurzane.com/biblioteca/libro/<id>.html
#   /biblioteca/recientes/pdf/<id>.pdf -> https://aurzane.com/biblioteca/recientes/<id>/
# Se añade al .htaccess de cada carpeta (copia del original en eliminar/). Uso: python3 pdf_canonico.py <carpeta_www>
import os, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
MARCA = '# AURZANE canonica PDF'
REGLAS = {
    'biblioteca/pdf': 'SetEnvIf Request_URI "^/biblioteca/pdf/([^/]+)\\.pdf$" AZPDF=$1\nHeader set Link "<https://aurzane.com/biblioteca/libro/%{AZPDF}e.html>; rel=\\"canonical\\"" env=AZPDF',
    'biblioteca/recientes/pdf': 'SetEnvIf Request_URI "^/biblioteca/recientes/pdf/([^/]+)\\.pdf$" AZPDFR=$1\nHeader set Link "<https://aurzane.com/biblioteca/recientes/%{AZPDFR}e/>; rel=\\"canonical\\"" env=AZPDFR',
}
for carpeta, regla in REGLAS.items():
    d = os.path.join(base, 'aurzane.com/public_html', carpeta)
    if not os.path.isdir(d): print('no existe', carpeta); continue
    f = os.path.join(d, '.htaccess')
    s = open(f, encoding='utf-8').read() if os.path.exists(f) else ''
    if MARCA in s: print('ya estaba', carpeta); continue
    if s:
        copia = os.path.join(base, 'aurzane.com', 'eliminar', f'pdf-canonico-{hoy}', carpeta.replace('/', '_') + '.htaccess')
        os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
    open(f, 'w', encoding='utf-8').write(s.rstrip() + ('\n\n' if s else '') + f'{MARCA}\n<IfModule mod_headers.c>\n{regla}\n</IfModule>\n')
    print('canónica añadida en', carpeta)
