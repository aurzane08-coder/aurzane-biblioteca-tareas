"""Sin anuncios en los tests de salud mental (17/11/2026, etapa 4 de la auditoría, tarea 46: anuncios con criterio).
Quien hace un test de ansiedad, depresión, estrés, burnout, TDAH o soledad está mirando algo delicado de su salud:
ahí no se muestran anuncios. Se quita el script de AdSense (anuncios automáticos) solo en esas páginas y se deja la
etiqueta de verificación de la cuenta. El resto de páginas públicas mantiene sus anuncios.
Corre cada día y tras cada despliegue, así ninguna regeneración vuelve a ponerlos. Copia previa en eliminar/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
WEB = 'mind.aurzane.com'
RUTAS = ['test-de-ansiedad', 'test-de-depresion', 'test-de-estres', 'test-de-burnout', 'test-de-tdah', 'test-de-soledad',
         'en/anxiety-test-gad-7', 'en/depression-test-phq-9', 'en/stress-test-dass-21', 'en/burnout-test-cbi',
         'pt/teste-de-ansiedade-gad-7', 'pt/teste-de-depressao-phq-9']
ADS = re.compile(r'<script[^>]*src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^"]*"[^>]*></script>\s*', re.I)
INS = re.compile(r'<ins class="adsbygoogle".*?</ins>\s*(<script>\s*\(adsbygoogle[^<]*</script>)?\s*', re.I | re.S)
n = 0
for r in RUTAS:
    p = os.path.join(base, WEB, 'public_html', r, 'index.html')
    if not os.path.exists(p): continue
    t = open(p, encoding='utf-8').read()
    nuevo = INS.sub('', ADS.sub('', t))
    if 'name="az-sin-anuncios"' not in nuevo:   # marca para estilo.js y para cualquier script que añada anuncios después
        nuevo = nuevo.replace('</head>', '<meta name="az-sin-anuncios" content="salud mental">\n</head>', 1)
    if nuevo != t:
        c = os.path.join(base, WEB, 'eliminar', 'sin-anuncios-' + hoy, r); os.makedirs(c, exist_ok=True); shutil.copy2(p, os.path.join(c, 'index.html'))
        open(p + '.tmp', 'w', encoding='utf-8').write(nuevo); os.replace(p + '.tmp', p); n += 1
print(f'::notice::Sin anuncios en tests de salud mental: {n} páginas cambiadas de {len(RUTAS)}')
