# Fuente editable de los productos fijos de AURZANE para el marketing automático.
# Ejecuta: python3 marketing/fijos.py  -> marketing/fijos.json
# Cada producto tiene 3 ganchos: cada red usa uno distinto, así nunca sale el mismo texto en todas.
import json, os
A = 'No es un diagnóstico: es una orientación. Si te preocupa, habla con un profesional.'
P = []
def p(id, tipo, mundo, url, titulo, ganchos, texto, tags, aviso='', img=None, emoji=''):
    P.append(dict(id=id, tipo=tipo, mundo=mundo, url=url, titulo=titulo, ganchos=ganchos, texto=texto,
                  hashtags=tags, aviso=aviso, img=img, emoji=emoji))

M = 'https://mind.aurzane.com'; L = 'https://live.aurzane.com'; B = 'https://build.aurzane.com'
N = 'https://nexus.aurzane.com'; W = 'https://aurzane.com'; LE = 'https://learn.aurzane.com'

# ---------- MIND ----------
p('test-personalidad', 'test', 'mind', f'{M}/test-de-personalidad/', 'Test de personalidad',
  ['¿Eres Fogata, Faro o Telescopio?', 'Tu personalidad, en 20, 50 o 120 preguntas', 'Conoce tus fortalezas y las carreras que encajan contigo'],
  'Test de los Cinco Grandes con 11 perfiles y 30 facetas. Eliges la versión corta, media o larga y ves tu resultado al momento. Gratis y sin registro.',
  ['TestDePersonalidad', 'Psicología', 'Autoconocimiento', 'BigFive'], emoji='🧠')
p('test-ansiedad', 'test', 'mind', f'{M}/test-de-ansiedad/', 'Test de ansiedad GAD-7',
  ['¿Es estrés normal o es ansiedad?', '7 preguntas para saber cómo está tu ansiedad', 'El cuestionario de ansiedad que usan médicos y psicólogos'],
  'El GAD-7 en español: 7 preguntas, 2 minutos y tu resultado explicado al instante, con qué hacer después. Gratis y anónimo.',
  ['Ansiedad', 'SaludMental', 'Psicología', 'Bienestar'], A, emoji='😮‍💨')
p('test-depresion', 'test', 'mind', f'{M}/test-de-depresion/', 'Test de depresión PHQ-9',
  ['¿Cómo está de verdad tu estado de ánimo?', 'Llevas semanas sin ganas de nada. ¿Y si lo miras?', 'El PHQ-9, en 3 minutos y gratis'],
  '9 preguntas del cuestionario que usan médicos y psicólogos, con tu resultado explicado y dónde pedir ayuda si la necesitas. Anónimo.',
  ['SaludMental', 'EstadoDeÁnimo', 'Psicología'], A + ' En España, 024 atiende las 24 horas.', emoji='🌧️')
p('test-autoestima', 'test', 'mind', f'{M}/test-de-autoestima/', 'Test de autoestima de Rosenberg',
  ['¿Cómo está tu autoestima?', '10 frases para saber cómo te ves', 'La escala de autoestima más usada del mundo, en 2 minutos'],
  'La escala de Rosenberg: 10 frases, tu puntuación explicada y consejos concretos para cuidarla. Gratis y anónimo.',
  ['Autoestima', 'Psicología', 'Bienestar', 'Autoconocimiento'], A, emoji='🪞')
p('test-tdah', 'test', 'mind', f'{M}/test-de-tdah/', 'Cribado de TDAH en adultos',
  ['¿Despistes o TDAH?', '6 preguntas de la OMS sobre TDAH en adultos', 'Te cuesta terminar lo que empiezas. ¿Podría ser TDAH?'],
  'El cribado ASRS de la OMS para adultos: 6 preguntas, resultado al momento y qué hacer si sale positivo. Gratis y anónimo.',
  ['TDAH', 'TDAHAdultos', 'Neurodiversidad', 'Psicología'], A, emoji='⚡')
p('test-autocompasion', 'test', 'mind', f'{M}/test-de-autocompasion/', 'Test de autocompasión',
  ['¿Te hablas como hablarías a un amigo?', 'Cómo te tratas cuando las cosas van mal', 'La escala de autocompasión de Kristin Neff, en español'],
  '12 frases de la escala de Neff validada en español y tu resultado explicado: amabilidad contigo, humanidad compartida y atención plena.',
  ['Autocompasión', 'Mindfulness', 'Psicología', 'Bienestar'], A, emoji='🤍')
p('test-satisfaccion', 'test', 'mind', f'{M}/test-de-satisfaccion-con-la-vida/', 'Test de satisfacción con la vida',
  ['¿Qué tan satisfecho estás con tu vida?', '5 frases y 1 minuto para medir tu satisfacción vital', 'La escala de Ed Diener, en 1 minuto'],
  'La escala de satisfacción con la vida de Ed Diener: 5 frases y tu resultado explicado al momento. Gratis y anónimo.',
  ['Felicidad', 'Bienestar', 'PsicologíaPositiva'], emoji='😊')
# ---------- LIVE ----------
p('test-bienestar', 'test', 'live', f'{L}/test-de-bienestar/', 'Test de bienestar WHO-5',
  ['¿Cómo está tu bienestar esta semana?', '5 preguntas de la OMS, 1 minuto', 'Tu bienestar de 0 a 100'],
  'El índice WHO-5 de la OMS: 5 preguntas, tu resultado de 0 a 100 y consejos claros. Gratis y anónimo.',
  ['Bienestar', 'SaludMental', 'OMS'], A, emoji='🌤️')
p('test-sueno', 'test', 'live', f'{L}/test-de-sueno/', 'Chequeo de sueño',
  ['¿Duermes bien de verdad?', 'Te despiertas cansado aunque duermas 8 horas', 'Tu sueño de 0 a 100 y un plan de 7 días'],
  '11 preguntas sobre tu descanso, tu puntuación de sueño y un plan de 7 días hecho para ti. Gratis y anónimo.',
  ['Sueño', 'Insomnio', 'Descanso', 'Salud'], emoji='🌙')
p('test-habitos', 'test', 'live', f'{L}/test-de-habitos/', 'Test de hábitos de vida',
  ['¿Qué tan sano es tu estilo de vida?', 'Tu estilo de vida en una nota de 0 a 10', 'Qué hábito cambiar primero'],
  'Alimentación, ejercicio, alcohol, tabaco y estrés: tu nota de 0 a 10 y qué cambiar primero. 2 minutos, gratis.',
  ['HábitosSaludables', 'VidaSana', 'Salud'], emoji='🥗')
p('calc-calorias', 'calculadora', 'live', f'{L}/calculadora-calorias/', 'Calculadora de calorías e IMC',
  ['¿Cuántas calorías necesitas al día?', 'Calorías, IMC, proteína y agua en 1 minuto', 'Deja de adivinar cuánto comer'],
  'Tus calorías diarias con la fórmula Mifflin-St Jeor, tu IMC y cuánta proteína y agua tomar. Gratis.',
  ['Nutrición', 'Calorías', 'IMC', 'Salud'], 'Orientativo. Si tienes una condición de salud, consulta con un profesional.', emoji='🍽️')
p('calc-embarazo', 'calculadora', 'live', f'{L}/calculadora-embarazo/', 'Calculadora de embarazo',
  ['¿De cuántas semanas estás?', 'Fecha probable de parto en 10 segundos', 'Tu calendario de ecografías y pruebas'],
  'Semanas de embarazo, fecha probable de parto y calendario de ecografías y pruebas, ajustado a tu ciclo. Gratis.',
  ['Embarazo', 'Maternidad', 'FechaDeParto'], 'Orientativo: tu matrona o ginecólogo confirma las fechas.', emoji='🤰')
# ---------- BUILD ----------
p('calc-hipoteca', 'calculadora', 'build', f'{B}/calculadora-hipoteca/', 'Calculadora de hipoteca 2026',
  ['¿Alquilar o comprar? Haz la cuenta', 'Tu cuota, impuestos y ahorro necesario', '¿Amortizar plazo o cuota? Mira cuánto ahorras'],
  'Cuota fija o variable con el euríbor actual, ITP de tu comunidad, gastos, si te sale mejor alquilar o comprar y cuánto ahorras amortizando.',
  ['Hipoteca', 'Vivienda', 'FinanzasPersonales', 'Euríbor'], emoji='🏠')
p('calc-sueldo', 'calculadora', 'build', f'{B}/calculadora-sueldo-neto/', 'Calculadora de sueldo neto 2026',
  ['¿Cuánto cobrarás en neto?', 'De bruto a neto con el IRPF de 2026', '30.000 € brutos, ¿cuánto son al mes?'],
  'Retención de IRPF y Seguridad Social de 2026, 12 o 14 pagas, hijos y edad. Resultado al instante y gratis.',
  ['Sueldo', 'IRPF', 'Nómina', 'FinanzasPersonales'], emoji='💶')
p('calc-reforma', 'calculadora', 'build', f'{B}/calculadora-reforma/', 'Calculadora de reforma',
  ['¿Cuánto cuesta reformar tu piso?', 'Presupuesto de reforma partida a partida', 'Antes de pedir presupuesto, haz tu cálculo'],
  'Presupuesto orientativo con precios de mercado de 2026, IVA e imprevistos incluidos. Cocina, baño, suelos y más.',
  ['Reforma', 'Vivienda', 'Presupuesto'], emoji='🛠️')
# ---------- NEXUS / OVP ----------
p('calc-pau', 'calculadora', 'nexus', f'{N}/calculadora-nota-pau/', 'Calculadora de nota PAU',
  ['¿Te llega la nota para tu carrera?', 'Tu nota de admisión sobre 14, con ponderaciones', 'Selectividad: calcula lo que te falta'],
  'Nota de acceso, nota de admisión sobre 14 con ponderaciones y lo que te falta para la nota de corte. Gratis.',
  ['PAU', 'Selectividad', 'EBAU', 'Universidad'], emoji='🧮')
p('notas-corte', 'seccion', 'nexus', f'{N}/universidades/notas-de-corte/', 'Notas de corte 2025-2026',
  ['Notas de corte oficiales de 275 carreras', '¿Qué nota piden para tu carrera?', 'Medicina, Psicología, Enfermería… todas las notas de corte'],
  'Las notas de corte oficiales del Ministerio, por carrera y por universidad pública, ordenadas de mayor a menor.',
  ['NotasDeCorte', 'PAU', 'Universidad', 'Selectividad'], emoji='📊')
p('universidades', 'seccion', 'nexus', f'{N}/universidades/', 'Buscador de universidades',
  ['Más de 6.000 universidades en 55 países', 'Encuentra tu universidad y tu carrera', '¿Dónde estudiar? Compara universidades'],
  'Universidades y carreras de España, Latinoamérica y el mundo, con filtros por ciudad, tipo y carrera. Gratis.',
  ['Universidad', 'Estudiar', 'Carreras'], emoji='🎓')
p('ovp', 'test', 'nexus', 'https://ovp.aurzane.com/', 'Orientación vocacional OVP',
  ['¿No sabes qué estudiar?', 'Seis instrumentos y un informe para elegir carrera', 'Elige carrera con más criterio'],
  'Evaluaciones psicológicas estandarizadas de intereses, aptitudes y personalidad, con informe integrador en PDF. Puedes pausar y seguir cuando quieras.',
  ['OrientaciónVocacional', 'QuéEstudiar', 'Universidad'], emoji='🧭')
# ---------- Conocimiento ----------
p('biblioteca', 'seccion', 'aurzane', f'{W}/biblioteca/', 'Biblioteca AURZANE',
  ['Libros de psicología para leer gratis online', 'Más de 700 libros con licencia abierta', 'Tu próxima lectura de psicología, gratis'],
  'Manuales, ensayos e investigaciones con licencia abierta para leer en el navegador, ordenados por temas.',
  ['LibrosGratis', 'Psicología', 'Lectura'], emoji='📚')
p('articulos', 'seccion', 'aurzane', f'{W}/articulos/', 'Artículos AURZANE',
  ['Lo que dice la ciencia, explicado claro', 'Artículos con sus fuentes citadas', 'Divulgación con fuentes, no opiniones'],
  'Artículos ordenados por mundo, con las fuentes científicas citadas para que puedas comprobarlo todo.',
  ['Divulgación', 'Ciencia', 'Psicología'], emoji='📰')
p('curso-neuro', 'curso', 'learn', f'{LE}/cursos.html?c=neuro-300260', 'Curso de neuroanatomía',
  ['Aprende el sistema nervioso tema a tema', 'Neuroanatomía con lecciones, esquemas y repaso', 'Del desarrollo a la corteza'],
  'Curso interactivo de organización morfofuncional del sistema nervioso: temas, lecciones, mapas y preguntas de repaso.',
  ['Neurociencia', 'Neuroanatomía', 'Estudiantes'], emoji='🧬')
p('curso-metod', 'curso', 'learn', f'{LE}/cursos.html?c=metod-300263', 'Curso de técnicas en neurociencias',
  ['¿Cómo se investiga el cerebro?', 'Estereotaxia, electrofisiología y más', 'Técnicas de investigación en neurociencias'],
  'Curso interactivo de metodología y técnicas de investigación en neurociencias, de la estereotaxia a la neurofarmacología.',
  ['Neurociencia', 'Investigación', 'Estudiantes'], emoji='🔬')
for k, n, e, t in [('mind', 'MIND', '🧠', 'Psicología y neurociencia'), ('live', 'LIVE', '🌿', 'Salud y bienestar'),
                   ('nexus', 'NEXUS', '🌐', 'Tecnología, IA y datos'), ('learn', 'LEARN', '📖', 'Ciencias del aprendizaje'),
                   ('build', 'BUILD', '🏛️', 'Historia, vivienda y civilizaciones')]:
    p(f'biblio-{k}', 'seccion', k, f'https://{k}.aurzane.com/{k}-biblioteca.html', f'Biblioteca {n}',
      [f'Biblioteca {n}: {t.lower()}', f'{t}: investigación para leer', f'Explora la biblioteca de {t.lower()}'],
      f'Literatura científica sobre {t.lower()}, con referencias para ir a las fuentes originales.', ['Investigación', 'Ciencia'], emoji=e)

# ---------- Creatividades del usuario (carpeta Marketing, lotes 05 a 07) ----------
T = 'https://aurzane.com/biblioteca/tema/'
C = [  # (lote, imagen, url, titulo, texto, tags)
 ('05', 1, T + 'neuropsicologia-y-funcionamiento-cerebral.html', 'El cerebro también se entrena', 'Libros abiertos de neuropsicología para entender cómo funciona tu mente y tu rendimiento.', ['Neurociencia', 'LibrosGratis']),
 ('05', 2, T + 'psicobiologia-y-bases-biologicas-de-la-conducta.html', 'Neurociencia para todos', 'Lecturas gratis sobre las bases biológicas de la conducta, explicadas con rigor.', ['Neurociencia', 'Divulgación']),
 ('05', 3, T + 'aprendizaje-y-psicologia-educativa.html', 'Educación y cerebro', 'Libros abiertos de psicología educativa para aprender a enseñar y a aprender mejor.', ['Educación', 'Neuroeducación']),
 ('05', 4, T + 'psicologia-digital-y-tecnologia.html', 'Salud mental en la era digital', 'Lecturas gratis sobre cómo la tecnología influye en la mente y cómo cuidarte en un mundo conectado.', ['SaludMental', 'Tecnología']),
 ('05', 5, 'https://ovp.aurzane.com/', 'Descubre tu vocación', 'Explora tus intereses, aptitudes y personalidad con la orientación vocacional de AURZANE y recibe tu informe.', ['OrientaciónVocacional', 'QuéEstudiar']),
 ('05', 8, W + '/research.html', 'Research Hub', 'Un punto de entrada para buscar investigación en varias bibliotecas científicas a la vez.', ['Investigación', 'Ciencia']),
 ('05', 9, W + '/biblioteca/', 'Biblioteca digital', 'Más de 700 libros con licencia abierta para leer gratis en línea, cuando quieras.', ['LibrosGratis', 'Lectura']),
 ('05', 11, M + '/', 'MIND: cuida tu mente', 'Tests, guías y lecturas de psicología para cuidar tu bienestar, todo gratis.', ['SaludMental', 'Psicología']),
 ('06', 1, W + '/biblioteca/', 'El poder de la lectura', 'Libros que inspiran y enseñan, de lectura directa y gratis en la Biblioteca AURZANE.', ['Lectura', 'LibrosGratis']),
 ('06', 2, T + 'filosofia-aplicada-a-la-vida.html', 'Filosofía para la vida', 'Lecturas para pensar mejor: filosofía aplicada a las decisiones de cada día.', ['Filosofía', 'PensamientoCrítico']),
 ('06', 3, T + 'emociones-y-regulacion-emocional.html', 'Neurociencia y emoción', 'Libros abiertos sobre emociones y regulación emocional para entenderte mejor.', ['Emociones', 'Psicología']),
 ('06', 5, T + 'aprendizaje-y-psicologia-educativa.html', 'Planifica tu aprendizaje', 'Lecturas sobre métodos de estudio, gestión del tiempo y cómo aprender de forma más eficaz.', ['Estudiar', 'TécnicasDeEstudio']),
 ('06', 8, W + '/research.html', 'Research Hub', 'Investiga y descubre publicaciones científicas desde un único buscador.', ['Investigación', 'Ciencia']),
 ('06', 14, W + '/articulos/', 'Artículos y guías', 'Información rigurosa y con fuentes citadas, al alcance de todos.', ['Divulgación', 'Ciencia']),
 ('06', 16, W + '/biblioteca/', 'Conocimiento abierto', 'Libros con licencia abierta: accede, aprende y comparte sin barreras.', ['AccesoAbierto', 'LibrosGratis']),
 ('07', 1, T + 'aprendizaje-y-psicologia-educativa.html', 'El cerebro en la educación', 'Memoria, atención y concentración: lecturas abiertas sobre cómo aprende el cerebro.', ['Neuroeducación', 'Educación']),
 ('07', 3, T + 'sueno-estres-y-bienestar.html', 'Mente sana, vida plena', 'Lecturas gratis sobre bienestar emocional, gestión del estrés y hábitos saludables.', ['Bienestar', 'Estrés']),
 ('07', 4, T + 'psicologia-digital-y-tecnologia.html', 'El futuro de la tecnología', 'Cómo la tecnología cambia nuestra mente: lecturas abiertas de psicología digital.', ['Tecnología', 'Psicología']),
 ('07', 8, W + '/research.html', 'Investiga sin fronteras', 'Busca artículos y publicaciones en varias fuentes académicas desde un solo lugar.', ['Investigación', 'Ciencia']),
 ('07', 14, W + '/articulos/', 'Artículos y guías', 'Información práctica y con fuentes para tu día a día.', ['Divulgación', 'Guías']),
]
for lote, n, url, tit, tx, tags in C:
    p(f'crea-l{lote}-{n:02d}', 'creativo', 'aurzane', url, tit, [tit, tit + ', gratis', tit], tx, tags, img=f'img/lote{lote}-{n:02d}-v.jpg')

# ---------- Campaña «Conoce AURZANE» (fase 4, punto 57; 17/11/2026) ----------
# Presentaciones de cada parte de AURZANE para Instagram, Facebook, Telegram, Bluesky y Mastodon (TikTok y YouTube solo llevan vídeos).
# Sin cifras escritas a mano: los números reales ya salen en cada página y se actualizan solos.
PROMOS = [
 ('promo-mind', 'mind', M + '/', 'MIND: tests de psicología gratis', ['Conócete mejor en 3 minutos', '¿Cómo estás de verdad? Míralo con un test serio', 'Tests de psicología validados, gratis y anónimos'],
  'Ansiedad, estrés, autoestima, personalidad, burnout y más: cuestionarios que usan los profesionales, con tu resultado explicado al momento. Sin registro.', ['Psicología', 'SaludMental', 'Autoconocimiento'], 'person reflecting'),
 ('promo-ejercicios', 'mind', M + '/ejercicios/', 'Ejercicios guiados con voz', ['Calma en 5 minutos, guiada con voz', 'Respira, suelta y vuelve a ti', 'Relajación guiada gratis, cuando la necesites'],
  'Respiración 4-7-8, escaneo corporal, coherencia cardiaca, técnica 5-4-3-2-1 y más ejercicios guiados con voz para bajar el estrés. Gratis.', ['Relajación', 'Mindfulness', 'Bienestar'], 'calm woman breathing nature'),
 ('promo-nexus', 'nexus', N + '/', 'NEXUS: qué y dónde estudiar', ['¿No sabes qué estudiar? Empieza aquí', 'Universidades y carreras de todo el mundo, en un buscador', 'Elige carrera con datos, no a ciegas'],
  'Busca universidades por país y ranking, compara carreras y consulta notas de corte oficiales en España. Gratis y sin registro.', ['Universidad', 'QuéEstudiar', 'Orientación'], 'university students campus'),
 ('promo-ovp', 'mind', 'https://ovp.aurzane.com/', 'Orientación vocacional AURZANE', ['Descubre a qué te gustaría dedicarte', 'Intereses, aptitudes y personalidad en un solo informe', 'Orientación vocacional hecha por un psicólogo'],
  'Un proceso guiado de orientación vocacional con informe personal: tus intereses, aptitudes y personalidad, y las carreras que encajan contigo.', ['OrientaciónVocacional', 'Carreras', 'Estudiantes'], 'young student thinking future'),
 ('promo-colegios', 'mind', 'https://aurzane.com/colegios/', 'Orientación vocacional para colegios', ['Colegios y academias: orientación vocacional para todo el curso', 'Informes vocacionales para tus alumnos, sin papeleo', 'Ayuda a tus alumnos a elegir carrera'],
  'Para departamentos de orientación, colegios y academias: un proceso vocacional completo para tus alumnos, con informe personal y panel para el orientador.', ['Orientadores', 'Colegios', 'Educación'], 'teacher classroom'),
 ('promo-live', 'live', L + '/', 'LIVE: salud y bienestar', ['Cuida tu cuerpo con calculadoras fiables', 'Sueño, agua, calorías e IMC en un clic', 'Pequeños hábitos, grandes cambios'],
  'Calculadoras de salud, guías de hábitos y lecturas de bienestar con fuentes citadas. Gratis y sin registro.', ['Salud', 'Bienestar', 'Hábitos'], 'healthy breakfast fruit'),
 ('promo-build', 'build', B + '/', 'BUILD: dinero y vivienda', ['Haz números antes de decidir', 'Hipoteca, sueldo neto y finiquito, calculados en un minuto', 'Tus finanzas, claras y sin letra pequeña'],
  'Calculadoras de hipoteca, sueldo neto, finiquito, ahorro y alquiler, con guías que explican cada número. Gratis.', ['Finanzas', 'Hipoteca', 'Ahorro'], 'calculator coins desk'),
 ('promo-learn', 'learn', LE + '/', 'LEARN: cursos gratis con certificado', ['Aprende algo nuevo esta semana', 'Cursos gratis a tu ritmo', 'Formación gratuita, de verdad'],
  'Cursos gratuitos de neurociencia, psicología y más, organizados por temas y a tu ritmo.', ['Cursos', 'AprendeGratis', 'Formación'], 'student reading notes'),
 ('promo-biblioteca', 'aurzane', W + '/biblioteca/', 'Biblioteca AURZANE', ['Libros de psicología para leer gratis', 'Tu próxima lectura, gratis y legal', 'Biblioteca abierta: lee sin pagar'],
  'Libros con licencia abierta de psicología, neurociencia, salud, historia y más, para leer en línea sin pagar y sin registro.', ['LibrosGratis', 'Lectura', 'Psicología'], 'library bookshelves'),
 ('promo-aurzane', 'aurzane', W + '/', 'AURZANE: todo en un lugar', ['Psicología, estudios, salud y dinero en un solo sitio', 'Herramientas gratis para decidir mejor', 'Tu mente, tus estudios y tu vida, más claros'],
  'Tests de psicología, buscador de universidades, calculadoras de salud y finanzas, cursos y una biblioteca abierta. Todo gratis.', ['AURZANE', 'Psicología', 'Gratis'], 'sunrise mountains'),
  # SaludOnNet (Awin, 18/11/2026): llevan a tests y calculadoras que muestran, junto al resultado, la consulta con un profesional a precio cerrado
 ('promo-estres', 'mind', M + '/test-de-estres/', 'Test de estrés gratis', ['¿Es estrés o algo más? Compruébalo en 2 minutos', 'Mide tu estrés con el test que usan los psicólogos', 'Antes de pedir cita, haz este test gratis'],
  'Test de estrés validado, gratis y anónimo, con tu resultado explicado al momento. Si lo necesitas, te mostramos cómo hablar con un psicólogo en clínica o por videoconsulta, con precio cerrado y sin seguro.', ['SaludMental', 'Estrés', 'Psicología'], 'stressed woman laptop'),
 ('promo-chequeo', 'live', L + '/test-de-habitos/', 'Test de hábitos saludables', ['¿Cómo de sanos son tus hábitos?', 'Tu salud en 10 preguntas', 'Pequeños cambios que se notan'],
  'Sueño, alimentación, movimiento y descanso: descubre qué hábitos te ayudan y cuáles mejorar. Y si quieres un chequeo, análisis y especialistas a precio cerrado sin seguro médico.', ['Salud', 'Hábitos', 'Chequeo'], 'doctor consultation clinic'),
]
for i_, mu, url, tit, gan, tx, tags, fq in PROMOS:
    p(i_, 'promo', mu, url, tit, gan, tx, tags)
    P[-1]['foto_q'] = fq

json.dump({'productos': P}, open(os.path.join(os.path.dirname(__file__), 'fijos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(P), 'productos fijos')
