# -*- coding: utf-8 -*-
"""Textos legales de AURZANE (privacidad, cookies, condiciones de uso y aviso legal).
Los usa legal/gen.py. Actualizados el 16/11/2026 con AURZANE ID, Guardados, biblioteca, LEARN, OVP y colegios.
Si cambia una función que trate datos, actualiza aquí el apartado y la fecha."""

FECHA = '16 de noviembre de 2026'
TITULAR = 'Adrián Mauricio Sánchez Samaniego'
DOMICILIO = 'Avenida de Portugal, 173, 37006 Salamanca (España)'
NIF = 'Z5464099V'
CORREO = '<a href="mailto:hola@aurzane.com">hola@aurzane.com</a>'

INDICE = lambda pares: '<nav aria-label="En esta página" style="background:rgba(15,21,48,.05);border-radius:14px;padding:16px 20px;margin:18px 0"><strong>En esta página</strong><ol style="margin:8px 0 0">' + \
    ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in pares) + '</ol></nav>'
TABLA = lambda cab, filas: '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.92rem;margin:12px 0">' + \
    '<thead><tr>' + ''.join(f'<th style="text-align:left;border-bottom:2px solid rgba(46,38,32,.25);padding:8px 10px">{c}</th>' for c in cab) + '</tr></thead><tbody>' + \
    ''.join('<tr>' + ''.join(f'<td style="border-bottom:1px solid rgba(46,38,32,.12);padding:8px 10px;vertical-align:top">{c}</td>' for c in f) + '</tr>' for f in filas) + '</tbody></table></div>'

# ---------------------------------------------------------------- PRIVACIDAD
PRIVACIDAD = f'''  <p class="firma" style="border:0;margin-top:0">Última actualización: {FECHA}</p>
  <p>Esta política explica qué datos personales trata AURZANE (aurzane.com y sus subdominios mind, nexus, live, learn, build y ovp.aurzane.com), para qué, con qué base legal, quién puede verlos, cuánto tiempo se guardan y cómo ejercer tus derechos. La mayor parte de AURZANE se puede usar sin dar ningún dato.</p>
  {INDICE([('responsable', 'Quién es el responsable'), ('sin-cuenta', 'Si usas AURZANE sin cuenta'), ('cuenta', 'Tu cuenta AURZANE ID'), ('servicios', 'Qué datos tratamos en cada servicio'),
           ('colegios', 'Colegios'), ('bases', 'Finalidades y bases legales'), ('acceso', 'Quién puede ver tus datos'), ('proveedores', 'Proveedores y transferencias'),
           ('conservacion', 'Cuánto tiempo los guardamos'), ('seguridad', 'Cómo los protegemos'), ('menores', 'Menores de edad'), ('derechos', 'Tus derechos'),
           ('ia', 'Inteligencia artificial'), ('publicidad', 'Publicidad y enlaces de afiliado'), ('youtube', 'Redes sociales y servicios de API de YouTube'), ('cambios', 'Cambios')])}

  <h2 id="responsable">1. Quién es el responsable</h2>
  <ul>
    <li><strong>Responsable del tratamiento</strong>: {TITULAR}, psicólogo clínico, titular de AURZANE.</li>
    <li><strong>Domicilio</strong>: {DOMICILIO}.</li>
    <li><strong>Contacto para privacidad</strong>: {CORREO} (indica «Privacidad» en el asunto) o el <a href="/contacto.html">formulario de contacto</a>.</li>
  </ul>

  <h2 id="sin-cuenta">2. Si usas AURZANE sin cuenta</h2>
  <p>Puedes leer, hacer tests, usar las calculadoras, los ejercicios y la biblioteca sin registrarte. En ese caso:</p>
  <ul>
    <li>Los <strong>tests y calculadoras</strong> se calculan en tu navegador: tus respuestas no se envían a ningún servidor.</li>
    <li>Lo que guardas con el botón <strong>Guardar</strong>, la página por la que vas en un libro de la biblioteca, tu última lección de un curso o la nota de admisión que escribes en OVP se quedan <strong>solo en tu navegador</strong> (almacenamiento local). No los recibimos. El detalle está en la <a href="/cookies.html">política de cookies</a>.</li>
    <li>Si haces un test sin iniciar sesión, su resultado puede quedar pendiente en una cookie de tu navegador durante 60 días, solo para añadirlo a tu historial si después entras en tu cuenta.</li>
    <li>El servidor registra datos técnicos de cada visita (dirección IP, navegador, página y hora) para funcionar y protegerse de ataques. No los usamos para identificarte.</li>
  </ul>

  <h2 id="cuenta">3. Tu cuenta AURZANE ID</h2>
  <p>Una sola cuenta sirve para todos los mundos de AURZANE. Al crearla guardamos tu correo, tu contraseña cifrada (nunca la vemos), tu nombre si lo indicas y las fechas de alta y de último acceso. La sesión se mantiene con una cookie propia compartida por los subdominios de aurzane.com.</p>

  <h2 id="servicios">4. Qué datos tratamos en cada servicio</h2>
  {TABLA(['Servicio', 'Qué datos', 'Quién los ve'], [
      ['Guardados', 'Con sesión iniciada: la dirección, el título, el mundo y el tipo de cada página que guardas, para tenerlos en todos tus dispositivos.', 'Solo tú.'],
      ['Historial de tests (Mi AURZANE)', 'Nombre del test, puntuación, nivel y fecha. Si activas el recordatorio mensual, tu correo para avisarte.', 'Solo tú.'],
      ['Test de personalidad', 'Si pulsas «Guardar en Mi AURZANE»: versión del test, puntuaciones de rasgos y facetas, perfil, fecha y tu correo.', 'Tú y el equipo de AURZANE, para orientarte mejor.'],
      ['Cursos de LEARN', 'Lecciones abiertas y completadas, respuestas y notas de los tests, repaso programado, apuntes y tarjetas de estudio.', 'Solo tú.'],
      ['Certificados de LEARN', 'El nombre que escribes, el curso, la nota final y la fecha, unidos a tu cuenta.', 'Cualquier persona con el código del certificado puede ver nombre, curso, horas, nota y fecha, nunca tu correo.'],
      ['Orientación vocacional (OVP)', 'Datos de perfil (nombre, correo, teléfono, edad, sexo, institución y curso si los das), evaluaciones elegidas, respuestas a los instrumentos (CHASIDE, Holland, AF5, hábitos de estudio, APT-A, APT-B), fechas del proceso, notas del profesional y el informe.', 'Tú y el profesional responsable. Tu colegio, solo en lo que se explica en el apartado 5.'],
      ['Boletín semanal', 'Tu correo, la fecha de alta y la página de suscripción. Doble confirmación por correo.', 'Solo el equipo de AURZANE.'],
      ['Formulario de contacto y solicitudes de colegios', 'Nombre, correo, motivo y mensaje; en solicitudes de colegios, además cargo, centro, ciudad y teléfono si lo indicas.', 'Solo el equipo de AURZANE.'],
      ['Avisos de errores', 'Si pulsas «Avísanos» en una página: la página y tu mensaje (te pedimos que no incluyas datos personales). Los errores técnicos de la web se registran con la página y el mensaje, sin datos personales.', 'Solo el equipo de AURZANE.'],
      ['Medición', 'Recuento de visitas a partir de los registros del servidor y de los clics en enlaces de compra (fecha, tienda y página de origen). No usamos analítica de terceros.', 'Solo el equipo de AURZANE, en cifras agregadas.']])}

  <h2 id="colegios">5. Colegios</h2>
  <p>Un colegio puede usar AURZANE OVP con sus estudiantes. Funciona así:</p>
  <ul>
    <li>El colegio tiene un <strong>enlace propio</strong>. Si creas tu cuenta y eliges tus evaluaciones entrando por ese enlace, tu proceso queda vinculado a ese colegio y tu informe lleva su membrete. No puedes vincularte a un colegio de otra forma.</li>
    <li>Solo las personas que el colegio autoriza (orientación y dirección), dadas de alta por AURZANE con su correo, pueden entrar a su panel.</li>
    <li>En el panel, el colegio ve tu <strong>nombre, tu curso, cuántas evaluaciones has elegido y completado, tu última actividad y si has terminado</strong>.</li>
    <li>Tus <strong>respuestas y tu informe no los ve el colegio</strong>, salvo que tú decidas compartir tu informe desde «Mi cuenta» en tu portal. Puedes dejar de compartirlo cuando quieras.</li>
    <li>El colegio puede <strong>retirarte</strong> de su panel si no eres estudiante suyo. Tu proceso sigue en AURZANE con el informe general, sin el membrete ni las secciones de ese colegio.</li>
    <li>El colegio solo puede usar esta información para la orientación de sus estudiantes y debe informar a las familias. Si tienes dudas, pregúntale a tu colegio o escríbenos.</li>
  </ul>

  <h2 id="bases">6. Finalidades y bases legales</h2>
  {TABLA(['Finalidad', 'Base legal (RGPD)'], [
      ['Crear y mantener tu cuenta, Guardados, historial, cursos y certificados', 'Ejecución del servicio que pides (art. 6.1.b).'],
      ['Evaluaciones e informe de orientación vocacional', 'Tu consentimiento explícito al iniciar el proceso (arts. 6.1.a y 9.2.a), ya que las respuestas psicológicas merecen especial protección.'],
      ['Mostrar tu avance a tu colegio y compartir tu informe con él', 'Tu consentimiento al entrar por el enlace del colegio y, para el informe, al activar «Compartir» (art. 6.1.a). En menores, con la autorización de su familia.'],
      ['Boletín y recordatorios', 'Tu consentimiento (art. 6.1.a), que puedes retirar en cada correo.'],
      ['Responder mensajes y solicitudes', 'Tu consentimiento y la gestión de tu petición (art. 6.1.a y b).'],
      ['Seguridad, errores técnicos y estadísticas agregadas', 'Interés legítimo en mantener el servicio seguro y funcionando (art. 6.1.f).'],
      ['Publicidad personalizada', 'Tu consentimiento en el aviso de cookies (art. 6.1.a).']])}
  <p>Tus datos no se venden, no se ceden con fines comerciales y no se usan para entrenar sistemas de inteligencia artificial.</p>

  <h2 id="acceso">7. Quién puede ver tus datos</h2>
  <p>La base de datos aplica la regla «cada persona solo ve lo suyo» en el propio servidor, no solo en la pantalla. El acceso de administración es una cuenta separada y los cambios en información sensible quedan registrados (quién, cuándo y qué). Los profesionales y los colegios solo ven lo que se describe en los apartados 4 y 5.</p>

  <h2 id="proveedores">8. Proveedores y transferencias internacionales</h2>
  <ul>
    <li><strong>SiteGround</strong> (alojamiento web y correo, servidores en la UE).</li>
    <li><strong>Supabase</strong> (base de datos, cuentas e inicio de sesión).</li>
    <li><strong>Google</strong> (publicidad de AdSense, traducción opcional de páginas y los asistentes de inteligencia artificial).</li>
    <li><strong>GitHub</strong> (automatización del sitio; no recibe datos de usuarios).</li>
  </ul>
  <p>Algunos pueden tratar datos fuera del Espacio Económico Europeo. Lo hacen con las garantías del Marco de Privacidad de Datos UE-EE. UU. o con las cláusulas contractuales tipo de la Comisión Europea.</p>

  <h2 id="conservacion">9. Cuánto tiempo los guardamos</h2>
  <ul>
    <li>Cuenta, Guardados, historial, cursos y certificados: mientras tengas la cuenta. Si la eliminas, se borran (los certificados quedan anulados).</li>
    <li>Proceso de orientación vocacional: mientras esté activo y después mientras puedas necesitar tu informe. Si pides el borrado, tus datos quedan marcados 30 días (por si fue un error) y después se eliminan de forma definitiva, incluidas tus respuestas.</li>
    <li>Boletín: hasta que te das de baja, momento en que se borra tu correo.</li>
    <li>Mensajes y solicitudes: el tiempo necesario para atenderlos y, como máximo, un año.</li>
    <li>Registros técnicos del servidor: el tiempo que fija el proveedor de alojamiento por seguridad, normalmente semanas.</li>
  </ul>

  <h2 id="seguridad">10. Cómo los protegemos</h2>
  <p>Conexión cifrada (HTTPS) en todo el sitio, contraseñas cifradas, seguridad por filas en la base de datos, cuentas de administración separadas, páginas internas fuera de los buscadores y copias de seguridad. Si alguna vez hubiera una brecha que afecte a tus datos, te avisaríamos y lo comunicaríamos a la autoridad de control como exige la ley.</p>

  <h2 id="menores">11. Menores de edad</h2>
  <p>En España, una persona menor de 14 años necesita la autorización de su madre, padre o tutor para crear una cuenta y hacer evaluaciones. En otros países se aplica la edad que fije su ley. Cuando el proceso se hace a través de un colegio, el colegio se encarga de informar a las familias y de recoger esa autorización. Si eres menor, habla con tu familia o con tu orientador antes de empezar.</p>

  <h2 id="derechos">12. Tus derechos</h2>
  <p>Puedes pedir en cualquier momento <strong>acceso</strong> a tus datos, su <strong>rectificación</strong>, su <strong>supresión</strong>, la <strong>limitación</strong> u <strong>oposición</strong> a su uso, la <strong>portabilidad</strong> y <strong>retirar tu consentimiento</strong> sin que afecte a lo hecho antes. Muchas cosas las puedes hacer tú mismo: quitar Guardados, borrar el historial de un test, dejar de compartir tu informe con tu colegio o darte de baja del boletín.</p>
  <p>Para lo demás, escríbenos a {CORREO} desde el correo de tu cuenta. Te respondemos en un plazo máximo de un mes. Si crees que no hemos atendido bien tu solicitud, puedes reclamar ante la <a href="https://www.aepd.es" target="_blank" rel="noopener">Agencia Española de Protección de Datos</a>.</p>

  <h2 id="ia">13. Inteligencia artificial</h2>
  <ul>
    <li><strong>Asistente de resultados</strong>: al terminar un test de MIND o LIVE puedes hacer preguntas. Solo si escribes una, se envían tu pregunta y el resumen del resultado (sin nombre, correo ni otros datos personales) a Google Gemini para responder. No guardamos preguntas ni respuestas; solo contamos cuántas se hacen al día, con un identificador anónimo, para limitar el uso.</li>
    <li><strong>Librero de la biblioteca y la tienda</strong>: si le escribes una pregunta, se envía tu texto a Google Gemini para recomendarte libros, sin nombre, correo ni otros datos personales. No guardamos la conversación.</li>
    <li><strong>Contenidos</strong>: usamos inteligencia artificial para ayudar a redactar guías y artículos, sin ningún dato de usuarios. Lo explica la <a href="/politica-editorial.html">política editorial</a>.</li>
    <li>Ningún informe ni resultado de OVP se envía a servicios de inteligencia artificial.</li>
  </ul>

  <h2 id="publicidad">14. Publicidad y enlaces de afiliado</h2>
  <ul>
    <li>Las páginas públicas pueden mostrar anuncios de <strong>Google AdSense</strong>. Si nos visitas desde el Espacio Económico Europeo, el Reino Unido o Suiza, te pedimos permiso antes con el aviso de consentimiento de Google, y puedes cambiar tu elección cuando quieras. Puedes desactivar los anuncios personalizados en la <a href="https://adssettings.google.com" target="_blank" rel="noopener">configuración de anuncios de Google</a>.</li>
    <li>Nunca mostramos anuncios en el portal de orientación vocacional, en las evaluaciones, en los informes ni en el panel de los colegios, y ningún dato de evaluación se comparte con anunciantes.</li>
    <li>Algunos enlaces son <strong>de afiliado</strong> (Amazon y tiendas de la red Awin). Se señalan en la página. Al pulsarlos sales de AURZANE y la tienda trata tus datos con su propia política; AURZANE solo sabe que hubo un clic y, si compras, recibe una comisión sin datos que te identifiquen.</li>
    <li>El «Vídeo del día» solo carga YouTube (modo de privacidad mejorada, youtube-nocookie.com) cuando pulsas para reproducirlo.</li>
    <li>La traducción con el botón 🌐 solo carga Google Traductor si la eliges. Nunca se traducen paneles con datos de evaluaciones.</li>
  </ul>

  <h2 id="youtube">15. Redes sociales y servicios de API de YouTube</h2>
  <p>AURZANE publica vídeos cortos en su propio canal de YouTube (<a href="https://www.youtube.com/channel/UCVt-98jePhAj4QreHyuumBQ" target="_blank" rel="noopener">AURZANE en YouTube</a>) con una herramienta interna, AURZANE Publica, que usa los Servicios de API de YouTube. Al ver nuestros vídeos en YouTube aceptas las <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener">Condiciones del Servicio de YouTube</a>, y Google trata tus datos según la <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Política de Privacidad de Google</a>.</p>
  <ul>
    <li>AURZANE Publica solo sube vídeos propios a nuestro canal con la autorización OAuth del propietario del canal (permiso youtube.upload). No pide acceso a la cuenta de YouTube de ningún visitante.</li>
    <li>No recopilamos, almacenamos ni compartimos datos de usuarios de YouTube. El único dato guardado es el token de autorización del propio canal, cifrado como secreto en nuestro sistema de automatización.</li>
    <li>El propietario puede revocar el acceso en la <a href="https://security.google.com/settings/security/permissions" target="_blank" rel="noopener">página de permisos de seguridad de Google</a>. Al revocarlo, el token deja de funcionar y se elimina.</li>
    <li>En nuestras otras redes (Instagram, Facebook, TikTok, Telegram, Bluesky, Mastodon y Pinterest) solo publicamos en nuestras cuentas y no tratamos datos de sus usuarios.</li>
  </ul>

  <h2 id="cambios">16. Cambios</h2>
  <p>Cuando añadimos una función que trata datos, actualizamos esta política y su fecha. Si un cambio afecta al uso de datos que ya nos diste, te lo comunicaremos directamente.</p>'''

# ---------------------------------------------------------------- COOKIES
COOKIES = f'''  <p class="firma" style="border:0;margin-top:0">Última actualización: {FECHA}</p>
  <h2>Qué son</h2>
  <p>Las cookies son pequeños archivos que una web guarda en tu navegador. El almacenamiento local es parecido: guarda información en tu navegador, pero no se envía a ningún servidor. Las técnicas son necesarias para que la web funcione o recuerde lo que tú eliges; las de publicidad solo se usan si las aceptas.</p>

  <h2>Cookies técnicas propias (no necesitan tu consentimiento)</h2>
  {TABLA(['Nombre', 'Para qué', 'Duración'], [
      ['aurzane-id-auth (y aurzane-id-auth.0, .1…)', 'Mantiene abierta tu sesión de AURZANE ID en todos los mundos de aurzane.com.', 'Hasta que cierras sesión'],
      ['azPend', 'Guarda el resultado de un test hecho sin sesión para añadirlo a tu historial si entras. Se borra al guardarlo.', '60 días'],
      ['aurzane-paleta', 'Recuerda el color o el tema que eliges.', '1 año']])}

  <h2>Almacenamiento local de tu navegador (no se envía a ningún servidor)</h2>
  {TABLA(['Clave', 'Para qué'], [
      ['az-guardados', 'Tu lista de Guardados en este navegador. Se comparte entre los subdominios de AURZANE mediante una página propia de aurzane.com que solo responde a páginas de aurzane.com.'],
      ['rh-guardados, aurzane-&lt;mundo&gt;-guardados', 'Listas guardadas antiguas del Research Hub y de cada mundo, que se unen a Guardados.'],
      ['az-bib-leidos, bib-vista', 'Los libros que has abierto y la página por la que vas; la vista que prefieres en la biblioteca (cuadrícula o lista).'],
      ['aurzane-curso-&lt;curso&gt;-ultima', 'La última lección que abriste de cada curso, para «Continuar».'],
      ['aurzane-ovp-nota', 'La nota de admisión que escribes en «Dónde estudiar», para usarla en los enlaces a NEXUS.'],
      ['aurzane-colegio', 'El último colegio que abriste en el panel del colegio.'],
      ['azBolOk, azBolVisto', 'Si ya te suscribiste o cerraste el aviso del boletín, para no repetirlo.']])}
  <p>Puedes borrarlo todo desde la configuración de tu navegador (datos de sitios). Si lo haces, perderás lo guardado solo en ese navegador; lo que guardaste con la sesión iniciada sigue en tu cuenta.</p>

  <h2>Cookies de terceros</h2>
  <ul>
    <li><strong>Google AdSense</strong> (publicidad, solo con tu consentimiento en el EEE, el Reino Unido y Suiza): Google y sus socios pueden usar cookies para mostrar anuncios, medir su rendimiento y, si lo aceptas, personalizarlos. Más información: <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">cómo usa Google los datos</a> y <a href="https://adssettings.google.com" target="_blank" rel="noopener">configuración de anuncios</a>. No hay anuncios en el portal vocacional, las evaluaciones, los informes ni el panel de los colegios.</li>
    <li><strong>googtrans</strong> (Google Traductor): recuerda el idioma, solo si traduces la página con el botón 🌐.</li>
    <li><strong>YouTube</strong>: el «Vídeo del día» usa el modo de privacidad mejorada y solo se carga si pulsas para reproducirlo.</li>
    <li><strong>Enlaces de afiliado</strong> (Amazon y tiendas de la red Awin): al pulsar uno, la tienda o la red de afiliación pueden guardar cookies en su propio dominio para saber que llegaste desde AURZANE. AURZANE no las lee.</li>
  </ul>

  <h2>Cómo cambiar tu elección</h2>
  <p>Puedes cambiar tu consentimiento de publicidad desde el aviso de privacidad que aparece en la web, o borrar las cookies y el almacenamiento desde tu navegador. Si tienes dudas, escríbenos a {CORREO}. Más detalles en la <a href="/privacidad.html">política de privacidad</a>.</p>'''

# ---------------------------------------------------------------- CONDICIONES
CONDICIONES = f'''  <p class="firma" style="border:0;margin-top:0">Última actualización: {FECHA}</p>
  <h2>1. Quién ofrece este sitio</h2>
  <p>aurzane.com y sus subdominios (mind, nexus, live, learn, build y ovp.aurzane.com) son un proyecto de divulgación cuyo titular figura en el <a href="/aviso-legal.html">aviso legal</a>. Contacto: {CORREO}. Al usar el sitio aceptas estas condiciones.</p>
  <h2>2. Contenido orientativo</h2>
  <p>Los tests, calculadoras, ejercicios, guías, artículos, cursos e informes son gratuitos y orientativos. <strong>No sustituyen una evaluación, un diagnóstico ni un tratamiento profesional.</strong> Si estás en peligro o piensas en hacerte daño, llama al 112 o al 024 en España, o al número de emergencias de tu país.</p>
  <h2>3. Cuenta AURZANE ID</h2>
  <p>Con una cuenta gratuita guardas tus resultados, tus Guardados, tu avance en los cursos y tu proceso de orientación vocacional. Los datos que das deben ser ciertos y tu contraseña es personal. Puedes cerrar tu cuenta y pedir el borrado de tus datos cuando quieras desde Mi AURZANE o escribiendo a {CORREO}. Podemos suspender una cuenta que incumpla estas condiciones.</p>
  <h2>4. Guardados</h2>
  <p>Puedes guardar tests, perfiles, calculadoras, ejercicios, cursos, libros, artículos y universidades. Sin sesión, la lista se guarda solo en tu navegador; con sesión, también en tu cuenta. Es una ayuda personal: no garantizamos que una página guardada siga existiendo siempre.</p>
  <h2>5. Cursos y certificados (LEARN)</h2>
  <p>Los cursos son formación libre y gratuita, <strong>no reglada</strong>. Los certificados acreditan el aprovechamiento de un curso según sus requisitos (por ejemplo, lecciones abiertas y nota mínima en la evaluación final), <strong>no son títulos oficiales</strong> y cualquiera puede verificarlos con su código. Emitir un certificado con datos falsos o usarlo de forma engañosa supone su anulación.</p>
  <h2>6. Orientación vocacional (OVP)</h2>
  <p>Las evaluaciones y el informe de AURZANE OVP son una herramienta de orientación elaborada con instrumentos publicados. Las decisiones sobre estudios y carrera corresponden a cada persona y, en el caso de menores, a su familia. Las carreras y universidades que aparecen en «Dónde estudiar» y en NEXUS proceden de fuentes oficiales y cambian cada año: confírmalas siempre con la universidad.</p>
  <h2>7. Colegios</h2>
  <ul>
    <li>El colegio que usa OVP recibe un enlace propio y un panel. Solo pueden entrar las personas que el colegio autoriza, dadas de alta por AURZANE con su correo.</li>
    <li>El colegio se compromete a usar el panel solo para la orientación de sus propios estudiantes, a informar a las familias y recoger su autorización cuando sea necesaria, a no compartir el enlace fuera del centro y a avisarnos para dar de baja a quien deje de trabajar en él.</li>
    <li>El colegio ve el avance de sus estudiantes y solo ve el informe de quien decide compartirlo. Puede retirar de su panel a quien no sea estudiante suyo.</li>
    <li>AURZANE puede desactivar el acceso de un colegio que haga un uso indebido.</li>
  </ul>
  <h2>8. Biblioteca, tienda y enlaces de afiliado</h2>
  <p>Los libros de la biblioteca mantienen la licencia indicada en cada ficha. De los libros con derechos solo mostramos una ficha propia y dónde conseguirlos. La tienda y los bloques de «socios» no venden ni envían nada: enlazan a tiendas externas, que gestionan el pedido, el pago, el envío y las devoluciones con sus propias condiciones. Muchos de esos enlaces son de afiliado y se señalan como tales; no cambian el precio para ti.</p>
  <h2>9. Propiedad intelectual</h2>
  <p>Los textos, diseños, herramientas, cursos e informes propios de AURZANE pertenecen a su titular. Puedes usarlos para tu uso personal y compartir sus enlaces. No está permitido copiarlos de forma masiva, extraer sus datos con programas automáticos ni presentarlos como propios.</p>
  <h2>10. Comportamiento</h2>
  <p>No está permitido usar el sitio para fines ilícitos, intentar acceder a datos o cuentas de otras personas o a zonas de administración, enviar contenido ofensivo por los formularios ni sobrecargar los servicios de forma automatizada.</p>
  <h2>11. Redes sociales y YouTube</h2>
  <p>Publicamos contenido propio en nuestras redes, incluido nuestro canal de YouTube, mediante la herramienta interna AURZANE Publica, que usa los Servicios de API de YouTube. Al ver ese contenido en YouTube aceptas las <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener">Condiciones del Servicio de YouTube</a> y se aplica la <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Política de Privacidad de Google</a>.</p>
  <h2>12. Responsabilidad</h2>
  <p>Cuidamos que la información sea correcta y cite sus fuentes, pero puede contener errores o quedar desactualizada, y el servicio puede interrumpirse por mantenimiento o fallos técnicos. AURZANE no se hace responsable de las decisiones que se tomen solo a partir de sus contenidos ni del contenido o las condiciones de las webs externas a las que enlaza.</p>
  <h2>13. Cambios</h2>
  <p>Podemos actualizar estas condiciones cuando añadimos o cambiamos funciones. La fecha de la última actualización figura al inicio. Si un cambio es importante y tienes cuenta, te lo comunicaremos.</p>
  <h2>14. Ley aplicable</h2>
  <p>Estas condiciones se rigen por la legislación española. Para cualquier controversia, y salvo que la normativa de consumidores disponga otra cosa, son competentes los juzgados y tribunales de Salamanca (España).</p>'''

# ---------------------------------------------------------------- AVISO LEGAL
AVISO = f'''  <p class="firma" style="border:0;margin-top:0">Última actualización: {FECHA}</p>
  <h2>Titular</h2>
  <p>En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico (LSSI), se informa de que aurzane.com y sus subdominios (mind, nexus, live, learn, build y ovp.aurzane.com) son un proyecto de:</p>
  <ul>
    <li><strong>Titular</strong>: {TITULAR}, psicólogo clínico (registro SENESCYT N.º 1033-2023-2618464).</li>
    <li><strong>NIE/NIF</strong>: {NIF}</li>
    <li><strong>Domicilio</strong>: {DOMICILIO}</li>
    <li><strong>Correo</strong>: {CORREO}</li>
  </ul>
  <h2>Finalidad</h2>
  <p>AURZANE ofrece divulgación de psicología, bienestar, estudio, vivienda y dinero; tests orientativos, calculadoras y ejercicios; un buscador de universidades; cursos gratuitos con certificado de aprovechamiento; una biblioteca de obras con licencia abierta o de dominio público; y AURZANE OVP, un servicio de orientación vocacional para personas y colegios. Los contenidos son orientativos y no sustituyen la valoración de un profesional sanitario.</p>
  <h2>Propiedad intelectual</h2>
  <p>Los textos, diseños, herramientas, cursos e informes propios de AURZANE pertenecen a su titular. Los libros, estudios, imágenes, música y frases de terceros se usan según su licencia (Creative Commons, dominio público o licencias de bancos como Unsplash, Wikimedia Commons, Pexels, Pixabay y Jamendo) y se indica su autor, su licencia y su origen.</p>
  <ul>
    <li>En la biblioteca solo se alojan obras de dominio público o con licencia abierta que permite compartirlas. Cada ficha muestra la licencia y la fuente original.</li>
    <li>Los libros con licencia «no comercial» se leen sin anuncios.</li>
    <li>De los libros con derechos solo mostramos la portada, los datos bibliográficos y una descripción propia, y enlazamos a la tienda donde se venden. No alojamos ni compartimos su contenido.</li>
  </ul>
  <h2 id="retirada">Retirada de contenidos</h2>
  <p>Si eres titular de derechos y crees que algún contenido no debería estar publicado, escríbenos a {CORREO} con el asunto «Retirada de contenido» indicando:</p>
  <ul>
    <li>La dirección exacta (URL) de la página o del archivo.</li>
    <li>La obra protegida y quién es su titular.</li>
    <li>Tus datos de contacto y una declaración de que la información es exacta y de que eres el titular o actúas en su nombre.</li>
  </ul>
  <p>Retiramos de forma cautelar el contenido señalado en un plazo máximo de 72 horas desde que recibimos la comunicación completa, lo revisamos y te respondemos por correo.</p>
  <h2>Enlaces de afiliado y publicidad</h2>
  <p>En calidad de Afiliado de Amazon, AURZANE obtiene ingresos por las compras adscritas que cumplen los requisitos aplicables. AURZANE también participa en programas de afiliados de la red Awin (por ejemplo, de librerías, viajes, deporte, hogar, salud y negocios) relacionados con sus contenidos. Estos enlaces se señalan en la página y comprar a través de ellos no te cuesta más. Las páginas públicas pueden mostrar publicidad de Google AdSense. AURZANE no vende ni envía productos: el pedido, el pago y las devoluciones los gestiona cada tienda.</p>
  <h2>Responsabilidad</h2>
  <p>Cuidamos que la información sea correcta y cite sus fuentes, pero puede contener errores. AURZANE no se hace responsable de las decisiones que se tomen solo a partir de sus contenidos. Los enlaces a otras webs se ofrecen como referencia y no controlamos su contenido.</p>
  <h2>Datos personales y cookies</h2>
  <p>Se explican en la <a href="/privacidad.html">política de privacidad</a> y en la <a href="/cookies.html">política de cookies</a>. Las condiciones para usar el sitio están en las <a href="/condiciones.html">condiciones de uso</a>.</p>'''
