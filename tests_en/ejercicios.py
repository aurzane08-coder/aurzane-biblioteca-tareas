# -*- coding: utf-8 -*-
"""English version of the 13 MIND guided exercises and their index (23/11/2026).
Takes the Spanish pages copied from the server (traer/servidor/mind.aurzane.com/ejercicios/) and writes
publicar/mind.aurzane.com/en/exercises/<slug>/index.html with the same design and player (animated circle, timer, voice).
The voice speaks English. The long Spanish reading guide at the end of each page is left out of the English version.
Texts: tests_en/ejercicios_en.py (same order as the Spanish strings). If a Spanish text is left untranslated, the script stops.
Usage: python3 tests_en/ejercicios.py"""
import os, re, sys, json, html

AQUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(AQUI)
ES = os.path.join(R, 'traer', 'servidor', 'mind.aurzane.com', 'ejercicios')
OUT = os.path.join(R, 'publicar', 'mind.aurzane.com', 'en', 'exercises')
BASE = 'https://mind.aurzane.com/en/exercises/'
sys.path.insert(0, AQUI)
import ejercicios_en  # noqa: E402

SLUG = {'atencion-a-la-respiracion': 'breath-awareness-meditation', 'coherencia-cardiaca': 'coherent-breathing', 'escaneo-corporal': 'body-scan',
        'lugar-seguro': 'safe-place-visualisation', 'pausa-de-autocompasion': 'self-compassion-break', 'relajacion-muscular-progresiva': 'progressive-muscle-relaxation',
        'respiracion-4-7-8': '4-7-8-breathing', 'respiracion-alterna': 'alternate-nostril-breathing', 'respiracion-cuadrada': 'box-breathing',
        'respiracion-diafragmatica': 'diaphragmatic-breathing', 'suspiro-ciclico': 'cyclic-sighing', 'tecnica-5-4-3-2-1': '5-4-3-2-1-grounding', 'tecnica-stop': 'stop-technique'}
H1 = {'atencion-a-la-respiracion': 'Breath awareness <span>meditation</span>', 'coherencia-cardiaca': 'Guided coherent <span>breathing</span>',
      'escaneo-corporal': 'Guided body <span>scan</span>', 'lugar-seguro': 'Safe place <span>visualisation</span>', 'pausa-de-autocompasion': 'Self-compassion <span>break</span>',
      'relajacion-muscular-progresiva': 'Progressive muscle <span>relaxation</span>', 'respiracion-4-7-8': 'Guided <span>4-7-8</span> breathing',
      'respiracion-alterna': 'Guided alternate nostril <span>breathing</span>', 'respiracion-cuadrada': 'Guided box <span>breathing</span>',
      'respiracion-diafragmatica': 'Guided diaphragmatic <span>breathing</span>', 'suspiro-ciclico': 'Guided cyclic <span>sighing</span>',
      'tecnica-5-4-3-2-1': 'The <span>5-4-3-2-1</span> technique', 'tecnica-stop': 'The <span>STOP</span> technique', '': 'Guided <span>exercises</span> to calm your mind'}
# tests de MIND que tienen versión en inglés (para el menú)
TEST_EN = {'/test-de-ansiedad/': '/en/anxiety-test-gad-7/', '/test-de-depresion/': '/en/depression-test-phq-9/', '/test-de-autoestima/': '/en/self-esteem-test-rosenberg/',
           '/test-de-tdah/': '/en/adhd-test-asrs/', '/test-de-autocompasion/': '/en/self-compassion-test-scs-sf/', '/test-de-estres/': '/en/stress-test-dass-21/',
           '/test-de-burnout/': '/en/burnout-test-cbi/', '/test-de-personalidad/': '/en/personality-test-big-five/'}
EXTRA = {'TDAH': 'ADHD', 'MIND': 'MIND', 'Duración': 'Duration', '👤 Mi AURZANE': '👤 My AURZANE', 'Mi AURZANE': 'My AURZANE'}


def textos_es():
    """Mismo inventario y orden que el de las traducciones (ver docstring de ejercicios_en)."""
    orden = {}
    for f in sorted(p for p in os.listdir(ES) if os.path.isdir(os.path.join(ES, p))) + ['']:
        s = open(os.path.join(ES, f, 'index.html'), encoding='utf-8').read()
        m = re.search(r'var GUIA=(\{.*?\});\n', s)
        if m:
            g = json.loads(m.group(1))
            for k in ('listo', 'inicio', 'compartir'):
                if g.get(k): orden.setdefault(g[k], f)
            for x in g.get('fases', []): orden.setdefault(x[2], f)
            for p in g.get('pasos', []): orden.setdefault(p[1], f)
        b = s[s.find('<body'):s.find('<!-- guia AURZANE')] if '<!-- guia AURZANE' in s else s[s.find('<body'):]
        b = re.sub(r'<script.*?</script>|<style.*?</style>', '', b, flags=re.S)
        for m2 in re.finditer(r'>([^<>]+)<', b):
            t = m2.group(1).strip()
            if t and re.search('[a-zá-úñ]{2}', t): orden.setdefault(t, f)
        for m2 in re.finditer(r'(?:alt|aria-label|title|placeholder)="([^"]+)"', b):
            if re.search('[a-zá-ú]{3}', m2.group(1)): orden.setdefault(m2.group(1), f)
        for pat in [r'<title>([^<]+)</title>', r'name="description" content="([^"]+)"', r'og:title" content="([^"]+)"', r'og:description" content="([^"]+)"']:
            m3 = re.search(pat, s)
            if m3: orden.setdefault(m3.group(1), f)
    return list(orden)


ES_TXT = textos_es()
assert len(ES_TXT) == len(ejercicios_en.EN), (len(ES_TXT), len(ejercicios_en.EN))
T = dict(zip(ES_TXT, ejercicios_en.EN)); T.update(EXTRA)
T_HTML = {html.unescape(k): v for k, v in T.items()}

JS = [  # reproductor y ayudas comunes
    ("var NOM={inhala:'Inhala',exhala:'Exhala',manten:'Mantén',pausa:'Pausa'};", "var NOM={inhala:'Breathe in',exhala:'Breathe out',manten:'Hold',pausa:'Pause'};"),
    ("u.lang='es-ES';", "u.lang='en-GB';"),
    ("var vs=speechSynthesis.getVoices().filter(function(v){return /^es/i.test(v.lang);});if(vs.length)u.voice=vs.filter(function(v){return /es-ES/i.test(v.lang);})[0]||vs[0];",
     "var vs=speechSynthesis.getVoices().filter(function(v){return /^en/i.test(v.lang);});if(vs.length)u.voice=vs.filter(function(v){return /en-GB/i.test(v.lang);})[0]||vs[0];"),
    ("$('gPlay').textContent='▶ Seguir';", "$('gPlay').textContent='▶ Resume';"),
    ("$('gPlay').textContent='⏸ Pausa';if('speechSynthesis' in window)speechSynthesis.resume();", "$('gPlay').textContent='⏸ Pause';if('speechSynthesis' in window)speechSynthesis.resume();"),
    ("fin=construir();activo=true;enPausa=false;$('gPlay').textContent='⏸ Pausa';", "fin=construir();activo=true;enPausa=false;$('gPlay').textContent='⏸ Pause';"),
    ("$('gPlay').textContent='▶ Empezar';", "$('gPlay').textContent='▶ Start';"),
    ("'Has terminado. Tómate unos segundos antes de volver a lo que estabas haciendo.'", "'You have finished. Take a few seconds before going back to what you were doing.'"),
    ("$('gHechos').textContent='Lo has hecho '+n+(n===1?' vez':' veces')+' en este dispositivo.';", "$('gHechos').textContent='You have done it '+n+(n===1?' time':' times')+' on this device.';"),
    ("$('gHechos').textContent='Lo has hecho '+n0+(n0===1?' vez':' veces')+' en este dispositivo.';", "$('gHechos').textContent='You have done it '+n0+(n0===1?' time':' times')+' on this device.';"),
    ("'Enlace copiado. Pégalo donde quieras compartirlo.'", "'Link copied. Paste it wherever you want to share it.'"),
    ("'Haz el tuyo gratis: '", "'Try it for free: '"), ("'Mi resultado en '", "'My result in '"), ("'. Haz el tuyo gratis: '", "'. Try it for free: '"),
    ("'Imagen descargada. Súbela a tus historias o envíala por WhatsApp.'", "'Image downloaded. Post it to your stories or send it on WhatsApp.'"),
    ("toLocaleString('es-ES'", "toLocaleString('en-GB'"),
]


def traducir_texto(t):
    k = t.strip()
    if not k or not re.search('[A-Za-zÁ-úñ]', k): return t
    en = T_HTML.get(html.unescape(k))
    if en is None: return t
    return t.replace(k, html.escape(en, quote=False))


def pagina(es_slug):
    s = open(os.path.join(ES, es_slug, 'index.html'), encoding='utf-8').read()
    en_slug = SLUG.get(es_slug, '')
    url = BASE + (en_slug + '/' if en_slug else '')
    url_es = 'https://mind.aurzane.com/ejercicios/' + (es_slug + '/' if es_slug else '')
    # fuera la guía larga en español (texto de apoyo para buscadores)
    s = re.sub(r'<!-- guia AURZANE[^>]*-->\s*<div class="wrap"><section class="bloque az-guia".*?</section></div>', '', s, flags=re.S)
    # guion del reproductor
    m = re.search(r'var GUIA=(\{.*?\});\n', s)
    if m:
        g = json.loads(m.group(1))
        for k in ('listo', 'inicio', 'compartir', 'final'):
            if g.get(k): g[k] = T[g[k]]
        for x in g.get('fases', []): x[2] = T[x[2]]
        for p in g.get('pasos', []): p[1] = T[p[1]]
        g['clave'] = g['clave'] + '-en'
        s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False) + s[m.end(1):]
    for a, b in JS:
        s = s.replace(a, b)
    # título principal (el orden de las palabras cambia en inglés)
    s = re.sub(r'<h1>.*?</h1>', '<h1>' + H1[es_slug] + '</h1>', s, count=1, flags=re.S)
    # cabecera: idioma, canónica, enlaces de idioma
    s = s.replace('<html lang="es">', '<html lang="en">', 1)
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<meta name="aurzane-idiomas" content="no">', 1)
    s = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="https://mind\.aurzane\.com/ejercicios/[^"]*">', '', s)
    s = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{url}">\n<link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="es" href="{url_es}"><link rel="alternate" hreflang="x-default" href="{url_es}">', s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]+', r'\g<1>' + url, s, count=1)
    s = s.replace('content="es_ES"', 'content="en_GB"')
    # datos estructurados
    def ld(mm):
        try: d = json.loads(mm.group(1))
        except Exception: return mm.group(0)
        def rec(x):
            if isinstance(x, dict): return {k: rec(v) for k, v in x.items()}
            if isinstance(x, list): return [rec(v) for v in x]
            if isinstance(x, str):
                if x.startswith('https://mind.aurzane.com/ejercicios/'):
                    r2 = x[len('https://mind.aurzane.com/ejercicios/'):].strip('/')
                    return BASE + (SLUG[r2] + '/' if r2 in SLUG else '')
                if x == 'es': return 'en'
                return T.get(x, x)
            return x
        return '<script type="application/ld+json">' + json.dumps(rec(d), ensure_ascii=False).replace('</', '<\\/') + '</script>'
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, s, flags=re.S)
    # enlaces internos
    for es_s, en_s in SLUG.items():
        s = s.replace(f'href="/ejercicios/{es_s}/"', f'href="/en/exercises/{en_s}/"').replace(f'href="https://mind.aurzane.com/ejercicios/{es_s}/"', f'href="{BASE}{en_s}/"')
    s = s.replace('href="/ejercicios/"', 'href="/en/exercises/"').replace('href="https://mind.aurzane.com/ejercicios/"', f'href="{BASE}"')
    for a, b in TEST_EN.items():
        s = s.replace(f'href="{a}"', f'href="{b}"')
    s = s.replace('<a href="https://mind.aurzane.com/">MIND</a><span>/</span>', '<a href="https://mind.aurzane.com/en/">MIND</a><span>/</span>')
    # textos: nodos de texto y atributos, fuera de scripts y estilos
    trozos = re.split(r'(<script.*?</script>|<style.*?</style>)', s, flags=re.S)
    for i in range(0, len(trozos), 2):
        c = trozos[i]
        c = re.sub(r'>([^<>]+)<', lambda mm: '>' + traducir_texto(mm.group(1)) + '<', c)
        c = re.sub(r'((?:alt|aria-label|title|placeholder|content)=")([^"]+)(")', lambda mm: mm.group(1) + traducir_texto(mm.group(2)) + mm.group(3), c)
        trozos[i] = c
    s = ''.join(trozos)
    s = re.sub(r'<title>([^<]+)</title>', lambda mm: '<title>' + traducir_texto(mm.group(1)) + '</title>', s, count=1)
    # enlace a la versión en español en el pie
    s = s.replace('>Privacy</a>', f'>Privacy</a> · <a href="{url_es}" hreflang="es" lang="es">Versión en español</a>', 1)
    # comprobación: no queda texto visible en español
    cuerpo = re.sub(r'<script.*?</script>|<style.*?</style>', '', s[s.find('<body'):], flags=re.S)
    restos = [t.strip() for t in re.findall(r'>([^<>]*[áéíóúñ¿¡][^<>]*)<', cuerpo) if t.strip() and 'Versión en español' not in t and not t.strip().startswith('Chóliz') and 'Röttger' not in t]
    restos += [x for x in re.findall(r'(?:alt|aria-label|title|placeholder)="([^"]*[áéíóúñ¿][^"]*)"', cuerpo)]
    restos += [t.strip() for t in re.findall(r'>([^<>]+)<', cuerpo) if re.search(r'(?i)\b(mi|de la|del|los|las|para|con|por|una|que|ejercicio|respiraci)\b', t) and 'Versión en español' not in t and not t.strip().startswith(('Chóliz', 'Röttger'))]
    if restos: raise SystemExit(f'{es_slug or "índice"}: quedan textos en español: ' + ' | '.join(restos[:8]))
    js = ' '.join(re.findall(r'<script(?![^>]*src)(?![^>]*ld\+json)[^>]*>(.*?)</script>', s, flags=re.S))
    restos_js = re.findall(r"'[^'\n]*(?:Pausa|Seguir|Empezar|veces|Enlace copiado|Has terminado)[^'\n]*'", js)
    if restos_js: raise SystemExit(f'{es_slug or "índice"}: el reproductor sigue en español: ' + ' | '.join(restos_js[:5]))
    d = os.path.join(OUT, en_slug) if en_slug else OUT
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(s)
    return url


for es_slug in list(SLUG) + ['']:
    print(pagina(es_slug))
