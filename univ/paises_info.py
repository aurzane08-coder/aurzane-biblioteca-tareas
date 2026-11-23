"""Datos básicos de cada país para «Estudiar en [país]» (17/11/2026, plan de la auditoría final, punto 44).
Fuente: REST Countries (datos abiertos): idiomas oficiales, moneda, capital y población. Se guarda en
univ/data/paises_info.json {iso: {...}} en cada publicación; si la fuente falla, la página sale sin esos datos."""
import json, os, sys, time, urllib.request
D = sys.argv[1] if len(sys.argv) > 1 else 'univ/data'
F = os.path.join(D, 'paises_info.json')
try:
    with urllib.request.urlopen(urllib.request.Request('https://restcountries.com/v3.1/all?fields=cca2,languages,currencies,capital,population,translations',
                                                       headers={'User-Agent': 'AURZANE-NEXUS/1.0'}), timeout=60) as r: datos = json.load(r)
except Exception as e: datos = {'message': str(e)}
if isinstance(datos, dict):   # REST Countries a veces responde con un error en JSON: se usa la copia abierta de mledoze/countries (sin población)
    print('::warning::REST Countries no da la lista:', str(datos)[:200])
    try:
        with urllib.request.urlopen('https://raw.githubusercontent.com/mledoze/countries/master/countries.json', timeout=60) as r: datos = json.load(r)
    except Exception as e: print('::warning::Copia de respaldo tampoco responde:', e); sys.exit(0)
ES_IDIOMA = {'Spanish': 'español', 'English': 'inglés', 'Portuguese': 'portugués', 'French': 'francés', 'German': 'alemán', 'Italian': 'italiano', 'Dutch': 'neerlandés',
             'Polish': 'polaco', 'Swedish': 'sueco', 'Norwegian': 'noruego', 'Danish': 'danés', 'Finnish': 'finés', 'Russian': 'ruso', 'Chinese': 'chino', 'Japanese': 'japonés',
             'Korean': 'coreano', 'Arabic': 'árabe', 'Hebrew': 'hebreo', 'Turkish': 'turco', 'Greek': 'griego', 'Czech': 'checo', 'Hungarian': 'húngaro', 'Romanian': 'rumano',
             'Catalan': 'catalán', 'Galician': 'gallego', 'Basque': 'euskera', 'Irish': 'irlandés', 'Hindi': 'hindi', 'Quechua': 'quechua', 'Aymara': 'aimara', 'Guaraní': 'guaraní',
             'Swiss German': 'alemán suizo', 'Afrikaans': 'afrikáans', 'Zulu': 'zulú', 'Malay': 'malayo', 'Indonesian': 'indonesio', 'Thai': 'tailandés', 'Vietnamese': 'vietnamita'}
out = {}
for x in datos:
    if not isinstance(x, dict): continue
    iso = (x.get('cca2') or '').lower()
    if not iso: continue
    idi = [ES_IDIOMA.get(v, v) for v in (x.get('languages') or {}).values()][:4]
    mon = [f"{v.get('name', '')} ({v.get('symbol', '')})".replace(' ()', '') for v in (x.get('currencies') or {}).values()][:2]
    out[iso] = {'idiomas': idi, 'moneda': mon, 'capital': (x.get('capital') or [''])[0], 'poblacion': x.get('population') or 0}
if len(out) < 150: print('::warning::Respuesta incompleta de REST Countries'); sys.exit(0)
json.dump(out, open(F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('paises_info:', len(out), 'países')
