"""SEO automático con Search Console (solo lectura).

Cada día:
  1. Lee las búsquedas reales de los últimos 28 días (consulta y página) de todas las propiedades de AURZANE.
  2. Páginas con muchas impresiones y pocos clics para su posición: la IA reescribe título y descripción
     usando las palabras con las que la gente las busca.
       - Páginas estáticas: se cambian en el servidor (copia del original en www/<sitio>/eliminar/seo-FECHA/).
       - Universidades: se guardan en univ/data/gsc_titulos.json y el generador del portal las usa.
       - Páginas que se regeneran solas (tienda, biblioteca, artículos) no se tocan.
     Como mucho 4 páginas al día y cada página una vez cada 45 días; seo/cambios.json guarda el antes y el después
     para medir si mejoró.
  3. Búsquedas con impresiones donde AURZANE sale lejos (posición > 12): la IA propone temas de artículo que
     ai/manager.py escribe (seo/temas.json).
  4. Resumen para el panel de resultados (seo/resumen.json).
Entradas: SSH, SG_DEST, GEMINI_API_KEY (y GITHUB_TOKEN como respaldo de IA).
"""
import json, os, re, subprocess, datetime, urllib.request, urllib.parse, collections, html

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(R, 'seo')
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
HOY = datetime.date.today()
CTR_ESPERADO = {1: .28, 2: .15, 3: .10, 4: .07, 5: .05, 6: .04, 7: .03, 8: .025, 9: .02, 10: .018}
GENERADAS = re.compile(r'aurzane\.com/(libros|biblioteca|articulos|novedades|mapa|frases|marketing|ir|panel|colegios/contacto)/|/admin|portal\.html|mi-aurzane')


def remoto(orden, entrada=None, t=120):
    if not SSH or not DEST: return ''
    try: return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=t, input=entrada).stdout
    except Exception as e: print('remoto', e); return ''


def leer(n, d):
    try: return json.load(open(os.path.join(D, n), encoding='utf-8'))
    except Exception: return d


def guardar(n, v): json.dump(v, open(os.path.join(D, n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def pedir(url, datos=None, cab=None):
    cuerpo = json.dumps(datos).encode() if isinstance(datos, (dict, list)) else (urllib.parse.urlencode(datos).encode() if datos else None)
    h = dict(cab or {}); h.setdefault('Content-Type', 'application/json' if isinstance(datos, (dict, list)) else 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(urllib.request.Request(url, data=cuerpo, headers=h), timeout=60) as r: return json.load(r)


def ia(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    for m in ['gemini-flash-latest', 'gemini-flash-lite-latest']:
        if not k: break
        try:
            r = pedir(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}',
                      {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': .4, 'responseMimeType': 'application/json'}})
            return json.loads(''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts']))
        except Exception as e: print('gemini', m, str(e)[:120])
    g = os.environ.get('GITHUB_TOKEN', '').strip()
    if g:
        try:
            r = pedir('https://models.github.ai/inference/chat/completions', {'model': 'openai/gpt-4.1-mini', 'messages': [{'role': 'user', 'content': prompt + '\nResponde solo JSON.'}]},
                      {'Authorization': 'Bearer ' + g})
            t = r['choices'][0]['message']['content']; return json.loads(t[t.index('{') if '{' in t else t.index('['):].rstrip('`\n '))
        except Exception as e: print('github models', str(e)[:120])
    return None


# ---------------------------------------------------------------- acceso
app = json.loads(remoto('cat www/aurzane.com/privado-youtube/app.json 2>/dev/null') or '{}')
rt = remoto('cat www/aurzane.com/privado-youtube/refresh_gsc 2>/dev/null').strip()
if not app.get('client_id') or not rt:
    guardar('resumen.json', {'fecha': HOY.isoformat(), 'conectado': False, 'aviso': 'Search Console sin conectar: entra en aurzane.com/youtube/?cuenta=gsc y autoriza con tu cuenta de Google.'})
    print('::warning title=SEO::Search Console sin conectar (aurzane.com/youtube/?cuenta=gsc)'); raise SystemExit(0)
tk = pedir('https://oauth2.googleapis.com/token', {'client_id': app['client_id'], 'client_secret': app['client_secret'], 'refresh_token': rt, 'grant_type': 'refresh_token'})['access_token']
AUT = {'Authorization': 'Bearer ' + tk}
sitios = [s['siteUrl'] for s in pedir('https://www.googleapis.com/webmasters/v3/sites', cab=AUT).get('siteEntry', []) if s.get('permissionLevel') != 'siteUnverifiedUser' and 'aurzane' in s['siteUrl']]
# si existe la propiedad de dominio, cubre todos los subdominios: no se suman las demás para no duplicar
if any(s.startswith('sc-domain:') for s in sitios): sitios = [s for s in sitios if s.startswith('sc-domain:')]
ini, fin = (HOY - datetime.timedelta(days=30)).isoformat(), (HOY - datetime.timedelta(days=3)).isoformat()
filas = []
for s in sitios:
    inicio = 0
    while True:
        r = pedir('https://www.googleapis.com/webmasters/v3/sites/' + urllib.parse.quote(s, safe='') + '/searchAnalytics/query',
                  {'startDate': ini, 'endDate': fin, 'dimensions': ['query', 'page'], 'rowLimit': 25000, 'startRow': inicio}, AUT)
        lote = r.get('rows', []); filas += [{'q': x['keys'][0], 'p': x['keys'][1], 'c': x['clicks'], 'i': x['impressions'], 'pos': x['position']} for x in lote]
        if len(lote) < 25000: break
        inicio += 25000
print('sitios', sitios, 'filas', len(filas))

# ---------------------------------------------------------------- resumen
por_q = collections.defaultdict(lambda: [0, 0, 0.0]); por_p = collections.defaultdict(lambda: [0, 0, 0.0])
for f in filas:
    for k, dic in ((f['q'], por_q), (f['p'], por_p)):
        a = dic[k]; a[0] += f['c']; a[1] += f['i']; a[2] += f['pos'] * f['i']
pos = lambda a: round(a[2] / a[1], 1) if a[1] else None
res = {'fecha': HOY.isoformat(), 'conectado': True, 'periodo': [ini, fin], 'clics': sum(f['c'] for f in filas), 'impresiones': sum(f['i'] for f in filas),
       'consultas': [[q, a[0], a[1], pos(a)] for q, a in sorted(por_q.items(), key=lambda z: -z[1][1])[:30]],
       'paginas': [[p, a[0], a[1], pos(a)] for p, a in sorted(por_p.items(), key=lambda z: -z[1][0] * 1000 - z[1][1])[:30]]}

# países desde los que llegan las búsquedas
paises = []
for s_ in sitios:
    try:
        r = pedir('https://www.googleapis.com/webmasters/v3/sites/' + urllib.parse.quote(s_, safe='') + '/searchAnalytics/query',
                  {'startDate': ini, 'endDate': fin, 'dimensions': ['country'], 'rowLimit': 60}, AUT)
        paises += [[x['keys'][0].upper(), x['clicks'], x['impressions'], round(x['position'], 1)] for x in r.get('rows', [])]
    except Exception as e: print('paises', e)
res['paises'] = sorted(paises, key=lambda z: -z[2])[:30]

# ---------------------------------------------------------------- 2. títulos y descripciones
cambios = leer('cambios.json', [])
hace45 = (HOY - datetime.timedelta(days=45)).isoformat()
recientes = {c['url'] for c in cambios if c['fecha'] >= hace45}
cand = []
for p, a in por_p.items():
    if a[1] < 80 or p in recientes or GENERADAS.search(p) or '#' in p: continue
    ps = pos(a)
    if not ps or ps > 15: continue
    esperado = CTR_ESPERADO.get(max(1, round(ps)), .012)
    ctr = a[0] / a[1]
    if ctr < esperado * .6: cand.append((a[1] * (esperado - ctr), p, a, ps, ctr))
cand.sort(reverse=True)
univ_t = json.load(open(os.path.join(R, 'univ/data/gsc_titulos.json'), encoding='utf-8')) if os.path.exists(os.path.join(R, 'univ/data/gsc_titulos.json')) else {}
hechos = 0
for _, p, a, ps, ctr in cand[:10]:
    if hechos >= 4: break
    u = urllib.parse.urlparse(p); host = u.hostname or ''
    if not re.match(r'^([a-z0-9-]+\.)?aurzane\.com$', host): continue
    ruta = u.path if not u.path.endswith('/') else u.path + 'index.html'
    if '..' in ruta or not re.match(r'^/[A-Za-z0-9/_.\-]*\.html$', ruta): continue
    es_univ = host == 'nexus.aurzane.com' and ruta.startswith('/universidades/')
    archivo = f'www/{host}/public_html{ruta}'
    fuente = remoto(f'cat {archivo} 2>/dev/null')
    mt = re.search(r'<title>(.*?)</title>', fuente, re.S); md = re.search(r'<meta name="description" content="([^"]*)"', fuente)
    if not mt: continue
    t0, d0 = html.unescape(mt.group(1).strip()), html.unescape(md.group(1)) if md else ''
    qs = sorted(((q_, x) for (q_, x) in ((f['q'], f) for f in filas if f['p'] == p)), key=lambda z: -z[1]['i'])[:12]
    lista = '\n'.join(f'- «{q_}»: {x["i"]} impresiones, {x["c"]} clics, posición {x["pos"]:.1f}' for q_, x in qs)
    j = ia('Eres SEO de AURZANE, una web española de psicología, bienestar, educación y orientación vocacional. '
           f'Esta página sale en Google en la posición media {ps} con {a[1]} impresiones pero solo {a[0]} clics.\nURL: {p}\nTítulo actual: {t0}\nDescripción actual: {d0}\n'
           f'Búsquedas reales con las que aparece:\n{lista}\n\nEscribe un título nuevo (máximo 60 caracteres) y una descripción nueva (entre 120 y 155 caracteres) en español, '
           'que respondan a lo que busca la gente con esas palabras, sin prometer nada que la página no tenga, sin mayúsculas sostenidas, sin rayas largas ni emojis, '
           'manteniendo «| AURZANE» o el nombre de la marca solo si cabe. Responde JSON: {"titulo": "...", "descripcion": "...", "motivo": "una frase"}')
    if not j or not j.get('titulo') or not (20 <= len(j['titulo']) <= 70) or not (80 <= len(j.get('descripcion', '')) <= 170): continue
    t1, d1 = j['titulo'].replace('—', ',').strip(), j['descripcion'].replace('—', ',').strip()
    if es_univ:
        univ_t[p] = {'titulo': t1, 'desc': d1}
    else:
        nuevo = fuente.replace(mt.group(0), '<title>' + html.escape(t1, quote=False) + '</title>', 1)
        if md: nuevo = nuevo.replace(md.group(0), '<meta name="description" content="' + html.escape(d1) + '"', 1)
        nuevo = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + html.escape(t1) + m.group(2), nuevo, count=1)
        nuevo = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(d1) + m.group(2), nuevo, count=1)
        copia = f'www/{host}/eliminar/seo-{HOY.isoformat()}{ruta}'
        orden = f'mkdir -p "$(dirname {copia})" && cp -p {archivo} {copia} && cat > {archivo}.seo-nuevo && mv {archivo}.seo-nuevo {archivo} && echo OK'
        if 'OK' not in remoto(orden, nuevo): print('no se pudo escribir', p); continue
    cambios.append({'fecha': HOY.isoformat(), 'url': p, 'antes': {'titulo': t0, 'desc': d0, 'clics': a[0], 'impresiones': a[1], 'ctr': round(ctr, 4), 'posicion': ps},
                    'despues': {'titulo': t1, 'desc': d1}, 'motivo': str(j.get('motivo', ''))[:200], 'consultas': [q_ for q_, _ in qs[:5]], 'via': 'univ' if es_univ else 'servidor'})
    hechos += 1; print('SEO', p, '->', t1)
if hechos and any(c['via'] == 'servidor' for c in cambios[-hechos:]):
    for h_ in {urllib.parse.urlparse(c['url']).hostname for c in cambios[-hechos:]}: remoto(f'site-tools-client domain-all update id={h_} flush_cache=1 >/dev/null 2>&1; true')
json.dump(univ_t, open(os.path.join(R, 'univ/data/gsc_titulos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# evaluación: cómo les va a las páginas cambiadas hace más de 21 días
for c in cambios:
    if c['fecha'] <= (HOY - datetime.timedelta(days=21)).isoformat() and c['url'] in por_p:
        a = por_p[c['url']]; c['ahora'] = {'fecha': HOY.isoformat(), 'clics': a[0], 'impresiones': a[1], 'ctr': round(a[0] / a[1], 4) if a[1] else 0, 'posicion': pos(a)}
guardar('cambios.json', cambios[-300:])

# ---------------------------------------------------------------- 3. temas de artículo
temas = leer('temas.json', [])
ya = {t['consulta'] for t in temas}
lejos = [(q, a) for q, a in por_q.items() if a[1] >= 15 and (pos(a) or 99) > 12 and q not in ya and len(q.split()) >= 2][:40]
lejos.sort(key=lambda z: -z[1][1])
if lejos:
    j = ia('Eres editor de AURZANE (psicología, bienestar, aprendizaje, universidades y orientación vocacional, en español). Estas son búsquedas de Google con las que la web aparece '
           'pero lejos de las primeras posiciones:\n' + '\n'.join(f'- «{q}» ({a[1]} impresiones, posición {pos(a)})' for q, a in lejos[:25]) +
           '\n\nElige como mucho 5 que merezcan un artículo útil y riguroso (descarta las de marcas, nombres propios de personas, contenido adulto o temas sin relación) '
           'y escribe para cada una un título de artículo claro (máximo 80 caracteres) que responda a esa búsqueda. Asigna el mundo: mind (salud mental, emociones), live (hábitos, sueño, cuerpo), '
           'learn (estudio, aprendizaje), nexus (universidades, carreras, orientación vocacional) o build (trabajo, dinero, vivienda). Asigna el test relacionado si lo hay, de esta lista: '
           'ansiedad, depresion, autoestima, autocompasion, autoeficacia, burnout, estres, resiliencia, satisfaccion, soledad, tdah, personalidad, bienestar, habitos, sueno, vocacional; si ninguno encaja, "". '
           'Responde JSON: [{"consulta": "...", "titulo": "...", "mundo": "...", "test": "..."}]')
    for t in (j if isinstance(j, list) else []):
        if isinstance(t, dict) and t.get('consulta') in dict(lejos) and t.get('mundo') in ('mind', 'live', 'learn', 'nexus', 'build') and 15 <= len(t.get('titulo', '')) <= 100:
            temas.append({'consulta': t['consulta'], 'titulo': t['titulo'].replace('—', ','), 'mundo': t['mundo'], 'test': t.get('test') or '', 'fecha': HOY.isoformat()})
guardar('temas.json', temas[-200:])

res['cambios_titulos'] = [[c['fecha'], c['url'], c['antes']['titulo'], c['despues']['titulo'], (c.get('ahora') or {}).get('ctr'), c['antes']['ctr']] for c in cambios[-15:]][::-1]
res['temas_nuevos'] = [[t['fecha'], t['consulta'], t['titulo']] for t in temas[-10:]][::-1]
guardar('resumen.json', res)
print(f'::notice title=SEO::{len(filas)} filas · {hechos} títulos mejorados · {len(temas)} temas en cola')
