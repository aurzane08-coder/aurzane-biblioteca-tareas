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
    ['mind', 'MIND', 'Mente y tests'], ['nexus', 'NEXUS', 'Universidades y carreras'], ['live', 'LIVE', 'Salud y día a día'],
    ['learn', 'LEARN', 'Cursos'], ['build', 'BUILD', 'Dinero, ingresos y vivienda'], ['ovp', 'OVP', 'Orientación vocacional']
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
    mind: { n: 'MIND', u: 'https://mind.aurzane.com/', l: [['Tests', 'https://mind.aurzane.com/#tests'], ['Test de personalidad', 'https://mind.aurzane.com/test-de-personalidad/'], ['Ejercicios guiados', 'https://mind.aurzane.com/ejercicios/'], ['Guías', 'https://mind.aurzane.com/#recentSection'], ['Biblioteca', 'https://mind.aurzane.com/mind-biblioteca.html']] },
    nexus: { n: 'NEXUS', u: 'https://nexus.aurzane.com/', l: [['Universidades', 'https://nexus.aurzane.com/universidades/'], ['¿Qué puedo estudiar?', 'https://nexus.aurzane.com/universidades/que-puedo-estudiar/'], ['Notas de corte', 'https://nexus.aurzane.com/universidades/notas-de-corte/'], ['Nota PAU', 'https://nexus.aurzane.com/calculadora-nota-pau/'], ['Artículos', 'https://nexus.aurzane.com/nexus.html'], ['Biblioteca', 'https://nexus.aurzane.com/nexus-biblioteca.html']] },
    live: { n: 'LIVE', u: 'https://live.aurzane.com/', l: [['Ovulación', 'https://live.aurzane.com/calculadora-ovulacion/'], ['Embarazo', 'https://live.aurzane.com/calculadora-embarazo/'], ['Peso ideal', 'https://live.aurzane.com/calculadora-peso-ideal/'], ['Calorías', 'https://live.aurzane.com/calculadora-calorias/'], ['Sueño', 'https://live.aurzane.com/calculadora-sueno/'], ['Test de bienestar', 'https://live.aurzane.com/test-de-bienestar/'], ['Todas las herramientas', 'https://live.aurzane.com/#tests'], ['Artículos', 'https://live.aurzane.com/#recentSection']] },
    learn: { n: 'LEARN', u: 'https://learn.aurzane.com/', l: [['Mi aprendizaje', 'https://learn.aurzane.com/cursos/#mis-cursos'], ['Cursos', 'https://learn.aurzane.com/cursos/'], ['Certificados', 'https://learn.aurzane.com/certificado/'], ['Mi aula', 'https://learn.aurzane.com/aula/'], ['Guías', 'https://learn.aurzane.com/#recentSection'], ['Biblioteca', 'https://learn.aurzane.com/learn-biblioteca.html']] },
    build: { n: 'BUILD', u: 'https://build.aurzane.com/', l: [['Hipoteca', 'https://build.aurzane.com/calculadora-hipoteca/'], ['Gastos de compra', 'https://build.aurzane.com/calculadora-gastos-compra-vivienda/'], ['Alquiler', 'https://build.aurzane.com/calculadora-rentabilidad-alquiler/'], ['Sueldo neto', 'https://build.aurzane.com/calculadora-sueldo-neto/'], ['Finiquito', 'https://build.aurzane.com/calculadora-finiquito/'], ['Ahorro', 'https://build.aurzane.com/calculadora-ahorro/'], ['Jubilación', 'https://build.aurzane.com/calculadora-jubilacion/'], ['Reforma', 'https://build.aurzane.com/calculadora-reforma/'], ['Guías', 'https://build.aurzane.com/#recentSection']] },
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

  /* ---------- 2e. Guardados comunes a todo el ecosistema ----------
     Lo que guardas en cualquier mundo aparece en todos: en este navegador (almacén común en aurzane.com) y,
     si has iniciado sesión con AURZANE ID, también en tu cuenta para verlo en cualquier dispositivo.
     Incorpora lo que ya tenías guardado en cada mundo y en «Mi lista» del Research Hub. */
  var SB_URL = 'https://chtfpqwrrarfdjcivlad.supabase.co', SB_KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw';
  var G = { d: null, cola: [], marco: null, n: 0, esperando: {}, cli: null, nube: false };
  var ICO_MARCA = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z"/></svg>';
  var TIPOS = ['Test', 'Perfil', 'Calculadora', 'Ejercicio', 'Curso', 'Artículo', 'Libro', 'Universidad', 'Artículo científico', 'Página'];
  function vacio() { return { l: [], b: [], i: [] }; }
  function pedir(op, v, cb) {
    if (host === 'aurzane.com') {
      try { if (op === 'escribir') localStorage.setItem('az-guardados', JSON.stringify(v)); var x = JSON.parse(localStorage.getItem('az-guardados') || 'null'); cb(x && x.l ? x : vacio()); } catch (e) { cb(op === 'escribir' ? v : vacio()); }
      return;
    }
    var id = ++G.n; G.esperando[id] = cb;
    var enviar = function () { G.marco.contentWindow.postMessage({ az: 'g', op: op, v: v, id: id }, 'https://aurzane.com'); };
    if (G.marco && G.marco.__listo) enviar(); else G.cola.push(enviar);
    setTimeout(function () { if (G.esperando[id]) { delete G.esperando[id]; cb(op === 'escribir' ? v : vacio()); } }, 6000);
  }
  function abrirAlmacen(cb) {
    if (host === 'aurzane.com') return cb();
    w.addEventListener('message', function (e) {
      if (e.origin !== 'https://aurzane.com' || !e.data || e.data.az !== 'g') return;
      if (e.data.listo) { G.marco.__listo = true; G.cola.splice(0).forEach(function (f) { f(); }); return; }
      var f = G.esperando[e.data.id]; if (f) { delete G.esperando[e.data.id]; f(e.data.v || vacio()); }
    });
    var f = d.createElement('iframe'); f.src = 'https://aurzane.com/guardados-almacen.html'; f.title = 'Almacén de guardados'; f.setAttribute('aria-hidden', 'true'); f.tabIndex = -1;
    f.style.cssText = 'position:absolute;width:1px;height:1px;border:0;left:-9999px;top:0;visibility:hidden';
    G.marco = f; d.body.appendChild(f); cb();
  }
  function guardarLocal(cb) { G.d.b = G.d.b.slice(-300); G.d.i = G.d.i.slice(-600); pedir('escribir', G.d, function () { pintarContador(); if (cb) cb(); }); }
  function esta(u) { return G.d && G.d.l.some(function (x) { return x.u === u; }); }
  function enlace(u) { return /^https?:/.test(u) ? u : 'https://' + u; }
  function anadir(it, sinNube) {
    if (!it || esta(it.u)) return;
    it.f = it.f || new Date().toISOString().slice(0, 10);
    G.d.l.unshift(it); G.d.b = G.d.b.filter(function (b) { return b !== it.u; });
    if (!sinNube) nube('poner', it);
  }
  function quitar(u, sinNube) {
    G.d.l = G.d.l.filter(function (x) { return x.u !== u; });
    if (G.d.b.indexOf(u) < 0) G.d.b.push(u);
    if (!sinNube) nube('quitar', { u: u });
  }

  /* la página actual: qué es y cómo se llama */
  function itemActual() {
    var p = ruta.replace(/index\.html$/, ''), h = location.hash || '', k = null, u = host + p;
    var mArt = h.match(/^#\/articulo\/([^/?#]+)/);
    if (mArt) { k = 'Artículo'; u = host + '/#/articulo/' + mArt[1]; }
    else if (/^\/test-de-personalidad\/p\/[^/]+\/$/.test(p)) k = 'Perfil';
    else if (/^\/(test-de-[^/]+|en\/[^/]+-test[^/]*|pt\/teste-[^/]+)\/$/.test(p) || (mundo === 'ovp' && /^\/$/.test(p))) k = 'Test';
    else if (/calculadora-[^/]+\/$/.test(p)) k = 'Calculadora';
    else if (/^\/ejercicios\/[^/]+\/$/.test(p)) k = 'Ejercicio';
    else if (mundo === 'learn' && /^\/curso\/[^/]+\/$/.test(p)) k = 'Curso';
    else if (mundo === 'aurzane' && /^\/(biblioteca\/libro\/[^/]+|libros\/[^/]+\/|biblioteca\/recientes\/[^/]+\/)$/.test(p)) k = 'Libro';
    else if (mundo === 'aurzane' && /^\/(articulos|articulos-ai)\/[^/]+\/$/.test(p)) k = 'Artículo';
    else if (mundo === 'nexus' && /^\/universidades\/[^/]+\/[^/]+\/$/.test(p) && !/notas-de-corte\/$|que-puedo-estudiar\/$/.test(p)) k = 'Universidad';
    if (!k) return null;
    var h1 = Array.prototype.filter.call(d.querySelectorAll('h1'), function (x) { return x.offsetParent !== null && !x.closest('.az-cab,.az-vieja'); })[0];
    var tt = d.title.split(/\s[|·–—]\s/)[0].replace(/:\s.*$/, '').replace(/\s+(gratis|online)\b.*$/i, '').trim();
    var t = /^(Test|Perfil|Calculadora|Ejercicio)$/.test(k) && tt ? tt : ((h1 && h1.innerText.replace(/\s+/g, ' ').trim()) || tt);
    return { u: u, t: t.slice(0, 120), m: mundo, k: k };
  }

  /* lo guardado antes en cada mundo y en el Research Hub pasa a la lista común (y se mantiene sincronizado) */
  function importar() {
    var cambio = false, clave;
    if (mundo !== 'aurzane' && mundo !== 'ovp') {
      clave = 'aurzane-' + mundo + '-guardados';
      var sl; try { sl = JSON.parse(localStorage.getItem(clave) || '[]'); } catch (e) { sl = []; }
      var limpio = sl.filter(function (s) { return G.d.b.indexOf(host + '/#/articulo/' + s) < 0 || G.d.i.indexOf(mundo + ':' + s) < 0; });
      if (limpio.length !== sl.length) { try { localStorage.setItem(clave, JSON.stringify(limpio)); } catch (e) {} sl.forEach(function (x) { if (limpio.indexOf(x) < 0) G.d.i = G.d.i.filter(function (k) { return k !== mundo + ':' + x; }); }); cambio = true; }
      limpio.forEach(function (s) {
        var key = mundo + ':' + s, u = host + '/#/articulo/' + s;
        if (G.d.i.indexOf(key) >= 0) return;
        var a = d.querySelector('a[href*="#/articulo/' + s + '"]'), t = a ? (a.querySelector('h3,h4,h2') || a).innerText.trim() : '';
        anadir({ u: u, t: (t || s.replace(/-/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); })).slice(0, 120), m: mundo, k: 'Artículo' });
        G.d.i.push(key); cambio = true;
      });
      G.d.i.filter(function (k) { return k.indexOf(mundo + ':') === 0; }).forEach(function (k) {
        var s = k.slice(mundo.length + 1);
        if (limpio.indexOf(s) < 0) { if (esta(host + '/#/articulo/' + s)) quitar(host + '/#/articulo/' + s); G.d.i = G.d.i.filter(function (z) { return z !== k; }); cambio = true; }
      });
    }
    if (mundo === 'aurzane' && /^\/research(\.html)?$/.test(ruta)) {
      var rl; try { rl = JSON.parse(localStorage.getItem('rh-guardados') || '[]'); } catch (e) { rl = []; }
      var limpia = rl.filter(function (x) { return !(x.url && G.d.b.indexOf(x.url) >= 0 && G.d.i.indexOf('rh:' + x.url) >= 0); });
      if (limpia.length !== rl.length) { try { localStorage.setItem('rh-guardados', JSON.stringify(limpia)); } catch (e) {} rl.forEach(function (x) { if (limpia.indexOf(x) < 0) G.d.i = G.d.i.filter(function (k) { return k !== 'rh:' + x.url; }); }); cambio = true; }
      var urls = limpia.map(function (x) { return x.url; });
      limpia.forEach(function (x) {
        if (!x.url || G.d.i.indexOf('rh:' + x.url) >= 0) return;
        anadir({ u: x.url, t: String(x.titulo || '').slice(0, 120), m: 'aurzane', k: 'Artículo científico' }); G.d.i.push('rh:' + x.url); cambio = true;
      });
      G.d.i.filter(function (k) { return k.indexOf('rh:') === 0; }).forEach(function (k) { var u = k.slice(3); if (urls.indexOf(u) < 0) { if (esta(u)) quitar(u); G.d.i = G.d.i.filter(function (z) { return z !== k; }); cambio = true; } });
    }
    return cambio;
  }

  /* cuenta AURZANE ID: misma lista en todos tus dispositivos */
  function cargarScript(src, ok) { var s = d.createElement('script'); s.src = src; s.onload = ok; s.onerror = function () {}; d.head.appendChild(s); }
  function conectarNube(cb) {
    if (!sesion()) return cb && cb(false);
    var listo = function () { try { G.cli = w.crearClienteAurzaneID(SB_URL, SB_KEY); G.nube = true; } catch (e) { G.nube = false; } if (cb) cb(G.nube); };
    var conId = function () { if (w.crearClienteAurzaneID) listo(); else cargarScript('https://aurzane.com/aurzane-id.js', listo); };
    if (w.supabase && w.supabase.createClient) conId(); else cargarScript('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js', conId);
  }
  function nube(op, it) {
    if (!G.nube || !G.cli) return;
    if (op === 'poner') G.cli.from('guardados').upsert({ url: it.u, titulo: it.t, mundo: it.m, tipo: it.k }, { onConflict: 'user_id,url' }).then(function () {}, function () {});
    else G.cli.from('guardados').delete().eq('url', it.u).then(function () {}, function () {});
  }
  function sincronizar(cb) {
    if (!G.nube) return cb && cb();
    G.cli.from('guardados').select('url,titulo,mundo,tipo,creado').order('creado', { ascending: false }).limit(1000).then(function (r) {
      if (r.error || !r.data) return cb && cb();
      var remotas = {};
      r.data.forEach(function (x) { remotas[x.url] = 1; if (G.d.b.indexOf(x.url) >= 0) nube('quitar', { u: x.url }); else if (!esta(x.url)) G.d.l.push({ u: x.url, t: x.titulo, m: x.mundo, k: x.tipo, f: String(x.creado || '').slice(0, 10) }); });
      G.d.l.forEach(function (x) { if (!remotas[x.u]) nube('poner', x); });
      G.d.l.sort(function (a, b) { return (b.f || '').localeCompare(a.f || ''); });
      guardarLocal(cb);
    }, function () { if (cb) cb(); });
  }

  /* interfaz: botón «Guardar» de la página, botón «Guardados» de la cabecera y su panel */
  function pintarContador() {
    var n = G.d ? G.d.l.length : 0;
    Array.prototype.forEach.call(d.querySelectorAll('.az-gd-n'), function (e) { e.textContent = n || ''; e.hidden = !n; });
    var b = d.querySelector('.az-gd-btn'); if (b) b.setAttribute('aria-label', 'Guardados' + (n ? ': ' + n : ''));
    var it = itemActual(), g = d.querySelector('.az-gd-esta');
    if (g) { g.hidden = !it; if (it) { var on = esta(it.u); g.setAttribute('aria-pressed', on); g.querySelector('.txt').textContent = on ? 'Guardado' : 'Guardar'; g.setAttribute('aria-label', (on ? 'Quitar de guardados: ' : 'Guardar: ') + it.t); } }
    if (G.panel && !G.panel.hidden) pintarPanel();
  }
  function pintarPanel() {
    var cuerpo = G.panel.querySelector('.az-gd-lista'), l = G.d.l;
    if (!l.length) { cuerpo.innerHTML = '<p class="az-gd-vacio">Aún no has guardado nada. Pulsa «Guardar» en cualquier test, calculadora, ejercicio, curso, libro, artículo o universidad y lo tendrás aquí, en todos los mundos.</p>'; return; }
    var grupos = {}; l.forEach(function (x) { (grupos[x.k] = grupos[x.k] || []).push(x); });
    cuerpo.innerHTML = TIPOS.concat(Object.keys(grupos).filter(function (k) { return TIPOS.indexOf(k) < 0; })).filter(function (k) { return grupos[k]; }).map(function (k) {
      return '<h3>' + esc(k === 'Artículo científico' ? 'Artículos científicos' : k === 'Universidad' ? 'Universidades' : k === 'Página' ? 'Páginas' : k + 's') + ' <span>' + grupos[k].length + '</span></h3><ul>' + grupos[k].map(function (x) {
        return '<li style="--c:' + (COLOR[x.m] || COLOR.aurzane) + '"><i aria-hidden="true"></i><a href="' + esc(enlace(x.u)) + '"' + (/^https?:/.test(x.u) ? ' target="_blank" rel="noopener"' : '') + '>' + esc(x.t) + '</a><small>' + esc(x.m === 'aurzane' ? 'AURZANE' : x.m.toUpperCase()) + '</small><button type="button" data-q="' + esc(x.u) + '" aria-label="Quitar ' + esc(x.t) + '">' +
          '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button></li>';
      }).join('') + '</ul>';
    }).join('');
  }
  function crearPanel() {
    var p = d.createElement('div'); p.className = 'az-gd-velo'; p.hidden = true;
    p.innerHTML = '<aside class="az-gd" role="dialog" aria-modal="true" aria-labelledby="azGdT"><div class="az-gd-cab"><h2 id="azGdT">Guardados</h2><button type="button" class="az-gd-cerrar" aria-label="Cerrar guardados"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button></div>' +
      '<div class="az-gd-lista"></div><p class="az-gd-pie"></p></aside>';
    d.body.appendChild(p); G.panel = p;
    p.addEventListener('mousedown', function (e) { if (e.target === p) cerrarPanel(); });
    p.querySelector('.az-gd-cerrar').addEventListener('click', cerrarPanel);
    p.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-q]'); if (!b) return;
      var u = b.getAttribute('data-q'), li = b.closest('li'), sig = li && (li.nextElementSibling || li.previousElementSibling);
      quitar(u); guardarLocal(function () { var f = sig && sig.querySelector('button[data-q]'); (f || p.querySelector('.az-gd-cerrar')).focus(); });
      pintarPanel(); pintarContador();
    });
    p.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); cerrarPanel(); }
      if (e.key === 'Tab') { var f = p.querySelectorAll('a[href],button'); if (!f.length) return; var a = f[0], z = f[f.length - 1];
        if (e.shiftKey && d.activeElement === a) { e.preventDefault(); z.focus(); } else if (!e.shiftKey && d.activeElement === z) { e.preventDefault(); a.focus(); } }
    });
  }
  function abrirPanel(origen) {
    if (!G.panel) crearPanel();
    G.origen = origen; pintarPanel();
    G.panel.querySelector('.az-gd-pie').innerHTML = G.nube ? 'Sincronizados con tu cuenta AURZANE ID: los verás en cualquier dispositivo.' : 'Se guardan en este navegador. <a href="https://aurzane.com/mi-aurzane.html">Inicia sesión</a> para verlos también en tus otros dispositivos.';
    G.panel.hidden = false; d.documentElement.style.overflow = 'hidden';
    G.panel.querySelector('.az-gd-cerrar').focus();
  }
  function cerrarPanel() { if (!G.panel || G.panel.hidden) return; G.panel.hidden = true; d.documentElement.style.overflow = ''; if (G.origen && G.origen.focus) G.origen.focus(); }
  function botones() {
    var acc = d.querySelector('.az-cab .az-acc'); if (!acc || acc.querySelector('.az-gd-btn')) return;
    var gs = d.createElement('button'); gs.type = 'button'; gs.className = 'az-btn az-gd-esta'; gs.hidden = true; gs.setAttribute('aria-pressed', 'false');
    gs.innerHTML = ICO_MARCA + '<span class="txt">Guardar</span>';
    var gb = d.createElement('button'); gb.type = 'button'; gb.className = 'az-btn az-gd-btn'; gb.setAttribute('aria-haspopup', 'dialog');
    gb.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h10v16l-5-3.5L5 20z"/><path d="M15 6h4v16l-4-2.8"/></svg><span class="txt">Guardados</span><span class="az-gd-n" hidden></span>';
    var cuenta = acc.querySelector('.az-cuenta'); acc.insertBefore(gs, cuenta); acc.insertBefore(gb, cuenta);
    gb.addEventListener('click', function () { abrirPanel(gb); });
    gs.addEventListener('click', function () {
      var it = itemActual(); if (!it) return;
      if (esta(it.u)) quitar(it.u); else anadir(it);
      guardarLocal(); pintarContador();
    });
    var caj = d.querySelector('.az-cajon ul'); if (caj) { var li = d.createElement('li'); li.innerHTML = '<a href="#" class="az-gd-cajon">' + ICO_MARCA + 'Guardados <span class="az-gd-n" hidden></span></a>'; caj.appendChild(li);
      li.querySelector('a').addEventListener('click', function (e) { e.preventDefault(); abrirPanel(gb); }); }
  }
  function guardados() {
    if (!d.querySelector('.az-cab')) return;
    botones();
    abrirAlmacen(function () {
      pedir('leer', null, function (v) {
        G.d = v && v.l ? v : vacio(); if (!G.d.b) G.d.b = []; if (!G.d.i) G.d.i = [];
        if (importar()) guardarLocal(); pintarContador();
        conectarNube(function (ok) { if (ok) sincronizar(pintarContador); });
      });
    });
    w.addEventListener('hashchange', function () { setTimeout(pintarContador, 400); });
    /* lo que se guarda o quita con los botones propios de cada mundo y del Research Hub se refleja al momento */
    var sc = d.getElementById('savedCount') || d.getElementById('nLista');
    if (sc && w.MutationObserver) new MutationObserver(function () { if (G.d && importar()) { guardarLocal(); pintarContador(); } }).observe(sc, { childList: true, characterData: true, subtree: true });
    setTimeout(function () { if (G.d && importar()) { guardarLocal(); pintarContador(); } }, 3000);
    w.AurzaneGuardados = { abrir: function () { abrirPanel(d.querySelector('.az-gd-btn')); }, lista: function () { return G.d ? G.d.l.slice() : []; } };
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
    var t = sinTildes(x[0]), desc = sinTildes(x[4] + ' ' + x[3] + ' ' + x[2] + ' ' + (x[6] || '')), p = 0, partes = q.split(/\s+/).filter(Boolean);
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

  /* módulos por zona: biblioteca (aurzane-bib.js) y aula de LEARN (aurzane-learn.js) */
  function modulos() {
    var h = location.hostname.replace(/^www\./, ''), p = location.pathname, src = '';
    if (h === 'aurzane.com' && /^\/biblioteca(\/|$)/.test(p)) src = 'https://aurzane.com/aurzane-bib.js?v=1';
    else if (h === 'learn.aurzane.com') src = 'https://aurzane.com/aurzane-learn.js?v=1';
    if (!src || d.querySelector('script[data-azmod]')) return;
    var s = d.createElement('script'); s.src = src; s.defer = true; s.setAttribute('data-azmod', '1'); d.head.appendChild(s);
  }
  function iniciar() { saltar(); barra(); pie(); mundosLimpios(); libreroAlFinal(); guardados(); anchoCompleto(); anotarVisita(); nombres(); setTimeout(nombres, 2500); modulos(); }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', iniciar); else iniciar();
  w.AurzaneBuscar = abrir; w.AurzaneIndice = INDICE;
  /* índice al día: herramientas/indice.py lo regenera cada día con los tests, calculadoras, ejercicios y cursos nuevos */
  (function () {
    function usar() { var G = w.AurzaneIndiceGen; if (G && G.length) { INDICE.length = 0; Array.prototype.push.apply(INDICE, G); } try { d.dispatchEvent(new Event('aurzane-indice')); } catch (e) {} }
    if (w.AurzaneIndiceGen) return usar();
    var s = d.createElement('script'); s.async = true; s.src = 'https://aurzane.com/aurzane-indice.js?d=' + new Date().toISOString().slice(0, 10); s.onload = usar; d.head.appendChild(s);
  })();
})(window, document);
