# -*- coding: utf-8 -*-
"""Páginas de confianza de AURZANE: sobre, contacto, política editorial y condiciones de uso.
Salida en publicar/aurzane.com/. Uso: python3 legal/gen.py"""
import os, json

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'publicar', 'aurzane.com')
PIE = ('<p class="firma"><a href="/sobre-aurzane.html">Sobre AURZANE</a> · <a href="/contacto.html">Contacto</a> · <a href="/politica-editorial.html">Política editorial</a> · '
       '<a href="/privacidad.html">Privacidad</a> · <a href="/cookies.html">Cookies</a> · <a href="/aviso-legal.html">Aviso legal</a> · <a href="/condiciones.html">Condiciones de uso</a></p>')
CSS = '''body{margin:0;background:var(--bg,#F6F0E8);color:var(--text,#2E2620);font:16px/1.7 "Instrument Sans",system-ui,sans-serif}
.h{background:#0F1530;color:#F5F3EE;padding:44px 20px}.h a{color:#EACF92}.w{max-width:760px;margin:0 auto}
h1{font:700 clamp(1.8rem,4vw,2.4rem)/1.15 "Bodoni Moda",serif;margin:8px 0}h2{font:700 1.3rem/1.3 "Bodoni Moda",serif;margin:34px 0 8px}
main{padding:10px 20px 70px}main a{color:inherit}ul{padding-left:20px}
.firma{margin-top:30px;padding-top:16px;border-top:1px solid rgba(95,80,68,.18);font-size:.92rem;color:#6b6153}
.ficha{display:flex;gap:18px;align-items:center;background:rgba(15,21,48,.05);border-radius:14px;padding:16px;margin:18px 0}.ficha img{width:120px;height:auto}
form.c{display:grid;gap:12px;margin-top:14px}form.c label{display:grid;gap:5px;font-size:.92rem}form.c input,form.c select,form.c textarea{font:inherit;padding:11px 13px;border:1px solid rgba(46,38,32,.25);border-radius:10px;background:#fff}
form.c button{justify-self:start;border:0;border-radius:99px;padding:12px 22px;background:#0F1530;color:#F5F3EE;font:700 .95rem inherit;cursor:pointer}.trampa{position:absolute;left:-9999px}
#estado{min-height:1.4em}'''


def pagina(slug, titulo, desc, h1, sub, cuerpo, extra_head=''):
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': titulo, 'url': f'https://aurzane.com/{slug}', 'inLanguage': 'es',
          'publisher': {'@type': 'Organization', 'name': 'AURZANE', 'url': 'https://aurzane.com/', 'email': 'hola@aurzane.com',
                        'founder': {'@type': 'Person', 'name': 'Adrián Mauricio Sánchez Samaniego', 'jobTitle': 'Psicólogo clínico'}}}
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>{titulo}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://aurzane.com/{slug}">
<meta property="og:title" content="{titulo}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://aurzane.com/og-portada.jpg">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@500;700&family=Instrument+Sans:wght@400;600&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>{extra_head}
</head>
<body>
<div class="h"><div class="w"><a href="https://aurzane.com/">AURZANE</a><h1>{h1}</h1><p>{sub}</p></div></div>
<main class="w">
{cuerpo}
{PIE}
</main>
</body>
</html>
'''


SOBRE = '''  <h2>Qué es AURZANE</h2>
  <p>AURZANE es un proyecto de divulgación gratuita en español sobre psicología, bienestar, estudio y orientación vocacional. Su objetivo es que cualquier persona pueda entender mejor lo que siente y tomar decisiones informadas sobre su salud emocional, sus hábitos y su futuro académico, con herramientas claras y sin tecnicismos.</p>
  <p>El sitio se organiza en cinco áreas:</p>
  <ul>
    <li><strong>MIND</strong>: salud mental, emociones, tests orientativos validados y ejercicios guiados de relajación.</li>
    <li><strong>NEXUS</strong>: buscador de universidades y carreras de más de 50 países y orientación académica.</li>
    <li><strong>LIVE</strong>: bienestar, sueño, hábitos y calculadoras de salud.</li>
    <li><strong>LEARN</strong>: técnicas de estudio, cursos y recursos de aprendizaje.</li>
    <li><strong>BUILD</strong>: trabajo, dinero y vivienda, con calculadoras prácticas.</li>
  </ul>
  <p>Además, AURZANE incluye una biblioteca de libros y estudios con licencia libre o de dominio público, una tienda de libros recomendados y AURZANE OVP, un sistema de orientación vocacional en línea con informe completo.</p>

  <h2>Quién está detrás</h2>
  <div class="ficha"><img src="https://aurzane.com/img/firma.png" alt="Firma de Adrián Sánchez Samaniego" width="120"><div>
  <p><strong>Adrián Mauricio Sánchez Samaniego</strong>, psicólogo clínico (registro SENESCYT N.º 1033-2023-2618464), es el responsable de AURZANE.</p></div></div>
  <p>Su trabajo se centra en la evaluación psicológica y psicopedagógica y en la orientación vocacional de estudiantes, también dentro de centros educativos. Es el autor de las herramientas de AURZANE y el responsable de sus contenidos.</p>

  <h2>Cómo preparamos los contenidos</h2>
  <ul>
    <li>Los <strong>tests</strong> usan escalas publicadas y validadas (por ejemplo, GAD-7, PHQ-9, Rosenberg o WHO-5), con su referencia y sus puntos de corte originales. Son orientativos y no dan diagnósticos.</li>
    <li>Las <strong>guías y artículos</strong> se apoyan en conocimiento científico establecido y en organismos de referencia. Parte de la redacción se hace con ayuda de herramientas de inteligencia artificial, siempre con instrucciones estrictas: no inventar cifras ni estudios, no recomendar medicación y remitir a un profesional cuando corresponde. El detalle está en nuestra <a href="/politica-editorial.html">política editorial</a>.</li>
    <li>Los <strong>libros y estudios</strong> de la biblioteca muestran siempre su licencia, su autor y su origen.</li>
    <li>Los <strong>datos de universidades</strong> proceden de registros oficiales de cada país y se actualizan periódicamente.</li>
  </ul>

  <h2>Cómo se financia</h2>
  <p>Todo el contenido es gratuito. Para sostener el proyecto, AURZANE usa enlaces de afiliado (por ejemplo, de Amazon o de tiendas de la red Awin) y puede mostrar publicidad de Google AdSense en las páginas públicas. Los enlaces de afiliado se señalan en la página y no cambian el precio para ti. Nunca se muestran anuncios en las evaluaciones ni en los informes de orientación vocacional, y ningún dato clínico se comparte con anunciantes.</p>

  <h2>Contacto</h2>
  <p>Puedes escribirnos a <a href="mailto:hola@aurzane.com">hola@aurzane.com</a> o desde la <a href="/contacto.html">página de contacto</a>. Si ves un error en algún contenido, usa el botón «⚑ Reportar» de cada página o escríbenos: lo revisamos y corregimos.</p>
  <p>¿Trabajas en un colegio? Mira <a href="/colegios/">AURZANE OVP para colegios</a>.</p>'''

CONTACTO = '''  <p>Respondemos personalmente a cada mensaje, normalmente en 2 o 3 días laborables.</p>
  <h2>Datos de contacto</h2>
  <ul>
    <li><strong>Correo</strong>: <a href="mailto:hola@aurzane.com">hola@aurzane.com</a></li>
    <li><strong>Responsable</strong>: Adrián Mauricio Sánchez Samaniego, psicólogo clínico</li>
    <li><strong>Dirección postal</strong>: Salamanca (España). La dirección completa figura en el <a href="/aviso-legal.html">aviso legal</a>.</li>
  </ul>
  <h2>Escríbenos</h2>
  <form class="c" id="fc" novalidate>
    <label>Tu nombre<input name="nombre" required maxlength="120" autocomplete="name"></label>
    <label>Tu correo<input name="correo" type="email" required maxlength="160" autocomplete="email"></label>
    <label>Motivo<select name="motivo" required><option value="">Elige una opción</option><option>Duda o sugerencia</option><option>Error en un contenido</option><option>Retirada de contenido o derechos de autor</option><option>Privacidad y datos personales</option><option>Colegios y orientación vocacional</option><option>Colaboraciones y prensa</option></select></label>
    <label>Mensaje<textarea name="mensaje" rows="6" required maxlength="3000"></textarea></label>
    <label class="trampa" aria-hidden="true">Web<input name="web" tabindex="-1" autocomplete="off"></label>
    <label style="display:flex;gap:8px;align-items:flex-start"><input type="checkbox" name="acepto" required style="margin-top:6px"> <span>Acepto que AURZANE use estos datos solo para responder a mi mensaje, según la <a href="/privacidad.html">política de privacidad</a>.</span></label>
    <button type="submit">Enviar mensaje</button>
    <p id="estado" role="status" aria-live="polite"></p>
  </form>
  <h2>Antes de escribir</h2>
  <ul>
    <li>AURZANE no ofrece atención clínica ni de urgencia por este formulario. Si estás en peligro o piensas en hacerte daño, llama al 112 o al 024 en España, o al número de emergencias de tu país.</li>
    <li>Para ejercer tus derechos sobre tus datos personales (acceso, rectificación, supresión), indica «Privacidad y datos personales» como motivo.</li>
    <li>Para pedir la retirada de un contenido, sigue el <a href="/aviso-legal.html#retirada">procedimiento de retirada</a>.</li>
  </ul>
<script>
(function(){var f=document.getElementById('fc'),e=document.getElementById('estado');f.addEventListener('submit',function(ev){ev.preventDefault();
if(!f.checkValidity()){e.textContent='Revisa los campos: falta algún dato o el correo no es válido.';f.reportValidity();return;}
var d={};new FormData(f).forEach(function(v,k){d[k]=v;});e.textContent='Enviando…';
fetch('/contacto.php',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json();})
.then(function(j){e.textContent=j.ok?j.mensaje:(j.error||'No se pudo enviar. Escríbenos a hola@aurzane.com.');if(j.ok)f.reset();})
.catch(function(){e.textContent='No se pudo enviar. Escríbenos a hola@aurzane.com.';});});})();
</script>'''

EDITORIAL = '''  <p>Esta política explica cómo se crean, revisan y corrigen los contenidos de AURZANE, para que sepas qué puedes esperar de ellos.</p>
  <h2>Principios</h2>
  <ul>
    <li><strong>Rigor</strong>: nos apoyamos en conocimiento científico establecido, guías clínicas y organismos de referencia (como la Organización Mundial de la Salud o los ministerios de sanidad y educación). No publicamos cifras ni estudios que no podamos respaldar.</li>
    <li><strong>Claridad</strong>: escribimos para personas sin formación específica, sin tecnicismos innecesarios.</li>
    <li><strong>Prudencia</strong>: los contenidos son orientativos. No diagnosticamos, no recomendamos medicación y siempre indicamos cuándo conviene consultar a un profesional y dónde pedir ayuda urgente.</li>
    <li><strong>Independencia</strong>: los enlaces de afiliado y la publicidad no deciden qué recomendamos. Recomendamos un libro o un recurso porque es útil para el tema, y lo señalamos cuando el enlace es de afiliado.</li>
  </ul>
  <h2>Tests y herramientas</h2>
  <p>Los tests de AURZANE usan cuestionarios publicados y validados en la literatura científica, con sus instrucciones, puntuaciones y puntos de corte originales, y citan su referencia. Cuando una escala tiene derechos que no permiten publicarla, no la usamos. Las calculadoras explican su fórmula y sus límites.</p>
  <h2>Uso de inteligencia artificial</h2>
  <p>Usamos herramientas de inteligencia artificial para ayudar a redactar guías, artículos y descripciones, siempre con instrucciones estrictas: no inventar datos concretos, citar solo organismos y fuentes reales, no hacer diagnósticos y remitir a un profesional cuando corresponde. Los textos de salud siguen un guion fijo y se revisan de forma periódica; si detectamos un error, lo corregimos.</p>
  <h2>Fuentes externas</h2>
  <p>Los libros y estudios de la biblioteca son de acceso abierto o de dominio público y muestran su licencia y su origen. Los datos de universidades proceden de registros oficiales de cada país. Las imágenes son propias o tienen licencia que permite su uso, con atribución cuando la licencia lo pide.</p>
  <h2>Correcciones</h2>
  <p>Si encuentras un error, usa el botón «⚑ Reportar» de cada página o escríbenos a <a href="mailto:hola@aurzane.com">hola@aurzane.com</a>. Revisamos cada aviso y, si procede, corregimos el contenido y actualizamos su fecha.</p>
  <h2>Responsable</h2>
  <p>El responsable de los contenidos es Adrián Mauricio Sánchez Samaniego, psicólogo clínico (registro SENESCYT N.º 1033-2023-2618464). Más información en <a href="/sobre-aurzane.html">Sobre AURZANE</a>.</p>'''

CONDICIONES = '''  <p class="firma" style="border:0;margin-top:0">Última actualización: noviembre de 2026</p>
  <h2>1. Quién ofrece este sitio</h2>
  <p>aurzane.com y sus subdominios (mind, nexus, live, learn, build y ovp.aurzane.com) son un proyecto de divulgación de Adrián Mauricio Sánchez Samaniego, psicólogo clínico. Los datos del titular están en el <a href="/aviso-legal.html">aviso legal</a>. Contacto: <a href="mailto:hola@aurzane.com">hola@aurzane.com</a>.</p>
  <h2>2. Uso del contenido</h2>
  <p>Los tests, calculadoras, guías, cursos y materiales son gratuitos y orientativos. No sustituyen una evaluación, un diagnóstico ni un tratamiento profesional. Puedes usarlos para tu uso personal y compartir los enlaces. No está permitido copiar de forma masiva los contenidos propios de AURZANE ni presentarlos como propios.</p>
  <h2>3. Cuenta de Mi AURZANE</h2>
  <p>Para guardar resultados o usar AURZANE OVP puedes crear una cuenta gratuita. Eres responsable de mantener tu contraseña en secreto. Puedes pedir el cierre de tu cuenta y el borrado de tus datos en cualquier momento escribiendo a hola@aurzane.com.</p>
  <h2>4. Orientación vocacional (OVP)</h2>
  <p>Las evaluaciones y el informe de AURZANE OVP son una herramienta de orientación. Las decisiones sobre estudios y carrera corresponden a cada persona y, en el caso de menores, a su familia. Los datos de las evaluaciones se tratan según la <a href="/privacidad.html">política de privacidad</a>.</p>
  <h2>5. Biblioteca y tienda</h2>
  <p>Los libros de la biblioteca mantienen la licencia indicada en cada ficha. La tienda de libros no vende ni envía productos: enlaza a tiendas externas, que gestionan el pedido, el pago, el envío y las devoluciones con sus propias condiciones. Algunos de esos enlaces son de afiliado.</p>
  <h2>6. Redes sociales y YouTube</h2>
  <p>Publicamos contenido propio en nuestras redes sociales, incluido nuestro canal de YouTube, mediante la herramienta interna AURZANE Publica, que usa los Servicios de API de YouTube. Al ver ese contenido en YouTube aceptas las <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener">Condiciones del Servicio de YouTube</a> y se aplica la <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Política de Privacidad de Google</a>.</p>
  <h2>7. Comportamiento</h2>
  <p>No está permitido usar el sitio para fines ilícitos, intentar acceder a datos de otras personas, enviar contenido ofensivo por los formularios ni sobrecargar los servicios de forma automatizada.</p>
  <h2>8. Responsabilidad</h2>
  <p>Cuidamos que la información sea correcta y cite sus fuentes, pero puede contener errores o quedar desactualizada. AURZANE no se hace responsable de las decisiones que se tomen solo a partir de sus contenidos ni del contenido de las webs externas a las que enlaza.</p>
  <h2>9. Cambios</h2>
  <p>Podemos actualizar estas condiciones. La fecha de la última actualización figura al inicio de esta página.</p>
  <h2>10. Ley aplicable</h2>
  <p>Estas condiciones se rigen por la legislación española. Para cualquier controversia, y salvo que la normativa de consumidores disponga otra cosa, serán competentes los juzgados y tribunales de Salamanca (España).</p>'''

os.makedirs(OUT, exist_ok=True)
for slug, t, d, h1, sub, c in [
    ('sobre-aurzane.html', 'Sobre AURZANE: quiénes somos y cómo trabajamos', 'Quién está detrás de AURZANE, cómo preparamos los contenidos de psicología, bienestar y orientación vocacional, cómo se financia el proyecto y cómo contactar.', 'Sobre AURZANE', 'Psicología, bienestar y aprendizaje explicados con rigor y de forma gratuita.', SOBRE),
    ('contacto.html', 'Contacto | AURZANE', 'Escribe a AURZANE: dudas, errores en un contenido, privacidad, retirada de contenidos, colegios y colaboraciones. Respondemos en 2 o 3 días laborables.', 'Contacto', 'Escríbenos: respondemos personalmente a cada mensaje.', CONTACTO),
    ('politica-editorial.html', 'Política editorial de AURZANE', 'Cómo se crean, revisan y corrigen los contenidos de AURZANE: fuentes, tests validados, uso de inteligencia artificial, independencia y correcciones.', 'Política editorial', 'Cómo creamos, revisamos y corregimos nuestros contenidos.', EDITORIAL),
    ('condiciones.html', 'Condiciones de uso · AURZANE', 'Condiciones de uso de aurzane.com y sus subdominios: contenido orientativo, cuenta de Mi AURZANE, orientación vocacional, biblioteca, tienda y responsabilidad.', 'Condiciones de uso', 'Las reglas para usar AURZANE.', CONDICIONES)]:
    open(os.path.join(OUT, slug), 'w', encoding='utf-8').write(pagina(slug, t, d, h1, sub, c))
print('ok')
