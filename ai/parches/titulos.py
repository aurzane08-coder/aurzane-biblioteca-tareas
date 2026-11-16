"""Títulos de 60 caracteres como máximo y sin repetir, cada día, en todas las páginas de los 7 dominios (16/11/2026).
Google corta los títulos largos (más de ~60 caracteres) y, si dos páginas tienen el mismo, suele mostrar solo una.
- Largo: se quitan primero los sufijos «| …», después añadidos poco útiles y, si aún sobra, se corta por palabra.
- Repetido dentro de un dominio: se añade el autor (libros) o el nombre de la carpeta, para que cada página sea única.
Solo cambia la etiqueta <title>; el resto de la página queda igual. NEXUS ya lo hace en su generador (univ/gen/gen.py)."""
import os, re, sys, html, json, collections

BASE = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
HOSTS = ['aurzane.com', 'mind.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com', 'nexus.aurzane.com']
FUERA = {'eliminar', 'node_modules', 'marketing', 'privado-ai', 'ai', 'panel', 'tiktok', 'youtube', 'ir', 'core', '.well-known'}
M = 60


def acortar(t, m=M):
    if len(t) <= m: return t
    partes = t.split(' | ')
    while len(partes) > 1 and len(' | '.join(partes)) > m: partes.pop()
    t = ' | '.join(partes)
    if len(t) > m: t = re.sub(r'\s*\((gratis|online|PDF|en PDF)\)', '', t)
    if len(t) > m: t = re.sub(r' y (sus )?[\d.]+ (carreras|grados)', '', t)
    for q in (' gratis y online', ' gratis', ' online questionnaire', ' free'):
        if len(t) > m and q in t: t = t.replace(q, '', 1)
    t = re.sub(r':\s*(free|gratis)$', '', t)
    if len(t) <= m: return t
    # se corta solo en una frontera natural (dos puntos o interrogación) que deje al menos 35 caracteres;
    # si no la hay, se deja como está (Google pondrá «…», mejor que una frase a medias)
    mejor = -1
    for mm in re.finditer(r'(\?|:)\s', t[:m + 1]):
        if mm.start() >= 35: mejor = mm.start() + (1 if mm.group(1) == '?' else 0)
    return t[:mejor].rstrip(' ,:;-') if mejor > 0 else t


def autor(t):
    for pat in (r'"author"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', r'"author"\s*:\s*\[\s*\{[^}]*"name"\s*:\s*"([^"]+)"', r'<meta name="author" content="([^"]+)"'):
        m = re.search(pat, t)
        if m: return html.unescape(m.group(1)).strip()
    return ''


cambios = 0
for h in HOSTS:
    raiz = BASE + '/' + h + '/public_html'
    if not os.path.isdir(raiz): continue
    pags = []
    for dp, dn, fn in os.walk(raiz):
        dn[:] = [d for d in dn if d not in FUERA and not d.startswith('carga-')]
        if h == 'nexus.aurzane.com' and os.path.relpath(dp, raiz).startswith('universidades'): continue   # su generador ya lo hace
        for f in fn:
            if f.endswith('.html'): pags.append(os.path.join(dp, f))
    datos = {}
    for p in pags:
        try: t = open(p, encoding='utf-8').read()
        except Exception: continue
        m = re.search(r'<title>(.*?)</title>', t, re.S | re.I)
        if not m: continue
        datos[p] = (t, m, re.sub(r'\s+', ' ', html.unescape(m.group(1))).strip())
    nuevos = {p: acortar(x[2]) for p, x in datos.items()}
    # repetidos: se diferencian con el autor o la carpeta
    rep = collections.defaultdict(list)
    for p, n in nuevos.items(): rep[n].append(p)
    for n, ps in rep.items():
        if len(ps) < 2: continue
        for p in ps:
            extra = autor(datos[p][0]) or os.path.basename(os.path.dirname(p)).replace('-', ' ')
            if not extra: continue
            base = acortar(n, M - len(extra) - 2) if len(n) + len(extra) + 2 > M else n
            nuevos[p] = f'{base}, {extra}' if len(base) + len(extra) + 2 <= M else acortar(f'{base}, {extra}')
    for p, n in nuevos.items():
        t, m, viejo = datos[p]
        if n == viejo or not n: continue
        t2 = t[:m.start()] + '<title>' + html.escape(n, quote=False) + '</title>' + t[m.end():]
        open(p, 'w', encoding='utf-8').write(t2); cambios += 1
    print(h, len(datos), 'páginas revisadas')
print('títulos cambiados:', cambios)
