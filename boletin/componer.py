"""Boletín semanal de AURZANE (v2, 24/11/2026). Se compone solo cada domingo con material que ya se actualiza solo.

Secciones de cada envío:
  1. Reto de la semana: un problema cotidiano con un test y un ejercicio guiado del mismo tema.
  2. Dato científico: un estudio real de acceso abierto (Research Hub, 25.000 artículos) contado en cuatro líneas por la IA,
     con su enlace. Si la IA falla o el texto no pasa el control de calidad, una curiosidad ya verificada con su fuente.
  3. Libro de la semana: qué problema resuelve y dónde conseguirlo (su ficha tiene Awin y Amazon), más una cita de un
     libro gratis de la biblioteca.
  4. Píldora de un curso gratis: una lección distinta cada semana, con enlace al curso.
  5. Recurso de temporada: según el calendario de España (PAU, vuelta al cole, Navidad, propósitos de año…).
  6. Artículo nuevo de la web (solo si hay uno que aún no se haya enviado) y una frase de cierre.
Nada se repite mientras quede material sin usar: lo enviado se anota en boletin/historial.json (se guarda solo al enviar).
Fotos reales del banco de imágenes (banco/banco.json). Salida: /tmp/boletin/boletin.html y asunto.txt.
"""
import json, os, re, html, datetime, hashlib, urllib.request, urllib.parse

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = lambda s: html.escape('' if s is None else str(s), quote=True)
HOY = datetime.date.fromisoformat(os.environ['FECHA']) if os.environ.get('FECHA') else datetime.date.today()
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1'
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'   # solo lectura de lo publicado
FH = os.path.join(R, 'boletin', 'historial.json')


def leer(p, d):
    try: return json.load(open(os.path.join(R, p), encoding='utf-8'))
    except Exception: return d


HIST = leer('boletin/historial.json', {'envios': []})
ULTIMO = {}   # tipo -> {id: fecha del último uso}
for env in HIST['envios']:
    for t, i in env.get('ids', {}).items(): ULTIMO.setdefault(t, {})[str(i)] = env['fecha']
USADO = {}


def elegir(tipo, cands, idf=lambda x: x['id']):
    """El primero que nunca se ha enviado; si ya salieron todos, el que hace más tiempo que salió."""
    if not cands: return None
    u = ULTIMO.get(tipo, {})
    nuevo = [c for c in cands if str(idf(c)) not in u]
    x = nuevo[0] if nuevo else min(cands, key=lambda c: u.get(str(idf(c)), ''))
    USADO[tipo] = idf(x); return x


def foto(mundo, tema, ancho=1120, alto=560):
    """Foto real del banco (Unsplash), elegida de forma estable por semana."""
    fs = (leer('banco/banco.json', {}).get(mundo) or {}).get(tema) or []
    if not fs: return ''
    f = fs[int(hashlib.md5(f'{HOY.isocalendar()[:2]}{tema}'.encode()).hexdigest(), 16) % len(fs)]
    return f['r'] + f'?w={ancho}&h={alto}&q=70&auto=format&fit=crop'


def pedir(url, datos=None, cab=None, t=60):
    rq = urllib.request.Request(url, data=json.dumps(datos).encode() if datos is not None else None,
                                headers=dict({'apikey': KEY, 'Content-Type': 'application/json'}, **(cab or {})))
    with urllib.request.urlopen(rq, timeout=t) as r: return json.load(r)


def ia(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    for m in ['gemini-flash-latest', 'gemini-flash-lite-latest']:
        if not k: break
        try:
            r = pedir(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}',
                      {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': .3, 'responseMimeType': 'application/json'}}, {'apikey': ''}, 120)
            return json.loads(''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts']))
        except Exception as e: print('gemini', m, str(e)[:90])
    return None


# ------------------------------------------------------------------ material fijo (verificado en el servidor)
M, L, N, B = 'https://mind.aurzane.com/', 'https://live.aurzane.com/', 'https://nexus.aurzane.com/', 'https://build.aurzane.com/'
TEST = {
    'estres': ('Test de estrés (DASS-21)', M + 'test-de-estres/', 4), 'ansiedad': ('Test de ansiedad GAD-7', M + 'test-de-ansiedad/', 2),
    'burnout': ('Test de burnout', M + 'test-de-burnout/', 3), 'sueno': ('Test de sueño', L + 'test-de-sueno/', 3),
    'autoestima': ('Test de autoestima de Rosenberg', M + 'test-de-autoestima/', 3), 'autocompasion': ('Test de autocompasión', M + 'test-de-autocompasion/', 4),
    'resiliencia': ('Test de resiliencia', M + 'test-de-resiliencia/', 2), 'soledad': ('Test de soledad', M + 'test-de-soledad/', 1),
    'satisfaccion': ('Test de satisfacción con la vida', M + 'test-de-satisfaccion-con-la-vida/', 2), 'autoeficacia': ('Test de autoeficacia', M + 'test-de-autoeficacia/', 3),
    'bienestar': ('Test de bienestar WHO-5', L + 'test-de-bienestar/', 2), 'habitos': ('Test de hábitos saludables', L + 'test-de-habitos/', 4),
    'personalidad': ('Test de personalidad (Cinco Grandes)', M + 'test-de-personalidad/', 5), 'vocacional': ('Test vocacional OVP', 'https://ovp.aurzane.com/', 10),
}
EJ = {
    'suspiro': ('Suspiro cíclico', M + 'ejercicios/suspiro-ciclico/', 2), '478': ('Respiración 4-7-8', M + 'ejercicios/respiracion-4-7-8/', 3),
    '54321': ('Técnica 5-4-3-2-1', M + 'ejercicios/tecnica-5-4-3-2-1/', 3), 'stop': ('Técnica STOP', M + 'ejercicios/tecnica-stop/', 1),
    'cuadrada': ('Respiración cuadrada', M + 'ejercicios/respiracion-cuadrada/', 4), 'coherencia': ('Coherencia cardiaca', M + 'ejercicios/coherencia-cardiaca/', 5),
    'escaneo': ('Escaneo corporal', M + 'ejercicios/escaneo-corporal/', 7), 'relajacion': ('Relajación muscular progresiva', M + 'ejercicios/relajacion-muscular-progresiva/', 8),
    'autocompasion': ('Pausa de autocompasión', M + 'ejercicios/pausa-de-autocompasion/', 5), 'lugar': ('Visualización del lugar seguro', M + 'ejercicios/lugar-seguro/', 5),
    'diafragma': ('Respiración diafragmática', M + 'ejercicios/respiracion-diafragmatica/', 5), 'alterna': ('Respiración alterna', M + 'ejercicios/respiracion-alterna/', 5),
    'atencion': ('Atención a la respiración', M + 'ejercicios/atencion-a-la-respiracion/', 5),
}
# reto: id, asunto, problema, test, ejercicio, (mundo, tema de foto), búsqueda en inglés para el estudio, meses en los que encaja mejor
RETOS = [
    ('agotado', '¿Llegas al domingo sin batería?', 'Si esta semana has ido con el depósito en reserva, mide cuánto te está pesando el trabajo y prueba a soltar tensión antes de dormir.', 'burnout', 'suspiro', ('mind', 'estres'), 'burnout', [9, 10, 11]),
    ('nervios', 'Cuando los nervios no te dejan pensar', 'Si notas el pecho apretado o la cabeza a mil, comprueba cómo están tus nervios y prueba una técnica que te devuelve al presente en tres minutos.', 'ansiedad', '54321', ('mind', 'ansiedad'), 'anxiety', [1, 5, 6, 11]),
    ('dormir', 'Dormir mejor empieza antes de acostarte', 'Si te cuesta dormirte o te despiertas cansado, descubre qué te quita descanso y prueba esta respiración en la cama.', 'sueno', '478', ('mind', 'sueno'), 'sleep', [7, 8, 9, 12]),
    ('estres', 'Cuánta tensión llevas encima', 'Antes de que la semana te arrastre, mide tu nivel de estrés en cuatro minutos y regálate un minuto de pausa consciente.', 'estres', 'stop', ('mind', 'estres'), 'stress', [3, 5, 10, 11, 12]),
    ('critica', 'Háblate como le hablarías a un amigo', 'Si eres tu crítico más duro, mira cómo te tratas cuando fallas y prueba una pausa de cinco minutos para hablarte con más amabilidad.', 'autocompasion', 'autocompasion', ('mind', 'autoestima'), 'self-compassion', [1, 2, 9]),
    ('autoestima', 'Lo que piensas de ti también se entrena', 'Diez frases, tres minutos: mira en qué punto está tu autoestima y qué puedes hacer para cuidarla.', 'autoestima', 'lugar', ('mind', 'autoestima'), 'self-esteem', [2, 3, 9]),
    ('soledad', 'Sentirse solo no siempre es estar solo', 'La soledad no deseada es más común de lo que parece. Tres preguntas para ponerle nombre y una visualización para sentirte a salvo.', 'soledad', 'lugar', ('mind', 'soledad'), 'loneliness', [8, 12, 1]),
    ('golpes', 'Volver a levantarse', 'Si te ha tocado una semana difícil, mira cuánto te recuperas de los golpes y prueba una respiración que baja revoluciones.', 'resiliencia', 'coherencia', ('mind', 'resiliencia'), 'resilience', [1, 4, 9]),
    ('balance', '¿Cómo de satisfecho estás con tu vida?', 'Cinco frases para hacer balance sin juzgarte, y siete minutos para escuchar a tu cuerpo.', 'satisfaccion', 'escaneo', ('general', 'camino'), 'life satisfaction', [12, 1, 6]),
    ('capaz', 'Sí puedes (y hay una escala que lo mide)', 'Cuando un reto te parece demasiado, mide tu autoeficacia y prepara la cabeza con una respiración que da foco.', 'autoeficacia', 'cuadrada', ('learn', 'concentracion'), 'self-efficacy', [4, 5, 6, 9]),
    ('bienestar', 'Cinco preguntas para saber cómo estás de verdad', 'El índice de bienestar de la OMS en dos minutos, y una respiración lenta para cerrar el día.', 'bienestar', 'diafragma', ('live', 'descanso'), 'wellbeing', [3, 10]),
    ('habitos', 'Pequeños hábitos, gran diferencia', 'Revisa cómo comes, duermes y te mueves con un test validado, y empieza por algo pequeño: cinco minutos de calma.', 'habitos', 'atencion', ('live', 'correr'), 'healthy habits', [1, 4, 9]),
    ('tension', 'El estrés también se queda en el cuerpo', 'Si tienes la espalda o la mandíbula tensas, mide tu estrés y aprende a soltar músculo a músculo.', 'estres', 'relajacion', ('mind', 'calma'), 'muscle relaxation', [6, 11]),
    ('personalidad', '¿Fogata, Faro o Telescopio?', 'Conocerte ayuda a decidir mejor. Descubre tu perfil de personalidad en cinco minutos y equilibra la mente con una respiración alterna.', 'personalidad', 'alterna', ('mind', 'emociones'), 'personality', [2, 7, 8]),
]
# recurso de temporada por mes (España): (título, texto, botón, url, (mundo, tema de foto))
TEMP = {
    1: [('Haz que tus ahorros trabajen', 'Enero es buen mes para echar números: mira cuánto crece lo que ahorras con el interés compuesto.', 'Calcular mis ahorros', L + 'calculadora-interes-compuesto/', ('build', 'ahorro')),
        ('¿Cuánto cobras de verdad?', 'Con la nueva nómina del año, comprueba tu sueldo neto con el IRPF actualizado.', 'Calcular mi sueldo neto', B + 'calculadora-sueldo-neto/', ('build', 'dinero'))],
    2: [('Rebajas: ¿cuánto te ahorras?', 'Descuentos, subidas y porcentajes, sin hacer cuentas a mano.', 'Calcular porcentajes', L + 'calculadora-porcentajes/', ('build', 'dinero'))],
    3: [('¿Qué estudiar el curso que viene?', 'Las inscripciones abren pronto. El test vocacional relaciona tus intereses con carreras reales.', 'Hacer el test vocacional', 'https://ovp.aurzane.com/', ('nexus', 'orientacion'))],
    4: [('Cuenta atrás para la PAU', 'Calcula tu nota de acceso y de admisión con las ponderaciones de cada universidad.', 'Calcular mi nota PAU', N + 'calculadora-nota-pau/', ('nexus', 'estudiantes'))],
    5: [('PAU a la vista', 'Calcula tu nota de admisión y compárala con las notas de corte del año pasado.', 'Ver las notas de corte', N + 'universidades/notas-de-corte/', ('nexus', 'estudiantes'))],
    6: [('Después de la PAU', 'Compara tu nota con las notas de corte y mira qué puedes estudiar y dónde.', 'Qué puedo estudiar', N + 'universidades/que-puedo-estudiar/', ('nexus', 'graduacion'))],
    7: [('Vacaciones que descansan', 'El verano es buen momento para revisar hábitos sin prisa.', 'Hacer el test de hábitos', L + 'test-de-habitos/', ('live', 'descanso')),
        ('Bebe lo que necesitas', 'Con el calor, calcula cuánta agua necesitas según tu peso y tu actividad.', 'Calcular mi agua', L + 'calculadora-agua/', ('live', 'agua'))],
    8: [('Antes de volver', 'Si vas a cambiar de piso o reformar en septiembre, calcula el presupuesto con precios de 2026.', 'Calcular la reforma', B + 'calculadora-reforma/', ('build', 'obra'))],
    9: [('Vuelta a clase con buen pie', 'Cursos gratis con certificado para empezar el curso con método.', 'Ver los cursos gratis', 'https://learn.aurzane.com/cursos/', ('learn', 'estudiar')),
        ('Comparar universidades', 'Si estás pensando en estudiar fuera, compara universidades de 55 países.', 'Comparar universidades', N + 'universidades/comparar/', ('nexus', 'campus'))],
    10: [('10 de octubre: Día de la Salud Mental', 'Un buen día para preguntarte cómo estás. El índice WHO-5 tarda dos minutos.', 'Hacer el test de bienestar', L + 'test-de-bienestar/', ('mind', 'esperanza'))],
    11: [('Organiza el final de año', 'Calcula cuántos días quedan para tus fechas importantes y planifica sin agobios.', 'Contar días', L + 'calculadora-dias-entre-fechas/', ('build', 'oficina')),
         ('¿Hipoteca a la vista?', 'Simula tu hipoteca con el Euríbor del día, gastos e impuestos incluidos.', 'Simular mi hipoteca', B + 'calculadora-hipoteca/', ('build', 'vivienda'))],
    12: [('Fiestas con calma', 'Las fiestas también pueden pesar. Si te sientes solo, no eres el único: ponerle nombre ayuda.', 'Hacer el test de soledad', M + 'test-de-soledad/', ('mind', 'familia')),
         ('Balance del año', 'Cinco frases para cerrar el año mirando lo que sí ha ido bien.', 'Hacer el test de satisfacción', M + 'test-de-satisfaccion-con-la-vida/', ('general', 'luz'))],
}
UTM = f'utm_source=boletin&utm_medium=email&utm_campaign={HOY.isoformat()}'
def u(x, c=''): return x + ('&' if '?' in x else '?') + UTM + (f'&utm_content={c}' if c else '')

# ------------------------------------------------------------------ elección de la semana
mes = HOY.month
retos = sorted([dict(zip(['id', 'asunto', 'problema', 'test', 'ej', 'foto', 'en', 'meses'], r)) for r in RETOS], key=lambda r: mes not in r['meses'])
reto = elegir('reto', retos)
temp = elegir('temporada', [dict(zip(['titulo', 'texto', 'boton', 'url', 'foto'], t), id=f'{mes}-{i}') for i, t in enumerate(TEMP[mes])])

# dato científico: estudio real (IA) o curiosidad verificada
dato = None
try:
    anio = HOY.year - 3
    q = urllib.parse.urlencode({'select': 'id,titulo,abstract,autores,anio,doi,url_articulo', 'es_acceso_abierto': 'eq.true', 'abstract': 'not.is.null',
                                'anio': f'gte.{anio}', 'titulo': f'ilike.*{reto["en"]}*', 'order': 'anio.desc,id', 'limit': '40'})
    est = [x for x in pedir(f'{SB}/biblioteca_unificada?{q}') if len(x.get('abstract') or '') > 400 and str(x['id']) not in ULTIMO.get('estudio', {})]
    for x in est[:3]:
        r = ia('Eres divulgador científico para un boletín en español de España (tuteo, sin rayas largas). Con este resumen de un estudio real, '
               'escribe un dato útil para la vida diaria. Reglas: no exageres ni inventes nada que no diga el resumen; si es un estudio pequeño o '
               'preliminar, dilo; nada de consejos médicos. Devuelve JSON {"titulo": "frase corta y atractiva, máximo 70 caracteres", '
               '"texto": "4 frases sencillas: qué estudiaron, qué encontraron y qué puede significar en el día a día", '
               '"nota": de 0 a 10 según lo fiel y útil que es, "motivo": "por qué esa nota"}.\n\n'
               f'Título: {x["titulo"]}\nAño: {x["anio"]}\nResumen: {x["abstract"][:3500]}')
        if r and float(r.get('nota') or 0) >= 8 and 120 < len(r.get('texto') or '') < 700 and '—' not in r['texto']:
            enl = f'https://doi.org/{x["doi"]}' if x.get('doi') else x.get('url_articulo')
            dato = {'titulo': r['titulo'], 'texto': r['texto'], 'fuente': f'{(x.get("autores") or "").split(",")[0]} y otros, {x["anio"]}', 'url': enl, 'boton': 'Leer el estudio completo'}
            USADO['estudio'] = x['id']; break
except Exception as e: print('estudio', str(e)[:120])
if not dato:
    cur = sorted([c for c in leer('ai/curiosidades.json', []) if c.get('fuente') and c.get('verificacion')], key=lambda c: c.get('fecha', ''), reverse=True)
    c = elegir('curiosidad', cur)
    if c: dato = {'titulo': c['titulo'], 'texto': c.get('resumen') or c['dato'], 'fuente': c['fuente'], 'url': 'https://aurzane.com/research.html', 'boton': 'Explorar 25.000 estudios'}

libros = [x for x in leer('tienda/catalogo.json', []) if x.get('portada') and (x.get('porque') or x.get('resumen'))]
libros.sort(key=lambda x: (not x.get('tendencia'), x.get('fecha', '')), reverse=False)
libro = elegir('libro', libros)
cita = elegir('cita', sorted([c for c in leer('ai/citas.json', []) if (c.get('nota') or 0) >= 8 and c.get('url')], key=lambda c: c.get('fecha', '')))
frase = elegir('frase', [f for f in leer('ai/frases_web.json', []) if f.get('ok') and (f.get('nota') or 0) >= 7 and len(f['texto']) < 180])
arts = sorted([a for a in leer('ai/articulos_ai.json', []) if a.get('slug')], key=lambda a: a.get('fecha', ''), reverse=True)
art = next((a for a in arts if a['slug'] not in ULTIMO.get('articulo', {})), None)
if art: USADO['articulo'] = art['slug']

leccion = None
try:
    cursos = pedir(f'{SB}/rpc/course_catalog_public', {})
    lecs = [{'id': f'{c["slug"]}/{i}', 'curso': c, 'tema': m['titulo'], 'titulo': l['titulo'], 'n': sum(len(mm['lecciones']) for mm in c['modulos'])}
            for c in cursos for m in c['modulos'] for i, l in enumerate(m['lecciones'][:1] + m['lecciones'][1:]) if l.get('titulo')]
    # cada semana un curso distinto (por turnos) y, dentro de él, la siguiente lección que no haya salido
    orden = sorted({x['curso']['slug'] for x in lecs}, key=lambda s: ULTIMO.get('curso', {}).get(s, ''))
    for s in orden:
        cand = [x for x in lecs if x['curso']['slug'] == s]
        if any(x['id'] not in ULTIMO.get('leccion', {}) for x in cand) or s == orden[-1]:
            leccion = elegir('leccion', cand); USADO['curso'] = s; break
except Exception as e: print('cursos', str(e)[:120])

# ------------------------------------------------------------------ correo
VERDE, CREMA, ORO, TINTA, GRIS = '#183D32', '#F6F5F0', '#E2BF6A', '#1d1f1c', '#5e605a'
def etiqueta(t): return f'<p style="margin:0 0 8px;font:700 12px/1.2 Arial,sans-serif;letter-spacing:.08em;color:#8a6d1f">{E(t)}</p>'
def boton(t, url, c, claro=False):
    bg, fg = (ORO, '#1b1440') if claro else (VERDE, CREMA)
    return f'<a href="{E(u(url, c))}" style="display:inline-block;background:{bg};color:{fg};padding:12px 22px;border-radius:99px;font:700 15px Arial,sans-serif;text-decoration:none;margin:4px 8px 4px 0">{E(t)}</a>'
def img(src, alt=''):
    return f'<img src="{E(src)}" width="560" alt="{E(alt)}" style="display:block;width:100%;max-width:560px;height:auto;border-radius:14px;margin:0 0 16px">' if src else ''
def bloque(contenido, fondo='#ffffff'):
    return f'<tr><td style="padding:26px 28px;background:{fondo};border-top:1px solid #ece8dd">{contenido}</td></tr>'
H2 = 'margin:0 0 8px;font:700 22px/1.25 Georgia,serif;color:' + TINTA
P = f'margin:0 0 14px;font:16px/1.6 Arial,sans-serif;color:{TINTA}'

t1, e1 = TEST[reto['test']], EJ[reto['ej']]
partes = [bloque(etiqueta('Reto de la semana') + img(foto(*reto['foto']), '') + f'<h2 style="{H2}">{E(reto["asunto"])}</h2><p style="{P}">{E(reto["problema"])}</p>'
                 f'<p style="{P}"><b>1.</b> {E(t1[0])} ({t1[2]} min, gratis y anónimo).<br><b>2.</b> {E(e1[0])}, guiado ({e1[2]} min).</p>'
                 + boton('Hacer el test', t1[1], 'reto-test') + boton('Probar el ejercicio', e1[1], 'reto-ejercicio', True))]
if dato:
    partes.append(bloque(etiqueta('Un dato de la ciencia') + f'<h2 style="{H2}">{E(dato["titulo"])}</h2><p style="{P}">{E(dato["texto"])}</p>'
                         f'<p style="margin:0 0 14px;font:13px/1.5 Arial,sans-serif;color:{GRIS}">Fuente: {E(dato["fuente"])}</p>'
                         f'<a href="{E(u(dato["url"], "dato"))}" style="font:700 15px Arial,sans-serif;color:{VERDE}">{E(dato["boton"])}</a>', '#fbfaf6'))
if libro:
    ficha = f'https://aurzane.com/libros/{libro["id"]}/'
    txt = (libro.get('porque') or libro.get('resumen') or '')
    txt = txt[:320].rsplit(' ', 1)[0] + '…' if len(txt) > 320 else txt
    c = (f'<table role="presentation" width="100%"><tr><td width="112" style="vertical-align:top;padding-right:18px"><img src="{E(libro["portada"])}" width="112" alt="Portada de {E(libro["titulo"])}" style="display:block;border-radius:6px;box-shadow:0 4px 14px rgba(0,0,0,.18)"></td>'
         f'<td style="vertical-align:top"><h2 style="{H2}">{E(libro["titulo"])}</h2><p style="margin:0 0 10px;font:14px Arial,sans-serif;color:{GRIS}">{E(libro["autor"])}</p>'
         f'<p style="{P}">{E(txt)}</p>' + boton('Ver dónde conseguirlo', ficha, 'libro') + '</td></tr></table>')
    if cita:
        c += (f'<div style="margin:22px 0 0;padding:16px 18px;border-left:4px solid {ORO};background:#fbf7ea;border-radius:0 12px 12px 0">'
              f'<p style="margin:0 0 6px;font:italic 16px/1.55 Georgia,serif;color:{TINTA}">«{E(cita["texto"])}»</p>'
              f'<p style="margin:0;font:13px/1.5 Arial,sans-serif;color:{GRIS}">De <i>{E(cita["libro"])}</i>, gratis en la biblioteca de AURZANE. '
              f'<a href="{E(u(cita["url"], "cita"))}" style="color:{VERDE};font-weight:700">Leerlo gratis</a></p></div>')
    partes.append(bloque(etiqueta('Libro de la semana') + c))
if leccion:
    cu = leccion['curso']; urlc = f'https://learn.aurzane.com/curso/{cu["slug"]}/'
    partes.append(bloque(etiqueta('Píldora de un curso gratis') + img(foto('learn', 'estudiar' if 'psicolog' in cu['titulo'].lower() else 'lectura'), '') +
                         f'<h2 style="{H2}">{E(leccion["titulo"])}</h2><p style="{P}">Es una de las {leccion["n"]} lecciones de <b>{E(cu["titulo"])}</b>, '
                         f'dentro del tema «{E(leccion["tema"])}». Se hace a tu ritmo desde el móvil, es gratis y, al aprobar, tienes tu certificado.</p>'
                         + boton('Empezar el curso', urlc, 'curso'), '#fbfaf6'))
if temp:
    partes.append(bloque(etiqueta('Para estas semanas') + img(foto(*temp['foto']), '') + f'<h2 style="{H2}">{E(temp["titulo"])}</h2><p style="{P}">{E(temp["texto"])}</p>'
                         + boton(temp['boton'], temp['url'], 'temporada', True)))
if art:
    a_url = f'https://aurzane.com/articulos/{art["slug"]}/'
    partes.append(bloque(etiqueta('Nuevo en la web') + f'<h2 style="{H2}"><a href="{E(u(a_url, "articulo"))}" style="color:{TINTA};text-decoration:none">{E(art["titulo"])}</a></h2>'
                         f'<p style="{P}">{E((art.get("resumen") or "")[:240])}</p><a href="{E(u(a_url, "articulo"))}" style="font:700 15px Arial,sans-serif;color:{VERDE}">Leer el artículo</a>', '#fbfaf6'))
if frase:
    partes.append(f'<tr><td style="padding:30px 28px;background:{VERDE};text-align:center"><p style="margin:0 0 8px;font:italic 19px/1.5 Georgia,serif;color:{CREMA}">«{E(frase["texto"])}»</p>'
                  f'<p style="margin:0;font:13px Arial,sans-serif;color:#D9CDB2">{E(frase["autor"])}</p></td></tr>')

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
pre = f'{reto["asunto"]} Además: {dato["titulo"] if dato else "un dato de la ciencia"}, el libro de la semana y una lección gratis.'
html_b = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="color-scheme" content="light"><title>Tu domingo en AURZANE</title></head>'
          f'<body style="margin:0;background:#efece3"><div style="display:none;max-height:0;overflow:hidden">{E(pre)}</div>'
          '<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 10px">'
          '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:616px;background:#fff;border-radius:18px;overflow:hidden">'
          f'<tr><td style="padding:26px 28px 22px;background:{VERDE}"><p style="margin:0;font:700 22px Georgia,serif;letter-spacing:.08em;color:{CREMA}">AUR<span style="color:{ORO}">Z</span>ANE</p>'
          f'<p style="margin:6px 0 0;font:14px Arial,sans-serif;color:#D9CDB2">Tu domingo · {HOY.day} de {MESES[HOY.month - 1]} de {HOY.year}</p></td></tr>'
          + ''.join(partes) +
          f'<tr><td style="padding:22px 28px 28px;font:13px/1.6 Arial,sans-serif;color:{GRIS};background:#fff">'
          f'Más de 700 libros gratis en la <a href="{E(u("https://aurzane.com/biblioteca/"))}" style="color:{GRIS}">biblioteca</a>, tests gratuitos en <a href="{E(u(M))}" style="color:{GRIS}">MIND</a> '
          f'y cursos con certificado en <a href="{E(u("https://learn.aurzane.com/cursos/"))}" style="color:{GRIS}">LEARN</a>. Los tests son orientativos y no sustituyen la valoración de un profesional. '
          'Algunos enlaces de libros son de afiliado: si compras, AURZANE recibe una pequeña comisión sin coste para ti.<br><br>'
          'Recibes este correo porque te suscribiste al boletín de AURZANE. <a href="{{BAJA}}" style="color:' + GRIS + '">Darme de baja</a>.</td></tr>'
          '</table></td></tr></table></body></html>')
asunto = reto['asunto'] + (f' · {libro["titulo"]}' if libro and len(reto['asunto'] + libro['titulo']) < 70 else '')
os.makedirs('/tmp/boletin', exist_ok=True)
open('/tmp/boletin/boletin.html', 'w', encoding='utf-8').write(html_b)
open('/tmp/boletin/asunto.txt', 'w', encoding='utf-8').write(asunto)
json.dump({'fecha': HOY.isoformat(), 'asunto': asunto, 'ids': USADO}, open('/tmp/boletin/envio.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('asunto:', asunto); print('piezas:', json.dumps(USADO, ensure_ascii=False))
