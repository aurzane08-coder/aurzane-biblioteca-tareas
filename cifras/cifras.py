"""Cifras reales en toda la web, actualizadas solas.

Cuenta lo que de verdad hay (artículos de cada biblioteca, libros, universidades y países, temas, lecciones y preguntas
de cada curso) y corrige esas cifras en las páginas del servidor. Así nunca se publica una cifra inflada ni desfasada.
Se ejecuta cada día, después de cada despliegue y a mano. Guarda las cifras en cifras/cifras.json (el panel las muestra).
Antes de cambiar una página guarda una copia en www/<sitio>/eliminar/cifras-FECHA/.
Entradas: SUPABASE_SERVICE_KEY, SSH, SG_DEST.
"""
import json, os, re, subprocess, datetime, urllib.request

R = os.path.dirname(os.path.abspath(__file__))
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
KEY = os.environ.get('SUPABASE_SERVICE_KEY', '').strip() or 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
HOY = datetime.date.today().isoformat()
MUNDOS = ['mind', 'nexus', 'live', 'learn', 'build']


def remoto(orden, entrada=None):
    r = subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=120, input=entrada)
    return r.stdout


def cuenta(tabla, filtro=''):
    rq = urllib.request.Request(f'{SB}{tabla}?select=id{filtro}', method='HEAD',
                                headers={'apikey': KEY, 'Prefer': 'count=exact', 'Range': '0-0'})
    with urllib.request.urlopen(rq, timeout=60) as r: return int(r.headers.get('Content-Range', '*/0').split('/')[-1])


def todos(tabla, campos, filtro=''):
    out, i = [], 0
    while True:
        rq = urllib.request.Request(f'{SB}{tabla}?select={campos}{filtro}', headers={'apikey': KEY, 'Range': f'{i}-{i + 999}'})
        with urllib.request.urlopen(rq, timeout=60) as r: lote = json.load(r)
        out += lote
        if len(lote) < 1000: return out
        i += 1000


mil = lambda n: f'{n:,}'.replace(',', '.')
redondo = lambda n: mil(n // 100 * 100 if n >= 1000 else n // 10 * 10)  # para «más de N»

# ---------- 1. contar ----------
c = {'fecha': HOY, 'articulos': {}}
for m in MUNDOS:
    try: c['articulos'][m] = cuenta(f'{m}_biblioteca')
    except Exception as e: print('sin tabla', m, e)
c['articulos_total'] = sum(c['articulos'].values())
u = todos('universidades', 'pais')
c['universidades'], c['paises'] = len(u), len({x['pais'] for x in u if x.get('pais')})
cat = remoto('cat ~/www/aurzane.com/public_html/biblioteca/catalogo.js')
try: c['libros'] = len(json.loads(cat[cat.index('{'):cat.rindex('}') + 1])['libros'])
except Exception as e: print('libros', e)
rq = urllib.request.Request(SB + 'rpc/course_catalog_public', data=b'{}', headers={'apikey': KEY, 'Content-Type': 'application/json'})
with urllib.request.urlopen(rq, timeout=60) as r: cursos = json.load(r)
c['cursos'] = {k['slug']: {'temas': len(k['modulos']), 'lecciones': sum(len(m['lecciones']) for m in k['modulos']), 'preguntas': k['preguntas'], 'tipos': k['tipos']} for k in cursos}
json.dump(c, open(os.path.join(R, 'cifras.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in c.items() if k != 'cursos'}, ensure_ascii=False))

# ---------- 2. reglas: (patrón, función que da el texto nuevo) ----------
A, NUM = c['articulos'], r'(\d{1,3}(?:\.\d{3})+|\d+)'
def reglas(sitio):
    rr = []
    for m in MUNDOS:
        if m not in A: continue
        M = m.upper()
        # tarjetas «Biblioteca MIND … 5.000 artículos» en la portada y descripciones de cada biblioteca
        rr.append((r'(Biblioteca ' + M + r'(?:(?!Biblioteca )[\s\S]){0,240}?)' + NUM + r'( artículos)', lambda x, n=A[m]: x.group(1) + mil(n) + x.group(3)))
        if sitio == f'{m}.aurzane.com':
            rr.append((NUM + r'( artículos científicos)', lambda x, n=A[m]: mil(n) + x.group(2)))
    if c['articulos_total']:
        rr.append((r'(bibliotecas del ecosistema a la vez: )' + NUM + r'( artículos)', lambda x: x.group(1) + mil(c['articulos_total']) + x.group(3)))
        rr.append((r'(")' + NUM + r'( artículos científicos en un solo buscador)', lambda x: x.group(1) + mil(c['articulos_total']) + x.group(3)))
    if c.get('libros'):
        rr.append((r'(Más de |más de )' + NUM + r'( libros)', lambda x: x.group(1) + redondo(c['libros']) + x.group(3)))
        rr.append((NUM + r' libros de psicología para leer gratis', lambda x: mil(c['libros']) + ' libros para leer gratis'))
    if c['universidades']:
        rr.append((NUM + r'( (?:instituciones|universidades) en )' + NUM + r'( países)', lambda x: mil(c['universidades']) + x.group(2) + str(c['paises']) + x.group(4)))
        rr.append((r'(\d{1,3}\.\d{3})( universidades)', lambda x: mil(c['universidades']) + x.group(2)))  # solo cifras del catálogo (miles)
    return rr


def cursos_en(texto):
    """Cifras de cada tarjeta de curso: el bloque que enlaza al curso lleva sus temas, lecciones y preguntas."""
    for slug, d in c['cursos'].items():
        def arregla(bloque):
            for campo in ('temas', 'lecciones', 'preguntas'):
                bloque = re.sub(r'(<b>)\d+(</b>\s*' + campo + ')', lambda x: x.group(1) + str(d[campo]) + x.group(2), bloque)
            return re.sub(r'(preguntas de )\d+( tipos)', lambda x: x.group(1) + str(d['tipos']) + x.group(2), bloque)
        texto = re.sub(r'<article[^>]*>(?:(?!</article>)[\s\S])*?c=' + slug + r'["#](?:(?!</article>)[\s\S])*?</article>', lambda x: arregla(x.group(0)), texto)
    return texto


# ---------- 3. aplicar ----------
PAGINAS = ['aurzane.com/index.html', 'aurzane.com/research.html', 'aurzane.com/mi-aurzane.html'] + \
          [f'{m}.aurzane.com/index.html' for m in MUNDOS] + [f'{m}.aurzane.com/{m}-biblioteca.html' for m in MUNDOS]
cambios = []
for p in PAGINAS:
    sitio, ruta = p.split('/', 1)
    arch = f'www/{sitio}/public_html/{ruta}'
    t = remoto(f'cat {arch} 2>/dev/null')
    if not t: continue
    n = t
    for pat, f in reglas(sitio): n = re.sub(pat, f, n)
    n = cursos_en(n)
    if n != t:
        copia = f'www/{sitio}/eliminar/cifras-{HOY}/{ruta}'
        r = remoto(f'mkdir -p "$(dirname {copia})" && cp -p {arch} {copia} && cat > {arch}.cif && mv {arch}.cif {arch} && echo OK', n)
        if 'OK' in r: cambios.append(p); print('cifras corregidas en', p)
for s in {p.split('/')[0] for p in cambios}: remoto(f'site-tools-client domain-all update id={s} flush_cache=1 >/dev/null 2>&1; true')
print(f'::notice title=Cifras::{len(cambios)} páginas corregidas con datos reales')
