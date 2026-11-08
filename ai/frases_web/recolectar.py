# -*- coding: utf-8 -*-
"""Recolector de frases célebres para AURZANE (gratis, en GitHub Actions).
Lee con calma (una página cada pocos segundos) las temáticas de Proverbia.net que encajan con la psicología y el bienestar,
respetando su robots.txt. Solo guarda frases de autores en dominio público (fallecidos hace más de 80 años, como pide la ley
española para autores muertos antes de 1987) y refranes o proverbios tradicionales, siempre citando autor y fuente.
Todas quedan listas (ok) sin revisión y AURZANE AI las publica en aurzane.com/frases/, en «Hoy en AURZANE» y en las redes.
Salida: ai/frases_web.json"""
import json, os, re, time, html, hashlib, datetime, socket, urllib.request, urllib.robotparser
socket.setdefaulttimeout(40)

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(D, 'frases_web.json')
UA = 'Mozilla/5.0 (compatible; AurzaneFrases/1.0; +https://aurzane.com/frases/)'
ANIO = datetime.date.today().year
LIMITE_MUERTE = ANIO - 81            # muerto en ese año o antes: dominio público en España
TEMAS = ['esperanza', 'adversidad', 'perseverancia', 'tolerancia', 'felicidad', 'amistad', 'amor', 'vida', 'tiempo', 'miedo',
         'valor', 'paciencia', 'sabiduria', 'alegria', 'soledad', 'animo', 'exito', 'fracaso', 'dolor', 'bondad', 'gratitud',
         'calma', 'conocimiento', 'esfuerzo', 'humildad', 'optimismo', 'superacion', 'mente', 'pensamiento', 'carácter',
         'educacion', 'confianza', 'serenidad', 'tristeza', 'libertad', 'naturaleza', 'trabajo', 'perdon', 'voluntad', 'verdad']
POR_VEZ = int(os.environ.get('PAGINAS', '14'))

def bajar(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'es-ES,es;q=0.9'})
    with urllib.request.urlopen(req, timeout=40) as r: return r.status, r.read().decode('utf-8', 'ignore')

robots = urllib.robotparser.RobotFileParser('https://proverbia.net/robots.txt')
try: robots.read()
except Exception: pass
def permitido(u):
    try: return robots.can_fetch(UA, u)
    except Exception: return False

def limpiar(t): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()

def extraer(pagina, url, tema):
    out = []
    for b in re.findall(r'<blockquote class="bsquote">(.*?)</blockquote>', pagina, re.S):
        p = re.search(r'<p>(.*?)</p>', b, re.S); a = re.search(r'<footer>\s*<a[^>]*>(.*?)</a>', b, re.S)
        vida = re.search(r'<em>\s*\((\d{3,4})\s*-\s*(\d{3,4})\)\s*(.*?)</em>', b, re.S)
        if not p: continue
        texto = limpiar(p.group(1)); autor = limpiar(a.group(1)) if a else ''
        tradicional = bool(re.search(r'^(Proverbio|Refrán)', autor, re.I))
        if not tradicional:
            if not vida or int(vida.group(2)) > LIMITE_MUERTE: continue   # vivo, sin fechas o fallecido hace poco: no se usa
        if not (25 <= len(texto) <= 230) or texto.count('"') > 2: continue
        out.append({'id': 'fw-' + hashlib.md5(texto.lower().encode()).hexdigest()[:10], 'texto': texto, 'autor': autor,
                    'vida': f'{vida.group(1)}-{vida.group(2)}' if vida else '', 'descripcion': limpiar(vida.group(3)) if vida else '',
                    'tema': (re.search(r'href="/frases-de-([a-z0-9-]+)"', b) or [None, tema])[1], 'fuente': 'Proverbia.net', 'url_fuente': url, 'recogida': datetime.date.today().isoformat()})
    return out

def gemini(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if not k: return ''
    cuerpo = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0, 'maxOutputTokens': 4096}}).encode()
    for m in ('gemini-flash-lite-latest', 'gemini-flash-latest'):
        try:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', data=cuerpo,
                                         headers={'Content-Type': 'application/json', 'x-goog-api-key': k})
            r = json.loads(urllib.request.urlopen(req, timeout=60).read())
            t = ''.join(x.get('text', '') for x in r['candidates'][0]['content'].get('parts', []))
            if t.strip(): return t
        except Exception as e: print('gemini', m, str(e)[:120]); time.sleep(4)
    return ''

datos = json.load(open(DEST, encoding='utf-8')) if os.path.exists(DEST) else []
vistos = {x['id'] for x in datos}
estado = json.load(open(DEST + '.estado', encoding='utf-8')) if os.path.exists(DEST + '.estado') else {'i': 0}
nuevas = []
paginas = ['https://proverbia.net/frase-del-dia']
N_TEMAS = 4
for k in range(N_TEMAS):
    paginas.append('https://proverbia.net/frases-de-' + TEMAS[(estado['i'] + k) % len(TEMAS)].replace('á', 'a').replace('ó', 'o').replace('ú', 'u'))
estado['i'] = (estado['i'] + N_TEMAS) % len(TEMAS)
# además, autor por autor: se recorre el índice de autores (46 páginas) y se visitan sus páginas poco a poco
estado.setdefault('cola', []); estado.setdefault('autores_vistos', []); estado.setdefault('pag_autores', 1)
if len(estado['cola']) < POR_VEZ:
    u_ix = 'https://proverbia.net/autores' + (f'?page={estado["pag_autores"]}' if estado['pag_autores'] > 1 else '')
    if permitido(u_ix):
        try:
            _, ix = bajar(u_ix); time.sleep(4)
            nuevos_a = [a for a in dict.fromkeys(re.findall(r'href="(/autor/frases-de-[^"]+)"', ix)) if a not in estado['autores_vistos']]
            estado['cola'] += nuevos_a; estado['pag_autores'] = estado['pag_autores'] % 46 + 1
        except Exception as e: print('índice de autores', str(e)[:100])
for a in estado['cola'][:max(0, POR_VEZ - N_TEMAS - 1)]:
    paginas.append('https://proverbia.net' + a); estado['autores_vistos'].append(a)
estado['cola'] = estado['cola'][max(0, POR_VEZ - N_TEMAS - 1):]
estado['autores_vistos'] = estado['autores_vistos'][-5000:]
for u in paginas:
    if not permitido(u): print('robots.txt no lo permite:', u); continue
    try:
        st, pag = bajar(u)
        tema = 'autor' if '/autor/' in u else u.rsplit('frases-de-', 1)[-1] if 'frases-de-' in u else 'frase del día'
        fr = [f for f in extraer(pag, u, tema) if f['id'] not in vistos]
        for f in fr: vistos.add(f['id']); nuevas.append(f)
        print(f'{st} {u}: {len(fr)} frases nuevas de dominio público')
    except Exception as e: print('no se pudo leer', u, str(e)[:100])
    time.sleep(5)

# frases de autores en dominio público y refranes: entran todas sin revisión (decisión de Adrián, 8-11-2026)
for f in nuevas: f['ok'] = True
datos.extend(nuevas)
for f in datos: f['ok'] = True
json.dump(datos, open(DEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(estado, open(DEST + '.estado', 'w', encoding='utf-8'))
print(f'::notice title=Frases::{len(nuevas)} nuevas, {sum(1 for f in datos if f.get("ok"))} listas en total, {sum(1 for f in datos if f.get("publicada"))} ya publicadas')
