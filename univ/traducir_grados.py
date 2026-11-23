# -*- coding: utf-8 -*-
"""Traduce al inglés los nombres oficiales de los grados españoles para «Study in Spain» (23/11/2026).

Lee univ/data/grados_en_pendientes.json (lo deja univ/gen/en.py) y guarda en univ/data/grados_en.json {nombre oficial: inglés}.
Cada nombre se traduce una sola vez y queda guardado. La IA traduce por lotes con un glosario fijo y reglas de estilo;
cada respuesta se comprueba antes de guardarla (forma «Bachelor's Degree in …», sin restos en español, longitud razonable).
Lo que no pasa la comprobación se queda pendiente y la página muestra el nombre oficial en español.
Uso: python3 univ/traducir_grados.py [máximo de nombres por pasada]"""
import os, re, sys, json, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, 'data')
F_TRAD, F_PEND = os.path.join(DATOS, 'grados_en.json'), os.path.join(DATOS, 'grados_en_pendientes.json')
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
LOTE = 40

GLOSARIO = '''Grado en / Graduado o Graduada en → Bachelor's Degree in
Doble Grado en / Programa Conjunto de Estudios Oficiales en → Double Bachelor's Degree in
Administración y Dirección de Empresas → Business Administration and Management
Ingeniería Informática → Computer Engineering
Ingeniería de Tecnologías de Telecomunicación → Telecommunication Technologies Engineering
Ingeniería en Tecnologías Industriales → Industrial Technologies Engineering
Maestro / Maestra en Educación Primaria → Primary Education Teaching
Maestro / Maestra en Educación Infantil → Early Childhood Education Teaching
Educación Social → Social Education
Trabajo Social → Social Work
Derecho → Law
Medicina → Medicine
Enfermería → Nursing
Fisioterapia → Physiotherapy
Odontología → Dentistry
Farmacia → Pharmacy
Psicología → Psychology
Periodismo → Journalism
Comunicación Audiovisual → Audiovisual Communication
Publicidad y Relaciones Públicas → Advertising and Public Relations
Ciencias de la Actividad Física y del Deporte → Physical Activity and Sports Sciences
Turismo → Tourism
Bellas Artes → Fine Arts
Estudios Ingleses → English Studies
Filología Hispánica / Lengua y Literatura Españolas → Spanish Language and Literature
Traducción e Interpretación → Translation and Interpreting
Relaciones Laborales y Recursos Humanos → Labour Relations and Human Resources
Gestión y Administración Pública → Public Management and Administration
Criminología → Criminology
Veterinaria → Veterinary Medicine
Arquitectura → Architecture
Fundamentos de la Arquitectura → Fundamentals of Architecture'''

PROMPT = '''You translate official names of Spanish university bachelor's degrees into British English for an international student audience.
Rules:
- Use the standard English name used by Spanish universities on their English websites, not a word-for-word rendering.
- The names come without the word "Grado": translate only the subject (for example "Administración y Dirección de Empresas" becomes "Business Administration and Management"). Never add "Bachelor's Degree in" or "Bachelor in".
- If the name already contains an official English version after a slash or a dash, use that English version without the "Bachelor in" prefix.
- Keep proper names, place names and institution names as they are (for example "Universidad de Salamanca", "Canarias" stays "Canary Islands" only when it is a region).
- Keep words like "mención", "itinerario" or bilingual markers translated naturally ("with a specialisation in", "bilingual").
- Use sentence-style title case like the examples, British spelling (specialisation, programme, labour).
- Never add information that is not in the original name.
Glossary (follow it exactly):
{glosario}
Answer ONLY with a JSON object mapping each original name to its English name, with the same keys, nothing else.
Names:
{nombres}'''


def gemini(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if not k: return ''
    cab = {'Content-Type': 'application/json', 'x-goog-api-key': k}
    try:
        req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200', headers=cab)
        ns = [m['name'].split('/')[-1] for m in json.load(urllib.request.urlopen(req, timeout=40)).get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
    except Exception as e:
        print('Gemini: no pude listar modelos:', e); return ''
    vers = sorted([n for n in ns if re.match(r'^gemini-\d[\d.]*-(flash|pro)$', n)], key=lambda n: ('flash' in n, [-int(x) for x in re.findall(r'\d+', n)]))
    modelos = [n for n in ('gemini-flash-latest',) if n in ns] + vers[:3]
    cuerpo = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0, 'maxOutputTokens': 8192, 'responseMimeType': 'application/json'}}).encode()
    for m in modelos:
        try:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', data=cuerpo, headers=cab, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=120))
            return ''.join(x.get('text', '') for x in r['candidates'][0]['content'].get('parts', []))
        except Exception as e:
            print('Gemini', m, e); time.sleep(4)
    return ''


def valida(es, en):
    if not isinstance(en, str): return False
    en = en.strip()
    if not (4 <= len(en) <= max(140, int(len(es) * 1.8))): return False
    if re.search(r'\b(Grado|Graduado|Doble|Ingeniería|Ciencias|Educación|Administración|Estudios|del|de la|y)\b', en): return False   # restos en español
    if re.match(r'^bachelor', en, re.I): return False   # solo la materia, como el resto de nombres
    return True


def main():
    trad = json.load(open(F_TRAD, encoding='utf-8')) if os.path.exists(F_TRAD) else {}
    pend = json.load(open(F_PEND, encoding='utf-8')) if os.path.exists(F_PEND) else []
    pend = [p for p in pend if p not in trad][:MAX]
    print('Pendientes:', len(pend), '· ya traducidos:', len(trad))
    if not pend or not os.environ.get('GEMINI_API_KEY'): return
    nuevos = rechazados = 0
    for i in range(0, len(pend), LOTE):
        lote = pend[i:i + LOTE]
        txt = gemini(PROMPT.format(glosario=GLOSARIO, nombres='\n'.join(lote)))
        try: r = json.loads(re.sub(r'^```(json)?|```$', '', txt.strip()))
        except Exception: print('Respuesta no válida en el lote', i // LOTE + 1); continue
        for es in lote:
            en = r.get(es)
            if valida(es, en): trad[es] = re.sub(r'\s+', ' ', en.strip()); nuevos += 1
            else: rechazados += 1
        json.dump(dict(sorted(trad.items())), open(F_TRAD, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        time.sleep(2)
    print(f'Traducidos ahora: {nuevos} · rechazados por la comprobación: {rechazados} · total: {len(trad)}')


if __name__ == '__main__':
    main()
