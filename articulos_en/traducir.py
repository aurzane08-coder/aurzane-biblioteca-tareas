"""Artículos de AURZANE en inglés (23/11/2026), punto 4 del plan de inglés (diseno/PLAN-INGLES.md).

No se traduce todo: solo la selección de articulos_en/lista.txt (temas con lectores en inglés). Para cada artículo:
  1. Lee la página española del servidor (aurzane.com/articulos/<slug>/).
  2. La IA de AURZANE (Gemini; si no hay cupo, los modelos gratuitos de GitHub) la traduce y adapta al lector anglosajón,
     sin cambiar datos ni fuentes y sin rayas largas. Se comprueba que el HTML queda igual (mismas etiquetas y enlaces).
  3. Una segunda pasada puntúa la traducción frente al original; solo se publica con 8/10 o más.
  4. Publica aurzane.com/en/articles/<slug>/ con enlaces de idioma (hreflang) en las dos versiones.
     Los enlaces a tests o páginas que ya tienen versión inglesa apuntan a esa versión.
  5. Rehace la portada aurzane.com/en/articles/.
Si la página española cambia, su versión inglesa se vuelve a generar sola (se guarda una huella en estado.json).
Nunca borra nada: antes de cambiar un archivo del servidor guarda una copia en www/aurzane.com/eliminar/articulos-en-FECHA/.
Entradas: SSH, SG_DEST, GEMINI_API_KEY, GITHUB_TOKEN. MAX = artículos nuevos por ejecución (6 por defecto)."""
import os, re, json, html, hashlib, subprocess, time, datetime, urllib.request, urllib.error

R = os.path.dirname(os.path.abspath(__file__))
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
MAX = int(os.environ.get('MAX') or 6)
HOY = datetime.date.today().isoformat()
WEB = 'www/aurzane.com/public_html'
EST_F = os.path.join(R, 'estado.json')
EST = json.load(open(EST_F, encoding='utf-8')) if os.path.exists(EST_F) else {}
LISTA = [l.split('#')[0].strip() for l in open(os.path.join(R, 'lista.txt'), encoding='utf-8') if l.split('#')[0].strip()]
url_es = lambda s: f'https://aurzane.com/articulos/{s}/'
url_en = lambda s: f'https://aurzane.com/en/articles/{s}/'


def remoto(orden, entrada=None, t=120):
    return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=t, input=entrada).stdout


def escribir(ruta, contenido):
    """Escribe un archivo del servidor guardando antes la versión anterior (si la había) en eliminar/."""
    copia = f'www/aurzane.com/eliminar/articulos-en-{HOY}/' + ruta.replace(WEB + '/', '')
    orden = (f'if [ -f {ruta} ] && [ ! -f {copia} ]; then mkdir -p "$(dirname {copia})" && cp -p {ruta} {copia}; fi; '
             f'mkdir -p "$(dirname {ruta})" && cat > {ruta}.tmp && mv {ruta}.tmp {ruta} && echo OK')
    return 'OK' in remoto(orden, contenido)


# ------------------------------------------------------------------ IA (igual que ai/manager.py)
def http(url, cab, datos, t=90):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=datos, headers=cab, method='POST' if datos else 'GET'), timeout=t) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
    except Exception as e: return 0, str(e).encode()


MODELOS = []
FALLOS = {'n': 0}


def ia(prompt, maxt=6000, temp=0.2):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if k and FALLOS['n'] < 8:
        cab = {'Content-Type': 'application/json', 'x-goog-api-key': k}
        if not MODELOS:
            st, b = http('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200', cab, None, 40)
            try:
                ns = [m['name'].split('/')[-1] for m in json.loads(b).get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                vers = sorted([n for n in ns if re.match(r'^gemini-\d[\d.]*-flash(-lite)?$', n)], key=lambda n: ('lite' in n, [-int(x) for x in re.findall(r'\d+', n)]))
                MODELOS.extend([n for n in ('gemini-flash-latest',) if n in ns] + vers[:3])
            except Exception: pass
        cuerpo = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': temp, 'maxOutputTokens': maxt}}).encode()
        for m in MODELOS:
            st, b = http(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', cab, cuerpo, 120)
            if st == 200:
                try:
                    c = json.loads(b)['candidates'][0]
                    txt = ''.join(x.get('text', '') for x in c['content'].get('parts', []) if not x.get('thought')).strip()
                    if txt: return txt
                    print(f'  {m}: respuesta vacía ({c.get("finishReason")})')
                except Exception as e: print(f'  {m}: respuesta no legible', str(e)[:80])
            else: print(f'  {m}: error {st}', b[:160].decode('utf-8', 'ignore').replace(chr(10), ' '))
            FALLOS['n'] += 1
            if st in (429, 503): time.sleep(4)
    tk = os.environ.get('GITHUB_TOKEN', '').strip()
    for m in ('openai/gpt-4.1-mini', 'openai/gpt-4o-mini') if tk else ():
        st, b = http('https://models.github.ai/inference/chat/completions', {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tk},
                     json.dumps({'model': m, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': temp, 'max_tokens': min(maxt, 8000)}).encode(), 150)
        if st == 200:
            try: return json.loads(b)['choices'][0]['message']['content'].strip()
            except Exception: pass
        print(f'  {m}: error {st}', b[:160].decode('utf-8', 'ignore').replace(chr(10), ' '))
    return ''


def sin_valla(t):
    return re.sub(r'^```[a-z]*\s*|\s*```$', '', t.strip())


# ------------------------------------------------------------------ piezas de la página
FIJOS = [   # textos de la plantilla de artículo que no están dentro de <main>
    ('<a href="https://aurzane.com">Inicio</a>', '<a href="https://aurzane.com">Home</a>'),
    ('<a href="https://aurzane.com/#mundos">Mundos</a>', '<a href="https://aurzane.com/#mundos">Worlds</a>'),
    ('<a href="https://aurzane.com/research.html">Investigación</a>', '<a href="https://aurzane.com/en/research.html">Research</a>'),
    ('<a href="https://aurzane.com/articulos/">Artículos</a>', '<a href="https://aurzane.com/en/articles/">Articles</a>'),
    ('AURZANE resume investigación real en un lenguaje simple. Cada guía es una síntesis original, escrita a partir de estudios y metaanálisis verificables citados al final de cada artículo.',
     'AURZANE explains real research in plain language. Every guide is an original summary, written from verifiable studies and meta-analyses cited at the end of each article.'),
]
ETQ = re.compile(r'<(/?[a-zA-Z][a-zA-Z0-9]*)')
HREF = re.compile(r'href="([^"]+)"')


def huella(t): return hashlib.sha1(t.encode('utf-8')).hexdigest()[:16]


def partes(t):
    m = re.search(r'<main class="article wrap">([\s\S]*?)</main>', t)
    if not m: return None
    main = re.sub(r'\s*<div class="related">[\s\S]*?</div>\s*</div>\s*(?=\s*<a class="back-hub"|\s*$)', '\n', m.group(1))   # tarjetas de otros artículos (en español): se rehacen
    return m, main


def traducir_main(main):
    """Devuelve el <main> en inglés o '' si la IA no conserva la estructura."""
    pedir = ('You translate pages of AURZANE, a free science-communication website run by a clinical psychologist, from Spanish into natural, '
             'warm and precise English for readers in the US, UK, Canada and Australia. Translate ALL visible text in the HTML below '
             '(headings, paragraphs, lists, labels such as "min de lectura" or "Fuentes", the call-to-action boxes, the disclaimer). Adapt idioms and units so '
             'they read naturally, but never change facts, numbers, study details or names, and do not add or remove information. Keep the titles of the '
             'cited studies exactly as they are. Do not use em dashes or en dashes: use commas, colons or full stops. Spanish crisis phone numbers (such as 024) '
             'stay as they are, followed by "(Spain)" if it is not already said. Keep every HTML tag and attribute exactly as it is, in the same order; '
             'do not translate URLs or attribute values. Reply with the translated HTML only, no comments and no code fences.\n\n' + main)
    for _ in range(2):
        r = sin_valla(ia(pedir, 24000))
        if not r: return ''
        r = r.replace(' — ', ', ').replace('—', ', ').replace(' – ', ', ')
        if ETQ.findall(r) == ETQ.findall(main) and HREF.findall(r) == HREF.findall(main): return r
        a, b = ETQ.findall(main), ETQ.findall(r)
        print(f'  la traducción cambió la estructura del HTML ({len(a)} etiquetas en el original, {len(b)} en la traducción); reintento')
    return ''


def nota(es, en):
    r = ia('You review translations for AURZANE. Score from 1 to 10 this English version against the Spanish original: same facts, numbers and caveats, '
           'nothing added or missing, natural English for a general reader, no leftover Spanish (except names of Spanish places, institutions or phone numbers). '
           'Reply ONLY with JSON: {"score": <1-10>, "reason": "<one sentence>"}\n\nSPANISH:\n' + re.sub(r'<[^>]+>', ' ', es)[:9000] +
           '\n\nENGLISH:\n' + re.sub(r'<[^>]+>', ' ', en)[:9000], 4000, 0)
    m = re.search(r'\{[\s\S]*\}', r)
    try: j = json.loads(m.group(0)) if m else {}
    except Exception: j = {}
    return int(j.get('score') or 0), str(j.get('reason') or '')


def mapa_ingles(urls):
    """Para cada página de AURZANE enlazada, su versión inglesa si existe (la que declara con hreflang="en")."""
    urls = sorted({u for u in urls if re.match(r'^https://([a-z]+\.)?aurzane\.com/', u)})
    if not urls: return {}
    py = r'''import os,re,sys,json
out={}
for u in json.load(sys.stdin):
    m=re.match(r'https://([^/]+)/([^?#]*)',u)
    if not m: continue
    f=os.path.expanduser('~/www/'+m.group(1)+'/public_html/'+m.group(2))
    if f.endswith('/') or os.path.isdir(f): f=f.rstrip('/')+'/index.html'
    try: t=open(f,encoding='utf-8',errors='ignore').read(60000)
    except Exception: continue
    x=re.search(r'<link[^>]+hreflang="en"[^>]+href="([^"]+)"',t) or re.search(r'<link[^>]+href="([^"]+)"[^>]+hreflang="en"',t)
    if x and x.group(1)!=u: out[u]=x.group(1)
print(json.dumps(out))'''
    remoto('cat > /tmp/azmapa.py', py)
    try: return json.loads(remoto('python3 /tmp/azmapa.py; rm -f /tmp/azmapa.py', json.dumps(urls)) or '{}')
    except Exception: return {}


def relacionados(slug, hechos):
    otros = [s for s in LISTA if s != slug and s in hechos][:3]
    if not otros: return ''
    tarjetas = ''.join(f'<a class="related-card" href="{url_en(s)}">\n      <span class="cat">{html.escape(hechos[s]["categoria"])}</span>\n      <h5>{html.escape(hechos[s]["titulo"])}</h5>\n'
                       f'      <p>{html.escape(hechos[s]["resumen"][:110])}…</p>\n    </a>' for s in otros)
    return f'\n  <div class="related">\n    <h3>Keep reading</h3>\n    <div class="related-grid">{tarjetas}</div>\n  </div>'


def pagina_en(t_es, slug, main_en, hechos):
    t = t_es
    for es, en in FIJOS: t = t.replace(es, en)
    tit = html.unescape(re.sub(r'<[^>]+>', '', (re.search(r'<h1 class="art-title">([\s\S]*?)</h1>', main_en) or [None, ''])[1])).strip()
    res = html.unescape(re.sub(r'<[^>]+>', '', (re.search(r'<p class="art-resumen">([\s\S]*?)</p>', main_en) or [None, ''])[1])).strip()
    cat = html.unescape(re.sub(r'<[^>]+>', '', (re.search(r'<span class="badge">([\s\S]*?)</span>', main_en) or [None, ''])[1])).strip()
    rel = relacionados(slug, hechos)
    main_en = re.sub(r'(\n\s*<a class="back-hub")', lambda m: rel + m.group(1), main_en, count=1) if rel and 'class="back-hub"' in main_en else main_en + rel
    t = re.sub(r'(<main class="article wrap">)[\s\S]*?(</main>)', lambda m: m.group(1) + main_en + m.group(2), t, count=1)
    # migas: el título corto
    t = re.sub(r'(<span class="current">)[^<]*(</span>)', lambda m: m.group(1) + html.escape(tit[:60] + ('…' if len(tit) > 60 else '')) + m.group(2), t, count=1)
    # cabecera: idioma, título, descripción, redes, canónica, idiomas y datos estructurados
    marca = (re.search(r'<title>[^<|]*\|\s*([^<]+)</title>', t) or [None, 'AURZANE'])[1].strip()
    E = lambda s: html.escape(s, quote=True)
    t = re.sub(r'<html lang="[^"]*"', '<html lang="en"', t, count=1)
    t = re.sub(r'<title>[^<]*</title>', f'<title>{E(tit)} | {E(marca)}</title>', t, count=1)
    for patron, valor in ((r'(<meta name="description" content=")[^"]*', res), (r'(<meta property="og:title" content=")[^"]*', f'{tit} | {marca}'),
                          (r'(<meta property="og:description" content=")[^"]*', res), (r'(<meta name="twitter:title" content=")[^"]*', f'{tit} | {marca}'),
                          (r'(<meta name="twitter:description" content=")[^"]*', res), (r'(<meta property="og:url" content=")[^"]*', url_en(slug))):
        t = re.sub(patron, lambda m, v=valor: m.group(1) + E(v), t, count=1)
    t = re.sub(r'<link rel="(canonical|alternate)"[^>]*>\s*', '', t)
    t = re.sub(r'(</title>)', lambda m: m.group(1) + f'\n<link rel="canonical" href="{url_en(slug)}"><link rel="alternate" hreflang="es" href="{url_es(slug)}">'
               f'<link rel="alternate" hreflang="en" href="{url_en(slug)}"><link rel="alternate" hreflang="x-default" href="{url_es(slug)}">', t, count=1)
    def jl(m):
        try: d = json.loads(m.group(1))
        except Exception: return m.group(0)
        d.update(headline=tit, description=res, inLanguage='en', articleSection=cat or d.get('articleSection', ''))
        d['mainEntityOfPage'] = {'@type': 'WebPage', '@id': url_en(slug)}
        if isinstance(d.get('reviewedBy'), dict): d['reviewedBy']['jobTitle'] = 'Clinical psychologist'
        return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    t = re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', jl, t, count=1)
    return t, {'titulo': tit, 'resumen': res, 'categoria': cat}


def enlazar_es(t, slug):
    if f'href="{url_en(slug)}"' in t: return t
    links = f'<link rel="alternate" hreflang="es" href="{url_es(slug)}"><link rel="alternate" hreflang="en" href="{url_en(slug)}"><link rel="alternate" hreflang="x-default" href="{url_es(slug)}">'
    t = re.sub(r'<link rel="alternate" hreflang="[^"]*"[^>]*>', '', t)
    m = re.search(r'<link rel="canonical"[^>]*>', t)
    return t[:m.end()] + '\n' + links + t[m.end():] if m else t.replace('</title>', '</title>\n' + links, 1)


def portada(hechos, plantilla):
    """aurzane.com/en/articles/: lista de los artículos en inglés, con el mismo diseño que los artículos."""
    items = ''.join(f'<a class="related-card" href="{url_en(s)}">\n      <span class="cat">{html.escape(hechos[s]["categoria"])}</span>\n      <h5>{html.escape(hechos[s]["titulo"])}</h5>\n'
                    f'      <p>{html.escape(hechos[s]["resumen"])}</p>\n    </a>' for s in LISTA if s in hechos)
    main = ('\n  <span class="art-eyebrow">AURZANE · Articles</span>\n  <h1 class="art-title">Science, explained simply</h1>\n'
            '  <p class="art-resumen">Plain-language summaries of studies and meta-analyses on learning, psychology, careers and wellbeing. '
            'Every article cites its sources, so you can check them yourself.</p>\n'
            f'  <div class="related" style="margin-top:28px">\n    <div class="related-grid">{items}</div>\n  </div>\n'
            '  <p style="font-size:.9rem;margin-top:26px">More articles in Spanish: <a href="https://aurzane.com/articulos/" hreflang="es" lang="es">Artículos de AURZANE</a>.</p>\n')
    t = plantilla
    for es, en in FIJOS: t = t.replace(es, en)
    t = re.sub(r'(<html lang=")[^"]*', lambda m: m.group(1) + 'en', t, count=1)
    t = re.sub(r'(<main class="article wrap">)[\s\S]*?(</main>)', lambda m: m.group(1) + main + m.group(2), t, count=1)
    t = re.sub(r'<nav class="breadcrumb wrap">[\s\S]*?</nav>', '<nav class="breadcrumb wrap">\n    <a href="https://aurzane.com">Home</a><span class="sep">/</span>\n    <span class="current">Articles</span>\n  </nav>', t, count=1)
    t = re.sub(r'<title>[^<]*</title>', '<title>Articles: science explained simply | AURZANE</title>', t, count=1)
    desc = 'Plain-language summaries of studies and meta-analyses on learning, psychology, careers and wellbeing, with their sources.'
    for p in (r'(<meta name="description" content=")[^"]*', r'(<meta property="og:description" content=")[^"]*', r'(<meta name="twitter:description" content=")[^"]*'):
        t = re.sub(p, lambda m: m.group(1) + desc, t, count=1)
    for p in (r'(<meta property="og:title" content=")[^"]*', r'(<meta name="twitter:title" content=")[^"]*'):
        t = re.sub(p, lambda m: m.group(1) + 'Articles: science explained simply | AURZANE', t, count=1)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + 'https://aurzane.com/en/articles/', t, count=1)
    t = re.sub(r'<meta property="og:type" content="article">', '<meta property="og:type" content="website">', t, count=1)
    t = re.sub(r'<link rel="(canonical|alternate)"[^>]*>\s*', '', t)
    t = t.replace('</title>', '</title>\n<link rel="canonical" href="https://aurzane.com/en/articles/"><link rel="alternate" hreflang="en" href="https://aurzane.com/en/articles/">'
                  '<link rel="alternate" hreflang="es" href="https://aurzane.com/articulos/"><link rel="alternate" hreflang="x-default" href="https://aurzane.com/articulos/">', 1)
    t = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>', '<script type="application/ld+json">' + json.dumps(
        {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'AURZANE articles in English', 'url': 'https://aurzane.com/en/articles/', 'inLanguage': 'en',
         'hasPart': [{'@type': 'Article', 'headline': hechos[s]['titulo'], 'url': url_en(s)} for s in LISTA if s in hechos]}, ensure_ascii=False) + '</script>', t, count=1)
    t = re.sub(r'<meta name="robots"[^>]*>\s*', '', t)   # la portada sí se indexa aunque el artículo usado como molde esté pendiente de revisión
    t = re.sub(r'<div class="art-hero">[\s\S]*?</div>', '', t)
    return t


# ------------------------------------------------------------------ programa
if not SSH: raise SystemExit('Falta SSH')
nuevos, cambios, plantilla = 0, False, ''
pendientes_rel = []   # artículos ya traducidos: se les ponen al día las tarjetas «Keep reading»
hechos = {s: v for s, v in EST.items() if v.get('titulo')}
for slug in LISTA:
    t_es = remoto(f'cat {WEB}/articulos/{slug}/index.html 2>/dev/null')
    p = partes(t_es) if t_es else None
    if not p: print('::warning::No encuentro el artículo español', slug); continue
    if not plantilla: plantilla = t_es
    _, main = p
    h = huella(main)
    existe = remoto(f'test -f {WEB}/en/articles/{slug}/index.html && echo SI').strip() == 'SI'
    if EST.get(slug, {}).get('huella') == h and existe:
        # el español no cambió: solo se asegura el enlace de idioma en la página española
        n_es = enlazar_es(t_es, slug)
        if n_es != t_es and escribir(f'{WEB}/articulos/{slug}/index.html', n_es): cambios = True
        pendientes_rel.append(slug)
        continue
    if nuevos >= MAX: continue
    nuevos += 1
    print('Traduciendo', slug)
    mapa = mapa_ingles(HREF.findall(main))
    main_en = traducir_main(main)
    if not main_en: print('::warning::Sin traducción válida para', slug); continue
    for es_u, en_u in mapa.items(): main_en = main_en.replace(f'href="{es_u}"', f'href="{en_u}"')
    nt, motivo = nota(main, main_en)
    print(f'  nota {nt}/10: {motivo}')
    if nt < 8: print('::warning::Traducción de', slug, 'con', nt, '/10, no se publica:', motivo); continue
    t_en, datos = pagina_en(t_es, slug, main_en, hechos)
    if escribir(f'{WEB}/en/articles/{slug}/index.html', t_en):
        EST[slug] = dict(datos, huella=h, fecha=HOY, nota=nt); hechos[slug] = EST[slug]; cambios = True
        n_es = enlazar_es(t_es, slug)
        if n_es != t_es: escribir(f'{WEB}/articulos/{slug}/index.html', n_es)
        print('  publicado', url_en(slug))
for slug in pendientes_rel:
    t_en = remoto(f'cat {WEB}/en/articles/{slug}/index.html 2>/dev/null')
    if '<main class="article wrap">' not in t_en: continue
    sin = re.sub(r'\n  <div class="related">[\s\S]*?</div>\n  </div>', '', t_en, count=1)
    rel = relacionados(slug, hechos)
    n_en = re.sub(r'(\n\s*<a class="back-hub")', lambda m: rel + m.group(1), sin, count=1) if rel and 'class="back-hub"' in sin else sin.replace('</main>', rel + '</main>', 1)
    if n_en != t_en and escribir(f'{WEB}/en/articles/{slug}/index.html', n_en): cambios = True
if hechos and plantilla and (cambios or remoto(f'test -f {WEB}/en/articles/index.html && echo SI').strip() != 'SI'):
    # en cada artículo, las tarjetas «Keep reading» con los demás ya traducidos
    escribir(f'{WEB}/en/articles/index.html', portada(hechos, plantilla))
    remoto('site-tools-client domain-all update id=aurzane.com flush_cache=1 >/dev/null 2>&1; true')
json.dump(EST, open(EST_F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'Artículos en inglés: {len(hechos)} publicados, {nuevos} trabajados hoy')
