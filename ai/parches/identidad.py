# Identidad de cada mundo, siempre igual en todo el ecosistema (fuente: mundos/identidad.json).
# Corre en el servidor cada día y cada vez que cambia identidad.json: pone título, descripción, encabezado y entrada
# de la portada de cada mundo, y cambia las etiquetas antiguas («NEXUS — Tecnología», «BUILD — Imperio físico»…)
# en los menús que aún quedan en las páginas. Copia previa en <web>/eliminar/identidad-FECHA/.
# Uso: python3 - www < identidad.py  (identidad.json se pasa en la variable de entorno AZ_IDENTIDAD)
import os, re, sys, json, shutil, datetime, html as H
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
ID = json.loads(os.environ['AZ_IDENTIDAD'])
cat = open(os.path.join(base, 'nexus.aurzane.com/public_html/universidades/index.html'), encoding='utf-8').read()
m = re.search(r'<li><b>([\d.]+)</b><span>instituciones', cat); N = m.group(1) if m else ''
P = (re.search(r'<li><b>(\d+)</b><span>pa[ií]ses', cat) or re.search(r'en (\d+) pa[ií]ses', cat))
P = P.group(1) if P else '55'
def rell(t): return t.replace('{N}', N).replace('{P}', P)
VIEJAS = {r'(?<=</span> )MIND — [^<]{3,40}(?=</a>)': 'MIND — ' + ID['mind']['corto'], r'NEXUS — Tecnolog[ií]a': 'NEXUS — ' + ID['nexus']['corto'],
          r'LIVE — Vida sin l[ií]mites': 'LIVE — ' + ID['live']['corto'], r'LEARN — Conocimiento': 'LEARN — ' + ID['learn']['corto'],
          r'BUILD — (?:Imperio f[ií]sico|Infraestructura)': 'BUILD — ' + ID['build']['corto'],
          r'Vida sin l[ií]mites: bienestar, propósito y hábitos': 'Bienestar, salud, hábitos y propósito', r'Vida sin l[ií]mites': ID['live']['corto'],
          r'Imperio f[ií]sico': ID['build']['corto'], r'(?<=NEXUS: )[Tt]ecnolog[ií]a, conocimiento y salud': ID['nexus']['corto'].lower()}
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']


def guardar(web, rel, s, t):
    if t == s: return 0
    c = os.path.join(base, web, 'eliminar', 'identidad-' + hoy, os.path.dirname(rel)); os.makedirs(c, exist_ok=True)
    shutil.copy2(os.path.join(base, web, 'public_html', rel), c)
    open(os.path.join(base, web, 'public_html', rel), 'w', encoding='utf-8').write(t); return 1


n = 0
for mundo, d in ID.items():
    if mundo.startswith('_'): continue
    web = mundo + '.aurzane.com'; f = os.path.join(base, web, 'public_html', 'index.html')
    if not N and '{N}' in d['entrada']: continue
    try: s = open(f, encoding='utf-8').read()
    except Exception: continue
    t, tit, des = s, H.escape(rell(d['titulo'])), H.escape(rell(d['descripcion']))
    t = re.sub(r'<title>[^<]*</title>', '<title>' + tit + '</title>', t, count=1)
    for a, v in (('name="description"', des), ('property="og:title"', tit), ('property="og:description"', des), ('name="twitter:title"', tit), ('name="twitter:description"', des)):
        t = re.sub(r'(<meta ' + a + r' content=")[^"]*(")', lambda x: x.group(1) + v + x.group(2), t, count=1)
    # encabezado de la portada del mundo: eyebrow + primer h1 estático + párrafo de entrada
    def hero(x):
        bloque = x.group(0)
        bloque = re.sub(r'(<span class="eyebrow">)[^<]*(</span>)', lambda y: y.group(1) + H.escape(d['eyebrow']) + y.group(2), bloque, count=1)
        bloque = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda y: y.group(1) + d['h1'] + y.group(2), bloque, count=1, flags=re.S)
        bloque = re.sub(r'(</h1>\s*<p[^>]*>).*?(</p>)', lambda y: y.group(1) + H.escape(rell(d['entrada'])) + y.group(2), bloque, count=1, flags=re.S)
        return bloque
    t = re.sub(r'(?:<span class="eyebrow">[^<]*</span>\s*)?<h1(?![^>]*\$\{)[^>]*>(?:(?!\$\{).)*?</h1>\s*<p[^>]*>.*?</p>', hero, t, count=1, flags=re.S)
    n += guardar(web, 'index.html', s, t)
# etiquetas antiguas de los menús en las páginas principales (hasta 2 niveles)
for web in WEBS:
    raiz = os.path.join(base, web, 'public_html')
    for dp, dn, fn in os.walk(raiz):
        rel_d = os.path.relpath(dp, raiz)
        if rel_d.count(os.sep) >= 2 or rel_d.split(os.sep)[0] in ('eliminar', 'wp-content', 'wp-includes', 'wp-admin', 'universidades', 'libros', 'biblioteca'):
            dn[:] = []; continue
        for x in fn:
            if not x.endswith('.html'): continue
            rel = os.path.normpath(os.path.join(rel_d, x)); p = os.path.join(raiz, rel)
            try: s = open(p, encoding='utf-8').read()
            except Exception: continue
            if ' — ' not in s and 'Vida sin l' not in s and 'Imperio f' not in s and 'NEXUS: ' not in s: continue
            t = s
            for a, b in VIEJAS.items(): t = re.sub(a, b, t)
            n += guardar(web, rel, s, t)
print('archivos con la identidad de los mundos al día:', n)
