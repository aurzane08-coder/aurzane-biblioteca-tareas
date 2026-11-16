# Textos que prometían algo que los tests gratis no dan (devolución con un profesional, interpretación clínica).
# Copia del original en <web>/eliminar/textos-FECHA/. Uso: python3 textos.py <carpeta_www>
import os, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
CAMBIOS = {
    'mind.aurzane.com/public_html/index.html': [
        ('<h4>Sin algoritmos genéricos</h4><p>Interpretación clínica real, no un resultado automático sin contexto.</p>',
         '<h4>Escalas validadas</h4><p>Cuestionarios publicados que usan los profesionales, con su referencia.</p>'),
        ('<h4>100% virtual</h4><p>Tests online, corrección automática, devolución con profesional.</p>',
         '<h4>Resultado al instante</h4><p>Tu puntuación explicada al momento, gratis y sin registro.</p>')],
    'ovp.aurzane.com/public_html/generar-informe.html': [('informe-opciones.js?v=20261018b', 'informe-opciones.js?v=20261116a'), ('informe-v2.js?v=20261109c', 'informe-v2.js?v=20261116b'), ('informe-v2.js?v=20261116a', 'informe-v2.js?v=20261116b')],
    'ovp.aurzane.com/public_html/informe-ejemplo.html': [('informe-opciones.js?v=20261018b', 'informe-opciones.js?v=20261116a'), ('informe-v2.js?v=20261109c', 'informe-v2.js?v=20261116b'), ('informe-v2.js?v=20261116a', 'informe-v2.js?v=20261116b')],
    # Admin: acceso directo a la gestión de colegios (alta de colegios, enfoque general o militar, equipo y estudiantes)
    'aurzane.com/public_html/admin.html': [
        ('        <span class="nav-label">Membretes</span>\n      </div>\n',
         '        <span class="nav-label">Membretes</span>\n      </div>\n      <a class="nav-item" href="https://ovp.aurzane.com/colegio.html" style="text-decoration:none;color:inherit">\n        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 10l9-6 9 6"/><path d="M5 10v9h14v-9M9 19v-5h6v5"/></svg>\n        <span class="nav-label">Colegios</span>\n      </a>\n')],
    # Colegios: acceso propio para el equipo del colegio y para sus estudiantes (panel en ovp.aurzane.com/colegio.html)
    'aurzane.com/public_html/colegios/index.html': [
        ('<a href="#contacto">Contacto</a></nav>', '<a href="#contacto">Contacto</a><a href="https://ovp.aurzane.com/colegio.html">Entrar al panel del colegio</a></nav>'),
        ('<a class="btn borde" href="https://ovp.aurzane.com/informe-ejemplo.html">Ver un informe de ejemplo</a>\n    </div>',
         '<a class="btn borde" href="https://ovp.aurzane.com/informe-ejemplo.html">Ver un informe de ejemplo</a>\n    </div>\n    <p class="nota">¿Tu colegio ya tiene acceso? <a href="https://ovp.aurzane.com/colegio.html">Entra al panel del colegio</a> con tu cuenta AURZANE ID.</p>'),
        ('<p class="sub">Todo el proceso es en línea. El colegio solo comparte un enlace con sus estudiantes.</p>',
         '<p class="sub">Todo el proceso es en línea. Hay dos accesos: el del equipo del colegio y el de cada estudiante.</p>'),
        ('<div class="paso"><h3>Enlace propio</h3><p>Preparamos el membrete de tu colegio y un enlace exclusivo. Quien entra por él recibe su informe con vuestra identidad.</p></div>',
         '<div class="paso"><h3>Panel del colegio</h3><p>Preparamos el membrete de tu colegio, su enlace y su código QR. Orientación y dirección entran al panel con su cuenta AURZANE ID y ven quién empezó, quién terminó y en qué curso está cada estudiante.</p></div>'),
        ('<div class="paso"><h3>Evaluaciones</h3><p>Cada estudiante crea su cuenta y elige sus evaluaciones.',
         '<div class="paso"><h3>Cuenta del estudiante</h3><p>Cada estudiante entra por el enlace o el QR del colegio, crea su cuenta AURZANE ID y queda vinculado a su colegio. Después elige sus evaluaciones.'),
        ('<div><b>Datos protegidos</b><span>Los resultados de cada estudiante se guardan aparte del resto de la plataforma y solo los ve él o ella y el profesional responsable.</span></div>',
         '<div><b>Datos protegidos</b><span>El colegio ve el avance de cada estudiante. Las respuestas y el informe solo los ve el propio estudiante y el profesional responsable, salvo que el estudiante decida compartir su informe con el colegio desde su portal.</span></div>'),
        # fase 4 (16/11/2026): el panel muestra intereses agregados y el modo aula de LEARN está disponible para los docentes
        ('<div><b>Datos protegidos</b><span>El colegio ve el avance de cada estudiante. Las respuestas y el informe solo los ve el propio estudiante y el profesional responsable, salvo que el estudiante decida compartir su informe con el colegio desde su portal.</span></div>',
         '<div><b>Datos protegidos</b><span>El colegio ve el avance de cada estudiante y, sin nombres, cuántos tienen cada área de interés como principal, con el consentimiento informado de las familias. El informe completo solo lo ve el colegio si el estudiante decide compartirlo desde su portal.</span></div>'),
        ('<div><b>Lenguaje claro</b><span>Escrito para que el estudiante y su familia lo entiendan sin tecnicismos, con recomendaciones concretas.</span></div>',
         '<div><b>Lenguaje claro</b><span>Escrito para que el estudiante y su familia lo entiendan sin tecnicismos, con recomendaciones concretas.</span></div>\n'
         '    <div><b>Panel con datos del colegio</b><span>Avance en tiempo real, intereses vocacionales por curso (CHASIDE y Holland) y descarga en CSV, para planificar charlas, ferias y visitas a universidades.</span></div>\n'
         '    <div><b>Cursos con certificado</b><span>Cada estudiante tiene su <a href="https://learn.aurzane.com/aula/">aula personal en AURZANE LEARN</a> con su progreso, sus horas de estudio y sus certificados verificables, sin que nadie tenga que gestionarlo.</span></div>'),
        ('<div><b>Cursos para tus clases</b><span>Con el <a href="https://learn.aurzane.com/aula/?docente=1">modo aula de AURZANE LEARN</a>, cada docente asigna un curso gratis y sigue el avance de su grupo: lecciones, notas y certificados.</span></div>',
         '<div><b>Cursos con certificado</b><span>Cada estudiante tiene su <a href="https://learn.aurzane.com/aula/">aula personal en AURZANE LEARN</a> con su progreso, sus horas de estudio y sus certificados verificables, sin que nadie tenga que gestionarlo.</span></div>')]}
# Identidad nueva de BUILD (dinero, ingresos y vivienda) y LIVE (salud y día a día), auditoría 16/11/2026
CAMBIOS.setdefault('build.aurzane.com/public_html/index.html', []).extend([
    ('<div class="status-pill"><span class="dot"></span>Los proyectos físicos siguen en exploración — la biblioteca de guías de BUILD ya es real</div>',
     '<div class="status-pill"><span class="dot"></span>8 calculadoras gratis con la normativa de 2026 y guías con fuentes</div>'),
    ('<p>BUILD es la dimensión más ambiciosa y también la más temprana de AURZANE: el punto donde la orientación vocacional de OVP, el conocimiento de MIND y las herramientas de NEXUS podrían convertirse en espacios físicos — clínicas, centros y proyectos con impacto real.</p>',
     '<p>BUILD es el mundo de AURZANE para decidir sobre tu dinero: cuánto cobrarás en neto, qué te deben si dejas un trabajo, cuánto ahorrar para una meta o para tu jubilación, cuánto cuesta comprar una casa y si compensa invertir en un piso para alquilar.</p>'),
    ('<p>Todavía no hay una clínica, un proyecto inmobiliario o una alianza institucional en marcha para mostrar — esa parte de BUILD sigue en etapa de exploración, y esta página lo cuenta honestamente en vez de simular algo que no existe. Lo que sí es real desde ahora es la biblioteca de BUILD: guías originales que sintetizan estudios verificables sobre bienes raíces, urbanismo, construcción sostenible y alianzas institucionales — el mismo tipo de investigación que, más adelante, va a sostener las decisiones detrás de esos proyectos físicos.</p>',
     '<p>Cada calculadora cita la ley o la fuente oficial de la que salen sus números, y la biblioteca de BUILD resume estudios verificables sobre vivienda, urbanismo y economía doméstica. Son herramientas orientativas: para firmar o invertir, consulta tu caso con un profesional.</p>'),
    ('<p class="pie-desc">AURZANE BUILD resume investigación real sobre bienes raíces, urbanismo e infraestructura en un lenguaje simple. Cada guía es una síntesis original — no una copia de las fuentes citadas. Los proyectos físicos de BUILD (clínicas, inmuebles, alianzas) siguen en etapa de exploración; cuando exista uno concreto, este espacio va a mostrarlo con el mismo nivel de detalle.</p>',
     '<p class="pie-desc">AURZANE BUILD: calculadoras y guías gratis para tu dinero, tus ingresos y tu casa, con números de 2026 y fuentes citadas. Información orientativa, no asesoramiento financiero.</p>')])
CAMBIOS.setdefault('live.aurzane.com/public_html/index.html', []).extend([
    ('<div class="trust-item"><h4>Fuentes verificables</h4><p>Cada artículo cita publicaciones reales — nada se inventa ni se resume sin respaldo.</p></div>',
     '<div class="trust-item"><h4>Fuentes verificables</h4><p>Cada calculadora y cada artículo citan la guía clínica o el estudio en que se basan.</p></div>'),
    ('<div class="trust-item"><h4>6 áreas de bienestar</h4><p>Propósito, equilibrio, hábitos, aventura y ciencia del deporte.</p></div>',
     '<div class="trust-item"><h4>Salud y día a día</h4><p>Ciclo y embarazo, peso y alimentación, sueño, bienestar emocional y las cuentas de cada día.</p></div>')])

for rel, pares in CAMBIOS.items():
    f = os.path.join(base, rel)
    try: s = open(f, encoding='utf-8').read()
    except Exception as e: print('no encontrado', rel, e); continue
    t = s
    for a, b in pares:
        if b not in t: t = t.replace(a, b)   # idempotente: no repite lo ya aplicado
    if t == s: print('sin cambios', rel); continue
    web = rel.split('/')[0]; copia = os.path.join(base, web, 'eliminar', 'textos-' + hoy, os.path.basename(f))
    os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
    open(f, 'w', encoding='utf-8').write(t); print('corregido', rel)

# El índice de artículos no cargaba la capa común (buscador, filtros, artículos de la IA): se añade si falta
import re
f = os.path.join(base, 'aurzane.com/public_html/articulos/index.html')
try:
    s = open(f, encoding='utf-8').read()
    if 'aurzane-paleta.js' not in s:
        copia = os.path.join(base, 'aurzane.com', 'eliminar', 'textos-' + hoy, 'articulos-index.html'); os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
        s = re.sub(r'(<meta name="viewport"[^>]*>)', r'\1\n<script src="https://aurzane.com/aurzane-paleta.js"></script>', s, count=1)
        open(f, 'w', encoding='utf-8').write(s); print('paleta añadida al índice de artículos')
    else: print('el índice de artículos ya tenía la paleta')
except Exception as e: print('índice de artículos', e)
