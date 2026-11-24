"""En qué idioma se imparte cada grado oficial de España (24/11/2026), para «Study in Spain» (NEXUS en inglés).
Fuente: RUCT del Ministerio. Cada título tiene su memoria verificada; en «Universidades y centros» cada centro declara
«Idiomas en los que se imparte» (CASTELLANO, INGLÉS, CATALÁN, EUSKERA, GALLEGO, VALENCIANO…).
Recorrido por grado: ficha del estudio → última solicitud (memoria) → centros → datos de cada centro.
Salida: univ/data/idiomas_grados.json  {codigo: {"idiomas": [...], "centros": {codCentro: [...]}, "fecha": "AAAA-MM-DD"}}
Es reanudable: guarda cada 50 grados y se detiene a los MINUTOS indicados; la acción lo vuelve a lanzar hasta terminar.
Los grados ya mirados se vuelven a mirar pasados 120 días (las memorias cambian poco)."""
import json, os, re, sys, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ruct

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SAL = os.path.join(D, 'idiomas_grados.json')
MINUTOS = float(os.environ.get('MINUTOS') or 300)
HOY = datetime.date.today()
W = 'https://www.educacion.gob.es'

grados = []
for cu, u in json.load(open(os.path.join(D, 'ruct.json'), encoding='utf-8'))['universidades'].items():
    for g in u['grados']:
        if g.get('codigo') and g.get('url'): grados.append((g['codigo'], g['url']))
grados = list(dict.fromkeys(grados))
hecho = json.load(open(SAL, encoding='utf-8')) if os.path.exists(SAL) else {}


def vigente(x):
    try: return (HOY - datetime.date.fromisoformat(x.get('fecha', '2000-01-01'))).days < 120
    except Exception: return False


def idiomas_de(url):
    est = ruct.get(ruct.B + url)
    cods = re.findall(r'solicitud/detalles\.action\?cod=(\d+)', est) or re.findall(r'[?&]cod=(\d{14,})', est)
    if not cods: return None
    cod = max(cods)   # la memoria más reciente (el código acaba en la fecha)
    ruct.get(ruct.B + 'solicitud/detalles.action?cod=' + cod + '&sit=A&actual=menu.solicitud.basicos')   # abre la memoria en la sesión
    p = ruct.get(W + '/ruct/solicitud/universidades?actual=menu.solicitud.universidades&cod=' + cod)
    centros = {}
    for l in dict.fromkeys(re.findall(r'href="(/ruct/solicitud/datosCentro!consulta\.action\?[^"]+)"', p)):
        l = l.replace('&amp;', '&')
        cc = (re.search(r'codCentro=(\d+)', l) or [None, ''])[1]
        t = ruct.limpio(ruct.get(W + l))
        m = re.search(r'Idiomas en los que se imparte:\s*Denominaci[óo]n\s*(.*?)\s*©', t)
        centros[cc] = sorted({x.strip().upper() for x in re.split(r'\s{1,}(?=[A-ZÁÉÍÓÚÑ]{4,})', m.group(1)) if x.strip()}) if m else []
    return {'cod_memoria': cod, 'centros': centros, 'idiomas': sorted({i for v in centros.values() for i in v})}


ini, n = time.time(), 0
pend = [(c, u) for c, u in grados if not (c in hecho and vigente(hecho[c]))]
print(f'Grados: {len(grados)}; por mirar: {len(pend)}', flush=True)
for c, u in pend:
    if (time.time() - ini) / 60 > MINUTOS: break
    try: r = idiomas_de(u)
    except Exception as e: print('  error', c, e); r = None
    hecho[c] = dict(r or {'idiomas': [], 'centros': {}}, fecha=str(HOY), **({} if r else {'sin_memoria': True}))
    n += 1
    if n % 50 == 0:
        json.dump(hecho, open(SAL, 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True)
        print(f'  {n} mirados ({len(pend) - n} quedan)', flush=True)
json.dump(hecho, open(SAL, 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True)
quedan = len(pend) - n
ingles = sum(1 for v in hecho.values() if 'INGLÉS' in v.get('idiomas', []))
print(f'Mirados hoy: {n}. Quedan: {quedan}. Grados con docencia en inglés hasta ahora: {ingles}')
open(os.environ.get('GITHUB_OUTPUT', os.devnull), 'a').write(f'quedan={quedan}\n')
