"""Guías completas para los tests, las calculadoras y los ejercicios de AURZANE.

Las páginas de herramientas tenían poco texto (300 a 450 palabras): para Google y AdSense eso es «contenido escaso».
Este script añade a cada una una guía original de 900 a 1.300 palabras escrita por la IA con un guion fijo
(qué es, cómo se interpreta, de qué depende, qué hacer, errores frecuentes, preguntas frecuentes) y la imagen de la página.

- La guía se guarda en guias/textos/<sitio>__<ruta>.json: si una página se regenera y la pierde, se vuelve a poner sin gastar IA.
- En el servidor se inserta antes de la firma del psicólogo (o antes del pie) dentro de <section data-guia>, con copia del
  original en www/<sitio>/eliminar/guias-FECHA/.
- Como mucho LIMITE guías nuevas por pasada (la cuota gratuita de la IA es pequeña).
Entradas: SSH, SG_DEST, GEMINI_API_KEY, GITHUB_TOKEN.
"""
import json, os, re, subprocess, datetime, html, urllib.request

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(R, 'guias', 'textos'); os.makedirs(D, exist_ok=True)
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
HOY = datetime.date.today().isoformat()
LIMITE = int(os.environ.get('LIMITE', '6'))
SITIOS = ['mind.aurzane.com', 'live.aurzane.com', 'build.aurzane.com', 'nexus.aurzane.com', 'learn.aurzane.com']
PATRON = r'(test-de-[a-z0-9-]+|calculadora-[a-z0-9-]+|ejercicios/[a-z0-9-]+)'


def remoto(orden, entrada=None, t=120):
    return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=t, input=entrada).stdout


def pedir(url, datos, cab):
    rq = urllib.request.Request(url, data=json.dumps(datos).encode(), headers=dict(cab, **{'Content-Type': 'application/json'}))
    with urllib.request.urlopen(rq, timeout=180) as r: return json.load(r)


def ia(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    for m in ['gemini-flash-latest', 'gemini-flash-lite-latest']:
        if not k: break
        try:
            r = pedir(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}',
                      {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': .5, 'maxOutputTokens': 6000, 'responseMimeType': 'application/json'}}, {})
            return json.loads(''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts']))
        except Exception as e: print('gemini', m, str(e)[:100])
    g = os.environ.get('GITHUB_TOKEN', '').strip()
    for m in ['openai/gpt-4.1', 'openai/gpt-4.1-mini']:
        if not g: break
        try:
            r = pedir('https://models.github.ai/inference/chat/completions', {'model': m, 'response_format': {'type': 'json_object'},
                      'messages': [{'role': 'user', 'content': prompt}]}, {'Authorization': 'Bearer ' + g})
            return json.loads(r['choices'][0]['message']['content'])
        except Exception as e: print('github', m, str(e)[:100])
    return None


def texto_visible(s):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()


def md(t):
    """Párrafos y listas sencillas a HTML (la IA devuelve texto plano con guiones para las listas)."""
    out, lista = [], []
    for linea in [l.strip() for l in str(t).split('\n')]:
        if re.match(r'^[-*•] ', linea): lista.append('<li>' + html.escape(linea[2:].strip()) + '</li>'); continue
        if lista: out.append('<ul>' + ''.join(lista) + '</ul>'); lista = []
        if linea: out.append('<p>' + html.escape(linea) + '</p>')
    if lista: out.append('<ul>' + ''.join(lista) + '</ul>')
    return ''.join(out).replace('—', ',')


def bloque(g, sitio, ruta):
    img = f'https://{sitio}/{ruta}/og.jpg'
    sec = ''.join(f'<h3>{html.escape(x["titulo"])}</h3>{md(x["texto"])}' for x in g['secciones'])
    faq = ''.join(f'<details><summary>{html.escape(f["p"])}</summary>{md(f["r"])}</details>' for f in g['faq'])
    fuentes = ''.join(f'<li>{html.escape(f)}</li>' for f in g.get('fuentes', [])[:6])
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': f['p'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['r']}} for f in g['faq']]}
    return (f'\n<!-- guia AURZANE {g["fecha"]} -->\n<div class="wrap"><section class="bloque az-guia" data-guia="1" id="guia">'
            '<style>.az-guia h2{margin-bottom:.4em}.az-guia h3{margin:1.4em 0 .4em;font-size:1.15rem}.az-guia p,.az-guia li{line-height:1.7}.az-guia ul{padding-left:1.2em;margin:.6em 0}'
            '.az-guia figure{margin:1.2em 0}.az-guia figure img{width:100%;height:auto;border-radius:14px;display:block}.az-guia figcaption{font-size:.85rem;opacity:.75;margin-top:.4em}'
            '.az-guia details{border-top:1px solid rgba(127,127,127,.25);padding:.7em 0}.az-guia summary{cursor:pointer;font-weight:600}.az-guia .fuentes{font-size:.88rem;opacity:.85}'
            '.az-guia .resp{font-size:.88rem;opacity:.8;margin-top:1em}</style>'
            f'<h2>{html.escape(g["titulo"])}</h2>{md(g["intro"])}'
            f'<figure><img src="{img}" alt="{html.escape(g.get("alt") or g["titulo"])}" loading="lazy" width="1200" height="630"><figcaption>{html.escape(g.get("alt") or "")}</figcaption></figure>'
            f'{sec}<h3>Preguntas frecuentes</h3>{faq}'
            + (f'<h3>Para saber más</h3><ul class="fuentes">{fuentes}</ul>' if fuentes else '')
            + f'<p class="resp">Guía elaborada por AURZANE. Responsable del contenido: Psi. Cl. Adrián Sánchez Samaniego, psicólogo clínico (Registro SENESCYT N.º 1033-2023-2618464). '
              f'Actualizada el {g["fecha"]}. Esta información es orientativa y no sustituye la valoración de un profesional.</p>'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script></section></div>\n')


def valida(g):
    try:
        palabras = len((g['intro'] + ' '.join(x['texto'] for x in g['secciones']) + ' '.join(f['r'] for f in g['faq'])).split())
        return g.get('titulo') and len(g['secciones']) >= 4 and len(g['faq']) >= 3 and palabras >= 700
    except Exception: return False


# 1) páginas candidatas en el servidor
lista = remoto('for s in ' + ' '.join(SITIOS) + '; do cd ~/www/$s/public_html 2>/dev/null && find . -maxdepth 3 -name index.html | sed "s#^\\.#$s#"; cd ~; done')
paginas = sorted({(l.split('/', 1)[0], os.path.dirname(l.split('/', 1)[1]).strip('/')) for l in lista.splitlines()
                  if re.search(r'/' + PATRON + r'/index\.html$', l)})
print(len(paginas), 'páginas de herramientas')
nuevas = hechas = 0
for sitio, ruta in paginas:
    archivo = f'www/{sitio}/public_html/{ruta}/index.html'
    fuente = remoto(f'cat {archivo}')
    if not fuente or 'data-guia="1"' in fuente: continue
    fj = os.path.join(D, f'{sitio}__{ruta.replace("/", "_")}.json')
    g = json.load(open(fj, encoding='utf-8')) if os.path.exists(fj) else None
    if not g:
        if nuevas >= LIMITE: continue
        h1 = texto_visible((re.search(r'<h1.*?</h1>', fuente, re.S) or [''])[0]) if re.search(r'<h1.*?</h1>', fuente, re.S) else ''
        tit = texto_visible((re.search(r'<title>(.*?)</title>', fuente, re.S) or ['', ''])[1])
        actual = texto_visible(re.sub(r'<header.*?</header>|<footer.*?</footer>', ' ', fuente, flags=re.S))[:5000]
        tipo = 'test psicológico de cribado' if ruta.startswith('test-de-') else 'ejercicio guiado de relajación o regulación emocional' if ruta.startswith('ejercicios/') else 'calculadora'
        g = ia('Eres redactor experto de AURZANE, una web española de psicología, bienestar, estudio y finanzas personales dirigida por un psicólogo clínico. '
               f'Escribe una guía original y útil para la página «{tit}» (h1: «{h1}»), que es un/a {tipo}. Lo que ya dice la página (no lo repitas, compleméntalo):\n{actual}\n\n'
               'Requisitos: español de España, cercano y riguroso, para público general; entre 1.000 y 1.300 palabras en total; sin rayas largas; sin inventar cifras, estudios ni autores concretos; '
               'solo conocimiento muy establecido (OMS, guías clínicas, organismos oficiales); nada de diagnósticos ni medicación; si es un test, explica qué mide, cómo interpretar cada rango, '
               'limitaciones y cuándo pedir ayuda (en España, 024 si hay ideas de hacerse daño); si es una calculadora, explica la fórmula en palabras, cómo usarla bien, ejemplos sencillos y sus límites; '
               'si es un ejercicio, explica cómo y cuándo practicarlo, qué se nota y precauciones. '
               'Formato JSON exacto: {"titulo": "título de la guía (máx. 70 caracteres)", "intro": "2 párrafos", "alt": "descripción de la imagen principal de la página (máx. 120 caracteres)", '
               '"secciones": [{"titulo": "...", "texto": "párrafos separados por saltos de línea; listas con líneas que empiezan por - "}] (entre 5 y 6 secciones), '
               '"faq": [{"p": "pregunta que la gente busca en Google", "r": "respuesta de 2 a 4 frases"}] (5 preguntas), '
               '"fuentes": ["organismos o documentos de referencia reales y generales, sin URL"] (3 o 4)}')
        if not valida(g): print('guía no válida', sitio, ruta); continue
        g['fecha'] = HOY; json.dump(g, open(fj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); nuevas += 1
    b = bloque(g, sitio, ruta)
    m = re.search(r'<div class="wrap"><aside class="firma"', fuente) or re.search(r'<footer', fuente)
    if not m: print('sin punto de inserción', sitio, ruta); continue
    nuevo = fuente[:m.start()] + b + fuente[m.start():]
    copia = f'www/{sitio}/eliminar/guias-{HOY}/{ruta}/index.html'
    r = remoto(f'mkdir -p "$(dirname {copia})" && cp -p {archivo} {copia} && cat > {archivo}.guia && mv {archivo}.guia {archivo} && echo OK', nuevo)
    if 'OK' in r: hechas += 1; print('guía puesta', sitio, ruta, len(texto_visible(nuevo).split()), 'palabras')
if hechas:
    for s in SITIOS: remoto(f'site-tools-client domain-all update id={s} flush_cache=1 >/dev/null 2>&1; true')
print(f'::notice title=Guías::{hechas} páginas con guía nueva ({nuevas} escritas por la IA hoy)')
