"""Fotos del catálogo de imágenes (índice banco/banco.json; las fotos salen del CDN de Pexels en AVIF, sin ocupar SiteGround).
Misma lógica que AurzaneBanco.foto() en diseno/v4_tema.js: tema por palabras clave del texto, foto fija para el mismo texto."""
import os, re, json, hashlib

CLAVES = [
    (r'ansiedad|anxi|p[áa]nico|panic|worry|preocupa', 'mind', 'ansiedad'), (r'depres|tristeza|sadness|mood|[áa]nimo', 'mind', 'tristeza'),
    (r'estr[ée]s|stress|burnout|agotamiento', 'mind', 'estres'), (r'cerebr|brain|neuro|cognit', 'mind', 'cerebro'),
    (r'terapia|therap|counsel|psicoterap', 'mind', 'terapia'), (r'mindful|medita|atenci[óo]n plena', 'mind', 'meditacion'),
    (r'sue[ñn]o|sleep|insomn|dormir', 'mind', 'sueno'), (r'pareja|couple|marital|romantic|amor', 'mind', 'pareja'),
    (r'famil|parent|padres|madre|padre|crianza', 'mind', 'familia'), (r'ni[ñn]|child|infan|kid|beb[ée]', 'mind', 'infancia'),
    (r'adolesc|teen|youth|j[óo]ven', 'mind', 'adolescentes'), (r'older|elder|aging|envejec|mayores|dementia|demencia|alzheimer', 'mind', 'mayores'),
    (r'emoci|emotion|feeling|sentimiento', 'mind', 'emociones'), (r'autoestima|self-esteem|self-efficacy|autoeficacia|confianza', 'mind', 'autoestima'),
    (r'soledad|loneli|isolat|aislamiento', 'mind', 'soledad'),
    (r'universi|higher education|college|campus|facultad', 'nexus', 'campus'), (r'estudiante|student|alumn', 'nexus', 'estudiantes'),
    (r'graduat|career|carrera|employab|vocaci', 'nexus', 'graduacion'), (r'teach|docen|profesor|lecture|ense[ñn]', 'nexus', 'clase'),
    (r'laborator|experiment', 'nexus', 'laboratorio'), (r'artificial|machine learning|software|algorit|digital|comput|tecnolog|internet|chatbot', 'nexus', 'tecnologia'),
    (r'research|investigaci|scien|cienc', 'nexus', 'investigacion'),
    (r'diet|nutri|food|aliment|obes|comida', 'live', 'alimentacion'), (r'exercis|ejercicio|physical activity|actividad f[íi]sica|running|correr|fitness', 'live', 'correr'),
    (r'yoga', 'live', 'yoga'), (r'water|hidrat|agua', 'live', 'agua'), (r'pregnan|embaraz|maternal|birth|parto|postpartum|posparto', 'live', 'embarazo'),
    (r'clinic|patient|paciente|hospital|medical|m[ée]dic|salud|health|cancer|c[áa]ncer', 'live', 'medico'), (r'sport|deport|athlet|atleta', 'live', 'deporte'),
    (r'lectura|reading|literacy|libro|book', 'learn', 'lectura'), (r'aprend|learning|study|estudi', 'learn', 'estudiar'),
    (r'aula|classroom|school|escuela|colegio', 'learn', 'aula'), (r'online|e-learning|mooc|virtual', 'learn', 'online'),
    (r'idioma|language|bilingu|lengua', 'learn', 'idiomas'), (r'memoria|memory', 'learn', 'memoria'), (r'escritura|writing|escribir', 'learn', 'escritura'),
    (r'atenci[óo]n|attention|focus|concentr|tdah|adhd', 'learn', 'concentracion'),
    (r'hipoteca|mortgage', 'build', 'llaves'), (r'alquiler|rent', 'build', 'pisos'), (r'vivienda|housing|home|house|hogar', 'build', 'vivienda'),
    (r'ahorro|saving|pensi[óo]n|retire|jubil', 'build', 'jubilacion'), (r'financ|money|dinero|income|ingreso|econom|sueldo|salario', 'build', 'dinero'),
    (r'architect|arquitect|urban|ciudad|city', 'build', 'arquitectura'), (r'construct|obra|reforma', 'build', 'obra'),
    (r'energ|solar|climat|emisi|emission|eco-', 'build', 'energia'), (r'trabaj|work|employ|labor|empleo', 'build', 'trabajo'),
]
RESERVA = {'mind': '1559757175-5700dde675bc', 'nexus': '1541339907198-e08756dedf3f', 'live': '1454496522488-7a8e488e8606',
           'learn': '1481627834876-b7833e8f5570', 'build': '1461360370896-922624d12aa1', 'general': '1506126613408-eca07ce68773'}
_idx = None

def _banco():
    global _idx
    if _idx is None:
        _idx = {}
        for r in (os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'banco', 'banco.json'), os.path.join('..', 'banco', 'banco.json')):
            try: _idx = json.load(open(r, encoding='utf-8')); break
            except Exception: pass
    return _idx

def foto_banco(texto, mundo='general', ancho=640, mundo_tema=None):
    """URL de una foto real del banco. mundo_tema=(mundo, tema) fuerza el tema; si no, se deduce del texto."""
    idx, t = _banco(), str(texto or '')
    m, tema = mundo_tema or next(((mm, tt) for r, mm, tt in CLAVES if re.search(r, t, re.I)), (None, None))
    lista = (idx.get(m) or {}).get(tema) if m else None
    if not lista or not any('p' in x for x in lista):
        lista = [x for v in (idx.get(mundo) or idx.get('general') or {}).values() for x in v]
    n = int(hashlib.md5((t + mundo).encode()).hexdigest(), 16)
    lista = [x for x in (lista or []) if 'p' in x]
    if lista:
        w = 1600 if ancho > 800 else 640; x = lista[n % len(lista)]
        return f'https://images.pexels.com/photos/{x["p"]}/pexels-photo-{x["p"]}.jpeg?auto=compress&cs=tinysrgb&w={w}&h={round(w * .625)}&fit=crop'
    return f'https://images.unsplash.com/photo-{RESERVA.get(m or mundo, RESERVA["general"])}?w={ancho}&q=70&fit=crop&auto=format'
