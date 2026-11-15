"""Índice del buscador común (Ctrl+K) siempre al día.
Parte del índice curado que lleva aurzane-ds.js y le añade solo cada test, calculadora, ejercicio y curso nuevo que
aparezca en el servidor; quita lo que ya no existe. Escribe aurzane.com/aurzane-indice.js, que aurzane-ds.js carga.
Corre en cursos-cifras.yml (cada día y tras cada despliegue). Entradas: SSH, SG_DEST."""
import os, subprocess, sys
SSH, DEST = os.environ.get('SSH', ''), os.environ.get('SG_DEST', '')
REMOTO = r'''
import os, re, json, glob, html, datetime
W = os.path.expanduser('~/www')
ds = open(W + '/aurzane.com/public_html/aurzane-ds.js', encoding='utf-8').read()
m = re.search(r'var INDICE = (\[.*?\]);\n', ds, re.S)
base = json.loads(m.group(1)) if m else []
def archivo(u):
    host, _, ruta = u.partition('/')
    f = os.path.join(W, host, 'public_html', ruta)
    return f + 'index.html' if f.endswith('/') else f
def meta(f):
    try: s = open(f, encoding='utf-8', errors='ignore').read(60000)
    except Exception: return None
    if re.search(r'<meta name="robots" content="[^"]*noindex', s): return None
    t = re.search(r'<title>(.*?)</title>', s, re.S); d = re.search(r'<meta name="description" content="([^"]*)"', s)
    t = html.unescape(re.sub(r'\s+', ' ', t.group(1))).strip() if t else ''
    t = re.split(r'\s+[|·—–-]\s+(?:AURZANE|Gratis|gratis)', t)[0].strip()
    d = html.unescape(d.group(1)).strip() if d else ''
    return t, (d[:117] + '…') if len(d) > 118 else d
out = [x for x in base if os.path.exists(archivo(x[1]))]
quitadas = len(base) - len(out)
ya = {x[1] for x in out}
REGLAS = [('mind', 'test-de-*/', 'Test', 'es'), ('live', 'test-de-*/', 'Test', 'es'), ('mind', 'en/*/', 'Test', 'en'), ('mind', 'pt/*/', 'Test', 'pt'),
          ('live', 'calculadora-*/', 'Calculadora', 'es'), ('build', 'calculadora-*/', 'Calculadora', 'es'), ('nexus', 'calculadora-*/', 'Calculadora', 'es'),
          ('mind', 'ejercicios/*/', 'Ejercicio', 'es'), ('learn', 'curso/*/', 'Curso', 'es')]
nuevas = 0
for mundo, patron, tipo, lang in REGLAS:
    raiz = os.path.join(W, mundo + '.aurzane.com', 'public_html')
    for d in sorted(glob.glob(os.path.join(raiz, patron))):
        if not os.path.exists(os.path.join(d, 'index.html')): continue
        u = mundo + '.aurzane.com/' + os.path.relpath(d, raiz).replace(os.sep, '/') + '/'
        if u in ya: continue
        mt = meta(os.path.join(d, 'index.html'))
        if not mt or not mt[0]: continue
        out.append([mt[0], u, mundo, tipo, mt[1], lang]); ya.add(u); nuevas += 1
js = '/* Índice del buscador común, generado por herramientas/indice.py el ' + datetime.date.today().isoformat() + '. No editar a mano. */\nwindow.AurzaneIndiceGen = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
f = W + '/aurzane.com/public_html/aurzane-indice.js'
viejo = open(f, encoding='utf-8').read() if os.path.exists(f) else ''
if re.sub(r'el \d{4}-\d\d-\d\d', '', viejo) != re.sub(r'el \d{4}-\d\d-\d\d', '', js): open(f, 'w', encoding='utf-8').write(js); print('índice escrito')
print(f'índice: {len(out)} páginas ({nuevas} nuevas, {quitadas} que ya no existen)')
'''
r = subprocess.run(SSH.split() + [DEST, 'python3 -'], input=REMOTO, capture_output=True, text=True, timeout=180)
print(r.stdout.strip(), r.stderr.strip()[-400:])
print('::notice title=Buscador::' + (r.stdout.strip().splitlines() or ['sin respuesta'])[-1])
