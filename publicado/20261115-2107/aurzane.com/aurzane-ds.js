/*
 * AURZANE · Sistema de diseño compartido (v3): cabecera única del ecosistema, buscador global (Ctrl+K),
 * enlace para saltar al contenido y arreglos de accesibilidad que no cambian contenidos ni lógica.
 * Lo carga aurzane-paleta.js en todas las páginas. No borra nada: la barra antigua solo se oculta.
 */
(function (w, d) {
  'use strict';
  if (w.AurzaneDS) return; w.AurzaneDS = 1;
  var host = location.hostname;
  if (!/(^|\.)aurzane\.com$/.test(host)) return;
  var ruta = location.pathname;
  /* páginas de trabajo interno o de prueba en curso: sin barra para no distraer */
  if (/^\/(admin|ai\/|panel\/)|admin-cursos|generar-informe|-cliente\.html$/.test(ruta)) return;
  var mundo = (host.match(/^(mind|nexus|live|learn|build|ovp)\./) || [])[1] || 'aurzane';

  var MUNDOS = [
    ['mind', 'MIND', 'Mente y tests'], ['nexus', 'NEXUS', 'Universidades'], ['live', 'LIVE', 'Bienestar y salud'],
    ['learn', 'LEARN', 'Cursos'], ['build', 'BUILD', 'Vivienda y dinero'], ['ovp', 'OVP', 'Orientación vocacional']
  ];
  var COLOR = { mind: 'var(--az-mind-c)', nexus: 'var(--az-nexus-c)', live: 'var(--az-live-c)', learn: 'var(--az-learn-c)', build: 'var(--az-build-c)', ovp: 'var(--az-ovp-c)', aurzane: 'var(--az-portada-c)' };
  /* índice del ecosistema: [título, url sin https, mundo, tipo, descripción, idioma] (generado del mapa del servidor) */
  var INDICE = [["Test de TDAH en adultos (ASRS v1.1 de la OMS)","mind.aurzane.com/test-de-tdah/","mind","Test","Haz el cribado de TDAH en adultos ASRS v1.1 de la Organización Mundial de la Salud: 6 preguntas, resultado al…","es"],["Test de ansiedad GAD-7","mind.aurzane.com/test-de-ansiedad/","mind","Test","Haz el test de ansiedad GAD-7, el cuestionario más usado por médicos y psicólogos. 7 preguntas, resultado al…","es"],["Test de autocompasión","mind.aurzane.com/test-de-autocompasion/","mind","Test","Haz el test de autocompasión de Kristin Neff en su versión breve validada en español: 12 frases, tu…","es"],["Test de autoeficacia","mind.aurzane.com/test-de-autoeficacia/","mind","Test","¿Confías en tu capacidad para resolver problemas? Haz el test de autoeficacia general de Schwarzer y…","es"],["Test de autoestima de Rosenberg","mind.aurzane.com/test-de-autoestima/","mind","Test","Haz el test de autoestima de Rosenberg, la escala más usada del mundo. 10 frases, puntuación al instante…","es"],["Test de bienestar emocional WHO-5","live.aurzane.com/test-de-bienestar/","live","Test","Haz el índice de bienestar WHO-5 de la Organización Mundial de la Salud en 1 minuto. Resultado de 0 a 100 al…","es"],["Test de burnout","mind.aurzane.com/test-de-burnout/","mind","Test","Haz el test de burnout del Copenhagen Burnout Inventory, de libre uso: 7 preguntas sobre el desgaste por tu…","es"],["Test de depresión PHQ-9","mind.aurzane.com/test-de-depresion/","mind","Test","Haz el test de depresión PHQ-9, el cuestionario que usan médicos y psicólogos. 9 preguntas, resultado al…","es"],["Test de estrés","mind.aurzane.com/test-de-estres/","mind","Test","¿Estás estresado/a? Haz el test de estrés de la escala DASS-21, de dominio público y validada en español: 7…","es"],["Test de hábitos saludables","live.aurzane.com/test-de-habitos/","live","Test","¿Qué tan saludable es tu estilo de vida? Test SLIQ validado en español: alimentación, ejercicio, alcohol…","es"],["Test de orientación vocacional","ovp.aurzane.com/","ovp","Test","Haz gratis un test de orientación vocacional completo y online: intereses (CHASIDE y Holland), autoconcepto…","es"],["Test de personalidad","mind.aurzane.com/test-de-personalidad/","mind","Test","Test de personalidad gratis basado en los Cinco Grandes (Big Five). Elige 20, 50 o 120 preguntas y descubre…","es"],["Test de resiliencia","mind.aurzane.com/test-de-resiliencia/","mind","Test","¿Cuánto te cuesta recuperarte de los golpes? Haz el test de resiliencia con la Brief Resilience Scale…","es"],["Test de satisfacción con la vida (felicidad)","mind.aurzane.com/test-de-satisfaccion-con-la-vida/","mind","Test","¿Qué tan satisfecho estás con tu vida? Haz la escala SWLS de Ed Diener, la más usada del mundo para medir la…","es"],["Test de soledad","mind.aurzane.com/test-de-soledad/","mind","Test","¿Te sientes solo/a? Haz el test de soledad de 3 preguntas basado en la escala UCLA, el que usan los estudios…","es"],["Test de sueño","live.aurzane.com/test-de-sueno/","live","Test","Chequeo de sueño en 2 minutos: cantidad, regularidad, calidad y hábitos según las recomendaciones de la…","es"],["Calculadora de IMC","live.aurzane.com/calculadora-imc/","live","Calculadora","Calcula tu IMC (índice de masa corporal) con tu peso y altura, mira en qué rango estás según la OMS y cuál es…","es"],["Calculadora de calorías e IMC","live.aurzane.com/calculadora-calorias/","live","Calculadora","Calcula cuántas calorías necesitas al día según tu edad, peso, altura y actividad, tu índice de masa corporal…","es"],["Calculadora de días entre fechas","live.aurzane.com/calculadora-dias-entre-fechas/","live","Calculadora","Calcula cuántos días, semanas y meses hay entre dos fechas, cuántos son laborables y cuánto falta para una…","es"],["Calculadora de edad exacta","live.aurzane.com/calculadora-edad/","live","Calculadora","Calcula tu edad exacta en años, meses y días, cuántos días has vivido y cuánto falta para tu próximo…","es"],["Calculadora de embarazo","live.aurzane.com/calculadora-embarazo/","live","Calculadora","Calcula de cuántas semanas estás y tu fecha probable de parto a partir de tu última regla, con el calendario…","es"],["Calculadora de hipoteca","build.aurzane.com/calculadora-hipoteca/","build","Calculadora","Calcula tu cuota de hipoteca fija o variable con el euríbor actual, los impuestos de tu comunidad (ITP o IVA…","es"],["Calculadora de interés compuesto","live.aurzane.com/calculadora-interes-compuesto/","live","Calculadora","Calcula cuánto crecen tus ahorros con el interés compuesto: capital inicial, aportación mensual, rentabilidad…","es"],["Calculadora de porcentajes","live.aurzane.com/calculadora-porcentajes/","live","Calculadora","Calcula porcentajes al instante: el X% de una cantidad, qué porcentaje es un número de otro, descuentos…","es"],["Calculadora de reforma","build.aurzane.com/calculadora-reforma/","build","Calculadora","Calcula cuánto cuesta reformar tu piso o casa en 2026 partida a partida: cocina, baños, electricidad…","es"],["Calculadora de sueldo neto","build.aurzane.com/calculadora-sueldo-neto/","build","Calculadora","Calcula tu sueldo neto mensual en 2026 a partir del bruto anual: retención de IRPF, cotización a la Seguridad…","es"],["Calculadora de nota PAU","nexus.aurzane.com/calculadora-nota-pau/","nexus","Calculadora","Calcula gratis tu nota de la PAU 2026 (selectividad, EBAU o EvAU): nota de acceso, nota de admisión sobre 14…","es"],["Calculadora de agua al día","live.aurzane.com/calculadora-agua/","live","Calculadora","¿Cuánta agua tienes que beber al día? Calcula los litros que necesitas según tu peso, tu actividad física y…","es"],["Coherencia cardiaca guiada: respiración 365 de 5 minutos","mind.aurzane.com/ejercicios/coherencia-cardiaca/","mind","Ejercicio","Practica la coherencia cardiaca guiada: 6 respiraciones por minuto (5 segundos inhalando y 5 exhalando)…","es"],["Escaneo corporal (body scan) guiado de 7 minutos","mind.aurzane.com/ejercicios/escaneo-corporal/","mind","Ejercicio","Haz un escaneo corporal o body scan guiado por voz de 7 minutos: recorre tu cuerpo con atención plena, de los…","es"],["Meditación guiada de 5 minutos: atención a la respiración","mind.aurzane.com/ejercicios/atencion-a-la-respiracion/","mind","Ejercicio","Medita 5 minutos con esta meditación guiada por voz de atención plena a la respiración, ideal para…","es"],["Pausa de autocompasión guiada de Kristin Neff","mind.aurzane.com/ejercicios/pausa-de-autocompasion/","mind","Ejercicio","Haz la pausa de autocompasión de Kristin Neff guiada por voz: reconoce que duele, recuerda que es humano y…","es"],["Relajación muscular progresiva de Jacobson guiada (8 min)","mind.aurzane.com/ejercicios/relajacion-muscular-progresiva/","mind","Ejercicio","Haz la relajación muscular progresiva de Jacobson guiada por voz: tensas y sueltas 11 grupos de músculos…","es"],["Respiración 4-7-8 guiada para dormir y calmar la ansiedad","mind.aurzane.com/ejercicios/respiracion-4-7-8/","mind","Ejercicio","Haz la respiración 4-7-8 del Dr. Andrew Weil guiada paso a paso, con temporizador, círculo animado y voz…","es"],["Respiración alterna (nadi shodhana) guiada","mind.aurzane.com/ejercicios/respiracion-alterna/","mind","Ejercicio","Haz la respiración alterna o nadi shodhana del yoga guiada: inhala por una fosa nasal y exhala por la otra…","es"],["Respiración cuadrada (box breathing) guiada","mind.aurzane.com/ejercicios/respiracion-cuadrada/","mind","Ejercicio","Haz la respiración cuadrada o box breathing guiada: inhala 4, mantén 4, exhala 4 y mantén 4, con…","es"],["Respiración diafragmática o abdominal guiada","mind.aurzane.com/ejercicios/respiracion-diafragmatica/","mind","Ejercicio","Aprende la respiración diafragmática o abdominal guiada: inhala 4 segundos llevando el aire a la tripa y…","es"],["Suspiro cíclico (physiological sigh) guiado","mind.aurzane.com/ejercicios/suspiro-ciclico/","mind","Ejercicio","Haz el suspiro cíclico o physiological sigh guiado: dos inhalaciones seguidas por la nariz y una espiración…","es"],["Técnica 5-4-3-2-1 guiada para la ansiedad (grounding)","mind.aurzane.com/ejercicios/tecnica-5-4-3-2-1/","mind","Ejercicio","Haz la técnica 5-4-3-2-1 guiada por voz: nombra 5 cosas que ves, 4 que tocas, 3 que oyes, 2 que hueles y 1…","es"],["Técnica STOP de mindfulness guiada (1 minuto)","mind.aurzane.com/ejercicios/tecnica-stop/","mind","Ejercicio","Haz la técnica STOP de mindfulness guiada en 1 minuto: para, toma aire, observa y prosigue. Para no…","es"],["Visualización guiada del lugar seguro (5 min)","mind.aurzane.com/ejercicios/lugar-seguro/","mind","Ejercicio","Haz una visualización guiada por voz de tu lugar seguro: imagina con todos los sentidos un sitio donde te…","es"],["Curso de Introducción a la Psicología","learn.aurzane.com/curso/introduccion-psicologia/","learn","Curso","Haz este curso de introducción a la psicología gratis y online. 20 horas, 16 temas desde las bases biológicas…","es"],["Curso de ansiedad","learn.aurzane.com/curso/ansiedad-dia-a-dia/","learn","Curso","Haz este curso online gratuito de 4 horas para gestionar la ansiedad diaria, calmar el cuerpo y afrontar lo…","es"],["Curso de neuroanatomía funcional","learn.aurzane.com/curso/neuroanatomia-funcional/","learn","Curso","Domina la neuroanatomía funcional con este curso online avanzado de 24 horas. Estudia el sistema nervioso…","es"],["Investigación en Neurociencias y Estereotaxia","learn.aurzane.com/curso/tecnicas-neurociencias/","learn","Curso","Domina la estereotaxia cerebral y técnicas de terapia celular en neurociencias con este curso online avanzado…","es"],["Biblioteca académica de BUILD","build.aurzane.com/build-biblioteca.html","build","Biblioteca","Índice de investigación abierta sobre historia, imperios y civilizaciones antiguas de los 5 continentes —…","es"],["Biblioteca académica de LEARN","learn.aurzane.com/learn-biblioteca.html","learn","Biblioteca","Índice de investigación abierta sobre ciencia del aprendizaje y educación — 5.000 artículos científicos de…","es"],["Biblioteca académica de LIVE","live.aurzane.com/live-biblioteca.html","live","Biblioteca","Índice de investigación abierta sobre bienestar, propósito y vida plena — 5.000 artículos científicos de…","es"],["Biblioteca académica de NEXUS","nexus.aurzane.com/nexus-biblioteca.html","nexus","Biblioteca","Índice de investigación abierta sobre tecnología y salud — 5.000 artículos científicos de acceso abierto, con…","es"],["Biblioteca académica de MIND","mind.aurzane.com/mind-biblioteca.html","mind","Biblioteca","Índice de investigación abierta sobre orientación vocacional, psicología educativa, hábitos de estudio y…","es"],["Research Hub","aurzane.com/research.html","aurzane","Biblioteca","Un solo buscador para las cinco bibliotecas académicas de AURZANE: 25.000 artículos científicos de acceso…","es"],["13 ejercicios de relajación y respiración guiados gratis","mind.aurzane.com/ejercicios/","mind","Página","Ejercicios de relajación, respiración, mindfulness y grounding guiados por voz y con temporizador…","es"],["Inicio de BUILD","build.aurzane.com/","build","Página","La biblioteca de BUILD: guías originales con fuentes verificables sobre bienes raíces, urbanismo…","es"],["Inicio de LEARN","learn.aurzane.com/","learn","Página","El área educativa de AURZANE: una biblioteca real de guías originales sobre aprendizaje adulto, dominio de…","es"],["Inicio de LIVE","live.aurzane.com/","live","Página","Artículos breves y con fuentes reales sobre bienestar, propósito, equilibrio vida-trabajo, hábitos, aventura…","es"],["Inicio de MIND","mind.aurzane.com/","mind","Página","Guías breves y con fuentes reales sobre orientación vocacional, elección de carrera, métodos de estudio…","es"],["Inicio de NEXUS","nexus.aurzane.com/","nexus","Página","El mundo NEXUS de AURZANE: un catálogo de 6.411 universidades de 55 países, artículos originales con fuentes…","es"],["Inicio de AURZANE","aurzane.com/","aurzane","Página","Tests psicológicos gratis (personalidad, bienestar, sueño, vocacional), calculadoras de hipoteca y reforma y…","es"],["Buscador de universidades y carreras gratis","nexus.aurzane.com/universidades/","nexus","Página","Buscador de universidades gratis: 6.411 universidades e institutos de 55 países y 109.967 carreras. España…","es"],["Certificados","learn.aurzane.com/certificado/","learn","Página","Obtén y verifica los certificados de aprovechamiento de los cursos de AURZANE LEARN. Formación libre y no…","es"],["Contacto","aurzane.com/contacto.html","aurzane","Página","Escribe a AURZANE: dudas, errores en un contenido, privacidad, retirada de contenidos, colegios y…","es"],["Cursos","learn.aurzane.com/cursos/","learn","Página","Cursos online gratuitos en español de psicología, bienestar y neurociencias, con tests, tarjetas de repaso y…","es"],["Frases célebres para pensar y sentirte mejor","aurzane.com/frases/","aurzane","Página","439 frases célebres de autores clásicos sobre la vida, la esperanza, la calma y la superación. Cada día…","es"],["Informe de ejemplo","ovp.aurzane.com/informe-ejemplo.html","ovp","Página","Ejemplo completo, con datos ficticios, del informe de orientación vocacional que AURZANE OVP entrega a cada…","es"],["Mapa de AURZANE","aurzane.com/mapa/","aurzane","Página","Todas las páginas de AURZANE en un solo lugar: tests, calculadoras, ejercicios, universidades, cursos y…","es"],["Mi AURZANE","aurzane.com/mi-aurzane.html","aurzane","Página","Inicia sesión con AURZANE ID: una sola cuenta para MIND, NEXUS, LIVE, LEARN y BUILD.","es"],["Mi proceso OVP","ovp.aurzane.com/portal.html","ovp","Página","Tu proceso de orientación vocacional AURZANE OVP: evaluaciones gratuitas e informe automático en un solo…","es"],["Novedades de AURZANE","aurzane.com/novedades/","aurzane","Página","Todo lo nuevo de AURZANE: tests, calculadoras, ejercicios guiados, cursos, libros y artículos, actualizado…","es"],["Orientación vocacional para colegios","aurzane.com/colegios/","aurzane","Página","Evaluación vocacional en línea para todo el bachillerato: seis instrumentos, informe automático firmado por…","es"],["Sobre AURZANE","aurzane.com/sobre-aurzane.html","aurzane","Página","Quién está detrás de AURZANE, cómo preparamos los contenidos de psicología, bienestar y orientación…","es"],["Amarse con los ojos abiertos","aurzane.com/biblioteca/libro/ref-amarse-ojos-abiertos.html","aurzane","Libro","Resumen de Amarse con los ojos abiertos, de Jorge Bucay y Silvia Salinas: de qué trata, ideas clave sobre la…","es"],["Déjame que te cuente (Jorge Bucay)","aurzane.com/biblioteca/libro/ref-dejame-que-te-cuente.html","aurzane","Libro","Resumen de Déjame que te cuente, de Jorge Bucay: de qué trata, cuentos más conocidos como El elefante…","es"],["El camino de las lágrimas","aurzane.com/biblioteca/libro/ref-camino-lagrimas.html","aurzane","Libro","Resumen de El camino de las lágrimas, de Jorge Bucay: qué dice sobre el duelo, ideas clave para atravesar una…","es"],["El niño, el topo, el zorro y el caballo","aurzane.com/biblioteca/libro/ref-nino-topo-zorro-caballo.html","aurzane","Libro","De qué trata El niño, el topo, el zorro y el caballo, de Charlie Mackesy: mensajes sobre amistad, valentía y…","es"],["El proceso de convertirse en persona","aurzane.com/biblioteca/libro/ref-proceso-convertirse-persona.html","aurzane","Libro","Resumen de El proceso de convertirse en persona, de Carl Rogers: ideas clave de la terapia centrada en la…","es"],["Los dones de la imperfección","aurzane.com/biblioteca/libro/ref-dones-imperfeccion.html","aurzane","Libro","Resumen de Los dones de la imperfección, de Brené Brown: las 10 guías para vivir de corazón, ideas clave…","es"],["Paula (Isabel Allende)","aurzane.com/biblioteca/libro/ref-paula.html","aurzane","Libro","Resumen de Paula, de Isabel Allende: de qué trata, ideas clave sobre el duelo y la memoria, para quién es y…","es"],["Recuerda que vas a morir. Vive","aurzane.com/biblioteca/libro/ref-recuerda-que-vas-a-morir.html","aurzane","Libro","Resumen de Recuerda que vas a morir. Vive, de Paul Kalanithi: de qué trata, ideas clave sobre el sentido de…","es"],["Volar sobre el pantano","aurzane.com/biblioteca/libro/ref-volar-sobre-pantano.html","aurzane","Libro","Resumen de Volar sobre el pantano, de Carlos Cuauhtémoc Sánchez: de qué trata, temas, mensaje, para quién es…","es"],["Aviso de Privacidad","aurzane.com/privacidad.html","aurzane","Legal","Qué datos recopila AURZANE OVP, para qué se usan, quién tiene acceso y cuáles son tus derechos sobre tu…","es"],["Aviso legal de AURZANE","aurzane.com/aviso-legal.html","aurzane","Legal","Datos del titular de aurzane.com, condiciones de uso del sitio y propiedad intelectual.","es"],["Condiciones de uso","aurzane.com/condiciones.html","aurzane","Legal","Condiciones de uso de aurzane.com y sus subdominios: contenido orientativo, cuenta de Mi AURZANE, orientación…","es"],["Política de cookies de AURZANE","aurzane.com/cookies.html","aurzane","Legal","Qué cookies usa AURZANE, para qué sirven, cuánto duran y cómo cambiar tu elección.","es"],["Política editorial de AURZANE","aurzane.com/politica-editorial.html","aurzane","Legal","Cómo se crean, revisan y corrigen los contenidos de AURZANE: fuentes, tests validados, uso de inteligencia…","es"],["Anxiety test (GAD-7)","mind.aurzane.com/en/anxiety-test-gad-7/","mind","Test","Take the GAD-7, the most widely used anxiety questionnaire in primary care. 7 questions, instant score with a…","en"],["Depression test (PHQ-9)","mind.aurzane.com/en/depression-test-phq-9/","mind","Test","Take the PHQ-9, the standard depression screening questionnaire used by doctors. 9 questions, instant score…","en"],["Life satisfaction test (SWLS)","mind.aurzane.com/en/life-satisfaction-test-swls/","mind","Test","Take the Satisfaction With Life Scale (Diener), the classic measure of how satisfied you are with your life.…","en"],["Resilience test (Brief Resilience Scale)","mind.aurzane.com/en/resilience-test-brs/","mind","Test","Take the Brief Resilience Scale (Smith et al.), which measures your ability to bounce back from stress. 6…","en"],["Self-compassion test (Neff, short form)","mind.aurzane.com/en/self-compassion-test-scs-sf/","mind","Test","Take the Self-Compassion Scale short form by Kristin Neff. 12 statements, instant result with an explanation.…","en"],["Self-efficacy test (General Self-Efficacy Scale)","mind.aurzane.com/en/self-efficacy-test-gse/","mind","Test","Take the General Self-Efficacy Scale (Schwarzer and Jerusalem): how confident you are in handling difficult…","en"],["Self-esteem test (Rosenberg)","mind.aurzane.com/en/self-esteem-test-rosenberg/","mind","Test","Take the Rosenberg Self-Esteem Scale, the most used self-esteem questionnaire in the world. 10 statements…","en"],["Stress test (DASS-21 stress scale)","mind.aurzane.com/en/stress-test-dass-21/","mind","Test","Take the stress scale of the DASS-21, a widely used and validated questionnaire. 7 statements about the past…","en"],["Teste de ansiedade (GAD-7)","mind.aurzane.com/pt/teste-de-ansiedade-gad-7/","mind","Test","Faça o GAD-7, o questionário de ansiedade mais usado na atenção primária. 7 perguntas, resultado imediato e…","pt"],["Teste de bem-estar (WHO-5)","mind.aurzane.com/pt/teste-de-bem-estar-who-5/","mind","Test","Faça o Índice de Bem-Estar WHO-5 da Organização Mundial da Saúde. 5 afirmações sobre as últimas duas semanas…","pt"],["Teste de depressão (PHQ-9)","mind.aurzane.com/pt/teste-de-depressao-phq-9/","mind","Test","Faça o PHQ-9, o questionário de rastreamento de depressão usado por médicos. 9 perguntas, resultado imediato…","pt"],["Wellbeing test (WHO-5)","mind.aurzane.com/en/wellbeing-test-who-5/","mind","Test","Take the WHO-5 Well-Being Index from the World Health Organization. 5 statements about the last two weeks…","en"],["Work burnout test (Copenhagen Burnout Inventory)","mind.aurzane.com/en/burnout-test-cbi/","mind","Test","Take the work-related scale of the Copenhagen Burnout Inventory, a free and validated burnout questionnaire.…","en"],["Free psychological tests in English","mind.aurzane.com/en/","mind","Página","Validated psychological questionnaires in their original English version: anxiety, depression, self-esteem…","en"],["Testes psicológicos grátis em português","mind.aurzane.com/pt/","mind","Página","Questionários psicológicos validados em português: ansiedade (GAD-7), depressão (PHQ-9) e bem-estar (WHO-5).…","pt"],["Biblioteca de libros","aurzane.com/biblioteca/","aurzane","Biblioteca","Libros abiertos de psicología para leer gratis","es"],["Artículos","aurzane.com/articulos/","aurzane","Página","Guías con fuentes citadas","es"],["Artículos de NEXUS","nexus.aurzane.com/nexus.html","nexus","Página","Un catálogo abierto y con fuentes reales sobre cómo la tecnología, la inteligencia artificial y los datos…","es"]];

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function sinTildes(t) { return String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  var ICO_LUPA = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
  var ICO_PERSONA = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>';
  var ICO_MUNDOS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/></svg>';

  /* ---------- 1. Enlace para saltar al contenido ---------- */
  function saltar() {
    if (d.querySelector('.az-saltar,.skip-link,a[href="#main"],a[href="#contenido"]')) return;
    var dest = d.querySelector('main') || d.querySelector('h1');
    if (!dest) return;
    if (!dest.id) dest.id = 'az-contenido';
    if (!dest.hasAttribute('tabindex')) dest.setAttribute('tabindex', '-1');
    var a = d.createElement('a'); a.className = 'az-saltar'; a.href = '#' + dest.id; a.textContent = 'Saltar al contenido';
    d.body.insertBefore(a, d.body.firstChild);
  }

  /* ---------- 2. Cabecera única del ecosistema ----------
     Una sola cabecera por página (pautas de NN/g sobre navegación universal y local):
     fila 1, sutil: AURZANE, los mundos, buscar, cuenta y tema; fila 2: las secciones del mundo en el que estás.
     Sustituye a la barra de mundos, a la cabecera propia de cada página y a los paneles «Todo», que repetían enlaces. */
  var LOCAL = {
    aurzane: { n: 'Conocimiento', u: 'https://aurzane.com/biblioteca/', l: [['Biblioteca de libros', 'https://aurzane.com/biblioteca/'], ['Libros recomendados', 'https://aurzane.com/libros/'], ['Artículos', 'https://aurzane.com/articulos/'], ['Research Hub', 'https://aurzane.com/research.html'], ['Frases', 'https://aurzane.com/frases/'], ['Novedades', 'https://aurzane.com/novedades/']] },
    mind: { n: 'MIND', u: 'https://mind.aurzane.com/', l: [['Tests', 'https://mind.aurzane.com/#tests'], ['Test de personalidad', 'https://mind.aurzane.com/test-de-personalidad/'], ['Ejercicios guiados', 'https://mind.aurzane.com/ejercicios/'], ['Guías', 'https://mind.aurzane.com/#recentSection'], ['Biblioteca', 'https://mind.aurzane.com/mind-biblioteca.html'], ['Guardados', 'https://mind.aurzane.com/#guardados', 'g']] },
    nexus: { n: 'NEXUS', u: 'https://nexus.aurzane.com/', l: [['Universidades', 'https://nexus.aurzane.com/universidades/'], ['¿Qué puedo estudiar?', 'https://nexus.aurzane.com/universidades/que-puedo-estudiar/'], ['Notas de corte', 'https://nexus.aurzane.com/universidades/notas-de-corte/'], ['Nota PAU', 'https://nexus.aurzane.com/calculadora-nota-pau/'], ['Artículos', 'https://nexus.aurzane.com/nexus.html'], ['Biblioteca', 'https://nexus.aurzane.com/nexus-biblioteca.html']] },
    live: { n: 'LIVE', u: 'https://live.aurzane.com/', l: [['Tests y calculadoras', 'https://live.aurzane.com/#tests'], ['Test de bienestar', 'https://live.aurzane.com/test-de-bienestar/'], ['Test de sueño', 'https://live.aurzane.com/test-de-sueno/'], ['Artículos', 'https://live.aurzane.com/#recentSection'], ['Biblioteca', 'https://live.aurzane.com/live-biblioteca.html'], ['Guardados', 'https://live.aurzane.com/#guardados', 'g']] },
    learn: { n: 'LEARN', u: 'https://learn.aurzane.com/', l: [['Cursos', 'https://learn.aurzane.com/cursos/'], ['Certificados', 'https://learn.aurzane.com/certificado/'], ['Guías', 'https://learn.aurzane.com/#recentSection'], ['Biblioteca', 'https://learn.aurzane.com/learn-biblioteca.html'], ['Guardados', 'https://learn.aurzane.com/#guardados', 'g']] },
    build: { n: 'BUILD', u: 'https://build.aurzane.com/', l: [['Hipoteca', 'https://build.aurzane.com/calculadora-hipoteca/'], ['Sueldo neto', 'https://build.aurzane.com/calculadora-sueldo-neto/'], ['Reforma', 'https://build.aurzane.com/calculadora-reforma/'], ['Guías', 'https://build.aurzane.com/#recentSection'], ['Biblioteca', 'https://build.aurzane.com/build-biblioteca.html'], ['Guardados', 'https://build.aurzane.com/#guardados', 'g']] },
    ovp: { n: 'OVP', u: 'https://ovp.aurzane.com/', l: [['Cómo funciona', 'https://ovp.aurzane.com/'], ['Mi proceso', 'https://ovp.aurzane.com/portal.html'], ['Informe de ejemplo', 'https://ovp.aurzane.com/informe-ejemplo.html'], ['Para colegios', 'https://aurzane.com/colegios/']] }
  };
  var esPortada = mundo === 'aurzane' && /^\/(index\.html)?$/.test(ruta);
  /* en aurzane.com la segunda fila es la del área Conocimiento; la cuenta, el contacto o lo legal no la necesitan */
  var sinFilaLocal = mundo === 'aurzane' && !/^\/(biblioteca|libros|articulos|articulos-ai|research|frases|novedades|temas|mapa)\b/.test(ruta);
  /* tests en inglés y portugués: su propia navegación, en su idioma */
  if (mundo === 'mind' && /^\/en\//.test(ruta)) LOCAL.mind = { n: 'MIND · English', u: 'https://mind.aurzane.com/en/', l: [['All tests', 'https://mind.aurzane.com/en/'], ['Español', 'https://mind.aurzane.com/']] };
  if (mundo === 'mind' && /^\/pt\//.test(ruta)) LOCAL.mind = { n: 'MIND · Português', u: 'https://mind.aurzane.com/pt/', l: [['Todos os testes', 'https://mind.aurzane.com/pt/'], ['Español', 'https://mind.aurzane.com/']] };

  function sesion() {   /* nombre de quien ha iniciado sesión con AURZANE ID (cookie compartida de .aurzane.com) */
    try {
      var leer = function (n) { var m = d.cookie.match(new RegExp('(?:^|; )' + n.replace(/\./g, '\\.') + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : null; };
      var v = leer('aurzane-id-auth');
      if (v === null) { var t = [], i = 0, x; while ((x = leer('aurzane-id-auth.' + i)) !== null) { t.push(x); i++; } v = t.length ? t.join('') : null; }
      if (!v) return null;
      var s = JSON.parse(v), u = s && (s.user || (s.currentSession && s.currentSession.user));
      if (!u || (s.expires_at && s.expires_at * 1000 < Date.now() - 864e5 * 30)) return null;
      var md = u.user_metadata || {};
      return String(md.nombre || md.name || md.full_name || (u.email || '').split('@')[0] || '').split(' ')[0] || null;
    } catch (e) { return null; }
  }
  function actual(u) {
    var a = d.createElement('a'); a.href = u;
    if (a.hostname !== host) return false;
    if (a.hash && a.hash !== '#') return a.pathname === ruta && location.hash === a.hash;
    var p = a.pathname.replace(/index\.html$/, '');
    return p !== '/' ? ruta.replace(/index\.html$/, '').indexOf(p) === 0 : false;
  }
  function ocultarViejas() {
    var sel = [
      'body > .utility', '.utility[data-nosnippet]', '#utilityBar',
      'body > header.topbar', 'body > div.topbar:has(.brand)', 'body > header.top', 'body > .w > nav.top', 'body > header:not([class]):has(> .w > .logo)',
      '.btn-todo', '.todo-panel', '.todo-overlay', 'header.principal', 'footer.pie-mind', 'footer.pie-live', 'footer.pie-nexus', 'footer.pie-learn', 'footer.pie-build'
    ];
    sel.forEach(function (s) { try { Array.prototype.forEach.call(d.querySelectorAll(s), function (e) { if (!e.closest('.az-cab')) { e.classList.add('az-vieja'); e.setAttribute('aria-hidden', 'true'); e.inert = true; } }); } catch (x) {} });
    /* plantillas con cabecera funcional: se conserva la herramienta y se quita solo lo repetido */
    var bib = d.querySelector('header.cabecera'); if (bib) bib.classList.add('az-cab-funcional');
    var uni = d.querySelector('nav.topnav#topnav'); if (uni && uni.closest('.az-vieja')) { var sub = d.createElement('nav'); sub.className = 'az-subnav'; sub.setAttribute('aria-label', uni.getAttribute('aria-label') || 'Sección'); var din = d.createElement('div'); din.className = 'az-subnav-in';
      var ya = (LOCAL[mundo] ? LOCAL[mundo].l : []).map(function (x) { var a = d.createElement('a'); a.href = x[1]; return a.pathname; });
      Array.prototype.forEach.call(uni.querySelectorAll('a'), function (a) { if (/mi-aurzane/.test(a.href) || ya.indexOf(a.pathname) >= 0) return; din.appendChild(a.cloneNode(true)); });
      sub.appendChild(din); return din.children.length ? sub : null; }
    if (/^\/research(\.html)?$/.test(ruta)) { var tb = d.querySelector('body > .topbar'); if (tb) { tb.classList.remove('az-vieja'); tb.removeAttribute('aria-hidden'); tb.inert = false; tb.classList.add('az-cab-funcional'); } }
    return null;
  }
  function barra() {
    if (d.querySelector('.az-cab')) return;
    if (/^\/cursos\.html$/.test(ruta) && mundo === 'learn') return;   /* el aula del curso tiene su propia barra de trabajo */
    var tema = d.getElementById('btnTema') || d.getElementById('btnTemaMi');
    var guard = d.getElementById('savedCount');
    var subnav = ocultarViejas();
    var L = LOCAL[mundo], nombre = sesion();
    var cab = d.createElement('header'); cab.className = 'az-cab'; cab.setAttribute('data-nosnippet', '');
    var mundos = MUNDOS.map(function (x) {
      return '<li><a href="https://' + x[0] + '.aurzane.com/" style="--c:' + COLOR[x[0]] + '"' + (x[0] === mundo ? ' aria-current="true"' : '') + '><i aria-hidden="true"></i><span>' + x[1] + '</span><small>' + x[2] + '</small></a></li>';
    }).join('');
    var locales = (L && !esPortada && !sinFilaLocal) ? L.l.map(function (x) {
      return '<li><a href="' + x[1] + '"' + (actual(x[1]) ? ' aria-current="page"' : '') + (x[2] === 'g' ? ' class="az-guard"' : '') + '>' + esc(x[0]) + (x[2] === 'g' ? ' <span class="az-n" hidden></span>' : '') + '</a></li>';
    }).join('') : '';
    cab.innerHTML =
      '<div class="az-cab-1"><div class="az-cab-in">' +
        '<a class="az-logo" href="https://aurzane.com/"' + (esPortada ? ' aria-current="page"' : '') + '>AUR<b>Z</b>ANE</a>' +
        (L && !esPortada && mundo !== 'aurzane' ? '<a class="az-donde" href="' + L.u + '" style="--c:' + COLOR[mundo] + '"><i aria-hidden="true"></i>' + esc(L.n.split(' ')[0]) + '</a>' : '') +
        '<nav class="az-mundos" aria-label="Mundos de AURZANE"><ul>' + mundos + '</ul></nav>' +
        '<div class="az-acc">' +
          '<button type="button" class="az-buscar" aria-haspopup="dialog" aria-label="Buscar en AURZANE">' + ICO_LUPA + '<span class="txt">Buscar en AURZANE</span><kbd>Ctrl K</kbd></button>' +
          '<a class="az-btn az-cuenta" href="https://aurzane.com/mi-aurzane.html"' + (/mi-aurzane/.test(ruta) ? ' aria-current="page"' : '') + (nombre ? ' aria-label="Mi AURZANE: ' + esc(nombre) + '"' : '') + '>' + ICO_PERSONA + '<span class="txt">' + (nombre ? esc(nombre) : 'Mi AURZANE') + '</span></a>' +
          '<span class="az-tema-hueco"></span>' +
          '<button type="button" class="az-btn az-menu" aria-expanded="false" aria-controls="azCajon" aria-label="Menú"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>' +
        '</div></div></div>' +
      (locales ? '<div class="az-cab-2" style="--c:' + COLOR[mundo] + '"><div class="az-cab-in"><a class="az-mundo" href="' + L.u + '"><i aria-hidden="true"></i>' + esc(L.n) + '</a><nav aria-label="' + esc(L.n) + '"><ul>' + locales + '</ul></nav></div></div>' : '') +
      '<div class="az-cajon" id="azCajon" hidden>' +
        (locales ? '<p class="az-cajon-t">' + esc(L.n) + '</p><ul>' + locales + '</ul>' : '') +
        '<p class="az-cajon-t">Tu cuenta</p><ul><li><a href="https://aurzane.com/mi-aurzane.html">' + ICO_PERSONA + (nombre ? esc(nombre) + ' · Mi AURZANE' : 'Mi AURZANE') + '</a></li></ul>' +
        '<p class="az-cajon-t">Mundos</p><ul class="az-cajon-mundos"><li><a href="https://aurzane.com/"><i aria-hidden="true" style="--c:var(--az-portada-c)"></i>Inicio de AURZANE</a></li>' + mundos + '</ul>' +
      '</div>';
    if (tema && !tema.closest('.todo-panel')) {
      tema.classList.add('az-tema');
      if (!tema.getAttribute('aria-label')) tema.setAttribute('aria-label', 'Cambiar entre tema claro y oscuro');
      tema.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor"/></svg><span class="txt">Tema</span>';
      tema.removeAttribute('aria-hidden'); tema.inert = false;
      cab.querySelector('.az-tema-hueco').replaceWith(tema);
    }
    d.documentElement.classList.add('az-ds', 'az-ds-' + mundo); if (mundo !== 'aurzane' && /^\/(index\.html)?$/.test(ruta)) d.documentElement.classList.add('az-pm');
    d.body.insertBefore(cab, d.body.firstChild);
    if (subnav) cab.parentNode.insertBefore(subnav, cab.nextSibling);
    var saltarA = d.querySelector('.az-saltar'); if (saltarA) d.body.insertBefore(saltarA, d.body.firstChild);
    /* guardados del mundo: número real de lo guardado en este navegador */
    try { var g = JSON.parse(localStorage.getItem('aurzane-' + mundo + '-guardados') || '[]'); Array.prototype.forEach.call(cab.querySelectorAll('.az-guard .az-n'), function (n) { if (g.length) { n.textContent = g.length; n.hidden = false; } }); } catch (e) {}
    if (guard && w.MutationObserver) new MutationObserver(function () { Array.prototype.forEach.call(cab.querySelectorAll('.az-guard .az-n'), function (n) { var v = (guard.textContent || '').trim(); n.textContent = v; n.hidden = !v || v === '0'; }); }).observe(guard, { childList: true, characterData: true, subtree: true });
    /* menú del móvil */
    var bm = cab.querySelector('.az-menu'), caj = cab.querySelector('.az-cajon');
    function cerrarCaj() { caj.hidden = true; bm.setAttribute('aria-expanded', 'false'); cab.classList.remove('abierto'); }
    bm.addEventListener('click', function () { var abrirlo = caj.hidden; caj.hidden = !abrirlo; bm.setAttribute('aria-expanded', abrirlo); cab.classList.toggle('abierto', abrirlo); if (abrirlo) { var p = caj.querySelector('a'); if (p) p.focus(); } });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !caj.hidden) { cerrarCaj(); bm.focus(); } });
    d.addEventListener('click', function (e) { if (!caj.hidden && !cab.contains(e.target)) cerrarCaj(); });
    caj.addEventListener('click', function (e) { if (e.target.closest('a')) cerrarCaj(); });
    cab.querySelector('.az-buscar').addEventListener('click', function () { abrir(this); });
    /* la sesión puede abrirse o cerrarse en esta misma página */
    var pill = d.getElementById('pillCuenta'), txt = cab.querySelector('.az-cuenta .txt');
    if (pill && w.MutationObserver) new MutationObserver(function () { var t = (pill.textContent || '').replace(/👤/g, '').trim(); if (t && !/^mi aurzane$/i.test(t)) txt.textContent = t; }).observe(pill, { childList: true, characterData: true, subtree: true });
    /* los anclajes #tests de MIND y LIVE apuntan al primer bloque de tests de su portada */
    if (!d.getElementById('tests')) { var h2 = Array.prototype.filter.call(d.querySelectorAll('h2'), function (h) { return /^Tests?\b/.test(h.textContent.trim()); })[0]; var sec = h2 && (h2.closest('section') || h2); if (sec && !sec.id) sec.id = 'tests'; }
  }

  /* ---------- 2b. Pie único: el mismo en todas las páginas ----------
     Los pies de cada plantilla conservan sus avisos (método, licencias, aviso clínico) pero pierden los enlaces
     que el pie común ya da, y desaparece la fila legal añadida aparte. */
  function pie() {
    if (d.querySelector('.az-pie') || (/^\/cursos\.html$/.test(ruta) && mundo === 'learn')) return;
    var REP = /^https?:\/\/(?:(?:mind|nexus|live|learn|build|ovp)\.)?aurzane\.com\/?(?:index\.html)?$|\/(?:privacidad|condiciones|cookies|aviso-legal|sobre-aurzane|contacto|politica-editorial)\.html$/;
    Array.prototype.forEach.call(d.querySelectorAll('footer'), function (f) {
      if (f.closest('.az-pie')) return;
      Array.prototype.forEach.call(f.querySelectorAll('a[href]'), function (a) { if (REP.test(a.href)) a.classList.add('az-vieja'); });
      setTimeout(function () { var t = (f.innerText || '').trim(); if (t.length < 120 && /©/.test(t) && !f.querySelector('form,button:not(.az-fallo),img,input')) f.classList.add('az-vieja'); }, 0);
      Array.prototype.forEach.call(f.querySelectorAll('nav,ul,div,p,span'), function (e) { if (!e.textContent.replace(/[\s·|/©]+/g, '').length || (e.querySelectorAll('a').length && e.querySelectorAll('a:not(.az-vieja)').length === 0 && !e.textContent.replace(/[\s·|/]+/g, '').replace(Array.prototype.map.call(e.querySelectorAll('a'), function (a) { return a.textContent.replace(/[\s·|/]+/g, ''); }).join(''), '').length)) e.classList.add('az-vieja'); });
    });
    var ano = new Date().getFullYear();
    var col = function (t, l) { return '<div><p class="az-pie-t">' + t + '</p><ul>' + l.map(function (x) { return '<li><a href="' + x[1] + '"' + (/^https?:\/\/(?!(?:[a-z]+\.)?aurzane\.com)/.test(x[1]) ? ' rel="noopener" target="_blank"' : '') + '>' + x[0] + '</a></li>'; }).join('') + '</ul></div>'; };
    var p = d.createElement('footer'); p.className = 'az-pie'; p.setAttribute('data-nosnippet', '');
    p.innerHTML = '<div class="az-pie-in">' +
      '<div class="az-pie-marca"><a class="az-logo" href="https://aurzane.com/">AUR<b>Z</b>ANE</a><p>Psicología, aprendizaje y bienestar con base científica. Tests, cursos y herramientas gratis, creados y revisados por un psicólogo clínico.</p>' +
      '<p class="az-pie-redes">' + [['Instagram', 'https://www.instagram.com/aurzane/'], ['YouTube', 'https://www.youtube.com/@AURZANE'], ['Telegram', 'https://t.me/aurzane'], ['Facebook', 'https://www.facebook.com/profile.php?id=61595806065060'], ['Pinterest', 'https://www.pinterest.com/aurzane08/'], ['Bluesky', 'https://bsky.app/profile/aurzane.bsky.social'], ['Mastodon', 'https://mastodon.social/@auzane']].map(function (x) { return '<a href="' + x[1] + '" rel="noopener me" target="_blank">' + x[0] + '</a>'; }).join('') + '</p></div>' +
      col('Mundos', MUNDOS.map(function (x) { return [x[1] + ' <small>' + x[2] + '</small>', 'https://' + x[0] + '.aurzane.com/']; })) +
      col('Conocimiento', LOCAL.aurzane.l.slice(0, 5)) +
      col('AURZANE', [['Mi AURZANE', 'https://aurzane.com/mi-aurzane.html'], ['Sobre AURZANE', 'https://aurzane.com/sobre-aurzane.html'], ['Política editorial', 'https://aurzane.com/politica-editorial.html'], ['Contacto', 'https://aurzane.com/contacto.html'], ['Mapa del sitio', 'https://aurzane.com/mapa/'], ['Apoya AURZANE', 'https://ko-fi.com/adriansan7']]) +
      '</div><div class="az-pie-legal"><span>© ' + ano + ' AURZANE · Contenido orientativo: no sustituye la valoración de un profesional.</span>' +
      '<span>' + [['Privacidad', 'privacidad.html'], ['Cookies', 'cookies.html'], ['Condiciones de uso', 'condiciones.html'], ['Aviso legal', 'aviso-legal.html']].map(function (x) { return '<a href="https://aurzane.com/' + x[1] + '">' + x[0] + '</a>'; }).join('') + '</span></div>';
    var fallo = d.querySelector('.az-fallo');
    d.body.appendChild(p);
    if (fallo) p.querySelector('.az-pie-legal').appendChild(fallo);
    else if (w.MutationObserver) { var mo = new MutationObserver(function () { var f = d.querySelector('footer:not(.az-pie) .az-fallo'); if (f) { p.querySelector('.az-pie-legal').appendChild(f); mo.disconnect(); } }); mo.observe(d.body, { childList: true, subtree: true }); setTimeout(function () { mo.disconnect(); }, 8000); }
  }


  /* ---------- 2c. Portadas de mundo sin repeticiones ----------
     «Sigue explorando en otros mundos» repetía la cabecera, y «Lo que X podría construir» anunciaba planes en lugar de contenido. */
  function mundosLimpios() {
    if (mundo === 'aurzane' || !/^\/(index\.html)?$/.test(ruta)) return;
    var x = d.getElementById('crossWorldSection'); if (x) x.classList.add('az-vieja');
    Array.prototype.forEach.call(d.querySelectorAll('.accesos-section'), function (e) { e.classList.add('az-vieja'); });
    /* «Más explorado» repetía los artículos de «Lo más relevante» y «Recientes»; la promoción de OVP ya tiene su propia sección y su mundo */
    ['exploredSection', 'toolSection'].forEach(function (id) { var e = d.getElementById(id); if (e) e.classList.add('az-vieja'); });
    Array.prototype.forEach.call(d.querySelectorAll('section h2'), function (h) { if (/^Lo que (MIND|NEXUS|LIVE|LEARN|BUILD) (podría|va a) construir/.test(h.textContent.trim())) h.closest('section').classList.add('az-vieja'); });
  }


  /* ---------- 2d. El librero va después del contenido ----------
     En la biblioteca aparecía antes del libro o del catálogo y empujaba lo que la persona vino a ver. */
  function libreroAlFinal() {
    if (mundo !== 'aurzane' || !/^\/(biblioteca|libros)\b/.test(ruta)) return;
    function mover() {
      var lib = d.querySelector('.az-lib'); if (!lib || lib.__azMovido) return !!lib;
      if (lib.previousElementSibling && lib.previousElementSibling.classList && lib.previousElementSibling.classList.contains('comprar')) { lib.__azMovido = 1; return true; }
      var m = d.querySelector('main') || lib.parentNode; lib.__azMovido = 1; m.appendChild(lib); lib.classList.add('az-lib-final'); return true;
    }
    if (mover() || !w.MutationObserver) return;
    var mo = new MutationObserver(function () { if (mover()) mo.disconnect(); }); mo.observe(d.body, { childList: true, subtree: true }); setTimeout(function () { mo.disconnect(); }, 10000);
  }

  function anchoCompleto() {
    var els = [d.querySelector('.az-cab'), d.querySelector('.az-pie'), d.querySelector('.az-subnav')].filter(Boolean);
    function ajustar() {
      var cw = d.documentElement.clientWidth;
      els.forEach(function (el) {
        el.style.width = ''; el.style.marginLeft = ''; el.style.maxWidth = '';
        var r = el.getBoundingClientRect();
        if (r.width < cw - 2 || r.left > 1) { el.style.width = cw + 'px'; el.style.maxWidth = 'none'; el.style.marginLeft = (-r.left) + 'px'; }
      });
    }
    ajustar(); w.addEventListener('resize', ajustar);
  }

  /* ---------- 3. Buscador global: diálogo con combobox (WAI-ARIA) ---------- */
  var caja, entrada, lista, anterior, sel = -1, actuales = [];
  var RECIENTES = 'az-recientes';
  function recientes() { try { return JSON.parse(localStorage.getItem(RECIENTES) || '[]'); } catch (e) { return []; } }
  function anotarVisita() {
    var u = (host + ruta).replace(/index\.html$/, '');
    var item = INDICE.filter(function (x) { return x[1] === u; })[0];
    if (!item) return;
    var r = recientes().filter(function (x) { return x !== u; }); r.unshift(u);
    try { localStorage.setItem(RECIENTES, JSON.stringify(r.slice(0, 5))); } catch (e) {}
  }
  function crear() {
    caja = d.createElement('div'); caja.className = 'az-paleta';
    caja.innerHTML = '<div class="az-paleta-caja" role="dialog" aria-modal="true" aria-label="Buscar en AURZANE">' +
      '<div class="az-paleta-cab">' + ICO_LUPA + '<input type="text" role="combobox" aria-expanded="true" aria-controls="azPalLista" aria-autocomplete="list" autocomplete="off" spellcheck="false" placeholder="¿Qué buscas? Ansiedad, hipoteca, universidades…" aria-label="Buscar en AURZANE"><button type="button" class="cerrar">Cerrar</button></div>' +
      '<ul class="az-paleta-lista" id="azPalLista" role="listbox" aria-label="Resultados"></ul>' +
      '<div class="az-paleta-pie"><span>↑ ↓ para moverte</span><span>Intro para abrir</span><span>Esc para cerrar</span></div></div>';
    d.body.appendChild(caja);
    entrada = caja.querySelector('input'); lista = caja.querySelector('ul');
    entrada.addEventListener('input', pintar);
    entrada.addEventListener('keydown', teclas);
    caja.addEventListener('mousedown', function (e) { if (e.target === caja) cerrar(); });
    caja.querySelector('.cerrar').addEventListener('click', cerrar);
    lista.addEventListener('click', function (e) { var li = e.target.closest('[role="option"]'); if (li) ir(+li.getAttribute('data-i')); });
    lista.addEventListener('mousemove', function (e) { var li = e.target.closest('[role="option"]'); if (li) marcar(+li.getAttribute('data-i')); });
  }
  function abrir(origen, texto) {
    if (!caja) crear();
    anterior = (origen && origen.focus) ? origen : d.activeElement;
    caja.classList.add('ver'); entrada.value = typeof texto === 'string' ? texto : ''; pintar(); entrada.focus();
    d.documentElement.style.overflow = 'hidden';
  }
  function cerrar() {
    if (!caja || !caja.classList.contains('ver')) return;
    caja.classList.remove('ver'); d.documentElement.style.overflow = '';
    if (anterior && anterior.focus) anterior.focus();
  }
  function puntuar(x, q) {
    var t = sinTildes(x[0]), desc = sinTildes(x[4] + ' ' + x[3] + ' ' + x[2]), p = 0, partes = q.split(/\s+/).filter(Boolean);
    for (var i = 0; i < partes.length; i++) {
      var k = partes[i];
      if (t.indexOf(k) === 0) p += 12; else if (new RegExp('\\b' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(t)) p += 8; else if (t.indexOf(k) >= 0) p += 5; else if (desc.indexOf(k) >= 0) p += 2; else return 0;
    }
    if (x[5] !== 'es') p -= 3;
    return p;
  }
  function resaltar(t, q) {
    var e = esc(t); if (!q) return e;
    var base = sinTildes(t), partes = q.split(/\s+/).filter(Boolean), marcas = [];
    partes.forEach(function (k) { var i = base.indexOf(k); if (i >= 0) marcas.push([i, i + k.length]); });
    if (!marcas.length) return e;
    marcas.sort(function (a, b) { return a[0] - b[0]; });
    var s = '', pos = 0;
    marcas.forEach(function (m) { if (m[0] < pos) return; s += esc(t.slice(pos, m[0])) + '<mark>' + esc(t.slice(m[0], m[1])) + '</mark>'; pos = m[1]; });
    return s + esc(t.slice(pos));
  }
  function fila(x, i, q) {
    var c = COLOR[x[2]] || COLOR.aurzane;
    return '<li role="option" id="azOp' + i + '" data-i="' + i + '" aria-selected="false" style="--c:' + c + '"><span class="pt" aria-hidden="true"></span><span><b>' + resaltar(x[0], q) + '</b><small>' + esc(x[4] || '') + '</small></span><span class="tipo">' + esc(x[3]) + (x[2] !== 'aurzane' ? ' · ' + x[2].toUpperCase() : '') + '</span></li>';
  }
  function pintar() {
    var q = sinTildes(entrada.value.trim()), html = '';
    actuales = [];
    if (!q) {
      var r = recientes().map(function (u) { return INDICE.filter(function (x) { return x[1] === u; })[0]; }).filter(Boolean);
      var top = ['mind.aurzane.com/test-de-personalidad/', 'mind.aurzane.com/test-de-ansiedad/', 'ovp.aurzane.com/', 'nexus.aurzane.com/universidades/', 'build.aurzane.com/calculadora-hipoteca/', 'learn.aurzane.com/cursos/', 'aurzane.com/research.html']
        .map(function (u) { return INDICE.filter(function (x) { return x[1] === u; })[0]; }).filter(Boolean);
      if (r.length) { html += '<li class="grupo" role="presentation">Visto hace poco</li>'; r.forEach(function (x) { html += fila(x, actuales.length, ''); actuales.push(x); }); }
      html += '<li class="grupo" role="presentation">Lo más usado</li>';
      top.forEach(function (x) { if (actuales.indexOf(x) < 0) { html += fila(x, actuales.length, ''); actuales.push(x); } });
    } else {
      var res = INDICE.map(function (x) { return [puntuar(x, q), x]; }).filter(function (a) { return a[0] > 0; })
        .sort(function (a, b) { return b[0] - a[0]; }).slice(0, 12).map(function (a) { return a[1]; });
      var grupos = {};
      res.forEach(function (x) { (grupos[x[3]] = grupos[x[3]] || []).push(x); });
      Object.keys(grupos).forEach(function (g) {
        html += '<li class="grupo" role="presentation">' + esc(g === 'Página' ? 'Páginas' : g === 'Biblioteca' ? 'Bibliotecas' : g + 's') + '</li>';
        grupos[g].forEach(function (x) { html += fila(x, actuales.length, q); actuales.push(x); });
      });
      var art = ['Buscar «' + entrada.value.trim() + '» en 25.000 artículos científicos', 'aurzane.com/research.html?q=' + encodeURIComponent(entrada.value.trim()), 'aurzane', 'Research Hub', 'Las cinco bibliotecas académicas a la vez', 'es'];
      html += '<li class="grupo" role="presentation">Artículos científicos</li>' + fila(art, actuales.length, ''); actuales.push(art);
      if (!res.length) html = '<li class="az-paleta-vacio" role="presentation">No hay herramientas con «' + esc(entrada.value.trim()) + '». Prueba con otra palabra o busca en los artículos.</li>' + html;
    }
    lista.innerHTML = html;
    marcar(actuales.length ? 0 : -1);
  }
  function marcar(i) {
    sel = i;
    Array.prototype.forEach.call(lista.querySelectorAll('[role="option"]'), function (li) { li.setAttribute('aria-selected', +li.getAttribute('data-i') === i ? 'true' : 'false'); });
    var li = d.getElementById('azOp' + i);
    if (li) { entrada.setAttribute('aria-activedescendant', li.id); li.scrollIntoView({ block: 'nearest' }); } else entrada.removeAttribute('aria-activedescendant');
  }
  function ir(i) { var x = actuales[i]; if (x) location.href = 'https://' + x[1]; }
  function teclas(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); marcar(Math.min(sel + 1, actuales.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); marcar(Math.max(sel - 1, 0)); }
    else if (e.key === 'Enter') { e.preventDefault(); ir(sel); }
    else if (e.key === 'Escape') { e.preventDefault(); cerrar(); }
    else if (e.key === 'Tab') { e.preventDefault(); }   /* el foco se queda dentro del diálogo */
  }
  d.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) { e.preventDefault(); if (caja && caja.classList.contains('ver')) cerrar(); else abrir(); }
  });

  /* ---------- 4. Accesibilidad: nombres accesibles que faltaban (sin cambiar textos visibles) ---------- */
  function nombres() {
    Array.prototype.forEach.call(d.querySelectorAll('a[href],button'), function (el) {
      if (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) return;
      var txt = (el.textContent || '').replace(/\s+/g, ' ').trim();
      var visible = el.offsetParent !== null || el.getClientRects().length;
      if (txt && visible && el.innerText && el.innerText.trim()) return;
      var img = el.querySelector('img[alt]');
      var n = txt || el.getAttribute('title') || (img && img.getAttribute('alt'));
      if (n) el.setAttribute('aria-label', n);
    });
    Array.prototype.forEach.call(d.querySelectorAll('select:not([aria-label]):not([aria-labelledby])'), function (s) {
      if (s.id && d.querySelector('label[for="' + s.id + '"]')) return;
      var o = s.options[0]; s.setAttribute('aria-label', s.getAttribute('title') || s.name || (o ? o.text : 'Opciones'));
    });
    /* lo que está oculto a lectores de pantalla tampoco recibe el foco del teclado (WCAG 4.1.2) */
    Array.prototype.forEach.call(d.querySelectorAll('[aria-hidden="true"]'), function (el) {
      if (el.__azInert || !el.querySelector('a[href],button,input,select,textarea,[tabindex]')) return;
      el.__azInert = 1;
      var sync = function () { el.inert = el.getAttribute('aria-hidden') === 'true'; };
      sync(); if (w.MutationObserver) new MutationObserver(sync).observe(el, { attributes: true, attributeFilter: ['aria-hidden'] });
    });
    /* zonas con desplazamiento propio: alcanzables con teclado */
    Array.prototype.forEach.call(d.querySelectorAll('.scroll,.now-strip,.summary-table,.tnc,.comp'), function (s) { if (!s.hasAttribute('tabindex') && s.scrollWidth > s.clientWidth) { s.setAttribute('tabindex', '0'); s.setAttribute('role', 'region'); if (!s.getAttribute('aria-label')) s.setAttribute('aria-label', s.classList.contains('now-strip') ? 'Lo último publicado' : 'Tabla desplazable'); } });
  }

  function iniciar() { saltar(); barra(); pie(); mundosLimpios(); libreroAlFinal(); anchoCompleto(); anotarVisita(); nombres(); setTimeout(nombres, 2500); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
  w.AurzaneBuscar = abrir; w.AurzaneIndice = INDICE;
})(window, document);
