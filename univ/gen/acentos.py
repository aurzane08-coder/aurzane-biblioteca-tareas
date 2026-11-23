"""Diccionario de acentos para nombres que llegan en mayúsculas sin tildes (Ecuador, Chile, Colombia). Lo usan gen.py y oficiales/importar.py."""
import re, unicodedata

# ---------------------------------------------------------------- acentos (Ecuador)
ACENTOS = {w.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u'): w for w in '''
Administración Agronomía Agropecuaria Agrícola Analítica Análisis Antropología Arqueología Artística Artísticas Auditoría Automatización Biología Biotecnología Biomédica Bioquímica Comunicación Contabilidad Construcción Criminalística Criminología Diseño Dirección Docencia Ecología Economía Educación Electricidad Eléctrica Electromecánica Electrónica Energía Enfermería Estética Física Fisioterapia Fonoaudiología Gastronomía Geografía Geología Gestión Gráfico Gráfica Hidráulica Historia Hotelería Información Informática Ingeniería Inglés Innovación Investigación Jurídica Jurídicas Lingüística Logística Matemática Matemáticas Mecánica Mecatrónica Medicina Metalmecánica Minería Música Nutrición Odontología Óptica Optometría Pedagogía Periodismo Petróleos Petroquímica Política Políticas Producción Programación Psicología Psicopedagogía Publicidad Química Radiología Recreación Rehabilitación Relaciones Seguridad Sociología Software Técnica Técnico Tecnología Tecnologías Telecomunicaciones Telemática Terapéutica Topografía Traducción Turística Turismo Veterinaria Zootecnia Acuicultura Cerámica Fotografía Cinematografía Animación Mecánico Electrónico Cosmetología Podología Atención Promoción Prevención Planificación Organización Comercialización Construcción Edificación Pública Público Inclusión Mediación Gerontología Logopedia Neuropsicología Psicorrehabilitación Rehabilitación Física Tecnológico Tecnológica Teología Filosofía Lógica Biomédicas Ciencias Química Farmacia Bioquímica Clínica Clínico Clínicas Diagnóstico Imagenología Imágenes Cirugía Agroindustrial Industrialización Cartografía Climatización Refrigeración Instalación Instalaciones Panadería Pastelería Cocina Bebidas Acústica Escénicas Plásticas Lenguas Idiomas Comunicación Educativa Educativo Básica Inicial Atención Integral Aeronáutica Náutica Marítima Pesquería Forestal Agroforestal Biomecánica Robótica Inteligencia Artificial Cibernética Ciberseguridad Electromédica Higiene Odontológica Mecánica Automotriz Prótesis Dental Química Laboratorio Analítico Analíticos Técnicas
'''.split()}
for _w in 'Católica Politécnica Amazónica Bolívar Simón Península Ibérica Pedagógico Académico Académica Manabí Tecnológicos Estatal Técnico Educación Agrícola Pacífico Atlántico Caribe Guayaquil Milagro Andrés Martín Ángel Ramón Hernández Martínez Pérez Gómez Rodríguez Bilingüe Indígena Marítimo Politécnico Médica Médicas'.split():
    ACENTOS[unicodedata.normalize('NFD', _w.lower()).encode('ascii', 'ignore').decode()] = _w
ACENTOS.update({'y': 'y', 'en': 'en', 'de': 'de', 'del': 'del'})




# vocabulario de Chile (SIES) y Colombia (SNIES), que llegan en mayúsculas sin tildes (23/11/2026)
for _w in """Computación Kinesiología Párvulos Concepción Valparaíso Bío Tarapacá Autónoma Ibáñez Henríquez Tomás Aysén Ñuble Región Mecánico
Acuícola Telecomunicación Máquinas Eléctrico Energías Metalúrgica Metalurgia Geomensura Estadística Geográfica Cinematográfico Cinematográfica Actuación
Teatral Licenciatura Magíster Castellano Inglesa Religión Lenguaje Enseñanza Farmacéutica Farmacéutico Químico Químicos Biológicas Biológica Médico Odontólogo
Matrón Matrona Psicólogo Sociólogo Antropólogo Geógrafo Geólogo Biólogo Ecólogo Físico Matemático Estadístico Ingeniería Ingeniero Técnicos Prótesis Óptico
Análisis Diagnóstico Terapéutico Políticas Jurídico Económico Económica Económicas Administrativo Administrativa Logístico Turístico Gastronómico Gastronómica
Automatización Mecatrónico Electrónicos Informático Telemático Agrónomo Agrónoma Agroindustrias Pecuario Pecuaria Zootecnista Topógrafo Cartógrafo Fotógrafo
Músico Artístico Escénico Plástico Diseñador Diseñadora Gráfica Arquitectónico Construcción Edificación Climática Hidrológica Hídricos Ambientales Energético
Energética Minero Minera Petróleo Química Gestión Técnica Tecnológico Tecnológica Tecnólogo Tecnóloga Público Pública Públicos Públicas Básico Básica Lingüística
Matemáticas Física Educación Pedagógica Pedagógico Psicopedagógico Fonoaudiólogo Nutricionista Kinesiólogo Odontológica Clínico Clínica Médica Quirúrgica
Quirúrgico Cirugía Anestesiología Radiología Pediatría Psiquiatría Cardiología Ginecología Obstetricia Oftalmología Dermatología Neurología Oncología
Urología Ortopedia Traumatología Gerontología Epidemiología Toxicología Farmacología Microbiología Inmunología Patología Fisiología Bioética
Información Comunicación Producción Innovación Dirección Administración Planificación Programación Investigación Evaluación Formación Orientación Atención
Intervención Rehabilitación Recreación Animación Narración Traducción Interpretación Organización Mediación Negociación Conservación Restauración
Iluminación Edición Postproducción Ilustración Composición Dirección Instrumentación Electrificación Refrigeración Climatización Fabricación Soldadura
Mantención Mantenimiento Operación Operaciones Prevención Protección Señalización Navegación Aviación Aeronáutico Náutico Pesquero Acuicultor Silvicultura
Biotecnológica Bioinformática Nanotecnología Robótica Domótica Teleinformática Ciberseguridad Analítica Ingenieril Ingenieros Matemática Jurídicas
Católica Pontificia Señora Bolivariana Javeriana Antártica Atacameña Amazonía Orinoquía Bogotá Medellín Cúcuta Ibagué Popayán Montería Ciénaga Facatativá
Fusagasugá Tuluá Envigado Itagüí Sogamoso Duitama Chiquinquirá Tumaco Quibdó Riohacha Valledupar Sincelejo Caquetá Guaviare Vaupés Guainía Boyacá Córdoba
Nariño Quindío Chocó Atlántico Bolívar Antioquia Pacífico Caribe Andina Andino Colombiano Colombiana Cooperativa Corporación Fundación Institución Escuela
Tecnológicos Politécnico Politécnica Agustiniana Adventista Pedagógica Militar Policía Educación Superior Técnica Técnico Profesional Artes Música
Pediátrica Pediátrico Genética Genético Estratégica Estratégico Didáctica Didáctico Geotécnica Oncológica Oncológico Psicoanalítica Psicosomática Diagnóstica Geomática Estéticas Éticas Ética Práctica Prácticas Práctico Área Áreas Través Astrofísica Desafíos Extracorpórea Neurocirugía Anatomía Patológica Plástica Plásticas Hispánicas Hispánica Dietética Arqueólogo Arqueóloga Intérprete Químico Bioquímico Cientista Político Política Músico Electrofisiología Cardíaca Cardíaco Ortopédica Hidrológico Agrícolas Económicas Teórica Teórico Histórica Histórico Crítica Crítico Gráfico Informáticos Informáticas Telemáticos Electrónicas Mecánicos Técnicas Químicas Físicas Médicos Clínicos Ciencias Administración Contaduría Economía Finanzas Mercadeo Psicología Enfermería Odontología Optometría Fonoaudiología Bacteriología Instrumentación""".split():
    ACENTOS[unicodedata.normalize('NFD', _w.lower()).encode('ascii', 'ignore').decode()] = _w


SUFIJOS = [(r'cion$', 'ción'), (r'sion$', 'sión'), (r'logia$', 'logía'), (r'grafia$', 'grafía'), (r'metria$', 'metría'), (r'nomia$', 'nomía'),
           (r'sofia$', 'sofía'), (r'terapia$', 'terapia'), (r'iatria$', 'iatría'), (r'patia$', 'patía')]


def acentuar(t, forzar=False):
    """Pone las tildes que faltan. Sin forzar no toca textos que ya traen alguna tilde (Ecuador); con forzar (datos oficiales de
    Chile y Colombia, que mezclan palabras con y sin tilde) revisa cada palabra y aplica además terminaciones seguras (-ción, -sión, -logía…)."""
    if not t or (not forzar and any(c in t for c in 'áéíóúÁÉÍÓÚñ')):
        return t
    def r(m):
        w = m.group(0); k = w.lower()
        if k in ACENTOS and len(k) > 3:
            a = ACENTOS[k]
            return a[0].upper() + a[1:] if w[0].isupper() else a.lower()
        if forzar and len(k) > 4:
            for pat, fin in SUFIJOS:
                if re.search(pat, k):
                    a = re.sub(pat, fin, k)
                    return (a[0].upper() + a[1:]) if w[0].isupper() else a
        return w
    return re.sub(r'(?<![A-Za-zÁÉÍÓÚáéíóúÑñÜü])[A-Za-z]+(?![A-Za-zÁÉÍÓÚáéíóúÑñÜü])', r, t)
