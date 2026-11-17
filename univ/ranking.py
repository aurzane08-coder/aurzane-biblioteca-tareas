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


# 1) todas las instituciones educativas de OpenAlex, desde su copia pública completa (S3, sin clave ni límite diario;
#    la API pide clave desde 2026). Cada institución está en la partición de su última actualización.
import gzip as _gz, io, xml.etree.ElementTree as ET
S3 = 'https://openalex.s3.amazonaws.com/'
claves, token = [], None
while True:
    q = 'list-type=2&prefix=data/jsonl/institutions/' + ('&continuation-token=' + urllib.parse.quote(token) if token else '')
    with urllib.request.urlopen(S3 + '?' + q, timeout=120) as r:
        x = ET.fromstring(r.read())
    ns = {'s': x.tag.split('}')[0].strip('{')}
    claves += [k.text for k in x.findall('s:Contents/s:Key', ns) if k.text.endswith('.gz')]
    t = x.find('s:NextContinuationToken', ns)
    if t is None: break
    token = t.text
claves.sort()   # por fecha de partición: la versión más reciente de cada institución gana
print('OpenAlex:', len(claves), 'archivos')
por_id = {}
for k in claves:
    for i in range(4):
        try:
            with urllib.request.urlopen(S3 + k, timeout=300) as r:
                datos = r.read(); break
        except Exception as e:
            print('reintento', k, str(e)[:60]); time.sleep(5 * (i + 1))
    else:
        raise SystemExit('No se pudo descargar ' + k + ': se deja el ranking anterior')
    for ln in _gz.GzipFile(fileobj=io.BytesIO(datos)):
        try: o = json.loads(ln)
        except Exception: continue
        if o.get('type') != 'education': por_id.pop(o.get('id'), None); continue
        por_id[o['id']] = {c: o.get(c) for c in ('id', 'display_name', 'display_name_alternatives', 'homepage_url', 'country_code', 'works_count', 'cited_by_count', 'summary_stats')}
inst = list(por_id.values())
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
