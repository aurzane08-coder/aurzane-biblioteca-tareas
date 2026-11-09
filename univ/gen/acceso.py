# -*- coding: utf-8 -*-
"""Cómo funciona el acceso a la universidad en cada país (texto propio de AURZANE, general y estable).
Lo usan las fichas de universidades y las páginas de país. Sin cifras ni fechas que cambian cada año."""

ACCESO = {
    'España': [
        'En España se accede al grado con el título de Bachillerato (o de Técnico Superior de FP) y la PAU, la prueba de acceso a la universidad. La nota de admisión se calcula sobre 14 puntos: la media de Bachillerato y la fase general cuentan hasta 10, y la fase específica suma hasta 4 más según las ponderaciones de cada grado.',
        'La preinscripción en las universidades públicas se hace en cada comunidad autónoma, normalmente en junio y julio, ordenando los grados por preferencia. Las notas de corte cambian cada año, porque dependen de las plazas y de la demanda.',
        'Los grados suelen durar cuatro años (240 créditos ECTS). En las universidades públicas el precio del crédito lo fija cada comunidad autónoma y existen becas del Ministerio de Educación y de las propias universidades.',
    ],
    'Ecuador': [
        'En Ecuador se accede a la educación superior con el título de bachiller, inscribiéndose en el registro nacional de educación superior y superando el proceso de admisión de cada institución.',
        'La Constitución establece la gratuidad de la educación superior pública de tercer nivel, vinculada a la responsabilidad académica del estudiante. Las universidades privadas fijan sus propios aranceles y suelen ofrecer becas.',
        'Además de las universidades, hay institutos técnicos y tecnológicos que ofrecen carreras más cortas y prácticas. Antes de matricularte, comprueba que la carrera esté aprobada por el Consejo de Educación Superior (CES).',
    ],
    'México': [
        'En México se accede a la licenciatura con el certificado de bachillerato o preparatoria y aprobando el examen de admisión de cada universidad. Muchas usan su propio examen y otras el EXANI-II del CENEVAL.',
        'Las licenciaturas duran normalmente entre cuatro y cinco años. Las universidades públicas tienen cuotas bajas y una alta demanda, por lo que la preparación del examen es clave.',
        'Si eliges una institución privada, comprueba que la carrera tenga RVOE (Reconocimiento de Validez Oficial de Estudios) de la SEP o de la autoridad estatal: sin él, el título puede no tener validez oficial.',
    ],
    'Colombia': [
        'En Colombia la mayoría de las universidades tiene en cuenta el resultado del examen Saber 11 del ICFES, y algunas aplican además su propio examen o entrevista.',
        'Las carreras profesionales suelen durar entre cuatro y cinco años. Además de universidades, hay instituciones técnicas y tecnológicas con programas más cortos.',
        'Antes de inscribirte, verifica en el SNIES que el programa tenga registro calificado vigente. La acreditación de alta calidad indica que la institución o el programa ha superado una evaluación adicional.',
    ],
    'Argentina': [
        'En Argentina, las universidades nacionales (públicas) tienen grado gratuito y, en general, ingreso directo con el título secundario. Muchas piden aprobar antes un curso de ingreso o un ciclo inicial.',
        'Las universidades privadas cobran aranceles y tienen sus propios requisitos de admisión. Las carreras de grado suelen durar entre cuatro y seis años.',
        'Además de las universidades, los institutos de educación superior ofrecen tecnicaturas y profesorados de menor duración.',
    ],
    'Chile': [
        'En Chile se accede a la universidad mediante el Sistema de Acceso a la Educación Superior: se rinde la PAES y se postula con un puntaje que combina las pruebas, las notas de enseñanza media (NEM) y el ranking del colegio.',
        'Las carreras universitarias suelen durar entre cuatro y seis años. Los institutos profesionales y los centros de formación técnica ofrecen alternativas más cortas.',
        'La gratuidad cubre a estudiantes de los hogares de menores ingresos en las instituciones adscritas. Conviene revisar también la acreditación de la institución.',
    ],
    'Perú': [
        'En Perú cada universidad organiza su propio examen de admisión, y muchas ofrecen además ingreso por centro preuniversitario o por haber estado entre los primeros puestos del colegio.',
        'Las universidades públicas no cobran por la enseñanza de pregrado y son muy demandadas. Las privadas fijan sus pensiones.',
        'Antes de elegir, comprueba que la universidad tenga el licenciamiento de la SUNEDU, que garantiza unas condiciones básicas de calidad.',
    ],
    'Estados Unidos': [
        'En Estados Unidos cada universidad gestiona su admisión. Se valora el expediente de la escuela secundaria (GPA), los ensayos, las cartas de recomendación y las actividades; muchas universidades han hecho opcionales los exámenes SAT o ACT.',
        'Muchas solicitudes se envían a través de plataformas comunes como Common App. Los community colleges ofrecen títulos de dos años y permiten después transferirse a una universidad.',
        'Los costos varían mucho entre universidades públicas y privadas, por lo que conviene revisar la ayuda financiera y las becas. Los estudiantes internacionales necesitan un visado de estudiante y, normalmente, acreditar su nivel de inglés.',
    ],
    'Brasil': [
        'En Brasil el ENEM es la principal vía de acceso: su nota se usa en el SISU para entrar en las universidades públicas, que son gratuitas, y en el ProUni, que concede becas en universidades privadas.',
        'Algunas universidades mantienen además su propio examen, el vestibular. Las carreras de grado suelen durar entre cuatro y seis años.',
    ],
    'Reino Unido': [
        'En el Reino Unido las solicitudes de grado se hacen a través de UCAS. Se piden calificaciones de nivel A level o equivalentes, una declaración personal y una referencia.',
        'Los grados suelen durar tres años en Inglaterra, Gales e Irlanda del Norte y cuatro en Escocia. Los estudiantes internacionales deben acreditar su nivel de inglés y revisar las tasas, que son más altas para ellos.',
    ],
    'Canadá': [
        'En Canadá cada universidad gestiona su admisión, y algunas provincias tienen plataformas comunes de solicitud. Se valora el expediente de secundaria y, para estudiantes extranjeros, el nivel de inglés o de francés.',
        'Los grados suelen durar entre tres y cuatro años. Los estudiantes internacionales necesitan un permiso de estudios.',
    ],
    'Alemania': [
        'En Alemania se necesita un título que dé acceso a la universidad (Hochschulzugangsberechtigung). Los estudiantes extranjeros suelen solicitar a través de uni-assist o directamente a cada universidad.',
        'En la mayoría de los estados federados las universidades públicas no cobran matrícula por el grado, aunque sí una cuota semestral. Muchos grados se imparten en alemán y piden acreditar el idioma.',
    ],
    'Francia': [
        'En Francia el acceso al primer año de grado se gestiona por la plataforma Parcoursup. Los estudiantes de fuera de la Unión Europea suelen hacer los trámites a través de Campus France.',
        'Las universidades públicas tienen tasas reducidas y los grados (licence) duran tres años.',
    ],
    'Italia': [
        'En Italia muchas carreras tienen acceso libre con el título de secundaria, y otras, como Medicina, tienen plazas limitadas con prueba de acceso.',
        'Las universidades públicas fijan sus tasas según los ingresos familiares. Los estudiantes extranjeros suelen hacer una preinscripción a través del portal Universitaly.',
    ],
    'Portugal': [
        'En Portugal el acceso a las universidades públicas se hace mediante un concurso nacional que tiene en cuenta las notas de secundaria y los exámenes nacionales. Hay vías específicas para estudiantes internacionales.',
        'Las licenciaturas suelen durar tres años, y las tasas de las públicas son moderadas.',
    ],
}

GENERAL = [
    'Los requisitos de acceso, los plazos y los precios cambian según el país, la institución y el año. Por eso conviene consultar siempre la web oficial de la universidad y el organismo de educación superior del país antes de tomar una decisión.',
    'Si vas a estudiar fuera de tu país, revisa también si necesitas homologar tu título de secundaria, acreditar el idioma de las clases o tramitar un visado de estudiante.',
]

ELEGIR = ('Para elegir bien no basta con el nombre de la universidad. Compara el plan de estudios de la carrera, las prácticas, '
          'la modalidad (presencial o en línea), el coste total y las salidas profesionales. Si todavía dudas qué estudiar, '
          'un test vocacional te ayuda a ordenar tus intereses y aptitudes antes de decidir.')


def acceso(pais):
    return ACCESO.get(pais) or GENERAL
