"""Catálogo de cursos de AURZANE LEARN, páginas de cada curso, títulos para Google y revisión diaria.

Cada día:
1. Lee de Supabase los cursos publicados con sus temas y lecciones.
2. Comprueba que cada curso funciona (temas, lecciones, preguntas suficientes, certificado) y deja el resultado
   en cursos/salud.json, que el panel de resultados muestra.
3. Para cada curso nuevo o con título de más de 30 días, mira qué busca la gente en Google (sugerencias de búsqueda)
   y pide a la IA un título y una descripción honestos que respondan a esas búsquedas (cursos/seo.json).
4. Genera learn.aurzane.com/cursos/ (catálogo con buscador y filtros), learn.aurzane.com/curso/<slug>/ (página
   indexable de cada curso con su temario y datos estructurados), sitemap y robots, y los sube al servidor.
Entradas: SUPABASE_SERVICE_KEY, GEMINI_API_KEY, GITHUB_TOKEN, SSH, SG_DEST.
"""
import json, os, re, html, datetime, subprocess, urllib.request, urllib.parse, tarfile, io

R = os.path.dirname(os.path.abspath(__file__))
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co'
KEY = os.environ.get('SUPABASE_SERVICE_KEY', '').strip() or 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'  # la publicable basta: solo se lee lo publicado
HOY = datetime.date.today().isoformat()
OUT = os.path.join(R, 'salida'); os.makedirs(OUT, exist_ok=True)
AREAS = ['Psicología y bienestar', 'Estudiar psicología', 'Neurociencias', 'Educación', 'Estudio y aprendizaje', 'Finanzas personales', 'Tecnología']
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)


def leer(n, d):
    try: return json.load(open(os.path.join(R, n), encoding='utf-8'))
    except Exception: return d


def guardar(n, d): json.dump(d, open(os.path.join(R, n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def sb(ruta):
    rq = urllib.request.Request(f'{SB}/rest/v1/{ruta}', headers={'apikey': KEY})
    with urllib.request.urlopen(rq, timeout=60) as r: return json.load(r)


def pedir(url, datos, cab):
    rq = urllib.request.Request(url, data=json.dumps(datos).encode(), headers=dict(cab, **{'Content-Type': 'application/json'}))
    with urllib.request.urlopen(rq, timeout=120) as r: return json.load(r)


def ia(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    for m in ['gemini-flash-latest', 'gemini-flash-lite-latest']:
        if not k: break
        try:
            r = pedir(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}',
                      {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': .4, 'responseMimeType': 'application/json'}}, {})
            return json.loads(''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts']))
        except Exception as e: print('gemini', m, str(e)[:90])
    g = os.environ.get('GITHUB_TOKEN', '').strip()
    for m in ['openai/gpt-4.1-mini', 'openai/gpt-4.1']:
        if not g: break
        try:
            r = pedir('https://models.github.ai/inference/chat/completions', {'model': m, 'response_format': {'type': 'json_object'},
                      'messages': [{'role': 'user', 'content': prompt}]}, {'Authorization': 'Bearer ' + g})
            return json.loads(r['choices'][0]['message']['content'])
        except Exception as e: print('github', m, str(e)[:90])
    return None


def sugerencias(q):
    """Lo que la gente escribe en Google empezando por q (España y Latinoamérica)."""
    out = []
    for gl in ['es', 'mx', 'ec']:
        try:
            u = 'https://suggestqueries.google.com/complete/search?client=firefox&hl=es&gl=' + gl + '&q=' + urllib.parse.quote(q)
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20) as r:
                out += json.loads(r.read().decode('utf-8', 'replace'))[1]
        except Exception as e: print('sugerencias', q, str(e)[:60])
    return list(dict.fromkeys(out))[:20]



# ---------- portadas: siempre fotos reales de Wikimedia Commons con licencia libre ----------
LIC_OK = re.compile(r'^(CC BY(-SA)? [0-9.]+|CC0|Public domain|PD.*|Dominio público)', re.I)
NO_FOTO = re.compile(r'logo|map\b|mapa|diagram|chart|icon|svg|drawing|illustration|ilustraci|clipart|cartoon|scheme|esquema|ai[- ]generated|midjourney|dall', re.I)


def commons(q):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
        'gsrsearch': q + ' filetype:bitmap', 'gsrlimit': 30, 'prop': 'imageinfo', 'iiprop': 'url|size|mime|extmetadata', 'iiurlwidth': 1600})
    with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AURZANE-cursos/1.0 (hola@aurzane.com)'}), timeout=60) as r:
        pags = (json.load(r).get('query') or {}).get('pages', {}).values()
    out = []
    for pg in pags:
        ii = (pg.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata') or {}
        lic = (md.get('LicenseShortName') or {}).get('value', '')
        w, h = ii.get('width', 0), ii.get('height', 0)
        if not LIC_OK.match(lic) or w < 1400 or not h or not 1.25 <= w / h <= 2.2 or ii.get('mime') not in ('image/jpeg', 'image/png') or NO_FOTO.search(pg.get('title', '')): continue
        autor = re.sub(r'<[^>]+>', '', (md.get('Artist') or {}).get('value', '')).strip()[:120] or 'Autor desconocido'
        desc = re.sub(r'<[^>]+>', '', (md.get('ImageDescription') or {}).get('value', ''))[:200]
        out.append({'titulo': pg['title'], 'desc': desc, 'autor': autor, 'licencia': lic, 'pagina': ii.get('descriptionurl'), 'url': ii.get('thumburl') or ii.get('url')})
    return out


def portada_web(c):
    """Elige y descarga una foto real para el curso si todavía no tiene una de la web. Devuelve True si cambió."""
    mt = meta.setdefault(c['slug'], {})
    if (mt.get('portada_credito') or {}).get('pagina'): return False
    cand = []
    for q in (mt.get('portada_busqueda') or (mt.get('etiquetas') or [c['titulo']])[:2]):
        try: cand += commons(q)
        except Exception as e: print('commons', q, str(e)[:80])
    cand = list({x['titulo']: x for x in cand}.values())[:24]
    if not cand: print('sin foto libre para', c['slug']); return False
    r = ia('Elige la mejor foto de portada para un curso online en español. Curso: «' + c['titulo'] + '». ' + (c.get('subtitulo') or '') +
           '. Debe ser una fotografía real, profesional, sin texto ni logotipos, sin personas en situación vulnerable o angustiosa, adecuada como portada. '
           'Candidatas (índice: título · descripción):\n' + '\n'.join(f'{i}: {x["titulo"]} · {x["desc"]}' for i, x in enumerate(cand)) +
           '\nJSON: {"indice": número, "alt": "descripción breve de la foto en español (máx. 120 caracteres)"}')
    i = r.get('indice') if isinstance(r, dict) else 0
    x = cand[i if isinstance(i, int) and 0 <= i < len(cand) else 0]
    from PIL import Image
    with urllib.request.urlopen(urllib.request.Request(x['url'], headers={'User-Agent': 'AURZANE-cursos/1.0 (hola@aurzane.com)'}), timeout=120) as resp:
        im = Image.open(io.BytesIO(resp.read())).convert('RGB')
    W, H = im.size; obj = 16 / 9
    if W / H > obj: nw = int(H * obj); im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
    else: nh = int(W / obj); im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    im = im.resize((1200, 675), Image.LANCZOS)
    nombre = mt.get('portada') or f'portada-{c["slug"]}.webp'
    p = os.path.join(OUT, 'cursos', nombre); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p, 'WEBP', quality=82)
    mt['portada'] = nombre
    mt['portada_credito'] = {'autor': x['autor'], 'licencia': x['licencia'], 'pagina': x['pagina'], 'titulo': x['titulo'], 'alt': (r or {}).get('alt') if isinstance(r, dict) else '', 'fecha': HOY}
    print('portada real', c['slug'], '·', x['titulo'], '·', x['licencia'])
    return True

# ---------- 1. datos ----------
rq = urllib.request.Request(f'{SB}/rest/v1/rpc/course_catalog_public', data=b'{}', headers={'apikey': KEY, 'Content-Type': 'application/json'})
with urllib.request.urlopen(rq, timeout=60) as r: cursos = json.load(r)
meta = leer('meta.json', {})
seo = leer('seo.json', {})
salud = {'fecha': HOY, 'cursos': []}

for c in cursos:
    c['n_lec'] = sum(len(m['lecciones']) for m in c['modulos'])
    c['n_preg'] = c.get('preguntas') or 0
    c['min'] = sum((l.get('minutos') or 0) for m in c['modulos'] for l in m['lecciones'])
    mt = meta.get(c['slug'])
    if not mt or mt.get('area') not in AREAS:
        r = ia(f'Clasifica este curso online. Título: {c["titulo"]}. Descripción: {c.get("descripcion") or ""}. '
               f'Devuelve JSON {{"area": una de {AREAS}, "publico": "a quién va dirigido en una frase corta", '
               '"etiquetas": ["8 palabras o expresiones cortas, en minúsculas, que alguien escribiría al buscar este curso"]}}')
        if r and r.get('area') in AREAS:
            mt = dict(mt or {}, **{k: r[k] for k in ('area', 'publico', 'etiquetas') if k in r}); meta[c['slug']] = mt
    c['meta'] = mt or {'area': 'Estudio y aprendizaje', 'publico': '', 'etiquetas': []}
    try: portada_web(c)
    except Exception as e: print('portada', c['slug'], str(e)[:120])
    c['meta'] = meta.get(c['slug'], c['meta'])

    # ---------- 2. revisión de funcionamiento ----------
    prob = []
    if not c['modulos']: prob.append('no tiene temas publicados')
    for m in c['modulos']:
        if not m['lecciones']: prob.append(f'el tema «{m["titulo"]}» no tiene lecciones')
    if c['n_lec'] and c['n_preg'] < c['n_lec'] * 3: prob.append(f'pocas preguntas ({c["n_preg"]} para {c["n_lec"]} lecciones)')
    if c.get('certificable'):
        try:
            st = pedir(f'{SB}/rest/v1/rpc/course_certificate_status', {'p_course': c['slug']}, {'apikey': KEY})
            if not (isinstance(st, dict) and st.get('certificable')): prob.append('el certificado no responde bien')
        except Exception as e: prob.append('el certificado da error: ' + str(e)[:80])
    horas_reales = round(c['min'] / 60 * 1.6, 1)  # lectura + práctica + tests
    if c.get('horas_estimadas') and abs(float(c['horas_estimadas']) - horas_reales) > max(2, horas_reales * .6):
        prob.append(f'las horas anunciadas ({c["horas_estimadas"]}) no cuadran con el contenido (unas {horas_reales})')
    salud['cursos'].append({'slug': c['slug'], 'titulo': c['titulo'], 'temas': len(c['modulos']), 'lecciones': c['n_lec'],
                            'preguntas': c['n_preg'], 'horas': c.get('horas_estimadas'), 'certificado': bool(c.get('certificable')),
                            'estado': 'ok' if not prob else 'revisar', 'problemas': prob})

    # ---------- 3. títulos según lo que se busca ----------
    s = seo.get(c['slug'])
    viejo = not s or (datetime.date.fromisoformat(s.get('fecha', '2000-01-01')) < datetime.date.today() - datetime.timedelta(days=30))
    if viejo:
        semillas = (c['meta'].get('etiquetas') or [])[:3] or [c['titulo']]
        consultas = []
        for q in ['curso ' + semillas[0], 'curso gratis ' + semillas[0]] + semillas[1:3]: consultas += sugerencias(q)
        consultas = list(dict.fromkeys(consultas))[:40]
        r = ia('Eres el responsable de SEO de AURZANE LEARN, una plataforma de cursos online gratuitos en español. '
               f'Curso: «{c["titulo"]}». {c.get("subtitulo") or ""}. Nivel: {c.get("nivel")}. Horas: {c.get("horas_estimadas")}. '
               f'Certificado gratuito: {"sí" if c.get("certificable") else "no"}. Temas: {", ".join(m["titulo"] for m in c["modulos"])}.\n'
               f'Búsquedas reales de Google relacionadas: {consultas}\n'
               'Escribe un título SEO (máximo 60 caracteres) y una meta descripción (entre 140 y 158 caracteres) que respondan a las búsquedas '
               'más útiles y sean 100 % verdaderos: no prometas nada que el curso no tenga, no digas «oficial» ni «título», sin rayas largas, sin mayúsculas en cada palabra. '
               'Si el curso tiene certificado puedes decir «con certificado». '
               'JSON: {"title": "...", "description": "...", "busquedas_objetivo": ["las 3 búsquedas que cubres"]}')
        if r and r.get('title') and len(r['title']) <= 65 and 100 <= len(r.get('description', '')) <= 170 and '—' not in r['title'] + r['description'] \
                and not re.search(r'oficial|t[ií]tulo|homologad', r['title'] + r['description'], re.I):
            seo[c['slug']] = {'title': r['title'], 'description': r['description'], 'busquedas': r.get('busquedas_objetivo', []), 'consultas': consultas[:15], 'fecha': HOY}
            print('título nuevo', c['slug'], '·', r['title'])
    c['seo'] = seo.get(c['slug']) or {'title': c['titulo'] + ' | Curso gratis', 'description': (c.get('descripcion') or '')[:155]}

guardar('meta.json', meta); guardar('seo.json', seo); guardar('salud.json', salud)

# ---------- 4. páginas ----------
CSS = """:root{--fondo:#f7f3ea;--superficie:#fffdf8;--tinta:#141a33;--suave:#5b5d6e;--linea:#e2dccd;--oro:#a8822f;--oro-cl:#e7d39b;--azul:#141a3a;--chip:#efe7d4;--acento:#1f2a5c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fondo:#0c1022;--superficie:#141a33;--tinta:#ece8dd;--suave:#a9adc2;--linea:#262e52;--chip:#1c2446;--acento:#e7d39b}}
:root[data-theme="dark"]{--fondo:#0c1022;--superficie:#141a33;--tinta:#ece8dd;--suave:#a9adc2;--linea:#262e52;--chip:#1c2446;--acento:#e7d39b}
*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--tinta);font:16px/1.6 'Instrument Sans',system-ui,sans-serif}
a{color:inherit}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--oro);outline-offset:2px}
.w{max-width:1120px;margin:0 auto;padding:0 16px}
.top{display:flex;justify-content:space-between;align-items:center;padding:18px 0}.top a{text-decoration:none;font-weight:600}
.marca{font:600 1.15rem 'Bodoni Moda',serif;letter-spacing:.14em}
h1{font:500 clamp(2rem,5vw,3.2rem)/1.08 'Bodoni Moda',serif;margin:.2em 0 .3em}
h2{font:500 1.7rem/1.2 'Bodoni Moda',serif;margin:1.6em 0 .5em}
.lead{color:var(--suave);max-width:62ch;font-size:1.08rem}
.btn{display:inline-block;padding:.75em 1.3em;border-radius:999px;background:var(--azul);color:#f4ead0;text-decoration:none;font-weight:600;border:0;cursor:pointer;font:inherit;font-weight:600}
:root[data-theme="dark"] .btn{background:var(--oro-cl);color:#141a33}@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .btn{background:var(--oro-cl);color:#141a33}}
.btn.sec{background:transparent;color:inherit;border:1px solid var(--linea)}
.chip{display:inline-flex;align-items:center;gap:.35em;padding:.3em .75em;border-radius:999px;background:var(--chip);font-size:.85rem;color:var(--tinta)}
.chip.oro{background:var(--oro);color:#fff}
footer{margin-top:64px;padding:28px 0;border-top:1px solid var(--linea);color:var(--suave);font-size:.9rem}"""
HEAD = lambda t, d, canon, extra='': (f'<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
    f'<script src="https://aurzane.com/aurzane-paleta.js"></script><title>{E(t)}</title><meta name="description" content="{E(d)}"><link rel="canonical" href="{canon}">'
    f'<meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(d)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">'
    '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,500;6..96,600&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">'
    f'<style>{CSS}</style>{extra}</head><body>')
PIE = ('<footer><div class="w">Cursos libres y gratuitos de AURZANE LEARN. Formación no reglada: los certificados acreditan el aprovechamiento de un curso, no son títulos oficiales. '
       '<a href="https://aurzane.com/politica-editorial.html">Política editorial</a> · <a href="https://aurzane.com/privacidad.html">Privacidad</a></div></footer></body></html>')
PORTADAS = {'ansiedad-dia-a-dia': 'portada-ansiedad.webp', 'neuroanatomia-funcional': 'portada-neuro.webp', 'tecnicas-neurociencias': 'portada-metodologia.webp'}
portada = lambda c: 'https://learn.aurzane.com/cursos/' + (meta.get(c['slug'], {}).get('portada') or PORTADAS.get(c['slug'], 'portada-neuro.webp'))
horas = lambda h: (f'{float(h):g} h' if h else '')
NIVEL = lambda n: {'inicial': 'Inicial', 'intermedio': 'Intermedio', 'avanzado': 'Avanzado'}.get((n or '').lower(), (n or '').capitalize() or 'Inicial')

ficheros = {}
for c in cursos:
    url = f'https://learn.aurzane.com/curso/{c["slug"]}/'
    temario = ''.join(f'<li><details{" open" if i == 0 else ""}><summary><span class="n">Tema {i + 1}</span> {E(m["titulo"])} <span class="t">{len(m["lecciones"])} lecciones</span></summary>'
                      + (f'<p>{E(m.get("descripcion"))}</p>' if m.get('descripcion') else '')
                      + '<ol>' + ''.join(f'<li>{E(l["titulo"])}<span class="t">{l.get("minutos") or ""} min</span></li>' for l in m['lecciones']) + '</ol></details></li>'
                      for i, m in enumerate(c['modulos']))
    objetivos = ''.join(f'<li>{E(o)}</li>' for o in (c.get('objetivos') or [])[:8])
    ld = {'@context': 'https://schema.org', '@type': 'Course', 'name': c['titulo'], 'description': c.get('descripcion') or c['seo']['description'],
          'url': url, 'inLanguage': 'es', 'isAccessibleForFree': True, 'image': portada(c),
          'provider': {'@type': 'Organization', 'name': 'AURZANE LEARN', 'url': 'https://learn.aurzane.com/'},
          'offers': {'@type': 'Offer', 'price': 0, 'priceCurrency': 'EUR', 'category': 'Free'},
          'hasCourseInstance': {'@type': 'CourseInstance', 'courseMode': 'Online', 'courseWorkload': f'PT{int(float(c.get("horas_estimadas") or 1))}H'},
          'educationalLevel': NIVEL(c.get('nivel')), 'syllabusSections': [{'@type': 'Syllabus', 'name': m['titulo']} for m in c['modulos']]}
    pg = (HEAD(c['seo']['title'] + ' · AURZANE LEARN' if 'AURZANE' not in c['seo']['title'] else c['seo']['title'], c['seo']['description'], url,
               '<style>.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:32px;align-items:center;padding:24px 0 8px}.hero img{width:100%;height:auto;border-radius:18px;display:block}'
               '.datos{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 22px}.tem{list-style:none;padding:0;margin:0}.tem>li{border:1px solid var(--linea);border-radius:14px;margin:10px 0;background:var(--superficie)}'
               '.tem summary{cursor:pointer;padding:14px 18px;font-weight:600;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}.tem .n{color:var(--oro);font-size:.85rem}.tem .t{margin-left:auto;color:var(--suave);font-weight:400;font-size:.88rem}'
               '.tem ol{margin:0 18px 16px 34px;padding:0}.tem ol li{padding:4px 0;display:flex;gap:10px}.tem ol .t{margin-left:auto}.tem p{margin:0 18px 8px;color:var(--suave)}'
               '.caja{background:var(--superficie);border:1px solid var(--linea);border-radius:16px;padding:20px 22px;margin:18px 0}.fuentes{font-size:.9rem;color:var(--suave)}'
               '@media (max-width:760px){.hero{grid-template-columns:1fr}}</style>'
               f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
          + '<div class="w"><nav class="top"><a class="marca" href="https://learn.aurzane.com/">AURZANE LEARN</a><a href="https://learn.aurzane.com/cursos/">Todos los cursos</a></nav>'
          f'<main><div class="hero"><div><span class="chip">{E(c["meta"]["area"])}</span><h1>{E(c["titulo"])}</h1><p class="lead">{E(c.get("subtitulo") or "")}</p>'
          f'<div class="datos"><span class="chip">{horas(c.get("horas_estimadas"))}</span><span class="chip">Nivel {E(NIVEL(c.get("nivel")))}</span>'
          f'<span class="chip">{len(c["modulos"])} temas · {c["n_lec"]} lecciones</span><span class="chip">{c["n_preg"]} preguntas</span><span class="chip">Gratis</span>'
          + ('<span class="chip oro">Con certificado</span>' if c.get('certificable') else '') + '</div>'
          f'<a class="btn" href="https://learn.aurzane.com/cursos.html?c={c["slug"]}">Empezar el curso</a> <a class="btn sec" href="#temario">Ver el temario</a></div>'
          f'<img src="{portada(c)}" alt="{E((c["meta"].get("portada_credito") or {}).get("alt") or "")}" width="1200" height="675"></div>'
          f'<div class="caja"><h2 style="margin-top:0">Sobre este curso</h2><p>{E(c.get("descripcion") or "")}</p>'
          + (f'<p><strong>A quién va dirigido:</strong> {E(c["meta"].get("publico"))}</p>' if c['meta'].get('publico') else '') + '</div>'
          + (f'<h2>Lo que aprenderás</h2><ul>{objetivos}</ul>' if objetivos else '')
          + f'<h2 id="temario">Temario</h2><ul class="tem">{temario}</ul>'
          + ('<div class="caja"><h2 style="margin-top:0">Certificado gratuito</h2><p>Al aprobar la evaluación final completa con un '
             f'{round(float(c.get("nota_minima") or .8) * 100)} % o más, y tras abrir al menos el 80 % de las lecciones, puedes descargar un certificado de aprovechamiento con código de verificación. '
             'Es formación libre y no reglada, sin validez académica oficial. <a href="https://learn.aurzane.com/certificado/">Verificar un certificado</a></p></div>' if c.get('certificable') else '')
          + f'<h2>Cómo funciona</h2><p>Cada tema incluye lecciones, mapa conceptual, esquema, tarjetas de repaso, la técnica de Feynman y un test. Solo necesitas una cuenta gratuita de AURZANE ID para guardar tu progreso.</p>'
          + f'<p class="fuentes"><strong>Fuentes y autoría:</strong> {E(c.get("nota_fuentes") or "")}</p>'
          + ((lambda k: f'<p class="fuentes"><strong>Imagen de portada:</strong> {E(k["autor"])}, <a href="{E(k["pagina"])}" rel="noopener">Wikimedia Commons</a>, {E(k["licencia"])}.</p>' if k else '')(c['meta'].get('portada_credito')))
          + f'<p><a class="btn" href="https://learn.aurzane.com/cursos.html?c={c["slug"]}">Empezar el curso gratis</a></p></main></div>' + PIE)
    ficheros[f'curso/{c["slug"]}/index.html'] = pg

# catálogo
datos_js = [{'s': c['slug'], 't': c['titulo'], 'st': c.get('subtitulo') or '', 'a': c['meta']['area'], 'n': NIVEL(c.get('nivel')),
             'h': float(c.get('horas_estimadas') or 0), 'cert': bool(c.get('certificable')), 'l': c['n_lec'], 'img': portada(c),
             'k': ' '.join([c['titulo'], c.get('subtitulo') or '', c['meta']['area']] + (c['meta'].get('etiquetas') or [])).lower(),
             'f': c.get('published_at') or ''} for c in cursos]
areas_usadas = [a for a in AREAS if any(d['a'] == a for d in datos_js)]
cat = (HEAD('Cursos gratis online con certificado · AURZANE LEARN',
            'Cursos online gratuitos en español de psicología, bienestar y neurociencias, con tests, tarjetas de repaso y certificado de aprovechamiento. Filtra por tema, nivel y duración.',
            'https://learn.aurzane.com/cursos/',
            '<style>.buscar{display:flex;gap:10px;margin:18px 0 6px}.buscar input{flex:1;font:inherit;padding:.8em 1em;border-radius:999px;border:1px solid var(--linea);background:var(--superficie);color:inherit}'
            '.intenciones{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 4px}.intenciones button{font:inherit;font-size:.92rem;padding:.5em 1em;border-radius:999px;border:1px solid var(--linea);background:var(--superficie);color:inherit;cursor:pointer}'
            '.intenciones button[aria-pressed="true"]{background:var(--azul);color:#f4ead0;border-color:var(--azul)}'
            '.filtros{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:16px 0;padding:14px 16px;background:var(--superficie);border:1px solid var(--linea);border-radius:16px}'
            '.filtros label{font-size:.85rem;color:var(--suave);display:flex;flex-direction:column;gap:4px}.filtros select{font:inherit;padding:.45em .7em;border-radius:10px;border:1px solid var(--linea);background:var(--fondo);color:inherit}'
            '.filtros .chk{flex-direction:row;align-items:center;gap:8px;color:var(--tinta);font-size:.95rem}.cuenta{margin-left:auto;color:var(--suave);font-size:.9rem}'
            '.rej{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}.card{background:var(--superficie);border:1px solid var(--linea);border-radius:18px;overflow:hidden;display:flex;flex-direction:column;text-decoration:none}'
            '.card img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block}.card .c{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}.card h3{font:600 1.2rem/1.25 "Bodoni Moda",serif;margin:0}'
            '.card p{margin:0;color:var(--suave);font-size:.95rem}.card .d{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:6px}.card:hover{border-color:var(--oro)}'
            '.reco{border:2px solid var(--oro)}.reco-et{font-size:.8rem;font-weight:700;color:var(--oro)}.vacio{padding:40px;text-align:center;color:var(--suave)}</style>')
       + '<div class="w"><nav class="top"><a class="marca" href="https://learn.aurzane.com/">AURZANE LEARN</a><a href="https://learn.aurzane.com/certificado/">Verificar certificado</a></nav><main>'
       '<h1>Cursos gratis, a tu ritmo</h1><p class="lead">Cursos completos en español con lecciones, mapas, tarjetas de repaso y tests. Algunos incluyen certificado de aprovechamiento gratuito.</p>'
       '<div class="buscar"><input id="q" type="search" placeholder="¿Qué quieres aprender? Por ejemplo: ansiedad, cerebro, estudiar mejor" aria-label="Buscar cursos"></div>'
       '<div class="intenciones" role="group" aria-label="¿Qué buscas?">'
       '<button type="button" data-i="bienestar" aria-pressed="false">Sentirme mejor</button><button type="button" data-i="cert" aria-pressed="false">Quiero un certificado</button>'
       '<button type="button" data-i="empezar" aria-pressed="false">Empezar desde cero</button><button type="button" data-i="corto" aria-pressed="false">Algo corto</button>'
       '<button type="button" data-i="profundo" aria-pressed="false">Profundizar en un tema</button></div>'
       '<div class="filtros"><label>Tema<select id="fa"><option value="">Todos</option>' + ''.join(f'<option>{E(a)}</option>' for a in areas_usadas) + '</select></label>'
       '<label>Nivel<select id="fn"><option value="">Todos</option><option>Inicial</option><option>Intermedio</option><option>Avanzado</option></select></label>'
       '<label>Duración<select id="fd"><option value="">Cualquiera</option><option value="0-5">Menos de 5 horas</option><option value="5-20">De 5 a 20 horas</option><option value="20-999">Más de 20 horas</option></select></label>'
       '<label>Ordenar<select id="fo"><option value="r">Recomendados</option><option value="n">Más nuevos</option><option value="c">Más cortos</option><option value="l">Más largos</option></select></label>'
       '<label class="chk"><input type="checkbox" id="fc"> Solo con certificado</label><span class="cuenta" id="cuenta" aria-live="polite"></span></div>'
       '<div class="rej" id="rej"></div></main></div>'
       '<script>(function(){var C=' + json.dumps(datos_js, ensure_ascii=False).replace('</', '<\\/') + ';'
       r"""var SIN={ansiedad:'estres nervios angustia preocupacion panico calma relajacion',estres:'ansiedad agobio',cerebro:'neuro neurociencia neuroanatomia sistema nervioso',psicologia:'psicologo mente emociones conducta',estudiar:'aprendizaje memoria estudio',dormir:'sueño insomnio'};
var $=function(i){return document.getElementById(i)},norm=function(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'')};
var ref=document.referrer||'',pista=/ansiedad|estres|gad|panico|preocupacion|sueno|relajacion|respiracion/.test(norm(ref))?'bienestar':'';
var url=new URLSearchParams(location.search),int=url.get('i')||'';
try{if(!int&&!url.get('q'))int=localStorage.getItem('azCursoInt')||''}catch(e){}
if(url.get('q'))$('q').value=url.get('q');
function pinta(){var q=norm($('q').value),words=q.split(/\s+/).filter(Boolean),fa=$('fa').value,fn=$('fn').value,fd=$('fd').value,fc=$('fc').checked,fo=$('fo').value;
 var L=C.filter(function(c){var k=norm(c.k+' '+c.t+' '+c.st);
  if(words.length&&!words.every(function(w){return k.indexOf(w)>=0||Object.keys(SIN).some(function(s){return (norm(s).indexOf(w)===0||norm(SIN[s]).indexOf(w)>=0)&&(k.indexOf(norm(s))>=0||norm(SIN[s]).split(' ').some(function(x){return k.indexOf(x)>=0}))})}))return false;
  if(fa&&c.a!==fa)return false;if(fn&&c.n!==fn)return false;if(fc&&!c.cert)return false;
  if(fd){var r=fd.split('-');if(c.h<+r[0]||c.h>=+r[1])return false}
  if(int==='bienestar'&&c.a!=='Psicología y bienestar')return false;if(int==='cert'&&!c.cert)return false;if(int==='empezar'&&c.n!=='Inicial')return false;if(int==='corto'&&c.h>=6)return false;if(int==='profundo'&&c.n==='Inicial')return false;
  return true});
 var pts=function(c){return (c.cert?3:0)+(c.n==='Inicial'?2:0)+((pista==='bienestar'&&c.a==='Psicología y bienestar')?5:0)};
 L.sort(fo==='n'?function(a,b){return b.f.localeCompare(a.f)}:fo==='c'?function(a,b){return a.h-b.h}:fo==='l'?function(a,b){return b.h-a.h}:function(a,b){return pts(b)-pts(a)});
 $('cuenta').textContent=L.length+(L.length===1?' curso':' cursos');
 $('rej').innerHTML=L.length?L.map(function(c,i){var reco=fo==='r'&&i===0&&!q;return '<a class="card'+(reco?' reco':'')+'" href="/curso/'+c.s+'/"><img src="'+c.img+'" alt="" loading="lazy" width="1200" height="675"><div class="c">'+(reco?'<span class="reco-et">Recomendado para empezar</span>':'')+'<span class="chip" style="align-self:flex-start">'+c.a+'</span><h3>'+c.t+'</h3><p>'+c.st+'</p><div class="d"><span class="chip">'+(c.h%1?c.h.toLocaleString('es-ES'):c.h)+' h</span><span class="chip">'+c.n+'</span><span class="chip">'+c.l+' lecciones</span>'+(c.cert?'<span class="chip oro">Certificado</span>':'')+'</div></div></a>'}).join(''):'<p class="vacio">No hay cursos con esos filtros todavía. Prueba a quitar alguno.</p>';
 Array.prototype.forEach.call(document.querySelectorAll('.intenciones button'),function(b){b.setAttribute('aria-pressed',b.dataset.i===int?'true':'false')})}
Array.prototype.forEach.call(document.querySelectorAll('.intenciones button'),function(b){b.addEventListener('click',function(){int=int===b.dataset.i?'':b.dataset.i;try{localStorage.setItem('azCursoInt',int)}catch(e){}pinta()})});
['q','fa','fn','fd','fo','fc'].forEach(function(i){$(i).addEventListener(i==='q'?'input':'change',pinta)});pinta()})();</script>"""
       + PIE)
ficheros['cursos/index.html'] = cat
ficheros['sitemap.xml'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                           + f'<url><loc>https://learn.aurzane.com/</loc></url><url><loc>https://learn.aurzane.com/cursos/</loc><lastmod>{HOY}</lastmod></url>'
                           + ''.join(f'<url><loc>https://learn.aurzane.com/curso/{c["slug"]}/</loc><lastmod>{HOY}</lastmod></url>' for c in cursos) + '</urlset>\n')
ficheros['robots.txt'] = 'User-agent: *\nAllow: /\nDisallow: /admin-cursos.html\nSitemap: https://learn.aurzane.com/sitemap.xml\n'
for n, t in ficheros.items():
    p = os.path.join(OUT, n); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8').write(t.replace('—', ', '))
print(len(cursos), 'cursos ·', sum(1 for s in salud['cursos'] if s['estado'] != 'ok'), 'para revisar')
for s in salud['cursos']:
    if s['problemas']: print('::warning title=Curso ' + s['slug'] + '::' + '; '.join(s['problemas']))

# ---------- 5. subir ----------
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
if SSH and DEST:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as t: t.add(OUT, arcname='.')
    r = subprocess.run(SSH.split() + [DEST, 'cd ~/www/learn.aurzane.com/public_html && tar xzf - && echo OK; site-tools-client domain-all update id=learn.aurzane.com flush_cache=1 >/dev/null 2>&1; true'],
                       input=buf.getvalue(), capture_output=True, timeout=120)
    print('subido' if b'OK' in r.stdout else 'fallo al subir ' + r.stderr.decode()[:200])
