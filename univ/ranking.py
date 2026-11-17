"""Ranking mundial de investigación para todas las universidades del catálogo (17/11/2026, etapa 3, tarea 40).
Fuente: OpenAlex (datos abiertos CC0, https://openalex.org), que recoge la producción científica de todas las
instituciones del mundo. Para cada universidad del catálogo se busca su ficha en OpenAlex por el dominio de su web
(y, si no, por el nombre dentro del mismo país) y se guardan: publicaciones, citas, índice h y la posición mundial
por citas entre todas las instituciones educativas de OpenAlex. No es un ranking comercial (QS, THE): es una medida
abierta y reproducible de impacto científico, y así se explica en la web.
Salida: univ/data/ranking.json  {"dom": {dominio: [pos, pos_pais, h, pub, citas, oa]}, "nom": {"iso|nombre": [...]}}
Uso: python3 univ/ranking.py univ/data   (lo corre cada mes .github/workflows/univ-ranking.yml)"""
import json, gzip, os, sys, time, re, unicodedata, urllib.request, urllib.parse
D = sys.argv[1] if len(sys.argv) > 1 else 'univ/data'
API = 'https://api.openalex.org/institutions'
CORREO = 'hola@aurzane.com'   # «polite pool» de OpenAlex


def pedir(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'AURZANE-NEXUS/1.0 (mailto:' + CORREO + ')'}), timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print('reintento', i + 1, str(e)[:80]); time.sleep(3 * (i + 1))
    raise SystemExit('OpenAlex no responde: se deja el ranking anterior')


def dominio(u):
    if not u: return ''
    h = urllib.parse.urlparse(u if '//' in u else 'http://' + u).netloc.lower().split(':')[0]
    h = re.sub(r'^(www\d?|web|portal|en|es)\.', '', h)
    return h


def norm(t):
    t = unicodedata.normalize('NFD', (t or '').lower()); t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', t).strip()


# 1) todas las instituciones educativas de OpenAlex (unas 25.000), con cursor
inst, cur, n = [], '*', 0
campos = 'id,display_name,display_name_alternatives,homepage_url,country_code,works_count,cited_by_count,summary_stats,type'
while cur:
    j = pedir(f'{API}?filter=type:education&per_page=200&select={campos}&cursor={urllib.parse.quote(cur)}&mailto={CORREO}')
    inst += j['results']; cur = j['meta'].get('next_cursor'); n += 1
    if n % 25 == 0: print(n, 'páginas,', len(inst), 'instituciones')
    time.sleep(0.15)
print('OpenAlex:', len(inst), 'instituciones educativas')
if len(inst) < 5000: raise SystemExit('Respuesta incompleta de OpenAlex: se deja el ranking anterior')
inst.sort(key=lambda x: -(x.get('cited_by_count') or 0))
pos, por_pais, pos_pais = {}, {}, {}
for i, x in enumerate(inst):
    pos[x['id']] = i + 1
    c = x.get('country_code') or ''
    por_pais[c] = por_pais.get(c, 0) + 1; pos_pais[x['id']] = por_pais[c]
dom, nom = {}, {}
for x in inst:
    if not x.get('works_count'): continue
    ss = x.get('summary_stats') or {}
    r = [pos[x['id']], pos_pais[x['id']], ss.get('h_index'), x.get('works_count'), x.get('cited_by_count'), x['id'].rsplit('/', 1)[-1]]
    d = dominio(x.get('homepage_url'))
    if d: dom.setdefault(d, r)
    for nm in [x.get('display_name')] + (x.get('display_name_alternatives') or []):
        nom.setdefault((x.get('country_code') or '').lower() + '|' + norm(nm), r)
# gen.py busca cada universidad por el dominio de su web y, si no, por país + nombre (univ/gen/gen.py: rank_de)
U = json.load(gzip.open(os.path.join(D, 'sb_universidades.json.gz')))
casan = sum(1 for u in U if dominio(u.get('sitio_web')) in dom)
print(f'Catálogo: {len(U)} universidades de Supabase; {casan} casan por web (más las del RUCT y las principales, que se buscan al generar)')
if casan < 1000: raise SystemExit('Muy pocas coincidencias: se deja el ranking anterior')
out = {'_fuente': 'OpenAlex (CC0)', '_fecha': time.strftime('%Y-%m-%d'), '_total': len(inst), '_campos': ['pos', 'pos_pais', 'h', 'publicaciones', 'citas', 'openalex'],
       'dom': dom, 'nom': nom}
json.dump(out, open(os.path.join(D, 'ranking.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('ranking.json:', len(dom), 'dominios,', len(nom), 'nombres')
