"""Guías de lectura automáticas para las fichas de libros con derechos (17/11/2026, plan de la auditoría final, punto 2).
Las 39 fichas con guía (de qué trata, ideas clave, para quién, lectura desde la psicología y preguntas) son las que más
clics traen de Google; las otras ~537 solo tenían una frase. Cada día se escriben guías nuevas para unas pocas fichas,
empezando por las que más aparecen en Google (seo/resumen.json), con la IA y con estas condiciones:
- Solo si la IA conoce el libro (si no, lo dice y se salta). Resumen propio: nunca citas ni texto del libro.
- Misma maqueta que las guías escritas a mano; firma «Resumen propio de AURZANE, elaborado con ayuda de IA».
- El título pasa de «ficha del libro» a «resumen e ideas clave».
Las guías se guardan en biblioteca/guias_auto.json y se vuelven a poner solas si un despliegue rehace la página.
Copia previa de cada página en www/aurzane.com/eliminar/guias-FECHA/. Entradas: GEMINI_API_KEY, GITHUB_TOKEN, SSH, SG_DEST."""
import json, os, re, sys, html, time, subprocess, datetime, urllib.request, urllib.error
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', 'ai')); from ia_respaldo import generar as _respaldo   # IA de respaldo común
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'biblioteca', 'guias_auto.json')
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
POR_DIA = int(os.environ.get('GUIAS_DIA', '4'))
HOY = datetime.date.today().isoformat()
DIR = 'www/aurzane.com/public_html/biblioteca/libro'
E = lambda t: html.escape(str(t), quote=False)


def remoto(orden, entrada=None):
    r = subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=180, input=entrada)
    return r.stdout


def post(url, datos, cab):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, json.dumps(datos).encode(), cab), timeout=120) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        try: cuerpo = e.read().decode()[:160]
        except Exception: cuerpo = ''
        print('IA', e.code, cuerpo); return None
    except Exception as e: print('IA', str(e)[:100]); return None


def ia(prompt):
    k = os.environ.get('GEMINI_API_KEY', '')
    for m in ('gemini-flash-latest', 'gemini-flash-lite-latest'):
        if not k: break
        j = post(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}',
                 {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.3, 'responseMimeType': 'application/json'}}, {'Content-Type': 'application/json'})
        try: return json.loads(j['candidates'][0]['content']['parts'][0]['text'])
        except Exception: pass
    t = _respaldo(prompt, json_mode=True)
    try: return json.loads(t[min([i for i in (t.find('{'), t.find('[')) if i >= 0]):]) if t else None
    except Exception as e: print('respaldo IA', str(e)[:90]); return None


def bloque(titulo, g):
    est = ("<style>.guia h2{font-family:'Bodoni Moda',Georgia,serif;font-size:1.6rem;margin:0 0 10px}.guia h3{font-size:1.12rem;margin:26px 0 8px}.guia p,.guia li{line-height:1.7;font-size:1.02rem}"
           ".guia ul{padding-left:20px}.guia li{margin:6px 0}.guia .psico{background:rgba(201,162,75,.12);border:1px solid rgba(201,162,75,.35);border-radius:14px;padding:16px 18px;margin-top:22px}"
           ".guia details{border-bottom:1px solid rgba(0,0,0,.12);padding:12px 0}.guia summary{cursor:pointer;font-weight:600}.guia .firma{font-size:.88rem;opacity:.75;margin-top:18px}</style>")
    return (f'\n  <section class="bloque guia guia-auto" aria-labelledby="t-guia" style="max-width:780px">\n    {est}\n    <h2 id="t-guia">Resumen de {E(titulo)}</h2>\n'
            f'    <h3>De qué trata</h3><p>{E(g["trata"])}</p>\n    <h3>Ideas clave</h3><ul>{"".join("<li>" + E(x) + "</li>" for x in g["ideas"])}</ul>\n'
            f'    <h3>Para quién es</h3><p>{E(g["para"])}</p>\n    <div class="psico"><h3 style="margin-top:0">Lectura desde la psicología</h3><p>{E(g["psico"])}</p></div>\n'
            f'    <h3>Preguntas frecuentes</h3>{"".join("<details><summary>" + E(q) + "</summary><p>" + E(a) + "</p></details>" for q, a in g["faq"])}\n'
            '    <p class="firma">Resumen propio de AURZANE, elaborado con ayuda de IA. No reproduce texto del libro.</p>\n  </section>')


def poner(pagina, titulo, g):
    """Mete la guía tras la ficha y cambia el título. Devuelve el HTML nuevo o '' si no hace falta."""
    if 'class="bloque guia' in pagina or '</article>' not in pagina: return ''
    i = pagina.index('</article>'); i = pagina.index('</div>', i) + len('</div>')   # cierre del contenedor de la ficha
    n = pagina[:i] + bloque(titulo, g) + pagina[i:]
    n = re.sub(r'(<title>[^<]*?)(?::\s*)?ficha del libro', r'\1: resumen e ideas clave', n, count=1)
    n = re.sub(r'(<meta property="og:title" content="[^"]*?)(?::\s*)?ficha del libro', r'\1: resumen e ideas clave', n, count=1)
    return n


guias = json.load(open(F, encoding='utf-8')) if os.path.exists(F) else {}
# 1) fichas que aún no tienen guía, en orden de impresiones en Google
sin = remoto(f'cd {DIR} && grep -L "class=\\"bloque guia" ref-*.html').split()
imp = {}
try:
    for u, c, i, *_ in json.load(open(os.path.join(R, 'seo', 'resumen.json'), encoding='utf-8')).get('paginas', []):
        m = re.search(r'ref-[a-z0-9-]+', u)
        if m: imp[m.group(0) + '.html'] = imp.get(m.group(0) + '.html', 0) + i
except Exception as e: print('seo', e)
sin.sort(key=lambda f: (-imp.get(f, 0), f))
print('fichas sin guía:', len(sin), '| guías guardadas:', len(guias))
# 2) volver a poner las guías guardadas que un despliegue haya quitado
pend = [f for f in sin if f in guias]
nuevas = 0
for f in [f for f in sin if f not in guias]:
    if nuevas >= POR_DIA: break
    time.sleep(6)   # sin pisar el cupo por minuto de la IA
    p = remoto(f'cat {DIR}/{f}')
    t = re.search(r'<h1>(.*?)</h1>', p); a = re.search(r'<p class="autores">(.*?)</p>', p); rs = re.search(r'<p class="resumen">(.*?)</p>', p)
    if not t: continue
    titulo, autor, res = html.unescape(t.group(1)), html.unescape(a.group(1)) if a else '', html.unescape(rs.group(1)) if rs else ''
    g = ia('Eres psicólogo clínico y escribes guías de lectura para AURZANE, una web española de psicología. '
           f'Libro: «{titulo}», de {autor}. Nota de la ficha: {res}\n'
           'Si no conoces bien este libro concreto, responde solo {"conozco": false}. Si lo conoces, escribe en español de España, con tus palabras, '
           'sin citas literales, sin rayas largas y sin inventar datos (ni fechas, ni cifras, ni capítulos que no conozcas con seguridad). Responde JSON: '
           '{"conozco": true, "trata": "un párrafo de 70 a 110 palabras sobre de qué trata", "ideas": ["5 ideas clave, una frase cada una"], '
           '"para": "un párrafo de 30 a 60 palabras sobre para quién es", "psico": "un párrafo de 60 a 100 palabras con una lectura crítica desde la psicología basada en la evidencia", '
           '"faq": [["pregunta frecuente", "respuesta de 25 a 60 palabras"], ["…", "…"], ["…", "…"]]}')
    ok = (isinstance(g, dict) and g.get('conozco') and isinstance(g.get('ideas'), list) and 4 <= len(g['ideas']) <= 7 and isinstance(g.get('faq'), list) and len(g['faq']) >= 3
          and all(isinstance(x, list) and len(x) == 2 for x in g['faq']) and 300 <= len(g.get('trata', '')) <= 1100 and g.get('para') and g.get('psico'))
    if g is None: print('IA sin respuesta (cupo o caída): se reintenta otro día'); break
    if isinstance(g, dict) and g.get('conozco') is False: print('la IA no conoce el libro, se salta:', titulo); guias[f] = {'saltar': True, 'fecha': HOY}; continue
    if not ok: print('respuesta no válida, se reintenta otro día:', titulo); continue
    g = {k: (v.replace('—', ',') if isinstance(v, str) else v) for k, v in g.items()}
    guias[f] = {'titulo': titulo, 'fecha': HOY, **{k: g[k] for k in ('trata', 'ideas', 'para', 'psico')}, 'faq': g['faq'][:4]}
    pend.append(f); nuevas += 1
puestas = 0
for f in pend:
    g = guias[f]
    if g.get('saltar'): continue
    p = remoto(f'cat {DIR}/{f}')
    n = poner(p, g['titulo'], g)
    if not n: continue
    r = remoto(f'mkdir -p www/aurzane.com/eliminar/guias-{HOY} && cp -p {DIR}/{f} www/aurzane.com/eliminar/guias-{HOY}/{f} && cat > {DIR}/{f}.g && mv {DIR}/{f}.g {DIR}/{f} && echo OK', n)
    if 'OK' in r: puestas += 1; print('guía puesta:', g['titulo'])
json.dump(guias, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if puestas: remoto('site-tools-client domain-all update id=aurzane.com flush_cache=1 >/dev/null 2>&1; true')
print(f'::notice title=Guías de libros::{nuevas} guías nuevas, {puestas} puestas en la web, {len([1 for g in guias.values() if not g.get("saltar")])} en total')
