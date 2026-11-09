/* ===================================================================
   informe-shared.js · AURZANE MIND
   Lógica de puntuación e interpretación del informe integrado de OVP
   (CHASIDE, Holland/RIASEC, AF5, CHTE, APT-B, APT-A) y la función que
   arma el HTML del informe (generateReportFromData). Compartida entre
   la vista admin (generar-informe.html) y la vista del cliente
   (portal.html "Mi Informe") para que ambas produzcan exactamente el
   mismo informe con una sola fuente de verdad.

   Contrato con quien lo incluye:
   - Debe definir antes de llamar a generateReportFromData(): las
     variables de datos crudos que las funciones compute* leen
     (cha_responses, af5_responses, cht_responses, apt_b_rows,
     apt_a_rows, holland_rows), cada página las llena desde sus
     propias consultas a Supabase.
   - Debe tener en el DOM un contenedor <div id="reportContent"
     class="aurzane-report"> antes de llamar a generateReportFromData;
     la función escribe el informe completo dentro de él.
   - Debe cargar informe-shared.css para que el informe se vea igual
     en ambas páginas (encabezado navy/gold incluido).
   =================================================================== */

const CHA_QUESTIONS = [
  "¿Aceptarías trabajar escribiendo artículos en la sección económica de un diario?",
  "¿Te ofrecerías para organizar el cumpleaños de uno de tus amigos?",
  "¿Te gustaría dirigir un proyecto de urbanización en tu provincia?",
  "¿A una frustración siempre opones un pensamiento positivo?",
  "¿Te dedicarías a socorrer a personas accidentadas o atacadas por asaltantes?",
  "¿Cuando eras chico, te interesaba saber cómo estaban construidos tus juguetes?",
  "¿Te interesan más los misterios de la naturaleza que los secretos de la tecnología?",
  "¿Escuchas atentamente los problemas que te plantean tus amigos?",
  "¿Te ofrecerías para explicar a tus compañeros un determinado tema que ellos no entendieron?",
  "¿Eres exigente y crítico con tu equipo de trabajo?",
  "¿Te atrae armar rompecabezas o puzzles?",
  "¿Puedes establecer la diferencia conceptual entre macroeconomía y microeconomía?",
  "¿Usar uniforme te hace sentir distinto, importante?",
  "¿Participarías como profesional en un espectáculo de acrobacia aérea?",
  "¿Organizas tu dinero de manera que te alcance hasta el próximo cobro?",
  "¿Convences fácilmente a otras personas sobre la validez de tus argumentos?",
  "¿Estás informado sobre los nuevos descubrimientos que se están realizando sobre la Teoría del Big-Bang?",
  "¿Ante una situación de emergencia actúas rápidamente?",
  "¿Cuando tienes que resolver un problema matemático, perseveras hasta encontrar la solución?",
  "¿Si te convocara tu club preferido para planificar, organizar y dirigir un campo de deportes, aceptarías?",
  "¿Eres el que pone un toque de alegría en las fiestas?",
  "¿Crees que los detalles son tan importantes como el todo?",
  "¿Te sentirías a gusto trabajando en un ámbito hospitalario?",
  "¿Te gustaría participar para mantener el orden ante grandes desórdenes y cataclismos?",
  "¿Pasarías varias horas leyendo algún libro de tu interés?",
  "¿Planificas detalladamente tus trabajos antes de empezar?",
  "¿Entablas una relación casi personal con tu computadora?",
  "¿Disfrutas modelando con arcilla?",
  "¿Ayudas habitualmente a los no videntes a cruzar la calle?",
  "¿Consideras importante que desde la escuela primaria se fomente la actitud crítica y la participación activa?",
  "¿Aceptarías que las mujeres formaran parte de las fuerzas armadas bajo las mismas normas que los hombres?",
  "¿Te gustaría crear nuevas técnicas para descubrir las patologías de algunas enfermedades a través del microscopio?",
  "¿Participarías en una campaña de prevención contra la enfermedad de Chagas?",
  "¿Te interesan los temas relacionados al pasado y a la evolución del hombre?",
  "¿Te incluirías en un proyecto de investigación de los movimientos sísmicos y sus consecuencias?",
  "¿Fuera de los horarios escolares, dedicas algún día de la semana a la realización de actividades corporales?",
  "¿Te interesan las actividades de mucha acción y de reacción rápida en situaciones imprevistas y de peligro?",
  "¿Te ofrecerías para colaborar como voluntario en los gabinetes espaciales de la NASA?",
  "¿Te gusta más el trabajo manual que el trabajo intelectual?",
  "¿Estarías dispuesto a renunciar a un momento placentero para ofrecer tu servicio como profesional?",
  "¿Participarías de una investigación sobre la violencia en el fútbol?",
  "¿Te gustaría trabajar en un laboratorio mientras estudias?",
  "¿Arriesgarías tu vida para salvar la vida de otro que no conoces?",
  "¿Te agradaría hacer un curso de primeros auxilios?",
  "¿Tolerarías empezar tantas veces como fuere necesario hasta obtener el logro deseado?",
  "¿Distribuyes tus horarios del día adecuadamente para poder hacer todo lo planeado?",
  "¿Harías un curso para aprender a fabricar los instrumentos y/o piezas de las máquinas o aparatos con que trabajas?",
  "¿Elegirías una profesión en la tuvieras que estar algunos meses alejado de tu familia, por ejemplo el marino?",
  "¿Te radicarías en una zona agrícola-ganadera para desarrollar tus actividades como profesional?",
  "¿Cuando estás en un grupo trabajando, te entusiasma producir ideas originales y que sean tenidas en cuenta?",
  "¿Te resulta fácil coordinar un grupo de trabajo?",
  "¿Te resultó interesante el estudio de las ciencias biológicas?",
  "¿Si una gran empresa solicita un profesional como gerente de comercialización, te sentirías a gusto desempeñando ese rol?",
  "¿Te incluirías en un proyecto nacional de desarrollo de la principal fuente de recursos de tu provincia?",
  "¿Tienes interés por saber cuáles son las causas que determinan ciertos fenómenos, aunque saberlo no altere tu vida?",
  "¿Descubriste algún filósofo o escritor que haya expresado tus mismas ideas con antelación?",
  "¿Desearías que te regalen algún instrumento musical para tu cumpleaños?",
  "¿Aceptarías colaborar con el cumplimiento de las normas en lugares públicos?",
  "¿Crees que tus ideas son importantes, y haces todo lo posible para ponerlas en práctica?",
  "¿Cuándo se descompone un artefacto en tu casa, te dispones prontamente a repararlo?",
  "¿Formarías parte de un equipo de trabajo orientado a la preservación de la flora y fauna en extinción?",
  "¿Acostumbras a leer revistas relacionadas con los últimos avances científicos y tecnológicos en el área de la salud?",
  "¿Preservar las raíces culturales de nuestro país, te parece importante y necesario?",
  "¿Te gustaría realizar una investigación que contribuyera a hacer más justa la distribución de la riqueza?",
  "¿Te gustaría realizar tareas auxiliares en una nave, como por ejemplo izado y arriado de velas, pintura y conservación del casco, arreglo de averías, conservación de motores, etc.?",
  "¿Crees que un país debe poseer la más alta tecnología armamentista, a cualquier precio?",
  "¿La libertad y la justicia son valores fundamentales en tu vida?",
  "¿Aceptarías hacer una práctica rentada en una industria de productos alimenticios en el sector de control de calidad?",
  "¿Consideras que la salud pública debe ser prioritaria, gratuita y eficiente para todos?",
  "¿Te interesaría investigar sobre alguna nueva vacuna?",
  "¿En un equipo de trabajo, prefieres el rol de coordinador?",
  "¿En una discusión entre amigos, te ofreces como mediador?",
  "¿Estás de acuerdo con la formación de un cuerpo de soldados profesionales?",
  "¿Lucharías por una causa justa hasta las últimas consecuencias?",
  "¿Te gustaría investigar científicamente sobre cultivos agrícolas?",
  "¿Harías un nuevo diseño de una prenda pasada de moda, ante una reunión imprevista?",
  "¿Visitarías un observatorio astronómico para conocer en acción el funcionamiento de los aparatos?",
  "¿Dirigirías el área de importación y exportación de una empresa?",
  "¿Te inhibes al entrar a un lugar nuevo con gente desconocida?",
  "¿Te gratificaría el trabajar con niños?",
  "¿Harías el diseño de un afiche para una campaña contra el sida?",
  "¿Dirigirías un grupo de teatro independiente?",
  "¿Enviarías tu currículum a una empresa automotriz que solicita gerente para su área de producción?",
  "¿Participarías en un grupo de defensa internacional dentro de alguna fuerza armada?",
  "¿Te costearías tus estudios trabajando en una auditoría?",
  "¿Eres de los que defiendes causas perdidas?",
  "¿Ante una emergencia epidémica participarías en una campaña brindando tu ayuda?",
  "¿Sabrías responder que significa ADN y ARN?",
  "¿Elegirías una carrera cuyo instrumento de trabajo fuera la utilización de un idioma extranjero?",
  "¿Trabajar con objetos te resulta más gratificante que trabajar con personas?",
  "¿Te resultaría gratificante ser asesor contable en una empresa reconocida?",
  "¿Ante un llamado solidario, te ofrecerías para cuidar a un enfermo?",
  "¿Te atrae investigar sobre los misterios del universo, por ejemplo los agujeros negros?",
  "¿El trabajo individual te resulta más rápido y efectivo que el trabajo grupal?",
  "¿Dedicarías parte de tu tiempo a ayudar a personas de zonas carenciadas?",
  "¿Cuando eliges tu ropa o decoras un ambiente, tienes en cuenta la combinación de los colores, las telas o el estilo de los muebles?",
  "¿Te gustaría trabajar como profesional dirigiendo la construcción de una empresa hidroeléctrica?",
  "¿Sabes qué es el PBI?"
];

const CHA_AREA_INFO = {
  C: {
    name: "Administrativas y Contables",
    interesTraits: ["Organizativo","Supervisión","Orden","Análisis y síntesis","Colaboración","Cálculo"],
    aptitudTraits: ["Persuasivo","Objetivo","Práctico","Tolerante","Responsable","Ambicioso"],
    workStyle: "El perfil combina intereses por la organización, la supervisión y el cálculo con aptitudes de persuasión, objetividad y responsabilidad. Suele tratarse de un perfil cómodo liderando procesos estructurados, tomando decisiones prácticas y comunicando ideas con seguridad. Habitualmente se desempeña bien en entornos donde el orden y los resultados medibles importan.",
    careers: ["Administración de Empresas","Contabilidad y Auditoría","Economía","Marketing","Negocios Internacionales","Turismo y Hotelería","Recursos Humanos","Finanzas","Gestión Pública","Derecho"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles de gestión y dirección: coordinar equipos, administrar presupuestos, liderar un área dentro de una empresa o emprender un negocio propio. También abre camino hacia auditoría, consultoría financiera, análisis de mercados o cargos de gestión pública, espacios donde la capacidad de organizar procesos y decidir con datos concretos marca la diferencia."
  },
  H: {
    name: "Humanidades y Ciencias Sociales",
    interesTraits: ["Precisión verbal","Organización","Relación de hechos","Lingüística","Orden","Justicia"],
    aptitudTraits: ["Responsable","Justo","Conciliador","Persuasivo","Sagaz","Imaginativo"],
    workStyle: "El perfil combina precisión verbal, orden y sentido de justicia con aptitudes de responsabilidad, conciliación e imaginación. Suele tratarse de una persona que razona con facilidad a través de la palabra, media en conflictos con naturalidad y encuentra sentido en comprender o defender causas humanas.",
    careers: ["Derecho","Ciencias Políticas","Comunicación Social","Periodismo","Historia","Filosofía","Sociología","Trabajo Social","Relaciones Internacionales","Educación / Pedagogía"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles donde la palabra y el análisis social son la herramienta principal: litigar o asesorar legalmente, investigar y comunicar, mediar conflictos, diseñar política pública o educar. Con los años, muchas de estas trayectorias derivan en consultoría, docencia universitaria, cargos de representación o trabajo en organismos internacionales."
  },
  A: {
    name: "Artísticas",
    interesTraits: ["Estético","Armónico","Manual","Visual","Auditivo"],
    aptitudTraits: ["Sensible","Imaginativo","Creativo","Detallista","Innovador","Intuitivo"],
    workStyle: "El perfil combina sensibilidad estética y disfrute por lo manual y visual con aptitudes de creatividad, innovación e intuición. Es un perfil que procesa el mundo de forma sensorial y encuentra satisfacción real en crear o dar forma a algo nuevo, más que en seguir procedimientos fijos.",
    careers: ["Diseño Gráfico","Arquitectura","Artes Plásticas","Música","Diseño de Modas","Cine y Audiovisuales","Publicidad Creativa","Danza y Artes Escénicas","Diseño de Interiores"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles donde dar forma visual, sonora o narrativa a una idea es el centro del trabajo: dirección creativa, diseño de producto, dirección de arte, producción audiovisual o musical. Muchas de estas trayectorias combinan con el tiempo el trabajo independiente (marca o estudio propio) con la colaboración en agencias, estudios o productoras."
  },
  S: {
    name: "Medicina y Ciencias de la Salud",
    interesTraits: ["Asistir","Investigativo","Precisión","Senso-perceptivo","Analítico","Ayudar"],
    aptitudTraits: ["Altruista","Solidario","Paciente","Comprensivo","Respetuoso","Persuasivo"],
    workStyle: "El perfil combina el interés por asistir, investigar y percibir con precisión, junto a aptitudes de altruismo, paciencia y comprensión. Es habitual en personas orientadas al cuidado de otros, que toleran bien la exigencia emocional del trabajo asistencial y encuentran motivación genuina en ayudar.",
    careers: ["Medicina","Enfermería","Odontología","Psicología","Nutrición","Fisioterapia / Rehabilitación","Bioquímica","Obstetricia","Veterinaria","Cultura Física y Deportes"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles de atención directa a personas (clínica, consulta, terapia, rehabilitación), con posibilidad de especializarse en un área concreta con los años, o de moverse hacia la docencia, la investigación clínica o la gestión de equipos de salud."
  },
  I: {
    name: "Ingeniería y Computación",
    interesTraits: ["Cálculo","Científico","Manual","Exacto","Planificar"],
    aptitudTraits: ["Preciso","Práctico","Crítico","Analítico","Riguroso"],
    workStyle: "El perfil combina el interés por el cálculo, la ciencia y la planificación con aptitudes de precisión, practicidad y análisis crítico. Suele tratarse de una persona que disfruta resolver problemas concretos con lógica y método, y que se siente más cómoda trabajando con sistemas que con la ambigüedad.",
    careers: ["Ingeniería en Sistemas / Software","Ingeniería Civil","Ingeniería Industrial","Ingeniería Electrónica","Ingeniería Mecánica","Ciencias de la Computación","Telecomunicaciones","Ciberseguridad","Robótica"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles de diseño y construcción de soluciones técnicas: desarrollar software, liderar proyectos de infraestructura, automatizar procesos o dirigir equipos técnicos. Con la experiencia, estas trayectorias suelen derivar en arquitectura de sistemas, gerencia técnica o en el desarrollo de un producto o empresa propia."
  },
  D: {
    name: "Defensa y Seguridad",
    interesTraits: ["Justicia","Equidad","Colaboración","Espíritu de equipo","Liderazgo"],
    aptitudTraits: ["Arriesgado","Solidario","Valiente","Enérgico","Persuasivo"],
    workStyle: "El perfil combina el interés por la justicia, la equidad y el trabajo en equipo con aptitudes de valentía, liderazgo y disposición al riesgo. Es un perfil que suele rendir bien bajo presión, asumir responsabilidad en situaciones críticas y encontrar sentido en proteger o hacer cumplir un orden.",
    careers: ["Ciencias Militares","Seguridad y Defensa","Criminología","Ciencias Policiales","Gestión de Riesgos y Emergencias","Marina Mercante","Aeronáutica"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles de mando, protección y respuesta ante situaciones críticas: liderar operativos, gestionar riesgos y emergencias, o coordinar equipos en contextos de alta exigencia. Con los años, estas trayectorias suelen abrir paso a posiciones de mando superior, planificación estratégica o formación de nuevas generaciones."
  },
  E: {
    name: "Ciencias Exactas y Agrarias",
    interesTraits: ["Clasificar","Numérico","Análisis y síntesis","Organización","Orden","Investigación"],
    aptitudTraits: ["Metódico","Analítico","Observador","Introvertido","Paciente","Seguro"],
    workStyle: "El perfil combina el interés por clasificar, investigar y organizar con aptitudes de método, observación y paciencia. Suele tratarse de una persona analítica, cómoda con el trabajo sostenido y minucioso, que prefiere apoyarse en evidencia y datos antes que en la intuición.",
    careers: ["Matemáticas","Física","Química","Agronomía","Biología","Ciencias Ambientales","Geología","Estadística","Ingeniería Agroindustrial","Medicina Veterinaria"],
    futureRoles: "A futuro, este perfil suele proyectarse hacia roles de investigación y análisis: generar y probar hipótesis, trabajar con datos y modelos, o aplicar ese conocimiento en el campo, el laboratorio o la industria. Con el tiempo, estas trayectorias suelen derivar en investigación académica, consultoría técnica especializada o gestión de proyectos científicos y ambientales."
  }
};

const CHA_KEY_INTERESES = {
  C: [98,12,64,53,85,1,78], H: [9,34,80,25,95,67,41], A: [21,45,96,57,28,11,50],
  S: [33,92,70,8,87,62,23], I: [75,6,19,38,60,27,83], D: [84,31,48,73,5,65,14],
  E: [77,42,88,17,93,32,68]
};

const CHA_KEY_APTITUDES = {
  C: [15,20,51,71,2,91,46], H: [63,74,30,56,72,89,86], A: [22,3,39,81,76,36,82],
  S: [69,44,40,16,29,52,4], I: [26,54,59,47,90,97,10], D: [13,37,66,58,18,24,43],
  E: [94,49,7,35,79,61,55]
};

const AF5_QUESTIONS = [
  "Hago bien los trabajos escolares (profesionales)",
  "Hago fácilmente amigos",
  "Tengo miedo de algunas cosas",
  "Soy muy criticado en casa",
  "Me cuido físicamente",
  "Mis superiores (profesores) me consideran un buen trabajador",
  "Soy una persona amigable",
  "Muchas cosas me ponen nervioso",
  "Me siento feliz en casa",
  "Me buscan para realizar actividades deportivas",
  "Trabajo mucho en clase (en el trabajo)",
  "Es difícil para mí hacer amigos",
  "Me asusto con facilidad",
  "Mi familia está decepcionada de mí",
  "Me considero elegante",
  "Mis superiores (profesores) me estiman",
  "Soy una persona alegre",
  "Cuando los mayores me dicen algo me pongo muy nervioso",
  "Mi familia me ayudaría en cualquier tipo de problemas",
  "Me gusta como soy físicamente",
  "Soy un buen trabajador (estudiante)",
  "Me cuesta hablar con desconocidos",
  "Me pongo nervioso cuando me pregunta el profesor (superior)",
  "Mis padres me dan confianza",
  "Soy bueno haciendo deporte",
  "Mis profesores (superiores) me consideran inteligente y trabajador",
  "Tengo muchos amigos",
  "Me siento nervioso",
  "Me siento querido por mis padres",
  "Soy una persona atractiva"
];

const AF5_REVERSED_ITEMS = [4, 12, 14, 22];

const AF5_DIMENSIONS = {
  academico: { name: "Académico / Laboral", items: [1,6,11,16,21,26] },
  social: { name: "Social", items: [2,7,12,17,22,27] },
  emocional: { name: "Emocional", items: [3,8,13,18,23,28], collectiveReversal: true },
  familiar: { name: "Familiar", items: [4,9,14,19,24,29] },
  fisico: { name: "Físico", items: [5,10,15,20,25,30] }
};

const AF5_DIM_INFO = {
  academico: {
    icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 6c-2-1.5-5-2-8-1v13c3-1 6-.5 8 1c2-1.5 5-2 8-1V5c-3-1-6-.5-8 1z"/><path d="M12 6v13"/></svg>`,
    def: "Cómo percibe su propio desempeño como estudiante o trabajador, y cómo cree que lo valoran sus profesores o superiores.",
    high: "Se percibe competente en su rol académico o laboral, y siente que las figuras de autoridad en ese entorno lo valoran positivamente. Esta percepción suele acompañarse de mayor motivación y mejor rendimiento sostenido.",
    medium: "Percibe su desempeño académico o laboral de forma similar a la mayoría de personas de su edad y contexto, sin sentirse especialmente destacado, pero tampoco cuestionado por profesores o superiores.",
    low: "Percibe su desempeño académico o laboral como insuficiente, o siente que no es reconocido por profesores o superiores. Esta percepción, aunque no siempre refleja el rendimiento real, puede afectar la motivación y el compromiso con la tarea."
  },
  social: {
    icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M14 15c2.5 0 5 1.8 5 5"/></svg>`,
    def: "Cómo percibe su facilidad para relacionarse, hacer amigos y mantener una red social.",
    high: "Se percibe sociable, con facilidad para vincularse y una red de amistades que considera sólida. Esto suele asociarse a mayor bienestar y mejor integración en grupos.",
    medium: "Percibe su facilidad para relacionarse dentro del rango esperable para su edad, se vincula sin especial dificultad, sin destacar tampoco por una sociabilidad excepcional.",
    low: "Percibe dificultad para relacionarse o hacer amigos con facilidad. No implica necesariamente aislamiento real, pero sí una vivencia de esfuerzo o incomodidad en lo social que vale la pena explorar."
  },
  emocional: {
    icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M20.8 8.6c0 5-8.8 10-8.8 10s-8.8-5-8.8-10a4.4 4.4 0 018-2.6 4.4 4.4 0 019.6 2.6z"/></svg>`,
    def: "El control percibido sobre las propias reacciones emocionales ante situaciones cotidianas, especialmente frente a figuras de autoridad.",
    high: "Se percibe con buen control emocional, respondiendo con calma ante situaciones que podrían generar nerviosismo. Suele asociarse a mayor autocontrol y menor ansiedad ante la evaluación o la exposición.",
    medium: "Muestra un nivel de control emocional dentro de lo esperable, presenta cierto nerviosismo ante situaciones puntuales de exposición, sin que esto sea marcadamente mayor a lo habitual en su grupo de edad.",
    low: "Reporta nerviosismo frecuente y mayor reactividad emocional, en particular frente a figuras de autoridad o situaciones de exposición. Es una dimensión especialmente relevante de monitorear si se combina con otras señales de ansiedad."
  },
  familiar: {
    icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 21V9l9-6 9 6v12"/><path d="M9 21v-6h6v6"/></svg>`,
    def: "La percepción de aceptación, confianza y apoyo dentro del núcleo familiar.",
    high: "Percibe a su familia como una fuente confiable de apoyo, afecto y confianza. Es uno de los factores protectores más importantes del autoconcepto global.",
    medium: "Percibe su vínculo familiar dentro de un rango esperable, sin una sensación marcada de crítica o distancia, aunque tampoco reporta un apoyo excepcionalmente fuerte.",
    low: "Percibe crítica, decepción o distancia dentro del núcleo familiar. Por su fuerte asociación con el bienestar emocional general, es una de las dimensiones que más conviene abordar en la sesión de devolución."
  },
  fisico: {
    icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>`,
    def: "La percepción personal sobre aspectos físicos y la relación con la actividad corporal.",
    high: "Reporta una percepción positiva en esta dimensión. Este resultado se interpreta en términos de autopercepción y relación con la actividad corporal, no como una valoración objetiva de apariencia física.",
    medium: "Su autopercepción en esta dimensión se ubica en un rango intermedio. El resultado debe entenderse como una percepción subjetiva y no como una medida objetiva de condición o apariencia física.",
    low: "Reporta una autopercepción menos favorable en esta dimensión. Conviene explorar, en contexto profesional, cómo se relaciona con la actividad corporal y el bienestar, sin convertir el resultado en una valoración de apariencia física."
  }
};

const AF5_NORM_TABLES = {
  primaria: {
    F: [
      [99, [9.43,9.9], [9.71,9.9], [8.51,9.9], null, [9.28,9.9]],
      [97, null, [9.53,9.7], [8.07,8.5], [8.84,9.27], null],
      [95, [9.01,9.42], [9.13,9.52], [7.84,8.06], [9.78,9.9], [8.56,8.83]],
      [93, null, null, [7.33,7.83], null, [8.35,8.55]],
      [90, [8.75,9.0], [8.79,9.12], [6.89,7.32], [9.63,9.77], [7.98,8.34]],
      [85, [8.51,8.74], [8.53,8.78], [6.51,6.88], [9.48,9.62], [7.74,7.97]],
      [80, [8.01,8.5], [8.34,8.52], [6.18,6.5], [9.31,9.47], [7.48,7.73]],
      [75, null, [8.16,8.33], [5.81,6.17], [9.16,9.3], [7.16,7.47]],
      [70, [7.51,8.0], [7.99,8.15], [5.58,5.8], [8.98,9.15], [6.68,7.15]],
      [65, null, [7.81,7.98], [5.36,5.57], [8.83,8.97], null],
      [60, [7.2,7.5], [7.59,7.8], [4.84,5.35], [8.66,8.82], [6.26,6.67]],
      [55, [6.93,7.19], [7.41,7.58], null, [8.51,8.65], null],
      [50, [6.59,6.92], [7.23,7.4], [4.61,4.83], [8.24,8.5], [5.97,6.25]],
      [45, [6.27,6.58], [7.01,7.22], [4.37,4.6], null, [5.66,5.96]],
      [40, [5.84,6.26], [6.76,7.0], [4.04,4.36], [8.01,8.23], [5.37,5.65]],
      [35, null, [6.51,6.75], [3.68,4.03], [7.81,8.0], [5.04,5.36]],
      [30, [5.34,5.83], [6.26,6.5], [3.38,3.67], [7.59,7.8], [4.59,5.03]],
      [25, [5.0,5.33], [6.01,6.25], [3.01,3.37], [7.29,7.58], [4.36,4.58]],
      [20, [4.68,4.99], [5.68,6.0], [2.53,3.0], [6.89,7.28], [3.98,4.35]],
      [15, [3.91,4.67], [5.21,5.67], [2.09,2.52], [6.49,6.88], [3.46,3.97]],
      [10, [3.49,3.9], [4.84,5.2], [1.54,2.08], [6.04,6.48], [3.0,3.45]],
      [7, [3.12,3.48], [4.63,4.83], null, [5.51,6.03], [2.72,2.99]],
      [5, [2.68,3.11], [4.16,4.62], [1.24,1.53], [4.85,5.5], [2.51,2.71]],
      [3, [1.27,2.67], [3.18,4.15], [0.34,1.23], [3.34,4.84], [1.45,2.5]],
      [1, [0,1.26], [0,3.17], [0,0.33], [0,3.33], [0,1.44]],
    ],
    M: [
      [99, [9.26,9.9], [9.71,9.9], [9.03,9.9], null, [9.57,9.9]],
      [97, null, [9.53,9.7], [8.57,9.02], [9.78,9.9], [9.36,9.56]],
      [95, [9.03,9.25], [9.13,9.52], [8.14,8.56], null, [9.04,9.35]],
      [93, [8.81,9.02], null, null, null, null],
      [90, [8.43,8.8], [8.79,9.12], [7.68,8.13], [9.63,9.77], [8.68,9.03]],
      [85, [8.18,8.42], [8.53,8.78], [7.22,7.67], [9.48,9.62], [8.46,8.67]],
      [80, [7.65,8.17], [8.34,8.52], [6.84,7.21], [9.31,9.47], [8.14,8.45]],
      [75, null, [8.16,8.33], [6.5,6.83], [9.16,9.3], [7.84,8.13]],
      [70, [7.36,7.64], [7.99,8.15], [5.84,6.49], [8.98,9.15], [7.59,7.83]],
      [65, [7.0,7.35], [7.81,7.98], null, [8.83,8.97], [7.34,7.58]],
      [60, [6.49,6.99], [7.59,7.8], [5.45,5.83], [8.66,8.82], [6.84,7.33]],
      [55, null, [7.41,7.58], null, [8.51,8.65], null],
      [50, [6.02,6.48], [7.23,7.4], [5.18,5.44], [8.24,8.5], [6.39,6.83]],
      [45, null, [7.01,7.22], [4.84,5.17], null, null],
      [40, [5.46,6.01], [6.76,7.0], [4.51,4.83], [8.01,8.23], [5.99,6.38]],
      [35, null, [6.51,6.75], [4.26,4.5], [7.81,8.0], null],
      [30, [5.16,5.45], [6.26,6.5], [4.04,4.25], [7.59,7.8], [5.67,5.98]],
      [25, [4.6,5.15], [6.01,6.25], [3.57,4.03], [7.29,7.58], [5.33,5.66]],
      [20, [4.01,4.59], [5.68,6.0], [3.2,3.56], [6.89,7.28], [4.82,5.32]],
      [15, [3.51,4.0], [5.21,5.67], [2.51,3.19], [6.49,6.88], [4.31,4.81]],
      [10, [3.22,3.5], [4.84,5.2], [1.85,2.5], [6.04,6.48], [3.84,4.3]],
      [7, [2.73,3.21], [4.63,4.83], null, [5.51,6.03], [3.34,3.83]],
      [5, [2.18,2.72], [4.16,4.62], [1.4,1.84], [4.85,5.5], [2.71,3.33]],
      [3, [1.0,2.17], [3.18,4.15], [0.88,1.39], [3.34,4.84], [1.24,2.7]],
      [1, [0,0.99], [0,3.17], [0,0.87], [0,3.33], [0,1.23]],
    ],
  },
  eso12: {
    F: [
      [99, [9.32,9.9], [9.71,9.9], [8.45,9.9], null, [8.59,9.9]],
      [97, [8.98,9.31], [9.53,9.7], [8.13,8.44], [9.76,9.9], [8.29,8.58]],
      [95, [8.71,8.97], [9.36,9.52], [7.68,8.12], null, [8.01,8.28]],
      [93, null, [9.14,9.35], [7.35,7.67], null, [7.71,8.0]],
      [90, [8.39,8.7], [8.88,9.13], [6.87,7.34], [9.61,9.75], [7.2,7.7]],
      [85, [8.09,8.38], [8.61,8.87], [6.46,6.86], [9.51,9.6], [6.9,7.19]],
      [80, [7.8,8.08], [8.34,8.6], [6.1,6.45], [9.31,9.5], [6.58,6.89]],
      [75, [7.51,7.79], [8.17,8.33], [5.73,6.09], [9.12,9.3], [6.29,6.57]],
      [70, [7.26,7.5], [7.99,8.16], [5.44,5.72], [8.94,9.11], [6.01,6.28]],
      [65, [6.99,7.25], [7.81,7.98], [5.2,5.43], [8.78,8.93], [5.76,6.0]],
      [60, [6.68,6.98], [7.62,7.8], [4.94,5.19], [8.54,8.77], [5.51,5.75]],
      [55, [6.34,6.67], [7.39,7.61], [4.68,4.93], [8.33,8.53], [5.31,5.5]],
      [50, [6.01,6.33], [7.16,7.38], [4.43,4.67], [8.16,8.32], [4.92,5.3]],
      [45, [5.76,6.0], [6.98,7.15], [4.16,4.42], [7.96,8.15], [4.59,4.91]],
      [40, [5.36,5.75], [6.74,6.97], [3.93,4.15], [7.74,7.95], [4.34,4.58]],
      [35, [5.09,5.35], [6.52,6.73], [3.56,3.92], [7.51,7.73], [4.01,4.33]],
      [30, [4.78,5.08], [6.31,6.51], [3.38,3.55], [7.16,7.5], [3.69,4.0]],
      [25, [4.19,4.77], [6.08,6.32], [3.07,3.37], [6.76,7.15], [3.36,3.68]],
      [20, [3.51,4.18], [5.76,6.07], [2.67,3.06], [6.42,6.75], [2.88,3.35]],
      [15, [2.84,3.5], [5.34,5.75], [2.09,2.66], [5.92,6.41], [2.44,2.87]],
      [10, [2.37,2.83], [4.93,5.33], [1.76,2.08], [5.38,5.91], [2.17,2.43]],
      [7, [1.85,2.36], [4.51,4.92], [1.58,1.75], [5.01,5.37], [1.91,2.16]],
      [5, [1.33,1.84], [3.71,4.5], [1.0,1.57], [4.3,5.0], [1.56,1.9]],
      [3, [0.59,1.32], [2.76,3.7], [0.25,0.99], [2.66,4.29], [0.99,1.55]],
      [1, [0,0.58], [0,2.75], [0,0.24], [0,2.65], [0,0.98]],
    ],
    M: [
      [99, [8.97,9.9], [9.71,9.9], [8.84,9.9], null, [9.06,9.9]],
      [97, [8.74,8.96], [9.53,9.7], [8.66,8.83], null, null],
      [95, [8.54,8.73], [9.36,9.52], [8.29,8.65], [9.76,9.9], [8.8,9.05]],
      [93, [8.31,8.53], [9.14,9.35], [8.03,8.28], null, [8.59,8.79]],
      [90, [7.89,8.3], [8.88,9.13], [7.62,8.02], [9.61,9.75], [8.14,8.58]],
      [85, [7.57,7.88], [8.61,8.87], [7.26,7.61], [9.51,9.6], [7.91,8.13]],
      [80, [7.16,7.56], [8.34,8.6], [6.93,7.25], [9.31,9.5], [7.61,7.9]],
      [75, [6.84,7.15], [8.17,8.33], [6.62,6.92], [9.12,9.3], [7.34,7.6]],
      [70, [6.55,6.83], [7.99,8.16], [6.28,6.58], [8.94,9.11], [7.07,7.33]],
      [65, [6.2,6.54], [7.81,7.98], [6.09,6.27], [8.78,8.93], [6.78,7.06]],
      [60, [5.93,6.19], [7.62,7.8], [5.68,6.08], [8.54,8.77], [6.57,6.77]],
      [55, [5.66,5.92], [7.39,7.61], [5.37,5.67], [8.33,8.53], [6.33,6.56]],
      [50, [5.34,5.65], [7.16,7.38], [5.09,5.36], [8.16,8.32], [6.14,6.32]],
      [45, [5.01,5.33], [6.98,7.15], [4.78,5.08], [7.96,8.15], [5.84,6.13]],
      [40, [4.68,5.0], [6.74,6.97], [4.51,4.77], [7.74,7.95], [5.59,5.83]],
      [35, [4.37,4.67], [6.52,6.73], [4.26,4.5], [7.51,7.73], [5.24,5.58]],
      [30, [4.03,4.36], [6.31,6.51], [4.0,4.25], [7.16,7.5], [4.87,5.23]],
      [25, [3.69,4.02], [6.08,6.32], [3.6,3.99], [6.76,7.15], [4.51,4.86]],
      [20, [3.22,3.68], [5.76,6.07], [3.11,3.59], [6.42,6.75], [4.05,4.5]],
      [15, [2.68,3.21], [5.34,5.75], [2.69,3.1], [5.92,6.41], [3.61,4.04]],
      [10, [2.24,2.67], [4.93,5.33], [2.41,2.68], [5.38,5.91], [3.25,3.6]],
      [7, [1.93,2.23], [4.51,4.92], [2.04,2.4], [5.01,5.37], [2.86,3.24]],
      [5, [1.6,1.92], [3.71,4.5], [1.73,2.03], [4.3,5.0], [2.51,2.85]],
      [3, [0.68,1.59], [2.76,3.7], [1.12,1.72], [2.66,4.29], [1.71,2.5]],
      [1, [0,0.67], [0,2.75], [0,1.11], [0,2.65], [0,1.7]],
    ],
  },
  eso34: {
    F: [
      [99, [9.04,9.9], [9.66,9.9], [8.39,9.9], [9.84,9.9], [8.29,9.9]],
      [97, [8.83,9.03], [9.54,9.65], [7.98,8.38], null, [7.96,8.28]],
      [95, [8.68,8.82], [9.36,9.53], [7.63,7.97], [9.69,9.83], [7.68,7.95]],
      [93, [8.38,8.67], [9.16,9.35], [7.34,7.62], null, [7.42,7.67]],
      [90, [8.05,8.37], [8.91,9.15], [6.81,7.33], [9.53,9.68], [7.11,7.41]],
      [85, [7.76,8.04], [8.68,8.9], [6.48,6.8], [9.38,9.52], [6.78,7.1]],
      [80, [7.43,7.75], [8.48,8.67], [6.01,6.47], [9.23,9.37], [6.43,6.77]],
      [75, [7.18,7.42], [8.29,8.47], [5.84,6.0], [9.08,9.22], [6.18,6.42]],
      [70, [7.01,7.17], [8.09,8.28], [5.51,5.83], [8.56,9.07], [5.84,6.17]],
      [65, [6.76,7.0], [7.93,8.08], [5.18,5.5], [8.56,8.55], [5.53,5.83]],
      [60, [6.46,6.75], [7.76,7.92], [4.94,5.17], [8.53,8.55], [5.26,5.52]],
      [55, [6.18,6.45], [7.59,7.75], [4.68,4.93], [8.33,8.55], [5.01,5.25]],
      [50, [5.93,6.17], [7.41,7.58], [4.43,4.67], [8.14,8.32], [4.76,5.0]],
      [45, [5.72,5.92], [7.19,7.4], [4.18,4.42], [7.93,8.13], [4.52,4.75]],
      [40, [5.51,5.71], [7.01,7.18], [3.96,4.17], [7.73,7.92], [4.28,4.51]],
      [35, [5.26,5.5], [6.78,7.0], [3.68,3.95], [7.48,7.72], [4.01,4.27]],
      [30, [5.01,5.25], [6.58,6.77], [3.36,3.67], [7.13,7.47], [3.68,4.0]],
      [25, [4.52,5.0], [6.26,6.57], [3.02,3.35], [6.78,7.12], [3.34,3.67]],
      [20, [4.18,4.51], [5.85,6.25], [2.74,3.01], [6.38,6.77], [2.99,3.33]],
      [15, [3.51,4.17], [5.43,5.84], [2.33,2.73], [5.76,6.37], [2.38,2.98]],
      [10, [3.01,3.5], [5.01,5.42], [2.01,2.32], [5.18,5.75], [2.0,2.37]],
      [7, [2.64,3.0], [4.68,5.0], [1.79,2.0], [4.51,5.17], [1.72,1.99]],
      [5, [2.09,2.63], [4.19,4.67], [1.48,1.78], [3.88,4.5], [1.41,1.71]],
      [3, [1.36,2.08], [3.43,4.18], [0.92,1.47], [2.44,3.87], [1.01,1.4]],
      [1, [0,1.35], [0,3.42], [0,0.91], [0,2.43], [0,1.0]],
    ],
    M: [
      [99, [8.86,9.9], [9.66,9.9], [8.88,9.9], [9.84,9.9], [9.28,9.9]],
      [97, [8.59,8.85], [9.54,9.65], [8.67,8.87], null, [9.08,9.27]],
      [95, [8.43,8.58], [9.36,9.53], [8.49,8.66], [9.69,9.83], [8.8,9.07]],
      [93, [8.18,8.42], [9.16,9.35], [8.1,8.48], null, [8.53,8.79]],
      [90, [7.76,8.17], [8.91,9.15], [7.73,8.09], [9.53,9.68], [8.14,8.52]],
      [85, [7.48,7.75], [8.68,8.9], [7.33,7.72], [9.38,9.52], [7.88,8.13]],
      [80, [7.21,7.47], [8.48,8.67], [7.01,7.32], [9.23,9.37], [7.68,7.87]],
      [75, [7.0,7.2], [8.29,8.47], [6.69,7.0], [9.08,9.22], [7.46,7.67]],
      [70, [6.73,6.99], [8.09,8.28], [6.18,6.68], [8.89,9.07], [7.23,7.45]],
      [65, [6.61,6.72], [7.93,8.08], [6.18,6.48], [8.73,8.88], [6.99,7.22]],
      [60, [6.26,6.6], [7.76,7.92], [5.84,6.17], [8.56,8.72], [6.78,6.98]],
      [55, [6.09,6.25], [7.59,7.75], [5.59,5.83], [8.33,8.55], [6.53,6.77]],
      [50, [5.84,6.08], [7.41,7.58], [5.34,5.58], [8.14,8.32], [6.32,6.52]],
      [45, [5.59,5.83], [7.19,7.4], [5.09,5.33], [7.94,8.13], [5.86,6.31]],
      [40, [5.34,5.58], [7.01,7.18], [5.09,5.33], [7.73,7.93], [5.87,6.14]],
      [35, [4.98,5.33], [6.78,7.0], [4.84,5.08], [7.48,7.72], [5.56,5.86]],
      [30, [4.68,4.97], [6.58,6.77], [4.34,4.83], [7.13,7.47], [5.34,5.55]],
      [25, [4.34,4.67], [6.26,6.57], [4.34,4.58], [6.78,7.12], [5.03,5.33]],
      [20, [3.84,4.33], [5.85,6.25], [3.84,4.33], [6.38,6.77], [4.64,5.02]],
      [15, [3.35,3.83], [5.43,5.84], [3.34,3.83], [5.76,6.37], [4.03,4.63]],
      [10, [2.9,3.34], [5.01,5.42], [3.01,3.33], [5.18,5.75], [3.53,4.02]],
      [7, [2.6,2.89], [4.68,5.0], [2.76,3.0], [4.51,5.17], [3.2,3.52]],
      [5, [1.88,2.59], [4.19,4.67], [2.43,2.75], [3.88,4.5], [2.49,3.19]],
      [3, [0.9,1.87], [3.43,4.18], [1.96,2.42], [2.44,3.87], [1.54,2.48]],
      [1, [0,0.89], [0,3.42], [0,1.95], [0,2.43], [0,1.53]],
    ],
  },
  bach: {
    F: [
      [99, [8.81,9.9], [9.59,9.9], [8.35,9.9], [9.84,9.9], [7.93,9.9]],
      [97, [8.65,8.8], [9.31,9.58], [7.93,8.34], null, [7.83,7.92]],
      [95, [8.36,8.64], [9.16,9.3], [7.62,7.92], [9.69,9.83], [7.38,7.82]],
      [93, [8.1,8.35], [8.94,9.15], [7.16,7.61], null, [7.09,7.37]],
      [90, [7.75,8.09], [8.68,8.93], [6.59,7.15], [9.35,9.68], [6.68,7.08]],
      [85, [7.34,7.74], [8.43,8.67], [6.07,6.58], null, [6.34,6.67]],
      [80, [7.06,7.33], [8.21,8.42], [5.84,6.08], [9.11,9.34], [6.01,6.33]],
      [75, [6.84,7.05], [8.02,8.2], [5.59,5.83], [8.79,9.1], [5.76,6.0]],
      [70, [6.68,6.83], [7.84,8.01], [5.33,5.58], null, [5.49,5.75]],
      [65, [6.51,6.67], [7.68,7.83], [5.01,5.32], null, [5.18,5.48]],
      [60, [6.34,6.5], [7.51,7.67], [4.79,5.0], [8.64,8.78], [5.0,5.17]],
      [55, [6.09,6.33], [7.34,7.5], [4.57,4.78], [8.49,8.63], [4.73,4.99]],
      [50, [5.93,6.08], [7.24,7.33], [4.21,4.56], [8.31,8.48], [4.53,4.72]],
      [45, [5.59,5.92], [7.01,7.23], [4.09,4.2], [8.09,8.3], [4.34,4.52]],
      [40, [5.41,5.58], [6.84,7.0], [4.01,4.2], [7.89,8.08], [4.01,4.33]],
      [35, null, [6.59,6.83], [3.7,4.0], [7.68,7.88], null],
      [30, [5.01,5.17], [6.34,6.58], [3.36,3.69], [7.36,7.67], [3.68,4.0]],
      [25, [4.68,5.0], [5.98,6.33], [3.18,3.45], [6.86,7.35], [3.46,3.67]],
      [20, [4.34,4.67], [5.64,5.97], [2.85,3.17], [6.25,6.85], [3.18,3.45]],
      [15, [3.97,4.33], [5.09,5.63], [2.43,2.84], [5.63,6.24], [2.65,3.17]],
      [10, [3.5,3.96], [4.71,5.08], [2.12,2.42], [4.94,5.62], [2.21,2.64]],
      [7, [3.24,3.49], [4.48,4.7], [1.87,2.11], [4.75,4.93], [1.89,2.2]],
      [5, [2.86,3.23], [4.02,4.47], [1.48,1.86], [3.71,4.74], [1.71,1.88]],
      [3, [2.21,2.85], [3.04,4.01], [0.59,1.47], [1.88,3.7], [1.09,1.7]],
      [1, [0,2.2], [0,3.03], [0,0.58], [0,1.87], [0,1.08]],
    ],
    M: [
      [99, [8.91,9.9], [9.59,9.9], [8.97,9.9], [9.71,9.9], [8.94,9.9]],
      [97, [8.36,8.9], [9.31,9.58], [8.7,8.96], null, [8.6,8.93]],
      [95, [8.05,8.35], [9.16,9.3], [8.43,8.69], [9.44,9.7], [8.17,8.59]],
      [93, null, [8.94,9.15], [8.01,8.42], null, null],
      [90, [7.72,8.04], [8.68,8.93], [7.67,8.0], [9.27,9.43], [7.93,8.16]],
      [85, [7.34,7.71], [8.43,8.67], [7.36,7.67], [8.99,9.26], [7.59,7.92]],
      [80, [7.08,7.33], [8.21,8.42], [7.14,7.35], [8.73,8.98], [7.38,7.58]],
      [75, [6.83,7.07], [8.02,8.2], [6.88,7.13], null, [7.14,7.37]],
      [70, [6.28,6.82], [7.84,8.01], [6.68,6.87], [8.53,8.72], [6.84,7.13]],
      [65, null, [7.68,7.83], [6.42,6.67], [8.34,8.52], [6.59,6.83]],
      [60, [6.06,6.27], [7.51,7.67], [6.01,6.41], [8.14,8.33], [6.18,6.35]],
      [55, [5.79,6.05], [7.34,7.5], [5.78,6.0], [7.98,8.13], [5.99,6.17]],
      [50, [5.54,5.78], [7.24,7.33], [5.5,5.77], [7.59,7.97], [5.7,5.98]],
      [45, [5.18,5.53], [7.01,7.23], [5.3,5.49], [7.26,7.58], [5.18,5.69]],
      [40, [4.93,5.17], [6.84,7.0], [4.99,5.29], [7.01,7.25], [5.1,5.17]],
      [35, [4.68,4.92], [6.59,6.83], [4.68,4.98], [6.81,7.0], [4.91,5.17]],
      [30, [4.15,4.67], [6.34,6.58], [4.5,4.67], [6.51,6.8], [4.58,4.9]],
      [25, null, [5.98,6.33], [4.16,4.49], [6.08,6.5], [4.18,4.57]],
      [20, [3.74,4.14], [5.64,5.97], [3.69,4.15], [5.19,6.07], [3.8,4.17]],
      [15, [3.3,3.73], [5.09,5.63], [3.19,3.68], [4.79,5.18], [3.43,3.79]],
      [10, [3.0,3.29], [4.71,5.08], [2.62,3.18], [4.49,4.78], [3.16,3.42]],
      [7, [2.68,2.99], [4.48,4.7], [2.48,2.61], [3.6,4.48], [2.86,3.15]],
      [5, [2.3,2.67], [4.02,4.47], [1.93,2.47], [2.86,3.59], [2.05,2.85]],
      [3, [1.52,2.29], [3.04,4.01], [0,1.92], [2.86,2.85], [2.05,2.04]],
      [1, [0,1.51], [0,3.03], [0,1.92], [0,2.85], [0,2.04]],
    ],
  },
  universitario: {
    F: [
      [99, [9.0,9.9], [9.45,9.9], [8.23,9.9], [9.63,9.9], [7.83,9.9]],
      [97, [8.71,8.99], [9.18,9.44], [7.84,8.22], null, [7.51,7.82]],
      [95, [8.51,8.7], [9.01,9.17], [7.66,7.83], null, [7.24,7.5]],
      [93, [8.34,8.5], [8.79,9.0], [7.25,7.65], [9.38,9.62], [6.51,7.23]],
      [90, [8.01,8.33], [8.51,8.78], [6.74,7.24], null, [6.18,6.5]],
      [85, [7.68,8.0], [8.28,8.5], [6.59,6.83], [9.05,9.37], [5.93,6.17]],
      [80, [7.5,7.67], [8.08,8.27], [6.18,6.58], null, [5.76,5.92]],
      [75, [7.34,7.49], [7.86,8.07], [5.94,6.17], [8.76,9.04], [5.51,5.75]],
      [70, [7.18,7.33], [7.68,7.85], [5.69,5.93], null, [5.35,5.5]],
      [65, [7.01,7.17], [7.51,7.67], [5.47,5.68], [8.58,8.75], [5.11,5.34]],
      [60, [6.84,7.0], [7.34,7.5], [5.18,5.46], [8.41,8.57], [4.85,5.1]],
      [55, [6.68,6.83], [7.09,7.33], [4.93,5.17], [8.24,8.4], [4.51,4.84]],
      [50, [6.5,6.67], [6.84,7.08], [4.66,4.92], [8.24,8.23], [4.68,4.5]],
      [45, [6.26,6.49], [6.59,6.83], [4.43,4.65], [7.76,8.04], [4.21,4.5]],
      [40, [6.01,6.25], [6.34,6.58], [4.18,4.42], [7.51,7.75], [4.01,4.2]],
      [35, [5.76,6.0], [6.09,6.33], [3.86,4.17], [7.51,7.51], [4.01,4.0]],
      [30, [5.53,5.75], [5.84,6.08], [3.34,3.85], [7.2,7.5], [3.76,4.0]],
      [25, [5.34,5.52], [5.59,5.83], [3.34,3.59], [6.84,7.19], [3.18,3.75]],
      [20, [5.01,5.33], [5.26,5.58], [2.93,3.33], [6.33,6.83], [2.27,3.17]],
      [15, [4.68,5.0], [4.86,5.25], [2.54,2.92], [5.44,6.32], [2.27,2.26]],
      [10, [4.3,4.67], [4.41,4.85], [2.31,2.53], [4.89,5.43], [1.82,2.26]],
      [7, [4.01,4.29], [4.11,4.4], [2.03,2.3], [4.55,4.88], [1.6,1.81]],
      [5, [3.78,4.0], [3.68,4.1], [1.78,2.02], [3.48,4.54], [1.82,1.59]],
      [3, [2.9,3.77], [2.46,3.67], [1.26,1.77], [2.05,3.47], [1.22,1.81]],
      [1, [0,2.89], [0,2.45], [0,1.25], [0,2.04], [0,1.21]],
    ],
    M: [
      [99, [8.51,9.9], [9.45,9.9], [8.67,9.9], [9.53,9.9], [8.09,9.9]],
      [97, [8.27,8.5], [9.18,9.44], [8.01,8.66], null, [7.61,8.08]],
      [95, [7.84,8.26], [9.01,9.17], [8.17,8.66], [9.14,9.52], [7.61,8.08]],
      [93, null, [8.79,9.0], [7.73,8.16], null, null],
      [90, [7.42,7.83], [8.51,8.78], [7.34,7.72], [8.91,9.13], [7.31,7.6]],
      [85, null, [8.28,8.5], [7.01,7.33], null, [6.96,7.3]],
      [80, [7.08,7.41], [8.08,8.27], [6.68,7.0], [8.54,8.9], [6.47,6.95]],
      [75, null, [7.86,8.07], null, null, null],
      [70, [6.68,7.07], [7.68,7.85], [6.34,6.67], [8.33,8.53], [6.01,6.46]],
      [65, null, [7.51,7.67], null, [8.08,8.32], null],
      [60, [6.34,6.67], [7.34,7.5], [5.84,6.33], [7.68,8.07], [5.68,6.0]],
      [55, null, [7.09,7.33], null, null, null],
      [50, [6.01,6.33], [6.84,7.08], [5.4,5.83], [7.43,7.67], [5.34,5.67]],
      [45, null, [6.59,6.83], [5.18,5.39], null, [4.93,5.33]],
      [40, [5.79,6.0], [6.34,6.58], [4.95,5.17], [6.86,7.42], [4.51,4.92]],
      [35, [5.54,5.78], [6.09,6.33], [4.67,4.94], null, null],
      [30, [5.34,5.53], [5.84,6.08], [4.47,4.66], [6.56,6.85], [4.09,4.5]],
      [25, null, [5.59,5.83], null, null, null],
      [20, [4.68,5.33], [5.26,5.58], [4.18,4.46], [6.0,6.28], [3.39,4.08]],
      [15, [4.32,4.67], [4.86,5.25], [3.82,4.17], [5.35,5.99], null],
      [10, [4.08,4.31], [4.41,4.85], [3.34,3.81], [4.63,5.34], [3.09,3.38]],
      [7, [3.46,4.07], [4.11,4.4], [2.76,3.08], [4.18,4.62], [2.23,2.75]],
      [5, [3.13,3.45], [3.68,4.1], [3.01,3.33], [3.61,4.17], [1.44,2.22]],
      [3, [2.57,3.12], [2.46,3.67], [2.6,3.0], [3.61,3.6], [1.22,1.43]],
      [1, [0,2.56], [0,2.45], [0,2.59], [0,3.6], [0,1.21]],
    ],
  },
  adulto: {
    F: [
      [99, [9.76,9.9], [9.76,9.9], [9.03,9.9], null, [7.84,9.9]],
      [97, null, [9.59,9.75], [8.76,9.02], null, [7.55,7.83]],
      [95, null, [9.17,9.58], [8.28,8.75], [9.76,9.9], [6.88,7.54]],
      [93, null, null, null, null, [6.62,6.87]],
      [90, [9.44,9.75], [8.93,9.16], [7.7,8.27], [9.61,9.75], [6.18,6.61]],
      [85, [9.09,9.43], [8.66,8.92], [6.99,7.69], [9.46,9.6], [5.93,6.17]],
      [80, null, [8.28,8.65], [6.3,6.98], [9.3,9.45], [5.53,5.92]],
      [75, [8.73,9.08], [8.07,8.27], null, [9.11,9.29], [5.18,5.52]],
      [70, null, [7.83,8.06], [6.63,6.98], [8.95,9.1], [4.88,5.17]],
      [65, [8.33,8.72], [7.64,7.82], [6.3,6.62], [8.81,8.94], [4.34,4.87]],
      [60, null, [7.34,7.63], [5.84,6.29], [8.51,8.8], null],
      [55, [8.01,8.32], [7.01,7.33], [5.29,5.83], [8.18,8.5], [4.02,4.33]],
      [50, null, [6.83,7.0], null, null, null],
      [45, [7.69,8.0], [6.64,6.82], [4.84,5.28], [8.0,8.17], [3.79,4.01]],
      [40, null, [6.43,6.63], null, [7.68,7.99], null],
      [35, [7.43,7.68], [6.16,6.42], [4.54,4.83], [7.44,7.67], [3.38,3.78]],
      [30, [6.9,7.42], [5.84,6.15], [4.24,4.53], [7.13,7.43], [3.02,3.37]],
      [25, [6.51,6.89], [5.51,5.83], [3.94,4.23], [6.66,7.12], [2.56,3.01]],
      [20, [5.84,6.5], [5.01,5.5], [3.42,3.93], [6.17,6.65], [2.32,2.55]],
      [15, [5.48,5.83], [4.68,5.0], [2.98,3.41], [5.82,6.16], [1.95,2.31]],
      [10, [5.01,5.47], [4.52,4.67], null, [5.39,5.81], [1.57,1.94]],
      [7, [4.56,5.0], [4.18,4.51], [1.71,2.31], [4.68,5.38], [1.26,1.7]],
      [5, [3.64,4.55], [2.89,4.17], [1.26,1.7], [3.73,4.67], [0.95,1.56]],
      [3, [0,3.63], [0,2.88], [0,1.25], [0,3.72], [0,0.94]],
      [1, [0,3.63], [0,2.88], [0,1.25], [0,3.72], [0,0.94]],
    ],
    M: [
      [99, [9.78,9.9], [9.76,9.9], [9.59,9.9], null, [8.73,9.9]],
      [97, null, [9.59,9.75], [9.18,9.58], [9.76,9.9], [8.38,8.72]],
      [95, null, [9.17,9.58], [8.85,9.17], null, [8.09,8.37]],
      [93, null, [9.17,9.58], null, null, null],
      [90, [9.22,9.49], [8.93,9.16], [8.46,8.84], [9.61,9.75], [8.09,8.37]],
      [85, [9.0,9.21], [8.66,8.92], [8.05,8.45], [9.46,9.6], [7.71,8.08]],
      [80, [8.67,8.99], [8.28,8.65], [7.68,8.04], [9.3,9.45], [7.43,7.7]],
      [75, [8.19,8.66], [8.07,8.27], null, [9.11,9.29], [7.01,7.42]],
      [70, null, [7.83,8.06], [6.9,7.17], [8.95,9.1], [6.45,7.0]],
      [65, [7.96,8.18], [7.64,7.82], [6.68,6.89], [8.81,8.94], null],
      [60, [7.56,7.95], [7.34,7.63], [6.34,6.67], [8.51,8.8], [5.61,5.98]],
      [55, null, [7.01,7.33], [5.71,5.98], [8.18,8.5], null],
      [50, [7.18,7.55], [6.83,7.0], [5.99,6.33], [8.0,8.17], [4.51,5.07]],
      [45, null, [6.64,6.82], null, [7.68,7.99], null],
      [40, [6.79,7.17], [6.43,6.63], [5.71,5.98], [7.44,7.67], [4.18,4.5]],
      [35, null, [6.16,6.42], [5.34,5.7], [7.13,7.43], [3.68,4.17]],
      [30, [6.34,6.78], [5.84,6.15], [5.01,5.33], [6.66,7.12], [3.68,4.17]],
      [25, [6.04,6.33], [5.51,5.83], [4.65,5.0], [6.17,6.65], [3.28,3.67]],
      [20, [5.5,6.03], [5.01,5.5], [4.35,4.64], [5.82,6.16], [2.68,3.27]],
      [15, [5.01,5.49], [4.68,5.0], null, [5.39,5.81], [2.22,2.67]],
      [10, null, [4.52,4.67], null, [4.68,5.38], [1.88,2.21]],
      [7, [4.34,5.0], [4.18,4.51], [3.01,3.67], [3.73,4.67], [0.76,1.87]],
      [5, [3.55,4.33], [2.89,4.17], [2.28,3.0], [3.73,4.67], [0.76,1.87]],
      [3, [0,3.54], [0,2.88], [0,2.27], [0,3.72], [0,0.75]],
      [1, [0,3.54], [0,2.88], [0,2.27], [0,3.72], [0,0.75]],
    ],
  },
};

const AF5_DIM_INDEX = { academico:1, social:2, emocional:3, familiar:4, fisico:5 };

const CHT_AREAS = {
  actitud: { name: "Actitud general hacia el estudio", items: [
    "Estudio porque quiero aprender, no solo por obtener una nota.",
    "Me pongo metas claras antes de empezar a estudiar una materia.",
    "Mantengo la motivación aunque el tema no me guste al principio.",
    "No postergo el estudio hasta último momento.",
    "No me distraigo pensando en otras cosas mientras estudio.",
    "Considero que estudiar es una inversión para mi futuro, no una obligación.",
    "Me siento capaz de superar las materias que me resultan difíciles.",
    "Prefiero entender un tema a memorizarlo sin comprenderlo.",
    "Cuando algo no me sale bien en el estudio, busco otra forma de intentarlo.",
    "Siento que tengo el control de mi propio proceso de aprendizaje."
  ]},
  lugar: { name: "Lugar de estudio", items: [
    "Tengo un lugar fijo destinado únicamente a estudiar.",
    "Mi lugar de estudio tiene buena iluminación.",
    "Estudio en un espacio silencioso o con el ruido bajo control.",
    "Mi mesa de estudio está ordenada antes de comenzar.",
    "Tengo a mano todos los materiales que necesito antes de empezar.",
    "Estudio con el celular fuera de mi alcance o en silencio.",
    "La temperatura del lugar donde estudio es adecuada.",
    "Mi silla y mesa me permiten mantener una postura cómoda.",
    "Evito estudiar en la cama o en lugares muy relajados.",
    "Otras personas respetan mi espacio de estudio mientras trabajo."
  ]},
  fisico: { name: "Estado físico del escolar", items: [
    "Duermo al menos 7-8 horas la noche antes de estudiar o rendir un examen.",
    "Como algo ligero antes de estudiar, sin sentirme con hambre ni pesado.",
    "Hago pausas activas (levantarme, estirar) cada cierto tiempo mientras estudio.",
    "Tomo agua con regularidad durante mis sesiones de estudio.",
    "Practico alguna actividad física con regularidad durante la semana.",
    "Siento que mi nivel de energía es suficiente para sostener una sesión de estudio."
  ]},
  plan: { name: "Plan de trabajo", items: [
    "Tengo un horario semanal de estudio que sigo la mayor parte del tiempo.",
    "Distribuyo mi tiempo según la dificultad de cada materia.",
    "Empiezo a preparar los exámenes con varios días de anticipación.",
    "Divido las tareas grandes en partes más pequeñas y manejables.",
    "Reviso al final del día si cumplí con lo que había planeado.",
    "Dejo tiempo de margen para imprevistos en mi planificación.",
    "Priorizo mis tareas según su urgencia e importancia.",
    "Evito acumular varias tareas para el mismo día.",
    "Uso alguna herramienta (agenda, app, calendario) para organizar mis pendientes.",
    "Cumplo con los tiempos que me propongo para cada tarea."
  ]},
  tecnicas: { name: "Técnicas de estudio", items: [
    "Subrayo o resalto las ideas principales de un texto al estudiar.",
    "Hago resúmenes con mis propias palabras después de leer un tema.",
    "Elaboro esquemas o mapas conceptuales para organizar la información.",
    "Me hago preguntas a mí mismo para comprobar si entendí un tema.",
    "Explico en voz alta lo que estudié, como si se lo enseñara a otra persona.",
    "Repaso los temas varios días después de haberlos estudiado por primera vez.",
    "Relaciono lo que estudio con cosas que ya sé o con ejemplos de la vida real.",
    "Leo primero todo el tema completo antes de entrar en detalle.",
    "Identifico las palabras clave de cada tema que estudio."
  ]},
  examenes: { name: "Exámenes y ejercicios", items: [
    "Leo todas las preguntas de un examen antes de empezar a responder.",
    "Distribuyo el tiempo del examen según la dificultad y el puntaje de cada pregunta.",
    "Reviso mis respuestas antes de entregar el examen si tengo tiempo.",
    "Controlo los nervios lo suficiente como para pensar con claridad durante un examen.",
    "Hago ejercicios de práctica similares a los que espero encontrar en el examen."
  ]},
  trabajos: { name: "Trabajos", items: [
    "Hago un esquema o guion antes de empezar a redactar un trabajo.",
    "Busco información en más de una fuente antes de escribir un trabajo.",
    "Verifico que mis fuentes de información sean confiables.",
    "Reviso la ortografía y redacción antes de entregar un trabajo.",
    "Cito o referencio correctamente la información que no es mía.",
    "Entrego mis trabajos dentro del plazo establecido."
  ]}
};

const CHT_AREA_DEF = {
  actitud: "La predisposición, el interés y la motivación de fondo hacia el hecho de estudiar, el motor que sostiene todo lo demás.",
  lugar: "La ubicación física y las condiciones del espacio donde estudia habitualmente, y qué tanto ese entorno favorece o compite con la concentración.",
  fisico: "Las condiciones físicas personales (sueño, alimentación, energía, pausas) que determinan cuánta capacidad de concentración real tiene disponible cada día.",
  plan: "La organización y estructuración del tiempo dedicado al estudio: si el esfuerzo se distribuye con criterio o se administra sobre la marcha.",
  tecnicas: "El conocimiento y uso de métodos concretos para procesar, comprender y fijar la información a largo plazo, más allá de la simple lectura repetida.",
  examenes: "Las pautas que sigue antes y durante un examen o ejercicio evaluado: gestión del tiempo, del orden de respuesta y de los nervios.",
  trabajos: "Cómo organiza, investiga, redacta y revisa un trabajo académico de principio a fin."
};

const CHT_AREA_INTERP = {
  actitud: {
    low: `presenta una motivación de base frágil hacia el estudio: es probable que perciba estudiar como una obligación externa más que como una elección propia, que le cueste sostener el esfuerzo cuando un tema no le resulta atractivo de entrada, y que la procrastinación aparezca con frecuencia como primera respuesta ante la tarea.`,
    medium: `mantiene una motivación funcional pero inconsistente: estudia y cumple, pero sin un compromiso interno fuerte que sostenga el esfuerzo cuando las condiciones externas (ánimo, tiempo, interés en la materia) no acompañan. Es un terreno fértil para intervenir, porque la base ya existe.`,
    high: `muestra una motivación interna sólida hacia el aprendizaje: entiende el estudio como algo con sentido propio, tolera bien la frustración ante materias difíciles y mantiene el esfuerzo incluso sin supervisión externa. Esta es la base emocional sobre la que se sostienen todas las demás áreas.`
  },
  lugar: {
    low: `estudia en condiciones ambientales que compiten activamente con su concentración: sin un espacio fijo, con distracciones accesibles (el celular, el ruido, otras personas) y sin los materiales organizados antes de empezar. Gran parte del esfuerzo mental se está gastando en resistir el entorno, no en aprender.`,
    medium: `cuenta con condiciones de estudio parcialmente favorables, pero con algunos elementos (ruido, orden, iluminación o acceso al celular) que siguen restando eficiencia a sus sesiones sin que lo perciba como un problema grave.`,
    high: `ha construido un entorno de estudio que trabaja a su favor: un espacio fijo, ordenado y con las distracciones bajo control. Esto reduce el esfuerzo de autocontrol necesario para concentrarse, dejando más energía mental disponible para el contenido mismo.`
  },
  fisico: {
    low: `estudia frecuentemente con el cuerpo en desventaja: sueño insuficiente, sin pausas activas ni hidratación regular. Esto no es un tema menor. La privación de sueño y la fatiga física reducen directamente la capacidad de memoria y concentración, independientemente de qué tan buenas sean las técnicas de estudio que use.`,
    medium: `mantiene un cuidado físico irregular alrededor del estudio: hay hábitos saludables presentes, pero no lo suficientemente constantes como para sostener el rendimiento en épocas de mayor exigencia (exámenes, entregas).`,
    high: `sostiene hábitos físicos que respaldan directamente su rendimiento académico: duerme lo necesario, se hidrata, hace pausas y mantiene actividad física. Esto le da una base de energía y claridad mental de la que muchos estudiantes carecen sin saberlo.`
  },
  plan: {
    low: `estudia principalmente de forma reactiva, sin una planificación que anticipe la carga de trabajo: las tareas se acumulan, los exámenes se preparan a último momento y no existe un sistema claro para priorizar qué atender primero. Esto genera una sensación de estar siempre "corriendo detrás" del tiempo.`,
    medium: `tiene nociones de planificación (una agenda, algunos horarios), pero no las sostiene con la disciplina suficiente como para que se vuelvan un sistema confiable. Funciona mejor en semanas tranquilas que en semanas de alta exigencia.`,
    high: `organiza su tiempo de estudio con anticipación real: distribuye la carga según dificultad, prioriza con criterio y llega a los exámenes sin depender de una maratón de último momento. Esta es, junto con las técnicas de estudio, una de las áreas de mayor impacto directo sobre el rendimiento.`
  },
  tecnicas: {
    low: `estudia mayormente por repetición pasiva (releer, repetir en voz baja) sin usar métodos que fuercen la comprensión activa del contenido. Esto explica por qué, incluso invirtiendo tiempo, la información no siempre se fija a largo plazo: el problema no es cuánto estudia, sino cómo.`,
    medium: `conoce y aplica algunas técnicas de estudio activo (resúmenes, esquemas), pero de forma poco sistemática. Las usa cuando se acuerda o cuando el tema lo exige, no como parte de un método fijo.`,
    high: `aplica de forma consistente técnicas de estudio activo que fuerzan la comprensión real del contenido (resúmenes propios, autopreguntas, explicación en voz alta, repaso espaciado). Esto es lo que distingue a un estudiante eficiente de uno que simplemente invierte muchas horas.`
  },
  examenes: {
    low: `llega al momento del examen sin una estrategia clara de gestión del tiempo ni del orden de respuesta, lo que puede llevarle a quedarse sin tiempo en preguntas que sí sabía responder, o a bloquearse frente a los nervios sin un plan para recuperar claridad.`,
    medium: `tiene algunas pautas básicas para rendir exámenes, pero le falta convertirlas en un procedimiento fijo que aplique siempre, independientemente del nivel de nervios o de la dificultad percibida de la prueba.`,
    high: `aborda los exámenes con una estrategia clara: lee todo antes de responder, administra el tiempo con criterio y mantiene el control emocional necesario para pensar con claridad bajo presión.`
  },
  trabajos: {
    low: `enfrenta los trabajos académicos sin una estructura previa. Empieza a escribir sin esquema, usa pocas fuentes y revisa poco o nada antes de entregar. Esto se traduce en trabajos que reflejan menos de lo que realmente sabe sobre el tema.`,
    medium: `sigue algunos pasos ordenados al hacer un trabajo, pero de forma incompleta (por ejemplo, investiga bien pero revisa poco, o al revés), dejando puntos débiles evitables en el resultado final.`,
    high: `sigue un proceso completo y ordenado para sus trabajos académicos: planifica, investiga de varias fuentes, y revisa antes de entregar. Esto se traduce en trabajos más sólidos y mejor sustentados.`
  }
};

const CHT_REC_LIBRARY = {
  actitud: {
    low: [
      "Fijar una meta <b>SMART</b> concreta para la semana (específica, medible, alcanzable, relevante, con plazo) en lugar de una intención vaga como \"estudiar más\".",
      "Aplicar la técnica de <b>los primeros 5 minutos</b>: comprometerse solo a empezar una sesión, no a terminarla, ya que el arranque suele ser la mayor barrera psicológica.",
      "Llevar un registro visual del progreso (un checklist o un calendario marcado con una X cada día cumplido) para reforzar la motivación con evidencia concreta.",
      "Identificar por escrito el \"para qué\" personal detrás de cada materia, más allá de la nota, lo cual conecta el esfuerzo con un sentido propio y sostenible.",
      "Reducir la meta inicial a algo casi ridículamente pequeño (\"solo leer una página\") para vencer la resistencia a empezar, ya que casi siempre se sigue una vez iniciado.",
      "Buscar un compañero de estudio o grupo de apoyo que genere compromiso externo mientras se consolida la motivación interna."
    ],
    medium: [
      "Revisar semanalmente las metas de estudio y ajustarlas según lo que realmente se cumplió, no según lo que se planeó.",
      "Practicar la técnica <b>Pomodoro</b> (25 min de estudio + 5 de descanso) para sostener la concentración sin agotarse ni depender solo de la fuerza de voluntad.",
      "Cerrar cada sesión reconociendo un logro concreto, por pequeño que sea, antes de pasar a otra cosa.",
      "Alternar materias que gustan más con las que cuestan más, para no acumular toda la resistencia en un solo bloque del día.",
      "Visualizar brevemente, antes de empezar, cómo se sentirá al terminar la tarea: anticipar el alivio ayuda a sostener el esfuerzo inicial."
    ],
    high: [
      "Explicar temas a compañeros o familiares como forma de consolidar y profundizar el propio aprendizaje (efecto protégé).",
      "Diseñar retos personales de aprendizaje que vayan un paso más allá del programa curricular, para mantener el interés activo.",
      "Llevar un diario breve de aprendizaje, anotando qué se entendió mejor y qué costó más, lo cual construye autoconocimiento como estudiante.",
      "Ofrecerse como tutor o apoyo de compañeros con más dificultad: enseñar es una de las formas más efectivas de aprender."
    ]
  },
  lugar: {
    low: [
      "Designar un único rincón fijo exclusivamente para estudiar, aunque sea pequeño, ya que el cerebro asocia el lugar con la actividad que ahí se realiza.",
      "Aplicar la regla de las <b>3 D</b>: Despejar el espacio, Delimitarlo físicamente y Dedicarlo solo al estudio, nunca a otra actividad.",
      "Guardar el celular en otra habitación o activarlo en modo avión durante las sesiones de estudio, ya que la sola presencia visible ya reduce la concentración.",
      "Priorizar luz natural o una lámpara de luz blanca/fría, evitando luz cálida o tenue que induce somnolencia.",
      "Preparar todos los materiales necesarios antes de sentarse a estudiar, para no interrumpir la concentración a mitad de sesión buscando algo.",
      "Negociar con quienes conviven en casa un horario de silencio o de \"no interrumpir\" durante los bloques de estudio."
    ],
    medium: [
      "Incorporar elementos que reduzcan el ruido ambiental (auriculares con cancelación de ruido, ruido blanco o música instrumental sin letra).",
      "Revisar la ergonomía de la silla y la altura de la mesa para sostener sesiones largas sin molestias físicas que distraigan.",
      "Ordenar el espacio de estudio al finalizar cada sesión, para empezar la siguiente sin fricción visual.",
      "Ajustar la temperatura del ambiente: un espacio demasiado cálido favorece la somnolencia, uno muy frío distrae por incomodidad."
    ],
    high: [
      "Rotar ocasionalmente el entorno de estudio para materias de memorización, ya que variar el contexto físico refuerza el recuerdo (efecto de codificación variable).",
      "Mantener el espacio de estudio como un ritual: entrar ahí debe funcionar como una señal automática para el cerebro de que toca concentrarse.",
      "Experimentar con pequeñas variables (tipo de música, temperatura, hora del día) para afinar aún más el rendimiento en ese espacio ya consolidado."
    ]
  },
  fisico: {
    low: [
      "Fijar una hora de sueño constante los días previos a exámenes, priorizando 7-8 horas, ya que el sueño consolida directamente la memoria de lo estudiado.",
      "Incorporar pausas activas cada 25-45 minutos: levantarse, estirar o caminar brevemente para reactivar la circulación y la atención.",
      "Mantener una botella de agua visible durante el estudio y tomar agua con regularidad, ya que la deshidratación leve ya afecta la concentración de forma medible.",
      "Evitar sentarse a estudiar inmediatamente después de comidas muy pesadas, que generan somnolencia por digestión.",
      "Reducir el consumo de cafeína o bebidas energéticas en las horas previas a dormir, para no comprometer la calidad del sueño reparador.",
      "Priorizar dormir bien la noche anterior a un examen por encima de una hora extra de repaso, ya que el descanso influye más en el rendimiento que el repaso de último momento."
    ],
    medium: [
      "Incorporar una caminata corta o estiramientos entre sesiones largas de estudio para renovar la energía mental.",
      "Cuidar la alimentación en época de exámenes, priorizando comidas ligeras y de liberación energética sostenida (frutas, frutos secos, cereales integrales).",
      "Establecer una rutina de \"desconexión\" 30 minutos antes de dormir (sin pantallas) para mejorar la calidad del sueño."
    ],
    high: [
      "Mantener una rutina de ejercicio físico regular como estrategia activa de manejo del estrés académico, no solo como hábito de salud general.",
      "Incorporar técnicas breves de respiración o mindfulness antes de sesiones de alta exigencia (exámenes, entregas importantes).",
      "Monitorear cómo distintos horarios del día afectan su energía y concentración, y reservar los bloques de mejor rendimiento para lo más exigente."
    ]
  },
  plan: {
    low: [
      "Elaborar un horario semanal simple, bloqueando franjas fijas de estudio por materia, ya que visualizar el tiempo disponible ayuda a usarlo con más criterio.",
      "Aplicar la <b>Matriz de Eisenhower</b> (urgente/importante) para decidir qué tarea atender primero cuando hay varias pendientes a la vez.",
      "Dividir tareas grandes en subtareas de máximo 30-45 minutos cada una, para que ninguna se sienta abrumadora antes de empezar.",
      "Usar un planificador físico o una app de tareas y revisarlo cada mañana antes de empezar el día.",
      "Empezar a preparar cada examen con al menos una semana de anticipación, aunque sea con sesiones cortas, en vez de concentrarlo todo la noche anterior.",
      "Anotar de inmediato cualquier tarea o fecha de entrega apenas se conozca, en vez de confiar en la memoria."
    ],
    medium: [
      "Incorporar la técnica de <b>bloques de tiempo</b> (time blocking): asignar un horario específico a cada tarea, no solo una lista sin horario asociado.",
      "Dejar un margen de aproximadamente 20% del tiempo planificado libre, para absorber imprevistos sin descuadrar todo el plan.",
      "Revisar cada domingo la semana siguiente completa, anticipando los días de mayor carga académica."
    ],
    high: [
      "Aplicar una revisión semanal de productividad al estilo <b>GTD (Getting Things Done)</b>: qué funcionó, qué ajustar para la semana siguiente.",
      "Anticipar la planificación de exámenes con 2-3 semanas de margen, distribuyendo el repaso mediante repetición espaciada en vez de concentrarlo al final.",
      "Enseñar el propio sistema de organización a un compañero con dificultades de planificación, lo cual consolida el hábito y ayuda a otros."
    ]
  },
  tecnicas: {
    low: [
      "Aprender y aplicar el método de <b>subrayado + resumen</b> como primer paso técnico antes de avanzar a métodos más complejos.",
      "Iniciar con el método <b>SQ3R</b> (Explorar, Preguntar, Leer, Recitar, Repasar) para textos largos o densos.",
      "Practicar la elaboración de esquemas simples inmediatamente después de cada lectura, mientras el contenido está fresco en la memoria.",
      "Usar tarjetas de repaso (<b>flashcards</b>) para datos, fechas o conceptos que requieren memorización directa.",
      "Reemplazar la relectura pasiva por la autoevaluación: cerrar el libro y tratar de recordar lo leído antes de volver a revisarlo.",
      "Elegir un único tema de prueba esta semana para aplicar una técnica nueva, en vez de intentar cambiar todo el método de golpe."
    ],
    medium: [
      "Incorporar la <b>Técnica Feynman</b>: explicar el tema con palabras simples, como si se lo enseñara a alguien que no sabe nada del tema: donde titubea, ahí está el vacío que falta reforzar.",
      "Aplicar <b>repaso espaciado</b> (spaced repetition) en vez de repasar todo de una sola vez la noche anterior al examen.",
      "Usar mapas mentales para temas con muchas relaciones entre conceptos, y esquemas lineales para procesos secuenciales.",
      "Combinar lectura con toma de notas activa (método Cornell: notas, señales y resumen en la misma hoja) en vez de solo transcribir."
    ],
    high: [
      "Practicar <b>active recall</b>: cerrar el material y tratar de reconstruirlo de memoria antes de volver a revisarlo, lo cual es más efectivo que releer.",
      "Combinar deliberadamente varias técnicas según el tipo de contenido: mapas para relaciones conceptuales, flashcards para datos puntuales, resúmenes para textos narrativos o argumentativos.",
      "Enseñar sus propias técnicas de estudio a compañeros: verbalizar el método propio suele revelar dónde se puede afinar aún más."
    ]
  },
  examenes: {
    low: [
      "Leer el examen completo antes de responder cualquier pregunta, para dimensionar el esfuerzo total y evitar sorpresas de último momento.",
      "Practicar con exámenes o ejercicios de años anteriores como simulacro real de la prueba, en condiciones similares a las del día real.",
      "Aplicar una regla simple de tiempo: dividir el tiempo total disponible entre el número de preguntas antes de empezar a responder.",
      "Practicar una respiración lenta de 4 segundos inhalando y 6 exhalando durante 1 minuto antes de comenzar, para reducir la activación nerviosa inicial."
    ],
    medium: [
      "Priorizar primero las preguntas que se dominan con seguridad, dejando las más difíciles para el final del tiempo disponible.",
      "Practicar una respiración breve y consciente si aparecen nervios durante el examen, para recuperar claridad mental sin perder tiempo valioso.",
      "Reservar los últimos minutos del examen exclusivamente para revisar respuestas, no para seguir avanzando contenido nuevo."
    ],
    high: [
      "Simular condiciones reales de examen durante la preparación: tiempo cronometrado, sin distracciones, en un espacio similar al real.",
      "Analizar los errores de exámenes anteriores para identificar patrones de fallo recurrentes y corregirlos de raíz, no solo memorizar la respuesta correcta puntual.",
      "Desarrollar un protocolo personal de pre-examen (rutina fija de la noche y la mañana anterior) que reduzca la variabilidad emocional del día."
    ]
  },
  trabajos: {
    low: [
      "Elaborar siempre un esquema o guion antes de empezar a redactar cualquier trabajo, ya que ordena las ideas antes de escribir y ahorra tiempo de reescritura.",
      "Consultar al menos dos o tres fuentes distintas antes de escribir, en vez de basarse en una sola fuente o en la primera que aparece.",
      "Dejar al menos un día entre terminar de escribir y hacer la revisión final, para detectar errores con mirada fresca.",
      "Dividir el trabajo en fases con fecha propia (investigación, redacción, revisión) en vez de tratarlo como una sola tarea gigante.",
      "Guardar copias de respaldo del trabajo en progreso, para evitar el estrés añadido de perder avances por un fallo técnico."
    ],
    medium: [
      "Aprender un formato de citación estándar (por ejemplo, APA) y aplicarlo de forma consistente en todos los trabajos, no solo cuando se recuerda.",
      "Pedir a otra persona que revise el trabajo antes de entregarlo: un segundo par de ojos detecta lo que el autor ya no ve.",
      "Verificar la confiabilidad de cada fuente utilizada (autor, fecha, origen) antes de incorporarla al trabajo."
    ],
    high: [
      "Desarrollar un banco personal de fuentes confiables por materia, reutilizable en futuros trabajos.",
      "Aplicar una revisión en capas antes de entregar: primero contenido y argumento, luego estructura, y por último ortografía y formato.",
      "Pedir retroalimentación específica sobre el argumento central del trabajo, no solo sobre redacción, para seguir elevando el nivel de análisis."
    ]
  }
};
function scoreChaTable(key){
  const scores = {};
  for(const letter in key){ scores[letter] = key[letter].filter(n => cha_responses[n] === 'si').length; }
  return scores;
}

function computeChaside(){
  const interesesScores = scoreChaTable(CHA_KEY_INTERESES);
  const aptitudesScores = scoreChaTable(CHA_KEY_APTITUDES);
  const rows = [];
  for(const letter in CHA_AREA_INFO){
    rows.push({ letter, interes: interesesScores[letter]||0, aptitud: aptitudesScores[letter]||0, total: (interesesScores[letter]||0)+(aptitudesScores[letter]||0) });
  }
  return rows.sort((a,b)=>b.total-a.total);
}

function af5ItemValue(n){
  const raw = af5_responses[n] !== undefined ? af5_responses[n] : 50;
  return AF5_REVERSED_ITEMS.includes(n) ? (100-raw) : raw;
}

function af5PdToCentil(bracket, sexo, dimIndex, pd){
  const rows = AF5_NORM_TABLES[bracket] && AF5_NORM_TABLES[bracket][sexo];
  if(!rows) return null;
  const points = rows.filter(row => row[dimIndex] !== null).map(row => ({ pct: row[0], min: row[dimIndex][0], max: row[dimIndex][1] })).sort((a,b)=>a.pct-b.pct);
  if(points.length === 0) return null;
  for(const p of points){ if(pd >= p.min && pd <= p.max) return p.pct; }
  if(pd < points[0].min) return points[0].pct;
  if(pd > points[points.length-1].max) return points[points.length-1].pct;
  for(let i=0;i<points.length-1;i++){
    const a=points[i], b=points[i+1];
    if(pd > a.max && pd < b.min){
      const aMid=(a.min+a.max)/2, bMid=(b.min+b.max)/2;
      if(bMid===aMid) return a.pct;
      return Math.round(a.pct + ((pd-aMid)/(bMid-aMid))*(b.pct-a.pct));
    }
  }
  return null;
}

function computeAF5(bracket, sexo){
  const result = {};
  for(const key in AF5_DIMENSIONS){
    const dim = AF5_DIMENSIONS[key];
    let pdRaw;
    if(dim.collectiveReversal){
      const rawSum = dim.items.reduce((s,n)=> s + (af5_responses[n]!==undefined?af5_responses[n]:50), 0);
      pdRaw = 600 - rawSum;
    } else {
      pdRaw = dim.items.reduce((s,n)=> s + af5ItemValue(n), 0);
    }
    const pd = Math.round((pdRaw/60)*100)/100;
    const centil = af5PdToCentil(bracket, sexo, AF5_DIM_INDEX[key], pd);
    result[key] = { key, name: dim.name, pd, centil };
  }
  return result;
}

function af5Band(centil){ if(centil===null) return 'medium'; if(centil>=75) return 'high'; if(centil<=25) return 'low'; return 'medium'; }

function chtBand(pct){ if(pct>=70) return 'high'; if(pct<40) return 'low'; return 'medium'; }

function computeCHTE(){
  const result = {};
  let counter = 0;
  Object.entries(CHT_AREAS).forEach(([key, area])=>{
    let si = 0;
    area.items.forEach(()=>{ counter++; if(cht_responses[counter]==='si') si++; });
    const pct = Math.round((si/area.items.length)*100);
    result[key] = { key, name: area.name, si, total: area.items.length, pct, band: chtBand(pct) };
  });
  return result;
}

// ===================== GRÁFICOS PROFESIONALES (SVG, sin librerías externas) =====================

function buildBarChartSVG(items, opts){
  // items: [{label, value, band}], value en escala 0-100
  const width = 640, rowH = 34, padTop = 10, padBottom = 30, padLeft = 190, padRight = 50;
  const height = padTop + padBottom + items.length * rowH;
  const chartW = width - padLeft - padRight;
  const colorFor = (band) => band === 'high' ? '#5f7a3f' : (band === 'low' ? '#a15353' : '#8A6A28');

  let bars = '';
  items.forEach((item, i) => {
    const y = padTop + i * rowH;
    const barW = Math.max(2, (item.value / 100) * chartW);
    const color = item.band ? colorFor(item.band) : '#8A6A28';
    bars += `
      <text x="${padLeft - 12}" y="${y + rowH/2 + 4}" text-anchor="end" font-family="Bodoni Moda, serif" font-size="11" fill="#3a3934">${item.label}</text>
      <rect x="${padLeft}" y="${y + 7}" width="${chartW}" height="${rowH - 14}" fill="#F3EFE2"/>
      <rect x="${padLeft}" y="${y + 7}" width="${barW}" height="${rowH - 14}" fill="${color}"/>
      <text x="${padLeft + barW + 8}" y="${y + rowH/2 + 4}" font-family="Bodoni Moda, serif" font-size="11" fill="#3a3934">${item.valueLabel || item.value}</text>
    `;
  });

  // Líneas guía verticales cada 25%
  let gridlines = '';
  [0,25,50,75,100].forEach(pct=>{
    const x = padLeft + (pct/100)*chartW;
    gridlines += `<line x1="${x}" y1="${padTop}" x2="${x}" y2="${height-padBottom+4}" stroke="#E4DECC" stroke-width="1"/>
      <text x="${x}" y="${height-padBottom+18}" text-anchor="middle" font-family="Bodoni Moda, serif" font-size="9" fill="#8A6A28">${pct}${opts && opts.suffix ? opts.suffix : ''}</text>`;
  });

  return `<svg viewBox="0 0 ${width} ${height}" style="width:100%;height:auto;font-family:'Bodoni Moda',serif;">${gridlines}${bars}</svg>`;
}

function buildRadarChartSVG(dimensions){
  // dimensions: [{name, value (0-100), band}], pensado para 5 ejes (AF5)
  const size = 420, cx = size/2, cy = size/2 - 10, R = 130;
  const n = dimensions.length;
  const angleFor = (i) => (Math.PI * 2 / n) * i - Math.PI/2;

  // Anillos de fondo (25/50/75/100%)
  let rings = '';
  [0.25,0.5,0.75,1].forEach(frac=>{
    const pts = dimensions.map((_,i)=>{
      const a = angleFor(i);
      const r = R*frac;
      return `${cx + r*Math.cos(a)},${cy + r*Math.sin(a)}`;
    }).join(' ');
    rings += `<polygon points="${pts}" fill="none" stroke="#E4DECC" stroke-width="1"/>`;
  });

  // Ejes y etiquetas
  let axes = '';
  dimensions.forEach((d,i)=>{
    const a = angleFor(i);
    const x2 = cx + R*Math.cos(a), y2 = cy + R*Math.sin(a);
    const lx = cx + (R+38)*Math.cos(a), ly = cy + (R+38)*Math.sin(a);
    axes += `<line x1="${cx}" y1="${cy}" x2="${x2}" y2="${y2}" stroke="#E4DECC" stroke-width="1"/>
      <text x="${lx}" y="${ly}" text-anchor="middle" font-family="Bodoni Moda, serif" font-size="10.5" fill="#3a3934" font-weight="600">${d.name}</text>
      <text x="${lx}" y="${ly+13}" text-anchor="middle" font-family="Bodoni Moda, serif" font-size="9" fill="#8A6A28">${d.value ?? '—'}</text>`;
  });

  // Polígono de datos
  const dataPts = dimensions.map((d,i)=>{
    const a = angleFor(i);
    const r = R * Math.max(0,Math.min(100,d.value ?? 0))/100;
    return `${cx + r*Math.cos(a)},${cy + r*Math.sin(a)}`;
  }).join(' ');

  return `<svg viewBox="0 0 ${size} ${size-10}" style="width:100%;max-width:420px;height:auto;margin:0 auto;display:block;">
    ${rings}${axes}
    <polygon points="${dataPts}" fill="rgba(201,162,75,0.28)" stroke="#8A6A28" stroke-width="2"/>
    ${dimensions.map((d,i)=>{
      const a = angleFor(i); const r = R * Math.max(0,Math.min(100,d.value ?? 0))/100;
      return `<circle cx="${cx + r*Math.cos(a)}" cy="${cy + r*Math.sin(a)}" r="4" fill="#8A6A28"/>`;
    }).join('')}
  </svg>`;
}

const BAND_LABEL = { high:'Alto', medium:'Medio', low:'Bajo' };
function PLAN_LABEL_ES(plan){
  return { basico:'Básico', completo:'Completo', premium:'Premium' }[plan] || plan || '—';
}
function planIncluyeAF5(plan){ return plan === 'completo' || plan === 'premium'; }
function planIncluyeAPTA(plan){ return plan === 'premium'; }
function planIncluyeAPTB(plan){ return plan === 'premium'; }

/* ================== APT-B: datos y claves (solo admin) ==================
   APT-B (Ortografía, Lenguaje, Relaciones Espaciales, Velocidad y Precisión)
   es el reemplazo ORIGINAL y de propiedad AURZANE del antiguo módulo DAT
   Forma T, reproducir los ítems y la clave de corrección reales de un test
   comercial de terceros en la plataforma planteaba un problema de derechos
   de autor y de seguridad del instrumento, así que este módulo se reconstruyó
   por completo con ítems, figuras y clave propios (ver [[aurzane-ovp-platform]]). */

const APTB_O_KEY = ["I", "I", "C", "C", "C", "C", "I", "C", "C", "C", "C", "C", "I", "I", "I", "C", "I", "I", "I", "C", "C", "I", "C", "I", "I", "I", "I", "I", "C", "C", "C", "I", "I", "I", "C", "C", "I", "C", "C", "C", "I", "C", "C", "I", "I", "C", "I", "I", "C", "I", "C", "C", "I", "C", "I", "I", "C", "C", "I", "C", "C", "C", "C", "C", "I", "I", "C", "C", "I", "I", "I", "I", "C", "I", "I", "C", "I", "I", "C", "I", "I", "C", "I", "I", "I", "I", "I", "C", "C", "I", "C", "C", "C", "C", "C", "I", "I", "C", "C", "I"];
const APTB_L_KEY = ["A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "B", "B", "B", "B", "B", "B", "B", "B", "B", "B", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "D", "D", "D", "D", "D", "D", "D", "D", "D", "D", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E"];
const APTB_RE_KEY = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D"];
const APTB_VP1_KEY = ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E"];
const APTB_VP2_KEY = ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E", "A", "B", "C", "D", "E"];

// Función genérica de corrección por adivinación, compartida por APT-A y
// APT-B: S = aciertos − errores/(n_opciones−1) (fórmula estándar para ítems
// de opción múltiple con posibilidad real de acertar al azar).
function scoreSubtestGenerico(key, respArr, clave, nItems, nOpciones){
  let aciertos = 0, errores = 0;
  for(let i=0;i<nItems;i++){
    if(respArr[i]!==null){
      if(respArr[i]===clave[i]) aciertos++; else errores++;
    }
  }
  const corregido = Math.max(0, aciertos - errores/(nOpciones-1));
  const pct = Math.round((corregido/nItems)*100);
  return { key, aciertos, errores, corregido: Math.round(corregido*10)/10, pct };
}

function computeAPTB(aptbRows){
  const resp = {
    O:  new Array(100).fill(null),
    L:  new Array(50).fill(null),
    RE: new Array(60).fill(null),
    VP1: new Array(100).fill(null),
    VP2: new Array(100).fill(null),
  };
  (aptbRows||[]).forEach(r=>{
    const n = r.item_num - 1;
    if(resp[r.subtest] && n>=0 && n<resp[r.subtest].length) resp[r.subtest][n] = r.valor;
  });

  const O  = scoreSubtestGenerico('O',  resp.O,  APTB_O_KEY,  100, 2);
  const L  = scoreSubtestGenerico('L',  resp.L,  APTB_L_KEY,  50,  5);
  const RE = scoreSubtestGenerico('RE', resp.RE, APTB_RE_KEY, 60,  4);
  const vp1 = scoreSubtestGenerico('VP1', resp.VP1, APTB_VP1_KEY, 100, 5);
  const vp2 = scoreSubtestGenerico('VP2', resp.VP2, APTB_VP2_KEY, 100, 5);
  const vpAciertos = vp1.aciertos + vp2.aciertos, vpErrores = vp1.errores + vp2.errores;
  const vpCorregido = Math.round((vp1.corregido + vp2.corregido)*10)/10;
  const VP = { key:'VP', aciertos: vpAciertos, errores: vpErrores, corregido: vpCorregido, pct: Math.round((vpCorregido/200)*100) };

  const respondidos = resp.O.filter(x=>x!==null).length + resp.L.filter(x=>x!==null).length
    + resp.RE.filter(x=>x!==null).length + resp.VP1.filter(x=>x!==null).length + resp.VP2.filter(x=>x!==null).length;

  return {
    O:  { ...O,  name: "Ortografía" },
    L:  { ...L,  name: "Lenguaje" },
    RE: { ...RE, name: "Relaciones Espaciales" },
    VP: { ...VP, name: "Velocidad y Precisión" },
    respondidos, totalItems: 100+50+60+200
  };
}

/* ================== APT-A: batería de aptitudes propia (solo admin) ==================
   Instrumento ORIGINAL de AURZANE (Razonamiento Verbal, Numérico, Abstracto y
   Comprensión Mecánica, 40 ítems cada uno). No es una digitalización de
   ningún test comercial de terceros: ítems, figuras y clave de corrección
   son de autoría y propiedad de AURZANE.

   Tanto APT-A como APT-B son instrumentos propios todavía sin muestra
   normativa de tipificación, así que NO reportan percentiles poblacionales
   (eso exigiría un estudio con una muestra de referencia que estos
   instrumentos aún no tienen, inventar esa cifra sería fabricar un dato).
   En su lugar se usa una escala interpretativa propia de tres bandas
   (Bajo/Medio/Alto) sobre el puntaje corregido por adivinación, con el mismo
   criterio ya usado en el Cuestionario AURZANE de Hábitos de Estudio (CHTE)
   para instrumentos propios sin baremos externos. */

const APT_V_KEY  = ["B", "E", "A", "B", "A", "D", "D", "E", "E", "E", "C", "B", "B", "D", "E", "D", "A", "B", "D", "A", "E", "D", "C", "D", "B", "C", "C", "C", "C", "B", "E", "A", "C", "C", "E", "A", "A", "D", "B", "A"];
const APT_N_KEY  = ["E", "D", "A", "E", "B", "B", "E", "A", "A", "E", "D", "C", "D", "C", "D", "A", "B", "C", "C", "C", "B", "B", "C", "A", "E", "A", "D", "D", "A", "B", "A", "D", "E", "E", "B", "D", "E", "C", "C", "B"];
const APT_AB_KEY = ["C", "E", "D", "C", "A", "E", "D", "B", "B", "C", "D", "E", "D", "B", "B", "C", "C", "A", "B", "D", "A", "A", "E", "C", "A", "A", "D", "E", "B", "D", "A", "E", "B", "A", "C", "E", "D", "C", "B", "E"];
const APT_ME_KEY = ["B", "A", "C", "A", "C", "B", "B", "C", "B", "B", "B", "B", "A", "A", "B", "C", "C", "A", "B", "A", "C", "A", "C", "B", "A", "A", "B", "C", "A", "C", "C", "C", "C", "A", "B", "A", "A", "C", "B", "A"];

function computeAPTA(aptRows){
  const resp = { V: new Array(40).fill(null), N: new Array(40).fill(null), AB: new Array(40).fill(null), ME: new Array(40).fill(null) };
  (aptRows||[]).forEach(r=>{
    const n = r.item_num - 1;
    if(resp[r.subtest] && n>=0 && n<40) resp[r.subtest][n] = r.valor;
  });

  const V  = scoreSubtestGenerico('V',  resp.V,  APT_V_KEY,  40, 5);
  const N  = scoreSubtestGenerico('N',  resp.N,  APT_N_KEY,  40, 5);
  const AB = scoreSubtestGenerico('AB', resp.AB, APT_AB_KEY, 40, 5);
  const ME = scoreSubtestGenerico('ME', resp.ME, APT_ME_KEY, 40, 3);

  const respondidos = resp.V.filter(x=>x!==null).length + resp.N.filter(x=>x!==null).length
    + resp.AB.filter(x=>x!==null).length + resp.ME.filter(x=>x!==null).length;

  return {
    V:  { ...V,  name: "Razonamiento Verbal" },
    N:  { ...N,  name: "Razonamiento Numérico" },
    AB: { ...AB, name: "Razonamiento Abstracto" },
    ME: { ...ME, name: "Comprensión Mecánica" },
    respondidos, totalItems: 160
  };
}

function aptBand(pct){ if(pct===null||pct===undefined) return 'medium'; if(pct>=70) return 'high'; if(pct<40) return 'low'; return 'medium'; }

/* ================== Holland / RIASEC: instrumento propio (solo admin) ==================
   Cuestionario original de AURZANE inspirado en la teoría pública RIASEC de
   John Holland (6 tipos). El mapeo ítem→dimensión (clave de corrección) vive
   únicamente aquí, del lado del informe. No viaja al archivo cliente
   holland-cliente.html. Es una medida ipsativa (compara la fuerza relativa
   de los 6 tipos dentro de la misma persona), por lo que, igual que
   APT-A/APT-B/CHTE, no reporta percentiles poblacionales, sino un puntaje
   0-10 por dimensión y un "código Holland" con los 3 tipos más marcados. */

const HOLLAND_KEY = ["A","E","E","S","S","A","C","S","S","E","C","I","E","C","I","A","E","S","R","S","I","R","A","A","I","C","C","R","E","I","A","E","R","R","A","R","R","R","S","I","E","S","C","R","C","S","I","C","A","A","R","I","E","I","E","A","C","I","C","S"];

const HOLLAND_INFO = {
  R: {
    name: "Realista",
    desc: "Disfruta de actividades concretas, manuales y físicas, se siente cómodo trabajando con herramientas, máquinas o al aire libre, y prefiere resultados tangibles antes que tareas puramente abstractas.",
    fieldsNote: "suele encajar bien en entornos técnicos, de producción, construcción o trabajo de campo, donde el saber-hacer práctico tiene un peso central."
  },
  I: {
    name: "Investigador",
    desc: "Le atrae observar, analizar y comprender el porqué de las cosas, disfruta resolver problemas mediante el razonamiento y la evidencia antes que por ensayo intuitivo.",
    fieldsNote: "suele encajar bien en entornos de investigación, análisis de datos, ciencia o tecnología, donde formular y comprobar hipótesis es parte central del trabajo."
  },
  A: {
    name: "Artístico",
    desc: "Busca espacios para expresarse de forma original y poco estructurada, valora la creatividad, la estética y la posibilidad de trabajar sin reglas fijas.",
    fieldsNote: "suele encajar bien en entornos creativos o expresivos, donde la originalidad y la sensibilidad estética se valoran más que seguir un procedimiento único."
  },
  S: {
    name: "Social",
    desc: "Encuentra satisfacción en ayudar, enseñar o acompañar a otras personas, disfruta el contacto humano y las tareas orientadas al bienestar o el desarrollo de los demás.",
    fieldsNote: "suele encajar bien en entornos de enseñanza, cuidado, acompañamiento o trabajo comunitario, donde el vínculo con otras personas es el centro de la actividad."
  },
  E: {
    name: "Emprendedor",
    desc: "Le atrae liderar, persuadir y asumir riesgos calculados para alcanzar metas ambiciosas, se siente cómodo tomando decisiones y motivando a otros hacia un objetivo.",
    fieldsNote: "suele encajar bien en entornos de liderazgo, negociación, ventas o gestión de proyectos, donde influir en decisiones y coordinar personas es parte central del rol."
  },
  C: {
    name: "Convencional",
    desc: "Prefiere el orden, la precisión y las reglas claras, se siente cómodo con tareas sistemáticas, datos y procedimientos bien definidos, y valora la exactitud sobre la improvisación.",
    fieldsNote: "suele encajar bien en entornos administrativos, contables o de gestión de información, donde la organización y el cumplimiento riguroso de procesos son clave."
  }
};

function hollandBand(score){ if(score>=7) return 'high'; if(score<=3) return 'low'; return 'medium'; }

function computeHolland(hollandRows){
  const resp = {};
  (hollandRows||[]).forEach(r=>{ resp[r.item_num] = r.valor; });
  const counts = { R:0, I:0, A:0, S:0, E:0, C:0 };
  HOLLAND_KEY.forEach((dim, idx)=>{
    if(resp[idx+1] === 'Si') counts[dim]++;
  });
  const rows = ["R","I","A","S","E","C"].map(d => ({ key: d, name: HOLLAND_INFO[d].name, score: counts[d], pct: Math.round(counts[d]/10*100) }));
  rows.sort((a,b)=>b.score-a.score);
  const codigo = rows.slice(0,3).map(r=>r.key).join('');
  const respondidos = Object.keys(resp).length;
  return { rows, codigo, respondidos, totalItems: 60 };
}

function escapeHtml(value){
  return String(value ?? '').replace(/[&<>'"]/g, ch => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[ch]));
}

function safeText(value, fallback='—'){
  const v = String(value ?? '').trim();
  return escapeHtml(v || fallback);
}

function generateReportFromData(cliente, membrete){
  const chaRanked = computeChaside();
  const chaGap1 = chaRanked[0].total - chaRanked[1].total;

  const sexo = cliente.sexo || '';
  const grupo = cliente.grupo_normativo || 'adulto';
  const incluyeAF5 = planIncluyeAF5(cliente.plan);
  const af5Dims = incluyeAF5 ? computeAF5(grupo, sexo) : null;
  const af5Sorted = af5Dims ? Object.values(af5Dims).sort((a,b)=>(b.centil??0)-(a.centil??0)) : null;
  const af5Banded = af5Sorted ? af5Sorted.map(d=>({...d, band: af5Band(d.centil)})) : null;

  const hollandResult = computeHolland(holland_rows);
  const hollandBanded = hollandResult.rows.map(d=>({...d, band: hollandBand(d.score)}));

  const chtAreas = computeCHTE();
  const chtSorted = Object.values(chtAreas).sort((a,b)=>b.pct-a.pct);
  const chtBajas = chtSorted.filter(d=>d.band==='low');
  const chtAltas = chtSorted.filter(d=>d.band==='high');

  const incluyeAPTB = planIncluyeAPTB(cliente.plan);
  const aptBResult = incluyeAPTB ? computeAPTB(apt_b_rows) : null;
  const aptBSorted = aptBResult ? [aptBResult.O, aptBResult.L, aptBResult.RE, aptBResult.VP].sort((a,b)=>b.pct-a.pct) : null;
  const aptBBanded = aptBSorted ? aptBSorted.map(d=>({...d, band: aptBand(d.pct)})) : null;
  const aptBBajas = aptBBanded ? aptBBanded.filter(d=>d.band==='low') : [];
  const aptBAltas = aptBBanded ? aptBBanded.filter(d=>d.band==='high') : [];

  const incluyeAPTA = planIncluyeAPTA(cliente.plan);
  const aptAResult = incluyeAPTA ? computeAPTA(apt_a_rows) : null;
  const aptASorted = aptAResult ? [aptAResult.V, aptAResult.N, aptAResult.AB, aptAResult.ME].sort((a,b)=>b.pct-a.pct) : null;
  const aptABanded = aptASorted ? aptASorted.map(d=>({...d, band: aptBand(d.pct)})) : null;

  const nombreRaw = cliente.nombre || '';
  const primerNombreRaw = nombreRaw.split(' ')[0] || '';
  const nombre = safeText(nombreRaw, '—');
  const primerNombre = safeText(primerNombreRaw, 'la persona evaluada');
  const edad = safeText(cliente.edad, '—');
  const fechaNac = cliente.fecha_nacimiento ? escapeHtml(new Date(cliente.fecha_nacimiento).toLocaleDateString('es-EC')) : "—";
  const ultimaFecha = (cliente.activaciones||[]).map(a=>a.completado_at).filter(Boolean).sort().pop();
  const fecha = ultimaFecha ? new Date(ultimaFecha).toLocaleDateString('es-EC') : new Date().toLocaleDateString('es-EC');
  const institucion = safeText(cliente.institucion, '—');
  const curso = safeText(cliente.curso, '—');
  const entrevista = cliente.entrevista_realizada || '';
  const motivo = escapeHtml(cliente.motivo_consulta || '');
  const expectativas = escapeHtml(cliente.expectativas || '');
  const dudas = escapeHtml(cliente.dudas_iniciales || '');

  const ENTREVISTA_LABEL = { estudiante: 'al estudiante', familia: 'a la familia', ambos: 'al estudiante y a su familia' };

  // ---- Top áreas CHASIDE con carreras ----
  const top2Cha = chaRanked.slice(0,2);

  // ---- Cruce integrador ----
  const academicoAF5 = incluyeAF5 ? af5Dims.academico : null;
  const academicoBand = incluyeAF5 ? af5Band(academicoAF5.centil) : null;
  const tecnicasCHT = chtAreas.tecnicas;
  const planCHT = chtAreas.plan;

  let crossText = "";
  if(incluyeAF5){
    if(academicoBand === 'low' && chaRanked[0].total >= 8){
      crossText += `<p>Un cruce relevante entre instrumentos: aunque el CHASIDE muestra un interés y aptitud consolidados hacia <b>${CHA_AREA_INFO[chaRanked[0].letter].name}</b>, el AF5 revela que ${primerNombre} tiene una autopercepción académica/laboral baja (Centil ${academicoAF5.centil ?? '—'}). Esto sugiere que la limitación no es de capacidad real, sino de confianza. Vale la pena reforzar explícitamente esa área en la devolución antes de que la inseguridad opaque un interés genuino y bien fundamentado.</p>`;
    } else if(academicoBand === 'high' && chaRanked[0].total >= 8){
      crossText += `<p>Los tres instrumentos convergen de forma consistente: el interés y aptitud del CHASIDE hacia <b>${CHA_AREA_INFO[chaRanked[0].letter].name}</b> se sostienen sobre una autopercepción académica/laboral sólida en el AF5 (Centil ${academicoAF5.centil ?? '—'}). Es una combinación que da mucha seguridad a la decisión vocacional.</p>`;
    }
  }

  // Convergencia CHASIDE ↔ Holland: correspondencia aproximada y solo
  // narrativa (no una equivalencia psicométrica estricta) entre las 7 áreas
  // del CHASIDE y los 6 tipos RIASEC, usada únicamente para señalar si ambos
  // instrumentos apuntan en una dirección compatible.
  const CHA_HOLLAND_AFFINITY = { C:['E','C'], H:['S','A'], A:['A'], S:['S','I'], I:['I','R'], D:['R','E'], E:['I','C'] };
  const afinesCha = CHA_HOLLAND_AFFINITY[chaRanked[0].letter] || [];
  const hollandTop2Keys = hollandBanded.slice(0,2).map(d=>d.key);
  const hayConvergenciaHolland = afinesCha.some(k => hollandTop2Keys.includes(k));
  if(hayConvergenciaHolland){
    crossText += `<p>El código Holland de ${primerNombre} (<b>${hollandResult.codigo}</b>) es coherente con la orientación hacia <b>${CHA_AREA_INFO[chaRanked[0].letter].name}</b> que ya señala el CHASIDE. Dos instrumentos distintos convergiendo en la misma dirección refuerza la confiabilidad de esa preferencia.</p>`;
  } else {
    crossText += `<p>El código Holland de ${primerNombre} (<b>${hollandResult.codigo}</b>) aporta un ángulo adicional al perfil: su tipo dominante (<b>${HOLLAND_INFO[hollandBanded[0].key].name}</b>) no coincide de forma directa con el área que lidera en el CHASIDE. Esto no es contradictorio. Vale la pena explorar en la devolución si ambas preferencias pueden combinarse dentro de una misma carrera, o si conviene priorizar una sobre la otra.</p>`;
  }

  if((tecnicasCHT.band === 'low' || planCHT.band === 'low')){
    const cuales = [tecnicasCHT.band==='low' ? 'las técnicas de estudio' : null, planCHT.band==='low' ? 'la planificación del tiempo' : null].filter(Boolean).join(' y ');
    crossText += `<p>El CHTE agrega una capa práctica importante: ${cuales} de ${primerNombre} está${cuales.includes(' y ')?'n':''} en un nivel bajo. Esto no cambia la orientación vocacional en sí, pero sí señala que antes de iniciar la carrera elegida conviene fortalecer estos hábitos. De lo contrario, incluso el interés más genuino puede verse minado por dificultades prácticas de sostenimiento académico durante el primer año.</p>`;
  } else if(tecnicasCHT.band === 'high' && planCHT.band === 'high'){
    crossText += `<p>El CHTE confirma que ${primerNombre} ya cuenta con las herramientas prácticas (técnicas de estudio y planificación) necesarias para sostener con éxito la exigencia de una carrera universitaria, sea cual sea el área elegida.</p>`;
  }

  // ---- Career cards ----
  // Correspondencia aproximada CHASIDE→Holland reutilizada aquí (misma tabla
  // narrativa definida arriba) para nombrar, cuando corresponde, qué tipo
  // Holland respalda cada área, ayuda a explicar el "por qué" con dos
  // instrumentos distintos en vez de solo uno.
  const careerCardsHtml = top2Cha.map((r, idx) => {
    const info = CHA_AREA_INFO[r.letter];
    const readinessNotes = [];
    if(incluyeAF5 && academicoBand === 'low') readinessNotes.push('reforzar la confianza académica antes de comenzar');
    if(tecnicasCHT.band === 'low') readinessNotes.push('desarrollar técnicas de estudio activo');
    if(planCHT.band === 'low') readinessNotes.push('construir un sistema de planificación del tiempo');
    const notaFinal = readinessNotes.length > 0
      ? `Antes de comenzar esta carrera, se recomienda especialmente: ${readinessNotes.join('; ')}.`
      : `${primerNombre} cuenta con una base de autoconcepto y hábitos de estudio favorable para sostener esta carrera desde el inicio.`;

    const afinesHolland = (CHA_HOLLAND_AFFINITY[r.letter] || []);
    const hollandRespalda = hollandBanded.slice(0,2).find(d => afinesHolland.includes(d.key));
    const hollandLine = hollandRespalda
      ? `El código Holland (<b>${hollandResult.codigo}</b>) respalda esta afinidad: el tipo <b>${HOLLAND_INFO[hollandRespalda.key].name}</b> encaja con este perfil de carreras.`
      : `El código Holland (<b>${hollandResult.codigo}</b>) no marca esta área como su tipo más fuerte, pero eso no la descarta. Vale la pena confirmarla en la devolución conversando ambos resultados juntos.`;

    return `
      <div class="career-card">
        <h4>${idx===1 ? 'Alternativa: ' : 'Prioridad: '}${info.name} <span class="mono" style="font-size:0.72rem;color:#8A6A28;font-weight:400;">(${r.total}/14 en CHASIDE)</span></h4>
        <div class="career-list"><b>Por qué se ajusta al perfil:</b> ${info.workStyle}</div>
        <div class="career-list"><b>Respaldo cruzado:</b> ${hollandLine}</div>
        <div class="career-list"><b>Carreras específicas a explorar:</b> ${info.careers.join(', ')}.</div>
        <div class="career-list"><b>A qué te puede llevar a futuro:</b> ${info.futureRoles || ''}</div>
        <div class="career-note">${notaFinal}</div>
      </div>
    `;
  }).join('');

  // ---- CHASIDE ranking + findings ----
  const chaMax = Math.max(...chaRanked.map(r=>r.total),1);
  const chaRankHtml = chaRanked.map((r,i)=>{
    const isTop = i<2;
    return `<div class="dim-row ${isTop?'high':''}">
      <div class="dim-top"><span class="dim-name">${CHA_AREA_INFO[r.letter].name}${isTop?'<span class="dim-tag">Top</span>':''}</span><span class="dim-pd">${r.total} / 14 · Interés ${r.interes} + Aptitud ${r.aptitud}</span></div>
      <div class="dim-bar-track"><div class="dim-bar-fill" style="width:${(r.total/chaMax*100)}%;"></div></div>
    </div>`;
  }).join('');

  const chaFindingsHtml = top2Cha.map((r,i)=>{
    const info = CHA_AREA_INFO[r.letter];
    return `<div class="finding-block high">
      <div class="fb-head"><h4>${info.name}</h4><span class="fb-total">${r.total} / 14 pts</span></div>
      <div class="fb-body">
        <p><b>Intereses asociados:</b> ${info.interesTraits.join(', ')}.</p>
        <p><b>Aptitudes asociadas:</b> ${info.aptitudTraits.join(', ')}.</p>
      </div>
    </div>`;
  }).join('');

  // ---- AF5 dims html ----
  const af5Max = 9.90;
  const af5ListHtml = af5Banded ? af5Banded.map(d=>{
    return `<div class="dim-row ${d.band}">
      <div class="dim-top"><span class="dim-name">${d.name}<span class="dim-tag">${BAND_LABEL[d.band]}</span></span><span class="dim-pd">PD ${d.pd.toFixed(2)} · Centil ${d.centil??'—'}</span></div>
      <div class="dim-bar-track"><div class="dim-bar-fill" style="width:${(d.pd/af5Max*100)}%;"></div></div>
    </div>`;
  }).join('') : '';

  // ---- Holland / RIASEC html ----
  const hollandListHtml = hollandBanded.map(d=>{
    return `<div class="dim-row ${d.band}">
      <div class="dim-top"><span class="dim-name">${d.name}<span class="dim-tag">${BAND_LABEL[d.band]}</span></span><span class="dim-pd">${d.score} / 10 · ${d.pct}%</span></div>
      <div class="dim-bar-track"><div class="dim-bar-fill" style="width:${d.pct}%;"></div></div>
    </div>`;
  }).join('');

  const top3Holland = hollandBanded.slice(0,3);
  let hollandInterpHtml = `<p>El código Holland resultante es <b>${hollandResult.codigo}</b>: ${top3Holland.map(d=>HOLLAND_INFO[d.key].name).join(' – ')}. Esto significa que las actividades que más atraen a ${primerNombre} combinan rasgos de estos tres tipos, con <b>${HOLLAND_INFO[top3Holland[0].key].name}</b> como el más marcado (${top3Holland[0].score}/10).</p>`;
  hollandInterpHtml += `<p>${HOLLAND_INFO[top3Holland[0].key].desc} En términos vocacionales, este tipo ${HOLLAND_INFO[top3Holland[0].key].fieldsNote}</p>`;
  const hollandGap1 = top3Holland[0].score - top3Holland[1].score;
  if(hollandGap1 <= 1){
    hollandInterpHtml += `<p>Los dos primeros tipos (<b>${HOLLAND_INFO[top3Holland[0].key].name}</b> y <b>${HOLLAND_INFO[top3Holland[1].key].name}</b>) aparecen prácticamente empatados, lo que sugiere un perfil de intereses combinado más que una única inclinación dominante. Ambas dimensiones son igualmente válidas para orientar la búsqueda de carrera.</p>`;
  }
  const hollandBajos = hollandBanded.filter(d=>d.band==='low');
  if(hollandBajos.length > 0){
    hollandInterpHtml += `<p>Las actividades típicas de <b>${hollandBajos.map(d=>HOLLAND_INFO[d.key].name).join('</b> y <b>')}</b> son las que menos atraen a ${primerNombre} dentro de este perfil. No se trata de una limitación, sino de una preferencia clara a tener en cuenta al momento de descartar opciones.</p>`;
  }

  // ---- CHTE areas html + recomendaciones solo para bajas/medias ----
  const chtMax = 100;
  const chtListHtml = chtSorted.map(d=>{
    return `<div class="dim-row ${d.band}">
      <div class="dim-top"><span class="dim-name">${d.name}<span class="dim-tag">${BAND_LABEL[d.band]}</span></span><span class="dim-pd">${d.si}/${d.total} · ${d.pct}%</span></div>
      <div class="dim-bar-track"><div class="dim-bar-fill" style="width:${d.pct}%;"></div></div>
    </div>`;
  }).join('');

  const chtRecoHtml = chtSorted.filter(d=>d.band!=='high').map(d=>{
    const items = CHT_REC_LIBRARY[d.key][d.band];
    return `<div class="reco-area">
      <div class="reco-area-head"><h4>${d.name}</h4><span class="reco-band ${d.band}">${BAND_LABEL[d.band]}</span></div>
      <ul class="reco-list">${items.slice(0,4).map(t=>`<li><span class="reco-mark">›</span><span>${t}</span></li>`).join('')}</ul>
    </div>`;
  }).join('');

  // ---- Resumen ejecutivo ----
  const af5Bajas = af5Banded ? af5Banded.filter(d=>d.band==='low') : [];
  const execHtml = `
    <div class="exec-summary">
      <div class="exec-card"><div class="ec-lbl">Área vocacional prioritaria</div><div class="ec-val">${CHA_AREA_INFO[chaRanked[0].letter].name}</div></div>
      <div class="exec-card"><div class="ec-lbl">Código Holland (RIASEC)</div><div class="ec-val">${hollandResult.codigo} · ${HOLLAND_INFO[hollandBanded[0].key].name}</div></div>
      ${incluyeAF5 ? `<div class="exec-card"><div class="ec-lbl">Autoconcepto: dimensión más alta</div><div class="ec-val">${af5Sorted[0].name} (Centil ${af5Sorted[0].centil??'—'})</div></div>` : ''}
      <div class="exec-card"><div class="ec-lbl">Hábitos de estudio: estado general</div><div class="ec-val">${chtBajas.length>0 ? chtBajas.length+' área'+(chtBajas.length>1?'s':'')+' por reforzar' : 'Perfil consolidado'}</div></div>
      ${aptBBanded ? `<div class="exec-card"><div class="ec-lbl">Aptitudes APT-B: mejor desempeño relativo</div><div class="ec-val">${aptBBanded[0].name} (${aptBBanded[0].pct}%)</div></div>` : ''}
    </div>

    <table class="summary-table">
      <thead><tr><th>Instrumento</th><th>Hallazgo principal</th><th>Resultado</th><th>Lectura breve</th></tr></thead>
      <tbody>
        <tr>
          <td>CHASIDE</td>
          <td>${CHA_AREA_INFO[chaRanked[0].letter].name}</td>
          <td class="mono">${chaRanked[0].total}/14</td>
          <td>${chaGap1<=2 ? 'Perfil compartido con una segunda área muy cercana' : 'Preferencia clara y consolidada'}</td>
        </tr>
        <tr>
          <td>Holland (RIASEC)</td>
          <td>${HOLLAND_INFO[hollandBanded[0].key].name}</td>
          <td class="mono">${hollandResult.codigo}</td>
          <td>${hayConvergenciaHolland ? 'Converge con el área CHASIDE prioritaria' : 'Aporta un ángulo adicional al perfil vocacional'}</td>
        </tr>
        ${incluyeAF5 ? `
        <tr>
          <td>AF5</td>
          <td>${af5Bajas.length>0 ? af5Bajas.map(d=>d.name).join(', ') : af5Sorted[0].name}</td>
          <td class="mono">${af5Bajas.length>0 ? 'Centil '+af5Bajas.map(d=>d.centil).join('/') : 'Centil '+af5Sorted[0].centil}</td>
          <td>${af5Bajas.length>0 ? 'Área de autoconcepto a reforzar' : 'Fortaleza de autoconcepto a capitalizar'}</td>
        </tr>
        ` : ''}
        <tr>
          <td>Hábitos de Estudio</td>
          <td>${chtBajas.length>0 ? chtBajas.map(d=>d.name).join(', ') : chtSorted[0].name}</td>
          <td class="mono">${chtBajas.length>0 ? chtBajas.map(d=>d.pct+'%').join('/') : chtSorted[0].pct+'%'}</td>
          <td>${chtBajas.length>0 ? 'Área práctica a fortalecer antes de iniciar la carrera' : 'Hábitos ya consolidados'}</td>
        </tr>
        ${aptBBanded ? `
        <tr>
          <td>APT-B</td>
          <td>${aptBBanded[0].name}</td>
          <td class="mono">${aptBBanded[0].pct}%</td>
          <td>${aptBBajas.length>0 ? 'Con '+aptBBajas.length+' área'+(aptBBajas.length>1?'s':'')+' a reforzar en el perfil' : 'Perfil de aptitudes consolidado'}</td>
        </tr>
        ` : ''}
      </tbody>
    </table>
  `;

  // ---- Conclusión global ----
  const conclusionText = `
    <p>El proceso de orientación vocacional-profesional de ${primerNombre} integra tres instrumentos complementarios: el <b>CHASIDE</b> (qué le interesa y para qué tiene aptitud), el <b>AF5</b> (cómo se percibe a sí mismo/a en distintas áreas de su vida) y el <b>Cuestionario de Hábitos de Estudio</b> (con qué herramientas prácticas cuenta hoy para sostener el esfuerzo académico).</p>
    <p>El área vocacional con mayor puntuación relativa es <b>${CHA_AREA_INFO[chaRanked[0].letter].name}</b>${chaGap1<=2 ? `, con una diferencia pequeña frente a <b>${CHA_AREA_INFO[chaRanked[1].letter].name}</b>. Por ello, conviene mantener abiertas ambas líneas de exploración.` : `. Este resultado orienta la exploración, pero no debe interpretarse como una elección predeterminada.`}</p>
    ${crossText}
    <p>En conjunto, los resultados no apuntan a una única respuesta cerrada, sino a un punto de partida estructurado: hacia dónde mirar primero, con qué fortalezas personales cuenta ${primerNombre} para sostener ese camino, y qué hábitos conviene fortalecer antes de comenzar.</p>
  `;

  // ---- RECOMENDACIONES PARA EL ESTUDIANTE ----
  const recoEstudiante = [];
  recoEstudiante.push(`Investigar en detalle la malla curricular, duración y campo laboral real de las carreras señaladas en <b>${CHA_AREA_INFO[chaRanked[0].letter].name}</b>${top2Cha.length>1?` y ${CHA_AREA_INFO[chaRanked[1].letter].name}`:''}, antes de tomar una decisión final.`);
  recoEstudiante.push(`Tener presente el código Holland obtenido (<b>${hollandResult.codigo}</b>) al momento de investigar carreras, ya que complementa el enfoque por áreas del CHASIDE con un lenguaje distinto pero compatible, útil para afinar la búsqueda dentro de cada área.`);
  recoEstudiante.push(`Conversar con profesionales en ejercicio de estas áreas para contrastar el perfil con la experiencia práctica del día a día, más allá de lo que transmite la malla curricular.`);
  recoEstudiante.push(`Investigar y comparar varias universidades o institutos técnicos distintos que ofrezcan estas carreras, sin asumir que el proceso es igual en todas partes: cada institución puede tener requisitos de admisión propios (examen de ingreso, nota mínima, entrevista, portafolio en el caso de carreras artísticas, materias prerrequisito, cupos limitados) y también difieren en duración, modalidad, costo y malla curricular. Revisar esto directamente en la página oficial de cada institución, o en una feria vocacional o jornada de puertas abiertas con contacto directo con la coordinación de la carrera, evita sorpresas al momento de postular.`);

  // Técnicas de estudio priorizadas: se toman de las 2-3 áreas del CHTE con menor puntaje,
  // extrayendo las recomendaciones ya construidas por área (CHT_REC_LIBRARY).
  const chtPrioritarias = chtSorted.filter(d=>d.band!=='high').slice(0,3);
  chtPrioritarias.forEach(d=>{
    const tecnica = CHT_REC_LIBRARY[d.key][d.band][0];
    recoEstudiante.push(`<b>${d.name}:</b> ${tecnica}`);
  });
  if(chtPrioritarias.length === 0){
    recoEstudiante.push(`Los hábitos de estudio ya evaluados están consolidados. El enfoque en esta etapa es de refinamiento: seguir puliendo las técnicas actuales durante el primer año de carrera, cuando la exigencia normalmente aumenta.`);
  }

  const recoEstudianteHtml = recoEstudiante.map((r,i)=>`<li><span class="reco-mark">${['i','ii','iii','iv','v','vi','vii'][i]||'·'}</span><span>${r}</span></li>`).join('');

  // ---- RECOMENDACIONES PARA LA FAMILIA ----
  const recoFamilia = [];
  recoFamilia.push(`Acompañar el proceso de decisión sin imponer una carrera basada en expectativas propias. El rol más útil de la familia aquí es sostener la exploración de ${primerNombre}, no acelerarla ni decidirla por adelantado.`);
  recoFamilia.push(`Reconocer explícitamente las fortalezas que arrojó esta evaluación (intereses, aptitudes y hábitos ya consolidados). El refuerzo positivo de lo que sí funciona acelera la confianza necesaria para decidir.`);
  recoFamilia.push(`Generar espacios de conversación regulares sobre el proceso vocacional, sin presión de "decidir ya". La indecisión en esta etapa es normal y no debe tratarse como un problema en sí mismo.`);

  const familiarBandAF5 = incluyeAF5 ? af5Band(af5Dims.familiar.centil) : null;
  if(familiarBandAF5 === 'low'){
    recoFamilia.push(`El AF5 sugiere que ${primerNombre} percibe cierta distancia o crítica en el ámbito familiar. Sin necesidad de indagar en el origen de esa percepción dentro de este informe, sí es recomendable que la familia muestre apoyo explícito e incondicional durante este proceso, independientemente de la carrera que finalmente se elija.`);
  }
  if(chtBajas.some(d=>['lugar','fisico','plan'].includes(d.key))){
    recoFamilia.push(`Facilitar en casa un espacio y horario fijo de estudio, y respetar ese tiempo sin interrupciones, apoya directamente las áreas de hábitos de estudio que salieron más bajas en este perfil.`);
  }
  recoFamilia.push(`Agendar la sesión de devolución junto a ${primerNombre}, para que las conclusiones de este informe se conversen en conjunto y no lleguen ya "decididas" desde afuera.`);

  const recoFamiliaHtml = recoFamilia.map((r,i)=>`<li><span class="reco-mark">${['i','ii','iii','iv','v','vi'][i]||'·'}</span><span>${r}</span></li>`).join('');

  // ---- BIENESTAR EMOCIONAL Y AUTOESTIMA (el "plus") ----
  const dimsBajasAF5 = af5Banded ? af5Banded.filter(d => d.band === 'low') : [];
  const dimsAltasAF5 = af5Banded ? af5Banded.filter(d => d.band === 'high') : [];
  let bienestarHtml = `<p>Elegir una carrera es, además de una decisión académica, un momento que pone a prueba la seguridad personal. Es normal que aparezcan dudas, comparaciones con otros o miedo a equivocarse. Sostener el bienestar emocional durante este proceso no es un tema aparte de la orientación vocacional: es parte de ella.</p>`;

  if(incluyeAF5){
    if(dimsBajasAF5.length > 0){
      const nombresBajas = dimsBajasAF5.map(d=>d.name).join(', ');
      bienestarHtml += `<p><b>Áreas a reforzar:</b> el AF5 señala ${dimsBajasAF5.length>1?'niveles bajos':'un nivel bajo'} en ${nombresBajas}. Esto no es un diagnóstico ni una etiqueta fija. Es una fotografía de cómo se percibe ${primerNombre} hoy, y las percepciones se pueden trabajar. Una autopercepción debilitada en estas áreas puede llevar a descartar opciones vocacionales válidas por inseguridad, no por falta de capacidad real, así que vale la pena abordarlo explícitamente antes de que eso ocurra.</p>`;
      dimsBajasAF5.forEach(d=>{
        const sugerencia = {
          academico: 'reconocer logros académicos concretos y recientes, por pequeños que sean, en vez de centrarse en comparaciones con el desempeño de otros.',
          social: 'proponer pequeños pasos de exposición social (un grupo de estudio, una actividad extracurricular) sin forzar un cambio drástico de la noche a la mañana.',
          emocional: 'practicar una técnica breve de respiración o pausa consciente antes de situaciones de evaluación o exposición, para reducir la intensidad del nerviosismo anticipado.',
          familiar: 'abrir una conversación familiar honesta y de bajo riesgo (no sobre la carrera, sino sobre cómo se siente cada uno en la relación) puede ser un primer paso más útil que forzar el tema vocacional.',
          fisico: 'enfocar la actividad física en el disfrute y el bienestar (no en la estética), y evitar comentarios comparativos sobre el cuerpo en el entorno cercano.'
        }[d.key];
        bienestarHtml += `<p style="margin-left:6px;">→ <b>${d.name}:</b> ${sugerencia}</p>`;
      });
    } else {
      bienestarHtml += `<p>El perfil de autoconcepto de ${primerNombre} no muestra áreas debilitadas. Es una base sólida para enfrentar la incertidumbre normal de esta etapa. Aun así, es útil recordarle explícitamente que la indecisión vocacional no refleja una falla personal, sino una etapa esperable del proceso.</p>`;
    }

    if(dimsAltasAF5.length > 0){
      bienestarHtml += `<p><b>Recurso a capitalizar:</b> <b>${dimsAltasAF5.map(d=>d.name).join(', ')}</b> ya funciona${dimsAltasAF5.length>1?'n':''} como un ancla emocional real. Nombrarlo explícitamente frente a ${primerNombre} (\"esto ya es una fortaleza tuya\") ayuda a sostener la confianza mientras se trabaja el resto.</p>`;
    }
  } else {
    bienestarHtml += `<p>Este plan no incluye el AF5 (autoconcepto), por lo que esta sección no detalla áreas específicas de autopercepción. Aun así, es útil recordarle explícitamente a ${primerNombre} que la indecisión vocacional es una etapa esperable del proceso y no una falla personal, y que buscar apoyo si la incertidumbre genera ansiedad significativa es una decisión válida en cualquier momento.</p>`;
  }


  // ---- Datos para los gráficos profesionales ----
  const chaChartSvg = buildBarChartSVG(
    chaRanked.map(r => ({ label: CHA_AREA_INFO[r.letter].name, value: (r.total/14*100), valueLabel: r.total + '/14', band: chaRanked.indexOf(r) < 2 ? 'high' : undefined }))
  );
  const af5ChartSvg = af5Banded ? buildRadarChartSVG(
    af5Banded.map(d => ({ name: d.name, value: d.centil, band: d.band }))
  ) : '';
  const chtChartSvg = buildBarChartSVG(
    chtSorted.map(d => ({ label: d.name, value: d.pct, valueLabel: d.pct + '%', band: d.band })),
    { suffix: '%' }
  );
  const hollandChartSvg = buildBarChartSVG(
    hollandBanded.map(d => ({ label: d.name, value: d.pct, valueLabel: d.score+'/10', band: d.band }))
  );

  // APT-B: instrumento propio de AURZANE (reemplaza al antiguo módulo DAT /
  // Forma T, retirado por derechos de autor). Sin percentiles poblacionales:
  // se reporta el puntaje corregido por adivinación sobre el máximo de cada
  // subtest y un nivel interpretativo en % sobre ese máximo, con las mismas
  // tres bandas (Bajo/Medio/Alto) usadas en APT-A y el CHTE.
  const APTB_MAX = { O:100, L:50, RE:60, VP:200 };
  const aptBChartSvg = aptBBanded ? buildBarChartSVG(
    aptBBanded.map(d => ({ label: d.name, value: d.pct, valueLabel: d.pct + '%', band: d.band }))
  ) : '';
  const aptBListHtml = aptBBanded ? aptBBanded.map(d => `
    <div class="dim-row ${d.band}">
      <div class="dim-top"><span class="dim-name">${d.name}<span class="dim-tag">${BAND_LABEL[d.band]}</span></span><span class="dim-pd">Puntaje corregido: ${d.corregido} / ${APTB_MAX[d.key]} (${d.aciertos} aciertos − ${d.errores} errores) · Nivel ${d.pct}%</span></div>
      <div class="dim-bar-track"><div class="dim-bar-fill" style="width:${d.pct}%;"></div></div>
    </div>`).join('') : '';

  let aptBInterpHtml = '';
  if(aptBBanded){
    const top = aptBBanded[0], bottom = aptBBanded[aptBBanded.length-1];
    aptBInterpHtml += `<p>En la batería APT-B, ${primerNombre} muestra su mejor desempeño relativo en <b>${top.name}</b> (nivel ${top.pct}%)${bottom.pct < top.pct ? `, frente a un desempeño más bajo en <b>${bottom.name}</b> (nivel ${bottom.pct}%)` : ', con un perfil parejo entre las cuatro áreas evaluadas'}.</p>`;
    if(aptBResult.O.pct>=70 && aptBResult.L.pct>=70){
      aptBInterpHtml += `<p>Ortografía y Lenguaje consolidados como fortaleza indican una base sólida de manejo del idioma escrito, un recurso especialmente relevante para carreras con alta carga de lectura, redacción o comunicación formal.</p>`;
    } else if(aptBResult.O.pct<40 && aptBResult.L.pct<40){
      aptBInterpHtml += `<p>Ortografía y Lenguaje aparecen como un área a reforzar. Esto no limita por sí solo ninguna elección vocacional, pero conviene trabajarlo explícitamente si la carrera elegida exige producción escrita frecuente (ensayos, informes, tesis).</p>`;
    }
    if(aptBResult.RE.pct>=70){
      aptBInterpHtml += `<p>Relaciones Espaciales se ubica como un punto fuerte, una aptitud especialmente útil en carreras que exigen visualizar objetos, estructuras o planos en tres dimensiones, como diseño, arquitectura, ingeniería o disciplinas técnicas.</p>`;
    } else if(aptBResult.RE.pct<40){
      aptBInterpHtml += `<p>Relaciones Espaciales aparece como un área más baja del perfil. Vale la pena tenerlo presente si la carrera elegida depende fuertemente de la visualización tridimensional, sin que esto descarte por sí solo esa opción.</p>`;
    }
    if(aptBResult.VP.pct>=70){
      aptBInterpHtml += `<p>Velocidad y Precisión perceptiva alta sugiere agilidad y exactitud para tareas administrativas, de revisión de detalle o de control de calidad bajo presión de tiempo.</p>`;
    } else if(aptBResult.VP.pct<40){
      aptBInterpHtml += `<p>Velocidad y Precisión perceptiva aparece como un área a reforzar, algo a tener presente si la carrera elegida exige revisión de detalle bajo presión de tiempo.</p>`;
    }
  }

  // APT-A: instrumento propio de AURZANE, sin percentiles poblacionales: se
  // reporta el puntaje corregido (0-40) y un nivel interpretativo en % sobre
  // ese máximo, con las mismas tres bandas (Bajo/Medio/Alto) del CHTE.
  const aptAChartSvg = aptABanded ? buildBarChartSVG(
    aptABanded.map(d => ({ label: d.name, value: d.pct, valueLabel: d.pct + '%', band: d.band }))
  ) : '';
  const aptAListHtml = aptABanded ? aptABanded.map(d => `
    <div class="dim-row ${d.band}">
      <div class="dim-top"><span class="dim-name">${d.name}<span class="dim-tag">${BAND_LABEL[d.band]}</span></span><span class="dim-pd">Puntaje corregido: ${d.corregido} / 40 (${d.aciertos} aciertos − ${d.errores} errores) · Nivel ${d.pct}%</span></div>
      <div class="dim-bar-track"><div class="dim-bar-fill" style="width:${d.pct}%;"></div></div>
    </div>`).join('') : '';

  let aptAInterpHtml = '';
  if(aptABanded){
    const top = aptABanded[0], bottom = aptABanded[aptABanded.length-1];
    aptAInterpHtml += `<p>En la batería APT-A, ${primerNombre} muestra su mejor desempeño relativo en <b>${top.name}</b> (nivel ${top.pct}%)${bottom.pct < top.pct ? `, frente a un desempeño más bajo en <b>${bottom.name}</b> (nivel ${bottom.pct}%)` : ', con un perfil parejo entre las cuatro áreas evaluadas'}.</p>`;
    if(aptAResult.V.pct>=70){
      aptAInterpHtml += `<p>Razonamiento Verbal alto sugiere buen manejo de relaciones de significado entre conceptos, un recurso valioso en carreras con fuerte componente de lectura, argumentación o comunicación.</p>`;
    } else if(aptAResult.V.pct<40){
      aptAInterpHtml += `<p>Razonamiento Verbal aparece como un área a reforzar. Conviene trabajarlo si la carrera elegida exige comprensión lectora o argumentación frecuente.</p>`;
    }
    if(aptAResult.N.pct>=70){
      aptAInterpHtml += `<p>Razonamiento Numérico alto indica facilidad para el cálculo y el razonamiento cuantitativo, relevante en carreras con carga matemática, económica o técnica.</p>`;
    } else if(aptAResult.N.pct<40){
      aptAInterpHtml += `<p>Razonamiento Numérico aparece como un área más baja del perfil. No descarta por sí solo ninguna carrera, pero conviene tenerlo presente si la formación elegida tiene alta carga de cálculo.</p>`;
    }
    if(aptAResult.AB.pct>=70){
      aptAInterpHtml += `<p>Razonamiento Abstracto alto sugiere buena capacidad para identificar patrones y reglas no verbales, útil en programación, diseño, ingeniería y disciplinas analíticas.</p>`;
    } else if(aptAResult.AB.pct<40){
      aptAInterpHtml += `<p>Razonamiento Abstracto aparece como un área a reforzar dentro del perfil de aptitudes.</p>`;
    }
    if(aptAResult.ME.pct>=70){
      aptAInterpHtml += `<p>Comprensión Mecánica alta indica buen entendimiento intuitivo de principios físicos aplicados, relevante en ingenierías, oficios técnicos y disciplinas con componente práctico-mecánico.</p>`;
    } else if(aptAResult.ME.pct<40){
      aptAInterpHtml += `<p>Comprensión Mecánica aparece como un área más baja del perfil, sin que esto descarte por sí solo ninguna elección vocacional.</p>`;
    }
  }

  let __secN = 0;
  const nextSec = () => String(__secN++).padStart(2,'0');
  let __modN = 0;
  const nextMod = () => ++__modN;

  const report = document.getElementById('reportContent');
  report.innerHTML = `
    <div class="report-head">
      <div class="rh-top">
        <div class="rh-brand">${safeText(membrete.nombre_marca, 'AURZANE')}</div>
        
        <div class="rh-meta"><div class="rh-meta-lbl">Fecha de la evaluación</div><div class="rh-meta-val">${fecha}</div></div>
      </div>
      <div class="rh-sub">${membrete.subtitulo ? safeText(membrete.subtitulo) + ' · ' : ''}Informe Integrado de Orientación Vocacional-Profesional</div>
      <div class="rh-rule"></div>
    </div>

    <div class="applicant-box">
      <div class="a-item"><div class="a-lbl">Postulante</div><div class="a-val">${nombre}</div></div>
      <div class="a-item"><div class="a-lbl">Edad</div><div class="a-val">${edad} años</div></div>
      <div class="a-item"><div class="a-lbl">Fecha de nacimiento</div><div class="a-val">${fechaNac}</div></div>
      <div class="a-item"><div class="a-lbl">Institución</div><div class="a-val">${institucion}</div></div>
      <div class="a-item"><div class="a-lbl">Curso</div><div class="a-val">${curso}</div></div>
    </div>
    <p class="section-note" style="margin-top:-24px;margin-bottom:32px;">Profesional a cargo: <b>Psi. Cl. Adrian Sánchez Samaniego</b>, Registro SENESCYT N.º 1033-2023-2618464.</p>

    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Motivo de la consulta</h2>
    <div class="brief-row" style="grid-template-columns:1fr;">
      <div class="brief-col">
        <p>${motivo ? motivo : `Proceso de orientación vocacional-profesional solicitado para apoyar la decisión de carrera de ${nombre}, a partir de sus propios intereses, aptitudes, autoconcepto y hábitos de estudio.`}</p>
        ${expectativas ? `<p style="margin-top:12px;"><b>Expectativas de la persona y su familia:</b> ${expectativas}</p>` : ''}
        ${dudas ? `<p style="margin-top:12px;"><b>Dudas o conflictos iniciales:</b> ${dudas}</p>` : ''}
      </div>
    </div>

    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Observación de conducta durante la evaluación</h2>
    <p class="section-note">${cliente.observacion_conducta ? escapeHtml(cliente.observacion_conducta) : `${primerNombre} mostró una actitud colaboradora durante la aplicación de los instrumentos, sin incidencias que reportar.`}</p>

    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Metodología y herramientas</h2>
    <p class="section-note">${entrevista ? `Entrevista realizada ${ENTREVISTA_LABEL[entrevista]}. ` : ''}Batería correspondiente al <b>Plan ${PLAN_LABEL_ES(cliente.plan)}</b>, aplicada por <b>${safeText(membrete.nombre_marca, 'AURZANE')}</b>. No se aplicaron técnicas proyectivas en este proceso.</p>
    <div class="interpretive-disclaimer"><strong>Alcance de la interpretación.</strong> Este informe es un apoyo para la orientación vocacional y la conversación profesional. Los resultados describen patrones de respuesta y desempeño en los instrumentos aplicados; no establecen por sí solos una carrera ideal, un diagnóstico clínico ni una predicción del futuro académico o laboral. La interpretación debe contextualizarse con la entrevista, la historia personal, el contexto educativo y las condiciones reales de cada opción formativa.</div>
    <div class="career-grid">
      <div class="career-card">
        <h4>CHASIDE: Evaluación de Orientación Vocacional</h4>
        <p class="career-list"><b>Objetivo:</b> identificar hacia qué áreas de formación profesional se orienta con mayor fuerza el perfil del evaluado.</p>
        <p class="career-list"><b>Qué mide:</b> intereses y aptitudes autopercibidas en siete áreas ocupacionales (Administrativas, Humanidades, Artísticas, Salud, Ingeniería, Defensa y Ciencias Exactas), mediante 98 preguntas de respuesta Sí/No.</p>
      </div>
      <div class="career-card">
        <h4>Holland: Intereses Vocacionales (RIASEC)</h4>
        <p class="career-list"><b>Objetivo:</b> identificar qué tipos de actividades resultan más atractivas para el evaluado, como segundo ángulo de intereses complementario al CHASIDE.</p>
        <p class="career-list"><b>Qué mide:</b> preferencia por actividades de tipo Realista, Investigador, Artístico, Social, Emprendedor y Convencional, mediante 60 preguntas de respuesta Sí/No, con un instrumento propio de AURZANE.</p>
      </div>
      ${incluyeAF5 ? `
      <div class="career-card">
        <h4>AF5: Autoconcepto Forma 5</h4>
        <p class="career-list"><b>Objetivo:</b> conocer cómo se percibe a sí mismo/a el evaluado en distintas áreas de su vida, como complemento al perfil vocacional.</p>
        <p class="career-list"><b>Qué mide:</b> autoconcepto académico/laboral, social, emocional, familiar y físico, mediante 30 frases de respuesta graduada (1-99), contrastadas contra baremos oficiales por edad y sexo.</p>
      </div>
      ` : ''}
      <div class="career-card">
        <h4>Cuestionario AURZANE de Hábitos de Estudio</h4>
        <p class="career-list"><b>Objetivo:</b> identificar con qué herramientas prácticas cuenta hoy el evaluado para sostener académicamente la carrera elegida.</p>
        <p class="career-list"><b>Qué mide:</b> actitud, lugar de estudio, estado físico, plan de trabajo, técnicas de estudio, exámenes y trabajos académicos, mediante 56 preguntas Sí/No.</p>
      </div>
      ${incluyeAPTB ? `
      <div class="career-card">
        <h4>APT-B: Ortografía, Lenguaje, Relaciones Espaciales y Velocidad</h4>
        <p class="career-list"><b>Objetivo:</b> medir aptitudes específicas (no autopercibidas) que complementan el perfil de intereses del CHASIDE con datos de desempeño real, mediante un instrumento propio de AURZANE.</p>
        <p class="career-list"><b>Qué mide:</b> Ortografía, Lenguaje, Relaciones Espaciales y Velocidad y Precisión perceptiva, mediante 410 ítems cronometrados por área, corregidos por adivinación y expresados en una escala interpretativa propia (Bajo/Medio/Alto).</p>
      </div>
      ` : ''}
      ${incluyeAPTA ? `
      <div class="career-card">
        <h4>APT-A: Batería de Aptitudes</h4>
        <p class="career-list"><b>Objetivo:</b> medir aptitudes específicas de desempeño real con un instrumento propio de AURZANE, diseñado con la misma lógica y nivel de detalle que una batería de aptitudes diferenciales de referencia.</p>
        <p class="career-list"><b>Qué mide:</b> Razonamiento Verbal, Razonamiento Numérico, Razonamiento Abstracto y Comprensión Mecánica, mediante 40 ítems cronometrados por área (160 en total), corregidos por adivinación y expresados en una escala interpretativa propia (Bajo/Medio/Alto).</p>
      </div>
      ` : ''}
    </div>

    <div class="module-divider"><span>Resultados de la evaluación</span></div>

    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Resumen ejecutivo</h2>
    ${execHtml}

    <div class="module-divider"><span>Módulo ${nextMod()}: Orientación Vocacional (CHASIDE)</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Perfil consolidado por área</h2>
    <div class="chart-box">${chaChartSvg}</div>
    <div class="dim-list">${chaRankHtml}</div>
    <h3 class="sub-title">Áreas de mayor afinidad</h3>
    ${chaFindingsHtml}

    <div class="module-divider"><span>Módulo ${nextMod()}: Intereses Vocacionales (Holland/RIASEC)</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Perfil de intereses RIASEC</h2>
    <p class="section-note">Instrumento propio de AURZANE inspirado en la teoría pública de John Holland. Mide la fuerza relativa de seis tipos de interés vocacional mediante 60 preguntas Sí/No. Es una medida ipsativa (compara preferencias dentro de la misma persona), por lo que no reporta percentiles poblacionales.</p>
    <div class="chart-box">${hollandChartSvg}</div>
    <div class="dim-list">${hollandListHtml}</div>
    ${hollandInterpHtml}

    ${incluyeAF5 ? `
    <div class="module-divider"><span>Módulo ${nextMod()}: Autoconcepto (AF5)</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Perfil por dimensión</h2>
    <div class="chart-box">${af5ChartSvg}</div>
    <div class="dim-list">${af5ListHtml}</div>
    ` : ''}

    <div class="module-divider"><span>Módulo ${nextMod()}: Hábitos de Estudio</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Perfil por área</h2>
    <div class="chart-box">${chtChartSvg}</div>
    <div class="dim-list">${chtListHtml}</div>
    ${chtRecoHtml ? `<h3 class="sub-title">Recomendaciones prioritarias</h3>${chtRecoHtml}` : ''}

    ${aptBBanded ? `
    <div class="module-divider"><span>Módulo ${nextMod()}: Ortografía, Lenguaje, Relaciones Espaciales y Velocidad (APT-B)</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Perfil de aptitudes APT-B</h2>
    <p class="section-note">Instrumento propio de AURZANE. El puntaje se corrige por adivinación y se expresa en una escala interpretativa de tres niveles (Bajo/Medio/Alto) propia de AURZANE. No corresponde a un percentil poblacional externo, ya que este instrumento todavía no cuenta con un estudio de tipificación con muestra de referencia.</p>
    <div class="chart-box">${aptBChartSvg}</div>
    <div class="dim-list">${aptBListHtml}</div>
    ${aptBInterpHtml}
    ` : ''}

    ${aptABanded ? `
    <div class="module-divider"><span>Módulo ${nextMod()}: Batería de Aptitudes APT-A</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Perfil de aptitudes APT-A</h2>
    <p class="section-note">Instrumento propio de AURZANE. El puntaje se corrige por adivinación y se expresa en una escala interpretativa de tres niveles (Bajo/Medio/Alto) propia de AURZANE. No corresponde a un percentil poblacional externo, ya que este instrumento todavía no cuenta con un estudio de tipificación con muestra de referencia.</p>
    <div class="chart-box">${aptAChartSvg}</div>
    <div class="dim-list">${aptAListHtml}</div>
    ${aptAInterpHtml}
    ` : ''}

    <div class="module-divider"><span>Síntesis integradora</span></div>
    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Áreas y carreras para explorar</h2>
    <p class="section-note">Las dos áreas con mayor puntaje en el CHASIDE, consideradas junto con el código Holland y el resto de la batería, sirven como punto de partida para explorar opciones. No constituyen una recomendación definitiva ni determinan por sí solas una elección de carrera.</p>
    <div class="career-grid">${careerCardsHtml}</div>

    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Conclusión integrada</h2>
    <div class="conclusion-box">${conclusionText}</div>

    <h2 class="section-title"><span class="st-num">${nextSec()}</span> Recomendaciones</h2>
    <p class="section-note">Recomendaciones específicas organizadas por destinatario, para que cada una se traduzca en una acción concreta.</p>

    <h3 class="sub-title">Para el estudiante</h3>
    <ul class="reco-list" style="border:1px solid var(--hair);background:var(--wash);margin-bottom:30px;">
      ${recoEstudianteHtml}
    </ul>

    <h3 class="sub-title">Para la familia</h3>
    <ul class="reco-list" style="border:1px solid var(--hair);background:var(--wash);margin-bottom:30px;">
      ${recoFamiliaHtml}
    </ul>

    <h3 class="sub-title">Bienestar emocional y autoestima</h3>
    <div class="conclusion-box" style="margin-bottom:36px;">${bienestarHtml}</div>

    <div class="methodology">
      <b>Sobre este informe.</b> Este documento integra tres fuentes de información independientes para ofrecer una lectura completa del perfil vocacional de ${primerNombre}. Su mayor valor se obtiene al conversarlo directamente en una sesión de devolución personalizada, donde cada hallazgo pueda contextualizarse con la historia y las circunstancias particulares del caso.
    </div>

    <div class="signature-block">
      <div class="sig-line">Adrian Sánchez Samaniego</div>
      <div class="sig-name">Psi. Cl. Adrian Sánchez Samaniego</div>
      <div class="sig-title">Psicólogo Clínico</div>
      <div class="sig-reg">Registro SENESCYT N.º 1033-2023-2618464</div>
      ${membrete.nota_legal ? `<div class="sig-reg" style="margin-top:4px;">${safeText(membrete.nota_legal)}</div>` : ''}
    </div>

    <div class="report-footer">
      <span>${safeText(membrete.nombre_marca, 'AURZANE')} · ${membrete.subtitulo || 'Orientación Vocacional-Profesional'}</span>
      <span>Documento confidencial de uso clínico</span>
    </div>
  `;

  window.scrollTo({top:0, behavior:'smooth'});
}
